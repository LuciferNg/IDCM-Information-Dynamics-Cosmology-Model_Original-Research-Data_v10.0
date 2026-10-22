#!/usr/bin/env python3
"""
O117/11: Radial kernel supersession -- C_DM/C_DH re-derivation is MOOT
=====================================================================
Trigger: SESSION_START "未執行" items 1-2 (listed 2026-09-24; executed 2026-09-26).

Background. O117 (2026-09-01) closed the radial side with the parameterization

    DH(z) = R_H * (1 + delta_k0(l) + C_DH*(l-0.5)*(1-4^-l)) / (1+z)
    C_DM = -0.1697331557,   C_DH = C_DM * B/N_gen = C_DM * 4/3

The unexecuted item was "re-derive C_DM / C_DH" after O169 falsified the
C_DM identity (C = 1-2phi^-1 = -(sqrt5-2) = -0.23606798 EXACT).

FINDING. Re-deriving C_DM/C_DH is MOOT. O170 (2026-09-15) closed the SAME
observable (DESI DR2 D_H/r_d, 6 cosmology bins) with a DIFFERENT and strictly
better parameterization:

    D_H(l) = R_world * 4^-l * M(l) / ln4
    M(l)   = sec(pi*n_c(l)/88),   n_c = N_d/2 + B*sin(pi*l)  (l < l_t)
                                  n_c = N_d/2                (l >= l_t)
    l_t    = log_4 N_gen = 0.792481

chi2(D_H) = 3.4712/6 (0.579/dof)  vs  O117's 7.41/6 (wrong errors)
                                        or 29.50/6 (correct errors)

Per the standing rule (sibling O already closes the same observable with
another parameterization => downgrade, do not keep both), O117's radial
parameterization is SUPERSEDED. This script verifies that claim independently
and maps the two parameterizations onto each other.

Source of the arch kernel: o170_phase_depth_distance/docs/06 §2, §4.
DESI data: o170 data/01_desi_dr2_radial_data.md (Table 6, verified).
"""
import mpmath as mp

mp.mp.dps = 40
PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {name}")
    else:
        FAIL += 1
        print(f"  FAIL: {name}")
    if detail:
        print(f"    {detail}")

# ============ Structural constants (identical to both O117 and O170) ============
R_world = mp.mpf("4129.94")          # Mpc, = c/H0_local (O167)
N_d     = 44
B       = 4
N_gen   = 3
phi     = (1 + mp.sqrt(5)) / 2
phi_inv = phi - 1
ln4     = mp.log(4)
rd      = mp.pi * R_world / 88 * mp.mpf(420) / mp.mpf(421)   # 147.088303

ell   = lambda z: mp.log(1 + z, 4)
l_t   = mp.log(N_gen, 4)             # 0.792481

print("=" * 78)
print("  O117/11 -- radial kernel supersession (C_DM/C_DH re-derivation moot)")
print("=" * 78)
print(f"  R_world = {mp.nstr(R_world,10)} Mpc   rd = {mp.nstr(rd,12)} Mpc")
print(f"  N_d = {N_d}, B = {B}, N_gen = {N_gen}")
print(f"  l_t = log_4(N_gen) = {mp.nstr(l_t,10)}")

# ============ O170 arch kernel ============
def n_c(l):
    if l < l_t:
        return mp.mpf(N_d)/2 + B * mp.sin(mp.pi * l)
    return mp.mpf(N_d)/2

def M_arch(l):
    return mp.sec(mp.pi * n_c(l) / 88)

def DH_arch(z):
    l = ell(z)
    return R_world * 4**(-l) * M_arch(l) / ln4

# ============ O117 parameterization (for comparison only) ============
C_DM_O117 = mp.mpf("-0.1697331557")
C_DH_O117 = C_DM_O117 * mp.mpf(B) / mp.mpf(N_gen)
sigma_phi = mp.log(phi, 4) / 2
def delta_k0(l):
    return phi_inv**3 * mp.exp(-(l - mp.mpf("0.5"))**2 / (2*sigma_phi**2))
def delta_gd(l, C):
    return C * (l - mp.mpf("0.5")) * (1 - 4**(-l))
def DH_O117(z, C):
    l = ell(z)
    return R_world * (1 + delta_k0(l) + delta_gd(l, C)) / (1 + z)

# ============ DESI DR2 Table 6 (verified, O170 data/01) ============
# (tracer, z, D_H/r_d, sigma, sigma_used_by_O117)
DESI = [
    ('LRG1',     mp.mpf("0.510"), mp.mpf("21.863"), mp.mpf("0.425"), mp.mpf("0.429")),
    ('LRG2',     mp.mpf("0.706"), mp.mpf("19.455"), mp.mpf("0.330"), mp.mpf("0.334")),
    ('LRG3+ELG1',mp.mpf("0.934"), mp.mpf("17.641"), mp.mpf("0.193"), mp.mpf("0.201")),
    ('ELG2',     mp.mpf("1.321"), mp.mpf("14.176"), mp.mpf("0.221"), mp.mpf("0.225")),
    ('QSO',      mp.mpf("1.484"), mp.mpf("12.817"), mp.mpf("0.516"), mp.mpf("0.518")),
    ('Lyalpha',  mp.mpf("2.330"), mp.mpf("8.632"),  mp.mpf("0.101"), mp.mpf("0.532")),
]

# ============ 1. O170 arch kernel: M_obs table + chi2 ============
print(f"\n{'-'*78}")
print("  1. O170 arch kernel -- independent recompute")
print(f"{'-'*78}")
print(f"  {'tracer':<11}{'z':>7}{'l':>9}{'M_obs':>10}{'sig_M':>9}{'M_arch':>10}{'pull':>9}")

chi2_arch = mp.mpf(0)
for nm, z, dh_obs, sig_dh, _ in DESI:
    l = ell(z)
    # M = D_H * (1+z) * ln4 / R_world  = (D_H/rd) * rd * (1+z) * ln4 / R_world
    M_obs = dh_obs * rd * (1 + z) * ln4 / R_world
    s_M   = sig_dh * rd * (1 + z) * ln4 / R_world
    M_a   = M_arch(l)
    pull  = (M_a - M_obs) / s_M
    chi2_arch += pull**2
    print(f"  {nm:<11}{float(z):>7.3f}{float(l):>9.5f}{float(M_obs):>10.4f}"
          f"{float(s_M):>9.4f}{float(M_a):>10.4f}{float(pull):>+9.2f}")

print(f"\n  chi2(D_H) = {mp.nstr(chi2_arch,6)} / 6   ({mp.nstr(chi2_arch/6,5)} per dof)")
check("arch kernel reproduces O170 chi2(D_H) = 3.4712/6",
      abs(chi2_arch - mp.mpf("3.4712")) < mp.mpf("0.01"),
      f"computed {mp.nstr(chi2_arch,6)}")

# ============ 2. Lyalpha adjudication ============
print(f"\n{'-'*78}")
print("  2. Lyalpha adjudication -- outlier under O117, resolved under arch")
print(f"{'-'*78}")
z_lya = mp.mpf("2.330")
l_lya = ell(z_lya)
obs_lya, sig_lya = mp.mpf("8.632"), mp.mpf("0.101")
pred_arch = DH_arch(z_lya) / rd
pred_o117 = DH_O117(z_lya, C_DH_O117) / rd
print(f"  DESI DR2 Lyalpha  D_H/rd = {float(obs_lya):.4f} +- {float(sig_lya):.3f}")
print(f"  O117 param.       pred   = {float(pred_o117):.4f}   pull = {float((pred_o117-obs_lya)/sig_lya):+.2f} sigma")
print(f"  O170 arch kernel  pred   = {float(pred_arch):.4f}   pull = {float((pred_arch-obs_lya)/sig_lya):+.2f} sigma")
check("Lyalpha resolved by arch kernel (<1 sigma), no new parameter",
      abs((pred_arch - obs_lya) / sig_lya) < 1.0,
      f"pull = {float((pred_arch-obs_lya)/sig_lya):+.2f} sigma")

# deep-limit diagnosis
M_deep_arch = M_arch(mp.mpf("10"))      # locked at N_d/2
M_deep_o117 = ln4                        # O117's (1+delta) -> ln4
print(f"\n  Deep limit M(inf):  arch = {float(M_deep_arch):.6f} (= sqrt2)")
print(f"                      O117 = {float(M_deep_o117):.6f} (= ln4)")
print(f"  O170 F3/F4: O117's M(inf) = ln4 = 1.386 != sqrt2 -> deep limit structurally wrong")
check("arch deep limit = sqrt2 = sec(pi/4)",
      abs(M_deep_arch - mp.sqrt(2)) < mp.mpf("1e-30"), f"{mp.nstr(M_deep_arch,10)}")

# ============ 3. Parameterization mapping ============
print(f"\n{'-'*78}")
print("  3. Parameterization mapping: (1+delta_O117)  vs  M_arch/ln4")
print(f"{'-'*78}")
print(f"  {'tracer':<11}{'l':>9}{'1+d_O117':>11}{'M_arch/ln4':>12}{'diff %':>10}")
for nm, z, dh_obs, sig_dh, _ in DESI:
    l = ell(z)
    one_plus = 1 + delta_k0(l) + delta_gd(l, C_DH_O117)
    arch_equiv = M_arch(l) / ln4
    diff = (one_plus / arch_equiv - 1) * 100
    print(f"  {nm:<11}{float(l):>9.5f}{float(one_plus):>11.5f}{float(arch_equiv):>12.5f}{float(diff):>+10.2f}")
print("\n  Both play the role of (1+delta); they differ -> different parameterizations")
print("  of the same observable. Only the arch form reproduces the deep limit sqrt2.")

# ============ 4. O117 chi2 under both error sets (recap) ============
print(f"\n{'-'*78}")
print("  4. O117 parameterization chi2 recap (from scripts/10)")
print(f"{'-'*78}")
def chi2_o117(C, use_table6):
    c2 = mp.mpf(0)
    for nm, z, dh_obs, sig6, sig_old in DESI:
        sig = sig6 if use_table6 else sig_old
        pred = DH_O117(z, C) / rd
        c2 += ((pred - dh_obs) / sig)**2
    return c2

c_old_err = chi2_o117(C_DH_O117, False)
c_new_err = chi2_o117(C_DH_O117, True)
print(f"  C_DH = C_DM*4/3 = {mp.nstr(C_DH_O117,10)}")
print(f"    O117 error set : chi2 = {mp.nstr(c_old_err,6)}/6")
print(f"    Table 6 errors : chi2 = {mp.nstr(c_new_err,6)}/6")
print(f"  O170 arch kernel : chi2 = {mp.nstr(chi2_arch,6)}/6   <-- best")
check("arch kernel strictly better than O117 param under either error set",
      chi2_arch < c_old_err and chi2_arch < c_new_err,
      f"arch {mp.nstr(chi2_arch,5)} < O117 {mp.nstr(c_old_err,5)} / {mp.nstr(c_new_err,5)}")

# ============ 5. Is 4/3 still a candidate? (O170 one-dim scan) ============
print(f"\n{'-'*78}")
print("  5. The 4/3 ratio in O170's language -- tested, excluded")
print(f"{'-'*78}")
def chi2_arch_params(A, W, l_lock):
    c2 = mp.mpf(0)
    for nm, z, dh_obs, sig6, _ in DESI:
        l = ell(z)
        nc = (mp.mpf(N_d)/2 + A*mp.sin(mp.pi*l/W)) if l < l_lock else mp.mpf(N_d)/2
        Ma = mp.sec(mp.pi*nc/88)
        M_obs = dh_obs * rd * (1+z) * ln4 / R_world
        s_M   = sig6 * rd * (1+z) * ln4 / R_world
        c2 += ((Ma - M_obs)/s_M)**2
    return c2

print(f"  arch width W (A=4, l_t=log4(3)) -- O170 docs/06 §3:")
for W in [mp.mpf("0.5"), mp.mpf(1), mp.mpf(4)/3, mp.mpf(2), mp.log(18,4)]:
    c2 = chi2_arch_params(mp.mpf(4), W, l_t)
    tag = "  <-- STRUCTURAL" if W == 1 else ("  <-- 4/3 hypothesis" if W == mp.mpf(4)/3 else "")
    print(f"    W = {float(W):>8.5f}   chi2 = {mp.nstr(c2,6):>10}{tag}")
c2_w43 = chi2_arch_params(mp.mpf(4), mp.mpf(4)/3, l_t)
c2_w1  = chi2_arch_params(mp.mpf(4), mp.mpf(1), l_t)
check("4/3 is EXCLUDED as the arch width (W=1 is the structural value)",
      c2_w43 > c2_w1 * 3,
      f"W=4/3 -> {mp.nstr(c2_w43,5)} vs W=1 -> {mp.nstr(c2_w1,5)}")

# ============ 6. H0 prediction ============
print(f"\n{'-'*78}")
print("  6. H0 prediction from the arch kernel")
print(f"{'-'*78}")
c_kms = mp.mpf("299792.458")
H0_arch = c_kms * ln4 / (R_world * M_arch(mp.mpf(0)))
H0_ln4  = c_kms * ln4 / (R_world * ln4)
print(f"  M(0) arch = {mp.nstr(M_arch(mp.mpf(0)),10)} (= sqrt2)")
print(f"  H0_arch   = {mp.nstr(H0_arch,8)} km/s/Mpc   (SH0ES 73.0+-1.0 -> {mp.nstr((H0_arch-73)/1,5)} sigma)")
print(f"  H0(ln4)   = {mp.nstr(H0_ln4,8)} km/s/Mpc   (const-ln4 kernel)")
check("H0_arch = 71.157 (-1.84 sigma SH0ES)",
      abs(H0_arch - mp.mpf("71.157")) < mp.mpf("0.01"),
      f"{mp.nstr(H0_arch,8)}")

# ============ 7. Verdict ============
print(f"\n{'='*78}")
print("  7. Verdict -- SESSION_START unexecuted items 1 & 2")
print(f"{'='*78}")
print(f"""
  ITEM 1 (C_DM / C_DH re-derivation) -> MOOT, not merely unfinished.

    O170 (2026-09-15) closed the same observable with the arch kernel:
      M(l) = sec(pi*n_c/88),  n_c = N_d/2 + B*sin(pi*l) | N_d/2
      chi2(D_H) = {mp.nstr(chi2_arch,5)}/6  (0.579/dof)
    vs O117's parameterization: {mp.nstr(c_old_err,5)}/6 (O117 errors) or {mp.nstr(c_new_err,5)}/6 (Table 6).

    The B/N_gen = 4/3 ratio is TESTED AND EXCLUDED as the arch width
    (W = 4/3 -> chi2 = {mp.nstr(c2_w43,5)} vs W = 1 -> {mp.nstr(c2_w1,5)}).
    B = 4 and N_gen = 3 do both appear in the arch kernel, but in DIFFERENT
    structural roles (B = arch amplitude, N_gen = lock point) -- not as a ratio.

  ITEM 2 (Lyalpha -4.76 sigma adjudication) -> RESOLVED.

    Under O117's parameterization Lyalpha is -4.76 sigma because the deep limit
    is M(inf) = ln4 = 1.386 instead of sqrt2. Under the arch kernel it is
    {mp.nstr((pred_arch-obs_lya)/sig_lya,4)} sigma. No new parameter, no damping factor.

  RETAINED from O117:
    - D_H != dD_A/dz (DM and DH are independent projections) -- O169 and O170 agree
    - DM/rd error set correct (12.81 / 9.65 reproduce exactly)
    - 3D anisotropy non-issue (AP chi2 = 4.65/5)

  SUPERSEDED:
    - DH(z) = R_H(1+delta_k0+delta_gd)/(1+z)  with delta_k0 Gaussian + delta_gd linear
    - C_DM = -C_delay*2phi^-1*sqrt5, C_DH = C_DM*B/N_gen
""")

out = {
    'trigger': 'O117 SESSION_START unexecuted items 1-2',
    'finding': 'C_DM/C_DH re-derivation MOOT -- O170 arch kernel supersedes',
    'chi2_DH_arch': mp.nstr(chi2_arch, 8),
    'chi2_DH_arch_per_dof': mp.nstr(chi2_arch/6, 6),
    'chi2_DH_O117_errorset': mp.nstr(c_old_err, 8),
    'chi2_DH_O117_table6': mp.nstr(c_new_err, 8),
    'lyalpha_pull_arch': mp.nstr((pred_arch-obs_lya)/sig_lya, 6),
    'lyalpha_pull_O117_table6': mp.nstr((pred_o117-obs_lya)/sig_lya, 6),
    'M_deep_arch': mp.nstr(M_deep_arch, 10),
    'M_deep_O117': mp.nstr(M_deep_o117, 10),
    'W_4over3_chi2': mp.nstr(c2_w43, 8),
    'W_1_chi2': mp.nstr(c2_w1, 8),
    'H0_arch': mp.nstr(H0_arch, 10),
    'retained': ['D_H != dD_A/dz independent projections',
                 'DM/rd error set correct',
                 '3D anisotropy non-issue'],
    'superseded': ['O117 radial parameterization with delta_k0 Gaussian + delta_gd linear',
                   'C_DM = -C_delay*2phi^-1*sqrt5 and C_DH = C_DM*B/N_gen'],
    'pass': PASS, 'fail': FAIL,
}
import json
with open('data/11_radial_kernel_supersession.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f"  Saved -> data/11_radial_kernel_supersession.json")
print(f"  PASS: {PASS}/{PASS+FAIL}")
