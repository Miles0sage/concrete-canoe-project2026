#!/usr/bin/env python3
"""
generate_cad_construction_drawings.py - NAU ASCE Concrete Canoe 2026
=====================================================================
Generates 3 professional CAD-style construction drawing sheets for Design C,
matching the style of the 2024 team's engineering drawings.

Design C: 216" x 36" x 18", t=0.75", ~318 lbs

Sheet 1: SECTION BREAKDOWN  (plan, profile, 3 cross-sections)
Sheet 2: TOP AND ISOMETRIC VIEW  (dimensioned plan + 3D wireframe)
Sheet 3: CONSTRUCTION DETAILS  (mold, reinforcement, layer buildup, keel)

Output:
  reports/figures/cad_sheet1_section_breakdown.png
  reports/figures/cad_sheet2_top_isometric.png
  reports/figures/cad_sheet3_construction_details.png
  (copies to docs/figures/)

Usage:
    /usr/local/bin/python3 generate_cad_construction_drawings.py
"""

import os
import sys
import shutil
import numpy as np
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon, FancyArrowPatch, Circle
from matplotlib.lines import Line2D
from matplotlib.path import Path as MplPath
import matplotlib.patheffects as pe

# =============================================================================
# DESIGN C PARAMETERS
# =============================================================================
LOA = 216.0           # Length overall (inches)
BEAM = 36.0           # Max beam at midship (inches)
DEPTH = 18.0          # Max depth at midship (inches)
THICKNESS = 0.75      # Wall thickness (inches)
HULL_WEIGHT = 318.0   # Estimated hull weight (lbs)
KEEL_THICKNESS = 1.0  # Reinforced keel thickness (inches)
V_BOTTOM_ANGLE = 15.0 # Deadrise angle (degrees)
FLARE_ANGLE = 10.0    # Flare angle (degrees)
ROCKER = 2.0          # Rocker rise at bow/stern (inches)

CANOE_NAME = "PLUTO JACKS"
TEAM_NAME = "NAU ASCE 2026"
DESIGN_LABEL = "Design C"

# Station data: (position_fraction, width, depth)
STATIONS = [
    (0.00, 8.0,  16.0),   # Bow
    (0.25, 26.0, 17.0),   # Station 1
    (0.50, 36.0, 18.0),   # Midship
    (0.75, 26.0, 17.0),   # Station 3
    (1.00, 8.0,  16.0),   # Stern
]

# Section cuts for Sheet 1
SECTION_CUTS = [
    ("A", "A", 0.25, 26.0, 17.0, "BOW (25%)"),
    ("B", "B", 0.50, 36.0, 18.0, "MIDSHIP (50%)"),
    ("C", "C", 0.75, 26.0, 17.0, "STERN (75%)"),
]

# =============================================================================
# OUTPUT PATHS
# =============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
REPORTS_FIG_DIR = os.path.join(PROJECT_ROOT, "reports", "figures")
DOCS_FIG_DIR = os.path.join(PROJECT_ROOT, "docs", "figures")

os.makedirs(REPORTS_FIG_DIR, exist_ok=True)
os.makedirs(DOCS_FIG_DIR, exist_ok=True)

DPI = 300
SHEET_W = 22   # inches landscape
SHEET_H = 17   # inches landscape

# =============================================================================
# COLOR PALETTE
# =============================================================================
C_BG = "#F0F0F0"            # Light gray background
C_WHITE = "#FFFFFF"
C_BLACK = "#000000"
C_DARK_GRAY = "#2C2C2C"
C_MED_GRAY = "#666666"
C_LIGHT_GRAY = "#CCCCCC"
C_VERY_LIGHT = "#E8E8E8"
C_BORDER = "#000000"
C_TITLE_BG = "#1A1A2E"      # Dark navy for title block
C_TITLE_TEXT = "#FFFFFF"
C_DIM_LINE = "#000000"
C_DIM_TEXT = "#000000"
C_SECTION_RED = "#CC0000"
C_SECTION_BLUE = "#0055AA"
C_SECTION_GREEN = "#006600"
C_HULL_FILL = "#D0D0D0"
C_HULL_EDGE = "#000000"
C_CONCRETE = "#A8A8A0"
C_FIBERGLASS = "#6BAF6B"
C_FOAM_BEIGE = "#F2E8D5"
C_RELEASE_AGENT = "#FFE0B0"
C_HATCH = "#888888"
C_WATER = "#B8D4E8"
C_KEEL_FILL = "#909090"


# =============================================================================
# HULL GEOMETRY FUNCTIONS
# =============================================================================
def hull_halfwidth(x_frac):
    """Half-width of hull at fractional position along length.
    Uses interpolation between station data for smooth shape."""
    fracs = np.array([s[0] for s in STATIONS])
    widths = np.array([s[1] / 2.0 for s in STATIONS])
    return np.interp(x_frac, fracs, widths)


def hull_depth_at(x_frac):
    """Depth of hull at fractional position along length."""
    fracs = np.array([s[0] for s in STATIONS])
    depths = np.array([s[2] for s in STATIONS])
    return np.interp(x_frac, fracs, depths)


def hull_keel_y(x_frac):
    """Keel line elevation (includes rocker at bow/stern).
    Returns offset from baseline (positive = higher)."""
    # Parabolic rocker: max rise at ends, zero at midship
    return ROCKER * (2 * x_frac - 1) ** 2


def get_cross_section_uv(width, depth, thickness, n_pts=40):
    """Generate U-shaped cross-section vertices (outer and inner).
    Returns outer_xy, inner_xy as arrays.
    The U-shape: flat bottom with angled V and flared sides."""
    hw = width / 2.0
    t = thickness
    dead_rad = np.radians(V_BOTTOM_ANGLE)
    flare_rad = np.radians(FLARE_ANGLE)

    # Bottom V-section: from center going outward
    # V-bottom half-width at the keel point
    v_depth = hw * np.tan(dead_rad) * 0.3  # V portion depth
    if v_depth > depth * 0.4:
        v_depth = depth * 0.4
    v_hw = v_depth / np.tan(dead_rad) if dead_rad > 0.01 else hw * 0.3

    # Build outer profile: start from port gunwale, go down to keel, back up to starboard
    # Use smooth curve through control points
    # Left gunwale -> left chine -> keel -> right chine -> right gunwale
    chine_y = v_depth
    chine_x = v_hw

    # Flare: gunwale is wider than chine
    flare_offset = (depth - chine_y) * np.tan(flare_rad)
    gunwale_x = chine_x + (depth - chine_y) / np.tan(np.radians(80)) + flare_offset

    # Ensure gunwale_x doesn't exceed half-width
    gunwale_x = min(gunwale_x, hw)
    chine_x = min(chine_x, hw * 0.6)

    # Build smooth outer profile with bezier-like interpolation
    # Port side (negative x) from gunwale down to keel
    n_side = n_pts // 2
    n_bottom = n_pts // 4

    # Port gunwale to port chine (side wall)
    t_side = np.linspace(0, 1, n_side)
    side_x_port = -gunwale_x + (gunwale_x - chine_x) * t_side
    side_y_port = depth - (depth - chine_y) * t_side

    # Port chine to keel (bottom V)
    t_bot = np.linspace(0, 1, n_bottom)[1:]  # skip first to avoid duplicate
    bot_x_port = -chine_x * (1 - t_bot)
    bot_y_port = chine_y * (1 - t_bot)

    # Mirror for starboard
    bot_x_star = bot_y_port / chine_y * chine_x if chine_y > 0 else t_bot * chine_x
    bot_y_star = t_bot * chine_y

    side_x_star = chine_x + (gunwale_x - chine_x) * t_side
    side_y_star = chine_y + (depth - chine_y) * t_side

    # Combine
    outer_x = np.concatenate([side_x_port, bot_x_port, bot_x_star, side_x_star])
    outer_y = np.concatenate([side_y_port, bot_y_port, bot_y_star, side_y_star])

    # Inner profile: offset inward by thickness
    # Simplified: just reduce dimensions by thickness
    inner_hw = hw - t
    inner_depth = depth - t
    scale_x = inner_hw / hw if hw > 0 else 1
    scale_y = inner_depth / depth if depth > 0 else 1

    inner_x = outer_x * scale_x
    inner_y = outer_y * scale_y + t * 0.5

    return np.column_stack([outer_x, outer_y]), np.column_stack([inner_x, inner_y])


def get_simple_u_section(width, depth, thickness):
    """Simple U-shaped cross-section for clean CAD display.
    Returns list of (x, y) outer and inner vertices."""
    hw = width / 2.0
    t = thickness
    dead_rad = np.radians(V_BOTTOM_ANGLE)

    # V-bottom parameters
    v_depth = min(hw * 0.25, depth * 0.2)
    v_hw = v_depth / np.tan(dead_rad) if dead_rad > 0.01 else hw * 0.3

    # Smooth the V-bottom with a curve
    n_bottom = 30
    n_side = 20

    # Build outer contour: from left gunwale, down left side, across bottom V, up right side
    # Left side: straight from (−hw, depth) to (−v_hw, v_depth)
    t_ls = np.linspace(0, 1, n_side)
    left_x = -hw + (hw - v_hw) * t_ls
    left_y = depth - (depth - v_depth) * t_ls

    # Bottom V: from (−v_hw, v_depth) through (0, 0) to (v_hw, v_depth)
    t_bot = np.linspace(-1, 1, n_bottom)
    # Smooth catenary-like bottom
    bot_x = t_bot * v_hw
    bot_y = v_depth * np.abs(t_bot)
    # Add slight rounding at keel
    bot_y = np.where(np.abs(t_bot) < 0.3,
                     v_depth * (t_bot / 0.3) ** 2,
                     bot_y)

    # Right side: from (v_hw, v_depth) to (hw, depth)
    right_x = v_hw + (hw - v_hw) * t_ls
    right_y = v_depth + (depth - v_depth) * t_ls

    outer_x = np.concatenate([left_x, bot_x[1:-1], right_x])
    outer_y = np.concatenate([left_y, bot_y[1:-1], right_y])

    # Inner contour: offset by thickness
    scale_x = (hw - t) / hw if hw > t else 0.5
    scale_y = (depth - t) / depth if depth > t else 0.5
    inner_x = outer_x * scale_x
    inner_y = outer_y * scale_y + t

    return outer_x, outer_y, inner_x, inner_y


# =============================================================================
# DRAWING UTILITIES
# =============================================================================
def draw_dimension_h(ax, x1, x2, y, label, offset=3, fontsize=7, color=C_DIM_LINE):
    """Draw horizontal dimension line with arrows and label."""
    # Extension lines
    ax.plot([x1, x1], [y - offset * 0.4, y + offset * 0.3], color=color, lw=0.4)
    ax.plot([x2, x2], [y - offset * 0.4, y + offset * 0.3], color=color, lw=0.4)
    # Dimension line with arrows
    ax.annotate('', xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle='<->', color=color, lw=0.8,
                                shrinkA=0, shrinkB=0))
    # Label
    ax.text((x1 + x2) / 2, y + offset * 0.35, label,
            ha='center', va='bottom', fontsize=fontsize, fontweight='bold',
            color=C_DIM_TEXT, fontfamily='sans-serif',
            bbox=dict(boxstyle='square,pad=0.1', facecolor='white', edgecolor='none', alpha=0.9))


def draw_dimension_v(ax, x, y1, y2, label, offset=3, fontsize=7, color=C_DIM_LINE, side='right'):
    """Draw vertical dimension line with arrows and label."""
    sign = 1 if side == 'right' else -1
    # Extension lines
    ax.plot([x - offset * 0.3, x + offset * 0.4 * sign], [y1, y1], color=color, lw=0.4)
    ax.plot([x - offset * 0.3, x + offset * 0.4 * sign], [y2, y2], color=color, lw=0.4)
    # Dimension line with arrows
    ax.annotate('', xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle='<->', color=color, lw=0.8,
                                shrinkA=0, shrinkB=0))
    # Label
    ha = 'left' if side == 'right' else 'right'
    x_text = x + offset * 0.5 * sign
    ax.text(x_text, (y1 + y2) / 2, label,
            ha=ha, va='center', fontsize=fontsize, fontweight='bold',
            color=C_DIM_TEXT, fontfamily='sans-serif', rotation=90,
            bbox=dict(boxstyle='square,pad=0.1', facecolor='white', edgecolor='none', alpha=0.9))


def draw_section_indicator(ax, x, y_top, y_bot, label, color=C_SECTION_RED):
    """Draw section cut indicator line with circle labels at ends."""
    ax.plot([x, x], [y_bot, y_top], color=color, lw=1.2, ls=(0, (6, 3)), zorder=5)
    # Circle with label at top
    circle_r = 2.8
    circle_top = plt.Circle((x, y_top + circle_r + 0.5), circle_r,
                             fill=True, facecolor=color, edgecolor=color, lw=0.8, zorder=6)
    ax.add_patch(circle_top)
    ax.text(x, y_top + circle_r + 0.5, label, ha='center', va='center',
            fontsize=6.5, fontweight='bold', color='white', zorder=7, fontfamily='sans-serif')
    # Circle with label at bottom
    circle_bot = plt.Circle((x, y_bot - circle_r - 0.5), circle_r,
                             fill=True, facecolor=color, edgecolor=color, lw=0.8, zorder=6)
    ax.add_patch(circle_bot)
    ax.text(x, y_bot - circle_r - 0.5, label, ha='center', va='center',
            fontsize=6.5, fontweight='bold', color='white', zorder=7, fontfamily='sans-serif')


def draw_engineering_border(fig):
    """Draw professional engineering drawing border with zone markers."""
    bax = fig.add_axes([0, 0, 1, 1], facecolor='none', zorder=100)
    bax.set_xlim(0, 1)
    bax.set_ylim(0, 1)
    bax.set_axis_off()

    ml, mr, mb, mt = 0.025, 0.975, 0.025, 0.975

    # Outer border (thick)
    outer = Rectangle((ml, mb), mr - ml, mt - mb,
                       linewidth=3.0, edgecolor=C_BLACK,
                       facecolor='none', zorder=101)
    bax.add_patch(outer)

    # Inner border (thin)
    im = 0.004
    inner = Rectangle((ml + im, mb + im), (mr - ml) - 2 * im, (mt - mb) - 2 * im,
                       linewidth=1.0, edgecolor=C_BLACK,
                       facecolor='none', zorder=101)
    bax.add_patch(inner)

    # Zone markers along edges
    zone_labels_h = ['4', '3', '2', '1']
    zone_labels_v = ['D', 'C', 'B', 'A']

    for i, lbl in enumerate(zone_labels_h):
        x = ml + (mr - ml) * (i + 0.5) / len(zone_labels_h)
        # Top edge
        bax.text(x, mt + 0.008, lbl, ha='center', va='bottom',
                 fontsize=8, fontweight='bold', fontfamily='sans-serif', zorder=102)
        # Bottom edge
        bax.text(x, mb - 0.008, lbl, ha='center', va='top',
                 fontsize=8, fontweight='bold', fontfamily='sans-serif', zorder=102)
        # Tick marks
        if i > 0:
            tick_x = ml + (mr - ml) * i / len(zone_labels_h)
            bax.plot([tick_x, tick_x], [mt, mt + 0.006], 'k-', lw=0.5, zorder=102)
            bax.plot([tick_x, tick_x], [mb - 0.006, mb], 'k-', lw=0.5, zorder=102)

    for i, lbl in enumerate(zone_labels_v):
        y = mb + (mt - mb) * (i + 0.5) / len(zone_labels_v)
        # Left edge
        bax.text(ml - 0.008, y, lbl, ha='right', va='center',
                 fontsize=8, fontweight='bold', fontfamily='sans-serif', zorder=102)
        # Right edge
        bax.text(mr + 0.008, y, lbl, ha='left', va='center',
                 fontsize=8, fontweight='bold', fontfamily='sans-serif', zorder=102)
        if i > 0:
            tick_y = mb + (mt - mb) * i / len(zone_labels_v)
            bax.plot([ml - 0.006, ml], [tick_y, tick_y], 'k-', lw=0.5, zorder=102)
            bax.plot([mr, mr + 0.006], [tick_y, tick_y], 'k-', lw=0.5, zorder=102)

    return bax


def draw_title_block(fig, sheet_title, sheet_num, total_sheets=3, scale="AS NOTED"):
    """Draw professional title block in lower-right corner."""
    bax = fig.add_axes([0, 0, 1, 1], facecolor='none', zorder=110)
    bax.set_xlim(0, 1)
    bax.set_ylim(0, 1)
    bax.set_axis_off()

    # Title block position and size
    tb_x = 0.52
    tb_y = 0.03
    tb_w = 0.445
    tb_h = 0.12

    # Main background
    tb_bg = Rectangle((tb_x, tb_y), tb_w, tb_h,
                       linewidth=2.0, edgecolor=C_BLACK,
                       facecolor=C_WHITE, zorder=111)
    bax.add_patch(tb_bg)

    # Top header bar (dark)
    header_h = tb_h * 0.30
    header_bg = Rectangle((tb_x, tb_y + tb_h - header_h), tb_w, header_h,
                           linewidth=1.5, edgecolor=C_BLACK,
                           facecolor=C_TITLE_BG, zorder=112)
    bax.add_patch(header_bg)

    # Header text
    bax.text(tb_x + tb_w / 2, tb_y + tb_h - header_h / 2,
             "CONCRETE CANOE",
             ha='center', va='center', fontsize=14, fontweight='bold',
             color=C_TITLE_TEXT, fontfamily='sans-serif', zorder=113)

    # Divider lines for lower section
    row_h = (tb_h - header_h) / 2

    # Horizontal divider
    mid_y = tb_y + row_h
    bax.plot([tb_x, tb_x + tb_w], [mid_y, mid_y],
             color=C_BLACK, lw=0.8, zorder=112)

    # Vertical dividers
    col_positions = [0.45, 0.70]
    for cp in col_positions:
        vx = tb_x + tb_w * cp
        bax.plot([vx, vx], [tb_y, tb_y + tb_h - header_h],
                 color=C_BLACK, lw=0.8, zorder=112)

    txt_kw = dict(zorder=113, fontfamily='sans-serif', va='center')

    # Row 1 (upper): Sheet title
    r1_y = mid_y + row_h / 2
    bax.text(tb_x + tb_w * 0.22, r1_y, sheet_title,
             ha='center', fontsize=11, fontweight='bold', **txt_kw)
    bax.text(tb_x + tb_w * 0.575, r1_y, f"SCALE: {scale}",
             ha='center', fontsize=8, **txt_kw)
    bax.text(tb_x + tb_w * 0.85, r1_y,
             f"SHEET {sheet_num} OF {total_sheets}",
             ha='center', fontsize=9, fontweight='bold', **txt_kw)

    # Row 2 (lower): Team info, date, notes
    r2_y = tb_y + row_h / 2
    bax.text(tb_x + tb_w * 0.22, r2_y,
             f"NAU ASCE 2026 \u2014 {CANOE_NAME}",
             ha='center', fontsize=8, **txt_kw)
    bax.text(tb_x + tb_w * 0.575, r2_y,
             f"DATE: {date.today().strftime('%m/%d/%Y')}",
             ha='center', fontsize=7, **txt_kw)
    bax.text(tb_x + tb_w * 0.85, r2_y,
             f"DWG: C-{sheet_num}",
             ha='center', fontsize=8, fontweight='bold', **txt_kw)

    # Notes below title block
    notes_y = tb_y - 0.012
    bax.text(tb_x + tb_w, notes_y, "DO NOT SCALE DRAWING",
             ha='right', va='top', fontsize=6, fontstyle='italic',
             fontfamily='sans-serif', color=C_MED_GRAY, zorder=113)
    bax.text(tb_x, notes_y, "DIMENSIONS ARE IN INCHES",
             ha='left', va='top', fontsize=6, fontstyle='italic',
             fontfamily='sans-serif', color=C_MED_GRAY, zorder=113)

    return bax


# =============================================================================
# SHEET 1: SECTION BREAKDOWN
# =============================================================================
def draw_sheet1_section_breakdown():
    """Plan view, profile view, and 3 cross-sections with full dimensions."""
    print("  Drawing Sheet 1: SECTION BREAKDOWN...")

    fig = plt.figure(figsize=(SHEET_W, SHEET_H), facecolor=C_BG)

    # Main drawing area
    ax = fig.add_axes([0.05, 0.16, 0.90, 0.80], facecolor=C_WHITE)
    ax.set_xlim(-30, 260)
    ax.set_ylim(-105, 100)
    ax.set_aspect('equal')
    ax.axis('off')

    # ─── PLAN VIEW (top portion) ───
    plan_y = 60  # center y for plan view
    x_hull = np.linspace(0, LOA, 300)
    x_frac = x_hull / LOA
    hw = hull_halfwidth(x_frac)

    # Fill hull shape
    ax.fill_between(x_hull, plan_y - hw, plan_y + hw,
                     color='#E8ECF0', alpha=0.6, edgecolor='none')
    ax.plot(x_hull, plan_y + hw, C_HULL_EDGE, lw=1.5)
    ax.plot(x_hull, plan_y - hw, C_HULL_EDGE, lw=1.5)

    # Centerline (chain dash)
    for i in range(0, int(LOA), 8):
        x_start = i
        x_end = min(i + 5, LOA)
        ax.plot([x_start, x_end], [plan_y, plan_y], 'k-', lw=0.4, alpha=0.5)
        if i + 6 < LOA:
            ax.plot([i + 5.5, i + 6.5], [plan_y, plan_y], 'k-', lw=0.4, alpha=0.5)

    # CL symbol
    ax.text(-8, plan_y, "CL", ha='center', va='center', fontsize=7,
            fontfamily='sans-serif', fontstyle='italic')
    # Overline on C
    ax.plot([-10.5, -5.5], [plan_y + 1.5, plan_y + 1.5], 'k-', lw=0.6)

    # Plan view label (positioned to left to avoid section indicator overlap)
    ax.text(30, plan_y + BEAM / 2 + 14, "PLAN VIEW",
            ha='left', va='bottom', fontsize=11, fontweight='bold',
            fontfamily='sans-serif')
    ax.text(30, plan_y + BEAM / 2 + 10, "SCALE: 1:10",
            ha='left', va='bottom', fontsize=7, fontfamily='sans-serif',
            color=C_MED_GRAY)

    # Overall length dimension
    dim_y_top = plan_y + BEAM / 2 + 6
    draw_dimension_h(ax, 0, LOA, dim_y_top, f'{LOA:.0f}"', offset=3, fontsize=9)

    # Extension lines from hull ends to dimension line
    ax.plot([0, 0], [plan_y, dim_y_top + 1], C_DIM_LINE, lw=0.3)
    ax.plot([LOA, LOA], [plan_y, dim_y_top + 1], C_DIM_LINE, lw=0.3)

    # Beam dimension at midship
    mid_x = LOA / 2
    mid_hw = hull_halfwidth(0.5)
    beam_dim_x = LOA + 10
    ax.plot([mid_x, beam_dim_x + 2], [plan_y + mid_hw, plan_y + mid_hw],
            C_DIM_LINE, lw=0.3, alpha=0.5)
    ax.plot([mid_x, beam_dim_x + 2], [plan_y - mid_hw, plan_y - mid_hw],
            C_DIM_LINE, lw=0.3, alpha=0.5)
    draw_dimension_v(ax, beam_dim_x, plan_y - mid_hw, plan_y + mid_hw,
                     f'{BEAM:.0f}"', offset=4, fontsize=8, side='right')

    # Section cut lines on plan view
    cut_colors = [C_SECTION_RED, C_SECTION_BLUE, C_SECTION_GREEN]
    for i, (lbl1, lbl2, frac, w, d, desc) in enumerate(SECTION_CUTS):
        sx = frac * LOA
        shw = hull_halfwidth(frac) + 5
        draw_section_indicator(ax, sx, plan_y + shw, plan_y - shw,
                               lbl1, color=cut_colors[i])

    # ─── PROFILE VIEW (middle portion) ───
    prof_y = 20  # baseline y for profile
    ax.text(30, prof_y + DEPTH + 6, "PROFILE VIEW",
            ha='left', va='bottom', fontsize=11, fontweight='bold',
            fontfamily='sans-serif')
    ax.text(30, prof_y + DEPTH + 2.5, "SCALE: 1:10",
            ha='left', va='bottom', fontsize=7, fontfamily='sans-serif',
            color=C_MED_GRAY)

    # Keel line (bottom of hull with rocker)
    x_prof = np.linspace(0, LOA, 300)
    x_frac_prof = x_prof / LOA
    keel_y = prof_y + hull_keel_y(x_frac_prof)
    depths = hull_depth_at(x_frac_prof)

    # Sheer line (top of hull)
    sheer_y = keel_y + depths

    # Draw hull profile
    ax.fill_between(x_prof, keel_y, sheer_y,
                     color='#E8ECF0', alpha=0.4, edgecolor='none')
    ax.plot(x_prof, keel_y, C_HULL_EDGE, lw=1.5)
    ax.plot(x_prof, sheer_y, C_HULL_EDGE, lw=1.5)

    # Connect bow and stern
    ax.plot([x_prof[0], x_prof[0]], [keel_y[0], sheer_y[0]], C_HULL_EDGE, lw=1.5)
    ax.plot([x_prof[-1], x_prof[-1]], [keel_y[-1], sheer_y[-1]], C_HULL_EDGE, lw=1.5)

    # Depth dimension at midship
    mid_idx = len(x_prof) // 2
    depth_dim_x = LOA + 10
    ax.plot([mid_x, depth_dim_x + 2], [keel_y[mid_idx], keel_y[mid_idx]],
            C_DIM_LINE, lw=0.3, alpha=0.5)
    ax.plot([mid_x, depth_dim_x + 2], [sheer_y[mid_idx], sheer_y[mid_idx]],
            C_DIM_LINE, lw=0.3, alpha=0.5)
    draw_dimension_v(ax, depth_dim_x, keel_y[mid_idx], sheer_y[mid_idx],
                     f'{DEPTH:.0f}"', offset=4, fontsize=8, side='right')

    # Rocker dimension
    rocker_x = 15
    ax.annotate(f'ROCKER: {ROCKER:.0f}"',
                xy=(10, keel_y[0]),
                xytext=(25, prof_y - 8),
                fontsize=6, fontfamily='sans-serif', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=C_MED_GRAY, lw=0.6),
                color=C_MED_GRAY)

    # Section cut lines on profile
    for i, (lbl1, lbl2, frac, w, d, desc) in enumerate(SECTION_CUTS):
        sx = frac * LOA
        idx = int(frac * (len(x_prof) - 1))
        draw_section_indicator(ax, sx, sheer_y[idx] + 2, keel_y[idx] - 2,
                               lbl1, color=cut_colors[i])

    # ─── CROSS-SECTIONS (bottom row) ───
    section_base_y = -55
    section_spacing = 70
    section_starts = [15, 15 + section_spacing, 15 + 2 * section_spacing]

    for i, (lbl1, lbl2, frac, width, depth, desc) in enumerate(SECTION_CUTS):
        cx = section_starts[i] + width / 2  # center x of section
        base_y = section_base_y

        # Get U-section geometry
        ox, oy, ix, iy = get_simple_u_section(width, depth, THICKNESS)

        # Scale for display (1:4 scale representation but in drawing coords)
        display_scale = 1.0

        # Offset to position
        draw_ox = ox * display_scale + cx
        draw_oy = oy * display_scale + base_y
        draw_ix = ix * display_scale + cx
        draw_iy = iy * display_scale + base_y

        # Draw filled U-shape (concrete)
        # Create closed polygon: outer path forward, inner path reversed
        outer_pts = list(zip(draw_ox, draw_oy))
        inner_pts = list(zip(draw_ix, draw_iy))
        all_pts = outer_pts + inner_pts[::-1]

        poly = Polygon(all_pts, closed=True,
                        facecolor=C_HULL_FILL, edgecolor=C_HULL_EDGE,
                        lw=1.2, zorder=3)
        ax.add_patch(poly)

        # Draw outer and inner profiles explicitly for clarity
        ax.plot(draw_ox, draw_oy, C_HULL_EDGE, lw=1.5, zorder=4)
        ax.plot(draw_ix, draw_iy, C_HULL_EDGE, lw=0.8, zorder=4, ls='-')

        # Hatching for concrete (diagonal lines)
        hatch_spacing = 2.0
        for hy in np.arange(base_y, base_y + depth, hatch_spacing):
            # Find intersection with outer and inner profile
            y_rel = hy - base_y
            # Simple hatch lines across the walls
            for hx_offset in np.arange(-width / 2, width / 2, hatch_spacing):
                hx = cx + hx_offset
                # Check if point is inside the U-shape (between outer and inner)
                # Simplified: just draw short diagonal lines in the fill area
                pass  # Skip complex hatching for cleaner look

        # Width dimension below
        draw_dimension_h(ax, cx - width / 2, cx + width / 2,
                          base_y - 6, f'{width:.0f}"', offset=3, fontsize=7)

        # Depth dimension to the right
        draw_dimension_v(ax, cx + width / 2 + 5, base_y, base_y + depth,
                          f'{depth:.0f}"', offset=3, fontsize=7, side='right')

        # Thickness callout
        # Arrow pointing to the wall
        wall_x = cx + width / 2 - THICKNESS / 2
        wall_y = base_y + depth * 0.6
        ax.annotate(f't = {THICKNESS:.2f}"',
                    xy=(cx + width / 2 * 0.85, base_y + depth * 0.5),
                    xytext=(cx + width / 2 + 12, base_y + depth * 0.7),
                    fontsize=6, fontfamily='sans-serif',
                    arrowprops=dict(arrowstyle='->', color=C_BLACK, lw=0.5),
                    bbox=dict(boxstyle='square,pad=0.15', facecolor='white',
                              edgecolor=C_LIGHT_GRAY, lw=0.5),
                    zorder=5)

        # Section label
        ax.text(cx, base_y + depth + 4,
                f"SECTION {lbl1}-{lbl2}",
                ha='center', va='bottom', fontsize=9, fontweight='bold',
                color=cut_colors[i], fontfamily='sans-serif')
        ax.text(cx, base_y + depth + 1,
                desc, ha='center', va='bottom', fontsize=6,
                color=C_MED_GRAY, fontfamily='sans-serif')
        ax.text(cx, base_y - 10,
                "SCALE 1:4", ha='center', va='top', fontsize=6,
                color=C_MED_GRAY, fontfamily='sans-serif')

        # Keel reinforcement indicator at bottom center
        if True:  # Show keel detail on all sections
            keel_w = 3.0
            keel_extra = KEEL_THICKNESS - THICKNESS
            keel_rect = Rectangle((cx - keel_w / 2, base_y - keel_extra),
                                   keel_w, keel_extra + 1,
                                   facecolor=C_KEEL_FILL, edgecolor=C_BLACK,
                                   lw=0.8, zorder=3)
            ax.add_patch(keel_rect)

    # ─── Notes ───
    ax.text(-20, -95, "NOTES:", fontsize=7, fontweight='bold',
            fontfamily='sans-serif')
    notes = [
        f"1. ALL DIMENSIONS IN INCHES",
        f"2. WALL THICKNESS: {THICKNESS}\" UNIFORM",
        f"3. KEEL THICKNESS: {KEEL_THICKNESS}\" (REINFORCED)",
        f"4. V-BOTTOM DEADRISE: {V_BOTTOM_ANGLE}\u00b0",
        f"5. HULL WEIGHT: {HULL_WEIGHT:.0f} LBS (EST.)",
        f"6. MATERIAL: LIGHTWEIGHT CONCRETE MIX @ 70 PCF",
    ]
    for j, note in enumerate(notes):
        ax.text(-20, -100 - j * 4, note, fontsize=5.5,
                fontfamily='sans-serif', color=C_DARK_GRAY)

    # Border and title block
    draw_engineering_border(fig)
    draw_title_block(fig, "SECTION BREAKDOWN", 1, scale="AS NOTED")

    out_path = os.path.join(REPORTS_FIG_DIR, "cad_sheet1_section_breakdown.png")
    fig.savefig(out_path, dpi=DPI, facecolor=C_BG, edgecolor='none')
    plt.close(fig)
    print(f"    Saved: {out_path}")
    return out_path


# =============================================================================
# SHEET 2: TOP AND ISOMETRIC VIEW
# =============================================================================
def draw_sheet2_top_isometric():
    """Dimensioned top view and 3D isometric wireframe."""
    print("  Drawing Sheet 2: TOP AND ISOMETRIC VIEW...")

    fig = plt.figure(figsize=(SHEET_W, SHEET_H), facecolor=C_BG)

    # ─── TOP VIEW (upper portion) ───
    ax_top = fig.add_axes([0.06, 0.48, 0.88, 0.46], facecolor=C_WHITE)
    ax_top.set_aspect('equal')
    ax_top.axis('off')

    x_hull = np.linspace(0, LOA, 400)
    x_frac = x_hull / LOA
    hw = hull_halfwidth(x_frac)

    # Fill hull
    ax_top.fill_between(x_hull, -hw, hw,
                         color='#E8ECF0', alpha=0.5, edgecolor='none')
    ax_top.plot(x_hull, hw, C_HULL_EDGE, lw=1.8)
    ax_top.plot(x_hull, -hw, C_HULL_EDGE, lw=1.8)

    # Centerline
    for i in range(0, int(LOA), 10):
        ax_top.plot([i, min(i + 7, LOA)], [0, 0], 'k-', lw=0.3, alpha=0.4)
        if i + 8.5 < LOA:
            ax_top.plot([i + 7.5, i + 8.5], [0, 0], 'k-', lw=0.3, alpha=0.4)

    # Station lines (every 12 inches = 18 stations)
    n_stations = 18
    for si in range(n_stations + 1):
        sx = si * LOA / n_stations
        sf = sx / LOA
        shw = hull_halfwidth(sf)
        if shw > 0.5:
            ax_top.plot([sx, sx], [-shw, shw], 'k-', lw=0.3, alpha=0.25)
            if si % 3 == 0 and si > 0 and si < n_stations:
                ax_top.text(sx, -shw - 2, f"STA {si}",
                            ha='center', va='top', fontsize=4.5,
                            fontfamily='sans-serif', color=C_MED_GRAY)

    # Overall length dimension
    dim_y = BEAM / 2 + 7
    draw_dimension_h(ax_top, 0, LOA, dim_y, f'{LOA:.0f}"', offset=3, fontsize=9)
    ax_top.plot([0, 0], [0, dim_y + 1], C_DIM_LINE, lw=0.3)
    ax_top.plot([LOA, LOA], [0, dim_y + 1], C_DIM_LINE, lw=0.3)

    # Beam dimension
    beam_dim_x = LOA + 12
    mid_hw = hull_halfwidth(0.5)
    ax_top.plot([LOA / 2, beam_dim_x + 2], [mid_hw, mid_hw], C_DIM_LINE, lw=0.3, alpha=0.4)
    ax_top.plot([LOA / 2, beam_dim_x + 2], [-mid_hw, -mid_hw], C_DIM_LINE, lw=0.3, alpha=0.4)
    draw_dimension_v(ax_top, beam_dim_x, -mid_hw, mid_hw,
                     f'{BEAM:.0f}"', offset=4, fontsize=8, side='right')

    # Partial dimensions (bow to midship, midship to stern)
    dim_y2 = BEAM / 2 + 3
    draw_dimension_h(ax_top, 0, LOA / 2, dim_y2, f'{LOA / 2:.0f}"', offset=2, fontsize=7)
    draw_dimension_h(ax_top, LOA / 2, LOA, dim_y2, f'{LOA / 2:.0f}"', offset=2, fontsize=7)

    # Station width dimensions at key stations
    for frac, lbl in [(0.25, "STA 1"), (0.50, "MID"), (0.75, "STA 3")]:
        sx = frac * LOA
        shw = hull_halfwidth(frac)
        w = shw * 2
        ax_top.plot([sx - 0.5, sx + 0.5], [-shw, -shw], 'k-', lw=0.5)
        ax_top.plot([sx - 0.5, sx + 0.5], [shw, shw], 'k-', lw=0.5)
        ax_top.text(sx, -shw - 3, f'{w:.0f}"', ha='center', va='top',
                    fontsize=6, fontweight='bold', fontfamily='sans-serif')

    # Labels
    ax_top.text(LOA / 2, BEAM / 2 + 16, "TOP VIEW (PLAN)",
                ha='center', va='bottom', fontsize=12, fontweight='bold',
                fontfamily='sans-serif')
    ax_top.text(LOA / 2, BEAM / 2 + 12.5, "SCALE: 1:10",
                ha='center', va='bottom', fontsize=7, fontfamily='sans-serif',
                color=C_MED_GRAY)

    # CL label
    ax_top.text(-10, 0, "CL", ha='center', va='center', fontsize=7,
                fontfamily='sans-serif', fontstyle='italic')
    ax_top.plot([-12, -8], [1.5, 1.5], 'k-', lw=0.6)

    # BOW / STERN labels
    ax_top.text(-5, 0, "BOW", ha='right', va='center', fontsize=7,
                fontweight='bold', fontfamily='sans-serif', rotation=90)
    ax_top.text(LOA + 5, 0, "STERN", ha='left', va='center', fontsize=7,
                fontweight='bold', fontfamily='sans-serif', rotation=90)

    ax_top.set_xlim(-20, LOA + 25)
    ax_top.set_ylim(-BEAM / 2 - 10, BEAM / 2 + 22)

    # ─── ISOMETRIC VIEW (lower portion) ───
    ax_iso = fig.add_axes([0.06, 0.02, 0.88, 0.44], facecolor=C_WHITE)
    ax_iso.set_aspect('equal')
    ax_iso.axis('off')

    # Isometric projection: 30 degree angles
    # Transform: x_iso = x * cos(30) - y * cos(30)
    #            y_iso = x * sin(30) + y * sin(30) + z
    angle = np.radians(30)
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)

    def iso_transform(x, y, z):
        """Transform 3D coords to isometric 2D."""
        xi = x * cos_a - y * cos_a
        yi = x * sin_a + y * sin_a + z
        return xi, yi

    # Generate hull surface stations
    n_long = 25  # longitudinal stations
    n_circ = 20  # circumferential points per station

    # Draw wireframe hull
    for i in range(n_long + 1):
        frac = i / n_long
        x_3d = frac * LOA
        hw_local = hull_halfwidth(frac)
        d_local = hull_depth_at(frac)
        keel_offset = hull_keel_y(frac)

        # Cross-section at this station: simple U-shape
        theta = np.linspace(-1, 1, n_circ)
        y_cs = theta * hw_local
        # Depth varies: deepest at center
        z_cs = -d_local * (1 - np.abs(theta) ** 1.5) - keel_offset

        # Sheer line (top of hull)
        z_sheer = np.zeros_like(theta) - keel_offset

        # Combine for cross-section curve (bottom + sides)
        x_arr = np.full_like(y_cs, x_3d)
        xi, yi = iso_transform(x_arr, y_cs, z_cs)
        xi_s, yi_s = iso_transform(x_arr, y_cs, z_sheer)

        # Draw cross-section waterlines
        if i % 3 == 0 or i == 0 or i == n_long:
            ax_iso.plot(xi, yi, C_HULL_EDGE, lw=0.5, alpha=0.5)
            # Connect sheer to bottom at edges
            if hw_local > 1:
                ax_iso.plot([xi[0], xi_s[0]], [yi[0], yi_s[0]],
                            C_HULL_EDGE, lw=0.4, alpha=0.3)
                ax_iso.plot([xi[-1], xi_s[-1]], [yi[-1], yi_s[-1]],
                            C_HULL_EDGE, lw=0.4, alpha=0.3)

    # Longitudinal lines (waterlines)
    for j in range(n_circ):
        theta_val = -1 + 2 * j / (n_circ - 1)
        x_long = []
        y_long = []
        for i in range(n_long + 1):
            frac = i / n_long
            x_3d = frac * LOA
            hw_local = hull_halfwidth(frac)
            d_local = hull_depth_at(frac)
            keel_offset = hull_keel_y(frac)

            y_3d = theta_val * hw_local
            z_3d = -d_local * (1 - np.abs(theta_val) ** 1.5) - keel_offset

            xi, yi = iso_transform(x_3d, y_3d, z_3d)
            x_long.append(xi)
            y_long.append(yi)

        if j % 3 == 0 or j == 0 or j == n_circ - 1:
            ax_iso.plot(x_long, y_long, C_HULL_EDGE, lw=0.4, alpha=0.4)

    # Sheer line (top edge) - port and starboard
    for side in [-1, 1]:
        x_sheer_3d = np.linspace(0, LOA, 200)
        y_sheer_3d = side * hull_halfwidth(x_sheer_3d / LOA)
        z_sheer_3d = -hull_keel_y(x_sheer_3d / LOA)
        xi_sh, yi_sh = iso_transform(x_sheer_3d, y_sheer_3d, z_sheer_3d)
        ax_iso.plot(xi_sh, yi_sh, C_HULL_EDGE, lw=1.5)

    # Keel line (bottom center)
    x_keel = np.linspace(0, LOA, 200)
    y_keel_3d = np.zeros(200)
    d_keel = hull_depth_at(x_keel / LOA)
    z_keel_3d = -d_keel - hull_keel_y(x_keel / LOA)
    xi_k, yi_k = iso_transform(x_keel, y_keel_3d, z_keel_3d)
    ax_iso.plot(xi_k, yi_k, C_HULL_EDGE, lw=1.2)

    # Fill the visible hull surface with light color
    # Use the starboard sheer and keel as boundary
    xi_sheer_s, yi_sheer_s = iso_transform(x_sheer_3d, hull_halfwidth(x_sheer_3d / LOA),
                                             -hull_keel_y(x_sheer_3d / LOA))
    hull_x_fill = np.concatenate([xi_sheer_s, xi_k[::-1]])
    hull_y_fill = np.concatenate([yi_sheer_s, yi_k[::-1]])
    ax_iso.fill(hull_x_fill, hull_y_fill, color='#E0E4E8', alpha=0.3, zorder=0)

    # Isometric label
    ax_iso.text(0.5, 0.97, "ISOMETRIC VIEW",
                transform=ax_iso.transAxes,
                ha='center', va='top', fontsize=12, fontweight='bold',
                fontfamily='sans-serif')
    ax_iso.text(0.5, 0.93, "3D WIREFRAME RENDERING — NTS",
                transform=ax_iso.transAxes,
                ha='center', va='top', fontsize=7,
                fontfamily='sans-serif', color=C_MED_GRAY)

    # Auto-scale
    ax_iso.autoscale()
    # Add some padding
    xl = ax_iso.get_xlim()
    yl = ax_iso.get_ylim()
    pad_x = (xl[1] - xl[0]) * 0.05
    pad_y = (yl[1] - yl[0]) * 0.08
    ax_iso.set_xlim(xl[0] - pad_x, xl[1] + pad_x)
    ax_iso.set_ylim(yl[0] - pad_y, yl[1] + pad_y)

    # Border and title block
    draw_engineering_border(fig)
    draw_title_block(fig, "TOP AND ISOMETRIC VIEW", 2, scale="AS NOTED")

    out_path = os.path.join(REPORTS_FIG_DIR, "cad_sheet2_top_isometric.png")
    fig.savefig(out_path, dpi=DPI, facecolor=C_BG, edgecolor='none')
    plt.close(fig)
    print(f"    Saved: {out_path}")
    return out_path


# =============================================================================
# SHEET 3: CONSTRUCTION DETAILS
# =============================================================================
def draw_sheet3_construction_details():
    """Mold section, reinforcement layout, layer buildup, and keel detail."""
    print("  Drawing Sheet 3: CONSTRUCTION DETAILS...")

    fig = plt.figure(figsize=(SHEET_W, SHEET_H), facecolor=C_BG)

    # ─── DETAIL A: MOLD CROSS-SECTION (upper left) ───
    ax_mold = fig.add_axes([0.05, 0.52, 0.44, 0.40], facecolor=C_WHITE)
    ax_mold.set_aspect('equal')
    ax_mold.axis('off')

    # Mold: female mold from EPS foam
    mold_w = BEAM + 8   # mold wider than hull
    mold_d = DEPTH + 4   # mold deeper than hull
    mold_base_y = 0

    # EPS foam block outline
    foam_rect = Rectangle((-mold_w / 2, mold_base_y), mold_w, mold_d,
                           facecolor=C_FOAM_BEIGE, edgecolor=C_BLACK,
                           lw=1.5, zorder=1)
    ax_mold.add_patch(foam_rect)

    # Female mold cavity (hull shape carved out)
    ox, oy, ix, iy = get_simple_u_section(BEAM, DEPTH, 0)  # just outer profile for mold
    # Fill the cavity
    cavity_x = np.concatenate([ox, [BEAM / 2, -BEAM / 2]])
    cavity_y = np.concatenate([oy, [DEPTH + 2, DEPTH + 2]]) + mold_base_y
    cavity_x_shifted = cavity_x
    ax_mold.fill(cavity_x_shifted, cavity_y, color=C_WHITE, edgecolor=C_BLACK,
                 lw=1.0, zorder=2)

    # Draw hull shell inside mold cavity
    ox2, oy2, ix2, iy2 = get_simple_u_section(BEAM, DEPTH, THICKNESS)
    outer_pts = list(zip(ox2, oy2 + mold_base_y))
    inner_pts = list(zip(ix2, iy2 + mold_base_y))
    shell_pts = outer_pts + inner_pts[::-1]
    shell_poly = Polygon(shell_pts, closed=True,
                          facecolor=C_CONCRETE, edgecolor=C_BLACK,
                          lw=1.0, zorder=3, alpha=0.7)
    ax_mold.add_patch(shell_poly)

    # Strongback / support table below
    table_y = mold_base_y - 3
    table_rect = Rectangle((-mold_w / 2 - 2, table_y), mold_w + 4, 2,
                            facecolor='#8B7355', edgecolor=C_BLACK, lw=1.0, zorder=1)
    ax_mold.add_patch(table_rect)
    # Legs
    for lx in [-mold_w / 2 + 2, mold_w / 2 - 2]:
        leg = Rectangle((lx - 1, table_y - 8), 2, 8,
                         facecolor='#8B7355', edgecolor=C_BLACK, lw=0.8, zorder=1)
        ax_mold.add_patch(leg)

    # Dimensions
    draw_dimension_h(ax_mold, -mold_w / 2, mold_w / 2,
                     mold_base_y + mold_d + 4, f'{mold_w:.0f}"', fontsize=7)
    draw_dimension_h(ax_mold, -BEAM / 2, BEAM / 2,
                     mold_base_y + DEPTH + 3, f'{BEAM:.0f}"', fontsize=6, color=C_MED_GRAY)
    draw_dimension_v(ax_mold, mold_w / 2 + 5, mold_base_y, mold_base_y + mold_d,
                     f'{mold_d:.0f}"', fontsize=7, side='right')
    draw_dimension_v(ax_mold, BEAM / 2 + 3, mold_base_y, mold_base_y + DEPTH,
                     f'{DEPTH:.0f}"', fontsize=6, side='right', color=C_MED_GRAY)

    # Labels
    ax_mold.text(0, mold_base_y + mold_d / 2 + 3, "EPS FOAM\nMOLD BLOCK",
                 ha='center', va='center', fontsize=7, fontweight='bold',
                 fontfamily='sans-serif', color='#8B6914',
                 bbox=dict(boxstyle='round,pad=0.2', facecolor=C_FOAM_BEIGE,
                           edgecolor='#8B6914', lw=0.5))
    ax_mold.text(0, mold_base_y + DEPTH * 0.4, "CONCRETE\nSHELL",
                 ha='center', va='center', fontsize=6, fontweight='bold',
                 fontfamily='sans-serif', color=C_DARK_GRAY)
    ax_mold.text(0, table_y - 5, "MDF STRONGBACK",
                 ha='center', va='center', fontsize=6, fontfamily='sans-serif',
                 color='#5C4033')

    ax_mold.set_xlim(-mold_w / 2 - 10, mold_w / 2 + 15)
    ax_mold.set_ylim(table_y - 12, mold_base_y + mold_d + 10)

    ax_mold.text(0.5, 1.02, "DETAIL A: MOLD CROSS-SECTION",
                 transform=ax_mold.transAxes, ha='center', va='bottom',
                 fontsize=10, fontweight='bold', fontfamily='sans-serif')
    ax_mold.text(0.5, 0.98, "AT MIDSHIP \u2014 SCALE: NTS",
                 transform=ax_mold.transAxes, ha='center', va='bottom',
                 fontsize=7, fontfamily='sans-serif', color=C_MED_GRAY)

    # ─── DETAIL B: REINFORCEMENT LAYOUT (upper right) ───
    ax_reinf = fig.add_axes([0.52, 0.52, 0.44, 0.40], facecolor=C_WHITE)
    ax_reinf.set_aspect('equal')
    ax_reinf.axis('off')

    # Cross-section showing reinforcement placement
    ox3, oy3, ix3, iy3 = get_simple_u_section(BEAM, DEPTH, THICKNESS)
    base_yr = 2

    # Draw outer hull shape
    ax_reinf.plot(ox3, oy3 + base_yr, C_HULL_EDGE, lw=1.5)
    ax_reinf.plot(ix3, iy3 + base_yr, C_HULL_EDGE, lw=1.0)

    # Fill concrete
    outer_pts_r = list(zip(ox3, oy3 + base_yr))
    inner_pts_r = list(zip(ix3, iy3 + base_yr))
    shell_pts_r = outer_pts_r + inner_pts_r[::-1]
    shell_r = Polygon(shell_pts_r, closed=True,
                       facecolor=C_HULL_FILL, edgecolor='none',
                       lw=0, zorder=1, alpha=0.5)
    ax_reinf.add_patch(shell_r)

    # Fiberglass mesh layers (shown as colored lines within the wall)
    # Outer mesh (near outer surface)
    mesh_scale_outer = 0.97
    mesh_scale_inner = 0.88
    mesh_ox = ox3 * mesh_scale_outer
    mesh_oy = oy3 * mesh_scale_outer + base_yr + THICKNESS * 0.05
    mesh_ix = ox3 * mesh_scale_inner
    mesh_iy = oy3 * mesh_scale_inner + base_yr + THICKNESS * 0.4

    ax_reinf.plot(mesh_ox, mesh_oy, color=C_FIBERGLASS, lw=2.0, ls='-', zorder=3,
                  label='Fiberglass mesh (outer)')
    ax_reinf.plot(mesh_ix, mesh_iy, color=C_FIBERGLASS, lw=2.0, ls='--', zorder=3,
                  label='Fiberglass mesh (inner)')

    # Callout arrows for mesh layers
    ax_reinf.annotate("OUTER FIBERGLASS\nMESH LAYER",
                      xy=(BEAM / 2 * 0.97, DEPTH * 0.6 + base_yr),
                      xytext=(BEAM / 2 + 8, DEPTH * 0.8 + base_yr),
                      fontsize=5.5, fontfamily='sans-serif', fontweight='bold',
                      color=C_FIBERGLASS,
                      arrowprops=dict(arrowstyle='->', color=C_FIBERGLASS, lw=0.6))

    ax_reinf.annotate("INNER FIBERGLASS\nMESH LAYER",
                      xy=(BEAM / 2 * 0.88, DEPTH * 0.45 + base_yr),
                      xytext=(BEAM / 2 + 8, DEPTH * 0.35 + base_yr),
                      fontsize=5.5, fontfamily='sans-serif', fontweight='bold',
                      color='#2D8B2D',
                      arrowprops=dict(arrowstyle='->', color='#2D8B2D', lw=0.6))

    # Concrete label
    mid_wall_x = BEAM / 2 * 0.92
    mid_wall_y = DEPTH * 0.55 + base_yr
    ax_reinf.annotate("CONCRETE\n(0.75\" THICK)",
                      xy=(0, DEPTH * 0.3 + base_yr),
                      xytext=(-BEAM / 2 - 10, DEPTH * 0.5 + base_yr),
                      fontsize=5.5, fontfamily='sans-serif',
                      color=C_MED_GRAY, fontweight='bold',
                      arrowprops=dict(arrowstyle='->', color=C_MED_GRAY, lw=0.6))

    # Keel reinforcement
    keel_marker = Rectangle((-2, base_yr - 0.5), 4, 1.5,
                             facecolor=C_KEEL_FILL, edgecolor=C_BLACK, lw=0.8, zorder=4)
    ax_reinf.add_patch(keel_marker)
    ax_reinf.annotate("THICKENED KEEL\n(1.00\" THICK)",
                      xy=(0, base_yr - 0.5),
                      xytext=(-BEAM / 2 - 10, base_yr - 3),
                      fontsize=5.5, fontfamily='sans-serif',
                      color=C_DARK_GRAY, fontweight='bold',
                      arrowprops=dict(arrowstyle='->', color=C_DARK_GRAY, lw=0.6))

    ax_reinf.set_xlim(-BEAM / 2 - 15, BEAM / 2 + 18)
    ax_reinf.set_ylim(base_yr - 6, base_yr + DEPTH + 6)

    ax_reinf.text(0.5, 1.02, "DETAIL B: REINFORCEMENT LAYOUT",
                  transform=ax_reinf.transAxes, ha='center', va='bottom',
                  fontsize=10, fontweight='bold', fontfamily='sans-serif')
    ax_reinf.text(0.5, 0.98, "CROSS-SECTION AT MIDSHIP \u2014 SCALE: NTS",
                  transform=ax_reinf.transAxes, ha='center', va='bottom',
                  fontsize=7, fontfamily='sans-serif', color=C_MED_GRAY)

    # Legend for reinforcement
    legend_elements = [
        Line2D([0], [0], color=C_FIBERGLASS, lw=2, label='Outer fiberglass mesh'),
        Line2D([0], [0], color=C_FIBERGLASS, lw=2, ls='--', label='Inner fiberglass mesh'),
        mpatches.Patch(facecolor=C_HULL_FILL, edgecolor=C_BLACK, lw=0.5, label='Concrete'),
        mpatches.Patch(facecolor=C_KEEL_FILL, edgecolor=C_BLACK, lw=0.5, label='Reinforced keel'),
    ]
    ax_reinf.legend(handles=legend_elements, loc='lower right', fontsize=6,
                    framealpha=0.9, edgecolor=C_LIGHT_GRAY)

    # ─── DETAIL C: LAYER BUILDUP (lower left) ───
    ax_layer = fig.add_axes([0.05, 0.14, 0.44, 0.34], facecolor=C_WHITE)
    ax_layer.set_aspect('equal')
    ax_layer.axis('off')

    # Show exploded layer buildup
    layer_x = 0
    layer_w = 40
    layers = [
        ("MOLD SURFACE (EPS FOAM)", 4.0, C_FOAM_BEIGE, C_BLACK),
        ("RELEASE AGENT", 0.5, C_RELEASE_AGENT, C_DARK_GRAY),
        ("OUTER FIBERGLASS MESH", 0.8, C_FIBERGLASS, C_BLACK),
        ("CONCRETE (0.75\")", 5.0, C_CONCRETE, C_BLACK),
        ("INNER FIBERGLASS MESH", 0.8, C_FIBERGLASS, C_BLACK),
        ("SURFACE FINISH / SEALANT", 0.4, '#E0D0C0', C_DARK_GRAY),
    ]

    current_y = 0
    gap = 1.5  # gap between layers for exploded view
    layer_positions = []

    for name, thick, fill_color, edge_color in layers:
        rect = Rectangle((layer_x, current_y), layer_w, thick,
                          facecolor=fill_color, edgecolor=edge_color,
                          lw=1.0, zorder=2)
        ax_layer.add_patch(rect)

        # Label
        ax_layer.text(layer_x + layer_w + 2, current_y + thick / 2,
                      name, ha='left', va='center', fontsize=6,
                      fontfamily='sans-serif', fontweight='bold',
                      color=C_DARK_GRAY)

        # Thickness dimension
        if thick >= 0.5:
            ax_layer.text(layer_x - 2, current_y + thick / 2,
                          f'{thick / 5 * 0.75:.2f}"' if name.startswith("CONCRETE") else "",
                          ha='right', va='center', fontsize=5.5,
                          fontfamily='sans-serif', color=C_MED_GRAY)

        layer_positions.append((current_y, thick))
        current_y += thick + gap

    # Overall thickness dimension
    total_bottom = layer_positions[2][0]  # outer fiberglass
    total_top = layer_positions[4][0] + layer_positions[4][1]  # inner fiberglass top
    draw_dimension_v(ax_layer, layer_x - 6, total_bottom, total_top,
                     f'{THICKNESS:.2f}" WALL', offset=3, fontsize=7, side='left')

    # Arrow showing "INSIDE" and "OUTSIDE"
    ax_layer.text(layer_x + layer_w / 2, -2, "\u2190 MOLD SIDE (OUTSIDE)",
                  ha='center', va='top', fontsize=6, fontweight='bold',
                  fontfamily='sans-serif', color=C_MED_GRAY)
    ax_layer.text(layer_x + layer_w / 2, current_y + 1, "INTERIOR SIDE \u2192",
                  ha='center', va='bottom', fontsize=6, fontweight='bold',
                  fontfamily='sans-serif', color=C_MED_GRAY)

    ax_layer.set_xlim(-15, layer_w + 35)
    ax_layer.set_ylim(-5, current_y + 5)

    ax_layer.text(0.5, 1.02, "DETAIL C: LAYER BUILDUP (EXPLODED)",
                  transform=ax_layer.transAxes, ha='center', va='bottom',
                  fontsize=10, fontweight='bold', fontfamily='sans-serif')
    ax_layer.text(0.5, 0.97, "WALL CONSTRUCTION SEQUENCE \u2014 NTS",
                  transform=ax_layer.transAxes, ha='center', va='bottom',
                  fontsize=7, fontfamily='sans-serif', color=C_MED_GRAY)

    # Build sequence numbering
    for idx, (name, thick, fill_color, edge_color) in enumerate(layers):
        y_pos = layer_positions[idx][0] + layer_positions[idx][1] / 2
        circle = plt.Circle((layer_x - 4, y_pos), 1.5,
                             facecolor=C_TITLE_BG, edgecolor=C_BLACK, lw=0.5, zorder=5)
        ax_layer.add_patch(circle)
        ax_layer.text(layer_x - 4, y_pos, str(idx + 1),
                      ha='center', va='center', fontsize=5.5, fontweight='bold',
                      color=C_WHITE, fontfamily='sans-serif', zorder=6)

    # ─── DETAIL D: KEEL DETAIL (lower right) ───
    ax_keel = fig.add_axes([0.52, 0.14, 0.44, 0.34], facecolor=C_WHITE)
    ax_keel.set_aspect('equal')
    ax_keel.axis('off')

    # Zoomed keel cross-section detail
    # Show the keel area with thickened section
    keel_zoom_scale = 8  # zoom factor

    # Draw zoomed keel area
    keel_width = 6.0 * keel_zoom_scale  # keel reinforcement width
    wall_thick = THICKNESS * keel_zoom_scale
    keel_thick = KEEL_THICKNESS * keel_zoom_scale

    keel_cx = 30  # center x
    keel_by = 5   # base y

    # V-bottom angle lines extending from keel
    v_angle_rad = np.radians(V_BOTTOM_ANGLE)
    v_length = 35

    # Port side hull wall
    port_outer_x = [keel_cx - keel_width / 2, keel_cx - keel_width / 2 - v_length * np.cos(v_angle_rad)]
    port_outer_y = [keel_by + keel_thick, keel_by + keel_thick + v_length * np.sin(v_angle_rad)]
    port_inner_x = [keel_cx - keel_width / 2 + wall_thick * 0.3,
                    keel_cx - keel_width / 2 - v_length * np.cos(v_angle_rad) + wall_thick * 1.1]
    port_inner_y = [keel_by + keel_thick,
                    keel_by + keel_thick + v_length * np.sin(v_angle_rad)]

    # Starboard side (mirror)
    star_outer_x = [keel_cx + keel_width / 2, keel_cx + keel_width / 2 + v_length * np.cos(v_angle_rad)]
    star_outer_y = [keel_by + keel_thick, keel_by + keel_thick + v_length * np.sin(v_angle_rad)]
    star_inner_x = [keel_cx + keel_width / 2 - wall_thick * 0.3,
                    keel_cx + keel_width / 2 + v_length * np.cos(v_angle_rad) - wall_thick * 1.1]
    star_inner_y = [keel_by + keel_thick,
                    keel_by + keel_thick + v_length * np.sin(v_angle_rad)]

    # Keel thickened block
    keel_block_pts = [
        (keel_cx - keel_width / 2, keel_by),
        (keel_cx - keel_width / 2, keel_by + keel_thick),
        (keel_cx + keel_width / 2, keel_by + keel_thick),
        (keel_cx + keel_width / 2, keel_by),
    ]
    keel_block = Polygon(keel_block_pts, closed=True,
                          facecolor='#909090', edgecolor=C_BLACK,
                          lw=1.5, zorder=3)
    ax_keel.add_patch(keel_block)

    # Inner cavity of keel (thinner at top)
    inner_keel_h = (KEEL_THICKNESS - THICKNESS) * keel_zoom_scale
    if inner_keel_h > 0:
        inner_w = keel_width * 0.6
        inner_block = Rectangle((keel_cx - inner_w / 2, keel_by),
                                 inner_w, wall_thick,
                                 facecolor=C_CONCRETE, edgecolor=C_BLACK,
                                 lw=0.8, zorder=4, alpha=0.8)
        ax_keel.add_patch(inner_block)

    # Hull walls extending from keel
    # Port wall
    port_wall = Polygon([
        (port_outer_x[0], port_outer_y[0]),
        (port_outer_x[1], port_outer_y[1]),
        (port_inner_x[1], port_inner_y[1]),
        (port_inner_x[0], port_inner_y[0]),
    ], closed=True, facecolor=C_HULL_FILL, edgecolor=C_BLACK, lw=1.2, zorder=2)
    ax_keel.add_patch(port_wall)

    # Starboard wall
    star_wall = Polygon([
        (star_outer_x[0], star_outer_y[0]),
        (star_outer_x[1], star_outer_y[1]),
        (star_inner_x[1], star_inner_y[1]),
        (star_inner_x[0], star_inner_y[0]),
    ], closed=True, facecolor=C_HULL_FILL, edgecolor=C_BLACK, lw=1.2, zorder=2)
    ax_keel.add_patch(star_wall)

    # Fiberglass mesh lines in walls
    for wall_pts in [(port_outer_x, port_outer_y), (star_outer_x, star_outer_y)]:
        # Outer mesh line
        mx = np.array(wall_pts[0])
        my = np.array(wall_pts[1])
        offset = wall_thick * 0.15
        # Shift inward slightly
        ax_keel.plot(mx, my + offset * 0.3, color=C_FIBERGLASS, lw=1.5, ls='-', zorder=5)

    # Dimensions
    # Keel thickness
    draw_dimension_v(ax_keel, keel_cx + keel_width / 2 + 8, keel_by, keel_by + keel_thick,
                     f'{KEEL_THICKNESS:.2f}"', offset=4, fontsize=7, side='right')

    # Wall thickness
    wall_dim_x = keel_cx + keel_width / 2 + v_length * np.cos(v_angle_rad) * 0.7
    wall_dim_y_bot = keel_by + keel_thick + v_length * np.sin(v_angle_rad) * 0.5
    ax_keel.annotate(f'WALL: {THICKNESS:.2f}"',
                     xy=(star_outer_x[1] * 0.6 + star_inner_x[1] * 0.4,
                         star_outer_y[1] * 0.6 + star_inner_y[1] * 0.4),
                     xytext=(keel_cx + keel_width / 2 + 20, keel_by + keel_thick + 20),
                     fontsize=6.5, fontfamily='sans-serif', fontweight='bold',
                     arrowprops=dict(arrowstyle='->', color=C_BLACK, lw=0.6),
                     bbox=dict(boxstyle='square,pad=0.15', facecolor='white',
                               edgecolor=C_LIGHT_GRAY, lw=0.5))

    # Keel width
    draw_dimension_h(ax_keel, keel_cx - keel_width / 2, keel_cx + keel_width / 2,
                     keel_by - 5, f'{6.0:.1f}"', fontsize=7)

    # V-bottom angle
    angle_arc_r = 15
    theta_arc = np.linspace(np.pi / 2, np.pi / 2 + v_angle_rad, 30)
    arc_x = keel_cx + angle_arc_r * np.cos(theta_arc)
    arc_y = keel_by + keel_thick + angle_arc_r * np.sin(theta_arc)
    ax_keel.plot(arc_x, arc_y, 'k-', lw=0.8)
    ax_keel.text(keel_cx + angle_arc_r * 0.6,
                 keel_by + keel_thick + angle_arc_r * 0.85,
                 f'{V_BOTTOM_ANGLE:.0f}\u00b0',
                 fontsize=7, fontweight='bold', fontfamily='sans-serif')

    # Labels
    ax_keel.text(keel_cx, keel_by + keel_thick / 2, "REINFORCED\nKEEL",
                 ha='center', va='center', fontsize=7, fontweight='bold',
                 fontfamily='sans-serif', color=C_WHITE,
                 bbox=dict(boxstyle='round,pad=0.2', facecolor='#606060',
                           edgecolor='none', alpha=0.8), zorder=6)

    ax_keel.set_xlim(keel_cx - 45, keel_cx + 55)
    ax_keel.set_ylim(keel_by - 10, keel_by + keel_thick + v_length * np.sin(v_angle_rad) + 10)

    ax_keel.text(0.5, 1.02, "DETAIL D: KEEL DETAIL (ENLARGED)",
                 transform=ax_keel.transAxes, ha='center', va='bottom',
                 fontsize=10, fontweight='bold', fontfamily='sans-serif')
    ax_keel.text(0.5, 0.97, f"V-BOTTOM DEADRISE: {V_BOTTOM_ANGLE}\u00b0 \u2014 NTS",
                 transform=ax_keel.transAxes, ha='center', va='bottom',
                 fontsize=7, fontfamily='sans-serif', color=C_MED_GRAY)

    # Construction notes
    ax_notes = fig.add_axes([0.05, 0.02, 0.44, 0.10], facecolor='none')
    ax_notes.axis('off')
    notes_text = (
        "CONSTRUCTION NOTES:\n"
        f"1. Hull wall thickness: {THICKNESS}\" uniform (except keel)\n"
        f"2. Keel thickness: {KEEL_THICKNESS}\" (reinforced with additional concrete + mesh)\n"
        f"3. Fiberglass mesh: 2 layers (inner and outer) throughout hull\n"
        f"4. V-bottom deadrise angle: {V_BOTTOM_ANGLE}\u00b0\n"
        f"5. Flare angle: {FLARE_ANGLE}\u00b0 at gunwale\n"
        f"6. Concrete density: 70 pcf lightweight mix\n"
        f"7. Apply release agent to mold before layup\n"
        f"8. Cure minimum 7 days before demolding"
    )
    ax_notes.text(0.02, 0.95, notes_text, transform=ax_notes.transAxes,
                  fontsize=5.5, fontfamily='sans-serif', va='top',
                  linespacing=1.4, color=C_DARK_GRAY)

    # Border and title block
    draw_engineering_border(fig)
    draw_title_block(fig, "CONSTRUCTION DETAILS", 3, scale="NTS")

    out_path = os.path.join(REPORTS_FIG_DIR, "cad_sheet3_construction_details.png")
    fig.savefig(out_path, dpi=DPI, facecolor=C_BG, edgecolor='none')
    plt.close(fig)
    print(f"    Saved: {out_path}")
    return out_path


# =============================================================================
# MAIN
# =============================================================================
def main():
    print("=" * 70)
    print("  NAU ASCE 2026 Concrete Canoe — CAD Construction Drawings")
    print(f"  Design C: {LOA}\" x {BEAM}\" x {DEPTH}\", t={THICKNESS}\"")
    print("=" * 70)

    sheets = []

    # Generate all three sheets
    sheets.append(draw_sheet1_section_breakdown())
    sheets.append(draw_sheet2_top_isometric())
    sheets.append(draw_sheet3_construction_details())

    # Copy to docs/figures/
    print("\n  Copying to docs/figures/...")
    for src in sheets:
        fname = os.path.basename(src)
        dst = os.path.join(DOCS_FIG_DIR, fname)
        shutil.copy2(src, dst)
        print(f"    Copied: {dst}")

    print("\n" + "=" * 70)
    print("  All 3 CAD sheets generated successfully!")
    print("=" * 70)

    # Print file list
    print("\n  Output files:")
    for src in sheets:
        size_kb = os.path.getsize(src) / 1024
        print(f"    {src}  ({size_kb:.0f} KB)")
    for src in sheets:
        fname = os.path.basename(src)
        dst = os.path.join(DOCS_FIG_DIR, fname)
        size_kb = os.path.getsize(dst) / 1024
        print(f"    {dst}  ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
