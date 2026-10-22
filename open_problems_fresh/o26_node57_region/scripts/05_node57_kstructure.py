#!/usr/bin/env python3
"""
05_node57_kstructure.py — O26 衍生: k 值結構 (frustration degree) 一次過分析
=============================================================================
問題: ΔE=0 節點 (k=2) 形成 6 對近對徑對 — 幾何必然定巧合?

核心工具: anchored_coloring.txt 最後一欄 = frustration 鄰居數 (k 值)
- k=0: 冇 frustration 邊
- k=1: 1 條 frustration 邊
- k=2: 2 條 frustration 邊 (= ΔE=0 節點, 零能量寫入)

分析:
1. k 值全表 + 分佈
2. 30 對近對徑嘅 k 值對稱性 (k_i = k_j?)
3. k=2 節點成對 — 幾何必然? (random 對照)
4. k=0 節點 (8 個) 嘅對徑結構 — 冷斑 node 0 同 node 57 都係 k=0!
5. ΔE=0 對 |ΔT| vs 其他 (T_local 版本)
6. k=0/1/2 嘅溫度統計 (|T| mean)
7. 冷斑↔對徑: 兩個 k=0 節點嘅對徑對
"""
import numpy as np
import math
import os
import healpy as hp
from collections import defaultdict
from scipy import stats

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
OUT = os.path.join(BASE, "o26_node57_region", "data")
rng = np.random.default_rng(2605)

# ============ 載入 ============
# k 值 (frustration neighbors)
k_val = {}
color = {}
with open(f"{BASE}/cmb_cold_spot/data/anchored_coloring.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        idx, ra, dec, c, fr = int(p[0]), float(p[1]), float(p[2]), int(p[3]), int(p[4])
        k_val[idx] = fr
        color[idx] = c

# 節點向量
nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])

# 溫度
rows = []
with open(f"{BASE}/o3_node_temperatures/data/node_temps.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        rows.append((int(p[0]), int(p[1]), float(p[2]), float(p[3]), float(p[4]), int(p[5])))
T = np.array([r[2] for r in rows])
hop = np.array([r[5] for r in rows])

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line)
    results.append(line)

log("=" * 72)
log("O26 衍生: k 值結構 (frustration degree) 一次過分析")
log("=" * 72)

# ============ 1. k 值全表 + 分佈 ============
log("\n=== 1. k 值分佈 ===")
k_dist = defaultdict(list)
for i in range(60):
    k_dist[k_val[i]].append(i)
for k in sorted(k_dist):
    nodes_k = sorted(k_dist[k])
    log(f"  k={k}: {len(nodes_k)} 節點 -> {nodes_k}")
log(f"  合計: {sum(len(v) for v in k_dist.values())}/60")

# ============ 2. 30 對近對徑嘅 k 值對稱性 ============
log("\n=== 2. 30 對近對徑 k 值對稱性 ===")
pairs = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang > 170:
            pairs.append((ang, i, j))
pairs.sort(reverse=True)
same_k = 0
k2_pairs = []
k0_pairs = []
for ang, i, j in pairs:
    ki, kj = k_val[i], k_val[j]
    same = "=" if ki == kj else "≠"
    if ki == kj:
        same_k += 1
    if ki == 2 and kj == 2:
        k2_pairs.append((i, j))
    if ki == 0 and kj == 0:
        k0_pairs.append((i, j))
    log(f"  #{i:>2}↔#{j:>2}: k={ki}/{kj} {same}  hop={hop[i]}/{hop[j]}")
log(f"  同 k 對: {same_k}/30")
log(f"  k=2↔k=2 對: {len(k2_pairs)}")
log(f"  k=0↔k=0 對: {len(k0_pairs)}")

# ============ 3. k=2 成對 — random 對照 ============
log("\n=== 3. k=2 節點成對 — 幾何必然定巧合? ===")
n_k2 = len(k_dist[2])
log(f"  k=2 節點數: {n_k2}")
# 計算: 如果 60 節點中 k=2 有 12 個, 30 對近對徑完全由 A₅ 幾何決定 (邊緣結構固定)
# 但「對徑」關係 = 幾何 (30 對), k 值 = 圖論 (frustration) — 兩個獨立結構
# Null: 隨機分配 12 個 k=2 標籤畀 60 節點, 30 對中 k2-k2 對數期望
n_pair = 30
n_perm = 100000
count_ge = 0
count_ge12 = 0
k2_pairs_obs = len(k2_pairs)
for _ in range(n_perm):
    idx = rng.choice(60, n_k2, replace=False)
    labels = np.zeros(60, dtype=int)
    labels[idx] = 1
    # 每對: 兩邊都係 k2?
    c = 0
    for ang, i, j in pairs:
        if labels[i] and labels[j]:
            c += 1
    if c >= k2_pairs_obs:
        count_ge += 1
    if c >= 6:
        count_ge12 += 1
log(f"  實際 k=2↔k=2 對: {k2_pairs_obs}/30")
log(f"  Random 期望: {n_k2*(n_k2-1)/(60*59)*n_pair:.2f} 對 (每對 2 邊)")
log(f"  P(≥{k2_pairs_obs} 對) = {count_ge/n_perm:.4f}")
log(f"  P(≥6 對) = {count_ge12/n_perm:.4f}")
# 更重要: 12 個 k=2 全部被覆蓋 (12/12)?
covered = set()
for i, j in k2_pairs:
    covered.add(i); covered.add(j)
log(f"  k=2 節點覆蓋: {len(covered)}/{n_k2}")
# 覆蓋概率: random 12 標籤, 30 對中 k2-k2 對覆蓋幾多個節點
# 直接計: 期望覆蓋 = 2×E[對數] (如果唔重疊)
log(f"  → 12/12 覆蓋 vs random 期望 ~{2*n_k2*(n_k2-1)/(60*59)*n_pair:.1f} 節點")

# ============ 4. k=0 節點對徑結構 ============
log("\n=== 4. k=0 節點 (8 個) 對徑結構 ===")
k0_nodes = sorted(k_dist[0])
log(f"  k=0 節點: {k0_nodes}")
# 每個 k=0 節點嘅最近對徑
for i in k0_nodes:
    best = None; best_ang = 1e9
    for j in range(60):
        if j == i: continue
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang > 170 and ang < best_ang:
            best_ang = ang; best = j
    log(f"  #{i:>2} (k=0) ↔ #{best:>2} (k={k_val[best]})  {best_ang:.2f}°  hop={hop[i]}/{hop[best]}")
# k=0 對徑對
log(f"  k=0↔k=0 對: {k0_pairs}")
# 檢查 k=0 節點嘅 hop 分佈
log(f"  k=0 hop 分佈: {sorted([hop[i] for i in k0_nodes])}")

# ============ 5. ΔE=0 對 |ΔT| (T_local 版本) ============
log("\n=== 5. ΔE=0 對 |ΔT| — T_local (去 30° 背景) ===")
# 30° 區域 mean (5° 平滑)
CACHE = "/tmp/cache_o3"
m5 = hp.read_map(f"{CACHE}/SMICA_smooth5.0.fits")
ns5 = hp.get_nside(m5)
rm = {}
for i in range(60):
    v = vecs[i]
    d = hp.query_disc(ns5, v, np.radians(30))
    rm[i] = m5[d].mean()*1e6
T_local = T - np.array([rm[i] for i in range(60)])

k2_dT = [abs(T_local[i]-T_local[j]) for _, i, j in pairs if k_val[i]==2 and k_val[j]==2]
other_dT = [abs(T_local[i]-T_local[j]) for _, i, j in pairs if not (k_val[i]==2 and k_val[j]==2)]
k2_dT = np.array(k2_dT); other_dT = np.array(other_dT)
log(f"  k=2 對 (6) |ΔT_local| mean = {k2_dT.mean():.2f} μK")
log(f"  其他對 (24) |ΔT_local| mean = {other_dT.mean():.2f} μK")
tt = stats.mannwhitneyu(k2_dT, other_dT, alternative='less')
log(f"  Mann-Whitney p = {tt.pvalue:.4f}")
# permutation
obs = k2_dT.mean() - other_dT.mean()
all_dT = np.array([abs(T_local[i]-T_local[j]) for _, i, j in pairs])
cnt = 0
for _ in range(50000):
    idx = rng.choice(30, 6, replace=False)
    a = all_dT[idx].mean(); b = np.delete(all_dT, idx).mean()
    if a - b <= obs: cnt += 1
log(f"  Permutation p = {cnt/50000:.4f}")
# 對徑對 |ΔT_local| 全表
log(f"  {'對':>10} {'k':>5} {'|ΔT_local|':>11}")
for ang, i, j in pairs:
    log(f"  #{i:>2}↔#{j:>2} k={k_val[i]}/{k_val[j]} {abs(T_local[i]-T_local[j]):11.2f}")

# ============ 6. k=0/1/2 溫度統計 ============
log("\n=== 6. k 值 vs 溫度 ===")
for k in [0, 1, 2]:
    idx = np.array([i for i in range(60) if k_val[i] == k])
    log(f"  k={k} ({len(idx)}): mean|T|={np.abs(T[idx]).mean():6.2f}  "
        f"mean T={T[idx].mean():+6.2f}  mean|T_local|={np.abs(T_local[idx]).mean():6.2f}")
# 統計: k=2 vs 其他
i2 = np.array([i for i in range(60) if k_val[i] == 2])
io = np.array([i for i in range(60) if k_val[i] != 2])
tt2 = stats.mannwhitneyu(np.abs(T[i2]), np.abs(T[io]), alternative='less')
log(f"  k=2 vs 其他 mean|T|: Mann-Whitney p = {tt2.pvalue:.4f}")

# ============ 7. 冷斑↔對徑 k=0 對徑對詳細 ============
log("\n=== 7. 冷斑 (0) ↔ 對徑 (57): k=0 對徑對 ===")
log(f"  node 0: k={k_val[0]}, hop={hop[0]}, T={T[0]:+.2f}, T_local={T_local[0]:+.2f}")
log(f"  node 57: k={k_val[57]}, hop={hop[57]}, T={T[57]:+.2f}, T_local={T_local[57]:+.2f}")
# k=0 全部節點溫度
log(f"  k=0 節點溫度:")
for i in k0_nodes:
    log(f"    #{i:>2}: T={T[i]:+8.2f}  T_local={T_local[i]:+8.2f}  hop={hop[i]}")

with open(os.path.join(OUT, "node57_kstructure_results.txt"), "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/node57_kstructure_results.txt")
