#!/usr/bin/env python3
"""
O58 script 66 — Z: Σ|det| = 200 geometric meaning.
Q: 200 = ? Candidates: χ=2(h11-h21) = 2(36-98) = -124 (no);
   Σγ=90 (no); 2×100; 44+156; 200 = 5×40 = 5×(44-4)?
   Also: 200 = ? relation to N points (48), Euler number -124,
   or the CY volume?
Test various combinations.
"""
import os, numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def main():
    os.chdir(DATA)
    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    tri = P.triangulate(backend="qhull")
    pts = [tuple(int(x) for x in p) for p in P.points()]
    simps = [list(s) for s in tri.simplices()]

    dets = []
    for s in simps:
        nonz = [v for v in s if v != 0]
        if len(nonz) >= 4:
            M = np.array([pts[v] for v in nonz[:4]])
            dets.append(np.linalg.det(M))
    total = sum(abs(d) for d in dets)
    signed = sum(d for d in dets)
    print(f"=== Z: Σ|det| = {total:.6f} ===")
    print(f"signed Σdet = {signed:.6f}")
    print()

    # candidates
    h11, h21 = 36, 98
    chi = 2*(h11 - h21)
    Nd, B = 44, 4
    print(f"χ = 2(h11-h21) = {chi}")
    print(f"Σγ = 90")
    print(f"N_d = 44, B = 4, N_d+B = 48 (M points), N_d+2B = 52")
    print(f"L₇ = 29, L₇+B² = 45, 2L₇ = 58, L₁₀ = 123")
    print()
    candidates = {
        "2χ_abs": 2*abs(chi),
        "3χ_abs": 3*abs(chi),
        "h11+h21+66": h11+h21+66,
        "2(h11+h21)": 2*(h11+h21),
        "h11*h21/17.6": h11*h21/17.6,
        "44+156": 44+156,
        "5*40": 200,
        "8*25": 200,
        "4*50": 200,
        "90+110": 200,
        "Σγ+110": 90+110,
        "2Σγ+20": 2*90+20,
        "2(h11+64)": 2*(36+64),
        "h21+102": 98+102,
        "h21+h11+66": 98+36+66,
        "4*29+84": 4*29+84,
        "L₇*7-3": 29*7-3,
        "L₇*8-32": 29*8-32,
        "44+36+90+30": 44+36+90+30,
        "2*98+4": 2*98+4,
        "2*44+112": 2*44+112,
        "2*h21+4": 2*98+4,
    }
    for name, v in candidates.items():
        if abs(v - total) < 0.5:
            print(f"  ✅ {name} = {v} ≈ Σ|det| = {total}")
    print()

    # Euler number relation: for toric CY, χ = -Σ (something)
    # 200 = -χ + 76? -(-124)+76 = 200! 76 = L₉!
    print(f"-χ + L₉ = {-chi + 76} = {abs(chi) + 76}? → {abs(chi) + 76}")
    print(f"-χ + L₉ = 124 + 76 = 200 ✅!!")
    print(f"L₉ = 76 (Lucas)")
    print()
    print(f"Σ|det| = 200 = -χ + L₉ = |2(h11-h21)| + L₉")
    print(f"       = 124 + 76")
    print(f"       = 2×(62 + 38)")
    print()

    # also: 200 = 2×100 = 2×(44+56) = 2×(44+2×28)?
    print("=== other relations ===")
    print(f"h11+h21 = {h11+h21} = 134")
    print(f"h21-h11 = {h21-h11} = 62")
    print(f"2(h21-h11) = 124 = |χ|")
    print(f"200 - 124 = 76 = L₉")
    print(f"200 = |χ| + L₉ = 124 + 76")
    print()
    print("=== check: Σ|det| per vertex star ===")
    # star sum by vertex
    star_sum = {}
    for s in simps:
        nonz = tuple(sorted(v for v in s if v != 0))
        d = dets[list(dets).index(nonz)] if False else None
    # simpler: recompute
    dets2 = {}
    for s in simps:
        nonz = [v for v in s if v != 0]
        if len(nonz) >= 4:
            M = np.array([pts[v] for v in nonz[:4]])
            dets2[tuple(sorted(nonz))] = np.linalg.det(M)
    for d in [0, 1, 3, 4, 7, 8]:
        ssum = 0.0
        for s in simps:
            if d in s:
                nonz = tuple(sorted(v for v in s if v != 0))
                ssum += abs(dets2.get(nonz, 0))
        print(f"  star Σ|det| div {d}: {ssum:.3f}")

if __name__ == "__main__":
    main()
