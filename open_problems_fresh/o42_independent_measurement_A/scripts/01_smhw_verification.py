#!/usr/bin/env python3
"""
O42 — Step 1: 真 SMHW 小波提取 A (Independent Measurement via Spherical Mexican Hat Wavelet)
============================================================================================
目標: 用 exact SMHW (harmonic-space kernel) 喺多尺度提取冷斑幅度,
      同 pixel 抽樣 (−134.19 μK) 同 O41 結構公式 A = 88×61/40 = 134.2 μK 比較。

方法:
  1. raw SMICA (o26 有 nside2048 raw) → remove_dipole → ud_grade 1024
  2. map2alm (lmax = 3*nside)
  3. SMHW kernel (Antoine & Vandergheynst 1999):
       ψ(γ;R) = (2π)^(-1/2) R^{-1} [1 + (γ/2R)²][2 − (γ/2R)²] exp(−γ²/2R²)
     harmonic 係數: w_l(R) = 2π ∫₀^π ψ(γ;R) P_l(cos γ) sin γ dγ
  4. a_lm × w_l(R) → alm2map → 抽節點 0 + 全 60 節點 rank
  5. 交叉驗證: Difference-of-Gaussians 近似 (SMHW ≈ 帶通) 同一尺度掃描
  6. 報告: 每尺度 T_wavelet, dev vs A=134.2 μK, rank/60

Frame: a5_nodes.txt = ICRS → Galactic (SMICA 係 Galactic frame) — 必須轉換!
"""
import os, sys
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy.special import eval_legendre
from scipy.integrate import fixed_quad

T_cmb = 2.7255
A_IDCM = 134.2  # μK
OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(OUTDIR, exist_ok=True)

RAW = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o26_node57_region/data/smica_iqu_2048.fits'
NODES = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'

# ---------- 節點 (ICRS -> Galactic) ----------
nodes = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_arr = np.array([float(g.l.deg) for g in gal])
b_arr = np.array([float(g.b.deg) for g in gal])

print(f"節點 0: ICRS ({nodes[0,0]:.2f}, {nodes[0,1]:.2f}) -> Gal ({l_arr[0]:.2f}, {b_arr[0]:.2f})")
print(f"A_IDCM = {A_IDCM} μK (= 88×61/40)")
print()

# ---------- 讀 raw + 預處理 ----------
m = hp.read_map(RAW, field=0)
print(f"raw SMICA: nside={hp.get_nside(m)}, finite={np.isfinite(m).mean():.4f}")
m = hp.remove_dipole(m)
m1024 = hp.ud_grade(m, 1024)          # 加速, SMHW R≥1° 唔需要 2048
nside = 1024
npix = hp.nside2npix(nside)
lmax = 3 * nside
print(f"prepared: nside={nside}, lmax={lmax}")
print()

# ---------- SMHW kernel 喺 harmonic 空間 ----------
def smhw_wl(R_rad, lmax, npts=200):
    """w_l(R) = 2π ∫ ψ(γ;R) P_l(cos γ) sin γ dγ   (Gauss-Legendre)"""
    gamma, wgt = np.polynomial.legendre.leggauss(npts)
    gamma = (gamma + 1) * np.pi / 2.0          # [0, π]
    wgt = wgt * np.pi / 2.0
    x = gamma / (2.0 * R_rad)
    psi = (2*np.pi)**(-0.5) / R_rad * (1 + x**2) * (2 - x**2) * np.exp(-gamma**2 / (2*R_rad**2))
    ls = np.arange(lmax+1)
    wl = np.empty(lmax+1)
    # P_l(cos γ) for all l, all γ
    cg = np.cos(gamma)
    for i, l in enumerate(ls):
        pl = eval_legendre(l, cg)
        wl[i] = 2*np.pi * np.sum(wgt * psi * pl * np.sin(gamma))
    return wl

scales = [1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0]   # 度
pix0 = hp.ang2pix(nside, l_arr[0], b_arr[0], lonlat=True)

print(f"{'R(deg)':>8} {'T_wavelet(μK)':>16} {'dev(vs A)':>12} {'rank/60':>8}")
print("-" * 50)
results = {}
a_lm = hp.map2alm(m1024, lmax=lmax)          # 一次計, 全尺度重用
# 文獻無偏修正 (Vielva 2004; Cruz 2005): 喺實空間扣低階模式, 唔用 a_lm 嘅 l<3
for R in scales:
    R_rad = np.radians(R)
    wl = smhw_wl(R_rad, lmax)
    # 應用核: 對每個 m, a_lm * w_l
    alm_w = hp.almxfl(a_lm, wl)
    wmap = hp.alm2map(alm_w, nside=nside, lmax=lmax)
    # 無偏: 扣 l<3 模式 (實空間投影) — 令小波係數反映局部異常而唔係大尺度背景
    alm_lo = hp.almxfl(a_lm, wl * (np.arange(lmax+1) < 3))
    wmap -= hp.alm2map(alm_lo, nside=nside, lmax=lmax)
    # 單位: o26 raw 已係 K_CMB (TUNIT1=K_CMB) — 唔好乘 T_cmb (會變 K²!)
    T0 = float(wmap[pix0]) * 1e6
    T_all = wmap[hp.ang2pix(nside, l_arr, b_arr, lonlat=True)] * 1e6
    rank = int(np.sum(T_all < T0) + 1)
    dev = abs(abs(T0) - A_IDCM) / A_IDCM * 100
    results[R] = dict(T=T0, rank=rank, dev_pct=dev)
    print(f"{R:>8.2f} {T0:>16.2f} {dev:>11.3f}% {rank:>7}/60")

print()
# ---------- DoG 交叉驗證 (SMHW ≈ 帶通近似) ----------
print("DoG 交叉驗證 (高斯差 = 小波帶通近似):")
print(f"{'R(deg)':>8} {'T_DoG(μK)':>16} {'dev(vs A)':>12} {'rank/60':>8}")
print("-" * 50)
dog_results = {}
for R in scales:
    sig = np.radians(R) / (2 * np.sqrt(2 * np.log(2)))   # FWHM=R
    sig2 = sig * 0.5
    m1 = hp.smoothing(m1024, sigma=sig)
    m2 = hp.smoothing(m1024, sigma=sig2)
    dog = m1 - m2
    T0 = float(dog[pix0]) * 1e6
    T_all = dog[hp.ang2pix(nside, l_arr, b_arr, lonlat=True)] * 1e6
    rank = int(np.sum(T_all < T0) + 1)
    dev = abs(abs(T0) - A_IDCM) / A_IDCM * 100
    dog_results[R] = dict(T=T0, rank=rank, dev_pct=dev)
    print(f"{R:>8.2f} {T0:>16.2f} {dev:>11.3f}% {rank:>7}/60")

# ---------- 儲存 ----------
out = dict(
    method='exact SMHW harmonic-space + DoG cross-check',
    raw=RAW, nside=nside, lmax=lmax,
    A_IDCM=A_IDCM, node0_gal=(float(l_arr[0]), float(b_arr[0])),
    smhw={str(R): results[R] for R in scales},
    dog={str(R): dog_results[R] for R in scales},
)
import json
with open(os.path.join(OUTDIR, '01_smhw_results.json'), 'w') as f:
    json.dump(out, f, indent=2)
print(f"\nsaved: {OUTDIR}/01_smhw_results.json")

# ---------- 結論 ----------
R_struct = 4.17
T4 = results[R_struct]['T']; dev4 = results[R_struct]['dev_pct']; rk4 = results[R_struct]['rank']
print()
print("=" * 60)
print(f"結構尺度 R=4.17°: T_SMHW = {T4:.2f} μK, dev = {dev4:.3f}% vs A, rank {rk4}/60")
if dev4 < 5.0:
    print("  ✅ A = 134.2 μK SMHW 獨立提取確認 (dev < 5%)")
else:
    print("  ⚠️ dev 超標, 需調查")
