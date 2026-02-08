# SolidWorks Hull Specifications – NAU Canoe 2026

**Target design: Canoe 1 – 18' × 30" × 18", 276 lbs**

---

## 1. Overall Dimensions

| Parameter | Value | Notes |
|-----------|-------|-------|
| Length (LOA) | 216 inches | 18 feet |
| Beam (max) | 30 inches | At midship |
| Depth | 18 inches | Bow to gunwale at midship |
| Shell thickness | 0.5 inches | Verified in reinforcement calcs |
| Target weight | 276 lbs | Concrete + reinforcement |

---

## 2. Cross-Section Specifications (5 Stations)

| Station | % Length | Width (in) | Depth (in) | V-angle |
|---------|----------|------------|------------|---------|
| 0 (Bow) | 0% | 6 | 16 | 15° |
| 1 | 25% | 22 | 17 | 15° |
| 2 (Midship) | 50% | 30 | 18 | 15° |
| 3 | 75% | 22 | 17 | 15° |
| 4 (Stern) | 100% | 6 | 16 | 15° |

**V-bottom angle:** 15° from horizontal  
**Flare:** Sides flare 10° outward from vertical  

---

## 3. Rocker Curve

- **Radius:** 2.5 feet (30 inches) at bow and stern
- **Rise:** ~2 inches at ends (slight rocker for maneuverability)
- **Profile:** Smooth parabola or circular arc

---

## 4. Flare & Entry Angles

- **Flare angle:** 10° (sides flare out from vertical)
- **Bow/stern entry:** 15° from centerline
- **Keel line:** Slight V along length

---

## 5. Export for CNC Mold

- **Format:** DXF or STEP
- **Cross-sections:** Every 6 inches along length (37 sections for 216")
- **Units:** Inches
- **Layers:** Separate for mold halves if needed

---

## 6. Mass Properties Check

After modeling, verify in SolidWorks:

- **Mass:** ~276 lbs (concrete density ~60–65 pcf)
- **Center of gravity:** Approximately 45% of depth from keel
- **Volume:** Displacement ~4.4 ft³ at design waterline

---

*Use with HullGeometry from `calculations/concrete_canoe_calculator.py` for intermediate dimensions.*
