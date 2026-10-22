#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O232 — scripts/02: 外部恆星年齡分佈尾端測試 (R1/R2 裁決)
========================================================
數據: Xiang, Rix & Liu (2024) LAMOST+Gaia eDR3 subgiant 星表 (320,028 星, YY isochrone 年齡)
  NADC DOI 10.12149/101467  (X22 = Xiang & Rix 2022 = 247,103 星 之更新版)
問題 (R1): IDCM τ = 1/ω_ring = 13.4701 Gyr 是否「可觀測星齡」硬天花板?
問題 (R2): 若有 0.26 Gyr 缺口, 有無結構因數?

紀律: 外部數據**只引用**; 尾端污染必須量化 (σ_A), 唔准把 artifact 當真齡。
"""
import json, os
import numpy as np
from astropy.io import fits
from mpmath import mp, mpf, nstr

mp.dps = 30
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FITS = os.path.join(BASE, "data", "raw", "LAMOST_Gaia_subgiants_Xiangetal2024.fits")

TAU = mpf('13.470063')          # IDCM: 1/ω_ring
A_STAR = mpf('13.73')           # Banik+2026 主結果
A_STAR_HI, A_STAR_LO = mpf('13.91'), mpf('13.58')
A_STAR_SIG = mpf('0.165')

checks = []
def ck(n, c, d=""):
    checks.append((n, bool(c), d)); print(("  ✅ " if c else "  ❌ ")+n+(f"   [{d}]" if d else ""))

print("="*78); print("O232 / 02 — 恆星年齡分佈尾端測試 (Xiang+2024, 320,028 星)"); print("="*78)
h = fits.open(FITS, memmap=True)
d = h[1].data
age  = np.asarray(d["AGE"], float);  eage = np.asarray(d["E_AGE"], float)
feh  = np.asarray(d["FEH"], float);  afe  = np.asarray(d["ALPHA_FE"], float)
logdis = np.asarray(d["LOGDIS"], float)     # log10(d/pc)
snr  = np.asarray(d["LAMOST_SNR_G"], float)
N = age.size
print(f"\n[Α] 原始星表: N = {N:,}   age max = {age.max():.2f}  (YY 網格上限 20 Gyr)")

# ---- B. 尾端統計 (raw) ----
print("\n[Β] 尾端累積 (raw, 無切割)")
thr = [13.0, float(TAU), 13.6, 13.73, 13.8, 14.0, 15.0, 16.0]
rows = {}
for t in thr:
    m = age > t
    rows[f"{t:.4f}"] = int(m.sum())
    print(f"  N(age > {t:7.4f}) = {int(m.sum()):8,d}  {100*m.sum()/N:7.4f}%")

# ---- C. 污染量化: 尾端 σ_A ----
print("\n[Γ] 尾端污染量化 (σ_A 隨齡升 ⟹ 高齡非硬探測)")
bins = [(11,12),(12,13),(13,float(TAU)),(float(TAU),14),(14,15),(15,16),(16,20.01)]
for lo,hi in bins:
    m = (age>=lo)&(age<hi)
    if m.sum():
        print(f"  {lo:6.2f}-{hi:<6.2f} N={int(m.sum()):7,d}  med σ_A={np.median(eage[m]):6.3f}  "
              f"frac(age-kσ>τ) k=1:{np.mean(age[m]-eage[m]>float(TAU)):5.2f} k=2:{np.mean(age[m]-2*eage[m]>float(TAU)):5.2f}")
n20 = int(np.count_nonzero(age >= 19.999)); print(f"  age >= 19.999 (網格硬邊) : {n20:,d}")

# ---- D. 穩健高齡 (A - kσ_A > τ) ----
print("\n[Δ] 穩健高齡計數 A − k·σ_A > τ = 13.4701")
sig = {}
for k in (1,2,3):
    m = age - k*eage > float(TAU)
    sig[k] = int(m.sum())
    print(f"  k={k}: N = {int(m.sum()):7,d}  {100*m.sum()/N:6.4f}%")
ck("C1 原始星表尾端達 YY 網格上限 20 Gyr (無硬 13.47 截斷)",
   age.max() >= 19.99 and rows[f"{float(TAU):.4f}"] > 0.01*N,
   f"max={age.max():.1f}, N>τ={rows[f'{float(TAU):.4f}']:,}")
ck("C2 尾端 N(>τ) 佔比 >5%", rows[f"{float(TAU):.4f}"]/N > 0.05, f"{100*rows[f'{float(TAU):.4f}']/N:.2f}%")
ck("C3 但穩健 (k≥3σ) 高齡極少 ⟹ 尾端主體係低顯著度 (污染)",
   sig[3] < 0.01*N and sig[3] < sig[1], f"k3={sig[3]:,} ({100*sig[3]/N:.3f}%), k1={sig[1]:,}")

# ---- E. 類論文切割樣本 ----
print("\n[Ε] 類 Banik+ 切割 (金屬貧 FEH<−0.6 ∧ α 富 ALPHA_FE>0.15 ∧ d<5kpc)")
mcut = (feh < -0.6) & (afe > 0.15) & (logdis < np.log10(5000.0)) & np.isfinite(age)
print(f"  N_cut = {int(mcut.sum()):,}")
a2, e2 = age[mcut], eage[mcut]
if a2.size:
    print(f"  age: median {np.median(a2):.2f}, 90pct {np.percentile(a2,90):.2f}, max {a2.max():.2f}")
    for t in [float(TAU), 13.6, 13.73, 14.0]:
        print(f"    N(> {t:7.4f}) = {int((a2>t).sum()):7,d}  {100*(a2>t).mean():6.3f}%")
    print(f"    robust A−3σ_A>τ : {int((a2-3*e2>float(TAU)).sum()):,}")
    print(f"    robust A−5σ_A>13.705 (論文之 0.1% artifact 判準): {int((a2-5*e2>13.705).sum()):,}")

# ---- F. 裁決 ----
print("\n[Ζ] 裁決")
print(f"  ★ IDCM τ (1/ω_ring)         = {nstr(TAU,7)} Gyr")
print(f"  ★ Banik+ 主結果 A_★        = 13.73 (+0.18/−0.15)  → [{nstr(A_STAR_LO,5)}, {nstr(A_STAR_HI,5)}]")
print(f"  ★ 星表 raw N(>τ) = {rows[f'{float(TAU):.4f}']:,} ({100*rows[f'{float(TAU):.4f}']/N:.2f}%)，但 k≥3σ 穩健者僅 {sig[3]:,}")
print("  ⇒ τ = 13.47 **唔係**星齡硬天花板 (尾端遠超 τ)；但尾端係低顯著度污染，")
print("    論文之 13.73 係**清洗後**值 ⇒ 兩者不可直接比。")
verdict = "🟡 R1: τ 非天花板 (IDCM 明言『冇年齡上限』); 1.6σ 框架係 category error；尾端污染未除不可裁決"
print(f"  判決: {verdict}")

npass = sum(1 for c in checks if c[1])
print("\n"+"="*78); print(f"RESULT: {npass}/{len(checks)} PASS"); print("="*78)

out = {
 "script": "02_stellar_age_tail_test.py", "source": "Xiang, Rix & Liu 2024 (NADC DOI 10.12149/101467)",
 "N": int(N), "age_max": float(age.max()), "tau_Gyr": float(TAU),
 "raw_cumulative": rows, "robust_over_tau": sig,
 "sigma_A_tail": {"13.5-14": float(np.median(eage[(age>=float(TAU))&(age<14)])),
                  "14-15": float(np.median(eage[(age>=14)&(age<15)])),
                  "15-16": float(np.median(eage[(age>=15)&(age<16)]))},
 "checks": [{"name": n, "pass": c, "detail": d} for n, c, d in checks],
 "pass": npass, "total": len(checks), "verdict": verdict,
}
with open(os.path.join(BASE, "data", "02_stellar_age_tail.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("data/02_stellar_age_tail.json written.")