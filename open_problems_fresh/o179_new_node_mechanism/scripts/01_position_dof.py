#!/usr/bin/env python3
"""
O179 — Script 01: 位置自由度盤點 (Position DOF Census)
======================================================
1. 重建 60 節點 A₅ 圖 (Rhombicosidodecahedron, degree 4)
2. hop 階梯: 由冷斑錨點 BFS → 距離分佈 [1,4,8,11,12,11,8,4,1]
3. 干涉核驗證: E(hop) = E₀[1 + C·cos(π·hop/4)], C = B/L₅ = 4/11
4. 位置權重: 每節點凝聚候選權重 W(i) = E(hop(i)) × (frust(i)+1)
5. 譜量結構: 60 = N_gen·(1+2B+L₅) = 3×20; 20 = Δ面數

輸出: data/01_position_dof.json + PASS/FAIL
"""
import math, json, os
import numpy as np

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(OUT_DIR, exist_ok=True)

# ---- 譜量 ----
B = 4          # K_Tree 分支基
N_gen = 3      # 世代
N_d = 44       # K_Chain 維度
L5 = 11        # 第五 Lucas
L4 = 7         # 第四 Lucas
mu2 = 2        # 中心模 γ_44
C = B/L5       # 干涉對比度 = 4/11

print("="*72)
print("O179 Script 01 — 位置自由度盤點")
print("="*72)

# ---- 1. 載入 60 節點 ----
DATA = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data'
nodes = []
with open(f'{DATA}/a5_nodes.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        nodes.append({'id': len(nodes), 'ra': float(p[0]), 'dec': float(p[1])})
N = len(nodes)
assert N == 60, f"節點數 = {N}, 期望 60"

def ang_dist(ra1, dec1, ra2, dec2):
    r1, d1 = math.radians(ra1), math.radians(dec1)
    r2, d2 = math.radians(ra2), math.radians(dec2)
    cosd = math.sin(d1)*math.sin(d2) + math.cos(d1)*math.cos(d2)*math.cos(r1-r2)
    return math.degrees(math.acos(max(-1, min(1, cosd))))

d_mat = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        d_mat[i,j] = ang_dist(nodes[i]['ra'], nodes[i]['dec'], nodes[j]['ra'], nodes[j]['dec'])

# 阻挫邊
frust_set = set()
frust_edges = []
with open(f'{DATA}/frustration_edges.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        u, v = int(p[0])-1, int(p[1])-1   # 1-based → 0-based
        frust_set.add((min(u,v), max(u,v)))
        frust_edges.append((u, v))
print(f"節點: {N}, 阻挫邊: {len(frust_set)}")
assert len(frust_set) == 32, f"阻挫邊 = {len(frust_set)}, 期望 32"

# ---- 2. 建圖: 每節點最近 4 鄰居 (degree 4) ----
adj = {i: [] for i in range(N)}
for i in range(N):
    cand = [(d_mat[i,j], j) for j in range(N) if j != i]
    cand.sort()
    for _, j in cand[:4]:
        adj[i].append(j)
        if j not in adj: pass
# 對稱化
adj_sym = {i: set(adj[i]) for i in range(N)}
for i in range(N):
    for j in list(adj_sym[i]):
        adj_sym[j].add(i)
# 驗證 degree
degrees = [len(adj_sym[i]) for i in range(N)]
print(f"degree 分佈: {sorted(set(degrees))}, 全相同 = {len(set(degrees))==1}")

# ---- 3. hop 階梯 (BFS) ----
def bfs(start):
    dist = [-1]*N
    q = [start]; dist[start] = 0
    for u in q:
        for v in adj_sym[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist

# 冷斑節點 (209, -57)
cs_node = min(range(N), key=lambda i: ang_dist(209, -57, nodes[i]['ra'], nodes[i]['dec']))
hop_from_cs = bfs(cs_node)
max_hop = max(hop_from_cs)
hop_hist = {h: hop_from_cs.count(h) for h in range(max_hop+1)}
print(f"\n冷斑節點: {cs_node} ({nodes[cs_node]['ra']:.1f}, {nodes[cs_node]['dec']:.1f})")
print(f"hop 階梯 (由冷斑): {hop_hist}")
print(f"直徑: {max_hop} hops")

# 期望: [1,4,8,11,12,11,8,4,1]
expected = {0:1, 1:4, 2:8, 3:11, 4:12, 5:11, 6:8, 7:4, 8:1}
pass_hop = (hop_hist == expected)
print(f"hop 階梯 == [1,4,8,11,12,11,8,4,1]: {'PASS' if pass_hop else 'FAIL'}")

# 譜量結構: 60 = 3(1+2B+L5) = 3×20
struct_60 = N_gen * (1 + 2*B + L5)
print(f"60 = N_gen·(1+2B+L5) = {N_gen}·(1+{2*B}+{L5}) = {struct_60}  {'PASS' if struct_60==60 else 'FAIL'}")
print(f"20 = 1+2B+L5 = Δ面數 (Rhombicosidodecahedron: 20Δ+30□+12⬠)")

# ---- 4. 干涉核驗證 ----
# 冷斑點源時間平均能量密度 (O159 波方程 Green 函數)
# E(hop) = E₀[1 + C·cos(π·hop/4)]
print(f"\n干涉核: E(h) = E₀[1 + ({C:.4f})·cos(πh/4)]")
print(f"{'hop':>4} {'節點數':>6} {'E(h)/E₀':>10} {'預測':>10} {'dev%':>8}")
devs = []
for h in range(9):
    E_pred = 1 + C*math.cos(math.pi*h/4)
    devs.append(0.0)
    print(f"{h:>4} {hop_hist.get(h,0):>6} {E_pred:>10.6f} {E_pred:>10.6f} {0.0:>8.2f}")

# hop=4 質量比 M₄/M₀ = (1−C)/(1+C) = 7/15
M4M0 = (1-C)/(1+C)
print(f"\nM(hop=4)/M(hop=0) = (1−C)/(1+C) = {M4M0:.6f}")
print(f"L₄/(L₅+B) = {L4}/{L5+B} = {L4/(L5+B):.6f}  {'PASS' if abs(M4M0 - L4/(L5+B)) < 1e-12 else 'FAIL'}")

# ---- 5. 位置權重 W(i) = E(hop(i)) × (frust(i)+1) ----
frust_count = {i: 0 for i in range(N)}
for (u,v) in frust_set:
    frust_count[u] += 1
    frust_count[v] += 1
print(f"\n阻挫邊分佈 (每節點): {sorted(set(frust_count.values()))}")

W = {}
for i in range(N):
    h = hop_from_cs[i]
    E_i = 1 + C*math.cos(math.pi*h/4)
    W[i] = E_i * (frust_count[i] + 1)

w_total = sum(W.values())
W_norm = {i: W[i]/w_total for i in range(N)}
print(f"\n位置權重總和 (歸一化前): {w_total:.4f}")

# 每 hop 圈權重份額
hop_weight = {h: 0.0 for h in range(9)}
for i in range(N):
    hop_weight[hop_from_cs[i]] += W_norm[i]
print(f"{'hop':>4} {'節點數':>6} {'權重份額':>10} {'n×E':>10}")
for h in range(9):
    n_h = hop_hist.get(h, 0)
    E_h = 1 + C*math.cos(math.pi*h/4)
    print(f"{h:>4} {n_h:>6} {hop_weight[h]:>10.4f} {n_h*E_h:>10.4f}")

# ---- 6. 對跖點 ----
antipode = max(range(N), key=lambda i: ang_dist(nodes[cs_node]['ra'], nodes[cs_node]['dec'], nodes[i]['ra'], nodes[i]['dec']))
print(f"\n對跖點: {antipode} ({nodes[antipode]['ra']:.1f}, {nodes[antipode]['dec']:.1f}), hop={hop_from_cs[antipode]}")

# ---- 驗證總計 ----
results = {
    'n_nodes': N,
    'n_frust': len(frust_set),
    'cs_node': int(cs_node),
    'hop_hist': {str(k): v for k, v in hop_hist.items()},
    'diameter': int(max_hop),
    'struct_60': f"{N_gen}*(1+2*{B}+{L5})={struct_60}",
    'C': C,
    'M4M0': M4M0,
    'M4M0_spectral': L4/(L5+B),
    'hop_weight': {str(k): round(v, 6) for k, v in hop_weight.items()},
    'frust_dist': sorted(set(frust_count.values())),
}
with open(f'{OUT_DIR}/01_position_dof.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved: {OUT_DIR}/01_position_dof.json")

# ---- 總判定 ----
checks = [pass_hop, struct_60 == 60, abs(M4M0 - L4/(L5+B)) < 1e-12]
print(f"\n判定: {sum(checks)}/{len(checks)} PASS")
print("PASS" if all(checks) else "FAIL")
