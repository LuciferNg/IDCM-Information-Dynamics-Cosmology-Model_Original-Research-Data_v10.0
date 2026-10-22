#!/usr/bin/env python3
"""
O58 script 37 — B: K[0,0,0] value pattern across instances.
Q: does K[0,0,0] correlate with (1,1,0,0) presence / point count / vertex count?
Values: 0:-360, 1:-340, 2:-640, 3:-336, 5:-584, 10:-594, 20:-596, 50:-342, 89:-610
"""
import os, json, numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def main():
    os.chdir(DATA)
    d0 = json.load(open("divisor0_universality.json"))
    p1100 = json.load(open("point_1100_universality.json"))
    iso = json.load(open("island_stats_swap_corrected.json"))
    # vertex counts for these instances from all_36_98.poly
    lines = open("all_36_98.poly").read().splitlines()
    polies = []
    i = 0
    while i < len(lines):
        parts = lines[i].split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            n, d = int(parts[0]), int(parts[1])
            polies.append(dict(n=n, d=d))
            i += n + 1
        else:
            i += 1
    # p1100 is a LIST indexed by position; find by idx field
    p1100_by_idx = {r["idx"]: r for r in p1100}
    print(f"{'inst':>4} {'nvert':>5} {'K000':>6} {'has1100':>8} {'K1100':>6} {'K000/8':>7}")
    for r in d0:
        idx = r["idx"]
        has = p1100_by_idx[idx]["has"]
        k1100 = p1100_by_idx[idx].get("K")
        nv = polies[idx]["n"]
        k000 = r["k000"]
        print(f"{idx:>4} {nv:>5} {k000:>6} {str(has):>8} {str(k1100):>6} {k000/8:>7.1f}")
    print()
    # analysis: K000 vs vertex count, vs has1100
    k000s = [r["k000"] for r in d0]
    nverts = [polies[r["idx"]]["n"] for r in d0]
    has = [p1100_by_idx[r["idx"]]["has"] for r in d0]
    print("K000 by has1100:")
    print("  has1100:", [r['k000'] for r in d0 if p1100_by_idx[r['idx']]['has']])
    print("  no1100: ", [r['k000'] for r in d0 if not p1100_by_idx[r['idx']]['has']])
    print()
    print("K000 by vertex count:")
    from collections import defaultdict
    byv = defaultdict(list)
    for r in d0:
        byv[polies[r['idx']]['n']].append(r['k000'])
    for v in sorted(byv):
        print(f"  {v} verts: {byv[v]}")
    print()
    # is K000 always negative?
    print("all K000 < 0:", all(k < 0 for k in k000s))
    print("K000 range:", min(k000s), "to", max(k000s))
    # K000/8 values
    print("K000/8:", sorted(set(round(k/8,1) for k in k000s)))
    # look for structure: -360=-8×45, -640=-8×80, -584=-8×73, -594=-8×74.25...
    print()
    print("factor analysis (K000/8):")
    for r in d0:
        k = r["k000"]
        print(f"  inst {r['idx']}: {k} = -8×{abs(k)//8}" + (f".{abs(k)%8}" if abs(k)%8 else ""))

if __name__ == "__main__":
    main()
