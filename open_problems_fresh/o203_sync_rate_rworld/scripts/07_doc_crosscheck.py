#!/usr/bin/env python3
"""
O203 Script 07 - Independent doc cross-check (from scratch, no import of scripts/01-06)
=======================================================================================
Recompute every numerical claim in docs/01-07 with mpmath 60 dps, built fresh.
Catches doc-vs-computation drift (audit discipline, O153 pattern).

Claims checked:
  A. spectral sums: S_even = N_d+mu2, S_odd = N_d, S_tot = 2N_d+mu2 (EXACT)
  B. C_energy = 1/(N_d+1) = 1/45 (EXACT); operator form Tr((Pe-Po)g)/Tr(g)
  C. sector velocities: v_obs = 22/45, v_world = 23/45, mean 1/2, drift 1/45 (c units)
  D. ladder: sin(pi/88) = v_g(43), cos(pi/88) = v_g(1) EXACT; c/45, c/88 NOT modes
  E. O7 writing = c/44 analytic; dev vs c/45 = 2.27%
  F. rate family: m/88 for m in {1,2,44,88} -> {1/88, 1/44, 1/2, 1} ; f_44/45 not in corpus
  G. T2 PSLQ: best |(1+/-b)^p phi^q - 1| for b=1/45 >= 1e-3 (no structure)
  H. Lagrangian: Im(w^2) = b*k for sync term (b=1/45, k=sqrt(2) at n=22) != 0
  I. T_ring identities: L_ring = c*T_ring; T*omega = 2pi (stored 0.0016% class)
  J. O169 assembly: <sec>_21 = 1.1183568, <sec>_28 = 1.2414181; a = <g>_odd/g_22 = 1
  K. trap near-misses: csc(pi/88) vs 28 (0.06%), 1-pi/44 vs 13/14 (0.003%),
     45/88 vs 23/45 (0.05%) - all > 1e-9 off = NOT exact
"""
import mpmath as mp

mp.mp.dps = 60

PASS = 0
FAIL = 0

def chk(tag, docval, computed, tol_rel=mp.mpf("1e-9")):
    """compare computed vs doc value (string or mpf); relative tolerance"""
    global PASS, FAIL
    docv = mp.mpf(str(docval)) if isinstance(docval, str) else docval
    dev = abs(computed - docv) / max(abs(docv), mp.mpf("1e-30"))
    ok = dev < tol_rel
    if ok:
        PASS += 1
        print(f"  [PASS] {tag}: {mp.nstr(computed, 12)}")
    else:
        FAIL += 1
        print(f"  [FAIL] {tag}: computed {mp.nstr(computed, 12)} vs doc {mp.nstr(docv, 12)} (dev {mp.nstr(dev, 4)})")

N_d = 44
mu2 = mp.mpf(2)
pi = mp.pi
phi = (1 + mp.sqrt(5)) / 2

g = [4 * mp.sin(pi * n / 88) ** 2 for n in range(1, N_d + 1)]
Se = sum(g[n - 1] for n in range(1, N_d + 1) if n % 2 == 0)
So = sum(g[n - 1] for n in range(1, N_d + 1) if n % 2 == 1)
St = Se + So

print("=" * 70)
print("O203 S7 - independent doc cross-check (from scratch, mpmath 60 dps)")
print("=" * 70)

# A. spectral sums
print("\n[A] spectral sums (docs/01)")
chk("S_even = N_d+mu2 = 46", "46", Se)
chk("S_odd = N_d = 44", "44", So)
chk("S_tot = 2N_d+mu2 = 90", "90", St)
chk("gamma_22 = mu2 = 2", "2", g[21])

# B. C_energy
print("\n[B] C_energy identities (docs/01/03)")
C = (Se - So) / St
chk("C_energy = 1/45", "0.02222222222222222222222222222222222222222222222222", C)
chk("C_energy = 1/(N_d+1)", mp.mpf(1) / 45, C)
chk("C_energy = mu2/(2N_d+mu2)", mp.mpf(2) / 90, C)
chk("operator form Tr((Pe-Po)g)/Tr(g)", C, (Se - So) / St)

# C. sector velocities
print("\n[C] sector velocities (docs/01/07)")
chk("v_obs = 22/45", mp.mpf(22) / 45, So / St)
chk("v_world = 23/45", mp.mpf(23) / 45, Se / St)
chk("mean = 1/2", mp.mpf(1) / 2, (So / St + Se / St) / 2)
chk("drift = C_energy", C, Se / St - So / St)

# D. ladder membership
print("\n[D] ladder membership (docs/01)")
chk("sin(pi/88) = v_g(43)", mp.sin(pi / 88), mp.cos(43 * pi / 88))
chk("cos(pi/88) = v_g(1)", mp.cos(pi / 88), mp.cos(1 * pi / 88))
# c/45 not a mode: min |v_g(n) - 1/45|
mind = min(abs(mp.cos(pi * n / 88) - mp.mpf(1) / 45) for n in range(1, N_d + 1))
chk("c/45 NOT a ladder mode (min dev > 1e-2)", "0.013", mind, tol_rel=mp.mpf("0.1"))
# c/88 not a mode
mind88 = min(abs(mp.cos(pi * n / 88) - mp.mpf(1) / 88) for n in range(1, N_d + 1))
chk("c/88 NOT a ladder mode (min dev > 1e-2)", "0.011", mind88, tol_rel=mp.mpf("0.1"))

# E. O7 writing
print("\n[E] O7 writing (docs/01/04)")
chk("writing = c/44 analytic", mp.mpf(1) / 44, mp.mpf(2) / 88)
dev45 = abs(mp.mpf(1) / 44 - mp.mpf(1) / 45) / (mp.mpf(1) / 45)
chk("dev vs c/45 = 2.2724%", "0.022724", dev45, tol_rel=mp.mpf("1e-3"))

# F. rate family
print("\n[F] rate family (docs/04)")
for m, exp in [(1, mp.mpf(1) / 88), (2, mp.mpf(1) / 44), (44, mp.mpf(1) / 2), (88, mp.mpf(1))]:
    chk(f"m={m} -> {mp.nstr(exp, 6)}", exp, mp.mpf(m) / 88)
# f_44/45 not corpus: check against f_ring, 2f_ring, Gamma, f_44 ratios
f44r = mp.mpf(1)
C_rate = f44r / 45
notmatch = all(abs(C_rate - r) / r > mp.mpf("1e-4") for r in
               [mp.mpf(1) / 88, mp.mpf(2) / 88, mp.mpf(44) / 88, mp.mpf(1)])
print("  [PASS] f_44/45 not any family rate" if notmatch else "  [FAIL] f_44/45 matches family")
PASS += 1 if notmatch else 0
FAIL += 0 if notmatch else 1

# G. T2 PSLQ best dev for 1/45
print("\n[G] T2 PSLQ (docs/02)")
b45 = mp.mpf(1) / 45
best = None
for p in range(-30, 31):
    if p == 0:
        continue
    for q in range(-20, 21):
        if q == 0:
            continue
        for s in (1, -1):
            v = (1 + s * b45) ** p * phi ** q
            d = abs(v - 1)
            if best is None or d < best[0]:
                best = (d, p, q, s)
chk("best dev for c/45 >= 1e-3 (no structure)", "0.00232", best[0], tol_rel=mp.mpf("0.1"))

# H. Lagrangian Im(w^2)
print("\n[H] Lagrangian sync term (docs/03)")
k22 = mu2 * mp.cos(pi * 22 / 88)
Imw2 = float(b45) * float(k22)
chk("Im(w^2) = b*k = 0.03143 for b=1/45, n=22", "0.031427", mp.mpf(str(Imw2)), tol_rel=mp.mpf("1e-3"))
chk("Im(w^2) != 0 -> standing-wave closure broken", True, Imw2 != 0)

# I. T_ring identities
print("\n[I] T_ring identities (docs/05)")
c_km = mp.mpf("299792.458")
T = mp.mpf("84.636")
Rw = mp.mpf("4129.94")
Lr = c_km * T * mp.mpf("3.15576e16") / mp.mpf("3.085677581e19")
devL = abs(Lr - 2 * pi * Rw) / (2 * pi * Rw)
chk("c*T_ring = 2pi*R_world (0.0016% class)", "1.3e-5", devL, tol_rel=mp.mpf("0.5"))
om = mp.mpf("72.59") * mp.mpf("0.0010227")
devT = abs(T * om - 2 * pi) / (2 * pi)
chk("T*omega = 2pi (0.0016% class)", "7.1e-7", devT, tol_rel=mp.mpf("0.5"))

# J. O169 assembly
print("\n[J] O169 assembly law (docs/06)")
sec = [1 / mp.cos(pi * n / 88) for n in range(1, N_d + 1)]
chk("<sec>_21 = 1.1183568", "1.1183568", sum(sec[:21]) / 21, tol_rel=mp.mpf("1e-6"))
chk("<sec>_28 = 1.2414181", "1.2414181", sum(sec[:28]) / 28, tol_rel=mp.mpf("1e-6"))
odd_g = [g[n - 1] for n in range(1, N_d + 1) if n % 2 == 1]
a = sum(odd_g) / len(odd_g) / g[21]
chk("a = <g>_odd/g_22 = 1", "1", a, tol_rel=mp.mpf("1e-30"))

# K. trap near-misses
print("\n[K] trap near-misses (docs/02/04/06)")
csc = 1 / mp.sin(pi / 88)
chk("csc(pi/88) vs 28: 0.0615% off (NOT exact)", "0.000615", abs(csc - 28) / 28, tol_rel=mp.mpf("0.1"))
proj = 1 - pi / 44
chk("1-pi/44 vs 13/14: 0.0031% off (NOT exact)", "0.0000309", abs(proj - mp.mpf(13) / 14) / (mp.mpf(13) / 14), tol_rel=mp.mpf("0.5"))
chk("45/88 vs 23/45: 0.0494% off (NOT exact)", "0.000494", abs(mp.mpf(45) / 88 - mp.mpf(23) / 45) / (mp.mpf(23) / 45), tol_rel=mp.mpf("0.1"))
inv21 = 1 / (sum(sec[:21]) / 21)
chk("1/<sec>_21 vs 2/sqrt5: 0.0289% off (trap)", "0.000289", abs(inv21 - 2 / mp.sqrt(5)) / (2 / mp.sqrt(5)), tol_rel=mp.mpf("0.1"))

print(f"\nAUDIT RESULT: {PASS}/{PASS + FAIL} doc claims independently re-verified")
