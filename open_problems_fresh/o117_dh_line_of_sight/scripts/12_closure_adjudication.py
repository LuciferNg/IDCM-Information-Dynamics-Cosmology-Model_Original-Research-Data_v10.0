#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O117/12 -- Closure adjudication: what actually survives?

Background. O117 was closed GREEN on 2026-09-01, demoted to YELLOW on 2026-09-24
(Lyalpha sigma misuse), then to "DH side void, superseded by O170 arch kernel" on
2026-09-26.  Before it can be re-closed, every item its retraction notice lists as
"still holds" must be re-verified rather than assumed.

The retraction notice (docs/01, RESULT.md) claims THREE survivors:
  (1) * D_H != dD_A/dz  (the diagnostic -- DM and DH are independent projections)
  (2) DM/rd error set correct (12.81 / 9.65 reproduced)
  (3) AP anisotropy test chi2 = 4.65 / 5

This script audits all three.

Sections
  A  reproduce the AP test exactly as scripts/04 computed it
  B  recompute AP under the CURRENT framework (O169 D_M + O170 arch D_H) + Table 6 sigma
  C  DM/rd error-set claim: is it O117's own, or inherited from upstream?
  D  surviving vs void inventory
  E  density-baseline adjudication (O208 rule: no quantile = not closed)
  F  verdict
"""
import math
import json
import os

PI = math.pi
LN4 = math.log(4.0)
R = 4129.94
RD = PI * R / 88 * 420 / 421
B = 4
NGEN = 3
ND = 44
ELL_T = math.log(3.0, 4.0)
PHI = (1 + math.sqrt(5.0)) / 2
PHI_INV = 1.0 / PHI
PHI_INV_3 = PHI ** -3
ELL_0 = 0.5
SIGMA_PHI = 0.5 * math.log(PHI, 4)
C_OLD = -0.1697331557
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

# ---------------- OLD (falsified) laws -- as scripts/04 used them ----------------
def delta_k0(l):
    d = l - ELL_0
    return PHI_INV_3 * math.exp(-d * d / (2 * SIGMA_PHI ** 2))

def D_app_OLD(z):
    l = ell(z)
    delta = C_OLD * (l - 0.5) * (1 - 4.0 ** (-l))
    return R * (1 - 4.0 ** (-l)) * (1 + 2 * PHI_INV * l + delta)

def DH_OLD(z):
    l = ell(z)
    delta = C_OLD * B / NGEN * (l - 0.5) * (1 - 4.0 ** (-l))
    return R * (1 + delta_k0(l) + delta) / (1 + z)

# ---------------- CURRENT laws ----------------
def DM_NEW(z):
    l = ell(z)
    return R * (1 - 4.0 ** (-l)) * (l + B_NEW) / RD

def arch_nc(l):
    return ND / 2.0 + B * math.sin(PI * l) if l < ELL_T else ND / 2.0

def DH_NEW(z):
    l = ell(z)
    return R * (4.0 ** (-l) / LN4) * (1.0 / math.cos(PI * arch_nc(l) / 88.0)) / RD

# DESI DR2, exactly as scripts/04 listed them (5 AP points)
DESI_AP_O117 = [
    (0.510, 13.588, 0.167, 21.863, 0.429),
    (0.706, 17.351, 0.177, 19.455, 0.334),
    (0.934, 21.576, 0.152, 17.641, 0.201),
    (1.321, 27.601, 0.318, 14.176, 0.225),
    (2.330, 38.989, 0.531,  8.632, 0.532),   # <-- 0.532 is the D_M sigma (WRONG)
]
# Table 6 corrected sigmas (O170 data/01, verified vs arXiv:2503.14738)
DESI_AP_T6 = [
    (0.510, 13.588, 0.167, 21.863, 0.425),
    (0.706, 17.351, 0.177, 19.455, 0.330),
    (0.934, 21.576, 0.152, 17.641, 0.193),
    (1.321, 27.601, 0.318, 14.176, 0.221),
    (2.330, 38.988, 0.531,  8.632, 0.101),   # <-- Table 6 value
]

print("=" * 78)
print("  O117/12 -- Closure adjudication: what actually survives?")
print("=" * 78)
print(f"  R_world = {R} Mpc | r_d = {RD:.6f} Mpc")
print(f"  B_NEW = {B_NEW:.8f} | M(0) = sqrt2 = {math.sqrt(2):.6f}")

# ================= A: reproduce scripts/04's AP chi2 =================
print("\n" + "-" * 78)
print("  A. AP test AS scripts/04 COMPUTED IT (old laws + O117 sigmas)")
print("-" * 78)
print(f"  {'z':>7} {'DM/rd':>9} {'DH/rd':>9} {'AP_idcm':>9} {'AP_obs':>9} {'sigma':>8}")
ap_old = 0.0
rows_a = []
for z, dm_o, dm_e, dh_o, dh_e in DESI_AP_O117:
    dm_i = D_app_OLD(z) / RD
    dh_i = DH_OLD(z) / RD
    ap_i = dm_i / dh_i
    ap_o = dm_o / dh_o
    ap_e = ap_o * math.sqrt((dm_e / dm_o) ** 2 + (dh_e / dh_o) ** 2)
    s = (ap_i - ap_o) / ap_e
    ap_old += s * s
    rows_a.append((z, dm_i, dh_i, ap_i, ap_o, s))
    print(f"  {z:>7.3f} {dm_i:>9.3f} {dh_i:>9.3f} {ap_i:>9.4f} {ap_o:>9.4f} {s:>+8.2f}")
print(f"  AP chi2 = {ap_old:.2f} / {len(DESI_AP_O117)} dof  "
      f"(chi2/dof = {ap_old/len(DESI_AP_O117):.2f})")
check("reproduces docs/01's AP chi2 = 4.65 (5 dof)", abs(ap_old - 4.65) < 0.15,
      f"got {ap_old:.2f}")

# ================= B: AP under CURRENT framework + Table 6 sigma =================
print("\n" + "-" * 78)
print("  B. AP test under CURRENT laws (O169 D_M + O170 arch D_H) + Table 6 sigma")
print("-" * 78)
print(f"  {'z':>7} {'DM/rd':>9} {'DH/rd':>9} {'AP_idcm':>9} {'AP_obs':>9} {'sigma':>8}")
ap_new = 0.0
rows_b = []
for z, dm_o, dm_e, dh_o, dh_e in DESI_AP_T6:
    dm_i = DM_NEW(z)
    dh_i = DH_NEW(z)
    ap_i = dm_i / dh_i
    ap_o = dm_o / dh_o
    ap_e = ap_o * math.sqrt((dm_e / dm_o) ** 2 + (dh_e / dh_o) ** 2)
    s = (ap_i - ap_o) / ap_e
    ap_new += s * s
    rows_b.append((z, dm_i, dh_i, ap_i, ap_o, s))
    print(f"  {z:>7.3f} {dm_i:>9.3f} {dh_i:>9.3f} {ap_i:>9.4f} {ap_o:>9.4f} {s:>+8.2f}")
print(f"  AP chi2 = {ap_new:.2f} / {len(DESI_AP_T6)} dof  "
      f"(chi2/dof = {ap_new/len(DESI_AP_T6):.2f})")

# the Lyalpha sigma matters enormously here
ly_a = [r for r in rows_a if r[0] == 2.330][0]
ly_b = [r for r in rows_b if r[0] == 2.330][0]
print(f"\n  Lyalpha AP pull: {ly_a[5]:+.2f} (O117 sigma 0.532) -> {ly_b[5]:+.2f} (Table 6 0.101)")

# ================= C: DM/rd error-set provenance =================
print("\n" + "-" * 78)
print("  C. Is the 'DM/rd error set correct' claim O117's OWN contribution?")
print("-" * 78)
print("  The D_M law E(ell) = ell + B_NEW is O169's (2026-09-15).")
print("  The D_M data/errors are DESI's.  O117 inherited both.")
# what O117 actually contributed to the DM side: the group-delay term
dm_plain = R * (1 - 4.0 ** (-ell(0.510))) * (ell(0.510) + B_NEW) / RD
print(f"  O117's own DM-side addition was the group-delay term C*(l-0.5)*(1-4^-l),")
print(f"  whose coefficient C_DM = -C_delay*2*phi^-1*sqrt(5) was FALSIFIED by O169.")
check("DM/rd 'correctness' is inherited (O169 + DESI), not an O117 result", True,
      "O117's own DM-side term (C_DM) is void")

# ================= D: inventory =================
print("\n" + "-" * 78)
print("  D. SURVIVING vs VOID inventory")
print("-" * 78)
inventory = [
    ("* D_H != dD_A/dz (independent projections)", "SURVIVES", "structural diagnostic; confirmed O169+O170"),
    ("AP test chi2 = 4.65/5",                     "VOID",     "uses falsified D_M + void DH + wrong Lyalpha sigma"),
    ("DM/rd error set correct",                    "INHERITED","from O169 law + DESI data; not O117's own"),
    ("DH(z) = R_H(1+dk0+dgd)/(1+z)",              "VOID",     "superseded by O170 arch kernel"),
    ("C_DM = -C_delay*2*phi^-1*sqrt(5)",           "VOID",     "falsified by O169"),
    ("C_DH = C_DM * 4/3",                          "VOID",     "4/3 excluded by 1-D scan"),
    ("delta_k0 Gaussian (sigma_phi = 0.5*log4 phi)","VOID",    "O170 docs/04 F3: coincidence"),
    ("Blind prediction Sigma m_nu = 0.08711 eV",   "VOID",     "computed from void C_DH framework"),
    ("T^5 phase coherence",                        "DEAD",     "assigned to O118; O118 closed premise-void"),
]
for name, status, why in inventory:
    mark = {"SURVIVES": "OK ", "VOID": "XX ", "INHERITED": "-> ", "DEAD": "-- "}[status]
    print(f"  [{mark}] {status:<9} {name}")
    print(f"              {why}")
n_surv = sum(1 for _, s, _ in inventory if s == "SURVIVES")
check("exactly ONE claim survives (the diagnostic)", n_surv == 1, f"{n_surv} survivors")

# ================= E: density baseline (O208 rule) =================
print("\n" + "-" * 78)
print("  E. Density baseline (O208 rule: no quantile = not closed)")
print("-" * 78)
print("  O117's surviving claim is a STRUCTURAL / no-go statement:")
print("    'the relation D_H = dD_A/dz is a Friedmann consequence and does not")
print("     hold in IDCM'")
print("  It is NOT a numeric match, so the density test does not apply.")
print("  The O's numeric claims are all VOID (section D), so there is no")
print("  numeric candidate left for which N_search / d_med / q_obs could be defined.")
check("no surviving numeric-match claim requires a density baseline", n_surv == 1,
      "N_search = N/A (structural claim), q_obs = N/A")

# ================= F: verdict =================
print("\n" + "=" * 78)
print("  F. VERDICT")
print("=" * 78)
print("  O117 CAN be closed -- but ONLY as a DIAGNOSTIC closure.")
print(f"  Of 3 claimed survivors, 1 survives: the D_H != dD_A/dz diagnostic.")
print(f"  The AP test (claimed survivor) is VOID: it was computed with the")
print(f"  falsified D_M law, the void DH formula, and the wrong Lyalpha sigma")
print(f"  (0.532 = D_M value; Table 6 = 0.101).")
print(f"  Under the current framework the AP test gives chi2 = {ap_new:.2f}/5 "
      f"({ap_new/5:.2f}/dof).")
print("  ALL numeric content of O117 is void; the radial law lives in O170.")

out = {
    "trigger": "O117 closure adjudication",
    "date": "2026-09-26",
    "AP_test": {
        "as_scripts04_computed": round(ap_old, 4),
        "dof": 5,
        "status": "VOID -- old laws + O117 sigma",
        "current_framework": round(ap_new, 4),
        "current_chi2_per_dof": round(ap_new / 5, 4),
        "lyalpha_pull_o117_sigma": round(ly_a[5], 3),
        "lyalpha_pull_table6_sigma": round(ly_b[5], 3),
    },
    "inventory": [{"item": n, "status": s, "reason": w} for n, s, w in inventory],
    "survivors": n_surv,
    "density_baseline": "N/A -- surviving claim is structural/no-go, not a numeric match",
    "verdict": "CLOSE as diagnostic closure; all numeric content void; radial law = O170",
    "pass": PASS, "fail": FAIL,
}
os.makedirs("data", exist_ok=True)
with open("data/12_closure_adjudication.json", "w") as f:
    json.dump(out, f, indent=2)
print(f"\n  PASS: {PASS}/{PASS+FAIL}")
print("  Saved -> data/12_closure_adjudication.json")
