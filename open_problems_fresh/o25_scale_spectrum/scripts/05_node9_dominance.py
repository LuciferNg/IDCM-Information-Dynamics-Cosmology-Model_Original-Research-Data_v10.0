#!/usr/bin/env python3
"""
05_node9_dominance.py — O25: node9 大尺度主導深入分析
=====================================================
發現: node9 喺 10° 平滑時 rank 1/60 (最冷), 冷斑跌到 rank 3。
驗證:
1. node9 三地圖 @ 10° 一致性
2. 大尺度 rank 穩定性 (7°-10°)
3. 對照: 隨機 60 點 @ 10° 最冷節點 rank 分佈 (bootstrap)
4. node9 區域 @ 10° — 係咪擴展咗嘅冷結構?
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy import stats
import os, json

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
CACHE = "/tmp/cache_o3"
OUT = os.path.join(BASE, "o25_scale_spectrum")
DATA = os.path.join(OUT, "data")

nodes = []
with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = np.array(gal.l.deg)
b_deg = np.array(gal.b.deg)

def load(mname, scale):
    if mname == "SMICA":
        fname = f"SMICA_smooth{scale}.fits" if scale != 4.17 else "SMICA_smooth4.17.fits"
    else:
        fname = f"{mname}_{scale}.fits"
    return hp.read_map(os.path.join(CACHE, fname), field=0)

# ============ 1. node9 三地圖 @ 10° ============
print("=" * 70)
print("1. node9 @ 10° 三地圖一致性")
print("=" * 70)
for mname in ["SMICA", "NILC", "Commander"]:
    m = load(mname, 10.0)
    nside = hp.get_nside(m)
    pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
    T = m[pix] * 1e6
    rank = int((T <= T[9]).sum())
    print(f"  {mname}: node9 T={T[9]:+.2f} μK, rank {rank}/60")

# ============ 2. node9 vs 冷斑 大尺度 ============
print("\n" + "=" * 70)
print("2. node9 vs 冷斑 大尺度衰減比")
print("=" * 70)
for s in [5.0, 7.0, 10.0]:
    m = load("SMICA", s)
    nside = hp.get_nside(m)
    pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
    T = m[pix] * 1e6
    print(f"  {s:>4.1f}°: node0={T[0]:+7.2f}  node9={T[9]:+7.2f}  node9/node0 = {T[9]/T[0]:.3f}")

# ============ 3. Bootstrap: 隨機 60 點最冷 rank ============
print("\n" + "=" * 70)
print("3. Bootstrap — 隨機 60 點最冷值分佈 @ 10°")
print("=" * 70)
rng = np.random.default_rng(42)
m = load("SMICA", 10.0)
nside = hp.get_nside(m)
npix = hp.nside2npix(nside)
# 全圖隨機抽 60 點 × 1000 次, 記錄最冷值
N_BOOT = 1000
coldest = []
for _ in range(N_BOOT):
    rpix = rng.integers(0, npix, 60)
    coldest.append(m[rpix].min() * 1e6)
coldest = np.array(coldest)
# node9 嘅值
pix9 = hp.ang2pix(nside, l_deg[9], b_deg[9], lonlat=True)
T9 = m[pix9] * 1e6
print(f"  node9 @ 10° = {T9:+.2f} μK")
print(f"  隨機 60 點最冷: mean={coldest.mean():.1f}±{coldest.std():.1f} μK")
z = (T9 - coldest.mean()) / coldest.std()
pct = (coldest <= T9).mean() * 100
print(f"  z = {z:.2f}σ, percentile = {pct:.1f}%")
print(f"  結論: node9 大尺度極端性 {'顯著' if pct < 5 else '唔顯著'}")

# 對比冷斑 node0
pix0 = hp.ang2pix(nside, l_deg[0], b_deg[0], lonlat=True)
T0 = m[pix0] * 1e6
z0 = (T0 - coldest.mean()) / coldest.std()
pct0 = (coldest <= T0).mean() * 100
print(f"  冷斑 node0 @ 10° = {T0:+.2f} μK, z={z0:.2f}σ, percentile={pct0:.1f}%")

# ============ 4. node9 區域 10° 結構 ============
print("\n" + "=" * 70)
print("4. node9 區域 @ 10° (10° 半徑內 mean T)")
print("=" * 70)
# 用 healpy query_disc
m = load("SMICA", 10.0)
vec9 = hp.pix2vec(nside, pix9)
radius = np.radians(10.0)
disc = hp.query_disc(nside, vec9, radius)
disc_mask = np.zeros(npix, dtype=bool)
disc_mask[disc] = True
disc_vals = m[disc_mask]
print(f"  node9 10° 半徑內: n={len(disc_vals)}, mean T = {disc_vals.mean()*1e6:+.2f} μK")
# 全圖 mean
print(f"  全圖 mean (10° 平滑): {m.mean()*1e6:+.2f} μK")
print(f"  區域 vs 全圖: {disc_vals.mean()*1e6 - m.mean()*1e6:+.2f} μK")

# 冷斑區域對照
disc0 = hp.query_disc(nside, hp.pix2vec(nside, pix0), radius)
disc0_vals = m[disc0]
print(f"  冷斑 10° 半徑內: n={len(disc0_vals)}, mean T = {disc0_vals.mean()*1e6:+.2f} μK")

# 隨機區域對照 (100 個隨機方向)
rng2 = np.random.default_rng(7)
random_discs = []
for _ in range(100):
    rvec = rng2.standard_normal(3)
    rvec /= np.linalg.norm(rvec)
    rd = hp.query_disc(nside, rvec, radius)
    random_discs.append(m[rd].mean() * 1e6)
random_discs = np.array(random_discs)
print(f"\n  隨機 100 個 10° 區域 mean: {random_discs.mean():+.2f} ± {random_discs.std():.2f} μK")
zn = (disc_vals.mean()*1e6 - random_discs.mean()) / random_discs.std()
print(f"  node9 區域 z = {zn:.2f}σ (vs 隨機區域)")
z0n = (disc0_vals.mean()*1e6 - random_discs.mean()) / random_discs.std()
print(f"  冷斑區域 z = {z0n:.2f}σ (vs 隨機區域)")

# 儲存
out = {
    "node9_10deg": {"T": float(T9), "rank": int((m[pix] * 1e6 <= T9).sum())},
    "bootstrap": {"mean": float(coldest.mean()), "std": float(coldest.std()), "z": float(z), "percentile": float(pct)},
    "region": {"node9_mean": float(disc_vals.mean()*1e6), "node0_mean": float(disc0_vals.mean()*1e6),
               "random_mean": float(random_discs.mean()), "random_std": float(random_discs.std()),
               "node9_z": float(zn), "node0_z": float(z0n)},
}
with open(os.path.join(DATA, "node9_dominance.json"), "w") as f:
    json.dump(out, f, indent=2)
print("\n✅ saved data/node9_dominance.json")
