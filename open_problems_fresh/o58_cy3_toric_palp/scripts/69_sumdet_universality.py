#!/usr/bin/env python3
"""
O58 script 69 — AB+AD: Σ|det|=-χ+L₉ and div3 star=48 across instances.
Q1 (AB): does Σ|det| = -χ + L₉ hold for other (36,98) instances?
Q2 (AD): does div3 star Σ|det| = 48 = N_d+B hold across instances?
For each: compute triangulation, Σ|det| over cones, compare with
-χ + L₉ = 124 + 76 = 200 (if h11,h21 fixed = 36,98, χ fixed = -124,
L₉ = 76 fixed → prediction is always 200).
Also check div-star sums.
"""
import os, json, re, numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def main():
    os.chdir(DATA)
    from cytools import Polytope, config
    config.enable_experimental_features()

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

    # sample instances (mix of sizes)
    N_SAMPLE = 10
    targets = [0, 1, 2, 3, 5, 10, 20, 50, 89, 15]
    targets = [t for t in targets if t < len(polys)][:N_SAMPLE]
    L9 = 76  # Lucas 9
    chi = 2*(36-98)  # -124
    pred = -chi + L9  # 200

    print(f"=== AB+AD: Σ|det| across instances ===\n")
    print(f"prediction: -χ + L₉ = {pred} (χ={chi}, L₉={L9})\n")

    results = []
    for t in targets:
        P = Polytope(polys[t])
        tri = P.triangulate(backend="qhull")
        pts = [tuple(int(x) for x in p) for p in P.points()]
        simps = [list(s) for s in tri.simplices()]
        dets = {}
        for s in simps:
            nonz = [v for v in s if v != 0]
            if len(nonz) >= 4:
                M = np.array([pts[v] for v in nonz[:4]])
                dets[tuple(sorted(nonz))] = np.linalg.det(M)
        total = sum(abs(d) for d in dets.values())
        # star sums
        stars = {}
        for d in [0, 1, 3, 4, 7, 8]:
            ssum = 0.0
            for s in simps:
                if d in s:
                    nonz = tuple(sorted(v for v in s if v != 0))
                    ssum += abs(dets.get(nonz, 0))
            stars[d] = ssum
        # find e₁-e₄ positions (unit vectors)
        e_pos = [idx for idx, p in enumerate(pts) if p in [(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)]]
        match = bool(abs(total - pred) < 1e-6)
        results.append(dict(idx=int(t), npts=int(len(pts)), total=float(total),
                            pred=float(pred), match=match,
                            stars={int(k): float(v) for k, v in stars.items()},
                            e_pos=[int(x) for x in e_pos]))
        print(f"inst {t:>3}: npts={len(pts):>2}, Σ|det|={total:>8.3f}, "
              f"match={match}, stars={ {k: round(v,2) for k,v in stars.items()} }")
    print()

    n_match = sum(1 for r in results if r["match"])
    print(f"Σ|det| = -χ+L₉ match: {n_match}/{len(results)}")
    # div3 star = 48?
    n_48 = sum(1 for r in results if abs(r["stars"].get(3, 0) - 48) < 1e-6)
    print(f"div3 star = 48: {n_48}/{len(results)}")
    # div8 star = 8?
    n_8 = sum(1 for r in results if abs(r["stars"].get(8, 0) - 8) < 1e-6)
    print(f"div8 star = 8: {n_8}/{len(results)}")

    json.dump(results, open("sumdet_universality.json", "w"), indent=2)
    print("Saved data/sumdet_universality.json")

if __name__ == "__main__":
    main()
