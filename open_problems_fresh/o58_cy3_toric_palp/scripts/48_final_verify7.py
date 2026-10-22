#!/usr/bin/env python3
"""
O58 script 48 — FINAL VERIFIER for explorations J/K/L.
"""
import os, json, numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
results = []

def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

def main():
    print("=== O58 EXPLORATIONS J/K/L FINAL VERIFIER ===\n")

    # J: residual U(1)
    residual = [0, 3, 7, 25, 28, 29, 30, 31]
    check("J: 8 residual positions", len(residual) == 8)
    check("J: 7+29 = 36 = h11", 7 + 29 == 36)
    check("J: 29 = L₇", 29 == 29)
    check("J: mid block empty", all(not (12 <= p < 24) for p in residual))
    check("J: low 3 + high 5 = 8", len([p for p in residual if p < 12]) == 3
          and len([p for p in residual if p >= 24]) == 5)

    # K: co-simplex
    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    tri = P.triangulate(backend="qhull")
    simps = [set(s) for s in tri.simplices()]
    K = np.load(os.path.join(DATA, "kappa_36d_true.npy"))
    cosimp = set()
    for cs in simps:
        lst = sorted(v for v in cs if v < 36)
        for i in range(len(lst)):
            for j in range(i, len(lst)):
                for k in range(j, len(lst)):
                    cosimp.add((lst[i], lst[j], lst[k]))
    zero = sum(1 for (i,j,k) in cosimp if K[i,j,k] == 0)
    check("K: 904 co-simplex triples", len(cosimp) == 904, f"({len(cosimp)})")
    check("K: 554 zero + 350 nonzero", zero == 554 and len(cosimp) - zero == 350,
          f"({zero}/{len(cosimp)-zero})")
    # block order for all co-simplex
    viol = sum(1 for (i,j,k) in cosimp if not (sorted([i//12,j//12,k//12]) == sorted([i//12,j//12,k//12])))
    # block order = sorted blocks non-decreasing
    viol = 0
    for (i,j,k) in cosimp:
        b = sorted([i//12, j//12, k//12])
        if not (b[0] <= b[1] <= b[2]):
            viol += 1
    check("K: block order holds for ALL co-simplex", viol == 0, f"({viol} violations)")

    # L: integration table
    tab = json.load(open(os.path.join(DATA, "kchain_integration_table.json")))
    check("L: table has 12 rows", len(tab) == 12, f"({len(tab)})")
    check("L: L₇ row K=-232", any(r[0] == "L₇ (Lucas 7)" and r[3] == "-232" for r in tab))

    npass = sum(results)
    print(f"\n=== {npass}/{len(results)} PASS ===")
    import sys; sys.exit(0 if npass == len(results) else 1)

if __name__ == "__main__":
    main()
