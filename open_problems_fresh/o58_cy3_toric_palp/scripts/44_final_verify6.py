#!/usr/bin/env python3
"""
O58 script 44 — FINAL VERIFIER for explorations G/H/I.
"""
import os, json, numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
results = []

def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

def main():
    print("=== O58 EXPLORATIONS G/H/I FINAL VERIFIER ===\n")

    # G: core divisor identity
    g = json.load(open(os.path.join(DATA, "core_divisor_identity.json")))
    d8 = next(d for d in g["core"] if d["div"] == 8)
    d0 = next(d for d in g["core"] if d["div"] == 0)
    check("G: div8 glsm_sum = +733", d8["glsm_sum"] == 733, f"({d8['glsm_sum']})")
    check("G: div0 glsm_sum = -742", d0["glsm_sum"] == -742, f"({d0['glsm_sum']})")
    check("G: div8 K = -232", d8["K"] == -232)
    check("G: div8 has 32 nonzero charges", len(d8["nz_charges"]) == 32)
    check("G: diag sum = -380", g["diag_sum"] == -380, f"({g['diag_sum']})")

    # H: co-simplex necessity
    # (verified interactively: 350/350 K≠0 triples in common simplex)
    # recompute quickly
    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    tri = P.triangulate(backend="qhull")
    simps = [set(s) for s in tri.simplices()]
    K = np.load(os.path.join(DATA, "kappa_36d_true.npy"))
    nnz = [(i,j,k) for i in range(36) for j in range(36) for k in range(36) if K[i,j,k]!=0]
    common = sum(1 for (i,j,k) in nnz if any(i in cs and j in cs and k in cs for cs in simps))
    check("H: 350/350 K≠0 triples co-simplex", common == len(nnz) == 350, f"({common}/{len(nnz)})")
    check("H: 144 maximal simplices", len(simps) == 144, f"({len(simps)})")

    # I: h21 monotonic law
    dist = json.load(open(os.path.join(DATA, "h21_family_vertex_dist.json")))
    # keys are strings
    def mverts(fam):
        return max(int(k) for k in fam)
    def over20(fam):
        return sum(v for k, v in fam.items() if int(k) >= 20)
    check("I: h21=98 max_vert=19", mverts(dist["98"]) == 19)
    check("I: h21=98 20+=0", over20(dist["98"]) == 0)
    check("I: h21=96 max_vert=19", mverts(dist["96"]) == 19)
    check("I: h21=90 has some 20+", over20(dist["90"]) == 7, "(7)")
    check("I: h21=102 max_vert=19", mverts(dist["102"]) == 19)

    npass = sum(results)
    print(f"\n=== {npass}/{len(results)} PASS ===")
    import sys; sys.exit(0 if npass == len(results) else 1)

if __name__ == "__main__":
    main()
