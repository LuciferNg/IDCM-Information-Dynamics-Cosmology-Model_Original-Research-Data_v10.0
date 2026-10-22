#!/usr/bin/env python3
"""
O153 script 10 — 文檔獨立核對 (doc cross-check)
獨立重算 docs/00-08 宣稱嘅所有關鍵公式/數值, 唔依賴原 scripts 輸出。
目的: 驗證每個 doc 入面嘅推導鏈內容、公式、數值正確。
"""
import mpmath as mp
mp.mp.dps = 50

# === 基礎結構 (O95/O148/O140/O142 錨點) ===
N_d = 44
B = 4
mu2 = 2
N_gen = 3
# O142 約定: Lucas 數列 L₀=2, L₁=1, L₂=3, L₃=4, L₄=7, L₅=11, L₆=18, L₇=29, L₈=47, L₉=76, L₁₀=123
L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123]
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]  # Fibonacci F₁..F₁₂

def gamma(k, N=88):
    """176-Laplacian 頭 88 模: γ_k = 4sin²(kπ/176)"""
    return mp.mpf(4) * mp.sin(mp.pi * k / 176)**2

S_even = sum(gamma(k) for k in range(2, 89, 2))
S_odd  = sum(gamma(k) for k in range(1, 89, 2))
S_tot  = S_even + S_odd
s0 = sum(gamma(k) for k in range(4, 89, 4))
s1 = sum(gamma(k) for k in range(1, 89, 4))
s2 = sum(gamma(k) for k in range(2, 89, 4))
s3 = sum(gamma(k) for k in range(3, 89, 4))

results = []
def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
def eq(a, b, tol=mp.mpf(10)**-10):
    return mp.fabs(mp.mpf(a) - mp.mpf(b)) < tol
def pct(a, b):
    return mp.fabs(mp.mpf(a) - mp.mpf(b)) / mp.mpf(b)

# ============================================================
# A. docs/01_clt_alpha_audit.md 核對 (script 01, 16/16)
# ============================================================
eps_exact = mp.mpf(19)/123
check("A1 19/123 = 0.1544715", eq(eps_exact, "0.1544715447154471544715447154"), mp.nstr(eps_exact, 18))
check("A2 φ⁻¹/4 = 0.1545085 (corpus)", eq(mp.mpf(1)/mp.phi/4, "0.15450849718747371205114670852"), mp.nstr(mp.mpf(1)/mp.phi/4, 18))
check("A3 ε_v1 0.1545 vs 19/123 dev 0.018%", pct("0.1545", eps_exact) < mp.mpf("0.0002"), mp.nstr(pct("0.1545", eps_exact), 8))
alpha = mp.mpf(19)*mp.sqrt(44)/123
check("A4 α = 19√44/123 = 1.0246483", eq(alpha, "1.02464830921549"), mp.nstr(alpha, 16))
check("A5 α = ε√N_d", eq(alpha, eps_exact*mp.sqrt(N_d)))
check("A6 α T̂ 形式 = (F₈−μ²)√(L₃L₅)/L₁₀", eq(alpha, (F[8]-2)*mp.sqrt(L[3]*L[5])/L[10]), f"{(F[8]-2)*mp.sqrt(L[3]*L[5])/L[10]}")
check("A7 Q7 √(π²/6−1) = 0.8031 (算術錯誤確認)", eq(mp.sqrt(mp.pi**2/6 - 1), "0.80307787097406"), mp.nstr(mp.sqrt(mp.pi**2/6-1), 14))
check("A8 1/√44 = 0.150756 ≠ ε", eq(mp.mpf(1)/mp.sqrt(44), "0.15075567228888"), mp.nstr(mp.mpf(1)/mp.sqrt(44), 14))
# FSR ζ_N(1) = ((2N)²−1)/12: docs/01 話 645.25 對 88-site 對偶鏈 (n=1..87)
check("A9 ζ_N(1) = ((2N)²−1)/12, N=44 → 645.25", eq((mp.mpf(88)**2-1)/12, "645.25"), mp.nstr((mp.mpf(88)**2-1)/12, 10))
check("A9b 直接求和 Σ_{n=1}^{87} 1/γ_n = 645.25 (FSR 88-L 形式, script 01 C5c 原式)", eq(sum(mp.mpf(1)/(4*mp.sin(mp.pi*n/88)**2) for n in range(1, 88)), "645.25"), mp.nstr(sum(mp.mpf(1)/(4*mp.sin(mp.pi*n/88)**2) for n in range(1,88)), 8))
alpha2_ratio = pct(alpha**2, mp.mpf(21)/20)
check("A11 α² vs 21/20 dev 9.1e-5", alpha2_ratio < mp.mpf("0.0001"), mp.nstr(alpha2_ratio, 8))

# ============================================================
# B. docs/02_nh_42_identity.md 核對 (script 02+03, 12/12+12/12)
# ============================================================
check("B1 1/ε² = 15129/361 = 41.9086", eq(mp.mpf(1)/eps_exact**2, mp.mpf(15129)/361), mp.nstr(mp.mpf(1)/eps_exact**2, 10))
check("B2 41.9086 ≈ 42 (MCMC artifact)", eq(mp.mpf(15129)/361, "41.9085872576"), mp.nstr(mp.mpf(15129)/361, 12))
check("B3 α²/ε² = 44 精確", eq((alpha/eps_exact)**2, 44), mp.nstr((alpha/eps_exact)**2, 12))
check("B4 42 = μ²·N_gen·L₄ = 2·3·7", 2*3*7 == 42)
check("B5 42 = N_d−μ² = 44−2", 44-2 == 42)
check("B6 42 = Σγ_odd−s0 = 88−46", eq(S_odd - s0, 42))
check("B7 42 = N_d(B−1)−Σγ_even = 132−90", eq(44*3 - S_even, 42))
check("B8 log₄(42/44) = −0.0336", eq(mp.log(mp.mpf(42)/44, 4), "-0.033557098"), mp.nstr(mp.log(mp.mpf(42)/44, 4), 8))
# N_EW
M_Pl = mp.mpf("1.220890e19")
v_pdg = mp.mpf("246.2196")
N_EW = (M_Pl/v_pdg)**2
check("B9 N_EW = (M_Pl/v)² = 2.4587e33", eq(N_EW, "2.4587e33", mp.mpf("1e30")), mp.nstr(N_EW, 6))
check("B10 log₁₀ N_EW = 33.3907", eq(mp.log10(N_EW), "33.3907", mp.mpf("1e-4")), mp.nstr(mp.log10(N_EW), 8))
check("B11 v vs 2L₁₀=246 dev 0.089% (L₀=2 約定, L₁₀=123)", eq(2*L[10], 246) and pct(v_pdg, 2*L[10]) < mp.mpf("0.001"), mp.nstr(pct(v_pdg, 2*L[10]), 8))
check("B12 v/M₀ = 8800 候選 (M₀=27.9009MeV)", eq(v_pdg/mp.mpf("0.0279009"), "8824", mp.mpf("10")), mp.nstr(v_pdg/mp.mpf("0.0279009"), 6))
check("B13 log₁₀ N_EW = 33.3907 vs 33.4 (K_Tree+μ²/F₅)", pct(mp.log10(N_EW), mp.mpf("33.4")) < mp.mpf("0.001"), mp.nstr(pct(mp.log10(N_EW), mp.mpf("33.4")), 8))

# ============================================================
# C. docs/03_four_domain_fsr.md 核對 (script 04, 18/18)
# ============================================================
def log4(x):
    return mp.log(mp.mpf(x), 4)
check("C1 ℓ(Planck) = log₄(1/44) = −2.73", eq(log4(mp.mpf(1)/44), "-2.7297", mp.mpf("1e-3")), mp.nstr(log4(mp.mpf(1)/44), 6))
check("C2 ℓ(Cosmic) = 0", eq(log4(44/44), 0))
check("C3 ℓ(Galaxy) = log₄(10⁶/44) = 7.236", eq(log4(mp.mpf(10)**6/44), "7.236", mp.mpf("1e-3")), mp.nstr(log4(mp.mpf(10)**6/44), 6))
check("C4 ℓ(EW) = log₄(2.5e33/44) = 52.74", eq(log4(mp.mpf("2.5e33")/44), "52.74", mp.mpf("0.01")), mp.nstr(log4(mp.mpf("2.5e33")/44), 6))
check("C5 log₄44 = 2.7297", eq(log4(44), "2.7297", mp.mpf("1e-4")), mp.nstr(log4(44), 8))
check("C6 log₄10⁶ = 9.9658 (vs 10=L₅−1, dev 0.34%)", eq(log4(mp.mpf(10)**6), "9.9658", mp.mpf("1e-3")), mp.nstr(log4(mp.mpf(10)**6), 8))
check("C7 log₄2.5e33 = 55.47 (vs 55=F₁₀, dev 0.86%)", eq(log4(mp.mpf("2.5e33")), "55.472778", mp.mpf("1e-3")), mp.nstr(log4(mp.mpf("2.5e33")), 8))
# N_crit
alpha2 = alpha**2
Ncrit = (4*mp.pi/alpha)**2
check("C8 N_crit = (4π/α)² = 150.408", eq(Ncrit, "150.408", mp.mpf("0.01")), mp.nstr(Ncrit, 6))
check("C9 150 = μ²·N_gen·F₅² = 2×3×25", 2*3*25 == 150)
check("C10 150 = Σγ_even×F₅/N_gen = 90×5/3", eq(S_even*5/3, 150))
check("C11 N_cont = 90×167 = 15030 (167=176−9)", eq(S_even*(B*N_d - N_gen**2), 15030), mp.nstr(S_even*(B*N_d-9), 10))
check("C12 N_cont/N_crit = 99.93 ≈ 100", eq(mp.mpf(15030)/Ncrit, "99.93", mp.mpf("0.01")), mp.nstr(mp.mpf(15030)/Ncrit, 6))
check("C13 N_cont 候選 = 90×(176−9)", eq(S_even*(176-9), 15030))

# ============================================================
# D. docs/05_residual_observer_42.md 核對 (script 06, 18/18)
# ============================================================
check("D1 R_obs = C_obs−N_d−μ² = 88−44−2 = 42", eq(S_odd - N_d - mu2, 42))
check("D2 (s0, R_obs) = (46, 42)", eq(s0, 46) and eq(S_odd-s0, 42))
check("D3 s0+R_obs = 88, s0−R_obs = 4", eq(s0 + (S_odd-s0), 88) and eq(s0 - (S_odd-s0), 4))
check("D4 90−48 = 42 (B·dim G_SM = 4×12)", eq(S_even - B*12, 42))
check("D5 178−136 = 42 (F₆·F_proj = 8×17)", eq(S_tot - 8*17, 42))
check("D6 42/88 = 21/44 = F₈/N_d", eq(mp.mpf(42)/88, mp.mpf(21)/44))
check("D7 42.5 = F₅·F_proj/2 = 5×17/2", 5*17/2 == 42.5)

# ============================================================
# E. docs/06_92_third_rung.md 核對 (script 07, 15/15)
# ============================================================
check("E1 92 = Σγ_even+μ² = 90+2", eq(S_even + mu2, 92))
check("E2 92 = 2s0 = 92", eq(2*s0, 92))
check("E3 92 = C_obs+B = 88+4", eq(S_odd + B, 92))
check("E4 92 = L₉+B² = 76+16", L[9] + B**2 == 92)
check("E5 92 = L₁₀−L₇−μ² = 123−29−2", L[10]-L[7]-mu2 == 92)
check("E6 端點和 88+92 = 180 = 2Σγ_even = B(N_d+1)", eq(S_odd + 92, 2*S_even) and eq(S_odd+92, B*(N_d+1)))
check("E7 84+88+92 = 264 = N_d·2N_gen", 84+88+92 == 44*6)
check("E8 總和 88+90+92 = 270 = N_gen×Σγ_even", 88+90+92 == 3*90)

# ============================================================
# F. docs/07_plus_minus_2.md 核對 (script 08, 18/18)
# ============================================================
check("F1 γ₄₄(176-L) = 4sin²(π/4) = 2", eq(gamma(44), 2))
check("F2 2γ₄₄ = 4 = B", eq(2*gamma(44), 4))
check("F3 178 = 43×B+γ₄₄+γ₈₈ = 172+2+4", eq(43*B + gamma(44) + gamma(88), 178))
check("F4 家族階梯 n=1: (84,88,92)", 84+88+92 == 264 and (84+92) == 176 and 88 == 88)
check("F5 n=2: (168,176,184)", 168+176+184 == 528 and (168+184) == 352)
check("F6 n=3: (336,352,368)", 336+352+368 == 1056 and (336+368) == 704)
check("F7 n=4: (672,704,736)", 672+704+736 == 2112 and (672+736) == 1408)
check("F8 偶數 n 中心 = 44×4^(n/2)", 44 == 44*4**0 and 176 == 44*4**1 and 704 == 44*4**2)
check("F9 per-op: 88 ops × 2 = 176", 88*mu2 == B*N_d)

# ============================================================
# G. docs/08_capacity_vs_operator.md 核對 (script 09, 30/30)
# ============================================================
check("G1 90+88 = 178 ≠ 176", eq(S_even+S_odd, 178) and not eq(S_even+S_odd, 176))
check("G2 178 = 176+μ²", eq(S_tot, B*N_d + mu2))
check("G3 90+88−μ² = 176", eq(S_even+S_odd-mu2, B*N_d))
check("G4 勢差 = 90−88 = 2", eq(S_even-S_odd, 2))
check("G5 176 = 172+4 (43×B+γ₈₈)", eq(43*B + gamma(88), B*N_d))
def vg(n):
    return mp.cos(mp.pi*n/176)
def beat(a, b):
    return mp.mpf(4)*mp.sin(mp.fabs(a-b)*mp.pi/176)*vg((a+b)/2)
check("G6 beat(44,44) = 0", eq(beat(44,44), 0))
check("G7 beat(44,45) = 0.05003", eq(beat(44,45), "0.0500320461923", mp.mpf("1e-10")), mp.nstr(beat(44,45), 12))
check("G8 beat(42,44) = 0.10274 ≠ beat(44,46)=0.09914", eq(beat(42,44), "0.102738996796", mp.mpf("1e-10")) and eq(beat(44,46), "0.099135168610", mp.mpf("1e-10")), f"{mp.nstr(beat(42,44),12)} vs {mp.nstr(beat(44,46),12)}")
check("G9 4 = 2μ² = γ₈₈ = 46−42", 2*mu2 == B and eq(gamma(88), 4) and 46-42 == 4)

# ============================================================
# H. docs/04 verdict table 關鍵值抽查
# ============================================================
check("H1 D1: ε_exact = 19/123 = (f_proj/f_unproj)/N_gen = (19/41)/3", eq(eps_exact, mp.mpf(19)/41/3))
check("H2 D2: α = 19√44/123 (F₈−μ²=19, L₃L₅=44, L₁₀=123)", F[8]-2 == 19 and L[3]*L[5] == 44 and L[10] == 123)
check("H3 D4: 41.9086 = 1/ε² 係 α=1 artifact", eq(mp.mpf(1)/eps_exact**2, "41.9086", mp.mpf("1e-3")))
check("H4 D7b: N_cont = 90×167 EXACT", eq(S_even*167, 15030))
check("H5 D9: 譜分解 178 = 172+2+4", eq(178, 172+2+4))
check("H6 D10: 殘差 4 = B = 46−42", 46-42 == 4 and B == 4)

# ============================================================
print("="*72)
print("O153 script 10 — 文檔獨立核對 (docs/00-08 公式數值交叉驗證)")
print("="*72)
fails = 0
for name, ok, detail in results:
    mark = "✅ PASS" if ok else "❌ FAIL"
    if not ok: fails += 1
    print(f"  {mark}  {name}  [{detail}]")
print("-"*72)
print(f"TOTAL: {len(results)-fails}/{len(results)} PASS, {fails} FAIL")
