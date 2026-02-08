#!/usr/bin/env python3
"""3 Alternative Designs with Full Visualizations - Qwen Enhanced"""

import sys
sys.path.insert(0, '/root/concrete-canoe-project2026')

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from calculations.concrete_canoe_calculator import (
    HullGeometry,
    HydrostaticAnalysis,
    StabilityAnalysis,
    StructuralAnalysis
)

print("="*70)
print("GENERATING 3 ALTERNATIVE DESIGNS - QWEN VERSION")
print("="*70)

# DESIGN SPECIFICATIONS
designs = {
    'A': {
        'name': 'Design A - Optimal (Lightest)',
        'length': 192,
        'beam': 32,
        'depth': 17,
        'thickness': 0.5,
        'color': '#3498db',
        'description': 'Minimum weight while meeting requirements'
    },
    'B': {
        'name': 'Design B - Conservative (Safety Margin)',
        'length': 196,
        'beam': 34,
        'depth': 18,
        'thickness': 0.5,
        'color': '#e74c3c',
        'description': 'Extra safety margin on all requirements'
    },
    'C': {
        'name': 'Design C - Traditional (Easier Construction)',
        'length': 216,
        'beam': 36,
        'depth': 18,
        'thickness': 0.5,
        'color': '#2ecc71',
        'description': 'Standard proportions, easier to paddle straight'
    }
}

# CALCULATE METRICS FOR ALL DESIGNS
design_metrics = {}

for key, d in designs.items():
    hull = HullGeometry(d['length'], d['beam'], d['depth'], d['thickness'])
    volume_ft3 = hull.calculate_hull_volume() / 1728.0
    weight = volume_ft3 * 60.0
    
    hydro = HydrostaticAnalysis(hull)
    fb_results = hydro.calculate_freeboard(weight, 4, 175.0)
    
    stab = StabilityAnalysis(hull)
    gm_results = stab.calculate_metacentric_height(weight, 4, 175.0)
    
    struct = StructuralAnalysis(hull)
    adequacy = struct.check_structural_adequacy(weight, 1500.0, 2.0)
    
    design_metrics[key] = {
        'name': d['name'],
        'length': d['length'],
        'beam': d['beam'],
        'depth': d['depth'],
        'weight': weight,
        'freeboard': fb_results['freeboard_in'],
        'gm': gm_results['GM_in'],
        'safety_factor': adequacy['actual_safety_factor'],
        'fb_pass': fb_results['freeboard_in'] >= 6.0,
        'gm_pass': gm_results['GM_in'] >= 6.0,
        'sf_pass': adequacy['is_adequate'],
        'all_pass': (fb_results['freeboard_in'] >= 6.0 and 
                    gm_results['GM_in'] >= 6.0 and 
                    adequacy['is_adequate']),
        'color': d['color'],
        'description': d['description']
    }

# CONSOLE SUMMARY
print("\n" + "="*70)
print("DESIGN COMPARISON TABLE")
print("="*70)
print(f"{'Design':<12} {'Dimensions':<18} {'Weight':<10} {'FB':<8} {'GM':<8} {'SF':<8} {'Status'}")
print("-"*70)

for key, m in design_metrics.items():
    dims = f"{m['length']}×{m['beam']}×{m['depth']}\""
    status = "✓ PASS" if m['all_pass'] else "✗ FAIL"
    print(f"{key:<12} {dims:<18} {m['weight']:<10.1f} {m['freeboard']:<8.2f} {m['gm']:<8.2f} {m['safety_factor']:<8.1f} {status}")

# FIGURE 1: SIDE-BY-SIDE PROFILES
print("\nGenerating Figure 1: Side-by-side hull profiles...")
fig1, axes1 = plt.subplots(1, 3, figsize=(20, 6))
fig1.suptitle('Hull Profiles - Side View Comparison', fontsize=16, fontweight='bold')

for idx, (key, m) in enumerate(design_metrics.items()):
    ax = axes1[idx]
    
    # Create hull profile with rocker
    x = np.linspace(0, m['length'], 200)
    rocker = 3 * np.sin(np.pi * x / m['length'])
    
    # Draw hull
    ax.fill_between(x, rocker, rocker + m['depth'], alpha=0.3, color=m['color'], label='Hull')
    ax.plot(x, rocker, color=m['color'], linewidth=3, label='Keel')
    ax.plot(x, rocker + m['depth'], color=m['color'], linewidth=3, label='Gunwale')
    
    # Waterline
    waterline_y = rocker + m['depth'] - m['freeboard']
    ax.plot(x, waterline_y, 'c--', linewidth=2, label='Waterline')
    
    # Paddler positions
    paddler_pos = [0.25, 0.375, 0.625, 0.75]
    for p in paddler_pos:
        px = p * m['length']
        py = rocker[int(p * 200)] + m['depth'] + 5
        ax.plot(px, py, 'ro', markersize=8)
    
    ax.set_title(f"Design {key}: {m['name'].split(' - ')[1]}\n{m['weight']:.0f} lbs", 
                 fontsize=12, fontweight='bold')
    ax.set_xlabel('Length (inches)', fontsize=10)
    ax.set_ylabel('Height (inches)', fontsize=10)
    ax.legend(fontsize=8, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, m['length'])

plt.tight_layout()
plt.savefig('reports/figures/3_designs_side_by_side.png', dpi=300, bbox_inches='tight')
print("✓ Saved: reports/figures/3_designs_side_by_side.png")

# FIGURE 2: CROSS-SECTIONS
print("Generating Figure 2: Cross-section comparison...")
fig2, axes2 = plt.subplots(1, 3, figsize=(20, 6))
fig2.suptitle('Hull Cross-Sections at Midship', fontsize=16, fontweight='bold')

for idx, (key, m) in enumerate(design_metrics.items()):
    ax = axes2[idx]
    
    half_beam = m['beam'] / 2
    v_angle = 7.5  # degrees
    v_notch = half_beam * np.tan(np.radians(v_angle))
    
    # Outer shell
    outer_x = [-half_beam, -half_beam, 0, half_beam, half_beam, -half_beam]
    outer_y = [0, m['depth'], m['depth'] - v_notch, m['depth'], 0, 0]
    ax.fill(outer_x, outer_y, alpha=0.3, color=m['color'], label='Shell')
    ax.plot(outer_x, outer_y, color=m['color'], linewidth=3)
    
    # Inner shell
    inner_half = half_beam - m['thickness']
    inner_depth = m['depth'] - m['thickness']
    inner_notch = v_notch - m['thickness'] * 0.5
    inner_x = [-inner_half, -inner_half, 0, inner_half, inner_half, -inner_half]
    inner_y = [m['thickness'], inner_depth, inner_depth - inner_notch, inner_depth, m['thickness'], m['thickness']]
    ax.fill(inner_x, inner_y, color='white', label='Hollow')
    ax.plot(inner_x, inner_y, 'k--', linewidth=2)
    
    # Waterline
    waterline = m['depth'] - m['freeboard']
    ax.axhline(waterline, color='cyan', linewidth=2, linestyle='--', label='Waterline')
    
    ax.set_title(f"Design {key}: {m['beam']}\" × {m['depth']}\"\nV-angle: {v_angle*2}°", 
                 fontsize=12, fontweight='bold')
    ax.set_xlabel('Width (inches)', fontsize=10)
    ax.set_ylabel('Height (inches)', fontsize=10)
    ax.set_aspect('equal')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('reports/figures/3_designs_cross_sections.png', dpi=300, bbox_inches='tight')
print("✓ Saved: reports/figures/3_designs_cross_sections.png")

# FIGURE 3: PERFORMANCE BARS
print("Generating Figure 3: Performance comparison bars...")
fig3, axes3 = plt.subplots(2, 2, figsize=(14, 10))
fig3.suptitle('Performance Metrics Comparison', fontsize=16, fontweight='bold')

labels = ['A', 'B', 'C']
colors = [design_metrics[k]['color'] for k in labels]

# Weight
axes3[0,0].bar(labels, [design_metrics[k]['weight'] for k in labels], color=colors)
axes3[0,0].axhline(237, color='red', linestyle='--', linewidth=2, label='Target: 237 lbs')
axes3[0,0].set_title('Weight (lighter = better)', fontweight='bold')
axes3[0,0].set_ylabel('Weight (lbs)')
axes3[0,0].legend()
axes3[0,0].grid(True, alpha=0.3, axis='y')

# Freeboard
axes3[0,1].bar(labels, [design_metrics[k]['freeboard'] for k in labels], color=colors)
axes3[0,1].axhline(6.0, color='red', linestyle='--', linewidth=2, label='Required: ≥6.0"')
axes3[0,1].set_title('Freeboard (higher = better)', fontweight='bold')
axes3[0,1].set_ylabel('Freeboard (inches)')
axes3[0,1].legend()
axes3[0,1].grid(True, alpha=0.3, axis='y')

# GM
axes3[1,0].bar(labels, [design_metrics[k]['gm'] for k in labels], color=colors)
axes3[1,0].axhline(6.0, color='red', linestyle='--', linewidth=2, label='Required: ≥6.0"')
axes3[1,0].set_title('Metacentric Height (higher = more stable)', fontweight='bold')
axes3[1,0].set_ylabel('GM (inches)')
axes3[1,0].legend()
axes3[1,0].grid(True, alpha=0.3, axis='y')

# Safety Factor
axes3[1,1].bar(labels, [design_metrics[k]['safety_factor'] for k in labels], color=colors)
axes3[1,1].axhline(2.0, color='red', linestyle='--', linewidth=2, label='Required: ≥2.0')
axes3[1,1].set_title('Safety Factor (higher = stronger)', fontweight='bold')
axes3[1,1].set_ylabel('Safety Factor')
axes3[1,1].legend()
axes3[1,1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('reports/figures/3_designs_performance_bars.png', dpi=300, bbox_inches='tight')
print("✓ Saved: reports/figures/3_designs_performance_bars.png")

# FIGURE 4: RADAR CHART
print("Generating Figure 4: Radar chart...")
fig4 = plt.figure(figsize=(10, 10))
ax4 = fig4.add_subplot(111, projection='polar')

categories = ['Weight\n(normalized)', 'Freeboard', 'GM\n(Stability)', 'Safety\nFactor', 'Maneuverability\n(length)']
N = len(categories)

angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

for key, m in design_metrics.items():
    # Normalize values (0-1 scale)
    values = [
        1 - (m['weight'] / 350),  # Lower weight = better
        m['freeboard'] / 12,
        m['gm'] / 12,
        min(m['safety_factor'] / 10, 1),
        1 - (m['length'] / 240)  # Shorter = more maneuverable
    ]
    values += values[:1]
    
    ax4.plot(angles, values, 'o-', linewidth=2, color=m['color'], label=f"Design {key}")
    ax4.fill(angles, values, alpha=0.15, color=m['color'])

ax4.set_xticks(angles[:-1])
ax4.set_xticklabels(categories, size=10)
ax4.set_ylim(0, 1)
ax4.set_title('Performance Radar Chart\n(Larger = Better)', 
              fontsize=14, fontweight='bold', pad=20)
ax4.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
ax4.grid(True)

plt.tight_layout()
plt.savefig('reports/figures/3_designs_radar.png', dpi=300, bbox_inches='tight')
print("✓ Saved: reports/figures/3_designs_radar.png")

# SAVE DATA TO CSV
df = pd.DataFrame(design_metrics).T
df.to_csv('data/3_alternative_designs_detailed.csv')
print("✓ Saved: data/3_alternative_designs_detailed.csv")

# FINAL SUMMARY
print("\n" + "="*70)
print("RECOMMENDATION")
print("="*70)

passing_designs = {k: m for k, m in design_metrics.items() if m['all_pass']}
if passing_designs:
    best = min(passing_designs.items(), key=lambda x: x[1]['weight'])
    print(f"✓ BEST DESIGN: {best[0]} - {best[1]['name']}")
    print(f"  {best[1]['description']}")
    print(f"  Weight: {best[1]['weight']:.0f} lbs (lightest passing design)")
    print(f"  All ASCE requirements: PASS ✓")
else:
    print("✗ NO DESIGNS PASS ALL REQUIREMENTS")

print("="*70)
print("✓ ALL VISUALIZATIONS COMPLETE!")
print("="*70)
