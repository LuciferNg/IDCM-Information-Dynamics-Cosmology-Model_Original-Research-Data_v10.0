#!/usr/bin/env python3
"""
03_gunn_peterson_analysis.py
==============================
IDCM 結構分析：Gunn-Peterson trough 作為 K_Chain mode 轉換

ΛCDM 解釋：z>6 嘅 Gunn-Peterson trough 係 IGM 中性氫吸收
IDCM 解釋：z=6 對應 ℓ = log₄(7) ≈ 1.403，係 K_Chain mode 激活/壓制閾值

分析目標：
1. 計算 z=6 對應嘅 K_Chain/K_Tree 結構參數
2. 找出 Gunn-Peterson 光學深度 τ_GP(z) 嘅結構預測
3. 與觀測數據比較

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
EPS = PHI_INV / 4
KAPPA = 1 / 16
BETA = PHI_INV / 2
N_d = 44
M = 33
B = 4
h11 = 36
h21 = 98
CY3 = h11 + h21
R_H = 4129.94  # Mpc
H0 = 72.59  # km/s/Mpc

# ================================================================
# K_Chain Mode Parameters
# ================================================================
def gamma_n(n):
    return 4 * (math.sin(math.pi * n / 88) ** 2)

def v_g(n):
    return math.cos(math.pi * n / 88)

def z_to_ell(z):
    """ℓ = log₄(1+z)"""
    return math.log(1 + z) / math.log(4)

def ell_to_z(ell):
    """z = 4^ℓ - 1"""
    return 4**ell - 1

# ================================================================
# 結構分析
# ================================================================
print("=" * 72)
print("IDCM 再電離問題 — 路徑 2：Gunn-Peterson 結構分析")
print("=" * 72)

# 關鍵紅移值
z_gp = 6.0  # Gunn-Peterson trough 位置
z_sync_bump = 0.6  # SYNC bump
z_nyquist = 17.0  # Nyquist cutoff

ell_gp = z_to_ell(z_gp)
ell_sync = z_to_ell(z_sync_bump)
ell_nyquist = z_to_ell(z_nyquist)

print(f"\n關鍵結構轉換：")
print(f"  z=0     → ℓ={z_to_ell(0):.3f}  (現在)")
print(f"  z=0.6   → ℓ={ell_sync:.3f}  (SYNC bump)")
print(f"  z=3     → ℓ={z_to_ell(3):.3f}  (K_Tree level ℓ=1)")
print(f"  z=6     → ℓ={ell_gp:.3f}  (Gunn-Peterson trough)")
print(f"  z=15    → ℓ={z_to_ell(15):.3f}  (K_Tree level ℓ=2)")
print(f"  z=17    → ℓ={ell_nyquist:.3f}  (Nyquist cutoff)")

# ================================================================
# K_Chain mode 激活閾值分析
# ================================================================
print(f"\n{'=' * 72}")
print("K_Chain mode 激活閾值分析")
print("=" * 72)

# 每個 K_Chain mode n 有一個激活紅移 z_n
# 跟據 IDCM，mode n 嘅激活紅移為：
# z_n = (γ_n / γ_2) * z_c - 1
# 其中 γ_2 = SYNC mode eigenvalue, z_c = 0.6 (SYNC bump)

gamma_2 = gamma_n(2)
z_c = 0.6

print(f"\nMode 激活紅移：z_n = (γ_n/γ₂) × z_c - 1")
print(f"  γ₂ = {gamma_2:.6f}, z_c = {z_c}")

print(f"\n  n   | γ_n     | z_n     | ℓ_n     | 意義")
print(f"  {'-'*5}|{'─'*9}|{'─'*9}|{'─'*9}|{'─'*20}")
for n in [1, 2, 3, 4, 5, 6, 7, 10, 15, 20, 22, 30, 40, 44]:
    gn = gamma_n(n)
    zn = (gn / gamma_2) * z_c - 1
    if zn < 0:
        continue
    eln = z_to_ell(zn)
    note = ""
    if abs(zn - 6) < 1:
        note = " ← Gunn-Peterson"
    elif abs(zn - 0.6) < 0.5:
        note = " ← SYNC bump"
    elif abs(zn - 17) < 3:
        note = " ← Nyquist"
    elif n == 22:
        note = " ← v_g = c"
    print(f"  {n:3d} | {gn:7.4f} | {zn:7.2f} | {eln:7.3f} |{note}")

# 找出 Gunn-Peterson 區域附近嘅 mode
print(f"\n\nGunn-Peterson 區域 (z≈4-8) 嘅 mode：")
print(f"  n   | γ_n     | z_n     | ℓ_n     | v_g")
for n in range(1, N_d + 1):
    gn = gamma_n(n)
    zn = (gn / gamma_2) * z_c - 1
    if 4 <= zn <= 8:
        eln = z_to_ell(zn)
        print(f"  {n:3d} | {gn:7.4f} | {zn:7.2f} | {eln:7.3f} | {v_g(n):+.4f}")

# ================================================================
# Gunn-Peterson 光學深度結構預測
# ================================================================
print(f"\n{'=' * 72}")
print("Gunn-Peterson 光學深度 τ_GP(z) 結構預測")
print("=" * 72)

# 喺 IDCM 中，τ_GP(z) 係未被激活 mode 嘅比例
# 當 mode n 激活時，佢嘅 beat frequency 會產生 UV 光子
# 未激活 mode 嘅區域 = 中性氫

# 簡單模型：τ_GP(z) ∝ (未激活 mode 數) / N_d
# 未激活 mode = 所有 z_n > z 嘅 mode

print(f"\nτ_GP(z) 模型：")
print(f"  τ_GP(z) ∝ (N_d - N_activated(z)) / N_d")
print(f"  其中 N_activated(z) = 激活紅移 z_n < z 嘅 mode 數")

for z in [0, 0.6, 3, 5, 6, 7, 10, 15, 17]:
    n_activated = 0
    for n in range(1, N_d + 1):
        gn = gamma_n(n)
        zn = (gn / gamma_2) * z_c - 1
        if zn <= z:
            n_activated += 1
    
    tau_gp = (N_d - n_activated) / N_d
    ell = z_to_ell(z)
    print(f"  z={z:5.1f} (ℓ={ell:.3f}): N_activated={n_activated:2d}, τ_GP={tau_gp:.4f}")

# ================================================================
# 與觀測比較
# ================================================================
print(f"\n{'=' * 72}")
print("與觀測比較")
print("=" * 72)

# 觀測數據（近似值）
# Gunn-Peterson 光學深度喺 z≈5.5 開始急劇上升
# 數據來源：Becker+2001, Fan+2006
obs_data = {
    5.0: 0.1,
    5.5: 0.5,
    5.8: 2.0,
    6.0: 5.0,
    6.5: 7.0,
}

print(f"\n  z     | τ_GP_pred | τ_GP_obs | 註釋")
print(f"  {'-'*6}|{'─'*11}|{'─'*10}|{'─'*16}")
for z in sorted(obs_data.keys()):
    n_activated = 0
    for n in range(1, N_d + 1):
        gn = gamma_n(n)
        zn = (gn / gamma_2) * z_c - 1
        if zn <= z:
            n_activated += 1
    tau_pred = (N_d - n_activated) / N_d * 10  # 歸一化比例
    tau_obs = obs_data[z]
    print(f"  {z:4.1f}  | {tau_pred:9.4f} | {tau_obs:8.1f} |")

print(f"\n（注意：τ_GP_pred 需要歸一化因子，上表用 ×10 做粗略比較）")

# ================================================================
# 儲存結果
# ================================================================
results = {
    'z_gp': z_gp,
    'ell_gp': ell_gp,
    'z_sync': z_sync_bump,
    'z_nyquist': z_nyquist,
    'mode_activation': {},
    'tau_gp_predictions': {}
}

for n in range(1, N_d + 1):
    gn = gamma_n(n)
    zn = (gn / gamma_2) * z_c - 1
    if zn > 0:
        results['mode_activation'][f'n_{n}'] = {
            'gamma': gn,
            'z_activation': zn,
            'ell_activation': z_to_ell(zn),
            'v_g': v_g(n)
        }

for z in [0, 0.6, 3, 5, 6, 7, 10, 15, 17]:
    n_activated = sum(1 for n in range(1, N_d + 1) 
                      if (gamma_n(n) / gamma_2) * z_c - 1 <= z)
    results['tau_gp_predictions'][f'z_{z}'] = {
        'ell': z_to_ell(z),
        'n_activated': n_activated,
        'tau_gp_ratio': (N_d - n_activated) / N_d
    }

with open('data/gp_analysis.json', 'w') as f:
    json.dump(results, f, indent=2, default=lambda x: float(f"{x:.6f}") if isinstance(x, float) else x)

print(f"\n結果已儲存至 data/gp_analysis.json")
print(f"{'=' * 72}")