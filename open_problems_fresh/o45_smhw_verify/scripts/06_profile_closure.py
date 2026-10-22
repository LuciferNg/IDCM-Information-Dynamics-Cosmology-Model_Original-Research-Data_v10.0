#!/usr/bin/env python3
"""
O45 — 閉合攻堅 1: 冷斑非高斯輪廓 + 1.4× 偏差來源 (2026-09-12)
===============================================================
步驟:
  1. 抽實測 4.17°-smooth 冷斑徑向剖面 T(θ) (0-20°, 0.25° bin)
  2. Fit 修正高斯: T(θ) = -A·exp(-θ²/2σ_c²) 對 核心區 (θ<2σ)
     + 測量有效半寬 (50% 回升點)
  3. 對比純高斯預言 (σ=3.68° 內稟) vs 實測剖面 → 量化核心 sharpness
  4. 用實測 profile 直接入 SMHW harmonic pipeline → 預言 7 尺度係數
     → 對比實測 SMHW 係數 (閉合 1.4× 偏差來源)

關鍵: 實測 profile 係零參數模型 (直接由數據嚟, 唔 fit A)
"""
import os, json, time
import numpy as np
import healpy as hp
from scipy.special import eval_legendre
from scipy.optimize import curve_fit

PROJECT = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
SMOOTH = os.path.join(PROJECT, 'open_problems_fresh/o5_catalog_compare/data/smooth_cache/smica2_smooth4.17.fits')
OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

A_IDCM = 134.2
COLD = (209.0, -57.0)   # Gal l, b

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

# ---------- 1. 實測徑向剖面 ----------
print("抽實測 4.17°-smooth 徑向剖面...")
m = hp.read_map(SMOOTH)  # 已 4.17° smooth + dipole removed
nside = hp.get_nside(m)
npix = hp.nside2npix(nside)
print(f"  cache map: nside={nside}, mean={m.mean():.2e}")

v0 = hp.ang2vec(COLD[0], COLD[1], lonlat=True)
v = hp.pix2vec(nside, np.arange(npix))
ang = np.degrees(np.arccos(np.clip(v[0]*v0[0] + v[1]*v0[1] + v[2]*v0[2], -1, 1)))
T_muK = m * 1e6

# 0.25° bin, 0-20°
bins = np.arange(0, 20.001, 0.25)
profile = []
for i in range(len(bins)-1):
    lo, hi = bins[i], bins[i+1]
    mask = (ang >= lo) & (ang < hi)
    if mask.sum() >= 5:
        profile.append({
            'theta_lo': float(lo), 'theta_hi': float(hi),
            'theta_mid': float((lo+hi)/2),
            'n_pix': int(mask.sum()),
            'T_mean': float(np.mean(T_muK[mask])),
            'T_median': float(np.median(T_muK[mask])),
        })

# 中心像素值 (直接採樣)
pix0 = hp.ang2pix(nside, COLD[0], COLD[1], lonlat=True)
T_center = float(T_muK[pix0])
print(f"  中心 T = {T_center:.2f} μK (A_IDCM={A_IDCM})")

# ---------- 2. 修正高斯 fit (核心區) ----------
print("\n修正高斯 fit (A 固定 134.2, 只 fit σ_c):")
# T(θ) = -A·exp(-θ²/2σ_c²)
th = np.array([p['theta_mid'] for p in profile])
Tb = np.array([p['T_mean'] for p in profile])

def gauss(theta, sigma):
    return -A_IDCM * np.exp(-theta**2 / (2*sigma**2))

# fit 核心區: θ < 8° (profile 明顯非零區)
core_mask = th < 8.0
try:
    popt, pcov = curve_fit(gauss, th[core_mask], Tb[core_mask],
                           p0=[3.0], bounds=([0.5], [15.0]))
    sigma_c = popt[0]
    sigma_c_err = np.sqrt(pcov[0][0])
    print(f"  σ_c = {sigma_c:.3f}° ± {sigma_c_err:.3f}° (A=134.2 固定, θ<8°)")
except Exception as e:
    print(f"  fit failed: {e}")
    sigma_c = np.nan

# 有效半寬: profile 回升到 -A/2 嘅 θ
T_half = -A_IDCM/2
interp_th = np.interp(T_half, Tb[::-1], th[::-1])  # 搵 T=T_half 嘅 θ
print(f"  50% 回升點 θ_1/2 = {interp_th:.2f}°")
sigma_eff = interp_th / np.sqrt(2*np.log(2))  # 高斯: T(θ)=A/2 → θ=σ√(2ln2)
print(f"  等效 σ_eff (由 θ_1/2) = {sigma_eff:.3f}°")
print(f"  → FWHM_eff = {2.355*sigma_eff:.2f}°")

# 對比純內稟高斯 (σ=3.68°)
sigma_int = 8.66/2.355
pred_int = gauss(th, sigma_int)
print(f"\n對比純內稟高斯 (σ={sigma_int:.2f}°):")
print(f"  {'θ(°)':>6} {'實測(μK)':>10} {'高斯(μK)':>10} {'實測/高斯':>10}")
for i in range(0, len(th), 8):
    print(f"  {th[i]:>6.2f} {Tb[i]:>10.2f} {pred_int[i]:>10.2f} {Tb[i]/pred_int[i]:>10.3f}")

# ---------- 3. 實測 profile 入 SMHW (零參數預言) ----------
print("\n實測 profile 入 SMHW harmonic pipeline (零參數)...")
# 構建「profile map」: 喺 nside=1024 上, 每個 pixel 用 profile T(θ)
nside2 = 1024
npix2 = hp.nside2npix(nside2)
v2 = hp.pix2vec(nside2, np.arange(npix2))
ang2 = np.degrees(np.arccos(np.clip(v2[0]*v0[0]+v2[1]*v0[1]+v2[2]*v0[2], -1, 1)))
# 線性插值 profile → 每個 pixel 嘅模型 T
model_map = np.interp(ang2, np.append([0], th), np.append([T_center], Tb)) * 1e-6  # K
print(f"  model map: nside={nside2}, center={model_map[np.argmin(ang2)]*1e6:.2f} μK")

lmax = 3*nside2
a_model = hp.map2alm(model_map, lmax=lmax)
pix0_2 = hp.ang2pix(nside2, COLD[0], COLD[1], lonlat=True)

scales = [1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0]
obs = json.load(open(os.path.join(OUTDIR, '01_smhw_results.json')))

print(f"\n{'R(°)':>6} {'預言(μK)':>10} {'實測(μK)':>10} {'比率':>8} {'偏差':>8}")
print("-" * 46)
smhw_predict = {}
for R in scales:
    wl = smhw_wl(np.radians(R), lmax)
    alm_w = hp.almxfl(a_model, wl)
    wm = hp.alm2map(alm_w, nside=nside2, lmax=lmax)
    alm_lo = hp.almxfl(a_model, wl * (np.arange(lmax+1) < 3))
    wm -= hp.alm2map(alm_lo, nside=nside2, lmax=lmax)
    pred = float(wm[pix0_2]) * 1e6
    o = obs['smhw'][str(R)]['T_wavelet']
    ratio = o/pred if pred != 0 else 0
    dev = abs(ratio-1)*100
    smhw_predict[str(R)] = {'predicted': pred, 'observed': o, 'ratio': ratio}
    print(f"{R:>6.2f} {pred:>10.2f} {o:>10.2f} {ratio:>8.3f} {dev:>7.2f}%")

# ---------- 4. 儲存 ----------
out = {
    'product': 'O45 closure-1: cold spot profile + 1.4x source',
    'date': '2026-09-12',
    'A_IDCM': A_IDCM,
    'cold_spot_gal': COLD,
    'profile': profile,
    'center_T': T_center,
    'gauss_fit': {'sigma_c': float(sigma_c) if not np.isnan(sigma_c) else None,
                  'sigma_int_compare': float(sigma_int),
                  'half_recovery_theta': float(interp_th),
                  'sigma_eff_from_half': float(sigma_eff),
                  'FWHM_eff': float(2.355*sigma_eff)},
    'smhw_profile_prediction': smhw_predict,
    'conclusion_1_4x': (
        "實測 profile (零參數) 入 SMHW 後, 預言 vs 實測比率應 ≈1 若偏差純粹來自輪廓形狀; "
        "殘餘偏差反映 smoothing 核同 SMHW 兩步 filter 嘅組合效應"
    )
}
with open(os.path.join(OUTDIR, '03_profile_closure.json'), 'w') as f:
    json.dump(out, f, indent=2)
print(f"\n儲存: {OUTDIR}/03_profile_closure.json")