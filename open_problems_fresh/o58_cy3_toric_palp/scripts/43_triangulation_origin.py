#!/usr/bin/env python3
"""
O58 script 43 — H: block partial order origin in triangulation.
Q: why does K[i,j,k]≠0 require sorted blocks non-decreasing?
Hypothesis: divisor ordering by block = some partial order on rays
(vertices → interior), and triple intersections only for 'compatible'
triples. Check:
  1. Triangulation maximal cones (which rays appear together)
  2. Does cone membership define the partial order?
"""
import os, json, numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def main():
    os.chdir(DATA)
    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    tri = P.triangulate(backend="qhull")
    pts = [tuple(int(x) for x in p) for p in P.points()]
    K = np.load("kappa_36d_true.npy")

    # triangulation maximal cones (CYTools API)
    print("=== triangulation structure ===")
    try:
        cones = tri.maximal_cones()
        print(f"maximal cones: {len(cones)}")
        # sample cones
        for c in list(cones)[:5]:
            print(f"  cone: {c}")
    except Exception as e:
        print(f"maximal_cones() error: {e}")

    # check star of each core divisor
    print("\n=== star (cones containing divisor) ===")
    try:
        for d in [0, 1, 3, 4, 8, 17, 33]:
            star = [c for c in cones if d in c]
            print(f"div {d}: star size = {len(star)}")
    except Exception as e:
        print(f"star calc error: {e}")

    # KEY TEST: does K[i,j,k]≠0 imply i,j,k co-star (share a cone)?
    # divs i,j,k with K≠0 → are they in a common maximal cone?
    print("\n=== K≠0 vs common cone ===")
    try:
        cone_sets = [set(c) for c in cones]
        nnz_triples = []
        for i in range(36):
            for j in range(36):
                for k in range(36):
                    if K[i,j,k] != 0:
                        nnz_triples.append((i,j,k))
        common = 0
        for (i,j,k) in nnz_triples:
            if any(i in cs and j in cs and k in cs for cs in cone_sets):
                common += 1
        print(f"K≠0 triples with common cone: {common}/{len(nnz_triples)}")
    except Exception as e:
        print(f"common cone calc error: {e}")

if __name__ == "__main__":
    main()
