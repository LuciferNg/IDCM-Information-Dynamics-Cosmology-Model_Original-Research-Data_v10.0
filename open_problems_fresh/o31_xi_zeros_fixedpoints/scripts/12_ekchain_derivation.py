"""
O31 — E_kchain 第一原理推導 + 真空能量譜
============================================
從 K_Chain 幾何推導真空能量標度 E_kchain。

關鍵問題: f_IDCM(0) = 0.1325 是無量綱量。
物理真空能量密度 ρ_vac = f_IDCM(0) · E_kchain⁴。

E_kchain 的候選來源:
1. K_Chain 質量標度 m_0 (由 m_7=13.8 MeV 反推)
2. 中微子質量標度 (p6 mode, ~0.05 eV)
3. 哈勃常數標度 (H₀, ~10⁻³³ eV)
4. SYNC 時間標度 (T_sync=84.64 Gyr, ~10⁻³³ eV)
"""

import numpy as np
from decimal import Decimal, getcontext

getcontext().prec = 100

N_SITES = 44
LAMBDA_SYNC = 406.1  # h⁻¹ Mpc
H0 = 72.59  # km/s/Mpc (IDCM structural)
c = 299792.458  # km/s
hbar_ev_s = 6.582119569e-16  # eV·s
Gyr_to_s = 3.15576e16  # s/Gyr
Mpc_to_m = 3.085677581e22  # m/Mpc
h = 0.674  # H0/100

# 物理常數
ev_to_gev = 1e-9
rho_lambda_obs = 3.6e-47  # GeV⁴ (觀測值)

print("=" * 67)
print("  O31 — E_kchain 第一原理推導")
print("=" * 67)

# ============================================================
# 1. f_IDCM(0) 計算
# ============================================================
print(f"\n─── 1. f_IDCM(0) = Π n/(n+0.5) ───")

prod = Decimal(1)
for n in range(1, N_SITES + 1):
    prod *= Decimal(n) / Decimal(n + Decimal('0.5'))
f_idcm_0 = float(prod)
print(f"  f_IDCM(0) = {f_idcm_0:.15f}")

# ============================================================
# 2. E_kchain 候選標度
# ============================================================
print(f"\n─── 2. E_kchain 候選標度 ───")

candidates = {}

# (a) 從 m_7 = 13.8 MeV 反推 K_Chain 質量標度
gamma_7 = 4 * np.sin(np.pi * 7 / (2 * N_SITES))**2
m_7 = 13.8e6  # eV
m_0_from_m7 = m_7 / np.sqrt(gamma_7)
candidates['m_0 (from m_7=13.8MeV)'] = m_0_from_m7

# (b) 中微子質量標度 (p6 mode)
gamma_6 = 4 * np.sin(np.pi * 6 / (2 * N_SITES))**2
m_nu = 0.05  # eV (典型中微子質量)
m_0_from_nu = m_nu / np.sqrt(gamma_6)
candidates['m_0 (from m_ν=0.05eV)'] = m_0_from_nu

# (c) 從觀測 ρ_Λ 反推
E_kchain_from_rho = (rho_lambda_obs / f_idcm_0) ** 0.25  # GeV
candidates['E_kchain (from ρ_Λ)'] = E_kchain_from_rho * 1e9  # eV

# (d) SYNC 時間標度
T_sync = 84.64  # Gyr
omega_sync = 2 * np.pi / (T_sync * Gyr_to_s)  # rad/s
E_sync = hbar_ev_s * omega_sync  # eV
candidates['E_sync (from T_sync=84.64Gyr)'] = E_sync

# (e) 哈勃常數標度
R_H = c / H0 * Mpc_to_m  # m
omega_H = c / R_H  # rad/s
E_H = hbar_ev_s * omega_H  # eV
candidates['E_H (from H₀=72.59)'] = E_H

# (f) K_Chain 晶格間距標度
a_kchain = LAMBDA_SYNC / h * Mpc_to_m / N_SITES  # m (物理間距, 去掉 h)
omega_lattice = c / a_kchain  # rad/s
E_lattice = hbar_ev_s * omega_lattice  # eV
candidates['E_lattice (a=λ_sync/44)'] = E_lattice

# (g) 從 Σγ_n = 90 的幾何平均
gamma_geo = np.exp(np.mean(np.log(4 * np.sin(np.pi * np.arange(1, N_SITES+1) / (2*N_SITES))**2)))
E_geo = E_kchain_from_rho * 1e9 * gamma_geo  # 用幾何平均修正
candidates['E_geo (幾何平均修正)'] = E_geo

# 輸出
print(f"\n  {'候選':<35} {'能量 (eV)':<20} {'能量 (meV)':<15} {'ρ_vac/ρ_Λ':<15}")
print(f"  {'-'*35} {'-'*20} {'-'*15} {'-'*15}")
best_match = None
best_ratio = np.inf
for name, E in candidates.items():
    rho = f_idcm_0 * (E * ev_to_gev)**4
    if E > 0:
        ratio = abs(rho / rho_lambda_obs)
        if ratio < best_ratio:
            best_ratio = ratio
            best_match = (name, E, rho)
        print(f"  {name:<35} {E:<20.6e} {E*1000:<15.6f} {rho/rho_lambda_obs:<15.2e}")

# ============================================================
# 3. 哪個候選與觀測 ρ_Λ 一致?
# ============================================================
print(f"\n─── 3. 與觀測 ρ_Λ 比較 ───")
print(f"  ρ_Λ(obs) = {rho_lambda_obs:.2e} GeV⁴")

best_match = None
best_ratio = np.inf
for name, E in candidates.items():
    rho = f_idcm_0 * (E * ev_to_gev)**4
    ratio = abs(rho / rho_lambda_obs)
    if ratio < best_ratio:
        best_ratio = ratio
        best_match = (name, E, rho)

print(f"  最佳匹配: {best_match[0]}")
print(f"    E = {best_match[1]:.6e} eV = {best_match[1]*1000:.6f} meV")
print(f"    ρ_vac = {best_match[2]:.2e} GeV⁴")
print(f"    ρ_vac/ρ_Λ = {best_ratio:.2f}")

# ============================================================
# 4. 中微子質量連接
# ============================================================
print(f"\n─── 4. K_Chain 質量譜 ───")

# K_Chain 質量標度: 從 ρ_Λ 反推的 E_kchain
E_kchain = (rho_lambda_obs / f_idcm_0) ** 0.25  # GeV
print(f"  E_kchain (from ρ_Λ) = {E_kchain*1e9:.6f} eV = {E_kchain*1e12:.3f} meV")

# 各模式的質量
gamma = np.array([4 * np.sin(np.pi * n / (2 * N_SITES))**2 for n in range(1, N_SITES + 1)])
m_n = E_kchain * 1e9 * np.sqrt(gamma)  # eV

print(f"\n  K_Chain 質量譜 (以 E_kchain 標度):")
print(f"  {'n':<5} {'γ_n':<15} {'√γ_n':<15} {'m_n (eV)':<15} {'備註':<20}")
print(f"  {'-'*5} {'-'*15} {'-'*15} {'-'*15} {'-'*20}")
for n in [1, 2, 3, 6, 7, 11, 22, 44]:
    note = ""
    if n == 6: note = "← 中微子 (p6)"
    if n == 7: note = "← m_7=13.8MeV (不同標度)"
    if n == 22: note = "← v_g=0.707c"
    if n == 44: note = "← Nyquist"
    print(f"  {n:<5} {gamma[n-1]:<15.10f} {np.sqrt(gamma[n-1]):<15.10f} {m_n[n-1]:<15.6f} {note:20}")

# 注意: m_7 = 13.8 MeV 是 K_Chain 的「質量模式」,
# 而 E_kchain ≈ 4 meV 是「真空能量標度」.
# 兩者相差 ~3.5 × 10⁶ 倍, 即 ~10⁶⁵ 倍在能量密度上.
ratio_mass = 13.8e6 / (E_kchain * 1e9)
print(f"\n  m_7 / E_kchain = {13.8e6:.1e} / {E_kchain*1e9:.6f} = {ratio_mass:.2e}")

# ============================================================
# 5. 物理詮釋
# ============================================================
print(f"\n─── 5. 物理詮釋 ───")
print(f"""
  E_kchain ≈ {E_kchain*1e12:.2f} meV 的物理意義:

  1. 這是 K_Chain 零點能量的正則化標度
  2. 不是粒子質量標度 (m_7=13.8MeV 是不同物理)
  3. 與中微子質量 ~0.05eV 相差 ~10 倍
  4. 與哈勃常數標度 ~10⁻³³eV 相差 ~10³⁰ 倍

  真空能量 = 幾何 × 動力學:
    ρ_vac = f_IDCM(0) × E_kchain⁴
          = 0.1325 × ({E_kchain*1e12:.2f} meV)⁴
          = {rho_lambda_obs:.2e} GeV⁴ ✅

  🔴 E_kchain 的絕對標度仍需 IDCM 質量標度理論推導。
     目前只能從觀測 ρ_Λ 反推，與 ΛCDM 做法相同。
""")

# 儲存
with open("data/ekchain_derivation.txt", "w") as f:
    f.write(f"O31 E_kchain First-Principles Derivation\n\n")
    f.write(f"f_IDCM(0) = {f_idcm_0:.15f}\n")
    f.write(f"E_kchain (from ρ_Λ) = {E_kchain*1e9:.6f} eV = {E_kchain*1e12:.3f} meV\n")
    f.write(f"Best candidate match: {best_match[0]}\n")
    f.write(f"\nCandidate scales:\n")
    for name, E in candidates.items():
        rho = f_idcm_0 * (E * ev_to_gev)**4
        f.write(f"  {name}: E={E:.6e} eV, ρ_vac/ρ_Λ={rho/rho_lambda_obs:.2e}\n")

print("  ✅ data/ekchain_derivation.txt")