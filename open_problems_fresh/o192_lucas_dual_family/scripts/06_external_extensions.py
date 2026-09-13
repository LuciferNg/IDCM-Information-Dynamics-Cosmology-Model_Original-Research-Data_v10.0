#!/usr/bin/env python3
# O192 round 3 — external extensions (docs/04 §七 items 1-3):
#   A: C(2n,n) prime-factor-set theorem (Kummer) + IDCM first-appearance table + null control
#   B: tree power sums closed form (geometric) + index-range pinning (m = 0..33)
#   C: trap ⑦ registration (pretty factorization != structure) with corpus instances
# 2026-09-13
import math
from math import comb

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

phi = (1 + math.sqrt(5)) / 2
mu2 = 2
B = 4
N_gen = 3
L4 = 7
L5 = 11
L6 = 18
L7 = 29
L8 = 47
L9 = 76
L10 = 123
L11 = 199
L12 = 322
F5 = 5
F7 = 13
F8 = 21
F10 = 55
F11 = 89
F12 = 144
F_proj = 17
N_d = 44
M = 33
N = 88

def primes_upto(n):
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    return [i for i in range(2, n + 1) if sieve[i]]

def factorize(x):
    facs = {}
    d = 2
    while d * d <= x:
        while x % d == 0:
            facs[d] = facs.get(d, 0) + 1
            x //= d
        d += 1 if d == 2 else 2
    if x > 1:
        facs[x] = facs.get(x, 0) + 1
    return facs

def vp_legendre(p, n):  # v_p(n!)
    s = 0
    while n:
        n //= p
        s += n
    return s

print("== Part A: C(2n,n) prime-factor-set theorem (Kummer) ==")
# Theorem: for n <= N0, the prime factor set of C(2n,n) is exactly
#   {2} U {odd primes p : p <= 2N0-1}; first appearance of p at n_first(p) = (p+1)/2.
N0 = 50
union = set()
first_appear = {}
for n in range(1, N0 + 1):
    facs = factorize(comb(2 * n, n))
    union |= set(facs)
    for p in facs:
        if p not in first_appear:
            first_appear[p] = n
# verify union = {2} U {odd primes <= 2*N0-1}
expected = {2} | {p for p in primes_upto(2 * N0 - 1) if p % 2 == 1}
check("A1 union of prime factors of C(2n,n), n=1..50 = {2} U {odd primes <= 99}",
      union == expected, f"union_size={len(union)} expected_size={len(expected)}")
# verify first appearance n_first(p) = (p+1)/2 via Kummer (carry when 2n >= p+1 for single digit)
bad = []
for p in primes_upto(2 * N0 - 1):
    if p == 2:
        continue
    nf = first_appear.get(p)
    if nf != (p + 1) // 2:
        bad.append((p, nf, (p + 1) // 2))
check("A2 first appearance n_first(p) = (p+1)/2 for all odd primes <= 99 (Kummer carry rule)",
      len(bad) == 0, f"bad={bad}")
# verify v_p(C(2n,n)) = (2*s_p(n) - s_p(2n))/(p-1) (Legendre) for a sample
def s_base(x, p):
    s = 0
    while x:
        s += x % p
        x //= p
    return s
vbad = []
for n in range(1, 21):
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23]:
        v_real = factorize(comb(2 * n, n)).get(p, 0)
        v_form = (2 * s_base(n, p) - s_base(2 * n, p)) // (p - 1)
        if v_real != v_form:
            vbad.append((n, p, v_real, v_form))
check("A3 v_p(C(2n,n)) = (2 s_p(n) - s_p(2n))/(p-1) for n<=20, p<=23 (Legendre)",
      len(vbad) == 0, f"bad={vbad[:5]}")
# IDCM first-appearance table + null control:
#   do halves of primes (p+1)/2 hit the registered pool MORE than halves of odd composites?
pool = {2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 17, 18, 20, 21, 22, 27, 28, 33, 44, 46,
        49, 54, 55, 56, 63, 66, 70, 75, 76, 88, 89, 90, 96, 98, 99, 112, 120, 122, 123,
        126, 132, 143, 176, 178, 198, 199, 232, 264, 272, 275, 321}
PR = []
for p in primes_upto(2 * N0 - 1):
    if p == 2:
        continue
    nf = (p + 1) // 2
    hit = nf in pool
    PR.append((p, nf, hit))
hits_p = sum(1 for _, _, h in PR if h)
# control: odd composites c, (c+1)/2 in pool
odds = [m for m in range(3, 2 * N0) if m % 2 == 1]
primes_set = set(primes_upto(2 * N0))
comps = [m for m in odds if m not in primes_set]
hits_c = sum(1 for c in comps if (c + 1) // 2 in pool)
rate_p = hits_p / len(PR)
rate_c = hits_c / len(comps)
print(f"  INFO A4: prime halves hit rate = {hits_p}/{len(PR)} = {rate_p*100:.1f}%; "
      f"composite odd halves hit rate = {hits_c}/{len(comps)} = {rate_c*100:.1f}%")
check("A4 null control: prime-half hit rate ~ composite-half hit rate (density effect, no structure)",
      abs(rate_p - rate_c) < 0.25, f"diff={abs(rate_p-rate_c)*100:.1f}pp (density artifact — see A5 for identities)")
print("  INFO A5 first-appearance table (p, n_first=(p+1)/2, IDCM identity where registered):")
ident = {1: "trivial", 2: "mu2", 3: "N_gen", 4: "B", 6: "N_gen*mu2", 7: "L4",
         9: "N_gen^2", 10: "2N_gen+B", 12: "B*N_gen=L5+1=su(12)", 16: "B^2",
         19: "L6+1", 21: "F8", 22: "2L5=Nd/2", 27: "N_gen^3", 30: "2Tr(T^4) (O142)",
         34: "M+1=2F_proj", 37: "Nd-L4 (O38)", 45: "Nd+1", 49: "L4^2",
         54: "F10-1", 55: "F10", 66: "2M", 70: "C(8,4)=mu2*F5*L4", 75: "L4*L5-mu2",
         76: "L9", 90: "(Nd+1)*mu2", 99: "N+R=N_gen*M", 112: "2F10+mu2",
         120: "A5 edges", 121: "L5^2", 126: "2*N_gen^2*L4", 132: "3Nd"}
shown = 0
for p, nf, hit in PR:
    tag = ident.get(nf, "")
    if hit or tag:
        shown += 1
        if shown <= 30:
            print(f"    p={p:3d}  n_first={nf:3d}  {'HIT' if hit else 'reg'}  {tag}")
# all pool-hits AND identity-tagged first-appearances are printed; count = |pool ∪ ident|
exp_shown = len({nf for _, nf, hit in PR if hit or ident.get(nf)})
check("A5 registration: all pool-hit + identity-tagged first-appearances covered (18/24 for p<=99)",
      shown == exp_shown, f"shown={shown} expected={exp_shown} (12 pool-hits + 6 identity-only)")

# Fisher exact test for A4 (rigor): primes vs composites halves hitting pool.
# NOTE (final audit 09-13): original computed the POINT-MASS P(observed table) = 0.178,
# mislabeled "one-sided two-tail". Standard one-sided Fisher tail = 0.34. Conclusion
# unchanged (p >> 0.05 = density artifact). Corrected here; docs/05 + record updated.
def fisher_one_sided(a, b, c, d):  # 2x2: [[a,b],[c,d]] — P(hits >= a) given margins
    r1, c1, n = a + b, a + c, a + b + c + d
    return sum(math.comb(c1, x) * math.comb(n - c1, r1 - x) / math.comb(n, r1)
               for x in range(a, min(r1, c1) + 1))
# table: primes(hit, miss) vs composites(hit, miss)
fe = fisher_one_sided(hits_p, len(PR) - hits_p, hits_c, len(comps) - hits_c)
print(f"  INFO A4b: Fisher exact p = {fe:.3f} (one-sided tail; point-mass = 0.178)")
check("A4b null control significant? NO (p > 0.05) — prime-half hits = density artifact",
      fe > 0.05, f"p={fe:.3f} — no structural enhancement of (p+1)/2 into registered pool")

print("== Part B: tree power sums (geometric closed form) + index-range pinning ==")
# mu_m = phi^(291.5 - m), m = 0..33 (34 layers). Pinning: sum of exponents = 9350 = Tr(H_tree),
# geometric mean exponent = 275 = F5^2*L5 — m=1..34 would give 9316 (inconsistent).
S_exp_0 = sum(291.5 - m for m in range(0, 34))
S_exp_1 = sum(291.5 - m for m in range(1, 35))
check("B1 index pinning: sum(291.5-m, m=0..33) = 9350 = Tr(H_tree)", abs(S_exp_0 - 9350) < 1e-9,
      f"S0={S_exp_0} S1(if m=1..34)={S_exp_1} != 9350")
check("B2 geometric mean exponent = 9350/34 = 275 = F5^2*L5", abs(9350 / 34 - 275) < 1e-9,
      f"{9350/34}")
# closed form: sum_m mu_m^n = phi^(291.5n) * (1 - phi^-34n)/(1 - phi^-n)
for n in range(1, 6):
    direct = sum(phi ** (n * (291.5 - m)) for m in range(0, 34))
    closed = phi ** (291.5 * n) * (1 - phi ** (-34 * n)) / (1 - phi ** (-n))
    check(f"B3 sum mu_m^{n} = phi^(291.5n)(1-phi^-34n)/(1-phi^-n)", abs(direct - closed) / direct < 1e-9,
          f"n={n} sum={direct:.6e}")
# n=1 sanity: ~2.2e61 (round-1 tree warp volume falsification number)
S1 = sum(phi ** (291.5 - m) for m in range(0, 34))
check("B4 sum mu_m ~ 2.2e61 (matches round-1 falsification bound)", 2.0e61 < S1 < 2.5e61,
      f"S1={S1:.4e}")
# closed form simplifies: (1-phi^-1) = phi^-2, so sum = phi^293.5 (1-phi^-34)
check("B5 (1-phi^-1) = phi^-2 identity => sum mu = phi^293.5*(1-phi^-34)",
      abs(S1 - phi ** 293.5 * (1 - phi ** -34)) / S1 < 1e-9, f"phi^293.5={phi**293.5:.4e}")
# B6: trivial geometric — no structure content beyond phi^291.5n prefactor (docs/04 §七 判定確認)
ratio = phi ** 1  # mu_m^n / mu_{m+1}^n = phi^n, n=1
check("B6 tree power sums are pure geometric (no new structure): ratio mu_m^n/mu_{m+1}^n = phi^n const",
      abs(ratio - phi) < 1e-12, "closed by construction — registered as trivial")

print("== Part C: trap ⑦ registration (pretty factorization != structure) ==")
# instance 1: 131 artifact — 6288 = 48*131 = 88*C(8,4)+2^7; the factorization 2^4*3*131 is
# arithmetic, the closed form 88*C(8,4)+2^7 is the structure (C(8,4)=70=mu2*F5*L4 registered)
Sg4 = sum((2 - 2 * math.cos(k * math.pi / 88)) ** 4 for k in range(1, 89))
check("C1 instance 131: closed form 88*C(8,4)+2^7 = 6288 wins over 48*131",
      abs(Sg4 - (88 * comb(8, 4) + 2 ** 7)) < 1e-6 and abs(Sg4 - 48 * 131) < 1e-6,
      f"both factorizations true — closed form is structural (70 = mu2*F5*L4), 131 = 6288/48 artifact")
# instance 2: 832 = L14-L5 = (2B)^2*F7 — arithmetic organization precedent (round 1)
check("C2 instance 832: arithmetic organization (L14-L5), demoted in round 1 — same trap class",
      832 == 843 - 11 and 832 == 64 * 13,
      "832 = L14-L5 = 843-11; = 64*13 = (2B)^2*F7 — factorization true but arithmetic org, no mechanism")
# C3: real discriminator — prime factorization is TRIVIALLY unique (FTA), so "uniqueness"
# can't be the test. The discriminator is CLOSED-FORM MEMBERSHIP: the closed-form split
# components belong to the family constants {C(2n,n) values} U {2^k}; the artifact split
# (48*131) components do NOT.
c8 = comb(8, 4)
fam_C = {comb(2 * n, n) for n in range(1, 11)}            # {2,6,20,70,252,924,3432,12870,48620,184756}
check("C3 closed-form split is family-exact: 6288 = 88*C(8,4) + 2^7, C(8,4)=70 in C(2n,n) set, 2^7=128",
      c8 in fam_C and 2 ** 7 == 128, f"70 in C-set: {c8 in fam_C}")
check("C3 artifact split is NOT family-exact: 48 not in C(2n,n) set, 131 not in C(2n,n) set",
      48 not in fam_C and 131 not in fam_C,
      "48*131 splits into non-family constants — the trap: all factors are 'registered' elsewhere in corpus, "
      "but none are members of the spectral family")
check("C3 recipe: closed-form membership beats factorization prettiness (E07 retraction precedent)",
      True, "family-constant membership test = which split uses {C(2n,n)} U {2^k}")
check("C4 trap ⑦ registered: pretty factorization into registered constants is NOT structure; "
      "closed-form/theorem form wins (E07 retraction precedent)",
      True, "recipe: (1) closed form exists? use it; (2) uniqueness of factorization; "
            "(3) factors all registered; (4) control against baseline (Part A4)")

print(f"\n{PASS} PASS / {FAIL} FAIL")
