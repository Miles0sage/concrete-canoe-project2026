# Design Comparison: Original vs. Optimized
## NAU ASCE Concrete Canoe 2026
*Generated: 2026-02-08 22:16*

---

## Dimensions

| Parameter | Original | Optimized | Change |
|-----------|--------:|---------:|-------:|
| Length (in) | 216 | 192 | -24 |
| Beam (in) | 30 | 32 | +2 |
| Depth (in) | 18 | 17 | -1 |
| Weight (lbs) | 276 | 224.8 | -51.2 |

## Performance

| Requirement | Min. | Original | Status | Optimized | Status |
|-------------|-----:|---------:|--------|----------:|--------|
| Freeboard (in) | ≥ 6.0 | 6.21 | ✓ | 11.21 | ✓ |
| GM (in) | ≥ 6.0 | 4.16 | ✗ FAIL | 7.06 | ✓ |
| Safety factor | ≥ 2.0 | 308.22 | ✓ | 22.51 | ✓ |

## Improvements

| Metric | Value |
|--------|------:|
| Weight savings | **51.2 lbs** (18.5%) |
| Length reduction | 24 in |
| Beam increase | +2 in |
| Depth reduction | 1 in |

## Summary

**Original (216" × 30" × 18", 276 lbs):** Failed the GM ≥ 6" stability
requirement due to narrow beam and high center of gravity.

**Optimized (192" × 32" × 17", 225 lbs):** Passes all three ASCE
requirements. Key changes:
- **+2" beam** → BM ∝ B², greatly improves transverse stability
- **-24" length** → reduces weight while maintaining capacity
- **-1" depth** → lowers CG, improves stability
- **Net weight savings: 51 lbs** (19%)
