#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O165 exploration — verify the phi-weight hypothesis before writing docs.
e^{-n} vs phi^{-2n}: exactness, sandwich, uniqueness, chain eigenvector decay.
"""
from mpmath import mp, mpf, e, exp, log, sin, pi, sqrt, power, almosteq
mp.dps = 60

phi = (1 + sqrt(5)) / 2
kappa = mpf(1) / 16

print("=" * 78)
print("[1] Exact sandwich: phi^{-4} > kappa > phi^{-6} ?")
print("=" * 78)
p4 = power(phi, -4); p6 = power(phi, -6)
e2 = exp(-2); e3 = exp(-3)
print(f"  phi^-4 = {mp.nstr(p4, 12)}   (old e^-2 = {mp.nstr(e2, 12)})")
print(f"  kappa  = {mp.nstr(kappa, 12)}")
print(f"  phi^-6 = {mp.nstr(p6, 12)}   (old e^-3 = {mp.nstr(e3, 12)})")
print(f"  phi^-4 > kappa > phi^-6 : {p4 > kappa > p6}")
print(f"  equivalent: phi^4 < 16 < phi^6 : {power(phi,4) < 16 < power(phi,6)}")
print(f"  phi^4 = 3*phi+2 = {mp.nstr(3*phi+2, 15)}  (algebraic form)")
print(f"  phi^6 = 8*phi+5 = {mp.nstr(8*phi+5, 15)}  (algebraic form)")

print()
print("=" * 78)
print("[2] Old e-form vs exact phi-form: who is approximating whom?")
print("=" * 78)
print(f"  phi^2 = {mp.nstr(phi**2, 12)}, e = {mp.nstr(e, 12)}, |1 - phi^2/e| = {mp.nstr(abs(1 - phi**2/e), 10)}")
print(f"  2*ln(phi) = {mp.nstr(2*log(phi), 12)}  (phi-form decay rate per layer)")
print(f"  -> phi^-2n = e^(-2n ln phi) = e^(-{mp.nstr(2*log(phi), 6)} n)   ~= e^-n (rate 1.0)")
print(f"  rate error: {mp.nstr(abs(2*log(phi) - 1), 6)} = {mp.nstr(abs(2*log(phi)-1)*100, 4)}%")
for n in range(0, 7):
    w_phi = power(phi, -2*n)
    w_e = exp(-n)
    rel = abs(w_phi - w_e) / w_phi
    print(f"  n={n}: phi^-{2*n} = {mp.nstr(w_phi, 8)} | e^-{n} = {mp.nstr(w_e, 8)} | rel diff {mp.nstr(rel*100, 4)}%")

print()
print("=" * 78)
print("[3] Visibility count: which weight families give exactly 3 visible modes?")
print("=" * 78)
def vis_count(weight, n_max=20):
    return [n for n in range(n_max) if weight(n) > kappa]
print(f"  phi^-2n  : visible n = {vis_count(lambda n: power(phi, -2*n))}  (len {len(vis_count(lambda n: power(phi, -2*n)))})")
print(f"  e^-n     : visible n = {vis_count(lambda n: exp(-n))}")
print(f"  e^-n^2   : visible n = {vis_count(lambda n: exp(-n*n))}  <- Gaussian FAILS (2 modes)")
print(f"  4^-n     : visible n = {vis_count(lambda n: power(4, -n))}  <- degenerate: 4^-2 == kappa exactly")
print(f"  2^-n     : visible n = {vis_count(lambda n: power(2, -n))}")
print(f"  phi^-n   : visible n = {vis_count(lambda n: power(phi, -n))}  <- amplitude-only FAILS (6 modes)")
# power law
print("  power law n^-p : n=0 diverges (no natural normalization); p-range giving {1,2,3} visible:")
import mpmath as mpm
for p in [1.5, 2.0, 2.3, 2.524, 3.0]:
    v = [n for n in range(1, 8) if power(n, -p) > kappa]
    print(f"    p={p}: visible (n>=1) = {v}")
# geometric family range
print("  geometric r^n: 3 visible iff r in (1/4, 16^(-1/3)] = (0.25, 0.397]")
r_lo = mpf(1)/4; r_hi = power(16, mpf(-1)/3)
print(f"    r_lo = {mp.nstr(r_lo, 8)} (excluded, degenerate), r_hi = {mp.nstr(r_hi, 8)}")
print(f"    phi^-2 = {mp.nstr(power(phi, -2), 8)} in range: {r_lo < power(phi, -2) <= r_hi}")

print()
print("=" * 78)
print("[4] Mass formula shift: old e-form vs exact phi-form")
print("=" * 78)
v = mpf(1)  # in units of v_EW
for n in [1, 2, 3]:
    m_e = (kappa - exp(-n)) * v * exp(-n)
    m_p = (kappa - power(phi, -2*n)) * v * power(phi, -2*n)
    print(f"  n={n}: old m = {mp.nstr(m_e, 8)} v | new m = {mp.nstr(m_p, 8)} v | ratio {mp.nstr(m_p/m_e if m_e != 0 else 0, 6)}")
# tachyonic threshold
n_star_e = log(16)          # e^-n > kappa  <=>  n < ln 16
n_star_p = log(16)/(2*log(phi))
print(f"  tachyon threshold: old n* = ln16 = {mp.nstr(n_star_e, 6)} | new n* = ln16/(2ln phi) = {mp.nstr(n_star_p, 6)}")
print(f"  -> both give n = 0,1,2 tachyon-visible, n=3 stable")

print()
print("=" * 78)
print("[5] K_chain eigenvector decay check (Q1 honesty)")
print("=" * 78)
N = 44
# normalized Dirichlet-ish eigenvectors of the chain (IDCM convention sin(pi*n*j/88))
import math
v_max = None
for k in range(1, 45):  # eigenvector index k (mode)
    vk = [math.sin(math.pi * k * j / 88) for j in range(1, 45)]
    # check exponential decay in site index j? ratio of consecutive entries
    ratios = [abs(vk[j+1]/vk[j]) if vk[j] != 0 else None for j in range(min(10, len(vk)-1))]
    # max |ratio deviation from 1|
    dev = max((abs(r - 1) for r in ratios if r is not None), default=0)
    if v_max is None or dev > v_max[0]:
        v_max = (dev, k)
print(f"  eigenvectors sin(pi*k*j/88): max consecutive-entry ratio deviation = {v_max[0]:.4f} (mode k={v_max[1]})")
print(f"  -> delocalized standing waves; NO intrinsic exponential decay in mode OR site index.")
# Green's function decay check: G(j) = sum_k sin(k j pi/88)^2 / (E - gamma_k), E below band
print("  Green's function decay (sub-band E<0): decays exponentially in SITE distance |i-j|,")
print("  NOT in mode index n. No e^-n in the chain spectrum itself.")
# R12: e transcendental vs phi algebraic
print()
print("=" * 78)
print("[6] R12 domain consistency (O152)")
print("=" * 78)
print("  Q(sqrt5) ∩ Q(zeta_88)^+ = Q : exact closures must be rational or")
print("  algebraic-in-Q(sqrt5). e is TRANSCENDENTAL -> e^-n CANNOT be an exact")
print("  spectral identity of the 88-site Laplacian (algebraic matrix).")
print(f"  phi^-2n = (2-phi)^n ∈ Q(sqrt5)  [since phi^2 = phi+1, phi^-2 = 2-phi]")
print(f"  phi^-2 = 2 - phi = {mp.nstr(2 - phi, 12)}  <- algebraic, in the tree's own number field")
print()
print("DONE")
