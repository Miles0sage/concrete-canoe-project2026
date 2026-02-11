# Calculator Verification & Fix Process Log

## Date: February 2026

## Problem Statement
A teammate questioned whether the calculator was correct. Investigation revealed the **core calculator (`concrete_canoe_calculator.py`) was correct all along**, but three wrapper scripts had copied formulas incorrectly, producing different numbers and creating confusion.

## Root Cause Analysis

### The core calculator (NO changes needed)
`calculations/concrete_canoe_calculator.py` v2.1 already had all correct formulas:
- Cwp = 0.70 (waterplane coefficient)
- 3D Bouguer's BM = I_wp / V_disp
- Weighted COG from hull + crew components
- Hull UDL + crew point load bending moment model
- Thin-shell U-section modulus via parallel axis theorem

### What was wrong: 3 wrapper scripts with inline physics

These scripts duplicated the calculator's formulas instead of calling it, and the copies were wrong/outdated:

| Bug | Wrong Value (wrapper scripts) | Correct Value (calculator) |
|-----|-------------------------------|---------------------------|
| Waterplane coeff | Cwp = 0.65 | Cwp = 0.70 |
| Metacentric radius | BM = B²/(12T) (2D shortcut) | BM = Cwp·L·B³/12 / V_disp (3D Bouguer's) |
| Center of gravity | KG = 0.45·D (fixed fraction) | KG = (W_hull·0.38D + W_crew·10"/12) / W_total |
| Bending moment | M = wL²/8 (uniform only) | M = wL²/8 + PL/4 (hull UDL + crew point load) |

Affected files:
1. `scripts/uncertainty_analysis.py` — Monte Carlo simulation
2. `dashboard/app.py` — Streamlit interactive dashboard
3. `scripts/generate_detailed_design_reports.py` — generated the design A/B/C analysis reports

### Stale reports
The design reports (A, B, C) showed Safety Factor = 103.8, 119.6, 111.7 — absurdly high because the report generator used the wrong section modulus (solid rectangle S = 1,452 in³ instead of thin-shell S = 58 in³).

## Fixes Applied

### Step 1: Created `scripts/verification_report.py`
Independent hand-calculation script that derives every result from first principles for Design A (192x32x17x0.5) and compares against the calculator. Sections:
- A. Hydrostatics (Archimedes)
- B. Stability (3D Bouguer's)
- C. Section Properties (parallel axis theorem)
- D. Bending Moment (hull UDL + crew point load)
- E. Stress & Safety Factor
- F. Cross-validation & reference ranges

**Result: 8/8 hand calculations match calculator within 2% tolerance.**

### Step 2: Fixed `scripts/uncertainty_analysis.py`
- Line 45: `cwp: 0.65` → `0.70`
- Lines 88-89: 2D BM → 3D formula, fixed KG → weighted COG
- Lines 93-94: uniform moment → hull+crew model
- Added imports: `bending_moment_distributed_crew`, `calculate_cog_height`

### Step 3: Fixed `dashboard/app.py`
- Line 41: `CWP = 0.65` → `0.70`
- Lines 78-79: Same BM and KG fixes
- Lines 82-83: Same moment fix
- Added imports

### Step 4: Fixed `scripts/generate_detailed_design_reports.py`
- Same 4 physics fixes in `full_analysis()`
- Updated report template to show hull+crew load model
- Regenerated all 3 design reports

### Step 5: Verification
- `pytest tests/ -v` — **60/60 tests pass**
- `python scripts/verification_report.py` — **8/8 hand calcs match**
- `python scripts/uncertainty_analysis.py` — Monte Carlo completes, 83.7% pass rate

## Impact Summary

### Design A (192x32x17x0.5)
| Metric | Before (wrong) | After (correct) |
|--------|---------------|-----------------|
| Section Modulus | 1,452 in³ | 58.0 in³ |
| Safety Factor | 103.8 | 2.30 |
| GM | 9.5" | 8.7" |
| Freeboard | 10.9" | 11.4" |

### Monte Carlo pass rate
Dropped from ~100% to 83.7% — expected because the corrected hull+crew moment model is 80% more conservative. Baseline designs still pass all criteria deterministically.

### What was NOT changed
- `calculations/concrete_canoe_calculator.py` — source of truth, already correct
- `scripts/generate_structural_fbd.py` — sinusoidal buoyancy is intentional for FBD diagrams
- `scripts/generate_appendix_c.py` — ACI factored loads are correct LRFD practice
- All 60 unit/integration tests — unchanged and passing

## Lesson Learned
Wrapper scripts should call the core calculator functions instead of reimplementing physics inline. When formulas are duplicated across files, they inevitably drift out of sync.

## References
- ACI 318-25: Building Code Requirements for Structural Concrete
- SNAME PNA Vol I: Principles of Naval Architecture — Stability & Strength
- Beer/Johnston: Mechanics of Materials (7th ed.)
