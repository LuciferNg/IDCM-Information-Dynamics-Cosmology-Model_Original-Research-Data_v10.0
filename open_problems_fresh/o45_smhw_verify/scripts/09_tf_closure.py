#!/usr/bin/env python3
"""
O45 — 閉合攻堅 4: Thomas-Fermi 凝聚輪廓 (2026-09-12)
======================================================
物理: 冷斑 = W-field 凝聚 (O39/O41)。凝聚密度 = Thomas-Fermi 輪廓
      (mean-field BEC: ρ ∝ max(μ−V(r),0), 諧振陷阱 → inverted parabola)

模型: δT(θ) = −A·max(1−(θ/R_TF)², 0)   (A=134.2 固定, fit R_TF)

結構預言: R_TF = 2×R8 = 8.34° (凝聚半徑 = 2×觀測核, O42 內稟閉合)

驗證通道:
  1. T_pix (4.17° smooth 中心) = −134.19 μK
  2. w(SMHW R=4.17°) = −31.17 μK
  3. Profile 全形: 零交叉 θ₀≈10°, 核心半寬 4.6°, 正環(旁瓣)
  4. R_TF fit 值 vs 2×R8
"""
import os, json
import numpy as np
import healpy as hp
from scipy.special import eval_legendre

PROJECT = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

A_IDCM = 134.2
COLD = (209.0, -57.0)
NSIDE = 512
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

T_pix_obs = -134.19
w_obs = -31.17
wl_417 = smhw_wl(np.radians(4.17), LMAX)

def tf_model(theta_deg, R_TF):
    """Thomas-Fermi inverted parabola"""
    return -A_IDCM * np.maximum(1 - (theta_deg/R_TF)**2, 0)

print(f"{'R_TF(°)':>8} {'T_pix(μK)':>10} {'w4.17(μK)':>10} {'ΔT_pix':>8} {'Δw':>7} {'θ₀(°)':>7}")
print("-" * 55)

results = []
for R_TF in np.arange(6.0, 12.01, 0.25):
    m = tf_model(ang, R_TF) * 1e-6
    m_sm = hp.smoothing(m, fwhm=np.radians(4.17))
    T_pix = float(m_sm[pix0]) * 1e6
    a = hp.map2alm(m, lmax=LMAX)
    aw = hp.almxfl(a, wl_417)
    wm = hp.alm2map(aw, nside=NSIDE, lmax=LMAX)
    alo = hp.almxfl(a, wl_417 * (np.arange(LMAX+1) < 3))
    wm -= hp.alm2map(alo, nside=NSIDE, lmax=LMAX)
    w = float(wm[pix0]) * 1e6
    # 零交叉
    m_sm_uK = m_sm * 1e6
    prof = m_sm_uK[np.argsort(ang)][:2000]
    ang_sorted = np.sort(ang)[:2000]
    cross = np.where(np.diff(np.sign(prof)) != 0)[0]
    theta0 = ang_sorted[cross[0]] if len(cross) else np.nan
    dT = abs(T_pix - T_pix_obs)
    dw = abs(w - w_obs)
    results.append({'R_TF': R_TF, 'T_pix': T_pix, 'w': w, 'theta0': theta0,
                    'dT': dT, 'dw': dw})
    if dT < 3 and dw < 3:
        print(f"{R_TF:>8.2f} {T_pix:>10.2f} {w:>10.2f} {dT:>8.2f} {dw:>7.2f} {theta0:>7.2f}")

# 最優
results.sort(key=lambda r: r['dT'] + 5*r['dw'])
best = results[0]
print(f"\n最優: R_TF = {best['R_TF']:.2f}°")
print(f"  T_pix = {best['T_pix']:.2f} (obs {T_pix_obs}, Δ={best['dT']:.2f})")
print(f"  w     = {best['w']:.2f} (obs {w_obs}, Δ={best['dw']:.2f})")
print(f"  零交叉 θ₀ = {best['theta0']:.2f}° (實測 ~10°)")
print(f"  結構預言 2×R8 = 8.34° vs fit {best['R_TF']:.2f}° (dev {abs(best['R_TF']-8.34)/8.34*100:.1f}%)")

# 精修
print("\n精修 (0.05° step):")
best2 = None
for R_TF in np.arange(max(6.0, best['R_TF']-0.6), min(12.0, best['R_TF']+0.6)+0.001, 0.05):
    m = tf_model(ang, R_TF) * 1e-6
    m_sm = hp.smoothing(m, fwhm=np.radians(4.17))
    T_pix = float(m_sm[pix0]) * 1e6
    a = hp.map2alm(m, lmax=LMAX)
    aw = hp.almxfl(a, wl_417)
    wm = hp.alm2map(aw, nside=NSIDE, lmax=LMAX)
    alo = hp.almxfl(a, wl_417 * (np.arange(LMAX+1) < 3))
    wm -= hp.alm2map(alo, nside=NSIDE, lmax=LMAX)
    w = float(wm[pix0]) * 1e6
    chi2 = ((T_pix - T_pix_obs)/0.5)**2 + ((w - w_obs)/0.3)**2
    if best2 is None or chi2 < best2['chi2']:
        best2 = {'R_TF': R_TF, 'T_pix': T_pix, 'w': w, 'chi2': chi2}

print(f"  ★ R_TF* = {best2['R_TF']:.2f}°")
print(f"    T_pix = {best2['T_pix']:.2f} (Δ={abs(best2['T_pix']-T_pix_obs):.2f} μK)")
print(f"    w     = {best2['w']:.2f} (Δ={abs(best2['w']-w_obs):.2f} μK)")
print(f"    χ² = {best2['chi2']:.2f}")
print(f"    vs 2×R8=8.34°: dev {abs(best2['R_TF']-8.34)/8.34*100:.1f}%")
print(f"    vs 內稟 FWHM=8.66°: dev {abs(best2['R_TF']-8.66)/8.66*100:.1f}%")

# profile 對比 (R_TF*)
m_best = tf_model(ang, best2['R_TF']) * 1e-6
m_sm_best = hp.smoothing(m_best, fwhm=np.radians(4.17)) * 1e6
print("\nProfile 對比 (smooth 後, 實測 vs TF 模型):")
print(f"  {'θ(°)':>6} {'實測(μK)':>9} {'TF(μK)':>9} {'差':>7}")
import json as _json
obs_prof = _json.load(open(os.path.join(OUTDIR, '03_profile_closure.json')))['profile']
obs_th = np.array([r['theta_mid'] for r in obs_prof])
obs_T = np.array([r['T_mean'] for r in obs_prof])
# TF profile at obs theta (interp from sorted ang)
order = np.argsort(ang)
ang_s = ang[order]
prof_s = m_sm_best[order]
tf_at = np.interp(obs_th, ang_s, prof_s)
for i in range(0, len(obs_th), 10):
    print(f"  {obs_th[i]:>6.2f} {obs_T[i]:>9.2f} {tf_at[i]:>9.2f} {obs_T[i]-tf_at[i]:>+7.2f}")

# 儲存
out = {
    'product': 'O45 closure-4: Thomas-Fermi condensate profile',
    'date': '2026-09-12',
    'model': 'δT(θ) = −A·max(1−(θ/R_TF)², 0), A=134.2 fixed',
    'physical_basis': 'W-field condensate (O39/O41), mean-field BEC Thomas-Fermi',
    'structural_prediction': 'R_TF = 2×R8 = 8.34°',
    'best': best2,
    'grid': results,
    'profile_comparison': {
        'theta': obs_th[::10].tolist(), 'observed': obs_T[::10].tolist(),
        'tf_model': tf_at[::10].tolist()},
}
with open(os.path.join(OUTDIR, '06_tf_closure.json'), 'w') as f:
    json.dump(out, f, indent=2)
print(f"\n儲存: {OUTDIR}/06_tf_closure.json")