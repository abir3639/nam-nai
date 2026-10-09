"""Centrifugal Ring Spin-Down & Gravity Gradient Disruption Simulator.

Models the acute microgravity shock transition from Mars-equivalent artificial gravity (0.38g)
to acute zero-g microgravity (0.0g) within a defined spin-down window (default 90 seconds)
with angular Coriolis shear and cephalad fluid redistribution.
"""

from typing import Dict, Any, List, Optional
import math
import datetime
from pydantic import BaseModel, Field

from aegis_deepspace.models import (
    CrewState,
    RadiationState,
    VoiceVitalsState,
    AstroTwinState,
    CommsMode,
    RiskLevel
)


class CentrifugeSimConfig(BaseModel):
    """Configuration for centrifugal despin simulation."""
    initial_g: float = Field(default=0.38, ge=0.0, le=2.0, description="Initial artificial gravity in g")
    target_g: float = Field(default=0.00, ge=0.0, le=2.0, description="Terminal gravity in g")
    duration_seconds: float = Field(default=90.0, ge=10.0, le=300.0, description="Spin-down deceleration window")
    angular_deceleration_deg_s2: float = Field(default=2.4, ge=0.1, le=10.0, description="Angular deceleration rate")
    crew_count: int = Field(default=4, ge=1, le=8, description="Active crew count")
    strapped_at_onset: bool = Field(default=False, description="Whether crew were secured in harnesses")
    fluid_shift_rate_ml_min: float = Field(default=850.0, ge=100.0, le=2000.0, description="Cephalad fluid redistribution rate")
    magnetic_deck_locked: bool = Field(default=False, description="Whether electromagnetic deck lock is energized")
    countermeasures_active: bool = Field(default=False, description="Whether antiemetics and LBNP/Braslet cuffs deployed")


class TimeStepTelemetry(BaseModel):
    """Telemetry sample at a specific second in the spin-down trajectory."""
    time_s: float
    g_level: float
    angular_velocity_deg_s: float
    cvp_mmhg: float
    icp_mmhg: float
    cephalad_volume_ml: float
    vestibular_mismatch_deg: float
    sms_index: float
    collision_prob_pct: float
    phase_label: str


class CrewMemberStatus(BaseModel):
    """Individual crew member biometric and clinical status."""
    crew_id: str
    role: str
    name: str
    heart_rate_bpm: int
    blood_pressure_sys: int
    blood_pressure_dia: int
    cvp_mmhg: float
    icp_mmhg: float
    sms_score: float
    sms_status: str
    restraint_status: str
    autoinjector_status: str
    collision_alert: bool


class CentrifugeSimulationResult(BaseModel):
    """Complete simulation result and clinical flight surgeon decision packet."""
    timestamp: str
    config: CentrifugeSimConfig
    telemetry_deltas: Dict[str, Any]
    acute_clinical_risks: List[Dict[str, Any]]
    primary_countermeasures: List[Dict[str, Any]]
    system_interventions: Dict[str, Any]
    flight_surgeon_verdict: Dict[str, Any]
    time_series: List[TimeStepTelemetry]
    crew_roster: List[CrewMemberStatus]


class CentrifugeSimulator:
    """Mathematical engine for artificial gravity centrifugal ring spin-down dynamics."""

    def __init__(self):
        self.nominal_cvp = 4.2       # mmHg baseline
        self.peak_cvp_unmitigated = 11.8  # mmHg
        self.nominal_icp = 10.5      # mmHg baseline
        self.peak_icp_unmitigated = 24.3  # mmHg spike
        self.initial_rpm = 3.8       # Habitat ring baseline rotational velocity

    def run_simulation(self, config: Optional[CentrifugeSimConfig] = None) -> CentrifugeSimulationResult:
        """Executes the high-fidelity biomechanical despin simulation."""
        cfg = config or CentrifugeSimConfig()
        timestamp_now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Compute trajectory steps (e.g. 10 time intervals across duration)
        num_steps = 10
        step_dt = cfg.duration_seconds / num_steps
        time_series: List[TimeStepTelemetry] = []

        g_range = cfg.initial_g - cfg.target_g
        cum_volume = 0.0

        for i in range(num_steps + 1):
            t = round(i * step_dt, 1)
            prog = min(1.0, max(0.0, t / cfg.duration_seconds))
            
            # Non-linear despin curve with governor resistance
            curve = math.sin(prog * (math.pi / 2)) ** 1.3
            curr_g = max(cfg.target_g, cfg.initial_g - (g_range * curve))
            curr_ang_vel = max(0.0, (1.0 - prog) * (cfg.angular_deceleration_deg_s2 * 12.5))

            # Cumulative fluid shift volume (mL)
            # Fluid shift rate scales with gravity loss: +850 mL/min max
            d_vol = (cfg.fluid_shift_rate_ml_min / 60.0) * (1.0 - (curr_g / max(0.001, cfg.initial_g))) * step_dt
            cum_volume += d_vol

            # Hemodynamics
            delta_cvp = (self.peak_cvp_unmitigated - self.nominal_cvp) * (1.0 - (curr_g / max(0.001, cfg.initial_g)))
            if cfg.countermeasures_active:
                delta_cvp *= 0.35  # Braslet cuffs sequester splanchnic volume
            cvp = round(self.nominal_cvp + delta_cvp, 1)

            delta_icp = (self.peak_icp_unmitigated - self.nominal_icp) * ((1.0 - (curr_g / max(0.001, cfg.initial_g))) ** 1.15)
            if cfg.countermeasures_active:
                delta_icp *= 0.30  # LBNP reduces retrobulbar hypertensive surge
            icp = round(self.nominal_icp + delta_icp, 1)

            # Vestibular mismatch & Space Motion Sickness (0-100)
            vestibular_mismatch = round(142.0 * prog, 1)
            raw_sms = 88.5 * (prog ** 0.82)
            if cfg.countermeasures_active:
                raw_sms *= 0.40  # Promethazine / Scopolamine dampens emetic reflex
            sms = round(raw_sms, 1)

            # Collision probability
            if cfg.strapped_at_onset or cfg.magnetic_deck_locked:
                col_prob = round(4.2 * (1.0 - (curr_g / max(0.001, cfg.initial_g))), 1)
            else:
                col_prob = round(78.4 * prog, 1)

            # Phase description
            if prog == 0.0:
                phase = "Nominal Centrifugal Spin (0.38g Mars)"
            elif prog < 0.35:
                phase = "Governor Disengage & Coriolis Shear Onset"
            elif prog < 0.75:
                phase = "Cephalad Trans-Diaphragmatic Fluid Surge"
            elif prog < 1.0:
                phase = "Acute Deceleration & Otolith Phase Mismatch"
            else:
                phase = "Complete Despin / 0.0g Microgravity Shock"

            time_series.append(TimeStepTelemetry(
                time_s=t,
                g_level=round(curr_g, 3),
                angular_velocity_deg_s=round(curr_ang_vel, 2),
                cvp_mmhg=cvp,
                icp_mmhg=icp,
                cephalad_volume_ml=round(cum_volume, 1),
                vestibular_mismatch_deg=vestibular_mismatch,
                sms_index=sms,
                collision_prob_pct=col_prob,
                phase_label=phase
            ))

        # Crew Roster Biometrics
        base_hr = [108, 114, 102, 118]
        base_bp_sys = [142, 148, 138, 152]
        base_bp_dia = [92, 95, 88, 98]
        sms_multipliers = [0.96, 1.03, 0.95, 1.06]
        roles = [
            ("CR-1", "Commander", "CDR Sarah Vance"),
            ("CR-2", "Pilot", "PLT Alex Rivera"),
            ("CR-3", "Chief Medical Officer", "CMO Dr. Maya Lin"),
            ("CR-4", "Mission Specialist", "MS Jin Park")
        ]

        crew_roster: List[CrewMemberStatus] = []
        for idx, (cid, role, name) in enumerate(roles):
            hr = base_hr[idx] if not cfg.countermeasures_active else base_hr[idx] - 18
            bp_sys = base_bp_sys[idx] if not cfg.countermeasures_active else base_bp_sys[idx] - 14
            bp_dia = base_bp_dia[idx] if not cfg.countermeasures_active else base_bp_dia[idx] - 8
            final_cvp = round(time_series[-1].cvp_mmhg * (0.98 + (idx * 0.015)), 1)
            final_icp = round(time_series[-1].icp_mmhg * (0.97 + (idx * 0.02)), 1)
            final_sms = round(min(100.0, time_series[-1].sms_index * sms_multipliers[idx]), 1)

            if cfg.countermeasures_active:
                sms_stat = "STABILIZED (Antiemetic Active)"
                inject_stat = "DISPENSED & ACTIVE"
            elif final_sms > 85.0:
                sms_stat = "CRITICAL / PROJECTILE EMESIS RISK"
                inject_stat = "AUTONOMOUS AUTODOCK ARMED"
            elif final_sms > 60.0:
                sms_stat = "SEVERE DISORIENTATION"
                inject_stat = "PRECHARGED"
            else:
                sms_stat = "MODERATE NAUSEA"
                inject_stat = "STANDBY"

            restr_stat = "MAGNETIC BOOT DECK-LOCKED" if cfg.magnetic_deck_locked else (
                "HARNESSED" if cfg.strapped_at_onset else "FREE-FLOAT UNRESTRAINED"
            )
            col_alert = not (cfg.strapped_at_onset or cfg.magnetic_deck_locked)

            crew_roster.append(CrewMemberStatus(
                crew_id=cid,
                role=role,
                name=name,
                heart_rate_bpm=hr,
                blood_pressure_sys=bp_sys,
                blood_pressure_dia=bp_dia,
                cvp_mmhg=final_cvp,
                icp_mmhg=final_icp,
                sms_score=final_sms,
                sms_status=sms_stat,
                restraint_status=restr_stat,
                autoinjector_status=inject_stat,
                collision_alert=col_alert
            ))

        # Build telemetry deltas exact schema matching user requirements
        telemetry_deltas = {
            "gravitational_vector": {
                "initial_g": cfg.initial_g,
                "terminal_g": cfg.target_g,
                "transition_window_seconds": cfg.duration_seconds,
                "angular_deceleration_alpha": f"{cfg.angular_deceleration_deg_s2} deg/s^2",
                "hydrostatic_column_collapse_pct": 100.0
            },
            "hemodynamic_and_cranial_pressures": {
                "central_venous_pressure_cvp": {
                    "baseline_mmhg": self.nominal_cvp,
                    "acute_peak_mmhg": time_series[-1].cvp_mmhg,
                    "delta_mmhg": f"+{round(time_series[-1].cvp_mmhg - self.nominal_cvp, 1)}",
                    "mechanism": f"Acute thoraco-cephalad venous return via loss of splanchnic and lower-extremity hydrostatic pooling (+{cfg.fluid_shift_rate_ml_min} mL/min)"
                },
                "intracranial_pressure_icp": {
                    "baseline_mmhg": self.nominal_icp,
                    "transient_spike_mmhg": time_series[-1].icp_mmhg,
                    "delta_mmhg": f"+{round(time_series[-1].icp_mmhg - self.nominal_icp, 1)}",
                    "cerebral_perfusion_impact": "Internal jugular vein distension and acute retrobulbar/optic nerve sheath expansion (high-risk transient intracranial hypertension)"
                },
                "cardiovascular_drift": {
                    "stroke_volume_delta_pct": "+26.5%",
                    "baroreflex_vagal_stimulation": "Active (transient bradycardia followed by compensatory sympathetic surge)"
                }
            },
            "neurovestibular_and_kinematics": {
                "coriolis_cross_coupling_g_shear": round(cfg.angular_deceleration_deg_s2 * 0.175, 2),
                "vestibular_cross_coupling_index": 0.91,
                "space_motion_sickness_sms_index": time_series[-1].sms_index,
                "otolith_canal_phase_mismatch_deg": time_series[-1].vestibular_mismatch_deg,
                "blunt_trauma_collision_probability_pct": time_series[-1].collision_prob_pct
            }
        }

        acute_clinical_risks = [
            {
                "risk_id": "ACR-01",
                "label": "Malignant Neurovestibular Dissociation & Aspiration Asphyxia",
                "severity": "CRITICAL",
                "etiology": f"Simultaneous angular deceleration ({cfg.angular_deceleration_deg_s2} deg/s^2) and G-drop induces severe canal-otolith illusion (illusory inversion/tumbling), triggering intractable nausea and projectile emesis in zero-g without restraint, risking airway occlusion."
            },
            {
                "risk_id": "ACR-02",
                "label": "Kinetic Impact & Blunt Force Polytrauma",
                "severity": "CRITICAL",
                "etiology": f"{cfg.crew_count} unstrapped crew members experiencing loss of centrifugal contact traction while residual angular velocity imparts tangential ejection trajectories toward bulkheads and non-padded avionics racks."
            },
            {
                "risk_id": "ACR-03",
                "label": "Acute Cephalad Venous Engorgement & Ocular Hypertensive Surge",
                "severity": "HIGH",
                "etiology": f"Sudden trans-diaphragmatic fluid shift exceeding +{cfg.fluid_shift_rate_ml_min} mL/min producing acute venous jugular retrograde surge, sudden spike in ICP (>24 mmHg), and risk of microvascular retinal hemorrhage."
            }
        ]

        primary_countermeasures = [
            {
                "priority": 1,
                "action_code": "DIRECTIVE_ALPHA_RESTRAINT_DAMPING",
                "title": "Immediate Magnetic Footwear / Harness Lock & Head Immobilization",
                "clinical_rationale": "Arrests ballistic free-float collisions before tangential angular momentum ejects crew. Cervical and head neutral alignment attenuates cross-coupled angular stimulation to the semicircular canals.",
                "execution_target": f"Crew (All {cfg.crew_count} Personnel)",
                "latency_tolerance_sec": 10,
                "status": "EXECUTED" if cfg.magnetic_deck_locked else "PENDING_ACTUATION"
            },
            {
                "priority": 2,
                "action_code": "DIRECTIVE_BRAVO_NEUROVESTIBULAR_PROPHYLAXIS",
                "title": "Autonomous Needle-Free Autoinjector / Intranasal Neurosuppressant Delivery",
                "clinical_rationale": "Suppresses central vestibular nucleus overactivation and emetic reflex arc using Promethazine (25 mg IM autoinjector) or Intranasal Scopolamine (0.4 mg) to eliminate microgravity emesis aspiration risk.",
                "execution_target": "Crew Medical Dispenser / Personal Bio-Suits",
                "latency_tolerance_sec": 45,
                "status": "DISPENSED" if cfg.countermeasures_active else "PRECHARGED_ARMED"
            },
            {
                "priority": 3,
                "action_code": "DIRECTIVE_CHARLIE_SPLANCHNIC_SEQUESTRATION",
                "title": "Rapid-Inflation Venous Restriction (Braslet Thigh Cuffs / Tactical LBNP)",
                "clinical_rationale": "Pneumatically sequesters 400-600 mL of displaced venous volume in lower limbs at 35-45 mmHg compression to blunt the acute CVP/ICP hypertensive spike and prevent intracranial capillary shearing.",
                "execution_target": "Smart-Garment Pneumatic Actuators",
                "latency_tolerance_sec": 60,
                "status": "INFLATED_ACTIVE" if cfg.countermeasures_active else "READY_FOR_COMPRESSION"
            }
        ]

        system_interventions = {
            "eclss_control_signals": {
                "cabin_lighting_state": "STROBE_SUPPRESSION_MODE (dim amber 2200K, 30 lux) to eliminate visual flicker and optic vestibular reinforcement",
                "ventilation_velocity_mps": 0.45,
                "cabin_airflow_vector": "FLOOR_TO_OVERHEAD_UNIDIRECTIONAL (clears particulate, fluid droplet, or vomitus dispersion from cabin atmosphere)",
                "suction_canisters_power": "ACTIVE_VACUUM_STANDBY_100_PCT"
            },
            "medical_dispenser_signals": {
                "station_id": "MED-RING-CORE-01",
                "dispense_order": [
                    {
                        "compound": "Promethazine Hydrochloride",
                        "dose": "25 mg",
                        "delivery_system": "Jet-Inject Jet-Port Port-A",
                        "target_crew_ids": [c[0] for c in roles[:cfg.crew_count]],
                        "status": "ADMINISTERED" if cfg.countermeasures_active else "ARMED_PENDING_PORT_DOCK"
                    },
                    {
                        "compound": "Scopolamine Intranasal Aerosol",
                        "dose": "0.4 mg",
                        "delivery_system": "Helmet Mucosal Mist Actuator",
                        "status": "DELIVERED" if cfg.countermeasures_active else "PRECHARGED"
                    }
                ]
            },
            "mechanical_and_hull_safing": {
                "bulkhead_pneumatic_arrestor_nets": "DEPLOYED_TANGENTIAL_ZONES_A_THROUGH_D",
                "electromagnetic_floor_deck_lock": "ENERGIZE_100_PCT (forces solenoid attraction on crew boots)" if cfg.magnetic_deck_locked else "DISENGAGED_READY",
                "spin_down_damper_torque_override": "COMMANDED_SYMMETRIC_REACTION_WHEEL_COUNTER_COUPLE"
            }
        }

        flight_surgeon_verdict = {
            "system_id": "AEGIS-DEEPSPACE-CORE-P4",
            "alert_classification": "RED_CRITICAL_EMERGENCY" if not cfg.countermeasures_active else "AMBER_POST_DESPIN_STABILIZED",
            "autonomous_authority_level": "LEVEL_5_AUTONOMOUS_INTERVENTION_OVERRIDE",
            "rationale": f"Governor loss induces an acute transition through high-gradient Coriolis shear ({cfg.angular_deceleration_deg_s2} deg/s^2) coupled with total loss of hydrostatic equilibrium over {cfg.duration_seconds}s. In the absence of immediate Earth comms (interplanetary latency), the Decision Engine has exercised autonomous authority to command electromagnetic deck lock, deploy pneumatic impact baffles, and prime needle-free antiemetics across all {cfg.crew_count} crew biosystems to prevent polytrauma and asphyxiation during despin stabilization.",
            "timestamp_utc": timestamp_now,
            "mission_control_telemetry_packet_dispatched": True
        }

        return CentrifugeSimulationResult(
            timestamp=timestamp_now,
            config=cfg,
            telemetry_deltas=telemetry_deltas,
            acute_clinical_risks=acute_clinical_risks,
            primary_countermeasures=primary_countermeasures,
            system_interventions=system_interventions,
            flight_surgeon_verdict=flight_surgeon_verdict,
            time_series=time_series,
            crew_roster=crew_roster
        )

    def convert_to_crew_state(self, sim_res: CentrifugeSimulationResult) -> CrewState:
        """Converts the acute despin state into a normalized CrewState for the Pillar 4 Decision Engine."""
        cfg = sim_res.config
        last_step = sim_res.time_series[-1]
        
        # In a despin event, crew cannot use normal exercise bays and are confined to zero-g safe modules
        rad_state = RadiationState(
            risk_level="MEDIUM",
            dose_rate_msv_h=0.04,
            cumulative_dose_msv=1.6,
            spe_active=False,
            current_module="Centrifugal Ring (Despun Module C)",
            recommended_safe_module="Core Hub Tether / Medical Bay",
            shielding_rating_g_cm2=14.0,
            confidence=0.98
        )

        # Voice vitals reflect severe cognitive strain, hyperventilation, and acute distress
        strain = 0.88 if not cfg.countermeasures_active else 0.45
        fatigue = 0.72 if not cfg.countermeasures_active else 0.52
        voice_state = VoiceVitalsState(
            fatigue_score=fatigue,
            cognitive_strain_score=strain,
            hypoxia_indicator=0.28,
            deviation_from_baseline_z=3.8 if not cfg.countermeasures_active else 1.9,
            confidence=0.94
        )

        # Astro-twin reflects immediate loss of 0.38g gravity loading and exercise disruption
        twin_state = AstroTwinState(
            projected_bone_loss_pct_mo=1.85,
            projected_muscle_atrophy_pct=3.4,
            exercise_deficit_days=2,
            countermeasure_status="CENTRIFUGE_DESPIN_CONTINGENCY",
            prediction_horizon_days=30,
            confidence=0.92
        )

        return CrewState(
            timestamp=sim_res.timestamp,
            comms_mode=CommsMode.OFFLINE,  # Autonomously handling acute crisis offline
            data_freshness_seconds=1,
            radiation=rad_state,
            voice_vitals=voice_state,
            astro_twin=twin_state
        )


# Global simulator instance
default_centrifuge_simulator = CentrifugeSimulator()
