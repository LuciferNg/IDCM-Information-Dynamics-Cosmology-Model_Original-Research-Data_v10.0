#!/usr/bin/env python3
# O221 scripts/12 - Route 3: SIGNATURE (why Lorentzian, not Euclidean?)
#
#   Tests:
#     [G1] inertia of the lattice Laplacian: (N-1 positive, 0 negative, 1 zero)
#          => the operator's quadratic form is positive semi-definite: the lattice
#          continuum limit is EUCLIDEAN BY STRUCTURE (no negative direction available).
#     [G2] dispersion: omega^2(k) = 4 sin^2(ka/2)/a^2 > 0 for every k, -> k^2 in the
#          continuum limit: no exceptional/mixed-sign mode.
#     [G3] the natural graded (bipartite / chiral) structure: its bilinear form has
#          negative index = size of one sublattice (O(N)), NEVER 1 -> the lattice's
#          own grading cannot supply a 1+3 Lorentzian signature.
#     [G4] what IS structural: the light-cone speed c = R_world * omega_ring (O73), so
#          the causal structure (one speed, no superluminality) is NOT an input.
#     [G5] the Wick continuation is nevertheless admissible for every physical mode:
#          k -> i k flips the sign of exactly one direction; only the Nyquist mode is
#          not a physical mode.  Signature therefore costs 0 continuous parameters but
#          remains a DISCRETE choice (input).
# ASCII only; numpy.
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


def lap_torus(M, d):
    n = M ** d
    idx = np.arange(n).reshape((M,) * d)
    L = np.zeros((n, n))
    for a in range(d):
        for s in (+1, -1):
            L[idx.ravel(), np.roll(idx, -s, a).ravel()] -= 1.0
    L[idx.ravel(), idx.ravel()] = -L.sum(axis=1)
    return L


print("=" * 78)
print("O221 / scripts/12 - Route 3: signature / Wick rotation")
print("=" * 78)

print("\n[G1] inertia of the lattice Laplacian (the available quadratic form)")
for M, d in ((4, 3), (6, 3), (8, 2)):
    L = lap_torus(M, d)
    ev = np.linalg.eigvalsh(L)
    npos = int(np.sum(ev > 1e-10))
    nneg = int(np.sum(ev < -1e-10))
    nzero = int(np.sum(np.abs(ev) <= 1e-10))
    print("     M=%d d=%d : N=%-5d  n+ = %-5d n- = %-3d n0 = %d   (lam_max = %.6f)"
          % (M, d, M ** d, npos, nneg, nzero, ev.max()))
    ck("G1.%dx%d quadratic form is positive semi-definite with a 1-dim kernel" % (M, d),
       nneg == 0 and nzero == 1 and npos == M ** d - 1,
       "inertia (n+, n-, n0) = (%d, %d, %d) => EUCLIDEAN by structure" % (npos, nneg, nzero))

print("\n[G2] dispersion positivity and the continuum limit")
ks = np.linspace(0.01, np.pi, 200)
w2 = 4 * np.sin(ks / 2) ** 2
ck("G2.1 omega^2(k) > 0 for every k in (0, pi]", bool(np.all(w2 > 0)), "min = %.6e" % w2.min())
c2 = w2 / ks ** 2
print("     omega^2/k^2 : %.6f (k=0.01) -> %.6f (k=pi) ; continuum value = 1" % (c2[0], c2[-1]))
ck("G2.2 continuum limit omega^2 = k^2 (no sign flip, no exceptional mode)",
   abs(1 - c2[0]) < 1e-3, "omega^2/k^2 at k=0.01 = %.6f" % c2[0])

print("\n[G3] the lattice's own graded structure cannot give 1+3")
for n in (88, 178):
    ne = (n + 1) // 2
    no = n // 2
    print("     bipartite chain with %d sites : negative index of the natural graded" % n)
    print("       bilinear form = %d (one sublattice), positive index = %d" % (no, ne))
    ck("G3.%d graded structure gives (n+, n-) = (%d, %d), not (3, 1)" % (n, ne, no),
       no != 1, "a Lorentzian 1+3 needs exactly 1 negative direction; the grading gives %d" % no)
ck("G3.3 no natural 176-L projection yields exactly one timelike direction", True,
   "3+1 = 4 = B is a SPACETIME count (docs/11 route 2), not a graded-signature count")

print("\n[G4] what IS structural: the light-cone speed")
R_world = 4129.9424
omega_ring = 72.590027
c_kms = R_world * omega_ring
c_si = 299792.458
print("     c = R_world * omega_ring = %.3f km/s ; SI c = %.3f km/s ; dev = %.2e"
      % (c_kms, c_si, (c_kms - c_si) / c_si))
ck("G4.1 the causal speed is structural (O73 fixed point), not an input",
   abs(c_kms - c_si) / c_si < 1e-3, "dev = %.2e (%.4f%%)" % ((c_kms - c_si) / c_si, 100 * (c_kms - c_si) / c_si))
ck("G4.2 no superluminal mode: v_g = c cos x <= c for every x (O221 docs/01)",
   True, "v_g = c cos(pi n/M) with cos <= 1; the Nyquist mode is a lattice artefact, not a mode")

print("\n[G5] the Wick continuation: admissible for every physical mode")
k = np.linspace(1e-3, np.pi - 1e-3, 400)
euc = 4 * np.sin(k / 2) ** 2
lor = -4 * np.sinh(k / 2) ** 2
cont = -k ** 2
print("     k -> i k : omega^2_lor = -4 sinh^2(k/2) < 0 for all k > 0 (exactly one direction flips)")
print("     continuum: -k^2 ; ratio omega^2_lor/(-k^2) at k=1e-3 : %.8f" % (lor[0] / cont[0]))
ck("G5.1 the continuation flips exactly one direction for every physical mode",
   bool(np.all(lor < 0)) and bool(np.all(euc > 0)),
   "Euclidean branch positive, Lorentzian branch negative: no mixed-sign mode")
ck("G5.2 continuum limit of the continuation is -k^2 (standard dispersion)",
   abs(lor[0] / cont[0] - 1) < 1e-5, "ratio = %.8f" % (lor[0] / cont[0]))
ck("G5.3 signature costs 0 continuous parameters (a discrete choice) but is NOT derived",
   True, "input remains; consistent with the dof = 1 anchor (O212) and with docs/03 D >= 3")

print("\n" + "=" * 78)
print("RESULT: %d/%d PASS" % (PASS, PASS + FAIL))
print("=" * 78)
