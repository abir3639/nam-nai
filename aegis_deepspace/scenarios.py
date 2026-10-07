"""Pre-configured demo scenarios for Aegis-DeepSpace Pillar 4 Autonomous Decision Engine.
Powered by the decoupled Pillar 1-3 Mock Providers.
"""

from typing import Dict, Any, Callable
from aegis_deepspace.models import CrewState
from aegis_deepspace.providers import (
    default_coordinator,
    MockRadiationProvider,
    MockVoiceVitalsProvider,
    MockAstroTwinProvider,
    TelemetryCoordinator
)


def get_scenario_normal() -> CrewState:
    """Scenario 1: Normal baseline operations."""
    return default_coordinator.get_crew_state("normal")


def get_scenario_solar_storm() -> CrewState:
    """Scenario 2: Solar storm (SPE) detected by Radiation Safe-Route."""
    return default_coordinator.get_crew_state("solar_storm")


def get_scenario_voice_anomaly() -> CrewState:
    """Scenario 3: Passive Voice Vitals detects fatigue and cognitive strain."""
    return default_coordinator.get_crew_state("voice_anomaly")


def get_scenario_combined_anomaly() -> CrewState:
    """Scenario 4: High radiation + Voice Vitals cognitive strain + Astro-Twin deconditioning."""
    return default_coordinator.get_crew_state("combined_anomaly")


def get_scenario_offline_blackout() -> CrewState:
    """Scenario 5: Communication blackout (20-min Mars delay / loss of Earth signal)."""
    return default_coordinator.get_crew_state("offline_blackout")


def get_scenario_uncertain_data() -> CrewState:
    """Scenario 6: Low confidence and conflicting/noisy signals."""
    return default_coordinator.get_crew_state("uncertain_data")


DEMO_SCENARIOS: Dict[str, Callable[[], CrewState]] = {
    "normal": get_scenario_normal,
    "solar_storm": get_scenario_solar_storm,
    "voice_anomaly": get_scenario_voice_anomaly,
    "combined_anomaly": get_scenario_combined_anomaly,
    "offline_blackout": get_scenario_offline_blackout,
    "uncertain_data": get_scenario_uncertain_data
}
