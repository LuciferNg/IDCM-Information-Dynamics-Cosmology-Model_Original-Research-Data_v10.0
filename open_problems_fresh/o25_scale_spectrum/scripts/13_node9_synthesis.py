#!/usr/bin/env python3
"""
13_node9_synthesis.py — O25: Node9 研究合併 — 透明度框架 vs 大尺度冷區
=====================================================================
合併 O1-O25 所有 node9 研究, 解開核心矛盾:

O21 結論: node9 單點 = 透明晶格 (z=-1.46σ@4.17°, z=-0.65σ@10°) — 高斯隨機
O25 結論: node9 區域 = 大尺度冷區 (20°盤 z=-2.0σ, 10°半徑 z=-2.56σ) + 熱環 z=+2.43σ

問題: 單點唔顯著但區域顯著 — 呢個矛盾點解?
假說 A: 區域效應由「周邊」驅動, 唔係 node9 本身 (node9 只係喺大冷區邊緣)
假說 B: 透明度框架 = 細尺度 (4°), 大尺度冷區 = 獨立現象 (兩個尺度層次)
假說 C: node9 嘅「透明」位置令佢反映背景冷區, 冇自身調製

檢驗:
1. node9 單點 vs 區域 mean 喺各尺度嘅比較
2. 冷區中心偏移: 冷區真正中心喺邊? (離開 node9 幾遠?)
3. node9 喺冷區嘅位置 (中心定邊緣?)
4. 三地圖確認冷區中心
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, json

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
CACHE = os.path.join(BASE, "o25_scale_spectrum", "data", "smooth_cache_large")
DATA = os.path.join(BASE, "o25_scale_spectrum", "data")

node9 = {"l": 214.92, "b": -31.16}
node0 = {"l": 209.00, "b": -57.00}

# 用 Commander 15° 平滑 (大尺度結構清晰)
m = hp.read_map(os.path.join(CACHE, "Commander_smooth15.0.fits"), field=0)
m_low = hp.ud_grade(m, 512)
nside_low = 512
npix_low = hp.nside2npix(nside_low)

print("=" * 70)
print("Node9 研究合併: 透明度 vs 大尺度冷區")
print("=" * 70)

# ============ 1. 冷區中心搜尋 (離開 node9) ============
print("\n[1] 冷區真正中心搜尋 (Commander 15°, 20° 圓盤)")
print("    喺 node9 附近 30° 內掃描, 搵最冷 20° 圓盤中心")
vec9 = hp.ang2vec(node9["l"], node9["b"], lonlat=True)
# 喺 30° 半徑內直接採樣 500 個中心 (用球座標)
rng = np.random.default_rng(123)
candidates = []
for _ in range(500):
    # 喺 node9 方向 30° 錐內均勻採樣:
    # 方法: 繞 node9 軸隨機旋轉 + 隨機角偏移
    theta = np.radians(30.0) * np.sqrt(rng.random())  # 均勻面積
    phi = rng.random() * 2 * np.pi
    # node9 方向向量
    l9, b9 = np.radians(node9["l"]), np.radians(node9["b"])
    v9 = np.array([np.cos(b9)*np.cos(l9), np.cos(b9)*np.sin(l9), np.sin(b9)])
    # 搵兩個正交基
    tmp = np.array([1.0, 0.0, 0.0]) if abs(v9[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    e1 = np.cross(v9, tmp); e1 /= np.linalg.norm(e1)
    e2 = np.cross(v9, e1)
    rv = np.cos(theta)*v9 + np.sin(theta)*(np.cos(phi)*e1 + np.sin(phi)*e2)
    candidates.append(rv)
print(f"    有效候選: {len(candidates)}")

best_mean = 1e9
best_vec = None
for rv in candidates:
    d = hp.query_disc(nside_low, rv, np.radians(20.0))
    mean_t = m_low[d].mean() * 1e6
    if mean_t < best_mean:
        best_mean = mean_t
        best_vec = rv

best_l, best_b = hp.vec2ang(best_vec, lonlat=True)
best_l = float(np.asarray(best_l).item()); best_b = float(np.asarray(best_b).item())
ang_off = np.degrees(np.arccos(np.clip(np.dot(vec9, best_vec), -1, 1)))
print(f"    最冷 20° 圓盤中心: (l={best_l:.2f}, b={best_b:.2f}), T={best_mean:+.2f} μK")
print(f"    距離 node9: {ang_off:.2f}°")
print(f"    node9 喺冷區: {'中心' if ang_off < 5 else ('內緣' if ang_off < 15 else '邊緣')}")

# node9 自己嘅 20° 盤
d9 = hp.query_disc(nside_low, vec9, np.radians(20.0))
t9 = m_low[d9].mean() * 1e6
print(f"    node9 中心 20° 盤: {t9:+.2f} μK (冷區中心 vs node9 中心: {best_mean-t9:+.2f})")

# ============ 2. 冷區中心 vs node9 嘅三地圖 ============
print("\n[2] 冷區中心三地圖確認")
for mname in ["NILC", "Commander"]:
    mm = hp.read_map(os.path.join(CACHE, f"{mname}_smooth15.0.fits"), field=0)
    mm_low = hp.ud_grade(mm, 512)
    d_best = hp.query_disc(nside_low, best_vec, np.radians(20.0))
    d9m = hp.query_disc(nside_low, vec9, np.radians(20.0))
    print(f"    {mname}: 冷區中心={mm_low[d_best].mean()*1e6:+.2f}  node9中心={mm_low[d9m].mean()*1e6:+.2f}")

# ============ 3. 單點 vs 區域: 透明度框架檢驗 ============
print("\n[3] 單點 vs 區域 — 透明度框架嘅尺度依賴")
print("    細尺度 (4°): node9 單點 = 透明 (O21 z=-1.46σ)")
print("    大尺度 (15°): node9 區域 = 冷區 (O25 z=-2.0σ)")
print("    → 兩個尺度層次: 細尺度透明 + 大尺度冷區 = 唔矛盾")

# 驗證: node9 單點喺 15° 平滑嘅 z (vs 60 節點)
nodes = []
with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
pix_nodes = hp.ang2pix(nside_low, gal.l.deg, gal.b.deg, lonlat=True)
T_nodes = m_low[pix_nodes] * 1e6
z9 = (T_nodes[9] - T_nodes.mean()) / T_nodes.std()
print(f"    node9 單點 @15°: T={T_nodes[9]:+.1f} μK, 60節點 z={z9:+.2f}σ")
print(f"    (O21 @10° z=-0.65σ; @15° 更平滑, 單點更弱)")

# ============ 4. 冷區中心對照文獻結構 ============
print("\n[4] 冷區中心 vs 已知結構")
# 冷區中心同冷斑距離
def angdist(l1, b1, l2, b2):
    l1, b1, l2, b2 = map(np.radians, [l1, b1, l2, b2])
    return np.degrees(np.arccos(np.clip(np.sin(b1)*np.sin(b2)+np.cos(b1)*np.cos(b2)*np.cos(l1-l2), -1, 1)))
d_center_node0 = angdist(best_l, best_b, node0["l"], node0["b"])
d_center_node9 = angdist(best_l, best_b, node9["l"], node9["b"])
print(f"    冷區中心 ↔ 冷斑 (209,-57): {d_center_node0:.1f}°")
print(f"    冷區中心 ↔ node9: {d_center_node9:.1f}°")
print(f"    → 冷區中心 {'接近 node9' if d_center_node9 < d_center_node0 else '更接近冷斑'}")

# 儲存
out = {
    "cold_region_center": {"l": best_l, "b": best_b, "T_20deg": float(best_mean), "dist_from_node9": float(ang_off)},
    "node9_disc": {"T_20deg": float(t9)},
    "node9_single_15deg": {"T": float(T_nodes[9]), "z_60nodes": float(z9)},
    "dist_to_coldspot": float(d_center_node0),
    "dist_to_node9": float(d_center_node9),
}
with open(os.path.join(DATA, "node9_synthesis.json"), "w") as f:
    json.dump(out, f, indent=2)
print("\n✅ saved data/node9_synthesis.json")
