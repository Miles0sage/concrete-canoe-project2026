#!/usr/bin/env python3
"""
NAU ASCE Concrete Canoe 2026 — Detailed Individual Design Reports
Generates complete analysis for Design B and Design C (Design A already exists).
Outputs: markdown reports, 5-subplot figure suites, CSV metric exports.
"""

import sys
import csv
import math
import traceback
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple

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
    bending_moment_uniform_load,
    section_modulus_rectangular,
    bending_stress_psi,
    safety_factor as calc_safety_factor,
)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

FIG_DIR = PROJECT_ROOT / "reports" / "figures"
DATA_DIR = PROJECT_ROOT / "data"
REPORT_DIR = PROJECT_ROOT / "reports"
for d in [FIG_DIR, DATA_DIR, REPORT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Constants ──
CONCRETE_DENSITY_PCF = 60.0
FLEXURAL_STRENGTH_PSI = 1500.0
WATERPLANE_CWP = 0.65
PADDLER_WEIGHT = 175.0
NUM_PADDLERS = 4
CREW_WEIGHT = PADDLER_WEIGHT * NUM_PADDLERS
REINF_FRACTION = 0.05
FINISH_WEIGHT_LBS = 3.0

CONCRETE_COST_PER_FT3 = 12.0
MESH_COST_PER_FT2 = 2.50
MOLD_COST = 350.0
FINISH_COST = 75.0
LABOR_RATE = 0.0  # volunteer
CONTINGENCY_PCT = 0.15

MIN_FB_IN = 6.0
MIN_GM_IN = 6.0
MIN_SF = 2.0
TARGET_WT = 237.0

@dataclass
class Design:
    name: str
    tag: str
    length_in: float
    beam_in: float
    depth_in: float
    thickness_in: float
    description: str
    color: str

DESIGNS = {
    "A": Design("Design A", "Optimal (Lightest)", 192, 32, 17, 0.5,
                 "Minimum weight while meeting requirements", "#2196F3"),
    "B": Design("Design B", "Conservative (Safety Margin)", 196, 34, 18, 0.5,
                 "Extra safety margin on all requirements", "#4CAF50"),
    "C": Design("Design C", "Traditional (Easy Build)", 216, 36, 18, 0.5,
                 "Standard proportions, easier construction", "#FF9800"),
}


def shell_weight(L_in, B_in, D_in, t_in, density=CONCRETE_DENSITY_PCF):
    L, B, D, t = L_in/12, B_in/12, D_in/12, t_in/12
    bottom = (math.pi/4) * L * B
    sides = 2 * L * D * 0.70
    return (bottom + sides) * t * density


def full_analysis(d: Design) -> Dict[str, Any]:
    """Complete analysis returning all metrics."""
    L, B, D, t = d.length_in, d.beam_in, d.depth_in, d.thickness_in
    L_ft, B_ft, D_ft, t_ft = L/12, B/12, D/12, t/12

    # Weight breakdown
    sw = shell_weight(L, B, D, t)
    rw = sw * REINF_FRACTION
    fw = FINISH_WEIGHT_LBS
    canoe_wt = sw + rw + fw
    loaded_wt = canoe_wt + CREW_WEIGHT

    # Hydrostatics
    disp_ft3 = displacement_volume(loaded_wt)
    wp_ft2 = L_ft * B_ft * WATERPLANE_CWP
    draft_ft = disp_ft3 / wp_ft2 if wp_ft2 > 0 else 0
    draft_in = draft_ft * 12
    fb_ft = max(0, D_ft - draft_ft)
    fb_in = fb_ft * 12

    # Stability
    KB = draft_ft / 2
    BM = (B_ft**2) / (12 * draft_ft) if draft_ft > 0 else 0
    KG = D_ft * 0.45
    GM_ft = KB + BM - KG
    GM_in = GM_ft * 12

    # GZ curve (0-90 degrees)
    angles = np.arange(0, 91, 1)
    GZ = GM_in * np.sin(np.deg2rad(angles))

    # Structural — 10 stations
    stations = np.linspace(0, L_ft, 11)
    w_per_ft = loaded_wt / L_ft
    BM_stations = []  # bending moment
    SF_stations = []  # shear force
    for x in stations:
        R = loaded_wt / 2  # reaction
        V = R - w_per_ft * x  # shear
        M = R * x - w_per_ft * x**2 / 2  # moment
        BM_stations.append(M)
        SF_stations.append(V)
    M_max = max(BM_stations)

    eff_depth = D - t
    S_in3 = section_modulus_rectangular(B, eff_depth)
    sigma = bending_stress_psi(M_max, S_in3)
    sf = calc_safety_factor(FLEXURAL_STRENGTH_PSI, sigma)

    # Material quantities
    shell_vol_ft3 = sw / CONCRETE_DENSITY_PCF
    batches_needed = math.ceil(shell_vol_ft3 / 0.5)  # 0.5 ft³ per batch
    mesh_area_ft2 = ((math.pi/4)*L_ft*B_ft + 2*L_ft*D_ft*0.70) * 1.15  # 15% overlap
    mold_length_ft = L_ft + 1
    mold_width_ft = B_ft + 1

    # Cost estimate
    concrete_cost = shell_vol_ft3 * CONCRETE_COST_PER_FT3
    mesh_cost = mesh_area_ft2 * MESH_COST_PER_FT2
    subtotal = concrete_cost + mesh_cost + MOLD_COST + FINISH_COST
    contingency = subtotal * CONTINGENCY_PCT
    total_cost = subtotal + contingency

    # Pass / fail
    fb_pass = fb_in >= MIN_FB_IN
    gm_pass = GM_in >= MIN_GM_IN
    sf_pass = sf >= MIN_SF
    all_pass = fb_pass and gm_pass and sf_pass

    return {
        "design": d,
        "shell_wt": sw, "reinf_wt": rw, "finish_wt": fw,
        "canoe_wt": canoe_wt, "loaded_wt": loaded_wt,
        "disp_ft3": disp_ft3, "wp_ft2": wp_ft2,
        "draft_ft": draft_ft, "draft_in": draft_in,
        "fb_ft": fb_ft, "fb_in": fb_in,
        "KB": KB, "BM_val": BM, "KG": KG, "GM_ft": GM_ft, "GM_in": GM_in,
        "angles": angles, "GZ": GZ,
        "stations_ft": stations, "BM_stations": BM_stations, "SF_stations": SF_stations,
        "M_max": M_max, "S_in3": S_in3, "sigma_psi": sigma, "sf": sf,
        "shell_vol_ft3": shell_vol_ft3, "batches": batches_needed,
        "mesh_area_ft2": mesh_area_ft2,
        "mold_length_ft": mold_length_ft, "mold_width_ft": mold_width_ft,
        "concrete_cost": concrete_cost, "mesh_cost": mesh_cost,
        "mold_cost": MOLD_COST, "finish_cost": FINISH_COST,
        "contingency": contingency, "total_cost": total_cost,
        "fb_pass": fb_pass, "gm_pass": gm_pass, "sf_pass": sf_pass,
        "all_pass": all_pass,
    }


# ═══════════════════════════════════════════════════════════════
# Figure: 5-subplot complete suite
# ═══════════════════════════════════════════════════════════════
def generate_figure_suite(a: Dict, label: str) -> Path:
    d = a["design"]
    color = d.color
    L, B, D, t = d.length_in, d.beam_in, d.depth_in, d.thickness_in

    fig = plt.figure(figsize=(20, 16))
    fig.suptitle(f"{d.name}: {d.tag} — Complete Analysis Suite",
                 fontsize=18, fontweight="bold", y=0.98)

    # ── 1. Hull profile ──
    ax1 = fig.add_subplot(2, 3, 1)
    x = np.linspace(0, L, 200)
    rocker = D * 0.08 * (2*x/L - 1)**2
    gunwale = np.full_like(x, D)
    ax1.fill_between(x, rocker, gunwale, alpha=0.2, color=color)
    ax1.plot(x, rocker, color=color, lw=2.5)
    ax1.plot(x, gunwale, color=color, lw=2)
    ax1.axhline(a["draft_in"], color="dodgerblue", ls="-.", lw=1.8,
                label=f'Waterline ({a["draft_in"]:.1f}")')
    paddler_xs = np.linspace(L*0.20, L*0.80, NUM_PADDLERS)
    for px in paddler_xs:
        ax1.plot(px, D+1.5, "ro", ms=7)
    ax1.set_title("Hull Profile (Side View)", fontweight="bold")
    ax1.set_xlabel("Length (in)")
    ax1.set_ylabel("Depth (in)")
    ax1.legend(fontsize=8)
    ax1.set_xlim(-5, L+5)
    ax1.grid(True, alpha=0.25)

    # ── 2. Cross-sections at 5 stations ──
    ax2 = fig.add_subplot(2, 3, 2)
    station_fracs = [0.0, 0.25, 0.5, 0.75, 1.0]
    station_names = ["Bow", "Qtr-Fwd", "Midship", "Qtr-Aft", "Stern"]
    alphas = [0.15, 0.25, 0.45, 0.25, 0.15]
    deadrise = D * 0.25
    for frac, name, alpha in zip(station_fracs, station_names, alphas):
        w = B * (0.3 + 0.7 * (1 - 2*abs(frac - 0.5)))
        xs = np.array([-w/2, -w/2, 0, w/2, w/2])
        ys = np.array([D, 0, -deadrise, 0, D])
        ax2.plot(xs, ys, lw=1.8, alpha=0.7+0.3*alpha, label=name)
        ax2.fill(xs, ys, alpha=alpha*0.5)
    ax2.axhline(a["draft_in"] - deadrise, color="dodgerblue", ls="-.", lw=1.5)
    ax2.set_title("Cross-Sections at 5 Stations", fontweight="bold")
    ax2.set_xlabel("Width (in)")
    ax2.set_ylabel("Height (in)")
    ax2.legend(fontsize=7, ncol=2)
    ax2.set_aspect("equal")
    ax2.grid(True, alpha=0.25)

    # ── 3. GZ stability curve ──
    ax3 = fig.add_subplot(2, 3, 3)
    ax3.plot(a["angles"], a["GZ"], color=color, lw=2.5)
    ax3.fill_between(a["angles"], 0, a["GZ"], where=a["GZ"]>0,
                      alpha=0.15, color=color)
    ax3.axhline(0, color="gray", ls="--", lw=1)
    max_gz = max(a["GZ"])
    max_angle = a["angles"][np.argmax(a["GZ"])]
    ax3.plot(max_angle, max_gz, "ro", ms=8)
    ax3.annotate(f"Max GZ = {max_gz:.1f}\" @ {max_angle}°",
                 xy=(max_angle, max_gz), xytext=(max_angle+10, max_gz-1),
                 fontsize=9, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color="red"))
    ax3.set_title("GZ Stability Curve (0-90°)", fontweight="bold")
    ax3.set_xlabel("Heel Angle (degrees)")
    ax3.set_ylabel("Righting Arm GZ (in)")
    ax3.grid(True, alpha=0.25)

    # ── 4. Bending moment diagram ──
    ax4 = fig.add_subplot(2, 3, 4)
    stations_in = np.array(a["stations_ft"]) * 12
    bm_vals = a["BM_stations"]
    ax4.fill_between(stations_in, 0, bm_vals, alpha=0.2, color=color)
    ax4.plot(stations_in, bm_vals, color=color, lw=2.5)
    max_m = max(bm_vals)
    mid_in = stations_in[np.argmax(bm_vals)]
    ax4.plot(mid_in, max_m, "ro", ms=8)
    ax4.annotate(f"Max M = {max_m:.0f} lb-ft", xy=(mid_in, max_m),
                 xytext=(mid_in+15, max_m*0.85), fontsize=9, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color="red"))
    ax4.set_title("Bending Moment Diagram", fontweight="bold")
    ax4.set_xlabel("Position (in)")
    ax4.set_ylabel("Bending Moment (lb-ft)")
    ax4.grid(True, alpha=0.25)

    # ── 5. Shear force + load distribution ──
    ax5 = fig.add_subplot(2, 3, 5)
    sf_vals = a["SF_stations"]
    ax5.fill_between(stations_in, 0, sf_vals, alpha=0.15, color="red")
    ax5.plot(stations_in, sf_vals, color="red", lw=2.5, label="Shear Force")
    w_per_in = a["loaded_wt"] / L
    ax5.axhline(0, color="gray", ls="--", lw=1)
    load_line = np.full_like(stations_in, -w_per_in*12)  # per foot
    ax5.plot(stations_in, load_line, "g--", lw=1.5,
             label=f"Load = {w_per_in*12:.1f} lb/ft")
    ax5.set_title("Shear Force & Load Distribution", fontweight="bold")
    ax5.set_xlabel("Position (in)")
    ax5.set_ylabel("Force (lbs)")
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.25)

    # ── 6. Summary metrics box ──
    ax6 = fig.add_subplot(2, 3, 6)
    ax6.axis("off")
    pf = lambda v: "PASS ✓" if v else "FAIL ✗"
    pfc = lambda v: "green" if v else "red"
    lines = [
        (f"{d.name}: {d.tag}", 16, "bold", color),
        (f'Dimensions: {L:.0f}" × {B:.0f}" × {D:.0f}" (t={t}")', 11, "normal", "black"),
        ("", 6, "normal", "black"),
        (f"Shell Weight:     {a['shell_wt']:.1f} lbs", 11, "normal", "black"),
        (f"Reinforcement:    {a['reinf_wt']:.1f} lbs", 11, "normal", "black"),
        (f"Finish:           {a['finish_wt']:.1f} lbs", 11, "normal", "black"),
        (f"Total Canoe:      {a['canoe_wt']:.1f} lbs  (target ≤{TARGET_WT})", 11, "bold", "black"),
        (f"Loaded (w/crew):  {a['loaded_wt']:.1f} lbs", 11, "normal", "black"),
        ("", 6, "normal", "black"),
        (f'Freeboard:  {a["fb_in"]:.1f}"  {pf(a["fb_pass"])}  (req ≥{MIN_FB_IN}")', 12, "bold", pfc(a["fb_pass"])),
        (f'GM:         {a["GM_in"]:.1f}"  {pf(a["gm_pass"])}  (req ≥{MIN_GM_IN}")', 12, "bold", pfc(a["gm_pass"])),
        (f"SF:         {a['sf']:.2f}  {pf(a['sf_pass'])}  (req ≥{MIN_SF})", 12, "bold", pfc(a["sf_pass"])),
        ("", 6, "normal", "black"),
        (f"OVERALL: {pf(a['all_pass'])}", 14, "bold", pfc(a["all_pass"])),
        ("", 6, "normal", "black"),
        (f"Est. Cost: ${a['total_cost']:.0f} (incl {CONTINGENCY_PCT*100:.0f}% contingency)", 11, "normal", "black"),
    ]
    y = 0.95
    for text, size, weight, clr in lines:
        ax6.text(0.05, y, text, fontsize=size, fontweight=weight, color=clr,
                 transform=ax6.transAxes, va="top", fontfamily="monospace")
        y -= 0.065

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out = FIG_DIR / f"design_{label}_complete_suite.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] Figure saved: {out.name}")
    return out


# ═══════════════════════════════════════════════════════════════
# CSV export
# ═══════════════════════════════════════════════════════════════
def export_csv(a: Dict, label: str) -> Path:
    d = a["design"]
    out = DATA_DIR / f"design_{label}_detailed_metrics.csv"
    rows = [
        ("Metric", "Value", "Unit"),
        ("Design Name", d.name, ""),
        ("Design Tag", d.tag, ""),
        ("Length", f"{d.length_in}", "in"),
        ("Beam", f"{d.beam_in}", "in"),
        ("Depth", f"{d.depth_in}", "in"),
        ("Thickness", f"{d.thickness_in}", "in"),
        ("Concrete Density", f"{CONCRETE_DENSITY_PCF}", "PCF"),
        ("Shell Weight", f"{a['shell_wt']:.2f}", "lbs"),
        ("Reinforcement Weight", f"{a['reinf_wt']:.2f}", "lbs"),
        ("Finish Weight", f"{a['finish_wt']:.2f}", "lbs"),
        ("Total Canoe Weight", f"{a['canoe_wt']:.2f}", "lbs"),
        ("Crew Weight", f"{CREW_WEIGHT:.0f}", "lbs"),
        ("Loaded Weight", f"{a['loaded_wt']:.2f}", "lbs"),
        ("Displacement Volume", f"{a['disp_ft3']:.4f}", "ft3"),
        ("Waterplane Area", f"{a['wp_ft2']:.4f}", "ft2"),
        ("Draft", f"{a['draft_in']:.2f}", "in"),
        ("Freeboard", f"{a['fb_in']:.2f}", "in"),
        ("KB", f"{a['KB']*12:.2f}", "in"),
        ("BM", f"{a['BM_val']*12:.2f}", "in"),
        ("KG", f"{a['KG']*12:.2f}", "in"),
        ("GM", f"{a['GM_in']:.2f}", "in"),
        ("Max Bending Moment", f"{a['M_max']:.2f}", "lb-ft"),
        ("Section Modulus", f"{a['S_in3']:.2f}", "in3"),
        ("Bending Stress", f"{a['sigma_psi']:.2f}", "psi"),
        ("Safety Factor", f"{a['sf']:.4f}", ""),
        ("Shell Volume", f"{a['shell_vol_ft3']:.4f}", "ft3"),
        ("Batches Needed", f"{a['batches']}", ""),
        ("Mesh Area", f"{a['mesh_area_ft2']:.2f}", "ft2"),
        ("Mold Size (L×W)", f"{a['mold_length_ft']:.1f} × {a['mold_width_ft']:.1f}", "ft"),
        ("Est. Total Cost", f"{a['total_cost']:.2f}", "$"),
        ("Freeboard Pass", str(a['fb_pass']), ""),
        ("GM Pass", str(a['gm_pass']), ""),
        ("SF Pass", str(a['sf_pass']), ""),
        ("Overall Pass", str(a['all_pass']), ""),
    ]
    with open(out, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"  [OK] CSV saved: {out.name}")
    return out


# ═══════════════════════════════════════════════════════════════
# Markdown report
# ═══════════════════════════════════════════════════════════════
def generate_md_report(a: Dict, label: str) -> Path:
    d = a["design"]
    pf = lambda v: "PASS ✓" if v else "FAIL ✗"
    L, B, D, t = d.length_in, d.beam_in, d.depth_in, d.thickness_in

    md = f"""# {d.name}: {d.tag} — Complete Analysis Report

## 1. Design Overview

| Parameter | Value |
|-----------|-------|
| Length | {L:.0f}" ({L/12:.1f} ft) |
| Beam | {B:.0f}" ({B/12:.2f} ft) |
| Depth | {D:.0f}" ({D/12:.2f} ft) |
| Wall Thickness | {t}" |
| Description | {d.description} |

## 2. Weight Breakdown

| Component | Weight (lbs) | % of Total |
|-----------|-------------|-----------|
| Concrete Shell | {a['shell_wt']:.1f} | {a['shell_wt']/a['canoe_wt']*100:.1f}% |
| Reinforcement (PVA mesh) | {a['reinf_wt']:.1f} | {a['reinf_wt']/a['canoe_wt']*100:.1f}% |
| Finish/Sealant | {a['finish_wt']:.1f} | {a['finish_wt']/a['canoe_wt']*100:.1f}% |
| **Total Canoe** | **{a['canoe_wt']:.1f}** | **100%** |
| Crew (4 × {PADDLER_WEIGHT:.0f} lbs) | {CREW_WEIGHT:.0f} | — |
| **Loaded Total** | **{a['loaded_wt']:.1f}** | — |

Target: ≤ {TARGET_WT} lbs → **{pf(a['canoe_wt'] <= TARGET_WT)}** ({(1 - a['canoe_wt']/TARGET_WT)*100:.0f}% under target)

## 3. Hydrostatic Analysis

| Parameter | Value |
|-----------|-------|
| Displacement Volume | {a['disp_ft3']:.3f} ft³ |
| Waterplane Area (Cwp={WATERPLANE_CWP}) | {a['wp_ft2']:.2f} ft² |
| Draft (loaded) | {a['draft_in']:.1f}" ({a['draft_ft']:.3f} ft) |
| Freeboard | {a['fb_in']:.1f}" ({a['fb_ft']:.3f} ft) |
| Freeboard Requirement | ≥ {MIN_FB_IN}" → **{pf(a['fb_pass'])}** |

## 4. Stability Analysis

| Parameter | Value (ft) | Value (in) |
|-----------|-----------|-----------|
| KB (center of buoyancy) | {a['KB']:.4f} | {a['KB']*12:.2f} |
| BM (metacentric radius) | {a['BM_val']:.4f} | {a['BM_val']*12:.2f} |
| KG (center of gravity) | {a['KG']:.4f} | {a['KG']*12:.2f} |
| **GM (metacentric height)** | **{a['GM_ft']:.4f}** | **{a['GM_in']:.2f}** |

GM = KB + BM - KG = {a['KB']:.4f} + {a['BM_val']:.4f} - {a['KG']:.4f} = {a['GM_ft']:.4f} ft = {a['GM_in']:.2f}"

GM Requirement: ≥ {MIN_GM_IN}" → **{pf(a['gm_pass'])}** (margin: {a['GM_in'] - MIN_GM_IN:.1f}")

### GZ Stability Curve
Maximum righting arm: GZ_max = {max(a['GZ']):.1f}" at {a['angles'][np.argmax(a['GZ'])]}°
Vanishing angle: ~90° (simplified model)

## 5. Structural Analysis

| Parameter | Value |
|-----------|-------|
| Load Distribution | {a['loaded_wt']/(L/12):.1f} lb/ft (uniform) |
| Max Bending Moment | {a['M_max']:.1f} lb-ft (at midship) |
| Effective Section Depth | {D - t:.1f}" |
| Section Modulus (S) | {a['S_in3']:.1f} in³ |
| Max Bending Stress | {a['sigma_psi']:.1f} psi |
| Flexural Strength | {FLEXURAL_STRENGTH_PSI:.0f} psi |
| **Safety Factor** | **{a['sf']:.2f}** |

Safety Factor Requirement: ≥ {MIN_SF} → **{pf(a['sf_pass'])}** ({a['sf']/MIN_SF:.0f}× over minimum)

### Station-by-Station Analysis

| Station | Position (ft) | Shear (lbs) | Moment (lb-ft) |
|---------|--------------|-------------|----------------|
"""
    for i, (s, v, m) in enumerate(zip(a["stations_ft"], a["SF_stations"], a["BM_stations"])):
        md += f"| {i} | {s:.1f} | {v:.1f} | {m:.1f} |\n"

    md += f"""
## 6. Material Quantities

| Material | Quantity | Notes |
|----------|---------|-------|
| Concrete Volume | {a['shell_vol_ft3']:.3f} ft³ | At {CONCRETE_DENSITY_PCF} PCF |
| Concrete Batches | {a['batches']} | 0.5 ft³ per batch |
| PVA Mesh | {a['mesh_area_ft2']:.1f} ft² | Includes 15% overlap |
| Mold Dimensions | {a['mold_length_ft']:.1f}' × {a['mold_width_ft']:.1f}' | With 6" margin |

## 7. Construction Specifications

- **Mold:** Female mold, {a['mold_length_ft']:.1f}' × {a['mold_width_ft']:.1f}', EPS foam with fiberglass shell
- **Layup:** 3-layer technique (outer shell → mesh → inner shell)
- **Thickness Control:** {t}" spacer blocks at 12" intervals
- **Curing:** 7-day moist cure under plastic, 28-day strength development
- **Demolding:** Day 7-10, flip with 6-person team
- **Finishing:** Sand to 220 grit, apply concrete sealer, competition graphics

## 8. Cost Estimate

| Item | Cost |
|------|------|
| Concrete Materials | ${a['concrete_cost']:.0f} |
| PVA Reinforcement Mesh | ${a['mesh_cost']:.0f} |
| Mold Materials | ${a['mold_cost']:.0f} |
| Finishing & Sealant | ${a['finish_cost']:.0f} |
| **Subtotal** | **${a['concrete_cost']+a['mesh_cost']+a['mold_cost']+a['finish_cost']:.0f}** |
| Contingency ({CONTINGENCY_PCT*100:.0f}%) | ${a['contingency']:.0f} |
| **Total** | **${a['total_cost']:.0f}** |

## 9. ASCE Compliance Summary

| Requirement | Value | Minimum | Status |
|-------------|-------|---------|--------|
| Freeboard | {a['fb_in']:.1f}" | ≥ {MIN_FB_IN}" | **{pf(a['fb_pass'])}** |
| Metacentric Height (GM) | {a['GM_in']:.1f}" | ≥ {MIN_GM_IN}" | **{pf(a['gm_pass'])}** |
| Safety Factor | {a['sf']:.2f} | ≥ {MIN_SF} | **{pf(a['sf_pass'])}** |
| Canoe Weight | {a['canoe_wt']:.1f} lbs | ≤ {TARGET_WT} lbs | **{pf(a['canoe_wt'] <= TARGET_WT)}** |
| **Overall** | | | **{pf(a['all_pass'])}** |

## 10. Figures

- Complete analysis suite: `figures/design_{label}_complete_suite.png`

---
*Generated by NAU ASCE Concrete Canoe Calculator — 2026*
"""
    out = REPORT_DIR / f"design_{label}_complete_analysis.md"
    out.write_text(md)
    print(f"  [OK] Report saved: {out.name}")
    return out


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════
def main():
    print("=" * 65)
    print("  PHASE 1: Complete Analysis for All 3 Designs")
    print("=" * 65)

    for label, design in DESIGNS.items():
        print(f"\n── {design.name}: {design.tag} ──")
        try:
            a = full_analysis(design)
            generate_figure_suite(a, label)
            export_csv(a, label)
            generate_md_report(a, label)
            print(f"  Weight={a['canoe_wt']:.1f} lbs  FB={a['fb_in']:.1f}\"  "
                  f"GM={a['GM_in']:.1f}\"  SF={a['sf']:.2f}  "
                  f"{'ALL PASS' if a['all_pass'] else 'FAIL'}")
        except Exception as e:
            print(f"  [ERROR] {e}")
            traceback.print_exc()

    print("\n  Phase 1 complete.")


if __name__ == "__main__":
    main()
