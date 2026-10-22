#!/usr/bin/env python3
"""
O58 script 58 — U: residual U(1) div0/div8 charge structure.
Q0+q8 has only 8 nonzero positions. Deep dive:
  1. Full charge vectors q0, q8 — verify cancellation pattern
  2. The 8 residual U(1) charges — are they K_Chain γ_n related?
  3. div7 U(1)#7 = -32 (div0), +31 (div8) — 32+31 = 63 = ? 
"""
import os, json, numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def main():
    os.chdir(DATA)
    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    tri = P.triangulate(backend="qhull")
    cy = tri.get_cy()
    glsm = cy.glsm_charge_matrix()

    q0 = glsm[:, 0].astype(int)
    q8 = glsm[:, 8].astype(int)
    q7 = glsm[:, 7].astype(int)
    print("=== U: div0/div8/div7 GLSM charge structure ===\n")
    print(f"q0 (div0): sum={q0.sum()}, nz={np.count_nonzero(q0)}")
    print(f"q8 (div8): sum={q8.sum()}, nz={np.count_nonzero(q8)}")
    print(f"q7 (div7): sum={q7.sum()}, nz={np.count_nonzero(q7)}")
    print()

    residual = [i for i in range(32) if q0[i] + q8[i] != 0]
    cancelled = [i for i in range(32) if q0[i] + q8[i] == 0]
    print(f"residual U(1) positions: {residual} ({len(residual)})")
    print(f"cancelled U(1) positions: {cancelled} ({len(cancelled)})")
    print()

    print("=== residual charges detail ===")
    print(f"{'U(1)':>4} {'q0':>5} {'q8':>5} {'q0+q8':>6} {'q7':>5}")
    for i in residual:
        print(f"{i:>4} {q0[i]:>5} {q8[i]:>5} {q0[i]+q8[i]:>6} {q7[i]:>5}")
    print()

    print("=== cancelled positions: q8 = -q0 exact ===")
    ok = all(q0[i] + q8[i] == 0 for i in cancelled)
    print(f"exact cancellation in {len(cancelled)} positions: {ok}")
    print()

    # what are the cancelled positions' charge magnitudes?
    mags = sorted(set(abs(q0[i]) for i in cancelled))
    print(f"cancelled charge magnitudes: {mags}")
    print()

    # γ_n comparison
    print("=== K_Chain γ_n comparison ===")
    import math
    g = {n: 4*math.sin(n*math.pi/88)**2 for n in range(1, 45)}
    print("residual U(1) positions → γ_n?")
    for i in residual:
        # n = i+1 or 44-i
        n1, n2 = i+1, 44-(i+1)
        print(f"  U(1){i}: γ_{n1}={g[n1]:.4f}, γ_{n2}={g[n2]:.4f}")
    print()

    # sum of residual q8
    print(f"Σ q8 over residual = {sum(q8[i] for i in residual)}")
    print(f"Σ q0 over residual = {sum(q0[i] for i in residual)}")
    print(f"Σ (q0+q8) over residual = {sum(q0[i]+q8[i] for i in residual)}")
    print()

    # q7 special: U(1)#7 charges on div0, div8
    print("=== U(1)#7 (residual position 7) ===")
    print(f"q7[div0] = {q7[0]}, q7[div8] = {q7[8]}")
    print(f"q7[0] + q7[8] = {q7[0]+q7[8]}")
    print(f"-q7[0] = {-q7[0]}, q7[8] = {q7[8]}, diff = {q7[8] - (-q7[0])}")
    print()
    print("=== 63? ===")
    print(f"q7[0] + q7[8] = {q7[0]+q7[8]} (32+31=63)")
    print(f"63 = 44+19? 63 = 7×9? 63 = 3×21 = 3F₈?")
    print()

    # check: q0 vs q8 mirror relationship globally
    print("=== q0 vs q8: is q8 ≈ -q0 + shift? ===")
    diff = q8 + q0
    print(f"q8 + q0 = {diff.tolist()}")
    print(f"nonzero positions: {[i for i,v in enumerate(diff) if v != 0]}")

if __name__ == "__main__":
    main()
