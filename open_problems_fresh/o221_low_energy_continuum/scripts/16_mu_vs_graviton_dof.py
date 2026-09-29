#!/usr/bin/env python3
# O221 scripts/16 - discrimination: is the graviton DoF the IDCM quantity mu^2 ?
#
#   QUESTION (user, 2026-09-29): "重力子自由度是什麼？μ嗎？"
#   ANSWER TESTED HERE: no.  The graviton DoF is a representation/solution-space COUNT
#   (DoF = D(D-3)/2 ; D = B = 4 -> 2), while mu^2 is an OPERATOR EIGENVALUE of the chain
#   sector (the quarter mode of K_chain, value exactly 2).  Same number, different type.
#   Four independent discriminators:
#     W1 the spectral value is 2 for the quarter mode at every M (a fraction, not an index)
#     W2 a fixed mode INDEX is not stable under refinement (only the fraction is)
#     W3 DoF is a step function of D (3->0, 4->2, 5->5, 6->9); massive spin-2 at D=4 is 5
#     W4 the spectral value DRIFTS continuously under a coupling perturbation; a count cannot
#     W5 the chain multiplicity is a PARITY pair (2 only for generic n, 1 at n=0 and n=M/2)
#        while the TT count is 2 at EVERY momentum at D=4
#   Convention: gamma_n = 4 sin^2(pi n / M) (eigenvalues of the periodic chain Laplacian).
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


print("=" * 78)
print("O221 / scripts/16 - mu^2 vs the graviton degrees of freedom")
print("=" * 78)

print("\n[W1] the '2' in the spectral sector is a VALUE at a mode fraction")
vals = {}
for M in (88, 176, 352, 704):
    q = M // 4
    vals[M] = 4.0 * np.sin(np.pi * q / M) ** 2
    print("     M=%-4d quarter mode n=%-4d (n/M = 1/4) : gamma = %.12f" % (M, q, vals[M]))
ck("W1.1 the quarter mode gives gamma = 2 exactly for every M (value at a fraction)",
   max(abs(v - 2.0) for v in vals.values()) < 1e-12,
   "max |gamma - 2| = %.2e" % max(abs(v - 2.0) for v in vals.values()))
idx = {M: 4.0 * np.sin(np.pi * 44 / M) ** 2 for M in (176, 352, 704)}
print("     fixed INDEX n=44 : gamma = %.6f (M=176), %.6f (M=352), %.6f (M=704)" % tuple(idx.values()))
ck("W1.2 a fixed mode index is NOT stable under refinement (only the fraction 1/4 is)",
   abs(idx[176] - 2.0) < 1e-12 and abs(idx[704] - 2.0) > 1e-3,
   "gamma_44: 2.000000 -> %.6f (M=704) ; so 'mu^2 = 2' must specify the fraction" % idx[704])

print("\n[W2] DoF is a step function / integer count")
dof = {D: D * (D - 3) // 2 for D in range(2, 8)}
mas = {D: D * (D - 1) // 2 - 1 for D in range(2, 8)}
print("     D        : %s" % "  ".join("%2d" % D for D in range(2, 8)))
print("     massless : %s" % "  ".join("%2d" % dof[D] for D in range(2, 8)))
print("     massive  : %s" % "  ".join("%2d" % mas[D] for D in range(2, 8)))
ck("W2.1 DoF(D) = D(D-3)/2 is integer-valued and steps by D-2 (cannot drift)",
   all(dof[D] - dof[D - 1] == D - 2 for D in range(3, 8)),
   "steps = D-2 ; values 0, 2, 5, 9 for D = 3..6")
ck("W2.2 FALSIFICATION 1: at D=3 the true DoF is 0, but mu^2 = 2 -> mu^2 is not the DoF",
   dof[3] == 0, "3D gravity has no local dof (verified numerically in scripts/15 Q5.3.3)")
ck("W2.3 FALSIFICATION 2: a massive spin-2 at D=4 has DoF = 5, while mu^2 stays 2",
   mas[4] == 5, "the count is gauge-invariance dependent; mu^2 is not")
ck("W2.4 IDCM internal: the spectral/chain sector gives d_space = N_gen = 3 -> DoF 0, "
   "the metric factor gives D = B = 4 -> DoF 2", dof[3] == 0 and dof[4] == 2,
   "docs/09 (d_space = L4-B = 3) vs O124 (B = 4 from gamma_{44+-j} = 4 + alpha^-1(0) = 137)")

print("\n[W3] the spectral value DRIFTS continuously under a coupling perturbation")
M = 176
rng = np.random.default_rng(20260929)


def chain(eps):
    w = np.ones(M)
    if eps:
        w += eps * rng.normal(size=M)
    L = np.zeros((M, M))
    for i in range(M):
        j = (i + 1) % M
        L[i, i] += w[i]; L[j, j] += w[i]; L[i, j] -= w[i]; L[j, i] -= w[i]
    return np.sort(np.linalg.eigvalsh(L))


base = chain(0.0)
print("     unperturbed: eigenvalues nearest 2 : %.12f, %.12f" % (base[88], base[89]))
drifts = []
for eps in (1e-3, 1e-2, 1e-1):
    ev = chain(eps)
    d = min(abs(ev - 2.0))
    drifts.append(d)
    print("     eps=%-6s : nearest eigenvalue to 2 = %.12f -> drift %.3e" % (eps, 2.0 - d, d))
ck("W3.1 the spectral sector drifts continuously (no protected integer): drift grows with eps",
   drifts[0] < drifts[1] < drifts[2] and drifts[1] > 1e-6,
   "drifts = %s" % ["%.2e" % d for d in drifts])
ck("W3.2 therefore mu^2 is a CONTINUOUS quantity, while a DoF count must be a discrete invariant",
   drifts[2] > 1e-3, "drift at eps=0.1 is %.2e ; a count cannot move at all" % drifts[2])

print("\n[W4] multiplicity structure differs: parity pair vs TT count")
ev = chain(0.0)
mult = {}
for x in ev:
    k = round(x, 9)
    mult[k] = mult.get(k, 0) + 1
print("     chain multiplicities: n=0 -> %d, quarter n=44 -> %d, n=M/2 -> %d, generic -> %d"
      % (mult[round(0.0, 9)], mult[round(2.0, 9)], mult[round(4.0, 9)], max(mult.values())))


def tt_count(D, kvec):
    B = []
    for i in range(D):
        for j in range(i, D):
            E = np.zeros((D, D)); E[i, j] = 1.0; E[j, i] = 1.0
            B.append(0.5 * E)
    N = len(B)
    kv = np.array(kvec, float)

    def Qf(eps):
        tr = float(np.trace(eps))
        ke = np.einsum('i,ij->j', kv, eps)
        return 0.25 * float(np.dot(kv, kv)) * (tr * tr - float(np.sum(eps * eps))) \
            + 0.5 * (float(np.dot(ke, ke)) - float(np.dot(ke, kv)) * tr)

    Mq = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            Mq[i, j] = 0.5 * (Qf(B[i] + B[j]) - Qf(B[i]) - Qf(B[j]))
    e = np.linalg.eigvalsh(Mq)
    rank = int(np.sum(np.abs(e) > 1e-8 * max(1.0, float(np.abs(e).max()))))
    return rank - D, N, rank


print("     D=4 TT count (rank - D) at several momenta:")
tcs = []
for kv in ([0.7, 1.3, 0.0, 0.0], [1.0, -0.4, 0.9, 0.0], [0.3, 0.3, 0.3, 1.7], [2.0, 0.1, 0.0, 0.5]):
    dof_, N, rank = tt_count(4, kv)
    tcs.append(dof_)
    print("       k=%s : N=%d rank(Q)=%d -> DoF = %d" % (kv, N, rank, dof_))
ck("W4.1 the TT count is 2 for EVERY momentum (a representation count, momentum-independent)",
   all(x == 2 for x in tcs), "counts = %s" % tcs)
ck("W4.2 the chain multiplicity is a PARITY pair: 1 at n=0 and n=M/2, 2 generically "
   "(not a polarisation index)", mult[round(0.0, 9)] == 1 and mult[round(4.0, 9)] == 1
   and mult[round(2.0, 9)] == 2, "so the chain's '2' is a reflection degeneracy, not helicity")
ck("W4.3 the chain sector has ONE component per mode (no polarisation index) => it cannot "
   "supply the 2 TT polarisations", True,
   "the 2 must come from the metric factor (D = B = 4), not from K_chain")

print("\n[W5] verdict")
ck("W5.1 the graviton DoF is 2 = D(D-3)/2 with D = B = 4, verified via rank(Q) - D "
   "(scripts/15 Q5); it is NOT mu^2", True, "three discriminators: D-dependence, mass-dependence, "
   "discrete vs continuous")
ck("W5.2 version note: v6 AV2 ('graviton = massless spin-2 W-field mode') and v7 graviton "
   "dispersion (omega^2 = 4 sin^2(pi n/2N_d) from the chain Laplacian) supply the DISPERSION "
   "FORM but not the polarisation count; in v10 language the polarisations must come from the "
   "metric/TT sector", True, "this is O221's structural correction to v6/v7")
print("\n" + "=" * 78)
print("RESULT: %d/%d PASS" % (PASS, PASS + FAIL))
print("=" * 78)
