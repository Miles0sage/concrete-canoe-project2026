#!/usr/bin/env python3
"""
NAU ASCE Concrete Canoe 2026 — Uncertainty & Sensitivity Analysis
Monte Carlo simulation (1000 iterations) + tornado sensitivity diagram.
"""

import sys
import csv
import math
from pathlib import Path
from typing import Dict, List
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from calculations.concrete_canoe_calculator import (
    WATER_DENSITY_LB_PER_FT3,
    displacement_volume,
    metacentric_height_approx,
    bending_moment_uniform_load,
    section_modulus_rectangular,
    section_modulus_thin_shell,
    bending_stress_psi,
    safety_factor as calc_safety_factor,
)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG_DIR = PROJECT_ROOT / "reports" / "figures"
REPORT_DIR = PROJECT_ROOT / "reports"
DATA_DIR = PROJECT_ROOT / "data"
for d in [FIG_DIR, REPORT_DIR, DATA_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Baseline (Design A) ──
BASE = {
    "L": 192, "B": 32, "D": 17, "t": 0.5,
    "density": 60.0,
    "flexural": 1500.0,
    "paddler_wt": 175.0,
    "n_paddlers": 4,
    "cwp": 0.65,
}

# ── Uncertainty ranges ──
UNCERTAINTIES = {
    "density":    {"mean": 60.0,  "std": 3.0,   "label": "Concrete Density (PCF)", "pct": "±5%"},
    "thickness":  {"mean": 0.5,   "std": 0.05,  "label": "Wall Thickness (in)",    "pct": "±10%"},
    "flexural":   {"mean": 1500,  "std": 150,   "label": "Flexural Strength (psi)","pct": "±10%"},
    "paddler_wt": {"mean": 175,   "std": 15,    "label": "Paddler Weight (lbs)",   "pct": "±8.6%"},
}

N_ITERATIONS = 1000
np.random.seed(42)

MIN_FB = 6.0
MIN_GM = 6.0
MIN_SF = 2.0


def shell_weight(L, B, D, t, density):
    Lf, Bf, Df, tf = L/12, B/12, D/12, t/12
    bottom = (math.pi/4) * Lf * Bf
    sides = 2 * Lf * Df * 0.70
    return (bottom + sides) * tf * density


def run_single(density, thickness, flexural, paddler_wt):
    """Run one Monte Carlo iteration. Returns dict of metrics."""
    L, B, D = BASE["L"], BASE["B"], BASE["D"]
    Lf, Bf, Df, tf = L/12, B/12, D/12, thickness/12

    sw = shell_weight(L, B, D, thickness, density)
    rw = sw * 0.05
    canoe_wt = sw + rw + 3.0  # +finish
    crew = paddler_wt * BASE["n_paddlers"]
    loaded = canoe_wt + crew

    disp = loaded / WATER_DENSITY_LB_PER_FT3
    wp = Lf * Bf * BASE["cwp"]
    draft_ft = disp / wp if wp > 0 else 0
    fb_in = max(0, (Df - draft_ft) * 12)

    KB = draft_ft / 2
    BM = (Bf**2) / (12 * draft_ft) if draft_ft > 0 else 0
    KG = Df * 0.45
    gm_ft = KB + BM - KG
    gm_in = gm_ft * 12

    w_per_ft = loaded / Lf
    M_max = w_per_ft * Lf**2 / 8
    S = section_modulus_thin_shell(B, D, thickness)
    sigma = (M_max * 12) / S if S > 0 else 0
    sf = flexural / sigma if sigma > 0 else 0

    return {
        "canoe_wt": canoe_wt, "loaded_wt": loaded,
        "fb_in": fb_in, "gm_in": gm_in, "sf": sf,
        "fb_pass": fb_in >= MIN_FB,
        "gm_pass": gm_in >= MIN_GM,
        "sf_pass": sf >= MIN_SF,
        "all_pass": fb_in >= MIN_FB and gm_in >= MIN_GM and sf >= MIN_SF,
    }


# ═══════════════════════════════════════════════════════════════
# Monte Carlo
# ═══════════════════════════════════════════════════════════════
def run_monte_carlo():
    print("  Running Monte Carlo simulation (1000 iterations)...")
    samples = {
        "density": np.random.normal(60, 3, N_ITERATIONS),
        "thickness": np.random.normal(0.5, 0.05, N_ITERATIONS),
        "flexural": np.random.normal(1500, 150, N_ITERATIONS),
        "paddler_wt": np.random.normal(175, 15, N_ITERATIONS),
    }
    # Clip to physical bounds
    samples["density"] = np.clip(samples["density"], 45, 80)
    samples["thickness"] = np.clip(samples["thickness"], 0.25, 1.0)
    samples["flexural"] = np.clip(samples["flexural"], 800, 2500)
    samples["paddler_wt"] = np.clip(samples["paddler_wt"], 120, 250)

    results = []
    for i in range(N_ITERATIONS):
        r = run_single(
            samples["density"][i],
            samples["thickness"][i],
            samples["flexural"][i],
            samples["paddler_wt"][i],
        )
        results.append(r)

    weights = np.array([r["canoe_wt"] for r in results])
    freeboards = np.array([r["fb_in"] for r in results])
    gms = np.array([r["gm_in"] for r in results])
    sfs = np.array([r["sf"] for r in results])
    all_pass = np.array([r["all_pass"] for r in results])

    stats = {
        "weight": {"mean": np.mean(weights), "std": np.std(weights),
                    "p5": np.percentile(weights, 5), "p95": np.percentile(weights, 95),
                    "min": np.min(weights), "max": np.max(weights), "data": weights},
        "freeboard": {"mean": np.mean(freeboards), "std": np.std(freeboards),
                       "p5": np.percentile(freeboards, 5), "p95": np.percentile(freeboards, 95),
                       "min": np.min(freeboards), "max": np.max(freeboards), "data": freeboards},
        "gm": {"mean": np.mean(gms), "std": np.std(gms),
                "p5": np.percentile(gms, 5), "p95": np.percentile(gms, 95),
                "min": np.min(gms), "max": np.max(gms), "data": gms},
        "sf": {"mean": np.mean(sfs), "std": np.std(sfs),
               "p5": np.percentile(sfs, 5), "p95": np.percentile(sfs, 95),
               "min": np.min(sfs), "max": np.max(sfs), "data": sfs},
        "pass_rate": np.mean(all_pass) * 100,
        "fail_rate": (1 - np.mean(all_pass)) * 100,
        "n_fail": int(np.sum(~all_pass)),
    }
    print(f"  Pass rate: {stats['pass_rate']:.1f}% ({stats['n_fail']} failures in {N_ITERATIONS})")
    return stats, samples


# ═══════════════════════════════════════════════════════════════
# Uncertainty distribution plots
# ═══════════════════════════════════════════════════════════════
def plot_distributions(stats):
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f"Uncertainty Analysis — Monte Carlo ({N_ITERATIONS} iterations)\n"
                 f"Design A: 192\" × 32\" × 17\"",
                 fontsize=15, fontweight="bold", y=1.02)

    metrics = [
        ("weight", "Canoe Weight (lbs)", "Weight (lbs)", 237, "≤ 237 lbs target", True),
        ("freeboard", "Freeboard (in)", "Freeboard (in)", MIN_FB, f"≥ {MIN_FB}\" required", False),
        ("gm", "Metacentric Height GM (in)", "GM (in)", MIN_GM, f"≥ {MIN_GM}\" required", False),
        ("sf", "Safety Factor", "Safety Factor", MIN_SF, f"≥ {MIN_SF} required", False),
    ]

    for ax, (key, title, xlabel, threshold, thresh_label, invert) in zip(axes.flat, metrics):
        data = stats[key]["data"]
        s = stats[key]

        # Histogram
        n, bins, patches = ax.hist(data, bins=40, alpha=0.7, color="#2196F3",
                                    edgecolor="black", linewidth=0.5, density=True)

        # Color fail zone
        for patch, left_edge in zip(patches, bins[:-1]):
            if invert and left_edge > threshold:
                patch.set_facecolor("red")
                patch.set_alpha(0.5)
            elif not invert and left_edge + (bins[1]-bins[0]) < threshold:
                patch.set_facecolor("red")
                patch.set_alpha(0.5)

        # Threshold line
        ax.axvline(threshold, color="red", ls="--", lw=2, label=thresh_label)

        # Mean and 95% CI
        ax.axvline(s["mean"], color="green", ls="-", lw=2,
                   label=f'Mean: {s["mean"]:.1f}')
        ax.axvline(s["p5"], color="orange", ls=":", lw=1.5,
                   label=f'5th %ile: {s["p5"]:.1f}')
        ax.axvline(s["p95"], color="orange", ls=":", lw=1.5,
                   label=f'95th %ile: {s["p95"]:.1f}')

        # Shaded 95% CI
        ax.axvspan(s["p5"], s["p95"], alpha=0.08, color="green")

        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Density")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.2)

    plt.tight_layout()
    out = FIG_DIR / "uncertainty_distributions.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] {out.name}")


# ═══════════════════════════════════════════════════════════════
# Sensitivity (tornado diagram)
# ═══════════════════════════════════════════════════════════════
def run_sensitivity():
    """One-at-a-time sensitivity: vary each param ±1σ, measure impact on each output."""
    print("  Running sensitivity analysis...")
    baseline = run_single(60, 0.5, 1500, 175)
    params = [
        ("density", 60, 3),
        ("thickness", 0.5, 0.05),
        ("flexural", 1500, 150),
        ("paddler_wt", 175, 15),
    ]
    outputs = ["canoe_wt", "fb_in", "gm_in", "sf"]
    output_labels = ["Canoe Weight (lbs)", "Freeboard (in)", "GM (in)", "Safety Factor"]

    sensitivities = {}  # {output: [(param_label, low_val, high_val, baseline_val)]}
    for okey, olabel in zip(outputs, output_labels):
        sens = []
        for pname, pmean, pstd in params:
            kwargs_low = {"density": 60, "thickness": 0.5, "flexural": 1500, "paddler_wt": 175}
            kwargs_high = dict(kwargs_low)
            kwargs_low[pname] = pmean - pstd
            kwargs_high[pname] = pmean + pstd
            r_low = run_single(**kwargs_low)
            r_high = run_single(**kwargs_high)
            sens.append((UNCERTAINTIES[pname]["label"] + f" ({UNCERTAINTIES[pname]['pct']})",
                         r_low[okey], r_high[okey], baseline[okey]))
        sensitivities[olabel] = sens

    return sensitivities, baseline


def plot_tornado(sensitivities, baseline):
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Sensitivity Analysis — Tornado Diagrams\n"
                 "Impact of ±1σ Parameter Variation on Key Metrics",
                 fontsize=15, fontweight="bold", y=1.02)

    for ax, (olabel, sens) in zip(axes.flat, sensitivities.items()):
        # Sort by total swing
        sens_sorted = sorted(sens, key=lambda s: abs(s[2] - s[1]), reverse=True)

        labels = [s[0] for s in sens_sorted]
        lows = [s[1] for s in sens_sorted]
        highs = [s[2] for s in sens_sorted]
        base_val = sens_sorted[0][3]

        y_pos = np.arange(len(labels))

        # Bars from baseline
        for i, (lbl, lo, hi, bv) in enumerate(sens_sorted):
            ax.barh(i, hi - bv, left=bv, height=0.5, color="#4CAF50",
                    alpha=0.7, edgecolor="black", linewidth=0.5)
            ax.barh(i, lo - bv, left=bv, height=0.5, color="#F44336",
                    alpha=0.7, edgecolor="black", linewidth=0.5)
            ax.text(hi + (hi-lo)*0.05, i, f"{hi:.1f}", va="center", fontsize=8)
            ax.text(lo - (hi-lo)*0.05, i, f"{lo:.1f}", va="center",
                    fontsize=8, ha="right")

        ax.axvline(base_val, color="black", ls="-", lw=1.5)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_title(f"{olabel} (baseline: {base_val:.1f})", fontweight="bold", fontsize=11)
        ax.grid(True, axis="x", alpha=0.2)
        ax.invert_yaxis()

    plt.tight_layout()
    out = FIG_DIR / "sensitivity_tornado.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] {out.name}")


# ═══════════════════════════════════════════════════════════════
# Markdown report
# ═══════════════════════════════════════════════════════════════
def write_report(stats, sensitivities, baseline):
    pf = lambda v: "PASS ✓" if v else "FAIL ✗"
    md = f"""# Uncertainty & Sensitivity Analysis Report
## Design A: 192" × 32" × 17" — Monte Carlo Simulation

## 1. Methodology

**Monte Carlo Simulation** with {N_ITERATIONS} random iterations.

### Parameter Distributions (Normal)

| Parameter | Mean | Std Dev | Range (±1σ) | Uncertainty |
|-----------|------|---------|-------------|-------------|
"""
    for key, u in UNCERTAINTIES.items():
        md += f"| {u['label']} | {u['mean']} | {u['std']} | {u['mean']-u['std']:.2f} – {u['mean']+u['std']:.2f} | {u['pct']} |\n"

    md += f"""
## 2. Monte Carlo Results

### Statistical Summary

| Metric | Mean | Std Dev | 5th %ile | 95th %ile | Min | Max |
|--------|------|---------|----------|-----------|-----|-----|
| Canoe Weight (lbs) | {stats['weight']['mean']:.1f} | {stats['weight']['std']:.1f} | {stats['weight']['p5']:.1f} | {stats['weight']['p95']:.1f} | {stats['weight']['min']:.1f} | {stats['weight']['max']:.1f} |
| Freeboard (in) | {stats['freeboard']['mean']:.1f} | {stats['freeboard']['std']:.1f} | {stats['freeboard']['p5']:.1f} | {stats['freeboard']['p95']:.1f} | {stats['freeboard']['min']:.1f} | {stats['freeboard']['max']:.1f} |
| GM (in) | {stats['gm']['mean']:.1f} | {stats['gm']['std']:.1f} | {stats['gm']['p5']:.1f} | {stats['gm']['p95']:.1f} | {stats['gm']['min']:.1f} | {stats['gm']['max']:.1f} |
| Safety Factor | {stats['sf']['mean']:.1f} | {stats['sf']['std']:.1f} | {stats['sf']['p5']:.1f} | {stats['sf']['p95']:.1f} | {stats['sf']['min']:.1f} | {stats['sf']['max']:.1f} |

### Pass/Fail Analysis

- **Overall pass rate: {stats['pass_rate']:.1f}%**
- Failures: {stats['n_fail']} / {N_ITERATIONS} iterations
- Failure rate: {stats['fail_rate']:.1f}%

### 95% Confidence Intervals

| Metric | 95% CI | Requirement | Worst Case | Status |
|--------|--------|-------------|------------|--------|
| Weight | {stats['weight']['p5']:.1f} – {stats['weight']['p95']:.1f} lbs | ≤ 237 lbs | {stats['weight']['max']:.1f} lbs | {pf(stats['weight']['max'] <= 237)} |
| Freeboard | {stats['freeboard']['p5']:.1f} – {stats['freeboard']['p95']:.1f}" | ≥ 6" | {stats['freeboard']['min']:.1f}" | {pf(stats['freeboard']['min'] >= MIN_FB)} |
| GM | {stats['gm']['p5']:.1f} – {stats['gm']['p95']:.1f}" | ≥ 6" | {stats['gm']['min']:.1f}" | {pf(stats['gm']['min'] >= MIN_GM)} |
| Safety Factor | {stats['sf']['p5']:.1f} – {stats['sf']['p95']:.1f} | ≥ 2.0 | {stats['sf']['min']:.1f} | {pf(stats['sf']['min'] >= MIN_SF)} |

## 3. Sensitivity Analysis

The tornado diagrams show the impact of varying each parameter by ±1 standard deviation
on each output metric. Parameters are ranked by total impact (swing).

### Most Sensitive Parameters (by impact on weight)
"""
    for olabel, sens in sensitivities.items():
        md += f"\n**{olabel}:**\n"
        for plabel, lo, hi, bv in sorted(sens, key=lambda s: abs(s[2]-s[1]), reverse=True):
            md += f"- {plabel}: {lo:.1f} to {hi:.1f} (swing: {abs(hi-lo):.1f})\n"

    md += f"""
## 4. Risk Mitigation Strategies

1. **Concrete Density Control**: Use precise batching with calibrated scales.
   Impact: ±3 PCF causes ±{abs(stats['weight']['std']):.1f} lbs weight variation.

2. **Thickness QC**: Use spacer blocks at every 12" to maintain 0.5" ± 0.02".
   Tighter tolerance reduces weight and freeboard variability.

3. **Flexural Strength**: Cure for minimum 28 days; test cylinders at 7, 14, 28 days.
   Target f'r > 1650 psi for additional safety margin.

4. **Paddler Weight**: Weigh crew before competition; adjust ballast if needed.

## 5. Recommendations

- **Design A remains viable** with {stats['pass_rate']:.1f}% pass rate under uncertainty.
- Worst-case freeboard ({stats['freeboard']['min']:.1f}") {'exceeds' if stats['freeboard']['min'] >= MIN_FB else 'fails'} the 6" requirement.
- Consider Design B if risk tolerance is lower (wider safety margins).

## 6. Figures

- `figures/uncertainty_distributions.png` — Monte Carlo histograms
- `figures/sensitivity_tornado.png` — Tornado diagrams

---
*Generated by NAU ASCE Concrete Canoe Calculator — 2026*
"""
    out = REPORT_DIR / "uncertainty_analysis_report.md"
    out.write_text(md)
    print(f"  [OK] {out.name}")


def main():
    print("=" * 55)
    print("  PHASE 3: Uncertainty & Sensitivity Analysis")
    print("=" * 55)

    stats, samples = run_monte_carlo()
    plot_distributions(stats)

    sensitivities, baseline = run_sensitivity()
    plot_tornado(sensitivities, baseline)

    write_report(stats, sensitivities, baseline)

    # Export raw MC data
    out = DATA_DIR / "monte_carlo_results.csv"
    with open(out, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["iteration", "weight_lbs", "freeboard_in", "gm_in", "safety_factor"])
        for i in range(N_ITERATIONS):
            writer.writerow([i+1,
                             f"{stats['weight']['data'][i]:.2f}",
                             f"{stats['freeboard']['data'][i]:.2f}",
                             f"{stats['gm']['data'][i]:.2f}",
                             f"{stats['sf']['data'][i]:.2f}"])
    print(f"  [OK] {out.name}")

    print("\n  Phase 3 complete.")


if __name__ == "__main__":
    main()
