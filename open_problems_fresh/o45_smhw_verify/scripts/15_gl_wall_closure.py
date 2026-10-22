#!/usr/bin/env python3
"""
O45 — 閉合攻堅 9: Ginzburg-Landau 凝聚疇壁 (2026-09-12)
==========================================================
物理鏈:
  O39 (取代 O37 舊暗能量版本): V(W) = −μ²|W|² + λ|W|⁴, μ²=2, λ=2/123, ⟨W⟩²=61.5
  真空能 (最新) = ⟨W⟩²/⟨W⟩²_max = 61.5/90 = 41/60 = 0.68333
  GL 靜態疇壁解: W(r) = W₀·tanh((R−r)/ξ), ξ = 相干長度 = 1/√(2μ²) (IDCM 單位)
  O41: 溫度 = 凝聚密度 (δT ∝ −|W|²), 冷斑 = 相位滑移疇

模型: δT(r) = −A·max(0, tanh((R−r)/ξ))²   (fit R 疇半徑, ξ 壁厚)
結構預言: ξ = 1/√(2μ²) = 1/2 (IDCM 單位) ↔ 角度換算
"""
import os, json
import numpy as np
import healpy as hp
from scipy.special import eval_legendre
from scipy.optimize import least_squares

A_IDCM = 134.2
COLD = (209.0, -57.0)
NSIDE, LMAX = 256, 768

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

prof_data = json.load(open('data/07_ring_nature.json'))
th_obs = np.array(prof_data['radial_profiles']['SMICA']['theta'])
T_obs = np.array(prof_data['radial_profiles']['SMICA']['T'])
m25 = th_obs < 25.0
th_obs, T_obs = th_obs[m25], T_obs[m25]
T_pix_obs, w_obs = -134.19, -31.17

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
    """GL 凝聚疇: δT = −A·max(0,tanh((R−θ)/ξ))²"""
    arg = (R - theta) / xi
    w = np.tanh(np.clip(arg, -30, 30))
    return -A_IDCM * np.maximum(w, 0)**2 * 1e-6

# --- GL 疇壁 (fit R, ξ) ---
print("=== GL 凝聚疇壁 δT = −A·max(0,tanh((R−θ)/ξ))², fit (R, ξ) ===")
def cost_gl(p):
    R, xi = p
    T = gl_domain(ang, R, xi)
    T_pix, w, prof = channels(T)
    return np.array([(T_pix-T_pix_obs)/0.5, (w-w_obs)/0.3, *((prof-T_obs)/5.0)])

r = least_squares(cost_gl, [5.5, 1.5], bounds=([3, 0.3], [10, 5]), max_nfev=80)
R_gl, xi_gl = r.x
T = gl_domain(ang, R_gl, xi_gl)
T_pix, w, prof = channels(T)
chi2 = float(np.sum(r.fun**2))
print(f"  R={R_gl:.3f}°, ξ={xi_gl:.3f}°")
print(f"  T_pix={T_pix:.2f} (Δ={abs(T_pix-T_pix_obs):.2f}), w={w:.2f} (Δ={abs(w-w_obs):.2f}), "
      f"profRMS={np.sqrt(np.mean((prof-T_obs)**2)):.2f}, χ²={chi2:.1f}")
print(f"  (對照: SG+R χ²=104, SG χ²=868, top-hat χ²=983)")
print(f"  結構: ξ×√(2μ²)×? — μ²=2 → ξ_GL(單位) = 1/√(2×2) = 0.5")
print(f"  角度換算: 88-site 鏈, 360/88={360/88:.3f}°/unit → ξ_pred={0.5*360/88:.3f}°")
print(f"          或 2×ξ={2*xi_gl:.3f}° vs ξ_pred 1.64-2.05°")

# --- GL + 正環 ---
print("\n=== GL 疇壁 + 正環 (R, ξ, B, θr, σr) ===")
def cost_glR(p):
    R, xi, B, th_r, sr = p
    T = gl_domain(ang, R, xi) + B*np.exp(-(ang-th_r)**2/(2*sr**2)) * 1e-6
    T_pix, w, prof = channels(T)
    return np.array([(T_pix-T_pix_obs)/0.5, (w-w_obs)/0.3, *((prof-T_obs)/5.0)])

r2 = least_squares(cost_glR, [5.5, 1.5, 44, 16, 3], bounds=([3, 0.3, 0, 5, 1], [10, 5, 100, 25, 15]), max_nfev=120)
R2, xi2, B2, thr2, sr2 = r2.x
T2 = gl_domain(ang, R2, xi2) + B2*np.exp(-(ang-thr2)**2/(2*sr2**2)) * 1e-6
T_pix2, w2, prof2 = channels(T2)
chi2_2 = float(np.sum(r2.fun**2))
print(f"  R={R2:.3f}°, ξ={xi2:.3f}°, B={B2:+.1f} @ {thr2:.2f}°, σr={sr2:.2f}°")
print(f"  T_pix={T_pix2:.2f} (Δ={abs(T_pix2-T_pix_obs):.2f}), w={w2:.2f} (Δ={abs(w2-w_obs):.2f}), "
      f"profRMS={np.sqrt(np.mean((prof2-T_obs)**2)):.2f}, χ²={chi2_2:.1f}")
print(f"  (對照: SG+R χ²=104, profRMS=6.6)")

# --- 總結 ---
print("\n=== 終極模型比較 ===")
print(f"  {'模型':<16} {'參數':<3} {'ΔT_pix':>7} {'Δw':>6} {'profRMS':>8} {'χ²':>8}")
print(f"  {'SG+R':<16} {'5':<3} {'1.9':>7} {'0.3':>6} {'6.6':>8} {'104':>8}")
print(f"  {'GL 疇壁':<16} {'2':<3} {abs(T_pix-T_pix_obs):>7.2f} {abs(w-w_obs):>6.2f} {np.sqrt(np.mean((prof-T_obs)**2)):>8.2f} {chi2:>8.1f}")
print(f"  {'GL+正環':<16} {'5':<3} {abs(T_pix2-T_pix_obs):>7.2f} {abs(w2-w_obs):>6.2f} {np.sqrt(np.mean((prof2-T_obs)**2)):>8.2f} {chi2_2:>8.1f}")

json.dump({'gl_wall': {'R': float(R_gl), 'xi': float(xi_gl), 'T_pix': T_pix, 'w': w,
                       'profRMS': float(np.sqrt(np.mean((prof-T_obs)**2))), 'chi2': float(chi2)},
           'gl_wall_R': {'R': float(R2), 'xi': float(xi2), 'B': float(B2), 'theta_r': float(thr2),
                         'sigma_r': float(sr2), 'T_pix': T_pix2, 'w': w2,
                         'profRMS': float(np.sqrt(np.mean((prof2-T_obs)**2))), 'chi2': float(chi2_2)}},
          open('data/15_gl_wall_closure.json', 'w'), indent=2)
print("\n儲存: data/15_gl_wall_closure.json")
