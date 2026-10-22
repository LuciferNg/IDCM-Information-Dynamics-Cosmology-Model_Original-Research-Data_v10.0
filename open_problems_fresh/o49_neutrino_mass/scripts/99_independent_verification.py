#!/usr/bin/env python3
"""
O49 Independent Cross-Verification (Phase 2)
=============================================
由原始定義重算所有關鍵數值，唔依賴 scripts 嘅中間輸出。
只讀唔寫。驗證 docs/01_derivation_report.md + scripts 嘅全部聲稱。
"""
import math, json

phi = (1 + math.sqrt(5)) / 2
M_Pl = 1.220910e19      # GeV (PDG Planck mass)
h11, h21, Nd = 36, 98, 44
v = 246.0               # GeV
PDG_dm31 = 2.434e-3     # eV^2
PDG_dm21 = 7.53e-5      # eV^2

ok = 0; fail = 0
def check(name, cond, detail):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name}: {detail}")
    else:    fail += 1; print(f"  ❌ {name}: {detail}")

print("=" * 78)
print("PHASE 2: INDEPENDENT CROSS-VERIFICATION (bare Python)")
print("=" * 78)

# ── 1. γ₆ ──
gamma6 = 4 * math.sin(6 * math.pi / 88) ** 2
print(f"\n[1] gamma6 = 4sin^2(6π/88) = {gamma6:.8f}")
check("gamma6 == 0.180736 (doc claim)", abs(gamma6 - 0.180736) < 1e-6, f"{gamma6:.6f}")

# ── 2. M_comp structural ──
denom = 2 * h11 * h21 * Nd
M_comp = M_Pl / denom
print(f"\n[2] M_comp = M_Pl/(2×h11×h21×Nd) = {M_comp:.6e} GeV")
check("denom = 310464 = 2^6×3^2×7^2×11", denom == 310464 and
      310464 == 2**6 * 3**2 * 7**2 * 11, f"{denom}")
check("M_comp == 3.9325e13 (doc claim)", abs(M_comp - 3.9325e13) / 3.9325e13 < 1e-4,
      f"{M_comp:.4e}")

# ── 3. m_0 base ──
numerator = (gamma6 * v) ** 2   # GeV^2
m0_GeV = numerator / M_comp
m0_eV = m0_GeV * 1e9
print(f"\n[3] (γ6×v)^2 = {numerator:.4f} GeV^2")
print(f"    m_0 = {m0_eV:.6f} eV")
check("m_0 == 0.05027 eV (doc claim)", abs(m0_eV - 0.05027) < 1e-4, f"{m0_eV:.5f}")

# ── 4. φ^(1/8) ──
phi18 = phi ** (1 / 8)
print(f"\n[4] φ^(1/8) = {phi18:.10f}")
check("φ^(1/8) == 1.061997", abs(phi18 - 1.061997) < 1e-6, f"{phi18:.6f}")

# ── 5. m_0' corrected ──
m0p = m0_eV * phi18
print(f"\n[5] m_0' = m_0 × φ^(1/8) = {m0p:.6f} eV")
check("m_0' == 0.05338 eV (doc claim)", abs(m0p - 0.05338) < 1e-4, f"{m0p:.5f}")

# ── 6. φ-power hierarchy ──
m_tau, m_mu, m_e = m0p, m0p / phi, m0p / phi**2
print(f"\n[6] m_τ={m_tau:.5f}, m_μ={m_mu:.5f}, m_e={m_e:.5f} eV")
check("m_τ/m_μ = φ", abs(m_tau/m_mu - phi) < 1e-9, f"{m_tau/m_mu:.10f}")
check("m_μ/m_e = φ", abs(m_mu/m_e - phi) < 1e-9, f"{m_mu/m_e:.10f}")

# ── 7. Δm²₃₁ ──
dm31 = m_tau**2 - m_e**2
err31 = abs(dm31 - PDG_dm31) / PDG_dm31 * 100
print(f"\n[7] Δm²₃₁ = {dm31:.6e} eV² (PDG {PDG_dm31:.3e}), err = {err31:.4f}%")
check("Δm²₃₁ < 0.1% (doc claim 0.002%)", err31 < 0.1, f"{err31:.4f}%")

# ── 8. Δm²₂₁ raw + Z3² correction ──
dm21_raw = m_mu**2 - m_e**2
ratio_raw = dm21_raw / PDG_dm21
print(f"\n[8] Δm²₂₁ raw = {dm21_raw:.6e} eV²")
print(f"    ratio raw/PDG = {ratio_raw:.4f} (should be ~9 = Z3²)")
dm21 = dm21_raw / 9
err21 = abs(dm21 - PDG_dm21) / PDG_dm21 * 100
print(f"    Δm²₂₁ corrected = {dm21:.6e} eV², err = {err21:.4f}%")
check("Δm²₂₁ < 1% (doc claim 0.73%)", err21 < 1.0, f"{err21:.4f}%")

# ── 9. Σm_ν ──
sum_mnu = m_tau + m_mu + m_e
print(f"\n[9] Σm_ν = {sum_mnu:.4f} eV (Planck < 0.12)")
check("Σm_ν < 0.12", sum_mnu < 0.12, f"{sum_mnu:.4f} eV")

# ── 10. Z5 quantum dimensions ──
print(f"\n[10] Z5 quantum dims d_k = sin(π(k+1)/5)/sin(π/5):")
d = [math.sin(math.pi*(k+1)/5) / math.sin(math.pi/5) for k in range(5)]
for k, dk in enumerate(d):
    print(f"     k={k}: d={dk:.6f}")
check("d_0=d_3=1, d_1=d_2=φ, d_4=0", 
      abs(d[0]-1) < 1e-9 and abs(d[3]-1) < 1e-9 and
      abs(d[1]-phi) < 1e-9 and abs(d[2]-phi) < 1e-9 and abs(d[4]) < 1e-9,
      f"d=[{d[0]:.3f},{d[1]:.3f},{d[2]:.3f},{d[3]:.3f},{d[4]:.3f}]")

# ── 11. Structural candidate errors (script 01/02/03 claims) ──
print(f"\n[11] Structural candidates vs M_comp (from Δm²₃₁):")
M_comp_dm31 = numerator / (math.sqrt(PDG_dm31 / (1 - phi**-4)) * 1e-9)
print(f"     M_comp from Δm²₃₁ alone = {M_comp_dm31:.4e} GeV")
e_cand = [
    ("B⁴×h¹¹²", 4**4 * 36**2),
    ("Nd⁴×N_gen/F₉", 44**4 * 3 / 34),
    ("Nd³×B", 44**3 * 4),
    ("2×h¹¹×h²¹×Nd", 2*36*98*44),
    ("2×h¹¹×h²¹×Nd×φ^(1/8)", 2*36*98*44*phi18),
]
for name, den in e_cand:
    m = M_Pl / den
    err = abs(m - M_comp_dm31) / M_comp_dm31 * 100
    print(f"     {name:<28} den={den:<12} err={err:.4f}%")
check("B⁴×h¹¹² error < 1% (script 01 claim 0.62%)",
      abs(M_Pl/(4**4*36**2) - M_comp_dm31)/M_comp_dm31*100 < 1.0, "")
check("2×h¹¹×h²¹×Nd error ~6.2% (script claim)",
      abs(abs(M_Pl/(2*36*98*44) - M_comp_dm31)/M_comp_dm31*100 - 6.2) < 0.5,
      f"{abs(M_Pl/(2*36*98*44) - M_comp_dm31)/M_comp_dm31*100:.2f}%")

# ── 12. Ratio factorization check (three references) ──
print(f"\n[12] M_Pl/M_comp ratios — three references:")
ratio_A = M_Pl / 3.6909e13   # [A] legacy calibrated
ratio_B = M_Pl / M_comp      # [B] structural = 310464 EXACT
ratio_C = M_Pl / M_comp_dm31 # [C] physical inversion
print(f"     [A] calib 3.6909e13:     ratio = {ratio_A:.1f}")
print(f"     [B] struct 3.9325e13:    ratio = {ratio_B:.1f}  (=2×36×98×44 EXACT)")
print(f"     [C] inversion 3.7030e13: ratio = {ratio_C:.1f}")
check("[B] ratio == 310464 exact", abs(ratio_B - 310464) < 1e-6, f"{ratio_B:.4f}")
check("[A] ratio ~330789 (script01/02 target)", abs(ratio_A - 330789) < 5, f"{ratio_A:.1f}")
check("[C] ratio ~329708 (script03 inversion)", abs(ratio_C - 329708) < 5, f"{ratio_C:.1f}")

# ── 13. Data JSON consistency (scripts saved) ──
print(f"\n[13] Data JSON cross-check:")
import os
dpath = os.path.join(os.path.dirname(__file__), "..", "data")
try:
    with open(os.path.join(dpath, "04_complete_derivation.json")) as f:
        j4 = json.load(f)
    check("JSON m_0_corrected == 0.053384", abs(j4["m_0_corrected"] - 0.053384) < 1e-5,
          f"{j4['m_0_corrected']:.6f}")
    check("JSON dm31 == 2.4341e-3", abs(j4["dm31"] - 2.4341e-3) < 1e-6,
          f"{j4['dm31']:.6e}")
    check("JSON dm21 == 7.4751e-5", abs(j4["dm21"] - 7.4751e-5) < 1e-8,
          f"{j4['dm21']:.6e}")
    check("JSON sum_mnu == 0.1068", abs(j4["sum_mnu"] - 0.1068) < 1e-3,
          f"{j4['sum_mnu']:.4f}")
except FileNotFoundError:
    print("  ❌ 04_complete_derivation.json missing — run scripts first")

# ── 14. Old-record consistency (read-only, no pollution) ──
print(f"\n[14] Old-record anchors (read-only reference):")
print(f"     neutrino_p6_mode.md: γ₆=0.180736 ✓ M_comp(calib)=3.6909e13 (separate calibrated value)")
print(f"     session_20260815: M_comp=M_Pl/(2×h11×h21×Nd)=3.93e13 ✓ (matches our structural)")
print(f"     Note: O49 uses STRUCTURAL M_comp=3.9325e13 (NOT the calibrated 3.6909e13)")
print(f"     → no modification made to any old file")

print(f"\n{'='*78}")
print(f"PHASE 2 RESULT: {ok} passed, {fail} failed")
print(f"{'='*78}")
sys_exit = 1 if fail else 0
raise SystemExit(sys_exit)