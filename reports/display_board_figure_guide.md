# NAU ASCE Concrete Canoe 2026 -- Display Board Figure Guide

## Reference: ASCE 2026 RFP Section 7.0 -- Product Display

**Display Constraints:**
- Maximum dimensions: 4 ft wide x 8 ft long x 7 ft tall
- Must be free-standing and self-supporting
- Judging from the front face only
- 25 points total for Product Display scoring

**Display Must Showcase:**
- Hull design process (shape selection, alternatives considered, analysis)
- Research and testing (mix design, structural verification, innovation)
- Construction techniques (mold, layup, curing, finishing)

**Selected Design:** Design A -- 192" x 32" x 17" x 0.5", 174.3 lbs ("Lightweight Racer")

---

## Complete Figure Inventory

The project contains **74 unique PNG figures** across three directories:
- `reports/figures/` (68 files -- primary location)
- `docs/figures/` (12 files -- copies for documentation)
- `docs/` (8 additional files)

---

## Section 1: HULL DESIGN (Top-Left Panel)

### Priority Figures:

**1. `design_A_complete_suite.png`** (HIGHEST PRIORITY)
- Path: `reports/figures/design_A_complete_suite.png`
- Shows: Six-panel composite proving Design A meets every ASCE threshold. Includes hull profile with waterline, cross-sections, GZ curve, bending moment, shear force, and summary (174.1 lbs, FB 11.4" PASS, GM 8.7" PASS, SF 2.38 PASS).
- Why: Single most important display figure. Print large (18"x12" minimum).

**2. `hull_profile.png`**
- Path: `reports/figures/hull_profile.png`
- Shows: Clean side elevation with sheer line, keel, waterline T=5.8", freeboard FB=11.2".
- Why: Simple, clean hull shape for immediate visual comprehension.

**3. `cross_sections.png`**
- Path: `reports/figures/cross_sections.png`
- Shows: Five stations from Bow to Stern showing V-bottom transitions.
- Why: Standard naval architecture deliverable ASCE judges expect.

**4. `hull_lines_plan.png`**
- Path: `reports/figures/hull_lines_plan.png`
- Shows: Traditional 3-view lines plan (body plan, profile, half-breadth) at 11 stations.
- Why: Gold standard of hull design documentation.

**5. `3d_hull_design_A.png`**
- Path: `reports/figures/3d_hull_design_A.png`
- Shows: 3D surface plot of Design A hull.
- Why: Eye-catching from distance, draws judges to the board.

**6. Alternative designs (to show design rationale):**
- `3_designs_profiles.png` -- side-by-side profiles of A/B/C with paddler positions
- `3_designs_radar.png` -- 5-axis radar comparing weight, freeboard, GM, SF, maneuverability
- `3_designs_performance.png` -- 2x2 bar charts of weight/freeboard/GM/SF vs thresholds
- `3_designs_summary_table.png` -- full comparison table with Design A starred
- `3_designs_cross_sections.png` -- midship sections for all three designs

---

## Section 2: MIX DESIGN (Top-Right Panel)

### Priority Figures:

**1. `mix3_showcase.png`** (HIGHEST PRIORITY)
- Path: `reports/figures/mix3_showcase.png`
- Shows: Five-panel breakdown -- cementitious pie (Portland 30.8%, Slag 47.2%, Fly Ash 18.9%, Lime 3.1%), aggregate bars (Poraver 131.2 lb, Perlite 88.2 lb, K1 38.9 lb), key properties (58.6 pcf, 1,774 psi, w/cm 0.36), strength timeline (7-day 273 psi to 28-day 1,774 psi), ASCE compliance grid.
- Why: Complete mix design on one sheet. Most critical mix figure.

**2. `mix_asce_compliance.png`**
- Path: `reports/figures/mix_asce_compliance.png`
- Shows: Compliance grid for all 3 mixes -- Portland <=40%, Lime <=5%, Density 48-65 pcf, 28-day >=1,500 psi, w/cm <=0.50. Mix 3 COMPLIANT; Mixes 1/2 NON-COMPLIANT.
- Why: Instant proof the selected mix passes every ASCE rule.

**3. `mix_co2_curing_benefit.png`**
- Path: `reports/figures/mix_co2_curing_benefit.png`
- Shows: Standard vs CO2 curing curves, day each hits 1,500 psi, benefits summary.
- Why: Innovation differentiator. CO2 curing shows research depth.

**4. Other mix figures available:**
- `mix_decision_matrix.png` -- weighted scoring, Mix 3 at 8.7/10 "EXCELLENT"
- `mix_strength_prediction.png` -- 28-day predictions with conservative/typical/optimistic bands
- `mix_composition_comparison.png` -- side-by-side pie charts for all 3 mixes
- `mix_comparison_table.png` -- full comparison table with winner callout

---

## Section 3: STRUCTURAL ANALYSIS (Center Panel)

### Priority Figures:

**1. `report_fbd_shear_moment.png`** (HIGHEST PRIORITY)
- Path: `reports/figures/report_fbd_shear_moment.png`
- Shows: 3-panel stacked: FBD (simply-supported beam, hull UDL, 4 paddler point loads, reactions), shear force diagram, bending moment diagram with M_max annotated.
- Why: Core structural engineering deliverable. Non-negotiable for ASCE display.

**2. `report_moi_analysis.png`**
- Path: `reports/figures/report_moi_analysis.png`
- Shows: (Left) Midship cross-section with 3 component rectangles and neutral axis. (Right) Full calculation trace: areas, centroids, parallel axis theorem, I_total, section modulus with ACI 318 0.75 reduction, bending stress, and safety factor box.
- Why: Complete calculation chain from geometry to SF verdict. Exactly what judges evaluate.

**3. `presentation_monte_carlo_simple.png`**
- Path: `reports/figures/presentation_monte_carlo_simple.png`
- Shows: Bell curve of 1,000 SF simulations, green SAFE zone vs red FAIL zone, pass rate annotation, statistics box.
- Why: Strong differentiator -- probabilistic analysis goes beyond basic hand calcs.

**4. New Design A figures:**
- `fbd_governing_design_A.png` -- FBD specific to Design A 4-person coed governing case
- `cross_section_design_A.png` -- U-section with neutral axis at y=4.57"
- `shear_moment_design_A.png` -- Shear and moment diagrams for Design A

**5. Other structural figures:**
- `report_section_breakdown.png` -- plan view with section cuts, cross-sections with title block
- `report_top_isometric.png` -- plan + isometric wireframe with title block
- `gz_curve.png` -- GZ stability curve (0-90 deg)
- `sensitivity_tornado.png` -- sensitivity of SF to input variations
- `uncertainty_distributions.png` -- input parameter distributions for Monte Carlo

---

## Section 4: CONSTRUCTION (Bottom Panel)

### Priority Figures:

**1. `construction_overview_timeline.png`** (HIGHEST PRIORITY)
- Path: `reports/figures/construction_overview_timeline.png`
- Shows: 21-day Gantt chart with 7 phases, week markers, milestones.
- Why: Full build process at a glance.

**2. Construction step sequence (7 figures):**
- `construction_step1_mold_build.png` -- EPS foam mold on MDF strongback
- `construction_step2_mold_surface.png` -- surface prep and release agent
- `construction_step3_reinforcement.png` -- PVA fiber mesh placement
- `construction_step4_concrete_application.png` -- hand-layup technique
- `construction_step5_curing.png` -- curing process
- `construction_step6_demold.png` -- hull extraction
- `construction_step7_finishing.png` -- finishing, sealing, graphics

**3. `cad_sheet3_construction_details.png`**
- Path: `reports/figures/cad_sheet3_construction_details.png`
- Shows: Mold details, reinforcement layout, layer buildup, keel detail.
- Why: Professional engineering construction drawing.
- NOTE: Currently generated for Design C (216x36x18). Should be regenerated for Design A.

---

## Section 5: PRESENTATION/COMPLIANCE (Supporting)

- `presentation_design_comparison.png` -- pass/fail table with RECOMMENDED badge
- `presentation_why_design_A.png` -- 4 bar charts (weight/FB/GM/SF vs thresholds)
- `presentation_how_it_works.png` -- 5-step flowchart of analysis pipeline
- `presentation_key_numbers.png` -- KPI dashboard (5 metric cards)
- AI snippet figures (4 files) -- code snippets showing AI-assisted development

---

## Recommended Display Board Layout (4 ft W x 8 ft L)

```
+================================================================+
|                    NAU ASCE CONCRETE CANOE 2026                 |  <- Title Banner
|                     "PLUTO JACKS" -- Design A                   |     (4" tall)
+================================+===============================+
|                                |                               |
|       HULL DESIGN              |        MIX DESIGN             |
|                                |                               |
|  [hull_profile.png]            |  [mix3_showcase.png]          |
|  [cross_sections.png]          |  [mix_asce_compliance.png]    |
|  [3_designs_radar.png]         |  [mix_co2_curing_benefit.png] |
|  [design_A_complete_suite.png] |                               |
|                                |                               |
+================================+===============================+
|                                                                |
|                   STRUCTURAL ANALYSIS                           |
|                                                                |
|  [report_fbd_shear_moment.png]    [report_moi_analysis.png]   |
|  [presentation_monte_carlo_simple.png]                         |
|                                                                |
+================================================================+
|                                                                |
|                   CONSTRUCTION PROCESS                          |
|                                                                |
|  [construction_overview_timeline.png]                          |
|  [step1] [step2] [step3] [step4] [step5] [step6] [step7]     |
|  [cad_sheet3_construction_details.png]                         |
|                                                                |
+================================================================+
|  Key Numbers: 174 lbs | FB 11.4" | GM 8.7" | SF 2.38 | PASS  |  <- Footer
+================================================================+
```

---

## Top 12 Priority Ranking

| Rank | Figure | Section | Rationale |
|------|--------|---------|-----------|
| 1 | `design_A_complete_suite.png` | Hull | Single figure proves all ASCE checks pass |
| 2 | `report_fbd_shear_moment.png` | Structural | Core structural engineering deliverable |
| 3 | `mix3_showcase.png` | Mix | Complete mix design on one sheet |
| 4 | `construction_overview_timeline.png` | Construction | Full build process at a glance |
| 5 | `hull_profile.png` | Hull | Clean hull shape visualization |
| 6 | `report_moi_analysis.png` | Structural | Calculation trace with safety factor result |
| 7 | `3_designs_radar.png` | Hull | Shows alternatives were considered |
| 8 | `mix_asce_compliance.png` | Mix | Proves mix meets every ASCE rule |
| 9 | `cross_sections.png` | Hull | Standard naval architecture deliverable |
| 10 | `presentation_monte_carlo_simple.png` | Structural | Innovation differentiator |
| 11 | `construction_step4_concrete_application.png` | Construction | Shows hand-layup technique |
| 12 | `cad_sheet3_construction_details.png` | Construction | Professional engineering drawing |

---

## Identified Gaps -- Figures Needed But Not Yet Created

### High Priority

1. **Construction Photographs:** All current figures are code-generated plots. The display needs real photographs of mold building, mesh placement, concrete layup, curing, demolding, finishing, and the final canoe on water.

2. **Canoe Name/Branding Graphic:** No standalone logo exists for "Pluto Jacks." A display-quality branding graphic is needed for the title banner.

3. **Sustainability/Environmental Impact Figure:** A figure showing CO2 reduction from 69.2% Portland replacement in Mix 3 and lifecycle comparison would strengthen the display given ASCE's emphasis on sustainability.

4. **Paddler Loading Configuration:** A Design A-specific diagram showing the 4-paddler positions, CG locations, and loading on the hull.

### Medium Priority

5. **Design A Reinforcement Layout:** The CAD Sheet 3 (`cad_sheet3_construction_details.png`) was generated for Design C (216x36x18). A version specific to Design A (192x32x17) is needed.

6. **Curing Protocol Detail:** A more detailed comparison of standard moist curing vs CO2 carbonation with temperature/humidity monitoring data.

7. **Cost Breakdown Chart:** Design A suite shows $742 estimated cost. A dedicated pie chart would help the economic argument.

8. **Weight Budget Waterfall Chart:** Showing concrete shell -> reinforcement -> filler -> 174.3 lbs total vs 237 lb target.

### Low Priority

9. **Competition Day Logistics Figure:** A specific competition-day checklist/timeline.

10. **QA/QC Testing Protocol:** Test cylinder schedule, density checks, thickness verification plan.

---

## Print Quality Notes

- All main figures are 300 DPI (suitable for large-format printing up to 24"x18")
- Report drawings (`report_*.png`) are 150 DPI -- regenerate at 300 DPI for large display prints
- NAU branding (Blue #003466, Gold #FFC72C) is consistent throughout
- For display viewing at 3-6 ft, ensure minimum 14pt font on printed figures
- Consider printing priority 1-4 figures at 150-200% scale

---

*Generated for NAU ASCE Concrete Canoe Team -- February 2026*
