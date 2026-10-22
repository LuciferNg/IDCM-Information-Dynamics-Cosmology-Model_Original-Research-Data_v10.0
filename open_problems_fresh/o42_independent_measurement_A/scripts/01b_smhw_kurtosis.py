#!/usr/bin/env python3
"""
O42 — Step 1b: SMHW kurtosis 檢驗 (Cruz 2005 原方法)
====================================================
Cruz 2005 用 SMHW 係數嘅 kurtosis 超高斯檢驗非高斯性, 冷斑係唯一來源。
呢個先係文獻驗證 A 嘅正確方法 — 唔係「單一係數=134 μK」,
而係「冷斑係 SMHW 係數嘅極端異常」。

方法:
  1. SMHW 係數 map (R = 250' = 4.17°, 文獻尺度)
  2. 全天空 kurtosis (無偏估計)
  3. 冷斑位置係數 rank (1/60 節點? 全天空 percentile?)
  4. Gaussian 模擬對照: 隨機相位 map 嘅 kurtosis 分佈
"""
import os, json
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u

OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
NODES = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
RAW = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o26_node57_region/data/smica_iqu_2048.fits'

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

nodes = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_arr = np.array([float(g.l.deg) for g in gal])
b_arr = np.array([float(g.b.deg) for g in gal])

# 讀 raw (K_CMB) → 1024 → lmax
m = hp.read_map(RAW, field=0)
m = hp.ud_grade(hp.remove_dipole(m), 1024)
nside = 1024
lmax = 3*nside
a_lm = hp.map2alm(m, lmax=lmax)
print(f"prepared: nside={nside}")

for R in [3.0, 4.17, 5.0, 7.0]:
    wl = smhw_wl(np.radians(R), lmax)
    # 無偏: 扣 l<3
    alm_w = hp.almxfl(a_lm, wl)
    wmap = hp.alm2map(alm_w, nside=nside, lmax=lmax)
    alm_lo = hp.almxfl(a_lm, wl * (np.arange(lmax+1) < 3))
    wmap -= hp.alm2map(alm_lo, nside=nside, lmax=lmax)
    
    # 統計
    w_uK = wmap * 1e6
    kurt = np.mean((w_uK - w_uK.mean())**4) / np.std(w_uK)**4 - 3
    pix0 = hp.ang2pix(nside, l_arr[0], b_arr[0], lonlat=True)
    T0 = w_uK[pix0]
    # 全天空 percentile
    pct = np.mean(w_uK < T0) * 100
    # 60 節點 rank
    T_all = w_uK[hp.ang2pix(nside, l_arr, b_arr, lonlat=True)]
    rank = int(np.sum(T_all < T0) + 1)
    print(f"R={R}°: kurtosis={kurt:+.3f} 冷斑係數={T0:+.2f} μK percentile={pct:.3f}% rank={rank}/60")

# Gaussian 對照 (kurtosis 期望 0 ± sigma)
print()
print("Gaussian kurtosis 期望: 0 ± sqrt(24/N) = 0 ± %.4f" % np.sqrt(24/len(m)))
