#!/usr/bin/env python3
"""
O58 script 63 — W: vertex index Lucas tendency — Zeckendorf + control.
Q: is the 84.1% Lucas vertex-index fraction significant vs a control
family (e.g. h11=37 or random h11)? And is it Zeckendorf-related?
"""
import os, json, re
from collections import Counter

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def lucas(n):
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def zeckendorf(n):
    """Zeckendorf representation: sum of non-consecutive Fibonacci."""
    fibs = [1, 2, 3, 5, 8, 13, 21, 34, 55]
    out = []
    for f in reversed(fibs):
        if n >= f:
            out.append(f)
            n -= f
    return out

def main():
    os.chdir(DATA)
    from cytools import Polytope, config
    config.enable_experimental_features()
    L = {lucas(n): n for n in range(1, 8)}
    lucas_set = set(L.keys())
    print("Lucas set:", sorted(lucas_set))

    # Load previous results
    data = json.load(open("vertex_lucas_universality.json"))
    print(f"\n=== W: vertex index analysis ({len(data)} instances) ===\n")

    # full vertex index distribution
    idx_counter = Counter()
    for r in data:
        for i in r["v_idx"]:
            idx_counter[i] += 1
    print("vertex index frequency (all instances):")
    for i in sorted(idx_counter):
        is_l = "← Lucas" if i in lucas_set else ""
        print(f"  index {i:>2}: {idx_counter[i]:>3}  {is_l}")
    print()

    # fraction of indices that are Lucas — already 84.1%
    total_v = sum(idx_counter.values())
    total_l = sum(v for i, v in idx_counter.items() if i in lucas_set)
    print(f"Lucas fraction: {total_l}/{total_v} = {total_l/total_v*100:.1f}%")

    # Zeckendorf: are vertex indices Zeckendorf-representable?
    print("\n=== Zeckendorf of vertex indices ===")
    for i in sorted(idx_counter):
        if i <= 0: continue
        z = zeckendorf(i)
        print(f"  {i}: Z = {z} {'(Lucas!)' if i in lucas_set else ''}")

    # control: what's the expected Lucas fraction for random indices?
    # If indices range 1..10, Lucas in [1,10] = {1,2,3,4,7} = 5/10 = 50%
    print("\n=== control comparison ===")
    print("random expectation (uniform 1..10): 50%")
    print(f"observed: {total_l/total_v*100:.1f}%")

    # control family: sample a different h11 family and check vertex indices
    # (need polytope data — use PALP quick check on a few h11=37 instances?)
    # For now: report the canonical family's own consistency
    print("\n=== consistency: do ALL instances have index 1? ===")
    all_have_1 = all(1 in r["v_idx"] for r in data)
    print(f"index 1 in all instances: {all_have_1}")
    all_have_2 = all(2 in r["v_idx"] for r in data)
    print(f"index 2 in all instances: {all_have_2}")
    all_have_3 = all(3 in r["v_idx"] for r in data)
    print(f"index 3 in all instances: {all_have_3}")

    # Lucas distribution by index
    print("\n=== which Lucas indices dominate? ===")
    for i in sorted(lucas_set):
        if i in idx_counter:
            print(f"  L_{L[i]} = {i}: {idx_counter[i]} instances ({idx_counter[i]/len(data)*100:.0f}%)")

    # Control: index 8 (not Lucas ≤ 7 except 8 = L? no — Lucas: 2,1,3,4,7,11... 8 NOT Lucas)
    if 8 in idx_counter:
        print(f"\n  index 8 (NOT Lucas): {idx_counter[8]} instances ({idx_counter[8]/len(data)*100:.0f}%)")
    if 9 in idx_counter:
        print(f"  index 9 (NOT Lucas): {idx_counter[9]} instances ({idx_counter[9]/len(data)*100:.0f}%)")

if __name__ == "__main__":
    main()
