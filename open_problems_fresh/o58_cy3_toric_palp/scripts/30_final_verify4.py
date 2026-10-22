#!/usr/bin/env python3
"""
O58 script 30 — FINAL VERIFIER (all O58 claims, corrected).
"""
import json, os, sys

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
results = []

def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

def main():
    print("=== O58 FINAL VERIFIER (corrected) ===\n")

    # 1. (1,1,0,0) ↔ -232 universality (script 27, coordinate search)
    p = json.load(open(os.path.join(DATA, "point_1100_universality.json")))
    present = [r for r in p if r["has"]]
    check("4 instances have (1,1,0,0)", len(present) == 4, f"({len(present)})")
    check("all give K=-232", all(r["K"] == -232 for r in present),
          f"({[r['K'] for r in present]})")
    check("-232 = -8×L₇", all(r["K"] == -8*29 for r in present))

    # 2. HF swap + island (independent of index issues)
    iso = json.load(open(os.path.join(DATA, "island_stats_swap_corrected.json")))
    check("total real (36,98) = 5021", iso["total_98"] == 5021, f"({iso['total_98']})")
    check("total family = 12,262,287", iso["total_fam"] == 12262287)

    # 3. canonical K[0,0,0] = -360 (divisor 0) — exists but NOT universal
    # verify from script 29 output JSON
    d0 = json.load(open(os.path.join(DATA, "divisor0_universality.json")))
    check("canonical (inst 0) K[0,0,0] = -360", d0[0]["k000"] == -360)
    check("K[0,0,0] NOT universal", len(set(r["k000"] for r in d0)) > 1)

    # 4. docs exist
    for doc in ["docs/09_index_fix_and_closure.md", "docs/10_option2_l7_b2.md",
                "docs/11_final_correction.md"]:
        check(f"{doc} exists", os.path.exists(doc))

    npass = sum(results)
    print(f"\n=== {npass}/{len(results)} PASS ===")
    sys.exit(0 if npass == len(results) else 1)

if __name__ == "__main__":
    main()
