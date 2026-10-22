#!/usr/bin/env python3
"""
O45 — 閉合攻堅 2: SMHW 係數 ↔ pixel 完整換算 (2026-09-12)
===========================================================
方法:
  1. 高斯 dip 家族 (A=134.2 固定, 掃 σ ∈ [1°, 12°]):
     - T_pix(σ) = 4.17° Gaussian smooth 後中心值
     - w(σ) = SMHW R=4.17° 係數 (harmonic-space, 同 01 一致)
     - 換算曲線: w/T_pix vs σ  (解析形式: T_pix = -A·σ²/(σ²+σ_sm²))
  2. 實測點定位:
     - 由 T_pix=-134.19 → σ_T (pixel 通道)
     - 由 w=-31.17 → σ_w (SMHW 通道)
     - σ_T vs σ_w 一致 → 純高斯閉合; 不一致 → 非高斯修正量化
  3. 完整換算表輸出 (R=1..10° × σ grid)
"""
import os, json, time
import numpy as np
import healpy as hp
from scipy.special import eval_legendre

PROJECT = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

A_IDCM = 134.2
SIGMA_SM = 4.17/2.355   # 1.771° — 4.17° FWHM smooth 核
COLD = (209.0, -57.0)
NSIDE = 1024
LMAX = 3*NSIDE

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

npix = hp.nside2npix(NSIDE)
v0 = hp.ang2vec(COLD[0], COLD[1], lonlat=True)
v = hp.pix2vec(NSIDE, np.arange(npix))
ang = np.degrees(np.arccos(np.clip(v[0]*v0[0]+v[1]*v0[1]+v[2]*v0[2], -1, 1)))
pix0 = hp.ang2pix(NSIDE, COLD[0], COLD[1], lonlat=True)

# ---------- 高斯家族掃描 ----------
sigma_grid = np.arange(1.0, 12.01, 0.5)
scales = [1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0]

# 預計算 SMHW kernels
wl_cache = {R: smhw_wl(np.radians(R), LMAX) for R in scales}

print(f"{'σ(°)':>6} {'T_pix(μK)':>10} {'w4.17(μK)':>10} {'w/T_pix':>8} {'w2(μK)':>9} {'w10(μK)':>9}")
print("-" * 58)

rows = []
for sigma in sigma_grid:
    m = -A_IDCM * np.exp(-ang**2/(2*sigma**2)) * 1e-6  # K
    # T_pix: 4.17° smooth 後中心
    m_sm = hp.smoothing(m, fwhm=np.radians(4.17))
    T_pix = float(m_sm[pix0]) * 1e6
    # SMHW
    a = hp.map2alm(m, lmax=LMAX)
    w_vals = {}
    for R in scales:
        wl = wl_cache[R]
        aw = hp.almxfl(a, wl)
        wm = hp.alm2map(aw, nside=NSIDE, lmax=LMAX)
        alo = hp.almxfl(a, wl * (np.arange(LMAX+1) < 3))
        wm -= hp.alm2map(alo, nside=NSIDE, lmax=LMAX)
        w_vals[R] = float(wm[pix0]) * 1e6
    rows.append({
        'sigma': float(sigma),
        'T_pix': T_pix,
        'w': {str(R): w_vals[R] for R in scales},
        'w_T_pix_R4.17': w_vals[4.17]/T_pix if T_pix != 0 else None,
    })
    print(f"{sigma:>6.2f} {T_pix:>10.2f} {w_vals[4.17]:>10.2f} "
          f"{w_vals[4.17]/T_pix if T_pix else 0:>8.3f} {w_vals[2.0]:>9.2f} {w_vals[10.0]:>9.2f}")

# ---------- 解析 T_pix 公式驗證 ----------
print("\n解析公式驗證: T_pix = -A·σ²/(σ²+σ_sm²)")
for sigma in [2.0, 3.5, 5.0, 8.0]:
    row = next(r for r in rows if abs(r['sigma']-sigma) < 0.01)
    analytic = -A_IDCM * sigma**2/(sigma**2 + SIGMA_SM**2)
    print(f"  σ={sigma:>4.1f}°: 數值={row['T_pix']:>8.2f}  解析={analytic:>8.2f}  "
          f"偏差={abs(row['T_pix']-analytic)/abs(analytic)*100:.2f}%")

# ---------- 實測點定位 ----------
print("\n實測點定位 (雙通道):")
T_pix_obs = -134.19
w_obs = -31.17

# 1) 由 T_pix 反推 σ (解析解): -T_pix = A·σ²/(σ²+σ_sm²)
#    σ²/(σ²+σ_sm²) = -T_pix/A → σ² = σ_sm²·r/(1-r), r = -T_pix/A
r = -T_pix_obs / A_IDCM
if r < 1:
    sigma_from_T = SIGMA_SM * np.sqrt(r/(1-r))
else:
    sigma_from_T = np.inf
print(f"  由 T_pix={T_pix_obs}: r={r:.4f} → σ_T = {sigma_from_T:.3f}°")

# 2) 由 w 反推 σ (數值插值 w4.17 vs σ)
w_vs_sigma = np.array([row['w']['4.17'] for row in rows])
sig_arr = np.array([row['sigma'] for row in rows])
# 搵 w 最接近 -31.17 嘅 σ (線性插值)
idx = np.argmin(np.abs(w_vs_sigma - w_obs))
if w_vs_sigma[idx] < w_obs:  # w 隨 σ 單調? 檢查
    sigma_from_w = sig_arr[idx]
else:
    sigma_from_w = sig_arr[idx]
# 精細插值
from scipy.interpolate import interp1d
# w 對 σ 可能非單調 (band-pass!), 用最接近點
best = np.argsort(np.abs(w_vs_sigma - w_obs))[:2]
sigma_from_w = float(np.mean(sig_arr[best]))
w_at_sigma_w = float(np.mean(w_vs_sigma[best]))
print(f"  由 w(R=4.17°)={w_obs}: 最近 σ_w = {sigma_from_w:.3f}° (w={w_at_sigma_w:.2f})")

print(f"\n  σ_T = {sigma_from_T:.3f}°  vs  σ_w = {sigma_from_w:.3f}°")
print(f"  純高斯預言: σ_T == σ_w")
print(f"  實測差: |σ_T - σ_w| = {abs(sigma_from_T-sigma_from_w):.3f}°")

# 3) 內稟尺度對照 (O42: σ_int=3.68°)
print(f"  O42 內稟 σ_int = {8.66/2.355:.3f}°")

# ---------- 完整換算表 (R grid × σ grid) ----------
print("\n完整換算表 w(R)/T_pix:")
print(f"  {'σ(°)':>6}", end='')
for R in scales:
    print(f" {f'R{R}':>8}", end='')
print()
for row in rows[::2]:  # 每隔一行
    print(f"  {row['sigma']:>6.1f}", end='')
    for R in scales:
        T = row['T_pix']
        ratio = row['w'][str(R)]/T if T != 0 else 0
        print(f" {ratio:>8.3f}", end='')
    print()

# ---------- 儲存 ----------
out = {
    'product': 'O45 closure-2: SMHW <-> pixel conversion',
    'date': '2026-09-12',
    'A_IDCM': A_IDCM,
    'sigma_smooth': SIGMA_SM,
    'analytic_T_pix': '-A*sigma^2/(sigma^2+sigma_sm^2)',
    'grid': rows,
    'observed': {
        'T_pix': T_pix_obs, 'w_R4.17': w_obs,
        'sigma_from_T': float(sigma_from_T),
        'sigma_from_w': float(sigma_from_w),
        'sigma_int_O42': float(8.66/2.355),
    },
}
with open(os.path.join(OUTDIR, '04_conversion_curve.json'), 'w') as f:
    json.dump(out, f, indent=2)
print(f"\n儲存: {OUTDIR}/04_conversion_curve.json")