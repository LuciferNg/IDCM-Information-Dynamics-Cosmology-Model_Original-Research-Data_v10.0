#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O133 scripts/04 — O86 W-field 線性微擾 → P(k) 傳遞 (v2 修正)
============================================================
測試 O86 統一 Lagrangian 嘅線性微擾能否閉合 P(k) broadband 形狀。

O86 Lagrangian (已閉合, 34/34):
    L = L_W + L_GR + L_SM
    L_W = ½(∂W)² + μ²|W|² − λ|W|⁴    (SSB: ⟨W⟩² = μ²/2λ = 61.5)
    L_GR = M_Pl²R/2 + Λ_eff + ζ·W·R   (ζ = M_Pl·λ 候選)
    L_SM: Yukawa y_f = √2·M₀·γ_k·S_f/v, W↔Higgs λ_WH = μ²/123

線性化 W = v + δW (v = ⟨W⟩ = √61.5):
    V''(v) = 4μ² ⇒ m_δW² (單位制); 質量尺度 m_δW ~ M₀/2 = 13.95 MeV
    (O100 scripts/10_remaining_items.py: m_7 = 13.95 MeV = M0/2)
    保守上限: m_δW ≤ M₀ = 27.9 MeV (任何激發質量 ≤ 主尺度)
    δW EOM: (□ + m_δW²)δW = −ζ·v·δR + ... (δR = metric perturbation)
    δ = δρ/ρ = 2δW/v (ρ ∝ |W|²)

空間譜 (K_Chain 88-site 環 / 44-site 鏈雙讀法):
    ω_n = 2sin(πn/88)                (O83 propagator 源頭)
    k_n = 44n/R_world                 (O100 C_ℓ 峰投影格: ℓ=44n → k=ℓ/R_world)
    P(k_n) ∝ G_n(0) = 1/(2ω_n)       (零時 propagator = 模振幅²)

符號約定: Δn ≡ n_model − n_BOSS (正 = 模型太扁, 需要 steepening)

檢查:
    A1: δW 質量喺宇宙尺度可忽略 (m_δW Mpc⁻¹ ≪ k_min, 用保守上限 M₀)
    A2: ζWR 耦合修正強度 κζ ≪ 1 (O100 docs/06 量化驗證值 9.4e-22)
    B1: W-field propagator 係下降功率律 (n ≤ −0.5)
    B2: 對照 BOSS broadband (|Δn| < 0.15 = 閉合?)
    C1: 需要嘅補充斜率有冇 IDCM 結構提供?
"""
import numpy as np

R_world = 4129.94          # Mpc (v10.0 kchain_wave_params)
M0_MeV = 27.9009           # MeV (O86 質量尺度)
MEV_TO_MINV = 1.643e-10    # 1 MeV ↔ Mpc⁻¹ (k=E/ħc: 5.068e12 m⁻¹ ÷ 3.0857e22 m/Mpc)
H = 0.6727                 # v10.0 h

# ---------- O86 結構常數 ----------
mu2 = 2.0                  # 單位制 μ² (O39: Σγ_even−Σγ_odd)
lam = 2.0 / 123.0          # λ = 2/123 (O39: 2/[3(N_d−3)])
v2 = mu2 / (2 * lam)       # ⟨W⟩² = 61.5
v = np.sqrt(v2)
m_dW_MeV = M0_MeV / 2      # 質量尺度 m_δW ~ M₀/2 = 13.95 MeV (O100 m_7)
kappa_zeta = 9.4e-22       # O100 docs/06: ζ·W·R 有效耦合 (量化驗證 O86 claim)

# ---------- 格構建 ----------
n_grid = np.arange(1, 45)                       # n = 1..44 (K_Chain 模)
omega_n = 2.0 * np.sin(np.pi * n_grid / 88.0)   # O83 dispersion
k_n = 44.0 * n_grid / R_world                   # Mpc⁻¹ (O100 投影格)
k_h = k_n * H                                   # h/Mpc

# ---------- A1: δW 質量可忽略性 (保守上限 m_δW ≤ M₀) ----------
m_dW_invMpc = m_dW_MeV * MEV_TO_MINV            # 13.95 MeV → 2.29e-9 Mpc⁻¹
m_M0_invMpc = M0_MeV * MEV_TO_MINV              # 上限 27.9 MeV → 4.58e-9 Mpc⁻¹
k_min = k_n[0]
A1 = m_M0_invMpc / k_min < 1e-3                 # 即使 M₀ 全值都 ≪ k_min?
r_mass = m_M0_invMpc / k_min

# ---------- A2: ζWR 耦合可忽略性 ----------
A2 = kappa_zeta < 1e-10

# ---------- B: W-field propagator P(k) ----------
P_W = 1.0 / (2.0 * omega_n)
P_W = P_W / P_W[0]

# 對照點: BOSS CMASS 喺 k_obs 位置 (m=1,2,3 線位)
k_obs_h = np.array([0.079, 0.193, 0.292])       # h/Mpc
P_obs = np.array([18036.0, 5117.0, 2409.0])     # BOSS CMASS P(k) (Mpc³)

# 3 點斜率: 每個 k_obs 取最近模 (argmin), 唔係 n=1,2,3!
idx3 = [int(np.argmin(np.abs(k_h - ko))) for ko in k_obs_h]
slope_W_3 = np.polyfit(np.log(k_obs_h), np.log(P_W[idx3]), 1)[0]
slope_obs_3 = np.polyfit(np.log(k_obs_h), np.log(P_obs), 1)[0]
slope_full = np.polyfit(np.log(k_h), np.log(P_W), 1)[0]

slope_obs_ref = -1.53                      # BOSS range [0.079,0.3] (docs/03 測定)
d_n_3 = slope_W_3 - slope_obs_3            # 正 = 太扁 (vs 3 點)
d_n_ref = slope_W_3 - slope_obs_ref        # 正 = 太扁 (vs range ref)

results = []
def check(name, cond, detail):
    results.append((name, bool(cond), detail))

check("A1_massless", A1, f"m_δW~{m_dW_MeV:.2f} MeV = {m_dW_invMpc:.2e} Mpc⁻¹, 上限 M₀={M0_MeV:.1f} MeV = {m_M0_invMpc:.2e} Mpc⁻¹ ≪ k_min={k_min:.4f} Mpc⁻¹ (r={r_mass:.1e})")
check("A2_zetaWR_negligible", A2, f"κζ={kappa_zeta:.1e} ≪ 1 (O100 docs/06 量化驗證) → ζWR 唔改變傳遞")
check("B1_propagator_falling", slope_W_3 <= -0.5, f"W-field P ∝ k^{{{slope_W_3:+.2f}}} (full {slope_full:+.2f}; 連續極限 −1.00) — 下降功率律")
check("B2_vs_BOSS", abs(d_n_ref) < 0.15, f"IDCM {slope_W_3:+.2f} vs BOSS {slope_obs_ref:+.2f} → Δn = {d_n_ref:+.2f} (正=太扁)")
check("C1_correction_source", False, f"需要 steepen |Δn| = {abs(d_n_ref):.2f} — K_Chain sin dispersion 只會更扁 (v_g→0 喺 Nyquist), 冇 IDCM 結構提供 extra steepening")

print("=" * 72)
print("O86 W-field 線性微擾 → P(k) 傳遞 (O133 scripts/04 v2)")
print("=" * 72)
print(f"\n[背景] ⟨W⟩² = μ²/2λ = {v2:.2f}, ⟨W⟩ = {v:.4f}")
print(f"[背景] V''(v) = 4μ² (單位制); 物理 m_δW ~ M₀/2 = {m_dW_MeV:.3f} MeV (O100 m_7)")
print(f"\n--- A. 可忽略性檢驗 ---")
print(f"  A1: m_δW = {m_dW_invMpc:.3e} Mpc⁻¹ (上限 M₀ = {m_M0_invMpc:.3e} Mpc⁻¹) ≪ k_min = {k_min:.5f} Mpc⁻¹ → 宇宙尺度 δW 質量零極限")
print(f"  A2: κζ = {kappa_zeta:.2e} ≪ 1 (O100 docs/06 量化驗證) → ζWR 無可觀測修正")
print(f"\n--- B. W-field propagator P(k) ---")
print(f"  P(k_n) ∝ 1/(2ω_n), ω_n = 2sin(πn/88), k_n = 44n/R_world (O100 投影格)")
print(f"  3點取模 (最近模): n = {idx3} ↔ k = {k_obs_h}")
for i in range(9):
    print(f"    n={n_grid[i]:2d}  k={k_h[i]:.4f} h/Mpc  ω={omega_n[i]:.4f}  P∝1/ω={P_W[i]:.3f}")
print(f"\n  斜率: W-field 3點: n_W = {slope_W_3:+.2f}  (full {slope_full:+.2f}, 連續極限 −1.00)")
print(f"        BOSS CMASS 同點: n_obs = {slope_obs_3:+.2f}")
print(f"        Δn (3點) = {d_n_3:+.2f} | Δn (vs −1.53 range) = {d_n_ref:+.2f}  (正 = 太扁)")
print(f"\n--- C. 判決 ---")
for name, ok, detail in results:
    print(f"  {'✅' if ok else '🔴'} {name}: {detail}")

n_pass = sum(1 for _, o, _ in results if o)
print(f"\n{'='*72}")
print(f"RESULT: O86 W-field 線性微擾 → P(k) ∝ 1/ω_n, 3點斜率 {slope_W_3:+.2f}")
print(f"        vs BOSS {slope_obs_ref:+.2f} → 太扁 Δn = {d_n_ref:+.2f} (需 steepen {abs(d_n_ref):.2f})")
print(f"        連續極限 −1.00 都唔夠 (仍需 {(-1.0 - slope_obs_ref):+.2f}); m_δW 同 κζ 可忽略性 PASS = 傳遞唔受 W-field 物理修改")
print(f"        ⇒ broadband 形狀來源唔係 W-field 自由微擾; 見 docs/05 三路徑綜合")
print(f"        PASS = {n_pass}/5")
exit(0 if n_pass == 5 else 1)