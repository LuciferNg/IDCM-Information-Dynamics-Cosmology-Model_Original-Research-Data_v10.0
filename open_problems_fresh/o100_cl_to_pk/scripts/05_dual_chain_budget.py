#!/usr/bin/env python3
"""
O100-B: 88/90 對偶 budget — dual-chain propagator 結構比
=====================================================
尋找 σ_8 度規化嘅結構修正: 世界鏈 (even, Σγ=90) vs 觀察者鏈 (odd, Σγ=88)。

候選結構比:
  ΣG_even/ΣG_odd, Σω_even/Σω_odd, Σγ_even/Σγ_odd, 44-site 鏈 vs 88-site 奇鏈
"""
import numpy as np

k = np.arange(1, 89)
gam = 4*np.sin(np.pi*k/176)**2
om  = 2*np.sin(np.pi*k/176)
G   = 1/(2*om)
odd  = k % 2 == 1
even = k % 2 == 0

print("== 88-site dual chain ==")
print(f"Σγ_odd = {gam[odd].sum():.6f} (觀察者)   Σγ_even = {gam[even].sum():.6f} (世界)")
print(f"ΣG_odd = {G[odd].sum():.6f}   ΣG_even = {G[even].sum():.6f}")
print(f"ΣG_even/ΣG_odd = {G[even].sum()/G[odd].sum():.8f}")
print(f"Σγ_even/Σγ_odd = {gam[even].sum()/gam[odd].sum():.8f}   (=90/88={90/88:.8f})")
print(f"Σω_even/Σω_odd = {om[even].sum()/om[odd].sum():.8f}")

n = np.arange(1, 45)
g44 = 4*np.sin(np.pi*n/88)**2
o44 = 2*np.sin(np.pi*n/88)
G44 = 1/(2*o44)
print("\n== 44-site chain ==")
print(f"Σγ(44) = {g44.sum():.6f}   ΣG(44) = {G44.sum():.6f}")
print(f"G44/ΣG_odd = {G44.sum()/G[odd].sum():.8f}")
print(f"G44/ΣG_even = {G44.sum()/G[even].sum():.8f}")

# 關鍵候選: 世界/觀察者 比嘅平方根同冪
r = gam[even].sum()/gam[odd].sum()
print(f"\n== 結構候選 ==")
print(f"r   = 90/88 = {r:.8f}")
print(f"r²  = {(90/88)**2:.8f}")
print(f"√r  = {(90/88)**0.5:.8f}")
print(f"44/43 = {44/43:.8f}   33/32 = {33/32:.8f}")

# σ_8 敏感度: σ8=0.7482 需要 ×多少先到 0.81
s8 = 0.7482
need_sq = (0.81/s8)**2
print(f"\n== σ_8 閉合需要 ==")
print(f"σ8² 需要 ×{need_sq:.4f}  (即 σ8 ×{0.81/s8:.4f})")
print(f"r²  提供 ×{(90/88)**2:.4f}  → σ8 = {s8*(90/88):.4f}")
print(f"r²+√r 組合 ×{(90/88)**2*(90/88)**0.5:.4f} → σ8 = {s8*(90/88)**1.5:.4f}")