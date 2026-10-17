#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P11 攻堅 — 藍/紅側 flux 比統計: 吸收 channel 無模型檢驗 (2026-10-17)
=====================================================================
record 21 後續: 吸收 channel 預言「藍弱 (R<1)」。M1 fit 有多自由度問題
(A Hβ 峰位錯亂), 改用零自由度代理:
  R_side = ∫_{v∈[-w,0]} I dv / ∫_{v∈[0,+w]} I dv   (Hα 窗內)
  R_side < 1 → 藍側弱 (吸收/bulk outflow 方向)
  R_side ≈ 1 → 對稱

樣本: 9 光源 (Rusakov A/C/E/F/G/I/J/K + 有 G395H 嘅測兩次)
輸出: data/28_side_ratio_stats.json
"""
import json, numpy as np, os
from astropy.io import fits

FITS_DIR = os.environ.get('P11_FITS_DIR', '/home/wsl/.hermes/cache/scratch/p11_data')
C_KM = 2.99792458e5
LAM_HA = 0.65628

SAMPLE = [
    ("A_JADES-GN-68797_H", "objA_g395h.fits", 5.0405, 2700),
    ("A_JADES-GN-68797_M", "objA_g395m.fits", 5.0405, 1000),
    ("C_JADES-GN-73488_H", "objC_g395h.fits", 4.1325, 2700),
    ("C_JADES-GN-73488_M", "objC_g395m.fits", 4.1325, 1000),
    ("E_RUBIES-EGS-49140",  "objE_g395m.fits", 6.6852, 1000),
    ("F_CEERS-EGS-1244",    "objF_g395m.fits", 4.4779, 1000),
    ("G_RUBIES-EGS-58237",  "objG_g395m.fits", 3.6493, 1000),
    ("I_JADES-GN-53501",    "objI_g395m.fits", 3.4304, 1000),
    ("J_JADES-GN-38147",    "objJ_g395m.fits", 5.8683, 1000),
    ("K_RUBIES-EGS-50052",  "objK_g395m.fits", 5.2394, 1000),
]

def compute(fn, z):
    h = fits.open(os.path.join(FITS_DIR, fn))
    d = h[1].data
    w, f = d['wave'], d['flux']
    ok = ~np.isnan(f)
    cobs = LAM_HA*(1+z)
    mcont = ok & (((w>=cobs-0.10)&(w<=cobs-0.06)) | ((w>=cobs+0.06)&(w<=cobs+0.10)))
    if mcont.sum() < 8:
        return None
    A = np.polyfit(w[mcont], f[mcont], 1)
    m = ok & (w>=cobs-0.03) & (w<=cobs+0.03)
    wl, fl = w[m], f[m]-np.polyval(A, w[m])
    if len(wl) < 10:
        return None
    # 積分藍/紅側 (v<0 / v>0)
    v = C_KM*(wl-cobs)/cobs
    mblue = v < 0
    mred = v > 0
    I_blue = np.trapezoid(fl[mblue], v[mblue])
    I_red = np.trapezoid(fl[mred], v[mred])
    if I_red <= 0:
        return None
    R = I_blue/I_red
    # 峰位 (最強點)
    ipeak = np.argmax(fl)
    vpeak = v[ipeak]
    return {"R_side": R, "I_blue": I_blue, "I_red": I_red,
            "vpeak": vpeak, "N": len(wl), "line_max": float(np.max(fl))}

out = {"date": "2026-10-17", "results": {}}
print(f"{'光源':<22} {'R':>4} {'I_藍':>9} {'I_紅':>9} {'峰位Δv':>7} {'z':>7} {'R~':>4}")
print("="*76)
n_blueweak = n_total = 0
for name, fn, z, R in SAMPLE:
    r = compute(fn, z)
    if r is None:
        print(f"{name}: cont fail")
        continue
    out["results"][name] = r
    n_total += 1
    if r["R_side"] < 1:
        n_blueweak += 1
    tag = "藍弱" if r["R_side"] < 1 else ("藍強" if r["R_side"] > 1 else "對稱")
    print(f"{name:<22} {r['R_side']:5.3f} {r['I_blue']:9.1f} {r['I_red']:9.1f} "
          f"{r['vpeak']:+7.0f} {z:7.4f} {tag}")

print("="*76)
frac = n_blueweak/n_total if n_total else 0
p_blueweak = sum((n_blueweak+0.5*k) for k in [0])  # 粗略
# binomial p: P(≥n_blueweak 藍弱 | 對稱假設 p=0.5)
from math import comb
pval = sum(comb(n_total, k)*(0.5**n_total) for k in range(n_blueweak, n_total+1))
print(f"藍弱比例: {n_blueweak}/{n_total} = {frac:.2f}")
print(f"二項檢驗 (H0: p=0.5 對稱): P(X≥{n_blueweak}) = {pval:.4f}")
print(f"⟹ {'顯著藍弱' if pval < 0.05 else ('邊際' if pval < 0.10 else '唔顯著')}: 吸收/bulk 預言")
out["summary"] = {"n_total": n_total, "n_blueweak": n_blueweak,
                  "frac_blueweak": frac, "binomial_p": pval}

# 同 IDCM hop 定量對比: 預言 R_e ≈ e^{-Δτ}, Δτ ∝ z?
print("\nhop 定量對比 (record 21): 預言 R<1, 弱化隨 τ_c (光深) 增加")
print("樣本冇 τ 量度 — 用 z 做代理: 更高 z → 更多凝聚層? 檢查 R 同 z 相關性")
zs = [v["z"] for v in []]
# 簡單相關
rs = []; zvals = []
for name, r in out["results"].items():
    # 需要對應 z — 由 SAMPLE 找
    for nm2, fn, z2, R2 in SAMPLE:
        if nm2 == name:
            rs.append(r["R_side"]); zvals.append(z2); break
if len(rs) >= 2:
    corr = np.corrcoef(rs, zvals)[0, 1]
    print(f"corr(R_side, z) = {corr:+.3f} ({len(rs)} 點)")
    out["summary"]["corr_R_z"] = float(corr)

with open('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p11_little_red_dots/data/28_side_ratio_stats.json', 'w') as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False)
print("\n[寫入] data/28_side_ratio_stats.json")