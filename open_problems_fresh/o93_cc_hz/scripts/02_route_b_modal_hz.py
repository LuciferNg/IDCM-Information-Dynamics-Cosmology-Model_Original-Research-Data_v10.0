#!/usr/bin/env python3
"""
O93/02: 路線 B — K_Chain 色散關係 → H(z) 結構推導
====================================================
核心思想: H(z) 唔係 dD_A/dz, 而係 K_Chain 模式激活嘅加權平均。

框架:
- γ_n = 4sin²(πn/88), n=1..88 — K_Chain 模式能量
- v_g(n) = c·cos(πn/88) — 群速度
- 喺紅移 z, 對應 ℓ = log₄(1+z), 激活模式 n ≤ n_max(ℓ)
- 世界能量 Σγ = 90 (44-site)
- H(z) = H₀ × (Σ_active_γ_n / Σγ) × (scale factor)

物理圖像:
  IDCM 中「膨脹」= K_Chain 模式嘅序貫激活。
  高 z → 更遠距離 → 更多模式激活 → 更高嘅有效頻率 → 更高嘅 H(z)
"""
import math
import numpy as np
import sys
sys.path.insert(0, '../data')
from cc_hz_data import *

# 常數
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
R_WORLD = 4129.94       # Mpc
C_LIGHT = 299792.458    # km/s
OMEGA_RING = 72.59      # km/s/Mpc = H(0)
N_SITES = 88            # 雙鏈
N_SITES_HALF = 44       # 世界鏈

# K_Chain 模式
N = np.arange(1, N_SITES + 1, dtype=float)
GAMMA_N = 4 * np.sin(np.pi * N / N_SITES)**2  # 模式能量
V_G_N = C_LIGHT * np.cos(np.pi * N / N_SITES)  # 群速度 (km/s)

# 世界能量
SUM_GAMMA = 90  # Σγ_even = 90 (44-site)

PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"    {detail}")

print("=" * 70)
print("  O93/02: 路線 B — K_Chain 色散關係 → H(z)")
print("=" * 70)

# ============ 1. K_Chain 模式結構 ============
print("\n--- 1. K_Chain 模式結構 ---")
print(f"  模式數: {N_SITES}")
print(f"  γ_n = 4sin²(πn/88)")
print(f"  Σγ (44-site) = {SUM_GAMMA}")
print(f"  v_g(n) = c·cos(πn/88)")

# 驗證結構常數
check("Σγ (44-site) = 90", abs(np.sum(GAMMA_N[1::2]) - 90) < 0.1,  # even indices = world chain (0-indexed, 1::2 = odd = even-k)
      f"Σγ_world = {np.sum(GAMMA_N[1::2]):.4f}")

check("Σγ (observer) = 88", abs(np.sum(GAMMA_N[::2]) - 88) < 0.1,
      f"Σγ_obs = {np.sum(GAMMA_N[::2]):.4f}")

check("Σγ_total = 178 = 2F₁₁", abs(np.sum(GAMMA_N) - 178) < 0.1,
      f"Σγ_total = {np.sum(GAMMA_N):.4f}")

check("v_g(1) ≈ c·cos(π/88) ≈ c",
      abs(V_G_N[0] / C_LIGHT - math.cos(math.pi / 88)) < 1e-6)

check("v_g(44) = 0 (Nyquist)",
      abs(V_G_N[43]) < 1e-6)

# ============ 2. 模式激活 redshift ============
print("\n\n--- 2. 模式激活 Redshift 映射 ---")
# 每個模式 n 喺特定 redshift z_n 激活
# ℓ = log₄(1+z) = n/N_sites  (模式序號/總模式數)
# z_n = 4^(n/N_sites) - 1

# 方法 1: 線性映射 (ℓ = n/44)
z_act_linear = [4**(n/44) - 1 for n in range(1, N_SITES_HALF + 1)]

# 方法 2: 能量映射 (γ_n / γ₂ 比例)
# 最低模式 n=2 對應 z=0, n 越高 z 越高
gamma_2 = 4 * math.sin(2 * math.pi / 88)**2
z_act_energy = [gamma_n / gamma_2 - 1 for gamma_n in GAMMA_N[1:N_SITES_HALF + 1:2]]  # odd indices (even-k in 1-indexed)

print(f"  {'n':>3} | {'γ_n':>10} | {'z_linear':>10} | {'z_energy':>10} | {'v_g/c':>8}")
for n in range(1, N_SITES_HALF + 1, 4):  # every 4th
    n_idx = n - 1  # 0-indexed (odd n = even-k world chain)
    z_lin = 4**(n / 44) - 1
    z_eng = GAMMA_N[n_idx] / gamma_2 - 1 if n_idx < len(GAMMA_N) else 0
    vg_ratio = V_G_N[n_idx] / C_LIGHT if n_idx < len(V_G_N) else 0
    print(f"  {n:3d} | {GAMMA_N[n_idx]:10.6f} | {z_lin:10.4f} | {z_eng:10.4f} | {vg_ratio:8.4f}")

# ============ 3. 模式加權 H(z) 模型 ============
print("\n\n--- 3. 模式加權 H(z) 模型 ---")

def H_kchain_modal(z, power=1.0, weight_type='gamma'):
    """
    K_Chain 模式加權 H(z)
    
    核心公式: 
    ℓ = log₄(1+z) — IDCM 距離尺度
    n_active(ℓ) = min(44, floor(44 * ℓ + 1)) — 激活模式數
    H(z) = H₀ × (Σ_{n=1}^{n_active} [γ_n · w(n)] / Σγ) × (1+z)^power
    
    考慮 active 模式嘅能量加權平均。高 z → 更多高能模式激活 → 更高 H(z)
    """
    ell = math.log(1 + z, 4)
    
    # 激活模式數 (世界鏈: n=1..44, odd indices in 1-indexed = even indices in 0-indexed)
    n_active = min(N_SITES_HALF, max(1, int(44 * ell)))
    
    # 世界模式 (odd n in 1-indexed = index 1,3,5,... in 0-indexed)
    world_gamma = GAMMA_N[1::2]  # 44 modes
    world_vg = V_G_N[1::2]
    
    # 加權和
    if weight_type == 'gamma':
        # 純能量加權
        weighted_sum = np.sum(world_gamma[:n_active])
    elif weight_type == 'gamma_vg':
        # 能量 × 群速度加權
        weighted_sum = np.sum(world_gamma[:n_active] * np.abs(world_vg[:n_active]))
    elif weight_type == 'uniform':
        # 均勻加權
        weighted_sum = float(n_active)
    elif weight_type == 'gamma_sq':
        weighted_sum = np.sum(world_gamma[:n_active]**2)
    else:
        weighted_sum = np.sum(world_gamma[:n_active])
    
    # 歸一化: H(z) = H₀ × (加權和 / Σγ) × 尺度因子
    norm = np.sum(world_gamma)  # = 90
    h = OMEGA_RING * (weighted_sum / norm) * (1 + z)**power
    
    return h

# 測試不同權重模型
print(f"  {'z':>5} | {'H_obs':>8} | {'γ_weight':>8} | {'γ·v_g':>8} | {'γ²_weight':>8} | {'uniform':>8} | {'H_LCDM':>8}")

weight_types = ['gamma', 'gamma_vg', 'gamma_sq', 'uniform']
z_vals = CC_COMBINED[0]
h_obs = CC_COMBINED[1]
h_err = CC_COMBINED[2]

for zi in range(min(10, len(z_vals))):
    z = z_vals[zi]
    h_ob = h_obs[zi]
    h_lc = H_lcdm(z) if 'H_lcdm' in dir() else 0
    # H_lcdm
    h_lc = 67.4 * math.sqrt(0.315 * (1+z)**3 + 0.685)
    
    h_gamma = H_kchain_modal(z, power=0, weight_type='gamma')
    h_gamma_vg = H_kchain_modal(z, power=0, weight_type='gamma_vg')
    h_gamma_sq = H_kchain_modal(z, power=0, weight_type='gamma_sq')
    h_uniform = H_kchain_modal(z, power=0, weight_type='uniform')
    
    print(f"  {z:5.3f} | {h_ob:8.1f} | {h_gamma:8.1f} | {h_gamma_vg:8.1f} | {h_gamma_sq:8.1f} | {h_uniform:8.1f} | {h_lc:8.1f}")

# ============ 4. 尋找最佳權重模型 ============
print(f"\n\n--- 4. 權重模型 χ² 比較 (全 36 點) ---")

for weight_type in weight_types:
    for power in [0, 0.5, 1.0, 1.5, 2.0]:
        chi2 = 0.0
        for i in range(len(z_vals)):
            z = z_vals[i]
            h_ob = h_obs[i]
            he = h_err[i]
            h_mod = H_kchain_modal(z, power=power, weight_type=weight_type)
            chi2 += ((h_ob - h_mod) / he)**2
        
        print(f"  {weight_type:12} | power={power:3.1f} | χ² = {chi2:8.2f} | χ²/dof = {chi2/len(z_vals):8.4f}")

# ============ 5. 最佳模型: 詳細結果 ============
print(f"\n\n--- 5. 最佳模型 (gamma_vg, power=1.0) — 詳細 ---")
print(f"  {'z':>5} | {'H_obs':>8} | {'σ_H':>6} | {'H_model':>8} | {'O-C':>8} | {'pull':>8}")

best_type = 'gamma_vg'
best_power = 1.0
chi2_best = 0.0

for i in range(len(z_vals)):
    z = z_vals[i]
    h_ob = h_obs[i]
    he = h_err[i]
    h_mod = H_kchain_modal(z, power=best_power, weight_type=best_type)
    oc = h_ob - h_mod
    pull = oc / he
    chi2_best += pull**2
    print(f"  {z:5.3f} | {h_ob:8.1f} | {he:6.1f} | {h_mod:8.1f} | {oc:+8.1f} | {pull:+8.3f}")

print(f"\n  χ² = {chi2_best:.2f}, χ²/dof = {chi2_best/len(z_vals):.4f}")

# ============ 6. 紅移分段 ============
print(f"\n\n--- 6. 紅移分段 χ² (最佳模型) ---")
mask_low = z_vals < 0.5
mask_mid = (z_vals >= 0.5) & (z_vals < 1.0)
mask_high = z_vals >= 1.0

for mask, label in [(mask_low, 'z<0.5'), (mask_mid, '0.5≤z<1.0'), (mask_high, 'z≥1.0')]:
    z_sub = z_vals[mask]
    h_sub = h_obs[mask]
    e_sub = h_err[mask]
    chi2 = np.sum(((h_sub - np.array([H_kchain_modal(z, best_power, best_type) for z in z_sub])) / e_sub)**2)
    print(f"  {label:>12} | N={np.sum(mask):2d} | χ² = {chi2:8.2f} | χ²/dof = {chi2/np.sum(mask):.4f}")

# ============ 7. H(z) 曲線 (最佳模型) ============
print(f"\n\n--- 7. 最佳模型 H(z) 曲線 ---")
print(f"  {'z':>5} | {'H_modal':>8} | {'H_LCDM':>8} | {'ratio':>8}")
for z in np.linspace(0, 2.0, 21):
    h_mod = H_kchain_modal(z, best_power, best_type)
    h_lc = 67.4 * math.sqrt(0.315 * (1+z)**3 + 0.685)
    print(f"  {z:5.2f} | {h_mod:8.1f} | {h_lc:8.1f} | {h_mod/h_lc:8.4f}")

# ============ 8. 結構分析: 模式激活曲線 ============
print(f"\n\n--- 8. 模式激活詳細分析 ---")
print(f"  {'z':>5} | {'ℓ':>6} | {'n_active':>8} | {'Σγ_active':>10} | {'weighted':>10} | {'H_model':>8}")

for z in [0.0, 0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]:
    ell = math.log(1 + z, 4)
    n_active = min(N_SITES_HALF, max(1, int(44 * ell)))
    world_gamma = GAMMA_N[1::2]
    world_vg = V_G_N[1::2]
    
    sum_gamma = np.sum(world_gamma[:n_active])
    weighted = np.sum(world_gamma[:n_active] * np.abs(world_vg[:n_active]))
    h_mod = H_kchain_modal(z, best_power, best_type)
    
    print(f"  {z:5.1f} | {ell:6.4f} | {n_active:8d} | {sum_gamma:10.4f} | {weighted:10.1f} | {h_mod:8.1f}")

# ============ 9. 與 ΛCDM 的全面比較 ============
print(f"\n\n--- 9. IDCM (modal) vs ΛCDM 全面 χ² 比較 ---")
chi2_idcm_best = 0.0
chi2_lcdm = 0.0
for i in range(len(z_vals)):
    z = z_vals[i]
    h_ob = h_obs[i]
    he = h_err[i]
    h_mod = H_kchain_modal(z, best_power, best_type)
    h_lc = 67.4 * math.sqrt(0.315 * (1+z)**3 + 0.685)
    chi2_idcm_best += ((h_ob - h_mod) / he)**2
    chi2_lcdm += ((h_ob - h_lc) / he)**2

print(f"  IDCM (modal): χ² = {chi2_idcm_best:.2f}, χ²/dof = {chi2_idcm_best/len(z_vals):.4f}")
print(f"  ΛCDM:         χ² = {chi2_lcdm:.2f}, χ²/dof = {chi2_lcdm/len(z_vals):.4f}")
print(f"  Δχ² = χ²_lcdm - χ²_idcm = {chi2_lcdm - chi2_idcm_best:+.2f}")

# ============ 總結 ============
print(f"\n{'='*70}")
print(f"  總結: 路線 B — K_Chain 色散關係 → H(z)")
print(f"  {'='*70}")
print(f"")
print(f"  最佳模型: {best_type}, power={best_power}")
print(f"  χ² = {chi2_best:.2f}, χ²/dof = {chi2_best/len(z_vals):.4f}")
print(f"  ΛCDM: χ² = {chi2_lcdm:.2f}, χ²/dof = {chi2_lcdm/len(z_vals):.4f}")
print(f"  Δχ² = {chi2_lcdm - chi2_idcm_best:+.2f}")

# 儲存結果
import json
results = {
    "route": "B",
    "best_weight_type": best_type,
    "best_power": best_power,
    "chi2_idcm_modal": float(f"{chi2_idcm_best:.2f}"),
    "chi2_lcdm": float(f"{chi2_lcdm:.2f}"),
    "delta_chi2": float(f"{chi2_lcdm - chi2_idcm_best:.2f}"),
    "n_total": int(len(z_vals)),
    "pass": int(PASS),
    "fail": int(FAIL),
    "status": "🟡"
}
with open("../data/02_route_b_results.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\n  結果已儲存至 data/02_route_b_results.json")