#!/usr/bin/env python3
"""
O58 script 53 — P: K=0 geometric vanishing — cone volume cancellation.
Q: which co-simplex triples vanish and why?
Hypothesis: K[i,j,k] = Σ over cones containing {i,j,k} of (volume of cone
restricted) with signs — vanishing = cancellation between cones.
Test: for each co-simplex triple, count cones containing it; compare
zero vs nonzero distribution.
"""
import os, json, numpy as np
from collections import Counter

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def main():
    os.chdir(DATA)
    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    tri = P.triangulate(backend="qhull")
    simps = [set(s) for s in tri.simplices()]
    K = np.load("kappa_36d_true.npy")

    cosimp = set()
    for cs in simps:
        lst = sorted(v for v in cs if v < 36)
        for i in range(len(lst)):
            for j in range(i, len(lst)):
                for k in range(j, len(lst)):
                    cosimp.add((lst[i], lst[j], lst[k]))

    zero = [(i,j,k) for (i,j,k) in cosimp if K[i,j,k] == 0]
    nz = [(i,j,k) for (i,j,k) in cosimp if K[i,j,k] != 0]

    # count cones containing each triple
    def n_cones(t):
        i, j, k = t
        return sum(1 for cs in simps if i in cs and j in cs and k in cs)

    z_cone = Counter(n_cones(t) for t in zero)
    n_cone = Counter(n_cones(t) for t in nz)
    print("=== P: cones containing triple ===")
    print(f"zero triples   cone-count dist: {dict(sorted(z_cone.items()))}")
    print(f"nonzero triples cone-count dist: {dict(sorted(n_cone.items()))}")
    print()

    # hypothesis: triples in MANY cones are more likely nonzero?
    # (more volume contributions)
    total_z = len(zero); total_n = len(nz)
    print("fraction nonzero by cone count:")
    all_cone_counts = set(list(z_cone) + list(n_cone))
    for c in sorted(all_cone_counts):
        zc = z_cone.get(c, 0); nc = n_cone.get(c, 0)
        frac = nc / (zc + nc) if (zc + nc) else 0
        print(f"  {c} cones: zero={zc}, nz={nc}, nonzero-frac={frac:.2f}")
    print()

    # div 0 in all cones → triples with 0 have max cone count
    # but div0 tends to VANISH → not about count
    print("=== div0 role ===")
    z0 = sum(1 for t in zero if 0 in t)
    n0 = sum(1 for t in nz if 0 in t)
    print(f"zero w/ div0: {z0}/{total_z} ({z0/total_z*100:.1f}%)")
    print(f"nz   w/ div0: {n0}/{total_n} ({n0/total_n*100:.1f}%)")
    print()

    # div 8 role (the (1,1,0,0) divisor)
    z8 = sum(1 for t in zero if 8 in t)
    n8 = sum(1 for t in nz if 8 in t)
    print(f"zero w/ div8: {z8}/{total_z} ({z8/total_z*100:.1f}%)")
    print(f"nz   w/ div8: {n8}/{total_n} ({n8/total_n*100:.1f}%)")
    print()

    # cone count for div8 triples only
    t8z = [t for t in zero if 8 in t]
    t8n = [t for t in nz if 8 in t]
    print(f"div8 triples: zero={len(t8z)}, nz={len(t8n)}")
    print()

    # K values by cone count (for nonzero)
    print("=== K value vs cone count (nonzero triples) ===")
    vals = {}
    for t in nz:
        c = n_cones(t)
        vals.setdefault(c, []).append(K[t])
    for c in sorted(vals):
        arr = vals[c]
        print(f"  {c} cones: n={len(arr)}, mean K={np.mean(arr):.2f}, min={min(arr)}, max={max(arr)}")
    print()

    # NEW hypothesis: K[i,j,k] = (# of "good" cones) - (# of "bad" cones)?
    # With div0 in ALL 144 cones, K[0,j,k] sums over 144 cones...
    # but K[0,0,0] = -360 — negative! So sign matters.
    # Test: cone volume signs — triangulation orientation
    print("=== orientation hypothesis ===")
    print("K = Σ_σ (oriented volume contribution of cone σ containing i,j,k)")
    print("If all contributions same sign → |K| grows with cone count")
    print("div8 star=8 (few cones) but K[8,8,8]=-232 (large negative)")
    print("div0 star=144 (all cones) but K[0,0,0]=-360 (large negative)")
    print("→ NOT simple count; large |K| needs large cone volumes")

if __name__ == "__main__":
    main()
