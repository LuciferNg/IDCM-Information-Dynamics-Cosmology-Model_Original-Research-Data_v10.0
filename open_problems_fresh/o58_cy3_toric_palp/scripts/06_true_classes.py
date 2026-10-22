#!/usr/bin/env python3
"""
O58 script 06 — TRUE equivalence classes of all_36_98.poly via CYTools
is_linearly_equivalent. PALP -N matrix comparison is invalid across
different vertex counts; CYTools does proper GL(4,Z)/affine checks.
We group the 100 instances into equivalence classes (expensive pairwise:
100×99/2 = 4950 checks × ~0.2s = ~17min. Use PALP normal-form first-6-rows
as a cheap pre-filter: only compare within same vertex count AND same
first row pattern, which drastically cuts pairs.)
"""
import subprocess, os, re, json, collections, itertools, sys

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

def main():
    os.chdir(DATA)
    polies = parse_poly_file("all_36_98.poly")
    print(f"{len(polies)} instances", flush=True)

    # cheap invariant: (vertex_count, point_count, sorted column-sum of coords)
    invariants = []
    for i, coords in enumerate(polies):
        colsum = tuple(sorted(sum(c[j] for c in coords) for j in range(4)))
        invariants.append((len(coords), colsum))
    # group by invariant
    groups = collections.defaultdict(list)
    for i, inv in enumerate(invariants):
        groups[inv].append(i)
    print(f"Invariant groups: {len(groups)}; largest: {max(len(v) for v in groups.values())}")

    # within each invariant group, do exact CYTools equivalence
    from cytools import Polytope
    classes = []
    for inv, idxs in groups.items():
        if len(idxs) == 1:
            classes.append([idxs[0]])
            continue
        polys = [(i, Polytope(polies[i])) for i in idxs]
        assigned = set()
        for i, Pi in polys:
            if i in assigned:
                continue
            cls = [i]
            assigned.add(i)
            for j, Pj in polys:
                if j in assigned:
                    continue
                try:
                    if Pi.is_linearly_equivalent(Pj):
                        cls.append(j)
                        assigned.add(j)
                except Exception as e:
                    print(f"  equiv check {i}~{j} error: {e}", flush=True)
            classes.append(cls)
    print(f"\nTRUE equivalence classes: {len(classes)}")
    for k, cls in enumerate(sorted(classes, key=len, reverse=True)):
        sizes = [len(polies[i]) for i in cls]
        print(f"  class {k}: {len(cls)} instances, vertex counts {sorted(sizes)}: idx {cls[:8]}{'...' if len(cls)>8 else ''}", flush=True)

    with open("true_equivalence_classes.json", "w") as f:
        json.dump([sorted(c) for c in classes], f, indent=2)
    print("Saved data/true_equivalence_classes.json")

if __name__ == "__main__":
    main()
