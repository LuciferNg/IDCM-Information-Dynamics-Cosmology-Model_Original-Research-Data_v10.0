"""
IDCM v10.0 — 中微子：W-field p6 模式質量公式
================================================
中微子質量 = W-field p6 模式 × Higgs VEV 嘅高維算符。

核心公式:
m_ν = (γ_6 × v)² / M_Pl

其中 γ_6 = 4sin²(6π/88) = 0.180736 (K_Chain n=6 harmonic)
v = 246 GeV (Higgs VEV)
M_Pl = 1.22 × 10¹⁹ GeV (Planck 質量)

呢個係「幾何 seesaw」: 無需右旋中微子, 無需 M_R
Planck 尺度天然係 suppression scale
"""

import math
import numpy as np

φ = (1 + math.sqrt(5)) / 2

M_Pl = 1.220910e19  # GeV
v = 246.0  # GeV

# K_Chain 44 模式
γ_n = [4 * math.sin(math.pi * n / 88)**2 for n in range(1, 45)]
γ_6 = γ_n[5]  # n=6

print("=" * 80)
print("IDCM v10.0 — 中微子：W-field p6 模式質量公式 🎯")
print("=" * 80)

# ══════════════════════════════════════════════════════════════
# 1. 幾何 Seesaw 公式
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("1. 幾何 Seesaw 公式")
print("─" * 80)

# m_ν = (γ_6 × v)² / M_Pl
m_nu_geometric = (γ_6 * v)**2 / M_Pl

print(f"  γ_6 = {γ_6:.6f} (K_Chain n=6 harmonic)")
print(f"  v = {v} GeV (Higgs VEV)")
print(f"  M_Pl = {M_Pl:.2e} GeV (Planck mass)")
print(f"")
print(f"  m_ν = (γ_6 × v)² / M_Pl")
print(f"       = ({γ_6:.6f} × {v})² / {M_Pl:.2e}")
print(f"       = ({γ_6 * v:.6f})² / {M_Pl:.2e}")
print(f"       = {(γ_6 * v)**2:.6f} / {M_Pl:.2e}")
print(f"       = {m_nu_geometric:.6e} GeV")
print(f"       = {m_nu_geometric * 1e9:.6e} eV")

# ══════════════════════════════════════════════════════════════
# 2. 同其他質量公式嘅對比
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("2. 質量公式對比")
print("─" * 80)

# Charged fermion: m_f = γ_n × M_eff (已經用 M_eff 校準)
# 中微子: m_ν = (γ_6 × v)² / M_Pl

# 用 electron 校準: m_e = γ_9 × M_eff
# M_eff = m_e / γ_9 = 0.511e-3 / 0.398918 = 1.281e-3 GeV

m_e_gev = 0.511e-3
γ_9 = γ_n[8]
M_eff = m_e_gev / γ_9

print(f"  Charged fermion: m_f = γ_n × M_eff")
print(f"    M_eff = m_e / γ_9 = {m_e_gev} / {γ_9:.6f} = {M_eff:.6e} GeV")
print(f"")
print(f"  如果中微子用 charged fermion 公式:")
m_nu_charged = γ_6 * M_eff
print(f"    m_ν = γ_6 × M_eff = {γ_6:.6f} × {M_eff:.6e} = {m_nu_charged:.6e} GeV = {m_nu_charged*1e9:.2f} eV ❌")
print(f"")
print(f"  中微子用幾何 seesaw 公式:")
print(f"    m_ν = (γ_6 × v)² / M_Pl = {m_nu_geometric:.6e} GeV = {m_nu_geometric*1e9:.6e} eV ✅")

# ══════════════════════════════════════════════════════════════
# 3. 中微子 mass hierarchy
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("3. 中微子質量層級 (Mass Hierarchy)")
print("─" * 80)

# 如果中微子係 p6 模式, 三種中微子應該對應唔同嘅 harmonic
# ν_e: n=6, γ_6 = 0.180736
# ν_μ: n=7, γ_7 = 0.244642 (或 n=5, γ_5 = 0.126101)
# ν_τ: n=8, γ_8 = 0.317493 (或 n=4, γ_4 = 0.081014)

# 但更可能: 三種中微子共享 n=6 模式, 但喺唔同嘅 twisted sector
# 類似 charged fermion 嘅 generation 結構

# 從 Z₅ analysis:
# ν_τ: Z₅=4, ν_μ: Z₅=0, ν_e: Z₅=3
# 佢哋嘅質量差異來自 Z₅ twisted sector 嘅 quantum dimension

# d_k = sin(πk/5) / sin(π/5)
# d_0 = 1, d_3 = φ, d_4 = 1

# 中微子質量比:
# m_ν_e : m_ν_μ : m_ν_τ = 1/d_3 : 1/d_0 : 1/d_4
# = 1/φ : 1 : 1

# 但呢個同觀測唔符 (ν_μ 比 ν_e 重)

# 更可能: 中微子質量差異來自 12D eigenvalue
# ν_τ: λ_9, ν_μ: λ_10, ν_e: λ_11

d = np.load("../p15_early_derivations/data/d_tensor_positive.npy")
v_kahler = np.array([φ ** (-k / 12) for k in range(12)])
Y_full = np.zeros((12, 12), dtype=complex)
for i in range(12):
    for j in range(12):
        Y_full[i, j] = sum(d[i, j, k] * v_kahler[k] for k in range(12))
Y_full = (Y_full + Y_full.T) / 2
evals, _ = np.linalg.eigh(Y_full)
evals = evals[np.argsort(evals)[::-1]]

# 中微子 eigenvalue
ν_evals = [evals[9], evals[10], evals[11]]

print(f"  中微子 eigenvalue (12D WDVV):")
print(f"    ν_τ: λ_9 = {ν_evals[0]:.6f}")
print(f"    ν_μ: λ_10 = {ν_evals[1]:.6f}")
print(f"    ν_e: λ_11 = {ν_evals[2]:.6f}")

# 中微子質量 (用幾何 seesaw 公式)
print(f"\n  中微子質量 (幾何 seesaw):")
for i, name in enumerate(["ν_τ", "ν_μ", "ν_e"]):
    m = (ν_evals[i] * v)**2 / M_Pl
    print(f"    {name}: m = ({ν_evals[i]:.6f} × {v})² / {M_Pl:.2e} = {m:.6e} GeV = {m*1e9:.6e} eV")

# 質量平方差
m_sq = [(ν_evals[i] * v)**2 / M_Pl for i in range(3)]
Δm_sq_21 = m_sq[1]**2 - m_sq[2]**2  # ν_μ² - ν_e²
Δm_sq_31 = m_sq[0]**2 - m_sq[2]**2  # ν_τ² - ν_e²

print(f"\n  質量平方差:")
print(f"    Δm²₂₁ = {Δm_sq_21:.6e} eV² (PDG: 7.5e-5 eV²)")
print(f"    Δm²₃₁ = {Δm_sq_31:.6e} eV² (PDG: 2.5e-3 eV²)")

# ══════════════════════════════════════════════════════════════
# 4. 同 PDG 對比
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("4. 同 PDG 對比")
print("─" * 80)

# PDG 中微子參數
# Normal hierarchy: m_ν₁ < m_ν₂ < m_ν₃
# Inverted hierarchy: m_ν₃ < m_ν₁ < m_ν₂
# Δm²₂₁ = 7.53e-5 eV²
# Δm²₃₁ = 2.45e-3 eV² (NH) 或 -2.51e-3 eV² (IH)

Δm21_PDG = 7.53e-5
Δm31_PDG_NH = 2.45e-3

print(f"  PDG 參考:")
print(f"    Δm²₂₁ = {Δm21_PDG:.2e} eV²")
print(f"    Δm²₃₁ = {Δm31_PDG_NH:.2e} eV² (Normal Hierarchy)")
print(f"")
print(f"  IDCM 預測 (幾何 seesaw):")
print(f"    Δm²₂₁ = {Δm_sq_21:.2e} eV²")
print(f"    Δm²₃₁ = {Δm_sq_31:.2e} eV²")
print(f"")

# 如果 IDCM 嘅 eigenvalue 分配唔啱
# 試其他分配: ν_e=λ_8, ν_μ=λ_9, ν_τ=λ_10
print(f"  嘗試其他 eigenvalue 分配:")

for assignment in [(8, 9, 10), (9, 10, 11), (7, 8, 9), (6, 7, 8)]:
    λ_e, λ_μ, λ_τ = evals[assignment[0]], evals[assignment[1]], evals[assignment[2]]
    m_e = (λ_e * v)**2 / M_Pl
    m_μ = (λ_μ * v)**2 / M_Pl
    m_τ = (λ_τ * v)**2 / M_Pl
    Δ21 = m_μ**2 - m_e**2
    Δ31 = m_τ**2 - m_e**2
    print(f"    λ ({assignment[0]},{assignment[1]},{assignment[2]}): "
          f"m=[{m_e*1e9:.2e}, {m_μ*1e9:.2e}, {m_τ*1e9:.2e}] eV, "
          f"Δm²₂₁={Δ21:.2e}, Δm²₃₁={Δ31:.2e}")

# ══════════════════════════════════════════════════════════════
# 5. 結論
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("5. 結論")
print("─" * 80)

print(f"""
  🎯 中微子幾何 Seesaw 公式:

  m_ν = (γ_6 × v)² / M_Pl

  無需右旋中微子, 無需 M_R
  Planck 尺度天然係 suppression scale

  m_ν = {m_nu_geometric*1e9:.6e} eV (單一模式)

  同 charged fermion 公式嘅對比:
  ────────────────────────────────
  Charged fermion: m_f = γ_n × M_eff (線性)
  中微子:         m_ν = (γ_n × v)² / M_Pl (二次)

  二次公式自然給出 sub-eV 質量, 因為 v²/M_Pl ≈ 10⁻⁶ eV

  中微子 eigenvalue 分配:
  ──────────────────────
  ν_τ: λ_9 = {ν_evals[0]:.6f}
  ν_μ: λ_10 = {ν_evals[1]:.6f}
  ν_e: λ_11 = {ν_evals[2]:.6f}

  需要更精確嘅 eigenvalue 分配同 Z₅ phase 分析
""")

with open("data/neutrino_p6_results.txt", "w") as f:
    f.write("中微子幾何 Seesaw 公式\n")
    f.write(f"m_ν = (γ_6 × v)² / M_Pl = {m_nu_geometric*1e9:.6e} eV\n")
    f.write(f"ν_τ: {((ν_evals[0]*v)**2/M_Pl*1e9):.6e} eV\n")
    f.write(f"ν_μ: {((ν_evals[1]*v)**2/M_Pl*1e9):.6e} eV\n")
    f.write(f"ν_e: {((ν_evals[2]*v)**2/M_Pl*1e9):.6e} eV\n")

print("已儲存 ✅")