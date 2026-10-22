#!/usr/bin/env python3
"""
O42 新線 C2 — 冷斑 SMHW 超額係數 vs 背景 (關鍵測試)
=====================================================
問題: 實測冷斑 SMHW 係數 (−31 μK) 含背景 CMB 貢獻, 唔可以直接同純冷斑模型比。
方法: 用「超額」= 冷斑係數 − 60 節點背景 median, 同純冷斑模型比。
      (60 節點均勻分佈全天 → 佢哋嘅 median 代表背景 level)
"""
import os, json
import numpy as np
import healpy as hp
from scipy.special import eval_legendre

OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
RAW = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o26_node57_region/data/smica_iqu_2048.fits'
NODES = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'

from astropy.coordinates import SkyCoord
import astropy.units as u
nodes = np.loadtxt(NODES)
scs = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gg = scs.galactic
l_arr = np.array([float(g.l.deg) for g in gg])
b_arr = np.array([float(g.b.deg) for g in gg])

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

# raw → 1024
m = hp.read_map(RAW, field=0)  # K_CMB
m = hp.ud_grade(hp.remove_dipole(m), 1024)
nside = 1024
lmax = 3*nside
a_lm = hp.map2alm(m, lmax=lmax)
pixs = hp.ang2pix(nside, l_arr, b_arr, lonlat=True)

print(f"{'R(°)':>6} {'冷斑係數':>10} {'60節點med':>10} {'超額':>10} {'背景std':>10}")
print("-" * 50)
excess = {}
for R in [1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0]:
    wl = smhw_wl(np.radians(R), lmax)
    alm_w = hp.almxfl(a_lm, wl)
    wmap = hp.alm2map(alm_w, nside=nside, lmax=lmax)
    alm_lo = hp.almxfl(a_lm, wl * (np.arange(lmax+1) < 3))
    wmap -= hp.alm2map(alm_lo, nside=nside, lmax=lmax)
    w_uK = wmap * 1e6
    T0 = w_uK[pixs[0]]
    T60 = w_uK[pixs]
    med = np.median(T60)
    std = T60.std()
    exc = T0 - med
    excess[R] = dict(coldspot=float(T0), median60=float(med), excess=float(exc), std60=float(std))
    print(f"{R:>6.2f} {T0:>10.2f} {med:>10.2f} {exc:>10.2f} {std:>10.2f}")

# 超額 vs 高斯模型 (07 已算: 高斯 dip 嘅純 SMHW 響應)
w_gauss = {1.0: -9.26, 2.0: -10.85, 3.0: -9.38, 4.17: -7.51, 5.0: -6.45, 7.0: -4.67, 10.0: -3.12}
print()
print("超額 vs 高斯模型響應:")
for R in [1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0]:
    exc = excess[R]['excess']
    wg = w_gauss[R]
    # 高斯模型係 A=134.2 純 dip 嘅響應, 單位 μK
    print(f"  R={R:>5.2f}°: 超額 {exc:+.2f} vs 高斯模型 {wg:+.2f} → 比率 {exc/wg:.2f}")
