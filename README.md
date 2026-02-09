# NAU ASCE Concrete Canoe 2026

**Computational Hull Optimization & Design Analysis**
Northern Arizona University — ASCE Student Chapter

[![Tests](https://img.shields.io/badge/tests-60%20passed-brightgreen)](#testing)
[![Coverage](https://img.shields.io/badge/coverage-47%25-yellow)](#testing)
[![Designs](https://img.shields.io/badge/designs-3%20PASS-brightgreen)](#designs)
[![Monte Carlo](https://img.shields.io/badge/MC%20pass%20rate-100%25-brightgreen)](#uncertainty-analysis)

## Project Overview

Three optimized hull designs for the 2026 ASCE National Concrete Canoe Competition, all verified to pass every ASCE requirement:

| Design | Dimensions | Weight | Freeboard | GM | Safety Factor | Status |
|--------|-----------|--------|-----------|-----|---------------|--------|
| **A (Optimal)** | 192" x 32" x 17" | 174 lbs | 11.0" | 9.5" | 104 | PASS |
| B (Conservative) | 196" x 34" x 18" | 188 lbs | 12.3" | 11.7" | 120 | PASS |
| C (Traditional) | 216" x 36" x 18" | 214 lbs | 13.0" | 16.0" | 112 | PASS |

**Recommended: Design A** — lightest at 174 lbs (28% under 237 lb target).

## Quick Start

```bash
# Clone and setup
git clone https://github.com/Miles0sage/concrete-canoe-project2026.git
cd concrete-canoe-project2026
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run hull analysis
python3 calculations/concrete_canoe_calculator.py

# Generate all 3 design comparisons with visualizations
python3 scripts/generate_3_best_designs.py

# Run tests
pip install pytest pytest-cov
pytest tests/ -v

# Launch interactive dashboard
pip install streamlit plotly pandas
streamlit run dashboard/app.py
```

## Repository Structure

```
concrete-canoe-project2026/
├── calculations/           # Core hull analysis engine
│   └── concrete_canoe_calculator.py
├── scripts/                # Analysis & visualization generators
│   ├── generate_3_best_designs.py        # 3-design comparison
│   ├── generate_detailed_design_reports.py # Individual design reports
│   ├── generate_3d_visualizations.py     # 3D hull renderings
│   ├── uncertainty_analysis.py           # Monte Carlo + sensitivity
│   └── generate_missing_diagrams.py      # ASCE competition diagrams
├── tests/                  # Pytest test suite (60 tests)
│   ├── test_hull_geometry.py
│   ├── test_hydrostatic_analysis.py
│   ├── test_stability_analysis.py
│   ├── test_structural_analysis.py
│   └── test_integration.py
├── dashboard/              # Interactive Streamlit web app
│   └── app.py
├── reports/                # Engineering analysis reports
│   ├── figures/            # 20+ publication-quality figures (300 DPI)
│   ├── design_A_complete_analysis.md
│   ├── design_B_complete_analysis.md
│   ├── design_C_complete_analysis.md
│   ├── uncertainty_analysis_report.md
│   └── 3_designs_comparison_report.md
├── data/                   # CSV exports and analysis data
├── design/                 # SolidWorks specs and DXF coordinates
├── documentation/          # Video script, storyboard, presentations
├── material-sourcing/      # Supplier contacts and pricing
├── construction/           # Build process documentation
└── testing/                # Physical test data
```

## Visualizations

### Hull Profiles & Cross-Sections
- `reports/figures/3_designs_profiles.png` — Side views with rocker curve
- `reports/figures/3_designs_cross_sections.png` — V-bottom midship sections
- `reports/figures/hull_lines_plan.png` — Traditional naval architecture lines plan

### 3D Renderings
- `reports/figures/3d_hull_design_A.png` — 4-view 3D rendering (isometric, front, side, top)
- `reports/figures/3d_comparison_all_designs.png` — All 3 hulls overlaid

### Performance Analysis
- `reports/figures/3_designs_performance.png` — Bar charts with requirement lines
- `reports/figures/3_designs_radar.png` — 5-axis radar comparison
- `reports/figures/3_designs_summary_table.png` — Visual comparison table

### Uncertainty & Sensitivity
- `reports/figures/uncertainty_distributions.png` — Monte Carlo histograms
- `reports/figures/sensitivity_tornado.png` — Parameter sensitivity tornado

### Competition Diagrams
- `reports/figures/construction_sequence.png` — 6-step build process
- `reports/figures/paddler_ergonomics.png` — Seating layout and clearances
- `reports/figures/racing_strategy.png` — Sprint and slalom course strategy

## Testing

```bash
pytest tests/ -v --cov=calculations
```

60 tests across 5 test modules:
- `test_hull_geometry.py` — HullGeometry class and conversions (7 tests)
- `test_hydrostatic_analysis.py` — Displacement, draft, freeboard (13 tests)
- `test_stability_analysis.py` — Metacentric height GM (7 tests)
- `test_structural_analysis.py` — Bending, section modulus, safety factor (15 tests)
- `test_integration.py` — End-to-end pipeline for all 3 designs (18 tests)

## Uncertainty Analysis

Monte Carlo simulation (1,000 iterations) varying:
- Concrete density: 60 +/- 3 PCF
- Wall thickness: 0.5 +/- 0.05"
- Flexural strength: 1500 +/- 150 psi
- Paddler weight: 175 +/- 15 lbs

**Result: 100% pass rate** — Design A passes under all tested uncertainty conditions.

## Interactive Dashboard

```bash
cd dashboard && pip install -r requirements.txt && streamlit run app.py
```

Features:
- Real-time hull parameter adjustment via sliders
- Live weight, freeboard, GM, safety factor calculations
- 3D hull preview (Plotly)
- Radar chart comparison against baseline designs
- CSV export

## Team

**NAU ASCE Student Chapter — Concrete Canoe Team 2026**

## Contact

Repository: [github.com/Miles0sage/concrete-canoe-project2026](https://github.com/Miles0sage/concrete-canoe-project2026)

---
*Last Updated: February 2026*
