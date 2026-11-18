"""
Analytical model of the stepped impedance resonator (SIR) - paper Sec. III-C, eqs. (1)-(4), Table III.

Resonance condition (fundamental mode, 0 < theta_t < pi):
    k * cot(0.5 * alpha * theta_t) = tan((1 - alpha) * 0.5 * theta_t)        (4)
with k = Z2/Z1 = 0.45644, alpha = theta2/(theta1+theta2) = 0.7306 (values given in the paper)
and theta_t = 2(theta1 + theta2).

Electrical -> physical length:  l = theta / beta,  beta = 2*pi*f*sqrt(eps_eff)/c.
The fabricated SIR has ONE thin centre section (electrical length 2*theta1, physical l1)
and TWO wide folded arms (electrical length theta2 each, physical l2).
The paper does not give the CPS gap / eps_eff, so eps_eff of both CPS lines is
back-calculated from Table III (see README); the script then reproduces Table III
and shows the size reduction an SIR gives over a uniform resonator (k = 1).
"""
import numpy as np
from scipy.optimize import brentq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

c = 299.792458  # mm*GHz
k, alpha = 0.45644, 0.7306
eeff1, eeff2 = 2.03, 2.40   # thin (asymmetric CPS) and wide (symmetric CPS) sections

def theta_t(k, alpha):
    g = lambda t: k / np.tan(0.5 * alpha * t) - np.tan((1 - alpha) * 0.5 * t)
    return brentq(g, 1e-4, 1.5 * np.pi)

tt = theta_t(k, alpha)
th1, th2 = 0.5 * (1 - alpha) * tt, 0.5 * alpha * tt
print(f"theta_t = {np.degrees(tt):.2f} deg  (UIR would need 180 deg)")
print(f"theta1 = {np.degrees(th1):.2f} deg, theta2 = {np.degrees(th2):.2f} deg, check k = tan1*tan2 = {np.tan(th1)*np.tan(th2):.5f}")

paper_an = {1.5: (15.08, 18.79), 1.8: (12.571, 15.66), 2.2: (10.29, 12.8), 2.6: (8.7, 10.84)}
paper_sim = {1.5: (14.14, 17.62), 1.8: (11.31, 14.098), 2.2: (9.62, 12.4), 2.6: (8.08, 10.07)}
rows = []
print("\n f(GHz) | l1 ours | l1 paper(an) | l1 paper(sim) | l2 ours | l2 paper(an) | l2 paper(sim)")
for f in (1.5, 1.8, 2.2, 2.6):
    l1 = 2 * th1 * c / (2 * np.pi * f * np.sqrt(eeff1))
    l2 = th2 * c / (2 * np.pi * f * np.sqrt(eeff2))
    rows.append((f, l1, l2, *paper_an[f], *paper_sim[f]))
    print(f"  {f:4.1f}  | {l1:7.2f} | {paper_an[f][0]:12.2f} | {paper_sim[f][0]:13.2f} | {l2:7.2f} | {paper_an[f][1]:12.2f} | {paper_sim[f][1]:13.2f}")

os.makedirs('figures', exist_ok=True)
np.savetxt('figures/table3_reproduced.csv', np.array(rows), delimiter=',', fmt='%.3f',
           header='f_GHz,l1_ours,l2_ours,l1_paper_an,l2_paper_an,l1_paper_sim,l2_paper_sim', comments='')

# ---- Figure: total electrical length vs impedance ratio k (alpha fixed) ----
ks = np.linspace(0.15, 1.5, 200)
tts = [np.degrees(theta_t(kk, alpha)) for kk in ks]
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
ax[0].plot(ks, tts, lw=2)
ax[0].axhline(180, ls='--', c='gray'); ax[0].text(1.0, 183, 'UIR (k = 1): 180°', fontsize=9)
ax[0].plot(k, np.degrees(tt), 'ro'); ax[0].annotate(f'paper: k={k:.3f}\nθt={np.degrees(tt):.1f}°', (k, np.degrees(tt)),
                                                   xytext=(0.65, 110), arrowprops=dict(arrowstyle='->'))
ax[0].set_xlabel('Impedance ratio k = Z2/Z1'); ax[0].set_ylabel('Total electrical length θt (deg)')
ax[0].set_title('SIR fundamental-mode length vs k (α = 0.7306)'); ax[0].grid(alpha=.3)

fs = np.array([r[0] for r in rows])
for i, (lab, m) in enumerate([('l1 (thin section)', 'o'), ('l2 (wide arm)', 's')]):
    ax[1].plot(fs, [r[1 + i] for r in rows], m + '-', label=f'{lab} – this work (eq. 4)')
    ax[1].plot(fs, [r[3 + i] for r in rows], m + '--', mfc='none', label=f'{lab} – paper analytical')
    ax[1].plot(fs, [r[5 + i] for r in rows], m + ':', label=f'{lab} – paper simulated')
ax[1].set_xlabel('Frequency (GHz)'); ax[1].set_ylabel('Physical length (mm)')
ax[1].set_title('Table III reproduced'); ax[1].grid(alpha=.3); ax[1].legend(fontsize=7)
plt.tight_layout(); plt.savefig('figures/sir_analysis.png', dpi=200)
print('\nsaved figures/sir_analysis.png')
