#!/usr/bin/env python3
"""
19_l3_axis_alignment.py — O25: l=3 octupole 軸 vs A₅ 對稱軸對齊檢驗
====================================================================
開放問題 #2: l=3 軸同 A₅ 晶格有冇對齊?

方法:
1. 由 alm 計算 l=3 octupole 嘅對稱軸 (用 a3m 最大方向)
2. 對比 A₅ 候選軸:
   - node0 (冷斑) 方向
   - node9 方向
   - O26 r₀ 軸 (328.28°, +18.00°) — 對徑映射軸
   - 冷區中心方向
3. 統計: 隨機 1000 個 octupole 軸 vs A₅ 節點最近距離分佈
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, json

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
CACHE = os.path.join(BASE, "o25_scale_spectrum", "data", "smooth_cache_large")
DATA = os.path.join(BASE, "o25_scale_spectrum", "data")

m = hp.read_map(os.path.join(CACHE, "Commander_smooth15.0.fits"), field=0)
m_low = hp.ud_grade(m, 512)
nside_low = 512

print("=" * 70)
print("l=3 octupole 軸 vs A₅ 對稱軸對齊檢驗")
print("=" * 70)

# ============ 1. 計算 l=3 軸 ============
print("\n[1] l=3 octupole 主軸 (由 a3m 搵最大 |Y3m| 方向)")
alm = hp.map2alm(m_low, lmax=10)
n_alm = hp.Alm.getsize(10)
alm3 = np.zeros(n_alm, dtype=complex)
for mm in range(-3, 4):
    idx = hp.Alm.getidx(10, 3, abs(mm))
    alm3[idx] = alm[idx]
only3 = hp.alm2map(alm3, nside_low, lmax=10)

# 搵最冷像素 (octupole 冷極)
ipix_min = np.argmin(only3)
l_min, b_min = hp.pix2ang(nside_low, ipix_min, lonlat=True)
print(f"  l=3 最冷方向: (l={float(l_min):.2f}, b={float(b_min):.2f}), T={only3[ipix_min]*1e6:+.2f} μK")

# 搵最熱像素
ipix_max = np.argmax(only3)
l_max, b_max = hp.pix2ang(nside_low, ipix_max, lonlat=True)
print(f"  l=3 最熱方向: (l={float(l_max):.2f}, b={float(b_max):.2f}), T={only3[ipix_max]*1e6:+.2f} μK")

# ============ 2. A₅ 候選軸 ============
print("\n[2] A₅ 候選軸對比")
nodes = []
with open(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic

def angdist(l1, b1, l2, b2):
    l1, b1, l2, b2 = map(np.radians, [l1, b1, l2, b2])
    return np.degrees(np.arccos(np.clip(np.sin(b1)*np.sin(b2)+np.cos(b1)*np.cos(b2)*np.cos(l1-l2), -1, 1)))

candidates = {
    "node0 冷斑": (209.00, -57.00),
    "node9": (214.92, -31.16),
    "O26 r₀ 軸": (328.28, 18.00),
    "冷區中心": (197.74, -20.26),
    "node33": (191.4, -16.1),
}
l3_axis = (float(l_min), float(b_min))
print(f"  l=3 冷軸: ({l3_axis[0]:.2f}, {l3_axis[1]:.2f})")
print(f"  {'候選':<14} | {'距離 l=3 冷軸':>14} | {'距離 l=3 熱軸':>14}")
for name, (l, b) in candidates.items():
    d_cold = angdist(l, b, l3_axis[0], l3_axis[1])
    d_hot = angdist(l, b, float(l_max), float(b_max))
    print(f"  {name:<14} | {d_cold:>12.2f}° | {d_hot:>12.2f}°")

# ============ 3. 統計對照 ============
print("\n[3] 隨機方向 vs A₅ 節點最近距離 (對照)")
rng = np.random.default_rng(42)
gal_l = gal.l.deg; gal_b = gal.b.deg
nearest_random = []
for _ in range(2000):
    rl = rng.uniform(0, 360)
    rb = np.degrees(np.arcsin(rng.uniform(-1, 1)))
    nd = min(angdist(rl, rb, gal_l[i], gal_b[i]) for i in range(60))
    nearest_random.append(nd)
nearest_random = np.array(nearest_random)
print(f"  隨機方向最近節點: {nearest_random.mean():.2f} ± {nearest_random.std():.2f}°")

# l=3 軸最近節點
d_l3_nodes = [angdist(l3_axis[0], l3_axis[1], gal_l[i], gal_b[i]) for i in range(60)]
d_l3_min = min(d_l3_nodes)
i_l3 = np.argmin(d_l3_nodes)
print(f"  l=3 冷軸最近節點: node {i_l3} ({d_l3_min:.2f}°)")
z = (d_l3_min - nearest_random.mean()) / nearest_random.std()
print(f"  z = {z:+.2f}σ ({'對齊' if abs(z) > 2 else '冇對齊'})")

# 冷區中心最近節點 (重算)
d_cc_nodes = [angdist(197.74, -20.26, gal_l[i], gal_b[i]) for i in range(60)]
d_cc_min = min(d_cc_nodes)
i_cc = np.argmin(d_cc_nodes)
z_cc = (d_cc_min - nearest_random.mean()) / nearest_random.std()
print(f"  冷區中心最近節點: node {i_cc} ({d_cc_min:.2f}°) → z={z_cc:+.2f}σ")

# ============ 4. l=3 軸 vs 冷區中心 ============
print("\n[4] l=3 冷軸 ↔ 冷區中心")
d_l3_cc = angdist(l3_axis[0], l3_axis[1], 197.74, -20.26)
print(f"  l=3 冷軸距冷區中心: {d_l3_cc:.2f}°")
print(f"  {'一致' if d_l3_cc < 15 else '唔一致 (冷軸係另一處)'}")

out = {
    "l3_cold_axis": {"l": float(l_min), "b": float(b_min)},
    "l3_hot_axis": {"l": float(l_max), "b": float(b_max)},
    "candidates_dist": {name: {"d_cold": float(angdist(l, b, l3_axis[0], l3_axis[1])),
                                "d_hot": float(angdist(l, b, float(l_max), float(b_max)))} for name, (l, b) in candidates.items()},
    "l3_nearest_node": {"node": int(i_l3), "dist": float(d_l3_min), "z": float(z)},
    "coldcenter_nearest_node": {"node": int(i_cc), "dist": float(d_cc_min), "z": float(z_cc)},
    "l3_cc_sep": float(d_l3_cc),
    "random_nearest": {"mean": float(nearest_random.mean()), "std": float(nearest_random.std())},
}
with open(os.path.join(DATA, "l3_axis_alignment.json"), "w") as f:
    json.dump(out, f, indent=2)
print("\n✅ saved data/l3_axis_alignment.json")
