#!/usr/bin/env python3
"""
O58 script 23 — FINAL VERIFIER (star-K closure + all O58 claims).
"""
import json, os, sys

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
results = []

def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

def main():
    print("=== O58 STAR-K FINAL VERIFIER ===\n")

    sk = json.load(open(os.path.join(DATA, "star_k_relation.json")))
    star8 = sk["star8"]
    check("star=8 has exactly 2 points", len(star8) == 2, f"({len(star8)})")
    check("pts[8] K = -232", star8[0]["K"] == -232 and star8[0]["idx"] == 8)
    check("pts[36] K = -360", star8[1]["K"] == -360 and star8[1]["idx"] == 36)
    check("Z₂ mirror pts[36] = -pts[8]",
          star8[1]["pt"] == [-x for x in star8[0]["pt"]])
    check("-232 = -8×L₇", star8[0]["K"] == -8*29)
    check("-360 = -8×45", star8[1]["K"] == -8*45)

    # island stats
    iso = json.load(open(os.path.join(DATA, "island_stats_swap_corrected.json")))
    check("total real (36,98) = 5021", iso["total_98"] == 5021, f"({iso['total_98']})")
    check("total family = 12,262,287", iso["total_fam"] == 12262287, f"({iso['total_fam']})")

    # lucas structure
    lk = json.load(open(os.path.join(DATA, "lucas_kappa_structure.json")))
    entries = {tuple(e[:2]): e[2] for e in lk["entries"]}
    check("K[7,7,7] = -232", entries.get((7,7)) == -232)
    check("K[0,0,35] = -44", entries.get((0,35)) == -44)

    # docs exist
    for doc in ["docs/07_star_k_closure.md", "docs/06_island_correction.md"]:
        check(f"{doc} exists", os.path.exists(doc))

    npass = sum(results)
    print(f"\n=== {npass}/{len(results)} PASS ===")
    sys.exit(0 if npass == len(results) else 1)

if __name__ == "__main__":
    main()
