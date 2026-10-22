#!/usr/bin/env python3
"""
O58 script 54 — R: redundant divisor 7 嘅雙重角色.
div7 = (0,0,0,1) = e₄ vertex, redundant, L₄=7, residual U(1) position 7.
Q: row structure of div7 in K — row sum, cross with core, star size.
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
    K = np.load("kappa_36d_true.npy")
    pts = [tuple(int(x) for x in p) for p in P.points()]
    verts = [tuple(int(x) for x in v) for v in P.vertices()]
    glsm = cy.glsm_charge_matrix()
    simps = [set(s) for s in tri.simplices()]

    print("=== R: divisor 7 double role ===\n")
    print(f"div 7 pt = {pts[7]}, vertex? {pts[7] in verts}")
    print(f"div 7 glsm_sum = {int(glsm[:,7].sum())}")
    print(f"div 7 diag K[7,7,7] = {K[7,7,7]}")
    star7 = sum(1 for cs in simps if 7 in cs)
    print(f"div 7 star = {star7}")
    print()

    # row 7 structure
    row7 = [(j, k, int(K[7,j,k])) for j in range(36) for k in range(36) if K[7,j,k] != 0]
    print(f"row 7 (K[7,j,k]≠0): {len(row7)} entries")
    # unique j
    js = sorted(set(j for j, k, v in row7))
    print(f"  j values: {js}")
    print(f"  j count: {len(js)}")
    # values
    vals = sorted(set(v for j, k, v in row7))
    print(f"  values: {vals}")
    print()

    # row sum
    rowsum = int(K[7].sum())
    print(f"row 7 sum (Σ_k K[7,7,k]? no — Σ over j,k) = {rowsum}")
    # the zero-sum functional found before: Σ_j K[7,7,j] = 0
    zsum = sum(int(K[7,7,k]) for k in range(36))
    print(f"Σ_k K[7,7,k] = {zsum} (0 = perfect zero-sum!)")
    print()

    # cross with core divisors
    print("=== div7 × core ===")
    core = [0, 1, 3, 4, 8, 17, 33]
    for d in core:
        v = int(K[7, d, d]) if (7, d, d) in [(7, d, d)] else int(K[7, d, d])
        print(f"  K[7,{d},{d}] = {v}")
    print()

    # residual U(1) position 7 — what U(1) charge is that?
    print("=== residual U(1) position 7 ===")
    # residual positions [0,3,7,25,28,29,30,31]
    # what does U(1) #7 charge on div7?
    q7_u1 = glsm[7, :].astype(int)  # row 7 of GLSM = U(1) 7 charges on all rays
    print(f"U(1)#7 charges on all 37 rays: {q7_u1.tolist()}")
    print(f"U(1)#7 charge on div7: {q7_u1[7]}")
    print(f"U(1)#7 charge on div8: {q7_u1[8]}")
    print(f"U(1)#7 charge on div0: {q7_u1[0]}")
    print()

    # compare with L₄=7: 7 = L₄; div7 = e₄ (4th vertex!)
    print("=== 7 = e₄ vertex: L₄ connection ===")
    print("div 7 = (0,0,0,1) = e₄ = 4th coordinate vertex")
    print("L₄ = 7 (Lucas) — div7 index = L₄ value!")
    print("residual U(1) position 7 — same 7")
    print("γ₇ mode — n=7")
    print("→ 7 appears 4 ways: vertex e₄, divisor index 7, U(1) position 7, γ₇ mode")
    print()

    # is there a pattern: vertex e_n ↔ divisor index = L_n?
    print("=== other vertices vs Lucas ===")
    for v in verts:
        idx = pts.index(v)
        print(f"  vertex {v} at pts[{idx}] — L? {idx} vs Lucas {[i for i in range(12) if lucas(i)==idx]}")
    print()

def lucas(n):
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a

if __name__ == "__main__":
    main()
