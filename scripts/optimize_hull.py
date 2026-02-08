#!/usr/bin/env python3
"""
NAU Concrete Canoe 2026 - Hull Dimension Optimizer
Finds optimal dimensions that minimize weight while meeting constraints.
Uses scipy.optimize. Run: pip install scipy tqdm
"""

import sys
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from calculations.concrete_canoe_calculator import run_complete_analysis
except ImportError:
    from concrete_canoe_calculator import run_complete_analysis

try:
    from scipy.optimize import minimize
    import numpy as np
except ImportError:
    print("Install: pip install scipy numpy")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda x, **kw: x


# Bounds: length 192-228", beam 28-36", depth 14-20"
BOUNDS = [(192, 228), (28, 36), (14, 20)]
THICKNESS = 0.5
FLEXURAL_PSI = 1500
MIN_FREEBOARD = 6.0
MIN_GM = 6.0
MIN_SF = 2.0


def weight_from_dimensions(L: float, B: float, D: float, t: float = 0.5) -> float:
    """Estimate concrete weight (lbs) from hull dimensions. Simplified surface area model."""
    surf_in2 = 2 * (L * D + B * D) + L * B
    vol_ft3 = surf_in2 * t / 1728
    return vol_ft3 * 60  # 60 pcf lightweight concrete


def objective(x: np.ndarray) -> float:
    """Minimize weight."""
    L, B, D = x
    return weight_from_dimensions(L, B, D, THICKNESS)


def constraints_g(x: np.ndarray) -> np.ndarray:
    """g(x) >= 0 for SLSQP ineq. We need fb>=6 so return fb-6."""
    L, B, D = x
    w = weight_from_dimensions(L, B, D, THICKNESS)
    try:
        r = run_complete_analysis(L, B, D, THICKNESS, w, FLEXURAL_PSI)
        fb = r["freeboard"]["freeboard_in"]
        gm = r["stability"]["gm_in"]
        sf = r["structural"]["safety_factor"]
        return np.array([fb - 6.0, gm - 6.0, sf - 2.0])
    except Exception:
        return np.array([-1e6, -1e6, -1e6])


def run_optimization(n_starts: int = 100) -> list:
    """Run optimization from multiple random starts. Returns top 10."""
    results = []
    np.random.seed(42)
    L0, L1 = BOUNDS[0]
    B0, B1 = BOUNDS[1]
    D0, D1 = BOUNDS[2]

    for _ in tqdm(range(n_starts), desc="Optimizing"):
        x0 = np.array([
            np.random.uniform(L0, L1),
            np.random.uniform(B0, B1),
            np.random.uniform(D0, D1),
        ])
        try:
            res = minimize(
                objective,
                x0,
                method="SLSQP",
                bounds=BOUNDS,
                constraints={"type": "ineq", "fun": constraints_g},
                options={"maxiter": 200},
            )
            if res.success:
                L, B, D = res.x
                w = weight_from_dimensions(L, B, D, THICKNESS)
                r = run_complete_analysis(L, B, D, THICKNESS, w, FLEXURAL_PSI)
                fb = r["freeboard"]["freeboard_in"]
                gm = r["stability"]["gm_in"]
                sf = r["structural"]["safety_factor"]
                if fb >= MIN_FREEBOARD and gm >= MIN_GM and sf >= MIN_SF:
                    results.append({
                        "length_in": L, "beam_in": B, "depth_in": D,
                        "weight_lbs": w, "freeboard_in": fb, "gm_in": gm,
                        "safety_factor": sf, "obj": res.fun,
                    })
        except Exception:
            pass

    results.sort(key=lambda x: x["weight_lbs"])
    return results[:10]


def main() -> int:
    print("NAU Canoe 2026 - Hull Optimizer")
    print("Constraints: Freeboard≥6\", GM≥6\", SF≥2")
    print("-" * 50)

    results = run_optimization(100)

    if not results:
        print("No feasible designs found. Try relaxing constraints.")
        return 1

    out_dir = PROJECT_ROOT / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "optimization_results.csv"

    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "length_in", "beam_in", "depth_in", "weight_lbs",
            "freeboard_in", "gm_in", "safety_factor", "obj",
        ])
        w.writeheader()
        w.writerows(results)

    print(f"\nTop {len(results)} designs (lightest first):")
    print(f"{'L(in)':>6} {'B(in)':>6} {'D(in)':>6} {'W(lbs)':>8} {'FB':>6} {'GM':>6} {'SF':>6}")
    print("-" * 50)
    for i, r in enumerate(results, 1):
        print(f"{r['length_in']:>6.0f} {r['beam_in']:>6.0f} {r['depth_in']:>6.0f} "
              f"{r['weight_lbs']:>8.1f} {r['freeboard_in']:>6.2f} {r['gm_in']:>6.2f} {r['safety_factor']:>6.2f}")

    print(f"\nSaved: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
