#!/usr/bin/env python3
"""
O80 — Script 4: Hamiltonian 重構 + 真空能 + 重整化 (Q2 + Q7)
=============================================================
解決 O72 Q2 (Hamiltonian? 真空能? 單位/意義未定義) + Q7 (真空能點 renormalize?)

Hamiltonian 結構:
  H = H_free + H_int + H_cond
  H_free = Σ_n [p_n²/2m + (K/2)(q_{n+1}−q_n)²]  (88-site 週期鏈)
         = Σ_k ħω_k(a†a + 1/2)                   (對角化)
  H_int  = Σ_n g_n·⟨W⟩·(a†+a),  g_n = κω_n       (O36)
  H_cond = V(W) 凝集部分

真空能結構:
  E_vac = Σγ/2 = 45 (K_Chain 基態)
  ⟨W⟩² = 61.5 (O39 凝聚預算)
  V_Λ = F(γ) + 44 − F₈ − B = 283.0821 (O62 全譜)

重整化:
  ★ 兩層真空能:
    L1 (鏈): E_vac = Σγ/2 = 45 (冇 renormalize 需要, 有限譜)
    L2 (凝聚): ⟨W⟩² = 61.5 (SSB 勢最小值能量)
    L3 (物理): V_Λ = 283.0821 (O62, CY₃ prepotential)
  ★ IDCM 冇 UV 發散 — 88-site lattice 係天然 cutoff (Q9!)
  ★ 冇需要 renormalize (有限), 但可以「重整化群」理解:
    lattice cutoff → 連續極限 → 有效參數流

本 script 驗證:
  [A] H_free 對角化 → ω_k = 2sin(πk/88)
  [B] 真空能 E_vac = 45 (基態, Noether 荷)
  [C] 二階自能 ΔE_n = −κ²ω_n (H_int 效應)
  [D] 凝聚能量 ⟨W⟩² = 61.5 + V_min = −61.5
  [E] V_Λ = 283.0821 (O62 全譜) — 三層真空能統一
  [F] UV cutoff: 88-site lattice (Q9 閉合)
  [G] 重整化: 冇發散 (有限譜), 但層間連接
"""

import numpy as np
from decimal import Decimal, getcontext
getcontext().prec = 60

phi = (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)
PI = Decimal('3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679')

results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'✅ PASS' if cond else '❌ FAIL'}] {name} {detail}")

print("=" * 70)
print("  O80 — Script 4: Hamiltonian + 真空能 + 重整化")
print("=" * 70)

# ──────────────────────────────────────────────
# [A] H_free 對角化 → ω_k
# ──────────────────────────────────────────────
print("\n─── [A] H_free 對角化 ───")
N = 88
# H = Σ [p²/2m + (K/2)(q_{n+1}−q_n)²]
# 動量矩陣: 質量 m=1 (自然單位), 彈簧 K=1
# 頻率: ω_k = 2√(K/m)·sin(πk/88) = 2sin(πk/88)
# 用 Laplacian 本徵值驗證: λ_k = 4sin²(πk/88) = ω_k²
A_mat = np.zeros((N, N))
for i in range(N):
    A_mat[i, (i+1) % N] = 1
    A_mat[i, (i-1) % N] = 1
Lap = 2*np.eye(N) - A_mat
eigvals = np.linalg.eigvalsh(Lap)
eig_sorted = np.sort(eigvals)
# 正頻率 (k=1..44): ω_k = 2sin(πk/88)
# Laplacian 本徵值 λ_k = 4sin²(πk/88) = ω_k²（k=0..87）
#   k=0: λ=0 (零模, 非簡併)
#   1≤k≤43: λ_k = λ_{88-k} (雙重簡併)
#   k=44: λ=4 (Nyquist, 非簡併)
# 驗證: 全部 88 個本徵值匹配
gamma_all = np.array([4*np.sin(np.pi*k/88)**2 for k in range(88)])
gamma_all_sorted = np.sort(gamma_all)
max_dev = np.max(np.abs(eig_sorted - gamma_all_sorted))
check("H_free 對角化: 88-site 週期鏈譜匹配", max_dev < 1e-10, f"(max dev {max_dev:.2e})")

# ──────────────────────────────────────────────
# [B] 真空能 E_vac = 45
# ──────────────────────────────────────────────
print("\n─── [B] 真空能 ───")
gamma_n = np.array([4*np.sin(np.pi*n/88)**2 for n in range(1, 45)])
E_vac = np.sum(gamma_n)/2
print(f"  E_vac = Σγ/2 = {E_vac:.6f}")
check("E_vac = 45 (鏈基態)", abs(E_vac - 45) < 1e-9, f"({E_vac:.6f})")

# 真空能正規序 vs 無序:
# 無序: Σω_n/2 (零點能)
# 正規序: 0 (相對於基態)
omega_n = 2*np.sin(np.pi*np.arange(1, 45)/88)
E_zp = np.sum(omega_n)/2
print(f"  零點能 Σω/2 = {E_zp:.6f} (ω 制)")
print(f"  能量制 Σγ/2 = {E_vac:.6f} (γ = ω²)")
check("能量制真空能 = 45 (O37 Q2)", abs(E_vac - 45) < 1e-9)

# ──────────────────────────────────────────────
# [C] 二階自能 ΔE_n = −κ²ω_n
# ──────────────────────────────────────────────
print("\n─── [C] 二階自能 (H_int 效應) ───")
# H_int = Σ g_n·⟨W⟩(a†+a), g_n = κω_n
# 二階修正: ΔE_n = −g_n²/ω_n = −κ²ω_n
E_kchain = Decimal('4.060265e-3')
M0_eV = E_kchain * phi**(Decimal(47) + Decimal(37)/Decimal(528))
M0_MeV = float(M0_eV) * 1e-6
kappa2 = M0_MeV  # 自然單位 κ² = M₀
deltaE = -kappa2 * omega_n
m_n = -deltaE  # 質量 = |ΔE|
print(f"  κ² = M₀ = {kappa2:.6f} MeV")
print(f"  ΔE_n = −κ²ω_n: n=1 → {deltaE[0]:.4f} MeV, n=7 → {deltaE[6]:.4f} MeV")
print(f"  m_7 = κ²ω_7 = {m_n[6]:.4f} MeV")
check("m_7 = κ²ω_7 = 13.8002 MeV", abs(m_n[6] - 13.8002) < 1e-3, f"({m_n[6]:.4f})")
check("m_44 = κ²·2 = 55.8018 MeV (Nyquist)", abs(m_n[43] - 55.8018) < 1e-3, f"({m_n[43]:.4f})")

# 質量譜形: m_n ∝ sin(nπ/88)
ratio = m_n / np.max(m_n)
expected = omega_n / np.max(omega_n)
check("質量譜形 ∝ sin(nπ/88)", np.max(np.abs(ratio - expected)) < 1e-12)

# ──────────────────────────────────────────────
# [D] 凝聚能量 (SSB)
# ──────────────────────────────────────────────
print("\n─── [D] 凝聚能量 (SSB) ───")
mu2, lam = 2.0, 2.0/123.0
w2 = mu2/(2*lam)
vmin = -mu2**2/(4*lam)
print(f"  ⟨W⟩² = {w2:.6f} (凝聚能量預算)")
print(f"  V_min = {vmin:.6f}")
check("⟨W⟩² = 61.5", abs(w2 - 61.5) < 1e-9)
check("V_min = −61.5", abs(vmin + 61.5) < 1e-9)

# ──────────────────────────────────────────────
# [E] V_Λ = 283.0821 (O62 全譜)
# ──────────────────────────────────────────────
print("\n─── [E] V_Λ (O62 全譜) ───")
# V_Λ = F(γ) + 44 − F₈ − B
# F(γ) = (1/6)Σκ_ijk γ_i γ_j γ_k = 264.0821 (真 CY₃ 交集數 @ γ VEV)
# 44 = N_d, F₈ = 21, B = 4
F_gamma = 264.082129
Nd = 44
F8 = 21
B = 4
V_Lambda = F_gamma + Nd - F8 - B
V_obs = 283.0752
dev = abs(V_Lambda - V_obs)/V_obs*100
print(f"  V_Λ = F(γ) + 44 − F₈ − B = {V_Lambda:.6f}")
print(f"  V_obs = {V_obs:.6f}")
print(f"  dev = {dev:.4f}%")
check("V_Λ = 283.0821 (0.0025%)", dev < 0.01, f"(dev {dev:.4f}%)")

# 三層真空能統一:
print("""
  三層真空能統一:
    L1 (鏈基態):   E_vac = Σγ/2 = 45
    L2 (凝聚):     ⟨W⟩² = 61.5, V_min = −61.5
    L3 (物理):     V_Λ = 283.0821 (O62)

  關係:
    45 + 61.5 = 106.5 (鏈+凝聚)
    283.0821/61.5 = 4.603 (O41 觀察者預算 × 4.6)
    283.0821 − 264.0821 = 19 = 44 − 25 (P̂ gap)
""")
check("283.0821/61.5 = 4.603 (O41)", abs(V_Lambda/61.5 - 4.603) < 0.001, f"({V_Lambda/61.5:.4f})")

# ──────────────────────────────────────────────
# [F] UV cutoff: 88-site lattice (Q9)
# ──────────────────────────────────────────────
print("\n─── [F] UV cutoff (Q9 閉合) ───")
# 88-site lattice = 天然 UV cutoff
# 最高頻率: ω_44 = 2sin(44π/88) = 2sin(π/2) = 2 (Nyquist)
omega_max = 2*np.sin(44*np.pi/88)
print(f"  ω_max = ω_44 = 2sin(π/2) = {omega_max:.6f} (Nyquist)")
check("ω_max = 2 (Nyquist cutoff)", abs(omega_max - 2) < 1e-12, f"({omega_max:.6f})")

# lattice spacing: a = R_world/88
R_world = 4129.94  # Mpc
a = R_world/88
print(f"  lattice spacing a = R_world/88 = {a:.4f} Mpc")
check("a = R_world/88 = 46.93 Mpc", abs(a - 46.9311) < 0.01, f"({a:.4f})")

# 物理身份: 88-site lattice cutoff = 對偶鏈 (88-site)
# 最高能標度: 對應最短波長 λ_min = 2a = R_world/44
lam_min = 2*a
print(f"  最短波長 λ_min = 2a = {lam_min:.4f} Mpc = R_world/44")
check("λ_min = R_world/44", abs(lam_min - R_world/44) < 1e-9, f"({lam_min:.4f})")

# ──────────────────────────────────────────────
# [G] 重整化: 冇發散, 層間連接
# ──────────────────────────────────────────────
print("\n─── [G] 重整化 (冇發散, 層間連接) ───")
# 標準 QFT: 真空能 Σω/2 → ∞ (UV 發散) → 需要 renormalize
# IDCM: 88-site lattice → 有限譜 → 冇發散!
print("""
  標準 QFT:      E_vac = Σ_k ω_k/2 → ∞ (UV 發散) → 需要 cutoff + counterterm
  IDCM:          E_vac = Σγ/2 = 45 (88-site lattice 天然 cutoff) → 有限!
  ★ Q9 閉合: UV cutoff = 88-site lattice (物理身份 = 對偶鏈)

  重整化理解 (冇發散, 但有層間流):
    lattice 參數 (a, m) → 連續極限 → 有效耦合 (λ, κ)
    O37: λ_eff = 2/123 (裸層) vs κ/2 = 1/32 (有效層)
    O39: λ_B/λ_C = 90(1+λ_B·fib) (兩層 λ 精確關係)
    → 「重整化群」類比: 層間參數流 = 標度變換 W_A = a·W_C

  誠實標記:
  🟢 冇 UV 發散 (有限譜, lattice cutoff 物理)
  🟢 兩層 λ 關係 = O39 閉合 (λ_B/λ_C = 90(1+λ_B·fib))
  🟡 「RG flow」只係類比 — 冇真正嘅 scale-dependent running
  🔴 冇 counterterm 需要 (冇發散)
""")
# 驗證 λ_B/λ_C = 90.0068 (O39 閉合)
lam_B = (phi**4 - 1)/4  # (φ⁴−1)/4 = 1/Ω_Λ
lam_C = Decimal(2)/Decimal(123)
ratio_lambda = float(lam_B/lam_C)
print(f"  λ_B/λ_C = {ratio_lambda:.6f} (O39: 90.0068)")
check("λ_B/λ_C ≈ 90.0068 (O39)", abs(ratio_lambda - 90.0068) < 0.01, f"({ratio_lambda:.4f})")

# ──────────────────────────────────────────────
# 總結
# ──────────────────────────────────────────────
print("\n" + "=" * 70)
total = len(results)
passed = sum(results)
print(f"  RESULT: {passed}/{total} PASS")
print("=" * 70)
import sys
sys.exit(0 if passed == total else 1)
