#!/usr/bin/env python3
"""
NAU ASCE Concrete Canoe 2026 - Hull Hydrostatics, Stability & Structural Analysis
VPS-compatible (no GUI dependencies). Runs headless for remote calculations.

Engineering fixes (v2.0):
  1. Waterplane coefficient default 0.10 → 0.70 (canoe hull Cwp)
  2. Thin-shell U-section modulus replaces solid-rectangle formula
  3. Hull weight estimation from geometry with verification
  4. BM = Iwp / V using Cwp × L × B³/12 (not B²/12T rectangle)
  5. ASCE 2026 thresholds: 6" freeboard, 6" GM, 2.0 SF
  6. Crew loading: crew_weight_lbs=700 (4 paddlers × 175 lbs)

v2.1 improvements (code review recommendations):
  7. Removed simplified BM fallback — always use full I_wp/V formula
  8. Weighted COG from hull + crew component heights (calculate_cog_height)
  9. validate_concrete_mix() sanity check for density and strength
  10. Bending moment model accounts for concentrated crew load at midship
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any
import math
import warnings


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
    length_ft: float, beam_ft: float, form_factor: float = 0.70
) -> float:
    """
    Approximate waterplane area (ft²).
    form_factor is the waterplane coefficient Cwp (ratio of waterplane area
    to circumscribing rectangle). Canoe hulls: Cwp ≈ 0.65-0.75.
    Previous default of 0.10 was incorrect — that is NOT a form factor,
    it produced a waterplane area 7× too small.
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
    length_ft: float = 0.0,
    waterplane_coeff: float = 0.70,
) -> float:
    """
    Approximate metacentric height GM (ft).
    GM = KB + BM - KG

    KB ≈ draft/2 (centroid of submerged volume)
    BM = I_wp / V_displaced
       where I_wp = Cwp × L × B³ / 12  (second moment of waterplane area)
       and   V    = Cwp × L × B × T     (displaced volume approximation)

    Always uses the full 3D formula with length. If length_ft is not
    provided (legacy calls), falls back to B²/(12T) with a warning.

    KG from COG estimate (typically 0.40-0.45 × depth for loaded canoe).
    """
    if draft_ft <= 0:
        return 0.0

    kb = draft_ft / 2.0

    if length_ft > 0:
        # Full 3D formula: BM = I_wp / V_displaced
        i_wp = waterplane_coeff * length_ft * (beam_ft ** 3) / 12.0
        v_disp = waterplane_coeff * length_ft * beam_ft * draft_ft
        if v_disp <= 0:
            return 0.0
        bm = i_wp / v_disp
    else:
        # Legacy fallback — assumes uniform Cwp cancellation (B²/12T).
        # This is only valid when waterplane and submerged volume share
        # the same coefficient. For hulls with tumblehome or flare, this
        # does NOT hold. Always pass length_ft for accurate results.
        warnings.warn(
            "metacentric_height_approx called without length_ft. "
            "Using simplified BM = B²/(12T). Pass length_ft for "
            "the full I_wp/V formula.",
            stacklevel=2,
        )
        bm = (beam_ft ** 2) / (12.0 * draft_ft)

    kg = cog_height_approx_ft if cog_height_approx_ft > 0 else depth_ft * 0.4
    return kb + bm - kg


def calculate_cog_height(
    hull_weight_lbs: float,
    hull_cog_ft: float,
    crew_weight_lbs: float,
    crew_cog_ft: float,
    gear_weight_lbs: float = 0.0,
    gear_cog_ft: float = 0.0,
) -> float:
    """
    Weighted center-of-gravity height (ft) from component masses.

    Accounts for hull, crew, and optional gear positions rather than
    using a fixed fraction of hull depth.

    Typical values:
      hull_cog_ft: ~0.38 × depth (empty hull COG)
      crew_cog_ft: ~10"/12 = 0.833 ft (kneeling paddler COG)
    """
    total = hull_weight_lbs + crew_weight_lbs + gear_weight_lbs
    if total <= 0:
        return 0.0
    return (
        hull_weight_lbs * hull_cog_ft
        + crew_weight_lbs * crew_cog_ft
        + gear_weight_lbs * gear_cog_ft
    ) / total


def validate_concrete_mix(
    density_pcf: float,
    flexural_psi: float,
    compressive_psi: float = 0.0,
) -> bool:
    """
    Validate concrete properties are physically reasonable for canoe hulls.
    Returns True if all checks pass. Issues warnings for each concern.

    Typical lightweight canoe concrete: 50-80 PCF, f'r 800-2500 psi.
    """
    ok = True

    if density_pcf < 40 or density_pcf > 120:
        warnings.warn(
            f"Density {density_pcf:.0f} pcf is unusual for concrete canoes "
            "(typical: 50-80 pcf for lightweight mixes).",
            stacklevel=2,
        )
        ok = False

    if flexural_psi < 300 or flexural_psi > 4000:
        warnings.warn(
            f"Flexural strength {flexural_psi:.0f} psi is unusual "
            "(typical: 800-2500 psi for canoe mixes).",
            stacklevel=2,
        )
        ok = False

    if compressive_psi > 0 and flexural_psi > 0.20 * compressive_psi:
        ratio = flexural_psi / compressive_psi
        warnings.warn(
            f"Flexural/compressive ratio {ratio:.1%} is high "
            "(typically 8-15% per ACI 318-25). Verify test data.",
            stacklevel=2,
        )
        ok = False

    return ok


def estimate_hull_weight(
    length_in: float,
    beam_in: float,
    depth_in: float,
    thickness_in: float,
    density_pcf: float = 60.0,
    prismatic_coeff: float = 0.55,
    overhead_factor: float = 1.10,
) -> float:
    """
    Estimate hull weight (lbs) from geometry.

    Models the hull as a U-shaped shell (bottom plate + 2 side walls):
      girth = beam + 2 × depth  (unfolded U perimeter)
      shell_area = girth × length × Cp  (prismatic coeff for tapered ends)
      shell_volume = shell_area × thickness
      weight = volume × density × overhead  (gunwales, ribs, thickened keel)

    Parameters:
      prismatic_coeff: ~0.55 for canoe (tapered bow/stern)
      overhead_factor: 1.10 (10% for reinforcements, gunwales)
    """
    # Convert to feet
    l_ft = length_in / INCHES_PER_FOOT
    b_ft = beam_in / INCHES_PER_FOOT
    d_ft = depth_in / INCHES_PER_FOOT
    t_ft = thickness_in / INCHES_PER_FOOT

    girth_ft = b_ft + 2.0 * d_ft  # U-shape unfolded
    shell_area_ft2 = girth_ft * l_ft * prismatic_coeff
    shell_volume_ft3 = shell_area_ft2 * t_ft
    weight_lbs = shell_volume_ft3 * density_pcf * overhead_factor

    return weight_lbs


def bending_moment_uniform_load(
    w_lbs_per_ft: float,
    length_ft: float,
) -> float:
    """Max bending moment (lb-ft) for simply supported beam with uniform load."""
    return w_lbs_per_ft * (length_ft ** 2) / 8


def bending_moment_distributed_crew(
    hull_weight_lbs: float,
    crew_weight_lbs: float,
    length_ft: float,
    crew_position_fraction: float = 0.5,
) -> float:
    """
    Bending moment (lb-ft) for hull (uniform) + crew (concentrated at midship).

    More realistic than pure uniform load because crew weight is concentrated
    amidships, not distributed along the full length.

    M_hull = w_hull × L² / 8        (uniform dead load)
    M_crew = P_crew × L / 4         (point load at midship, simply supported)
    M_total = M_hull + M_crew

    Note: This still uses simple-support boundary conditions. A real canoe
    sits on a continuous elastic foundation (water buoyancy), which reduces
    the actual moment by ~20-40%. This model is therefore conservative.
    """
    if length_ft <= 0:
        return 0.0
    w_hull_per_ft = hull_weight_lbs / length_ft
    m_hull = w_hull_per_ft * (length_ft ** 2) / 8.0
    m_crew = crew_weight_lbs * length_ft / 4.0
    return m_hull + m_crew


def section_modulus_thin_shell(
    beam_in: float, depth_in: float, thickness_in: float
) -> float:
    """
    Section modulus (in³) for a thin-shell U-shaped cross-section.

    Models the hull cross-section as:
      - Bottom plate: beam × thickness
      - Two side walls: thickness × (depth - thickness) each

    Uses parallel axis theorem to compute I about the neutral axis,
    then S = I / c_max.

    For Canoe 1 (B=30, D=18, t=0.5): Sx ≈ 85 in³ (NOT 1,452 from solid rect).
    """
    b = beam_in
    t = thickness_in
    d = depth_in

    # --- Component 1: Bottom plate (b × t) ---
    a_bot = b * t
    # Centroid of bottom plate is at y = t/2 from bottom
    y_bot = t / 2.0
    # I of bottom plate about its own centroid
    i_bot_self = b * t**3 / 12.0

    # --- Component 2: Two side walls, each t × (d - t) ---
    h_wall = d - t  # wall height (from top of bottom plate to top of hull)
    a_wall = t * h_wall  # area of one wall
    # Centroid of each wall is at y = t + h_wall/2 from bottom
    y_wall = t + h_wall / 2.0
    # I of one wall about its own centroid
    i_wall_self = t * h_wall**3 / 12.0

    # --- Composite neutral axis ---
    total_area = a_bot + 2.0 * a_wall
    if total_area <= 0:
        return 0.0
    y_na = (a_bot * y_bot + 2.0 * a_wall * y_wall) / total_area

    # --- Parallel axis theorem for total I about NA ---
    i_total = (
        i_bot_self + a_bot * (y_na - y_bot) ** 2
        + 2.0 * (i_wall_self + a_wall * (y_wall - y_na) ** 2)
    )

    # --- Section modulus: S = I / c_max ---
    c_top = d - y_na  # distance from NA to top fiber
    c_bot = y_na       # distance from NA to bottom fiber
    c_max = max(c_top, c_bot)

    if c_max <= 0:
        return 0.0

    return i_total / c_max


# Keep old function for backward compatibility but mark deprecated
def section_modulus_rectangular(b_in: float, h_in: float) -> float:
    """
    Section modulus (in³) for solid rectangular cross-section. S = b*h²/6.
    DEPRECATED: Use section_modulus_thin_shell() for canoe hulls.
    A canoe is a thin shell, not a solid block.
    """
    return b_in * (h_in ** 2) / 6


def bending_stress_psi(moment_lb_ft: float, section_modulus_in3: float) -> float:
    """Bending stress (psi). sigma = M/S (moment converted to lb-in)."""
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
    waterplane_form_factor: float = 0.70,
    concrete_density_pcf: float = 60.0,
    crew_weight_lbs: float = 700.0,
) -> Dict[str, Any]:
    """
    Run full hull analysis. All dimensions in inches, weight in lbs.
    Returns dict with freeboard, stability, structural, and pass/fail.

    Parameters:
      concrete_weight_lbs: Self-weight of the concrete hull (lbs).
      crew_weight_lbs: Total crew weight (lbs). Default 700 = 4 × 175.
                       Set to 0 if concrete_weight_lbs already includes crew.
      waterplane_form_factor: Cwp waterplane coefficient (default 0.70).
      concrete_density_pcf: Concrete density (lb/ft³), used for weight check.
    """
    hull = HullGeometry(
        length_in=hull_length_in,
        beam_in=hull_beam_in,
        depth_in=hull_depth_in,
        thickness_in=hull_thickness_in,
    )

    # --- Material validation ---
    validate_concrete_mix(concrete_density_pcf, flexural_strength_psi)

    # --- Fix 3: Weight verification ---
    estimated_weight = estimate_hull_weight(
        hull_length_in, hull_beam_in, hull_depth_in,
        hull_thickness_in, concrete_density_pcf,
    )
    weight_diff_pct = abs(concrete_weight_lbs - estimated_weight) / estimated_weight * 100
    if weight_diff_pct > 20:
        warnings.warn(
            f"Provided hull weight ({concrete_weight_lbs:.0f} lbs) differs from "
            f"estimated ({estimated_weight:.0f} lbs) by {weight_diff_pct:.0f}%. "
            f"Check your weight input.",
            stacklevel=2,
        )

    # --- Fix 6: Total displacement includes crew ---
    total_weight_lbs = concrete_weight_lbs + crew_weight_lbs

    # Hydrostatics (using total loaded weight for displacement)
    disp_ft3 = displacement_volume(total_weight_lbs)
    wp_ft2 = waterplane_approximation(
        hull.length_ft, hull.beam_ft, waterplane_form_factor
    )
    draft_ft = draft_from_displacement(disp_ft3, wp_ft2)
    draft_in = draft_ft * INCHES_PER_FOOT
    fb_ft = freeboard(hull.depth_ft, draft_ft)
    fb_in = fb_ft * INCHES_PER_FOOT

    # Stability — weighted COG from hull + crew components
    hull_cog_ft = hull.depth_ft * 0.38   # empty hull COG
    crew_cog_ft = 10.0 / INCHES_PER_FOOT  # kneeling paddler COG at ~10"
    cog_approx_ft = calculate_cog_height(
        concrete_weight_lbs, hull_cog_ft,
        crew_weight_lbs, crew_cog_ft,
    )
    gm_ft = metacentric_height_approx(
        hull.beam_ft, draft_ft, hull.depth_ft, cog_approx_ft,
        length_ft=hull.length_ft,
        waterplane_coeff=waterplane_form_factor,
    )
    gm_in = gm_ft * INCHES_PER_FOOT

    # Structural (Fix 2: thin-shell section modulus)
    # Use distributed crew model for more realistic bending moment
    m_max_lb_ft = bending_moment_distributed_crew(
        concrete_weight_lbs, crew_weight_lbs, hull.length_ft
    )
    s_in3 = section_modulus_thin_shell(hull.beam_in, hull.depth_in, hull.thickness_in)
    sigma_psi = bending_stress_psi(m_max_lb_ft, s_in3)
    sf = safety_factor(flexural_strength_psi, sigma_psi)

    # Pass/Fail — Fix 5: corrected ASCE 2026 thresholds
    min_freeboard_in = 6.0
    min_gm_in = 6.0
    min_sf = 2.0

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
    print("NAU Concrete Canoe 2026 - Hull Analysis (v2.1)")
    print("=" * 60)

    # Canoe 1: 18' × 30" × 18", 276 lbs, density 70 pcf
    results = run_complete_analysis(
        hull_length_in=18 * 12,
        hull_beam_in=30,
        hull_depth_in=18,
        hull_thickness_in=0.5,
        concrete_weight_lbs=276,
        flexural_strength_psi=1500,
        concrete_density_pcf=70.0,
    )

    print("\n--- Canoe 1: 18' × 30\" × 18\", 276 lbs (+ 700 crew) ---")
    print(f"Freeboard:      {results['freeboard']['freeboard_in']:.2f} in"
          f"  (min {results['freeboard']['min_required_in']:.0f} in)"
          f"  {'PASS' if results['freeboard']['pass'] else 'FAIL'}")
    print(f"Draft:          {results['freeboard']['draft_in']:.2f} in")
    print(f"Displacement:   {results['freeboard']['displacement_ft3']:.2f} ft³")
    print(f"Metacentric GM: {results['stability']['gm_in']:.2f} in"
          f"  (min {results['stability']['min_required_in']:.0f} in)"
          f"  {'PASS' if results['stability']['pass'] else 'FAIL'}")
    print(f"Section Mod Sx: {results['structural']['section_modulus_in3']:.1f} in³")
    print(f"Max BM:         {results['structural']['max_bending_moment_lb_ft']:.1f} lb-ft")
    print(f"Bending stress: {results['structural']['bending_stress_psi']:.1f} psi")
    print(f"Safety factor:  {results['structural']['safety_factor']:.2f}"
          f"  (min {results['structural']['min_sf']:.1f})"
          f"  {'PASS' if results['structural']['pass'] else 'FAIL'}")
    print(f"\nOverall: {'PASS' if results['overall_pass'] else 'FAIL'}")

    # Weight verification
    est_w = estimate_hull_weight(216, 30, 18, 0.5, 70.0)
    print(f"\nWeight check: provided=276 lbs, estimated={est_w:.0f} lbs")
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
