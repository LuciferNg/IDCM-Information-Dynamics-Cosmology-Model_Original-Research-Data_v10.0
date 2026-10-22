#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O237 U2 — K_tree 譜家族盲測 (𝒯 = K_chain ⊗ K_tree 嘅樹側讀數)
================================================================================
docs/09: chain 內部標量/統計家族全負。剩真正未試: K_tree 譜 (O155 R3, O210 C9):
  λ_k = B sin²(kπ/sites), sites = 4(B²+1) = 68, k = 1..K_tree^(mode) = 33
  Σλ = B³ + B/2 = 66 = 2·K_tree^(mode); 固定點 k=17 → λ=μ²=2; 配對和 = B

候選讀數家族 (全 chain 內, 零外部):
  G1: λ_n (樹譜喺 A5 mode n), G2: 66/λ_n, G3: λ_n/λ_1, G4: λ_n·γ_n,
  G5: 66/γ_n, G6: 66/層能量, G7: λ_n/γ_n, G8: Σλ(到n) cumsum
先計晒, 後對照 (唔 fit)。
"""
import math

def g(m): return 4 * math.sin(math.pi * m / 88) ** 2
def lam(k): return 4 * math.sin(math.pi * k / 68) ** 2   # B=4: B sin²(kπ/68), ×?  4=B

B = 4
sites = 4*(B**2+1)   # 68
K = 2*B**2 + 1       # 33 = K_tree^(mode)
SIGL = B**3 + B/2    # 66

MODES = [1, 2, 3, 4, 5, 7, 9, 11]
PG = {"e":"e","u":"u","d":"d","s":"s","mu":"mu","c":"c","tau":"tau","b":"b"}

print("="*96)
print("O237 U2 — K_tree 樹譜讀數家族 (先計, 後對照)")
print("="*96)
print(f"  λ_k = B sin²(kπ/68), B=4, sites=68, K_tree^(mode)=33, Σλ=66 (O155 R3 / O210 C9)")

lam1 = lam(1)
gg1 = g(1)
print(f"\n[1] 樹譜樣本: λ_1={lam1:.10f}  λ_17={lam(17):.6f} (固定點, 期望 μ²=2)  λ_33={lam(33):.6f}")
print(f"     ∑λ = {sum(lam(k) for k in range(1,34)):.4f} (期望 66)")

rows = []
for n in MODES:
    G1 = lam(n)
    G2 = SIGL/lam(n)
    G3 = lam(n)/lam1
    G4 = lam(n)*g(n)
    G5 = SIGL/g(n)
    G6 = SIGL/(g(n) + g(44-n))
    G7 = lam(n)/g(n)
    G8 = sum(lam(k) for k in range(1, n+1))
    rows.append((n, G1, G2, G3, G4, G5, G6, G7, G8))
    print(f"  n={n:>2}: λ_n={G1:>10.6f}  66/λ={G2:>12.5f}  λ/λ1={G3:>10.5f}  λγ={G4:>10.5f}  "
          f"66/γ={G5:>12.5f}  66/(γ+γ')={G6:>10.5f}  λ/γ={G7:>10.5f}  cumλ={G8:>10.5f}")

print("\n[2] A5 C_f 對照 (O206 第十輪):")
M0 = 27.9009
MASS = {"e":0.510998950,"u":2.16,"d":4.67,"s":93.4,"mu":105.6583755,
        "c":1270.0,"tau":1776.86,"b":4180.0}
CF = {n: MASS[p]/(M0*g(n)) for p, n in zip(PG, MODES)}
for n, p in zip(MODES, PG):
    print(f"  {p:>4} n={n:>2}: C_f={CF[n]:>10.4f}")

print("\n[3] 家族 × C_f 比例 spread (1.0 = 完美結構):")
families = {'G1 lam_n': 1, 'G2 66/lam_n': 2, 'G3 lam/lam1': 3, 'G4 lam*gamma': 4,
            'G5 66/gamma': 5, 'G6 66/(g+gprime)': 6, 'G7 lam/gamma': 7, 'G8 cumlam': 8}
for fname, idx in families.items():
    r = [CF[n]/row[idx] for n, row in zip(MODES, rows)]
    spread = max(r)/min(r)
    print(f"  {fname:>14}: ratio spread = {spread:>10.4f}×")

print("""
[判定] 若任何家族 ratio spread ≪ 3 (接近常數), 話聲 — 但要注意唔可以放寬標準。
      期望: 同 chain 標量掃描一致, 全部 spread 大 (C_f 需要 richer structure)。
      真正結構 = 一次過 8 值, 唔係個別 near-miss。
""")