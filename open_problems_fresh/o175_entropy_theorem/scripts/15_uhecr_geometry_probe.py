#!/usr/bin/env python3
"""
O175-D3 強化檢驗 — Auger Open Data 事件方向 vs IDCM 幾何 (初步, 109 SD events)
==============================================================================
數據: data/auger/auger_catalogSD.csv (opendata.auger.org, 公開免費)
      id, utctime, energy(EeV), denergy, theta, phi, ra, dec, risetime, drisetime, multiplicity

背景 (O7/O173): UHECR = 阻挫邊重聯 = 調律者寫入事件 (相位滑移 π, ΔE=2|h_i|)。
可證偽預言: UHECR 事件方向應與 88 格節點網格有幾何關聯 — 特別係:
  P1. 事件到最近 A5 節點 (60 節點, 冷斑分析用) 嘅角距離分佈 vs 均勻期望
  P2. 事件銀緯分佈 (目錄斑 vs 結構: 記憶 — 阻挫邊喺 |b|<20°)

樣本: 109 SD events (featured sample, E in [46,166] EeV → 0.46-1.66e20 eV?)
      統計力弱 — 明確標註「初步」, 負結果 = 樣本不足, 唔係否決。
"""
import csv, math
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "auger"

def angdist(ra1, dec1, ra2, dec2):
    """角距離 (deg)。ra/dec in deg。"""
    r1, d1, r2, d2 = map(math.radians, (ra1, dec1, ra2, dec2))
    c = math.sin(d1)*math.sin(d2) + math.cos(d1)*math.cos(d2)*math.cos(r1-r2)
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))

# 88 格節點幾何 — A5 60 節點 (cmb_cold_spot 分析產物, 只讀)
nodes = []
for cand in [BASE / "data" / "a5_nodes.txt",
             Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt")]:
    if cand.exists():
        for line in cand.read_text().splitlines():
            p = line.split()
            if len(p) >= 2:
                try: nodes.append((float(p[0]), float(p[1])))
                except ValueError: pass
        if nodes: break
print(f"節點來源: {len(nodes)} nodes (冷斑分析 a5_nodes.txt, 只讀)")

rows = []
with open(DATA / "auger_catalogSD.csv") as f:
    for d in csv.DictReader(f):
        try:
            rows.append((float(d["energy"]), float(d["ra"]), float(d["dec"])))
        except ValueError:
            pass
print(f"Auger SD events: {len(rows)}, E range [{min(r[0] for r in rows):.0f}, {max(r[0] for r in rows):.0f}] EeV")

# ---------------------------------------------------------------------------
# P2: 銀緯分佈
print("\n== P2: 銀緯分佈 ==")
lat = []
for e, ra, dec in rows:
    # 簡化: 銀緯 ~ dec (粗略, 唔做座標轉換) — 註明
    lat.append(dec)
nb_low = sum(1 for x in lat if abs(x) < 20) / len(lat)
print(f"  |dec|<20° 比例: {nb_low:.2f} ({sum(1 for x in lat if abs(x)<20)}/{len(lat)})")
print(f"  全天空均勻期望: sin(20°)=0.342 (dec 均勻喺赤道附近唔適用 — 註: 粗略)")
# 均勻球面期望: 面積分數 = 1-cos(20°) = 0.060
print(f"  均勻球面期望 |b|<20°: 1-cos(20°) = {1-math.cos(math.radians(20)):.3f}")

# ---------------------------------------------------------------------------
# P1: 到最近節點角距離 (如果有節點)
if nodes:
    print(f"\n== P1: 到最近 A5 節點角距離 (n={len(rows)} events, {len(nodes)} nodes) ==")
    # 均勻分佈期望: 60 節點平均最近距離 ~ sqrt(4pi/(60*4pi))? 用 Monte Carlo
    import random
    random.seed(42)
    mc = []
    for _ in range(5000):
        r2 = random.uniform(-1, 1); dec_r = math.degrees(math.asin(r2))
        ra_r = random.uniform(0, 360)
        mc.append(min(angdist(ra_r, dec_r, n[0], n[1]) for n in nodes))
    mc_mean = sum(mc)/len(mc)
    obs = [min(angdist(ra, dec, n[0], n[1]) for n in nodes) for _, ra, dec in rows]
    obs_mean = sum(obs)/len(obs)
    print(f"  obs 平均最近節點距離: {obs_mean:.2f}°  (n={len(obs)})")
    print(f"  MC 均勻期望:          {mc_mean:.2f}°")
    print(f"  dev: {(obs_mean-mc_mean)/mc_mean*100:+.1f}%")
    # 最近節點 id 統計 (有冇聚集?)
    from collections import Counter
    c = Counter(min(range(len(nodes)), key=lambda i: angdist(ra, dec, nodes[i][0], nodes[i][1])) for _, ra, dec in rows)
    print(f"  最近節點命中 top5: {c.most_common(5)}")
else:
    print("\n== P1 跳過 (冇節點檔) ==")

print("\n== 註 ==")
print("樣本 = opendata 目錄 featured subset (109), 非完整 25086 (zenodo 403 blocked)。")
print("結論強度: 初步幾何探針; 統計力不足以下結論; 完整樣本後續補。")
