#!/usr/bin/env python3
"""
O58 script 61 — X: verify q8=-q0-1 correspondence FIRST.
CRITICAL: does GLSM column d correspond to pts[d] or pts[d+1]?
(rays vs divisors off-by-one check)
Then: lattice relation pts[8] = pts[1]+pts[2]?
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
    glsm = cy.glsm_charge_matrix()  # shape (32, 37)?
    print(f"glsm shape: {glsm.shape}")
    pts = [tuple(int(x) for x in p) for p in P.points()]
    print(f"n points: {len(pts)}")
    print()

    # GLSM: (32,37) means 32 U(1) × 37 rays
    # 37 rays = which pts? Check: are ray charges integer per column?
    for d in [0, 1, 2, 7, 8, 36]:
        q = glsm[:, d].astype(int)
        print(f"glsm col {d}: sum={q.sum()}, nz={np.count_nonzero(q)}, "
              f"pts[{d}]={pts[d] if d < len(pts) else 'OOR'}")
    print()

    # coordinate rays: unit vectors with single +1
    print("=== identify coordinate vs non-coordinate rays ===")
    coord = []
    noncoord = []
    for d in range(glsm.shape[1]):
        q = glsm[:, d].astype(int)
        if np.count_nonzero(q) == 1 and q.sum() == 1:
            coord.append(d)
        else:
            noncoord.append(d)
    print(f"coordinate rays (cols): {coord}")
    print(f"non-coordinate rays (cols): {noncoord}")
    print()

    # which pts are coordinate (unit vectors)?
    print("=== pts that are unit vectors ===")
    for i, p in enumerate(pts):
        if p in [(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)]:
            print(f"  pts[{i}] = {p} ← unit vector")
    print()

    # lattice relations: pts[8] = ?
    print("=== lattice relations involving pts[8] ===")
    p8 = np.array(pts[8])
    print(f"pts[8] = {p8}")
    # find pairs summing to pts[8]
    for i in range(len(pts)):
        for j in range(i, len(pts)):
            if np.array_equal(np.array(pts[i]) + np.array(pts[j]), p8):
                print(f"  pts[{i}] + pts[{j}] = pts[8]  ({pts[i]} + {pts[j]})")
    print()

    # GLSM charge of pts[8] via linearity: if pts[8] = pts[i]+pts[j],
    # then q(pts[8]) = q(pts[i]) + q(pts[j]) ONLY if q is linear on lattice
    # → test linearity: does glsm column of ray containing pts[8]
    # equal sum of columns of rays containing pts[i], pts[j]?
    print("=== linearity test: q(pts[8]) vs q(pts[i])+q(pts[j]) ===")
    # need ray→pts mapping. Check glsm columns 8 and compare with
    # columns for pts[1] and pts[2]-like rays.
    for i in range(len(pts)):
        if np.array_equal(np.array(pts[i]), np.array(pts[1]) + np.array(pts[2])):
            print(f"  pts[{i}] = pts[1]+pts[2]")
    print("pts[1] =", pts[1], ", pts[2] =", pts[2])

if __name__ == "__main__":
    main()
