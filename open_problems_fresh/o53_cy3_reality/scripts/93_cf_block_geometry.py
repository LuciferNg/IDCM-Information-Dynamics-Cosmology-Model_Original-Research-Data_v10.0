#!/usr/bin/env python3
"""
O53 A1 攻堅: c_f n/3 機制 — 真 κ block 幾何對應
====================================================
c_f 表 (9 粒子):
  t: +1/3, b: +1, c: +2/3, τ: -2/3, s: -2/3, μ: -1/3, d: -2/3, u: 0, e: +1

假設: c_f 由 (36,98) 真 κ 嘅 3×12 block 幾何決定
測試: block 本徵值/trace 同 c_f 相關?
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53: c_f vs 真 κ block 幾何")
print("=" * 70)

with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
    ct = json.load(f)
K = np.array(ct['kappa'])

with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])

Y = np.einsum('ijk,k->ij', K, J0)
Y = (Y + Y.T) / 2

blocks = [(0,12), (12,24), (24,36)]
print(f"[1] 3×12 block 譜 (真 κ):")
block_evals = []
for bi, (a, b) in enumerate(blocks):
    B = Y[a:b, a:b]
    ev = np.linalg.eigvalsh(B)
    ev_sorted = np.sort(ev)[::-1]
    block_evals.append(ev_sorted)
    print(f"  Block {bi}: λ = {ev_sorted[:4]}...")
    print(f"    tr = {np.trace(B):.4f}, det = {np.linalg.det(B):.4f}")
    print(f"    λ_max = {ev_sorted[0]:.4f}, |λ_min| = {abs(ev_sorted[-1]):.4f}")

# 生成 c_f 結構候選
# c_f ∈ {+1, +2/3, +1/3, 0, -1/3, -2/3}
# 全部 n/3, n ∈ {-2,-1,0,1,2,3}
# 對應 3c_f ∈ {-2,-1,0,1,2,3}

# 粒子 → 3c_f:
particles = {
    't': 1, 'b': 3, 'c': 2, 'tau': -2, 's': -2,
    'mu': -1, 'd': -2, 'u': 0, 'e': 3
}
print(f"\n[2] 3c_f 值: {particles}")

# 有趣: 3c_f ∈ {-2,-1,0,1,2,3} = 連續 6 整數
# 呢個同之前 3c 矩陣 (代×電荷) 一致!

# 檢查: 3c_f 值域 {-2..3} 對應 (36,98) 咩結構?
# 36 = 6², 98 = ?
print(f"\n[3] 數字結構:")
print(f"  3c_f 值域: {-2,-1,0,1,2,3} (6 個連續值)")
print(f"  6 = B+1 = φ³-φ⁻³+1")
print(f"  6² = 36 = h11")
print(f"  3c_f 平均: {np.mean(list(particles.values())):.3f}")
print(f"  Σ3c_f = {sum(particles.values())}")
print(f"  Σ(3c_f)² = {sum(v*v for v in particles.values())}")

# 關鍵: Σ(3c_f)² = 36? (之前 scripts/55 發現)
s = sum(v*v for v in particles.values())
print(f"\n  Σ(3c_f)² = {s} vs 36 = h11: {'✅' if s == 36 else '❌'}")

# 每個 block 嘅 c_f 分配?
# 粒子 (t,b,c,τ,s,μ,d,u,e) — 3 代 × 3 粒子
# 代 1: (u,d,e), 代 2: (c,s,μ), 代 3: (t,b,τ)
gen1 = [particles['u'], particles['d'], particles['e']]  # (0,-2,3)
gen2 = [particles['c'], particles['s'], particles['mu']]  # (2,-2,-1)
gen3 = [particles['t'], particles['b'], particles['tau']] # (1,3,-2)
print(f"\n[4] 三代 3c_f:")
print(f"  代1 (u,d,e): {gen1}, 和 = {sum(gen1)}")
print(f"  代2 (c,s,μ): {gen2}, 和 = {sum(gen2)}")
print(f"  代3 (t,b,τ): {gen3}, 和 = {sum(gen3)}")

# 3×3 矩陣 (代 × 電荷)
M = np.array([gen1, gen2, gen3])
print(f"\n  3×3 矩陣 (代×電荷):")
print(M)
print(f"  det = {np.linalg.det(M):.0f}")
print(f"  tr = {np.trace(M):.0f}")
print(f"  ΣΣ = {M.sum():.0f}")
print(f"  Σ代² (行和平方): {[sum(r*r for r in row) for row in M]}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)