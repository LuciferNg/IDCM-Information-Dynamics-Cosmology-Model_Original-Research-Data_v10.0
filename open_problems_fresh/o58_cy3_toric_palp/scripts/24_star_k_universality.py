#!/usr/bin/env python3
"""
O58 script 24 — Option 1: Star-K universality across all_36_98.poly instances.
Samples 8 instances (different vertex counts), computes for each:
  - K[i,i,i] diagonal (negative list)
  - star sizes from qhull triangulation
  - test: do negative-K points have small star? star=8 ↔ negative K?
  - test: are negative K values = -8×{Lucas or N_d-related}?
CAVEAT: star size is triangulation-dependent (K is not); same qhull backend
used throughout for consistency.
"""
import os, json, numpy as np, math, sys
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

def analyze_instance(coords, idx):
    """Return dict with diag K, star sizes, negative-K points."""
    from cytools import Polytope, config
    config.enable_experimental_features()
    P = Polytope(coords)
    tri = P.triangulate(backend="qhull")
    cy = tri.get_cy()
    inter = cy.intersection_numbers()
    K = np.zeros((36, 36, 36))
    for (i, j, k), v in inter.items():
        for a, b, c in permutations((i-1, j-1, k-1)):
            K[a, b, c] = v

    pts = P.points()
    simps = tri.simplices()
    star = Counter()
    for s in simps:
        for i in s:
            if i != 0:
                star[i] += 1

    diag = [int(K[i, i, i]) for i in range(36)]
    neg = [(i, diag[i]) for i in range(36) if diag[i] < 0]
    # map diag index → point index: intersection divisor (i+1) ↔ pts[i+1]
    neg_pts = []
    for i, v in neg:
        pid = i + 1
        p = tuple(int(x) for x in pts[pid]) if pid < len(pts) else None
        st = star.get(pid)
        neg_pts.append(dict(k_idx=i, value=v, pts_idx=pid, point=p, star=st))
    # star=8 points
    s8 = [(pid, star[pid], diag[pid-1]) for pid in star if star[pid] == 8 and pid < 37]
    # star histogram
    star_hist = dict(Counter(star.values()))
    # min star points
    min_star = min(star.values()) if star else None
    min_pts = [(pid, star[pid], diag[pid-1]) for pid in star if star[pid] == min_star and pid < 37]
    return dict(idx=idx, n_vert=len(coords), n_pts=len(pts),
                neg=neg_pts, star8=s8, min_star=min_star, min_pts=min_pts,
                star_hist=star_hist, diag=diag)

def main():
    os.chdir(DATA)
    polies = parse_poly_file("all_36_98.poly")
    sample_idx = [0, 1, 2, 5, 10, 20, 50, 89]
    results = []
    for idx in sample_idx:
        print(f"=== instance {idx} ({len(polies[idx])} verts) ===", flush=True)
        try:
            r = analyze_instance(polies[idx], idx)
            results.append(r)
            print(f"  points={r['n_pts']}, star8={r['star8']}, min_star={r['min_star']} @ {r['min_pts']}")
            print(f"  negative K: {[(d['k_idx'], d['value'], d['pts_idx'], d['point'], d['star']) for d in r['neg']]}")
        except Exception as e:
            print(f"  ERROR: {str(e)[:100]}")
            results.append(dict(idx=idx, error=str(e)[:100]))
    # summary stats
    print("\n=== SUMMARY ===")
    n_star8_neg = 0
    n_star8 = 0
    n_neg = 0
    n_neg_minstar = 0
    for r in results:
        if "error" in r:
            continue
        n_neg += len(r["neg"])
        if r["star8"]:
            n_star8 += len(r["star8"])
            n_star8_neg += sum(1 for _, _, v in r["star8"] if v < 0)
        if r["min_pts"]:
            n_neg_minstar += sum(1 for _, _, v in r["min_pts"] if v < 0)
    print(f"instances with star=8: {n_star8} points, negative K: {n_star8_neg}")
    print(f"total negative-K points: {n_neg}, negative-K at min-star: {n_neg_minstar}")
    # Lucas check on negative values
    L = [2, 1]
    for n in range(2, 16):
        L.append(L[-1] + L[-2])
    lucas = {v: n for n, v in enumerate(L)}
    print("\nNegative K values and -K/8:")
    for r in results:
        if "error" in r:
            continue
        for d in r["neg"]:
            v = d["value"]
            q = -v / 8
            qs = f"{q:.2f}"
            tag = ""
            if abs(v) % 8 == 0:
                qi = -v // 8
                tag = f" = -8×{qi}"
                if qi in lucas:
                    tag += f" (L_{lucas[qi]})"
            print(f"  inst {r['idx']}: K[{d['k_idx']},{d['k_idx']},{d['k_idx']}] = {v} {tag}")
    json.dump(results, open("star_k_universality.json", "w"), indent=2, default=str)
    print("\nSaved data/star_k_universality.json")

if __name__ == "__main__":
    main()
