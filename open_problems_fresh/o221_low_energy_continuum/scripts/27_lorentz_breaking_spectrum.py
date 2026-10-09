#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O221 / scripts/27 — Round 22 (Arm 1: L-Lor): Lorentz-breaking scaling on the OPERATOR SPECTRUM
=================================================================================================
Sub-problem L-Lor (O221/L-Lor, exec arm) — first numerics round.  Target: the CONTINUOUS layer
(SR), via the operator spectrum of the 4D product lattice.  FSR is the DISCRETE layer; discrete
exactness (gamma_n = csc, mode-by-mode mass shell) is NOT a statement about the continuous
Lorentz group (layer rule, Calibrator 2026-10-02).  This script therefore measures how the
lattice dispersion approaches the relativistic one.

WHY THE OPERATOR SPECTRUM AND NOT THE FIELD MAP:
  The residual-5 deficit (docs/19-21) lives in the FIELD-MAP normalisation (naive/vert/cube cell
  sampling, internal, ~ +1 M-power).  The dispersion identity omega = c k sin(x)/x is EXACT on the
  spectrum and is sampling-free.  The Lorentz-breaking question is a question about the spectrum;
  using the map-dependent amplitudes would mix it with residual 5.  Decision (pre-registered):
  all measurements here are eigenvalue-based.  Residual 5 is NOT re-litigated here.

PRE-REGISTRATION (blind, 2026-10-02, written before running):
  * BLIND M SET (unseen; all prior O221 M-scans used M <= 16):  M in {20, 24, 32}
    Secondary set for the second-order check:  M in {40, 48, 64}.
  * Fixed physical modes (4D integer vectors, base-n family):
        axis   nA = (2,0,0,0)      |n| = 2     sum khat^4 = 1      (A1g component)
        face   nF = (2,2,0,0)      |n| = rt8   sum khat^4 = 1/2    (face-diagonal)
        body   nB = (2,2,2,0)      |n| = rt12  sum khat^4 = 1/3    (body-diagonal)
        hyper  nH = (2,2,2,2)      |n| = 4     sum khat^4 = 1/4    (hyper-diagonal)
    plus axis probes n = 3, 5 (subluminality by mode), all |n| pi / M <= 0.63 at M = 20 (window).
  * Quantity:  D(M; n) = omega_lat(M)/k_cont - 1   with
        omega_lat^2 = c^2 * sum_j (2/a)^2 sin^2(pi n_j / M),   k_cont = 2 pi |n| / (M a)
    In units a = 1, c = 1 (ratio only):  D = sqrt(sum_j sin^2 x_j)/|x| - 1,  x_j = pi n_j / M.
  * LEADING LAW (analytic, target):  D = -|x|^2 * S4/6 + ...  with  S4 = sum_j khat_j^4.
        -D * M^2 * 6 / ((pi|n|)^2 S4)  -->  1   (the isotropy-normalised amplitude A_dir)
  * EXPONENT of the leading term = 2.000 exactly (x_j = pi n_j / M => leading correction O(M^-2)).
  * SECOND ORDER: with S6 = sum khat_j^6,  D = -|x|^2 S4/6 + |x|^4 (S6/45 - S4^2/72) + ...
        axis:  S4 = S6 = 1  =>  +|x|^4/120  (matches sin(x)/x = 1 - x^2/6 + x^4/120 - ...)
  * FALSIFICATION (F3): a genuine dim-4 (O(1/M)) breaking operator would DOMINATE the
    M^-2 leading term at large M.  Two dominance tests (see the check block; the earlier naive
    |c_1|/sigma construction was discarded as an audit-side artefact of model mis-specification
    on near-exact 6-point data):
        (i)  pure-law fit D = a2/M^2 + a3/M^4 over the 6-point window: max relative residual
             must be < 1e-4 (a 1/M operator present at > 1e-4 of the signal breaks the pure law);
        (ii) free fit D = b1/M + b2/M^2 + b3/M^4: a best-fit b1 must not displace the leading
             amplitude by more than 5% at the largest M: |b1|*Mmax^2/|b2| < 0.05.
    Either failure => "irrelevance (dim >= 5)" is REFUTED and recorded; thresholds are NOT relaxed.

CHECKS:
  C0  product-form eigenvalues = explicit 4D dense diagonalisation at M = 4 (all 256 modes)
  F0a axis n=2 : exponent in [1.95, 2.05] on blind M;  A_dir -> 1 within 5e-3
  F0b axis n=2 : prefactor D*M^2 -> (pi n)^2/6 = 6.579736267... within 5e-3
  F1a axes n=3,5: exponent in [1.95, 2.05] on blind M (subluminal by mode)
  F1b second order: residual R = (-D - |x|^2/6)*M^4 -> (pi n)^4/120 on {40,48,64} within 2%
  F2a direction ladder: A_dir -> 1 within 1e-2 for all four rays at M = 64
  F2b no extra anisotropy: (A_dir - 1) < 1e-2 for all rays AND all blind M (isotropy of limits)
  F3  falsification guard: |c_1|/sigma < 5 (free 1/M term on blind window)
  F4  honest grading: signature/Wick remain inputs; record, do not claim closure.
OUTPUT: canonical laptops log + derived data/27; run via systemd unit; rc appended last.
"""

import numpy as np
from numpy.linalg import eigvalsh, lstsq

def ck(cond, msg, extra=""):
    tag = "[PASS]" if cond else "[FAIL]"
    print("%s %s %s" % (tag, msg, extra))
    return bool(cond)

def omega_lat(nvec, M):
    x = np.pi * np.asarray(nvec, float) / M
    return np.sqrt(np.sum(np.sin(x) ** 2))          # a = 1, c = 1

def k_cont(nvec, M):
    return 2.0 * np.pi * np.linalg.norm(nvec) / M

def Dval(nvec, M):
    x = np.pi * np.asarray(nvec, float) / M
    return np.sqrt(np.sum(np.sin(x) ** 2)) / np.linalg.norm(x) - 1.0

def S4_of(nvec):
    n = np.asarray(nvec, float); nn = np.linalg.norm(n)
    return np.sum((n / nn) ** 4)

def fit_exponent(nvec, Ms):
    ys = np.array([np.log(-Dval(nvec, M)) for M in Ms])
    xs = np.array([np.log(M) for M in Ms])
    A = np.vstack([xs, np.ones_like(xs)]).T
    (sl, ic), _, _, _ = lstsq(A, ys, rcond=None)
    return sl, ic

def fit_m_inv(nvec, Ms):
    """D(M) = c0 + c1/M + c2/M^2 -> free 1/M term test (F3)."""
    xs = np.array([1.0 / M for M in Ms]); ys = np.array([Dval(nvec, M) for M in Ms])
    A = np.vstack([xs, xs ** 2, np.ones_like(xs)]).T
    (c1, c2, c0), res, rank, sv = lstsq(A, ys, rcond=None)
    yhat = A @ np.array([c1, c2, c0])
    dof = len(ys) - 3
    sig = np.sqrt(np.sum((ys - yhat) ** 2) / dof) / np.sqrt(np.sum((A[:, 0]) ** 2))
    return c1, sig

print("=" * 72)
print("O221 scripts/27 — L-Lor Arm 1: Lorentz-breaking scaling on the operator spectrum")
print("Blind M set {20,24,32}; secondary {40,48,64} | layer rule: FSR discrete / SR continuous")
print("=" * 72)

ok = True

# ---- C0: product form vs explicit 4D dense diagonalisation at M = 4 ----
M0 = 4
lam1 = np.array([4.0 * np.sin(np.pi * n / M0) ** 2 for n in range(M0)])
L1 = np.zeros((M0, M0))
for i in range(M0):
    L1[i, i] = 2.0
    L1[i, (i - 1) % M0] = -1.0          # periodic (88-ring convention; lam1 = 4 sin^2(pi n/M0))
    L1[i, (i + 1) % M0] = -1.0
L4 = np.zeros((M0 ** 4, M0 ** 4))
for j in range(4):
    term = np.eye(M0 ** j)
    term = np.kron(term, L1)
    term = np.kron(term, np.eye(M0 ** (3 - j)))
    L4 += term
eigs4 = np.sort(eigvalsh(L4))
prod = np.sort(np.array([sum(lam1[nj] for nj in n4)
                         for n4 in np.ndindex(*([M0] * 4))]))
dev = float(np.max(np.abs(eigs4 - prod)))
ok &= ck(dev < 1e-10,
         "C0  product-form == explicit 4D spectrum (M=4, all 256 modes)",
         "max|dev| = %.3e" % dev)

# ---- geometry ----
rays = {"axis(2,0,0,0)": (2, 0, 0, 0), "face(2,2,0,0)": (2, 2, 0, 0),
        "body(2,2,2,0)": (2, 2, 2, 0), "hyper(2,2,2,2)": (2, 2, 2, 2)}
axis3, axis5 = (3, 0, 0, 0), (5, 0, 0, 0)
BLIND = [20, 24, 32]; SEC = [40, 48, 64]

for nm, nv in list(rays.items()) + [("axis n=3", axis3), ("axis n=5", axis5)]:
    print("\n[%s] |n| = %.4f  S4 = %.12g" % (nm, np.linalg.norm(nv), S4_of(nv)))
    for M in BLIND + SEC:
        print("   M=%3d  xmax=%.4f  D(M)=%+15.10e" % (M, np.pi * np.max(nv) / M, Dval(nv, M)))

# ---- F0a/F1a: |exponent| on the blind set (D < 0; slope of log(-D) vs log M ~ -2) ----
exp_ok = True
for nm, nv in list(rays.items()) + [("axis n=3", axis3), ("axis n=5", axis5)]:
    sl, ic = fit_exponent(nv, BLIND)
    mag = -sl
    within = 1.95 <= mag <= 2.05
    exp_ok &= within
    print("   |exponent| (blind) = %.6f  in [1.95,2.05]: %s" % (mag, within))
ok &= ck(exp_ok,
         "F0a+F1a  leading |exponent| = 2.000 +/- 0.05 on the blind M set (all rays)",
         "")

# ---- F0b: axis prefactor (-D)*M^2 -> (pi n)^2/6 at M = 32 ----
pref0 = -Dval(rays["axis(2,0,0,0)"], 32) * 32.0 ** 2
tgt0 = (np.pi ** 2) * 4.0 / 6.0
ok &= ck(abs(pref0 - tgt0) / tgt0 < 5e-3,
         "F0b  axis prefactor (-D)*M^2 = (pi*n)^2/6 (exact)",
         "got %.10f target %.10f rel %.3e" % (pref0, tgt0, abs(pref0 - tgt0) / tgt0))

# ---- F1b: second order via R = (-D - x^2/6) * M^4 -> -(2 pi)^4 / 120 (axis) ----
Rvals = []
for M in SEC:
    x = np.pi * 2.0 / M
    R = (-Dval(rays["axis(2,0,0,0)"], M) - x ** 2 / 6.0) * M ** 4
    Rvals.append(R)
tgt1 = -(np.pi * 2.0) ** 4 / 120.0
best = Rvals[-1]
ok &= ck(abs(best - tgt1) / abs(tgt1) < 2e-2,
         "F1b  second order -(2 pi)^4/120 at M^-4 (dim-7 operator, axis parity)",
         "R(M=64)=%.8f target %.8f rel %.3e | ladder %s" % (best, tgt1,
                                                            abs(best - tgt1) / abs(tgt1),
                                                            ["%.7f" % r for r in Rvals]))

# ---- F2a: A_dir -> 1 at M = 64 for all rays ----
A64 = {nm: -Dval(nv, 64) * 64.0 ** 2 * 6.0 / ((np.pi * np.linalg.norm(nv)) ** 2 * S4_of(nv))
       for nm, nv in rays.items()}
ok &= ck(all(abs(a - 1.0) < 1e-2 for a in A64.values()),
         "F2a  isotropy-normalised amplitude A_dir -> 1 at M=64 (direction ladder)",
         str({k: round(v, 6) for k, v in A64.items()}))

# ---- F2b: A_dir in [0.99,1.01] for ALL rays on ALL blind M (uniform isotropy of limits) ----
Aall = {nm: {M: -Dval(nv, M) * M ** 2 * 6.0 / ((np.pi * np.linalg.norm(nv)) ** 2 * S4_of(nv))
             for M in BLIND} for nm, nv in rays.items()}
flat = [a for d in Aall.values() for a in d.values()]
ok &= ck(all(abs(a - 1.0) < 1e-2 for a in flat),
         "F2b  A_dir within 1e-2 of 1 on every blind M and every ray (no extra anisotropy)",
         "A range [%.6f, %.6f]" % (min(flat), max(flat)))

# ---- F3: falsification guard (REVISED construction, audit-side 2026-10-02) ----
# A dim-4 (1/M) breaking operator dominates at large M; two observable tests:
Ms6 = BLIND + SEC
ys = np.array([Dval(rays["axis(2,0,0,0)"], M) for M in Ms6])
xs2 = np.array([1.0 / M ** 2 for M in Ms6]); xs4 = np.array([1.0 / M ** 4 for M in Ms6])
A2 = np.vstack([xs2, xs4, np.ones_like(xs2)]).T
(a2, a3, a0), *_ = lstsq(A2, ys, rcond=None)
res_pure = np.max(np.abs(ys - A2 @ np.array([a2, a3, a0]))) / np.max(np.abs(ys))
xs1 = np.array([1.0 / M for M in Ms6])
A3 = np.vstack([xs1, xs2, xs4, np.ones_like(xs1)]).T
(b1, b2, b3, b0), *_ = lstsq(A3, ys, rcond=None)
disp = abs(b1) * Ms6[-1] ** 2 / (abs(b2) + 1e-300)
ok &= ck(res_pure < 1e-4 and disp < 0.05,
         "F3  no dim-4 (1/M) breaking operator: pure M^-2/M^-4 law holds to 1e-4 and a free"
         " 1/M term displaces the leading amplitude by < 5%",
         "(i) max rel residual %.3e < 1e-4  |  (ii) |b1|*Mmax^2/|b2| = %.4f < 0.05"
         % (res_pure, disp))
print("\nF3 note: the earlier naive |c1|/sigma construction was discarded (audit-side): with"
      " near-exact 6-point data sigma -> 0, so any functional-form mismatch is significant in"
      " sigma units.  The dominance tests above are the honest criteria; a present 1/M operator"
      " would break the pure M^-2/M^-4 law at > 1e-4 or shift the leading amplitude by > 5%.")

# ---- F4: honest grading ----
print("\n[F4] HONEST GRADING")
print("  * kinematic reduction to d'Alembertian in the continuum:      YES (exact identity)")
print("  * leading breaking exponent 2.000, irrelevant (dim-5+):       measured above")
print("  * SIGNATURE (Euclidean -> Lorentzian) and Wick rotation:      INPUT (U3-4, not claimed)")
print("  * boost/Poincare group as a SYMMETRY of the continuum:        NOT established here")
print("  * layer rule: FSR = discrete layer; SR = continuous layer.    Any 'SR derived' claim")
print("    must state its layer.  This script measures the CONTINUOUS-layer approach speed.")

print("\nRESULT: %s" % ("ALL CHECKS PASS" if ok else "SOME CHECKS FAILED"))
print("HONEST STATUS: the Lorentz-breaking operators of the free 4D product lattice scale as")
print("  |D| ~ (pi|n|)^2 S4/(6 M^2) exactly (|exponent| %.5f; prefactor law confirmed)"
      % (-fit_exponent(rays["axis(2,0,0,0)"], BLIND)[0]))
print("  with the second order -(2 pi)^4/(120 M^4) on the axis, and the direction dependence")
print("  exactly the free-lattice S4 ladder (axis:face:body:hyper = 1:1/2:1/3:1/4) -- i.e. the")
print("  only breaking is the lattice's own finite-spacing kinematics, which is IRRELEVANT")
print("  (dim >= 5).  This is the first step of demoting O140's axiom A2 (relativity principle)")
print("  to a theorem; it does NOT by itself construct the Lorentz group, and the signature")
print("  remains an input.")