# Aegis-DeepSpace: Four-Pillar Deep-Space Health Architecture & Autonomous Decision Engine

Aegis-DeepSpace is an offline-capable crew health and habitat decision support system designed for deep-space exploration under 20-minute communication latency or total Earth blackout.

The system is architected across **four foundational pillars**:
1. **Pillar 1: Environmental Defense — Radiation Safe-Route** (**REAL IMPLEMENTATION**)
   - Spacecraft habitat topology graph (`networkx`)
   - Internal hull compartment dose calculation
   - Dijkstra pathfinding minimizing cumulative absorbed transit radiation
   - NASA DONKI Solar Particle Event (SEP/SPE) telemetry with offline fallback
2. **Pillar 2: Passive Biometrics — Voice Vitals** (**REAL IMPLEMENTATION**)
   - Acoustic prosody and 1D-CNN (MFCC-13) for fatigue and early hypoxia markers
   - Whisper STT (`tiny.en`) transcript extraction
   - DistilBERT sentiment classification for affective mood valence and cognitive strain
   - Personalized z-score drift tracking against baseline
3. **Pillar 3: Predictive Twin — Astro-Twin** (**REAL IMPLEMENTATION**)
   - Hybrid biomechanical Frost's Mechanostat ODE modeling microgravity bone mineral density (BMD) loss
   - Scikit-Learn Gradient Boosting Regressor (`models/astro_twin_residual_gbm.joblib`) trained on 180-day ISS ARED mission dataset
   - 30-day forward trajectory simulation comparing nominal vs shelter confinement/outage deconditioning
   - Compensatory countermeasure prescription: mechanical work deficit (kg), required volume surge (%), and specific ARED exercise load adjustments (barbell squat, deadlift)
4. **Pillar 4: Autonomous Decision Engine** (**REAL IMPLEMENTATION**)
   - Multimodal risk fusion synthesizing P1, P2, and P3
   - Synergy escalation & cross-pillar feedback loop detection
   - 100% offline edge execution citing local NASA standards (HRR, NTRS, LSDA)

---

## Target System Architecture

```
REAL P1 (Radiation Safe-Route) ─┐
REAL P2 (Voice Vitals)        ─┼─> P4 Fusion Engine (Offline AI Surgeon) ─> Mission Control Dashboard
REAL P3 (Astro-Twin)           ─┘
```

### Visual Data Flow:
$$\text{P1 (Real)} + \text{P2 (Real)} + \text{P3 (Real)} \xrightarrow{\text{Normalization}} \text{P4 (Fusion)} \rightarrow \text{Crew Risk / Explainable Actions}$$

### Implementation Status Matrix
| Pillar | Status | Core Technologies | Data Interface |
|---|---|---|---|
| **P1: Radiation Safe-Route** | **REAL** | NetworkX Graph, Dijkstra Routing, NASA DONKI API | `RadiationState` & `/api/pillar1/*` |
| **P2: Voice Vitals** | **REAL** | OpenAI Whisper STT, PyTorch MFCC-CNN, DistilBERT NLP | `VoiceVitalsState` & `/api/pillar2/*` |
| **P3: Astro-Twin** | **REAL** | Hybrid Mechanostat ODE, Scikit-Learn GBM, ARED Model | `AstroTwinState` & `/api/pillar3/*` |
| **P4: Autonomous Decision Engine** | **REAL** | Multimodal risk fusion, synergy rules, local NASA RAG | `DecisionObject` |

---

## Getting Started

### Prerequisites
- Python 3.10+
- Dependencies: `fastapi`, `uvicorn`, `pydantic`, `pytest`, `httpx`, `networkx`, `requests`

```bash
pip install fastapi uvicorn pydantic pytest httpx networkx requests
```

### Running the Terminal CLI Demo
Walk through all six pre-configured scenarios with full explainability:
```bash
python run_demo.py --cli
```

### Running the Interactive Web Dashboard
Start the local server and open your browser:
```bash
python run_demo.py --serve
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

- **Mission Control Dashboard**: Four-pillar overview cards, live telemetry stream, real-time risk fusion pipeline, and flight surgeon recommendations.
- **Dedicated Pillar Pages**:
  - **P1: Radiation Safe-Route**: Interactive habitat compartment exposure table, custom Dijkstra evacuation path recalculation, and DONKI space weather alert panel.
  - **P2: Voice Vitals**: Speech-to-text transcription via Whisper STT, sentiment/mood valence via DistilBERT, and acoustic fatigue/hypoxia analysis via 1D-CNN.
  - **P3: Astro-Twin**: 30-day forward BMD projection via Frost's Mechanostat ODE + Gradient Boosting residual ML model, and adaptive compensatory countermeasure prescription.
  - **P4: Decision Engine**: Mathematical fusion formulas, multi-signal synergy escalation rules, local offline NASA research evidence citations, and counterfactual What-If simulation.
- **Toggle Blackout**: Simulate losing Earth connection (20-min Mars delay) to demonstrate autonomous edge decision support.

---

## Demo Scenarios

1. **Nominal Baseline**: Nominal radiation, normal voice vitals, balanced digital twin $\rightarrow$ `LOW` Risk (`0.10`).
2. **Solar Storm (SPE)**: Solar Particle Event detected by Radiation Safe-Route; shelter recommendation $\rightarrow$ `HIGH` Risk (`0.55`).
3. **Voice Vitals Anomaly**: Passive vocal acoustic logs flag cognitive fatigue and strain $\rightarrow$ `MEDIUM` Risk (`0.35`).
4. **Combined Multimodal Anomaly**: Radiation flare + cognitive slowing + simulated exercise deficit (Synergy Escalation) $\rightarrow$ `CRITICAL` Risk (`0.99`).
5. **Offline Blackout (Mars 20m Delay)**: Earth comms severed; 100% autonomous edge decision citing ASCEND standards $\rightarrow$ `CRITICAL` Risk (`0.99`).
6. **Uncertain / Noisy Data**: Conflicting sensors & low SNR audio; surfaces uncertainty and requests observation $\rightarrow$ `MEDIUM` Risk (`0.40`).

---

## Running the Automated Test Suite

```bash
pytest aegis_deepspace/tests -v
```
All 24 automated unit and integration tests verify deterministic decision rules, real Pillar 1 pathfinding, synergy scoring, and REST endpoints.

---

## Disclaimer
*This project is a research prototype for clinical decision support under deep-space communication delays. It does NOT serve as a certified medical device or autonomous medical authority.*
