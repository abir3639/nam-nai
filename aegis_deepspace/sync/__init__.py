"""Aegis-DeepSpace: Asymmetric Federated Sync with Houston Ground Control.
Provides offline store-and-forward telemetry and lightweight federated learning aggregation
under interplanetary communication latencies and blackouts.
"""

from aegis_deepspace.sync.models import (
    SyncState,
    SyncRecordStatus,
    RecordType,
    HealthEventRecord,
    TelemetrySummaryRecord,
    ModelUpdateRecord,
    FederatedGlobalModel,
    SyncActivityLog
)

__all__ = [
    "SyncState",
    "SyncRecordStatus",
    "RecordType",
    "HealthEventRecord",
    "TelemetrySummaryRecord",
    "ModelUpdateRecord",
    "FederatedGlobalModel",
    "SyncActivityLog"
]
