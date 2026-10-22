#!/usr/bin/env python3
"""
O58 script 59 — T: vertex index = Lucas universality across 100 instances.
Q: do other (36,98) instances have coordinate vertices at Lucas indices?
For each instance: list vertices, check if any 4 (or subset) of the
coordinate vertex indices = consecutive Lucas L₁-L₄ (1,3,4,7).
"""
import os, json, re, numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def lucas(n):
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def main():
    os.chdir(DATA)
    from cytools import Polytope, config
    config.enable_experimental_features()

    # read all_36_98.poly
    polys = []
    with open("all_36_98.poly") as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if re.match(r'^\d+ \d+$', line):
            n, d = map(int, line.split())
            verts = []
            for k in range(n):
                i += 1
                verts.append([int(x) for x in lines[i].strip().split()])
            polys.append(verts)
        i += 1
    print(f"polytopes: {len(polys)}")

    # sample subset for speed (CYTools slow: 2-5s each)
    N_SAMPLE = 30
    targets = list(range(0, min(len(polys), N_SAMPLE)))
    L = {lucas(n): n for n in range(1, 8)}
    print(f"Lucas: {L}")
    print()

    results = []
    for t in targets:
        P = Polytope(polys[t])
        pts = [tuple(int(x) for x in p) for p in P.points()]
        verts = [tuple(int(x) for x in v) for v in P.vertices()]
        v_idx = sorted(pts.index(v) for v in verts)
        # coordinate vertices: unit vectors e_i
        coord = [i for i in v_idx if pts[i] in [(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)]]
        # check: which vertex indices are Lucas?
        lucas_idx = [i for i in v_idx if i in L.values()]
        # check L1-L4 present?
        l1l4 = all(l in lucas_idx for l in [1, 3, 4, 7])
        results.append(dict(idx=t, npts=len(pts), nvert=len(verts),
                            v_idx=v_idx, coord=coord,
                            lucas_idx=lucas_idx, has_L1L4=l1l4))
        status = "✅ L₁-L₄" if l1l4 else ("🟡 partial" if len(lucas_idx) >= 2 else "❌")
        print(f"inst {t:>3}: npts={len(pts):>2}, nvert={len(verts):>2}, "
              f"coord={coord}, lucas_idx={lucas_idx} {status}")

    # summary
    n_full = sum(1 for r in results if r["has_L1L4"])
    print()
    print(f"=== SUMMARY ===")
    print(f"instances with full L₁-L₄ vertex indices: {n_full}/{len(results)}")
    # how many have at least the coord vertices at Lucas positions?
    n_any = sum(1 for r in results if len(r["lucas_idx"]) >= 2)
    print(f"instances with ≥2 Lucas vertex indices: {n_any}/{len(results)}")

    json.dump(results, open("vertex_lucas_universality.json", "w"), indent=2)
    print("Saved data/vertex_lucas_universality.json")

if __name__ == "__main__":
    main()
