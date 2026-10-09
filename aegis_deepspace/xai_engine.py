"""Explainable AI (XAI) Health Alerts Engine Using SHAP (Feature B).
Provides model-specific Shapley attribution quantifying input feature contributions
toward predicted anomaly scores without claiming biological causation.

Supports:
1. Multimodal Crew Anomaly Model (Linear/Additive with Federated Global Weights)
2. Astro-Twin Physiological Deconditioning Residual Model (TreeExplainer with GradientBoostingRegressor)
3. Audit-trail preservation, deterministic efficiency, offline queue compatibility, and caching.
"""

import os
import math
import json
import uuid
import hashlib
import datetime
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field

import numpy as np

# Canonical feature keys for the multimodal crew anomaly scoring model
FEATURE_KEYS = [
    "rad_rate",      # Radiation dose rate (mSv/h)
    "fatigue",       # Vocal acoustic fatigue indicator [0.0 - 1.0]
    "strain",        # Cognitive strain indicator [0.0 - 1.0]
    "hypoxia",       # Vocal hypoxia / dyspnea indicator [0.0 - 1.0]
    "bone_loss",     # Musculoskeletal bone loss rate (%/month)
    "shear"          # Centrifugal Coriolis shear indicator [0.0 - 1.0]
]

# Human-readable feature metadata and standard operational units
FEATURE_METADATA = {
    "rad_rate": {
        "label": "Radiation Dose Rate",
        "unit": "mSv/h",
        "nominal_baseline": 0.02,
        "valid_range": (0.0, 50.0),
        "description": "Galactic cosmic ray and solar energetic particle flux."
    },
    "fatigue": {
        "label": "Vocal Acoustic Fatigue",
        "unit": "index [0.0-1.0]",
        "nominal_baseline": 0.15,
        "valid_range": (0.0, 1.0),
        "description": "Acoustic prosodic slowing and vocal jitter derived from voice log."
    },
    "strain": {
        "label": "Cognitive Strain Indicator",
        "unit": "index [0.0-1.0]",
        "nominal_baseline": 0.12,
        "valid_range": (0.0, 1.0),
        "description": "Neuro-affective sentiment and response latency drift."
    },
    "hypoxia": {
        "label": "Acoustic Hypoxia Marker",
        "unit": "index [0.0-1.0]",
        "nominal_baseline": 0.04,
        "valid_range": (0.0, 1.0),
        "description": "Acoustic spectral perturbation indicating early oxygen desaturation."
    },
    "bone_loss": {
        "label": "Musculoskeletal Bone Loss Rate",
        "unit": "%/mo",
        "nominal_baseline": 0.80,
        "valid_range": (0.0, 10.0),
        "description": "Monthly bone mineral density resorption velocity from Frost Mechanostat."
    },
    "shear": {
        "label": "Coriolis Cross-Coupled Shear",
        "unit": "index [0.0-1.0]",
        "nominal_baseline": 0.00,
        "valid_range": (0.0, 1.0),
        "description": "Angular velocity gradient across artificial gravity centrifuge radius."
    }
}

# Standard operational baseline weights (v1.0.0)
DEFAULT_BASELINE_WEIGHTS = {
    "rad_rate": 0.42,
    "fatigue": 0.28,
    "strain": 0.32,
    "hypoxia": 0.48,
    "bone_loss": 0.22,
    "shear": 0.35,
    "bias": -0.45
}

# Standard scientific disclaimer
DEFAULT_DISCLAIMER = (
    "Operational decision-support prototype. Statistical attribution (SHAP) quantifies mathematical "
    "model feature weighting and does not establish medical causation or clinical diagnosis."
)


class ShapFeatureContribution(BaseModel):
    """Individual feature contribution according to Shapley values."""
    feature_name: str
    feature_label: str
    feature_value: float
    unit: str
    attribution: float = Field(..., description="Shapley value (phi_i)")
    direction: str = Field(..., description="INCREASES_RISK, DECREASES_RISK, or NEUTRAL")
    magnitude: float = Field(..., description="Absolute contribution magnitude |phi_i|")
    rank: int = Field(..., description="1-based rank by magnitude")
    baseline_reference_value: float = Field(..., description="Reference background expectation")


class ShapAlertExplanation(BaseModel):
    """Complete explainability package for an astronaut health alert."""
    explanation_id: str
    alert_id: str
    created_utc: str
    model_name: str
    model_version: str
    model_type: str
    explainer_type: str
    predicted_score: float
    base_value: float = Field(..., description="Expected model value E[f(x)] over reference background")
    efficiency_error: float = Field(..., description="Verification error |f(x) - (E[f(x)] + sum(phi))|")
    severity_category: str
    classification_rule: str
    status: str = Field(default="AVAILABLE", description="AVAILABLE, EXPLANATION_UNAVAILABLE, or CACHED")
    error_message: Optional[str] = None
    contributions: List[ShapFeatureContribution] = Field(default_factory=list)
    top_features_summary: List[str] = Field(default_factory=list)
    plain_language_narrative: str
    limitations_disclaimer: str = Field(default=DEFAULT_DISCLAIMER)


FEATURE_TO_WEIGHT_KEY = {
    "rad_rate": "w_rad",
    "fatigue": "w_fatigue",
    "strain": "w_strain",
    "hypoxia": "w_hypoxia",
    "bone_loss": "w_bone",
    "shear": "w_shear"
}


class MultimodalCrewAnomalyExplainer:
    """Exact Shapley explainer for the Multimodal Crew Anomaly Scoring Model.
    
    For linear/additive models f(x) = sum(w_i * x_i) + bias:
        E[f(x)] = sum(w_i * E[x_i]) + bias
        phi_i = w_i * (x_i - E[x_i])
        sum(phi_i) = f(x) - E[f(x)]
    This satisfies Shapley Efficiency, Symmetry, Linearity, and Null Player properties exactly.
    """

    def __init__(self, model_weights: Optional[Dict[str, float]] = None, model_version: str = "v1.0.0"):
        self.weights = model_weights.copy() if model_weights else DEFAULT_BASELINE_WEIGHTS.copy()
        self.model_version = model_version
        self.model_name = "Multimodal Crew Anomaly Detector"
        self.model_type = "linear_additive_anomaly_score"
        self.explainer_type = "shap.LinearExplainer (Exact Shapley)"

        # Nominal background vector E[x]
        self.nominal_background = {
            k: FEATURE_METADATA[k]["nominal_baseline"] for k in FEATURE_KEYS
        }

    def _get_weight(self, key: str) -> float:
        w_key = FEATURE_TO_WEIGHT_KEY.get(key, f"w_{key}")
        return float(self.weights.get(w_key, self.weights.get(key, 0.0)))

    def update_model(self, model_weights: Dict[str, float], model_version: str):
        """Updates model weights when a new federated model round is aggregated."""
        self.weights = model_weights.copy()
        self.model_version = model_version

    def predict(self, sample: Dict[str, float]) -> float:
        """Computes raw model anomaly score f(x)."""
        score = self.weights.get("bias", -0.45)
        for k in FEATURE_KEYS:
            w = self._get_weight(k)
            x_val = sample.get(k, self.nominal_background[k])
            score += w * x_val
        return max(0.0, min(1.0, float(score)))

    def compute_expected_value(self) -> float:
        """Computes reference background expected value E[f(x)]."""
        base = self.weights.get("bias", -0.45)
        for k in FEATURE_KEYS:
            w = self._get_weight(k)
            base += w * self.nominal_background[k]
        return float(base)

    def explain(self, sample: Dict[str, float], alert_id: Optional[str] = None) -> ShapAlertExplanation:
        """Computes exact Shapley attributions for input sample."""
        explanation_id = f"XAI-{alert_id or uuid.uuid4().hex[:8].upper()}"
        ts_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Sanitize and validate inputs
        sanitized = {}
        for k in FEATURE_KEYS:
            val = sample.get(k)
            if val is None or not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                sanitized[k] = self.nominal_background[k]
            else:
                sanitized[k] = float(val)

        # Raw continuous model output
        raw_pred = self.weights.get("bias", -0.45)
        for k in FEATURE_KEYS:
            w = self._get_weight(k)
            raw_pred += w * sanitized[k]
        predicted_score = round(max(0.0, min(1.0, float(raw_pred))), 4)

        # Expected value over reference background
        base_value = round(self.compute_expected_value(), 4)

        # Compute exact Shapley values: phi_i = w_i * (x_i - E[x_i])
        contributions_raw: List[Dict[str, Any]] = []
        for k in FEATURE_KEYS:
            w = self._get_weight(k)
            x_i = sanitized[k]
            ref_i = self.nominal_background[k]
            phi_i = round(w * (x_i - ref_i), 4)


            direction = "NEUTRAL"
            if phi_i > 0.0001:
                direction = "INCREASES_RISK"
            elif phi_i < -0.0001:
                direction = "DECREASES_RISK"

            meta = FEATURE_METADATA[k]
            contributions_raw.append({
                "feature_name": k,
                "feature_label": meta["label"],
                "feature_value": round(x_i, 3),
                "unit": meta["unit"],
                "attribution": phi_i,
                "direction": direction,
                "magnitude": abs(phi_i),
                "baseline_reference_value": ref_i
            })

        # Rank by magnitude descending
        contributions_raw.sort(key=lambda c: c["magnitude"], reverse=True)
        final_contributions: List[ShapFeatureContribution] = []
        for idx, c in enumerate(contributions_raw, 1):
            c["rank"] = idx
            final_contributions.append(ShapFeatureContribution(**c))

        # Check efficiency property: E[f(x)] + sum(phi) == f(x)
        sum_phi = sum(c.attribution for c in final_contributions)
        efficiency_error = round(abs((base_value + sum_phi) - raw_pred), 4)

        # Map severity category and classification rule
        if predicted_score >= 0.70:
            severity = "CRITICAL"
            rule = "Anomaly Score >= 0.70 (Critical Multi-Signal Anomaly)"
        elif predicted_score >= 0.50:
            severity = "HIGH"
            rule = "Anomaly Score >= 0.50 (High Operational Risk)"
        elif predicted_score >= 0.30:
            severity = "MEDIUM"
            rule = "Anomaly Score >= 0.30 (Elevated Drift from Baseline)"
        else:
            severity = "LOW"
            rule = "Anomaly Score < 0.30 (Nominal Spaceflight Operations)"

        # Generate top features summary
        top_drivers = [c for c in final_contributions if c.direction == "INCREASES_RISK"][:2]
        top_mitigators = [c for c in final_contributions if c.direction == "DECREASES_RISK"][:1]
        
        top_summary = [
            f"{c.feature_label} ({'+' if c.attribution > 0 else ''}{c.attribution:.3f})"
            for c in final_contributions[:3]
        ]

        # Plain language narrative (non-causal)
        if top_drivers:
            driver_phrases = [
                f"{d.feature_label} ({d.feature_value} {d.unit}, +{d.attribution:.3f} model contribution)"
                for d in top_drivers
            ]
            narrative = (
                f"Model anomaly score of {predicted_score:.3f} was driven primarily by "
                f"{' and '.join(driver_phrases)}, elevating the output relative to nominal baseline ({base_value:.3f}). "
                f"Classification threshold: {rule}."
            )
        else:
            narrative = (
                f"Model anomaly score of {predicted_score:.3f} reflects nominal baseline operations "
                f"(expected baseline: {base_value:.3f}). No anomalous feature perturbations detected."
            )

        return ShapAlertExplanation(
            explanation_id=explanation_id,
            alert_id=alert_id or "ALERT-LOCAL",
            created_utc=ts_utc,
            model_name=self.model_name,
            model_version=self.model_version,
            model_type=self.model_type,
            explainer_type=self.explainer_type,
            predicted_score=predicted_score,
            base_value=base_value,
            efficiency_error=efficiency_error,
            severity_category=severity,
            classification_rule=rule,
            status="AVAILABLE",
            contributions=final_contributions,
            top_features_summary=top_summary,
            plain_language_narrative=narrative,
            limitations_disclaimer=DEFAULT_DISCLAIMER
        )


class AstroTwinResidualExplainer:
    """TreeExplainer for Pillar 3 Gradient Boosting deconditioning residual model."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "models", "astro_twin_residual_gbm.joblib")
        )
        self.model = None
        self.explainer = None
        self.model_name = "Astro-Twin Residual Gradient Boosting Model"
        self.model_version = "v1.0.0"
        self.model_type = "gradient_boosting_regressor"
        self.explainer_type = "shap.TreeExplainer"
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                import joblib
                import shap
                self.model = joblib.load(self.model_path)
                self.explainer = shap.TreeExplainer(self.model)
            except Exception as e:
                self.model = None
                self.explainer = None

    def explain(self, sample_features: Dict[str, float], alert_id: Optional[str] = None) -> ShapAlertExplanation:
        explanation_id = f"XAI-TWIN-{alert_id or uuid.uuid4().hex[:8].upper()}"
        ts_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if self.model is None or self.explainer is None:
            return ShapAlertExplanation(
                explanation_id=explanation_id,
                alert_id=alert_id or "ALERT-TWIN",
                created_utc=ts_utc,
                model_name=self.model_name,
                model_version=self.model_version,
                model_type=self.model_type,
                explainer_type=self.explainer_type,
                predicted_score=0.0,
                base_value=0.0,
                efficiency_error=0.0,
                severity_category="UNKNOWN",
                classification_rule="Model file not accessible",
                status="EXPLANATION_UNAVAILABLE",
                error_message="GBM model file or TreeExplainer not available",
                contributions=[],
                top_features_summary=[],
                plain_language_narrative="Explanation unavailable: digital twin residual model is not loaded.",
                limitations_disclaimer=DEFAULT_DISCLAIMER
            )

        feature_names = getattr(self.model, "feature_names_in_", [
            "mission_day", "age", "sex_binary", "body_mass_kg", "baseline_hip_bmd",
            "rolling_ared_7d", "rolling_treadmill_7d", "consecutive_offline_days",
            "dietary_calcium_mg", "vitamin_d_iu", "bisphosphonate_administered"
        ])

        # Prepare vector
        vec = [float(sample_features.get(f, 0.0)) for f in feature_names]
        X = np.array([vec])

        try:
            pred = float(self.model.predict(X)[0])
            expected_val = float(self.explainer.expected_value[0] if isinstance(self.explainer.expected_value, (list, np.ndarray)) else self.explainer.expected_value)
            shap_vals = self.explainer(X).values[0]

            contributions_raw = []
            for name, val, s_val in zip(feature_names, vec, shap_vals):
                s_float = round(float(s_val), 5)
                direction = "INCREASES_RISK" if s_float > 0.0001 else ("DECREASES_RISK" if s_float < -0.0001 else "NEUTRAL")
                contributions_raw.append({
                    "feature_name": name,
                    "feature_label": name.replace("_", " ").title(),
                    "feature_value": round(val, 2),
                    "unit": "units",
                    "attribution": s_float,
                    "direction": direction,
                    "magnitude": abs(s_float),
                    "baseline_reference_value": 0.0
                })

            contributions_raw.sort(key=lambda c: c["magnitude"], reverse=True)
            final_contribs = []
            for i, c in enumerate(contributions_raw, 1):
                c["rank"] = i
                final_contribs.append(ShapFeatureContribution(**c))

            sum_s = sum(c.attribution for c in final_contribs)
            eff_err = round(abs((expected_val + sum_s) - pred), 5)

            top_summary = [f"{c.feature_label} ({'+' if c.attribution > 0 else ''}{c.attribution:.4f})" for c in final_contribs[:3]]

            return ShapAlertExplanation(
                explanation_id=explanation_id,
                alert_id=alert_id or "ALERT-TWIN",
                created_utc=ts_utc,
                model_name=self.model_name,
                model_version=self.model_version,
                model_type=self.model_type,
                explainer_type=self.explainer_type,
                predicted_score=round(pred, 4),
                base_value=round(expected_val, 4),
                efficiency_error=eff_err,
                severity_category="HIGH" if pred > 0.001 else "NOMINAL",
                classification_rule="Deconditioning residual deviation > 0.001 g/cm2",
                status="AVAILABLE",
                contributions=final_contribs,
                top_features_summary=top_summary,
                plain_language_narrative=f"TreeExplainer attributed residual delta of {pred:.4f} to exercise deficits and mission duration.",
                limitations_disclaimer=DEFAULT_DISCLAIMER
            )
        except Exception as err:
            return ShapAlertExplanation(
                explanation_id=explanation_id,
                alert_id=alert_id or "ALERT-TWIN",
                created_utc=ts_utc,
                model_name=self.model_name,
                model_version=self.model_version,
                model_type=self.model_type,
                explainer_type=self.explainer_type,
                predicted_score=0.0,
                base_value=0.0,
                efficiency_error=0.0,
                severity_category="UNKNOWN",
                classification_rule="Explanation computation failed",
                status="EXPLANATION_UNAVAILABLE",
                error_message=str(err),
                contributions=[],
                top_features_summary=[],
                plain_language_narrative="Explanation unavailable due to tree explanation error.",
                limitations_disclaimer=DEFAULT_DISCLAIMER
            )


class XAIEngine:
    """Unified Explainable AI Engine for Aegis-DeepSpace.
    Coordinates explainers, manages caching, and links explanations to health alerts.
    """

    def __init__(self, coordinator=None):
        self.coordinator = coordinator
        self.multimodal_explainer = MultimodalCrewAnomalyExplainer()
        self.twin_explainer = AstroTwinResidualExplainer()
        self._cache: Dict[str, ShapAlertExplanation] = {}

    def _compute_cache_key(self, model_name: str, model_version: str, inputs: Dict[str, Any]) -> str:
        """Constructs an invariant cache key from model version and input vector."""
        items = sorted((str(k), round(float(v), 4) if isinstance(v, (int, float)) else str(v)) for k, v in inputs.items())
        serialized = json.dumps(items, sort_keys=True)
        h = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]
        return f"{model_name}:{model_version}:{h}"

    def explain_crew_anomaly(
        self,
        features: Dict[str, float],
        model_version: Optional[str] = None,
        alert_id: Optional[str] = None,
        use_cache: bool = True
    ) -> ShapAlertExplanation:
        """Explains multimodal crew anomaly scoring prediction."""
        # Get active model weights from coordinator if available
        active_version = model_version or "v1.0.0"
        if self.coordinator and hasattr(self.coordinator, "aggregator"):
            try:
                global_model = self.coordinator.aggregator.get_or_create_global_model()
                active_version = model_version or global_model.version
                self.multimodal_explainer.update_model(global_model.global_weights, active_version)
            except Exception:
                pass

        cache_key = self._compute_cache_key(
            self.multimodal_explainer.model_name,
            active_version,
            features
        )

        if use_cache and cache_key in self._cache:
            cached = self._cache[cache_key].model_copy(deep=True) if hasattr(self._cache[cache_key], "model_copy") else self._cache[cache_key].copy(deep=True)
            cached.status = "CACHED"
            if alert_id:
                cached.alert_id = alert_id
            return cached

        try:
            explanation = self.multimodal_explainer.explain(features, alert_id=alert_id)
            if use_cache and explanation.status == "AVAILABLE":
                self._cache[cache_key] = explanation
            return explanation
        except Exception as exc:
            # Fallback gracefully without crashing monitoring pipeline
            return ShapAlertExplanation(
                explanation_id=f"XAI-ERR-{uuid.uuid4().hex[:8].upper()}",
                alert_id=alert_id or "ALERT-UNKNOWN",
                created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                model_name=self.multimodal_explainer.model_name,
                model_version=active_version,
                model_type=self.multimodal_explainer.model_type,
                explainer_type=self.multimodal_explainer.explainer_type,
                predicted_score=0.0,
                base_value=0.0,
                efficiency_error=0.0,
                severity_category="UNKNOWN",
                classification_rule="Explanation failed",
                status="EXPLANATION_UNAVAILABLE",
                error_message=str(exc),
                contributions=[],
                top_features_summary=[],
                plain_language_narrative="Explanation generation encountered an unhandled exception.",
                limitations_disclaimer=DEFAULT_DISCLAIMER
            )

    def extract_features_from_state(self, crew_state: Any) -> Dict[str, float]:
        """Extracts canonical multimodal feature vector from normalized CrewState."""
        rad = getattr(crew_state, "radiation", None)
        voice = getattr(crew_state, "voice_vitals", None)
        twin = getattr(crew_state, "astro_twin", None)

        return {
            "rad_rate": float(getattr(rad, "dose_rate_msv_h", 0.02) if rad else 0.02),
            "fatigue": float(getattr(voice, "fatigue_score", 0.15) if voice else 0.15),
            "strain": float(getattr(voice, "cognitive_strain_score", 0.12) if voice else 0.12),
            "hypoxia": float(getattr(voice, "hypoxia_indicator", 0.04) if voice else 0.04),
            "bone_loss": float(getattr(twin, "projected_bone_loss_pct_mo", 0.80) if twin else 0.80),
            "shear": 0.0
        }

    def explain_health_event(self, event: Any, crew_state: Optional[Any] = None) -> ShapAlertExplanation:
        """Explains a HealthEventRecord using its attached payload or provided CrewState."""
        features: Dict[str, float] = {}

        # 1. Try extracting from crew_state
        if crew_state:
            features = self.extract_features_from_state(crew_state)
        # 2. Try extracting from event payload
        elif hasattr(event, "payload") and isinstance(event.payload, dict):
            p = event.payload
            features = {
                "rad_rate": float(p.get("dose_rate_msv_h", 0.02)),
                "fatigue": float(p.get("fatigue_score", 0.15)),
                "strain": float(p.get("cognitive_strain", 0.12)),
                "hypoxia": float(p.get("hypoxia_indicator", 0.04)),
                "bone_loss": float(p.get("bone_loss_pct_mo", 0.80)),
                "shear": float(p.get("shear", 0.0))
            }
        else:
            features = {k: FEATURE_METADATA[k]["nominal_baseline"] for k in FEATURE_KEYS}

        event_id = getattr(event, "event_id", "EVT-UNKNOWN")
        return self.explain_crew_anomaly(features, alert_id=event_id)


# Global default instance
default_xai_engine = XAIEngine()
