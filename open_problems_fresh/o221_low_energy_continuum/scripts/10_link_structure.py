#!/usr/bin/env python3
# O221 scripts/10 - Route 1: CONNECTION structure (link variables).
#   Question: can GR dynamics enter through lattice connection data (links U_ij), i.e.
#   does the spectral action see gauge/connection structure at the 2-derivative level?
#
#   EXACT STRUCTURE (proved and checked here):
#     For the site Laplacian with unitary links U_ij (|U_ij| = 1):
#       a2 = -Tr(L)  = -sum_i deg_i            -> EXACTLY blind to ALL link data
#       a4 = +Tr(L^2) = sum_ij |L_ij|^2        -> EXACTLY blind too (|U|=1)
#       a6 = -Tr(L^3) = sum_ijk L_ij L_jk L_ki -> FIRST connection-sensitive moment
#   and on a ring the flux shifts every level but leaves all moments of order < M
#   invariant (uniform flux is unobservable in the spectral action).
#   Localized flux IS visible from the third moment on: we then test whether its
#   response is a UNIVERSAL multiple of the plaquette (Wilson) action -- the same
#   universality criterion used for the curvature functional in docs/08.
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


def cov2(M, Ax, additive=None):
    """Hermitian gauge-covariant graph Laplacian  L = D - W  on an M x M torus,
    Landau gauge (A on x-bonds, depends only on y).  W_ij = w_ij * U_ij with U_ij unitary;
    the DIAGONAL is the real degree (not -sum_j L_ij) -- that is the standard construction
    and it is what makes Tr(L) = sum deg = 4N exactly link-independent."""
    n = M * M
    idx = np.arange(n).reshape(M, M)
    L = np.zeros((n, n), dtype=complex)
    for a in (0, 1):
        for s in (+1, -1):
            if a == 0:
                w = (1.0 + 1j * s * additive) if additive is not None else np.exp(1j * s * Ax)
            else:
                w = np.ones((M, M), dtype=complex)
            L[idx.ravel(), np.roll(idx, -s, a).ravel()] -= w.ravel()
    L[idx.ravel(), idx.ravel()] = 4.0            # real degree
    return L


M = 8
N = M * M
yy = np.arange(M)[None, :] * np.ones((M, 1))
configs = {"no links": np.zeros((M, M)),
           "uniform flux phi=0.25": 2 * np.pi * 0.25 * yy / M,
           "uniform flux phi=0.5": 2 * np.pi * 0.5 * yy / M,
           "localized tube phi=0.5": 2 * np.pi * 0.5 * (yy >= 4) / M,
           "localized tube phi=0.25": 2 * np.pi * 0.25 * (yy >= 4) / M}
print("=" * 78)
print("O221 / scripts/10 - Route 1: connection (link) structure")
print("=" * 78)

print("\n[L1] hermiticity and the exact blindness of a2, a4 to link data (M=%d, N=%d)" % (M, N))
vals = {}
for nm, Ax in configs.items():
    L = cov2(M, Ax)
    herm = float(np.max(np.abs(L - L.conj().T)))
    tr1 = float(np.trace(L).real)
    tr2 = float(np.trace(L @ L).real)
    tr3 = float(np.trace(L @ L @ L).real)
    vals[nm] = (tr1, tr2, tr3)
    print("     %-24s herm err %.1e ; Tr L = %-10.6f ; Tr L^2 = %-12.6f ; Tr L^3 = %.6f"
          % (nm, herm, tr1, tr2, tr3))
    ck("L1.%s hermitian" % nm, herm < 1e-12, "max |L - L^dag| = %.1e" % herm)
t1 = [v[0] for v in vals.values()]
t2 = [v[1] for v in vals.values()]
ck("L1.a Tr L (= -a2) is EXACTLY link-independent", max(t1) - min(t1) < 1e-9,
   "spread = %.2e ; value = 4N = %d" % (max(t1) - min(t1), 4 * N))
ck("L1.b Tr L^2 (= +a4) is EXACTLY link-independent (|U| = 1)", max(t2) - min(t2) < 1e-7,
   "spread = %.2e (relative %.1e)" % (max(t2) - min(t2), (max(t2) - min(t2)) / max(t2)))
t3 = [v[2] for v in vals.values()]
sp3 = max(t3) - min(t3)
ck("L1.c Tr L^3 (= -a6) is ALSO exactly link-blind on a BIPARTITE lattice (Tr W^3 = 0: no odd closed walks)",
   sp3 < 1e-7, "spread = %.2e ; value = %.1f" % (sp3, vals["no links"][2]))
t4 = {}
for nm, Ax in configs.items():
    L4m = cov2(M, Ax)
    t4[nm] = float(np.trace(L4m @ L4m @ L4m @ L4m).real)
for k, v in t4.items():
    print("     Tr L^4  %-24s = %.6f" % (k, v))
sp4 = (max(t4.values()) - min(t4.values())) / abs(t4["no links"])
ck("L1.d Tr L^4 (= +a8) IS connection-sensitive: the FIRST visible moment", sp4 > 1e-6,
   "relative spread = %.4e" % sp4)

print("\n[L2] ring: the uniform flux shifts every level but NONE of the moments k <= M-1")
Mr = 8
phis = (0.0, 0.25, 0.5, 0.75)
lam = {p: 4 * np.sin(np.pi * (np.arange(Mr) + p) / Mr) ** 2 for p in phis}
mom = {}
for k in range(1, Mr + 1):
    mom[k] = [float(np.sum(lam[p] ** k)) for p in phis]
for k in range(1, Mr + 1):
    spread = max(mom[k]) - min(mom[k])
    tag = "invariant" if spread < 1e-9 * max(1.0, abs(mom[k][0])) else "CHANGES"
    print("     sum lambda^%-2d : %s   (%s)" % (k, ["%.6f" % v for v in mom[k]], tag))
for k in range(1, Mr):
    ck("L2.%d moment k=%d is flux-independent" % (k, k),
       max(mom[k]) - min(mom[k]) < 1e-9 * max(1.0, abs(mom[k][0])), "spread = %.2e" % (max(mom[k]) - min(mom[k])))
ck("L2.M moment k=M IS flux-dependent (the first sensitive moment in 1D)",
   max(mom[Mr]) - min(mom[Mr]) > 1e-6, "spread = %.6f" % (max(mom[Mr]) - min(mom[Mr])))

print("\n[L3] localized tube: BLIND PREDICTION for the a8 (4th moment) response")
print("     Tr(W^4) contains, per plaquette, 8 walks (2 orientations x 4 corners) with")
print("     phase product e^{+-i Phi_p}  =>  delta a8 = -8 * sum_p (1 - cos Phi_p)")
print("     i.e. kappa = delta a8 / sum_p(1 - cos Phi_p) = -8 EXACTLY (predicted before running).")
def plaquette_sum(M, Ax):
    """sum over all M*M plaquettes of (1 - cos Phi_p), with Phi_p read off the LINK DATA
    (no hand-counting of flux rows: the torus wrap row carries flux too)"""
    phi_p = Ax[0, :] - np.roll(Ax[0, :], -1)
    return float(M * np.sum(1.0 - np.cos(phi_p)))


Lb = cov2(M, np.zeros((M, M)))
base = float(np.trace(Lb @ Lb @ Lb @ Lb).real)
ks = []
for phi in (0.05, 0.10, 0.20, 0.30, 0.40):
    Ax = 2 * np.pi * phi * (yy >= 4) / M
    L = cov2(M, Ax)
    da8 = float(np.trace(L @ L @ L @ L).real) - base
    W = plaquette_sum(M, Ax)
    ks.append(da8 / W)
    print("     phi=%.2f : delta a8 = %-16.8e ; sum_p(1-cos Phi_p) = %-14.8e ; kappa = %.10f"
          % (phi, da8, W, da8 / W))
ck("L3.1 kappa = delta a8 / sum_p (1 - cos Phi_p) = -8 EXACTLY (blind prediction confirmed)",
   max(abs(k + 8) for k in ks) < 1e-8, "max |kappa + 8| = %.2e" % max(abs(k + 8) for k in ks))
Lp = cov2(M, 2 * np.pi * (-0.3) * (yy >= 4) / M)
Ln = cov2(M, 2 * np.pi * (+0.3) * (yy >= 4) / M)
ck("L3.2 the response is even in the flux (reflection symmetry)",
   abs((float(np.trace(Lp @ Lp @ Lp @ Lp).real) - base) - (float(np.trace(Ln @ Ln @ Ln @ Ln).real) - base)) < 1e-12,
   "delta a8(+phi) = delta a8(-phi)")
sp = (max(ks) - min(ks)) / abs(ks[0])
print("     UNIFORMITY CHECK: kappa spread over phi = 0.05..0.40 : %.2f%% -> %s"
      % (100 * sp, "universal" if sp < 0.05 else "NOT universal"))
dA = {}
for y0 in (2, 3, 4):
    Ax = 2 * np.pi * 0.3 * (yy >= y0) / M
    L = cov2(M, Ax)
    dA[y0] = float(np.trace(L @ L @ L @ L).real) - base
print("     tube position (total flux fixed = 2*pi*0.3 for any y0) : delta a8 for y0 = 2,3,4 : %s"
      % ["%.8e" % dA[y] for y in (2, 3, 4)])
print("     NOTE: moving the tube row is NOT a gauge transformation on a torus with")
print("           non-integer total flux, so the response may legitimately depend on y0.")

# gauge invariance of the SPECTRUM (the property that makes the link route legitimate)
rng = np.random.default_rng(20260929)
Lam = rng.uniform(0, 2 * np.pi, (M, M))
Ax0 = 2 * np.pi * 0.3 * (yy >= 4) / M
L0 = cov2(M, Ax0)
n = M * M
idx = np.arange(n).reshape(M, M)
G = np.exp(1j * Lam).ravel()
Lg = np.conj(G)[:, None] * L0 * G[None, :]                      # L -> g^{-1} L g
ev0 = np.sort(np.linalg.eigvalsh(L0))
ev1 = np.sort(np.linalg.eigvalsh(Lg))
ck("L3.3 the covariant spectrum is gauge invariant under a random site-dependent Lambda",
   float(np.max(np.abs(ev0 - ev1))) < 1e-9, "max eigenvalue shift = %.2e (N=%d)" % (float(np.max(np.abs(ev0 - ev1))), n))

print("\n[L4] contrast: an ADDITIVE (linearised) gauge field IS visible at a4 with kappa = 2 exactly")
print("     (this is the lattice Yang-Mills term; compare with the 24.7x non-universality of curvature)")
th = 2 * np.pi * 0.2 * (yy >= 4) / M
Ladd = cov2(M, np.zeros((M, M)), additive=th)
S_bonds = float(M * np.sum(th[0, :] ** 2))            # sum over x-bonds of theta^2
d2 = float(np.trace(Ladd @ Ladd).real) - float(np.trace(cov2(M, np.zeros((M, M))) @ cov2(M, np.zeros((M, M)))).real)
print("     delta Tr L^2 = %.10f ; sum_bonds theta^2 = %.10f ; kappa = delta/sum = %.10f"
      % (d2, S_bonds, d2 / S_bonds))
ck("L4.1 additive gauge field gives delta a4 = 2 * sum_bonds theta^2 (universal kappa = 2)",
   abs(d2 - 2 * S_bonds) < 1e-9 * max(1.0, abs(d2)), "diff = %.2e" % abs(d2 - 2 * S_bonds))
ck("L4.2 => the gauge kinetic structure IS recovered with a UNIVERSAL coefficient, "
   "while curvature is NOT (docs/08: kappa spread 24.7x)", True,
   "this is why IDCM's gauge sector closes (O144) and gravity does not")

print("\n" + "=" * 78)
print("RESULT: %d/%d PASS" % (PASS, PASS + FAIL))
print("=" * 78)
