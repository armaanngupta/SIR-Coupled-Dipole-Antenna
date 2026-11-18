"""Make all result figures from the openEMS runs in results/."""
import sys; sys.path = [p for p in sys.path if "dist-packages" not in p]
import os, json, glob, sys
import numpy as np, h5py, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R = 'results'; F = '../figures'
os.makedirs(F, exist_ok=True)
plt.rcParams.update({'font.size': 10, 'axes.grid': True, 'grid.alpha': .3})

def s11(tag):
    d = np.loadtxt(f'{R}/{tag}/s11.csv', delimiter=',', skiprows=1)
    return d[:, 0], d[:, 1], d[:, 2] + 1j * d[:, 3]

def bands(f, s, thr=-10):
    m = s < thr; out = []; i = 0
    while i < len(m):
        if m[i]:
            j = i
            while j + 1 < len(m) and m[j + 1]: j += 1
            out.append((f[i], f[j], f[i + np.argmin(s[i:j + 1])], s[i:j + 1].min())); i = j + 1
        else: i += 1
    return out

summary = {}
# ---------- 1. final S11 / VSWR / Zin ----------
f, s, z = s11('e')
b = bands(f, s); summary['final_bands'] = b
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
ax[0].plot(f, s, lw=2, label='openEMS (this work)')
ax[0].axhline(-10, c='gray', ls='--', lw=1)
ax[0].axvspan(2.405, 2.5, color='C1', alpha=.15, label='paper meas. 2:1 VSWR bands')
ax[0].axvspan(4.52, 5.9, color='C1', alpha=.15)
for lo, hi, fm, sm in b:
    ax[0].annotate(f'{fm:.3f} GHz\n{sm:.1f} dB', (fm, sm), xytext=(fm + .35, sm + 2), fontsize=8, arrowprops=dict(arrowstyle='->'))
ax[0].set_xlabel('Frequency (GHz)'); ax[0].set_ylabel('|S11| (dB)'); ax[0].set_title('Reflection coefficient – final antenna (case e)')
ax[0].set_ylim(-30, 1); ax[0].legend(fontsize=8, loc='lower right')
g = np.abs((z - 50) / (z + 50)); vs = (1 + g) / (1 - g)
ax[1].plot(f, vs, lw=2); ax[1].axhline(2, c='gray', ls='--'); ax[1].set_ylim(1, 6)
ax[1].set_xlabel('Frequency (GHz)'); ax[1].set_ylabel('VSWR'); ax[1].set_title('VSWR (2:1 line dashed)')
plt.tight_layout(); plt.savefig(f'{F}/s11_final.png', dpi=200); plt.close()

fig, ax = plt.subplots(figsize=(6, 3.6))
ax.plot(f, z.real, label='Re{Zin}'); ax.plot(f, z.imag, label='Im{Zin}'); ax.axhline(50, c='gray', ls='--', lw=1)
ax.set_ylim(-250, 250); ax.set_xlabel('Frequency (GHz)'); ax.set_ylabel('Ω'); ax.set_title('Input impedance – final antenna'); ax.legend()
plt.tight_layout(); plt.savefig(f'{F}/zin_final.png', dpi=200); plt.close()

# ---------- 2. evolution ----------
names = {'a': '(a) planar dipole', 'b': '(b) dipole + UIR', 'c': '(c) bent dipole + UIR',
         'd': '(d) bent dipole + folded UIR', 'e': '(e) bent dipole + SIR'}
fig, ax = plt.subplots(figsize=(8, 4.2)); summary['evolution'] = {}
for k, n in names.items():
    if not os.path.exists(f'{R}/{k}/s11.csv'): continue
    ff, ss, _ = s11(k); ax.plot(ff, ss, lw=1.8, label=n)
    from scipy.signal import argrelmin
    mins = [(ff[i], ss[i]) for i in argrelmin(ss, order=25)[0] if ss[i] < -3]
    summary['evolution'][k] = mins
ax.axhline(-10, c='gray', ls='--', lw=1); ax.set_xlabel('Frequency (GHz)'); ax.set_ylabel('|S11| (dB)')
ax.set_title('Antenna evolution (cf. paper Fig. 1)'); ax.legend(fontsize=8); ax.set_ylim(-35, 1)
plt.tight_layout(); plt.savefig(f'{F}/evolution_s11.png', dpi=200); plt.close()

# ---------- 3. with/without SIR & UIR vs SIR ----------
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
for k, n, a in [('bent', 'without SIR (bent dipole only)', 0), ('e', 'with SIR', 0), ('d', 'folded UIR', 1), ('e', 'folded SIR', 1)]:
    if os.path.exists(f'{R}/{k}/s11.csv'):
        ff, ss, _ = s11(k); ax[a].plot(ff, ss, lw=1.8, label=n)
ax[0].set_title('Effect of the SIR (cf. paper Fig. 4)'); ax[1].set_title('UIR vs SIR of equal length (cf. paper Fig. 5)')
for a in ax: a.axhline(-10, c='gray', ls='--', lw=1); a.legend(fontsize=8); a.set_xlabel('Frequency (GHz)'); a.set_ylabel('|S11| (dB)'); a.set_ylim(-35, 1)
plt.tight_layout(); plt.savefig(f'{F}/sir_effect.png', dpi=200); plt.close()

# ---------- 4. parametric ----------
fig, ax = plt.subplots(1, 3, figsize=(14, 3.7)); summary['sweeps'] = {}
for a, (p, vals, nom, lab) in zip(ax, [('C', ['0.2', '0.8'], '0.4', 'gap C (mm)'), ('er', ['4.0', '4.6'], '4.3', 'εr'), ('h', ['1.2', '2.0'], '1.6', 'h (mm)')]):
    for v in sorted(vals + [nom], key=float):
        tag = 'e' if v == nom else f'e_{p}{v}'
        if not os.path.exists(f'{R}/{tag}/s11.csv'): continue
        ff, ss, _ = s11(tag); a.plot(ff, ss, lw=1.6, label=f'{lab} = {v}')
        m = json.load(open(f'{R}/{tag}/meta.json')); summary['sweeps'][f'{p}={v}'] = (m['f_low'] / 1e9, m['f_high'] / 1e9, m['s11_low'], m['s11_high'])
    a.axhline(-10, c='gray', ls='--', lw=1); a.legend(fontsize=8); a.set_xlabel('Frequency (GHz)'); a.set_ylabel('|S11| (dB)'); a.set_ylim(-35, 1)
    a.set_title(f'Sweep of {lab}')
plt.tight_layout(); plt.savefig(f'{F}/parametric.png', dpi=200); plt.close()

# ---------- 5. far field ----------
m = json.load(open(f'{R}/e/meta.json')); summary['ff'] = m.get('ff')
E = np.load(f'{R}/e/ff_E_norm.npy'); theta, phi = np.load(f'{R}/e/ff_meta.npy', allow_pickle=True)
th = np.deg2rad(theta)
freqs = m['ff']['freqs']
pick = [1, 3]  # 2.45 and 5.2? -> indices into ff_f list [f_low,2.45,5.2,5.8,f_high]
fig, axs = plt.subplots(2, 3, subplot_kw=dict(projection='polar'), figsize=(12, 7.6))
for row, idx in enumerate([1, 2]):
    En = E[idx] / E[idx].max(); D = m['ff']['Dmax_dBi'][idx]
    P = 20 * np.log10(np.maximum(En, 1e-3)) + D
    def cut(ph):
        i = np.argmin(np.abs(phi - ph)); j = np.argmin(np.abs(phi - (ph + 180) % 360))
        ang = np.r_[th, 2 * np.pi - th[::-1]]; val = np.r_[P[:, i], P[::-1, j]]; return ang, val
    for col, (ph, nm) in enumerate([(0, 'XZ plane (φ = 0°, E-plane)'), (90, 'YZ plane (φ = 90°, H-plane)')]):
        ang, val = cut(ph); ax = axs[row, col]
        ax.plot(ang, np.maximum(val, D - 30)); ax.set_theta_zero_location('N'); ax.set_theta_direction(-1)
        ax.set_rlim(D - 30, D + 1); ax.set_title(f'{freqs[idx]/1e9:.2f} GHz – {nm}', fontsize=9)
    it = np.argmin(np.abs(theta - 90)); ax = axs[row, 2]
    ax.plot(np.deg2rad(phi), np.maximum(P[it], D - 30)); ax.set_rlim(D - 30, D + 1)
    ax.set_title(f'{freqs[idx]/1e9:.2f} GHz – XY plane (θ = 90°)', fontsize=9)
plt.suptitle('Directivity patterns (dBi) – openEMS NF2FF', y=.99); plt.tight_layout(); plt.savefig(f'{F}/patterns.png', dpi=200); plt.close()

# 3D patterns
from mpl_toolkits.mplot3d import Axes3D  # noqa
fig = plt.figure(figsize=(10, 4.5))
for k, idx in enumerate([1, 2]):
    En = E[idx] / E[idx].max(); r = En ** 2
    T, Ph = np.meshgrid(th, np.deg2rad(phi), indexing='ij')
    X = r * np.sin(T) * np.cos(Ph); Y = r * np.sin(T) * np.sin(Ph); Z = r * np.cos(T)
    ax = fig.add_subplot(1, 2, k + 1, projection='3d')
    ax.plot_surface(X, Y, Z, facecolors=plt.cm.jet(r), rstride=1, cstride=1, linewidth=0, antialiased=False, shade=False)
    ax.set_box_aspect([1, 1, 1]); ax.set_xlabel('x'); ax.set_ylabel('y'); ax.set_zlabel('z')
    lim = max(np.abs(X).max(), np.abs(Y).max(), np.abs(Z).max()); ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)
    ax.set_title(f'{freqs[idx]/1e9:.2f} GHz, D = {m["ff"]["Dmax_dBi"][idx]:.2f} dBi', fontsize=10)
plt.tight_layout(); plt.savefig(f'{F}/pattern3d.png', dpi=180); plt.close()

# gain vs frequency
gd = np.loadtxt(f'{R}/e/gain.csv', delimiter=',', skiprows=1)
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.plot(gd[:, 0], gd[:, 1], label='Directivity'); ax.plot(gd[:, 0], gd[:, 2], label='Gain (IEEE)')
ax.plot(gd[:, 0], gd[:, 3], '--', label='Realized gain (incl. mismatch)')
ax.plot([2.48, 5.35], [2.6, 3.6], 'k*', ms=11, label='paper measured peak gain')
ax.set_ylim(-10, 6); ax.set_xlabel('Frequency (GHz)'); ax.set_ylabel('dBi'); ax.legend(fontsize=8); ax.set_title('Gain vs frequency')
plt.tight_layout(); plt.savefig(f'{F}/gain.png', dpi=200); plt.close()
summary['gain_table'] = gd.tolist()

# ---------- 6. field maps ----------
def load_fd(fn):
    with h5py.File(fn, 'r') as h:
        x = np.array(h['Mesh/x']); y = np.array(h['Mesh/y'])
        fd = h['FieldData/FD']; out = []
        for i in range(len(fd)):
            out.append(np.array(fd[f'f{i}']))
    return x, y, out
sim = '/tmp/sim_e'
if os.path.exists(f'{sim}/Et.h5'):
    from plot_geometry import draw
    for name, fn, lab in [('efield', 'Et.h5', '|E| (dB, normalised)'), ('current', 'Jt.h5', '|J_s| (dB, normalised)')]:
        x, y, fl = load_fd(f'{sim}/{fn}')
        fig, axs = plt.subplots(1, 2, figsize=(12, 3.6))
        for a, fdat, fr in zip(axs, fl, [2.4, 5.3]):
            arr = np.squeeze(np.array(fdat))
            # shape (3, nz?, ny, nx) or (3, nx, ny, nz): find spatial dims
            mag = np.sqrt(np.sum(np.abs(arr) ** 2, axis=0)).squeeze()
            if mag.shape != (len(x), len(y)): mag = mag.T
            mag_db = 20 * np.log10(mag / mag.max() + 1e-12)
            pc = a.pcolormesh(x * 1e3 if x.max() < 1 else x, y * 1e3 if y.max() < 1 else y, mag_db.T, vmin=-40, vmax=0, cmap='jet', shading='auto')
            a.set_aspect('equal'); a.set_title(f'{lab} at {fr} GHz', fontsize=10); plt.colorbar(pc, ax=a, fraction=.025)
            if name == 'current':
                jx = np.real(arr[0]).squeeze(); jy = np.real(arr[1]).squeeze()
                if jx.shape != (len(x), len(y)): jx, jy = jx.T, jy.T
                xs = (x * 1e3 if x.max() < 1 else x); ys = (y * 1e3 if y.max() < 1 else y)
                st = 3
                msk = (mag_db > -28)
                ux = np.where(msk, jx / (mag + 1e-20), np.nan); uy = np.where(msk, jy / (mag + 1e-20), np.nan)
                a.quiver(xs[::st], ys[::st], ux[::st, ::st].T, uy[::st, ::st].T,
                         color='k', scale=55, width=.002, alpha=.8)
            a.set_xlim(-13, 13); a.set_ylim(-10, 0.5); a.set_xlabel('x (mm)'); a.set_ylabel('y (mm)')
        plt.tight_layout(); plt.savefig(f'{F}/{name}.png', dpi=200); plt.close()

json.dump(summary, open(f'{F}/summary.json', 'w'), indent=1, default=float)
print(json.dumps({k: summary[k] for k in summary if k != 'gain_table'}, indent=1, default=float))
