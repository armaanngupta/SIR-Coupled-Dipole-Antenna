"""Build the course-project report (HTML -> PDF with headless Chrome via Playwright)."""
import os, json, base64, subprocess, html
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG = os.path.join(ROOT, 'figures')
S = json.load(open(os.path.join(FIG, 'summary.json')))

GROUP = 'Group 12'
GUIDE = 'Assistant Prof. Trivesh Kumar'
REPO = 'https://github.com/&lt;your-username&gt;/SIR-Dual-Band-Dipole'
MEMBERS = [('Armaan Gupta', '23BSM014'), ('Ayush Tiwari', '23BEC025'), ('Rajesh Singh', '23BEC091')]
TITLE = 'A Dual Band SIR Coupled Dipole Antenna for 2.4/5.2/5.8 GHz Applications'

fig_no = [0]
def img(path, caption, width='100%'):
    fig_no[0] += 1
    with open(path, 'rb') as fh:
        b64 = base64.b64encode(fh.read()).decode()
    return (f'<figure><img src="data:image/png;base64,{b64}" style="width:{width}">'
            f'<figcaption><b>Figure {fig_no[0]}:</b> {caption}</figcaption></figure>')

def fig(name, caption, width='100%'):
    return img(os.path.join(FIG, name), caption, width)

# ------------------------------------------------------------------ numbers
fb = S['final_bands']                       # [(lo, hi, fmin, smin), ...]
low = [b for b in fb if b[2] < 3.5]; high = [b for b in fb if b[2] > 3.5]
lo_b = low[0] if low else None; hi_b = high[0] if high else None
ff = S['ff']; fq = [x / 1e9 for x in ff['freqs']]
G = S['gain_table']
def gain_at(f):
    r = min(G, key=lambda r: abs(r[0] - f)); return r
g245, g52, g58 = gain_at(2.45), gain_at(5.2), gain_at(5.8)
ev = S['evolution']; sw = S['sweeps']
_bm = json.load(open(os.path.join(ROOT, 'openems', 'results', 'bent', 'meta.json')))
BENT = f"{_bm['f_high']/1e9:.2f} GHz ({_bm['s11_high']:.1f} dB)"
def evf(k, which):
    mins = sorted(ev.get(k, []), key=lambda m: m[1])
    if which == 'low':
        c = [m for m in ev.get(k, []) if m[0] < 3.6]
    else:
        c = [m for m in ev.get(k, []) if m[0] >= 3.6]
    if not c: return '—'
    m = min(c, key=lambda m: m[1]); return f'{m[0]:.2f} GHz ({m[1]:.1f} dB)'
peak_hi = max([r for r in G if hi_b[0] - 0.05 <= r[0] <= hi_b[1] + 0.05], key=lambda r: r[2])
peak_lo = min(G, key=lambda r: abs(r[0] - lo_b[2]))
bw_low = (lo_b[1] - lo_b[0]) * 1e3 if lo_b else 0
bw_high = (hi_b[1] - hi_b[0]) if hi_b else 0

# ------------------------------------------------------------------ html
css = open(os.path.join(HERE, 'style.css')).read()
LOGO = base64.b64encode(open(os.path.join(HERE, 'iiitdm_logo.png'), 'rb').read()).decode()
H = []
add = H.append
add(f'''<!DOCTYPE html><html><head><meta charset="utf-8"><title>{TITLE} | {GROUP}</title><style>{css}</style></head><body>''')

# ---------------- cover ----------------
rows = ''.join(f'<tr><td>{GROUP}</td><td>{n}</td><td>{r}</td></tr>' for n, r in MEMBERS)
add(f'''
<section class="cover">
 <img class="logo" src="data:image/png;base64,{LOGO}">
 <div class="inst">PDPM INDIAN INSTITUTE OF INFORMATION TECHNOLOGY,<br>DESIGN AND MANUFACTURING, JABALPUR</div>
 <div class="dept">Department of Electronics and Communication Engineering</div>
 <div class="course">Course Project Report &nbsp;•&nbsp; Advanced Antenna Theory and Design (OE4E25) &nbsp;•&nbsp; 2026</div>
 <div class="titlebox"><h1>A DUAL BAND SIR COUPLED DIPOLE ANTENNA<br>FOR 2.4 / 5.2 / 5.8 GHz APPLICATIONS</h1>
 <div class="sub">{GROUP.upper()} &nbsp;•&nbsp; Full-Wave Modelling, Simulation &amp; Analytical Verification Report</div></div>
 <div class="guide"><i>Under the Guidance of</i><br><b>{GUIDE}</b><br><b>Department of Electronics and Communication Engineering, PDPM IIITDM Jabalpur</b></div>
 <div class="subm">Submitted by — {GROUP}</div>
 <table class="members"><tr><th>Group</th><th>Student Name</th><th>Roll Number</th></tr>{rows}</table>
 <p class="repo"><b>PROJECT LINK :</b> <a href="#">{REPO}</a></p>
 <div class="abstract"><h3>ABSTRACT</h3>
 <p>This report reproduces and analyses the physically small, coplanar dual-band antenna of Deepak <i>et al.</i>
 (IEEE Trans. Antennas Propag., 2015), in which a half-ring (bent) planar dipole is electrically coupled to a folded
 stepped impedance resonator (SIR) on a 25 mm × 9 mm FR4 substrate (ε<sub>r</sub> = 4.3, h = 1.6 mm). The dipole
 provides the wide 5–6 GHz band while the parasitic SIR introduces an independent, non-harmonic resonance in the
 2.4 GHz ISM band. The antenna was parameterised from Table I of the paper and simulated with the open-source full-wave FDTD solver
 openEMS. The study covers the five-step antenna evolution, the effect of the SIR, UIR vs SIR loading,
 field and surface-current distributions, radiation patterns, gain and a parametric study of the coupling gap, permittivity and
 substrate thickness. The simulated antenna resonates at {lo_b[2]:.3f} GHz and {hi_b[2]:.2f} GHz, with a −10 dB upper band of
 {hi_b[0]:.2f}–{hi_b[1]:.2f} GHz, against 2.405–2.5 GHz and 4.52–5.9 GHz reported in the paper; the evolution trends of the
 paper are reproduced, with the folded-UIR stage within 3 % of the published resonances. The analytical SIR resonance condition
 (eq. 4) was solved numerically and reproduces Table III of the paper, showing that the impedance ratio k = 0.456 shortens the
 resonator to θ<sub>t</sub> = 143.6° compared with 180° for a uniform resonator.</p>
 <p class="kw"><b>Keywords:</b> Stepped impedance resonator, bent dipole, dual-band antenna, ISM band, WLAN, openEMS, FDTD, coplanar stripline, physically small antenna.</p></div>
</section>''')

# ---------------- 1 intro ----------------
add(f'''
<h2>1. Introduction</h2>
<p>The 2.4 GHz and 5.2/5.8 GHz bands carry IEEE 802.11b/g/n/a/ac WLAN, Bluetooth and HiperLAN traffic, so compact terminals need a
single antenna that covers both. Common solutions — PIFAs, monopoles with large ground planes, slot antennas — are either bulky
or depend on a large ground plane. Deepak <i>et al.</i> [1] instead start from a balanced planar dipole, which needs no ground plane,
and add a lower band by coupling a parasitic <b>stepped impedance resonator</b> to it.</p>
<p>An SIR is a resonator built from two transmission-line sections of different characteristic impedance (Z<sub>1</sub>, Z<sub>2</sub>).
Its resonance depends on the impedance ratio k = Z<sub>2</sub>/Z<sub>1</sub> as well as on electrical length, so it can be made
shorter than a uniform half-wave resonator (UIR) and its spurious harmonics can be moved away from the fundamental [2], [3].
In [1] the SIR is realised in coplanar stripline (CPS) form — one 0.2 mm high-impedance strip between two 2 mm folded arms — and is placed
a fraction of a millimetre from the open ends of a half-ring dipole. Because the dipole ends are E-field maxima, the SIR is excited
capacitively, producing a 2.4 GHz resonance that is independent of the dipole's 5 GHz mode.</p>
<p>In this project we rebuilt the antenna from the published dimensions, simulated it with openEMS, an open-source
finite-difference time-domain (FDTD) full-wave solver, scripted in Python so that every dimension is a parameter. We also re-derived the analytical SIR model of the paper.
All model files, scripts and data are in the project repository.</p>

<h2>2. Project Objectives</h2>
<ul>
<li><b>3D modelling and parameterisation:</b> build the coplanar bent-dipole + folded-SIR antenna in openEMS from Table I, with every dimension as a script parameter.</li>
<li><b>Impedance matching:</b> simulate S<sub>11</sub>, VSWR and input impedance from 1–8 GHz and compare the two bands with the paper.</li>
<li><b>Design evolution:</b> reproduce the five evolution stages (planar dipole → … → bent dipole + SIR, paper Fig. 1) and the UIR-vs-SIR comparison (Figs. 4, 5).</li>
<li><b>Physical mechanism:</b> visualise the E-field and surface currents at 2.4 and 5.3 GHz to confirm the capacitive coupling and the x-directed polarisation (Figs. 10, 11).</li>
<li><b>Radiation:</b> compute 3D and 2D far-field patterns, directivity, gain and radiation efficiency.</li>
<li><b>Parametric study:</b> vary the coupling gap C, the permittivity ε<sub>r</sub> and the thickness h (paper Sec. III-D).</li>
<li><b>Analytical verification:</b> solve the SIR resonance condition (eq. 4) and reproduce Table III.</li>
<li><b>Comparison with the paper:</b> compare every result with the published HFSS simulations and measurements, and explain the remaining differences.</li>
</ul>
''')

# ---------------- 3 theory ----------------
add(f'''
<h2>3. Theory</h2>
<h3>3.1 Bent planar dipole</h3>
<p>A centre-fed planar dipole resonates when its total length is about λ<sub>g</sub>/2, where
λ<sub>g</sub> = λ<sub>0</sub>/√ε<sub>eff</sub>. For a strip printed on one face of FR4 with air on the other, ε<sub>eff</sub> lies
between 1 and (ε<sub>r</sub>+1)/2 ≈ 2.65. Bending the two arms into a half ring (inner radius R<sub>1</sub> = 7 mm, outer
R<sub>2</sub> = 9 mm) keeps the arc length — and so roughly the resonant frequency — while shrinking the footprint. It also brings
the two open ends, where the E-field is maximum, up next to the parasitic element. The currents along y on the two arms flow in
opposite directions and cancel in the far field, so the net radiating current — and the polarisation — is along x.</p>
<h3>3.2 Stepped impedance resonator</h3>
<p>For the symmetric SIR of Fig. 3 (paper Fig. 13), with impedance ratio and length ratio</p>
<p class="eq">k = Z<sub>2</sub> / Z<sub>1</sub> &nbsp;&nbsp;(1) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; α = θ<sub>2</sub> / (θ<sub>1</sub> + θ<sub>2</sub>) &nbsp;&nbsp;(2)</p>
<p>the fundamental resonance occurs when</p>
<p class="eq">k = tan θ<sub>1</sub> · tan θ<sub>2</sub> &nbsp;&nbsp;(3) &nbsp;&nbsp;&nbsp;⇔&nbsp;&nbsp;&nbsp;
k · cot(0.5 α θ<sub>t</sub>) = tan((1 − α) 0.5 θ<sub>t</sub>), &nbsp; θ<sub>t</sub> = 2(θ<sub>1</sub> + θ<sub>2</sub>) &nbsp;&nbsp;(4)</p>
<p>For k = 1 (a UIR) this reduces to θ<sub>t</sub> = π, the familiar half-wave resonator. For k &lt; 1, θ<sub>t</sub> &lt; π: the SIR
resonates while electrically shorter, which is what moves the lower band from 2.9 GHz (folded UIR) down to 2.4 GHz with no change in
physical length. The paper models the two sections as a symmetric CPS (two 2 mm strips) and an asymmetric CPS (0.2 mm and 2 mm strips),
giving k = 0.45644 and α = 0.7306.</p>
<h3>3.3 Coupling mechanism</h3>
<p>A parasitic element longer than the driven element and placed 0.1–0.25 λ<sub>g</sub> away acts as a reflector (Yagi-Uda
behaviour). Placed very close — here C = 0.4 mm ≈ 0.006 λ<sub>g</sub> — it instead couples reactively to the driven element and adds a
resonance of its own. The coupling capacitance between the dipole tips and the SIR bars is set mainly by the gap C, so C is the main
tuning parameter for the lower band.</p>
''')

# ---------------- 4 geometry ----------------
add(f'''
<h2>4. Antenna Configuration and Geometry</h2>
<h3>4.1 Design evolution</h3>
<p>The paper derives the antenna in five steps (Fig. 1 of [1]): (a) planar dipole resonating at 5 GHz; (b) top-loading with a UIR, which detunes
the dipole (4.9 GHz, poor match) because the near-field coupling adds inductance; (c) bending the dipole, which reduces that coupling and restores the match
(4.2 GHz); (d) folding the UIR by 90°, which gives a well-matched second resonance at 2.9 GHz together with the 4.6 GHz dipole mode; and
(e) replacing the UIR with an SIR of the same total length (34.42 mm), which moves the lower resonance to 2.4 GHz. Figure 1 shows the
six configurations we modelled.</p>
{fig('evolution_geometries.png', 'Modelled evolution geometries (copper: brown, FR4: green, port: red). The "bent dipole only" case is the "without SIR" curve of paper Fig. 4.')}
<h3>4.2 Final geometry and dimensions</h3>
{fig('geometry.png', 'Top view of the final antenna as modelled, with the Table I dimensions. The origin is the centre of the dipole arcs.', '92%')}
{fig('openems_3d/model_3d.png', '3D view of the openEMS model: FR4 substrate (green), copper bent dipole and folded SIR (orange; copper thickness exaggerated for visibility), and the 50 Ω lumped port 1 across the feed gap (red), with the parameter list used in the simulation script.')}
<table class="t"><caption>Table 1: Physical dimensions of the antenna (paper Table I) and derived quantities (mm)</caption>
<tr><th>Parameter</th><th>Value</th><th>Description</th><th>Parameter</th><th>Value</th><th>Description</th></tr>
<tr><td>L1</td><td>9.62</td><td>thin SIR section length (l<sub>1</sub>)</td><td>R1</td><td>7</td><td>dipole inner radius</td></tr>
<tr><td>L2</td><td>6.7</td><td>wide SIR horizontal bar</td><td>R2</td><td>9</td><td>dipole outer radius</td></tr>
<tr><td>L3</td><td>7.7</td><td>wide SIR vertical leg</td><td>C</td><td>0.4</td><td>dipole-to-SIR gap</td></tr>
<tr><td>W1</td><td>2</td><td>wide strip / dipole width</td><td>G</td><td>1</td><td>feed gap</td></tr>
<tr><td>W2</td><td>0.2</td><td>thin SIR strip width</td><td>H</td><td>4.1</td><td>arc tip height</td></tr>
<tr><td>l<sub>2</sub> = L2+L3−W1</td><td>12.4</td><td>each wide arm (centre-line)</td><td>Substrate</td><td>25 × 9 × 1.6</td><td>FR4, ε<sub>r</sub> = 4.3</td></tr>
<tr><td>SIR total</td><td>34.42</td><td>L1 + 2 l<sub>2</sub> (matches paper)</td><td>Dipole arm</td><td>≈ 9.1</td><td>mean-radius arc length</td></tr>
</table>
<p><b>Modelling assumptions.</b> Fig. 2 of the paper is not to scale and leaves a few details open, so we fixed them as follows for the simulation:
(i) the arc tips are cut horizontally at y = −(R<sub>1</sub> − H) = −2.9 mm, and the bottom of the SIR bars sits C above that cut;
(ii) the thin W2 strip is centred on the wide bars; (iii) FR4 tan δ = 0.02 (not given in the paper); (iv) the excitation is a 50 Ω
lumped port across the feed gap G, i.e. the coplanar (balanced) version of the antenna, not the double-sided microstrip-fed prototype
of paper Fig. 7, whose feed dimensions are not fully specified. As a consistency check, the derived total SIR length (34.42 mm) and wide-arm
length (l<sub>2</sub> = 12.4 mm) agree exactly with the values quoted in the paper text and in Table III.</p>
''')

# ---------------- 5 simulation setup ----------------
add(f'''
<h2>5. Simulation Setup</h2>
<table class="t"><caption>Table 2: Solver configuration</caption>
<tr><th>Item</th><th>openEMS setting</th></tr>
<tr><td>Method</td><td>FDTD (equivalent-circuit FDTD), rectilinear mesh, Python interface (CSXCAD)</td></tr>
<tr><td>Frequency range</td><td>1 – 8 GHz (Gaussian pulse, f<sub>0</sub> = 4.5 GHz, f<sub>c</sub> = 3.5 GHz)</td></tr>
<tr><td>Boundaries</td><td>8-cell PML on all six faces, 30 mm air margin</td></tr>
<tr><td>Excitation</td><td>Lumped port, 50 Ω, across the 1 mm feed gap</td></tr>
<tr><td>Mesh</td><td>0.09–0.3 mm in the antenna (≥ 2 cells across the 0.2 mm strip), graded to λ/20 at 8 GHz outside; ≈ 0.7 M cells</td></tr>
<tr><td>Conductors</td><td>Zero-thickness PEC sheet</td></tr>
<tr><td>Substrate</td><td>FR4, ε<sub>r</sub> = 4.3, tan δ = 0.02</td></tr>
<tr><td>Convergence</td><td>Energy decay −50 dB</td></tr>
<tr><td>Outputs</td><td>S<sub>11</sub>, Z<sub>in</sub>; E-field and surface current at 2.4 / 5.3 GHz; NF2FF far field at 2.45 / 5.2 / 5.8 GHz and 2.2–6.5 GHz for gain</td></tr>
<tr><td>Run time</td><td>≈ 3–5 min per case on 2 CPU cores (12 cases in total)</td></tr>
</table>
''')

# ---------------- 6 results ----------------
add(f'''
<h2>6. Simulation Results and Discussion</h2>
<h3>6.1 Reflection coefficient, VSWR and input impedance</h3>
{fig('s11_final.png', 'openEMS: S<sub>11</sub> and VSWR of the final antenna. Shaded: 2:1 VSWR bands reported in the paper (2.405–2.5 GHz and 4.52–5.9 GHz).')}
<p>The openEMS model shows the expected dual-band behaviour. The <b>lower resonance at {lo_b[2]:.3f} GHz</b> (S<sub>11</sub> = {lo_b[3]:.1f} dB)
is produced by the SIR, and the <b>upper band, {hi_b[0]:.2f}–{hi_b[1]:.2f} GHz</b> ({bw_high*1e3:.0f} MHz, minimum {hi_b[3]:.1f} dB at {hi_b[2]:.2f} GHz),
by the bent dipole. Compared with the HFSS simulation in paper Fig. 6 (≈ 2.45 GHz and ≈ 4.9 GHz, read off the plot), our lower resonance is about
{(lo_b[2]/2.45-1)*100:.0f} % higher and our upper resonance about {(1-hi_b[2]/4.9)*100:.0f} % lower. Our lower-band match is also shallower,
giving only {bw_low:.0f} MHz of −10 dB bandwidth against 95 MHz measured. Both differences point to the coupling between the dipole tips and the SIR
being weaker in our model than in the authors': the tip shape and the exact position of the SIR are the least well specified features of paper Fig. 2,
and Section 6.5 shows that the lower band is very sensitive to C. The narrow lower band is typical of a high-Q resonator coupled through a small capacitance.
The measured upper band of the paper (4.52–5.9 GHz) is wider than even its own simulation, which the authors attribute to return current on the
coaxial feed cable of the unbalanced SMA connection — an effect that a lumped-port simulation does not include.</p>
{fig('zin_final.png', 'openEMS: input impedance of the final antenna. Both resonances are close to 50 Ω real with a zero crossing of the reactance.', '62%')}
''')

add(f'''
<h3>6.2 Design evolution</h3>
{fig('evolution_s11.png', 'openEMS: S<sub>11</sub> of the five evolution stages (compare with paper Fig. 1).')}
<table class="t"><caption>Table 3: Resonances of the evolution stages — paper (HFSS, read from Fig. 1) vs this work (openEMS)</caption>
<tr><th>Stage</th><th>Paper: lower</th><th>Paper: upper</th><th>openEMS: lower (S<sub>11</sub>)</th><th>openEMS: upper (S<sub>11</sub>)</th></tr>
<tr><td>(a) planar dipole</td><td>—</td><td>5.0 GHz, matched</td><td>—</td><td>{evf('a','high')}</td></tr>
<tr><td>(b) dipole + UIR</td><td>tendency only</td><td>4.9 GHz, poor match</td><td>—</td><td>{evf('b','high')}</td></tr>
<tr><td>(c) bent dipole + UIR</td><td>3.14 GHz, poor</td><td>4.2 GHz, matched</td><td>—</td><td>{evf('c','high')}</td></tr>
<tr><td>(d) bent dipole + folded UIR</td><td>2.9 GHz</td><td>4.6 GHz</td><td>{evf('d','low')}</td><td>{evf('d','high')}</td></tr>
<tr><td>(e) bent dipole + SIR</td><td>2.4 GHz</td><td>≈ 4.9 GHz</td><td>{evf('e','low')}</td><td>{evf('e','high')}</td></tr>
</table>
<p>The main trends are reproduced. Top-loading the planar dipole with a UIR pulls its resonance down ((a) → (b)), and folding the UIR
creates a well-matched lower resonance ((d): {evf('d','low')}, within 3 % of the paper's 2.9 GHz) while the dipole mode stays near 4.6–4.7 GHz.
Replacing the UIR with an SIR of the <i>same physical length</i> then moves the lower resonance down by
{(ev['d'][0][0] if ev.get('d') else 0) - lo_b[2]:.2f} GHz with almost no change in the upper band — direct evidence that the SIR lowers the resonance
through the impedance ratio k rather than through length. Stage (c) is the one that disagrees: our straight UIR spans the full 23 mm SIR footprint just above
the arc tips, which detunes the dipole more strongly than in the paper. The paper does not give the UIR dimensions for stages (b) and (c), so this
stage depends most on our assumptions.</p>
<h3>6.3 Effect of the SIR and UIR vs SIR loading</h3>
{fig('sir_effect.png', 'openEMS: (left) with and without the SIR — the SIR adds the 2.4 GHz band and only slightly shifts the dipole mode (paper Fig. 4); (right) folded UIR vs folded SIR of equal length (paper Fig. 5).')}
<p>Without the SIR the bent dipole has a single resonance at {BENT}, close to the 5 GHz of paper Fig. 4. Adding the SIR creates the
lower resonance and shifts the dipole mode down slightly, because the SIR adds capacitance at the open ends of the dipole — the same behaviour the
authors describe. The right-hand plot reproduces the key point of paper Fig. 5: the two resonances are independent and not harmonically related
(f<sub>high</sub>/f<sub>low</sub> ≈ {hi_b[2]/lo_b[2]:.2f}, not 2 or 3).</p>
''')

add(f'''
<h3>6.4 Electric field and surface current distribution</h3>
{fig('efield.png', 'openEMS: normalised |E| on the copper plane at 2.4 GHz and 5.3 GHz (compare with paper Fig. 10).')}
{fig('current.png', 'openEMS: normalised surface-current magnitude with direction arrows at 2.4 GHz and 5.3 GHz (compare with paper Fig. 11).')}
<p>At 2.4 GHz the strongest E-field is concentrated in the gaps C between the dipole tips and the SIR bars and along the thin SIR section, confirming
that the SIR is excited capacitively by the voltage maxima at the open ends of the dipole (paper Fig. 10). The current is largest on the SIR — especially on
the high-impedance 0.2 mm strip, which carries the current maximum of the fundamental SIR mode — while the y-directed currents on the two folded arms flow
in opposite directions. At 5.3 GHz the current is concentrated on the bent dipole near the feed and decays towards the tips, as expected for a half-wave
dipole mode, and the SIR carries comparatively little current. In both bands the y-components cancel by symmetry, leaving a net x-directed current, so the
antenna is x-polarised in both bands, as the paper reports and verifies experimentally.</p>
''')

ffr = lambda i: f"{ff['Dmax_dBi'][i]:.2f}"
add(f'''
<h3>6.5 Radiation patterns, gain and efficiency</h3>
{fig('openems_3d/farfield_2p45GHz.png', 'openEMS: 3D directivity pattern at 2.45 GHz (dBi).', '72%')}
{fig('openems_3d/farfield_5p2GHz.png', 'openEMS: 3D directivity pattern at 5.2 GHz (dBi); note the null along the x axis (dipole axis).', '72%')}
{fig('patterns.png', 'openEMS: directivity cuts (dBi) in the XZ (E-), YZ (H-) and XY planes at 2.45 GHz (top) and 5.2 GHz (bottom).')}
{fig('gain.png', 'openEMS: directivity, IEEE gain and realised gain vs frequency, with the measured peak gains of the paper.', '72%')}
<p>Both bands show the doughnut-shaped pattern of a short x-directed dipole: an almost omnidirectional YZ (H) plane, and minima along the x axis
in the XZ (E) and XY planes. At 5.2 GHz these are deep nulls (&gt; 20 dB). At 2.45 GHz they are only ≈ 8 dB deep, because the y-directed currents on the
folded SIR arms do not cancel completely. This agrees with the "nearly omnidirectional" measured patterns of paper Fig. 15. Directivity is {ffr(1)} dBi at 2.45 GHz
and {ffr(2)} dBi at 5.2 GHz. The simulated gain is {g245[2]:.2f} dBi at 2.45 GHz and {g52[2]:.2f} dBi at 5.2 GHz (at the lower resonance
{peak_lo[2]:.2f} dBi at {peak_lo[0]:.2f} GHz; peak in the upper −10 dB band {peak_hi[2]:.2f} dBi at {peak_hi[0]:.2f} GHz), against 2.6 dBi and 3.6 dBi measured. The radiation
efficiency is {g245[4]*100:.0f} % at 2.45 GHz and {g52[4]*100:.0f} % at 5.2 GHz. The lower efficiency in the 2.4 GHz band is expected: the high-Q SIR
mode stores a lot of energy in the lossy FR4 (we assumed tan δ = 0.02), whereas the paper's Wheeler-cap measurement gives 88.6 %. The gain we compute is
therefore sensitive to the assumed loss tangent and should be read as a conservative estimate.</p>
''')

swr = lambda k: (f"{sw[k][0]:.3f} / {sw[k][1]:.2f}" if k in sw else '—')
swm = lambda k: (f"{sw[k][2]:.1f} / {sw[k][3]:.1f}" if k in sw else '—')
add(f'''
<h3>6.6 Parametric study</h3>
{fig('parametric.png', 'openEMS: parametric sweeps of the coupling gap C, the substrate permittivity ε<sub>r</sub> and the thickness h.')}
<table class="t"><caption>Table 4: Parametric study — resonant frequencies (GHz) and S<sub>11</sub> minima (dB), lower / upper band</caption>
<tr><th>Case</th><th>f<sub>low</sub> / f<sub>high</sub> (GHz)</th><th>S<sub>11</sub> low / high (dB)</th><th>Case</th><th>f<sub>low</sub> / f<sub>high</sub> (GHz)</th><th>S<sub>11</sub> low / high (dB)</th></tr>
<tr><td>C = 0.2 mm</td><td>{swr('C=0.2')}</td><td>{swm('C=0.2')}</td><td>ε<sub>r</sub> = 4.0</td><td>{swr('er=4.0')}</td><td>{swm('er=4.0')}</td></tr>
<tr><td>C = 0.4 mm (nominal)</td><td>{swr('C=0.4')}</td><td>{swm('C=0.4')}</td><td>ε<sub>r</sub> = 4.6</td><td>{swr('er=4.6')}</td><td>{swm('er=4.6')}</td></tr>
<tr><td>C = 0.8 mm</td><td>{swr('C=0.8')}</td><td>{swm('C=0.8')}</td><td>h = 1.2 mm</td><td>{swr('h=1.2')}</td><td>{swm('h=1.2')}</td></tr>
<tr><td></td><td></td><td></td><td>h = 2.0 mm</td><td>{swr('h=2.0')}</td><td>{swm('h=2.0')}</td></tr>
</table>
<p>__PARAM_TEXT__</p>
''')

# ---------------- 7 analytical ----------------
add(f'''
<h2>7. Analytical Verification of the SIR (Eq. 4, Table III)</h2>
<p>Eq. (4) was solved numerically (Brent's method in Python, <code>fzero</code> in MATLAB — <code>analysis/sir_analysis.py</code> / <code>.m</code>)
for the paper's k = 0.45644 and α = 0.7306, which gives θ<sub>t</sub> = 143.57°, θ<sub>1</sub> = 19.34° and θ<sub>2</sub> = 52.44°
(check: tan θ<sub>1</sub> tan θ<sub>2</sub> = 0.45644). Converting to physical length needs ε<sub>eff</sub> of each CPS line, which the paper does not
state. Writing the thin centre section as electrical length 2θ<sub>1</sub> (physical l<sub>1</sub>) and each folded arm as θ<sub>2</sub> (physical l<sub>2</sub>),
Table III is reproduced exactly with ε<sub>eff,1</sub> ≈ 2.03 and ε<sub>eff,2</sub> ≈ 2.40, both physically reasonable for CPS on 1.6 mm FR4
(between 1 and (ε<sub>r</sub>+1)/2 = 2.65). Since l·f is constant in every row of Table III, the paper's analytical lengths follow from a single pair of
ε<sub>eff</sub> values.</p>
{fig('../analysis/figures/sir_analysis.png', '(Left) SIR fundamental-mode electrical length versus impedance ratio k: k = 0.456 gives a 20 % shorter resonator than a UIR. (Right) Table III reproduced from eq. (4), with the paper’s analytical and simulated lengths.')}
<p>The simulated lengths in the paper are 4–10 % shorter than the analytical ones because of fringing fields at the open ends and the folds, which the
transmission-line model ignores. The authors fabricated the simulated set for 2.2 GHz (l<sub>1</sub> = 9.62 mm, l<sub>2</sub> = 12.4 mm), so the 2.2 GHz design
moves up to 2.4 GHz once the 90° bend and the coupling to the dipole are added (Sec. III-D of [1]).</p>
''')

# ---------------- 8 comparison ----------------
add(f'''
<h2>8. Summary Comparison</h2>
<table class="t"><caption>Table 5: Paper vs this work (paper "sim" values read from Fig. 6; "meas" from the text)</caption>
<tr><th>Quantity</th><th>Paper (HFSS sim / measured)</th><th>openEMS (this work)</th></tr>
<tr><td>Lower resonance</td><td>≈ 2.45 GHz / 2.38–2.47 GHz</td><td>{lo_b[2]:.3f} GHz ({lo_b[3]:.1f} dB)</td></tr>
<tr><td>Lower −10 dB band</td><td>2.405–2.5 GHz (95 MHz)</td><td>{lo_b[0]:.3f}–{lo_b[1]:.3f} GHz ({bw_low:.0f} MHz)</td></tr>
<tr><td>Upper resonance</td><td>≈ 4.9 GHz / ≈ 5.5 GHz</td><td>{hi_b[2]:.2f} GHz ({hi_b[3]:.1f} dB)</td></tr>
<tr><td>Upper −10 dB band</td><td>4.52–5.9 GHz (1.38 GHz)</td><td>{hi_b[0]:.2f}–{hi_b[1]:.2f} GHz ({bw_high:.2f} GHz)</td></tr>
<tr><td>Gain, lower band</td><td>2.6 dBi @ 2.48 GHz</td><td>{peak_lo[2]:.2f} dBi @ {peak_lo[0]:.2f} GHz</td></tr>
<tr><td>Peak gain, upper band</td><td>3.6 dBi @ 5.35 GHz</td><td>{peak_hi[2]:.2f} dBi @ {peak_hi[0]:.2f} GHz</td></tr>
<tr><td>Polarisation / pattern</td><td>x-polarised, nearly omni</td><td>x-polarised, omni in YZ plane</td></tr>
<tr><td>Size</td><td colspan="2">25 × 9 × 1.6 mm (0.36 cm³ substrate); ka ≈ 0.80 at 2.4 GHz → physically small antenna</td></tr>
</table>
''')

# ---------------- 9 limitations ----------------
add(f'''
<h2>9. Sources of Discrepancy and Limitations</h2>
<ol>
<li><b>Geometry ambiguity.</b> The arc-tip shape, the vertical position of the SIR and the dimensions of the stage (b)/(c) UIR are not given numerically.
Section 6.6 shows that C alone moves the lower band by more than 100 MHz, so a few tenths of a millimetre in the tip position explain the ≈ 4 % offset.</li>
<li><b>Solver differences.</b> The paper used HFSS (FEM, tetrahedral mesh); openEMS is a time-domain method on a rectilinear mesh.
The curved arms are staircased in FDTD, and the 0.2 mm strip and 0.4 mm gap are only 2–4 cells wide, which shifts high-Q resonances by a few percent.</li>
<li><b>Material data.</b> FR4 tan δ and copper thickness are not specified; they mainly affect gain and efficiency, not the resonant frequencies.</li>
<li><b>Feed.</b> We simulate the balanced coplanar antenna with an ideal port. The paper's measured coplanar results include the effect of the unbalanced
SMA feed, which is why its measured upper band is wider. The double-sided microstrip-fed prototype (paper Fig. 7) was not modelled because its overlap geometry is not fully specified.</li>
<li><b>No fabrication / measurement.</b> All our results are simulated.</li>
</ol>

<h2>10. Conclusion</h2>
<p>We modelled the dual-band SIR coupled dipole of Deepak <i>et al.</i> from its published dimensions, simulated it with the openEMS FDTD solver. The simulations confirm the design principle: a half-ring dipole supplies a broad band around
{hi_b[2]:.1f} GHz, and a folded coplanar-stripline SIR, coupled capacitively through a 0.4 mm gap at the dipole's open ends, adds an independent, non-harmonic
resonance near 2.4–2.5 GHz, with both bands x-polarised and nearly omnidirectional. Replacing a UIR by an SIR of identical length lowers the
resonance through the impedance ratio alone; the analytical model gives the same conclusion, with k = 0.456 shortening the resonator from 180° to 143.6°.
The remaining few-percent offsets from the paper can be traced to unspecified geometry details and to solver differences, and the parametric study identifies
the coupling gap C as the main knob for retuning the lower band. Fabricating the double-sided prototype and measuring its patterns would complete the validation.</p>

<h2>References</h2>
<ol class="refs">
<li>U. Deepak, T. K. Roshna, C. M. Nijas, K. Vasudevan and P. Mohanan, "A Dual Band SIR Coupled Dipole Antenna for 2.4/5.2/5.8 GHz Applications," <i>IEEE Trans. Antennas Propag.</i>, 2015, DOI: 10.1109/TAP.2015.2393876.</li>
<li>M. Makimoto and S. Yamashita, "Bandpass filters using parallel coupled stripline stepped impedance resonators," <i>IEEE Trans. Microw. Theory Techn.</i>, vol. 28, no. 12, pp. 1413–1417, Dec. 1980.</li>
<li>M. Makimoto and S. Yamashita, <i>Microwave Resonators and Filters for Wireless Communication: Theory, Design and Application</i>. Berlin: Springer, 2001.</li>
<li>C. A. Balanis, <i>Antenna Theory: Analysis and Design</i>, 4th ed. Hoboken, NJ: Wiley, 2016.</li>
<li>T. Liebig, <i>openEMS — a free and open electromagnetic field solver</i>, https://openems.de.</li>
</ol>
</body></html>''')

doc = '\n'.join(H).replace('__PARAM_TEXT__', open(os.path.join(HERE, 'param_text.html')).read())
open(os.path.join(HERE, 'report.html'), 'w').write(doc)
pdf = os.path.join(HERE, 'Group12_SIR_Coupled_Dual_Band_Dipole_Antenna.pdf')
foot = ('<div style="font-size:7.5px;width:100%;text-align:center;color:#555;font-family:Times New Roman,Liberation Serif,serif">'
        'PDPM IIITDM Jabalpur • Department of Electronics and Communication Engineering • 2026 &nbsp;&nbsp;|&nbsp;&nbsp; Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>')
head = ('<div style="font-size:7.5px;width:100%;text-align:right;margin-right:14mm;color:#555;font-family:Times New Roman,Liberation Serif,serif">'
        f'{TITLE} | {GROUP} | OE4E25</div>')
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = b.new_page(); pg.goto('file://' + os.path.join(HERE, 'report.html')); pg.wait_for_timeout(500)
    pg.pdf(path=pdf, format='A4', print_background=True, display_header_footer=True, header_template=head, footer_template=foot,
           margin=dict(top='16mm', bottom='16mm', left='16mm', right='16mm'))
    b.close()
print('wrote', pdf)
