#!/usr/bin/env python3
"""
NAU ASCE Concrete Canoe 2026 - Hull Hydrostatics, Stability & Structural Analysis
VPS-compatible (no GUI dependencies). Runs headless for remote calculations.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any
import math


# Constants
WATER_DENSITY_LB_PER_FT3 = 62.4  # freshwater
GRAVITY_FT_S2 = 32.174
INCHES_PER_FOOT = 12


@dataclass
class HullGeometry:
    """Hull dimensions in inches."""
    length_in: float
    beam_in: float
    depth_in: float
    thickness_in: float

    @property
    def length_ft(self) -> float:
        return self.length_in / INCHES_PER_FOOT

    @property
    def beam_ft(self) -> float:
        return self.beam_in / INCHES_PER_FOOT

    @property
    def depth_ft(self) -> float:
        return self.depth_in / INCHES_PER_FOOT

    @property
    def thickness_ft(self) -> float:
        return self.thickness_in / INCHES_PER_FOOT


def waterplane_approximation(
    length_ft: float, beam_ft: float, form_factor: float = 0.10
) -> float:
    """
    Approximate waterplane area (ft²). Canoe hulls have tapered ends,
    so effective area << length×beam. form_factor ~0.08-0.15 typical.
    Calibrate against your Excel hydrostatics if needed.
    """
    return length_ft * beam_ft * form_factor


def displacement_volume(canoe_weight_lbs: float) -> float:
    """Displacement volume (ft³) from weight (Archimedes)."""
    return canoe_weight_lbs / WATER_DENSITY_LB_PER_FT3


def draft_from_displacement(
    displacement_ft3: float,
    waterplane_ft2: float,
) -> float:
    """Draft (ft) from displacement and waterplane area."""
    if waterplane_ft2 <= 0:
        return 0.0
    return displacement_ft3 / waterplane_ft2


def freeboard(depth_ft: float, draft_ft: float) -> float:
    """Freeboard (ft) = depth - draft."""
    return max(0.0, depth_ft - draft_ft)


def metacentric_height_approx(
    beam_ft: float,
    draft_ft: float,
    depth_ft: float,
    cog_height_approx_ft: float,
) -> float:
    """
    Approximate metacentric height GM (ft).
    GM = KB + BM - KG
    KB ≈ draft/2, BM ≈ beam²/(12*draft), KG from COG estimate.
    """
    if draft_ft <= 0:
        return 0.0
    kb = draft_ft / 2
    bm = (beam_ft ** 2) / (12 * draft_ft)
    kg = cog_height_approx_ft if cog_height_approx_ft > 0 else depth_ft * 0.4
    return kb + bm - kg


def bending_moment_uniform_load(
    w_lbs_per_ft: float,
    length_ft: float,
) -> float:
    """Max bending moment (lb-ft) for simply supported beam with uniform load."""
    return w_lbs_per_ft * (length_ft ** 2) / 8


def section_modulus_rectangular(b_in: float, h_in: float) -> float:
    """Section modulus (in³) for rectangular cross-section. S = b*h²/6"""
    return b_in * (h_in ** 2) / 6


def bending_stress_psi(moment_lb_ft: float, section_modulus_in3: float) -> float:
    """Bending stress (psi). sigma = M*c/I = M/S"""
    if section_modulus_in3 <= 0:
        return 0.0
    moment_lb_in = moment_lb_ft * INCHES_PER_FOOT
    return moment_lb_in / section_modulus_in3


def safety_factor(ultimate_stress_psi: float, design_stress_psi: float) -> float:
    """Safety factor = ultimate / design."""
    if design_stress_psi <= 0:
        return 0.0
    return ultimate_stress_psi / design_stress_psi


def run_complete_analysis(
    hull_length_in: float,
    hull_beam_in: float,
    hull_depth_in: float,
    hull_thickness_in: float,
    concrete_weight_lbs: float,
    flexural_strength_psi: float = 1500,
    waterplane_form_factor: float = 0.10,
    concrete_density_pcf: float = 60.0,  # Optional, for compatibility
) -> Dict[str, Any]:
    """
    Run full hull analysis. All dimensions in inches, weight in lbs.
    Returns dict with freeboard, stability, structural, and pass/fail.
    """
    hull = HullGeometry(
        length_in=hull_length_in,
        beam_in=hull_beam_in,
        depth_in=hull_depth_in,
        thickness_in=hull_thickness_in,
    )

    # Hydrostatics
    disp_ft3 = displacement_volume(concrete_weight_lbs)
    wp_ft2 = waterplane_approximation(
        hull.length_ft, hull.beam_ft, waterplane_form_factor
    )
    draft_ft = draft_from_displacement(disp_ft3, wp_ft2)
    draft_in = draft_ft * INCHES_PER_FOOT
    fb_ft = freeboard(hull.depth_ft, draft_ft)
    fb_in = fb_ft * INCHES_PER_FOOT

    # Stability
    cog_approx_ft = hull.depth_ft * 0.45
    gm_ft = metacentric_height_approx(
        hull.beam_ft, draft_ft, hull.depth_ft, cog_approx_ft
    )
    gm_in = gm_ft * INCHES_PER_FOOT

    # Structural
    w_per_ft = concrete_weight_lbs / hull.length_ft
    m_max_lb_ft = bending_moment_uniform_load(w_per_ft, hull.length_ft)
    # Hull cross-section: beam × (depth as effective)
    effective_depth = hull.depth_in - hull.thickness_in
    s_in3 = section_modulus_rectangular(hull.beam_in, effective_depth)
    sigma_psi = bending_stress_psi(m_max_lb_ft, s_in3)
    sf = safety_factor(flexural_strength_psi, sigma_psi)

    # Pass/Fail (ASCE 2026: min freeboard ~4–6", GM > 0 for stability)
    min_freeboard_in = 4.0
    min_gm_in = 0.5
    min_sf = 1.5

    pass_freeboard = fb_in >= min_freeboard_in
    pass_stability = gm_in >= min_gm_in
    pass_structural = sf >= min_sf
    is_adequate = pass_structural

    return {
        "hull": {
            "length_in": hull_length_in,
            "beam_in": hull_beam_in,
            "depth_in": hull_depth_in,
            "weight_lbs": concrete_weight_lbs,
        },
        "freeboard": {
            "freeboard_in": fb_in,
            "draft_in": draft_in,
            "displacement_ft3": disp_ft3,
            "pass": pass_freeboard,
            "min_required_in": min_freeboard_in,
        },
        "stability": {
            "gm_in": gm_in,
            "GM_in": gm_in,  # Alias for workflow compatibility
            "pass": pass_stability,
            "min_required_in": min_gm_in,
        },
        "structural": {
            "max_bending_moment_lb_ft": m_max_lb_ft,
            "bending_stress_psi": sigma_psi,
            "section_modulus_in3": s_in3,
            "safety_factor": sf,
            "flexural_strength_psi": flexural_strength_psi,
            "pass": pass_structural,
            "is_adequate": is_adequate,  # Alias for workflow compatibility
            "min_sf": min_sf,
        },
        "overall_pass": pass_freeboard and pass_stability and pass_structural,
    }


def main() -> None:
    """CLI entry - run analysis for default Canoe 1."""
    print("=" * 60)
    print("NAU Concrete Canoe 2026 - Hull Analysis")
    print("=" * 60)

    # Canoe 1: 18' × 30" × 18", 276 lbs
    results = run_complete_analysis(
        hull_length_in=18 * 12,
        hull_beam_in=30,
        hull_depth_in=18,
        hull_thickness_in=0.5,
        concrete_weight_lbs=276,
        flexural_strength_psi=1500,
    )

    print("\n--- Canoe 1: 18' × 30\" × 18\", 276 lbs ---")
    print(f"Freeboard:      {results['freeboard']['freeboard_in']:.2f} in (min {results['freeboard']['min_required_in']} in) {'✓' if results['freeboard']['pass'] else '✗'}")
    print(f"Draft:          {results['freeboard']['draft_in']:.2f} in")
    print(f"Metacentric GM: {results['stability']['gm_in']:.2f} in (min {results['stability']['min_required_in']} in) {'✓' if results['stability']['pass'] else '✗'}")
    print(f"Max BM:         {results['structural']['max_bending_moment_lb_ft']:.1f} lb-ft")
    print(f"Bending stress: {results['structural']['bending_stress_psi']:.0f} psi")
    print(f"Safety factor:  {results['structural']['safety_factor']:.2f} (min {results['structural']['min_sf']}) {'✓' if results['structural']['pass'] else '✗'}")
    print(f"\nOverall: {'PASS' if results['overall_pass'] else 'FAIL'}")
    print("=" * 60)


def visualize_hull_analysis(
    hull: HullGeometry,
    concrete_weight_lbs: float = 276,
    flexural_strength_psi: float = 1500,
    save: bool = True,
    show: bool = False,
):
    """
    Create 4 plots: Hull profile, cross-sections, stability curve, load distribution.
    save=True writes PNGs to reports/figures/; show=True displays (needs display).
    Returns list of figure objects.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return []

    results = run_complete_analysis(
        hull.length_in, hull.beam_in, hull.depth_in, hull.thickness_in,
        concrete_weight_lbs, flexural_strength_psi,
    )
    figures = []

    # 1. Hull profile (side silhouette)
    fig1, ax1 = plt.subplots(figsize=(10, 3))
    l_ft = hull.length_ft
    d_ft = hull.depth_ft
    rocker_rad = 2.5  # feet
    x = np.linspace(0, l_ft, 50)
    y_bottom = d_ft * 0.1 * np.sin(np.pi * x / l_ft)  # slight rocker
    ax1.fill_between(x, 0, d_ft, alpha=0.3)
    ax1.plot(x, d_ft + y_bottom * 0, "k-", lw=2)
    ax1.set_xlabel("Length (ft)")
    ax1.set_ylabel("Depth (ft)")
    ax1.set_title("Hull Profile (Side View)")
    ax1.set_aspect("equal")
    ax1.grid(True, alpha=0.3)
    figures.append(fig1)
    if save:
        out_dir = Path(__file__).parent.parent / "reports" / "figures"
        out_dir.mkdir(parents=True, exist_ok=True)
        fig1.savefig(out_dir / "1_hull_profile.png", dpi=100, bbox_inches="tight")
    if show:
        plt.show()

    # 2. Cross-sections (bow, midship, stern)
    fig2, axes = plt.subplots(1, 3, figsize=(12, 4))
    stations = [0.0, 0.5, 1.0]
    titles = ["Bow", "Midship", "Stern"]
    for ax, st, title in zip(axes, stations, titles):
        w = hull.beam_in / 12 * (0.3 + 0.7 * (1 - 2 * abs(st - 0.5)))
        h = hull.depth_in / 12
        theta = np.deg2rad(15)
        x_v = np.array([-w/2, 0, w/2])
        y_v = np.array([0, h * 0.2, 0])
        ax.fill(x_v, y_v, alpha=0.3)
        ax.plot(x_v, y_v, "k-", lw=2)
        ax.set_title(title)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
    fig2.suptitle("Hull Cross-Sections (V-Bottom)")
    figures.append(fig2)
    if save:
        fig2.savefig(out_dir / "2_cross_sections.png", dpi=100, bbox_inches="tight")

    # 3. Stability curve (GZ vs heel angle)
    fig3, ax3 = plt.subplots(figsize=(7, 4))
    gm_in = results["stability"]["gm_in"]
    angles = np.linspace(0, 90, 91)
    gz = gm_in * np.sin(np.deg2rad(angles))
    ax3.plot(angles, gz, "b-", lw=2)
    ax3.axhline(0, color="gray", ls="--")
    ax3.set_xlabel("Heel angle (deg)")
    ax3.set_ylabel("GZ (in)")
    ax3.set_title("Stability Curve (GZ vs Heel Angle)")
    ax3.grid(True, alpha=0.3)
    figures.append(fig3)
    if save:
        fig3.savefig(out_dir / "3_stability_curve.png", dpi=100, bbox_inches="tight")

    # 4. Load distribution / bending moment
    fig4, ax4 = plt.subplots(figsize=(8, 4))
    L = hull.length_ft
    w = concrete_weight_lbs / L
    x = np.linspace(0, L, 100)
    M = w * x * (L - x) / 2  # Simple beam
    ax4.fill_between(x, 0, M, alpha=0.3)
    ax4.plot(x, M, "b-", lw=2)
    ax4.axvline(L/2, color="r", ls="--", label="Max at midship")
    ax4.set_xlabel("Position (ft)")
    ax4.set_ylabel("Bending moment (lb-ft)")
    ax4.set_title("Bending Moment Distribution")
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    figures.append(fig4)
    if save:
        fig4.savefig(out_dir / "4_load_distribution.png", dpi=100, bbox_inches="tight")

    plt.close("all")
    return figures


if __name__ == "__main__":
    main()
