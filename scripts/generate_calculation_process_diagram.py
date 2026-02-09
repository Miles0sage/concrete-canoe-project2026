#!/usr/bin/env python3
"""
NAU ASCE Concrete Canoe 2026 — Calculation Process Diagram
Generates a visual flowchart PNG showing how the Python calculator works,
with a worked example (Design C) showing real numbers at every step.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

from calculations.concrete_canoe_calculator import (
    run_complete_analysis,
    estimate_hull_weight,
    section_modulus_thin_shell,
    bending_moment_distributed_crew,
    calculate_cog_height,
    WATER_DENSITY_LB_PER_FT3,
    INCHES_PER_FOOT,
)

FIG_DIR = PROJECT_ROOT / "reports" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# ── Design C parameters for worked example ──
L, B, D, T = 216.0, 36.0, 18.0, 0.75
DENSITY = 60.0
CREW = 700.0
FR = 1500.0
CWP = 0.70


def run_example():
    """Run Design C and collect all intermediate values."""
    canoe_wt = estimate_hull_weight(L, B, D, T, DENSITY)
    total = canoe_wt + CREW
    L_ft, B_ft, D_ft = L/12, B/12, D/12

    disp = total / WATER_DENSITY_LB_PER_FT3
    wp = L_ft * B_ft * CWP
    draft_ft = disp / wp
    draft_in = draft_ft * 12
    fb_in = (D_ft - draft_ft) * 12

    hull_kg = D_ft * 0.38
    crew_kg = 10.0 / 12.0
    kg = calculate_cog_height(canoe_wt, hull_kg, CREW, crew_kg)
    kb = draft_ft / 2
    i_wp = CWP * L_ft * B_ft**3 / 12
    v_disp = CWP * L_ft * B_ft * draft_ft
    bm = i_wp / v_disp
    gm_in = (kb + bm - kg) * 12

    sx = section_modulus_thin_shell(B, D, T)
    m_max = bending_moment_distributed_crew(canoe_wt, CREW, L_ft)
    sigma = (m_max * 12) / sx
    sf = FR / sigma

    r = run_complete_analysis(
        L, B, D, T, canoe_wt, FR, CWP, DENSITY, CREW
    )

    return {
        "canoe_wt": canoe_wt, "crew": CREW, "total": total,
        "disp": disp, "wp": wp, "draft_in": draft_in, "fb_in": fb_in,
        "kg": kg, "kb": kb, "bm_val": bm, "gm_in": gm_in,
        "sx": sx, "m_max": m_max, "sigma": sigma, "sf": sf,
        "results": r,
    }


def draw_box(ax, x, y, w, h, title, lines, color, title_color="white"):
    """Draw a styled box with title bar and content lines."""
    # Main box
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02",
        facecolor="white", edgecolor=color, linewidth=2.5,
    )
    ax.add_patch(rect)

    # Title bar
    title_h = h * 0.28
    title_rect = FancyBboxPatch(
        (x, y + h - title_h), w, title_h,
        boxstyle="round,pad=0.02",
        facecolor=color, edgecolor=color, linewidth=2,
    )
    ax.add_patch(title_rect)

    # Title text
    ax.text(x + w/2, y + h - title_h/2, title,
            ha="center", va="center", fontsize=11, fontweight="bold",
            color=title_color, family="monospace")

    # Content lines
    content_y = y + h - title_h - 0.04
    line_spacing = (h - title_h - 0.06) / max(len(lines), 1)
    for i, line in enumerate(lines):
        ax.text(x + 0.04, content_y - i * line_spacing, line,
                ha="left", va="top", fontsize=8.5, family="monospace",
                color="#333333")


def draw_arrow(ax, x1, y1, x2, y2, color="#555555"):
    """Draw a curved arrow between two points."""
    ax.annotate("",
        xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="-|>", color=color, lw=2.0,
            connectionstyle="arc3,rad=0.0",
        ),
    )


def generate_diagram(d):
    """Generate the full process flow diagram."""
    fig, ax = plt.subplots(figsize=(22, 28))
    ax.set_xlim(-0.1, 4.6)
    ax.set_ylim(-0.3, 11.8)
    ax.axis("off")

    # Title
    ax.text(2.25, 11.5,
            "NAU ASCE Concrete Canoe 2026",
            ha="center", va="center", fontsize=22, fontweight="bold",
            color="#1a237e")
    ax.text(2.25, 11.2,
            "Calculator Process Flow  —  Design C Worked Example",
            ha="center", va="center", fontsize=14, color="#555555")
    ax.text(2.25, 10.95,
            f"L={L:.0f}\"  B={B:.0f}\"  D={D:.0f}\"  t={T}\"  "
            f"density={DENSITY:.0f} PCF  f'r={FR:.0f} psi",
            ha="center", va="center", fontsize=11, color="#888888",
            family="monospace")

    bw = 1.9   # box width
    bh = 1.05  # box height

    # ═══════════════════════════════════════════
    # STEP 1: INPUTS (top)
    # ═══════════════════════════════════════════
    draw_box(ax, 0.2, 9.7, bw, bh,
        "STEP 1: INPUTS",
        [
            f"Length:    {L:.0f} in ({L/12:.0f} ft)",
            f"Beam:     {B:.0f} in",
            f"Depth:    {D:.0f} in",
            f"Thickness:{T} in",
            f"Density:  {DENSITY:.0f} PCF",
        ],
        "#1565C0")

    draw_box(ax, 2.5, 9.7, bw, bh,
        "STEP 2: WEIGHT",
        [
            f"Hull (U-shell): {d['canoe_wt']:.0f} lbs",
            f"  girth x L x Cp x t x rho",
            f"Crew (4x175):   {d['crew']:.0f} lbs",
            f"Total loaded:   {d['total']:.0f} lbs",
        ],
        "#1565C0")

    draw_arrow(ax, 2.1, 10.2, 2.5, 10.2)

    # ═══════════════════════════════════════════
    # STEP 3: HYDROSTATICS (row 2)
    # ═══════════════════════════════════════════
    draw_box(ax, 0.2, 8.1, 4.2, bh,
        "STEP 3: HYDROSTATICS",
        [
            f"Displaced volume:  V = {d['total']:.0f} / {WATER_DENSITY_LB_PER_FT3} = {d['disp']:.2f} ft3        "
            f"(Archimedes: V = W / rho_water)",
            f"Waterplane area:   Awp = Cwp x L x B = {CWP} x {L/12:.0f} x {B/12:.1f} = {d['wp']:.1f} ft2    "
            f"(Cwp = {CWP} for canoe hull)",
            f"Draft:             T = V / Awp = {d['disp']:.2f} / {d['wp']:.1f} = {d['draft_in']:.2f} in",
            f"Freeboard:         FB = D - T = {D:.0f} - {d['draft_in']:.2f} = {d['fb_in']:.2f} in          "
            f"(>= 6.0\" required)",
        ],
        "#2E7D32")

    draw_arrow(ax, 2.25, 9.7, 2.25, 9.15)

    # ═══════════════════════════════════════════
    # STEP 4: STABILITY (row 3)
    # ═══════════════════════════════════════════
    draw_box(ax, 0.2, 6.5, 4.2, bh + 0.25,
        "STEP 4: STABILITY (GM = KB + BM - KG)",
        [
            f"KB = draft/2 = {d['kb']:.4f} ft                            "
            f"(centroid of displaced volume)",
            f"BM = I_wp / V_disp = {d['bm_val']:.4f} ft                   "
            f"(I_wp = Cwp x L x B^3 / 12)",
            f"KG = weighted COG = {d['kg']:.4f} ft                        "
            f"(hull @0.38D + crew @10\")",
            f"GM = {d['kb']:.4f} + {d['bm_val']:.4f} - {d['kg']:.4f} = {d['gm_in']:.2f} in",
            f"                                                           "
            f"(>= 6.0\" required)",
        ],
        "#F57F17")

    draw_arrow(ax, 2.25, 8.1, 2.25, 7.75)

    # ═══════════════════════════════════════════
    # STEP 5: SECTION PROPERTIES (row 4)
    # ═══════════════════════════════════════════
    draw_box(ax, 0.2, 4.8, 2.05, bh + 0.55,
        "STEP 5: U-SECTION",
        [
            "  _______________",
            " |               |",
            " |   thin-shell  |",
            " |___________B___|",
            "",
            f"A_total = {(B*T + 2*T*(D-T)):.1f} in2",
            f"y_bar = {section_y_bar(B, D, T):.2f} in",
            f"Ix  = {section_ix(B, D, T):.0f} in4",
            f"Sx  = {d['sx']:.1f} in3",
        ],
        "#6A1B9A")

    draw_box(ax, 2.35, 4.8, 2.05, bh + 0.55,
        "STEP 6: BENDING",
        [
            f"M_hull = wL^2/8",
            f"M_crew = PL/4 (midship)",
            f"M_total = {d['m_max']:.0f} lb-ft",
            f"",
            f"sigma = M x 12 / Sx",
            f"      = {d['m_max']*12:.0f} / {d['sx']:.1f}",
            f"      = {d['sigma']:.1f} psi",
            f"SF = {FR:.0f} / {d['sigma']:.1f}",
            f"   = {d['sf']:.2f}  (>= 2.0)",
        ],
        "#C62828")

    draw_arrow(ax, 2.25, 6.5, 1.2, 5.95)
    draw_arrow(ax, 2.25, 6.5, 3.3, 5.95)

    # ═══════════════════════════════════════════
    # STEP 7: RESULTS (bottom)
    # ═══════════════════════════════════════════
    r = d["results"]
    overall = r["overall_pass"]
    result_color = "#2E7D32" if overall else "#C62828"
    status = "ALL PASS" if overall else "FAIL"

    draw_box(ax, 0.2, 3.0, 4.2, bh + 0.25,
        f"STEP 7: ASCE COMPLIANCE  —  {status}",
        [
            f"  Freeboard:  {d['fb_in']:>8.2f} in   >= 6.0\"   "
            f"{'PASS' if d['fb_in'] >= 6 else 'FAIL'}",
            f"  GM:         {d['gm_in']:>8.2f} in   >= 6.0\"   "
            f"{'PASS' if d['gm_in'] >= 6 else 'FAIL'}",
            f"  SF (ASD):   {d['sf']:>8.2f}        >= 2.0    "
            f"{'PASS' if d['sf'] >= 2 else 'FAIL'}",
            f"  Weight:     {d['canoe_wt']:>8.0f} lbs   <= 237    "
            f"{'PASS' if d['canoe_wt'] <= 237 else 'OVER'}",
        ],
        result_color)

    draw_arrow(ax, 1.2, 4.8, 2.25, 4.25)
    draw_arrow(ax, 3.3, 4.8, 2.25, 4.25)

    # ═══════════════════════════════════════════
    # CODE SNIPPET PANEL (bottom section)
    # ═══════════════════════════════════════════
    code_box = FancyBboxPatch(
        (0.2, 0.0), 4.2, 2.6,
        boxstyle="round,pad=0.02",
        facecolor="#263238", edgecolor="#37474F", linewidth=2.5,
    )
    ax.add_patch(code_box)

    ax.text(2.25, 2.45,
            "Python Code  —  How to Run",
            ha="center", va="center", fontsize=13, fontweight="bold",
            color="#80CBC4", family="monospace")

    code_lines = [
        "from calculations.concrete_canoe_calculator import run_complete_analysis",
        "",
        "results = run_complete_analysis(",
        f"    hull_length_in={L:.0f},    hull_beam_in={B:.0f},",
        f"    hull_depth_in={D:.0f},     hull_thickness_in={T},",
        f"    concrete_weight_lbs={d['canoe_wt']:.0f},",
        f"    flexural_strength_psi={FR:.0f},",
        f"    concrete_density_pcf={DENSITY:.0f},",
        f"    crew_weight_lbs={CREW:.0f},",
        ")",
        "",
        f"print(results['freeboard']['freeboard_in'])  # {d['fb_in']:.2f}",
        f"print(results['stability']['gm_in'])         # {d['gm_in']:.2f}",
        f"print(results['structural']['safety_factor']) # {d['sf']:.2f}",
        f"print(results['overall_pass'])                # {overall}",
    ]

    for i, line in enumerate(code_lines):
        color = "#80CBC4"
        if line.startswith("#") or "# " in line:
            color = "#A5D6A7"
        elif line.startswith("from ") or line.startswith("print"):
            color = "#CE93D8"
        elif "=" in line and not line.strip().startswith("hull") and not line.strip().startswith("concrete") and not line.strip().startswith("crew") and not line.strip().startswith("flexural"):
            color = "#90CAF9"

        ax.text(0.35, 2.2 - i * 0.145, line,
                ha="left", va="top", fontsize=8.2, family="monospace",
                color=color)

    # Footer
    ax.text(2.25, -0.2,
            "github.com/Miles0sage/concrete-canoe-project2026  |  "
            "concrete_canoe_calculator.py v2.1  |  60/60 tests passing",
            ha="center", va="center", fontsize=9, color="#999999",
            style="italic")

    plt.tight_layout()
    out = FIG_DIR / "calculation_process_diagram.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def section_y_bar(b, d, t):
    a_bot = b * t
    h_wall = d - t
    a_wall = t * h_wall
    total = a_bot + 2 * a_wall
    return (a_bot * (t/2) + 2 * a_wall * (t + h_wall/2)) / total


def section_ix(b, d, t):
    a_bot = b * t
    y_bot = t / 2
    i_bot_s = b * t**3 / 12
    h_wall = d - t
    a_wall = t * h_wall
    y_wall = t + h_wall / 2
    i_wall_s = t * h_wall**3 / 12
    total = a_bot + 2 * a_wall
    y_na = (a_bot * y_bot + 2 * a_wall * y_wall) / total
    return (i_bot_s + a_bot * (y_na - y_bot)**2
            + 2 * (i_wall_s + a_wall * (y_wall - y_na)**2))


def main():
    print("=" * 60)
    print("  Generating Calculation Process Diagram...")
    print("=" * 60)

    d = run_example()

    print(f"\n  Design C worked example:")
    print(f"    Weight:    {d['canoe_wt']:.0f} lbs hull + {d['crew']:.0f} crew = {d['total']:.0f} lbs")
    print(f"    Freeboard: {d['fb_in']:.2f} in")
    print(f"    GM:        {d['gm_in']:.2f} in")
    print(f"    Sx:        {d['sx']:.1f} in3")
    print(f"    SF:        {d['sf']:.2f}")
    print(f"    Overall:   {'PASS' if d['results']['overall_pass'] else 'FAIL'}")

    out = generate_diagram(d)
    print(f"\n  Diagram saved: {out}")
    print(f"  Size: {out.stat().st_size:,} bytes")
    print("=" * 60)


if __name__ == "__main__":
    main()
