#!/usr/bin/env python3
"""
O58 script 45 — J: residual 8 U(1) positions ↔ K_Chain.
The 8 residual U(1) positions where q0+q8 ≠ 0: [0,3,7,25,28,29,30,31].
Q: do these map to K_Chain γ_n modes / special structure?
K_Chain: γ_n = 4sin²(nπ/88), n=1..44; special modes: 7, 20, 44 etc.
"""
import numpy as np, math

def main():
    residual = [0, 3, 7, 25, 28, 29, 30, 31]
    print("=== J: residual U(1) positions [0,3,7,25,28,29,30,31] ===")
    print(f"count: {len(residual)} = 8 = B×2 = 2³")
    print()
    # positions analysis
    print("position patterns:")
    print(f"  [0, 3, 7] = first block (0-11)")
    print(f"  [25, 28, 29, 30, 31] = last block (24-35)")
    print()
    # gaps
    gaps = np.diff(residual)
    print(f"gaps: {gaps} (3,4,18,3,1,1,1)")
    print(f"sum of gaps: {sum(gaps)}")
    print()
    # K_Chain mapping candidates
    print("K_Chain candidates:")
    print("  0 → n=0 (DC/ground)")
    print("  3 → n=3? 7 → n=7 (L₇!)")
    print("  25,28,29,30,31 → n=25..31 (mirror region 44-13..44-19)")
    print()
    # mirror: 44 - position
    print("mirror pairs (44-n):")
    for p in residual:
        print(f"  {p} → 44-{p} = {44-p}", end="")
        # is 44-p in residual?
        if (44-p) in residual:
            print(" ← PAIRED!")
        else:
            print()
    print()
    # gamma values at these positions (mod 44)
    print("γ_n for n in residual (if n = position):")
    for p in residual:
        if 1 <= p <= 44:
            g = 4*math.sin(p*math.pi/88)**2
            print(f"  n={p}: γ_{p} = {g:.4f}")
    print()
    # special: 7 → L₇=29, 25 = 44-19?, 28 = 44-16, 29,30,31
    print("special relations:")
    print("  7 = L₄? no. 7 = mode of m_ν₃ (γ₆v)²? γ₇ = n/p mechanism!")
    print("  25 = 44-19 = 44-F₈? 28 = 44-16 = 44-B²? 29 = L₇!")
    print("  30 = 44-14, 31 = 44-13")
    print()
    # 8 positions: 3 in low block, 5 in high block
    # 3 = B-1? 5 = B+1?
    print("  3 = B-1 = 4-1 ✓, 5 count in high block = B+1 = 5 ✓")
    print("  low block (0-11): {0,3,7} — 7 = the L₇ mode!")
    print("  high block (24-35): {25,28,29,30,31} — 29 = L₇!")
    print()
    print("=== KEY: 7 and 29 both appear! ===")
    print("  position 7 in residual AND L₇ = 29 in high block!")
    print("  7 ↔ 29 mirror pair (44-7=37, 44-29=15... no direct)")
    print("  but 7+29 = 36 = h11! ✓✓✓")
    print("  3+25 = 28, 0+31 = 31, 28+30 = 58...")

if __name__ == "__main__":
    main()
