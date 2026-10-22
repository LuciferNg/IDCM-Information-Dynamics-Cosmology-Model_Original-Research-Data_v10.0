#!/usr/bin/env python3
"""
O58 script 52 — FINAL VERIFIER for explorations M/N/O.
"""
import os, json, numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
results = []

def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

def lucas(n):
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def main():
    print("=== O58 EXPLORATIONS M/N/O FINAL VERIFIER ===\n")

    # N: Lucas decomposition (pure math, no CYTools needed)
    check("N: L₄ = 7", lucas(4) == 7)
    check("N: L₇ = 29", lucas(7) == 29)
    check("N: L₄+L₇ = 36 = h11", lucas(4) + lucas(7) == 36)
    check("N: L₁₁ = L₇L₄−L₃", lucas(11) == lucas(7)*lucas(4) - lucas(3), f"({lucas(11)})")
    # unique non-trivial decomposition: only L4+L7 and L6+L6
    decomp = [(a, b) for a in range(12) for b in range(a, 12) if lucas(a)+lucas(b) == 36]
    check("N: 36 = L₄+L₇ only non-trivial", (4, 7) in decomp and len(decomp) == 2, f"({decomp})")

    # M: redundancy — verify redundant divisors = [2,3,6,7] and 4 = B
    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    tri = P.triangulate(backend="qhull")
    cy = tri.get_cy()
    basis = [int(b) - 1 for b in cy.divisor_basis()]
    redundant = sorted([d for d in range(36) if d not in basis])
    check("M: 4 redundant divisors", len(redundant) == 4, f"({redundant})")
    check("M: redundant includes 7", 7 in redundant)
    check("M: redundant includes 2,3,6", all(d in redundant for d in [2,3,6]))

    # O: div0 K values — canonical only 45
    d0 = json.load(open(os.path.join(DATA, "divisor0_universality.json")))
    k000_by_idx = {r["idx"]: r["k000"] for r in d0}
    check("O: canonical K000 = -360", k000_by_idx[0] == -360)
    check("O: canonical -K/8 = 45", -k000_by_idx[0]//8 == 45)
    # shallow (with 1100) vs deep (without)
    p1100 = json.load(open(os.path.join(DATA, "point_1100_universality.json")))
    has = {r["idx"] for r in p1100 if r.get("has")}
    shallow = [-k000_by_idx[i]/8 for i in has if i in k000_by_idx]
    deep = [-k000_by_idx[i]/8 for i in k000_by_idx if i not in has]
    check("O: shallow -K/8 ∈ [42,45]", all(42 <= v <= 45 for v in shallow), f"({sorted(shallow)})")
    check("O: deep -K/8 ∈ [73,80]", all(73 <= v <= 80 for v in deep), f"({sorted(deep)})")
    check("O: groups separated", max(shallow) < min(deep))

    npass = sum(results)
    print(f"\n=== {npass}/{len(results)} PASS ===")
    import sys; sys.exit(0 if npass == len(results) else 1)

if __name__ == "__main__":
    main()
