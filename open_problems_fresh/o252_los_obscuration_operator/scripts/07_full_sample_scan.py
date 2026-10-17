#!/usr/bin/env python3
"""
O252 — Script 07: 全樣本 dip 掃描 + 統計閉合 (2026-10-17)
==========================================================
結構預言 (scripts 04-06 已凍結, 零參數):
  P1 窗中心 |v| = V_max/√2 = 289.76 km/s (hop=4 凝聚重心窗)
  P2 窗寬 σ = FSR ℓ=3 quantum = 167.23 km/s
  P3 深度 τ_w = ⟨hop⟩ = 4 → depth = 0.9817
  P4 帶方向: 藍側 (v<0) 被遮蔽
掃描: 全部 obj fits (A/C/E/F/G/I/J/K) × Hα/Hβ, M4 bounded fit (同 record 24
      pipeline: broad × dip), 抽取 dip 位置/depth/σ
判定:
  [S1] dip 位置統計: 全部 dip |v| 對預言窗 ±(289.76±167.23) 命中率 vs MC null
  [S2] dip 方向統計: 藍側比例 (P-Cygni 凝聚層喺視線近側)
  [S3] depth vs 預言 0.9817 (A 已有 0.979; 其他源若有高 SNR dip 對照)
  誠實: 每個 dip fit 要報 ΔAIC (M4 vs M0) — 唔顯著嘅 dip 唔算數
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

# 源目錄 (record 24 用過嘅)
SOURCES = [
    ("A",  'objA_g395m.fits', 5.0405),
    ("A",  'objA_g395h.fits', 5.0405),
    ("C",  'objC_g395m.fits', 4.1325),
    ("C",  'objC_g395h.fits', 4.1325),
    ("E",  'objE_g395m.fits', 6.6847),
    ("F",  'objF_g395m.fits', 4.4779),
    ("G",  'objG_g395m.fits', 3.6493),
    ("I",  'objI_g395m.fits', 3.4304),
    ("J",  'objJ_g395m.fits', 5.8683),
    ("J",  'objJ_g395h.fits', 5.8683),
    ("K",  'objK_g395m.fits', 5.2394),
]

# z 值: 揾 record 24/paper 用嘅 (冇就 None → 跳過)
ZS = {"A": 5.0405, "E": 6.6847}
# C/F/G/I/J/K 嘅 z 從邊度? record 21 有峰位 → 至少 G/C 有. 用 fits 檔 header 試
def get_z(path):
    try:
        h = fits.open(path)
        for kw in ['Z','REDSHIFT','Z_SRC','ZDEC']:
            if kw in h[0].header:
                v = float(h[0].header[kw])
                if 0.5 < v < 12: return v
        if 'REDSHIFT' in h[1].columns.names if len(h)>1 else False:
            pass
    except Exception:
        pass
    return None

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

def m0(x, a, s, x0, c0):
    return a*np.exp(-0.5*((x-x0)/s)**2) + c0
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
    except Exception:
        return None, None

print("="*84)
print("O252/07 — 全樣本 dip 掃描 + 統計閉合")
print("="*84)
print(f"預言: |v|=289.76±167.23 (P1+P2), depth=0.9817 (P3), 藍側 (P4)")

results = []
for src, fn, z_hint in SOURCES:
    path = os.path.join(FITS_DIR, fn)
    if not os.path.exists(path): continue
    z = z_hint or get_z(path)
    if z is None:
        print(f"  [{src} {fn}] — z 未知, 跳過"); continue
    for lname in ['Hα','Hβ']:
        r = load_win(fn, z, lname, w=0.05)
        if r is None: continue
        x, y, cobs = r
        # M0 (baseline)
        p00 = [np.percentile(y,90), 250.0, 0.0, np.median(y)]
        b0 = ([-np.inf, 20, -800, -np.inf], [np.inf, 1500, 800, np.inf])
        p0m, aic0 = fit_b(m0, x, y, p00, b0)
        # M4 (broad × dip)
        p04 = [np.percentile(y,90), 250.0, 0.0, 0.4, 180.0, 0.0, np.median(y)]
        b4 = ([-np.inf, 50, -800, 0.0, 30, -800, -np.inf],
               [np.inf, 1500, 800, 1.5, 400, 800, np.inf])
        p4m, aic4 = fit_b(m4_fix, x, y, p04, b4)
        if p4m is None or aic0 is None: continue
        dAIC = aic0 - aic4    # 正 = M4 更好
        a_b, s_b, x0, a_a, s_a, dv, c0 = p4m
        sig = (dAIC > 4)      # ΔAIC>4 先算顯著 dip (保守)
        hit = bool((abs(abs(float(dv))-v_abs) <= sig3) if sig else False)
        results.append({"src": src, "line": lname, "dv": float(dv),
                        "depth": float(a_a), "sig_dip": float(s_a),
                        "dAIC": float(dAIC), "sig": bool(sig),
                        "hit_pred": hit})
        print(f"  [{src} {fn.split('.')[0]} {lname}] dv={dv:+7.1f} depth={a_a:.2f} "
              f"σ={s_a:5.0f} ΔAIC={dAIC:+7.1f} {'✓dip' if sig else '  —'} "
              f"{'HIT' if hit else ''}")

# ---------- 統計 ----------
sig_dips = [r for r in results if r["sig"]]
hits = [r for r in sig_dips if r["hit_pred"]]
print(f"\n顯著 dip: {len(sig_dips)}, 預言窗命中 (|v|∈289.76±167.23): {len(hits)}")
if sig_dips:
    hit_rate = len(hits)/len(sig_dips)
    print(f"命中率 {hit_rate:.2%}")
    # 方向
    n_blue = sum(1 for r in sig_dips if r["dv"] < 0)
    print(f"藍側比例: {n_blue}/{len(sig_dips)}")
    # MC null: dip 位置均匀 ±1500, 命中率 (窗 334.5/3000)
    p_single = 2*sig3/3000.0
    from math import comb
    n_trials = len(sig_dips)
    pmf = lambda k: comb(n_trials,k)*(p_single**k)*((1-p_single)**(n_trials-k))
    p_ge = sum(pmf(k) for k in range(len(hits), n_trials+1))
    ck("S1 命中數 vs MC null", p_ge < 0.05,
       f"{len(hits)}/{n_trials} hits, p(≥{len(hits)} by chance)={p_ge:.4f} (p_single={p_single:.4f})")
    ck("S2 藍側方向", n_blue/len(sig_dips) >= 0.6, f"{n_blue}/{len(sig_dips)} 藍側")

data = {"pred": {"v_abs": v_abs, "sigma": sig3, "depth_pred": 1-math.exp(-4)},
        "results": results,
        "summary": {"n_dips": len(sig_dips), "n_hits": len(hits),
                    "n_blue": n_blue if sig_dips else None,
                    "p_ge_by_chance": p_ge if sig_dips else None},
        "note": "顯著 dip = ΔAIC(M4−M0)>4; 命中窗 = |dv|∈[122.5,457.0]",
        "checks": [{"name": n, "pass": p, "detail": d} for n,p,d in LOG]}
with open(f"{OUT}/07_full_sample_scan.json","w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

np_ok = sum(1 for _,p,_ in LOG if p)
print(f"\n結果: {np_ok}/{len(LOG)} PASS → data/07_full_sample_scan.json")