#!/usr/bin/env python3
"""
O93/05: 深入 — K_Chain Beat Decoherence Rate + Magic Vector 鎖定
=================================================================
根據 calibrator 嘅核心洞察重新構建:

1. CC H(z) 測量嘅 dz/dt 中, dt 係 K_Chain 上嘅相位色散去相干率
2. 被動星系光譜年齡差 Δt = 累積拍頻算符嘅和頻項
3. H(z) × D_A(z) 鎖定在 magic vector

關鍵公式猜測:
- H(z) 嘅結構 = 活躍模式嘅拍頻「和頻能量」/ 尺度因子
- 和頻算符 Σ(ω_i + ω_j) 對應宇宙年齡嘅累積
- 乘積 H(z) · D_A(z) · (1+z)^k = 常數 (magic row 鎖定)
"""
import math
import numpy as np
import sys
sys.path.insert(0, '../data')
from cc_hz_data import *

# 常數
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
R_WORLD = 4129.94
C_LIGHT = 299792.458
OMEGA_RING = 72.59
C_DELAY = -0.1697
N_DUAL = 88
N_HALF = 44

# K_Chain 頻率
ns = np.arange(1, N_DUAL + 1, dtype=float)
OMEGA = 2 * np.sin(np.pi * ns / N_DUAL)  # ω_n
GAMMA = OMEGA**2                           # γ_n = ω_n²

# 世界鏈 (even-k, 1-indexed: k=2,4,...,88)
world_omega = OMEGA[1::2]  # 44 modes
world_gamma = GAMMA[1::2]

# 觀察者鏈 (odd-k, 1-indexed: k=1,3,...,87)
obs_omega = OMEGA[::2]
obs_gamma = GAMMA[::2]

SUM_GAMMA_WORLD = 90
SUM_GAMMA_OBS = 88

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

# 44×44 拍頻矩陣
B = np.zeros((44, 44))
for i in range(44):
    for j in range(44):
        B[i, j] = abs(world_omega[i] - world_omega[j])

print("=" * 70)
print("  O93/05: Beat Decoherence Rate + Magic Vector 鎖定")
print("=" * 70)

# ============ 1. Magic Vector 分析 ============
print("\n--- 1. Magic Vector 分析 (d=14, d=22) ---")
# d=14 (GEN 世代行) — 三代 quark 質量比
# d=22 (HALF 半節點) — 對偶對稱

# 收集所有 d=14 嘅拍頻
d14_row = np.array([B[i, i+14] for i in range(44-14)])
d22_row = np.array([B[i, i+22] for i in range(44-22)])

print(f"  d=14 (GEN): {len(d14_row)} beats, mean={d14_row.mean():.6f}, std={d14_row.std():.6f}")
print(f"  d=22 (HALF): {len(d22_row)} beats, mean={d22_row.mean():.6f}, std={d22_row.std():.6f}")
print(f"  d=14/d=22 ratio = {d14_row.mean()/d22_row.mean():.6f}")

# 檢查 d=14 拍頻嘅分佈
print(f"\n  d=14 beat 分佈:")
for i, beat in enumerate(d14_row):
    print(f"    i={i:2d}, j={i+14:2d}: beat={beat:.6f}")

# ============ 2. 和頻累積 ============
print("\n\n--- 2. 和頻累積 — 宇宙年齡對應 ---")
# 宇宙年齡 T(ℓ) = 和頻累積 / 總和頻
# t(ℓ) = Σ_{i<j}^{n_active} (ω_i + ω_j) / Σ_{i<j}^{44} (ω_i + ω_j) × T_sync

T_sync = 84.64  # Gyr (SYNC time)

# 總和頻 (所有 44 模式)
total_sum_omega = 0.0
for i in range(44):
    for j in range(i+1, 44):
        total_sum_omega += world_omega[i] + world_omega[j]

print(f"  總和頻 = {total_sum_omega:.6f}")

# 計算 t(ℓ) 同 H(z) = -(1/(1+z)) dz/dt
print(f"  {'z':>5} | {'ℓ':>6} | {'n_active':>8} | {'Σ(ω_i+ω_j)':>12} | {'t(Gyr)':>8} | {'dt/dz':>10} | {'H_pred':>8} | {'H_obs':>8}")

for z in [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]:
    ell = math.log(1 + z, 4)
    n_active = min(44, max(1, int(44 * ell)))
    
    # 累積和頻
    cum_sum = 0.0
    for i in range(n_active):
        for j in range(i+1, n_active):
            cum_sum += world_omega[i] + world_omega[j]
    
    # 宇宙年齡
    t_age = cum_sum / total_sum_omega * T_sync
    
    # 數值 dt/dz
    if z > 0.01:
        z_prev = z * 0.99
        ell_prev = math.log(1 + z_prev, 4)
        n_prev = min(44, max(1, int(44 * ell_prev)))
        cum_prev = 0.0
        for i in range(n_prev):
            for j in range(i+1, n_prev):
                cum_prev += world_omega[i] + world_omega[j]
        t_prev = cum_prev / total_sum_omega * T_sync
        dt_dz = (t_age - t_prev) / (z - z_prev)
        H_pred = -1 / ((1 + z) * dt_dz) * 977.8  # Convert Gyr⁻¹ to km/s/Mpc
    else:
        dt_dz = 0
        H_pred = OMEGA_RING
    
    # nearest CC obs
    idx = np.argmin(np.abs(z_vals - z))
    h_cc = h_obs[idx] if abs(z_vals[idx] - z) < 0.05 else 0
    
    print(f"  {z:5.1f} | {ell:6.4f} | {n_active:8d} | {cum_sum:12.4f} | {t_age:8.2f} | {dt_dz:10.4f} | {H_pred:8.1f} | {h_cc:8.1f}")

# ============ 3. 關鍵: H(z) · D_A(z) · (1+z)^k = 常數? ============
print(f"\n\n--- 3. ★ 拓撲不變量: H(z) × D_A(z) × (1+z)^k ---")
# 試唔同 k 值, 睇邊個令乘積最接近常數

for k in np.linspace(-2, 2, 17):
    products = []
    for i in range(len(z_vals)):
        z = z_vals[i]
        h_cc = h_obs[i]
        da = D_A_idcm(z)
        prod = h_cc * da * (1+z)**k
        products.append(prod)
    
    prod_arr = np.array(products)
    cv = prod_arr.std() / prod_arr.mean()  # 變異係數
    print(f"  k={k:+.2f}: mean={prod_arr.mean():.0f}, cv={cv:.4f} {'🟢' if cv < 0.5 else '🔴'}")

# 試 k = -1, 0, 1 詳細
for k_test in [-1.0, 0.0, 1.0]:
    print(f"\n  k={k_test:+.0f} 詳細:")
    print(f"    {'z':>5} | {'H×D':>10} | {'(1+z)^k':>8} | {'product':>10}")
    products_k = []
    for i in range(len(z_vals)):
        z = z_vals[i]
        h_cc = h_obs[i]
        da = D_A_idcm(z)
        prod = h_cc * da * (1+z)**k_test
        products_k.append(prod)
        print(f"    {z:5.3f} | {h_cc*da:10.0f} | {(1+z)**k_test:8.4f} | {prod:10.0f}")
    pk = np.array(products_k)
    print(f"    mean={pk.mean():.0f}, cv={pk.std()/pk.mean():.4f}")

# ============ 4. Decohrence Rate 模型 ============
print(f"\n\n--- 4. 解相干率模型 — 活躍拍頻和 = R(ℓ) = Σ|ω_i-ω_j| ---")
# 假設: H(z) = H₀ × (R(ℓ) / R_total) × (1+z)^α
# R(ℓ) = Σ_{i<j}^{n_active} |ω_i - ω_j| (活躍拍頻總和)

def R_active(ell):
    """活躍拍頻總和 R(ℓ)"""
    n_active = min(44, max(1, int(44 * ell)))
    if n_active < 2:
        return 0.0
    total = 0.0
    for i in range(n_active):
        for j in range(i+1, n_active):
            total += B[i, j]
    return total

R_total = R_active(math.log(1 + 10, 4))  # ℓ→∞ 嘅總和

print(f"  總拍頻和 R_total = {R_total:.4f}")

# 掃描 α
best_alpha = 0.0
best_chi2 = 1e10
for alpha in np.linspace(-2, 3, 51):
    chi2 = 0.0
    for i in range(len(z_vals)):
        z = z_vals[i]
        h_ob = h_obs[i]
        he = h_err[i]
        ell = math.log(1 + z, 4)
        R = R_active(ell)
        if R_total > 0:
            h_mod = OMEGA_RING * (R / R_total) * (1+z)**alpha
        else:
            h_mod = OMEGA_RING
        chi2 += ((h_ob - h_mod) / he)**2
    chi2_dof = chi2 / len(z_vals)
    if chi2_dof < best_chi2:
        best_chi2 = chi2_dof
        best_alpha = alpha

print(f"  最佳 α = {best_alpha:.2f}, χ²/dof = {best_chi2:.4f}")

# 詳細顯示最佳模型
print(f"\n  最佳模型 (α={best_alpha:.2f}) 詳細:")
print(f"  {'z':>5} | {'H_obs':>8} | {'σ_H':>6} | {'H_model':>8} | {'O-C':>8}")
for i in range(min(20, len(z_vals))):
    z = z_vals[i]
    h_ob = h_obs[i]
    he = h_err[i]
    ell = math.log(1 + z, 4)
    R = R_active(ell)
    h_mod = OMEGA_RING * (R / R_total) * (1+z)**best_alpha
    print(f"  {z:5.3f} | {h_ob:8.1f} | {he:6.1f} | {h_mod:8.1f} | {h_ob-h_mod:+8.1f}")

# ============ 5. 和頻率模型 ============
print(f"\n\n--- 5. 和頻率模型 — H(z) = H₀ × (Σ_active(ω_i+ω_j) / Σ_total(ω_i+ω_j)) × (1+z)^α ---")
# 另一個模型: 用和頻代替差頻

def S_active(ell):
    """活躍和頻總和 S(ℓ)"""
    n_active = min(44, max(1, int(44 * ell)))
    if n_active < 2:
        return 0.0
    total = 0.0
    for i in range(n_active):
        for j in range(i+1, n_active):
            total += world_omega[i] + world_omega[j]
    return total

S_total = S_active(math.log(1 + 10, 4))

best_alpha2 = 0.0
best_chi2_2 = 1e10
for alpha in np.linspace(-2, 3, 51):
    chi2 = 0.0
    for i in range(len(z_vals)):
        z = z_vals[i]
        h_ob = h_obs[i]
        he = h_err[i]
        ell = math.log(1 + z, 4)
        S = S_active(ell)
        h_mod = OMEGA_RING * (S / S_total) * (1+z)**alpha if S_total > 0 else OMEGA_RING
        chi2 += ((h_ob - h_mod) / he)**2
    chi2_dof = chi2 / len(z_vals)
    if chi2_dof < best_chi2_2:
        best_chi2_2 = chi2_dof
        best_alpha2 = alpha

print(f"  最佳 α = {best_alpha2:.2f}, χ²/dof = {best_chi2_2:.4f}")

# ============ 6. γ_n 加權模型 ============
print(f"\n\n--- 6. K_Chain 能量加權 — H(z) = H₀ × (Σ_active γ_n × ω_n / Σ_total γ_n × ω_n) × (1+z)^α ---")
# 能量 × 頻率加權

def EF_active(ell):
    """活躍能量×頻率總和"""
    n_active = min(44, max(1, int(44 * ell)))
    return np.sum(world_gamma[:n_active] * world_omega[:n_active])

EF_total = EF_active(math.log(1 + 10, 4))

best_alpha3 = 0.0
best_chi2_3 = 1e10
for alpha in np.linspace(-2, 3, 51):
    chi2 = 0.0
    for i in range(len(z_vals)):
        z = z_vals[i]
        h_ob = h_obs[i]
        he = h_err[i]
        ell = math.log(1 + z, 4)
        ef = EF_active(ell)
        h_mod = OMEGA_RING * (ef / EF_total) * (1+z)**alpha if EF_total > 0 else OMEGA_RING
        chi2 += ((h_ob - h_mod) / he)**2
    chi2_dof = chi2 / len(z_vals)
    if chi2_dof < best_chi2_3:
        best_chi2_3 = chi2_dof
        best_alpha3 = alpha

print(f"  最佳 α = {best_alpha3:.2f}, χ²/dof = {best_chi2_3:.4f}")

# ============ 7. 全部模型比較 ============
print(f"\n\n--- 7. 全部模型 χ² 比較 ---")
print(f"  {'模型':>30} | {'最佳α':>6} | {'χ²/dof':>10} | {'判定':>6}")
print(f"  {'-'*30} | {'-'*6} | {'-'*10} | {'-'*6}")
print(f"  {'ΛCDM (reference)':>30} | {'—':>6} | {0.6055:10.4f} | {'🟢':>6}")
print(f"  {'dD_A/dz (FLRW)':>30} | {'—':>6} | {50.78:10.2f} | {'❌':>6}")
print(f"  {'R(ℓ) = Σ|ω_i-ω_j| × (1+z)^α':>30} | {best_alpha:6.2f} | {best_chi2:10.4f} | {'🟡' if best_chi2<5 else '🔴':>6}")
print(f"  {'S(ℓ) = Σ(ω_i+ω_j) × (1+z)^α':>30} | {best_alpha2:6.2f} | {best_chi2_2:10.4f} | {'🟡' if best_chi2_2<5 else '🔴':>6}")
print(f"  {'EF(ℓ) = Σγ·ω × (1+z)^α':>30} | {best_alpha3:6.2f} | {best_chi2_3:10.4f} | {'🟡' if best_chi2_3<5 else '🔴':>6}")

# ============ 8. 關鍵 insight: magic vector 鎖定 ============
print(f"\n\n--- 8. ★ Magic Vector 鎖定分析 ---")
# 睇 H(z) × D_A(z) 嘅變化規律同 magic row 嘅關係
# 如果 H(z) × D_A(z) / (1+z)^(某 magic exponent) = 常數

# 試 d=14: 平均 beat = 0.9317
# 試 d=22: 平均 beat = 1.0543

# H(z) × D_A(z) / (R_world × d14_avg) 應該接近 H(0)?
hd_vals = np.array([h_obs[i] * D_A_idcm(z_vals[i]) for i in range(len(z_vals))])
hd_mean = hd_vals.mean()

# 用 d=14 歸一化
norm_d14 = R_WORLD * d14_row.mean()
norm_d22 = R_WORLD * d22_row.mean()

print(f"  H×D_A mean = {hd_mean:.0f}")
print(f"  R_world × d14_avg = {norm_d14:.0f}")
print(f"  R_world × d22_avg = {norm_d22:.0f}")
print(f"  H×D_A / (R×d14) = {hd_mean / norm_d14:.4f}")
print(f"  H×D_A / (R×d22) = {hd_mean / norm_d22:.4f}")

# 試 H×D_A / (R × d-avg) / (1+z)^k = constant
for d_magic, d_name in [(14, "GEN"), (22, "HALF"), (7, "ANCHOR"), (20, "TRANSFER"), (33, "KTREE")]:
    d_beats = np.array([B[i, i+d_magic] for i in range(44-d_magic)])
    d_avg = d_beats.mean()
    
    for k in np.linspace(-2, 2, 17):
        vals = []
        for i in range(len(z_vals)):
            z = z_vals[i]
            h = h_obs[i]
            da = D_A_idcm(z)
            v = h * da / (R_WORLD * d_avg) / (1+z)**k
            vals.append(v)
        v_arr = np.array(vals)
        cv = v_arr.std() / v_arr.mean()
        if cv < 0.5:
            print(f"  d={d_magic:2d} ({d_name:8}): k={k:+.2f}, mean={v_arr.mean():.4f}, cv={cv:.4f} 🟢")

print(f"\n{'='*70}")
print(f"  總結: 路線 B 深入 — Beat Decoherence + Magic Vector")
print(f"  {'='*70}")
print(f"")
print(f"  最佳模型: R(ℓ) = Σ|ω_i-ω_j| × (1+z)^{best_alpha:.2f}")
print(f"  χ²/dof = {best_chi2:.4f}")
print(f"  ΛCDM χ²/dof = 0.6055")
print(f"")
print(f"  H×D_A 不變量測試:")
print(f"    k=0: cv={hd_vals.std()/hd_vals.mean():.4f}")
print(f"    k=-1: cv={np.std(hd_vals/(1+z_vals))/np.mean(hd_vals/(1+z_vals)):.4f}")

# 儲存
import json
results = {
    "route": "B_deep_v2",
    "best_model": "R_active",
    "best_alpha": float(f"{best_alpha:.2f}"),
    "chi2_R": float(f"{best_chi2:.4f}"),
    "chi2_S": float(f"{best_chi2_2:.4f}"),
    "chi2_EF": float(f"{best_chi2_3:.4f}"),
    "hd_mean": float(f"{hd_mean:.0f}"),
    "hd_cv": float(f"{hd_vals.std()/hd_vals.mean():.4f}"),
    "d14_avg": float(f"{d14_row.mean():.6f}"),
    "d22_avg": float(f"{d22_row.mean():.6f}"),
    "pass": int(PASS),
    "fail": int(FAIL),
    "status": "🟡"
}
with open("../data/05_route_b_deep_v2.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\n  結果已儲存至 data/05_route_b_deep_v2.json")