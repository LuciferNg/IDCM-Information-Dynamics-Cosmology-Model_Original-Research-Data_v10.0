#!/usr/bin/env python3
"""
O58 script 05 — Family structure of all_36_98.poly (100 instances):
  - vertex-count distribution
  - normal-form classes (via CYTools is_linearly_equivalent, pairwise for
    the 6/7-vertex instances; count-based for larger)
  - which instance matches the canonical 6-vertex (polytope_36_98.txt)
  - point-count distribution (M-side)
Result: the "family ID" structure of (36,98) — how many distinct polytopes
exist in the KS-derived list, and which is the canonical one.
"""
import subprocess, os, re, json, collections

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

def run_palp(args, inp, timeout=60):
    r = subprocess.run(["poly.x"] + args, input=inp.encode(),
                       capture_output=True, timeout=timeout)
    return r.stdout.decode(errors="replace")

def main():
    os.chdir(DATA)
    polies = parse_poly_file("all_36_98.poly")
    print(f"Parsed {len(polies)} instances")
    vdist = collections.Counter(len(p) for p in polies)
    print("Vertex count distribution:", dict(sorted(vdist.items())))

    # point counts via poly.x -g (fast, batch-able) — do the first 40
    point_counts = []
    for i, coords in enumerate(polies[:40]):
        out = run_palp(["-g"], f"{len(coords)} 4\n" + "\n".join(" ".join(map(str,c)) for c in coords) + "\n")
        m = re.search(r"M:(\d+)\s+\d+\s+N:(\d+)\s+\d+\s+H:", out)
        if m:
            point_counts.append((i, len(coords), int(m.group(1)), int(m.group(2))))
    print("\nPoint counts (idx, n_vert, M_pts, N_pts) first 40:")
    for t in point_counts[:15]:
        print("  ", t)

    # canonical 6-vertex: which instances have identical vertex SET (up to perm)?
    canon_set = frozenset(tuple(c) for c in polies[0])
    # canonical is instance 0? actually polytope_36_98.txt = first entry
    matches = [i for i, coords in enumerate(polies) if frozenset(tuple(c) for c in coords) == canon_set]
    print(f"\nInstances with identical vertex set to #0: {matches}")

    # normal-form equivalence classes via CYTools for all 100 (is_linearly_equivalent is
    # expensive pairwise — use PALP normal form matrix as hash instead)
    # PALP -N output gives 4×n matrix; for same n_vert, same matrix = same class
    nf_classes = collections.Counter()
    for i, coords in enumerate(polies):
        out = run_palp(["-N"], f"{len(coords)} 4\n" + "\n".join(" ".join(map(str,c)) for c in coords) + "\n")
        rows = []
        seen_nf = False
        for l in out.splitlines():
            s = l.strip()
            if "Normal form" in s:
                seen_nf = True
                continue
            if seen_nf:
                parts = s.split()
                if len(parts) >= len(coords):
                    try:
                        rows.append(tuple(int(x) for x in parts))
                    except ValueError:
                        pass
                elif rows:
                    break
                if len(rows) == 4:
                    break
        nf_classes[tuple(rows)] += 1
    print(f"\nDistinct normal-form classes (by PALP matrix): {len(nf_classes)}")
    for k, v in nf_classes.most_common(10):
        print(f"  {v} instances, nf rows={len(k)} first row={k[0][:6] if k else None}")

    with open("family_structure.json", "w") as f:
        json.dump(dict(vdist=dict(vdist),
                       nf_classes=len(nf_classes),
                       point_counts=point_counts[:15],
                       canonical_matches=matches), f, indent=2)
    print("\nSaved data/family_structure.json")

if __name__ == "__main__":
    main()
