#!/usr/bin/env python3
"""
O32-14: 視覺化 — RAR + BTFR + 旋轉曲線
========================================
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

c = 299792.458
R_H = 4129.94
H0_idcm = c / R_H
Mpc_to_km = 3.085677581e19
c_ms = c * 1e3
H0_s = H0_idcm / Mpc_to_km
G = 6.674e-11
Msun = 1.989e30
kpc_to_m = 3.085677581e19

A0_IDCM = c_ms * H0_s / (2 * np.pi)   # 1.1225e-10
A0_MOND = 1.2e-10

# ============ 1. RAR 圖 ============
# 官方 bins
rar_bins = []
with open('data/RARbins.mrt') as f:
    for line in f:
        parts = line.split()
        if len(parts) == 4:
            try:
                rar_bins.append((float(parts[0]), float(parts[1]), float(parts[2]), int(parts[3])))
            except ValueError:
                continue
rar_bins = np.array(rar_bins)

def interp_log(gbar_log, a0):
    gbar = 10**gbar_log
    y = a0 / np.maximum(gbar, 1e-30)
    return np.log10(gbar * (1 + np.sqrt(1 + 4 * y)) / 2)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# RAR
ax = axes[0]
x_plot = np.linspace(-12, -8, 100)
ax.errorbar(rar_bins[:, 0], rar_bins[:, 1], yerr=rar_bins[:, 2],
            fmt='o', color='black', capsize=3, label='SPARC bins (Lelli+2017)', zorder=3)
ax.plot(x_plot, interp_log(x_plot, A0_IDCM), 'r-', linewidth=2,
        label=f'IDCM a₀=cH₀/2π={A0_IDCM:.2e} (0 param)', zorder=2)
ax.plot(x_plot, interp_log(x_plot, A0_MOND), 'b--', linewidth=2,
        label=f'MOND a₀={A0_MOND:.1e} (1 param)', zorder=2)
ax.plot(x_plot, x_plot, 'k:', linewidth=1, label='Newtonian (slope 1)')
ax.plot(x_plot, x_plot/2 + np.log10(2), 'g:', linewidth=1, label='Deep-MOND (slope 0.5)')
ax.set_xlabel(r'log $g_{bar}$ [m/s²]')
ax.set_ylabel(r'log $g_{obs}$ [m/s²]')
ax.set_title('Radial Acceleration Relation\nIDCM zero-parameter vs MOND')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

# ============ 2. BTFR 圖 ============
btfr = []
with open('data/BTFR_Lelli2016a.mrt') as f:
    for line in f:
        parts = line.split()
        if len(parts) < 9:
            continue
        name = parts[0]
        if not name or name in ('Galaxy', 'Authors', 'Table', 'Title:') or not name[0].isalpha():
            continue
        try:
            logMb = float(parts[4])
            logVf = float(parts[6])
            btfr.append((logMb, logVf))
        except ValueError:
            continue

btfr = np.array(btfr)
ax = axes[1]
ax.scatter(btfr[:, 1], btfr[:, 0], s=20, alpha=0.7, color='steelblue',
           label=f'SPARC BTFR ({len(btfr)} galaxies)')
v_plot = np.linspace(0.9, 2.6, 50)
# IDCM: logMb = 4·logVf + intercept_idcm
intercept_idcm = 4*np.log10(1e3) - np.log10(G*A0_IDCM) - np.log10(Msun)
ax.plot(v_plot, 4*v_plot + intercept_idcm, 'r-', linewidth=2,
        label=f'IDCM: V⁴=GM·a₀ (slope 4, 0 param)')
# fit
slope, intercept = np.polyfit(btfr[:, 1], btfr[:, 0], 1)
ax.plot(v_plot, slope*v_plot + intercept, 'k--', linewidth=1.5,
        label=f'Fit: slope={slope:.2f}')
ax.set_xlabel(r'log $V_f$ [km/s]')
ax.set_ylabel(r'log $M_{bary}$ [$M_\odot$]')
ax.set_title('Baryonic Tully-Fisher Relation')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('docs/rar_btfr.png', dpi=150)
print("保存: docs/rar_btfr.png")

# ============ 3. 旋轉曲線圖 ============
# 從 MassModels 提取 3 個星系
from scipy.optimize import minimize_scalar

def parse_mass_models(path):
    galaxies = {}
    with open(path) as f:
        for line in f:
            if line.startswith(('Title', 'Authors', 'Table', 'Byte', '---', 'Note',
                                '       Spitzer', '======')):
                continue
            line = line.rstrip('\n').rstrip('\r')
            if len(line.strip()) < 40:
                continue
            try:
                name = line[0:11].strip()
                R = float(line[19:25])
                Vobs = float(line[26:32])
                eVobs = float(line[33:38])
                Vgas = float(line[39:45])
                Vdisk = float(line[46:52])
                Vbul = float(line[53:59])
            except ValueError:
                continue
            if name not in galaxies:
                galaxies[name] = []
            galaxies[name].append({
                'R': R, 'Vobs': Vobs, 'eVobs': eVobs,
                'Vgas': Vgas, 'Vdisk': Vdisk, 'Vbul': Vbul
            })
    return galaxies

galaxies = parse_mass_models('data/MassModels_Lelli2016c.mrt')

def interpol_simple(gbar, a0):
    y = a0 / np.maximum(gbar, 1e-30)
    return gbar * (1 + np.sqrt(1 + 4 * y)) / 2

def gal_chi2(ups, gal, a0):
    R = np.array([p['R'] for p in gal]) * kpc_to_m
    Vobs = np.array([p['Vobs'] for p in gal])
    eVobs = np.array([p['eVobs'] for p in gal])
    Vgas_ms = np.array([p['Vgas'] for p in gal]) * 1e3
    Vdisk_ms = np.array([p['Vdisk'] for p in gal]) * 1e3
    Vbul_ms = np.array([p['Vbul'] for p in gal]) * 1e3
    Vbar2 = ups * (Vdisk_ms**2 + Vbul_ms**2) + Vgas_ms**2
    gbar = Vbar2 / R
    gobs_pred = interpol_simple(gbar, a0)
    Vpred = np.sqrt(np.maximum(R * gobs_pred, 0)) / 1e3
    return np.sum(((Vobs - Vpred) / eVobs)**2)

fig2, axes2 = plt.subplots(1, 3, figsize=(15, 5))
for idx, gname in enumerate(['NGC2403', 'NGC3198', 'NGC6503']):
    if gname not in galaxies:
        continue
    gal = galaxies[gname]
    R = np.array([p['R'] for p in gal])
    Vobs = np.array([p['Vobs'] for p in gal])
    eVobs = np.array([p['eVobs'] for p in gal])
    Vgas = np.array([p['Vgas'] for p in gal])
    Vdisk = np.array([p['Vdisk'] for p in gal])
    Vbul = np.array([p['Vbul'] for p in gal])

    # Fit Υ
    res = minimize_scalar(lambda u: gal_chi2(u, gal, A0_IDCM),
                          bounds=(0.05, 2.0), method='bounded')
    ups = res.x

    # 預測
    R_m = R * kpc_to_m
    Vbar2 = ups * ((Vdisk*1e3)**2 + (Vbul*1e3)**2) + (Vgas*1e3)**2
    gbar = Vbar2 / R_m
    gpred = interpol_simple(gbar, A0_IDCM)
    Vpred = np.sqrt(R_m * gpred) / 1e3
    # Kepler (無修正)
    Vkepler = np.sqrt(np.maximum(Vbar2, 0)) / 1e3

    ax = axes2[idx]
    ax.errorbar(R, Vobs, yerr=eVobs, fmt='o', color='black', markersize=4,
                capsize=2, label='Observed', zorder=3)
    ax.plot(R, Vpred, 'r-', linewidth=2, label=f'IDCM (Υ={ups:.2f})')
    ax.plot(R, Vkepler, 'b--', linewidth=1.5, label='Baryonic only')
    ax.set_xlabel('R [kpc]')
    ax.set_ylabel('V [km/s]')
    ax.set_title(f'{gname}')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('docs/rotation_curves.png', dpi=150)
print("保存: docs/rotation_curves.png")
