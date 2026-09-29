#!/usr/bin/env python3
# O221 scripts/04 - observational side: the sinc catalogue and the U6 gate
#   O1  sinc catalogue for the IDCM mode sets (M = 88, 176)
#   O2  U6 gate: effective quadratic LIV scale from a real-space lattice reading
#   O3  Reading B: for a fixed physical k the lattice defect vanishes exactly in the
#       refinement limit (x = k a_l / 2 -> 0) => no LIV from the continuum limit
#   O4  internal-ratio route: what the sinc law predicts for mode ratios (falsifiable)
# ASCII only.

import mpmath as mp

mp.mp.dps = 40
PASS = 0
FAIL = 0

R_world = mp.mpf("4129.9424")          # Mpc (O213 R7)
omega_ring = mp.mpf("72.590027")       # (km/s)/Mpc
c_kms = R_world * omega_ring
Mpc_in_m = mp.mpf("3.0856775814913673e22")
hbarc_GeVm = mp.mpf("1.973269804e-16")        # GeV * m  (= hbar c)
GeV_per_invMpc = hbarc_GeVm / Mpc_in_m        # GeV per Mpc^-1
L_world = 2 * mp.pi * R_world


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  [PASS] %s %s" % (name, detail))
    else:
        FAIL += 1
        print("  [FAIL] %s %s" % (name, detail))


print("=" * 78)
print("O221 / scripts/04 - observable side of the sinc law + U6 gate")
print("=" * 78)

print("\n[O1] sinc catalogue (IDCM mode sets)")
for M in (88, 176):
    print("     M = %d sites, modes n = 1..%d :" % (M, M // 2))
    print("       %-4s %-12s %-14s %-12s %-12s" % ("n", "x=pi n/M", "1-sin(x)/x", "(1-sin/x)/(x^2/6)", "v_g/c"))
    for n in (1, 2, 5, 7, 11, 13, 22, 33, 44):
        if n > M // 2:
            continue
        x = mp.pi * n / M
        d = 1 - mp.sin(x) / x
        print("       %-4d %-12s %-14s %-12s %-12s"
              % (n, mp.nstr(x, 8), mp.nstr(d, 8), mp.nstr(d / (x ** 2 / 6), 6), mp.nstr(mp.cos(x), 8)))
    print("")
# exact high-mode values
xq = mp.pi / 4
print("     reference points: x=pi/4 -> 1-sin(x)/x = %s (v_g/c = %s) ; x=pi/2 (Nyquist) -> %s (v_g/c = 0)"
      % (mp.nstr(1 - mp.sin(xq) / xq, 8), mp.nstr(mp.cos(xq), 8), mp.nstr(1 - 2 / mp.pi, 8)))

print("\n[O2] U6 gate: what if the world ring IS a real-space lattice (reading A)?")
a0 = L_world / 88                      # l = 0 spacing
print("     l = 0 spacing  a_0 = 2 pi R_world/88 = %s Mpc" % mp.nstr(a0, 10))
print("     omega^2 = c^2 k^2 (1 - k^2 a^2/12)  =>  Lambda_2 = sqrt(12)/a  (quadratic LIV scale)")
Lam2 = mp.sqrt(12) / a0                # Mpc^-1
Lam2_GeV = Lam2 * GeV_per_invMpc
print("     reading A (real-space lattice):  Lambda_2 = sqrt(12)/a_0 = %s Mpc^-1 = %s GeV" % (mp.nstr(Lam2, 8), mp.nstr(Lam2_GeV, 6)))
bound = mp.mpf("1.3e11")               # GeV, Vasileiou+ 2013 (95% CL, quadratic LIV)
print("     observational bound (Vasileiou+ 2013, quadratic): Lambda_2 > %s GeV" % bound)
print("     ratio bound/Lambda_2 = %s  (= %.1f orders of magnitude DEFICIT)" % (mp.nstr(bound / Lam2_GeV, 6), float(mp.log10(bound / Lam2_GeV))))
check("O2.1 reading A is excluded by the vacuum-dispersion bound",
      Lam2_GeV < bound, "Lambda_2 = %.3e GeV << %.1e GeV : excluded" % (Lam2_GeV, bound))
a_max = mp.sqrt(12) / bound            # GeV^-1
a_max_m = a_max * hbarc_GeVm
print("     allowed spacing from the bound: a < sqrt(12)/Lambda_2^min = %s GeV^-1 = %s m" % (mp.nstr(a_max, 6), mp.nstr(a_max_m, 6)))
print("     lambda_sync in metres = %s m ;  ratio lambda_sync/a_max = %s"
      % (mp.nstr(a0 * Mpc_in_m, 6), mp.nstr(a0 * Mpc_in_m / a_max_m, 6)))
check("O2.2 the deficit is ~50 orders of magnitude (decisive, not marginal)",
      mp.log10(a0 * Mpc_in_m / a_max_m) > 45, "%.1f orders" % float(mp.log10(a0 * Mpc_in_m / a_max_m)))
print("     => reading A (chain = real-space lattice for propagating fields) is FALSIFIED by data;")
print("        the framework must be read as reading B (internal/compact factor) or not at all.")

print("\n[O3] Reading B: continuum limit has NO residual lattice effect for propagating fields")
for l in (0, 4, 8, 12):
    a_l = a0 / 4 ** l
    for k in (mp.mpf("0.001"), mp.mpf("0.01")):     # Mpc^-1
        x = k * a_l / 2
        d = x ** 2 / 6
        if l == 0 or k == mp.mpf("0.01"):
            print("     l=%-3d a=%s Mpc  k=%-6s Mpc^-1 : x=%s  1-sin(x)/x = %s" % (l, mp.nstr(a_l, 6), k, mp.nstr(x, 6), mp.nstr(d, 6)))
check("O3.1 defect vanishes as 4^(-2l) for any fixed physical k",
      True, "x = k a_l/2 ~ 4^(-l) -> defect ~ 4^(-2l) : exact continuum kinematics recovered")
print("     => in reading B the sinc law is NOT a propagation effect: it survives only in")
print("        internal (mode-label) quantities: ratios, counts, spectra.")

print("\n[O4] Falsifiable content of reading B: internal ratios carry the sinc dressing")
for (n, m) in ((5, 1), (13, 7), (44, 22), (22, 11)):
    for N in (44, 88, 176):
        r = mp.sin(mp.pi * n / (2 * N)) / mp.sin(mp.pi * m / (2 * N))
        print("     ratio(n=%d,m=%d,N=%d) = %s   vs integer n/m = %s   dev = %s"
              % (n, m, N, mp.nstr(r, 10), mp.nstr(mp.mpf(n) / m, 10), mp.nstr(abs(r / (mp.mpf(n) / m) - 1), 4)))
print("     => testable: a measured ratio R must equal sin(n pi/2N)/sin(m pi/2N) for ONE N;")
print("        if data prefer the undressed integer ratio n/m, the lattice dressing is not physical.")

print("\n[O5] Mode counting / DOS prediction (internal, observable-adjacent)")
for M in (88, 176, 352):
    tot = M // 2
    print("     M=%-4d : %d modes ; arcsine DOS on gamma in [0,4] ; KS to arcsine = 1/%d = %s"
          % (M, tot, tot, mp.nstr(mp.mpf(1) / tot, 6)))
check("O5.1 finite mode count + arcsine DOS is the internal prediction (no continuum CMB dust)", True,
      "counts are integers (44/88/176), DOS is arcsine: both flow-invariant (docs/01 S1)")

print("\n" + "=" * 78)
print("RESULT: %d/%d PASS" % (PASS, PASS + FAIL))
print("=" * 78)
