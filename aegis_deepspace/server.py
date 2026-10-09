"""FastAPI Web Server for Aegis-DeepSpace Pillar 4 Autonomous Decision Engine MVP."""

import os
import time
import datetime
import hashlib
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from aegis_deepspace.models import CrewState, DecisionObject, CommsMode, RadiationState, VoiceVitalsState, AstroTwinState
from aegis_deepspace.decision_engine import AutonomousDecisionEngine
from aegis_deepspace.scenarios import DEMO_SCENARIOS
from aegis_deepspace.providers import (
    default_coordinator,
    MockRadiationProvider,
    MockVoiceVitalsProvider,
    MockAstroTwinProvider
)
from aegis_deepspace.copilot import default_copilot, ChatRequest, ChatResponse
from aegis_deepspace.dossier import (
    NasaMedicalDossier,
    generate_medical_dossier,
    format_dossier_markdown
)
from aegis_deepspace.sync.models import (
    SyncState,
    SyncRecordStatus,
    HealthEventRecord,
    TelemetrySummaryRecord,
    ModelUpdateRecord,
    FederatedGlobalModel,
    SyncStatusOverview
)
from aegis_deepspace.sync.coordinator import default_sync_coordinator
from aegis_deepspace.xai_engine import (
    default_xai_engine,
    ShapAlertExplanation,
    FEATURE_METADATA,
    FEATURE_KEYS
)


app = FastAPI(
    title="Aegis-DeepSpace: Autonomous Decision Engine (Pillar 4 MVP)",
    description="Offline AI Flight Surgeon Decision Support synthesizing Radiation, Voice Vitals, and Astro-Twin.",
    version="1.0.0"
)

engine = AutonomousDecisionEngine()

# In-memory current scenario tracker and state
active_scenario: str = "normal"
current_state: CrewState = DEMO_SCENARIOS["normal"]()
current_decision: DecisionObject = engine.process(current_state)


@app.get("/api/providers/radiation", response_model=RadiationState)
def get_radiation_provider_state():
    """Direct Pillar 1 provider endpoint."""
    return default_coordinator.radiation_provider.get_radiation_state(active_scenario)


@app.get("/api/pillar1/analysis")
def get_pillar1_analysis(start_module: str = "Module D", flux_msv: Optional[float] = None):
    """Exposes the full real Pillar 1 implementation: habitat topology, internal doses, and Dijkstra route."""
    from aegis_deepspace.pillar1_real import RealRadiationProvider
    if isinstance(default_coordinator.radiation_provider, RealRadiationProvider):
        provider = default_coordinator.radiation_provider
    else:
        provider = RealRadiationProvider()
    return provider.get_full_analysis(start_module=start_module, external_flux_mSv=flux_msv)


class EvacuationRequest(BaseModel):
    start_module: str = "Module D"
    target_module: Optional[str] = "Module B"
    external_flux_mSv: float = 250.0


@app.post("/api/pillar1/calculate_route")
def calculate_pillar1_route(req: EvacuationRequest):
    """Calculates Dijkstra minimum-dose path for given start module and external flux."""
    from aegis_deepspace.pillar1_real import RealRadiationProvider
    if isinstance(default_coordinator.radiation_provider, RealRadiationProvider):
        provider = default_coordinator.radiation_provider
    else:
        provider = RealRadiationProvider()
    route, transit_dose, steps = provider.calculate_evacuation_path(
        req.start_module, req.target_module, req.external_flux_mSv
    )
    compartment_doses = provider.compute_compartment_doses(req.external_flux_mSv)
    return {
        "start_module": req.start_module,
        "target_module": req.target_module or provider.get_safest_shelter(),
        "external_flux_mSv": req.external_flux_mSv,
        "route": route,
        "transit_dose_mSv": transit_dose,
        "steps": steps,
        "compartment_doses": compartment_doses
    }


@app.get("/api/providers/voice_vitals", response_model=VoiceVitalsState)
def get_voice_vitals_provider_state():
    """Direct Pillar 2 provider endpoint."""
    return default_coordinator.voice_provider.get_voice_vitals(active_scenario)


@app.get("/api/pillar2/analysis")
def get_pillar2_analysis(scenario: Optional[str] = None):
    """Exposes real Pillar 2 ML pipeline: Whisper transcript, DistilBERT sentiment, MFCC-CNN vitals, and drift alerts."""
    from aegis_deepspace.pillar2_real import RealVoiceVitalsProvider
    if isinstance(default_coordinator.voice_provider, RealVoiceVitalsProvider):
        provider = default_coordinator.voice_provider
    else:
        provider = RealVoiceVitalsProvider()
    chosen_scenario = scenario or active_scenario or "normal"
    return provider.get_full_analysis(scenario=chosen_scenario)


class AudioProcessRequest(BaseModel):
    audio_path: Optional[str] = None
    crew_id: Optional[str] = "ASTRO-01"


@app.get("/api/pillar2/audio_options")
def get_pillar2_audio_options():
    """Returns available audio logs and astronaut profiles for voice vitals analysis."""
    from aegis_deepspace.pillar2_real import load_astronaut_profiles, list_available_audio_logs
    profiles = load_astronaut_profiles()
    logs = list_available_audio_logs()
    return {
        "profiles": profiles,
        "audio_files": logs
    }


@app.post("/api/pillar2/process_audio")
def process_voice_audio(req: AudioProcessRequest):
    """Processes an audio recording through the real Whisper STT, DistilBERT, and MFCC-CNN pipeline."""
    from aegis_deepspace.pillar2_real import RealVoiceVitalsProvider
    if isinstance(default_coordinator.voice_provider, RealVoiceVitalsProvider):
        provider = default_coordinator.voice_provider
    else:
        provider = RealVoiceVitalsProvider()
    return provider.analyze_audio(req.audio_path, crew_id=req.crew_id or "ASTRO-01")


@app.post("/api/pillar2/upload_audio")
async def upload_voice_audio(
    file: UploadFile = File(...),
    crew_id: str = Form("ASTRO-01")
):
    """Accepts an uploaded or recorded voice log (wav/webm/ogg/mp3), saves and analyzes it."""
    import time
    import subprocess
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
    os.makedirs(upload_dir, exist_ok=True)
    
    filename = file.filename or "recording.wav"
    file_ext = os.path.splitext(filename)[1].lower() or ".wav"
    safe_name = f"voice_input_{int(time.time())}{file_ext}"
    save_path = os.path.join(upload_dir, safe_name)
    
    contents = await file.read()
    with open(save_path, "wb") as f:
        f.write(contents)
        
    target_wav = save_path
    if file_ext not in [".wav"]:
        target_wav = os.path.splitext(save_path)[0] + ".wav"
        venv_ffmpeg = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".venv", "bin", "ffmpeg"))
        cmd = [venv_ffmpeg, "-y", "-i", save_path, "-ar", "16000", "-ac", "1", target_wav]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
    from aegis_deepspace.pillar2_real import RealVoiceVitalsProvider
    if isinstance(default_coordinator.voice_provider, RealVoiceVitalsProvider):
        provider = default_coordinator.voice_provider
    else:
        provider = RealVoiceVitalsProvider()
        
    result = provider.analyze_audio(target_wav, crew_id=crew_id)
    return result


@app.get("/api/providers/astro_twin", response_model=AstroTwinState)
def get_astro_twin_provider_state():
    """Direct Pillar 3 provider endpoint."""
    return default_coordinator.astro_twin_provider.get_astro_twin_state(active_scenario)


class AstroTwinSimulateRequest(BaseModel):
    astronaut_id: Optional[str] = "CDR-MARK-WATNEY"
    age: Optional[int] = 42
    sex: Optional[str] = "M"
    body_mass_kg: Optional[float] = 80.5
    baseline_hip_bmd: Optional[float] = 1.050
    outage_days: Optional[int] = Field(default=4, ge=0, le=30, description="Consecutive exercise outage days")
    outage_start_day: Optional[int] = Field(default=8, ge=1, le=25, description="Day outage begins")
    recovery_window_days: Optional[int] = Field(default=6, ge=1, le=30, description="Days to recover work deficit")
    nominal_volume_kg: Optional[float] = Field(default=9000.0, ge=1000.0, description="Nominal daily mechanical work")


@app.get("/api/pillar3/analysis")
def get_pillar3_analysis(scenario: Optional[str] = None):
    """Exposes real Pillar 3 ML/ODE simulation pipeline: forward BMD trajectories and countermeasure surge."""
    from aegis_deepspace.pillar3_real import RealAstroTwinProvider
    if isinstance(default_coordinator.astro_twin_provider, RealAstroTwinProvider):
        provider = default_coordinator.astro_twin_provider
    else:
        provider = RealAstroTwinProvider()
    chosen_scenario = scenario or active_scenario or "normal"
    return provider.get_full_analysis(scenario=chosen_scenario)


@app.post("/api/pillar3/simulate")
def simulate_astro_twin(req: AstroTwinSimulateRequest):
    """Runs on-demand digital twin forward simulation with custom astronaut profile and exercise outage."""
    from aegis_deepspace.pillar3_real import RealAstroTwinProvider
    if isinstance(default_coordinator.astro_twin_provider, RealAstroTwinProvider):
        provider = default_coordinator.astro_twin_provider
    else:
        provider = RealAstroTwinProvider()

    profile = {
        "astronaut_id": req.astronaut_id or "CDR-MARK-WATNEY",
        "age": req.age or 42,
        "sex": req.sex or "M",
        "body_mass_kg": req.body_mass_kg or 80.5,
        "baseline_hip_bmd": req.baseline_hip_bmd or 1.050,
        "dietary_calcium_mg": 1100,
        "vitamin_d_iu": 1000
    }
    return provider.simulate_digital_twin(
        astronaut_profile=profile,
        total_days=30,
        outage_start=req.outage_start_day if req.outage_start_day is not None else 8,
        outage_duration=req.outage_days if req.outage_days is not None else 4,
        recovery_window=req.recovery_window_days if req.recovery_window_days is not None else 6,
        nominal_volume=req.nominal_volume_kg if req.nominal_volume_kg is not None else 9000.0
    )


@app.get("/api/state")
def get_current_state():
    """Returns current active telemetry and latest decision."""
    global current_state, current_decision, active_scenario
    return {
        "scenario_id": active_scenario,
        "crew_state": current_state,
        "decision": current_decision
    }


@app.get("/api/scenarios")
def list_scenarios():
    """Lists available demo scenarios."""
    return {
        "scenarios": [
            {"id": "normal", "name": "1. Nominal Baseline", "description": "Nominal radiation, normal voice vitals, balanced digital twin."},
            {"id": "solar_storm", "name": "2. Solar Storm (SPE)", "description": "High-flux solar event detected by Radiation Safe-Route; shelter required."},
            {"id": "voice_anomaly", "name": "3. Voice Vitals Anomaly", "description": "Passive voice log flags cognitive fatigue and neuro-affective strain."},
            {"id": "combined_anomaly", "name": "4. Combined Multimodal Anomaly", "description": "Radiation flare + cognitive slowing + simulated exercise deficit (Synergy Escalation)."},
            {"id": "offline_blackout", "name": "5. Offline Blackout (Mars 20m Delay)", "description": "Earth comms severed; 100% autonomous edge decision using local NASA knowledge."},
            {"id": "uncertain_data", "name": "6. Uncertain / Noisy Telemetry", "description": "Conflicting sensor signals & low SNR audio; surfaces uncertainty rather than false certainty."}
        ]
    }


@app.post("/api/scenarios/{scenario_id}")
def run_scenario(scenario_id: str):
    """Loads and executes a demo scenario."""
    global current_state, current_decision, active_scenario
    if scenario_id == "centrifuge_despin":
        return inject_centrifuge_to_engine()

    if scenario_id not in DEMO_SCENARIOS:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    active_scenario = scenario_id
    current_state = DEMO_SCENARIOS[scenario_id]()
    current_decision = engine.process(current_state)

    # Ingest event into sync store if anomaly or elevated risk
    default_sync_coordinator.record_health_event_from_decision(
        decision=current_decision,
        crew_state=current_state,
        scenario_id=scenario_id
    )

    return {
        "scenario_id": scenario_id,
        "crew_state": current_state,
        "decision": current_decision
    }


@app.post("/api/comms/toggle")
def toggle_comms_mode():
    """Toggles communication between ONLINE and OFFLINE blackout."""
    global current_state, current_decision, active_scenario
    if current_state.comms_mode == CommsMode.ONLINE:
        current_state.comms_mode = CommsMode.OFFLINE
        default_sync_coordinator.comms_manager.set_state(SyncState.OFFLINE, reason="Dashboard Toggle Blackout")
        if active_scenario == "normal":
            active_scenario = "offline_blackout"
            current_state = DEMO_SCENARIOS["offline_blackout"]()
    else:
        current_state.comms_mode = CommsMode.ONLINE
        default_sync_coordinator.comms_manager.set_state(SyncState.ONLINE, reason="Dashboard Restore Earth Link")
        if active_scenario == "offline_blackout":
            active_scenario = "normal"
            current_state = DEMO_SCENARIOS["normal"]()
        
    current_decision = engine.process(current_state)
    return {
        "scenario_id": active_scenario,
        "comms_mode": current_state.comms_mode,
        "crew_state": current_state,
        "decision": current_decision
    }


@app.get("/api/pillar4/decision-trace")
def get_pillar4_decision_trace():
    """Exposes the transparent deterministic Decision Trace explaining why Pillar 4 reached its decision."""
    global current_state, current_decision
    if current_decision.decision_trace is None:
        current_decision = engine.process(current_state)
    return current_decision.decision_trace


class WhatIfDelayRequest(BaseModel):
    delay_minutes: float = Field(default=0.0, ge=0.0, le=120.0, description="Evacuation delay in minutes")
    scenario: Optional[str] = Field(default=None, description="Optional scenario ID to simulate against")


@app.post("/api/pillar4/what-if")
def simulate_evacuation_delay(req: WhatIfDelayRequest):
    """Counterfactual What-If Simulator: Projects radiation exposure from an evacuation delay

    and passes the counterfactual CrewState through the real existing Pillar 4 Decision Engine.
    """
    global current_state, active_scenario
    
    # 1. Base reference state: either from requested scenario or active mission state
    if req.scenario and req.scenario in DEMO_SCENARIOS:
        base_state = DEMO_SCENARIOS[req.scenario]()
    else:
        base_state = current_state.model_copy(deep=True)
        
    baseline_decision = engine.process(base_state)
    
    # 2. Extract P1 parameters: ambient unshielded dose rate, cumulative dose, and current module
    base_rad = base_state.radiation
    current_dose_rate = max(0.01, base_rad.dose_rate_msv_h)
    delay_hours = req.delay_minutes / 60.0
    
    # Deterministic physical projection:
    # Extra exposure incurred while delaying evacuation in the current (less-shielded) compartment
    additional_exposure_msv = round(current_dose_rate * delay_hours, 3)
    projected_cumulative_dose_msv = round(base_rad.cumulative_dose_msv + additional_exposure_msv, 2)
    
    # 3. Create counterfactual RadiationState
    counterfactual_rad = base_rad.model_copy(update={
        "cumulative_dose_msv": projected_cumulative_dose_msv,
        # If delay increases in high flux, acute effective risk level scales deterministically
        "risk_level": "CRITICAL" if (base_rad.spe_active or current_dose_rate >= 0.50 or projected_cumulative_dose_msv >= 6.0)
                      else ("HIGH" if (current_dose_rate >= 0.10 or projected_cumulative_dose_msv >= 3.0) else base_rad.risk_level)
    })
    
    # Also if delay > 15 mins during solar storm, exercise restriction in Astro-Twin persists / increments
    counterfactual_twin = base_state.astro_twin.model_copy()
    if req.delay_minutes >= 30 and base_rad.spe_active:
        counterfactual_twin.exercise_deficit_days = max(counterfactual_twin.exercise_deficit_days, 2)
        counterfactual_twin.countermeasure_status = "RESTRICTED_DELAY"
        
    counterfactual_state = base_state.model_copy(update={
        "radiation": counterfactual_rad,
        "astro_twin": counterfactual_twin
    })
    
    # 4. PASS DIRECTLY THROUGH EXISTING PILLAR 4 DECISION ENGINE (Architecture constraint)
    counterfactual_decision = engine.process(counterfactual_state)
    
    # 5. Delta comparison against immediate action (0 min delay)
    return {
        "disclaimer": "SIMULATION / COUNTERFACTUAL MODEL ONLY - Deterministic operational projection; not an accredited clinical diagnostic model.",
        "delay_minutes": req.delay_minutes,
        "baseline": {
            "projected_exposure_msv": round(base_rad.cumulative_dose_msv, 2),
            "dose_rate_msv_h": round(base_rad.dose_rate_msv_h, 2),
            "risk_level": baseline_decision.risk_level.value,
            "risk_score": baseline_decision.risk_score,
            "recommended_action": baseline_decision.recommended_action
        },
        "counterfactual": {
            "projected_exposure_msv": projected_cumulative_dose_msv,
            "dose_rate_msv_h": round(counterfactual_rad.dose_rate_msv_h, 2),
            "risk_level": counterfactual_decision.risk_level.value,
            "risk_score": counterfactual_decision.risk_score,
            "recommended_action": counterfactual_decision.recommended_action,
            "decision_trace": counterfactual_decision.decision_trace
        },
        "impact": {
            "delta_exposure_msv": round(additional_exposure_msv, 3),
            "delta_risk_score": round(counterfactual_decision.risk_score - baseline_decision.risk_score, 2),
            "level_escalated": counterfactual_decision.risk_level != baseline_decision.risk_level,
            "summary": f"+{additional_exposure_msv:.2f} mSv absorbed ({baseline_decision.risk_level.value} → {counterfactual_decision.risk_level.value})"
        }
    }


class DashboardSimulatorRequest(BaseModel):
    external_flux_msv: float = Field(default=5.0, ge=0.0, le=1000.0)
    current_module: str = Field(default="Module A")
    cognitive_strain: float = Field(default=0.12, ge=0.0, le=1.0)
    fatigue_score: float = Field(default=0.10, ge=0.0, le=1.0)
    hypoxia_marker: float = Field(default=0.04, ge=0.0, le=1.0)
    exercise_deficit_days: int = Field(default=0, ge=0, le=30)
    comms_mode: str = Field(default="ONLINE")
    sync_to_dashboard: bool = Field(default=False)


@app.post("/api/simulator/evaluate")
def evaluate_dashboard_simulator(req: DashboardSimulatorRequest):
    """Interactive Flight Surgeon Simulator endpoint for live dashboard evaluation."""
    global current_state, current_decision
    
    from aegis_deepspace.pillar1_real import RealRadiationProvider, MODULE_METADATA
    rad_provider = RealRadiationProvider()
    
    start_mod = req.current_module if req.current_module in MODULE_METADATA else "Module A"
    mod_meta = MODULE_METADATA.get(start_mod, {"shielding_factor": 0.20, "shielding_g_cm2": 12.0, "name": "Command Deck"})
    shielding_factor = mod_meta["shielding_factor"]
    internal_dose_rate = round(req.external_flux_msv * (1.0 - shielding_factor), 2)
    
    is_spe = req.external_flux_msv >= 20.0
    if internal_dose_rate >= 50.0 or req.external_flux_msv >= 200.0:
        rad_risk_level = "CRITICAL"
    elif internal_dose_rate >= 10.0 or req.external_flux_msv >= 50.0:
        rad_risk_level = "HIGH"
    elif internal_dose_rate >= 1.0 or req.external_flux_msv >= 15.0:
        rad_risk_level = "MEDIUM"
    else:
        rad_risk_level = "LOW"
        
    safest_mod = "Module B"
    evac_route, transit_dose, route_steps = rad_provider.calculate_evacuation_path(
        start_module=start_mod,
        target_module=safest_mod,
        external_flux=req.external_flux_msv
    )
    
    # Build RadiationState
    rad_state = RadiationState(
        risk_level=rad_risk_level,
        dose_rate_msv_h=internal_dose_rate,
        cumulative_dose_msv=round(1.2 + (internal_dose_rate * 0.1), 2),
        spe_active=is_spe,
        current_module=f"{start_mod}: {mod_meta.get('name', start_mod)}",
        recommended_safe_module=f"{safest_mod}: Storm Shelter",
        shielding_rating_g_cm2=mod_meta.get("shielding_g_cm2", 12.0),
        confidence=0.95
    )
    
    # Build Voice Vitals Modeling (Pillar 2)
    dev_z = round(((req.cognitive_strain - 0.12) * 4.5) + ((req.fatigue_score - 0.10) * 3.5), 1)
    voice_state = VoiceVitalsState(
        fatigue_score=req.fatigue_score,
        cognitive_strain_score=req.cognitive_strain,
        hypoxia_indicator=req.hypoxia_marker,
        deviation_from_baseline_z=max(0.1, dev_z),
        confidence=0.92
    )
    
    # Build Astro-Twin Modeling (Pillar 3)
    bone_loss = round(0.8 + (0.16 * req.exercise_deficit_days), 2)
    muscle_loss = round(1.5 + (0.42 * req.exercise_deficit_days), 2)
    countermeasure_status = "CRITICAL DEFICIT" if req.exercise_deficit_days >= 5 else ("MODERATE DEFICIT" if req.exercise_deficit_days >= 2 else "NOMINAL")
    twin_state = AstroTwinState(
        projected_bone_loss_pct_mo=bone_loss,
        projected_muscle_atrophy_pct=muscle_loss,
        exercise_deficit_days=req.exercise_deficit_days,
        countermeasure_status=countermeasure_status,
        prediction_horizon_days=14,
        confidence=0.90
    )
    
    # Synthesize Combined CrewState & Compute Pillar 4 Decision
    simulated_state = CrewState(
        comms_mode=CommsMode.OFFLINE if req.comms_mode.upper() == "OFFLINE" else CommsMode.ONLINE,
        data_freshness_seconds=3,
        radiation=rad_state,
        voice_vitals=voice_state,
        astro_twin=twin_state
    )
    
    decision = engine.process(simulated_state)
    
    if req.sync_to_dashboard:
        current_state = simulated_state
        current_decision = decision
        
    return {
        "decision": decision,
        "crew_state": simulated_state,
        "simulation_summary": {
            "internal_dose_rate_msv_h": internal_dose_rate,
            "shielding_pct": int(shielding_factor * 100),
            "evacuation_route": evac_route,
            "transit_dose_msv": round(transit_dose, 2),
            "safest_module": safest_mod,
            "bone_loss_pct_mo": bone_loss,
            "muscle_atrophy_pct": muscle_loss,
            "baseline_deviation_sigma": dev_z,
            "synergy_active": (decision.risk_fusion.synergy_score > 0) if decision.risk_fusion else False,
            "synergy_score": decision.risk_fusion.synergy_score if decision.risk_fusion else 0.0,
            "formula": decision.risk_fusion.formula if decision.risk_fusion else ""
        }
    }


@app.post("/api/process")
def process_custom_telemetry(state: CrewState):
    """Ingests custom raw telemetry and computes a decision object."""
    global current_state, current_decision
    current_state = state
    current_decision = engine.process(current_state)
    return current_decision

# ===================================================================
# Centrifugal Ring Spin-Down & Gravity Gradient Disruption Simulator
# ===================================================================
from aegis_deepspace.centrifuge_sim import (
    CentrifugeSimConfig,
    CentrifugeSimulationResult,
    default_centrifuge_simulator
)

latest_centrifuge_result: Optional[CentrifugeSimulationResult] = None


@app.get("/api/centrifuge/state")
def get_centrifuge_state():
    """Returns the current artificial gravity centrifugal simulation status."""
    global latest_centrifuge_result
    if latest_centrifuge_result is None:
        latest_centrifuge_result = default_centrifuge_simulator.run_simulation()
    return latest_centrifuge_result


@app.post("/api/centrifuge/simulate")
def simulate_centrifuge(cfg: CentrifugeSimConfig):
    """Executes the centrifugal ring spin-down simulation with specified configuration."""
    global latest_centrifuge_result
    latest_centrifuge_result = default_centrifuge_simulator.run_simulation(cfg)
    return latest_centrifuge_result


@app.post("/api/centrifuge/inject")
def inject_centrifuge_to_engine():
    """Injects the centrifugal despin emergency state into the active Flight Surgeon Decision Engine."""
    global current_state, current_decision, latest_centrifuge_result, active_scenario
    if latest_centrifuge_result is None:
        latest_centrifuge_result = default_centrifuge_simulator.run_simulation()
    active_scenario = "centrifuge_despin"
    current_state = default_centrifuge_simulator.convert_to_crew_state(latest_centrifuge_result)
    current_decision = engine.process(current_state)
    return {
        "status": "injected",
        "scenario_id": active_scenario,
        "crew_state": current_state,
        "decision": current_decision,
        "centrifuge_telemetry": latest_centrifuge_result
    }


class CentrifugeActuationRequest(BaseModel):
    lock_magnetic_deck: bool = True
    dispense_antiemetics: bool = True
    inflate_braslet_cuffs: bool = True
    eclss_strobe_suppression: bool = True


@app.post("/api/centrifuge/actuate")
def actuate_centrifuge_countermeasures(req: CentrifugeActuationRequest):
    """Actuates autonomous medical and mechanical countermeasures to stabilize the crew."""
    global latest_centrifuge_result, current_state, current_decision
    cfg = latest_centrifuge_result.config if latest_centrifuge_result else CentrifugeSimConfig()
    cfg.magnetic_deck_locked = req.lock_magnetic_deck
    cfg.countermeasures_active = (req.dispense_antiemetics or req.inflate_braslet_cuffs)
    latest_centrifuge_result = default_centrifuge_simulator.run_simulation(cfg)
    
    # If currently active scenario is centrifuge_despin, update mission control decision as well
    if active_scenario == "centrifuge_despin":
        current_state = default_centrifuge_simulator.convert_to_crew_state(latest_centrifuge_result)
        current_decision = engine.process(current_state)
        
    return {
        "status": "actuated",
        "result": latest_centrifuge_result,
        "stabilized": True
    }


@app.post("/api/chat", response_model=ChatResponse)
def copilot_chat(req: ChatRequest):
    """Low-resource Two-Tier AI Flight Surgeon Copilot endpoint."""
    global current_state, current_decision, active_scenario, latest_centrifuge_result
    
    try:
        response = default_copilot.ask(
            query=req.message,
            crew_state=current_state,
            decision=current_decision,
            active_scenario=active_scenario,
            centrifuge_result=latest_centrifuge_result,
            session_id=req.session_id or "default"
        )
        
        # If the copilot triggered an action, execute it on the server
        if response.action_triggered:
            action_data = response.action_triggered
            action_type = action_data.get("action")
            if action_type == "set_scenario":
                scen_id = action_data.get("scenario_id", "normal")
                if scen_id == "centrifuge_despin":
                    from aegis_deepspace.centrifuge_sim import default_centrifuge_simulator, CentrifugeSimConfig
                    active_scenario = "centrifuge_despin"
                    latest_centrifuge_result = default_centrifuge_simulator.run_simulation(CentrifugeSimConfig())
                    current_state = default_centrifuge_simulator.convert_to_crew_state(latest_centrifuge_result)
                    current_decision = engine.process(current_state)
                elif scen_id in DEMO_SCENARIOS:
                    active_scenario = scen_id
                    current_state = DEMO_SCENARIOS[scen_id]()
                    current_decision = engine.process(current_state)
            elif action_type == "toggle_blackout":
                new_mode = CommsMode.OFFLINE if current_state.comms_mode == CommsMode.ONLINE else CommsMode.ONLINE
                current_state.comms_mode = new_mode
                current_decision = engine.process(current_state)
            elif action_type == "actuate_centrifuge":
                from aegis_deepspace.centrifuge_sim import default_centrifuge_simulator, CentrifugeSimConfig
                cfg = latest_centrifuge_result.config if latest_centrifuge_result else CentrifugeSimConfig()
                cfg.magnetic_deck_locked = action_data.get("lock_magnetic_deck", True)
                cfg.countermeasures_active = action_data.get("dispense_antiemetics", True)
                latest_centrifuge_result = default_centrifuge_simulator.run_simulation(cfg)
                if active_scenario == "centrifuge_despin":
                    current_state = default_centrifuge_simulator.convert_to_crew_state(latest_centrifuge_result)
                    current_decision = engine.process(current_state)
                    
        return response
    except Exception as err:
        import traceback
        traceback.print_exc()
        fallback_reply = (
            f"**Autonomous AI Flight Surgeon Diagnostic Note:**\n\n"
            f"- **Habitat Status:** Risk Score `{current_decision.risk_score:.2f}` ({current_decision.risk_level.value})\n"
            f"- **Telemetry Channels:** Radiation `{current_state.radiation.dose_rate_msv_h:.2f} mSv/h` | "
            f"Voice Strain `{current_state.voice_vitals.cognitive_strain_score:.2f}` | "
            f"Bone Loss Projection `{current_state.astro_twin.projected_bone_loss_pct_mo:.1f}%/mo`\n"
            f"- **Clinical Recommendation:** {current_decision.recommended_action}\n\n"
            f"Local telemetry bus is operational. Ask about **radiation limits**, **voice fatigue**, **Astro-Twin**, or **centrifuge status**."
        )
        return ChatResponse(
            reply=fallback_reply,
            intent="OFFLINE_FALLBACK",
            confidence=0.90,
            citations=["NASA-STD-3001 Space Flight Human-System Standards"],
            telemetry_context={
                "risk_score": current_decision.risk_score,
                "risk_level": current_decision.risk_level.value,
                "dose_rate_msv_h": current_state.radiation.dose_rate_msv_h
            },
            suggested_prompts=[
                "Check current mission risk score",
                "What are NASA radiation limits?",
                "Simulate centrifuge governor failure"
            ]
        )
    

@app.get("/api/mission/dossier", response_model=NasaMedicalDossier)
def get_mission_medical_dossier():
    """Generates the real-time NASA-STD-3001 Flight Surgeon Medical Event Dossier."""
    global current_state, current_decision, active_scenario, latest_centrifuge_result
    return generate_medical_dossier(
        crew_state=current_state,
        decision=current_decision,
        active_scenario=active_scenario,
        centrifuge_result=latest_centrifuge_result
    )


@app.get("/api/mission/dossier/markdown")
def get_mission_medical_dossier_markdown():
    """Returns the formatted NASA Med-B Briefing in Markdown for display or export."""
    global current_state, current_decision, active_scenario, latest_centrifuge_result
    dossier = generate_medical_dossier(
        crew_state=current_state,
        decision=current_decision,
        active_scenario=active_scenario,
        centrifuge_result=latest_centrifuge_result
    )
    md_content = format_dossier_markdown(dossier)
    return {
        "dossier_id": dossier.dossier_id,
        "markdown": md_content,
        "checksum": dossier.telemetry_checksum_sha256
    }


@app.get("/api/mission/dossier/download")
def download_mission_medical_dossier():
    """Directly downloads the NASA Flight Surgeon Medical Dossier as an official .md document."""
    global current_state, current_decision, active_scenario, latest_centrifuge_result
    dossier = generate_medical_dossier(
        crew_state=current_state,
        decision=current_decision,
        active_scenario=active_scenario,
        centrifuge_result=latest_centrifuge_result
    )
    md_content = format_dossier_markdown(dossier)
    filename = f"NASA_MEDB_DEBRIEF_{dossier.dossier_id}.md"
    return Response(
        content=md_content,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


# ===================================================================
# Asymmetric Federated Sync & Deep Space Communications
# ===================================================================

class CommsStateChangeRequest(BaseModel):
    state: str = Field(..., description="ONLINE or OFFLINE")
    reason: Optional[str] = "Operator manual command"
    force_failure: Optional[bool] = False


class EdgeTrainingRequest(BaseModel):
    client_target: str = Field(default="both", description="both, watney, or vogel")
    num_samples_client1: int = Field(default=40, ge=5, le=500)
    num_samples_client2: int = Field(default=35, ge=5, le=500)


@app.get("/api/sync/status", response_model=SyncStatusOverview)
def get_sync_status():
    """Returns the real-time status of the deep-space communications and federated sync subsystem."""
    return default_sync_coordinator.comms_manager.get_status_overview()


@app.post("/api/sync/comms/drop")
def drop_dsn_link():
    """Simulates immediate DSN carrier drop / occultation, transitioning state to OFFLINE immediately."""
    global current_state
    reason = "DSN link lost. Onboard monitoring continues; synchronization paused."
    new_state = default_sync_coordinator.comms_manager.simulate_dsn_drop(reason=reason)
    current_state.comms_mode = CommsMode.OFFLINE
    return {
        "status": "success",
        "comms_state": new_state.value,
        "message": reason
    }


@app.post("/api/sync/comms/state")
def set_comms_state(req: CommsStateChangeRequest):
    """Sets communication link state to ONLINE or OFFLINE, with optional failure simulation."""
    global current_state
    target_state = SyncState.ONLINE if req.state.upper() == "ONLINE" else SyncState.OFFLINE
    if req.force_failure:
        default_sync_coordinator.comms_manager.force_transient_failure = True
    result_state = default_sync_coordinator.comms_manager.set_state(target_state, reason=req.reason or "API Request")
    current_state.comms_mode = CommsMode.ONLINE if result_state == SyncState.ONLINE else CommsMode.OFFLINE
    return {
        "status": "success",
        "comms_state": result_state.value,
        "forced_failure": default_sync_coordinator.comms_manager.force_transient_failure
    }


@app.post("/api/sync/comms/toggle")
def toggle_sync_comms():
    """Toggles communication link state between ONLINE and OFFLINE."""
    global current_state
    new_state = default_sync_coordinator.comms_manager.toggle_connection(reason="Operator toggle API")
    current_state.comms_mode = CommsMode.ONLINE if new_state == SyncState.ONLINE else CommsMode.OFFLINE
    return {"status": "success", "comms_state": new_state.value}


@app.post("/api/sync/trigger")
def trigger_synchronization(batch_size: int = 50, force: bool = False):
    """Manually triggers store-and-forward batch transmission to Houston Ground Control."""
    return default_sync_coordinator.comms_manager.synchronize_pending_records(batch_size=batch_size, force=force)


@app.get("/api/sync/queue/pending")
def get_pending_sync_queue():
    """Returns all unsynchronized records currently held in the spacecraft persistent queue."""
    return {
        "health_events": default_sync_coordinator.store.get_pending_health_events(limit=50),
        "telemetry_summaries": default_sync_coordinator.store.get_pending_telemetry_summaries(limit=50),
        "model_updates": default_sync_coordinator.store.get_pending_model_updates(limit=20)
    }


@app.get("/api/sync/ground/events")
def get_ground_received_events(limit: int = 100):
    """Returns health events downlinked and stored at Houston Ground Control."""
    return {
        "events": default_sync_coordinator.store.get_ground_health_events(limit=limit)
    }


@app.get("/api/sync/ground/models")
def get_ground_models():
    """Returns global federated anomaly model versions and aggregation rounds."""
    latest = default_sync_coordinator.store.get_latest_global_model()
    all_models = default_sync_coordinator.store.get_all_global_models()
    return {
        "latest_model": latest,
        "history": all_models
    }


@app.post("/api/sync/federated/train")
def train_edge_federated_models(req: EdgeTrainingRequest):
    """Triggers local training on simulated edge clients (Watney / Vogel), creating queued model updates."""
    updates = default_sync_coordinator.trigger_edge_client_training(
        client_target=req.client_target,
        num_samples_client1=req.num_samples_client1,
        num_samples_client2=req.num_samples_client2
    )
    return {
        "status": "training_completed",
        "updates_queued": len(updates),
        "updates": [u.model_dump() for u in updates]
    }


@app.get("/api/sync/logs")
def get_sync_activity_logs(limit: int = 50):
    """Returns audit logs of communication transitions and synchronization operations."""
    return {
        "logs": default_sync_coordinator.store.get_activity_logs(limit=limit),
        "state_history": default_sync_coordinator.store.get_state_history(limit=20)
    }


@app.post("/api/sync/demo/run")
def run_sync_demonstration():
    """Runs the full reproducible 12-step offline-to-online mission demonstration sequence."""
    return default_sync_coordinator.run_e2e_demonstration()


@app.post("/api/sync/demo/reset")
def reset_sync_demo():
    """Clears all synchronization queues and ground archives back to initial state."""
    default_sync_coordinator.store.reset_all()
    default_sync_coordinator.aggregator._ensure_baseline_model()
    default_sync_coordinator.comms_manager.set_state(SyncState.ONLINE, reason="Reset demo baseline")
    return {"status": "reset_completed"}


# ===================================================================
# Feature B: Explainable AI Health Alerts Using SHAP
# ===================================================================

class CustomExplainRequest(BaseModel):
    features: Dict[str, float] = Field(..., description="Feature values: rad_rate, fatigue, strain, hypoxia, bone_loss, shear")
    model_version: Optional[str] = None
    alert_id: Optional[str] = None


@app.get("/api/xai/models")
def get_xai_models():
    """Returns available explainable models, feature schemas, and baseline expectations."""
    global_model = default_sync_coordinator.aggregator.get_or_create_global_model()
    return {
        "models": [
            {
                "name": "Multimodal Crew Anomaly Detector",
                "version": global_model.version,
                "type": "linear_additive_anomaly_score",
                "explainer": "shap.LinearExplainer (Exact Shapley)",
                "features": FEATURE_METADATA,
                "weights": global_model.global_weights,
                "classification_thresholds": {
                    "NOMINAL": "< 0.30",
                    "MEDIUM": "0.30 - 0.50",
                    "HIGH": "0.50 - 0.70",
                    "CRITICAL": ">= 0.70"
                }
            },
            {
                "name": "Astro-Twin Residual Gradient Boosting Model",
                "version": "v1.0.0",
                "type": "gradient_boosting_regressor",
                "explainer": "shap.TreeExplainer",
                "feature_count": 11
            }
        ]
    }


@app.get("/api/xai/explain/decision", response_model=ShapAlertExplanation)
def explain_current_decision():
    """Generates a SHAP explanation for the current active CrewState and Decision."""
    global current_state, current_decision
    features = default_xai_engine.extract_features_from_state(current_state)
    alert_id = current_decision.decision_id if current_decision else "DEC-CURRENT"
    return default_xai_engine.explain_crew_anomaly(features, alert_id=alert_id)


@app.get("/api/xai/explain/event/{event_id}")
def explain_health_event_by_id(event_id: str):
    """Retrieves or calculates the SHAP explanation for a specific health event record."""
    # Check onboard store
    events = default_sync_coordinator.store.get_pending_health_events(limit=200)
    target = next((e for e in events if e.event_id == event_id), None)

    # Check ground archive
    if not target:
        ground_events = default_sync_coordinator.store.get_ground_health_events(limit=200)
        target_dict = next((g for g in ground_events if g["event_id"] == event_id), None)
        if target_dict:
            if target_dict.get("explanation"):
                return target_dict["explanation"]
            # Fallback calculate from payload
            return default_xai_engine.explain_crew_anomaly(
                features=target_dict.get("payload", {}),
                alert_id=event_id
            )

    if target:
        if target.explanation:
            return target.explanation
        return default_xai_engine.explain_health_event(target)

    # If not found
    raise HTTPException(status_code=404, detail=f"Health event '{event_id}' not found in onboard or ground stores.")


@app.post("/api/xai/explain/custom", response_model=ShapAlertExplanation)
def explain_custom_features(req: CustomExplainRequest):
    """On-demand SHAP explanation for arbitrary biometric input values."""
    return default_xai_engine.explain_crew_anomaly(
        features=req.features,
        model_version=req.model_version,
        alert_id=req.alert_id or f"CUSTOM-{int(time.time())}"
    )


@app.post("/api/xai/demo/scenario")
def run_xai_demo_workflow():
    """Executes the complete reproducible Feature B demonstration scenario:
    1. Nominal baseline sample
    2. Anomaly 1 detected with SHAP explanation (ONLINE)
    3. Simulated DSN carrier drop (OFFLINE)
    4. Anomaly 2 detected with SHAP explanation persisted locally
    5. Link restored (ONLINE) with store-and-forward batch transmission
    6. Ground receipt verification preserving original model version and explanation.
    """
    # 1. Reset demo state
    default_sync_coordinator.store.reset_all()
    default_sync_coordinator.aggregator._ensure_baseline_model()
    default_sync_coordinator.comms_manager.set_state(SyncState.ONLINE, reason="XAI Demo Init ONLINE")

    # Step 1: Normal Sample
    normal_features = {
        "rad_rate": 0.02,
        "fatigue": 0.15,
        "strain": 0.12,
        "hypoxia": 0.04,
        "bone_loss": 0.80,
        "shear": 0.00
    }
    nom_expl = default_xai_engine.explain_crew_anomaly(normal_features, alert_id="ALERT-NOM-01")

    # Step 2: Anomaly 1 (Solar Flare + Cognitive Strain)
    anom1_features = {
        "rad_rate": 1.35,
        "fatigue": 0.25,
        "strain": 0.55,
        "hypoxia": 0.06,
        "bone_loss": 0.85,
        "shear": 0.00
    }
    anom1_expl = default_xai_engine.explain_crew_anomaly(anom1_features, alert_id="EVT-XAI-SPE-01")
    evt1 = HealthEventRecord(
        event_id="EVT-XAI-SPE-01",
        severity=anom1_expl.severity_category,
        occurrence_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_pillar="Pillar 1: Radiation Safe-Route",
        title="SPE Solar Particle Acute Radiation Spike",
        description="Dose rate surged to 1.35 mSv/h with elevated crew cognitive strain.",
        action_recommended="Immediate evacuation to Module B Water-Wall Storm Shelter.",
        risk_score=anom1_expl.predicted_score,
        payload=anom1_features,
        telemetry_checksum_sha256=hashlib.sha256(b"EVT-XAI-SPE-01").hexdigest()[:24].upper(),
        idempotency_key="DEMO:XAI:SPE:01",
        sync_status=SyncRecordStatus.PENDING,
        explanation=anom1_expl.model_dump() if hasattr(anom1_expl, "model_dump") else anom1_expl.dict()
    )
    default_sync_coordinator.store.enqueue_health_event(evt1)
    sync_res1 = default_sync_coordinator.comms_manager.synchronize_pending_records()

    # Step 3: Disconnect Link (OFFLINE BLACKOUT)
    default_sync_coordinator.comms_manager.simulate_dsn_drop(reason="XAI Demo: Mars Conjunction Blackout")

    # Step 4: Anomaly 2 generated OFFLINE (Acoustic Hypoxia & Fatigue)
    anom2_features = {
        "rad_rate": 0.03,
        "fatigue": 0.85,
        "strain": 0.60,
        "hypoxia": 0.70,
        "bone_loss": 0.90,
        "shear": 0.00
    }
    anom2_expl = default_xai_engine.explain_crew_anomaly(anom2_features, alert_id="EVT-XAI-HYPOX-02")
    evt2 = HealthEventRecord(
        event_id="EVT-XAI-HYPOX-02",
        severity=anom2_expl.severity_category,
        occurrence_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_pillar="Pillar 2: Voice Vitals",
        title="Acoustic Hypoxia & Neuro-Affective Exhaustion",
        description="Speech latency and vocal formant shift indicate acute hypoxia.",
        action_recommended="Deploy supplemental O2; verify ECLSS cabin pressure.",
        risk_score=anom2_expl.predicted_score,
        payload=anom2_features,
        telemetry_checksum_sha256=hashlib.sha256(b"EVT-XAI-HYPOX-02").hexdigest()[:24].upper(),
        idempotency_key="DEMO:XAI:HYPOX:02",
        sync_status=SyncRecordStatus.PENDING,
        explanation=anom2_expl.model_dump() if hasattr(anom2_expl, "model_dump") else anom2_expl.dict()
    )
    default_sync_coordinator.store.enqueue_health_event(evt2)
    pending_offline = default_sync_coordinator.store.get_pending_health_events()

    # Step 5: Restore Link (ONLINE) and synchronize to Houston
    default_sync_coordinator.comms_manager.set_state(SyncState.ONLINE, reason="XAI Demo: Restore Link via Deep Space Network")
    sync_res2 = default_sync_coordinator.comms_manager.synchronize_pending_records()

    # Step 6: Ground verification
    ground_events = default_sync_coordinator.store.get_ground_health_events()

    return {
        "demo_status": "COMPLETED",
        "step1_nominal": nom_expl.model_dump() if hasattr(nom_expl, "model_dump") else nom_expl.dict(),
        "step2_alert_online": anom1_expl.model_dump() if hasattr(anom1_expl, "model_dump") else anom1_expl.dict(),
        "step3_comms_state": "OFFLINE",
        "step4_offline_alert_saved": anom2_expl.model_dump() if hasattr(anom2_expl, "model_dump") else anom2_expl.dict(),
        "step4_offline_pending_count": len(pending_offline),
        "step5_reconnected_sync": sync_res2,
        "step6_ground_records_count": len(ground_events),
        "preserved_explanations": [
            {
                "event_id": g["event_id"],
                "model_version": (g.get("explanation") or {}).get("model_version"),
                "top_feature": ((g.get("explanation") or {}).get("top_features_summary") or ["N/A"])[0]
            }
            for g in ground_events
        ]
    }


@app.post("/api/xai/demo/reset")
def reset_xai_demo():
    """Resets the XAI demonstration state."""
    default_sync_coordinator.store.reset_all()
    default_sync_coordinator.aggregator._ensure_baseline_model()
    default_sync_coordinator.comms_manager.set_state(SyncState.ONLINE, reason="XAI Demo Reset")
    return {"status": "xai_demo_reset_completed"}



@app.get("/health")
@app.head("/health")
def health_check():
    """Health check endpoint for container and uptime monitoring."""
    return {"status": "ok", "app": "aegis-deepspace"}


# Mount static assets for frontend dashboard
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    class NoCacheStaticFiles(StaticFiles):
        """Custom StaticFiles subclass ensuring development asset changes are never stale-cached."""
        def file_response(self, *args, **kwargs) -> Response:
            response = super().file_response(*args, **kwargs)
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response

    app.mount("/static", NoCacheStaticFiles(directory=static_dir), name="static")

    @app.api_route("/", methods=["GET", "HEAD"])
    def serve_dashboard():
        return FileResponse(
            os.path.join(static_dir, "index.html"),
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
