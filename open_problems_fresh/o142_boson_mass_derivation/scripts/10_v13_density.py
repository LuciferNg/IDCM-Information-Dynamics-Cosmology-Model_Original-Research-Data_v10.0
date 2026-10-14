#!/usr/bin/env python3
# -*- coding: ascii -*-
"""v13 density scan + residue analysis - alpha_s principle-first closure
Question: is Lambda_IDCM = sqrt(lmax)*M0*(N_gen/L5) a unique structural hit?"""
import mpmath as mp
mp.mp.dps = 40

phi = (1+mp.sqrt(5))/2
psi_ = (1-mp.sqrt(5))/2
L = lambda n: phi**n + psi_**n
F = lambda n: (phi**n - psi_**n)/mp.sqrt(5)
gamma = lambda n: 4*mp.sin(mp.pi*n/88)**2

M0 = mp.mpf('27.900915')
N_d = mp.mpf(44); B = mp.mpf(4); N_gen = mp.mpf(3)
L5 = L(5); L4 = L(4)
lam_max = 36 - 1/gamma(20)
strong_scale = mp.sqrt(lam_max)*M0   # O59: 166.0445 MeV

# Target: what the 1-loop beta decay needs
M_Z = mp.mpf('91.1876')
alpha_s_PDG = mp.mpf('0.1180')
alpha_s_inv_PDG = 1/alpha_s_PDG
Lambda_target_1loop = M_Z*mp.exp(-2*mp.pi*alpha_s_inv_PDG/7)   # b0 = L4 = 7
# Ratio that Lambda_IDCM must reproduce (same units: MeV/MeV):
ratio_target = strong_scale/(Lambda_target_1loop*1000)      # ~3.6632

print("strong_scale =", mp.nstr(strong_scale, 8), "MeV")
print("Lambda_1loop(b0=7) =", mp.nstr(Lambda_target_1loop*1000, 8), "MeV")
print("ratio_target =", mp.nstr(ratio_target, 10))

# === FULL density scan: a/b with 1<=a,b<=34 ===
print("\n=== Full rational scan 1..34 ===")
hits = []
for a in range(1, 35):
    for b in range(1, 35):
        r = mp.mpf(a)/b
        dev = ((r - ratio_target)/ratio_target)
        if abs(dev) < 0.02:
            hits.append((float(dev)*100, a, b, float(r)))
hits.sort()
print(f"hits within 2% of ratio_target: {len(hits)}")
for dev,a,b,r in hits[:20]:
    print(f"  {a}/{b} = {r:.6f}  dev {dev:+.4f}%")

print("\nhits within 1%:", sum(1 for h in hits if abs(h[0])<1.0))
print("hits within 0.5%:", sum(1 for h in hits if abs(h[0])<0.5))
print("hits within 0.2%:", sum(1 for h in hits if abs(h[0])<0.2))

# best non-structural rational
print("\nBest rationals (no structural claim):")
for dev,a,b,r in hits[:3]:
    print(f"  {a}/{b} dev {dev:+.4f}%")
# 11/3:
r_11_3 = mp.mpf(11)/3
print(f"\n11/3 = {mp.nstr(r_11_3,8)} dev {mp.nstr((r_11_3-ratio_target)/ratio_target*100,6)}%")
print(f"3/11 = N_gen/L5 (structural); 11/3 is its inverse")

# === Check residue: what is ratio_target exactly? ===
print("\n=== Residue analysis ===")
res = ratio_target / (mp.mpf(11)/3)   # = 1 - 0.095%... 
print("ratio_target/(11/3) =", mp.nstr(res, 12), " (dev from 1:", mp.nstr((res-1)*100, 6), "%)")
# lambda_max alternative: is 45.28 = m_something/2? m_s(M=2GeV) ~ 92.5/2 = 46.25?
print("Lambda_IDCM =", mp.nstr(strong_scale*N_gen/L5, 10), "MeV")
print("m_s/2 = 46.25?  m_s~92.5 -> m_s/2 =", 92.5/2, "dev", mp.nstr((strong_scale*N_gen/L5 - 46.25)/46.25*100, 5), "%")
# O61/O64 mass formula check: m = M0*gamma_n*F_proj.  Lambda = M0 * sqrt(lam_max) * 3/11.
# sqrt(lam_max) = 5.9512, 3/11 = 0.2727 -> Lambda = M0 * 1.6231...
print("sqrt(lmax)*3/11 =", mp.nstr(mp.sqrt(lam_max)*N_gen/L5, 8), "(effective gamma for Lambda)")
# 1.6231 = ?  gamma_19 = 4sin^2(19pi/88)?
print("gamma_19 =", mp.nstr(gamma(19), 8), "; gamma_21 =", mp.nstr(gamma(21), 8))
print("phi =", mp.nstr(phi, 8), "; 1.6231 vs 1.6180 dev:", mp.nstr((mp.sqrt(lam_max)*N_gen/L5 - phi)/phi*100, 5), "%")
# so Lambda_IDCM = M0 * (effective gamma ~ phi-ish * L5-correction)

# === Statistical: rational density in [0, 20] x [0, 20] hitting 0.1%? ===
print("\n=== Statistical density (fair) ===")
# candidates a/b within 1% of ratio: total rationals 34x34=1156; window 2% -> ~2%*2 = expected?
print(f"34x34 = {34*34} rationals; ratio in (0.6..6). per-unit density ~ high.")
# P(any given small rational within 0.2%) ~ 0.4% * density. ~ 5-10 hits expected at 2%; at 0.5%:
print("=> within 0.5%:", sum(1 for h in hits if abs(h[0])<0.5), "hits / 1156 -> meaningful uniqueness at chosen N_gen/L5?")
# NOTE: ratio direction is L5/N_gen (11/3), NOT N_gen/L5 (3/11) which is the inverse.
print("L5/N_gen = 11/3 dev:", mp.nstr((mp.mpf(11)/3 - ratio_target)/ratio_target*100, 6), "%")
print("=> 11/3 unique <=0.5% hit:", "YES" if sum(1 for h in hits if abs(h[0])<0.5)==3 else "NO - check")