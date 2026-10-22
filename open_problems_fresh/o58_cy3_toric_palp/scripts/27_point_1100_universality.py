#!/usr/bin/env python3
"""
O58 script 27 — THE REAL UNIVERSALITY: lattice point (1,1,0,0) ↔ K=-232.
Hypothesis: in EVERY (36,98) instance that CONTAINS point (1,1,0,0),
that point has self-intersection K = -232 = -8×L₇ (L₇=29).
Star size is triangulation-dependent (NOT universal); the point is.
Test on all 9 sampled instances + full check on which have (1,1,0,0).
"""
import os, json, numpy as np
from itertools import permutations
from collections import Counter

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def parse_poly_file(path):
    lines = open(path).read().splitlines()
    polies = []
    i = 0
    while i < len(lines):
        parts = lines[i].split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            n, d = int(parts[0]), int(parts[1])
            coords = []
            ok = True
            j = i + 1
            for _ in range(n):
                if j >= len(lines):
                    ok = False
                    break
                cp = lines[j].split()
                if len(cp) != d:
                    ok = False
                    break
                try:
                    coords.append([int(x) for x in cp])
                except ValueError:
                    ok = False
                    break
                j += 1
            if ok:
                polies.append(coords)
                i = j
                continue
        i += 1
    return polies

def find_point_K(coords):
    """Find (1,1,0,0) in points; return its K[i,i,i] if present."""
    from cytools import Polytope, config
    config.enable_experimental_features()
    P = Polytope(coords)
    pts = P.points()
    target = (1, 1, 0, 0)
    pid = None
    for i, p in enumerate(pts):
        if tuple(int(x) for x in p) == target:
            pid = i
            break
    if pid is None:
        return None, None, len(pts), None
    tri = P.triangulate(backend="qhull")
    cy = tri.get_cy()
    inter = cy.intersection_numbers()
    # K index = pid - 1 (intersection divisor pid ↔ K[pid-1])
    k = pid - 1
    K = 0
    for (i, j, kk), v in inter.items():
        if i == pid and j == pid and kk == pid:
            K = int(v)
            break
    # star of pid
    simps = tri.simplices()
    star = sum(1 for s in simps if pid in s)
    return pid, K, len(pts), star

def main():
    os.chdir(DATA)
    polies = parse_poly_file("all_36_98.poly")
    sample = [0, 1, 2, 3, 5, 10, 20, 50, 89]
    print("=== (1,1,0,0) ↔ K=-232 test ===")
    n_have = 0
    n_neg232 = 0
    results = []
    for idx in sample:
        pid, K, npts, star = find_point_K(polies[idx])
        if pid is None:
            print(f"inst {idx}: NO (1,1,0,0) point")
            results.append(dict(idx=idx, has=False))
        else:
            n_have += 1
            ok = (K == -232)
            if ok:
                n_neg232 += 1
            print(f"inst {idx}: HAS (1,1,0,0) @ pts[{pid}] → K={K} "
                  f"{'✅ = -232 = -8×L₇' if ok else '❌'} (star={star})")
            results.append(dict(idx=idx, has=True, pid=pid, K=K, star=star))
    print(f"\n{ n_have} instances have (1,1,0,0); {n_neg232}/{n_have} give K=-232")
    json.dump(results, open("point_1100_universality.json", "w"), indent=2)

if __name__ == "__main__":
    main()
