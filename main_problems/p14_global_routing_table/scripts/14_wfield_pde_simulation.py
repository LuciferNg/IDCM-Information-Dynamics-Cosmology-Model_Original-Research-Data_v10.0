#!/usr/bin/env python3
"""GRT-14: W-field PDE 數值模擬 — 路由表驗證.

W-field 離散方程:
  Φ_i(t+1) - 2Φ_i(t) + Φ_i(t-1) = Σ_j K_ij Φ_j(t) - φ Φ_i(t)

模擬目標:
1. 喺 A5 晶網上注入脈衝, 追蹤傳播時間
2. 驗證 PDE 傳播速度 = 路由表 hop 距離
3. 阻挫邊 vs 正常邊嘅傳播特性
4. K_Chain 44 mode 共振響應
"""
import sys, os
import numpy as np
sys.path.insert(0, ".")
from grt_common import (build_graph, compute_frustration_edges,
                        edge_threshold_from_histogram, load_colors, load_nodes,
                        PHI, PHI_INV, EPS)

OUT = "../data"
os.makedirs(OUT, exist_ok=True)

nodes, vecs = load_nodes()
N = len(nodes)
thresh, _ = edge_threshold_from_histogram(vecs)
adj = build_graph(vecs, thresh)
colors = load_colors()
frust = compute_frustration_edges(adj, colors)
hop = np.load(f"{OUT}/hop_matrix.npy")
E = sum(len(s) for s in adj.values()) // 2

# K_ij 耦合矩陣: 鄰接 + 自身 φ 項
# W-field: K_ij = 1 if (i,j) edge, else 0
# 但 K_chain 分解: K = K_chain ⊗ K_tree, 呢度用 A5 鄰接近似
K = np.zeros((N, N))
for i in range(N):
    for j in adj[i]:
        K[i, j] = 1.0

# 阻尼項 (Hubble damping)
H0 = 0.01  # Hubble 阻尼係數 (from wfield PDE skill)
DT = 0.1   # 時間步長
STEPS = 5000  # 總步數

lines = []; L = lambda s: (lines.append(s), print(s))
L("=" * 78)
L("  W-field PDE 數值模擬 — A5 晶網傳播驗證")
L("=" * 78)
L(f"  節點: {N} | 邊: {E} | 阻挫邊: {len(frust)}")
L(f"  DT: {DT} | 步數: {STEPS} | Hubble 阻尼: {H0}")

# 初始化: 喺節點 0 (冷斑) 注入脈衝
Phi = np.zeros((N, STEPS + 2))
Phi_prev = np.zeros(N)
Phi_curr = np.zeros(N)
Phi_curr[0] = 1.0  # 脈衝

# 傳播時間記錄
arrival = np.full(N, -1, dtype=int)
arrival[0] = 0

# 時間疊代
for t in range(STEPS):
    # W-field 方程
    laplacian = K @ Phi_curr  # Σ_j K_ij Φ_j
    Phi_next = 2*Phi_curr - Phi_prev + DT**2 * (laplacian - PHI * Phi_curr - H0 * (Phi_curr - Phi_prev) / DT)
    Phi_prev = Phi_curr.copy()
    Phi_curr = Phi_next.copy()
    
    # 記錄到達時間 (能量 > 0.01)
    for i in range(N):
        if arrival[i] == -1 and abs(Phi_curr[i]) > 0.01:
            arrival[i] = t + 1

# 結果
L(f"\n  PDE 傳播到達時間 vs 路由表 hop 距離:")
L(f"  {'節點':<6} {'PDE 到達(步)':<15} {'路由 hop':<10} {'比例':<10}")
L(f"  {'-'*6} {'-'*15} {'-'*10} {'-'*10}")

# 對比 PDE 到達時間 vs 路由表 hop
valid = [(i, arrival[i]) for i in range(N) if arrival[i] > 0]
if valid:
    for i, a in sorted(valid, key=lambda x: hop[0, x[0]]):
        ratio = a / hop[0, i] if hop[0, i] > 0 else 0
        L(f"  節點{i:<3} {a:<15} {hop[0,i]:<10} {ratio:<10.2f}")

# 相關性分析: PDE 到達時間 vs hop 距離
arrival_times = np.array([arrival[i] for i in range(N)])
hop_dists = hop[0]
valid_mask = (arrival_times > 0) & (hop_dists > 0)
corr = np.corrcoef(arrival_times[valid_mask], hop_dists[valid_mask])[0, 1]
L(f"\n  相關係數 (PDE 到達 vs hop 距離): {corr:.4f}")

# 阻挫邊 vs 正常邊傳播特性
L(f"\n  阻挫邊傳播特性:")
# 搵兩條阻挫邊同正常邊做對比
frust_samples = list(frust)[:3]
norm_samples = []
for u in range(N):
    for v in adj[u]:
        if v > u and (u,v) not in frust and (v,u) not in frust:
            norm_samples.append((u,v))
            if len(norm_samples) >= 3: break
    if len(norm_samples) >= 3: break

for (u,v) in frust_samples:
    L(f"  阻挫邊 ({u},{v}): 兩端到達時間 {arrival[u]}-{arrival[v]}, 差={abs(arrival[u]-arrival[v])}")
for (u,v) in norm_samples:
    L(f"  正常邊 ({u},{v}): 兩端到達時間 {arrival[u]}-{arrival[v]}, 差={abs(arrival[u]-arrival[v])}")

# K_Chain 44 mode 共振響應
L(f"\n  K_Chain 44 mode 共振頻譜:")
nk = 44
omega_scale = 88 * 299792.458 * 1e3 / (4129.94 * 3.085677581e19 * 1e3)
# 模擬: 對 Phi 做 FFT 睇頻譜
fft_vals = np.abs(np.fft.fft(Phi_curr[:1000]))[:100]
peaks = np.argsort(fft_vals)[-5:][::-1]
L(f"  訊號能量前 5 峰值頻率: {peaks}")
L(f"  (理想: 應該對應 K_Chain mode 頻率)")

# 結論
L(f"\n  結論:")
L(f"  1. PDE 傳播時間與路由表 hop 距離相關性: r={corr:.4f}")
L(f"  2. {'W-field PDE 驗證了路由表 hop 距離! ✅' if corr > 0.5 else 'W-field PDE 與 hop 距離相關性較弱, 需要進一步調參 ⚠️'}")
L(f"  3. 阻挫邊傳播特性: 需要更多分析")
L(f"  4. K_Chain 共振: 初步檢測")

np.save(f"{OUT}/wfield_pde_arrival.npy", arrival)
np.save(f"{OUT}/wfield_pde_signal.npy", Phi_curr)
with open(f"{OUT}/wfield_pde_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"\n✅ 已寫入: {OUT}/wfield_pde_results.txt")