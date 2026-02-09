#!/usr/bin/env python3
"""
generate_shop_drawings.py - NAU ASCE Concrete Canoe 2026
=========================================================
Generates professional construction shop drawings (20 sheets) for Design A.
Female mold process, V-bottom hull with 15 deg deadrise.

Output: /root/concrete-canoe-project2026/reports/construction_drawings/*.png (300 DPI)

Usage:
    python3 generate_shop_drawings.py            # Generate all sheets (1-4)
    python3 generate_shop_drawings.py --sheet 4  # Generate only sheet 4
"""

import os
import sys
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Rectangle, Circle, Polygon, Arc, FancyBboxPatch
from matplotlib.collections import PatchCollection, LineCollection
from matplotlib.path import Path
from matplotlib import patheffects
import matplotlib.patheffects as pe
from datetime import date

# =============================================================================
# OUTPUT CONFIGURATION
# =============================================================================
OUTPUT_DIR = "/root/concrete-canoe-project2026/reports/construction_drawings"
DXF_FILE = "/root/concrete-canoe-project2026/design/dxf_coords_design_A.txt"
DPI = 300
SHEET_W_IN = 22    # ANSI D sheet width (inches) - landscape
SHEET_H_IN = 17    # ANSI D sheet height (inches) - landscape
TOTAL_SHEETS = 20

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =============================================================================
# DESIGN A - HULL PARAMETERS
# =============================================================================
HULL_LENGTH = 192.0
HULL_BEAM = 32.0
HULL_DEPTH = 17.0
WALL_THICKNESS = 0.5
DEADRISE_ANGLE = 15.0
NUM_STATIONS = 33
STATION_SPACING = 6.0
MIDSHIP_STATION = 16

# EPS Foam mold parameters
FOAM_DENSITY = 2.0
FOAM_SHEET_THICK = 4.0
FOAM_SHEET_W = 48.0
FOAM_SHEET_L = 96.0
NUM_FOAM_SHEETS = 8

# MDF Strongback
MDF_THICK = 0.75
MDF_WIDTH = 36.0
MDF_LENGTH = 192.0
SAWHORSE_HEIGHT = 36.0

# Concrete
CONCRETE_DENSITY = 60.0

# =============================================================================
# STATION DATA - half-beam and depth at each station
# =============================================================================
_STATION_HALF_BEAM_RAW = [
    0.0,   1.6,  3.1,  4.7,  6.1,  7.6,  8.9,  10.2,
    11.3,  12.4, 13.3, 14.1, 14.8, 15.3, 15.7, 15.9,
    16.0,
]

_STATION_DEPTH_RAW = [
    0.0,   3.2,  5.3,  7.3,  9.0,  10.5, 11.7, 12.8,
    13.7,  14.5, 15.1, 15.6, 16.0, 16.3, 16.5, 16.8,
    17.0,
]

STATION_HALF_BEAM = np.array(
    _STATION_HALF_BEAM_RAW + _STATION_HALF_BEAM_RAW[-2::-1], dtype=float
)
STATION_DEPTH = np.array(
    _STATION_DEPTH_RAW + _STATION_DEPTH_RAW[-2::-1], dtype=float
)
STATION_FULL_BEAM = STATION_HALF_BEAM * 2.0
STATION_POSITIONS = np.arange(NUM_STATIONS) * STATION_SPACING

# =============================================================================
# COLOR PALETTE
# =============================================================================
C_NAU_BLUE     = "#003466"
C_NAU_GOLD     = "#FFC72C"
C_DARK_GRAY    = "#2C2C2C"
C_MED_GRAY     = "#666666"
C_LIGHT_GRAY   = "#D0D0D0"
C_VERY_LIGHT   = "#F0F0F0"
C_WHITE        = "#FFFFFF"
C_CONCRETE     = "#A8A8A0"
C_FOAM_PINK    = "#F5D6C0"
C_FOAM_BEIGE   = "#F2E8D5"
C_MDF_BROWN    = "#C4A56C"
C_WATER_BLUE   = "#B8D4E8"
C_MESH_GREEN   = "#6BAF6B"
C_RED_DIM      = "#CC0000"
C_DIM_BLUE     = "#0055AA"
C_SECTION_RED  = "#DD0000"
C_HATCH_GRAY   = "#888888"
C_BG_CREAM     = "#FAFAF5"
C_BORDER       = "#003466"
C_TITLE_BG     = "#003466"
C_GRID_FAINT   = "#E0E0E0"

# =============================================================================
# DXF COORDINATE PARSER
# =============================================================================
def parse_dxf_coordinates(filepath=DXF_FILE):
    """Parse the DXF coordinate file for Design A."""
    stations = {}
    if not os.path.isfile(filepath):
        print(f"  [WARN] DXF file not found: {filepath}")
        return stations
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) < 4:
                continue
            try:
                stn = int(parts[0].strip())
                x = float(parts[2].strip())
                y = float(parts[3].strip())
                stations.setdefault(stn, []).append((x, y))
            except (ValueError, IndexError):
                continue
    return stations


DXF_COORDS = parse_dxf_coordinates()


# =============================================================================
# CROSS-SECTION GENERATOR
# =============================================================================
def get_cross_section(station_idx, n_points=60):
    """Return (xs, ys) for outer hull cross-section at a station."""
    hb = STATION_HALF_BEAM[station_idx]
    d = STATION_DEPTH[station_idx]
    if hb < 0.01:
        return np.array([0.0]), np.array([0.0])
    if station_idx in DXF_COORDS:
        pts = DXF_COORDS[station_idx]
        hull_pts = [(x, y) for (x, y) in pts if y < d + 1.0]
        if len(hull_pts) >= 3:
            hull_pts.sort(key=lambda p: p[0])
            xs = np.array([p[0] for p in hull_pts])
            ys = np.array([p[1] for p in hull_pts])
            return xs, ys
    x_half = np.linspace(0, hb, n_points // 2)
    y_half = x_half * (d / hb) if hb > 0 else x_half * 0
    xs = np.concatenate([(-x_half)[::-1], x_half[1:]])
    ys = np.concatenate([y_half[::-1], y_half[1:]])
    return xs, ys


def get_female_mold_section(station_idx, margin_w=2.0, margin_d=1.0):
    """Return female mold block dimensions and hull profile."""
    hb = STATION_HALF_BEAM[station_idx]
    d = STATION_DEPTH[station_idx]
    block_w = 2.0 * hb + 2.0 * margin_w
    block_h = d + margin_d
    xs, ys = get_cross_section(station_idx)
    return block_w, block_h, xs, ys


# =============================================================================
# HELPER: PROFESSIONAL TITLE BLOCK
# =============================================================================
def draw_title_block(fig, sheet_num, sheet_title, total_sheets=TOTAL_SHEETS):
    """Draw a professional ANSI-D style title block border on the figure."""
    margin_l = 0.03
    margin_r = 0.97
    margin_b = 0.03
    margin_t = 0.97

    border_ax = fig.add_axes([0, 0, 1, 1], facecolor="none")
    border_ax.set_xlim(0, 1)
    border_ax.set_ylim(0, 1)
    border_ax.set_axis_off()

    # Double border
    outer_rect = Rectangle((margin_l, margin_b),
                            margin_r - margin_l, margin_t - margin_b,
                            linewidth=3.0, edgecolor=C_BORDER,
                            facecolor="none", zorder=100)
    border_ax.add_patch(outer_rect)

    inner_margin = 0.005
    inner_rect = Rectangle((margin_l + inner_margin, margin_b + inner_margin),
                            (margin_r - margin_l) - 2 * inner_margin,
                            (margin_t - margin_b) - 2 * inner_margin,
                            linewidth=1.0, edgecolor=C_BORDER,
                            facecolor="none", zorder=100)
    border_ax.add_patch(inner_rect)

    # Title strip
    title_h = 0.075
    title_y = margin_b + inner_margin
    title_x = margin_l + inner_margin
    title_w = (margin_r - margin_l) - 2 * inner_margin

    title_bg = Rectangle((title_x, title_y), title_w, title_h,
                          linewidth=1.5, edgecolor=C_BORDER,
                          facecolor=C_TITLE_BG, zorder=101)
    border_ax.add_patch(title_bg)

    # Vertical dividers
    div_positions = [0.22, 0.68, 0.85]
    for dx in div_positions:
        x_pos = title_x + dx * title_w
        border_ax.plot([x_pos, x_pos], [title_y, title_y + title_h],
                       color=C_NAU_GOLD, linewidth=1.0, zorder=102)

    # Horizontal dividers in right sections
    mid_y = title_y + title_h * 0.5
    for x_start_frac, x_end_frac in [
        (div_positions[1], div_positions[2]),
        (div_positions[2], 1.0)
    ]:
        x_s = title_x + x_start_frac * title_w
        x_e = title_x + x_end_frac * title_w
        border_ax.plot([x_s, x_e], [mid_y, mid_y],
                       color=C_NAU_GOLD, linewidth=0.8, zorder=102)

    txt_kw = dict(zorder=103, fontfamily="sans-serif", verticalalignment="center")

    # Section 1: Organization (left)
    sec1_cx = title_x + 0.11 * title_w
    border_ax.text(sec1_cx, title_y + title_h * 0.72,
                   "NAU ASCE CONCRETE CANOE 2026",
                   fontsize=9, fontweight="bold", color=C_NAU_GOLD,
                   ha="center", **txt_kw)
    border_ax.text(sec1_cx, title_y + title_h * 0.45,
                   "Northern Arizona University",
                   fontsize=6.5, color=C_WHITE, ha="center", **txt_kw)
    border_ax.text(sec1_cx, title_y + title_h * 0.22,
                   "American Society of Civil Engineers",
                   fontsize=5.5, color=C_LIGHT_GRAY, ha="center", **txt_kw)

    # Section 2: Drawing Title (center)
    sec2_cx = title_x + (0.22 + 0.68) / 2.0 * title_w
    border_ax.text(sec2_cx, title_y + title_h * 0.72,
                   "DESIGN A \u2014 CONSTRUCTION DRAWINGS",
                   fontsize=8, fontweight="bold", color=C_NAU_GOLD,
                   ha="center", **txt_kw)
    border_ax.text(sec2_cx, title_y + title_h * 0.40,
                   sheet_title.upper(),
                   fontsize=10, fontweight="bold", color=C_WHITE,
                   ha="center", **txt_kw)
    border_ax.text(sec2_cx, title_y + title_h * 0.15,
                   '192" L \u00d7 32" B \u00d7 17" D  |  0.5" Wall  |  '
                   'V-Bottom 15\u00b0 Deadrise  |  33 Stations @ 6" Spacing',
                   fontsize=5, color=C_LIGHT_GRAY, ha="center", **txt_kw)

    # Section 3: Sheet number & date
    sec3_cx = title_x + (0.68 + 0.85) / 2.0 * title_w
    border_ax.text(sec3_cx, title_y + title_h * 0.75,
                   f"SHEET {sheet_num:02d} OF {total_sheets:02d}",
                   fontsize=9, fontweight="bold", color=C_NAU_GOLD,
                   ha="center", **txt_kw)
    border_ax.text(sec3_cx, title_y + title_h * 0.28,
                   f"DATE: {date.today().strftime('%Y-%m-%d')}",
                   fontsize=6, color=C_WHITE, ha="center", **txt_kw)

    # Section 4: Scale & Revision
    sec4_cx = title_x + (0.85 + 1.0) / 2.0 * title_w
    border_ax.text(sec4_cx, title_y + title_h * 0.75,
                   "REV: A",
                   fontsize=7, fontweight="bold", color=C_NAU_GOLD,
                   ha="center", **txt_kw)
    border_ax.text(sec4_cx, title_y + title_h * 0.28,
                   "SCALE: AS NOTED",
                   fontsize=5.5, color=C_WHITE, ha="center", **txt_kw)

    # Fold marks
    for fx in [0.25, 0.50, 0.75]:
        border_ax.plot(fx, margin_b - 0.005, marker="^", markersize=3,
                       color=C_MED_GRAY, zorder=100)
        border_ax.plot(fx, margin_t + 0.005, marker="v", markersize=3,
                       color=C_MED_GRAY, zorder=100)

    return border_ax


# =============================================================================
# HELPER: DIMENSION LINE
# =============================================================================
def draw_dimension_line(ax, p1, p2, text, offset=0.0, color=C_DIM_BLUE,
                        fontsize=7, text_offset=0.0, horizontal=None,
                        flip_text=False, linewidth=0.7, arrowstyle="<->",
                        extension_lines=True, ext_len=None):
    """Draw a professional dimension line from p1 to p2, with centered text."""
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux

    ox1 = x1 + nx * offset
    oy1 = y1 + ny * offset
    ox2 = x2 + nx * offset
    oy2 = y2 + ny * offset

    ax.annotate("", xy=(ox2, oy2), xytext=(ox1, oy1),
                arrowprops=dict(arrowstyle=arrowstyle, color=color,
                                lw=linewidth, shrinkA=0, shrinkB=0),
                zorder=50)

    if extension_lines and abs(offset) > 0.1:
        gap = 0.05 * abs(offset) if abs(offset) > 1 else 0.05
        overshoot = ext_len if ext_len is not None else 0.12 * abs(offset)
        sign = 1.0 if offset >= 0 else -1.0
        for (fx, fy), (ox, oy) in [((x1, y1), (ox1, oy1)),
                                     ((x2, y2), (ox2, oy2))]:
            ex_start_x = fx + nx * gap * sign
            ex_start_y = fy + ny * gap * sign
            ex_end_x = ox + nx * overshoot * sign
            ex_end_y = oy + ny * overshoot * sign
            ax.plot([ex_start_x, ex_end_x], [ex_start_y, ex_end_y],
                    color=color, linewidth=linewidth * 0.6, zorder=49, linestyle="-")

    tcx = (ox1 + ox2) / 2.0
    tcy = (oy1 + oy2) / 2.0
    t_shift = fontsize * 0.015 + abs(text_offset)
    if flip_text:
        t_shift = -t_shift
    tcx += nx * t_shift
    tcy += ny * t_shift

    angle = math.degrees(math.atan2(dy, dx))
    if horizontal is True:
        angle = 0
    elif horizontal is not False:
        if angle > 90:
            angle -= 180
        elif angle < -90:
            angle += 180

    ax.text(tcx, tcy, text, fontsize=fontsize, color=color,
            ha="center", va="center", rotation=angle,
            fontweight="bold", fontfamily="sans-serif",
            bbox=dict(boxstyle="round,pad=0.1", facecolor=C_WHITE,
                      edgecolor="none", alpha=0.85),
            zorder=51)


# =============================================================================
# HELPER: SECTION CUT SYMBOL
# =============================================================================
def draw_section_cut_symbol(ax, x, y, label, radius=0.8, color=C_SECTION_RED,
                            fontsize=8, direction="down"):
    """Draw an A-A style section cut circle with direction arrow."""
    circle = Circle((x, y), radius, linewidth=1.8, edgecolor=color,
                     facecolor=C_WHITE, zorder=60)
    ax.add_patch(circle)
    ax.plot([x - radius, x + radius], [y, y],
            color=color, linewidth=1.2, zorder=61)
    ax.text(x, y + radius * 0.35, label, fontsize=fontsize,
            fontweight="bold", color=color, ha="center", va="center",
            zorder=62, fontfamily="sans-serif")
    ax.text(x, y - radius * 0.35, label, fontsize=fontsize,
            fontweight="bold", color=color, ha="center", va="center",
            zorder=62, fontfamily="sans-serif")
    arrow_len = radius * 1.5
    dir_map = {"down": (0, -1), "up": (0, 1),
               "left": (-1, 0), "right": (1, 0)}
    adx, ady = dir_map.get(direction, (0, -1))
    ax.annotate("", xy=(x + adx * (radius + arrow_len),
                        y + ady * (radius + arrow_len)),
                xytext=(x + adx * radius, y + ady * radius),
                arrowprops=dict(arrowstyle="-|>", color=color,
                                lw=1.5, shrinkA=0, shrinkB=0),
                zorder=61)


# =============================================================================
# HELPER: HATCHING PATTERNS
# =============================================================================
def draw_hatch_diagonal(ax, x0, y0, w, h, spacing=0.4, angle=45,
                        color=C_HATCH_GRAY, linewidth=0.3, zorder=5):
    """Draw diagonal line hatching in a rectangular region (for concrete)."""
    rad = math.radians(angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    diag = math.hypot(w, h)
    n_lines = int(2 * diag / spacing) + 2
    lines = []
    for i in range(n_lines):
        d_val = -diag + i * spacing
        pts = []
        for t in np.linspace(-diag, diag, 200):
            px = x0 + w / 2.0 + t * cos_a + d_val * sin_a
            py = y0 + h / 2.0 + t * sin_a - d_val * cos_a
            if x0 <= px <= x0 + w and y0 <= py <= y0 + h:
                pts.append((px, py))
        if len(pts) >= 2:
            lines.append([pts[0], pts[-1]])
    if lines:
        lc = LineCollection(lines, colors=color, linewidths=linewidth, zorder=zorder)
        ax.add_collection(lc)


def draw_hatch_dots(ax, x0, y0, w, h, spacing=0.5,
                    color=C_FOAM_PINK, size=0.5, zorder=5):
    """Draw dot-pattern fill (for foam)."""
    xs = np.arange(x0 + spacing / 2, x0 + w, spacing)
    ys = np.arange(y0 + spacing / 2, y0 + h, spacing)
    for i, xi in enumerate(xs):
        offset_y = spacing / 2.0 if i % 2 else 0
        for yj in ys:
            yy = yj + offset_y
            if y0 <= yy <= y0 + h:
                ax.plot(xi, yy, ".", color=color, markersize=size, zorder=zorder)


def draw_hatch_crosshatch(ax, x0, y0, w, h, spacing=0.6,
                          color=C_MESH_GREEN, linewidth=0.3, zorder=5):
    """Draw crosshatch pattern (for mesh reinforcement)."""
    draw_hatch_diagonal(ax, x0, y0, w, h, spacing, angle=45,
                        color=color, linewidth=linewidth, zorder=zorder)
    draw_hatch_diagonal(ax, x0, y0, w, h, spacing, angle=-45,
                        color=color, linewidth=linewidth, zorder=zorder)


# =============================================================================
# HELPER: LEADER LINE WITH NOTE
# =============================================================================
def draw_leader(ax, point, text_pos, text, color=C_DARK_GRAY, fontsize=6,
                arrowstyle="-|>", linewidth=0.7, ha="left", va="center",
                bbox_color=C_WHITE):
    """Draw a leader line from a point to a text annotation."""
    ax.annotate(text, xy=point, xytext=text_pos,
                fontsize=fontsize, color=color, fontweight="normal",
                fontfamily="sans-serif", ha=ha, va=va,
                arrowprops=dict(arrowstyle=arrowstyle, color=color,
                                lw=linewidth, connectionstyle="arc3,rad=0.1"),
                bbox=dict(boxstyle="round,pad=0.15", facecolor=bbox_color,
                          edgecolor=color, linewidth=0.4, alpha=0.9),
                zorder=55)


# =============================================================================
# HELPER: SCALE BAR
# =============================================================================
def draw_scale_bar(ax, x, y, length, label, color=C_DARK_GRAY, fontsize=5):
    """Draw a graphic scale bar."""
    bar_h = length * 0.05
    n_blocks = 4
    block_w = length / n_blocks
    for i in range(n_blocks):
        fc = C_DARK_GRAY if i % 2 == 0 else C_WHITE
        rect = Rectangle((x + i * block_w, y), block_w, bar_h,
                          facecolor=fc, edgecolor=C_DARK_GRAY, linewidth=0.5)
        ax.add_patch(rect)
    ax.text(x, y - bar_h * 0.6, "0", fontsize=fontsize - 1, ha="center",
            va="top", color=color, fontfamily="sans-serif")
    ax.text(x + length, y - bar_h * 0.6, label, fontsize=fontsize - 1,
            ha="center", va="top", color=color, fontfamily="sans-serif")
    ax.text(x + length / 2, y + bar_h * 1.5, f'SCALE: {label}',
            fontsize=fontsize, ha="center", va="bottom", color=color,
            fontweight="bold", fontfamily="sans-serif")


# =============================================================================
# HELPER: CREATE / SAVE SHEET
# =============================================================================
def create_sheet(sheet_num, sheet_title):
    """Create a new figure with title block, return (fig, content_ax)."""
    fig = plt.figure(figsize=(SHEET_W_IN, SHEET_H_IN), dpi=DPI, facecolor=C_WHITE)
    draw_title_block(fig, sheet_num, sheet_title)
    content_ax = fig.add_axes([0.05, 0.13, 0.90, 0.82], facecolor=C_BG_CREAM)
    content_ax.set_aspect("equal", adjustable="datalim")
    return fig, content_ax


def save_sheet(fig, sheet_num, name_suffix=""):
    """Save figure as high-res PNG."""
    fname = f"Sheet_{sheet_num:02d}{name_suffix}.png"
    fpath = os.path.join(OUTPUT_DIR, fname)
    fig.savefig(fpath, dpi=DPI, bbox_inches="tight",
                facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"  [OK] Saved: {fpath}")
    return fpath


# #############################################################################
#
#  SHEET 1: TITLE SHEET
#
# #############################################################################
def sheet_01_title():
    """Generate Sheet 01 - Professional title page with drawing index."""
    print("Generating Sheet 01: Title Sheet...")
    fig = plt.figure(figsize=(SHEET_W_IN, SHEET_H_IN), dpi=DPI, facecolor=C_WHITE)
    draw_title_block(fig, 1, "Title Sheet & Drawing Index")

    ax = fig.add_axes([0.05, 0.13, 0.90, 0.82], facecolor=C_BG_CREAM)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 80)
    ax.set_axis_off()

    # ---- LARGE PROJECT TITLE ----
    ax.text(50, 74, "NAU ASCE CONCRETE CANOE 2026",
            fontsize=28, fontweight="bold", color=C_NAU_BLUE,
            ha="center", va="center", fontfamily="sans-serif")

    # Gold accent lines
    ax.plot([15, 85], [71.5, 71.5], color=C_NAU_GOLD, linewidth=3, zorder=10)
    ax.plot([15, 85], [71.0, 71.0], color=C_NAU_BLUE, linewidth=1, zorder=10)

    ax.text(50, 68.5, "DESIGN A \u2014 CONSTRUCTION SHOP DRAWINGS",
            fontsize=18, fontweight="bold", color=C_NAU_GOLD,
            ha="center", va="center", fontfamily="sans-serif")
    ax.text(50, 65.5, "Female Mold Process  |  V-Bottom Hull  |  15\u00b0 Deadrise",
            fontsize=11, color=C_MED_GRAY, ha="center", va="center",
            fontfamily="sans-serif")

    # ---- KEY SPECIFICATIONS TABLE (left) ----
    spec_x = 8
    spec_y = 60
    spec_w = 38
    spec_h = 32

    spec_bg = Rectangle((spec_x, spec_y - spec_h), spec_w, spec_h,
                         facecolor=C_WHITE, edgecolor=C_NAU_BLUE,
                         linewidth=1.5, zorder=5)
    ax.add_patch(spec_bg)

    hdr_rect = Rectangle((spec_x, spec_y - 3.5), spec_w, 3.5,
                          facecolor=C_NAU_BLUE, edgecolor=C_NAU_BLUE,
                          linewidth=1.5, zorder=6)
    ax.add_patch(hdr_rect)
    ax.text(spec_x + spec_w / 2, spec_y - 1.75,
            "KEY SPECIFICATIONS", fontsize=10, fontweight="bold",
            color=C_NAU_GOLD, ha="center", va="center", zorder=7,
            fontfamily="sans-serif")

    specs = [
        ("Hull Length", '192" (16\'-0")'),
        ("Maximum Beam", '32" (2\'-8")'),
        ("Maximum Depth", '17"'),
        ("Wall Thickness", '0.5" (nominal)'),
        ("Hull Form", "V-Bottom, 15\u00b0 Deadrise"),
        ("Number of Stations", '33 (0-32) @ 6" spacing'),
        ("Midship Station", "Station 16"),
        ("Symmetry", "Bow-to-Stern (Stn 0 = Stn 32)"),
        ("Concrete Density", "60 PCF (target)"),
        ("Reinforcement", "Basalt mesh + PVA fibers"),
        ("Mold Material", "EPS foam (2 lb/ft\u00b3)"),
        ("Strongback", '3/4" MDF, 36" \u00d7 192"'),
    ]

    row_h = (spec_h - 3.5) / len(specs)
    for i, (param, value) in enumerate(specs):
        ry = spec_y - 3.5 - i * row_h
        if i % 2 == 0:
            row_bg = Rectangle((spec_x, ry - row_h), spec_w, row_h,
                                facecolor=C_VERY_LIGHT, edgecolor="none", zorder=5)
            ax.add_patch(row_bg)
        ax.plot([spec_x, spec_x + spec_w], [ry, ry],
                color=C_LIGHT_GRAY, linewidth=0.3, zorder=6)
        div_x = spec_x + 18
        ax.plot([div_x, div_x], [ry, ry - row_h],
                color=C_LIGHT_GRAY, linewidth=0.3, zorder=6)
        ax.text(spec_x + 1.5, ry - row_h / 2, param,
                fontsize=6.5, color=C_DARK_GRAY, ha="left", va="center",
                fontfamily="sans-serif", fontweight="bold", zorder=7)
        ax.text(div_x + 1.5, ry - row_h / 2, value,
                fontsize=6.5, color=C_MED_GRAY, ha="left", va="center",
                fontfamily="sans-serif", zorder=7)

    # ---- DRAWING INDEX TABLE (right) ----
    idx_x = 54
    idx_y = 60
    idx_w = 40
    idx_h = 50

    idx_bg = Rectangle((idx_x, idx_y - idx_h), idx_w, idx_h,
                        facecolor=C_WHITE, edgecolor=C_NAU_BLUE,
                        linewidth=1.5, zorder=5)
    ax.add_patch(idx_bg)

    idx_hdr = Rectangle((idx_x, idx_y - 3.5), idx_w, 3.5,
                         facecolor=C_NAU_BLUE, edgecolor=C_NAU_BLUE,
                         linewidth=1.5, zorder=6)
    ax.add_patch(idx_hdr)
    ax.text(idx_x + idx_w / 2, idx_y - 1.75,
            "DRAWING INDEX", fontsize=10, fontweight="bold",
            color=C_NAU_GOLD, ha="center", va="center", zorder=7,
            fontfamily="sans-serif")

    drawings = [
        ("01", "Title Sheet & Drawing Index"),
        ("02", "Bill of Materials"),
        ("03", "Strongback Assembly"),
        ("04", "Foam Nesting Layout"),
        ("05", "Station Templates (Bow: 0-8)"),
        ("06", "Station Templates (Mid: 9-16)"),
        ("07", "Station Templates (Stern: 17-24)"),
        ("08", "Station Templates (Stern: 25-32)"),
        ("09", "Mold Assembly - Exploded View"),
        ("10", "Mold Assembly - Plan & Elevation"),
        ("11", "Mold Fairing & Surface Prep"),
        ("12", "Reinforcement Layout - Basalt Mesh"),
        ("13", "Reinforcement Layout - PVA Fibers"),
        ("14", "Concrete Placement Sequence"),
        ("15", "Curing & Demolding Procedure"),
        ("16", "Hull Lines Drawing - Plan View"),
        ("17", "Hull Lines Drawing - Profile"),
        ("18", "Hull Lines Drawing - Body Plan"),
        ("19", "Finishing & Paint Schedule"),
        ("20", "Quality Control Checklist"),
    ]

    row_h_idx = (idx_h - 3.5) / len(drawings)
    for i, (num, title) in enumerate(drawings):
        ry = idx_y - 3.5 - i * row_h_idx
        if i % 2 == 0:
            row_bg = Rectangle((idx_x, ry - row_h_idx), idx_w, row_h_idx,
                                facecolor=C_VERY_LIGHT, edgecolor="none", zorder=5)
            ax.add_patch(row_bg)
        ax.plot([idx_x, idx_x + idx_w], [ry, ry],
                color=C_LIGHT_GRAY, linewidth=0.3, zorder=6)
        num_col_w = 6
        ax.plot([idx_x + num_col_w, idx_x + num_col_w], [ry, ry - row_h_idx],
                color=C_LIGHT_GRAY, linewidth=0.3, zorder=6)
        ax.text(idx_x + num_col_w / 2, ry - row_h_idx / 2,
                f"SH-{num}", fontsize=6, fontweight="bold",
                color=C_NAU_BLUE, ha="center", va="center",
                fontfamily="sans-serif", zorder=7)
        ax.text(idx_x + num_col_w + 1.5, ry - row_h_idx / 2,
                title, fontsize=6, color=C_DARK_GRAY,
                ha="left", va="center", fontfamily="sans-serif", zorder=7)

    # ---- GENERAL NOTES ----
    note_x = 8
    note_y = 25
    notes_title_rect = Rectangle((note_x, note_y - 2.5), 38, 2.5,
                                  facecolor=C_NAU_BLUE, edgecolor=C_NAU_BLUE,
                                  linewidth=1, zorder=5)
    ax.add_patch(notes_title_rect)
    ax.text(note_x + 19, note_y - 1.25, "GENERAL NOTES",
            fontsize=8, fontweight="bold", color=C_NAU_GOLD,
            ha="center", va="center", zorder=6, fontfamily="sans-serif")

    general_notes = [
        "1.  ALL DIMENSIONS ARE IN INCHES UNLESS OTHERWISE NOTED.",
        "2.  CONCRETE DENSITY: 60 PCF (TARGET), LIGHTWEIGHT MIX DESIGN.",
        '3.  WALL THICKNESS: 0.5" NOMINAL, TOLERANCE \u00b10.0625".',
        "4.  EPS FOAM: 2 LB/FT\u00b3 EXPANDED POLYSTYRENE.",
        "5.  MOLD ORIENTATION: FEMALE (HULL INVERTED, LAYUP ON INSIDE).",
        "6.  ALL STATION CROSS-SECTIONS ARE SYMMETRIC ABOUT CENTERLINE.",
        "7.  BOW (STN 0) AND STERN (STN 32) ARE IDENTICAL (SYMMETRIC HULL).",
        "8.  REINFORCEMENT: SINGLE LAYER BASALT MESH + PVA FIBERS IN MIX.",
        "9.  DO NOT SCALE DRAWINGS - USE FIGURED DIMENSIONS ONLY.",
        "10. REFER TO MIX DESIGN REPORT FOR CONCRETE PROPORTIONS.",
    ]

    notes_bg = Rectangle((note_x, note_y - 2.5 - len(general_notes) * 1.6),
                          38, len(general_notes) * 1.6,
                          facecolor=C_WHITE, edgecolor=C_NAU_BLUE,
                          linewidth=1, zorder=4)
    ax.add_patch(notes_bg)

    for i, note in enumerate(general_notes):
        ny = note_y - 2.5 - (i + 0.5) * 1.6
        ax.text(note_x + 1.5, ny, note, fontsize=5.2, color=C_DARK_GRAY,
                ha="left", va="center", fontfamily="sans-serif", zorder=6)

    # ---- HULL PROFILE SILHOUETTE (decorative) ----
    profile_cx = 50
    profile_cy = 5
    profile_scale = 0.12

    px = STATION_POSITIONS * profile_scale + (profile_cx - 96 * profile_scale)
    py_sheer = STATION_DEPTH * profile_scale + profile_cy
    py_keel = np.zeros_like(px) + profile_cy

    hull_xs = np.concatenate([px, px[::-1]])
    hull_ys = np.concatenate([py_keel, py_sheer[::-1]])
    hull_poly = Polygon(np.column_stack([hull_xs, hull_ys]),
                        closed=True, facecolor=C_NAU_BLUE, edgecolor=C_NAU_BLUE,
                        linewidth=1, alpha=0.3, zorder=3)
    ax.add_patch(hull_poly)
    ax.plot(px, py_sheer, color=C_NAU_BLUE, linewidth=1.2, zorder=4)
    ax.plot(px, py_keel, color=C_NAU_BLUE, linewidth=1.2, zorder=4)

    ax.text(profile_cx, profile_cy - 1.5, "DESIGN A PROFILE (NTS)",
            fontsize=5, color=C_MED_GRAY, ha="center", va="center",
            fontfamily="sans-serif", fontstyle="italic")

    save_sheet(fig, 1, "_Title_Sheet")


# #############################################################################
#
#  SHEET 2: BILL OF MATERIALS
#
# #############################################################################
def sheet_02_bom():
    """Generate Sheet 02 - Complete Bill of Materials."""
    print("Generating Sheet 02: Bill of Materials...")
    fig = plt.figure(figsize=(SHEET_W_IN, SHEET_H_IN), dpi=DPI, facecolor=C_WHITE)
    draw_title_block(fig, 2, "Bill of Materials")

    ax = fig.add_axes([0.04, 0.12, 0.92, 0.84], facecolor=C_BG_CREAM)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 80)
    ax.set_axis_off()

    # Column layout: Item#, Description, Qty, Size/Spec, Vendor, Unit$, Total$
    col_x = [2, 8, 48, 54, 68, 80, 88, 98]
    col_labels = ["ITEM", "DESCRIPTION", "QTY", "SIZE / SPECIFICATION",
                  "VENDOR", "UNIT $", "TOTAL $"]
    col_centers = [(col_x[i] + col_x[i + 1]) / 2 for i in range(len(col_labels))]

    table_top = 76
    header_h = 3.0
    row_h = 2.2
    section_h = 2.8

    # Sheet title
    ax.text(50, 78.5, "BILL OF MATERIALS \u2014 DESIGN A CONSTRUCTION",
            fontsize=14, fontweight="bold", color=C_NAU_BLUE,
            ha="center", va="center", fontfamily="sans-serif")

    # Column headers
    hdr_rect = Rectangle((col_x[0], table_top - header_h),
                          col_x[-1] - col_x[0], header_h,
                          facecolor=C_NAU_BLUE, edgecolor=C_NAU_BLUE,
                          linewidth=1.2, zorder=5)
    ax.add_patch(hdr_rect)

    for i, label in enumerate(col_labels):
        ax.text(col_centers[i], table_top - header_h / 2, label,
                fontsize=5.5, fontweight="bold", color=C_NAU_GOLD,
                ha="center", va="center", fontfamily="sans-serif", zorder=6)

    def draw_table_grid(y_top, y_bottom):
        for cx in col_x:
            ax.plot([cx, cx], [y_top, y_bottom], color=C_LIGHT_GRAY,
                    linewidth=0.4, zorder=4)

    # BOM data organized by section
    bom_sections = {
        "A. MOLD MATERIALS": [
            ("A1", "EPS Foam Sheets (2 lb/ft\u00b3)", "8", '4" \u00d7 48" \u00d7 96"', "Insulfoam", "$42.00", "$336.00"),
            ("A2", "MDF Sheet (Strongback)", "1", '3/4" \u00d7 36" \u00d7 192"', "Home Depot", "$65.00", "$65.00"),
            ("A3", "Gorilla Glue (Foam Adhesive)", "4", "18 oz bottle", "Gorilla", "$8.50", "$34.00"),
            ("A4", "PVA Mold Release Agent", "2", "1 quart", "Partall", "$18.00", "$36.00"),
            ("A5", "Sandpaper Assortment", "1", "80/120/220 grit pack", "3M", "$24.00", "$24.00"),
            ("A6", "Drywall Screws (Alignment)", "1", '#8 \u00d7 2", 100-pk', "GRK", "$8.00", "$8.00"),
            ("A7", "Shims & Leveling Wedges", "2", "8-pk composite", "Nelson", "$6.00", "$12.00"),
            ("A8", "Plastic Sheeting (Mold Wrap)", "1", '6 mil, 10\' \u00d7 25\'', "Husky", "$15.00", "$15.00"),
        ],
        "B. CONCRETE & REINFORCEMENT": [
            ("B1", "Portland Cement Type I/II", "60", "lb (1 bag)", "Quikrete", "$12.00", "$12.00"),
            ("B2", "Poraver Expanded Glass", "40", "lb (0.25-0.5mm grade)", "Poraver", "$45.00", "$45.00"),
            ("B3", "Class F Fly Ash", "15", "lb", "Boral", "$8.00", "$8.00"),
            ("B4", "Silica Fume (Densified)", "8", "lb", "Norchem", "$12.00", "$12.00"),
            ("B5", "Basalt Fiber Mesh", "3", "yd\u00b2 (4mm grid)", "Sudaglass", "$28.00", "$84.00"),
            ("B6", "PVA Fibers (3/4\" chopped)", "2", "lb", "Nycon", "$18.00", "$36.00"),
            ("B7", "HRWR Admixture (Superplast.)", "1", "1 quart", "Fritz-Pak", "$22.00", "$22.00"),
            ("B8", "Air Entrainer", "1", "8 oz", "Fritz-Pak", "$15.00", "$15.00"),
            ("B9", "Concrete Sealer (Penetrating)", "1", "1 quart", "Aqua-X", "$32.00", "$32.00"),
            ("B10", "Latex Paint (NAU Blue/Gold)", "2", "1 quart each", "Sherwin-Williams", "$16.00", "$32.00"),
        ],
        "C. TOOLS & EQUIPMENT": [
            ("C1", "Margin Trowels (Assorted)", "4", '3",4",6" widths', "Marshalltown", "$9.00", "$36.00"),
            ("C2", "Mixing Buckets (5 gal)", "4", "5-gallon", "Homer", "$4.00", "$16.00"),
            ("C3", "Orbital Sander", "1", '5" random orbit', "DEWALT", "$65.00", "$65.00"),
            ("C4", "Hot Wire Foam Cutter", "1", '4\' bow type', "Proxxon", "$85.00", "$85.00"),
            ("C5", "Spray Bottles", "4", "32 oz", "Generic", "$3.00", "$12.00"),
            ("C6", "Mixing Drill + Paddle", "1", '1/2" drill w/ paddle', "Milwaukee", "$0.00", "OWNED"),
            ("C7", "Levels (2\' and 4\')", "2", "Aluminum", "Stanley", "$0.00", "OWNED"),
            ("C8", "Tape Measures", "3", '25\' steel', "Stanley", "$0.00", "OWNED"),
            ("C9", "Safety Equipment (PPE)", "1", "Kit: goggles, gloves, masks", "3M", "$35.00", "$35.00"),
            ("C10", "Curing Blankets (Burlap)", "2", '3\' \u00d7 12\' rolls', "Mutual Ind.", "$12.00", "$24.00"),
        ],
    }

    current_y = table_top - header_h
    all_rows_bottom = current_y

    for section_name, items in bom_sections.items():
        # Section header
        sec_rect = Rectangle((col_x[0], current_y - section_h),
                              col_x[-1] - col_x[0], section_h,
                              facecolor="#E8E0D0", edgecolor=C_MED_GRAY,
                              linewidth=0.5, zorder=5)
        ax.add_patch(sec_rect)
        ax.text(col_x[0] + 2, current_y - section_h / 2,
                section_name, fontsize=7, fontweight="bold",
                color=C_NAU_BLUE, ha="left", va="center",
                fontfamily="sans-serif", zorder=6)
        current_y -= section_h

        for row_idx, (item, desc, qty, size, vendor, unit_c, total_c) in enumerate(items):
            ry = current_y - row_h
            if row_idx % 2 == 0:
                row_bg = Rectangle((col_x[0], ry), col_x[-1] - col_x[0], row_h,
                                    facecolor=C_VERY_LIGHT, edgecolor="none", zorder=3)
                ax.add_patch(row_bg)
            ax.plot([col_x[0], col_x[-1]], [ry, ry],
                    color=C_LIGHT_GRAY, linewidth=0.2, zorder=4)

            row_data = [item, desc, qty, size, vendor, unit_c, total_c]
            aligns = ["center", "left", "center", "left", "center", "right", "right"]
            x_offsets = [0, 1.0, 0, 0.5, 0, -0.5, -0.5]
            for ci, (txt, align, x_off) in enumerate(zip(row_data, aligns, x_offsets)):
                if align == "left":
                    tx = col_x[ci] + 0.8 + x_off
                elif align == "right":
                    tx = col_x[ci + 1] - 0.8 + x_off
                else:
                    tx = col_centers[ci] + x_off
                ax.text(tx, ry + row_h / 2, txt,
                        fontsize=4.8, color=C_DARK_GRAY,
                        ha=align, va="center", fontfamily="sans-serif", zorder=6)
            current_y = ry
        all_rows_bottom = current_y

    # Grand total row
    total_h = 3.0
    total_rect = Rectangle((col_x[0], all_rows_bottom - total_h),
                            col_x[-1] - col_x[0], total_h,
                            facecolor=C_NAU_BLUE, edgecolor=C_NAU_BLUE,
                            linewidth=1.2, zorder=5)
    ax.add_patch(total_rect)
    ax.text(col_centers[3], all_rows_bottom - total_h / 2,
            "ESTIMATED GRAND TOTAL", fontsize=8, fontweight="bold",
            color=C_NAU_GOLD, ha="center", va="center",
            fontfamily="sans-serif", zorder=6)
    ax.text(col_x[-1] - 1.5, all_rows_bottom - total_h / 2,
            "$1,131.00", fontsize=9, fontweight="bold",
            color=C_NAU_GOLD, ha="right", va="center",
            fontfamily="sans-serif", zorder=6)

    draw_table_grid(table_top, all_rows_bottom - total_h)

    # Notes
    note_y = all_rows_bottom - total_h - 2.5
    ax.text(col_x[0] + 1, note_y, "NOTES:", fontsize=5.5, fontweight="bold",
            color=C_NAU_BLUE, ha="left", va="top", fontfamily="sans-serif")
    bom_notes = [
        'Items marked "OWNED" are existing tools - no additional cost.',
        "Quantities include 10-15% waste/contingency factor.",
        "Prices based on Feb 2026 estimates; confirm before purchasing.",
        "Concrete mix proportions per separate Mix Design Report (Appendix B).",
        'EPS foam quantity accounts for lamination to achieve 8" block thickness.',
    ]
    for i, note in enumerate(bom_notes):
        ax.text(col_x[0] + 3, note_y - (i + 1) * 1.4,
                f"{i+1}. {note}", fontsize=4.5, color=C_MED_GRAY,
                ha="left", va="top", fontfamily="sans-serif")

    save_sheet(fig, 2, "_Bill_of_Materials")


# #############################################################################
#
#  SHEET 3: STRONGBACK ASSEMBLY
#
# #############################################################################
def sheet_03_strongback():
    """Generate Sheet 03 - Strongback Assembly (plan + elevation + detail)."""
    print("Generating Sheet 03: Strongback Assembly...")
    fig = plt.figure(figsize=(SHEET_W_IN, SHEET_H_IN), dpi=DPI, facecolor=C_WHITE)
    draw_title_block(fig, 3, "Strongback Assembly")

    # ========== TOP VIEW (PLAN) ==========
    ax_plan = fig.add_axes([0.06, 0.55, 0.88, 0.38], facecolor=C_BG_CREAM)
    ax_plan.set_xlim(-15, 210)
    ax_plan.set_ylim(-12, 30)
    ax_plan.set_aspect("equal")
    ax_plan.set_axis_off()

    ax_plan.text(-10, 27, "TOP VIEW (PLAN)", fontsize=10, fontweight="bold",
                 color=C_NAU_BLUE, ha="left", va="center", fontfamily="sans-serif",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor=C_WHITE,
                           edgecolor=C_NAU_BLUE, linewidth=1.0))
    ax_plan.text(-10, 24.5, 'SCALE: 1" = 12" (1:12)', fontsize=6,
                 color=C_MED_GRAY, ha="left", va="center", fontfamily="sans-serif")

    # MDF Board outline
    mdf_y0 = -MDF_WIDTH / 2
    mdf_y1 = MDF_WIDTH / 2
    mdf_rect = Rectangle((0, mdf_y0), MDF_LENGTH, MDF_WIDTH,
                          facecolor=C_MDF_BROWN, edgecolor=C_DARK_GRAY,
                          linewidth=1.5, alpha=0.4, zorder=3)
    ax_plan.add_patch(mdf_rect)

    # Wood grain hatching
    for gy in np.arange(mdf_y0 + 1, mdf_y1, 2.5):
        ax_plan.plot([0, MDF_LENGTH], [gy, gy], color=C_MDF_BROWN,
                     linewidth=0.3, alpha=0.5, zorder=4)

    # Centerline
    ax_plan.plot([0, MDF_LENGTH], [0, 0], color=C_SECTION_RED,
                 linewidth=0.8, linestyle=(0, (15, 5, 3, 5)), zorder=10)
    ax_plan.text(MDF_LENGTH + 2, 0, "CL", fontsize=7, fontweight="bold",
                 color=C_SECTION_RED, ha="left", va="center", fontfamily="sans-serif")
    ax_plan.plot([MDF_LENGTH + 1, MDF_LENGTH + 1], [-1.0, 1.0],
                 color=C_SECTION_RED, linewidth=0.8, zorder=10)

    # Station marks
    for i in range(NUM_STATIONS):
        sx = i * STATION_SPACING
        line_style = "-" if i == MIDSHIP_STATION else "--"
        lw = 1.2 if i == MIDSHIP_STATION else 0.4
        clr = C_NAU_BLUE if i == MIDSHIP_STATION else C_MED_GRAY
        ax_plan.plot([sx, sx], [mdf_y0, mdf_y1], color=clr,
                     linewidth=lw, linestyle=line_style, zorder=5)
        if i % 4 == 0 or i == MIDSHIP_STATION or i == NUM_STATIONS - 1:
            ax_plan.text(sx, mdf_y1 + 1.5, f"S{i}", fontsize=5,
                         fontweight="bold", color=C_NAU_BLUE,
                         ha="center", va="bottom", fontfamily="sans-serif", zorder=10)

    # Midship callout
    ms_x = MIDSHIP_STATION * STATION_SPACING
    draw_leader(ax_plan, (ms_x, mdf_y1), (ms_x + 15, mdf_y1 + 7),
                "MIDSHIP\nSTATION 16", color=C_NAU_BLUE, fontsize=6)

    # Dimension lines
    draw_dimension_line(ax_plan, (0, mdf_y0), (MDF_LENGTH, mdf_y0),
                        '192"  (16\'-0")', offset=-5, color=C_DIM_BLUE, fontsize=7)
    draw_dimension_line(ax_plan, (MDF_LENGTH, mdf_y0), (MDF_LENGTH, mdf_y1),
                        '36"', offset=6, color=C_DIM_BLUE, fontsize=7)
    draw_dimension_line(ax_plan, (0, mdf_y1), (STATION_SPACING, mdf_y1),
                        '6" TYP.', offset=4, color=C_RED_DIM, fontsize=6)

    # Section cut symbol
    draw_section_cut_symbol(ax_plan, ms_x, mdf_y0 - 7, "A", radius=1.5, direction="up")

    # ========== SIDE VIEW (ELEVATION) ==========
    ax_elev = fig.add_axes([0.06, 0.26, 0.88, 0.28], facecolor=C_BG_CREAM)
    ax_elev.set_xlim(-15, 210)
    ax_elev.set_ylim(-5, 50)
    ax_elev.set_aspect("equal")
    ax_elev.set_axis_off()

    ax_elev.text(-10, 47, "SIDE VIEW (ELEVATION)", fontsize=10, fontweight="bold",
                 color=C_NAU_BLUE, ha="left", va="center", fontfamily="sans-serif",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor=C_WHITE,
                           edgecolor=C_NAU_BLUE, linewidth=1.0))
    ax_elev.text(-10, 44, 'SCALE: 1" = 12" (1:12)', fontsize=6,
                 color=C_MED_GRAY, ha="left", va="center", fontfamily="sans-serif")

    # Floor line
    ax_elev.plot([-10, 200], [0, 0], color=C_DARK_GRAY, linewidth=0.5,
                 linestyle="-.", zorder=2)
    ax_elev.text(200, -1.5, "FLOOR", fontsize=5, color=C_MED_GRAY,
                 ha="right", va="top", fontfamily="sans-serif")

    # 4 Sawhorses
    sawhorse_positions = [24, 72, 120, 168]
    sh_top = SAWHORSE_HEIGHT
    sh_leg_spread = 18
    sh_top_w = 24

    for sx in sawhorse_positions:
        ax_elev.plot([sx - sh_leg_spread / 2, sx - sh_top_w / 4],
                     [0, sh_top], color=C_DARK_GRAY, linewidth=1.5, zorder=5)
        ax_elev.plot([sx + sh_leg_spread / 2, sx + sh_top_w / 4],
                     [0, sh_top], color=C_DARK_GRAY, linewidth=1.5, zorder=5)
        brace_y = sh_top * 0.55
        ax_elev.plot([sx - sh_leg_spread * 0.3, sx + sh_leg_spread * 0.3],
                     [brace_y, brace_y], color=C_DARK_GRAY, linewidth=0.8, zorder=5)
        ax_elev.plot([sx - sh_top_w / 2, sx + sh_top_w / 2],
                     [sh_top, sh_top], color=C_DARK_GRAY, linewidth=2.0, zorder=6)

    # MDF Board on sawhorses
    mdf_bottom = sh_top
    mdf_top_elev = sh_top + MDF_THICK
    mdf_side = Rectangle((0, mdf_bottom), MDF_LENGTH, MDF_THICK,
                          facecolor=C_MDF_BROWN, edgecolor=C_DARK_GRAY,
                          linewidth=1.2, alpha=0.6, zorder=7)
    ax_elev.add_patch(mdf_side)

    # Level indicators
    for lx in [48, 96, 144]:
        lw_icon = 8
        lh_icon = 2
        level_rect = Rectangle((lx - lw_icon / 2, mdf_top_elev + 0.5),
                                lw_icon, lh_icon,
                                facecolor=C_WATER_BLUE, edgecolor=C_DARK_GRAY,
                                linewidth=0.5, alpha=0.5, zorder=8)
        ax_elev.add_patch(level_rect)
        bubble = Circle((lx, mdf_top_elev + 0.5 + lh_icon / 2), 0.6,
                         facecolor="#90EE90", edgecolor=C_DARK_GRAY,
                         linewidth=0.3, zorder=9)
        ax_elev.add_patch(bubble)

    # Dimensions
    draw_dimension_line(ax_elev, (sawhorse_positions[0] - sh_leg_spread / 2 - 2, 0),
                        (sawhorse_positions[0] - sh_leg_spread / 2 - 2, sh_top),
                        '36"', offset=-5, color=C_DIM_BLUE, fontsize=6)
    draw_dimension_line(ax_elev, (MDF_LENGTH + 2, mdf_bottom),
                        (MDF_LENGTH + 2, mdf_top_elev),
                        '3/4"', offset=4, color=C_RED_DIM, fontsize=5)
    draw_dimension_line(ax_elev, (0, 0), (MDF_LENGTH, 0),
                        '192"', offset=-3, color=C_DIM_BLUE, fontsize=7)
    draw_dimension_line(ax_elev,
                        (sawhorse_positions[0], sh_top + 5),
                        (sawhorse_positions[1], sh_top + 5),
                        '48" TYP.', offset=2, color=C_RED_DIM, fontsize=5)

    # Labels
    draw_leader(ax_elev, (96, mdf_bottom + MDF_THICK / 2),
                (96, mdf_bottom + 8),
                '3/4" MDF STRONGBACK\n36" W \u00d7 192" L', color=C_NAU_BLUE, fontsize=5.5)
    draw_leader(ax_elev, (sawhorse_positions[1], sh_top * 0.5),
                (sawhorse_positions[1] + 25, sh_top * 0.3),
                "SAWHORSE (4 REQ'D)\n36\" HEIGHT, ADJUSTABLE", color=C_DARK_GRAY, fontsize=5)

    # ========== DETAIL A: Station Marking ==========
    ax_det = fig.add_axes([0.55, 0.13, 0.40, 0.16], facecolor=C_BG_CREAM)
    ax_det.set_xlim(-2, 42)
    ax_det.set_ylim(-8, 12)
    ax_det.set_aspect("equal")
    ax_det.set_axis_off()

    ax_det.text(20, 10.5, "DETAIL A: STATION MARKING", fontsize=8,
                fontweight="bold", color=C_NAU_BLUE, ha="center", va="center",
                fontfamily="sans-serif",
                bbox=dict(boxstyle="round,pad=0.3", facecolor=C_WHITE,
                          edgecolor=C_NAU_BLUE, linewidth=1.0))
    ax_det.text(20, 8.5, 'SCALE: 1" = 2" (1:2)', fontsize=5,
                color=C_MED_GRAY, ha="center", va="center", fontfamily="sans-serif")

    # Zoomed MDF surface
    det_mdf = Rectangle((0, -5), 40, 10,
                         facecolor=C_MDF_BROWN, edgecolor=C_DARK_GRAY,
                         linewidth=1.0, alpha=0.4, zorder=3)
    ax_det.add_patch(det_mdf)

    # Centerline
    ax_det.plot([0, 40], [0, 0], color=C_SECTION_RED, linewidth=0.8,
                linestyle=(0, (10, 3, 2, 3)), zorder=10)
    ax_det.text(41, 0, "CL", fontsize=6, fontweight="bold",
                color=C_SECTION_RED, ha="left", va="center")

    # Three station lines
    for idx, sx in enumerate([8, 14, 20]):
        stn_num = idx + 5
        ax_det.plot([sx, sx], [-5, 5], color=C_NAU_BLUE,
                    linewidth=0.8, linestyle="--", zorder=5)
        ax_det.text(sx, 5.8, f"S{stn_num}", fontsize=7, fontweight="bold",
                    color=C_NAU_BLUE, ha="center", va="bottom",
                    fontfamily="sans-serif", zorder=10)
        ax_det.plot([sx - 0.5, sx + 0.5], [0, 0], color=C_SECTION_RED,
                    linewidth=1.5, zorder=11)

    draw_dimension_line(ax_det, (8, -5), (14, -5),
                        '6.000"', offset=-2, color=C_DIM_BLUE, fontsize=6)

    ax_det.text(30, -6.5,
                "MARK ALL 33 STATIONS\nWITH SHARPIE ON CL\nUSE STEEL TAPE",
                fontsize=4.5, color=C_MED_GRAY, ha="center", va="top",
                fontfamily="sans-serif", fontstyle="italic",
                bbox=dict(boxstyle="round,pad=0.2", facecolor=C_WHITE,
                          edgecolor=C_LIGHT_GRAY, linewidth=0.3))

    # ========== ASSEMBLY NOTES ==========
    ax_note = fig.add_axes([0.06, 0.13, 0.45, 0.16], facecolor=C_BG_CREAM)
    ax_note.set_xlim(0, 50)
    ax_note.set_ylim(0, 12)
    ax_note.set_axis_off()

    note_title_rect = Rectangle((1, 9.5), 48, 2.2,
                                 facecolor=C_NAU_BLUE, edgecolor=C_NAU_BLUE,
                                 linewidth=1, zorder=5)
    ax_note.add_patch(note_title_rect)
    ax_note.text(25, 10.6, "ASSEMBLY NOTES", fontsize=7, fontweight="bold",
                 color=C_NAU_GOLD, ha="center", va="center",
                 fontfamily="sans-serif", zorder=6)

    assembly_notes = [
        '1. SET SAWHORSES ON LEVEL FLOOR, 48" O.C. SPACING.',
        '2. PLACE MDF BOARD ON SAWHORSES, VERIFY LEVEL (+/- 1/16").',
        "3. SHIM SAWHORSE LEGS AS NEEDED FOR LEVELNESS.",
        "4. MARK CENTERLINE FULL LENGTH WITH CHALK LINE.",
        '5. MARK ALL 33 STATIONS AT 6" O.C. FROM BOW (LEFT) END.',
        "6. LABEL EACH STATION WITH PERMANENT MARKER.",
        '7. VERIFY STATION 16 (MIDSHIP) IS AT 96" FROM EACH END.',
        '8. APPLY REFERENCE GRID: CENTERLINE + 6",12",18" EACH SIDE.',
    ]

    notes_bg = Rectangle((1, 0.5), 48, 9,
                          facecolor=C_WHITE, edgecolor=C_NAU_BLUE,
                          linewidth=0.8, zorder=4)
    ax_note.add_patch(notes_bg)

    for i, note in enumerate(assembly_notes):
        ax_note.text(2.5, 8.8 - i * 1.05, note, fontsize=4.5,
                     color=C_DARK_GRAY, ha="left", va="center",
                     fontfamily="sans-serif", zorder=6)

    save_sheet(fig, 3, "_Strongback_Assembly")


# #############################################################################
#
#  SHEET 4: FOAM NESTING LAYOUT
#
# #############################################################################
def sheet_04_foam_nesting():
    """
    Generate Sheet 04 - Foam Nesting Layout.
    Shows how to cut station cross-sections from 8 EPS foam sheets.
    Lamination strategy, nesting, waste calculations.
    """
    print("Generating Sheet 04: Foam Nesting Layout...")
    fig = plt.figure(figsize=(SHEET_W_IN, SHEET_H_IN), dpi=DPI, facecolor=C_WHITE)
    draw_title_block(fig, 4, "Foam Nesting Layout (EPS Mold Sections)")

    # ======================================================================
    # Compute station footprints and nesting assignments
    # ======================================================================
    # Each station section requires:
    #   width = full_beam + 4" margin (2" each side)
    #   height = depth + 2" margin (1" top, 1" bottom)
    station_footprints = []
    for i in range(NUM_STATIONS):
        hb = STATION_HALF_BEAM[i]
        d = STATION_DEPTH[i]
        if hb < 0.1 and d < 0.1:
            continue  # skip bow/stern tips
        req_w = 2.0 * hb + 4.0
        req_h = d + 2.0
        station_footprints.append((i, req_w, req_h))

    # Greedy row-packing onto 48x96 sheets
    sheet_assignments = []
    current_sheet = []
    cursor_x = 0
    cursor_y = 0
    row_max_h = 0
    SHEET_USABLE_W = FOAM_SHEET_L  # 96" (long dimension)
    SHEET_USABLE_H = FOAM_SHEET_W  # 48" (short dimension)
    ROW_GAP = 1.0
    COL_GAP = 1.0

    for (stn_idx, fw, fh) in station_footprints:
        if cursor_x + fw > SHEET_USABLE_W:
            cursor_y += row_max_h + ROW_GAP
            cursor_x = 0
            row_max_h = 0
        if cursor_y + fh > SHEET_USABLE_H:
            sheet_assignments.append(current_sheet)
            current_sheet = []
            cursor_x = 0
            cursor_y = 0
            row_max_h = 0
        current_sheet.append((stn_idx, cursor_x, cursor_y, fw, fh))
        cursor_x += fw + COL_GAP
        row_max_h = max(row_max_h, fh)

    if current_sheet:
        sheet_assignments.append(current_sheet)

    n_sheets_needed = len(sheet_assignments)

    # ======================================================================
    # DRAW NESTING LAYOUTS (upper-left area)
    # ======================================================================
    ax_main = fig.add_axes([0.04, 0.30, 0.62, 0.62], facecolor=C_BG_CREAM)
    ax_main.set_axis_off()

    n_cols = 2
    n_rows = math.ceil(n_sheets_needed / n_cols)
    pad = 8
    draw_scale = 0.42

    total_draw_w = n_cols * (SHEET_USABLE_W * draw_scale + pad)
    total_draw_h = n_rows * (SHEET_USABLE_H * draw_scale + pad + 5)
    ax_main.set_xlim(-5, total_draw_w + 5)
    ax_main.set_ylim(-5, total_draw_h + 5)

    ax_main.text(total_draw_w / 2, total_draw_h + 3,
                 f"FOAM SHEET NESTING  ({n_sheets_needed} SHEETS REQUIRED)",
                 fontsize=11, fontweight="bold", color=C_NAU_BLUE,
                 ha="center", va="center", fontfamily="sans-serif",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor=C_WHITE,
                           edgecolor=C_NAU_BLUE, linewidth=1.0))

    for sheet_idx, sections in enumerate(sheet_assignments):
        col = sheet_idx % n_cols
        row = n_rows - 1 - sheet_idx // n_cols

        sx0 = col * (SHEET_USABLE_W * draw_scale + pad)
        sy0 = row * (SHEET_USABLE_H * draw_scale + pad + 5)
        sw = SHEET_USABLE_W * draw_scale
        sh = SHEET_USABLE_H * draw_scale

        # Foam sheet background
        sheet_rect = Rectangle((sx0, sy0), sw, sh,
                                facecolor=C_FOAM_BEIGE, edgecolor=C_DARK_GRAY,
                                linewidth=1.2, zorder=3)
        ax_main.add_patch(sheet_rect)

        # Sheet label
        ax_main.text(sx0 + sw / 2, sy0 + sh + 1.5,
                     f"SHEET {sheet_idx + 1}",
                     fontsize=7, fontweight="bold", color=C_NAU_BLUE,
                     ha="center", va="bottom", fontfamily="sans-serif")
        ax_main.text(sx0 + sw / 2, sy0 + sh + 0.3,
                     f'{FOAM_SHEET_L}" \u00d7 {FOAM_SHEET_W}" \u00d7 {FOAM_SHEET_THICK}"',
                     fontsize=4.5, color=C_MED_GRAY, ha="center", va="bottom",
                     fontfamily="sans-serif")

        # Draw station sections
        total_section_area = 0
        for (stn, px, py, pw, ph) in sections:
            dpx = sx0 + px * draw_scale
            dpy = sy0 + py * draw_scale
            dpw = pw * draw_scale
            dph = ph * draw_scale

            # Section rectangle (blank before cutting)
            sec_rect = Rectangle((dpx, dpy), dpw, dph,
                                  facecolor=C_FOAM_PINK, edgecolor=C_NAU_BLUE,
                                  linewidth=0.8, alpha=0.7, zorder=5)
            ax_main.add_patch(sec_rect)

            # Hull cross-section cut line
            xs_hull, ys_hull = get_cross_section(stn)
            if len(xs_hull) > 1:
                hb = STATION_HALF_BEAM[stn]
                d = STATION_DEPTH[stn]
                cx = dpx + dpw / 2
                hull_draw_x = cx + xs_hull * draw_scale
                hull_draw_y = dpy + (1.0 + ys_hull) * draw_scale

                ax_main.plot(hull_draw_x, hull_draw_y, color=C_SECTION_RED,
                             linewidth=0.6, zorder=6)

                # Fill trough region
                hull_fill_x = np.concatenate([hull_draw_x,
                                               [hull_draw_x[-1], hull_draw_x[0]]])
                hull_fill_y = np.concatenate([hull_draw_y,
                                               [dpy, dpy]])
                try:
                    trough = Polygon(np.column_stack([hull_fill_x, hull_fill_y]),
                                     closed=True, facecolor=C_WHITE,
                                     edgecolor=C_SECTION_RED, linewidth=0.4,
                                     alpha=0.5, zorder=4)
                    ax_main.add_patch(trough)
                except Exception:
                    pass

            # Station label
            ax_main.text(dpx + dpw / 2, dpy + dph / 2,
                         f"S{stn}", fontsize=5 if dpw > 4 else 3.5,
                         fontweight="bold", color=C_NAU_BLUE,
                         ha="center", va="center", fontfamily="sans-serif", zorder=8)

            total_section_area += pw * ph

        # Waste percentage
        waste_pct = max(0, (FOAM_SHEET_W * FOAM_SHEET_L - total_section_area) / (FOAM_SHEET_W * FOAM_SHEET_L) * 100)
        ax_main.text(sx0 + sw - 1, sy0 + 1,
                     f"Waste: {waste_pct:.0f}%", fontsize=4,
                     color=C_MED_GRAY, ha="right", va="bottom",
                     fontfamily="sans-serif", fontstyle="italic", zorder=10)

    # ======================================================================
    # LAMINATION DETAIL (right side)
    # ======================================================================
    ax_lam = fig.add_axes([0.68, 0.55, 0.28, 0.37], facecolor=C_BG_CREAM)
    ax_lam.set_xlim(-2, 28)
    ax_lam.set_ylim(-4, 32)
    ax_lam.set_aspect("equal")
    ax_lam.set_axis_off()

    ax_lam.text(13, 30.5, "LAMINATION DETAIL", fontsize=8, fontweight="bold",
                color=C_NAU_BLUE, ha="center", va="center", fontfamily="sans-serif",
                bbox=dict(boxstyle="round,pad=0.3", facecolor=C_WHITE,
                          edgecolor=C_NAU_BLUE, linewidth=1.0))
    ax_lam.text(13, 28.5, 'SCALE: 1" = 1" (1:1)', fontsize=5,
                color=C_MED_GRAY, ha="center", va="center", fontfamily="sans-serif")

    # Step 1: Two 4" foam layers stacked
    layer1 = Rectangle((2, 18), 20, 4,
                        facecolor=C_FOAM_BEIGE, edgecolor=C_DARK_GRAY,
                        linewidth=1.0, zorder=3)
    ax_lam.add_patch(layer1)
    draw_hatch_dots(ax_lam, 2, 18, 20, 4, spacing=1.0,
                    color=C_FOAM_PINK, size=1.0, zorder=4)

    layer2 = Rectangle((2, 22), 20, 4,
                        facecolor=C_FOAM_BEIGE, edgecolor=C_DARK_GRAY,
                        linewidth=1.0, zorder=3)
    ax_lam.add_patch(layer2)
    draw_hatch_dots(ax_lam, 2, 22, 20, 4, spacing=1.0,
                    color=C_FOAM_PINK, size=1.0, zorder=4)

    # Glue line
    ax_lam.plot([2, 22], [22, 22], color=C_NAU_GOLD, linewidth=2.5, zorder=5)
    draw_leader(ax_lam, (12, 22), (25, 22),
                "GORILLA GLUE\n(THIN BEAD)", color=C_NAU_GOLD, fontsize=4.5)

    # Dimensions for layers
    draw_dimension_line(ax_lam, (0.5, 18), (0.5, 22),
                        '4"', offset=-1.2, color=C_DIM_BLUE, fontsize=5.5)
    draw_dimension_line(ax_lam, (0.5, 22), (0.5, 26),
                        '4"', offset=-1.2, color=C_DIM_BLUE, fontsize=5.5)
    draw_dimension_line(ax_lam, (24, 18), (24, 26),
                        '8" TOTAL', offset=1.5, color=C_RED_DIM, fontsize=5.5)

    # Arrow to step 2
    ax_lam.annotate("", xy=(12, 14.5), xytext=(12, 17),
                    arrowprops=dict(arrowstyle="-|>", color=C_NAU_BLUE, lw=1.5), zorder=10)
    ax_lam.text(12, 15.8, 'RIP TO 6"', fontsize=6, fontweight="bold",
                color=C_NAU_BLUE, ha="center", va="center", fontfamily="sans-serif",
                bbox=dict(boxstyle="round,pad=0.2", facecolor=C_NAU_GOLD,
                          edgecolor=C_NAU_BLUE, linewidth=0.5, alpha=0.3))

    # Step 2: 6" usable block
    block_6 = Rectangle((2, 7), 20, 6,
                         facecolor=C_FOAM_BEIGE, edgecolor=C_DARK_GRAY,
                         linewidth=1.2, zorder=3)
    ax_lam.add_patch(block_6)
    draw_hatch_dots(ax_lam, 2, 7, 20, 6, spacing=1.0,
                    color=C_FOAM_PINK, size=1.0, zorder=4)

    # Waste strip (2")
    waste_strip = Rectangle((2, 13), 20, 2,
                             facecolor=C_LIGHT_GRAY, edgecolor=C_DARK_GRAY,
                             linewidth=0.6, linestyle="--", zorder=3)
    ax_lam.add_patch(waste_strip)
    draw_hatch_diagonal(ax_lam, 2, 13, 20, 2, spacing=1.5,
                        color=C_MED_GRAY, linewidth=0.4, zorder=4)
    ax_lam.text(12, 14, 'WASTE (2")', fontsize=4.5, color=C_RED_DIM,
                ha="center", va="center", fontfamily="sans-serif",
                fontweight="bold", zorder=5)

    draw_dimension_line(ax_lam, (0.5, 7), (0.5, 13),
                        '6"', offset=-1.2, color=C_DIM_BLUE, fontsize=5.5)

    ax_lam.text(12, 10, "MOLD SECTION\n(6\" THICK)", fontsize=5.5,
                fontweight="bold", color=C_NAU_BLUE, ha="center", va="center",
                fontfamily="sans-serif", zorder=6)

    # Step 3 note
    ax_lam.text(12, 4, "CUT STATION PROFILE\nWITH HOT WIRE CUTTER",
                fontsize=5, fontweight="bold", color=C_DARK_GRAY,
                ha="center", va="center", fontfamily="sans-serif",
                bbox=dict(boxstyle="round,pad=0.3", facecolor=C_VERY_LIGHT,
                          edgecolor=C_MED_GRAY, linewidth=0.5))

    # Process flow
    ax_lam.text(12, 0.5,
                '4" SHEET \u00d7 2  \u2192  GLUE  \u2192  8" BLOCK  \u2192  RIP TO 6"  \u2192  CUT PROFILE',
                fontsize=3.8, color=C_MED_GRAY, ha="center", va="center",
                fontfamily="sans-serif", fontstyle="italic")

    # ======================================================================
    # NESTING TABLE (bottom)
    # ======================================================================
    ax_table = fig.add_axes([0.04, 0.13, 0.92, 0.18], facecolor=C_BG_CREAM)
    ax_table.set_xlim(0, 100)
    ax_table.set_ylim(0, 16)
    ax_table.set_axis_off()

    ax_table.text(50, 15, "FOAM CUTTING SCHEDULE", fontsize=9,
                  fontweight="bold", color=C_NAU_BLUE, ha="center", va="center",
                  fontfamily="sans-serif",
                  bbox=dict(boxstyle="round,pad=0.3", facecolor=C_WHITE,
                            edgecolor=C_NAU_BLUE, linewidth=1.0))

    tbl_cols = [2, 12, 55, 68, 80, 98]
    tbl_hdrs = ["SHEET #", "STATIONS", "# SECTIONS", "USAGE %", "NOTES"]
    tbl_hdr_cx = [(tbl_cols[i] + tbl_cols[i + 1]) / 2 for i in range(len(tbl_hdrs))]

    hdr_y = 13
    hdr_h = 1.8
    hdr_bg = Rectangle((tbl_cols[0], hdr_y - hdr_h),
                        tbl_cols[-1] - tbl_cols[0], hdr_h,
                        facecolor=C_NAU_BLUE, edgecolor=C_NAU_BLUE,
                        linewidth=1, zorder=5)
    ax_table.add_patch(hdr_bg)

    for i, hdr in enumerate(tbl_hdrs):
        ax_table.text(tbl_hdr_cx[i], hdr_y - hdr_h / 2, hdr,
                      fontsize=5.5, fontweight="bold", color=C_NAU_GOLD,
                      ha="center", va="center", fontfamily="sans-serif", zorder=6)

    row_h_t = 1.3
    for sheet_idx, sections in enumerate(sheet_assignments):
        ry = hdr_y - hdr_h - sheet_idx * row_h_t

        if sheet_idx % 2 == 0:
            rbg = Rectangle((tbl_cols[0], ry - row_h_t),
                             tbl_cols[-1] - tbl_cols[0], row_h_t,
                             facecolor=C_VERY_LIGHT, edgecolor="none", zorder=3)
            ax_table.add_patch(rbg)

        ax_table.plot([tbl_cols[0], tbl_cols[-1]], [ry, ry],
                      color=C_LIGHT_GRAY, linewidth=0.3, zorder=4)

        stn_list = [s[0] for s in sections]
        stn_str = ", ".join(f"S{s}" for s in stn_list)
        n_sections = len(sections)
        total_area = sum(s[3] * s[4] for s in sections)
        sheet_total = FOAM_SHEET_W * FOAM_SHEET_L
        usage = total_area / sheet_total * 100

        note = ""
        if any(s[0] == MIDSHIP_STATION for s in sections):
            note = "Contains midship (widest)"
        elif all(STATION_HALF_BEAM[s[0]] < 5 for s in sections):
            note = "Small bow/stern sections"

        row_data = [f"Sheet {sheet_idx + 1}", stn_str, str(n_sections),
                    f"{usage:.0f}%", note]
        for ci, txt in enumerate(row_data):
            ax_table.text(tbl_hdr_cx[ci], ry - row_h_t / 2, txt,
                          fontsize=4.2, color=C_DARK_GRAY,
                          ha="center", va="center",
                          fontfamily="sans-serif", zorder=6)

    bottom_y = hdr_y - hdr_h - len(sheet_assignments) * row_h_t
    ax_table.plot([tbl_cols[0], tbl_cols[-1]], [bottom_y, bottom_y],
                  color=C_NAU_BLUE, linewidth=1, zorder=4)
    for cx in tbl_cols:
        ax_table.plot([cx, cx], [hdr_y, bottom_y],
                      color=C_LIGHT_GRAY, linewidth=0.4, zorder=4)

    ax_table.text(50, bottom_y - 1,
                  f"TOTAL: {sum(len(s) for s in sheet_assignments)} SECTIONS FROM "
                  f"{n_sheets_needed} FOAM SHEETS  |  "
                  'EACH SECTION = 6" THICK (2\u00d74" LAMINATED, RIPPED)  |  '
                  "ALL CUTS WITH HOT WIRE CUTTER",
                  fontsize=4.5, color=C_MED_GRAY, ha="center", va="top",
                  fontfamily="sans-serif", fontstyle="italic")

    save_sheet(fig, 4, "_Foam_Nesting_Layout")




# ===================================================================
#  SHEETS 5-20 (Merged from Part 2)
# ===================================================================

# Compatibility aliases: Part 2 uses shorter variable names
FIG_W = SHEET_W_IN
FIG_H = SHEET_H_IN
NAU_BLUE = C_NAU_BLUE
NAU_GOLD = C_NAU_GOLD
CONCRETE_GRAY = C_CONCRETE
FOAM_COLOR = C_FOAM_BEIGE
MESH_COLOR = C_MESH_GREEN
WHITE = C_WHITE
LIGHT_GRAY = C_LIGHT_GRAY
MED_GRAY = C_MED_GRAY
DARK_GRAY = C_DARK_GRAY

# Build STATIONS dict from arrays: {station_num: (half_beam, depth)}
STATIONS = {i: (STATION_HALF_BEAM[i], STATION_DEPTH[i])
            for i in range(len(STATION_HALF_BEAM))}
DXF_DATA = DXF_COORDS  # Alias for Part 2 compatibility

# ---------------------------------------------------------------------------
# Helper: generate a smooth hull cross-section curve for a given station
# ---------------------------------------------------------------------------

def _hull_curve(station_num, n_pts=80):
    """Return (xs, ys) for the full cross-section of a station.
    Curve goes from port gunwale across keel to starboard gunwale.
    x = athwartship (0 = CL), y = vertical (0 = keel, positive up).
    V-bottom approximation with smooth blend at bilge."""
    hb, d = STATIONS[station_num]
    if hb == 0 and d == 0:
        return np.array([0]), np.array([0])
    t = np.linspace(-1, 1, n_pts)
    x = hb * t
    y = d * (1 - np.abs(t) ** 1.6)
    y = d - y
    return x, y


def _draw_template(ax, station_num, foam_extra_w=4, foam_extra_h=2):
    """Draw a single foam template in the given axes.
    Shows outer foam block, hull cut-out, dimensions, hatching."""
    hb, d = STATIONS[station_num]
    full_beam = 2 * hb
    block_w = full_beam + foam_extra_w
    block_h = d + foam_extra_h

    rect = Rectangle((-block_w / 2, 0), block_w, block_h,
                      linewidth=2, edgecolor=DARK_GRAY,
                      facecolor=FOAM_COLOR, zorder=1)
    ax.add_patch(rect)

    xs, ys = _hull_curve(station_num)
    # Close the hull curve for filling (unused vars kept for reference)
    # xs_closed = np.concatenate([xs, [xs[-1], xs[0]]])
    # ys_closed = np.concatenate([ys, [block_h, block_h]])

    ax.fill(xs, ys, color=WHITE, zorder=2)
    ax.plot(xs, ys, color=NAU_BLUE, linewidth=2.5, zorder=3)

    ax.text(0, d * 0.45, "CUT THIS\nSHAPE OUT",
            ha="center", va="center", fontsize=9, fontweight="bold",
            color="red", zorder=5,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="red", alpha=0.85))

    for yy in np.arange(0, block_h, 1.0):
        ax.plot([-block_w / 2, block_w / 2], [yy, yy],
                color=MED_GRAY, linewidth=0.3, linestyle=':', zorder=1.5)

    ax.axvline(0, color=NAU_BLUE, linewidth=1, linestyle='-.', zorder=4)
    ax.text(0.3, block_h - 0.5, "CL", fontsize=8, color=NAU_BLUE,
            fontstyle='italic', zorder=5)

    if hb > 0:
        angle_len = min(hb * 0.6, 5)
        ax.annotate('', xy=(angle_len, angle_len * np.tan(np.radians(15))),
                     xytext=(0, 0),
                     arrowprops=dict(arrowstyle='->', color='red', lw=1.2))
        ax.text(angle_len * 0.5, angle_len * np.tan(np.radians(15)) + 0.6,
                '15\u00b0', fontsize=8, color='red', ha='center')

    offset = 1.5
    draw_dimension_line(ax, (-full_beam / 2, block_h + offset),
                        (full_beam / 2, block_h + offset),
                        f'{full_beam:.1f}"', 0.5, DARK_GRAY)
    draw_dimension_line(ax, (block_w / 2 + offset, 0),
                        (block_w / 2 + offset, d),
                        f'{d:.1f}"', 0.5, DARK_GRAY)
    draw_dimension_line(ax, (-block_w / 2, -offset),
                        (block_w / 2, -offset),
                        f'{block_w:.1f}" block', 0.5, MED_GRAY)

    ax.set_xlim(-block_w / 2 - 3, block_w / 2 + 5)
    ax.set_ylim(-3, block_h + 4)
    ax.set_aspect('equal')
    ax.set_title(f'Station {station_num}  (HB={hb}", D={d}")',
                 fontsize=11, fontweight='bold', color=NAU_BLUE)
    ax.set_xlabel('inches')
    ax.set_ylabel('inches')
    ax.grid(True, alpha=0.2)


def _template_sheet(stations, sheet_num, sheet_title):
    """Generic 2x2 template sheet for 4 stations."""
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    draw_title_block(fig, sheet_num, sheet_title)

    positions = [(0.06, 0.52, 0.42, 0.38),
                 (0.54, 0.52, 0.42, 0.38),
                 (0.06, 0.08, 0.42, 0.38),
                 (0.54, 0.08, 0.42, 0.38)]

    for idx, st in enumerate(stations):
        ax = fig.add_axes(positions[idx])
        _draw_template(ax, st)

    if sheet_num == 8:
        fig.text(0.5, 0.03,
                 "NOTE: Stations 17-31 mirror Stations 15-1 respectively. "
                 "Use same templates flipped.",
                 ha='center', fontsize=12, fontstyle='italic',
                 color='red', fontweight='bold')

    out = os.path.join(OUTPUT_DIR, f'sheet_{sheet_num:02d}_{sheet_title.lower().replace(" ","_")}.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out


# ===================================================================
# SHEET 5 - Foam Templates Stations 1-4
# ===================================================================
def sheet_05_templates_1_4():
    """Foam cutting templates for Stations 1-4."""
    return _template_sheet([1, 2, 3, 4], 5, "Foam Templates St 1-4")


# ===================================================================
# SHEET 6 - Foam Templates Stations 5-8
# ===================================================================
def sheet_06_templates_5_8():
    """Foam cutting templates for Stations 5-8."""
    return _template_sheet([5, 6, 7, 8], 6, "Foam Templates St 5-8")


# ===================================================================
# SHEET 7 - Foam Templates Stations 9-12
# ===================================================================
def sheet_07_templates_9_12():
    """Foam cutting templates for Stations 9-12."""
    return _template_sheet([9, 10, 11, 12], 7, "Foam Templates St 9-12")


# ===================================================================
# SHEET 8 - Foam Templates Stations 13-16
# ===================================================================
def sheet_08_templates_13_16():
    """Foam cutting templates for Stations 13-16 (16 = midship, widest)."""
    return _template_sheet([13, 14, 15, 16], 8, "Foam Templates St 13-16")


# ===================================================================
# SHEET 9 - Mold Assembly Sequence
# ===================================================================
def sheet_09_mold_assembly():
    """4-panel mold assembly sequence diagram."""
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    draw_title_block(fig, 9, "Mold Assembly Sequence")

    panel_specs = [
        (0.06, 0.52, 0.42, 0.38),
        (0.54, 0.52, 0.42, 0.38),
        (0.06, 0.08, 0.42, 0.38),
        (0.54, 0.08, 0.42, 0.38),
    ]
    titles = [
        "Step 1: Place Midship Station (St 16)",
        "Step 2: Work Outward Symmetrically",
        "Step 3: Fill Gaps with Foam Strips",
        "Step 4: Sand to Fair Contour",
    ]

    # Panel 1 - Place St 16
    ax1 = fig.add_axes(panel_specs[0])
    ax1.set_xlim(-5, 220)
    ax1.set_ylim(-5, 30)
    ax1.set_aspect('equal')
    ax1.add_patch(Rectangle((0, 0), 216, 3, fc=MESH_COLOR, ec=DARK_GRAY, lw=2))
    ax1.text(108, 1.5, 'STRONGBACK  (216" x 6" x 6")', ha='center', va='center',
             fontsize=9, color=WHITE, fontweight='bold')
    st16_x = 108
    hb16, d16 = STATIONS[16]
    xs16, ys16 = _hull_curve(16, 40)
    ax1.plot(xs16 / 3 + st16_x, ys16 / 3 + 3, color=NAU_BLUE, lw=2)
    ax1.annotate("St 16\n(MIDSHIP)", xy=(st16_x, 3 + d16 / 3 + 1),
                 fontsize=10, ha='center', fontweight='bold', color=NAU_BLUE)
    ax1.annotate('', xy=(st16_x, 3), xytext=(st16_x, 12),
                 arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax1.text(st16_x + 20, 10, "Center on\nstrongback", fontsize=9, color="red")
    ax1.set_title(titles[0], fontsize=11, fontweight='bold', color=NAU_BLUE)
    ax1.grid(True, alpha=0.15)

    # Panel 2 - Work outward
    ax2 = fig.add_axes(panel_specs[1])
    ax2.set_xlim(-5, 220)
    ax2.set_ylim(-5, 30)
    ax2.set_aspect('equal')
    ax2.add_patch(Rectangle((0, 0), 216, 3, fc=MESH_COLOR, ec=DARK_GRAY, lw=2))
    spacing = 216 / 32
    for st_offset in range(0, 5):
        for side in [-1, 1]:
            st_num = 16 + side * st_offset
            if st_num < 0 or st_num > 32:
                continue
            x_pos = st_num * spacing
            hb_s, d_s = STATIONS[st_num]
            if d_s == 0:
                continue
            xs_s, ys_s = _hull_curve(st_num, 30)
            ax2.plot(xs_s / 3 + x_pos, ys_s / 3 + 3,
                     color=NAU_BLUE, lw=1.5, alpha=0.7)
            ax2.text(x_pos, 3 + d_s / 3 + 1, str(st_num),
                     fontsize=7, ha='center', color=NAU_BLUE)
    ax2.annotate('', xy=(60, 25), xytext=(108, 25),
                 arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax2.annotate('', xy=(156, 25), xytext=(108, 25),
                 arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax2.text(108, 27, "Work outward from midship", ha="center",
             fontsize=10, color='red', fontweight='bold')
    ax2.text(30, 15, "15,14,13...\n(then 17,18,19...)",
             fontsize=8, ha='center', color=DARK_GRAY)
    ax2.set_title(titles[1], fontsize=11, fontweight='bold', color=NAU_BLUE)
    ax2.grid(True, alpha=0.15)

    # Panel 3 - Fill gaps with foam strips
    ax3 = fig.add_axes(panel_specs[2])
    ax3.set_xlim(-2, 30)
    ax3.set_ylim(-2, 20)
    ax3.set_aspect('equal')
    for xoff, lbl in [(5, 'St N'), (20, 'St N+1')]:
        ax3.add_patch(Rectangle((xoff - 1.5, 0), 3, 15,
                                 fc=FOAM_COLOR, ec=DARK_GRAY, lw=2))
        ax3.text(xoff, 15.5, lbl, ha='center', fontsize=9, fontweight='bold')
    for yy in np.arange(1, 14, 2.5):
        ax3.add_patch(Rectangle((8, yy), 8, 1.5,
                                 fc=NAU_GOLD, ec=DARK_GRAY, lw=1, alpha=0.7))
    ax3.text(12, -1, "Foam strip infill", ha="center", fontsize=9,
             color=DARK_GRAY, fontstyle='italic')
    for yy in [2, 7, 12]:
        ax3.plot([7.5, 8.5], [yy, yy], 'r-', lw=2)
        ax3.plot([16, 17], [yy, yy], 'r-', lw=2)
    ax3.text(25, 5, "Adhesive\nplacement\n(red marks)", fontsize=8,
             color='red', ha='center')
    ax3.set_title(titles[2], fontsize=11, fontweight='bold', color=NAU_BLUE)
    ax3.grid(True, alpha=0.15)

    # Panel 4 - Sand to fair contour
    ax4 = fig.add_axes(panel_specs[3])
    ax4.set_xlim(-5, 220)
    ax4.set_ylim(-5, 30)
    ax4.set_aspect('equal')
    ax4.add_patch(Rectangle((0, 0), 216, 3, fc=MESH_COLOR, ec=DARK_GRAY, lw=2))
    x_env = np.array([s * 216 / 32 for s in range(0, 33)])
    y_top = np.array([STATIONS[s][1] / 3 + 3 for s in range(0, 33)])
    ax4.fill_between(x_env, 3, y_top, color=FOAM_COLOR, alpha=0.5)
    ax4.plot(x_env, y_top, color=NAU_BLUE, lw=2.5)
    ax4.plot([40, 180], [y_top[6], y_top[26]], 'r--', lw=2)
    ax4.text(110, y_top[16] + 3, "Check with 4' batten\n(max 1/16\" gap)",
             ha='center', fontsize=10, color='red', fontweight='bold')
    for xp in [50, 90, 130, 170]:
        sidx = int(xp * 32 / 216)
        ax4.annotate('', xy=(xp + 10, y_top[sidx] - 1),
                     xytext=(xp, y_top[sidx] - 1),
                     arrowprops=dict(arrowstyle='->', color=MED_GRAY, lw=1.5))
    ax4.text(108, 1.5, "STRONGBACK", ha="center", va="center",
             fontsize=9, color=WHITE, fontweight='bold')
    ax4.set_title(titles[3], fontsize=11, fontweight='bold', color=NAU_BLUE)
    ax4.grid(True, alpha=0.15)

    out = os.path.join(OUTPUT_DIR, 'sheet_09_mold_assembly.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out


# ===================================================================
# SHEET 10 - Surface Fairing & Release Agent
# ===================================================================
def sheet_10_surface_prep():
    """Surface preparation stages: sanding grits + PVA release agent."""
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    draw_title_block(fig, 10, "Surface Fairing & Release Agent")

    ax = fig.add_axes([0.08, 0.10, 0.84, 0.78])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 70)
    ax.set_aspect('equal')
    ax.axis('off')

    stages = [
        ("1. ROUGH FOAM", "#D2B48C", "As-cut foam surface\nVisible tool marks"),
        ("2. 80-GRIT SAND", "#DEB887", "Remove high spots\nFlatten ridges"),
        ("3. 120-GRIT SAND", "#F5DEB3", "Smooth surface\nRemove 80-grit scratches"),
        ("4. 220-GRIT SAND", "#FAEBD7", "Final smooth\nReady for PVA"),
        ("5. PVA COAT 1", "#ADD8E6", "Thin, even coat\nDry 2 hours min"),
        ("6. PVA COAT 2", "#87CEEB", "Second coat perpendicular\nDry 2 hours min"),
    ]

    y_start = 60
    layer_h = 8
    layer_w = 70
    x_start = 15

    for i, (label, color, note) in enumerate(stages):
        y = y_start - i * (layer_h + 1.5)
        ax.add_patch(FancyBboxPatch((x_start, y), layer_w, layer_h,
                                     boxstyle="round,pad=0.3",
                                     facecolor=color, edgecolor=DARK_GRAY,
                                     linewidth=2))
        ax.text(x_start + 3, y + layer_h / 2, label,
                fontsize=12, fontweight='bold', va='center', color=DARK_GRAY)
        ax.text(x_start + layer_w - 3, y + layer_h / 2, note,
                fontsize=9, va='center', ha='right', color=DARK_GRAY,
                fontstyle='italic')
        if i < len(stages) - 1:
            ax.annotate('', xy=(x_start + layer_w / 2, y - 1),
                         xytext=(x_start + layer_w / 2, y + 0.2),
                         arrowprops=dict(arrowstyle='->', color=NAU_BLUE, lw=2))

    ax.text(x_start + layer_w + 5, y_start - 2 * (layer_h + 1.5),
            "TIMING NOTES:", fontsize=11, fontweight="bold", color="red")
    ax.text(x_start + layer_w + 5, y_start - 2 * (layer_h + 1.5) - 3,
            "2 hrs drying between PVA coats\n"
            "Apply PVA at 65-75\u00b0F\n"
            "Total surface prep: ~8 hrs",
            fontsize=9, color=DARK_GRAY)
    ax.text(x_start + layer_w + 5, y_start - 4 * (layer_h + 1.5),
            "FAIRNESS TOLERANCE:", fontsize=11, fontweight="bold", color="red")
    ax.text(x_start + layer_w + 5, y_start - 4 * (layer_h + 1.5) - 3,
            "Max 1/16\" gap under\n4-foot batten",
            fontsize=10, color=DARK_GRAY, fontweight="bold")

    # Zoomed cross-section detail
    ax_detail = fig.add_axes([0.55, 0.10, 0.38, 0.25])
    ax_detail.set_xlim(0, 10)
    ax_detail.set_ylim(0, 6)
    ax_detail.set_aspect('equal')
    layers_detail = [
        ("Foam substrate", FOAM_COLOR, 2.0),
        ("Sanded surface", "#FAEBD7", 0.5),
        ("PVA Coat 1", "#ADD8E6", 0.4),
        ("PVA Coat 2", "#87CEEB", 0.4),
    ]
    y_d = 0
    for lbl, clr, th in layers_detail:
        ax_detail.add_patch(Rectangle((0, y_d), 10, th,
                                       fc=clr, ec=DARK_GRAY, lw=1))
        ax_detail.text(5, y_d + th / 2, lbl, ha='center', va='center',
                       fontsize=8, fontweight='bold')
        y_d += th
    ax_detail.set_title("Cross-Section Detail (zoomed)", fontsize=10,
                        fontweight='bold', color=NAU_BLUE)
    ax_detail.set_yticks([])
    ax_detail.set_xticks([])

    out = os.path.join(OUTPUT_DIR, 'sheet_10_surface_prep.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out


# ===================================================================
# SHEET 11 - Basalt Mesh Cutting Pattern
# ===================================================================
def sheet_11_mesh_cutting():
    """Basalt mesh cutting pattern - flattened hull top-down view."""
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    draw_title_block(fig, 11, "Basalt Mesh Cutting Pattern")

    ax = fig.add_axes([0.08, 0.12, 0.84, 0.76])
    length = 216
    stations_x = np.array([s * length / 32 for s in range(33)])
    half_beams = np.array([STATIONS[s][0] for s in range(33)])

    girths = []
    for s in range(33):
        hb, d = STATIONS[s]
        if hb == 0 and d == 0:
            girths.append(0)
        else:
            girth = 2 * np.sqrt(hb ** 2 + d ** 2)
            girths.append(girth)
    girths = np.array(girths)
    half_girths = girths / 2

    ax.fill_between(stations_x, -half_girths, half_girths,
                     color=LIGHT_GRAY, alpha=0.4, edgecolor=DARK_GRAY, lw=2)
    ax.plot(stations_x, half_girths, color=DARK_GRAY, lw=2)
    ax.plot(stations_x, -half_girths, color=DARK_GRAY, lw=2)

    panels = [
        ("BOW PANEL", 0, 11, "red"),
        ("MID PANEL", 10, 23, NAU_BLUE),
        ("STERN PANEL", 22, 32, NAU_GOLD),
    ]
    hatches = ["///", "\\\\\\\\", "|||"]
    for i, (name, s_start, s_end, clr) in enumerate(panels):
        xs = stations_x[s_start:s_end + 1]
        hg_top = half_girths[s_start:s_end + 1]
        hg_bot = -half_girths[s_start:s_end + 1]
        ax.fill_between(xs, hg_bot * 0.95, hg_top * 0.95,
                         alpha=0.2, color=clr, hatch=hatches[i],
                         edgecolor=clr, lw=0.5)
        mid_x = (xs[0] + xs[-1]) / 2
        ax.text(mid_x, 0, name, ha='center', va='center',
                fontsize=14, fontweight='bold', color=clr,
                bbox=dict(fc='white', ec=clr, boxstyle='round,pad=0.3'))

    for s_overlap in [10.5, 22.5]:
        x_ov = s_overlap * length / 32
        ax.axvline(x_ov, color='red', lw=2, linestyle='--')
        ax.text(x_ov, max(half_girths) + 2, 'OVERLAP\n3" min',
                ha='center', fontsize=9, color='red', fontweight='bold')
    for s_c in [10.5, 22.5]:
        x1 = (s_c - 0.5) * length / 32
        x2 = (s_c + 0.5) * length / 32
        ax.axvspan(x1, x2, alpha=0.15, color='red')

    for sx, label in [(stations_x[1], "BOW"), (stations_x[31], "STERN")]:
        ax.annotate(f"Relief dart cut\n({label})",
                     xy=(sx, half_girths[1] * 0.5),
                     xytext=(sx + 15, half_girths[1] * 0.5 + 8),
                     fontsize=9, color='red',
                     arrowprops=dict(arrowstyle='->', color='red'),
                     fontweight='bold')
        dart_y = half_girths[1] * 0.5
        ax.plot([sx - 1, sx, sx + 1], [dart_y + 3, dart_y, dart_y + 3],
                'r-', lw=2)

    ax.axhline(0, color=NAU_BLUE, linewidth=1, linestyle='-.')
    ax.text(5, 1, "CL", fontsize=9, color=NAU_BLUE, fontstyle="italic")

    for s in range(0, 33, 2):
        ax.text(stations_x[s], -max(half_girths) - 3, str(s),
                ha='center', fontsize=7, color=MED_GRAY)
    ax.text(108, -max(half_girths) - 6, "Station Number",
            ha='center', fontsize=9, color=DARK_GRAY)

    total_area_sqin = np.trapezoid(girths, stations_x)
    total_area_sqft = total_area_sqin / 144
    ax.text(0.98, 0.02,
            f"Total mesh area ~ {total_area_sqft:.1f} sq ft\n"
            f"({total_area_sqin:.0f} sq in)\n"
            f"Order +15% for waste: {total_area_sqft * 1.15:.1f} sq ft",
            transform=ax.transAxes, fontsize=11, ha='right', va='bottom',
            fontweight='bold', color=NAU_BLUE,
            bbox=dict(fc='white', ec=NAU_BLUE, boxstyle='round,pad=0.4'))

    ax.set_xlabel("Length along hull (inches)", fontsize=11)
    ax.set_ylabel("Flattened half-girth (inches)", fontsize=11)
    ax.set_title("Basalt Mesh Cutting Layout (Flattened Hull)", fontsize=13,
                 fontweight='bold', color=NAU_BLUE)
    ax.grid(True, alpha=0.2)

    out = os.path.join(OUTPUT_DIR, 'sheet_11_mesh_cutting.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out


# ===================================================================
# SHEET 12 - First Concrete Lift (0.20")
# ===================================================================
def sheet_12_concrete_lift1():
    """First concrete lift placement - 0.20 inch thickness."""
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    draw_title_block(fig, 12, 'First Concrete Lift (0.20")')

    ax = fig.add_axes([0.08, 0.35, 0.55, 0.53])
    xs_mold, ys_mold = _hull_curve(16, 100)
    ax.fill(xs_mold, ys_mold, color=FOAM_COLOR, alpha=0.6, label='Foam mold')
    ax.plot(xs_mold, ys_mold, color=DARK_GRAY, lw=2)

    scale = 0.96
    xs_lift = xs_mold * scale
    ys_lift = ys_mold * scale + 0.3
    ax.fill(xs_lift, ys_lift, color=CONCRETE_GRAY, alpha=0.5, label='Lift 1 (0.20")')
    ax.plot(xs_lift, ys_lift, color=NAU_BLUE, lw=2)

    arrow_positions = [(0, 2), (-5, 6), (5, 6), (-10, 10), (10, 10)]
    arrow_dirs = [(0, 1), (-1, 0.8), (1, 0.8), (-1, 0.5), (1, 0.5)]
    for (px, py), (dx, dy) in zip(arrow_positions, arrow_dirs):
        ax.annotate('', xy=(px + dx * 2, py + dy * 2), xytext=(px, py),
                     arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
    ax.text(0, 0.5, "START\nHERE", ha="center", va="center", fontsize=8,
            color='red', fontweight='bold')

    for gx in np.arange(-14, 15, 4):
        gy_idx = np.argmin(np.abs(xs_mold - gx))
        gy = ys_mold[gy_idx]
        ax.plot(gx, gy + 0.5, 'v', color=NAU_GOLD, markersize=8)
    ax.plot([], [], 'v', color=NAU_GOLD, markersize=8, label='Thickness gauge position')

    ax.set_aspect('equal')
    ax.legend(loc='upper right', fontsize=9)
    ax.set_title("Cross-Section at Midship (St 16) - Lift 1 Placement",
                 fontsize=12, fontweight='bold', color=NAU_BLUE)
    ax.set_xlabel("inches")
    ax.set_ylabel("inches")
    ax.grid(True, alpha=0.2)

    ax2 = fig.add_axes([0.08, 0.08, 0.55, 0.22])
    ax2.set_xlim(-5, 220)
    ax2.set_ylim(-3, 20)
    ax2.set_aspect('equal')
    stations_x = np.array([s * 216 / 32 for s in range(33)])
    depths = np.array([STATIONS[s][1] for s in range(33)])
    ax2.fill_between(stations_x, 0, depths * 0.8, color=FOAM_COLOR, alpha=0.3)
    ax2.plot(stations_x, depths * 0.8, color=DARK_GRAY, lw=2)
    ax2.annotate('', xy=(30, 15), xytext=(108, 15),
                 arrowprops=dict(arrowstyle='->', color='red', lw=2.5))
    ax2.annotate('', xy=(186, 15), xytext=(108, 15),
                 arrowprops=dict(arrowstyle='->', color='red', lw=2.5))
    ax2.text(108, 17, "Apply: bottom center > sides > bow/stern",
             ha='center', fontsize=10, color='red', fontweight='bold')
    for gx in np.arange(12, 210, 24):
        ax2.plot(gx, -1, '^', color=NAU_GOLD, markersize=8)
    ax2.text(108, -2.5, 'Thickness gauges every 24"', ha="center",
             fontsize=9, color=NAU_GOLD)
    ax2.set_title("Side View - Application Direction", fontsize=11,
                  fontweight='bold', color=NAU_BLUE)
    ax2.grid(True, alpha=0.15)

    ax3 = fig.add_axes([0.68, 0.10, 0.28, 0.78])
    ax3.axis('off')
    notes = [
        "FIRST LIFT NOTES", "",
        "- Target thickness: 0.20\"",
        "- Mix batch size: ~2 gallons",
        "- Working time: 45 min/batch",
        "- Apply with rubber float", "",
        "APPLICATION ORDER:",
        "1. Keel centerline first",
        "2. Work up both sides equally",
        "3. Finish at gunwale edge",
        "4. Check thickness at every",
        "   gauge point before moving on", "",
        "ENVIRONMENTAL:",
        "- Temperature: 65-80 deg F",
        "- Humidity: >50% preferred",
        "- No direct sunlight", "",
        "QUALITY CHECK:",
        "- No voids or bare spots",
        "- Uniform gray color",
        "- Thickness: 0.20\" +/-0.05\"",
    ]
    for i, line in enumerate(notes):
        weight = 'bold' if line.isupper() or line == '' else 'normal'
        color = NAU_BLUE if line.isupper() else DARK_GRAY
        ax3.text(0.05, 0.97 - i * 0.038, line, fontsize=10,
                 fontweight=weight, color=color, transform=ax3.transAxes,
                 verticalalignment='top', fontfamily='monospace')

    out = os.path.join(OUTPUT_DIR, 'sheet_12_concrete_lift1.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out


# ===================================================================
# SHEET 13 - Mesh + Second Lift (0.30")
# ===================================================================
def sheet_13_concrete_lift2():
    """Second lift with basalt mesh - 0.30 inch over mesh."""
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    draw_title_block(fig, 13, 'Mesh Placement & Second Lift (0.30")')

    ax = fig.add_axes([0.08, 0.35, 0.55, 0.53])
    xs_mold, ys_mold = _hull_curve(16, 100)
    ax.fill(xs_mold, ys_mold, color=FOAM_COLOR, alpha=0.4, label='Foam mold')
    ax.plot(xs_mold, ys_mold, color=DARK_GRAY, lw=1.5)

    s1 = 0.96
    xs1 = xs_mold * s1
    ys1 = ys_mold * s1 + 0.3
    ax.fill(xs1, ys1, color=CONCRETE_GRAY, alpha=0.4, label='Lift 1 (0.20")')
    ax.plot(xs1, ys1, color=MED_GRAY, lw=1.5)

    s_m = 0.93
    xs_m = xs_mold * s_m
    ys_m = ys_mold * s_m + 0.5
    ax.plot(xs_m, ys_m, color=MESH_COLOR, lw=3, linestyle='--', label='Basalt mesh')

    s2 = 0.90
    xs2 = xs_mold * s2
    ys2 = ys_mold * s2 + 0.7
    ax.fill(xs2, ys2, color=CONCRETE_GRAY, alpha=0.6, label='Lift 2 (0.30")')
    ax.plot(xs2, ys2, color=NAU_BLUE, lw=2)

    ax.annotate("Gunwale thickening\n0.625\"-0.75\"",
                 xy=(15, ys_mold[-5]),
                 xytext=(18, ys_mold[-5] + 3),
                 fontsize=9, fontweight='bold', color='red',
                 arrowprops=dict(arrowstyle='->', color='red', lw=1.5))

    ax.text(0, max(ys2) * 0.5, "Press mesh into\nwet Lift 1",
            ha='center', fontsize=9, color=MESH_COLOR, fontweight='bold',
            bbox=dict(fc='white', ec=MESH_COLOR, boxstyle='round,pad=0.2'))

    ax.set_aspect('equal')
    ax.legend(loc='upper right', fontsize=9)
    ax.set_title("Cross-Section: All Layers at Midship (St 16)",
                 fontsize=12, fontweight='bold', color=NAU_BLUE)
    ax.grid(True, alpha=0.2)

    # Wall cross-section detail
    ax_wall = fig.add_axes([0.08, 0.08, 0.35, 0.22])
    ax_wall.set_xlim(0, 12)
    ax_wall.set_ylim(0, 5)
    ax_wall.set_aspect('equal')
    layers_wall = [
        ("Foam mold (removed later)", FOAM_COLOR, 1.0),
        ("PVA release", "#87CEEB", 0.15),
        ("Lift 1 - 0.20\"", CONCRETE_GRAY, 0.8),
        ("Basalt mesh", MESH_COLOR, 0.15),
        ("Lift 2 - 0.30\"", CONCRETE_GRAY, 1.2),
    ]
    y_w = 0
    for lbl, clr, th in layers_wall:
        ax_wall.add_patch(Rectangle((0, y_w), 12, th,
                                     fc=clr, ec=DARK_GRAY, lw=1))
        ax_wall.text(6, y_w + th / 2, lbl, ha='center', va='center',
                     fontsize=7, fontweight='bold')
        y_w += th
    ax_wall.text(6, y_w + 0.3,
                 "Total wall: 0.50\" (concrete only)",
                 ha='center', fontsize=9, fontweight='bold', color=NAU_BLUE)
    ax_wall.set_title("Wall Cross-Section Detail", fontsize=10,
                      fontweight='bold', color=NAU_BLUE)
    ax_wall.set_yticks([])
    ax_wall.set_xticks([])

    ax_n = fig.add_axes([0.68, 0.10, 0.28, 0.78])
    ax_n.axis('off')
    notes = [
        "SECOND LIFT NOTES", "",
        "- Mesh into wet Lift 1",
        "- Overlap mesh seams 3\" min",
        "- Lift 2 thickness: 0.30\"",
        "- Total wall: 0.50\"", "",
        "GUNWALE THICKENING:",
        "- Build up to 0.625-0.75\"",
        "- Extra mesh strip at gunwale",
        "- Smooth transition to wall", "",
        "TROWEL FINISHING:",
        "- Rubber float for interior",
        "- Smooth, no ridges",
        "- Wet trowel for final pass", "",
        "TIMING:",
        "- Mesh within 30 min of Lift 1",
        "- Lift 2 within 15 min of mesh",
        "- Finish within working time",
    ]
    for i, line in enumerate(notes):
        weight = 'bold' if line.isupper() or line == '' else 'normal'
        color = NAU_BLUE if line.isupper() else DARK_GRAY
        ax_n.text(0.05, 0.97 - i * 0.04, line, fontsize=10,
                  fontweight=weight, color=color, transform=ax_n.transAxes,
                  verticalalignment='top', fontfamily='monospace')

    out = os.path.join(OUTPUT_DIR, 'sheet_13_concrete_lift2.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out


# ===================================================================
# SHEET 14 - Curing Setup
# ===================================================================
def sheet_14_curing():
    """Curing setup: plastic tent, misting schedule, temperature control."""
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    draw_title_block(fig, 14, "Curing Setup & Schedule")

    ax = fig.add_axes([0.08, 0.40, 0.84, 0.48])
    ax.set_xlim(-20, 240)
    ax.set_ylim(-10, 50)
    ax.set_aspect('equal')
    ax.add_patch(Rectangle((0, 0), 216, 3, fc=MESH_COLOR, ec=DARK_GRAY, lw=2))
    ax.text(108, 1.5, "STRONGBACK", ha="center", va="center",
             fontsize=9, color=WHITE, fontweight='bold')

    stations_x = np.array([s * 216 / 32 for s in range(33)])
    depths = np.array([STATIONS[s][1] for s in range(33)])
    ax.fill_between(stations_x, 3, depths * 0.9 + 3, color=CONCRETE_GRAY, alpha=0.4)
    ax.plot(stations_x, depths * 0.9 + 3, color=NAU_BLUE, lw=2)
    ax.text(108, 10, "CANOE HULL", ha="center", fontsize=10,
            fontweight='bold', color=NAU_BLUE)

    tent_x = np.array([-10, 0, 30, 60, 108, 156, 186, 216, 226])
    tent_y = np.array([0, 5, 30, 40, 45, 40, 30, 5, 0])
    ax.plot(tent_x, tent_y, color='green', lw=2.5, linestyle='--')
    ax.fill_between(tent_x, tent_y, alpha=0.05, color='green')
    ax.text(108, 42, "PLASTIC SHEETING TENT", ha="center", fontsize=11,
            fontweight='bold', color='green')

    spray_x = [54, 108, 162]
    for sx in spray_x:
        ax.annotate('', xy=(sx, 25), xytext=(sx, 38),
                     arrowprops=dict(arrowstyle='->', color='blue', lw=2))
        ax.plot(sx, 39, 'o', color='blue', markersize=10)
        ax.text(sx, 39, 'S', ha='center', va='center', fontsize=7,
                color='white', fontweight='bold')
    ax.text(108, 47, "Misting spray positions (3 locations)",
            ha='center', fontsize=9, color='blue', fontstyle='italic')

    for tx in [36, 180]:
        ax.plot(tx, 8, 's', color='red', markersize=10)
        ax.text(tx, 6, 'T', fontsize=8, ha='center', color='red', fontweight='bold')
    ax.text(216 + 5, 8, "T = Thermometer", fontsize=8, color="red", ha="left")
    ax.set_title("Side View: Curing Tent Setup", fontsize=12,
                 fontweight='bold', color=NAU_BLUE)
    ax.grid(True, alpha=0.15)

    # 7-day calendar
    ax_cal = fig.add_axes([0.08, 0.08, 0.50, 0.28])
    ax_cal.set_xlim(0, 8)
    ax_cal.set_ylim(0, 4)
    ax_cal.axis('off')
    ax_cal.set_title("7-Day Curing Schedule", fontsize=12,
                     fontweight='bold', color=NAU_BLUE)
    days = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7']
    for i, day in enumerate(days):
        x = i + 0.5
        ax_cal.add_patch(FancyBboxPatch((x - 0.4, 1.0), 0.8, 2.2,
                                         boxstyle="round,pad=0.05",
                                         fc=LIGHT_GRAY if i < 3 else '#E8F5E9',
                                         ec=NAU_BLUE, lw=1.5))
        ax_cal.text(x, 3.0, day, ha='center', fontsize=8, fontweight='bold',
                    color=NAU_BLUE)
        ax_cal.text(x, 2.5, "Mist\n6AM", ha="center", fontsize=7, color="blue")
        ax_cal.text(x, 1.7, "Mist\n6PM", ha="center", fontsize=7, color="blue")
        if i < 3:
            ax_cal.text(x, 1.2, "CRITICAL", ha="center", fontsize=6,
                        color='red', fontweight='bold')
    ax_cal.text(4, 0.5, "Mist every 12 hours  |  Keep tent sealed between misting",
                ha='center', fontsize=9, color=DARK_GRAY, fontstyle='italic')

    ax_temp = fig.add_axes([0.62, 0.08, 0.34, 0.28])
    ax_temp.axis('off')
    temp_notes = [
        "TEMPERATURE CONTROL", "",
        "Acceptable range: 60-80 deg F", "",
        "- Below 60F: Add space heater",
        "  inside tent (not on hull)",
        "- Above 80F: Increase misting",
        "  frequency to every 8 hrs",
        "- Record temp at each misting", "",
        "DO NOT REMOVE TENT",
        "FOR 7 FULL DAYS",
    ]
    for i, line in enumerate(temp_notes):
        weight = 'bold' if line.isupper() else 'normal'
        color = 'red' if 'DO NOT' in line else (NAU_BLUE if line.isupper() else DARK_GRAY)
        ax_temp.text(0.05, 0.95 - i * 0.08, line, fontsize=10,
                     fontweight=weight, color=color, transform=ax_temp.transAxes,
                     verticalalignment='top')

    out = os.path.join(OUTPUT_DIR, 'sheet_14_curing.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out


# ===================================================================
# SHEET 15 - Demolding Procedure
# ===================================================================
def sheet_15_demolding():
    """Demolding: person positions, sequence, support cradle."""
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    draw_title_block(fig, 15, "Demolding Procedure")

    ax = fig.add_axes([0.08, 0.45, 0.84, 0.43])
    ax.set_xlim(-30, 250)
    ax.set_ylim(-30, 30)
    ax.set_aspect('equal')
    stations_x = np.array([s * 216 / 32 for s in range(33)])
    half_beams = np.array([STATIONS[s][0] for s in range(33)])
    ax.fill_between(stations_x, -half_beams, half_beams,
                     color=CONCRETE_GRAY, alpha=0.3, edgecolor=NAU_BLUE, lw=2)
    ax.text(108, 0, "HULL (top view)", ha="center", va="center",
            fontsize=11, fontweight='bold', color=NAU_BLUE)

    persons = [
        (20, 22, "P1\nBow"),
        (196, 22, "P2\nStern"),
        (72, 22, "P3\nPort Fwd"),
        (144, 22, "P4\nPort Aft"),
        (72, -22, "P5\nStbd Fwd"),
        (144, -22, "P6\nStbd Aft"),
    ]
    for px, py, lbl in persons:
        ax.add_patch(Circle((px, py), 5, fc=NAU_GOLD, ec=DARK_GRAY, lw=2, zorder=5))
        ax.text(px, py, lbl, ha='center', va='center', fontsize=7,
                fontweight='bold', zorder=6)
        dy = -1 if py > 0 else 1
        ax.annotate('', xy=(px, py + dy * 8), xytext=(px, py + dy * 5),
                     arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
    ax.set_title("Top View: 6 Person Positions for Demolding",
                 fontsize=12, fontweight='bold', color=NAU_BLUE)
    ax.grid(True, alpha=0.15)

    ax2 = fig.add_axes([0.08, 0.08, 0.50, 0.32])
    ax2.set_xlim(-10, 230)
    ax2.set_ylim(-15, 25)
    ax2.set_aspect('equal')
    ax2.axis('off')
    steps = [
        (10, 18, "1) Remove bow\n   foam first"),
        (70, 18, "2) Work toward\n   midship"),
        (140, 18, "3) Lift & flip\n   (6 people)"),
        (200, 18, "4) Set in cradle"),
    ]
    for i, (sx, sy, txt) in enumerate(steps):
        ax2.add_patch(FancyBboxPatch((sx - 25, sy - 8), 50, 16,
                                      boxstyle="round,pad=0.3",
                                      fc=LIGHT_GRAY, ec=NAU_BLUE, lw=2))
        ax2.text(sx, sy, txt, ha='center', va='center',
                 fontsize=9, fontweight='bold', color=DARK_GRAY)
        if i < len(steps) - 1:
            ax2.annotate('', xy=(steps[i + 1][0] - 25, sy),
                         xytext=(sx + 25, sy),
                         arrowprops=dict(arrowstyle='->', color=NAU_BLUE, lw=2))

    ax2.add_patch(Rectangle((160, -12), 60, 3, fc=MESH_COLOR, ec=DARK_GRAY, lw=2))
    ax2.text(190, -10.5, "SUPPORT CRADLE", ha="center", va="center",
             fontsize=8, color=WHITE, fontweight='bold')
    ax2.text(190, -14, '60" long x 20" wide x 12" tall',
             ha='center', fontsize=8, color=DARK_GRAY)
    ax2.set_title("Demolding Sequence", fontsize=11,
                  fontweight='bold', color=NAU_BLUE)

    ax3 = fig.add_axes([0.62, 0.08, 0.34, 0.32])
    ax3.axis('off')
    wt_notes = [
        "WEIGHT DISTRIBUTION", "",
        "Estimated hull: ~174 lbs",
        "Per person: ~29 lbs", "",
        "LIFTING NOTES:",
        "- Lift on count of 3",
        "- Keep hull level",
        "- Bow/stern persons",
        "  guide, not lift",
        "- Support at gunwale only", "",
        "CRADLE DIMENSIONS:",
        "- Length: 60\"",
        "- Width: 20\"",
        "- Height: 12\"",
        "- Padded contact points",
    ]
    for i, line in enumerate(wt_notes):
        weight = 'bold' if line.isupper() else 'normal'
        color = NAU_BLUE if line.isupper() else DARK_GRAY
        ax3.text(0.05, 0.95 - i * 0.055, line, fontsize=10,
                 fontweight=weight, color=color, transform=ax3.transAxes,
                 verticalalignment='top')

    out = os.path.join(OUTPUT_DIR, 'sheet_15_demolding.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out


# ===================================================================
# SHEET 16 - Finishing & Graphics
# ===================================================================
def sheet_16_finishing():
    """Finishing, graphics layout, sanding/sealer schedule."""
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    draw_title_block(fig, 16, "Finishing & Graphics")

    ax = fig.add_axes([0.08, 0.50, 0.84, 0.38])
    ax.set_xlim(-5, 220)
    ax.set_ylim(-5, 25)
    ax.set_aspect('equal')
    stations_x = np.array([s * 216 / 32 for s in range(33)])
    depths = np.array([STATIONS[s][1] for s in range(33)])
    sheer = depths * 0.9 + 2
    keel = np.full(33, 2.0)
    ax.fill_between(stations_x, keel, sheer, color=CONCRETE_GRAY, alpha=0.3)
    ax.plot(stations_x, sheer, color=NAU_BLUE, lw=2)
    ax.plot(stations_x, keel, color=NAU_BLUE, lw=2)

    zones = [
        (0, 54, "BOW\nGRAPHICS", NAU_GOLD),
        (54, 162, "TEAM NAME / SCHOOL LOGO\nNAU LUMBERJACKS", NAU_BLUE),
        (162, 216, "STERN\nGRAPHICS", NAU_GOLD),
    ]
    for x1, x2, label, clr in zones:
        mid = (x1 + x2) / 2
        mid_st = int(mid * 32 / 216)
        y_mid = (sheer[mid_st] + keel[mid_st]) / 2
        ax.axvline(x1, color=clr, lw=1.5, linestyle=':', alpha=0.7)
        ax.axvline(x2, color=clr, lw=1.5, linestyle=':', alpha=0.7)
        ax.text(mid, y_mid, label, ha='center', va='center',
                fontsize=10, fontweight='bold', color=clr,
                bbox=dict(fc='white', ec=clr, alpha=0.8, boxstyle='round,pad=0.3'))
    ax.set_title("Side View: Graphics Layout", fontsize=12,
                 fontweight='bold', color=NAU_BLUE)
    ax.grid(True, alpha=0.15)

    ax2 = fig.add_axes([0.08, 0.08, 0.40, 0.36])
    ax2.axis('off')
    ax2.set_title("Sanding & Sealer Schedule", fontsize=12,
                  fontweight='bold', color=NAU_BLUE)
    schedule = [
        ("INTERIOR SANDING", ""),
        ("  1. 120-grit pass", "Remove surface imperfections"),
        ("  2. 220-grit pass", "Smooth finish"),
        ("", ""),
        ("EXTERIOR SANDING", ""),
        ("  1. 220-grit only", "Light touch, don't thin wall"),
        ("", ""),
        ("SEALER APPLICATION", ""),
        ("  1. Coat 1 (exterior)", "Even, thin coat"),
        ("  2. Dry 24 hours", ""),
        ("  3. Coat 2 (exterior)", "Perpendicular to coat 1"),
        ("  4. Dry 24 hours", ""),
        ("", ""),
        ("PAINT (GRAPHICS)", ""),
        ("  1. Mask layout", "Use painter's tape"),
        ("  2. NAU Blue base", "2 coats, 4 hrs between"),
        ("  3. NAU Gold accents", "1 coat, detail brush"),
        ("  4. Clear seal over paint", "Protect graphics"),
    ]
    for i, (step, note) in enumerate(schedule):
        weight = 'bold' if step.strip().isupper() else 'normal'
        color = NAU_BLUE if step.strip().isupper() else DARK_GRAY
        ax2.text(0.02, 0.95 - i * 0.05, step, fontsize=9,
                 fontweight=weight, color=color, transform=ax2.transAxes,
                 verticalalignment='top')
        if note:
            ax2.text(0.65, 0.95 - i * 0.05, note, fontsize=8,
                     color=MED_GRAY, transform=ax2.transAxes,
                     verticalalignment='top', fontstyle='italic')

    ax3 = fig.add_axes([0.55, 0.08, 0.40, 0.36])
    ax3.axis('off')
    ax3.add_patch(FancyBboxPatch((0.1, 0.5), 0.8, 0.4,
                                  boxstyle="round,pad=0.05",
                                  fc=LIGHT_GRAY, ec=NAU_BLUE, lw=3,
                                  transform=ax3.transAxes))
    ax3.text(0.5, 0.78, "FINAL WEIGHT TARGET", ha="center",
             fontsize=14, fontweight='bold', color=NAU_BLUE,
             transform=ax3.transAxes)
    ax3.text(0.5, 0.62, "174 lbs +/- 15 lbs", ha="center",
             fontsize=20, fontweight='bold', color='red',
             transform=ax3.transAxes)

    color_swatches = [
        ("NAU Blue", NAU_BLUE),
        ("NAU Gold", NAU_GOLD),
        ("Concrete Gray", CONCRETE_GRAY),
    ]
    for i, (name, clr) in enumerate(color_swatches):
        y_pos = 0.35 - i * 0.12
        ax3.add_patch(FancyBboxPatch((0.15, y_pos), 0.15, 0.08,
                                      boxstyle="round,pad=0.02",
                                      fc=clr, ec=DARK_GRAY, lw=1,
                                      transform=ax3.transAxes))
        ax3.text(0.35, y_pos + 0.04, f"  {name}  ({clr})", fontsize=10,
                 va='center', color=DARK_GRAY, transform=ax3.transAxes)

    out = os.path.join(OUTPUT_DIR, 'sheet_16_finishing.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out


# ===================================================================
# SHEET 17 - Hull Lines Plan
# ===================================================================
def sheet_17_lines_plan():
    """Traditional 3-view naval architecture lines plan."""
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    draw_title_block(fig, 17, "Hull Lines Plan")

    # Body Plan (port side sections)
    ax_body = fig.add_axes([0.08, 0.62, 0.84, 0.28])
    ax_body.set_title("Body Plan (Port Side Sections)", fontsize=12,
                      fontweight='bold', color=NAU_BLUE)
    for s in range(0, 17):
        hb, d = STATIONS[s]
        if hb == 0 and d == 0:
            continue
        if s in DXF_DATA and len(DXF_DATA[s]) > 2:
            coords = np.array(DXF_DATA[s])
            xs_p = coords[:, 0]
            ys_p = coords[:, 1]
            mask = xs_p >= 0
            ax_body.plot(xs_p[mask], ys_p[mask], lw=1.5,
                         label=f'St {s}' if s % 2 == 0 else None)
        else:
            xs_h, ys_h = _hull_curve(s, 50)
            mask = xs_h >= 0
            ax_body.plot(xs_h[mask], ys_h[mask], lw=1.5,
                         label=f'St {s}' if s % 2 == 0 else None)
        ax_body.text(hb + 0.3, d, str(s), fontsize=6, color=MED_GRAY)
    ax_body.axvline(0, color=NAU_BLUE, lw=1, linestyle='-.', alpha=0.5)
    ax_body.text(0.3, -0.5, "CL", fontsize=8, color=NAU_BLUE)
    ax_body.set_xlabel("Half-beam (inches)")
    ax_body.set_ylabel("Depth (inches)")
    ax_body.set_aspect('equal')
    ax_body.legend(loc='upper right', fontsize=7, ncol=3)
    ax_body.grid(True, alpha=0.2)

    # Profile (side view)
    ax_prof = fig.add_axes([0.08, 0.35, 0.84, 0.22])
    ax_prof.set_title("Profile (Side View)", fontsize=12,
                      fontweight='bold', color=NAU_BLUE)
    stations_x = np.array([s * 216 / 32 for s in range(33)])
    depths = np.array([STATIONS[s][1] for s in range(33)])
    ax_prof.plot(stations_x, depths, color=NAU_BLUE, lw=2.5, label='Sheer line')
    ax_prof.axhline(0, color=DARK_GRAY, lw=2, label='Keel line')
    ax_prof.axhline(6.06, color='blue', lw=1.5, linestyle='--', label='DWL (6.06")')
    for s in range(0, 33, 2):
        ax_prof.axvline(stations_x[s], color=MED_GRAY, lw=0.5, alpha=0.3)
        ax_prof.text(stations_x[s], -1.5, str(s), ha='center', fontsize=7,
                     color=MED_GRAY)
    ax_prof.set_xlabel("Length (inches)")
    ax_prof.set_ylabel("Height (inches)")
    ax_prof.legend(loc='upper right', fontsize=9)
    ax_prof.grid(True, alpha=0.2)

    # Half-Breadth Plan (top view)
    ax_hb = fig.add_axes([0.08, 0.08, 0.84, 0.22])
    ax_hb.set_title("Half-Breadth Plan (Top View)", fontsize=12,
                     fontweight='bold', color=NAU_BLUE)
    half_beams = np.array([STATIONS[s][0] for s in range(33)])
    ax_hb.plot(stations_x, half_beams, color=NAU_BLUE, lw=2.5, label='Beam at gunwale')
    ax_hb.fill_between(stations_x, 0, half_beams, color=LIGHT_GRAY, alpha=0.3)
    ax_hb.axhline(0, color=DARK_GRAY, lw=1.5)
    wl_beams = []
    for s in range(33):
        hb, d = STATIONS[s]
        if d == 0:
            wl_beams.append(0)
        else:
            ratio = min(6.06 / d, 1.0)
            wl_beams.append(hb * ratio ** 0.6)
    ax_hb.plot(stations_x, wl_beams, color='blue', lw=1.5, linestyle='--',
               label='Beam at DWL')
    for s in range(0, 33, 2):
        ax_hb.axvline(stations_x[s], color=MED_GRAY, lw=0.5, alpha=0.3)
        ax_hb.text(stations_x[s], -1, str(s), ha='center', fontsize=7,
                   color=MED_GRAY)
    ax_hb.set_xlabel("Length (inches)")
    ax_hb.set_ylabel("Half-beam (inches)")
    ax_hb.legend(loc='upper right', fontsize=9)
    ax_hb.grid(True, alpha=0.2)

    out = os.path.join(OUTPUT_DIR, 'sheet_17_lines_plan.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out


# ===================================================================
# SHEET 18 - Waterline & Load Diagram
# ===================================================================
def sheet_18_waterline():
    """Loaded waterline, freeboard, paddler positions, stability."""
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    draw_title_block(fig, 18, "Waterline & Load Diagram")

    ax = fig.add_axes([0.08, 0.45, 0.84, 0.43])
    ax.set_xlim(-10, 226)
    ax.set_ylim(-5, 25)
    ax.set_aspect('equal')
    stations_x = np.array([s * 216 / 32 for s in range(33)])
    depths = np.array([STATIONS[s][1] for s in range(33)])
    sheer = depths

    ax.axhspan(-5, 6.06, color='#B0E0E6', alpha=0.3)
    ax.axhline(6.06, color='blue', lw=2.5, label='Loaded Waterline (6.06" draft)')
    ax.fill_between(stations_x, 0, sheer, color=CONCRETE_GRAY, alpha=0.3)
    ax.plot(stations_x, sheer, color=NAU_BLUE, lw=2.5)
    ax.plot(stations_x, np.zeros(33), color=DARK_GRAY, lw=2)

    fb_stations = [8, 16, 24]
    for s in fb_stations:
        x = stations_x[s]
        ax.annotate('', xy=(x + 2, 6.06), xytext=(x + 2, sheer[s]),
                     arrowprops=dict(arrowstyle='<->', color='green', lw=2))
        ax.text(x + 4, (6.06 + sheer[s]) / 2,
                f'FB={sheer[s] - 6.06:.1f}"',
                fontsize=8, color='green', fontweight='bold')

    ax.annotate('', xy=(216 + 5, 0), xytext=(216 + 5, 6.06),
                 arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(220, 3, "Draft\n6.06\"", fontsize=9, color="red", fontweight="bold")

    ax.annotate('', xy=(-5, 6.06), xytext=(-5, sheer[16]),
                 arrowprops=dict(arrowstyle='<->', color='green', lw=2))
    ax.text(-8, (6.06 + sheer[16]) / 2, '10.94"',
            fontsize=9, color='green', fontweight='bold', ha='right')

    paddler_x = [54, 88, 128, 162]
    for i, px in enumerate(paddler_x):
        st_idx = int(px * 32 / 216)
        py = sheer[st_idx]
        ax.plot(px, py + 2, 'o', color=NAU_GOLD, markersize=8)
        ax.plot([px, px], [py, py + 1.5], color=NAU_GOLD, lw=2)
        ax.text(px, py + 4, f'P{i + 1}\n175 lb', ha='center', fontsize=7,
                fontweight='bold', color=NAU_GOLD)

    cg_x = 108
    cg_y = 8
    ax.plot(cg_x, cg_y, 'D', color='red', markersize=12, zorder=5)
    ax.text(cg_x + 5, cg_y, 'CG', fontsize=11, fontweight='bold', color='red')
    ax.set_title("Side Profile: Loaded Waterline & Paddler Positions",
                 fontsize=12, fontweight='bold', color=NAU_BLUE)
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.2)
    ax.set_xlabel("Length (inches)")
    ax.set_ylabel("Height (inches)")

    # Stability diagram
    ax2 = fig.add_axes([0.08, 0.08, 0.40, 0.32])
    ax2.set_xlim(-22, 22)
    ax2.set_ylim(-5, 22)
    ax2.set_aspect('equal')
    xs_hull, ys_hull = _hull_curve(16, 80)
    ax2.fill(xs_hull, ys_hull, color=CONCRETE_GRAY, alpha=0.3)
    ax2.plot(xs_hull, ys_hull, color=NAU_BLUE, lw=2)
    ax2.axhline(6.06, color='blue', lw=1.5, linestyle='--')
    ax2.fill_between([-20, 20], [-5, -5], [6.06, 6.06],
                      color='#B0E0E6', alpha=0.2)
    B_y = 3.0
    G_y = 8.0
    M_y = 12.0
    for pt_y, label, clr in [(B_y, 'B', 'blue'), (G_y, 'G', 'red'), (M_y, 'M', 'green')]:
        ax2.plot(0, pt_y, 'o', color=clr, markersize=10, zorder=5)
        ax2.text(1.5, pt_y, label, fontsize=12, fontweight='bold', color=clr)
    ax2.annotate('', xy=(3, M_y), xytext=(3, G_y),
                 arrowprops=dict(arrowstyle='<->', color='green', lw=2.5))
    ax2.text(5, (G_y + M_y) / 2, 'GM', fontsize=11,
             fontweight='bold', color='green')
    ax2.set_title("Stability Diagram (Midship)", fontsize=11,
                  fontweight='bold', color=NAU_BLUE)
    ax2.grid(True, alpha=0.2)

    ax3 = fig.add_axes([0.55, 0.08, 0.40, 0.32])
    ax3.axis('off')
    load_info = [
        "LOAD SUMMARY", "",
        "Hull weight:       ~174 lbs",
        "Crew (4 paddlers):  700 lbs",
        "Total displaced:    874 lbs", "",
        "Draft (loaded):    6.06\"",
        "Freeboard (mid):  10.94\"",
        "Freeboard (min):   >6\"", "",
        "STABILITY:",
        "  B (buoyancy):  ~3.0\" above keel",
        "  G (gravity):   ~8.0\" above keel",
        "  M (metacenter):~12\" above keel",
        "  GM = ~4\" (positive = stable)", "",
        "All 4 paddlers kneeling,",
        "evenly spaced about midship.",
    ]
    for i, line in enumerate(load_info):
        weight = 'bold' if line.isupper() else 'normal'
        color = NAU_BLUE if line.isupper() else DARK_GRAY
        ax3.text(0.05, 0.95 - i * 0.052, line, fontsize=10,
                 fontweight=weight, color=color, transform=ax3.transAxes,
                 verticalalignment='top', fontfamily='monospace')

    out = os.path.join(OUTPUT_DIR, 'sheet_18_waterline.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out


# ===================================================================
# SHEET 19 - QC Inspection Checklist
# ===================================================================
def sheet_19_qc_checklist():
    """Visual QC flowchart with pass/fail at each construction stage."""
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    draw_title_block(fig, 19, "QC Inspection Checklist")

    ax = fig.add_axes([0.04, 0.06, 0.92, 0.82])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 70)
    ax.axis('off')

    stages = [
        ("MOLD ASSEMBLY", [
            "Stations aligned +/-1/8\"",
            "Strongback level +/-1/16\"",
            "All gaps filled",
        ]),
        ("SURFACE PREP", [
            "Fairness: <1/16\" under 4' batten",
            "PVA 2 coats applied",
            "No bare spots",
        ]),
        ("MESH PLACEMENT", [
            "3\" min overlap at seams",
            "Relief cuts at bow/stern",
            "Mesh lies flat, no bunching",
        ]),
        ("LIFT 1 (0.20\")", [
            "Thickness 0.20\" +/-0.05\"",
            "No voids or bare spots",
            "Uniform color/texture",
        ]),
        ("LIFT 2 (0.30\")", [
            "Thickness 0.30\" +/-0.05\"",
            "Gunwale 0.625\"-0.75\"",
            "Smooth trowel finish",
        ]),
        ("CURING", [
            "Tent sealed 7 days",
            "Misted every 12 hrs",
            "Temp 60-80 deg F logged",
        ]),
        ("DEMOLDING", [
            "No cracks or chips",
            "Clean separation from mold",
            "Support in cradle immediately",
        ]),
        ("FINISHING", [
            "Wall thickness +/-0.1\"",
            "Weight 174 +/-15 lbs",
            "Fairness +/-1/16\"",
            "Photo documentation complete",
        ]),
    ]

    n_cols = 4
    box_w = 20
    box_h = 22
    x_margin = 5
    y_top = 63
    y_gap = 30
    x_gap = 24

    for idx, (title, criteria) in enumerate(stages):
        col = idx % n_cols
        row = idx // n_cols
        x = x_margin + col * x_gap
        y = y_top - row * y_gap

        ax.add_patch(FancyBboxPatch((x, y - box_h), box_w, box_h,
                                     boxstyle="round,pad=0.4",
                                     fc=LIGHT_GRAY, ec=NAU_BLUE, lw=2.5))
        ax.text(x + box_w / 2, y - 1.5, title,
                ha='center', va='top', fontsize=10, fontweight='bold',
                color=NAU_BLUE)
        ax.add_patch(Circle((x + 2, y - 2), 1.5,
                             fc=NAU_BLUE, ec=WHITE, lw=1.5, zorder=5))
        ax.text(x + 2, y - 2, str(idx + 1), ha='center', va='center',
                fontsize=9, fontweight='bold', color=WHITE, zorder=6)

        for j, crit in enumerate(criteria):
            cy = y - 6 - j * 3.5
            ax.add_patch(Rectangle((x + 1.5, cy - 0.8), 1.6, 1.6,
                                    fc=WHITE, ec=DARK_GRAY, lw=1))
            ax.text(x + 4.5, cy, crit, fontsize=7.5, va='center',
                    color=DARK_GRAY)

        pf_y = y - box_h + 2.5
        ax.add_patch(FancyBboxPatch((x + 1, pf_y - 1), 8, 2.5,
                                     boxstyle="round,pad=0.15",
                                     fc='#C8E6C9', ec='green', lw=1.5))
        ax.text(x + 5, pf_y + 0.25, "PASS", ha="center", va="center",
                fontsize=8, fontweight='bold', color='green')
        ax.add_patch(FancyBboxPatch((x + 11, pf_y - 1), 8, 2.5,
                                     boxstyle="round,pad=0.15",
                                     fc='#FFCDD2', ec='red', lw=1.5))
        ax.text(x + 15, pf_y + 0.25, "FAIL", ha="center", va="center",
                fontsize=8, fontweight='bold', color='red')

        if idx < len(stages) - 1:
            next_col = (idx + 1) % n_cols
            if next_col > col:
                ax.annotate('', xy=(x + x_gap - 1, y - box_h / 2),
                             xytext=(x + box_w + 0.5, y - box_h / 2),
                             arrowprops=dict(arrowstyle='->', color=NAU_BLUE, lw=2))
            else:
                ax.annotate('', xy=(x_margin + box_w / 2, y - y_gap + box_h / 2 + 1),
                             xytext=(x + box_w / 2, y - box_h - 0.5),
                             arrowprops=dict(arrowstyle='->', color=NAU_BLUE,
                                            lw=2, connectionstyle='arc3,rad=0.3'))

    ax.text(50, 2,
            "PHOTO DOCUMENTATION: Photograph each stage before and after. "
            "Include measurement tools in frame for scale reference.",
            ha='center', fontsize=10, fontstyle='italic', color='red',
            fontweight='bold',
            bbox=dict(fc='#FFF9C4', ec='red', boxstyle='round,pad=0.4'))

    out = os.path.join(OUTPUT_DIR, 'sheet_19_qc_checklist.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out


# ===================================================================
# SHEET 20 - Full Assembly Overview
# ===================================================================
def sheet_20_overview():
    """Isometric-style assembly overview with cross-reference callouts."""
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    draw_title_block(fig, 20, "Full Assembly Overview")

    ax = fig.add_axes([0.06, 0.08, 0.88, 0.80])
    ax.set_xlim(-30, 260)
    ax.set_ylim(-20, 80)
    ax.set_aspect('equal')
    ax.axis('off')

    iso_dx = 0.35
    iso_dy = 0.25
    sb_x, sb_y = 10, 5
    sb_w, sb_h = 216, 6
    depth_3d = 10

    # Front face
    ax.add_patch(Polygon([(sb_x, sb_y), (sb_x + sb_w, sb_y),
                           (sb_x + sb_w, sb_y + sb_h),
                           (sb_x, sb_y + sb_h)],
                          closed=True, fc=MESH_COLOR, ec=DARK_GRAY, lw=2, alpha=0.8))
    # Top face
    ax.add_patch(Polygon([(sb_x, sb_y + sb_h),
                           (sb_x + sb_w, sb_y + sb_h),
                           (sb_x + sb_w + depth_3d * iso_dx,
                            sb_y + sb_h + depth_3d * iso_dy),
                           (sb_x + depth_3d * iso_dx,
                            sb_y + sb_h + depth_3d * iso_dy)],
                          closed=True, fc='#A0784A', ec=DARK_GRAY, lw=1.5, alpha=0.6))
    # Side face
    ax.add_patch(Polygon([(sb_x + sb_w, sb_y),
                           (sb_x + sb_w + depth_3d * iso_dx,
                            sb_y + depth_3d * iso_dy),
                           (sb_x + sb_w + depth_3d * iso_dx,
                            sb_y + sb_h + depth_3d * iso_dy),
                           (sb_x + sb_w, sb_y + sb_h)],
                          closed=True, fc='#8B6D3F', ec=DARK_GRAY, lw=1.5, alpha=0.6))

    stations_x = np.array([s * 216 / 32 for s in range(33)]) + sb_x
    depths = np.array([STATIONS[s][1] for s in range(33)])
    hull_base = sb_y + sb_h + depth_3d * iso_dy * 0.3
    hull_top = hull_base + depths * 0.7

    ax.fill_between(stations_x + depth_3d * iso_dx * 0.3,
                     hull_base, hull_top,
                     color=CONCRETE_GRAY, alpha=0.4)
    ax.plot(stations_x + depth_3d * iso_dx * 0.3, hull_top,
            color=NAU_BLUE, lw=2.5)

    for s in [4, 8, 12, 16, 20, 24, 28]:
        x_s = stations_x[s]
        ax.plot([x_s, x_s], [hull_base, hull_top[s]],
                color=FOAM_COLOR, lw=3, alpha=0.6)
        ax.plot([x_s, x_s + depth_3d * iso_dx * 0.5],
                [hull_top[s], hull_top[s] + depth_3d * iso_dy * 0.3],
                color=FOAM_COLOR, lw=2, alpha=0.4)

    callouts = [
        (1, sb_x + sb_w / 2, sb_y + 3, "Strongback", "SEE SHEET 3",
         sb_x + sb_w / 2, sb_y - 8),
        (2, stations_x[16] + 3, hull_top[16] + 2, "Midship template (St 16)",
         "SEE SHEET 8", stations_x[16] + 25, hull_top[16] + 15),
        (3, stations_x[8] + 3, hull_top[8] + 2, "Bow templates",
         "SEE SHEETS 5-6", stations_x[4], hull_top[4] + 20),
        (4, stations_x[24] + 3, hull_top[24] + 2, "Stern templates",
         "SEE SHEETS 7-8", stations_x[28], hull_top[28] + 20),
        (5, stations_x[12] + 3, hull_base + 3, "Foam gap fill",
         "SEE SHEET 9", stations_x[12] - 20, hull_base - 8),
        (6, stations_x[16] + 3, hull_top[16] - 3, "Surface prep & PVA",
         "SEE SHEET 10", stations_x[16] + 50, hull_top[16] - 5),
        (7, stations_x[10] + 3, hull_top[10] - 2, "Basalt mesh",
         "SEE SHEET 11", stations_x[10] - 30, hull_top[10] + 18),
        (8, stations_x[14], hull_top[14] - 4, "Concrete lifts 1 & 2",
         "SEE SHEETS 12-13", stations_x[14] - 35, hull_top[14] - 12),
        (9, stations_x[20], hull_top[20] + 5, "Curing tent",
         "SEE SHEET 14", stations_x[20] + 40, hull_top[20] + 20),
        (10, stations_x[22], hull_top[22] + 3, "Demold & finish",
         "SEE SHEETS 15-16", stations_x[22] + 45, hull_top[22] + 12),
    ]

    for num, cx, cy, desc, sheet_ref, tx, ty in callouts:
        ax.add_patch(FancyBboxPatch((tx - 18, ty - 4), 36, 9,
                                     boxstyle="round,pad=0.3",
                                     fc=WHITE, ec=NAU_BLUE, lw=1.5,
                                     alpha=0.92, zorder=8))
        ax.add_patch(Circle((tx - 14, ty + 0.5), 2.5,
                             fc=NAU_BLUE, ec=WHITE, lw=1, zorder=9))
        ax.text(tx - 14, ty + 0.5, str(num), ha='center', va='center',
                fontsize=9, fontweight='bold', color=WHITE, zorder=10)
        ax.text(tx - 10, ty + 2, desc, fontsize=8, fontweight='bold',
                color=DARK_GRAY, zorder=9)
        ax.text(tx - 10, ty - 1.5, sheet_ref, fontsize=8, fontstyle='italic',
                color=NAU_BLUE, fontweight='bold', zorder=9)
        ax.annotate('', xy=(cx, cy), xytext=(tx - 14, ty - 3.5),
                     arrowprops=dict(arrowstyle='->', color=NAU_BLUE,
                                    lw=1, connectionstyle='arc3,rad=0.2'),
                     zorder=7)

    ax.text(130, 75, "NAU ASCE CONCRETE CANOE 2026 -- ASSEMBLY OVERVIEW",
            ha='center', fontsize=16, fontweight='bold', color=NAU_BLUE,
            bbox=dict(fc=LIGHT_GRAY, ec=NAU_BLUE, lw=2,
                      boxstyle='round,pad=0.5'))
    ax.text(130, 70, "Assembly sequence numbered 1-10. See individual sheets for details.",
            ha='center', fontsize=11, color=MED_GRAY, fontstyle='italic')

    out = os.path.join(OUTPUT_DIR, 'sheet_20_overview.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out


# ###################################################################
#  MAIN ENTRY POINT
# ###################################################################
if __name__ == "__main__":
    print("=" * 70)
    print("  NAU ASCE Concrete Canoe 2026 - Construction Shop Drawings")
    print('  Design A: 192" x 32" x 17" | Female Mold | V-Bottom 15 deg')
    print("=" * 70)
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"  DPI: {DPI}")
    print(f"  Sheet size: {SHEET_W_IN}\" x {SHEET_H_IN}\" (ANSI D landscape)")
    print(f"  DXF data: {'Loaded' if DXF_COORDS else 'Not found (using parametric)'}")
    print(f"  Stations loaded: {len(STATION_HALF_BEAM)} (half-beams), "
          f"{len(STATION_DEPTH)} (depths)")
    print()

    target_sheet = None
    if "--sheet" in sys.argv:
        idx = sys.argv.index("--sheet")
        if idx + 1 < len(sys.argv):
            target_sheet = int(sys.argv[idx + 1])

    sheet_functions = {
        1: sheet_01_title,
        2: sheet_02_bom,
        3: sheet_03_strongback,
        4: sheet_04_foam_nesting,
        5: sheet_05_templates_1_4,
        6: sheet_06_templates_5_8,
        7: sheet_07_templates_9_12,
        8: sheet_08_templates_13_16,
        9: sheet_09_mold_assembly,
        10: sheet_10_surface_prep,
        11: sheet_11_mesh_cutting,
        12: sheet_12_concrete_lift1,
        13: sheet_13_concrete_lift2,
        14: sheet_14_curing,
        15: sheet_15_demolding,
        16: sheet_16_finishing,
        17: sheet_17_lines_plan,
        18: sheet_18_waterline,
        19: sheet_19_qc_checklist,
        20: sheet_20_overview,
    }

    if target_sheet:
        if target_sheet in sheet_functions:
            print(f"  Generating sheet {target_sheet} only...")
            sheet_functions[target_sheet]()
        else:
            print(f"  [ERROR] Sheet {target_sheet} not implemented")
            sys.exit(1)
    else:
        for num in sorted(sheet_functions.keys()):
            print(f"  Generating sheet {num}/20...")
            sheet_functions[num]()

    print()
    print("=" * 70)
    print("  Generation complete! 20 sheets generated.")
    print(f"  Files saved to: {OUTPUT_DIR}")
    print("=" * 70)
