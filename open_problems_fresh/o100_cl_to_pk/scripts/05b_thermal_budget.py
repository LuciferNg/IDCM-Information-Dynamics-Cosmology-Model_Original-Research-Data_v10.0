#!/usr/bin/env python3
"""
O100-B (續): 熱態歸一化 — Σ1/γ 世界/觀察者 budget
=================================================
O83 熱 propagator: ⟨φ²⟩_T → 1/(βγ_n) 高溫極限 → 方差 ∝ 1/γ_n。
σ_8 歸一化嘅結構候選: 世界鏈 (even/44-site) vs 觀察者鏈 (odd) 嘅 Σ1/γ。

核心問題: 我而家嘅 σ8 用「觀察到嘅 9 條峰」做歸一化。若果世界嘅完整
material variance 係 Σ1/γ 全鏈 (44 模式), 而觀察只係 subset (9 峰),
個修正因子係咪就係補埋嘅 17%?
"""
import numpy as np
from math import comb

k = np.arange(1, 89)
gam88 = 4*np.sin(np.pi*k/176)**2
odd  = k % 2 == 1
even = k % 2 == 0

inv_odd  = (1/gam88)[odd].sum()
inv_even = (1/gam88)[even].sum()
print("== Σ1/γ (熱態方差 budget) ==")
print(f"Σ1/γ_odd  (觀察者) = {inv_odd:.4f}")
print(f"Σ1/γ_even (世界)   = {inv_even:.4f}")
print(f"Σ1/γ_even/Σ1/γ_odd = {inv_even/inv_odd:.6f}")
print(f"Σ1/γ_odd/Σ1/γ_even = {inv_odd/inv_even:.6f}")

n = np.arange(1, 45)
gam44 = 4*np.sin(np.pi*n/88)**2
print(f"\nΣ1/γ(44-site) = {(1/gam44).sum():.4f}")
print(f"44/odd = {(1/gam44).sum()/inv_odd:.6f}  44/even = {(1/gam44).sum()/inv_even:.6f}")

# 觀察峰階梯 n_m (半整數諧和嘅整數分子): ℓ_m = 44n_m → γ(n_m) 用 88-site?
M = 33; F6, F8 = 8, 21
n_m = [M - comb(9-m, 2) if m != 5 else M - F6 for m in range(1, 10)]
print(f"\n== 9 峰階梯 n_m = {n_m} ==")
# 峰對應嘅鏈模式索引: 用 44-site γ(n) 定 88-site?
g44_nm = 4*np.sin(np.pi*np.array(n_m)/88)**2   # n_m ≤ 33 有效 (44-site)
g88_nm = 4*np.sin(np.pi*np.array(n_m)/176)**2
print(f"Σ1/γ(9峰, 44-site idx) = {(1/g44_nm).sum():.4f}")
print(f"Σ1/γ(9峰, 88-site idx) = {(1/g88_nm).sum():.4f}")
print(f"世界/9峰 (44-site): Σ1/γ_44 / Σ1/γ_9peak = {(1/gam44).sum()/(1/g44_nm).sum():.6f}")
print(f"世界/9峰 (88-site): Σ1/γ_even / Σ1/γ_9peak = {inv_even/(1/g88_nm).sum():.6f}")

# 需要嘅修正: σ8² ×1.172 (0.748→0.81)
need = (0.81/0.7482)**2
print(f"\n== 需要 ×{need:.4f} 於 σ8² ==")
print(f"(90/88)³ = {(90/88)**3:.4f}   ← r³ 候選")
print(f"世界/9峰(44-site) = {(1/gam44).sum()/(1/g44_nm).sum():.4f}   ← 熱態候選")

# 高溫極限完整方差 vs 我用的 (2ℓ+1)/4π: 峰數 9 vs 44 模式
print(f"峰數比: 44 模式 / 9 峰 = {44/9:.4f}  (但 9 峰每條帶 (2ℓ+1) 度簡併)")