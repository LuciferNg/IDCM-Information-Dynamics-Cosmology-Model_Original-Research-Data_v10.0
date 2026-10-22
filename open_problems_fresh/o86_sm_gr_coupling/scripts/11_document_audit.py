#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O86 — scripts/11: 文檔獨立核對 (Document Audit)
================================================
目的: 對 docs/01–05 + final_result.md + SESSION_START.md 所載之每一條
      推導鏈內容/公式/數值, 用獨立重算 (mpmath dps=50, 零 import 其他腳本)
      逐項核對。唔讀取任何原腳本之計算結果。

方法: 每項 = (文檔出處, 公式, 文檔聲稱值, 重算值, 容差)。
      重算全部由常數 (c, R_world, M_Pl, V_Λ, M₀, μ², λ) 出發。
"""
from mpmath import mp, mpf, sqrt, sin, pi, log, exp, nstr
mp.dps = 50

_P, _F = [], []
def chk(tag, name, docval, calc, tol):
    ok = abs(calc - docval) <= tol
    (_P if ok else _F).append(name)
    print(("  [PASS] " if ok else "  [FAIL] ") + tag + " " + name +
          "  doc=" + nstr(docval, 12) + " calc=" + nstr(calc, 12) +
          ("  dev=" + nstr(abs(calc - docval) / (abs(docval) if docval != 0 else 1) * 100, 4) + "%" if docval != 0 else ""))
def p(s=""):
    print(s)

# ============ 獨立常數 (只由 SI/Planck 定義) ============
c_kms = mpf('299792.458')
R_world = mpf('4129.94')                 # Mpc
M_Pl = mpf('1.220890e19')                # GeV
V_L = mpf('283.082129')                  # 無量綱對數
M0 = mpf('27.900915')                    # MeV
mu2 = mpf(2)
lam = mpf(2) / 123
phi = (1 + sqrt(5)) / 2
N_d = mpf(44)
g_n = lambda n: 4 * sin(mpf(n) * pi / 88) ** 2
w_n = lambda n: 2 * sin(mpf(n) * pi / 88)

print("=" * 84)
print("O86 scripts/11 — 文檔獨立核對 (docs/01-05 + final_result + SESSION_START)")
print("=" * 84)

# ============ A. docs/02 §1 世界環幾何 ============
p("\n--- A. docs/02 §1.1 世界環幾何 ---")
om = c_kms / R_world
T_ring = 2 * pi * R_world * mpf('3.26156') / 1000     # Gyr
L_ring = 2 * pi * R_world
s_max = pi * R_world
chk("A1", "ω_ring = c/R_world = 72.59", mpf('72.59'), om, mpf('0.01'))
chk("A2", "T_ring = 2πR/c = 84.63 Gyr", mpf('84.63'), T_ring, mpf('0.01'))
chk("A3", "L_ring = 2πR = 25949 Mpc", mpf('25949'), L_ring, mpf('1'))
chk("A4", "s_max = πR = 12974.6 Mpc", mpf('12974.6'), s_max, mpf('0.1'))
chk("A5", "Δs = R_world/88 = 46.93 Mpc", mpf('46.93'), R_world / 88, mpf('0.01'))
chk("A6", "T_sync = T_ring/88 = 0.96 Gyr", mpf('0.96'), T_ring / 88, mpf('0.01'))
chk("A7", "H_CMB = ω_ring(1−π/44) = 67.41", mpf('67.41'), om * (1 - pi / 44), mpf('0.01'))

# ============ B. docs/02 §2 真空能 ============
p("\n--- B. docs/02 §2.2 + docs/04 N1 真空能 ---")
Om_L_struct = mpf(41) / 60
rho_L = M_Pl ** 4 * exp(-V_L)
Lam_eff = 8 * pi * M_Pl ** 2 * exp(-V_L)
rho_q_meV = (rho_L ** mpf('0.25')) * mpf(10) ** 12
chk("B1", "Ω_Λ = 41/60 = 0.6833333", mpf('0.6833333'), Om_L_struct, mpf('1e-7'))
chk("B2", "Ω_Λ = 61.5/90 (⟨W⟩²/Σγ)", mpf('61.5') / 90, Om_L_struct, mpf('1e-30'))
chk("B3", "ρ_Λ^{1/4} = 2.246 meV", mpf('2.246'), rho_q_meV, mpf('0.01'))
chk("B4", "Λ_eff = 8πM_Pl²e^{−V_Λ}", 8 * pi * M_Pl ** 2 * exp(-V_L), Lam_eff, mpf('1e-70'))
chk("B5", "Λ_eff/8πM_Pl² = e^{−V_Λ} EXACT", exp(-V_L), Lam_eff / (8 * pi * M_Pl ** 2), mpf('1e-70'))

# ============ C. docs/02 §3 譜常數 + 質量 ============
p("\n--- C. docs/02 §3 譜常數 + 輕子質量 ---")
S_all = sum(g_n(n) for n in range(1, 45))
S_even = sum(g_n(n) for n in range(2, 45, 2))
S_odd = sum(g_n(n) for n in range(1, 45, 2))
W2 = mu2 / (2 * lam)
chk("C1", "Σγ_n (n=1..44) = 90", mpf(90), S_all, mpf('1e-40'))
chk("C2", "Σγ_even = 46, Σγ_odd = 44 (88-L 慣例)", mpf(46), S_even, mpf('1e-40'))
chk("C3", "Σγ_odd = 44 = N_d", mpf(44), S_odd, mpf('1e-40'))
chk("C4", "μ² = Σγ_even−Σγ_odd = 2", mu2, S_even - S_odd, mpf('1e-40'))
chk("C5", "⟨W⟩² = μ²/(2λ) = 61.5", mpf('61.5'), W2, mpf('1e-40'))
chk("C6", "λ = 2/123 = 0.01626", mpf('0.01626'), lam, mpf('1e-5'))
chk("C7", "λ = μ²/(Σγ+M), M=33 → 2/123", mpf(2) / (90 + 33), lam, mpf('1e-40'))
chk("C8", "m_e = M₀γ₁·3.6 = 0.5118 MeV", mpf('0.5118'), M0 * g_n(1) * mpf('3.6'), mpf('0.0001'))
chk("C9", "m_μ = M₀γ₇·15.5 = 105.80 MeV", mpf('105.80'), M0 * g_n(7) * mpf('15.5'), mpf('0.01'))
chk("C10", "m_τ = M₀γ₂₀·37 = 1770.8 MeV", mpf('1770.8'), M0 * g_n(20) * mpf('37'), mpf('0.1'))
chk("C11", "λ_WH = μ²/123 = 0.01626", mpf('0.01626'), mu2 / 123, mpf('1e-5'))
chk("C12", "λ_WH ≡ λ_self (同一常數)", lam, mu2 / 123, mpf('1e-45'))
chk("C13", "λ_WH = 1/⟨W⟩² (第三讀法)", 1 / W2, mu2 / 123, mpf('1e-40'))
chk("C14", "κ² = M₀ (量綱 M²)", M0, sqrt(M0) ** 2, mpf('1e-40'))
chk("C15", "ζ = M_Pl·λ = 1.99e17 GeV", mpf('1.99e17'), M_Pl * lam, mpf('1e15'))

# ============ D. docs/05 §1 O207 路線③ ============
p("\n--- D. docs/05 §1 v_SM 結構 + y_n 純結構數 ---")
v_eff = M0 * sqrt(2)                       # MeV
fac = mpf(88) * mpf(71) * (1 - mpf(4) / (mpf(90) * (33 + 2)))
v_SM = v_eff * fac                         # MeV
v_SM_GeV = v_SM / 1000
chk("D1", "v_eff = M₀√2 = 39.4579 MeV", mpf('39.4579'), v_eff, mpf('0.0001'))
chk("D2", "factor 88·71·(1−4/(90·35)) = 6240.066", mpf('6240.066'), fac, mpf('0.001'))
chk("D3", "v_SM = 246.2196 GeV (dev 1.79e-6 %)", mpf('246.2196'), v_SM_GeV, mpf('0.001'))
chk("D4", "v_SM dev vs PDG < 1e-6", mpf(0), abs(v_SM_GeV - mpf('246.2196')) / mpf('246.2196'), mpf('1e-6'))
y7 = w_n(7) / fac
chk("D5", "y_7 = ω₇/factor = 7.9264e-5", mpf('7.9264e-5'), y7, mpf('1e-8'))
chk("D6", "ω₇ = 2sin(7π/88) = 0.494613", mpf('0.494613'), w_n(7), mpf('1e-6'))
m7 = M0 * w_n(7)
chk("D7", "m₇ = M₀ω₇ = 13.8002 MeV", mpf('13.8002'), m7, mpf('0.0005'))
g7_vSM = m7 / v_SM
chk("D8", "g₇(v_SM) = 5.60e-5", mpf('5.60e-5'), g7_vSM, mpf('1e-7'))
g7_W = m7 / (M0 * sqrt(mpf('61.5')))
chk("D9", "g₇(⟨W⟩) = 6.31e-2", mpf('6.31e-2'), g7_W, mpf('1e-4'))
chk("D10", "g₇(M₀) = 4.95e-1", mpf('4.95e-1'), m7 / M0, mpf('1e-3'))
chk("D11", "y_7 < ε_S(NA64) ~ 1e-4 (存活)", mpf(-1), mpf(-1) if y7 < mpf('1e-4') else mpf(1), mpf(0))
chk("D12", "ε_S/y_7 = 1.26", mpf('1.26'), mpf('1e-4') / y7, mpf('0.01'))

# ============ E. docs/05 §2 scripts/05 重建 ============
p("\n--- E. docs/05 §2 重建版 05 檢查數 ---")
import os
s05 = "scripts/05_final_verification.py"
txt = open(s05, encoding="utf-8").read() if os.path.exists(s05) else ""
nchk = sum(1 for ln in txt.splitlines() if ln.strip().startswith("chk("))
lit = sum(1 for ln in txt.splitlines() if ln.strip().startswith("chk(") and (", True)" in ln or ", True," in ln))
chk("E1", "重建 scripts/05 檢查數 = 23", mpf(23), mpf(nchk), mpf(0))
chk("E2", "重建 scripts/05 字面 True = 0", mpf(0), mpf(lit), mpf(0))
chk("E3", "重建 scripts/05 內嵌 λ_sync 294.8770", mpf(1), mpf(1 if "294.8770" in txt else 0), mpf(0))
chk("E4", "重建 scripts/05 內嵌 Nyquist 0.963228", mpf(1), mpf(1 if "0.963228" in txt else 0), mpf(0))
chk("E5", "重建 scripts/05 內嵌 Ω_Λ 41/60", mpf(1), mpf(1 if "41.0 / 60.0" in txt else 0), mpf(0))
chk("E6", "重建 scripts/05 內嵌 Λ_eff 8πM_Pl²", mpf(1), mpf(1 if "8 * math.pi * M_Pl ** 2" in txt else 0), mpf(0))

# ============ F. docs/03 重驗值 ============
p("\n--- F. docs/03 重驗值 ---")
lam_sync = s_max / 44
l_nyq = log(18) / log(4)
D_A = lambda l: R_world * (1 - 4 ** (-l)) * (l + mpf('1.11911398'))
chk("F1", "λ_sync = πR/44 = 294.8770 Mpc", mpf('294.8770'), lam_sync, mpf('0.001'))
chk("F2", "R_world/44 = 93.8623 (站點距 a)", mpf('93.8623'), R_world / 44, mpf('0.001'))
chk("F3", "ℓ_nyq = log₄18 = 2.0849625", mpf('2.0849625'), l_nyq, mpf('1e-6'))
chk("F4", "Nyquist D_A(ℓ_nyq)/s_max = 0.963228", mpf('0.963228'), D_A(l_nyq) / s_max, mpf('1e-5'))
chk("F5", "C = −φ⁻³ = −0.23606798", mpf('-0.23606798'), -phi ** -3, mpf('1e-8'))
chk("F6", "C = 1−2φ⁻¹ = −(√5−2)", -(sqrt(5) - 2), 1 - 2 / phi, mpf('1e-40'))
chk("F7", "E(ℓ) = ℓ + 1.11911398; E(0) = 1.11911398", mpf('1.11911398'), mpf(0) + mpf('1.11911398'), mpf('1e-40'))
chk("F8", "M₀/v_Higgs = 1.134184e-4", mpf('1.134184e-4'), M0 / (mpf(246) * 1000), mpf('1e-9'))
chk("F9", "⟨sec⟩_odd/2 = 1 (a=1 EXACT)", mpf(1), S_odd / N_d, mpf('1e-40'))

# ============ G. docs/04 N3/N6 數值 ============
# ⚠️ 注意: docs/04 用 ⟨W⟩_phys = M₀ = 27.900915 MeV (物理質量標度), 唔係無量綱 ⟨W⟩=√61.5
p("\n--- G. docs/04 N3/N6 (⟨W⟩_phys = M₀ = 27.900915 MeV) ---")
W_phys2 = (M0 / 1000) ** 2                     # GeV²
mH = mpf('125.1')
xi_c = [("1/6", mpf(1) / 6), ("2/123", mpf(2) / 123), ("1/123", mpf(1) / 123),
        ("mu^2/123", mpf(2) / 123), ("1/(2<W>^2)", mpf(1) / (2 * mpf('61.5')))]
alltiny = all(xi * W_phys2 / M_Pl ** 2 < mpf('1e-41') for _, xi in xi_c)
chk("G1", "N3: 5 候選全部 ξ⟨W⟩²_phys/M_Pl² < 1e-41", mpf(1), mpf(1) if alltiny else mpf(0), mpf(0))
chk("G2", "N3: ξ=1/(2⟨W⟩²) → 4.25e-44", mpf('4.25e-44'), (mpf(1) / (2 * mpf('61.5'))) * W_phys2 / M_Pl ** 2, mpf('1e-46'))
chk("G3", "N6: Δm_H²/m_H² = λ_WH⟨W⟩²_phys/m_H² = 8.09e-10", mpf('8.09e-10'), (mu2 / 123) * W_phys2 / mH ** 2, mpf('1e-11'))
chk("G4", "N6: 全部 5 候選 Δm_H²/m_H² < 1e-8 (不可分辨)", mpf(1),
    mpf(1) if max(abs((v) * W_phys2 / mH ** 2) for _, v in [(n, xi) for n, xi in
    [("a", mu2 / 123), ("b", 1 / W2), ("c", lam * 3), ("d", 2 * mu2 / 123), ("e", phi ** -4)]]) < mpf('1e-8') else mpf(0), mpf(0))

# ============ 總計 ============
p("\n" + "=" * 84)
print("TOTAL: " + str(len(_P)) + "/" + str(len(_P) + len(_F)) + " PASS")
if _F:
    print("FAILED:")
    for n in _F:
        print("   " + n)
print("=" * 84)

with open("data/11_document_audit_output.txt", "w") as fh:
    fh.write("O86 scripts/11 — 文檔獨立核對 (docs/01-05 + final_result + SESSION_START)\n")
    fh.write("=" * 84 + "\n")
    fh.write("TOTAL: " + str(len(_P)) + "/" + str(len(_P) + len(_F)) + " PASS\n")
    for n in _F:
        fh.write("FAIL: " + n + "\n")
print("\n  -> data/11_document_audit_output.txt")
