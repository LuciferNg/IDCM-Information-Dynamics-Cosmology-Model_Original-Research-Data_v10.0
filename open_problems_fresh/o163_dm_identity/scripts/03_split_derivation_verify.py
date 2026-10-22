#!/usr/bin/env python3
"""O163 P0f: Split hypothesis - structural forcing + uniqueness + observation.

Prove (or falsify): Omega_b = N_gen/60 = 3/60, Omega_DM = B^2/60 = 16/60,
ratio 16/3, is (1) structurally derived, (2) UNIQUE among operator
decompositions of 19 consistent with the baryon-fraction constraint,
(3) observationally closed.

Structural chain:
  S1: kappa = B^-2 = 1/16; e^-n > kappa -> n = 0,1,2 visible (3 modes) [O116]
  S2: f_unproj = (1+M/SumGamma)/2 = (1+33/90)/2 = 41/60 [O148, M=K_tree=33]
  S3: L10 = M + SumGamma = 123 = N_gen*(N_d-N_gen) [O147]
  S4: 60 = N_d + B^2 ; 41 = N_d - N_gen ; 19 = 60-41 = N_gen + B^2
  S5: baryons = N_gen/60, DM = B^2/60, ratio = B^2/N_gen = 16/3
"""
from mpmath import mp, mpf, e, ln
mp.dps = 30

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1; print(f"  [FAIL] {name} {detail}")

print("=== S1: kappa threshold -> 3 visible modes (O116 first principles) ===")
B, N_gen, N_d = 4, 3, 44
kappa = mpf(1)/B**2
n_vis = [n for n in range(6) if e**(-n) > kappa]
print(f"  kappa = {kappa}; e^-n > kappa for n = {n_vis}")
check("visible modes = {0,1,2} (3 modes)", n_vis == [0,1,2])
check("3 modes = N_gen", len(n_vis) == N_gen)

print("\n=== S2: f_unproj = (1+M/SumGamma)/2 (O148) ===")
M, SG = 33, 90
f_un = (mpf(1) + mpf(M)/SG)/2
check("f_unproj = 41/60", mp.almosteq(f_un, mpf(41)/60, rel_eps=mpf('1e-28')), f"got {f_un}")
check("f_proj = 19/60", mp.almosteq(1-f_un, mpf(19)/60, rel_eps=mpf('1e-28')))

print("\n=== S3: L10 = M + SumGamma = N_gen*(N_d-N_gen) ===")
L10 = M + SG
check("L10 = 123", L10 == 123)
check("L10 = N_gen*(N_d-N_gen)", L10 == N_gen*(N_d-N_gen), f"{L10} vs {N_gen*(N_d-N_gen)}")

print("\n=== S4: operator identities ===")
check("60 = N_d + B^2", 60 == N_d + B**2)
check("41 = N_d - N_gen", 41 == N_d - N_gen)
check("19 = N_gen + B^2", 19 == N_gen + B**2)
check("41+3+16 = 60", 41+3+16 == 60)
check("B = N_gen + 1", B == N_gen + 1)
check("60 = B*N_gen*F5", 60 == 4*3*5)

print("\n=== S5: UNIQUENESS - enumerate operator decompositions of 19 ===")
# operator set from IDCM corpus (single operators)
ops = sorted(set([1,2,3,4,5,7,8,9,11,13,16,17,18,21,22,25,29,33,41,44,88,90,123]))
decomps = []
for a in ops:
    b = 19 - a
    if b in ops and a <= b:
        decomps.append((a,b))
print(f"  operator decompositions of 19: {decomps}")
# baryon fraction constraint: Omega_b/Omega_m ~ 0.1564 (Planck 2018)
obs_frac = mpf('0.04931')/mpf('0.3153')
print(f"  observed baryon fraction of matter: {obs_frac}  (target 3/19 = {mpf(3)/19})")
ok = [(a,b) for (a,b) in decomps if abs(mpf(a)/19 - obs_frac)/obs_frac < 0.05]
print(f"  decompositions matching baryon fraction within 5%: {ok}")
check("UNIQUE: only N_gen+B^2 survives", ok == [(3,16)])

print("\n=== S6: observation closure (Planck 2018) ===")
ob_l, odm_l = mpf('0.04931'), mpf('0.2645')
check("Omega_b = 3/60 vs 0.04931", abs(mpf(3)/60 - ob_l)/ob_l < mpf('0.02'), f"dev {float((mpf(3)/60-ob_l)/ob_l*100):.2f}%")
check("Omega_DM = 16/60 vs 0.2645", abs(mpf(16)/60 - odm_l)/odm_l < mpf('0.02'), f"dev {float((mpf(16)/60-odm_l)/odm_l*100):.2f}%")
r = mpf(16)/3; r_l = odm_l/ob_l
check("ratio 16/3 vs 5.364", abs(r-r_l)/r_l < mpf('0.01'), f"dev {float((r-r_l)/r_l*100):.3f}%")
r_old = mpf(13)/2
print(f"  old IDCM 13/2 dev: {float((r_old-r_l)/r_l*100):.1f}% (abandoned)")
# BBN: Omega_b h^2 anchored 0.02237, implied h
obh2 = mpf('0.02237')
h_impl = mp.sqrt(obh2/(mpf(3)/60))
check("implied h ~ Planck side", abs(h_impl - mpf('0.6736'))/mpf('0.6736') < mpf('0.01'), f"h = {float(h_impl):.4f} (Planck 0.6736)")
h_old = mp.sqrt(obh2/mpf('0.042229'))
print(f"  old phi-form implies h = {float(h_old):.4f} (IDCM 0.7259 side)")

print(f"\n=== TOTAL: {PASS} PASS / {FAIL} FAIL ===")
