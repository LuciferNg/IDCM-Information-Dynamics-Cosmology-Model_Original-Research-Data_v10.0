#!/usr/bin/env python3
"""
O45 — SMHW 小波完整數據輸出 (2026-09-12)
==========================================
生成完整 SMHW 小波數據產品:
  1. 60 節點 × 7 尺度 SMHW 係數表 (含全天空 percentile)
  2. 全天空統計 (mean/std/min/max, cold spot percentile)
  3. 冷斑徑向 SMHW 剖面 (0-30° ring 平均, R=4.17°)

輸出: data/02_smhw_full_data.json
Pipeline 同 01_smhw_extract.py 完全一致 (harmonic-space exact SMHW, 扣 l<3)。
"""
import os, sys, json, time
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy.special import eval_legendre

PROJECT = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
RAW = os.path.join(PROJECT, 'open_problems_fresh/o26_node57_region/data/smica_iqu_2048.fits')
NODES = os.path.join(PROJECT, 'main_problems/p4_cmb_cold_spot/data/a5_nodes.txt')
OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

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

# ---------- 節點 (ICRS -> Galactic) ----------
nodes = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_arr = np.array([float(g.l.deg) for g in gal])
b_arr = np.array([float(g.b.deg) for g in gal])

# ---------- 讀 raw + 預處理 ----------
print(f"讀取 raw SMICA...")
t0 = time.time()
m = hp.read_map(RAW, field=0)
m1024 = hp.ud_grade(hp.remove_dipole(m), 1024)
nside = 1024
lmax = 3*nside
npix = hp.nside2npix(nside)
a_lm = hp.map2alm(m1024, lmax=lmax)
print(f"  nside={nside}, lmax={lmax}, T={time.time()-t0:.1f}s")

scales = [1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0]

# ---------- 計算所有尺度係數 map ----------
wmaps = {}   # R -> full-sky wavelet map (uK)
for R in scales:
    t1 = time.time()
    wl = smhw_wl(np.radians(R), lmax)
    alm_w = hp.almxfl(a_lm, wl)
    wmap = hp.alm2map(alm_w, nside=nside, lmax=lmax)
    alm_lo = hp.almxfl(a_lm, wl * (np.arange(lmax+1) < 3))
    wmap -= hp.alm2map(alm_lo, nside=nside, lmax=lmax)
    wmaps[R] = wmap * 1e6
    print(f"  R={R:>5}°: T={time.time()-t1:.1f}s")

# ---------- 1. 60 節點 × 7 尺度係數表 ----------
print("\n60 節點 SMHW 係數...")
node_data = {}
for i in range(60):
    pix = hp.ang2pix(nside, l_arr[i], b_arr[i], lonlat=True)
    row = {'gal': [round(float(l_arr[i]), 4), round(float(b_arr[i]), 4)],
           'icrs': [round(float(nodes[i,0]), 4), round(float(nodes[i,1]), 4)]}
    for R in scales:
        T = float(wmaps[R][pix])
        pct = float(np.mean(wmaps[R] < T) * 100)
        row[f'R{R}'] = {'T': T, 'percentile': pct}
    node_data[f'node{i}'] = row

# ---------- 2. 全天空統計 ----------
print("全天空統計...")
sky_stats = {}
for R in scales:
    w = wmaps[R]
    pix0 = hp.ang2pix(nside, l_arr[0], b_arr[0], lonlat=True)
    T0 = float(w[pix0])
    sky_stats[f'R{R}'] = {
        'mean': float(np.mean(w)),
        'std': float(np.std(w)),
        'min': float(np.min(w)),
        'max': float(np.max(w)),
        'cold_spot_T': T0,
        'cold_spot_percentile': float(np.mean(w < T0) * 100),
        'kurtosis': float(np.mean((w - w.mean())**4) / np.std(w)**4 - 3),
    }

# ---------- 3. 冷斑徑向 SMHW 剖面 (R=4.17°) ----------
print("冷斑徑向剖面 (R=4.17°)...")
R_ref = 4.17
v0 = hp.ang2vec(l_arr[0], b_arr[0], lonlat=True)
v = hp.pix2vec(nside, np.arange(npix))
ang = np.degrees(np.arccos(np.clip(v[0]*v0[0] + v[1]*v0[1] + v[2]*v0[2], -1, 1)))
w_ref = wmaps[R_ref]

radial = []
for lo in np.arange(0, 30, 1.0):
    hi = lo + 1.0
    mask = (ang >= lo) & (ang < hi)
    if mask.sum() > 0:
        radial.append({
            'ring_deg': [float(lo), float(hi)],
            'n_pix': int(mask.sum()),
            'mean_wavelet': float(np.mean(w_ref[mask])),
            'median_wavelet': float(np.median(w_ref[mask])),
        })

# ---------- 儲存 ----------
out = {
    'product': 'O45 SMHW full data export',
    'date': '2026-09-12',
    'method': 'exact SMHW harmonic-space, lmax=3072, subtract l<3',
    'raw_map': RAW,
    'nside': nside,
    'scales': scales,
    'A_IDCM': 134.2,
    'nodes': node_data,
    'sky_stats': sky_stats,
    'radial_profile_R4_17': radial,
}

outpath = os.path.join(OUTDIR, '02_smhw_full_data.json')
with open(outpath, 'w') as f:
    json.dump(out, f, indent=2)

print(f"\n儲存: {outpath} ({os.path.getsize(outpath)/1024:.0f} KB)")

# ---------- 摘要 ----------
print("\n=== 摘要 ===")
print(f"{'R(°)':>6} {'冷斑T(μK)':>10} {'冷斑pct':>8} {'天空std':>8} {'kurt':>7}")
for R in scales:
    s = sky_stats[f'R{R}']
    print(f"{R:>6.2f} {s['cold_spot_T']:>10.2f} {s['cold_spot_percentile']:>7.3f}% "
          f"{s['std']:>8.2f} {s['kurtosis']:>+7.3f}")