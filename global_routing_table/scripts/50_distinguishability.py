#!/usr/bin/env python3
"""
GRT-50: A — 可區分性掃描 — 唔同注入節點 → 唔同阻挫圖案?
================================================================
調律者: 「A B C 順序」— A 係可區分性

問題: 注入唔同節點, 會唔會產生唔同嘅阻挫圖案 (32-bit)?
如果會 → 注入節點 = 調制符號 (訊息)
如果唔會 (全部一樣) → 冇信息容量, 要其他方法

方法:
  1. 對 12 個 ΔE=0 節點逐個注入 (強度 6.0)
  2. 記錄最終阻挫圖案 (32-bit)
  3. 兩兩比較 XOR distance → 可區分性矩陣
  4. 搵最大獨立碼集 (Hamming distance ≥ 2)
"""
import math
import numpy as np
import os, sys
from itertools import combinations

sys.path.insert(0, ".")
from grt_common import (build_graph, compute_frustration_edges,
                        edge_threshold_from_histogram, load_colors,
                        load_nodes, ang_deg)

OUT = "../data"
os.makedirs(OUT, exist_ok=True)

LINES = []
def L(s=""):
    LINES.append(str(s))
    print(s)

L("=" * 84)
L("  GRT-50: A — 可區分性 — 唔同注入節點 → 唔同阻挫圖案?")
L("=" * 84)

nodes, vecs = load_nodes()
N = len(nodes)
thresh, dists = edge_threshold_from_histogram(vecs)
adj = build_graph(vecs, thresh)
colors = load_colors()
frust = compute_frustration_edges(adj, colors)

zero_nodes = []
for i in range(N):
    k = sum(1 for j in adj[i] if (min(i,j), max(i,j)) in frust)
    if k == 2:
        zero_nodes.append(i)

A = 134.2
E_J = 1.0
J_coup = 0.5
gamma = 0.1
dt = 0.01

theta0 = np.zeros(N)
for i in range(N):
    if i in zero_nodes:
        theta0[i] = math.pi/2
    elif colors[i] == 1:
        theta0[i] = math.pi
    else:
        theta0[i] = 0.0

h = A * np.cos(theta0)

alpha_map = {}
for (i,j) in frust:
    alpha_map[(min(i,j), max(i,j))] = math.pi
for i in range(N):
    for j in adj[i]:
        if i < j and (i,j) not in alpha_map:
            alpha_map[(i,j)] = 0.0

def alpha(i, j):
    return alpha_map.get((min(i,j), max(i,j)), 0.0)

def sg_step(theta, omega, dt, inj_nodes=None, inj_strength=0, inj_duration=0, t=0):
    dtheta = omega.copy()
    domega = np.zeros(N)
    for i in range(N):
        domega[i] = -gamma * omega[i] - (E_J + h[i]) * math.sin(theta[i])
        for j in adj[i]:
            domega[i] -= J_coup * math.sin(theta[i] - theta[j] - alpha(i,j))
        if inj_nodes is not None and i in inj_nodes and t < inj_duration:
            domega[i] += inj_strength
    return dtheta, domega

def sg_integrate(theta0, omega0, dt, steps, inj_nodes=None, inj_strength=0, inj_duration=0):
    theta = theta0.copy()
    omega = omega0.copy()
    t = 0.0
    for step in range(steps):
        k1t, k1o = sg_step(theta, omega, dt, inj_nodes, inj_strength, inj_duration, t)
        k2t, k2o = sg_step(theta + 0.5*dt*k1t, omega + 0.5*dt*k1o, dt, inj_nodes, inj_strength, inj_duration, t+0.5*dt)
        k3t, k3o = sg_step(theta + 0.5*dt*k2t, omega + 0.5*dt*k2o, dt, inj_nodes, inj_strength, inj_duration, t+0.5*dt)
        k4t, k4o = sg_step(theta + dt*k3t, omega + dt*k3o, dt, inj_nodes, inj_strength, inj_duration, t+dt)
        theta = theta + (dt/6)*(k1t + 2*k2t + 2*k3t + k4t)
        omega = omega + (dt/6)*(k1o + 2*k2o + 2*k3o + k4o)
        t += dt
    return theta, omega

def phase_dist(a, b):
    return abs((a - b + math.pi) % (2*math.pi) - math.pi)

def frustration_bits(theta):
    """32-bit 阻挫圖案 (同相=1, 異相=0), 按邊排序"""
    edges = sorted(frust, key=lambda x: (x[0], x[1]))
    bits = []
    for (i,j) in edges:
        d = phase_dist(theta[i], theta[j])
        bits.append("1" if d < math.pi/2 else "0")
    return "".join(bits)

def hamming(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)

omega0 = np.zeros(N)
s_inj = 6.0

# ============================================================
# 一、基底圖案
# ============================================================
L("━" * 84)
L("  一、基底阻挫圖案")
L("━" * 84)

bits_base = frustration_bits(theta0)
L(f"  基底: {bits_base}")
L(f"  同相數: {bits_base.count('1')}/32")
L(f"  ΔE=0 節點: {zero_nodes}")
L("")

# ============================================================
# 二、12 個 ΔE=0 節點逐個注入
# ============================================================
L("━" * 84)
L("  二、12 個 ΔE=0 節點逐個注入 (強度 6.0)")
L("━" * 84)

patterns = {}
L(f"  {'注入':>4} | {'阻挫圖案 (32-bit)':>36} | {'改變':>4} | {'同相':>4}")
L(f"  {'-'*4} | {'-'*36} | {'-'*4} | {'-'*4}")

for node in zero_nodes:
    theta_f, _ = sg_integrate(theta0, omega0, dt, 4000, inj_nodes={node}, inj_strength=s_inj, inj_duration=50)
    bits = frustration_bits(theta_f)
    n_diff = hamming(bits_base, bits)
    patterns[node] = bits
    L(f"  {node:>4} | {bits} | {n_diff:>4} | {bits.count('1'):>4}")

L("")

# ============================================================
# 三、可區分性矩陣
# ============================================================
L("━" * 84)
L("  三、可區分性矩陣 (Hamming distance)")
L("━" * 84)

L(f"  {'':>6}" + "".join(f"{n:>4}" for n in zero_nodes))
for n1 in zero_nodes:
    row = f"  {n1:>4} "
    for n2 in zero_nodes:
        if n1 == n2:
            row += "  -- "
        else:
            row += f"{hamming(patterns[n1], patterns[n2]):>4} "
    L(row)

L("")

# 分析
dists = []
for n1, n2 in combinations(zero_nodes, 2):
    dists.append(hamming(patterns[n1], patterns[n2]))

L(f"  兩兩距離統計:")
L(f"    min: {min(dists)} bit")
L(f"    mean: {np.mean(dists):.1f} bit")
L(f"    max: {max(dists)} bit")
L(f"    唯一圖案數: {len(set(patterns.values()))}/{len(zero_nodes)}")
L("")

# ============================================================
# 四、最大獨立碼集
# ============================================================
L("━" * 84)
L("  四、最大獨立碼集 (Hamming ≥ 2)")
L("━" * 84)

# 貪心: 由距離最遠嘅開始
best_codes = []
remaining = list(zero_nodes)
while remaining:
    # 揀同已選全部距離 ≥ 2 嘅節點
    chosen = None
    for n in remaining:
        if all(hamming(patterns[n], patterns[c]) >= 2 for c in best_codes):
            chosen = n
            break
    if chosen is None:
        break
    best_codes.append(chosen)
    remaining.remove(chosen)

L(f"  最大獨立碼集: {best_codes}")
L(f"  碼集大小: {len(best_codes)}")
L(f"  信息容量: log₂({len(best_codes)}) = {math.log2(max(len(best_codes),2)):.1f} bits/幀")
L("")

# ============================================================
# 五、結論
# ============================================================
L("━" * 84)
L("  五、結論")
L("━" * 84)

unique = len(set(patterns.values()))
L(f"""
  ══════════════════════════════════════════════════════════
  🎯 GRT-50 (A) 結果:
  ══════════════════════════════════════════════════════════

  唯一圖案數: {unique}/{len(zero_nodes)}
  {'→ 🟢🟢 唔同注入節點 → 唔同阻挫圖案!' if unique == len(zero_nodes) else '→ ⚠️ 有碰撞 (兩個節點同圖案)'}
  {'→ 注入節點 = 調制符號! 信息可區分!' if unique == len(zero_nodes) else ''}

  兩兩距離: min {min(dists)} / mean {np.mean(dists):.1f} / max {max(dists)} bit
  最大碼集: {len(best_codes)} 個節點 (Hamming ≥ 2)
  容量: {math.log2(max(len(best_codes),2)):.1f} bits/幀 (獨立碼)

  → {'✅ 可區分性確認!' if unique == len(zero_nodes) else '🔴 需要額外編碼'}
  ══════════════════════════════════════════════════════════
""")

with open(os.path.join(OUT, "distinguishability.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(LINES) + "\n")
print(f"\n✅ 已寫入: ../data/distinguishability.txt")
