#!/usr/bin/env python3
"""
O58 script 04 — GL(4,Z) normal form fingerprints for all candidate
(36,98) polytopes:
  A) canonical 6-vertex (polytope_36_98.txt / all_36_98.poly #0)  M:48 6
  B) HF instance 0 (cy36_98_hf.poly)  20 vertices, 132 points
  C) HF instance 1                      20 vertices, 131 points
Plus: check which all_36_98.poly instances share the canonical normal form.
Purpose: give (36,98) a rigorous "ID" = normal-form fingerprint, and test
whether the HF instances are the same polytope (affine equivalent) as the
canonical one.
"""
import subprocess, os, re, json, collections

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def run_palp(args, inp, timeout=120):
    r = subprocess.run(["poly.x"] + args, input=inp.encode(),
                       capture_output=True, timeout=timeout)
    return r.stdout.decode(errors="replace"), r.stderr.decode(errors="replace")

def poly_text(coords):
    lines = [f"{len(coords)} 4"] + [" ".join(str(x) for x in c) for c in coords]
    return "\n".join(lines) + "\n"

def normal_form(coords):
    """GL(4,Z) normal form via poly.x -N.
    Output: '4 6  Normal form of vertices of P    perm=...' then 4×6 int matrix.
    Returns tuple of the 4 matrix rows."""
    out, err = run_palp(["-N"], poly_text(coords))
    lines = out.splitlines()
    rows = []
    for i, l in enumerate(lines):
        if "Normal form" in l:
            # next 4 non-empty lines are the matrix rows
            j = i + 1
            while j < len(lines) and len(rows) < 4:
                s = lines[j].strip()
                if s:
                    parts = s.split()
                    if len(parts) >= 4:
                        try:
                            rows.append(tuple(int(x) for x in parts))
                        except ValueError:
                            pass
                    else:
                        break
                j += 1
            break
    return tuple(rows)

def full_hodge(coords):
    out, err = run_palp(["-g"], poly_text(coords))
    m = re.search(r"M:(\d+)\s+(\d+)\s+N:(\d+)\s+(\d+)\s+H:(\d+),(\d+)\s*\[(\d+)\]", out)
    return (int(m.group(5)), int(m.group(6))) if m else None

def parse_poly_file(path):
    """Parse PALP .poly blocks (header 'n d' + n coordinate lines)."""
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

    # A) canonical 6-vertex
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    # B) HF instance 0 — cy36_98_hf.poly is a bare vertex list (no header)
    hf0 = []
    for l in open("cy36_98_hf.poly"):
        parts = l.split()
        if len(parts) == 4:
            try:
                hf0.append([int(x) for x in parts])
            except ValueError:
                pass
    # C) HF instance 1 — hardcode from the parquet read
    hf1 = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,-1,1,0],[0,0,0,1],[-2,0,0,-1],[-2,0,-1,-1],
           [-3,0,-2,0],[-3,0,-2,-1],[-2,-1,1,-1],[-2,-2,1,0],[-2,-2,1,-1],[-5,0,-3,-1],
           [-3,-3,1,-1],[-5,-1,-1,-2],[-5,-3,1,-2],[-7,-2,-4,0],[-9,-1,-5,-2],[-8,-6,1,-2],
           [-19,-6,-10,-2]]

    print("=" * 70)
    print("(36,98) POLYTOPE FINGERPRINTS")
    print("=" * 70)
    results = {}
    for name, coords in [("A canonical 6v", canon), ("B HF inst0 20v", hf0), ("C HF inst1 20v", hf1)]:
        h = full_hodge(coords)
        nf = normal_form(coords)
        print(f"\n--- {name} ---")
        print(f"  vertices: {len(coords)}, Hodge: {h}")
        print(f"  normal form rows: {len(nf)}")
        results[name] = {"hodge": list(h) if h else None, "nf": [list(r) for r in nf]}

    # equivalence tests
    print("\n=== Affine equivalence (normal form match) ===")
    for a, b in [("A canonical 6v", "B HF inst0 20v"),
                 ("A canonical 6v", "C HF inst1 20v"),
                 ("B HF inst0 20v", "C HF inst1 20v")]:
        same = results[a]["nf"] == results[b]["nf"]
        print(f"  {a} == {b}: {'✅ SAME polytope' if same else '❌ different normal form'}")
        results[f"equiv {a} vs {b}"] = same

    # also compare against the old polytope_36_98.txt
    print("\n=== Canonical vs polytope_36_98.txt ===")
    # (identical vertex list, just re-verified via PALP earlier)

    # normal-form distribution over all_36_98.poly (first 30)
    print("\n=== Normal-form classes in all_36_98.poly (first 30 instances) ===")
    polies = parse_poly_file("all_36_98.poly")
    classes = collections.Counter()
    for i, coords in enumerate(polies[:30]):
        nf = normal_form(coords)
        classes[nf] += 1
    print(f"  {len(classes)} distinct normal forms among first 30")
    canon_nf = results["A canonical 6v"]["nf"]
    canon_count = sum(1 for nf in classes for _ in range(classes[nf])
                      if list(nf) == canon_nf) if False else None
    # count how many match canonical
    n_match = 0
    for i, coords in enumerate(polies[:30]):
        nf = normal_form(coords)
        if list(nf) == canon_nf:
            n_match += 1
    print(f"  {n_match}/30 match canonical normal form")

    with open("polytope_fingerprints.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved data/polytope_fingerprints.json")

if __name__ == "__main__":
    main()
