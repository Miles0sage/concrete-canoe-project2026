#!/usr/bin/env python3
"""
NAU Concrete Canoe 2026 - Hull Analysis Comparison Runner
Runs analysis for three canoe variants and saves comparison to CSV.
VPS-compatible: no GUI, uses only stdlib + calculations module.
"""

import sys
import csv
from datetime import datetime
from pathlib import Path

# Add project root for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from calculations.concrete_canoe_calculator import run_complete_analysis
except ImportError:
    from concrete_canoe_calculator import run_complete_analysis


# Canoe variants: (length_in, beam_in, depth_in, weight_lbs)
VARIANTS = [
    ("Canoe 1", 18 * 12, 30, 18, 276),   # 18' × 30" × 18", 276 lbs
    ("Canoe 2", 18 * 12, 36, 18, 300),   # 18' × 36" × 18", 300 lbs
    ("Canoe 3", 16 * 12, 42, 18, 320),   # 16' × 42" × 18", 320 lbs
]

HULL_THICKNESS_IN = 0.5
FLEXURAL_STRENGTH_PSI = 1500


def run_comparison() -> list:
    """Run analysis for all variants, return list of result dicts."""
    rows = []
    for name, length, beam, depth, weight in VARIANTS:
        try:
            r = run_complete_analysis(
                hull_length_in=length,
                hull_beam_in=beam,
                hull_depth_in=depth,
                hull_thickness_in=HULL_THICKNESS_IN,
                concrete_weight_lbs=weight,
                flexural_strength_psi=FLEXURAL_STRENGTH_PSI,
            )
            rows.append({
                "name": name,
                "length_in": length,
                "beam_in": beam,
                "depth_in": depth,
                "weight_lbs": weight,
                "freeboard_in": round(r["freeboard"]["freeboard_in"], 2),
                "gm_in": round(r["stability"]["gm_in"], 2),
                "max_bm_lb_ft": round(r["structural"]["max_bending_moment_lb_ft"], 1),
                "safety_factor": round(r["structural"]["safety_factor"], 2),
                "pass": "Pass" if r["overall_pass"] else "Fail",
            })
        except Exception as e:
            rows.append({
                "name": name,
                "error": str(e),
                "pass": "Error",
            })
    return rows


def save_csv(rows: list, out_dir: Path) -> Path:
    """Save comparison to CSV. Returns output path."""
    out_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    out_path = out_dir / f"hull_comparison_{date_str}.csv"

    fieldnames = [
        "name", "length_in", "beam_in", "depth_in", "weight_lbs",
        "freeboard_in", "gm_in", "max_bm_lb_ft", "safety_factor", "pass",
    ]
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    return out_path


def main() -> int:
    print("NAU Concrete Canoe 2026 - Hull Comparison")
    print("-" * 50)

    rows = run_comparison()

    # Print table
    print(f"{'Variant':<10} {'Freeboard':>10} {'GM':>8} {'Max BM':>10} {'SF':>6} {'Status':>8}")
    print("-" * 56)
    for r in rows:
        if "error" in r:
            print(f"{r['name']:<10} ERROR: {r['error'][:30]}")
        else:
            print(f"{r['name']:<10} {r['freeboard_in']:>8.2f}in {r['gm_in']:>6.2f}in {r['max_bm_lb_ft']:>8.1f} {r['safety_factor']:>6.2f} {r['pass']:>8}")

    # Save
    out_dir = PROJECT_ROOT / "data" / "test_results"
    out_path = save_csv(rows, out_dir)
    print(f"\nSaved to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
