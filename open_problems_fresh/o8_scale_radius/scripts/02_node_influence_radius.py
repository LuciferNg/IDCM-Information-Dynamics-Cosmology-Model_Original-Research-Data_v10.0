#!/usr/bin/env python3
"""
02_node_influence_radius.py — O8 實測節點影響半徑
==================================================
用 SMICA 平滑 cache 直接量度「節點影響範圍」:
- 每個節點嘅角徑向 profile: 距節點 θ 處嘅平均 |ΔT|
- 影響半徑定義: profile 跌到半峰 (或某基準) 嘅 θ
- 對比 26.09/2π = 4.15° 預測

用 o5_catalog_compare/data/smooth_cache/ 嘅 cache (唔使重平滑)
"""
import healpy as hp
import numpy as np
import math
from astropy.coordinates import SkyCoord
import astropy.units as u

phi = (1 + 5**0.5) / 2

# ===== 1. 載入節點 =====
nodes = []
with open("/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg
print(f"60 節點載入 ✅")

# ===== 2. 載入平滑 cache (多尺度) =====
cache_dir = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare/data/smooth_cache"
scales = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]

maps = {}
for s in scales:
    fn = f"{cache_dir}/smica2_smooth{s}.fits"
    try:
        m = hp.read_map(fn, field=0)
        maps[s] = hp.remove_dipole(m)
        print(f"  載入 {s}°: nside={hp.get_nside(m)}, std={maps[s].std()*1e6:.1f} μK")
    except Exception as e:
        print(f"  ❌ {s}°: {e}")

# ===== 3. 角徑向 profile =====
def radial_profile(m, nside, center_l, center_b, rmax=30, nbins=60):
    """以中心為圓心, 量度每環嘅平均溫度"""
    # 採樣環 (用 vector 方法)
    center_vec = hp.ang2vec(center_l, center_b, lonlat=True)
    # 喺中心附近採樣 pixels (用 query_disc)
    pix = hp.query_disc(nside, center_vec, np.radians(rmax))
    theta = hp.pix2ang(nside, pix, lonlat=False)[0]  # 極角
    # 轉成距中心角距
    # 用 center 喺 equator 嘅技巧: 直接計中心向量同每 pixel 向量嘅角
    pix_vecs = np.array(hp.pix2vec(nside, pix)).T
    angs = np.degrees(np.arccos(np.clip(pix_vecs @ center_vec, -1, 1)))
    vals = m[pix]
    # 分 bin
    bins = np.linspace(0, rmax, nbins+1)
    idx = np.digitize(angs, bins[1:-1])
    prof = []
    for i in range(nbins):
        sel = idx == i
        if sel.sum() > 0:
            prof.append(( (bins[i]+bins[i+1])/2, np.mean(vals[sel]) ))
    prof = np.array(prof)
    return prof

# 只用節點 0 (冷斑) 做詳細 profile + 全部節點平均
print("\n=== 角徑向 profile (節點 0 = 冷斑, 4.17° 平滑) ===")
m = maps[4.17]
nside = hp.get_nside(m)
prof = radial_profile(m, nside, l_deg[0], b_deg[0], rmax=30, nbins=60)

# 影響半徑: profile 由中心值跌到中心值一半 (半峰)
T0 = m[hp.ang2pix(nside, l_deg[0], b_deg[0], lonlat=True)]
print(f"冷斑中心 T = {T0*1e6:.1f} μK")
half = T0/2
# 搵第一個低過 half 嘅 bin
for r, v in prof:
    if v < half:
        print(f"  半峰半徑: ~{r:.2f}° (T={v*1e6:.1f} μK, 中心 {T0*1e6:.1f})")
        break

# 全部節點平均 profile (4.17° 平滑)
print("\n=== 全部 60 節點平均 |ΔT| profile (4.17° 平滑) ===")
all_prof = np.zeros((60, len(prof)))
for i in range(60):
    p = radial_profile(m, nside, l_deg[i], b_deg[i], rmax=30, nbins=60)
    all_prof[i] = p[:, 1]
mean_prof = all_prof.mean(axis=0)
abs_prof = np.abs(all_prof).mean(axis=0)

print(f"{'θ (°)':>8}{'mean T (μK)':>14}{'mean |T| (μK)':>16}")
for j in range(0, len(mean_prof), 4):
    print(f"{prof[j,0]:>8.2f}{mean_prof[j]*1e6:>14.2f}{abs_prof[j]*1e6:>16.2f}")

# ===== 4. 影響半徑定義 =====
# 定義 A: 平均 |ΔT| 跌到 4° 內均值嘅 1/e
base = np.abs(all_prof[:, -1]).mean()  # 30° 基準 (遠離節點)
center_abs = np.abs(all_prof[:, 0]).mean()
print(f"\n中心 mean|T| = {center_abs*1e6:.2f} μK, 30° 基準 = {base*1e6:.2f} μK")
print(f"中心/基準比 = {center_abs/base:.2f}")

# 半峰半徑 (per 節點, 用 |T| profile)
half_radii = []
for i in range(60):
    p = np.abs(all_prof[i])
    c0 = p[0]
    target = (c0 + base)/2
    for j in range(1, len(p)):
        if p[j] < target:
            half_radii.append(prof[j,0])
            break
half_radii = np.array(half_radii)
print(f"\n半峰半徑 (mean|T|): median={np.median(half_radii):.2f}°, mean={half_radii.mean():.2f}°")
print(f"  分佈: min={half_radii.min():.2f}, max={half_radii.max():.2f}")

# ===== 5. 對比預測 =====
print("\n=== 對比預測 ===")
preds = {
    "a/2π = 26.09/2π": 26.091346/(2*np.pi),
    "180/44 (半波)": 180/44,
    "Vielva R8": 4.17,
}
for name, val in preds.items():
    print(f"  {name:<20} = {val:.3f}°")
print(f"  實測半峰半徑 (median) = {np.median(half_radii):.3f}°")
dev = abs(np.median(half_radii) - 26.091346/(2*np.pi))/(26.091346/(2*np.pi))*100
print(f"  實測 vs a/2π 偏差: {dev:.1f}%")

# 儲存
np.save("/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o8_scale_radius/data/radial_profiles.npy", all_prof)
np.save("/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o8_scale_radius/data/half_radii.npy", half_radii)
with open("/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o8_scale_radius/data/radial_summary.txt", "w") as f:
    f.write(f"# O8 節點影響半徑實測 (SMICA 4.17° 平滑 cache)\n")
    f.write(f"# 中心 mean|T| = {center_abs*1e6:.2f} μK\n")
    f.write(f"# 30° 基準 = {base*1e6:.2f} μK\n")
    f.write(f"# 半峰半徑 median = {np.median(half_radii):.3f}°, mean = {half_radii.mean():.3f}°\n")
    f.write(f"# 預測 a/2π = {26.091346/(2*np.pi):.4f}°, 180/44 = {180/44:.4f}°\n")
print("\n✅ 已存: data/radial_profiles.npy, data/half_radii.npy, data/radial_summary.txt")
