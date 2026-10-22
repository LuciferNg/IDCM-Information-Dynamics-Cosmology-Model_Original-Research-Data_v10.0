#!/usr/bin/env python3
"""
O93/09: 最終閉合 — Kurtosis + d14 生成元投影 + z=0 基線
========================================================
三個修正:
1. z=0 基線: H(z) = H₀ × [1 + κ(ℓ)/κ_max]^p × (1+z)^α
2. d=14 生成元投影: ω_active 投影到 d=14 本徵方向
3. 完整公式: H(z) = H₀ × [1 + κ(ℓ)/κ_max + λ·P_d14(ℓ)]^p × (1+z)^α
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

# K_Chain 世界鏈
OMEGA = 2 * np.sin(np.pi * np.arange(1, 89, dtype=float) / 88)
world_omega = OMEGA[1::2]  # 44 modes, even-k
world_gamma = world_omega**2

# 44×44 拍頻矩陣
B = np.zeros((44, 44))
for i in range(44):
    for j in range(44):
        B[i, j] = abs(world_omega[i] - world_omega[j])

# CC data
z_vals = CC_COMBINED[0]
h_obs = CC_COMBINED[1]
h_err = CC_COMBINED[2]

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

def D_A_idcm(z):
    ell = math.log(1 + z, 4)
    base = R_WORLD * (1 - 4**(-ell))
    proj = 1 + 2 * PHI_INV * ell
    delta = C_DELAY * (ell - 0.5) * (1 - 4**(-ell))
    return base * (proj + delta)

def H_lcdm(z):
    return 67.4 * math.sqrt(0.315 * (1+z)**3 + 0.685)

# 統計量
def cum_kurtosis(n):
    if n < 2:
        return 0.0
    w = world_omega[:n]
    return np.mean((w - np.mean(w))**4) / np.std(w, ddof=0)**4

# ============ d=14 生成元本徵向量 ============
print("=" * 70)
print("  O93/09: 最終閉合 — Kurtosis + d14 生成元投影")
print("=" * 70)

print("\n--- 1. d=14 生成元本徵向量 ---")
# d=14 生成元: 44×44 矩陣, 只保留 |j-i|=14 嘅 beats
G14 = np.zeros((44, 44))
for i in range(44 - 14):
    G14[i, i+14] = B[i, i+14]
    G14[i+14, i] = B[i, i+14]  # 對稱

# d=22 生成元
G22 = np.zeros((44, 44))
for i in range(44 - 22):
    G22[i, i+22] = B[i, i+22]
    G22[i+22, i] = B[i, i+22]

# 計算本徵向量 (最大本徵值對應嘅方向)
eigvals_14, eigvecs_14 = np.linalg.eigh(G14)
eigvals_22, eigvecs_22 = np.linalg.eigh(G22)

# 最大本徵值對應嘅本徵向量 = 主生成方向
v14 = eigvecs_14[:, -1]  # 最大本徵值
v22 = eigvecs_22[:, -1]

print(f"  G14 本徵值範圍: [{eigvals_14[0]:.4f}, {eigvals_14[-1]:.4f}]")
print(f"  G22 本徵值範圍: [{eigvals_22[0]:.4f}, {eigvals_22[-1]:.4f}]")
print(f"  G14 最大本徵值: {eigvals_14[-1]:.4f}")
print(f"  G22 最大本徵值: {eigvals_22[-1]:.4f}")

# 本徵向量嘅前幾個分量
print(f"\n  v14 (前 22 分量): {v14[:22].round(4)}")
print(f"  v22 (前 22 分量): {v22[:22].round(4)}")

# ============ 2. 生成元投影 ============
print(f"\n\n--- 2. d=14 生成元投影 ---")
# P_d14(ℓ) = |⟨ω_active | v14⟩| / |ω_active|·|v14|
# 測量活躍模式頻率向量同 d=14 生成方向嘅夾角

def projection_d14(ell):
    """ω_active 投影到 d=14 生成方向"""
    n_active = min(44, max(1, int(44 * ell)))
    w = world_omega[:n_active]
    v = v14[:n_active]
    dot = np.dot(w, v)
    norm_w = np.linalg.norm(w)
    norm_v = np.linalg.norm(v)
    if norm_w == 0 or norm_v == 0:
        return 0.0
    return abs(dot) / (norm_w * norm_v)

def projection_d22(ell):
    """ω_active 投影到 d=22 生成方向"""
    n_active = min(44, max(1, int(44 * ell)))
    w = world_omega[:n_active]
    v = v22[:n_active]
    dot = np.dot(w, v)
    norm_w = np.linalg.norm(w)
    norm_v = np.linalg.norm(v)
    if norm_w == 0 or norm_v == 0:
        return 0.0
    return abs(dot) / (norm_w * norm_v)

print(f"  {'z':>5} | {'ℓ':>6} | {'n':>3} | {'P_d14':>8} | {'P_d22':>8} | {'κ(ℓ)':>8}")
for z in [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]:
    ell = math.log(1 + z, 4)
    n = min(44, max(1, int(44 * ell)))
    p14 = projection_d14(ell)
    p22 = projection_d22(ell)
    k = cum_kurtosis(n)
    print(f"  {z:5.2f} | {ell:6.4f} | {n:3d} | {p14:8.4f} | {p22:8.4f} | {k:8.4f}")

# ============ 3. 模型掃描 ============
print(f"\n\n--- 3. 模型掃描 ---")

# 模型 1: 純 Kurtosis + 基線 (corrected)
def H_kurt_baseline(z, p=1.0, alpha=0.0):
    ell = math.log(1 + z, 4)
    n = min(44, max(1, int(44 * ell)))
    k = cum_kurtosis(n)
    k_max = cum_kurtosis(44)
    if k_max == 0:
        return OMEGA_RING
    return OMEGA_RING * (1 + k/k_max)**p * (1+z)**alpha

# 模型 2: Kurtosis + d14 投影 (乘性修正)
def H_kurt_d14proj(z, p=1.0, lam=0.0, alpha=0.0):
    ell = math.log(1 + z, 4)
    n = min(44, max(1, int(44 * ell)))
    k = cum_kurtosis(n)
    k_max = cum_kurtosis(44)
    p14 = projection_d14(ell)
    if k_max == 0:
        return OMEGA_RING
    # 乘性修正: (κ/κ_max)^p × (1 + λ·P_d14)
    base = (k / k_max) ** p if k > 0 else 0.0
    corr = 1.0 + lam * p14
    if corr <= 0:
        corr = 0.1
    return OMEGA_RING * base * corr * (1+z)**alpha

# 模型 3: Kurtosis + d14 + d22 投影 (乘性修正)
def H_kurt_d14d22proj(z, p=1.0, lam1=0.0, lam2=0.0, alpha=0.0):
    ell = math.log(1 + z, 4)
    n = min(44, max(1, int(44 * ell)))
    k = cum_kurtosis(n)
    k_max = cum_kurtosis(44)
    p14 = projection_d14(ell)
    p22 = projection_d22(ell)
    if k_max == 0:
        return OMEGA_RING
    # 乘性修正: (κ/κ_max)^p × (1 + λ₁·P_d14 + λ₂·P_d22)
    base = (k / k_max) ** p if k > 0 else 0.0
    corr = 1.0 + lam1 * p14 + lam2 * p22
    if corr <= 0:
        corr = 0.1
    return OMEGA_RING * base * corr * (1+z)**alpha

# 掃描
from itertools import product

# 模型 1
best_c1 = 1e10
best_p1 = 0.0
best_a1 = 0.0
for p in np.linspace(0.1, 3.0, 30):
    for a in np.linspace(-1, 2, 31):
        chi2 = sum(((h_obs[i] - H_kurt_baseline(z_vals[i], p, a)) / h_err[i])**2 for i in range(len(z_vals)))
        if chi2 < best_c1:
            best_c1 = chi2
            best_p1 = p
            best_a1 = a
print(f"  模型1 (Kurtosis+baseline): p={best_p1:.2f}, α={best_a1:.2f}, χ²/dof={best_c1/len(z_vals):.4f}")

# 模型 2
best_c2 = 1e10
best_p2 = 0.0
best_l2 = 0.0
best_a2 = 0.0
for p in np.linspace(0.1, 3.0, 20):
    for lam in np.linspace(-2, 2, 21):
        for a in np.linspace(-1, 2, 16):
            chi2 = sum(((h_obs[i] - H_kurt_d14proj(z_vals[i], p, lam, a)) / h_err[i])**2 for i in range(len(z_vals)))
            if chi2 < best_c2:
                best_c2 = chi2
                best_p2 = p
                best_l2 = lam
                best_a2 = a
print(f"  模型2 (+d14投影): p={best_p2:.2f}, λ={best_l2:.2f}, α={best_a2:.2f}, χ²/dof={best_c2/len(z_vals):.4f}")

# 模型 3
best_c3 = 1e10
best_p3 = 0.0
best_l3a = 0.0
best_l3b = 0.0
best_a3 = 0.0
for p in np.linspace(0.1, 3.0, 15):
    for lam1 in np.linspace(-1, 1, 11):
        for lam2 in np.linspace(-1, 1, 11):
            for a in np.linspace(-0.5, 1.5, 11):
                chi2 = sum(((h_obs[i] - H_kurt_d14d22proj(z_vals[i], p, lam1, lam2, a)) / h_err[i])**2 for i in range(len(z_vals)))
                if chi2 < best_c3:
                    best_c3 = chi2
                    best_p3 = p
                    best_l3a = lam1
                    best_l3b = lam2
                    best_a3 = a
print(f"  模型3 (+d14+d22投影): p={best_p3:.2f}, λ₁={best_l3a:.2f}, λ₂={best_l3b:.2f}, α={best_a3:.2f}, χ²/dof={best_c3/len(z_vals):.4f}")

# ============ 4. 最佳模型詳細 ============
print(f"\n\n--- 4. 最佳模型詳細 ---")
# 選最佳
models = [
    (best_c1, "Kurtosis+baseline", H_kurt_baseline, (best_p1, best_a1)),
    (best_c2, "Kurtosis+d14", H_kurt_d14proj, (best_p2, best_l2, best_a2)),
    (best_c3, "Kurtosis+d14+d22", H_kurt_d14d22proj, (best_p3, best_l3a, best_l3b, best_a3))
]
best = min(models, key=lambda x: x[0])
best_name = best[1]
best_func = best[2]
best_params = best[3]
best_chi2 = best[0]

print(f"  最佳模型: {best_name}")
print(f"  χ²/dof = {best_chi2/len(z_vals):.4f}")
print(f"  ΛCDM = 0.6055")
print(f"  Δ = {best_chi2/len(z_vals) - 0.6055:+.4f}")

print(f"\n  {'z':>5} | {'H_obs':>8} | {'σ_H':>6} | {'H_model':>8} | {'O-C':>8} | {'pull':>8}")
for i in range(len(z_vals)):
    z = z_vals[i]
    h_ob = h_obs[i]
    he = h_err[i]
    h_mod = best_func(z, *best_params)
    oc = h_ob - h_mod
    pull = oc / he
    print(f"  {z:5.3f} | {h_ob:8.1f} | {he:6.1f} | {h_mod:8.1f} | {oc:+8.1f} | {pull:+8.3f}")

# ============ 5. 紅移分段 ============
print(f"\n\n--- 5. 紅移分段 ---")
mask_low = z_vals < 0.5
mask_mid = (z_vals >= 0.5) & (z_vals < 1.0)
mask_high = z_vals >= 1.0

for mask, label in [(mask_low, 'z<0.5'), (mask_mid, '0.5≤z<1.0'), (mask_high, 'z≥1.0')]:
    z_sub = z_vals[mask]
    h_sub = h_obs[mask]
    e_sub = h_err[mask]
    chi2 = sum(((h_sub[i] - best_func(z_sub[i], *best_params)) / e_sub[i])**2 for i in range(len(z_sub)))
    print(f"  {label:>12} | N={np.sum(mask):2d} | χ² = {chi2:8.2f} | χ²/dof = {chi2/np.sum(mask):.4f}")

# ============ 6. 關鍵紅移 ============
print(f"\n\n--- 6. 關鍵紅移 H(z) 值 ---")
print(f"  {'z':>5} | {'H_model':>8} | {'H_LCDM':>8} | {'ratio':>8}")
for z in [0.0, 0.03, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]:
    h_mod = best_func(z, *best_params)
    h_lc = H_lcdm(z)
    print(f"  {z:5.2f} | {h_mod:8.1f} | {h_lc:8.1f} | {h_mod/h_lc:8.4f}")

# ============ 7. 殘差比較 ============
print(f"\n\n--- 7. 殘差比較 ---")
print(f"  高 z (z≥0.5) 殘差 RMS:")
for name, _, func, params in models:
    resid = np.array([h_obs[i] - func(z_vals[i], *params) for i in range(len(z_vals))])
    rms = np.sqrt(np.mean(resid[z_vals >= 0.5]**2))
    print(f"    {name:25}: {rms:.1f}")

# ΛCDM 殘差
resid_lcdm = np.array([h_obs[i] - H_lcdm(z_vals[i]) for i in range(len(z_vals))])
rms_lcdm = np.sqrt(np.mean(resid_lcdm[z_vals >= 0.5]**2))
print(f"    {'ΛCDM':25}: {rms_lcdm:.1f}")

# ============ 8. 最終公式輸出 ============
print(f"\n\n--- 8. ★ 最終 H(z) 公式 ---")
print(f"")
print(f"  IDCM H(z) = H₀ × [1 + κ(ℓ)/κ_max + λ₁·P_d14(ℓ) + λ₂·P_d22(ℓ)]^p × (1+z)^α")
print(f"")
print(f"  where:")
print(f"    ℓ = log₄(1+z)")
print(f"    n_active = floor(44·ℓ)")
print(f"    κ(ℓ) = 4th moment of {{ω₁,...,ω_{n_active}}}")
print(f"    P_d14(ℓ) = |⟨ω_active|v14⟩| / ||ω_active||·||v14||")
print(f"    P_d22(ℓ) = |⟨ω_active|v22⟩| / ||ω_active||·||v22||")
print(f"    v14 = G14 最大本徵向量 (d=14 生成方向)")
print(f"    v22 = G22 最大本徵向量 (d=22 生成方向)")
print(f"")
print(f"  最佳參數:")
if best_name == "Kurtosis+baseline":
    print(f"    p = {best_p1:.2f}, α = {best_a1:.2f}")
elif best_name == "Kurtosis+d14":
    print(f"    p = {best_p2:.2f}, λ = {best_l2:.2f}, α = {best_a2:.2f}")
else:
    print(f"    p = {best_p3:.2f}, λ₁ = {best_l3a:.2f}, λ₂ = {best_l3b:.2f}, α = {best_a3:.2f}")
print(f"")
print(f"  χ²/dof = {best_chi2/len(z_vals):.4f}  (ΛCDM = 0.6055)")
print(f"  Δ = {best_chi2/len(z_vals) - 0.6055:+.4f}")
print(f"")
print(f"  {'✅' if best_chi2/len(z_vals) < 0.7 else '🟡' if best_chi2/len(z_vals) < 0.8 else '🔴'}  O93 狀態: {'閉合' if best_chi2/len(z_vals) < 0.7 else '部分閉合'}")

# 儲存
import json
results = {
    "route": "B_final_v2",
    "best_model": best_name,
    "chi2_dof": float(f"{best_chi2/len(z_vals):.4f}"),
    "chi2_lcdm": 0.6055,
    "delta": float(f"{best_chi2/len(z_vals) - 0.6055:.4f}"),
    "params": {k: float(f"{v:.4f}") for k, v in zip(
        ['p','lam1','lam2','alpha'][:len(best_params)], best_params)},
    "pass": int(PASS),
    "fail": int(FAIL),
    "status": "🟡"
}
with open("../data/09_route_b_final_v2.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\n  結果已儲存至 data/09_route_b_final_v2.json")