#!/usr/bin/env python3
"""
NAU ASCE Concrete Canoe 2026 — Interactive Design Dashboard
Run: streamlit run dashboard/app.py
"""

import sys
import math
import csv
import io
from pathlib import Path

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from calculations.concrete_canoe_calculator import (
    WATER_DENSITY_LB_PER_FT3,
    displacement_volume,
    metacentric_height_approx,
    bending_moment_uniform_load,
    section_modulus_rectangular,
    section_modulus_thin_shell,
    bending_stress_psi,
    safety_factor as calc_safety_factor,
)

# ── Page config ──
st.set_page_config(
    page_title="NAU Concrete Canoe 2026",
    page_icon="🛶",
    layout="wide",
)

# ── Constants ──
CWP = 0.65
FLEXURAL = 1500
CONCRETE_DENSITY = 60.0
MIN_FB = 6.0
MIN_GM = 6.0
MIN_SF = 2.0
TARGET_WT = 237.0

# ── Baseline designs for comparison ──
BASELINES = {
    "Design A (Optimal)": {"L": 192, "B": 32, "D": 17, "t": 0.5},
    "Design B (Conservative)": {"L": 196, "B": 34, "D": 18, "t": 0.5},
    "Design C (Traditional)": {"L": 216, "B": 36, "D": 18, "t": 0.5},
}


def shell_weight(L, B, D, t, density=CONCRETE_DENSITY):
    Lf, Bf, Df, tf = L/12, B/12, D/12, t/12
    bottom = (math.pi/4) * Lf * Bf
    sides = 2 * Lf * Df * 0.70
    return (bottom + sides) * tf * density


def full_calc(L, B, D, t, n_paddlers, paddler_wt, density):
    sw = shell_weight(L, B, D, t, density)
    rw = sw * 0.05
    canoe_wt = sw + rw + 3.0
    crew = n_paddlers * paddler_wt
    loaded = canoe_wt + crew

    Lf, Bf, Df = L/12, B/12, D/12
    disp = loaded / WATER_DENSITY_LB_PER_FT3
    wp = Lf * Bf * CWP
    draft_ft = disp / wp if wp > 0 else 0
    fb_in = max(0, (Df - draft_ft) * 12)

    KB = draft_ft / 2
    BM = Bf**2 / (12 * draft_ft) if draft_ft > 0 else 0
    KG = Df * 0.45
    gm_in = (KB + BM - KG) * 12

    w_per_ft = loaded / Lf if Lf > 0 else 0
    M_max = w_per_ft * Lf**2 / 8
    S = section_modulus_thin_shell(B, D, t)
    sigma = (M_max * 12) / S if S > 0 else 0
    sf = FLEXURAL / sigma if sigma > 0 else 0

    return {
        "canoe_wt": canoe_wt, "loaded_wt": loaded,
        "draft_in": draft_ft * 12, "fb_in": fb_in,
        "gm_in": gm_in, "sf": sf, "sigma_psi": sigma,
        "M_max": M_max,
    }


# ════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════
st.sidebar.title("🛶 Hull Parameters")
st.sidebar.markdown("Adjust dimensions to explore designs in real time.")

length = st.sidebar.slider("Length (inches)", 168, 240, 192, 2)
beam = st.sidebar.slider("Beam (inches)", 26, 42, 32, 1)
depth = st.sidebar.slider("Depth (inches)", 12, 22, 17, 1)
thickness = st.sidebar.slider("Thickness (inches)", 0.30, 0.75, 0.50, 0.05)
density = st.sidebar.slider("Concrete Density (PCF)", 50, 70, 60, 1)
n_paddlers = st.sidebar.selectbox("Paddlers", [2, 3, 4], index=2)
paddler_wt = st.sidebar.slider("Paddler Weight (lbs)", 130, 220, 175, 5)

r = full_calc(length, beam, depth, thickness, n_paddlers, paddler_wt, density)

# ════════════════════════════════════════════
# MAIN PANEL
# ════════════════════════════════════════════
st.title("NAU ASCE Concrete Canoe 2026 — Design Dashboard")
st.markdown(f"**Current Design:** {length}\" × {beam}\" × {depth}\" (t={thickness}\")")

# ── KPI row ──
cols = st.columns(5)
with cols[0]:
    delta = r["canoe_wt"] - TARGET_WT
    st.metric("Canoe Weight", f'{r["canoe_wt"]:.1f} lbs',
              f'{delta:+.1f} vs {TARGET_WT}',
              delta_color="inverse")
with cols[1]:
    st.metric("Freeboard", f'{r["fb_in"]:.1f}"',
              "PASS ✓" if r["fb_in"] >= MIN_FB else "FAIL ✗",
              delta_color="normal" if r["fb_in"] >= MIN_FB else "inverse")
with cols[2]:
    st.metric("GM (Stability)", f'{r["gm_in"]:.1f}"',
              "PASS ✓" if r["gm_in"] >= MIN_GM else "FAIL ✗",
              delta_color="normal" if r["gm_in"] >= MIN_GM else "inverse")
with cols[3]:
    st.metric("Safety Factor", f'{r["sf"]:.1f}',
              "PASS ✓" if r["sf"] >= MIN_SF else "FAIL ✗",
              delta_color="normal" if r["sf"] >= MIN_SF else "inverse")
with cols[4]:
    all_pass = r["fb_in"] >= MIN_FB and r["gm_in"] >= MIN_GM and r["sf"] >= MIN_SF
    st.metric("Overall", "ALL PASS ✓" if all_pass else "FAIL ✗", "ASCE Compliant" if all_pass else "Non-compliant")

st.divider()

# ── Two-column layout ──
left, right = st.columns(2)

# ── Radar chart ──
with left:
    st.subheader("Performance Radar")

    # Normalize metrics (higher = better, 0-1)
    w_norm = max(0, min(1, 1 - (r["canoe_wt"] - 150) / 100))
    fb_norm = max(0, min(1, r["fb_in"] / 16))
    gm_norm = max(0, min(1, r["gm_in"] / 20))
    sf_norm = max(0, min(1, r["sf"] / 150))
    man_norm = max(0, min(1, 1 - (length/beam - 4) / 4))

    categories = ["Weight", "Freeboard", "Stability", "Safety", "Maneuverability"]
    values = [w_norm, fb_norm, gm_norm, sf_norm, man_norm]

    radar = go.Figure()
    radar.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself", fillcolor="rgba(33, 150, 243, 0.2)",
        line=dict(color="#2196F3", width=2.5),
        name="Your Design",
    ))

    # Add baseline designs
    colors = {"Design A (Optimal)": "#FF9800", "Design B (Conservative)": "#4CAF50",
              "Design C (Traditional)": "#9C27B0"}
    for bname, bd in BASELINES.items():
        br = full_calc(bd["L"], bd["B"], bd["D"], bd["t"], n_paddlers, paddler_wt, density)
        bvals = [
            max(0, min(1, 1 - (br["canoe_wt"] - 150) / 100)),
            max(0, min(1, br["fb_in"] / 16)),
            max(0, min(1, br["gm_in"] / 20)),
            max(0, min(1, br["sf"] / 150)),
            max(0, min(1, 1 - (bd["L"]/bd["B"] - 4) / 4)),
        ]
        radar.add_trace(go.Scatterpolar(
            r=bvals + [bvals[0]],
            theta=categories + [categories[0]],
            line=dict(color=colors[bname], width=1.5, dash="dash"),
            name=bname.split(" (")[0],
        ))

    radar.update_layout(
        polar=dict(radialaxis=dict(range=[0, 1], showticklabels=False)),
        showlegend=True, height=400, margin=dict(t=30, b=30),
    )
    st.plotly_chart(radar, use_container_width=True)

# ── 3D hull preview ──
with right:
    st.subheader("3D Hull Preview")
    n_long, n_circ = 50, 25
    u = np.linspace(0, 1, n_long)
    v = np.linspace(0, 1, n_circ)
    X, Y, Z = np.zeros((n_long, n_circ)), np.zeros((n_long, n_circ)), np.zeros((n_long, n_circ))
    for i, ui in enumerate(u):
        taper = max(1.0 - (2*ui-1)**4, 0.02)
        hb = (beam/2) * taper
        dd = depth * 0.20 * taper
        for j, vj in enumerate(v):
            X[i,j] = ui * length
            if vj <= 0.3:
                frac = vj/0.3
                Y[i,j] = hb * 0.8 * frac
                Z[i,j] = -dd * (1-frac)
            else:
                frac = (vj-0.3)/0.7
                Y[i,j] = hb * (0.8 + 0.2*frac)
                Z[i,j] = depth * frac

    hull3d = go.Figure()
    hull3d.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale="Blues", opacity=0.7, showscale=False))
    hull3d.add_trace(go.Surface(x=X, y=-Y, z=Z, colorscale="Blues", opacity=0.7, showscale=False))
    hull3d.update_layout(
        scene=dict(
            xaxis_title="Length (in)", yaxis_title="Beam (in)", zaxis_title="Depth (in)",
            aspectratio=dict(x=2, y=0.5, z=0.3),
        ),
        height=400, margin=dict(t=10, b=10, l=10, r=10),
    )
    st.plotly_chart(hull3d, use_container_width=True)

# ── Comparison table ──
st.subheader("Comparison with Baseline Designs")
rows = []
for bname, bd in BASELINES.items():
    br = full_calc(bd["L"], bd["B"], bd["D"], bd["t"], n_paddlers, paddler_wt, density)
    rows.append({
        "Design": bname,
        "Dimensions": f'{bd["L"]}" × {bd["B"]}" × {bd["D"]}"',
        "Weight (lbs)": f'{br["canoe_wt"]:.1f}',
        'Freeboard (in)': f'{br["fb_in"]:.1f}',
        'GM (in)': f'{br["gm_in"]:.1f}',
        'Safety Factor': f'{br["sf"]:.1f}',
        'Status': "PASS ✓" if (br["fb_in"]>=MIN_FB and br["gm_in"]>=MIN_GM and br["sf"]>=MIN_SF) else "FAIL ✗",
    })
rows.append({
    "Design": "➤ Your Design",
    "Dimensions": f'{length}" × {beam}" × {depth}"',
    "Weight (lbs)": f'{r["canoe_wt"]:.1f}',
    'Freeboard (in)': f'{r["fb_in"]:.1f}',
    'GM (in)': f'{r["gm_in"]:.1f}',
    'Safety Factor': f'{r["sf"]:.1f}',
    'Status': "PASS ✓" if all_pass else "FAIL ✗",
})
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ── Export ──
st.divider()
st.subheader("Export")
col1, col2 = st.columns(2)
with col1:
    csv_buf = io.StringIO()
    writer = csv.writer(csv_buf)
    writer.writerow(["parameter", "value", "unit"])
    writer.writerow(["length", length, "in"])
    writer.writerow(["beam", beam, "in"])
    writer.writerow(["depth", depth, "in"])
    writer.writerow(["thickness", thickness, "in"])
    writer.writerow(["canoe_weight", f'{r["canoe_wt"]:.2f}', "lbs"])
    writer.writerow(["freeboard", f'{r["fb_in"]:.2f}', "in"])
    writer.writerow(["gm", f'{r["gm_in"]:.2f}', "in"])
    writer.writerow(["safety_factor", f'{r["sf"]:.4f}', ""])
    st.download_button("📥 Download CSV", csv_buf.getvalue(),
                       file_name="canoe_design_export.csv", mime="text/csv")
with col2:
    st.markdown("Run locally: `cd dashboard && pip install -r requirements.txt && streamlit run app.py`")

st.caption("NAU ASCE Concrete Canoe 2026 — Interactive Design Dashboard")
