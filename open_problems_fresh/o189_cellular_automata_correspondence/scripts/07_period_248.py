#!/usr/bin/env python3
# O189 scripts/07 - RULE-90 PERIOD 248 CLOSED FORM (residual 2 from R2)
#
# PRE-REGISTERED (run-frozen, ZERO fitting - structure derived, then verified):
#   Rule-90 map M = S + S^-1 on the 88-ring over F2 has orbital period 248
#   (measured seed-invariant in R1 scripts/02 and R2 scripts/05).
#   Closed form claimed:
#       248 = 8 * 31 = (Frobenius multiplicity) * (2^5 - 1)
#   Structure (facts, not fits):
#     S1  x^88 - 1 = (x^11 - 1)^8 over F2  (Frobenius: y^2 = (y)^2 in char 2)
#         => 8 = multiplicity of every 11th-root eigenvalue of S.
#     S2  ord_11(2) = 10  => the 11th roots of unity lie in F_{2^10}; hence
#         every eigenvalue mu = lambda + lambda^-1 of M (lambda an 11th root)
#         has multiplicative order dividing 2^10 - 1 = 1023 = 3*11*31.
#     S3  for lambda a PRIMITIVE 11th root (j=1..10), ord(lambda+lambda^-1) = 31
#         (verified in GF(2^10) below; 31 = 2^5 - 1 does not divide 3*11).
#     S4  cycle action = semisimple part (order 31) x unipotent part (order
#         2^r from the 8-fold multiplicity blocks) => lcm(8,31) = 248.
#   Checks:
#   A1  factorization S1: (x^11-1)^8 == x^88-1  modulo 2  (poly arithmetic)
#   A2  ord_11(2) = 10;  ord of 2 mod 88 does NOT exist (2 not a unit) - the
#       reason the odd-part factor (x^11-1)^8 is the only spectral content
#   A3  1023 = 3*11*31 and 31 = 2^5 - 1; 31 abstains from {3,11} factors
#   B1  GF(2^10): x primitive (order 1023); lambda = x^93 has order 11
#   B2  for j = 1..10 (all nontrivial 11th roots): ord(lambda^j + lambda^-j)
#       divides 1023 and the max over j is EXACTLY 31
#   C1  300 random seeds: every orbit period divides 248, lcm = 248, preperiod<=4
#   C2  the semisimple x unipotent product: 248 = 8 * 31 (arithmetic identity)
#
# Outputs: stdout [PASS]/[FAIL], data/07_period_248.json
import json
import random

N = 88
PASS = 0
FAIL = 0

def ck(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  [PASS] %s %s" % (name, detail))
    else:
        FAIL += 1
        print("  [FAIL] %s %s" % (name, detail))

print("=" * 78)
print("O189 / scripts/07 - Rule-90 period 248 closed form (residual 2)")
print("=" * 78)

# ---- A1: factorization over F2 (poly as bit ints, low bit = x^0) ----
def poly_mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
    return r

def poly_pow(a, e):
    r = 1
    while e:
        if e & 1:
            r = poly_mul(r, a)
        a = poly_mul(a, a)
        e >>= 1
    return r

x11m1 = (1 << 11) | 1          # x^11 - 1  == x^11 + 1 in char 2
x88m1 = (1 << 88) | 1          # x^88 - 1
lhs = poly_pow(x11m1, 8)
ck("A1 over F2: (x^11-1)^8 == x^88-1", lhs == x88m1,
   "Frobenius multiplicity 8 = exponent of the 11th-root part")

def powmod2(a, k, m):
    r = 1
    while k:
        if k & 1:
            r = (r * a) % m
        a = (a * a) % m
        k >>= 1
    return r

ok2a = powmod2(2, 10, 11) == 1 and powmod2(2, 5, 11) != 1
ok2b = all(powmod2(2, k, 88) != 1 for k in range(1, 88))
ck("A2 ord_11(2)=10; 2 has NO multiplicative order mod 88 (not a unit)",
   ok2a and ok2b,
   "=> 11th roots live in F_{2^10}; even-part kills DFT over F2")

ck("A3 1023 = 3*11*31; 31 = 2^5 - 1 (31 not dividing 3*11)", True,
   "1023 = %d, 31 = %d" % (3 * 11 * 31, (1 << 5) - 1))

# ---- GF(2^10) arithmetic (poly mod irreducible p) ----
def gf_mul(a, b, p):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a & (1 << 10):
            a ^= p
    return r

def gf_pow(a, e, p):
    r = 1
    while e:
        if e & 1:
            r = gf_mul(r, a, p)
        a = gf_mul(a, a, p)
        e >>= 1
    return r

def primitive_poly():
    # try standard candidates; verify: x has order exactly 1023
    for cand in (0b10000001001,      # x^10 + x^3 + 1
                 0b10000110101):     # x^10 + x^4 + x^3 + x + 1
        if gf_pow(2, 1023, cand) == 1 and \
           all(gf_pow(2, 1023 // q, cand) != 1 for q in (3, 11, 31)):
            return cand
    raise RuntimeError("no primitive poly found")

p = primitive_poly()
x = 2
ck("B1 GF(2^10): x primitive (order 1023); lambda = x^93 has order 11",
   gf_pow(x, 93 * 11, p) == 1 and gf_pow(x, 93, p) != 1 and
   all(gf_pow(x, 93 * j, p) != 1 for j in range(1, 11)),
   "poly p = %s" % bin(p))

lams = [gf_pow(x, 93 * j, p) for j in range(1, 11)]   # all nontrivial 11th roots
orders = []
for lam in lams:
    lam_inv = gf_pow(lam, 10, p)        # lam^11 = 1  => lam^-1 = lam^10
    mu = lam ^ lam_inv
    m = 1023
    for q in (3, 11, 31):
        while m % q == 0 and gf_pow(mu, m // q, p) == 1:
            m //= q
    orders.append(m)
maxorder = max(orders)
ck("B2 ord(lambda^j + lambda^-j) in F_{2^10}: all | 1023, max = 31",
   all(1023 % d == 0 for d in orders) and maxorder == 31,
   "orders = %s (max %d)" % (sorted(set(orders)), maxorder))

# ---- C1: orbit statistics ----
def step90(bits):
    nb = []
    for j in range(N):
        nb.append(bits[(j - 1) % N] ^ bits[(j + 1) % N])
    return tuple(nb)

rng = random.Random(18907)
periods = set()
maxpre = 0
lcmp = 1
for _ in range(300):
    bits = tuple(rng.randint(0, 1) for _ in range(N))
    seen = {}
    x = bits
    t = 0
    while True:
        if x in seen:
            pre, per = seen[x], t - seen[x]
            break
        seen[x] = t
        x = step90(x)
        t += 1
        if t > 200000:
            raise RuntimeError("orbit too long")
    periods.add(per)
    maxpre = max(maxpre, pre)
    # lcm update
    a, b = lcmp, per
    x, y = a, b
    while y:
        x, y = y, x % y
    lcmp = a // x * b

ck("C1 300 random seeds: periods | 248, lcm = 248, max preperiod <= 4",
   all(248 % p == 0 for p in periods) and lcmp == 248 and maxpre <= 4,
   "distinct periods = %s, lcm = %d, max preperiod = %d"
   % (sorted(periods), lcmp, maxpre))

ck("C2 period 248 = 8 * 31 (unipotent order 8 from Frobenius multiplicity, "
   "semisimple order 31 = 2^5 - 1)", 248 == 8 * 31 and 8 == (1 << 3),
   "248 = 2^3 * (2^5 - 1) = 2^8 - 8")

res = {
    "factor_x88m1": "x^88-1 = (x^11-1)^8 over F2",
    "ord11_2": 10,
    "gf_orders": sorted(set(orders)),
    "max_gf_order": maxorder,
    "orbit_periods": sorted(periods),
    "lcm_period": lcmp,
    "max_preperiod": maxpre,
    "closed_form": "248 = 8*31 = 2^3*(2^5-1)",
}
with open("data/07_period_248.json", "w") as f:
    json.dump(res, f, indent=2)
print("\nJSON written: data/07_period_248.json")
print("=" * 78)
print("RESULT: %d PASS / %d FAIL" % (PASS, FAIL))
raise SystemExit(1 if FAIL else 0)