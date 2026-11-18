"""
openEMS (FDTD) model of the Dual Band SIR Coupled Dipole Antenna
U. Deepak et al., IEEE TAP 2015, DOI 10.1109/TAP.2015.2393876

Usage:
    python3 sir_dipole.py <case> [--fields] [--sweep NAME=VALUE]

Cases (paper Fig. 1 / Fig. 4 / Fig. 5):
    a      planar (straight) dipole
    b      straight dipole + straight UIR (top loaded)
    c      bent dipole + straight UIR
    d      bent dipole + folded UIR (uniform 2 mm strip, same footprint as SIR)
    e      bent dipole + folded SIR   (final proposed antenna, Table I)
    bent   bent dipole alone (Fig. 4 "without SIR")

Coordinate system (mm): x along the antenna length, y up, z normal.
Origin = centre of the dipole arcs. Metal is a zero-thickness PEC sheet on
top of a 1.6 mm FR4 substrate (er = 4.3, tan d = 0.02 assumed).
"""
import os, sys, json, argparse
import numpy as np
from CSXCAD import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import C0

# ---------------- Table I dimensions (mm) ----------------
P = dict(L1=9.62, L2=6.7, L3=7.7, W1=2.0, W2=0.2, R1=7.0, R2=9.0,
         C=0.4, G=1.0, H=4.1, h=1.6, er=4.3, tand=0.02, Wsub=25.0, Lsub=9.0)

ap = argparse.ArgumentParser()
ap.add_argument('case')
ap.add_argument('--fields', action='store_true')
ap.add_argument('--sweep', default=None, help='e.g. C=0.6 or er=4.6 or h=1.2')
ap.add_argument('--out', default=None)
args = ap.parse_args()
tag = args.case
if args.sweep:
    k, v = args.sweep.split('=')
    P[k] = float(v)
    tag += f'_{k}{v}'
case = args.case
out = os.path.abspath(args.out or f'results/{tag}')
os.makedirs(out, exist_ok=True)
simpath = f'/tmp/sim_{tag}'

L1, L2, L3, W1, W2 = P['L1'], P['L2'], P['L3'], P['W1'], P['W2']
R1, R2, C, G, H, h = P['R1'], P['R2'], P['C'], P['G'], P['H'], P['h']

# derived geometry
y_tip = -(R1 - H)                 # arc tips are cut horizontally H above the inner arc bottom
y_bar_bot = y_tip + C             # SIR horizontal bars sit a gap C above the arc tips
y_bar_top = y_bar_bot + W1
x_in = L1 / 2                     # inner end of wide horizontal bar (junction with thin line)
x_out = L1 / 2 + L2               # outer edge of SIR
y_leg_bot = y_bar_top - L3
y_c = 0.5 * (y_bar_top + y_bar_bot)
ysub_top = y_bar_top + 0.25
ysub_bot = ysub_top - P['Lsub']

unit = 1e-3
f0, fc = 4.5e9, 3.5e9
fmin, fmax = 1e9, 8e9

FDTD = openEMS(NrTS=400000, EndCriteria=1e-5)
FDTD.SetGaussExcite(f0, fc)
FDTD.SetBoundaryCond(['PML_8'] * 6)
CSX = ContinuousStructure()
FDTD.SetCSX(CSX)
mesh = CSX.GetGrid()
mesh.SetDeltaUnit(unit)

sub = CSX.AddMaterial('FR4', epsilon=P['er'],
                      kappa=P['tand'] * 2 * np.pi * 2.4e9 * 8.854e-12 * P['er'])
sub.AddBox([-P['Wsub'] / 2, ysub_bot, 0], [P['Wsub'] / 2, ysub_top, h], priority=0)
pec = CSX.AddMetal('PEC')
zt = h

def arc_arm(sign):
    """Annular-sector arm between R1 and R2, from the feed gap up to y_tip (horizontal cut)."""
    th_in0 = np.arcsin((G / 2) / R1)
    pts = []
    # inner edge: from bottom (near gap) to tip
    th_tip_in = np.arccos(-y_tip / R1)   # angle from -y axis
    th_tip_out = np.arccos(-y_tip / R2)
    th0_in = np.arcsin((G / 2) / R1)
    th0_out = np.arcsin((G / 2) / R2)
    for t in np.linspace(th0_in, th_tip_in, 60):
        pts.append((sign * R1 * np.sin(t), -R1 * np.cos(t)))
    for t in np.linspace(th_tip_out, th0_out, 60):
        pts.append((sign * R2 * np.sin(t), -R2 * np.cos(t)))
    return np.array(pts)

def add_poly(pts):
    pec.AddPolygon([pts[:, 0], pts[:, 1]], 'z', zt, priority=10)

bent = case in ('c', 'd', 'e', 'bent')
arm_len = None
if bent:
    for s in (+1, -1):
        add_poly(arc_arm(s))
    th_mid = np.arccos(-y_tip / ((R1 + R2) / 2)) - np.arcsin(G / 2 / ((R1 + R2) / 2))
    arm_len = (R1 + R2) / 2 * th_mid
else:
    # straight dipole with the same arm length as the bent arm (mean radius arc length)
    th_mid = np.arccos(-y_tip / ((R1 + R2) / 2)) - np.arcsin(G / 2 / ((R1 + R2) / 2))
    arm_len = (R1 + R2) / 2 * th_mid
    for s in (+1, -1):
        pec.AddBox([s * G / 2, -R2, zt], [s * (G / 2 + arm_len), -R1, zt], priority=10)

# parasitic element
if case in ('b', 'c'):          # straight UIR above the dipole, same span as the SIR
    pec.AddBox([-x_out, y_bar_bot, zt], [x_out, y_bar_top, zt], priority=10)
if case in ('d', 'e'):
    for s in (+1, -1):
        pec.AddBox([s * x_in, y_bar_bot, zt], [s * x_out, y_bar_top, zt], priority=10)       # horizontal wide bar (L2)
        pec.AddBox([s * (x_out - W1), y_leg_bot, zt], [s * x_out, y_bar_top, zt], priority=10)  # vertical leg (L3)
    if case == 'e':   # thin high-impedance section, width W2, length L1
        pec.AddBox([-x_in, y_c - W2 / 2, zt], [x_in, y_c + W2 / 2, zt], priority=10)
    else:             # UIR: the centre section is as wide as the rest
        pec.AddBox([-x_in, y_bar_bot, zt], [x_in, y_bar_top, zt], priority=10)

# lumped port across the feed gap
port = FDTD.AddLumpedPort(1, 50, [-G / 2, -R2, zt], [G / 2, -R1, zt], 'x', excite=1, priority=20)

# ---------------- mesh ----------------
res_max = C0 / fmax / unit / 20
xs = [-P['Wsub'] / 2, P['Wsub'] / 2, -G / 2, G / 2, 0]
for s in (+1, -1):
    xs += [s * x_in, s * x_out, s * (x_out - W1), s * R1, s * R2,
           s * np.sqrt(R1**2 - y_tip**2), s * np.sqrt(R2**2 - y_tip**2)]
    if not bent:
        xs += [s * (G / 2 + arm_len)]
ys = [ysub_bot, ysub_top, -R2, -R1, y_tip, y_bar_bot, y_bar_top, y_leg_bot,
      y_c - W2 / 2, y_c + W2 / 2, y_c]
def merge(lines, tol=0.08):
    lines = np.sort(np.unique(np.round(lines, 4)))
    outl = [lines[0]]
    for v in lines[1:]:
        if v - outl[-1] > tol:
            outl.append(v)
    return np.array(outl)

xs = list(xs) + list(np.arange(-x_out, x_out + 1e-9, 0.3))
ys = list(ys) + list(np.arange(-R2, y_bar_top + 1e-9, 0.25))
mesh.AddLine('x', merge(xs))
mesh.AddLine('y', merge(ys))
mesh.AddLine('z', np.linspace(0, h, 5))
mesh.SmoothMeshLines('all', 0.3, 1.3)
air = 30
mesh.AddLine('x', [-P['Wsub'] / 2 - air, P['Wsub'] / 2 + air])
mesh.AddLine('y', [ysub_bot - air, ysub_top + air])
mesh.AddLine('z', [-air, h + air])
mesh.SmoothMeshLines('all', res_max, 1.3)
for d in 'xyz':
    l = mesh.GetLines(d)
    print('mesh', d, len(l), 'min cell', np.diff(l).min())

nf2ff = FDTD.CreateNF2FFBox()

freqs_dump = [2.4e9, 5.3e9]
if args.fields:
    et = CSX.AddDump('Et', dump_type=10, file_type=1, frequency=freqs_dump)
    et.AddBox([-P['Wsub'] / 2 - 2, ysub_bot - 2, zt], [P['Wsub'] / 2 + 2, ysub_top + 2, zt])
    jt = CSX.AddDump('Jt', dump_type=13, file_type=1, frequency=freqs_dump)
    jt.AddBox([-P['Wsub'] / 2, ysub_bot, zt], [P['Wsub'] / 2, ysub_top, zt])

if '--geom' in sys.argv:
    CSX.Write2XML(os.path.join(out, 'geometry.xml'))
FDTD.Run(simpath, cleanup=True, verbose=1)

f = np.linspace(fmin, fmax, 1401)
port.CalcPort(simpath, f)
s11 = port.uf_ref / port.uf_inc
zin = port.uf_tot / port.if_tot
np.savetxt(os.path.join(out, 's11.csv'),
           np.c_[f / 1e9, 20 * np.log10(np.abs(s11)), zin.real, zin.imag],
           delimiter=',', header='f_GHz,S11_dB,Re_Zin,Im_Zin', comments='')

# far field at the two band centres + gain vs frequency
s11db = 20 * np.log10(np.abs(s11))
low = (f > 2.0e9) & (f < 3.0e9)
high = (f > 4.0e9) & (f < 7.0e9)
f_low = f[low][np.argmin(s11db[low])]
f_high = f[high][np.argmin(s11db[high])]
meta = dict(case=case, params=P, arm_len=arm_len, f_low=f_low, f_high=f_high,
            s11_low=float(s11db[low].min()), s11_high=float(s11db[high].min()))
if case in ('e',) or args.fields:
    theta = np.arange(0, 181, 2.0)
    phi = np.arange(0, 361, 3.0)
    ff_f = [f_low, 2.45e9, 5.2e9, 5.8e9, f_high]
    res = nf2ff.CalcNF2FF(simpath, ff_f, theta, phi, center=[0, -4e-3, h / 2 * 1e-3])
    np.save(os.path.join(out, 'ff_E_norm.npy'), np.array([e for e in res.E_norm]))
    np.save(os.path.join(out, 'ff_meta.npy'), np.array([theta, phi], dtype=object), allow_pickle=True)
    # input power to compute gain = Dmax * (1-|S11|^2)? openEMS Dmax uses accepted power -> realized gain = D*Prad/Pinc
    Pin = []
    for fi in ff_f:
        i = np.argmin(np.abs(f - fi))
        Pin.append(float(np.real(0.5 * port.uf_tot[i] * np.conj(port.if_tot[i]))))
    meta['ff'] = dict(freqs=ff_f, Dmax_dBi=[float(10 * np.log10(d)) for d in res.Dmax],
                      Prad=[float(p) for p in res.Prad], Pacc=Pin,
                      eff_rad=[float(p / q) for p, q in zip(res.Prad, Pin)])
    # gain vs freq on a coarse set
    gf = np.linspace(2.2e9, 6.5e9, 44)
    r2 = nf2ff.CalcNF2FF(simpath, gf, np.arange(0, 181, 5.0), np.arange(0, 361, 10.0), center=[0, -4e-3, h / 2 * 1e-3], outfile='nf2ff_gain.h5')
    G = []
    for k, fi in enumerate(gf):
        i = np.argmin(np.abs(f - fi))
        pinc = float(0.5 * np.abs(port.uf_inc[i]) ** 2 / 50)
        pacc = float(np.real(0.5 * port.uf_tot[i] * np.conj(port.if_tot[i])))
        G.append([fi / 1e9, 10 * np.log10(r2.Dmax[k]), 10 * np.log10(r2.Dmax[k] * r2.Prad[k] / pacc),
                  10 * np.log10(r2.Dmax[k] * r2.Prad[k] / pinc), r2.Prad[k] / pacc])
    np.savetxt(os.path.join(out, 'gain.csv'), np.array(G), delimiter=',',
               header='f_GHz,D_dBi,Gain_dBi,RealizedGain_dBi,rad_eff', comments='')
json.dump(meta, open(os.path.join(out, 'meta.json'), 'w'), indent=1, default=float)
print('DONE', json.dumps({k: meta[k] for k in ('f_low', 'f_high', 's11_low', 's11_high')}, default=float))
