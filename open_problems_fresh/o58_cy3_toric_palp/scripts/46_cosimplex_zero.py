#!/usr/bin/env python3
"""
O58 script 46 — K: why do 554 co-simplex triples have K=0?
The 350 nonzero triples are all co-simplex (necessary). But 554 co-simplex
triples vanish. Q: what distinguishes them?
Hypotheses:
  1. Index range (some divisors beyond h11=36 basis)
  2. Divisor type (vertex vs interior)
  3. Kähler cone / nef condition
  4. Ordering (sorted blocks non-decreasing + something)
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
    simps = [set(s) for s in tri.simplices()]
    K = np.load("kappa_36d_true.npy")
    pts = [tuple(int(x) for x in p) for p in P.points()]
    verts = [tuple(int(x) for x in v) for v in P.vertices()]

    # all co-simplex triples (restrict to divisor basis 0..35)
    cosimp = set()
    for cs in simps:
        lst = sorted(v for v in cs if v < 36)
        for i in range(len(lst)):
            for j in range(i, len(lst)):
                for k in range(j, len(lst)):
                    cosimp.add((lst[i], lst[j], lst[k]))
    print(f"co-simplex triples: {len(cosimp)}")

    # which are zero?
    zero_triples = []
    nz_triples = []
    for (i,j,k) in cosimp:
        if K[i,j,k] == 0:
            zero_triples.append((i,j,k))
        else:
            nz_triples.append((i,j,k))
    print(f"co-simplex with K=0: {len(zero_triples)}")
    print(f"co-simplex with K≠0: {len(nz_triples)}")
    print()

    # Hypothesis 1: vertex/interior composition
    def vt(d):
        return "V" if pts[d] in verts else "I"
    from collections import Counter
    comp_zero = Counter()
    comp_nz = Counter()
    for (i,j,k) in zero_triples:
        comp_zero[tuple(sorted([vt(i),vt(j),vt(k)]))] += 1
    for (i,j,k) in nz_triples:
        comp_nz[tuple(sorted([vt(i),vt(j),vt(k)]))] += 1
    print("composition of ZERO triples:", dict(comp_zero))
    print("composition of NONZERO triples:", dict(comp_nz))
    print()

    # Hypothesis 2: does triple contain div 0?
    z0 = sum(1 for t in zero_triples if 0 in t)
    n0 = sum(1 for t in nz_triples if 0 in t)
    print(f"zero triples containing div0: {z0}/{len(zero_triples)} ({z0/len(zero_triples)*100:.1f}%)")
    print(f"nz triples containing div0: {n0}/{len(nz_triples)} ({n0/len(nz_triples)*100:.1f}%)")
    print()

    # Hypothesis 3: star size product
    star = {}
    for s in simps:
        for v in s:
            star[v] = star.get(v, 0) + 1
    z_star = [star.get(t[0],0)*star.get(t[1],0)*star.get(t[2],0) for t in zero_triples]
    n_star = [star.get(t[0],0)*star.get(t[1],0)*star.get(t[2],0) for t in nz_triples]
    print(f"zero triples: mean star-product = {np.mean(z_star):.1f}")
    print(f"nz triples: mean star-product = {np.mean(n_star):.1f}")
    print()

    # Hypothesis 4: block partial order VIOLATION?
    # all co-simplex should already satisfy? check
    viol_z = 0
    for (i,j,k) in zero_triples:
        b = sorted([i//12, j//12, k//12])
        if not (b[0] <= b[1] <= b[2]):
            viol_z += 1
    print(f"zero triples violating block order: {viol_z}")

    # so block order holds for ALL co-simplex? that means block order
    # is a property of the triangulation, not of K
    viol_all = 0
    for (i,j,k) in cosimp:
        b = sorted([i//12, j//12, k//12])
        if not (b[0] <= b[1] <= b[2]):
            viol_all += 1
    print(f"ALL co-simplex violating block order: {viol_all}")

if __name__ == "__main__":
    main()
