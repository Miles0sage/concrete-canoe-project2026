# Installation Guide

## System Requirements

- Python 3.10+
- pip (package manager)
- Git
- 500 MB free disk space

## Setup

```bash
# 1. Clone repository
git clone https://github.com/Miles0sage/concrete-canoe-project2026.git
cd concrete-canoe-project2026

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Install core dependencies
pip install -r requirements.txt

# 4. Verify installation
python3 calculations/concrete_canoe_calculator.py
```

## Optional: Dashboard Dependencies

```bash
pip install streamlit plotly pandas
```

## Optional: Testing Dependencies

```bash
pip install pytest pytest-cov
pytest tests/ -v
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: matplotlib` | `pip install matplotlib numpy` |
| `No module named 'calculations'` | Run from project root directory |
| Figures not saving | Check `reports/figures/` directory exists |
| `venv not found` | `python3 -m venv venv` then activate |
