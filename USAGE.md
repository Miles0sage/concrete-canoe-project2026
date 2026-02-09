# Usage Guide

## Running Calculations

### Single Hull Analysis
```bash
python3 calculations/concrete_canoe_calculator.py
```

### 3-Design Comparison (with visualizations)
```bash
python3 scripts/generate_3_best_designs.py
```
Outputs: 5 PNG figures, CSV data, markdown report.

### Individual Design Reports
```bash
python3 scripts/generate_detailed_design_reports.py
```
Outputs: Complete analysis for each design (A, B, C) with 5-subplot figures.

### 3D Visualizations
```bash
python3 scripts/generate_3d_visualizations.py
```
Outputs: 4-view 3D renderings for each design + comparison overlay.

### Uncertainty Analysis
```bash
python3 scripts/uncertainty_analysis.py
```
Outputs: Monte Carlo distributions, tornado diagrams, risk report.

### Missing ASCE Diagrams
```bash
python3 scripts/generate_missing_diagrams.py
```
Outputs: Lines plan, construction sequence, ergonomics, transport, racing.

## Modifying Designs

Edit the `DESIGNS` list in `scripts/generate_3_best_designs.py`:

```python
DesignSpec(
    name="Design D",
    label="Custom",
    color="#9C27B0",
    length_in=200,    # Change dimensions here
    beam_in=33,
    depth_in=17,
    thickness_in=0.5,
    description="My custom design",
)
```

Then re-run the script.

## Interactive Dashboard

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

Adjust sliders to explore designs interactively.

## Exporting Data

All scripts automatically export:
- CSV files to `data/`
- PNG figures to `reports/figures/`
- Markdown reports to `reports/`
