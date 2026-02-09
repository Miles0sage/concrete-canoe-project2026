#!/usr/bin/env python3
"""
NAU ASCE Concrete Canoe 2026 — Missing ASCE Diagrams
Generates: lines plan, construction sequence, paddler ergonomics,
           transportation logistics, racing strategy.
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
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Arc

FIG_DIR = PROJECT_ROOT / "reports" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Design A (recommended) dimensions
L, B, D, t = 192, 32, 17, 0.5
L_ft, B_ft, D_ft = L/12, B/12, D/12


def hull_half_beam(station_frac):
    """Half-beam at a given station fraction (0=bow, 1=stern)."""
    return (B / 2) * max(1.0 - (2*station_frac - 1)**4, 0.02)


def hull_deadrise(station_frac):
    """Deadrise depth at a station fraction."""
    taper = max(1.0 - (2*station_frac - 1)**4, 0.02)
    return D * 0.20 * taper


# ═══════════════════════════════════════════════════════════════
# 1. HULL LINES PLAN (traditional naval architecture)
# ═══════════════════════════════════════════════════════════════
def fig_lines_plan():
    fig, axes = plt.subplots(3, 1, figsize=(18, 16))
    fig.suptitle("Hull Lines Plan — Design A (192\" × 32\" × 17\")\nTraditional Naval Architecture Drawing",
                 fontsize=15, fontweight="bold", y=0.99)

    stations = np.linspace(0, 1, 11)  # 0-10
    station_labels = [str(i) for i in range(11)]

    # ── Body Plan (cross-sections) ──
    ax = axes[0]
    ax.set_title("Body Plan (Cross-Sections at 11 Stations)", fontweight="bold", fontsize=13)
    for i, s in enumerate(stations):
        hb = hull_half_beam(s)
        dd = hull_deadrise(s)
        # V-bottom cross section (right half only for body plan)
        xs = np.array([0, hb * 0.8, hb, hb])
        ys = np.array([-dd, 0, 0, D])
        color = plt.cm.viridis(i / 10)
        lw = 2.5 if i == 5 else 1.5
        ax.plot(xs, ys, color=color, lw=lw, label=f"Stn {i}")
        # Mirror
        ax.plot(-xs, ys, color=color, lw=lw)
        # Station number
        ax.text(hb + 0.5, D + 0.5, str(i), fontsize=7, color=color, ha="center")

    ax.axhline(0, color="gray", ls=":", lw=0.8)
    ax.axvline(0, color="gray", ls=":", lw=0.8)
    ax.set_xlabel("Half-Beam (in)")
    ax.set_ylabel("Height (in)")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.2)
    ax.legend(fontsize=7, ncol=6, loc="lower right")

    # ── Profile Plan (side view with stations) ──
    ax = axes[1]
    ax.set_title("Profile Plan (Side View with Station Lines)", fontweight="bold", fontsize=13)
    x = np.linspace(0, L, 200)
    rocker = D * 0.06 * (2*x/L - 1)**2
    bottom = rocker
    gunwale = np.full_like(x, D)
    ax.fill_between(x, bottom, gunwale, alpha=0.08, color="blue")
    ax.plot(x, bottom, "b-", lw=2, label="Keel (bottom)")
    ax.plot(x, gunwale, "b-", lw=2)

    # Station lines
    for i, s in enumerate(stations):
        sx = s * L
        ax.axvline(sx, color="gray", ls="--", lw=0.8, alpha=0.6)
        ax.text(sx, D + 1.5, str(i), ha="center", fontsize=8, color="gray")

    # Waterline
    ax.axhline(6.0, color="cyan", ls="-.", lw=1.5, label="Waterline (6.0\")")
    ax.set_xlabel("Length (in)")
    ax.set_ylabel("Height (in)")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.2)

    # ── Half-Breadth Plan (top view) ──
    ax = axes[2]
    ax.set_title("Half-Breadth Plan (Top View)", fontweight="bold", fontsize=13)
    u = np.linspace(0, 1, 200)
    xs = u * L
    half_beams = np.array([hull_half_beam(ui) for ui in u])
    ax.fill_between(xs, -half_beams, half_beams, alpha=0.1, color="blue")
    ax.plot(xs, half_beams, "b-", lw=2, label="Gunwale outline")
    ax.plot(xs, -half_beams, "b-", lw=2)

    # Waterlines at different heights
    for wl_frac, wl_label, ls in [(0.3, "WL 1 (low)", ":"),
                                    (0.5, "WL 2 (mid)", "--"),
                                    (0.7, "WL 3 (high)", "-.")]:
        wl_beams = half_beams * (0.5 + 0.5 * wl_frac)
        ax.plot(xs, wl_beams, ls=ls, lw=1.2, alpha=0.6, label=wl_label)
        ax.plot(xs, -wl_beams, ls=ls, lw=1.2, alpha=0.6)

    # Station lines
    for i, s in enumerate(stations):
        sx = s * L
        ax.axvline(sx, color="gray", ls="--", lw=0.5, alpha=0.4)

    ax.set_xlabel("Length (in)")
    ax.set_ylabel("Half-Beam (in)")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(True, alpha=0.2)
    ax.set_aspect("equal")

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out = FIG_DIR / "hull_lines_plan.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] {out.name}")


# ═══════════════════════════════════════════════════════════════
# 2. CONSTRUCTION SEQUENCE
# ═══════════════════════════════════════════════════════════════
def fig_construction_sequence():
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle("Construction Sequence — Step-by-Step Build Process",
                 fontsize=16, fontweight="bold", y=1.01)

    steps = [
        ("Step 1: Mold Setup", "#E3F2FD",
         "Build female EPS foam mold\non plywood strongback.\n"
         f"Mold: {L_ft+1:.0f}' × {B_ft+1:.0f}'\n"
         "Apply mold release agent."),
        ("Step 2: Reinforcement", "#E8F5E9",
         "Lay PVA fiber mesh in mold.\n"
         "Position spacer blocks (0.5\")\nat 12\" intervals.\n"
         "Pre-cut mesh panels to shape."),
        ("Step 3: Concrete Placement", "#FFF3E0",
         "Mix lightweight concrete (60 PCF).\n"
         "Apply outer layer (0.25\").\n"
         "Place mesh reinforcement.\n"
         "Apply inner layer (0.25\")."),
        ("Step 4: Curing", "#F3E5F5",
         "Cover with plastic sheeting.\n"
         "Moist cure for 7 days.\n"
         "Maintain 70°F minimum.\n"
         "Mist every 12 hours."),
        ("Step 5: Demolding", "#FFEBEE",
         "Day 7-10: Remove from mold.\n"
         "6-person flip team required.\n"
         "Support at 1/4 points.\n"
         "Inspect for defects."),
        ("Step 6: Finishing", "#E0F7FA",
         "Sand exterior to 220 grit.\n"
         "Apply concrete sealer.\n"
         "Add competition graphics.\n"
         "Final weight check."),
    ]

    for idx, (title, bg_color, description) in enumerate(steps):
        ax = axes[idx // 3][idx % 3]
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_facecolor(bg_color)

        # Step number circle
        circle = plt.Circle((1.2, 8.5), 0.7, color="white", ec="black", lw=2)
        ax.add_patch(circle)
        ax.text(1.2, 8.5, str(idx + 1), ha="center", va="center",
                fontsize=16, fontweight="bold")

        ax.set_title(title, fontsize=13, fontweight="bold", pad=10)

        # Description text
        ax.text(5, 4.5, description, ha="center", va="center",
                fontsize=11, fontfamily="monospace",
                bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8))

        # Simple illustration
        if idx == 0:  # Mold
            mold_x = [2, 2, 8, 8]
            mold_y = [1.5, 0.8, 0.8, 1.5]
            ax.fill(mold_x + [8, 2], mold_y + [1.5, 1.5], alpha=0.3, color="brown")
            ax.plot(mold_x, mold_y, "k-", lw=2)
        elif idx == 1:  # Mesh
            for yy in np.arange(1, 2, 0.15):
                ax.plot([2.5, 7.5], [yy, yy], "g-", lw=0.8, alpha=0.5)
            for xx in np.arange(2.5, 8, 0.3):
                ax.plot([xx, xx], [0.8, 2], "g-", lw=0.8, alpha=0.5)
        elif idx == 2:  # Concrete
            cx = [2, 2, 5, 8, 8]
            cy = [2, 0.8, 0.5, 0.8, 2]
            ax.fill(cx, cy, alpha=0.3, color="gray")
            ax.plot(cx, cy, "k-", lw=2)
        elif idx == 3:  # Curing
            ax.fill([1.5, 1.5, 8.5, 8.5], [0.5, 2.2, 2.2, 0.5],
                    alpha=0.15, color="purple")
            ax.plot([1.5, 8.5], [2.2, 2.2], "m--", lw=1.5)
            ax.text(5, 1.3, "PLASTIC COVER", ha="center", fontsize=8,
                    color="purple", fontstyle="italic")
        elif idx == 4:  # Demolding
            ax.annotate("", xy=(5, 2.5), xytext=(5, 0.8),
                        arrowprops=dict(arrowstyle="->", lw=2, color="red"))
            ax.text(5, 1.5, "FLIP", ha="center", fontsize=10,
                    fontweight="bold", color="red")
        elif idx == 5:  # Finishing
            ax.fill([2, 2, 5, 8, 8], [2, 1, 0.7, 1, 2],
                    alpha=0.4, color="skyblue")
            ax.text(5, 1.3, "SEALED", ha="center", fontsize=10,
                    fontweight="bold", color="blue")

        ax.set_xticks([])
        ax.set_yticks([])

    plt.tight_layout()
    out = FIG_DIR / "construction_sequence.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] {out.name}")


# ═══════════════════════════════════════════════════════════════
# 3. PADDLER ERGONOMICS
# ═══════════════════════════════════════════════════════════════
def fig_paddler_ergonomics():
    fig, axes = plt.subplots(1, 2, figsize=(20, 8))
    fig.suptitle("Paddler Ergonomics & Seating Layout",
                 fontsize=16, fontweight="bold", y=1.01)

    # ── Top View ──
    ax = axes[0]
    ax.set_title("Top View — Seating Positions", fontweight="bold", fontsize=13)

    u = np.linspace(0, 1, 200)
    xs = u * L
    hb = np.array([hull_half_beam(ui) for ui in u])
    ax.fill_between(xs, -hb, hb, alpha=0.1, color="blue")
    ax.plot(xs, hb, "b-", lw=2)
    ax.plot(xs, -hb, "b-", lw=2)

    # Paddler positions
    positions = [
        (L * 0.20, "P1\n(Bow)", "Bow paddler"),
        (L * 0.40, "P2", "Power position"),
        (L * 0.60, "P3", "Power position"),
        (L * 0.80, "P4\n(Stern)", "Steering"),
    ]
    colors = ["#F44336", "#FF9800", "#4CAF50", "#2196F3"]

    for (px, plabel, role), clr in zip(positions, colors):
        frac = px / L
        local_hb = hull_half_beam(frac)

        # Seated figure (simplified)
        ax.plot(px, 0, "o", ms=14, color=clr, zorder=5)
        ax.text(px, -local_hb * 0.6, plabel, ha="center", fontsize=10,
                fontweight="bold", color=clr)
        ax.text(px, local_hb * 0.5, role, ha="center", fontsize=8,
                color=clr, fontstyle="italic")

        # Paddle arc (swing clearance)
        paddle_len = 20  # inches
        for angle in [-40, 0, 40]:
            dx = paddle_len * math.sin(math.radians(angle))
            dy = paddle_len * math.cos(math.radians(angle))
            ax.plot([px, px + dx], [0, dy], color=clr, lw=0.8, alpha=0.3)
        # Paddle arc
        arc_y = np.linspace(-paddle_len * 0.65, paddle_len * 0.65, 30)
        arc_x = px + np.sqrt(np.maximum(0, paddle_len**2 - arc_y**2)) * 0.3
        ax.plot(arc_x, arc_y, color=clr, lw=1, ls=":", alpha=0.5)

    # Dimensions
    ax.annotate("", xy=(0, -B/2 - 5), xytext=(L, -B/2 - 5),
                arrowprops=dict(arrowstyle="<->", lw=1.2))
    ax.text(L/2, -B/2 - 7, f"L = {L}\"", ha="center", fontsize=10,
            fontweight="bold")

    ax.set_xlabel("Length (in)")
    ax.set_ylabel("Beam (in)")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.2)

    # ── Side View (Ergonomics) ──
    ax = axes[1]
    ax.set_title("Side View — Paddler Clearances", fontweight="bold", fontsize=13)

    x = np.linspace(0, L, 200)
    rocker = D * 0.06 * (2*x/L - 1)**2
    gunwale = np.full_like(x, D)
    ax.fill_between(x, rocker, gunwale, alpha=0.1, color="blue")
    ax.plot(x, rocker, "b-", lw=2)
    ax.plot(x, gunwale, "b-", lw=2)

    # Waterline
    ax.axhline(6.0, color="cyan", ls="-.", lw=1.5, alpha=0.6)

    # Paddler figures (simplified stick figures)
    for (px, plabel, _), clr in zip(positions, colors):
        frac = px / L
        floor_y = D * 0.06 * (2*frac - 1)**2 + t  # floor level

        # Seated height ~30" from floor
        seat_y = floor_y + 2  # sitting on hull bottom
        head_y = seat_y + 22  # approximate

        # Body
        ax.plot([px, px], [seat_y, seat_y + 15], color=clr, lw=2.5)
        # Head
        ax.plot(px, head_y, "o", ms=8, color=clr)
        # Arms
        ax.plot([px - 8, px + 8], [seat_y + 12, seat_y + 12],
                color=clr, lw=1.5)
        # Knee clearance annotation
        ax.annotate("", xy=(px + 5, floor_y), xytext=(px + 5, seat_y + 8),
                    arrowprops=dict(arrowstyle="<->", color=clr, lw=1))
        ax.text(px + 7, (floor_y + seat_y + 8) / 2, "Knee\nclear.",
                fontsize=7, color=clr, va="center")

    # Freeboard annotation
    ax.annotate("", xy=(L - 15, 6.0), xytext=(L - 15, D),
                arrowprops=dict(arrowstyle="<->", color="green", lw=1.5))
    ax.text(L - 8, (6.0 + D) / 2, f"FB\n{D-6:.0f}\"", fontsize=9,
            color="green", fontweight="bold", va="center")

    ax.set_xlabel("Length (in)")
    ax.set_ylabel("Height (in)")
    ax.set_xlim(-5, L + 15)
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    out = FIG_DIR / "paddler_ergonomics.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] {out.name}")


# ═══════════════════════════════════════════════════════════════
# 4. TRANSPORTATION LOGISTICS
# ═══════════════════════════════════════════════════════════════
def fig_transportation():
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    fig.suptitle("Transportation & Logistics Plan",
                 fontsize=16, fontweight="bold", y=1.01)

    # ── Trailer Layout ──
    ax = axes[0]
    ax.set_title("Trailer Layout — Canoe Transport", fontweight="bold", fontsize=13)

    # Trailer frame
    trailer_L = 220  # inches
    trailer_W = 60
    ax.add_patch(plt.Rectangle((-10, -trailer_W/2), trailer_L + 20, trailer_W,
                                fill=False, edgecolor="black", lw=2))
    ax.text(trailer_L/2, -trailer_W/2 - 5, f"Trailer: {trailer_L+20}\" × {trailer_W}\"",
            ha="center", fontsize=10)

    # Canoe outline (top view)
    u = np.linspace(0, 1, 200)
    xs = u * L
    hb = np.array([hull_half_beam(ui) for ui in u])
    ax.fill_between(xs, -hb, hb, alpha=0.2, color="blue")
    ax.plot(xs, hb, "b-", lw=2)
    ax.plot(xs, -hb, "b-", lw=2)
    ax.text(L/2, 0, f"CANOE\n{L}\" × {B}\"", ha="center", va="center",
            fontsize=12, fontweight="bold", color="blue")

    # Tie-down points
    td_positions = [(L*0.15, B/2+5), (L*0.85, B/2+5),
                    (L*0.15, -B/2-5), (L*0.85, -B/2-5)]
    for tx, ty in td_positions:
        ax.plot(tx, ty, "rx", ms=12, mew=3)
        ax.plot([tx, tx + (5 if ty > 0 else -5)],
                [ty, ty + (5 if ty > 0 else -5)], "r-", lw=1.5)
    ax.text(L*0.15, B/2 + 12, "Tie-down", fontsize=8, color="red",
            ha="center")

    # Support cradles
    for cx in [L*0.25, L*0.5, L*0.75]:
        ax.plot([cx-5, cx+5], [B/2+2, B/2+2], "k-", lw=3)
        ax.plot([cx-5, cx+5], [-B/2-2, -B/2-2], "k-", lw=3)
        ax.text(cx, B/2 + 4, "Cradle", fontsize=7, ha="center")

    ax.set_xlabel("Length (in)")
    ax.set_ylabel("Width (in)")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.2)

    # ── Loading Procedure ──
    ax = axes[1]
    ax.set_title("Loading Procedure — Step-by-Step", fontweight="bold", fontsize=13)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    steps = [
        "1. Position trailer level on flat ground",
        "2. Place 3 foam cradles on trailer bed",
        "   (at 25%, 50%, 75% of canoe length)",
        "3. Team of 6: lift canoe from mold area",
        "   - 2 at bow, 2 at stern, 2 at midship",
        "4. Walk to trailer, lower onto cradles",
        "5. Verify alignment (centered, level)",
        "6. Secure 4 ratchet straps at quarter points",
        "7. Add foam padding at all contact points",
        "8. Cover with fitted tarp for transport",
        "",
        "SAFETY NOTES:",
        "- Minimum 6 persons for lifting",
        f"- Canoe weight: ~174 lbs (29 lbs/person)",
        "- Always support at 1/4 point locations",
        "- Never grip gunwale edges directly",
        "- Transport speed: ≤ 45 mph",
    ]
    y = 9.5
    for line in steps:
        weight = "bold" if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "SAFETY")) else "normal"
        color = "red" if "SAFETY" in line else "black"
        ax.text(0.5, y, line, fontsize=10, fontweight=weight, color=color,
                fontfamily="monospace", va="top")
        y -= 0.55

    plt.tight_layout()
    out = FIG_DIR / "transportation_logistics.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] {out.name}")


# ═══════════════════════════════════════════════════════════════
# 5. RACING STRATEGY
# ═══════════════════════════════════════════════════════════════
def fig_racing_strategy():
    fig, axes = plt.subplots(1, 2, figsize=(20, 9))
    fig.suptitle("Competition Racing Strategy",
                 fontsize=16, fontweight="bold", y=1.01)

    # ── Sprint Course ──
    ax = axes[0]
    ax.set_title("Sprint Race — 200m Straight Course", fontweight="bold", fontsize=13)

    # Lane markers
    for lane in range(4):
        y = lane * 30
        ax.fill_between([0, 200], y - 10, y + 10, alpha=0.05, color="blue")
        ax.plot([0, 200], [y - 10, y - 10], "b-", lw=0.5, alpha=0.3)
        ax.plot([0, 200], [y + 10, y + 10], "b-", lw=0.5, alpha=0.3)
        ax.text(-10, y, f"Lane {lane+1}", ha="right", fontsize=9, va="center")

    # Our canoe in lane 2
    our_y = 30
    canoe_x = [70, 86]  # canoe at ~80m mark
    ax.fill([canoe_x[0], canoe_x[0], canoe_x[1], canoe_x[1]],
            [our_y-3, our_y+3, our_y+3, our_y-3],
            alpha=0.6, color="#2196F3")
    ax.text(78, our_y, "NAU", ha="center", va="center", fontsize=8,
            color="white", fontweight="bold")

    # Start and finish
    ax.axvline(0, color="green", lw=3, label="Start")
    ax.axvline(200, color="red", lw=3, label="Finish")
    ax.text(0, -20, "START", ha="center", fontsize=11, fontweight="bold", color="green")
    ax.text(200, -20, "FINISH", ha="center", fontsize=11, fontweight="bold", color="red")

    # Strategy annotations
    ax.annotate("Phase 1: Explosive Start\n(0-50m, max power)",
                xy=(25, 95), fontsize=9, fontweight="bold",
                bbox=dict(boxstyle="round", facecolor="yellow", alpha=0.8))
    ax.annotate("Phase 2: Maintain Speed\n(50-150m, steady cadence)",
                xy=(90, 95), fontsize=9, fontweight="bold",
                bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.8))
    ax.annotate("Phase 3: Sprint Finish\n(150-200m, max effort)",
                xy=(160, 95), fontsize=9, fontweight="bold",
                bbox=dict(boxstyle="round", facecolor="salmon", alpha=0.8))

    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Lane Position")
    ax.legend(fontsize=10)
    ax.set_xlim(-20, 220)
    ax.grid(True, alpha=0.2)

    # ── Slalom Course ──
    ax = axes[1]
    ax.set_title("Slalom Race — Gate Navigation", fontweight="bold", fontsize=13)

    # Course outline
    course_x = np.linspace(0, 200, 500)
    course_center = 40 * np.sin(course_x * np.pi / 50)

    ax.fill_between(course_x, course_center - 20, course_center + 20,
                    alpha=0.05, color="blue")
    ax.plot(course_x, course_center - 20, "b-", lw=1, alpha=0.3)
    ax.plot(course_x, course_center + 20, "b-", lw=1, alpha=0.3)

    # Gates
    gate_positions = [30, 60, 90, 120, 150, 180]
    for i, gx in enumerate(gate_positions):
        gy = 40 * math.sin(gx * math.pi / 50)
        gate_w = 20
        ax.plot([gx, gx], [gy - gate_w/2, gy + gate_w/2], "r-", lw=3)
        ax.plot(gx, gy - gate_w/2, "rv", ms=8)
        ax.plot(gx, gy + gate_w/2, "r^", ms=8)
        ax.text(gx, gy + gate_w/2 + 5, f"Gate {i+1}", ha="center",
                fontsize=8, fontweight="bold", color="red")

    # Optimal path
    opt_x = np.linspace(0, 200, 200)
    opt_y = 35 * np.sin(opt_x * np.pi / 50)
    ax.plot(opt_x, opt_y, "g--", lw=2.5, label="Optimal path")

    # Canoe position
    ax.fill([40, 40, 56, 56], [-2, 4, 4, -2],
            alpha=0.6, color="#2196F3")
    ax.text(48, 1, "NAU", ha="center", va="center", fontsize=7,
            color="white", fontweight="bold")

    ax.axvline(0, color="green", lw=3)
    ax.axvline(200, color="red", lw=3)
    ax.text(0, -55, "START", ha="center", fontsize=11, fontweight="bold", color="green")
    ax.text(200, -55, "FINISH", ha="center", fontsize=11, fontweight="bold", color="red")

    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Lateral Position")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    out = FIG_DIR / "racing_strategy.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] {out.name}")


def main():
    print("=" * 55)
    print("  PHASE 7: Missing ASCE Diagrams")
    print("=" * 55)

    generators = [
        ("Hull Lines Plan", fig_lines_plan),
        ("Construction Sequence", fig_construction_sequence),
        ("Paddler Ergonomics", fig_paddler_ergonomics),
        ("Transportation Logistics", fig_transportation),
        ("Racing Strategy", fig_racing_strategy),
    ]

    for name, func in generators:
        print(f"\n  Generating {name}...")
        try:
            func()
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")
            import traceback; traceback.print_exc()

    print("\n  Phase 7 complete.")


if __name__ == "__main__":
    main()
