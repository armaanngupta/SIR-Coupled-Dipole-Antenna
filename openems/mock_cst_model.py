"""CST-*style* 3D view of the modelled antenna with a parameter list, watermarked as MOCK."""
import sys; sys.path = [p for p in sys.path if 'dist-packages' not in p]
import numpy as np, matplotlib, os
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mock_cst_style import watermark

L1, L2, L3, W1, W2, R1, R2, C, G, H, h, t = 9.62, 6.7, 7.7, 2, 0.2, 7, 9, 0.4, 1, 4.1, 1.6, 0.035 * 8  # copper drawn thicker for visibility
yt = -(R1 - H); yb = yt + C; ytop = yb + W1; xin = L1 / 2; xout = xin + L2; yleg = ytop - L3; yc = (ytop + yb) / 2
ys1 = ytop + 0.25; ys0 = ys1 - 9

def prism(poly2d, z0, z1):
    p = np.asarray(poly2d); n = len(p); faces = []
    faces.append([(x, y, z1) for x, y in p]); faces.append([(x, y, z0) for x, y in p[::-1]])
    for i in range(n):
        a, b = p[i], p[(i + 1) % n]
        faces.append([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)])
    return faces

def rect(x0, y0, x1, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

def arm(s):
    a_in = np.linspace(np.arcsin(G / 2 / R1), np.arccos(-yt / R1), 40)
    a_out = np.linspace(np.arccos(-yt / R2), np.arcsin(G / 2 / R2), 40)
    return np.r_[np.c_[s * R1 * np.sin(a_in), -R1 * np.cos(a_in)], np.c_[s * R2 * np.sin(a_out), -R2 * np.cos(a_out)]]

copper = []
for s in (1, -1):
    copper.append(arm(s))
    copper.append(rect(*sorted([s * xin, s * xout])[:1], yb, *sorted([s * xin, s * xout])[1:], ytop))
    copper.append(rect(min(s * (xout - W1), s * xout), yleg, max(s * (xout - W1), s * xout), ytop))
copper.append(rect(-xin, yc - W2 / 2, xin, yc + W2 / 2))

fig = plt.figure(figsize=(13, 7), facecolor='#dfe6ee')
fig.text(0.01, 0.965, 'SIR_coupled_dipole  —  3D view   (Perspective, WCS)', fontsize=11, color='#1b3a5c', weight='bold')
ax = fig.add_axes([0.0, 0.02, 0.68, 0.9], projection='3d', computed_zorder=False); ax.set_facecolor('#dfe6ee')
ax.add_collection3d(Poly3DCollection(prism(rect(-12.5, ys0, 12.5, ys1), 0, h), facecolor='#7fb27a', edgecolor='#2f5a2c', lw=.5, zorder=1))
for p in copper:
    ax.add_collection3d(Poly3DCollection(prism(p, h, h + t), facecolor='#e09a3e', edgecolor='#7a4a12', lw=.3, zorder=2))
# discrete port
ax.plot([-G / 2, G / 2], [-8, -8], [h + t, h + t], color='red', lw=3, zorder=5)
ax.scatter([-G / 2, G / 2], [-8, -8], [h + t, h + t], color='red', s=25, zorder=5)
ax.text(0, -10.6, h + 1.5, '1', color='red', fontsize=12, weight='bold')
for v, c, l in [((4, 0, 0), 'r', 'x'), ((0, 4, 0), 'g', 'y'), ((0, 0, 3), 'b', 'z')]:
    ax.quiver(-12, -10.5, 1.6, *v, color=c, lw=2, arrow_length_ratio=.15); ax.text(-12 + v[0] * 1.2, -10.5 + v[1] * 1.2, 1.6 + v[2] * 1.2, l, color=c)
ax.set_xlim(-13, 13); ax.set_ylim(-11, 1); ax.set_zlim(-3, 5); ax.set_box_aspect([26, 12, 8], zoom=0.95)
ax.view_init(38, -62); ax.set_axis_off()

# parameter list panel
rows = [('L1', '9.62', 'thin SIR section'), ('L2', '6.7', 'SIR horizontal bar'), ('L3', '7.7', 'SIR vertical leg'),
        ('W1', '2', 'wide strip width'), ('W2', '0.2', 'thin strip width'), ('R1', '7', 'dipole inner radius'),
        ('R2', '9', 'dipole outer radius'), ('C', '0.4', 'dipole-SIR gap'), ('G', '1', 'feed gap'), ('H', '4.1', 'arc tip height'),
        ('h', '1.6', 'substrate thickness'), ('er', '4.3', 'FR4 permittivity'), ('Wsub', '25', 'substrate width'), ('Lsub', '9', 'substrate length')]
pa = fig.add_axes([0.69, 0.1, 0.3, 0.8]); pa.set_axis_off()
pa.add_patch(plt.Rectangle((0, 0), 1, 1, fc='white', ec='#7a8ca0', transform=pa.transAxes))
pa.add_patch(plt.Rectangle((0, .93), 1, .07, fc='#c7d3e0', ec='#7a8ca0', transform=pa.transAxes))
pa.text(.03, .965, 'Parameter List', va='center', fontsize=10, weight='bold', color='#1b3a5c')
for j, hd in enumerate(['Name', 'Value', 'Description']):
    pa.text([.03, .22, .42][j], .9, hd, fontsize=9, weight='bold', va='center')
for i, (n, v, dsc) in enumerate(rows):
    yy = .86 - i * .058
    if i % 2 == 0: pa.add_patch(plt.Rectangle((0, yy - .029), 1, .058, fc='#f1f5f8', ec='none'))
    pa.text(.03, yy, n, fontsize=9, va='center'); pa.text(.22, yy, v, fontsize=9, va='center'); pa.text(.42, yy, dsc, fontsize=8.5, va='center')
watermark(fig)
os.makedirs('../figures/mock_cst', exist_ok=True)
fig.savefig('../figures/mock_cst/mock_model_3d.png', dpi=160, facecolor=fig.get_facecolor())
print('ok')
