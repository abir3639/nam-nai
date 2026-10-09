"""CLI and Server entrypoint for Aegis-DeepSpace Pillar 4 Autonomous Decision Engine MVP."""

import sys
import argparse
import uvicorn
from aegis_deepspace.decision_engine import AutonomousDecisionEngine
from aegis_deepspace.scenarios import DEMO_SCENARIOS

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def run_cli_demo():
    """Runs through each demo scenario in the terminal and prints the decision output."""
    engine = AutonomousDecisionEngine()
    print("=" * 80)
    print("        AEGIS-DEEPSPACE: PILLAR 4 AUTONOMOUS DECISION ENGINE (MVP)")
    print("       Synthesizing Radiation Safe-Route + Voice Vitals + Astro-Twin")
    print("=" * 80)
    print("NOTE: 100% Offline Clinical Decision Support for 20-min Comms Delay.\n")

    scenario_keys = [
        ("normal", "1. NOMINAL BASELINE"),
        ("solar_storm", "2. SOLAR STORM (SPE)"),
        ("voice_anomaly", "3. VOICE VITALS ANOMALY"),
        ("combined_anomaly", "4. COMBINED MULTIMODAL ANOMALY"),
        ("offline_blackout", "5. OFFLINE BLACKOUT (MARS COMM DELAY)"),
        ("uncertain_data", "6. UNCERTAIN / NOISY DATA")
    ]

    for key, title in scenario_keys:
        print("-" * 80)
        print(f"SCENARIO: {title}")
        print("-" * 80)
        state_func = DEMO_SCENARIOS[key]
        state = state_func()
        decision = engine.process(state)

        print(f"Mode:               {decision.mode.value}")
        print(f"Risk Level:         {decision.risk_level.value} (Score: {decision.risk_score:.2f})")
        print(f"System Confidence:  {int(decision.confidence * 100)}%")
        if decision.risk_fusion:
            rf = decision.risk_fusion
            print(f"Risk Fusion Math:   {rf.formula}")
            print(f"Pillars Breakdown:  [P1 Rad: +{rf.p1_radiation.score_addition:.2f} ({rf.p1_radiation.status})] "
                  f"[P2 Voice: +{rf.p2_voice_vitals.score_addition:.2f} ({rf.p2_voice_vitals.status})] "
                  f"[P3 Twin: +{rf.p3_astro_twin.score_addition:.2f} ({rf.p3_astro_twin.status})] "
                  f"[Synergy: +{rf.synergy_score:.2f}]")
        print(f"\nRECOMMENDED ACTION (DECISION SUPPORT):")
        print(f"  {decision.recommended_action}")
        if decision.alternative_action:
            print(f"ALTERNATIVE CONTINGENCY:\n  {decision.alternative_action}")

        print("\nEXPLAINABLE REASONS ('WHY'):")
        for r in decision.reasons:
            print(f"  * {r}")

        if decision.contributing_factors:
            print("\nCONTRIBUTING FACTORS:")
            for f in decision.contributing_factors:
                print(f"  [{f.pillar}] {f.factor} ({f.severity_contribution}) -> {f.detail}")

        if decision.uncertainty:
            print("\nUNCERTAINTIES & CAVEATS:")
            for u in decision.uncertainty:
                print(f"  [UNCERTAINTY] {u}")

        print("\nNASA EVIDENCE CITATIONS (OFFLINE):")
        for ev in decision.evidence:
            print(f"  [DOC: {ev.source}] {ev.title} ({ev.citation})")
        print("\n")


def start_server(host: str = "127.0.0.1", port: int = 8000):
    """Starts the FastAPI web server."""
    print(f"Starting Aegis-DeepSpace Flight Surgeon Dashboard on http://{host}:{port}")
    uvicorn.run("aegis_deepspace.server:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aegis-DeepSpace Pillar 4")
    parser.add_argument("--cli", action="store_true", help="Run terminal scenario demo")
    parser.add_argument("--serve", action="store_true", help="Start dashboard web server")
    parser.add_argument("--host", default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=8000, help="Port number")

    args = parser.parse_args()

    if args.cli:
        run_cli_demo()
    elif args.serve:
        start_server(args.host, args.port)
    else:
        # Default: run CLI demo then notify how to run server
        run_cli_demo()
        print("To start the interactive web dashboard, run:")
        print("  python run_demo.py --serve\n")
