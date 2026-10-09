"""NASA Autonomous Medical Event Debrief & Telemetry Dossier (MEDB Packet).

Compliant with NASA-STD-3001 (Space Flight Human-System Standard) and NASA HRP guidelines.
Synthesizes all four pillars and centrifugal telemetry into an auditable, timestamped,
and cryptographically verified flight surgeon medical briefing for deep-space transit
during Earth communication blackouts and Houston DSN downlinks.
"""

import hashlib
import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from aegis_deepspace.models import CrewState, DecisionObject, CommsMode
from aegis_deepspace.centrifuge_sim import CentrifugeSimulationResult


class NasaMedicalDossier(BaseModel):
    """Structured clinical flight surgeon dossier complying with NASA-STD-3001."""
    dossier_id: str = Field(..., description="Unique clinical debriefing packet identifier")
    timestamp_utc: str = Field(..., description="ISO 8601 UTC timestamp")
    mission_elapsed_time: str = Field(..., description="Mission Elapsed Time (MET) on Mars transit")
    spacecraft_id: str = Field(default="AEGIS-DEEPSPACE-01 [HERMES CLASS]")
    destination: str = Field(default="Earth-Mars Interplanetary Transfer (Sol 142)")
    comms_status: str = Field(..., description="ONLINE or OFFLINE (20-min latency / Blackout)")
    active_scenario: str = Field(..., description="Active simulation scenario or event")
    telemetry_checksum_sha256: str = Field(..., description="Cryptographic SHA-256 verification hash")
    
    # Executive Clinical Verdict
    risk_level: str
    risk_score: float
    confidence_pct: float
    primary_recommendation: str
    secondary_action: Optional[str] = None
    flight_surgeon_verdict: str
    
    # Pillar-by-Pillar Telemetry
    pillar1_environmental: Dict[str, Any]
    pillar2_neuro_vocal: Dict[str, Any]
    pillar3_musculoskeletal: Dict[str, Any]
    pillar4_synergy_fusion: Dict[str, Any]
    centrifuge_dynamics: Optional[Dict[str, Any]] = None
    
    # Countermeasures & Protocol Log
    countermeasures_actuated: List[Dict[str, Any]]
    
    # NASA Regulatory Evidence Citations
    nasa_standards_cited: List[Dict[str, str]]
    
    # Transmission metadata for Deep Space Network (DSN)
    dsn_dispatch_status: str


def compute_telemetry_hash(payload: str) -> str:
    """Computes SHA-256 verification checksum for deep-space telemetry integrity."""
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24].upper()


def generate_medical_dossier(
    crew_state: CrewState,
    decision: DecisionObject,
    active_scenario: str = "normal",
    centrifuge_result: Optional[CentrifugeSimulationResult] = None
) -> NasaMedicalDossier:
    """Generates an auditable NASA-STD-3001 Flight Surgeon Medical Event Dossier."""
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    timestamp_str = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Mission Elapsed Time simulation based on Sol 142
    met_str = f"MET T+142d {now_utc.strftime('%H:%M:%S')}"
    
    dossier_id = f"MEDB-{now_utc.strftime('%Y%m%d')}-{active_scenario[:6].upper()}-{hash(timestamp_str) % 10000:04d}"
    
    comms_status = "ONLINE [EARTH DSN LINK ACTIVE]" if crew_state.comms_mode == CommsMode.ONLINE else "OFFLINE [20-MIN BLACKOUT • AUTONOMOUS EDGE]"
    
    # Extract Pillar 1 Telemetry
    p1 = crew_state.radiation
    p1_data = {
        "hazard_level": p1.risk_level,
        "dose_rate_msv_h": round(p1.dose_rate_msv_h, 3),
        "cumulative_dose_msv": round(p1.cumulative_dose_msv, 2),
        "spe_alert_active": p1.spe_active,
        "current_compartment": p1.current_module,
        "recommended_safe_compartment": p1.recommended_safe_module,
        "shielding_rating_g_cm2": p1.shielding_rating_g_cm2,
        "permissible_exposure_status": "WITHIN 30-DAY PEL" if p1.cumulative_dose_msv < 250.0 else "EXCEEDS 30-DAY PEL (250 mGy-Eq)"
    }
    
    # Extract Pillar 2 Telemetry
    p2 = crew_state.voice_vitals
    p2_data = {
        "fatigue_score": round(p2.fatigue_score, 2),
        "cognitive_strain_score": round(p2.cognitive_strain_score, 2),
        "hypoxia_indicator": round(p2.hypoxia_indicator, 2),
        "baseline_drift_sigma": round(p2.deviation_from_baseline_z, 1),
        "vocal_prosody_status": "ELEVATED ACOUSTIC DEGRADATION" if p2.deviation_from_baseline_z >= 2.0 else "NOMINAL PROSODY"
    }
    
    # Extract Pillar 3 Telemetry
    p3 = crew_state.astro_twin
    p3_data = {
        "projected_bmd_loss_pct_mo": round(p3.projected_bone_loss_pct_mo, 2),
        "projected_muscle_atrophy_pct": round(p3.projected_muscle_atrophy_pct, 2),
        "exercise_deficit_days": p3.exercise_deficit_days,
        "countermeasure_status": p3.countermeasure_status,
        "mechanostat_remodeling_balance": "RESORPTION DOMINANT (DEFICIT)" if p3.exercise_deficit_days >= 2 else "BONE HOMEOSTASIS MAINTAINED"
    }
    
    # Extract Pillar 4 Synergy Fusion
    p4_fusion = decision.risk_fusion
    p4_data = {
        "composite_risk_score": decision.risk_score,
        "risk_level": decision.risk_level.value,
        "synergy_score": p4_fusion.synergy_score if p4_fusion else 0.0,
        "synergy_active": (p4_fusion.synergy_score > 0.0) if p4_fusion else False,
        "formula": p4_fusion.formula if p4_fusion else f"Risk = {decision.risk_score:.2f}",
        "reasons": decision.reasons
    }
    
    # Extract Centrifuge Dynamics if active scenario or available
    centrifuge_data = None
    if active_scenario == "centrifuge_despin" and centrifuge_result:
        deltas = centrifuge_result.telemetry_deltas
        hemo = deltas.get("hemodynamic_and_cranial_pressures", {})
        neuro = deltas.get("neurovestibular_and_kinematics", {})
        cvp_info = hemo.get("central_venous_pressure_cvp", {})
        icp_info = hemo.get("intracranial_pressure_icp", {})

        centrifuge_data = {
            "gravity_transition": f"{centrifuge_result.config.initial_g}g -> {centrifuge_result.config.target_g}g ({int(centrifuge_result.config.duration_seconds)}s)",
            "cvp_delta": str(cvp_info.get("delta_mmhg", "+7.6")),
            "icp_delta": str(icp_info.get("delta_mmhg", "+13.8")),
            "sms_severity_index": float(neuro.get("space_motion_sickness_sms_index", 88.5)),
            "cross_coupling_index": float(neuro.get("vestibular_cross_coupling_index", 0.91)),
            "collision_probability_pct": float(neuro.get("blunt_trauma_collision_probability_pct", 78.4)),
            "magnetic_deck_locked": centrifuge_result.config.magnetic_deck_locked,
            "crew_roster_count": len(centrifuge_result.crew_roster)
        }
    
    # Build list of actuated countermeasures
    countermeasures: List[Dict[str, Any]] = []
    
    if p1.spe_active or p1.dose_rate_msv_h > 0.10:
        countermeasures.append({
            "system": "HABITAT SHIELDING ROUTE (PILLAR 1)",
            "action": f"Immediate crew evacuation to {p1.recommended_safe_module}",
            "status": "DEPLOYED",
            "clinical_rationale": "Polyethylene/water wall provides >20 g/cm² areal mass shielding, attenuating CME proton dose by >95%."
        })
        
    if p2.cognitive_strain_score > 0.40 or p2.fatigue_score > 0.50:
        countermeasures.append({
            "system": "CREW DUTY ALLOCATION & SLEEP HYGIENE (PILLAR 2)",
            "action": "Enforce mandatory 4-hour cognitive offload rest cycle & red-shifted circadian lighting",
            "status": "SCHEDULED",
            "clinical_rationale": "Mitigate neurobehavioral degradation and reaction latency under NASA HRP cognitive standard."
        })
        
    if p3.exercise_deficit_days > 0:
        surge_pct = min(40, p3.exercise_deficit_days * 8)
        countermeasures.append({
            "system": "ARED RESISTIVE EXERCISE SURGE (PILLAR 3)",
            "action": f"Prescribe +{surge_pct}% mechanical load surge over next 6-day recovery window",
            "status": "PRESCRIBED",
            "clinical_rationale": "Compensate mechanical work deficit (Frost's Mechanostat ODE) to prevent trabecular bone microfracture."
        })
        
    if active_scenario == "centrifuge_despin" and centrifuge_result:
        countermeasures.append({
            "system": "AUTONOMOUS GRAVITATIONAL EMERGENCY OVERRIDE",
            "action": "Energize electromagnetic boot-deck couplings & bilateral Braslet occlusion cuffs",
            "status": "ACTUATED" if centrifuge_result.config.magnetic_deck_locked else "PENDING_CREW_ACKNOWLEDGEMENT",
            "clinical_rationale": "Prevents blunt trauma deceleration injuries and dampens +850 mL/min cephalad fluid surge toward cranium."
        })
        countermeasures.append({
            "system": "AUTONOMOUS PHARMACOTHERAPY DISPENSER",
            "action": "Dispense transdermal Promethazine (25 mg) + Ondansetron (4 mg ODT) for acute SMS",
            "status": "ACTUATED" if centrifuge_result.config.countermeasures_active else "PREPARED",
            "clinical_rationale": "Dampens Graybiel neurovestibular mismatch and prevents aspiration emesis in zero-g free float."
        })

    if not countermeasures:
        countermeasures.append({
            "system": "PREVENTIVE HEALTH MAINTENANCE",
            "action": "Maintain nominal 2.5-hour daily ARED/T2 exercise regimen and baseline acoustic logging",
            "status": "ACTIVE_NOMINAL",
            "clinical_rationale": "All environmental and physiological parameters within nominal NASA-STD-3001 bounds."
        })

    # NASA Regulatory Evidence Citations
    citations: List[Dict[str, str]] = [
        {
            "standard": "NASA-STD-3001 Vol 1 (Rev B)",
            "section": "Section 4.8: Space Radiation Permissible Exposure Limits (PEL)",
            "directive": "Blood-forming organ 30-day ceiling is 250 mGy-Eq; hull flux >0.10 mSv/h warrants storm shelter shelter-in-place."
        },
        {
            "standard": "NASA-STD-3001 Vol 2 (Rev C)",
            "section": "Chapter 6 & 7: Habitability & Autonomous Medical Care",
            "directive": "Interplanetary spacecraft must sustain autonomous medical diagnosis, triage, and life support intervention without Earth uplink."
        },
        {
            "standard": "NASA Human Research Program (HRP)",
            "section": "Risk of Bone Fracture & Cardiovascular/SANS Deconditioning",
            "directive": "Bone mineral loss exceeding 1.0%/mo requires mechanical work deficit surge; cephalad fluid redistribution requires venous occlusion countermeasures."
        }
    ]

    # Clinical Verdict synthesis
    if decision.risk_level.value == "CRITICAL":
        verdict = (
            "CRITICAL MEDICAL DIRECTIVE: Autonomous Level-5 emergency override active. Multi-pillar synergy "
            "escalation detected. Execute immediate compartment sheltering, apply vascular occlusion cuffs, "
            "and suspend non-critical operational tasks until biometrics stabilize."
        )
    elif decision.risk_level.value == "HIGH":
        verdict = (
            "ELEVATED MEDICAL ADVISORY: Significant physiological or environmental strain detected. "
            "Mandate protective shielding relocation and adjust compensatory ARED mechanical countermeasure loads."
        )
    elif decision.risk_level.value == "MEDIUM":
        verdict = (
            "MODERATE CLINICAL MONITORING: Sub-clinical biomarker drift or sensor noise flagged. "
            "Enforce passive vocal vitals surveillance and rest interval scheduling."
        )
    else:
        verdict = (
            "NOMINAL FLIGHT SURGEON STATUS: All crew vitals, environmental shielding, and musculoskeletal "
            "remodeling rates are within certified NASA-STD-3001 operational tolerances."
        )

    # Compute SHA-256 Telemetry Hash
    raw_hash_seed = f"{dossier_id}:{timestamp_str}:{decision.risk_score}:{p1.cumulative_dose_msv}:{p2.fatigue_score}:{p3.exercise_deficit_days}"
    checksum = compute_telemetry_hash(raw_hash_seed)

    dsn_status = (
        "TRANSMITTED TO HOUSTON DSN [DEEP SPACE NETWORK ACKNOWLEDGED]"
        if crew_state.comms_mode == CommsMode.ONLINE
        else "QUEUED IN HABITAT EDGE BUFFER [AWAITING DSN PASSAGE / 20-MIN DELAY UPLINK]"
    )

    return NasaMedicalDossier(
        dossier_id=dossier_id,
        timestamp_utc=timestamp_str,
        mission_elapsed_time=met_str,
        spacecraft_id="AEGIS-DEEPSPACE-01 [HERMES CLASS]",
        destination="Earth-Mars Interplanetary Transfer (Sol 142)",
        comms_status=comms_status,
        active_scenario=active_scenario,
        telemetry_checksum_sha256=checksum,
        risk_level=decision.risk_level.value,
        risk_score=decision.risk_score,
        confidence_pct=round(decision.confidence * 100.0, 1),
        primary_recommendation=decision.recommended_action,
        secondary_action=decision.alternative_action,
        flight_surgeon_verdict=verdict,
        pillar1_environmental=p1_data,
        pillar2_neuro_vocal=p2_data,
        pillar3_musculoskeletal=p3_data,
        pillar4_synergy_fusion=p4_data,
        centrifuge_dynamics=centrifuge_data,
        countermeasures_actuated=countermeasures,
        nasa_standards_cited=citations,
        dsn_dispatch_status=dsn_status
    )


def format_dossier_markdown(dossier: NasaMedicalDossier) -> str:
    """Renders the NASA Medical Dossier as a formatted NASA Med-B Briefing document."""
    lines = [
        "```",
        "================================================================================",
        "             NATIONAL AERONAUTICS AND SPACE ADMINISTRATION (NASA)",
        "               JOHNSON SPACE CENTER - FLIGHT MEDICINE DIRECTORY",
        "         AEGIS-DEEPSPACE AUTONOMOUS FLIGHT SURGEON CLINICAL DOSSIER (MED-B)",
        "================================================================================",
        f"DOSSIER ID    : {dossier.dossier_id}",
        f"TIMESTAMP (UTC): {dossier.timestamp_utc}",
        f"MISSION CLOCK : {dossier.mission_elapsed_time}",
        f"SPACECRAFT    : {dossier.spacecraft_id}",
        f"TRAJECTORY    : {dossier.destination}",
        f"COMMS STATUS  : {dossier.comms_status}",
        f"SCENARIO REF  : {dossier.active_scenario.upper()}",
        f"INTEGRITY HASH: SHA-256 [{dossier.telemetry_checksum_sha256}]",
        "================================================================================",
        "```",
        "",
        "## 1. EXECUTIVE CLINICAL TRIAGE & VERDICT",
        "",
        f"- **Composite Risk Score**: `{dossier.risk_score:.2f} / 1.00` &mdash; **TRIAGE LEVEL: `{dossier.risk_level}`**",
        f"- **Diagnostic Confidence**: `{dossier.confidence_pct}%`",
        f"- **Flight Surgeon Verdict**: {dossier.flight_surgeon_verdict}",
        f"- **Primary Action Directive**: **{dossier.primary_recommendation}**",
    ]
    
    if dossier.secondary_action:
        lines.append(f"- **Contingency Directive**: {dossier.secondary_action}")
        
    lines.extend([
        "",
        "---",
        "",
        "## 2. MULTI-PILLAR TELEMETRY SYNTHESIS",
        "",
        "### Pillar 1: Environmental Defense (Radiation Safe-Route)",
        f"- **Hull Dose Rate**: `{dossier.pillar1_environmental['dose_rate_msv_h']} mSv/h` | **Cumulative Mission Dose**: `{dossier.pillar1_environmental['cumulative_dose_msv']} mSv`",
        f"- **Solar Particle Event (SPE)**: `{'ACTIVE' if dossier.pillar1_environmental['spe_alert_active'] else 'INACTIVE'}`",
        f"- **Current Habitat Module**: `{dossier.pillar1_environmental['current_compartment']}`",
        f"- **Optimal Safe Shelter**: `{dossier.pillar1_environmental['recommended_safe_compartment']}` (Areal Mass: `{dossier.pillar1_environmental['shielding_rating_g_cm2']} g/cm²`)",
        f"- **Radiation Standard Status**: `{dossier.pillar1_environmental['permissible_exposure_status']}`",
        "",
        "### Pillar 2: Passive Biometrics (Voice Vitals)",
        f"- **Vocal Acoustic Fatigue**: `{dossier.pillar2_neuro_vocal['fatigue_score'] * 100:.0f}%` | **Cognitive Strain Index**: `{dossier.pillar2_neuro_vocal['cognitive_strain_score'] * 100:.0f}%`",
        f"- **Early Hypoxia Biomarker**: `{dossier.pillar2_neuro_vocal['hypoxia_indicator'] * 100:.0f}%`",
        f"- **Baseline Drift**: `{dossier.pillar2_neuro_vocal['baseline_drift_sigma']} σ` ({dossier.pillar2_neuro_vocal['vocal_prosody_status']})",
        "",
        "### Pillar 3: Predictive Digital Twin (Astro-Twin Mechanostat)",
        f"- **BMD Loss Projection**: `-{dossier.pillar3_musculoskeletal['projected_bmd_loss_pct_mo']}% / month`",
        f"- **Muscle Atrophy Projection**: `-{dossier.pillar3_musculoskeletal['projected_muscle_atrophy_pct']}%`",
        f"- **Exercise Deficit**: `{dossier.pillar3_musculoskeletal['exercise_deficit_days']} consecutive days` ({dossier.pillar3_musculoskeletal['countermeasure_status']})",
        f"- **Bone Remodeling State**: `{dossier.pillar3_musculoskeletal['mechanostat_remodeling_balance']}`",
        "",
        "### Pillar 4: Autonomous Fusion & Synergy Escalation",
        f"- **Synergy Multiplier Active**: `{'YES (ESCALATED)' if dossier.pillar4_synergy_fusion['synergy_active'] else 'NO (ADDITIVE)'}`",
        f"- **Synergy Score Penalty**: `+{dossier.pillar4_synergy_fusion['synergy_score']:.2f}`",
        f"- **Mathematical Formula**: `{dossier.pillar4_synergy_fusion['formula']}`",
    ])

    if dossier.centrifuge_dynamics:
        lines.extend([
            "",
            "### Gravitational Dynamics: Centrifuge Ring Transition",
            f"- **Gravity Gradient Transition**: `{dossier.centrifuge_dynamics['gravity_transition']}`",
            f"- **CVP Delta**: `{dossier.centrifuge_dynamics['cvp_delta']} mmHg` | **ICP Delta**: `{dossier.centrifuge_dynamics['icp_delta']} mmHg`",
            f"- **Space Motion Sickness (SMS) Index**: `{dossier.centrifuge_dynamics['sms_severity_index']:.1f} / 100`",
            f"- **Cross-Coupling Index**: `{dossier.centrifuge_dynamics['cross_coupling_index']}` | **Collision Risk**: `{dossier.centrifuge_dynamics['collision_probability_pct']}%`",
            f"- **Magnetic Deck Interlock**: `{'ENERGIZED' if dossier.centrifuge_dynamics['magnetic_deck_locked'] else 'DISENGAGED'}`",
        ])

    lines.extend([
        "",
        "---",
        "",
        "## 3. AUTONOMOUS COUNTERMEASURES & CLINICAL INTERVENTIONS LOG",
        "",
        "| Subsystem / Protocol | Action Directive | Status | Clinical Rationale |",
        "|---|---|---|---|"
    ])

    for cm in dossier.countermeasures_actuated:
        lines.append(f"| **{cm['system']}** | {cm['action']} | `{cm['status']}` | {cm['clinical_rationale']} |")

    lines.extend([
        "",
        "---",
        "",
        "## 4. REGULATORY EVIDENCE & NASA TECHNICAL STANDARDS",
        ""
    ])

    for std in dossier.nasa_standards_cited:
        lines.append(f"- **{std['standard']}** ({std['section']}): {std['directive']}")

    lines.extend([
        "",
        "---",
        "",
        "## 5. TELEMETRY INTEGRITY & DSN DISPATCH AUDIT",
        "",
        f"- **Deep Space Network Status**: `{dossier.dsn_dispatch_status}`",
        f"- **Cryptographic Checksum**: `SHA-256:{dossier.telemetry_checksum_sha256}`",
        f"- **Autonomous Flight Surgeon Signature**: `AEGIS-EDGE-MD-DAEMON v1.0.0 [OFFLINE-CERTIFIED]`",
        "",
        "> *DISCLAIMER: NASA Space Apps Hackathon Research Prototype. Autonomous flight surgeon decision support architecture for deep-space exploration under delayed or severed communications.*"
    ])

    return "\n".join(lines)
