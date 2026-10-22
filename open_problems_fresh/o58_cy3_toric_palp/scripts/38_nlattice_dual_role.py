#!/usr/bin/env python3
"""
O58 script 38 — E: (1,1,0,0) role in N-lattice (dual polytope).
Q: what does the point (1,1,0,0) in M-lattice correspond to in N-lattice?
Check: which N-lattice points pair with it (inner product), which facets contain it.
"""
import os, json, numpy as np
from itertools import permutations

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def main():
    os.chdir(DATA)
    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    # M-lattice point (1,1,0,0)
    m1100 = np.array([1,1,0,0])
    # N-lattice points (dual polytope)
    N = P.dual()  # N-lattice polytope
    npts = [np.array([int(x) for x in p]) for p in N.points()]
    print(f"N-lattice: {len(npts)} points")
    # inner products with (1,1,0,0)
    ips = [(int(m1100 @ p), idx, tuple(int(x) for x in p)) for idx, p in enumerate(npts)]
    ips.sort(reverse=True)
    print("\nTop inner products M(1,1,0,0)·N-point:")
    for ip, idx, p in ips[:12]:
        print(f"  <{idx:2d}> {p} → {ip}")
    print("\nBottom:")
    for ip, idx, p in ips[-8:]:
        print(f"  <{idx:2d}> {p} → {ip}")
    print()
    # which N-points give +1 (facets containing (1,1,0,0))? +2?
    pos1 = [(idx, p) for ip, idx, p in ips if ip == 1]
    pos2 = [(idx, p) for ip, idx, p in ips if ip == 2]
    zero = [(idx, p) for ip, idx, p in ips if ip == 0]
    print(f"N-points with IP=1 (facets containing m1100?): {len(pos1)}")
    for idx, p in pos1[:10]:
        print(f"  <{idx}> {p}")
    print(f"\nN-points with IP=2: {len(pos2)}")
    for idx, p in pos2[:10]:
        print(f"  <{idx}> {p}")
    print(f"\nN-points with IP=0: {len(zero)}")
    # K_Chain correspondence: 44-site? N=85 points
    print("\nK_Chain: N points = 85 = ?")
    print("  85 = 44 + 41 = 44 + Σγ/2 - 4")

if __name__ == "__main__":
    main()
