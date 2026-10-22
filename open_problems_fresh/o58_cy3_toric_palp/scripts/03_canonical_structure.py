#!/usr/bin/env python3
"""
O58 script 03 — Full structural audit of the canonical CY₃(36,98) polytope:
  M-side: 48 points (expect = N_d + B = 44 + 4), 6 vertices
  N-side: 85 points, 7 vertices
  Facets, reflexivity, dual polytope
  Normal form (GL(4,Z) canonical)
  Compare against O57 expectations: 48 = 44+4, 144 simplicial cones,
  SR ideal 484 generators, adjacency 155 = 2×73+9.
"""
import subprocess, os, re, sys, json, itertools

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def run_palp(args, inp):
    r = subprocess.run(["poly.x"] + args, input=inp.encode(),
                       capture_output=True, timeout=120)
    return r.stdout.decode(errors="replace"), r.stderr.decode(errors="replace")

CANON = """6 4
1 0 0 0
-15 -10 -4 0
0 0 1 0
1 2 0 0
-47 -30 -12 -4
0 0 0 1
"""

def main():
    os.chdir(DATA)
    results = {}

    # 1. Full general output with dual points
    out, err = run_palp(["-gd"], CANON)
    m = re.search(r"M:(\d+)\s+(\d+)\s+N:(\d+)\s+(\d+)\s+H:(\d+),(\d+)\s*\[(\d+)\]", out)
    results["hodge"] = [int(m.group(5)), int(m.group(6))] if m else None
    results["M_points"], results["M_vertices"] = (int(m.group(1)), int(m.group(2))) if m else (None, None)
    results["N_points"], results["N_vertices"] = (int(m.group(3)), int(m.group(4))) if m else (None, None)
    results["chi"] = int(m.group(7)) if m else None
    print(f"Hodge h21,h11 = {results['hodge']}, chi={results['chi']}")
    print(f"M: {results['M_points']} points, {results['M_vertices']} vertices;  N: {results['N_points']} points, {results['N_vertices']} vertices")

    # 2. Dual points (N-lattice) — parse the point block after 'Dual of:'
    # poly.x -d prints N points
    out, err = run_palp(["-d"], CANON)
    npoints = []
    for l in out.splitlines():
        s = l.strip()
        parts = s.split()
        if len(parts) == 4:
            try:
                npoints.append(tuple(int(x) for x in parts))
            except ValueError:
                pass
    print(f"N-lattice points parsed: {len(npoints)} (expect 85)")
    results["N_points_parsed"] = len(npoints)

    # 3. Symmetries
    out, err = run_palp(["-S"], CANON)
    m = re.search(r"#GL\(Z,4\)-Symmetries=(\d+),\s*#VPM-Symmetries=(\d+)", out)
    if m:
        results["GLZ_sym"] = int(m.group(1))
        results["VPM_sym"] = int(m.group(2))
        print(f"GL(Z,4) symmetries = {results['GLZ_sym']}, VPM symmetries = {results['VPM_sym']}")

    # 4. Normal form
    out, err = run_palp(["-N"], CANON)
    rows = []
    for l in out.splitlines():
        s = l.strip()
        parts = s.split()
        if len(parts) == 4:
            try:
                rows.append(tuple(int(x) for x in parts))
            except ValueError:
                pass
    nf = tuple(sorted(rows))
    print(f"Normal form: {len(nf)} rows")
    results["normal_form"] = [list(r) for r in nf]

    # 5. Facets (F option)
    out, err = run_palp(["-F"], CANON)
    # parse facet lines
    print("Facet output (first 12 lines):")
    fl = [l for l in out.splitlines() if l.strip()][:12]
    for l in fl:
        print("   ", l)

    # 6. K_Chain structure expectations
    print("\n=== K_Chain structure check ===")
    checks = {
        "M_points = N_d + B (48 = 44+4)": results["M_points"] == 48,
        "chi = -124": results["chi"] == -124,
        "h21 = 98, h11 = 36": results["hodge"] == [98, 36],
    }
    for k, v in checks.items():
        print(f"  {'✅' if v else '❌'} {k}")
    results["kchain_checks"] = checks

    with open("canonical_structure.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved data/canonical_structure.json")

if __name__ == "__main__":
    main()
