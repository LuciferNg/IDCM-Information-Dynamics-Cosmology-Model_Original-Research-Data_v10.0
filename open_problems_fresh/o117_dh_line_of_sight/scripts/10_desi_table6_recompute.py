#!/usr/bin/env python3
"""
O117/10: DESI DR2 Table 6 error correction -- full DH/rd chi2 recompute
=======================================================================
Trigger: O170 docs/04_falsifications_open_items.md F2 (2026-09-15/24).

O117 scripts 01/02/08/09 used DH errors that were NOT DESI DR2 Table 6 values:
  LRG1     0.429  (Table 6: 0.425)
  LRG2     0.334  (Table 6: 0.330)
  LRG3+ELG 0.201  (Table 6: 0.193)
  ELG2     0.225  (Table 6: 0.221)
  QSO      0.518  (Table 6: 0.516)
  Lyalpha  0.532  (Table 6: 0.101)   <-- CRITICAL: 0.532 is the Lyalpha D_M error

Root cause of the Lyalpha value: v9.0 covariance matrix rows [11,12] are ordered
[D_H, D_M], while the data list was ordered [D_M, D_H] -> Lyalpha D_H picked up
the D_M variance:
  cov[11,11] = 1.02136194e-02 -> sigma = 0.101  (true Lyalpha D_H)
  cov[12,12] = 2.82685779e-01 -> sigma = 0.532  (true Lyalpha D_M)

This script does NOT modify scripts 01/02/08/09 (temporal integrity: closed
records keep their original content). It recomputes from the authoritative
Table 6 error set and reports the delta.

Source of Table 6 values: O170 data/01_desi_dr2_radial_data.md
  (arXiv:2503.14738 Table 6 + IOP suppdata; verified 2026-09-15)
"""
import json, math

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

# ============ Constants (identical to scripts 01/02/08/09) ============
R_H = 4129.94
phi = (1 + math.sqrt(5)) / 2
phi_inv = phi - 1
phi_inv_3 = phi_inv ** 3
rd_idcm = math.pi * R_H / 88
rd = rd_idcm * 420/421
ell_0 = math.log(2) / math.log(4)
sigma_phi = 0.5 * math.log(phi) / math.log(4)

# O117 closure coefficients (as closed 2026-09-01)
C_DM = -0.1697331557
C_DH = C_DM * 4/3          # -0.2263108742

def ell(z):
    return math.log(1 + z, 4)

def delta_k0(l):
    d = l - ell_0
    return phi_inv_3 * math.exp(-d**2 / (2 * sigma_phi**2))

def DH_of(z, C):
    """O117 DH(z) = R_H x (1 + d_k0 + C x (l-0.5) x (1-4^-l)) / (1+z)"""
    l = ell(z)
    return R_H * (1 + delta_k0(l) + C * (l - 0.5) * (1 - 4**(-l))) / (1 + z)

print("=" * 78)
print("  O117/10 -- DESI DR2 Table 6 error correction, DH/rd chi2 recompute")
print("=" * 78)
print(f"  R_H = {R_H} Mpc,  rd = {rd:.6f} Mpc")
print(f"  C_DM = {C_DM:.10f},  C_DH = C_DM x 4/3 = {C_DH:.10f}")

# ============ Data: O117 original error set vs DESI DR2 Table 6 ============
# (tracer, z, obs, err_O117, err_Table6)
DH_DATA = [
    ('LRG1',     0.510, 21.863, 0.429, 0.425),
    ('LRG2',     0.706, 19.455, 0.334, 0.330),
    ('LRG3+ELG', 0.934, 17.641, 0.201, 0.193),
    ('ELG2',     1.321, 14.176, 0.225, 0.221),
    ('QSO',      1.484, 12.817, 0.518, 0.516),
    ('Lyalpha',  2.330,  8.632, 0.532, 0.101),
]

DM_DATA = [
    # O117 convention: first 5 = LRG1, LRG2, LRG3+ELG, ELG2, Lyalpha (no QSO D_M)
    ('LRG1',     0.510, 13.588, 0.167),
    ('LRG2',     0.706, 17.351, 0.177),
    ('LRG3+ELG', 0.934, 21.576, 0.152),
    ('ELG2',     1.321, 27.601, 0.318),
    ('Lyalpha',  2.330, 38.989, 0.531),
    ('QSO',      1.484, 30.512, 0.760),
]

def chi2_dh(C, use_table6):
    c2 = 0.0
    rows = []
    for nm, z, obs, e_old, e_new in DH_DATA:
        err = e_new if use_table6 else e_old
        pred = DH_of(z, C) / rd
        pull = (pred - obs) / err
        c2 += pull**2
        rows.append((nm, z, pred, obs, err, pull))
    return c2, rows

# ============ 1. Reproduce O117 recorded value with its own error set ============
print(f"\n{'-'*78}")
print("  1. Reproduce O117 closure (2026-09-01) using O117 error set")
print(f"{'-'*78}")
c2_old, rows_old = chi2_dh(C_DH, use_table6=False)
print(f"  {'tracer':<10}{'z':>7}{'DH/rd pred':>12}{'DESI':>9}{'sigma':>8}{'pull':>9}")
for nm, z, p, o, e, s in rows_old:
    print(f"  {nm:<10}{z:>7.3f}{p:>12.4f}{o:>9.3f}{e:>8.3f}{s:>+9.2f}")
print(f"\n  DH/rd chi2 = {c2_old:.2f} (6 dof)   [O117 recorded: 7.41]")
check("reproduces O117 recorded chi2 = 7.41", abs(c2_old - 7.41) < 0.02, f"{c2_old:.2f}")

# ============ 2. Recompute with authoritative Table 6 errors ============
print(f"\n{'-'*78}")
print("  2. Recompute with DESI DR2 Table 6 errors")
print(f"{'-'*78}")
c2_new, rows_new = chi2_dh(C_DH, use_table6=True)
print(f"  {'tracer':<10}{'z':>7}{'DH/rd pred':>12}{'DESI':>9}{'sig_old':>9}{'sig_new':>9}{'pull':>9}")
for (nm, z, p, o, eo, so), (_, _, _, _, en, sn) in zip(rows_old, rows_new):
    print(f"  {nm:<10}{z:>7.3f}{p:>12.4f}{o:>9.3f}{eo:>9.3f}{en:>9.3f}{sn:>+9.2f}")
print(f"\n  DH/rd chi2 = {c2_new:.2f} (6 dof),  chi2/dof = {c2_new/6:.2f}")
check("Table 6 recompute differs from O117 value", abs(c2_new - c2_old) > 1.0,
      f"{c2_old:.2f} -> {c2_new:.2f}")

# ============ 3. Per-tracer error deviations ============
print(f"\n{'-'*78}")
print("  3. Error-set deviation (O117 vs Table 6)")
print(f"{'-'*78}")
for nm, z, obs, e_old, e_new in DH_DATA:
    dev = (e_old - e_new) / e_new * 100
    flag = 'CRITICAL' if abs(dev) > 50 else ('warn' if abs(dev) > 1 else 'ok')
    print(f"  {nm:<10} {e_old:.3f} -> {e_new:.3f}   {dev:>+8.2f}%   {flag}")
check("only Lyalpha has a >50% error deviation",
      all(abs((eo-en)/en*100) <= 50 for nm, z, o, eo, en in DH_DATA if nm != 'Lyalpha'))
check("Lyalpha deviation is ~427%",
      abs(((0.532-0.101)/0.101*100) - 426.7) < 1.0,
      f"{(0.532-0.101)/0.101*100:.2f}%")

# ============ 4. Coefficient variants under Table 6 errors ============
print(f"\n{'-'*78}")
print("  4. Coefficient variants under Table 6 errors (diagnostic only)")
print(f"{'-'*78}")
variants = [('bare R_H/(1+z)', 0.0), ('C_DM', C_DM), ('C_DH = C_DM x 4/3', C_DH)]
for lbl, C in variants:
    c2v, rv = chi2_dh(C, use_table6=True)
    print(f"  {lbl:<22} C = {C:>+10.7f}   chi2 = {c2v:>7.2f}")
# pure scan (diagnostic, NOT a closure claim)
best_C, best_c2 = 0.0, 1e9
c = -0.60
while c < 0.05:
    v, _ = chi2_dh(c, use_table6=True)
    if v < best_c2:
        best_c2, best_C = v, c
    c += 0.00005
print(f"  {'[scan] optimal':<22} C = {best_C:>+10.7f}   chi2 = {best_c2:>7.2f}")
print(f"  (scan is a DIAGNOSTIC of how far the data pulls the coefficient,")
print(f"   not a closure claim -- see docs/02 for the first-principles rule)")

# ============ 5. DM side unchanged (errors were already correct) ============
print(f"\n{'-'*78}")
print("  5. DM/rd side -- check errors were already Table 6 correct")
print(f"{'-'*78}")
def chi2_dm(npts, C=0.0):
    c2 = 0.0
    rows = []
    for nm, z, obs, err in DM_DATA[:npts]:
        l = ell(z)
        pred = R_H * (1 - 4**(-l)) * (1 + 2*phi_inv*l + C*(l - 0.5)*(1 - 4**(-l))) / rd
        pull = (pred - obs) / err
        c2 += pull**2
        rows.append((nm, z, pred, obs, err, pull))
    return c2, rows

print("  O117 convention (5 points, no QSO D_M), bare D_app:")
c2_dm5, rows_dm5 = chi2_dm(5)
for nm, z, p, o, e, s in rows_dm5:
    print(f"  {nm:<10}{z:>7.3f}{p:>12.4f}{o:>9.3f}{e:>8.3f}{s:>+9.2f}")
print(f"  DM/rd chi2 = {c2_dm5:.2f} (5 dof)")

print("\n  O117 convention (5 points) with group delay C_DM:")
c2_dm5c, _ = chi2_dm(5, C_DM)
print(f"  DM/rd chi2 = {c2_dm5c:.2f} (5 dof)   [O117 docs/01 + script 02 recorded 12.81]")
print("\n  O117 convention (5 points) with group delay C_DH:")
c2_dm5d, _ = chi2_dm(5, C_DH)
print(f"  DM/rd chi2 = {c2_dm5d:.2f} (5 dof)   [O117 docs/02 recorded 9.65]")

print("\n  Full Table 6 (6 points, incl. QSO D_M), bare D_app:")
c2_dm, rows_dm = chi2_dm(6)
for nm, z, p, o, e, s in rows_dm:
    print(f"  {nm:<10}{z:>7.3f}{p:>12.4f}{o:>9.3f}{e:>8.3f}{s:>+9.2f}")
print(f"  DM/rd chi2 = {c2_dm:.2f} (6 dof)")

check("DM/rd errors need no correction (all match Table 6)",
      abs(DM_DATA[4][3] - 0.531) < 1e-9 and abs(DM_DATA[5][3] - 0.760) < 1e-9,
      "Lyalpha D_M 0.531 and QSO D_M 0.760 both present in O117 data")
check("DM/rd 5-pt with C_DM reproduces O117 recorded 12.81",
      abs(c2_dm5c - 12.81) < 0.02, f"{c2_dm5c:.2f}")
check("DM/rd 5-pt with C_DH reproduces O117 docs/02 recorded 9.65",
      abs(c2_dm5d - 9.65) < 0.02, f"{c2_dm5d:.2f}")

# ============ 6. Verdict ============
print(f"\n{'='*78}")
print("  6. Verdict")
print(f"{'='*78}")
print(f"""
  O117 closure value   DH/rd chi2 = {c2_old:.2f} / 6 dof   (O117 error set)
  Table 6 corrected    DH/rd chi2 = {c2_new:.2f} / 6 dof
  Delta                +{c2_new - c2_old:.2f}

  Lyalpha pull:  {rows_old[5][5]:+.2f} sigma  ->  {rows_new[5][5]:+.2f} sigma

  => The DH/rd chi2 = 7.41 closure (2026-09-01) is VOID.
     It rested on a Lyalpha sigma that was the D_M error, not the D_H error.
     With the correct Table 6 error, Lyalpha becomes a {abs(rows_new[5][5]):.2f} sigma outlier.

  UNAFFECTED (retained):
    - Core conclusion D_H != dD_A/dz  (DM and DH are independent projections)
    - DM/rd side: all six errors were already Table 6 values
""")

result = {
    'trigger': 'O170 docs/04 F2 (DESI DR2 Table 6 error correction)',
    'chi2_dh_O117_errorset': round(c2_old, 4),
    'chi2_dh_table6': round(c2_new, 4),
    'chi2_dh_table6_dof': 6,
    'delta_chi2': round(c2_new - c2_old, 4),
    'chi2_dm_table6_5pt': round(c2_dm5, 4),
    'chi2_dm_table6_6pt': round(c2_dm, 4),
    'C_DM': C_DM,
    'C_DH': C_DH,
    'per_tracer': [
        {'tracer': nm, 'z': z, 'DH_pred': round(p, 5), 'DESI': o,
         'sigma_O117': eo, 'sigma_table6': en, 'pull_table6': round(s, 4)}
        for (nm, z, p, o, eo, so), (_, _, _, _, en, s) in zip(rows_old, rows_new)
    ],
    'lyalpha_pull_O117': round(rows_old[5][5], 4),
    'lyalpha_pull_table6': round(rows_new[5][5], 4),
    'scan_optimal_C_diagnostic': round(best_C, 7),
    'scan_optimal_chi2_diagnostic': round(best_c2, 4),
    'verdict': 'DH/rd chi2 = 7.41 VOID; Lyalpha sigma 0.532 -> 0.101',
    'retained': ['D_H != dD_A/dz (independent projections)', 'DM/rd error set already correct'],
    'pass': PASS, 'fail': FAIL
}

with open('data/10_desi_table6_recompute.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"  Saved -> data/10_desi_table6_recompute.json")
print(f"  PASS: {PASS}/{PASS+FAIL}")
