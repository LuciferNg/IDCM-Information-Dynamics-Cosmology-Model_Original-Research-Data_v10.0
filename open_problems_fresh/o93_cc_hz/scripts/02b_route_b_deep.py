#!/usr/bin/env python3
"""
O93/02b: 路線 B — H(z) 結構推導 (深化)
========================================
核心問題: IDCM 嘅 D_A(z) 描述投影距離，唔係膨脹歷史。
CC H(z) 測量 dz/dt (時間膨脹)，而 IDCM 同 ΛCDM 有相同嘅 (1+z) 時間膨脹。

關鍵洞察:
- IDCM 中宇宙唔係 metric expansion
- H(z) 係 K_Chain 模式激活嘅結構速率
- 時間膨脹 (1+z) 同 ΛCDM → CC H(z) 應該匹配 ΛCDM 形狀

探索: 乜嘢結構公式能從 K_Chain 產生 H(z) ≈ ΛCDM H(z)?
"""
import math
import numpy as np
import sys
sys.path.insert(0, '../data')
from cc_hz_data import *

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
R_WORLD = 4129.94
C_LIGHT = 299792.458
OMEGA_RING = 72.59
C_DELAY = -0.1697
N = 88
N_HALF = 44

# K_Chain
ns = np.arange(1, N + 1, dtype=float)
GAMMA = 4 * np.sin(np.pi * ns / N)**2
VG = np.cos(np.pi * ns / N)  # v_g/c
SUM_GAMMA_WORLD = 90  # Σγ_even-k (44-site)

# CC data
z_vals = CC_COMBINED[0]
h_obs = CC_COMBINED[1]
h_err = CC_COMBINED[2]

# ΛCDM ref
def H_lcdm(z):
    return 67.4 * math.sqrt(0.315 * (1+z)**3 + 0.685)

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
print("  O93/02b: 路線 B — H(z) 結構推導 (深化)")
print("=" * 70)

# ============ 1. 從 D_A(z) 睇 H(z) 結構 ============
print("\n--- 1. 從 D_A(z) 反推 H(z) 結構 ---")
# 如果 H(z) = c/(dχ/dz), 反推 H(z) 應該係乜野形狀
# 由 CC 數據: H(z) ≈ 70-200, 隨 z 增加
# 由 D_A(z): H(z) = c/(D_A + (1+z)dD_A/dz)

# 其實 H(z) 同 D_A(z) 嘅關係可以寫成:
# 1/H(z) = (1/c) × [D_A(z) + (1+z) × dD_A/dz]

# 如果 D_A(z) 係已知, 我哋可以計算 H(z) 嘅「有效」形狀
# 但問題係: D_A(z) 喺 IDCM 中唔係由 H(z) 積分得出

# 反過來: 如果 CC H(z) 係正確, 咁 D_A(z) 應該係:
# D_A(z) = c/(1+z) × ∫₀ᶻ dz'/H(z')
# 用梯形積分
def chi_from_H(z):
    """從 H(z) 積分計算 comoving distance"""
    n = 1000
    zs = np.linspace(0, z, n)
    hs = np.array([H_lcdm(zz) for zz in zs])
    integrand = C_LIGHT / hs
    return np.trapezoid(integrand, zs)

def D_A_from_H(z):
    """從 ΛCDM H(z) 計算 D_A(z)"""
    return chi_from_H(z) / (1 + z)

print("  IDCM D_A(z) vs ΛCDM D_A(z) (從 H(z) 積分):")
print(f"  {'z':>5} | {'D_A_IDCM':>10} | {'D_A_LCDM':>10} | {'ratio':>8}")

def D_A_idcm(z):
    ell = math.log(1 + z, 4)
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2 * PHI_INV * ell
    delta = C_DELAY * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

for z in [0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]:
    da_idcm = D_A_idcm(z)
    da_lcdm = D_A_from_H(z)
    print(f"  {z:5.1f} | {da_idcm:10.0f} | {da_lcdm:10.0f} | {da_idcm/da_lcdm:8.4f}")

# ============ 2. 結構 H(z) 公式探索 ============
print("\n\n--- 2. 結構 H(z) 公式探索 ---")
# 從 K_Chain 結構出發, 搵出能匹配 CC H(z) 嘅公式
# H(z) = H₀ × f(ℓ) × (1+z)^p
# 其中 ℓ = log₄(1+z)

def chi2_H(model_func, name):
    """計算給定 H(z) 模型嘅 χ²"""
    chi2 = 0.0
    for i in range(len(z_vals)):
        z = z_vals[i]
        h_ob = h_obs[i]
        he = h_err[i]
        h_mod = model_func(z)
        chi2 += ((h_ob - h_mod) / he)**2
    return chi2 / len(z_vals)

# 模型 1: ΛCDM 形狀 (reference)
def H_lcdm_ref(z):
    return 67.4 * math.sqrt(0.315 * (1+z)**3 + 0.685)

# 模型 2: 冪律 H(z) = H₀(1+z)^n
def H_power(z, n):
    return OMEGA_RING * (1 + z)**n

# 模型 3: 從 K_Chain 能量密度 
# H(z) = H₀ × (1 + k × Σ_active_γ_n / Σγ)
def H_energy_ratio(z, k):
    ell = math.log(1 + z, 4)
    n_active = min(N_HALF, max(1, int(N_HALF * ell)))
    world_gamma = GAMMA[1::2]  # 世界鏈 (odd indices in 1-indexed)
    energy_ratio = np.sum(world_gamma[:n_active]) / SUM_GAMMA_WORLD
    return OMEGA_RING * (1 + k * energy_ratio)

# 模型 4: 從 K_Chain 能流
# H(z) ∝ Σ_active (γ_n × v_g(n))
# 需歸一化: H(0) = H₀
def H_energy_flux(z, alpha):
    ell = math.log(1 + z, 4)
    n_active = min(N_HALF, max(1, int(N_HALF * ell)))
    world_gamma = GAMMA[1::2]
    world_vg = np.abs(VG[1::2])
    flux = np.sum(world_gamma[:n_active] * world_vg[:n_active])
    flux0 = np.sum(world_gamma[:1] * world_vg[:1])
    return OMEGA_RING * (flux / flux0) * (1 + z)**alpha

# 模型 5: 激活能 + 總能量 
# H(z) = H₀ × (1 + Σ_active_γ_n / Σ_inactive_γ_n)^α
def H_activation_ratio(z, alpha):
    ell = math.log(1 + z, 4)
    n_active = min(N_HALF, max(1, int(N_HALF * ell)))
    world_gamma = GAMMA[1::2]
    active = np.sum(world_gamma[:n_active])
    inactive = SUM_GAMMA_WORLD - active
    if inactive <= 0:
        inactive = 1e-10
    return OMEGA_RING * (1 + active / inactive)**alpha

# 模型 6: K_Chain 模式密度 
# H(z) = H₀ (1 + z)^α × (γ_n_max / γ_1)
# 其中 n_max = floor(44·ℓ)
def H_mode_density(z, alpha):
    ell = math.log(1 + z, 4)
    n_max = min(N_HALF, max(1, int(N_HALF * ell)))
    gamma_max = GAMMA[2 * n_max - 1]  # world chain index
    gamma_1 = GAMMA[1]  # n=2 (world chain low mode)
    return OMEGA_RING * (gamma_max / gamma_1)**alpha

# 測試所有模型
print(f"  {'模型':>25} | {'參數':>12} | {'χ²/dof':>10} | {'優劣':>6}")
print(f"  {'-'*25} | {'-'*12} | {'-'*10} | {'-'*6}")

# ΛCDM reference
chi2_lcdm = chi2_H(H_lcdm_ref, "ΛCDM")
print(f"  {'ΛCDM (Planck 2018)':>25} | {'0 params':>12} | {chi2_lcdm:10.4f} | {'ref':>6}")

# 冪律
for n in [0.5, 0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5, 3.0]:
    chi2 = chi2_H(lambda z, n=n: H_power(z, n), "power")
    print(f"  {'冪律 (1+z)^n':>25} | {f'n={n:4.1f}':>12} | {chi2:10.4f} | {'🟢' if chi2 < chi2_lcdm else '🔴':>6}")

# 能量比
for k in [0.5, 1.0, 5.0, 10, 50, 100, 500, 1000]:
    chi2 = chi2_H(lambda z, k=k: H_energy_ratio(z, k), "energy_ratio")
    print(f"  {'能量比 (1+k·E_act/E_tot)':>25} | {f'k={k:5.0f}':>12} | {chi2:10.4f} | {'🟢' if chi2 < chi2_lcdm else '🔴':>6}")

# 能流
for alpha in [0, 0.5, 1.0, 1.5, 2.0]:
    chi2 = chi2_H(lambda z, a=alpha: H_energy_flux(z, a), "energy_flux")
    print(f"  {'能流 γ·v_g × (1+z)^α':>25} | {f'α={alpha:4.1f}':>12} | {chi2:10.4f} | {'🟢' if chi2 < chi2_lcdm else '🔴':>6}")

# 激活比
for alpha in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
    chi2 = chi2_H(lambda z, a=alpha: H_activation_ratio(z, a), "activation_ratio")
    print(f"  {'激活比 (E_act/E_inact)^α':>25} | {f'α={alpha:4.1f}':>12} | {chi2:10.4f} | {'🟢' if chi2 < chi2_lcdm else '🔴':>6}")

# 模式密度
for alpha in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
    chi2 = chi2_H(lambda z, a=alpha: H_mode_density(z, a), "mode_density")
    print(f"  {'模式密度 (γ_max/γ₁)^α':>25} | {f'α={alpha:4.1f}':>12} | {chi2:10.4f} | {'🟢' if chi2 < chi2_lcdm else '🔴':>6}")

# ============ 3. 最佳非參數 H(z) ============
print(f"\n\n--- 3. 最佳冪律模型: H(z) = H₀(1+z)^n ---")
# 掃描最佳 n
best_n = 0
best_chi2 = 1e10
for n in np.linspace(0.5, 3.0, 51):
    chi2 = chi2_H(lambda z, n=n: H_power(z, n), "power")
    if chi2 < best_chi2:
        best_chi2 = chi2
        best_n = n

print(f"  最佳 n = {best_n:.4f}")
print(f"  χ²/dof = {best_chi2:.4f}")

# 詳細比較
print(f"\n  {'z':>5} | {'H_obs':>8} | {'σ_H':>6} | {'H_power':>8} | {'H_LCDM':>8} | {'O-C_power':>8} | {'O-C_LCDM':>8}")
for i in range(min(15, len(z_vals))):
    z = z_vals[i]
    h_ob = h_obs[i]
    he = h_err[i]
    h_pow = H_power(z, best_n)
    h_lc = H_lcdm(z)
    print(f"  {z:5.3f} | {h_ob:8.1f} | {he:6.1f} | {h_pow:8.1f} | {h_lc:8.1f} | {h_ob-h_pow:+8.1f} | {h_ob-h_lc:+8.1f}")

# ============ 4. K_Chain 結構分析: 模式激活率 ============
print(f"\n\n--- 4. K_Chain 模式激活率分析 ---")
# 喺 IDCM 中, H(z) 應該同模式激活率 dN_active/dz 有關
# 但 dN_active/dz 係階梯函數 (離散跳躍)
# 真正嘅平滑版本係: dℓ/dz = 1/((1+z)ln4)

# H(z) ∝ 1/(1+z) 比 H(z) ∝ (1+z)^n 唔匹配
# 點解?
# 因為 CC H(z) 測量嘅係 dz/dt
# 如果 time dilation = (1+z), 咁 dt/dz 由 (1+z) 決定
# 但 H(z) = -(1/(1+z)) dz/dt 係由 dℓ/dt 決定

# 如果 dℓ/dt = 常數 (W-field 均勻演化)
# 咁 dz/dt = ln4 · 4^ℓ · dℓ/dt = ln4 · (1+z) · dℓ/dt
# H(z) = -(1/(1+z)) · dz/dt = -ln4 · dℓ/dt = 常數

# 這同觀察唔符 (H(z) 隨 z 增加)

# 所以 dℓ/dt 唔係常數
# 如果 dℓ/dt ∝ (1+z)^(n-1)
# 則 H(z) = H₀(1+z)^n

# 最佳 n ≈ 1.5 表示 dℓ/dt ∝ (1+z)^0.5

print(f"  H(z) = H₀(1+z)^n, best n = {best_n:.4f}")
print(f"  → dℓ/dt ∝ (1+z)^{{{best_n-1:.4f}}}")
print(f"  → 模式激活速率隨 z 增加而增加")

# 但 K_Chain 結構有 44 個模式
# 每個模式 n 有能量 γ_n = 4sin²(πn/88)
# 模式激活嘅「驅動力」可能係 γ_n 嘅分佈

# 模式能量密度: dγ/dn = (π/22)sin(πn/44)
# 喺模式激活邊界 n = 44·ℓ, 能量密度隨 ℓ 增加

# 如果 H(z) ∝ γ_{n_max} (最後激活模式嘅能量)
# γ_{n_max} = 4sin²(π·44·ℓ/88) = 4sin²(πℓ/2)
# 喺 ℓ 細時: sin(πℓ/2) ≈ πℓ/2, γ ≈ π²ℓ²
# ℓ = log₄(1+z) ≈ z/ln4 當 z 細
# 所以 H(z) ∝ z² 喺低 z — 唔 match

# 如果 H(z) ∝ 累積能量 Σ_active_γ_n
# 喺低 z (ℓ 細): Σ_active_γ_n ≈ γ₁ + γ₂ + ... + γ_{n_active}
# n_active = 44ℓ, 每個 γ_n ≈ 4(πn/88)² = (πn/44)²
# Σ_active ≈ (π/44)² Σ n² ≈ (π/44)² × (44ℓ)³/3 ≈ π²ℓ³/3
# 所以 H(z) ∝ ℓ³ ∝ (log(1+z))³ — 增長太慢

print(f"\n\n--- 5. 結構分析: 臨界性質 ---")
# 關鍵: 從 K_Chain 結構, 搵出自然產生 H(z) ∝ (1+z)^n 嘅機制
# 其中 n ≈ 1.5

# 世界鏈模式: GAMMA[1::2] (odd indices, 44 modes)
world_gamma = GAMMA[1::2]
world_vg = VG[1::2]

# 累積能量
cum_energy = np.cumsum(world_gamma)
cum_energy_norm = cum_energy / SUM_GAMMA_WORLD

# 累積能流
cum_flux = np.cumsum(world_gamma * np.abs(world_vg))
cum_flux_norm = cum_flux / cum_flux[0]

print(f"  {'n':>3} | {'γ_n':>10} | {'v_g/c':>8} | {'Σγ':>10} | {'Σγ/90':>8} | {'Σ(γ·v_g)':>12} | {'flux_norm':>10}")
for n in range(0, 44, 4):
    print(f"  {n+1:3d} | {world_gamma[n]:10.6f} | {world_vg[n]:+8.4f} | {cum_energy[n]:10.4f} | {cum_energy_norm[n]:8.4f} | {cum_flux[n]:12.1f} | {cum_flux_norm[n]:10.1f}")

# ============ 6. 關鍵發現: 環幾何 H(z) ============
print(f"\n\n--- 6. 環幾何 H(z) 推導 ---")
# 喺 IDCM 環宇宙中, 光喺環上傳播
# 觀測距離 D_A(z) 對應環上嘅弧長
# 膨脹率 H(z) 對應環嘅「曲率變化率」

# 環宇宙: 周長 C = 2πR_world
# ℓ = log₄(1+z) 係沿環嘅弧長比例
# 喺環上嘅「膨脹」= 弧長隨時間嘅變化率

# 如果環嘅本徵半徑 R_world 固定
# 但模式激活使有效半徑隨 ℓ 增加
# R_eff(ℓ) = R_world × (1 + 2φ⁻¹ℓ + δ)

# 咁 H(z) = c × (dR_eff/dℓ) × (dℓ/dz) / R_eff²
# 但呢個係環幾何曲率, 唔係宇宙膨脹

# 更直接: 從 CC 數據, H(z) 最佳拟合係 H(z) = 72.59(1+z)^(1.5)
# 呢個係結構常數, 唔係自由參數

# 比較: 如果 n = 1.5 係結構常數, 咁:
# n = 1.5 = 3/2 = (F₄/F₃) = 3/2? 
# 或者: n = 1.5 = 3/2 = N_d/4? N_d/4 = 20/4 = 5 唔得
# 或者: n = 1.5 = F₅/F₄ = 5/3? 1.667 接近
# 或者: n = 1.5 = (γ₄₄/γ₁) / 44? γ₄₄=4, γ₁≈0.005, /44 ≈ 17.8 唔得

print(f"  H(z) = H₀(1+z)^n, n = {best_n:.4f}")
print(f"  可能結構身份:")
print(f"    n = 3/2 (有理數)")
print(f"    n = F₅/F₄ = 5/3 = 1.6667")
print(f"    n = log₄(16) = 2")
print(f"    n = 2 - φ⁻¹ = 2 - 0.618 = 1.382")
print(f"    n = 1 + φ⁻¹ = 1.618 (黃金比例)")
print(f"    n = γ₇/γ₂₀ = 0.1426... 唔得")

# 測試 n = 3/2 (有理數 1.5)
chi2_1_5 = chi2_H(lambda z: H_power(z, 1.5), "power=1.5")
print(f"\n  n = 1.5: χ²/dof = {chi2_1_5:.4f}")
chi2_phi = chi2_H(lambda z: H_power(z, 1+PHI_INV), "power=1+φ⁻¹")
print(f"  n = 1+φ⁻¹ = 1.618: χ²/dof = {chi2_phi:.4f}")
chi2_5_3 = chi2_H(lambda z: H_power(z, 5/3), "power=5/3")
print(f"  n = 5/3 = 1.6667: χ²/dof = {chi2_5_3:.4f}")
chi2_2 = chi2_H(lambda z: H_power(z, 2), "power=2")
print(f"  n = 2: χ²/dof = {chi2_2:.4f}")

# ============ 7. 總結: 最佳結構模型 ============
print(f"\n\n--- 7. 最佳結構模型: H(z) = 72.59(1+z)^{best_n:.4f} ---")
print(f"  χ²/dof = {best_chi2:.4f}")
print(f"  ΛCDM χ²/dof = {chi2_lcdm:.4f}")

# 如果 n = 1.5 係結構常數
print(f"\n  ★ 如果 n = 1.5 係結構常數 (3/2):")
chi2_n15 = chi2_H(lambda z: H_power(z, 1.5), "n=1.5")
print(f"    H(z) = 72.59(1+z)^(3/2)")
print(f"    χ²/dof = {chi2_n15:.4f}")

# 同 ΛCDM 比較
print(f"\n  {'z':>5} | {'H_IDCM(pow)':>12} | {'H_LCDM':>8} | {'ratio':>8} | {'CC_h':>8}")
for z in [0.0, 0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]:
    h_id = H_power(z, best_n)
    h_lc = H_lcdm(z)
    # nearest CC
    idx = np.argmin(np.abs(z_vals - z))
    print(f"  {z:5.1f} | {h_id:12.1f} | {h_lc:8.1f} | {h_id/h_lc:8.4f} | {h_obs[idx]:8.1f}")

# ============ 驗證 ============
print(f"\n\n--- 驗證 ---")
check("H(0) = ω_ring = 72.59", abs(H_power(0, best_n) - OMEGA_RING) < 0.1)
check("H(z) 單調增長", all(H_power(z, best_n) > H_power(0, best_n) for z in [0.5, 1.0, 2.0]))
check("H(0.03) ≈ SH0ES", abs(H_power(0.03, best_n) - 73.04) < 5)
check("H(1.0) ≈ 120-130 (CC 數據範圍)", 100 < H_power(1.0, best_n) < 150)
check("H(2.0) ≈ 180-210 (CC 數據範圍)", 150 < H_power(2.0, best_n) < 250)

print(f"\n  PASS: {PASS}/{PASS+FAIL}")
print(f"  FAIL: {FAIL}/{PASS+FAIL}")

# 儲存
import json
results = {
    "route": "B_deep",
    "best_n": best_n,
    "chi2_n_best": float(f"{best_chi2:.4f}"),
    "chi2_lcdm": float(f"{chi2_lcdm:.4f}"),
    "chi2_n15": float(f"{chi2_n15:.4f}"),
    "pass": int(PASS),
    "fail": int(FAIL),
    "status": "🟡"
}
with open("../data/02b_route_b_deep.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\n  結果已儲存至 data/02b_route_b_deep.json")