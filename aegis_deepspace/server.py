"""FastAPI Web Server for Aegis-DeepSpace Pillar 4 Autonomous Decision Engine MVP."""

import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from aegis_deepspace.models import CrewState, DecisionObject, CommsMode
from aegis_deepspace.decision_engine import AutonomousDecisionEngine
from aegis_deepspace.scenarios import DEMO_SCENARIOS

app = FastAPI(
    title="Aegis-DeepSpace: Autonomous Decision Engine (Pillar 4 MVP)",
    description="Offline AI Flight Surgeon Decision Support synthesizing Radiation, Voice Vitals, and Astro-Twin.",
    version="1.0.0"
)

engine = AutonomousDecisionEngine()

# In-memory current state initialized to normal scenario
current_state: CrewState = DEMO_SCENARIOS["normal"]()
current_decision: DecisionObject = engine.process(current_state)


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
    global current_state, current_decision
    if scenario_id not in DEMO_SCENARIOS:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
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
