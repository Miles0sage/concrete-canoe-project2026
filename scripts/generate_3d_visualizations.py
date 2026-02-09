#!/usr/bin/env python3
"""
NAU ASCE Concrete Canoe 2026 — 3D Hull Visualizations
Generates 3D surface plots for each design + comparison overlay.
Output: PNG (static 300 DPI).
"""

import sys
import math
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

FIG_DIR = PROJECT_ROOT / "reports" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# ── Design definitions ──
DESIGNS = {
    "A": {"name": "Design A: Optimal", "L": 192, "B": 32, "D": 17,
           "t": 0.5, "color": "#2196F3", "cmap": "Blues"},
    "B": {"name": "Design B: Conservative", "L": 196, "B": 34, "D": 18,
           "t": 0.5, "color": "#4CAF50", "cmap": "Greens"},
    "C": {"name": "Design C: Traditional", "L": 216, "B": 36, "D": 18,
           "t": 0.5, "color": "#FF9800", "cmap": "Oranges"},
}


def generate_hull_surface(L, B, D, n_long=80, n_circ=40):
    """
    Generate 3D hull surface coordinates.
    Parametric model: length along x, cross-section varies with station.
    Returns X, Y, Z arrays for matplotlib surface plot.
    """
    # Longitudinal stations
    u = np.linspace(0, 1, n_long)  # 0=bow, 1=stern
    # Circumferential parameter (half-section, mirrored)
    v = np.linspace(0, 1, n_circ)  # 0=keel, 1=gunwale

    X = np.zeros((n_long, n_circ))
    Y = np.zeros((n_long, n_circ))
    Z = np.zeros((n_long, n_circ))

    for i, ui in enumerate(u):
        x = ui * L  # longitudinal position

        # Station shape factor (tapers at bow and stern)
        taper = 1.0 - (2*ui - 1)**4  # smooth taper
        taper = max(taper, 0.02)

        # Half-beam at this station
        half_b = (B / 2) * taper

        # Depth at this station (slight rocker)
        rocker = D * 0.06 * (2*ui - 1)**2
        local_D = D - rocker

        # Deadrise (V-bottom)
        deadrise_depth = local_D * 0.20

        for j, vj in enumerate(v):
            X[i, j] = x

            if vj <= 0.3:
                # Keel to chine (V-bottom)
                frac = vj / 0.3
                Y[i, j] = half_b * 0.8 * frac
                Z[i, j] = -deadrise_depth * (1 - frac)
            else:
                # Chine to gunwale (flared sides)
                frac = (vj - 0.3) / 0.7
                Y[i, j] = half_b * (0.8 + 0.2 * frac)
                Z[i, j] = local_D * frac

    return X, Y, Z


def plot_single_hull_3d(label, d, save=True):
    """Generate 4-view 3D plot for a single design."""
    L, B, D = d["L"], d["B"], d["D"]
    name = d["name"]
    cmap_name = d["cmap"]

    X, Y, Z = generate_hull_surface(L, B, D)
    # Mirror for full hull
    X_full = np.vstack([X, X])
    Y_full = np.vstack([Y, -Y[:, ::-1]])
    Z_full = np.vstack([Z, Z[:, ::-1]])

    fig = plt.figure(figsize=(20, 16))
    fig.suptitle(f"{name}\n{L}\" × {B}\" × {D}\" — 3D Hull Rendering",
                 fontsize=16, fontweight="bold", y=0.98)

    views = [
        ("Isometric View", 25, -55),
        ("Front View (Bow)", 5, -90),
        ("Side View (Port)", 5, 0),
        ("Top View (Plan)", 89, -90),
    ]

    # Waterline height (approximate draft ~5-6")
    wl_z = -(D * 0.20) + 5  # rough waterline

    for idx, (title, elev, azim) in enumerate(views, 1):
        ax = fig.add_subplot(2, 2, idx, projection="3d")

        # Hull surface colored by depth
        surf = ax.plot_surface(X_full, Y_full, Z_full,
                               cmap=cmap_name, alpha=0.75,
                               edgecolor="gray", linewidth=0.15,
                               rstride=2, cstride=2)

        # Waterline ring
        u_wl = np.linspace(0, 1, 200)
        for ui in u_wl:
            taper = max(1.0 - (2*ui - 1)**4, 0.02)
            hb = (B/2) * taper
            x_wl = ui * L
            ax.plot([x_wl, x_wl], [hb, -hb], [wl_z, wl_z],
                    color="cyan", alpha=0.01, lw=0.3)
        # Waterline contour (simplified)
        wl_x = np.linspace(0, L, 100)
        wl_taper = np.array([max(1.0-(2*xi/L-1)**4, 0.02) for xi in wl_x])
        wl_y_pos = (B/2) * wl_taper
        ax.plot(wl_x, wl_y_pos, wl_z, color="cyan", lw=2.5,
                label="Waterline", zorder=10)
        ax.plot(wl_x, -wl_y_pos, wl_z, color="cyan", lw=2.5, zorder=10)

        # Keel line
        keel_z = np.array([-(D*0.20)*(1-(2*xi/L-1)**2*0) - D*0.20*(1-max(1-(2*xi/L-1)**4,0.02))
                           for xi in wl_x])
        # Simplified keel
        keel_z2 = np.array([-(D*0.20)*max(1-(2*xi/L-1)**4, 0.02) for xi in wl_x])
        ax.plot(wl_x, np.zeros_like(wl_x), keel_z2,
                color="red", lw=1.5, ls="--", alpha=0.6, label="Keel line")

        ax.view_init(elev=elev, azim=azim)
        ax.set_xlabel("Length (in)", fontsize=9)
        ax.set_ylabel("Beam (in)", fontsize=9)
        ax.set_zlabel("Depth (in)", fontsize=9)
        ax.set_title(title, fontsize=12, fontweight="bold")
        if idx == 1:
            ax.legend(fontsize=9, loc="upper left")

        # Set consistent aspect-ish
        ax.set_xlim(0, L)
        ax.set_ylim(-B/2 - 5, B/2 + 5)
        ax.set_zlim(-D*0.3, D*1.1)

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    out = FIG_DIR / f"3d_hull_design_{label}.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] {out.name}")
    return out


def plot_comparison_3d():
    """All 3 hulls overlaid in 3D — 2 views."""
    fig = plt.figure(figsize=(20, 10))
    fig.suptitle("3D Hull Comparison — All 3 Designs Overlaid",
                 fontsize=16, fontweight="bold", y=0.99)

    hulls = {}
    for label, d in DESIGNS.items():
        X, Y, Z = generate_hull_surface(d["L"], d["B"], d["D"])
        X_full = np.vstack([X, X])
        Y_full = np.vstack([Y, -Y[:, ::-1]])
        Z_full = np.vstack([Z, Z[:, ::-1]])
        hulls[label] = (X_full, Y_full, Z_full, d)

    views = [
        ("Isometric Overlay", 25, -55),
        ("Side-by-Side (Top View)", 89, -90),
    ]

    for idx, (title, elev, azim) in enumerate(views, 1):
        ax = fig.add_subplot(1, 2, idx, projection="3d")

        for label, (Xf, Yf, Zf, d) in hulls.items():
            color = d["color"]
            ax.plot_surface(Xf, Yf, Zf, color=color, alpha=0.25,
                            edgecolor=color, linewidth=0.2,
                            rstride=3, cstride=3)
            # Gunwale outline
            ax.plot(Xf[0, :], Yf[0, :], Zf[0, :], color=color, lw=0.5)
            # Add label at midpoint
            mid = len(Xf)//4
            ax.text(Xf[mid, -1], Yf[mid, -1]+5, Zf[mid, -1]+3,
                    d["name"].split(":")[0], color=color, fontsize=10,
                    fontweight="bold")

        ax.view_init(elev=elev, azim=azim)
        ax.set_xlabel("Length (in)", fontsize=10)
        ax.set_ylabel("Beam (in)", fontsize=10)
        ax.set_zlabel("Depth (in)", fontsize=10)
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_xlim(0, 220)
        ax.set_ylim(-25, 25)
        ax.set_zlim(-10, 22)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out = FIG_DIR / "3d_comparison_all_designs.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] {out.name}")
    return out


def main():
    print("=" * 55)
    print("  PHASE 2: 3D Hull Visualizations")
    print("=" * 55)

    for label, d in DESIGNS.items():
        print(f"\n  Rendering {d['name']}...")
        try:
            plot_single_hull_3d(label, d)
        except Exception as e:
            print(f"  [ERROR] {label}: {e}")
            import traceback; traceback.print_exc()

    print(f"\n  Rendering comparison overlay...")
    try:
        plot_comparison_3d()
    except Exception as e:
        print(f"  [ERROR] comparison: {e}")
        import traceback; traceback.print_exc()

    print("\n  Phase 2 complete.")


if __name__ == "__main__":
    main()
