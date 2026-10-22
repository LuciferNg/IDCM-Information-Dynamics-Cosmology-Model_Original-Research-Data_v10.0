#!/usr/bin/env python3
"""
O58 script 29 — Divisor 0 (-360 = -8×45) universality + final verification.
Tests: in each sampled instance, what is K[0,0,0] (divisor 0)?
Is it always -360? Is it always -8×(N_d+1)?
"""
import os, json
from collections import Counter

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def parse_poly_file(path):
    lines = open(path).read().splitlines()
    polies = []
    i = 0
    while i < len(lines):
        parts = lines[i].split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            n, d = int(parts[0]), int(parts[1])
            coords = []
            ok = True
            j = i + 1
            for _ in range(n):
                if j >= len(lines):
                    ok = False
                    break
                cp = lines[j].split()
                if len(cp) != d:
                    ok = False
                    break
                try:
                    coords.append([int(x) for x in cp])
                except ValueError:
                    ok = False
                    break
                j += 1
            if ok:
                polies.append(coords)
                i = j
                continue
        i += 1
    return polies

def get_diag(coords):
    from cytools import Polytope, config
    config.enable_experimental_features()
    P = Polytope(coords)
    tri = P.triangulate(backend="qhull")
    cy = tri.get_cy()
    inter = cy.intersection_numbers()
    return inter, P, tri, cy

def main():
    os.chdir(DATA)
    polies = parse_poly_file("all_36_98.poly")
    sample = [0, 1, 2, 3, 5, 10, 20, 50, 89]
    print("=== divisor 0 K[0,0,0] across instances ===")
    results = []
    for idx in sample:
        try:
            inter, P, tri, cy = get_diag(polies[idx])
            k000 = inter.get((0,0,0), 0)
            k888 = inter.get((8,8,8), None)
            has_1100 = any(tuple(int(x) for x in p) == (1,1,0,0) for p in P.points())
            print(f"inst {idx}: K[0,0,0]={k000}, K[8,8,8]={k888}, has(1,1,0,0)={has_1100}")
            results.append(dict(idx=idx, k000=int(k000), k888=int(k888) if k888 is not None else None,
                                has_1100=has_1100))
        except Exception as e:
            print(f"inst {idx}: ERROR {str(e)[:60]}")
    # stats
    k000s = [r["k000"] for r in results if r["k000"] != 0]
    k888s = [r["k888"] for r in results if r["k888"] is not None]
    print(f"\nK[0,0,0] values: {k000s}")
    print(f"K[8,8,8] values: {k888s}")
    print(f"K[0,0,0] always -360: {all(k == -360 for k in k000s)}")
    print(f"K[8,8,8] always -232 when present: {all(k == -232 for k in k888s)}")
    json.dump(results, open("divisor0_universality.json", "w"), indent=2)

if __name__ == "__main__":
    main()
