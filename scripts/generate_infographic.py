#!/usr/bin/env python3
"""
NAU ASCE Concrete Canoe 2026 - Infographic Generator
Generates an 11"x17" landscape PDF infographic for Design A (PLUTO JACKS)
Compliant with ASCE 2026 RFP Section 5.5.4
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

# --- Data (Design A) ---
CANOE_NAME = "PLUTO JACKS"
DESIGN     = "Design A"

DIMENSIONS = {
    'Length':         '192" (16.0 ft)',
    'Beam':           '32" (2.67 ft)',
    'Depth':          '17" (1.42 ft)',
    'Wall Thickness': '0.5"',
}

WEIGHTS = {
    'Concrete Shell':      163.1,
    'Reinforcement (PVA)':   8.2,
    'Finish / Sealant':      3.0,
}
TOTAL_WEIGHT = 174.3

STRUCTURAL = {
    'Flexural Strength':    '1,500 psi',
    'Compressive Strength': '2,000 psi',
    'Max Bending Moment':   '3,148.5 lb-ft',
    'Safety Factor':        '2.30 (req \u2265 2.0)',
}

REINFORCEMENT = {
    'Type':   'PVA Fiber Mesh',
    'POA':    '42% (req \u2265 40%)',
    'Layers': 'Multi-layer layup',
}

MIX_DESIGN = {
    'Wet Density':          '~80 PCF',
    'Oven-Dried Density':   '60 PCF',
    'Slump':                '4 - 6 in.',
    'Air Content':          '8 - 12%',
    'Compressive Strength': '2,000 psi',
    'Flexural Strength':    '1,500 psi',
}

COMPLIANCE = [
    ('Freeboard',          '11.4"',   '\u2265 6.0"',  True),
    ('Metacentric Height', '8.68"',   '\u2265 6.0"',  True),
    ('Safety Factor',      '2.30',    '\u2265 2.0',   True),
    ('Canoe Weight',       '174.3 lb','\u2264 237 lb', True),
    ('Cement Ratio',       '0.35',    '\u2264 0.40',  True),
    ('Reinforcement POA',  '42%',     '\u2265 40%',   True),
]

# --- Helper ---
def draw_rounded_box(ax, x, y, w, h, color=NAU_NAVY, alpha=1.0, radius=0.02):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=color, edgecolor='none', alpha=alpha,
        transform=ax.transAxes, clip_on=False
    )
    ax.add_patch(box)

def section_header(ax, x, y, text, fontsize=13):
    ax.text(x, y, text, transform=ax.transAxes,
            fontsize=fontsize, fontweight='bold', color=NAU_NAVY,
            va='top', ha='left', fontfamily='sans-serif')
    ax.plot([x, x + 0.23], [y - 0.018, y - 0.018],
            transform=ax.transAxes, color=NAU_GOLD, linewidth=3,
            solid_capstyle='round', clip_on=False)

def table_row(ax, x, y, label, value, fontsize=9.5, label_w=0.13, bold_value=False):
    ax.text(x, y, label, transform=ax.transAxes,
            fontsize=fontsize, color=NAU_GRAY, va='center', ha='left',
            fontfamily='sans-serif')
    ax.text(x + label_w, y, value, transform=ax.transAxes,
            fontsize=fontsize, color=NAU_NAVY, va='center', ha='left',
            fontweight='bold' if bold_value else 'normal',
            fontfamily='sans-serif')


# ========== CREATE FIGURE ==========
fig = plt.figure(figsize=(17, 11), dpi=150, facecolor=NAU_WHITE)

ax = fig.add_axes([0, 0, 1, 1], frameon=False)
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.set_xticks([]); ax.set_yticks([])

# ===== HEADER =====
draw_rounded_box(ax, 0.0, 0.88, 1.0, 0.12, color=NAU_NAVY, radius=0.0)
ax.text(0.5, 0.955, 'NAU ASCE CONCRETE CANOE 2026',
        transform=ax.transAxes, fontsize=28, fontweight='bold',
        color=NAU_WHITE, va='center', ha='center', fontfamily='sans-serif',
        path_effects=[pe.withStroke(linewidth=1, foreground=NAU_DARK)])
ax.text(0.5, 0.905, f'{CANOE_NAME}  \u2014  {DESIGN}  |  Northern Arizona University',
        transform=ax.transAxes, fontsize=14, color=NAU_GOLD,
        va='center', ha='center', fontfamily='sans-serif')
ax.plot([0, 1], [0.88, 0.88], color=NAU_GOLD, linewidth=4,
        transform=ax.transAxes, clip_on=False)

# ===== FOOTER =====
draw_rounded_box(ax, 0.0, 0.0, 1.0, 0.035, color=NAU_NAVY, radius=0.0)
ax.text(0.5, 0.017,
        'NAU ASCE Student Chapter  |  Flagstaff, Arizona  |  ASCE 2026 National Concrete Canoe Competition',
        transform=ax.transAxes, fontsize=8, color=NAU_GOLD,
        va='center', ha='center', fontfamily='sans-serif')

# ===== SECTION 1: CHAPTER PROFILE (top-left) =====
s1x, s1y = 0.03, 0.85
section_header(ax, s1x, s1y, 'NAU CHAPTER PROFILE', fontsize=13)

profile_lines = [
    "Northern Arizona University ASCE Student Chapter,",
    "Flagstaff AZ. Active in regional and national",
    "competitions. Committed to sustainable infrastructure",
    "and hands-on engineering education.",
]
for i, line in enumerate(profile_lines):
    ax.text(s1x + 0.005, s1y - 0.04 - i * 0.022, line,
            transform=ax.transAxes, fontsize=9, color=NAU_GRAY,
            va='top', ha='left', fontfamily='sans-serif')

# ===== SECTION 2: INNOVATIVE FEATURES (top-right) =====
s2x = 0.52
section_header(ax, s2x, s1y, 'INNOVATIVE FEATURES', fontsize=13)

innovations = [
    '\u2022  Lightweight concrete with Poraver expanded glass aggregate',
    '\u2022  Computational hull optimization exploring 3 candidate designs',
    '\u2022  AI-assisted structural analysis and verification',
    '\u2022  CO\u2082-cured mix design for improved sustainability',
    '\u2022  PVA fiber mesh reinforcement (42% POA)',
]
for i, line in enumerate(innovations):
    ax.text(s2x + 0.005, s1y - 0.04 - i * 0.025, line,
            transform=ax.transAxes, fontsize=9, color=NAU_GRAY,
            va='top', ha='left', fontfamily='sans-serif')

# ===== SECTION 3: PROTOTYPE SPECIFICATIONS (middle-left) =====
s3y = 0.685
section_header(ax, s1x, s3y, 'PROTOTYPE SPECIFICATIONS', fontsize=13)

draw_rounded_box(ax, s1x - 0.005, s3y - 0.30, 0.46, 0.28,
                 color=NAU_LIGHT, alpha=0.5, radius=0.01)

ry = s3y - 0.05
ax.text(s1x + 0.005, ry, 'DIMENSIONS', transform=ax.transAxes,
        fontsize=9, fontweight='bold', color=NAU_GOLD, va='center', fontfamily='sans-serif')
ry -= 0.028
for k, v in DIMENSIONS.items():
    table_row(ax, s1x + 0.01, ry, k, v, label_w=0.10)
    ry -= 0.024

ry -= 0.008
ax.text(s1x + 0.005, ry, 'WEIGHT', transform=ax.transAxes,
        fontsize=9, fontweight='bold', color=NAU_GOLD, va='center', fontfamily='sans-serif')
ry -= 0.028
table_row(ax, s1x + 0.01, ry, 'Total Weight', f'{TOTAL_WEIGHT} lbs', label_w=0.10, bold_value=True)
ry -= 0.024
for comp, wt in WEIGHTS.items():
    table_row(ax, s1x + 0.015, ry, comp, f'{wt} lbs', fontsize=8.5, label_w=0.12)
    ry -= 0.021

ry -= 0.008
ax.text(s1x + 0.005, ry, 'STRUCTURAL', transform=ax.transAxes,
        fontsize=9, fontweight='bold', color=NAU_GOLD, va='center', fontfamily='sans-serif')
ry -= 0.028
for k, v in STRUCTURAL.items():
    table_row(ax, s1x + 0.01, ry, k, v, label_w=0.13)
    ry -= 0.024

ry -= 0.008
ax.text(s1x + 0.005, ry, 'REINFORCEMENT', transform=ax.transAxes,
        fontsize=9, fontweight='bold', color=NAU_GOLD, va='center', fontfamily='sans-serif')
ry -= 0.028
for k, v in REINFORCEMENT.items():
    table_row(ax, s1x + 0.01, ry, k, v, label_w=0.10)
    ry -= 0.024

# ===== SECTION 4: MIX DESIGN (middle-right top) =====
s4x = 0.52
s4y = 0.685
section_header(ax, s4x, s4y, 'MIX DESIGN SPECIFICATIONS', fontsize=13)

draw_rounded_box(ax, s4x - 0.005, s4y - 0.19, 0.47, 0.17,
                 color=NAU_LIGHT, alpha=0.5, radius=0.01)

ry = s4y - 0.045
for k, v in MIX_DESIGN.items():
    table_row(ax, s4x + 0.01, ry, k, v, label_w=0.15)
    ry -= 0.025

# ===== ASCE COMPLIANCE CHECKLIST (middle-right lower) =====
cy = 0.475
section_header(ax, s4x, cy, 'ASCE COMPLIANCE', fontsize=13)

draw_rounded_box(ax, s4x - 0.005, cy - 0.22, 0.47, 0.20,
                 color=NAU_LIGHT, alpha=0.5, radius=0.01)

hy = cy - 0.04
ax.text(s4x + 0.01,  hy, 'Requirement',  transform=ax.transAxes,
        fontsize=8.5, fontweight='bold', color=NAU_NAVY, va='center', fontfamily='sans-serif')
ax.text(s4x + 0.14,  hy, 'Actual',       transform=ax.transAxes,
        fontsize=8.5, fontweight='bold', color=NAU_NAVY, va='center', fontfamily='sans-serif')
ax.text(s4x + 0.24,  hy, 'Required',     transform=ax.transAxes,
        fontsize=8.5, fontweight='bold', color=NAU_NAVY, va='center', fontfamily='sans-serif')
ax.text(s4x + 0.37,  hy, 'Status',       transform=ax.transAxes,
        fontsize=8.5, fontweight='bold', color=NAU_NAVY, va='center', fontfamily='sans-serif')

ax.plot([s4x + 0.005, s4x + 0.455], [hy - 0.012, hy - 0.012],
        color=NAU_NAVY, linewidth=0.5, transform=ax.transAxes, alpha=0.4)

ry = hy - 0.032
for req, actual, minimum, passed in COMPLIANCE:
    ax.text(s4x + 0.01, ry, req, transform=ax.transAxes,
            fontsize=8.5, color=NAU_GRAY, va='center', fontfamily='sans-serif')
    ax.text(s4x + 0.14, ry, actual, transform=ax.transAxes,
            fontsize=8.5, color=NAU_NAVY, fontweight='bold', va='center', fontfamily='sans-serif')
    ax.text(s4x + 0.24, ry, minimum, transform=ax.transAxes,
            fontsize=8.5, color=NAU_GRAY, va='center', fontfamily='sans-serif')
    sc = '#1B7D3A' if passed else '#CC0000'
    st = '\u2713 PASS' if passed else '\u2717 FAIL'
    ax.text(s4x + 0.37, ry, st, transform=ax.transAxes,
            fontsize=9, fontweight='bold', color=sc, va='center', fontfamily='sans-serif')
    ry -= 0.027

# ===== HULL CROSS-SECTION (bottom-left) =====
ax_hull = fig.add_axes([0.03, 0.05, 0.28, 0.28])
ax_hull.set_aspect('equal')
ax_hull.set_xlim(-22, 22)
ax_hull.set_ylim(-20, 8)
ax_hull.set_facecolor(NAU_WHITE)
ax_hull.set_title('Hull Cross-Section (Midship)', fontsize=11, fontweight='bold',
                  color=NAU_NAVY, pad=8, fontfamily='sans-serif')

# Outer hull (parabolic)
x_o = np.linspace(-16, 16, 200)
y_o = -17 * (1 - (x_o / 16) ** 2)

# Inner hull
sc = 0.94
x_i = x_o * sc
y_i = y_o * sc + 0.8

# Water fill below waterline
wl = -5.6
x_water = np.linspace(-16, 16, 200)
y_water_hull = -17 * (1 - (x_water / 16) ** 2)
mask = y_water_hull < wl
if mask.any():
    ax_hull.fill_between(x_water[mask], y_water_hull[mask], wl,
                         color='#BBDEFB', alpha=0.4)

# Shell fill
ax_hull.fill(
    np.concatenate([x_o, x_i[::-1]]),
    np.concatenate([y_o, y_i[::-1]]),
    color=NAU_NAVY, alpha=0.3, edgecolor=NAU_NAVY, linewidth=1.5
)

# Waterline
ax_hull.axhline(y=wl, color='#2196F3', linewidth=1.5, linestyle='--', alpha=0.7)
ax_hull.text(17.5, wl + 0.5, 'WL', fontsize=8, color='#2196F3', va='bottom', fontfamily='sans-serif')

# Freeboard arrow
ax_hull.annotate('', xy=(18, 0), xytext=(18, wl),
                 arrowprops=dict(arrowstyle='<->', color=NAU_GOLD, lw=1.5))
ax_hull.text(19.5, wl / 2, '11.4"', fontsize=7.5, color=NAU_GOLD, va='center',
             fontweight='bold', fontfamily='sans-serif')

# Depth arrow
ax_hull.annotate('', xy=(-19, 0), xytext=(-19, -17),
                 arrowprops=dict(arrowstyle='<->', color=NAU_NAVY, lw=1.5))
ax_hull.text(-21.5, -8.5, '17"', fontsize=7.5, color=NAU_NAVY, va='center',
             fontweight='bold', rotation=90, fontfamily='sans-serif')

# Beam arrow
ax_hull.annotate('', xy=(-16, 4), xytext=(16, 4),
                 arrowprops=dict(arrowstyle='<->', color=NAU_NAVY, lw=1.5))
ax_hull.text(0, 6, '32" Beam', fontsize=8, color=NAU_NAVY, va='center', ha='center',
             fontweight='bold', fontfamily='sans-serif')

# Wall label
ax_hull.annotate('0.5" wall', xy=(12, -7), xytext=(17, -13),
                 fontsize=7, color=NAU_GRAY, va='center', fontfamily='sans-serif',
                 arrowprops=dict(arrowstyle='->', color=NAU_GRAY, lw=0.8))

for spine in ax_hull.spines.values():
    spine.set_visible(False)
ax_hull.set_xticks([]); ax_hull.set_yticks([])

# ===== WEIGHT PIE CHART (bottom-center) =====
ax_pie = fig.add_axes([0.34, 0.06, 0.22, 0.26])

labels = list(WEIGHTS.keys())
sizes  = list(WEIGHTS.values())
colors_pie = [NAU_NAVY, NAU_GOLD, '#8AADCF']
explode = (0.03, 0.03, 0.03)

wedges, texts, autotexts = ax_pie.pie(
    sizes, labels=None, autopct='%1.1f%%',
    colors=colors_pie, explode=explode,
    startangle=140, pctdistance=0.75,
    textprops={'fontsize': 8, 'fontfamily': 'sans-serif'}
)
for t in autotexts:
    t.set_color(NAU_WHITE)
    t.set_fontweight('bold')

ax_pie.set_title('Weight Breakdown', fontsize=11, fontweight='bold',
                 color=NAU_NAVY, pad=8, fontfamily='sans-serif')

ax_pie.legend(
    wedges, [f'{l} ({w} lbs)' for l, w in zip(labels, sizes)],
    loc='lower center', bbox_to_anchor=(0.5, -0.15),
    fontsize=7.5, frameon=False, ncol=1,
    prop={'family': 'DejaVu Sans'}
)

ax_pie.text(0, 0, f'{TOTAL_WEIGHT}\nlbs', ha='center', va='center',
            fontsize=11, fontweight='bold', color=NAU_NAVY, fontfamily='sans-serif')

# ===== KEY METRICS BOXES (bottom-right) =====
metrics = [
    ('174.3', 'lbs',  'Total Weight'),
    ('2.30',  'SF',   'Safety Factor'),
    ('11.4"', '',     'Freeboard'),
    ('8.68"', '',     'GM Height'),
]

bx_start = 0.60
by = 0.12
bw = 0.085
bh = 0.16
bg = 0.005

for i, (val, unit, label) in enumerate(metrics):
    bx = bx_start + i * (bw + bg)
    draw_rounded_box(ax, bx, by, bw, bh, color=NAU_NAVY, radius=0.008)
    display = f'{val}{unit}' if unit and unit != 'SF' else val
    ax.text(bx + bw/2, by + bh*0.62, display,
            transform=ax.transAxes, fontsize=16, fontweight='bold',
            color=NAU_GOLD, va='center', ha='center', fontfamily='sans-serif')
    if unit == 'SF':
        ax.text(bx + bw/2, by + bh*0.42, unit,
                transform=ax.transAxes, fontsize=9,
                color=NAU_WHITE, va='center', ha='center', fontfamily='sans-serif')
    ax.text(bx + bw/2, by + bh*0.2, label,
            transform=ax.transAxes, fontsize=8, color=NAU_WHITE,
            va='center', ha='center', fontfamily='sans-serif')
    ax.text(bx + bw/2, by + bh*0.88, '\u2713',
            transform=ax.transAxes, fontsize=14, color='#4CAF50',
            va='center', ha='center', fontweight='bold')

# ===== SAVE =====
out = Path('/root/concrete-canoe-project2026/reports/infographic_design_A.pdf')
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(str(out), format='pdf', dpi=150,
            bbox_inches='tight', pad_inches=0.1,
            facecolor=NAU_WHITE, edgecolor='none')
plt.close(fig)

print(f'Infographic saved to: {out}')
print(f'File size: {out.stat().st_size / 1024:.1f} KB')
print('Done.')
