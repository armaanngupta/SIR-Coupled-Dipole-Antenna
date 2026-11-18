"""CST-*style* renderings of the openEMS results, permanently watermarked as MOCK (openEMS data, not CST)."""
import sys; sys.path = [p for p in sys.path if 'dist-packages' not in p]
import json, numpy as np, h5py, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa
from plot_geometry import draw

R = 'results/e'; OUT = '../figures/mock_cst'
import os; os.makedirs(OUT, exist_ok=True)
WM = 'MOCK — openEMS data, not CST'

def watermark(fig):
    for (x, y) in [(0.5, 0.5), (0.22, 0.2), (0.78, 0.8)]:
        fig.text(x, y, WM, fontsize=26 if (x, y) == (0.5, 0.5) else 15, color='red', alpha=.28, rotation=25,
                 ha='center', va='center', weight='bold', zorder=100)
    fig.text(0.995, 0.005, 'MOCK image — simulated with openEMS (FDTD); styled to resemble a CST plot', ha='right',
             va='bottom', fontsize=7, color='red')

def main():
    # ---------- 1. S11 in "1D Results" style ----------
    d = np.loadtxt(f'{R}/s11.csv', delimiter=',', skiprows=1); f, s = d[:, 0], d[:, 1]
    fig = plt.figure(figsize=(10, 6), facecolor='#dfe6ee')
    fig.text(0.01, 0.965, '1D Results \\ S-Parameters \\ S1,1   [Magnitude in dB]', fontsize=11, color='#1b3a5c', weight='bold')
    ax = fig.add_axes([0.08, 0.1, 0.7, 0.8], facecolor='white')
    ax.plot(f, s, color='#d40000', lw=1.6, label='S1,1')
    ax.grid(color='#b0b0b0', lw=.6); ax.set_xlim(1, 8); ax.set_ylim(-25, 0)
    ax.set_xlabel('Frequency / GHz'); ax.set_ylabel('Magnitude [dB]'); ax.legend(loc='lower right', fontsize=9)
    marks = []
    for lo, hi in [(2.0, 3.0), (4.0, 6.0)]:
        m = (f > lo) & (f < hi); i = np.flatnonzero(m)[np.argmin(s[m])]; marks.append((f[i], s[i]))
    for k, (fm, sm) in enumerate(marks, 1):
        ax.plot(fm, sm, 'v', color='k', ms=7); ax.annotate(f'{k}', (fm, sm), xytext=(4, -12), textcoords='offset points', fontsize=9)
    ax.axhline(-10, color='#3060c0', ls='--', lw=.8)
    tx = 'Markers\n' + '\n'.join(f'{k}: {fm:.3f} GHz   {sm:.2f} dB' for k, (fm, sm) in enumerate(marks, 1))
    fig.text(0.8, 0.75, tx, fontsize=9, family='monospace', va='top', bbox=dict(fc='white', ec='#7a8ca0'))
    watermark(fig); fig.savefig(f'{OUT}/mock_s11.png', dpi=170, facecolor=fig.get_facecolor()); plt.close()

    # ---------- 2. 3D far-field "realized gain" style ----------
    m = json.load(open(f'{R}/meta.json')); E = np.load(f'{R}/ff_E_norm.npy')
    theta, phi = np.load(f'{R}/ff_meta.npy', allow_pickle=True)
    th, ph = np.deg2rad(theta), np.deg2rad(phi)
    for idx, tag in [(1, '2p45'), (2, '5p2')]:
        D = m['ff']['Dmax_dBi'][idx]; fr = m['ff']['freqs'][idx] / 1e9
        Pdb = 20 * np.log10(np.maximum(E[idx] / E[idx].max(), 1e-3)) + D
        rng = 30; r = np.clip(Pdb - (D - rng), 0, None) / rng
        T, P = np.meshgrid(th, ph, indexing='ij')
        X, Y, Z = r * np.sin(T) * np.cos(P), r * np.sin(T) * np.sin(P), r * np.cos(T)
        fig = plt.figure(figsize=(9, 7), facecolor='#dfe6ee')
        ax = fig.add_axes([0.0, 0.05, 0.8, 0.85], projection='3d'); ax.set_facecolor('#dfe6ee')
        norm = plt.Normalize(D - rng, D)
        ax.plot_surface(X, Y, Z, facecolors=plt.cm.jet(norm(Pdb)), rstride=1, cstride=1, lw=0, antialiased=False, shade=False)
        for v, c, l in [((1.25, 0, 0), 'r', 'x'), ((0, 1.25, 0), 'g', 'y'), ((0, 0, 1.25), 'b', 'z')]:
            ax.quiver(0, 0, 0, *v, color=c, lw=2, arrow_length_ratio=.08); ax.text(*[1.08 * q for q in v], l, color=c, fontsize=12)
        ax.set_axis_off(); ax.set_box_aspect([1, 1, 1]); ax.view_init(25, -55)
        ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.set_zlim(-1, 1)
        cax = fig.add_axes([0.83, 0.2, 0.03, 0.55]); cb = plt.colorbar(plt.cm.ScalarMappable(norm, 'jet'), cax=cax); cb.set_label('dBi')
        fig.text(0.01, 0.965, f'farfield (f={fr:.2f}) [1]   Type: Farfield   Approximation: enabled (kR >> 1)', fontsize=10, color='#1b3a5c', weight='bold')
        fig.text(0.01, 0.93, f'Monitor: Directivity   Frequency: {fr:.2f} GHz   Dir. = {D:.3f} dBi', fontsize=9, color='#1b3a5c')
        watermark(fig); fig.savefig(f'{OUT}/mock_farfield_{tag}GHz.png', dpi=160, facecolor=fig.get_facecolor()); plt.close()

    # ---------- 3. surface current style ----------
    with h5py.File('/tmp/sim_e/Jt.h5', 'r') as h:
        x = np.array(h['Mesh/x']) * 1e3; y = np.array(h['Mesh/y']) * 1e3
        J = [np.squeeze(np.array(h[f'FieldData/FD/f{i}'])) for i in range(2)]
    for arr, fr in zip(J, [2.4, 5.3]):
        mag = np.sqrt(np.sum(np.abs(arr) ** 2, axis=0)); mdb = 20 * np.log10(mag / mag.max() + 1e-12)
        fig = plt.figure(figsize=(10, 5), facecolor='#dfe6ee')
        ax = fig.add_axes([0.05, 0.12, 0.8, 0.72], facecolor='#1a2a6c')
        pc = ax.pcolormesh(x, y, mdb.T, vmin=-40, vmax=0, cmap='jet', shading='auto')
        msk = mdb > -28; ux = np.where(msk, np.real(arr[0]) / (mag + 1e-20), np.nan); uy = np.where(msk, np.real(arr[1]) / (mag + 1e-20), np.nan)
        ax.quiver(x[::3], y[::3], ux[::3, ::3].T, uy[::3, ::3].T, color='w', scale=55, width=.002)
        ax.set_aspect('equal'); ax.set_xlim(-13, 13); ax.set_ylim(-10, .5); ax.set_xticks([]); ax.set_yticks([])
        cax = fig.add_axes([0.87, 0.2, 0.025, 0.55]); cb = plt.colorbar(pc, cax=cax); cb.set_label('dB (A/m), normalised')
        fig.text(0.01, 0.94, f'Type: Surface Current (peak)   Monitor: h-field (f={fr})   Component: Abs   Frequency: {fr} GHz',
                 fontsize=10, color='#1b3a5c', weight='bold')
        watermark(fig); fig.savefig(f'{OUT}/mock_surface_current_{str(fr).replace(".", "p")}GHz.png', dpi=170, facecolor=fig.get_facecolor()); plt.close()
    print(sorted(os.listdir(OUT)))

if __name__ == '__main__':
    main()
