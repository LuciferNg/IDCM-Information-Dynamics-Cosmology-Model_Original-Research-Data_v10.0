#!/usr/bin/env python3
"""
O58 script 07 — N-lattice (dual polytope) Z₂ structure of the canonical
(36,98) polytope. The dual has 85 points / 7 vertices.
Test: does the N-polytope exhibit the K_Chain Z₂ mirror (n ↔ 44−n)
structure? O57 found Z₂ preserves parity in beat space; here we check
the geometry side: point set symmetry under sign flips / coordinate
permutations of the N-lattice.
"""
import subprocess, os, re, json, collections, itertools

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def run_palp(args, inp, timeout=120):
    r = subprocess.run(["poly.x"] + args, input=inp.encode(),
                       capture_output=True, timeout=timeout)
    return r.stdout.decode(errors="replace"), r.stderr.decode(errors="replace")

CANON = """6 4
1 0 0 0
-15 -10 -4 0
0 0 1 0
1 2 0 0
-47 -30 -12 -4
0 0 0 1
"""

def parse_dual_points(out):
    """Parse the '85 4  Points of P-dual' block."""
    pts = []
    in_dual = False
    for l in out.splitlines():
        s = l.strip()
        if "Points of P-dual" in s:
            in_dual = True
            continue
        if in_dual:
            parts = s.split()
            if len(parts) == 4:
                try:
                    pts.append(tuple(int(x) for x in parts))
                except ValueError:
                    pass
            elif len(parts) == 2 and parts[0].isdigit():
                # header line '85 4' — skip
                pass
            else:
                if pts:
                    break
    return pts

def main():
    os.chdir(DATA)
    out, err = run_palp(["-d"], CANON)
    pts = parse_dual_points(out)
    print(f"N-lattice points: {len(pts)}")

    # unique points (should all be unique)
    uniq = set(pts)
    print(f"unique: {len(uniq)} (expect 85)")

    # coordinate distributions
    for j in range(4):
        vals = collections.Counter(p[j] for p in uniq)
        print(f"  coord {j}: min={min(vals)}, max={max(vals)}, distinct={len(vals)}")

    # origin? interior?
    origin = (0,0,0,0) in uniq
    print(f"contains origin: {origin}")

    # Z₂ candidate: coordinate sign flip symmetry (p -> -p) on some subset
    # Check how many points pair with their negation
    neg_pairs = 0
    for p in uniq:
        if tuple(-x for x in p) in uniq:
            neg_pairs += 1
    print(f"points whose negation is also present: {neg_pairs} (pairs: {neg_pairs//2})")

    # reflection symmetries: coordinate flip p_j -> -p_j (on the whole set)
    for j in range(4):
        flipped = {tuple(-x if i == j else x for i, x in enumerate(p)) for p in uniq}
        same = flipped == uniq
        print(f"  reflection x{j} -> -x{j} is symmetry: {same}")

    # sort by norm to see radial structure
    norms = sorted((sum(x*x for x in p), p) for p in uniq)
    print("\nSmallest 8 (by norm):")
    for n2, p in norms[:8]:
        print(f"  ||p||²={n2:3d}  {p}")
    print("Largest 8:")
    for n2, p in norms[-8:]:
        print(f"  ||p||²={n2:3d}  {p}")

    results = dict(n_points=len(pts), unique=len(uniq), contains_origin=origin,
                   neg_pairs=neg_pairs, reflections=[f"x{j}" for j in range(4)
                   if {tuple(-x if i == j else x for i, x in enumerate(p)) for p in uniq} == uniq])
    with open("n_lattice_structure.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved data/n_lattice_structure.json")

if __name__ == "__main__":
    main()
