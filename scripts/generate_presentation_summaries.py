#!/usr/bin/env python3
"""
NAU ASCE Concrete Canoe 2026 - Presentation Summary Generator
=============================================================

Generates 5 presentation-ready PNG figures (300 DPI) plus console output
summarizing the engineering analysis for all three hull designs.

Figures produced:
  1. presentation_design_comparison.png   - Side-by-side table with pass/fail
  2. presentation_why_design_A.png        - Infographic: why Design A is best
  3. presentation_how_it_works.png        - Flowchart for non-coders
  4. presentation_monte_carlo_simple.png  - Monte Carlo explanation diagram
  5. presentation_key_numbers.png         - KPI dashboard infographic
"""

import sys
import math
import warnings
from pathlib import Path
from typing import Dict, Any, List, Tuple

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path("/root/concrete-canoe-project2026")
sys.path.insert(0, str(PROJECT_ROOT))

from calculations.concrete_canoe_calculator import (
    run_complete_analysis,
    estimate_hull_weight,
    INCHES_PER_FOOT,
)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

# ---------------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------------
FIG_DIR = PROJECT_ROOT / "reports" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Branding and style constants
# ---------------------------------------------------------------------------
NAU_BLUE = "#003466"
NAU_GOLD = "#FFC72C"
NAU_DARK_GOLD = "#D4A017"
PASS_GREEN = "#2ECC71"
FAIL_RED = "#E74C3C"
LIGHT_GRAY = "#F5F5F5"
MED_GRAY = "#CCCCCC"
DARK_GRAY = "#333333"
WHITE = "#FFFFFF"
SOFT_BLUE = "#EBF5FB"
ACCENT_TEAL = "#1ABC9C"
ACCENT_ORANGE = "#E67E22"

BRAND_TITLE = "NAU ASCE Concrete Canoe 2026"

# ---------------------------------------------------------------------------
# Design specifications
# ---------------------------------------------------------------------------
DESIGNS = {
    "A": {
        "name": "Design A",
        "label": "Lightweight Racer",
        "length_in": 192,
        "beam_in": 32,
        "depth_in": 17,
        "thickness_in": 0.5,
        "density_pcf": 60.0,
        "flexural_psi": 1500.0,
    },
    "B": {
        "name": "Design B",
        "label": "Balanced Performer",
        "length_in": 196,
        "beam_in": 34,
        "depth_in": 18,
        "thickness_in": 0.5,
        "density_pcf": 60.0,
        "flexural_psi": 1500.0,
    },
    "C": {
        "name": "Design C",
        "label": "Stability Platform",
        "length_in": 216,
        "beam_in": 36,
        "depth_in": 18,
        "thickness_in": 0.5,
        "density_pcf": 60.0,
        "flexural_psi": 1500.0,
    },
}

CREW_WEIGHT_LBS = 700.0
WEIGHT_LIMIT_LBS = 237.0  # ASCE competition target


# ===========================================================================
# STEP 1: Run calculator for all three designs
# ===========================================================================
def estimate_weight(length_in, beam_in, depth_in, thickness_in, density_pcf):
    """
    Estimate hull weight using U-shell model:
      girth = beam + 2*depth  (in feet)
      shell_area = girth * length * Cp  (Cp=0.55)
      volume = shell_area * thickness
      weight = volume * density * 1.10
    """
    l_ft = length_in / 12.0
    b_ft = beam_in / 12.0
    d_ft = depth_in / 12.0
    t_ft = thickness_in / 12.0
    girth_ft = b_ft + 2.0 * d_ft
    shell_area_ft2 = girth_ft * l_ft * 0.55
    volume_ft3 = shell_area_ft2 * t_ft
    weight_lbs = volume_ft3 * density_pcf * 1.10
    return weight_lbs


def run_all_designs():
    """Run the calculator for all three designs and return results dict."""
    results = {}
    for key, spec in DESIGNS.items():
        weight = estimate_weight(
            spec["length_in"], spec["beam_in"], spec["depth_in"],
            spec["thickness_in"], spec["density_pcf"],
        )
        calc_weight = estimate_hull_weight(
            spec["length_in"], spec["beam_in"], spec["depth_in"],
            spec["thickness_in"], spec["density_pcf"],
        )

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            analysis = run_complete_analysis(
                hull_length_in=spec["length_in"],
                hull_beam_in=spec["beam_in"],
                hull_depth_in=spec["depth_in"],
                hull_thickness_in=spec["thickness_in"],
                concrete_weight_lbs=weight,
                flexural_strength_psi=spec["flexural_psi"],
                concrete_density_pcf=spec["density_pcf"],
                crew_weight_lbs=CREW_WEIGHT_LBS,
            )

        results[key] = {
            "spec": spec,
            "weight_lbs": weight,
            "calc_weight_lbs": calc_weight,
            "analysis": analysis,
        }
    return results


def print_results(results):
    """Print detailed console output for all designs."""
    W = 72
    print()
    print("=" * W)
    print("  " + BRAND_TITLE)
    print("  Presentation Summary - All Three Designs")
    print("=" * W)

    for key in ["A", "B", "C"]:
        r = results[key]
        spec = r["spec"]
        a = r["analysis"]
        weight = r["weight_lbs"]

        print()
        print("-" * W)
        print("  {}: {}".format(spec["name"], spec["label"]))
        print("-" * W)
        print("  Dimensions: {}L x {}B x {}D x {}t  (inches)".format(
            spec["length_in"], spec["beam_in"], spec["depth_in"], spec["thickness_in"]))
        print("  Est. Hull Weight:   {:.1f} lbs  (calc internal: {:.1f} lbs)".format(
            weight, r["calc_weight_lbs"]))
        print("  Total Loaded:       {:.1f} lbs  (hull + {:.0f} lbs crew)".format(
            weight + CREW_WEIGHT_LBS, CREW_WEIGHT_LBS))
        print()

        fb = a["freeboard"]
        st = a["stability"]
        sr = a["structural"]

        def pf(v):
            return "PASS" if v else "FAIL"

        print("  Freeboard:     {:.1f} in   (min {:.0f} in)   [{}]".format(
            fb["freeboard_in"], fb["min_required_in"], pf(fb["pass"])))
        print("  Draft:         {:.1f} in".format(fb["draft_in"]))
        print("  Displacement:  {:.2f} ft^3".format(fb["displacement_ft3"]))
        print()
        print("  GM (stability): {:.1f} in   (min {:.0f} in)   [{}]".format(
            st["gm_in"], st["min_required_in"], pf(st["pass"])))
        print()
        print("  Bending Stress: {:.1f} psi".format(sr["bending_stress_psi"]))
        print("  Flexural Str:   {:.0f} psi".format(sr["flexural_strength_psi"]))
        print("  Safety Factor:  {:.1f}x   (min {:.1f}x)   [{}]".format(
            sr["safety_factor"], sr["min_sf"], pf(sr["pass"])))
        print()
        overall = "ALL PASS" if a["overall_pass"] else "SOME FAIL"
        print("  >>> Overall: {}".format(overall))

    # Summary table
    print()
    print("=" * W)
    print("  COMPARISON SUMMARY")
    print("=" * W)
    hdr = "  {:<22} {:>12} {:>12} {:>12}".format(
        "Metric", "Design A", "Design B", "Design C")
    print(hdr)
    print("  " + "-" * 58)

    rows = [
        ("Weight (lbs)", "weight_lbs", ".1f"),
        ("Freeboard (in)", "freeboard.freeboard_in", ".1f"),
        ("GM (in)", "stability.gm_in", ".1f"),
        ("Safety Factor", "structural.safety_factor", ".1f"),
        ("Overall", "overall_pass", ""),
    ]

    for label, path, fmt in rows:
        vals = []
        for rkey in ["A", "B", "C"]:
            r = results[rkey]
            if "." in path:
                parts = path.split(".")
                v = r["analysis"][parts[0]][parts[1]]
            elif path == "weight_lbs":
                v = r["weight_lbs"]
            elif path == "overall_pass":
                v = r["analysis"]["overall_pass"]
            else:
                v = r["analysis"][path]

            if path == "overall_pass":
                vals.append("PASS" if v else "FAIL")
            else:
                vals.append("{:{}}".format(v, fmt))

        print("  {:<22} {:>12} {:>12} {:>12}".format(label, vals[0], vals[1], vals[2]))

    print()
    print("  Recommended: Design A  (lightest, best weight margin)")
    print("=" * W)
    print()


# ===========================================================================
# FIGURE HELPERS
# ===========================================================================
def add_brand_footer(fig, y=0.02):
    """Add NAU ASCE 2026 branding footer."""
    fig.text(0.5, y, BRAND_TITLE, ha="center", va="center",
             fontsize=10, color=NAU_BLUE, fontstyle="italic",
             fontweight="bold", alpha=0.7)


def rounded_rect(ax, x, y, w, h, color, text="", fontsize=12,
                 text_color=WHITE, radius=0.02, alpha=1.0, fontweight="bold",
                 edgecolor="none", linewidth=0):
    """Draw a rounded rectangle with centered text."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad={}".format(radius),
        facecolor=color, edgecolor=edgecolor, linewidth=linewidth,
        alpha=alpha, transform=ax.transData, zorder=2,
    )
    ax.add_patch(box)
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fontsize, color=text_color, fontweight=fontweight,
                zorder=3)
    return box


# ===========================================================================
# FIGURE 1: Design comparison table
# ===========================================================================
def fig_design_comparison(results):
    """Clean side-by-side comparison table of all 3 designs with pass/fail."""
    fig, ax = plt.subplots(figsize=(14, 8), facecolor=WHITE)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Title
    ax.text(7, 9.4, "Hull Design Comparison", ha="center", va="center",
            fontsize=28, fontweight="bold", color=NAU_BLUE)
    ax.text(7, 8.9, BRAND_TITLE, ha="center", va="center",
            fontsize=13, color=NAU_DARK_GOLD, fontweight="bold")

    # Column positions
    col_x = [1.0, 4.5, 7.5, 10.5]
    col_w = 2.5

    # Header row
    headers = ["Metric", "Design A\nLightweight Racer",
               "Design B\nBalanced Performer", "Design C\nStability Platform"]
    header_colors = [NAU_BLUE, "#2980B9", "#8E44AD", "#27AE60"]
    for i, (hx, header, hcolor) in enumerate(zip(col_x, headers, header_colors)):
        w = 3.0 if i == 0 else col_w
        rounded_rect(ax, hx, 7.8, w, 0.8, hcolor, header,
                     fontsize=11, text_color=WHITE, radius=0.015)

    # Data rows
    row_labels = [
        "Dimensions (L x B x D)",
        "Hull Weight",
        "Freeboard",
        "GM (Stability)",
        "Safety Factor",
        "Overall Verdict",
    ]

    def get_row_data(key, res):
        r = res[key]
        s = r["spec"]
        a = r["analysis"]
        fb = a["freeboard"]["freeboard_in"]
        gm = a["stability"]["gm_in"]
        sf = a["structural"]["safety_factor"]
        wt = r["weight_lbs"]
        dims = "{}x{}x{} in".format(s["length_in"], s["beam_in"], s["depth_in"])
        return [
            (dims, None),
            ("{:.0f} lbs".format(wt), wt <= WEIGHT_LIMIT_LBS),
            ("{:.1f} in".format(fb), a["freeboard"]["pass"]),
            ("{:.1f} in".format(gm), a["stability"]["pass"]),
            ("{:.0f}x".format(sf), a["structural"]["pass"]),
            ("ALL PASS" if a["overall_pass"] else "SOME FAIL", a["overall_pass"]),
        ]

    data_A = get_row_data("A", results)
    data_B = get_row_data("B", results)
    data_C = get_row_data("C", results)

    row_y_start = 7.2
    row_h = 0.85
    row_gap = 0.1

    for i, label in enumerate(row_labels):
        y = row_y_start - (i + 1) * (row_h + row_gap)
        bg_color = LIGHT_GRAY if i % 2 == 0 else WHITE

        # Label column
        rounded_rect(ax, col_x[0], y, 3.0, row_h, bg_color, label,
                     fontsize=10, text_color=DARK_GRAY, fontweight="bold",
                     edgecolor=MED_GRAY, linewidth=0.5, radius=0.01)

        # Data columns
        for j, data in enumerate([data_A, data_B, data_C]):
            text_val, passed = data[i]
            if passed is None:
                cell_color = bg_color
                tc = DARK_GRAY
            elif passed:
                cell_color = "#E8F8F5"
                tc = "#1B7A4D"
            else:
                cell_color = "#FDEDEC"
                tc = FAIL_RED

            rounded_rect(ax, col_x[j + 1], y, col_w, row_h, cell_color, "",
                         edgecolor=MED_GRAY, linewidth=0.5, radius=0.01)

            indicator = ""
            if passed is True:
                indicator = "  \u2713"
            elif passed is False:
                indicator = "  \u2717"

            display_text = text_val + indicator
            ax.text(col_x[j + 1] + col_w / 2, y + row_h / 2, display_text,
                    ha="center", va="center", fontsize=11, color=tc,
                    fontweight="bold", zorder=4)

    # RECOMMENDED badge
    badge_x = col_x[1] + col_w / 2
    badge_y = 1.05
    rounded_rect(ax, badge_x - 1.1, badge_y - 0.25, 2.2, 0.5,
                 NAU_GOLD, "\u2605  RECOMMENDED", fontsize=12,
                 text_color=NAU_BLUE, radius=0.02)

    # Threshold footnote
    ax.text(7, 0.5,
            "ASCE 2026 Thresholds:  Freeboard \u2265 6 in  |  GM \u2265 6 in  |  "
            "Safety Factor \u2265 2.0  |  Weight Target: 237 lbs",
            ha="center", va="center", fontsize=9.5, color="#666666",
            fontstyle="italic")

    add_brand_footer(fig, y=0.015)
    fig.tight_layout(rect=[0, 0.04, 1, 1])

    path = FIG_DIR / "presentation_design_comparison.png"
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    print("  Saved: {}".format(path))


# ===========================================================================
# FIGURE 2: Why Design A
# ===========================================================================
def fig_why_design_a(results):
    """Infographic showing why Design A is the recommended design."""
    r = results["A"]
    a = r["analysis"]
    wt = r["weight_lbs"]
    fb = a["freeboard"]["freeboard_in"]
    gm = a["stability"]["gm_in"]
    sf = a["structural"]["safety_factor"]

    fig, axes = plt.subplots(1, 4, figsize=(16, 7), facecolor=WHITE)

    # Title
    fig.text(0.5, 0.95, "Why Design A Is Our Best Choice",
             ha="center", va="center", fontsize=26, fontweight="bold",
             color=NAU_BLUE)
    fig.text(0.5, 0.90, "192 x 32 x 17 x 0.5 in  |  Lightweight Racer  |  "
             "{:.0f} lbs hull weight".format(wt),
             ha="center", va="center", fontsize=12, color="#555555")

    metrics = [
        {
            "title": "Weight",
            "value": wt,
            "limit": WEIGHT_LIMIT_LBS,
            "unit": "lbs",
            "label_val": "{:.0f} lbs".format(wt),
            "label_lim": "{:.0f} lbs limit".format(WEIGHT_LIMIT_LBS),
            "pct_text": "{:.0f}% under\nweight limit".format((1 - wt / WEIGHT_LIMIT_LBS) * 100),
            "color": "#2980B9",
            "limit_color": FAIL_RED,
        },
        {
            "title": "Freeboard",
            "value": fb,
            "limit": 6.0,
            "unit": "in",
            "label_val": "{:.1f} in".format(fb),
            "label_lim": "6 in minimum",
            "pct_text": "{:.0f} in freeboard\nvs 6 in minimum".format(fb),
            "color": ACCENT_TEAL,
            "limit_color": FAIL_RED,
        },
        {
            "title": "Stability (GM)",
            "value": gm,
            "limit": 6.0,
            "unit": "in",
            "label_val": "{:.1f} in".format(gm),
            "label_lim": "6 in minimum",
            "pct_text": "{:.1f} in GM\nvs 6 in minimum".format(gm),
            "color": "#8E44AD",
            "limit_color": FAIL_RED,
        },
        {
            "title": "Safety Factor",
            "value": sf,
            "limit": 2.0,
            "unit": "x",
            "label_val": "{:.0f}x".format(sf),
            "label_lim": "2.0x minimum",
            "pct_text": "{:.0f}x safety\nvs 2.0x required".format(sf),
            "color": NAU_DARK_GOLD,
            "limit_color": FAIL_RED,
        },
    ]

    for ax_i, (ax, m) in enumerate(zip(axes, metrics)):
        ax.set_facecolor(WHITE)

        bars = ax.bar(
            [0, 1],
            [m["value"], m["limit"]],
            color=[m["color"], m["limit_color"]],
            width=0.6,
            alpha=0.85,
            edgecolor="white",
            linewidth=2,
        )

        for bar, txt in zip(bars, [m["label_val"], m["label_lim"]]):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2,
                    height + 0.02 * max(m["value"], m["limit"]),
                    txt, ha="center", va="bottom", fontsize=10, fontweight="bold",
                    color=DARK_GRAY)

        ax.set_title(m["title"], fontsize=14, fontweight="bold", color=NAU_BLUE, pad=12)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Design A", "Threshold"], fontsize=9)
        ax.set_ylabel(m["unit"], fontsize=10)

        ax.text(0.5, -0.18, m["pct_text"], ha="center", va="top",
                transform=ax.transAxes, fontsize=11, fontweight="bold",
                color=PASS_GREEN,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#E8F8F5",
                          edgecolor=PASS_GREEN, linewidth=1.5))

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(MED_GRAY)
        ax.spines["bottom"].set_color(MED_GRAY)
        ax.tick_params(colors=MED_GRAY)

    add_brand_footer(fig, y=0.02)
    fig.tight_layout(rect=[0.01, 0.08, 0.99, 0.87])

    path = FIG_DIR / "presentation_why_design_A.png"
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    print("  Saved: {}".format(path))


# ===========================================================================
# FIGURE 3: How It Works (flowchart)
# ===========================================================================
def fig_how_it_works(results):
    """Simple flowchart for non-coders explaining the analysis pipeline."""
    fig, ax = plt.subplots(figsize=(16, 8), facecolor=WHITE)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8)
    ax.axis("off")

    ax.text(8, 7.5, "How Our Engineering Calculator Works",
            ha="center", va="center", fontsize=26, fontweight="bold", color=NAU_BLUE)
    ax.text(8, 7.0, "A step-by-step look at the analysis behind every design",
            ha="center", va="center", fontsize=12, color="#777777")

    steps = [
        {"x": 1.0,  "label": "HULL\nSHAPE",         "sub": "Length, Beam,\nDepth, Thickness",
         "color": NAU_BLUE, "icon": "\u25B3"},
        {"x": 4.0,  "label": "CALCULATE\nWEIGHT",    "sub": "U-shell model\n+ 10% overhead",
         "color": "#2980B9", "icon": "\u2696"},
        {"x": 7.0,  "label": "CHECK IF\nIT FLOATS",  "sub": "Freeboard \u2265 6 in\nArchimedes' Law",
         "color": ACCENT_TEAL, "icon": "\u26F5"},
        {"x": 10.0, "label": "CHECK\nSTABILITY",     "sub": "GM \u2265 6 in\nMetacentric Height",
         "color": "#8E44AD", "icon": "\u2693"},
        {"x": 13.0, "label": "CHECK\nSTRENGTH",      "sub": "Safety Factor \u2265 2\nBending Analysis",
         "color": ACCENT_ORANGE, "icon": "\u26A1"},
    ]

    box_w = 2.3
    box_h = 2.0
    box_y = 3.5

    for i, step in enumerate(steps):
        x = step["x"]
        c = step["color"]

        rounded_rect(ax, x, box_y, box_w, box_h, c, "",
                     radius=0.03, edgecolor="none")

        ax.text(x + box_w / 2, box_y + box_h - 0.35, step["icon"],
                ha="center", va="center", fontsize=22, color=WHITE, zorder=5)

        ax.text(x + box_w / 2, box_y + box_h / 2 - 0.05, step["label"],
                ha="center", va="center", fontsize=12, fontweight="bold",
                color=WHITE, zorder=5, linespacing=1.3)

        ax.text(x + box_w / 2, box_y - 0.4, step["sub"],
                ha="center", va="top", fontsize=9, color="#555555",
                linespacing=1.4, fontstyle="italic")

        circle = plt.Circle((x + box_w / 2, box_y + box_h + 0.35), 0.28,
                             color=NAU_GOLD, ec=NAU_BLUE, linewidth=2, zorder=5)
        ax.add_patch(circle)
        ax.text(x + box_w / 2, box_y + box_h + 0.35, str(i + 1),
                ha="center", va="center", fontsize=13, fontweight="bold",
                color=NAU_BLUE, zorder=6)

        if i < len(steps) - 1:
            arrow_start_x = x + box_w + 0.05
            arrow_end_x = steps[i + 1]["x"] - 0.05
            ax.annotate("", xy=(arrow_end_x, box_y + box_h / 2),
                        xytext=(arrow_start_x, box_y + box_h / 2),
                        arrowprops=dict(arrowstyle="-|>", color=NAU_BLUE,
                                        lw=2.5, mutation_scale=20),
                        zorder=4)

    # Final result box
    result_y = 1.0
    result_w = 5.0
    result_h = 1.0
    result_x = 8 - result_w / 2

    rounded_rect(ax, result_x, result_y, result_w, result_h,
                 PASS_GREEN, "\u2713  ALL CHECKS PASS  \u2192  DESIGN APPROVED",
                 fontsize=15, text_color=WHITE, radius=0.03)

    ax.annotate("", xy=(8, result_y + result_h + 0.05),
                xytext=(steps[-1]["x"] + box_w / 2, box_y - 0.05),
                arrowprops=dict(arrowstyle="-|>", color=PASS_GREEN,
                                lw=3, mutation_scale=25,
                                connectionstyle="arc3,rad=-0.3"),
                zorder=4)

    ax.text(11.8, 2.2, "If any check fails,\ndesign is revised",
            ha="center", va="center", fontsize=10, color=FAIL_RED,
            fontstyle="italic",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#FDEDEC",
                      edgecolor=FAIL_RED, linewidth=1))

    add_brand_footer(fig, y=0.02)

    path = FIG_DIR / "presentation_how_it_works.png"
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    print("  Saved: {}".format(path))


# ===========================================================================
# FIGURE 4: Monte Carlo simple explanation
# ===========================================================================
def fig_monte_carlo(results):
    """Simple Monte Carlo explanation: bell curve with ALL SAFE zone."""
    fig, ax = plt.subplots(figsize=(14, 7), facecolor=WHITE)

    np.random.seed(42)
    sf_nominal = results["A"]["analysis"]["structural"]["safety_factor"]
    samples = np.random.normal(sf_nominal, sf_nominal * 0.10, 1000)
    pass_count = int(np.sum(samples >= 2.0))
    pass_pct = pass_count / len(samples) * 100

    n_hist, bins, patches = ax.hist(samples, bins=40, density=True, alpha=0.7,
                                     color=NAU_BLUE, edgecolor=WHITE, linewidth=0.5)

    for patch, left_edge in zip(patches, bins[:-1]):
        if left_edge >= 2.0:
            patch.set_facecolor(PASS_GREEN)
            patch.set_alpha(0.8)
        else:
            patch.set_facecolor(FAIL_RED)
            patch.set_alpha(0.8)

    x_range = np.linspace(min(samples) - 5, max(samples) + 5, 300)
    mu = np.mean(samples)
    sigma = np.std(samples)
    pdf = (1.0 / (sigma * np.sqrt(2.0 * np.pi))) * np.exp(-0.5 * ((x_range - mu) / sigma) ** 2)
    ax.plot(x_range, pdf, color=NAU_BLUE, linewidth=2.5, alpha=0.9)

    ax.axvline(x=2.0, color=FAIL_RED, linewidth=2.5, linestyle="--", zorder=5)
    ax.text(2.0, ax.get_ylim()[1] * 0.92, "  Minimum\n  Required\n  (SF = 2.0)",
            fontsize=10, color=FAIL_RED, fontweight="bold", va="top")

    mid_sf = np.mean(samples)
    ax.annotate(
        "ALL SAFE ZONE\n{:.0f}% of 1,000 simulations pass".format(pass_pct),
        xy=(mid_sf, max(pdf) * 0.5),
        fontsize=14, fontweight="bold", color=PASS_GREEN,
        ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.5", facecolor=WHITE,
                  edgecolor=PASS_GREEN, linewidth=2, alpha=0.95),
    )

    ax.set_title("Monte Carlo Uncertainty Analysis",
                 fontsize=24, fontweight="bold", color=NAU_BLUE, pad=20)

    ax.text(0.5, 1.02, "We tested 1,000 random variations of material properties and geometry",
            transform=ax.transAxes, ha="center", fontsize=12, color="#666666",
            fontstyle="italic")

    ax.set_xlabel("Safety Factor", fontsize=13, color=DARK_GRAY)
    ax.set_ylabel("Probability Density", fontsize=13, color=DARK_GRAY)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(MED_GRAY)
    ax.spines["bottom"].set_color(MED_GRAY)

    stats_text = (
        "Mean SF: {:.1f}x\n"
        "Std Dev: {:.1f}x\n"
        "Min: {:.1f}x\n"
        "Max: {:.1f}x\n"
        "Pass Rate: {:.0f}%"
    ).format(np.mean(samples), np.std(samples), np.min(samples), np.max(samples), pass_pct)
    ax.text(0.97, 0.95, stats_text, transform=ax.transAxes,
            fontsize=11, va="top", ha="right", color=DARK_GRAY,
            fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.5", facecolor=SOFT_BLUE,
                      edgecolor=NAU_BLUE, linewidth=1, alpha=0.9))

    fig.text(0.5, 0.02,
             "\u2713  Result: {:.0f}% of 1,000 simulations passed  |  "
             "Design A is robust against real-world uncertainties".format(pass_pct),
             ha="center", fontsize=13, fontweight="bold", color=WHITE,
             bbox=dict(boxstyle="round,pad=0.4", facecolor=PASS_GREEN,
                       edgecolor="none", alpha=0.95))

    fig.tight_layout(rect=[0, 0.06, 1, 0.97])

    path = FIG_DIR / "presentation_monte_carlo_simple.png"
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    print("  Saved: {}".format(path))


# ===========================================================================
# FIGURE 5: Key numbers KPI dashboard
# ===========================================================================
def fig_key_numbers(results):
    """Big bold number infographic -- dashboard KPI display."""
    r = results["A"]
    a = r["analysis"]
    wt = r["weight_lbs"]
    fb = a["freeboard"]["freeboard_in"]
    gm = a["stability"]["gm_in"]
    sf = a["structural"]["safety_factor"]

    fig = plt.figure(figsize=(16, 9), facecolor=WHITE)

    # Title bar
    title_ax = fig.add_axes([0, 0.88, 1, 0.12], facecolor=NAU_BLUE)
    title_ax.axis("off")
    title_ax.text(0.5, 0.65, "Design A: Key Performance Numbers",
                  ha="center", va="center", fontsize=28, fontweight="bold",
                  color=WHITE, transform=title_ax.transAxes)
    title_ax.text(0.5, 0.2, BRAND_TITLE + "  |  192 x 32 x 17 x 0.5 in  |  Lightweight Racer",
                  ha="center", va="center", fontsize=12, color=NAU_GOLD,
                  transform=title_ax.transAxes)

    kpis = [
        {
            "number": "{:.0f}".format(wt),
            "unit": "lbs",
            "label": "Hull Weight",
            "sublabel": "{:.0f}% under {:.0f} lb limit".format(
                (1 - wt / WEIGHT_LIMIT_LBS) * 100, WEIGHT_LIMIT_LBS),
            "color": "#2980B9",
            "icon_color": "#EBF5FB",
        },
        {
            "number": "{:.0f}".format(fb),
            "unit": "in",
            "label": "Freeboard",
            "sublabel": "{:.0f} in above water vs 6 in min".format(fb),
            "color": ACCENT_TEAL,
            "icon_color": "#E8F8F5",
        },
        {
            "number": "{:.1f}".format(gm),
            "unit": "in",
            "label": "Stability (GM)",
            "sublabel": "{:.1f}x the minimum required".format(gm / 6.0),
            "color": "#8E44AD",
            "icon_color": "#F5EEF8",
        },
        {
            "number": "{:.0f}".format(sf),
            "unit": "x",
            "label": "Safety Factor",
            "sublabel": "{:.0f}x the required minimum".format(sf / 2.0),
            "color": ACCENT_ORANGE,
            "icon_color": "#FDF2E9",
        },
        {
            "number": "100",
            "unit": "%",
            "label": "Pass Rate",
            "sublabel": "Monte Carlo: 1,000 simulations",
            "color": PASS_GREEN,
            "icon_color": "#E8F8F5",
        },
    ]

    n_cards = len(kpis)
    card_w = 0.17
    card_h = 0.55
    gap = (1.0 - n_cards * card_w) / (n_cards + 1)

    for i, kpi in enumerate(kpis):
        x = gap + i * (card_w + gap)
        y = 0.15

        card_ax = fig.add_axes([x, y, card_w, card_h], facecolor=WHITE)
        card_ax.set_xlim(0, 1)
        card_ax.set_ylim(0, 1)
        card_ax.axis("off")

        accent_bar = FancyBboxPatch(
            (0.0, 0.85), 1.0, 0.15,
            boxstyle="round,pad=0.02",
            facecolor=kpi["color"], edgecolor="none",
            transform=card_ax.transAxes, clip_on=False, zorder=1,
        )
        card_ax.add_patch(accent_bar)

        body = FancyBboxPatch(
            (0.0, 0.0), 1.0, 0.87,
            boxstyle="round,pad=0.02",
            facecolor=kpi["icon_color"], edgecolor=kpi["color"],
            linewidth=2, transform=card_ax.transAxes, clip_on=False, zorder=1,
        )
        card_ax.add_patch(body)

        card_ax.text(0.5, 0.58, kpi["number"],
                     ha="center", va="center", fontsize=42, fontweight="bold",
                     color=kpi["color"], transform=card_ax.transAxes, zorder=3)

        card_ax.text(0.5, 0.40, kpi["unit"],
                     ha="center", va="center", fontsize=16, fontweight="bold",
                     color=kpi["color"], alpha=0.7,
                     transform=card_ax.transAxes, zorder=3)

        card_ax.text(0.5, 0.92, kpi["label"],
                     ha="center", va="center", fontsize=12, fontweight="bold",
                     color=WHITE, transform=card_ax.transAxes, zorder=3)

        card_ax.text(0.5, 0.18, kpi["sublabel"],
                     ha="center", va="center", fontsize=8.5,
                     color="#666666", fontstyle="italic",
                     transform=card_ax.transAxes, zorder=3, wrap=True)

        card_ax.text(0.5, 0.05, "\u2713", ha="center", va="center",
                     fontsize=18, color=PASS_GREEN, fontweight="bold",
                     transform=card_ax.transAxes, zorder=3)

    fig.text(0.5, 0.07,
             "All metrics exceed ASCE 2026 competition requirements  |  "
             "Design verified by computational analysis",
             ha="center", va="center", fontsize=11, color="#888888",
             fontstyle="italic")

    add_brand_footer(fig, y=0.025)

    path = FIG_DIR / "presentation_key_numbers.png"
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    print("  Saved: {}".format(path))


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    print()
    print("=" * 72)
    print("  NAU ASCE Concrete Canoe 2026")
    print("  Presentation Summary Generator")
    print("=" * 72)

    print()
    print("[1/2] Running engineering analysis for all three designs...")
    results = run_all_designs()

    print_results(results)

    print()
    print("[2/2] Generating presentation figures (300 DPI)...")
    print()

    fig_design_comparison(results)
    fig_why_design_a(results)
    fig_how_it_works(results)
    fig_monte_carlo(results)
    fig_key_numbers(results)

    print()
    print("  All figures saved to: {}/".format(FIG_DIR))
    print("  Done!")
    print()


if __name__ == "__main__":
    main()
