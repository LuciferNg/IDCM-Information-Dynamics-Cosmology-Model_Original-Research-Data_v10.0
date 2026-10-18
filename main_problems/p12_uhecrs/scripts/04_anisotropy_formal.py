#!/usr/bin/env python3
"""
UHECR 各向異性正式驗證 — 60 A₅ 節點 vs 文獻記錄嘅高能事件
============================================================
IDCM 預測: UHECR 到達方向集中喺 60 A₅ 節點 (拓撲渦旋應力釋放點)
  + 32 條阻挫邊 (應力集中線, 好似斷層線)

已知文獻高能事件 (E > 40 EeV, 有記錄嘅):
  - Auger: 244 EeV 事件 (2021), 166 EeV (2017), Cen A 過量 (4.0σ)
  - Telescope Array: Oh-My-God 3.2e20 eV (1991 Fly's Eye, RA≈283 Dec≈50)
  - TA hotspot: RA≈146.5 Dec≈43.2 (20° 過量)

方法: 每個事件到最近節點嘅角距離, 同隨機分佈比較
"""
import math, os, json, random

def ang_dist(ra1, dec1, ra2, dec2):
    ra1, dec1, ra2, dec2 = map(math.radians, [ra1, dec1, ra2, dec2])
    cosd = math.sin(dec1)*math.sin(dec2) + math.cos(dec1)*math.cos(dec2)*math.cos(ra1-ra2)
    return math.degrees(math.acos(max(-1, min(1, cosd))))

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data'
nodes = []
with open(os.path.join(BASE, 'a5_nodes.txt')) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        p = line.split()
        nodes.append((float(p[0]), float(p[1])))
print(f"60 節點載入完成: {len(nodes)}")

# 文獻已知高能事件 (RA, Dec, E_EeV, 名稱)
events = [
    (201.1, -43.0, 244, "Auger 2021 244 EeV"),
    (287.4, -44.5, 166, "Auger 2017 166 EeV (近似)"),
    (283.0, -30.0, 100, "Cen A 方向 (Auger excess)"),
    (283.0, 50.0, 320, "Oh-My-God 3.2e20 eV (Fly's Eye 1991)"),
    (146.5, 43.2, 100, "TA hotspot 中心"),
    (201.1, -43.0, 57, "Auger 熱點 (天區)"),
]
print(f"測試事件: {len(events)}")

print(f"\n{'='*70}")
print(f"{'事件':<32} {'RA':>7} {'Dec':>7} {'E(EeV)':>7} {'Δθ節點':>8} {'Δθ邊':>8}")
print(f"{'='*70}")

# 阻挫邊 (32條)
edges = []
with open(os.path.join(BASE, 'frustration_edges.txt')) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        p = line.split()
        edges.append((float(p[4]), float(p[5]), float(p[6]), float(p[7])))

def dist_to_edge(ra, dec, e):
    return min(ang_dist(ra, dec, e[0], e[1]), ang_dist(ra, dec, e[2], e[3]))

hits_8 = 0
hits_15 = 0
for ra, dec, E, name in events:
    d_node = min(ang_dist(ra, dec, n[0], n[1]) for n in nodes)
    d_edge = min(dist_to_edge(ra, dec, e) for e in edges)
    if d_node < 8: hits_8 += 1
    if d_node < 15: hits_15 += 1
    print(f"{name:<32} {ra:>7.1f} {dec:>7.1f} {E:>7.0f} {d_node:>8.2f} {d_edge:>8.2f}")

# 蒙特卡羅
N_MC = 100000
count_8 = 0
count_15 = 0
for _ in range(N_MC):
    ra = random.uniform(0, 360)
    dec = math.degrees(math.asin(random.uniform(-1, 1)))
    d = min(ang_dist(ra, dec, n[0], n[1]) for n in nodes)
    if d < 8: count_8 += 1
    if d < 15: count_15 += 1

print(f"\n蒙特卡羅 (N={N_MC}):")
print(f"  隨機事件到最近節點 < 8°:  {count_8/N_MC*100:.2f}%")
print(f"  隨機事件到最近節點 < 15°: {count_15/N_MC*100:.2f}%")
print(f"\n觀測 ({len(events)} 事件):")
print(f"  < 8°: {hits_8}/{len(events)} = {hits_8/len(events)*100:.0f}%  (隨機 {count_8/N_MC*100:.1f}%)")
print(f"  < 15°: {hits_15}/{len(events)} = {hits_15/len(events)*100:.0f}%  (隨機 {count_15/N_MC*100:.1f}%)")

# Poisson 顯著性
from math import exp, factorial
p_8 = 1 - exp(-len(events) * count_8/N_MC)
# 觀測 hits_8 嘅二項檢驗
def binom_pmf(k, n, p):
    from math import comb
    return comb(n, k) * p**k * (1-p)**(n-k)
p_val = sum(binom_pmf(k, len(events), count_8/N_MC) for k in range(hits_8, len(events)+1))
print(f"\n二項檢驗 P(≥{hits_8} hits | 隨機) = {p_val:.4f}")
if p_val < 0.05:
    print("→ 顯著偏離隨機! 支持節點各向異性 🟢")
else:
    print("→ 樣本太少, 未能拒絕隨機 (需完整 Auger 目錄)")

# 保存
os.makedirs('data', exist_ok=True)
with open('data/anisotropy_known_events.json', 'w') as f:
    json.dump({
        "events": [{"name": n, "ra": ra, "dec": dec, "E_EeV": E} for ra, dec, E, n in events],
        "mc_pct_8": count_8/N_MC*100,
        "mc_pct_15": count_15/N_MC*100,
        "hits_8": hits_8, "hits_15": hits_15,
        "binom_p": p_val
    }, f, indent=2, ensure_ascii=False)
print(f"結果已保存至 data/anisotropy_known_events.json")
