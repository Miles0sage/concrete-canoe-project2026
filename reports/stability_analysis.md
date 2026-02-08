# Stability Analysis
## NAU ASCE Concrete Canoe 2026 — Optimized Hull
*Generated: 2026-02-08 22:16*

---

## Metacentric Height Calculation

| Parameter | Value (ft) | Value (in) |
|-----------|----------:|----------:|
| Center of buoyancy (KB) | 0.2412 | 2.89 |
| Metacentric radius (BM) | 1.1089 | 13.31 |
| Center of gravity (KG) | 0.7616 | 9.14 |
| **Metacentric height (GM)** | **0.5885** | **7.06** |

### Calculation Detail
```
KB = Draft / 2
   = 0.4825 / 2
   = 0.2412 ft (2.89 in)

Iw = Ci × L × B³ / 12       (Ci = 0.65 for canoe hull form)
   = 0.65 × 16.00 × 2.667³ / 12
   = 16.4346 ft⁴

BM = Iw / ∇
   = 16.4346 / 14.821
   = 1.1089 ft (13.31 in)

KG = (W_hull × KG_hull + W_crew × KG_crew) / W_total
   = (224.8 × 0.538 + 700 × 0.833) / 924.8
   = 0.7616 ft (9.14 in)

GM = KB + BM - KG
   = 0.2412 + 1.1089 - 0.7616
   = 0.5885 ft = 7.06 in
```

## GM Verification

| Requirement | Value | Status |
|-------------|------:|--------|
| Minimum GM | 6.00 in | Required |
| Calculated GM | 7.06 in | ✓ PASS |
| Margin | +1.06 in | — |

## Righting Moments at Key Heel Angles

| Heel Angle | GZ (ft) | GZ (in) | Righting Moment (lb·ft) |
|:----------:|--------:|--------:|------------------------:|
| 10° | 0.1052 | 1.26 | 97.3 |
| 20° | 0.2264 | 2.72 | 209.4 |
| 30° | 0.3866 | 4.64 | 357.6 |

## GZ Curve Data (0°–90°)

| Angle (°) | GZ (ft) | GZ (in) |
|:----------:|--------:|--------:|
|   0 | 0.0000 | 0.00 |
|   5 | 0.0517 | 0.62 |
|  10 | 0.1052 | 1.26 |
|  15 | 0.1626 | 1.95 |
|  20 | 0.2264 | 2.72 |
|  25 | 0.2997 | 3.60 |
|  30 | 0.3866 | 4.64 |
|  35 | 0.4935 | 5.92 |
|  40 | 0.4209 | 5.05 |
|  45 | 0.2822 | 3.39 |
|  50 | 0.1414 | 1.70 |
|  55 | 0.0000 | 0.00 |
|  60 | 0.0000 | 0.00 |
|  65 | 0.0000 | 0.00 |
|  70 | 0.0000 | 0.00 |
|  75 | 0.0000 | 0.00 |
|  80 | 0.0000 | 0.00 |
|  85 | 0.0000 | 0.00 |
|  90 | 0.0000 | 0.00 |

*See: reports/figures/gz_curve.png*

## Interpretation
- Positive GM (7.06 in) confirms initial transverse stability.
- GZ remains positive well past 30°, providing strong capsize resistance.
- Wider beam (32 in) compared to original (30 in) is the primary stability driver.
