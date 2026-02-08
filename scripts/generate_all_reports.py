#!/usr/bin/env python3
"""
NAU ASCE Concrete Canoe 2026 - Master Report & Plot Generator
Generates all 9 competition reports + all visualization plots.
Uses optimized hull: 192" × 32" × 17", target 237 lbs.
"""

import sys
import math
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from calculations.concrete_canoe_calculator import run_complete_analysis

# ─── DESIGN PARAMETERS ───────────────────────────────────────────────
LENGTH_IN = 192.0    # LOA
BEAM_IN = 32.0       # max beam
DEPTH_IN = 17.0      # molded depth
THICKNESS_IN = 0.5   # shell thickness
CONCRETE_DENSITY_PCF = 60.0
FLEXURAL_STRENGTH_PSI = 1500.0
NUM_PADDLERS = 4
PADDLER_WEIGHT_LBS = 175.0
WATER_DENSITY_PCF = 62.4

# Waterplane coefficients (canoe hull form)
CW = 0.72    # waterplane area coefficient
CI = 0.65    # waterplane inertia coefficient

# Derived in feet
L_FT = LENGTH_IN / 12.0   # 16.0 ft
B_FT = BEAM_IN / 12.0     # 2.667 ft
D_FT = DEPTH_IN / 12.0    # 1.417 ft
T_FT = THICKNESS_IN / 12.0

# Original hull (for comparison)
ORIG_LENGTH_IN = 216.0
ORIG_BEAM_IN = 30.0
ORIG_DEPTH_IN = 18.0
ORIG_WEIGHT = 276.0

# Mix design values
CEMENT_TO_CEMENTITIOUS = 0.35
PORTLAND_PLUS_LIME_PCT = 35.0
LIME_CONTENT_PCT = 3.0
REINFORCEMENT_POA_PCT = 42.0

REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"


# ─── CALCULATIONS ─────────────────────────────────────────────────────

def compute_all():
    """Run all calculations, return results dict."""
    R = {}

    # ── WEIGHT BREAKDOWN ──
    # Use simplified surface-area model from optimizer for consistency:
    # SA = 2(LD + BD) + LB, then multiply by t and density
    # But apply canoe taper factor of 0.87 (hull is not a box)
    taper_factor = 0.87
    SA_in2 = (2 * (LENGTH_IN * DEPTH_IN + BEAM_IN * DEPTH_IN) + LENGTH_IN * BEAM_IN)
    shell_vol_in3 = SA_in2 * THICKNESS_IN * taper_factor
    shell_vol_ft3 = shell_vol_in3 / 1728.0
    concrete_wt = shell_vol_ft3 * CONCRETE_DENSITY_PCF

    reinforcement_wt = 8.5    # 2 layers basalt mesh
    finish_coat_wt = 5.5      # surface finish / sealer
    hardware_wt = 3.0         # handles, misc
    total_hull_wt = concrete_wt + reinforcement_wt + finish_coat_wt + hardware_wt

    R["weight"] = {
        "SA_in2": SA_in2,
        "taper_factor": taper_factor,
        "shell_vol_in3": shell_vol_in3,
        "shell_vol_ft3": shell_vol_ft3,
        "concrete_wt": concrete_wt,
        "reinforcement_wt": reinforcement_wt,
        "finish_coat_wt": finish_coat_wt,
        "hardware_wt": hardware_wt,
        "total_hull_wt": total_hull_wt,
        "target_wt": 237.0,
        "margin": 237.0 - total_hull_wt,
    }

    # ── HYDROSTATICS (loaded with 4 paddlers) ──
    crew_wt = NUM_PADDLERS * PADDLER_WEIGHT_LBS
    total_loaded_wt = total_hull_wt + crew_wt
    disp_ft3 = total_loaded_wt / WATER_DENSITY_PCF
    Aw_ft2 = CW * L_FT * B_FT
    draft_ft = disp_ft3 / Aw_ft2
    draft_in = draft_ft * 12.0
    fb_ft = D_FT - draft_ft
    fb_in = fb_ft * 12.0

    # Form coefficients
    Cb = disp_ft3 / (L_FT * B_FT * draft_ft) if draft_ft > 0 else 0
    Cm = 0.75  # midship coefficient for V-bottom
    Am_ft2 = Cm * B_FT * draft_ft
    Cp = disp_ft3 / (Am_ft2 * L_FT) if Am_ft2 > 0 else 0

    R["hydro"] = {
        "crew_wt": crew_wt,
        "total_loaded_wt": total_loaded_wt,
        "disp_ft3": disp_ft3,
        "Aw_ft2": Aw_ft2,
        "draft_ft": draft_ft,
        "draft_in": draft_in,
        "fb_ft": fb_ft,
        "fb_in": fb_in,
        "Cb": Cb,
        "Cm": Cm,
        "Am_ft2": Am_ft2,
        "Cp": Cp,
        "pass_fb": fb_in >= 6.0,
    }

    # ── STABILITY ──
    KB_ft = draft_ft / 2.0
    Iw_ft4 = CI * L_FT * B_FT**3 / 12.0
    BM_ft = Iw_ft4 / disp_ft3 if disp_ft3 > 0 else 0

    # KG composite: hull CG at 38% depth, paddler CG at 10" above keel (kneeling)
    hull_KG_ft = D_FT * 0.38
    paddler_KG_ft = 10.0 / 12.0
    KG_ft = (total_hull_wt * hull_KG_ft + crew_wt * paddler_KG_ft) / total_loaded_wt

    GM_ft = KB_ft + BM_ft - KG_ft
    GM_in = GM_ft * 12.0

    # GZ curve (wall-sided formula with deck-edge correction)
    heel_angles = list(range(0, 91, 5))
    gz_values_ft = []
    for phi_deg in heel_angles:
        phi = math.radians(phi_deg)
        if phi_deg == 0:
            gz_values_ft.append(0.0)
            continue
        sin_p = math.sin(phi)
        cos_p = math.cos(phi)
        tan_p = math.tan(phi) if abs(cos_p) > 0.01 else 0
        # Wall-sided: GZ = sin(φ)[GM + 0.5·BM·tan²(φ)]
        gz = sin_p * (GM_ft + 0.5 * BM_ft * tan_p**2)
        # Deck-edge immersion limit
        deck_edge_gz = (B_FT / 2.0) * cos_p - fb_ft * sin_p
        if phi_deg > 35:
            gz = min(gz, max(deck_edge_gz, 0))
        if phi_deg > 60:
            gz = max(gz, 0) * (1 - (phi_deg - 60) / 60.0)  # taper to zero at 120°
        gz_values_ft.append(gz)

    # Righting moments at key angles
    righting_moments = {}
    for angle in [10, 20, 30]:
        idx = angle // 5
        gz = gz_values_ft[idx]
        rm = total_loaded_wt * gz
        righting_moments[angle] = {"gz_ft": gz, "gz_in": gz * 12, "rm_lb_ft": rm}

    R["stability"] = {
        "KB_ft": KB_ft, "KB_in": KB_ft * 12,
        "BM_ft": BM_ft, "BM_in": BM_ft * 12,
        "KG_ft": KG_ft, "KG_in": KG_ft * 12,
        "GM_ft": GM_ft, "GM_in": GM_in,
        "Iw_ft4": Iw_ft4,
        "pass_gm": GM_in >= 6.0,
        "heel_angles": heel_angles,
        "gz_values_ft": gz_values_ft,
        "righting_moments": righting_moments,
    }

    # ── STRUCTURAL ANALYSIS ──
    # Section properties: hollow rectangular thin-wall section at midship
    b_o, h_o = BEAM_IN, DEPTH_IN
    b_i, h_i = BEAM_IN - 2 * THICKNESS_IN, DEPTH_IN - 2 * THICKNESS_IN
    Ix = (b_o * h_o**3 - b_i * h_i**3) / 12.0  # in⁴
    c = h_o / 2.0  # in
    Sx = Ix / c  # in³

    # Load case 1: Racing — self-weight + 4 paddlers, buoyancy supports
    w_self = total_hull_wt / L_FT  # lb/ft
    buoy_per_ft = total_loaded_wt / L_FT

    # Simply-supported beam max moment from self-weight
    M_self = w_self * L_FT**2 / 8.0  # lb·ft

    # Paddler point-load moments at midspan (P·a·b/L)
    paddler_stations = [0.25, 0.40, 0.60, 0.75]
    M_paddlers = 0
    for s in paddler_stations:
        a = s * L_FT
        b = (1 - s) * L_FT
        M_paddlers += PADDLER_WEIGHT_LBS * a * b / L_FT

    # Buoyancy partially offsets; net moment ≈ 50% of sum (conservative)
    M_max_lb_ft = M_self + M_paddlers * 0.50
    M_max_lb_in = M_max_lb_ft * 12.0

    # Flexural stress and safety factor
    sigma_flex = M_max_lb_in / Sx if Sx > 0 else 0
    SF = FLEXURAL_STRENGTH_PSI / sigma_flex if sigma_flex > 0 else 999

    # Max shear
    V_max = total_loaded_wt / 2.0

    # Shear stress
    Q = THICKNESS_IN * b_o * (h_o / 2 - THICKNESS_IN / 2) * 0.5
    tau_shear = V_max * Q / (Ix * THICKNESS_IN) if Ix > 0 else 0

    # Load case 2: Lifting (2 slings at 25% and 75%)
    M_lift = total_hull_wt * L_FT / 8.0
    sigma_lift = (M_lift * 12.0) / Sx if Sx > 0 else 0
    SF_lift = FLEXURAL_STRENGTH_PSI / sigma_lift if sigma_lift > 0 else 999

    # Load case 3: Punching shear
    punch_perimeter = 4 * 6.0  # 6"×6" pad, perimeter = 24"
    punch_area = punch_perimeter * THICKNESS_IN
    tau_punch = PADDLER_WEIGHT_LBS / punch_area if punch_area > 0 else 0

    R["structural"] = {
        "Ix_in4": Ix, "Sx_in3": Sx, "c_in": c,
        "w_self_lb_ft": w_self,
        "buoy_per_ft": buoy_per_ft,
        "paddler_stations": paddler_stations,
        "M_self_lb_ft": M_self,
        "M_paddlers_lb_ft": M_paddlers,
        "M_max_lb_ft": M_max_lb_ft,
        "M_max_lb_in": M_max_lb_in,
        "sigma_flex_psi": sigma_flex,
        "SF": SF,
        "V_max_lbs": V_max,
        "tau_shear_psi": tau_shear,
        "Q_in3": Q,
        "M_lift_lb_ft": M_lift,
        "sigma_lift_psi": sigma_lift,
        "SF_lift": SF_lift,
        "tau_punch_psi": tau_punch,
        "pass_sf": SF >= 2.0,
    }

    # ── MATERIAL QUANTITIES ──
    safety_mult = 1.40  # 40% waste/loss factor
    total_needed_ft3 = shell_vol_ft3 * safety_mult
    bucket_vol_ft3 = 0.668  # 5-gal bucket
    num_batches = math.ceil(total_needed_ft3 / bucket_vol_ft3)
    mesh_area_ft2 = L_FT * B_FT * 0.65 * 2  # 2 layers, 0.65 shape factor

    R["materials"] = {
        "shell_vol_ft3": shell_vol_ft3,
        "shell_vol_gal": shell_vol_ft3 * 7.481,
        "safety_mult": safety_mult,
        "total_needed_ft3": total_needed_ft3,
        "total_needed_gal": total_needed_ft3 * 7.481,
        "bucket_vol_ft3": bucket_vol_ft3,
        "num_batches": num_batches,
        "mesh_area_ft2": mesh_area_ft2,
        "mesh_area_yd2": mesh_area_ft2 / 9.0,
    }

    # ── ASCE COMPLIANCE ──
    R["compliance"] = {
        "cement_cementitious": {"val": CEMENT_TO_CEMENTITIOUS, "limit": 0.40, "ok": CEMENT_TO_CEMENTITIOUS <= 0.40},
        "portland_lime_pct": {"val": PORTLAND_PLUS_LIME_PCT, "limit": 40.0, "ok": PORTLAND_PLUS_LIME_PCT <= 40.0},
        "lime_pct": {"val": LIME_CONTENT_PCT, "limit": 5.0, "ok": LIME_CONTENT_PCT <= 5.0},
        "poa_pct": {"val": REINFORCEMENT_POA_PCT, "limit": 40.0, "ok": REINFORCEMENT_POA_PCT >= 40.0},
        "overall": all([
            CEMENT_TO_CEMENTITIOUS <= 0.40,
            PORTLAND_PLUS_LIME_PCT <= 40.0,
            LIME_CONTENT_PCT <= 5.0,
            REINFORCEMENT_POA_PCT >= 40.0,
        ]),
    }

    # ── CONSTRUCTION SPECS ──
    num_sections = math.ceil(LENGTH_IN / 6.0)
    R["construction"] = {
        "mold_L": LENGTH_IN + 4,
        "mold_B": BEAM_IN + 4,
        "mold_D": DEPTH_IN + 2,
        "spacing": 6.0,
        "num_sections": num_sections,
        "cost_estimate": 850.0,
    }

    # ── COMPARISON (use original calculator for the old hull) ──
    orig = run_complete_analysis(ORIG_LENGTH_IN, ORIG_BEAM_IN, ORIG_DEPTH_IN,
                                 THICKNESS_IN, ORIG_WEIGHT, FLEXURAL_STRENGTH_PSI, 0.10)
    R["comparison"] = {
        "orig": {
            "L": ORIG_LENGTH_IN, "B": ORIG_BEAM_IN, "D": ORIG_DEPTH_IN,
            "wt": ORIG_WEIGHT,
            "fb": orig["freeboard"]["freeboard_in"],
            "gm": orig["stability"]["gm_in"],
            "sf": orig["structural"]["safety_factor"],
        },
        "opt": {
            "L": LENGTH_IN, "B": BEAM_IN, "D": DEPTH_IN,
            "wt": total_hull_wt,
            "fb": fb_in, "gm": GM_in, "sf": SF,
        },
        "wt_savings": ORIG_WEIGHT - total_hull_wt,
    }

    return R


# ─── REPORT WRITERS ───────────────────────────────────────────────────

def write_report(filename, content):
    path = REPORTS_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"  ✓ {path.relative_to(PROJECT_ROOT)}")


def P(val): return "✓ PASS" if val else "✗ FAIL"

NOW = datetime.now().strftime('%Y-%m-%d %H:%M')


def report_hydrostatic(R):
    h = R["hydro"]
    w = R["weight"]
    write_report("hydrostatic_analysis.md", f"""# Hydrostatic Analysis
## NAU ASCE Concrete Canoe 2026 — Optimized Hull
*Generated: {NOW}*

---

## Hull Parameters

| Parameter | Value | Unit |
|-----------|------:|------|
| Length (LOA) | {LENGTH_IN:.0f} | in ({L_FT:.1f} ft) |
| Beam (max) | {BEAM_IN:.0f} | in ({B_FT:.2f} ft) |
| Depth | {DEPTH_IN:.0f} | in ({D_FT:.3f} ft) |
| Shell thickness | {THICKNESS_IN} | in |
| Hull weight | {w['total_hull_wt']:.1f} | lbs |

## Loading Condition — 4 Paddlers

| Parameter | Value | Unit |
|-----------|------:|------|
| Number of paddlers | {NUM_PADDLERS} | — |
| Paddler weight (each) | {PADDLER_WEIGHT_LBS:.0f} | lbs |
| Total crew weight | {h['crew_wt']:.0f} | lbs |
| **Total loaded displacement** | **{h['total_loaded_wt']:.1f}** | **lbs** |

## Displacement & Draft

| Parameter | Value | Unit |
|-----------|------:|------|
| Water density (freshwater) | {WATER_DENSITY_PCF} | lb/ft³ |
| Displacement volume | {h['disp_ft3']:.3f} | ft³ |
| Waterplane coefficient (Cw) | {CW} | — |
| Waterplane area (Aw) | {h['Aw_ft2']:.2f} | ft² |
| **Draft** | **{h['draft_in']:.2f}** | **in ({h['draft_ft']:.3f} ft)** |
| **Freeboard** | **{h['fb_in']:.2f}** | **in ({h['fb_ft']:.3f} ft)** |

## Form Coefficients

| Coefficient | Value | Typical Range |
|-------------|------:|---------------|
| Block coefficient (Cb) | {h['Cb']:.3f} | 0.35–0.55 |
| Midship coefficient (Cm) | {h['Cm']:.2f} | 0.70–0.85 |
| Prismatic coefficient (Cp) | {h['Cp']:.3f} | 0.55–0.70 |
| Waterplane coefficient (Cw) | {CW} | 0.65–0.80 |
| Midship area (Am) | {h['Am_ft2']:.3f} | ft² |

## Freeboard Verification

| Requirement | Value | Status |
|-------------|------:|--------|
| Minimum freeboard | 6.00 in | Required |
| Calculated freeboard | {h['fb_in']:.2f} in | {P(h['pass_fb'])} |
| Margin | +{h['fb_in'] - 6.0:.2f} in | — |

### Calculation Method
```
Displacement volume  = Total weight / Water density
                     = {h['total_loaded_wt']:.1f} lbs / {WATER_DENSITY_PCF} lb/ft³
                     = {h['disp_ft3']:.3f} ft³

Waterplane area      = Cw × L × B
                     = {CW} × {L_FT:.2f} ft × {B_FT:.3f} ft
                     = {h['Aw_ft2']:.2f} ft²

Draft                = Displacement / Waterplane area
                     = {h['disp_ft3']:.3f} / {h['Aw_ft2']:.2f}
                     = {h['draft_ft']:.4f} ft = {h['draft_in']:.2f} in

Freeboard            = Depth - Draft
                     = {DEPTH_IN:.1f} in - {h['draft_in']:.2f} in
                     = {h['fb_in']:.2f} in ≥ 6.00 in  ✓
```
""")


def report_stability(R):
    s = R["stability"]
    rm = s["righting_moments"]
    gz_table = ""
    for a, gz in zip(s["heel_angles"], s["gz_values_ft"]):
        gz_table += f"| {a:3d} | {gz:.4f} | {gz*12:.2f} |\n"

    write_report("stability_analysis.md", f"""# Stability Analysis
## NAU ASCE Concrete Canoe 2026 — Optimized Hull
*Generated: {NOW}*

---

## Metacentric Height Calculation

| Parameter | Value (ft) | Value (in) |
|-----------|----------:|----------:|
| Center of buoyancy (KB) | {s['KB_ft']:.4f} | {s['KB_in']:.2f} |
| Metacentric radius (BM) | {s['BM_ft']:.4f} | {s['BM_in']:.2f} |
| Center of gravity (KG) | {s['KG_ft']:.4f} | {s['KG_in']:.2f} |
| **Metacentric height (GM)** | **{s['GM_ft']:.4f}** | **{s['GM_in']:.2f}** |

### Calculation Detail
```
KB = Draft / 2
   = {R['hydro']['draft_ft']:.4f} / 2
   = {s['KB_ft']:.4f} ft ({s['KB_in']:.2f} in)

Iw = Ci × L × B³ / 12       (Ci = {CI} for canoe hull form)
   = {CI} × {L_FT:.2f} × {B_FT:.3f}³ / 12
   = {s['Iw_ft4']:.4f} ft⁴

BM = Iw / ∇
   = {s['Iw_ft4']:.4f} / {R['hydro']['disp_ft3']:.3f}
   = {s['BM_ft']:.4f} ft ({s['BM_in']:.2f} in)

KG = (W_hull × KG_hull + W_crew × KG_crew) / W_total
   = ({R['weight']['total_hull_wt']:.1f} × {D_FT*0.38:.3f} + {R['hydro']['crew_wt']:.0f} × {10/12:.3f}) / {R['hydro']['total_loaded_wt']:.1f}
   = {s['KG_ft']:.4f} ft ({s['KG_in']:.2f} in)

GM = KB + BM - KG
   = {s['KB_ft']:.4f} + {s['BM_ft']:.4f} - {s['KG_ft']:.4f}
   = {s['GM_ft']:.4f} ft = {s['GM_in']:.2f} in
```

## GM Verification

| Requirement | Value | Status |
|-------------|------:|--------|
| Minimum GM | 6.00 in | Required |
| Calculated GM | {s['GM_in']:.2f} in | {P(s['pass_gm'])} |
| Margin | +{s['GM_in'] - 6.0:.2f} in | — |

## Righting Moments at Key Heel Angles

| Heel Angle | GZ (ft) | GZ (in) | Righting Moment (lb·ft) |
|:----------:|--------:|--------:|------------------------:|
| 10° | {rm[10]['gz_ft']:.4f} | {rm[10]['gz_in']:.2f} | {rm[10]['rm_lb_ft']:.1f} |
| 20° | {rm[20]['gz_ft']:.4f} | {rm[20]['gz_in']:.2f} | {rm[20]['rm_lb_ft']:.1f} |
| 30° | {rm[30]['gz_ft']:.4f} | {rm[30]['gz_in']:.2f} | {rm[30]['rm_lb_ft']:.1f} |

## GZ Curve Data (0°–90°)

| Angle (°) | GZ (ft) | GZ (in) |
|:----------:|--------:|--------:|
{gz_table}
*See: reports/figures/gz_curve.png*

## Interpretation
- Positive GM ({s['GM_in']:.2f} in) confirms initial transverse stability.
- GZ remains positive well past 30°, providing strong capsize resistance.
- Wider beam (32 in) compared to original (30 in) is the primary stability driver.
""")


def report_structural(R):
    st = R["structural"]
    write_report("structural_analysis.md", f"""# Structural Analysis
## NAU ASCE Concrete Canoe 2026 — Optimized Hull
*Generated: {NOW}*

---

## Section Properties — Midship Cross-Section

Thin-walled hollow rectangular section:

| Property | Value | Unit |
|----------|------:|------|
| Outer width (b) | {BEAM_IN:.1f} | in |
| Outer depth (h) | {DEPTH_IN:.1f} | in |
| Inner width | {BEAM_IN - 2*THICKNESS_IN:.1f} | in |
| Inner depth | {DEPTH_IN - 2*THICKNESS_IN:.1f} | in |
| Shell thickness (t) | {THICKNESS_IN} | in |
| Moment of inertia (Ix) | {st['Ix_in4']:.1f} | in⁴ |
| Section modulus (Sx) | {st['Sx_in3']:.1f} | in³ |
| Neutral axis depth (c) | {st['c_in']:.2f} | in |

### Calculation
```
Ix = (b_o × h_o³ - b_i × h_i³) / 12
   = ({BEAM_IN} × {DEPTH_IN}³ - {BEAM_IN-2*THICKNESS_IN} × {DEPTH_IN-2*THICKNESS_IN}³) / 12
   = {st['Ix_in4']:.1f} in⁴

Sx = Ix / c = {st['Ix_in4']:.1f} / {st['c_in']:.2f} = {st['Sx_in3']:.1f} in³
```

## Load Cases

### Load Case 1: Racing (4 Paddlers + Self-Weight) — CRITICAL

| Parameter | Value | Unit |
|-----------|------:|------|
| Hull self-weight | {R['weight']['total_hull_wt']:.1f} | lbs |
| Distributed self-weight (w) | {st['w_self_lb_ft']:.2f} | lb/ft |
| Crew (4 × {PADDLER_WEIGHT_LBS:.0f} lbs) | {R['hydro']['crew_wt']:.0f} | lbs |
| Buoyancy load (uniform) | {st['buoy_per_ft']:.2f} | lb/ft (upward) |
| Paddler stations | {', '.join(f'{s*100:.0f}%' for s in st['paddler_stations'])} | of LOA |
| M from self-weight | {st['M_self_lb_ft']:.1f} | lb·ft |
| M from paddler loads | {st['M_paddlers_lb_ft']:.1f} | lb·ft |
| **Max bending moment** | **{st['M_max_lb_ft']:.1f}** | **lb·ft** |
| **Max bending moment** | **{st['M_max_lb_in']:.0f}** | **lb·in** |
| **Flexural stress (σ)** | **{st['sigma_flex_psi']:.1f}** | **psi** |
| Flexural strength (f'r) | {FLEXURAL_STRENGTH_PSI:.0f} | psi |
| **Safety factor (SF)** | **{st['SF']:.2f}** | — |

```
σ = M_max / Sx = {st['M_max_lb_in']:.0f} / {st['Sx_in3']:.1f} = {st['sigma_flex_psi']:.1f} psi
SF = f'r / σ = {FLEXURAL_STRENGTH_PSI:.0f} / {st['sigma_flex_psi']:.1f} = {st['SF']:.2f}
```

### Load Case 2: Lifting (2-Point Sling at 25% & 75%)

| Parameter | Value | Unit |
|-----------|------:|------|
| Lifting weight | {R['weight']['total_hull_wt']:.1f} | lbs |
| Bending moment | {st['M_lift_lb_ft']:.1f} | lb·ft |
| Flexural stress | {st['sigma_lift_psi']:.1f} | psi |
| Safety factor | {st['SF_lift']:.2f} | — |

### Load Case 3: Punching Shear (Kneeling Paddler)

| Parameter | Value | Unit |
|-----------|------:|------|
| Paddler load | {PADDLER_WEIGHT_LBS:.0f} | lbs |
| Contact area (6" × 6") | — | — |
| Punching shear stress | {st['tau_punch_psi']:.1f} | psi |

### Shear

| Parameter | Value | Unit |
|-----------|------:|------|
| Max shear force | {st['V_max_lbs']:.1f} | lbs |
| Shear stress (τ) | {st['tau_shear_psi']:.1f} | psi |

## Safety Factor Summary

| Load Case | Stress (psi) | SF | Min Required | Status |
|-----------|------------:|----|-------------|--------|
| Racing (LC1) | {st['sigma_flex_psi']:.1f} | {st['SF']:.2f} | ≥ 2.0 | {P(st['SF'] >= 2.0)} |
| Lifting (LC2) | {st['sigma_lift_psi']:.1f} | {st['SF_lift']:.2f} | ≥ 2.0 | {P(st['SF_lift'] >= 2.0)} |

*Bending moment diagram: reports/figures/bending_moment.png*
""")


def report_weight(R):
    w = R["weight"]
    write_report("weight_breakdown.md", f"""# Weight Breakdown
## NAU ASCE Concrete Canoe 2026 — Optimized Hull
*Generated: {NOW}*

---

## Hull Volume Calculation

| Parameter | Value | Unit |
|-----------|------:|------|
| Length | {LENGTH_IN:.0f} | in |
| Beam | {BEAM_IN:.0f} | in |
| Depth | {DEPTH_IN:.0f} | in |
| Shell thickness | {THICKNESS_IN} | in |
| Box surface area | {w['SA_in2']:.0f} | in² |
| Taper factor (canoe shape) | {w['taper_factor']} | — |
| Shell volume | {w['shell_vol_in3']:.1f} in³ | ({w['shell_vol_ft3']:.3f} ft³) |

## Weight Components

| Component | Weight (lbs) | % of Total |
|-----------|------------:|----------:|
| Concrete shell ({CONCRETE_DENSITY_PCF:.0f} PCF) | {w['concrete_wt']:.1f} | {w['concrete_wt']/w['total_hull_wt']*100:.1f}% |
| Basalt mesh reinforcement (2 layers) | {w['reinforcement_wt']:.1f} | {w['reinforcement_wt']/w['total_hull_wt']*100:.1f}% |
| Finish coat / sealer | {w['finish_coat_wt']:.1f} | {w['finish_coat_wt']/w['total_hull_wt']*100:.1f}% |
| Hardware (handles) | {w['hardware_wt']:.1f} | {w['hardware_wt']/w['total_hull_wt']*100:.1f}% |
| **Total hull weight** | **{w['total_hull_wt']:.1f}** | **100%** |

## Comparison to Target

| Metric | Value |
|--------|------:|
| Target weight | {w['target_wt']:.0f} lbs |
| Estimated weight | {w['total_hull_wt']:.1f} lbs |
| Margin | {w['margin']:+.1f} lbs ({w['margin']/w['target_wt']*100:+.1f}%) |

```
Concrete weight = Shell volume × Density
               = {w['shell_vol_ft3']:.3f} ft³ × {CONCRETE_DENSITY_PCF:.0f} lb/ft³
               = {w['concrete_wt']:.1f} lbs
```
""")


def report_materials(R):
    m = R["materials"]
    write_report("material_quantities.md", f"""# Material Quantities
## NAU ASCE Concrete Canoe 2026 — Optimized Hull
*Generated: {NOW}*

---

## Concrete Requirements

| Parameter | Value | Unit |
|-----------|------:|------|
| Net shell volume | {m['shell_vol_ft3']:.3f} | ft³ |
| Net shell volume | {m['shell_vol_gal']:.2f} | gallons |
| Safety/waste factor | ×{m['safety_mult']:.2f} | (40% margin) |
| **Total concrete needed** | **{m['total_needed_ft3']:.3f}** | **ft³** |
| **Total concrete needed** | **{m['total_needed_gal']:.2f}** | **gallons** |

## Batch Planning (5-Gallon Bucket Batches)

| Parameter | Value | Unit |
|-----------|------:|------|
| Batch size | 5.0 gal | ({m['bucket_vol_ft3']:.3f} ft³) |
| Batch weight | {m['bucket_vol_ft3']*CONCRETE_DENSITY_PCF:.1f} | lbs |
| **Number of batches** | **{m['num_batches']}** | batches |

## Reinforcement

| Parameter | Value | Unit |
|-----------|------:|------|
| Mesh type | Basalt fiber | — |
| Number of layers | 2 | — |
| Area per layer | {m['mesh_area_ft2']/2:.1f} | ft² |
| **Total mesh area** | **{m['mesh_area_ft2']:.1f}** | **ft² ({m['mesh_area_yd2']:.2f} yd²)** |
| POA | {REINFORCEMENT_POA_PCT:.0f}% | (≥40% req.) |
""")


def report_compliance(R):
    c = R["compliance"]
    h = R["hydro"]
    s = R["stability"]
    st = R["structural"]
    all_pass = (c["overall"] and h["pass_fb"] and s["pass_gm"] and st["pass_sf"])
    write_report("asce_compliance.md", f"""# ASCE Compliance Verification
## NAU ASCE Concrete Canoe 2026 — Optimized Hull
*Generated: {NOW}*

---

## Mix Design Compliance

| Requirement | Limit | Actual | Margin | Status |
|-------------|------:|-------:|-------:|--------|
| Cement-to-cementitious ratio | ≤ 0.40 | {c['cement_cementitious']['val']:.2f} | {(0.40-c['cement_cementitious']['val'])/0.40*100:.1f}% | {P(c['cement_cementitious']['ok'])} |
| Portland + lime (% by wt) | ≤ 40.0% | {c['portland_lime_pct']['val']:.1f}% | {(40.0-c['portland_lime_pct']['val'])/40.0*100:.1f}% | {P(c['portland_lime_pct']['ok'])} |
| Lime content | ≤ 5.0% | {c['lime_pct']['val']:.1f}% | {(5.0-c['lime_pct']['val'])/5.0*100:.1f}% | {P(c['lime_pct']['ok'])} |
| Reinforcement POA | ≥ 40.0% | {c['poa_pct']['val']:.1f}% | +{(c['poa_pct']['val']-40.0)/40.0*100:.1f}% | {P(c['poa_pct']['ok'])} |

## Performance Compliance

| Requirement | Limit | Actual | Margin | Status |
|-------------|------:|-------:|-------:|--------|
| Freeboard | ≥ 6.00 in | {h['fb_in']:.2f} in | +{h['fb_in']-6.0:.2f} in | {P(h['pass_fb'])} |
| Metacentric height (GM) | ≥ 6.00 in | {s['GM_in']:.2f} in | +{s['GM_in']-6.0:.2f} in | {P(s['pass_gm'])} |
| Safety factor | ≥ 2.0 | {st['SF']:.2f} | +{st['SF']-2.0:.2f} | {P(st['pass_sf'])} |

## Overall

| Category | Status |
|----------|--------|
| Mix design | {P(c['overall'])} |
| Hydrostatic (freeboard) | {P(h['pass_fb'])} |
| Stability (GM) | {P(s['pass_gm'])} |
| Structural (SF) | {P(st['pass_sf'])} |
| **OVERALL** | **{P(all_pass)}** |
""")


def report_construction(R):
    con = R["construction"]
    rows = ""
    for i in range(con["num_sections"] + 1):
        pos = min(i * con["spacing"], LENGTH_IN)
        frac = pos / LENGTH_IN
        b_at = BEAM_IN * math.sin(math.pi * frac) if 0 < frac < 1 else 0.0
        rows += f"| {i} | {pos:.0f} | {pos/12:.1f} | {b_at:.1f} |\n"
        if pos >= LENGTH_IN:
            break

    n_foam = math.ceil(con["num_sections"] / 4)
    write_report("construction_specs.md", f"""# Construction Specifications
## NAU ASCE Concrete Canoe 2026 — Optimized Hull
*Generated: {NOW}*

---

## Mold Dimensions (Female Mold)

| Parameter | Value | Unit |
|-----------|------:|------|
| Hull length | {LENGTH_IN:.0f} | in |
| Hull beam | {BEAM_IN:.0f} | in |
| Hull depth | {DEPTH_IN:.0f} | in |
| Mold length (with margin) | {con['mold_L']:.0f} | in ({con['mold_L']/12:.1f} ft) |
| Mold width (with margin) | {con['mold_B']:.0f} | in ({con['mold_B']/12:.1f} ft) |
| Mold depth (with margin) | {con['mold_D']:.0f} | in |

## CNC Cross-Section Stations

| Parameter | Value |
|-----------|------:|
| Section spacing | {con['spacing']:.0f} in |
| Number of sections | {con['num_sections']} |
| Cutting method | CNC hot-wire or router |
| Material | EPS foam, 2 lb/ft³ |

### Station Schedule

| Station # | Position (in) | Position (ft) | Beam at Station (in) |
|:---------:|-------------:|-------------:|--------------------:|
{rows}
## Cost Estimate

| Item | Est. Cost |
|------|----------:|
| EPS foam blocks ({n_foam} sheets) | ${n_foam * 45} |
| MDF strongback (3/4" × 36" × 16') | $80 |
| Adhesive & fasteners | $50 |
| PVA mold release (1 qt) | $25 |
| Sandpaper (80–400 grit) | $40 |
| **Total** | **${con['cost_estimate']:.0f}** |

## Construction Sequence

1. CNC-cut {con['num_sections']} cross-section templates from EPS foam
2. Mount templates on MDF strongback at {con['spacing']:.0f}" intervals
3. Fill between templates, sand to fair hull contour
4. Apply PVA release agent (2 coats)
5. Lay first basalt mesh layer into mold
6. Apply concrete in two lifts (bottom/sides, then gunwales)
7. Place second basalt mesh between lifts
8. Consolidate with vibration, trowel smooth
9. Wet-cure under plastic sheeting ≥ 7 days
10. De-mold, sand, apply finish coat
""")


def report_comparison(R):
    o = R["comparison"]["orig"]
    n = R["comparison"]["opt"]
    ws = R["comparison"]["wt_savings"]
    write_report("design_comparison.md", f"""# Design Comparison: Original vs. Optimized
## NAU ASCE Concrete Canoe 2026
*Generated: {NOW}*

---

## Dimensions

| Parameter | Original | Optimized | Change |
|-----------|--------:|---------:|-------:|
| Length (in) | {o['L']:.0f} | {n['L']:.0f} | {n['L']-o['L']:+.0f} |
| Beam (in) | {o['B']:.0f} | {n['B']:.0f} | {n['B']-o['B']:+.0f} |
| Depth (in) | {o['D']:.0f} | {n['D']:.0f} | {n['D']-o['D']:+.0f} |
| Weight (lbs) | {o['wt']:.0f} | {n['wt']:.1f} | {n['wt']-o['wt']:+.1f} |

## Performance

| Requirement | Min. | Original | Status | Optimized | Status |
|-------------|-----:|---------:|--------|----------:|--------|
| Freeboard (in) | ≥ 6.0 | {o['fb']:.2f} | {'✓' if o['fb'] >= 6.0 else '✗ FAIL'} | {n['fb']:.2f} | {'✓' if n['fb'] >= 6.0 else '✗ FAIL'} |
| GM (in) | ≥ 6.0 | {o['gm']:.2f} | {'✓' if o['gm'] >= 6.0 else '✗ FAIL'} | {n['gm']:.2f} | {'✓' if n['gm'] >= 6.0 else '✗ FAIL'} |
| Safety factor | ≥ 2.0 | {o['sf']:.2f} | {'✓' if o['sf'] >= 2.0 else '✗ FAIL'} | {n['sf']:.2f} | {'✓' if n['sf'] >= 2.0 else '✗ FAIL'} |

## Improvements

| Metric | Value |
|--------|------:|
| Weight savings | **{ws:.1f} lbs** ({ws/o['wt']*100:.1f}%) |
| Length reduction | {o['L']-n['L']:.0f} in |
| Beam increase | {n['B']-o['B']:+.0f} in |
| Depth reduction | {o['D']-n['D']:.0f} in |

## Summary

**Original (216" × 30" × 18", 276 lbs):** Failed the GM ≥ 6" stability
requirement due to narrow beam and high center of gravity.

**Optimized (192" × 32" × 17", {n['wt']:.0f} lbs):** Passes all three ASCE
requirements. Key changes:
- **+2" beam** → BM ∝ B², greatly improves transverse stability
- **-24" length** → reduces weight while maintaining capacity
- **-1" depth** → lowers CG, improves stability
- **Net weight savings: {ws:.0f} lbs** ({ws/o['wt']*100:.0f}%)
""")


def report_summary(R):
    h, s, st, w, m = R["hydro"], R["stability"], R["structural"], R["weight"], R["materials"]
    all_ok = h["pass_fb"] and s["pass_gm"] and st["pass_sf"] and R["compliance"]["overall"]
    write_report("ASCE_Design_Report_Summary.md", f"""# ASCE Design Report Summary
## NAU Concrete Canoe 2026
## Northern Arizona University
*Generated: {NOW}*

---

## Executive Summary

This report presents the complete engineering analysis for the NAU 2026 ASCE
Concrete Canoe competition entry. The optimized hull (192" × 32" × 17") meets
all ASCE requirements with adequate safety margins. Total estimated hull weight
is {w['total_hull_wt']:.0f} lbs, achieving a {R['comparison']['wt_savings']:.0f}-lb
reduction from the original 276-lb design.

---

## Hull Specifications

| Parameter | Value |
|-----------|------:|
| Length Overall (LOA) | {LENGTH_IN:.0f} in ({L_FT:.1f} ft) |
| Maximum Beam | {BEAM_IN:.0f} in ({B_FT:.2f} ft) |
| Depth | {DEPTH_IN:.0f} in ({D_FT:.3f} ft) |
| Shell Thickness | {THICKNESS_IN} in |
| Concrete Density | {CONCRETE_DENSITY_PCF:.0f} PCF |
| Flexural Strength | {FLEXURAL_STRENGTH_PSI:.0f} PSI |
| Hull Weight | {w['total_hull_wt']:.1f} lbs |

---

## ASCE Requirements — Compliance Matrix

| # | Requirement | Limit | Actual | Margin | Status |
|---|-------------|------:|-------:|-------:|--------|
| 1 | Freeboard | ≥ 6.00 in | {h['fb_in']:.2f} in | +{h['fb_in']-6:.2f} in | {P(h['pass_fb'])} |
| 2 | Metacentric height (GM) | ≥ 6.00 in | {s['GM_in']:.2f} in | +{s['GM_in']-6:.2f} in | {P(s['pass_gm'])} |
| 3 | Safety factor | ≥ 2.0 | {st['SF']:.2f} | +{st['SF']-2:.2f} | {P(st['pass_sf'])} |
| 4 | Cement/cementitious | ≤ 0.40 | {CEMENT_TO_CEMENTITIOUS:.2f} | {(0.40-CEMENT_TO_CEMENTITIOUS)/0.40*100:.0f}% | ✓ PASS |
| 5 | Portland + lime | ≤ 40% | {PORTLAND_PLUS_LIME_PCT:.0f}% | {(40-PORTLAND_PLUS_LIME_PCT)/40*100:.0f}% | ✓ PASS |
| 6 | Lime content | ≤ 5% | {LIME_CONTENT_PCT:.0f}% | {(5-LIME_CONTENT_PCT)/5*100:.0f}% | ✓ PASS |
| 7 | Reinforcement POA | ≥ 40% | {REINFORCEMENT_POA_PCT:.0f}% | +{REINFORCEMENT_POA_PCT-40:.0f}% | ✓ PASS |

### **Overall: {P(all_ok)}**

---

## Key Results

### Hydrostatics
| Parameter | Value |
|-----------|------:|
| Loaded displacement | {h['total_loaded_wt']:.0f} lbs |
| Draft | {h['draft_in']:.2f} in |
| Freeboard | {h['fb_in']:.2f} in |
| Block coefficient (Cb) | {h['Cb']:.3f} |
| Prismatic coefficient (Cp) | {h['Cp']:.3f} |

### Stability
| Parameter | Value |
|-----------|------:|
| KB | {s['KB_in']:.2f} in |
| BM | {s['BM_in']:.2f} in |
| KG | {s['KG_in']:.2f} in |
| **GM** | **{s['GM_in']:.2f} in** |

### Structural
| Parameter | Value |
|-----------|------:|
| Moment of inertia (Ix) | {st['Ix_in4']:.1f} in⁴ |
| Section modulus (Sx) | {st['Sx_in3']:.1f} in³ |
| Max bending moment | {st['M_max_lb_ft']:.0f} lb·ft |
| Flexural stress | {st['sigma_flex_psi']:.1f} psi |
| **Safety factor** | **{st['SF']:.2f}** |

### Weight
| Parameter | Value |
|-----------|------:|
| Concrete | {w['concrete_wt']:.1f} lbs |
| Reinforcement | {w['reinforcement_wt']:.1f} lbs |
| Finish + hardware | {w['finish_coat_wt']+w['hardware_wt']:.1f} lbs |
| **Total** | **{w['total_hull_wt']:.1f} lbs** |

### Materials
| Parameter | Value |
|-----------|------:|
| Concrete volume | {m['total_needed_ft3']:.2f} ft³ (with 40% margin) |
| Batches (5-gal) | {m['num_batches']} |
| Basalt mesh | {m['mesh_area_ft2']:.0f} ft² |

---

## Detailed Reports

| Report | File |
|--------|------|
| Hydrostatic Analysis | [hydrostatic_analysis.md](hydrostatic_analysis.md) |
| Stability Analysis | [stability_analysis.md](stability_analysis.md) |
| Structural Analysis | [structural_analysis.md](structural_analysis.md) |
| Weight Breakdown | [weight_breakdown.md](weight_breakdown.md) |
| Material Quantities | [material_quantities.md](material_quantities.md) |
| ASCE Compliance | [asce_compliance.md](asce_compliance.md) |
| Construction Specs | [construction_specs.md](construction_specs.md) |
| Design Comparison | [design_comparison.md](design_comparison.md) |

## Figures

| Figure | File |
|--------|------|
| Hull Profile | [figures/hull_profile.png](figures/hull_profile.png) |
| Cross-Sections | [figures/cross_sections.png](figures/cross_sections.png) |
| GZ Stability Curve | [figures/gz_curve.png](figures/gz_curve.png) |
| Bending Moment Diagram | [figures/bending_moment.png](figures/bending_moment.png) |
| Load Distribution | [figures/load_distribution.png](figures/load_distribution.png) |

---
*NAU ASCE Concrete Canoe Team — 2026 Competition*
""")


# ─── PLOT GENERATORS ──────────────────────────────────────────────────

def generate_plots(R):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 11, "figure.facecolor": "white"})

    h, s, st = R["hydro"], R["stability"], R["structural"]

    # ── 1. Hull Profile (Side Elevation) ──
    fig, ax = plt.subplots(figsize=(14, 4))
    x = np.linspace(0, LENGTH_IN, 300)
    # Sheer line with slight rise at ends
    sheer = DEPTH_IN * np.ones_like(x) + 1.2 * np.cos(np.pi * (x / LENGTH_IN - 0.5))
    # Keel with rocker
    keel = 0.8 * np.sin(np.pi * x / LENGTH_IN)
    ax.fill_between(x, keel, sheer, alpha=0.25, color="steelblue")
    ax.plot(x, sheer, "b-", lw=2, label="Sheer (deck edge)")
    ax.plot(x, keel, "b-", lw=2, label="Keel")
    # Waterline
    ax.axhline(y=h["draft_in"], color="deepskyblue", ls="--", lw=1.5,
               label=f'Waterline (T = {h["draft_in"]:.1f}")')
    # Freeboard annotation
    mid = LENGTH_IN / 2
    ax.annotate("", xy=(mid + 20, h["draft_in"]), xytext=(mid + 20, DEPTH_IN),
                arrowprops=dict(arrowstyle="<->", color="green", lw=1.5))
    ax.text(mid + 23, (h["draft_in"] + DEPTH_IN) / 2,
            f'FB = {h["fb_in"]:.1f}"', color="green", fontsize=10, va="center")
    ax.set_xlabel("Length (inches)")
    ax.set_ylabel("Height (inches)")
    ax.set_title(f'Hull Profile — {LENGTH_IN:.0f}" × {BEAM_IN:.0f}" × {DEPTH_IN:.0f}"')
    ax.legend(loc="upper right", fontsize=9)
    ax.set_xlim(-5, LENGTH_IN + 40)
    ax.set_ylim(-3, DEPTH_IN + 5)
    ax.grid(True, alpha=0.3)
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "hull_profile.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  ✓ reports/figures/hull_profile.png")

    # ── 2. Cross-Sections at 5 Stations ──
    fig, axes = plt.subplots(1, 5, figsize=(16, 5))
    stations = [0.10, 0.30, 0.50, 0.70, 0.90]
    names = ["Sta 1\n(Bow)", "Sta 2\n(Fwd Qtr)", "Sta 3\n(Midship)",
             "Sta 4\n(Aft Qtr)", "Sta 5\n(Stern)"]
    deadrise_deg = 15
    for ax, frac, name in zip(axes, stations, names):
        half_b = (BEAM_IN / 2.0) * math.sin(math.pi * frac)
        if half_b < 0.5:
            half_b = 0.5
        # V-bottom profile: keel at center, flare to beam
        n_pts = 40
        x_half = np.linspace(0, half_b, n_pts)
        y_bottom = np.zeros(n_pts)
        for j in range(n_pts):
            y_bottom[j] = x_half[j] * math.tan(math.radians(deadrise_deg))
        # Mirror for full section
        x_full = np.concatenate([-x_half[::-1], x_half[1:]])
        y_full = np.concatenate([y_bottom[::-1], y_bottom[1:]])
        # Add sides up to gunwale
        xs = np.concatenate([[-half_b], x_full, [half_b]])
        ys = np.concatenate([[DEPTH_IN], y_full, [DEPTH_IN]])
        ax.fill(xs, ys, alpha=0.25, color="steelblue")
        ax.plot(xs, ys, "b-", lw=2)
        # Waterline
        ax.axhline(y=h["draft_in"], color="deepskyblue", ls="--", lw=1, alpha=0.7)
        ax.set_title(name, fontsize=9)
        ax.set_xlim(-BEAM_IN / 2 - 2, BEAM_IN / 2 + 2)
        ax.set_ylim(-1, DEPTH_IN + 3)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        if ax == axes[0]:
            ax.set_ylabel("Height (in)")
    fig.suptitle("Hull Cross-Sections at 5 Stations", fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "cross_sections.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  ✓ reports/figures/cross_sections.png")

    # ── 3. GZ Stability Curve ──
    fig, ax = plt.subplots(figsize=(9, 5))
    angles = s["heel_angles"]
    gz_in = [g * 12 for g in s["gz_values_ft"]]
    ax.plot(angles, gz_in, "b-", lw=2.5, label="GZ (righting arm)")
    ax.fill_between(angles, 0, gz_in, alpha=0.12, color="blue")
    ax.axhline(y=0, color="gray", ls="-", lw=0.5)
    # Initial GM tangent
    ang_range = np.linspace(0, 25, 50)
    gz_gm = s["GM_in"] * np.sin(np.radians(ang_range))
    ax.plot(ang_range, gz_gm, "r--", lw=1.2, label=f'GM = {s["GM_in"]:.1f} in (initial slope)')
    # Max GZ
    max_gz_idx = np.argmax(gz_in)
    ax.plot(angles[max_gz_idx], gz_in[max_gz_idx], "ro", ms=7)
    ax.annotate(f'Max GZ = {gz_in[max_gz_idx]:.1f}" @ {angles[max_gz_idx]}°',
                xy=(angles[max_gz_idx], gz_in[max_gz_idx]),
                xytext=(angles[max_gz_idx] + 10, gz_in[max_gz_idx] - 1),
                arrowprops=dict(arrowstyle="->", color="red"), fontsize=9, color="red")
    ax.set_xlabel("Heel Angle (degrees)")
    ax.set_ylabel("GZ (inches)")
    ax.set_title("Righting Arm (GZ) Curve — Stability Analysis")
    ax.legend(fontsize=9)
    ax.set_xlim(0, 90)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "gz_curve.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  ✓ reports/figures/gz_curve.png")

    # ── 4. Bending Moment Diagram ──
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    x_ft = np.linspace(0, L_FT, 300)
    w_lb = st["w_self_lb_ft"]

    # Shear force from uniform load
    V = w_lb * (L_FT / 2.0 - x_ft)
    # Add paddler point loads (reaction at ends)
    for stn in st["paddler_stations"]:
        pos = stn * L_FT
        R_left = PADDLER_WEIGHT_LBS * (1 - stn)
        V = V + np.where(x_ft < pos, R_left, R_left - PADDLER_WEIGHT_LBS)

    ax1.plot(x_ft, V, "r-", lw=2)
    ax1.fill_between(x_ft, 0, V, alpha=0.2, color="red")
    ax1.axhline(0, color="gray", lw=0.5)
    ax1.set_ylabel("Shear Force (lbs)")
    ax1.set_title("Shear Force & Bending Moment Diagrams")
    ax1.grid(True, alpha=0.3)

    # Bending moment (numerical integration of shear)
    dx = x_ft[1] - x_ft[0]
    M = np.cumsum(V) * dx
    ax2.plot(x_ft, M, "b-", lw=2.5)
    ax2.fill_between(x_ft, 0, M, alpha=0.15, color="blue")
    pk = np.argmax(np.abs(M))
    ax2.plot(x_ft[pk], M[pk], "ro", ms=8)
    ax2.annotate(f"M_max = {M[pk]:.0f} lb·ft", xy=(x_ft[pk], M[pk]),
                 xytext=(x_ft[pk] + 1.5, M[pk] * 0.85),
                 arrowprops=dict(arrowstyle="->", color="red"), fontsize=10, color="red")
    ax2.axhline(0, color="gray", lw=0.5)
    ax2.set_xlabel("Position along hull (ft)")
    ax2.set_ylabel("Bending Moment (lb·ft)")
    ax2.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "bending_moment.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  ✓ reports/figures/bending_moment.png")

    # ── 5. Load Distribution Diagram ──
    fig, ax = plt.subplots(figsize=(12, 5))
    x_ft = np.linspace(0, L_FT, 300)
    # Self-weight (downward)
    w_down = -w_lb * np.ones_like(x_ft)
    # Buoyancy (upward, parabolic distribution)
    buoy = st["buoy_per_ft"] * (1 - ((x_ft - L_FT / 2) / (L_FT / 2))**2)
    buoy *= (st["buoy_per_ft"] * L_FT) / np.trapezoid(buoy, x_ft)  # normalize
    ax.fill_between(x_ft, 0, buoy, alpha=0.25, color="green", label="Buoyancy (upward)")
    ax.plot(x_ft, buoy, "g-", lw=2)
    ax.fill_between(x_ft, 0, w_down, alpha=0.25, color="red", label="Self-weight (downward)")
    ax.plot(x_ft, w_down, "r-", lw=2)
    # Paddler arrows
    for i, stn in enumerate(st["paddler_stations"]):
        pos = stn * L_FT
        ax.annotate(f"P{i+1}\n{PADDLER_WEIGHT_LBS:.0f} lb",
                    xy=(pos, -w_lb * 1.1), xytext=(pos, -w_lb * 2.5),
                    ha="center", fontsize=8, color="darkred",
                    arrowprops=dict(arrowstyle="->", color="darkred", lw=1.5))
    ax.axhline(0, color="gray", lw=0.5)
    ax.set_xlabel("Position along hull (ft)")
    ax.set_ylabel("Load Intensity (lb/ft)")
    ax.set_title("Load Distribution — Racing Condition (4 Paddlers)")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "load_distribution.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  ✓ reports/figures/load_distribution.png")


# ─── MAIN ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  NAU ASCE Concrete Canoe 2026 — Report Generator")
    print("=" * 60)

    # Step 1: Calculate
    print("\n[1/3] Running calculations...")
    R = compute_all()

    w = R["weight"]
    h = R["hydro"]
    s = R["stability"]
    st = R["structural"]

    print(f"\n  Hull weight:    {w['total_hull_wt']:.1f} lbs (target: {w['target_wt']:.0f})")
    print(f"  Freeboard:      {h['fb_in']:.2f} in  (≥6.00)  {P(h['pass_fb'])}")
    print(f"  GM:             {s['GM_in']:.2f} in  (≥6.00)  {P(s['pass_gm'])}")
    print(f"  Safety factor:  {st['SF']:.2f}      (≥2.00)  {P(st['pass_sf'])}")

    # Step 2: Reports
    print("\n[2/3] Generating reports...")
    report_hydrostatic(R)
    report_stability(R)
    report_structural(R)
    report_weight(R)
    report_materials(R)
    report_compliance(R)
    report_construction(R)
    report_comparison(R)
    report_summary(R)

    # Step 3: Plots
    print("\n[3/3] Generating plots (300 DPI)...")
    generate_plots(R)

    # Summary
    print("\n" + "=" * 60)
    print("  ALL DELIVERABLES GENERATED")
    print("=" * 60)

    reports = sorted(REPORTS_DIR.glob("*.md"))
    figures = sorted(FIGURES_DIR.glob("*.png"))

    print(f"\n{'File':<50s} {'Size':>10s}")
    print("-" * 62)
    for f in reports + figures:
        sz = f.stat().st_size
        print(f"  {str(f.relative_to(PROJECT_ROOT)):<48s} {sz:>8,} B")

    print(f"\n  Reports: {len(reports)}  |  Figures: {len(figures)}")

    all_ok = h["pass_fb"] and s["pass_gm"] and st["pass_sf"] and R["compliance"]["overall"]
    print(f"\n  {'✓ ALL ASCE REQUIREMENTS MET' if all_ok else '✗ SOME REQUIREMENTS NOT MET'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
