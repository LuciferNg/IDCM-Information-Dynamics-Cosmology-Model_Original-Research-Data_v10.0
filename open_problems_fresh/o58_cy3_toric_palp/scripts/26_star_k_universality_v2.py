#!/usr/bin/env python3
"""
O58 script 26 — Option 1 FIX: Star-K universality with correct index handling.
Some instances' intersection_numbers() have keys beyond 36 (1-based divisors
may go up to n_rays>36 in non-canonical forms). Build K sized to the MAX key,
then only analyze the h11=36 diagonal block.
Also: use divisor_basis to map correctly.
"""
import os, json, numpy as np, math
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

def analyze(coords, idx):
    from cytools import Polytope, config
    config.enable_experimental_features()
    P = Polytope(coords)
    tri = P.triangulate(backend="qhull")
    cy = tri.get_cy()
    inter = cy.intersection_numbers()
    # max key determines K size
    maxk = max(max(k) for k in inter)
    nD = max(maxk, 36)
    K = np.zeros((nD, nD, nD))
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
    diag = [int(K[i, i, i]) for i in range(min(36, nD))]
    neg = [(i, diag[i]) for i in range(len(diag)) if diag[i] < 0]
    neg_info = []
    for i, v in neg:
        pid = i + 1
        p = tuple(int(x) for x in pts[pid]) if pid < len(pts) else None
        neg_info.append(dict(k=i, v=v, pid=pid, pt=p, star=star.get(pid)))
    s8 = []
    for pid in star:
        if star[pid] == 8 and pid < 37 and pid-1 < nD:
            s8.append(dict(pid=pid, star=8, K=int(K[pid-1, pid-1, pid-1]),
                           pt=tuple(int(x) for x in pts[pid])))
    return dict(idx=idx, n_vert=len(coords), n_pts=len(pts), nD=nD,
                neg=neg_info, star8=s8, star_hist=dict(Counter(star.values())))

def main():
    os.chdir(DATA)
    polies = parse_poly_file("all_36_98.poly")
    sample = [0, 1, 2, 3, 5, 10, 20, 50, 89]
    results = []
    for idx in sample:
        try:
            r = analyze(polies[idx], idx)
            results.append(r)
            print(f"inst {idx} ({r['n_vert']}v, {r['n_pts']}pts, nD={r['nD']}): "
                  f"star8={[(s['pid'], s['K']) for s in r['star8']]}, "
                  f"neg={[(n['k'], n['v'], n['star']) for n in r['neg']]}", flush=True)
        except Exception as e:
            print(f"inst {idx}: ERROR {str(e)[:80]}", flush=True)
            results.append(dict(idx=idx, error=str(e)[:80]))
    json.dump(results, open("star_k_universality_v2.json", "w"), indent=2, default=str)

if __name__ == "__main__":
    main()
