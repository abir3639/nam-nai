"""Unit and integration tests for Aegis-DeepSpace Flight Surgeon Copilot."""

import pytest
from fastapi.testclient import TestClient

from aegis_deepspace.server import app
from aegis_deepspace.copilot import default_copilot
from aegis_deepspace.models import CrewState
from aegis_deepspace.scenarios import DEMO_SCENARIOS
from aegis_deepspace.decision_engine import AutonomousDecisionEngine


@pytest.fixture
def client():
    return TestClient(app)


def test_copilot_telemetry_radiation():
    state = DEMO_SCENARIOS["normal"]()
    engine = AutonomousDecisionEngine()
    decision = engine.process(state)
    
    resp = default_copilot.ask("What is the current radiation level and safe shelter?", state, decision)
    assert resp.intent == "RADIATION_QUERY"
    assert resp.confidence >= 0.90
    assert "Module B" in resp.reply
    assert resp.telemetry_context is not None
    assert "dose_rate_msv_h" in resp.telemetry_context


def test_copilot_telemetry_centrifuge():
    state = DEMO_SCENARIOS["normal"]()
    engine = AutonomousDecisionEngine()
    decision = engine.process(state)
    
    resp = default_copilot.ask("Centrifuge gravity and rotation status", state, decision)
    assert resp.intent == "CENTRIFUGE_TELEMETRY"
    assert "0.38g" in resp.reply or "gravity" in resp.reply.lower()


def test_copilot_clinical_rag_sans():
    state = DEMO_SCENARIOS["normal"]()
    engine = AutonomousDecisionEngine()
    decision = engine.process(state)
    
    resp = default_copilot.ask("What causes SANS and intracranial pressure elevation?", state, decision)
    assert resp.intent == "CLINICAL_KNOWLEDGE_RAG"
    assert len(resp.citations) > 0
    assert "NASA" in resp.citations[0] or "HRP" in resp.citations[0]
    assert "fluid" in resp.reply.lower() or "sans" in resp.reply.lower()


def test_copilot_action_trigger():
    state = DEMO_SCENARIOS["normal"]()
    engine = AutonomousDecisionEngine()
    decision = engine.process(state)
    
    resp = default_copilot.ask("simulate solar storm", state, decision)
    assert resp.intent == "SYSTEM_ACTION"
    assert resp.action_triggered is not None
    assert resp.action_triggered.get("scenario_id") == "solar_storm"


def test_copilot_api_endpoint(client):
    payload = {"message": "What is our composite risk score?"}
    r = client.post("/api/chat", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "reply" in data
    assert "intent" in data
    assert "citations" in data
    assert "suggested_prompts" in data
    assert len(data["suggested_prompts"]) > 0


def test_copilot_api_action_execution(client):
    # Ask copilot to switch scenario to voice_anomaly
    payload = {"message": "simulate voice anomaly"}
    r = client.post("/api/chat", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["intent"] == "SYSTEM_ACTION"
    assert data["action_triggered"]["action"] == "set_scenario"
    
    # Verify state reflects change
    st = client.get("/api/state").json()
    assert st["scenario_id"] == "voice_anomaly"


def test_copilot_website_info_query(client):
    payload = {"message": "website info"}
    r = client.post("/api/chat", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["intent"] == "WEBSITE_INFO"
    assert "Aegis-DeepSpace" in data["reply"]
    assert "Pillar 1" in data["reply"]
    assert "Pillar 2" in data["reply"]
    assert "Pillar 3" in data["reply"]
    assert "Pillar 4" in data["reply"]
    assert "Centrifugal" in data["reply"]


def test_copilot_with_centrifuge_sim_result(client):
    from aegis_deepspace.centrifuge_sim import default_centrifuge_simulator, CentrifugeSimConfig
    sim_res = default_centrifuge_simulator.run_simulation(CentrifugeSimConfig())
    state = DEMO_SCENARIOS["normal"]()
    engine = AutonomousDecisionEngine()
    decision = engine.process(state)

    # 1. Ask general RAG question with centrifuge_result populated
    resp1 = default_copilot.ask("What causes SANS?", state, decision, centrifuge_result=sim_res)
    assert resp1.intent == "CLINICAL_KNOWLEDGE_RAG"
    assert resp1.telemetry_context is not None
    assert "gravity_g" in resp1.telemetry_context

    # 2. Ask centrifuge question with centrifuge_result populated
    resp2 = default_copilot.ask("Centrifuge rotation status", state, decision, centrifuge_result=sim_res)
    assert resp2.intent == "CENTRIFUGE_TELEMETRY"
    assert "CVP" in resp2.reply
    assert resp2.telemetry_context["gravity_g"] >= 0.0

    # 3. Via API endpoint after centrifuge simulation
    client.post("/api/centrifuge/simulate", json={})
    r = client.post("/api/chat", json={"message": "What is our current situation?"})
    assert r.status_code == 200
    assert "reply" in r.json()


