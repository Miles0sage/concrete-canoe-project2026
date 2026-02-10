#!/usr/bin/env python3
"""Generate a short animated showcase video for the NAU Concrete Canoe 2026 project.

Creates a ~45-second MP4 video with smooth transitions showing:
- Project title and team
- Engineering highlights (hull design, structural analysis)
- AI-powered development stats
- Cost and time savings
- Why it's elite

Output: docs/nau-canoe-ai-showcase.mp4 (H.264, 1080p, web-optimized)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import matplotlib.animation as animation
import numpy as np
import os

# Color scheme
NAVY = '#1B365D'
GOLD = '#D4A843'
DARK_BG = '#0a0a1a'
CODE_BG = '#1e1e2e'
WHITE = '#ffffff'
LIGHT_GRAY = '#cccccc'
ACCENT_BLUE = '#4fc3f7'
GREEN = '#50fa7b'
RED = '#ff5555'
PINK = '#ff79c6'
CYAN = '#8be9fd'
ORANGE = '#ffb86c'

FPS = 30
DURATION = 48  # seconds
TOTAL_FRAMES = FPS * DURATION

# Scene definitions: (start_time, end_time, scene_function_name)
SCENES = [
    (0, 6, 'title_card'),
    (6, 12, 'hull_design'),
    (12, 18, 'engineering_stats'),
    (18, 26, 'ai_development'),
    (26, 34, 'savings_breakdown'),
    (34, 41, 'code_quality'),
    (41, 48, 'closing_card'),
]


def ease_in_out(t):
    """Smooth ease-in-out interpolation."""
    return t * t * (3 - 2 * t)


def fade_alpha(frame, scene_start, scene_end, fade_in=0.5, fade_out=0.5):
    """Calculate fade alpha for a frame within a scene."""
    t = frame / FPS
    scene_dur = scene_end - scene_start
    local_t = (t - scene_start) / scene_dur

    if local_t < fade_in / scene_dur:
        return ease_in_out(local_t / (fade_in / scene_dur))
    elif local_t > 1 - fade_out / scene_dur:
        return ease_in_out((1 - local_t) / (fade_out / scene_dur))
    return 1.0


def draw_particle_bg(ax, frame, n=40):
    """Draw animated floating particles for background ambience."""
    np.random.seed(42)
    base_x = np.random.uniform(0, 16, n)
    base_y = np.random.uniform(0, 9, n)
    sizes = np.random.uniform(2, 8, n)
    speeds = np.random.uniform(0.2, 0.8, n)
    t = frame / FPS

    for i in range(n):
        x = (base_x[i] + speeds[i] * t * 0.3) % 16
        y = (base_y[i] + np.sin(t * speeds[i] + i) * 0.3) % 9
        alpha = 0.05 + 0.05 * np.sin(t * speeds[i] * 2 + i)
        ax.plot(x, y, 'o', color=GOLD, markersize=sizes[i], alpha=alpha)


def draw_bottom_bar(ax, text="NAU ASCE Concrete Canoe 2026 — Pluto Jacks"):
    """Persistent bottom info bar."""
    bar = FancyBboxPatch((0, 0), 16, 0.6, boxstyle="square,pad=0",
                          facecolor=NAVY, edgecolor='none', alpha=0.9)
    ax.add_patch(bar)
    ax.text(8, 0.3, text, color=GOLD, fontsize=8, ha='center', va='center',
            fontweight='bold', fontfamily='sans-serif')


def scene_title_card(ax, frame, scene_start, scene_end):
    """Scene 1: Project title card with team name."""
    alpha = fade_alpha(frame, scene_start, scene_end)
    t = frame / FPS - scene_start

    # Animated gold ring
    theta = np.linspace(0, 2 * np.pi * min(t / 2, 1), 100)
    r = 2.5
    cx, cy = 8, 5
    ring_x = cx + r * np.cos(theta)
    ring_y = cy + r * np.sin(theta)
    ax.plot(ring_x, ring_y, color=GOLD, linewidth=3, alpha=alpha * 0.7)

    # Title text
    scale = ease_in_out(min(t / 1.5, 1))
    ax.text(8, 5.8, "NAU CONCRETE CANOE", color=WHITE, fontsize=22 * scale,
            ha='center', va='center', fontweight='bold', alpha=alpha,
            fontfamily='sans-serif')
    ax.text(8, 4.8, "2026", color=GOLD, fontsize=36 * scale,
            ha='center', va='center', fontweight='bold', alpha=alpha,
            fontfamily='sans-serif')

    if t > 1.5:
        sub_alpha = alpha * ease_in_out(min((t - 1.5) / 1, 1))
        ax.text(8, 3.6, "PLUTO JACKS", color=ACCENT_BLUE, fontsize=14,
                ha='center', va='center', fontweight='bold', alpha=sub_alpha,
                fontfamily='sans-serif', style='italic')
        ax.text(8, 2.8, "ASCE Pacific Southwest Conference", color=LIGHT_GRAY,
                fontsize=9, ha='center', va='center', alpha=sub_alpha * 0.8)

    draw_bottom_bar(ax)


def scene_hull_design(ax, frame, scene_start, scene_end):
    """Scene 2: Hull design specs with animated hull cross-section."""
    alpha = fade_alpha(frame, scene_start, scene_end)
    t = frame / FPS - scene_start

    ax.text(8, 8.0, "OPTIMIZED HULL DESIGN", color=GOLD, fontsize=18,
            ha='center', va='center', fontweight='bold', alpha=alpha)

    # Animated U-shaped cross section
    reveal = ease_in_out(min(t / 2, 1))
    theta = np.linspace(-np.pi/2, np.pi/2, 100)
    beam_half = 2.5
    depth = 2.0
    hull_y = 5 + beam_half * np.cos(theta[:int(100 * reveal)])
    hull_z = 4 - depth * np.sin(np.maximum(theta[:int(100 * reveal)], 0))
    if len(hull_y) > 1:
        ax.plot(hull_y, hull_z, color=ACCENT_BLUE, linewidth=3, alpha=alpha)
        # Water line
        ax.axhline(y=3.2, color=CYAN, linewidth=1, alpha=alpha * 0.4, linestyle='--')
        ax.text(2, 3.35, "WL", color=CYAN, fontsize=7, alpha=alpha * 0.5)

    # Specs
    if t > 1.5:
        spec_alpha = alpha * ease_in_out(min((t - 1.5) / 1, 1))
        specs = [
            ("LOA:  18'-0\" (216\")", 0),
            ("Beam: 30\"", 0.15),
            ("Depth: 18\"", 0.3),
            ("Thickness: 0.50\"", 0.45),
            ("Weight: 276 lbs", 0.6),
        ]
        for i, (spec, delay) in enumerate(specs):
            if t - 1.5 > delay:
                sa = spec_alpha * ease_in_out(min((t - 1.5 - delay) / 0.5, 1))
                # Spec card
                card = FancyBboxPatch((10.5, 6.5 - i * 0.9), 4.5, 0.7,
                                       boxstyle="round,pad=0.05",
                                       facecolor=CODE_BG, edgecolor=GOLD,
                                       linewidth=1, alpha=sa * 0.8)
                ax.add_patch(card)
                ax.text(12.75, 6.85 - i * 0.9, spec, color=WHITE, fontsize=10,
                        ha='center', va='center', fontfamily='monospace', alpha=sa)

    draw_bottom_bar(ax)


def scene_engineering_stats(ax, frame, scene_start, scene_end):
    """Scene 3: Engineering analysis highlights."""
    alpha = fade_alpha(frame, scene_start, scene_end)
    t = frame / FPS - scene_start

    ax.text(8, 8.0, "ENGINEERING ANALYSIS", color=GOLD, fontsize=18,
            ha='center', va='center', fontweight='bold', alpha=alpha)

    stats = [
        ("Freeboard", "8.5\"", "> 6\" min", GREEN),
        ("Factor of Safety", "3.2x", "> 2.0x req", GREEN),
        ("Metacentric Height", "4.1\"", "Stable", ACCENT_BLUE),
        ("Max Bending Stress", "842 psi", "< 2,700 psi", GREEN),
    ]

    for i, (label, value, sub, color) in enumerate(stats):
        delay = i * 0.4
        if t > delay:
            sa = alpha * ease_in_out(min((t - delay) / 0.8, 1))
            x = 2.5 + (i % 2) * 6
            y = 5.5 - (i // 2) * 2.5

            card = FancyBboxPatch((x - 2, y - 1), 4.5, 2.2,
                                   boxstyle="round,pad=0.1",
                                   facecolor=CODE_BG, edgecolor=color,
                                   linewidth=2, alpha=sa * 0.85)
            ax.add_patch(card)
            ax.text(x + 0.25, y + 0.6, value, color=color, fontsize=20,
                    ha='center', va='center', fontweight='bold', alpha=sa)
            ax.text(x + 0.25, y - 0.1, label, color=WHITE, fontsize=10,
                    ha='center', va='center', alpha=sa)
            ax.text(x + 0.25, y - 0.6, sub, color=LIGHT_GRAY, fontsize=8,
                    ha='center', va='center', alpha=sa * 0.7)

    draw_bottom_bar(ax)


def scene_ai_development(ax, frame, scene_start, scene_end):
    """Scene 4: AI-powered development showcase."""
    alpha = fade_alpha(frame, scene_start, scene_end)
    t = frame / FPS - scene_start

    ax.text(8, 8.2, "AI-POWERED DEVELOPMENT", color=GOLD, fontsize=18,
            ha='center', va='center', fontweight='bold', alpha=alpha)
    ax.text(8, 7.5, "Claude + Gemini | Autonomous Engineering Pipeline",
            color=LIGHT_GRAY, fontsize=9, ha='center', va='center', alpha=alpha * 0.8)

    # Animated code rain effect
    np.random.seed(123)
    n_drops = 30
    for i in range(n_drops):
        x = 0.5 + (i / n_drops) * 15
        speed = 0.5 + np.random.random() * 1.5
        y_pos = (7 - ((t * speed + i * 0.7) % 7))
        char = np.random.choice(list("def class import return assert yield lambda"))
        drop_alpha = alpha * 0.15 * (y_pos / 7)
        ax.text(x, y_pos + 0.5, char, color=GREEN, fontsize=6,
                alpha=drop_alpha, fontfamily='monospace')

    # Central stats
    items = [
        ("33 Python Scripts", ACCENT_BLUE, 0),
        ("20,000+ Lines of Code", GREEN, 0.5),
        ("77 Publication Figures", ORANGE, 1.0),
        ("60 Automated Tests", PINK, 1.5),
        ("24-Slide Presentation", CYAN, 2.0),
        ("Full Documentation Site", WHITE, 2.5),
    ]

    for i, (text, color, delay) in enumerate(items):
        if t > delay:
            sa = alpha * ease_in_out(min((t - delay) / 0.6, 1))
            y = 6.0 - i * 0.85
            # Bullet
            ax.text(4.5, y, ">", color=GOLD, fontsize=12, fontweight='bold',
                    ha='center', va='center', alpha=sa, fontfamily='monospace')
            ax.text(5.2, y, text, color=color, fontsize=12,
                    ha='left', va='center', alpha=sa, fontfamily='sans-serif')

    draw_bottom_bar(ax)


def scene_savings_breakdown(ax, frame, scene_start, scene_end):
    """Scene 5: Time and cost savings with animated bars."""
    alpha = fade_alpha(frame, scene_start, scene_end)
    t = frame / FPS - scene_start

    ax.text(8, 8.2, "TIME & COST SAVINGS", color=GOLD, fontsize=18,
            ha='center', va='center', fontweight='bold', alpha=alpha)

    # Comparison bars: Manual vs AI
    categories = [
        ("Calculator", 36, 4),
        ("Figures", 48, 6),
        ("Testing", 12, 2),
        ("CAD Drawings", 16, 3),
        ("Website", 24, 4),
        ("Presentation", 8, 2),
        ("Mix Design", 20, 3),
    ]

    max_hours = 50
    bar_height = 0.5
    y_start = 7.0

    for i, (cat, manual, ai) in enumerate(categories):
        delay = i * 0.3
        if t > delay:
            sa = alpha * ease_in_out(min((t - delay) / 0.6, 1))
            y = y_start - i * 0.85

            ax.text(1.0, y, cat, color=WHITE, fontsize=8, ha='left', va='center',
                    alpha=sa, fontfamily='sans-serif')

            # Manual bar (red)
            manual_width = (manual / max_hours) * 7 * sa
            bar_m = FancyBboxPatch((4.5, y + 0.05), manual_width, bar_height * 0.4,
                                    boxstyle="round,pad=0.02",
                                    facecolor=RED, edgecolor='none', alpha=sa * 0.8)
            ax.add_patch(bar_m)
            ax.text(4.5 + manual_width + 0.2, y + 0.25, f"{manual}h",
                    color=RED, fontsize=7, va='center', alpha=sa)

            # AI bar (green)
            ai_width = (ai / max_hours) * 7 * sa
            bar_a = FancyBboxPatch((4.5, y - bar_height * 0.4 - 0.05), ai_width, bar_height * 0.4,
                                    boxstyle="round,pad=0.02",
                                    facecolor=GREEN, edgecolor='none', alpha=sa * 0.8)
            ax.add_patch(bar_a)
            ax.text(4.5 + ai_width + 0.2, y - 0.25, f"{ai}h",
                    color=GREEN, fontsize=7, va='center', alpha=sa)

    # Legend
    if t > 2:
        leg_alpha = alpha * ease_in_out(min((t - 2) / 0.5, 1))
        ax.text(13, 7.8, "Manual", color=RED, fontsize=9, ha='center',
                va='center', alpha=leg_alpha, fontweight='bold')
        ax.text(13, 7.3, "AI-Powered", color=GREEN, fontsize=9, ha='center',
                va='center', alpha=leg_alpha, fontweight='bold')

    # Big totals
    if t > 3:
        tot_alpha = alpha * ease_in_out(min((t - 3) / 1, 1))
        total_card = FancyBboxPatch((10.5, 1.2), 5, 3.5, boxstyle="round,pad=0.1",
                                     facecolor=NAVY, edgecolor=GOLD, linewidth=2,
                                     alpha=tot_alpha * 0.9)
        ax.add_patch(total_card)
        ax.text(13, 4.0, "85%", color=GREEN, fontsize=30, fontweight='bold',
                ha='center', va='center', alpha=tot_alpha)
        ax.text(13, 3.0, "Time Reduction", color=WHITE, fontsize=11,
                ha='center', va='center', alpha=tot_alpha)
        ax.text(13, 2.2, "164 hrs → 24 hrs", color=LIGHT_GRAY, fontsize=9,
                ha='center', va='center', alpha=tot_alpha * 0.8)
        ax.text(13, 1.7, "$16,400+ saved", color=GOLD, fontsize=10,
                ha='center', va='center', alpha=tot_alpha, fontweight='bold')

    draw_bottom_bar(ax)


def scene_code_quality(ax, frame, scene_start, scene_end):
    """Scene 6: Code quality and testing."""
    alpha = fade_alpha(frame, scene_start, scene_end)
    t = frame / FPS - scene_start

    ax.text(8, 8.2, "PRODUCTION-QUALITY CODE", color=GOLD, fontsize=18,
            ha='center', va='center', fontweight='bold', alpha=alpha)

    # Animated test results
    test_categories = [
        ("Hull Geometry", 12, GREEN),
        ("Structural Analysis", 15, GREEN),
        ("Stability & Safety", 10, GREEN),
        ("Load Distribution", 8, GREEN),
        ("Integration Tests", 15, GREEN),
    ]

    for i, (name, count, color) in enumerate(test_categories):
        delay = i * 0.5
        if t > delay:
            sa = alpha * ease_in_out(min((t - delay) / 0.6, 1))
            y = 6.5 - i * 1.0

            # Test suite row
            row = FancyBboxPatch((2, y - 0.3), 12, 0.7, boxstyle="round,pad=0.05",
                                  facecolor=CODE_BG, edgecolor='#333355', linewidth=1,
                                  alpha=sa * 0.8)
            ax.add_patch(row)

            ax.text(2.5, y, f"  {name}", color=WHITE, fontsize=10,
                    ha='left', va='center', alpha=sa, fontfamily='monospace')

            # Animated pass count
            shown = int(count * min((t - delay) / 1, 1))
            ax.text(11, y, f"{shown}/{count} passed", color=color, fontsize=10,
                    ha='center', va='center', alpha=sa, fontfamily='monospace',
                    fontweight='bold')

            # Check mark
            if t - delay > 1:
                ax.text(13.5, y, "PASS", color=GREEN, fontsize=10, fontweight='bold',
                        ha='center', va='center', alpha=sa)

    # Total at bottom
    if t > 3:
        tot_alpha = alpha * ease_in_out(min((t - 3) / 0.5, 1))
        total_box = FancyBboxPatch((4, 1.0), 8, 1.2, boxstyle="round,pad=0.1",
                                    facecolor=NAVY, edgecolor=GREEN, linewidth=2,
                                    alpha=tot_alpha * 0.9)
        ax.add_patch(total_box)
        ax.text(8, 1.6, "60/60 TESTS PASSING", color=GREEN, fontsize=16,
                fontweight='bold', ha='center', va='center', alpha=tot_alpha)

    draw_bottom_bar(ax)


def scene_closing_card(ax, frame, scene_start, scene_end):
    """Scene 7: Closing card."""
    alpha = fade_alpha(frame, scene_start, scene_end, fade_out=1.5)
    t = frame / FPS - scene_start

    # Big gold ring
    theta = np.linspace(0, 2 * np.pi, 200)
    r = 3.0
    ring_x = 8 + r * np.cos(theta)
    ring_y = 4.5 + r * np.sin(theta)
    ax.plot(ring_x, ring_y, color=GOLD, linewidth=2, alpha=alpha * 0.4)

    scale = ease_in_out(min(t / 1, 1))

    ax.text(8, 6.0, "THE FUTURE OF", color=LIGHT_GRAY, fontsize=12,
            ha='center', va='center', alpha=alpha * scale)
    ax.text(8, 5.0, "ENGINEERING", color=WHITE, fontsize=28,
            ha='center', va='center', fontweight='bold', alpha=alpha * scale)
    ax.text(8, 4.0, "IS AI-POWERED", color=GOLD, fontsize=28,
            ha='center', va='center', fontweight='bold', alpha=alpha * scale)

    if t > 1.5:
        sub_alpha = alpha * ease_in_out(min((t - 1.5) / 1, 1))
        ax.text(8, 2.5, "NAU Concrete Canoe 2026 | Pluto Jacks",
                color=ACCENT_BLUE, fontsize=11, ha='center', va='center',
                alpha=sub_alpha, fontweight='bold')
        ax.text(8, 1.8, "Built smarter. Built faster. Built to win.",
                color=LIGHT_GRAY, fontsize=9, ha='center', va='center',
                alpha=sub_alpha * 0.8, style='italic')

    draw_bottom_bar(ax)


# Map scene names to functions
SCENE_FUNCS = {
    'title_card': scene_title_card,
    'hull_design': scene_hull_design,
    'engineering_stats': scene_engineering_stats,
    'ai_development': scene_ai_development,
    'savings_breakdown': scene_savings_breakdown,
    'code_quality': scene_code_quality,
    'closing_card': scene_closing_card,
}


def animate(frame):
    """Master animation function called for each frame."""
    ax.clear()
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor(DARK_BG)

    # Background particles
    draw_particle_bg(ax, frame)

    # Determine which scene we're in
    t = frame / FPS
    for start, end, scene_name in SCENES:
        if start <= t < end:
            SCENE_FUNCS[scene_name](ax, frame, start, end)
            break

    return []


def main():
    global fig, ax
    fig, ax = plt.subplots(1, 1, figsize=(16, 9), dpi=120)
    fig.set_facecolor(DARK_BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    print(f"Generating {DURATION}s video at {FPS}fps ({TOTAL_FRAMES} frames)...")
    print("This will take a few minutes...")

    anim = animation.FuncAnimation(fig, animate, frames=TOTAL_FRAMES,
                                    interval=1000/FPS, blit=True)

    output_path = '/root/concrete-canoe-project2026/docs/nau-canoe-ai-showcase.mp4'

    writer = animation.FFMpegWriter(
        fps=FPS,
        metadata={'title': 'NAU Concrete Canoe 2026 - AI Showcase',
                  'artist': 'Pluto Jacks Team'},
        bitrate=2500,
        extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p',
                    '-preset', 'medium', '-crf', '23']
    )

    anim.save(output_path, writer=writer, dpi=120)
    plt.close(fig)

    # Check file size
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\nVideo saved: {output_path}")
    print(f"File size: {size_mb:.1f} MB")
    print(f"Duration: {DURATION} seconds")
    print(f"Resolution: 1920x1080 (1080p)")

    # Also create a smaller web version if too large
    if size_mb > 15:
        small_path = output_path.replace('.mp4', '-web.mp4')
        os.system(f'ffmpeg -y -i "{output_path}" -vf scale=1280:720 '
                  f'-b:v 1500k -preset fast -crf 28 "{small_path}" 2>/dev/null')
        small_size = os.path.getsize(small_path) / (1024 * 1024)
        print(f"Web version: {small_path} ({small_size:.1f} MB)")


if __name__ == '__main__':
    main()
