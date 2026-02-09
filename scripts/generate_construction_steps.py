#!/usr/bin/env python3
"""
Generate Construction Step Visualization PNGs for NAU ASCE 2026 Concrete Canoe.
Female mold construction process - 10 detailed diagrams.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Circle, Rectangle
import numpy as np
import os

OUTPUT_DIR = '/root/concrete-canoe-project2026/reports/figures'
DPI = 300
FIG_W, FIG_H = 19.20, 10.80

COLORS = {
    'blue_dark': '#1B3A5C', 'blue_med': '#2E6B9E', 'blue_light': '#5BA3D9',
    'blue_pale': '#B8D8F0', 'gray_dark': '#3D3D3D', 'gray_med': '#7A7A7A',
    'gray_light': '#B0B0B0', 'gray_pale': '#E8E8E8', 'orange': '#E87D2F',
    'orange_light': '#F4A95B', 'green': '#4CAF50', 'green_dark': '#2E7D32',
    'white': '#FFFFFF', 'concrete': '#C4B9A8', 'concrete_dark': '#A69882',
    'eps_foam': '#E8E4DC', 'mdf': '#C4A06A', 'mesh': '#D4A843',
    'pva': '#A8D8A8', 'plastic': '#D0D0E8', 'bg': '#FAFAFA',
}
BRAND_TEXT = 'NAU ASCE 2026'


def setup_fig(title, figsize=(FIG_W, FIG_H)):
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    fig.patch.set_facecolor(COLORS['bg'])
    ax.set_facecolor(COLORS['white'])
    fig.suptitle(title, fontsize=24, fontweight='bold', color=COLORS['blue_dark'],
                 y=0.96, fontfamily='sans-serif')
    fig.text(0.98, 0.02, BRAND_TEXT, fontsize=11, color=COLORS['blue_med'],
             ha='right', va='bottom', fontweight='bold', fontstyle='italic')
    return fig, ax


def add_label_arrow(ax, text, xy, xytext, fontsize=11, color=None):
    if color is None:
        color = COLORS['gray_dark']
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=fontsize, fontweight='bold',
                color=color, ha='center', va='center',
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5),
                bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS['white'],
                          edgecolor=color, alpha=0.9))


def save_fig(fig, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor=fig.get_facecolor(),
                edgecolor='none', pad_inches=0.3)
    plt.close(fig)
    print(f"  Saved: {path}")


def offset_curve(base_x, base_y, offset_val):
    ox, oy = [], []
    for i in range(len(base_x)):
        if i > 0 and i < len(base_x) - 1:
            dx_t = base_x[i+1] - base_x[i-1]
            dy_t = base_y[i+1] - base_y[i-1]
        elif i == 0:
            dx_t = base_x[1] - base_x[0]
            dy_t = base_y[1] - base_y[0]
        else:
            dx_t = base_x[-1] - base_x[-2]
            dy_t = base_y[-1] - base_y[-2]
        mag = max((dx_t**2 + dy_t**2)**0.5, 1e-6)
        nx, ny = -dy_t / mag, dx_t / mag
        ox.append(base_x[i] + nx * offset_val)
        oy.append(base_y[i] + ny * offset_val)
    return ox, oy


def generate_step1():
    print("Generating Step 1: Mold Build...")
    fig, ax = setup_fig('Step 1: Female Mold Construction\nEPS Foam Sections on MDF Strongback')
    ax.set_xlim(-10, 210); ax.set_ylim(-15, 45); ax.set_aspect('equal'); ax.axis('off')

    sb = FancyBboxPatch((0, -5), 192, 4, boxstyle='round,pad=0.3',
                         facecolor=COLORS['mdf'], edgecolor=COLORS['gray_dark'], lw=2)
    ax.add_patch(sb)
    ax.text(96, -3, 'MDF STRONGBACK', ha='center', va='center', fontsize=12,
            fontweight='bold', color=COLORS['gray_dark'])
    for x in [20, 80, 120, 172]:
        ax.add_patch(Rectangle((x, -12), 6, 7, facecolor=COLORS['mdf'],
                     edgecolor=COLORS['gray_dark'], lw=1.5))

    for i in range(32):
        xc = i * 6 + 3
        t = xc / 192.0
        if t < 0.15: df = t/0.15; wf = (t/0.15)**0.5
        elif t > 0.85: df = (1-t)/0.15; wf = ((1-t)/0.15)**0.5
        else: df = 1.0; wf = 1.0
        fh = 17*df + 5; bl = 32*wf; cd = 17*df
        xl = xc - 2.75; fb = -1
        ax.add_patch(Rectangle((xl, fb), 5.5, fh, facecolor=COLORS['eps_foam'],
                     edgecolor=COLORS['gray_light'], lw=0.5, alpha=0.9))
        if cd > 2 and bl > 4:
            hb = min(bl/2, 2.45)
            cx, cy = [], []
            for j in range(21):
                f = j/20
                cx.append(xc - hb + 2*hb*f)
                cy.append(fb + fh - cd*(1-(2*f-1)**2)*0.6)
            cx += [xc+hb, xc-hb]; cy += [fb+fh+1, fb+fh+1]
            ax.add_patch(Polygon(list(zip(cx, cy)), facecolor=COLORS['white'],
                        edgecolor=COLORS['blue_med'], lw=0.8, zorder=3))

    # Cross-section inset
    iax = fig.add_axes([0.68, 0.15, 0.28, 0.40])
    iax.set_facecolor(COLORS['white'])
    iax.set_title('Cross-Section at Midship', fontsize=11, fontweight='bold', color=COLORS['blue_dark'])
    mx, my = [], []
    for i in range(51):
        f = i/50; mx.append(-16 + 32*f); my.append(17*(2*f-1)**2)
    iax.add_patch(Rectangle((-18, -2), 36, 24, facecolor=COLORS['eps_foam'],
                  edgecolor=COLORS['gray_dark'], lw=2))
    cvx = mx + [18, 18, -18, -18, mx[0]]
    cvy = my + [my[-1], 23, 23, my[0], my[0]]
    iax.add_patch(Polygon(list(zip(cvx, cvy)), facecolor=COLORS['white'],
                  edgecolor=COLORS['blue_med'], lw=2))
    iax.plot(mx, my, color=COLORS['blue_dark'], lw=3, zorder=5)
    iax.annotate('', xy=(-16, -4), xytext=(16, -4),
                 arrowprops=dict(arrowstyle='<->', color=COLORS['orange'], lw=2))
    iax.text(0, -5.5, '32"', ha='center', fontsize=10, fontweight='bold', color=COLORS['orange'])
    iax.annotate('', xy=(21, 0), xytext=(21, 17),
                 arrowprops=dict(arrowstyle='<->', color=COLORS['orange'], lw=2))
    iax.text(24, 8.5, '17"', ha='center', fontsize=10, fontweight='bold',
             color=COLORS['orange'], rotation=90)
    iax.set_xlim(-22, 26); iax.set_ylim(-8, 26); iax.set_aspect('equal'); iax.axis('off')

    ax.annotate('', xy=(0, -13), xytext=(192, -13),
                arrowprops=dict(arrowstyle='<->', color=COLORS['orange'], lw=2))
    ax.text(96, -14.5, '192" (16 ft)', ha='center', fontsize=13, fontweight='bold',
            color=COLORS['orange'])
    add_label_arrow(ax, 'EPS Foam Sections\n(6" spacing)', (50, 15), (50, 38), 12, COLORS['blue_dark'])
    add_label_arrow(ax, 'Concave Female\nMold Cavity', (96, 18), (140, 38), 12, COLORS['blue_med'])
    add_label_arrow(ax, 'MDF Strongback\nBase', (30, -3), (-5, 10), 11, COLORS['gray_dark'])
    ax.annotate('', xy=(6, 0), xytext=(12, 0),
                arrowprops=dict(arrowstyle='<->', color=COLORS['orange'], lw=1.5))
    ax.text(9, 2, '6"', ha='center', fontsize=9, fontweight='bold', color=COLORS['orange'])
    save_fig(fig, 'construction_step1_mold_build.png')


def generate_step2():
    print("Generating Step 2: Mold Surface Prep...")
    fig, ax = setup_fig('Step 2: Mold Surface Preparation\nSanded Smooth with PVA Release Agent')
    ax.set_xlim(-5, 45); ax.set_ylim(-5, 30); ax.set_aspect('equal'); ax.axis('off')
    beam, depth, n = 32, 17, 80
    mx, my = [], []
    for i in range(n+1):
        f = i/n; mx.append(5+beam*f); my.append(5+depth*(2*f-1)**2)
    ax.add_patch(Rectangle((2, 3), 38, 25, facecolor=COLORS['eps_foam'],
                 edgecolor=COLORS['gray_dark'], lw=2, zorder=1))
    cvx = mx + [40, 40, 2, 2, mx[0]]
    cvy = my + [my[-1], 29, 29, my[0], my[0]]
    ax.add_patch(Polygon(list(zip(cvx, cvy)), facecolor=COLORS['white'], edgecolor='none', zorder=2))
    ax.plot(mx, my, color=COLORS['gray_dark'], lw=3, zorder=5)

    for coat, off, col, alpha in [(1, 0.4, COLORS['pva'], 0.7), (2, 0.8, COLORS['green'], 0.6)]:
        px, py = offset_curve(mx, my, off)
        ax.plot(px, py, color=col, lw=4, zorder=5+coat, alpha=alpha)

    add_label_arrow(ax, 'EPS Foam\n(sanded smooth)', (10, 12), (-3, 18), 12, COLORS['gray_dark'])
    add_label_arrow(ax, 'PVA Release Agent\nCoat 1', (15, 9), (-2, 5), 11, COLORS['green_dark'])
    add_label_arrow(ax, 'PVA Release Agent\nCoat 2', (28, 11), (42, 18), 11, COLORS['green_dark'])
    add_label_arrow(ax, 'Smooth Mold\nInterior Surface', (21, 5.5), (21, -2), 12, COLORS['blue_dark'])

    cb = FancyBboxPatch((30, 24), 14, 5, boxstyle='round,pad=0.4',
                         facecolor=COLORS['blue_pale'], edgecolor=COLORS['blue_dark'], lw=2, zorder=10)
    ax.add_patch(cb)
    ax.text(37, 27.5, 'SURFACE FINISH', ha='center', va='center', fontsize=11,
            fontweight='bold', color=COLORS['blue_dark'])
    ax.text(37, 25.5, '220-grit final sand\n+ 2x PVA coats', ha='center', va='center',
            fontsize=9, color=COLORS['gray_dark'])

    iax = fig.add_axes([0.62, 0.15, 0.32, 0.35])
    iax.set_facecolor(COLORS['white'])
    iax.set_title('Surface Detail (zoomed)', fontsize=11, fontweight='bold', color=COLORS['blue_dark'])
    for y0, h, c, lb in [(0,3,COLORS['eps_foam'],'EPS Foam'),(3,0.3,COLORS['gray_light'],'Sanded Surface'),
                          (3.3,0.3,COLORS['pva'],'PVA Coat 1'),(3.6,0.3,COLORS['green'],'PVA Coat 2')]:
        iax.add_patch(Rectangle((0.5, y0), 8, h, facecolor=c, edgecolor=COLORS['gray_dark'], lw=1.5))
        iax.text(9.2, y0+h/2, lb, va='center', fontsize=9, fontweight='bold', color=COLORS['gray_dark'])
    iax.set_xlim(0, 16); iax.set_ylim(-0.5, 5); iax.set_aspect('equal'); iax.axis('off')
    ax.text(21, -4, 'PVA (polyvinyl alcohol) release agent ensures clean canoe demold',
            ha='center', fontsize=11, fontstyle='italic', color=COLORS['gray_med'])
    save_fig(fig, 'construction_step2_mold_surface.png')


def generate_step3():
    print("Generating Step 3: Reinforcement Placement...")
    fig, ax = setup_fig('Step 3: Basalt Fiber Mesh Reinforcement\nDraped into Female Mold')
    ax.set_xlim(-5, 45); ax.set_ylim(-5, 30); ax.set_aspect('equal'); ax.axis('off')
    beam, depth, n = 32, 17, 80
    mx, my = [], []
    for i in range(n+1):
        f = i/n; mx.append(5+beam*f); my.append(5+depth*(2*f-1)**2)
    ax.add_patch(Rectangle((2, 3), 38, 25, facecolor=COLORS['eps_foam'],
                 edgecolor=COLORS['gray_dark'], lw=2, zorder=1))
    cvx = mx + [40, 40, 2, 2, mx[0]]
    cvy = my + [my[-1], 29, 29, my[0], my[0]]
    ax.add_patch(Polygon(list(zip(cvx, cvy)), facecolor=COLORS['white'], edgecolor='none', zorder=2))
    ax.plot(mx, my, color=COLORS['gray_dark'], lw=3, zorder=4)

    px, py = offset_curve(mx, my, 0.5)
    ax.plot(px, py, color=COLORS['pva'], lw=3, zorder=5, alpha=0.6)
    mshx, mshy = offset_curve(mx, my, 1.0)
    ax.plot(mshx, mshy, color=COLORS['mesh'], lw=5, zorder=6, alpha=0.8)
    for i in range(0, n+1, 3):
        if 0 < i < n:
            dx = mx[i+1]-mx[i-1]; dy = my[i+1]-my[i-1]
            mag = max((dx**2+dy**2)**0.5, 1e-6)
            nx, ny = -dy/mag, dx/mag
            ax.plot([mshx[i]-nx*0.5, mshx[i]+nx*0.5], [mshy[i]-ny*0.5, mshy[i]+ny*0.5],
                    color=COLORS['mesh'], lw=1.5, zorder=7, alpha=0.6)
    ax.plot([mshx[0]-1, mshx[0]], [mshy[0]+2, mshy[0]], color=COLORS['mesh'], lw=5, alpha=0.5, zorder=6)
    ax.plot([mshx[-1], mshx[-1]+1], [mshy[-1], mshy[-1]+2], color=COLORS['mesh'], lw=5, alpha=0.5, zorder=6)

    add_label_arrow(ax, 'Basalt Fiber Mesh\n(draped into mold)', (21, 7), (21, -2), 13, COLORS['orange'])
    add_label_arrow(ax, 'PVA Release\nLayer Below', (12, 10), (-3, 14), 11, COLORS['green_dark'])
    add_label_arrow(ax, 'Mesh Overlap\nat Gunwale', (38, 23), (42, 27), 11, COLORS['orange'])
    add_label_arrow(ax, 'Female Mold\nCavity', (30, 14), (42, 10), 12, COLORS['blue_dark'])

    ib = FancyBboxPatch((0, 24), 18, 5, boxstyle='round,pad=0.4',
                         facecolor=COLORS['orange_light'], edgecolor=COLORS['orange'], lw=2, alpha=0.3, zorder=10)
    ax.add_patch(ib)
    ax.text(9, 27.5, 'BASALT MESH', ha='center', va='center', fontsize=11,
            fontweight='bold', color=COLORS['orange'])
    ax.text(9, 25.5, 'Alkali-resistant\nHigh tensile strength', ha='center', va='center',
            fontsize=9, color=COLORS['gray_dark'])
    save_fig(fig, 'construction_step3_reinforcement.png')


def generate_step4():
    print("Generating Step 4: Concrete Application...")
    fig, ax = setup_fig('Step 4: Two-Lift Concrete Application\nFirst Lift, Mesh, Second Lift (0.5" Total)')
    ax.set_xlim(-5, 45); ax.set_ylim(-5, 32); ax.set_aspect('equal'); ax.axis('off')
    beam, depth, n = 32, 17, 80
    mx, my = [], []
    for i in range(n+1):
        f = i/n; mx.append(5+beam*f); my.append(5+depth*(2*f-1)**2)
    ax.add_patch(Rectangle((2, 3), 38, 25, facecolor=COLORS['eps_foam'],
                 edgecolor=COLORS['gray_dark'], lw=2, zorder=1))
    cvx = mx + [40, 40, 2, 2, mx[0]]
    cvy = my + [my[-1], 29, 29, my[0], my[0]]
    ax.add_patch(Polygon(list(zip(cvx, cvy)), facecolor=COLORS['white'], edgecolor='none', zorder=2))
    ax.plot(mx, my, color=COLORS['gray_dark'], lw=2, zorder=4)

    # First lift
    l1x, l1y = offset_curve(mx, my, 1.1)
    fx = mx + l1x[::-1]; fy = my + l1y[::-1]
    ax.add_patch(Polygon(list(zip(fx, fy)), facecolor=COLORS['concrete'],
                 edgecolor=COLORS['concrete_dark'], lw=1, zorder=5, alpha=0.9))
    # Mesh
    mshx, mshy = offset_curve(mx, my, 1.2)
    ax.plot(mshx, mshy, color=COLORS['mesh'], lw=4, zorder=7, alpha=0.8)
    for i in range(0, n+1, 4):
        if 0 < i < n:
            dx = mshx[min(i+1,n)]-mshx[max(i-1,0)]; dy = mshy[min(i+1,n)]-mshy[max(i-1,0)]
            mag = max((dx**2+dy**2)**0.5, 1e-6)
            nx, ny = -dy/mag, dx/mag
            ax.plot([mshx[i]-nx*0.4, mshx[i]+nx*0.4], [mshy[i]-ny*0.4, mshy[i]+ny*0.4],
                    color=COLORS['mesh'], lw=1.2, zorder=8, alpha=0.5)
    # Second lift
    l2ix, l2iy = offset_curve(mx, my, 1.3)
    l2ox, l2oy = offset_curve(mx, my, 2.8)
    f2x = l2ix + l2ox[::-1]; f2y = l2iy + l2oy[::-1]
    ax.add_patch(Polygon(list(zip(f2x, f2y)), facecolor=COLORS['concrete_dark'],
                 edgecolor=COLORS['concrete_dark'], lw=1, zorder=6, alpha=0.8))

    # Trowel
    tc = 27; tf = (tc-5)/beam; ty = 5 + depth*(2*tf-1)**2 + 4
    ax.add_patch(Polygon([(tc-3,ty),(tc+3,ty-0.3),(tc+3,ty+0.3),(tc-3,ty+0.6)],
                 facecolor=COLORS['gray_light'], edgecolor=COLORS['gray_dark'], lw=1.5, zorder=12))
    ax.plot([tc+3, tc+5.5], [ty, ty+2], color=COLORS['mdf'], lw=4, zorder=12, solid_capstyle='round')
    for dx in [-2, 0, 2]:
        ax.annotate('', xy=(tc+dx-1.5, ty-1), xytext=(tc+dx+1.5, ty-1),
                    arrowprops=dict(arrowstyle='->', color=COLORS['orange'], lw=1, alpha=0.5))

    add_label_arrow(ax, 'FIRST LIFT\nConcrete (0.2")', (14, 8), (-3, 2), 12, COLORS['blue_dark'])
    add_label_arrow(ax, 'Basalt Mesh\nLayer', (11, 10.5), (-3, 14), 11, COLORS['orange'])
    add_label_arrow(ax, 'SECOND LIFT\nConcrete (0.3")', (17, 11), (-3, 20), 12, COLORS['blue_dark'])
    add_label_arrow(ax, 'Trowel\nSmoothing', (tc+4, ty+1), (42, 28), 11, COLORS['gray_dark'])
    add_label_arrow(ax, 'Mold Surface\n(outer face of canoe)', (28, 7.5), (42, 3), 11, COLORS['gray_dark'])

    cb = FancyBboxPatch((0.5, 25), 14, 5, boxstyle='round,pad=0.4',
                         facecolor=COLORS['blue_pale'], edgecolor=COLORS['blue_dark'], lw=2, zorder=10)
    ax.add_patch(cb)
    ax.text(7.5, 28, 'TOTAL THICKNESS', ha='center', va='center', fontsize=10,
            fontweight='bold', color=COLORS['blue_dark'])
    ax.text(7.5, 26, '0.5" (0.2" + mesh + 0.3")', ha='center', va='center',
            fontsize=9, color=COLORS['gray_dark'])
    save_fig(fig, 'construction_step4_concrete_application.png')


def generate_step5():
    print("Generating Step 5: Curing...")
    fig, ax = setup_fig('Step 5: Moist Curing Process\n7-Day Controlled Environment')
    ax.set_xlim(-10, 210); ax.set_ylim(-20, 55); ax.set_aspect('equal'); ax.axis('off')

    ax.add_patch(Rectangle((5, 0), 190, 3, facecolor=COLORS['mdf'], edgecolor=COLORS['gray_dark'], lw=2))
    for lx in [15, 85, 115, 185]:
        ax.add_patch(Rectangle((lx, -15), 4, 15, facecolor=COLORS['mdf'],
                     edgecolor=COLORS['gray_dark'], lw=1.5))
    ax.add_patch(Polygon([(10,3),(190,3),(190,28),(10,28)], facecolor=COLORS['eps_foam'],
                 edgecolor=COLORS['gray_dark'], lw=2, zorder=2))

    hx = np.linspace(10, 190, 100)
    hb = []
    for x in hx:
        t = (x-10)/180
        if t < 0.12: h = 15*(t/0.12)**0.7
        elif t > 0.88: h = 15*((1-t)/0.12)**0.7
        else: h = 15
        hb.append(3 + 22 - h)
    ax.add_patch(Polygon(list(zip(hx, hb)) + [(190,28),(10,28)], facecolor=COLORS['concrete'],
                 edgecolor=COLORS['concrete_dark'], lw=1, zorder=3, alpha=0.7))

    px = np.linspace(5, 195, 150)
    py = [30 + 3*np.sin(np.pi*(x-5)/190) + 1.5*np.sin(3*np.pi*(x-5)/190 + 0.5) for x in px]
    ax.fill_between(px, 28, py, facecolor=COLORS['plastic'], edgecolor=COLORS['blue_light'],
                     lw=2, alpha=0.4, zorder=5)
    ax.plot(px, py, color=COLORS['blue_med'], lw=2.5, zorder=6)
    ax.plot([5,5], [28, py[0]-2], color=COLORS['blue_med'], lw=2, zorder=6)
    ax.plot([195,195], [28, py[-1]-2], color=COLORS['blue_med'], lw=2, zorder=6)

    np.random.seed(42)
    for _ in range(20):
        mx = np.random.uniform(20, 180); my = np.random.uniform(32, 42)
        ax.add_patch(Polygon([(mx,my+1.2),(mx-0.5,my),(mx,my-0.3),(mx+0.5,my)],
                     facecolor=COLORS['blue_light'], edgecolor=COLORS['blue_med'], lw=0.5, alpha=0.6, zorder=7))

    tx, ty = 200, 20
    ax.plot([tx,tx], [ty-5,ty+8], color=COLORS['gray_dark'], lw=4, solid_capstyle='round', zorder=8)
    ax.plot([tx,tx], [ty-5,ty+4], color='#E04040', lw=2.5, solid_capstyle='round', zorder=9)
    ax.add_patch(Circle((tx, ty-5), 1.5, facecolor='#E04040', edgecolor=COLORS['gray_dark'], lw=1.5, zorder=9))
    ax.text(tx, ty+10, '70\u00b0F', ha='center', fontsize=12, fontweight='bold', color='#E04040')

    cb = FancyBboxPatch((50, 38), 100, 12, boxstyle='round,pad=0.8',
                         facecolor=COLORS['blue_dark'], edgecolor=COLORS['orange'], lw=3, zorder=10, alpha=0.95)
    ax.add_patch(cb)
    ax.text(100, 46, '7 DAY MOIST CURE', ha='center', va='center', fontsize=22,
            fontweight='bold', color=COLORS['white'], zorder=11)
    ax.text(100, 40.5, 'Plastic sheeting  |  Water mist daily  |  70\u00b0F maintained',
            ha='center', va='center', fontsize=12, color=COLORS['blue_pale'], zorder=11)

    add_label_arrow(ax, 'Plastic Sheeting\n(moisture barrier)', (60, 34), (20, 42), 11, COLORS['blue_med'])
    add_label_arrow(ax, 'Concrete Canoe\nin Female Mold', (100, 15), (100, -8), 12, COLORS['gray_dark'])
    add_label_arrow(ax, 'Water Mist\n(daily application)', (140, 37), (175, 45), 11, COLORS['blue_light'])
    add_label_arrow(ax, 'MDF Table', (50, 1.5), (20, -10), 10, COLORS['gray_dark'])
    save_fig(fig, 'construction_step5_curing.png')


def generate_step6():
    print("Generating Step 6: Demold...")
    fig, ax = setup_fig('Step 6: Demolding\nCanoe Lifted from Female Mold')
    ax.set_xlim(-10, 210); ax.set_ylim(-20, 70); ax.set_aspect('equal'); ax.axis('off')

    ax.add_patch(Rectangle((10, -5), 180, 3, facecolor=COLORS['mdf'],
                 edgecolor=COLORS['gray_dark'], lw=2, zorder=1))
    ax.add_patch(Rectangle((15, -2), 170, 20, facecolor=COLORS['eps_foam'],
                 edgecolor=COLORS['gray_dark'], lw=2, zorder=2))

    cx = np.linspace(20, 180, 80)
    cb = []
    for x in cx:
        t = (x-20)/160
        if t < 0.12: d = 14*(t/0.12)**0.7
        elif t > 0.88: d = 14*((1-t)/0.12)**0.7
        else: d = 14
        cb.append(-2 + 18 - d)
    ax.add_patch(Polygon(list(zip(cx, cb)) + [(180,18),(20,18)], facecolor=COLORS['white'],
                 edgecolor=COLORS['blue_med'], lw=1.5, zorder=3))

    lh = 25
    co, ci = [], []
    for x in cx:
        t = (x-20)/160
        if t < 0.12: d = 14*(t/0.12)**0.7
        elif t > 0.88: d = 14*((1-t)/0.12)**0.7
        else: d = 14
        co.append(lh + 18 - d); ci.append(lh + 18 - d + 2)
    ax.add_patch(Polygon(list(zip(cx, co)) + list(zip(cx[::-1], ci[::-1])),
                 facecolor=COLORS['concrete'], edgecolor=COLORS['concrete_dark'], lw=2, zorder=5))
    ax.plot([20,20], [co[0],ci[0]], color=COLORS['concrete_dark'], lw=2, zorder=6)
    ax.plot([180,180], [co[-1],ci[-1]], color=COLORS['concrete_dark'], lw=2, zorder=6)

    for ax_ in [50, 100, 150]:
        ax.annotate('', xy=(ax_, lh+20), xytext=(ax_, lh-3),
                    arrowprops=dict(arrowstyle='->', color=COLORS['orange'], lw=2.5, mutation_scale=20))

    for fx in [30, 60, 90, 110, 140, 170]:
        fb = lh + 20; hy = fb + 16; by = fb + 8
        ax.add_patch(Circle((fx, hy), 2, facecolor=COLORS['blue_pale'],
                     edgecolor=COLORS['blue_dark'], lw=1.5, zorder=8))
        ax.plot([fx,fx], [hy-2, by], color=COLORS['blue_dark'], lw=2, zorder=7)
        ax.plot([fx,fx-3], [by, fb], color=COLORS['blue_dark'], lw=2, zorder=7)
        ax.plot([fx,fx+3], [by, fb], color=COLORS['blue_dark'], lw=2, zorder=7)
        idx = np.argmin(np.abs(cx - fx))
        at = ci[idx]
        ax.plot([fx,fx-2], [by+3, at+1], color=COLORS['blue_dark'], lw=2, zorder=7)
        ax.plot([fx,fx+2], [by+3, at+1], color=COLORS['blue_dark'], lw=2, zorder=7)

    add_label_arrow(ax, 'Smooth Outer\nSurface', (100, co[40]-2), (100, -10), 13, COLORS['blue_dark'])
    add_label_arrow(ax, 'Empty Female\nMold Below', (60, 8), (15, -12), 11, COLORS['gray_dark'])
    add_label_arrow(ax, '6-Person\nLift Team', (170, 60), (195, 60), 12, COLORS['blue_dark'])
    ax.text(100, lh-6, 'LIFT', ha='center', fontsize=16, fontweight='bold', color=COLORS['orange'], zorder=10)

    nb = FancyBboxPatch((55, -18), 90, 7, boxstyle='round,pad=0.5',
                         facecolor=COLORS['blue_pale'], edgecolor=COLORS['blue_dark'], lw=2, zorder=10, alpha=0.9)
    ax.add_patch(nb)
    ax.text(100, -14.5, 'Female mold produces smooth outer surface - no sanding needed!',
            ha='center', va='center', fontsize=11, fontweight='bold', color=COLORS['blue_dark'], zorder=11)
    save_fig(fig, 'construction_step6_demold.png')


def generate_step7():
    print("Generating Step 7: Finishing...")
    fig, ax = setup_fig('Step 7: Finishing & Graphics\nSealed Surface with Team Branding')
    ax.set_xlim(-10, 210); ax.set_ylim(-15, 45); ax.set_aspect('equal'); ax.axis('off')

    cx = np.linspace(10, 190, 100)
    ct, cb = np.zeros_like(cx), np.zeros_like(cx)
    for i, x in enumerate(cx):
        t = (x-10)/180
        if t < 0.12: h = 14*(t/0.12)**0.6
        elif t > 0.88: h = 14*((1-t)/0.12)**0.6
        else: h = 14
        ct[i] = 20; cb[i] = 20 - h
    ax.add_patch(Polygon(list(zip(cx, cb)) + list(zip(cx[::-1], ct[::-1])),
                 facecolor=COLORS['concrete'], edgecolor=COLORS['concrete_dark'], lw=2, zorder=3))

    sx = np.linspace(15, 185, 80)
    sy = []
    for x in sx:
        t = (x-10)/180
        if t < 0.12: h = 14*(t/0.12)**0.6
        elif t > 0.88: h = 14*((1-t)/0.12)**0.6
        else: h = 14
        sy.append(20 - h*0.5)
    ax.plot(sx, sy, color=COLORS['blue_light'], lw=2, alpha=0.4, zorder=4, linestyle='--')

    gp = []
    for x in np.linspace(60, 140, 40): gp.append((x, 20-14*0.15))
    for x in np.linspace(140, 60, 40): gp.append((x, 20-14*0.85))
    ax.add_patch(Polygon(gp, facecolor=COLORS['orange_light'], edgecolor=COLORS['orange'],
                 lw=2, alpha=0.3, zorder=5, linestyle='--'))

    ax.text(100, 12, 'NAU', ha='center', va='center', fontsize=28, fontweight='bold',
            color=COLORS['blue_dark'], alpha=0.6, zorder=6)
    ax.text(100, 7.5, 'LUMBERJACKS', ha='center', va='center', fontsize=16,
            fontweight='bold', color=COLORS['orange'], alpha=0.5, zorder=6)
    ax.plot(cx, ct, color=COLORS['blue_dark'], lw=4, zorder=7)
    ax.axhline(y=14, color=COLORS['blue_light'], lw=1, linestyle=':', alpha=0.5, xmin=0.05, xmax=0.95, zorder=2)
    ax.text(195, 14, 'Waterline', fontsize=9, color=COLORS['blue_light'], va='center')

    add_label_arrow(ax, 'Sealed Surface\n(waterproofing sealer)', (40, 10), (-5, 0), 12, COLORS['blue_dark'])
    add_label_arrow(ax, 'Team Graphics\nArea', (120, 9), (155, -5), 12, COLORS['orange'])
    add_label_arrow(ax, 'Gunwale Edge\n(reinforced)', (70, 20), (40, 30), 12, COLORS['blue_dark'])
    ax.text(13, 17, 'BOW', fontsize=12, fontweight='bold', color=COLORS['gray_dark'], ha='center', rotation=30)
    ax.text(187, 17, 'STERN', fontsize=12, fontweight='bold', color=COLORS['gray_dark'], ha='center', rotation=-30)

    clb = FancyBboxPatch((5, 28), 65, 14, boxstyle='round,pad=0.5',
                          facecolor=COLORS['blue_pale'], edgecolor=COLORS['blue_dark'], lw=2, zorder=10, alpha=0.9)
    ax.add_patch(clb)
    ax.text(37, 39, 'FINISHING CHECKLIST', ha='center', fontsize=12,
            fontweight='bold', color=COLORS['blue_dark'], zorder=11)
    for i, c in enumerate(['> Sand any imperfections', '> Apply concrete sealer (2 coats)',
                           '> Apply team graphics/decals', '> Seal gunwale edges']):
        ax.text(10, 36-i*2.5, c, fontsize=9, color=COLORS['gray_dark'], zorder=11)
    save_fig(fig, 'construction_step7_finishing.png')


def generate_step8():
    print("Generating Step 8: Construction Timeline...")
    fig, ax = setup_fig('Construction Overview Timeline\n21-Day Build Schedule')
    steps = [
        ('Step 1: Mold Build', 1, 5, COLORS['blue_dark']),
        ('Step 2: Surface Prep', 6, 7, COLORS['blue_med']),
        ('Step 3: Reinforcement', 8, 8, COLORS['blue_light']),
        ('Step 4: Concrete', 9, 10, COLORS['concrete_dark']),
        ('Step 5: Curing', 11, 17, COLORS['green']),
        ('Step 6: Demold', 18, 18, COLORS['orange']),
        ('Step 7: Finishing', 19, 21, COLORS['orange_light']),
    ]
    ax.set_xlim(0, 23); ax.set_ylim(-1, len(steps)+0.5)
    ax.set_xlabel('Day', fontsize=14, fontweight='bold', color=COLORS['gray_dark'])
    for d in range(1, 22):
        ax.axvline(x=d, color=COLORS['gray_pale'], lw=0.5, zorder=0)
    for i, (name, s, e, col) in enumerate(steps):
        y = len(steps)-1-i; dur = e-s+1
        ax.add_patch(FancyBboxPatch((s-0.4, y-0.35), dur+0.8-1, 0.7, boxstyle='round,pad=0.15',
                     facecolor=col, edgecolor='white', lw=2, zorder=3, alpha=0.9))
        ax.text(-0.2, y, name, ha='right', va='center', fontsize=12, fontweight='bold', color=COLORS['gray_dark'])
        if dur > 2:
            lb = f'Days {s}-{e}' if s != e else f'Day {s}'
            ax.text((s+e)/2, y, lb, ha='center', va='center', fontsize=10, fontweight='bold', color='white', zorder=4)
        else:
            lb = f'Day {s}' if s == e else f'D{s}-{e}'
            ax.text((s+e)/2, y, lb, ha='center', va='center', fontsize=9, fontweight='bold', color='white', zorder=4)
    ax.set_xticks(range(1, 22)); ax.set_xticklabels(range(1, 22), fontsize=10); ax.set_yticks([])
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False); ax.spines['bottom'].set_color(COLORS['gray_light'])

    for day, lb, col in [(8,'Mesh\nPlaced',COLORS['blue_light']),(10,'Concrete\nComplete',COLORS['concrete_dark']),
                          (18,'DEMOLD\nDAY!',COLORS['orange'])]:
        ax.plot(day, -0.7, marker='^', markersize=12, color=col, zorder=5)
        ax.text(day, -1.2, lb, ha='center', va='top', fontsize=8, fontweight='bold', color=col)
    for we in [7, 14, 21]:
        ax.axvline(x=we+0.5, color=COLORS['gray_med'], lw=1.5, linestyle='--', alpha=0.5, zorder=1)
    ax.text(4, len(steps)+0.3, 'Week 1', ha='center', fontsize=11, fontweight='bold', color=COLORS['gray_med'])
    ax.text(11, len(steps)+0.3, 'Week 2', ha='center', fontsize=11, fontweight='bold', color=COLORS['gray_med'])
    ax.text(18.5, len(steps)+0.3, 'Week 3', ha='center', fontsize=11, fontweight='bold', color=COLORS['gray_med'])
    plt.subplots_adjust(left=0.22, right=0.95, top=0.88, bottom=0.12)
    save_fig(fig, 'construction_overview_timeline.png')


def generate_step9():
    print("Generating Step 9: Materials List...")
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    fig.patch.set_facecolor(COLORS['bg'])
    fig.suptitle('Construction Materials & Cost Breakdown', fontsize=24,
                 fontweight='bold', color=COLORS['blue_dark'], y=0.96)
    fig.text(0.98, 0.02, BRAND_TEXT, fontsize=11, color=COLORS['blue_med'],
             ha='right', va='bottom', fontweight='bold', fontstyle='italic')

    am = fig.add_axes([0.05, 0.15, 0.42, 0.72]); am.set_facecolor(COLORS['white']); am.axis('off')
    am.add_patch(FancyBboxPatch((0.02, 0.88), 0.96, 0.10, boxstyle='round,pad=0.02',
                 facecolor=COLORS['blue_dark'], edgecolor='none', transform=am.transAxes, zorder=5))
    am.text(0.5, 0.93, 'MOLD MATERIALS', ha='center', va='center', transform=am.transAxes,
            fontsize=16, fontweight='bold', color='white', zorder=6)
    mitems = [('EPS Foam Blocks','24 sheets (2" thick)','$360'),('MDF Strongback',"4'x16' platform",'$80'),
              ('Foam Adhesive','Construction grade','$50'),('PVA Release Agent','2 gallons','$25'),
              ('Sandpaper (assorted)','60-220 grit','$40'),('Misc (screws, tape)','Various','$95'),
              ('Tools & Safety','PPE, blades, etc.','$200')]
    for i, (it, sp, co) in enumerate(mitems):
        y = 0.82 - i*0.09; bg = COLORS['white'] if i%2==0 else COLORS['gray_pale']
        am.add_patch(FancyBboxPatch((0.02, y-0.03), 0.96, 0.07, boxstyle='round,pad=0.01',
                     facecolor=bg, edgecolor=COLORS['gray_light'], lw=0.5, transform=am.transAxes, zorder=2))
        am.text(0.05, y, it, ha='left', va='center', transform=am.transAxes, fontsize=11,
                fontweight='bold', color=COLORS['gray_dark'], zorder=3)
        am.text(0.55, y, sp, ha='left', va='center', transform=am.transAxes, fontsize=10,
                color=COLORS['gray_med'], zorder=3)
        am.text(0.93, y, co, ha='right', va='center', transform=am.transAxes, fontsize=12,
                fontweight='bold', color=COLORS['blue_dark'], zorder=3)
    ys = 0.82 - len(mitems)*0.09 - 0.02
    am.add_patch(FancyBboxPatch((0.02, ys-0.03), 0.96, 0.07, boxstyle='round,pad=0.01',
                 facecolor=COLORS['blue_pale'], edgecolor=COLORS['blue_dark'], lw=2, transform=am.transAxes, zorder=4))
    am.text(0.05, ys, 'SUBTOTAL', ha='left', va='center', transform=am.transAxes,
            fontsize=13, fontweight='bold', color=COLORS['blue_dark'], zorder=5)
    am.text(0.93, ys, '$850', ha='right', va='center', transform=am.transAxes,
            fontsize=14, fontweight='bold', color=COLORS['blue_dark'], zorder=5)

    ac = fig.add_axes([0.53, 0.15, 0.42, 0.72]); ac.set_facecolor(COLORS['white']); ac.axis('off')
    ac.add_patch(FancyBboxPatch((0.02, 0.88), 0.96, 0.10, boxstyle='round,pad=0.02',
                 facecolor=COLORS['orange'], edgecolor='none', transform=ac.transAxes, zorder=5))
    ac.text(0.5, 0.93, 'CANOE MATERIALS', ha='center', va='center', transform=ac.transAxes,
            fontsize=16, fontweight='bold', color='white', zorder=6)
    citems = [('Concrete Mix','Custom lightweight','$200'),('Basalt Fiber Mesh','50 sq ft roll','$120'),
              ('Concrete Sealer','Penetrating type','$60'),('Team Graphics','Vinyl decals','$50'),
              ('Misc Supplies','Trowels, forms, etc.','$150')]
    for i, (it, sp, co) in enumerate(citems):
        y = 0.82 - i*0.09; bg = COLORS['white'] if i%2==0 else COLORS['gray_pale']
        ac.add_patch(FancyBboxPatch((0.02, y-0.03), 0.96, 0.07, boxstyle='round,pad=0.01',
                     facecolor=bg, edgecolor=COLORS['gray_light'], lw=0.5, transform=ac.transAxes, zorder=2))
        ac.text(0.05, y, it, ha='left', va='center', transform=ac.transAxes, fontsize=11,
                fontweight='bold', color=COLORS['gray_dark'], zorder=3)
        ac.text(0.55, y, sp, ha='left', va='center', transform=ac.transAxes, fontsize=10,
                color=COLORS['gray_med'], zorder=3)
        ac.text(0.93, y, co, ha='right', va='center', transform=ac.transAxes, fontsize=12,
                fontweight='bold', color=COLORS['orange'], zorder=3)
    ys2 = 0.82 - len(citems)*0.09 - 0.02
    ac.add_patch(FancyBboxPatch((0.02, ys2-0.03), 0.96, 0.07, boxstyle='round,pad=0.01',
                 facecolor=COLORS['orange_light'], edgecolor=COLORS['orange'], lw=2, transform=ac.transAxes, zorder=4))
    ac.text(0.05, ys2, 'SUBTOTAL', ha='left', va='center', transform=ac.transAxes,
            fontsize=13, fontweight='bold', color=COLORS['orange'], zorder=5)
    ac.text(0.93, ys2, '$580', ha='right', va='center', transform=ac.transAxes,
            fontsize=14, fontweight='bold', color=COLORS['orange'], zorder=5)

    ta = fig.add_axes([0.15, 0.03, 0.70, 0.08]); ta.axis('off')
    ta.add_patch(FancyBboxPatch((0.05, 0.1), 0.90, 0.8, boxstyle='round,pad=0.03',
                 facecolor=COLORS['blue_dark'], edgecolor=COLORS['orange'], lw=3, transform=ta.transAxes, zorder=5))
    ta.text(0.3, 0.5, 'GRAND TOTAL', ha='center', va='center', transform=ta.transAxes,
            fontsize=18, fontweight='bold', color='white', zorder=6)
    ta.text(0.7, 0.5, '$1,430', ha='center', va='center', transform=ta.transAxes,
            fontsize=26, fontweight='bold', color=COLORS['orange_light'], zorder=6)
    save_fig(fig, 'construction_materials_list.png')


def generate_step10():
    print("Generating Step 10: Wall Cross-Section Detail...")
    fig, ax = setup_fig('Wall Cross-Section Detail\nLayered Construction (0.5" Total Thickness)')
    ax.set_xlim(-2, 20); ax.set_ylim(-1, 12); ax.set_aspect('equal'); ax.axis('off')

    lw = 14; xs = 1
    layers = [(1.5, COLORS['blue_pale'], 'Smooth Outer Surface\n(from female mold)', ''),
              (2.5, COLORS['concrete'], 'Concrete Layer 1 (First Lift)', '0.2"'),
              (0.6, COLORS['mesh'], 'Basalt Fiber Mesh', ''),
              (3.5, COLORS['concrete_dark'], 'Concrete Layer 2 (Second Lift)', '0.3"'),
              (1.0, COLORS['gray_pale'], 'Inner Surface (troweled)', '')]
    yc = 0; lpos = []
    for h, col, lb, tl in layers:
        ax.add_patch(FancyBboxPatch((xs, yc), lw, h, boxstyle='round,pad=0.05',
                     facecolor=col, edgecolor=COLORS['gray_dark'], lw=1.5, zorder=3))
        lpos.append((yc, h, lb, tl)); yc += h

    for y0, h, lb, tl in lpos:
        ym = y0 + h/2
        ax.text(xs+lw+0.5, ym, lb, ha='left', va='center', fontsize=11, fontweight='bold',
                color=COLORS['gray_dark'], bbox=dict(boxstyle='round,pad=0.2',
                facecolor=COLORS['white'], edgecolor=COLORS['gray_light'], alpha=0.9))
        ax.annotate('', xy=(xs+lw, ym), xytext=(xs+lw+0.4, ym),
                    arrowprops=dict(arrowstyle='->', color=COLORS['gray_dark'], lw=1))

    # Dimension arrows
    for idx, lwidth in [(1, 2), (2, 1.5), (3, 2)]:
        y0 = lpos[idx][0]; h = lpos[idx][1]
        ax.annotate('', xy=(xs-0.8, y0), xytext=(xs-0.8, y0+h),
                    arrowprops=dict(arrowstyle='<->', color=COLORS['orange'], lw=lwidth))
    ax.text(xs-1.2, lpos[1][0]+lpos[1][1]/2, '0.2"', ha='right', va='center',
            fontsize=12, fontweight='bold', color=COLORS['orange'])
    ax.text(xs-1.2, lpos[2][0]+lpos[2][1]/2, 'mesh', ha='right', va='center',
            fontsize=10, fontweight='bold', color=COLORS['orange'])
    ax.text(xs-1.2, lpos[3][0]+lpos[3][1]/2, '0.3"', ha='right', va='center',
            fontsize=12, fontweight='bold', color=COLORS['orange'])

    ty0 = lpos[1][0]; ty1 = lpos[3][0]+lpos[3][1]
    ax.annotate('', xy=(xs-2.2, ty0), xytext=(xs-2.2, ty1),
                arrowprops=dict(arrowstyle='<->', color=COLORS['blue_dark'], lw=2.5))
    ax.text(xs-2.5, (ty0+ty1)/2, '0.5"\nTOTAL', ha='right', va='center',
            fontsize=13, fontweight='bold', color=COLORS['blue_dark'])
    ax.text(xs+lw/2, -0.7, 'OUTSIDE (water side)', ha='center', fontsize=13,
            fontweight='bold', color=COLORS['blue_med'])
    ax.text(xs+lw/2, yc+0.5, 'INSIDE (paddler side)', ha='center', fontsize=13,
            fontweight='bold', color=COLORS['blue_med'])

    inset = fig.add_axes([0.62, 0.15, 0.32, 0.30])
    inset.set_facecolor(COLORS['white'])
    inset.set_title('Basalt Mesh Weave (detail)', fontsize=10, fontweight='bold', color=COLORS['blue_dark'])
    ws = 10
    for i in range(ws+1):
        for j in range(ws):
            z = 3 if (i+j)%2==0 else 1; a = 1.0 if (i+j)%2==0 else 0.5
            inset.plot([j, j+1], [i, i], color=COLORS['mesh'], lw=3, zorder=z, alpha=a, solid_capstyle='round')
            z2 = 2 if (i+j)%2==0 else 4; a2 = 1.0 if (i+j)%2==0 else 0.7
            inset.plot([i, i], [j, j+1], color='#B8892B', lw=3, zorder=z2, alpha=a2, solid_capstyle='round')
    inset.set_xlim(-0.5, ws+0.5); inset.set_ylim(-0.5, ws+0.5); inset.set_aspect('equal'); inset.axis('off')
    fig.text(0.5, 0.04, 'Note: Layer thicknesses shown exaggerated for clarity. Actual total wall thickness is 0.5 inches.',
             ha='center', fontsize=10, fontstyle='italic', color=COLORS['gray_med'])
    save_fig(fig, 'construction_cross_section_detail.png')


def main():
    print("=" * 60)
    print("NAU ASCE 2026 Concrete Canoe Construction Step Generator")
    print("Female Mold Process - 10 Diagrams")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    generate_step1()
    generate_step2()
    generate_step3()
    generate_step4()
    generate_step5()
    generate_step6()
    generate_step7()
    generate_step8()
    generate_step9()
    generate_step10()
    print()
    print("=" * 60)
    print("All 10 construction diagrams generated successfully!")
    print("=" * 60)
    files = sorted([f for f in os.listdir(OUTPUT_DIR) if f.startswith('construction_') and f.endswith('.png')])
    print(f"\nGenerated files ({len(files)}):")
    for f in files:
        p = os.path.join(OUTPUT_DIR, f)
        print(f"  {f:55s}  ({os.path.getsize(p)/1024:.0f} KB)")

if __name__ == '__main__':
    main()
