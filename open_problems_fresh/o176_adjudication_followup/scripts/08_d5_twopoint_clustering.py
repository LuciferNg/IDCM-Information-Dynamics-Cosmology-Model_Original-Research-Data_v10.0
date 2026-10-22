#!/usr/bin/env python3
"""O176 D5 attack — condensation field 2-pt function -> LRD clustering scale.

O174 Lagrangian: S_l = sum_n (gamma_n + mu2)|Phi_n|^2  (free field)
  -> propagator / 2-pt in mode space: w_n = 1/(gamma_n + mu2)
  gamma_n = csc(pi n / 2N), N = 88 (O140 FSR), mu2 = 2 (O159/O161)
Real-space correlation on the 88-site chain (lattice pitch R_c = R_world/44^3):
  G(r) = sum_n w_n cos(pi n r / L) / sum_n w_n,   L = 88 sites
Correlation length: xi^2 = sum_n w_n (L/(pi n))^2 / sum_n w_n
Compare with Zhang+26 LRD clustering: r0,CCF = 3.43-4.45 h^-1 Mpc
  (halo masses 10^10.1-10^11.3, bias 2.85-4.11).
"""
import math

N = 88          # chain sites (dual chain)
mu2 = 2.0       # O159/O161: mu^2 = E-O = gamma_44 = 2
R_world_Mpc = 4130.0     # c*T_ring/2pi, T_ring=84.63 Gyr (O39)
R_c_kpc = R_world_Mpc*1e3 / 44**3   # 48.5 kpc per cell (O175)

def gamma(n):   # O140 FSR
    return 1.0/math.sin(math.pi*n/(2*N))

# mode weights (propagator)
w = [1.0/(gamma(n)+mu2) for n in range(1, N+1)]
Z = sum(w)
print("="*72)
print("D5: condensation 2-pt function (O174 S_l -> propagator)")
print("="*72)
print(f"  gamma_n = csc(pi n/176), n=1..88 | mu2 = 2 | Z = sum w_n = {Z:.4f}")
print(f"  dominant modes: n=88 w={w[-1]:.4f} (gamma=1) | n=44 w={w[43]:.4f} (gamma={gamma(44):.3f})")

# correlation function in lattice units (1D chain, periodic-ish)
def G(r_sites):
    return sum(wk*math.cos(math.pi*k*r_sites/N) for k, wk in enumerate(w, 1))/Z

# correlation length: second moment in lattice units
xi2 = sum(wk*(N/(math.pi*k))**2 for k, wk in enumerate(w, 1))/Z
xi = math.sqrt(xi2)
print(f"\n  xi^2 = <r^2> = sum w_n (L/pi n)^2 / Z = {xi2:.4f} sites^2")
print(f"  xi  = {xi:.4f} sites = {xi*R_c_kpc/1000:.2f} Mpc (pitch {R_c_kpc:.1f} kpc)")

# correlation function shape: find r0 (G(r0)=0) and FWHM
print("\n  G(r) profile (lattice units):")
for r in [0,1,2,3,4,5,8,10,15,20,30,44]:
    print(f"    r={r:>2}: G={G(r):+.4f}")
r0 = None
for r in range(1, 200):
    if G(r) <= 0:
        r0 = r; break
print(f"  G(r)=0 crossing at r0 = {r0} sites = {r0*R_c_kpc/1000:.2f} Mpc (if any)")

# observed LRD clustering (Zhang+26 Table 1)
print("\n" + "="*72)
print("Compare with Zhang+26 (arXiv:2606.02773) LRD clustering")
print("="*72)
obs = [(7.5, 10.10, 4.45, 2.85), (6.5, 10.05, 4.45, 2.85),
       (5.5, 10.19, 3.45, 2.85), (4.5, 10.49, 3.43, 3.31), (3.5, 11.26, 3.67, 4.11)]
print(f"  {'z':<6}{'log Mh':>8}{'r0,CCF h^-1Mpc':>16}{'bias':>8}")
for z, mh, r0o, bias in obs:
    print(f"  z~{z:<4}{mh:>8.2f}{r0o:>14.2f}{bias:>8.2f}")
print(f"\n  observed r0 = 3.43-4.45 h^-1 Mpc = {3.43*0.7:.2f}-{4.45*0.7:.2f} Mpc (h=0.7)")
print(f"  model xi   = {xi*R_c_kpc/1000:.2f} Mpc (1D chain projection)")
print(f"  model r0   = {r0*R_c_kpc/1000 if r0 else float('nan'):.2f} Mpc (zero-crossing)")
ratio_xi = xi*R_c_kpc/1000/(4.45*0.7)
print(f"\n  xi_model / r0_obs = {ratio_xi:.3f}")

print("\n" + "="*72)
print("VERDICT (honest)")
print("="*72)
print("  1D-chain xi is a PROJECTION scale, not the 3D correlation length directly;")
print("  LRD r0 ~ 3-4 h^-1 Mpc corresponds to halos, not raw condensation field;")
print("  if condensation seeds track halo peaks, xi sets the SEED correlation scale")
print("  -> model vs obs ratio {:.2f} = order-of-magnitude check only".format(ratio_xi))
print("  Next step: 3D lattice (K_tree x K_chain) propagator + bias mapping")
