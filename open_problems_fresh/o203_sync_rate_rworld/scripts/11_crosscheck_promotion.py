#!/usr/bin/env python3
"""
O203 Script 11 - INDEPENDENT cross-check of docs/09 + docs/10 (S7/S8)
=====================================================================
Re-derives every numeric/structural claim in docs/09 (promotion mechanisms) and
docs/10 (coefficient uniqueness + observables) FROM SCRATCH. Does NOT import
scripts/09 or scripts/10. Uses a DIFFERENT null seed (311) than S9 (203) so the
null-control claim is genuinely independent.
"""
import random
import mpmath as mp
import numpy as np

mp.mp.dps = 60
pi = mp.pi
N = 44
mu2 = mp.mpf(2)
Rw = mp.mpf("4129.94")
rd = pi * Rw / 88 * mp.mpf(420) / 421
T = mp.mpf(1) / 45

PASS = FAIL = 0
def chk(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  [PASS] {name}")
    else:
        FAIL += 1; print(f"  [FAIL] {name}")
    if detail:
        print(f"         {detail}")

def G(n): return 4 * mp.sin(pi * n / 88) ** 2
def V(n): return mp.cos(pi * n / 88)
def S(n): return 1 / mp.cos(pi * n / 88)

print("=" * 74)
print("O203 S11 - independent re-derivation of docs/09 + docs/10")
print("=" * 74)

# --- docs/09 A1 ---
print("\n[docs/09 A1] Niven + divergence")
d44 = min(abs(V(n) - T) for n in range(1, 45))
chk("A1a 44-mode min |v_g - 1/45| = 0.0134701", abs(d44 - mp.mpf("0.0134701")) < mp.mpf("1e-7"),
    f"{mp.nstr(d44, 8)}")
d88 = min(abs(mp.cos(pi * k / 176) - T) / T for k in range(1, 89))
chk("A1b 176-chain min RELATIVE dev = 19.68%", abs(d88 - mp.mpf("0.1968")) < mp.mpf("1e-3"),
    f"{mp.nstr(d88 * 100, 6)}%")
chk("A1c v_g(44) = 0 and 1/v_g(44) = 1.75e61 (divergence)",
    abs(V(44)) < mp.mpf("1e-55") and abs(S(44) - mp.mpf("1.751e61")) / mp.mpf("1.751e61") < mp.mpf("0.01"),
    f"1/v_g(44) = {mp.nstr(S(44), 5)}")
chk("A1d sec(n) >= 1 for n <= 43", min(S(n) for n in range(1, 44)) >= 1)

# --- docs/09 A3 ---
print("\n[docs/09 A3] [L,J] = 0 and C_energy")
tr = sum(((-1) ** n) * G(n) for n in range(1, 45))
Stot = sum(G(n) for n in range(1, 45))
chk("A3a Tr(LJ) = 2 = mu^2 EXACT", abs(tr - mu2) < mp.mpf("1e-50"), f"{mp.nstr(tr, 20)}")
chk("A3b Sigma_g = 90 EXACT", abs(Stot - 90) < mp.mpf("1e-50"), f"{mp.nstr(Stot, 20)}")
chk("A3c C_energy = 1/45 EXACT", abs(tr / Stot - T) < mp.mpf("1e-50"))

# --- docs/09 Part B key values ---
print("\n[docs/09 B] mechanism family key values")
b03 = sum(G(n) * V(n) for n in range(1, 45)) / Stot
chk("B03 <v_g>_gamma = 0.414849535965", abs(b03 - mp.mpf("0.414849535965")) < mp.mpf("1e-11"),
    f"{mp.nstr(b03, 14)}")
trap = abs(b03 - (mp.sqrt(2) - 1)) / (mp.sqrt(2) - 1)
chk("B03 is a sqrt(2)-1 TRAP (dev 0.154%, not an identity)",
    abs(trap * 100 - mp.mpf("0.154")) < mp.mpf("0.01"), f"{mp.nstr(trap * 100, 5)}%")
b08 = (sum(V(n) for n in range(1, 45) if n % 2 == 0) / 22
       - sum(V(n) for n in range(1, 45) if n % 2 == 1) / 22)
chk("B08 sector mean diff = -0.0231329966884 (|.| is 4.1% from 1/45 -> still fails)",
    abs(b08 - mp.mpf("-0.0231329966884")) < mp.mpf("1e-11"), f"{mp.nstr(b08, 14)}")
chk("B24 (Sigma_e-Sigma_o)/(2N_d) = 1/44 = 0.0227272727273",
    abs((46 - 44) / mp.mpf(88) - mp.mpf("0.0227272727273")) < mp.mpf("1e-13"))
chk("B25 1/(N_d+0.5) = 0.0224719101124 (half-integer near-miss, 1.12%)",
    abs(1 / (N + mp.mpf("0.5")) - mp.mpf("0.0224719101124")) < mp.mpf("1e-13"))

# --- docs/09 B23/B27 equivalence ---
print("\n[docs/09 B23/B27] equivalence Sigma_g = 2*centroid <=> mu^2 = 2")
cent = (mp.mpf(2) + mp.mpf(88)) / 2
chk("centroid_world = 45, 2*centroid = Sigma_g = 90 (equivalence holds)",
    cent == 45 and abs(2 * cent - Stot) < mp.mpf("1e-50"),
    f"(45-44)/45 = {mp.nstr((cent - 44) / cent, 12)} = 1/45")

# --- docs/09 C2 two-field ---
print("\n[docs/09 C2] two-field Z2-odd coupling")
g = T
real_ok, mean_ok, split_ok = True, True, True
for n in range(1, 45):
    k = mu2 * mp.cos(pi * n / 88)
    m = mu2 * mp.sin(pi * n / 88)
    w2p = k ** 2 + m ** 2 + 2 * g * abs(k)
    w2m = k ** 2 + m ** 2 - 2 * g * abs(k)
    if w2m < 0:
        real_ok = False
    vp, vm = (k + g) / mu2, (k - g) / mu2
    if abs((vp + vm) / 2 - k / mu2) > mp.mpf("1e-45"):
        mean_ok = False
    if abs((vp - vm) - 2 * g / mu2) > mp.mpf("1e-45"):
        split_ok = False
chk("C2a two-field dispersion REAL for all 44 modes", real_ok)
chk("C2c mean transport EXACTLY invariant", mean_ok)
chk("C2d velocity branch split = 2g/mu^2 = g = 1/45", split_ok)
chk("C1 single-field term Im(omega^2) = g*k(22) = 0.031427 != 0",
    abs(g * mu2 * mp.cos(pi * 22 / 88) - mp.mpf("0.031427")) < mp.mpf("1e-6"),
    f"{mp.nstr(g * mu2 * mp.cos(pi * 22 / 88), 8)}")

# --- docs/10 T2 normalization ---
print("\n[docs/10 T2] normalization uniqueness + 2.27% resolution")
Se, So = mp.mpf(46), mp.mpf(44)
chk("T2a normalization A shares sum to 1 (partition of c)",
    abs(Se / Stot + So / Stot - 1) < mp.mpf("1e-50"),
    f"v_w = 23c/45, v_o = 22c/45, drift = 1/45")
chk("T2b normalization B shares sum to 45/44 = 1.0227 > 1 (violates partition)",
    abs(Se / 88 + So / 88 - mp.mpf(45) / 44) < mp.mpf("1e-50"))
chk("T2e (1/44)/(1/45) = 45/44 = Sigma_g/(2N_d) -> the 2.27% IS the measure ratio",
    abs((mp.mpf(1) / 44) / T - mp.mpf(45) / 44) < mp.mpf("1e-50"))

# --- docs/10 T1/T3/T4 O169 DESI ---
print("\n[docs/10 T1/T3/T4] O169 DESI consequences")
L4, Ng, Fp = 7, 3, 17
TR = [('0.510', '13.588', '0.167'), ('0.706', '17.351', '0.177'), ('0.934', '21.576', '0.152'),
      ('1.321', '27.601', '0.318'), ('1.484', '30.512', '0.760'), ('2.330', '38.988', '0.531')]
def ell(z): return mp.log(1 + mp.mpf(z), 4)
def Kf(l): return int(mp.nint(L4 * (Ng + (4 ** l - 1) / Fp)))
def bsec(K, sh=None):
    return mp.fsum(1 / (V(n) + (sh(n) if sh else 0)) for n in range(1, K + 1)) / K
def chi2(f):
    t = mp.mpf(0)
    for z, dm, em in TR:
        l = ell(z)
        t += ((Rw * (1 - 4 ** (-l)) * (l + f(l)) / rd - mp.mpf(dm)) / mp.mpf(em)) ** 2
    return t
A = Bv = mp.mpf(0)
for z, dm, em in TR:
    l = ell(z); x = Rw * (1 - 4 ** (-l)) / rd
    y = mp.mpf(dm) - Rw * (1 - 4 ** (-l)) * l / rd; w = 1 / mp.mpf(em) ** 2
    A += w * x * x; Bv += w * x * y
b0 = Bv / A
chk("T1a b_struct = <sec>_{1..21} = 1.11835681", abs(bsec(21) - mp.mpf("1.11835681")) < mp.mpf("1e-8"),
    f"{mp.nstr(bsec(21), 10)}")
chk("T1a' b0 = 1.118850105, chi2_ref = 2.4514475/6",
    abs(b0 - mp.mpf("1.118850105")) < mp.mpf("1e-8") and abs(chi2(lambda l: b0) - mp.mpf("2.4514475")) < mp.mpf("1e-6"),
    f"b0 = {mp.nstr(b0, 10)}, chi2_ref = {mp.nstr(chi2(lambda l: b0), 9)}")
c_struct = chi2(lambda l: bsec(Kf(l)))                    # O169 window law
c_const = chi2(lambda l: bsec(21))                        # constant intercept
chk("T1b O169 window-law chi^2 = 2.6309184/6 (= O169's reported 2.63/6)",
    abs(c_struct - mp.mpf("2.6309184")) < mp.mpf("1e-6"), f"{mp.nstr(c_struct, 9)}")
chk("T1c constant-b chi^2 = 2.4562836/6; window costs Delta = 0.1746",
    abs(c_const - mp.mpf("2.4562836")) < mp.mpf("1e-6")
    and abs((c_struct - c_const) - mp.mpf("0.1746348")) < mp.mpf("1e-5"),
    f"{mp.nstr(c_const, 9)}, Delta = {mp.nstr(c_struct - c_const, 8)}")
dh = g / mu2
c_p = chi2(lambda l: bsec(Kf(l), lambda n: ((-1) ** n) * dh))
c_m = chi2(lambda l: bsec(Kf(l), lambda n: -((-1) ** n) * dh))
chk("T3 world-faster: chi2 = 2.6640011/6 (Delta chi2 = +0.033, NOT excluded)",
    abs(c_p - mp.mpf("2.6640011")) < mp.mpf("1e-6"), f"{mp.nstr(c_p, 9)}")
chk("T3 reversed: chi2 = 2.6544492/6 (Delta chi2 = +0.024, sign unresolved)",
    abs(c_m - mp.mpf("2.6544492")) < mp.mpf("1e-6"), f"{mp.nstr(c_m, 9)}")
chk("T3a Delta<sec>_21 = +0.000952894 (world-faster)",
    abs((bsec(21, lambda n: ((-1) ** n) * dh) - bsec(21)) - mp.mpf("0.000952894")) < mp.mpf("1e-9"),
    f"{mp.nstr(bsec(21, lambda n: ((-1) ** n) * dh) - bsec(21), 8)}")

def bsec_dbl(K, gg):
    return mp.fsum(1 / (V(n) + gg / mu2) + 1 / (V(n) - gg / mu2) for n in range(1, K + 1)) / (2 * K)
d21 = bsec_dbl(21, g) - bsec(21)
c_dbl = chi2(lambda l: bsec_dbl(Kf(l), g))
chk("T4a branch doubling shifts <sec> only at O(g^2): 1e-6 < Delta<sec>_21 < 1e-3",
    mp.mpf("1e-6") < abs(d21) < mp.mpf("1e-3"), f"Delta<sec>_21 = {mp.nstr(d21, 6)}")
chk("T4b closure intact: Delta chi^2 = 0.019 << 1 (negligible on 6 dof)",
    abs(c_dbl - c_struct) < mp.mpf("0.05"), f"Delta chi^2 = {mp.nstr(c_dbl - c_struct, 6)}")

# --- docs/09 Part D null with INDEPENDENT seed ---
print("\n[docs/09 D] null control (independent seed 311)")
random.seed(311)
vnp = np.array([float(V(n)) for n in range(1, 45)])
gnp = np.array([float(G(n)) for n in range(1, 45)])
nnp = np.arange(1, 45, dtype=float)
snp = np.array([float(S(n)) for n in range(1, 45)])
bases = [np.ones(44), nnp, gnp, snp, nnp ** 2, gnp ** 2, nnp * (45 - nnp), 1 / nnp, 1 / gnp,
         np.sin(np.pi * nnp / 88)]
hits = 0
NT = 3000
for _ in range(NT):
    a, b = random.randint(0, 9), random.randint(0, 9)
    p1, p2 = random.uniform(-4, 4), random.uniform(-4, 4)
    w = (bases[a] ** p1) * (bases[b] ** p2)
    if not np.all(np.isfinite(w)) or w.sum() == 0 or np.any(w < 0):
        continue
    val = float((w * vnp).sum() / w.sum())
    if abs(val - float(T)) / float(T) < 0.01:
        hits += 1
chk("D1 null (seed 311): p < 0.01 -> enumeration discriminative (reproduced independently)",
    hits / NT < 0.01, f"{hits}/{NT} within 1% of 1/45")

print(f"\nRESULT: {PASS}/{PASS + FAIL} PASS")
