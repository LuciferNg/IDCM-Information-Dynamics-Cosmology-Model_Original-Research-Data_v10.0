#!/usr/bin/env python3
"""
O58 script 67 — AA: e₁-e₄ positions = Lucas across instances.
Q: do other (36,98) instances have unit vectors e₁-e₄ at Lucas pts
indices {1,3,7,47}? Or at least Lucas-like positions?
"""
import os, json, re

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

    N_SAMPLE = 30
    targets = list(range(0, min(len(polys), N_SAMPLE)))
    L = {lucas(n) for n in range(1, 10)}  # {1,2,3,4,7,11,18,29,47}

    results = []
    for t in targets:
        P = Polytope(polys[t])
        pts = [tuple(int(x) for x in p) for p in P.points()]
        e_pos = []
        for i, p in enumerate(pts):
            if p in [(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)]:
                e_pos.append(i)
        n_lucas = sum(1 for i in e_pos if i in L)
        results.append(dict(idx=t, e_pos=e_pos, n_lucas=n_lucas,
                            frac=n_lucas/len(e_pos) if e_pos else 0))
        status = "✅" if n_lucas == len(e_pos) else ("🟡" if n_lucas >= 2 else "❌")
        print(f"inst {t:>3}: e-positions={e_pos}, Lucas={n_lucas}/{len(e_pos)} {status}")

    n_full = sum(1 for r in results if r["frac"] == 1.0)
    print()
    print(f"=== SUMMARY ===")
    print(f"instances with ALL e-positions Lucas: {n_full}/{len(results)}")
    total_e = sum(len(r["e_pos"]) for r in results)
    total_l = sum(r["n_lucas"] for r in results)
    print(f"e-positions total: {total_e}, Lucas: {total_l} ({total_l/total_e*100:.1f}%)")
    # random expectation: Lucas in pts range 1..~50 = 9/50 ≈ 18%
    print(f"random expectation: ~18% (9 Lucas / 50 pts)")

    json.dump(results, open("e_positions_lucas_universality.json", "w"), indent=2)
    print("Saved data/e_positions_lucas_universality.json")

if __name__ == "__main__":
    main()
