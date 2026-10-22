#!/usr/bin/env python3
"""
02_tau_structural_derivation_v2.py
====================================
IDCM 結構推導：CMB 光深 τ — 修正版

第一版問題：v_g(n) = cos(πn/88) 喺 n=1..44 全部 ≥0（因為 πn/88 ∈ [0, π/2]）
所以「反向傳播 mode」概念唔成立，需要重新推導。

新推導：τ = κ × (1 - ε) = 0.05284
物理意義：κ = 最小作用量單位（quartic coupling）
         1 - ε = 管道容量中非耗散嘅比例
         τ = 散射概率 = κ × (1 - ε)

IDCM v10.0 — 共震點宇宙學
"""

import sys
import math
import json

# ================================================================
# IDCM Core Constants
# ================================================================
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
EPS = PHI_INV / 4            # 0.1545084972
KAPPA = 1 / 16               # 0.0625
BETA = PHI_INV / 2           # 0.3090169944
N_d = 44                     # K_Chain dimension
M = 33                       # K_Tree depth
B = 4                        # MERA branching factor
h11 = 36                     # CY₃ h¹¹
h21 = 98                     # CY₃ h²¹
CY3 = h11 + h21              # 134

# ================================================================
# K_Chain Mode Parameters
# ================================================================
def gamma_n(n):
    """K_Chain eigenvalue γ_n = 4 sin²(πn/88)"""
    return 4 * (math.sin(math.pi * n / 88) ** 2)

def v_g(n):
    """Group velocity v_g(n) = cos(πn/88)
    NOTE: For n=1..44, v_g ≥ 0 (cos(πn/88) ∈ [cos(π/2), cos(π/88)] = [0, ~1])
    All 44 modes are forward-propagating!"""
    return math.cos(math.pi * n / 88)

# ================================================================
# τ 結構公式推導
# ================================================================
print("=" * 72)
print("IDCM 再電離問題 — 路徑 1：τ 結構公式推導（修正版）")
print("=" * 72)

# 確認 v_g 範圍
print(f"\nK_Chain v_g 驗證：")
print(f"  n=1:  v_g = cos({math.pi/88:.6f}) = {v_g(1):.6f}")
print(f"  n=22: v_g = cos({22*math.pi/88:.6f}) = {v_g(22):.6f}")
print(f"  n=44: v_g = cos({44*math.pi/88:.6f}) = {v_g(44):.6f}")
print(f"  → All 44 modes have v_g ≥ 0 (forward-propagating)")

# 外部參考 (Planck 2018 Table 2, TT,TE,EE+lowE, arXiv:1807.06209)
TAU_PLANCK = 0.0544
TAU_PLANCK_ERR = 0.0073

# ================================================================
# 公式 A：τ = κ × (1 - ε)
# ================================================================
tau_A = KAPPA * (1 - EPS)
err_A = abs(tau_A / TAU_PLANCK - 1) * 100

print(f"\n{'─' * 72}")
print(f"公式 A：τ = κ × (1 - ε)")
print(f"{'─' * 72}")
print(f"  κ = {KAPPA} (quartic coupling, 最小作用量單位)")
print(f"  1-ε = {1-EPS:.6f} (管道非耗散比例)")
print(f"  τ = {KAPPA} × {1-EPS:.6f} = {tau_A:.6f}")
print(f"  Planck 2018: τ = {TAU_PLANCK} ± {TAU_PLANCK_ERR}")
print(f"  誤差: {err_A:.2f}%")
print(f"  σ偏差: {abs(tau_A - TAU_PLANCK)/TAU_PLANCK_ERR:.2f}σ")
if err_A < 10:
    print(f"  ✅ 吻合！")
elif err_A < 30:
    print(f"  🟡 大致吻合")
else:
    print(f"  ❌ 唔吻合")

# 物理意義
print(f"\n  物理意義：")
print(f"  κ = 1/16 = W-field 四階耦合常數 (最小作用量)")
print(f"  1-ε = 1 - φ⁻¹/4 = 管道容量中用於投影嘅比例")
print(f"  τ = κ × (1-ε) = 光子散射概率")
print(f"  即係：CMB 光子有 τ 概率喺投影過程中與自由電子散射")

# ================================================================
# 公式 B：τ = κ × (1 - ε) × (1 + ε²)  （ε² 階修正）
# ================================================================
tau_B = KAPPA * (1 - EPS) * (1 + EPS**2)
err_B = abs(tau_B / TAU_PLANCK - 1) * 100
print(f"\n{'─' * 72}")
print(f"公式 B：τ = κ × (1 - ε) × (1 + ε²)")
print(f"{'─' * 72}")
print(f"  τ = {tau_B:.6f}")
print(f"  Planck: {TAU_PLANCK}")
print(f"  誤差: {err_B:.2f}%")
print(f"  σ偏差: {abs(tau_B - TAU_PLANCK)/TAU_PLANCK_ERR:.2f}σ")

# ================================================================
# 公式 C：τ = κ × (1 - ε) × (1 + ε² - ε³)  （ε²+ε³ 修正）
# ================================================================
tau_C = KAPPA * (1 - EPS) * (1 + EPS**2 - EPS**3)
err_C = abs(tau_C / TAU_PLANCK - 1) * 100
print(f"\n{'─' * 72}")
print(f"公式 C：τ = κ × (1 - ε) × (1 + ε² - ε³)")
print(f"{'─' * 72}")
print(f"  τ = {tau_C:.6f}")
print(f"  Planck: {TAU_PLANCK}")
print(f"  誤差: {err_C:.2f}%")
print(f"  σ偏差: {abs(tau_C - TAU_PLANCK)/TAU_PLANCK_ERR:.2f}σ")

# ================================================================
# 公式 D：τ = κ × (1 - ε) × (h11/CY₃)  （CY₃ 投影修正）
# ================================================================
tau_D = KAPPA * (1 - EPS) * (h11 / CY3)
err_D = abs(tau_D / TAU_PLANCK - 1) * 100
print(f"\n{'─' * 72}")
print(f"公式 D：τ = κ × (1 - ε) × (h¹¹/CY₃)")
print(f"{'─' * 72}")
print(f"  τ = {tau_D:.6f}")
print(f"  Planck: {TAU_PLANCK}")
print(f"  誤差: {err_D:.2f}%")

# ================================================================
# 公式 E：τ = 1/B^M + κ × (1 - ε)  （K_Tree 深度修正）
# ================================================================
tau_E = (1 / B**M) + KAPPA * (1 - EPS)
err_E = abs(tau_E / TAU_PLANCK - 1) * 100
print(f"\n{'─' * 72}")
print(f"公式 E：τ = 1/B^M + κ × (1 - ε)")
print(f"{'─' * 72}")
print(f"  1/B^M = 1/{B}^{M} ≈ {1/B**M:.2e}（可忽略）")
print(f"  τ = {tau_E:.6f}")
print(f"  Planck: {TAU_PLANCK}")
print(f"  誤差: {err_E:.2f}%")

# ================================================================
# 總結
# ================================================================
print(f"\n{'=' * 72}")
print("總結")
print("=" * 72)

results = {
    'A (基本)': {'value': tau_A, 'err_pct': err_A, 'sigma': abs(tau_A - TAU_PLANCK)/TAU_PLANCK_ERR},
    'B (ε²修正)': {'value': tau_B, 'err_pct': err_B, 'sigma': abs(tau_B - TAU_PLANCK)/TAU_PLANCK_ERR},
    'C (ε²-ε³)': {'value': tau_C, 'err_pct': err_C, 'sigma': abs(tau_C - TAU_PLANCK)/TAU_PLANCK_ERR},
    'D (CY₃)': {'value': tau_D, 'err_pct': err_D, 'sigma': abs(tau_D - TAU_PLANCK)/TAU_PLANCK_ERR},
    'E (tree)': {'value': tau_E, 'err_pct': err_E, 'sigma': abs(tau_E - TAU_PLANCK)/TAU_PLANCK_ERR},
}

PASS = 0
FAIL = 0
for name, r in results.items():
    if r['err_pct'] < 30:
        mark = '✅' if r['sigma'] < 1 else '🟡'
        PASS += 1
    else:
        mark = '❌'
        FAIL += 1
    print(f"  {mark} 公式 {name}: τ={r['value']:.6f}, err={r['err_pct']:.2f}%, σ={r['sigma']:.2f}")

print(f"\n結果：{PASS}/{PASS + FAIL} 通過")
best = min(results.items(), key=lambda x: x[1]['err_pct'])
print(f"最佳公式：{best[0]} (τ={best[1]['value']:.6f}, err={best[1]['err_pct']:.2f}%)")

# 同步儲存
with open('data/tau_results_v2.json', 'w') as f:
    json.dump({'results': results, 'best': best[0], 'tau_planck': TAU_PLANCK}, f, indent=2)

print(f"\n結果已儲存至 data/tau_results_v2.json")
print(f"{'=' * 72}")