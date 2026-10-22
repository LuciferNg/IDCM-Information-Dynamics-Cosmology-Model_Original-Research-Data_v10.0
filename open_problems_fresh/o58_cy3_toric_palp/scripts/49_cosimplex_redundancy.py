#!/usr/bin/env python3
"""
O58 script 49 — M: co-simplex K=0 消去機制 (redundant divisor analysis).
Q: are the 554 vanishing co-simplex triples explained by divisor-basis
redundancy? cy.divisor_basis() returns 32 of 36 (4 redundant).
Hypothesis: triples involving redundant divisors (or their linear combos)
are the ones that vanish.
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
    simps = [set(s) for s in tri.simplices()]
    K = np.load("kappa_36d_true.npy")

    # divisor basis (1-based per CYTools)
    basis_1b = cy.divisor_basis()
    basis = [b - 1 for b in basis_1b]  # 0-based
    redundant = [d for d in range(36) if d not in basis]
    print(f"divisor_basis (0-based): {sorted(basis)}")
    print(f"count: {len(basis)}")
    print(f"REDUNDANT divisors (0-based): {sorted(redundant)}")
    print(f"redundant count: {len(redundant)}")
    print()

    # all co-simplex triples
    cosimp = set()
    for cs in simps:
        lst = sorted(v for v in cs if v < 36)
        for i in range(len(lst)):
            for j in range(i, len(lst)):
                for k in range(j, len(lst)):
                    cosimp.add((lst[i], lst[j], lst[k]))
    zero = [(i,j,k) for (i,j,k) in cosimp if K[i,j,k] == 0]
    nz = [(i,j,k) for (i,j,k) in cosimp if K[i,j,k] != 0]
    print(f"co-simplex total: {len(cosimp)}, zero: {len(zero)}, nonzero: {len(nz)}")
    print()

    # H1: do zero triples contain more redundant divisors?
    def n_redundant(t):
        return sum(1 for d in t if d in redundant)
    z_red = [n_redundant(t) for t in zero]
    n_red = [n_redundant(t) for t in nz]
    from collections import Counter
    print("zero triples redundant-count distribution:", dict(Counter(z_red)))
    print("nz   triples redundant-count distribution:", dict(Counter(n_red)))
    print()

    # H2: ALL-nonzero-basis triples — are they always nonzero?
    pure_basis_zero = [t for t in zero if n_redundant(t) == 0]
    pure_basis_nz = [t for t in nz if n_redundant(t) == 0]
    print(f"pure-basis (no redundant) triples: zero={len(pure_basis_zero)}, nz={len(pure_basis_nz)}")
    print()

    # H3: K as function of redundant divisor presence
    # if redundant divisors are linear combos of basis, K[i,j,k] for redundant i
    # is determined by linearity. Check linearity consistency:
    # K[i,j,k] for redundant i should equal sum over basis expansion.
    print("=== linearity check for redundant divisors ===")
    # build expansion: represent each divisor's intersection with basis
    # Use K[i,j,k] where i redundant, j,k basis: reconstruct K[basis,...]? 
    # Instead: check if K[i,j,k] is a linear function: for fixed (j,k),
    # K[.,j,k] as vector over i — redundant rows should lie in span of basis rows
    M = np.zeros((36, 36))  # K[i,j,k] flattened over k for each (i,j)
    # too big; sample instead: check one redundant divisor at a time
    for red in sorted(redundant):
        # K[red, :, :] matrix
        row = np.zeros((36, 36))
        for j in range(36):
            for k in range(36):
                row[j, k] = K[red, j, k]
        # basis rows
        basis_rows = np.array([np.array([[K[b, j, k] for k in range(36)] for j in range(36)]) for b in basis])
        # flatten
        flat = row.flatten()
        bflat = basis_rows.reshape(len(basis), -1)
        # least squares fit
        coef, res, rank, sv = np.linalg.lstsq(bflat.T, flat, rcond=None)
        resid = np.linalg.norm(bflat.T @ coef - flat) / max(np.linalg.norm(flat), 1e-30)
        print(f"  redundant div {red}: fit residual {resid:.2e} (0 = exact linear combo of basis)")
    print()
    print("=== conclusion ===")
    print("If redundant rows are exact linear combos → K=0 for co-simplex")
    print("triples is NOT redundancy — it's genuine geometric vanishing")
    print("(triple of divisors whose cone product misses the CY hypersurface)")

if __name__ == "__main__":
    main()
