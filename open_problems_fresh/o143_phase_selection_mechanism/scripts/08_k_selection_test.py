#!/usr/bin/env python3
"""
O143 continuation #2 — frustration-degree (k) as the structural phase selector
==============================================================================
O7 Task 5 table: σ_T by node type = 79.5 (k=0) / 41.0 (k=1) / 23.9 (k=2) μK
  -> variance monotone decreasing in frustration degree k  (STRUCTURAL, not longitude)

Test:
  T1: k=2 set == ΔE=0 set {10,12,19,22,23,25,28,32,37,40,45,46}?
  T2: σ per k (independent recompute with O182-corrected extraction)
  T3: mean |cos θ| per k  (θ = arccos(T/A), A=134.2)
  T4: O143's ΔE=0 criterion (12 nodes θ≈π/2) re-evaluated under correct criterion
  T5: top/bottom 10 nodes — what is the real "second coldest"?
"""
import numpy as np, math, json, os
from collections import defaultdict, deque

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
NODES_FILE = f'{BASE}/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
TEMPS_FILE = f'{BASE}/open_problems_fresh/o182_88grid_geometry/data/temps2_SMICA_4.17deg.json'
DE0 = {10,12,19,22,23,25,28,32,37,40,45,46}

nodes = np.loadtxt(NODES_FILE)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
adj = defaultdict(set); edges = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i); edges.append((i, j))
hop = {0: 0}; q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in hop: hop[v] = hop[u]+1; q.append(v)
color = {0: 1}; q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in color: color[w] = 1-color[u]; q.append(w)
frust = set((u,v) for u,v in edges if color[u] == color[v])
kdeg = {i: 0 for i in range(60)}
for u, v in frust: kdeg[u] += 1; kdeg[v] += 1

T = np.array(json.load(open(TEMPS_FILE))['A5_60'][:60])
A = 134.2
k_arr = np.array([kdeg[i] for i in range(60)])
hop_arr = np.array([hop[i] for i in range(60)])

print("="*74); print("  O143 continuation #2: 阻挫度 k = 結構相位選擇器"); print("="*74)

# T1: k=2 set vs DE0
k2set = set(i for i in range(60) if kdeg[i] == 2)
print(f"\n[T1] k=2 節點集 vs ΔE=0 節點集")
print(f"  k=2 ({len(k2set)}): {sorted(k2set)}")
print(f"  ΔE=0 ({len(DE0)}): {sorted(DE0)}")
print(f"  完全相同? {k2set == DE0}   (交集 {len(k2set & DE0)}, 差集 k2\\DE0={sorted(k2set-DE0)}, DE0\\k2={sorted(DE0-k2set)})")

# T2: sigma per k
print(f"\n[T2] 每個 k 嘅溫度統計 (O182 修正提取, SMICA 4.17°)")
print(f"  {'k':>3} {'n':>3} {'mean T':>9} {'std T':>9} {'mean|T|':>9} {'max|T|':>8}")
for kk in sorted(set(kdeg.values())):
    m = k_arr == kk
    print(f"  {kk:>3} {m.sum():>3} {T[m].mean():>9.1f} {T[m].std(ddof=1):>9.1f} {np.abs(T[m]).mean():>9.1f} {np.abs(T[m]).max():>8.1f}")
print(f"  (O7 原表: k=0 ±79.5 / k=1 ±41.0 / k=2 ±23.9)")

# T3: |cos| per k
cosT = np.clip(T/A, -1, 1)
print(f"\n[T3] mean |cos θ| per k (θ = arccos(T/A))")
for kk in sorted(set(kdeg.values())):
    m = k_arr == kk
    print(f"  k={kk}: n={m.sum():>2}, mean|cos|={np.mean(np.abs(cosT[m])):.4f}, "
          f"正交(|cos|<0.2)={int((np.abs(cosT[m])<0.2).sum())}/{m.sum()}, "
          f"波腹(|cos|>0.8)={int((np.abs(cosT[m])>0.8).sum())}/{m.sum()}")

# T4: O143's DE0 criterion
print(f"\n[T4] ΔE=0 12 節點 (O143 原判據: 應全部 θ≈π/2)")
de0 = sorted(DE0)
de0_cos = np.abs(cosT[de0])
print(f"  mean|cos| = {de0_cos.mean():.4f}  (k=2 組 mean|cos| = {np.mean(np.abs(cosT[k_arr==2])):.4f})")
print(f"  near π/2 (|θ-90°|<0.5rad): {int((np.abs(np.arccos(cosT[de0])-np.pi/2)<0.5).sum())}/12")
print(f"  對比全部 60: mean|cos| = {np.mean(np.abs(cosT)):.4f}")

# T5: top/bottom 10
print(f"\n[T5] 最冷/最熱 10 節點")
order = np.argsort(T)
print(f"  {'rank':>4} {'node':>5} {'T':>8} {'hop':>4} {'k':>3} {'color':>6} {'in DE0':>7}")
for r, i in enumerate(order[:10]):
    print(f"  {r+1:>4} {i:>5} {T[i]:>8.1f} {hop[i]:>4} {kdeg[i]:>3} {color[i]:>6} {str(i in DE0):>7}")
print("  ...")
for r, i in enumerate(order[-5:]):
    print(f"  {60-4+r:>4} {i:>5} {T[i]:>8.1f} {hop[i]:>4} {kdeg[i]:>3} {color[i]:>6} {str(i in DE0):>7}")

# correlation summary
print(f"\n[相關] corr(k, |T|) = {np.corrcoef(k_arr, np.abs(T))[0,1]:+.4f}; "
      f"corr(k, |cos|) = {np.corrcoef(k_arr, np.abs(cosT))[0,1]:+.4f}")

res = {
    'k2_equals_DE0': bool(k2set == DE0),
    'k2_set': sorted(k2set), 'DE0_set': sorted(DE0),
    'per_k': {str(kk): {'n': int((k_arr==kk).sum()),
                        'mean_T': float(T[k_arr==kk].mean()),
                        'std_T': float(T[k_arr==kk].std(ddof=1)),
                        'mean_absT': float(np.abs(T[k_arr==kk]).mean()),
                        'mean_abs_cos': float(np.mean(np.abs(cosT[k_arr==kk])))}
              for kk in sorted(set(kdeg.values()))},
    'de0_mean_abs_cos': float(de0_cos.mean()),
    'all_mean_abs_cos': float(np.mean(np.abs(cosT))),
    'corr_k_absT': float(np.corrcoef(k_arr, np.abs(T))[0,1]),
    'corr_k_abscos': float(np.corrcoef(k_arr, np.abs(cosT))[0,1]),
    'coldest10': [int(i) for i in order[:10]],
    'hottest5': [int(i) for i in order[-5:]],
    'T_obs': [float(t) for t in T],
}
with open(f'{O143}/data/step5_k_selection.json', 'w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step5_k_selection.json")
