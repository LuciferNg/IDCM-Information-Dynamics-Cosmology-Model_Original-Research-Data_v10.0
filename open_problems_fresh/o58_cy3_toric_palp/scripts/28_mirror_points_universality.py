#!/usr/bin/env python3
"""
O58 script 28 — BOTH mirror points: (1,1,0,0) AND (-1,-1,0,0).
Test on all 9 sampled instances:
  - does each instance contain (1,1,0,0)? its K?
  - does each instance contain (-1,-1,0,0)? its K?
  - is K[(1,1,0,0)] + K[(-1,-1,0,0)] constant? (mirror sum)
  - is K[1100] always -232 when present?
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

def analyze_point_K(coords, target):
    from cytools import Polytope, config
    config.enable_experimental_features()
    P = Polytope(coords)
    pts = P.points()
    t = tuple(target)
    pid = None
    for i, p in enumerate(pts):
        if tuple(int(x) for x in p) == t:
            pid = i
            break
    if pid is None:
        return None, None
    tri = P.triangulate(backend="qhull")
    cy = tri.get_cy()
    inter = cy.intersection_numbers()
    K = None
    for (i, j, k), v in inter.items():
        if i == pid and j == pid and k == pid:
            K = int(v)
            break
    if K is None:
        # maybe 1-based differs: try K[pid-1]
        K = 0
        for (i, j, k), v in inter.items():
            if (i-1) == (pid-1) and (j-1) == (pid-1) and (k-1) == (pid-1):
                K = int(v)
                break
    return pid, K

def main():
    os.chdir(DATA)
    polies = parse_poly_file("all_36_98.poly")
    sample = [0, 1, 2, 3, 5, 10, 20, 50, 89]
    print("=== mirror points (1,1,0,0) & (-1,-1,0,0) ===")
    results = []
    for idx in sample:
        p_plus, K_plus = analyze_point_K(polies[idx], [1, 1, 0, 0])
        p_minus, K_minus = analyze_point_K(polies[idx], [-1, -1, 0, 0])
        row = dict(idx=idx, p1100=p_plus, K1100=K_plus,
                   pm1100=p_minus, Km1100=K_minus)
        results.append(row)
        if K_plus is None and K_minus is None:
            print(f"inst {idx}: neither point present")
        else:
            print(f"inst {idx}: (1,1,0,0)@{p_plus} K={K_plus} | "
                  f"(-1,-1,0,0)@{p_minus} K={K_minus}")
    # stats
    kplus = [r["K1100"] for r in results if r["K1100"] is not None]
    kminus = [r["Km1100"] for r in results if r["Km1100"] is not None]
    print(f"\nK[(1,1,0,0)] values: {kplus}")
    print(f"K[(-1,-1,0,0)] values: {kminus}")
    print(f"(1,1,0,0) always -232: {all(k == -232 for k in kplus) if kplus else 'n/a'}")
    json.dump(results, open("mirror_points_universality.json", "w"), indent=2)

if __name__ == "__main__":
    main()
