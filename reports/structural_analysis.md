# Structural Analysis
## NAU ASCE Concrete Canoe 2026 — Optimized Hull
*Generated: 2026-02-08 22:16*

---

## Section Properties — Midship Cross-Section

Thin-walled hollow rectangular section:

| Property | Value | Unit |
|----------|------:|------|
| Outer width (b) | 32.0 | in |
| Outer depth (h) | 17.0 | in |
| Inner width | 31.0 | in |
| Inner depth | 16.0 | in |
| Shell thickness (t) | 0.5 | in |
| Moment of inertia (Ix) | 2520.0 | in⁴ |
| Section modulus (Sx) | 296.5 | in³ |
| Neutral axis depth (c) | 8.50 | in |

### Calculation
```
Ix = (b_o × h_o³ - b_i × h_i³) / 12
   = (32.0 × 17.0³ - 31.0 × 16.0³) / 12
   = 2520.0 in⁴

Sx = Ix / c = 2520.0 / 8.50 = 296.5 in³
```

## Load Cases

### Load Case 1: Racing (4 Paddlers + Self-Weight) — CRITICAL

| Parameter | Value | Unit |
|-----------|------:|------|
| Hull self-weight | 224.8 | lbs |
| Distributed self-weight (w) | 14.05 | lb/ft |
| Crew (4 × 175 lbs) | 700 | lbs |
| Buoyancy load (uniform) | 57.80 | lb/ft (upward) |
| Paddler stations | 25%, 40%, 60%, 75% | of LOA |
| M from self-weight | 449.7 | lb·ft |
| M from paddler loads | 2394.0 | lb·ft |
| **Max bending moment** | **1646.7** | **lb·ft** |
| **Max bending moment** | **19760** | **lb·in** |
| **Flexural stress (σ)** | **66.7** | **psi** |
| Flexural strength (f'r) | 1500 | psi |
| **Safety factor (SF)** | **22.51** | — |

```
σ = M_max / Sx = 19760 / 296.5 = 66.7 psi
SF = f'r / σ = 1500 / 66.7 = 22.51
```

### Load Case 2: Lifting (2-Point Sling at 25% & 75%)

| Parameter | Value | Unit |
|-----------|------:|------|
| Lifting weight | 224.8 | lbs |
| Bending moment | 449.7 | lb·ft |
| Flexural stress | 18.2 | psi |
| Safety factor | 82.41 | — |

### Load Case 3: Punching Shear (Kneeling Paddler)

| Parameter | Value | Unit |
|-----------|------:|------|
| Paddler load | 175 | lbs |
| Contact area (6" × 6") | — | — |
| Punching shear stress | 14.6 | psi |

### Shear

| Parameter | Value | Unit |
|-----------|------:|------|
| Max shear force | 462.4 | lbs |
| Shear stress (τ) | 24.2 | psi |

## Safety Factor Summary

| Load Case | Stress (psi) | SF | Min Required | Status |
|-----------|------------:|----|-------------|--------|
| Racing (LC1) | 66.7 | 22.51 | ≥ 2.0 | ✓ PASS |
| Lifting (LC2) | 18.2 | 82.41 | ≥ 2.0 | ✓ PASS |

*Bending moment diagram: reports/figures/bending_moment.png*
