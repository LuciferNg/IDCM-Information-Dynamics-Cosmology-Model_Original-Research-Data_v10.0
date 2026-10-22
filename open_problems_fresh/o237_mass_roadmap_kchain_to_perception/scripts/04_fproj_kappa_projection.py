#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O237 U2 — R1 攻堅: κ_ijk=18·I9 張量投影迹 → F_proj (docs/01 R1 候選)
================================================================================
核心問題: F_proj(n) 係咪由 κ 張量 (κ_ijk = 18·δ_ijδ_jk, CSSG-v3/O206 docs/25 定理)
投影到 A5 模式扇區而生成?

方法 (盲測紀律, 禁 C_f 池匹配):
  §1 定義 κ̂ 張量投影 → F_proj^R1(n) = Tr(P_n κ̂) / dim(投影核?) 嘅最自然定義
     - 唔再用「fit C_f」揀定義; 用結構必然性 (κ 對角 = 18, 模式波函數 2sin(nπi/88))
  §2 對比: P_n 如果 = mode n 嘅 rank-1 投影 (經 CY3 9 維空間嵌入)
  §3 結果: 自動產生嘅值同 A5 C_f 比對 (唔調整參數)
  §4 判定: 命中 / 離群 → 誠實記錄
"""
import math
import numpy as np

PASS, FAIL = [], []
def ck(name, got, exp, tol=None):
    if tol is not None:
        ok = float(abs(got-exp)) < tol
    else:
        ok = bool(got == exp)
    (PASS if ok else FAIL).append(name)
    print(f"  {'OK ' if ok else 'FAIL'} {name} = {got}" + ("" if ok else f"  [exp {exp}]"))

print("="*88)
print("O237 U2 R1 — κ_ijk=18·I9 投影迹 → F_proj")
print("="*88)

M0 = 27.9009
MASS = {"e":0.510998950,"u":2.16,"d":4.67,"s":93.4,"mu":105.6583755,
        "c":1270.0,"tau":1776.86,"b":4180.0}
MODES = {"e":1,"u":2,"d":3,"s":4,"mu":5,"c":7,"tau":9,"b":11}
def gam(n): return 4*math.sin(math.pi*n/88)**2
CF = {p: MASS[p]/(M0*gam(MODES[p])) for p in MASS}

# ---------------------------------------------------------------- §1 κ̂ 定義
print("\n[1] κ 張量  κ_ijk = 18·δ_ijδ_jk  (i,j,k ∈ 1..9, CSSG-v3 定理)")
print("    對角 κ_iii = 18; 非對角 = 0.  → 'κ̂' 縮併為 9x9 對角矩陣 K = 18·I9")
K = 18*np.eye(9)
print(f"    K = 18·I₉; Tr(K) = {np.trace(K)} = 162 = 9×18")

# ---------------------------------------------------------------- §2 投影定義
print("\n[2] F_proj^R1(n) 最自然定義 (盲, 唔 fit):")
print("""    向量模式嵌入: e_i(n) = 2sin(n·πi/88)  (i=1..9, CY3 9 維)
    F_proj^R1(n) := (∑_i e_i(n))⁻¹ · Tr(K · P_n) / F5?  NO —— 唔准引額外常數。
    結構必然形式: κ 張量作用喺 mode 向量之「三次不變量」:
        I(n) = ∑_ijk κ_ijk e_i(n) e_j(n) e_k(n) = 18 ∑_i e_i(n)³
    (三次不變量係 CY3 三重相交 κ_ijk 對模式向量嘅最自然投影, 零新參數)""")
def e_i(n, i): return 2*math.sin(math.pi*n*i/88)
I3 = {}
for p, n in MODES.items():
    I3[p] = 18*sum(e_i(n,i)**3 for i in range(1,10))
    print(f"    I({p:>4}, n={n:>2}) = 18·Σe³ = {I3[p]:>12.5f}")

print("\n    比對: I3(n) vs C_f(n) (scale-free 比對 I3/C_f):")
ratios = {}
for p in MASS:
    ratios[p] = I3[p]/CF[p]
    print(f"      {p:>4}: I3 = {I3[p]:>12.5f}  C_f = {CF[p]:>10.4f}  I3/C_f = {ratios[p]:>8.4f}")
rvals = list(ratios.values())
spread = max(rvals)/min(rvals)
print(f"    I3/C_f 跨粒子 spread = {spread:.3f}×  (常數 = 結構, 非常數 = 冇結構)")
ck("R1 κ-三次不變量: I3/C_f 唔係常數 (spread >> 1.05)", spread > 1.05, True)

# ---------------------------------------------------------------- §3 有冇 mode 修正?
print("\n[3] 嘗試「κ 對角迹」家族 (唔 fit):  F^R1b(n) = Tr(K·P_n) 其中 P_n = 對角投影 (9 維)")
print("    若 P_n = diag(δ_{i,n}): F^R1b = κ_nnn = 18 對所有 n → 冇區分, 排除")
print("    若 P_n = diag(φ=9 正交基底 x3 投影): 即 Φ 目錄 —— 已 O206 第十輪精確 0/8, 排除")

# ---------------------------------------------------------------- §4 判定
print("\n" + "="*88)
print("[4] 判定")
print("="*88)
print(f"""  R1 兩個最自然 κ 投影定義:
  (a) κ-三次不變量 I(n) = 18·Σ e_i(n)³: I3/C_f spread = {spread:.3f}× ⟹ 冇單一標度 ⟹ 唔係結構
  (b) κ 對角迹: 恆等 18 ⟹ 冇 mode 區分 ⟹ 唔可以提供 8 個不同 C_f
  ⟹ R1 (κ_ijk=18·I9 直接投影) 喺最自然形式下【唔生成】A5 C_f.
  誠實結論: U2 經 4 個 blind 負結果 (γ 幂律/Z(n)/Φ×k/I3) 後, 仍無幾何生成規則;
  維持 🔴。剩餘候選 (未試): R2 φ=9 世代混合扇區 2-adic 正交接 C_f; R3 阻抗共振 A5 版;
  兩者都唔喺 O237 推 (docs/01 邊界: 本 O 盤點+裁定, 開新 der O 先可以推)。""")

print("\n" + "="*88)
print(f"U2 R1 round: {len(PASS)} PASS / {len(FAIL)} FAIL")
print("="*88)
print("PASS" if not FAIL else "FAIL")