"""Pre-configured demo scenarios for Aegis-DeepSpace Pillar 4 Autonomous Decision Engine.
Allows demonstrating the full decision engine without live APIs or network connection.
"""

from typing import Dict, Any
from aegis_deepspace.models import (
    CrewState,
    RadiationState,
    VoiceVitalsState,
    AstroTwinState,
    CommsMode
)


def get_scenario_normal() -> CrewState:
    """Scenario 1: Normal baseline operations."""
    return CrewState(
        comms_mode=CommsMode.ONLINE,
        data_freshness_seconds=5,
        radiation=RadiationState(
            risk_level="LOW",
            dose_rate_msv_h=0.02,
            cumulative_dose_msv=1.2,
            spe_active=False,
            current_module="Command Module",
            recommended_safe_module="Command Module",
            shielding_rating_g_cm2=12.0,
            confidence=0.96
        ),
        voice_vitals=VoiceVitalsState(
            fatigue_score=0.10,
            cognitive_strain_score=0.12,
            hypoxia_indicator=0.04,
            deviation_from_baseline_z=0.3,
            confidence=0.92
        ),
        astro_twin=AstroTwinState(
            projected_bone_loss_pct_mo=0.8,
            projected_muscle_atrophy_pct=1.5,
            exercise_deficit_days=0,
            countermeasure_status="NOMINAL",
            prediction_horizon_days=14,
            confidence=0.90
        )
    )


def get_scenario_solar_storm() -> CrewState:
    """Scenario 2: Solar storm (SPE) detected by Radiation Safe-Route."""
    return CrewState(
        comms_mode=CommsMode.ONLINE,
        data_freshness_seconds=8,
        radiation=RadiationState(
            risk_level="CRITICAL",
            dose_rate_msv_h=0.68,
            cumulative_dose_msv=4.8,
            spe_active=True,
            current_module="Gym / Exercise Bay",
            recommended_safe_module="Storm Shelter (Water Wall)",
            shielding_rating_g_cm2=10.0,
            confidence=0.94
        ),
        voice_vitals=VoiceVitalsState(
            fatigue_score=0.20,
            cognitive_strain_score=0.25,
            hypoxia_indicator=0.06,
            deviation_from_baseline_z=0.6,
            confidence=0.89
        ),
        astro_twin=AstroTwinState(
            projected_bone_loss_pct_mo=1.0,
            projected_muscle_atrophy_pct=2.0,
            exercise_deficit_days=1,
            countermeasure_status="PENDING_SHELTER",
            prediction_horizon_days=14,
            confidence=0.88
        )
    )


def get_scenario_voice_anomaly() -> CrewState:
    """Scenario 3: Passive Voice Vitals detects fatigue and cognitive strain."""
    return CrewState(
        comms_mode=CommsMode.ONLINE,
        data_freshness_seconds=12,
        radiation=RadiationState(
            risk_level="LOW",
            dose_rate_msv_h=0.03,
            cumulative_dose_msv=1.5,
            spe_active=False,
            current_module="Science Laboratory",
            recommended_safe_module="Science Laboratory",
            shielding_rating_g_cm2=14.0,
            confidence=0.95
        ),
        voice_vitals=VoiceVitalsState(
            fatigue_score=0.68,
            cognitive_strain_score=0.74,
            hypoxia_indicator=0.18,
            deviation_from_baseline_z=2.4,
            confidence=0.91
        ),
        astro_twin=AstroTwinState(
            projected_bone_loss_pct_mo=0.9,
            projected_muscle_atrophy_pct=1.8,
            exercise_deficit_days=0,
            countermeasure_status="NOMINAL",
            prediction_horizon_days=14,
            confidence=0.89
        )
    )


def get_scenario_combined_anomaly() -> CrewState:
    """Scenario 4: High radiation + Voice Vitals cognitive strain + Astro-Twin deconditioning."""
    return CrewState(
        comms_mode=CommsMode.ONLINE,
        data_freshness_seconds=6,
        radiation=RadiationState(
            risk_level="CRITICAL",
            dose_rate_msv_h=0.55,
            cumulative_dose_msv=5.2,
            spe_active=True,
            current_module="Service Module",
            recommended_safe_module="Storm Shelter (Water Wall)",
            shielding_rating_g_cm2=8.0,
            confidence=0.93
        ),
        voice_vitals=VoiceVitalsState(
            fatigue_score=0.72,
            cognitive_strain_score=0.69,
            hypoxia_indicator=0.45,
            deviation_from_baseline_z=2.8,
            confidence=0.88
        ),
        astro_twin=AstroTwinState(
            projected_bone_loss_pct_mo=1.8,
            projected_muscle_atrophy_pct=4.2,
            exercise_deficit_days=4,
            countermeasure_status="RESTRICTED_BY_STORM",
            prediction_horizon_days=14,
            confidence=0.86
        )
    )


def get_scenario_offline_blackout() -> CrewState:
    """Scenario 5: Communication blackout (20-min Mars delay / loss of Earth signal)."""
    return CrewState(
        comms_mode=CommsMode.OFFLINE,
        data_freshness_seconds=15,
        radiation=RadiationState(
            risk_level="HIGH",
            dose_rate_msv_h=0.18,
            cumulative_dose_msv=2.9,
            spe_active=True,
            current_module="Habitat Quarters",
            recommended_safe_module="Storm Shelter (Water Wall)",
            shielding_rating_g_cm2=18.0,
            confidence=0.90
        ),
        voice_vitals=VoiceVitalsState(
            fatigue_score=0.55,
            cognitive_strain_score=0.52,
            hypoxia_indicator=0.12,
            deviation_from_baseline_z=1.8,
            confidence=0.87
        ),
        astro_twin=AstroTwinState(
            projected_bone_loss_pct_mo=1.2,
            projected_muscle_atrophy_pct=2.8,
            exercise_deficit_days=2,
            countermeasure_status="ADAPTIVE_EDGE_SCHEDULE",
            prediction_horizon_days=14,
            confidence=0.85
        )
    )


def get_scenario_uncertain_data() -> CrewState:
    """Scenario 6: Low confidence and conflicting/noisy signals."""
    return CrewState(
        comms_mode=CommsMode.ONLINE,
        data_freshness_seconds=420,  # Stale data
        radiation=RadiationState(
            risk_level="MEDIUM",
            dose_rate_msv_h=0.08,
            cumulative_dose_msv=1.9,
            spe_active=False,
            current_module="Command Module",
            recommended_safe_module="Habitat Quarters",
            shielding_rating_g_cm2=12.0,
            confidence=0.48  # Low confidence sensor
        ),
        voice_vitals=VoiceVitalsState(
            fatigue_score=0.45,
            cognitive_strain_score=0.38,
            hypoxia_indicator=0.15,
            deviation_from_baseline_z=1.1,
            confidence=0.52  # Low SNR audio
        ),
        astro_twin=AstroTwinState(
            projected_bone_loss_pct_mo=1.1,
            projected_muscle_atrophy_pct=2.1,
            exercise_deficit_days=1,
            countermeasure_status="NOMINAL",
            prediction_horizon_days=14,
            confidence=0.55  # Sparse parameters
        )
    )


DEMO_SCENARIOS = {
    "normal": get_scenario_normal,
    "solar_storm": get_scenario_solar_storm,
    "voice_anomaly": get_scenario_voice_anomaly,
    "combined_anomaly": get_scenario_combined_anomaly,
    "offline_blackout": get_scenario_offline_blackout,
    "uncertain_data": get_scenario_uncertain_data
}
