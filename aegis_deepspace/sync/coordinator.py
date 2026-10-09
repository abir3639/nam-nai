"""High-level Coordinator connecting Onboard Monitoring, Persistent Store-and-Forward Sync,
and Houston Ground Control Federated Aggregation.
"""

import hashlib
import datetime
from typing import Dict, Any, List, Optional, Tuple

from aegis_deepspace.models import CrewState, DecisionObject, RiskLevel
from aegis_deepspace.sync.models import (
    SyncState,
    SyncRecordStatus,
    HealthEventRecord,
    TelemetrySummaryRecord,
    ModelUpdateRecord,
    SyncStatusOverview
)
from aegis_deepspace.sync.persistence import SyncStore
from aegis_deepspace.sync.federated_engine import (
    GroundFederatedAggregator,
    EdgeFederatedClient,
    DEFAULT_BASELINE_WEIGHTS
)
from aegis_deepspace.sync.ground_receiver import GroundReceiver
from aegis_deepspace.sync.comms_manager import CommsManager
from aegis_deepspace.xai_engine import XAIEngine


class SyncCoordinator:
    """Facade orchestrating communication states, store-and-forward queueing,
    explainable AI (SHAP) attributions, and federated learning between the spacecraft and Houston Ground Control.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.store = SyncStore(db_path=db_path)
        self.aggregator = GroundFederatedAggregator(self.store)
        self.ground_receiver = GroundReceiver(self.store, self.aggregator)
        self.comms_manager = CommsManager(self.store, self.ground_receiver, initial_state=SyncState.ONLINE)
        self.xai_engine = XAIEngine(coordinator=self)

        # Two simulated edge clients onboard the spacecraft
        self.client_watney = EdgeFederatedClient(
            client_id="HERMES-EDGE-01",
            astronaut_name="CDR-MARK-WATNEY",
            base_version="v1.0.0"
        )
        self.client_vogel = EdgeFederatedClient(
            client_id="HERMES-EDGE-02",
            astronaut_name="DR-ALEX-VOGEL",
            base_version="v1.0.0"
        )

    # =========================================================================
    # HEALTH EVENT & TELEMETRY RECORDING FROM PILLAR 4
    # =========================================================================

    def record_health_event_from_decision(
        self,
        decision: DecisionObject,
        crew_state: CrewState,
        scenario_id: str = "normal",
        force_event_id: Optional[str] = None
    ) -> Optional[HealthEventRecord]:
        """Translates an active decision into an auditable health event and enqueues it.
        Only enqueues if risk level is MEDIUM, HIGH, or CRITICAL, or if special condition met.
        """
        # If risk is nominal, skip logging as an anomaly health event (handled by periodic summary)
        if decision.risk_level == RiskLevel.LOW and not crew_state.radiation.spe_active:
            return None

        # Build stable idempotency key to prevent duplicate creation on repetitive cycles
        # Key depends on scenario_id, risk_level, dose_rate rounded, and day/hour block
        hour_block = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H")
        idempotency_key = f"{scenario_id}:{decision.risk_level.value}:{crew_state.radiation.dose_rate_msv_h:.2f}:{hour_block}"

        event_id = force_event_id or f"EVT-{decision.risk_level.value[:3]}-{hashlib.sha256(idempotency_key.encode()).hexdigest()[:8].upper()}"
        ts_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Identify primary source pillar
        source = "Pillar 4: Decision Fusion"
        if crew_state.radiation.spe_active or crew_state.radiation.dose_rate_msv_h >= 0.10:
            source = "Pillar 1: Radiation Safe-Route"
        elif crew_state.voice_vitals.cognitive_strain_score >= 0.40 or crew_state.voice_vitals.hypoxia_indicator >= 0.30:
            source = "Pillar 2: Voice Vitals"
        elif crew_state.astro_twin.exercise_deficit_days >= 2:
            source = "Pillar 3: Astro-Twin"

        title = f"{decision.risk_level.value} Risk: {decision.recommended_action[:50]}..."
        description = " | ".join(decision.reasons) if decision.reasons else "Autonomous health engine detected anomalous physiological/environmental shift."

        payload = {
            "scenario_id": scenario_id,
            "dose_rate_msv_h": crew_state.radiation.dose_rate_msv_h,
            "cognitive_strain": crew_state.voice_vitals.cognitive_strain_score,
            "fatigue_score": crew_state.voice_vitals.fatigue_score,
            "bone_loss_pct_mo": crew_state.astro_twin.projected_bone_loss_pct_mo,
            "recommended_action": decision.recommended_action,
            "confidence": decision.confidence
        }

        checksum = hashlib.sha256(
            f"{event_id}:{decision.risk_level.value}:{ts_utc}:{title}".encode("utf-8")
        ).hexdigest()[:24].upper()

        # Compute Explainable AI (SHAP) attribution package
        explanation = self.xai_engine.explain_health_event(event=None, crew_state=crew_state)
        explanation.alert_id = event_id

        event = HealthEventRecord(
            event_id=event_id,
            severity=decision.risk_level.value,
            occurrence_utc=ts_utc,
            source_pillar=source,
            title=title,
            description=description,
            action_recommended=decision.recommended_action,
            risk_score=decision.risk_score,
            payload=payload,
            telemetry_checksum_sha256=checksum,
            idempotency_key=idempotency_key,
            sync_status=SyncRecordStatus.PENDING,
            explanation=explanation.model_dump() if hasattr(explanation, "model_dump") else explanation.dict()
        )

        record, created_new = self.store.enqueue_health_event(event)


        if created_new:
            self.store.log_activity(
                action="HEALTH_EVENT_ENQUEUED",
                status="WARNING" if decision.risk_level.value in ["HIGH", "CRITICAL"] else "INFO",
                details=f"[{record.severity}] {record.title} (ID: {record.event_id}) queued locally."
            )
            # If currently ONLINE, auto-sync can dispatch immediately
            if self.comms_manager.state == SyncState.ONLINE:
                self.comms_manager.synchronize_pending_records()

        return record

    def record_telemetry_snapshot(
        self,
        crew_state: CrewState,
        decision: DecisionObject,
        scenario_id: str = "normal"
    ) -> TelemetrySummaryRecord:
        """Records a periodic telemetry summary snapshot."""
        ts_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
        summary_id = f"SUM-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S%f')[:17]}"
        checksum = hashlib.sha256(
            f"{summary_id}:{scenario_id}:{decision.risk_score:.2f}".encode("utf-8")
        ).hexdigest()[:24].upper()

        summary = TelemetrySummaryRecord(
            summary_id=summary_id,
            timestamp_utc=ts_utc,
            scenario_id=scenario_id,
            risk_level=decision.risk_level.value,
            risk_score=decision.risk_score,
            dose_rate_msv_h=crew_state.radiation.dose_rate_msv_h,
            voice_strain=crew_state.voice_vitals.cognitive_strain_score,
            projected_bone_loss=crew_state.astro_twin.projected_bone_loss_pct_mo,
            telemetry_checksum_sha256=checksum,
            sync_status=SyncRecordStatus.PENDING
        )
        self.store.enqueue_telemetry_summary(summary)
        return summary

    # =========================================================================
    # FEDERATED LEARNING ACTIONS
    # =========================================================================

    def trigger_edge_client_training(
        self,
        client_target: str = "both",
        num_samples_client1: int = 40,
        num_samples_client2: int = 35
    ) -> List[ModelUpdateRecord]:
        """Runs onboard edge training for Client 1 (Watney) and/or Client 2 (Vogel),
        generating model updates and queueing them in the local persistent store.
        """
        # Synchronize edge clients' base version with ground
        latest_global = self.store.get_latest_global_model()
        active_ver = latest_global.version if latest_global else "v1.0.0"
        self.client_watney.current_base_version = active_ver
        self.client_vogel.current_base_version = active_ver

        updates_created = []

        if client_target in ["both", "client1", "watney"]:
            # Client 1: Simulated telemetry with high exercise/airlock variance
            samples1 = [
                {
                    "rad_rate": 0.08 + (0.01 * (i % 5)),
                    "fatigue": 0.22 + (0.03 * (i % 4)),
                    "strain": 0.18 + (0.02 * (i % 3)),
                    "hypoxia": 0.05,
                    "bone_loss": 0.95,
                    "shear": 0.0,
                    "target_anomaly": 0.25
                }
                for i in range(num_samples_client1)
            ]
            upd1 = self.client_watney.train_on_local_telemetry(samples1, learning_rate=0.06)
            self.store.enqueue_model_update(upd1)
            updates_created.append(upd1)
            self.store.log_activity(
                action="EDGE_TRAINING_COMPLETE",
                status="INFO",
                details=f"Client {upd1.client_id} completed local training ({upd1.num_samples} samples, loss {upd1.loss}). Update {upd1.update_id} queued."
            )

        if client_target in ["both", "client2", "vogel"]:
            # Client 2: Simulated telemetry with high lab/sleep shift variance
            samples2 = [
                {
                    "rad_rate": 0.03 + (0.005 * (i % 4)),
                    "fatigue": 0.35 + (0.04 * (i % 6)),
                    "strain": 0.30 + (0.03 * (i % 5)),
                    "hypoxia": 0.07,
                    "bone_loss": 0.85,
                    "shear": 0.0,
                    "target_anomaly": 0.32
                }
                for i in range(num_samples_client2)
            ]
            upd2 = self.client_vogel.train_on_local_telemetry(samples2, learning_rate=0.05)
            self.store.enqueue_model_update(upd2)
            updates_created.append(upd2)
            self.store.log_activity(
                action="EDGE_TRAINING_COMPLETE",
                status="INFO",
                details=f"Client {upd2.client_id} completed local training ({upd2.num_samples} samples, loss {upd2.loss}). Update {upd2.update_id} queued."
            )

        # If ONLINE, auto-sync dispatches
        if self.comms_manager.state == SyncState.ONLINE:
            self.comms_manager.synchronize_pending_records()

        return updates_created

    # =========================================================================
    # REPRODUCIBLE END-TO-END DEMONSTRATION WORKFLOW
    # =========================================================================

    def run_e2e_demonstration(self) -> Dict[str, Any]:
        """Executes the complete reproducible 12-step offline-to-online demonstration sequence."""
        # 1. Reset to baseline
        self.store.reset_all()
        self.comms_manager.set_state(SyncState.ONLINE, reason="Demo Step 1: Initialize ONLINE link")

        # 2. Simulate baseline nominal telemetry (ONLINE)
        ts_base = datetime.datetime.now(datetime.timezone.utc).isoformat()
        evt_nom = HealthEventRecord(
            event_id="EVT-NOM-BASELINE-01",
            severity="LOW",
            occurrence_utc=ts_base,
            source_pillar="Pillar 4: Decision Fusion",
            title="Nominal Crew Telemetry Synchronized",
            description="All environmental and physiological parameters within baseline tolerances.",
            action_recommended="Continue nominal flight routine.",
            risk_score=0.10,
            payload={"dose_rate_msv_h": 0.02, "fatigue": 0.12},
            telemetry_checksum_sha256=hashlib.sha256(b"EVT-NOM-BASELINE-01").hexdigest()[:24].upper(),
            idempotency_key="DEMO:NOMINAL:01",
            sync_status=SyncRecordStatus.PENDING,
            explanation=self.xai_engine.explain_crew_anomaly({"rad_rate": 0.02, "fatigue": 0.12}, alert_id="EVT-NOM-BASELINE-01").model_dump()
        )
        self.store.enqueue_health_event(evt_nom)
        sync_nom = self.comms_manager.synchronize_pending_records()

        # 3. Disconnect communications (OFFLINE BLACKOUT)
        self.comms_manager.set_state(SyncState.OFFLINE, reason="Demo Step 4: Orbital Conjunction Comms Blackout (Mars 20m Delay)")

        # 4. Generate Event 1 during blackout (HIGH severity solar flare)
        ts_storm = datetime.datetime.now(datetime.timezone.utc).isoformat()
        evt_storm = HealthEventRecord(
            event_id="EVT-SPE-BLACKOUT-02",
            severity="CRITICAL",
            occurrence_utc=ts_storm,
            source_pillar="Pillar 1: Radiation Safe-Route",
            title="CRITICAL Solar Particle Event Detected in Transit",
            description="External flux surge to 250 mSv. Dose rate in Gym 0.68 mSv/h exceeding NASA ceiling.",
            action_recommended="Immediate evacuation to Module B Water-Wall Storm Shelter.",
            risk_score=0.92,
            payload={"dose_rate_msv_h": 0.68, "spe_active": True},
            telemetry_checksum_sha256=hashlib.sha256(b"EVT-SPE-BLACKOUT-02").hexdigest()[:24].upper(),
            idempotency_key="DEMO:STORM:02",
            sync_status=SyncRecordStatus.PENDING,
            explanation=self.xai_engine.explain_crew_anomaly({"rad_rate": 0.68, "fatigue": 0.15}, alert_id="EVT-SPE-BLACKOUT-02").model_dump()
        )
        self.store.enqueue_health_event(evt_storm)

        # 5. Generate Event 2 during blackout (HIGH severity vocal fatigue & hypoxia marker)
        ts_voice = datetime.datetime.now(datetime.timezone.utc).isoformat()
        evt_voice = HealthEventRecord(
            event_id="EVT-VOX-BLACKOUT-03",
            severity="HIGH",
            occurrence_utc=ts_voice,
            source_pillar="Pillar 2: Voice Vitals",
            title="Acoustic Hypoxia & Cognitive Exhaustion Marker",
            description="Speech jitter +2.4 SD above baseline, fundamental frequency drift indicates acute strain.",
            action_recommended="Verify cabin ppO2 partial pressure; stage supplemental O2 mask.",
            risk_score=0.74,
            payload={"fatigue": 0.78, "hypoxia": 0.45},
            telemetry_checksum_sha256=hashlib.sha256(b"EVT-VOX-BLACKOUT-03").hexdigest()[:24].upper(),
            idempotency_key="DEMO:VOICE:03",
            sync_status=SyncRecordStatus.PENDING,
            explanation=self.xai_engine.explain_crew_anomaly({"fatigue": 0.78, "hypoxia": 0.45}, alert_id="EVT-VOX-BLACKOUT-03").model_dump()
        )
        self.store.enqueue_health_event(evt_voice)


        # 6. Train edge federated models while OFFLINE
        model_updates = self.trigger_edge_client_training(client_target="both", num_samples_client1=45, num_samples_client2=38)

        # 7. Verify pending queue status
        counts_offline = self.store.get_counts()

        # 8. Reconnect communications link (ONLINE)
        self.comms_manager.set_state(SyncState.ONLINE, reason="Demo Step 8: Earth Link Restored via Mars Relay Orbiter")
        reconnect_result = self.comms_manager.last_sync_result or {}

        # 9. Additional sync trigger (if anything remained)
        sync_result = self.comms_manager.synchronize_pending_records()
        total_synced = reconnect_result.get("synced_count", 0) + sync_result.get("synced_count", 0)

        # 10. Test idempotency: re-run sync immediately to ensure no duplicate ground records
        sync_retry = self.comms_manager.synchronize_pending_records()

        # 11. Fetch Ground records
        ground_events = self.store.get_ground_health_events()
        global_model = self.store.get_latest_global_model()
        final_counts = self.store.get_counts()

        return {
            "demo_status": "COMPLETED",
            "offline_queued_events": counts_offline["pending_health_events"],
            "offline_queued_models": counts_offline["pending_model_updates"],
            "reconnect_synced_count": total_synced,
            "idempotency_check": {
                "retry_synced_count": sync_retry.get("synced_count", 0),
                "retry_status": sync_retry.get("status")
            },
            "ground_events_count": len(ground_events),
            "ground_events": ground_events,
            "latest_global_model": global_model.model_dump() if global_model else None,
            "final_counts": final_counts
        }


# Global coordinator singleton
default_sync_coordinator = SyncCoordinator()
