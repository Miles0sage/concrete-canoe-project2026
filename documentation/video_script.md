# NAU Concrete Canoe 2026 — Video Script (5 Minutes)

## 0:00–0:30 — Problem Statement

**[SHOW: Title card with NAU logo]**

> "The NAU ASCE Concrete Canoe team identified a critical stability problem
> in the 2025 competition season — insufficient metacentric height (GM)
> caused near-capsize incidents during slalom events.
>
> For 2026, we redesigned the hull from scratch using computational
> optimization to guarantee compliance with all ASCE requirements."

**[SHOW: `reports/figures/3_designs_summary_table.png`]**

---

## 0:30–1:30 — Optimization Approach

**[SHOW: `calculations/concrete_canoe_calculator.py` code scrolling]**

> "We built a Python-based hydrostatic, stability, and structural
> analysis pipeline. The calculator models:
>
> - Weight estimation from hull geometry and concrete density (60 PCF)
> - Freeboard under loaded conditions (4 paddlers at 175 lbs each)
> - Metacentric height GM using KB + BM - KG
> - Structural safety factor from bending analysis
>
> We ran Monte Carlo simulation with 1,000 iterations varying
> concrete density, wall thickness, flexural strength, and paddler
> weight to quantify uncertainty."

**[SHOW: `reports/figures/uncertainty_distributions.png`]**

> "Result: 100% pass rate under all tested conditions."

---

## 1:30–2:30 — Three Design Comparison

**[SHOW: `reports/figures/3_designs_profiles.png`]**

> "We generated three alternative hull designs:
>
> - **Design A (Optimal)**: 192" × 32" × 17" at 174 lbs — lightest option
> - **Design B (Conservative)**: 196" × 34" × 18" at 188 lbs — extra margin
> - **Design C (Traditional)**: 216" × 36" × 18" at 214 lbs — easiest build
>
> All three pass every ASCE requirement."

**[SHOW: `reports/figures/3_designs_performance.png` — bar charts]**

> "Design A is 28% under the 237 lb weight target, with 11 inches
> of freeboard, 9.5 inches of GM, and a safety factor of 104."

**[SHOW: `reports/figures/3_designs_radar.png` — radar chart]**

---

## 2:30–3:30 — Interactive Dashboard Demo

**[SHOW: Screen recording of `dashboard/app.py` running]**

> "We built an interactive Streamlit dashboard that lets anyone
> explore hull designs in real time. Adjust sliders for length,
> beam, depth, thickness, and number of paddlers.
>
> The dashboard shows live pass/fail indicators, a 3D hull preview,
> radar chart comparison against all three baseline designs,
> and one-click CSV export."

**[SHOW: Adjusting sliders, 3D hull rotating]**

---

## 3:30–4:30 — Construction Roadmap

**[SHOW: `reports/figures/construction_sequence.png`]**

> "Construction follows six phases:
>
> 1. Mold fabrication (EPS foam on plywood strongback)
> 2. PVA mesh reinforcement placement
> 3. Three-layer concrete application (0.5" total)
> 4. Seven-day moist cure
> 5. Demolding with 6-person team
> 6. Finishing, sealing, and graphics
>
> Estimated material cost: $580 including 15% contingency."

**[SHOW: `reports/figures/hull_lines_plan.png`]**

---

## 4:30–5:00 — Next Steps & Closing

**[SHOW: `reports/figures/3d_hull_design_A.png`]**

> "Next steps:
> - Finalize concrete mix design by February 15
> - Begin mold construction by March 1
> - Concrete placement by April 1
> - Competition prep by April 15
>
> We're confident Design A delivers the optimal combination
> of performance, weight, and constructability for NAU's
> 2026 ASCE Concrete Canoe entry.
>
> Thank you."

**[SHOW: Final title card with team members]**
