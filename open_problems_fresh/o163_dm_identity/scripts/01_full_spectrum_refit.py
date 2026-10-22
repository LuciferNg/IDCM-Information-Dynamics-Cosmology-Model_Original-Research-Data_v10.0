#!/usr/bin/env python3
"""O163 P0: LambdaCDM parameter re-estimation - zero-Omega_c full-spectrum fit.

Q: Does the Planck binned TT spectrum REQUIRE non-baryonic matter (DM),
   or can baryons-only / IDCM budgets fit it?
Models:
  A: LambdaCDM fiducial (reference)
  B: IDCM hidden sector as CDM (ombh2=0.02224, omch2=0.1446, h=0.7259)
  C: baryons-only, IDCM h (omch2=0, h=0.7259)
  D: baryons-only, Planck h (omch2=0, h=0.6736)
For each: fit As (analytic) + ns (grid 0.90-1.00), chi2 vs Planck binned TT.
"""
import numpy as np
import camb

# ---- Planck 2018 binned TT (ACT mirror): ell, C_ell (uK^2), sigma ----
data = np.loadtxt('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o163_dm_identity/data/planck_tt.txt')
ell, C, sig = data[:,0], data[:,1], data[:,2]
D_obs = C * ell*(ell+1)/(2*np.pi)          # D_ell in uK^2
sigD   = sig * ell*(ell+1)/(2*np.pi)

def spectrum(ombh2, omch2, H0, ns, As):
    pars = camb.CAMBparams()
    pars.set_cosmology(H0=H0, ombh2=ombh2, omch2=omch2, tau=0.0544)
    pars.InitPower.set_params(ns=ns, As=As)
    pars.set_for_lmax(2600)
    pars.set_matter_power(redshifts=[0.0], kmax=60.0, k_per_logint=50)  # baryons-only needs high k
    results = camb.get_results(pars)
    cls = results.get_cmb_power_spectra(spectra=['total'], CMB_unit='muK')['total']
    return cls[:,0]  # lensed TT D_ell uK^2, row index = ell

AS_UNIT = 2.0e-9  # realistic normalization for CAMB lensing check

def chi2_model(ombh2, omch2, H0, ns_grid=(0.88, 0.92, 0.96, 0.98, 1.00, 1.02, 1.04), verbose=True):
    best = (None, None, None, None)
    for ns in ns_grid:
        # D_model = As * D_unit (As = dimensionless scale ~1; As_phys = As*AS_UNIT)
        D_unit = spectrum(ombh2, omch2, H0, ns, AS_UNIT)
        # interpolate model to data ell
        D_m = np.interp(ell, np.arange(len(D_unit)), D_unit)
        w = 1.0/sigD**2
        As = np.sum(w*D_m*D_obs)/np.sum(w*D_m**2)
        chi2 = np.sum(w*(As*D_m - D_obs)**2)
        if best[0] is None or chi2 < best[0]:
            best = (chi2, ns, As, D_m)
    chi2, ns, As, D_m = best
    dof = len(ell) - 2
    if verbose:
        print(f"  ombh2={ombh2:.5f} omch2={omch2:.4f} h={H0/100:.4f}: chi2={chi2:.1f}/{dof} chi2/dof={chi2/dof:.2f} ns={ns} As_phys={As*AS_UNIT:.3e}")
    return chi2, ns, As

print("=== O163 P0: Planck TT full-spectrum re-fit (zero-Omega_c test) ===")
print(f"data: {len(ell)} bins, ell range {ell[0]:.0f}-{ell[-1]:.0f}\n")
print("Model A: LambdaCDM fiducial (reference)")
cA = chi2_model(0.02237, 0.1200, 67.36)
print("Model B: IDCM hidden sector as CDM (h=0.7259)")
cB = chi2_model(0.02224, 0.1446, 72.59)
print("Model C: baryons-only, IDCM h")
cC = chi2_model(0.02224, 0.0, 72.59)
print("Model D: baryons-only, Planck h")
cD = chi2_model(0.02237, 0.0, 67.36)

# physics: matter-radiation equality z_eq = om_m h^2 / om_g h^2 - 1, om_g h^2 = 2.47e-5
print("\n=== z_eq (matter-radiation equality) ===")
for name, ombh2, omch2, h in [("A LambdaCDM",0.02237,0.12,0.6736),("B IDCM hidden-as-CDM",0.02224,0.1446,0.7259),("C baryons-only IDCM h",0.02224,0.0,0.7259),("D baryons-only Planck h",0.02237,0.0,0.6736)]:
    zeq = (ombh2+omch2)/2.47e-5 - 1
    print(f"  {name}: z_eq = {zeq:.0f}")
