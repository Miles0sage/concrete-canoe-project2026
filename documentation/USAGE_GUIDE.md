# NAU Concrete Canoe 2026 – Usage Guide

## Setup (MacBook & VPS)

### 1. Clone and Install

```bash
cd ~/nau-canoe-2026  # or your project path
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

### 2. Run Hull Analysis

```bash
# Single analysis (Canoe 1 default)
python3 calculations/concrete_canoe_calculator.py

# Compare all 3 variants, save CSV
python3 scripts/run_hull_analysis.py
```

### 3. ASCE Compliance Check

```bash
# Default values
python3 scripts/asce_compliance_checker.py

# Custom: cement_ratio portland_lime% lime% poa%
python3 scripts/asce_compliance_checker.py 0.35 35 3 42
```

### 4. Batch Sheets

```bash
python3 scripts/generate_batch_sheets.py          # Batch #1
python3 scripts/generate_batch_sheets.py 5        # Batch #5
```

## File Locations

- **Calculations:** `calculations/concrete_canoe_calculator.py`
- **Comparison results:** `data/test_results/hull_comparison_YYYYMMDD.csv`
- **Compliance reports:** `data/compliance/compliance_report_YYYYMMDD.json`
- **Batch sheets:** `reports/batch_sheets/`
- **Spreadsheets:** `data/spreadsheets/`

## VPS Usage (Terminal-Only, GPU/Qwen)

Same commands work on VPS. No GUI required.

### Run Analysis

```bash
git pull
source venv/bin/activate
python3 calculations/concrete_canoe_calculator.py
python3 scripts/run_hull_analysis.py
```

### Visualize Data (Terminal-Only VPS)

VPS has no display. Generate an HTML report, then download to your Mac:

```bash
# On VPS:
python3 scripts/generate_visualization.py
```

**On your Mac** (download and view):

```bash
scp user@VPS_IP:~/nau-canoe-2026/reports/figures/report.html ~/Desktop/
open ~/Desktop/report.html
```

The report opens in your browser with charts (freeboard, GM, trade-offs).

### Dimension Decision Workflow

See [DIMENSION_DECISION_WORKFLOW.md](DIMENSION_DECISION_WORKFLOW.md) for step-by-step to finalize hull dimensions.

## Excel Verification

1. Open `data/spreadsheets/mixture_design_compliance_2026.xlsx` and `reinforcement_poa_calculations_2026.xlsx`
2. Compare your Excel freeboard, GM, and structural results to Python output
3. Update `scripts/asce_compliance_checker.py` input from mix design sheet if needed
