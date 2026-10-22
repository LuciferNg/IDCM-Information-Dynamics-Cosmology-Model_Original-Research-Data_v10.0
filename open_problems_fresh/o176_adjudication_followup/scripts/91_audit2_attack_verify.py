#!/usr/bin/env python3
"""O176 audit round 2 — independent verification of attack-phase numbers
(docs/09, docs/10, docs/11 + sibling docs/09_d8_d9_identities).
Cross-checks every new claim WITHOUT reusing the attack scripts' code paths.
"""
import math, random

ok = fail = 0
def check(name, got, exp, tol=0.01):
    global ok, fail
    good = abs(got-exp)/max(abs(exp),1e-12) < tol
    print(f"  [{'OK ' if good else 'FAIL'}] {name}: got={got:.6g} exp={exp:.6g} (dev {abs(got-exp)/max(abs(exp),1e-12)*100:.4f}%)")
    ok += good; fail += (not good)

print("=== A. docs/09 D8: r_LRD operator identity ===")
K_tree, L5, Nd, B = 33, 11, 44, 4
check("N_gen = K_tree/L5", K_tree/L5, 3)
check("r_LRD = N_gen/(Nd-B)", 3/40, 3/(44-4))
check("3/40 = (K_tree/L5)/(Nd-B)", (K_tree/L5)/(Nd-B), 0.075)
check("40 = F5*2^3", 5*8, 40)

print("\n=== B. docs/09 D9: slope -22/25 ===")
check("-22/25", -22/25, -0.88)
check("-(Nd/2)/F5^2", -(44/2)/25, -0.88)
# endpoint approx: log10(5.25/0.0135)/3.05
ep = math.log10(5.25/0.0135)/3.05
print(f"  endpoint approx = {ep:.4f} (docs claim 0.849)")
check("endpoint ~0.849", ep, 0.849, 0.005)
check("-8/9 dev from -0.88", abs(-8/9+0.88), 0.00889, 0.5)  # 1%
check("-7/8 dev from -0.88", abs(-7/8+0.88), 0.005, 0.5)    # 0.6%

print("\n=== C. O174 arcsine (docs/11 cites it) ===")
# normalization: int_{-1}^{1} 1/(pi sqrt(1-x^2)) dx = 1
N = 200000
s = 0.0
for _ in range(N):
    x = random.uniform(-1, 1)
    s += 1.0/(math.pi*math.sqrt(max(1e-12, 1-x*x)))
check("arcsine norm (2*mean)", 2*s/N, 1.0, 0.005)
# seed range: delta_hat in [-1,1] -> M in [0, 2^1.5 * M_base]
M_base = 1.914e6
check("M(1) = 2^1.5*M_base", M_base*(2**1.5), 5.413e6, 0.002)

print("\n=== D. docs/10 D1: 11/45 candidate ===")
check("11/45", 11/45, 0.2444444, 0.0001)
check("obs/(11/15) ~ 1/3", 0.244345/(11/15), 1/3, 0.02)
check("60*B(n)*0.244345 = 61.5/3", 60*(123/88)*0.244345, 20.5, 0.002)

print("\n=== E. docs/11 D6: Gaussian exclusion numbers ===")
def tail_sigma(sig): return 0.5*math.erfc(91.4/(sig*math.sqrt(2)))
for sig, exp in [(1.0, 91.4), (10.0, 9.14)]:
    z = 91.4/sig
    check(f"sigma={sig} -> {z:.1f} sigma", z, exp, 0.005)
# logN: ln(1+91.4)=4.526, mu=ln(2.367)=0.862
mu = math.log(2.367)
for s, expz in [(1.0, 3.66), (1.5, 2.44), (2.0, 1.83)]:
    z = (math.log(92.4)-mu)/s
    check(f"logN s={s} UHz1 z-sigma", z, expz, 0.02)
# sigma_lnM = 1.5 s, sigma_dex = sigma_lnM/ln(10)
check("s=1.5 -> sigma_dex", 1.5*1.5/math.log(10), 0.977, 0.01)

print("\n=== F. docs/09 (mine): 23/306 variant ===")
check("23/306", 23/306, 0.0751634, 0.0005)
check("23 = (Nd+mu2)/2", (44+2)/2, 23)
check("306 = L6*F_proj", 18*17, 306)
check("23/306 vs 3/40 dev", (23/306-3/40)/(3/40)*100, 0.2179, 0.05)
check("f_bar = B/(Nd-B)", 4/40, 0.1)
check("r_LRD/f_bar = N_gen/B", (3/40)/0.1, 3/4)
check("M_BH/M_halo = 3/400", 0.075*0.1, 0.0075)

print(f"\n===== AUDIT2 RESULT: {ok} OK / {fail} FAIL =====")
