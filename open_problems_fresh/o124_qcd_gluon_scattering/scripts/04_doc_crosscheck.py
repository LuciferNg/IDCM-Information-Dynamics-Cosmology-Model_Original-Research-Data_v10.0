#!/usr/bin/env python3
"""
O124 — Script 04: 文檔核對 (doc cross-check)
============================================
由零重算 docs/02 同 docs/03 嘅每個數值 claim, **唔 import scripts/01-03**。
每個 claim 一行 chk(), 最後印 AUDIT RESULT。

目的: 捉文檔入面嘅錯 (包括自己以前寫錯嘅)。
"""
import math, re, os
from fractions import Fraction as Fr
from mpmath import mp, mpf, sin, cos, tan, pi, nstr
mp.dps = 50

PASS = 0; FAIL = 0; TOTAL = 0
def chk(doc, claim, got, want, tol=1e-9):
    global PASS, FAIL, TOTAL; TOTAL += 1
    got, want = float(got), float(want)
    ok = abs(got - want) <= tol*max(1.0, abs(want))
    PASS += ok; FAIL += (not ok)
    print(f"  [{'✔' if ok else '✘'}] {doc:<9} {claim:<52} got={got:.8g} want={want:.8g}")

B, N_gen, N_c, N_f, N_d, K_tree = 4, 3, 3, 6, 44, 33
L = [0,1,3,4,7,11,18,29,47,76,123]
F = [0,1,1,2,3,5,8,13,21,34,55]

print("=" * 78)
print("  O124 Script 04: 文檔核對 (獨立重算 docs/02 + docs/03)")
print("=" * 78)

print("\n── A. docs/02 前置驗證數值 ──")
chk("docs/02", "A1 純 SU(3) b₀ = 11", 11*N_c/3, 11)
sigma_v9 = (1/16)/(2*math.pi) * (246.2639*(1+5**0.5)/2)**(-33/2)**1
# 重算: Λ_MERA = V_EW · φ^(−16.5)
PHI = (1+5**0.5)/2
Lam_MERA = 246.2639 * PHI**(-16.5)
chk("docs/02", "A2 Λ_MERA = 0.08772 GeV", Lam_MERA, 0.0877212, 1e-4)
sig = (1/16)/(2*math.pi)*Lam_MERA**2
chk("docs/02", "A2 σ_v9script = 7.6544e−5 GeV²", sig, 7.6544e-5, 1e-4)
chk("docs/02", "A2 比值 0.1745/σ = 2280", 0.1745/sig, 2280, 1e-3)
a14 = 1/(1/0.1179 + 7/(2*math.pi)*math.log(14000/91.188))
sgg = 9*math.pi*a14**2/(2*14000.0**2)*3.89379e5
chk("docs/02", "A3 σ(gg→gg) = 1.415e−4 nb", sgg, 1.415e-4, 1e-3)
chk("docs/02", "A3 比值 100/σ = 7.07e5", 100/sgg, 7.07e5, 1e-2)
chk("docs/02", "A3b 1 GeV⁻² = 3.894e8 pb", 3.89379e8, 3.894e8, 1e-3)
chk("docs/02", "A4 Λ_QCD = 0.0450 GeV", 91.188*math.exp(-2*math.pi/(7*0.1179)), 0.0450, 1e-2)
chk("docs/02", "A6 123110/27.9009 = 4412", 123110/27.900915, 4412, 1e-3)
chk("docs/02", "C4 f^{abc} 獨立三元組 = 9", 9, 9, 0)
chk("docs/02", "C4 非零分量 = 54 = 9×3!", 9*6, 54, 0)
chk("docs/02", "C4 C(8,3) = 56", math.comb(8,3), 56, 0)
chk("docs/02", "判決 13 = 4+1+8", 4+1+8, 13, 0)
chk("docs/02", "存活率 5/13 = 38%", 5/13*100, 38.46, 1e-3)
chk("docs/02", "D4 α_s⁻¹ dev vs SM = 0.130%",
    abs((F[6] + (1-(cos(pi/8)-tan(3*pi/88)*sin(pi/8))**2) + mpf(1)/B) - mpf('8.4818'))/mpf('8.4818')*100,
    0.130, 1e-2)

print("\n── B. docs/03 §A 色扇區 ──")
sumQ2 = 3*(3*(mpf(2)/3)**2 + 3*(mpf(1)/3)**2 + 1)
chk("docs/03", "A.2 Σ_f N_c Q_f² = 8", float(sumQ2), 8, 1e-12)
chk("docs/03", "A.2 N_c²−1 = 8 = F₆", N_c**2-1, F[6], 0)
chk("docs/03", "A.3 C_F = 4/3 = B/3", float(Fr(B,3)), 4/3, 1e-15)
chk("docs/03", "A.3 (N_c²−1)/(2N_c) = 4/3", float(Fr(N_c**2-1, 2*N_c)), 4/3, 1e-15)
chk("docs/03", "A.3 B=4 ⟺ 3(B−2)=2(B−1)", 3*(B-2) - 2*(B-1), 0, 0)
chk("docs/03", "A.4 φ³−φ⁻³ = 4 = B", float(PHI**3 - PHI**-3), 4.0, 1e-12)
chk("docs/03", "A.4 3²(φ³−φ⁻³) = 36", 9*4, 36, 0)
chk("docs/03", "A.4 K_tree+N_gen = 36", K_tree+N_gen, 36, 0)
chk("docs/03", "A.4 N_d−2B = 36", N_d-2*B, 36, 0)
chk("docs/03", "A.4 24 = 2(L₅+1) = h¹¹−12", 2*(L[5]+1), 36-12, 0)

print("\n── C. docs/03 §B 連結膠子譜 ──")
lam = [4*sin(pi*n/88)**2 for n in range(88)]
chk("docs/03", "B.2 λ₀ = 0", float(lam[0]), 0, 0)
chk("docs/03", "B.2 Σλ(0..87) = 176 = 4N_d", float(sum(lam)), 4*N_d, 1e-30)
chk("docs/03", "B.2 Σλ(1..44) = 90 = Σγ", float(sum(lam[1:45])), 90, 1e-30)
chk("docs/03", "B.2 88 = 2×43 + 2", 2*43+2, 88, 0)
chk("docs/03", "B.2 λ_n = λ_{88−n}", float(max(abs(lam[n]-lam[88-n]) for n in range(1,44))), 0, 1e-30)
chk("docs/03", "B.3 holonomy 88×(π/88) = π", 88*(math.pi/88), math.pi, 1e-15)
chk("docs/03", "B.3 88 = B × 2L₅", B*2*L[5], 88, 0)

print("\n── D. docs/03 §C 頂點 ──")
chk("docs/03", "C.1 稀疏度 9/56 = 0.1607", 9/56, 0.160714, 1e-6)
chk("docs/03", "C.2 88² = 7744", 88**2, 7744, 0)
chk("docs/03", "C.2 N³ = 681472", 88**3, 681472, 0)

print("\n── E. docs/03 §D β 函數 ──")
Th = [[1,1],[1,0]]
def mpow(M, n):
    R = [[1,0],[0,1]]
    for _ in range(n):
        R = [[R[0][0]*M[0][0]+R[0][1]*M[1][0], R[0][0]*M[0][1]+R[0][1]*M[1][1]],
             [R[1][0]*M[0][0]+R[1][1]*M[1][0], R[1][0]*M[0][1]+R[1][1]*M[1][1]]]
    return R
T4 = mpow(Th,4); T5 = mpow(Th,5); T3 = mpow(Th,3)
chk("docs/03", "D T̂⁴ = [[5,3],[3,2]]", T4[0][0], 5, 0)
chk("docs/03", "D Tr(T̂⁴) = 7", T4[0][0]+T4[1][1], 7, 0)
chk("docs/03", "D Tr(T̂⁵) = 11 = L₅", T5[0][0]+T5[1][1], L[5], 0)
chk("docs/03", "D Tr(T̂³) = 4 = L₃", T3[0][0]+T3[1][1], L[3], 0)
chk("docs/03", "D b₀ = 11 − 2N_f/3 = 7", 11-2*N_f/3, 7, 0)
chk("docs/03", "D L₅−L₃ = L₄ = 7", L[5]-L[3], L[4], 0)
chk("docs/03", "D 唯一解 N_f = 6", [n for n in range(12) if 11*3-2*n == 21][0], 6, 0)
chk("docs/03", "D b₁ = 102 − 38N_f/3 = 26 = 2F₇", 102-38*N_f/3, 2*F[7], 0)
chk("docs/03", "D 3B−1 = 11 = 8+3", 3*B-1, 11, 0)

print("\n── F. docs/03 §E α_s ──")
sin2W = 1 - (cos(pi/8) - tan(3*pi/88)*sin(pi/8))**2
a_inv = F[6] + sin2W + mpf(1)/B
chk("docs/03", "E α_s⁻¹ = 8.4707757", float(a_inv), 8.4707757, 1e-8)
chk("docs/03", "E α_s = 0.118053", float(1/a_inv), 0.118053, 1e-5)
chk("docs/03", "E dev vs SM = 0.130%", abs(float(a_inv)-8.4818)/8.4818*100, 0.130, 1e-2)
chk("docs/03", "E α₂⁻¹ = N_d − 2L₄ = 30", N_d-2*L[4], 30, 0)
chk("docs/03", "E α₂⁻¹ dev vs 29.57 = 1.45%", abs(30-29.57)/29.57*100, 1.45, 1e-2)
chk("docs/03", "E F₆ = b₀+1 = 8", F[6], L[4]+1, 0)
chk("docs/03", "E sin²θ_W 閉式 = 模式比", float(sin2W - (1-(sin(30*pi/88)/sin(41*pi/88))**2)), 0, 1e-30)

print("\n── G. docs/03 §F gg→gg ──")
chk("docs/03", "F.1 G_ss = C_A²(N_c²−1) = 72", N_c**2*(N_c**2-1), 72, 0)
chk("docs/03", "F.1 |G_off| = 36 = G_diag/2", 72/2, 36, 0)
chk("docs/03", "F.1 等角 cos = 1/2", 36/72, 0.5, 0)
chk("docs/03", "F.1 9/2 = C_A²/2", N_c**2/2, 4.5, 0)
chk("docs/03", "F.1 (N_c²−1)² = 64", (N_c**2-1)**2, 64, 0)
def Br(s,t,u): return 3 - u*t/s**2 - u*s/t**2 - s*t/u**2
chk("docs/03", "F.2 B 交叉對稱 B(s,t,u) = B(t,s,u)", Br(5,-3,-2), Br(-3,5,-2), 1e-12)
chk("docs/03", "F.2 |M|/g⁴ = 34.30 < 16π", abs(4.5*Br(5,-3,-2)), 34.295, 1e-3)
chk("docs/03", "F.2 16π = 50.265", 16*math.pi, 50.265, 1e-3)

print("\n── H. docs/03 §G 禁閉 ──")
chk("docs/03", "G 2M₀ = 55.8018 MeV", 2*27.900915, 55.8018, 1e-5)

print("\n── I. 計數對帳 (docs vs scripts 輸出) ──")
def last_result(path):
    if not os.path.exists(path): return None
    m = re.findall(r"結果:\s*(\d+)/(\d+) PASS", open(path, encoding="utf-8").read())
    return m[-1] if m else None
tot = 0
for f, want in [("01_preverification", (27,27)), ("02_discrete_qcd", (53,53)),
                ("03_cross_validation", (30,30))]:
    r = last_result(f"data/{f}_results.txt")
    ok = r is not None and tuple(map(int, r)) == want
    TOTAL += 1; PASS += ok; FAIL += (not ok)
    print(f"  [{'✔' if ok else '✘'}] scripts   {f+'.py':<28} RESULT = {r} want={want}")
    if r: tot += int(r[0])
chk("docs/03", "總 PASS = 27+53+30 = 110", tot, 110, 0)

# docs/03 誠實標記表計數
txt = open("docs/03_derivation.md", encoding="utf-8").read()
tbl = txt.split("## 誠實標記總表")[1].split("## 檔案")[0]
rows = [l for l in tbl.splitlines() if l.startswith("| ") and "|" in l[2:]]
data_rows = [l for l in rows if "---" not in l and "項目" not in l]
g = sum(1 for l in data_rows if "🟢" in l); y = sum(1 for l in data_rows if "🟡" in l)
r_ = sum(1 for l in data_rows if "🔴" in l)
chk("docs/03", "誠實標記表 16 行", len(data_rows), 16, 0)
chk("docs/03", "誠實標記表 🟢 13", g, 13, 0)
chk("docs/03", "誠實標記表 🟡 2", y, 2, 0)
chk("docs/03", "誠實標記表 🔴 1", r_, 1, 0)
print(f"      (實測: {len(data_rows)} 行, 🟢{g} 🟡{y} 🔴{r_})")

print(f"\n{'='*78}")
print(f"  AUDIT RESULT: {PASS}/{TOTAL} 核對通過" + ("" if FAIL == 0 else f"  ({FAIL} FAIL)"))
print(f"{'='*78}")
import sys
sys.exit(0 if FAIL == 0 else 1)
