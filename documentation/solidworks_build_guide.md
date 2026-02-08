# SolidWorks Hull Build Guide – NAU Canoe 2026

## Step-by-Step Instructions

### 1. Create Hull Using Loft Feature

1. **Create 5 reference planes** at 0%, 25%, 50%, 75%, 100% of 216" length  
2. **Sketch cross-sections** on each plane per `design/solidworks_specifications.md`  
3. **Loft** the 5 profiles with smooth tangency  
4. **Shell** the solid with 0.5" thickness (inside)

### 2. Cross-Section Sketch Guide

**At each station:**
- Draw centerline (vertical)
- V-bottom: two lines at 15° from horizontal, meeting at keel
- Add 10° flare on sides
- Dimensions from specs table

### 3. Verify Dimensions

- **Mass properties** → should be ~276 lbs  
- **Measure** length, beam, depth at key stations  
- Compare to Python calculator output

### 4. Export for CNC

1. Create planes every 6" along length  
2. **Intersect** hull with each plane → get cross-section curves  
3. **Export as DXF** (one file per section or combined)  
4. Save to `design/cad_exports/`

### 5. Common Issues

- **Loft fails:** Check that all profiles have same number of segments  
- **Shell fails:** Ensure no zero-thickness regions  
- **Mass too high:** Verify concrete density in material properties  

---

*Reference: `design/solidworks_specifications.md` for exact dimensions.*
