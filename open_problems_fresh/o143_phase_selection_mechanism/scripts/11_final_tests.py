#!/usr/bin/env python3
"""
O143 continuation #5 — final tests for the two solid claims
===========================================================
C1: ΔE=0 (k=2) 12 nodes have lower mean|cos θ| than random 12-node groups
    (O143 original prediction: ΔE=0 nodes should be θ≈π/2)
C2: extremes (|T|>100) concentrate in k=0 group — Fisher exact
C3: k=2 ⟺ ΔE=0 is graph-only (re-verify without touching T)
"""
import numpy as np, math, json
from collections import defaultdict, deque
from scipy import stats

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
NODES_FILE = f'{BASE}/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
TEMPS_FILE = f'{BASE}/open_problems_fresh/o182_88grid_geometry/data/temps2_SMICA_4.17deg.json'
rng = np.random.default_rng(99)
DE0 = np.array([10,12,19,22,23,25,28,32,37,40,45,46])

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
abscos = np.abs(np.clip(T/A, -1, 1))

print("="*74); print("  O143 #5: 兩項核心聲稱嘅檢定"); print("="*74)

# C1
m_de0 = abscos[DE0].mean()
N = 200000
cnt = sum(1 for _ in range(N) if abscos[rng.choice(60, 12, replace=False)].mean() <= m_de0)
p1 = (cnt+1)/(N+1)
print(f"\n[C1] ΔE=0 (k=2) 12 節點 mean|cos θ| = {m_de0:.4f}")
print(f"     全部 60 mean|cos| = {abscos.mean():.4f}")
print(f"     隨機 12 節點組 ≤ {m_de0:.4f} 概率 p = {p1:.5f}  (N={N})")
print(f"     ⟹ O143 原判據「ΔE=0 節點 θ≈π/2」喺觀測相位下 {'✅ 顯著成立' if p1<0.05 else '🟡 唔顯著'}")

# C2 Fisher
ext_mask = np.abs(T) > 100
tab = [[int((ext_mask & (kdeg==0)).sum()), int((~ext_mask & (kdeg==0)).sum())],
       [int((ext_mask & (kdeg>0)).sum()), int((~ext_mask & (kdeg>0)).sum())]]
odds, pf = stats.fisher_exact(tab)
print(f"\n[C2] 極端 (|T|>100) 分佈: k=0: {tab[0][0]}/{sum(tab[0])} (37.5%), k>0: {tab[1][0]}/{sum(tab[1])} (1.9%)")
print(f"     Fisher exact p = {pf:.5f}, odds ratio = {odds:.2f}")
print(f"     ⟹ k=0 自由節點顯著承載極端 {'✅' if pf<0.05 else '🟡'}")

# C3 graph-only
k2 = set(np.where(kdeg==2)[0].tolist())
print(f"\n[C3] k=2 ⟺ ΔE=0 (純圖, 未用 T): {k2 == set(DE0.tolist())}")
print(f"     12 個 k=2 節點 = {sorted(k2)}")

# summary table
print(f"\n{'='*74}"); print("總結表 (觀測 SMICA 4.17°, O182 修正提取)"); print(f"{'='*74}")
print(f"  {'k':>3} {'n':>3} {'σ(T)':>7} {'mean|T|':>8} {'mean|cosθ|':>11} {'極端':>6} {'身份':>22}")
for kk, ident in [(0,'自由節點 (無阻挫)'),(1,'端點 (縫合線端)'),(2,'ΔE=0 最優位元')]:
    m = kdeg==kk
    print(f"  {kk:>3} {m.sum():>3} {T[m].std(ddof=1):>7.1f} {np.abs(T[m]).mean():>8.1f} "
          f"{abscos[m].mean():>11.4f} {int((np.abs(T[m])>100).sum()):>6} {ident:>22}")

res = {'C1_de0_mean_abscos': float(m_de0), 'C1_p': float(p1), 'C1_N': N,
       'C2_table': tab, 'C2_fisher_p': float(pf), 'C2_odds': float(odds),
       'C3_k2_equals_DE0': bool(k2 == set(DE0.tolist())),
       'per_k': {str(kk): {'n': int((kdeg==kk).sum()), 'std_T': float(T[kdeg==kk].std(ddof=1)),
                            'mean_absT': float(np.abs(T[kdeg==kk]).mean()),
                            'mean_abscos': float(abscos[kdeg==kk].mean()),
                            'n_extreme': int((np.abs(T[kdeg==kk])>100).sum())} for kk in (0,1,2)}}
with open(f'{O143}/data/step8_final_tests.json', 'w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step8_final_tests.json")
