"""Tests for FastAPI server endpoints in Aegis-DeepSpace Pillar 4."""

import pytest
from fastapi.testclient import TestClient
from aegis_deepspace.server import app

client = TestClient(app)


def test_api_state():
    """Verify /api/state returns current telemetry and decision."""
    response = client.get("/api/state")
    assert response.status_code == 200
    data = response.json()
    assert "crew_state" in data
    assert "decision" in data
    assert data["decision"]["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def test_api_scenarios_list():
    """Verify /api/scenarios lists the 6 demo scenarios."""
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    scenarios = response.json()["scenarios"]
    assert len(scenarios) == 6
    ids = [s["id"] for s in scenarios]
    assert "normal" in ids
    assert "solar_storm" in ids
    assert "voice_anomaly" in ids
    assert "combined_anomaly" in ids
    assert "offline_blackout" in ids
    assert "uncertain_data" in ids


def test_api_run_scenarios():
    """Verify all scenarios can be executed via the endpoint."""
    for s_id in ["normal", "solar_storm", "voice_anomaly", "combined_anomaly", "offline_blackout", "uncertain_data"]:
        response = client.post(f"/api/scenarios/{s_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["scenario_id"] == s_id
        assert "decision" in data
        assert data["decision"]["risk_score"] >= 0.0


def test_api_comms_toggle():
    """Verify comms toggle endpoint switches between ONLINE and OFFLINE."""
    # Ensure starting in ONLINE
    client.post("/api/scenarios/normal")
    
    # Toggle to OFFLINE
    res1 = client.post("/api/comms/toggle")
    assert res1.status_code == 200
    assert res1.json()["comms_mode"] == "OFFLINE"
    assert res1.json()["decision"]["mode"] == "OFFLINE"

    # Toggle back to ONLINE
    res2 = client.post("/api/comms/toggle")
    assert res2.status_code == 200
    assert res2.json()["comms_mode"] == "ONLINE"
    assert res2.json()["decision"]["mode"] == "ONLINE"


def test_api_process_custom():
    """Verify custom telemetry ingestion via /api/process."""
    custom_state = {
        "radiation": {
            "risk_level": "CRITICAL",
            "dose_rate_msv_h": 0.85,
            "spe_active": True,
            "current_module": "Gym / Exercise Bay",
            "recommended_safe_module": "Storm Shelter (Water Wall)"
        },
        "voice_vitals": {
            "cognitive_strain_score": 0.8,
            "fatigue_score": 0.75,
            "hypoxia_indicator": 0.1
        },
        "astro_twin": {
            "exercise_deficit_days": 2
        }
    }
    response = client.post("/api/process", json=custom_state)
    assert response.status_code == 200
    decision = response.json()
    assert decision["risk_level"] == "CRITICAL"
    assert "SHELTER" in decision["recommended_action"].upper()


def test_api_providers_endpoints():
    """Verify individual provider endpoints return correct pillar state."""
    # Test normal
    client.post("/api/scenarios/normal")
    r1 = client.get("/api/providers/radiation")
    assert r1.status_code == 200
    assert r1.json()["risk_level"] == "LOW"

    r2 = client.get("/api/providers/voice_vitals")
    assert r2.status_code == 200
    assert r2.json()["fatigue_score"] <= 0.20

    r3 = client.get("/api/providers/astro_twin")
    assert r3.status_code == 200
    assert r3.json()["exercise_deficit_days"] == 0

    # Test solar storm scenario
    client.post("/api/scenarios/solar_storm")
    r_storm = client.get("/api/providers/radiation")
    assert r_storm.status_code == 200
    assert r_storm.json()["spe_active"] is True
    assert r_storm.json()["risk_level"] == "CRITICAL"


def test_api_pillar1_analysis_and_routing():
    """Verify Pillar 1 dedicated endpoints for habitat analysis and Dijkstra routing."""
    res = client.get("/api/pillar1/analysis?start_module=Module+D&flux_msv=250.0")
    assert res.status_code == 200
    data = res.json()
    assert data["safest_shelter"] == "Module B"
    assert data["evacuation_route"] == ["Module D", "Module C", "Module B"]
    assert len(data["compartment_risks"]) == 4
    assert data["transit_dose_mSv"] > 0

    route_res = client.post("/api/pillar1/calculate_route", json={
        "start_module": "Module A",
        "target_module": "Module B",
        "external_flux_mSv": 250.0
    })
    assert route_res.status_code == 200
    rdata = route_res.json()
    assert rdata["route"] == ["Module A", "Module B"]
    assert rdata["transit_dose_mSv"] > 0
    assert len(rdata["steps"]) == 2


def test_api_pillar2_analysis():
    """Verify Pillar 2 dedicated endpoint for real voice vitals ML analysis."""
    res = client.get("/api/pillar2/analysis")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "REAL_PIPELINE_ACTIVE"
    assert "telemetry" in data
    assert "transcript" in data["telemetry"]
    assert "models_loaded" in data


def test_api_pillar4_decision_trace():
    """Verify GET /api/pillar4/decision-trace returns structured DecisionTrace."""
    client.post("/api/scenarios/solar_storm")
    res = client.get("/api/pillar4/decision-trace")
    assert res.status_code == 200
    data = res.json()
    assert "base_risk" in data
    assert "signals" in data
    assert "synergy_rules" in data
    assert data["final_risk"] >= 0.50
    assert len(data["signals"]) == 3


def test_api_pillar4_what_if():
    """Verify POST /api/pillar4/what-if executes deterministic delay simulation."""
    res = client.post("/api/pillar4/what-if", json={
        "delay_minutes": 25.0,
        "scenario": "solar_storm"
    })
    assert res.status_code == 200
    data = res.json()
    assert "baseline" in data
    assert "counterfactual" in data
    assert "impact" in data
    assert data["delay_minutes"] == 25.0
    assert data["impact"]["delta_exposure_msv"] > 0
    assert data["counterfactual"]["risk_score"] >= data["baseline"]["risk_score"]
    assert "decision_trace" in data["counterfactual"]


def test_api_pillar3_analysis_and_simulation():
    """Verify Pillar 3 dedicated endpoints for real hybrid digital twin analysis and simulation."""
    # Test GET /api/pillar3/analysis
    res = client.get("/api/pillar3/analysis?scenario=solar_storm")
    assert res.status_code == 200
    data = res.json()
    assert data["scenario"] == "solar_storm"
    assert "astro_twin_state" in data
    assert "simulation" in data
    assert data["simulation"]["status"] == "REAL_SIMULATION_ACTIVE"
    assert len(data["simulation"]["nominal_trajectory"]) == 30
    assert "prescription" in data["simulation"]
    assert data["simulation"]["prescription"]["outage_duration_days"] == 1

    # Test POST /api/pillar3/simulate
    sim_res = client.post("/api/pillar3/simulate", json={
        "astronaut_id": "TEST-ASTRONAUT-1",
        "age": 45,
        "sex": "F",
        "body_mass_kg": 65.0,
        "baseline_hip_bmd": 0.98,
        "outage_days": 4,
        "outage_start_day": 8,
        "recovery_window_days": 6,
        "nominal_volume_kg": 9000.0
    })
    assert sim_res.status_code == 200
    sdata = sim_res.json()
    assert sdata["status"] == "REAL_SIMULATION_ACTIVE"
    assert sdata["model_metadata"]["model_loaded"] is True
    assert len(sdata["nominal_trajectory"]) == 30
    assert len(sdata["outage_trajectory"]) == 30
    assert sdata["prescription"]["outage_duration_days"] == 4
    assert sdata["prescription"]["total_mechanical_work_deficit_kg"] == 36000.0
    assert sdata["prescription"]["required_daily_volume_surge"] == "+66.7%"
    assert "barbell_squat" in sdata["prescription"]["specific_exercise_adjustments"]




