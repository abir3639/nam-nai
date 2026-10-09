"""Communications State Manager for Deep-Space Interplanetary Links.
Manages ONLINE, OFFLINE, and SYNCING transitions, simulates propagation delays,
and executes reliable store-and-forward synchronization with bounded exponential backoff.
"""

import time
import datetime
import threading
from typing import Dict, Any, List, Optional, Tuple

from aegis_deepspace.sync.models import (
    SyncState,
    SyncRecordStatus,
    HealthEventRecord,
    TelemetrySummaryRecord,
    ModelUpdateRecord,
    SyncStatusOverview
)
from aegis_deepspace.sync.persistence import SyncStore
from aegis_deepspace.sync.ground_receiver import GroundReceiver, GroundBatchPayload, DEFAULT_MISSION_TOKEN
from aegis_deepspace.sync.federated_engine import GroundFederatedAggregator, EdgeFederatedClient


class CommsManager:
    """Manages deep-space communication states and autonomous store-and-forward synchronization."""

    def __init__(
        self,
        store: SyncStore,
        ground_receiver: GroundReceiver,
        initial_state: SyncState = SyncState.ONLINE
    ):
        self.store = store
        self.ground_receiver = ground_receiver
        self._state: SyncState = initial_state
        self._lock = threading.Lock()
        
        # Configuration parameters
        self.simulated_latency_seconds = 1200  # 20-minute Mars delay baseline
        self.simulated_failure_rate_pct = 0.0  # Percentage chance of transient DSN drop
        self.force_transient_failure = False   # Toggle to simulate momentary connection drop
        self.last_successful_sync_utc: Optional[str] = None
        self.max_retries = 5
        self.base_backoff_seconds = 1.0
        self.max_backoff_seconds = 16.0

        self.last_sync_result: Optional[Dict[str, Any]] = None

        # Log initial state
        self.store.log_state_transition(
            old_state="BOOT",
            new_state=self._state.value,
            reason="Subsystem initialization"
        )

    @property
    def state(self) -> SyncState:
        with self._lock:
            return self._state

    def set_state(self, new_state: SyncState, reason: str = "Operator manual command", auto_sync: bool = True) -> SyncState:
        """Transitions communications link to a new state and logs the transition."""
        old_val = ""
        trigger_sync = False
        with self._lock:
            if self._state == new_state:
                return self._state
            old_val = self._state.value
            self._state = new_state
            if new_state == SyncState.ONLINE and auto_sync:
                trigger_sync = True

        self.store.log_state_transition(
            old_state=old_val,
            new_state=new_state.value,
            reason=reason
        )
        self.store.log_activity(
            action="STATE_CHANGE",
            status="INFO",
            details=f"Comms transitioned from {old_val} to {new_state.value} ({reason})"
        )

        # Automatic sync trigger when connection is restored
        if trigger_sync:
            self.last_sync_result = self.synchronize_pending_records(force=True)

        return self._state

    def toggle_connection(self, reason: str = "Operator toggle") -> SyncState:
        """Toggles link between ONLINE and OFFLINE."""
        current = self.state
        if current == SyncState.ONLINE:
            return self.set_state(SyncState.OFFLINE, reason=reason)
        else:
            return self.set_state(SyncState.ONLINE, reason=reason)

    def simulate_dsn_drop(self, reason: str = "DSN link lost. Onboard monitoring continues; synchronization paused.") -> SyncState:
        """Simulates an abrupt Deep Space Network carrier lock drop / occultation, transitioning immediately to OFFLINE."""
        return self.set_state(SyncState.OFFLINE, reason=reason, auto_sync=False)

    def synchronize_pending_records(self, batch_size: int = 50, force: bool = False) -> Dict[str, Any]:
        """Executes store-and-forward synchronization of all pending records.
        Prioritizes CRITICAL health events before routine telemetry summaries or model updates.
        """
        with self._lock:
            current_state = self._state
            if current_state == SyncState.OFFLINE and not force:
                return {
                    "status": "ABORTED_OFFLINE",
                    "message": "DSN link lost. Onboard monitoring continues; synchronization paused.",
                    "synced_count": 0
                }
            if current_state == SyncState.SYNCING:
                return {
                    "status": "ALREADY_SYNCING",
                    "message": "Synchronization batch already in progress.",
                    "synced_count": 0
                }
            self._state = SyncState.SYNCING

        self.store.log_activity(
            action="SYNC_BEGIN",
            status="INFO",
            details="Starting batch store-and-forward transmission to Houston Ground Control."
        )

        pending_events: List[HealthEventRecord] = []
        pending_summaries: List[TelemetrySummaryRecord] = []
        pending_models: List[ModelUpdateRecord] = []

        try:
            # 1. Fetch pending items
            pending_events = self.store.get_pending_health_events(limit=batch_size)
            pending_summaries = self.store.get_pending_telemetry_summaries(limit=batch_size)
            pending_models = self.store.get_pending_model_updates(limit=20)

            # Check for simulated network failure
            if self.force_transient_failure:
                self.force_transient_failure = False  # Reset toggle
                raise ConnectionError("Simulated Deep Space Network (DSN) carrier phase lock lost.")

            total_pending = len(pending_events) + len(pending_summaries) + len(pending_models)
            if total_pending == 0:
                with self._lock:
                    self._state = SyncState.ONLINE
                return {
                    "status": "UP_TO_DATE",
                    "message": "No pending records in queue.",
                    "synced_count": 0
                }

            # 2. Mark records as IN_PROGRESS
            for ev in pending_events:
                self.store.update_health_event_status(ev.event_id, SyncRecordStatus.IN_PROGRESS, increment_attempts=False)
            for sm in pending_summaries:
                self.store.update_telemetry_summary_status(sm.summary_id, SyncRecordStatus.IN_PROGRESS, increment_attempts=False)
            for md in pending_models:
                self.store.update_model_update_status(md.update_id, SyncRecordStatus.IN_PROGRESS, increment_attempts=False)

            # 3. Assemble GroundBatchPayload
            now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
            batch = GroundBatchPayload(
                mission_token=DEFAULT_MISSION_TOKEN,
                spacecraft_id="AEGIS-DEEPSPACE-01 [HERMES CLASS]",
                dispatch_timestamp_utc=now_utc,
                health_events=pending_events,
                telemetry_summaries=pending_summaries,
                model_updates=pending_models
            )

            # 4. Transmit to Houston Ground Receiver
            receipt = self.ground_receiver.ingest_batch(batch)

            if receipt.status in ["SUCCESS", "PARTIAL_SUCCESS"]:
                # Mark confirmed items as SYNCED
                for ev in pending_events:
                    self.store.update_health_event_status(
                        ev.event_id,
                        SyncRecordStatus.SYNCED,
                        ground_received_utc=receipt.ground_received_utc
                    )
                for sm in pending_summaries:
                    self.store.update_telemetry_summary_status(
                        sm.summary_id,
                        SyncRecordStatus.SYNCED,
                        ground_received_utc=receipt.ground_received_utc
                    )
                for md in pending_models:
                    self.store.update_model_update_status(
                        md.update_id,
                        SyncRecordStatus.SYNCED,
                        ground_received_utc=receipt.ground_received_utc
                    )

                self.last_successful_sync_utc = receipt.ground_received_utc
                self.store.log_activity(
                    action="SYNC_COMPLETED",
                    status="SUCCESS",
                    details=(
                        f"Receipt {receipt.receipt_id}: Ingested {receipt.events_ingested} events "
                        f"({receipt.events_duplicates} duplicates skipped), {receipt.summaries_ingested} summaries, "
                        f"{receipt.model_updates_aggregated} model updates aggregated into global model."
                    )
                )

                with self._lock:
                    self._state = SyncState.ONLINE

                return {
                    "status": "SUCCESS",
                    "receipt": receipt.model_dump(),
                    "synced_count": receipt.events_ingested + receipt.summaries_ingested + receipt.model_updates_ingested,
                    "duplicates": receipt.events_duplicates
                }
            else:
                # Ground rejected with error
                err_msg = "; ".join(receipt.errors)
                self._handle_sync_failure(pending_events, pending_summaries, pending_models, err_msg)
                with self._lock:
                    self._state = SyncState.ONLINE
                return {
                    "status": "FAILED",
                    "error": err_msg,
                    "synced_count": 0
                }

        except Exception as ex:
            err_msg = str(ex)
            # Revert items to FAILED for later retry
            if not (pending_events or pending_summaries or pending_models):
                pending_events = self.store.get_pending_health_events(limit=batch_size)
                pending_summaries = self.store.get_pending_telemetry_summaries(limit=batch_size)
                pending_models = self.store.get_pending_model_updates(limit=20)
            self._handle_sync_failure(pending_events, pending_summaries, pending_models, err_msg)

            with self._lock:
                self._state = SyncState.ONLINE

            retained = len(pending_events) + len(pending_summaries) + len(pending_models)
            return {
                "status": "TRANSIENT_FAILURE",
                "error": err_msg,
                "message": f"Transmission failed ({err_msg}). {retained} records safely preserved in queue for automatic retry.",
                "synced_count": 0,
                "retained_count": retained
            }

    def _handle_sync_failure(
        self,
        events: List[HealthEventRecord],
        summaries: List[TelemetrySummaryRecord],
        models: List[ModelUpdateRecord],
        err_msg: str
    ):
        """Marks items as FAILED with bounded retry attempts and logs warning."""
        for ev in events:
            self.store.update_health_event_status(
                ev.event_id,
                SyncRecordStatus.FAILED,
                last_error=err_msg,
                increment_attempts=True
            )
        for sm in summaries:
            self.store.update_telemetry_summary_status(
                sm.summary_id,
                SyncRecordStatus.FAILED,
                last_error=err_msg,
                increment_attempts=True
            )
        for md in models:
            self.store.update_model_update_status(
                md.update_id,
                SyncRecordStatus.FAILED,
                last_error=err_msg,
                increment_attempts=True
            )

        self.store.log_activity(
            action="SYNC_RETRY_QUEUED",
            status="WARNING",
            details=f"Sync failed ({err_msg}). {len(events)+len(summaries)+len(models)} records retained for retry."
        )

    def get_status_overview(self) -> SyncStatusOverview:
        """Returns unified subsystem metrics for the dashboard."""
        counts = self.store.get_counts()
        latest_global = self.store.get_latest_global_model()
        ground_version = latest_global.version if latest_global else "v1.0.0"

        return SyncStatusOverview(
            comms_state=self.state,
            pending_health_events=counts["pending_health_events"],
            pending_telemetry_summaries=counts["pending_telemetry_summaries"],
            pending_model_updates=counts["pending_model_updates"],
            synced_records_total=counts["synced_records_total"],
            failed_records_total=counts["failed_records_total"],
            unsynchronized_critical_count=counts["unsynchronized_critical_count"],
            last_successful_sync_utc=self.last_successful_sync_utc,
            local_model_version=ground_version,  # Edge uses synced global model
            ground_model_version=ground_version,
            simulated_latency_seconds=self.simulated_latency_seconds,
            simulated_failure_rate_pct=self.simulated_failure_rate_pct
        )
