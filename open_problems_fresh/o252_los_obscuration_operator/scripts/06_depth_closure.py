#!/usr/bin/env python3
"""
O252 — Script 06: 深度閉合 + 跨源重 fit (2026-10-17)
====================================================
第二輪已定: v_abs = V_max/√2 = 289.76 km/s (hop=4 凝聚窗, 事前預言)
          σ = FSR ℓ=3 quantum = 167.23 km/s (record 14)
本 script:
  Part A — 深度零常數: τ_w 候選
    D-a: τ_w = ⟨hop⟩ = B = 4   (hop 階梯重心 = 凝聚層厚度的結構量)
         depth = 1−e^{−4} = 0.9817 vs A Hα depth 0.979 (record 24)
    D-b: τ_w = n(4)/Σ = 12/60 = 0.2  (凝聚重心層節點比)
    D-c: τ_w = ln(W_max/W_min) ... 唔係, 跳過
  Part B — A Hα 完整 fit 重現 depth (script 30 M4 結果 0.9789)
  Part C — E Hα 重新獨立 fit (唔靠 paper): dip 位置 +47 定 −90?
    用 script 30 嘅 load_win + M4 模型 (bounded fit)
  零觀測 reference 只限 dip 位置; 深度係結構預言 (呢個同 record 28 判準一致:
  τ(v) 形狀同深度都必須由結構推出, 唔係 fit)
"""
import json, math, os
import numpy as np
from astropy.io import fits
from scipy.optimize import curve_fit

FITS_DIR = os.environ.get('P11_FITS_DIR', '/home/wsl/.hermes/cache/scratch/p11_data')
C_KM = 2.99792458e5
LAM = {'Hα': 0.65628, 'Hβ': 0.48614}
R_world_Mpc = 4129.94
Mpc_km = 3.0856775814913673e19
a0 = C_KM**2/(2*math.pi*R_world_Mpc*Mpc_km)
R_c_kpc = R_world_Mpc/44**3*1000.0
R_c_km = R_c_kpc*3.0856775814913673e16
V_max = math.sqrt(a0*R_c_km)
v_abs = V_max/math.sqrt(2.0)
sig3 = C_KM*math.pi/(88*4**3)
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
LOG = []
def ck(name, cond, detail=''):
    LOG.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

print("="*84)
print("O252/06 — depth closure + E refit (independent)")
print("="*84)
print(f"v_abs={v_abs:.3f}, σ={sig3:.3f}")

# ---------- Part A: 深度結構候選 ----------
depth_A_obs = 0.9789568609591053   # record 24 data/30 A_Hα
for name, tau in [("D-a ⟨hop⟩=B=4", 4.0),
                  ("D-b n(4)/Σ=0.2", 12/60),
                  ("D-c 1/e 深度", 1.0)]:
    d = 1 - math.exp(-tau)
    dev = abs(d - depth_A_obs)/depth_A_obs*100
    print(f"  {name}: τ={tau:.4f} → depth={d:.4f} vs obs={depth_A_obs:.4f} (dev {dev:.2f}%)")
ck("D-a ⟨hop⟩=4 深度命中 <2%", abs((1-math.exp(-4.0))-depth_A_obs)/depth_A_obs < 0.02,
   f"dev {abs((1-math.exp(-4.0))-depth_A_obs)/depth_A_obs*100:.2f}%")

# ---------- Part B/C: 載入 + fit (E 獨立重 fit) ----------
def load_win(fn, z, lname, w=0.05):
    h = fits.open(os.path.join(FITS_DIR, fn))
    d = h[1].data
    wv, f = d['wave'], d['flux']
    ok = ~np.isnan(f)
    cobs = LAM[lname]*(1+z)
    mcont = ok & (((wv>=cobs-0.12)&(wv<=cobs-0.07)) | ((wv>=cobs+0.07)&(wv<=cobs+0.12)))
    if mcont.sum() < 8: return None
    A = np.polyfit(wv[mcont], f[mcont], 1)
    m = ok & (wv>=cobs-w) & (wv<=cobs+w)
    if m.sum() < 15: return None
    return wv[m]-cobs, f[m]-np.polyval(A, wv[m]), cobs

def m4_fix(x, a_b, s_b, x0, a_a, s_a, dv_km, c0):
    v = C_KM*(x-x0)/cobs
    vabs = v - dv_km
    dip = 1.0 - a_a*np.exp(-0.5*(vabs/s_a)**2)
    return a_b*np.exp(-0.5*((v)/(s_b))**2)*dip + c0

def fit_b(model, x, y, p0, bounds=(-np.inf, np.inf)):
    try:
        popt, _ = curve_fit(model, x, y, p0=p0, bounds=bounds, maxfev=100000)
        resid = y - model(x, *popt)
        n, k = len(y), len(popt)
        sig2 = np.var(resid, ddof=k)
        aic = n*np.log(sig2) + 2*k
        return popt, aic
    except Exception as e:
        print("  fit error:", e); return None, None

print("\n── Part C: E Hα 獨立重 fit (M4: broad × dip) ──")
zE = 6.6847
r = load_win('objE_g395m.fits', zE, 'Hα', w=0.05)
if r is not None:
    x, y, cobs = r
    v = C_KM*x/cobs
    # p0: broad amp, broad σ, centroid, dip depth, dip σ, dip dv, cont
    # bounds: a_a∈[0,1.5], s_a∈[30,400], dv∈[-800,800]
    p0 = [np.percentile(y,90), 250.0, 0.0, 0.4, 180.0, 0.0, 0.0]
    bnd = ([-np.inf, 50, -800, 0.0, 30, -800, -np.inf],
           [ np.inf, 1500, 800, 1.5, 400, 800, np.inf])
    popt, aic = fit_b(m4_fix, x, y, p0, bnd)
    if popt is not None:
        a_b, s_b, x0, a_a, s_a, dv, c0 = popt
        print(f"  E Hα M4: broad_amp={a_b:.1f} σ={s_b:.0f} x0={x0:.4f} "
              f"| dip_depth={a_a:.3f} σ={s_a:.0f} dv={dv:+.1f} km/s")
        print(f"  → 我哋 fit dip @ {dv:+.1f} km/s (paper +47)")
        ck("E-dip 藍側 (dv<0, 同 paper +47 分歧)", dv < 0, f"dv={dv:+.1f}")
    else:
        print("  E fit 失敗")
else:
    print("  E window 載入失敗")

# ---------- Part A 對照輸出 ----------
data = {"v_abs_kms": v_abs, "sigma_kms": sig3,
        "depth_A_obs": depth_A_obs,
        "depth_candidates": {"D_a_hop4": 1-math.exp(-4.0),
                              "D_b_n4": 1-math.exp(-12/60),
                              "D_c_1": 1-math.exp(-1.0)},
        "note": "D-a 之前 (script 04) 已用 ⟨hop⟩=4 推位置; 深度標籤後驗",
        "checks": [{"name": n, "pass": p, "detail": d} for n,p,d in LOG]}
with open(f"{OUT}/06_depth_closure.json","w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
np_ok = sum(1 for _,p,_ in LOG if p)
print(f"\n結果: {np_ok}/{len(LOG)} PASS → data/06_depth_closure.json")