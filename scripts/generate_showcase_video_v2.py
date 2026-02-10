#!/usr/bin/env python3
"""Generate narrated showcase video for NAU Concrete Canoe 2026.

V2: Professional neural voice narration (edge-tts) + improved visuals.
Generates per-scene audio clips, builds synced video, merges with ffmpeg.

Output: docs/nau-canoe-ai-showcase.mp4 (H.264, 1080p, with voiceover)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import matplotlib.animation as animation
import numpy as np
import subprocess
import json
import os
import tempfile
import struct
import wave

# ─── Colors ───────────────────────────────────────────────────────
NAVY = '#1B365D'
DARK_NAVY = '#0d1b2a'
GOLD = '#D4A843'
DARK_BG = '#080810'
PANEL_BG = '#111122'
CODE_BG = '#1a1a2e'
WHITE = '#ffffff'
LIGHT = '#e0e0e0'
MUTED = '#888899'
BLUE = '#4fc3f7'
GREEN = '#50fa7b'
RED = '#ff5555'
PINK = '#ff79c6'
CYAN = '#8be9fd'
ORANGE = '#ffb86c'
PURPLE = '#bd93f9'
TEAL = '#00d4aa'

VOICE = "en-US-AndrewMultilingualNeural"  # Warm, confident
FPS = 30

# ─── Scene narration scripts ─────────────────────────────────────
# Each scene: (narration_text, transition_buffer_seconds)
SCENES = [
    {
        "id": "intro",
        "narration": (
            "NAU Concrete Canoe, twenty twenty-six. Pluto Jacks. "
            "We used AI to design, analyze, and document a competition-ready concrete canoe."
        ),
        "buffer": 0.8,
    },
    {
        "id": "hull",
        "narration": (
            "Eighteen feet long, thirty inches wide, eighteen inches deep. "
            "Half-inch wall. Two hundred seventy-six pounds. "
            "Every dimension optimized by parametric Python code."
        ),
        "buffer": 0.8,
    },
    {
        "id": "analysis",
        "narration": (
            "Full structural analysis per ACI three-eighteen. "
            "Eight point five inches freeboard, above the six-inch minimum. "
            "Factor of safety: three point two x. "
            "Max stress eight forty-two psi, well under the limit. "
            "Every check passes."
        ),
        "buffer": 0.8,
    },
    {
        "id": "pipeline",
        "narration": (
            "Here's what makes it elite. "
            "Thirty-three Python scripts. Twenty thousand lines of code. "
            "Seventy-seven engineering figures. Sixty automated tests. "
            "A full presentation, CAD drawings, and documentation website. "
            "All AI-assisted."
        ),
        "buffer": 0.8,
    },
    {
        "id": "savings",
        "narration": (
            "One hundred sixty-four hours of manual work, "
            "done in twenty-four. "
            "Eighty-five percent time reduction. "
            "Over sixteen thousand dollars saved."
        ),
        "buffer": 0.8,
    },
    {
        "id": "quality",
        "narration": (
            "And it's verified. Sixty out of sixty tests passing. "
            "Every calculation hand-checked. "
            "This is production-quality engineering."
        ),
        "buffer": 0.8,
    },
    {
        "id": "closing",
        "narration": (
            "Pluto Jacks. "
            "Built smarter. Built faster. Built to win."
        ),
        "buffer": 1.5,
    },
]


def generate_audio_clips(tmpdir):
    """Generate individual audio clips per scene using edge-tts."""
    scene_durations = []

    for i, scene in enumerate(SCENES):
        mp3_path = os.path.join(tmpdir, f"scene_{i}.mp3")
        wav_path = os.path.join(tmpdir, f"scene_{i}.wav")

        # Generate with edge-tts (use = syntax so -5% isn't parsed as a flag)
        cmd = [
            "edge-tts",
            f"--voice={VOICE}",
            "--rate=-5%",
            f"--text={scene['narration']}",
            f"--write-media={mp3_path}",
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        # Convert to wav for duration measurement
        subprocess.run([
            "ffmpeg", "-y", "-i", mp3_path, "-ar", "44100", "-ac", "1", wav_path
        ], check=True, capture_output=True)

        # Get duration
        result = subprocess.run([
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", mp3_path
        ], capture_output=True, text=True)
        info = json.loads(result.stdout)
        dur = float(info["format"]["duration"])
        total = dur + scene["buffer"]
        scene_durations.append(total)

        print(f"  Scene {i} ({scene['id']}): audio={dur:.1f}s + buffer={scene['buffer']:.1f}s = {total:.1f}s")

    # Concatenate all audio with silence buffers
    concat_file = os.path.join(tmpdir, "concat.txt")
    silence_path = os.path.join(tmpdir, "silence.wav")

    with open(concat_file, "w") as f:
        for i, scene in enumerate(SCENES):
            mp3_path = os.path.join(tmpdir, f"scene_{i}.mp3")
            # Pad with silence for buffer
            padded = os.path.join(tmpdir, f"scene_{i}_padded.mp3")
            buf = scene["buffer"]
            subprocess.run([
                "ffmpeg", "-y", "-i", mp3_path,
                "-af", f"apad=pad_dur={buf}",
                "-t", f"{scene_durations[i]:.2f}",
                padded
            ], check=True, capture_output=True)
            f.write(f"file '{padded}'\n")

    # Concatenate
    full_audio = os.path.join(tmpdir, "full_narration.mp3")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file, "-c", "copy", full_audio
    ], check=True, capture_output=True)

    total_duration = sum(scene_durations)
    print(f"\n  Total duration: {total_duration:.1f}s")

    return scene_durations, full_audio, total_duration


# ─── Visual rendering functions ───────────────────────────────────

def ease(t):
    """Smooth ease-in-out, always clamped 0-1."""
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def safe_alpha(*factors):
    """Multiply alpha factors, clamp to [0, 1]."""
    result = 1.0
    for f in factors:
        result *= f
    return max(0.0, min(1.0, result))


def draw_particles(ax, frame, n=35):
    """Subtle floating particles."""
    np.random.seed(42)
    bx = np.random.uniform(0, 16, n)
    by = np.random.uniform(0, 9, n)
    sizes = np.random.uniform(1, 5, n)
    speeds = np.random.uniform(0.15, 0.6, n)
    t = frame / FPS
    for i in range(n):
        x = (bx[i] + speeds[i] * t * 0.2) % 16
        y = (by[i] + np.sin(t * speeds[i] + i) * 0.2) % 9
        a = max(0, min(1, 0.03 + 0.04 * np.sin(t * speeds[i] * 2 + i)))
        ax.plot(x, y, 'o', color=GOLD, markersize=sizes[i], alpha=a)


def draw_bar(ax, text="NAU ASCE Concrete Canoe 2026  |  Pluto Jacks  |  CENE 476 Capstone"):
    """Bottom info strip."""
    bar = FancyBboxPatch((-0.1, -0.1), 16.2, 0.65, boxstyle="square,pad=0",
                          facecolor=NAVY, edgecolor='none', alpha=0.95)
    ax.add_patch(bar)
    ax.text(8, 0.25, text, color=GOLD, fontsize=7, ha='center', va='center',
            fontfamily='sans-serif', fontweight='bold')


def scene_intro(ax, frame, t_local, dur):
    """Scene 0: Title card with animated elements."""
    p = t_local / dur
    a = max(0.0, ease(min(t_local / 1.2, 1)) * (1 if t_local < dur - 0.8 else ease(max(0, dur - t_local) / 0.8)))

    # Animated gold circle reveal
    angle = min(p * 1.5, 1) * 2 * np.pi
    theta = np.linspace(0, angle, 200)
    r = 2.8
    ax.plot(8 + r * np.cos(theta), 4.8 + r * np.sin(theta),
            color=GOLD, linewidth=2.5, alpha=a * 0.6)

    # Inner ring
    theta2 = np.linspace(0, min(p * 2, 1) * 2 * np.pi, 200)
    ax.plot(8 + 2.2 * np.cos(theta2), 4.8 + 2.2 * np.sin(theta2),
            color=BLUE, linewidth=1, alpha=a * 0.3)

    # Title stack
    s = ease(min(t_local / 1, 1))
    ax.text(8, 6.2, "NAU CONCRETE CANOE", color=WHITE, fontsize=20 * s,
            ha='center', va='center', fontweight='bold', alpha=a, fontfamily='sans-serif')
    ax.text(8, 5.2, "2 0 2 6", color=GOLD, fontsize=38 * s,
            ha='center', va='center', fontweight='bold', alpha=a, fontfamily='sans-serif')

    if t_local > 1.5:
        sa = a * ease(min((t_local - 1.5) / 0.8, 1))
        ax.text(8, 3.8, "PLUTO JACKS", color=BLUE, fontsize=16,
                ha='center', va='center', fontweight='bold', alpha=sa, style='italic')

    if t_local > 2.5:
        sa = a * ease(min((t_local - 2.5) / 0.8, 1))
        ax.text(8, 2.8, "AI-Powered Structural Engineering", color=LIGHT, fontsize=10,
                ha='center', va='center', alpha=sa * 0.9)
        ax.text(8, 2.2, "ASCE Pacific Southwest Conference", color=MUTED, fontsize=8,
                ha='center', va='center', alpha=sa * 0.7)

    draw_bar(ax)


def scene_hull(ax, frame, t_local, dur):
    """Scene 1: Hull design with animated cross-section and specs."""
    a = max(0.0, ease(min(t_local / 0.6, 1)) * (1 if t_local < dur - 0.6 else ease(max(0, dur - t_local) / 0.6)))

    # Section title
    ax.text(8, 8.3, "HULL DESIGN", color=GOLD, fontsize=20,
            ha='center', va='center', fontweight='bold', alpha=a)
    ax.text(8, 7.7, "Parametric Optimization  |  U-Shell Profile", color=MUTED, fontsize=8,
            ha='center', va='center', alpha=a * 0.8)

    # Animated hull profile (side view)
    reveal = ease(min(t_local / 2.5, 1))
    n_pts = int(200 * reveal)
    if n_pts > 2:
        x_hull = np.linspace(0, 216, n_pts)
        # Bow and stern taper
        bow_factor = np.minimum(x_hull / 40, 1)
        stern_factor = np.minimum((216 - x_hull) / 40, 1)
        taper = bow_factor * stern_factor
        depth_profile = 18 * taper

        # Scale and position hull
        sx = x_hull / 216 * 6 + 1.5  # map to x=[1.5, 7.5]
        sy = 4.5 - depth_profile / 18 * 2  # map depth

        # Sheer line (top)
        ax.plot(sx, np.full_like(sx, 4.5), color=BLUE, linewidth=2, alpha=a * 0.9)
        # Keel line (bottom)
        ax.plot(sx, sy, color=BLUE, linewidth=2, alpha=a * 0.9)
        # Fill hull
        ax.fill_between(sx, sy, 4.5, color=BLUE, alpha=a * 0.08)

        # Water line
        if t_local > 1.5:
            wl_a = a * ease(min((t_local - 1.5) / 0.5, 1))
            ax.axhline(y=3.8, xmin=0.08, xmax=0.52, color=CYAN, linewidth=1,
                       alpha=wl_a * 0.5, linestyle='--')
            ax.text(1.2, 3.95, "WL", color=CYAN, fontsize=6, alpha=wl_a * 0.6)

    # Spec cards on the right side
    specs = [
        ("LOA", "18'-0\" (216\")", BLUE, 1.2),
        ("Beam", "30\"", GREEN, 1.6),
        ("Depth", "18\"", ORANGE, 2.0),
        ("Thickness", "0.50\"", PURPLE, 2.4),
        ("Weight", "276 lbs", GOLD, 2.8),
        ("Mix", "f'c = 6,000 psi", TEAL, 3.2),
    ]

    for i, (label, value, color, delay) in enumerate(specs):
        if t_local > delay:
            sa = a * ease(min((t_local - delay) / 0.5, 1))
            y = 7.0 - i * 0.72
            # Card background
            card = FancyBboxPatch((9.5, y - 0.28), 6, 0.56,
                                   boxstyle="round,pad=0.04",
                                   facecolor=PANEL_BG, edgecolor=color,
                                   linewidth=1.5, alpha=sa * 0.85)
            ax.add_patch(card)
            ax.text(9.8, y, label, color=MUTED, fontsize=8, va='center', alpha=sa)
            ax.text(12.5, y, value, color=color, fontsize=11, fontweight='bold',
                    va='center', ha='center', fontfamily='monospace', alpha=sa)

    draw_bar(ax)


def scene_analysis(ax, frame, t_local, dur):
    """Scene 2: Engineering analysis results."""
    a = max(0.0, ease(min(t_local / 0.6, 1)) * (1 if t_local < dur - 0.6 else ease(max(0, dur - t_local) / 0.6)))

    ax.text(8, 8.3, "STRUCTURAL ANALYSIS", color=GOLD, fontsize=20,
            ha='center', va='center', fontweight='bold', alpha=a)
    ax.text(8, 7.7, "ACI 318-25  |  ASCE Rules  |  Naval Architecture", color=MUTED, fontsize=8,
            ha='center', va='center', alpha=a * 0.8)

    results = [
        ("Freeboard", "8.5\"", "> 6\" min", GREEN, "PASS", 0.5),
        ("Factor of Safety", "3.2x", "> 2.0x required", GREEN, "PASS", 1.5),
        ("Metacentric Height", "4.1\"", "Stable hull", BLUE, "PASS", 2.5),
        ("Max Bending Stress", "842 psi", "< 2,700 psi limit", GREEN, "PASS", 3.5),
    ]

    for i, (label, value, sub, color, status, delay) in enumerate(results):
        if t_local > delay:
            sa = a * ease(min((t_local - delay) / 0.8, 1))
            col = i % 2
            row = i // 2
            x = 2.5 + col * 6.5
            y = 5.5 - row * 2.8

            # Card
            card = FancyBboxPatch((x - 2.5, y - 1.1), 5.8, 2.4,
                                   boxstyle="round,pad=0.08",
                                   facecolor=PANEL_BG, edgecolor=color,
                                   linewidth=2, alpha=sa * 0.85)
            ax.add_patch(card)

            # Value (big)
            ax.text(x + 0.4, y + 0.5, value, color=color, fontsize=22, fontweight='bold',
                    ha='center', va='center', alpha=sa, fontfamily='sans-serif')
            # Label
            ax.text(x + 0.4, y - 0.15, label, color=WHITE, fontsize=10,
                    ha='center', va='center', alpha=sa)
            # Subtitle
            ax.text(x + 0.4, y - 0.65, sub, color=MUTED, fontsize=8,
                    ha='center', va='center', alpha=sa * 0.8)

            # Animated pass badge
            if t_local - delay > 0.6:
                badge_a = sa * ease(min((t_local - delay - 0.6) / 0.3, 1))
                badge = FancyBboxPatch((x + 1.8, y + 0.8), 1.3, 0.45,
                                       boxstyle="round,pad=0.05",
                                       facecolor=GREEN, edgecolor='none',
                                       alpha=badge_a * 0.9)
                ax.add_patch(badge)
                ax.text(x + 2.45, y + 1.03, "PASS", color=DARK_BG, fontsize=8,
                        fontweight='bold', ha='center', va='center', alpha=badge_a)

    draw_bar(ax)


def scene_pipeline(ax, frame, t_local, dur):
    """Scene 3: AI development pipeline."""
    a = max(0.0, ease(min(t_local / 0.6, 1)) * (1 if t_local < dur - 0.6 else ease(max(0, dur - t_local) / 0.6)))

    ax.text(8, 8.3, "AI-POWERED DEVELOPMENT", color=GOLD, fontsize=20,
            ha='center', va='center', fontweight='bold', alpha=a)
    ax.text(8, 7.7, "Claude + Gemini  |  33 Scripts  |  Full Automation", color=MUTED,
            fontsize=8, ha='center', va='center', alpha=a * 0.8)

    # Animated code rain (subtle)
    np.random.seed(99)
    for j in range(25):
        cx = 0.5 + (j / 25) * 15
        speed = 0.3 + np.random.random() * 1.2
        cy = (7 - ((t_local * speed + j * 0.5) % 7)) + 0.5
        kw = np.random.choice(["def", "class", "import", "return", "assert", "for", "if"])
        ax.text(cx, cy, kw, color=GREEN, fontsize=5, alpha=a * 0.08, fontfamily='monospace')

    items = [
        ("33", "Python Scripts", "All AI-generated, human-verified", BLUE, 0.5),
        ("20,847", "Lines of Code", "Calculator + visuals + tests + site", GREEN, 1.2),
        ("77", "Engineering Figures", "FBDs, 3D views, CAD, construction", ORANGE, 1.9),
        ("60/60", "Automated Tests", "100% pass rate, full coverage", PINK, 2.6),
        ("24", "Slide Presentation", "Complete capstone review deck", PURPLE, 3.3),
        ("3", "CAD Drawing Sheets", "Professional construction docs", CYAN, 4.0),
    ]

    for i, (num, label, sub, color, delay) in enumerate(items):
        if t_local > delay:
            sa = a * ease(min((t_local - delay) / 0.6, 1))
            y = 6.5 - i * 0.92

            # Number badge
            badge = FancyBboxPatch((2.5, y - 0.3), 2.0, 0.65,
                                    boxstyle="round,pad=0.05",
                                    facecolor=color, edgecolor='none', alpha=sa * 0.2)
            ax.add_patch(badge)
            ax.text(3.5, y + 0.02, num, color=color, fontsize=16, fontweight='bold',
                    ha='center', va='center', alpha=sa, fontfamily='sans-serif')

            # Label + sub
            ax.text(5.2, y + 0.08, label, color=WHITE, fontsize=11,
                    ha='left', va='center', alpha=sa, fontweight='bold')
            ax.text(5.2, y - 0.3, sub, color=MUTED, fontsize=7,
                    ha='left', va='center', alpha=sa * 0.8)

    draw_bar(ax)


def scene_savings(ax, frame, t_local, dur):
    """Scene 4: Time and cost savings with animated comparison bars."""
    a = max(0.0, ease(min(t_local / 0.6, 1)) * (1 if t_local < dur - 0.6 else ease(max(0, dur - t_local) / 0.6)))

    ax.text(8, 8.3, "TIME & COST SAVINGS", color=GOLD, fontsize=20,
            ha='center', va='center', fontweight='bold', alpha=a)

    categories = [
        ("Structural Calculator", 36, 4),
        ("Engineering Figures", 48, 6),
        ("Test Suite", 12, 2),
        ("CAD Drawings", 16, 3),
        ("Website + Dashboard", 24, 4),
        ("Presentation", 8, 2),
        ("Mix Design Analysis", 20, 3),
    ]

    max_h = 50
    y_start = 7.2

    # Legend
    ax.text(12, 7.7, "Manual", color=RED, fontsize=8, ha='left', alpha=a * 0.9, fontweight='bold')
    ax.text(14, 7.7, "AI", color=GREEN, fontsize=8, ha='left', alpha=a * 0.9, fontweight='bold')

    for i, (cat, manual, ai_h) in enumerate(categories):
        delay = 0.3 + i * 0.4
        if t_local > delay:
            sa = a * ease(min((t_local - delay) / 0.6, 1))
            y = y_start - i * 0.8

            ax.text(1.0, y, cat, color=LIGHT, fontsize=7.5, ha='left', va='center',
                    alpha=sa, fontfamily='sans-serif')

            # Manual bar
            mw = (manual / max_h) * 6 * sa
            bar_m = FancyBboxPatch((5.0, y + 0.02), mw, 0.22,
                                    boxstyle="round,pad=0.02",
                                    facecolor=RED, edgecolor='none', alpha=sa * 0.75)
            ax.add_patch(bar_m)
            ax.text(5.0 + mw + 0.15, y + 0.13, f"{manual}h", color=RED,
                    fontsize=6, va='center', alpha=sa)

            # AI bar
            aw = (ai_h / max_h) * 6 * sa
            bar_a = FancyBboxPatch((5.0, y - 0.26), aw, 0.22,
                                    boxstyle="round,pad=0.02",
                                    facecolor=GREEN, edgecolor='none', alpha=sa * 0.75)
            ax.add_patch(bar_a)
            ax.text(5.0 + aw + 0.15, y - 0.15, f"{ai_h}h", color=GREEN,
                    fontsize=6, va='center', alpha=sa)

    # Big summary card on the right
    if t_local > 3.5:
        ca = a * ease(min((t_local - 3.5) / 0.8, 1))
        card = FancyBboxPatch((11, 1.2), 4.5, 5.5, boxstyle="round,pad=0.1",
                               facecolor=NAVY, edgecolor=GOLD, linewidth=2, alpha=ca * 0.95)
        ax.add_patch(card)

        ax.text(13.25, 6.0, "85%", color=GREEN, fontsize=36, fontweight='bold',
                ha='center', va='center', alpha=ca)
        ax.text(13.25, 5.0, "Time Reduction", color=WHITE, fontsize=11,
                ha='center', va='center', alpha=ca)

        # Divider
        ax.plot([11.5, 15], [4.4, 4.4], color=GOLD, linewidth=0.5, alpha=ca * 0.4)

        ax.text(13.25, 3.7, "164 hrs", color=RED, fontsize=14, fontweight='bold',
                ha='center', va='center', alpha=ca)
        ax.text(13.25, 3.1, "manual development", color=MUTED, fontsize=7,
                ha='center', va='center', alpha=ca)

        ax.text(13.25, 2.3, "24 hrs", color=GREEN, fontsize=14, fontweight='bold',
                ha='center', va='center', alpha=ca)
        ax.text(13.25, 1.7, "with AI assistance", color=MUTED, fontsize=7,
                ha='center', va='center', alpha=ca)

    # Cost saved
    if t_local > 5:
        ca2 = a * ease(min((t_local - 5) / 0.6, 1))
        ax.text(5.5, 1.0, "$16,400+", color=GOLD, fontsize=20, fontweight='bold',
                ha='center', va='center', alpha=ca2)
        ax.text(5.5, 0.5, "equivalent cost saved", color=MUTED, fontsize=8,
                ha='center', va='center', alpha=ca2 * 0.8)

    draw_bar(ax, "NAU Concrete Canoe 2026  |  85% Time Reduction  |  $16,400+ Saved")


def scene_quality(ax, frame, t_local, dur):
    """Scene 5: Code quality and testing."""
    a = max(0.0, ease(min(t_local / 0.6, 1)) * (1 if t_local < dur - 0.6 else ease(max(0, dur - t_local) / 0.6)))

    ax.text(8, 8.3, "VERIFIED ENGINEERING", color=GOLD, fontsize=20,
            ha='center', va='center', fontweight='bold', alpha=a)
    ax.text(8, 7.7, "Every calculation hand-checked  |  60/60 automated tests", color=MUTED,
            fontsize=8, ha='center', va='center', alpha=a * 0.8)

    suites = [
        ("Hull Geometry", 12, 0.4),
        ("Structural Capacity", 15, 1.2),
        ("Stability & Safety", 10, 2.0),
        ("Load Distribution", 8, 2.8),
        ("Integration Tests", 15, 3.6),
    ]

    total_shown = 0
    for i, (name, count, delay) in enumerate(suites):
        if t_local > delay:
            sa = a * ease(min((t_local - delay) / 0.7, 1))
            y = 6.5 - i * 1.05

            # Row background
            row = FancyBboxPatch((1.5, y - 0.35), 13, 0.75, boxstyle="round,pad=0.04",
                                  facecolor=PANEL_BG, edgecolor='#222244', linewidth=1,
                                  alpha=sa * 0.8)
            ax.add_patch(row)

            ax.text(2.0, y, name, color=WHITE, fontsize=10,
                    ha='left', va='center', alpha=sa, fontfamily='monospace')

            # Animated count
            progress = min((t_local - delay) / 1.0, 1)
            shown = int(count * progress)
            total_shown += shown

            # Progress bar
            bar_w = (shown / count) * 4
            bar_bg = FancyBboxPatch((8, y - 0.15), 4, 0.3, boxstyle="round,pad=0.02",
                                     facecolor='#1a1a2e', edgecolor='none', alpha=sa * 0.5)
            ax.add_patch(bar_bg)
            if bar_w > 0.1:
                bar_fill = FancyBboxPatch((8, y - 0.15), bar_w, 0.3, boxstyle="round,pad=0.02",
                                           facecolor=GREEN, edgecolor='none', alpha=sa * 0.6)
                ax.add_patch(bar_fill)

            ax.text(12.5, y, f"{shown}/{count}", color=GREEN, fontsize=10,
                    ha='center', va='center', alpha=sa, fontfamily='monospace', fontweight='bold')

            # Pass badge
            if progress >= 1:
                badge = FancyBboxPatch((13.2, y - 0.18), 1.1, 0.36,
                                       boxstyle="round,pad=0.04",
                                       facecolor=GREEN, edgecolor='none', alpha=sa * 0.85)
                ax.add_patch(badge)
                ax.text(13.75, y, "PASS", color=DARK_BG, fontsize=7, fontweight='bold',
                        ha='center', va='center', alpha=sa)

    # Total
    if t_local > 5:
        ta = a * ease(min((t_local - 5) / 0.5, 1))
        total_box = FancyBboxPatch((4, 0.8), 8, 1.2, boxstyle="round,pad=0.08",
                                    facecolor=NAVY, edgecolor=GREEN, linewidth=2.5,
                                    alpha=ta * 0.95)
        ax.add_patch(total_box)
        ax.text(8, 1.4, "60 / 60  TESTS  PASSING", color=GREEN, fontsize=18,
                fontweight='bold', ha='center', va='center', alpha=ta,
                fontfamily='sans-serif')

    draw_bar(ax)


def scene_closing(ax, frame, t_local, dur):
    """Scene 6: Closing card."""
    a = max(0.0, ease(min(t_local / 0.8, 1)) * (1 if t_local < dur - 1.2 else ease(max(0, dur - t_local) / 1.2)))

    # Dual rings
    theta = np.linspace(0, 2 * np.pi, 300)
    ax.plot(8 + 3.2 * np.cos(theta), 4.5 + 3.2 * np.sin(theta),
            color=GOLD, linewidth=2, alpha=a * 0.35)
    ax.plot(8 + 2.6 * np.cos(theta), 4.5 + 2.6 * np.sin(theta),
            color=BLUE, linewidth=1, alpha=a * 0.2)

    s = ease(min(t_local / 0.8, 1))
    ax.text(8, 6.5, "THE FUTURE OF", color=MUTED, fontsize=13,
            ha='center', va='center', alpha=a * s)
    ax.text(8, 5.3, "ENGINEERING", color=WHITE, fontsize=30,
            ha='center', va='center', fontweight='bold', alpha=a * s)
    ax.text(8, 4.1, "IS AI-POWERED", color=GOLD, fontsize=30,
            ha='center', va='center', fontweight='bold', alpha=a * s)

    if t_local > 1.2:
        sa = a * ease(min((t_local - 1.2) / 0.6, 1))
        ax.text(8, 2.6, "NAU Concrete Canoe 2026  |  Pluto Jacks", color=BLUE,
                fontsize=11, ha='center', va='center', alpha=sa, fontweight='bold')
        ax.text(8, 2.0, "Built smarter.  Built faster.  Built to win.", color=LIGHT,
                fontsize=9, ha='center', va='center', alpha=sa * 0.9, style='italic')

    draw_bar(ax)


SCENE_RENDERERS = [scene_intro, scene_hull, scene_analysis,
                    scene_pipeline, scene_savings, scene_quality, scene_closing]


def main():
    print("Step 1: Generating narration audio...")
    tmpdir = tempfile.mkdtemp(prefix="canoe_video_")

    scene_durations, audio_path, total_duration = generate_audio_clips(tmpdir)

    # Compute scene start times
    scene_starts = []
    t = 0
    for d in scene_durations:
        scene_starts.append(t)
        t += d

    total_frames = int(total_duration * FPS) + 1
    print(f"\nStep 2: Rendering {total_frames} frames ({total_duration:.1f}s)...")

    fig, ax = plt.subplots(1, 1, figsize=(16, 9), dpi=120)
    fig.set_facecolor(DARK_BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    silent_video = os.path.join(tmpdir, "silent.mp4")

    def animate(frame):
        ax.clear()
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 9)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_facecolor(DARK_BG)

        draw_particles(ax, frame)

        t = frame / FPS
        for i, (start, dur) in enumerate(zip(scene_starts, scene_durations)):
            if start <= t < start + dur:
                t_local = t - start
                SCENE_RENDERERS[i](ax, frame, t_local, dur)
                break

        if frame % (FPS * 5) == 0:
            print(f"  Frame {frame}/{total_frames} ({frame/total_frames*100:.0f}%)")

        return []

    anim = animation.FuncAnimation(fig, animate, frames=total_frames,
                                    interval=1000/FPS, blit=True)

    writer = animation.FFMpegWriter(
        fps=FPS,
        bitrate=3000,
        extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p',
                    '-preset', 'medium', '-crf', '22']
    )

    anim.save(silent_video, writer=writer, dpi=120)
    plt.close(fig)
    print(f"  Silent video: {silent_video}")

    # Step 3: Merge audio + video
    print("\nStep 3: Merging audio and video...")
    output = '/root/concrete-canoe-project2026/docs/nau-canoe-ai-showcase.mp4'
    subprocess.run([
        "ffmpeg", "-y",
        "-i", silent_video,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        output
    ], check=True, capture_output=True)

    size_mb = os.path.getsize(output) / (1024 * 1024)
    print(f"\nDone!")
    print(f"  Output: {output}")
    print(f"  Size: {size_mb:.1f} MB")
    print(f"  Duration: {total_duration:.1f}s")
    print(f"  Resolution: 1920x1080")
    print(f"  Audio: AAC 128kbps (neural voice narration)")

    # Cleanup
    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == '__main__':
    main()
