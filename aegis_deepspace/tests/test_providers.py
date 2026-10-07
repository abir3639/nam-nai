"""Tests for Pillar 1-3 decoupled Mock Providers and interfaces."""

import pytest
from aegis_deepspace.providers import (
    BaseRadiationProvider,
    BaseVoiceVitalsProvider,
    BaseAstroTwinProvider,
    MockRadiationProvider,
    MockVoiceVitalsProvider,
    MockAstroTwinProvider,
    TelemetryCoordinator
)
from aegis_deepspace.models import (
    RadiationState,
    VoiceVitalsState,
    AstroTwinState,
    CrewState,
    CommsMode
)
from aegis_deepspace.decision_engine import AutonomousDecisionEngine


def test_mock_radiation_provider_interface():
    """Verify MockRadiationProvider satisfies BaseRadiationProvider interface."""
    provider = MockRadiationProvider()
    assert isinstance(provider, BaseRadiationProvider)
    
    rad_normal = provider.get_radiation_state("normal")
    assert isinstance(rad_normal, RadiationState)
    assert rad_normal.risk_level == "LOW"
    assert rad_normal.spe_active is False

    rad_storm = provider.get_radiation_state("solar_storm")
    assert isinstance(rad_storm, RadiationState)
    assert rad_storm.risk_level == "CRITICAL"
    assert rad_storm.spe_active is True
    assert rad_storm.dose_rate_msv_h > 0.5


def test_mock_voice_vitals_provider_interface():
    """Verify MockVoiceVitalsProvider satisfies BaseVoiceVitalsProvider interface."""
    provider = MockVoiceVitalsProvider()
    assert isinstance(provider, BaseVoiceVitalsProvider)

    voice_normal = provider.get_voice_vitals("normal")
    assert isinstance(voice_normal, VoiceVitalsState)
    assert voice_normal.fatigue_score <= 0.20
    assert voice_normal.cognitive_strain_score <= 0.20

    voice_anomaly = provider.get_voice_vitals("voice_anomaly")
    assert isinstance(voice_anomaly, VoiceVitalsState)
    assert voice_anomaly.cognitive_strain_score > 0.60
    assert voice_anomaly.fatigue_score > 0.60


def test_mock_astro_twin_provider_interface():
    """Verify MockAstroTwinProvider satisfies BaseAstroTwinProvider interface."""
    provider = MockAstroTwinProvider()
    assert isinstance(provider, BaseAstroTwinProvider)

    twin_normal = provider.get_astro_twin_state("normal")
    assert isinstance(twin_normal, AstroTwinState)
    assert twin_normal.exercise_deficit_days == 0
    assert twin_normal.countermeasure_status == "NOMINAL"

    twin_storm = provider.get_astro_twin_state("solar_storm")
    assert isinstance(twin_storm, AstroTwinState)
    assert twin_storm.exercise_deficit_days >= 1
    assert "SHELTER" in twin_storm.countermeasure_status

    twin_combined = provider.get_astro_twin_state("combined_anomaly")
    assert isinstance(twin_combined, AstroTwinState)
    assert twin_combined.exercise_deficit_days >= 3
    assert twin_combined.projected_muscle_atrophy_pct > 3.0


def test_telemetry_coordinator_pluggable_replacement():
    """Verify that a custom or future real provider can plug into the coordinator without changing Pillar 4."""
    class CustomRealRadProvider(BaseRadiationProvider):
        def get_radiation_state(self, scenario: str = "normal") -> RadiationState:
            return RadiationState(
                risk_level="HIGH",
                dose_rate_msv_h=0.35,
                spe_active=True,
                current_module="Greenhouse",
                recommended_safe_module="Storm Shelter"
            )

    custom_coord = TelemetryCoordinator(radiation_provider=CustomRealRadProvider())
    crew_state = custom_coord.get_crew_state("normal")
    
    assert crew_state.radiation.current_module == "Greenhouse"
    assert crew_state.radiation.dose_rate_msv_h == 0.35
    
    # Process through Pillar 4 decision engine
    engine = AutonomousDecisionEngine()
    decision = engine.process(crew_state)
    assert "SHELTER" in decision.recommended_action.upper()
    assert decision.risk_score >= 0.40


def test_scenario_offline_and_uncertainty():
    """Verify coordinator properly marks comms and data freshness."""
    coord = TelemetryCoordinator()
    
    offline_state = coord.get_crew_state("offline_blackout")
    assert offline_state.comms_mode == CommsMode.OFFLINE

    uncertain_state = coord.get_crew_state("uncertain_data")
    assert uncertain_state.data_freshness_seconds >= 300
    assert uncertain_state.radiation.confidence < 0.60
    assert uncertain_state.voice_vitals.confidence < 0.60
    assert uncertain_state.astro_twin.confidence < 0.60


def test_real_astro_twin_provider():
    """Verify RealAstroTwinProvider simulation runs and satisfies BaseAstroTwinProvider."""
    from aegis_deepspace.pillar3_real import RealAstroTwinProvider
    provider = RealAstroTwinProvider()
    assert isinstance(provider, BaseAstroTwinProvider)

    # Test get_astro_twin_state
    norm = provider.get_astro_twin_state("normal")
    assert norm.exercise_deficit_days == 0
    assert norm.countermeasure_status == "NOMINAL"

    comb = provider.get_astro_twin_state("combined_anomaly")
    assert comb.exercise_deficit_days == 4
    assert comb.projected_muscle_atrophy_pct >= 4.0
    assert "STORM" in comb.countermeasure_status

    # Test full simulation
    sim = provider.simulate_digital_twin(
        astronaut_profile={"age": 40, "sex": "M", "body_mass_kg": 80, "baseline_hip_bmd": 1.05},
        total_days=30,
        outage_start=8,
        outage_duration=4,
        recovery_window=6
    )
    assert sim["status"] == "REAL_SIMULATION_ACTIVE"
    assert len(sim["nominal_trajectory"]) == 30
    assert len(sim["outage_trajectory"]) == 30
    assert sim["prescription"]["outage_duration_days"] == 4
    assert sim["prescription"]["total_mechanical_work_deficit_kg"] == 36000.0
    assert "+66.7%" in sim["prescription"]["required_daily_volume_surge"]

