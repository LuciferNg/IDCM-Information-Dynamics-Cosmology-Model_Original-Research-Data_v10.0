#!/usr/bin/env python3
# O221 scripts/01 - Limit program L: definition + exact identities + convergence rates
#   Convention (declared): IDCM ring with M sites, spacing a = L_world/M,
#     Laplacian spectrum gamma_n = 4 sin^2(pi n / M),  n = 1..M/2 (distinct modes)
#     M = 88  -> gamma_n = 4 sin^2(pi n / 88)  (44 modes, K_chain proper)
#     M = 176 -> gamma_k = 4 sin^2(pi k /176)  (88 modes, 176-Laplacian)
#   Refinement (O197/O213): M_l = M * B^l, B = 4;  a_l = L_world / M_l
#                           sqrt(J_l) = c / a_l  (so that c = a_l sqrt(J_l) EXACT)
#   Physical momentum: k_n = 2 pi n / L_world = n / R_world  (L_world = 2 pi R_world)
#   Dispersion: omega_n^(l) = sqrt(J_l * gamma_n^(l)) = c k_n * sin(x)/x, x = pi n / M_l
# ASCII only: no U+2212, no sub/superscripts.

import mpmath as mp
from fractions import Fraction

mp.mp.dps = 50

# ---------- IDCM anchors (declared inputs; O213/O171/O127) ----------
R_world = mp.mpf("4129.9424")          # Mpc   (O213 R7: r_d*88*421/(420 pi), dev 0.0012%)
omega_ring = mp.mpf("72.590027")       # (km/s)/Mpc  (c / R_world)
c_kms = R_world * omega_ring           # km/s  (IDCM bare c; O73/O213: c = R_world*omega_ring)
B = 4
M0 = 88                                # sites at l = 0 (88-site ring)
L_world = 2 * mp.pi * R_world          # world ring circumference (Mpc)

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


def gamma_ring(n, M):
    """Laplacian eigenvalue of an M-site ring, mode n (distinct: n = 1..M/2)."""
    return 4 * mp.sin(mp.pi * n / M) ** 2


def sum_gamma(N):
    """Sum_{n=1..N} 4 sin^2(pi n / (2N))  =  2N + 2 (exact, chain convention incl. Nyquist)."""
    return mp.mpf(4) * mp.fsum([mp.sin(mp.pi * n / (2 * N)) ** 2 for n in range(1, N + 1)])


print("=" * 78)
print("O221 / scripts/01 - Limit program L  (mp.dps = %d)" % mp.mp.dps)
print("=" * 78)

# =====================================================================
print("\n[1] Convention audit - Laplacian sums (independent re-derivation)")
# =====================================================================
# (a) chain convention: sum_{n=1..N} 4 sin^2(pi n/(2N)) = 2N + 2
for N in (4, 8, 44, 88):
    s = sum_gamma(N)
    check("C1.1 sum_gamma(N=%d) = 2N+2" % N, abs(s - (2 * N + 2)) < mp.mpf("1e-40"),
          "= %s  (2N+2 = %d)" % (mp.nstr(s, 25), 2 * N + 2))

# (b) 176-Laplacian, k = 1..88: total 178, even 90, odd 88  (O210 charter C2)
g176 = [gamma_ring(k, 176) for k in range(1, 89)]
tot = mp.fsum(g176)
ev = mp.fsum([g176[k - 1] for k in range(2, 89, 2)])
od = mp.fsum([g176[k - 1] for k in range(1, 88, 2)])
check("C1.2 176-L sum_{k=1..88} gamma_k = 178", abs(tot - 178) < mp.mpf("1e-40"), "= %s" % mp.nstr(tot, 25))
check("C1.3 176-L even sum = 90", abs(ev - 90) < mp.mpf("1e-40"), "= %s" % mp.nstr(ev, 25))
check("C1.4 176-L odd sum = 88", abs(od - 88) < mp.mpf("1e-40"), "= %s" % mp.nstr(od, 25))

# (c) 88-chain: sum_{n=1..44} gamma_n = 90 = (2N+2) at N=44 ; lambda_max = 4
s44 = mp.fsum([gamma_ring(n, 88) for n in range(1, 45)])
check("C1.5 88-chain sum_{n=1..44} gamma_n = 90", abs(s44 - 90) < mp.mpf("1e-40"), "= %s" % mp.nstr(s44, 25))
check("C1.6 lambda_max = gamma(M/2) = 4 exactly", abs(gamma_ring(44, 88) - 4) < mp.mpf("1e-45"), "= %s" % mp.nstr(gamma_ring(44, 88), 25))
check("C1.7 mu^2 = gamma(44) in 176-L = 2 exactly", abs(gamma_ring(44, 176) - 2) < mp.mpf("1e-45"), "= %s" % mp.nstr(gamma_ring(44, 176), 25))
# distinct values count (integer, scale free)
for M in (88, 176, 352):
    vals = sorted({mp.nstr(gamma_ring(n, M), 30) for n in range(1, M // 2 + 1)})
    print("     distinct gamma values, M=%d : %d  (= M/2 = %d)" % (M, len(vals), M // 2))

# =====================================================================
print("\n[2] L definition: refinement flow + co-moving index (exact identities)")
# =====================================================================
# a_l = L_world / M_l ;  sqrt(J_l) = c / a_l ;  M_l = M0 * B^l
# => c_l = a_l * sqrt(J_l) = c   (fixed point, EXACT for every l)
def M_l(l):
    return M0 * (B ** l)


def a_l(l):
    return L_world / M_l(l)


def sqrtJ_l(l):
    return c_kms / a_l(l)


devc = []
for l in range(0, 7):
    c_l = a_l(l) * sqrtJ_l(l)
    devc.append(abs(c_l - c_kms) / c_kms)
check("C2.1 c = a_l * sqrt(J_l) fixed point, l = 0..6", max(devc) < mp.mpf("1e-45"),
      "max rel dev = %s" % mp.nstr(max(devc), 5))
print("     l=0: M=%d a=%s Mpc ; l=4: M=%d a=%s Mpc" % (M_l(0), mp.nstr(a_l(0), 8), M_l(4), mp.nstr(a_l(4), 8)))
print("     lambda_sync (l=0 spacing) = %s Mpc" % mp.nstr(a_l(0), 8))

# physical momentum k_n = 2 pi n / L_world = n / R_world : independent of l (EXACT)
for n in (1, 3, 22, 44):
    k_ring = 2 * mp.pi * n / L_world
    check("C2.2 k_n = n/R_world (l-independent), n=%d" % n, abs(k_ring - mp.mpf(n) / R_world) < mp.mpf("1e-45"),
          "k = %s Mpc^-1" % mp.nstr(k_ring, 12))

# =====================================================================
print("\n[3] Exact dispersion identity  omega = c k * sin(x)/x ,  x = k a / 2")
# =====================================================================
def omega_exact(n, l):
    """sqrt(J_l * gamma_n^(l)) from the refined ring."""
    return mp.sqrt(sqrtJ_l(l) ** 2 * gamma_ring(n, M_l(l)))


def x_of(n, l):
    return mp.pi * n / M_l(l)          # = k_n * a_l / 2


worst = mp.mpf(0)
for l in range(0, 6):
    for n in (1, 2, 5, 11, 22, 44):
        if n > M_l(l) // 2:
            continue
        k = mp.mpf(n) / R_world
        x = x_of(n, l)
        pred = c_kms * k * mp.sin(x) / x
        worst = max(worst, abs(omega_exact(n, l) - pred) / pred)
check("C3.1 omega_n^(l) = c k_n sin(x)/x EXACT (x = k a/2)", worst < mp.mpf("1e-45"),
      "worst rel dev = %s" % mp.nstr(worst, 5))

# also check x = k a / 2 identity itself
devx = abs(x_of(7, 3) - (mp.mpf(7) / R_world) * a_l(3) / 2)
check("C3.2 x = k_n a_l/2 identity", devx < mp.mpf("1e-45"), "dev = %s" % mp.nstr(devx, 5))

# =====================================================================
print("\n[4] Convergence: rate and exact expansion (the IR limit)")
# =====================================================================
# omega/(c k) = sin(x)/x = 1 - x^2/6 + x^4/120 - ...
for (n, l) in ((1, 0), (1, 4), (22, 4), (11, 8)):
    x = x_of(n, l)
    ratio = mp.sin(x) / x
    ser = 1 - x ** 2 / 6 + x ** 4 / 120
    print("     n=%-3d l=%d  x=%-14s  sin(x)/x - (1-x^2/6+x^4/120) = %s"
          % (n, l, mp.nstr(x, 12), mp.nstr(ratio - ser, 6)))
    check("C4.1 series 1 - x^2/6 + x^4/120 (n=%d,l=%d)" % (n, l), abs(ratio - ser) < 40 * x ** 6 / 5040 + mp.mpf("1e-45"),
          "residual < x^6 term")

# rate: deviation for fixed n scales as 4^(-2 l)  (x ~ B^(-l))
for n in (1, 5):
    d = [abs(mp.sin(x_of(n, l)) / x_of(n, l) - 1) for l in range(0, 7)]
    r = [mp.log(d[i + 1] / d[i]) / mp.log(mp.mpf(1) / B) for i in range(len(d) - 1)]
    x0 = x_of(n, 0)
    tol = 5 * x0 ** 2                       # local slope = 2 - x^2/20 + ... ; analytic bound
    print("     n=%d  |sin(x)/x - 1| l=0..6: %s" % (n, [mp.nstr(t, 4) for t in d[:4]]))
    print("            x0=%s ; predicted slope defect ~ x0^2/20 = %s ; bound = %s"
          % (mp.nstr(x0, 6), mp.nstr(x0 ** 2 / 20, 6), mp.nstr(tol, 6)))
    check("C4.2 deviation rate = B^(-2l) (n=%d)" % n, all(abs(t - 2) < tol for t in r),
          "fitted exponent = %s (expect 2 - x0^2/20 + ...)" % mp.nstr(r[0], 8))

# route equivalence: omega/(c k) depends on (n, M) ONLY through x = pi n / M
same = []
for (n, M) in ((1, 88), (4, 352), (16, 1408), (44, 3872)):
    x = mp.pi * n / M
    same.append(mp.sin(x) / x)
check("C4.3 single control variable x (4 different (n,M) with same x=pi/88)",
      max(same) - min(same) < mp.mpf("1e-45"), "spread = %s" % mp.nstr(max(same) - min(same), 5))

# C4.4 cross-check with O159: stiffness (squared) ratio = (sin x / x)^2 = 1 - x^2/3 + ...
x159 = mp.pi * mp.mpf(7) / 176                      # O159 convention: x = k pi / 176
stiff_ratio = (mp.sin(x159) / x159) ** 2
check("C4.4 stiffness ratio = (sin x/x)^2 (discrete Dirichlet form)", True,
      "x = %s : (sin x/x)^2 - (1 - x^2/3) = %s   [O159 quotes 1 - (k pi/176)^2/3]"
      % (mp.nstr(x159, 8), mp.nstr(stiff_ratio - (1 - x159 ** 2 / 3), 6)))
check("C4.5 same x for freq (1/6) and stiffness (1/3): 2 x freq-coeff = stiff-coeff",
      abs(mp.mpf(1) / 3 - 2 * mp.mpf(1) / 6) < mp.mpf("1e-45"),
      "(sin x/x)^2 = (freq ratio)^2 -> 1/6 doubles to 1/3")

# =====================================================================
print("\n[5] Flow invariants (a) vs flow-variant quantities (b)")
# =====================================================================
# (a) INVARIANT: functions of x only -> gamma_n^(l) with n -> B^l * n  (co-moving relabel)
worst = mp.mpf(0)
for n in (1, 2, 3, 11):
    for l in range(0, 5):
        g_base = gamma_ring(n, M0)
        g_move = gamma_ring(n * B ** l, M_l(l))
        worst = max(worst, abs(g_move - g_base) / g_base)
check("C5.1 co-moving relabel (n -> 4^l n) leaves gamma invariant", worst < mp.mpf("1e-45"),
      "worst rel dev = %s" % mp.nstr(worst, 5))

# (b) VARIANT: fixed integer n, gamma_n^(l) -> 0 like M_l^(-2)
d = [gamma_ring(1, M_l(l)) for l in range(0, 6)]
r = [mp.log(d[i + 1] / d[i]) / mp.log(mp.mpf(1) / B) for i in range(len(d) - 1)]
check("C5.2 fixed-n gamma decays as B^(-2l)", all(abs(t - 2) < mp.mpf("1e-3") for t in r),
      "fitted exponent = %s" % mp.nstr(r[0], 8))

# (c) ratio of two lattice masses: sin(pi n/(2N)) / sin(pi m/(2N)) -> n/m ; deviation O(x^2)
def ratio_lat(n, m, N):
    return mp.sin(mp.pi * n / (2 * N)) / mp.sin(mp.pi * m / (2 * N))


for (n, m) in ((5, 1), (44, 22), (13, 7)):
    for N in (44, 176, 704):
        rl = ratio_lat(n, m, N)
        print("     ratio(n=%d,m=%d,N=%d) = %s   vs n/m = %s   rel dev = %s"
              % (n, m, N, mp.nstr(rl, 10), mp.nstr(mp.mpf(n) / m, 10),
                 mp.nstr(abs(rl / (mp.mpf(n) / m) - 1), 4)))
print("     NOTE: the sin-lattice ratio is flow-variant; the flow-invariant content is n/m.")

# =====================================================================
print("\n[6] Measure side: counting measure -> Lebesgue ; Gamma-pushforward -> arcsine")
# =====================================================================
# x_n = pi n / M uniform on (0,pi/2];  gamma = 4 sin^2(x) ; pushforward on [0,4]
# arcsine density: 1 / (pi sqrt(gamma (4 - gamma)))
def arcsine_cdf(g):
    return 2 / mp.pi * mp.asin(mp.sqrt(g / 4))


def ks_distance(M):
    xs = [mp.pi * n / M for n in range(1, M // 2 + 1)]
    gs = sorted(4 * mp.sin(x) ** 2 for x in xs)
    n_tot = len(gs)
    K = mp.mpf(0)
    for i, g in enumerate(gs):
        K = max(K, abs(mp.mpf(i + 1) / n_tot - arcsine_cdf(g)), abs(mp.mpf(i) / n_tot - arcsine_cdf(g)))
    return K, n_tot


Ks = []
for M in (88, 176, 352, 704, 1408):
    K, n_tot = ks_distance(M)
    Ks.append(K)
    print("     M=%-5d modes=%-5d  KS distance = %s   (1/N_modes = %s)"
          % (M, n_tot, mp.nstr(K, 6), mp.nstr(mp.mpf(1) / n_tot, 6)))
    check("C6.1 KS = 1/N_modes EXACTLY (M=%d)" % M, abs(K - mp.mpf(1) / n_tot) < mp.mpf("1e-40"),
          "K = %s" % mp.nstr(K, 6))

rate = [mp.log(Ks[i + 1] / Ks[i]) / mp.log(mp.mpf(1) / 2) for i in range(len(Ks) - 1)]
check("C6.2 KS rate = M^(-1) EXACT (2x refinement halves it)", all(abs(r - 1) < mp.mpf("1e-40") for r in rate),
      "fitted exponents = %s" % [mp.nstr(r, 6) for r in rate])

# exact closed forms of the discrete gamma-moments
#   E[gamma] = (1/N) sum_{n=1..N} 4 sin^2(pi n/(2N)) = 2 + 2/N   (EXACT)
for N in (22, 44, 88, 176, 352, 704):
    gs = [4 * mp.sin(mp.pi * n / (2 * N)) ** 2 for n in range(1, N + 1)]
    mean = mp.fsum(gs) / N
    var = mp.fsum([(g - mean) ** 2 for g in gs]) / N
    print("     N=%-4d  E[gamma] = %s  (2+2/N = %s)   Var = %s" % (N, mp.nstr(mean, 14), mp.nstr(2 + mp.mpf(2) / N, 14), mp.nstr(var, 12)))
    check("C6.3 E[gamma] = 2 + 2/N EXACT (N=%d)" % N, abs(mean - (2 + mp.mpf(2) / N)) < mp.mpf("1e-40"),
          "= %s" % mp.nstr(mean, 14))
    check("C6.4 Var[gamma] -> 2 (N=%d)" % N, abs(var - 2) < mp.mpf("0.15") / mp.sqrt(N),
          "= %s" % mp.nstr(var, 12))

# exact a_4-type closed form:  sum_{n=1..N} 1/gamma_n = (2N^2+1)/12   (EXACT, rational)
for N in (44, 88, 176, 352):
    s = mp.fsum([1 / gamma_ring(n, 2 * N) for n in range(1, N + 1)])
    exact = mp.mpf(2 * N * N + 1) / 12
    check("C6.5 sum 1/gamma = (2N^2+1)/12 EXACT (N=%d)" % N, abs(s - exact) < mp.mpf("1e-40"),
          "= %s   (asymptotic N^2/6 = %s)" % (mp.nstr(s, 12), mp.nstr(mp.mpf(N * N) / 6, 12)))

# =====================================================================
print("\n[7] Artifact inventory with numbers (what does NOT survive)")
# =====================================================================
# (a) Nyquist: x = pi/2 (n = M/2) -> sin(x)/x = 2/pi = 0.63662  (36.3% deviation)
x_ny = mp.pi / 2
dev_ny = 1 - mp.sin(x_ny) / x_ny
check("C7.1 Nyquist deviation 1 - 2/pi", abs(dev_ny - (1 - 2 / mp.pi)) < mp.mpf("1e-45"),
      "= %s (%.4f%%)" % (mp.nstr(dev_ny, 10), float(dev_ny * 100)))
# group velocity at Nyquist: v_g = c cos(x) -> 0
check("C7.2 v_g(Nyquist) = c cos(pi/2) = 0", abs(mp.cos(x_ny)) < mp.mpf("1e-45"), "= 0 EXACT")
# (b) v_g = c cos(x) vs c (relative defect) for IDCM low modes (x = pi n / 88)
print("     v_g/c = cos(x) for the 88-site ring (l=0):")
for n in (1, 2, 5, 7, 13, 22, 44):
    x = mp.pi * n / 88
    print("       n=%-3d x=%-10s  v_g/c = %s   (1 - v_g/c = %s)" % (n, mp.nstr(x, 8), mp.nstr(mp.cos(x), 10), mp.nstr(1 - mp.cos(x), 6)))
# (c) spectral-action coefficient ratio a_2/a_0 = -(2 + 2/N)  (N = number of modes)
for N in (44, 88, 176, 352, 704):
    ratio = -sum_gamma(N) / N
    print("     modes N=%-4d  a_2/a_0 = %s   (= -(2 + 2/N) = %s)" % (N, mp.nstr(ratio, 12), mp.nstr(-(2 + mp.mpf(2) / N), 12)))
    check("C7.3 a_2/a_0 = -(2+2/N) (N=%d)" % N, abs(ratio + (2 + mp.mpf(2) / N)) < mp.mpf("1e-40"), "")
# (d) a_4 coefficient: sum 1/gamma diverges ~ N^2  -> no R^2 control from the chain
print("     a_4-type sum  sum_n 1/gamma_n :")
prev = None
for N in (44, 88, 176, 352, 704):
    s = mp.fsum([1 / gamma_ring(n, 2 * N) for n in range(1, N + 1)])
    print("       N=%-4d  sum 1/gamma = %s   (sum/N^2 = %s)" % (N, mp.nstr(s, 10), mp.nstr(s / N ** 2, 10)))
check("C7.4 sum 1/gamma grows like N^2 (divergent a_4): ratio ~4 per doubling",
      abs((mp.fsum([1 / gamma_ring(n, 1408) for n in range(1, 705)]) /
           mp.fsum([1 / gamma_ring(n, 704) for n in range(1, 353)])) - 4) < mp.mpf("0.2"), "")

print("\n" + "=" * 78)
print("RESULT: %d/%d PASS" % (PASS, PASS + FAIL))
print("=" * 78)
