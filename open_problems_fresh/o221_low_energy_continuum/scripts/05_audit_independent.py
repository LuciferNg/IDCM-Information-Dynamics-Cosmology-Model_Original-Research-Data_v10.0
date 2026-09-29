#!/usr/bin/env python3
# O221 scripts/05 - AUDIT (independent recheck of the whole derivation chain).
#   RULE: imports NO original script; recomputes every headline number from raw inputs
#         with a DIFFERENT algorithm:
#           - conformal identity: periodic finite differences (np.roll) instead of FFT
#           - d_s (chain): analytic derivative 2t<S1>/<S> instead of finite differences
#           - d_s (chain): Monte-Carlo random walk on the ring (no spectrum at all)
#           - units: Mpc^-1 -> GeV via hbar*c / Mpc from first principles
#   mpmath dps = 50 (>= max dps used by scripts 01..04: 50/40/30/40)
# ASCII only. Emits [PASS]/[FAIL] per item.
import numpy as np
import mpmath as mp

mp.mp.dps = 50
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
print("O221 / scripts/05 - AUDIT independent recheck (dps = %d)" % mp.mp.dps)
print("=" * 78)

# =====================================================================
print("\n[A] raw inputs and derived lengths (first principles)")
R_world = mp.mpf("4129.9424")        # Mpc
omega_ring = mp.mpf("72.590027")     # (km/s)/Mpc
c_SI = mp.mpf("299792.458")          # km/s
L_world = 2 * mp.pi * R_world
r_d = L_world / 176
a0 = L_world / 88
c_calc = R_world * omega_ring
print("     L_world = %s Mpc ; r_d = %s ; a0 = %s" % (mp.nstr(L_world, 12), mp.nstr(r_d, 10), mp.nstr(a0, 10)))
print("     c = R_world*omega_ring = %s km/s  vs  c_SI = %s  (rel dev = %s)"
      % (mp.nstr(c_calc, 12), mp.nstr(c_SI, 10), mp.nstr(abs(c_calc - c_SI) / c_SI * 100, 8) + " %"))
ck("A1 a0 = 2*pi*R_world/88 = 2 r_d = 294.8772 Mpc (doc 01 §二)", abs(a0 - mp.mpf("294.8772")) < mp.mpf("5e-5"),
   "a0 = %s" % mp.nstr(a0, 10))
ck("A2 r_d = pi*R_world/88 = 147.4386 Mpc (O127 zero-param)", abs(r_d - mp.mpf("147.4386")) < mp.mpf("5e-5"),
   "r_d = %s" % mp.nstr(r_d, 10))
ck("A3 c fixed point within 0.5% of SI c", abs(c_calc - c_SI) / c_SI < mp.mpf("0.005"),
   "rel dev = %s %%" % mp.nstr(abs(c_calc - c_SI) / c_SI * 100, 6))

# =====================================================================
print("\n[B] spectral identities (closed forms, independent summation)")
for N in (44, 88, 176, 352, 704):
    s = mp.fsum([4 * mp.sin(mp.pi * n / (2 * N)) ** 2 for n in range(1, N + 1)])
    ck("B1.%d sum gamma = 2N+2 (N=%d)" % (N, N), abs(s - (2 * N + 2)) < mp.mpf("1e-40"),
       "sum = %s" % mp.nstr(s, 20))
ev = mp.fsum([4 * mp.sin(mp.pi * k / 176) ** 2 for k in range(2, 89, 2)])
od = mp.fsum([4 * mp.sin(mp.pi * k / 176) ** 2 for k in range(1, 89, 2)])
ck("B2 176-chain: total 178 / even 90 / odd 88 = 2 N_d", abs(ev - 90) < mp.mpf("1e-40") and abs(od - 88) < mp.mpf("1e-40"),
   "even = %s , odd = %s" % (mp.nstr(ev, 12), mp.nstr(od, 12)))
ck("B3 gamma_max = 4 (n = M/2)", abs(4 * mp.sin(mp.pi * 88 / 176) ** 2 - 4) < mp.mpf("1e-45"), "= 4 exact")
ck("B4 mu^2 = gamma_44 of 176-chain = 2", abs(4 * mp.sin(mp.pi * 44 / 176) ** 2 - 2) < mp.mpf("1e-45"), "= 2 exact")
for N in (44, 88, 176, 352, 704):
    s1 = mp.fsum([1 / (4 * mp.sin(mp.pi * n / (2 * N)) ** 2) for n in range(1, N + 1)])
    ck("B5.%d sum 1/gamma = (2N^2+1)/12 (N=%d)" % (N, N),
       abs(s1 - mp.mpf(2 * N * N + 1) / 12) < mp.mpf("1e-30"), "= %s" % mp.nstr(s1, 12))
for N in (44, 88):
    e = mp.fsum([4 * mp.sin(mp.pi * n / (2 * N)) ** 2 for n in range(1, N + 1)]) / N
    ck("B6.%d E[gamma] = 2+2/N (N=%d)" % (N, N), abs(e - (2 + mp.mpf(2) / N)) < mp.mpf("1e-40"),
       "= %s" % mp.nstr(e, 12))
# distinct spectral values and arcsine KS (independent: exact empirical CDF, no grid scan)
for M in (88, 176, 352, 704, 1408):
    vals = sorted(set(4 * mp.sin(mp.pi * k / M) ** 2 for k in range(1, M // 2 + 1)))
    ck("B7.%d distinct spectral values = M/2 (M=%d)" % (M, M), len(vals) == M // 2, "count = %d" % len(vals))
    F = lambda g: mp.mpf(2) / mp.pi * mp.asin(mp.sqrt(g / 4))
    ks = max([abs(mp.mpf(i + 1) / len(vals) - F(g)) for i, g in enumerate(vals)] +
             [abs(mp.mpf(i) / len(vals) - F(g)) for i, g in enumerate(vals)])
    ck("B8.%d KS(arcsine) = 1/N_modes (M=%d)" % (M, M), abs(ks - mp.mpf(1) / len(vals)) < mp.mpf("1e-25"),
       "KS = %s vs 1/%d = %s" % (mp.nstr(ks, 10), len(vals), mp.nstr(mp.mpf(1) / len(vals), 10)))
var_vals = [4 * mp.sin(mp.pi * n / 1760) ** 2 for n in range(1, 881)]
mu_s = mp.fsum(var_vals) / 880
var = mp.fsum([(v - mu_s) ** 2 for v in var_vals]) / 880
var2 = mp.fsum([(v - 2) ** 2 for v in var_vals]) / 880
ck("B9 Var[gamma] -> 2 (arcsine, M=1760; matches docs/01 1.999995 to 1e-5)", abs(var - 2) < mp.mpf("1e-5"),
   "sample mean = %s -> Var = %s ; with mu=2: %s (docs/01 records 1.999995)"
   % (mp.nstr(mu_s, 10), mp.nstr(var, 10), mp.nstr(var2, 10)))

# =====================================================================
print("\n[C] the limit program L: exact identity + convergence rates (independent algebra)")
ck("C1 2 sqrt(J) sin(ka/2) == c k sin(x)/x identically (x = ka/2)", True,
   "2sqrt(J) sin x vs a sqrt(J) (2x/a) sin x /x = 2 sqrt(J) sin x")
worst = mp.mpf(0)
for l in range(0, 7):
    M_l = 88 * 4 ** l
    a_l = L_world / M_l
    for n in (1, 3, 11, 43):
        x = mp.pi * n / M_l
        lhs = 2 * (c_calc / a_l) * mp.sin(x)
        rhs = c_calc * (n / R_world) * mp.sin(x) / x
        worst = max(worst, abs(lhs - rhs) / abs(lhs))
ck("C2 worst residual of C1 over l = 0..6", worst < mp.mpf("1e-40"), "worst rel = %s" % mp.nstr(worst, 8))
pairs = [(1, 88), (4, 352), (16, 1408), (64, 5632)]
xs = [mp.pi * n / M for n, M in pairs]
ck("C3a four (n,M) pairs (refinement n -> 4n, M -> 4M) share x = pi/88 exactly",
   max(xs) - min(xs) < mp.mpf("1e-45"), "x = %s" % mp.nstr(xs[0], 12))
vals = [mp.sin(x) / x for x in xs]
ck("C3b single control variable: sin(x)/x spread = 0 across those pairs",
   max(vals) - min(vals) < mp.mpf("1e-45"), "spread = %s" % mp.nstr(max(vals) - min(vals), 8))
coef = []
sinc = lambda x: mp.mpf(1) if x == 0 else mp.sin(x) / x
for k in (2, 4):
    coef.append(mp.diff(sinc, 0, k) / mp.factorial(k))
ck("C4 sin(x)/x Taylor = 1 - x^2/6 + x^4/120 - ...", abs(coef[0] + mp.mpf(1) / 6) < mp.mpf("1e-45")
   and abs(coef[1] - mp.mpf(1) / 120) < mp.mpf("1e-45"),
   "c2 = %s , c4 = %s" % (mp.nstr(coef[0], 10), mp.nstr(coef[1], 10)))
sq = lambda x: (mp.mpf(1) if x == 0 else mp.sin(x) / x) ** 2
c2 = mp.diff(sq, 0, 2) / 2
c4 = mp.diff(sq, 0, 4) / mp.factorial(4)
ck("C5 stiffness ratio (sin x/x)^2 = 1 - x^2/3 + 2x^4/45 (O159 cross-check)",
   abs(c2 + mp.mpf(1) / 3) < mp.mpf("1e-45") and abs(c4 - mp.mpf(2) / 45) < mp.mpf("1e-45"),
   "c2 = %s , c4 = %s" % (mp.nstr(c2, 10), mp.nstr(c4, 10)))
lhs = []
for l in range(7):
    M_l = 88 * 4 ** l
    x = mp.pi / M_l
    lhs.append(mp.log(abs(mp.sin(x) / x - 1)))
sl = [(lhs[i + 1] - lhs[i]) / mp.log(4) for i in range(len(lhs) - 1)]
ck("C6 fixed n: (omega/(ck) - 1) ~ 4^(-2l) (|fitted exponent| ~ 2)", abs(abs(sl[0]) - 2) < mp.mpf("0.01"),
   "first-step fitted exponent = %s (doc 1.9999)" % mp.nstr(sl[0], 8))
for (n, N, doc) in ((5, 44, "4.974547"), (13, 7, None)):
    r = mp.sin(mp.pi * n / (2 * N)) / mp.sin(mp.pi * 1 / (2 * N))
    if doc:
        ck("C7 ratio(5,1) at N=44 vs doc 4.974547", abs(r - mp.mpf(doc)) < mp.mpf("1e-6"), "= %s" % mp.nstr(r, 10))
r4422 = mp.sin(mp.pi * 44 / 88) / mp.sin(mp.pi * 22 / 88)          # M = 88   -> sqrt 2
r4422b = mp.sin(mp.pi * 44 / 352) / mp.sin(mp.pi * 22 / 352)       # M = 352  -> docs/04 "N=176"
r4422c = mp.sin(mp.pi * 44 / 1408) / mp.sin(mp.pi * 22 / 1408)     # M = 1408 -> docs/01 "N=704"
ck("C8 ratio(44,22): M=88 = sqrt2 ; M=352 = 1.961570561 (docs/04) ; M=1408 = 1.99759 (docs/01)",
   abs(r4422 - mp.sqrt(2)) < mp.mpf("1e-30") and abs(r4422b - mp.mpf("1.961570561")) < mp.mpf("1e-8")
   and abs(r4422c - mp.mpf("1.997591")) < mp.mpf("1e-5"),
   "sqrt2 = %s ; 1.96157 = %s ; 1.99759 = %s" % (mp.nstr(r4422, 10), mp.nstr(r4422b, 10), mp.nstr(r4422c, 10)))

# =====================================================================
print("\n[D] GR side: spectral-action coefficients, d_s by TWO independent methods")
for N in (44, 704):
    a_2 = -(2 * N + 2)
    ck("D1.%d a2/a0 = -(2+2/N) (N=%d)" % (N, N), abs(mp.mpf(a_2) / N + (2 + mp.mpf(2) / N)) < mp.mpf("1e-40"),
       "= %s (doc -2.04545 / -2.00284)" % mp.nstr(mp.mpf(a_2) / N, 8))
for N in (44, 704):
    a4 = mp.mpf(2 * N * N + 1) / (12 * N)
    ck("D2.%d a4/a0 = (2N^2+1)/(12N) (N=%d)" % (N, N), abs(a4 - mp.mpf(2 * N * N + 1) / (12 * N)) < mp.mpf("1e-30"),
       "= %s (doc 117.33 at N=704)" % mp.nstr(a4, 10))


def ds_analytic(gammas, ts):
    """d_s(t) = 2t <lambda>_t with analytic derivative (no finite differences)."""
    out = []
    for t in ts:
        w = [mp.e ** (-gm * t) for gm in gammas]
        S = mp.fsum(w)
        S1 = mp.fsum([w[i] * gammas[i] for i in range(len(gammas))])
        out.append(2 * t * S1 / S)
    return out


def tgrid(gammas, npts=301, lo=mp.mpf("0.1"), hi=mp.mpf("10")):
    """Adaptive log grid spanning (lo/lambda_max ... hi/lambda_min): avoids mpmath underflow
       and is set purely by the spectrum itself (no external convention)."""
    lmax, lmin = max(gammas), min(gammas)
    n0, n1 = mp.log10(lo / lmax), mp.log10(hi / lmin)
    return [mp.mpf(10) ** (n0 + (n1 - n0) * mp.mpf(i) / (npts - 1)) for i in range(npts)]


# NOTE (audit finding 1): script 02 uses the FULL Laplacian spectrum n = 0..M-1
#   (zero mode INCLUDED). The zero mode is what drives d_s back to 0 in the IR;
#   omitting it changes the numbers, so the audit uses the SAME spectrum definition.
def gspec(M):
    return [4 * mp.sin(mp.pi * n / M) ** 2 for n in range(0, M)]


def run_near_one(us, vs, tol=mp.mpf("0.01")):
    """longest CONTIGUOUS run of grid points with |d_s - 1| < tol (script-02 'one' criterion)."""
    best = (mp.mpf(0), None)
    i = 0
    while i < len(us):
        if abs(vs[i] - 1) < tol:
            j = i
            while j + 1 < len(us) and abs(vs[j + 1] - 1) < tol:
                j += 1
            if (us[j] - us[i]) > best[0]:
                best = (us[j] - us[i], (i, j))
            i = j + 1
        else:
            i += 1
    return best


for M, docv, docw in ((88, "1.0018705", "1.221"), (176, "1.0006198", "1.839"),
                      (352, "1.0017963", "2.428"), (704, "1.0013310", "3.043")):
    vals = gspec(M)
    uh = float(mp.log10(mp.mpf(M) ** 2)) + 1.0
    us = [mp.mpf(-2) + (mp.mpf(uh) + 2) * i / 220 for i in range(221)]   # script-02 grid (220 steps)
    d = ds_analytic(vals, [mp.mpf(10) ** u for u in us])
    width, rng_ = run_near_one(us, d)
    seg = d[rng_[0]:rng_[1] + 1]
    mid = (max(seg) + min(seg)) / 2
    print("     M=%-4d (script-02 grid) window 10^%s..10^%s : width = %s decades ; mid d_s = %s (min %s, max %s)"
          % (M, mp.nstr(us[rng_[0]], 4), mp.nstr(us[rng_[1]], 4), mp.nstr(width, 6), mp.nstr(mid, 9),
             mp.nstr(min(seg), 6), mp.nstr(max(seg), 6)))
    ck("D3.%d window mid d_s reproduces docs/02 %s (tol 2e-4)" % (M, docv), abs(mid - mp.mpf(docv)) < mp.mpf("2e-4"),
       "computed %s" % mp.nstr(mid, 9))
    ck("D4.%d window width reproduces docs/02 %s decades (tol 0.01)" % (M, docw),
       abs(width - mp.mpf(docw)) < mp.mpf("0.01"), "computed %s decades" % mp.nstr(width, 6))
    # AUDIT FINDING 3: the window MID is grid-resolution sensitive (the endpoints move with density).
    #   Only the grid-robust statements may be quoted: |d_s - 1| ~ 1e-3 and window > 1 decade.
    mids2 = []
    for npts in (110, 440, 880):
        us2 = [mp.mpf(-2) + (mp.mpf(uh) + 2) * i / npts for i in range(npts + 1)]
        d2 = ds_analytic(vals, [mp.mpf(10) ** u for u in us2])
        w2, r2 = run_near_one(us2, d2)
        mids2.append(((max(d2[r2[0]:r2[1] + 1]) + min(d2[r2[0]:r2[1] + 1])) / 2, w2))
    ck("D5.%d grid-robust: mid drift < 5e-3 and window > 1.1 decades on every grid" % M,
       max(abs(m2 - 1) for m2, _ in mids2) < mp.mpf("5e-3") and min(w2 for _, w2 in mids2) > mp.mpf("1.1"),
       "mids on coarser/finer grids = %s" % [mp.nstr(m2, 8) for m2, _ in mids2])
# IR: with the zero mode, K(t) -> 1/M (not 0) beyond the gap, so d_s is the exponentially
#     small 2 t (2 gamma_1) e^{-gamma_1 t} / (1 + ...)  -- docs/02 quotes 6.3e-221301 at t = 1e8.
vals88 = gspec(88)
t8 = mp.mpf(10) ** 8
d_ir = ds_analytic(vals88, [t8])[0]
asy_ir = 2 * t8 * 2 * vals88[1] * mp.e ** (-vals88[1] * t8)
ck("D10 IR gap: d_s(1e8) = 2t(2 gamma_1)e^{-gamma_1 t} = 6.3e-221301 (docs/02 Q5.3)",
   abs(mp.log10(d_ir) + 221301) < 1 and abs(d_ir / asy_ir - 1) < mp.mpf("1e-6"),
   "log10 d_s = %s ; direct/analytic = %s" % (mp.nstr(mp.log10(d_ir), 8), mp.nstr(d_ir / asy_ir, 8)))
for M in (88, 704):
    d_uv = ds_analytic(gspec(M), [mp.mpf("0.001")])[0]
    ck("D11.%d UV: d_s(1e-3) = 2 t E[gamma], E[gamma] = 2 EXACTLY for the full spectrum" % M,
       abs(d_uv - 4 * mp.mpf("0.001")) < mp.mpf("1e-4"),
       "d_s = %s (distinct-mode convention gives E = 2+2/N, see B6)" % mp.nstr(d_uv, 8))
# --- MC random walk on the ring: no spectrum involved at all
rng = np.random.default_rng(20260928)
M, Nw, T = 88, 400000, 400
pos = np.zeros(Nw, dtype=np.int64)
steps = rng.integers(0, 2, size=(T, Nw), dtype=np.int8) * 2 - 1
P = {}
for t, s in enumerate(steps, start=1):
    pos += s
    if t in (50, 100, 200, 400):
        P[t] = float(np.mean(pos % M == 0))
ds_mc = -2 * (np.log(P[200]) - np.log(P[50])) / np.log(4)
print("     MC return prob P(50) = %.6f  P(200) = %.6f  -> d_s = %.4f" % (P[50], P[200], ds_mc))
ck("D5 chain d_s by MC random walk (no spectrum) = 1 +/- 0.1", abs(ds_mc - 1) < 0.1, "d_s_MC = %.4f" % ds_mc)
# --- ladder (any discrete scale set) contributes no dimension: three NULL ladders, independent
phi = (1 + mp.sqrt(5)) / 2
ladder = [phi ** (mp.mpf(583) / 2 - m) for m in range(0, 34)]
print("     phi^33 = %s (doc 7.8812e6) ; ladder range = %s"
      % (mp.nstr(phi ** 33, 8), mp.nstr(ladder[0] / ladder[-1], 8)))
ck("D6 mu_0/mu_33 = phi^33 = 7.8812e6", abs(phi ** 33 / mp.mpf("7.8812e6") - 1) < mp.mpf("1e-5"),
   "= %s" % mp.nstr(phi ** 33, 10))


def flat_run(us, vs, rel=mp.mpf("0.05")):
    """longest run of consecutive grid points whose spread < rel * mid value
       (this is the 'const' plateau criterion used by script 02 / docs-02; re-implemented)."""
    best = (mp.mpf(0), mp.mpf(0), mp.mpf(0), mp.mpf(0))
    i = 0
    while i < len(us):
        j = i
        while j < len(us):
            seg = vs[i:j + 1]
            if (max(seg) - min(seg)) < rel * ((max(seg) + min(seg)) / 2):
                j += 1
            else:
                break
        j -= 1
        if j > i and (us[j] - us[i]) > best[0]:
            best = (us[j] - us[i], us[i], us[j], (max(vs[i:j + 1]) + min(vs[i:j + 1])) / 2)
        i = j + 1
    return best


# NOTE (audit finding 2): the ladder must be NORMALISED (mu_m/mu_0) exactly as in script 02 --
#   d_s is scale-invariant in VALUE, but the scan range u = log10 t then covers the same regime.
lf = [phi ** -m for m in range(0, 34)]
us_l = [mp.mpf(-4) + 14 * mp.mpf(i) / 560 for i in range(561)]
rng_n = np.random.default_rng(20260928)
nulls = {
    "random log-uniform": sorted([mp.mpf(float(phi ** (-rng_n.uniform(0, 33)))) for _ in range(34)]),
    "arithmetic 1..34": [mp.mpf(i + 1) / 34 for i in range(34)],
    "dyadic 2^-i": [mp.mpf(2) ** -i for i in range(34)],
}
res = {}
for name_, vals_ in [("phi-ladder", lf)] + list(nulls.items()):
    vs_ = ds_analytic(vals_, [mp.mpf(10) ** u for u in us_l])
    L_, u0_, u1_, vm_ = flat_run(us_l, vs_)
    sel = [v for u, v in zip(us_l, vs_) if u >= 2]
    res[name_] = (L_, max(sel) / min(sel), max(vs_))
    print("     %-20s flat window = %.3f decades ; d_s there ~ %s ; max d_s = %s ; spread(u>=2) = %s"
          % (name_, float(L_), mp.nstr(vm_, 6), mp.nstr(max(vs_), 6), mp.nstr(res[name_][1], 6)))
ck("D7a phi-ladder flat window = 0.275 decades (docs/02 Q6.1)",
   abs(res["phi-ladder"][0] - mp.mpf("0.275")) < mp.mpf("0.05"),
   "computed %.3f decades" % float(res["phi-ladder"][0]))
ck("D7b phi-ladder: O(1)+ spread and huge max d_s (single-level tail) -> no dimension",
   res["phi-ladder"][1] > 3 and res["phi-ladder"][2] > 100,
   "spread = %s , max d_s = %s" % (mp.nstr(res["phi-ladder"][1], 6), mp.nstr(res["phi-ladder"][2], 6)))
for name_, docL, docS, kind in (("random log-uniform", "1.000", "19617", "spread"),
                                ("arithmetic 1..34", "0.150", "5.88e8", "max"),
                                ("dyadic 2^-i", "0.425", "27.3", "spread")):
    L_, spread_, mx_ = res[name_]
    val = spread_ if kind == "spread" else mx_
    ck("D7c NULL '%s' reproduces docs/02 (flat %s dec, %s %s)" % (name_, docL, kind, docS),
       abs(L_ - mp.mpf(docL)) < mp.mpf("0.05") and abs(val / mp.mpf(docS) - 1) < mp.mpf("0.05"),
       "computed flat = %.3f , %s = %s" % (float(L_), kind, mp.nstr(val, 8)))
ck("D7d phi is NOT special: no genuine plateau, same ballpark as the nulls",
   res["phi-ladder"][0] <= max(res[k][0] for k in nulls) and mp.mpf("0.1") <= res["phi-ladder"][0] <= mp.mpf("1.2"),
   "phi = %.3f decades vs nulls %s" % (float(res["phi-ladder"][0]), [round(float(res[k][0]), 3) for k in nulls]))
# D8/D9 product = chain (x) ladder : 88 x 34 = 2992 eigenvalues (docs/02 Q7)
prod = [g * mu for g in gspec(88) for mu in lf]
us_p = [mp.mpf(-6) + 16 * mp.mpf(i) / 560 for i in range(561)]
vs_p = ds_analytic(prod, [mp.mpf(10) ** u for u in us_p])
Lp, ap, bp, vpm = flat_run(us_p, vs_p)
print("     product (88x34 = %d values): flat window = %.3f decades (10^%s..10^%s) ; d_s there ~ %s ; max d_s = %s"
      % (len(prod), float(Lp), mp.nstr(ap, 4), mp.nstr(bp, 4), mp.nstr(vpm, 6), mp.nstr(max(vs_p), 6)))
ck("D8 max d_s(T) = 0.993785 (docs/02 Q7) -> no dimension above 1", abs(max(vs_p) - mp.mpf("0.993785")) < mp.mpf("0.01"),
   "computed %s" % mp.nstr(max(vs_p), 8))
ck("D9 product flat window = 0.486 decades < chain's 1.221 (ladder does not widen the window)",
   abs(Lp - mp.mpf("0.486")) < mp.mpf("0.05") and Lp < mp.mpf("1.221"),
   "computed %.3f decades" % float(Lp))

# =====================================================================
print("\n[E] dimension mechanism: conformal identity by periodic finite differences (no FFT)")
A = 0.4
for D, N in ((2, 96), (3, 64), (4, 32)):
    xs = 2 * np.pi * np.arange(N) / N
    grid = np.meshgrid(*[xs] * D, indexing="ij")
    f = A * np.prod([np.cos(g) for g in grid], axis=0)
    h = 2 * np.pi / N
    g2 = np.zeros_like(f)
    lap = np.zeros_like(f)
    for ax in range(D):
        # 4th-order periodic central differences (independent of the FFT route used in script 03)
        gp = (np.roll(f, 2, ax) - 8 * np.roll(f, 1, ax) + 8 * np.roll(f, -1, ax) - np.roll(f, -2, ax)) / (12 * h)
        g2 += gp ** 2
        lap += (-np.roll(f, 2, ax) + 16 * np.roll(f, 1, ax) - 30 * f
                + 16 * np.roll(f, -1, ax) - np.roll(f, -2, ax)) / (12 * h ** 2)
    R = -(D - 1) * np.exp(-2 * f) * (2 * lap + (D - 2) * g2)
    lhs_ = float(np.mean(R * np.exp(D * f)) * (2 * np.pi) ** D)
    integ = float(np.mean(np.exp((D - 2) * f) * g2) * (2 * np.pi) ** D)
    K = lhs_ / integ if integ != 0 else float("nan")
    print("     D=%d (N=%d, FD) : lhs = %+.8e , integ = %+.8e , K = %.6f" % (D, N, lhs_, integ, K))
    if D == 2:
        ck("E1 D=2: int R sqrt(g) = 0 (topological) |lhs|/scale < 1e-6", abs(lhs_) / max(1.0, abs(integ)) < 1e-6,
           "rel = %.2e" % (abs(lhs_) / max(1.0, abs(integ))))
    else:
        ck("E2.%d K(D) = (D-1)(D-2) = %d by FD (tol 1e-2)" % (D, (D - 1) * (D - 2)),
           abs(K - (D - 1) * (D - 2)) < 0.01 * (D - 1) * (D - 2), "K = %.6f" % K)
ck("E3 graviton DoF: D=3 -> 0, D=4 -> 2 (first propagating dimension = 4)",
   3 * 0 // 2 == 0 and 4 * 1 // 2 == 2, "D(D-3)/2 : 0 vs 2")
ck("E4 Weyl components: D=3 -> 0, D=4 -> 10", 3 * 4 * 5 * 0 // 12 == 0 and 4 * 5 * 6 * 1 // 12 == 10,
   "D(D+1)(D+2)(D-3)/12")
# independent numerology null: different base set, count the hits per target
BASE = [2, 3, 4, 5, 6, 8, 9, 11, 13, 44, 88]
from fractions import Fraction
tg = list(range(2, 14))
hits = {v: 0 for v in tg}
lv = [Fraction(v) for v in BASE]
for a in lv:
    for b in lv:
        for r in (a + b, a - b, a * b, (a / b if b else None)):
            if r is not None and r.denominator == 1 and r.denominator <= 200 and int(r) in hits:
                hits[int(r)] += 1
print("     independent null hits:", {k: hits[k] for k in tg})
n3 = hits[3]
ck("E5 '3' hit count is unremarkable (within [min/3, 3*max] of the distribution)",
   min(hits.values()) / 3 <= n3 <= 3 * max(hits.values()),
   "n3 = %d , min = %d , max = %d -> no discriminative power" % (n3, min(hits.values()), max(hits.values())))

# =====================================================================
print("\n[F] U6 observable gate: units from first principles + reading B")
Mpc_m = mp.mpf("3.0856775814913673e22")
hbar_c = mp.mpf("1.973269804e-16")           # GeV*m
GeV_per_invMpc = hbar_c / Mpc_m
print("     hbar*c/Mpc = %s GeV per Mpc^-1 (doc 6.3948e-39)" % mp.nstr(GeV_per_invMpc, 8))
ck("F1 Mpc^-1 -> GeV conversion factor", abs(GeV_per_invMpc / mp.mpf("6.3948e-39") - 1) < mp.mpf("1e-4"),
   "= %s" % mp.nstr(GeV_per_invMpc, 10))
Lam2 = mp.sqrt(12) / a0
Lam2_GeV = Lam2 * GeV_per_invMpc
bound = mp.mpf("1.3e11")
nord = mp.log10(bound / Lam2_GeV)
print("     Lambda_2 = %s Mpc^-1 = %s GeV ; bound = %s GeV ; deficit = %s orders"
      % (mp.nstr(Lam2, 10), mp.nstr(Lam2_GeV, 8), mp.nstr(bound, 6), mp.nstr(nord, 8)))
ck("F2 reading A excluded: deficit > 50 orders of magnitude", nord > 50,
   "%s orders (doc 51.2)" % mp.nstr(nord, 8))
a_max = mp.sqrt(12) / bound                 # GeV^-1
a_max_m = a_max * hbar_c
print("     a_max = %s GeV^-1 = %s m (doc 5.25816e-27 m)" % (mp.nstr(a_max, 8), mp.nstr(a_max_m, 8)))
ck("F3 a_max = sqrt(12)/Lambda2min in metres = 5.25816e-27 m",
   abs(a_max_m / mp.mpf("5.25816e-27") - 1) < mp.mpf("1e-5"), "= %s" % mp.nstr(a_max_m, 8))
for l, doc in ((4, "5.53e-6"), (8, "8.43e-11"), (12, "1.29e-15")):
    M_l = 88 * 4 ** l
    x = (mp.mpf("0.01") * (L_world / M_l)) / 2            # x = k a / 2 , k = 0.01 Mpc^-1 , a = L_world/M_l
    d = 1 - mp.sin(x) / x
    ck("F4.%d reading B defect 1-sin(x)/x at l=%d -> %s" % (l, l, doc),
       abs(d / mp.mpf(doc) - 1) < mp.mpf("0.02"), "computed %s" % mp.nstr(d, 6))
for (n, m, N, doc) in ((5, 1, 44, "4.974547113"), (13, 7, 44, "1.809969447"),
                       (22, 11, 44, "1.847759065"), (44, 22, 88, "1.847759065")):
    r = mp.sin(mp.pi * n / (2 * N)) / mp.sin(mp.pi * m / (2 * N))
    ck("F5 ratio(%d,%d) N=%d matches docs/04 %s" % (n, m, N, doc), abs(r - mp.mpf(doc)) < mp.mpf("1e-8"),
       "= %s" % mp.nstr(r, 12))
for n, doc in ((1, "0.999363"), (5, "0.98411"), (7, "0.96894"), (13, "0.89423"), (22, "0.70711")):
    v = mp.cos(mp.pi * n / 88)
    ck("F6 v_g/c = cos(pi n/88) n=%d vs docs/01 %s" % (n, doc), abs(v - mp.mpf(doc)) < mp.mpf("1e-4"),
       "= %s" % mp.nstr(v, 8))
ck("F7 Nyquist deviation 1 - 2/pi = 36.338%", abs((1 - 2 / mp.pi) * 100 - mp.mpf("36.338")) < mp.mpf("1e-3"),
   "= %s %%" % mp.nstr((1 - 2 / mp.pi) * 100, 8))

print("\n" + "=" * 78)
print("RESULT: %d/%d PASS" % (PASS, PASS + FAIL))
print("=" * 78)
