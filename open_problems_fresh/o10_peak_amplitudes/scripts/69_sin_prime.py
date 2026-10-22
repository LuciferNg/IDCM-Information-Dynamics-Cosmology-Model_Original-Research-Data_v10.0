#!/usr/bin/env python3
"""
O10 69: 質數峰 sin 相位 — 質數直接結構
=======================================
sin(πℓ/88): m1: +0.9994, m2: -0.0357, m3: -0.7319, m5: +0.7319, m7: +0.0357

候選: sin(πℓ/88) = cos(π×p/22)?
  p=1: cos(π/22) = 0.9898?
  p=2: cos(2π/22) = 0.9595?
  p=3: cos(3π/22) = 0.9096?
  p=5: cos(5π/22) = 0.7557?
  p=7: cos(7π/22) = 0.5406?
"""
import numpy as np, math

phi = (1 + 5**0.5) / 2
eps = phi**-1/4

print("=" * 72)
print("質數峰 sin 相位 vs 質數")
print("=" * 72)

# 實際 sin
sin_obs = {1: 0.9994, 2: -0.0357, 3: -0.7319, 5: 0.7319, 7: 0.0357}

print("候選: sin(πℓ/88) = ±cos(π×p/22)?")
for p in [1, 2, 3, 5, 7]:
    c = math.cos(math.pi*p/22)
    print(f"  p={p}: cos(π×{p}/22) = {c:+.4f} vs obs {sin_obs[p]:+.4f}")

print()
print("唔匹配 (cos 全部正)")
print()

print("候選: sin(πℓ/88) = sin(π×p/44)?")
for p in [1, 2, 3, 5, 7]:
    s = math.sin(math.pi*p/44)
    print(f"  p={p}: sin(π×{p}/44) = {s:+.4f} vs obs {sin_obs[p]:+.4f}")

print()
print("候選: sin(πℓ/88) = sin(π×2p/44)?")
for p in [1, 2, 3, 5, 7]:
    s = math.sin(math.pi*2*p/44)
    print(f"  p={p}: sin(π×{2*p}/44) = {s:+.4f} vs obs {sin_obs[p]:+.4f}")

print()
# sin(πN/44) 用 N_m
print("候選: sin(πℓ/88) = ±sin(πN/44)?")
N = {1: 5, 2: 12, 3: 18, 5: 25, 7: 32}
for m in [1, 2, 3, 5, 7]:
    s = math.sin(math.pi*N[m]/44)
    print(f"  m={m}: sin(π×{N[m]}/44) = {s:+.4f} vs obs {sin_obs[m]:+.4f}")

print()
print("候選: sin(πℓ/88) = ±cos(πN/44)?")
for m in [1, 2, 3, 5, 7]:
    c = math.cos(math.pi*N[m]/44)
    print(f"  m={m}: cos(π×{N[m]}/44) = {c:+.4f} vs obs {sin_obs[m]:+.4f}")

print()
# 直接: ℓ mod 88
print("ℓ mod 88:")
ells = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}
for m in [1, 2, 3, 5, 7]:
    print(f"  m={m}: ℓ mod 88 = {ells[m] % 88}")

print()
print("ℓ mod 88: 45, 87, 23, 65, 1")
print("sin(π×45/88) =", math.sin(math.pi*45/88))
print("sin(π×87/88) =", math.sin(math.pi*87/88))
print("sin(π×23/88) =", math.sin(math.pi*23/88))
print("sin(π×65/88) =", math.sin(math.pi*65/88))
print("sin(π×1/88) =", math.sin(math.pi/88))
