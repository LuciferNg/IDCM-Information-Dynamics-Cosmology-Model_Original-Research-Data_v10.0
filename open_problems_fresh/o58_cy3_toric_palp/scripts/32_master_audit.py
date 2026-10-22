#!/usr/bin/env python3
"""
O58 script 32 — MASTER AUDIT: re-derive every key claim from raw JSON/npy
and verify docs consistency. This is the final no-hallucination gate.
"""
import os, json, sys, numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
results = []

def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

def main():
    print("=== O58 MASTER AUDIT ===\n")

    # 1. CORRECT κ (script 31 output)
    K = np.load(os.path.join(DATA, "kappa_36d_true.npy"))
    check("κ shape 36³", K.shape == (36,36,36))
    nnz = int(np.count_nonzero(K))
    check("κ nnz = 350", nnz == 350, f"({nnz})")
    check("K[0,0,0] = -360 (divisor 0)", int(K[0,0,0]) == -360, f"({int(K[0,0,0])})")
    check("K[8,8,8] = -232 (divisor 8 = (1,1,0,0))", int(K[8,8,8]) == -232, f"({int(K[8,8,8])})")
    check("K[1,1,1] = 4 (divisor 1)", int(K[1,1,1]) == 4, f"({int(K[1,1,1])})")
    neg = [(d, int(K[d,d,d])) for d in range(36) if K[d,d,d] < 0]
    check("negative diag = [(0,-360),(8,-232),(12,-5),(17,-5)]", neg == [(0,-360),(8,-232),(12,-5),(17,-5)], f"({neg})")

    # 2. (1,1,0,0) universality (script 27)
    p = json.load(open(os.path.join(DATA, "point_1100_universality.json")))
    present = [r for r in p if r["has"]]
    check("4 instances have (1,1,0,0)", len(present) == 4)
    check("all K = -232", all(r["K"] == -232 for r in present))
    check("-232 = -8×L₇", all(r["K"] == -8*29 for r in present))

    # 3. HF swap + island
    iso = json.load(open(os.path.join(DATA, "island_stats_swap_corrected.json")))
    check("total (36,98) = 5021", iso["total_98"] == 5021, f"({iso['total_98']})")
    check("family = 12,262,287", iso["total_fam"] == 12262287)
    check("20+ vert has 0 (36,98)", all(r["real3698"] == 0 for r in iso["per_file"] if int(r["file"].split("-")[2]) >= 20))

    # 4. divisor 0 NOT universal
    d0 = json.load(open(os.path.join(DATA, "divisor0_universality.json")))
    check("K[0,0,0] not universal", len(set(r["k000"] for r in d0)) > 1)
    check("canonical K[0,0,0] = -360", d0[0]["k000"] == -360)

    # 5. mirror point (-1,-1,0,0) = +8 (not -360)
    mp = json.load(open(os.path.join(DATA, "mirror_points_universality.json")))
    check("inst0 (-1,-1,0,0) K = +8", mp[0]["Km1100"] == 8, f"({mp[0]['Km1100']})")

    # 6. option2: 45 = 29 + 16 (B²)
    check("45 - 29 = 16 = B²", 45 - 29 == 16)
    check("-360 = -8×45", -360 == -8*45)
    check("-232 = -8×29", -232 == -8*29)

    # 7. docs all present
    docs = ["01_palp_identification.md", "02_true_dijk_vs_dtensor.md",
            "03_k000_hf_audit.md", "04_hf_metadata_swap.md",
            "05_summary_2explorations.md", "06_island_correction.md",
            "07_star_k_closure.md", "08_point_1100_closure.md",
            "09_index_fix_and_closure.md", "10_option2_l7_b2.md",
            "11_final_correction.md"]
    for d in docs:
        check(f"docs/{d} exists", os.path.exists(os.path.join("docs", d)))

    # 8. no UNQUALIFIED stale claims in docs (allow ❌/撤回 context)
    import re
    stale_patterns = ["K\\[35,35,35\\] = -360", "K\\[0,0,35\\] = -44",
                      "1359 nnz", "K\\[0,0,0\\]=4\\.0", "1122 nnz",
                      "97.8%"]
    for pat in stale_patterns:
        hits = []
        for d in docs:
            content = open(os.path.join("docs", d)).read()
            for m in re.finditer(pat, content):
                # context: 40 chars before/after
                ctx = content[max(0, m.start()-60):m.end()+40]
                # skip if the line is a retraction (❌/撤回/實為/唔係/舊)
                if any(w in ctx for w in ["❌", "撤回", "實為", "唔係", "舊", "artifact", "錯"]):
                    continue
                hits.append(d)
        check(f"no unqualified stale '{pat[:25]}'", not hits, f"({hits})")

    npass = sum(results)
    print(f"\n=== {npass}/{len(results)} PASS ===")
    sys.exit(0 if npass == len(results) else 1)

if __name__ == "__main__":
    main()
