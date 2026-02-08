#!/usr/bin/env python3
"""
Quick verification: Does Canoe 1 (18' × 30" × 18", 276 lbs) pass all requirements?
Run: python3 scripts/verify_canoe1.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from calculations.concrete_canoe_calculator import run_complete_analysis

print("\n" + "=" * 70)
print("VERIFYING YOUR CANOE 1 FROM EXCEL")
print("=" * 70)

results = run_complete_analysis(
    hull_length_in=216.0,
    hull_beam_in=30.0,
    hull_depth_in=18.0,
    hull_thickness_in=0.5,
    concrete_weight_lbs=276.0,
    flexural_strength_psi=1500.0,
)

fb = results["freeboard"]["freeboard_in"]
gm = results["stability"]["GM_in"]
adeq = results["structural"]["is_adequate"]

print(f"\nFreeboard: {fb:.2f} inches (need ≥6.0) {'✓' if fb >= 6.0 else '✗'}")
print(f"Stability GM: {gm:.2f} inches (need ≥6.0) {'✓' if gm >= 6.0 else '✗'}")
print(f"Structural: {'✓ ADEQUATE' if adeq else '✗ INADEQUATE'}")

print("\n" + "=" * 70)
print("PROCEED TO SOLIDWORKS? ", end="")
if fb >= 6.0 and gm >= 6.0 and adeq:
    print("YES! ✓ All requirements met")
    print("\nNext: Generate SolidWorks spec sheet - see design/solidworks_specifications.md")
else:
    print("NOT YET - Run optimizer first")
    print("\nNext: python3 scripts/optimize_hull.py")
print("=" * 70 + "\n")
