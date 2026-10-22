#!/usr/bin/env python3
"""
O58 script 09 — Yukawa hierarchy from TRUE κ at a LEGAL Kähler tip.
O57 found: J* is NOT in the Kähler cone (quadratic positivity fails);
φ-power t gives 5 finite e^{−V} masses. Here we use the canonical
polytope's own Kähler cone (cy.toric_kahler_cone()) tip, project κ·t,
and look at the φ-exponent hierarchy of eigenvalues (O50 upgrade:
real geometry instead of d_tensor).
"""
import subprocess, os, json, sys, numpy as np, math
from itertools import permutations

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
PHI = (1 + math.sqrt(5)) / 2

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

    # Kähler cone
    kc = cy.toric_kahler_cone()
    print("Kähler cone dim:", kc.dim())
    basis = cy.divisor_basis()
    print("divisor basis (1-based):", basis)

    # try cone tip (stretched)
    try:
        tip = kc.tip_of_stretched_cone(1.0)
        print("tip len:", len(tip))
        # map to 36D: divisor_basis indices are 1-based into 36; tip is 32D
        t36 = np.zeros(36)
        for idx, bidx in enumerate(basis):
            t36[bidx - 1] = tip[idx]
        # Yukawa Y = K·t (contract last index)
        Y = np.einsum('ijk,k->ij', K, t36)
        evals = np.linalg.eigvalsh(Y)
        pos = evals[evals > 1e-10]
        print(f"Y eigenvalues: {len(evals)} total, {len(pos)} positive")
        pos_sorted = np.sort(pos)[::-1]
        # φ-exponents relative to largest
        if len(pos_sorted) > 1:
            exps = [-math.log(v/pos_sorted[0], PHI) for v in pos_sorted]
            print("φ-exponents (desc):", [round(e, 3) for e in exps[:12]])
            # near-integer test
            near_int = sum(1 for e in exps[:12] if abs(e - round(e)) < 0.1)
            print(f"near-integer exponents (first 12): {near_int}/12")
    except Exception as e:
        print("tip failed:", e)

    # φ-power t in divisor basis (t_i = φ^(35-i) → t32)
    t32 = np.array([PHI ** (35 - i) for i in range(32)])
    # normalize to max 1 (avoid overflow)
    t32 = t32 / t32.max()
    t36b = np.zeros(36)
    for idx, bidx in enumerate(basis):
        t36b[bidx - 1] = t32[idx]
    Y2 = np.einsum('ijk,k->ij', K, t36b)
    ev2 = np.linalg.eigvalsh(Y2)
    pos2 = np.sort(ev2[ev2 > 1e-10])[::-1]
    print(f"\nφ-power t: {len(pos2)} positive eigenvalues")
    if len(pos2) > 1:
        exps2 = [-math.log(v/pos2[0], PHI) for v in pos2]
        print("φ-exponents (desc):", [round(e, 3) for e in exps2[:12]])
        near_int2 = sum(1 for e in exps2[:12] if abs(e - round(e)) < 0.1)
        print(f"near-integer exponents (first 12): {near_int2}/12")
        # mass ratios
        if len(pos2) >= 3:
            print(f"λ1/λ2 = {pos2[0]/pos2[1]:.4f} (φ^{exps2[1]:.2f})")
            print(f"λ2/λ3 = {pos2[1]/pos2[2]:.4f} (φ^{exps2[2]-exps2[1]:.2f})")

    with open("yukawa_true_kappa.json", "w") as f:
        json.dump(dict(nnz=int(np.count_nonzero(K)),
                       tip_exps=[round(e,3) for e in locals().get('exps', [])[:12]],
                       phi_exps=[round(e,3) for e in locals().get('exps2', [])[:12]]), f, indent=2)

if __name__ == "__main__":
    main()
