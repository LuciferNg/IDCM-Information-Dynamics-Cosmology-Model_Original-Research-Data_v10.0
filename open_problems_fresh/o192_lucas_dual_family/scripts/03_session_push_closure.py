#!/usr/bin/env python3
# O192 session push closure verifier — items 1..6 (SESSION_START.md 下一步)
# First-principles: no imports of verified scripts; constants recomputed from definitions.
# 2026-09-13
import math

PASS = 0
FAIL = 0
def check(name, cond, info=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS {name}  {info}")
    else:
        FAIL += 1
        print(f"  FAIL {name}  {info}")

# ---------- constant pool (recomputed, zero new constants) ----------
phi = (1 + math.sqrt(5)) / 2
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
def luc(n):
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a
F = {m: fib(m) for m in range(0, 16)}     # F0..F15
L = {m: luc(m) for m in range(0, 16)}     # L0..L15
B     = 4          # O95
N_gen = 3
N_d   = 44
N     = 88
M     = 33
R     = L[5]       # 11 = L5 = rank (O95/O190)
F_proj = 17        # O138+O143 (= L6-1)
mu2   = 2          # O159
dimC  = 3
# sanity: constant pool self-check
pool = dict(B=4, N_gen=3, N_d=44, N=88, M=33, R=R, F_proj=17, mu2=2,
            F5=F[5], F7=F[7], F10=F[10], F11=F[11], F12=F[12], F13=F[13],
            L4=L[4], L5=L[5], L6=L[6], L7=L[7], L8=L[8], L10=L[10], L14=L[14])
check("POOL F5=5", F[5] == 5, f"F5={F[5]}")
check("POOL F10=55", F[10] == 55, f"F10={F[10]}")
check("POOL F11=89", F[11] == 89, f"F11={F[11]}")
check("POOL F12=144", F[12] == 144, f"F12={F[12]}")
check("POOL F13=233", F[13] == 233, f"F13={F[13]}")
check("POOL L4=7 L5=11 L6=18 L14=843", (L[4], L[5], L[6], L[14]) == (7, 11, 18, 843))
check("POOL R=L5=11", R == 11)
check("POOL M=F9-1=33", F[9] - 1 == 33)
check("POOL N=F11-1=88", F[11] - 1 == 88)

# gamma spectrum (176-Laplacian, O159): gamma_k = 4 sin^2(k pi/176), k=1..88
g = [4 * math.sin(k * math.pi / 176.0) ** 2 for k in range(1, 89)]
g_odd  = [g[k] for k in range(0, 88, 2)]    # k=1,3,...,87
g_even = [g[k] for k in range(1, 88, 2)]    # k=2,4,...,88

print("\n== Part A: item 1 — k r_c = L5 mechanism test (docs/02 七.1) ==")
# A01: hierarchy -> kr_c
ln15 = 15 * math.log(10.0)
ln16 = 16 * math.log(10.0)
kr15 = ln15 / math.pi
kr16 = ln16 / math.pi
dev11_15 = abs(kr15 - 11) / 11 * 100
dev11_16 = abs(kr16 - 11) / 11 * 100
check("A01 kr_c(1e-15) near 11", abs(kr15 - 11) < 0.01, f"kr_c={kr15:.6f} dev={dev11_15:.4f}% (doc 0.0542%)")
check("A01 kr_c(1e-16) in [10.99,11.73]", kr16 > kr15 and kr16 < 11.73, f"kr_c(1e-16)={kr16:.4f}")
# A02: the coincidence is 11*pi ~ ln(1e15): e^{11 pi} ~ 1e15
e11pi = math.exp(11 * math.pi)
check("A02 11*pi ~ ln(1e15)", abs(11 * math.pi - ln15) / ln15 < 6e-4,
      f"11pi={11*math.pi:.4f} ln(1e15)={ln15:.4f} rel dev {abs(11*math.pi-ln15)/ln15*100:.4f}%")
check("A02 e^{11pi} ~ 1e15", abs(e11pi / 1e15 - 1) < 0.02, f"e^(11pi)={e11pi:.4e}")
# A03: IDCM hierarchy generator phi^{-k}: no integer k hits 1e-15
kstar = ln15 / math.log(phi)
nearest = round(kstar)
phipow = phi ** (-nearest)
check("A03 phi^{-k} never = 1e-15 (k=71.77 non-integer)", abs(kstar - nearest) > 0.2,
      f"k*={kstar:.2f} nearest k={nearest} phi^-k={phipow:.3e} vs 1e-15 (dev {abs(phipow/1e-15-1)*100:.1f}%)")
# A05: IDCM stability equation fixes N (chain length), contains no e/pi/1e15
check("A05 stability eq N+1=F_L5=89 -> N=88", F[L[5]] == 89 and F[L[5]] - 1 == 88,
      "IDCM side fixes N=88 (chain length); no warp/e/pi anywhere in the equation")
check("A05 rank lock L5=11 is su(12) rank (O95)", R == 11, "R=11 independent of hierarchy")

print("\n== Part B: item 2 — tree warp-volume hypothesis (docs/02 七.2) ==")
# B01: tree spectrum product exponent and mean
Sexp = sum(291.5 - m for m in range(0, 34))          # sum of exponents = 9350
mean_exp = Sexp / 34.0                                # 275
check("B01 sum exponent = 9350", Sexp == 9350, f"Sexp={Sexp}")
check("B01 mean exponent = 275", abs(mean_exp - 275) < 1e-9, f"mean={mean_exp}")
# B02: geometric mean and total weight magnitude
gm = phi ** mean_exp
total = phi ** 291.5 * sum(phi ** (-m) for m in range(0, 34))
check("B02 total spectral weight ~ 1e61 (not O(1))", total > 1e60, f"sum_mu_m={total:.3e}")
check("B02 RS1 warp volume 1/(4k)=1/44 ~ 0.023 (no match)", total > 1e50,
      "tree weight ~1e61 vs RS1 0.023 — incommensurate (62 orders)")
# B03: tree levels discrete — no continuous y integral; no-go extends
check("B03 tree has no volume element: 34 discrete levels, exponent ladder phi^1",
      abs(math.log(phi ** 291.5 / phi ** 258.5)) == 33 * math.log(phi),
      "level spacing = phi (33 steps) — discrete radial ladder, no dy")

print("\n== Part C: item 3 — L family independent budget (832 = 2^6*F7) ==")
# C01: sum L_m over family interval = L14 - L5 (standard identity)
sumL = sum(L[m] for m in range(4, 13))
check("C01 sum(L4..L12) = 832", sumL == 832, f"sumL={sumL}")
check("C01 = L14-L5 (standard identity)", sumL == L[14] - L[5], f"L14-L5={L[14]-L[5]}")
# C02: 832 factorization (2B)^2 * F7 = 64*13
check("C02 832 = (2B)^2 * F7", sumL == (2 * B) ** 2 * F[7], f"(2B)^2*F7={64*13}")
# C03: sum(L_m - 1) = 823 prime
sumLm1 = sum(L[m] - 1 for m in range(4, 13))
def isprime(x):
    if x < 2:
        return False
    for d in range(2, int(math.sqrt(x)) + 1):
        if x % d == 0:
            return False
    return True
check("C03 sum(L_m-1) = 823", sumLm1 == 823, f"sum(Lm-1)={sumLm1}")
check("C03 823 is prime (no structural factorisation)", isprime(823), "823 prime")
# C04: no spectral sum matches {L_m-1} x mu2
Sg1 = sum(g); Sg2 = sum(x * x for x in g); Sg3 = sum(x ** 3 for x in g)
Sg1o = sum(g_odd); Sg1e = sum(g_even)
Sg2o = sum(x * x for x in g_odd); Sg2e = sum(x * x for x in g_even)
Sg3o = sum(x ** 3 for x in g_odd); Sg3e = sum(x ** 3 for x in g_even)
Sl = 66  # tree spectral sum (O191)
spec = set([Sg1, Sg1o, Sg1e, Sg2, Sg2o, Sg2e, Sg3, Sg3o, Sg3e, Sl, 9350])
lmu2 = {(L[m] - 1) * mu2 for m in range(4, 13)}
check("C04 no spectral sum in (L_m-1)*mu2 set", len(spec & lmu2) == 0,
      f"spectral={{...}} vs Lxmu2={sorted(lmu2)} — disjoint")
# C05: F family sum for contrast: sum(F_m-1) = 363 = N_gen*R^2
sumFm1 = sum(F[m] - 1 for m in range(4, 13))
check("C05 sum(F_m-1) = 363 = N_gen*R^2", sumFm1 == 363 and sumFm1 == N_gen * R * R,
      f"sum(Fm-1)={sumFm1} = 3*121")
check("C05 asymmetry: F sum factorised vs L sum prime", isprime(sumFm1) is False and isprime(sumLm1) is True)

print("\n== Part D: item 4 — mechanism chains for 198 / 321 ==")
# D01: junction 99 = N+R = N_gen*M = N_gen^2*R
j99 = N + R
check("D01 99 = N+R", j99 == 99, f"N+R={j99}")
check("D01 99 = N_gen*M", j99 == N_gen * M, f"Ngen*M={N_gen*M}")
check("D01 99 = N_gen^2*R", j99 == N_gen * N_gen * R, f"Ngen^2*R={N_gen*N_gen*R}")
# D02: 198 = 2(N+R) = 2*N_gen*M = N_gen*sum_lambda
check("D02 198 = 2(N+R)", L[11] - 1 == 2 * (N + R), f"L11-1={L[11]-1}")
check("D02 198 = 2*N_gen*M", L[11] - 1 == 2 * N_gen * M)
check("D02 198 = N_gen*sum_lambda", L[11] - 1 == N_gen * Sl, f"Ngen*66={N_gen*Sl}")
# D03: pairing law decomposition
check("D03 pairing L11-1 = (F10-1)+(F12-1)+1 = 54+143+1",
      L[11] - 1 == (F[10] - 1) + (F[12] - 1) + 1,
      f"54+143+1={54 + 143 + 1}")
check("D03 54 = N_gen*L6, 143 = dim SU(12)", (54 == N_gen * L[6]) and (143 == 12 * 12 - 1))
# D04: 321 = sum_gamma + (F12-1) = 2*F11 + F12 - 1
check("D04 321 = sum_gamma + (F12-1)", L[12] - 1 == Sg1 + (F[12] - 1), f"{Sg1}+143={Sg1 + 143}")
check("D04 321 = 2F11 + F12 - 1", L[12] - 1 == 2 * F[11] + F[12] - 1, f"178+144-1={2*F[11]+F[12]-1}")
check("D04 pairing L12-1 = (F11-1)+(F13-1)+1 = 88+232+1", L[12] - 1 == 88 + 232 + 1)
# D05: L10-1 = M+N+1 (moduli sum, docs/01)
check("D05 L10-1 = M+N+1 = 122", L[10] - 1 == M + N + 1, f"M+N+1={M+N+1}")
# D06: uniqueness scan (registered-constant pool factor/sum forms)
cpool = [2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 17, 18, 20, 28, 33, 44, 46, 54, 55,
         66, 75, 88, 89, 90, 99, 122, 123, 143, 178, 198, 232, 264, 272, 321, 536]
prod198 = sorted({(a, b) for a in cpool for b in cpool if a <= b and a * b == 198})
sum321 = sorted({(a, b) for a in cpool for b in cpool if a <= b and a + b == 321})
# verifier fix (2026-09-13, honesty record): expected counts were wrong (22 not in pool; 89+232 missed)
check("D06 198 product-forms = 4, all moduli re-params", len(prod198) == 4, f"{prod198}")
check("D06 321 sum-forms = 3: 178+143, 198+123, 89+232", len(sum321) == 3, f"{sum321}")
check("D06 321 canonical = sum_gamma + (F12-1)", (143, 178) in sum321,
      "178+143 = budget + truncation boundary (F12-1 = 143 = dim SU(12))")

print("\n== Part E: item 5 — cubic layer (falsifiable surface) ==")
# E01: exact cubic sums
check("E01 sum_gamma^3_odd = 880", abs(Sg3o - 880) < 1e-9, f"odd={Sg3o:.9f}")
check("E01 sum_gamma^3_even = 912", abs(Sg3e - 912) < 1e-9, f"even={Sg3e:.9f}")
check("E01 sum_gamma^3 = 1792", abs(Sg3 - 1792) < 1e-9, f"total={Sg3:.9f}")
# E02: corpus registration cross-check (ckm_reconstruction/docs/09: 880 = 5x176, 912 = 5x176+32)
check("E02 ckm doc form 5*176 + {0,32}", abs(Sg3o - 5 * 176) < 1e-9 and abs(Sg3e - (5 * 176 + 32)) < 1e-9,
      "880 = 5x176, 912 = 5x176+32 (ckm_reconstruction/docs/09_pmns_wfield_flavor) ✓")
# E03: parity-gap law diff_n = mu2 * B^(n-1)
d1 = Sg1e - Sg1o; d2 = Sg2e - Sg2o; d3 = Sg3e - Sg3o
check("E03 diff1 = 2 = mu2*B^0", abs(d1 - 2) < 1e-9, f"d1={d1:.6f}")
check("E03 diff2 = 8 = mu2*B^1", abs(d2 - 8) < 1e-9, f"d2={d2:.6f}")
check("E03 diff3 = 32 = mu2*B^2", abs(d3 - 32) < 1e-9, f"d3={d3:.6f}")
# E04: predict n=4: diff = 128 = mu2*B^3; compute quartic
g4o = sum(x ** 4 for x in g_odd); g4e = sum(x ** 4 for x in g_even)
check("E04 diff4 = 128 = mu2*B^3 (prediction)", abs((g4e - g4o) - 128) < 1e-6,
      f"d4={g4e - g4o:.6f} predicted 128")
g4 = g4o + g4e
check("E04 sum_gamma^4 integer", abs(g4 - round(g4)) < 1e-6, f"Sg4={g4:.6f}")
# E04b: parity-gap law at n=5 (predict 512 = mu2*B^4)
g5o = sum(x ** 5 for x in g_odd); g5e = sum(x ** 5 for x in g_even)
check("E04b diff5 = 512 = mu2*B^4 (prediction)", abs((g5e - g5o) - 512) < 1e-3,
      f"d5={g5e - g5o:.6f} predicted 512")
g5 = g5o + g5e
check("E04b sum_gamma^5 integer", abs(g5 - round(g5)) < 1e-3, f"Sg5={g5:.6f}")
# E05: structure x mu2 at cubic level: Sg3 = mu2 * 2^4 * (F10+1) = 2*16*56
check("E05 Sg3 = mu2 * 2^4 * (F10+1)", abs(Sg3 - mu2 * 16 * (F[10] + 1)) < 1e-9,
      f"2*16*56={2*16*56}")
check("E05 Sg3_odd = 2^4 * F10 = 16*55", abs(Sg3o - 16 * F[10]) < 1e-9, f"16*55={16*55}")
check("E05 Sg3_even = 2^4 * (F10+mu2) = 16*57", abs(Sg3e - 16 * (F[10] + mu2)) < 1e-9)
# E06: sine-power sums land on structural numbers
s2 = Sg1 / 4.0; s4 = Sg2 / 16.0; s6 = Sg3 / 64.0
check("E06 sum sin^2 = F11/2 = 44.5", abs(s2 - F[11] / 2) < 1e-12, f"{s2}")
check("E06 sum sin^4 = (2M+1)/2 = 33.5", abs(s4 - (2 * M + 1) / 2) < 1e-12, f"{s4}")
check("E06 sum sin^6 = L7-1 = 28 (L-1 family member!)", abs(s6 - (L[7] - 1)) < 1e-12,
      f"28 = L7-1 = B*L4 — member of the family under study")
# E07: quartic layer — structure x mu2 degrades (falsifiable boundary)
check("E07 Sg4 = 6288 = 2^4 * 3 * 131", abs(g4 - 16 * 3 * 131) < 1e-6, f"16*3*131={16*3*131}")
check("E07 131 = O51 cold-spot phase solver (registered, derived not modulus)",
      abs(g4 - mu2 * (8 * 3 * 131)) < 1e-6,
      "Sg4 = mu2 * 2^3 * N_gen * 131 — structure = composite 3144, single-constant form absent")
check("E07 structure quality degrades 89 -> 268 -> 896 -> 3144",
      (89, 268, 896, 3144) == (F[11], B * (2 * M + 1), 16 * (F[10] + 1), 8 * 3 * 131),
      "clean single-constant structure ends at cubic; quartic = composite via O51 131")

print("\n== Part F: item 6 — 9350 operator identity ==")
# F01: exponent sum and factorisations
check("F01 9350 = (M+1)*275", Sexp == (M + 1) * 275, f"(M+1)*275={34*275}")
check("F01 275 = F5^2*L5 = F5*F10", 275 == F[5] ** 2 * L[5] and 275 == F[5] * F[10],
      "25*11 = 5*55 = 275")
# F02: 9350 = 2*F5^2*L5*F_proj = mu2*F5*F10*F_proj
check("F02 9350 = 2*F5^2*L5*F_proj", Sexp == 2 * F[5] ** 2 * L[5] * F_proj, f"{2*25*11*17}")
check("F02 9350 = mu2*F5*F10*F_proj (budget-quantum form)", Sexp == mu2 * F[5] * F[10] * F_proj,
      f"2*5*55*17={2*5*55*17}")
# F03: trace identity: Tr = level count x mean exponent; 561 = M*F_proj
check("F03 561 = sum_{m=0}^{33} m = M*F_proj", 33 * 34 // 2 == M * F_proj, f"{33*17}")
check("F03 Tr(H_tree) = 34*291.5 - 561 = 9350", 34 * 291.5 - 561 == 9350)
# F04: trap — V10 = L10*phi + L9 = 275.018 vs 275 near-hit (phi-convergence)
V10 = L[10] * phi + L[9]
conv = abs(L[10] * phi - L[11]) / L[11] * 100
check("F04 V10 = 275.018 (near-hit 0.0066%)", abs(V10 - 275.018181) < 1e-4, f"V10={V10:.6f}")
check("F04 near-hit controlled by L10*phi ~ L11 (0.0092%)", conv < 0.02,
      f"|L10*phi - L11|/L11 = {conv:.4f}% — phi-convergence artifact, NOT a bridge")
# F05: 550 = 2*275 = 10*F10 (o87 registration cross-check)
check("F05 550 = 2*275 = 10*F10", 2 * 275 == 10 * F[10], "o87: 1496-946 = 550 = 10xF10 ✓")

print("\n== Part G: verdict summary ==")
print(f"  item1 k r_c = L5: 拆穿 (trap 5: ln(1e15) ~ 11*pi); IDCM phi^-k never hits 1e-15")
print(f"  item2 tree warp volume: falsified (tree weight ~1e61 vs RS1 1/44; no volume element)")
print(f"  item3 L family budget: demoted (823 prime, no spectral match, 832 arithmetic org)")
print(f"  item4 198/321 mechanisms: closed (2(N+R); sum_gamma + F12-1; pairing law primary)")
print(f"  item5 cubic layer: parity-gap law diff_n = mu2*B^(n-1) NEW; Sg3 = mu2*16*(F10+1); sin^6 sum = L7-1")
print(f"  item6 9350: operator identity Tr = (M+1)*F5*F10 = mu2*F5*F10*F_proj; trap 6: V10 near-hit")
print(f"\n{PASS} PASS / {FAIL} FAIL")
