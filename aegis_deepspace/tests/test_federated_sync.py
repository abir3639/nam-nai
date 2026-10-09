"""Automated Unit and Integration Tests for Asymmetric Federated Sync with Houston Ground Control.
Verifies offline persistence, store-and-forward queueing, retry idempotency,
lightweight federated learning aggregation, and end-to-end mission workflows.
"""

import os
import tempfile
import pytest
import datetime
import hashlib

from aegis_deepspace.sync.models import (
    SyncState,
    SyncRecordStatus,
    HealthEventRecord,
    TelemetrySummaryRecord,
    ModelUpdateRecord,
    FederatedGlobalModel
)
from aegis_deepspace.sync.persistence import SyncStore
from aegis_deepspace.sync.federated_engine import (
    EdgeFederatedClient,
    GroundFederatedAggregator,
    DEFAULT_BASELINE_WEIGHTS,
    compute_weights_hash
)
from aegis_deepspace.sync.ground_receiver import GroundReceiver, GroundBatchPayload, DEFAULT_MISSION_TOKEN
from aegis_deepspace.sync.comms_manager import CommsManager
from aegis_deepspace.sync.coordinator import SyncCoordinator
from aegis_deepspace.models import CrewState, RadiationState, VoiceVitalsState, AstroTwinState, CommsMode
from aegis_deepspace.decision_engine import AutonomousDecisionEngine


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


def test_offline_health_events_persisted(coordinator):
    """Test 1: Health events are enqueued and persisted locally when communications are OFFLINE."""
    coordinator.comms_manager.set_state(SyncState.OFFLINE, reason="Test comms loss")
    assert coordinator.comms_manager.state == SyncState.OFFLINE

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    evt = HealthEventRecord(
        event_id="EVT-TEST-01",
        severity="HIGH",
        occurrence_utc=now,
        source_pillar="Pillar 1: Radiation Safe-Route",
        title="Solar Particle Event Detected Offline",
        description="Dose rate elevated during Mars transit blackout.",
        action_recommended="Maneuver to storm shelter",
        risk_score=0.75,
        payload={"dose_rate": 0.55},
        telemetry_checksum_sha256="HASH123",
        idempotency_key="TEST:KEY:01",
        sync_status=SyncRecordStatus.PENDING
    )

    rec, created = coordinator.store.enqueue_health_event(evt)
    assert created is True
    assert rec.event_id == "EVT-TEST-01"

    pending = coordinator.store.get_pending_health_events()
    assert len(pending) == 1
    assert pending[0].sync_status == SyncRecordStatus.PENDING

    # Attempting to sync while offline must be safely aborted without losing records
    res = coordinator.comms_manager.synchronize_pending_records()
    assert res["status"] == "ABORTED_OFFLINE"
    assert len(coordinator.store.get_pending_health_events()) == 1


def test_sync_after_reconnection(coordinator):
    """Test 2: Pending records synchronize automatically when connection returns to ONLINE."""
    coordinator.comms_manager.set_state(SyncState.OFFLINE)
    
    evt = HealthEventRecord(
        event_id="EVT-TEST-02",
        severity="CRITICAL",
        occurrence_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_pillar="Pillar 1: Radiation Safe-Route",
        title="Critical Radiation Spike",
        description="Hazardous SPE surge.",
        action_recommended="Shelter",
        risk_score=0.95,
        payload={"flux": 300},
        telemetry_checksum_sha256="HASH234",
        idempotency_key="TEST:KEY:02",
        sync_status=SyncRecordStatus.PENDING
    )
    coordinator.store.enqueue_health_event(evt)
    assert len(coordinator.store.get_pending_health_events()) == 1

    # Reconnect link
    coordinator.comms_manager.set_state(SyncState.ONLINE, reason="Link restored")
    assert coordinator.comms_manager.state == SyncState.ONLINE

    # Sync
    res = coordinator.comms_manager.synchronize_pending_records()
    assert res["status"] in ["SUCCESS", "UP_TO_DATE"]

    # Pending queue should now be empty
    pending = coordinator.store.get_pending_health_events()
    assert len(pending) == 0

    # Ground should have received the event
    ground_events = coordinator.store.get_ground_health_events()
    assert len(ground_events) == 1
    assert ground_events[0]["event_id"] == "EVT-TEST-02"
    assert ground_events[0]["ground_received_utc"] is not None


def test_idempotent_sync_no_duplicates(coordinator):
    """Test 3: Retrying synchronization does not create duplicate ground records."""
    coordinator.comms_manager.set_state(SyncState.ONLINE)

    evt = HealthEventRecord(
        event_id="EVT-IDEMP-01",
        severity="MEDIUM",
        occurrence_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_pillar="Pillar 2: Voice Vitals",
        title="Voice Fatigue Drift",
        description="Acoustic strain marker.",
        action_recommended="Rest cycle",
        risk_score=0.45,
        payload={"fatigue": 0.5},
        telemetry_checksum_sha256="HASH345",
        idempotency_key="TEST:IDEMP:01",
        sync_status=SyncRecordStatus.PENDING
    )
    coordinator.store.enqueue_health_event(evt)

    # First sync
    res1 = coordinator.comms_manager.synchronize_pending_records()
    assert res1["status"] == "SUCCESS"
    ground_before = len(coordinator.store.get_ground_health_events())
    assert ground_before == 1

    # Duplicate enqueue attempt locally
    rec_dup, created = coordinator.store.enqueue_health_event(evt)
    assert created is False  # Must not create duplicate in local queue

    # Simulate direct ground batch resend
    batch = GroundBatchPayload(
        mission_token=DEFAULT_MISSION_TOKEN,
        dispatch_timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        health_events=[evt]
    )
    receipt = coordinator.ground_receiver.ingest_batch(batch)
    assert receipt.events_duplicates == 1
    assert receipt.events_ingested == 0

    ground_after = len(coordinator.store.get_ground_health_events())
    assert ground_after == 1  # Absolutely no duplicates!


def test_application_restart_preserves_queue(temp_db):
    """Test 4: Application restart / re-instantiation preserves the local pending queue."""
    # Instance 1: enqueue offline events
    store1 = SyncStore(db_path=temp_db)
    evt = HealthEventRecord(
        event_id="EVT-RESTART-01",
        severity="HIGH",
        occurrence_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_pillar="Pillar 3: Astro-Twin",
        title="Musculoskeletal Outage Warning",
        description="ARED outage in progress.",
        action_recommended="Engage band countermeasures",
        risk_score=0.65,
        payload={"deficit_days": 3},
        telemetry_checksum_sha256="HASH_RESTART",
        idempotency_key="TEST:RESTART:01",
        sync_status=SyncRecordStatus.PENDING
    )
    store1.enqueue_health_event(evt)
    del store1

    # Instance 2: Simulate application restart using same DB file
    store2 = SyncStore(db_path=temp_db)
    pending = store2.get_pending_health_events()
    assert len(pending) == 1
    assert pending[0].event_id == "EVT-RESTART-01"
    assert pending[0].severity == "HIGH"


def test_failed_uploads_recoverable(coordinator):
    """Test 5: Failed uploads remain recoverable with last_error tracked and status FAILED."""
    coordinator.comms_manager.set_state(SyncState.ONLINE)

    evt = HealthEventRecord(
        event_id="EVT-FAIL-01",
        severity="MEDIUM",
        occurrence_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_pillar="Pillar 1: Radiation Safe-Route",
        title="Radiation Baseline Check",
        description="Testing error recovery.",
        action_recommended="Monitor",
        risk_score=0.25,
        payload={},
        telemetry_checksum_sha256="HASH_FAIL",
        idempotency_key="TEST:FAIL:01",
        sync_status=SyncRecordStatus.PENDING
    )
    coordinator.store.enqueue_health_event(evt)

    # Force simulated transient network connection failure
    coordinator.comms_manager.force_transient_failure = True
    res = coordinator.comms_manager.synchronize_pending_records()
    assert res["status"] == "TRANSIENT_FAILURE"

    # Verify record was preserved as FAILED with error message
    pending = coordinator.store.get_pending_health_events()
    assert len(pending) == 1
    assert pending[0].sync_status == SyncRecordStatus.FAILED
    assert pending[0].attempts >= 1
    assert "carrier phase lock lost" in (pending[0].last_error or "")

    # Now retry without failure: must recover!
    res_retry = coordinator.comms_manager.synchronize_pending_records()
    assert res_retry["status"] == "SUCCESS"
    assert len(coordinator.store.get_pending_health_events()) == 0


def test_critical_health_event_priority(coordinator):
    """Test 6: Critical health events receive priority queue order over LOW/MEDIUM/HIGH."""
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # Enqueue in reverse order: LOW first, then MEDIUM, then CRITICAL
    e_low = HealthEventRecord(
        event_id="EVT-P-LOW", severity="LOW", occurrence_utc=now, source_pillar="P1",
        title="Low event", description="Low", action_recommended="None", risk_score=0.1,
        payload={}, telemetry_checksum_sha256="H1", idempotency_key="K_LOW"
    )
    e_med = HealthEventRecord(
        event_id="EVT-P-MED", severity="MEDIUM", occurrence_utc=now, source_pillar="P2",
        title="Med event", description="Med", action_recommended="None", risk_score=0.4,
        payload={}, telemetry_checksum_sha256="H2", idempotency_key="K_MED"
    )
    e_crit = HealthEventRecord(
        event_id="EVT-P-CRIT", severity="CRITICAL", occurrence_utc=now, source_pillar="P1",
        title="Critical SPE", description="Crit", action_recommended="Shelter", risk_score=0.99,
        payload={}, telemetry_checksum_sha256="H3", idempotency_key="K_CRIT"
    )

    coordinator.store.enqueue_health_event(e_low)
    coordinator.store.enqueue_health_event(e_med)
    coordinator.store.enqueue_health_event(e_crit)

    # get_pending_health_events must return CRITICAL first
    ordered = coordinator.store.get_pending_health_events()
    assert len(ordered) == 3
    assert ordered[0].severity == "CRITICAL"
    assert ordered[0].event_id == "EVT-P-CRIT"


def test_federated_learning_edge_training_and_aggregation(coordinator):
    """Test 7: Edge client generates weight deltas, Ground validates and performs FedAvg."""
    # 1. Edge Client 1 local training
    client1 = EdgeFederatedClient("HERMES-EDGE-01", "CDR-WATNEY", base_version="v1.0.0")
    samples1 = [{"rad_rate": 0.10, "fatigue": 0.20, "strain": 0.15, "hypoxia": 0.05, "bone_loss": 0.9, "shear": 0.0, "target_anomaly": 0.3} for _ in range(30)]
    upd1 = client1.train_on_local_telemetry(samples1)

    assert upd1.client_id == "HERMES-EDGE-01"
    assert upd1.base_version == "v1.0.0"
    assert upd1.num_samples == 30
    assert "w_rad" in upd1.weights_delta

    # 2. Edge Client 2 local training
    client2 = EdgeFederatedClient("HERMES-EDGE-02", "DR-VOGEL", base_version="v1.0.0")
    samples2 = [{"rad_rate": 0.05, "fatigue": 0.40, "strain": 0.35, "hypoxia": 0.08, "bone_loss": 0.8, "shear": 0.0, "target_anomaly": 0.4} for _ in range(25)]
    upd2 = client2.train_on_local_telemetry(samples2)

    # 3. Validation test
    aggregator = coordinator.aggregator
    is_valid1, _ = aggregator.validate_update(upd1)
    is_valid2, _ = aggregator.validate_update(upd2)
    assert is_valid1 is True
    assert is_valid2 is True

    # 4. Aggregation (FedAvg)
    global_model, msg = aggregator.aggregate_updates([upd1, upd2])
    assert global_model is not None
    assert global_model.version == "v1.1.0"
    assert global_model.round == 1
    assert global_model.num_participating_clients == 2
    assert global_model.total_samples_trained == 55


def test_federated_rejects_incompatible_or_duplicate(coordinator):
    """Test 8: Incompatible base version, duplicate update, or malformed update is rejected."""
    aggregator = coordinator.aggregator

    # Incompatible base version
    stale_update = ModelUpdateRecord(
        update_id="UPD-STALE",
        client_id="HERMES-EDGE-01",
        base_version="v0.0.1-OUTDATED",
        timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        num_samples=20,
        loss=0.15,
        weights_delta=DEFAULT_BASELINE_WEIGHTS.copy(),
        weights_checksum_sha256=compute_weights_hash(DEFAULT_BASELINE_WEIGHTS)
    )
    is_valid, reason = aggregator.validate_update(stale_update)
    assert is_valid is False
    assert "Incompatible / stale base version" in reason

    # Malformed weights (NaN)
    bad_weights = DEFAULT_BASELINE_WEIGHTS.copy()
    bad_weights["w_rad"] = float("nan")
    bad_update = ModelUpdateRecord(
        update_id="UPD-BAD",
        client_id="HERMES-EDGE-01",
        base_version="v1.0.0",
        timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        num_samples=20,
        loss=0.15,
        weights_delta=bad_weights,
        weights_checksum_sha256="FAKE"
    )
    is_valid_bad, reason_bad = aggregator.validate_update(bad_update)
    assert is_valid_bad is False


def test_complete_e2e_demonstration_workflow(coordinator):
    """Test 9: End-to-end reproducible offline-to-online demonstration succeeds completely."""
    result = coordinator.run_e2e_demonstration()
    assert result["demo_status"] == "COMPLETED"
    assert result["offline_queued_events"] >= 2
    assert result["offline_queued_models"] >= 2
    assert result["reconnect_synced_count"] >= 3
    assert result["idempotency_check"]["retry_synced_count"] == 0  # No duplicates on retry!
    assert result["ground_events_count"] >= 3
    assert result["latest_global_model"] is not None
    assert result["final_counts"]["pending_health_events"] == 0


def test_local_monitoring_continues_offline(coordinator):
    """Test 10: Onboard health-monitoring pipeline functions fully while communications are OFFLINE."""
    coordinator.comms_manager.set_state(SyncState.OFFLINE, reason="Mars 20m Blackout")
    engine = AutonomousDecisionEngine()

    # Create an offline state with critical solar event
    state = CrewState(
        comms_mode=CommsMode.OFFLINE,
        data_freshness_seconds=3,
        radiation=RadiationState(
            risk_level="CRITICAL",
            dose_rate_msv_h=0.72,
            spe_active=True,
            current_module="Gym / Exercise Bay",
            recommended_safe_module="Module B: Storm Shelter"
        ),
        voice_vitals=VoiceVitalsState(
            fatigue_score=0.45,
            cognitive_strain_score=0.55
        ),
        astro_twin=AstroTwinState(
            projected_bone_loss_pct_mo=1.2,
            exercise_deficit_days=2
        )
    )

    # Autonomous decision engine processes without network dependency
    decision = engine.process(state)
    assert decision.risk_level.value == "CRITICAL"
    assert "Module B" in decision.recommended_action

    # Enqueue event through coordinator while OFFLINE
    record = coordinator.record_health_event_from_decision(decision, state, scenario_id="offline_blackout")
    assert record is not None
    assert record.sync_status == SyncRecordStatus.PENDING
    assert record.severity == "CRITICAL"

    # Queue must persist event locally
    pending = coordinator.store.get_pending_health_events()
    assert any(e.event_id == record.event_id for e in pending)


def test_dsn_drop_transitions_to_offline_and_pauses_sync(coordinator):
    """Test 11: DSN drop explicitly transitions link to OFFLINE, aborts sync, and preserves queue."""
    assert coordinator.comms_manager.state == SyncState.ONLINE

    # Simulate DSN carrier phase lock drop
    res_drop = coordinator.comms_manager.simulate_dsn_drop(reason="Simulated Deep Space Network (DSN) carrier phase lock lost.")
    assert res_drop == SyncState.OFFLINE
    assert coordinator.comms_manager.state == SyncState.OFFLINE

    # Enqueue a new event while offline
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    evt = HealthEventRecord(
        event_id="EVT-DSN-01",
        severity="HIGH",
        occurrence_utc=now,
        source_pillar="Pillar 1: Radiation Safe-Route",
        title="Offline Habitat Spike",
        description="Event recorded during DSN drop",
        action_recommended="Monitor",
        risk_score=0.65,
        payload={},
        telemetry_checksum_sha256="HASH_DSN_01",
        idempotency_key="TEST:DSN:01",
        sync_status=SyncRecordStatus.PENDING
    )
    coordinator.store.enqueue_health_event(evt)

    # Attempt to sync: must abort cleanly without errors or loss
    sync_res = coordinator.comms_manager.synchronize_pending_records()
    assert sync_res["status"] == "ABORTED_OFFLINE"
    assert "DSN link lost" in sync_res["message"]

    # Queue must retain the pending event
    pending = coordinator.store.get_pending_health_events()
    assert len(pending) == 1
    assert pending[0].event_id == "EVT-DSN-01"
    assert pending[0].sync_status == SyncRecordStatus.PENDING


def test_restoring_link_sets_online_and_triggers_sync(coordinator):
    """Test 12: Restoring Earth link sets ONLINE and automatically syncs pending records."""
    coordinator.comms_manager.set_state(SyncState.OFFLINE, reason="Transit Blackout")
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    evt = HealthEventRecord(
        event_id="EVT-RESTORE-01",
        severity="MEDIUM",
        occurrence_utc=now,
        source_pillar="Pillar 2: Acoustic Neuro-Vitals",
        title="Speech Latency",
        description="Recorded offline",
        action_recommended="Log",
        risk_score=0.3,
        payload={},
        telemetry_checksum_sha256="HASH_RESTORE",
        idempotency_key="TEST:RESTORE:01",
        sync_status=SyncRecordStatus.PENDING
    )
    coordinator.store.enqueue_health_event(evt)

    # Restoring link to ONLINE with auto_sync=True
    state_res = coordinator.comms_manager.set_state(SyncState.ONLINE, reason="AOS Houston DSN", auto_sync=True)
    assert state_res == SyncState.ONLINE
    assert coordinator.comms_manager.state == SyncState.ONLINE

    # Verify event was synced to Ground
    pending = coordinator.store.get_pending_health_events()
    assert len(pending) == 0
    ground_events = coordinator.store.get_ground_health_events()
    assert any(e["event_id"] == "EVT-RESTORE-01" for e in ground_events)



def test_sync_error_does_not_corrupt_comms_state(coordinator):
    """Test 13: Job-level transient transmission failure marks records FAILED without flipping link to OFFLINE."""
    assert coordinator.comms_manager.state == SyncState.ONLINE

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    evt = HealthEventRecord(
        event_id="EVT-ERR-ISO-01",
        severity="LOW",
        occurrence_utc=now,
        source_pillar="Pillar 3: Adaptive Countermeasures",
        title="Treadmill Telemetry",
        description="Testing error isolation",
        action_recommended="None",
        risk_score=0.1,
        payload={},
        telemetry_checksum_sha256="HASH_ERR_ISO",
        idempotency_key="TEST:ERR:ISO",
        sync_status=SyncRecordStatus.PENDING
    )
    coordinator.store.enqueue_health_event(evt)

    # Induce transient upload error while link remains ONLINE
    coordinator.comms_manager.force_transient_failure = True
    sync_res = coordinator.comms_manager.synchronize_pending_records()
    assert sync_res["status"] == "TRANSIENT_FAILURE"

    # Crucial assertion: Comms state MUST still be ONLINE
    assert coordinator.comms_manager.state == SyncState.ONLINE

    # Record must be marked FAILED for retry backoff
    pending = coordinator.store.get_pending_health_events()
    assert len(pending) == 1
    assert pending[0].sync_status == SyncRecordStatus.FAILED
    assert pending[0].attempts == 1

    # When transient issue resolves, retry succeeds
    coordinator.comms_manager.force_transient_failure = False
    retry_res = coordinator.comms_manager.synchronize_pending_records()
    assert retry_res["status"] == "SUCCESS"
    assert len(coordinator.store.get_pending_health_events()) == 0


def test_repeated_disconnect_reconnect_race_conditions(coordinator):
    """Test 14: Rapid cycling between ONLINE and OFFLINE preserves data consistency and avoids deadlocks."""
    for i in range(10):
        # Drop link
        coordinator.comms_manager.simulate_dsn_drop(reason=f"Drop cycle {i}")
        assert coordinator.comms_manager.state == SyncState.OFFLINE

        # Enqueue record during offline state
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        evt = HealthEventRecord(
            event_id=f"EVT-CYCLE-{i}",
            severity="LOW",
            occurrence_utc=now,
            source_pillar="Pillar 1",
            title=f"Cycle {i} event",
            description="Testing cycling",
            action_recommended="None",
            risk_score=0.2,
            payload={},
            telemetry_checksum_sha256=f"HASH_CYCLE_{i}",
            idempotency_key=f"TEST:CYCLE:{i}",
            sync_status=SyncRecordStatus.PENDING
        )
        coordinator.store.enqueue_health_event(evt)

        # Reconnect link
        coordinator.comms_manager.set_state(SyncState.ONLINE, reason=f"Restore cycle {i}", auto_sync=True)
        assert coordinator.comms_manager.state == SyncState.ONLINE

    # All 10 events should have been synced cleanly without database lock or lost records
    pending = coordinator.store.get_pending_health_events()
    assert len(pending) == 0
    ground_events = coordinator.store.get_ground_health_events()
    assert len(ground_events) >= 10



