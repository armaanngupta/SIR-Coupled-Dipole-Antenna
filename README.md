# Dual Band SIR Coupled Dipole Antenna for 2.4 / 5.2 / 5.8 GHz — Course Project (OE4E25)

Course project for **OE4E25 – Advanced Antenna Theory and Design**, PDPM IIITDM Jabalpur.
We reproduce and analyse:

> U. Deepak, T. K. Roshna, C. M. Nijas, K. Vasudevan and P. Mohanan, "A Dual Band SIR Coupled Dipole Antenna for
> 2.4/5.2/5.8 GHz Applications," *IEEE Trans. Antennas Propag.*, 2015, DOI 10.1109/TAP.2015.2393876.

| Member | Roll No. |
|---|---|
| Armaan Gupta | 23BSM014 |
| Ayush Tiwari | 23BEC025 |
| Rajesh Singh | 23BEC091 |

## Repository layout
```
report/            report source (build_report.py -> HTML -> PDF) and the submitted PDF
openems/           full-wave FDTD model (openEMS)
  sir_dipole.py      parametric model; cases a, b, c, d, e, bent; --sweep NAME=VALUE; --fields
  run_all.sh         runs every case + parametric sweeps
  plot_results.py    makes all figures in figures/
  plot_geometry.py   top-view drawings of the modelled geometries
analysis/          analytical SIR model (eq. 4, Table III) in Python and MATLAB
figures/           generated plots
```

## Reproducing
```bash
# openEMS (Linux): build from https://github.com/thliebig/openEMS-Project, then
cd openems && bash run_all.sh && python3 plot_results.py && python3 plot_geometry.py
cd ../analysis && python3 sir_analysis.py        # or run sir_analysis.m in MATLAB/Octave
cd ../report && python3 build_report.py           # rebuilds the PDF
```

## Modelling assumptions (not fully specified in the paper)
* Arc tips are cut **horizontally** at H = 4.1 mm above the inner arc bottom (y = −2.9 mm from the arc centre);
  the SIR bars sit a gap C = 0.4 mm above that cut. Each dipole arm is then ≈ 9.1 mm long (mean-radius arc).
* The thin SIR section (W2 = 0.2 mm) is centred on the wide bars.
* FR4 loss tangent 0.02 (not given in the paper). Zero-thickness PEC copper. 50 Ω lumped port across the feed gap G.
* Evolution cases (a)–(c) use a straight UIR spanning the SIR footprint (23.02 mm) and straight dipole arms of the same 9.1 mm length.
* Eq. (4) maps electrical to physical length via ε_eff of the two CPS lines, which the paper does not give; we
  back-calculate ε_eff ≈ 2.03 (thin section, length 2θ1) and ≈ 2.40 (wide arm, length θ2) from Table III.
