# Hydrostatic Analysis
## NAU ASCE Concrete Canoe 2026 — Optimized Hull
*Generated: 2026-02-08 22:16*

---

## Hull Parameters

| Parameter | Value | Unit |
|-----------|------:|------|
| Length (LOA) | 192 | in (16.0 ft) |
| Beam (max) | 32 | in (2.67 ft) |
| Depth | 17 | in (1.417 ft) |
| Shell thickness | 0.5 | in |
| Hull weight | 224.8 | lbs |

## Loading Condition — 4 Paddlers

| Parameter | Value | Unit |
|-----------|------:|------|
| Number of paddlers | 4 | — |
| Paddler weight (each) | 175 | lbs |
| Total crew weight | 700 | lbs |
| **Total loaded displacement** | **924.8** | **lbs** |

## Displacement & Draft

| Parameter | Value | Unit |
|-----------|------:|------|
| Water density (freshwater) | 62.4 | lb/ft³ |
| Displacement volume | 14.821 | ft³ |
| Waterplane coefficient (Cw) | 0.72 | — |
| Waterplane area (Aw) | 30.72 | ft² |
| **Draft** | **5.79** | **in (0.482 ft)** |
| **Freeboard** | **11.21** | **in (0.934 ft)** |

## Form Coefficients

| Coefficient | Value | Typical Range |
|-------------|------:|---------------|
| Block coefficient (Cb) | 0.720 | 0.35–0.55 |
| Midship coefficient (Cm) | 0.75 | 0.70–0.85 |
| Prismatic coefficient (Cp) | 0.960 | 0.55–0.70 |
| Waterplane coefficient (Cw) | 0.72 | 0.65–0.80 |
| Midship area (Am) | 0.965 | ft² |

## Freeboard Verification

| Requirement | Value | Status |
|-------------|------:|--------|
| Minimum freeboard | 6.00 in | Required |
| Calculated freeboard | 11.21 in | ✓ PASS |
| Margin | +5.21 in | — |

### Calculation Method
```
Displacement volume  = Total weight / Water density
                     = 924.8 lbs / 62.4 lb/ft³
                     = 14.821 ft³

Waterplane area      = Cw × L × B
                     = 0.72 × 16.00 ft × 2.667 ft
                     = 30.72 ft²

Draft                = Displacement / Waterplane area
                     = 14.821 / 30.72
                     = 0.4825 ft = 5.79 in

Freeboard            = Depth - Draft
                     = 17.0 in - 5.79 in
                     = 11.21 in ≥ 6.00 in  ✓
```
