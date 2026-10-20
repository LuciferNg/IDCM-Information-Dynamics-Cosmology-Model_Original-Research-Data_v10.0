#!/usr/bin/env python3
"""
O7 Task 1: 邊類型關聯 — 阻挫邊係咪偏向某種面組合 (Δ-□, ⬠-□, □-□)?
====================================================================
方法:
1. 從 faces.txt 讀取每條邊嘅兩側面類型
2. 分類所有 120 條邊為 Δ-□, ⬠-□, □-□
3. 睇 32 條阻挫邊嘅面類型分佈
4. χ² 檢定 vs 隨機期望
"""
import numpy as np
import math
from collections import defaultdict, Counter

# ============ 1. 載入數據 ============
DATA = "/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data"

# 節點
nodes = []
with open(f"{DATA}/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))

# 阻挫邊
frust_edges = set()
with open(f"{DATA}/frustration_edges.txt") as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split()
        u, v = int(parts[0]), int(parts[1])
        frust_edges.add((u, v) if u < v else (v, u))

# 面資料
edge_faces = defaultdict(list)  # edge -> [(face_type, face_vertices)]
all_faces = []
with open(f"{DATA}/faces.txt") as f:
    for line in f:
        if line.startswith("#"):
            continue
        parts = line.strip().split()
        if not parts:
            continue
        ft = parts[0]  # T, S, P
        vertices = eval(" ".join(parts[1:]).split(" colors=")[0])
        all_faces.append((ft, vertices))
        n = len(vertices)
        for i in range(n):
            e = tuple(sorted((vertices[i], vertices[(i+1) % n])))
            edge_faces[e].append(ft)

print("=" * 70)
print("O7 Task 1: 邊類型關聯分析")
print("=" * 70)

# ============ 2. 所有邊嘅面類型分佈 ============
edge_type_counts = Counter()
edge_type_list = {}  # edge -> type_label
for e, fts in edge_faces.items():
    if len(fts) != 2:
        edge_type_counts[f"??-{''.join(fts)}"] += 1
        edge_type_list[e] = f"??-{''.join(fts)}"
        continue
    # 排序面類型
    t = tuple(sorted(fts))
    labels = {"T": "Δ", "S": "□", "P": "⬠"}
    label = f"{labels[t[0]]}-{labels[t[1]]}"
    edge_type_counts[label] += 1
    edge_type_list[e] = label

print(f"\n📊 全部 120 條邊嘅面類型分佈:")
for t, c in sorted(edge_type_counts.items()):
    pct = c / 120 * 100
    print(f"   {t}: {c} ({pct:.1f}%)")

# ============ 3. 阻挫邊嘅面類型分佈 ============
frust_type_counts = Counter()
frust_details = []
for e in frust_edges:
    t = edge_type_list.get(e, "??")
    frust_type_counts[t] += 1
    u, v = e
    ra_u, dec_u = nodes[u]
    ra_v, dec_v = nodes[v]
    frust_details.append((t, u, v, ra_u, dec_u, ra_v, dec_v))

print(f"\n📊 32 條阻挫邊嘅面類型分佈:")
for t, c in sorted(frust_type_counts.items()):
    pct = c / 32 * 100
    total_t = edge_type_counts.get(t, 0)
    frac = c / total_t if total_t > 0 else 0
    print(f"   {t}: {c} ({pct:.1f}%)  [佔所有 {t} 邊嘅 {frac*100:.1f}%]")

# ============ 4. χ² 檢定 ============
# H0: 阻挫邊嘅面類型分佈 = 全部邊嘅面類型分佈
print(f"\n📐 χ² 檢定 (H0: 阻挫分佈 = 整體分佈):")
expected = {}
for t, total in edge_type_counts.items():
    expected[t] = total / 120 * 32
chi2 = 0
for t in sorted(edge_type_counts.keys()):
    obs = frust_type_counts.get(t, 0)
    exp = expected[t]
    if exp > 0:
        term = (obs - exp) ** 2 / exp
        chi2 += term
        arrow = "↑" if obs > exp else "↓" if obs < exp else "="
        print(f"   {t}: 觀測 {obs:2d} / 期望 {exp:5.1f}  {arrow}  (χ²貢獻={term:.2f})")
    else:
        print(f"   {t}: 觀測 {obs:2d} / 期望 {exp:5.1f}  (無期望)")
from scipy.stats import chi2 as chi2_dist
dof = len([t for t in edge_type_counts if expected[t] > 0]) - 1
p_val = 1 - chi2_dist.cdf(chi2, dof) if dof > 0 else 1.0
print(f"\n   χ² = {chi2:.3f}, dof = {dof}, p = {p_val:.4f}")
if p_val < 0.05:
    print(f"   → p < 0.05: 分佈有顯著偏差 🟡")
else:
    print(f"   → p ≥ 0.05: 未能拒絕 H0 🟢 (分佈無顯著偏差)")

# ============ 5. Fisher Exact Test 逐對 ============
print(f"\n📐 Fisher Exact Test (逐對 vs 其他):")
from scipy.stats import fisher_exact

for t in sorted(edge_type_counts.keys()):
    obs_t = frust_type_counts.get(t, 0)
    other_t = 32 - obs_t
    total_t = edge_type_counts[t]
    other_total = 120 - total_t
    # 2x2 table
    table = [[obs_t, total_t - obs_t],
             [other_t, other_total - (total_t - obs_t)]]
    # 確保所有值 >= 0
    if all(x >= 0 for row in table for x in row):
        odds, p_fish = fisher_exact(table)
        arrow = "↑" if obs_t > total_t/120*32 else "↓"
        sig = "🟡" if p_fish < 0.05 else "🟢"
        print(f"   {t}: OR={odds:.2f}, p={p_fish:.4f} {arrow} {sig}")

# ============ 6. 詳細列出每條阻挫邊 ============
print(f"\n📋 32 條阻挫邊詳細:")
print(f"   {'#':>2} {'類型':>6} {'節點':>8} {'RA1':>8} {'Dec1':>8} {'RA2':>8} {'Dec2':>8}")
print(f"   {'-'*56}")
cold_frust = 0
hot_frust = 0
for i, (t, u, v, ra_u, dec_u, ra_v, dec_v) in enumerate(frust_details):
    color_u = 1  # from anchored_coloring: we'll check
    print(f"   {i+1:>2} {t:>6} ({u:>2},{v:>2}) {ra_u:>8.1f} {dec_u:>8.1f} {ra_v:>8.1f} {dec_v:>8.1f}")

# ============ 7. 冷-冷 vs 熱-熱 嘅邊類型分佈 ============
print(f"\n📊 冷-冷 vs 熱-熱 嘅邊類型分佈:")
# Load coloring
color = {}
with open(f"{DATA}/anchored_coloring.txt") as f:
    f.readline()  # skip header
    for line in f:
        parts = line.strip().split()
        idx, c = int(parts[0]), int(parts[3])
        color[idx] = c

cold_cold_type = Counter()
hot_hot_type = Counter()
for e in frust_edges:
    t = edge_type_list.get(e, "??")
    u, v = e
    if color[u] == 1:  # cold
        cold_cold_type[t] += 1
    else:
        hot_hot_type[t] += 1

print(f"   冷-冷 (16):")
for t, c in sorted(cold_cold_type.items()):
    print(f"      {t}: {c}")
print(f"   熱-熱 (16):")
for t, c in sorted(hot_hot_type.items()):
    print(f"      {t}: {c}")

# 冷-冷 vs 熱-熱 嘅 χ² 檢定
print(f"\n📐 冷-冷 vs 熱-熱 分佈異同檢定:")
all_types = sorted(set(list(cold_cold_type.keys()) + list(hot_hot_type.keys())))
chi2_cross = 0
for t in all_types:
    obs_c = cold_cold_type.get(t, 0)
    obs_h = hot_hot_type.get(t, 0)
    exp_c = (16/32) * (cold_cold_type[t] + hot_hot_type[t]) if (cold_cold_type[t] + hot_hot_type[t]) > 0 else 0
    exp_h = (16/32) * (cold_cold_type[t] + hot_hot_type[t]) if (cold_cold_type[t] + hot_hot_type[t]) > 0 else 0
    if exp_c > 0:
        chi2_cross += (obs_c - exp_c)**2 / exp_c + (obs_h - exp_h)**2 / exp_h
p_cross = 1 - chi2_dist.cdf(chi2_cross, len(all_types) - 1) if len(all_types) > 1 else 1.0
print(f"   χ² = {chi2_cross:.3f}, dof = {len(all_types)-1}, p = {p_cross:.4f}")
if p_cross < 0.05:
    print(f"   → 冷-冷 同 熱-熱 嘅邊類型分佈有顯著差異 🟡")
else:
    print(f"   → 冷-冷 同 熱-熱 嘅邊類型分佈一致 🟢")

# ============ 8. 總結 ============
print(f"\n{'='*70}")
print("📋 總結")
print(f"{'='*70}")
print(f"   全部邊: Δ-□={edge_type_counts.get('Δ-□',0)} ({edge_type_counts.get('Δ-□',0)/120*100:.1f}%), "
      f"⬠-□={edge_type_counts.get('⬠-□',0)} ({edge_type_counts.get('⬠-□',0)/120*100:.1f}%), "
      f"□-□={edge_type_counts.get('□-□',0)} ({edge_type_counts.get('□-□',0)/120*100:.1f}%)")
print(f"   阻挫邊: Δ-□={frust_type_counts.get('Δ-□',0)} ({frust_type_counts.get('Δ-□',0)/32*100:.1f}%), "
      f"⬠-□={frust_type_counts.get('⬠-□',0)} ({frust_type_counts.get('⬠-□',0)/32*100:.1f}%), "
      f"□-□={frust_type_counts.get('□-□',0)} ({frust_type_counts.get('□-□',0)/32*100:.1f}%)")
print(f"   χ² p={p_val:.4f} {'🟡 有偏差' if p_val < 0.05 else '🟢 無顯著偏差'}")
print(f"   冷-冷 vs 熱-熱: p={p_cross:.4f} {'🟡 有差異' if p_cross < 0.05 else '🟢 一致'}")