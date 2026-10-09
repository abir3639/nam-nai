"""Modular Federated Learning Engine for Deep-Space Anomaly Detection.
Simulates onboard edge model training across multiple astronaut nodes,
produces lightweight parameter deltas without transmitting raw health records,
and performs robust, validated Federated Averaging (FedAvg) at Houston Ground Control.
"""

import math
import json
import hashlib
import datetime
from typing import Dict, Any, List, Optional, Tuple
from aegis_deepspace.sync.models import (
    ModelUpdateRecord,
    FederatedGlobalModel,
    SyncRecordStatus
)
from aegis_deepspace.sync.persistence import SyncStore

# Canonical feature keys for the multimodal crew anomaly scoring model
MODEL_FEATURE_KEYS = [
    "w_rad",          # Radiation dose rate sensitivity
    "w_fatigue",      # Vocal acoustic fatigue sensitivity
    "w_strain",       # Cognitive strain sensitivity
    "w_hypoxia",      # Hypoxia / acoustic dyspnea sensitivity
    "w_bone",         # Musculoskeletal bone loss rate sensitivity
    "w_shear",        # Centrifugal Coriolis shear sensitivity
    "bias"            # Calibrated baseline threshold bias
]

# Baseline Global Model Weights (Round 0 / v1.0.0)
DEFAULT_BASELINE_WEIGHTS: Dict[str, float] = {
    "w_rad": 0.42,
    "w_fatigue": 0.28,
    "w_strain": 0.32,
    "w_hypoxia": 0.48,
    "w_bone": 0.22,
    "w_shear": 0.35,
    "bias": -0.45
}


def compute_weights_hash(weights: Dict[str, float]) -> str:
    """Computes SHA-256 integrity hash of serialized model weights."""
    sorted_items = sorted(weights.items())
    serialized = json.dumps(sorted_items, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:24].upper()


class EdgeFederatedClient:
    """Simulates an onboard spacecraft edge client training on local crew biometrics."""

    def __init__(self, client_id: str, astronaut_name: str, base_version: str = "v1.0.0"):
        self.client_id = client_id
        self.astronaut_name = astronaut_name
        self.current_base_version = base_version
        self.local_weights = DEFAULT_BASELINE_WEIGHTS.copy()

    def train_on_local_telemetry(
        self,
        telemetry_samples: List[Dict[str, float]],
        learning_rate: float = 0.05
    ) -> ModelUpdateRecord:
        """Trains local model weights incrementally using local batch gradients.
        Raw biometrics remain onboard; only delta parameters are packed into the update.
        """
        n_samples = max(1, len(telemetry_samples))
        # Compute local gradient steps based on simulated telemetry variance
        grad_accumulator = {k: 0.0 for k in MODEL_FEATURE_KEYS}

        for sample in telemetry_samples:
            # Synthetic linear activation error
            y_pred = (
                self.local_weights["w_rad"] * sample.get("rad_rate", 0.05) +
                self.local_weights["w_fatigue"] * sample.get("fatigue", 0.15) +
                self.local_weights["w_strain"] * sample.get("strain", 0.12) +
                self.local_weights["w_hypoxia"] * sample.get("hypoxia", 0.04) +
                self.local_weights["w_bone"] * sample.get("bone_loss", 0.8) +
                self.local_weights["w_shear"] * sample.get("shear", 0.0) +
                self.local_weights["bias"]
            )
            # Simulated target ground-truth anomaly indicator
            y_true = sample.get("target_anomaly", 0.2)
            error = y_pred - y_true

            # Accumulate gradients
            grad_accumulator["w_rad"] += error * sample.get("rad_rate", 0.05)
            grad_accumulator["w_fatigue"] += error * sample.get("fatigue", 0.15)
            grad_accumulator["w_strain"] += error * sample.get("strain", 0.12)
            grad_accumulator["w_hypoxia"] += error * sample.get("hypoxia", 0.04)
            grad_accumulator["w_bone"] += error * sample.get("bone_loss", 0.8) * 0.1
            grad_accumulator["w_shear"] += error * sample.get("shear", 0.0)
            grad_accumulator["bias"] += error

        # Calculate parameter deltas: delta_W = - lr * grad / N
        weights_delta = {}
        for k in MODEL_FEATURE_KEYS:
            delta = -learning_rate * (grad_accumulator[k] / n_samples)
            # Clamp delta to prevent explosive updates
            delta = max(-0.5, min(0.5, delta))
            weights_delta[k] = round(delta, 5)

        loss = round(sum(abs(g) for g in grad_accumulator.values()) / (n_samples * len(MODEL_FEATURE_KEYS)), 4)
        ts_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
        update_id = f"UPD-FL-{self.client_id}-{datetime.datetime.now(datetime.timezone.utc).strftime('%H%M%S%f')[:9]}"
        checksum = compute_weights_hash(weights_delta)

        return ModelUpdateRecord(
            update_id=update_id,
            client_id=self.client_id,
            base_version=self.current_base_version,
            timestamp_utc=ts_utc,
            num_samples=n_samples,
            loss=loss,
            weights_delta=weights_delta,
            weights_checksum_sha256=checksum,
            sync_status=SyncRecordStatus.PENDING,
            aggregated=False
        )


class GroundFederatedAggregator:
    """Houston Ground Control server component that validates and aggregates federated updates."""

    def __init__(self, store: SyncStore):
        self.store = store
        self._ensure_baseline_model()

    def _ensure_baseline_model(self):
        latest = self.store.get_latest_global_model()
        if not latest:
            init_model = FederatedGlobalModel(
                version="v1.0.0",
                round=0,
                base_version="v0.0.0",
                aggregated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                num_participating_clients=0,
                total_samples_trained=0,
                global_weights=DEFAULT_BASELINE_WEIGHTS.copy(),
                weights_checksum_sha256=compute_weights_hash(DEFAULT_BASELINE_WEIGHTS),
                aggregation_notes="Initial baseline global anomaly model calibrated on ISS historic telemetry."
            )
            self.store.save_global_model(init_model)

    def get_or_create_global_model(self) -> FederatedGlobalModel:
        latest = self.store.get_latest_global_model()
        if not latest:
            self._ensure_baseline_model()
            latest = self.store.get_latest_global_model()
        return latest

    def validate_update(self, update: ModelUpdateRecord) -> Tuple[bool, str]:
        """Validates update format, compatibility, and basic numerical integrity."""
        current_global = self.get_or_create_global_model()

        # 1. Version compatibility check
        # We allow updates trained on the current global model version
        if update.base_version != current_global.version:
            return False, f"Incompatible / stale base version: update trained on {update.base_version}, but current global is {current_global.version}."

        # 2. Check if already aggregated
        if update.aggregated:
            return False, f"Update {update.update_id} has already been aggregated into a global round."

        # 3. Check sample count
        if update.num_samples <= 0:
            return False, "Invalid sample count (must be > 0)."

        # 4. Numerical integrity & feature schema check
        delta = update.weights_delta
        if not isinstance(delta, dict):
            return False, "Malformed weights_delta: expected dictionary."

        for key in MODEL_FEATURE_KEYS:
            if key not in delta:
                return False, f"Missing required feature weight: '{key}'"
            val = delta[key]
            if not isinstance(val, (int, float)):
                return False, f"Weight for '{key}' is not numeric"
            if math.isnan(val) or math.isinf(val):
                return False, f"Numerical instability: '{key}' contains NaN or Inf"
            if abs(val) > 2.0:
                return False, f"Unbounded weight explosion: '{key}' delta {val} exceeds safety ceiling 2.0"

        # 5. Checksum verification
        expected_hash = compute_weights_hash(delta)
        if update.weights_checksum_sha256 != expected_hash:
            return False, f"Checksum verification mismatch: payload hash altered or corrupt."

        return True, "Valid"

    def aggregate_updates(
        self,
        updates: List[ModelUpdateRecord],
        aggregation_notes: Optional[str] = None
    ) -> Tuple[Optional[FederatedGlobalModel], str]:
        """Executes Federated Averaging (FedAvg) on verified client updates.
        Weighted by local training sample count:
            Delta_W_global = sum( (N_k / N_total) * Delta_W_k )
            W_global_new = W_global_old + Delta_W_global
        """
        current_global = self.get_or_create_global_model()
        if not updates:
            return None, "No updates provided for aggregation round."

        # Validate each update
        valid_updates: List[ModelUpdateRecord] = []
        rejected_reasons: List[str] = []
        seen_clients = set()

        for upd in updates:
            # Deduplication: only one update per client per aggregation round
            if upd.client_id in seen_clients:
                rejected_reasons.append(f"Duplicate client {upd.client_id} update in single round rejected.")
                continue

            is_valid, reason = self.validate_update(upd)
            if not is_valid:
                rejected_reasons.append(f"Update {upd.update_id} rejected: {reason}")
                continue

            valid_updates.append(upd)
            seen_clients.add(upd.client_id)

        if not valid_updates:
            return None, f"All updates rejected: {'; '.join(rejected_reasons)}"

        total_samples = sum(u.num_samples for u in valid_updates)
        new_weights = current_global.global_weights.copy()

        # Execute FedAvg
        for feature in MODEL_FEATURE_KEYS:
            weighted_delta = sum(
                (u.num_samples / total_samples) * u.weights_delta[feature]
                for u in valid_updates
            )
            new_weights[feature] = round(new_weights[feature] + weighted_delta, 5)

        new_round = current_global.round + 1
        new_version = f"v1.{new_round}.0"
        aggregated_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        new_checksum = compute_weights_hash(new_weights)

        notes = aggregation_notes or (
            f"Round {new_round} FedAvg completed with {len(valid_updates)} edge clients "
            f"({', '.join(u.client_id for u in valid_updates)}), total samples: {total_samples}."
        )

        new_global_model = FederatedGlobalModel(
            version=new_version,
            round=new_round,
            base_version=current_global.version,
            aggregated_at_utc=aggregated_ts,
            num_participating_clients=len(valid_updates),
            total_samples_trained=current_global.total_samples_trained + total_samples,
            global_weights=new_weights,
            weights_checksum_sha256=new_checksum,
            aggregation_notes=notes
        )

        # Save to store and mark updates as aggregated
        self.store.save_global_model(new_global_model)
        for u in valid_updates:
            self.store.update_model_update_status(
                update_id=u.update_id,
                status=SyncRecordStatus.SYNCED,
                aggregated=True
            )

        self.store.log_activity(
            action="FEDERATED_AGGREGATION",
            status="SUCCESS",
            details=f"New Global Model {new_version} created (Round {new_round}). Participating clients: {len(valid_updates)}."
        )

        return new_global_model, f"Successfully created {new_version} from {len(valid_updates)} client updates."
