# NAU ASCE Concrete Canoe 2026 – Hull Design Plan

**Version:** 1.0  
**Date:** February 2026  
**Team:** Northern Arizona University – Miles (PM/Mix), Tevion (Finance), Dr. Mark Lamer (Advisor)

---

## 1. Executive Summary

- **Competition:** ASCE Intermountain Southwest Student Symposium, April 16–18, 2026  
- **Target Hull:** 18' × 30" × 18", ~276 lbs  
- **Design Phase:** Dimension finalization and hydrostatic analysis  
- **Tools:** Python calculator, Excel verification, CAD-ready geometry  

---

## 2. Hull Geometry Options

| Variant | Length | Beam | Depth | Weight (lbs) | Use Case |
|--------|--------|------|-------|--------------|----------|
| Canoe 1 | 18' | 30" | 18" | 276 | Primary design |
| Canoe 2 | 18' | 36" | 18" | 300 | High stability |
| Canoe 3 | 16' | 42" | 18" | 320 | Sprint / stability |

---

## 3. Hydrostatic Design Targets

- **Minimum freeboard:** 4–6 in (ASCE 2026 guidance)  
- **Metacentric height (GM):** > 0.5 in for adequate stability  
- **Draft:** Minimized for speed while meeting freeboard  

---

## 4. Structural Considerations

- **Shell thickness:** ~0.5 in  
- **Flexural strength:** ≥ 1500 psi (from mix design)  
- **Safety factor:** ≥ 1.5 on bending  

---

## 5. Analysis Workflow

1. Run `calculations/concrete_canoe_calculator.py` for single-hull analysis  
2. Run `scripts/run_hull_analysis.py` for three-variant comparison  
3. Compare Python results to Excel (`data/spreadsheets/`)  
4. Finalize dimensions for Op 4.6 presentation  

---

## 6. References

- ASCE 2026 Concrete Canoe RFP  
- 2019 NAU VolCanoe (219" × 33" × 16", 300 lbs) for validation  
- Hull_Design_Evaluation_Action_Plan.docx  
