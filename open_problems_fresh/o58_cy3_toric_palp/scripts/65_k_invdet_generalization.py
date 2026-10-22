#!/usr/bin/env python3
"""
O58 script 65 — Y: generalize K[i,j,k] = -L₇×Σ1/|det| to all triples.
Q: does K[i,j,k] = c_ijk × Σ_{σ∋i,j,k} 1/|det(σ)| with c_ijk a simple
coefficient? For (8,8,8): c = -L₇ = -29 exactly.
Test ALL 350 nonzero triples: compute Σ1/|det| and check ratio K/Σinv.
"""
import os, numpy as np
from collections import Counter

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def main():
    os.chdir(DATA)
    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    tri = P.triangulate(backend="qhull")
    K = np.load("kappa_36d_true.npy")
    pts = [tuple(int(x) for x in p) for p in P.points()]
    simps = [list(s) for s in tri.simplices()]

    # precompute det for each maximal cone (sorted non-origin rays)
    dets = {}
    for s in simps:
        nonz = [v for v in s if v != 0]
        if len(nonz) >= 4:
            M = np.array([pts[v] for v in nonz[:4]])
            dets[tuple(sorted(nonz))] = np.linalg.det(M)

    # compute Σ 1/|det| over cones containing each triple
    inv_sum = {}
    for i in range(36):
        for j in range(i, 36):
            for k in range(j, 36):
                if K[i,j,k] == 0:
                    continue
                s_inv = 0.0
                ncon = 0
                for s in simps:
                    if i in s and j in s and k in s:
                        nonz = tuple(sorted(v for v in s if v != 0))
                        d = dets.get(nonz, 0)
                        if d != 0:
                            s_inv += 1/abs(d)
                            ncon += 1
                inv_sum[(i,j,k)] = (s_inv, ncon)

    print(f"=== Y: K vs Σ1/|det| for all {len(inv_sum)} nonzero triples ===\n")

    # ratio distribution
    ratios = []
    clean = []
    for (i,j,k), (s_inv, ncon) in inv_sum.items():
        if s_inv > 0:
            r = K[i,j,k] / s_inv
            ratios.append(r)
            # integer ratio?
            if abs(r - round(r)) < 1e-9:
                clean.append(((i,j,k), round(r), s_inv, ncon))
    print(f"triples with Σinv>0: {len(ratios)}/{len(inv_sum)}")
    print(f"triples with INTEGER ratio: {len(clean)}/{len(inv_sum)}")
    print()

    # distribution of integer ratios
    rc = Counter(r for _, r, _, _ in clean)
    print("integer ratio distribution:")
    for r in sorted(rc, key=lambda x: -rc[x])[:20]:
        print(f"  ratio {r:>5}: {rc[r]} triples")
    print()

    # how many have ratio = -29 (like (8,8,8))?
    n_29 = sum(1 for _, r, _, _ in clean if r == -29)
    print(f"triples with ratio = -29 (L₇): {n_29}")
    if n_29:
        print("  examples:", [(i,j,k) for (i,j,k),r,_,_ in clean if r == -29][:10])
    print()

    # ratio = 8 (Σinv = cone count for det=1)?
    n_8 = sum(1 for _, r, _, _ in clean if r == 8)
    print(f"triples with ratio = 8: {n_8}")
    print()

    # K = 1 cases: what's Σinv?
    print("=== K=1 triples (smallest values) ===")
    k1 = [(t, s_inv, ncon) for t, (s_inv, ncon) in inv_sum.items() if K[t] == 1]
    print(f"K=1 triples: {len(k1)}")
    for t, s_inv, ncon in k1[:10]:
        print(f"  {t}: Σinv={s_inv:.4f}, cones={ncon}")
    print()

    # overall: is ratio ~ constant across triples with same cone count?
    print("=== ratio by cone count ===")
    by_cones = {}
    for (i,j,k), (s_inv, ncon) in inv_sum.items():
        if s_inv > 0:
            by_cones.setdefault(ncon, []).append(K[i,j,k]/s_inv)
    for c in sorted(by_cones):
        arr = by_cones[c]
        print(f"  {c} cones: n={len(arr)}, mean ratio={np.mean(arr):.2f}, std={np.std(arr):.2f}")

if __name__ == "__main__":
    main()
