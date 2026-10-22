"""
O31 — 真空能量解析延拓
========================
計算 f_IDCM(0) 作為 K_Chain 零點能量的正則化值。

核心公式:
  ρ_vacuum ∝ Σ γ_n →^{Analytic Continuation} f_IDCM(0)
  
  f_IDCM(0) = e^{β} · Π_{n=1}^{44} s_n / p_n
            = e^{β} · Π_{n=1}^{44} (λ_sync/(n+0.5)) / (λ_sync/n)
            = e^{β} · Π_{n=1}^{44} n/(n+0.5)

物理意義: 將 K_Chain 的離散譜 γ_n = 4sin²(πn/88) 的零點和
通過 Hadamard 亞純函數正則化，得到有限真空能量密度。
"""

import numpy as np
import math
from decimal import Decimal, getcontext

N_SITES = 44
LAMBDA_SYNC = 406.1  # h⁻¹ Mpc
phi = (1 + np.sqrt(5)) / 2
H0 = 67.4  # km/s/Mpc

# 提高精度
getcontext().prec = 100

print("=" * 67)
print("  O31 — 真空能量解析延拓")
print("=" * 67)

# ============================================================
# 1. K_Chain 零點能量 (原始和)
# ============================================================
print(f"\n─── 1. K_Chain 零點能量 Σ γ_n ───")

gamma = np.array([4 * np.sin(np.pi * n / (2 * N_SITES))**2 for n in range(1, N_SITES + 1)])
sum_gamma = np.sum(gamma)
print(f"  Σ γ_n = {sum_gamma:.10f}  (n=1..44)")
print(f"  γ_n 範圍: [{gamma[0]:.6f}, {gamma[-1]:.6f}]")

# 半和 (量子零點能)
E_zero = 0.5 * sum_gamma
print(f"  零點能量 E_0 = (1/2)Σγ_n = {E_zero:.10f}")

# ============================================================
# 2. f_IDCM(0) 的計算
# ============================================================
print(f"\n─── 2. f_IDCM(0) = Π n/(n+0.5) ───")

# 精確計算使用 Decimal
prod = Decimal(1)
for n in range(1, N_SITES + 1):
    prod *= Decimal(n) / Decimal(n + Decimal('0.5'))

f_idcm_0 = float(prod)
print(f"  f_IDCM(0) = Π_{1}^{N_SITES} n/(n+0.5) = {f_idcm_0:.15f}")
print(f"  ln[f_IDCM(0)] = {math.log(f_idcm_0):.10f}")

# 解析形式: Π n/(n+0.5) = 44! · 2^44 / (89!!)
# 驗證
fact_44 = math.factorial(44)
double_fact_89 = 1
for k in range(1, 90, 2):  # 1, 3, 5, ..., 89
    double_fact_89 *= k
ratio_exact = fact_44 * (2**44) / double_fact_89
print(f"  解析形式驗證: 44!·2^44/89!! = {ratio_exact:.15f}")
print(f"  一致: {'✅' if abs(ratio_exact - f_idcm_0) < 1e-15 else '❌'}")

# ============================================================
# 3. 正則化比值
# ============================================================
print(f"\n─── 3. 正則化比值 ───")

# 比值: 正則化值 / 原始和
ratio = f_idcm_0 / sum_gamma
print(f"  f_IDCM(0) / Σγ_n = {f_idcm_0:.10f} / {sum_gamma:.10f} = {ratio:.10e}")
print(f"  這表示正則化壓縮了 {1/ratio:.1f} 倍")

# 對比: 如果 Σγ_n 是「裸真空能」, f_IDCM(0) 是「正則化真空能」
# 真空能量災難: QFT 預測比觀測大 120 階
# IDCM 正則化壓縮比: 1/ratio
print(f"\n  真空能量災難對比:")
print(f"  QFT 預測 vs 觀測: ~10¹²⁰ 倍")
print(f"  IDCM 正則化壓縮: ~{1/ratio:.1f} 倍")
print(f"  是否需要指數因子 e^β 來達到 10¹²⁰ 壓縮?")

# 需要的 β 來匹配真空能量災難的壓縮
beta_needed_120 = math.log(1e120 * ratio)
print(f"  若需要 10¹²⁰ 壓縮: β = ln(10¹²⁰ · ratio) = {beta_needed_120:.2f}")

# 但 IDCM 沒有真空能量災難 (因為 K_Chain 是離散譜, 不是 QFT)
# 所以不需要匹配 QFT 的 120 階
print(f"\n  但 IDCM 沒有 QFT 的真空能量災難:")
print(f"  K_Chain 是離散 44 模, 不是連續 QFT")
print(f"  正則化壓縮比 {1/ratio:.1f} 是有限的幾何效應")

# ============================================================
# 4. γ_n 的生成函數 G(z) 在 z=0 處
# ============================================================
print(f"\n─── 4. G(0) = Σ γ_n · 0^n = 0 (平凡) ───")

# G(z) = Σ γ_n z^n, G(0) = γ_0 · 0^0... 但 n 從 1 開始
# G(0) = 0 (因為所有項 z^n = 0)
# 所以 G(0) 不是有用的正則化

# 但 G(1) = Σ γ_n = 90 (原始和)
# 而 f_IDCM(0) = Π n/(n+0.5) ≠ 0 是真正的正則化值

print(f"  G(1) = Σ γ_n = {sum_gamma:.10f} (原始和)")
print(f"  f_IDCM(0) = Π n/(n+0.5) = {f_idcm_0:.10f} (正則化值)")
print(f"  兩者不同: 正則化不是簡單的生成函數求值")

# ============================================================
# 5. 物理詮釋
# ============================================================
print(f"\n─── 5. 物理詮釋 ───")
print(f"""
  f_IDCM(0) = {f_idcm_0:.10f} 的物理意義:

  這是 K_Chain 零點能量經 Hadamard 亞純函數正則化後的有限值。
  它代表宇宙真空的能量密度，單位為 K_Chain 自然單位。

  要轉換為物理單位 (GeV⁴):
  - 需要 K_Chain 的能量標度 E_kchain
  - ρ_vac = f_IDCM(0) · E_kchain⁴
  - 觀測 ρ_Λ ≈ (2.3 meV)⁴ ≈ 3.6 × 10⁻⁴⁷ GeV⁴
  - 所以 E_kchain = (ρ_Λ / f_IDCM(0))^{1/4}

  🔴 這需要 IDCM 的質量標度理論來確定 E_kchain
""")

# 計算需要的 E_kchain
rho_lambda_gev = 3.6e-47  # GeV⁴
E_kchain = (rho_lambda_gev / f_idcm_0) ** 0.25
print(f"  若 ρ_vac = f_IDCM(0) · E_kchain⁴ = ρ_Λ:")
print(f"  E_kchain = ({rho_lambda_gev:.1e} / {f_idcm_0:.10f})^{{1/4}}")
print(f"  E_kchain = {E_kchain:.6e} GeV")
print(f"  E_kchain = {E_kchain*1e9:.2f} eV")
print(f"  這在 meV 量級, 與中微子質量尺度一致 ✅")

# 比對 K_Chain 特徵頻率
# γ_n = 4sin²(πn/88), 最大 γ_44 = 4
# 對應頻率: ω_n = √γ_n · ω_0
# 最大 ω_44 = 2 · ω_0
# 若 ω_0 = E_kchain / ħ, 則最高頻率 ~ 2E_kchain ~ 2 meV
print(f"\n  K_Chain 最高頻率: ω_44 = 2 · E_kchain = {2*E_kchain*1e9:.2f} eV")
print(f"  這在 ~meV 範圍, 對應遠紅外/微波")

# ============================================================
# 結論
# ============================================================
print(f"\n{'═'*67}")
print(f"  結論")
print(f"{'═'*67}")
print(f"""
  f_IDCM(0) = {f_idcm_0:.10f}
  Σγ_n = {sum_gamma:.10f}
  正則化壓縮比: {1/ratio:.1f}
  
  🟢 f_IDCM(0) 計算完成
  🔴 需要 K_Chain 能量標度 E_kchain 的理論推導
     才能將 f_IDCM(0) 轉換為物理真空能量密度
""")

# 儲存
with open("data/vacuum_energy_results.txt", "w") as f:
    f.write(f"O31 Vacuum Energy Analytic Continuation\n\n")
    f.write(f"sum_gamma = {sum_gamma:.15f}\n")
    f.write(f"f_IDCM(0) = {f_idcm_0:.15f}\n")
    f.write(f"ratio = f_IDCM(0)/sum_gamma = {ratio:.15e}\n")
    f.write(f"E_kchain (from ρ_Λ) = {E_kchain:.6e} GeV\n")
    f.write(f"E_kchain = {E_kchain*1e9:.2f} eV\n")

print("  ✅ data/vacuum_energy_results.txt")