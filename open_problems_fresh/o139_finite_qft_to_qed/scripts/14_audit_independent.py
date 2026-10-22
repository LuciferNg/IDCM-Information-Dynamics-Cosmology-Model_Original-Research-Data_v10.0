#!/usr/bin/env python3
# O139 審計 — 獨立核對載重常數 (第三方方法: 純 mpmath + Fraction, 唔 import 任何 O139 script)
# 只驗證 docs 中嘅載重數字, 唔改任何檔案
import mpmath as mp
from fractions import Fraction
mp.mp.dps = 40

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  PASS " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail else ""))

print("═══ O139 docs 載重常數獨立核對 ═══")

# ── 1. α 端點結構身份 (docs/01 §2.4, docs/03, final_result)
B = 4          # 阻挫基
N_gen = 3
F_proj = 17    # O138/O143
F5, F6 = 5, 8
Tr_I44 = 44
c1 = mp.binomial(B**2, 2)   # C(16,2) = 120
print(f"  C(B²,2) = C(16,2) = {c1}")
check("α⁻¹(0) = C(B²,2)+F_proj = 137", c1 + F_proj == 137, f"{c1}+{F_proj}")
check("α⁻¹(0) 第二身份 3·Tr(I₄₄)+F₅ = 137", 3*Tr_I44 + F5 == 137, f"{3*Tr_I44}+{F5}")
check("α⁻¹(M_Z) = C(B²,2)+2B = 128", c1 + 2*B == 128, f"{c1}+{2*B}")
check("α⁻¹(M_Z) 第二身份 2·Tr(I₄₄)+F₅F₆ = 128", 2*Tr_I44 + F5*F6 == 128, f"{2*Tr_I44}+{F5*F6}")
check("Δα⁻¹ = F_proj−2B = 9 = N_gen²", F_proj - 2*B == 9 == N_gen**2)
check("(B−1)² = 9", (B-1)**2 == 9)
# B-scan 2..6 → 1/4/9/16/25
scan = [(F_proj_b := (b*b+1)) - 2*b for b in range(2, 7)]
check("B-scan (F_proj=B²+1): Δ=(B−1)² 2..6 → 1/4/9/16/25", scan == [1,4,9,16,25], f"{scan}")

# ── 2. Λ_mass = M₀·ω_max (docs/01 §三, docs/04)
M0 = mp.mpf('27.900915')   # MeV
check("Λ_mass = 2M₀ = 55.801830 MeV", abs(2*M0 - mp.mpf('55.801830')) < 1e-6, f"{2*M0}")

# ── 3. Λ_ℓ = ħπ·44·4^ℓ/R_world (docs/05, final_result) → 2.140399e−31 eV × 4^ℓ
# ħ = 6.582119569e-16 eV·s; R_world = 46.93 Mpc (格點距 a = R_world/88)
hbar = mp.mpf('6.582119569e-16')          # eV·s
Mpc_m = mp.mpf('3.0856775814913673e22')   # m
R_world_Mpc = mp.mpf('46.93') * 88        # 88 × 格點距
R_world = R_world_Mpc * Mpc_m             # m
c = mp.mpf('299792458')                   # m/s
Lam0 = hbar * mp.pi * 44 / (R_world / c)  # eV
print(f"  Λ_ℓ(ℓ=0) = {mp.nstr(Lam0, 8)} eV")
check("Λ_ℓ(0) ≈ 2.140399e−31 eV", abs(Lam0/mp.mpf('2.140399e-31') - 1) < 5e-3, f"{mp.nstr(Lam0,7)}")

# ── 4. running / δ / spread (docs/07, docs/08, final_result)
a0_phys = mp.mpf('137.035999177')
aZ_phys = mp.mpf('127.930')
running = a0_phys - aZ_phys
check("物理 running = 137.035999177 − 127.930 = 9.1060(8)", abs(running - mp.mpf('9.1060')) < 5e-4, f"{mp.nstr(running,8)}")
delta = running - 9
check("δ = +0.1060", abs(delta - mp.mpf('0.1060')) < 5e-4, f"{mp.nstr(delta,6)}")
spread = mp.mpf('1.1654')
check("δ/spread = 0.0910", abs(delta/spread - mp.mpf('0.0910')) < 1e-3, f"{mp.nstr(delta/spread,5)}")
# 1.1654 = 4.979 − 3.814
check("強子處理差異 = 4.979 − 3.814 = 1.165", abs((mp.mpf('4.979')-mp.mpf('3.814')) - spread) < 5e-4,
      f"{mp.mpf('4.979')-mp.mpf('3.814')}")
check("差異 = 11×δ", abs(spread/delta - 11) < 0.15, f"{mp.nstr(spread/delta,4)}")
# δ_exp: σ_exp = 0.008 → 13.25σ  (⚠️ 純實驗分母; 理論層分母係 spread=1.1654 ⇒ δ/spread=0.0910,
#    見 docs/08「13.2σ 係誤導」同 docs/07 R2 — 呢行只係覆核算術, 唔係背書該框架)
check("δ/σ_exp = 0.1060/0.008 = 13.25σ (算術覆核; 見 docs/08 限定)", abs(delta/mp.mpf('0.008') - mp.mpf('13.25')) < 0.05,
      f"{mp.nstr(delta/mp.mpf('0.008'),4)}")
# scheme: 128.933 − 127.930 = 1.003
check("MS-bar↔on-shell scheme 轉換 = 128.933−127.930 = 1.003", abs((mp.mpf('128.933')-mp.mpf('127.930')) - mp.mpf('1.003')) < 1e-9)
check("IDCM 128 vs MS-bar 127.930 dev = 0.055%", abs(abs(128-mp.mpf('127.930'))/mp.mpf('127.930')*100 - mp.mpf('0.0547')) < 5e-3,
      f"{float(abs(128-mp.mpf('127.930'))/mp.mpf('127.930')*100):.4f}%")
check("on-shell 128.933 dev = 0.72%", abs(abs(128-mp.mpf('128.933'))/mp.mpf('128.933')*100 - mp.mpf('0.7232')) < 5e-3,
      f"{float(abs(128-mp.mpf('128.933'))/mp.mpf('128.933')*100):.4f}%")

# ── 5. 受限強子 HVP 比率 (docs/09, docs/10, final_result)
free_q = mp.mpf('4.9726'); disp = mp.mpf('3.8137')
ratio = disp/free_q
check("受限/自由 = 3.8137/4.9726 = 0.766943", abs(ratio - mp.mpf('0.766943')) < 5e-6, f"{mp.nstr(ratio,7)}")
# docs/10 寫 0.23305（= 1 − 顯示值 0.76695，5 dp）；精確值 0.2330572
check("1 − ratio = 0.23305 (doc 5dp) / 0.2330572 exact", abs(1-ratio - mp.mpf('0.23305')) < 5e-5,
      f"{mp.nstr(1-ratio,7)}")
check("m_eff = 71.4591 > 鏈天花板 2M₀ = 55.8018 (28% 高)",
      mp.mpf('71.4591') > 2*M0 and abs(mp.mpf('71.4591')/(2*M0) - 1 - mp.mpf('0.2806')) < 1e-3,
      f"比 {mp.nstr(mp.mpf('71.4591')/(2*M0),4)}")

# ── 6. g-2 精度牆: 12 位 = 圈數 × log₁₀(π/α) (docs/05, final_result)
alpha = mp.mpf('0.0072973525693')
loops_per_digit = mp.log10(mp.pi/alpha)
check("log₁₀(π/α) = 2.634", abs(loops_per_digit - mp.mpf('2.634')) < 1e-3, f"{mp.nstr(loops_per_digit,5)}")
check("12 位 ↔ 圈數 = 12×2.634 = 31.6", abs(12*loops_per_digit - mp.mpf('31.6')) < 0.1, f"{mp.nstr(12*loops_per_digit,4)}")

# ── 7. 繞數機制 (docs/09): 2μ²·Δα⁻¹ = 36; F₁₁ = 89 = 53+36 (docs/09)
mu2 = 2
check("2μ²·Δα⁻¹ = 2×2×9 = 36", 2*mu2*9 == 36)
check("F₁₁ = 89 = 53 + 36", 53 + 36 == 89)
# F₁₁ Lucas: L: 2,1,3,4,7,11,18,29,47,76,123... F: 0,1,1,2,3,5,8,13,21,34,55,89
L = [2,1]; [L.append(L[-1]+L[-2]) for _ in range(12)]
F = [0,1]; [F.append(F[-1]+F[-2]) for _ in range(12)]
check("F₁₁ = 89 (Fibonacci 索引)", F[11] == 89, f"F={F}")
check("L₅ = 11, L₄ = 7", L[5] == 11 and L[4] == 7, f"L={L}")

# ── 8. 晶格離散化候選 (docs/09 §4): 兩個唔同嘅量, 唔可以混淆 ──
#   (a) WEIGHT  (1/M)Σx(1−x) = (M²−1)/(6M²) = (1/6)(1−1/M²)   @ M=44 → 0.1665806
#   (b) SHIFT   running 嘅移動 = 離散和 − 連續和            @ M=44 → −0.003313
M = 44
latt = (M**2 - 1)/(6*M**2)
check("(a) WEIGHT (M²−1)/(6M²) @ M=44 = 0.1665806", abs(latt - mp.mpf('1935')/mp.mpf('11616')) < 1e-15,
      f"{mp.nstr(latt,8)}")
check("(a) (1/6)(1−1/M²) 同式", abs((mp.mpf(1)/6)*(1-1/M**2) - latt) < 1e-15)
check("(a) 1/M² = 1/1936 = 5.165e−04", abs(mp.mpf(1)/M**2 - mp.mpf('5.1652892562e-4')) < 1e-12,
      f"{mp.nstr(mp.mpf(1)/M**2,7)}")
shift44 = mp.mpf('9.282959') - mp.mpf('9.286272')          # docs/09 §4 table
check("(b) SHIFT @ M=44 = −0.003313 (9.282959 − 9.286272)", abs(shift44 + mp.mpf('0.003313')) < 1e-6,
      f"{mp.nstr(shift44,7)}")
shift88 = mp.mpf('9.285504') - mp.mpf('9.286272')
check("(b) SHIFT @ M=88 = −0.000768 (9.285504 − 9.286272)", abs(shift88 + mp.mpf('0.000768')) < 1e-6,
      f"{mp.nstr(shift88,7)}")
check("(b) 32× 太細: |δ|/|shift44| = 0.1060/0.003313 ≈ 32",
      abs(mp.mpf('0.1060')/abs(shift44) - 32) < 1.0,
      f"{mp.nstr(mp.mpf('0.1060')/abs(shift44),4)}")
check("(b) 符號相反: shift < 0 < δ", shift44 < 0 < mp.mpf('0.1060'))

# ── 9. p_min/m_e = 9.52e−39 (docs/05)
p_min = hbar*mp.pi/ (R_world/c)   # eV
m_e = mp.mpf('0.51099895e6')      # eV
check("p_min/m_e = 9.52e−39", abs(p_min/m_e/mp.mpf('9.52e-39') - 1) < 0.02, f"{mp.nstr(p_min/m_e,4)}")

# ── 10. 譜禁區 Λ = 1.393178 MeV, m₁ = 1.991698 MeV (docs/06)
check("Λ_dressing = 1.393178 MeV = 2.7264 m_e", abs(mp.mpf('1.393178')/mp.mpf('0.51099895') - mp.mpf('2.7264')) < 1e-3,
      f"{mp.nstr(mp.mpf('1.393178')/mp.mpf('0.51099895'),5)}")
check("m₁ 過衝 = 1.991698/1.393178 = 1.4297 (3.11× 淨?)", mp.mpf('1.991698') > mp.mpf('1.393178'),
      f"m₁/Λ = {mp.nstr(mp.mpf('1.991698')/mp.mpf('1.393178'),5)}")

# ── 11. 2.343e+06 × 電子精度 (docs/06)
check("relative IR gap 2.626987e−4 = 2.343e6 × a_e 精度",
      abs(mp.mpf('2.626987e-4')/mp.mpf('1.121e-10')/1e6 - mp.mpf('2.343')) < 0.05,
      f"{mp.nstr(mp.mpf('2.626987e-4')/mp.mpf('1.121e-10')/1e6,5)}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL:
    print("FAIL:", FAIL)
    exit(1)
