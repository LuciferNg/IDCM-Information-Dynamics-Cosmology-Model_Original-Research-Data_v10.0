"""
IDCM v10.0 — 中微子：W-field p6 模式質量推導
==============================================
從 K_Chain 嘅 n=6 諧波模式推導中微子質量。

核心假設:
1. 中微子 = W-field 嘅 p6 模式 (K_Chain n=6)
2. 質量 = λ × M_Pl × exp(-V_cycle) × f_sector
3. 唔係 Seesaw 機制 (無需 M_R)
"""

import math
import numpy as np

φ = (1 + math.sqrt(5)) / 2
sqrt_φ = math.sqrt(φ)

M_Pl = 1.220910e22  # MeV

print("=" * 80)
print("IDCM v10.0 — 中微子：W-field p6 模式質量推導 🎯")
print("=" * 80)

# ══════════════════════════════════════════════════════════════
# 1. 載入 d_tensor 同 eigenvalue
# ══════════════════════════════════════════════════════════════
print("\n1. 載入 d_tensor 同 eigenvalue 結構")

d = np.load("../p15_early_derivations/data/d_tensor_positive.npy")
v = np.array([φ ** (-k / 12) for k in range(12)])

Y_full = np.zeros((12, 12), dtype=complex)
for i in range(12):
    for j in range(12):
        Y_full[i, j] = sum(d[i, j, k] * v[k] for k in range(12))
Y_full = (Y_full + Y_full.T) / 2

evals, evecs = np.linalg.eigh(Y_full)
idx = np.argsort(evals)[::-1]
evals = evals[idx]
evecs = evecs[:, idx]

# K_Chain 44 模式
γ_n = [4 * math.sin(math.pi * n / 88)**2 for n in range(1, 45)]

print(f"  d_tensor: {d.shape} ✅")
print(f"  Eigenvalues: {[f'{ev:.4f}' for ev in evals[:10]]}")

# ══════════════════════════════════════════════════════════════
# 2. K_Chain 諧波模式同粒子對應
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("2. K_Chain 諧波模式同粒子對應")
print("─" * 80)

# 已知粒子嘅 eigenvalue 同質量
particle_data = {
    "Top":     {"idx": 0, "mass_mev": 172760e3, "n_mode": 1,  "γ_n": γ_n[0]},
    "Bottom":  {"idx": 1, "mass_mev": 4180e3,   "n_mode": 2,  "γ_n": γ_n[1]},
    "Tau":     {"idx": 2, "mass_mev": 1777e3,   "n_mode": 3,  "γ_n": γ_n[2]},
    "Charm":   {"idx": 3, "mass_mev": 1270e3,   "n_mode": 4,  "γ_n": γ_n[3]},
    "Strange": {"idx": 4, "mass_mev": 93.4,     "n_mode": 5,  "γ_n": γ_n[4]},
    "Muon":    {"idx": 5, "mass_mev": 105.658,  "n_mode": 6,  "γ_n": γ_n[5]},
    "Up":      {"idx": 6, "mass_mev": 2.16,     "n_mode": 7,  "γ_n": γ_n[6]},
    "Down":    {"idx": 7, "mass_mev": 4.67,     "n_mode": 8,  "γ_n": γ_n[7]},
    "Electron":{"idx": 8, "mass_mev": 0.511,    "n_mode": 9,  "γ_n": γ_n[8]},
}

print(f"  {'Particle':>10} | {'λ':>10} | {'mass(MeV)':>12} | {'n':>3} | {'γ_n':>10} | {'mass/λ':>10}")
print("-" * 65)

for name, data in particle_data.items():
    λ = evals[data["idx"]]
    m = data["mass_mev"]
    m_over_λ = m / λ if λ > 0 else 0
    print(f"  {name:>10} | {λ:>10.4f} | {m:>12.4f} | {data['n_mode']:>3} | {data['γ_n']:>10.6f} | {m_over_λ:>10.2f}")

# ══════════════════════════════════════════════════════════════
# 3. V_cycle 反推
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("3. V_cycle 反推 (從已知粒子)")
print("─" * 80)

# V_cycle = ln(λ × M_Pl / m)
# 假設 f_sector = 1 (無額外修正)

print(f"  {'Particle':>10} | {'λ':>10} | {'mass(MeV)':>12} | {'λ×M_Pl':>15} | {'V_cycle':>10} | {'exp(-V)':>12}")
print("-" * 65)

v_cycles = {}
for name, data in particle_data.items():
    λ = evals[data["idx"]]
    m = data["mass_mev"]
    λM = λ * M_Pl
    V = math.log(λM / m)
    expV = math.exp(-V)
    v_cycles[name] = V
    print(f"  {name:>10} | {λ:>10.4f} | {m:>12.4f} | {λM:>15.2f} | {V:>10.4f} | {expV:>12.6e}")

# ══════════════════════════════════════════════════════════════
# 4. V_cycle 同 K_Chain 模式嘅關係
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("4. V_cycle 同 K_Chain 模式嘅關係")
print("─" * 80)

# V_cycle 似乎同 γ_n 成正比
# 即係: V_cycle ∝ γ_n
# 或者: V_cycle ∝ n (模式序號)

print(f"  {'Particle':>10} | {'n':>3} | {'γ_n':>10} | {'V_cycle':>10} | {'V/γ_n':>10} | {'V/n':>10}")
print("-" * 55)

for name, data in particle_data.items():
    V = v_cycles[name]
    n = data["n_mode"]
    γ = data["γ_n"]
    print(f"  {name:>10} | {n:>3} | {γ:>10.6f} | {V:>10.4f} | {V/γ:>10.4f} | {V/n:>10.4f}")

# ══════════════════════════════════════════════════════════════
# 5. 中微子 eigenvalue 同 V_cycle 估算
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("5. 中微子 eigenvalue 同 V_cycle 估算")
print("─" * 80)

# 中微子 = p6 模式 (n=6)
# 但 K_Chain 嘅 n=6 對應 μ 子 (n=6 係 Muon)
# 所以中微子唔係 n=6 嘅 γ_n
# 而係 12D eigenvalue 嘅第 9,10,11 個 eigenvalue

# 中微子 eigenvalue
ν_indices = [9, 10, 11]  # ν_τ, ν_μ, ν_e
ν_evals = [evals[i] for i in ν_indices]

print(f"  中微子 eigenvalue:")
for i, idx in enumerate(ν_indices):
    print(f"    ν_{['τ', 'μ', 'e'][i]}: λ_{idx} = {evals[idx]:.6f}")

# 用 V_cycle 擬合
# 從已知粒子, V_cycle 似乎大致同 n 成正比
# 但對於中微子, n 係 12D eigenvalue index, 唔係 K_Chain mode

# 方法: 用 lepton 嘅 V_cycle pattern 外推
# Tau (n=3): V=46.678
# Muon (n=6): V=46.295
# Electron (n=9): V=46.389
# 平均 V_cycle ≈ 46.45

# 中微子嘅 V_cycle 應該同 lepton 相近 (同一 sector)
# 假設 V_cycle ≈ 46.4

V_nu_est = 46.4

print(f"\n  V_cycle 估算:")
print(f"    從 lepton 平均: V_cycle ≈ 46.45")
print(f"    取 V_cycle = {V_nu_est:.4f}")

# 中微子質量
print(f"\n  {'ν':>5} | {'λ':>10} | {'V_cycle':>10} | {'mass(eV)':>12} | {'PDG上限(eV)':>12}")
print("-" * 55)

ν_names = ["ν_τ", "ν_μ", "ν_e"]
ν_pdg_upper = [1.8e4, 9.0e3, 0.8]

for i, idx in enumerate(ν_indices):
    λ = evals[idx]
    m = λ * M_Pl * math.exp(-V_nu_est) * 1e6  # eV
    print(f"  {ν_names[i]:>5} | {λ:>10.6f} | {V_nu_est:>10.4f} | {m:>12.6e} | {ν_pdg_upper[i]:>12.2e}")

# ══════════════════════════════════════════════════════════════
# 6. 中微子嘅 sector factor 分析
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("6. 中微子嘅 sector factor 分析")
print("─" * 80)

# 所有粒子嘅質量公式: m = λ × M_Pl × exp(-V_cycle) × f_sector
# f_sector 係 sector-specific factor
# 對於夸克同 lepton, f_sector 包含 √φ 修正

# 中微子嘅 sector factor 可能係:
# 1. 1 (無修正)
# 2. 1/φ (來自 Fibonacci anyon)
# 3. 1/√φ (來自波函數重整化)

# 如果中微子無修正, m_ν ≈ 10^-10 eV (太輕)
# 如果中微子有修正, 需要更大嘅 f_sector

# 從 PDG 上限反推 f_sector
print(f"  {'ν':>5} | {'λ':>10} | {'m_PDG(eV)':>12} | {'V_cycle':>10} | {'f_sector':>12}")
print("-" * 55)

# 用 ν_μ 嘅 PDG 上限 (9.0e3 eV) 反推
for i, idx in enumerate(ν_indices):
    λ = evals[idx]
    m_pdg = ν_pdg_upper[i]
    # 假設 V_cycle = 46.4
    m_base = λ * M_Pl * math.exp(-V_nu_est) * 1e6  # eV
    f_needed = m_pdg / m_base if m_base > 0 else 0
    print(f"  {ν_names[i]:>5} | {λ:>10.6f} | {m_pdg:>12.2e} | {V_nu_est:>10.4f} | {f_needed:>12.4e}")

# ══════════════════════════════════════════════════════════════
# 7. 中微子嘅 p6 模式 harmonic 結構
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("7. 中微子嘅 p6 模式 harmonic 結構")
print("─" * 80)

# 中微子 = W-field 嘅 p6 模式
# K_Chain 嘅 n=6 模式, γ_6 = 4sin²(6π/88)
γ_6 = γ_n[5]  # n=6
γ_3 = γ_n[2]  # n=3 (Tau)
γ_9 = γ_n[8]  # n=9 (Electron)

# 如果中微子質量同 γ_n 成正比
# m_ν ∝ γ_6
# 比例常數從 lepton 推導
# m_e = γ_9 × K, m_τ = γ_3 × K
# K = m_e / γ_9 = 0.511 / 0.3989 = 1.281 MeV

K_e = 0.511 / γ_9
K_τ = 1777.0 / γ_3

print(f"  γ_3 (Tau) = {γ_3:.6f}")
print(f"  γ_6 (ν) = {γ_6:.6f}")
print(f"  γ_9 (e) = {γ_9:.6f}")
print(f"  K_e = m_e / γ_9 = {K_e:.4f} MeV")
print(f"  K_τ = m_τ / γ_3 = {K_τ:.4f} MeV")
print(f"")
print(f"  如果中微子質量同 γ_n 成正比:")
m_nu_gamma = γ_6 * K_e
print(f"  m_ν ≈ γ_6 × K_e = {m_nu_gamma:.4f} MeV = {m_nu_gamma*1e6:.2f} eV")
print(f"  (PDG: m_ν < 0.8 eV) — 仍然太大!")
print(f"")
print(f"  所以中微子嘅質量機制唔係簡單嘅 γ_n 比例!")
print(f"  中微子嘅 eigenvalue λ more important than γ_n")

# ══════════════════════════════════════════════════════════════
# 8. 總結
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("8. 總結")
print("─" * 80)

print(f"""
  🎯 中微子質量推導結果:

  eigenvalue: λ_ν₉ = {evals[9]:.6f}, λ_ν₁₀ = {evals[10]:.6f}, λ_ν₁₁ = {evals[11]:.6f}
  V_cycle ≈ {V_nu_est:.2f} (從 lepton 平均)
  
  中微子質量 (無 sector factor):
  m_ν_τ = {λ * M_Pl * math.exp(-V_nu_est) * 1e6:.6e} eV
  m_ν_μ = {ν_evals[1] * M_Pl * math.exp(-V_nu_est) * 1e6:.6e} eV
  m_ν_e = {ν_evals[2] * M_Pl * math.exp(-V_nu_est) * 1e6:.6e} eV
  
  問題: 中微子質量遠小於 PDG 上限 (10⁻¹⁰ eV vs 10⁴ eV)
  
  可能原因:
  1. eigenvalue 分配唔啱 — 中微子可能對應更大嘅 eigenvalue
  2. V_cycle 不同 — 中微子可能有更細嘅 V_cycle
  3. 需要 W-field 嘅非對角混合 (類似 CKM 嘅 PMNS)
  4. 中微子 eigenvalue 來自 12D 結構嘅高階微擾

  下一步:
  ──────
  1. 檢查 12D eigenvalue 嘅正確分配
  2. 推導中微子嘅 V_cycle (可能同 lepton 唔同)
  3. 引入 W-field 非對角混合 (PMNS)
""")

# 儲存
with open("data/neutrino_p6_results.txt", "w") as f:
    f.write("中微子質量推導結果\n")
    f.write(f"ν_τ: λ={evals[9]:.6f}, m≈{evals[9]*M_Pl*math.exp(-V_nu_est)*1e6:.6e} eV\n")
    f.write(f"ν_μ: λ={evals[10]:.6f}, m≈{evals[10]*M_Pl*math.exp(-V_nu_est)*1e6:.6e} eV\n")
    f.write(f"ν_e: λ={evals[11]:.6f}, m≈{evals[11]*M_Pl*math.exp(-V_nu_est)*1e6:.6e} eV\n")

print("已儲存 ✅")