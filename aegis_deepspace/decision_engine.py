"""Autonomous Decision Engine (Pillar 4 MVP) for Aegis-DeepSpace.
Synthesizes environmental radiation risks, passive voice biometrics, and Astro-Twin physiological simulations
into explainable clinical decision support with offline independence.
"""

import uuid
import datetime
from typing import List, Tuple, Dict, Any

from aegis_deepspace.models import (
    CrewState,
    DecisionObject,
    RiskLevel,
    CommsMode,
    ContributingFactor,
    EvidenceCitation,
    PillarContribution,
    RiskFusionBreakdown,
    DecisionTrace,
    TraceSignal,
    TraceSynergyRule
)
from aegis_deepspace.knowledge_base import retrieve_relevant_evidence


class AutonomousDecisionEngine:
    """Core Pillar 4 Decision Engine implementation."""

    def __init__(self):
        # Configurable risk thresholds
        self.radiation_critical_dose_rate = 0.5  # mSv/h
        self.radiation_high_dose_rate = 0.1      # mSv/h
        self.radiation_medium_dose_rate = 0.05   # mSv/h

        self.voice_critical_strain = 0.75
        self.voice_high_strain = 0.50
        self.voice_medium_strain = 0.35
        self.voice_hypoxia_threshold = 0.40

        self.twin_critical_deficit_days = 4
        self.twin_high_deficit_days = 2
        self.twin_bone_loss_warning_pct = 1.2

    def process(self, crew_state: CrewState) -> DecisionObject:
        """Processes normalized CrewState and generates an explainable DecisionObject."""
        decision_id = f"DEC-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # 1. Evaluate individual pillar signals
        rad = crew_state.radiation
        voice = crew_state.voice_vitals
        twin = crew_state.astro_twin
        
        reasons: List[str] = []
        contributing_factors: List[ContributingFactor] = []
        uncertainties: List[str] = []
        
        # Signal anomaly flags
        rad_anomaly = False
        voice_anomaly = False
        hypoxia_anomaly = False
        twin_anomaly = False
        
        # Track numerical contributions per pillar
        baseline_score = 0.10
        p1_score = 0.0
        p1_status = "NOMINAL"
        p1_detail = f"Dose rate {rad.dose_rate_msv_h:.2f} mSv/h within background levels"

        p2_score = 0.0
        p2_status = "NOMINAL"
        p2_detail = f"Acoustic markers within baseline limits (+{voice.deviation_from_baseline_z:.1f}σ)"

        p3_score = 0.0
        p3_status = "NOMINAL"
        p3_detail = f"Simulation model projects stable musculoskeletal state"

        synergy_score = 0.0
        synergy_details = []

        # --- Evaluate Radiation Safe-Route (Pillar 1) ---
        if rad.spe_active or rad.dose_rate_msv_h >= self.radiation_critical_dose_rate or rad.risk_level == "CRITICAL":
            rad_anomaly = True
            p1_score = 0.45
            p1_status = "CRITICAL SPE"
            p1_detail = f"Severe SPE active ({rad.dose_rate_msv_h:.2f} mSv/h in {rad.current_module})"
            reasons.append(f"Severe Solar Particle Event active (Dose rate: {rad.dose_rate_msv_h:.2f} mSv/h). Current shielding ({rad.shielding_rating_g_cm2:.1f} g/cm²) insufficient.")
            contributing_factors.append(ContributingFactor(
                pillar="Radiation Safe-Route",
                factor="Critical SPE / High Dose Rate",
                severity_contribution="CRITICAL",
                detail=f"{rad.dose_rate_msv_h:.2f} mSv/h in {rad.current_module}"
            ))
        elif rad.dose_rate_msv_h >= self.radiation_high_dose_rate or rad.risk_level in ["HIGH", "ELEVATED"]:
            rad_anomaly = True
            p1_score = 0.30
            p1_status = "ELEVATED"
            p1_detail = f"Elevated dose rate ({rad.dose_rate_msv_h:.2f} mSv/h)"
            reasons.append(f"Elevated solar radiation detected ({rad.dose_rate_msv_h:.2f} mSv/h).")
            contributing_factors.append(ContributingFactor(
                pillar="Radiation Safe-Route",
                factor="Elevated Radiation Flux",
                severity_contribution="HIGH",
                detail=f"{rad.dose_rate_msv_h:.2f} mSv/h"
            ))
        elif rad.dose_rate_msv_h >= self.radiation_medium_dose_rate or rad.risk_level == "MEDIUM":
            p1_score = 0.15
            p1_status = "MODERATE"
            p1_detail = f"Moderate flux above baseline ({rad.dose_rate_msv_h:.2f} mSv/h)"
            reasons.append(f"Moderate radiation flux above baseline ({rad.dose_rate_msv_h:.2f} mSv/h).")
            contributing_factors.append(ContributingFactor(
                pillar="Radiation Safe-Route",
                factor="Moderate Ambient Dose Rate",
                severity_contribution="MODERATE",
                detail=f"{rad.dose_rate_msv_h:.2f} mSv/h"
            ))

        # --- Evaluate Voice Vitals (Pillar 2) ---
        if voice.hypoxia_indicator >= self.voice_hypoxia_threshold:
            hypoxia_anomaly = True
            voice_anomaly = True
            p2_score += 0.35
            p2_status = "HYPOXIA RISK"
            p2_detail = f"Vocal dyspnea/hypoxia index {voice.hypoxia_indicator:.2f}"
            reasons.append(f"Acoustic markers indicate possible early hypoxia or respiratory fatigue (Index: {voice.hypoxia_indicator:.2f}).")
            contributing_factors.append(ContributingFactor(
                pillar="Voice Vitals",
                factor="Possible Early Hypoxia Indicator",
                severity_contribution="HIGH",
                detail=f"Hypoxia score {voice.hypoxia_indicator:.2f}"
            ))

        if voice.cognitive_strain_score >= self.voice_high_strain or voice.fatigue_score >= self.voice_high_strain or voice.deviation_from_baseline_z >= 2.0:
            voice_anomaly = True
            p2_score += 0.25
            if p2_status == "NOMINAL":
                p2_status = "HIGH STRAIN"
                p2_detail = f"Cognitive strain {voice.cognitive_strain_score:.2f}, Fatigue {voice.fatigue_score:.2f} (+{voice.deviation_from_baseline_z:.1f}σ)"
            else:
                p2_detail += f"; Cognitive strain {voice.cognitive_strain_score:.2f}"
            reasons.append(f"Significant cognitive strain ({voice.cognitive_strain_score:.2f}) and fatigue ({voice.fatigue_score:.2f}) above personal baseline (+{voice.deviation_from_baseline_z:.1f}σ).")
            contributing_factors.append(ContributingFactor(
                pillar="Voice Vitals",
                factor="Cognitive Strain / Fatigue Spike",
                severity_contribution="HIGH",
                detail=f"Strain {voice.cognitive_strain_score:.2f}, Fatigue {voice.fatigue_score:.2f}"
            ))
        elif voice.cognitive_strain_score >= self.voice_medium_strain or voice.fatigue_score >= self.voice_medium_strain or voice.deviation_from_baseline_z >= 1.2:
            voice_anomaly = True
            p2_score += 0.15
            if p2_status == "NOMINAL":
                p2_status = "MODERATE STRAIN"
                p2_detail = f"Vocal deviation +{voice.deviation_from_baseline_z:.1f}σ vs baseline"
            reasons.append(f"Moderate vocal strain and fatigue detected (+{voice.deviation_from_baseline_z:.1f}σ vs baseline).")
            contributing_factors.append(ContributingFactor(
                pillar="Voice Vitals",
                factor="Subclinical Fatigue Deviation",
                severity_contribution="MODERATE",
                detail=f"+{voice.deviation_from_baseline_z:.1f}σ deviation"
            ))

        # --- Evaluate Astro-Twin (Pillar 3) ---
        if twin.exercise_deficit_days >= self.twin_critical_deficit_days or twin.projected_bone_loss_pct_mo >= 2.0:
            twin_anomaly = True
            p3_score = 0.30
            p3_status = "SEVERE DEFICIT"
            p3_detail = f"{twin.exercise_deficit_days}d exercise deficit, {twin.projected_bone_loss_pct_mo:.1f}% BMD/mo"
            reasons.append(f"Astro-Twin forward simulation projects accelerated deconditioning: {twin.exercise_deficit_days} days exercise deficit (Projected bone loss: {twin.projected_bone_loss_pct_mo:.1f}%/mo).")
            contributing_factors.append(ContributingFactor(
                pillar="Astro-Twin",
                factor="Severe Exercise Deficit / Bone Loss",
                severity_contribution="HIGH",
                detail=f"{twin.exercise_deficit_days} days deficit, {twin.projected_bone_loss_pct_mo:.1f}% BMD/mo"
            ))
        elif twin.exercise_deficit_days >= self.twin_high_deficit_days or twin.projected_bone_loss_pct_mo >= self.twin_bone_loss_warning_pct:
            twin_anomaly = True
            p3_score = 0.20
            p3_status = "MODERATE DEFICIT"
            p3_detail = f"{twin.exercise_deficit_days}d deficit, {twin.projected_bone_loss_pct_mo:.1f}% BMD/mo"
            reasons.append(f"Astro-Twin simulation flags impending musculoskeletal deconditioning ({twin.exercise_deficit_days} days deficit, {twin.projected_bone_loss_pct_mo:.1f}% BMD/mo).")
            contributing_factors.append(ContributingFactor(
                pillar="Astro-Twin",
                factor="Simulated Musculoskeletal Deficit",
                severity_contribution="MODERATE",
                detail=f"{twin.exercise_deficit_days} days exercise deficit"
            ))

        # --- Multi-Signal Synergy & Escalation ---
        active_anomaly_count = sum([1 for flag in [rad_anomaly, voice_anomaly, twin_anomaly] if flag])
        
        if active_anomaly_count >= 3:
            synergy_score += 0.20
            synergy_details.append("3 independent pillars coincident")
            reasons.append("MULTIMODAL ESCALATION: 3 independent systems confirm simultaneous operational & physiological risk.")
        elif active_anomaly_count == 2:
            synergy_score += 0.10
            synergy_details.append("2 coincident anomalies")
            reasons.append("SYNERGY ESCALATION: Coincident environmental and crew biometric anomalies detected.")

        if hypoxia_anomaly and voice.cognitive_strain_score >= self.voice_medium_strain:
            synergy_score += 0.10
            synergy_details.append("Hypoxia-cognitive correlation")
            reasons.append("ATMOSPHERIC CORRELATION: Hypoxia indicator correlates with cognitive slowing.")

        # --- Downstream Astro-Twin Feedback Loop Check ---
        if rad_anomaly and twin.exercise_deficit_days > 0:
            reasons.append("FEEDBACK LOOP: Radiation shelter restriction is driving simulated exercise deficits in Astro-Twin.")

        # Total calculated raw risk score
        raw_risk_score = baseline_score + p1_score + p2_score + p3_score + synergy_score

        # --- Data Freshness & Uncertainty Checks ---
        if crew_state.data_freshness_seconds > 300:
            uncertainties.append(f"Telemetry stream is stale ({crew_state.data_freshness_seconds}s old). Confidence reduced.")
            
        avg_confidence = (rad.confidence + voice.confidence + twin.confidence) / 3.0
        
        if rad.confidence < 0.60:
            uncertainties.append("Radiation sensor telemetry has low confidence; possible sensor degradation.")
        if voice.confidence < 0.60:
            uncertainties.append("Voice log audio quality has low SNR; acoustic metrics have higher variance.")
        if twin.confidence < 0.60:
            uncertainties.append("Astro-Twin physiological model projection has widened confidence intervals.")

        if crew_state.comms_mode == CommsMode.OFFLINE:
            reasons.append("COMMUNICATION BLACKOUT: Operating autonomously on habitat edge server without Earth Houston uplink.")

        # Cap score between 0.05 and 0.99
        final_risk_score = min(max(raw_risk_score, 0.05), 0.99)

        # 2. Map risk score to RiskLevel
        if final_risk_score >= 0.75:
            risk_level = RiskLevel.CRITICAL
        elif final_risk_score >= 0.50:
            risk_level = RiskLevel.HIGH
        elif final_risk_score >= 0.30:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        # 3. If uncertainty is high or confidence is very low, adjust posture
        if avg_confidence < 0.60:
            if risk_level == RiskLevel.CRITICAL and not rad.spe_active:
                risk_level = RiskLevel.HIGH
            uncertainties.append("Overall confidence is below 60%. Requesting additional confirmatory observations.")

        # 4. Formulate Explainable Recommendations
        rec_action, alt_action = self._determine_recommendation(
            risk_level=risk_level,
            rad=rad,
            voice=voice,
            twin=twin,
            rad_anomaly=rad_anomaly,
            voice_anomaly=voice_anomaly,
            hypoxia_anomaly=hypoxia_anomaly,
            twin_anomaly=twin_anomaly,
            avg_confidence=avg_confidence
        )

        if not reasons:
            reasons.append("All environmental, biometric, and physiological digital twin metrics remain within nominal operational boundaries.")

        # 5. Retrieve NASA Evidence citations locally
        evidence = retrieve_relevant_evidence(
            radiation_flag=rad_anomaly,
            voice_flag=voice_anomaly,
            hypoxia_flag=hypoxia_anomaly,
            astro_flag=twin_anomaly,
            comms_offline=(crew_state.comms_mode == CommsMode.OFFLINE)
        )

        # 6. Build the Risk Fusion Mathematical Trace
        formula_parts = [f"{baseline_score:.2f} (Base)"]
        if p1_score > 0:
            formula_parts.append(f"{p1_score:.2f} (P1 Rad)")
        if p2_score > 0:
            formula_parts.append(f"{p2_score:.2f} (P2 Voice)")
        if p3_score > 0:
            formula_parts.append(f"{p3_score:.2f} (P3 Twin)")
        if synergy_score > 0:
            formula_parts.append(f"{synergy_score:.2f} (Synergy)")
        formula_str = " + ".join(formula_parts) + f" = {final_risk_score:.2f}"

        risk_fusion_breakdown = RiskFusionBreakdown(
            baseline_score=baseline_score,
            p1_radiation=PillarContribution(
                pillar_id="P1",
                name="Radiation Safe-Route",
                status=p1_status,
                score_addition=round(p1_score, 2),
                detail=p1_detail
            ),
            p2_voice_vitals=PillarContribution(
                pillar_id="P2",
                name="Voice Vitals",
                status=p2_status,
                score_addition=round(p2_score, 2),
                detail=p2_detail
            ),
            p3_astro_twin=PillarContribution(
                pillar_id="P3",
                name="Astro-Twin",
                status=p3_status,
                score_addition=round(p3_score, 2),
                detail=p3_detail
            ),
            synergy_score=round(synergy_score, 2),
            synergy_detail="; ".join(synergy_details) if synergy_details else None,
            final_score=round(final_risk_score, 2),
            formula=formula_str
        )

        # 7. Build the Structured Decision Trace (Explain Decision)
        trace_signals: List[TraceSignal] = [
            TraceSignal(
                source="P1",
                name="Radiation Safe-Route",
                metric="Ambient Dose Rate & SPE Status",
                value=f"{rad.dose_rate_msv_h:.2f} mSv/h ({'SPE ACTIVE' if rad.spe_active else 'NOMINAL GCR'}) in {rad.current_module}",
                threshold=f"Critical >= {self.radiation_critical_dose_rate:.2f} mSv/h, High >= {self.radiation_high_dose_rate:.2f} mSv/h",
                contribution=round(p1_score, 2),
                triggered=rad_anomaly or p1_score > 0,
                explanation=p1_detail
            ),
            TraceSignal(
                source="P2",
                name="Voice Vitals",
                metric="Fatigue, Cognitive Strain & Hypoxia Index",
                value=f"Strain: {voice.cognitive_strain_score:.2f}, Fatigue: {voice.fatigue_score:.2f}, Hypoxia: {voice.hypoxia_indicator:.2f} (+{voice.deviation_from_baseline_z:.1f}σ)",
                threshold=f"Hypoxia >= {self.voice_hypoxia_threshold:.2f}, High Strain >= {self.voice_high_strain:.2f}, Drift >= +2.0σ",
                contribution=round(p2_score, 2),
                triggered=voice_anomaly or p2_score > 0,
                explanation=p2_detail
            ),
            TraceSignal(
                source="P3",
                name="Astro-Twin [SIMULATED]",
                metric="Exercise Deficit & Bone Mineral Density Loss",
                value=f"{twin.exercise_deficit_days} missed exercise days, -{twin.projected_bone_loss_pct_mo:.1f}% BMD/mo",
                threshold=f"Critical Deficit >= {self.twin_critical_deficit_days}d, Warning >= {self.twin_high_deficit_days}d or Loss > {self.twin_bone_loss_warning_pct:.1f}%/mo",
                contribution=round(p3_score, 2),
                triggered=twin_anomaly or p3_score > 0,
                explanation=p3_detail
            )
        ]

        trace_synergy_rules: List[TraceSynergyRule] = [
            TraceSynergyRule(
                name="Multi-Pillar Concordance Escalation",
                triggered=active_anomaly_count >= 2,
                contribution=round(0.20 if active_anomaly_count >= 3 else (0.10 if active_anomaly_count == 2 else 0.0), 2),
                explanation=f"{active_anomaly_count} independent pillars detected concurrent anomalies." if active_anomaly_count >= 2 else "No coincident multi-pillar trigger threshold reached."
            ),
            TraceSynergyRule(
                name="Hypoxia-Cognitive Impairment Coupling",
                triggered=hypoxia_anomaly and voice.cognitive_strain_score >= self.voice_medium_strain,
                contribution=round(0.10 if (hypoxia_anomaly and voice.cognitive_strain_score >= self.voice_medium_strain) else 0.0, 2),
                explanation="Acoustic hypoxia biomarker coincides with psychomotor cognitive slowing." if (hypoxia_anomaly and voice.cognitive_strain_score >= self.voice_medium_strain) else "No hypoxia-cognitive coupling detected."
            )
        ]

        decision_trace = DecisionTrace(
            base_risk=baseline_score,
            signals=trace_signals,
            synergy_rules=trace_synergy_rules,
            final_risk=round(final_risk_score, 2),
            final_level=risk_level
        )

        return DecisionObject(
            decision_id=decision_id,
            timestamp=timestamp,
            mode=crew_state.comms_mode,
            risk_level=risk_level,
            risk_score=round(final_risk_score, 2),
            risk_fusion=risk_fusion_breakdown,
            decision_trace=decision_trace,
            reasons=reasons,
            contributing_factors=contributing_factors,
            recommended_action=rec_action,
            alternative_action=alt_action,
            evidence=evidence,
            confidence=round(avg_confidence, 2),
            uncertainty=uncertainties,
            raw_crew_state=crew_state
        )

    def _determine_recommendation(
        self,
        risk_level: RiskLevel,
        rad,
        voice,
        twin,
        rad_anomaly: bool,
        voice_anomaly: bool,
        hypoxia_anomaly: bool,
        twin_anomaly: bool,
        avg_confidence: float
    ) -> Tuple[str, str]:
        """Formulates deterministic clinical decision support recommendations."""
        if avg_confidence < 0.60 and not rad.spe_active:
            return (
                "REQUEST CONFIRMATORY TELEMETRY: Re-record 30s voice check-in and re-verify environmental sensors before taking further action.",
                "Maintain current duty rotation while initiating passive cabin sensor diagnostics."
            )

        if rad_anomaly and (voice_anomaly or twin_anomaly):
            return (
                f"IMMEDIATE ACTION: Relocate crew from {rad.current_module} to {rad.recommended_safe_module} (>35 g/cm² shielding). Re-schedule high-demand cognitive tasks and initiate post-shelter countermeasure routine in Astro-Twin.",
                "If relocation delayed, don personal water-garment shielding and reduce cabin workload immediately."
            )

        if rad_anomaly:
            return (
                f"MOVE TO SHELTER: Guide crew to {rad.recommended_safe_module}. Solar event flux exceeds safe threshold for {rad.current_module}.",
                f"Verify hatch closures and monitor habitat module dosimeter telemetry."
            )

        if hypoxia_anomaly:
            return (
                "CABIN ATMOSPHERE PROTOCOL: Check Environmental Control & Life Support (ECLSS) ppO2/ppCO2 in crew quarters. Administer 10-minute supplemental normobaric oxygen if dyspnea persists.",
                "Relocate crew member to high-ventilation central hub module and perform pulse oximetry test."
            )

        if voice_anomaly:
            return (
                "FATIGUE MITIGATION: Stand down crew member from critical robotics / EVA operations. Prescribe mandatory 60-minute rest period and acoustic re-evaluation.",
                "Conduct brief psychomotor vigilance check if operational requirements mandate duty continuation."
            )

        if twin_anomaly:
            return (
                f"COUNTERMEASURE ADJUSTMENT: Astro-Twin projects {twin.exercise_deficit_days}-day cumulative deficit. Increase resistive ARED cycle loading by 15% and schedule high-intensity aerobic session.",
                "Split daily countermeasure protocol into two 45-minute interval sessions."
            )

        return (
            "CONTINUE NOMINAL OPERATIONS: All vital metrics nominal. Maintain routine 24-hour passive monitoring cycle.",
            "No corrective action recommended."
        )
