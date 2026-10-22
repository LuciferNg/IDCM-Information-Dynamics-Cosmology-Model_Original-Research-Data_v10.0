#!/usr/bin/env python3
"""
O58 script 71 — FINAL VERIFIER for explorations AB/AC/AD.
"""
import os, json, numpy as np, math

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
results = []

def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

def main():
    print("=== O58 EXPLORATIONS AB/AC/AD FINAL VERIFIER ===\n")

    # AB: Σ|det| ≈ 4.4×npts across instances
    data = json.load(open(os.path.join(DATA, "sumdet_universality.json")))
    npts = np.array([r["npts"] for r in data])
    tot = np.array([r["total"] for r in data])
    ratio = tot / npts
    check("AB: 10 instances", len(data) == 10)
    check("AB: mean ratio ≈ 4.4", abs(np.mean(ratio) - 4.4) < 0.1,
          f"({np.mean(ratio):.3f})")
    check("AB: corr > 0.9", np.corrcoef(npts, tot)[0,1] > 0.9,
          f"({np.corrcoef(npts, tot)[0,1]:.3f})")
    check("AB: -χ+L₉ NOT universal", sum(1 for r in data if r["match"]) == 1,
          f"({sum(1 for r in data if r['match'])}/10)")

    # AD: div3 star=48 only canonical
    n_48 = sum(1 for r in data if abs(r["stars"].get("3", 0) - 48) < 1e-6)
    check("AD: div3 star=48 only canonical", n_48 == 1, f"({n_48}/10)")

    # AC: (36,98) vs control — no significance
    d3698 = json.load(open(os.path.join(DATA, "e_positions_lucas_universality.json")))
    dctrl = json.load(open(os.path.join(DATA, "e_positions_control_families.json")))
    luc = {1,2,3,4,7,11,18,29,47}
    # (36,98) excl e1
    te = tl = 0
    for r in d3698:
        for i, p in enumerate(r["e_pos"]):
            if i == 0: continue
            te += 1
            if p in luc: tl += 1
    frac98 = tl/te
    # control excl e1
    te2 = tl2 = 0
    for r in dctrl:
        for i, p in enumerate(r["e_pos"]):
            if i == 0: continue
            te2 += 1
            if p in luc: tl2 += 1
    fracc = tl2/te2
    z = (frac98 - fracc)/math.sqrt(fracc*(1-fracc)/te)
    check("AC: control has 63 e-pos", te2 >= 60, f"({te2})")
    check("AC: (36,98) vs control z<3", abs(z) < 3, f"(z={z:.2f})")
    check("AC: control fraction ~46%", abs(fracc - 0.46) < 0.08, f"({fracc*100:.1f}%)")

    npass = sum(results)
    print(f"\n=== {npass}/{len(results)} PASS ===")
    import sys; sys.exit(0 if npass == len(results) else 1)

if __name__ == "__main__":
    main()
