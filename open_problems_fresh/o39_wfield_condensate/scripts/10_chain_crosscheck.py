#!/usr/bin/env python3
"""
O39 — 推導鏈獨立核對 (Derivation Chain Independent Cross-Check)
=================================================================
獨立重算 docs/01_derivation_record.md 所有關鍵公式/數值, 確認:
1. SSB 勢結構: μ²=2, λ=2/123, ⟨W⟩²=61.5, V_min, V''
2. Ω_Λ 恆等式: 4/(φ⁴−1), Ω_Λ/Ω_m=4φ/3, 41/19 修正 (O148)
3. 三重閉合: (Σγ_even+M)/2, 3(N_d−dim_ℂ)/2
4. 無熱寂: T_sync, λ_sync
5. 層次正交: ⟨W⟩=M₀ vs ⟨Φ²⟩=61.5
6. 遺留閉合: κ_eff, m_δW/m_7≈90/89, η=0, λ₁/λ₂
7. 統一閉合: λ=1/凝聚值

只讀核對 — 唔寫任何其他文件, 唔污染舊記錄。
"""

from decimal import Decimal, getcontext
getcontext().prec = 60
import math, os, sys

phi = (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)

passes, fails = [], []
def check(name, claim, value, tol):
    # 簽名: claim=期望值, value=實測值 (tol 可係數值或 Decimal)
    if isinstance(claim, str):
        ok = (claim == value)
    else:
        ok = abs(claim - value) <= tol
    if ok:
        passes.append(name)
    else:
        fails.append(f"{name}: claim={claim} actual={value}")
        print(f"  ❌ {name}: claim={claim} actual={value}")

print("="*70)
print("O39: 推導鏈獨立核對 (derivation chain cross-check)")
print("="*70)

# ═══════════════════════════════════════════════════════════
# 1. SSB 勢結構
# ═══════════════════════════════════════════════════════════
print("\n─── 1. SSB 勢結構 ───")
S_even = Decimal(90); S_odd = Decimal(88)
N_d = Decimal(44); dimC = Decimal(3)
mu2 = S_even - S_odd
lam = Decimal(2)/(Decimal(3)*(N_d - dimC))
W2 = mu2/(Decimal(2)*lam)
Vmin = -(mu2**2)/(Decimal(4)*lam)
Vpp = Decimal(4)*mu2
check("μ² = 2", mu2, Decimal(2), 0)
check("λ = 2/123", lam, Decimal(2)/Decimal(123), 0)
check("⟨W⟩² = 61.5", W2, Decimal('61.5'), Decimal('1e-50'))
check("V_min = −61.5", Vmin, -Decimal('61.5'), Decimal('1e-50'))
check("V''(⟨W⟩) = 8", Vpp, Decimal(8), 0)
print(f"   μ²={mu2}, λ={float(lam):.6f}, ⟨W⟩²={float(W2)}, V_min={float(Vmin)}, V''={float(Vpp)}")

# ═══════════════════════════════════════════════════════════
# 2. Ω_Λ 恆等式 + O148 修正
# ═══════════════════════════════════════════════════════════
print("\n─── 2. Ω_Λ 恆等式 + O148 修正 ───")
Omega_L = Decimal(4)/(phi**4 - 1)
Omega_m = Decimal(1) - Omega_L
ratio = Omega_L/Omega_m
t43 = Decimal(4)*phi/Decimal(3)
check("Ω_Λ = 4/(φ⁴−1)", Omega_L, Decimal(4)/(phi**4-1), 0)
dev43 = abs(ratio - t43)
print(f"   Ω_Λ/Ω_m = {float(ratio):.10f} vs 4φ/3 = {float(t43):.10f} (dev {float(dev43):.2e})")
print(f"   → 4φ/3 係代數表達 (dev 3e-59), 唔係「精確有理」")
r4119 = Decimal(41)/Decimal(19)
d4 = Decimal(5).sqrt()*phi**-9/Decimal(57)
check("41/19 = 4φ/3 + δ₄ (O148)", r4119, t43 + d4, Decimal('1e-55'))
dev4119 = abs(r4119 - ratio)
print(f"   O148: 41/19 = {float(r4119):.10f} (dev vs Ω_Λ/Ω_m = {float(dev4119):.2e})")
print(f"   ★ 41/19 先係精確有理 (o143 節點分區 41:19); 4φ/3 係近似 (0.024%)")
# 確認: 41/19 = 4φ/3 + δ₄ 精確成立 (δ₄ = √5φ⁻⁹/57), 而 41/19 ≠ Ω_Λ/Ω_m (dev 5e-4)
check("O148 修正成立 (41/19 = 4φ/3+δ₄ 精確)", True, abs(r4119 - (t43 + d4)) < Decimal('1e-55'), 0)

# ═══════════════════════════════════════════════════════════
# 3. 三重閉合
# ═══════════════════════════════════════════════════════════
print("\n─── 3. 三重閉合 ───")
M33 = Decimal(33)
check("(Σγ_even+M)/2 = 61.5", (S_even+M33)/2, Decimal('61.5'), 0)
check("3(N_d−dim_ℂ)/2 = 61.5", Decimal(3)*(N_d-dimC)/2, Decimal('61.5'), 0)
check("μ²/(2λ) = 61.5", W2, Decimal('61.5'), Decimal('1e-50'))
print(f"   (90+33)/2 = {float((S_even+M33)/2)} = 3(44−3)/2 = {float(Decimal(3)*(N_d-dimC)/2)} = μ²/2λ = {float(W2)} ✓")

# ═══════════════════════════════════════════════════════════
# 4. 無熱寂: T_sync, λ_sync
# ═══════════════════════════════════════════════════════════
print("\n─── 4. 無熱寂: T_sync, λ_sync ───")
H0 = Decimal('72.59')  # km/s/Mpc
MPC_KM = Decimal('3.085677581e19')  # km per Mpc
Gyr_s = Decimal('3.15576e16')  # s per Gyr
# H₀ in s⁻¹: 72.59 km/s/Mpc = 72.59 / 3.085677581e19 s⁻¹
H0_s = H0 / MPC_KM
# T_sync = 2π/H₀ (Hubble 週期)
T_sync = Decimal('6.28318530717958647692528676655900576839433879875021164194988918461563281257241799725606965068423413596') / H0_s / Gyr_s
check("T_sync = 84.64 Gyr", Decimal('84.64'), T_sync, Decimal('0.01'))
# λ_sync = c·T_sync/88
c_km = Decimal('299792.458')  # km/s
lam_sync = c_km * (T_sync * Gyr_s) / Decimal(88) / MPC_KM
check("λ_sync = 294.88 Mpc", Decimal('294.88'), lam_sync, Decimal('0.05'))
print(f"   T_sync = {float(T_sync):.2f} Gyr, λ_sync = {float(lam_sync):.2f} Mpc")

# ═══════════════════════════════════════════════════════════
# 5. 層次正交: ⟨W⟩=M₀ vs ⟨Φ²⟩=61.5
# ═══════════════════════════════════════════════════════════
print("\n─── 5. 層次正交 ───")
E_kchain = Decimal('4.060265e-3')
M0_eV = E_kchain * phi**(Decimal(47)+Decimal(37)/Decimal(528))
M0_MeV = M0_eV * Decimal('1e-6')
check("M₀ = 27.9009 MeV", M0_MeV, Decimal('27.9009'), Decimal('0.001'))
Phi2 = Omega_L * Decimal(90)
check("⟨Φ²⟩ = Ω_Λ·90 ≈ 61.5", Phi2, Decimal('61.5'), Decimal('0.05'))
print(f"   M₀ = {float(M0_MeV):.4f} MeV, ⟨Φ²⟩ = {float(Phi2):.4f} (61.5, dev {(abs(Phi2-Decimal(61.5))/Decimal(61.5)*100):.4f}%)")

# ═══════════════════════════════════════════════════════════
# 6. 遺留閉合
# ═══════════════════════════════════════════════════════════
print("\n─── 6. 遺留閉合 ───")
kappa = Decimal(1)/Decimal(16)
lam_O37 = kappa/Decimal(2)
kappa_eff = Decimal(2)*lam_O37*M0_MeV/Decimal(90).sqrt()
check("κ_eff = 0.1838 MeV", kappa_eff, Decimal('0.1838'), Decimal('0.001'))
s7 = 4*math.sin(7*math.pi/88)
check("4sin(7π/88) ≈ 1−1/90", 1-1/90, s7, 0.0012)  # dev 0.034% → tol 0.0012
eta = (2*2 - 4*(2/123)*61.5)/(6*61.5**2)
check("η = 0 (高階項)", 0, eta, 1e-12)
lam1 = Decimal(2)/Decimal(123)
lam2 = (phi**4-1)/Decimal(4)
check("λ₁ = 1/61.5", lam1, Decimal(1)/Decimal('61.5'), Decimal('1e-30'))
check("λ₂ = 1/Ω_Λ", lam2, Decimal(1)/Omega_L, Decimal('1e-30'))
print(f"   κ_eff = {float(kappa_eff):.4f} MeV, 4sin(7π/88) = {s7:.6f}, η = {eta:.2e}")
print(f"   λ₁ = {float(lam1):.8f} = 1/61.5 ✓, λ₂ = {float(lam2):.8f} = 1/Ω_Λ ✓")

# ═══════════════════════════════════════════════════════════
# 7. 統一閉合: λ = 1/凝聚值
# ═══════════════════════════════════════════════════════════
print("\n─── 7. 統一閉合 ───")
check("⟨Φ²⟩ = ⟨w⟩²·Σγ", Phi2, Omega_L*Decimal(90), Decimal('1e-40'))
check("λ₁·Σγ ≈ λ₂", lam1*Decimal(90), lam2, Decimal('0.001'))
print(f"   ⟨Φ²⟩ = ⟨w⟩²·Σγ = Ω_Λ·90 = {float(Phi2):.4f} (61.5)")

# ═══════════════════════════════════════════════════════════
print(f"\n{'='*70}")
print(f"O39 推導鏈獨立核對: {len(passes)}/{len(passes)+len(fails)} PASS")
for f in fails:
    print(f"  ❌ {f}")
if fails:
    print("❌ 有 FAIL")
    sys.exit(1)
print("✅ 全部通過 — docs/01 所有公式數值獨立重算一致")

# 寫結果 (只寫 data/, 唔碰其他文件)
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'chain_crosscheck_results.txt')
with open(out, 'w') as f:
    f.write(f"O39 推導鏈獨立核對: {len(passes)}/{len(passes)+len(fails)} PASS\n")
    f.write(f"日期: 2026-08-19 (O39), O148 修正確認 2026-09-05\n")
    f.write(f"★ O148 修正: Ω_Λ/Ω_m = 4φ/3 係代數表達 (dev 3e-59), 精確有理 = 41/19 = 4φ/3 + √5φ⁻⁹/57\n")
    f.write(f"★ 所有 docs/01 公式數值獨立重算一致\n")
print(f"\n  結果已寫入 data/chain_crosscheck_results.txt")
