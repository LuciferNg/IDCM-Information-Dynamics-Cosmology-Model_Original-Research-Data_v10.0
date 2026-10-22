#!/usr/bin/env python3
"""
O58 script 15 — SYSTEMATIC Lucas/K_Chain structure in TRUE κ diagonal.
Hypotheses:
  H1: K[7,7,7] = -232 = -8×L₇  (L₇=29)
  H2: K[35,35,35] = -360 = -8×(N_d+1) = -8×45
  H3: K[0,0,35] = -44 = -N_d
  H4: all large |K[i,i,i]| and K[i,i,j] factor as 8×{L_n or N_d-related}
Method: list ALL |K| ≥ 20 values, factor them, count how many are
8×Lucas or 8×integer-with-K_Chain-meaning.
Control: random integers in same range — how many factor as 8×Lucas?
"""
import os, json, numpy as np, math, random
from itertools import permutations

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
PHI = (1 + math.sqrt(5)) / 2

def lucas(n):
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def main():
    os.chdir(DATA)
    from cytools import Polytope, config
    config.enable_experimental_features()
    canon = [[1,0,0,0],[-15,-10,-4,0],[0,0,1,0],[1,2,0,0],[-47,-30,-12,-4],[0,0,0,1]]
    P = Polytope(canon)
    tri = P.triangulate(backend="qhull")
    cy = tri.get_cy()
    inter = cy.intersection_numbers()
    K = np.zeros((36, 36, 36))
    for (i, j, k), v in inter.items():
        for a, b, c in permutations((i-1, j-1, k-1)):
            K[a, b, c] = v

    L = {lucas(n): n for n in range(0, 15)}  # L_0..L_14

    # collect all K[i,i,j] with |v| >= 20
    big = []
    for i in range(36):
        for j in range(36):
            v = int(K[i,i,j])
            if abs(v) >= 20:
                big.append((i, j, v))

    print(f"=== |K[i,i,j]| >= 20: {len(big)} entries ===")
    for i, j, v in sorted(big, key=lambda x: -abs(x[2])):
        av = abs(v)
        # try factor: v = 8×L? or 8×int?
        q8 = av / 8
        q8int = q8 == int(q8)
        lucas_hit = q8int and int(q8) in L
        lucas_n = L[int(q8)] if lucas_hit else None
        print(f"  K[{i:2d},{i:2d},{j:2d}] = {v:6d}  |v|/8={q8:7.2f} {'L'+str(lucas_n) if lucas_hit else ''}")

    # statistics
    n_big = len(big)
    n_8mult = sum(1 for _, _, v in big if abs(v) % 8 == 0)
    n_lucas8 = sum(1 for _, _, v in big if abs(v) % 8 == 0 and (abs(v)//8) in L)
    print(f"\n|v|≥20: {n_big}; divisible by 8: {n_8mult}; 8×Lucas: {n_lucas8}")

    # control: random integers uniform in [-400, 400], count 8×Lucas
    rng = random.Random(7)
    n_ctl = 10000
    ctl = [rng.randint(-400, 400) for _ in range(n_ctl)]
    ctl_8 = sum(1 for v in ctl if abs(v) % 8 == 0)
    ctl_lucas = sum(1 for v in ctl if abs(v) % 8 == 0 and (abs(v)//8) in L)
    print(f"Control ({n_ctl} uniform [-400,400]): divisible by 8: {ctl_8} ({ctl_8/n_ctl*100:.1f}%), "
          f"8×Lucas: {ctl_lucas} ({ctl_lucas/n_ctl*100:.1f}%)")
    # expected 8×Lucas in [1..50]: L values ≤ 50: 2,1,3,4,7,11,18,29,47 → 9 values
    exp_frac = (9/400)  # 9 lucky quotients out of 400 possible
    print(f"Expected random 8×Lucas fraction: {exp_frac*100:.2f}%")

    results = dict(n_big=n_big, n_8mult=n_8mult, n_lucas8=n_lucas8,
                   ctl_8=ctl_8, ctl_lucas=ctl_lucas,
                   entries=[[i,j,v] for i,j,v in big])
    with open("lucas_kappa_structure.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print("\nSaved data/lucas_kappa_structure.json")

if __name__ == "__main__":
    main()
