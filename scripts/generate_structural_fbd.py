#!/usr/bin/env python3
"""
Generate Professional Structural Engineering Diagrams for NAU ASCE 2026 Concrete Canoe.

Figure 1: Free Body Diagram with Shear Force and Bending Moment Diagrams
Figure 2: Moment of Inertia - Parallel Axis Theorem Cross-Section Analysis

Design A Parameters:
  Length = 192" (16 ft), Beam = 32", Depth = 17", Thickness = 0.5"
  Hull weight = 171 lbs, Crew = 4 x 175 lbs = 700 lbs
  Total loaded weight = 871 lbs

Author: NAU ASCE Concrete Canoe Team 2026
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon
from matplotlib.lines import Line2D
import os

# ============================================================================
# COLOR SCHEME
# ============================================================================
BLUE = "#2980b9"
BLUE_LIGHT = "#85c1e9"
RED = "#e74c3c"
RED_LIGHT = "#f1948a"
PURPLE = "#8e44ad"
PURPLE_LIGHT = "#bb8fce"
GREEN = "#27ae60"
DARK_GRAY = "#2c3e50"
LIGHT_GRAY = "#ecf0f1"
MEDIUM_GRAY = "#95a5a6"
ORANGE = "#e67e22"

# ============================================================================
# DESIGN PARAMETERS
# ============================================================================
L_in = 192.0        # Length in inches
L_ft = L_in / 12.0  # Length in feet (16 ft)
B = 32.0            # Beam in inches
D = 17.0            # Depth in inches
t = 0.5             # Shell thickness in inches

W_hull = 171.0      # Hull weight in lbs
n_crew = 4
W_crew_each = 175.0
W_crew = n_crew * W_crew_each  # 700 lbs
W_total = W_hull + W_crew       # 871 lbs

w_hull_per_ft = W_hull / L_ft   # lb/ft distributed hull weight

# Crew positions (fractions of L)
crew_fracs = [0.25, 0.40, 0.60, 0.75]
crew_pos_ft = [f * L_ft for f in crew_fracs]
crew_pos_in = [f * L_in for f in crew_fracs]


def buoyancy_distribution(x_ft, L, W_total):
    """
    Sinusoidal buoyancy distribution: b(x) = b_max * sin(pi*x/L)^0.6
    Normalized so integral over [0, L] = W_total.
    Returns b(x) in lb/ft.
    """
    xi = np.clip(x_ft / L, 0, 1)
    shape = np.sin(np.pi * xi) ** 0.6
    # Numerical integration to find normalization constant
    x_fine = np.linspace(0, L, 10000)
    xi_fine = x_fine / L
    shape_fine = np.sin(np.pi * xi_fine) ** 0.6
    # np.trapezoid for numpy 2.x, fallback to np.trapz for older
    _trapz = getattr(np, 'trapezoid', None) or np.trapz
    integral = _trapz(shape_fine, x_fine)
    b_max = W_total / integral
    return b_max * shape, b_max


def hull_profile_y(x_ft, L, D_in):
    """
    Generate a canoe hull profile (top and bottom edges) for visualization.
    Returns y_top and y_bottom in a normalized coordinate system.
    """
    xi = x_ft / L
    # Smooth canoe profile - narrower at bow/stern
    profile = np.sin(np.pi * xi) ** 0.4
    depth_fraction = 0.5  # visual fraction
    y_top = profile * depth_fraction
    y_bottom = -profile * depth_fraction * 0.3
    return y_top, y_bottom


def compute_shear_moment(x_ft, L, W_total, W_hull, crew_pos, crew_load):
    """
    Compute shear force V(x) and bending moment M(x) numerically.
    Sign convention: upward forces positive.
    V(x) = integral_0^x [b(x') - w_hull] dx' - sum(crew loads where x >= pos)
    M(x) = integral_0^x V(x') dx'
    """
    n = len(x_ft)
    dx = x_ft[1] - x_ft[0]

    # Distributed loads
    b_dist, b_max = buoyancy_distribution(x_ft, L, W_total)
    w_hull_dist = W_hull / L * np.ones_like(x_ft)  # uniform hull weight

    # Net distributed load (upward positive)
    q_net = b_dist - w_hull_dist

    # Shear force by numerical integration
    V = np.zeros(n)
    for i in range(1, n):
        V[i] = V[i - 1] + q_net[i] * dx
        # Subtract crew point loads
        for pos, load in zip(crew_pos, crew_load):
            if x_ft[i - 1] < pos <= x_ft[i]:
                V[i] -= load

    # Bending moment by integrating shear
    M = np.zeros(n)
    for i in range(1, n):
        M[i] = M[i - 1] + V[i] * dx

    return V, M, b_dist, b_max


# ============================================================================
# FIGURE 1: FREE BODY DIAGRAM + SHEAR + MOMENT
# ============================================================================
def generate_figure1():
    """Generate the FBD with Shear and Bending Moment diagrams."""
    print("Generating Figure 1: FBD with Shear and Bending Moment...")

    N = 2000
    x = np.linspace(0, L_ft, N)
    dx = x[1] - x[0]

    crew_loads = [W_crew_each] * n_crew

    V, M, b_dist, b_max = compute_shear_moment(
        x, L_ft, W_total, W_hull, crew_pos_ft, crew_loads
    )

    # Convert moment to lb-ft (it's already in lb*ft from integration)
    M_lbft = M  # Already in lb-ft since x is in ft and forces in lb

    # Find extremes
    V_max_val = np.max(np.abs(V))
    V_max_idx = np.argmax(np.abs(V))
    M_max_val = np.max(np.abs(M_lbft))
    M_max_idx = np.argmax(np.abs(M_lbft))
    M_actual_max = M_lbft[M_max_idx]

    # -----------------------------------------------------------------------
    # Create figure
    # -----------------------------------------------------------------------
    fig, axes = plt.subplots(3, 1, figsize=(13, 12), gridspec_kw={
        'height_ratios': [1.4, 0.8, 0.8], 'hspace': 0.25
    })
    fig.patch.set_facecolor('white')

    # === Title ===
    fig.suptitle(
        "Figure 1: Free Body Diagram w/ Shear Force and Bending Moment",
        fontsize=16, fontweight='bold', color=DARK_GRAY, y=0.97
    )
    fig.text(
        0.5, 0.94,
        'NAU Concrete Canoe 2026 \u2014 Design A (192" \u00d7 32" \u00d7 17")',
        fontsize=12, ha='center', color=MEDIUM_GRAY, style='italic'
    )

    # ===================================================================
    # TOP PANEL: FREE BODY DIAGRAM
    # ===================================================================
    ax1 = axes[0]
    ax1.set_xlim(-0.5, L_ft + 0.5)
    ax1.set_ylim(-3.5, 5.0)
    ax1.set_aspect('auto')
    ax1.set_ylabel('', fontsize=10)
    ax1.set_title('Free Body Diagram', fontsize=13, fontweight='bold',
                   color=DARK_GRAY, pad=8)

    # --- Hull Profile ---
    # Draw the canoe hull as a filled shape
    hull_y_center = 1.0  # vertical center of hull in plot coords
    hull_half_height = 0.35

    # Hull outline - canoe shape
    x_hull = np.linspace(0, L_ft, 200)
    xi_hull = x_hull / L_ft
    # Top profile
    hull_width_factor = np.sin(np.pi * xi_hull) ** 0.35
    hull_top = hull_y_center + hull_half_height * hull_width_factor
    hull_bot = hull_y_center - hull_half_height * hull_width_factor * 0.8

    # Fill hull body
    ax1.fill_between(x_hull, hull_bot, hull_top, color='#d5dbdb',
                      edgecolor=DARK_GRAY, linewidth=1.5, zorder=5)
    # Hull centerline
    ax1.plot(x_hull, np.full_like(x_hull, hull_y_center), '--',
             color=MEDIUM_GRAY, linewidth=0.5, zorder=6)

    # BOW and STERN labels
    ax1.text(-0.3, hull_y_center, 'BOW', fontsize=11, fontweight='bold',
             ha='right', va='center', color=DARK_GRAY)
    ax1.text(L_ft + 0.3, hull_y_center, 'STERN', fontsize=11,
             fontweight='bold', ha='left', va='center', color=DARK_GRAY)

    # --- Buoyancy (upward distributed load) ---
    # Draw filled buoyancy region below hull
    buoy_base_y = -2.8
    buoy_scale = 2.0 / b_max  # scale so max buoyancy arrow reaches hull bottom

    # Buoyancy profile curve
    x_buoy = np.linspace(0.1, L_ft - 0.1, 300)
    b_buoy, _ = buoyancy_distribution(x_buoy, L_ft, W_total)
    buoy_top = buoy_base_y + b_buoy * buoy_scale

    # Fill the buoyancy region
    ax1.fill_between(x_buoy, buoy_base_y, buoy_top,
                      color=BLUE_LIGHT, alpha=0.4, zorder=2)
    ax1.plot(x_buoy, buoy_top, color=BLUE, linewidth=2.0, zorder=3)
    ax1.plot(x_buoy, np.full_like(x_buoy, buoy_base_y), color=BLUE,
             linewidth=1.0, zorder=3)

    # Draw upward buoyancy arrows (spaced evenly)
    n_arrows = 25
    arrow_x_positions = np.linspace(0.4, L_ft - 0.4, n_arrows)
    for ax_pos in arrow_x_positions:
        b_val, _ = buoyancy_distribution(np.array([ax_pos]), L_ft, W_total)
        b_val = b_val[0]
        if b_val > 5:  # only draw if significant
            arr_top = buoy_base_y + b_val * buoy_scale
            ax1.annotate('', xy=(ax_pos, arr_top + 0.15),
                         xytext=(ax_pos, buoy_base_y + 0.05),
                         arrowprops=dict(arrowstyle='->', color=BLUE,
                                         lw=1.2, mutation_scale=10),
                         zorder=4)

    # Buoyancy label
    mid_b, _ = buoyancy_distribution(np.array([L_ft / 2]), L_ft, W_total)
    ax1.text(L_ft / 2, buoy_base_y - 0.35,
             f'Buoyancy (sinusoidal dist.)\nb$_{{max}}$ = {b_max:.1f} lb/ft',
             fontsize=9, ha='center', va='top', color=BLUE,
             fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                       edgecolor=BLUE, alpha=0.9))

    # --- Hull self-weight (downward distributed) ---
    n_w_arrows = 30
    w_arrow_x = np.linspace(0.3, L_ft - 0.3, n_w_arrows)
    hull_w_arrow_len = 0.7
    for wx in w_arrow_x:
        # Position arrows on top of hull
        idx = int(wx / L_ft * (len(x_hull) - 1))
        idx = np.clip(idx, 0, len(x_hull) - 1)
        y_start = hull_top[idx] + hull_w_arrow_len + 0.05
        y_end = hull_top[idx] + 0.05
        ax1.annotate('', xy=(wx, y_end), xytext=(wx, y_start),
                     arrowprops=dict(arrowstyle='->', color=RED,
                                     lw=0.9, mutation_scale=8),
                     zorder=6)

    # Hull weight distribution line on top
    hw_line_y = hull_top + hull_w_arrow_len + 0.05
    ax1.plot(x_hull, hw_line_y, color=RED, linewidth=1.5, zorder=6)

    # Hull weight label
    ax1.text(L_ft * 0.82, hull_top[int(0.82 * len(hull_top))] + hull_w_arrow_len + 0.5,
             f'w$_{{hull}}$ = {w_hull_per_ft:.1f} lb/ft\n({W_hull} lb total)',
             fontsize=9, ha='center', va='bottom', color=RED,
             fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                       edgecolor=RED, alpha=0.9))

    # --- Crew point loads (downward) ---
    for i, (pos, load) in enumerate(zip(crew_pos_ft, crew_loads)):
        idx = int(pos / L_ft * (len(x_hull) - 1))
        idx = np.clip(idx, 0, len(x_hull) - 1)
        y_hull_top_at = hull_top[idx]

        # Large downward arrow
        arrow_start_y = y_hull_top_at + hull_w_arrow_len + 1.5
        arrow_end_y = y_hull_top_at + 0.05

        ax1.annotate('', xy=(pos, arrow_end_y), xytext=(pos, arrow_start_y),
                     arrowprops=dict(arrowstyle='->', color=PURPLE,
                                     lw=3.0, mutation_scale=18),
                     zorder=8)

        # Crew label
        crew_label = f'{int(load)} lb'
        ax1.text(pos, arrow_start_y + 0.15, crew_label,
                 fontsize=10, fontweight='bold', ha='center', va='bottom',
                 color=PURPLE,
                 bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                           edgecolor=PURPLE, alpha=0.9))

        # Position marker
        ax1.text(pos, arrow_start_y + 0.65,
                 f'Crew {i + 1}\n({pos:.1f} ft)',
                 fontsize=7, ha='center', va='bottom', color=PURPLE)

    # Axis styling for FBD
    ax1.set_xlim(-1.0, L_ft + 1.0)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.set_xticks([])
    ax1.set_yticks([])

    # Length dimension line below buoyancy
    dim_y = -3.3
    ax1.annotate('', xy=(L_ft, dim_y), xytext=(0, dim_y),
                 arrowprops=dict(arrowstyle='<->', color=DARK_GRAY, lw=1.2))
    ax1.text(L_ft / 2, dim_y - 0.2, f'L = {L_ft:.0f} ft ({L_in:.0f}")',
             fontsize=10, ha='center', va='top', color=DARK_GRAY,
             fontweight='bold')

    # ===================================================================
    # MIDDLE PANEL: SHEAR FORCE DIAGRAM
    # ===================================================================
    ax2 = axes[1]
    ax2.set_title('Shear Force Diagram', fontsize=13, fontweight='bold',
                   color=DARK_GRAY, pad=8)

    # Fill positive shear blue, negative red
    V_pos = np.where(V >= 0, V, 0)
    V_neg = np.where(V < 0, V, 0)
    ax2.fill_between(x, V_pos, 0, color=BLUE_LIGHT, alpha=0.6, zorder=2)
    ax2.fill_between(x, V_neg, 0, color=RED_LIGHT, alpha=0.6, zorder=2)
    ax2.plot(x, V, color=DARK_GRAY, linewidth=2.0, zorder=3)
    ax2.axhline(y=0, color=DARK_GRAY, linewidth=0.8, zorder=1)

    # Mark V_max
    # Find positive max and negative max
    V_pos_max_idx = np.argmax(V)
    V_neg_min_idx = np.argmin(V)
    V_pos_max = V[V_pos_max_idx]
    V_neg_min = V[V_neg_min_idx]

    if abs(V_pos_max) >= abs(V_neg_min):
        vm_idx, vm_val = V_pos_max_idx, V_pos_max
    else:
        vm_idx, vm_val = V_neg_min_idx, V_neg_min

    # Mark both positive and negative extremes
    for idx_mark, val_mark, label_prefix in [
        (V_pos_max_idx, V_pos_max, 'V$_{max}$'),
        (V_neg_min_idx, V_neg_min, 'V$_{min}$')
    ]:
        color = BLUE if val_mark >= 0 else RED
        ax2.plot(x[idx_mark], val_mark, 'o', color=color, markersize=7, zorder=5)
        offset_y = 30 if val_mark >= 0 else -30
        ax2.annotate(
            f'{label_prefix} = {val_mark:.0f} lb\nat x = {x[idx_mark]:.1f} ft',
            xy=(x[idx_mark], val_mark),
            xytext=(20, offset_y),
            textcoords='offset points',
            fontsize=9, fontweight='bold', color=color,
            arrowprops=dict(arrowstyle='->', color=color, lw=1.2),
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor=color, alpha=0.9)
        )

    # Mark crew load positions with vertical dashed lines
    for pos in crew_pos_ft:
        ax2.axvline(x=pos, color=PURPLE, linewidth=0.8, linestyle='--',
                     alpha=0.5, zorder=1)

    ax2.set_ylabel('Shear Force (lb)', fontsize=11, fontweight='bold',
                    color=DARK_GRAY)
    ax2.set_xlim(0, L_ft)
    ax2.grid(True, alpha=0.3, linewidth=0.5)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.tick_params(labelsize=9)

    # ===================================================================
    # BOTTOM PANEL: BENDING MOMENT DIAGRAM
    # ===================================================================
    ax3 = axes[2]
    ax3.set_title('Bending Moment Diagram', fontsize=13, fontweight='bold',
                   color=DARK_GRAY, pad=8)

    # Fill moment diagram
    M_pos = np.where(M_lbft >= 0, M_lbft, 0)
    M_neg = np.where(M_lbft < 0, M_lbft, 0)
    ax3.fill_between(x, M_pos, 0, color=RED_LIGHT, alpha=0.5, zorder=2)
    ax3.fill_between(x, M_neg, 0, color=BLUE_LIGHT, alpha=0.5, zorder=2)
    ax3.plot(x, M_lbft, color=RED, linewidth=2.5, zorder=3)
    ax3.axhline(y=0, color=DARK_GRAY, linewidth=0.8, zorder=1)

    # Mark M_max
    ax3.plot(x[M_max_idx], M_actual_max, 'o', color=RED, markersize=9,
             zorder=5, markeredgecolor='white', markeredgewidth=1.5)
    ax3.annotate(
        f'M$_{{max}}$ = {M_actual_max:.0f} lb-ft\nat x = {x[M_max_idx]:.1f} ft',
        xy=(x[M_max_idx], M_actual_max),
        xytext=(40, 25),
        textcoords='offset points',
        fontsize=10, fontweight='bold', color=RED,
        arrowprops=dict(arrowstyle='->', color=RED, lw=1.5),
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                  edgecolor=RED, alpha=0.95)
    )

    # Also mark minimum moment if significant
    M_min_idx = np.argmin(M_lbft)
    M_min_val = M_lbft[M_min_idx]
    if abs(M_min_val) > 20:
        ax3.plot(x[M_min_idx], M_min_val, 'o', color=BLUE, markersize=7,
                 zorder=5)
        ax3.annotate(
            f'M$_{{min}}$ = {M_min_val:.0f} lb-ft',
            xy=(x[M_min_idx], M_min_val),
            xytext=(-30, -25),
            textcoords='offset points',
            fontsize=8, color=BLUE,
            arrowprops=dict(arrowstyle='->', color=BLUE, lw=1.0),
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                      edgecolor=BLUE, alpha=0.9)
        )

    # Crew position markers
    for pos in crew_pos_ft:
        ax3.axvline(x=pos, color=PURPLE, linewidth=0.8, linestyle='--',
                     alpha=0.5, zorder=1)

    ax3.set_ylabel('Bending Moment (lb-ft)', fontsize=11, fontweight='bold',
                    color=DARK_GRAY)
    ax3.set_xlabel('Position along hull (ft)', fontsize=11, fontweight='bold',
                    color=DARK_GRAY)
    ax3.set_xlim(0, L_ft)
    ax3.grid(True, alpha=0.3, linewidth=0.5)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.tick_params(labelsize=9)

    # ===================================================================
    # EQUILIBRIUM CHECK ANNOTATION
    # ===================================================================
    equil_text = (
        r"$\Sigma F_y = 0$: Buoyancy (871 lb) = Hull (171 lb) + Crew (700 lb) $\checkmark$"
    )
    fig.text(0.5, 0.015, equil_text, fontsize=11, ha='center', va='bottom',
             color=GREEN, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#eafaf1',
                       edgecolor=GREEN, alpha=0.95))

    # Legend
    legend_elements = [
        Line2D([0], [0], color=BLUE, lw=2, label='Buoyancy (upward)'),
        Line2D([0], [0], color=RED, lw=2, label=f'Hull weight ({w_hull_per_ft:.1f} lb/ft)'),
        Line2D([0], [0], color=PURPLE, lw=3, label=f'Crew loads (4 x {W_crew_each:.0f} lb)'),
    ]
    axes[0].legend(handles=legend_elements, loc='upper left', fontsize=9,
                   framealpha=0.9, edgecolor=MEDIUM_GRAY)

    plt.subplots_adjust(top=0.91, bottom=0.07, left=0.08, right=0.95)

    # Save
    outpath = '/root/concrete-canoe-project2026/reports/figures/report_fig1_fbd_buoyancy.png'
    fig.savefig(outpath, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {outpath}")
    return outpath


# ============================================================================
# FIGURE 2: MOMENT OF INERTIA - PARALLEL AXIS THEOREM
# ============================================================================
def generate_figure2():
    """Generate the MOI cross-section and calculation diagram."""
    print("Generating Figure 2: Moment of Inertia - Parallel Axis Theorem...")

    # Section properties
    B_sec = 32.0    # beam width (in)
    D_sec = 17.0    # total depth (in)
    t_sec = 0.5     # wall thickness (in)

    # Component dimensions
    # Rect 1: Bottom plate
    b1 = B_sec       # 32"
    h1 = t_sec       # 0.5"
    A1 = b1 * h1     # 16.0 in^2
    y1 = h1 / 2      # 0.250"

    # Rect 2,3: Side walls (height = D - t for bottom plate)
    b2 = t_sec        # 0.5"
    h2 = D_sec - t_sec  # 16.5"
    A2 = b2 * h2      # 8.25 in^2
    y2 = t_sec + h2 / 2  # 0.5 + 8.25 = 8.750"

    # Neutral axis
    A_total = A1 + 2 * A2
    y_NA = (A1 * y1 + 2 * A2 * y2) / A_total

    # Individual moments of inertia about own centroid
    Ic1 = b1 * h1**3 / 12
    Ic2 = b2 * h2**3 / 12

    # Distances to NA
    d1 = abs(y_NA - y1)
    d2 = abs(y_NA - y2)

    # Parallel axis terms
    Ad1_sq = A1 * d1**2
    Ad2_sq = A2 * d2**2

    # Total I
    I_total = Ic1 + Ad1_sq + 2 * (Ic2 + Ad2_sq)

    # Section modulus
    c_top = D_sec - y_NA  # distance to top fiber
    c_bot = y_NA           # distance to bottom fiber
    c_max = max(c_top, c_bot)
    S_x = I_total / c_max
    S_design = S_x * 0.75  # ACI thin-shell reduction

    # -----------------------------------------------------------------------
    # Create figure
    # -----------------------------------------------------------------------
    fig, (ax_cs, ax_calc) = plt.subplots(1, 2, figsize=(16, 10),
                                          gridspec_kw={'width_ratios': [1, 1.1]})
    fig.patch.set_facecolor('white')

    fig.suptitle(
        "Figure 2: Moment of Inertia \u2014 Parallel Axis Theorem",
        fontsize=16, fontweight='bold', color=DARK_GRAY, y=0.97
    )
    fig.text(
        0.5, 0.935,
        'Midship Cross-Section (B=32", D=17", t=0.5")',
        fontsize=12, ha='center', color=MEDIUM_GRAY, style='italic'
    )

    # ===================================================================
    # LEFT PANEL: CROSS-SECTION DRAWING
    # ===================================================================
    ax = ax_cs
    ax.set_title('Cross-Section (U-Shell)', fontsize=13, fontweight='bold',
                  color=DARK_GRAY, pad=12)

    # Exaggerated thickness for visibility
    t_vis = 2.0  # Visual thickness (4x exaggeration)
    scale = 1.0

    # Draw the U-section with exaggerated thickness
    # Outer boundary
    outer_left = 0
    outer_right = B_sec
    outer_bottom = 0
    outer_top = D_sec

    # Bottom plate (RECT 1) - BLUE
    bottom_plate = plt.Rectangle(
        (outer_left, 0), B_sec, t_vis,
        facecolor=BLUE_LIGHT, edgecolor=BLUE, linewidth=2.0, zorder=3
    )
    ax.add_patch(bottom_plate)

    # Left wall (RECT 2) - RED
    left_wall = plt.Rectangle(
        (outer_left, t_vis), t_vis, D_sec - t_vis,
        facecolor=RED_LIGHT, edgecolor=RED, linewidth=2.0, zorder=3
    )
    ax.add_patch(left_wall)

    # Right wall (RECT 3) - RED
    right_wall = plt.Rectangle(
        (B_sec - t_vis, t_vis), t_vis, D_sec - t_vis,
        facecolor=RED_LIGHT, edgecolor=RED, linewidth=2.0, zorder=3
    )
    ax.add_patch(right_wall)

    # Outer outline
    outline_x = [0, B_sec, B_sec, B_sec - t_vis, B_sec - t_vis,
                 t_vis, t_vis, 0, 0]
    outline_y = [0, 0, D_sec, D_sec, t_vis, t_vis, D_sec, D_sec, 0]
    ax.plot(outline_x, outline_y, color=DARK_GRAY, linewidth=2.5, zorder=4)

    # --- Neutral Axis ---
    ax.axhline(y=y_NA, color=GREEN, linewidth=2.5, linestyle='--', zorder=5,
               label=f'Neutral Axis (y$_{{NA}}$ = {y_NA:.2f}")')
    ax.text(B_sec + 1.5, y_NA,
            f'N.A.\ny$_{{NA}}$ = {y_NA:.2f}"',
            fontsize=10, fontweight='bold', color=GREEN, va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#eafaf1',
                      edgecolor=GREEN, alpha=0.9))

    # --- Centroid markers ---
    # Rect 1 centroid
    cx1 = B_sec / 2
    cy1 = t_vis / 2  # visual centroid of bottom plate
    ax.plot(cx1, cy1, 'o', color=BLUE, markersize=10, zorder=6,
            markeredgecolor='white', markeredgewidth=1.5)
    ax.text(cx1 + 2, cy1, f'C$_1$ (\u0233$_1$={y1:.3f}")',
            fontsize=9, color=BLUE, fontweight='bold', va='center')

    # Rect 2 centroid (left wall)
    cx2 = t_vis / 2
    cy2 = t_vis + (D_sec - t_vis) / 2  # visual centroid
    ax.plot(cx2, cy2, 'o', color=RED, markersize=10, zorder=6,
            markeredgecolor='white', markeredgewidth=1.5)
    ax.text(cx2 + 2.5, cy2 + 0.5, f'C$_2$ (\u0233$_2$={y2:.3f}")',
            fontsize=9, color=RED, fontweight='bold', va='center')

    # Rect 3 centroid (right wall)
    cx3 = B_sec - t_vis / 2
    cy3 = cy2
    ax.plot(cx3, cy3, 'o', color=RED, markersize=10, zorder=6,
            markeredgecolor='white', markeredgewidth=1.5)
    ax.text(cx3 - 12, cy3 + 0.5, f'C$_3$ (\u0233$_3$={y2:.3f}")',
            fontsize=9, color=RED, fontweight='bold', va='center')

    # --- Distance arrows from centroids to NA ---
    # d1: bottom plate centroid to NA
    ax.annotate('', xy=(B_sec * 0.35, y_NA), xytext=(B_sec * 0.35, cy1),
                arrowprops=dict(arrowstyle='<->', color=ORANGE, lw=2.0))
    ax.text(B_sec * 0.35 + 1.5, (cy1 + y_NA) / 2,
            f'd$_1$ = {d1:.2f}"',
            fontsize=9, fontweight='bold', color=ORANGE, va='center')

    # d2: side wall centroid to NA
    ax.annotate('', xy=(B_sec * 0.7, y_NA), xytext=(B_sec * 0.7, cy2),
                arrowprops=dict(arrowstyle='<->', color=ORANGE, lw=2.0))
    ax.text(B_sec * 0.7 + 1.5, (cy2 + y_NA) / 2,
            f'd$_2$ = {d2:.2f}"',
            fontsize=9, fontweight='bold', color=ORANGE, va='center')

    # --- Dimension lines ---
    dim_offset = 3.5
    # Width dimension (B)
    ax.annotate('', xy=(B_sec, -dim_offset), xytext=(0, -dim_offset),
                arrowprops=dict(arrowstyle='<->', color=DARK_GRAY, lw=1.5))
    ax.text(B_sec / 2, -dim_offset - 1.0, f'B = {B_sec:.0f}"',
            fontsize=11, fontweight='bold', ha='center', color=DARK_GRAY)

    # Depth dimension (D) - right side
    ax.annotate('', xy=(B_sec + dim_offset + 3, D_sec),
                xytext=(B_sec + dim_offset + 3, 0),
                arrowprops=dict(arrowstyle='<->', color=DARK_GRAY, lw=1.5))
    ax.text(B_sec + dim_offset + 4.5, D_sec / 2, f'D = {D_sec:.0f}"',
            fontsize=11, fontweight='bold', ha='left', va='center',
            color=DARK_GRAY, rotation=90)

    # Thickness dimension (t) - at bottom plate
    ax.annotate('', xy=(B_sec / 2 + 5, t_vis),
                xytext=(B_sec / 2 + 5, 0),
                arrowprops=dict(arrowstyle='<->', color=MEDIUM_GRAY, lw=1.2))
    ax.text(B_sec / 2 + 6.5, t_vis / 2, f't = {t_sec:.1f}"',
            fontsize=9, fontweight='bold', va='center', color=MEDIUM_GRAY)

    # Component labels
    ax.text(B_sec / 2, -1.2,
            f'RECT 1 (Bottom Plate): {b1:.0f}" \u00d7 {h1:.1f}"',
            fontsize=9, ha='center', color=BLUE, fontweight='bold')

    ax.text(-5, D_sec / 2 + 2,
            f'RECT 2\n(Left Wall)\n{b2:.1f}" \u00d7 {h2:.1f}"',
            fontsize=8, ha='center', color=RED, fontweight='bold',
            va='center')

    ax.text(B_sec + 5, D_sec / 2 + 2,
            f'RECT 3\n(Right Wall)\n{b2:.1f}" \u00d7 {h2:.1f}"',
            fontsize=8, ha='center', color=RED, fontweight='bold',
            va='center')

    # Exaggeration note
    ax.text(B_sec / 2, D_sec + 2,
            '(thickness exaggerated 4\u00d7 for clarity)',
            fontsize=8, ha='center', va='bottom', color=MEDIUM_GRAY,
            style='italic')

    ax.set_xlim(-8, B_sec + 10)
    ax.set_ylim(-dim_offset - 2.5, D_sec + 3.5)
    ax.set_aspect('equal')
    ax.axis('off')

    # ===================================================================
    # RIGHT PANEL: CALCULATION BOX
    # ===================================================================
    ax_calc.axis('off')
    ax_calc.set_xlim(0, 10)
    ax_calc.set_ylim(0, 10)

    # Build calculation text
    calc_lines = [
        ("PARALLEL AXIS THEOREM", 'bold', 14, DARK_GRAY),
        (r"$I_{total} = \Sigma(I_{c,i} + A_i \cdot d_i^2)$", 'normal', 13, DARK_GRAY),
        ("", 'normal', 6, DARK_GRAY),
        ("\u2500" * 52, 'normal', 8, MEDIUM_GRAY),
        ("Component 1 \u2014 Bottom Plate (32\" \u00d7 0.5\")", 'bold', 11, BLUE),
        (f"  A\u2081 = {A1:.1f} in\u00b2          \u0233\u2081 = {y1:.3f}\"", 'normal', 10, DARK_GRAY),
        (f"  I_c1 = {b1}\u00d7{h1}\u00b3/12 = {Ic1:.3f} in\u2074", 'normal', 10, DARK_GRAY),
        (f"  d\u2081 = |{y_NA:.2f} - {y1:.2f}| = {d1:.2f}\"", 'normal', 10, ORANGE),
        (f"  A\u2081d\u2081\u00b2 = {A1:.1f} \u00d7 {d1**2:.2f} = {Ad1_sq:.1f} in\u2074", 'normal', 10, DARK_GRAY),
        ("", 'normal', 4, DARK_GRAY),
        ("\u2500" * 52, 'normal', 8, MEDIUM_GRAY),
        ("Components 2,3 \u2014 Side Walls (0.5\" \u00d7 16.5\" each)", 'bold', 11, RED),
        (f"  A\u2082 = {A2:.2f} in\u00b2        \u0233\u2082 = {y2:.3f}\"", 'normal', 10, DARK_GRAY),
        (f"  I_c2 = {b2}\u00d7{h2}\u00b3/12 = {Ic2:.2f} in\u2074", 'normal', 10, DARK_GRAY),
        (f"  d\u2082 = |{y_NA:.2f} - {y2:.2f}| = {d2:.2f}\"", 'normal', 10, ORANGE),
        (f"  A\u2082d\u2082\u00b2 = {A2:.2f} \u00d7 {d2**2:.2f} = {Ad2_sq:.1f} in\u2074", 'normal', 10, DARK_GRAY),
        ("", 'normal', 4, DARK_GRAY),
        ("\u2500" * 52, 'normal', 8, MEDIUM_GRAY),
        ("TOTALS", 'bold', 12, DARK_GRAY),
        (f"  I_total = {Ic1:.2f} + {Ad1_sq:.1f} + 2\u00d7({Ic2:.2f} + {Ad2_sq:.1f})", 'normal', 10, DARK_GRAY),
        (f"  I_total = {I_total:.1f} in\u2074", 'bold', 12, GREEN),
        ("", 'normal', 4, DARK_GRAY),
        ("\u2500" * 52, 'normal', 8, MEDIUM_GRAY),
        ("SECTION MODULUS", 'bold', 12, DARK_GRAY),
        (f"  c_max = {D_sec} - {y_NA:.2f} = {c_max:.2f}\" (top fiber)", 'normal', 10, DARK_GRAY),
        (f"  S_x = I/c = {I_total:.1f}/{c_max:.2f} = {S_x:.1f} in\u00b3", 'normal', 10, DARK_GRAY),
        (f"  S_design = {S_x:.1f} \u00d7 0.75 = {S_design:.1f} in\u00b3", 'bold', 11, GREEN),
        ("  (ACI thin-shell reduction factor)", 'normal', 9, MEDIUM_GRAY),
    ]

    # Render calculation text
    y_pos = 9.6
    for text, weight, size, color in calc_lines:
        if text == "":
            y_pos -= size * 0.015
            continue
        ax_calc.text(0.3, y_pos, text, fontsize=size, fontweight=weight,
                     color=color, family='monospace', va='top',
                     transform=ax_calc.transAxes if False else ax_calc.transData)
        y_pos -= size * 0.032

    # Add a border around the calculation
    calc_box = FancyBboxPatch(
        (0.05, y_pos - 0.2), 9.9, 9.8 - y_pos + 0.2,
        boxstyle='round,pad=0.15',
        facecolor='#fdfefe', edgecolor=MEDIUM_GRAY,
        linewidth=1.5, zorder=0
    )
    ax_calc.add_patch(calc_box)

    plt.subplots_adjust(top=0.90, bottom=0.04, left=0.03, right=0.97,
                        wspace=0.05)

    # Save
    outpath = '/root/concrete-canoe-project2026/reports/figures/report_fig2_moi_rectangles.png'
    fig.savefig(outpath, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {outpath}")
    return outpath


# ============================================================================
# MAIN
# ============================================================================
if __name__ == '__main__':
    # Ensure output directory exists
    os.makedirs('/root/concrete-canoe-project2026/reports/figures', exist_ok=True)

    print("=" * 65)
    print("NAU ASCE 2026 Concrete Canoe - Structural Engineering Diagrams")
    print("=" * 65)
    print(f"\nDesign A Parameters:")
    print(f"  Length = {L_in:.0f}\" ({L_ft:.0f} ft)")
    print(f"  Beam = {B:.0f}\", Depth = {D:.0f}\", Thickness = {t:.1f}\"")
    print(f"  Hull weight = {W_hull:.0f} lbs ({w_hull_per_ft:.1f} lb/ft)")
    print(f"  Crew = {n_crew} x {W_crew_each:.0f} = {W_crew:.0f} lbs")
    print(f"  Total loaded weight = {W_total:.0f} lbs")
    print()

    path1 = generate_figure1()
    print()
    path2 = generate_figure2()

    print()
    print("=" * 65)
    print("DONE. Both figures generated successfully.")
    print(f"  Figure 1: {path1}")
    print(f"  Figure 2: {path2}")
    print("=" * 65)
