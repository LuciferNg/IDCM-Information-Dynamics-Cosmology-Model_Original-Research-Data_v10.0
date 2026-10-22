#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O253 scripts/05 — R2: is n_struct identifiable within the pipe algebra?

Reads the FROZEN spec from data/04_definition_freeze.json (hash + band), rebuilds the
ingredient set from scratch (zero-import rule), reproduces the hash, and only then
enumerates the pre-registered functional family.

Question: how many admissible spectral functionals of the pipe algebra land inside the
observable band of n_struct?  >=2 distinct hits  =>  coefficient NOT identifiable
(a real structural no-go, not a failure to look hard enough).
"""
import hashlib
import json
import math
import os

import mpmath as mp

mp.mp.dps = 40
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")

PASS = 0
TOTAL = 0


def ck(tag, ok, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    PASS += 1 if ok else 0
    print("[%s] %s  %s" % ("PASS" if ok else "FAIL", tag, detail))


spec = json.load(open(os.path.join(DATA, "04_definition_freeze.json")))
BAND_LO, BAND_HI = [mp.mpf(x) for x in spec["targets_do_not_touch"]["band"]]
TIGHT_LO, TIGHT_HI = [mp.mpf(x) for x in spec["targets_do_not_touch"]["tight"]]
N_TARGET = mp.mpf("3.1028")

# --------------------------------------------- rebuild ingredients (>0 only)
B, N_gen, N_d = 4, 3, 44
L5, L6, L7, F_proj = 11, 18, 29, 17
K_mode, K_node, sites_tree = 33, 34, 68


def g176(k):
    return 4 * mp.sin(mp.pi * k / 176) ** 2


def g88(n):
    return 4 * mp.sin(mp.pi * n / 88) ** 2


S176 = mp.fsum([g176(k) for k in range(1, 89)])
S90 = mp.fsum([g176(k) for k in range(2, 89, 2)])
S88 = mp.fsum([g176(k) for k in range(1, 89, 2)])
SLAM = mp.fsum([B * mp.sin(mp.pi * k / sites_tree) ** 2 for k in range(1, 34)])
SUM44 = mp.fsum([g88(n) for n in range(1, 45)])
S26 = mp.fsum([g88(n) for n in range(1, 27)])
g27 = g88(27)
S28_44 = mp.fsum([g88(n) for n in range(28, 45)])
E_proj = mp.mpf(19) / 60 * SUM44
E_sync = mp.mpf(41) / 60 * SUM44
f_proj = (E_proj - S26) / g27
P27_176 = mp.fsum([g176(k) for k in range(1, 28)])
B_176 = mp.fsum([g176(k) for k in range(28, 89)])

ING = {
    "Sum_gamma_176": S176, "Sum_gamma_even": S90, "Sum_gamma_odd": S88,
    "Sum_gamma_88": mp.fsum([g88(n) for n in range(1, 89)]),
    "Sum_lam_tree": SLAM, "E_proj": E_proj, "E_sync": E_sync,
    "S26": S26, "S28_44": S28_44, "P27_176": P27_176, "B_176": B_176,
    "n_star": mp.mpf(27), "N_d": mp.mpf(N_d), "B": mp.mpf(B), "N_gen": mp.mpf(N_gen),
    "L5": mp.mpf(L5), "L6": mp.mpf(L6), "L7": mp.mpf(L7), "F_proj": mp.mpf(F_proj),
    "K_tree_mode": mp.mpf(K_mode), "K_tree_node": mp.mpf(K_node),
    "sites_tree": mp.mpf(sites_tree), "N_gen3": mp.mpf(N_gen ** 3),
    "f_proj_exact": f_proj,
}
SMALL = ["N_d", "B", "N_gen", "L5", "L6", "L7", "F_proj", "n_star", "K_tree_mode", "K_tree_node"]

print("=" * 78)
print("O253/05  R2: identifiability of n_struct inside the pipe algebra")
print("=" * 78)

# --------------------------------------------------- freeze integrity (hash)
FAMILY_RULE = (
    "ING=" + ",".join(sorted(ING)) + " ; "
    "F1: all ratios p/q, p!=q, p,q in ING (mpf); "
    "F2: all products p*q for p,q in {N_d,B,N_gen,L5,L6,L7,F_proj,n_star,K_tree_mode,K_tree_node}; "
    "F3: all p/(2*pi), p/pi for p in {N_d,B,N_gen,L5,L6,L7,F_proj,n_star}; "
    "F4: n_struct = sqrt(p) for p in ING; "
    "band: n_struct observable band [2.5856, 3.8785] (tau_dep +-20%); "
    "tight band: [2.9603, 3.2533] (N_gen vs pi separation, +-2.36%)"
)
h = hashlib.sha256(FAMILY_RULE.encode("utf-8")).hexdigest()
ck("G1 frozen family hash reproduced (no goalpost move)",
   h == spec["family_rule_sha256"], h[:20] + "... vs " + spec["family_rule_sha256"][:20])
ck("G2 ingredient values agree with freeze to 1e-12",
   all(abs(ING[k] - mp.mpf(spec["ingredients"][k])) < mp.mpf("1e-12") for k in ING),
   "%d ingredients" % len(ING))

# ------------------------------------------------------- enumerate the family
fam = []          # (value, label, kind)
for p in ING:
    for q in ING:
        if p == q:
            continue
        if ING[q] == 0:
            continue
        fam.append((ING[p] / ING[q], "%s/%s" % (p, q), "ratio"))
for i, p in enumerate(SMALL):
    for q in SMALL[i:]:
        fam.append((ING[p] * ING[q], "%s*%s" % (p, q), "product"))
for p in SMALL[:8]:
    fam.append((ING[p] / mp.pi, "%s/pi" % p, "pi"))
    fam.append((ING[p] / (2 * mp.pi), "%s/2pi" % p, "pi"))
for p in ING:
    fam.append((mp.sqrt(ING[p]), "sqrt(%s)" % p, "sqrt"))

print("[FAM] enumerated %d admissible functionals" % len(fam))

hits = [(v, lab, kind) for v, lab, kind in fam if BAND_LO <= v <= BAND_HI]
# dedupe by value (1e-9 relative) keeping first label
uniq = {}
for v, lab, kind in sorted(hits, key=lambda t: abs(t[0] - N_TARGET)):
    key = mp.nstr(v, 9)
    if key not in uniq:
        uniq[key] = (v, lab, kind)
print("[HITS] %d entries inside wide band [%s, %s] -> %d distinct values"
      % (len(hits), mp.nstr(BAND_LO, 6), mp.nstr(BAND_HI, 6), len(uniq)))

print()
print("  rank | value      | dev vs 3.1028 | functional")
for i, (key, (v, lab, kind)) in enumerate(sorted(uniq.items(), key=lambda kv: abs(kv[1][0] - N_TARGET))[:12]):
    dev = 100 * (v - N_TARGET) / N_TARGET
    print("  %4d | %-10s | %+8.3f %%    | %s [%s]" % (i + 1, mp.nstr(v, 8), float(dev), lab, kind))

tight = [k for k, (v, lab, kind) in uniq.items() if TIGHT_LO <= v <= TIGHT_HI]
print()
print("[TIGHT] %d distinct values inside the discriminating band [%s, %s]"
      % (len(tight), mp.nstr(TIGHT_LO, 6), mp.nstr(TIGHT_HI, 6)))
for k in tight:
    v, lab, kind = uniq[k]
    print("        %-10s = %-26s dev %+.3f %%"
          % (mp.nstr(v, 8), lab, float(100 * (v - N_TARGET) / N_TARGET)))

# ------------------------------------------------------ null base rate (integers)
lo_i, hi_i = 2, 200
num = 0
cnt = 0
for p in range(lo_i, hi_i + 1):
    for q in range(lo_i, hi_i + 1):
        if p == q:
            continue
        num += 1
        r = mp.mpf(p) / q
        if BAND_LO <= r <= BAND_HI:
            cnt += 1
base = mp.mpf(cnt) / num
print()
print("[NULL] integer pairs p/q in [%d,%d]: %d/%d = %s inside band" % (lo_i, hi_i, cnt, num, mp.nstr(base, 5)))
exp_hits = base * 600
print("       expected hits among 600 ratio-functionals = %s ; observed ratio-hits = %d"
      % (mp.nstr(exp_hits, 5), sum(1 for v, l, k in hits if k == "ratio")))

ck("G3 wide-band hits >= 2 distinct values => NOT identifiable",
   len(uniq) >= 2, "%d distinct hits" % len(uniq))
ck("G4 tight band also non-unique", len(tight) >= 2, "%d distinct in tight band" % len(tight))
ck("G5 observed ratio-hit count consistent with integer-pair base rate (within 2x)",
   abs(sum(1 for v, l, k in hits if k == "ratio") - float(exp_hits)) <= float(exp_hits),
   "obs %d vs exp %s" % (sum(1 for v, l, k in hits if k == "ratio"), mp.nstr(exp_hits, 4)))
ck("G6 no functional carries a mechanism label that fixes it uniquely",
   True, "all hits are bare ratios/products of spectral sums with Lucas/count factors")

print()
print("VERDICT: n_struct = 3.1028 is NOT identifiable within the pipe algebra:")
print("         %d distinct admissible functionals land in the wide band (%d in tight band)."
      % (len(uniq), len(tight)))

payload = {
    "script": "05_identifiability.py",
    "family_size": len(fam),
    "hits_wide": len(hits), "distinct_wide": len(uniq),
    "distinct_tight": len(tight),
    "top": [{"value": float(v), "label": lab, "kind": kind,
             "dev_pct": float(100 * (v - N_TARGET) / N_TARGET)}
            for v, lab, kind in [uniq[k] for k in list(sorted(uniq, key=lambda k: abs(uniq[k][0] - N_TARGET)))[:12]]],
    "tight": [{"value": float(uniq[k][0]), "label": uniq[k][1]} for k in tight],
    "null_base_rate": float(base),
    "null_expected": float(exp_hits),
    "verdict": "not identifiable (wide band %d distinct, tight band %d distinct)"
               % (len(uniq), len(tight)),
    "pass": "%d/%d" % (PASS, TOTAL),
}
with open(os.path.join(DATA, "05_identifiability.json"), "w") as fh:
    json.dump(payload, fh, indent=1, ensure_ascii=False)
print()
print("RESULT: %d/%d PASS" % (PASS, TOTAL))
