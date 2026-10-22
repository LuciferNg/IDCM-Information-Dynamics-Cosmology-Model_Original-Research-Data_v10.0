#!/usr/bin/env python3
"""
O45 — 閉合攻堅 8: sine-Gordon 孤子凝聚 (sech²) 三通道閉合 (2026-09-12)
======================================================================
物理: O7 調律者 = sine-Gordon; 冷斑 = 相位滑移 π (寫入事件);
      凝聚能量密度 ε(x) ∝ φ'² = sech²(x/λ) — 頂帽狀孤子輪廓

模型: δT(θ) = −A·sech²(θ/λ)   (A=134.2 固定, fit λ)
結構預言: λ = R8×5/4 = 4.17×1.25 = 5.213°  (5=F₅, 4=L₃; 或 26.17/F₅=5.234)

驗證: T_pix + w(SMHW) + profile 全形, 對比 SG+R (χ²=104)
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

prof_data = json.load(open(os.path.join(OUTDIR, '07_ring_nature.json')))
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

# --- sech² 純模型 ---
print("=== sech² (1 參數 λ) ===")
def cost_sech(p):
    lam = p[0]
    T = -A_IDCM * (1/np.cosh(ang/lam))**2 * 1e-6
    T_pix, w, prof = channels(T)
    return np.array([(T_pix-T_pix_obs)/0.5, (w-w_obs)/0.3, *((prof-T_obs)/5.0)])

r = least_squares(cost_sech, [5.2], bounds=([3.0], [8.0]), max_nfev=40)
lam = r.x[0]
T = -A_IDCM * (1/np.cosh(ang/lam))**2 * 1e-6
T_pix, w, prof = channels(T)
chi2 = float(np.sum(r.fun**2))
prof_rms = float(np.sqrt(np.mean((prof-T_obs)**2)))
print(f"  λ={lam:.3f}°, T_pix={T_pix:.2f} (Δ={abs(T_pix-T_pix_obs):.2f}), "
      f"w={w:.2f} (Δ={abs(w-w_obs):.2f}), profRMS={prof_rms:.2f} μK, χ²={chi2:.1f}")
print(f"  結構預言: R8×5/4={4.17*5/4:.3f} (dev {abs(lam-4.17*5/4)/(4.17*5/4)*100:.2f}%)")
print(f"           26.17/F₅={26.17/5:.3f} (dev {abs(lam-26.17/5)/(26.17/5)*100:.2f}%)")
print(f"           2F₇/F₅={2*13/5:.3f} (dev {abs(lam-2*13/5)/(2*13/5)*100:.2f}%)")

# --- sech² + 背景正環 (2 參數核心 λ + 正環) ---
print("\n=== sech² + 正環 (λ + B, θr, σr) ===")
def cost_sechR(p):
    lam, B, th_r, sr = p
    T = (-A_IDCM * (1/np.cosh(ang/lam))**2
         + B * np.exp(-(ang-th_r)**2/(2*sr**2))) * 1e-6
    T_pix, w, prof = channels(T)
    return np.array([(T_pix-T_pix_obs)/0.5, (w-w_obs)/0.3, *((prof-T_obs)/5.0)])

r2 = least_squares(cost_sechR, [5.2, 44, 16, 3], bounds=([3, 0, 5, 1], [8, 100, 25, 15]), max_nfev=80)
lam2, B2, thr2, sr2 = r2.x
T2 = (-A_IDCM * (1/np.cosh(ang/lam2))**2
      + B2 * np.exp(-(ang-thr2)**2/(2*sr2**2))) * 1e-6
T_pix2, w2, prof2 = channels(T2)
chi2_2 = float(np.sum(r2.fun**2))
prof_rms2 = float(np.sqrt(np.mean((prof2-T_obs)**2)))
print(f"  λ={lam2:.3f}°, B={B2:+.1f} μK @ θr={thr2:.2f}°, σr={sr2:.2f}°")
print(f"  T_pix={T_pix2:.2f} (Δ={abs(T_pix2-T_pix_obs):.2f}), w={w2:.2f} (Δ={abs(w2-w_obs):.2f}), "
      f"profRMS={prof_rms2:.2f} μK, χ²={chi2_2:.1f}")
print(f"  (對照 SG+R: χ²=104, profRMS=6.6)")

# --- 總結 ---
print("\n=== 模型比較 ===")
print(f"  {'模型':<14} {'參數':<6} {'ΔT_pix':>7} {'Δw':>6} {'profRMS':>8} {'χ²':>8}")
print(f"  {'SG (n=10.9)':<14} {'2':<6} {'1.5':>7} {'1.2':>6} {'20.5':>8} {'868':>8}")
print(f"  {'SG+R':<14} {'5':<6} {'1.9':>7} {'0.3':>6} {'6.6':>8} {'104':>8}")
print(f"  {'sech²':<14} {'1':<6} {abs(T_pix-T_pix_obs):>7.1f} {abs(w-w_obs):>6.2f} {prof_rms:>8.2f} {chi2:>8.1f}")
print(f"  {'sech²+R':<14} {'4':<6} {abs(T_pix2-T_pix_obs):>7.1f} {abs(w2-w_obs):>6.2f} {prof_rms2:>8.2f} {chi2_2:>8.1f}")

out = {
    'product': 'O45 closure-8: sine-Gordon soliton (sech²)',
    'date': '2026-09-12',
    'physical_basis': 'O7 tuner sine-Gordon, cold spot = phase slip π, ε ∝ φ\'² = sech²(x/λ)',
    'sech2': {'lambda': float(lam), 'T_pix': T_pix, 'w': w, 'profRMS': prof_rms, 'chi2': chi2,
              'structural': {'R8x5/4': 4.17*5/4, 'dhop/F5': 26.17/5, '2F7/F5': 2*13/5}},
    'sech2_R': {'lambda': float(lam2), 'B': float(B2), 'theta_r': float(thr2),
                'sigma_r': float(sr2), 'T_pix': T_pix2, 'w': w2, 'profRMS': prof_rms2, 'chi2': chi2_2},
    'comparison': {'SG_chi2': 868, 'SG_R_chi2': 104},
}
with open(os.path.join(OUTDIR, '11_sech2_closure.json'), 'w') as f:
    json.dump(out, f, indent=2)
print(f"\n儲存: {OUTDIR}/11_sech2_closure.json")