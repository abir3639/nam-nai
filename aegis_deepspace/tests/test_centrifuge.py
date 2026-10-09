"""Tests for Centrifugal Ring Spin-Down Simulator."""

import pytest
from aegis_deepspace.centrifuge_sim import (
    CentrifugeSimulator,
    CentrifugeSimConfig,
    default_centrifuge_simulator
)


def test_centrifuge_default_simulation():
    sim = CentrifugeSimulator()
    result = sim.run_simulation()
    
    # Check config
    assert result.config.initial_g == 0.38
    assert result.config.target_g == 0.00
    assert result.config.duration_seconds == 90.0
    
    # Check deltas
    deltas = result.telemetry_deltas
    assert deltas["gravitational_vector"]["initial_g"] == 0.38
    assert deltas["gravitational_vector"]["terminal_g"] == 0.00
    cvp = deltas["hemodynamic_and_cranial_pressures"]["central_venous_pressure_cvp"]
    assert cvp["baseline_mmhg"] == 4.2
    assert cvp["acute_peak_mmhg"] >= 10.0
    
    icp = deltas["hemodynamic_and_cranial_pressures"]["intracranial_pressure_icp"]
    assert icp["baseline_mmhg"] == 10.5
    assert icp["transient_spike_mmhg"] >= 20.0
    
    # Check acute clinical risks
    assert len(result.acute_clinical_risks) == 3
    risk_ids = [r["risk_id"] for r in result.acute_clinical_risks]
    assert "ACR-01" in risk_ids
    assert "ACR-02" in risk_ids
    assert "ACR-03" in risk_ids
    
    # Check 3 prioritized countermeasures
    assert len(result.primary_countermeasures) == 3
    assert result.primary_countermeasures[0]["action_code"] == "DIRECTIVE_ALPHA_RESTRAINT_DAMPING"
    assert result.primary_countermeasures[1]["action_code"] == "DIRECTIVE_BRAVO_NEUROVESTIBULAR_PROPHYLAXIS"
    assert result.primary_countermeasures[2]["action_code"] == "DIRECTIVE_CHARLIE_SPLANCHNIC_SEQUESTRATION"
    
    # Check system interventions
    assert "eclss_control_signals" in result.system_interventions
    assert "medical_dispenser_signals" in result.system_interventions
    assert "mechanical_and_hull_safing" in result.system_interventions
    
    # Check verdict
    assert result.flight_surgeon_verdict["alert_classification"] == "RED_CRITICAL_EMERGENCY"
    assert result.flight_surgeon_verdict["autonomous_authority_level"] == "LEVEL_5_AUTONOMOUS_INTERVENTION_OVERRIDE"
    
    # Check crew roster
    assert len(result.crew_roster) == 4
    assert result.crew_roster[0].role == "Commander"


def test_centrifuge_mitigated_simulation():
    sim = CentrifugeSimulator()
    cfg = CentrifugeSimConfig(
        magnetic_deck_locked=True,
        countermeasures_active=True
    )
    result = sim.run_simulation(cfg)
    
    # Mitigated CVP and ICP should be lower than unmitigated peak
    last_step = result.time_series[-1]
    assert last_step.collision_prob_pct < 10.0
    assert last_step.sms_index < 50.0
    assert result.flight_surgeon_verdict["alert_classification"] == "AMBER_POST_DESPIN_STABILIZED"


def test_crew_state_conversion():
    sim = CentrifugeSimulator()
    result = sim.run_simulation()
    crew_state = sim.convert_to_crew_state(result)
    assert crew_state.voice_vitals.cognitive_strain_score > 0.7
    assert crew_state.astro_twin.countermeasure_status == "CENTRIFUGE_DESPIN_CONTINGENCY"
