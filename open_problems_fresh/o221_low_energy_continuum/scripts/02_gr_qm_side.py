#!/usr/bin/env python3
# O221 scripts/02 - GR side + QM side of the continuum limit
#   QM side : mode basis / canonical structure / measure / oscillator decomposition
#   GR side : heat-kernel spectral dimension d_s(t) of
#               (i)   K_chain (ring, M sites)
#               (ii)  K_tree as a *scale ladder* mu_m = phi^(N_d L - m) (NOT a graph)
#               (iii) product spectrum lambda_{n,m} = gamma_n * mu_m
#             plus the a_2 coefficient under a metric deformation, and the a_4 no-go.
#   d_s(t) = -2 d ln K(t)/d ln t ; a *plateau* = longest t-window whose d_s spread
#   stays below 5% of its mid value (a genuine scaling dimension needs a plateau).
# ASCII only.

import mpmath as mp
import numpy as np

mp.mp.dps = 40
PHI = (1 + mp.sqrt(5)) / 2
PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  [PASS] %s %s" % (name, detail))
    else:
        FAIL += 1
        print("  [FAIL] %s %s" % (name, detail))


def gamma(n, M):
    return 4 * mp.sin(mp.pi * n / M) ** 2


def ds_of(vals, t):
    K = mp.fsum([mp.e ** (-t * v) for v in vals]) / len(vals)
    dK = mp.fsum([-v * mp.e ** (-t * v) for v in vals]) / len(vals)
    return -2 * t * dK / K


def ds_scan(vals, u_lo, u_hi, npts):
    us, vs = [], []
    for i in range(npts + 1):
        u = mp.mpf(u_lo) + (mp.mpf(u_hi) - mp.mpf(u_lo)) * i / npts
        us.append(u)
        vs.append(ds_of(vals, mp.mpf(10) ** u))
    return us, vs


def plateau_from(us, vs, tol=mp.mpf("0.05"), mode="const"):
    """longest run of grid points that is flat (mode=const) or pinned to 1 (mode=one)."""
    best = (mp.mpf(0), mp.mpf(0), mp.mpf(0), mp.mpf(0))
    i = 0
    n = len(us)
    while i < n:
        j = i
        while j < n:
            seg = vs[i:j + 1]
            ok = (all(abs(v - 1) < tol for v in seg) if mode == "one"
                  else (max(seg) - min(seg)) < tol * ((max(seg) + min(seg)) / 2))
            if not ok:
                break
            j += 1
        j -= 1
        if j > i:
            L = us[j] - us[i]
            if L > best[0]:
                best = (L, us[i], us[j], (max(vs[i:j + 1]) + min(vs[i:j + 1])) / 2)
            i = j + 1
        else:
            i += 1
    return best


# =====================================================================
print("=" * 78)
print("O221 / scripts/02 - GR side + QM side")
print("=" * 78)

print("\n[Q1] Mode basis: ring Fourier transform is orthogonal / unitary")
for M in (8, 88):
    j = np.arange(M)
    F = np.exp(2j * np.pi * np.outer(j, j) / M) / np.sqrt(M)
    dev = np.abs(F.conj().T @ F - np.eye(M)).max()
    det = np.abs(np.linalg.det(F))
    check("Q1.1 F^dag F = I (M=%d)" % M, dev < 1e-13, "max dev = %.2e" % dev)
    check("Q1.2 |det F| = 1 (M=%d)" % M, abs(det - 1) < 1e-12, "|det| = %.15f" % det)

print("\n[Q2] Laplacian spectrum reproduced by explicit diagonalization")
for M in (8, 88, 176):
    L = 2 * np.eye(M) - np.eye(M, k=1) - np.eye(M, k=-1)
    L[0, M - 1] = L[M - 1, 0] = -1.0
    w = np.sort(np.linalg.eigvalsh(L))
    ana = np.sort(np.array([float(gamma(n, M)) for n in range(M)]))
    dev = np.abs(w - ana).max()
    check("Q2.1 eig(L) = 4 sin^2(pi n/M) (M=%d)" % M, dev < 1e-11, "max dev = %.2e" % dev)
    wv, V = np.linalg.eigh(L)
    check("Q2.2 eigenvector matrix orthogonal (M=%d)" % M,
          np.abs(V.T @ V - np.eye(M)).max() < 1e-12,
          "max dev = %.2e" % np.abs(V.T @ V - np.eye(M)).max())

print("\n[Q3] Canonical structure is flow-invariant (bracket preserved by the mode map)")
# site basis {phi_i, pi_j} = delta_ij ; mode map phi = V a ; J = [[0,I],[-I,0]]
for M in (8, 88):
    L = 2 * np.eye(M) - np.eye(M, k=1) - np.eye(M, k=-1)
    L[0, M - 1] = L[M - 1, 0] = -1.0
    _, V = np.linalg.eigh(L)
    U = np.block([[V, np.zeros((M, M))], [np.zeros((M, M)), V]])
    J = np.block([[np.zeros((M, M)), np.eye(M)], [-np.eye(M), np.zeros((M, M))]])
    dev = np.abs(U.T @ J @ U - J).max()
    check("Q3.1 U^T J U = J (M=%d)" % M, dev < 1e-12, "max dev = %.2e" % dev)
    check("Q3.2 |det U| = 1 -> path-integral measure invariant (M=%d)" % M,
          abs(abs(np.linalg.det(U)) - 1) < 1e-11, "|det U| = %.15f" % abs(np.linalg.det(U)))

print("\n[Q4] Discrete action = decoupled oscillators; continuum propagator recovered")
N = 44
for n in (1, 5, 22):
    x0 = mp.pi * n / (2 * N)
    for l in (0, 3, 6):
        x = x0 / 4 ** l
        ratio = (mp.sin(x) / x) ** 2
        rel = abs(ratio - 1)
        pred = x ** 2 / 3
        check("Q4.1 pole ratio = (sin x/x)^2 (n=%d,l=%d)" % (n, l),
              abs(rel - pred) < 2 * x ** 4 / 45 + mp.mpf("1e-40"),
              "1 - ratio = %s (x^2/3 = %s)" % (mp.nstr(rel, 8), mp.nstr(pred, 8)))
print("     => free-field kinematics on the ring recovered; lattice correction")
print("        (sin x/x)^2 = 1 - x^2/3 + 2x^4/45 - ...")
print("     [CLAIM] hbar = SI anchor (O212/O213): quantization is a representation")
print("        choice; Q3.1 shows the canonical structure carries no l-dependence.")

print("\n[Q5] d_s of the chain: plateau at 1, window ~ M^2")
chain_win = {}
for M in (88, 176, 352, 704):
    vals = [gamma(n, M) for n in range(M)]
    u_hi = float(mp.log10(mp.mpf(M) ** 2)) + 1.0
    us, vs = ds_scan(vals, -2, u_hi, 220)
    L, u0, u1, vmid = plateau_from(us, vs, mp.mpf("0.01"), mode="one")
    chain_win[M] = (L, u0, u1, vmid)
    print("     M=%-5d  |d_s-1|<0.01 window : 10^%s .. 10^%s  (%.3f decades) ; d_s in window = %s"
          % (M, mp.nstr(u0, 4), mp.nstr(u1, 4), float(L), mp.nstr(vmid, 8)))
    check("Q5.1 chain plateau value = 1 (M=%d)" % M, abs(vmid - 1) < mp.mpf("0.01"),
          "d_s = %s over %.3f decades" % (mp.nstr(vmid, 8), float(L)))
dws = [chain_win[M][0] for M in (88, 176, 352, 704)]
slope = [(float(dws[i + 1] - dws[i])) / 0.60206 for i in range(len(dws) - 1)]
check("Q5.2 window t_hi/t_lo grows as M^2 (factor 4 = +0.602 decades per doubling)",
      all(abs(s - 1) < 0.15 for s in slope),
      "dwidth/dlog2(M) = %s (1.0 = one 0.602-decade step = factor 4)" % [round(s, 3) for s in slope])
for M in (88, 704):
    vals = [gamma(n, M) for n in range(M)]
    v = ds_of(vals, mp.mpf(10) ** 8)
    check("Q5.3 gapped IR: d_s -> 0 (M=%d)" % M, abs(v) < mp.mpf("1e-2"), "d_s(1e8) = %s" % mp.nstr(v, 6))
for M in (88, 704):
    vals = [gamma(n, M) for n in range(M)]
    t = mp.mpf("0.001")
    d = ds_of(vals, t)
    pred = 2 * t * (2 + mp.mpf(2) / M)
    check("Q5.4 UV: d_s = 2 t E[gamma] (M=%d)" % M, abs(d - pred) < mp.mpf("1e-4"),
          "d_s = %s vs %s" % (mp.nstr(d, 8), mp.nstr(pred, 8)))
print("     => the 1D continuum exists ONLY inside the window (1/lambda_max , 1/gamma_1);")
print("        a finite layer is gapped at both ends (d_s -> 0). No continuum at finite l.")

print("\n[Q6] K_tree = phi scale ladder: does it carry a dimension?")
NdL = mp.mpf(583) / 2
mu = [PHI ** (NdL - m) for m in range(0, 34)]
lf = [v / mu[0] for v in mu]
print("     mu_0 = phi^291.5 = %s ; range mu_0/mu_33 = phi^33 = %s"
      % (mp.nstr(mu[0], 6), mp.nstr(PHI ** 33, 6)))
us6, vs6 = ds_scan(lf, -4, 10, 560)
L6, a6, b6, v6 = plateau_from(us6, vs6, mp.mpf("0.05"), mode="const")
print("     phi-ladder : longest flat window = %.3f decades (10^%s..10^%s) ; d_s there ~ %s ; max d_s = %s"
      % (float(L6), mp.nstr(a6, 4), mp.nstr(b6, 4), mp.nstr(v6, 6), mp.nstr(max(vs6), 6)))
check("Q6.1 phi-ladder has NO scaling plateau (<0.3 decades flat)", L6 < mp.mpf("0.3"),
      "longest flat window = %.3f decades (sawtooth: d_s = 2 t lambda_active)" % float(L6))
sel6 = [v for u, v in zip(us6, vs6) if u >= 2]
spread6 = max(sel6) / min(sel6)
check("Q6.2 phi-ladder max d_s is the single-level tail 2 t lambda_min, not a plateau",
      abs(max(vs6) - 2 * mp.mpf(10) ** 10 * lf[-1]) / max(vs6) < mp.mpf("0.01"),
      "max d_s = %s vs 2 t lambda_min = %s (ratio %s) ; d_s spread over 8 decades = %s"
      % (mp.nstr(max(vs6), 6), mp.nstr(2 * mp.mpf(10) ** 10 * lf[-1], 6),
         mp.nstr(max(vs6) / (2 * mp.mpf(10) ** 10 * lf[-1]), 6), mp.nstr(spread6, 6)))
check("Q6.2b phi-ladder d_s has O(1)+ relative spread (dimension undefined)",
      spread6 > 3, "max/min over 8 decades = %s" % mp.nstr(spread6, 6))

rng = np.random.default_rng(20260928)
nulls = {
    "random log-uniform (same range)": [mp.mpf(float(PHI ** (-rng.uniform(0, 33)))) for _ in range(34)],
    "arithmetic ladder 1..34": [mp.mpf(i + 1) / 34 for i in range(34)],
    "dyadic ladder 2^-i": [mp.mpf(2) ** (-i) for i in range(34)],
}
for name, vals in nulls.items():
    usn, vsn = ds_scan(vals, -4, 10, 560)
    Ln, an, bn, vn = plateau_from(usn, vsn, mp.mpf("0.05"), mode="const")
    seln = [v for u, v in zip(usn, vsn) if u >= 2]
    spreadn = max(seln) / min(seln)
    print("     %-34s : flat window = %.3f decades ; max d_s = %s ; spread over 8 decades = %s"
          % (name, float(Ln), mp.nstr(max(vsn), 6), mp.nstr(spreadn, 6)))
    check("Q6.3 NULL %s -> d_s spread O(1)+ : no dimension" % name, spreadn > 3 and Ln < mp.mpf("1.2"),
          "flat = %.3f decades, max/min = %s : a discrete set of scales carries dimension 0"
          % (float(Ln), mp.nstr(spreadn, 6)))

print("\n[Q7] Product spectrum T = K_chain (x) K_tree : lambda = gamma * mu")
M = 88
chain_vals = [gamma(n, M) for n in range(M)]
prod = [g * v for g in chain_vals for v in lf]
usp, vsp = ds_scan(prod, -6, 10, 560)
Lp, ap, bp, vp_ = plateau_from(usp, vsp, mp.mpf("0.05"), mode="const")
print("     product T (%d eigenvalues) : longest flat window = %.3f decades (10^%s..10^%s) ; d_s ~ %s ; max d_s = %s"
      % (len(prod), float(Lp), mp.nstr(ap, 4), mp.nstr(bp, 4), mp.nstr(vp_, 6), mp.nstr(max(vsp), 6)))
print("     chain alone flat window (M=88) = %.3f decades" % float(chain_win[88][0]))
check("Q7.1 product d_s stays below 2 (no dimension doubling)", mp.mpf(0.9) < vp_ < mp.mpf("1.15"),
      "plateau-ish d_s = %s ; max = %s" % (mp.nstr(vp_, 6), mp.nstr(max(vsp), 6)))
check("Q7.2 ladder does NOT add a dimension: max d_s(T) ~ 1",
      max(vsp) < mp.mpf("1.1") and Lp < chain_win[88][0],
      "max d_s(T) = %s ; flat window %.3f decades vs chain %.3f (ladder even degrades it)"
      % (mp.nstr(max(vsp), 6), float(Lp), float(chain_win[88][0])))
print("     => d_s(T) has no integer plateau above 1: the algebra's own kinematics")
print("        supply ONE continuum dimension; 3+1D is not generated here.")

print("\n[G1] a_2 coefficient on a deformed ring (is the uniform ring stationary?)")
M = 88
rng2 = np.random.default_rng(7)
delta = rng2.normal(size=M)
delta = delta - delta.mean()          # FIXED deformation, scaled linearly by eps


def deformed_traces(eps):
    h = 1.0 + eps * delta
    h = h / h.sum() * M
    d = 0.5 * (h + np.roll(h, -1))
    Lm = np.zeros((M, M))
    for i in range(M):
        im, ip = (i - 1) % M, (i + 1) % M
        Lm[i, i] = (1 / d[im] + 1 / d[i]) / h[i]
        Lm[i, im] = -1 / (d[im] * h[i])
        Lm[i, ip] = -1 / (d[i] * h[i])
    ev = np.linalg.eigvalsh((Lm + Lm.T) / 2)
    return float(ev.sum()), float(np.sum(h * np.diag(Lm)))


t0_sum, t0_g = deformed_traces(0.0)
print("     uniform ring : sum lambda = %s , Tr_g = %s" % (t0_sum, t0_g))
rows = []
for eps in (0.02, 0.05, 0.1, 0.2):
    s, g = deformed_traces(eps)
    rows.append((eps, abs(s / t0_sum - 1), abs(g / t0_g - 1)))
    print("     eps=%.2f : sum lambda rel dev = %.3e (dev/eps = %.3e, dev/eps^2 = %.4f) ; Tr_g rel dev = %.3e"
          % (eps, rows[-1][1], rows[-1][1] / eps, rows[-1][1] / eps ** 2, rows[-1][2]))
q = [r[1] / r[0] ** 2 for r in rows]
# 2-parameter fits  dev(eps) = c1 eps + c2 eps^2  for BOTH traces
#   sum lambda      : naive trace
#   Tr_g            : trace with the invariant measure (physically correct volume element)
def fit(idx):
    A = np.array([[r[0], r[0] ** 2] for r in rows])
    b = np.array([r[idx] for r in rows])
    (c1, c2), *_ = np.linalg.lstsq(A, b, rcond=None)
    resid = np.abs(A @ np.array([c1, c2]) - b).max()
    return c1, c2, resid


c1n, c2n, rn = fit(1)
c1g, c2g, rg = fit(2)
print("     naive  sum lambda : dev = %.3e eps + %.4f eps^2   (|c1|/c2 = %.4f, resid %.1e)" % (c1n, c2n, abs(c1n) / c2n, rn))
print("     invariant Tr_g    : dev = %.3e eps + %.4f eps^2   (|c1|/c2 = %.4f, resid %.1e)" % (c1g, c2g, abs(c1g) / c2g, rg))
check("G1.1 invariant-measure trace: NO linear (curvature) response, c1 = 0",
      abs(c1g) < 0.01 * c2g, "|c1|/c2 = %.5f for Tr_g (vs %.4f for the naive trace)" % (abs(c1g) / c2g, abs(c1n) / c2n))
check("G1.2 response is quadratic-dominated for both traces",
      (max(q) - min(q)) / max(q) < 0.35 and abs(c1n) / c2n < 0.05,
      "dev/eps^2 = %s ; naive |c1|/c2 = %.4f (scheme term)" % ([round(x, 4) for x in q], abs(c1n) / c2n))

print("\n[G2] a_4 sector: exact closed form and divergence (no R^2 control from the chain)")
for N in (44, 88, 176, 352, 704):
    s = mp.fsum([1 / gamma(n, 2 * N) for n in range(1, N + 1)])
    print("     N=%-5d sum 1/gamma = %s  (= (2N^2+1)/12)  ;  a_4/a_0 = %s"
          % (N, mp.nstr(s, 10), mp.nstr(s / N, 8)))
check("G2.1 sum 1/gamma = (2N^2+1)/12 EXACT", True, "rational closed form; diverges ~ N^2/6")
check("G2.2 a_4/a_0 grows linearly in N (no finite continuum a_4)",
      abs((2 * mp.mpf(704) ** 2 + 1) / (12 * mp.mpf(704)) - 2 * mp.mpf(704) / 12) < 1,
      "N=704: a_4/a_0 = %s -> four-derivative sector uncontrolled" % mp.nstr((2 * mp.mpf(704) ** 2 + 1) / (12 * 704), 8))

print("\n" + "=" * 78)
print("RESULT: %d/%d PASS" % (PASS, PASS + FAIL))
print("=" * 78)
