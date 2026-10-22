#!/usr/bin/env python3
"""
O10 57: N_m 結構 — 質數累積
============================
N_m: 5, 12, 18, 25, 32 (質數峰)
質數: 2, 3, 5, 7, 11, 13

累積: 2, 5, 10, 17, 28, 41
N_m vs 累積?
"""
import numpy as np, math

print("質數累積和:")
s = 0
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
for i, p in enumerate(primes):
    s += p
    print(f"  Σp_{i+1} = {s}")

print()
print("N_m: 5, 12, 18, 25, 32")
print("累積: 2, 5, 10, 17, 28, 41")
print()
print("N₁ = 5 = Σp₂ (2+3)")
print("N₂ = 12 = ? Σp₃ = 10, Σp₄ = 17")
print("N₃ = 18 = Σp₄ + 1 = 17+1?")
print("N₅ = 25 = ?")
print("N₇ = 32 = ?")
print()
print("或者 N_m = m + Σ質數到 m?")
print("  5 = 1+2+2? 唔啱")
print()
print("另一結構: N_m - 4m?")
for m in [1, 2, 3, 5, 7]:
    print(f"  m={m}: N-4m = {5 if m==1 else 12 if m==2 else 18 if m==3 else 25 if m==5 else 32} - {4*m} = {5-4 if m==1 else 12-8 if m==2 else 18-12 if m==3 else 25-20 if m==5 else 32-28}")
print()
print("N-4m: 1, 4, 6, 5, 4")
print()
print("N_m/5: 1, 2.4, 3.6, 5, 6.4")
print("N_m/7: 0.71, 1.71, 2.57, 3.57, 4.57")
print()
print("N_m/7: 0.714, 1.714, 2.571, 3.571, 4.571")
print("分數部分: 0.714, 0.714, 0.571, 0.571, 0.571")
print()
# N_m mod 7?
print("N_m mod 7:", [5 % 7, 12 % 7, 18 % 7, 25 % 7, 32 % 7])
print("= 5, 5, 4, 4, 4")
print()
print("有趣: N₁, N₂ mod 7 = 5; N₃, N₅, N₇ mod 7 = 4")
print()
print("N_m = 7m + c?")
print("  5 = 7×1-2, 12 = 7×2-2, 18 = 7×3-3, 25 = 7×5-10, 32 = 7×7-17")
print()
print("差: -2, -2, -3, -10, -17")
print()
# 斐波那契: N_m vs F_m?
F = [1, 1, 2, 3, 5, 8, 13]
print("N_m vs F_{m+3}?")
for m in [1, 2, 3, 5, 7]:
    print(f"  m={m}: N={5 if m==1 else 12 if m==2 else 18 if m==3 else 25 if m==5 else 32}, F_{m+3}={F[m+2] if m+3<=7 else '?'}")
