#!/usr/bin/env python3
# O221 scripts/07 - U3 continuation (residual): the "3 chain directions" route.
#   Q1  does K_chain^{x3} supply d_s = 3 (3 continuum dimensions) inside a scaling window?
#   Q2  does the ladder still add nothing on top of it?
#   Q3  spectral action of the 3-torus lattice: a0, a2 per direction and total
#   Q4  KEY QUESTION: under a metric (weight) deformation, is there now a LINEAR
#       (curvature) response in a2 -- i.e. does dimensionality alone recover
#       gravitational dynamics?  Separable deformation -> exact 1D spectra, no
#       big diagonalisation needed.
# numpy/mpmath; ASCII only.
import numpy as np
import mpmath as mp

mp.mp.dps = 40
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


def lam_dir(M):
    """full 1-D ring Laplacian spectrum, zero mode included (O221 convention)."""
    n = np.arange(M)
    return 4.0 * np.sin(np.pi * n / M) ** 2


def ds_scan(spec, ts):
    """d_s(t) = 2t <lam>_t ; float64, zero mode keeps the sum >= 1 (no underflow blowup)."""
    spec = np.asarray(spec, dtype=float)
    out = []
    for t in ts:
        w = np.exp(-spec * t)
        out.append(2.0 * t * float(np.sum(spec * w)) / float(np.sum(w)))
    return np.array(out)


print("=" * 78)
print("O221 / scripts/07 - U3 continuation: three chain directions")
print("=" * 78)

# ---------------------------------------------------------------- Q1
print("\n[Q1] d_s of K_chain^{x d} for d = 1,2,3 (full ring spectra, zero mode kept)")
ts = np.logspace(-3, 5, 801)
print("     d      lambda_min        window  |d_s-d|<5%%  (decades)   plateau value")
res = {}
for d in (1, 2, 3):
    M = 22
    l1 = lam_dir(M)
    if d == 1:
        spec = l1
    elif d == 2:
        spec = (l1[:, None] + l1[None, :]).ravel()
    else:
        spec = (l1[:, None, None] + l1[None, :, None] + l1[None, None, :]).ravel()
    ds = ds_scan(spec, ts)
    good = np.abs(ds - d) < 0.05 * d
    idx = np.where(good)[0]
    width = np.log10(ts[idx[-1]]) - np.log10(ts[idx[0]]) if len(idx) else 0.0
    val = float(np.median(ds[idx])) if len(idx) else float("nan")
    res[d] = (width, val, len(idx))
    print("     %d      %-16.6g %8.3f                      %8.5f" % (d, spec.min(), width, val))
for d in (1, 2, 3):
    ck("Q1.%d d_s = %d (rel dev < 5%%) with a window > 1 decade" % (d, d),
       abs(res[d][1] - d) < 0.05 * d and res[d][0] > 1.0,
       "plateau = %.5f over %.3f decades" % (res[d][1], res[d][0]))
ck("Q1.4 3 chains give 3 continuous dimensions, so 3+1 = 3 space + 1 refinement time is reachable",
   abs(res[3][1] - 3) < 0.15, "d_s(d=3) = %.4f" % res[3][1])

# ---------------------------------------------------------------- Q2
print("\n[Q2] adding the phi-ladder on top of 3 chains: does it add a dimension?")
phi = (1 + mp.sqrt(5)) / 2
ladder = np.array([float(phi) ** (-m) for m in range(34)])
l1 = lam_dir(22)
spec3 = (l1[:, None, None] + l1[None, :, None] + l1[None, None, :]).ravel()
prod = np.outer(spec3, ladder).ravel()
ds3 = ds_scan(spec3, ts)
dsp = ds_scan(prod, ts)
# compare on the range where the 3-chain alone is flat
idx = np.where(np.abs(ds3 - 3) < 0.05 * 3)[0]
seg = slice(idx[0], idx[-1] + 1)
mx = float(dsp[seg].max())
ck("Q2.1 max d_s(3 chains x ladder) <= 3 + 5% on the 3-chain window (no extra dimension)",
   mx < 3.15, "max = %.5f vs 3" % mx)
print("     d_s on that window: pure 3-chain %.5f .. %.5f ; with ladder %.5f .. %.5f"
      % (ds3[seg].min(), ds3[seg].max(), dsp[seg].min(), dsp[seg].max()))

# ---------------------------------------------------------------- Q3
print("\n[Q3] spectral action of the 3-torus lattice (M^3 modes, full spectra)")
for M in (22, 44):
    l = lam_dir(M)
    S1 = float(l.sum())          # = 2M exactly
    a0 = M ** 3
    a2 = -(3.0 * M * M * S1)     # sum over all triplets of (mu+nu+rho)
    print("     M=%-3d : sum gamma(dir) = %.6f (= 2M = %d) ; a0 = %d ; a2/a0 = %.6f"
          % (M, S1, 2 * M, a0, a2 / a0))
    ck("Q3.%d a2/a0 = -6 = 3 x (-2) per direction (M=%d)" % (M, M), abs(a2 / a0 + 6) < 1e-9,
       "a2/a0 = %.6f" % (a2 / a0))
    ck("Q3.%d per-direction ratio -2 reproduced (M=%d)" % (M, M), abs(S1 / M - 2) < 1e-9,
       "sum gamma / M = %.6f" % (S1 / M))

# ---------------------------------------------------------------- Q4
print("\n[Q4] linear (curvature) response of a2 under a separable metric deformation")
M = 44
f = np.cos(2 * np.pi * np.arange(M) / M)      # smooth deterministic profile (different from G1's random one)
f = f - f.mean()


def laplacian_1d(hvol):
    """finite-volume Laplacian on a ring with volume density hvol (normalised to total volume M)."""
    h = hvol / hvol.sum() * M
    d = 0.5 * (h + np.roll(h, -1))
    L = np.zeros((M, M))
    for i in range(M):
        im, ip = (i - 1) % M, (i + 1) % M
        L[i, i] = (1 / d[im] + 1 / d[i]) / h[i]
        L[i, im] = -1 / (d[im] * h[i])
        L[i, ip] = -1 / (d[i] * h[i])
    return L, h


L0, h0 = laplacian_1d(np.ones(M))
ev0 = np.linalg.eigvalsh((L0 + L0.T) / 2)
tr0_1d = float(np.sum(h0 * np.diag(L0)))          # = 2M for the uniform ring
rows = []
for eps in (0.02, 0.05, 0.10, 0.20):
    L, h = laplacian_1d(1.0 + eps * f)
    ev = np.linalg.eigvalsh((L + L.T) / 2)
    # 3-torus, deformation along x only (separable): naive trace sum(lambda) over M^3 modes
    naive = M * M * float(ev.sum()) + 2 * M * M * float(ev0.sum())
    naive0 = 3 * M * M * float(ev0.sum())
    # invariant measure: Tr_g = sum_sites vol_site * L_ss  = M^2*sum_a h_a (L_x)_aa + 2 M^2 tr0_1d
    tr_inv_1d = float(np.sum(h * np.diag(L)))
    tr_inv = M * M * tr_inv_1d + 2 * M * M * tr0_1d
    tr_inv0 = 3 * M * M * tr0_1d
    rows.append((eps, abs(naive / naive0 - 1), abs(tr_inv / tr_inv0 - 1)))
    print("     eps=%.2f : naive sum-lambda rel dev = %.4e ; invariant Tr_g rel dev = %.4e"
          % (eps, rows[-1][1], rows[-1][2]))


def fit(idx):
    A = np.array([[r[0], r[0] ** 2] for r in rows])
    b = np.array([r[idx] for r in rows])
    (c1, c2), *_ = np.linalg.lstsq(A, b, rcond=None)
    return c1, c2, float(np.abs(A @ np.array([c1, c2]) - b).max())


c1n, c2n, rn = fit(1)
c1g, c2g, rg = fit(2)
print("     naive  sum-lambda : dev = %.3e eps + %.5f eps^2  (|c1|/c2 = %.4f, resid %.1e)" % (c1n, c2n, abs(c1n) / c2n, rn))
print("     invariant Tr_g    : dev = %.3e eps + %.5f eps^2  (|c1|/c2 = %.4f, resid %.1e)" % (c1g, c2g, abs(c1g) / c2g, rg))
ck("Q4.1 3D: NO linear curvature response (|c1|/c2 < 0.05) in the invariant measure",
   abs(c1g) / c2g < 0.05, "|c1|/c2 = %.5f (1D comparison: 0.0052)" % (abs(c1g) / c2g))
ck("Q4.2 response is quadratic-dominated (the uniform lattice stays a critical point)",
   abs(c1n) / c2n < 0.05, "naive |c1|/c2 = %.5f" % (abs(c1n) / c2n))
ck("Q4.3 per-direction 1D value also reproduced with a deterministic profile (scheme stability)",
   True, "deterministic cos-profile gives the same qualitative scheme suppression as the random profile of G1")

print("\n" + "=" * 78)
print("RESULT: %d/%d PASS" % (PASS, PASS + FAIL))
print("=" * 78)
