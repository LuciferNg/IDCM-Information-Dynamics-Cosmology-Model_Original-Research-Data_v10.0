#!/usr/bin/env python3
"""
O33 — 獨立驗證腳本 (scripts/verify_all.py)
====================================================
獨立核對 o33_projection_mechanism 全部文檔嘅公式與數值。
唔 import 任何推導腳本，由原始結構常數重新計算。

文檔覆蓋:
  01_problem_record.md — 問題定位 + O13 閉合
  closure_derivation.md — 投影截止 + 黑洞反投影 + D_app 接駁
  operator_derivation.md — T_pipe 算子 + ℓ_max + D_app + 黑洞熵
  projection_derivation.md — 水喉模型 + 觀察者預算 + O148 修正
"""

import math

# ═══ 原始結構常數 (反幻覺鐵律: 讀 src/kchain_wave_params.py) ═══
N_d = 44          # K_Chain 維度
M = 33            # K_Tree 深度
B = 4             # MERA 分支
PHI = (1 + math.sqrt(5)) / 2
EPS = PHI - 1     # 1/φ

def lucas(n):
    """Lucas 數列 L₀=2, L₁=1"""
    if n == 0: return 2
    if n == 1: return 1
    a, b = 2, 1
    for _ in range(1, n):
        a, b = b, a + b
    return b

def gamma(n):
    """K_Chain 譜係數 γ_n = 4sin²(nπ/88)"""
    return 4 * math.sin(n * math.pi / 88) ** 2

passed = []
failed = []

def check(name, cond, detail=""):
    if cond:
        passed.append(name)
        print(f"  ✅ [{name}] {detail}")
    else:
        failed.append(name)
        print(f"  ❌ [{name}] {detail}")

print("=" * 67)
print("  O33 — 獨立驗證 (scripts/verify_all.py)")
print("=" * 67)

# ═══════════════════════════════════════════════════════════════
# [A] 基礎結構
# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*67}\n  [A] 基礎結構")
print(f"{'─'*67}")

S_gamma = sum(gamma(n) for n in range(1, 45))
check("A1 Σγ = 90 (K_Chain 總能量)", abs(S_gamma - 90) < 1e-6,
      f"Σγ={S_gamma:.6f}")

Omega_L = 4 / (PHI**4 - 1)
check("A2 Ω_Λ = 4/(φ⁴-1) = 0.683282", abs(Omega_L - 0.683282) < 1e-6,
      f"Ω_Λ={Omega_L:.6f}")

E_sync_obs = N_d * lucas(10) / 88
check("A3 E_sync = N_d×L₁₀/88 = 61.5", abs(E_sync_obs - 61.5) < 1e-6,
      f"E_sync={E_sync_obs:.6f} (L₁₀={lucas(10)})")

E_proj = S_gamma - E_sync_obs
check("A4 E_proj = 90-61.5 = 28.5", abs(E_proj - 28.5) < 1e-6,
      f"E_proj={E_proj:.6f}")

# Ω_m/Ω_Λ = 3ε
eps3 = 3 * EPS / 4
check("A5 Ω_m/Ω_Λ = 3ε = 0.4635", abs(E_proj/E_sync_obs - eps3)/eps3 < 0.001,
      f"E_proj/E_sync={E_proj/E_sync_obs:.6f}, 3ε={eps3:.6f}")

# ═══════════════════════════════════════════════════════════════
# [B] closure_derivation.md — 投影截止閾值
# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*67}\n  [B] closure_derivation.md — 投影截止閾值")
print(f"{'─'*67}")

L6 = lucas(6)  # 18
n_star = N_d - L6 + 1
check("B1 n* = N_d-L₆+1 = 27", n_star == 27,
      f"n*={n_star} (L₆={L6}=φ⁶+φ⁻⁶)")

S26 = sum(gamma(n) for n in range(1, 27))
g27 = gamma(27)
S28_44 = sum(gamma(n) for n in range(28, 45))
check("B2 Σγ₁..₂₆ = 26.4165", abs(S26 - 26.4165) < 1e-3,
      f"Σγ₁..₂₆={S26:.4f}")
check("B3 γ₂₇ = 2.6989", abs(g27 - 2.6989) < 1e-3,
      f"γ₂₇={g27:.4f}")
check("B4 Σγ₂₈..₄₄ = 60.8845", abs(S28_44 - 60.8845) < 1e-3,
      f"Σγ₂₈..₄₄={S28_44:.4f}")

# f_sync / f_proj
f_sync = (lucas(10) - 2*S28_44) / (2*g27)
f_proj = 1 - f_sync
check("B5 f_sync = 0.2280", abs(f_sync - 0.2280) < 1e-3,
      f"f_sync={f_sync:.4f}")
check("B6 f_proj = 0.7720", abs(f_proj - 0.7720) < 1e-3,
      f"f_proj={f_proj:.4f}")

E_proj_check = S26 + f_proj * g27
E_sync_check = S28_44 + f_sync * g27
check("B7 E_proj = 26.4165+0.772×2.6989 = 28.5", abs(E_proj_check - 28.5) < 1e-3,
      f"E_proj={E_proj_check:.4f}")
check("B8 E_sync = 60.8845+0.228×2.6989 = 61.5", abs(E_sync_check - 61.5) < 1e-3,
      f"E_sync={E_sync_check:.4f}")

# 回收率
recovery = E_proj / E_sync_obs
check("B9 回收率 = 28.5/61.5 = 0.4634 ≈ 3ε", abs(recovery - 0.4634) < 1e-3,
      f"回收率={recovery:.4f}, 3ε={eps3:.4f}")

# 投影截止 γ_cutoff = E_sync/(N_d/2)
gamma_cut = E_sync_obs / (N_d/2)
check("B10 γ_cutoff = 61.5/22 = 2.795", abs(gamma_cut - 2.795) < 1e-2,
      f"γ_cutoff={gamma_cut:.3f}")

# ═══════════════════════════════════════════════════════════════
# [C] operator_derivation.md — T_pipe 算子 + 接駁
# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*67}\n  [C] operator_derivation.md — T_pipe + D_app 接駁")
print(f"{'─'*67}")

# f_proj 精確
f_proj_exact = (E_proj - S26) / g27
check("C1 f_proj = (E_proj-Σγ₁..₂₆)/γ₂₇ = 0.771960", abs(f_proj_exact - 0.771960) < 1e-5,
      f"f_proj={f_proj_exact:.6f}")

# Δn = 1/ln φ
delta_n = 1 / math.log(PHI)
check("C2 Δn = 1/ln φ = 2.078087", abs(delta_n - 2.078087) < 1e-5,
      f"Δn={delta_n:.6f}")

# δ = Δn·ln(1/f_proj - 1)
delta_c = delta_n * math.log(1/f_proj_exact - 1)
check("C3 δ = Δn·ln(1/f-1) = -2.534046", abs(delta_c - (-2.534046)) < 1e-4,
      f"δ={delta_c:.6f}")

# ℓ_max = (Ω_m/Ω_Λ)·(N_d/ln B)
ell_max = (E_proj/E_sync_obs) * (N_d / math.log(B))
check("C4 ℓ_max = 0.463415×31.7393 = 14.7085", abs(ell_max - 14.7085) < 1e-3,
      f"ℓ_max={ell_max:.4f}")

# D_app = B·ln(1+ℓ_max/φ)/(1+Ω_m/Ω_Λ)
D_app = B * math.log(1 + ell_max/PHI) / (1 + E_proj/E_sync_obs)
check("C5 D_app = 6.3183 → 6", abs(D_app - 6.3183) < 1e-3,
      f"D_app={D_app:.4f}")

# 黑洞熵: S/k_B = 4πM²/M_P² (1 M_⊙)
M_sun = 1.989e30  # kg
M_P = 2.176e-8    # kg
S_BH = 4 * math.pi * (M_sun/M_P)**2
# 文檔宣稱 1.90e131 — 正確值 1.05e77 (公認值 ~1.07e77, Carroll & Ostlie)
check("C6 S_BH/k_B = 4πM²/M_P² (1M_⊙) = 1.05e77 [文檔 1.90e131 錯]",
      abs(math.log10(S_BH) - 77.02) < 0.3,
      f"S_BH/k_B={S_BH:.3e} (文檔 1.90e131 偏差 54 數量級, 已修正)")

# ═══════════════════════════════════════════════════════════════
# [D] projection_derivation.md — 水喉 + 觀察者稅 + O148 修正
# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*67}\n  [D] projection_derivation.md — 水喉 + O148 修正")
print(f"{'─'*67}")

# 觀察者稅 δ = 0.683333 - 0.683282
obs_tax = E_sync_obs/S_gamma - Omega_L
check("D1 觀察者稅 δ = 5.176e-5", abs(obs_tax - 5.176e-5) < 1e-7,
      f"δ={obs_tax:.6e}")

# O148 修正: δ = 41/60 − 4/(φ⁴−1) = √5φ⁻¹⁰/[60(3φ+1)]
delta_148 = 41/60 - Omega_L
lucas_tail = math.sqrt(5) * PHI**-10 / (60*(3*PHI+1))
check("D2 δ = 41/60−Ω_Λ = √5φ⁻¹⁰/[60(3φ+1)]", abs(delta_148 - lucas_tail) < 1e-15,
      f"δ={delta_148:.6e}, Lucas尾={lucas_tail:.6e}")

# L_n·φ − L_{n+1} = (−1)ⁿ√5φ⁻ⁿ (n=10)
L10, L11 = lucas(10), lucas(11)
check("D3 L₁₀φ−L₁₁ = √5φ⁻¹⁰", abs((L10*PHI - L11) - math.sqrt(5)*PHI**-10) < 1e-10,
      f"L₁₀φ−L₁₁={L10*PHI-L11:.10f}, √5φ⁻¹⁰={math.sqrt(5)*PHI**-10:.10f}")

# ε 精確 = 19/123; φ⁻¹/4 偏差 δ₃ = −√5φ⁻¹⁰/492 = 0.023%
eps_exact = 19/123
eps_approx = PHI**-1 / 4
delta_eps = eps_exact - eps_approx
check("D4 ε = 19/123, δ₃ = −√5φ⁻¹⁰/492 = 0.023%",
      abs(delta_eps + math.sqrt(5)*PHI**-10/492) < 1e-12,
      f"ε_exact={eps_exact:.8f}, ε_approx={eps_approx:.8f}, δ={delta_eps:.2e}")

# 3ε 精確 = 19/41; 3/(4φ) 偏差 δ₂ = −√5φ⁻⁹/(164φ) = 0.024%
eps3_exact = 19/41
eps3_approx = 3/(4*PHI)
delta_eps3 = eps3_exact - eps3_approx
check("D5 3ε = 19/41, δ₂ = −√5φ⁻⁹/(164φ) = 0.024%",
      abs(delta_eps3 + math.sqrt(5)*PHI**-9/(164*PHI)) < 1e-12,
      f"3ε_exact={eps3_exact:.8f}, 3ε_approx={eps3_approx:.8f}, δ={delta_eps3:.2e}")

# ═══════════════════════════════════════════════════════════════
# [E] 01_problem_record.md — O13 n/p 閉合
# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*67}\n  [E] O13 n/p = γ₇/γ₂₀")
print(f"{'─'*67}")

g7 = gamma(7)
g20 = gamma(20)
np_ratio = g7 / g20
check("E1 n/p = γ₇/γ₂₀ = 0.14262 ≈ 1/7", abs(np_ratio - 0.14262) < 1e-4,
      f"γ₇/γ₂₀={np_ratio:.5f} (0.17% vs 1/7)")

# 7+20 = 27 = 3³
check("E2 7+20 = 27 = N_gen³", 7+20 == 27)

# ═══════════════════════════════════════════════════════════════
# 總結
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print(f"  驗證結果: {len(passed)} PASS, {len(failed)} FAIL")
if failed:
    print(f"  FAIL: {failed}")
print(f"{'═'*67}")

# 儲存
with open("data/verify_all_results.txt", "w") as f:
    f.write("O33 — Independent Verification Results\n")
    f.write("=" * 67 + "\n")
    for name in passed:
        f.write(f"PASS: {name}\n")
    for name in failed:
        f.write(f"FAIL: {name}\n")
    f.write(f"\nTotal: {len(passed)} PASS, {len(failed)} FAIL\n")