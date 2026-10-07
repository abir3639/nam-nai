# Aegis-DeepSpace: Pillar 4 Autonomous Decision Engine (Offline AI Flight Surgeon)

Aegis-DeepSpace is an offline-capable crew health and habitat decision support system designed for deep-space exploration under 20-minute communication latency or total Earth blackout.

This repository implements the **Autonomous Decision Engine (Pillar 4)**, synthesizing telemetry and alerts from:
1. **Pillar 1: Environmental Defense — Radiation Safe-Route** (SPE/CME flux, habitat module shielding topology)
2. **Pillar 2: Passive Biometrics — Voice Vitals** (Passive voice logs detecting fatigue, cognitive strain, and early hypoxia)
3. **Pillar 3: Predictive Twin — Astro-Twin** (Forward-simulated musculoskeletal deconditioning under shelter restrictions)

---

## Architecture: Multimodal Risk Fusion

```
P1: Radiation Safe-Route   +   P2: Voice Vitals   +   P3: Astro-Twin
                          │
                          ▼
            [ Autonomous Decision Engine (Pillar 4) ]
       - Normalization (Standardized CrewState)
       - Multimodal Risk Fusion & Synergy Escalation
       - Local Offline NASA Evidence (HRR, NTRS, LSDA)
       - Explainable Reasons ("Why") & Decision Support
                          │
                          ▼
      [ Flight Surgeon Decision Support Dashboard & CLI ]
```

### Risk Fusion Mathematical Trace
$$\text{Fused Risk Score} = \text{Base (0.10)} + \text{P1 Rad} + \text{P2 Voice} + \text{P3 Twin} + \text{Synergy}$$
- Categorized into: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
- Multi-signal synergy escalation: Simultaneous coincident anomalies elevate risk non-linearly.
- Closed-loop feedback: Radiation-enforced sheltering triggering Astro-Twin exercise deficits is flagged automatically.

---

## Getting Started

### Prerequisites
- Python 3.10+
- Dependencies: `fastapi`, `uvicorn`, `pydantic`, `pytest`, `httpx`

```bash
pip install fastapi uvicorn pydantic pytest httpx
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

- Click between the 6 scenario buttons to inspect real-time telemetry, risk fusion breakdown, reasons, and NASA research citations.
- Toggle the **BLACKOUT** button to simulate losing contact with Earth and observe edge autonomous decision mode.

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
All 17 automated unit and integration tests verify deterministic decision rules, synergy scoring, staleness penalties, and REST endpoints.

---

## Disclaimer
*This project is a hackathon/research prototype for clinical decision support under spaceflight communication delays. It does NOT serve as a certified medical device or autonomous medical authority.*
