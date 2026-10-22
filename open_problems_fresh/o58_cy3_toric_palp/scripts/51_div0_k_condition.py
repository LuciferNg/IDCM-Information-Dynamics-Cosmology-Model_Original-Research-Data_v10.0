#!/usr/bin/env python3
"""
O58 script 51 — O: N_d+1=45 點解只喺 canonical? div0 K 值條件.
Q: div0 (origin) K[0,0,0] = -360 = -8×45 only in canonical (6v).
Other instances: -336..-640. What determines the value?
Hypothesis: div0 K = -8 × (something about the polytope: N points, N lattice
points, total lattice points, vertex count).
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
    inter = cy.intersection_numbers()
    pts = [tuple(int(x) for x in p) for p in P.points()]
    verts = [tuple(int(x) for x in v) for v in P.vertices()]

    print("=== O: div0 K value analysis (canonical) ===")
    print(f"K[0,0,0] = {K[0,0,0]}")
    print(f"N_lattice_points (M) = {len(pts)}")
    print(f"N_vertices = {len(verts)}")
    print(f"N_interior = {len(pts) - len(verts)}")
    print()
    print(f"-K[0,0,0]/8 = {-K[0,0,0]/8} = 45")
    print(f"45 = N_d + 1 = 44 + 1")
    print(f"45 = L₇ + B² = 29 + 16")
    print(f"45 = Σγ/2 = 90/2")
    print(f"45 = (N_lattice + 42)/2? 48+42=90/2=45 ✓ (N_lattice=48)")
    print()

    # across instances: what correlates with K000?
    d0 = json.load(open("divisor0_universality.json"))
    p1100 = json.load(open("point_1100_universality.json"))
    print("=== across instances ===")
    print(f"{'inst':>4} {'npts':>5} {'nvert':>5} {'K000':>6} {'-K/8':>5} {'45?':>4}")
    for r in d0:
        print(f"{r['idx']:>4} {r.get('npts','?'):>5} {r.get('nvert','?'):>5} {r['k000']:>6} {-r['k000']//8:>5} {'✓' if -r['k000']/8 == 45 else ''}")
    print()

    # correlation: K000 vs npts
    print("=== K000 vs polytope size ===")
    for r in d0:
        npts = r.get('npts', '?')
        nvert = r.get('nvert', '?')
        print(f"  inst {r['idx']}: npts={npts}, nvert={nvert}, K000={r['k000']}, -K/8={-r['k000']/8}")
    print()
    print("canonical 6v: M=48 (44+4), K000=-360 → -K/8=45=N_d+1")
    print("7v inst 2: K000=-640 → -K/8=80 = ?")
    print("80 = 44+36? 80 = 2×40? 80 = 5×16 = 5B²? 80 = 44+36 = N_d+h11!")
    print()
    print("=== 80 = N_d + h11? ===")
    print("80 = 44 + 36 = N_d + h11 ✓ for inst 2 (7v)")
    print("45 = 44 + 1 for canonical")
    print("-> -K[0,0,0]/8 = N_d + (extra) where extra varies")
    print("canonical: extra=1, inst2: extra=36")
    print()

    # hypothesis: extra = number of vertices - 5? 
    # canonical: 6 verts → extra 1 = 6-5 ✓; inst2: 7 verts → 36? no.
    print("=== testing extra hypotheses ===")
    for r in d0:
        nv = r.get('nvert', None)
        if nv is None: continue
        extra = -r['k000']/8 - 44
        print(f"  inst {r['idx']}: nvert={nv}, extra={extra}, extra-1={extra-1}")

if __name__ == "__main__":
    main()
