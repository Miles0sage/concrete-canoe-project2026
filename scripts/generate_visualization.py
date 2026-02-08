#!/usr/bin/env python3
"""
NAU Concrete Canoe 2026 - Visualization Generator
Generates PNG charts and HTML report. Works headless on VPS (no display).
Download reports/ to your Mac and open report.html in a browser.
"""

import sys
import base64
import io
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
REPORTS_DIR = PROJECT_ROOT / "reports" / "figures"

try:
    from calculations.concrete_canoe_calculator import run_complete_analysis
except ImportError:
    from concrete_canoe_calculator import run_complete_analysis

# Canoe variants
VARIANTS = [
    ("Canoe 1", 18 * 12, 30, 18, 276),
    ("Canoe 2", 18 * 12, 36, 18, 300),
    ("Canoe 3", 16 * 12, 42, 18, 320),
]


def run_analysis() -> list:
    """Get analysis results for all variants."""
    rows = []
    for name, length, beam, depth, weight in VARIANTS:
        r = run_complete_analysis(length, beam, depth, 0.5, weight, 1500)
        rows.append({
            "name": name,
            "length_in": length,
            "beam_in": beam,
            "depth_in": depth,
            "weight_lbs": weight,
            "freeboard_in": r["freeboard"]["freeboard_in"],
            "gm_in": r["stability"]["gm_in"],
            "safety_factor": r["structural"]["safety_factor"],
            "pass": r["overall_pass"],
        })
    return rows


def fig_to_base64(fig) -> str:
    """Convert matplotlib figure to base64 for HTML embedding."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def generate_charts(rows: list) -> dict:
    """Generate charts, return {title: base64_img}."""
    try:
        import matplotlib
        matplotlib.use("Agg")  # Headless - no display
        import matplotlib.pyplot as plt
    except ImportError:
        return {}

    names = [r["name"] for r in rows]
    result = {}

    # 1. Freeboard comparison
    fig, ax = plt.subplots(figsize=(7, 4))
    fb = [r["freeboard_in"] for r in rows]
    colors = ["#2ecc71" if r["pass"] else "#e74c3c" for r in rows]
    ax.bar(names, fb, color=colors)
    ax.axhline(y=4, color="gray", linestyle="--", label="Min 4 in")
    ax.set_ylabel("Freeboard (in)")
    ax.set_title("Freeboard by Hull Variant")
    ax.legend()
    ax.set_ylim(0, max(fb) * 1.2)
    result["freeboard"] = fig_to_base64(fig)
    plt.close()

    # 2. Metacentric height (stability)
    fig, ax = plt.subplots(figsize=(7, 4))
    gm = [r["gm_in"] for r in rows]
    ax.bar(names, gm, color=colors)
    ax.axhline(y=0.5, color="gray", linestyle="--", label="Min 0.5 in")
    ax.set_ylabel("GM (in)")
    ax.set_title("Metacentric Height (Stability) by Variant")
    ax.legend()
    ax.set_ylim(0, max(gm) * 1.1)
    result["gm"] = fig_to_base64(fig)
    plt.close()

    # 3. Weight vs freeboard trade-off
    fig, ax = plt.subplots(figsize=(7, 4))
    w = [r["weight_lbs"] for r in rows]
    ax.scatter(w, fb, s=150, c=range(len(names)), cmap="viridis")
    for i, n in enumerate(names):
        ax.annotate(n, (w[i], fb[i]), textcoords="offset points", xytext=(0, 8), ha="center")
    ax.set_xlabel("Weight (lbs)")
    ax.set_ylabel("Freeboard (in)")
    ax.set_title("Weight vs Freeboard Trade-off")
    result["tradeoff"] = fig_to_base64(fig)
    plt.close()

    return result


def generate_html_report(rows: list, charts: dict) -> str:
    """Build self-contained HTML report."""
    table_rows = ""
    for r in rows:
        status = "✓ Pass" if r["pass"] else "✗ Fail"
        table_rows += f"""
        <tr>
            <td>{r['name']}</td>
            <td>{r['length_in']//12}'</td>
            <td>{r['beam_in']}\"</td>
            <td>{r['depth_in']}\"</td>
            <td>{r['weight_lbs']}</td>
            <td>{r['freeboard_in']:.2f}</td>
            <td>{r['gm_in']:.2f}</td>
            <td>{r['safety_factor']:.2f}</td>
            <td>{status}</td>
        </tr>"""

    chart_html = ""
    for key, b64 in charts.items():
        chart_html += f'<img src="data:image/png;base64,{b64}" style="max-width:600px; margin:10px;"/>'

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>NAU Canoe 2026 - Hull Analysis</title>
<style>
  body {{ font-family: system-ui; margin: 2rem; max-width: 800px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
  th {{ background: #333; color: white; }}
  .pass {{ color: green; }} .fail {{ color: red; }}
</style>
</head>
<body>
<h1>NAU ASCE Concrete Canoe 2026 – Hull Analysis</h1>
<p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>

<h2>Comparison Table</h2>
<table>
<tr><th>Variant</th><th>Length</th><th>Beam</th><th>Depth</th><th>Weight</th><th>Freeboard</th><th>GM</th><th>SF</th><th>Status</th></tr>
{table_rows}
</table>

<h2>Charts</h2>
<div>{chart_html}</div>

<h2>Next Steps</h2>
<ul>
<li>Pick variant with best freeboard + stability for your race profile</li>
<li>Validate with Excel and CAD</li>
<li>Document final dimensions in NAU_Hull_Design_Plan_2026.md</li>
</ul>
</body>
</html>"""


def main() -> int:
    print("NAU Canoe 2026 - Generating visualization report...")

    rows = run_analysis()
    charts = generate_charts(rows)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    html_path = REPORTS_DIR / "report.html"

    html = generate_html_report(rows, charts)
    with open(html_path, "w") as f:
        f.write(html)

    print(f"Report saved: {html_path}")
    print("")
    print("To view on your Mac (from VPS):")
    print("  scp user@YOUR_VPS_IP:~/nau-canoe-2026/reports/figures/report.html ~/Desktop/")
    print("  open ~/Desktop/report.html")
    print("")
    print("Or download the whole reports folder:")
    print("  scp -r user@YOUR_VPS_IP:~/nau-canoe-2026/reports ~/Desktop/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
