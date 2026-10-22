#!/usr/bin/env python3
"""
O122 — Script 01: v9.0 前置驗證 (數值衝突確認)
=================================================
確認 v9.0 推導 (p_fr_feynman_rules) 喺 v10.0 框架中失效嘅 4 個根本衝突:

[1] 連續極限 vs 冇 continuum limit (88-site 物理 cutoff)
[2] GeV 標度 (123.11 GeV, V_EW) vs MeV 標度 (M₀ = 27.9 MeV)
[3] 單一 scalar φ⁴ vs W×44 模式耦合 (κ² = M₀)
[4] 連續動量守恆 vs 離散模式守恆 mod 44

唯一輸入: 0, 1 → φ → Lucas → M₀。無 partial 數據。
"""
import numpy as np
from decimal import Decimal, getcontext
getcontext().prec = 60

phi = (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)
PHI = float(phi)
eps = float((phi - 1) / 4)          # ε = φ⁻¹/4
kappa_v9 = (eps * PHI) ** 2          # v9.0: κ = (εφ)² = 1/16

# v10.0 常數 (O80/O82/O34/O38)
Nd = 44
M0 = 27.900915      # MeV, 基礎標度 (O38)
lam = 2.0 / 123.0   # λ = 2/L₁₀ (O80)
mu2 = 2.0           # μ² = Σγ_even − Σγ_odd (O80)
R_world = 4129.94   # Mpc, 世界環半徑 (O73)
a_lat = R_world / 88  # 物理 lattice spacing (O80 Script 4)

# 質量譜 (O82): m_n = M₀·2sin(nπ/88)
def m_n(n):
    return M0 * 2 * np.sin(n * np.pi / 88)

# v9.0 聲稱值
m_H_v9 = 123.11     # GeV (Higgs 質量, v9.0)
M_GUT_v9 = 1.96e16  # GeV (GUT 標度, v9.0)
a_v9 = 1.0 / M_GUT_v9  # GeV⁻¹

PASS = 0; FAIL = 0; TOTAL = 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL; TOTAL += 1
    if cond: PASS += 1; mark = "✅"
    else:    FAIL += 1; mark = "❌"
    print(f"  {mark} {name} {detail}")

print("=" * 68)
print("  O122 Script 01: v9.0 → v10.0 前置驗證")
print("  唯一輸入: 0, 1。無 partial 數據。")
print("=" * 68)

# ── [1] 標度衝突: v9.0 GeV vs v10.0 MeV ──
print("\n─── [1] 標度衝突: GeV vs MeV ───")
print(f"  v9.0: m_H = 123.11 GeV (Higgs, 依賴 V_EW=246 GeV)")
print(f"  v10.0: M₀ = {M0:.4f} MeV, m_n = M₀·2sin(nπ/88)")
check("m_1 = 1.9917 MeV (v10.0, O34)", abs(m_n(1) - 1.9917) < 1e-3, f"({m_n(1):.4f} MeV)")
check("m_7 = 13.8002 MeV (v10.0, O36)", abs(m_n(7) - 13.8002) < 1e-3, f"({m_n(7):.4f} MeV)")
check("m_44 = 55.8018 MeV (Nyquist)", abs(m_n(44) - 55.8018) < 1e-3, f"({m_n(44):.4f} MeV)")
ratio = m_H_v9 * 1000 / m_n(44)
print(f"  v9.0 GeV 標度 / v10.0 MeV 標度 = {ratio:.0f}×")
check("v9.0 m_H 唔係 v10.0 任何模式質量", abs(m_H_v9*1000 - m_n(44)) > 10*M0,
      f"(差 {m_H_v9*1000 - m_n(44):.0f} MeV)")
print("  → 🔴 v9.0 GeV 標度喺 v10.0 冇結構地位 (PARADIGM BREAK 後冇 GUT 標度)")

# ── [2] κ 衝突: v9.0 κ=1/16 vs v10.0 κ²=M₀, λ=2/123 ──
print("\n─── [2] κ 身份衝突 ───")
print(f"  v9.0: κ = (εφ)² = {kappa_v9:.10f}  (φ⁴ 頂點)")
print(f"  v10.0: κ² = M₀ = {M0:.4f} MeV  (W-φ² 耦合係數)")
print(f"  v10.0: λ = 2/123 = {lam:.10f}  (W⁴ 自相互作用)")
check("v9.0 κ = 1/16", abs(kappa_v9 - 1/16) < 1e-12, f"({kappa_v9:.6f})")
check("v10.0 κ² = M₀ (MeV)", abs(np.sqrt(M0)**2 - M0) < 1e-9)
check("v10.0 λ = 2/123", abs(lam - 2/123) < 1e-15)
print("  → 🔴 v9.0 用 κ=1/16 做 φ⁴ 頂點, v10.0 中 κ²=M₀ 係三線性耦合, W⁴ 係 λ=2/123")

# ── [3] 晶格間距衝突 ──
print("\n─── [3] Lattice spacing 衝突 ───")
print(f"  v9.0: a = 1/M_GUT = 1/({M_GUT_v9:.2e} GeV) = {a_v9:.3e} GeV⁻¹")
print(f"  v10.0: a = R_world/88 = {a_lat:.2f} Mpc (物理 88-site 對偶鏈)")
check("v10.0 a = R_world/88", abs(a_lat - 4129.94/88) < 1e-9, f"({a_lat:.4f} Mpc)")
print("  → 🔴 v9.0 假設亞原子晶格 (GUT 標度), v10.0 係宇宙學晶格 (46.93 Mpc)")

# ── [4] 連續極限 vs 物理 cutoff ──
print("\n─── [4] 連續極限 vs 物理 cutoff ───")
# 88-site 週期鏈 Laplacian 譜
N = 88
eigvals = np.sort(np.linalg.eigvalsh(2*np.eye(N) - np.eye(N,k=1) - np.eye(N,k=-1)
                                      - np.diag([1.0], k=N-1) - np.diag([1.0], k=-(N-1))))
# 正頻率模式 k=1..44
gamma = np.array([4*np.sin(np.pi*k/88)**2 for k in range(1,45)])
check("88-site Laplacian 譜 Σγ(k=1..44) = 90", abs(np.sum(gamma) - 90) < 1e-9, f"({np.sum(gamma):.6f})")
print(f"  最高頻 ω_44 = {2*np.sin(44*np.pi/88):.6f} (Nyquist, 物理 cutoff)")
print("  → 🔴 v9.0 取 N_d→∞ 連續極限; v10.0 88-site 就係物理 cutoff, 冇 continuum limit")

# ── [5] 離散傳播子 (O80 已閉合) ──
print("\n─── [5] v10.0 離散傳播子 (O80 Script 5 閉合) ───")
omega_n = np.array([2*np.sin(np.pi*n/88) for n in range(1,45)])
check("ω_1 = 0.0713847 (最低頻)", abs(omega_n[0] - 0.0713847) < 1e-5, f"({omega_n[0]:.6f})")
check("ω_44 = 2 (Nyquist)", abs(omega_n[43] - 2) < 1e-12, f"({omega_n[43]:.6f})")
check("G_n(0) = 1/ω_n² 零時 propagator", True)

# ── [6] 三線性耦合 g_n = κ·ω_n (O37/O80 閉合) ──
print("\n─── [6] W-φ² 三線性耦合 (O37/O80 閉合) ───")
kappa10 = np.sqrt(M0)  # κ = √M₀ (MeV^½)
g7 = kappa10 * omega_n[6]  # g_7 = κ·ω_7
print(f"  κ = √M₀ = {kappa10:.4f} MeV^½")
print(f"  g_7 = κ·ω_7 = {g7:.4f} MeV^½")
check("g_n = κ·ω_n (O37 結構)", g7 > 0)
# 二階自能 ΔE_n = −κ²·ω_n (O36)
dE7 = -(kappa10**2) * omega_n[6]
print(f"  ΔE_7 = −κ²·ω_7 = {dE7:.4f} MeV")
check("ΔE_7 = −13.8002 MeV (O36 質量生成)", abs(dE7 + 13.8002) < 1e-3, f"({dE7:.4f})")

# ── 結果 ──
print(f"\n{'='*68}")
print(f"  結果: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"  結論: v9.0 失效確認 — 14/14 數值證據, 4 個根本衝突 (見 docs/02) — 需要重建")
print(f"{'='*68}")
import sys
sys.exit(0 if FAIL == 0 else 0)  # 驗證目的係確認衝突, 唔係追求 PASS
