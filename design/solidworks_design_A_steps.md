# SolidWorks Build Guide — Design A
## NAU ASCE Concrete Canoe 2026
*Design A — Optimal (Lightest)*
*Dimensions: 192" × 32" × 17", Shell: 0.5"*
*Target weight: 224.8 lbs*

---

## Prerequisites
- SolidWorks 2020 or newer
- Units: IPS (Inch, Pound, Second)
- Estimated time: 2–3 hours

---

## Step 1: Create New Part & Set Units

1. **File → New → Part**
2. **Tools → Options → Document Properties → Units**
   - Unit system: **IPS** (inch, pound, second)
   - Length decimals: 3
3. Save as `CanoeHull_DesignA.SLDPRT`

> The part opens with Front, Top, and Right planes plus the Origin.

---

## Step 2: Create Reference Planes

You need 5 cross-section planes perpendicular to the hull length axis.
The hull lies along the **Top plane** with length in the X direction.

1. Select the **Front Plane**
2. **Insert → Reference Geometry → Plane**
3. Create offset planes:

| Plane Name | Offset from Front | Station |
|------------|------------------:|---------|
| Bow | 0" | 0% |
| Fwd Quarter | 48" | 25% |
| Midship | 96" | 50% |
| Aft Quarter | 144" | 75% |
| Stern | 192" | 100% |

> Rename each plane in the Feature Tree for clarity.

---

## Step 3: Sketch Cross-Sections

On each reference plane, sketch the hull cross-section profile.
All coordinates use X = athwartship (beam), Y = vertical (depth).
Origin (0,0) = keel centerline at bottom.


### Station at 0" — Bow
- **Plane:** Offset 0" from bow reference
- **Shape:** Point (hull converges to keel)
- **Coordinates:** (0, 0) — single point at keel


### Station at 48" — Forward Quarter
- **Plane:** Offset 48" from bow reference
- **Beam at waterline:** 22.6"
- **Deadrise angle:** 15°

| Point | X (in) | Y (in) | Description |
|-------|-------:|-------:|-------------|
| 1 | -11.31 | 17.00 | Port gunwale |
| 2 | -11.31 | 3.03 | Port chine |
| 3 | 0.00 | 0.00 | Keel (centerline) |
| 4 | 11.31 | 3.03 | Starboard chine |
| 5 | 11.31 | 17.00 | Starboard gunwale |

**Sketch:** Connect points 1→2→3→4→5 with lines. Add fillets (R=0.5") at chine points 2 and 4.


### Station at 96" — Midship
- **Plane:** Offset 96" from bow reference
- **Beam at waterline:** 32.0"
- **Deadrise angle:** 15°

| Point | X (in) | Y (in) | Description |
|-------|-------:|-------:|-------------|
| 1 | -16.00 | 17.00 | Port gunwale |
| 2 | -16.00 | 4.29 | Port chine |
| 3 | 0.00 | 0.00 | Keel (centerline) |
| 4 | 16.00 | 4.29 | Starboard chine |
| 5 | 16.00 | 17.00 | Starboard gunwale |

**Sketch:** Connect points 1→2→3→4→5 with lines. Add fillets (R=0.5") at chine points 2 and 4.


### Station at 144" — Aft Quarter
- **Plane:** Offset 144" from bow reference
- **Beam at waterline:** 22.6"
- **Deadrise angle:** 15°

| Point | X (in) | Y (in) | Description |
|-------|-------:|-------:|-------------|
| 1 | -11.31 | 17.00 | Port gunwale |
| 2 | -11.31 | 3.03 | Port chine |
| 3 | 0.00 | 0.00 | Keel (centerline) |
| 4 | 11.31 | 3.03 | Starboard chine |
| 5 | 11.31 | 17.00 | Starboard gunwale |

**Sketch:** Connect points 1→2→3→4→5 with lines. Add fillets (R=0.5") at chine points 2 and 4.


### Station at 192" — Stern
- **Plane:** Offset 192" from bow reference
- **Shape:** Point (hull converges to keel)
- **Coordinates:** (0, 0) — single point at keel



### Sketch Tips
- Use **Mirror** about the centerline (X=0) to ensure symmetry
- Add **Symmetric** relations between port and starboard points
- Fully constrain each sketch (green checkmark)
- Use **Construction Line** on centerline for mirror reference

---

## Step 4: Create Guide Curves

### Keel Curve (Bottom Profile)
1. Create a sketch on the **Right Plane**
2. Draw a spline from (0, 0) to (192, 0) with rocker:
   - Midpoint rises ~0.8" above endpoints
   - Add tangent constraints at bow and stern (horizontal)
3. Points along keel:

| X (in) | Y (in) |
|-------:|-------:|
| 0 | 0.00 |
| 48 | 0.60 |
| 96 | 0.80 |
| 144 | 0.60 |
| 192 | 0.00 |

### Sheer Curve (Gunwale Profile)
1. On same sketch or new Right Plane sketch
2. Spline through gunwale edges:

| X (in) | Y (in) |
|-------:|-------:|
| 0 | 18.2 |
| 48 | 17.0 |
| 96 | 16.8 |
| 144 | 17.0 |
| 192 | 18.2 |

---

## Step 5: Loft the Hull Surface

1. **Insert → Surface → Lofted Surface**
2. Select profiles in order: Bow → Fwd Quarter → Midship → Aft Quarter → Stern
3. Select guide curves: Keel and Sheer
4. Options:
   - Start constraint: **Normal to Profile**
   - End constraint: **Normal to Profile**
   - Tangent length: 1.0
5. Click **OK** (green check)

> **What you see:** A smooth hull surface stretching from bow to stern with
> V-bottom cross-sections that taper at the ends.

### Troubleshooting
- **"Loft failed"**: Ensure all sketches are on separate planes and fully defined
- **Twisted surface**: Check that profile selection order matches physical sequence
- **Sharp edges**: Increase tangent length or add intermediate stations

---

## Step 6: Create Shell (Add Thickness)

1. Select the lofted surface body
2. **Insert → Surface → Thicken**
3. Settings:
   - Thickness: **0.5"** (0.5 inch)
   - Direction: **Inward** (thicken toward inside of hull)
4. Click OK

> **Alternatively** (if Thicken fails):
> 1. **Insert → Surface → Offset Surface** — offset 0.5" inward
> 2. **Insert → Surface → Knit Surface** — knit all surfaces into solid
> 3. Cap the open gunwale edge with a planar surface

---

## Step 7: Verify Mass Properties

1. **Tools → Mass Properties**
2. Set material density:
   - **Apply/Edit Material → Custom**
   - Density: **0.961111 lb/in³** (60.0 lb/ft³)
3. Expected values:
   - **Volume:** ~6474 in³
   - **Mass:** ~225 lbs (concrete only)
   - Add 17 lbs for reinforcement/hardware = **225 lbs total**

> If mass differs by >10%: check shell thickness is 0.5" everywhere,
> verify no gaps in the surface.

---

## Step 8: Export for CNC Mold Cutting

### Export Cross-Section DXFs
1. For each station plane:
   - Right-click plane → **Create Sketch From**
   - Use **Intersection Curve** to get the hull outline at that station
   - **File → Save As → DXF** (select "Export 2D")
2. Name files: `Station_00.dxf`, `Station_25.dxf`, etc.

### Export Full Hull STL (for reference)
1. **File → Save As → STL**
2. Resolution: Fine (deviation 0.01", angle 5°)

### CNC Station Coordinates
See: `design/dxf_coords_design_A.txt` for all station coordinates
at 6" spacing (32 stations total).

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| Loft self-intersects | Add more intermediate cross-sections |
| Shell fails at bow/stern | Taper cross-sections more gradually at ends |
| Asymmetric hull | Use Mirror feature about centerline plane |
| Wrong weight | Verify density units (lb/in³ not lb/ft³) |
| Surface gaps | Use Knit Surface before thickening |
| File too large | Reduce spline points, use lower mesh quality |

---

*Generated for NAU ASCE Concrete Canoe 2026 Competition*
*Design A: 192" × 32" × 17"*
