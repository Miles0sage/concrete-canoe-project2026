# NAU ASCE Concrete Canoe 2026 — Presentation Slides

## Slide 1: Title
**NAU ASCE Concrete Canoe 2026**
*Computational Hull Optimization & Design Analysis*
Northern Arizona University — ASCE Student Chapter

---

## Slide 2: Problem Statement
- 2025 competition: GM stability failure during slalom
- Root cause: Insufficient metacentric height (GM < 6")
- Goal: Redesign hull to guarantee ASCE compliance

**Key Requirements:**
| Metric | Requirement |
|--------|-------------|
| Freeboard | ≥ 6 inches |
| GM (Stability) | ≥ 6 inches |
| Safety Factor | ≥ 2.0 |
| Weight | ≤ 237 lbs |

---

## Slide 3: Methodology
- Python-based analysis pipeline (`concrete_canoe_calculator.py`)
- Hydrostatic, stability, and structural calculations
- Monte Carlo uncertainty quantification (1,000 iterations)
- Sensitivity analysis via tornado diagrams

**[IMAGE: `uncertainty_distributions.png`]**

---

## Slide 4: Three Design Alternatives
| | Design A | Design B | Design C |
|---|---|---|---|
| Dimensions | 192" × 32" × 17" | 196" × 34" × 18" | 216" × 36" × 18" |
| Weight | 174 lbs | 188 lbs | 214 lbs |
| Philosophy | Lightest | Extra margin | Easy build |

**[IMAGE: `3_designs_profiles.png`]**

---

## Slide 5: Performance Comparison
**[IMAGE: `3_designs_performance.png`]**

All 3 designs PASS every ASCE requirement.

---

## Slide 6: Radar Analysis
**[IMAGE: `3_designs_radar.png`]**

Design A excels on weight and maneuverability.
Design C excels on stability and freeboard.

---

## Slide 7: 3D Visualization
**[IMAGE: `3d_hull_design_A.png`]**

Four views: Isometric, Front, Side, Top

---

## Slide 8: Recommendation — Design A
| Metric | Value | vs. Requirement |
|--------|-------|-----------------|
| Weight | 174 lbs | 28% under target |
| Freeboard | 11.0" | 83% over minimum |
| GM | 9.5" | 58% over minimum |
| Safety Factor | 104 | 52× over minimum |

**[IMAGE: `design_A_complete_suite.png`]**

---

## Slide 9: Construction Plan
**6-Phase Build Sequence:**
1. Mold fabrication (EPS foam)
2. PVA mesh placement
3. Concrete application (3-layer, 0.5" total)
4. 7-day moist cure
5. Demolding (6-person team)
6. Finishing and graphics

**Estimated Cost: $580** (incl. 15% contingency)

**[IMAGE: `construction_sequence.png`]**

---

## Slide 10: Timeline
| Milestone | Date |
|-----------|------|
| Mix design finalized | Feb 15, 2026 |
| Mold construction complete | Mar 1, 2026 |
| Concrete placement | Apr 1, 2026 |
| Curing complete | Apr 8, 2026 |
| Finishing & graphics | Apr 12, 2026 |
| Competition prep | Apr 15, 2026 |

---

## Slide 11: Budget
| Item | Cost |
|------|------|
| Concrete materials | $32 |
| PVA reinforcement | $87 |
| Mold materials | $350 |
| Finishing | $75 |
| Contingency (15%) | $75 |
| **Total** | **$580** |

---

## Slide 12: Q&A
**Thank you!**

Repository: `github.com/Miles0sage/concrete-canoe-project2026`
Dashboard: Run `streamlit run dashboard/app.py`

*Questions?*
