#!/usr/bin/env python3
"""
NAU ASCE Concrete Canoe 2026 - Infographic Generator
11"x17" landscape PDF per ASCE 2026 RFP Section 5.5.4
Also generates a 36"x24" poster version for display board use.

Fixed: no overlapping text, photo placeholders, clean layout.
"""

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe
import numpy as np
from pathlib import Path

# --- NAU Brand Colors ---
NAU_NAVY   = '#003466'
NAU_GOLD   = '#FFB81C'
NAU_WHITE  = '#FFFFFF'
NAU_LIGHT  = '#E8EEF4'
NAU_DARK   = '#002244'
NAU_GRAY   = '#4A4A4A'
GREEN      = '#1B7D3A'

# --- Data (Design A) ---
CANOE_NAME = "PLUTO JACKS"
DESIGN     = "Design A"

# --- Helper functions ---
def draw_box(ax, x, y, w, h, color=NAU_NAVY, alpha=1.0, radius=0.008):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=color, edgecolor='none', alpha=alpha,
        transform=ax.transAxes, clip_on=False
    )
    ax.add_patch(box)

def draw_placeholder(ax, x, y, w, h, label, sublabel=""):
    """Dashed border box = placeholder for photo."""
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0,rounding_size=0.005",
        facecolor='#F5F5F5', edgecolor=NAU_NAVY,
        linewidth=1.5, linestyle='--', alpha=0.6,
        transform=ax.transAxes, clip_on=False
    )
    ax.add_patch(rect)
    ax.text(x + w/2, y + h*0.6, label,
            transform=ax.transAxes, fontsize=9, fontweight='bold',
            color=NAU_NAVY, va='center', ha='center', fontfamily='sans-serif',
            alpha=0.7)
    if sublabel:
        ax.text(x + w/2, y + h*0.3, sublabel,
                transform=ax.transAxes, fontsize=7, color=NAU_GRAY,
                va='center', ha='center', fontfamily='sans-serif', alpha=0.7)

def section_header(ax, x, y, text, line_w=0.20, fontsize=12):
    ax.text(x, y, text, transform=ax.transAxes,
            fontsize=fontsize, fontweight='bold', color=NAU_NAVY,
            va='top', ha='left', fontfamily='sans-serif')
    ax.plot([x, x + line_w], [y - 0.015, y - 0.015],
            transform=ax.transAxes, color=NAU_GOLD, linewidth=3,
            solid_capstyle='round', clip_on=False)

def kv_row(ax, x, y, label, value, fontsize=9, label_w=0.12, bold=False):
    ax.text(x, y, label, transform=ax.transAxes,
            fontsize=fontsize, color=NAU_GRAY, va='center', ha='left',
            fontfamily='sans-serif')
    ax.text(x + label_w, y, value, transform=ax.transAxes,
            fontsize=fontsize, color=NAU_NAVY, va='center', ha='left',
            fontweight='bold' if bold else 'normal', fontfamily='sans-serif')


def build_infographic(width_in, height_in, dpi, output_path, scale=1.0):
    """Build the infographic at any size. scale adjusts font sizes."""

    fs = lambda s: s * scale  # font scaler

    fig = plt.figure(figsize=(width_in, height_in), dpi=dpi, facecolor=NAU_WHITE)
    ax = fig.add_axes([0, 0, 1, 1], frameon=False)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks([]); ax.set_yticks([])

    # ================================================================
    # HEADER
    # ================================================================
    draw_box(ax, 0.0, 0.90, 1.0, 0.10, color=NAU_NAVY, radius=0.0)
    ax.text(0.5, 0.965, 'NAU ASCE CONCRETE CANOE 2026',
            transform=ax.transAxes, fontsize=fs(26), fontweight='bold',
            color=NAU_WHITE, va='center', ha='center', fontfamily='sans-serif',
            path_effects=[pe.withStroke(linewidth=1, foreground=NAU_DARK)])
    ax.text(0.5, 0.92, f'{CANOE_NAME}  \u2014  {DESIGN}  |  Northern Arizona University',
            transform=ax.transAxes, fontsize=fs(13), color=NAU_GOLD,
            va='center', ha='center', fontfamily='sans-serif')
    ax.plot([0, 1], [0.90, 0.90], color=NAU_GOLD, linewidth=3,
            transform=ax.transAxes, clip_on=False)

    # ================================================================
    # FOOTER
    # ================================================================
    draw_box(ax, 0.0, 0.0, 1.0, 0.03, color=NAU_NAVY, radius=0.0)
    ax.text(0.5, 0.015,
            'NAU ASCE Student Chapter  |  Flagstaff, Arizona  |  ASCE 2026 National Concrete Canoe Competition',
            transform=ax.transAxes, fontsize=fs(7.5), color=NAU_GOLD,
            va='center', ha='center', fontfamily='sans-serif')

    # ================================================================
    # LEFT COLUMN (x: 0.02 - 0.49)
    # ================================================================
    LX = 0.025

    # --- NAU CHAPTER PROFILE ---
    section_header(ax, LX, 0.875, 'NAU CHAPTER PROFILE', line_w=0.20, fontsize=fs(11))
    profile = (
        "Northern Arizona University ASCE Student Chapter, Flagstaff AZ.\n"
        "Active in regional and national competitions. Committed to\n"
        "sustainable infrastructure and hands-on engineering education."
    )
    ax.text(LX + 0.005, 0.835, profile,
            transform=ax.transAxes, fontsize=fs(8.5), color=NAU_GRAY,
            va='top', ha='left', fontfamily='sans-serif', linespacing=1.4)

    # --- PROTOTYPE SPECIFICATIONS ---
    section_header(ax, LX, 0.765, 'PROTOTYPE SPECIFICATIONS', line_w=0.22, fontsize=fs(11))
    draw_box(ax, LX - 0.003, 0.56, 0.465, 0.19, color=NAU_LIGHT, alpha=0.4, radius=0.005)

    ry = 0.725
    # Dimensions + Weight + Structural in 3 columns
    ax.text(LX + 0.005, ry, 'DIMENSIONS', transform=ax.transAxes,
            fontsize=fs(8.5), fontweight='bold', color=NAU_GOLD, va='center', fontfamily='sans-serif')
    ry -= 0.024
    for k, v in [('Length', '192" (16.0 ft)'), ('Beam', '32" (2.67 ft)'),
                 ('Depth', '17" (1.42 ft)'), ('Wall Thickness', '0.5"')]:
        kv_row(ax, LX + 0.01, ry, k, v, fontsize=fs(8.5), label_w=0.10)
        ry -= 0.021

    # Weight + Structural side by side — compact
    ry -= 0.005
    ax.text(LX + 0.005, ry, 'WEIGHT', transform=ax.transAxes,
            fontsize=fs(8.5), fontweight='bold', color=NAU_GOLD, va='center', fontfamily='sans-serif')
    ax.text(LX + 0.24, ry, 'STRUCTURAL', transform=ax.transAxes,
            fontsize=fs(8.5), fontweight='bold', color=NAU_GOLD, va='center', fontfamily='sans-serif')
    ry -= 0.023
    kv_row(ax, LX + 0.01, ry, 'Total', '174.3 lbs', fontsize=fs(8.5), label_w=0.08, bold=True)
    kv_row(ax, LX + 0.25, ry, 'Flexural', '1,500 psi', fontsize=fs(8.5), label_w=0.10)
    ry -= 0.020
    kv_row(ax, LX + 0.01, ry, 'Shell', '163.1 lbs', fontsize=fs(8), label_w=0.08)
    kv_row(ax, LX + 0.25, ry, 'Compressive', '2,000 psi', fontsize=fs(8.5), label_w=0.10)
    ry -= 0.020
    kv_row(ax, LX + 0.01, ry, 'PVA Mesh', '8.2 lbs', fontsize=fs(8), label_w=0.08)
    kv_row(ax, LX + 0.25, ry, 'Safety Factor', '2.30', fontsize=fs(8.5), label_w=0.10, bold=True)
    ry -= 0.020
    kv_row(ax, LX + 0.01, ry, 'Finish', '3.0 lbs', fontsize=fs(8), label_w=0.08)
    kv_row(ax, LX + 0.25, ry, 'Reinforcement', 'PVA 42% POA', fontsize=fs(8.5), label_w=0.10)

    # --- ASCE COMPLIANCE --- (moved down to avoid overlap)
    section_header(ax, LX, 0.49, 'ASCE COMPLIANCE', line_w=0.16, fontsize=fs(11))
    draw_box(ax, LX - 0.003, 0.295, 0.465, 0.18, color=NAU_LIGHT, alpha=0.4, radius=0.005)

    hy = 0.455
    for hdr, hx in [('Requirement', LX+0.01), ('Actual', LX+0.15),
                     ('Required', LX+0.26), ('Status', LX+0.38)]:
        ax.text(hx, hy, hdr, transform=ax.transAxes,
                fontsize=fs(8), fontweight='bold', color=NAU_NAVY,
                va='center', fontfamily='sans-serif')
    ax.plot([LX+0.005, LX+0.455], [hy-0.01, hy-0.01],
            color=NAU_NAVY, linewidth=0.5, transform=ax.transAxes, alpha=0.4)

    ry = hy - 0.026
    for req, actual, minimum, passed in [
        ('Freeboard',          '11.4"',    '\u2265 6.0"',  True),
        ('Metacentric Height', '8.68"',    '\u2265 6.0"',  True),
        ('Safety Factor',      '2.30',     '\u2265 2.0',   True),
        ('Canoe Weight',       '174.3 lb', '\u2264 237 lb', True),
        ('Cement Ratio',       '0.35',     '\u2264 0.40',  True),
        ('Reinforcement POA',  '42%',      '\u2265 40%',   True),
    ]:
        ax.text(LX+0.01,  ry, req,     transform=ax.transAxes, fontsize=fs(8), color=NAU_GRAY, va='center', fontfamily='sans-serif')
        ax.text(LX+0.15,  ry, actual,  transform=ax.transAxes, fontsize=fs(8), color=NAU_NAVY, fontweight='bold', va='center', fontfamily='sans-serif')
        ax.text(LX+0.26,  ry, minimum, transform=ax.transAxes, fontsize=fs(8), color=NAU_GRAY, va='center', fontfamily='sans-serif')
        ax.text(LX+0.38,  ry, '\u2713 PASS', transform=ax.transAxes, fontsize=fs(8.5), fontweight='bold', color=GREEN, va='center', fontfamily='sans-serif')
        ry -= 0.024

    # ================================================================
    # RIGHT COLUMN (x: 0.51 - 0.98)
    # ================================================================
    RX = 0.52

    # --- INNOVATIVE FEATURES ---
    section_header(ax, RX, 0.875, 'INNOVATIVE FEATURES', line_w=0.19, fontsize=fs(11))
    innovations = [
        'Lightweight concrete with Poraver expanded glass aggregate',
        'Computational hull optimization exploring 3 candidate designs',
        'AI-assisted structural analysis and verification',
        'CO\u2082-cured mix design for improved sustainability',
        'PVA fiber mesh reinforcement (42% POA)',
    ]
    iy = 0.84
    for line in innovations:
        ax.text(RX + 0.005, iy, f'\u2022  {line}',
                transform=ax.transAxes, fontsize=fs(8.5), color=NAU_GRAY,
                va='top', ha='left', fontfamily='sans-serif')
        iy -= 0.023

    # --- MIX DESIGN SPECIFICATIONS ---
    section_header(ax, RX, 0.72, 'MIX DESIGN SPECIFICATIONS', line_w=0.22, fontsize=fs(11))
    draw_box(ax, RX - 0.003, 0.575, 0.47, 0.13, color=NAU_LIGHT, alpha=0.4, radius=0.005)

    ry = 0.685
    for k, v in [('Wet Density', '~80 PCF'), ('Oven-Dried Density', '60 PCF'),
                 ('Slump', '4 - 6 in.'), ('Air Content', '8 - 12%'),
                 ('Compressive Strength', '2,000 psi'), ('Flexural Strength', '1,500 psi')]:
        kv_row(ax, RX + 0.01, ry, k, v, fontsize=fs(8.5), label_w=0.16)
        ry -= 0.022

    # ================================================================
    # BOTTOM ROW — Hull diagram + Pie chart + Photo placeholders
    # ================================================================

    # --- Hull Cross-Section (bottom-left) ---
    ax_hull = fig.add_axes([0.52, 0.30, 0.22, 0.24])
    ax_hull.set_aspect('equal')
    ax_hull.set_xlim(-22, 22)
    ax_hull.set_ylim(-20, 8)
    ax_hull.set_facecolor(NAU_WHITE)
    ax_hull.set_title('Hull Cross-Section', fontsize=fs(10), fontweight='bold',
                      color=NAU_NAVY, pad=6, fontfamily='sans-serif')

    x_o = np.linspace(-16, 16, 200)
    y_o = -17 * (1 - (x_o / 16) ** 2)
    sc_inner = 0.94
    x_i = x_o * sc_inner
    y_i = y_o * sc_inner + 0.8

    # Water fill
    wl = -5.6
    x_w = np.linspace(-16, 16, 200)
    y_w = -17 * (1 - (x_w / 16) ** 2)
    mask = y_w < wl
    if mask.any():
        ax_hull.fill_between(x_w[mask], y_w[mask], wl, color='#BBDEFB', alpha=0.4)

    # Shell
    ax_hull.fill(np.concatenate([x_o, x_i[::-1]]),
                 np.concatenate([y_o, y_i[::-1]]),
                 color=NAU_NAVY, alpha=0.3, edgecolor=NAU_NAVY, linewidth=1.5)

    ax_hull.axhline(y=wl, color='#2196F3', linewidth=1.5, linestyle='--', alpha=0.7)
    ax_hull.text(17.5, wl + 0.5, 'WL', fontsize=fs(7), color='#2196F3', va='bottom', fontfamily='sans-serif')

    ax_hull.annotate('', xy=(18, 0), xytext=(18, wl),
                     arrowprops=dict(arrowstyle='<->', color=NAU_GOLD, lw=1.5))
    ax_hull.text(19.5, wl/2, '11.4"', fontsize=fs(7), color=NAU_GOLD, va='center',
                 fontweight='bold', fontfamily='sans-serif')

    ax_hull.annotate('', xy=(-19, 0), xytext=(-19, -17),
                     arrowprops=dict(arrowstyle='<->', color=NAU_NAVY, lw=1.5))
    ax_hull.text(-21.5, -8.5, '17"', fontsize=fs(7), color=NAU_NAVY, va='center',
                 fontweight='bold', rotation=90, fontfamily='sans-serif')

    ax_hull.annotate('', xy=(-16, 4), xytext=(16, 4),
                     arrowprops=dict(arrowstyle='<->', color=NAU_NAVY, lw=1.5))
    ax_hull.text(0, 6, '32" Beam', fontsize=fs(7.5), color=NAU_NAVY, va='center', ha='center',
                 fontweight='bold', fontfamily='sans-serif')

    ax_hull.annotate('0.5" wall', xy=(12, -7), xytext=(17, -13),
                     fontsize=fs(6.5), color=NAU_GRAY, va='center', fontfamily='sans-serif',
                     arrowprops=dict(arrowstyle='->', color=NAU_GRAY, lw=0.8))

    for spine in ax_hull.spines.values():
        spine.set_visible(False)
    ax_hull.set_xticks([]); ax_hull.set_yticks([])

    # --- Weight Pie Chart (bottom-center-right) ---
    ax_pie = fig.add_axes([0.75, 0.30, 0.23, 0.24])

    labels = ['Concrete Shell', 'Reinforcement (PVA)', 'Finish / Sealant']
    sizes  = [163.1, 8.2, 3.0]
    pcts   = [f'{s/174.3*100:.1f}%' for s in sizes]
    colors_pie = [NAU_NAVY, NAU_GOLD, '#8AADCF']

    wedges, texts, autotexts = ax_pie.pie(
        sizes, labels=None, autopct='',
        colors=colors_pie, explode=(0.03, 0.06, 0.06),
        startangle=140,
        textprops={'fontsize': fs(7.5), 'fontfamily': 'sans-serif'}
    )

    ax_pie.set_title('Weight Breakdown', fontsize=fs(10), fontweight='bold',
                     color=NAU_NAVY, pad=6, fontfamily='sans-serif')

    # Legend with percentages built in
    legend_labels = [f'{l} — {p} ({w} lbs)' for l, p, w in zip(labels, pcts, sizes)]
    ax_pie.legend(
        wedges, legend_labels,
        loc='lower center', bbox_to_anchor=(0.5, -0.18),
        fontsize=fs(6.5), frameon=False, ncol=1,
        prop={'family': 'DejaVu Sans'}
    )

    ax_pie.text(0, 0, f'174.3\nlbs', ha='center', va='center',
                fontsize=fs(10), fontweight='bold', color=NAU_NAVY, fontfamily='sans-serif')

    # ================================================================
    # PHOTO PLACEHOLDERS (bottom section)
    # ================================================================
    ph_y = 0.045
    ph_h = 0.24
    ph_w = 0.115
    ph_gap = 0.008

    placeholders = [
        ('CYLINDER\nTEST',        'Insert split cylinder photo'),
        ('CONSTRUCTION\nPHOTO',   'Insert layup / mold photo'),
        ('CANOE ON\nWATER',       'Insert float test photo'),
        ('TEAM\nPHOTO',           'Insert team photo'),
    ]

    for i, (label, sub) in enumerate(placeholders):
        px = LX + i * (ph_w + ph_gap)
        draw_placeholder(ax, px, ph_y, ph_w, ph_h, label, sub)

    # ================================================================
    # SAVE
    # ================================================================
    fig.savefig(str(output_path), format='pdf', dpi=dpi,
                bbox_inches='tight', pad_inches=0.1,
                facecolor=NAU_WHITE, edgecolor='none')
    plt.close(fig)
    print(f'  Saved: {output_path} ({output_path.stat().st_size / 1024:.1f} KB)')


# ============================================================
# Generate BOTH sizes
# ============================================================
OUT_DIR = Path('/root/concrete-canoe-project2026/reports')

print('Generating infographic (11"x17" — ASCE submission)...')
build_infographic(17, 11, 150,
    OUT_DIR / 'infographic_design_A.pdf', scale=1.0)

print('Generating poster version (36"x24" — display board)...')
build_infographic(36, 24, 150,
    OUT_DIR / 'infographic_design_A_poster.pdf', scale=1.8)

print('\nDone! Both versions generated.')
