#!/usr/bin/env python3
"""GRT-15: 完整文檔 + 數據驗證 (Final Audit).

驗證所有記錄文檔嘅數字 claim 與實際數據一致.
"""
import sys, os, math
import numpy as np
sys.path.insert(0, ".")
from grt_common import (build_graph, compute_frustration_edges,
                        edge_threshold_from_histogram, load_colors, load_nodes,
                        PHI, PHI_INV, EPS)

OUT = "../data"
DOC1 = "../docs/01_global_routing_table_record.md"
DOC2 = "../docs/02_fusion_and_wfield_record.md"

# 載入數據
nodes, vecs = load_nodes()
N = len(nodes)
thresh, dists = edge_threshold_from_histogram(vecs)
adj = build_graph(vecs, thresh)
colors = load_colors()
frust = compute_frustration_edges(adj, colors)
E = sum(len(s) for s in adj.values()) // 2

hop5 = np.load(f"{OUT}/hop_matrix.npy")
n5 = np.load(f"{OUT}/next_hop_table.npy")
wdelay = np.load(f"{OUT}/weighted_delay_matrix.npy")
ladder = np.load(f"{OUT}/ladder_amplitude.npy")
node_bc = np.load(f"{OUT}/node_betweenness.npy")
edge_bc = np.load(f"{OUT}/edge_betweenness.npy", allow_pickle=True).item()

# Fusion data
fh = np.load(f"{OUT}/fusion_hop_matrix.npy")
fn = np.load(f"{OUT}/fusion_next_hop_table.npy")
fs = np.load(f"{OUT}/fusion_stats.npy")

# 載入文檔
with open(DOC1, encoding="utf-8") as f: d1 = f.read()
with open(DOC2, encoding="utf-8") as f: d2 = f.read()

errors = []
warnings = []
passes = []

def check(name, condition, detail=""):
    if condition:
        passes.append(f"  ✅ {name}: {detail}")
    else:
        errors.append(f"  ❌ {name}: {detail}")

def check_in_doc(doc, name, value, doc_label):
    """檢查 value 嘅 string 表示喺 doc 入面."""
    s = str(value)
    found = s in doc
    label = f"{doc_label}: {name}"
    if found:
        passes.append(f"  ✅ {label}: '{s}' 存在")
    else:
        errors.append(f"  ❌ {label}: '{s}' 不存在 (實際={value})")

def check_files_exist(files, label):
    for f in files:
        full = os.path.join("..", f)
        if os.path.exists(full):
            passes.append(f"  ✅ 檔案存在: {f}")
        else:
            errors.append(f"  ❌ 檔案缺失: {f}")

print("=" * 78)
print("  完整文檔 + 數據驗證 (Final Audit)")
print("=" * 78)

# ====== 1. 檔案存在性 ======
print("\n[1] 檔案存在性檢查:")

check_files_exist([
    "docs/01_global_routing_table_record.md",
    "docs/02_fusion_and_wfield_record.md",
    "data/hop_matrix.npy", "data/next_hop_table.npy",
    "data/weighted_delay_matrix.npy", "data/ladder_amplitude.npy",
    "data/edge_betweenness.npy", "data/node_betweenness.npy",
    "data/path_count_matrix.npy", "data/routing_table_plain.txt",
    "data/directions_1_4_analysis.txt", "data/space_comm_bom.txt",
    "data/wfield_resonance_theory.txt", "data/fusion_hop_matrix.npy",
    "data/fusion_next_hop_table.npy", "data/fusion_routing_plain.txt",
    "data/fusion_stats.npy", "data/frustration_routing_optimization.txt",
    "data/wfield_pde_results.txt",
], "docs/data")

# ====== 2. 圖結構 (文檔 1 §二) ======
print("\n[2] 圖結構驗證 (文檔 1 §二):")
check("V=60", N == 60)
check("E=120", E == 120)
check("deg=4-regular", all(len(adj[i]) == 4 for i in range(N)))
check("threshold=28.923°", abs(thresh - 28.923) < 0.001)
check("frust=32", len(frust) == 32)
check_in_doc(d1, "V=60", 60, "Doc1")
check_in_doc(d1, "E=120", 120, "Doc1")
check_in_doc(d1, "frust=32", 32, "Doc1")

# ====== 3. 跳數矩陣 (文檔 1 §三) ======
print("\n[3] 跳數矩陣驗證 (文檔 1 §三):")
diam5 = int(hop5.max())
check("直徑=8", diam5 == 8)
check("hop[0,57]=8", hop5[0, 57] == 8)
check_in_doc(d1, "直徑=8", 8, "Doc1")

# 跳數分佈
hist = {d: int((hop5 == d).sum()) for d in range(diam5 + 1)}
expected = {0: 60, 1: 240, 2: 480, 3: 660, 4: 720, 5: 660, 6: 480, 7: 240, 8: 60}
check("跳數分佈正確", hist == expected, f"actual={hist}")
check("跳數分佈對稱", all(hist[d] == hist[diam5-d] for d in range(diam5+1)))

# 冷斑 BFS 分佈
hop0 = {d: int((hop5[0] == d).sum()) for d in range(diam5 + 1)}
expected0 = {0: 1, 1: 4, 2: 8, 3: 11, 4: 12, 5: 11, 6: 8, 7: 4, 8: 1}
check("冷斑 BFS 分佈正確", hop0 == expected0, f"actual={hop0}")

# ====== 4. BC 值 (文檔 1 §五) ======
print("\n[4] Betweenness Centrality 驗證 (文檔 1 §五):")
frust_bc = [edge_bc.get(str(e), 0) for e in frust]
norm_bc = [edge_bc.get(str((u,v)), 0) for u in range(N) for v in adj[u] if v>u and (u,v) not in frust and (v,u) not in frust]
check("node BC 全部一致", np.std(node_bc) < 1e-10)
check("node BC = 0.051130", abs(node_bc[0] - 0.051130) < 1e-6)
check("frust BC mean = 0.031780", abs(np.mean(frust_bc) - 0.031780) < 1e-6)
check("norm BC mean = 0.034669", abs(np.mean(norm_bc) - 0.034669) < 1e-6)

# ====== 5. 加權延遲 (文檔 1 §六) ======
print("\n[5] 加權延遲驗證 (文檔 1 §六):")
check("wdelay max = 5.4705", abs(wdelay.max() - 5.4705) < 1e-4)
check("wdelay[0,57] = 5.4705", abs(wdelay[0,57] - 5.4705) < 1e-4)

# ====== 6. 融合路由 (文檔 2) ======
print("\n[6] 融合路由表驗證 (文檔 2):")
NA5, NK, NLOG = 60, 44, 2640
check("fusion hop shape", fh.shape == (NLOG, NLOG), f"shape={fh.shape}")
check("fusion diam = 30", int(fh.max()) == 30)
check("fusion mean = 15.0", abs(fh.mean() - 15.0) < 0.001)
check("fusion symmetric", all(int((fh == d).sum()) == int((fh == 30-d).sum()) for d in range(15)))
check("fusion[0, 57*44+0] = 8", fh[0, 57*NK+0] == 8)
check("fusion[0, 57*44+22] = 30", fh[0, 57*NK+22] == 30)
check_in_doc(d2, "fusion 直徑=30", 30, "Doc2")
check_in_doc(d2, "fusion 節點=2640", 2640, "Doc2")

# ====== 7. Next-hop 路由驗證 (fusion) ======
print("\n[7] Fusion Next-hop 驗證:")
rng = np.random.default_rng(42)
errs = 0
for _ in range(500):
    s = rng.integers(NLOG)
    t = rng.integers(NLOG)
    if s == t: continue
    nh = fn[s, t]
    if nh < 0 or fh[nh, t] != fh[s, t] - 1:
        errs += 1
check("fusion next-hop 500 抽樣", errs == 0, f"errors={errs}")

# ====== 8. 冷斑路由路徑 (文檔 1 §四) ======
print("\n[8] 冷斑路由路徑驗證 (文檔 1 §四):")
path = [0]; cur = 0
while cur != 57:
    nxt = n5[cur, 57]; path.append(nxt); cur = nxt
check("路徑長度 8", len(path) - 1 == 8, f"actual={len(path)-1}")
check("路徑起點 0", path[0] == 0)
check("路徑終點 57", path[-1] == 57)
# 每跳 hop 遞減
ok = all(hop5[path[i], 57] == hop5[path[i-1], 57] - 1 for i in range(1, len(path)))
check("每跳 hop 遞減", ok)

# ====== 9. 阻挫邊距離 (文檔 1 §二) ======
print("\n[9] 阻挫邊距離驗證 (文檔 1 §二):")
frust_dists = []
for (u, v) in frust:
    dot = np.clip(np.dot(vecs[u], vecs[v]), -1, 1)
    frust_dists.append(np.degrees(np.arccos(dot)))
check("所有阻挫邊距離 26.09°±0.08°", all(25.5 < d < 27.0 for d in frust_dists))
check("最小距離", abs(min(frust_dists) - 26.09) < 0.02, f"min={min(frust_dists):.4f}")
check("最大距離", abs(max(frust_dists) - 26.17) < 0.02, f"max={max(frust_dists):.4f}")

# ====== 10. 30 對最遠節點 (文檔 1 §三) ======
print("\n[10] 30 對最遠節點驗證 (文檔 1 §三):")
far = sum(1 for s in range(N) for t in range(s+1, N) if hop5[s, t] == 8)
check("30 對最遠節點", far == 30, f"actual={far}")

# ====== 11. 方向 1-4 分析 (文檔 1 §十) ======
print("\n[11] 方向 1-4 分析驗證 (文檔 1 §十):")
check_in_doc(d1, "CMB 160.40 GHz", "160.40", "Doc1")
check_in_doc(d1, "F5 8.82 MHz", "8.82", "Doc1")
check_in_doc(d1, "F8 37.48 MHz", "37.48", "Doc1")
check_in_doc(d1, "K_Chain 融合", "2640", "Doc1")
check_in_doc(d1, "BOM ~$100K", "100K", "Doc1")

# ====== 12. 文檔 1 引用嘅檔案 ======
print("\n[12] 文檔 1 引用檔案檢查:")
refs = ["hop_matrix.npy", "path_count_matrix.npy", "next_hop_table.npy",
        "weighted_delay_matrix.npy", "ladder_amplitude.npy",
        "edge_betweenness.npy", "node_betweenness.npy",
        "routing_table_plain.txt", "directions_1_4_analysis.txt",
        "fusion_logical_nodes.npy", "space_comm_bom.txt",
        "wfield_resonance_theory.txt", "fusion_hop_matrix.npy",
        "fusion_next_hop_table.npy", "fusion_stats.npy",
        "fusion_routing_plain.txt"]
for ref in refs:
    if ref in d1:
        passes.append(f"  ✅ Doc1 引用: {ref}")
    else:
        warnings.append(f"  ⚠️ Doc1 未引用: {ref}")

# ====== 13. 文檔 2 引用嘅檔案 ======
print("\n[13] 文檔 2 引用檔案檢查:")
refs2 = ["fusion_hop_matrix.npy", "fusion_next_hop_table.npy",
         "fusion_routing_plain.txt", "fusion_stats.npy",
         "wfield_resonance_theory.txt", "space_comm_bom.txt"]
for ref in refs2:
    if ref in d2:
        passes.append(f"  ✅ Doc2 引用: {ref}")
    else:
        warnings.append(f"  ⚠️ Doc2 未引用: {ref}")

# ====== 14. W-field PDE 結果 ======
print("\n[14] W-field PDE 結果驗證:")
arrival = np.load(f"{OUT}/wfield_pde_arrival.npy")
check("PDE arrival shape", arrival.shape == (60,))
check("PDE 所有非源節點到達", (arrival[1:] > 0).all(), f"sum(arrival<=0)={int((arrival<=0).sum())}")
# 相關性
hop_dists = hop5[0]
valid = (arrival > 0) & (hop_dists > 0)
corr = np.corrcoef(arrival[valid], hop_dists[valid])[0, 1]
check("PDE-hop 相關性 > 0.99", corr > 0.99, f"r={corr:.4f}")

# ====== 總結 ======
print("\n" + "=" * 78)
print(f"  驗證總結: {len(passes)} 通過, {len(errors)} 錯誤, {len(warnings)} 警告")
print("=" * 78)
for p in passes: print(p)
for w in warnings: print(w)
for e in errors: print(e)

# 寫入報告
with open(f"{OUT}/final_audit_report.txt", "w", encoding="utf-8") as f:
    f.write(f"驗證總結: {len(passes)} 通過, {len(errors)} 錯誤, {len(warnings)} 警告\n")
    for p in passes: f.write(p + "\n")
    for w in warnings: f.write(w + "\n")
    for e in errors: f.write(e + "\n")
print(f"\n✅ 已寫入: {OUT}/final_audit_report.txt")