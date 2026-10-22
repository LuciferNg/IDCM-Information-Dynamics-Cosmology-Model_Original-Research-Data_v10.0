#!/usr/bin/env python3
"""
O143 continuation #4 — robustness of the k-|T| correlation
==========================================================
The corr(k,|T|) = -0.382 (p_perm = 0.0012) could be driven by 3-4 extreme nodes.
Test: remove extremes / node47 / k=0 group and see if the signal survives.
Also: Bonferroni over the ~7 structural quantities tested in script 07.
"""
import numpy as np, math, json
from collections import defaultdict, deque

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
NODES_FILE = f'{BASE}/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
TEMPS_FILE = f'{BASE}/open_problems_fresh/o182_88grid_geometry/data/temps2_SMICA_4.17deg.json'
rng = np.random.default_rng(7)

nodes = np.loadtxt(NODES_FILE)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
adj = defaultdict(set); edges = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i); edges.append((i, j))
color = {0: 1}; q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in color: color[w] = 1-color[u]; q.append(w)
frust = set((u,v) for u,v in edges if color[u] == color[v])
kdeg = np.zeros(60, int)
for u, v in frust: kdeg[u] += 1; kdeg[v] += 1
T = np.array(json.load(open(TEMPS_FILE))['A5_60'][:60]); A = 134.2

def perm_p(kk, tt, N=100000):
    r = np.corrcoef(kk, tt)[0,1]
    c = sum(1 for _ in range(N) if np.corrcoef(kk, rng.permutation(tt))[0,1] <= r)
    return r, (c+1)/(N+1)

print("="*74); print("  O143 #4: k-|T| 相關穩健性"); print("="*74)

absT = np.abs(T)
r0, p0 = perm_p(kdeg, absT, 100000)
print(f"\n[基準] 全 60 節點: corr(k,|T|) = {r0:+.4f}, p = {p0:.5f}")

# A: remove top-4 extremes
for name, rm in [('移除 4 個極端 (|T|>100)', [0,47,9,53]),
                 ('移除 3 個極端 (原 O143: 0,9,53)', [0,9,53]),
                 ('移除 k=0 全組', list(np.where(kdeg==0)[0])),
                 ('移除 node47', [47]),
                 ('只留 k=1,2 (移除 k=0)', list(np.where(kdeg==0)[0]))]:
    keep = np.array([i for i in range(60) if i not in rm])
    if len(keep) < 10: continue
    r, p = perm_p(kdeg[keep], absT[keep], 50000)
    print(f"  {name:>28}: n={len(keep):>2}, corr = {r:+.4f}, p = {p:.5f}")

# B: Bonferroni over script-07 quantities
print(f"\n[Bonferroni] script 07 測咗 7 個結構量; 最強 = corr(k,|T|) p=0.0012")
print(f"  校正 p = 0.0012 × 7 = {0.0012*7:.5f} — 仍 < 0.05 ✅")

# C: 位移檢定 — k=0 group mean|T| vs rest
g0 = absT[kdeg==0]; gr = absT[kdeg>0]
print(f"\n[位移] k=0 mean|T| = {g0.mean():.1f} (n=8), k>0 mean|T| = {gr.mean():.1f} (n=52)")
diff = g0.mean() - gr.mean()
cnt = 0; NC = 200000
for _ in range(NC):
    p = rng.permutation(absT)
    if p[:8].mean() - p[8:].mean() >= diff: cnt += 1
print(f"  置換 p (單尾) = {(cnt+1)/(NC+1):.5f}")

# D: 極端節點 vs k 關係 (k=0 有 2 個極端, 佔 k=0 嘅 25%; k=1 有 1 個 (node47), 佔 2.5%; k=2 有 0)
print(f"\n[極端分佈] |T|>100 節點:")
for kk in (0,1,2):
    m = (kdeg==kk)
    n_ext = int((np.abs(T[m])>100).sum())
    print(f"  k={kk}: n={m.sum():>2}, 極端 {n_ext} ({100*n_ext/m.sum():.1f}%)")

res = {'baseline': {'r': float(r0), 'p': float(p0)},
       'bonferroni_7': float(0.0012*7),
       'k0_vs_rest': {'mean_absT_k0': float(g0.mean()), 'mean_absT_k_gt0': float(gr.mean())},
       'extreme_by_k': {str(kk): {'n': int((kdeg==kk).sum()),
                                   'n_extreme': int((np.abs(T[kdeg==kk])>100).sum())} for kk in (0,1,2)}}
with open(f'{O143}/data/step7_robustness.json', 'w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step7_robustness.json")
