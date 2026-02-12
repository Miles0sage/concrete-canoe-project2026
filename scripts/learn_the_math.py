#!/usr/bin/env python3
"""
NAU ASCE Concrete Canoe 2026 — "PLUTO JACKS" Design A
Learn the Math: Step-by-Step Engineering Tutorial

This script prints a complete walkthrough of the 7 core engineering
calculations for the concrete canoe project. It is NOT interactive --
just run it and read the output like a textbook that shows its work.

Each lesson:
  1. States the question in plain English
  2. Shows the formula
  3. Plugs in Design A numbers step by step
  4. Shows every intermediate calculation
  5. Shows the final answer
  6. Explains WHY each constant exists
  7. Shows the ASCE requirement and whether it passes

Design A Parameters:
  Length = 192 in (16 ft)    Beam = 32 in (2.667 ft)
  Depth  = 17 in (1.417 ft) Thickness = 0.5 in (0.0417 ft)
  Density = 60 PCF           Flexural strength = 1500 psi
  Crew = 4 x 175 = 700 lbs  Cwp = 0.70

Usage:
  python3 scripts/learn_the_math.py
"""

import math

# ──────────────────────────────────────────────────────────────
#  DESIGN A PARAMETERS
# ──────────────────────────────────────────────────────────────
L_in = 192.0        # Length (inches)
B_in = 32.0         # Beam / width (inches)
D_in = 17.0         # Depth (inches)
t_in = 0.5          # Wall thickness (inches)
density_pcf = 60.0  # Concrete density (lb/ft3)
f_r = 1500.0        # Flexural strength (psi) = modulus of rupture
crew_lbs = 700.0    # 4 paddlers x 175 lbs
Cwp = 0.70          # Waterplane coefficient
Cp = 0.55           # Prismatic coefficient
overhead = 1.10     # Hull weight overhead factor
WATER_DENSITY = 62.4  # Freshwater density (lb/ft3)

# Actual Design A hull weight (from detailed estimate)
HULL_WT = 174.26    # lbs (shell + reinforcement + finish)

# Convert to feet
L_ft = L_in / 12.0   # 16.0000 ft
B_ft = B_in / 12.0   # 2.6667 ft
D_ft = D_in / 12.0   # 1.4167 ft
t_ft = t_in / 12.0   # 0.0417 ft

W = 66  # print width


def banner(num, title, subtitle):
    """Print a lesson banner."""
    print()
    print()
    print(f"\u2554{'═' * (W - 2)}\u2557")
    print(f"\u2551  LESSON {num}: {title:<{W - 15}}\u2551")
    print(f"\u2551  {subtitle:<{W - 4}}\u2551")
    print(f"\u255A{'═' * (W - 2)}\u255D")
    print()


def check(label, value, op, threshold, unit=""):
    """Print a pass/fail check line."""
    if op == ">=":
        passed = value >= threshold
        symbol = ">="
    elif op == ">":
        passed = value > threshold
        symbol = ">"
    else:
        passed = value >= threshold
        symbol = ">="
    tag = "PASS" if passed else "FAIL"
    marker = "[PASS]" if passed else "[FAIL]"
    print(f"  {marker} {label}: {value:.2f}{unit} {symbol} {threshold:.1f}{unit}  --> {tag}")
    return passed


def section_break():
    """Print a thin separator."""
    print(f"  {'─' * (W - 4)}")


# ══════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════
print(f"\u2554{'═' * (W - 2)}\u2557")
print(f"\u2551{'':^{W - 2}}\u2551")
print(f"\u2551{'NAU ASCE Concrete Canoe 2026':^{W - 2}}\u2551")
print(f"\u2551{'\"PLUTO JACKS\" — Design A':^{W - 2}}\u2551")
print(f"\u2551{'Learn the Math: 7-Lesson Tutorial':^{W - 2}}\u2551")
print(f"\u2551{'':^{W - 2}}\u2551")
print(f"\u255A{'═' * (W - 2)}\u255D")
print()
print("  Design A Parameters:")
print(f"    Length:     {L_in:.0f} in  ({L_ft:.3f} ft)")
print(f"    Beam:       {B_in:.0f} in  ({B_ft:.3f} ft)")
print(f"    Depth:      {D_in:.0f} in  ({D_ft:.3f} ft)")
print(f"    Thickness:  {t_in:.1f} in  ({t_ft:.4f} ft)")
print(f"    Density:    {density_pcf:.0f} PCF")
print(f"    Flexural:   {f_r:.0f} psi")
print(f"    Crew:       4 x 175 = {crew_lbs:.0f} lbs")
print(f"    Cwp:        {Cwp:.2f}")


# ══════════════════════════════════════════════════════════════
#  LESSON 1: Hull Weight
# ══════════════════════════════════════════════════════════════
banner(1, "Hull Weight", '"How heavy is the canoe?"')

print("  Formula (geometry estimate):")
print("    girth      = beam + 2 x depth           (U-shape unfolded)")
print("    shell_area = girth x length x Cp         (prismatic taper)")
print("    volume     = shell_area x thickness")
print("    weight     = volume x density x overhead")
print()

girth = B_ft + 2.0 * D_ft
shell_area = girth * L_ft * Cp
volume = shell_area * t_ft
est_wt = volume * density_pcf * overhead

print("  Plugging in Design A numbers:")
print(f"    girth      = {B_ft:.3f} + 2 x {D_ft:.3f}")
print(f"               = {girth:.3f} ft")
print()
print(f"    shell_area = {girth:.3f} x {L_ft:.1f} x {Cp}")
print(f"               = {shell_area:.3f} ft2")
print()
print(f"    volume     = {shell_area:.3f} x {t_ft:.4f}")
print(f"               = {volume:.4f} ft3")
print()
print(f"    weight     = {volume:.4f} x {density_pcf:.1f} x {overhead:.2f}")
print(f"               = {est_wt:.2f} lbs  (geometry estimate)")
print()

section_break()
print()
print("  Actual Design A weight (detailed breakdown):")
print(f"    Shell concrete:      163.11 lbs")
print(f"    PVA reinforcement:     8.16 lbs")
print(f"    Surface finish:        3.00 lbs")
print(f"    {'─' * 30}")
print(f"    Total:               {HULL_WT:.2f} lbs")
print()
print(f"  The geometry estimate ({est_wt:.2f} lbs) is lower because it")
print(f"  models the hull as a simple U-shell. The actual weight")
print(f"  ({HULL_WT:.2f} lbs) includes thickened areas, reinforcement,")
print(f"  and surface finish. We use {HULL_WT:.2f} lbs for all")
print(f"  downstream calculations.")
print()

section_break()
print()
print("  Why each constant:")
print(f"    {Cp} (Cp)  = Prismatic coefficient. A canoe tapers at bow")
print(f"              and stern, so only ~55% of the full rectangular")
print(f"              surface is actual hull shell.")
print(f"    {overhead:.2f}       = 10% overhead for gunwales, keel thickening,")
print(f"              and reinforcement overlaps.")
print(f"    {density_pcf:.0f} PCF   = Lightweight concrete density. Normal concrete")
print(f"              is 150 PCF; our lightweight mix with glass")
print(f"              microspheres achieves 60 PCF.")


# ══════════════════════════════════════════════════════════════
#  LESSON 2: Draft
# ══════════════════════════════════════════════════════════════
banner(2, "Draft (How Deep It Sits)", '"How far does the canoe sink into the water?"')

print("  Concept: Archimedes' Principle")
print("    The canoe displaces a volume of water equal to its")
print("    total weight divided by water density.")
print()

print("  Formulas:")
print("    total_weight = hull_weight + crew_weight")
print("    displacement = total_weight / water_density     (ft3)")
print("    waterplane   = length x beam x Cwp              (ft2)")
print("    draft        = displacement / waterplane        (ft)")
print()

total_wt = HULL_WT + crew_lbs
disp_ft3 = total_wt / WATER_DENSITY
wp_ft2 = L_ft * B_ft * Cwp
draft_ft_calc = disp_ft3 / wp_ft2
draft_in_calc = draft_ft_calc * 12.0

print("  Step 1: Total loaded weight")
print(f"    total_weight = {HULL_WT:.2f} + {crew_lbs:.0f}")
print(f"                 = {total_wt:.2f} lbs")
print()

print("  Step 2: Displacement volume (Archimedes)")
print(f"    displacement = {total_wt:.2f} / {WATER_DENSITY}")
print(f"                 = {disp_ft3:.4f} ft3")
print()
print(f"    This means the canoe pushes {disp_ft3:.2f} cubic feet of")
print(f"    water out of the way to stay afloat.")
print()

print("  Step 3: Waterplane area")
print(f"    waterplane   = {L_ft:.1f} x {B_ft:.4f} x {Cwp}")
print(f"                 = {wp_ft2:.4f} ft2")
print()

print("  Step 4: Draft")
print(f"    draft        = {disp_ft3:.4f} / {wp_ft2:.4f}")
print(f"                 = {draft_ft_calc:.4f} ft")
print(f"                 = {draft_ft_calc:.4f} x 12")
print(f"                 = {draft_in_calc:.2f} inches")
print()

section_break()
print()
print("  Why each constant:")
print(f"    {WATER_DENSITY} lb/ft3 = Freshwater density at ~60 deg F.")
print(f"                  Saltwater is 64.0. We race in fresh water.")
print(f"    {Cwp} (Cwp)   = Waterplane coefficient. The canoe's waterline")
print(f"                  shape is an oval, not a rectangle. Only ~70%")
print(f"                  of (L x B) is actual waterplane area. Canoe")
print(f"                  hulls range Cwp = 0.65-0.75.")
print()

check("Draft", draft_in_calc, ">=", 0, '"')
print("  (Draft itself has no ASCE minimum; it feeds into freeboard.)")


# ══════════════════════════════════════════════════════════════
#  LESSON 3: Freeboard
# ══════════════════════════════════════════════════════════════
banner(3, "Freeboard", '"How much hull sticks up above the water?"')

print("  Formula:")
print("    freeboard = depth - draft")
print()
print("  This is the simplest calculation, but one of the most")
print("  important. If freeboard is too low, water splashes over")
print("  the sides and the canoe swamps.")
print()

fb_ft_calc = D_ft - draft_ft_calc
fb_in_calc = fb_ft_calc * 12.0

print("  Plugging in:")
print(f"    freeboard = {D_ft:.4f} - {draft_ft_calc:.4f}")
print(f"              = {fb_ft_calc:.4f} ft")
print(f"              = {fb_ft_calc:.4f} x 12")
print(f"              = {fb_in_calc:.2f} inches")
print()

section_break()
print()
print("  ASCE 2026 Requirement:")
check("Freeboard", fb_in_calc, ">=", 6.0, '"')
print()
print(f"  Margin: {fb_in_calc:.2f} - 6.00 = {fb_in_calc - 6.0:.2f} inches of margin")
print(f"  That is {(fb_in_calc - 6.0)/6.0*100:.0f}% above the minimum requirement.")


# ══════════════════════════════════════════════════════════════
#  LESSON 4: Metacentric Height (Stability)
# ══════════════════════════════════════════════════════════════
banner(4, "Metacentric Height (GM)", '"Will the canoe tip over?"')

print("  GM tells you how stable the canoe is when tilted.")
print("  A positive GM means the canoe rights itself. Bigger = more stable.")
print()
print("  Formula:")
print("    GM = KB + BM - KG")
print()
print("  Where:")
print("    KB = draft / 2              (center of buoyancy height)")
print("    BM = I_wp / V_disp          (metacentric radius)")
print("    KG = weighted COG height    (center of gravity)")
print()
print("  And:")
print("    I_wp   = Cwp x L x B^3 / 12   (2nd moment of waterplane)")
print("    V_disp = Cwp x L x B x T       (displaced volume)")
print("    KG     = (W_hull x COG_hull + W_crew x COG_crew) / W_total")
print()

# KB
KB = draft_ft_calc / 2.0
print("  Step 1: KB (center of buoyancy)")
print(f"    KB = {draft_ft_calc:.4f} / 2")
print(f"       = {KB:.4f} ft")
print()

# I_wp and V_disp
I_wp = Cwp * L_ft * B_ft**3 / 12.0
V_disp = Cwp * L_ft * B_ft * draft_ft_calc
BM = I_wp / V_disp
print("  Step 2: BM (metacentric radius)")
print(f"    I_wp   = {Cwp} x {L_ft:.1f} x {B_ft:.4f}^3 / 12")
print(f"           = {Cwp} x {L_ft:.1f} x {B_ft**3:.4f} / 12")
print(f"           = {I_wp:.4f} ft4")
print()
print(f"    V_disp = {Cwp} x {L_ft:.1f} x {B_ft:.4f} x {draft_ft_calc:.4f}")
print(f"           = {V_disp:.4f} ft3")
print()
print(f"    BM     = {I_wp:.4f} / {V_disp:.4f}")
print(f"           = {BM:.4f} ft")
print()

# KG (weighted COG)
hull_cog_ft = D_ft * 0.38
crew_cog_ft = 10.0 / 12.0
KG = (HULL_WT * hull_cog_ft + crew_lbs * crew_cog_ft) / total_wt
print("  Step 3: KG (center of gravity, weighted)")
print(f"    hull_cog = {D_ft:.4f} x 0.38 = {hull_cog_ft:.4f} ft")
print(f"               (empty hull COG is ~38% of depth from keel)")
print()
print(f"    crew_cog = 10.0 / 12 = {crew_cog_ft:.4f} ft")
print(f"               (kneeling paddler COG is ~10 inches up)")
print()
print(f"    KG = ({HULL_WT:.2f} x {hull_cog_ft:.4f} + {crew_lbs:.0f} x {crew_cog_ft:.4f})")
print(f"         / {total_wt:.2f}")
print(f"       = ({HULL_WT * hull_cog_ft:.4f} + {crew_lbs * crew_cog_ft:.4f})")
print(f"         / {total_wt:.2f}")
print(f"       = {HULL_WT * hull_cog_ft + crew_lbs * crew_cog_ft:.4f} / {total_wt:.2f}")
print(f"       = {KG:.4f} ft")
print()

# GM
GM_ft = KB + BM - KG
GM_in = GM_ft * 12.0
print("  Step 4: GM (metacentric height)")
print(f"    GM = KB + BM - KG")
print(f"       = {KB:.4f} + {BM:.4f} - {KG:.4f}")
print(f"       = {GM_ft:.4f} ft")
print(f"       = {GM_ft:.4f} x 12")
print(f"       = {GM_in:.2f} inches")
print()

section_break()
print()
print("  Why each constant:")
print(f"    0.38     = Hull COG fraction. For a U-shaped shell,")
print(f"               the center of mass is ~38% of depth up from")
print(f"               the keel (lower than 50% because the bottom")
print(f"               plate pulls the centroid down).")
print(f"    10 in    = Kneeling paddler COG. ASCE assumes paddlers")
print(f"               kneel, so their center of gravity is about")
print(f"               10 inches above the keel.")
print(f"    {Cwp}     = Same Cwp used for waterplane. The waterplane")
print(f"               and displaced volume share this coefficient,")
print(f"               so in BM = I/V, the L and Cwp terms partly")
print(f"               cancel, leaving BM ~ B^2 / (12T).")
print()

print("  ASCE 2026 Requirement:")
check("GM", GM_in, ">=", 6.0, '"')
print()
print(f"  Margin: {GM_in:.2f} - 6.00 = {GM_in - 6.0:.2f} inches above minimum")


# ══════════════════════════════════════════════════════════════
#  LESSON 5: Section Modulus
# ══════════════════════════════════════════════════════════════
banner(5, "Section Modulus", '"How strong is the hull cross-section?"')

print("  The section modulus S measures how well the cross-section")
print("  resists bending. Bigger S = stronger in bending.")
print()
print("  We model the hull as a thin-shell U-section (bottom plate")
print("  + two side walls), NOT a solid rectangle.")
print()
print("  Components:")
print("    Bottom plate: {b x t}          (wide, thin)")
print("    Two side walls: {t x h_wall}   (thin, tall)")
print()
print("  Formula:")
print("    1. Find each component's area and centroid")
print("    2. Find composite neutral axis y_NA")
print("    3. Use parallel axis theorem for total I")
print("    4. S = (I / c_max) x 0.75   (ACI thin-shell reduction)")
print()

b = B_in
t = t_in
d = D_in

# Bottom plate
a_bot = b * t
y_bot = t / 2.0
i_bot_self = b * t**3 / 12.0

print(f"  Step 1: Bottom plate ({b:.0f}\" wide x {t:.1f}\" thick)")
print(f"    A_bot    = {b:.0f} x {t:.1f} = {a_bot:.2f} in2")
print(f"    y_bot    = {t:.1f} / 2 = {y_bot:.4f} in  (centroid from bottom)")
print(f"    I_bot    = {b:.0f} x {t:.1f}^3 / 12 = {i_bot_self:.4f} in4")
print()

# Side walls
h_wall = d - t
a_wall = t * h_wall
y_wall = t + h_wall / 2.0
i_wall_self = t * h_wall**3 / 12.0

print(f"  Step 2: Each side wall ({t:.1f}\" thick x {h_wall:.2f}\" tall)")
print(f"    h_wall   = {d:.0f} - {t:.1f} = {h_wall:.2f} in")
print(f"    A_wall   = {t:.1f} x {h_wall:.2f} = {a_wall:.2f} in2  (each)")
print(f"    y_wall   = {t:.1f} + {h_wall:.2f}/2 = {y_wall:.4f} in  (centroid)")
print(f"    I_wall   = {t:.1f} x {h_wall:.2f}^3 / 12 = {i_wall_self:.4f} in4  (each)")
print()

# Composite neutral axis
total_area = a_bot + 2.0 * a_wall
y_na = (a_bot * y_bot + 2.0 * a_wall * y_wall) / total_area

print(f"  Step 3: Composite neutral axis")
print(f"    A_total  = {a_bot:.2f} + 2 x {a_wall:.2f} = {total_area:.2f} in2")
print(f"    y_NA     = ({a_bot:.2f} x {y_bot:.4f} + 2 x {a_wall:.2f} x {y_wall:.4f})")
print(f"               / {total_area:.2f}")
print(f"             = ({a_bot * y_bot:.4f} + {2 * a_wall * y_wall:.4f}) / {total_area:.2f}")
print(f"             = {a_bot * y_bot + 2 * a_wall * y_wall:.4f} / {total_area:.2f}")
print(f"             = {y_na:.4f} in from bottom")
print()

# Parallel axis theorem
I_total = (
    i_bot_self + a_bot * (y_na - y_bot)**2
    + 2.0 * (i_wall_self + a_wall * (y_wall - y_na)**2)
)

d_bot = y_na - y_bot
d_wall = y_wall - y_na

print(f"  Step 4: Parallel axis theorem (I = sum of I_self + A*d^2)")
print(f"    d_bot    = {y_na:.4f} - {y_bot:.4f} = {d_bot:.4f} in")
print(f"    d_wall   = {y_wall:.4f} - {y_na:.4f} = {d_wall:.4f} in")
print()
print(f"    I_bot_total  = {i_bot_self:.4f} + {a_bot:.2f} x {d_bot:.4f}^2")
i_bot_total = i_bot_self + a_bot * d_bot**2
print(f"                 = {i_bot_self:.4f} + {a_bot * d_bot**2:.4f}")
print(f"                 = {i_bot_total:.4f} in4")
print()
i_wall_total = i_wall_self + a_wall * d_wall**2
print(f"    I_wall_total = {i_wall_self:.4f} + {a_wall:.2f} x {d_wall:.4f}^2")
print(f"                 = {i_wall_self:.4f} + {a_wall * d_wall**2:.4f}")
print(f"                 = {i_wall_total:.4f} in4  (each)")
print()
print(f"    I_total  = {i_bot_total:.4f} + 2 x {i_wall_total:.4f}")
print(f"             = {I_total:.4f} in4")
print()

# Section modulus
c_top = d - y_na
c_bot = y_na
c_max = max(c_top, c_bot)
S_raw = I_total / c_max
S = S_raw * 0.75

print(f"  Step 5: Section modulus")
print(f"    c_top    = {d:.0f} - {y_na:.4f} = {c_top:.4f} in  (NA to top)")
print(f"    c_bot    = {y_na:.4f} in  (NA to bottom)")
print(f"    c_max    = max({c_top:.4f}, {c_bot:.4f}) = {c_max:.4f} in")
print()
print(f"    S_raw    = {I_total:.4f} / {c_max:.4f} = {S_raw:.4f} in3")
print()
print(f"    S_design = {S_raw:.4f} x 0.75 = {S:.2f} in3")
print()

section_break()
print()
print("  Why each constant:")
print(f"    0.75     = ACI 318 thin-shell reduction factor. Thin")
print(f"               concrete shells (t < 1\") are prone to local")
print(f"               buckling and microcracking that reduce the")
print(f"               effective section modulus. The 0.75 factor")
print(f"               accounts for this conservatively.")
print()
print(f"  Why NOT use S = b*h^2/6 (solid rectangle)?")
print(f"    A solid 32\"x17\" rectangle gives S = {b*d**2/6:.0f} in3.")
print(f"    But the canoe is hollow! Only the thin shell carries")
print(f"    load. The thin-shell model gives {S:.0f} in3 -- about")
print(f"    {S / (b*d**2/6) * 100:.0f}x smaller. Using the solid formula")
print(f"    would dangerously overestimate structural capacity.")


# ══════════════════════════════════════════════════════════════
#  LESSON 6: Bending Moment
# ══════════════════════════════════════════════════════════════
banner(6, "Bending Moment", '"How hard is the canoe being bent?"')

print("  The canoe is modeled as a simply-supported beam with:")
print("    - Hull self-weight as a uniform distributed load (UDL)")
print("    - Crew weight as a point load at midspan")
print()
print("  Formulas:")
print("    w_hull = hull_weight / length            (lb/ft)")
print("    M_hull = w_hull x L^2 / 8               (UDL midspan)")
print("    M_crew = P_crew x L / 4                  (point load midspan)")
print("    M_total = M_hull + M_crew")
print()

w_hull = HULL_WT / L_ft
M_hull = w_hull * L_ft**2 / 8.0
M_crew = crew_lbs * L_ft / 4.0
M_total = M_hull + M_crew

print(f"  Step 1: Hull distributed load")
print(f"    w_hull   = {HULL_WT:.2f} / {L_ft:.1f}")
print(f"             = {w_hull:.4f} lb/ft")
print()

print(f"  Step 2: Hull bending moment (UDL: M = wL^2/8)")
print(f"    M_hull   = {w_hull:.4f} x {L_ft:.1f}^2 / 8")
print(f"             = {w_hull:.4f} x {L_ft**2:.2f} / 8")
print(f"             = {M_hull:.2f} lb-ft")
print()

print(f"  Step 3: Crew bending moment (point load: M = PL/4)")
print(f"    M_crew   = {crew_lbs:.0f} x {L_ft:.1f} / 4")
print(f"             = {M_crew:.2f} lb-ft")
print()

print(f"  Step 4: Total bending moment")
print(f"    M_total  = {M_hull:.2f} + {M_crew:.2f}")
print(f"             = {M_total:.2f} lb-ft")
print()

section_break()
print()
print("  Why these formulas?")
print(f"    wL^2/8  = Classic beam formula for max moment of a")
print(f"              uniformly distributed load on a simply-")
print(f"              supported beam. The hull's own weight is")
print(f"              spread along the whole length.")
print(f"    PL/4    = Classic formula for max moment of a point")
print(f"              load at midspan. Crew weight concentrates")
print(f"              amidships where all 4 paddlers sit.")
print()
print(f"  Conservative assumption: simple supports at bow and")
print(f"  stern. In reality, the water provides continuous buoyant")
print(f"  support, which reduces the moment by ~20-40%. This model")
print(f"  is intentionally conservative for safety.")


# ══════════════════════════════════════════════════════════════
#  LESSON 7: Bending Stress & Safety Factor
# ══════════════════════════════════════════════════════════════
banner(7, "Bending Stress & Safety Factor", '"Will the canoe break?"')

print("  This is the final check. We compare the bending stress")
print("  in the hull to the concrete's flexural strength.")
print()
print("  Formulas:")
print("    sigma = M / S      (bending stress, with M in lb-in)")
print("    SF    = f_r / sigma (safety factor)")
print()

M_total_lb_in = M_total * 12.0
sigma = M_total_lb_in / S
sf = f_r / sigma

print(f"  Step 1: Convert moment to lb-in")
print(f"    M_total  = {M_total:.2f} lb-ft x 12")
print(f"             = {M_total_lb_in:.2f} lb-in")
print()

print(f"  Step 2: Bending stress (sigma = M / S)")
print(f"    sigma    = {M_total_lb_in:.2f} / {S:.2f}")
print(f"             = {sigma:.2f} psi")
print()

print(f"  Step 3: Safety factor (SF = f_r / sigma)")
print(f"    SF       = {f_r:.0f} / {sigma:.2f}")
print(f"             = {sf:.4f}")
print()

section_break()
print()
print("  Interpretation:")
print(f"    The hull experiences {sigma:.0f} psi of bending stress,")
print(f"    but the concrete can handle {f_r:.0f} psi before it cracks.")
print(f"    That means we have a {sf:.1f}x safety margin -- the hull")
print(f"    can take {sf:.1f} times the design load before failure.")
print()
print("  ASCE 2026 Requirement:")
check("Safety Factor", sf, ">=", 2.0, "")
print()
print(f"  Margin: {sf:.4f} - 2.0 = {sf - 2.0:.4f} above minimum")
print(f"  That is {(sf - 2.0)/2.0*100:.1f}% above the ASCE requirement.")


# ══════════════════════════════════════════════════════════════
#  SUMMARY
# ══════════════════════════════════════════════════════════════
print()
print()
print(f"\u2554{'═' * (W - 2)}\u2557")
print(f"\u2551{'SUMMARY — Design A Results':^{W - 2}}\u2551")
print(f"\u255A{'═' * (W - 2)}\u255D")
print()
print(f"  {'Parameter':<28} {'Value':>12}  {'Unit':<8}")
print(f"  {'─' * 52}")
print(f"  {'Hull Weight':<28} {HULL_WT:>12.2f}  {'lbs':<8}")
print(f"  {'Draft':<28} {draft_in_calc:>12.2f}  {'in':<8}")
print(f"  {'Freeboard':<28} {fb_in_calc:>12.2f}  {'in':<8}")
print(f"  {'Metacentric Height (GM)':<28} {GM_in:>12.2f}  {'in':<8}")
print(f"  {'Section Modulus (S)':<28} {S:>12.2f}  {'in3':<8}")
print(f"  {'Bending Moment (M)':<28} {M_total:>12.2f}  {'lb-ft':<8}")
print(f"  {'Bending Stress (sigma)':<28} {sigma:>12.2f}  {'psi':<8}")
print(f"  {'Safety Factor (SF)':<28} {sf:>12.4f}  {'':<8}")
print()
print(f"  {'ASCE 2026 Compliance Checks':}")
print(f"  {'─' * 52}")
check("Freeboard >= 6 in", fb_in_calc, ">=", 6.0, '"')
check("GM >= 6 in", GM_in, ">=", 6.0, '"')
check("Safety Factor >= 2.0", sf, ">=", 2.0, "")
print()
overall = fb_in_calc >= 6.0 and GM_in >= 6.0 and sf >= 2.0
tag = "ALL CHECKS PASS" if overall else "SOME CHECKS FAIL"
print(f"  >>> {tag} <<<")
print()


# ══════════════════════════════════════════════════════════════
#  BONUS LESSON 8: ACI 318 Shear Check (Trevion's Method)
# ══════════════════════════════════════════════════════════════
banner("8 (BONUS)", "ACI 318 Shear Capacity", '"Can the hull resist shear forces?" (Trevion\'s method)')

print("  This bonus lesson uses ACI 318 concrete and steel shear")
print("  provisions. Trevion's Excel spreadsheet uses these formulas")
print("  with PVA fiber reinforcement modeled as distributed shear steel.")
print()

print("  Formulas:")
print("    Vc   = 2 x (density/150) x sqrt(f'c) x bw x d")
print("    Vs   = Av x fy x d / s")
print("    phiVn = 0.75 x (Vc + Vs)")
print()

print("  Where:")
print("    Vc   = Concrete shear capacity (lbs)")
print("    Vs   = Steel (PVA fiber) shear capacity (lbs)")
print("    phiVn = Design shear capacity (with phi = 0.75)")
print()

# Trevion's inputs
dens_s = 70.0       # PCF (his mix)
fc_s = 1500.0       # psi (compressive strength)
bw_s = 1.0          # in (unit width strip)
d_s = 13.1453       # in (effective depth)
Av_s = 0.0017       # in2 (PVA fiber area per unit width)
fy_s = 80000.0      # psi (PVA fiber tensile strength)
s_s = 0.875         # in (fiber spacing)

print("  Trevion's inputs:")
print(f"    density  = {dens_s:.0f} PCF")
print(f"    f'c      = {fc_s:.0f} psi")
print(f"    bw       = {bw_s:.1f} in  (unit width strip)")
print(f"    d        = {d_s:.4f} in  (effective depth)")
print(f"    Av       = {Av_s:.4f} in2  (PVA fiber area)")
print(f"    fy       = {fy_s:.0f} psi  (PVA tensile strength)")
print(f"    s        = {s_s:.3f} in  (fiber spacing)")
print()

section_break()
print()

# Vc
lambda_factor = dens_s / 150.0
sqrt_fc = math.sqrt(fc_s)
Vc = 2.0 * lambda_factor * sqrt_fc * bw_s * d_s

print("  Step 1: Concrete shear capacity (Vc)")
print(f"    lambda   = density / 150 = {dens_s:.0f} / 150")
print(f"             = {lambda_factor:.6f}")
print()
print(f"    sqrt(f'c) = sqrt({fc_s:.0f})")
print(f"              = {sqrt_fc:.6f}")
print()
print(f"    Vc = 2 x {lambda_factor:.6f} x {sqrt_fc:.6f} x {bw_s:.1f} x {d_s:.4f}")
print(f"       = {Vc:.2f} lbs")
print()

# Vs
Vs = Av_s * fy_s * d_s / s_s

print("  Step 2: Fiber shear capacity (Vs)")
print(f"    Vs = {Av_s:.4f} x {fy_s:.0f} x {d_s:.4f} / {s_s:.3f}")
print(f"       = {Av_s * fy_s:.2f} x {d_s:.4f} / {s_s:.3f}")
print(f"       = {Av_s * fy_s * d_s:.2f} / {s_s:.3f}")
print(f"       = {Vs:.2f} lbs")
print()

# phiVn
phiVn = 0.75 * (Vc + Vs)

print("  Step 3: Design shear capacity (phiVn)")
print(f"    phiVn = 0.75 x (Vc + Vs)")
print(f"         = 0.75 x ({Vc:.2f} + {Vs:.2f})")
print(f"         = 0.75 x {Vc + Vs:.2f}")
print(f"         = {phiVn:.2f} lbs")
print()

section_break()
print()
print("  Verification against Trevion's Excel:")
print(f"    Python Vc    = {Vc:.2f}     Excel Vc    = 475.17")
print(f"    Python Vs    = {Vs:.2f}    Excel Vs    = 2043.16")
print(f"    Python phiVn = {phiVn:.2f}    Excel phiVn = 1888.75")

# Check match
vc_err = abs(Vc - 475.17) / 475.17 * 100
vs_err = abs(Vs - 2043.16) / 2043.16 * 100
phi_err = abs(phiVn - 1888.75) / 1888.75 * 100
print()
print(f"    Vc  error:   {vc_err:.4f}%")
print(f"    Vs  error:   {vs_err:.4f}%")
print(f"    phiVn error: {phi_err:.4f}%")
print()
if max(vc_err, vs_err, phi_err) < 0.01:
    print("    >>> Python matches Excel to within 0.01% <<<")
else:
    print(f"    >>> Max error: {max(vc_err, vs_err, phi_err):.4f}% <<<")
print()

print("  Why each constant:")
print(f"    2        = ACI 318 Eq. 22.5.5.1 coefficient for shear")
print(f"               in members without shear reinforcement design.")
print(f"    150      = Normal-weight concrete density (PCF). The")
print(f"               ratio density/150 is ACI's lambda factor for")
print(f"               lightweight concrete (reduces shear capacity")
print(f"               because lightweight aggregate has weaker")
print(f"               interlock at cracks).")
print(f"    sqrt(f'c)= Concrete tensile strength is roughly")
print(f"               proportional to the square root of f'c.")
print(f"    0.75     = ACI 318 strength reduction factor (phi) for")
print(f"               shear. Shear failures are sudden and brittle,")
print(f"               so ACI requires a larger safety margin than")
print(f"               for flexure (phi=0.90).")
print(f"    80,000   = PVA fiber tensile strength (psi). Much higher")
print(f"               than rebar (~60,000) because PVA fibers are")
print(f"               synthetic polymer strands.")


# ══════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════
print()
print()
print(f"\u2554{'═' * (W - 2)}\u2557")
print(f"\u2551{'':^{W - 2}}\u2551")
print(f"\u2551{'END OF TUTORIAL':^{W - 2}}\u2551")
print(f"\u2551{'NAU ASCE Concrete Canoe 2026 — Design A':^{W - 2}}\u2551")
print(f"\u2551{'All 7 lessons + bonus shear check complete.':^{W - 2}}\u2551")
print(f"\u2551{'':^{W - 2}}\u2551")
print(f"\u255A{'═' * (W - 2)}\u255D")
print()
