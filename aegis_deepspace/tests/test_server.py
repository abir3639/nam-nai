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
