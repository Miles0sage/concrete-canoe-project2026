#!/usr/bin/env python3
"""
NAU Concrete Canoe 2026 - ASCE Mix Design Compliance Checker
Checks mix design against ASCE 2026 requirements.
VPS-compatible. Exports JSON report.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "compliance"


# ASCE 2026 limits (from competition rules)
LIMITS = {
    "cement_to_cementitious_ratio": {"max": 0.40, "unit": "ratio"},
    "portland_plus_lime_pct": {"max": 40.0, "unit": "%"},
    "lime_content_pct": {"max": 5.0, "unit": "%"},
    "reinforcement_poa_pct": {"min": 40.0, "unit": "%"},
}


def check_compliance(
    cement_to_cementitious: float,
    portland_plus_lime_pct: float,
    lime_content_pct: float,
    reinforcement_poa_pct: float,
) -> Dict[str, Any]:
    """
    Check mix design against ASCE 2026 requirements.
    Returns compliance report dict.
    """
    checks = []

    # Cement-to-cementitious ≤ 0.40
    lim = LIMITS["cement_to_cementitious_ratio"]
    actual = cement_to_cementitious
    max_val = lim["max"]
    pass_val = actual <= max_val
    margin = ((max_val - actual) / max_val * 100) if max_val > 0 else 0
    checks.append({
        "requirement": "Cement-to-cementitious ratio ≤ 0.40",
        "actual": round(actual, 4),
        "limit": max_val,
        "unit": "ratio",
        "pass": pass_val,
        "margin_pct": round(margin, 1) if pass_val else None,
    })

    # Portland + lime ≤ 40%
    lim = LIMITS["portland_plus_lime_pct"]
    actual = portland_plus_lime_pct
    max_val = lim["max"]
    pass_val = actual <= max_val
    margin = ((max_val - actual) / max_val * 100) if max_val > 0 else 0
    checks.append({
        "requirement": "Portland cement + lime ≤ 40% by weight",
        "actual": round(actual, 2),
        "limit": max_val,
        "unit": "%",
        "pass": pass_val,
        "margin_pct": round(margin, 1) if pass_val else None,
    })

    # Lime ≤ 5%
    lim = LIMITS["lime_content_pct"]
    actual = lime_content_pct
    max_val = lim["max"]
    pass_val = actual <= max_val
    margin = ((max_val - actual) / max_val * 100) if max_val > 0 else 0
    checks.append({
        "requirement": "Lime content ≤ 5%",
        "actual": round(actual, 2),
        "limit": max_val,
        "unit": "%",
        "pass": pass_val,
        "margin_pct": round(margin, 1) if pass_val else None,
    })

    # POA ≥ 40%
    lim = LIMITS["reinforcement_poa_pct"]
    actual = reinforcement_poa_pct
    min_val = lim["min"]
    pass_val = actual >= min_val
    margin = ((actual - min_val) / min_val * 100) if min_val > 0 else 0
    checks.append({
        "requirement": "Reinforcement POA ≥ 40%",
        "actual": round(actual, 2),
        "limit": min_val,
        "unit": "%",
        "pass": pass_val,
        "margin_pct": round(margin, 1) if pass_val else None,
    })

    overall = all(c["pass"] for c in checks)

    return {
        "timestamp": datetime.now().isoformat(),
        "overall_pass": overall,
        "checks": checks,
        "input": {
            "cement_to_cementitious": cement_to_cementitious,
            "portland_plus_lime_pct": portland_plus_lime_pct,
            "lime_content_pct": lime_content_pct,
            "reinforcement_poa_pct": reinforcement_poa_pct,
        },
    }


def save_report(report: Dict[str, Any]) -> Path:
    """Save compliance report to JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    out_path = OUTPUT_DIR / f"compliance_report_{date_str}.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    return out_path


def main() -> int:
    # Example: default mix values (user should update from their Excel)
    # These can be overridden via CLI args or config file
    if len(sys.argv) >= 5:
        cement = float(sys.argv[1])
        portland_lime = float(sys.argv[2])
        lime = float(sys.argv[3])
        poa = float(sys.argv[4])
    else:
        # Default placeholder values
        cement = 0.35
        portland_lime = 35.0
        lime = 3.0
        poa = 42.0
        print("Using default values. Pass: cement_ratio portland_lime% lime% poa%")

    report = check_compliance(cement, portland_lime, lime, poa)

    print("ASCE 2026 Compliance Check")
    print("-" * 50)
    for c in report["checks"]:
        status = "✓ Pass" if c["pass"] else "✗ Fail"
        margin = f" (margin: {c['margin_pct']}%)" if c.get("margin_pct") is not None else ""
        print(f"{c['requirement']}: {c['actual']} {c['unit']} → {status}{margin}")
    print("-" * 50)
    print(f"Overall: {'PASS' if report['overall_pass'] else 'FAIL'}")

    out_path = save_report(report)
    print(f"Saved: {out_path}")
    return 0 if report["overall_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
