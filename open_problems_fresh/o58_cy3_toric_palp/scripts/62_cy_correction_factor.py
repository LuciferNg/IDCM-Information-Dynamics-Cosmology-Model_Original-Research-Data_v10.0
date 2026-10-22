#!/usr/bin/env python3
"""
O58 script 62 — V: cone determinant CY correction factor formula.
K[i,j,k] = Σ_σ det(σ)·f(CY) where f involves the CY constraint.
Try: f = (number of CY points on cone) / (something)?
Better: use the actual CY equation — the hypersurface intersects
the cone. K[i,j,k] = Σ_σ Vol(σ ∩ CY).
Test via the Batyrev formula: κ_ijk = Σ_{σ ∋ i,j,k} |det(v_σ)|·c_σ
where c_σ is the CY restriction coefficient.
"""
import os, numpy as np

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
    pts = [tuple(int(x) for x in p) for p in P.points()]
    simps = [list(s) for s in tri.simplices()]
    inter = cy.intersection_numbers()

    print("=== V: CY correction factor for cone determinants ===\n")
    print(f"maximal cones: {len(simps)}")

    # For each maximal cone (5 pts: origin + 4 rays), the 4 rays form
    # a basis. The CY hypersurface equation has a Newton polytope Δ = P.
    # The coefficient of the CY equation for the cone σ is given by the
    # unique primitive relation among the 5 points.
    # In Batyrev: the CY is {Σ a_v x^v = 0} with v over Δ.
    # The intersection D_i·D_j·D_k·[CY] = Σ_σ (contribution of σ).
    # For a hypersurface, [CY] = Σ_v (coefficient) D_v via the linear
    # equivalence: Σ_v q^U_v D_v = 0 for each U(1).

    # Test the simple version: K[i,j,k] = Σ_σ det(σ)/det(total)
    # where total = Σ over all cones of |det|. Let's just record ratios.
    dets = {}
    for s in simps:
        nonz = [v for v in s if v != 0]
        if len(nonz) >= 4:
            M = np.array([pts[v] for v in nonz[:4]])
            dets[tuple(sorted(nonz))] = np.linalg.det(M)

    total_abs = sum(abs(v) for v in dets.values())
    print(f"Σ|det| over all cones = {total_abs:.3f}")

    # try: K[i,j,k] = Σ_σ det(σ) × (|det(σ)|/total_abs) × N?
    # Better idea: the correction might be 1/|det(σ)| per cone — the
    # CY intersection picks up inverse-volume weights.
    print("\n=== test: K vs Σ_σ sign(det) ===")
    test = [(8,8,8), (0,0,0), (1,1,1), (0,1,1), (0,8,8), (7,8,8), (8,8,17)]
    for (i,j,k) in test:
        kv = K[i,j,k]
        contrib = 0.0
        ncones = 0
        for s in simps:
            if i in s and j in s and k in s:
                nonz = tuple(sorted(v for v in s if v != 0))
                d = dets.get(nonz, 0)
                contrib += np.sign(d) if d != 0 else 0
                ncones += 1
        print(f"  K[{i},{j},{k}] = {kv:>6} | Σsign(det) = {contrib:>6.1f} | ratio = {kv/contrib if contrib else 'N/A'}")

    # Hypothesis: K[i,j,k] = Σ_σ vol(σ) where vol = det of rays / det of full cone lattice?
    # Let's try including the CY: K = Σ_σ (1/|det|) — volume form on CY
    print("\n=== test: K vs Σ_σ 1/|det| ===")
    for (i,j,k) in test:
        kv = K[i,j,k]
        contrib = 0.0
        for s in simps:
            if i in s and j in s and k in s:
                nonz = tuple(sorted(v for v in s if v != 0))
                d = dets.get(nonz, 0)
                if d != 0:
                    contrib += 1/abs(d)
        print(f"  K[{i},{j},{k}] = {kv:>6} | Σ1/|det| = {contrib:>8.4f} | ratio = {kv/contrib if contrib else 'N/A'}")

if __name__ == "__main__":
    main()
