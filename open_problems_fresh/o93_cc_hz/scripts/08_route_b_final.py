#!/usr/bin/env python3
"""
O93/08: 符號內積 — κ_ω 同 d=14 GEN 雙線性型
=============================================
正確嘅「符號內積」= 雙線性型 (bilinear form):
  ⟨κ_ω | d14 | κ_ω⟩ = Σ_i κ_ω(i) × B(i,i+14) × κ_ω(i+14)

唔係之前嘅線性投影 (κ_ω · d14_weight)！
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
world_omega = OMEGA[1::2]  # 44 modes
world_gamma = world_omega**2

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

# 統計量函數
def cum_stats(n):
    if n < 2:
        return {'mean': 0, 'std': 0, 'skew': 0, 'kurt': 0}
    w = world_omega[:n]
    mean = np.mean(w)
    std = np.std(w, ddof=0)
    skew = np.mean((w - mean)**3) / std**3 if std > 0 else 0
    kurt = np.mean((w - mean)**4) / std**4 if std > 0 else 0
    return {'mean': mean, 'std': std, 'skew': skew, 'kurt': kurt}

print("=" * 70)
print("  O93/08: 符號內積 — κ_ω 同 d=14 GEN 雙線性型")
print("=" * 70)

# ============ 1. 雙線性型定義 ============
print("\n--- 1. 雙線性型 ⟨κ_ω | d14 | κ_ω⟩ ---")

def bilinear_d14(ell):
    """κ_ω 同 d=14 嘅雙線性內積"""
    n_active = min(44, max(1, int(44 * ell)))
    if n_active < 2:
        return 0.0
    total = 0.0
    weight = 0.0
    for i in range(n_active - 14):
        j = i + 14
        if j >= n_active:
            break
        ki = cum_stats(i+1)['kurt']
        kj = cum_stats(j+1)['kurt']
        beat = B[i, j]
        total += ki * beat * kj
        weight += beat
    return total / weight if weight > 0 else 0.0

def bilinear_d22(ell):
    """κ_ω 同 d=22 嘅雙線性內積"""
    n_active = min(44, max(1, int(44 * ell)))
    if n_active < 2:
        return 0.0
    total = 0.0
    weight = 0.0
    for i in range(n_active - 22):
        j = i + 22
        if j >= n_active:
            break
        ki = cum_stats(i+1)['kurt']
        kj = cum_stats(j+1)['kurt']
        beat = B[i, j]
        total += ki * beat * kj
        weight += beat
    return total / weight if weight > 0 else 0.0

# 顯示雙線性型值
print(f"  {'z':>5} | {'ℓ':>6} | {'n':>3} | {'⟨κ|d14|κ⟩':>12} | {'⟨κ|d22|κ⟩':>12} | {'κ(ℓ)':>8}")
for z in [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]:
    ell = math.log(1 + z, 4)
    n = min(44, max(1, int(44 * ell)))
    b14 = bilinear_d14(ell)
    b22 = bilinear_d22(ell)
    k = cum_stats(n)['kurt']
    print(f"  {z:5.1f} | {ell:6.4f} | {n:3d} | {b14:12.4f} | {b22:12.4f} | {k:8.4f}")

# ============ 2. 純 Kurtosis 模型 (baseline) ============
print(f"\n\n--- 2. 純 Kurtosis 模型 (baseline) ---")

def H_kurt(z, p=1.0, alpha=0.0):
    ell = math.log(1 + z, 4)
    n = min(44, max(1, int(44 * ell)))
    k = cum_stats(n)['kurt']
    k_max = cum_stats(44)['kurt']
    if k_max == 0:
        return OMEGA_RING
    return OMEGA_RING * (k / k_max)**p * (1+z)**alpha

# 掃描純 Kurtosis 最佳
best_pk = 0.0
best_ak = 0.0
best_ck = 1e10
for p in np.linspace(0.05, 2.0, 40):
    for a in np.linspace(-1, 3, 41):
        chi2 = sum(((h_obs[i] - H_kurt(z_vals[i], p, a)) / h_err[i])**2 for i in range(len(z_vals)))
        if chi2 < best_ck:
            best_ck = chi2
            best_pk = p
            best_ak = a

print(f"  最佳 p={best_pk:.2f}, α={best_ak:.2f}, χ²/dof={best_ck/len(z_vals):.4f}")

# ============ 3. Kurtosis + d14 雙線性修正 ============
print(f"\n\n--- 3. Kurtosis + d14 雙線性修正 ---")
# H(z) = H₀ × [κ(ℓ) + λ × ⟨κ|d14|κ⟩(ℓ)] × (1+z)^α

def H_kurt_d14_bilin(z, lam=0.0, alpha=0.0):
    ell = math.log(1 + z, 4)
    n = min(44, max(1, int(44 * ell)))
    k = cum_stats(n)['kurt']
    k_max = cum_stats(44)['kurt']
    b14 = bilinear_d14(ell)
    if k_max == 0:
        return OMEGA_RING
    return OMEGA_RING * (k/k_max + lam * b14) * (1+z)**alpha

best_l = 0.0
best_a = 0.0
best_c = 1e10
for lam in np.linspace(-2, 2, 41):
    for a in np.linspace(-1, 3, 41):
        chi2 = sum(((h_obs[i] - H_kurt_d14_bilin(z_vals[i], lam, a)) / h_err[i])**2 for i in range(len(z_vals)))
        if chi2 < best_c:
            best_c = chi2
            best_l = lam
            best_a = a

print(f"  最佳 λ={best_l:.2f}, α={best_a:.2f}, χ²/dof={best_c/len(z_vals):.4f}")

# 詳細
chi2_best = 0.0
print(f"\n  {'z':>5} | {'H_obs':>8} | {'σ_H':>6} | {'H_model':>8} | {'O-C':>8} | {'pull':>8}")
for i in range(len(z_vals)):
    z = z_vals[i]
    h_ob = h_obs[i]
    he = h_err[i]
    h_mod = H_kurt_d14_bilin(z, best_l, best_a)
    oc = h_ob - h_mod
    pull = oc / he
    chi2_best += pull**2
    print(f"  {z:5.3f} | {h_ob:8.1f} | {he:6.1f} | {h_mod:8.1f} | {oc:+8.1f} | {pull:+8.3f}")

# ============ 4. d22 雙線性修正 ============
print(f"\n\n--- 4. Kurtosis + d22 雙線性修正 ---")

def H_kurt_d22_bilin(z, lam=0.0, alpha=0.0):
    ell = math.log(1 + z, 4)
    n = min(44, max(1, int(44 * ell)))
    k = cum_stats(n)['kurt']
    k_max = cum_stats(44)['kurt']
    b22 = bilinear_d22(ell)
    if k_max == 0:
        return OMEGA_RING
    return OMEGA_RING * (k/k_max + lam * b22) * (1+z)**alpha

best_l2 = 0.0
best_a2 = 0.0
best_c2 = 1e10
for lam in np.linspace(-2, 2, 41):
    for a in np.linspace(-1, 3, 41):
        chi2 = sum(((h_obs[i] - H_kurt_d22_bilin(z_vals[i], lam, a)) / h_err[i])**2 for i in range(len(z_vals)))
        if chi2 < best_c2:
            best_c2 = chi2
            best_l2 = lam
            best_a2 = a

print(f"  最佳 λ={best_l2:.2f}, α={best_a2:.2f}, χ²/dof={best_c2/len(z_vals):.4f}")

# ============ 5. d14 + d22 雙重修正 ============
print(f"\n\n--- 5. d14 + d22 雙重雙線性修正 ---")

def H_kurt_d14d22(z, lam1=0.0, lam2=0.0, alpha=0.0):
    ell = math.log(1 + z, 4)
    n = min(44, max(1, int(44 * ell)))
    k = cum_stats(n)['kurt']
    k_max = cum_stats(44)['kurt']
    b14 = bilinear_d14(ell)
    b22 = bilinear_d22(ell)
    if k_max == 0:
        return OMEGA_RING
    return OMEGA_RING * (k/k_max + lam1 * b14 + lam2 * b22) * (1+z)**alpha

best_c3 = 1e10
best_l1 = 0.0
best_l2 = 0.0
best_a3 = 0.0
for lam1 in np.linspace(-1, 1, 21):
    for lam2 in np.linspace(-1, 1, 21):
        for a in np.linspace(-0.5, 1.5, 21):
            chi2 = sum(((h_obs[i] - H_kurt_d14d22(z_vals[i], lam1, lam2, a)) / h_err[i])**2 for i in range(len(z_vals)))
            if chi2 < best_c3:
                best_c3 = chi2
                best_l1 = lam1
                best_l2 = lam2
                best_a3 = a

print(f"  最佳 λ₁={best_l1:.2f}, λ₂={best_l2:.2f}, α={best_a3:.2f}, χ²/dof={best_c3/len(z_vals):.4f}")

# 詳細
print(f"\n  {'z':>5} | {'H_obs':>8} | {'σ_H':>6} | {'H_model':>8} | {'O-C':>8} | {'pull':>8}")
chi2_dd = 0.0
for i in range(len(z_vals)):
    z = z_vals[i]
    h_ob = h_obs[i]
    he = h_err[i]
    h_mod = H_kurt_d14d22(z, best_l1, best_l2, best_a3)
    oc = h_ob - h_mod
    pull = oc / he
    chi2_dd += pull**2
    print(f"  {z:5.3f} | {h_ob:8.1f} | {he:6.1f} | {h_mod:8.1f} | {oc:+8.1f} | {pull:+8.3f}")

# ============ 6. 殘差分析 ============
print(f"\n\n--- 6. 殘差分析 ---")
print(f"  {'z':>5} | {'res_kurt':>8} | {'res_k+d14':>8} | {'res_k+d14d22':>8} | {'res_LCDM':>8}")

for i in range(len(z_vals)):
    z = z_vals[i]
    rk = h_obs[i] - H_kurt(z, best_pk, best_ak)
    rk14 = h_obs[i] - H_kurt_d14_bilin(z, best_l, best_a)
    rkdd = h_obs[i] - H_kurt_d14d22(z, best_l1, best_l2, best_a3)
    rl = h_obs[i] - H_lcdm(z)
    print(f"  {z:5.3f} | {rk:+8.1f} | {rk14:+8.1f} | {rkdd:+8.1f} | {rl:+8.1f}")

# 高 z 殘差
high_z = z_vals >= 0.5
print(f"\n  高 z (z≥0.5) 殘差 RMS:")
rk_arr = np.array([h_obs[i] - H_kurt(z_vals[i], best_pk, best_ak) for i in range(len(z_vals))])
rk14_arr = np.array([h_obs[i] - H_kurt_d14_bilin(z_vals[i], best_l, best_a) for i in range(len(z_vals))])
rkdd_arr = np.array([h_obs[i] - H_kurt_d14d22(z_vals[i], best_l1, best_l2, best_a3) for i in range(len(z_vals))])
rl_arr = np.array([h_obs[i] - H_lcdm(z_vals[i]) for i in range(len(z_vals))])

print(f"    Kurtosis:     {np.sqrt(np.mean(rk_arr[high_z]**2)):.1f}")
print(f"    K+d14:        {np.sqrt(np.mean(rk14_arr[high_z]**2)):.1f}")
print(f"    K+d14+d22:    {np.sqrt(np.mean(rkdd_arr[high_z]**2)):.1f}")
print(f"    ΛCDM:         {np.sqrt(np.mean(rl_arr[high_z]**2)):.1f}")

# ============ 7. 比較 ============
print(f"\n\n--- 7. χ² 比較 ---")
print(f"  {'模型':>40} | {'χ²/dof':>10} | {'Δχ²':>8} | {'判定':>6}")
print(f"  {'-'*40} | {'-'*10} | {'-'*8} | {'-'*6}")
print(f"  {'ΛCDM (target)':>40} | {sum(((h_obs[i]-H_lcdm(z_vals[i]))/h_err[i])**2 for i in range(len(z_vals)))/len(z_vals):10.4f} | {'—':>8} | {'🟢':>6}")
print(f"  {'Kurtosis (純)':>40} | {best_ck/len(z_vals):10.4f} | {(best_ck-best_ck)/len(z_vals):+8.4f} | {'🟡':>6}")
print(f"  {'Kurtosis + d14 bilinear':>40} | {best_c/len(z_vals):10.4f} | {(best_c-best_ck)/len(z_vals):+8.4f} | {'🟡' if best_c<best_ck else '🔴':>6}")
print(f"  {'Kurtosis + d22 bilinear':>40} | {best_c2/len(z_vals):10.4f} | {(best_c2-best_ck)/len(z_vals):+8.4f} | {'🟡' if best_c2<best_ck else '🔴':>6}")
print(f"  {'Kurtosis + d14+d22':>40} | {best_c3/len(z_vals):10.4f} | {(best_c3-best_ck)/len(z_vals):+8.4f} | {'🟡' if best_c3<best_ck else '🔴':>6}")

# ============ 8. 最終 H(z) 公式 ============
print(f"\n\n--- 8. 最終 H(z) 公式 ---")
# 用最佳模型輸出公式
chosen = "kurtosis+d14+d22"
if best_c3 < best_c and best_c3 < best_ck and best_c3 < best_c2:
    chosen = "kurtosis+d14+d22"
    params = (best_l1, best_l2, best_a3)
    chi2_val = best_c3/len(z_vals)
elif best_c < best_ck and best_c < best_c2:
    chosen = "kurtosis+d14"
    params = (best_l, best_a)
    chi2_val = best_c/len(z_vals)
elif best_c2 < best_ck:
    chosen = "kurtosis+d22"
    params = (best_l2, best_a2)
    chi2_val = best_c2/len(z_vals)
else:
    chosen = "kurtosis"
    params = (best_pk, best_ak)
    chi2_val = best_ck/len(z_vals)

print(f"  最佳模型: {chosen}")
print(f"  χ²/dof = {chi2_val:.4f}")
print(f"  ΛCDM = 0.6055")
print(f"  Δ = {chi2_val - 0.6055:+.4f}")

if chosen == "kurtosis+d14+d22":
    print(f"\n  H(z) = H₀ × [κ(ℓ)/κ_max + {best_l1:.2f}·⟨κ|d14|κ⟩ + {best_l2:.2f}·⟨κ|d22|κ⟩] × (1+z)^{best_a3:.2f}")
elif chosen == "kurtosis+d14":
    print(f"\n  H(z) = H₀ × [κ(ℓ)/κ_max + {best_l:.2f}·⟨κ|d14|κ⟩] × (1+z)^{best_a:.2f}")
else:
    print(f"\n  H(z) = H₀ × [κ(ℓ)/κ_max]^{best_pk:.2f} × (1+z)^{best_ak:.2f}")

# 關鍵紅移值
print(f"\n  關鍵紅移 H(z) 值:")
print(f"  {'z':>5} | {'H(z)':>8} | {'H_LCDM':>8} | {'ratio':>8}")
for z in [0.0, 0.03, 0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]:
    if chosen == "kurtosis+d14+d22":
        h = H_kurt_d14d22(z, best_l1, best_l2, best_a3)
    elif chosen == "kurtosis+d14":
        h = H_kurt_d14_bilin(z, best_l, best_a)
    elif chosen == "kurtosis+d22":
        h = H_kurt_d22_bilin(z, best_l2, best_a2)
    else:
        h = H_kurt(z, best_pk, best_ak)
    hl = H_lcdm(z)
    print(f"  {z:5.2f} | {h:8.1f} | {hl:8.1f} | {h/hl:8.4f}")

# ============ 最後 ============
print(f"\n{'='*70}")
print(f"  O93 最終: 符號內積閉合")
print(f"  {'='*70}")
print(f"")
print(f"  {'🟢' if chi2_val < 0.7 else '🟡' if chi2_val < 1.0 else '🔴'} 最佳 χ²/dof = {chi2_val:.4f}")
print(f"  {'🟢' if chi2_val - 0.6055 < 0.1 else '🟡' if chi2_val - 0.6055 < 0.3 else '🔴'} 距 ΛCDM Δ = {chi2_val - 0.6055:+.4f}")
print(f"")
print(f"  關鍵公式:")
print(f"  ℓ = log₄(1+z)")
print(f"  n_active = floor(44·ℓ)")
print(f"  κ(ℓ) = 4th moment of ω₁,...,ω_{{n_active}}")
print(f"  ⟨κ|d14|κ⟩ = Σ κ(i)·B(i,i+14)·κ(i+14) / Σ B(i,i+14)")
print(f"  H(z) = H₀ × [κ(ℓ)/κ_max + λ₁·⟨κ|d14|κ⟩ + λ₂·⟨κ|d22|κ⟩] × (1+z)^α")

import json
results = {
    "route": "B_final",
    "best_model": chosen,
    "chi2_dof": float(f"{chi2_val:.4f}"),
    "chi2_lcdm": 0.6055,
    "delta": float(f"{chi2_val - 0.6055:.4f}"),
    "kurtosis_p": float(f"{best_pk:.2f}"),
    "kurtosis_alpha": float(f"{best_ak:.2f}"),
    "kurtosis_chi2": float(f"{best_ck/len(z_vals):.4f}"),
    "d14_lambda": float(f"{best_l:.2f}"),
    "d14_alpha": float(f"{best_a:.2f}"),
    "d14_chi2": float(f"{best_c/len(z_vals):.4f}"),
    "d22_lambda": float(f"{best_l2:.2f}"),
    "d22_alpha": float(f"{best_a2:.2f}"),
    "d22_chi2": float(f"{best_c2/len(z_vals):.4f}"),
    "d14d22_l1": float(f"{best_l1:.2f}"),
    "d14d22_l2": float(f"{best_l2:.2f}"),
    "d14d22_alpha": float(f"{best_a3:.2f}"),
    "d14d22_chi2": float(f"{best_c3/len(z_vals):.4f}"),
    "pass": int(PASS),
    "fail": int(FAIL),
    "status": "🟡"
}
with open("../data/08_route_b_final.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\n  結果已儲存至 data/08_route_b_final.json")