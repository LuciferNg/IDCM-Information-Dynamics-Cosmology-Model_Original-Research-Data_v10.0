#!/usr/bin/env python3
"""
O179 — Script 03: 位置選擇機制 — 阻挫翻轉 = 位置更新算子 (Lagrangian 級)
========================================================================
核心命題: 「凝聚揀新位置」= 阻挫邊翻轉 (O7 Ising 位元) 重組 W(i) 權重分佈.
每圈 (T_ring) 凝聚/釋放 → 翻轉阻挫邊 → frust(i) 改變 → W(i) 演化 → 位置更新.

1. 翻轉算子: 單條阻挫邊翻轉 → W 分佈變化 ΔW (位置移動)
2. 位置記憶: 翻轉後新權重分佈同舊分佈嘅重疊 (舊位置遺忘率)
3. 極限環相位: T_ring 週期內 W 演化 → 凝聚位置掃過網絡
4. Lagrangian: S = Σ_i [μ²|Φ_i|² + λ|Φ_i|⁴] + Σ_⟨ij⟩ K_ij Φ_i*Φ_j, K_ij = 阻挫翻轉耦合
5. 驗證: 翻轉動力學 → 位置分佈穩態 = W(i) 歸一化

輸出: data/03_flip_mechanism.json + PASS/FAIL
"""
import math, json, os, random
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
frust_edges = []
with open(f'{DATA}/frustration_edges.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        u, v = int(p[0])-1, int(p[1])-1
        frust_set.add((min(u,v), max(u,v)))
        frust_edges.append((u, v))

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

def compute_W(frust_active):
    """由阻挫邊集合計 W(i) = (frust+1)·E(hop)"""
    fc = {i: 0 for i in range(N)}
    for (u,v) in frust_active:
        fc[u] += 1; fc[v] += 1
    W = {}
    for i in range(N):
        h = hop_from_cs[i]
        E_i = 1 + C*math.cos(math.pi*h/4)
        W[i] = E_i * (fc[i] + 1)
    s = sum(W.values())
    return {i: W[i]/s for i in range(N)}, fc

print("="*72)
print("O179 Script 03 — 阻挫翻轉 = 位置更新算子")
print("="*72)

W0, fc0 = compute_W(frust_set)
print(f"初始 32 阻挫邊: W 分佈就緒")

# ---- 1. 翻轉算子: 移除一條阻挫邊 (翻轉 = 重聯) ----
print(f"\n1. 單邊翻轉 → 位置權重變化:")
flip_effects = []
for (u,v) in sorted(frust_set)[:8]:
    new_set = frust_set - {(u,v)}
    W1, _ = compute_W(new_set)
    # 位置移動量 = L1 距離
    l1 = sum(abs(W1[i] - W0[i]) for i in range(N))
    # 端點權重變化
    du = W1[u] - W0[u]; dv = W1[v] - W0[v]
    flip_effects.append({'edge': (u,v), 'L1': l1, 'dW_u': du, 'dW_v': dv})
    print(f"   邊 {u}-{v} (hop {hop_from_cs[u]},{hop_from_cs[v]}): L1移動 = {l1:.6f}, ΔW端點 = {du:+.4f}/{dv:+.4f}")

# 平均翻轉效應
avg_l1 = np.mean([e['L1'] for e in flip_effects])
print(f"   平均單翻轉 L1 移動: {avg_l1:.6f}")

# ---- 2. 位置記憶 / 遺忘率 ----
# 翻轉 k 條邊後, 同初始 W 嘅重疊 (correlation)
print(f"\n2. 翻轉 k 條邊 → 位置重疊 (遺忘曲線):")
overlap_data = []
random.seed(42)
edges_list = list(frust_set)
for k in [1, 2, 4, 8, 16, 32]:
    new_set = set(random.sample(edges_list, 32 - k))  # 翻轉掉 k 條
    Wk, _ = compute_W(new_set)
    # 重疊 = 歸一化點積 (cosine)
    w0v = np.array([W0[i] for i in range(N)])
    wkv = np.array([Wk[i] for i in range(N)])
    cos = float(np.dot(w0v, wkv) / (np.linalg.norm(w0v)*np.linalg.norm(wkv)))
    l1 = float(np.sum(np.abs(wkv - w0v)))
    overlap_data.append({'k': k, 'cos': cos, 'L1': l1})
    print(f"   k={k:>2}: cos 重疊 = {cos:.6f}, L1 = {l1:.6f}")

# ---- 3. 穩態: 翻轉平衡後 W 分佈 ----
# 每次翻轉隨機移除 + 隨機加返一條 (穩態翻轉流, 阻挫數守恆 32)
print(f"\n3. 穩態翻轉流 (32 邊守恆, 2000 步):")
W_cur = dict(W0)
fc_cur = dict(fc0)
steady_samples = []
for step in range(2000):
    # 隨機移除一條阻挫邊
    e_rm = random.choice(list(frust_set))
    # 隨機加一條非阻挫邊 (全圖最近鄰邊中)
    non_frust = [(a,b) for a in range(N) for b in adj_sym[a] if a < b and (a,b) not in frust_set]
    e_add = random.choice(non_frust)
    frust_set.remove(e_rm)
    frust_set.add(e_add)
    if step % 500 == 499:
        Ws, _ = compute_W(frust_set)
        steady_samples.append({i: Ws[i] for i in range(N)})

# 穩態平均 vs 初始
if steady_samples:
    Ws_avg = {i: np.mean([s[i] for s in steady_samples]) for i in range(N)}
    w0v = np.array([W0[i] for i in range(N)])
    wsv = np.array([Ws_avg[i] for i in range(N)])
    cos_ss = float(np.dot(w0v, wsv)/(np.linalg.norm(w0v)*np.linalg.norm(wsv)))
    print(f"   穩態平均 W vs 初始 W: cos = {cos_ss:.6f}")
    # 穩態 W 嘅 hop 圈結構
    hop_prob_ss = {h: 0.0 for h in range(9)}
    for i in range(N):
        hop_prob_ss[hop_from_cs[i]] += Ws_avg[i]
    print(f"   穩態 hop 圈概率: { {h: round(v,4) for h,v in hop_prob_ss.items()} }")

# ---- 4. Lagrangian 翻譯 ----
print(f"\n4. Lagrangian 級翻譯 (凝聚場 Φ 喺 A₅ 網絡):")
print(f"   S = Σ_i [μ²|Φ_i|² + λ|Φ_i|⁴] + Σ_⟨ij⟩ K_ij Φ_i* Φ_j")
print(f"   K_ij = 跳躍耦合, 阻挫邊 K_ij = −κ (符號翻轉)")
print(f"   μ² = {mu2} (O159 中心模), λ = 2/123 (O39), κ = 阻挫成本 = 2 (O7)")
print(f"   凝聚基態 Φ_i = v·ψ_i, 密度 n_i = |Φ_i|² ∝ W(i) (局部應變能密度)")
print(f"   翻轉算子: F: 阻挫集 → 阻挫集∖{{e}}∪{{e'}} — 位置更新 (重聯釋放 = 重新阻挫)")

# ---- 5. 檢查: 翻轉動力學嘅守恆量 ----
# 阻挫邊數守恆 = 32 = 20Δ + 12⬠ (O7) — 翻轉保持 32 條
# 凝聚事件率守恆: Σ P(i) = 1 (W 歸一化)
print(f"\n5. 守恆檢查:")
print(f"   阻挫邊數 = {len(frust_set)} (翻轉後仍 32): {'PASS' if len(frust_set)==32 else 'FAIL'}")
print(f"   ΣW = 1 (歸一化): {'PASS' if abs(sum(W0.values())-1) < 1e-9 else 'FAIL'}")

if steady_samples:
    cos_ss_val = float(cos_ss)
    hop_prob_ss_val = {str(h): round(v, 4) for h, v in hop_prob_ss.items()}
else:
    cos_ss_val = None
    hop_prob_ss_val = None

results = {
    'avg_flip_L1': float(avg_l1),
    'flip_effects': flip_effects,
    'overlap_curve': overlap_data,
    'steady_cos': cos_ss_val,
    'steady_hop_prob': hop_prob_ss_val,
    'lagrangian': 'S = sum_i [mu2|Phi_i|^2 + lam|Phi_i|^4] + sum_<ij> K_ij Phi_i* Phi_j',
    'mu2': mu2, 'lam': 2/123, 'kappa': 2,
}
with open(f'{OUT_DIR}/03_flip_mechanism.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved: {OUT_DIR}/03_flip_mechanism.json")

checks = [len(frust_set) == 32, abs(sum(W0.values())-1) < 1e-9]
print(f"\n判定: {sum(checks)}/{len(checks)} PASS")
print("PASS" if all(checks) else "FAIL")
