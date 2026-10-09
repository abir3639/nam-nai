"""SQLite-backed persistent store for store-and-forward telemetry and federated learning.
Ensures zero data loss across application restarts, strict ACID transactions,
and idempotency preventing duplicate event creation or ground ingestion.
"""

import os
import json
import sqlite3
import hashlib
import uuid
import datetime
import threading
from typing import List, Dict, Any, Optional, Tuple

from aegis_deepspace.sync.models import (
    SyncRecordStatus,
    HealthEventRecord,
    TelemetrySummaryRecord,
    ModelUpdateRecord,
    FederatedGlobalModel,
    SyncActivityLog
)

DEFAULT_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "sync_store.db")
)


class SyncStore:
    """Thread-safe, restart-persistent SQLite store for spacecraft and ground records."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                
                # 1. Onboard Health Events Queue
                cur.execute("""
                CREATE TABLE IF NOT EXISTS onboard_health_events (
                    event_id TEXT PRIMARY KEY,
                    severity TEXT NOT NULL,
                    occurrence_utc TEXT NOT NULL,
                    source_pillar TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    action_recommended TEXT NOT NULL,
                    risk_score REAL NOT NULL,
                    payload_json TEXT NOT NULL,
                    telemetry_checksum_sha256 TEXT NOT NULL,
                    idempotency_key TEXT UNIQUE NOT NULL,
                    sync_status TEXT NOT NULL,
                    ground_received_utc TEXT,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT,
                    explanation_json TEXT
                )
                """)

                # 2. Onboard Telemetry Summaries Queue
                cur.execute("""
                CREATE TABLE IF NOT EXISTS onboard_telemetry_summaries (
                    summary_id TEXT PRIMARY KEY,
                    timestamp_utc TEXT NOT NULL,
                    scenario_id TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    risk_score REAL NOT NULL,
                    dose_rate_msv_h REAL NOT NULL,
                    voice_strain REAL NOT NULL,
                    projected_bone_loss REAL NOT NULL,
                    telemetry_checksum_sha256 TEXT NOT NULL,
                    sync_status TEXT NOT NULL,
                    ground_received_utc TEXT,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT
                )
                """)

                # 3. Onboard Model Updates Queue
                cur.execute("""
                CREATE TABLE IF NOT EXISTS onboard_model_updates (
                    update_id TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL,
                    base_version TEXT NOT NULL,
                    timestamp_utc TEXT NOT NULL,
                    num_samples INTEGER NOT NULL,
                    loss REAL NOT NULL,
                    weights_delta_json TEXT NOT NULL,
                    weights_checksum_sha256 TEXT NOT NULL,
                    sync_status TEXT NOT NULL,
                    ground_received_utc TEXT,
                    aggregated INTEGER NOT NULL DEFAULT 0,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT
                )
                """)

                # 4. Houston Ground Control Received Events
                cur.execute("""
                CREATE TABLE IF NOT EXISTS ground_health_events (
                    event_id TEXT PRIMARY KEY,
                    severity TEXT NOT NULL,
                    occurrence_utc TEXT NOT NULL,
                    ground_received_utc TEXT NOT NULL,
                    source_pillar TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    action_recommended TEXT NOT NULL,
                    risk_score REAL NOT NULL,
                    payload_json TEXT NOT NULL,
                    telemetry_checksum_sha256 TEXT NOT NULL,
                    idempotency_key TEXT UNIQUE NOT NULL,
                    explanation_json TEXT
                )
                """)

                # 5. Houston Ground Control Received Summaries
                cur.execute("""
                CREATE TABLE IF NOT EXISTS ground_telemetry_summaries (
                    summary_id TEXT PRIMARY KEY,
                    timestamp_utc TEXT NOT NULL,
                    ground_received_utc TEXT NOT NULL,
                    scenario_id TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    risk_score REAL NOT NULL,
                    dose_rate_msv_h REAL NOT NULL,
                    voice_strain REAL NOT NULL,
                    projected_bone_loss REAL NOT NULL,
                    telemetry_checksum_sha256 TEXT NOT NULL
                )
                """)

                # 6. Global Federated Models (Houston Archive)
                cur.execute("""
                CREATE TABLE IF NOT EXISTS global_models (
                    version TEXT PRIMARY KEY,
                    round INTEGER NOT NULL,
                    base_version TEXT NOT NULL,
                    aggregated_at_utc TEXT NOT NULL,
                    num_participating_clients INTEGER NOT NULL,
                    total_samples_trained INTEGER NOT NULL,
                    global_weights_json TEXT NOT NULL,
                    weights_checksum_sha256 TEXT NOT NULL,
                    aggregation_notes TEXT NOT NULL
                )
                """)

                # 7. Sync Activity Logs
                cur.execute("""
                CREATE TABLE IF NOT EXISTS sync_activity_logs (
                    log_id TEXT PRIMARY KEY,
                    timestamp_utc TEXT NOT NULL,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT NOT NULL
                )
                """)

                # 8. Communication State Transitions
                cur.execute("""
                CREATE TABLE IF NOT EXISTS comms_state_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp_utc TEXT NOT NULL,
                    old_state TEXT NOT NULL,
                    new_state TEXT NOT NULL,
                    reason TEXT NOT NULL
                )
                """)

                # Schema migration safe guards for existing database files
                try:
                    cur.execute("ALTER TABLE onboard_health_events ADD COLUMN explanation_json TEXT")
                except sqlite3.OperationalError:
                    pass
                try:
                    cur.execute("ALTER TABLE ground_health_events ADD COLUMN explanation_json TEXT")
                except sqlite3.OperationalError:
                    pass

                conn.commit()


    # =========================================================================
    # ONBOARD QUEUE OPERATIONS
    # =========================================================================

    def enqueue_health_event(self, event: HealthEventRecord) -> Tuple[HealthEventRecord, bool]:
        """Enqueues an onboard health event. If idempotency_key already exists, returns existing without duplicate.
        Returns (record, created_new: bool).
        """
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                # Check for existing idempotency key
                cur.execute(
                    "SELECT * FROM onboard_health_events WHERE idempotency_key = ? OR event_id = ?",
                    (event.idempotency_key, event.event_id)
                )
                row = cur.fetchone()
                if row:
                    existing = self._row_to_health_event(row)
                    return existing, False

                expl_json = json.dumps(event.explanation) if event.explanation else None
                cur.execute("""
                INSERT INTO onboard_health_events (
                    event_id, severity, occurrence_utc, source_pillar, title, description,
                    action_recommended, risk_score, payload_json, telemetry_checksum_sha256,
                    idempotency_key, sync_status, ground_received_utc, attempts, last_error, explanation_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.event_id,
                    event.severity,
                    event.occurrence_utc,
                    event.source_pillar,
                    event.title,
                    event.description,
                    event.action_recommended,
                    event.risk_score,
                    json.dumps(event.payload),
                    event.telemetry_checksum_sha256,
                    event.idempotency_key,
                    event.sync_status.value,
                    event.ground_received_utc,
                    event.attempts,
                    event.last_error,
                    expl_json
                ))
                conn.commit()

                return event, True

    def enqueue_telemetry_summary(self, summary: TelemetrySummaryRecord) -> bool:
        """Enqueues a telemetry summary snapshot."""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT summary_id FROM onboard_telemetry_summaries WHERE summary_id = ?", (summary.summary_id,))
                if cur.fetchone():
                    return False
                cur.execute("""
                INSERT INTO onboard_telemetry_summaries (
                    summary_id, timestamp_utc, scenario_id, risk_level, risk_score,
                    dose_rate_msv_h, voice_strain, projected_bone_loss, telemetry_checksum_sha256,
                    sync_status, ground_received_utc, attempts, last_error
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    summary.summary_id,
                    summary.timestamp_utc,
                    summary.scenario_id,
                    summary.risk_level,
                    summary.risk_score,
                    summary.dose_rate_msv_h,
                    summary.voice_strain,
                    summary.projected_bone_loss,
                    summary.telemetry_checksum_sha256,
                    summary.sync_status.value,
                    summary.ground_received_utc,
                    summary.attempts,
                    summary.last_error
                ))
                conn.commit()
                return True

    def enqueue_model_update(self, update: ModelUpdateRecord) -> bool:
        """Enqueues a federated model update."""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT update_id FROM onboard_model_updates WHERE update_id = ?", (update.update_id,))
                if cur.fetchone():
                    return False
                cur.execute("""
                INSERT INTO onboard_model_updates (
                    update_id, client_id, base_version, timestamp_utc, num_samples, loss,
                    weights_delta_json, weights_checksum_sha256, sync_status, ground_received_utc,
                    aggregated, attempts, last_error
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    update.update_id,
                    update.client_id,
                    update.base_version,
                    update.timestamp_utc,
                    update.num_samples,
                    update.loss,
                    json.dumps(update.weights_delta),
                    update.weights_checksum_sha256,
                    update.sync_status.value,
                    update.ground_received_utc,
                    1 if update.aggregated else 0,
                    update.attempts,
                    update.last_error
                ))
                conn.commit()
                return True

    def get_pending_health_events(self, limit: int = 50) -> List[HealthEventRecord]:
        """Returns pending health events ordered by priority: CRITICAL > HIGH > MEDIUM > LOW, then occurrence_utc asc."""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                SELECT * FROM onboard_health_events
                WHERE sync_status IN ('PENDING', 'FAILED', 'IN_PROGRESS')
                ORDER BY 
                    CASE severity
                        WHEN 'CRITICAL' THEN 1
                        WHEN 'HIGH' THEN 2
                        WHEN 'MEDIUM' THEN 3
                        ELSE 4
                    END ASC,
                    occurrence_utc ASC
                LIMIT ?
                """, (limit,))
                rows = cur.fetchall()
                return [self._row_to_health_event(r) for r in rows]

    def get_pending_telemetry_summaries(self, limit: int = 50) -> List[TelemetrySummaryRecord]:
        """Returns pending telemetry summaries."""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                SELECT * FROM onboard_telemetry_summaries
                WHERE sync_status IN ('PENDING', 'FAILED', 'IN_PROGRESS')
                ORDER BY timestamp_utc ASC
                LIMIT ?
                """, (limit,))
                rows = cur.fetchall()
                return [self._row_to_telemetry_summary(r) for r in rows]

    def get_pending_model_updates(self, limit: int = 20) -> List[ModelUpdateRecord]:
        """Returns pending federated model updates."""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                SELECT * FROM onboard_model_updates
                WHERE sync_status IN ('PENDING', 'FAILED', 'IN_PROGRESS')
                ORDER BY timestamp_utc ASC
                LIMIT ?
                """, (limit,))
                rows = cur.fetchall()
                return [self._row_to_model_update(r) for r in rows]

    def update_health_event_status(
        self,
        event_id: str,
        status: SyncRecordStatus,
        ground_received_utc: Optional[str] = None,
        last_error: Optional[str] = None,
        increment_attempts: bool = True
    ):
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                attempts_clause = "attempts = attempts + 1," if increment_attempts else ""
                cur.execute(f"""
                UPDATE onboard_health_events
                SET sync_status = ?,
                    {attempts_clause}
                    ground_received_utc = COALESCE(?, ground_received_utc),
                    last_error = ?
                WHERE event_id = ?
                """, (status.value, ground_received_utc, last_error, event_id))
                conn.commit()

    def update_telemetry_summary_status(
        self,
        summary_id: str,
        status: SyncRecordStatus,
        ground_received_utc: Optional[str] = None,
        last_error: Optional[str] = None,
        increment_attempts: bool = True
    ):
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                attempts_clause = "attempts = attempts + 1," if increment_attempts else ""
                cur.execute(f"""
                UPDATE onboard_telemetry_summaries
                SET sync_status = ?,
                    {attempts_clause}
                    ground_received_utc = COALESCE(?, ground_received_utc),
                    last_error = ?
                WHERE summary_id = ?
                """, (status.value, ground_received_utc, last_error, summary_id))
                conn.commit()

    def update_model_update_status(
        self,
        update_id: str,
        status: SyncRecordStatus,
        ground_received_utc: Optional[str] = None,
        last_error: Optional[str] = None,
        aggregated: Optional[bool] = None,
        increment_attempts: bool = True
    ):
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                attempts_clause = "attempts = attempts + 1," if increment_attempts else ""
                cur.execute(f"""
                UPDATE onboard_model_updates
                SET sync_status = ?,
                    {attempts_clause}
                    ground_received_utc = COALESCE(?, ground_received_utc),
                    last_error = ?,
                    aggregated = CASE WHEN ? IS NOT NULL THEN ? ELSE aggregated END
                WHERE update_id = ?
                """, (status.value, ground_received_utc, last_error, 1 if aggregated else (0 if aggregated is False else None), 1 if aggregated else 0, update_id))
                conn.commit()

    # =========================================================================
    # HOUSTON GROUND CONTROL INGESTION (IDEMPOTENT)
    # =========================================================================

    def ground_ingest_health_event(self, event: HealthEventRecord, received_utc: str) -> Tuple[bool, str]:
        """Ingests a health event into Houston Ground Control table.
        Returns (is_new: bool, message: str).
        """
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT ground_received_utc FROM ground_health_events WHERE event_id = ? OR idempotency_key = ?", (event.event_id, event.idempotency_key))
                row = cur.fetchone()
                if row:
                    return False, f"Event {event.event_id} already exists at Ground (received {row['ground_received_utc']})"

                expl_json = json.dumps(event.explanation) if event.explanation else None
                cur.execute("""
                INSERT INTO ground_health_events (
                    event_id, severity, occurrence_utc, ground_received_utc, source_pillar,
                    title, description, action_recommended, risk_score, payload_json,
                    telemetry_checksum_sha256, idempotency_key, explanation_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.event_id,
                    event.severity,
                    event.occurrence_utc,
                    received_utc,
                    event.source_pillar,
                    event.title,
                    event.description,
                    event.action_recommended,
                    event.risk_score,
                    json.dumps(event.payload),
                    event.telemetry_checksum_sha256,
                    event.idempotency_key,
                    expl_json
                ))
                conn.commit()
                return True, f"Event {event.event_id} successfully ingested at Houston Ground Control."

    def ground_ingest_telemetry_summary(self, summary: TelemetrySummaryRecord, received_utc: str) -> Tuple[bool, str]:
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT summary_id FROM ground_telemetry_summaries WHERE summary_id = ?", (summary.summary_id,))
                if cur.fetchone():
                    return False, f"Summary {summary.summary_id} already ingested"
                cur.execute("""
                INSERT INTO ground_telemetry_summaries (
                    summary_id, timestamp_utc, ground_received_utc, scenario_id, risk_level,
                    risk_score, dose_rate_msv_h, voice_strain, projected_bone_loss,
                    telemetry_checksum_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    summary.summary_id,
                    summary.timestamp_utc,
                    received_utc,
                    summary.scenario_id,
                    summary.risk_level,
                    summary.risk_score,
                    summary.dose_rate_msv_h,
                    summary.voice_strain,
                    summary.projected_bone_loss,
                    summary.telemetry_checksum_sha256
                ))
                conn.commit()
                return True, f"Summary {summary.summary_id} ingested"

    def get_ground_health_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Returns all events received at Houston Ground Control."""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                SELECT * FROM ground_health_events
                ORDER BY ground_received_utc DESC
                LIMIT ?
                """, (limit,))
                rows = cur.fetchall()
                results = []
                for r in rows:
                    expl = None
                    if "explanation_json" in r.keys() and r["explanation_json"]:
                        try:
                            expl = json.loads(r["explanation_json"])
                        except Exception:
                            expl = None
                    results.append({
                        "event_id": r["event_id"],
                        "severity": r["severity"],
                        "occurrence_utc": r["occurrence_utc"],
                        "ground_received_utc": r["ground_received_utc"],
                        "source_pillar": r["source_pillar"],
                        "title": r["title"],
                        "description": r["description"],
                        "action_recommended": r["action_recommended"],
                        "risk_score": r["risk_score"],
                        "payload": json.loads(r["payload_json"]),
                        "telemetry_checksum_sha256": r["telemetry_checksum_sha256"],
                        "idempotency_key": r["idempotency_key"],
                        "explanation": expl
                    })
                return results


    # =========================================================================
    # FEDERATED MODEL MANAGEMENT (HOUSTON GROUND)
    # =========================================================================

    def save_global_model(self, model: FederatedGlobalModel):
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                INSERT OR REPLACE INTO global_models (
                    version, round, base_version, aggregated_at_utc, num_participating_clients,
                    total_samples_trained, global_weights_json, weights_checksum_sha256, aggregation_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    model.version,
                    model.round,
                    model.base_version,
                    model.aggregated_at_utc,
                    model.num_participating_clients,
                    model.total_samples_trained,
                    json.dumps(model.global_weights),
                    model.weights_checksum_sha256,
                    model.aggregation_notes
                ))
                conn.commit()

    def get_latest_global_model(self) -> Optional[FederatedGlobalModel]:
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM global_models ORDER BY round DESC LIMIT 1")
                row = cur.fetchone()
                if not row:
                    return None
                return FederatedGlobalModel(
                    version=row["version"],
                    round=row["round"],
                    base_version=row["base_version"],
                    aggregated_at_utc=row["aggregated_at_utc"],
                    num_participating_clients=row["num_participating_clients"],
                    total_samples_trained=row["total_samples_trained"],
                    global_weights=json.loads(row["global_weights_json"]),
                    weights_checksum_sha256=row["weights_checksum_sha256"],
                    aggregation_notes=row["aggregation_notes"]
                )

    def get_all_global_models(self) -> List[FederatedGlobalModel]:
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM global_models ORDER BY round ASC")
                rows = cur.fetchall()
                return [
                    FederatedGlobalModel(
                        version=r["version"],
                        round=r["round"],
                        base_version=r["base_version"],
                        aggregated_at_utc=r["aggregated_at_utc"],
                        num_participating_clients=r["num_participating_clients"],
                        total_samples_trained=r["total_samples_trained"],
                        global_weights=json.loads(r["global_weights_json"]),
                        weights_checksum_sha256=r["weights_checksum_sha256"],
                        aggregation_notes=r["aggregation_notes"]
                    ) for r in rows
                ]

    # =========================================================================
    # AUDIT LOGS & COUNTS
    # =========================================================================

    def log_activity(self, action: str, status: str, details: str):
        log_id = f"LOG-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO sync_activity_logs (log_id, timestamp_utc, action, status, details) VALUES (?, ?, ?, ?, ?)",
                    (log_id, ts, action, status, details)
                )
                conn.commit()

    def get_activity_logs(self, limit: int = 50) -> List[SyncActivityLog]:
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM sync_activity_logs ORDER BY timestamp_utc DESC LIMIT ?", (limit,))
                rows = cur.fetchall()
                return [
                    SyncActivityLog(
                        log_id=r["log_id"],
                        timestamp_utc=r["timestamp_utc"],
                        action=r["action"],
                        status=r["status"],
                        details=r["details"]
                    ) for r in rows
                ]

    def log_state_transition(self, old_state: str, new_state: str, reason: str):
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO comms_state_history (timestamp_utc, old_state, new_state, reason) VALUES (?, ?, ?, ?)",
                    (ts, old_state, new_state, reason)
                )
                conn.commit()

    def get_state_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM comms_state_history ORDER BY id DESC LIMIT ?", (limit,))
                rows = cur.fetchall()
                return [
                    {
                        "id": r["id"],
                        "timestamp_utc": r["timestamp_utc"],
                        "old_state": r["old_state"],
                        "new_state": r["new_state"],
                        "reason": r["reason"]
                    } for r in rows
                ]

    def get_counts(self) -> Dict[str, int]:
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM onboard_health_events WHERE sync_status IN ('PENDING', 'FAILED', 'IN_PROGRESS')")
                pending_events = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM onboard_telemetry_summaries WHERE sync_status IN ('PENDING', 'FAILED', 'IN_PROGRESS')")
                pending_summaries = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM onboard_model_updates WHERE sync_status IN ('PENDING', 'FAILED', 'IN_PROGRESS')")
                pending_models = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM onboard_health_events WHERE sync_status = 'SYNCED'")
                synced_events = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM onboard_telemetry_summaries WHERE sync_status = 'SYNCED'")
                synced_summaries = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM onboard_model_updates WHERE sync_status = 'SYNCED'")
                synced_models = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM onboard_health_events WHERE sync_status = 'FAILED'")
                failed_events = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM onboard_health_events WHERE sync_status IN ('PENDING', 'FAILED', 'IN_PROGRESS') AND severity = 'CRITICAL'")
                unsynced_critical = cur.fetchone()[0]

                return {
                    "pending_health_events": pending_events,
                    "pending_telemetry_summaries": pending_summaries,
                    "pending_model_updates": pending_models,
                    "synced_records_total": synced_events + synced_summaries + synced_models,
                    "failed_records_total": failed_events,
                    "unsynchronized_critical_count": unsynced_critical
                }

    def reset_all(self):
        """Clears all records for demonstration seeding or testing."""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM onboard_health_events")
                cur.execute("DELETE FROM onboard_telemetry_summaries")
                cur.execute("DELETE FROM onboard_model_updates")
                cur.execute("DELETE FROM ground_health_events")
                cur.execute("DELETE FROM ground_telemetry_summaries")
                cur.execute("DELETE FROM global_models")
                cur.execute("DELETE FROM sync_activity_logs")
                cur.execute("DELETE FROM comms_state_history")
                conn.commit()

    # --- Helpers ---
    def _row_to_health_event(self, r: sqlite3.Row) -> HealthEventRecord:
        expl = None
        if "explanation_json" in r.keys() and r["explanation_json"]:
            try:
                expl = json.loads(r["explanation_json"])
            except Exception:
                expl = None
        return HealthEventRecord(
            event_id=r["event_id"],
            severity=r["severity"],
            occurrence_utc=r["occurrence_utc"],
            source_pillar=r["source_pillar"],
            title=r["title"],
            description=r["description"],
            action_recommended=r["action_recommended"],
            risk_score=r["risk_score"],
            payload=json.loads(r["payload_json"]),
            telemetry_checksum_sha256=r["telemetry_checksum_sha256"],
            idempotency_key=r["idempotency_key"],
            sync_status=SyncRecordStatus(r["sync_status"]),
            ground_received_utc=r["ground_received_utc"],
            attempts=r["attempts"],
            last_error=r["last_error"],
            explanation=expl
        )


    def _row_to_telemetry_summary(self, r: sqlite3.Row) -> TelemetrySummaryRecord:
        return TelemetrySummaryRecord(
            summary_id=r["summary_id"],
            timestamp_utc=r["timestamp_utc"],
            scenario_id=r["scenario_id"],
            risk_level=r["risk_level"],
            risk_score=r["risk_score"],
            dose_rate_msv_h=r["dose_rate_msv_h"],
            voice_strain=r["voice_strain"],
            projected_bone_loss=r["projected_bone_loss"],
            telemetry_checksum_sha256=r["telemetry_checksum_sha256"],
            sync_status=SyncRecordStatus(r["sync_status"]),
            ground_received_utc=r["ground_received_utc"],
            attempts=r["attempts"],
            last_error=r["last_error"]
        )

    def _row_to_model_update(self, r: sqlite3.Row) -> ModelUpdateRecord:
        return ModelUpdateRecord(
            update_id=r["update_id"],
            client_id=r["client_id"],
            base_version=r["base_version"],
            timestamp_utc=r["timestamp_utc"],
            num_samples=r["num_samples"],
            loss=r["loss"],
            weights_delta=json.loads(r["weights_delta_json"]),
            weights_checksum_sha256=r["weights_checksum_sha256"],
            sync_status=SyncRecordStatus(r["sync_status"]),
            ground_received_utc=r["ground_received_utc"],
            aggregated=bool(r["aggregated"]),
            attempts=r["attempts"],
            last_error=r["last_error"]
        )
