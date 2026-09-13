#!/usr/bin/env python3
"""O176 attack session — D8 (r_LRD operator identity) + D10 (f_bar identity).

Structural candidates derived WITHOUT fitting, from IDCM operators:
  D10: f_bar = B/(N_d-B) = 4/40 = 1/10  (same operator as r_LRD!)
       lambda_Edd = 10% (P3 prediction) = B/(N_d-B)  -> dual identity
  D8 : r_LRD = N_gen/(N_d-B) = 3/40 = 7.5%  (primary)
       alt : 23/306 = ((N_d+mu2)/2)/(L6*F_proj) = 0.07516  (completion semantics)
  New: r_LRD / f_bar = N_gen/B = 3/4
       M_BH/M_halo (LRD phase) = r_LRD * f_bar = 3/400 = 0.0075
"""
import math

N_d, B, N_gen, mu2 = 44, 4, 3, 2
L4, L5, L6, F_proj = 7, 11, 18, 17

print("="*72)
print("D10 attack: f_bar = 10% == lambda_Edd (P3) — operator identity?")
print("="*72)
fbar = B/(N_d-B)
print(f"  B/(N_d-B)        = {fbar:.6f}  (target f_bar 0.10)")
print(f"  B/(N_d-B) as %   = {fbar*100:.4f}%   <- structural candidate")
print(f"  4/40 = 1/10      = {1/10:.6f}")
print(f"  Planck Omega_b/Omega_m = 0.157 (cosmological, NOT the 10% used)")
print(f"  -> f_bar used in docs/07 (3060*M_BH) is B/(N_d-B), not Omega ratio")
print(f"  lambda_Edd (P3)  = 10% == B/(N_d-B)  -> DUAL IDENTITY candidate")

print()
print("="*72)
print("D8 attack: r_LRD — two candidates, same operator family")
print("="*72)
r1 = N_gen/(N_d-B)
r2 = ((N_d+mu2)//2)/(L6*F_proj)
print(f"  r_LRD (primary)  = N_gen/(N_d-B) = 3/40   = {r1:.6f} = {r1*100:.4f}%")
print(f"  r_LRD (alt)      = ((N_d+mu2)/2)/(L6*Fp) = 23/306 = {r2:.6f} = {r2*100:.4f}%")
print(f"  difference       = {(r2-r1)/r1*100:.3f}%  (data scatter 0.9 dex cannot separate)")
print(f"  23 = (N_d+mu2)/2 = {(N_d+mu2)//2}  |  306 = L6*F_proj = {L6*F_proj}")
print(f"  M_star/M_BH LRD  = 40/3 = {40/3:.4f}  vs  306/23 = {306/23:.4f}  (0.22% apart)")

print()
print("="*72)
print("New operator relations (attack product)")
print("="*72)
print(f"  r_LRD / f_bar    = N_gen/B = {N_gen/B:.4f} = 3/4")
print(f"  M_BH/M_halo(LRD) = r_LRD * f_bar = {r1*fbar:.6f} = {r1*fbar*100:.4f}% = 3/400")
print(f"  f_bar * M_star(fin)/M_BH = f_bar*306 = {fbar*306:.1f} = 30.6")
print(f"  M_halo(compl)    = 3060*M_BH  <->  306*f_bar^-1 = {306/fbar:.1f}  (docs/07)")
print(f"  r_LRD vs budget  = 61.5 * r_LRD = {61.5*r1:.3f}  (=20.5/2.667? D1 budget/N_gen = {61.5/3:.1f})")

print()
print("="*72)
print("Cross-check vs observations (Kocevski+25 LRD-only medians)")
print("="*72)
obs = [(3,4,6.03),(4,5,8.13),(5,6,7.85),(6,7,9.44)]
for lo,hi,med in obs:
    d1 = math.log10(med/100) - math.log10(r1)
    d2 = math.log10(med/100) - math.log10(r2)
    print(f"  z={lo}-{hi}: obs {med:.2f}% | dev vs 3/40: {d1:+.3f} dex | dev vs 23/306: {d2:+.3f} dex")

print()
print("VERDICT:")
print("  D10: f_bar = B/(N_d-B) = 1/10 — CLEAN operator identity (candidate level)")
print("       lambda_Edd 10% same operator -> dual identity strengthens P3")
print("  D8 : 3/40 (N_gen/(N_d-B)) and 23/306 ((N_d+mu2)/2/306) both fit;")
print("       3/40 uses only base operators; 23/306 has completion semantics")
print("       (LRD host = 23/306 of final mass). 0.22% apart - z<3 data decides.")
print("  New: r_LRD/f_bar = N_gen/B = 3/4; M_BH/M_halo(LRD) = 3/400")
