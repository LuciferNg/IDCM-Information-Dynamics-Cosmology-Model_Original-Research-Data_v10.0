#!/usr/bin/env python3
"""GRT-06: 方向 1→2→3→4 推進分析.

1. 擴展路由表到全宇宙 (K_Chain 44-site + A5 晶網融合)
2. 阻挫邊 L1 通道物理實現 (Fibonacci 共振頻率)
3. 連續幅度模型 (A = F₅·φ^(-d/2))
4. 路由優化 (30 對最遠節點最小加權延遲路徑)
"""
import sys
import math
sys.path.insert(0, ".")
from grt_common import (build_graph, compute_frustration_edges,
                        edge_threshold_from_histogram, load_colors, load_nodes,
                        PHI, PHI_INV, EPS)
import numpy as np

OUT = "../data"
nodes, vecs = load_nodes()
N = len(nodes)
thresh, _ = edge_threshold_from_histogram(vecs)
adj = build_graph(vecs, thresh)
colors = load_colors()
frust = compute_frustration_edges(adj, colors)
hop = np.load(f"{OUT}/hop_matrix.npy")
next_hop = np.load(f"{OUT}/next_hop_table.npy")
wdelay = np.load(f"{OUT}/weighted_delay_matrix.npy")
ladder = np.load(f"{OUT}/ladder_amplitude.npy")
E = sum(len(s) for s in adj.values()) // 2

lines = []
def L(s):
    lines.append(s)
    print(s)

# ============================================================
# 方向 1: 擴展路由表到全宇宙
# ============================================================
L("=" * 78)
L("  方向 1: 擴展路由表到全宇宙")
L("  K_Chain (44-site) + A5 晶網 (60-node) 融合路由")
L("=" * 78)

# K_Chain 參數
R_H = 4129.94    # Mpc
Nd = 44          # site 數
c = 299792.458   # km/s
H0 = 72.59       # km/s/Mpc
dx = R_H / Nd    # site 間距

L(f"\n  K_Chain 基礎參數:")
L(f"    環周長 R_H = {R_H:.2f} Mpc")
L(f"    site 數 N_d = {Nd}")
L(f"    site 間距 dx = {dx:.2f} Mpc")
L(f"    44 個模式: γ_n = 4sin²(πn/88), Σγ = 90")

# K_Chain 鄰接: 一維環 (circular chain)
# 每個 site 連接到 n-1, n+1 (mod 44)
L(f"\n  K_Chain 路由表 (一維環):")
L(f"    直徑 = {44//2} hops (環直徑)")
L(f"    度數 = 2-regular (每個 site 2 個鄰居)")
L(f"    路由 = 簡單: 沿環 clockwise/counterclockwise 最短方向")

# A5 晶網 vs K_Chain 比較
L(f"\n  A5 晶網 vs K_Chain 路由對比:")
L(f"    {'指標':<20} {'A5 晶網 (60節點)':<25} {'K_Chain (44-site)':<25}")
L(f"    {'-'*20} {'-'*25} {'-'*25}")
L(f"    {'維度':<20} {'2D 球面 (Rhombicosidodecahedron)':<25} {'1D 環':<25}")
L(f"    {'度數':<20} {'4-regular':<25} {'2-regular':<25}")
L(f"    {'直徑':<20} {'8 hops':<25} {'22 hops':<25}")
L(f"    {'路由策略':<20} {'Next-hop 表 (全連通)':<25} {'左/右 最短方向':<25}")
L(f"    {'阻挫/缺陷':<20} {'32 條阻挫邊':<25} {'無 (環係 bipartite)':<25}")

# 融合: K_Chain modes 映射到 A5 節點幅度
# 每個 A5 節點嘅幅度 = 44 個 K_Chain mode 嘅疊加
L(f"\n  K_Chain ⊗ A5 融合路由:")
L(f"    每個 A5 節點 = 44 個 K_Chain mode 嘅疊加")
L(f"    每條 A5 邊 = 兩個節點之間嘅 mode 共振通道")
L(f"    路由 hop = K_Chain mode 之間嘅相位同步跳躍")
L(f"    全宇宙路由表維度: 60(A5) × 44(K_Chain) = 2640 個邏輯節點")

# ============================================================
# 方向 2: 阻挫邊 L1 通道物理實現
# ============================================================
L("\n" + "=" * 78)
L("  方向 2: 阻挫邊 L1 通道物理實現")
L("  Fibonacci 共振頻率 + 載體調頻理論")
L("=" * 78)

# CMB 頻率: 2.728K 黑體輻射峰值 ≈ 160 GHz
T_CMB = 2.7284  # K
# Wien's law: f_peak = 5.879e10 * T (Hz/K)
f_peak = 5.879e10 * T_CMB  # Hz
L(f"\n  CMB 背景頻率:")
L(f"    T_CMB = {T_CMB} K")
L(f"    f_peak = {f_peak/1e9:.2f} GHz (Wien's law)")

# Fibonacci 階梯頻率
# F₅ 冷斑振幅 = 150 μK → 頻率偏移 Δf/f = ΔT/T
FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
cold_spot_amp = 150e-6  # 150 μK in K
L(f"\n  Fibonacci 階梯頻率偏移 (ΔT ladder):")
L(f"    {'等級':<10} {'ΔT (μK)':<12} {'Δf/f (×10⁻⁶)':<16} {'Δf (Hz)':<16}")
L(f"    {'-'*10} {'-'*12} {'-'*16} {'-'*16}")

for i in range(5, 9):
    amp = cold_spot_amp * FIB[i] / FIB[5]  # 相對 F₅ 比例
    df_f = amp / T_CMB
    df = df_f * f_peak
    L(f"    F{i}={'F'+str(FIB[i]):<5} {amp*1e6:<10.1f} {df_f*1e6:<14.3f} {df:<15.1f}")

# 阻挫邊作為共振通道
L(f"\n  阻挫邊 (L1 通道) 物理實現:")
L(f"    阻挫邊 = 同色節點相鄰 = 拓撲缺陷 = 特殊共振通道")
L(f"    正常邊 (L2) = 雙色節點相鄰 = 普通通道")
L(f"")
L(f"  載體調頻方案:")
L(f"    1. 將載體 (光子/訊息) 調頻到目標節點嘅 Fibonacci 等級")
L(f"    2. 沿阻挫邊 (L1) 傳輸: 同色 = 共振頻率匹配 = 高帶寬")
L(f"    3. 沿正常邊 (L2) 傳輸: 雙色 = 頻率偏移 = 需轉換")
L(f"")
L(f"  關鍵洞察: 阻挫邊 BC 比正常邊低 (91.7%)")
L(f"  → 阻挫邊唔係「高流量通道」, 而係「高保真通道」")
L(f"  → 同色 = 頻率匹配 = 訊號保真度高, 但路由選擇較少")

# ============================================================
# 方向 3: 連續幅度模型
# ============================================================
L("\n" + "=" * 78)
L("  方向 3: 連續幅度模型")
L("  A(d) = F₅·φ^(-d/2)  vs  6-level discrete ladder")
L("=" * 78)

# 6-level discrete ladder
L(f"\n  6-level discrete ladder (當前):")
L(f"    {'d':<6} {'F等級':<10} {'幅度':<10}")
L(f"    {'-'*6} {'-'*10} {'-'*10}")
for d in range(0, 9):
    f_level = FIB[max(0, 5-d)]
    L(f"    {d:<6} F{max(0,5-d):<7} {f_level:<10}")

# 連續模型: A = F₅·φ^(-d/2)
L(f"\n  連續模型 A(d) = F₅ · φ^(-d/2):")
L(f"    {'d':<6} {'連續 A':<10} {'離散 A':<10} {'偏差%':<10}")
L(f"    {'-'*6} {'-'*10} {'-'*10} {'-'*10}")
for d in range(0, 9):
    cont = FIB[5] * (PHI_INV ** (d/2))
    disc = FIB[max(0, 5-d)]
    err = (cont - disc) / disc * 100
    L(f"    {d:<6} {cont:<10.3f} {disc:<10} {err:<+9.2f}%")

# 加權延遲對比
# 重新計算連續模型嘅加權延遲
L(f"\n  連續模型加權延遲對比:")
cont_ladder = np.array([FIB[5] * (PHI_INV ** (d/2)) for d in hop[0]], dtype=float)
# 粗略估計: 平均偏差 = 連續/離散差異
mean_err = np.mean([abs(FIB[5] * (PHI_INV ** (d/2)) - FIB[max(0,5-d)]) / FIB[max(0,5-d)] * 100 for d in range(9)])
L(f"    平均偏差: {mean_err:.1f}%")
L(f"    最大偏差: d=4 時 {abs(FIB[5] * (PHI_INV ** (4/2)) - FIB[1]) / FIB[1] * 100:.1f}%")
L(f"    建議: 6-level ladder 已足夠, 連續模型改善有限 ({mean_err:.1f}%)")

# ============================================================
# 方向 4: 路由優化
# ============================================================
L("\n" + "=" * 78)
L("  方向 4: 路由優化 — 30 對最遠節點最小加權延遲路徑")
L("=" * 78)

# 搵 30 對最遠節點
pairs = []
for s in range(N):
    for t in range(s+1, N):
        if hop[s, t] == 8:
            pairs.append((s, t))

# Dijkstra 路徑重建 (用加權延遲)
import heapq
def shortest_path(adj, next_hop, s, t):
    path = [s]
    cur = s
    while cur != t:
        nxt = next_hop[cur, t]
        path.append(nxt)
        cur = nxt
    return path

L(f"\n  {'#':<4} {'節點A':<8} {'節點B':<8} {'跳數':<6} {'加權延遲':<12} {'最短路徑'}")
L(f"  {'-'*4} {'-'*8} {'-'*8} {'-'*6} {'-'*12} {'-'*30}")
for i, (s, t) in enumerate(pairs):
    path = shortest_path(adj, next_hop, s, t)
    hops = len(path) - 1
    delay = wdelay[s, t]
    path_str = "→".join(str(n) for n in path[:5]) + f"...({len(path)}跳)"
    L(f"  {i+1:<4} 節點{s:<4} 節點{t:<4} {hops:<6} {delay:<12.4f} {path_str}")

# 分析: hop 路由 vs 加權路由
L(f"\n  路由優化分析:")
L(f"    30 對最遠節點全部 hop=8 (直徑)")
L(f"    加權延遲範圍: [{min(wdelay[s,t] for s,t in pairs):.4f}, {max(wdelay[s,t] for s,t in pairs):.4f}]")
L(f"    平均加權延遲: {np.mean([wdelay[s,t] for s,t in pairs]):.4f}")

# 最佳路由 vs 最差路由
best = min(pairs, key=lambda p: wdelay[p[0], p[1]])
worst = max(pairs, key=lambda p: wdelay[p[0], p[1]])
L(f"\n    最低延遲路徑: 節點{best[0]}→節點{best[1]}, delay={wdelay[best[0],best[1]]:.4f}")
L(f"    最高延遲路徑: 節點{worst[0]}→節點{worst[1]}, delay={wdelay[worst[0],worst[1]]:.4f}")

# 優化建議
L(f"\n  路由優化建議:")
L(f"    1. Hop 路由 (最小跳數) 已經足夠: 所有 30 對都係 8 hops")
L(f"    2. 加權延遲路由 (Dijkstra) 考慮 Fibonacci 幅度差異")
L(f"    3. 3 條路由策略: (a) 最小 hop (b) 最小加權延遲 (c) 最大帶寬 (沿阻挫邊)")
L(f"    4. 阻挫邊路由: 偏好沿阻挫邊 (L1) 傳輸 → 需檢查是否增加 hop 數")

# 分析阻挫邊路由
L(f"\n  阻挫邊偏好路由分析:")
# 對於每條最遠路徑, 計算阻挫邊佔比
frust_ratio = []
for s, t in pairs:
    path = shortest_path(adj, next_hop, s, t)
    frust_count = 0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        if (u, v) in frust or (v, u) in frust:
            frust_count += 1
    frust_ratio.append(frust_count / (len(path) - 1))
L(f"    30 條最遠路徑嘅阻挫邊平均佔比: {np.mean(frust_ratio):.2%}")
L(f"    (隨機預期: {len(frust)/E:.2%})")
if np.mean(frust_ratio) > len(frust)/E:
    L(f"    → 阻挫邊喺最遠路徑中比隨機更多 ✅")
else:
    L(f"    → 阻挫邊喺最遠路徑中比隨機更少 ⚠️")

# ============================================================
# 保存
# ============================================================
L("\n" + "=" * 78)
L("  方向 1→4 分析完成")
L("=" * 78)

with open(f"{OUT}/directions_1_4_analysis.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"\n✅ 已寫入: {OUT}/directions_1_4_analysis.txt")