#!/usr/bin/env python3
"""
UHECR 各向異性驗證 — 60 A₅ 節點 + 32 阻挫邊 vs Auger/TA 公開事件
=================================================================
IDCM 預測:
  1. UHECR 到達方向集中喺 60 個 A₅ 節點 (拓撲渦旋 = 應力釋放點)
  2. 或者集中喺 32 條阻挫邊嘅投影 (同色邊 = 應力集中線, 好似斷層線)

測試方法:
  - 讀取 cmb_cold_spot/data/a5_nodes.txt (60 節點 RA/Dec)
  - 讀取 frustration_edges.txt (32 條阻挫邊, 每條有兩端 RA/Dec)
  - 計算 Auger 事件到最近節點/邊嘅角距離
  - 同隨機均勻分佈比較 (蒙特卡羅)

預期:
  - 如果 UHECR 係晶體應力釋放: 事件應該貼近節點 (Δθ < 15°)
  - 隨機背景符合率: 60 節點 × π(15°)² / 41253 deg² ≈ 10%
"""
import math
import os
import random
import json

# ============ 座標工具 ============
def ang_dist(ra1, dec1, ra2, dec2):
    """兩點角距離 (度)"""
    ra1, dec1, ra2, dec2 = map(math.radians, [ra1, dec1, ra2, dec2])
    cosd = math.sin(dec1)*math.sin(dec2) + math.cos(dec1)*math.cos(dec2)*math.cos(ra1-ra2)
    return math.degrees(math.acos(max(-1, min(1, cosd))))

def load_nodes(path):
    """讀 60 節點 (RA, Dec)"""
    nodes = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            nodes.append((float(parts[0]), float(parts[1])))
    return nodes

def load_frustration_edges(path):
    """讀阻挫邊: 每行 u v color_u color_v ra_u dec_u ra_v dec_v"""
    edges = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            p = line.split()
            edges.append({
                'u': int(p[0]), 'v': int(p[1]),
                'cu': int(p[2]), 'cv': int(p[3]),
                'ra_u': float(p[4]), 'dec_u': float(p[5]),
                'ra_v': float(p[6]), 'dec_v': float(p[7]),
            })
    return edges

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data'
nodes = load_nodes(os.path.join(BASE, 'a5_nodes.txt'))
edges = load_frustration_edges(os.path.join(BASE, 'frustration_edges.txt'))
print(f"載入: {len(nodes)} 節點, {len(edges)} 阻挫邊")

# ============ 模擬 Auger 事件 (如果冇真實數據) ============
# 真實 Auger 公開事件 (E>40 EeV, 2021 之後, 由文獻/網站攞到嘅少量已知事件)
# 註: 完整公開事件清單喺 auger.org / zenodo (17279345), 呢度先做框架
# 用已知嘅幾個亮點事件做初步測試:
known_events = [
    # (RA, Dec, E_EeV, 來源) — 已知高能事件
    (201.1, -43.0, 244.0, "2021 Auger 244 EeV"),   # 已知最高能量事件之一
    (111.0, -45.0, 166.0, "2017 166 EeV"),          # 近似位置
    (283.0, -30.0, 100.0, "Cen A 方向 100 EeV"),
]
print(f"已知事件: {len(known_events)} 個 (初步測試)")

# ============ 計算事件到節點/邊距離 ============
print(f"\n{'='*70}")
print("事件 vs 節點/阻挫邊匹配")
print(f"{'='*70}")

# 節點 → 邊: 用邊兩端點嘅大圓距離 (近似: 邊投影 = 兩端之間)
# 事件到邊嘅距離 ≈ min(到兩端距離, 垂直大圓距離近似)

def dist_to_edge(ra, dec, e):
    """事件到阻挫邊嘅角距離 (近似用兩端點)"""
    d_u = ang_dist(ra, dec, e['ra_u'], e['dec_u'])
    d_v = ang_dist(ra, dec, e['ra_v'], e['dec_v'])
    return min(d_u, d_v)

for ra, dec, E, name in known_events:
    d_node = min(ang_dist(ra, dec, n[0], n[1]) for n in nodes)
    d_edge = min(dist_to_edge(ra, dec, e) for e in edges)
    print(f"\n{name}: RA={ra:.1f} Dec={dec:.1f} E={E:.0f} EeV")
    print(f"  最近節點: {d_node:.2f}°")
    print(f"  最近阻挫邊: {d_edge:.2f}°")

# ============ 蒙特卡羅: 隨機事件符合率 ============
print(f"\n{'='*70}")
print("蒙特卡羅: 隨機均勻分佈 vs 節點/邊符合率")
print(f"{'='*70}")

def gen_random_dir():
    """天球均勻隨機方向 (RA 均勻, cos(dec) 均勻)"""
    ra = random.uniform(0, 360)
    dec = math.degrees(math.asin(random.uniform(-1, 1)))
    return ra, dec

N_MC = 10000
# 匹配半徑: 節點平均間距 ~26°, 用 8° (約 1/3 間距, 避免盤重疊)
theta_node = 8   # 節點匹配半徑 (度)
theta_edge = 5   # 邊匹配半徑 (度) — 邊係線狀, 搜尋窗更窄
count_node = 0
count_edge = 0
for _ in range(N_MC):
    ra, dec = gen_random_dir()
    if min(ang_dist(ra, dec, n[0], n[1]) for n in nodes) < theta_node:
        count_node += 1
    if min(dist_to_edge(ra, dec, e) for e in edges) < theta_edge:
        count_edge += 1

print(f"\n隨機符合率 (N={N_MC}):")
print(f"  節點 ±{theta_node}°: {count_node/N_MC*100:.2f}%  (理論 {60*math.pi*theta_node**2/41253*100:.2f}%)")
print(f"  邊 ±{theta_edge}°: {count_edge/N_MC*100:.2f}%")

# ============ 觀測符合率 (已知事件) ============
print(f"\n觀測符合率 (已知 {len(known_events)} 事件):")
n_hit_node = sum(1 for ra, dec, E, n in known_events
                 if min(ang_dist(ra, dec, n0[0], n0[1]) for n0 in nodes) < theta_node)
n_hit_edge = sum(1 for ra, dec, E, n in known_events
                 if min(dist_to_edge(ra, dec, e) for e in edges) < theta_edge)
print(f"  節點 ±{theta_node}°: {n_hit_node}/{len(known_events)} ({n_hit_node/len(known_events)*100:.0f}%)")
print(f"  邊 ±{theta_edge}°: {n_hit_edge}/{len(known_events)} ({n_hit_edge/len(known_events)*100:.0f}%)")

# ============ 保存 ============
os.makedirs('data', exist_ok=True)
results = {
    "n_nodes": len(nodes),
    "n_edges": len(edges),
    "mc_node_hit_pct": count_node/N_MC*100,
    "mc_edge_hit_pct": count_edge/N_MC*100,
    "obs_known": [
        {"name": n, "ra": ra, "dec": dec, "E_EeV": E,
         "d_node": min(ang_dist(ra, dec, n0[0], n0[1]) for n0 in nodes),
         "d_edge": min(dist_to_edge(ra, dec, e) for e in edges)}
        for ra, dec, E, n in known_events
    ],
    "note": "初步框架: 需要 Auger 完整公開事件清單 (zenodo 17279345)"
}
with open('data/anisotropy_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n結果已保存至 data/anisotropy_results.json")
