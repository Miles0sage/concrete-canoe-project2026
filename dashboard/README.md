# NAU Concrete Canoe 2026 — Interactive Dashboard

Real-time hull design explorer with ASCE compliance checking.

## Quick Start

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`.

## Features

- **Sliders** for length, beam, depth, thickness, density, paddlers
- **Real-time** weight, freeboard, GM, safety factor calculations
- **Pass/Fail** indicators for ASCE compliance
- **3D hull preview** (interactive Plotly)
- **Radar chart** comparing your design to 3 baselines
- **CSV export** of current design parameters

## Deployment

To deploy on Streamlit Cloud:
1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Select `dashboard/app.py` as the main file
4. Deploy
