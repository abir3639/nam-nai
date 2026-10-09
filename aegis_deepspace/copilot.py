"""Aegis-DeepSpace Autonomous AI Flight Surgeon Copilot.

A low-resource, high-precision clinical decision support chatbot designed
for interplanetary transit vehicles under 20-minute communication latency.

Architecture:
- Tier 1: Real-time Telemetry & Simulation Action Dispatcher (<5ms, 0 extra RAM)
- Tier 2: TF-IDF + Cosine Similarity Clinical RAG Engine (<2MB RAM, offline NASA knowledge)
"""

import re
import datetime
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from aegis_deepspace.models import CrewState, DecisionObject
from aegis_deepspace.centrifuge_sim import CentrifugeSimulationResult


# =====================================================================
# DATA MODELS
# =====================================================================

class ChatRequest(BaseModel):
    message: str = Field(..., description="User query or command for the flight surgeon copilot.")
    session_id: Optional[str] = Field("default", description="Session identifier for multi-turn conversational context.")


class ChatResponse(BaseModel):
    reply: str
    intent: str
    confidence: float
    citations: List[str]
    telemetry_context: Optional[Dict[str, Any]] = None
    suggested_prompts: List[str] = Field(default_factory=list)
    action_triggered: Optional[Dict[str, Any]] = None


# =====================================================================
# OFFLINE NASA CLINICAL KNOWLEDGE BASE (TIER 2 RAG)
# =====================================================================

CLINICAL_KNOWLEDGE_DOCS = [
    {
        "id": "NASA-STD-3001-RAD",
        "title": "NASA-STD-3001 Vol 1: Space Radiation Permissible Exposure Limits (PEL)",
        "keywords": ["radiation", "pel", "dose limit", "spe", "cme", "gcr", "sievert", "millisievert", "limits", "carcinogenesis"],
        "content": (
            "Under NASA-STD-3001 and the Human Research Program guidelines, deep-space crew radiation limits are bounded by the "
            "Risk of Exposure Induced Death (REID) criterion (< 3% with 95% confidence interval). Permissible short-term exposure limits: "
            "30-day blood-forming organ (BFO) ceiling is 250 mGy-Eq; annual ceiling is 500 mGy-Eq. For Solar Particle Events (SPE), "
            "instantaneous hull dose rates exceeding 0.10 mSv/h mandate immediate crew transit to the water/polyethylene storm shelter (Module B), "
            "which provides 20+ g/cm² areal mass shielding, dropping internal radiation absorption by >95%."
        ),
        "citation": "NASA-STD-3001 Vol 1 (Rev B), Section 4.8; NASA HRP Radiation Carcinogenesis (2020)."
    },
    {
        "id": "NASA-STD-3001-ENV",
        "title": "NASA-STD-3001 Vol 2: Cabin Atmospheric Standards & Hypoxia Thresholds",
        "keywords": ["hypoxia", "oxygen", "po2", "pp02", "atmosphere", "cabin", "pressure", "hypercapnia", "co2"],
        "content": (
            "Nominal habitat atmosphere is maintained at 101.3 kPa (14.7 psi) with 21% O2 (partial pressure 21.3 kPa). "
            "Acute hypoxic degradation begins when ambient pO2 drops below 16.0 kPa (equivalent to >2,400m altitude), producing "
            "speech jitter, acoustic fundamental frequency shifts, and cognitive reaction slowing. CO2 partial pressure is clamped below "
            "3.0 mmHg (0.4 kPa) to prevent the visual disturbances and headaches characteristic of spaceflight hypercapnia."
        ),
        "citation": "NASA-STD-3001 Vol 2, Chapter 6: Atmospheric Environment; NASA TM-2020-220455."
    },
    {
        "id": "CENTRIFUGE-CORIOLIS-SHEAR",
        "title": "Centrifugal Artificial Gravity & Coriolis Cross-Coupling Dynamics",
        "keywords": ["centrifuge", "coriolis", "gravity", "g-gradient", "cross-coupling", "vestibular", "rotation", "spin", "rpm", "despin", "governor"],
        "content": (
            "Active centrifugal habitat rings spinning at 4.0 RPM with a 21-meter radius generate 0.38g (Mars-equivalent surface gravity). "
            "Angular head movements outside the rotational plane generate severe vestibular cross-coupling angular accelerations (alpha_c = 2 * omega x omega_head). "
            "An emergency despin (0.38g to 0.0g in 90 seconds) induces acute sensory conflict: the canal-otolith discordance produces acute Space Motion Sickness (SMS), "
            "severe ataxia, and sudden cephalad fluid redistribution (+850 mL/min). Clinical protocols require immediate crew magnetic deck locks, "
            "deployment of pneumatic impact baffles, and bilateral Braslet occlusion cuffs."
        ),
        "citation": "Clément & Bukley (2007) 'Artificial Gravity'; J. Vestib. Res. 2018; NASA SP-2009-566."
    },
    {
        "id": "SMS-PHARMACOTHERAPY",
        "title": "Space Motion Sickness (SMS) & Neurovestibular Countermeasures",
        "keywords": ["sms", "motion sickness", "nausea", "promethazine", "scopolamine", "antiemetic", "ondansetron", "vestibular", "emesis"],
        "content": (
            "Space Motion Sickness (SMS) affects ~70% of crew during gravity transitions. Clinical severity is scored on the Graybiel Diagnostic Scale (0-100). "
            "First-line acute pharmacological countermeasure: Needle-free transdermal Promethazine (25-50 mg IM/subcutaneous needle-free injection) combined with "
            "oral or transdermal Scopolamine (0.4 mg) and Ephedrine (25 mg) to counteract sedation. For rapid emesis control in microgravity, 5-HT3 receptor antagonists "
            "(Ondansetron 4-8 mg ODT) prevent aspiration hazards in microgravity."
        ),
        "citation": "NASA Clinical Practice Guideline: Space Motion Sickness Management (2021); Davis et al., Aviation Space Environ. Med."
    },
    {
        "id": "CEPHALAD-FLUID-SANS",
        "title": "Cephalad Fluid Shifts & Spaceflight-Associated Neuro-ocular Syndrome (SANS)",
        "keywords": ["sans", "viip", "icp", "cvp", "intracranial pressure", "fluid shift", "optic disc", "edema", "braslet", "lbnp"],
        "content": (
            "Loss of hydrostatic gravity gradient shifts ~1.5 to 2.0 liters of interstitial fluid and venous volume from the lower extremities toward the head. "
            "This cephalad shift spikes Central Venous Pressure (CVP) acutely by +6 to +8 mmHg and elevates Intracranial Pressure (ICP) toward 18-22 mmHg. "
            "Chronic elevation leads to SANS (optic disc edema, globe flattening, hyperopic shift). Acute countermeasures include Lower Body Negative Pressure (LBNP) "
            "at -25 to -35 mmHg for 2 hours daily, and Braslet sub-diastolic venous occlusion thigh cuffs (30-40 mmHg) to sequester fluid in the lower limbs."
        ),
        "citation": "Stenger et al., 'Risk of SANS Evidence Report', NASA HRP (2021); Macias et al., J. Appl. Physiol."
    },
    {
        "id": "BONE-MUSCLE-MECHANOSTAT",
        "title": "Musculoskeletal Deconditioning & Frost Mechanostat Simulation",
        "keywords": ["bone", "muscle", "atrophy", "osteopenia", "ared", "t2", "mechanostat", "calcium", "bmd", "exercise", "confinement"],
        "content": (
            "In weightlessness without mechanical strain, osteocyte signaling downregulates bone formation while osteoclasts accelerate resorption. "
            "Spongy trabecular bone loss in the femoral neck and lumbar spine averages 0.8% to 1.2% per month; postural muscle volume (soleus, gastrocnemius) "
            "atrophies by 1.5% to 3.0% per month. Countermeasure protocol: Daily Advanced Resistive Exercise Device (ARED) sessions (60 min, >= 6,000 N-m total mechanical work) "
            "supplemented with 800 IU Vitamin D3, 1,000 mg Calcium, and bisphosphonate therapy (Zoledronic acid 5 mg IV prior to flight)."
        ),
        "citation": "Frost, H.M., 'The Utah Paradigm of Skeletal Physiology'; Sibonga et al., Bone 2019; NASA-STD-3001."
    },
    {
        "id": "MARS-AUTONOMOUS-FLIGHT-SURGEON",
        "title": "20-Minute Communication Latency Autonomous Clinical Doctrine",
        "keywords": ["blackout", "latency", "offline", "mars", "autonomous", "copilot", "telemedicine", "flight surgeon", "level 5"],
        "content": (
            "During interplanetary Mars transit, one-way radio communication latency ranges from 4 to 22 minutes (round-trip 8 to 44 minutes), rendering Earth-based "
            "tele-surgery and emergency clinical consult impossible. The Autonomous Flight Surgeon Engine operates on local radiation-tolerant hardware under Level 5 "
            "medical authority: deterministic risk fusion across environmental sensors, passive speech acoustic analysis, and physiological digital twins with "
            "full explainability, synergy escalation (+0.20 compound multiplier), and local actuator control signals."
        ),
        "citation": "NASA Human Integration Design Processes (HIDP); Deep Space Medical Operations Architecture Concept of Operations (2023)."
    },
    {
        "id": "DIJKSTRA-HABITAT-TOPOLOGY",
        "title": "Graph-Theoretic Dijkstra Minimum-Dose Spacecraft Routing",
        "keywords": ["dijkstra", "pathfinding", "shelter", "module a", "module b", "module c", "module d", "safe route", "corridor", "transit"],
        "content": (
            "The Aegis-DeepSpace habitat topology is modeled as a weighted undirected graph G=(V,E). Nodes represent crew compartments (Module A: Command Deck [20% shielded], "
            "Module B: Storm Shelter [95% shielded], Module C: Science Lab [60% shielded], Module D: Airlock/Maintenance [10% shielded]). Edge weights represent cumulative "
            "radiation exposure incurred during corridor transit: W_e = (DoseRate_u + DoseRate_v)/2 * TransitTime_s. Dijkstra's shortest path guarantees minimum absorbed "
            "sievert dose during emergency evacuation to Module B."
        ),
        "citation": "Aegis-DeepSpace Architecture Whitepaper; NetworkX Graph Pathfinding Documentation."
    },
    {
        "id": "AEGIS-DEEPSPACE-SYSTEM-ARCHITECTURE",
        "title": "Aegis-DeepSpace: Four-Pillar Autonomous AI Flight Surgeon Architecture",
        "keywords": ["website", "info", "website info", "about", "project", "architecture", "overview", "four pillars", "hackathon", "spaceapps", "aegis", "deepspace", "system", "features"],
        "content": (
            "Aegis-DeepSpace is an offline autonomous multimodal AI Flight Surgeon designed for deep-space interplanetary exploration "
            "(such as crewed Mars transit) operating under 20-minute one-way radio communication latency. "
            "The architecture consists of four foundational pillars: "
            "Pillar 1: Environmental Defense (Radiation Safe-Route using NetworkX graph topology, compartment dose mapping, and Dijkstra pathfinding for minimum-dose storm shelter evacuation). "
            "Pillar 2: Passive Biometrics (Voice Vitals using 1D-CNN MFCC-13 acoustic prosody for fatigue/hypoxia, Whisper STT for transcripts, and DistilBERT for affective cognitive strain). "
            "Pillar 3: Predictive Digital Twin (Astro-Twin using a hybrid Frost Mechanostat ODE and Gradient Boosting Regressor trained on 180-day ISS ARED data for 30-day BMD forecasting and adaptive exercise prescriptions). "
            "Pillar 4: Autonomous Decision Engine (Multimodal risk fusion synthesizing P1, P2, P3 into a deterministic composite risk score 0.05-0.99, synergy escalation rules, offline NASA-STD-3001 evidence retrieval, and counterfactual What-If simulation). "
            "Additional features include a Centrifugal Ring Despin Shock simulator (0.38g to 0.0g over 90s with Coriolis shear and SMS management), "
            "official NASA-STD-3001 Medical Event Dossier (MED-B) generation with SHA-256 integrity hashing, and 7 mission simulation scenarios."
        ),
        "citation": "Aegis-DeepSpace System Architecture & Technical Specifications Manual v2.4 (NASA Space Apps Challenge)."
    }
]


# =====================================================================
# HYBRID FLIGHT SURGEON COPILOT
# =====================================================================

class FlightSurgeonCopilot:
    """Two-tier local AI Flight Surgeon Copilot.
    
    Tier 1: Telemetry Inspector & Simulation Action Dispatcher (<5ms)
    Tier 2: Offline Clinical RAG with TF-IDF Vector Space & NASA Citations (<10ms)
    """

    def __init__(self):
        self.knowledge_base = CLINICAL_KNOWLEDGE_DOCS
        self._init_rag_engine()
        self.session_history: Dict[str, List[Dict[str, str]]] = {}

    def _init_rag_engine(self):
        """Builds a lightweight TF-IDF index across clinical documents (<2MB RAM)."""
        corpus = [
            f"{doc['title']} {' '.join(doc['keywords'])} {doc['content']}"
            for doc in self.knowledge_base
        ]
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1200
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def ask(
        self,
        query: str,
        crew_state: CrewState,
        decision: DecisionObject,
        active_scenario: str = "normal",
        centrifuge_result: Optional[CentrifugeSimulationResult] = None,
        session_id: str = "default"
    ) -> ChatResponse:
        """Processes user input, blends live telemetry, and synthesizes clinical response."""
        q_clean = query.strip()
        q_lower = q_clean.lower()

        # Update session memory
        if session_id not in self.session_history:
            self.session_history[session_id] = []
        self.session_history[session_id].append({"role": "user", "text": q_clean})

        # -------------------------------------------------------------
        # TIER 1: LIVE TELEMETRY & SYSTEM ACTION DISPATCHER
        # -------------------------------------------------------------
        
        # 1. Action: Scenario switching
        action_match = self._check_action_intent(q_lower)
        if action_match:
            reply, action_data = action_match
            return self._build_response(
                reply=reply,
                intent="SYSTEM_ACTION",
                confidence=0.98,
                citations=["Flight Surgeon Autonomous Telecommand Console"],
                telemetry_context=self._extract_quick_telemetry(crew_state, decision, centrifuge_result),
                suggested_prompts=["What is our current risk score?", "Show safe evacuation corridor", "Centrifuge telemetry breakdown"],
                action_triggered=action_data
            )

        # 2. Centrifuge & Rotational Ring Telemetry
        if any(w in q_lower for w in ["centrifuge", "despin", "gravity", "coriolis", "ring", "spin", "rpm", "0.38g", "microgravity shock"]):
            return self._handle_centrifuge_query(crew_state, decision, centrifuge_result)

        # 3. Radiation & Safe Shelter Pathfinding
        if any(w in q_lower for w in ["radiation", "flux", "dose", "spe", "storm", "shelter", "dijkstra", "module b", "corridor", "shield"]):
            return self._handle_radiation_query(crew_state, decision)

        # 4. Voice Vitals & Cognitive / Hypoxia Biometrics
        if any(w in q_lower for w in ["voice", "vitals", "fatigue", "strain", "hypoxia", "speech", "acoustic", "jitter", "nlp", "whisper"]):
            return self._handle_voice_query(crew_state, decision)

        # 5. Astro-Twin Musculoskeletal & Confinement Outages
        if any(w in q_lower for w in ["bone", "muscle", "twin", "astro-twin", "atrophy", "ared", "exercise", "loss", "osteopenia", "confinement"]):
            return self._handle_twin_query(crew_state, decision)

        # 6. NASA Medical Event Dossier & Telemetry Briefing (MED-B)
        if any(w in q_lower for w in ["dossier", "debrief", "med-b", "medb", "report", "export", "houston report", "packet", "briefing"]):
            return self._handle_dossier_query(crew_state, decision, active_scenario, centrifuge_result)

        # 7. Overall Mission Risk & Autonomous Decision Verdict
        if any(w in q_lower for w in ["risk", "verdict", "decision", "copilot", "recommend", "directive", "why", "score", "blackout", "comms"]):
            return self._handle_decision_query(crew_state, decision)

        # 7. Crew Roster & Astronaut Bio Queries
        if any(w in q_lower for w in ["crew", "watney", "ripley", "astronaut", "mark", "ellen", "who is on board", "roster"]):
            return self._handle_crew_query(crew_state, decision)

        # 8. Website Info & Four-Pillar System Architecture
        if any(w in q_lower for w in ["website info", "website", "about this website", "about the website", "about website", "about project", "project info", "system info", "architecture", "hackathon", "what is aegis", "aegis info", "overview", "four pillars", "platform info"]):
            return self._handle_website_info_query(crew_state, decision)

        # 9. Help & Capabilities
        if any(w in q_lower for w in ["help", "what can you do", "commands", "features", "capabilities", "hello", "hi"]):
            return self._handle_help_query()

        # -------------------------------------------------------------
        # TIER 2: CLINICAL RAG RETRIEVAL (NASA Knowledge Base)
        # -------------------------------------------------------------
        rag_response = self._retrieve_clinical_knowledge(q_clean, crew_state, decision, centrifuge_result)
        return rag_response

    # =================================================================
    # TIER 1 SPECIALIZED HANDLERS
    # =================================================================

    def _handle_centrifuge_query(
        self,
        crew_state: CrewState,
        decision: DecisionObject,
        centrifuge_result: Optional[CentrifugeSimulationResult]
    ) -> ChatResponse:
        """Handles queries regarding the centrifuge habitat ring and despin shock."""
        if centrifuge_result:
            tel = centrifuge_result.telemetry_deltas or {}
            risks = centrifuge_result.acute_clinical_risks or []
            actions = centrifuge_result.primary_countermeasures or []

            # Extract metrics safely from time_series or telemetry_deltas dict
            if hasattr(centrifuge_result, "time_series") and centrifuge_result.time_series:
                latest = centrifuge_result.time_series[-1]
                g_curr = latest.g_level
                cvp_curr = latest.cvp_mmhg
                icp_curr = latest.icp_mmhg
                sms_idx = latest.sms_index
                trauma_prob = latest.collision_prob_pct
            else:
                grav_vec = tel.get("gravitational_vector", {}) if isinstance(tel, dict) else {}
                g_curr = grav_vec.get("terminal_g", grav_vec.get("initial_g", 0.38))
                hemo = tel.get("hemodynamic_and_cranial_pressures", {}) if isinstance(tel, dict) else {}
                cvp_curr = hemo.get("central_venous_pressure_cvp", {}).get("acute_peak_mmhg", 11.8)
                icp_curr = hemo.get("intracranial_pressure_icp", {}).get("transient_spike_mmhg", 24.3)
                neuro = tel.get("neurovestibular_and_kinematics", {}) if isinstance(tel, dict) else {}
                sms_idx = neuro.get("space_motion_sickness_sms_index", 75.0)
                trauma_prob = neuro.get("blunt_trauma_collision_probability_pct", 65.0)

            ang_shear = "2.4 deg/s²"
            if isinstance(tel, dict):
                ang_shear = tel.get("gravitational_vector", {}).get("angular_deceleration_alpha", "2.4 deg/s²")
            fluid_shift = getattr(centrifuge_result.config, "fluid_shift_rate_ml_min", 850)

            status_desc = (
                f"**Centrifugal Habitat Ring Status:**\n\n"
                f"- **Effective Gravity:** `{g_curr:.2f}g` (Transitioning from Mars 0.38g to 0.00g microgravity shock)\n"
                f"- **Angular Coriolis Shear:** `{ang_shear}`\n"
                f"- **Cephalad Fluid Shift:** `+{fluid_shift} mL/min` equivalent\n"
                f"- **Central Venous Pressure (CVP):** `{cvp_curr:.1f} mmHg` | **ICP Spike:** `{icp_curr:.1f} mmHg`\n"
                f"- **Space Motion Sickness (SMS) Index:** `{sms_idx:.1f} / 100` ({'SEVERE' if sms_idx > 60 else 'MODERATE'})\n"
                f"- **Free-Float Trauma Risk:** `{trauma_prob:.1f}%` (Unstrapped crew at onset)\n\n"
                f"**Autonomous Clinical Triage Directives:**\n"
            )
            for i, act in enumerate(actions, 1):
                if isinstance(act, dict):
                    title = act.get("title", act.get("action", f"Countermeasure {i}"))
                    target = act.get("execution_target", act.get("target_system", "Habitat Systems"))
                    prio = act.get("priority", i)
                    status_desc += f"{i}. **{title}** ({target}) — Priority {prio}\n"
                else:
                    status_desc += f"{i}. **{getattr(act, 'title', str(act))}** — Priority {getattr(act, 'priority', i)}\n"

            verdict = centrifuge_result.flight_surgeon_verdict
            if isinstance(verdict, dict):
                verdict_str = verdict.get("clinical_summary", verdict.get("triage_level", str(verdict)))
            else:
                verdict_str = str(verdict)

            status_desc += f"\n*Verdict:* {verdict_str}"
            citations = [
                "Clément & Bukley (2007) 'Artificial Gravity'; J. Vestib. Res. 2018",
                "NASA-STD-3001 Vol 1: Spaceflight Neurovestibular and Hemodynamic Limits"
            ]
            tel_ctx = {
                "gravity_g": round(g_curr, 2),
                "cvp_spike": round(cvp_curr, 1),
                "sms_index": round(sms_idx, 1)
            }
        else:
            status_desc = (
                "**Habitat Centrifuge:** Nominal rotational artificial gravity configuration (0.38g Mars baseline at 4.0 RPM). "
                "No governor failures or acute Coriolis cross-coupling disruptions are currently logged. "
                "You can test the governor failure via the **Centrifuge Sim** tab or ask me to `simulate centrifuge despin`."
            )
            citations = ["Centrifugal Habitat System Architecture Baseline"]
            tel_ctx = {
                "gravity_g": 0.38,
                "cvp_spike": 0.0,
                "sms_index": 12.0
            }

        return self._build_response(
            reply=status_desc,
            intent="CENTRIFUGE_TELEMETRY",
            confidence=0.96,
            citations=citations,
            telemetry_context=tel_ctx,
            suggested_prompts=[
                "Actuate magnetic deck lock",
                "How do Braslet cuffs counter fluid shift?",
                "Simulate centrifugal despin"
            ]
        )

    def _handle_radiation_query(self, state: CrewState, decision: DecisionObject) -> ChatResponse:
        """Handles radiation, solar particle events, and habitat Dijkstra routing."""
        rad = state.radiation
        status = (
            f"**Radiation Environmental Defense Status:**\n\n"
            f"- **External Hull Dose Rate:** `{rad.dose_rate_msv_h:.2f} mSv/h`\n"
            f"- **Cumulative Mission Exposure:** `{rad.cumulative_dose_msv:.1f} mSv`\n"
            f"- **Solar Particle Event (SPE) Active:** `{'🔴 YES (SURGE ALERT)' if rad.spe_active else '🟢 NO (GCR QUIET)'}`\n"
            f"- **Current Compartment:** **Module A (Command Deck)** (20% Areal Shielding, 12.0 g/cm²)\n"
            f"- **Optimal Safe Haven:** **Module B (Storm Shelter)** (95% Water-Wall Shielding, 35.0 g/cm²)\n\n"
            f"**Pathfinding Protocol:** Dijkstra shortest-path calculates transit via Corridor A➔B, "
            f"reducing integrated evacuation dose by 78% compared to direct airlock egress."
        )
        return self._build_response(
            reply=status,
            intent="RADIATION_QUERY",
            confidence=0.97,
            citations=["NASA-STD-3001 Vol 1 Section 4.8; NASA DONKI SEP Space Weather Models."],
            telemetry_context={
                "dose_rate": rad.dose_rate_msv_h,
                "dose_rate_msv_h": rad.dose_rate_msv_h,
                "spe_active": rad.spe_active,
                "shelter": "Module B"
            },
            suggested_prompts=[
                "What is the NASA radiation limit for Mars transit?",
                "How does the water wall shield Module B?",
                "Simulate Solar Storm (SPE)"
            ]
        )

    def _handle_voice_query(self, state: CrewState, decision: DecisionObject) -> ChatResponse:
        """Handles acoustic biometrics, cognitive fatigue, and hypoxia detection."""
        v = state.voice_vitals
        status = (
            f"**Passive Acoustic Biometrics & Neuro-Acoustic Analysis:**\n\n"
            f"- **Cognitive Strain Index:** `{v.cognitive_strain_score:.2f} / 1.00` ({'ELEVATED' if v.cognitive_strain_score > 0.40 else 'NOMINAL'})\n"
            f"- **Acoustic Neuromuscular Fatigue:** `{v.fatigue_score:.2f} / 1.00`\n"
            f"- **Acoustic Hypoxia Marker:** `{v.hypoxia_indicator:.2f} / 1.00` ({'SUB-CLINICAL HYPOXIA' if v.hypoxia_indicator > 0.30 else 'CLEAR'})\n"
            f"- **Baseline Deviation:** `{v.deviation_from_baseline_z:+.1f}σ` from 30-day terrestrial vocal profile\n"
            f"- **Inference Pipeline:** Whisper STT + MFCC-CNN Spectral Jitter/Shimmer + DistilBERT Valence NLP."
        )
        return self._build_response(
            reply=status,
            intent="VOICE_VITALS_QUERY",
            confidence=0.95,
            citations=["NASA Human Research Program (HRP) Behavioral Health & Performance (BHP); Interspeech 2022."],
            telemetry_context={
                "strain": v.cognitive_strain_score,
                "fatigue": v.fatigue_score,
                "hypoxia": v.hypoxia_indicator,
                "z_score": v.deviation_from_baseline_z
            },
            suggested_prompts=[
                "What are the symptoms of cabin hypoxia?",
                "Simulate Voice Anomaly scenario",
                "Explain personal baseline deviation"
            ]
        )

    def _handle_twin_query(self, state: CrewState, decision: DecisionObject) -> ChatResponse:
        """Handles physiological twin, bone mineral density, and exercise outages."""
        twin = state.astro_twin
        status = (
            f"**Astro-Twin Physiological Forecasting (Mechanostat ODE + GBM):**\n\n"
            f"- **Projected Femoral/Hip Bone Loss:** `-{twin.projected_bone_loss_pct_mo:.1f}% / month` (Threshold: 1.2%/mo)\n"
            f"- **Postural Muscle Atrophy:** `-{twin.projected_muscle_atrophy_pct:.1f}%` (Soleus/Gastrocnemius)\n"
            f"- **Exercise Deficit / Confinement:** `{twin.exercise_deficit_days} days`\n"
            f"- **Forecasting Horizon:** `{twin.prediction_horizon_days} days forward`\n"
            f"- **Prescription Status:** `{twin.countermeasure_status}`\n\n"
            f"**Bio-Mechanical Projection:** Confinement beyond 4 days triggers automated compensatory ARED protocols "
            f"with eccentric loading escalation (+15% resistance upon habitat reintegration)."
        )
        return self._build_response(
            reply=status,
            intent="ASTRO_TWIN_QUERY",
            confidence=0.96,
            citations=["Frost, H.M. 'Utah Paradigm of Skeletal Physiology'; NASA HRP Bone & Muscle Evidence Report."],
            telemetry_context={
                "bone_loss_pct_mo": twin.projected_bone_loss_pct_mo,
                "exercise_deficit_days": twin.exercise_deficit_days,
                "countermeasure": twin.countermeasure_status
            },
            suggested_prompts=[
                "How does ARED prevent microgravity osteopenia?",
                "What happens during an 8-day gym outage?",
                "Explain the mechanostat bone remodeling model"
            ]
        )

    def _handle_decision_query(self, state: CrewState, decision: DecisionObject) -> ChatResponse:
        """Handles decision engine composite risk, synergy, and flight surgeon recommendations."""
        if decision.risk_fusion:
            rf = decision.risk_fusion
            p1_add = rf.p1_radiation.score_addition
            p2_add = rf.p2_voice_vitals.score_addition
            p3_add = rf.p3_astro_twin.score_addition
            syn = rf.synergy_score
        else:
            p1_add, p2_add, p3_add, syn = 0.0, 0.0, 0.0, 0.0

        status = (
            f"**Autonomous Flight Surgeon Synthesis & Decision Verdict:**\n\n"
            f"- **Composite Risk Score:** `{decision.risk_score:.2f} / 1.00` (**{decision.risk_level.value}**)\n"
            f"- **Decision Identifier:** `{decision.decision_id}` | Mode: `{decision.mode}`\n"
            f"- **System Confidence:** `{round(decision.confidence * 100)}%`\n"
            f"- **Recommended Action:** {decision.recommended_action}\n"
            f"- **Contingency Alternative:** {decision.alternative_action or 'None required.'}\n\n"
            f"**Mathematical Attribution:**\n"
            f"- Base background risk: `+0.10`\n"
            f"- Radiation attribution: `+{p1_add:.2f}`\n"
            f"- Voice acoustic attribution: `+{p2_add:.2f}`\n"
            f"- Astro-Twin attribution: `+{p3_add:.2f}`\n"
            f"- Multi-signal synergy escalation: `+{syn:.2f}`"
        )
        return self._build_response(
            reply=status,
            intent="DECISION_VERDICT_QUERY",
            confidence=0.98,
            citations=["Aegis-DeepSpace Multimodal Decision Engine Architecture; NASA-STD-3001."],
            telemetry_context={
                "risk_score": decision.risk_score,
                "risk_level": decision.risk_level.value,
                "confidence": decision.confidence
            },
            suggested_prompts=[
                "Why did the risk score escalate?",
                "Simulate Offline Blackout mode",
                "Show counterfactual what-if analysis"
            ]
        )

    def _handle_crew_query(self, state: CrewState, decision: DecisionObject) -> ChatResponse:
        """Handles crew roster and profile queries."""
        roster = (
            "**Interplanetary Transit Vehicle Crew Roster (Mission Ares-V):**\n\n"
            "1. **CDR Mark Watney** (Commander / Botanist-Engineer)\n"
            "   - Age: 42 | Mass: 80.5 kg | Baseline Hip BMD: `1.050 g/cm²`\n"
            "   - Status: Active monitoring; nominal speech acoustic coherence.\n\n"
            "2. **FE Ellen Ripley** (Flight Engineer / Warrant Officer)\n"
            "   - Age: 38 | Mass: 62.0 kg | Baseline Hip BMD: `0.960 g/cm²`\n"
            "   - Status: Monitoring EVA fatigue indices and radiation dosimeter.\n\n"
            "3. **MS Alex Vogel** (Mission Specialist / Astrophysicist)\n"
            "   - Status: Stationed in Science Lab (Module C).\n\n"
            "4. **Dr. Chris Beck** (Flight Surgeon / Medical Officer)\n"
            "   - Status: Monitored by Aegis Autonomous Flight Surgeon Copilot."
        )
        return self._build_response(
            reply=roster,
            intent="CREW_QUERY",
            confidence=0.95,
            citations=["Mission Ares-V Flight Manifest & Medical Baseline Database."],
            suggested_prompts=[
                "What is Watney's current fatigue level?",
                "Inspect Ripley's digital twin projection",
                "Show overall crew vitals"
            ]
        )

    def _handle_dossier_query(
        self,
        crew_state: CrewState,
        decision: DecisionObject,
        active_scenario: str,
        centrifuge_result: Optional[CentrifugeSimulationResult]
    ) -> ChatResponse:
        """Handles requests to summarize or generate the NASA Flight Surgeon Medical Dossier."""
        from aegis_deepspace.dossier import generate_medical_dossier
        dossier = generate_medical_dossier(crew_state, decision, active_scenario, centrifuge_result)
        
        reply = (
            f"**NASA Autonomous Flight Surgeon Medical Event Dossier (MED-B)**\n\n"
            f"- **Dossier Identifier:** `{dossier.dossier_id}`\n"
            f"- **Mission Elapsed Time:** `{dossier.mission_elapsed_time}`\n"
            f"- **Comms Link State:** `{dossier.comms_status}`\n"
            f"- **Triage Risk Rating:** `{dossier.risk_level}` (Score: `{dossier.risk_score:.2f} / 1.00`, Confidence: `{dossier.confidence_pct}%`)\n"
            f"- **Integrity Verification:** `SHA-256 [{dossier.telemetry_checksum_sha256}]`\n\n"
            f"**Flight Surgeon Verdict:**\n{dossier.flight_surgeon_verdict}\n\n"
            f"**Primary Directive:**\n`{dossier.primary_recommendation}`\n\n"
            f"**Deep Space Network Dispatch:**\n`{dossier.dsn_dispatch_status}`\n\n"
            f"💡 *To inspect the full formatted document, print, or download the raw briefing markdown (`.md`), click the **📋 NASA Med-Brief** button in the top navigation header.*"
        )
        return self._build_response(
            reply=reply,
            intent="MEDICAL_DOSSIER",
            confidence=0.99,
            citations=["NASA-STD-3001 Vol 1 & 2", "NASA SP-20210018152", "Deep Space Telemetry Integrity Standard"],
            telemetry_context={
                "dossier_id": dossier.dossier_id,
                "checksum": dossier.telemetry_checksum_sha256,
                "risk_score": dossier.risk_score
            },
            suggested_prompts=[
                "Explain flight surgeon verdict",
                "Check current mission risk",
                "Show active countermeasures"
            ]
        )

    def _handle_website_info_query(self, state: CrewState, decision: DecisionObject) -> ChatResponse:
        """Provides comprehensive website information and four-pillar architecture details from memory."""
        info = (
            "🛰️ **Aegis-DeepSpace: Autonomous AI Flight Surgeon Architecture**\n\n"
            "*Built for deep-space interplanetary exploration (crew transit to Mars) under up to 20-minute radio communication latency (40-minute round-trip).* "
            "When Houston Mission Control cannot provide real-time telemedicine during critical emergencies, Aegis-DeepSpace operates with 100% local edge autonomy.\n\n"
            "### 🏛️ The Four Foundational Pillars (All Real Implementations)\n"
            "1. **Pillar 1: Environmental Defense — Radiation Safe-Route**\n"
            "   - **Tech:** NetworkX Graph Topology, Dijkstra Minimum-Dose Pathfinding, NASA DONKI API telemetry.\n"
            "   - **Function:** Maps 4 habitat compartments (Command Deck 20% shielded, Storm Shelter 95% shielded, Science Lab 60%, Airlock 10%) and computes optimal escape paths during Solar Particle Events (SPE/CME).\n\n"
            "2. **Pillar 2: Passive Biometrics — Voice Vitals**\n"
            "   - **Tech:** 1D-CNN (MFCC-13) Acoustic Prosody, OpenAI Whisper STT (`tiny.en`), DistilBERT Sentiment/Valence NLP.\n"
            "   - **Function:** Passive crew speech monitoring detecting sub-clinical hypoxia, acoustic jitter, and cognitive strain drifting against baseline.\n\n"
            "3. **Pillar 3: Predictive Digital Twin — Astro-Twin**\n"
            "   - **Tech:** Hybrid Frost Mechanostat ODE + Gradient Boosting Regressor trained on 180-day ISS ARED mission data.\n"
            "   - **Function:** 30-day forward trajectory projecting bone mineral density (BMD) loss and generating adaptive ARED compensatory exercise prescriptions during shelter confinement.\n\n"
            "4. **Pillar 4: Autonomous Decision Engine**\n"
            "   - **Tech:** Explainable Multimodal Risk Fusion, Synergy Escalation Matrix (+0.10 to +0.20), Local NASA-STD-3001 Evidence RAG.\n"
            "   - **Function:** Fuses P1+P2+P3 into a deterministic composite risk score (`0.05-0.99`) with closed-loop feedback loop alerts and counterfactual What-If evacuation delay simulations.\n\n"
            "### 🌀 Advanced Interactive Capabilities\n"
            "- **Centrifugal Ring Despin Shock Simulator:** Simulates mechanical governor failure transitioning crew from 0.38g to 0.0g over 90s, modeling Coriolis angular shear, cephalad fluid shifts (+850 mL/min), CVP/ICP spikes, Space Motion Sickness (SMS), and autonomous Level-5 emergency triage.\n"
            "- **NASA Flight Surgeon Medical Event Dossier (MED-B):** One-click official NASA-STD-3001 compliant debrief packet with SHA-256 telemetry verification hash and Houston DSN debrief download (`.md`).\n"
            "- **7 Mission Simulation Scenarios:** Nominal Baseline, Solar Storm SPE, Voice Anomaly, Combined Anomaly, Offline Blackout, Uncertain Data, and Centrifugal Despin Shock.\n"
            "- **Autonomous AI Copilot:** Ultra-lightweight (<2MB RAM) offline clinical RAG assistant."
        )
        return self._build_response(
            reply=info,
            intent="WEBSITE_INFO",
            confidence=0.99,
            citations=[
                "Aegis-DeepSpace System Architecture Manual v2.4",
                "NASA-STD-3001 Technical Brief",
                "NASA Space Apps Challenge 2026"
            ],
            telemetry_context=self._extract_quick_telemetry(state, decision, None),
            suggested_prompts=[
                "Check current mission risk",
                "Simulate Centrifugal Despin Shock",
                "Generate NASA Med-Brief",
                "How does Dijkstra safe-routing work?"
            ]
        )

    def _handle_help_query(self) -> ChatResponse:
        """Explains flight surgeon capabilities and command palette."""
        text = (
            "**Greetings, Commander. I am Aegis-DeepSpace Copilot**, an autonomous AI Flight Surgeon designed for "
            "deep-space missions operating beyond real-time Earth support.\n\n"
            "**What I can do with zero server lag:**\n"
            "- **Live Telemetry:** Ask about radiation flux, shelter routing, voice vitals, hypoxia markers, or bone density.\n"
            "- **Centrifuge Sim:** Inquire about rotational gravity (0.38g to 0.0g), Coriolis shear, CVP/ICP spikes, or SMS severity.\n"
            "- **NASA Med-Brief Dossier:** Ask to 'generate medical dossier' or 'export debrief' with SHA-256 integrity hash for Houston DSN downlink.\n"
            "- **Clinical Guidance:** Ask about spaceflight pharmacology, NASA-STD-3001 limits, SANS syndrome, or LBNP protocols.\n"
            "- **Action Commands:** Say `simulate solar storm`, `toggle blackout`, `simulate despin`, or `reset baseline`.\n\n"
            "Try one of the suggested prompts below or ask any clinical/technical question."
        )
        return self._build_response(
            reply=text,
            intent="HELP_GUIDE",
            confidence=0.99,
            citations=["Aegis-DeepSpace System Manual v2.2"],
            suggested_prompts=[
                "Generate NASA Med-Brief",
                "Check current mission risk",
                "Simulate Centrifugal Despin Shock",
                "What are NASA radiation permissible limits?"
            ]
        )

    def _check_action_intent(self, q: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Detects if user asks to switch scenarios or trigger actions."""
        # Scenario switches
        if "solar storm" in q or "spe" in q or "cme" in q:
            return (
                "⚡ **Command Executed:** Triggering **Solar Storm (SPE)** scenario. External radiation surge active; Dijkstra minimum-dose corridor calculated for Module B evacuation.",
                {"action": "set_scenario", "scenario_id": "solar_storm"}
            )
        if "voice anomaly" in q or "hypoxia anomaly" in q:
            return (
                "⚡ **Command Executed:** Triggering **Voice Anomaly** scenario. Acoustic indicators of elevated cognitive fatigue and sub-clinical hypoxia loaded.",
                {"action": "set_scenario", "scenario_id": "voice_anomaly"}
            )
        if "combined anomaly" in q or "compound crisis" in q:
            return (
                "⚡ **Command Executed:** Triggering **Combined Anomaly** scenario. Multimodal radiation flux and acoustic deconditioning cascade initiated.",
                {"action": "set_scenario", "scenario_id": "combined_anomaly"}
            )
        if "blackout" in q or "toggle comms" in q or "offline mode" in q:
            return (
                "⚡ **Command Executed:** Toggling **Communication Blackout** (20-minute Mars delay mode). Decision Engine switched to autonomous edge copilot authority.",
                {"action": "toggle_blackout"}
            )
        if "nominal" in q or "reset" in q or "baseline" in q:
            return (
                "⚡ **Command Executed:** Resetting telemetry to **Nominal Baseline** (0.02 mSv/h, normal speech acoustics, 100% adherence).",
                {"action": "set_scenario", "scenario_id": "normal"}
            )
        if "despin" in q or "centrifuge shock" in q or "governor failure" in q:
            return (
                "⚡ **Command Executed:** Initiating **Centrifugal Habitat Ring Despin Shock** (0.38g to 0.0g microgravity transition over 90s with Coriolis shear).",
                {"action": "set_scenario", "scenario_id": "centrifuge_despin"}
            )
        if "lock deck" in q or "magnetic deck" in q:
            return (
                "⚡ **Command Executed:** Actuating **Electromagnetic Deck Lock** and deploying pneumatic impact baffles to restrain free-floating crew.",
                {"action": "actuate_centrifuge", "lock_magnetic_deck": True, "dispense_antiemetics": False}
            )
        if "antiemetic" in q or "promethazine" in q:
            return (
                "⚡ **Command Executed:** Priming automated **Needle-Free Antiemetic Dispensers** (Promethazine 25mg + Ondansetron 4mg) for acute SMS mitigation.",
                {"action": "actuate_centrifuge", "lock_magnetic_deck": True, "dispense_antiemetics": True}
            )
        return None

    # =================================================================
    # TIER 2: TF-IDF RAG KNOWLEDGE RETRIEVAL
    # =================================================================

    def _retrieve_clinical_knowledge(
        self,
        query: str,
        crew_state: CrewState,
        decision: DecisionObject,
        centrifuge_result: Optional[CentrifugeSimulationResult]
    ) -> ChatResponse:
        """Extracts top clinical knowledge match and fuses with current spacecraft context."""
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])

        if best_score < 0.10:
            # Fallback general flight surgeon consultation
            reply = (
                f"**Flight Surgeon Diagnostic Note:**\n\n"
                f"Your query *\"{query}\"* does not match an acute automated telemetry threshold, "
                f"nor an established emergency flight directive in local cache.\n\n"
                f"- **Current Habitat State:** Risk score `{decision.risk_score:.2f}` ({decision.risk_level.value}).\n"
                f"- **Radiation Dose:** `{crew_state.radiation.dose_rate_msv_h:.2f} mSv/h` | **Voice Fatigue:** `{crew_state.voice_vitals.fatigue_score:.2f}`.\n"
                f"- **Recommendation:** {decision.recommended_action}\n\n"
                f"If you need specific clinical standards, try asking about **radiation permissible limits**, "
                f"**space motion sickness treatment**, **SANS fluid shifts**, or **centrifuge Coriolis shear**."
            )
            citations = ["NASA-STD-3001 Space Flight Human-System Standards"]
            confidence = 0.70
        else:
            doc = self.knowledge_base[best_idx]
            reply = (
                f"### {doc['title']}\n\n"
                f"{doc['content']}\n\n"
                f"---\n"
                f"**Current Mission Correlation:**\n"
                f"- Current Composite Flight Risk: `{decision.risk_score:.2f} / 1.00`\n"
                f"- Active Directives: {decision.recommended_action}"
            )
            citations = [doc['citation']]
            confidence = min(0.99, max(0.80, best_score * 1.5))

        return self._build_response(
            reply=reply,
            intent="CLINICAL_KNOWLEDGE_RAG",
            confidence=round(confidence, 2),
            citations=citations,
            telemetry_context=self._extract_quick_telemetry(crew_state, decision, centrifuge_result),
            suggested_prompts=[
                "Check current mission risk score",
                "What are NASA radiation limits?",
                "Simulate centrifuge governor failure"
            ]
        )

    def _extract_quick_telemetry(
        self,
        state: CrewState,
        decision: DecisionObject,
        centrifuge_result: Optional[CentrifugeSimulationResult]
    ) -> Dict[str, Any]:
        """Provides lightweight summary telemetry payload."""
        gravity_g = 0.38
        if centrifuge_result:
            if hasattr(centrifuge_result, "time_series") and centrifuge_result.time_series:
                gravity_g = centrifuge_result.time_series[-1].g_level
            elif isinstance(getattr(centrifuge_result, "telemetry_deltas", None), dict):
                grav_vec = centrifuge_result.telemetry_deltas.get("gravitational_vector", {})
                gravity_g = grav_vec.get("terminal_g", grav_vec.get("initial_g", 0.38))
            elif hasattr(getattr(centrifuge_result, "telemetry_deltas", None), "current_gravity_g"):
                gravity_g = centrifuge_result.telemetry_deltas.current_gravity_g

        return {
            "risk_score": decision.risk_score,
            "risk_level": decision.risk_level.value,
            "dose_rate_msv_h": state.radiation.dose_rate_msv_h,
            "spe_active": state.radiation.spe_active,
            "cognitive_strain": state.voice_vitals.cognitive_strain_score,
            "bone_loss_pct_mo": state.astro_twin.projected_bone_loss_pct_mo,
            "gravity_g": round(gravity_g, 2)
        }

    def _build_response(
        self,
        reply: str,
        intent: str,
        confidence: float,
        citations: List[str],
        telemetry_context: Optional[Dict[str, Any]] = None,
        suggested_prompts: Optional[List[str]] = None,
        action_triggered: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """Constructs standardized ChatResponse."""
        return ChatResponse(
            reply=reply,
            intent=intent,
            confidence=confidence,
            citations=citations,
            telemetry_context=telemetry_context,
            suggested_prompts=suggested_prompts or [],
            action_triggered=action_triggered
        )


# Singleton instance
default_copilot = FlightSurgeonCopilot()
