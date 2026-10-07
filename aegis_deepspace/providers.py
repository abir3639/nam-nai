"""Provider Interfaces and Mock Implementations for Pillars 1, 2, and 3.

ARCHITECTURE PRINCIPLE:
Pillars 1-3 are decoupled providers with clean, standardized interfaces.
Future real implementations (e.g. real-time NASA DONKI/SPE models, Whisper/CNN acoustic
inference, or biomechanical digital twin ODE engines) can replace these mocks by
implementing the same abstract interfaces without modifying Pillar 4 or the frontend.

All mock data is deterministic, scenario-driven, and clearly designated as SIMULATED/DEMO DATA.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from aegis_deepspace.models import (
    RadiationState,
    VoiceVitalsState,
    AstroTwinState,
    CommsMode,
    CrewState
)


# =====================================================================
# Abstract Provider Interfaces (Contracts for real & mock implementations)
# =====================================================================

class BaseRadiationProvider(ABC):
    """Clean interface for Pillar 1: Environmental Defense (Radiation Safe-Route)."""

    @abstractmethod
    def get_radiation_state(self, scenario: str = "normal") -> RadiationState:
        """Retrieves current or predicted radiation state across habitat compartments.
        
        Args:
            scenario: Current operational scenario identifier.
            
        Returns:
            RadiationState with dose rates, cumulative dose, SPE status, and safe module.
        """
        pass


class BaseVoiceVitalsProvider(ABC):
    """Clean interface for Pillar 2: Passive Biometrics (Voice Vitals)."""

    @abstractmethod
    def get_voice_vitals(self, scenario: str = "normal") -> VoiceVitalsState:
        """Retrieves acoustic vitals derived from passive crew vocal logs.
        
        Args:
            scenario: Current operational scenario identifier.
            
        Returns:
            VoiceVitalsState with fatigue, cognitive strain, hypoxia indicator, and z-score.
        """
        pass


class BaseAstroTwinProvider(ABC):
    """Clean interface for Pillar 3: Predictive Twin (Astro-Twin)."""

    @abstractmethod
    def get_astro_twin_state(self, scenario: str = "normal") -> AstroTwinState:
        """Retrieves forward-simulated physiological digital twin trajectory.
        
        Args:
            scenario: Current operational scenario identifier.
            
        Returns:
            AstroTwinState with projected bone mineral density loss, muscle atrophy, and deficit days.
        """
        pass


# =====================================================================
# Lightweight Deterministic Mock Implementations
# =====================================================================

class MockRadiationProvider(BaseRadiationProvider):
    """Lightweight deterministic mock provider for Pillar 1 (Radiation Safe-Route)."""

    def __init__(self):
        # Deterministic scenario tables based on habitat topology and space weather
        self._scenario_data: Dict[str, Dict[str, Any]] = {
            "normal": {
                "risk_level": "LOW",
                "dose_rate_msv_h": 0.02,
                "cumulative_dose_msv": 1.2,
                "spe_active": False,
                "current_module": "Command Module",
                "recommended_safe_module": "Command Module",
                "shielding_rating_g_cm2": 12.0,
                "confidence": 0.96
            },
            "solar_storm": {
                "risk_level": "CRITICAL",
                "dose_rate_msv_h": 0.68,
                "cumulative_dose_msv": 4.8,
                "spe_active": True,
                "current_module": "Gym / Exercise Bay",
                "recommended_safe_module": "Storm Shelter (Water Wall)",
                "shielding_rating_g_cm2": 10.0,
                "confidence": 0.94
            },
            "voice_anomaly": {
                "risk_level": "LOW",
                "dose_rate_msv_h": 0.03,
                "cumulative_dose_msv": 1.5,
                "spe_active": False,
                "current_module": "Science Laboratory",
                "recommended_safe_module": "Science Laboratory",
                "shielding_rating_g_cm2": 14.0,
                "confidence": 0.95
            },
            "combined_anomaly": {
                "risk_level": "CRITICAL",
                "dose_rate_msv_h": 0.55,
                "cumulative_dose_msv": 5.2,
                "spe_active": True,
                "current_module": "Service Module",
                "recommended_safe_module": "Storm Shelter (Water Wall)",
                "shielding_rating_g_cm2": 8.0,
                "confidence": 0.93
            },
            "offline_blackout": {
                "risk_level": "HIGH",
                "dose_rate_msv_h": 0.18,
                "cumulative_dose_msv": 2.9,
                "spe_active": True,
                "current_module": "Habitat Quarters",
                "recommended_safe_module": "Storm Shelter (Water Wall)",
                "shielding_rating_g_cm2": 18.0,
                "confidence": 0.90
            },
            "uncertain_data": {
                "risk_level": "MEDIUM",
                "dose_rate_msv_h": 0.08,
                "cumulative_dose_msv": 1.9,
                "spe_active": False,
                "current_module": "Command Module",
                "recommended_safe_module": "Habitat Quarters",
                "shielding_rating_g_cm2": 12.0,
                "confidence": 0.48  # Low confidence / noisy sensor
            }
        }

    def get_radiation_state(self, scenario: str = "normal") -> RadiationState:
        data = self._scenario_data.get(scenario, self._scenario_data["normal"])
        return RadiationState(**data)


class MockVoiceVitalsProvider(BaseVoiceVitalsProvider):
    """Lightweight deterministic mock provider for Pillar 2 (Voice Vitals)."""

    def __init__(self):
        self._scenario_data: Dict[str, Dict[str, Any]] = {
            "normal": {
                "fatigue_score": 0.10,
                "cognitive_strain_score": 0.12,
                "hypoxia_indicator": 0.04,
                "deviation_from_baseline_z": 0.3,
                "confidence": 0.92
            },
            "solar_storm": {
                "fatigue_score": 0.20,
                "cognitive_strain_score": 0.25,
                "hypoxia_indicator": 0.06,
                "deviation_from_baseline_z": 0.6,
                "confidence": 0.89
            },
            "voice_anomaly": {
                "fatigue_score": 0.68,
                "cognitive_strain_score": 0.74,
                "hypoxia_indicator": 0.18,
                "deviation_from_baseline_z": 2.4,
                "confidence": 0.91
            },
            "combined_anomaly": {
                "fatigue_score": 0.72,
                "cognitive_strain_score": 0.69,
                "hypoxia_indicator": 0.45,
                "deviation_from_baseline_z": 2.8,
                "confidence": 0.88
            },
            "offline_blackout": {
                "fatigue_score": 0.55,
                "cognitive_strain_score": 0.52,
                "hypoxia_indicator": 0.12,
                "deviation_from_baseline_z": 1.8,
                "confidence": 0.87
            },
            "uncertain_data": {
                "fatigue_score": 0.45,
                "cognitive_strain_score": 0.38,
                "hypoxia_indicator": 0.15,
                "deviation_from_baseline_z": 1.1,
                "confidence": 0.52  # Low SNR audio
            }
        }

    def get_voice_vitals(self, scenario: str = "normal") -> VoiceVitalsState:
        data = self._scenario_data.get(scenario, self._scenario_data["normal"])
        return VoiceVitalsState(**data)


class MockAstroTwinProvider(BaseAstroTwinProvider):
    """Lightweight deterministic mock provider for Pillar 3 (Astro-Twin)."""

    def __init__(self):
        self._scenario_data: Dict[str, Dict[str, Any]] = {
            "normal": {
                "projected_bone_loss_pct_mo": 0.8,
                "projected_muscle_atrophy_pct": 1.5,
                "exercise_deficit_days": 0,
                "countermeasure_status": "NOMINAL",
                "prediction_horizon_days": 14,
                "confidence": 0.90
            },
            "solar_storm": {
                # Exercise restricted due to storm shelter confinement
                "projected_bone_loss_pct_mo": 1.0,
                "projected_muscle_atrophy_pct": 2.0,
                "exercise_deficit_days": 1,
                "countermeasure_status": "PENDING_SHELTER",
                "prediction_horizon_days": 14,
                "confidence": 0.88
            },
            "voice_anomaly": {
                "projected_bone_loss_pct_mo": 0.9,
                "projected_muscle_atrophy_pct": 1.8,
                "exercise_deficit_days": 0,
                "countermeasure_status": "NOMINAL",
                "prediction_horizon_days": 14,
                "confidence": 0.89
            },
            "combined_anomaly": {
                # Severe deconditioning after prolonged confinement / cumulative stress
                "projected_bone_loss_pct_mo": 1.8,
                "projected_muscle_atrophy_pct": 4.2,
                "exercise_deficit_days": 4,
                "countermeasure_status": "RESTRICTED_BY_STORM",
                "prediction_horizon_days": 14,
                "confidence": 0.86
            },
            "offline_blackout": {
                "projected_bone_loss_pct_mo": 1.2,
                "projected_muscle_atrophy_pct": 2.8,
                "exercise_deficit_days": 2,
                "countermeasure_status": "ADAPTIVE_EDGE_SCHEDULE",
                "prediction_horizon_days": 14,
                "confidence": 0.85
            },
            "uncertain_data": {
                "projected_bone_loss_pct_mo": 1.1,
                "projected_muscle_atrophy_pct": 2.1,
                "exercise_deficit_days": 1,
                "countermeasure_status": "NOMINAL",
                "prediction_horizon_days": 14,
                "confidence": 0.55  # Sparse parameters
            }
        }

    def get_astro_twin_state(self, scenario: str = "normal") -> AstroTwinState:
        data = self._scenario_data.get(scenario, self._scenario_data["normal"])
        return AstroTwinState(**data)


# =====================================================================
# Unified Multimodal Telemetry Synthesizer
# =====================================================================

class TelemetryCoordinator:
    """Coordinates Pillars 1-3 to build unified CrewState inputs for Pillar 4.
    
    Accepts any implementations of BaseRadiationProvider, BaseVoiceVitalsProvider,
    and BaseAstroTwinProvider, allowing seamless swap-in of real models in the future.
    """

    def __init__(
        self,
        radiation_provider: Optional[BaseRadiationProvider] = None,
        voice_provider: Optional[BaseVoiceVitalsProvider] = None,
        astro_twin_provider: Optional[BaseAstroTwinProvider] = None
    ):
        if radiation_provider is None:
            from aegis_deepspace.pillar1_real import RealRadiationProvider
            self.radiation_provider = RealRadiationProvider()
        else:
            self.radiation_provider = radiation_provider

        if voice_provider is None:
            from aegis_deepspace.pillar2_real import RealVoiceVitalsProvider
            self.voice_provider = RealVoiceVitalsProvider()
        else:
            self.voice_provider = voice_provider

        if astro_twin_provider is None:
            from aegis_deepspace.pillar3_real import RealAstroTwinProvider
            self.astro_twin_provider = RealAstroTwinProvider()
        else:
            self.astro_twin_provider = astro_twin_provider

    def get_crew_state(self, scenario: str = "normal", comms_override: Optional[CommsMode] = None) -> CrewState:
        """Queries Pillars 1-3 and assembles the standard CrewState for Pillar 4."""
        rad_state = self.radiation_provider.get_radiation_state(scenario)
        voice_state = self.voice_provider.get_voice_vitals(scenario)
        twin_state = self.astro_twin_provider.get_astro_twin_state(scenario)

        # Telemetry metadata based on scenario
        freshness = 5
        comms = CommsMode.ONLINE

        if scenario == "offline_blackout":
            comms = CommsMode.OFFLINE
            freshness = 15
        elif scenario == "uncertain_data":
            freshness = 420  # Stale data (7 minutes old)
        elif scenario == "solar_storm":
            freshness = 8
        elif scenario == "voice_anomaly":
            freshness = 12
        elif scenario == "combined_anomaly":
            freshness = 6

        if comms_override is not None:
            comms = comms_override

        return CrewState(
            comms_mode=comms,
            data_freshness_seconds=freshness,
            radiation=rad_state,
            voice_vitals=voice_state,
            astro_twin=twin_state
        )


# Global default coordinator instance
default_coordinator = TelemetryCoordinator()
