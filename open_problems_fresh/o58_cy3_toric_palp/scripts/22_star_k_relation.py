#!/usr/bin/env python3
"""
O58 script 22 — STAR SIZE ↔ K[i,i,i] relation (the -232/-360 mechanism).
Claims:
  1. Only 2 points have star=8: pts[8]=(1,1,0,0), pts[36]=(-1,-1,0,0)
  2. These are the ONLY negative-large-K divisors: K=-232, -360
  3. pts[8] ↔ pts[36] are Z₂ mirror partners (p → -p)
  4. K[i,i,i] = -8 × f(star)? Test: for star=8, K = -8×{29, 45}
     where 29=L₇ (Lucas), 45=N_d+1
  5. Check ALL star sizes vs K ratio — find the pattern
"""
import os, json, numpy as np, math
from itertools import permutations
from collections import Counter

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

    pts = P.points()
    simps = tri.simplices()
    star = Counter()
    for s in simps:
        for i in s:
            if i != 0:
                star[i] += 1

    print("=== Z₂ mirror check: pts[8] vs pts[36] ===")
    p8 = tuple(int(x) for x in pts[8])
    p36 = tuple(int(x) for x in pts[36])
    neg8 = tuple(-x for x in p8)
    print(f"pts[8]  = {p8}")
    print(f"pts[36] = {p36}")
    print(f"-pts[8] = {neg8}")
    print(f"pts[36] == -pts[8]: {p36 == neg8}")

    print("\n=== ALL star sizes and K[i,i,i] ===")
    rows = []
    for idx in sorted(star):
        if idx >= 37:
            continue
        k_idx = idx - 1
        kiii = int(K[k_idx, k_idx, k_idx])
        rows.append((idx, star[idx], kiii, tuple(int(x) for x in pts[idx])))
    for idx, st, kiii, p in rows:
        mark = ""
        if kiii < 0:
            mark = " ← negative"
        print(f"  pts[{idx:2d}] star={st:2d} K={kiii:6d} {p}{mark}")

    print("\n=== star=8 special ===")
    s8 = [(idx, kiii, p) for idx, st, kiii, p in rows if st == 8]
    for idx, kiii, p in s8:
        print(f"  pts[{idx}] K={kiii} = -8×{-kiii//8} | -kiii/8: {-kiii/8:.2f}")

    print("\n=== Lucas check ===")
    L = [2, 1]
    for n in range(2, 16):
        L.append(L[-1] + L[-2])
    lucas = {v: n for n, v in enumerate(L)}
    for idx, kiii, p in s8:
        q = -kiii // 8
        if q in lucas:
            print(f"  pts[{idx}]: -K/8 = {q} = L_{lucas[q]} ✅ Lucas")
        else:
            print(f"  pts[{idx}]: -K/8 = {q} = N_d+1 = 45 (not Lucas)")

    # hypothesis: K = -8 × (star-relative weight)? star=8 for both, so
    # the difference (29 vs 45) must come from the POINT, not the star.
    # pts[8]=(1,1,0,0): 1+1+0+0 = 2; pts[36]=(-1,-1,0,0): sum = -2
    # norm²: 2 vs 2 — same!
    print("\n=== point invariants ===")
    for idx, kiii, p in s8:
        print(f"  pts[{idx}]: sum={sum(p)}, norm²={sum(x*x for x in p)}, "
              f"max|coord|={max(abs(x) for x in p)}")

    def clean(x):
        if isinstance(x, (np.integer,)):
            return int(x)
        if isinstance(x, (np.floating,)):
            return float(x)
        return x

    json.dump(dict(star8=[dict(idx=int(idx), K=int(kiii), pt=[int(x) for x in p]) for idx, kiii, p in s8],
                    z2_mirror=bool(p36 == neg8),
                    star_hist={str(k): int(v) for k, v in Counter(star.values()).items()}),
              open("star_k_relation.json", "w"))

if __name__ == "__main__":
    main()
