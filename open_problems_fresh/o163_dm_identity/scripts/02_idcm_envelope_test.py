#!/usr/bin/env python3
"""O163 P0b: IDCM structural envelope vs Planck full-spectrum tail.

Test 1: GR re-fit summary (A/B/C/D) with fixed ns grid.
Test 2: IDCM Silk envelope exp[-(ell/9055)^(3/2)] vs observed damping tail.
        Does IDCM's back-fit Silk scale (ell_D=9055, from 4 prime peaks)
        match the Planck tail at ell > 1409?
"""
import numpy as np
import camb

data = np.loadtxt('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o163_dm_identity/data/planck_tt.txt')
ell, C, sig = data[:,0], data[:,1], data[:,2]
D_obs = C * ell*(ell+1)/(2*np.pi)
sigD   = sig * ell*(ell+1)/(2*np.pi)
w = 1.0/sigD**2

def spectrum(ombh2, omch2, H0, ns, As):
    pars = camb.CAMBparams()
    pars.set_cosmology(H0=H0, ombh2=ombh2, omch2=omch2, tau=0.0544)
    pars.InitPower.set_params(ns=ns, As=As)
    pars.set_for_lmax(2600)
    pars.set_matter_power(redshifts=[0.0], kmax=60.0, k_per_logint=50)
    return camb.get_results(pars).get_cmb_power_spectra(spectra=['total'], CMB_unit='muK')['total'][:,0]

AS = 2.0e-9
def chi2_model(ombh2, omch2, H0, ns_grid=(0.92, 0.96, 0.98, 1.00, 1.02, 1.04)):
    best = (1e99, None, None)
    for ns in ns_grid:
        D = spectrum(ombh2, omch2, H0, ns, AS)
        D_m = np.interp(ell, np.arange(len(D)), D)
        As = np.sum(w*D_m*D_obs)/np.sum(w*D_m**2)
        chi2 = np.sum(w*(As*D_m - D_obs)**2)
        if chi2 < best[0]:
            best = (chi2, ns, As)
    return best

print("=== Test 1: GR full-spectrum re-fit (215 bins, As+ns fit) ===")
for name, ob, oc, h in [("A LambdaCDM", 0.02237, 0.1200, 67.36),
                        ("B IDCM hidden-as-CDM h=0.7259", 0.02224, 0.1446, 72.59),
                        ("C baryons-only IDCM h", 0.02224, 0.0, 72.59),
                        ("D baryons-only Planck h", 0.02237, 0.0, 67.36)]:
    chi2, ns, As = chi2_model(ob, oc, h)
    print(f"  {name}: chi2/dof = {chi2/213:.2f}  (ns={ns}, As={As*AS:.3e})")

print("\n=== Test 2: IDCM Silk envelope vs Planck damping tail ===")
# IDCM prime-peak formula (O10): A(p_j) = A1 * 3eps*(33/34) * Prod(F_k/F_{k+1}) * exp[-(ell/9055)^(3/2)]
eps = (1/np.sqrt(5)*0+ 0.6180339887498949)/4  # phi^-1/4  (phi = golden ratio)
phi = (1+np.sqrt(5))/2
eps = phi**-1 / 4
F = [1,1,2,3,5,8,13,21,34]  # F_1..F_9
def idcm_prime_amp(j, ell_p, A1):
    # j = prime index (1->p=2, 2->p=3, 3->p=5, 4->p=7); geometric factor 3eps*Prod_{k<j} F_k/F_{k+1}
    g = 3*eps*(33/34)
    for k in range(1, j):
        g *= F[k]/F[k+1]
    return A1 * g * np.exp(-(ell_p/9055.0)**1.5)

peaks = [(221,1,5816.0),(527,2,2579.0),(815,3,2553.0),(1121,4,1246.0),(1409,5,822.0)]
# j for p=2,3,5,7 -> prime index 1,2,3,4 ; p=221 is m=1 (p=2? no: m=1 = p=2 -> j=1)
print("  IDCM prime-peak predictions vs observed:")
for ell_p, j, D_obs_p in peaks:
    # observed at this ell (nearest bin)
    i = np.argmin(np.abs(ell-ell_p))
    D_o = D_obs[i]
    D_p = idcm_prime_amp(j, ell_p, 5816.0)
    print(f"  ell={ell_p:4d}: IDCM {D_p:7.1f}  obs {D_o:7.1f}  dev {(D_p-D_o)/D_o*100:+6.2f}%")

print("\n  Silk envelope exp[-(ell/9055)^1.5] vs observed tail (normalized at ell=1409):")
D1409 = D_obs[np.argmin(np.abs(ell-1409))]
for lp in [1500, 1800, 2000, 2200, 2492]:
    i = np.argmin(np.abs(ell-lp))
    silk_pred = np.exp(-(ell[i]/9055.0)**1.5) / np.exp(-(1409/9055.0)**1.5)
    obs_ratio = D_obs[i]/D1409
    print(f"  ell={ell[i]:5.0f}: Silk(9055) pred {silk_pred*100:5.1f}%  observed {obs_ratio*100:5.1f}%  ratio {silk_pred/obs_ratio:5.2f}")

# what ell_D does the observed tail actually require?
print("\n  Effective Silk scale from observed tail (solve exp[-(ell/ellD)^1.5] = obs_ratio):")
for lp in [1800, 2200, 2492]:
    i = np.argmin(np.abs(ell-lp))
    obs_ratio = D_obs[i]/D1409
    ellD = lp / (-np.log(obs_ratio))**(1/1.5)
    print(f"  ell={ell[i]:5.0f}: required ell_D = {ellD:.0f}")
