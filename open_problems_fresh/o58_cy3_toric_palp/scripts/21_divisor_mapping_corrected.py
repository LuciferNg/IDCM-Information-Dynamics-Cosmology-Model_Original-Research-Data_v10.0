#!/usr/bin/env python3
"""
O58 script 21 — CORRECT divisor identification + star-size analysis.
Fixes off-by-one: K[i,i,i] (0-based) ↔ intersection (i+1,i+1,i+1) (1-based)
↔ pts[i+1]. Identifies pts[8] (K[7,7,7]=-232) and pts[36] (K[35,35,35]=-360).
Computes star sizes (maximal cones containing each ray) from triangulation,
tests K[i,i,i] = -8 × star(ray) hypothesis.
"""
import os, json, numpy as np, math
from itertools import permutations

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def main():
    os.chdir(DATA)
    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    tri = P.triangulate(backend="qhull")
    cy = tri.get_cy()
    inter = cy.intersection_numbers()
    K = np.zeros((36, 36, 36))
    for (i, j, k), v in inter.items():
        for a, b, c in permutations((i-1, j-1, k-1)):
            K[a, b, c] = v

    pts = P.points()
    verts = [tuple(v) for v in P.vertices()]
    print(f"total points: {len(pts)}, vertices: {len(verts)}")
    print("\n=== point inventory (idx: coords, status) ===")
    status = {}
    for idx in range(len(pts)):
        p = tuple(int(x) for x in pts[idx])
        if p == (0,0,0,0):
            st = "origin"
        elif p in verts:
            st = "VERTEX"
        else:
            st = "interior/bdry"
        status[idx] = st
        if idx <= 8 or idx >= 33:
            print(f"  pts[{idx:2d}] = {p}  {st}")

    # intersection index (1-based) → pts index: divisor d (1-based) ↔ pts[d]
    print("\n=== K diagonal → point mapping ===")
    for k_idx in [0, 7, 11, 16, 35]:
        div_1based = k_idx + 1
        if div_1based < len(pts):
            print(f"  K[{k_idx},{k_idx},{k_idx}] = {int(K[k_idx,k_idx,k_idx]):6d}  ↔ "
                  f"intersection ({div_1based},{div_1based},{div_1based}) ↔ pts[{div_1based}] = "
                  f"{tuple(int(x) for x in pts[div_1based])} [{status[div_1based]}]")

    # star sizes: count maximal cones (simplices) containing each point (ray)
    simps = tri.simplices()
    print(f"\ntriangulation: {len(simps)} maximal cones")
    from collections import Counter
    star = Counter()
    for s in simps:
        for i in s:
            if i != 0:  # exclude origin
                star[i] += 1
    print("\n=== star sizes (maximal cones per point) ===")
    for idx in [1, 8, 12, 17, 36]:
        if idx in star:
            print(f"  pts[{idx}] star = {star[idx]}")

    # test: K[i,i,i] vs star
    print("\n=== K[i,i,i] vs star size ===")
    for idx in sorted(star):
        if idx >= 37:
            continue
        k_idx = idx - 1  # intersection divisor idx (1-based) = K index idx-1
        if k_idx < 36:
            kiii = int(K[k_idx, k_idx, k_idx])
            if kiii != 0:
                print(f"  pts[{idx:2d}] star={star[idx]:2d}  K={kiii:6d}  ratio={kiii/star[idx]:8.3f}")

    # negative K[i,i,i] divisors: what points are they?
    print("\n=== negative diagonal divisors → points ===")
    for k_idx in range(36):
        v = int(K[k_idx, k_idx, k_idx])
        if v < 0:
            div = k_idx + 1
            p = tuple(int(x) for x in pts[div]) if div < len(pts) else None
            print(f"  K[{k_idx},{k_idx},{k_idx}] = {v} ↔ pts[{div}] = {p} [{status.get(div,'?')}] star={star.get(div,'?')}")

    json.dump(dict(
        pts8=list(int(x) for x in pts[8]), pts36=list(int(x) for x in pts[36]),
        status8=status.get(8), status36=status.get(36),
        star8=star.get(8), star36=star.get(36),
        star_all=dict(star)), open("divisor_mapping_corrected.json", "w"))

if __name__ == "__main__":
    main()
