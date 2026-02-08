# SolidWorks Concrete Canoe Build Guide — Master Reference
## NAU ASCE Concrete Canoe 2026
*Recommended: Design A (192" × 32" × 17")*
*Generated: 2026-02-08*

---

## Quick Reference — 3 Available Designs

| Design | Dimensions | Weight | Use Case |
|--------|-----------|--------|----------|
| **A (Recommended)** | 192" × 32" × 17" | ~225 lbs | Lightest, meets all reqs |
| B (Conservative) | 196" × 34" × 18" | ~259 lbs | Extra safety margin |
| C (Speed) | 216" × 36" × 18" | ~296 lbs | Fastest hull speed |

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
6. Thicken surface to 0.5" (inward)
7. Verify mass properties
8. Export DXFs for CNC / STL for reference
```

## Key Settings

| Parameter | Value |
|-----------|-------|
| Unit system | IPS (inch, pound, second) |
| Shell thickness | 0.5" |
| Concrete density | 60.0 lb/ft³ = 0.034722 lb/in³ |
| Deadrise angle | 15° |
| Rocker | 0.8" max at midship |
| Sheer rise | 1.2" at bow/stern |

---
*NAU ASCE Concrete Canoe Team — 2026*
