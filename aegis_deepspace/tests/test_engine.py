"""Automated tests for Aegis-DeepSpace Pillar 4 Autonomous Decision Engine."""

import pytest
from aegis_deepspace.models import (
    CrewState,
    RadiationState,
    VoiceVitalsState,
    AstroTwinState,
    RiskLevel,
    CommsMode
)
from aegis_deepspace.decision_engine import AutonomousDecisionEngine
from aegis_deepspace.scenarios import (
    get_scenario_normal,
    get_scenario_solar_storm,
    get_scenario_voice_anomaly,
    get_scenario_combined_anomaly,
    get_scenario_offline_blackout,
    get_scenario_uncertain_data
)


@pytest.fixture
def engine():
    return AutonomousDecisionEngine()


def test_scenario_normal(engine):
    """Test 1: Normal baseline operations produces LOW risk and nominal advice."""
    state = get_scenario_normal()
    decision = engine.process(state)

    assert decision.risk_level == RiskLevel.LOW
    assert decision.risk_score < 0.30
    assert "NOMINAL" in decision.recommended_action.upper()
    assert decision.confidence >= 0.85
    assert len(decision.reasons) > 0
    assert len(decision.evidence) > 0


def test_scenario_solar_storm(engine):
    """Test 2: Solar particle event triggers shelter recommendation."""
    state = get_scenario_solar_storm()
    decision = engine.process(state)

    assert decision.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    assert decision.risk_score >= 0.50
    assert "SHELTER" in decision.recommended_action.upper()
    assert any("Radiation Safe-Route" in f.pillar for f in decision.contributing_factors)
    assert any("Radiation" in e.title or "Solar" in e.title for e in decision.evidence)


def test_scenario_voice_anomaly(engine):
    """Test 3: Voice Vitals fatigue and strain triggers rest recommendation."""
    state = get_scenario_voice_anomaly()
    decision = engine.process(state)

    assert decision.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]
    assert any("Voice Vitals" in f.pillar for f in decision.contributing_factors)
    assert any("fatigue" in r.lower() or "cognitive" in r.lower() for r in decision.reasons)
    assert "FATIGUE" in decision.recommended_action.upper() or "REST" in decision.recommended_action.upper()


def test_scenario_astro_twin_decline(engine):
    """Test 4: Standalone Astro-Twin deconditioning triggers countermeasure adjustment."""
    state = CrewState(
        radiation=RadiationState(risk_level="LOW", dose_rate_msv_h=0.02),
        voice_vitals=VoiceVitalsState(fatigue_score=0.1, cognitive_strain_score=0.1),
        astro_twin=AstroTwinState(
            projected_bone_loss_pct_mo=1.8,
            exercise_deficit_days=3,
            countermeasure_status="DEFICIT"
        )
    )
    decision = engine.process(state)

    assert decision.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]
    assert any("Astro-Twin" in f.pillar for f in decision.contributing_factors)
    assert "COUNTERMEASURE" in decision.recommended_action.upper() or "EXERCISE" in decision.recommended_action.upper()


def test_scenario_combined_anomaly(engine):
    """Test 5: Combined environmental, biometric, and digital twin anomalies escalate to CRITICAL."""
    state = get_scenario_combined_anomaly()
    decision = engine.process(state)

    assert decision.risk_level == RiskLevel.CRITICAL
    assert decision.risk_score >= 0.75
    assert any("ESCALATION" in r for r in decision.reasons)
    assert len(decision.contributing_factors) >= 3


def test_scenario_offline_blackout(engine):
    """Test 6: Offline mode functions 100% locally and marks decision OFFLINE."""
    state = get_scenario_offline_blackout()
    decision = engine.process(state)

    assert decision.mode == CommsMode.OFFLINE
    assert any("BLACKOUT" in r for r in decision.reasons)
    assert len(decision.evidence) > 0
    assert any("ASCEND" in e.citation or "Blackouts" in e.title for e in decision.evidence)


def test_scenario_uncertain_data(engine):
    """Test 7: Low confidence inputs surface uncertainty and avoid overconfident actions."""
    state = get_scenario_uncertain_data()
    decision = engine.process(state)

    assert decision.confidence < 0.60
    assert len(decision.uncertainty) > 0
    assert ("CONFIRMATORY" in decision.recommended_action.upper() or "OBSERVATION" in decision.recommended_action.upper())


def test_multi_signal_synergy(engine):
    """Test 8: Two anomalies produce higher score than individual single anomaly."""
    single_rad_state = CrewState(
        radiation=RadiationState(risk_level="HIGH", dose_rate_msv_h=0.15),
        voice_vitals=VoiceVitalsState(fatigue_score=0.1, cognitive_strain_score=0.1),
        astro_twin=AstroTwinState(exercise_deficit_days=0)
    )
    dual_state = CrewState(
        radiation=RadiationState(risk_level="HIGH", dose_rate_msv_h=0.15),
        voice_vitals=VoiceVitalsState(fatigue_score=0.6, cognitive_strain_score=0.6, deviation_from_baseline_z=2.1),
        astro_twin=AstroTwinState(exercise_deficit_days=0)
    )

    dec_single = engine.process(single_rad_state)
    dec_dual = engine.process(dual_state)

    assert dec_dual.risk_score > dec_single.risk_score


def test_conflicting_signals(engine):
    """Test 9: High biometric strain with nominal environment resolves to clinical rather than shelter."""
    state = CrewState(
        radiation=RadiationState(risk_level="LOW", dose_rate_msv_h=0.01, spe_active=False),
        voice_vitals=VoiceVitalsState(fatigue_score=0.8, cognitive_strain_score=0.75, deviation_from_baseline_z=2.5),
        astro_twin=AstroTwinState(exercise_deficit_days=0)
    )
    decision = engine.process(state)
    
    # Should identify health concern without unnecessarily alarming on shelter
    assert "FATIGUE" in decision.recommended_action.upper() or "REST" in decision.recommended_action.upper()
    assert not any("Radiation Safe-Route" in f.pillar for f in decision.contributing_factors)


def test_deterministic_consistency(engine):
    """Test 10: Repeated identical states yield identical risk scores and recommendations."""
    state = get_scenario_combined_anomaly()
    dec_1 = engine.process(state)
    dec_2 = engine.process(state)

    assert dec_1.risk_score == dec_2.risk_score
    assert dec_1.risk_level == dec_2.risk_level
    assert dec_1.recommended_action == dec_2.recommended_action
    assert dec_1.reasons == dec_2.reasons


def test_data_staleness_uncertainty(engine):
    """Test 11: Telemetry older than 300s is flagged in uncertainty."""
    state = get_scenario_normal()
    state.data_freshness_seconds = 450
    decision = engine.process(state)

    assert any("stale" in u.lower() for u in decision.uncertainty)


def test_risk_fusion_breakdown(engine):
    """Test 12: Verify transparent risk fusion mathematical trace."""
    state = get_scenario_combined_anomaly()
    decision = engine.process(state)

    assert decision.risk_fusion is not None
    rf = decision.risk_fusion
    assert rf.baseline_score == 0.10
    assert rf.p1_radiation.score_addition > 0
    assert rf.p2_voice_vitals.score_addition > 0
    assert rf.p3_astro_twin.score_addition > 0
    assert rf.synergy_score > 0
    assert rf.final_score == decision.risk_score
    assert "Base" in rf.formula and "P1 Rad" in rf.formula


def test_decision_trace_structure_and_matching(engine):
    """Test 13: Decision trace contains actual contributing signals and matches engine decision."""
    state = get_scenario_combined_anomaly()
    decision = engine.process(state)

    assert decision.decision_trace is not None
    trace = decision.decision_trace
    assert trace.base_risk == 0.10
    assert trace.final_risk == decision.risk_score
    assert trace.final_level == decision.risk_level

    # Check signals
    assert len(trace.signals) == 3
    sources = [s.source for s in trace.signals]
    assert "P1" in sources and "P2" in sources and "P3" in sources

    # P1 signal verification
    p1_sig = next(s for s in trace.signals if s.source == "P1")
    assert p1_sig.triggered is True
    assert p1_sig.contribution > 0
    assert "Threshold" in p1_sig.threshold or ">=" in p1_sig.threshold

    # Synergy rules verification
    assert len(trace.synergy_rules) >= 2
    multi_rule = next(r for r in trace.synergy_rules if "Multi-Pillar" in r.name)
    assert multi_rule.triggered is True
    assert multi_rule.contribution > 0


def test_what_if_simulation_endpoint():
    """Test 14: What-If simulation is deterministic and passes through existing P4 engine."""
    from aegis_deepspace.server import simulate_evacuation_delay, WhatIfDelayRequest
    
    # 0 min delay
    res_0a = simulate_evacuation_delay(WhatIfDelayRequest(delay_minutes=0.0, scenario="solar_storm"))
    res_0b = simulate_evacuation_delay(WhatIfDelayRequest(delay_minutes=0.0, scenario="solar_storm"))
    assert res_0a["counterfactual"]["risk_score"] == res_0b["counterfactual"]["risk_score"]
    assert res_0a["impact"]["delta_exposure_msv"] == 0.0

    # 30 min delay vs 60 min delay
    res_30 = simulate_evacuation_delay(WhatIfDelayRequest(delay_minutes=30.0, scenario="solar_storm"))
    res_60 = simulate_evacuation_delay(WhatIfDelayRequest(delay_minutes=60.0, scenario="solar_storm"))

    # Monotonic exposure increase: delay cannot decrease exposure
    assert res_60["counterfactual"]["projected_exposure_msv"] >= res_30["counterfactual"]["projected_exposure_msv"]
    assert res_30["impact"]["delta_exposure_msv"] > 0
    assert res_60["impact"]["delta_exposure_msv"] > res_30["impact"]["delta_exposure_msv"]
    assert res_60["counterfactual"]["risk_score"] >= res_0a["baseline"]["risk_score"]
    assert "decision_trace" in res_60["counterfactual"]

