#!/usr/bin/env python3
"""
O179 — Script 02: 層級映射 + 位置選擇規則 (Hierarchy Mapping)
============================================================
1. <hop> = B = 4 驗證 (位置分佈重心 = 分支基)
2. hop 階梯對稱性 n(h)=n(8-h), 直徑 8 = 2B
3. 阻挫邊 hop 分佈 — 翻轉端點 = 新凝聚燃料位置
4. 4^{-ℓ} 事件率 × 位置權重 → 空間分佈預言
5. 凝聚事件位置概率 P(i) ∝ W(i) = (frust(i)+1)·E(hop(i))

輸出: data/02_hierarchy_mapping.json + PASS/FAIL
"""
import math, json, os
import numpy as np

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(OUT_DIR, exist_ok=True)

B = 4; N_gen = 3; N_d = 44; L5 = 11; L4 = 7; mu2 = 2
C = B/L5

DATA = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data'
nodes = []
with open(f'{DATA}/a5_nodes.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        nodes.append({'id': len(nodes), 'ra': float(p[0]), 'dec': float(p[1])})
N = len(nodes)

def ang_dist(ra1, dec1, ra2, dec2):
    r1, d1 = math.radians(ra1), math.radians(dec1)
    r2, d2 = math.radians(ra2), math.radians(dec2)
    cosd = math.sin(d1)*math.sin(d2) + math.cos(d1)*math.cos(d2)*math.cos(r1-r2)
    return math.degrees(math.acos(max(-1, min(1, cosd))))

d_mat = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        d_mat[i,j] = ang_dist(nodes[i]['ra'], nodes[i]['dec'], nodes[j]['ra'], nodes[j]['dec'])

frust_set = set()
with open(f'{DATA}/frustration_edges.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        u, v = int(p[0])-1, int(p[1])-1
        frust_set.add((min(u,v), max(u,v)))

adj = {i: [] for i in range(N)}
for i in range(N):
    cand = [(d_mat[i,j], j) for j in range(N) if j != i]
    cand.sort()
    for _, j in cand[:4]:
        adj[i].append(j)
adj_sym = {i: set(adj[i]) for i in range(N)}
for i in range(N):
    for j in list(adj_sym[i]):
        adj_sym[j].add(i)

def bfs(start):
    dist = [-1]*N
    q = [start]; dist[start] = 0
    for u in q:
        for v in adj_sym[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist

cs_node = min(range(N), key=lambda i: ang_dist(209, -57, nodes[i]['ra'], nodes[i]['dec']))
hop_from_cs = bfs(cs_node)
hop_hist = {h: hop_from_cs.count(h) for h in range(max(hop_from_cs)+1)}

print("="*72)
print("O179 Script 02 — 層級映射 + 位置選擇規則")
print("="*72)

# ---- 1. <hop> = B = 4 ----
total_hops = sum(h*hop_hist[h] for h in hop_hist)
mean_hop = total_hops / N
print(f"\n1. 平均 hop 距離: Σh·n(h) = {total_hops}, <hop> = {mean_hop:.6f}")
print(f"   B = {B}  {'PASS' if abs(mean_hop - B) < 1e-9 else 'FAIL'}")

# ---- 2. 對稱性 ----
D = max(hop_from_cs)
sym_ok = all(hop_hist[h] == hop_hist[D-h] for h in range(D+1))
print(f"2. hop 階梯對稱 n(h)=n({D}-h): {'PASS' if sym_ok else 'FAIL'}, 直徑 = {D} = 2B = {2*B}  {'PASS' if D==2*B else 'FAIL'}")

# ---- 3. 阻挫邊 hop 分佈 ----
print(f"\n3. 阻挫邊 hop 分佈 (翻轉端點 = 凝聚燃料):")
frust_hop_pairs = []
edge_hop_mid = []
for (u, v) in frust_set:
    hu, hv = hop_from_cs[u], hop_from_cs[v]
    frust_hop_pairs.append((min(hu,hv), max(hu,hv)))
    edge_hop_mid.append((hu+hv)/2)

# 端點 hop 統計
endpoint_hops = []
for (u,v) in frust_set:
    endpoint_hops.append(hop_from_cs[u])
    endpoint_hops.append(hop_from_cs[v])
from collections import Counter
ep_hist = Counter(endpoint_hops)
print(f"   端點 hop 分佈: {dict(sorted(ep_hist.items()))}")
# 期望: 每 hop 圈節點數 × 阻挫邊碰觸率
# 阻挫邊端點總數 = 64 = 2×32

# 阻挫邊中點 hop (邊所在位置)
mid_hist = Counter(round(m,1) for m in edge_hop_mid)
print(f"   邊中點 hop 分佈: {dict(sorted(mid_hist.items()))}")

# ---- 4. 位置權重 W(i) = (frust+1)·E(hop) ----
frust_count = {i: 0 for i in range(N)}
for (u,v) in frust_set:
    frust_count[u] += 1
    frust_count[v] += 1

W = {}
for i in range(N):
    h = hop_from_cs[i]
    E_i = 1 + C*math.cos(math.pi*h/4)
    W[i] = E_i * (frust_count[i] + 1)

# 結構身份檢查: ΣW = ? 
sumW = sum(W.values())
print(f"\n4. ΣW(i) = {sumW:.6f}")
# 候選: ΣW = Σ_h n(h)·E(h)·<frust+1|h>  — 需要條件平均
# 先計 Σ_h n(h)·E(h) (冇 frust):
sum_nE = sum(hop_hist[h]*(1 + C*math.cos(math.pi*h/4)) for h in range(D+1))
print(f"   Σ n(h)·E(h) = {sum_nE:.6f} (冇 frust 調製)")
# 候選身份: Σ n·E = ?
# 1.3636+5.0285+8+8.1716+7.6364+8.1716+8+5.0285+1.3636 ≈ 52.76
candidates = {
    '3·N_gen+B·L5+mu2': 3*N_gen + B*L5 + mu2,       # 9+44+2 = 55
    'L6+L5+L4+L3': 18+11+7+4,                        # 40
    'F11-F10': 89-55,                                 # 34
    'N_d+B+L4+mu2': 44+4+7+2,                         # 57
    '2F7+F5': 2*13+5,                                 # 31
    'B·(L5+2)+mu2': 4*13+2,                           # 54
}
for name, val in candidates.items():
    print(f"   候選 {name} = {val:.4f}  dev = {100*abs(val-sum_nE)/sum_nE:.2f}%")

# ---- 5. 層級映射: N_ℓ = 44·4^ℓ 模態預算 ↔ 位置 ----
print(f"\n5. 層級映射 (O140 FSR + O174 電荷稀釋):")
print(f"   N_ℓ = {N_d}·4^ℓ 模態預算:")
for ell in range(5):
    Nl = N_d * 4**ell
    ql = 1/4**ell
    print(f"   ℓ={ell}: N_ℓ = {Nl:>6}, q_ℓ = {ql:.6f} = 4^−{ell}")

# 模態預算 vs 節點/邊
print(f"   60 節點 + 32 阻挫邊 = 92 位置自由度")
print(f"   N_0 = 44 模態 ↔ 每模態 1 個世界通道 (O140)")
# 44·4^ℓ 同 60 嘅關係: 44 = N_d, 60 = 節點
# 每層 ℓ 凝聚事件率 q_ℓ = 4^−ℓ → 每圈 hop 圈嘅事件數 ∝ W

# ---- 6. 預言: 新凝聚位置分佈 P(i) ∝ W(i) ----
print(f"\n6. 位置選擇規則 (凝聚概率 ∝ 局部應變能密度):")
print(f"   P(i) ∝ W(i) = (frust(i)+1)·[1 + (B/L₅)·cos(π·hop(i)/4)]")
print(f"   {'節點':>4} {'hop':>4} {'frust':>6} {'W(i)':>10} {'P(i)%':>8}")
top = sorted(range(N), key=lambda i: W[i], reverse=True)[:10]
for i in top:
    print(f"   {i:>4} {hop_from_cs[i]:>4} {frust_count[i]:>6} {W[i]:>10.4f} {100*W[i]/sumW:>8.3f}")

# 各 hop 圈凝聚概率 (加總節點權重)
print(f"\n   每 hop 圈凝聚概率份額:")
hop_prob = {h: 0.0 for h in range(D+1)}
for i in range(N):
    hop_prob[hop_from_cs[i]] += W[i]/sumW
for h in range(D+1):
    print(f"   hop={h}: n={hop_hist[h]}, P = {hop_prob[h]:.4f}")

# ---- 7. 候選身份: 阻挫端點權重 ----
# 阻挫邊端點 = 凝聚燃料位置 — 端點 hop 中位數
frust_node_set = set()
for (u,v) in frust_set:
    frust_node_set.add(u); frust_node_set.add(v)
n_frust_nodes = len(frust_node_set)
print(f"\n7. 阻挫邊端點節點數: {n_frust_nodes}/60")
print(f"   32 條邊 × 2 = 64 端點, 獨特節點 {n_frust_nodes}")

# 檢查: 有冇節點連接 >1 條阻挫邊?
multi = {i: c for i, c in frust_count.items() if c > 1}
print(f"   連接 2 條阻挫邊嘅節點: {len(multi)} 個")
print(f"   連接 0 條: {list(frust_count.values()).count(0)} 個")

# ---- 總判定 ----
results = {
    'mean_hop': float(mean_hop),
    'B': B,
    'diameter': int(D),
    'sym': sym_ok,
    'frust_endpoint_hop_hist': {str(k): v for k, v in sorted(ep_hist.items())},
    'sumW': float(sumW),
    'sum_nE': float(sum_nE),
    'hop_prob': {str(k): round(v, 6) for k, v in hop_prob.items()},
    'n_frust_nodes': n_frust_nodes,
    'multi_frust_nodes': len(multi),
    'zero_frust_nodes': list(frust_count.values()).count(0),
}
with open(f'{OUT_DIR}/02_hierarchy_mapping.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved: {OUT_DIR}/02_hierarchy_mapping.json")

checks = [abs(mean_hop - B) < 1e-9, sym_ok, D == 2*B]
print(f"\n判定: {sum(checks)}/{len(checks)} PASS")
print("PASS" if all(checks) else "FAIL")
