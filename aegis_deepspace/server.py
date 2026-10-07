"""FastAPI Web Server for Aegis-DeepSpace Pillar 4 Autonomous Decision Engine MVP."""

import os
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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


@app.post("/api/pillar2/process_audio")
def process_voice_audio(req: AudioProcessRequest):
    """Processes an audio recording through the real Whisper STT, DistilBERT, and MFCC-CNN pipeline."""
    from aegis_deepspace.pillar2_real import RealVoiceVitalsProvider
    if isinstance(default_coordinator.voice_provider, RealVoiceVitalsProvider):
        provider = default_coordinator.voice_provider
    else:
        provider = RealVoiceVitalsProvider()
    return provider.analyze_audio(req.audio_path)


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
    global current_state, current_decision
    return {
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
    if scenario_id not in DEMO_SCENARIOS:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    active_scenario = scenario_id
    current_state = DEMO_SCENARIOS[scenario_id]()
    current_decision = engine.process(current_state)
    return {
        "scenario_id": scenario_id,
        "crew_state": current_state,
        "decision": current_decision
    }


@app.post("/api/comms/toggle")
def toggle_comms_mode():
    """Toggles communication between ONLINE and OFFLINE blackout."""
    global current_state, current_decision
    if current_state.comms_mode == CommsMode.ONLINE:
        current_state.comms_mode = CommsMode.OFFLINE
    else:
        current_state.comms_mode = CommsMode.ONLINE
        
    current_decision = engine.process(current_state)
    return {
        "comms_mode": current_state.comms_mode,
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


@app.post("/api/process")
def process_custom_telemetry(state: CrewState):
    """Ingests custom raw telemetry and computes a decision object."""
    global current_state, current_decision
    current_state = state
    current_decision = engine.process(current_state)
    return current_decision


# Mount static assets for frontend dashboard
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    def serve_dashboard():
        return FileResponse(os.path.join(static_dir, "index.html"))
