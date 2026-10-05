#!/usr/bin/env python3
"""GRT-07: 文檔完整性檢查 — 對比文檔宣稱 vs 實際數據."""
import sys
import os
sys.path.insert(0, ".")
from grt_common import (build_graph, compute_frustration_edges,
                        edge_threshold_from_histogram, load_colors, load_nodes)
import numpy as np

OUT = "../data"
DOC = "../docs/01_global_routing_table_record.md"

nodes, vecs = load_nodes()
N = len(nodes)
thresh, dists = edge_threshold_from_histogram(vecs)
adj = build_graph(vecs, thresh)
colors = load_colors()
frust = compute_frustration_edges(adj, colors)
hop = np.load(f"{OUT}/hop_matrix.npy")
next_hop = np.load(f"{OUT}/next_hop_table.npy")
wdelay = np.load(f"{OUT}/weighted_delay_matrix.npy")
ladder = np.load(f"{OUT}/ladder_amplitude.npy")
node_bc = np.load(f"{OUT}/node_betweenness.npy")
edge_bc = np.load(f"{OUT}/edge_betweenness.npy", allow_pickle=True).item()
E = sum(len(s) for s in adj.values()) // 2

# 讀文檔
with open(DOC, encoding="utf-8") as f:
    doc = f.read()

print("=" * 70)
print("文檔完整性檢查 (doc claims vs actual data)")
print("=" * 70)

checks = []

def check(name, actual, doc_contains, fmt=None):
    if fmt:
        shown = fmt.format(actual)
    else:
        shown = str(actual)
    found = shown in doc
    checks.append((name, found, shown))
    status = "✅" if found else "❌ 缺失/錯誤!"
    print(f"  {status} {name}: 實際={shown} | 文檔包含={found}")

# 1. 結構
check("節點數 V", N, "60", "{}")
check("邊數 E", E, "120", "{}")
check("度數", "4-regular", "4-regular")
check("threshold", thresh, "28.923", "{:.3f}")
check("阻挫邊", len(frust), "32", "{}")

# 2. 跳數矩陣
check("直徑", int(hop.max()), "8", "{}")
check("半徑", int(hop.max(axis=1).min()), "8", "{}")
check("冷斑→對跖 hop", int(hop[0,57]), "8", "{}")

# 3. 跳數分佈
hist = {d: int((hop == d).sum()) for d in range(9)}
hist_str = "-".join(str(hist[d]) for d in range(9))
check("跳數分佈", hist_str, "60-240-480-660-720-660-480-240-60")

# 4. 冷斑 BFS 距離分佈
hop0 = {d: int((hop[0] == d).sum()) for d in range(9)}
hop0_str = "-".join(str(hop0[d]) for d in range(9))
check("冷斑 BFS 分佈", hop0_str, "1-4-8-11-12-11-8-4-1")

# 5. 阻挫邊距離範圍
frust_dists = []
for (u, v) in frust:
    dot = np.clip(np.dot(vecs[u], vecs[v]), -1, 1)
    frust_dists.append(np.degrees(np.arccos(dot)))
frust_range = f"{min(frust_dists):.2f}-{max(frust_dists):.2f}"
check("阻挫邊距離", frust_range, frust_range)

# 6. BC 值
frust_bc = [edge_bc.get(str(e), 0) for e in frust]
norm_bc = [edge_bc.get(str((u,v)), 0) for u in range(N) for v in adj[u] if v>u and (u,v) not in frust and (v,u) not in frust]
check("阻挫邊平均 BC", np.mean(frust_bc), "0.031780", "{:.6f}")
check("正常邊平均 BC", np.mean(norm_bc), "0.034669", "{:.6f}")
check("Node BC", node_bc[0], "0.051130", "{:.6f}")

# 7. 加權延遲
check("加權延遲 max", wdelay.max(), "5.4705", "{:.4f}")
check("冷斑→對跖延遲", wdelay[0,57], "5.4705", "{:.4f}")

# 8. 文件存在性
print()
print("檔案存在性檢查:")
files = [
    "data/hop_matrix.npy", "data/path_count_matrix.npy",
    "data/next_hop_table.npy", "data/weighted_delay_matrix.npy",
    "data/ladder_amplitude.npy", "data/edge_betweenness.npy",
    "data/node_betweenness.npy",
    "data/routing_table_plain.txt", "data/directions_1_4_analysis.txt",
    "docs/01_global_routing_table_record.md",
    "scripts/grt_common.py", "scripts/01_hop_matrix.py",
    "scripts/02_routing_table.py", "scripts/03_verify_frustration.py",
    "scripts/04_verify_all.py", "scripts/05_plain_text_routing_table.py",
    "scripts/06_directions_1_4.py",
]
missing = []
for f in files:
    full = os.path.join("..", f)
    if not os.path.exists(full):
        missing.append(f)
        print(f"  ❌ 缺失: {f}")
if not missing:
    print("  ✅ 所有 17 個檔案存在")

# 9. 文檔中遺漏嘅項目
print()
print("文檔遺漏檢查 (有數據但文檔未提及):")
omissions = []
# routing_table_plain.txt 喺文檔 §八 冇列
if "routing_table_plain.txt" not in doc:
    omissions.append("data/routing_table_plain.txt (純文字路由表)")
if "directions_1_4_analysis.txt" not in doc:
    omissions.append("data/directions_1_4_analysis.txt (方向1-4分析)")
if "05_plain_text_routing_table.py" not in doc:
    omissions.append("scripts/05_plain_text_routing_table.py")
if "06_directions_1_4.py" not in doc:
    omissions.append("scripts/06_directions_1_4.py")
if "04_verify_all.py" not in doc:
    omissions.append("scripts/04_verify_all.py")
if "debug_frust.py" not in doc:
    omissions.append("scripts/debug_frust.py (除錯腳本, 可忽略)")
if "Next-Hop" not in doc or "next_hop" not in doc:
    omissions.append("next_hop_table 詳細內容")
if "K_Chain" not in doc:
    omissions.append("K_Chain 融合路由 (方向1)")
if "CMB" not in doc and "160" not in doc:
    omissions.append("CMB 頻率分析 (方向2)")
if "連續" not in doc and "continuous" not in doc:
    omissions.append("連續幅度模型 (方向3)")
if "路由優化" not in doc:
    omissions.append("路由優化分析 (方向4)")

if omissions:
    for o in omissions:
        print(f"  ⚠️ {o}")
else:
    print("  ✅ 無遺漏")

print()
print("=" * 70)
print(f"總結: {sum(1 for _, f, _ in checks if f)}/{len(checks)} 數字檢查通過, "
      f"{len(omissions)} 項遺漏")
print("=" * 70)