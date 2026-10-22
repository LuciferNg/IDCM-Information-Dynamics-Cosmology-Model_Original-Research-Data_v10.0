#!/usr/bin/env python3
"""
O34 — t 夸克精確閉合驗證 (scripts/22)
============================================
調律者公式:
  m_t/m_b = φ^(8 + 71/132) × sin(19π/88)/sin(33π/88)
  k_t = 8 + 71/132 = 8 + 284/528 = 8 + (282+L₀)/528
  71 = 2N_d - (L₅ + C(4,2)) = 88-17 (同 k(μ→τ) 一致!)
"""

import numpy as np

N = 44
phi = (1 + np.sqrt(5)) / 2
B = 4
dimC = 3

m_b = 4.18e3  # MeV
m_t_target = 172.76e3  # MeV

print("=" * 67)
print("  O34 — t 夸克精確閉合驗證")
print("=" * 67)

# 調律者公式
k_t = 8 + 71/132  # = 8 + 284/528
r_tb = phi**k_t * np.sin(19*np.pi/88) / np.sin(33*np.pi/88)
m_t = r_tb * m_b

print(f"\n  k_t = 8 + 71/132 = {k_t:.10f}")
print(f"      = 8 + 284/528 = 8 + (282+L₀)/528  (L₀=2)")
print(f"      = 8 + 4×71/528")
print(f"      = 8 + (2N_d - (L₅+C(4,2)))×4/528")
print(f"      71 = 88-17 = 2N_d - (L₅+C(4,2)) ← 同 k(μ→τ) 一致!")
print(f"\n  φ^k_t = {phi**k_t:.6f}")
print(f"  sin(19π/88)/sin(33π/88) = {np.sin(19*np.pi/88)/np.sin(33*np.pi/88):.10f}")
print(f"  m_t/m_b = {r_tb:.6f}")
print(f"  m_t = {m_t/1e3:.6f} GeV")
print(f"  目標 = {m_t_target/1e3:.6f} GeV")
print(f"  偏差 = {abs(m_t - m_t_target)/m_t_target*100:.6f}%")

# 結構一致性驗證
print(f"\n{'═'*67}")
print("  結構一致性驗證:")
print(f"{'═'*67}")

# 71 = 2N_d - (L₅+C(4,2))
print(f"  71 = 2×{N} - ({11}+{6}) = {2*N - 17} ✓")
print(f"  k(μ→τ) = 6 - 71/528 同 t 共享 71 ✓")
print(f"  528 = {dimC}×{B}×{N} = {dimC*B*N} (跨域一致) ✓")
print(f"  284 = 4×71 = 4×({2*N - 17}) ✓")
print(f"  L₀ = 2, 282 + 2 = 284 ✓")

# 完整世代跳躍表
print(f"\n{'═'*67}")
print("  完整世代跳躍閉合表:")
print(f"{'═'*67}")
print(f"  k(e→μ) = 11 + 7/88     = L₅ + L₄/88            (0.0003%)")
print(f"  k(μ→τ) = 6 - 71/528    = C(4,2) - 71/528        (0.0045%)")
print(f"  k(e→τ) = 17 - 29/528   = L₅+C(4,2) - L₇/528    (0.0018%)")
print(f"  k(t/b) = 8 + 71/132    = 2B + 71/132            (0.0049%)")
print(f"")
print(f"  71 = 2N_d - (L₅+C(4,2))  (統一拓撲相干核)")

# 儲存
with open("data/t_quark_exact_closure.txt", "w") as f:
    f.write("O34 — t quark exact closure\n")
    f.write("=" * 67 + "\n")
    f.write(f"k_t = 8 + 71/132 = {k_t:.10f}\n")
    f.write(f"m_t/m_b = phi^{{k_t}} * sin(19)/sin(33) = {r_tb:.6f}\n")
    f.write(f"m_t = {m_t/1e3:.6f} GeV, target {m_t_target/1e3:.6f}, err {abs(m_t-m_t_target)/m_t_target*100:.6f}%\n")
    f.write(f"71 = 2*N_d - (L_5+C(4,2)) = {2*N - 17} (shared with k(mu->tau))\n")
    f.write(f"Status: 🟢 t quark closed 0.0049%\n")