#!/usr/bin/env python3
"""
O45 — 內稟冷斑 SMHW 模型預言 (Intrinsic cold spot model prediction)
"""
import os, sys, json
import numpy as np
import healpy as hp
from scipy.special import eval_legendre

def smhw_wl(R_rad, lmax, npts=200):
    gamma, wgt = np.polynomial.legendre.leggauss(npts)
    gamma = (gamma+1)*np.pi/2; wgt = wgt*np.pi/2
    x = gamma/(2*R_rad)
    psi = (2*np.pi)**(-0.5)/R_rad*(1+x**2)*(2-x**2)*np.exp(-gamma**2/(2*R_rad**2))
    cg = np.cos(gamma); ls = np.arange(lmax+1)
    wl = np.empty(lmax+1)
    for l in ls:
        wl[l] = 2*np.pi*np.sum(wgt*psi*eval_legendre(l,cg)*np.sin(gamma))
    return wl

PROJECT = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
OUTDIR = os.path.join(PROJECT, 'open_problems_fresh/o45_smhw_verify/data')
nside = 1024
lmax = 3*nside
A = 134.2
npix = hp.nside2npix(nside)
pix0 = hp.ang2pix(nside, 209, -57, lonlat=True)

# Models
v0 = hp.ang2vec(209, -57, lonlat=True)
v = hp.pix2vec(nside, np.arange(npix))
ang = np.degrees(np.arccos(np.clip(
    v[0]*v0[0] + v[1]*v0[1] + v[2]*v0[2], -1, 1)))

models = {
    'R8_smoothed': {'sigma': 4.17/2.355, 'desc': 'R8 平滑核 (σ=1.771°), A=134.2 μK'},
    'intrinsic':   {'sigma': 8.66/2.355, 'desc': '內稟冷斑 (FWHM=8.66°, σ=3.68°), A=134.2 μK'},
    'intrinsic_x2': {'sigma': 8.66/2.355, 'A': 2*A, 'desc': '內稟冷斑 ×2 (A=268.4 μK)'},
}

# Load observed
obs = json.load(open(os.path.join(OUTDIR, '01_smhw_results.json')))

print(f"{'R(°)':>6}", end='')
for name in models:
    print(f" {name:>14}", end='')
print(f" {'Obs(μK)':>10} {'BestMatch':>12}")
print('-' * 70)

for R in [1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0]:
    wl = smhw_wl(np.radians(R), lmax)
    obs_val = obs['smhw'][str(R)]['T_wavelet']
    
    print(f"{R:>6.2f}", end='')
    best_match = ''
    best_diff = 1e9
    
    for name, params in models.items():
        sigma = params['sigma']
        amp = params.get('A', A)
        m = -amp * np.exp(-ang**2/(2*sigma**2)) * 1e-6
        a = hp.map2alm(m, lmax=lmax)
        aw = hp.almxfl(a, wl)
        wm = hp.alm2map(aw, nside=nside, lmax=lmax)
        alo = hp.almxfl(a, wl * (np.arange(lmax+1) < 3))
        wm -= hp.alm2map(alo, nside=nside, lmax=lmax)
        p = float(wm[pix0]) * 1e6
        diff = abs(abs(p) - abs(obs_val))
        if diff < best_diff:
            best_diff = diff
            best_match = name
        print(f" {p:>14.2f}", end='')
    
    print(f" {obs_val:>10.2f} {best_match:>12}")

print()
print("模型描述:")
for name, params in models.items():
    print(f"  {name}: {params['desc']}")