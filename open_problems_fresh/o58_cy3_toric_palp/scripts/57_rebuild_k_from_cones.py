#!/usr/bin/env python3
"""
O58 script 57 — S: rebuild K from cone volumes (exact algebraic test).
K[i,j,k] should be computable from triangulation data:
K[i,j,k] = Σ over maximal cones σ containing {i,j,k} of (oriented volume).
For a CY hypersurface in toric variety: κ_ijk = Σ_σ Vol(σ) where the
intersection of divisors D_i·D_j·D_k is computed via the fan.

Test: reconstruct K[i,j,k] for the canonical (36,98) from simplices and
compare with cy.intersection_numbers().
"""
import os, json, numpy as np
from itertools import combinations

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def main():
    os.chdir(DATA)
    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    tri = P.triangulate(backend="qhull")
    cy = tri.get_cy()
    K = np.load("kappa_36d_true.npy")
    inter = cy.intersection_numbers()
    pts = [tuple(int(x) for x in p) for p in P.points()]
    simps = [list(s) for s in tri.simplices()]

    print("=== S: rebuild K from cones ===\n")
    print(f"maximal cones: {len(simps)}")
    print(f"K nnz: {np.count_nonzero(K)}")

    # Each maximal cone = 5 points (4D simplex): [origin + 4 rays]
    # The CY triple intersection K[i,j,k] relates to the cone fan.
    # In the Batyrev construction, for the hypersurface:
    # K[i,j,k] = Σ_σ (det of the 4 rays in σ) / (something)
    # where σ ranges over cones containing rays i,j,k.
    # Test the simplest version: K[i,j,k] ∝ Σ_σ det(rays of σ)
    # where σ contains i,j,k (as rays).

    # first: which simplices contain which divisors?
    # a divisor D_i corresponds to a ray/pts[i]
    # cone contains divisor i if pts[i] is one of its 5 points
    def contains(s, i):
        return i in s

    # build the signed volume of each simplex (det of 4 non-origin rays)
    vols = {}
    for s in simps:
        nonz = [v for v in s if v != 0]
        if len(nonz) < 4:
            continue
        # take first 4 non-origin rays
        rays = [pts[v] for v in nonz[:4]]
        M = np.array(rays)
        vols[tuple(sorted(nonz))] = np.linalg.det(M)

    # test: K[i,j,k] vs Σ signed det over cones containing i,j,k
    print("\n=== test: K[i,j,k] vs Σ_σ det(σ) ===")
    test_triples = [(8,8,8), (0,0,0), (1,1,1), (8,8,17), (0,1,1), (7,8,8), (0,8,8)]
    for (i,j,k) in test_triples:
        kv = K[i,j,k]
        # cones containing i,j,k
        contrib = 0.0
        ncones = 0
        for s in simps:
            if i in s and j in s and k in s:
                nonz = tuple(sorted(v for v in s if v != 0))
                contrib += vols.get(nonz, 0)
                ncones += 1
        print(f"  K[{i},{j},{k}] = {kv:>6} | Σdet = {contrib:>10.2f} | cones={ncones} | ratio={kv/contrib if contrib else 'N/A'}")

    # Better: use the fan intersection formula directly.
    # For toric variety: D_i·D_j·D_k = Σ_{cones σ ⊇ {i,j,k}} (det of generators)
    # The CY hypersurface restriction divides by... let's check magnitudes.
    print("\n=== magnitude check ===")
    print("CY κ values are integers; cone dets are floats (can be fractional)")
    print("→ the reconstruction needs the CY hypersurface constraint")
    print("  (the 4th condition: Σ charges = 0).")

    # Alternative: the "redundant" divisors 2,3,6,7 are NOT in the
    # divisor basis → their K rows are determined by the basis via the
    # linear relations of the fan. The vanishing of co-simplex triples
    # may come from these relations + the CY constraint.
    print("\n=== linear relations of the fan ===")
    # each maximal cone gives a relation: Σ_{v in σ} (lattice relation)
    # The star of a point = number of cones containing it
    star = {}
    for s in simps:
        for v in s:
            star[v] = star.get(v, 0) + 1
    print("star sizes for core divisors:")
    for d in [0, 1, 3, 4, 7, 8, 17, 33]:
        print(f"  div {d}: star={star.get(d, 0)}")

if __name__ == "__main__":
    main()
