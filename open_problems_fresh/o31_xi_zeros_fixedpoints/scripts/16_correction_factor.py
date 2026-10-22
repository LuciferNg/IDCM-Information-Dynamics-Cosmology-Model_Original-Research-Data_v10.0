"""
O31 — 7% 修正因子結構探索
============================
E_kchain = √(M_Planck · ħ·H₀) × correction
correction = 4.060/4.348 = 0.9338

探索: 呢個因子係咪 IDCM 嘅結構常數?
"""

import numpy as np

phi = (1 + np.sqrt(5)) / 2
phi_inv = phi - 1
N_SITES = 44

# 基礎量
gamma = np.array([4 * np.sin(np.pi * n / (2 * N_SITES))**2 for n in range(1, N_SITES + 1)])
sum_gamma = np.sum(gamma)  # 90.0
sum_sqrt_gamma = np.sum(np.sqrt(gamma))  # Σ√γ_n

# 物理常數
H0 = 72.59  # km/s/Mpc
hbar_ev_s = 6.582119569e-16  # eV·s
H0_per_s = H0 * 1000 / 3.085677581e22
E_H = hbar_ev_s * H0_per_s  # eV
M_Planck = 1.220910e28  # eV
E_gm = np.sqrt(E_H * M_Planck)  # √(ħ·H₀ · M_Planck) in eV

# f_IDCM(0)
from decimal import Decimal, getcontext
getcontext().prec = 100
prod = Decimal(1)
for n in range(1, N_SITES + 1):
    prod *= Decimal(n) / Decimal(n + Decimal('0.5'))
f_idcm_0 = float(prod)

# 目標 E_kchain
rho_lambda_obs = 3.6e-47  # GeV⁴
E_kchain_target = (rho_lambda_obs / f_idcm_0) ** 0.25 * 1e9  # eV
E_gm_ev = E_gm  # E_gm is already in eV = 0.004348 eV
correction_target = E_kchain_target / E_gm_ev  # 無量綱比值

print("=" * 67)
print("  O31 — 7% 修正因子結構探索")
print("=" * 67)
print(f"\n  E_kchain = {E_kchain_target*1000:.6f} meV")
print(f"  √(M_P·ħH₀) = {E_gm*1000:.6f} meV")
print(f"  correction = {correction_target:.10f}")
print(f"  1 - correction = {1-correction_target:.10f}")
print(f"  偏差 = {1-correction_target:.4%}")

# ============================================================
# 探索 1: φ 冪次
# ============================================================
print(f"\n─── 探索 1: φ 冪次 ───")

# 找最近的 φ^k
for k_float in np.linspace(-1, 1, 2001):
    test = phi ** k_float
    if abs(test - correction_target) < 0.0001:
        print(f"  φ^{k_float:.6f} = {test:.10f} (偏差 {test-correction_target:+.10f})")

# 檢查 k = -1/7 = -0.142857...
k_minus_1_7 = -1/7
test = phi ** k_minus_1_7
print(f"  φ^(-1/7) = {test:.10f} (偏差 {test-correction_target:+.10e})")

# 檢查 k = -1/φ^5 = -0.0902
k_minus_1_phi5 = -1/phi**5
test = phi ** k_minus_1_phi5
print(f"  φ^(-1/φ⁵) = {test:.10f} (偏差 {test-correction_target:+.10e})")

# 檢查 k = -γ_7 = -0.2446
k_minus_gamma7 = -gamma[6]
test = phi ** k_minus_gamma7
print(f"  φ^(-γ_7) = {test:.10f} (偏差 {test-correction_target:+.10e})")

# ============================================================
# 探索 2: 有理數近似
# ============================================================
print(f"\n─── 探索 2: 有理數近似 ───")

# 連分數展開找到最好的有理近似
from fractions import Fraction
frac = Fraction(correction_target).limit_denominator(1000)
print(f"  correction ≈ {frac.numerator}/{frac.denominator} = {float(frac):.10f}")
print(f"  偏差: {correction_target - float(frac):.2e}")

# 嘗試找到 correction 的簡單表達式
# 1 - correction = 0.0662... 
one_minus = 1 - correction_target
print(f"\n  1 - correction = {one_minus:.10f}")

# 檢查是否 = 1/φ^? 
for k in range(1, 20):
    test = 1/phi**k
    if abs(test - one_minus) < 0.01:
        print(f"  1/φ^{k} = {test:.10f} (偏差 {test-one_minus:+.10f})")

# 檢查是否 = γ_n / Σγ
for n in range(1, N_SITES + 1):
    test = gamma[n-1] / sum_gamma
    if abs(test - one_minus) < 0.01:
        print(f"  γ_{n}/Σγ = {test:.10f} (偏差 {test-one_minus:+.10f})")

# 檢查是否 = (γ_n - γ_m) / Σγ
for n in range(1, N_SITES + 1):
    for m in range(n+1, N_SITES + 1):
        test = (gamma[n-1] - gamma[m-1]) / sum_gamma
        if abs(test - one_minus) < 0.005:
            print(f"  (γ_{n} - γ_{m})/Σγ = {test:.10f} (偏差 {test-one_minus:+.10f})")

# ============================================================
# 探索 3: K_Chain 譜結構
# ============================================================
print(f"\n─── 探索 3: K_Chain 譜結構 ───")

# Σ√γ_n 
print(f"  Σ√γ_n = {sum_sqrt_gamma:.10f}")
print(f"  Σ√γ_n / N = {sum_sqrt_gamma/N_SITES:.10f}")
print(f"  N / Σ√γ_n = {N_SITES/sum_sqrt_gamma:.10f}")

# Check if correction = (Σ√γ_n / N) / (something)?
test = (sum_sqrt_gamma / N_SITES) / 2.0
print(f"  (Σ√γ_n/N)/2 = {test:.10f} (偏差 {test-correction_target:+.10e})")

# Check if correction = f_IDCM(0) * something?
test = f_idcm_0 * (sum_sqrt_gamma / f_idcm_0**0.5)
print(f"  f_IDCM(0) * Σ√γ/√f = {test:.10f}")

# ============================================================
# 探索 4: 量子修正解釋
# ============================================================
print(f"\n─── 探索 4: 量子修正解釋 ───")

# 在 QFT 中, 真空能量有 Casimir 型修正
# 對於 K_Chain 這個 44 模系統, Casimir 修正因子 = ?

# Casimir 修正: 1 - π²/(6N²) for N modes?
# 或者: 1 - (ζ(2))/(N²) = 1 - π²/(6N²)?
N = N_SITES
casimir = 1 - np.pi**2 / (6 * N**2)
print(f"  1 - π²/(6N²) = {casimir:.10f} (偏差 {casimir-correction_target:+.10e})")

# 或者: 1 - 1/(2N)?
test = 1 - 1/(2*N)
print(f"  1 - 1/(2N) = {test:.10f} (偏差 {test-correction_target:+.10e})")

# 或者: 1 - 1/N^2?
test = 1 - 1/N**2
print(f"  1 - 1/N² = {test:.10f} (偏差 {test-correction_target:+.10e})")

# ============================================================
# 探索 5: 最精確匹配
# ============================================================
print(f"\n─── 探索 5: 精確匹配搜尋 ───")

# 搜尋: correction = φ^(-1/7) × (1 + small correction)?
candidates = []

# 1. φ^(-1/7)
candidates.append(("φ^(-1/7)", phi**(-1/7)))

# 2. exp(-1/15)
candidates.append(("exp(-1/15)", np.exp(-1/15)))

# 3. 1 - 1/φ^5
candidates.append(("1 - 1/φ⁵", 1 - 1/phi**5))

# 4. 1 - γ_1
candidates.append(("1 - γ_1", 1 - gamma[0]))

# 5. 1 - γ_2
candidates.append(("1 - γ_2", 1 - gamma[1]))

# 6. 1 - γ_3
candidates.append(("1 - γ_3", 1 - gamma[2]))

# 7. (Σγ - 1)/Σγ
candidates.append(("(Σγ-1)/Σγ", (sum_gamma-1)/sum_gamma))

# 8. (Σγ - γ_1)/Σγ
candidates.append(("(Σγ-γ₁)/Σγ", (sum_gamma-gamma[0])/sum_gamma))

# 9. φ^(-Σγ/N²)
candidates.append(("φ^(-Σγ/N²)", phi**(-sum_gamma/N_SITES**2)))

# 10. 1 - φ^(-N)
candidates.append(("1 - φ^(-N)", 1 - phi**(-N_SITES)))

# 排序
sorted_candidates = sorted(candidates, key=lambda x: abs(x[1] - correction_target))
print(f"  {'表達式':<25} {'值':<15} {'偏差':<15}")
print(f"  {'-'*25} {'-'*15} {'-'*15}")
for name, val in sorted_candidates[:10]:
    print(f"  {name:<25} {val:<15.10f} {abs(val-correction_target):<15.2e}")

# ============================================================
# 結論
# ============================================================
best_name, best_val = sorted_candidates[0]
print(f"\n{'═'*67}")
print(f"  結論")
print(f"{'═'*67}")
print(f"""
  最佳匹配: {best_name} = {best_val:.10f}
  目標: {correction_target:.10f}
  偏差: {abs(best_val-correction_target):.2e}
  
  E_kchain = √(M_Planck · ħ·H₀) × {best_name}
           = {E_gm*1000:.4f} × {best_val:.6f} meV
           = {E_gm*best_val*1000:.6f} meV
  目標: {E_kchain_target*1000:.6f} meV
  
  🟡 修正因子可能係 IDCM 結構常數, 但需要更多理論推導
""")

# 儲存
with open("data/correction_factor_results.txt", "w") as f:
    f.write(f"O31 7% Correction Factor Exploration\n\n")
    f.write(f"correction = {correction_target:.10f}\n")
    f.write(f"Best match: {best_name} = {best_val:.10f}\n")
    f.write(f"Deviation: {abs(best_val-correction_target):.2e}\n")
    for name, val in sorted_candidates[:5]:
        f.write(f"  {name}: {val:.10f} (dev={abs(val-correction_target):.2e})\n")

print("  ✅ data/correction_factor_results.txt")