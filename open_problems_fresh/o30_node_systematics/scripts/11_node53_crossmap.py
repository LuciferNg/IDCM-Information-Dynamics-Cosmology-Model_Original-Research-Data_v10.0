#!/usr/bin/env python3
"""
11_node53_crossmap.py — O30: node53 三地圖一致性 (SMICA/NILC/Commander)
========================================================================
O27 判據: 三地圖一致 (<5% spread) + 平譜 → 真實結構
node53 喺 3 種 component-separation 方法嘅熱信號一致?
資源: o5_catalog_compare/data/smooth_cache/ 有 4.17° 三地圖
"""
import healpy as hp
import numpy as np
import os, json

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")
OUT = os.path.join(BASE, "o30_node_systematics/data")

MAPS = {
    "SMICA": os.path.join(CACHE, "smica2_smooth4.17.fits"),
    "NILC": os.path.join(CACHE, "nilc2_smooth4.17.fits"),
    "Commander": os.path.join(CACHE, "commander_smooth4.17.fits"),
}
L, B = 319.50, -34.20  # node53
NODES = np.loadtxt(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt"))
NODE53_T = None  # 4.17° 節點溫度 (O3)

print("=" * 70)
print("O30: node53 三地圖一致性 (4.17°)")
print("=" * 70)

vals = {}
for name, path in MAPS.items():
    m = hp.read_map(path, field=0)
    nside = hp.get_nside(m)
    # 中心 3° 盤平均 (對稱)
    vec = hp.ang2vec(L, B, lonlat=True)
    pix = hp.query_disc(nside, vec, np.radians(3.0))
    v = np.mean(m[pix]) * 1e6
    vals[name] = float(v)
    print(f"{name:<12} 3°盤: {v:+.2f} μK")

# 環背景修正後 (4-8°)
vals_ring = {}
for name, path in MAPS.items():
    m = hp.read_map(path, field=0)
    nside = hp.get_nside(m)
    vec = hp.ang2vec(L, B, lonlat=True)
    p_core = hp.query_disc(nside, vec, np.radians(2.0))
    p_ring = hp.query_disc(nside, vec, np.radians(8.0))
    p_in = hp.query_disc(nside, vec, np.radians(4.0))
    p_ring = np.setdiff1d(p_ring, p_in)
    dT = (np.mean(m[p_core]) - np.mean(m[p_ring])) * 1e6
    vals_ring[name] = float(dT)
    print(f"{name:<12} 環背景ΔT: {dT:+.2f} μK")

# spread
arr = np.array(list(vals.values()))
arr_r = np.array(list(vals_ring.values()))
spread = (arr.max() - arr.min()) / abs(arr.mean()) * 100
spread_r = (arr_r.max() - arr_r.min()) / abs(arr_r.mean()) * 100
print(f"\n3°盤 spread: {spread:.1f}% (O27 判據: <5% 🟢, 5-20% 🟡)")
print(f"環背景 spread: {spread_r:.1f}%")

verdict = "🟢🟢 三地圖一致" if spread < 5 else ("🟢 一致" if spread < 10 else ("🟡 邊緣" if spread < 20 else "🔴 分歧"))
print(f"判定: {verdict} (3°盤 spread={spread:.1f}%)")

# 高緯隨機對照: 3 點 spread 分佈
RNG = np.random.default_rng(42)
spreads_ctrl = []
m_s = hp.read_map(MAPS["SMICA"], field=0)
m_n = hp.read_map(MAPS["NILC"], field=0)
m_c = hp.read_map(MAPS["Commander"], field=0)
nside = hp.get_nside(m_s)
for _ in range(500):
    rl = RNG.uniform(0, 360)
    rb = RNG.uniform(-90, 90)
    if abs(rb) < 20:
        continue
    vec = hp.ang2vec(rl, rb, lonlat=True)
    pix = hp.query_disc(nside, vec, np.radians(3.0))
    vs = np.array([np.mean(m_s[pix])*1e6, np.mean(m_n[pix])*1e6, np.mean(m_c[pix])*1e6])
    if abs(vs.mean()) > 1:
        spreads_ctrl.append((vs.max()-vs.min())/abs(vs.mean())*100)
spreads_ctrl = np.array(spreads_ctrl)
p_rank = (spreads_ctrl >= spread).mean()
print(f"\n隨機 500 點 spread 分佈: median={np.median(spreads_ctrl):.1f}%, p(spread≥{spread:.1f}%)={p_rank:.3f}")

with open(os.path.join(OUT, "11_node53_crossmap.json"), "w") as f:
    json.dump({"l": L, "b": B, "core_3deg": vals, "ring_dT": vals_ring,
               "spread_pct": spread, "spread_ring_pct": spread_r,
               "verdict": verdict, "ctrl_median": float(np.median(spreads_ctrl)),
               "p_rank": float(p_rank)}, f, indent=2)
print(f"\n✅ 已存: {os.path.join(OUT, '11_node53_crossmap.json')}")
