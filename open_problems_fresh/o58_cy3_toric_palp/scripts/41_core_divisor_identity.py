#!/usr/bin/env python3
"""
O58 script 41 — G: core divisor {0,1,3,4,8} ↔ K_Chain correspondence.
Questions:
  1. GLSM charges of core divisors — any pattern (q=0/±1, sum)?
  2. divisor 33 (K=40, the large positive) — what is it?
  3. Is {0,1,3,4,8} = 5 elements = B+1? Or related to K_tree?
  4. Which M-lattice points are the core divisors?
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
    cy = tri.get_cy()
    glsm = cy.glsm_charge_matrix()
    inter = cy.intersection_numbers()
    pts = [tuple(int(x) for x in p) for p in P.points()]
    verts = [tuple(int(x) for x in v) for v in P.vertices()]

    core = [0, 1, 3, 4, 7, 8, 17, 33]
    print("=== G: core divisor identities ===")
    print(f"glsm shape: {glsm.shape} (32 U(1) × {glsm.shape[1]} rays)")
    print(f"{'div':>3} {'pt':>22} {'vertex?':>7} {'glsm_sum':>8} {'q=0':>4} {'q=±1':>5} {'diagK':>6}")
    for d in core:
        p = pts[d]
        isv = p in verts
        s = int(glsm[:, d].sum())
        nz0 = int((glsm[:, d] == 0).sum())
        nz1 = int((np.abs(glsm[:, d]) == 1).sum())
        K = int(inter.get((d, d, d), 0))
        print(f"{d:>3} {str(p):>22} {str(isv):>7} {s:>8} {nz0:>4} {nz1:>5} {K:>6}")

    print("\n=== GLSM charge vectors (core) ===")
    for d in core:
        q = glsm[:, d].astype(int)
        nz = [(i, int(v)) for i, v in enumerate(q) if v != 0]
        print(f"div {d}: {len(nz)} nonzero charges, sample: {nz[:8]}")

    # K_Chain correspondence
    print("\n=== K_Chain correspondence ===")
    print("core = {0,1,3,4,7,8,17,33}")
    print("5-element core {0,1,3,4,8} — is 5 = B+1 = 4+1?")
    print("8 = B×2, 33 = ? (K=40 diag)")
    print("div 33 pt:", pts[33])

    # check: which divisors have K=8 diagonal (the generic value)?
    k8 = [d for d in range(36) if int(inter.get((d,d,d),0)) == 8]
    print(f"\ndivisors with diag K=8: {len(k8)}: {k8}")
    print("K=8 count = 8? B×2?")

    # sum of all diagonals
    diag_sum = sum(int(inter.get((d,d,d),0)) for d in range(36))
    print(f"\nΣ diag K = {diag_sum}")

    json.dump(dict(core=[dict(div=d, pt=pts[d], vertex=pts[d] in verts,
                              glsm_sum=int(glsm[:,d].sum()),
                              nz_charges=[(int(i),int(v)) for i,v in enumerate(glsm[:,d]) if v!=0],
                              K=int(inter.get((d,d,d),0))) for d in core],
                   k8_divs=k8, diag_sum=int(diag_sum)),
              open("core_divisor_identity.json", "w"), indent=2, default=str)
    print("\nSaved data/core_divisor_identity.json")

if __name__ == "__main__":
    main()
