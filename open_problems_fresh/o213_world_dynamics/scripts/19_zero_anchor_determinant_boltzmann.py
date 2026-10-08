#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O213 scripts/19 — R9 零錨第五輪: 譜 determinant + Boltzmann 形式（2026-10-08）
=======================================================================
承接 scripts/18（Σγ²=272=B²(B²+1), Σγ²+Σκ=264）。本輪:

  A. ★ 譜 determinant 定理: Π_{n=1}^{44} γ_n = 4N_d = 176 EXACT ?
     推導: ∏sin(nπ/88) = 88^{1/2}/2^{87/2} (n=1..44, 對稱折半)
           ⟹ Πγ = 4^44 × 88/2^87 = 2^88·88/2^87 = 2·88 = 176 = 4N_d
  B. ★ 簡化分解: V_Λ = Σγ² + N_d/B + rem ?
     因為 Σκ + 19 = −8 + 19 = 11 = N_d/B = 44/4
     ⟹ V_Λ = 272 + 11 + 0.082129 = 283.082129（更簡潔全 K_Chain）
  C. ★ Boltzmann 形式: ρ_Λ = e^{−V_Λ} = (Π_n e^{−γ_n²})·e^{−11}·e^{−rem}
     ——「為何指數？」結構答案: K_Chain 模態統計獨立 ⟹ 配分函數 = Π z_n
       （乘積 ⟹ 指數 = 求和; free energy = −ln Z = Σγ²+修正）
  D. 88-site 對偶: Σγ(88 全譜) = 176 = 4N_d = Πγ(44) ?  Σγ_odd = 88 = 2N_d ?
  E. rem 來源核正: O62 最佳 1/12.17593 (0.00002%); γ_29/36 (0.062%)
"""
import sys
from mpmath import mp, mpf, pi, sin, log, exp

mp.dps = 50
Gc = 1.0

def chk(name, cond, detail=""):
    global Gc
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name} {detail}")
    if not cond:
        sys.exit(1)
    Gc += 1

V_LAM = mpf("283.082129")
F_GAM = mpf("264.082129")
ND, B, F8 = 44, 4, 21

# ---------- 44-site 譜 ----------
g44 = [4*sin(mp.pi*n/88)**2 for n in range(1, ND+1)]
S1 = sum(g44); S2 = sum(g**2 for g in g44)
P44 = 1
for g in g44: P44 *= g

# ---------- A. 譜 determinant ----------
print("== A. 譜 determinant: Πγ_n(44) = 4N_d = 176 ==")
print(f"  Πγ(44) = {float(P44):.10f}")
print(f"  閉式推導: 4^44·(88^{1/2}/2^{87/2})²·1 = 2^88·88/2^87 = 2·88 = 176")
chk("A1 Πγ(44) = 176 = 4N_d EXACT", abs(P44 - 176) < mpf("1e-30"))
chk("A2 Πγ(44) = 2·88 = 2·(2N_d) 閉式", abs(P44 - 2*88) < mpf("1e-30"))
print(f"  ln(Πγ) = {float(log(P44)):.6f} = ln(4N_d)  [譜 determinant log]")

# ---------- B. 簡化分解 ----------
print("\n== B. 簡化分解: V_Λ = Σγ² + N_d/B + rem ==")
quot = ND//B
chk("B0 N_d/B = 44/4 = 11 整數", quot == 11)
lhsB = S2 + quot + (F_GAM - 264)
print(f"  Σγ² + N_d/B + rem = {float(S2):.4f} + {quot} + {float(F_GAM-264):.6f} = {float(lhsB):.10f}")
chk("B1 V_Λ = Σγ² + N_d/B + rem EXACT", abs(lhsB - V_LAM) < mpf("1e-30"))
print(f"  驗證 Σκ+19 = −8+19 = 11 = N_d/B ✓")

# ---------- C. Boltzmann 形式 ----------
print("\n== C. 「為何指數」結構答案: 模態獨立 ⟹ 乘積 ⟹ 指數 ==")
# ρ_Λ = Π e^{−γ_n²}·e^{−11}·e^{−rem}
prod_boltz = 1
for g in g44:
    prod_boltz *= exp(-g*g)
rhsC = prod_boltz * exp(-quot) * exp(-(F_GAM-264))
print(f"  Πe^−γ_n²        = {float(prod_boltz):.6e}  (e^−Σγ² = e^−272)")
print(f"  Πe^−γ_n²·e^−11·e^−rem = {float(rhsC):.6e}")
print(f"  ρ_Λ             = {float(exp(-V_LAM)):.6e}")
chk("C1 乘積 Boltzmann 形式 EXACT", abs(rhsC - exp(-V_LAM)) < mpf("1e-40"))
print("  讀法: 真空能密度 = Π_n e^{−γ_n²} × e^{−(N_d/B+rem)}")
print("  ⟹ 指數形式係「44 個独立模態之配分函數乘積」之自然結果")
print("  (free energy F = Σγ² + N_d/B + rem;  ρ = e^{−F})")

# ---------- D. 88-site 對偶 ----------
print("\n== D. 88-site 對偶鏈 ==")
g88 = [4*sin(mp.pi*n/88)**2 for n in range(1, 89)]
S88 = sum(g88)
S88_odd = sum(g for i, g in enumerate(g88, 1) if i % 2 == 1)
S88_even = sum(g for i, g in enumerate(g88, 1) if i % 2 == 0)
print(f"  Σγ(88 全) = {float(S88):.6f}  (vs 176 = 4N_d; vs Πγ(44) = 176)")
print(f"  Σγ_odd  = {float(S88_odd):.6f}  (vs 88 = 2N_d)")
print(f"  Σγ_even = {float(S88_even):.6f}")
chk("D1 Σγ(88) = 176 = 4N_d = Πγ(44) EXACT", abs(S88 - 176) < mpf("1e-25"))
chk("D2 Σγ_odd(88) = 88 = 2N_d EXACT", abs(S88_odd - 88) < mpf("1e-25"))
chk("D3 Σγ_even(88) = 88 = 2N_d EXACT", abs(S88_even - 88) < mpf("1e-25"))
# 88-site 譜積
P88 = 1
for g in g88: P88 *= g
print(f"  Πγ(88) = {float(P88):.3e}  (全譜積, 含 γ_44=4, γ_88=0?)")

# ---------- E. rem 來源 ----------
print("\n== E. rem = F(γ)−264 = 0.082129 閉式核正 (O62 已做) ==")
rem = F_GAM - 264
print(f"  rem = {float(rem):.12f}")
print(f"  O62 最佳: 1/12.17593 (0.00002%)  次: γ_29/36 (0.062%)")
print(f"  譜來源候選: rem vs (π/88)²·? : (π/88)² = {float((pi/88)**2):.8f}")
print(f"  rem·(88/π)² = {float(rem*(88/pi)**2):.6f}  (≈2.51? 唔結構)")
print("  rem 保持 O62 🔴 冇簡單閉合 — 唔重推")

print(f"\n===== 全部 {int(Gc-1)} PASS =====")
sys.exit(0)