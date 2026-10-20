#!/usr/bin/env python3
"""
01_antipode_region.py — O6: 節點 57 對徑點區域掃描
=====================================================
節點 57 (對徑點, +8.21 μK @ 4.17°) 附近 5° 溫度場:
1. 5° 半徑內 mean/std/min/max (SMICA 4.17° cache)
2. 同節點 0 (冷斑) 5° 區域對比
3. 熱斑結構檢查 (O2: F6 @ 1.0°, F7 @ 0.5°)
4. 全天空背景對比

注意: a5_nodes.txt 係 ICRS, SMICA cache 係 Galactic frame → SkyCoord 轉換!
"""
import healpy as hp
import numpy as np
import os
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
NODE_FILE = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
CACHE = "/tmp/cache_o3"
OUT = os.path.join(BASE, "o6_antipode_check/data")

rng = np.random.default_rng(42)

# ============ 載入節點 ============
nodes = []
with open(NODE_FILE) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)

# ============ 載入 SMICA 4.17° cache ============
m = hp.read_map(os.path.join(CACHE, "SMICA_4.17.fits"), field=0)
nside = hp.get_nside(m)
npix = hp.nside2npix(nside)
print("=" * 66)
print("O6: 節點 57 對徑點區域掃描 (SMICA 4.17° 平滑)")
print("=" * 66)
print(f"nside={nside}, npix={npix}, finite={np.isfinite(m).all()}")

# ============ 節點 → 銀河座標 ============
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = gal.l.deg
b_deg = gal.b.deg

# 節點 57 同 0
for i in [0, 57]:
    print(f"\n節點 {i}: ICRS=({nodes[i,0]:.2f},{nodes[i,1]:.2f}), "
          f"Gal=({l_deg[i]:.2f},{b_deg[i]:.2f})")

def region_stats(idx, radius_deg):
    """以節點 idx 為中心, radius 內嘅像素統計"""
    center_vec = hp.ang2vec(l_deg[idx], b_deg[idx], lonlat=True)
    # 用高 res 查詢: 直接搵半徑內像素
    disc = hp.query_disc(nside, center_vec, np.radians(radius_deg))
    vals = m[disc] * 1e6
    return vals

def disk_coverage(radius_deg):
    """60 節點 5° 盤覆蓋率 (MC 200k)"""
    rng2 = np.random.default_rng(7)
    # 隨機單位向量 (均勻球面)
    z = rng2.uniform(-1, 1, 200000)
    theta = rng2.uniform(0, 2*np.pi, 200000)
    pts = np.stack([np.sqrt(1-z**2)*np.cos(theta),
                    np.sqrt(1-z**2)*np.sin(theta), z], axis=1)
    node_vecs = hp.ang2vec(l_deg, b_deg, lonlat=True)
    covered = np.zeros(len(pts), dtype=bool)
    for nv in node_vecs:
        dots = np.clip(pts @ nv, -1, 1)
        covered |= np.degrees(np.arccos(dots)) < radius_deg
    return covered.mean()

# ============ 1. 節點 57 vs 節點 0: 5° 區域 ============
print("\n=== 1. 5° 半徑區域統計 (SMICA 4.17°) ===")
for idx, label in [(0, "節點 0 (冷斑)"), (57, "節點 57 (對徑)")]:
    vals = region_stats(idx, 5.0)
    print(f"{label}: n_pix={len(vals)}, mean={vals.mean():+.2f} μK, "
          f"std={vals.std():.1f} μK, min={vals.min():+.2f}, max={vals.max():+.2f}")
    # 中心值
    pix_c = hp.ang2pix(nside, l_deg[idx], b_deg[idx], lonlat=True)
    print(f"  中心像素 T = {m[pix_c]*1e6:+.2f} μK")

# ============ 2. 節點 57 附近有冇熱斑? ============
print("\n=== 2. 節點 57 5° 內極值 (熱斑結構檢查) ===")
vals57 = region_stats(57, 5.0)
order = np.argsort(vals57)
print("5° 內最冷 3 像素:")
for k in order[:3]:
    print(f"  T={vals57[k]:+.2f} μK")
print("5° 內最熱 3 像素:")
for k in order[-3:]:
    print(f"  T={vals57[k]:+.2f} μK")

# 熱像素位置
hot_pix = np.argpartition(vals57, -5)[-5:]
hot_vecs = hp.pix2ang(nside, hp.query_disc(nside, hp.ang2vec(l_deg[57], b_deg[57], lonlat=True), np.radians(5.0))[hot_pix], lonlat=True)
# 簡化: 直接報告最熱像素位置
disc57 = hp.query_disc(nside, hp.ang2vec(l_deg[57], b_deg[57], lonlat=True), np.radians(5.0))
hot_idx = disc57[np.argsort(m[disc57])[-5:]]
l_h, b_h = hp.pix2ang(nside, hot_idx, lonlat=True)
print("最熱 5 像素位置 (Gal):")
for j in range(5):
    print(f"  T={m[hot_idx[j]]*1e6:+.2f} μK @ (l={l_h[j]:.2f}, b={b_h[j]:.2f})")

# ============ 3. 對比: 節點 0 5° 區域極值 ============
print("\n=== 3. 節點 0 5° 區域 (對比) ===")
disc0 = hp.query_disc(nside, hp.ang2vec(l_deg[0], b_deg[0], lonlat=True), np.radians(5.0))
cold_idx = disc0[np.argsort(m[disc0])[:5]]
l_c, b_c = hp.pix2ang(nside, cold_idx, lonlat=True)
print("最冷 5 像素位置 (Gal):")
for j in range(5):
    print(f"  T={m[cold_idx[j]]*1e6:+.2f} μK @ (l={l_c[j]:.2f}, b={b_c[j]:.2f})")

# ============ 4. 節點 57 喺全天空嘅百分位 ============
print("\n=== 4. 節點 57 全天空百分位 ===")
pix57 = hp.ang2pix(nside, l_deg[57], b_deg[57], lonlat=True)
T57 = m[pix57] * 1e6
# 用子採樣計百分位 (2GB 地圖排序太慢)
sample = m[::7] * 1e6
pct = (sample < T57).mean() * 100
print(f"節點 57 T={T57:+.2f} μK → 百分位 {pct:.1f}% (比 {pct:.1f}% 像素熱)")
pix0 = hp.ang2pix(nside, l_deg[0], b_deg[0], lonlat=True)
T0 = m[pix0] * 1e6
pct0 = (sample < T0).mean() * 100
print(f"節點 0 T={T0:+.2f} μK → 百分位 {pct0:.1f}%")

# ============ 5. 覆蓋率 ============
cov = disk_coverage(5.0)
print(f"\n=== 5. 60 節點 5° 盤覆蓋率: {cov*100:.1f}% (MC 200k) ===")

# ============ 6. 對徑點係咪「平」? ============
print("\n=== 6. 對徑點區域 vs 隨機 5° 盤 (bootstrap) ===")
# 用 200 個隨機 5° 盤計 mean/std 分佈, 對比節點 57 區域
rand_means = []
rand_stds = []
for _ in range(200):
    # 隨機方向
    v = rng.normal(size=3)
    v = v / np.linalg.norm(v)
    d = hp.query_disc(nside, v, np.radians(5.0))
    rv = m[d] * 1e6
    rand_means.append(rv.mean())
    rand_stds.append(rv.std())
rand_means = np.array(rand_means)
rand_stds = np.array(rand_stds)
m57 = region_stats(57, 5.0).mean()
s57 = region_stats(57, 5.0).std()
z_m = (m57 - rand_means.mean()) / rand_means.std()
z_s = (s57 - rand_stds.mean()) / rand_stds.std()
print(f"隨機 5° 盤 mean: {rand_means.mean():+.2f} ± {rand_means.std():.2f} μK")
print(f"節點 57 區域 mean: {m57:+.2f} μK → z = {z_m:+.2f}σ")
print(f"隨機 5° 盤 std: {rand_stds.mean():.2f} ± {rand_stds.std():.2f} μK")
print(f"節點 57 區域 std: {s57:.2f} μK → z = {z_s:+.2f}σ")

# 儲存
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "antipode_region.txt"), "w") as f:
    f.write(f"# O6 節點 57 對徑點區域掃描 (SMICA 4.17°)\n")
    f.write(f"# node57: T={T57:+.2f} uK, pct={pct:.1f}%, l={l_deg[57]:.2f}, b={b_deg[57]:.2f}\n")
    f.write(f"# node0: T={T0:+.2f} uK, pct={pct0:.1f}%, l={l_deg[0]:.2f}, b={b_deg[0]:.2f}\n")
    f.write(f"# region57_5deg: mean={m57:+.2f}, std={s57:.2f}, z_mean={z_m:+.2f}, z_std={z_s:+.2f}\n")
    f.write(f"# coverage_5deg: {cov*100:.1f}%\n")
    f.write(f"# node57_5deg_hot5:\n")
    for j in range(5):
        f.write(f"#   T={m[hot_idx[j]]*1e6:+.2f} @ ({l_h[j]:.2f},{b_h[j]:.2f})\n")
    f.write(f"# node0_5deg_cold5:\n")
    for j in range(5):
        f.write(f"#   T={m[cold_idx[j]]*1e6:+.2f} @ ({l_c[j]:.2f},{b_c[j]:.2f})\n")
print(f"\n✅ 已存: {OUT}/antipode_region.txt")
