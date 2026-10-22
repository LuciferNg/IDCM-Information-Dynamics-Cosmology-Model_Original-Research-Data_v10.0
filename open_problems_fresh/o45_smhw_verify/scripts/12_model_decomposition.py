#!/usr/bin/env python3
"""
O45 — 閉合攻堅 7: 多模型分解比較 (2026-09-12)
================================================
目標: 分辨「n*=12 物理起源」— 冷斑核心真係 super-Gaussian 頂帽,
      定係「高斯核心 + 背景/正環」嘅等效組合?

模型 (smooth 4.17° 前):
  G  : δT = −A·exp(−θ²/2σ²)                      [fit σ]
  G+C: δT = −A·exp(−θ²/2σ²) + C                   [fit σ, C]
  G+R: δT = −A·exp(−θ²/2σ²) + B·exp(−(θ−θ_r)²/2σ_r²)  [fit σ, B, θ_r, σ_r]
  SG : δT = −A·exp(−(θ/σ)ⁿ/2)                     [fit σ, n]  (對照)

通道: T_pix(4.17° smooth 中心) = −134.19, w(SMHW 4.17°) = −31.17,
      profile 全形 RMS (θ 0-25°, 0.5° bin)
"""
import os, json
import numpy as np
import healpy as hp
from scipy.special import eval_legendre
from scipy.optimize import least_squares

PROJECT = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

A_IDCM = 134.2
COLD = (209.0, -57.0)
NSIDE = 256          # 快: 786K pix, lmax=768 對 R=4.17° 已夠
LMAX = 3*NSIDE
SIGMA_SM2 = (4.17/2.355)**2

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
wl_417 = smhw_wl(np.radians(4.17), LMAX)

# 實測 profile (0.5° bin, 0-25°) from 10_ring_nature
prof_data = json.load(open(os.path.join(OUTDIR, '07_ring_nature.json')))
th_obs = np.array(prof_data['radial_profiles']['SMICA']['theta'])
T_obs = np.array(prof_data['radial_profiles']['SMICA']['T'])
m25 = th_obs < 25.0
th_obs, T_obs = th_obs[m25], T_obs[m25]

T_pix_obs, w_obs = -134.19, -31.17

def compute_channels(theta_map, T_model_K):
    """smooth + SMHW + profile"""
    m = T_model_K  # already K
    m_sm = hp.smoothing(m, fwhm=np.radians(4.17)) * 1e6
    T_pix = float(m_sm[pix0])
    a = hp.map2alm(m, lmax=LMAX)
    aw = hp.almxfl(a, wl_417)
    wm = hp.alm2map(aw, nside=NSIDE, lmax=LMAX)
    alo = hp.almxfl(a, wl_417 * (np.arange(LMAX+1) < 3))
    wm -= hp.alm2map(alo, nside=NSIDE, lmax=LMAX)
    w = float(wm[pix0]) * 1e6
    # profile: bin 0.5° like observed
    prof = np.interp(th_obs, np.sort(ang), m_sm[np.argsort(ang)])
    return T_pix, w, prof

models = {}

# --- G: 純高斯 ---
print("=== 模型 G: 純高斯 (fit σ) ===")
def cost_G(p):
    sigma = p[0]
    T = -A_IDCM * np.exp(-ang**2/(2*sigma**2)) * 1e-6
    T_pix, w, prof = compute_channels(ang, T)
    return np.array([(T_pix-T_pix_obs)/0.5, (w-w_obs)/0.3,
                     *((prof-T_obs)/5.0)])

r = least_squares(cost_G, [4.0], bounds=([1.0], [15.0]), max_nfev=40)
sigma_g = r.x[0]
T = -A_IDCM * np.exp(-ang**2/(2*sigma_g**2)) * 1e-6
T_pix, w, prof = compute_channels(ang, T)
chi2 = float(np.sum(r.fun**2))
models['G'] = {'sigma': float(sigma_g), 'T_pix': T_pix, 'w': w,
               'profile_rms': float(np.sqrt(np.mean((prof-T_obs)**2))), 'chi2': chi2}
print(f"  σ={sigma_g:.3f}°, T_pix={T_pix:.2f} (Δ={abs(T_pix-T_pix_obs):.2f}), "
      f"w={w:.2f} (Δ={abs(w-w_obs):.2f}), profile RMS={models['G']['profile_rms']:.2f} μK")

# --- G+C: 高斯 + offset ---
print("\n=== 模型 G+C: 高斯 + 背景 offset (fit σ, C) ===")
def cost_GC(p):
    sigma, C = p
    T = (-A_IDCM * np.exp(-ang**2/(2*sigma**2)) + C) * 1e-6
    T_pix, w, prof = compute_channels(ang, T)
    return np.array([(T_pix-T_pix_obs)/0.5, (w-w_obs)/0.3,
                     *((prof-T_obs)/5.0)])

r = least_squares(cost_GC, [5.0, 20.0], bounds=([1.0, -50.0], [15.0, 80.0]), max_nfev=60)
sigma_gc, C_gc = r.x
T = (-A_IDCM * np.exp(-ang**2/(2*sigma_gc**2)) + C_gc) * 1e-6
T_pix, w, prof = compute_channels(ang, T)
chi2 = float(np.sum(r.fun**2))
models['G+C'] = {'sigma': float(sigma_gc), 'C': float(C_gc), 'T_pix': T_pix, 'w': w,
                 'profile_rms': float(np.sqrt(np.mean((prof-T_obs)**2))), 'chi2': chi2}
print(f"  σ={sigma_gc:.3f}°, C={C_gc:+.2f} μK, T_pix={T_pix:.2f} (Δ={abs(T_pix-T_pix_obs):.2f}), "
      f"w={w:.2f} (Δ={abs(w-w_obs):.2f}), profile RMS={models['G+C']['profile_rms']:.2f} μK")

# --- G+R: 高斯 + 正環 ---
print("\n=== 模型 G+R: 高斯 + 正環高斯 (fit σ, B, θr, σr) ===")
def cost_GR(p):
    sigma, B, th_r, sr = p
    T = (-A_IDCM * np.exp(-ang**2/(2*sigma**2))
         + B * np.exp(-(ang-th_r)**2/(2*sr**2))) * 1e-6
    T_pix, w, prof = compute_channels(ang, T)
    return np.array([(T_pix-T_pix_obs)/0.5, (w-w_obs)/0.3,
                     *((prof-T_obs)/5.0)])

r = least_squares(cost_GR, [4.0, 38.0, 15.0, 5.0],
                  bounds=([1.0, 0, 5, 1.0], [15.0, 100, 25, 15.0]), max_nfev=80)
sigma_gr, B_gr, thr_gr, sr_gr = r.x
T = (-A_IDCM * np.exp(-ang**2/(2*sigma_gr**2))
     + B_gr * np.exp(-(ang-thr_gr)**2/(2*sr_gr**2))) * 1e-6
T_pix, w, prof = compute_channels(ang, T)
chi2 = float(np.sum(r.fun**2))
models['G+R'] = {'sigma': float(sigma_gr), 'B': float(B_gr), 'theta_r': float(thr_gr),
                 'sigma_r': float(sr_gr), 'T_pix': T_pix, 'w': w,
                 'profile_rms': float(np.sqrt(np.mean((prof-T_obs)**2))), 'chi2': chi2}
print(f"  σ={sigma_gr:.3f}°, B={B_gr:+.2f}, θr={thr_gr:.2f}°, σr={sr_gr:.2f}°")
print(f"  T_pix={T_pix:.2f} (Δ={abs(T_pix-T_pix_obs):.2f}), w={w:.2f} (Δ={abs(w-w_obs):.2f}), "
      f"profile RMS={models['G+R']['profile_rms']:.2f} μK")

# --- SG: super-Gaussian (對照) ---
print("\n=== 模型 SG: super-Gaussian (fit σ, n) 對照 ===")
def cost_SG(p):
    sigma, n = p
    T = -A_IDCM * np.exp(-(ang/sigma)**n/2) * 1e-6
    T_pix, w, prof = compute_channels(ang, T)
    return np.array([(T_pix-T_pix_obs)/0.5, (w-w_obs)/0.3,
                     *((prof-T_obs)/5.0)])

r = least_squares(cost_SG, [5.5, 10.0], bounds=([1.0, 2.0], [15.0, 20.0]), max_nfev=60)
sigma_sg, n_sg = r.x
T = -A_IDCM * np.exp(-(ang/sigma_sg)**n_sg/2) * 1e-6
T_pix, w, prof = compute_channels(ang, T)
chi2 = float(np.sum(r.fun**2))
models['SG'] = {'sigma': float(sigma_sg), 'n': float(n_sg), 'T_pix': T_pix, 'w': w,
                'profile_rms': float(np.sqrt(np.mean((prof-T_obs)**2))), 'chi2': chi2}
print(f"  σ={sigma_sg:.3f}°, n={n_sg:.2f}, T_pix={T_pix:.2f} (Δ={abs(T_pix-T_pix_obs):.2f}), "
      f"w={w:.2f} (Δ={abs(w-w_obs):.2f}), profile RMS={models['SG']['profile_rms']:.2f} μK")

# --- 總結 ---
print("\n=== 模型比較總結 ===")
print(f"{'模型':>6} {'參數':>16} {'ΔT_pix':>8} {'Δw':>7} {'profRMS':>8} {'χ²':>8}")
for name, d in models.items():
    print(f"{name:>6} {str(d.get('sigma',d.get('n','')))[:8]:>8} "
          f"{abs(d['T_pix']-T_pix_obs):>8.2f} {abs(d['w']-w_obs):>7.2f} "
          f"{d['profile_rms']:>8.2f} {d['chi2']:>8.1f}")

# 最佳模型 profile 對比
best_name = min(models, key=lambda k: models[k]['chi2'])
print(f"\n最佳: {best_name}")
best = models[best_name]
# 重算 best profile 輸出
print(f"  σ={best.get('sigma')}, n={best.get('n','-')}, C={best.get('C','-')}")

out = {
    'product': 'O45 closure-7: multi-model decomposition',
    'date': '2026-09-12',
    'observables': {'T_pix': T_pix_obs, 'w': w_obs},
    'models': models,
    'best': best_name,
    'conclusion': (
        "若 G+C 或 G+R 同 SG 一樣好 → n*=12 係高斯核心+背景嘅等效組合, "
        "頂帽非本質; 若 SG 明顯更好 → 冷斑核心真係頂帽狀"
    )
}
with open(os.path.join(OUTDIR, '09_model_decomposition.json'), 'w') as f:
    json.dump(out, f, indent=2)
print(f"\n儲存: {OUTDIR}/09_model_decomposition.json")