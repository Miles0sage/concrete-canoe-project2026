#!/usr/bin/env python3
"""
NAU ASCE Concrete Canoe 2026 - 3 Alternative Hull Designs
Comprehensive analysis, visualization, and comparison.

Generates:
  - 5 publication-quality figures (300 DPI)
  - CSV data export
  - Markdown comparison report
  - Console summary table
"""

import sys
import os
import csv
import math
import traceback
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from calculations.concrete_canoe_calculator import (
    HullGeometry,
    run_complete_analysis,
    WATER_DENSITY_LB_PER_FT3,
    INCHES_PER_FOOT,
    displacement_volume,
    waterplane_approximation,
    draft_from_displacement,
    freeboard as calc_freeboard,
    metacentric_height_approx,
    safety_factor as calc_safety_factor,
)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ---------------------------------------------------------------------------
# Output directories
# ---------------------------------------------------------------------------
FIG_DIR = PROJECT_ROOT / "reports" / "figures"
DATA_DIR = PROJECT_ROOT / "data"
REPORT_DIR = PROJECT_ROOT / "reports"
for d in [FIG_DIR, DATA_DIR, REPORT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CONCRETE_DENSITY_PCF = 60.0       # lightweight concrete density
FLEXURAL_STRENGTH_PSI = 1500.0    # mix design flexural strength
WATERPLANE_CWP = 0.65             # realistic canoe hull waterplane coefficient
PADDLER_WEIGHT_LBS = 175.0        # per paddler
NUM_PADDLERS = 4
CREW_WEIGHT = PADDLER_WEIGHT_LBS * NUM_PADDLERS  # 700 lbs
REINFORCEMENT_WEIGHT_FRACTION = 0.05  # 5% of concrete weight
TARGET_WEIGHT_LBS = 237.0         # competition target

# ASCE compliance thresholds (competition rules)
MIN_FREEBOARD_IN = 6.0
MIN_GM_IN = 6.0
MIN_SAFETY_FACTOR = 2.0

# ---------------------------------------------------------------------------
# Design definitions
# ---------------------------------------------------------------------------
@dataclass
class DesignSpec:
    name: str
    label: str
    color: str
    length_in: float
    beam_in: float
    depth_in: float
    thickness_in: float
    description: str

DESIGNS = [
    DesignSpec(
        name="Design A",
        label="Optimal\n(Lightest)",
        color="#2196F3",   # blue
        length_in=192,
        beam_in=32,
        depth_in=17,
        thickness_in=0.5,
        description="Minimum weight while meeting all requirements",
    ),
    DesignSpec(
        name="Design B",
        label="Conservative\n(Safety Margin)",
        color="#4CAF50",   # green
        length_in=196,
        beam_in=34,
        depth_in=18,
        thickness_in=0.5,
        description="Extra safety margin on all requirements",
    ),
    DesignSpec(
        name="Design C",
        label="Traditional\n(Easy Build)",
        color="#FF9800",   # orange
        length_in=216,
        beam_in=36,
        depth_in=18,
        thickness_in=0.5,
        description="Standard proportions, easier construction",
    ),
]


# ---------------------------------------------------------------------------
# Helper: estimate concrete shell weight
# ---------------------------------------------------------------------------
def estimate_shell_weight(length_in, beam_in, depth_in, thickness_in,
                          density_pcf=CONCRETE_DENSITY_PCF):
    """
    Estimate concrete shell weight (lbs) using a simplified open-mold model.
    Shell = bottom + two sides, tapered at ends via a form factor.
    """
    L = length_in / 12.0  # ft
    B = beam_in / 12.0
    D = depth_in / 12.0
    t = thickness_in / 12.0

    # Bottom panel (elliptical planform ≈ π/4 * L * B)
    bottom_area = (math.pi / 4) * L * B
    # Two side panels (roughly rectangular, tapered ~0.7)
    side_area = 2 * L * D * 0.70
    total_area = bottom_area + side_area  # ft²
    volume_ft3 = total_area * t            # ft³
    weight = volume_ft3 * density_pcf
    return weight


# ---------------------------------------------------------------------------
# Run analysis for one design
# ---------------------------------------------------------------------------
def analyse_design(spec: DesignSpec) -> Dict[str, Any]:
    """Run full analysis for a single design spec."""
    # Weight estimate
    shell_wt = estimate_shell_weight(
        spec.length_in, spec.beam_in, spec.depth_in, spec.thickness_in
    )
    reinforcement_wt = shell_wt * REINFORCEMENT_WEIGHT_FRACTION
    total_canoe_wt = shell_wt + reinforcement_wt

    # Total loaded weight (canoe + crew)
    loaded_weight = total_canoe_wt + CREW_WEIGHT

    # Run calculator — pass canoe-only weight; calculator adds crew internally
    results = run_complete_analysis(
        hull_length_in=spec.length_in,
        hull_beam_in=spec.beam_in,
        hull_depth_in=spec.depth_in,
        hull_thickness_in=spec.thickness_in,
        concrete_weight_lbs=total_canoe_wt,
        flexural_strength_psi=FLEXURAL_STRENGTH_PSI,
        waterplane_form_factor=WATERPLANE_CWP,
        concrete_density_pcf=CONCRETE_DENSITY_PCF,
        crew_weight_lbs=CREW_WEIGHT,
    )

    fb_in = results["freeboard"]["freeboard_in"]
    gm_in = results["stability"]["gm_in"]
    sf = results["structural"]["safety_factor"]

    # ASCE compliance with competition thresholds
    fb_pass = fb_in >= MIN_FREEBOARD_IN
    gm_pass = gm_in >= MIN_GM_IN
    sf_pass = sf >= MIN_SAFETY_FACTOR
    all_pass = fb_pass and gm_pass and sf_pass

    # Maneuverability score (inverse of length-to-beam ratio, normalised)
    lb_ratio = spec.length_in / spec.beam_in
    maneuverability = max(0, min(1, 1.0 - (lb_ratio - 4.0) / 4.0))

    return {
        "spec": spec,
        "shell_weight_lbs": shell_wt,
        "reinforcement_weight_lbs": reinforcement_wt,
        "total_canoe_weight_lbs": total_canoe_wt,
        "loaded_weight_lbs": loaded_weight,
        "freeboard_in": fb_in,
        "draft_in": results["freeboard"]["draft_in"],
        "gm_in": gm_in,
        "safety_factor": sf,
        "bending_stress_psi": results["structural"]["bending_stress_psi"],
        "max_bm_lb_ft": results["structural"]["max_bending_moment_lb_ft"],
        "fb_pass": fb_pass,
        "gm_pass": gm_pass,
        "sf_pass": sf_pass,
        "all_pass": all_pass,
        "maneuverability": maneuverability,
        "raw_results": results,
    }


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 1 — Hull Profiles (Side View)
# ═══════════════════════════════════════════════════════════════════════════
def fig1_hull_profiles(analyses: List[Dict]) -> Path:
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Hull Profiles — Side View with Rocker Curve", fontsize=16,
                 fontweight="bold", y=1.02)

    for ax, a in zip(axes, analyses):
        sp = a["spec"]
        L = sp.length_in
        D = sp.depth_in
        draft = a["draft_in"]
        wt = a["total_canoe_weight_lbs"]
        color = sp.color

        x = np.linspace(0, L, 200)

        # Hull bottom with rocker (parabolic rise at ends)
        rocker_height = D * 0.08
        bottom = rocker_height * (2 * x / L - 1) ** 2

        # Gunwale (deck line)
        gunwale = np.full_like(x, D)

        # Waterline
        waterline_y = draft

        # Fill hull shell
        ax.fill_between(x, bottom, gunwale, alpha=0.20, color=color)
        ax.plot(x, bottom, color=color, lw=2.5, label="Hull bottom")
        ax.plot(x, gunwale, color=color, lw=2.0)

        # Inner surface (shell thickness)
        inner_bottom = bottom + sp.thickness_in
        inner_top = gunwale - sp.thickness_in
        ax.plot(x, inner_bottom, color=color, lw=1.0, ls="--", alpha=0.6)

        # Waterline
        ax.axhline(waterline_y, color="dodgerblue", ls="-.", lw=1.8,
                    label=f"Waterline ({waterline_y:.1f}\")")
        ax.fill_between(x, 0, np.minimum(waterline_y, bottom),
                        alpha=0.08, color="blue")

        # Paddler positions (4 paddlers, evenly spaced in middle 60%)
        paddler_xs = np.linspace(L * 0.20, L * 0.80, NUM_PADDLERS)
        for px in paddler_xs:
            ax.plot(px, D + 1.5, "ro", ms=8, zorder=5)
            ax.plot([px, px], [D, D + 1.0], "r-", lw=1.5)

        # Dimension annotations
        ax.annotate("", xy=(0, -2), xytext=(L, -2),
                     arrowprops=dict(arrowstyle="<->", color="black", lw=1.2))
        ax.text(L / 2, -3.5, f"L = {L:.0f}\"", ha="center", fontsize=10,
                fontweight="bold")

        ax.annotate("", xy=(L + 3, 0), xytext=(L + 3, D),
                     arrowprops=dict(arrowstyle="<->", color="black", lw=1.2))
        ax.text(L + 7, D / 2, f"D = {D:.0f}\"", ha="left", fontsize=10,
                fontweight="bold", rotation=90, va="center")

        ax.set_title(f"{sp.name}: {sp.label.replace(chr(10), ' ')}\n"
                     f"Weight: {wt:.0f} lbs",
                     fontsize=12, fontweight="bold", color=color)
        ax.set_xlabel("Length (inches)")
        ax.set_ylabel("Depth (inches)")
        ax.set_xlim(-10, L + 15)
        ax.set_ylim(-6, D + 8)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.25)
        ax.legend(fontsize=8, loc="upper left")

    plt.tight_layout()
    out = FIG_DIR / "3_designs_profiles.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] Figure 1 saved: {out}")
    return out


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 2 — Midship Cross-Sections
# ═══════════════════════════════════════════════════════════════════════════
def fig2_cross_sections(analyses: List[Dict]) -> Path:
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("Midship Cross-Sections — V-Bottom Profile", fontsize=16,
                 fontweight="bold", y=1.02)

    for ax, a in zip(axes, analyses):
        sp = a["spec"]
        B = sp.beam_in
        D = sp.depth_in
        t = sp.thickness_in
        draft = a["draft_in"]
        color = sp.color

        # V-bottom angle
        deadrise = D * 0.25  # V depth

        # Outer shell vertices
        outer_x = np.array([-B/2, -B/2, 0, B/2, B/2])
        outer_y = np.array([D, 0, -deadrise, 0, D])

        # Inner shell vertices
        inner_x = np.array([-(B/2 - t), -(B/2 - t), 0, (B/2 - t), (B/2 - t)])
        inner_y = np.array([D - t, t, -deadrise + t, t, D - t])

        # Fill shell (between outer and inner)
        from matplotlib.patches import Polygon
        from matplotlib.collections import PatchCollection

        # Outer fill
        outer_poly = plt.Polygon(np.column_stack([outer_x, outer_y]),
                                  closed=True, facecolor=color, alpha=0.3,
                                  edgecolor=color, lw=2.5)
        ax.add_patch(outer_poly)

        # Inner void
        inner_poly = plt.Polygon(np.column_stack([inner_x, inner_y]),
                                  closed=True, facecolor="white", alpha=1.0,
                                  edgecolor=color, lw=1.2, ls="--")
        ax.add_patch(inner_poly)

        # Waterline
        wl_y = draft - deadrise  # relative to keel
        ax.axhline(wl_y, color="dodgerblue", ls="-.", lw=2.0,
                    label=f"Waterline", zorder=3)

        # Water fill below waterline
        water_x = np.linspace(-B/2, B/2, 100)
        water_bottom = np.interp(water_x, outer_x, outer_y)
        water_top = np.full_like(water_x, wl_y)
        mask = water_bottom < wl_y
        ax.fill_between(water_x[mask], water_bottom[mask],
                        np.minimum(water_top[mask], water_bottom[mask] + (wl_y - water_bottom[mask])),
                        alpha=0.15, color="blue")

        # Thickness annotation
        ax.annotate("", xy=(B/2 + 1, 0), xytext=(B/2 + 1 + t * 8, 0),
                     arrowprops=dict(arrowstyle="<->", color="red", lw=1.5))
        ax.text(B/2 + 2 + t * 4, 1.5, f"t = {t}\"", color="red",
                fontsize=10, fontweight="bold")

        # Beam annotation
        ax.annotate("", xy=(-B/2, D + 2), xytext=(B/2, D + 2),
                     arrowprops=dict(arrowstyle="<->", color="black", lw=1.2))
        ax.text(0, D + 3.5, f"B = {B:.0f}\"", ha="center", fontsize=10,
                fontweight="bold")

        # Depth annotation
        ax.annotate("", xy=(-B/2 - 3, -deadrise), xytext=(-B/2 - 3, D),
                     arrowprops=dict(arrowstyle="<->", color="black", lw=1.2))
        ax.text(-B/2 - 5, D / 2 - deadrise / 2, f"D = {D:.0f}\"",
                ha="right", fontsize=10, fontweight="bold", rotation=90,
                va="center")

        ax.set_title(f"{sp.name}: {sp.label.replace(chr(10), ' ')}",
                     fontsize=12, fontweight="bold", color=color)
        ax.set_xlim(-B/2 - 10, B/2 + 10)
        ax.set_ylim(-deadrise - 5, D + 8)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.25)
        ax.legend(fontsize=9, loc="upper left")
        ax.set_xlabel("Width (inches)")
        ax.set_ylabel("Height (inches)")

    plt.tight_layout()
    out = FIG_DIR / "3_designs_cross_sections.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] Figure 2 saved: {out}")
    return out


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 3 — Performance Bar Charts (2×2)
# ═══════════════════════════════════════════════════════════════════════════
def fig3_performance_bars(analyses: List[Dict]) -> Path:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Design Performance Comparison", fontsize=16,
                 fontweight="bold", y=1.01)

    names = [a["spec"].name for a in analyses]
    colors = [a["spec"].color for a in analyses]
    x = np.arange(len(names))
    bar_w = 0.55

    # --- Weight ---
    ax = axes[0, 0]
    weights = [a["total_canoe_weight_lbs"] for a in analyses]
    bars = ax.bar(x, weights, bar_w, color=colors, alpha=0.85, edgecolor="black",
                  linewidth=0.8)
    ax.axhline(TARGET_WEIGHT_LBS, color="red", ls="--", lw=2,
               label=f"Target: {TARGET_WEIGHT_LBS} lbs")
    for bar, val in zip(bars, weights):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                f"{val:.0f}", ha="center", va="bottom", fontweight="bold",
                fontsize=11)
    ax.set_ylabel("Weight (lbs)", fontsize=12)
    ax.set_title("Canoe Weight", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=11)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    # --- Freeboard ---
    ax = axes[0, 1]
    freeboards = [a["freeboard_in"] for a in analyses]
    bars = ax.bar(x, freeboards, bar_w, color=colors, alpha=0.85,
                  edgecolor="black", linewidth=0.8)
    ax.axhline(MIN_FREEBOARD_IN, color="red", ls="--", lw=2,
               label=f"Min Required: {MIN_FREEBOARD_IN}\"")
    for bar, val in zip(bars, freeboards):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                f"{val:.1f}\"", ha="center", va="bottom", fontweight="bold",
                fontsize=11)
    ax.set_ylabel("Freeboard (inches)", fontsize=12)
    ax.set_title("Freeboard", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=11)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    # --- GM ---
    ax = axes[1, 0]
    gms = [a["gm_in"] for a in analyses]
    bars = ax.bar(x, gms, bar_w, color=colors, alpha=0.85, edgecolor="black",
                  linewidth=0.8)
    ax.axhline(MIN_GM_IN, color="red", ls="--", lw=2,
               label=f"Min Required: {MIN_GM_IN}\"")
    for bar, val in zip(bars, gms):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                f"{val:.1f}\"", ha="center", va="bottom", fontweight="bold",
                fontsize=11)
    ax.set_ylabel("Metacentric Height GM (inches)", fontsize=12)
    ax.set_title("Stability (GM)", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=11)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    # --- Safety Factor ---
    ax = axes[1, 1]
    sfs = [a["safety_factor"] for a in analyses]
    bars = ax.bar(x, sfs, bar_w, color=colors, alpha=0.85, edgecolor="black",
                  linewidth=0.8)
    ax.axhline(MIN_SAFETY_FACTOR, color="red", ls="--", lw=2,
               label=f"Min Required: {MIN_SAFETY_FACTOR}")
    for bar, val in zip(bars, sfs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                f"{val:.2f}", ha="center", va="bottom", fontweight="bold",
                fontsize=11)
    ax.set_ylabel("Safety Factor", fontsize=12)
    ax.set_title("Structural Safety Factor", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=11)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    out = FIG_DIR / "3_designs_performance.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] Figure 3 saved: {out}")
    return out


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 4 — Radar Chart
# ═══════════════════════════════════════════════════════════════════════════
def fig4_radar(analyses: List[Dict]) -> Path:
    categories = ["Weight\n(lighter=better)", "Freeboard", "Stability\n(GM)",
                   "Safety\nFactor", "Maneuverability"]
    N = len(categories)

    # Normalise each metric to 0-1 (higher = better)
    all_weights = [a["total_canoe_weight_lbs"] for a in analyses]
    all_fb = [a["freeboard_in"] for a in analyses]
    all_gm = [a["gm_in"] for a in analyses]
    all_sf = [a["safety_factor"] for a in analyses]
    all_man = [a["maneuverability"] for a in analyses]

    def norm(vals, invert=False):
        mn, mx = min(vals), max(vals)
        rng = mx - mn if mx != mn else 1
        out = [(v - mn) / rng for v in vals]
        if invert:
            out = [1 - o for o in out]
        # Scale 0.2-1.0 for visibility
        return [0.2 + 0.8 * o for o in out]

    norm_wt = norm(all_weights, invert=True)  # lighter is better
    norm_fb = norm(all_fb)
    norm_gm = norm(all_gm)
    norm_sf = norm(all_sf)
    norm_man = norm(all_man)

    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]  # close polygon

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
    fig.suptitle("Design Comparison — Radar Chart", fontsize=16,
                 fontweight="bold", y=1.02)

    for i, a in enumerate(analyses):
        values = [norm_wt[i], norm_fb[i], norm_gm[i], norm_sf[i], norm_man[i]]
        values += values[:1]
        ax.plot(angles, values, "o-", linewidth=2.5, label=a["spec"].name,
                color=a["spec"].color, markersize=7)
        ax.fill(angles, values, alpha=0.12, color=a["spec"].color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11, fontweight="bold")
    ax.set_ylim(0, 1.15)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=9)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=12)
    ax.grid(True, alpha=0.3)

    out = FIG_DIR / "3_designs_radar.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] Figure 4 saved: {out}")
    return out


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 5 — Summary Table
# ═══════════════════════════════════════════════════════════════════════════
def fig5_summary_table(analyses: List[Dict]) -> Path:
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.axis("off")
    fig.suptitle("Design Comparison — Summary Table", fontsize=18,
                 fontweight="bold", y=0.97)

    # Find recommended design (lightest that passes all)
    passing = [a for a in analyses if a["all_pass"]]
    if passing:
        recommended = min(passing, key=lambda a: a["total_canoe_weight_lbs"])
    else:
        recommended = min(analyses, key=lambda a: a["total_canoe_weight_lbs"])

    col_labels = ["Metric", "Requirement"]
    for a in analyses:
        tag = " ★" if a["spec"].name == recommended["spec"].name else ""
        col_labels.append(f"{a['spec'].name}{tag}")

    rows_data = [
        ["Length (in)", "—",
         *[f"{a['spec'].length_in:.0f}" for a in analyses]],
        ["Beam (in)", "—",
         *[f"{a['spec'].beam_in:.0f}" for a in analyses]],
        ["Depth (in)", "—",
         *[f"{a['spec'].depth_in:.0f}" for a in analyses]],
        ["Thickness (in)", "—",
         *[f"{a['spec'].thickness_in}" for a in analyses]],
        ["Shell Weight (lbs)", f"≤ {TARGET_WEIGHT_LBS:.0f}",
         *[f"{a['shell_weight_lbs']:.1f}" for a in analyses]],
        ["Total Weight (lbs)", f"≤ {TARGET_WEIGHT_LBS:.0f}",
         *[f"{a['total_canoe_weight_lbs']:.1f}" for a in analyses]],
        ["Freeboard (in)", f"≥ {MIN_FREEBOARD_IN:.0f}\"",
         *[f"{a['freeboard_in']:.1f}  {'✓' if a['fb_pass'] else '✗'}"
           for a in analyses]],
        ["GM (in)", f"≥ {MIN_GM_IN:.0f}\"",
         *[f"{a['gm_in']:.1f}  {'✓' if a['gm_pass'] else '✗'}"
           for a in analyses]],
        ["Safety Factor", f"≥ {MIN_SAFETY_FACTOR:.1f}",
         *[f"{a['safety_factor']:.2f}  {'✓' if a['sf_pass'] else '✗'}"
           for a in analyses]],
        ["Draft (in)", "—",
         *[f"{a['draft_in']:.1f}" for a in analyses]],
        ["Bending Stress (psi)", "—",
         *[f"{a['bending_stress_psi']:.0f}" for a in analyses]],
        ["OVERALL", "ALL PASS",
         *[("PASS ✓" if a["all_pass"] else "FAIL ✗") for a in analyses]],
    ]

    table = ax.table(
        cellText=rows_data,
        colLabels=col_labels,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.0, 1.8)

    # Style header row
    for j in range(len(col_labels)):
        cell = table[0, j]
        cell.set_facecolor("#333333")
        cell.set_text_props(color="white", fontweight="bold", fontsize=12)

    # Color-code design columns
    for col_idx, a in enumerate(analyses, start=2):
        color = a["spec"].color
        for row_idx in range(1, len(rows_data) + 1):
            cell = table[row_idx, col_idx]
            cell.set_facecolor(color + "18")  # very light tint
            text = cell.get_text().get_text()
            if "✗" in text:
                cell.set_text_props(color="red", fontweight="bold")
            elif "✓" in text or "PASS" in text:
                cell.set_text_props(color="green", fontweight="bold")

    # Highlight recommended row
    rec_idx = next(i for i, a in enumerate(analyses)
                   if a["spec"].name == recommended["spec"].name)
    for row_idx in range(1, len(rows_data) + 1):
        cell = table[row_idx, rec_idx + 2]
        existing = cell.get_facecolor()
        cell.set_edgecolor(recommended["spec"].color)
        cell.set_linewidth(2)

    # Overall row highlight
    for j in range(len(col_labels)):
        cell = table[len(rows_data), j]
        cell.set_facecolor("#F5F5F5")
        cell.set_text_props(fontweight="bold", fontsize=12)

    # Metric column style
    for row_idx in range(1, len(rows_data) + 1):
        table[row_idx, 0].set_text_props(fontweight="bold")
        table[row_idx, 0].set_facecolor("#F0F0F0")
        table[row_idx, 1].set_facecolor("#FFF8E1")

    # Recommendation note
    ax.text(0.5, -0.02,
            f"★ Recommended: {recommended['spec'].name} — "
            f"{recommended['spec'].description}",
            ha="center", fontsize=13, fontweight="bold",
            color=recommended["spec"].color,
            transform=ax.transAxes)

    plt.tight_layout()
    out = FIG_DIR / "3_designs_summary_table.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] Figure 5 saved: {out}")
    return out


# ═══════════════════════════════════════════════════════════════════════════
# CSV Export
# ═══════════════════════════════════════════════════════════════════════════
def export_csv(analyses: List[Dict]) -> Path:
    out = DATA_DIR / "3_alternative_designs_comparison.csv"
    fields = [
        "design", "length_in", "beam_in", "depth_in", "thickness_in",
        "shell_weight_lbs", "total_weight_lbs", "loaded_weight_lbs",
        "freeboard_in", "gm_in", "safety_factor", "draft_in",
        "bending_stress_psi", "fb_pass", "gm_pass", "sf_pass", "all_pass",
    ]
    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for a in analyses:
            writer.writerow({
                "design": a["spec"].name,
                "length_in": a["spec"].length_in,
                "beam_in": a["spec"].beam_in,
                "depth_in": a["spec"].depth_in,
                "thickness_in": a["spec"].thickness_in,
                "shell_weight_lbs": round(a["shell_weight_lbs"], 2),
                "total_weight_lbs": round(a["total_canoe_weight_lbs"], 2),
                "loaded_weight_lbs": round(a["loaded_weight_lbs"], 2),
                "freeboard_in": round(a["freeboard_in"], 2),
                "gm_in": round(a["gm_in"], 2),
                "safety_factor": round(a["safety_factor"], 4),
                "draft_in": round(a["draft_in"], 2),
                "bending_stress_psi": round(a["bending_stress_psi"], 2),
                "fb_pass": a["fb_pass"],
                "gm_pass": a["gm_pass"],
                "sf_pass": a["sf_pass"],
                "all_pass": a["all_pass"],
            })
    print(f"  [OK] CSV saved: {out}")
    return out


# ═══════════════════════════════════════════════════════════════════════════
# Markdown Report
# ═══════════════════════════════════════════════════════════════════════════
def generate_report(analyses: List[Dict]) -> Path:
    # Find recommended
    passing = [a for a in analyses if a["all_pass"]]
    if passing:
        rec = min(passing, key=lambda a: a["total_canoe_weight_lbs"])
    else:
        rec = min(analyses, key=lambda a: a["total_canoe_weight_lbs"])

    lines = []
    lines.append("# NAU ASCE Concrete Canoe 2026 — 3 Alternative Designs Comparison")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"Three hull designs were analysed for the 2026 ASCE Concrete Canoe Competition. "
                 f"Each design uses **{CONCRETE_DENSITY_PCF:.0f} PCF lightweight concrete** with "
                 f"**{FLEXURAL_STRENGTH_PSI:.0f} psi flexural strength** and **0.5\" wall thickness**.")
    lines.append("")
    lines.append(f"Loading condition: canoe shell + {NUM_PADDLERS} paddlers "
                 f"@ {PADDLER_WEIGHT_LBS:.0f} lbs each ({CREW_WEIGHT:.0f} lbs total crew).")
    lines.append("")
    n_pass = sum(1 for a in analyses if a["all_pass"])
    lines.append(f"**Result: {n_pass} of 3 designs pass all ASCE compliance checks.**")
    lines.append(f"**Recommended: {rec['spec'].name}** — {rec['spec'].description}")
    lines.append("")

    # Compliance requirements
    lines.append("## ASCE Compliance Requirements")
    lines.append("")
    lines.append(f"| Metric | Requirement |")
    lines.append(f"|--------|-------------|")
    lines.append(f"| Freeboard | >= {MIN_FREEBOARD_IN:.0f} inches |")
    lines.append(f"| Metacentric Height (GM) | >= {MIN_GM_IN:.0f} inches |")
    lines.append(f"| Safety Factor | >= {MIN_SAFETY_FACTOR:.1f} |")
    lines.append(f"| Target Weight | <= {TARGET_WEIGHT_LBS:.0f} lbs |")
    lines.append("")

    # Detailed comparison table
    lines.append("## Detailed Comparison")
    lines.append("")
    header = "| Metric | " + " | ".join(a["spec"].name for a in analyses) + " |"
    sep = "|--------|" + "|".join(["--------"] * len(analyses)) + "|"
    lines.append(header)
    lines.append(sep)

    def pf(val):
        return "PASS" if val else "FAIL"

    rows = [
        ("Length (in)", [f"{a['spec'].length_in:.0f}" for a in analyses]),
        ("Beam (in)", [f"{a['spec'].beam_in:.0f}" for a in analyses]),
        ("Depth (in)", [f"{a['spec'].depth_in:.0f}" for a in analyses]),
        ("Thickness (in)", [f"{a['spec'].thickness_in}" for a in analyses]),
        ("Shell Weight (lbs)", [f"{a['shell_weight_lbs']:.1f}" for a in analyses]),
        ("Total Canoe Weight (lbs)", [f"{a['total_canoe_weight_lbs']:.1f}" for a in analyses]),
        ("Loaded Weight (lbs)", [f"{a['loaded_weight_lbs']:.1f}" for a in analyses]),
        ("Draft (in)", [f"{a['draft_in']:.1f}" for a in analyses]),
        ("Freeboard (in)", [f"{a['freeboard_in']:.1f} {pf(a['fb_pass'])}" for a in analyses]),
        ("GM (in)", [f"{a['gm_in']:.1f} {pf(a['gm_pass'])}" for a in analyses]),
        ("Safety Factor", [f"{a['safety_factor']:.2f} {pf(a['sf_pass'])}" for a in analyses]),
        ("Bending Stress (psi)", [f"{a['bending_stress_psi']:.0f}" for a in analyses]),
        ("**OVERALL**", [f"**{pf(a['all_pass'])}**" for a in analyses]),
    ]
    for label, vals in rows:
        lines.append(f"| {label} | " + " | ".join(vals) + " |")
    lines.append("")

    # Pros / Cons
    lines.append("## Design Analysis")
    lines.append("")

    pros_cons = {
        "Design A": {
            "pros": [
                "Lightest design — best for competition weight scoring",
                "Smallest footprint — easier to transport and store",
                "Most efficient use of materials",
            ],
            "cons": [
                "Tightest margins on stability and freeboard",
                "Less forgiving of construction variations",
                "Narrower beam may reduce paddler comfort",
            ],
        },
        "Design B": {
            "pros": [
                "Good balance of weight and safety margin",
                "Wider beam provides comfortable paddling",
                "Extra freeboard for rough water conditions",
            ],
            "cons": [
                "Slightly heavier than Design A",
                "May be over-engineered if conditions are calm",
                "Moderate material usage",
            ],
        },
        "Design C": {
            "pros": [
                "Standard proportions simplify construction",
                "Maximum stability and freeboard",
                "Most forgiving of construction tolerances",
                "Best for teams with less building experience",
            ],
            "cons": [
                "Heaviest design — worst weight score",
                "Largest material requirements",
                "Longer hull harder to transport",
                "Reduced maneuverability due to length",
            ],
        },
    }

    for a in analyses:
        name = a["spec"].name
        lines.append(f"### {name}: {a['spec'].label.replace(chr(10), ' ')}")
        lines.append(f"*{a['spec'].description}*")
        lines.append("")
        lines.append("**Pros:**")
        for p in pros_cons[name]["pros"]:
            lines.append(f"- {p}")
        lines.append("")
        lines.append("**Cons:**")
        for c in pros_cons[name]["cons"]:
            lines.append(f"- {c}")
        lines.append("")

    # Recommendation
    lines.append("## Recommendation")
    lines.append("")
    lines.append(f"**{rec['spec'].name}** is the recommended design.")
    lines.append("")
    lines.append(f"- Weight: **{rec['total_canoe_weight_lbs']:.1f} lbs** "
                 f"(target: {TARGET_WEIGHT_LBS} lbs)")
    lines.append(f"- Freeboard: **{rec['freeboard_in']:.1f}\"** "
                 f"(requirement: >= {MIN_FREEBOARD_IN}\")")
    lines.append(f"- GM: **{rec['gm_in']:.1f}\"** "
                 f"(requirement: >= {MIN_GM_IN}\")")
    lines.append(f"- Safety Factor: **{rec['safety_factor']:.2f}** "
                 f"(requirement: >= {MIN_SAFETY_FACTOR})")
    lines.append("")

    # Figures
    lines.append("## Figures")
    lines.append("")
    lines.append("| # | Figure | File |")
    lines.append("|---|--------|------|")
    lines.append("| 1 | Hull Profiles (Side View) | `figures/3_designs_profiles.png` |")
    lines.append("| 2 | Midship Cross-Sections | `figures/3_designs_cross_sections.png` |")
    lines.append("| 3 | Performance Bar Charts | `figures/3_designs_performance.png` |")
    lines.append("| 4 | Radar Comparison | `figures/3_designs_radar.png` |")
    lines.append("| 5 | Summary Table | `figures/3_designs_summary_table.png` |")
    lines.append("")
    lines.append("---")
    lines.append(f"*Generated by NAU ASCE Concrete Canoe Calculator — 2026*")

    out = REPORT_DIR / "3_designs_comparison_report.md"
    out.write_text("\n".join(lines))
    print(f"  [OK] Report saved: {out}")
    return out


# ═══════════════════════════════════════════════════════════════════════════
# Console output
# ═══════════════════════════════════════════════════════════════════════════
def print_console_summary(analyses: List[Dict]):
    passing = [a for a in analyses if a["all_pass"]]
    if passing:
        rec = min(passing, key=lambda a: a["total_canoe_weight_lbs"])
    else:
        rec = min(analyses, key=lambda a: a["total_canoe_weight_lbs"])

    W = 90
    print("\n" + "=" * W)
    print("  NAU ASCE CONCRETE CANOE 2026 — 3 ALTERNATIVE DESIGNS COMPARISON")
    print("=" * W)
    print(f"  Loading: {NUM_PADDLERS} paddlers @ {PADDLER_WEIGHT_LBS:.0f} lbs = "
          f"{CREW_WEIGHT:.0f} lbs crew | Concrete: {CONCRETE_DENSITY_PCF:.0f} PCF | "
          f"f'r = {FLEXURAL_STRENGTH_PSI:.0f} psi")
    print("-" * W)

    # Header
    hdr = f"{'Metric':<28}"
    for a in analyses:
        tag = " ★" if a["spec"].name == rec["spec"].name else ""
        hdr += f"{a['spec'].name + tag:>18}"
    hdr += f"{'Requirement':>16}"
    print(hdr)
    print("-" * W)

    def pf_sym(val):
        return "  ✓" if val else "  ✗"

    metrics = [
        ("Length (in)", [f"{a['spec'].length_in:.0f}" for a in analyses], "—"),
        ("Beam (in)", [f"{a['spec'].beam_in:.0f}" for a in analyses], "—"),
        ("Depth (in)", [f"{a['spec'].depth_in:.0f}" for a in analyses], "—"),
        ("Shell Weight (lbs)", [f"{a['shell_weight_lbs']:.1f}" for a in analyses],
         f"<= {TARGET_WEIGHT_LBS:.0f}"),
        ("Total Weight (lbs)", [f"{a['total_canoe_weight_lbs']:.1f}" for a in analyses],
         f"<= {TARGET_WEIGHT_LBS:.0f}"),
        ("Draft (in)", [f"{a['draft_in']:.1f}" for a in analyses], "—"),
        ("Freeboard (in)", [f"{a['freeboard_in']:.1f}{pf_sym(a['fb_pass'])}" for a in analyses],
         f">= {MIN_FREEBOARD_IN:.0f}"),
        ("GM (in)", [f"{a['gm_in']:.1f}{pf_sym(a['gm_pass'])}" for a in analyses],
         f">= {MIN_GM_IN:.0f}"),
        ("Safety Factor", [f"{a['safety_factor']:.2f}{pf_sym(a['sf_pass'])}" for a in analyses],
         f">= {MIN_SAFETY_FACTOR:.1f}"),
        ("Bending Stress (psi)", [f"{a['bending_stress_psi']:.0f}" for a in analyses], "—"),
    ]

    for label, vals, req in metrics:
        row = f"  {label:<26}"
        for v in vals:
            row += f"{v:>18}"
        row += f"{req:>16}"
        print(row)

    print("-" * W)
    overall_row = f"  {'OVERALL':<26}"
    for a in analyses:
        status = "PASS ✓" if a["all_pass"] else "FAIL ✗"
        overall_row += f"{status:>18}"
    overall_row += f"{'ALL PASS':>16}"
    print(overall_row)
    print("=" * W)
    print(f"\n  ★ RECOMMENDED: {rec['spec'].name} — {rec['spec'].description}")
    print(f"    Weight: {rec['total_canoe_weight_lbs']:.1f} lbs | "
          f"Freeboard: {rec['freeboard_in']:.1f}\" | "
          f"GM: {rec['gm_in']:.1f}\" | "
          f"SF: {rec['safety_factor']:.2f}")
    print("=" * W + "\n")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
def main():
    print("=" * 70)
    print("  NAU ASCE Concrete Canoe 2026 — Generating 3 Best Designs")
    print("=" * 70)

    # ── Step 1: Analyse all 3 designs ──
    print("\n[1/7] Running analysis for 3 designs...")
    analyses = []
    for spec in DESIGNS:
        try:
            result = analyse_design(spec)
            analyses.append(result)
            print(f"  [OK] {spec.name}: weight={result['total_canoe_weight_lbs']:.1f} lbs, "
                  f"FB={result['freeboard_in']:.1f}\", GM={result['gm_in']:.1f}\", "
                  f"SF={result['safety_factor']:.2f} "
                  f"{'PASS' if result['all_pass'] else 'FAIL'}")
        except Exception as e:
            print(f"  [ERROR] {spec.name}: {e}")
            traceback.print_exc()

    if not analyses:
        print("\n[FATAL] No designs could be analysed. Exiting.")
        sys.exit(1)

    # ── Step 2-4: Generate 5 figures ──
    print(f"\n[2/7] Generating Figure 1: Hull Profiles...")
    try:
        fig1_hull_profiles(analyses)
    except Exception as e:
        print(f"  [ERROR] Figure 1 failed: {e}")
        traceback.print_exc()

    print(f"\n[3/7] Generating Figure 2: Cross-Sections...")
    try:
        fig2_cross_sections(analyses)
    except Exception as e:
        print(f"  [ERROR] Figure 2 failed: {e}")
        traceback.print_exc()

    print(f"\n[4/7] Generating Figure 3: Performance Bars...")
    try:
        fig3_performance_bars(analyses)
    except Exception as e:
        print(f"  [ERROR] Figure 3 failed: {e}")
        traceback.print_exc()

    print(f"\n[5/7] Generating Figure 4: Radar Chart...")
    try:
        fig4_radar(analyses)
    except Exception as e:
        print(f"  [ERROR] Figure 4 failed: {e}")
        traceback.print_exc()

    print(f"\n[6/7] Generating Figure 5: Summary Table...")
    try:
        fig5_summary_table(analyses)
    except Exception as e:
        print(f"  [ERROR] Figure 5 failed: {e}")
        traceback.print_exc()

    # ── Step 5: Export CSV ──
    print(f"\n[7/7] Exporting data...")
    try:
        export_csv(analyses)
    except Exception as e:
        print(f"  [ERROR] CSV export failed: {e}")
        traceback.print_exc()

    # ── Step 6: Generate report ──
    try:
        generate_report(analyses)
    except Exception as e:
        print(f"  [ERROR] Report generation failed: {e}")
        traceback.print_exc()

    # ── Step 7: Console summary ──
    print_console_summary(analyses)

    # ── Verification ──
    print("VERIFICATION:")
    expected_files = [
        FIG_DIR / "3_designs_profiles.png",
        FIG_DIR / "3_designs_cross_sections.png",
        FIG_DIR / "3_designs_performance.png",
        FIG_DIR / "3_designs_radar.png",
        FIG_DIR / "3_designs_summary_table.png",
        DATA_DIR / "3_alternative_designs_comparison.csv",
        REPORT_DIR / "3_designs_comparison_report.md",
    ]
    all_ok = True
    for f in expected_files:
        exists = f.exists()
        size = f.stat().st_size if exists else 0
        status = f"OK ({size:,} bytes)" if exists else "MISSING"
        if not exists:
            all_ok = False
        print(f"  [{status}] {f.relative_to(PROJECT_ROOT)}")

    if all_ok:
        print(f"\n  All {len(expected_files)} output files verified successfully!")
    else:
        print(f"\n  WARNING: Some files are missing!")

    print("\nDone.")


if __name__ == "__main__":
    main()
