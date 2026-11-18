"""Top-view drawing of the modelled antenna (same equations as sir_dipole.py), with key dimensions."""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

L1, L2, L3, W1, W2, R1, R2, C, G, H = 9.62, 6.7, 7.7, 2, 0.2, 7, 9, 0.4, 1, 4.1
yt = -(R1 - H); yb = yt + C; ytop = yb + W1; xin = L1 / 2; xout = xin + L2
yleg = ytop - L3; yc = (ytop + yb) / 2; ysub_top = ytop + 0.25; ysub_bot = ysub_top - 9

def arm(s):
    a_in = np.linspace(np.arcsin(G / 2 / R1), np.arccos(-yt / R1), 60)
    a_out = np.linspace(np.arccos(-yt / R2), np.arcsin(G / 2 / R2), 60)
    return np.r_[np.c_[s * R1 * np.sin(a_in), -R1 * np.cos(a_in)], np.c_[s * R2 * np.sin(a_out), -R2 * np.cos(a_out)]]

def draw(ax, case='e', dims=True):
    ax.add_patch(Rectangle((-12.5, ysub_bot), 25, 9, fc='#cfe3c4', ec='k', lw=.8))
    cu = dict(fc='#b8732e', ec='#5a3510', lw=.6)
    if case in ('c', 'd', 'e', 'bent'):
        for s in (1, -1): ax.add_patch(Polygon(arm(s), **cu))
    else:
        al = 9.098
        for s in (1, -1): ax.add_patch(Rectangle((min(s * G / 2, s * (G / 2 + al)), -R2), al, 2, **cu))
    if case in ('b', 'c'):
        ax.add_patch(Rectangle((-xout, yb), 2 * xout, W1, **cu))
    if case in ('d', 'e'):
        for s in (1, -1):
            ax.add_patch(Rectangle((min(s * xin, s * xout), yb), L2, W1, **cu))
            ax.add_patch(Rectangle((min(s * (xout - W1), s * xout), yleg), W1, L3, **cu))
        if case == 'e': ax.add_patch(Rectangle((-xin, yc - W2 / 2), L1, W2, **cu))
        else: ax.add_patch(Rectangle((-xin, yb), L1, W1, **cu))
    ax.add_patch(Rectangle((-G / 2, -R2), G, 2, fc='red', ec='red', alpha=.7))
    ax.set_xlim(-13.5, 13.5); ax.set_ylim(ysub_bot - 1, ysub_top + 1); ax.set_aspect('equal')
    if dims:
        kw = dict(arrowprops=dict(arrowstyle='<->', lw=.8), annotation_clip=False)
        ax.annotate('', (-xin, ytop + .6), (xin, ytop + .6), **kw); ax.text(0, ytop + .75, 'L1 = 9.62', ha='center', fontsize=8)
        ax.annotate('', (xin, ytop + .6), (xout, ytop + .6), **kw); ax.text((xin + xout) / 2, ytop + .75, 'L2 = 6.7', ha='center', fontsize=8)
        ax.annotate('', (xout + .5, ytop), (xout + .5, yleg), **kw); ax.text(xout + .7, (ytop + yleg) / 2, 'L3 = 7.7', rotation=90, va='center', fontsize=8)
        ax.annotate('', (0, 0), (R2 * np.sin(-0.6), -R2 * np.cos(0.6)), arrowprops=dict(arrowstyle='->', lw=.7))
        ax.text(-3.4, -4.2, 'R2 = 9', fontsize=8); ax.text(-1.6, -2.4, 'R1 = 7', fontsize=8)
        ax.annotate('', (0, 0), (R1 * np.sin(-0.25), -R1 * np.cos(0.25)), arrowprops=dict(arrowstyle='->', lw=.7))
        ax.annotate('', (7.3, yt), (7.3, yb), **kw); ax.text(6.0, yt + .05, 'C', fontsize=8)
        ax.annotate('', (5.6, yt), (5.6, -R1), **kw); ax.text(4.9, -5.2, 'H = 4.1', fontsize=8, rotation=90)
        ax.text(0, -R2 - .6, 'feed gap G = 1 (port)', ha='center', fontsize=7, color='red')
        ax.text(-xin + .2, yc + .25, 'W2 = 0.2', fontsize=7)
        ax.text(-xout + .1, yleg - .55, 'W1 = 2', fontsize=7)
        ax.plot(0, 0, 'k+')
    ax.set_xlabel('x (mm)'); ax.set_ylabel('y (mm)')

if __name__ == '__main__':
    fig, ax = plt.subplots(figsize=(9, 4.2))
    draw(ax); ax.set_title('Modelled geometry (top view) — FR4, εr = 4.3, h = 1.6 mm, 25 × 9 mm')
    plt.tight_layout(); plt.savefig('../figures/geometry.png', dpi=220)
    fig, axs = plt.subplots(2, 3, figsize=(13, 5.2))
    names = {'a': '(a) planar dipole', 'b': '(b) dipole + UIR', 'c': '(c) bent dipole + UIR',
             'd': '(d) bent dipole + folded UIR', 'e': '(e) bent dipole + SIR (final)', 'bent': 'bent dipole only (no SIR)'}
    for ax, c in zip(axs.flat, ['a', 'b', 'c', 'd', 'e', 'bent']):
        draw(ax, c, dims=False); ax.set_title(names[c], fontsize=10); ax.set_xlabel(''); ax.set_ylabel('')
    plt.tight_layout(); plt.savefig('../figures/evolution_geometries.png', dpi=200)
