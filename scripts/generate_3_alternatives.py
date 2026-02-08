#!/usr/bin/env python3
"""
NAU ASCE Concrete Canoe 2026 — 3 Alternative Hull Designs
Compares Optimal (lightest), Conservative (extra margin), and Long/Stable designs.
Uses the same hydrostatic model as the main report generator.
"""

import sys
import math
import csv
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# ─── Constants ────────────────────────────────────────────────────────
WATER_DENSITY_PCF = 62.4
CONCRETE_DENSITY_PCF = 60.0
FLEXURAL_STRENGTH_PSI = 1500.0
THICKNESS_IN = 0.5
NUM_PADDLERS = 4
PADDLER_WEIGHT_LBS = 175.0
CW = 0.72       # waterplane area coefficient
CI = 0.65       # waterplane inertia coefficient
TAPER = 0.87    # canoe shape taper factor

REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
DATA_DIR = PROJECT_ROOT / "data"
DESIGN_DIR = PROJECT_ROOT / "design"

for d in [FIGURES_DIR, DATA_DIR, DESIGN_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─── 3 Designs ────────────────────────────────────────────────────────
DESIGNS = [
    {
        "id": "A", "name": "Design A — Optimal (Lightest)",
        "desc": "Minimum weight, meets all requirements with adequate margin",
        "L": 192, "B": 32, "D": 17,
    },
    {
        "id": "B", "name": "Design B — Conservative (Extra Margin)",
        "desc": "Wider beam & deeper hull for generous freeboard and GM margin",
        "L": 196, "B": 34, "D": 18,
    },
    {
        "id": "C", "name": "Design C — Long & Stable (Speed)",
        "desc": "Longer waterline for higher hull speed; wider beam for stability",
        "L": 216, "B": 36, "D": 18,
    },
]

# ─── Analysis Engine ──────────────────────────────────────────────────

def analyze_design(d):
    """Full hydrostatic/stability/structural analysis for one design."""
    L, B, D, t = d["L"], d["B"], d["D"], THICKNESS_IN
    L_ft, B_ft, D_ft = L / 12.0, B / 12.0, D / 12.0

    # Weight
    SA = 2 * (L * D + B * D) + L * B
    shell_vol_ft3 = SA * t * TAPER / 1728.0
    concrete_wt = shell_vol_ft3 * CONCRETE_DENSITY_PCF
    total_hull_wt = concrete_wt + 17.0  # reinforcement + finish + hardware

    # Hydrostatics (loaded)
    crew_wt = NUM_PADDLERS * PADDLER_WEIGHT_LBS
    total_wt = total_hull_wt + crew_wt
    disp_ft3 = total_wt / WATER_DENSITY_PCF
    Aw_ft2 = CW * L_ft * B_ft
    draft_ft = disp_ft3 / Aw_ft2
    draft_in = draft_ft * 12
    fb_in = D - draft_in

    # Stability
    KB_ft = draft_ft / 2
    Iw_ft4 = CI * L_ft * B_ft**3 / 12.0
    BM_ft = Iw_ft4 / disp_ft3 if disp_ft3 > 0 else 0
    hull_KG_ft = D_ft * 0.38
    paddler_KG_ft = 10.0 / 12.0
    KG_ft = (total_hull_wt * hull_KG_ft + crew_wt * paddler_KG_ft) / total_wt
    GM_ft = KB_ft + BM_ft - KG_ft
    GM_in = GM_ft * 12

    # Structural
    b_o, h_o = B, D
    b_i, h_i = B - 2 * t, D - 2 * t
    Ix = (b_o * h_o**3 - b_i * h_i**3) / 12.0
    Sx = Ix / (h_o / 2.0)
    w_self = total_hull_wt / L_ft
    M_self = w_self * L_ft**2 / 8.0
    # Paddler moments
    M_p = 0
    for s in [0.25, 0.40, 0.60, 0.75]:
        a, b = s * L_ft, (1 - s) * L_ft
        M_p += PADDLER_WEIGHT_LBS * a * b / L_ft
    M_max = M_self + M_p * 0.50
    sigma = (M_max * 12) / Sx if Sx > 0 else 0
    SF = FLEXURAL_STRENGTH_PSI / sigma if sigma > 0 else 999

    # Hull speed (Froude)
    hull_speed_kts = 1.34 * math.sqrt(L_ft)

    return {
        "id": d["id"], "name": d["name"], "desc": d["desc"],
        "L": L, "B": B, "D": D,
        "hull_wt": round(total_hull_wt, 1),
        "total_wt": round(total_wt, 1),
        "draft_in": round(draft_in, 2),
        "fb_in": round(fb_in, 2),
        "GM_in": round(GM_in, 2),
        "SF": round(SF, 2),
        "Ix": round(Ix, 1),
        "Sx": round(Sx, 1),
        "M_max": round(M_max, 1),
        "sigma": round(sigma, 1),
        "hull_speed": round(hull_speed_kts, 2),
        "Aw_ft2": round(Aw_ft2, 2),
        "disp_ft3": round(disp_ft3, 3),
        "KB_in": round(KB_ft * 12, 2),
        "BM_in": round(BM_ft * 12, 2),
        "KG_in": round(KG_ft * 12, 2),
        "fb_pass": fb_in >= 6.0,
        "gm_pass": GM_in >= 6.0,
        "sf_pass": SF >= 2.0,
        "all_pass": fb_in >= 6.0 and GM_in >= 6.0 and SF >= 2.0,
    }


# ─── Run Analysis ────────────────────────────────────────────────────

def run_all():
    results = [analyze_design(d) for d in DESIGNS]

    # Console output
    print("=" * 80)
    print("  NAU ASCE Concrete Canoe 2026 — 3 Alternative Hull Designs")
    print("=" * 80)
    print()
    hdr = f"{'Design':<40} {'L×B×D':<14} {'Wt(lb)':<9} {'FB(in)':<8} {'GM(in)':<8} {'SF':<7} {'Status'}"
    print(hdr)
    print("-" * 95)
    for r in results:
        dims = f"{r['L']}×{r['B']}×{r['D']}"
        st = "✓ ALL PASS" if r["all_pass"] else "✗ FAIL"
        print(f"  {r['name']:<38} {dims:<14} {r['hull_wt']:<9} {r['fb_in']:<8} {r['GM_in']:<8} {r['SF']:<7} {st}")

    print()
    print("-" * 95)
    print("  Detailed Breakdown:")
    for r in results:
        print(f"\n  [{r['id']}] {r['name']}")
        print(f"      {r['desc']}")
        print(f"      Dimensions:   {r['L']}\" × {r['B']}\" × {r['D']}\"")
        print(f"      Hull weight:  {r['hull_wt']} lbs")
        print(f"      Loaded disp:  {r['total_wt']} lbs")
        print(f"      Draft:        {r['draft_in']}\"")
        print(f"      Freeboard:    {r['fb_in']}\"  (≥6\")  {'✓' if r['fb_pass'] else '✗'}")
        print(f"      GM:           {r['GM_in']}\"  (≥6\")  {'✓' if r['gm_pass'] else '✗'}")
        print(f"      Safety factor:{r['SF']}     (≥2.0) {'✓' if r['sf_pass'] else '✗'}")
        print(f"      Hull speed:   {r['hull_speed']} kts")

    # Save CSV
    csv_path = DATA_DIR / "3_alternative_designs.csv"
    fields = ["id", "name", "L", "B", "D", "hull_wt", "total_wt", "draft_in",
              "fb_in", "GM_in", "SF", "hull_speed", "fb_pass", "gm_pass", "sf_pass", "all_pass"]
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(results)
    print(f"\n  ✓ Saved: {csv_path.relative_to(PROJECT_ROOT)}")

    return results


# ─── Visualization: Side-by-Side Hull Profiles ───────────────────────

def plot_3_designs_profiles(results):
    """3 hull profiles at same scale, side by side."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    colors = ["#2196F3", "#4CAF50", "#FF9800"]

    max_L = max(r["L"] for r in results)

    for ax, r, clr in zip(axes, results, colors):
        L, D = r["L"], r["D"]
        x = np.linspace(0, L, 300)
        sheer = D + 1.2 * np.cos(np.pi * (x / L - 0.5))
        keel = 0.8 * np.sin(np.pi * x / L)
        ax.fill_between(x, keel, sheer, alpha=0.25, color=clr)
        ax.plot(x, sheer, color=clr, lw=2)
        ax.plot(x, keel, color=clr, lw=2)
        # Waterline
        ax.axhline(y=r["draft_in"], color="deepskyblue", ls="--", lw=1.5)
        # Dimension annotations
        ax.annotate("", xy=(0, -2.5), xytext=(L, -2.5),
                     arrowprops=dict(arrowstyle="<->", color="black", lw=1))
        ax.text(L / 2, -3.5, f'{L}"', ha="center", fontsize=10, fontweight="bold")
        ax.annotate("", xy=(L + 3, 0), xytext=(L + 3, D),
                     arrowprops=dict(arrowstyle="<->", color="black", lw=1))
        ax.text(L + 8, D / 2, f'{D}"', ha="left", va="center", fontsize=10, fontweight="bold")
        # Freeboard arrow
        ax.annotate("", xy=(L * 0.6, r["draft_in"]), xytext=(L * 0.6, D),
                     arrowprops=dict(arrowstyle="<->", color="green", lw=1.5))
        ax.text(L * 0.6 + 3, (r["draft_in"] + D) / 2, f'FB={r["fb_in"]:.1f}"',
                color="green", fontsize=9, va="center")

        status = "✓ ALL PASS" if r["all_pass"] else "✗ FAIL"
        ax.set_title(f'{r["name"]}\n{r["hull_wt"]} lbs | GM={r["GM_in"]:.1f}" | SF={r["SF"]:.1f}\n{status}',
                     fontsize=10, fontweight="bold")
        ax.set_xlim(-5, max_L + 20)
        ax.set_ylim(-5, 25)
        ax.set_aspect("equal")
        ax.set_xlabel("Length (in)")
        ax.grid(True, alpha=0.2)
        if ax == axes[0]:
            ax.set_ylabel("Height (in)")

    fig.suptitle("NAU Concrete Canoe 2026 — 3 Alternative Hull Profiles", fontsize=14, fontweight="bold")
    fig.tight_layout()
    path = FIGURES_DIR / "3_designs_comparison.png"
    fig.savefig(path, dpi=600, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {path.relative_to(PROJECT_ROOT)} (600 DPI)")


# ─── Visualization: Comparison Charts ─────────────────────────────────

def plot_comparison_charts(results):
    """Bar charts + radar chart comparing all 3 designs."""
    fig = plt.figure(figsize=(18, 12))
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)

    names = [f"Design {r['id']}" for r in results]
    colors = ["#2196F3", "#4CAF50", "#FF9800"]

    # 1. Weight comparison
    ax1 = fig.add_subplot(gs[0, 0])
    vals = [r["hull_wt"] for r in results]
    bars = ax1.bar(names, vals, color=colors, alpha=0.8, edgecolor="black", lw=0.5)
    ax1.axhline(y=237, color="red", ls="--", lw=1.5, label="Target (237 lbs)")
    for bar, v in zip(bars, vals):
        ax1.text(bar.get_x() + bar.get_width() / 2, v + 3, f"{v:.0f}", ha="center", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Hull Weight (lbs)")
    ax1.set_title("Hull Weight", fontweight="bold")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.2, axis="y")

    # 2. Freeboard comparison
    ax2 = fig.add_subplot(gs[0, 1])
    vals = [r["fb_in"] for r in results]
    bars = ax2.bar(names, vals, color=colors, alpha=0.8, edgecolor="black", lw=0.5)
    ax2.axhline(y=6.0, color="red", ls="--", lw=1.5, label="Min (6.0 in)")
    for bar, v in zip(bars, vals):
        ax2.text(bar.get_x() + bar.get_width() / 2, v + 0.2, f"{v:.1f}", ha="center", fontsize=10, fontweight="bold")
    ax2.set_ylabel("Freeboard (in)")
    ax2.set_title("Freeboard", fontweight="bold")
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.2, axis="y")

    # 3. GM comparison
    ax3 = fig.add_subplot(gs[0, 2])
    vals = [r["GM_in"] for r in results]
    bars = ax3.bar(names, vals, color=colors, alpha=0.8, edgecolor="black", lw=0.5)
    ax3.axhline(y=6.0, color="red", ls="--", lw=1.5, label="Min (6.0 in)")
    for bar, v in zip(bars, vals):
        ax3.text(bar.get_x() + bar.get_width() / 2, v + 0.3, f"{v:.1f}", ha="center", fontsize=10, fontweight="bold")
    ax3.set_ylabel("GM (in)")
    ax3.set_title("Metacentric Height (GM)", fontweight="bold")
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.2, axis="y")

    # 4. Safety Factor comparison
    ax4 = fig.add_subplot(gs[1, 0])
    vals = [r["SF"] for r in results]
    bars = ax4.bar(names, vals, color=colors, alpha=0.8, edgecolor="black", lw=0.5)
    ax4.axhline(y=2.0, color="red", ls="--", lw=1.5, label="Min (2.0)")
    for bar, v in zip(bars, vals):
        ax4.text(bar.get_x() + bar.get_width() / 2, v + 0.5, f"{v:.1f}", ha="center", fontsize=10, fontweight="bold")
    ax4.set_ylabel("Safety Factor")
    ax4.set_title("Structural Safety Factor", fontweight="bold")
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.2, axis="y")

    # 5. Hull Speed comparison
    ax5 = fig.add_subplot(gs[1, 1])
    vals = [r["hull_speed"] for r in results]
    bars = ax5.bar(names, vals, color=colors, alpha=0.8, edgecolor="black", lw=0.5)
    for bar, v in zip(bars, vals):
        ax5.text(bar.get_x() + bar.get_width() / 2, v + 0.05, f"{v:.2f}", ha="center", fontsize=10, fontweight="bold")
    ax5.set_ylabel("Hull Speed (kts)")
    ax5.set_title("Theoretical Hull Speed", fontweight="bold")
    ax5.grid(True, alpha=0.2, axis="y")

    # 6. Radar chart — 5 metrics normalized
    ax6 = fig.add_subplot(gs[1, 2], polar=True)
    categories = ["Light\nWeight", "Freeboard", "Stability\n(GM)", "Strength\n(SF)", "Speed"]
    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    for r, clr in zip(results, colors):
        # Normalize: lower weight is better (invert), others higher is better
        max_wt = max(x["hull_wt"] for x in results)
        min_wt = min(x["hull_wt"] for x in results)
        wt_range = max_wt - min_wt if max_wt != min_wt else 1
        wt_score = 1.0 - (r["hull_wt"] - min_wt) / wt_range  # inverted
        fb_score = min(r["fb_in"] / 15.0, 1.0)
        gm_score = min(r["GM_in"] / 15.0, 1.0)
        sf_score = min(r["SF"] / 30.0, 1.0)
        spd_score = min(r["hull_speed"] / 6.5, 1.0)
        values = [wt_score, fb_score, gm_score, sf_score, spd_score]
        values += values[:1]
        ax6.plot(angles, values, "o-", lw=2, color=clr, label=f"Design {r['id']}", markersize=5)
        ax6.fill(angles, values, alpha=0.1, color=clr)

    ax6.set_xticks(angles[:-1])
    ax6.set_xticklabels(categories, fontsize=9)
    ax6.set_ylim(0, 1.1)
    ax6.set_title("Overall Performance\n(Normalized)", fontweight="bold", pad=20)
    ax6.legend(loc="lower right", fontsize=8, bbox_to_anchor=(1.3, -0.1))

    fig.suptitle("NAU Concrete Canoe 2026 — Design Comparison Dashboard", fontsize=15, fontweight="bold", y=1.01)
    path = FIGURES_DIR / "design_comparison_charts.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {path.relative_to(PROJECT_ROOT)}")


# ─── Cross-Section Visualization ──────────────────────────────────────

def plot_3_designs_cross_sections(results):
    """3×5 grid: each design at 5 stations + top view."""
    fig, axes = plt.subplots(3, 6, figsize=(22, 12))
    colors = ["#2196F3", "#4CAF50", "#FF9800"]
    stations = [0.0, 0.25, 0.50, 0.75, 1.0]
    sta_names = ["Bow\n0%", "Fwd Qtr\n25%", "Midship\n50%", "Aft Qtr\n75%", "Stern\n100%"]
    deadrise = 15  # degrees

    for row, (r, clr) in enumerate(zip(results, colors)):
        L, B, D = r["L"], r["B"], r["D"]
        # Cross-sections at 5 stations
        for col, (frac, sname) in enumerate(zip(stations, sta_names)):
            ax = axes[row][col]
            half_b = (B / 2.0) * math.sin(math.pi * max(frac, 0.01) * min(frac / 1.0, 0.99)) if 0 < frac < 1 else 0.5
            if frac == 0 or frac == 1:
                half_b = 1.0  # narrow at ends
            n = 40
            xh = np.linspace(0, half_b, n)
            yh = xh * math.tan(math.radians(deadrise))
            xf = np.concatenate([-xh[::-1], xh[1:]])
            yf = np.concatenate([yh[::-1], yh[1:]])
            xs = np.concatenate([[-half_b], xf, [half_b]])
            ys = np.concatenate([[D], yf, [D]])
            ax.fill(xs, ys, alpha=0.2, color=clr)
            ax.plot(xs, ys, color=clr, lw=2)
            ax.axhline(y=r["draft_in"], color="deepskyblue", ls="--", lw=1, alpha=0.6)
            ax.set_xlim(-B / 2 - 2, B / 2 + 2)
            ax.set_ylim(-1, D + 3)
            ax.set_aspect("equal")
            ax.grid(True, alpha=0.2)
            if row == 0:
                ax.set_title(sname, fontsize=9)
            if col == 0:
                ax.set_ylabel(f"Design {r['id']}\n({r['L']}×{r['B']}×{r['D']})", fontsize=9, fontweight="bold")

        # Top view (plan)
        ax = axes[row][5]
        x_plan = np.linspace(0, L, 200)
        half_beam = (B / 2) * np.sin(np.pi * x_plan / L)
        ax.fill_between(x_plan, -half_beam, half_beam, alpha=0.2, color=clr)
        ax.plot(x_plan, half_beam, color=clr, lw=2)
        ax.plot(x_plan, -half_beam, color=clr, lw=2)
        ax.set_title("Plan View" if row == 0 else "", fontsize=9)
        ax.set_xlim(-5, max(r2["L"] for r2 in results) + 5)
        ax.set_ylim(-22, 22)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.2)
        ax.set_xlabel("in" if row == 2 else "")

    fig.suptitle("Hull Cross-Sections & Plan Views — 3 Designs", fontsize=14, fontweight="bold")
    fig.tight_layout()
    path = FIGURES_DIR / "3_designs_visual_comparison.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {path.relative_to(PROJECT_ROOT)}")


# ─── DXF Coordinate Files ────────────────────────────────────────────

def generate_dxf_coords(results):
    """Generate station coordinate files for CNC cutting."""
    deadrise = 15
    for r in results:
        L, B, D = r["L"], r["B"], r["D"]
        spacing = 6.0
        num_sta = int(L / spacing) + 1
        lines = []
        lines.append(f"# NAU Concrete Canoe 2026 — Design {r['id']} CNC Coordinates")
        lines.append(f"# {r['name']}")
        lines.append(f"# Hull: {L}\" × {B}\" × {D}\", thickness {THICKNESS_IN}\"")
        lines.append(f"# Stations every {spacing}\" ({num_sta} stations)")
        lines.append(f"# Format: Station_Number, Position_in, X_coord, Y_coord")
        lines.append(f"# Cross-section: V-bottom, deadrise={deadrise}°, depth={D}\"")
        lines.append(f"# Origin: keel centerline at bottom")
        lines.append("")
        lines.append("Station, Pos(in), X(in), Y(in)")

        for i in range(num_sta):
            pos = i * spacing
            if pos > L:
                pos = L
            frac = pos / L
            half_b = (B / 2.0) * math.sin(math.pi * frac) if 0 < frac < 1 else 0.0
            # Generate outline points for this station
            n = 21  # points per half
            lines.append(f"# --- Station {i} at {pos:.0f}\" (beam={2*half_b:.1f}\") ---")
            if half_b < 0.1:
                lines.append(f"{i}, {pos:.1f}, 0.000, 0.000")
                continue
            for j in range(n):
                x = -half_b + j * (2 * half_b) / (n - 1)
                y_bottom = abs(x) * math.tan(math.radians(deadrise))
                lines.append(f"{i}, {pos:.1f}, {x:.3f}, {y_bottom:.3f}")
            # Side walls
            lines.append(f"{i}, {pos:.1f}, {half_b:.3f}, {D:.3f}")
            lines.append(f"{i}, {pos:.1f}, {-half_b:.3f}, {D:.3f}")
            if pos >= L:
                break

        path = DESIGN_DIR / f"dxf_coords_design_{r['id']}.txt"
        path.write_text("\n".join(lines))
        print(f"  ✓ {path.relative_to(PROJECT_ROOT)}")


# ─── SolidWorks Guides ───────────────────────────────────────────────

def generate_solidworks_guide(r):
    """Generate detailed SolidWorks step-by-step for one design."""
    L, B, D = r["L"], r["B"], r["D"]
    deadrise = 15

    # Calculate station coordinates
    station_data = []
    for frac, name in [(0.0, "Bow"), (0.25, "Forward Quarter"), (0.50, "Midship"),
                        (0.75, "Aft Quarter"), (1.0, "Stern")]:
        pos = frac * L
        half_b = (B / 2.0) * math.sin(math.pi * frac) if 0 < frac < 1 else 0.0
        keel_y = half_b * math.tan(math.radians(deadrise)) if half_b > 0 else 0
        station_data.append({
            "frac": frac, "name": name, "pos": pos,
            "half_b": half_b, "full_b": 2 * half_b, "keel_y": keel_y,
        })

    # Station coordinate tables
    station_sections = ""
    for sd in station_data:
        if sd["half_b"] < 0.1:
            station_sections += f"""
### Station at {sd['pos']:.0f}\" — {sd['name']}
- **Plane:** Offset {sd['pos']:.0f}\" from bow reference
- **Shape:** Point (hull converges to keel)
- **Coordinates:** (0, 0) — single point at keel

"""
        else:
            # Key points for the V-bottom cross-section
            hb = sd["half_b"]
            ky = sd["keel_y"]
            station_sections += f"""
### Station at {sd['pos']:.0f}\" — {sd['name']}
- **Plane:** Offset {sd['pos']:.0f}\" from bow reference
- **Beam at waterline:** {sd['full_b']:.1f}\"
- **Deadrise angle:** {deadrise}°

| Point | X (in) | Y (in) | Description |
|-------|-------:|-------:|-------------|
| 1 | {-hb:.2f} | {D:.2f} | Port gunwale |
| 2 | {-hb:.2f} | {ky:.2f} | Port chine |
| 3 | 0.00 | 0.00 | Keel (centerline) |
| 4 | {hb:.2f} | {ky:.2f} | Starboard chine |
| 5 | {hb:.2f} | {D:.2f} | Starboard gunwale |

**Sketch:** Connect points 1→2→3→4→5 with lines. Add fillets (R=0.5\") at chine points 2 and 4.

"""

    content = f"""# SolidWorks Build Guide — Design {r['id']}
## NAU ASCE Concrete Canoe 2026
*{r['name']}*
*Dimensions: {L}\" × {B}\" × {D}\", Shell: {THICKNESS_IN}\"*
*Target weight: {r['hull_wt']} lbs*

---

## Prerequisites
- SolidWorks 2020 or newer
- Units: IPS (Inch, Pound, Second)
- Estimated time: 2–3 hours

---

## Step 1: Create New Part & Set Units

1. **File → New → Part**
2. **Tools → Options → Document Properties → Units**
   - Unit system: **IPS** (inch, pound, second)
   - Length decimals: 3
3. Save as `CanoeHull_Design{r['id']}.SLDPRT`

> The part opens with Front, Top, and Right planes plus the Origin.

---

## Step 2: Create Reference Planes

You need 5 cross-section planes perpendicular to the hull length axis.
The hull lies along the **Top plane** with length in the X direction.

1. Select the **Front Plane**
2. **Insert → Reference Geometry → Plane**
3. Create offset planes:

| Plane Name | Offset from Front | Station |
|------------|------------------:|---------|
| Bow | 0\" | 0% |
| Fwd Quarter | {L * 0.25:.0f}\" | 25% |
| Midship | {L * 0.50:.0f}\" | 50% |
| Aft Quarter | {L * 0.75:.0f}\" | 75% |
| Stern | {L:.0f}\" | 100% |

> Rename each plane in the Feature Tree for clarity.

---

## Step 3: Sketch Cross-Sections

On each reference plane, sketch the hull cross-section profile.
All coordinates use X = athwartship (beam), Y = vertical (depth).
Origin (0,0) = keel centerline at bottom.

{station_sections}

### Sketch Tips
- Use **Mirror** about the centerline (X=0) to ensure symmetry
- Add **Symmetric** relations between port and starboard points
- Fully constrain each sketch (green checkmark)
- Use **Construction Line** on centerline for mirror reference

---

## Step 4: Create Guide Curves

### Keel Curve (Bottom Profile)
1. Create a sketch on the **Right Plane**
2. Draw a spline from (0, 0) to ({L}, 0) with rocker:
   - Midpoint rises ~0.8\" above endpoints
   - Add tangent constraints at bow and stern (horizontal)
3. Points along keel:

| X (in) | Y (in) |
|-------:|-------:|
| 0 | 0.00 |
| {L*0.25:.0f} | 0.60 |
| {L*0.50:.0f} | 0.80 |
| {L*0.75:.0f} | 0.60 |
| {L:.0f} | 0.00 |

### Sheer Curve (Gunwale Profile)
1. On same sketch or new Right Plane sketch
2. Spline through gunwale edges:

| X (in) | Y (in) |
|-------:|-------:|
| 0 | {D + 1.2:.1f} |
| {L*0.25:.0f} | {D:.1f} |
| {L*0.50:.0f} | {D - 0.2:.1f} |
| {L*0.75:.0f} | {D:.1f} |
| {L:.0f} | {D + 1.2:.1f} |

---

## Step 5: Loft the Hull Surface

1. **Insert → Surface → Lofted Surface**
2. Select profiles in order: Bow → Fwd Quarter → Midship → Aft Quarter → Stern
3. Select guide curves: Keel and Sheer
4. Options:
   - Start constraint: **Normal to Profile**
   - End constraint: **Normal to Profile**
   - Tangent length: 1.0
5. Click **OK** (green check)

> **What you see:** A smooth hull surface stretching from bow to stern with
> V-bottom cross-sections that taper at the ends.

### Troubleshooting
- **"Loft failed"**: Ensure all sketches are on separate planes and fully defined
- **Twisted surface**: Check that profile selection order matches physical sequence
- **Sharp edges**: Increase tangent length or add intermediate stations

---

## Step 6: Create Shell (Add Thickness)

1. Select the lofted surface body
2. **Insert → Surface → Thicken**
3. Settings:
   - Thickness: **{THICKNESS_IN}\"** (0.5 inch)
   - Direction: **Inward** (thicken toward inside of hull)
4. Click OK

> **Alternatively** (if Thicken fails):
> 1. **Insert → Surface → Offset Surface** — offset {THICKNESS_IN}\" inward
> 2. **Insert → Surface → Knit Surface** — knit all surfaces into solid
> 3. Cap the open gunwale edge with a planar surface

---

## Step 7: Verify Mass Properties

1. **Tools → Mass Properties**
2. Set material density:
   - **Apply/Edit Material → Custom**
   - Density: **{CONCRETE_DENSITY_PCF / 1728 * 27.68:.6f} lb/in³** ({CONCRETE_DENSITY_PCF} lb/ft³)
3. Expected values:
   - **Volume:** ~{r['hull_wt'] / CONCRETE_DENSITY_PCF * 1728:.0f} in³
   - **Mass:** ~{r['hull_wt']:.0f} lbs (concrete only)
   - Add 17 lbs for reinforcement/hardware = **{r['hull_wt']:.0f} lbs total**

> If mass differs by >10%: check shell thickness is {THICKNESS_IN}\" everywhere,
> verify no gaps in the surface.

---

## Step 8: Export for CNC Mold Cutting

### Export Cross-Section DXFs
1. For each station plane:
   - Right-click plane → **Create Sketch From**
   - Use **Intersection Curve** to get the hull outline at that station
   - **File → Save As → DXF** (select "Export 2D")
2. Name files: `Station_00.dxf`, `Station_25.dxf`, etc.

### Export Full Hull STL (for reference)
1. **File → Save As → STL**
2. Resolution: Fine (deviation 0.01\", angle 5°)

### CNC Station Coordinates
See: `design/dxf_coords_design_{r['id']}.txt` for all station coordinates
at 6\" spacing ({math.ceil(L / 6)} stations total).

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| Loft self-intersects | Add more intermediate cross-sections |
| Shell fails at bow/stern | Taper cross-sections more gradually at ends |
| Asymmetric hull | Use Mirror feature about centerline plane |
| Wrong weight | Verify density units (lb/in³ not lb/ft³) |
| Surface gaps | Use Knit Surface before thickening |
| File too large | Reduce spline points, use lower mesh quality |

---

*Generated for NAU ASCE Concrete Canoe 2026 Competition*
*Design {r['id']}: {L}\" × {B}\" × {D}\"*
"""
    path = DESIGN_DIR / f"solidworks_design_{r['id']}_steps.md"
    path.write_text(content)
    print(f"  ✓ {path.relative_to(PROJECT_ROOT)}")


def generate_master_solidworks_guide():
    """Master SolidWorks guide with recommended Design A."""
    content = f"""# SolidWorks Concrete Canoe Build Guide — Master Reference
## NAU ASCE Concrete Canoe 2026
*Recommended: Design A (192\" × 32\" × 17\")*
*Generated: {datetime.now().strftime('%Y-%m-%d')}*

---

## Quick Reference — 3 Available Designs

| Design | Dimensions | Weight | Use Case |
|--------|-----------|--------|----------|
| **A (Recommended)** | 192\" × 32\" × 17\" | ~225 lbs | Lightest, meets all reqs |
| B (Conservative) | 196\" × 34\" × 18\" | ~259 lbs | Extra safety margin |
| C (Speed) | 216\" × 36\" × 18\" | ~296 lbs | Fastest hull speed |

## Design-Specific Guides

- [Design A Steps](solidworks_design_A_steps.md) — *Recommended*
- [Design B Steps](solidworks_design_B_steps.md)
- [Design C Steps](solidworks_design_C_steps.md)

## CNC Coordinate Files

- [Design A Coordinates](dxf_coords_design_A.txt)
- [Design B Coordinates](dxf_coords_design_B.txt)
- [Design C Coordinates](dxf_coords_design_C.txt)

## General SolidWorks Workflow

```
1. New Part (IPS units)
2. Create 5 reference planes (station spacing)
3. Sketch cross-sections on each plane
4. Add keel & sheer guide curves
5. Loft surface through all stations
6. Thicken surface to 0.5\" (inward)
7. Verify mass properties
8. Export DXFs for CNC / STL for reference
```

## Key Settings

| Parameter | Value |
|-----------|-------|
| Unit system | IPS (inch, pound, second) |
| Shell thickness | 0.5\" |
| Concrete density | {CONCRETE_DENSITY_PCF} lb/ft³ = {CONCRETE_DENSITY_PCF / 1728:.6f} lb/in³ |
| Deadrise angle | 15° |
| Rocker | 0.8\" max at midship |
| Sheer rise | 1.2\" at bow/stern |

---
*NAU ASCE Concrete Canoe Team — 2026*
"""
    path = DESIGN_DIR / "solidworks_step_by_step.md"
    path.write_text(content)
    print(f"  ✓ {path.relative_to(PROJECT_ROOT)}")


# ─── Markdown Comparison Report ───────────────────────────────────────

def generate_comparison_report(results):
    """Save detailed comparison as markdown report."""
    rows = ""
    for r in results:
        st = "✓ ALL PASS" if r["all_pass"] else "✗ FAIL"
        rows += f"| {r['name']} | {r['L']}×{r['B']}×{r['D']} | {r['hull_wt']} | {r['fb_in']} | {r['GM_in']} | {r['SF']} | {r['hull_speed']} | {st} |\n"

    content = f"""# 3 Alternative Hull Designs — Comparison
## NAU ASCE Concrete Canoe 2026
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*

---

## Summary Table

| Design | L×B×D (in) | Weight (lb) | FB (in) | GM (in) | SF | Speed (kts) | Status |
|--------|-----------|------------|---------|---------|-----|------------|--------|
{rows}
**Requirements:** Freeboard ≥ 6.0\", GM ≥ 6.0\", SF ≥ 2.0

---

## Design Descriptions

"""
    for r in results:
        content += f"""### Design {r['id']}: {r['name'].split('—')[1].strip()}
- **Dimensions:** {r['L']}\" × {r['B']}\" × {r['D']}\"
- **Philosophy:** {r['desc']}
- **Hull weight:** {r['hull_wt']} lbs | Loaded: {r['total_wt']} lbs
- **Freeboard:** {r['fb_in']}\" {'✓' if r['fb_pass'] else '✗'}
- **GM:** {r['GM_in']}\" {'✓' if r['gm_pass'] else '✗'}
- **Safety factor:** {r['SF']} {'✓' if r['sf_pass'] else '✗'}
- **Hull speed:** {r['hull_speed']} kts

"""

    content += """## Recommendation

**Design A** is recommended as the primary competition entry:
- Lightest weight saves paddler energy
- Meets all ASCE requirements with adequate margin
- Shorter length is easier to handle, transport, and store

**Design B** is the backup if structural concerns arise during testing.

**Design C** is optimal for straight-line sprint races due to higher hull speed,
but the weight penalty may offset the speed advantage.

## Figures
- [3 Hull Profiles](figures/3_designs_comparison.png)
- [Cross-Sections & Plan Views](figures/3_designs_visual_comparison.png)
- [Comparison Dashboard](figures/design_comparison_charts.png)
"""
    path = PROJECT_ROOT / "reports" / "3_alternative_designs.md"
    path.write_text(content)
    print(f"  ✓ {path.relative_to(PROJECT_ROOT)}")


# ─── Main ─────────────────────────────────────────────────────────────

def main():
    results = run_all()

    print("\n  Generating visualizations...")
    plot_3_designs_profiles(results)
    plot_comparison_charts(results)
    plot_3_designs_cross_sections(results)

    print("\n  Generating CNC coordinates...")
    generate_dxf_coords(results)

    print("\n  Generating SolidWorks guides...")
    for r in results:
        generate_solidworks_guide(r)
    generate_master_solidworks_guide()

    print("\n  Generating comparison report...")
    generate_comparison_report(results)

    print("\n" + "=" * 80)
    print("  ALL ALTERNATIVE DESIGN DELIVERABLES GENERATED")
    print("=" * 80)

    # File listing
    all_files = (
        sorted(FIGURES_DIR.glob("3_designs*")) +
        sorted(FIGURES_DIR.glob("design_comparison*")) +
        sorted(DATA_DIR.glob("3_alt*")) +
        sorted(DESIGN_DIR.glob("solidworks*")) +
        sorted(DESIGN_DIR.glob("dxf*")) +
        sorted(REPORTS_DIR.glob("3_alt*"))
    )
    print(f"\n  {'File':<55} {'Size':>8}")
    print("  " + "-" * 65)
    for f in all_files:
        print(f"  {str(f.relative_to(PROJECT_ROOT)):<55} {f.stat().st_size:>8,} B")

    return 0


if __name__ == "__main__":
    sys.exit(main())
