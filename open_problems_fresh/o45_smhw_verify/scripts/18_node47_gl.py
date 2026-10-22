#!/usr/bin/env python3
"""O45 — GL 疇網絡驗證: node 47 三通道 GL 疇 fit (2026-09-12)
node 47: T_pix=−123.4 (第二大疇, 距冷斑 90.5°)
驗證: GL 疇壁模型係咪通用結構 (唔係冷斑專屬)
對比: 固定 ξ=0.663 (冷斑值) vs 自由 fit (R, ξ)
"""
import os, json
import numpy as np
import healpy as hp
from scipy.special import eval_legendre
from scipy.optimize import least_squares

A_IDCM = 134.2
XI_COLD = 0.663  # 冷斑 GL 相干長度
PROJECT = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
CACHE = os.path.join(PROJECT, 'open_problems_fresh/o5_catalog_compare/data/smooth_cache')
NSIDE, LMAX = 256, 768

data = json.load(open('data/02_smhw_full_data.json'))
gal = np.array([data['nodes'][f'node{i}']['gal'] for i in range(60)])
NODE47 = tuple(gal[47])
print(f"node 47 座標: l={NODE47[0]:.2f}°, b={NODE47[1]:.2f}°")

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
v0 = hp.ang2vec(NODE47[0], NODE47[1], lonlat=True)
v = hp.pix2vec(NSIDE, np.arange(npix))
ang = np.degrees(np.arccos(np.clip(v[0]*v0[0]+v[1]*v0[1]+v[2]*v0[2], -1, 1)))
pix0 = hp.ang2pix(NSIDE, NODE47[0], NODE47[1], lonlat=True)
wl_417 = smhw_wl(np.radians(4.17), LMAX)

# 實測 node 47: T_pix (smooth map 抽) + w (data/02 R4.17 係 w) + profile (自建)
m_sm_obs_full = hp.read_map(os.path.join(CACHE, 'smica2_smooth4.17.fits'))
m_sm_obs = hp.ud_grade(m_sm_obs_full, NSIDE)  # 統一 256 (pixel 0.23° << 4.17°)
T_pix_obs = float(m_sm_obs[pix0]) * 1e6
w_obs = float(data['nodes']['node47']['R4.17']['T'])  # μK (SMHW 係數)
print(f"node 47 實測: T_pix={T_pix_obs:.2f} μK, w(4.17°)={w_obs:.2f} μK")

# 抽 node 47 徑向 profile (0-25°)
prof_data = json.load(open('data/07_ring_nature.json'))
# 用相同 binning: 由 smooth map 抽
th_bins = np.arange(0, 25.01, 0.25)
th_obs = (th_bins[:-1] + th_bins[1:]) / 2
T_prof = np.empty(len(th_obs))
for k in range(len(th_obs)):
    lo, hi = th_bins[k], th_bins[k+1]
    # 環內像素
    m = (ang >= lo) & (ang < hi)
    T_prof[k] = np.mean(m_sm_obs[m]) * 1e6

def channels(T_model_K):
    m_sm = hp.smoothing(T_model_K, fwhm=np.radians(4.17)) * 1e6
    T_pix = float(m_sm[pix0])
    a = hp.map2alm(T_model_K, lmax=LMAX)
    aw = hp.almxfl(a, wl_417)
    wm = hp.alm2map(aw, nside=NSIDE, lmax=LMAX)
    alo = hp.almxfl(a, wl_417 * (np.arange(LMAX+1) < 3))
    wm -= hp.alm2map(alo, nside=NSIDE, lmax=LMAX)
    w = float(wm[pix0]) * 1e6
    prof = np.interp(th_obs, np.sort(ang), m_sm[np.argsort(ang)])
    return T_pix, w, prof

def gl_domain(theta, R, xi):
    arg = (R - theta) / xi
    w = np.tanh(np.clip(arg, -30, 30))
    return -A_IDCM * np.maximum(w, 0)**2 * 1e-6

# --- 固定 ξ=0.663 (冷斑值), fit R ---
print("\n=== node 47: GL 疇壁 (固定 ξ=0.663, fit R) ===")
def cost_fix(p):
    T = gl_domain(ang, p[0], XI_COLD)
    T_pix, w, prof = channels(T)
    return np.array([(T_pix-T_pix_obs)/0.5, (w-w_obs)/0.3, *((prof-T_prof)/5.0)])

r = least_squares(cost_fix, [2.0], bounds=([0.5], [8]), max_nfev=60)
R_f = r.x[0]
T = gl_domain(ang, R_f, XI_COLD)
T_pix, w, prof = channels(T)
chi2 = float(np.sum(r.fun**2))
print(f"  R={R_f:.3f}° (ξ 固定 0.663)")
print(f"  T_pix={T_pix:.2f} (Δ={abs(T_pix-T_pix_obs):.2f}), w={w:.2f} (Δ={abs(w-w_obs):.2f}), "
      f"profRMS={np.sqrt(np.mean((prof-T_prof)**2)):.2f}, χ²={chi2:.1f}")

# --- 自由 fit (R, ξ) ---
print("\n=== node 47: GL 疇壁 (自由 fit R, ξ) ===")
def cost_free(p):
    T = gl_domain(ang, p[0], p[1])
    T_pix, w, prof = channels(T)
    return np.array([(T_pix-T_pix_obs)/0.5, (w-w_obs)/0.3, *((prof-T_prof)/5.0)])

r2 = least_squares(cost_free, [2.0, 0.7], bounds=([0.5, 0.2], [8, 3]), max_nfev=80)
R2, xi2 = r2.x
T2 = gl_domain(ang, R2, xi2)
T_pix2, w2, prof2 = channels(T2)
chi2_2 = float(np.sum(r2.fun**2))
print(f"  R={R2:.3f}°, ξ={xi2:.3f}°")
print(f"  T_pix={T_pix2:.2f} (Δ={abs(T_pix2-T_pix_obs):.2f}), w={w2:.2f} (Δ={abs(w2-w_obs):.2f}), "
      f"profRMS={np.sqrt(np.mean((prof2-T_prof)**2)):.2f}, χ²={chi2_2:.1f}")
print(f"  ξ vs 冷斑 0.663: dev {abs(xi2-0.663)/0.663*100:.1f}%")

# --- 對照: 純高斯 (fit σ) ---
print("\n=== node 47: 純高斯 (fit σ) 對照 ===")
def cost_g(p):
    T = -A_IDCM * np.exp(-(ang/p[0])**2/2) * 1e-6
    T_pix, w, prof = channels(T)
    return np.array([(T_pix-T_pix_obs)/0.5, (w-w_obs)/0.3, *((prof-T_prof)/5.0)])

r3 = least_squares(cost_g, [3.0], bounds=([0.5], [10]), max_nfev=60)
sg = r3.x[0]
T3 = -A_IDCM * np.exp(-(ang/sg)**2/2) * 1e-6
T_pix3, w3, prof3 = channels(T3)
chi2_3 = float(np.sum(r3.fun**2))
print(f"  σ={sg:.3f}°")
print(f"  T_pix={T_pix3:.2f} (Δ={abs(T_pix3-T_pix_obs):.2f}), w={w3:.2f} (Δ={abs(w3-w_obs):.2f}), "
      f"profRMS={np.sqrt(np.mean((prof3-T_prof)**2)):.2f}, χ²={chi2_3:.1f}")

print("\n=== node 47 模型比較 ===")
print(f"  {'模型':<22} {'χ²':>8}")
print(f"  {'GL 固定 ξ':<22} {chi2:>8.1f}")
print(f"  {'GL 自由':<22} {chi2_2:>8.1f}")
print(f"  {'純高斯':<22} {chi2_3:>8.1f}")

json.dump({'node47': {'gal': list(NODE47), 'T_pix_obs': T_pix_obs, 'w_obs': w_obs,
                      'gl_fixed': {'R': float(R_f), 'chi2': chi2},
                      'gl_free': {'R': float(R2), 'xi': float(xi2), 'chi2': chi2_2},
                      'gauss': {'sigma': float(sg), 'chi2': chi2_3}}},
          open('data/17_node47_gl.json', 'w'), indent=2)
print("\n儲存: data/17_node47_gl.json")
