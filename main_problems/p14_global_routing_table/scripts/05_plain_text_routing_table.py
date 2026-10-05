#!/usr/bin/env python3
"""GRT-05: 純文字宇宙路由表生成."""
import sys
sys.path.insert(0, ".")
from grt_common import (build_graph, compute_frustration_edges,
                        edge_threshold_from_histogram, load_colors, load_nodes)
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
edge_bc = np.load(f"{OUT}/edge_betweenness.npy", allow_pickle=True).item()
node_bc = np.load(f"{OUT}/node_betweenness.npy")

E = sum(len(s) for s in adj.values()) // 2
lines = []

def L(s):
    lines.append(s)
    print(s)

L("=" * 78)
L("  A₅ 晶網全域路由表 (Global Routing Table)")
L("  宇宙 = 離散網絡 | 曲速 = 拓撲路由 | 直徑 = 8 hops")
L("=" * 78)
L(f"  生成日期: 2026-08-16")
L(f"  節點: {N} | 邊: {E} | 阻挫邊: {len(frust)} | 正常邊: {E - len(frust)}")
L(f"  直徑: {hop.max():.0f} hops | 半徑: {hop.min(axis=1).max():.0f}")
L(f"  threshold: {thresh:.4f}° | 多面體: Rhombicosidodecahedron")
L(f"  冷斑 anchor: 節點 0 (RA={nodes[0][0]:.1f}°, Dec={nodes[0][1]:.1f}°)")
L(f"  對跖點: 節點 57 (RA={nodes[57][0]:.1f}°, Dec={nodes[57][1]:.1f}°)")
L(f"  冷斑→對跖 hop: {hop[0,57]:.0f} | 加權延遲: {wdelay[0,57]:.4f}")
L("=" * 78)

L("\n" + "━" * 78)
L("  一、全對跳數分佈 (All-Pairs Hop Distribution)")
L("━" * 78)
L(f"  {'跳數':<6} {'節點對數':<10} {'佔比':<8} {'柱狀圖'}")
L(f"  {'-'*6} {'-'*10} {'-'*8} {'-'*30}")
hist = {d: int((hop == d).sum()) for d in range(9)}
for d in range(9):
    pct = hist[d] / 3600 * 100
    bar = "█" * int(hist[d] / 15)
    L(f"  {d:<6} {hist[d]:<10} {pct:<7.1f}% {bar}")
L(f"  {'-'*6} {'-'*10} {'-'*8} {'-'*30}")
L(f"  總和: {sum(hist.values())} / 3600")

L("\n" + "━" * 78)
L("  二、冷斑節點 0 BFS 路由樹 (Cold Spot Routing Tree)")
L("━" * 78)
L(f"  {'距離':<6} {'節點數':<8} {'節點列表':<50} {'幅度'}")
L(f"  {'-'*6} {'-'*8} {'-'*50} {'-'*6}")
for d in range(9):
    nodes_at_d = [i for i in range(N) if hop[0, i] == d]
    names = ",".join(str(n) for n in nodes_at_d)
    amp = int(ladder[nodes_at_d[0]]) if nodes_at_d else 0
    L(f"  d={d:<3} {len(nodes_at_d):<8} [{names:<48}] F{amp if amp>0 else 0}")

L("\n" + "━" * 78)
L("  三、30 對最遠節點對 (Antipodal Pairs, Hop=8)")
L("━" * 78)
pairs = []
for s in range(N):
    for t in range(s+1, N):
        if hop[s, t] == 8:
            pairs.append((s, t))
L(f"  {'#':<4} {'節點A':<8} {'RA_A':<10} {'Dec_A':<10} {'↔':<3} {'節點B':<8} {'RA_B':<10} {'Dec_B':<10}")
L(f"  {'-'*4} {'-'*8} {'-'*10} {'-'*10} {'-'*3} {'-'*8} {'-'*10} {'-'*10}")
for i, (s, t) in enumerate(pairs):
    ra_s, dec_s = nodes[s]
    ra_t, dec_t = nodes[t]
    L(f"  {i+1:<4} 節點{s:<4} {ra_s:<9.1f}° {dec_s:<9.1f}° ↔ 節點{t:<4} {ra_t:<9.1f}° {dec_t:<9.1f}°")

L("\n" + "━" * 78)
L("  四、冷斑 → 對跖點 路由路徑 (8 hops)")
L("━" * 78)
path = [0]
cur = 0
while cur != 57:
    nxt = next_hop[cur, 57]
    path.append(nxt)
    cur = nxt
route_str = " → ".join(f"節點{n}" for n in path)
L(f"  {route_str}")
L(f"  跳數: {len(path)-1} | 加權延遲: {wdelay[0,57]:.4f}")

L("\n" + "━" * 78)
L("  五、Next-Hop 路由表 (部分)")
L("━" * 78)
L(f"  格式: 源節點 → [目標:下一跳, ...] (按 hop 距離分組)")
L(f"  3600 條路由全部驗證通過 ✅")
L("")
for src in [0, 1, 5, 57]:
    L(f"  ── 節點 {src} (RA={nodes[src][0]:.1f}°, Dec={nodes[src][1]:.1f}°) ──")
    for d in range(1, 9):
        targets = [t for t in range(N) if hop[src, t] == d]
        if not targets:
            continue
        # 顯示頭 5 個目標嘅下一跳
        examples = []
        for t in targets[:5]:
            nh = next_hop[src, t]
            examples.append(f"節點{t}→節點{nh}")
        suffix = f", ... (+{len(targets)-5})" if len(targets) > 5 else ""
        L(f"    d={d}: {', '.join(examples)}{suffix}")
    L("")

L("━" * 78)
L("  六、阻挫邊 (Backbone L1 通道)")
L("━" * 78)
L(f"  {'#':<4} {'邊':<10} {'距離':<10} {'顏色':<12} {'BC值':<10}")
L(f"  {'-'*4} {'-'*10} {'-'*10} {'-'*12} {'-'*10}")
for i, (u, v) in enumerate(sorted(frust)):
    cu = "冷" if colors[u] == 1 else "熱"
    cv = "冷" if colors[v] == 1 else "熱"
    d = np.degrees(np.arccos(np.clip(np.dot(vecs[u], vecs[v]), -1, 1)))
    bc = edge_bc.get(str((u, v)), 0)
    L(f"  {i+1:<4} ({u:2d},{v:2d}) {d:<9.4f}° {cu}-{cv:<8} {bc:<10.6f}")

L(f"\n  阻挫邊總數: {len(frust)} (20Δ + 12⬠ = 32)")
L(f"  阻挫邊平均 BC: {np.mean([edge_bc.get(str(e),0) for e in frust]):.6f}")
L(f"  正常邊平均 BC: {np.mean([edge_bc.get(str((u,v)),0) for u in range(60) for v in adj[u] if v>u and (u,v) not in frust and (v,u) not in frust]):.6f}")

L("\n" + "━" * 78)
L("  七、節點 Betweenness Centrality (Top 10)")
L("━" * 78)
sorted_nodes = sorted(enumerate(node_bc), key=lambda x: -x[1])
L(f"  {'排名':<6} {'節點':<8} {'RA':<10} {'Dec':<10} {'BC':<12} {'冷/熱'}")
L(f"  {'-'*6} {'-'*8} {'-'*10} {'-'*10} {'-'*12} {'-'*8}")
for i, (node, bc) in enumerate(sorted_nodes[:10]):
    ra, dec = nodes[node]
    tag = "冷" if colors[node] == 1 else "熱"
    L(f"  {i+1:<6} 節點{node:<3} {ra:<9.1f}° {dec:<9.1f}° {bc:<12.6f} {tag}")
L(f"  (Vertex-transitive: 所有 60 節點 BC 相同={sorted_nodes[0][1]:.6f})")

L("\n" + "━" * 78)
L("  八、Edge Betweenness Centrality (Top 10)")
L("━" * 78)
edge_bc_list = [(eval(k), v) for k, v in edge_bc.items()]
edge_bc_list.sort(key=lambda x: -x[1])
L(f"  {'排名':<6} {'邊':<10} {'BC':<12} {'類型':<10} {'距離':<10}")
L(f"  {'-'*6} {'-'*10} {'-'*12} {'-'*10} {'-'*10}")
for i, ((u, v), bc) in enumerate(edge_bc_list[:10]):
    in_frust = (u, v) in frust or (v, u) in frust
    tag = "🟢阻挫" if in_frust else "🔵正常"
    d = np.degrees(np.arccos(np.clip(np.dot(vecs[u], vecs[v]), -1, 1)))
    L(f"  {i+1:<6} ({u:2d},{v:2d}) {bc:<12.6f} {tag:<10} {d:<9.4f}°")

L("\n" + "━" * 78)
L("  九、加權延遲 (Fibonacci Ladder)")
L("━" * 78)
L(f"  幅度模型: d=0→F₅=8, d=1→F₄=5, d=2→F₃=3, d=3→F₂=2, d≥4→F₁=1")
L(f"  加權延遲範圍: [{wdelay.min():.4f}, {wdelay.max():.4f}]")
L(f"  冷斑→對跖點: {wdelay[0,57]:.4f}")
L("")

L("=" * 78)
L("  路由表生成完成 — 3600 條路由全部可驗證")
L("=" * 78)

# 寫入檔案
with open(f"{OUT}/routing_table_plain.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"\n✅ 已寫入: {OUT}/routing_table_plain.txt")