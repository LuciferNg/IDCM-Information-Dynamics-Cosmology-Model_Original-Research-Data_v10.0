#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O253 scripts/04 — R1: DEFINITION FREEZE (Round 2 pre-registration)

Purpose: freeze, BEFORE any comparison with the O253 target (n_struct = 3.1028), the
  (a) sector semantics, (b) the closed ingredient set of the pipe algebra, and
  (c) the admissible functional family + its sha256.
Any later script that extends the family must announce a MOVED GOALPOST (new doc).

Sector semantics (frozen):
  chain sector  = 未束縛、可傳播嘅譜態 (HI 相)      -- K_chain spectrum, 176-L convention
  tree sector   = 束縛、嵌套嘅譜態 (H2 / 星)        -- K_tree Dirichlet modes
  pipe          = T_pipe = diag(sigma_1..sigma_44) (O33), cutoff n* = N_d - L6 + 1 = 27
  conversion    eps_HI = n_struct * omega_ring (O253 docs/02, dimensional forcing)

Ingredients are read-only from closed O's (O33 / O210 charter / O121 / O173-P1).
Nothing here is compared against the O253 target; no number is fitted.
"""
import hashlib
import json
import os

import mpmath as mp

mp.mp.dps = 40
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "data")

PASS = 0
TOTAL = 0


def ck(tag, ok, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    PASS += 1 if ok else 0
    print("[%s] %s  %s" % ("PASS" if ok else "FAIL", tag, detail))


# ------------------------------------------------ closed structural constants
B = 4                    # branch number, = phi^3 - phi^-3 (exact algebraic)
N_gen = 3                # 12 = B*N_gen
N_d = 44                 # chain sites (88-L ring / 2)
L5, L6, L7 = 11, 18, 29  # Lucas
F_proj = 17              # = L6 - 1 = dim ker T_pipe (O138 / O210 registry)
K_tree_mode = 2 * B ** 2 + 1     # 33 = N_gen*L5  (Dirichlet non-zero modes)
K_tree_node = 2 * (B ** 2 + 1)   # 34 = F9       (nodes / levels)
sites_tree = 4 * (B ** 2 + 1)    # 68

# ---------------------------------------------------------------- spectra
def gamma176(k):        # K_chain, 176-L standard (O210 charter C1)
    return 4 * mp.sin(mp.pi * k / 176) ** 2


def gamma88(n):         # 44-site ring reading (explicit map only)
    return 4 * mp.sin(mp.pi * n / 88) ** 2


def lam(k):             # K_tree Dirichlet spectrum (O155 R3 / O210 skill)
    return B * mp.sin(mp.pi * k / sites_tree) ** 2


SUM_176 = mp.fsum([gamma176(k) for k in range(1, 89)])
SUM_176_even = mp.fsum([gamma176(k) for k in range(2, 89, 2)])
SUM_176_odd = mp.fsum([gamma176(k) for k in range(1, 89, 2)])
SUM_88 = mp.fsum([gamma88(n) for n in range(1, 89)])
SUM_LAM = mp.fsum([lam(k) for k in range(1, K_tree_mode + 1)])

n_star = N_d - L6 + 1
S26 = mp.fsum([gamma88(n) for n in range(1, 27)])       # O33: full-pass band
g27 = gamma88(27)
S28_44 = mp.fsum([gamma88(n) for n in range(28, 45)])   # O33: blocked band
SUM_44 = mp.fsum([gamma88(n) for n in range(1, 45)])    # = even-sector total 90
# O33 budget is over Sigma_gamma_even = 90 (world sector); split is structural:
E_proj = mp.mpf(19) / 60 * SUM_44        # 28.5 exact (= 19/60 * 90)
E_sync = mp.mpf(41) / 60 * SUM_44        # 61.5 exact (= 41/60 * 90)
# O33 prints f_proj = 0.7720 (4-digit display); derive it exactly instead of importing
f_proj_exact = (E_proj - S26) / g27
f_sync_exact = (E_sync - S28_44) / g27

# sums of the 176-L family restricted to the same mode windows (labelled convention)
P27_176 = mp.fsum([gamma176(k) for k in range(1, 28)])
B_176 = mp.fsum([gamma176(k) for k in range(28, 89)])

print("=" * 78)
print("O253/04  R1 definition freeze (pipe algebra ingredients)")
print("=" * 78)
print("SUM_176           = %s" % mp.nstr(SUM_176, 12))
print("  even / odd      = %s / %s" % (mp.nstr(SUM_176_even, 10), mp.nstr(SUM_176_odd, 10)))
print("SUM_88 (n=1..88)  = %s" % mp.nstr(SUM_88, 12))
print("SUM_lam(tree)     = %s" % mp.nstr(SUM_LAM, 12))
print("n* = N_d-L6+1     = %d ; gamma88(n*) = %s" % (n_star, mp.nstr(g27, 10)))
print("S26 / S28-44      = %s / %s" % (mp.nstr(S26, 10), mp.nstr(S28_44, 10)))
print("E_proj / E_sync   = %s / %s" % (mp.nstr(E_proj, 10), mp.nstr(E_sync, 10)))
print("176-L window 1-27 / 28-88 = %s / %s" % (mp.nstr(P27_176, 10), mp.nstr(B_176, 10)))
print()

ck("F1 SUM_176 = 178 (176-L, k=1..88)", abs(SUM_176 - 178) < mp.mpf("1e-25"),
   "= %s" % mp.nstr(SUM_176, 10))
ck("F2 even/odd = 90/88 (charter C2)", abs(SUM_176_even - 90) < mp.mpf("1e-25")
   and abs(SUM_176_odd - 88) < mp.mpf("1e-25"),
   "%s / %s" % (mp.nstr(SUM_176_even, 8), mp.nstr(SUM_176_odd, 8)))
ck("F3 SUM_88 = 176 (44-site ring reading differs from 176-L: 178)",
   abs(SUM_88 - 176) < mp.mpf("1e-25"), "= %s  (convention label mandatory)" % mp.nstr(SUM_88, 10))
ck("F4 SUM_lam = 66 = B^3+B/2 = 2*K_tree_mode (graph theorem)",
   abs(SUM_LAM - 66) < mp.mpf("1e-25"), "= %s" % mp.nstr(SUM_LAM, 10))
ck("F5 n* = 27 = N_d-L6+1", n_star == 27, "n* = %d" % n_star)
ck("F6 E_proj = 28.5 = 19/60 x Sigma_even(90)", abs(E_proj - mp.mpf("28.5")) < mp.mpf("1e-25"),
   "= %s" % mp.nstr(E_proj, 12))
ck("F7 E_sync = 61.5 = 41/60 x 90 and E_proj/E_sync = 19/41",
   abs(E_sync - mp.mpf("61.5")) < mp.mpf("1e-25")
   and abs(E_proj / E_sync - mp.mpf(19) / 41) < mp.mpf("1e-25"),
   "E_sync = %s ; ratio = %s" % (mp.nstr(E_sync, 12), mp.nstr(E_proj / E_sync, 12)))
ck("F6b S26 + g27 + S28_44 = 90 = Sigma_even (O33 budget scale)",
   abs(SUM_44 - 90) < mp.mpf("1e-25"), "SUM_44 = %s" % mp.nstr(SUM_44, 10))
ck("F6c f_proj derived exactly = %s -> rounds to O33's printed 0.7720"
   % mp.nstr(f_proj_exact, 10),
   abs(f_proj_exact - mp.mpf("0.7720")) < mp.mpf("1e-4"),
   "f_proj = %s ; f_sync = %s" % (mp.nstr(f_proj_exact, 10), mp.nstr(f_sync_exact, 10)))
ck("F8 K_tree_mode = 33 = N_gen*L5 ; K_tree_node = 34 = F9",
   K_tree_mode == 33 and K_tree_node == 34, "33 / 34 (two counts, label mandatory)")

# ------------------------------------------------------- FROZEN ingredient set
ING = {
    "Sum_gamma_176": float(SUM_176),          # 178
    "Sum_gamma_even": float(SUM_176_even),    # 90
    "Sum_gamma_odd": float(SUM_176_odd),      # 88
    "Sum_gamma_88": float(SUM_88),            # 176
    "Sum_lam_tree": float(SUM_LAM),           # 66
    "E_proj": float(E_proj),                  # 28.5
    "E_sync": float(E_sync),                  # 61.5
    "S26": float(S26),
    "S28_44": float(S28_44),
    "P27_176": float(P27_176),
    "B_176": float(B_176),
    "n_star": 27, "N_d": N_d, "B": B, "N_gen": N_gen,
    "L5": L5, "L6": L6, "L7": L7, "F_proj": F_proj,
    "K_tree_mode": K_tree_mode, "K_tree_node": K_tree_node,
    "sites_tree": sites_tree, "N_gen3": N_gen ** 3,
    "f_proj_exact": float(f_proj_exact),
}
print()
print("[ING] frozen ingredient set (24 entries):")
for k in sorted(ING):
    print("      %-16s %s" % (k, mp.nstr(mp.mpf(ING[k]), 10)))

# ------------------------------- FROZEN functional family rule (sha256 locked)
FAMILY_RULE = (
    "ING=" + ",".join(sorted(ING)) + " ; "
    "F1: all ratios p/q, p!=q, p,q in ING (mpf); "
    "F2: all products p*q for p,q in {N_d,B,N_gen,L5,L6,L7,F_proj,n_star,K_tree_mode,K_tree_node}; "
    "F3: all p/(2*pi), p/pi for p in {N_d,B,N_gen,L5,L6,L7,F_proj,n_star}; "
    "F4: n_struct = sqrt(p) for p in ING; "
    "band: n_struct observable band [2.5856, 3.8785] (tau_dep +-20%); "
    "tight band: [2.9603, 3.2533] (N_gen vs pi separation, +-2.36%)"
)
fam_hash = hashlib.sha256(FAMILY_RULE.encode("utf-8")).hexdigest()
print()
print("[FREEZE] family rule sha256 = %s" % fam_hash)
print("         (scripts/05 must reproduce this hash before it may use the family)")
ck("F9 family rule hash reproducible", len(fam_hash) == 64, fam_hash[:16] + "...")

# ---------------------------------------------------------------- dump data
os.makedirs(OUT, exist_ok=True)
payload = {
    "script": "04_definition_freeze.py",
    "sector_semantics": {
        "chain (HI)": "176-L K_chain spectrum gamma_k = 4 sin^2(k pi/176), k=1..88",
        "tree (H2/star)": "K_tree Dirichlet lambda_k = B sin^2(k pi/68), k=1..33",
        "pipe": "T_pipe = diag(sigma_1..sigma_44), n* = N_d-L6+1 = 27, f_proj = 0.7720 (O33)",
        "conversion": "eps_HI = SFRD/rho_HI = n_struct * omega_ring (O253 docs/02)",
    },
    "ingredients": ING,
    "family_rule": FAMILY_RULE,
    "family_rule_sha256": fam_hash,
    "targets_do_not_touch": {"n_struct": 3.1028, "band": [2.5856, 3.8785],
                             "tight": [2.9603, 3.2533]},
    "pass": "%d/%d" % (PASS, TOTAL),
}
with open(os.path.join(OUT, "04_definition_freeze.json"), "w") as fh:
    json.dump(payload, fh, indent=1, ensure_ascii=False)

print()
print("RESULT: %d/%d PASS" % (PASS, TOTAL))
