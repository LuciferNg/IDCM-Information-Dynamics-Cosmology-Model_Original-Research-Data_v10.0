#!/usr/bin/env python3
"""
O93/07: FWM 相角修正 + d=14 GEN 正交投影
===========================================
補齊 0.23 差距嘅兩個結構修正:

1. Quantized Decoupling (FWM 相角):
   - 離散模式激活嘅相位差累積, 唔係連續 Kurtosis
   - 每個新模式激活時, 同之前所有模式嘅 FWM 相位失配 Δβ(n) = Σ|ω_n - ω_i|
   - 總解相干 = Σ Δβ(n) × 階梯函數

2. d=14 GEN 正交投影:
   - κ_ω 投影到 d=14 magic row 嘅 beat pattern
   - d=14 有 30 beats, 對稱分佈, 中心零點
   - 尾部修正 = κ_ω × d14_pattern × (1+z)^α
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

# K_Chain 世界鏈 (44 modes)
OMEGA = 2 * np.sin(np.pi * np.arange(1, 89, dtype=float) / 88)
world_omega = OMEGA[1::2]  # 44 modes, even-k
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

print("=" * 70)
print("  O93/07: FWM 相角修正 + d=14 GEN 正交投影")
print("=" * 70)

# ============ 1. Quantized FWM Phase Mismatch ============
print("\n--- 1. Quantized FWM 相位失配累積 ---")
# FWM 相位失配: Δβ(n) = Σ_{i=1}^{n-1} |ω_n - ω_i|
# 當模式 n 激活, 佢同之前所有模式產生 FWM 拍頻
# 總解相干 = Σ Δβ(n) × Θ(n - n_active)

# 計算每個模式嘅 FWM 相位失配
def fwm_phase_mismatch(n):
    """模式 n 同之前所有模式嘅 FWM 相位失配 (1-indexed)"""
    if n <= 1:
        return 0.0
    omega_n = world_omega[n-1]
    total = 0.0
    for i in range(n-1):
        total += abs(omega_n - world_omega[i])
    return total

# 累積 FWM 解相干
def D_fwm_cum(ell):
    """累積 FWM 解相干"""
    n_active = min(44, max(1, int(44 * ell)))
    total = 0.0
    for n in range(1, n_active + 1):
        total += fwm_phase_mismatch(n)
    return total

D_fwm_total = D_fwm_cum(math.log(1 + 10, 4))

print(f"  FWM 相位失配 (每個模式):")
print(f"  {'n':>3} | {'Δβ(n)':>10} | {'累積':>10} | {'ω_n':>8}")
for n in [1, 2, 3, 5, 8, 12, 16, 22, 29, 34, 44]:
    dp = fwm_phase_mismatch(n)
    cum = sum(fwm_phase_mismatch(i) for i in range(1, n+1))
    print(f"  {n:3d} | {dp:10.4f} | {cum:10.4f} | {world_omega[n-1]:8.4f}")

print(f"\n  總 FWM 解相干 D_total = {D_fwm_total:.4f}")

# ============ 2. FWM 模型 ============
print(f"\n\n--- 2. FWM 解相干模型: H(z) = H₀ × (D_fwm(ℓ) / D_total)^p × (1+z)^α ---")

def H_fwm(z, p=1.0, alpha=0.0):
    ell = math.log(1 + z, 4)
    D = D_fwm_cum(ell)
    if D_fwm_total == 0:
        return OMEGA_RING
    return OMEGA_RING * (D / D_fwm_total)**p * (1+z)**alpha

# 掃描
best_p = 0.0
best_a = 0.0
best_c = 1e10
for p in np.linspace(0.05, 2.0, 40):
    for a in np.linspace(-1, 3, 41):
        chi2 = 0.0
        for i in range(len(z_vals)):
            z = z_vals[i]
            h_ob = h_obs[i]
            he = h_err[i]
            h_mod = H_fwm(z, p, a)
            chi2 += ((h_ob - h_mod) / he)**2
        if chi2 < best_c:
            best_c = chi2
            best_p = p
            best_a = a

print(f"  最佳 p={best_p:.2f}, α={best_a:.2f}, χ²/dof={best_c/len(z_vals):.4f}")

# 詳細
chi2_fwm = 0.0
print(f"\n  {'z':>5} | {'H_obs':>8} | {'σ_H':>6} | {'H_FWM':>8} | {'O-C':>8} | {'pull':>8}")
for i in range(len(z_vals)):
    z = z_vals[i]
    h_ob = h_obs[i]
    he = h_err[i]
    h_mod = H_fwm(z, best_p, best_a)
    oc = h_ob - h_mod
    pull = oc / he
    chi2_fwm += pull**2
    print(f"  {z:5.3f} | {h_ob:8.1f} | {he:6.1f} | {h_mod:8.1f} | {oc:+8.1f} | {pull:+8.3f}")

# ============ 3. d=14 GEN 行結構 ============
print(f"\n\n--- 3. d=14 GEN 行正交投影 ---")
# d=14 嘅 30 個 beats 形成一個對稱向量
# 呢個向量編碼咗 6 夸克/相空間結構
# 符號內積: κ_ω · d14_vec = 尾部修正

# d=14 beat vector
d14_beats = np.array([abs(world_omega[i] - world_omega[i+14]) for i in range(44-14)])
# 對稱化: 將 30 beats 映射到 44 模式上
# 每個 beat 連接 i 同 i+14, 所以每個模式 i 嘅權重 = 同佢連接嘅 beats 嘅和

# 模式 i 嘅 d14 權重
d14_weight = np.zeros(44)
for i in range(44-14):
    d14_weight[i] += d14_beats[i] / 2  # 一半權重俾 i
    d14_weight[i+14] += d14_beats[i] / 2  # 一半權重俾 i+14

print(f"  d=14 beat 向量:")
print(f"    beats: {d14_beats[:10]} ...")
print(f"    mean: {d14_beats.mean():.6f}")
print(f"    std: {d14_beats.std():.6f}")

print(f"\n  d=14 模式權重 (前 22 個):")
for i in range(22):
    print(f"    i={i:2d}: weight={d14_weight[i]:.6f}")

# ============ 4. Kurtosis + d14 修正 ============
print(f"\n\n--- 4. Kurtosis + d14 正交投影模型 ---")
# H(z) = H₀ × [κ_ω(ℓ) + λ × inner_prod(κ_ω, d14)] × (1+z)^α
# inner_prod(κ_ω, d14) = Σ κ_ω(i) × d14_weight(i) for active modes

def cum_kurtosis(n):
    """累積到第 n 個模式嘅 kurtosis"""
    if n < 2:
        return 0.0
    w = world_omega[:n]
    return np.mean((w - np.mean(w))**4) / np.std(w, ddof=0)**4

def d14_inner(ell):
    """κ_ω 同 d14 嘅內積 (活躍模式)"""
    n_active = min(44, max(1, int(44 * ell)))
    kurt = np.array([cum_kurtosis(n) for n in range(1, n_active+1)])
    # 對應 d14 權重 (truncated to active modes)
    w = d14_weight[:n_active]
    # 歸一化內積
    if np.sum(w) == 0:
        return 0.0
    return np.dot(kurt, w) / np.sum(w)

def H_kurt_d14(z, lam=0.1, alpha=0.0):
    """Kurtosis + d14 修正模型"""
    ell = math.log(1 + z, 4)
    n_active = min(44, max(1, int(44 * ell)))
    
    kurt = cum_kurtosis(n_active)
    d14_corr = d14_inner(ell)
    kurt_max = cum_kurtosis(44)
    
    # 歸一化
    h_kurt = OMEGA_RING * (kurt / kurt_max)
    h_corr = OMEGA_RING * lam * (d14_corr / kurt_max)
    
    return (h_kurt + h_corr) * (1+z)**alpha

# 掃描
best_lam = 0.0
best_a2 = 0.0
best_c2 = 1e10
for lam in np.linspace(-2, 2, 41):
    for a in np.linspace(-1, 3, 41):
        chi2 = 0.0
        for i in range(len(z_vals)):
            z = z_vals[i]
            h_ob = h_obs[i]
            he = h_err[i]
            h_mod = H_kurt_d14(z, lam, a)
            chi2 += ((h_ob - h_mod) / he)**2
        if chi2 < best_c2:
            best_c2 = chi2
            best_lam = lam
            best_a2 = a

print(f"  最佳 λ={best_lam:.2f}, α={best_a2:.2f}, χ²/dof={best_c2/len(z_vals):.4f}")

# 詳細
print(f"\n  {'z':>5} | {'H_obs':>8} | {'σ_H':>6} | {'H_k+d14':>8} | {'O-C':>8} | {'pull':>8}")
chi2_kd14 = 0.0
for i in range(len(z_vals)):
    z = z_vals[i]
    h_ob = h_obs[i]
    he = h_err[i]
    h_mod = H_kurt_d14(z, best_lam, best_a2)
    oc = h_ob - h_mod
    pull = oc / he
    chi2_kd14 += pull**2
    print(f"  {z:5.3f} | {h_ob:8.1f} | {he:6.1f} | {h_mod:8.1f} | {oc:+8.1f} | {pull:+8.3f}")

# ============ 5. FWM + d14 聯合模型 ============
print(f"\n\n--- 5. FWM + d14 聯合模型 ---")
# H(z) = H₀ × [D_fwm(ℓ)/D_total + λ × d14_inner(ℓ)] × (1+z)^α

def H_fwm_d14(z, lam=0.1, alpha=0.0):
    ell = math.log(1 + z, 4)
    n_active = min(44, max(1, int(44 * ell)))
    
    D = D_fwm_cum(ell)
    d14 = d14_inner(ell)
    
    h_fwm = D / D_fwm_total if D_fwm_total > 0 else 0
    h_d14 = lam * d14
    
    return OMEGA_RING * (h_fwm + h_d14) * (1+z)**alpha

best_lam2 = 0.0
best_a3 = 0.0
best_c3 = 1e10
for lam in np.linspace(-2, 2, 41):
    for a in np.linspace(-1, 3, 41):
        chi2 = 0.0
        for i in range(len(z_vals)):
            z = z_vals[i]
            h_ob = h_obs[i]
            he = h_err[i]
            h_mod = H_fwm_d14(z, lam, a)
            chi2 += ((h_ob - h_mod) / he)**2
        if chi2 < best_c3:
            best_c3 = chi2
            best_lam2 = lam
            best_a3 = a

print(f"  最佳 λ={best_lam2:.2f}, α={best_a3:.2f}, χ²/dof={best_c3/len(z_vals):.4f}")

# ============ 6. 全部模型比較 ============
print(f"\n\n--- 6. 全部模型 χ² 比較 ---")
print(f"  {'模型':>40} | {'χ²/dof':>10} | {'Δχ²':>8} | {'判定':>6}")
print(f"  {'-'*40} | {'-'*10} | {'-'*8} | {'-'*6}")

chi2_lcdm = sum(((h_obs[i] - H_lcdm(z_vals[i])) / h_err[i])**2 for i in range(len(z_vals))) / len(z_vals)
print(f"  {'ΛCDM (target)':>40} | {chi2_lcdm:10.4f} | {'—':>8} | {'🟢':>6}")

fd = chi2_fwm - chi2_lcdm * len(z_vals)
print(f"  {'FWM Quantized Decoupling':>40} | {chi2_fwm/len(z_vals):10.4f} | {fd/len(z_vals):+8.4f} | {'🟡' if chi2_fwm/len(z_vals)<2 else '🔴':>6}")

kd = chi2_kd14 - chi2_lcdm * len(z_vals)
print(f"  {'Kurtosis + d14 GEN project':>40} | {chi2_kd14/len(z_vals):10.4f} | {kd/len(z_vals):+8.4f} | {'🟡' if chi2_kd14/len(z_vals)<2 else '🔴':>6}")

fwmd = best_c3 - chi2_lcdm * len(z_vals)
print(f"  {'FWM + d14 聯合模型':>40} | {best_c3/len(z_vals):10.4f} | {fwmd/len(z_vals):+8.4f} | {'🟡' if best_c3/len(z_vals)<2 else '🔴':>6}")

# ============ 7. 分析殘差模式 ============
print(f"\n\n--- 7. 殘差分析: FWM + d14 嘅尾部修正 ---")
# 睇高 z 部分 (z>0.5) 嘅殘差
residuals_fwm = np.array([h_obs[i] - H_fwm(z_vals[i], best_p, best_a) for i in range(len(z_vals))])
residuals_kd14 = np.array([h_obs[i] - H_kurt_d14(z_vals[i], best_lam, best_a2) for i in range(len(z_vals))])
residuals_lcdm = np.array([h_obs[i] - H_lcdm(z_vals[i]) for i in range(len(z_vals))])

print(f"  {'z':>5} | {'res_FWM':>8} | {'res_K+d14':>8} | {'res_LCDM':>8}")
for i in range(len(z_vals)):
    z = z_vals[i]
    print(f"  {z:5.3f} | {residuals_fwm[i]:+8.1f} | {residuals_kd14[i]:+8.1f} | {residuals_lcdm[i]:+8.1f}")

# 高 z 殘差統計
high_z = z_vals >= 0.5
print(f"\n  高 z (z≥0.5) 殘差 RMS:")
print(f"    FWM:     {np.sqrt(np.mean(residuals_fwm[high_z]**2)):.1f}")
print(f"    K+d14:   {np.sqrt(np.mean(residuals_kd14[high_z]**2)):.1f}")
print(f"    ΛCDM:    {np.sqrt(np.mean(residuals_lcdm[high_z]**2)):.1f}")

# ============ 8. 結論 ============
print(f"\n{'='*70}")
print(f"  總結: FWM + d14 修正")
print(f"  {'='*70}")
print(f"")
print(f"  路線進展:")
print(f"    🟢 正交驗證: dD_A/dz 爆炸 = FLRW 不兼容")
print(f"    🟡 Kurtosis 模型: χ²/dof = 0.84 (基礎)")
print(f"    🟡 FWM Quantized: χ²/dof = {chi2_fwm/len(z_vals):.2f}")
print(f"    🟡 K+d14 投影:    χ²/dof = {chi2_kd14/len(z_vals):.2f}")
print(f"    🟡 FWM+d14 聯合:  χ²/dof = {best_c3/len(z_vals):.2f}")
print(f"    🟢 ΛCDM目標:      χ²/dof = 0.61")
print(f"")
print(f"  0.23 差距嘅結構起源:")
print(f"    1. FWM 相位失配 → 離散階梯修正 (已試)")
print(f"    2. d=14 GEN 正交投影 → 尾部修正 (已試)")
print(f"    3. 剩餘差距: 需要更高階拍頻張量 (d=14 × d=22 雙重內積)")
print(f"")
print(f"  🔴 開放: 完整嘅 K_Chain 色散矩陣 → H(z) 解析推導")
print(f"  🔴 建議 O94: 44×44 拍頻張量嘅完整譜分解")

import json
results = {
    "route": "B_fwm_d14",
    "chi2_fwm": float(f"{chi2_fwm/len(z_vals):.4f}"),
    "chi2_kd14": float(f"{chi2_kd14/len(z_vals):.4f}"),
    "chi2_fwm_d14": float(f"{best_c3/len(z_vals):.4f}"),
    "chi2_lcdm": 0.6055,
    "best_fwm_p": float(f"{best_p:.2f}"),
    "best_fwm_alpha": float(f"{best_a:.2f}"),
    "best_kd14_lam": float(f"{best_lam:.2f}"),
    "best_kd14_alpha": float(f"{best_a2:.2f}"),
    "pass": int(PASS),
    "fail": int(FAIL),
    "status": "🟡"
}
with open("../data/07_route_b_fwm_d14.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\n  結果已儲存至 data/07_route_b_fwm_d14.json")