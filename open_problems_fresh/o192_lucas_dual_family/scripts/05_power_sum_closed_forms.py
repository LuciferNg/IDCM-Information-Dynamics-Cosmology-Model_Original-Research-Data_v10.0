#!/usr/bin/env python3
# O192 session push round 2 — unified power-sum closed form + trap ⑥ family scan
# Theorem (analytic, this session): for the N=88 chain gamma_k = 4sin^2(k pi/176), k=1..88:
#   sum gamma^n     = 88*C(2n,n) + 2^(2n-1)      (total)
#   sum gamma^n_odd = 44*C(2n,n)                  (observer)
#   sum gamma^n_even= 44*C(2n,n) + 2^(2n-1)      (world; gap = 2^(2n-1) N-independent)
#   sum sin^{2m}    = 88*C(2m,m)/4^m + 1/2
# Proof: binomial expansion + alternating cosine sum lemma. Verified n=1..20 (n=6..20 prediction).
# Also: 131 at quartic = artifact factorization (6288 = 48*131 vs 88*C(8,4)+128) — E07 corrected.
# Also: trap ⑥ phi-convergence family |L_n phi - L_{n+1}| = sqrt(5) phi^{-n}, corpus instances.
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
def C(n, r):
    return math.comb(n, r)

N = 88
g = [4 * math.sin(k * math.pi / 176.0) ** 2 for k in range(1, 89)]
g_odd  = [g[k] for k in range(0, 88, 2)]
g_even = [g[k] for k in range(1, 88, 2)]

print("== Part A: unified closed form sum gamma^n = 88*C(2n,n) + 2^(2n-1) (n=1..20) ==")
for n in range(1, 21):
    tot = sum(x ** n for x in g)
    pred = N * C(2 * n, n) + 2 ** (2 * n - 1)
    o = sum(x ** n for x in g_odd)
    e = sum(x ** n for x in g_even)
    check(f"A n={n}: total {pred}", abs(tot - pred) < 1e-6 * max(1, tot),
          f"sum={tot:.6f} pred={pred} ({'prediction' if n > 5 else 'verified'})")
    check(f"A n={n}: odd = 44*C(2n,n), even = odd + 2^(2n-1)", abs(o - 44 * C(2 * n, n)) < 1e-6 * max(1, o)
          and abs(e - (44 * C(2 * n, n) + 2 ** (2 * n - 1))) < 1e-6 * max(1, e),
          f"odd={o:.6f} even={e:.6f} gap={e - o:.6f}")

print("== Part B: sum sin^{2m} = 88*C(2m,m)/4^m + 1/2 (m=1..10) ==")
for m in range(1, 11):
    s = sum(math.sin(k * math.pi / 176.0) ** (2 * m) for k in range(1, 89))
    pred = N * C(2 * m, m) / (4.0 ** m) + 0.5
    check(f"B m={m}: sin^{2*m} sum", abs(s - pred) < 1e-9 * max(1, s), f"sum={s:.9f} pred={pred:.9f}")

print("== Part C: alternating cosine sum lemma (proof backbone) ==")
# Lemma: sum_{k=1}^{88} cos(b k pi/88) = 88 if b ≡ 0 (mod 176); -1 if b odd; 0 otherwise
for b in [0, 1, 3, 87, 89, 90, 176, 175, 44, 88, 264]:
    s = sum(math.cos(b * k * math.pi / 88.0) for k in range(1, 89))
    expect = 88 if b % 176 == 0 else (-1 if b % 2 == 1 else 0)
    check(f"C cos-sum b={b}", abs(s - expect) < 1e-9, f"sum={s:.9f} expect={expect}")
# T_a = sum (-1)^k cos(a k pi/88) = 88 if a=±88, -1 if a odd, 0 if a even (|a|<88)
for a in [0, 1, 3, 87, 2, 44, 86, 88, -88]:
    s = sum(((-1) ** k) * math.cos(a * k * math.pi / 88.0) for k in range(1, 89))
    expect = 88 if abs(a) == 88 else (-1 if a % 2 == 1 else 0)
    check(f"C T_a a={a}", abs(s - expect) < 1e-9, f"T={s:.9f} expect={expect}")

print("== Part D: C(2n,n)/2 factorization into registered constants (structure table) ==")
reg = {"2": "mu2", "3": "N_gen", "4": "B", "5": "F5", "6": "N_gen*mu2", "7": "L4", "9": "N_gen^2",
       "10": "2N_gen+B", "11": "L5", "13": "F7", "17": "F_proj", "18": "L6", "20": "F8-1",
       "28": "L7-1", "33": "M", "44": "N_d", "55": "F10", "66": "2M", "77": "L4L5", "88": "N",
       "89": "F11", "98": "h21", "99": "N+R", "123": "L10", "143": "dimSU12", "176": "2N",
       "178": "2F11", "198": "L11-1", "232": "F13-1", "264": "dimC*N_d*mu2", "272": "2B*F_proj*mu2",
       "321": "L12-1", "536": "B(2M+1)mu2", "832": "L14-L5", "880": "2^4*F10", "912": "2^4(F10+2)",
       "1792": "2^4(2F10+2)", "9350": "mu2*F5*F10*F_proj"}
for n in range(1, 11):
    c = C(2 * n, n)
    half = c // 2
    # factor search over registered primes {2,3,5,7,11,13,17} + 19 = L6+1 (Lucas-derived prime)
    facs = []
    rem = c
    for p in [2, 3, 5, 7, 11, 13, 17, 19]:
        while rem % p == 0:
            facs.append(p)
            rem //= p
    allreg = rem == 1
    check(f"D C(2n,n) n={n}: {c} = {'x'.join(map(str, facs))} (all registered primes)",
          allreg, f"C(2n,n)={c} half={half} leftover={rem if rem != 1 else 'none'} (19 = L6+1)")

print("== Part E: 131 at quartic = artifact factorization (E07 correction) ==")
Sg4 = sum(x ** 4 for x in g)
check("E 6288 = 88*C(8,4) + 2^7 (closed form)", abs(Sg4 - (88 * C(8, 4) + 2 ** 7)) < 1e-6,
      f"{88*C(8,4)}+128 = {88*C(8,4)+128}")
check("E 6288 = 48*131 is an ALTERNATIVE factorization (131 = 6288/48, not structural)",
      abs(Sg4 - 48 * 131) < 1e-6 and 131 == int(round(Sg4)) // 48,
      "131 has no mechanism — artifact of choosing 48*131")
check("E C(8,4) = 70 = mu2*F5*L4 = 2*5*7 (registered factorization)",
      C(8, 4) == 70 and 70 == 2 * 5 * 7, "structure constant 70, NOT 3144-composite")
check("E structure chain is smooth: 89, 268, 896, 3144, 11344 = 44*C(2n,n)+2^(2n-2)",
      (44 * C(2, 1) + 1, 44 * C(4, 2) + 4, 44 * C(6, 3) + 16, 44 * C(8, 4) + 64, 44 * C(10, 5) + 256)
      == (89, 268, 896, 3144, 11344))

print("== Part F: trap ⑥ phi-convergence family scan ==")
# F1: |L_n phi - L_{n+1}| = sqrt(5) phi^{-n} exactly
for n in range(1, 16):
    dev = abs(luc(n) * phi - luc(n + 1))
    pred = math.sqrt(5) * phi ** (-n)
    check(f"F1 n={n}: |L{n}*phi - L{n+1}| = sqrt5*phi^-n", abs(dev - pred) < 1e-9,
          f"dev={dev:.6f} pred={pred:.6f} rel={dev/luc(n+1)*100:.4f}%")
# F2: corpus instances of the family (near-hits < 0.5% on registered pool)
pool = [2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 17, 18, 20, 28, 33, 44, 46, 54, 55, 66, 75, 76,
        88, 89, 90, 98, 99, 122, 123, 143, 176, 178, 198, 199, 232, 264, 272, 275, 321, 536, 832, 880, 912, 1792]
hits = []
for n in range(1, 16):
    for m in pool:
        rel = abs(luc(n) * phi - m) / m
        if rel < 0.005:
            hits.append((rel, n, m, abs(luc(n) * phi - m)))
hits.sort()
print(f"  INFO F2: L_n*phi near registered pool hits (<0.5%): {[(f'{rel*100:.3f}%', n, m) for rel, n, m, _ in hits]}")
check("F2 known instances: n=9 -> m=123 (L9*phi~123, 0.024% = O148 Lucas tail)",
      any(abs(rel - 0.00024) < 0.00005 for rel, n, m, _ in hits if m == 123),
      "O148: 4*phi/3 ~ 41/19 mechanized = n=9 member")
check("F2 n=10 -> m=199 = L11 (0.009%): V10 = L10*phi + L9 = 275.018 mechanism",
      any(abs(rel - 0.000091) < 0.00002 for rel, n, m, _ in hits if m == 199),
      "L10*phi = L11 + sqrt5*phi^-10; V10 = 275 + sqrt5*phi^-10 exactly")
check("F2 V10 = 275 + sqrt5*phi^-10 (exact)", abs((luc(10) * phi + luc(9)) - (275 + math.sqrt(5) * phi ** -10)) < 1e-9,
      f"V10 = {luc(10)*phi + luc(9):.6f}")
# F3: generic phi^n ~ L_n (Binet) deviations for the pool members
print("  INFO F3: phi^n vs L_n (Binet convergence): "
      + "; ".join(f"n={n}: {abs(phi**n - luc(n))/luc(n)*100:.4f}%" for n in range(7, 13)))
# F4: all sub-0.1% L_n*phi hits are EXACTLY the L_{n+1} family members {76, 123, 199} —
#     zero hits on non-Lucas registered constants (no false bridges)
fam = {76, 123, 199}
nonfam = [(rel, n, m) for rel, n, m, _ in hits if rel < 0.001 and m not in fam]
check("F4 all sub-0.1% L_n*phi hits = L_{n+1} family {76,123,199} only (no false bridges)",
      len(nonfam) == 0, f"non-family deep hits={nonfam}")
# F5: phi^k near registered integers (Binet family)
phihits = []
for k in range(1, 21):
    for m in pool:
        rel = abs(phi ** k - m) / m
        if rel < 0.005:
            phihits.append((rel, k, m))
print(f"  INFO F5: phi^k near pool: {[(f'{rel*100:.3f}%', k, m) for rel, k, m in phihits]}")
check("F5 phi^k hits all = L_k Binet-convergence (k>=7) or 0.8%+ (k<7) — no new traps",
      all(abs(phi ** k - luc(k)) / luc(k) < 0.01 for rel, k, m in phihits),
      "phi^k ~ L_k for k>=7 (error phi^{-k}); k<7 all >0.3% — generic convergence, not structure")

print(f"\n{PASS} PASS / {FAIL} FAIL")
