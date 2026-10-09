"""Tests for NASA Medical Event Dossier & Telemetry Debrief (MED-B)."""

import pytest
from fastapi.testclient import TestClient

from aegis_deepspace.models import (
    CrewState,
    RadiationState,
    VoiceVitalsState,
    AstroTwinState,
    CommsMode,
    RiskLevel
)
from aegis_deepspace.decision_engine import AutonomousDecisionEngine
from aegis_deepspace.centrifuge_sim import default_centrifuge_simulator, CentrifugeSimConfig
from aegis_deepspace.dossier import (
    NasaMedicalDossier,
    generate_medical_dossier,
    format_dossier_markdown,
    compute_telemetry_hash
)
from aegis_deepspace.server import app


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def decision_engine():
    return AutonomousDecisionEngine()


def test_compute_telemetry_hash():
    """Verify cryptographic SHA-256 telemetry verification hash."""
    h1 = compute_telemetry_hash("sample_telemetry_data_1")
    h2 = compute_telemetry_hash("sample_telemetry_data_2")
    assert isinstance(h1, str)
    assert len(h1) == 24
    assert h1 != h2
    # Deterministic check
    assert h1 == compute_telemetry_hash("sample_telemetry_data_1")


def test_generate_medical_dossier_nominal(decision_engine):
    """Verify dossier generation under nominal crew baseline."""
    nominal_state = CrewState(
        comms_mode=CommsMode.ONLINE,
        radiation=RadiationState(risk_level="LOW", dose_rate_msv_h=0.02, cumulative_dose_msv=1.2),
        voice_vitals=VoiceVitalsState(fatigue_score=0.10, cognitive_strain_score=0.08, deviation_from_baseline_z=0.3),
        astro_twin=AstroTwinState(exercise_deficit_days=0, countermeasure_status="NOMINAL")
    )
    decision = decision_engine.process(nominal_state)
    dossier = generate_medical_dossier(nominal_state, decision, active_scenario="normal")

    assert isinstance(dossier, NasaMedicalDossier)
    assert dossier.risk_level == "LOW"
    assert dossier.risk_score <= 0.25
    assert "ONLINE" in dossier.comms_status
    assert "MET T+142d" in dossier.mission_elapsed_time
    assert len(dossier.telemetry_checksum_sha256) == 24
    assert len(dossier.nasa_standards_cited) >= 2
    assert dossier.pillar1_environmental["permissible_exposure_status"] == "WITHIN 30-DAY PEL"

    # Test markdown formatting
    md = format_dossier_markdown(dossier)
    assert "NATIONAL AERONAUTICS AND SPACE ADMINISTRATION" in md
    assert dossier.dossier_id in md
    assert "EXECUTIVE CLINICAL TRIAGE & VERDICT" in md


def test_generate_medical_dossier_solar_storm(decision_engine):
    """Verify dossier generation during high-flux solar particle event."""
    storm_state = CrewState(
        comms_mode=CommsMode.ONLINE,
        radiation=RadiationState(
            risk_level="HIGH",
            dose_rate_msv_h=0.48,
            cumulative_dose_msv=8.5,
            spe_active=True,
            current_module="Module A: Command Deck",
            recommended_safe_module="Module B: Storm Shelter"
        ),
        voice_vitals=VoiceVitalsState(fatigue_score=0.20, cognitive_strain_score=0.15),
        astro_twin=AstroTwinState(exercise_deficit_days=1, countermeasure_status="RESTRICTED")
    )
    decision = decision_engine.process(storm_state)
    dossier = generate_medical_dossier(storm_state, decision, active_scenario="solar_storm")

    assert dossier.risk_level in ["HIGH", "CRITICAL"]
    assert dossier.pillar1_environmental["spe_alert_active"] is True
    # Should have shelter evacuation in countermeasures
    cm_systems = [cm["system"] for cm in dossier.countermeasures_actuated]
    assert any("HABITAT SHIELDING ROUTE" in s for s in cm_systems)


def test_generate_medical_dossier_centrifuge_despin(decision_engine):
    """Verify dossier generation with centrifugal microgravity shock simulation."""
    sim_res = default_centrifuge_simulator.run_simulation(CentrifugeSimConfig(duration_seconds=90.0))
    crew_state = default_centrifuge_simulator.convert_to_crew_state(sim_res)
    decision = decision_engine.process(crew_state)

    dossier = generate_medical_dossier(
        crew_state=crew_state,
        decision=decision,
        active_scenario="centrifuge_despin",
        centrifuge_result=sim_res
    )

    assert dossier.centrifuge_dynamics is not None
    assert "0.38g -> 0.0g" in dossier.centrifuge_dynamics["gravity_transition"]
    assert dossier.centrifuge_dynamics["sms_severity_index"] > 50.0

    # Countermeasures should include antiemetics and gravitational override
    cm_systems = [cm["system"] for cm in dossier.countermeasures_actuated]
    assert any("GRAVITATIONAL EMERGENCY" in s for s in cm_systems)
    assert any("PHARMACOTHERAPY" in s for s in cm_systems)

    md = format_dossier_markdown(dossier)
    assert "Gravitational Dynamics: Centrifuge Ring Transition" in md
    assert "Space Motion Sickness (SMS) Index" in md


def test_generate_medical_dossier_offline_blackout(decision_engine):
    """Verify dossier handles 20-min communication blackout autonomously."""
    blackout_state = CrewState(
        comms_mode=CommsMode.OFFLINE,
        radiation=RadiationState(risk_level="MEDIUM", dose_rate_msv_h=0.08),
        voice_vitals=VoiceVitalsState(fatigue_score=0.35, cognitive_strain_score=0.30),
        astro_twin=AstroTwinState(exercise_deficit_days=2)
    )
    decision = decision_engine.process(blackout_state)
    dossier = generate_medical_dossier(blackout_state, decision, active_scenario="offline_blackout")

    assert "OFFLINE" in dossier.comms_status
    assert "EDGE BUFFER" in dossier.dsn_dispatch_status


def test_api_dossier_endpoints(test_client):
    """Verify FastAPI endpoints for JSON, Markdown, and download."""
    # 1. JSON endpoint
    res_json = test_client.get("/api/mission/dossier")
    assert res_json.status_code == 200
    data = res_json.json()
    assert "dossier_id" in data
    assert "telemetry_checksum_sha256" in data
    assert "pillar1_environmental" in data
    assert "countermeasures_actuated" in data

    # 2. Markdown endpoint
    res_md = test_client.get("/api/mission/dossier/markdown")
    assert res_md.status_code == 200
    md_data = res_md.json()
    assert "markdown" in md_data
    assert "DOSSIER ID" in md_data["markdown"]

    # 3. Direct file download endpoint
    res_dl = test_client.get("/api/mission/dossier/download")
    assert res_dl.status_code == 200
    assert "text/markdown" in res_dl.headers.get("content-type", "")
    assert "attachment; filename=" in res_dl.headers.get("content-disposition", "")
    assert "NATIONAL AERONAUTICS AND SPACE ADMINISTRATION" in res_dl.text


def test_copilot_dossier_query(test_client):
    """Verify copilot responds intelligently to medical dossier requests."""
    chat_res = test_client.post("/api/chat", json={"message": "Generate medical dossier for Houston"})
    assert chat_res.status_code == 200
    reply_data = chat_res.json()
    assert reply_data["intent"] == "MEDICAL_DOSSIER"
    assert "MEDB-" in reply_data["reply"]
    assert "SHA-256" in reply_data["reply"]
    assert "NASA-STD-3001" in "".join(reply_data["citations"])
