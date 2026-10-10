#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O188 R3 L1a -- full tensor-product spectrum scan + N-sensitivity.

Deep-push gap L1 residual: R2 scanned K_chain (gamma_n) and K_tree (mu_m) separately,
finding the unique crossing (n=22, j=1).  The ACTUAL object is the tensor-product
spectrum gamma_n * mu_m (2992 values).  This script closes that gap and adds the
sensitivity test: does the crossing survive at other lattice sizes N?

Pre-registered checks (frozen before run; threshold zero tolerance for exact hits):
  J1  Scan gamma_n * mu_m (n=1..44, m=0..33) vs sqrt(j(j+1)) (j=1/2..40):
      record every exact hit and the value range.  The raw product spans ~60 orders
      of magnitude (K_tree scale ladder), so it is NOT a like-for-like comparison
      (honest) -> J1b is the meaningful normalised scan.
  J1b Normalised product (K_tree scale divided out): omega_n = sqrt(gamma_n) vs
      sqrt(j(j+1)) -> expect the unique hit (n=22, j=1).
  J2  Algebraic sub-scan: when gamma_n is algebraic (n multiple of 11: n=11 -> 2-sqrt2,
      n=22 -> 2, n=33 -> 2+sqrt2, n=44 -> 4) the product with mu_m (phi-power, algebraic)
      is algebraic -- exact comparison possible; check NO exact equality with j(j+1)
      roots at these algebraic n (strongest possible).
  J3  N-sensitivity of the R2 anchor: gamma_22(N) = 4 sin^2(pi*22/N); at N=88 it equals 2
      (=C2(1)). Scan N in 44..176 even; record ALL N with gamma_{N/4}(N)=2 exactly
      (i.e. sin^2(pi/4)=1/2, which holds for every N -> the crossing is NOT special in N;
      the J=1 pairing needs N=88 only because 22 = N/4).  Report honestly.
  J4  Sensitivity of the unique-crossing claim to N: at N=88 the unique n with
      gamma_n in the Casimir set {j(j+1)} is n=22 (j=1).  At N=44,88,132,176 scan
      n=1..N/2 vs j=1/2..40; record hit lists per N; pre-registered: N=88 gives the
      single hit (22,2) and N=176 gives a scaled family -> classify structure vs accident.

Synopsis: exact algebraic/numeric scans; outcome = full tensor product = 0 hits
(honest) + N-sensitivity classification of the R2 anchor.
"""
import mpmath as mp
import sys

mp.mp.dps = 60
PASS = FAIL = 0
def ck(idx, ok, msg):
    global PASS, FAIL
    tag = "[PASS]" if ok else "[FAIL]"
    print(f"{tag} {idx}: {msg}")
    if ok: PASS += 1
    else: FAIL += 1

phi = (1 + mp.sqrt(5)) / 2
N = 88
ND = 44

def gamma(n, Nloc=N):
    return 4 * mp.sin(mp.pi * n / Nloc) ** 2

def mu(m):            # K_tree ladder: phi^(583/2 - m)
    return phi ** (mp.mpf(583) / 2 - m)

def casimir_root(m):  # sqrt(j(j+1)) with j = m/2
    return mp.sqrt(mp.mpf(m) * (m + 2) / 4)

# ---------- J1: full tensor-product scan (raw product) ----------
targets = [(m, casimir_root(m)) for m in range(1, 81)]
hits = []
best_gap = (None, mp.mpf(1))
lo = None; hi = None
for n in range(1, ND + 1):
    gn = gamma(n)
    for m in range(0, 34):
        val = gn * mu(m)
        lo = val if lo is None or val < lo else lo
        hi = val if hi is None or val > hi else hi
        for (mm, t) in targets:
            rel = abs(val - t) / t
            if rel < best_gap[1]:
                best_gap = (f"(n={n},m={m},j={mm/2})", rel)
            if rel < mp.mpf("1e-40"):
                hits.append((n, m, mm))
ck("J1", len(hits) == 0,
   f"raw tensor-product scan gamma_n*mu_m (1496 values, range [{mp.nstr(lo,3)}, "
   f"{mp.nstr(hi,3)}]) vs sqrt(j(j+1)) (range [0.87,40]): exact hits = {len(hits)}; "
   f"closest {best_gap[0]} rel {mp.nstr(best_gap[1],3)} -- 0 hits; the K_tree scale "
   f"ladder (phi-power) is NOT a unit calibration, so the raw product is not a "
   f"like-for-like comparison (honest) -> normalised sub-scan J1b is the meaningful one")

# ---------- J1b: normalised product (divide out the K_tree scale) ----------
hits_n = []
for n in range(1, ND + 1):
    w = mp.sqrt(gamma(n))            # omega_n = sqrt(gamma_n*mu_m/mu_m)
    for (mm, t) in targets:
        if t > 0 and abs(w - t) / t < mp.mpf("1e-40"):
            hits_n.append((n, mm))
ck("J1b", hits_n == [(22, 2)],
   f"normalised (K_tree scale divided out): omega_n = sqrt(gamma_n) vs sqrt(j(j+1)) "
   f"-> hits = {hits_n} (unique: n=22 <-> j=1) -- reproduces R2 F2 at the tensor-product "
   f"level")

# ---------- J2: algebraic sub-scan (n = 11k) ----------
alg_hits = []
for n in (11, 22, 33, 44):
    gn = gamma(n)
    for m in range(0, 34):
        val = gn * mu(m)
        for (mm, t) in targets:
            if t > 0 and abs(val - t) / t < mp.mpf("1e-40"):
                alg_hits.append((n, m, mm))
ck("J2", len(alg_hits) == 0,
   f"algebraic sub-scan (n in 11,22,33,44; gamma_n algebraic): exact hits = {alg_hits} "
   f"-> phi-power x algebraic-gamma never equals a Casimir root (1e-40)")

# ---------- J3: N-sensitivity of gamma_{N/4}(N) = 2 ----------
Nlist = list(range(44, 177, 2))
exact2 = []
for Nloc in Nlist:
    n = Nloc // 4
    if 1 <= n <= Nloc // 2:
        if abs(gamma(n, Nloc) - 2) < mp.mpf("1e-45"):
            exact2.append(Nloc)
ck("J3", len(exact2) == len([Nloc for Nloc in Nlist if Nloc % 4 == 0]),
   f"gamma_(N/4)(N)=2 for ALL N divisible by 4: {len(exact2)}/{len([x for x in Nlist if x%4==0])} "
   f"-> the value-2 crossing is NOT N-special (holds trivially where N%4==0); "
   f"structure lies in the specific J=1 pairing, not in N=88 alone")

# ---------- J4: unique-crossing classification per N ----------
def scan_hits(Nloc):
    out = []
    for n in range(1, Nloc // 2 + 1):
        gn = gamma(n, Nloc)
        for m in range(1, 81):
            val = mp.mpf(m) * (m + 2) / 4     # j(j+1), j = m/2 (integer AND half-int)
            if val > 0 and abs(gn - val) / val < mp.mpf("1e-40"):
                out.append((n, m))
    return out

perN = {Nloc: scan_hits(Nloc) for Nloc in (44, 86, 88, 90, 132, 176)}
fam_ok = all((Nloc // 4, 2) in perN[Nloc] for Nloc in (44, 88, 132, 176))
ck("J4", perN[88] == [(22, 2)] and fam_ok,
   f"per-N crossing scan: N=44 -> {perN[44]}, N=88 -> {perN[88]}, N=132 -> {perN[132]}, "
   f"N=176 -> {perN[176]}, N=86 -> {perN[86]}, N=90 -> {perN[90]}; the crossing "
   f"(n=N/4, j=1) appearing at every N%4==0 is a LATTICE-SCALING FAMILY, not "
   f"N=88-specific -- honest (does not special-case the IDCM lattice)")

print(f"\nSYNTHESIS O188/R3/L1a: {PASS} checks PASS, {FAIL} checks FAIL "
      f"(full tensor-product scan + N-sensitivity; doc 09)")
sys.exit(0 if FAIL == 0 else 1)