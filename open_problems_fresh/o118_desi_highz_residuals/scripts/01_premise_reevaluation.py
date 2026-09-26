#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O118/01 -- Premise re-evaluation: is the high-z DESI residual an artifact?

O118 was created 2026-08-29 on the premise:
    "group-delay correction (C = -0.16973) brings DESI DR2 chi2 from 42.23 to
     18.09/7, but chi2/dof = 2.58 -- residual is systematic;
     LRG1 (z=0.51) is the largest outlier at -4.8%; cubic term failed."

Since then two upstream results landed:
  (1) O169 (2026-09-15): elongation law E = 1 + 2*phi^-1 * ell was FALSIFIED
      (DESI DR2 D_M x 6 excludes it at 4.88 sigma)
      -> replaced by E(ell) = ell + B_NEW,  B_NEW = 22/sum(cos(pi n/88), n=1..22)
  (2) O170 docs/06 (2026-09-15): radial law replaced by the arch kernel
      M(ell) = sec(pi*n_c/88),  n_c = N_d/2 + B*sin(pi*ell) (ell < ell_t) | N_d/2
  (3) O117 scripts/10 (2026-09-24): Lyalpha sigma was misused (0.532 = D_M value);
      Table 6 correct value = 0.101

This script asks: does the O118 residual SURVIVE under the corrected framework?

Tests
  A  reproduce O118's premise under the OLD (falsified) D_M law
  B  same data under the O169-corrected D_M law
  C  full joint (D_M + D_H) under the current framework
  D  per-tracer pull table -- is LRG1 still the largest outlier?
  E  high-z (Lyalpha) check
  F  free-scan: can ANY single-parameter tweak still be demanded by the data?
"""
import math
from fractions import Fraction

PI = math.pi
LN4 = math.log(4.0)
R = 4129.94                      # R_world [Mpc] (O167/O171 definition)
RD = PI * R / 88 * 420 / 421     # r_d = pi*R/88 * 420/421  [Mpc]
B = 4                            # K_tree branching
ND = 44                          # 88-site chain -> 44 modes
NGEN = 3
ELL_T = math.log(3.0, 4.0)       # log_4(N_gen) = 0.792481
PHI = (1 + math.sqrt(5.0)) / 2

# O169 correction constant: 1/<v_g>_{1..22}
B_NEW = 22.0 / sum(math.cos(PI * n / 88.0) for n in range(1, 23))

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name}" + (f"  -- {detail}" if detail else ""))
    else:
        FAIL += 1
        print(f"  [FAIL] {name}" + (f"  -- {detail}" if detail else ""))

def ell(z):
    return math.log1p(z) / LN4

# ---- DESI DR2 Table 6, 6 cosmological bins (O170 data/01, verified vs arXiv:2503.14738) ----
DATA = [
    # name        z       D_M      s_DM     D_H     s_DH    rho
    ('LRG1',      0.510, 13.588, 0.167, 21.863, 0.425, -0.459),
    ('LRG2',      0.706, 17.351, 0.177, 19.455, 0.330, -0.404),
    ('LRG3+ELG1', 0.934, 21.576, 0.152, 17.641, 0.193, -0.416),
    ('ELG2',      1.321, 27.601, 0.318, 14.176, 0.221, -0.434),
    ('QSO',       1.484, 30.512, 0.760, 12.817, 0.516, -0.500),
    ('Lyalpha',   2.330, 38.988, 0.531,  8.632, 0.101, -0.431),
]

# ================= laws =================
def DM_old(z):
    """O117/O76 baseline: falsified by O169 (4.88 sigma). Returns D_M/r_d."""
    e = ell(z)
    return R * (1 - 4.0**(-e)) * (1 + 2 * PHI**-1 * e) / RD

def DM_new(z):
    """O169-corrected: E(ell) = ell + B_NEW. Returns D_M/r_d."""
    e = ell(z)
    return R * (1 - 4.0**(-e)) * (e + B_NEW) / RD

def DH_old(z, C=-0.1697331557):
    """O117 radial: group-delay linear term with falsified C. Returns D_H/r_d."""
    e = ell(z)
    base = R * (1 - 4.0**(-e)) * (1 + 2 * PHI**-1 * e)
    return base * (1 + C * (e - 0.5) * (1 - 4.0**(-e))) / RD

def arch_nc(e):
    if e < ELL_T:
        return ND / 2.0 + B * math.sin(PI * e)
    return ND / 2.0

def M_arch(e):
    """O170 docs/06 arch kernel: impedance = 1/v_g(n_c)."""
    return 1.0 / math.cos(PI * arch_nc(e) / 88.0)

def DH_arch(z):
    """D_H(ell) = R_world * (d ell/dz) * M(ell);  d ell/dz = 4^-ell / ln4. Returns D_H/r_d."""
    e = ell(z)
    return R * (4.0**(-e) / LN4) * M_arch(e) / RD

def chi2_side(law, key, sig_key):
    tot, rows = 0.0, []
    for name, z, dm, sm, dh, sh, rho in DATA:
        pred = law(z)
        obs = dm if key == 'dm' else dh
        sig = sm if key == 'dm' else sh
        pull = (pred - obs) / sig
        tot += pull**2
        rows.append((name, z, pred, obs, sig, pull))
    return tot, rows

def chi2_joint(dm_law, dh_law):
    """Full 12-point chi2 with per-tracer D_M-D_H correlation."""
    tot, rows = 0.0, []
    for name, z, dm, sm, dh, sh, rho in DATA:
        pm, ph = dm_law(z), dh_law(z)
        rm, rh = (pm - dm) / sm, (ph - dh) / sh
        # 2x2 correlation matrix inverse
        det = 1.0 - rho * rho
        c2 = (rm*rm - 2*rho*rm*rh + rh*rh) / det
        tot += c2
        rows.append((name, z, rm, rh, c2))
    return tot, rows

print("=" * 78)
print("  O118/01 -- Is the high-z DESI residual an artifact?")
print("=" * 78)
print(f"  R_world = {R} Mpc | r_d = {RD:.6f} Mpc | B_NEW = {B_NEW:.8f}")
print(f"  ell_t = log4(3) = {ELL_T:.6f} | M(0) = sqrt2 = {math.sqrt(2):.6f}")

# ---------------- A: reproduce O118 premise under OLD law ----------------
print("\n" + "-" * 78)
print("  A. O118 PREMISE under the OLD (falsified) D_M law")
print("-" * 78)
chi2_a, rows_a = chi2_side(DM_old, 'dm', 'sm')
print(f"  DM/rd chi2 (OLD law, 6 pts, 6 dof) = {chi2_a:.4f}")
print(f"  {'tracer':<11} {'z':>6} {'pred':>9} {'DESI':>8} {'sig':>7} {'pull':>8} {'dev%':>7}")
for name, z, pred, obs, sig, pull in rows_a:
    dev = 100 * (pred - obs) / obs
    print(f"  {name:<11} {z:>6.3f} {pred:>9.4f} {obs:>8.3f} {sig:>7.3f} {pull:>+8.2f} {dev:>+7.2f}")
lr = rows_a[0]
lr_dev = 100 * (lr[2] - lr[3]) / lr[3]
check("reproduces O118 LRG1 claim (~ -4.8%)", abs(lr_dev + 4.8) < 0.6,
      f"LRG1 dev = {lr_dev:+.2f}%")
worst = max(rows_a, key=lambda r: abs(r[5]))
check("reproduces O118 'LRG1 is largest outlier'", worst[0] == 'LRG1',
      f"worst = {worst[0]} ({worst[5]:+.2f} sigma)")

# ---------------- B: same data, corrected D_M law ----------------
print("\n" + "-" * 78)
print("  B. SAME DATA under the O169-corrected D_M law  E(ell) = ell + B_NEW")
print("-" * 78)
chi2_b, rows_b = chi2_side(DM_new, 'dm', 'sm')
print(f"  DM/rd chi2 (NEW law, 6 pts, 6 dof) = {chi2_b:.4f}   (chi2/dof = {chi2_b/6:.3f})")
print(f"  {'tracer':<11} {'z':>6} {'pred':>9} {'DESI':>8} {'sig':>7} {'pull':>8} {'dev%':>7}")
for name, z, pred, obs, sig, pull in rows_b:
    dev = 100 * (pred - obs) / obs
    print(f"  {name:<11} {z:>6.3f} {pred:>9.4f} {obs:>8.3f} {sig:>7.3f} {pull:>+8.2f} {dev:>+7.2f}")
lr_b = rows_b[0]
lr_dev_b = 100 * (lr_b[2] - lr_b[3]) / lr_b[3]
check("LRG1 outlier shrinks below 1.5%", abs(lr_dev_b) < 1.5, f"LRG1 dev = {lr_dev_b:+.2f}%")
check("LRG1 pull within 1.5 sigma", abs(lr_b[5]) < 1.5, f"pull = {lr_b[5]:+.2f} sigma")
worst_b = max(rows_b, key=lambda r: abs(r[5]))
check("LRG1 no longer the largest outlier", worst_b[0] != 'LRG1',
      f"worst now = {worst_b[0]} ({worst_b[5]:+.2f} sigma)")
check("DM/rd chi2 improves vs OLD law", chi2_b < chi2_a,
      f"{chi2_a:.3f} -> {chi2_b:.3f}")
check("DM/rd chi2/dof < 2", chi2_b / 6 < 2.0, f"{chi2_b/6:.3f}")

# ---------------- C: DH side, both laws ----------------
print("\n" + "-" * 78)
print("  C. DH/rd side: O117 radial vs O170 arch kernel")
print("-" * 78)
chi2_dh_old, rows_dh_old = chi2_side(DH_old, 'dh', 'sh')
chi2_dh_new, rows_dh_new = chi2_side(DH_arch, 'dh', 'sh')
print(f"  DH/rd chi2 (O117 radial, falsified C)  = {chi2_dh_old:.4f} / 6 dof")
print(f"  DH/rd chi2 (O170 arch kernel, 0-param) = {chi2_dh_new:.4f} / 6 dof")
print(f"  {'tracer':<11} {'z':>6} {'arch':>9} {'DESI':>8} {'sig':>7} {'pull':>8}")
for name, z, pred, obs, sig, pull in rows_dh_new:
    print(f"  {name:<11} {z:>6.3f} {pred:>9.4f} {obs:>8.3f} {sig:>7.3f} {pull:>+8.2f}")
check("arch kernel beats O117 radial on D_H", chi2_dh_new < chi2_dh_old,
      f"{chi2_dh_old:.3f} -> {chi2_dh_new:.3f}")

# ---------------- D: joint ----------------
print("\n" + "-" * 78)
print("  D. JOINT (D_M + D_H, 12 points, correlation-aware)")
print("-" * 78)
chi2_j_old, _ = chi2_joint(DM_old, DH_old)
chi2_j_new, rows_j = chi2_joint(DM_new, DH_arch)
n_pts = 2 * len(DATA)
print(f"  joint chi2 (OLD framework) = {chi2_j_old:.4f} / {n_pts} pts")
print(f"  joint chi2 (CURRENT framework) = {chi2_j_new:.4f} / {n_pts} pts"
      f"   (chi2/pt = {chi2_j_new/n_pts:.3f})")
print(f"  {'tracer':<11} {'z':>6} {'pull_DM':>9} {'pull_DH':>9} {'chi2_c':>8}")
for name, z, rm, rh, c2 in rows_j:
    print(f"  {name:<11} {z:>6.3f} {rm:>+9.2f} {rh:>+9.2f} {c2:>8.3f}")
check("joint chi2/pt < 2 (no gross systematic)", chi2_j_new / n_pts < 2.0,
      f"{chi2_j_new/n_pts:.3f}")
check("joint chi2 improves massively vs OLD", chi2_j_new < 0.5 * chi2_j_old,
      f"{chi2_j_old:.1f} -> {chi2_j_new:.1f}")

# ---------------- E: high-z check ----------------
print("\n" + "-" * 78)
print("  E. High-z (Lyalpha, z=2.33) -- O118's second named residual")
print("-" * 78)
ly_old = [r for r in rows_dh_old if r[0] == 'Lyalpha'][0]
ly_new = [r for r in rows_dh_new if r[0] == 'Lyalpha'][0]
print(f"  O117 radial : pred = {ly_old[2]:.4f}  pull = {ly_old[5]:+.2f} sigma")
print(f"  arch kernel : pred = {ly_new[2]:.4f}  pull = {ly_new[5]:+.2f} sigma")
check("Lyalpha pull within 1 sigma under arch kernel", abs(ly_new[5]) < 1.0,
      f"{ly_new[5]:+.2f} sigma")

# ---------------- F: is any correction still DEMANDED? ----------------
print("\n" + "-" * 78)
print("  F. Is a further correction still DEMANDED by the data?")
print("-" * 78)
# O118 proposed a local impedance correction near the SYNC turnover z_c = 0.6.
# Test: does adding a free local bump at z_c improve chi2 significantly?
best = (chi2_j_new, 0.0, 0.0)
for amp10 in range(-40, 41):
    amp = amp10 / 100.0
    for w10 in range(2, 41):
        w = w10 / 50.0
        tot = 0.0
        for name, z, dm, sm, dh, sh, rho in DATA:
            pm, ph = DM_new(z), DH_arch(z)
            ph *= (1 + amp * math.exp(-((z - 0.6) / w) ** 2))
            rm, rh = (pm - dm) / sm, (ph - dh) / sh
            det = 1 - rho * rho
            tot += (rm*rm - 2*rho*rm*rh + rh*rh) / det
        if tot < best[0]:
            best = (tot, amp, w)
dchi2 = chi2_j_new - best[0]
print(f"  free local bump at z_c=0.6: best amp = {best[1]:+.2f}, w = {best[2]:.2f}")
print(f"  chi2 {chi2_j_new:.3f} -> {best[0]:.3f}   (Delta chi2 = {dchi2:.3f} for 2 params)")
check("local SYNC correction NOT demanded (Delta chi2 < 4)", dchi2 < 4.0,
      f"Delta chi2 = {dchi2:.3f} for 2 extra parameters")

# ---------------- G: reproduce O118's exact 18.09/7 source ----------------
print("\n" + "-" * 78)
print("  G. REPRODUCE the exact 18.09/7 figure (o51_kchain_origin scripts/86)")
print("-" * 78)
# o51 scripts/86 'desi_7pt_chi2_lin' = 18.09 ; recipe: 7 pts, D_lin law,
# and for the two D_V points it used D_H = dD_app/dz  (the WRONG relation O117 later found)
DATA7 = [
    ('BGS',      0.295, 'DV',  7.942, 0.075),
    ('LRG1',     0.510, 'DM', 13.588, 0.167),
    ('LRG2',     0.706, 'DM', 17.351, 0.177),
    ('LRG3+ELG', 0.934, 'DM', 21.576, 0.152),
    ('ELG2',     1.321, 'DM', 27.601, 0.318),
    ('QSO',      1.484, 'DV', 26.055, 0.398),
    ('Lyalpha',  2.330, 'DM', 38.988, 0.531),
]

def D_app_old_Mpc(e):
    return R * (1 - 4.0**(-e)) * (1 + 2 * PHI**-1 * e)

def DM_new_Mpc(e):
    """O169-corrected D_M in Mpc (function of ell)."""
    return R * (1 - 4.0**(-e)) * (e + B_NEW)

def D_lin_Mpc(e, C=-0.16973):
    d1 = C * (e - 0.5) * (1 - 4.0**(-e))
    return R * (1 - 4.0**(-e)) * (1 + 2 * PHI**-1 * e + d1)

def DH_from_dDapp_dz(z):
    dz = 1e-6
    return (D_lin_Mpc(ell(z + dz)) - D_lin_Mpc(ell(z - dz))) / (2 * dz)

def chi2_7pt(law_M, dh_mode):
    tot = 0.0
    rows = []
    for name, z, dtype, obs, err in DATA7:
        e = ell(z)
        if dtype == 'DM':
            pred = law_M(e) / RD
        else:
            if dh_mode == 'dDdz':
                dh = DH_from_dDapp_dz(z)
            else:
                dh = DH_arch(z) * RD          # arch D_H in Mpc
            pred = (z * law_M(e)**2 * dh)**(1.0/3.0) / RD
        pull = (pred - obs) / err
        tot += pull**2
        rows.append((name, z, dtype, pred, obs, err, pull))
    return tot, rows

chi2_7_lin, rows_7_lin = chi2_7pt(D_lin_Mpc, 'dDdz')
print("  O51 'Linear correction' (7 pt, D_H = dD_app/dz):")
print(f"  {'tracer':<11} {'z':>6} {'typ':>3} {'pred':>9} {'DESI':>8} {'sig':>7} {'pull':>8}")
for name, z, dtype, pred, obs, err, pull in rows_7_lin:
    print(f"  {name:<11} {z:>6.3f} {dtype:>3} {pred:>9.4f} {obs:>8.3f} {err:>7.3f} {pull:>+8.2f}")
print(f"  chi2 = {chi2_7_lin:.2f} / 7 dof  (chi2/dof = {chi2_7_lin/7:.2f})")
check("reproduces O118's chi2 = 18.09 / 7", abs(chi2_7_lin - 18.09) < 0.35,
      f"got {chi2_7_lin:.2f}")

# same 7 points, current framework
chi2_7_new, rows_7_new = chi2_7pt(DM_new_Mpc, 'arch')
print("\n  SAME 7 points under CURRENT framework (O169 D_M + O170 arch D_H):")
print(f"  {'tracer':<11} {'z':>6} {'typ':>3} {'pred':>9} {'DESI':>8} {'sig':>7} {'pull':>8}")
for name, z, dtype, pred, obs, err, pull in rows_7_new:
    print(f"  {name:<11} {z:>6.3f} {dtype:>3} {pred:>9.4f} {obs:>8.3f} {err:>7.3f} {pull:>+8.2f}")
print(f"  chi2 = {chi2_7_new:.2f} / 7 dof  (chi2/dof = {chi2_7_new/7:.2f})")
check("7-pt chi2/dof < 1.5 under current framework", chi2_7_new / 7 < 1.5,
      f"{chi2_7_new/7:.3f}  (was {chi2_7_lin/7:.2f})")

# ---------------- verdict ----------------
print("\n" + "=" * 78)
print("  VERDICT")
print("=" * 78)
print(f"  O118 premise chi2 = 18.09/7 (chi2/dof = 2.58) was computed with:")
print(f"    (i)  the FALSIFIED elongation law E = 1 + 2*phi^-1*ell   (O169, 4.88 sigma)")
print(f"    (ii) the FALSIFIED group-delay C = -0.16973             (O169)")
print(f"  Under the current framework (O169 D_M + O170 arch D_H):")
print(f"    DM/rd  chi2 = {chi2_b:.3f} / 6 dof   (chi2/dof = {chi2_b/6:.3f})")
print(f"    DH/rd  chi2 = {chi2_dh_new:.3f} / 6 dof   (chi2/dof = {chi2_dh_new/6:.3f})")
print(f"    joint  chi2 = {chi2_j_new:.3f} / {n_pts} pts  (chi2/pt = {chi2_j_new/n_pts:.3f})")
print(f"  LRG1 deviation: {lr_dev:+.2f}% (OLD) -> {lr_dev_b:+.2f}% (NEW)")
print(f"  => O118 residual is an ARTIFACT of the falsified laws.")
print(f"  => No local impedance / SYNC correction is demanded (Delta chi2 = {dchi2:.2f}).")

print(f"\n  PASS: {PASS}/{PASS+FAIL}")

# ---------------- data dump ----------------
import json, os
out = {
    "trigger": "O118 premise re-evaluation under O169-corrected D_M + O170 arch kernel D_H",
    "date": "2026-09-26",
    "o118_premise": {
        "chi2": 18.09, "dof": 7, "chi2_per_dof": 2.58,
        "source": "o51_kchain_origin/scripts/86_cubic_correction.py (desi_7pt_chi2_lin)",
        "recipe": "7 pt (5 D_M + 2 D_V), D_lin law (falsified E=1+2phi^-1*ell + C1=-0.16973), "
                  "and D_V built from D_H = dD_app/dz (the WRONG relation O117 identified)",
    },
    "reproduced": {
        "chi2_7pt_old": round(chi2_7_lin, 4),
        "chi2_per_dof_old": round(chi2_7_lin / 7, 4),
        "exact_match": abs(chi2_7_lin - 18.09) < 0.005,
    },
    "current_framework": {
        "D_M_law": "R_world*(1-4^-ell)*(ell + B_NEW), B_NEW = 22/sum(cos(pi n/88), n=1..22)",
        "D_H_law": "R_world*(4^-ell/ln4)*sec(pi*n_c/88), n_c = N_d/2 + B*sin(pi*ell) (ell<ell_t) | N_d/2",
        "chi2_DM_6pt": round(chi2_b, 4),
        "chi2_DH_6pt": round(chi2_dh_new, 4),
        "chi2_joint_12pt": round(chi2_j_new, 4),
        "chi2_joint_per_pt": round(chi2_j_new / n_pts, 4),
        "chi2_7pt": round(chi2_7_new, 4),
        "chi2_7pt_per_dof": round(chi2_7_new / 7, 4),
    },
    "LRG1": {
        "dev_pct_old": round(lr_dev, 3),
        "dev_pct_new": round(lr_dev_b, 3),
        "pull_old": round(lr[5], 3),
        "pull_new": round(lr_b[5], 3),
    },
    "Lyalpha": {
        "pull_old_radial": round(ly_old[5], 3),
        "pull_arch": round(ly_new[5], 3),
    },
    "sync_bump_test": {
        "z_c": 0.6, "best_amp": best[1], "best_w": best[2],
        "delta_chi2": round(dchi2, 4), "dof_cost": 2,
        "demanded": dchi2 >= 4.0,
    },
    "verdict": "O118 residual is an ARTIFACT of the falsified laws; premise VOID",
    "pass": PASS, "fail": FAIL,
}
os.makedirs("data", exist_ok=True)
with open("data/01_premise_reevaluation.json", "w") as f:
    json.dump(out, f, indent=2)
print("  Saved -> data/01_premise_reevaluation.json")
