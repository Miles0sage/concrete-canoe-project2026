#!/usr/bin/env python3
"""
Generate professional engineering report drawings for NAU ASCE 2026 Concrete Canoe.
Matches the style of the 2024 NAU report (Figures 1, 2, 8, 9).

Design A: 192" x 32" x 17", t=0.5", ~171 lbs hull weight
Crew: 4 paddlers @ 175 lbs = 700 lbs
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

# Design A parameters
LENGTH_IN = 192
BEAM_IN = 32
DEPTH_IN = 17
THICKNESS_IN = 0.5
HULL_WEIGHT_LBS = 171  # estimated from calculator
CREW_WEIGHT_LBS = 700  # 4 paddlers
FLEXURAL_STRENGTH_PSI = 1500
CANOE_NAME = "USS Lumberjack"
TEAM = "NAU Concrete Canoe 2026"

OUT_DIR = Path(__file__).parent.parent / "reports" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def draw_title_block(ax, fig, title, sheet_num, total_sheets=5, scale="NTS"):
    """Draw a professional engineering title block in the lower-right."""
    # Title block dimensions (in axes fraction coords)
    tb_w, tb_h = 0.42, 0.22
    tb_x, tb_y = 0.97 - tb_w, 0.03

    # Background
    tb = FancyBboxPatch(
        (tb_x, tb_y), tb_w, tb_h,
        boxstyle="square,pad=0",
        transform=ax.transAxes,
        facecolor="white", edgecolor="black", linewidth=1.5,
        zorder=10,
    )
    ax.add_patch(tb)

    # Divider lines
    for frac in [0.55, 0.75]:
        y_line = tb_y + tb_h * frac
        ax.plot([tb_x, tb_x + tb_w], [y_line, y_line],
                'k-', lw=0.8, transform=ax.transAxes, zorder=11)

    # Vertical divider in bottom section
    x_mid = tb_x + tb_w * 0.5
    ax.plot([x_mid, x_mid], [tb_y, tb_y + tb_h * 0.55],
            'k-', lw=0.8, transform=ax.transAxes, zorder=11)

    # Text
    props = dict(transform=ax.transAxes, zorder=12, fontfamily='sans-serif')

    # Top row: team name
    ax.text(tb_x + tb_w / 2, tb_y + tb_h * 0.88, "CONCRETE CANOE",
            ha='center', va='center', fontsize=11, fontweight='bold', **props)

    # Middle row: title
    ax.text(tb_x + tb_w / 2, tb_y + tb_h * 0.65, title,
            ha='center', va='center', fontsize=9, fontweight='bold', **props)

    # Bottom-left quadrant
    ax.text(tb_x + tb_w * 0.25, tb_y + tb_h * 0.40,
            f"NAU ASCE 2026", ha='center', va='center', fontsize=7, **props)
    ax.text(tb_x + tb_w * 0.25, tb_y + tb_h * 0.27,
            f"{CANOE_NAME}", ha='center', va='center', fontsize=7, style='italic', **props)
    ax.text(tb_x + tb_w * 0.25, tb_y + tb_h * 0.12,
            f"Design A: {LENGTH_IN}\"x{BEAM_IN}\"x{DEPTH_IN}\"",
            ha='center', va='center', fontsize=6, **props)

    # Bottom-right quadrant
    ax.text(tb_x + tb_w * 0.75, tb_y + tb_h * 0.40,
            f"SCALE: {scale}", ha='center', va='center', fontsize=7, **props)
    ax.text(tb_x + tb_w * 0.75, tb_y + tb_h * 0.25,
            f"SHEET {sheet_num} OF {total_sheets}",
            ha='center', va='center', fontsize=8, fontweight='bold', **props)
    ax.text(tb_x + tb_w * 0.75, tb_y + tb_h * 0.10,
            "DWG: A", ha='center', va='center', fontsize=7, **props)


def draw_border(ax):
    """Draw engineering drawing border with zone markers."""
    for spine in ax.spines.values():
        spine.set_linewidth(2)
        spine.set_color('black')

    # Zone markers
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    xr = xlim[1] - xlim[0]
    yr = ylim[1] - ylim[0]

    for i, label in enumerate(['2', '1']):
        x = xlim[0] + xr * (0.25 + 0.5 * i)
        ax.text(x, ylim[1] + yr * 0.02, label, ha='center', va='bottom',
                fontsize=10, fontweight='bold', clip_on=False)
        ax.text(x, ylim[0] - yr * 0.02, label, ha='center', va='top',
                fontsize=10, fontweight='bold', clip_on=False)

    for i, label in enumerate(['A', 'B']):
        y = ylim[0] + yr * (0.25 + 0.5 * i)
        ax.text(xlim[0] - xr * 0.02, y, label, ha='right', va='center',
                fontsize=10, fontweight='bold', clip_on=False)
        ax.text(xlim[1] + xr * 0.02, y, label, ha='left', va='center',
                fontsize=10, fontweight='bold', clip_on=False)


def hull_halfwidth(x_frac):
    """Half-width of hull at fractional position (0=bow, 1=stern). Returns fraction of max beam."""
    # Symmetric hull with fine bow, full midship, moderate stern
    return np.sin(np.pi * x_frac) ** 0.6


def hull_depth_at(x_frac):
    """Depth of hull at fractional position. Slightly shallower at ends."""
    return 0.4 + 0.6 * np.sin(np.pi * x_frac) ** 0.5


# ─────────────────────────────────────────────────────────────
# DRAWING 1: Section Breakdown (like their Figure 8)
# ─────────────────────────────────────────────────────────────
def draw_section_breakdown():
    fig = plt.figure(figsize=(14, 10), facecolor='white')

    # Main axes for the drawing area
    ax = fig.add_axes([0.06, 0.06, 0.88, 0.88])
    ax.set_xlim(-20, 220)
    ax.set_ylim(-80, 90)
    ax.set_aspect('equal')
    ax.axis('off')

    # ── Plan View (top) ──
    x_hull = np.linspace(0, LENGTH_IN, 200)
    x_frac = x_hull / LENGTH_IN
    hw = hull_halfwidth(x_frac) * BEAM_IN / 2

    y_offset = 45
    ax.fill_between(x_hull, y_offset - hw, y_offset + hw,
                     color='#d4e6f1', alpha=0.5, edgecolor='black', linewidth=1.5)
    ax.plot(x_hull, y_offset + hw, 'k-', lw=1.5)
    ax.plot(x_hull, y_offset - hw, 'k-', lw=1.5)
    # Centerline
    ax.plot([0, LENGTH_IN], [y_offset, y_offset], 'k--', lw=0.5, alpha=0.5)
    ax.text(LENGTH_IN / 2, y_offset + BEAM_IN / 2 + 8, "PLAN VIEW",
            ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Overall dimension lines
    dim_y = y_offset + BEAM_IN / 2 + 3
    ax.annotate('', xy=(LENGTH_IN, dim_y), xytext=(0, dim_y),
                arrowprops=dict(arrowstyle='<->', color='black', lw=1))
    ax.text(LENGTH_IN / 2, dim_y + 1.5, f'{LENGTH_IN:.0f}"',
            ha='center', va='bottom', fontsize=8, fontweight='bold')

    # Beam dimension at midship
    mid_x = LENGTH_IN / 2
    mid_hw = hull_halfwidth(0.5) * BEAM_IN / 2
    ax.annotate('', xy=(mid_x + 15, y_offset + mid_hw),
                xytext=(mid_x + 15, y_offset - mid_hw),
                arrowprops=dict(arrowstyle='<->', color='black', lw=1))
    ax.text(mid_x + 18, y_offset, f'{BEAM_IN:.0f}"',
            ha='left', va='center', fontsize=7)

    # Section cut lines
    stations = [0.15, 0.5, 0.85]
    labels = ['A', 'B', 'C']
    colors = ['#e74c3c', '#2980b9', '#27ae60']
    for st, lbl, col in zip(stations, labels, colors):
        sx = st * LENGTH_IN
        shw = hull_halfwidth(st) * BEAM_IN / 2 + 5
        ax.plot([sx, sx], [y_offset - shw, y_offset + shw],
                color=col, lw=2, ls='--')
        ax.text(sx, y_offset + shw + 2, lbl, ha='center', va='bottom',
                fontsize=10, fontweight='bold', color=col)
        ax.text(sx, y_offset - shw - 2, lbl, ha='center', va='top',
                fontsize=10, fontweight='bold', color=col)

    # ── Cross-Sections (bottom row) ──
    section_y_offset = -30
    section_spacing = 65
    section_x_starts = [10, 10 + section_spacing, 10 + 2 * section_spacing]

    for i, (st, lbl, col) in enumerate(zip(stations, labels, colors)):
        cx = section_x_starts[i]
        hw_st = hull_halfwidth(st) * BEAM_IN / 2
        d_st = hull_depth_at(st) * DEPTH_IN

        # U-shaped cross-section
        t = THICKNESS_IN * 8  # exaggerate thickness for visibility
        # Outer profile
        x_outer = np.array([-hw_st, -hw_st, hw_st, hw_st])
        y_outer = np.array([0, -d_st, -d_st, 0])
        # Inner profile
        x_inner = np.array([-(hw_st - t), -(hw_st - t), (hw_st - t), (hw_st - t)])
        y_inner = np.array([0, -(d_st - t), -(d_st - t), 0])

        # Draw filled U-shape
        from matplotlib.patches import Polygon
        outer = list(zip(x_outer + cx + hw_st, y_outer + section_y_offset))
        inner = list(zip(x_inner + cx + hw_st, y_inner + section_y_offset))
        # Close the U: outer path forward, inner path reversed
        verts = outer + inner[::-1]
        poly = Polygon(verts, closed=True, facecolor='#bdc3c7', edgecolor='black', lw=1.2)
        ax.add_patch(poly)

        # Dimension: width
        ax.annotate('', xy=(cx + 2 * hw_st, section_y_offset - d_st - 5),
                    xytext=(cx, section_y_offset - d_st - 5),
                    arrowprops=dict(arrowstyle='<->', color='black', lw=0.8))
        ax.text(cx + hw_st, section_y_offset - d_st - 7, f'{2 * hw_st / (BEAM_IN / 2) * BEAM_IN / 2:.1f}"',
                ha='center', va='top', fontsize=6)

        # Dimension: depth
        ax.annotate('', xy=(cx + 2 * hw_st + 3, section_y_offset),
                    xytext=(cx + 2 * hw_st + 3, section_y_offset - d_st),
                    arrowprops=dict(arrowstyle='<->', color='black', lw=0.8))
        ax.text(cx + 2 * hw_st + 5, section_y_offset - d_st / 2, f'{d_st:.1f}"',
                ha='left', va='center', fontsize=6)

        # Thickness callout
        ax.annotate(f't={THICKNESS_IN}"',
                    xy=(cx + hw_st - t / 2, section_y_offset - d_st + t / 2),
                    xytext=(cx + hw_st - 15, section_y_offset - d_st + 10),
                    fontsize=6, ha='center',
                    arrowprops=dict(arrowstyle='->', color='black', lw=0.5))

        # Label
        ax.text(cx + hw_st, section_y_offset + 4,
                f"SECTION {lbl}-{lbl}\nSCALE 1:4",
                ha='center', va='bottom', fontsize=7, fontweight='bold', color=col)

    draw_title_block(ax, fig, "Section Breakdown", 1, scale="1:8 / 1:4")

    fig.savefig(OUT_DIR / "report_section_breakdown.png", dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  [1/4] Section Breakdown saved")


# ─────────────────────────────────────────────────────────────
# DRAWING 2: Top and Isometric View (like their Figure 9)
# ─────────────────────────────────────────────────────────────
def draw_top_and_isometric():
    fig = plt.figure(figsize=(14, 10), facecolor='white')
    ax = fig.add_axes([0.06, 0.06, 0.88, 0.88])
    ax.set_xlim(-30, 250)
    ax.set_ylim(-100, 80)
    ax.set_aspect('equal')
    ax.axis('off')

    # ── Plan View (top portion) ──
    x_hull = np.linspace(0, LENGTH_IN, 200)
    x_frac = x_hull / LENGTH_IN
    hw = hull_halfwidth(x_frac) * BEAM_IN / 2

    py = 40  # plan y-offset
    ax.fill_between(x_hull, py - hw, py + hw,
                     color='#d4e6f1', alpha=0.4, edgecolor='black', linewidth=1.5)
    ax.plot(x_hull, py + hw, 'k-', lw=1.5)
    ax.plot(x_hull, py - hw, 'k-', lw=1.5)
    ax.plot([0, LENGTH_IN], [py, py], 'k-.', lw=0.5, alpha=0.4)

    # Dimension: overall length
    dim_y_top = py + BEAM_IN / 2 + 5
    ax.annotate('', xy=(LENGTH_IN, dim_y_top), xytext=(0, dim_y_top),
                arrowprops=dict(arrowstyle='<->', color='black', lw=1))
    ax.text(LENGTH_IN / 2, dim_y_top + 2, f'{LENGTH_IN}.00"',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Dimension: beam
    bx = LENGTH_IN + 8
    mid_hw = hull_halfwidth(0.5) * BEAM_IN / 2
    ax.annotate('', xy=(bx, py + mid_hw), xytext=(bx, py - mid_hw),
                arrowprops=dict(arrowstyle='<->', color='black', lw=1))
    ax.text(bx + 3, py, f'{BEAM_IN}.00"', ha='left', va='center', fontsize=8, fontweight='bold')
    ax.plot([LENGTH_IN / 2, bx - 1], [py + mid_hw, py + mid_hw], 'k:', lw=0.5, alpha=0.5)
    ax.plot([LENGTH_IN / 2, bx - 1], [py - mid_hw, py - mid_hw], 'k:', lw=0.5, alpha=0.5)

    # Station lines
    for i in range(1, 16):
        sx = i * LENGTH_IN / 16
        shw = hull_halfwidth(i / 16) * BEAM_IN / 2
        ax.plot([sx, sx], [py - shw, py + shw], 'k-', lw=0.3, alpha=0.3)

    # Bulkhead positions (at 1/4 and 3/4)
    for bk_frac in [0.25, 0.75]:
        bx_pos = bk_frac * LENGTH_IN
        bk_hw = hull_halfwidth(bk_frac) * BEAM_IN / 2
        ax.plot([bx_pos, bx_pos], [py - bk_hw, py + bk_hw], 'b-', lw=1.5, alpha=0.7)
        ax.text(bx_pos, py - bk_hw - 3, "BHD", ha='center', va='top',
                fontsize=5, color='blue')

    ax.text(LENGTH_IN / 2, py + BEAM_IN / 2 + 15, "PLAN VIEW (TOP)",
            ha='center', va='bottom', fontsize=9, fontweight='bold')

    # ── Isometric View (bottom portion) ──
    # Simple 3D projection: x'=x-y*cos30, y'=-z+y*sin30
    iso_x_off = 20
    iso_y_off = -55
    cos30 = np.cos(np.radians(30)) * 0.4
    sin30 = np.sin(np.radians(30)) * 0.4

    def iso(x, y, z):
        """Convert 3D to isometric 2D."""
        return (x + y * cos30 + iso_x_off, z + y * sin30 + iso_y_off)

    # Hull outline - draw port side, starboard side, bottom
    n = 80
    x3d = np.linspace(0, LENGTH_IN, n)
    x_frac3 = x3d / LENGTH_IN

    # Top edge - port side
    pts_top_port = [iso(x, -hull_halfwidth(f) * BEAM_IN / 2, 0) for x, f in zip(x3d, x_frac3)]
    # Top edge - starboard side
    pts_top_star = [iso(x, hull_halfwidth(f) * BEAM_IN / 2, 0) for x, f in zip(x3d, x_frac3)]
    # Bottom edge - centerline (keel)
    pts_bot = [iso(x, 0, -hull_depth_at(f) * DEPTH_IN) for x, f in zip(x3d, x_frac3)]

    # Draw hull surfaces
    # Port side (visible face)
    port_xs = [p[0] for p in pts_top_port]
    port_ys = [p[1] for p in pts_top_port]
    bot_xs = [p[0] for p in pts_bot]
    bot_ys = [p[1] for p in pts_bot]
    star_xs = [p[0] for p in pts_top_star]
    star_ys = [p[1] for p in pts_top_star]

    # Fill the visible hull face (port side to bottom)
    hull_x = port_xs + bot_xs[::-1]
    hull_y = port_ys + bot_ys[::-1]
    ax.fill(hull_x, hull_y, color='#d5dbdb', alpha=0.5, edgecolor='none')

    # Fill top deck area
    deck_x = port_xs + star_xs[::-1]
    deck_y = port_ys + star_ys[::-1]
    ax.fill(deck_x, deck_y, color='#d4e6f1', alpha=0.3, edgecolor='none')

    # Draw edges
    ax.plot(port_xs, port_ys, 'k-', lw=1.5)
    ax.plot(star_xs, star_ys, 'k-', lw=1.2, alpha=0.7)
    ax.plot(bot_xs, bot_ys, 'k-', lw=1.0, alpha=0.5)

    # Bow and stern closing lines
    bow_top_p = iso(0, 0, 0)
    bow_bot = iso(0, 0, -hull_depth_at(0) * DEPTH_IN)
    ax.plot([bow_top_p[0], bow_bot[0]], [bow_top_p[1], bow_bot[1]], 'k-', lw=1.5)

    stern_top_p = iso(LENGTH_IN, 0, 0)
    stern_bot = iso(LENGTH_IN, 0, -hull_depth_at(1.0) * DEPTH_IN)
    ax.plot([stern_top_p[0], stern_bot[0]], [stern_top_p[1], stern_bot[1]], 'k-', lw=1.5)

    # Bulkhead lines in isometric
    for bk_frac in [0.25, 0.75]:
        bx3 = bk_frac * LENGTH_IN
        bk_hw = hull_halfwidth(bk_frac) * BEAM_IN / 2
        bk_d = hull_depth_at(bk_frac) * DEPTH_IN
        p1 = iso(bx3, -bk_hw, 0)
        p2 = iso(bx3, bk_hw, 0)
        p3 = iso(bx3, 0, -bk_d)
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'b-', lw=1, alpha=0.6)
        ax.plot([p1[0], p3[0]], [p1[1], p3[1]], 'b-', lw=0.8, alpha=0.4)
        ax.plot([p2[0], p3[0]], [p2[1], p3[1]], 'b-', lw=0.8, alpha=0.4)

    ax.text(LENGTH_IN / 2 + iso_x_off, iso_y_off - DEPTH_IN - 15,
            "ISOMETRIC VIEW", ha='center', va='top', fontsize=9, fontweight='bold')

    draw_title_block(ax, fig, "Top and Isometric View", 2, scale="1:8 / 1:35")

    fig.savefig(OUT_DIR / "report_top_isometric.png", dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  [2/4] Top and Isometric View saved")


# ─────────────────────────────────────────────────────────────
# DRAWING 3: Free Body Diagram w/ Shear & Moment (like Figure 1)
# ─────────────────────────────────────────────────────────────
def draw_fbd_shear_moment():
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [2, 1, 1]})
    fig.patch.set_facecolor('white')
    fig.subplots_adjust(hspace=0.35, left=0.1, right=0.92, top=0.93, bottom=0.08)

    L = LENGTH_IN / 12  # in feet
    w_hull = HULL_WEIGHT_LBS / L  # lb/ft hull UDL
    P_crew = CREW_WEIGHT_LBS  # total crew point load at midspan
    w_buoyancy = (HULL_WEIGHT_LBS + CREW_WEIGHT_LBS) / L  # buoyancy UDL (reaction)

    # ── FBD ──
    ax1 = axes[0]
    ax1.set_xlim(-1, L + 1)
    ax1.set_ylim(-4, 7)
    ax1.set_aspect('equal')

    # Hull beam
    ax1.fill_between([0, L], [0, 0], [0.8, 0.8], color='#bdc3c7', edgecolor='black', lw=1.5)
    ax1.text(L / 2, 0.4, f"Concrete Hull (L = {L:.1f} ft)", ha='center', va='center', fontsize=8)

    # Distributed hull weight (downward arrows)
    for xi in np.linspace(0.5, L - 0.5, 15):
        ax1.annotate('', xy=(xi, -0.3), xytext=(xi, -1.8),
                     arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=1))
    ax1.fill_between([0, L], [-1.8, -1.8], [-0.3, -0.3], color='#e74c3c', alpha=0.1)
    ax1.text(L / 2, -2.2, f"w_hull = {w_hull:.1f} lb/ft (dead load)",
             ha='center', va='top', fontsize=7, color='#e74c3c')

    # Crew point loads (4 paddlers in middle half)
    crew_positions = [L * 0.3, L * 0.4, L * 0.6, L * 0.7]
    P_each = 175  # lbs per paddler
    for cp in crew_positions:
        ax1.annotate('', xy=(cp, 0.8), xytext=(cp, 3.5),
                     arrowprops=dict(arrowstyle='->', color='#8e44ad', lw=2))
        ax1.text(cp, 3.7, f'{P_each} lb', ha='center', va='bottom', fontsize=6, color='#8e44ad')
    ax1.text(L / 2, 4.5, "Crew Live Loads (4 paddlers)", ha='center', va='bottom',
             fontsize=7, color='#8e44ad', fontweight='bold')

    # Buoyancy reaction (upward distributed)
    for xi in np.linspace(0.5, L - 0.5, 20):
        ax1.annotate('', xy=(xi, 0), xytext=(xi, -0.3),
                     arrowprops=dict(arrowstyle='->', color='#2980b9', lw=0.5, alpha=0.5))

    # Support triangles at ends
    for sx in [0, L]:
        tri_x = [sx - 0.3, sx + 0.3, sx]
        tri_y = [-0.3, -0.3, 0]
        ax1.fill(tri_x, tri_y, color='#2c3e50', alpha=0.7)

    # Reactions
    ax1.annotate('', xy=(0, -0.3), xytext=(0, -3.0),
                 arrowprops=dict(arrowstyle='<-', color='#2980b9', lw=2))
    R = (HULL_WEIGHT_LBS + CREW_WEIGHT_LBS) / 2
    ax1.text(0, -3.3, f'R_A = {R:.0f} lb', ha='center', va='top', fontsize=7,
             color='#2980b9', fontweight='bold')
    ax1.annotate('', xy=(L, -0.3), xytext=(L, -3.0),
                 arrowprops=dict(arrowstyle='<-', color='#2980b9', lw=2))
    ax1.text(L, -3.3, f'R_B = {R:.0f} lb', ha='center', va='top', fontsize=7,
             color='#2980b9', fontweight='bold')

    ax1.set_title("Free Body Diagram", fontsize=11, fontweight='bold', pad=10)
    ax1.axis('off')

    # ── Shear Force Diagram ──
    ax2 = axes[1]
    x = np.linspace(0, L, 500)
    # Shear from UDL hull weight
    V = R - w_hull * x
    # Add crew point loads
    for cp in crew_positions:
        V = np.where(x >= cp, V - P_each, V)

    ax2.fill_between(x, 0, V, where=(V >= 0), color='#3498db', alpha=0.3)
    ax2.fill_between(x, 0, V, where=(V < 0), color='#e74c3c', alpha=0.3)
    ax2.plot(x, V, 'b-', lw=2)
    ax2.axhline(0, color='black', lw=0.5)
    ax2.set_ylabel("Shear (lb)", fontsize=9)
    ax2.set_title("Shear Force Diagram", fontsize=10, fontweight='bold')
    ax2.set_xlim(0, L)
    V_max = np.max(np.abs(V))
    ax2.text(L * 0.02, V_max * 0.8, f"V_max = {V_max:.0f} lb", fontsize=8,
             fontweight='bold', color='blue')
    ax2.grid(True, alpha=0.2)
    ax2.set_xlabel("")
    ax2.tick_params(axis='x', labelbottom=False)

    # ── Bending Moment Diagram ──
    ax3 = axes[2]
    # Moment from UDL
    M = R * x - w_hull * x ** 2 / 2
    # Add crew point loads
    for cp in crew_positions:
        M = np.where(x >= cp, M - P_each * (x - cp), M)

    ax3.fill_between(x, 0, M, color='#e74c3c', alpha=0.2)
    ax3.plot(x, M, 'r-', lw=2)
    ax3.axhline(0, color='black', lw=0.5)

    M_max = np.max(M)
    M_max_x = x[np.argmax(M)]
    ax3.axvline(M_max_x, color='red', ls='--', alpha=0.5)
    ax3.plot(M_max_x, M_max, 'ro', ms=6)
    ax3.text(M_max_x + 0.3, M_max * 0.95, f"M_max = {M_max:.0f} lb-ft\nat x = {M_max_x:.1f} ft",
             fontsize=8, fontweight='bold', color='red')

    ax3.set_ylabel("Moment (lb-ft)", fontsize=9)
    ax3.set_xlabel("Position along hull (ft)", fontsize=9)
    ax3.set_title("Bending Moment Diagram", fontsize=10, fontweight='bold')
    ax3.set_xlim(0, L)
    ax3.grid(True, alpha=0.2)

    fig.savefig(OUT_DIR / "report_fbd_shear_moment.png", dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  [3/4] FBD / Shear / Moment saved")


# ─────────────────────────────────────────────────────────────
# DRAWING 4: Cross-Section / Moment of Inertia Analysis (like Figure 2)
# ─────────────────────────────────────────────────────────────
def draw_moi_analysis():
    fig = plt.figure(figsize=(16, 11), facecolor='white')

    B = BEAM_IN
    D = DEPTH_IN
    t = THICKNESS_IN

    # Real calculations
    a_bot = B * t
    y_bot = t / 2
    h_wall = D - t
    a_wall = t * h_wall
    y_wall = t + h_wall / 2
    total_area = a_bot + 2 * a_wall
    y_na = (a_bot * y_bot + 2 * a_wall * y_wall) / total_area

    i_bot_self = B * t ** 3 / 12
    i_wall_self = t * h_wall ** 3 / 12
    i_total = (i_bot_self + a_bot * (y_na - y_bot) ** 2
               + 2 * (i_wall_self + a_wall * (y_wall - y_na) ** 2))
    c_top = D - y_na
    c_bot = y_na
    c_max = max(c_top, c_bot)
    S_raw = i_total / c_max
    S_reduced = S_raw * 0.75

    L_ft = LENGTH_IN / 12
    M_hull = (HULL_WEIGHT_LBS / L_ft) * L_ft ** 2 / 8
    M_crew = CREW_WEIGHT_LBS * L_ft / 4
    M_total = M_hull + M_crew
    sigma = M_total * 12 / S_reduced
    SF = FLEXURAL_STRENGTH_PSI / sigma

    # ── Left: Cross-Section with exaggerated thickness ──
    ax1 = fig.add_axes([0.04, 0.08, 0.45, 0.82])

    # Use visual thickness = 2" for visibility (actual = 0.5")
    tv = 2.0  # visual thickness for drawing
    scale_note = f"(Wall thickness exaggerated {tv/t:.0f}x for clarity; actual t = {t}\")"

    ax1.set_xlim(-B / 2 - 8, B / 2 + 8)
    ax1.set_ylim(-4, D + 5)
    ax1.set_aspect('equal')

    # Component 1: Bottom plate
    rect1 = Rectangle((-B / 2, 0), B, tv, facecolor='#3498db', alpha=0.5,
                       edgecolor='#2471a3', lw=2.5)
    ax1.add_patch(rect1)

    # Component 2: Left wall
    rect2 = Rectangle((-B / 2, tv), tv, D - tv, facecolor='#e74c3c', alpha=0.5,
                       edgecolor='#c0392b', lw=2.5)
    ax1.add_patch(rect2)

    # Component 3: Right wall
    rect3 = Rectangle((B / 2 - tv, tv), tv, D - tv, facecolor='#e74c3c', alpha=0.5,
                       edgecolor='#c0392b', lw=2.5)
    ax1.add_patch(rect3)

    # Interior (hollow)
    rect_int = Rectangle((-B / 2 + tv, tv), B - 2 * tv, D - tv + 1,
                          facecolor='#fafafa', edgecolor='gray', lw=0.8, ls='--')
    ax1.add_patch(rect_int)

    # Neutral axis (at real y_na position)
    ax1.axhline(y_na, color='#27ae60', lw=3, ls='-.')
    ax1.text(B / 2 + 1.5, y_na + 0.5, f'Neutral Axis\ny_NA = {y_na:.2f}"',
             fontsize=9, color='#27ae60', va='bottom', fontweight='bold')

    # Component labels (big, visible)
    ax1.text(0, tv / 2, f'RECT 1\nBottom Plate\n{B}" x {t}"',
             ha='center', va='center', fontsize=9, fontweight='bold', color='#1a5276')
    ax1.text(-B / 2 + tv / 2, tv + (D - tv) / 2,
             f'RECT 2\nLeft Wall\n{t}" x {h_wall:.1f}"',
             ha='center', va='center', fontsize=8, fontweight='bold', color='#922b21',
             rotation=90)
    ax1.text(B / 2 - tv / 2, tv + (D - tv) / 2,
             f'RECT 3\nRight Wall\n{t}" x {h_wall:.1f}"',
             ha='center', va='center', fontsize=8, fontweight='bold', color='#922b21',
             rotation=90)

    # Centroid markers
    ax1.plot(0, y_bot, 'o', color='#2980b9', ms=8, zorder=5)
    ax1.text(2, y_bot, f'  y\u0305\u2081={y_bot:.2f}"', fontsize=7, color='#2980b9', va='center')
    ax1.plot(-B / 2 + tv / 2, y_wall, 's', color='#e74c3c', ms=8, zorder=5)
    ax1.text(-B / 2 + tv + 1, y_wall, f'  y\u0305\u2082={y_wall:.2f}"',
             fontsize=7, color='#e74c3c', va='center')

    # Dimension: overall width
    ax1.annotate('', xy=(B / 2, -2.5), xytext=(-B / 2, -2.5),
                 arrowprops=dict(arrowstyle='<->', color='black', lw=1.2))
    ax1.text(0, -3.2, f'B = {B}"', ha='center', va='top', fontsize=11, fontweight='bold')

    # Dimension: overall depth
    ax1.annotate('', xy=(-B / 2 - 4, D), xytext=(-B / 2 - 4, 0),
                 arrowprops=dict(arrowstyle='<->', color='black', lw=1.2))
    ax1.text(-B / 2 - 5.5, D / 2, f'D = {D}"', ha='right', va='center', fontsize=11,
             fontweight='bold', rotation=90)

    # Thickness callout
    ax1.annotate(f't = {t}" (actual)',
                 xy=(-B / 2 + tv, tv + 2), xytext=(-B / 2 + 8, tv + 6),
                 fontsize=8, ha='center', fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color='black', lw=1))

    ax1.set_title("Midship Cross-Section — MOI Components",
                   fontsize=12, fontweight='bold', pad=10)
    ax1.text(0, -3.8, scale_note, ha='center', va='top', fontsize=7, style='italic',
             color='gray')

    # Custom legend
    from matplotlib.lines import Line2D
    legend_elements = [
        mpatches.Patch(facecolor='#3498db', alpha=0.5, edgecolor='#2471a3', label='Bottom plate (Rect 1)'),
        mpatches.Patch(facecolor='#e74c3c', alpha=0.5, edgecolor='#c0392b', label='Side walls (Rect 2, 3)'),
        Line2D([0], [0], color='#27ae60', lw=3, ls='-.', label=f'N.A. at {y_na:.2f}"'),
    ]
    ax1.legend(handles=legend_elements, loc='upper right', fontsize=8,
               framealpha=0.9, edgecolor='gray')
    ax1.grid(True, alpha=0.1)
    ax1.set_xlabel('Width (in)', fontsize=9)
    ax1.set_ylabel('Height (in)', fontsize=9)

    # ── Right: Calculation summary ──
    ax2 = fig.add_axes([0.52, 0.08, 0.46, 0.82])
    ax2.axis('off')

    calc_lines = [
        ("STRUCTURAL ANALYSIS — DESIGN A", 14, 'bold', 'black'),
        (f"{'─' * 52}", 8, 'normal', 'gray'),
        ("", 6, 'normal', 'black'),
        ("CROSS-SECTION PROPERTIES  (Thin-Shell U-Section)", 11, 'bold', '#2c3e50'),
        (f"  B = {B}\"    D = {D}\"    t = {t}\"", 10, 'normal', 'black'),
        ("", 6, 'normal', 'black'),
        ("  Component 1 — Bottom Plate:", 10, 'bold', '#2980b9'),
        (f"    A\u2081 = {B} \u00d7 {t} = {a_bot:.1f} in\u00b2", 10, 'normal', 'black'),
        (f"    y\u0305\u2081 = {y_bot:.3f}\"        I\u2081 = {i_bot_self:.4f} in\u2074", 10, 'normal', 'black'),
        ("", 4, 'normal', 'black'),
        ("  Components 2,3 — Side Walls (each):", 10, 'bold', '#e74c3c'),
        (f"    A\u2082 = {t} \u00d7 {h_wall:.1f} = {a_wall:.2f} in\u00b2", 10, 'normal', 'black'),
        (f"    y\u0305\u2082 = {y_wall:.3f}\"       I\u2082 = {i_wall_self:.2f} in\u2074", 10, 'normal', 'black'),
        ("", 4, 'normal', 'black'),
        ("  Neutral Axis (Composite):", 10, 'bold', '#27ae60'),
        (f"    y\u0305_NA = \u03a3A\u1d62y\u1d62 / \u03a3A\u1d62 = {y_na:.3f}\" from bottom", 10, 'normal', 'black'),
        ("", 4, 'normal', 'black'),
        ("  Moment of Inertia (Parallel Axis Theorem):", 10, 'bold', '#2c3e50'),
        (f"    I_total = \u03a3(I\u1d62 + A\u1d62\u00b7d\u1d62\u00b2) = {i_total:.1f} in\u2074", 10, 'normal', 'black'),
        ("", 4, 'normal', 'black'),
        ("  Section Modulus:", 10, 'bold', '#2c3e50'),
        (f"    c_max = {c_max:.3f}\" ({'top' if c_top > c_bot else 'bottom'} fiber governs)", 10, 'normal', 'black'),
        (f"    S_raw = I / c = {S_raw:.2f} in\u00b3", 10, 'normal', 'black'),
        (f"    S_design = S_raw \u00d7 0.75 = {S_reduced:.2f} in\u00b3", 11, 'bold', '#8e44ad'),
        (f"    (ACI 318 thin-shell reduction for cracking)", 8, 'normal', 'gray'),
        ("", 6, 'normal', 'black'),
        (f"{'─' * 52}", 8, 'normal', 'gray'),
        ("BENDING ANALYSIS", 11, 'bold', '#c0392b'),
        ("", 4, 'normal', 'black'),
        (f"  M_hull  = wL\u00b2/8 = {M_hull:.1f} lb-ft   (uniform dead load)", 10, 'normal', 'black'),
        (f"  M_crew  = PL/4  = {M_crew:.1f} lb-ft   (point load at midspan)", 10, 'normal', 'black'),
        (f"  M_total = {M_total:.1f} lb-ft", 11, 'bold', 'black'),
        ("", 4, 'normal', 'black'),
        (f"  \u03c3_max = M \u00d7 12 / S = {sigma:.1f} psi", 10, 'normal', 'black'),
        (f"  f'r = {FLEXURAL_STRENGTH_PSI} psi (flexural strength)", 10, 'normal', 'black'),
        ("", 6, 'normal', 'black'),
        (f"{'─' * 52}", 8, 'normal', 'gray'),
    ]

    # Safety factor box
    sf_pass = SF >= 2.0
    sf_color = '#27ae60' if sf_pass else '#e74c3c'
    sf_text = f"SAFETY FACTOR = f'r / \u03c3 = {SF:.2f}   {'PASS (\u2265 2.0)' if sf_pass else 'FAIL (< 2.0)'}"

    y_pos = 0.97
    for text, size, weight, color in calc_lines:
        ax2.text(0.02, y_pos, text, transform=ax2.transAxes,
                 fontsize=size, fontweight=weight, color=color,
                 fontfamily='monospace', va='top')
        y_pos -= size * 0.0025 + 0.008

    # Big safety factor result box
    y_pos -= 0.02
    sf_box = FancyBboxPatch((0.02, y_pos - 0.06), 0.96, 0.07,
                             boxstyle="round,pad=0.01",
                             transform=ax2.transAxes,
                             facecolor=sf_color, alpha=0.15,
                             edgecolor=sf_color, linewidth=2)
    ax2.add_patch(sf_box)
    ax2.text(0.50, y_pos - 0.025, sf_text,
             transform=ax2.transAxes, fontsize=13, fontweight='bold',
             color=sf_color, ha='center', va='center', fontfamily='monospace')

    fig.suptitle("Moment of Inertia & Structural Analysis — Midship Section",
                 fontsize=15, fontweight='bold', y=0.97)

    fig.savefig(OUT_DIR / "report_moi_analysis.png", dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  [4/4] MOI / Structural Analysis saved")


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Generating report drawings for {TEAM}...")
    print(f"Design A: {LENGTH_IN}\" x {BEAM_IN}\" x {DEPTH_IN}\", t={THICKNESS_IN}\"")
    print()
    draw_section_breakdown()
    draw_top_and_isometric()
    draw_fbd_shear_moment()
    draw_moi_analysis()
    print()
    print(f"All 4 drawings saved to {OUT_DIR}/")
    print("  report_section_breakdown.png")
    print("  report_top_isometric.png")
    print("  report_fbd_shear_moment.png")
    print("  report_moi_analysis.png")
