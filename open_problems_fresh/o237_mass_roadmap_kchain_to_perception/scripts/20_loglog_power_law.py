#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O237 U2 — log-log 冪律檢查: corr(C_f,γ)=+0.95 嘅結構含義
================================================================================
scripts/19 T4 意外發現: corr(C_f, γ_mode) = +0.9464 (唔係正交!).
原因: C_f = m/(M₀γ); assignment 按質量排序; mode 越大質量越大.
若 log C_f vs log γ 係直線 → 冪律 C_f = a·γ^p. 斜率 p = 結構數?

歷史: docs/04 判「γ 冪律負 (94%)」— 但當時可能冇 log-log fit 或 C_f 定義唔同
      (O206 第十輪 A5 主 scheme 後 C_f 係對應 A5 mode). 本 script 重新檢驗.
"""
import math
import numpy as np

def g(n): return 4 * math.sin(math.pi * n / 88) ** 2

M0 = 27.9009
MASS = {"e":0.510998950,"u":2.16,"d":4.67,"s":93.4,"mu":105.6583755,
        "c":1270.0,"tau":1776.86,"b":4180.0}
MODES = {"e":1,"u":2,"d":3,"s":4,"mu":5,"c":7,"tau":9,"b":11}
ORDER = ["e","u","d","s","mu","c","tau","b"]

CF = {p: MASS[p]/(M0*g(n)) for p, n in MODES.items()}

print("="*92)
print("O237 U2 — log-log 冪律檢查: corr(C_f,γ) = +0.95 嘅結構")
print("="*92)

print(f"\n{'p':>4} {'n':>3} {'γ_n':>10} {'C_f':>10} {'log γ':>10} {'log C_f':>10}")
lg = []; lc = []
for p in ORDER:
    n = MODES[p]
    gg = g(n)
    cf = CF[p]
    lg.append(math.log(gg)); lc.append(math.log(cf))
    print(f"{p:>4} {n:>3} {gg:>10.6f} {cf:>10.4f} {math.log(gg):>10.4f} {math.log(cf):>10.4f}")

# 線性回歸 log C_f = log a + p·log γ
lg = np.array(lg); lc = np.array(lc)
p_slope, intercept = np.polyfit(lg, lc, 1)
resid = lc - (p_slope*lg + intercept)
r2 = 1 - np.sum(resid**2)/np.sum((lc - lc.mean())**2)
corr = np.corrcoef(lg, lc)[0,1]

print(f"\nlog-log fit: log C_f = {p_slope:.4f}·log γ + {intercept:.4f}")
print(f"  r² = {r2:.6f}, corr = {corr:+.6f}, max resid = {np.max(np.abs(resid)):.4f}")
print(f"  ⟹ C_f ∝ γ^{p_slope:.4f}")

# 斜率候選結構數:
cands = {"0.5 (√γ)":0.5, "1.0 (γ)":1.0, "1.5":1.5, "2.0 (γ²)":2.0,
         "φ/2=0.809":(1+math.sqrt(5))/4, "3/4=0.75":0.75, "4/3":4/3,
         "1/(2-φ)=?":1/(2-(1+math.sqrt(5))/2)}
print("\n斜率候選:")
for name, val in cands.items():
    print(f"  {name:>12} = {val:.6f}   dev = {(p_slope-val)/val*100:+.2f}%")

# C_f 直接 vs γ: 之前 docs/04「γ 冪律 94%」係咩意思?
print("""
[重要] docs/04 §二 記錄「γ 冪律」負: m = M₀γ·(γ冪律?) 唔可以用 C_f 冪律 fit 全部質量.
      但 O206/本 script 嘅 C_f = m/(M₀γ) 係商定義 — 若 C_f ∝ γ^p, 則 m ∝ M₀γ^{1+p}!
      即係質量 m_f ∝ γ^{1+p} — 一個純譜冪律商!
""")
pp = 1 + p_slope
print(f"  若 C_f ∝ γ^{p_slope:.3f} ⟹ m_f ∝ M₀·γ^{pp:.3f}")
cands2 = {"1.5 (γ^{3/2})":1.5, "2.0 (γ²)":2.0, "2.5":2.5, "3.0":3.0,
          "1+φ/2=1.809":1+(1+math.sqrt(5))/4, "5/3":5/3, "7/4":7/4}
for name, val in cands2.items():
    print(f"  {name:>14} = {val:.6f}   dev = {(pp-val)/val*100:+.2f}%")

# 但: 呢個係 8 點 fit — 過度擬合風險! 睇逐點殘差
print("\n逐點 C_f/γ^p 比:")
for p in ORDER:
    n = MODES[p]
    ratio = CF[p] / g(n)**p_slope
    print(f"  {p:>4}: C_f/γ^{p_slope:.3f} = {ratio:.4f}")
ratios = [CF[p]/g(MODES[p])**p_slope for p in ORDER]
spread = max(ratios)/min(ratios)
print(f"  ratio spread = {spread:.3f}×  (1.0 = 完美冪律)")
print(f"""
[判定]: spread {spread:.2f}× {'≪ 常數(結構冪律!)' if spread < 2 else '> 2× = 唔係單一冪律'}

注意: C_f 嘅 log-log 相關高可能只係因為 mass 範圍跨度大 (0.5→4180, 8e3×)
      而 assignment 已按質量排序 — 任何單調函數都有高 corr. 但冪律指數若接近
      結構數 (如 p=1.5 → m ∝ γ^{5/2}) 先有意思。
""")