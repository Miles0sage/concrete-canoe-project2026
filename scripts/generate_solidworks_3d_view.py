#!/usr/bin/env python3
"""
Generate SolidWorks-Style 3D Dimensioned View for NAU ASCE 2026 Concrete Canoe.

Produces a professional isometric 3D rendering with full dimension callouts,
station cross-sections, and engineering annotations — styled to resemble
a SolidWorks dimensioned model view.

Canoe 1 Specs (from solidworks_specifications.md):
  LOA = 216" (18 ft), Beam = 30", Depth = 18", t = 0.5"
  V-bottom angle: 15 deg, Flare: 10 deg outward
  5 stations with taper

Author: NAU ASCE Concrete Canoe Team 2026
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
import os

# ============================================================================
# DESIGN PARAMETERS (SolidWorks Canoe 1)
# ============================================================================
LOA = 216.0       # Length overall (inches)
BEAM = 30.0       # Max beam at midship (inches)
DEPTH = 18.0      # Depth at midship (inches)
THICK = 0.5       # Shell thickness (inches)
WEIGHT = 276.0    # Target weight (lbs)
V_ANGLE = 15.0    # V-bottom angle (degrees)
FLARE = 10.0      # Flare angle (degrees)

# Station data from solidworks_specifications.md
STATIONS = [
    {"name": "Bow",     "pct": 0.00, "width": 6,  "depth": 16},
    {"name": "Sta 1",   "pct": 0.25, "width": 22, "depth": 17},
    {"name": "Midship", "pct": 0.50, "width": 30, "depth": 18},
    {"name": "Sta 3",   "pct": 0.75, "width": 22, "depth": 17},
    {"name": "Stern",   "pct": 1.00, "width": 6,  "depth": 16},
]

# Colors
SW_BG = "#f0f0f0"        # SolidWorks-ish light gray background
SW_HULL = "#7eb8d8"       # Light blue hull
SW_HULL_EDGE = "#3a7ca5"  # Darker blue edges
SW_DIM = "#1a1a1a"        # Dimension line color
SW_DIM_TEXT = "#0033cc"   # Blue dimension text (SolidWorks style)
SW_STATION = "#cc3300"    # Station cross-section lines
SW_WATERLINE = "#00cccc"  # Waterline
SW_GREEN = "#009933"      # Green for annotations


def generate_hull_surface(n_long=100, n_circ=50):
    """Generate 3D hull surface using station interpolation."""
    u = np.linspace(0, 1, n_long)
    v = np.linspace(0, 1, n_circ)

    # Interpolate station widths and depths
    st_pcts = [s["pct"] for s in STATIONS]
    st_widths = [s["width"] for s in STATIONS]
    st_depths = [s["depth"] for s in STATIONS]

    X = np.zeros((n_long, n_circ))
    Y = np.zeros((n_long, n_circ))
    Z = np.zeros((n_long, n_circ))

    for i, ui in enumerate(u):
        x = ui * LOA

        # Interpolate width and depth at this station
        half_b = np.interp(ui, st_pcts, st_widths) / 2.0
        local_D = np.interp(ui, st_pcts, st_depths)

        # V-bottom geometry
        deadrise_depth = local_D * 0.18

        for j, vj in enumerate(v):
            X[i, j] = x
            if vj <= 0.3:
                # Keel to chine (V-bottom)
                frac = vj / 0.3
                Y[i, j] = half_b * 0.75 * frac
                Z[i, j] = -deadrise_depth * (1 - frac)
            else:
                # Chine to gunwale (flared sides)
                frac = (vj - 0.3) / 0.7
                Y[i, j] = half_b * (0.75 + 0.25 * frac)
                Z[i, j] = local_D * frac

    return X, Y, Z


def generate_station_cross_section(pct, width, depth, n_pts=40):
    """Generate cross-section outline at a station."""
    half_b = width / 2.0
    deadrise_depth = depth * 0.18

    pts_y = []
    pts_z = []

    for vj in np.linspace(0, 1, n_pts):
        if vj <= 0.3:
            frac = vj / 0.3
            y = half_b * 0.75 * frac
            z = -deadrise_depth * (1 - frac)
        else:
            frac = (vj - 0.3) / 0.7
            y = half_b * (0.75 + 0.25 * frac)
            z = depth * frac

        pts_y.append(y)
        pts_z.append(z)

    # Mirror for full cross-section
    full_y = list(reversed([-y for y in pts_y])) + pts_y
    full_z = list(reversed(pts_z)) + pts_z

    return np.array(full_y), np.array(full_z)


def draw_dimension_line_3d(ax, start, end, label, offset=None, fontsize=9,
                            color=SW_DIM_TEXT, arrow_color=SW_DIM):
    """Draw a 3D dimension line with text label."""
    # Draw the line
    ax.plot([start[0], end[0]], [start[1], end[1]], [start[2], end[2]],
            color=arrow_color, linewidth=1.2, zorder=10)

    # Draw arrow heads (short perpendicular ticks)
    ax.plot([start[0]], [start[1]], [start[2]], '|', color=arrow_color,
            markersize=8, zorder=10)
    ax.plot([end[0]], [end[1]], [end[2]], '|', color=arrow_color,
            markersize=8, zorder=10)

    # Text at midpoint
    mid = [(s + e) / 2 for s, e in zip(start, end)]
    if offset:
        mid = [m + o for m, o in zip(mid, offset)]

    ax.text(mid[0], mid[1], mid[2], label,
            fontsize=fontsize, fontweight='bold', color=color,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                      edgecolor=color, alpha=0.95, linewidth=0.8),
            zorder=15)


def generate_solidworks_view():
    """Generate the main SolidWorks-style 3D dimensioned view."""
    print("Generating SolidWorks-Style 3D Dimensioned View...")

    X, Y, Z = generate_hull_surface()

    # Mirror for full hull
    X_full = np.vstack([X, X])
    Y_full = np.vstack([Y, -Y[:, ::-1]])
    Z_full = np.vstack([Z, Z[:, ::-1]])

    # ===================================================================
    # Create figure with 2 panels: main isometric + front cross-section
    # ===================================================================
    fig = plt.figure(figsize=(20, 14))
    fig.patch.set_facecolor('white')

    # Title block
    fig.suptitle(
        "SolidWorks 3D Model — NAU ASCE Concrete Canoe 2026",
        fontsize=18, fontweight='bold', color='#1a1a1a', y=0.97
    )
    fig.text(0.5, 0.94,
             f'LOA: {LOA:.0f}" ({LOA/12:.0f} ft)  |  Beam: {BEAM:.0f}"  |  '
             f'Depth: {DEPTH:.0f}"  |  t: {THICK:.1f}"  |  Weight: {WEIGHT:.0f} lbs',
             fontsize=12, ha='center', color='#666666', style='italic')

    # -------------------------------------------------------------------
    # PANEL 1: Main Isometric View (large)
    # -------------------------------------------------------------------
    ax1 = fig.add_subplot(121, projection='3d')

    # Hull surface
    surf = ax1.plot_surface(
        X_full, Y_full, Z_full,
        color=SW_HULL, alpha=0.65,
        edgecolor=SW_HULL_EDGE, linewidth=0.12,
        rstride=3, cstride=2,
        shade=True
    )

    # Gunwale edge (top edge) - both sides
    ax1.plot(X[0:, -1], Y[0:, -1], Z[0:, -1],
             color=SW_HULL_EDGE, linewidth=2.0, zorder=8)
    ax1.plot(X[0:, -1], -Y[0:, -1], Z[0:, -1],
             color=SW_HULL_EDGE, linewidth=2.0, zorder=8)

    # Keel line
    ax1.plot(X[:, 0], Y[:, 0], Z[:, 0],
             color='#cc0000', linewidth=2.0, linestyle='--', zorder=8,
             label='Keel Line')

    # Waterline (approximate at ~5" depth)
    wl_z = 5.0
    wl_x = np.linspace(0, LOA, 150)
    wl_y = []
    for xi in wl_x:
        ui = xi / LOA
        half_b = np.interp(ui, [s["pct"] for s in STATIONS],
                           [s["width"]/2 for s in STATIONS])
        local_D = np.interp(ui, [s["pct"] for s in STATIONS],
                            [s["depth"] for s in STATIONS])
        # Find y at waterline z
        if wl_z <= local_D:
            frac = wl_z / local_D
            y_at_wl = half_b * (0.75 + 0.25 * frac)
        else:
            y_at_wl = half_b
        wl_y.append(y_at_wl)
    wl_y = np.array(wl_y)
    ax1.plot(wl_x, wl_y, wl_z, color=SW_WATERLINE, linewidth=2.5, zorder=9,
             label='Waterline')
    ax1.plot(wl_x, -wl_y, wl_z, color=SW_WATERLINE, linewidth=2.5, zorder=9)

    # --- Station cross-sections ---
    for st in STATIONS:
        x_pos = st["pct"] * LOA
        cs_y, cs_z = generate_station_cross_section(
            st["pct"], st["width"], st["depth"]
        )
        cs_x = np.full_like(cs_y, x_pos)
        ax1.plot(cs_x, cs_y, cs_z, color=SW_STATION, linewidth=1.8,
                 linestyle='-', alpha=0.7, zorder=7)

        # Station label
        ax1.text(x_pos, st["width"]/2 + 4, st["depth"] + 2,
                 st["name"], fontsize=8, color=SW_STATION,
                 fontweight='bold', ha='center')

    # --- Dimension Lines ---

    # 1. LOA dimension (along bottom)
    dim_z_base = -8
    ax1.plot([0, LOA], [0, 0], [dim_z_base, dim_z_base],
             color=SW_DIM, linewidth=1.5, zorder=10)
    # Extension lines
    ax1.plot([0, 0], [0, 0], [Z[:, 0].min(), dim_z_base],
             color=SW_DIM, linewidth=0.8, linestyle=':', zorder=10)
    ax1.plot([LOA, LOA], [0, 0], [Z[-1, 0].min(), dim_z_base],
             color=SW_DIM, linewidth=0.8, linestyle=':', zorder=10)
    # Arrow ticks at ends
    tick_len = 3
    ax1.plot([0, tick_len], [0, 0], [dim_z_base, dim_z_base],
             color=SW_DIM, linewidth=2.5, zorder=10)
    ax1.plot([LOA, LOA - tick_len], [0, 0], [dim_z_base, dim_z_base],
             color=SW_DIM, linewidth=2.5, zorder=10)
    # Label
    ax1.text(LOA/2, -2, dim_z_base - 2,
             f'LOA = {LOA:.0f}" ({LOA/12:.0f} ft)',
             fontsize=11, fontweight='bold', color=SW_DIM_TEXT,
             ha='center', va='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                       edgecolor=SW_DIM_TEXT, alpha=0.95, linewidth=1.0),
             zorder=15)

    # 2. Beam dimension at midship
    mid_x = LOA / 2
    beam_z = DEPTH + 3
    ax1.plot([mid_x, mid_x], [-BEAM/2, BEAM/2], [beam_z, beam_z],
             color=SW_DIM, linewidth=1.5, zorder=10)
    # Extension lines
    ax1.plot([mid_x, mid_x], [-BEAM/2, -BEAM/2], [DEPTH, beam_z],
             color=SW_DIM, linewidth=0.8, linestyle=':', zorder=10)
    ax1.plot([mid_x, mid_x], [BEAM/2, BEAM/2], [DEPTH, beam_z],
             color=SW_DIM, linewidth=0.8, linestyle=':', zorder=10)
    ax1.text(mid_x + 5, 0, beam_z + 2,
             f'Beam = {BEAM:.0f}"',
             fontsize=10, fontweight='bold', color=SW_DIM_TEXT,
             ha='center',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                       edgecolor=SW_DIM_TEXT, alpha=0.95),
             zorder=15)

    # 3. Depth dimension at midship (right side)
    depth_y = BEAM/2 + 5
    deadrise = DEPTH * 0.18
    ax1.plot([mid_x, mid_x], [depth_y, depth_y], [-deadrise, DEPTH],
             color=SW_DIM, linewidth=1.5, zorder=10)
    # Extension lines
    ax1.plot([mid_x, mid_x], [BEAM/2, depth_y], [-deadrise, -deadrise],
             color=SW_DIM, linewidth=0.8, linestyle=':', zorder=10)
    ax1.plot([mid_x, mid_x], [BEAM/2, depth_y], [DEPTH, DEPTH],
             color=SW_DIM, linewidth=0.8, linestyle=':', zorder=10)
    ax1.text(mid_x + 3, depth_y + 3, DEPTH/2,
             f'Depth = {DEPTH:.0f}"',
             fontsize=10, fontweight='bold', color=SW_DIM_TEXT,
             ha='center',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                       edgecolor=SW_DIM_TEXT, alpha=0.95),
             zorder=15)

    # 4. Thickness callout
    ax1.text(LOA * 0.15, -BEAM/2 - 8, DEPTH * 0.6,
             f't = {THICK:.1f}"',
             fontsize=10, fontweight='bold', color=SW_GREEN,
             ha='center',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#e8f5e9',
                       edgecolor=SW_GREEN, alpha=0.95),
             zorder=15)

    # 5. V-angle callout
    ax1.text(LOA * 0.15, -BEAM/2 - 8, DEPTH * 0.3,
             f'V-angle = {V_ANGLE:.0f}\u00b0',
             fontsize=9, fontweight='bold', color='#993300',
             ha='center',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#fff3e0',
                       edgecolor='#993300', alpha=0.95),
             zorder=15)

    # View settings
    ax1.view_init(elev=22, azim=-52)
    ax1.set_xlabel('Length (in)', fontsize=10, labelpad=8)
    ax1.set_ylabel('Beam (in)', fontsize=10, labelpad=8)
    ax1.set_zlabel('Depth (in)', fontsize=10, labelpad=8)
    ax1.set_title('Isometric View — Full Hull with Dimensions',
                   fontsize=13, fontweight='bold', color='#333333', pad=10)

    ax1.set_xlim(0, LOA)
    ax1.set_ylim(-BEAM/2 - 12, BEAM/2 + 12)
    ax1.set_zlim(-12, DEPTH + 6)

    ax1.legend(fontsize=9, loc='upper left')
    ax1.tick_params(labelsize=8)

    # Lighten the grid
    ax1.xaxis.pane.fill = False
    ax1.yaxis.pane.fill = False
    ax1.zaxis.pane.fill = False
    ax1.xaxis.pane.set_edgecolor('#cccccc')
    ax1.yaxis.pane.set_edgecolor('#cccccc')
    ax1.zaxis.pane.set_edgecolor('#cccccc')
    ax1.grid(True, alpha=0.3)

    # -------------------------------------------------------------------
    # PANEL 2: Midship Cross-Section with Full Dimensions
    # -------------------------------------------------------------------
    ax2 = fig.add_subplot(122)

    # Draw the midship cross-section
    cs_y, cs_z = generate_station_cross_section(0.5, BEAM, DEPTH)

    # Fill the cross-section
    ax2.fill(cs_y, cs_z, color=SW_HULL, alpha=0.4, zorder=2)
    ax2.plot(cs_y, cs_z, color=SW_HULL_EDGE, linewidth=2.5, zorder=3)

    # Inner surface (thickness offset - approximate)
    inner_scale = 1 - 2*THICK/BEAM
    cs_y_inner = cs_y * inner_scale
    cs_z_inner = cs_z * 0.97 + THICK * 0.5  # approximate inner offset
    ax2.fill(cs_y_inner, cs_z_inner, color='white', zorder=2.5)
    ax2.plot(cs_y_inner, cs_z_inner, color=SW_HULL_EDGE, linewidth=1.5,
             linestyle='--', zorder=3, alpha=0.6)

    # Neutral axis
    y_NA = 5.43  # from MOI calculations
    ax2.axhline(y=y_NA, color=SW_GREEN, linewidth=2, linestyle='--',
                 zorder=4, label=f'N.A. (y = {y_NA:.2f}")')

    # --- Dimension Lines ---
    deadrise = DEPTH * 0.18

    # Beam dimension (top)
    dim_top_z = DEPTH + 2
    ax2.annotate('', xy=(BEAM/2, dim_top_z), xytext=(-BEAM/2, dim_top_z),
                 arrowprops=dict(arrowstyle='<->', color=SW_DIM, lw=1.8))
    ax2.plot([-BEAM/2, -BEAM/2], [DEPTH, dim_top_z + 0.3],
             color=SW_DIM, linewidth=0.8, linestyle=':')
    ax2.plot([BEAM/2, BEAM/2], [DEPTH, dim_top_z + 0.3],
             color=SW_DIM, linewidth=0.8, linestyle=':')
    ax2.text(0, dim_top_z + 0.8, f'B = {BEAM:.0f}"',
             fontsize=12, fontweight='bold', color=SW_DIM_TEXT, ha='center',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                       edgecolor=SW_DIM_TEXT, alpha=0.95))

    # Depth dimension (right side)
    dim_right_y = BEAM/2 + 3
    ax2.annotate('', xy=(dim_right_y, DEPTH), xytext=(dim_right_y, -deadrise),
                 arrowprops=dict(arrowstyle='<->', color=SW_DIM, lw=1.8))
    ax2.plot([BEAM/2, dim_right_y + 0.5], [DEPTH, DEPTH],
             color=SW_DIM, linewidth=0.8, linestyle=':')
    ax2.plot([BEAM/2, dim_right_y + 0.5], [-deadrise, -deadrise],
             color=SW_DIM, linewidth=0.8, linestyle=':')
    ax2.text(dim_right_y + 2.5, DEPTH/2 - deadrise/2, f'D = {DEPTH:.0f}"',
             fontsize=12, fontweight='bold', color=SW_DIM_TEXT, ha='center',
             va='center', rotation=90,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                       edgecolor=SW_DIM_TEXT, alpha=0.95))

    # Thickness callout with leader
    t_label_y = -BEAM/2 + 2
    t_label_z = DEPTH * 0.5
    ax2.annotate(f't = {THICK:.1f}"',
                 xy=(-BEAM/2 * 0.85, DEPTH * 0.4),
                 xytext=(t_label_y - 5, t_label_z + 3),
                 fontsize=10, fontweight='bold', color=SW_GREEN,
                 arrowprops=dict(arrowstyle='->', color=SW_GREEN, lw=1.5),
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#e8f5e9',
                           edgecolor=SW_GREEN, alpha=0.95))

    # V-angle indicator at bottom
    # Draw the V-angle arc
    v_rad = np.radians(V_ANGLE)
    arc_r = 6
    theta_range = np.linspace(-np.pi/2, -np.pi/2 + v_rad, 20)
    arc_y = arc_r * np.cos(theta_range)
    arc_z = -deadrise + arc_r * np.sin(theta_range) + arc_r
    ax2.plot(arc_y, arc_z, color='#993300', linewidth=1.5, zorder=5)
    ax2.text(4, -deadrise + 1.5, f'{V_ANGLE:.0f}\u00b0',
             fontsize=10, fontweight='bold', color='#993300',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='#fff3e0',
                       edgecolor='#993300', alpha=0.95))

    # Centerline
    ax2.plot([0, 0], [-deadrise - 2, DEPTH + 1], color='#999999',
             linewidth=1, linestyle='-.', zorder=1)
    ax2.text(0.5, -deadrise - 3, 'CL', fontsize=9, color='#999999',
             ha='center', fontweight='bold')

    # Station labels (widths at each station)
    station_info = (
        f"Station Widths:\n"
        f"  Bow: {STATIONS[0]['width']}\"  |  "
        f"Sta 1: {STATIONS[1]['width']}\"  |  "
        f"Mid: {STATIONS[2]['width']}\"\n"
        f"  Sta 3: {STATIONS[3]['width']}\"  |  "
        f"Stern: {STATIONS[4]['width']}\""
    )
    ax2.text(0, -deadrise - 6, station_info,
             fontsize=9, ha='center', va='top', color='#333333',
             fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#f5f5f5',
                       edgecolor='#999999', alpha=0.95))

    # Style
    ax2.set_xlim(-BEAM/2 - 8, BEAM/2 + 8)
    ax2.set_ylim(-deadrise - 10, DEPTH + 5)
    ax2.set_aspect('equal')
    ax2.set_title('Midship Cross-Section — Dimensioned',
                   fontsize=13, fontweight='bold', color='#333333', pad=12)
    ax2.set_xlabel('Width (in)', fontsize=10)
    ax2.set_ylabel('Height (in)', fontsize=10)
    ax2.grid(True, alpha=0.2, linewidth=0.5)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.legend(fontsize=9, loc='upper left')
    ax2.tick_params(labelsize=9)

    # -------------------------------------------------------------------
    # Title block (bottom)
    # -------------------------------------------------------------------
    tb_text = (
        f"NAU ASCE Concrete Canoe 2026  |  Canoe 1  |  "
        f"Material: Lightweight Concrete (~60-65 pcf)  |  "
        f"Shell: {THICK}\" uniform  |  "
        f"V-bottom: {V_ANGLE}\u00b0  |  Flare: {FLARE}\u00b0"
    )
    fig.text(0.5, 0.02, tb_text,
             fontsize=10, ha='center', va='bottom', color='#555555',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8f8f8',
                       edgecolor='#cccccc', alpha=0.95))

    plt.subplots_adjust(top=0.90, bottom=0.08, left=0.05, right=0.97,
                        wspace=0.15)

    # Save
    outpath = '/root/concrete-canoe-project2026/reports/figures/solidworks_3d_dimensioned.png'
    fig.savefig(outpath, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {outpath}")
    return outpath


if __name__ == '__main__':
    os.makedirs('/root/concrete-canoe-project2026/reports/figures', exist_ok=True)

    print("=" * 65)
    print("NAU ASCE 2026 Concrete Canoe — SolidWorks 3D Dimensioned View")
    print("=" * 65)
    print(f"\nCanoe 1 Specifications:")
    print(f"  LOA = {LOA:.0f}\" ({LOA/12:.0f} ft)")
    print(f"  Beam = {BEAM:.0f}\", Depth = {DEPTH:.0f}\", t = {THICK:.1f}\"")
    print(f"  Weight = {WEIGHT:.0f} lbs")
    print(f"  V-bottom = {V_ANGLE:.0f}\u00b0, Flare = {FLARE:.0f}\u00b0")
    print()

    path = generate_solidworks_view()

    print()
    print("=" * 65)
    print(f"DONE. SolidWorks 3D view saved: {path}")
    print("=" * 65)
