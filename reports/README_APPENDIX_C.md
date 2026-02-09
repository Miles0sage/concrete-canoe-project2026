# Appendix C — Example Design Calculations

**NAU ASCE Concrete Canoe 2026 | Design C: 216" × 36" × 18" × 0.75"**

---

## 📄 Competition Submission (Use This)

**PDF for judges:** [`Appendix_C_Integrated.pdf`](./Appendix_C_Integrated.pdf) (248 KB, 4 pages)

Meets ASCE 2026 RFP Section 5.5.16 requirements:
- ✅ All assumptions listed with references [1]-[8]
- ✅ Free-body diagram with loads, dimensions, reactions
- ✅ All 4 load cases (2-person male/female, 4-person coed, transportation)
- ✅ Moment of inertia with neutral axis location (parallel axis theorem)
- ✅ Maximum compressive, tensile, and punching shear stresses
- ✅ Cross-sectional properties by hand calculation
- ✅ Safety factors / demand-capacity ratios justified
- ✅ Format: Times New Roman 12pt, 0.5" margins, 8.5×11

---

## 🔧 How It Was Generated

**Generator script:** [`../scripts/generate_appendix_c_integrated.py`](../scripts/generate_appendix_c_integrated.py)

**Key feature:** Integrated with calculator v2.1 — **single source of truth**

This script:
1. **Imports** functions from `calculations/concrete_canoe_calculator.py` (no duplicate physics)
2. **Calls** the validated hull analysis engine:
   - `estimate_hull_weight()` → 245 lbs from geometry
   - `section_modulus_thin_shell()` → 129.6 in³ via parallel axis theorem
   - `run_complete_analysis()` → freeboard, GM, stresses for each load case
   - `metacentric_height_approx()` → GM = 15.69" (Bouguer's formula)
3. **Generates** 4-page PDF with full citations to [1]-[8]
4. **Outputs** step-by-step calculation trace to console

---

## 📊 Example Calculation Trace

When you run the script, you see every intermediate step:

```
[STEP 1] HULL WEIGHT FROM GEOMETRY
  estimate_hull_weight(216.0, 36.0, 18.0, 0.75, 60.0) → 245.0 lbs
  Method: U-shell (bottom + 2 walls) × Cp=0.55 × 1.10 overhead
  Cross-check (Ramanujan half-ellipse): 318.1 lbs (no overhead)
  Ratio: 0.77 (prismatic + overhead adjustment)

[STEP 2] CROSS-SECTION PROPERTIES — THIN-SHELL U-SECTION
  section_modulus_thin_shell(36.0, 18.0, 0.75) → S_x = 129.6 in³

  Component 1 — Bottom plate (36.0 × 0.75):
    A₁ = 27.00 in², y₁ = 0.375"
  Component 2,3 — Side walls (0.75 × 17.25):
    A₂ = A₃ = 12.938 in², y₂ = y₃ = 9.375"

  Composite centroid [5] Eq. 6.3:
    y_bar = ΣA_i·y_i / ΣA = 4.779" from bottom

  Moment of inertia [5] Eq. 6.6 (I = I_c + A·d²):
    I_bot = 1.27 + 27.00×(4.78-0.375)² = 525.0 in⁴
    I_side = 320.81 + 12.94×(9.38-4.779)² = 594.1 in⁴
    I_x = 525.0 + 2×594.1 = 1713.1 in⁴

  Section moduli [5] S = I/c:
    S_top = 1713.1/13.22 = 129.6 in³ (compression)
    S_bot = 1713.1/4.78 = 358.4 in³ (tension)

[STEP 3] ANALYZE ALL LOAD CASES
  4-Person Coed (700 lbs crew):
    W_total = 245 + 700 = 945 lbs
    Draft = 4.81", Freeboard = 13.19"
    GM = 15.69"
    M_max = 3701 lb-ft
    σ = 342.8 psi, SF = 4.38

  GOVERNING CASE: 4-Person Coed (M = 3701 lb-ft)

[STEP 4] DETAILED GOVERNING CASE CALCULATIONS
  A. Hydrostatics [3] SNAME Vol I, Ch. 2
     V_disp = W/ρ_water = 945/62.4 = 15.14 ft³
     A_wp = L×B×C_wp = 18.0×3.00×0.7 = 37.80 ft²
     Draft = V/A_wp = 15.14/37.80 = 4.81"
     Freeboard = 18 - 4.81 = 13.19" > 6.0" ✓

  B. Stability [3] SNAME Vol I, Ch. 3
     I_wp = 0.7×18.0×3.00³/12 = 28.35 ft⁴
     BM = I_wp/V = 28.35/15.14 = 22.46" (Bouguer's formula)
     GM = KB + BM - KG = 2.40 + 22.46 - 9.18 = 15.69" > 6.0" ✓

  C. Structural [1] ACI 318-25 LRFD
     M_u = 1.2M_D + 1.6M_L = 1.2×551 + 1.6×3150 = 5702 lb-ft
     σ_c = M_u/S_top = 68419/129.6 = 528.0 psi
     SF_comp = 2000/528.0 = 3.79 > 2.0 ✓
     DCR = M_u/φM_n = 5702/29124 = 0.196 < 1.0 ✓

  D. Punching Shear [1] ACI 318-25 Sec 22.6.5.2
     φV_c = 0.75×4√2000×18.40×0.60 = 1481 lbs
     DCR = 280/1481 = 0.189 < 1.0 ✓
```

**All checks PASS.**

---

## 📚 References (Cited Throughout)

| Tag | Source | What It Covers |
|-----|--------|----------------|
| [1] | ACI 318-25 | Load factors (5.3.1b), phi factors (21.2.1), punching shear (22.6.5.2) |
| [2] | ASCE 2026 RFP | Crew weights (6.2), dimensions (5.5.4), Appendix C format (5.5.16) |
| [3] | *Principles of Naval Architecture* (SNAME) | Waterplane area, draft, Bouguer's BM = I_wp/V |
| [4] | Ramanujan (1914) | Ellipse perimeter for hull surface area → weight |
| [5] | Beer et al. *Mechanics of Materials* | Parallel axis theorem (Eq 6.6), σ = M/S, beam formulas |
| [6] | ASTM C78 | Modulus of rupture test method |
| [7] | Tupper *Intro to Naval Architecture* | COG estimation for loaded canoe |
| [8] | ACI 318R-25 Commentary | Plain concrete phi factor justification |

---

## 🔁 How to Regenerate (If Dimensions Change)

```bash
cd concrete-canoe-project2026
/opt/sys-venv/bin/python3 scripts/generate_appendix_c_integrated.py
```

**To change design parameters**, edit these lines at the top of `generate_appendix_c_integrated.py`:

```python
L_in = 216.0   # length (inches)
B_in = 36.0    # beam (inches)
D_in = 18.0    # depth (inches)
t_in = 0.75    # wall thickness (inches)
density_pcf = 60.0
f_c = 2000.0   # compressive strength (psi)
f_r = 1500.0   # modulus of rupture (psi)
```

Everything else recalculates automatically from geometry.

---

## ⚠️ Note on Standalone Version

`Appendix_C_Example_Calculations.pdf` (first version) exists as a backup but has **hardcoded physics** separate from the calculator. **Do not use** for competition — it was replaced by the integrated version.

---

## ✅ Verification

All calculations independently verified by:
- **concrete_canoe_calculator.py v2.1** — NAU's validated hull analysis engine
- **5 test modules** (pytest) covering geometry, hydrostatics, stability, structural analysis
- **Hand calculations** using parallel axis theorem per ASCE 2026 Sec 5.5.16

Functions used:
- `[Tool-A]` run_complete_analysis() — full pipeline
- `[Tool-B]` section_modulus_thin_shell() — I_x, S_x
- `[Tool-C]` metacentric_height_approx() — GM
- `[Tool-D]` estimate_hull_weight() — W from geometry
- `[Tool-E]` bending_moment_distributed_crew() — M with concentrated crew

---

**Contact:** Northern Arizona University ASCE Student Chapter
**Repository:** https://github.com/Miles0sage/concrete-canoe-project2026
**Competition:** ASCE 2026 Concrete Canoe Competition
