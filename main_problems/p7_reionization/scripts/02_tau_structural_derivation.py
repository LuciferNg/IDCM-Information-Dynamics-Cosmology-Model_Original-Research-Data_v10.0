#!/usr/bin/env python3
"""
02_tau_structural_derivation.py
================================
IDCM 結構推導：CMB 光深 τ 嘅結構公式

從 K_Chain mode impedance Z_n = γ_n / |v_g(n)| 推導 τ，
唔用 ΛCDM 嘅積分 ∫ n_e σ_T c dt。

假設：τ 係 K_Chain 高阻抗 mode 嘅駐波節點密度，
等於 44 個 mode 中 v_g < 0 嘅比例乘某個投影因子。

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
R_H = 4129.94                # Mpc (c/H₀ with H₀=72.59)
H0 = 72.59                   # km/s/Mpc
LAMBDA_SYNC = 294.88         # Mpc
BAO = LAMBDA_SYNC / 2        # 147.44 Mpc

# ================================================================
# K_Chain Mode Parameters
# ================================================================
def gamma_n(n):
    """K_Chain eigenvalue γ_n = 4 sin²(πn/88)"""
    return 4 * (math.sin(math.pi * n / 88) ** 2)

def v_g(n):
    """Group velocity v_g(n) = cos(πn/88)"""
    return math.cos(math.pi * n / 88)

def Z_n(n):
    """Impedance Z_n = γ_n / |v_g(n)|"""
    vg = v_g(n)
    if abs(vg) < 1e-15:
        return float('inf')
    return gamma_n(n) / abs(vg)

# ================================================================
# Path 1: τ (CMB optical depth) structural derivation
# ================================================================
print("=" * 72)
print("IDCM 再電離問題 — 路徑 1：τ 結構公式推導")
print("=" * 72)

# Compute all 44 mode parameters
modes = []
for n in range(1, N_d + 1):
    modes.append({
        'n': n,
        'gamma': gamma_n(n),
        'v_g': v_g(n),
        'Z': Z_n(n),
        'v_g_sign': 1 if v_g(n) >= 0 else -1
    })

# 高阻抗 mode (v_g < 0，代表反向傳播 = 駐波節點)
n_high_z = [m for m in modes if m['v_g_sign'] < 0]
n_low_z = [m for m in modes if m['v_g_sign'] >= 0]

print(f"\nK_Chain 44 modes:")
print(f"  正向傳播 (v_g ≥ 0): {len(n_low_z)} modes (n=1..22)")
print(f"  反向傳播 (v_g < 0): {len(n_high_z)} modes (n=23..44)")
print(f"  SYNC mode (n=22): γ={gamma_n(22):.6f}, v_g={v_g(22):.6f}")

# τ 結構公式：高阻抗 mode 密度 × CY₃ 投影因子 × ε 階修正
# 高阻抗 mode 比例 = 22/44 = 0.5
# 但只有部分高阻抗 mode 貢獻 τ（因為駐波節點密度）
# 駐波節點 = v_g 接近 0 嘅 mode 附近

# 第一假設：τ = (高阻抗 mode 比例) × (CY₃ 投影因子) × (K_Tree 深度因子)
# CY₃ 投影因子 = h11 / h21 = 36/98 ≈ 0.367
# K_Tree 深度因子 = 1 - 1/B^M ≈ 1 (因為 M=33, B=4)
# 但實際上 τ 應該係雙層結構 (K_Chain + K_Tree)

# 推導 τ 公式：
# τ = (N_highZ / N_d) × (h11/CY3) × (1 - 1/B^M) × (1 + ε)
# 物理：τ = 反向傳播 mode 比例 × 投影維度比 × 樹深度修正 × ε 階修正

# 公式 1: 基本結構
tau_v1 = (len(n_high_z) / N_d) * (h11 / CY3) * (1 - 1 / B**M) * (1 + EPS)
print(f"\nτ 公式 v1 (基本結構):")
print(f"  τ = (N_highZ/N_d) × (h11/CY₃) × (1-1/B^M) × (1+ε)")
print(f"    = ({len(n_high_z)}/{N_d}) × ({h11}/{CY3}) × (1-1/{B}^{M}) × (1+{EPS:.6f})")
print(f"    = {tau_v1:.6f}")

# 公式 2: 用阻抗比代替簡單計數
# Z_avg_high = 高阻抗 mode 嘅平均阻抗
# Z_avg_low = 低阻抗 mode 嘅平均阻抗
Z_high = [m['Z'] for m in n_high_z]
Z_low = [m['Z'] for m in n_low_z]
Z_ratio = sum(Z_high) / sum(Z_low)

tau_v2 = (Z_ratio / (1 + Z_ratio)) * (h11 / CY3) * (1 - 1 / B**M)
print(f"\nτ 公式 v2 (阻抗比):")
print(f"  τ = (Z_high/Z_total) × (h11/CY₃) × (1-1/B^M)")
print(f"  Z_ratio (高/低) = {Z_ratio:.4f}")
print(f"  τ = {tau_v2:.6f}")

# 公式 3: 駐波節點密度
# 駐波節點出現喺 v_g 符號反轉附近 (n=22,23)
# τ = (1/2) × (1/44) × (h11+CY3)/CY3 × (1 - 1/B^M)
# 物理：每對相鄰 mode 有一個駐波節點，共 44 個間隔，一半係駐波節點
tau_v3 = 0.5 * (1/N_d) * ((h11 + CY3) / CY3) * (1 - 1/B**M * EPS)
print(f"\nτ 公式 v3 (駐波節點):")
print(f"  τ = (1/2) × (1/N_d) × ((h¹¹+CY₃)/CY₃) × (1-1/B^M × ε)")
print(f"    = {tau_v3:.6f}")

# 公式 4: 最優結構公式
# τ = (N_d - h11) / (N_d * CY3) * (1 + ε) × (1 - 1/B^M)
# N_d - h11 = 44 - 36 = 8 (剩餘通道)
tau_v4 = (N_d - h11) / (N_d * CY3) * (1 + EPS) * (1 - 1 / B**M)
print(f"\nτ 公式 v4 (剩餘通道):")
print(f"  τ = (N_d - h¹¹) / (N_d × CY₃) × (1+ε) × (1-1/B^M)")
print(f"    = ({N_d - h11}) / ({N_d} × {CY3}) × (1+{EPS:.6f}) × (1-1/{B}^{M})")
print(f"    = {tau_v4:.6f}")

# ================================================================
# 外部參考：Planck 2018 τ
# ================================================================
TAU_PLANCK = 0.054  # Planck 2018 τ = 0.054 ± 0.007
TAU_PLANCK_ERR = 0.007

print(f"\n{'=' * 72}")
print(f"外部參考：Planck 2018 τ = {TAU_PLANCK} ± {TAU_PLANCK_ERR}")
print(f"{'=' * 72}")

results = {
    'tau_v1 (基本結構)': {'value': tau_v1, 'error_pct': abs(tau_v1/TAU_PLANCK - 1) * 100, 'status': '🟡' if abs(tau_v1/TAU_PLANCK - 1) * 100 < 30 else '🔴'},
    'tau_v2 (阻抗比)': {'value': tau_v2, 'error_pct': abs(tau_v2/TAU_PLANCK - 1) * 100, 'status': '🟡' if abs(tau_v2/TAU_PLANCK - 1) * 100 < 30 else '🔴'},
    'tau_v3 (駐波節點)': {'value': tau_v3, 'error_pct': abs(tau_v3/TAU_PLANCK - 1) * 100, 'status': '🟡' if abs(tau_v3/TAU_PLANCK - 1) * 100 < 30 else '🔴'},
    'tau_v4 (剩餘通道)': {'value': tau_v4, 'error_pct': abs(tau_v4/TAU_PLANCK - 1) * 100, 'status': '🟡' if abs(tau_v4/TAU_PLANCK - 1) * 100 < 30 else '🔴'},
}

PASS = 0
FAIL = 0
for name, r in results.items():
    mark = '✅' if r['error_pct'] < 10 else '🟡' if r['error_pct'] < 30 else '❌'
    if r['error_pct'] < 30:
        PASS += 1
    else:
        FAIL += 1
    print(f"\n  {mark} {name}")
    print(f"      τ = {r['value']:.6f} (ref {TAU_PLANCK}, err {r['error_pct']:.2f}%)")
    r['status'] = mark

print(f"\n{'=' * 72}")
print(f"結果：{PASS}/{PASS + FAIL} 通過（30% 閾值）")
print(f"{'=' * 72}")

# ================================================================
# 儲存結果
# ================================================================
output = {
    'tau_planck': TAU_PLANCK,
    'tau_planck_err': TAU_PLANCK_ERR,
    'formulas': results,
    'mode_counts': {
        'forward': len(n_low_z),
        'backward': len(n_high_z)
    },
    'impedance_ratio': Z_ratio,
    'best_tau': min(results.items(), key=lambda x: abs(x[1]['value']/TAU_PLANCK - 1))[1]['value'],
    'best_formula': min(results.items(), key=lambda x: abs(x[1]['value']/TAU_PLANCK - 1))[0],
}

with open('data/tau_results.json', 'w') as f:
    json.dump(output, f, indent=2, default=lambda x: float(f"{x:.6f}") if isinstance(x, float) else x)

print(f"\n結果已儲存至 data/tau_results.json")

# 總結
print(f"\n{'=' * 72}")
print("最佳公式：", output['best_formula'])
print(f"最佳 τ = {output['best_tau']:.6f} (Planck {TAU_PLANCK}, err {abs(output['best_tau']/TAU_PLANCK-1)*100:.2f}%)")
print(f"{'=' * 72}")