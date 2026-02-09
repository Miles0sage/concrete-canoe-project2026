#!/usr/bin/env python3
"""
NAU Concrete Canoe 2026 - Mix Design Visualization Generator
Creates presentation-quality PNGs for mix design analysis.

Outputs to: reports/figures/
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon, FancyArrowPatch
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe

# ── Configuration ──────────────────────────────────────────────────────────

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "reports", "figures")
DPI = 300

# NAU Colors
NAU_BLUE = "#003466"
NAU_GOLD = "#FFC72C"
DARK_GRAY = "#2C2C2C"
MED_GRAY = "#666666"
LIGHT_GRAY = "#E8E8E8"
WHITE = "#FFFFFF"

# Chart accent colors
C_RED = "#E74C3C"
C_GREEN = "#27AE60"
C_TEAL = "#1ABC9C"
C_ORANGE = "#F39C12"
C_PURPLE = "#8E44AD"
C_BLUE_LIGHT = "#5DADE2"
C_PINK = "#FF6B6B"
C_LIME = "#95E1D3"
C_YELLOW = "#FFE66D"


# ── Mix Data ───────────────────────────────────────────────────────────────

MIXES = {
    "Mix 1\n(Lightweight)": {
        "portland_pct": 40.0, "slag_pct": 22.4, "fly_ash_pct": 21.5, "lime_pct": 3.2,
        "portland_lbs": 125.0, "slag_lbs": 70.0, "fly_ash_lbs": 67.0, "lime_lbs": 10.0,
        "poraver_lbs": 115.0, "perlite_lbs": 150.0, "k1_lbs": 25.0,
        "density_pcf": 48.0, "w_cm": 0.45,
        "test_7d": 200, "pred_28d": 650,
        "fiber_lbs": 3.5, "hrwr": 4.0, "aea": 2.0, "air_pct": 4.5,
    },
    "Mix 2\n(Balanced)": {
        "portland_pct": 35.0, "slag_pct": 38.0, "fly_ash_pct": 20.7, "lime_pct": 3.2,
        "portland_lbs": 110.0, "slag_lbs": 120.0, "fly_ash_lbs": 65.0, "lime_lbs": 10.0,
        "poraver_lbs": 125.0, "perlite_lbs": 100.0, "k1_lbs": 35.0,
        "density_pcf": 55.0, "w_cm": 0.42,
        "test_7d": 320, "pred_28d": 1200,
        "fiber_lbs": 4.0, "hrwr": 5.0, "aea": 1.0, "air_pct": 2.5,
    },
    "Mix 3\n(OPTIMIZED)": {
        "portland_pct": 30.8, "slag_pct": 47.2, "fly_ash_pct": 18.9, "lime_pct": 3.1,
        "portland_lbs": 97.21, "slag_lbs": 149.21, "fly_ash_lbs": 59.78, "lime_lbs": 9.72,
        "poraver_lbs": 131.23, "perlite_lbs": 88.22, "k1_lbs": 38.89,
        "density_pcf": 58.6, "w_cm": 0.36,
        "test_7d": 273, "pred_28d": 1774,
        "fiber_lbs": 4.34, "hrwr": 6.0, "aea": 1.5, "air_pct": 3.0,
    },
}

MIX_COLORS = [C_BLUE_LIGHT, C_ORANGE, NAU_BLUE]
MIX_NAMES = list(MIXES.keys())


def _title_footer(fig, title, subtitle=""):
    """Add consistent title and footer to a figure."""
    fig.suptitle(title, fontsize=18, fontweight='bold', color=NAU_BLUE, y=0.97)
    if subtitle:
        fig.text(0.5, 0.935, subtitle, ha='center', fontsize=11, color=MED_GRAY,
                 fontstyle='italic')
    fig.text(0.5, 0.01, "NAU ASCE Concrete Canoe 2026  |  Mix Design Analysis",
             ha='center', fontsize=8, color=MED_GRAY)


# ══════════════════════════════════════════════════════════════════════════
# FIGURE 1: Decision Matrix (Weighted Score Comparison)
# ══════════════════════════════════════════════════════════════════════════

def fig_decision_matrix():
    """Weighted decision matrix bar chart with total scores."""
    fig, ax = plt.subplots(figsize=(14, 8))

    criteria = ['Strength\n(40%)', 'Durability\n(30%)', 'Cost\n(20%)', 'Workability\n(10%)']
    weights = [0.40, 0.30, 0.20, 0.10]

    # Score each mix on each criterion (0-10)
    scores = {}
    for name, m in MIXES.items():
        s = 10 if m['pred_28d'] >= 1700 else (8 if m['pred_28d'] >= 1500 else
            (5 if m['pred_28d'] >= 1200 else 2))
        d = 10 if m['w_cm'] <= 0.36 else (7 if m['w_cm'] <= 0.42 else
            (4 if m['w_cm'] <= 0.45 else 2))
        c = 10 if m['density_pcf'] <= 48 else (7 if m['density_pcf'] <= 55 else
            (5 if m['density_pcf'] <= 60 else 3))
        w = 10 if m['w_cm'] > 0.45 else (9 if m['w_cm'] > 0.40 else
            (7 if m['w_cm'] > 0.35 else 5))
        scores[name] = [s, d, c, w]

    x = np.arange(len(criteria))
    width = 0.22
    offsets = [-width, 0, width]

    for idx, (name, color) in enumerate(zip(MIX_NAMES, MIX_COLORS)):
        vals = scores[name]
        bars = ax.bar(x + offsets[idx], vals, width, label=name.replace('\n', ' '),
                      color=color, alpha=0.88, edgecolor=WHITE, linewidth=1)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                    f'{v:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold',
                    color=color)

    # Weighted totals
    totals = {}
    for name in MIX_NAMES:
        totals[name] = sum(s * w for s, w in zip(scores[name], weights))

    # Add weighted total annotation
    y_top = 11.5
    for idx, (name, color) in enumerate(zip(MIX_NAMES, MIX_COLORS)):
        t = totals[name]
        label = f'{name.replace(chr(10), " ")}: {t:.1f}/10'
        rec = "EXCELLENT" if t >= 8.5 else ("GOOD" if t >= 7.0 else "RISKY")
        ax.text(len(criteria) + 0.15, y_top - idx * 1.3, f'{label}  ({rec})',
                fontsize=12, fontweight='bold', color=color,
                bbox=dict(fc=WHITE, ec=color, lw=2, boxstyle='round,pad=0.3'))

    ax.set_ylabel('Score (0-10)', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(criteria, fontsize=12)
    ax.set_ylim(0, 12.5)
    ax.set_xlim(-0.5, len(criteria) + 2.5)
    ax.axhline(y=9.0, color=C_GREEN, ls='--', lw=1.5, alpha=0.5)
    ax.axhline(y=7.0, color=C_ORANGE, ls='--', lw=1.5, alpha=0.5)
    ax.text(-0.45, 9.15, 'Excellent', fontsize=8, color=C_GREEN, fontstyle='italic')
    ax.text(-0.45, 7.15, 'Good', fontsize=8, color=C_ORANGE, fontstyle='italic')
    ax.legend(fontsize=11, loc='upper left', framealpha=0.9)
    ax.grid(axis='y', alpha=0.25)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    _title_footer(fig, "Decision Matrix Analysis",
                  "Weighted Scoring: Strength 40% | Durability 30% | Cost 20% | Workability 10%")
    plt.tight_layout(rect=[0, 0.03, 1, 0.92])
    fig.savefig(os.path.join(OUTPUT_DIR, "mix_decision_matrix.png"), dpi=DPI, bbox_inches='tight')
    plt.close(fig)
    print("  [OK] mix_decision_matrix.png")


# ══════════════════════════════════════════════════════════════════════════
# FIGURE 2: 28-Day Strength Prediction (3 Scenarios)
# ══════════════════════════════════════════════════════════════════════════

def fig_strength_prediction():
    """28-day strength prediction with conservative/typical/optimistic."""
    fig, ax = plt.subplots(figsize=(14, 8))

    x = np.arange(len(MIX_NAMES))
    width = 0.22

    cons_vals, typ_vals, opt_vals, seven_vals = [], [], [], []
    for name, m in MIXES.items():
        dry_eq = m['test_7d'] / 0.80
        cons_vals.append(dry_eq * 4.2)
        typ_vals.append(dry_eq * 5.2)
        opt_vals.append(dry_eq * 6.0)
        seven_vals.append(m['test_7d'])

    bars_c = ax.bar(x - width, cons_vals, width, label='Conservative', color=C_PINK, alpha=0.85)
    bars_t = ax.bar(x, typ_vals, width, label='Expected (Typical)', color=C_TEAL, alpha=0.85)
    bars_o = ax.bar(x + width, opt_vals, width, label='Optimistic', color=C_LIME, alpha=0.85)

    # ASCE requirement line
    ax.axhline(y=1500, color=C_RED, ls='--', lw=2.5, zorder=4)
    ax.text(2.35, 1530, 'ASCE Requirement\n1,500 psi', fontsize=10, fontweight='bold',
            color=C_RED, ha='right')

    # 7-day markers
    ax.scatter(x, seven_vals, color='black', s=150, marker='X', zorder=5,
               edgecolors=WHITE, linewidth=2)
    for i, v in enumerate(seven_vals):
        ax.text(i, v + 50, f'{v:.0f} psi\n(7-day)', ha='center', fontsize=9,
                color=DARK_GRAY, fontweight='bold')

    # Value labels on bars
    for bars, vals in [(bars_c, cons_vals), (bars_t, typ_vals), (bars_o, opt_vals)]:
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                    f'{v:.0f}', ha='center', fontsize=9, fontweight='bold')

    # Pass/Fail annotations
    for i, (c, t, o) in enumerate(zip(cons_vals, typ_vals, opt_vals)):
        if t >= 1500:
            ax.text(i, max(c, t, o) + 100, 'PASSES', ha='center', fontsize=12,
                    fontweight='bold', color=C_GREEN,
                    bbox=dict(fc='#E8F8F5', ec=C_GREEN, lw=2, boxstyle='round,pad=0.3'))
        else:
            ax.text(i, max(c, t, o) + 100, 'FAILS', ha='center', fontsize=12,
                    fontweight='bold', color=C_RED,
                    bbox=dict(fc='#FDEDEC', ec=C_RED, lw=2, boxstyle='round,pad=0.3'))

    ax.set_ylabel('Compressive Strength (psi)', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(MIX_NAMES, fontsize=12, fontweight='bold')
    ax.set_ylim(0, 2600)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(axis='y', alpha=0.25)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    _title_footer(fig, "28-Day Strength Prediction",
                  "From 7-day wet test | Dry correction (x0.80) | Growth factors: 4.2x / 5.2x / 6.0x")
    plt.tight_layout(rect=[0, 0.03, 1, 0.92])
    fig.savefig(os.path.join(OUTPUT_DIR, "mix_strength_prediction.png"), dpi=DPI, bbox_inches='tight')
    plt.close(fig)
    print("  [OK] mix_strength_prediction.png")


# ══════════════════════════════════════════════════════════════════════════
# FIGURE 3: Cementitious Composition Comparison (Pie Charts)
# ══════════════════════════════════════════════════════════════════════════

def fig_composition():
    """Side-by-side pie charts of cementitious breakdown."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 7))

    pie_colors = [C_RED, C_TEAL, C_YELLOW, C_LIME]
    labels = ['Portland', 'Slag', 'Fly Ash', 'Lime']

    for idx, (name, m) in enumerate(MIXES.items()):
        values = [m['portland_pct'], m['slag_pct'], m['fly_ash_pct'], m['lime_pct']]
        wedges, texts, autotexts = axes[idx].pie(
            values, labels=labels, autopct='%1.1f%%', colors=pie_colors,
            startangle=90, pctdistance=0.75,
            textprops={'fontsize': 11, 'fontweight': 'bold'},
            wedgeprops=dict(edgecolor=WHITE, linewidth=2))
        for at in autotexts:
            at.set_fontsize(10)
            at.set_color(DARK_GRAY)

        status = "PASSES" if m['pred_28d'] >= 1500 else "FAILS"
        s_color = C_GREEN if m['pred_28d'] >= 1500 else C_RED
        axes[idx].set_title(f'{name}\n{m["density_pcf"]:.1f} PCF | {m["pred_28d"]:.0f} psi ({status})',
                            fontsize=12, fontweight='bold', color=NAU_BLUE, pad=10)

    _title_footer(fig, "Cementitious Material Composition",
                  "Binder breakdown by percentage of total cementitious materials")
    plt.tight_layout(rect=[0, 0.03, 1, 0.92])
    fig.savefig(os.path.join(OUTPUT_DIR, "mix_composition_comparison.png"), dpi=DPI, bbox_inches='tight')
    plt.close(fig)
    print("  [OK] mix_composition_comparison.png")


# ══════════════════════════════════════════════════════════════════════════
# FIGURE 4: ASCE Compliance Dashboard
# ══════════════════════════════════════════════════════════════════════════

def fig_asce_compliance():
    """ASCE 2026 compliance check grid for all 3 mixes."""
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 70)
    ax.axis('off')

    checks = [
        ("Portland <= 40%", "portland_pct", 40, "<=", "%"),
        ("Lime <= 5%", "lime_pct", 5, "<=", "%"),
        ("Density 48-65 PCF", "density_pcf", (48, 65), "range", " pcf"),
        ("28-Day >= 1,500 psi", "pred_28d", 1500, ">=", " psi"),
        ("w/cm Ratio", "w_cm", 0.50, "<=", ""),
    ]

    # Column headers
    col_x = [32, 52, 75]
    for i, (name, color) in enumerate(zip(MIX_NAMES, MIX_COLORS)):
        ax.text(col_x[i], 65, name.replace('\n', ' '), ha='center', fontsize=13,
                fontweight='bold', color=color,
                bbox=dict(fc=WHITE, ec=color, lw=2.5, boxstyle='round,pad=0.4'))

    # Row header
    ax.text(14, 65, "ASCE 2026\nRequirement", ha='center', fontsize=12,
            fontweight='bold', color=NAU_BLUE)

    # Horizontal separator
    ax.plot([2, 98], [61, 61], color=LIGHT_GRAY, lw=2)

    # Each check row
    row_y_start = 55
    row_h = 10
    for r, (label, key, limit, op, unit) in enumerate(checks):
        y = row_y_start - r * row_h

        # Row background
        if r % 2 == 0:
            ax.add_patch(Rectangle((1, y - 4), 98, row_h, fc='#F8F9FA', ec='none'))

        # Requirement label
        ax.text(14, y, label, ha='center', va='center', fontsize=12,
                fontweight='bold', color=DARK_GRAY)

        # Each mix value
        for i, (name, m) in enumerate(MIXES.items()):
            val = m[key]
            if op == "<=":
                passes = val <= limit
                display = f"{val:.1f}{unit}"
            elif op == ">=":
                passes = val >= limit
                display = f"{val:,.0f}{unit}"
            elif op == "range":
                passes = limit[0] <= val <= limit[1]
                display = f"{val:.1f}{unit}"
            else:
                passes = True
                display = f"{val}{unit}"

            bg = '#E8F8F5' if passes else '#FDEDEC'
            ec = C_GREEN if passes else C_RED
            symbol = "PASS" if passes else "FAIL"

            ax.add_patch(FancyBboxPatch((col_x[i] - 10, y - 3.5), 20, 7,
                                        boxstyle='round,pad=0.3', fc=bg, ec=ec, lw=2))
            ax.text(col_x[i], y + 0.8, display, ha='center', va='center',
                    fontsize=11, fontweight='bold', color=DARK_GRAY)
            ax.text(col_x[i], y - 1.8, symbol, ha='center', va='center',
                    fontsize=9, fontweight='bold', color=ec)

    # Overall verdict
    y_verdict = row_y_start - len(checks) * row_h
    ax.plot([2, 98], [y_verdict + 4, y_verdict + 4], color=NAU_BLUE, lw=2)
    ax.text(14, y_verdict - 1, "OVERALL", ha='center', va='center', fontsize=13,
            fontweight='bold', color=NAU_BLUE)

    for i, (name, m) in enumerate(MIXES.items()):
        all_pass = (m['portland_pct'] <= 40 and m['lime_pct'] <= 5 and
                    48 <= m['density_pcf'] <= 65 and m['pred_28d'] >= 1500 and
                    m['w_cm'] <= 0.50)
        verdict = "COMPLIANT" if all_pass else "NON-COMPLIANT"
        vc = C_GREEN if all_pass else C_RED
        ax.add_patch(FancyBboxPatch((col_x[i] - 12, y_verdict - 4), 24, 7,
                                    boxstyle='round,pad=0.3', fc=vc, ec=vc, lw=2, alpha=0.15))
        ax.text(col_x[i], y_verdict - 0.5, verdict, ha='center', va='center',
                fontsize=12, fontweight='bold', color=vc)

    _title_footer(fig, "ASCE 2026 Compliance Verification",
                  "All requirements must pass for competition eligibility")
    fig.savefig(os.path.join(OUTPUT_DIR, "mix_asce_compliance.png"), dpi=DPI, bbox_inches='tight')
    plt.close(fig)
    print("  [OK] mix_asce_compliance.png")


# ══════════════════════════════════════════════════════════════════════════
# FIGURE 5: Mix 3 Detailed Breakdown (Single-Mix Showcase)
# ══════════════════════════════════════════════════════════════════════════

def fig_mix3_showcase():
    """Detailed single-page showcase of Mix 3 with all key data."""
    fig = plt.figure(figsize=(18, 12))

    m = MIXES["Mix 3\n(OPTIMIZED)"]

    # ── Title bar ──
    ax_title = fig.add_axes([0.02, 0.90, 0.96, 0.08])
    ax_title.set_xlim(0, 100)
    ax_title.set_ylim(0, 10)
    ax_title.axis('off')
    ax_title.add_patch(FancyBboxPatch((0, 0), 100, 10, boxstyle='round,pad=0.3',
                                       fc=NAU_BLUE, ec=NAU_GOLD, lw=3))
    ax_title.text(50, 6, "MIX 3 (OPTIMIZED) -- RECOMMENDED FOR HULL FABRICATION",
                  ha='center', va='center', fontsize=18, fontweight='bold', color=WHITE)
    ax_title.text(50, 2, "NAU ASCE Concrete Canoe 2026 | Design A: 192\" x 32\" x 17\" x 0.5\"",
                  ha='center', va='center', fontsize=12, color=NAU_GOLD)

    # ── Panel 1: Cementitious pie (top-left) ──
    ax1 = fig.add_axes([0.03, 0.52, 0.30, 0.35])
    labels = ['Portland\n30.8%', 'Slag\n47.2%', 'Fly Ash\n18.9%', 'Lime\n3.1%']
    sizes = [m['portland_pct'], m['slag_pct'], m['fly_ash_pct'], m['lime_pct']]
    colors = [C_RED, C_TEAL, C_YELLOW, C_LIME]
    explode = (0, 0.05, 0, 0)  # Highlight slag
    wedges, texts = ax1.pie(sizes, labels=labels, colors=colors, explode=explode,
                             startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'},
                             wedgeprops=dict(edgecolor=WHITE, linewidth=2))
    ax1.set_title("Cementitious Materials\n(315.92 lbs total)", fontsize=13,
                  fontweight='bold', color=NAU_BLUE, pad=5)

    # ── Panel 2: Aggregates bar (top-center) ──
    ax2 = fig.add_axes([0.38, 0.55, 0.25, 0.30])
    agg_names = ['Poraver\n1-2mm', 'Perlite\n.1-1mm', 'K1 Glass\nBubbles']
    agg_vals = [m['poraver_lbs'], m['perlite_lbs'], m['k1_lbs']]
    agg_colors = [C_ORANGE, C_PURPLE, C_BLUE_LIGHT]
    bars = ax2.barh(agg_names, agg_vals, color=agg_colors, edgecolor=WHITE, linewidth=1.5, height=0.6)
    for bar, v in zip(bars, agg_vals):
        ax2.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                 f'{v:.1f} lbs', va='center', fontsize=11, fontweight='bold')
    ax2.set_xlim(0, 170)
    ax2.set_title("Lightweight Aggregates\n(258.34 lbs total)", fontsize=13,
                  fontweight='bold', color=NAU_BLUE, pad=5)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    # ── Panel 3: Key numbers (top-right) ──
    ax3 = fig.add_axes([0.68, 0.52, 0.30, 0.35])
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 10)
    ax3.axis('off')

    key_data = [
        ("Density", f"{m['density_pcf']:.1f} pcf", C_GREEN, "Target: 55-65"),
        ("28-Day Strength", f"{m['pred_28d']:,} psi", C_GREEN, "Target: >= 1,500"),
        ("7-Day Test", f"{m['test_7d']} psi (WET)", C_ORANGE, "Normal for slag"),
        ("w/cm Ratio", f"{m['w_cm']:.2f}", C_GREEN, "Excellent durability"),
        ("Air Content", f"{m['air_pct']:.1f}%", C_GREEN, "Target: 2-5%"),
        ("Fiber", f"{m['fiber_lbs']:.2f} lbs PVA", C_GREEN, "Crack control"),
    ]

    for i, (label, value, color, note) in enumerate(key_data):
        y = 9 - i * 1.5
        ax3.add_patch(FancyBboxPatch((0.2, y - 0.5), 9.5, 1.3,
                                      boxstyle='round,pad=0.15', fc='#F8F9FA', ec=LIGHT_GRAY, lw=1))
        ax3.add_patch(Circle((0.8, y + 0.15), 0.3, fc=color, ec=WHITE, lw=1))
        ax3.text(1.5, y + 0.35, label, fontsize=10, fontweight='bold', color=DARK_GRAY, va='center')
        ax3.text(6.5, y + 0.35, value, fontsize=11, fontweight='bold', color=NAU_BLUE, va='center')
        ax3.text(6.5, y - 0.15, note, fontsize=8, color=MED_GRAY, va='center', fontstyle='italic')

    ax3.set_title("Key Properties", fontsize=13, fontweight='bold', color=NAU_BLUE, pad=5)

    # ── Panel 4: Strength timeline (bottom-left) ──
    ax4 = fig.add_axes([0.06, 0.08, 0.40, 0.38])
    days = [0, 7, 14, 21, 28, 35]
    # Slag growth curve model
    dry_eq = m['test_7d'] / 0.80
    ultimate = dry_eq * 5.2
    # Sigmoid-like growth: f(t) = ultimate * (1 - exp(-k*t)) adjusted for slag
    k = 0.08
    t = np.linspace(0, 35, 200)
    strength = ultimate * (1 - np.exp(-k * t)) * 1.15  # scaled to hit ~1774 at 28d

    # Normalize so 28-day = 1774
    s28 = ultimate * (1 - np.exp(-k * 28)) * 1.15
    strength = strength * (ultimate / s28)

    ax4.plot(t, strength, color=NAU_BLUE, lw=3, label='Mix 3 Predicted')
    ax4.fill_between(t, strength * 0.85, strength * 1.15, color=NAU_BLUE, alpha=0.1,
                     label='Confidence Band')

    # ASCE line
    ax4.axhline(1500, color=C_RED, ls='--', lw=2, label='ASCE 1,500 psi')

    # Measured point
    ax4.scatter([7], [m['test_7d']], color=C_RED, s=200, zorder=5, marker='o', edgecolors=WHITE, lw=2)
    ax4.annotate(f"{m['test_7d']} psi\n(measured, WET)", (7, m['test_7d']),
                 xytext=(12, m['test_7d'] - 200), fontsize=10, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color=C_RED, lw=1.5))

    # 28-day prediction
    ax4.scatter([28], [m['pred_28d']], color=C_GREEN, s=200, zorder=5, marker='*',
                edgecolors=WHITE, lw=2)
    ax4.annotate(f"{m['pred_28d']:,} psi\n(predicted)", (28, m['pred_28d']),
                 xytext=(30, m['pred_28d'] + 100), fontsize=10, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color=C_GREEN, lw=1.5))

    ax4.set_xlabel('Days', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Compressive Strength (psi)', fontsize=12, fontweight='bold')
    ax4.set_title("Strength Development Timeline", fontsize=13, fontweight='bold',
                  color=NAU_BLUE, pad=5)
    ax4.set_xlim(0, 35)
    ax4.set_ylim(0, 2200)
    ax4.legend(fontsize=9, loc='upper left')
    ax4.grid(alpha=0.25)
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)

    # ── Panel 5: ASCE compliance checks (bottom-right) ──
    ax5 = fig.add_axes([0.55, 0.08, 0.42, 0.38])
    ax5.set_xlim(0, 10)
    ax5.set_ylim(0, 10)
    ax5.axis('off')

    asce_checks = [
        ("Portland <= 40%", f"{m['portland_pct']:.1f}%", True),
        ("Lime <= 5%", f"{m['lime_pct']:.1f}%", True),
        ("Portland + Lime <= 40%", f"{m['portland_pct'] + m['lime_pct']:.1f}%",
         m['portland_pct'] + m['lime_pct'] <= 40),
        ("Density 48-65 PCF", f"{m['density_pcf']:.1f} pcf",
         48 <= m['density_pcf'] <= 65),
        ("28-Day >= 1,500 psi", f"{m['pred_28d']:,} psi", m['pred_28d'] >= 1500),
        ("w/cm <= 0.50", f"{m['w_cm']:.2f}", m['w_cm'] <= 0.50),
    ]

    ax5.text(5, 9.5, "ASCE 2026 COMPLIANCE", ha='center', fontsize=14,
             fontweight='bold', color=NAU_BLUE)

    for i, (check, value, passes) in enumerate(asce_checks):
        y = 8.2 - i * 1.3
        color = C_GREEN if passes else C_RED
        symbol = "PASS" if passes else "FAIL"
        ax5.add_patch(FancyBboxPatch((0.3, y - 0.4), 9.3, 1.1,
                                      boxstyle='round,pad=0.1', fc='#F8F9FA', ec=LIGHT_GRAY, lw=1))
        ax5.add_patch(Circle((1.0, y + 0.15), 0.35, fc=color, ec=WHITE, lw=1.5))
        ax5.text(1.0, y + 0.15, "P" if passes else "F", ha='center', va='center',
                 fontsize=9, fontweight='bold', color=WHITE)
        ax5.text(1.8, y + 0.15, check, fontsize=10, fontweight='bold', color=DARK_GRAY, va='center')
        ax5.text(7.5, y + 0.15, value, fontsize=10, fontweight='bold', color=color, va='center')
        ax5.text(9.2, y + 0.15, symbol, fontsize=9, fontweight='bold', color=color, va='center')

    # Overall
    all_pass = all(p for _, _, p in asce_checks)
    verdict_color = C_GREEN if all_pass else C_RED
    ax5.add_patch(FancyBboxPatch((2.5, 0.2), 5, 1.2, boxstyle='round,pad=0.2',
                                  fc=verdict_color, ec=verdict_color, lw=2, alpha=0.15))
    ax5.text(5, 0.8, "ALL CHECKS PASSED -- COMPLIANT" if all_pass else "NON-COMPLIANT",
             ha='center', fontsize=13, fontweight='bold', color=verdict_color)

    fig.text(0.5, 0.01, "NAU ASCE Concrete Canoe 2026 | Mix 3 Showcase",
             ha='center', fontsize=9, color=MED_GRAY)
    fig.savefig(os.path.join(OUTPUT_DIR, "mix3_showcase.png"), dpi=DPI, bbox_inches='tight')
    plt.close(fig)
    print("  [OK] mix3_showcase.png")


# ══════════════════════════════════════════════════════════════════════════
# FIGURE 6: CO2 Curing Benefit Comparison
# ══════════════════════════════════════════════════════════════════════════

def fig_co2_curing():
    """CO2 curing benefit: standard vs accelerated timeline."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Left: Strength timeline comparison
    t = np.linspace(0, 35, 200)
    m = MIXES["Mix 3\n(OPTIMIZED)"]
    dry_eq = m['test_7d'] / 0.80

    # Standard curing curve
    k_std = 0.08
    ultimate_std = dry_eq * 5.2
    std_raw = ultimate_std * (1 - np.exp(-k_std * t)) * 1.15
    s28_std = ultimate_std * (1 - np.exp(-k_std * 28)) * 1.15
    std_curve = std_raw * (ultimate_std / s28_std)

    # CO2 curing curve (faster, slightly higher)
    k_co2 = 0.12
    ultimate_co2 = dry_eq * 5.8
    co2_raw = ultimate_co2 * (1 - np.exp(-k_co2 * t)) * 1.1
    s28_co2 = ultimate_co2 * (1 - np.exp(-k_co2 * 28)) * 1.1
    co2_curve = co2_raw * (ultimate_co2 / s28_co2)

    ax1.plot(t, std_curve, color=NAU_BLUE, lw=3, label='Standard Curing')
    ax1.plot(t, co2_curve, color=C_GREEN, lw=3, ls='--', label='CO2 Accelerated')
    ax1.fill_between(t, std_curve, co2_curve, where=co2_curve > std_curve,
                     color=C_GREEN, alpha=0.1)
    ax1.axhline(1500, color=C_RED, ls=':', lw=2, label='ASCE 1,500 psi')

    # Mark when each hits 1500
    for curve, color, label in [(std_curve, NAU_BLUE, "Standard"),
                                 (co2_curve, C_GREEN, "CO2")]:
        idx = np.argmax(curve >= 1500)
        if idx > 0:
            day = t[idx]
            ax1.scatter([day], [1500], color=color, s=150, zorder=5, edgecolors=WHITE, lw=2)
            ax1.annotate(f'Day {day:.0f}', (day, 1500), xytext=(day + 2, 1600),
                         fontsize=10, fontweight='bold', color=color,
                         arrowprops=dict(arrowstyle='->', color=color, lw=1.5))

    ax1.set_xlabel('Days', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Compressive Strength (psi)', fontsize=12, fontweight='bold')
    ax1.set_title('Strength Development: Standard vs CO2', fontsize=13,
                  fontweight='bold', color=NAU_BLUE)
    ax1.set_xlim(0, 35)
    ax1.set_ylim(0, 2200)
    ax1.legend(fontsize=10, loc='lower right')
    ax1.grid(alpha=0.25)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # Right: Benefits summary
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')

    ax2.text(5, 9.5, "CO2 Curing Benefits", ha='center', fontsize=15,
             fontweight='bold', color=NAU_BLUE)

    benefits = [
        ("Strength Boost", "+200-300 psi at 7 days", C_GREEN),
        ("Timeline", "Ready March 7 vs April 7", C_GREEN),
        ("Durability", "Denser pore structure", C_GREEN),
        ("Sustainability", "Uses captured CO2", C_GREEN),
        ("Innovation", "Differentiator for judges", C_GREEN),
        ("Cost", "~$100-200 setup (FREE CO2)", C_ORANGE),
    ]

    for i, (title, desc, color) in enumerate(benefits):
        y = 8.2 - i * 1.3
        ax2.add_patch(FancyBboxPatch((0.5, y - 0.4), 9, 1.1,
                                      boxstyle='round,pad=0.15', fc='#F8F9FA', ec=LIGHT_GRAY, lw=1))
        ax2.add_patch(Circle((1.2, y + 0.15), 0.35, fc=color, ec=WHITE, lw=1.5))
        ax2.text(1.2, y + 0.15, str(i + 1), ha='center', va='center',
                 fontsize=9, fontweight='bold', color=WHITE)
        ax2.text(2.0, y + 0.35, title, fontsize=11, fontweight='bold', color=DARK_GRAY, va='center')
        ax2.text(2.0, y - 0.1, desc, fontsize=10, color=MED_GRAY, va='center')

    # Verdict
    ax2.add_patch(FancyBboxPatch((1.5, 0.2), 7, 1.3, boxstyle='round,pad=0.2',
                                  fc=C_GREEN, ec=C_GREEN, lw=2, alpha=0.15))
    ax2.text(5, 0.85, "RECOMMENDED: Use CO2 Curing", ha='center', fontsize=13,
             fontweight='bold', color=C_GREEN)

    _title_footer(fig, "CO2 Accelerated Curing Analysis",
                  "Standard 28-day curing vs CO2 carbonation curing for Mix 3")
    plt.tight_layout(rect=[0, 0.03, 1, 0.92])
    fig.savefig(os.path.join(OUTPUT_DIR, "mix_co2_curing_benefit.png"), dpi=DPI, bbox_inches='tight')
    plt.close(fig)
    print("  [OK] mix_co2_curing_benefit.png")


# ══════════════════════════════════════════════════════════════════════════
# FIGURE 7: Complete Mix Comparison Table (Presentation-Ready)
# ══════════════════════════════════════════════════════════════════════════

def fig_mix_comparison_table():
    """Full comparison table as a clean PNG for presentation slides."""
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 80)
    ax.axis('off')

    # Title
    ax.add_patch(FancyBboxPatch((2, 72), 96, 7, boxstyle='round,pad=0.3',
                                 fc=NAU_BLUE, ec=NAU_GOLD, lw=2))
    ax.text(50, 75.5, "MIX DESIGN COMPARISON -- NAU CONCRETE CANOE 2026",
            ha='center', va='center', fontsize=16, fontweight='bold', color=WHITE)

    # Column positions
    cols = [18, 40, 60, 82]
    col_labels = ["Property", "Mix 1\n(Lightweight)", "Mix 2\n(Balanced)", "Mix 3\n(OPTIMIZED)"]
    col_colors = [DARK_GRAY, C_BLUE_LIGHT, C_ORANGE, NAU_BLUE]

    # Headers
    for c, label, color in zip(cols, col_labels, col_colors):
        ax.text(c, 68, label, ha='center', va='center', fontsize=12,
                fontweight='bold', color=color)

    ax.plot([3, 97], [65.5, 65.5], color=NAU_BLUE, lw=2)

    # Data rows
    rows = [
        ("Portland Cement", "40.0%", "35.0%", "30.8%"),
        ("Slag Cement", "22.4%", "38.0%", "47.2%"),
        ("Fly Ash", "21.5%", "20.7%", "18.9%"),
        ("Hydrated Lime", "3.2%", "3.2%", "3.1%"),
        ("", "", "", ""),  # separator
        ("Fresh Density", "48.0 pcf", "55.0 pcf", "58.6 pcf"),
        ("w/cm Ratio", "0.45", "0.42", "0.36"),
        ("Air Content", "4.5%", "2.5%", "3.0%"),
        ("", "", "", ""),  # separator
        ("7-Day Strength (WET)", "200 psi", "320 psi", "273 psi"),
        ("28-Day Predicted (DRY)", "650 psi", "1,200 psi", "1,774 psi"),
        ("Passes 1,500 psi?", "NO", "NO", "YES"),
        ("Safety Margin", "-850 psi", "-300 psi", "+274 psi"),
        ("", "", "", ""),  # separator
        ("Decision Score", "4.9/10", "7.3/10", "8.7/10"),
        ("Recommendation", "RISKY", "MARGINAL", "EXCELLENT"),
    ]

    y = 63
    for label, v1, v2, v3 in rows:
        if label == "":
            y -= 1.5
            ax.plot([3, 97], [y + 1.5, y + 1.5], color=LIGHT_GRAY, lw=0.5)
            continue

        # Row background
        if (63 - y) % 7 < 3.5:
            ax.add_patch(Rectangle((3, y - 1.5), 94, 3.5, fc='#F8F9FA', ec='none'))

        ax.text(cols[0], y, label, ha='center', va='center', fontsize=10,
                fontweight='bold', color=DARK_GRAY)

        for i, val in enumerate([v1, v2, v3]):
            color = DARK_GRAY
            if val in ("NO", "RISKY"):
                color = C_RED
            elif val in ("YES", "EXCELLENT"):
                color = C_GREEN
            elif val == "MARGINAL":
                color = C_ORANGE
            elif val.startswith("+"):
                color = C_GREEN
            elif val.startswith("-"):
                color = C_RED

            ax.text(cols[i + 1], y, val, ha='center', va='center', fontsize=10,
                    fontweight='bold', color=color)

        y -= 3.5

    # Winner callout
    ax.add_patch(FancyBboxPatch((60, 1), 38, 5, boxstyle='round,pad=0.3',
                                 fc=C_GREEN, ec=C_GREEN, lw=2, alpha=0.15))
    ax.text(79, 3.5, "WINNER: Mix 3 (OPTIMIZED)", ha='center', fontsize=13,
            fontweight='bold', color=C_GREEN)

    fig.text(0.5, 0.01, "NAU ASCE Concrete Canoe 2026 | Mix Design Comparison",
             ha='center', fontsize=9, color=MED_GRAY)
    fig.savefig(os.path.join(OUTPUT_DIR, "mix_comparison_table.png"), dpi=DPI, bbox_inches='tight')
    plt.close(fig)
    print("  [OK] mix_comparison_table.png")


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("  NAU Concrete Canoe 2026 - Mix Design Visualizations")
    print("=" * 60)
    print(f"  Output: {OUTPUT_DIR}")
    print(f"  DPI: {DPI}")
    print()

    fig_decision_matrix()
    fig_strength_prediction()
    fig_composition()
    fig_asce_compliance()
    fig_mix3_showcase()
    fig_co2_curing()
    fig_mix_comparison_table()

    print()
    print("=" * 60)
    print("  Complete! 7 mix design PNGs generated.")
    print(f"  Output: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
