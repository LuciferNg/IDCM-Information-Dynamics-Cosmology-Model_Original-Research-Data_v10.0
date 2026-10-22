#!/usr/bin/env python3
"""
O58 script 34 — A: (1,1,0,0) mechanism deep-dive.
Q: WHY does (1,1,0,0) always give K=-232 in every (36,98) instance?
Compare: which OTHER norm²=2 / sum=2 points exist? What are their K?
Check star cone structure + divisor volume.
"""
import os, json, numpy as np
from itertools import permutations

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def analyze(coords, label):
    from cytools import Polytope, config
    config.enable_experimental_features()
    P = Polytope(coords)
    tri = P.triangulate(backend="qhull")
    cy = tri.get_cy()
    inter = cy.intersection_numbers()
    pts = [tuple(int(x) for x in p) for p in P.points()]
    print(f"\n=== {label} ===")
    print(f"  points: {len(pts)}, h11={P.h11()}, h21={P.h21()}")
    # find norm²=2 and sum=2 points
    for tgt_norm, tgt_sum, tname in [(2, 2, "norm²=2 & sum=2"), (2, None, "norm²=2"), (None, 2, "sum=2")]:
        hits = [p for p in pts if (tgt_norm is None or sum(x*x for x in p) == tgt_norm)
                and (tgt_sum is None or sum(p) == tgt_sum)]
        if hits:
            print(f"  {tname}: {len(hits)} points")
            for h in hits[:12]:
                # find K at this point's divisor index
                didx = pts.index(h)
                K = inter.get((didx, didx, didx))
                print(f"    pts[{didx}] = {h} → K={K}")
    # the (1,1,0,0) point itself
    if (1,1,0,0) in pts:
        didx = pts.index((1,1,0,0))
        K = inter.get((didx, didx, didx))
        # row structure
        row = sorted([(j, k, v) for (i, j, k), v in inter.items() if i == didx and v != 0])
        print(f"  (1,1,0,0) at pts[{didx}], K={K}")
        print(f"  row {didx} nnz: {len(row)}, sum: {sum(v for _,_,v in row)}")
        big = [(j,k,v) for j,k,v in row if abs(v) >= 8]
        print(f"  row {didx} |v|≥8: {big[:15]}")
    else:
        print(f"  (1,1,0,0) NOT PRESENT")
    return P, tri, cy, pts, inter

def main():
    os.chdir(DATA)
    from cytools import Polytope, config
    config.enable_experimental_features()
    # parse all_36_98.poly
    lines = open("all_36_98.poly").read().splitlines()
    polies = []
    i = 0
    while i < len(lines):
        parts = lines[i].split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            n, d = int(parts[0]), int(parts[1])
            coords = [[int(x) for x in lines[i+1+j].split()] for j in range(n)]
            polies.append(coords)
            i += n + 1
        else:
            i += 1
    print(f"parsed {len(polies)} polytopes")
    # analyze instances 0, 1, 3, 50 (have 1100) and 2, 5 (don't)
    results = {}
    for idx in [0, 1, 3, 50, 2, 5]:
        try:
            P, tri, cy, pts, inter = analyze(polies[idx], f"inst {idx}")
            d = dict(
                idx=idx,
                npts=len(pts),
                has_1100=(1,1,0,0) in pts,
                norm2_sum2=[p for p in pts if sum(x*x for x in p)==2 and sum(p)==2],
                K1100=None
            )
            if (1,1,0,0) in pts:
                didx = pts.index((1,1,0,0))
                d["K1100"] = int(inter.get((didx, didx, didx)))
                d["pid1100"] = didx
            results[idx] = d
        except Exception as e:
            print(f"inst {idx} ERROR: {str(e)[:80]}")
    json.dump(results, open("mechanism_1100.json", "w"), indent=2, default=str)
    print("\nSaved data/mechanism_1100.json")

if __name__ == "__main__":
    main()
