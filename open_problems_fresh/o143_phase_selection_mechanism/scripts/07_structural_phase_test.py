#!/usr/bin/env python3
"""
O143 continuation — structural phase test via O179 interference kernel
=====================================================================
After O182 verdict (longitude projection dead), re-derive θ_i from the
O179 structure: hop ladder + interference kernel phase π·hop/4
(W(i) = (frust+1)[1+(B/L₅)cos(π·hop/4)], zero free parameters).

Hypotheses tested (ALL structure-forced, no fitting):
  H1  θ_i = π·(1 + hop/4)      -> δT = A·cos(θ_i)   [interference phase + π offset]
  H2  θ_i = π·hop/4            -> δT = A·cos(θ_i)
  H3  amplitude modulation    -> δT = A·cos(π·hop/4)·sign
  H4  W(i) as weight          -> correlation of |T| with W(i)

A = 134.2 μK (structure: cold spot |node0|, O41/O7 topological bit amplitude)
Observed: O182 extracted SMICA 4.17° A5_60 temperatures (verified extraction).
"""
import numpy as np
import math
from collections import defaultdict, deque
import json, os

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
NODES_FILE = f'{BASE}/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
FRUST_FILE = f'{BASE}/main_problems/p4_cmb_cold_spot/data/frustration_edges.txt'
TEMPS_FILE = f'{BASE}/open_problems_fresh/o182_88grid_geometry/data/temps2_SMICA_4.17deg.json'
OUTDIR = f'{O143}/data'

print("=" * 74)
print("  O143 continuation: 結構相位測試 (O179 干涉核, 非 longitude)")
print("=" * 74)

# ── 1. 圖結構 (複製 O4 慣例: 閾值 28°) ──
nodes = np.loadtxt(NODES_FILE)
vecs = np.array([np.array([math.cos(math.radians(d))*math.cos(math.radians(r)),
                           math.cos(math.radians(d))*math.sin(math.radians(r)),
                           math.sin(math.radians(d))]) for r, d in nodes])
adj = defaultdict(set); edges = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i); edges.append((i, j))

hop = {0: 0}; q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in hop:
            hop[v] = hop[u] + 1; q.append(v)

color = {0: 1}; q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in color:
            color[w] = 1 - color[u]; q.append(w)

frust = set((u, v) for u, v in edges if color[u] == color[v])
kdeg = {i: 0 for i in range(60)}
for u, v in frust:
    kdeg[u] += 1; kdeg[v] += 1

ladder = [sum(1 for i in range(60) if hop[i] == h) for h in range(9)]
print(f"\n[結構驗證] 邊數={len(edges)}, 阻挫={len(frust)}, hop階梯={ladder}")
print(f"  <hop> = {np.mean([hop[i] for i in range(60)]):.4f} (理論 B=4)")
print(f"  k 分佈: " + ", ".join(f"k={kk}:{sum(1 for i in range(60) if kdeg[i]==kk)}" for kk in sorted(set(kdeg.values()))))

# ── 2. 觀測溫度 ──
d = json.load(open(TEMPS_FILE))
T_obs = np.array(d['A5_60'][:60])
print(f"\n[觀測] SMICA 4.17°: node0={T_obs[0]:.1f}, node9={T_obs[9]:.1f}, node53={T_obs[53]:.1f}")

# ── 3. 結構相位假設 ──
A = 134.2
hop_arr = np.array([hop[i] for i in range(60)])
k_arr = np.array([kdeg[i] for i in range(60)])

print(f"\n{'='*74}")
print("H1: θ_i = π(1 + hop/4)  [干涉相位 + π 偏移]")
print(f"{'='*74}")
theta1 = np.pi * (1 + hop_arr/4)
T1 = A * np.cos(theta1)
print(f"  {'hop':>4} {'n':>3} {'θ_pred':>8} {'cos':>7} {'T_pred':>8} {'T_obs mean':>10} {'|T|obs':>7}")
for h in range(9):
    m = hop_arr == h
    if m.sum() == 0: continue
    print(f"  {h:>4} {m.sum():>3} {np.degrees(theta1[m][0]):>8.1f} {np.cos(theta1[m][0]):>7.3f} {T1[m][0]:>8.1f} {T_obs[m].mean():>10.1f} {np.abs(T_obs[m]).mean():>7.1f}")
r1 = np.corrcoef(T1, T_obs)[0,1]
print(f"  corr(T_pred, T_obs) = {r1:+.4f}")
print(f"  node0: pred {T1[0]:.1f} vs obs {T_obs[0]:.1f}")
print(f"  node9: pred {T1[9]:.1f} vs obs {T_obs[9]:.1f}")
print(f"  node53: pred {T1[53]:.1f} vs obs {T_obs[53]:.1f}")

print(f"\n{'='*74}")
print("H2: θ_i = π·hop/4  [純干涉相位, 無偏移]")
print(f"{'='*74}")
theta2 = np.pi * hop_arr / 4
T2 = A * np.cos(theta2)
r2 = np.corrcoef(T2, T_obs)[0,1]
print(f"  corr = {r2:+.4f}   node0: {T2[0]:.1f} vs {T_obs[0]:.1f}")

# ── 4. 結構量 vs 觀測相關 ──
print(f"\n{'='*74}")
print("結構量 vs 觀測相關 (探索性, 多重比較警告)")
print(f"{'='*74}")
W = (k_arr + 1) * (1 + (4/11) * np.cos(np.pi * hop_arr / 4))
cands = {
    'cos(π(1+hop/4))': np.cos(theta1),
    'cos(π·hop/4)': np.cos(theta2),
    'W(i)=(frust+1)[1+C cos(πh/4)]': W,
    'frust+1 (k+1)': k_arr + 1.0,
    'hop': hop_arr.astype(float),
    '(-1)^hop': (-1.0)**hop_arr,
    'color (BFS parity)': np.array([color[i] for i in range(60)], float),
}
for name, v in cands.items():
    print(f"  corr({name:>32}, T_obs) = {np.corrcoef(v, T_obs)[0,1]:+.4f}   |T|: {np.corrcoef(v, np.abs(T_obs))[0,1]:+.4f}")

# ── 5. 極端節點結構特徵 ──
print(f"\n{'='*74}")
print("極端節點結構特徵 (|T| > 100 μK)")
print(f"{'='*74}")
ext = np.where(np.abs(T_obs) > 100)[0]
print(f"  {'node':>5} {'T_obs':>8} {'hop':>4} {'k':>3} {'color':>6} {'θ_obs(deg)':>11}")
for i in ext:
    cos_obs = np.clip(T_obs[i]/A, -1, 1)
    print(f"  {i:>5} {T_obs[i]:>8.1f} {hop[i]:>4} {kdeg[i]:>3} {color[i]:>6} {np.degrees(np.arccos(cos_obs)):>11.1f}")

# 全部 k=0 節點
print(f"\n  k=0 節點 (自由節點, O43-F 機制):")
print(f"  {'node':>5} {'T_obs':>8} {'hop':>4} {'color':>6}")
for i in range(60):
    if kdeg[i] == 0:
        print(f"  {i:>5} {T_obs[i]:>8.1f} {hop[i]:>4} {color[i]:>6}")

# ── 6. 儲存 ──
res = {
    'edges': len(edges), 'frustration': len(frust), 'hop_ladder': ladder,
    'mean_hop': float(np.mean(hop_arr)),
    'A_muK': A,
    'corr_H1': float(r1), 'corr_H2': float(r2),
    'corr_W_Tobs': float(np.corrcoef(W, T_obs)[0,1]),
    'corr_k_Tobs': float(np.corrcoef(k_arr, T_obs)[0,1]),
    'corr_hop_Tobs': float(np.corrcoef(hop_arr, T_obs)[0,1]),
    'per_hop': {str(h): {'n': int((hop_arr==h).sum()),
                          'T_mean': float(T_obs[hop_arr==h].mean()),
                          'absT_mean': float(np.abs(T_obs[hop_arr==h]).mean()),
                          'T_pred_H1': float(T1[hop_arr==h][0])} for h in range(9) if (hop_arr==h).sum()>0},
    'node_hop': [int(hop[i]) for i in range(60)],
    'node_k': [int(kdeg[i]) for i in range(60)],
    'node_color': [int(color[i]) for i in range(60)],
    'T_obs': [float(t) for t in T_obs],
    'T_pred_H1': [float(t) for t in T1],
}
os.makedirs(OUTDIR, exist_ok=True)
with open(f'{OUTDIR}/step4_structural_phase.json', 'w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {OUTDIR}/step4_structural_phase.json")
