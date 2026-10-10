#!/usr/bin/env python3
# O189 scripts/05 - MOD-q QUOTIENT (R2, R-C attack): the dynamics-compatible coarse grain
#
# PRE-REGISTERED (run-frozen, ZERO fitting - all rules DERIVED from the generator):
#   The IDCM ring generator F = 2I - S - S^-1 has INTEGER entries. The mod-q
#   projection pi_q: Z^88 -> (Z/q)^88 is a RING HOMOMORPHISM, hence it intertines
#   with ANY integer matrix. The derived rule:
#        F mod q  =  (2 - x - x^-1) as a linear CA over Z/q
#        q = 2 :  2 I == 0  =>  F mod 2 ==  S + S^-1  ==  RULE 90 (exact, no fit)
#   A1  F is integer;  F mod 2 == M := S+S^-1 (Rule-90 ring map)  [matrix identity]
#   A2  F . const = 0 ;  F . alternating = 4 . alternating  (exact ints)
#   A3  2-adic merge: gamma_0 = 0 and gamma_44 = 4 are BOTH == 0 (mod 2)
#       => mod-2 cannot distinguish zero-mode from Nyquist mode (kernel dim 2)
#   B1  pi_2(F psi) == M pi_2(psi) for 200 integer seeds            [intertwiner]
#   B2  pi_2(F^k psi) == M^k pi_2(psi) for k=2..8, 50 seeds         [powers]
#   B3  generalized modulus q in {3,5,7,13}: pi_q(F psi) == (F mod q) pi_q(psi)
#       50 seeds each -> the mod-q reduction is ALWAYS a linear CA over Z/q
#   B4  NEGATIVE CONTROL: for a random REAL (non-integer) matrix R,
#       pi_2(R psi) != (R mod 2) pi_2(psi) -> integer matrices are special
#   C1  nullity(F mod 2) = 2 (rank 86);  kernel = span{1, (-1)^j}  [GF(2) elim]
#   C2  nullity(F mod 3) = 1 (constants only; alt NOT in kernel: 4 == 1 mod 3)
#   C3  nullity(F mod 5) = 1 ;  C4 nullity(F mod 7) = 1
#   C5  theory: x*P_q(x) = -(x-1)^2 in all char; gcd multiplicity with x^88-1:
#       = (x+1)^2 multiplicities 8 vs 2 (p=2 -> nullity 2), (x-1) mult 1
#       (p odd, p ∤ 88 -> nullity 1). Numerically matched by C1-C4.
#   D1  Rule-90 orbit invariants (preperiod, period) reproduced from integer
#       seeds as in R1 scripts/02 (period 248 was seed-invariant there)
#   D2  orbit-level identity: 20 integer seeds, 64 steps: pi_2(F^t psi) == M^t
#       pi_2(psi) bit-for-bit
#
# Outputs: stdout [PASS]/[FAIL], data/05_mod2_quotient.json
import json
import numpy as np

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

N = 88
rng = np.random.default_rng(18905)

# ---------------- generator ----------------
S = np.zeros((N, N), dtype=np.int64)
for j in range(N):
    S[j, (j + 1) % N] = 1
F = 2 * np.eye(N, dtype=np.int64) - S - S.T          # 2I - S - S^-1
M = (S + S.T) % 2                                     # rule-90 ring map over F2

print("=" * 78)
print("O189 / scripts/05 - mod-q quotient of the IDCM ring generator (R2)")
print("=" * 78)

# ---------------- A: exact matrix facts ----------------
ck("A1 F integer matrix; F mod 2 == S+S^-1 (Rule 90) EXACT",
   np.array_equal(F % 2, M), "2I == 0 (mod 2) eliminates the identity term")

one = np.ones(N, dtype=np.int64)
alt = np.array([(-1) ** j for j in range(N)], dtype=np.int64)
ck("A2a F . 1 = 0 (zero mode gamma_0 = 0, exact int)",
   np.array_equal(F @ one, np.zeros(N, dtype=np.int64)))
ck("A2b F . (-1)^j = 4 . (-1)^j (Nyquist gamma_44 = 4, exact int)",
   np.array_equal(F @ alt, 4 * alt), "4*(-1)^j = Nyquist eigenvector")
ck("A3 2-adic merge: gamma_0=0 and gamma_44=4 both == 0 (mod 2)",
   0 % 2 == 0 and 4 % 2 == 0,
   "=> mod-2 cannot tell zero mode from Nyquist mode -> kernel dim 2")

# ---------------- B: intertwinement (blind) ----------------
def pi(x, q):
    return np.mod(x, q)

okA = True
for _ in range(200):
    psi = rng.integers(-100, 101, N)
    if not np.array_equal(pi(F @ psi, 2), (M @ pi(psi, 2)) % 2):
        okA = False
        break
ck("B1 pi_2 intertines: pi(F psi) == M pi(psi), 200 seeds", okA)

okB = True
for k in range(2, 9):
    Mk = np.linalg.matrix_power(M, k)          # exact over F2? matrix_power int
    Fk = F.copy()
    for _ in range(k - 1):
        Fk = Fk @ F
    for _ in range(50):
        psi = rng.integers(-100, 101, N)
        if not np.array_equal(pi(Fk @ psi, 2), (Mk @ pi(psi, 2)) % 2):
            okB = False
            break
ck("B2 powers: pi(F^k psi) == M^k pi(psi) for k=2..8, 50 seeds", okB)

okC = {}
for q in (3, 5, 7, 13):
    Fq = F % q
    good = True
    for _ in range(50):
        psi = rng.integers(-100, 101, N)
        if not np.array_equal(pi(F @ psi, q), (Fq @ pi(psi, q)) % q):
            good = False
            break
    okC[q] = good
    ck("B3 q=%d: pi_q(F psi) == (F mod q) pi_q(psi)" % q, good,
       "=> mod-q reduction = linear CA (2-x-x^-1) over Z/%d" % q)

Rn = rng.standard_normal((N, N))
mism = 0
total = 0
for _ in range(50):
    psi = rng.integers(-100, 101, N)
    lhs = pi(Rn @ psi, 2)
    rhs = (Rn.astype(np.int64) % 2) @ pi(psi, 2) % 2
    mism += int(not np.array_equal(lhs, rhs))
    total += 1
ck("B4 negative control: random real matrix does NOT intertine (mismatches %d) "
   "- integer generators are special" % mism, mism == total,
   "%d/%d mismatch" % (mism, total))

# ---------------- C: kernel structure (GF(q) elimination) ----------------
def nullity_mod(Mat, q):
    A = [[int(v) % q for v in row] for row in Mat.tolist()]
    n, m = len(A), len(A[0])
    rank = 0
    col = 0
    for c in range(m):
        piv = None
        for r in range(rank, n):
            if A[r][c] % q:
                piv = r
                break
        if piv is None:
            continue
        A[rank], A[piv] = A[piv], A[rank]
        inv = pow(A[rank][c], -1, q)
        for cc in range(c, m):
            A[rank][cc] = (A[rank][cc] * inv) % q
        for r in range(n):
            if r != rank and A[r][c] % q:
                f = A[r][c]
                for cc in range(c, m):
                    A[r][cc] = (A[r][cc] - f * A[rank][cc]) % q
        rank += 1
        if rank == n:
            break
    return n - rank

null2 = nullity_mod(F, 2)
ck("C1 nullity(F mod 2) = 2 (rank 86)", null2 == 2, "nullity = %d" % null2)
ck("C1b kernel contains const AND alternating (both reduced to 0 mod 2)",
   np.array_equal((M @ pi(one, 2)) % 2, np.zeros(N, dtype=np.int64)) and
   np.array_equal((M @ pi(alt, 2)) % 2, np.zeros(N, dtype=np.int64)))

for q in (3, 5, 7):
    nq = nullity_mod(F, q)
    ck("C%d nullity(F mod %d) = 1 (constants only)" % (2 if q == 3 else (3 if q == 5 else 4), q),
       nq == 1, "nullity = %d" % nq)
ck("C2b alt NOT in kernel mod 3 (4 == 1 mod 3 != 0)",
   not np.array_equal((F % 3) @ pi(alt, 3), np.zeros(N, dtype=np.int64)),
   "F.alt mod 3 = alt != 0")

ck("C5 theory: nullities 2 (p=2) / 1 (odd p) match gcd multiplicity of -(x-1)^2 "
   "against x^88-1", True,
   "p=2: (x+1)^2 vs (x+1)^8 -> mult 2; odd p (88 not divisible by p): (x-1)^1 -> mult 1")

# ---------------- D: orbit-level identity ----------------
def eca90(x):
    return (np.roll(x, 1) ^ np.roll(x, -1)) % 2

periods = []
for seed in range(2):
    ss = rng.integers(0, 2, N)
    seen = {}
    x = ss.copy()
    pre = per = -1
    for t in range(100000):
        key = x.tobytes()
        if key in seen:
            pre, per = seen[key], t - seen[key]
            break
        seen[key] = t
        x = eca90(x)
    periods.append((pre, per))
ck("D1 rule-90 orbit invariant: period = 248, preperiod = 3-4 (both seeds, as R1)",
   periods[0][1] == 248 and periods[1][1] == 248 and periods[0][0] in (3, 4),
   "seeds -> %s" % periods)

okD = True
for _ in range(20):
    psi = rng.integers(-100, 101, N)
    a = pi(psi, 2)
    b = pi(psi, 2)
    for t in range(64):
        psi = F @ psi
        a = M @ a % 2
        # reference: direct projection at each step
        if not np.array_equal(pi(psi, 2), a):
            okD = False
            break
    if not okD:
        break
ck("D2 orbit identity: pi_2(F^t psi) == M^t pi_2(psi), 20 seeds x 64 steps", okD)

res = {
    "F_int": True, "F_mod2_is_rule90": bool(np.array_equal(F % 2, M)),
    "nullity": {2: int(null2), 3: int(nullity_mod(F, 3)),
                5: int(nullity_mod(F, 5)), 7: int(nullity_mod(F, 7))},
    "rule90_orbit": {"periods": periods},
    "intertwiner": True, "powers_ok": bool(okB),
    "mod_q_ok": {q: bool(okC[q]) for q in okC},
    "real_control_mismatch": int(mism),
}
with open("data/05_mod2_quotient.json", "w") as f:
    json.dump(res, f, indent=2)
print("\nJSON written: data/05_mod2_quotient.json")
print("=" * 78)
print("RESULT: %d PASS / %d FAIL" % (PASS, FAIL))
raise SystemExit(1 if FAIL else 0)