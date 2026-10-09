"""Automated Unit and Integration Tests for Feature B: Explainable AI Health Alerts Using SHAP.
Tests:
1. Explanations are generated for supported model predictions.
2. Contributions and feature names correspond to the actual model inputs.
3. Explanation output handles positive and negative contributions correctly where applicable.
4. Invalid or missing inputs are handled safely.
5. Unsupported explainers do not crash the monitoring pipeline.
6. Explanation failure does not discard a valid health alert.
7. Historical explanations retain the correct model version across federated model updates.
8. Explanations remain available for queued alerts during offline operation and application restart.
9. Synchronization transfers explanations without duplicate alerts.
10. Dashboard APIs display actual explanation results rather than hardcoded sample values.
11. Existing health monitoring and Feature 3 tests continue to pass.
"""

import os
import math
import tempfile
import pytest
import datetime
from starlette.testclient import TestClient

from aegis_deepspace.server import app
from aegis_deepspace.sync.models import (
    SyncState,
    SyncRecordStatus,
    HealthEventRecord,
    ModelUpdateRecord
)
from aegis_deepspace.sync.coordinator import SyncCoordinator
from aegis_deepspace.xai_engine import (
    XAIEngine,
    MultimodalCrewAnomalyExplainer,
    AstroTwinResidualExplainer,
    FEATURE_KEYS,
    FEATURE_METADATA,
    DEFAULT_BASELINE_WEIGHTS
)
from aegis_deepspace.models import (
    CrewState,
    RadiationState,
    VoiceVitalsState,
    AstroTwinState,
    CommsMode
)
from aegis_deepspace.decision_engine import AutonomousDecisionEngine

client = TestClient(app)


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def coordinator(temp_db):
    return SyncCoordinator(db_path=temp_db)


@pytest.fixture
def xai_engine(coordinator):
    return XAIEngine(coordinator=coordinator)


def test_multimodal_crew_anomaly_shap_explanation(xai_engine):
    """Test 1: Explanations are generated for supported model predictions and feature names match."""
    sample = {
        "rad_rate": 0.72,
        "fatigue": 0.35,
        "strain": 0.55,
        "hypoxia": 0.04,
        "bone_loss": 0.80,
        "shear": 0.00
    }
    explanation = xai_engine.explain_crew_anomaly(sample, alert_id="ALERT-TEST-01")

    assert explanation.status == "AVAILABLE"
    assert explanation.alert_id == "ALERT-TEST-01"
    assert explanation.model_name == "Multimodal Crew Anomaly Detector"
    assert explanation.model_version == "v1.0.0"
    assert explanation.predicted_score > 0.30
    assert len(explanation.contributions) == len(FEATURE_KEYS)

    # Feature names match actual inputs
    feature_names = {c.feature_name for c in explanation.contributions}
    assert feature_names == set(FEATURE_KEYS)

    # Check Shapley efficiency property: E[f(x)] + sum(phi) == f(x)
    sum_phi = sum(c.attribution for c in explanation.contributions)
    reconstructed = explanation.base_value + sum_phi
    assert abs(reconstructed - explanation.predicted_score) < 1e-3


def test_positive_and_negative_contributions(xai_engine):
    """Test 2: Explanation handles positive (risk increasing) and negative (mitigating) contributions."""
    # rad_rate is elevated (0.80 > nominal 0.02) -> must be INCREASES_RISK
    # fatigue is below nominal (0.05 < nominal 0.15) -> must be DECREASES_RISK
    sample = {
        "rad_rate": 0.80,
        "fatigue": 0.05,
        "strain": 0.12,
        "hypoxia": 0.04,
        "bone_loss": 0.80,
        "shear": 0.00
    }
    explanation = xai_engine.explain_crew_anomaly(sample)
    contrib_map = {c.feature_name: c for c in explanation.contributions}

    assert contrib_map["rad_rate"].attribution > 0.10
    assert contrib_map["rad_rate"].direction == "INCREASES_RISK"

    assert contrib_map["fatigue"].attribution < -0.01
    assert contrib_map["fatigue"].direction == "DECREASES_RISK"


def test_sanitization_of_invalid_and_missing_inputs(xai_engine):
    """Test 3: Missing features, NaNs, and unexpected types are sanitized safely."""
    bad_sample = {
        "rad_rate": float("nan"),
        "fatigue": None,
        "strain": "bad_string",
        "hypoxia": 0.50
    }
    explanation = xai_engine.explain_crew_anomaly(bad_sample, alert_id="ALERT-SANITY")

    assert explanation.status in ["AVAILABLE", "CACHED"]
    assert not math.isnan(explanation.predicted_score)
    assert not math.isnan(explanation.efficiency_error)
    assert len(explanation.contributions) == len(FEATURE_KEYS)


def test_astro_twin_tree_explainer():
    """Test 4: Astro-Twin physiological deconditioning residual model is explained using TreeExplainer."""
    twin_explainer = AstroTwinResidualExplainer()
    sample_features = {
        "mission_day": 30.0,
        "age": 42.0,
        "sex_binary": 1.0,
        "body_mass_kg": 80.5,
        "baseline_hip_bmd": 1.05,
        "rolling_ared_7d": 6000.0,
        "rolling_treadmill_7d": 2000.0,
        "consecutive_offline_days": 4.0,
        "dietary_calcium_mg": 1100.0,
        "vitamin_d_iu": 1000.0,
        "bisphosphonate_administered": 0.0
    }
    explanation = twin_explainer.explain(sample_features, alert_id="ALERT-TWIN-01")

    assert explanation.model_name == "Astro-Twin Residual Gradient Boosting Model"
    assert explanation.explainer_type == "shap.TreeExplainer"
    if explanation.status == "AVAILABLE":
        assert len(explanation.contributions) == 11
        assert abs(explanation.efficiency_error) < 1e-3


def test_explainer_failure_does_not_crash_pipeline_or_discard_alert(coordinator):
    """Test 5: If an explainer encounters an unexpected fault, the health alert is preserved."""
    engine = AutonomousDecisionEngine()
    state = CrewState(
        radiation=RadiationState(risk_level="CRITICAL", dose_rate_msv_h=0.85, spe_active=True),
        voice_vitals=VoiceVitalsState(fatigue_score=0.40),
        astro_twin=AstroTwinState()
    )
    decision = engine.process(state)

    # Monkeypatch xai_engine to simulate an unhandled internal exception
    def broken_explain(*args, **kwargs):
        raise RuntimeError("Simulated internal GPU/C-extension fault in explainer")

    coordinator.xai_engine.multimodal_explainer.explain = broken_explain
    coordinator.comms_manager.set_state(SyncState.OFFLINE)

    # Record event: must succeed and NOT crash or discard alert!
    record = coordinator.record_health_event_from_decision(decision, state, scenario_id="fault_test")
    assert record is not None
    assert record.event_id is not None
    assert record.severity == "CRITICAL"

    # Explanation attached must reflect graceful EXPLANATION_UNAVAILABLE
    assert record.explanation is not None
    assert record.explanation["status"] == "EXPLANATION_UNAVAILABLE"
    assert "Simulated internal GPU/C-extension fault" in record.explanation["error_message"]

    # Queue retains event
    pending = coordinator.store.get_pending_health_events()
    assert any(e.event_id == record.event_id for e in pending)


def test_historical_explanations_retain_model_version(coordinator):
    """Test 6: Historical explanations retain originating model version when federated model updates."""
    from aegis_deepspace.sync.federated_engine import DEFAULT_BASELINE_WEIGHTS as FED_BASELINE_WEIGHTS, compute_weights_hash

    coordinator.comms_manager.set_state(SyncState.OFFLINE)

    # 1. Enqueue health event with v1.0.0
    state1 = CrewState(
        radiation=RadiationState(risk_level="HIGH", dose_rate_msv_h=0.45),
        voice_vitals=VoiceVitalsState(cognitive_strain_score=0.50)
    )
    dec1 = AutonomousDecisionEngine().process(state1)
    rec1 = coordinator.record_health_event_from_decision(dec1, state1, scenario_id="v1_event")
    assert rec1.explanation["model_version"] == "v1.0.0"

    # 2. Promote global model via Federated Learning update (Round 1 -> v1.1.0)
    upd = ModelUpdateRecord(
        update_id="UPD-PROMO-01",
        client_id="HERMES-EDGE-01",
        base_version="v1.0.0",
        timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        num_samples=50,
        loss=0.08,
        weights_delta={k: 0.05 for k in FED_BASELINE_WEIGHTS},
        weights_checksum_sha256=""
    )
    upd.weights_checksum_sha256 = compute_weights_hash(upd.weights_delta)
    global_m, reason = coordinator.aggregator.aggregate_updates([upd])
    assert global_m is not None, f"Aggregation failed: {reason}"
    assert global_m.version == "v1.1.0"

    # 3. Retrieve historical event: must STILL retain v1.0.0 and NOT be silently regenerated
    historical = coordinator.store.get_pending_health_events()
    target = next(e for e in historical if e.event_id == rec1.event_id)
    assert target.explanation["model_version"] == "v1.0.0"


def test_offline_queue_preserves_explanations_across_restart(temp_db):
    """Test 7: Explanations remain available for queued alerts during offline operation and app restart."""
    coord1 = SyncCoordinator(db_path=temp_db)
    coord1.comms_manager.set_state(SyncState.OFFLINE, reason="Conjunction Blackout")

    state = CrewState(
        radiation=RadiationState(risk_level="CRITICAL", dose_rate_msv_h=0.75, spe_active=True)
    )
    dec = AutonomousDecisionEngine().process(state)
    rec = coord1.record_health_event_from_decision(dec, state, scenario_id="offline_blackout")

    # Simulate cold restart by constructing new SyncCoordinator with same SQLite database
    coord2 = SyncCoordinator(db_path=temp_db)
    pending = coord2.store.get_pending_health_events()
    assert len(pending) == 1
    reloaded = pending[0]
    assert reloaded.event_id == rec.event_id
    assert reloaded.sync_status == SyncRecordStatus.PENDING
    assert reloaded.explanation is not None
    assert reloaded.explanation["status"] == "AVAILABLE"
    assert reloaded.severity in ["HIGH", "CRITICAL"]
    assert reloaded.explanation["severity_category"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert reloaded.explanation["predicted_score"] is not None
    assert len(reloaded.explanation["contributions"]) > 0


def test_sync_transfers_explanations_without_duplicates(coordinator):
    """Test 8: Reconnection synchronizes explanations to Houston Ground Control without duplicates."""
    coordinator.comms_manager.set_state(SyncState.OFFLINE, reason="Transit Blackout")
    state = CrewState(
        radiation=RadiationState(risk_level="HIGH", dose_rate_msv_h=0.35),
        voice_vitals=VoiceVitalsState(fatigue_score=0.60)
    )
    dec = AutonomousDecisionEngine().process(state)
    rec = coordinator.record_health_event_from_decision(dec, state, scenario_id="sync_test")

    # Reconnect and synchronize
    coordinator.comms_manager.set_state(SyncState.ONLINE, reason="AOS Houston Link", auto_sync=True)

    # Verify Houston Ground archive
    ground_events = coordinator.store.get_ground_health_events()
    assert len(ground_events) == 1
    g_evt = ground_events[0]
    assert g_evt["event_id"] == rec.event_id
    assert g_evt["explanation"] is not None
    assert g_evt["explanation"]["model_version"] == "v1.0.0"

    # Retrying synchronization does not create duplicate ground records
    retry_res = coordinator.comms_manager.synchronize_pending_records()
    assert retry_res["synced_count"] == 0
    assert len(coordinator.store.get_ground_health_events()) == 1


def test_xai_caching_performance(xai_engine):
    """Test 9: Identical feature inputs reuse cached explanations with zero recomputation delay."""
    sample = {"rad_rate": 0.50, "fatigue": 0.30, "strain": 0.40, "hypoxia": 0.05, "bone_loss": 0.8, "shear": 0.0}
    
    # First call: computed and cached
    e1 = xai_engine.explain_crew_anomaly(sample, use_cache=True)
    assert e1.status == "AVAILABLE"

    # Second call: retrieved from cache
    e2 = xai_engine.explain_crew_anomaly(sample, use_cache=True)
    assert e2.status == "CACHED"
    assert e2.predicted_score == e1.predicted_score


def test_api_xai_endpoints():
    """Test 10: Backend /api/xai/* endpoints return valid model schemas, explanations, and demo workflows."""
    # 1. Models endpoint
    r_models = client.get("/api/xai/models")
    assert r_models.status_code == 200
    m_data = r_models.json()
    assert len(m_data["models"]) >= 2
    assert m_data["models"][0]["name"] == "Multimodal Crew Anomaly Detector"
    assert "features" in m_data["models"][0]

    # 2. Explain active decision
    r_dec = client.get("/api/xai/explain/decision")
    assert r_dec.status_code == 200
    dec_data = r_dec.json()
    assert "predicted_score" in dec_data
    assert "contributions" in dec_data
    assert len(dec_data["contributions"]) == 6

    # 3. Custom features explanation
    r_custom = client.post("/api/xai/explain/custom", json={
        "features": {
            "rad_rate": 1.50,
            "fatigue": 0.85,
            "strain": 0.75,
            "hypoxia": 0.60,
            "bone_loss": 2.50,
            "shear": 0.40
        }
    })
    assert r_custom.status_code == 200
    c_data = r_custom.json()
    assert c_data["severity_category"] in ["HIGH", "CRITICAL"]
    assert c_data["efficiency_error"] < 0.001
    assert "Statistical attribution (SHAP)" in c_data["limitations_disclaimer"]

    # 4. Reproducible 6-step demo workflow endpoint
    r_demo = client.post("/api/xai/demo/scenario")
    assert r_demo.status_code == 200
    demo_res = r_demo.json()
    assert demo_res["demo_status"] == "COMPLETED"
    assert demo_res["step1_nominal"]["severity_category"] == "LOW"
    assert demo_res["step2_alert_online"]["severity_category"] in ["HIGH", "CRITICAL"]
    assert demo_res["step3_comms_state"] == "OFFLINE"
    assert demo_res["step4_offline_pending_count"] >= 1
    assert demo_res["step6_ground_records_count"] >= 2

    # 5. Reset demo
    r_reset = client.post("/api/xai/demo/reset")
    assert r_reset.status_code == 200
    assert r_reset.json()["status"] == "xai_demo_reset_completed"
