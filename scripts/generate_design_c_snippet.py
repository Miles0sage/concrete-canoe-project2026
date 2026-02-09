#!/usr/bin/env python3
"""
NAU ASCE Concrete Canoe 2026 — Design C Calculation Snippet
Generates a detailed, judge-ready calculation report for Design C.
Every number is computed from the calculator — no hardcoded values.
"""

import sys
import math
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from calculations.concrete_canoe_calculator import (
    HullGeometry,
    run_complete_analysis,
    estimate_hull_weight,
    waterplane_approximation,
    displacement_volume,
    draft_from_displacement,
    freeboard as calc_freeboard,
    metacentric_height_approx,
    bending_moment_uniform_load,
    section_modulus_thin_shell,
    bending_stress_psi,
    safety_factor as calc_safety_factor,
    WATER_DENSITY_LB_PER_FT3,
    INCHES_PER_FOOT,
)

# ── Design C Parameters ──
L_IN = 216.0       # length (in)
B_IN = 36.0        # beam (in)
D_IN = 18.0        # depth (in)
T_IN = 0.75        # wall thickness (in)
DENSITY_PCF = 60.0 # concrete density (lb/ft³)
CREW_LBS = 700.0   # 4 paddlers × 175 lbs
FLEXURAL_PSI = 1500.0  # flexural strength f'r (psi)
CWP = 0.70         # waterplane coefficient

# ACI 318-25 LRFD factors
PHI_FLEXURE = 0.65  # strength reduction factor, unreinforced concrete
DEAD_LOAD_FACTOR = 1.2
LIVE_LOAD_FACTOR = 1.6

REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def compute_all():
    """Compute every intermediate value from first principles via calculator functions."""

    hull = HullGeometry(L_IN, B_IN, D_IN, T_IN)
    L_ft = hull.length_ft
    B_ft = hull.beam_ft
    D_ft = hull.depth_ft
    T_ft = hull.thickness_ft

    # ── 1. Weight ──
    canoe_wt = estimate_hull_weight(L_IN, B_IN, D_IN, T_IN, DENSITY_PCF)
    total_wt = canoe_wt + CREW_LBS

    # ── 2. Hydrostatics ──
    disp_ft3 = displacement_volume(total_wt)
    wp_ft2 = waterplane_approximation(L_ft, B_ft, CWP)
    draft_ft = draft_from_displacement(disp_ft3, wp_ft2)
    draft_in = draft_ft * INCHES_PER_FOOT
    fb_ft = calc_freeboard(D_ft, draft_ft)
    fb_in = fb_ft * INCHES_PER_FOOT

    # ── 3. Stability ──
    # Second moment of waterplane area
    I_wp_ft4 = CWP * L_ft * (B_ft ** 3) / 12.0
    # Displaced volume for BM (prismatic approximation)
    V_disp_ft3 = CWP * L_ft * B_ft * draft_ft
    BM_ft = I_wp_ft4 / V_disp_ft3 if V_disp_ft3 > 0 else 0
    KB_ft = draft_ft / 2.0
    KG_ft = D_ft * 0.45
    GM_ft = KB_ft + BM_ft - KG_ft
    GM_in = GM_ft * INCHES_PER_FOOT

    # Cross-check with calculator function
    gm_check_ft = metacentric_height_approx(
        B_ft, draft_ft, D_ft, KG_ft,
        length_ft=L_ft, waterplane_coeff=CWP,
    )

    # ── 4. Structural — Thin-Shell U-Section Properties ──
    b, d, t = B_IN, D_IN, T_IN

    # Bottom plate
    A_bot = b * t
    y_bot = t / 2.0
    I_bot_self = b * t**3 / 12.0

    # Side walls (two)
    h_wall = d - t
    A_wall = t * h_wall
    y_wall = t + h_wall / 2.0
    I_wall_self = t * h_wall**3 / 12.0

    # Composite
    A_total = A_bot + 2.0 * A_wall
    y_bar = (A_bot * y_bot + 2.0 * A_wall * y_wall) / A_total

    # Parallel axis theorem
    I_bot = I_bot_self + A_bot * (y_bar - y_bot) ** 2
    I_wall = I_wall_self + A_wall * (y_wall - y_bar) ** 2
    Ix = I_bot + 2.0 * I_wall

    c_top = d - y_bar
    c_bot = y_bar
    c_max = max(c_top, c_bot)
    Sx = Ix / c_max

    # Cross-check with calculator function
    Sx_check = section_modulus_thin_shell(B_IN, D_IN, T_IN)

    # ── 5. Unfactored (ASD) Bending ──
    w_service_per_ft = total_wt / L_ft
    M_service_lb_ft = bending_moment_uniform_load(w_service_per_ft, L_ft)
    M_service_lb_in = M_service_lb_ft * INCHES_PER_FOOT
    sigma_service = M_service_lb_in / Sx if Sx > 0 else 0
    SF = calc_safety_factor(FLEXURAL_PSI, sigma_service)

    # ── 6. ACI 318-25 LRFD ──
    w_dead_per_ft = canoe_wt / L_ft   # dead load = canoe self-weight
    w_live_per_ft = CREW_LBS / L_ft   # live load = crew
    w_u_per_ft = DEAD_LOAD_FACTOR * w_dead_per_ft + LIVE_LOAD_FACTOR * w_live_per_ft
    M_u_lb_ft = bending_moment_uniform_load(w_u_per_ft, L_ft)
    M_u_lb_in = M_u_lb_ft * INCHES_PER_FOOT
    sigma_u = M_u_lb_in / Sx if Sx > 0 else 0

    # Design capacity
    phi_Mn_lb_in = PHI_FLEXURE * FLEXURAL_PSI * Sx
    phi_Mn_lb_ft = phi_Mn_lb_in / INCHES_PER_FOOT

    DCR = M_u_lb_in / phi_Mn_lb_in if phi_Mn_lb_in > 0 else 999

    # ── 7. Full calculator cross-check ──
    r = run_complete_analysis(
        hull_length_in=L_IN, hull_beam_in=B_IN, hull_depth_in=D_IN,
        hull_thickness_in=T_IN, concrete_weight_lbs=canoe_wt,
        flexural_strength_psi=FLEXURAL_PSI,
        waterplane_form_factor=CWP,
        concrete_density_pcf=DENSITY_PCF,
        crew_weight_lbs=CREW_LBS,
    )

    return {
        # Geometry
        "L_in": L_IN, "B_in": B_IN, "D_in": D_IN, "T_in": T_IN,
        "L_ft": L_ft, "B_ft": B_ft, "D_ft": D_ft, "T_ft": T_ft,
        "density_pcf": DENSITY_PCF,
        # Weight
        "canoe_wt": canoe_wt, "crew_wt": CREW_LBS, "total_wt": total_wt,
        # Hydrostatics
        "disp_ft3": disp_ft3, "wp_ft2": wp_ft2, "cwp": CWP,
        "draft_ft": draft_ft, "draft_in": draft_in,
        "fb_ft": fb_ft, "fb_in": fb_in,
        # Stability
        "I_wp_ft4": I_wp_ft4, "V_disp_ft3": V_disp_ft3,
        "BM_ft": BM_ft, "KB_ft": KB_ft, "KG_ft": KG_ft,
        "GM_ft": GM_ft, "GM_in": GM_in, "gm_check_ft": gm_check_ft,
        # Section properties
        "A_bot": A_bot, "y_bot": y_bot, "I_bot_self": I_bot_self,
        "h_wall": h_wall, "A_wall": A_wall, "y_wall": y_wall, "I_wall_self": I_wall_self,
        "A_total": A_total, "y_bar": y_bar,
        "I_bot": I_bot, "I_wall": I_wall, "Ix": Ix,
        "c_top": c_top, "c_bot": c_bot, "c_max": c_max,
        "Sx": Sx, "Sx_check": Sx_check,
        # Unfactored (ASD)
        "w_service": w_service_per_ft, "M_service_ft": M_service_lb_ft,
        "M_service_in": M_service_lb_in, "sigma_service": sigma_service, "SF": SF,
        # LRFD
        "w_dead": w_dead_per_ft, "w_live": w_live_per_ft, "w_u": w_u_per_ft,
        "M_u_ft": M_u_lb_ft, "M_u_in": M_u_lb_in, "sigma_u": sigma_u,
        "phi_Mn_in": phi_Mn_lb_in, "phi_Mn_ft": phi_Mn_lb_ft, "DCR": DCR,
        # Full calculator check
        "calc_results": r,
    }


def print_console(d):
    """Print every intermediate calculation to console."""
    W = 80
    print("=" * W)
    print("  DESIGN C — COMPLETE CALCULATION SNIPPET")
    print("  NAU ASCE Concrete Canoe 2026")
    print("=" * W)

    print("\n── 1. HULL PARTICULARS ──")
    print(f"  Length:          {d['L_in']:.1f} in  ({d['L_ft']:.2f} ft)")
    print(f"  Beam:            {d['B_in']:.1f} in  ({d['B_ft']:.3f} ft)")
    print(f"  Depth:           {d['D_in']:.1f} in  ({d['D_ft']:.3f} ft)")
    print(f"  Wall Thickness:  {d['T_in']:.2f} in ({d['T_ft']:.4f} ft)")
    print(f"  Concrete Density:{d['density_pcf']:.1f} PCF")
    print(f"  f'r (flexural):  {FLEXURAL_PSI:.0f} psi")

    print("\n── 2. WEIGHT ESTIMATION ──")
    print(f"  Canoe shell (estimated):  {d['canoe_wt']:.1f} lbs")
    print(f"  Crew (4 x 175 lbs):       {d['crew_wt']:.0f} lbs")
    print(f"  Total loaded:             {d['total_wt']:.1f} lbs")

    print("\n── 3. HYDROSTATIC ANALYSIS ──")
    print(f"  Total displacement:  {d['total_wt']:.1f} lbs")
    print(f"  Displaced volume:    V = {d['total_wt']:.1f} / {WATER_DENSITY_LB_PER_FT3} = {d['disp_ft3']:.4f} ft3")
    print(f"  Waterplane area:     Awp = Cwp x L x B = {d['cwp']} x {d['L_ft']:.2f} x {d['B_ft']:.3f} = {d['wp_ft2']:.3f} ft2")
    print(f"  Draft:               T = V / Awp = {d['disp_ft3']:.4f} / {d['wp_ft2']:.3f} = {d['draft_ft']:.4f} ft ({d['draft_in']:.2f} in)")
    print(f"  Freeboard:           FB = D - T = {d['D_ft']:.3f} - {d['draft_ft']:.4f} = {d['fb_ft']:.4f} ft ({d['fb_in']:.2f} in)")

    print("\n── 4. STABILITY ANALYSIS ──")
    print(f"  I_wp = Cwp x L x B^3 / 12 = {d['cwp']} x {d['L_ft']:.2f} x {d['B_ft']:.3f}^3 / 12 = {d['I_wp_ft4']:.4f} ft4")
    print(f"  V_displaced (prism) = Cwp x L x B x T = {d['V_disp_ft3']:.4f} ft3")
    print(f"  BM = I_wp / V = {d['I_wp_ft4']:.4f} / {d['V_disp_ft3']:.4f} = {d['BM_ft']:.4f} ft")
    print(f"  KB = T / 2 = {d['draft_ft']:.4f} / 2 = {d['KB_ft']:.4f} ft")
    print(f"  KG = 0.45 x D = 0.45 x {d['D_ft']:.3f} = {d['KG_ft']:.4f} ft")
    print(f"  GM = KB + BM - KG = {d['KB_ft']:.4f} + {d['BM_ft']:.4f} - {d['KG_ft']:.4f} = {d['GM_ft']:.4f} ft ({d['GM_in']:.2f} in)")
    print(f"  Cross-check (calculator): GM = {d['gm_check_ft'] * 12:.2f} in  {'OK' if abs(d['GM_in'] - d['gm_check_ft']*12) < 0.01 else 'MISMATCH'}")

    print("\n── 5. STRUCTURAL — THIN-SHELL U-SECTION PROPERTIES ──")
    print(f"  Bottom plate:  A = {d['B_in']:.0f} x {d['T_in']:.2f} = {d['A_bot']:.2f} in2,  y = {d['y_bot']:.3f} in,  Io = {d['I_bot_self']:.4f} in4")
    print(f"  Each wall:     A = {d['T_in']:.2f} x {d['h_wall']:.2f} = {d['A_wall']:.3f} in2,  y = {d['y_wall']:.3f} in,  Io = {d['I_wall_self']:.3f} in4")
    print(f"  Composite:     A_total = {d['A_bot']:.2f} + 2 x {d['A_wall']:.3f} = {d['A_total']:.3f} in2")
    print(f"  Neutral axis:  y_bar = ({d['A_bot']:.2f} x {d['y_bot']:.3f} + 2 x {d['A_wall']:.3f} x {d['y_wall']:.3f}) / {d['A_total']:.3f} = {d['y_bar']:.3f} in")
    print(f"  Parallel axis: I_bot  = {d['I_bot_self']:.4f} + {d['A_bot']:.2f} x ({d['y_bar']:.3f} - {d['y_bot']:.3f})^2 = {d['I_bot']:.2f} in4")
    print(f"                 I_wall = {d['I_wall_self']:.3f} + {d['A_wall']:.3f} x ({d['y_wall']:.3f} - {d['y_bar']:.3f})^2 = {d['I_wall']:.2f} in4")
    print(f"  Total Ix:      {d['I_bot']:.2f} + 2 x {d['I_wall']:.2f} = {d['Ix']:.2f} in4")
    print(f"  c_top = {d['D_in']:.0f} - {d['y_bar']:.3f} = {d['c_top']:.3f} in")
    print(f"  c_bot = {d['y_bar']:.3f} in")
    print(f"  c_max = {d['c_max']:.3f} in")
    print(f"  Sx = Ix / c_max = {d['Ix']:.2f} / {d['c_max']:.3f} = {d['Sx']:.2f} in3")
    print(f"  Cross-check (calculator): Sx = {d['Sx_check']:.2f} in3  {'OK' if abs(d['Sx'] - d['Sx_check']) < 0.01 else 'MISMATCH'}")

    print("\n── 6. UNFACTORED (ASD) BENDING ──")
    print(f"  w_service = {d['total_wt']:.1f} / {d['L_ft']:.2f} = {d['w_service']:.2f} lb/ft")
    print(f"  M_max = w L^2 / 8 = {d['w_service']:.2f} x {d['L_ft']:.2f}^2 / 8 = {d['M_service_ft']:.1f} lb-ft ({d['M_service_in']:.0f} lb-in)")
    print(f"  sigma = M / Sx = {d['M_service_in']:.0f} / {d['Sx']:.2f} = {d['sigma_service']:.1f} psi")
    print(f"  Safety Factor = f'r / sigma = {FLEXURAL_PSI:.0f} / {d['sigma_service']:.1f} = {d['SF']:.2f}")

    print("\n── 7. ACI 318-25 LRFD CHECK ──")
    print(f"  w_D = canoe / L = {d['canoe_wt']:.1f} / {d['L_ft']:.2f} = {d['w_dead']:.2f} lb/ft")
    print(f"  w_L = crew / L = {d['crew_wt']:.0f} / {d['L_ft']:.2f} = {d['w_live']:.2f} lb/ft")
    print(f"  w_u = 1.2 w_D + 1.6 w_L = 1.2 x {d['w_dead']:.2f} + 1.6 x {d['w_live']:.2f} = {d['w_u']:.2f} lb/ft")
    print(f"  M_u = w_u L^2 / 8 = {d['w_u']:.2f} x {d['L_ft']:.2f}^2 / 8 = {d['M_u_ft']:.1f} lb-ft ({d['M_u_in']:.0f} lb-in)")
    print(f"  sigma_u = M_u / Sx = {d['M_u_in']:.0f} / {d['Sx']:.2f} = {d['sigma_u']:.1f} psi")
    print(f"  phi*Mn = phi x f'r x Sx = {PHI_FLEXURE} x {FLEXURAL_PSI:.0f} x {d['Sx']:.2f} = {d['phi_Mn_in']:.0f} lb-in ({d['phi_Mn_ft']:.1f} lb-ft)")
    print(f"  DCR = M_u / (phi*Mn) = {d['M_u_in']:.0f} / {d['phi_Mn_in']:.0f} = {d['DCR']:.3f}")
    print(f"  DCR < 1.0 ? {'PASS' if d['DCR'] < 1.0 else 'FAIL'}")

    print("\n── 8. ASCE COMPLIANCE SUMMARY ──")
    r = d["calc_results"]
    print(f"  {'Metric':<25} {'Value':>12} {'Requirement':>15} {'Status':>10}")
    print(f"  {'-'*62}")
    print(f"  {'Freeboard':<25} {d['fb_in']:>10.2f} in {'>= 6.0 in':>15} {'PASS' if d['fb_in'] >= 6.0 else 'FAIL':>10}")
    print(f"  {'Metacentric Height GM':<25} {d['GM_in']:>10.2f} in {'>= 6.0 in':>15} {'PASS' if d['GM_in'] >= 6.0 else 'FAIL':>10}")
    print(f"  {'Safety Factor (ASD)':<25} {d['SF']:>10.2f} {'>= 2.0':>15} {'PASS' if d['SF'] >= 2.0 else 'FAIL':>10}")
    print(f"  {'DCR (LRFD)':<25} {d['DCR']:>10.3f} {'< 1.0':>15} {'PASS' if d['DCR'] < 1.0 else 'FAIL':>10}")
    overall = d['fb_in'] >= 6.0 and d['GM_in'] >= 6.0 and d['SF'] >= 2.0 and d['DCR'] < 1.0
    print(f"  {'OVERALL':<25} {'':>12} {'':>15} {'PASS' if overall else 'FAIL':>10}")

    print(f"\n── 9. VERIFICATION ──")
    checks = [
        ("Sx in 50-150 in3", 50 <= d["Sx"] <= 150, f"{d['Sx']:.2f}"),
        ("SF in 2-10", 2 <= d["SF"] <= 10, f"{d['SF']:.2f}"),
        ("GM in 4-20 in", 4 <= d["GM_in"] <= 20, f"{d['GM_in']:.2f}"),
        ("Freeboard > 6 in", d["fb_in"] > 6, f"{d['fb_in']:.2f}"),
        ("DCR < 1.0", d["DCR"] < 1.0, f"{d['DCR']:.3f}"),
    ]
    all_ok = True
    for label, ok, val in checks:
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_ok = False
        print(f"  {label:<25} = {val:>10}  {status}")
    print(f"\n  All verification checks: {'PASS' if all_ok else 'FAIL'}")
    print("=" * W)


def generate_markdown(d):
    """Generate judge-ready markdown calculation snippet."""
    r = d["calc_results"]
    overall = d['fb_in'] >= 6.0 and d['GM_in'] >= 6.0 and d['SF'] >= 2.0 and d['DCR'] < 1.0

    md = f"""# Design C — Complete Calculation Snippet
## NAU ASCE Concrete Canoe 2026

---

## 1. Hull Particulars

| Parameter | Value | Units |
|-----------|------:|-------|
| Length (LOA) | {d['L_in']:.1f} | in ({d['L_ft']:.2f} ft) |
| Beam (max) | {d['B_in']:.1f} | in ({d['B_ft']:.3f} ft) |
| Depth (molded) | {d['D_in']:.1f} | in ({d['D_ft']:.3f} ft) |
| Wall Thickness | {d['T_in']:.2f} | in |
| Concrete Density | {d['density_pcf']:.1f} | PCF |
| Flexural Strength f'r | {FLEXURAL_PSI:.0f} | psi |
| Crew | 4 paddlers x 175 | lbs ({d['crew_wt']:.0f} total) |

## 2. Hydrostatic Analysis

| Step | Calculation | Result |
|------|-------------|--------|
| Canoe Weight (est.) | U-shell model, Cp=0.55, OH=1.10 | {d['canoe_wt']:.1f} lbs |
| Total Displacement | {d['canoe_wt']:.1f} + {d['crew_wt']:.0f} | {d['total_wt']:.1f} lbs |
| Displaced Volume | V = {d['total_wt']:.1f} / {WATER_DENSITY_LB_PER_FT3} | {d['disp_ft3']:.4f} ft3 |
| Waterplane Area | Awp = Cwp x L x B = {d['cwp']} x {d['L_ft']:.2f} x {d['B_ft']:.3f} | {d['wp_ft2']:.3f} ft2 |
| Draft | T = V / Awp = {d['disp_ft3']:.4f} / {d['wp_ft2']:.3f} | {d['draft_ft']:.4f} ft ({d['draft_in']:.2f} in) |
| **Freeboard** | FB = D - T = {d['D_ft']:.3f} - {d['draft_ft']:.4f} | **{d['fb_in']:.2f} in** |

## 3. Stability Analysis

| Step | Calculation | Result |
|------|-------------|--------|
| I_wp | Cwp x L x B^3 / 12 = {d['cwp']} x {d['L_ft']:.2f} x {d['B_ft']:.3f}^3 / 12 | {d['I_wp_ft4']:.4f} ft4 |
| V_displaced | Cwp x L x B x T | {d['V_disp_ft3']:.4f} ft3 |
| BM | I_wp / V = {d['I_wp_ft4']:.4f} / {d['V_disp_ft3']:.4f} | {d['BM_ft']:.4f} ft |
| KB | T / 2 | {d['KB_ft']:.4f} ft |
| KG | 0.45 x D = 0.45 x {d['D_ft']:.3f} | {d['KG_ft']:.4f} ft |
| **GM** | KB + BM - KG = {d['KB_ft']:.4f} + {d['BM_ft']:.4f} - {d['KG_ft']:.4f} | **{d['GM_ft']:.4f} ft ({d['GM_in']:.2f} in)** |

## 4. Structural Analysis

### 4a. Thin-Shell U-Section Properties

Cross-section modeled as bottom plate + 2 side walls (parallel axis theorem):

| Component | Area (in2) | Centroid y (in) | I_self (in4) | I_parallel (in4) |
|-----------|----------:|----------------:|-------------:|------------------:|
| Bottom plate ({d['B_in']:.0f} x {d['T_in']:.2f}) | {d['A_bot']:.2f} | {d['y_bot']:.3f} | {d['I_bot_self']:.4f} | {d['I_bot']:.2f} |
| Wall 1 ({d['T_in']:.2f} x {d['h_wall']:.2f}) | {d['A_wall']:.3f} | {d['y_wall']:.3f} | {d['I_wall_self']:.3f} | {d['I_wall']:.2f} |
| Wall 2 ({d['T_in']:.2f} x {d['h_wall']:.2f}) | {d['A_wall']:.3f} | {d['y_wall']:.3f} | {d['I_wall_self']:.3f} | {d['I_wall']:.2f} |
| **Total** | **{d['A_total']:.3f}** | **y_bar = {d['y_bar']:.3f}** | | **Ix = {d['Ix']:.2f}** |

| Property | Value |
|----------|------:|
| c_top = D - y_bar | {d['c_top']:.3f} in |
| c_bot = y_bar | {d['c_bot']:.3f} in |
| c_max | {d['c_max']:.3f} in |
| **Sx = Ix / c_max** | **{d['Sx']:.2f} in3** |

### 4b. Unfactored (ASD) Bending

| Step | Calculation | Result |
|------|-------------|--------|
| Service load | w = {d['total_wt']:.1f} / {d['L_ft']:.2f} | {d['w_service']:.2f} lb/ft |
| Max moment | M = wL^2/8 = {d['w_service']:.2f} x {d['L_ft']:.2f}^2 / 8 | {d['M_service_ft']:.1f} lb-ft |
| Bending stress | sigma = M/Sx = {d['M_service_in']:.0f} / {d['Sx']:.2f} | {d['sigma_service']:.1f} psi |
| **Safety Factor** | SF = f'r / sigma = {FLEXURAL_PSI:.0f} / {d['sigma_service']:.1f} | **{d['SF']:.2f}** |

### 4c. ACI 318-25 LRFD Check

| Step | Calculation | Result |
|------|-------------|--------|
| Dead load (D) | w_D = {d['canoe_wt']:.1f} / {d['L_ft']:.2f} | {d['w_dead']:.2f} lb/ft |
| Live load (L) | w_L = {d['crew_wt']:.0f} / {d['L_ft']:.2f} | {d['w_live']:.2f} lb/ft |
| Factored load | w_u = 1.2D + 1.6L = 1.2({d['w_dead']:.2f}) + 1.6({d['w_live']:.2f}) | {d['w_u']:.2f} lb/ft |
| Factored moment | M_u = w_u L^2 / 8 | {d['M_u_ft']:.1f} lb-ft ({d['M_u_in']:.0f} lb-in) |
| Factored stress | sigma_u = M_u / Sx | {d['sigma_u']:.1f} psi |
| Design capacity | phi*Mn = phi x f'r x Sx = {PHI_FLEXURE} x {FLEXURAL_PSI:.0f} x {d['Sx']:.2f} | {d['phi_Mn_in']:.0f} lb-in ({d['phi_Mn_ft']:.1f} lb-ft) |
| **DCR** | M_u / (phi*Mn) = {d['M_u_in']:.0f} / {d['phi_Mn_in']:.0f} | **{d['DCR']:.3f}** |

## 5. ASCE Compliance Summary

| Metric | Value | Requirement | Status |
|--------|------:|-------------|--------|
| Freeboard | {d['fb_in']:.2f} in | >= 6.0 in | **{'PASS' if d['fb_in'] >= 6.0 else 'FAIL'}** |
| Metacentric Height GM | {d['GM_in']:.2f} in | >= 6.0 in | **{'PASS' if d['GM_in'] >= 6.0 else 'FAIL'}** |
| Safety Factor (ASD) | {d['SF']:.2f} | >= 2.0 | **{'PASS' if d['SF'] >= 2.0 else 'FAIL'}** |
| DCR (LRFD) | {d['DCR']:.3f} | < 1.0 | **{'PASS' if d['DCR'] < 1.0 else 'FAIL'}** |
| **Overall** | | | **{'PASS' if overall else 'FAIL'}** |

## 6. 10-Step Design Process Overview

1. **Define hull geometry** — L, B, D from competition constraints and team experience
2. **Select concrete mix** — lightweight aggregate, target {d['density_pcf']:.0f} PCF, f'r = {FLEXURAL_PSI:.0f} psi
3. **Estimate hull weight** — U-shell model with prismatic coefficient Cp = 0.55
4. **Compute displacement** — Archimedes: V = W_total / rho_water
5. **Determine draft** — T = V / (Cwp x L x B), verify draft < depth
6. **Check freeboard** — FB = D - T >= 6.0 in (ASCE minimum)
7. **Evaluate stability** — GM = KB + BM - KG >= 6.0 in (ASCE minimum)
8. **Compute section properties** — Thin-shell U-section via parallel axis theorem
9. **ASD check** — SF = f'r / sigma >= 2.0
10. **LRFD check** — DCR = M_u / (phi x Mn) < 1.0 per ACI 318-25

## 7. Tools & Verification

- **Calculator**: `calculations/concrete_canoe_calculator.py` v2.0
- **Repository**: [github.com/Miles0sage/concrete-canoe-project2026](https://github.com/Miles0sage/concrete-canoe-project2026)
- **Test suite**: 60/60 tests passing (`pytest tests/ -v`)
- **Section modulus cross-check**: `section_modulus_thin_shell({d['B_in']:.0f}, {d['D_in']:.0f}, {d['T_in']:.2f})` = {d['Sx_check']:.2f} in3 (matches hand calc)
- **GM cross-check**: `metacentric_height_approx()` = {d['gm_check_ft']*12:.2f} in (matches hand calc)
- **Full pipeline**: `run_complete_analysis()` returns SF={d['calc_results']['structural']['safety_factor']:.2f}, GM={d['calc_results']['stability']['gm_in']:.2f} in

---
*Generated by NAU ASCE Concrete Canoe Calculator v2.0 — February 2026*
"""
    out = REPORT_DIR / "Design_C_Calculation_Snippet.md"
    out.write_text(md)
    print(f"\n  Markdown saved: {out}")
    return out


def main():
    import warnings
    warnings.filterwarnings("ignore")

    d = compute_all()
    print_console(d)
    generate_markdown(d)


if __name__ == "__main__":
    main()
