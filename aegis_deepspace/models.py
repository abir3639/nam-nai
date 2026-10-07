"""Data models and schemas for Aegis-DeepSpace Pillar 4 (Autonomous Decision Engine).
Standardizes inputs from Pillars 1-3 into a unified CrewState and defines the structured DecisionObject.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import datetime


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CommsMode(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class RadiationState(BaseModel):
    """Pillar 1: Environmental Defense - Radiation Safe-Route output."""
    risk_level: str = Field(default="LOW", description="Radiation hazard rating (LOW, MEDIUM, HIGH, CRITICAL)")
    dose_rate_msv_h: float = Field(default=0.02, description="Current or predicted dose rate in mSv/h")
    cumulative_dose_msv: float = Field(default=1.4, description="Accumulated mission dose in mSv")
    spe_active: bool = Field(default=False, description="Whether a Solar Particle Event / CME is active or incoming")
    current_module: str = Field(default="Gym / Exercise Bay", description="Current location of the crew member")
    recommended_safe_module: str = Field(default="Storm Shelter (Water Wall)", description="Topologically optimal safe module")
    shielding_rating_g_cm2: float = Field(default=10.0, description="Shielding mass density of current module")
    confidence: float = Field(default=0.95, ge=0.0, le=1.0)


class VoiceVitalsState(BaseModel):
    """Pillar 2: Passive Biometrics - Voice Vitals output."""
    fatigue_score: float = Field(default=0.15, ge=0.0, le=1.0, description="Acoustic fatigue indicator (0=rested, 1=exhausted)")
    cognitive_strain_score: float = Field(default=0.12, ge=0.0, le=1.0, description="Neuro-affective cognitive strain indicator (0=normal, 1=impaired)")
    hypoxia_indicator: float = Field(default=0.05, ge=0.0, le=1.0, description="Vocal acoustic marker for early hypoxia / dyspnea")
    deviation_from_baseline_z: float = Field(default=0.4, description="Standard deviations away from personalized baseline")
    confidence: float = Field(default=0.90, ge=0.0, le=1.0)


class AstroTwinState(BaseModel):
    """Pillar 3: Predictive Twin - Astro-Twin output."""
    projected_bone_loss_pct_mo: float = Field(default=1.0, description="Projected monthly bone mineral density loss rate (%)")
    projected_muscle_atrophy_pct: float = Field(default=2.0, description="Projected muscle volume decline (%) over horizon")
    exercise_deficit_days: int = Field(default=0, description="Consecutive simulated days without resistive/aerobic exercise")
    countermeasure_status: str = Field(default="NOMINAL", description="Status of physical countermeasure plan")
    prediction_horizon_days: int = Field(default=14, description="Simulation projection window in days")
    confidence: float = Field(default=0.88, ge=0.0, le=1.0)


class CrewState(BaseModel):
    """Layer 2 Normalized Crew State integrating Pillars 1, 2, and 3."""
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    comms_mode: CommsMode = Field(default=CommsMode.ONLINE, description="Earth communication link status (ONLINE or OFFLINE)")
    data_freshness_seconds: int = Field(default=5, description="Age of most recent telemetry stream in seconds")
    radiation: RadiationState = Field(default_factory=RadiationState)
    voice_vitals: VoiceVitalsState = Field(default_factory=VoiceVitalsState)
    astro_twin: AstroTwinState = Field(default_factory=AstroTwinState)


class ContributingFactor(BaseModel):
    """Transparent factor contributing to the fused risk state."""
    pillar: str = Field(..., description="Pillar source: Radiation Safe-Route, Voice Vitals, or Astro-Twin")
    factor: str = Field(..., description="Description of the observation")
    severity_contribution: str = Field(..., description="Impact: LOW, MODERATE, HIGH, CRITICAL")
    detail: str = Field(..., description="Numerical metric or trigger context")


class EvidenceCitation(BaseModel):
    """Document evidence supporting decision co-pilot recommendations."""
    source: str = Field(..., description="NASA repository source (e.g., NASA HRR, NTRS, LSDA)")
    title: str = Field(..., description="Title of scientific research or technical standard")
    citation: str = Field(..., description="Authors, Year, or Document identifier")
    excerpt: str = Field(..., description="Relevant clinical or operational excerpt")
    reference_url: Optional[str] = None


class PillarContribution(BaseModel):
    """Numerical contribution of a single pillar to the fused risk score."""
    pillar_id: str = Field(..., description="P1, P2, or P3")
    name: str = Field(..., description="Full pillar name")
    status: str = Field(..., description="Current status/state: NOMINAL, MODERATE, ELEVATED, CRITICAL")
    score_addition: float = Field(..., description="Direct points added to risk score")
    detail: str = Field(..., description="Summary explanation of the contribution")


class RiskFusionBreakdown(BaseModel):
    """Transparent mathematical trace of the multimodal risk fusion calculation."""
    baseline_score: float = Field(default=0.10, description="Nominal background baseline score")
    p1_radiation: PillarContribution
    p2_voice_vitals: PillarContribution
    p3_astro_twin: PillarContribution
    synergy_score: float = Field(default=0.0, description="Additional multi-signal escalation penalty")
    synergy_detail: Optional[str] = Field(None, description="Explanation of multi-signal synergy if active")
    final_score: float = Field(..., description="Total fused score (min 0.05, max 0.99)")
    formula: str = Field(..., description="Readable formula string, e.g., 0.10 + 0.45 + 0.00 + 0.00 = 0.55")


class TraceSignal(BaseModel):
    """Detailed signal trace component in DecisionTrace."""
    source: str = Field(..., description="Pillar source: P1, P2, P3")
    name: str = Field(..., description="Signal name")
    metric: str = Field(..., description="Metric description, e.g. Dose rate, Cognitive strain")
    value: str = Field(..., description="Observed value formatted as string with units")
    threshold: str = Field(..., description="Evaluation threshold condition")
    contribution: float = Field(..., description="Score addition to risk score")
    triggered: bool = Field(..., description="Whether threshold condition was triggered")
    explanation: str = Field(..., description="Deterministic rationale for contribution")


class TraceSynergyRule(BaseModel):
    """Multi-signal escalation rule in DecisionTrace."""
    name: str = Field(..., description="Synergy rule name")
    triggered: bool = Field(..., description="Whether synergy condition was triggered")
    contribution: float = Field(..., description="Score addition")
    explanation: str = Field(..., description="Explanation of multi-signal escalation")


class DecisionTrace(BaseModel):
    """Transparent deterministic breakdown of decision engine input thresholds and contributions."""
    base_risk: float = Field(default=0.10, description="Nominal background baseline risk score")
    signals: List[TraceSignal] = Field(default_factory=list)
    synergy_rules: List[TraceSynergyRule] = Field(default_factory=list)
    final_risk: float = Field(..., description="Composite risk score [0.05, 0.99]")
    final_level: RiskLevel = Field(..., description="Mapped categorical risk level")


class DecisionObject(BaseModel):
    """Structured decision output produced by Pillar 4."""
    decision_id: str
    timestamp: str
    mode: CommsMode
    risk_level: RiskLevel
    risk_score: float = Field(ge=0.0, le=1.0, description="Normalized composite risk score")
    
    # Mathematical fusion trace
    risk_fusion: Optional[RiskFusionBreakdown] = None
    
    # Structured Decision Trace for Explain Decision panel
    decision_trace: Optional[DecisionTrace] = None
    
    # Explainability elements
    reasons: List[str] = Field(default_factory=list, description="Bulleted explainable justifications")
    contributing_factors: List[ContributingFactor] = Field(default_factory=list)
    recommended_action: str = Field(..., description="Primary clinical/operational decision support recommendation")
    alternative_action: Optional[str] = Field(None, description="Contingency or alternative approach")
    
    # Evidence & Rigor
    evidence: List[EvidenceCitation] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, description="System confidence in this synthesis")
    uncertainty: List[str] = Field(default_factory=list, description="Exposed caveats, missing data, or signal noise")
    
    # Input snapshot
    raw_crew_state: CrewState
    
    # Disclaimer
    disclaimer: str = Field(
        default="RESEARCH/HACKATHON PROTOTYPE ONLY - Clinical decision support advisory, not an autonomous medical device or autonomous authority."
    )
