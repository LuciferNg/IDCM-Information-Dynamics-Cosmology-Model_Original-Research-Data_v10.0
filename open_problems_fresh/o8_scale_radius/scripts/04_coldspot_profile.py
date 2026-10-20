#!/usr/bin/env python3
"""
04_coldspot_profile.py — O8 冷斑本體 profile (正確半徑定義)
=============================================================
核心: 節點影響範圍 4.17° 係「冷斑凹陷」嘅半徑
用冷斑 (節點 0) 本體溫度 profile 量度半峰半徑
→ 對比 26.09/2π = 4.153° 同 180/44 = 4.091°
"""
import healpy as hp
import numpy as np
import math
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy.interpolate import interp1d

a_edge = 26.091346
phi = (1 + 5**0.5) / 2

# ===== 1. 節點 =====
nodes = []
with open("/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg

cache_dir = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare/data/smooth_cache"

# ===== 2. 冷斑徑向 profile (多尺度) =====
print("=== 冷斑 (節點 0) 徑向 profile ===")
scales = [3.0, 4.0, 4.17, 5.0, 7.0]
print(f"冷斑位置: l={l_deg[0]:.2f}°, b={b_deg[0]:.2f}°")

for s in scales:
    m = hp.remove_dipole(hp.read_map(f"{cache_dir}/smica2_smooth{s}.fits", field=0))
    nside = hp.get_nside(m)
    center_vec = hp.ang2vec(l_deg[0], b_deg[0], lonlat=True)
    pix = hp.query_disc(nside, center_vec, np.radians(12))
    pix_vecs = np.array(hp.pix2vec(nside, pix)).T
    angs = np.degrees(np.arccos(np.clip(pix_vecs @ center_vec, -1, 1)))
    vals = m[pix]
    # 分 bin 0.25°
    bins = np.linspace(0, 12, 49)
    idx = np.digitize(angs, bins[1:-1])
    prof = []
    for i in range(48):
        sel = idx == i
        if sel.sum() > 0:
            prof.append(((bins[i]+bins[i+1])/2, np.mean(vals[sel])))
    prof = np.array(prof)
    r, v = prof[:, 0], prof[:, 1]
    T0 = v[0]
    # 半峰 (凹陷: 由 -134 升到背景 ~0)
    target = T0/2
    f = interp1d(v, r, kind='linear', bounds_error=False, fill_value='extrapolate')
    hr = float(f(target))
    print(f"  {s:>5}° 平滑: 中心 T={T0*1e6:7.1f} μK, 半峰半徑={hr:5.2f}° (target {target*1e6:.1f} μK)")
    # 印 profile 幾個點
    for rr, vv in prof[::4]:
        print(f"      θ={rr:5.2f}°: T={vv*1e6:7.1f} μK")

print(f"""
預測比較:
  a/2π = {a_edge/(2*np.pi):.4f}°
  180/44 = {180/44:.4f}°
  26.09×ε = {a_edge*(1/phi)/4:.4f}°
""")

# ===== 3. 冷斑半峰半徑 vs 尺度 (最佳尺度搵半峰) =====
print("\n=== 冷斑半峰半徑隨平滑尺度 ===")
all_scales = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
print(f"{'尺度':>6}{'中心T':>10}{'半峰半徑':>10}{'a/2π偏差':>10}")
for s in all_scales:
    m = hp.remove_dipole(hp.read_map(f"{cache_dir}/smica2_smooth{s}.fits", field=0))
    nside = hp.get_nside(m)
    center_vec = hp.ang2vec(l_deg[0], b_deg[0], lonlat=True)
    pix = hp.query_disc(nside, center_vec, np.radians(15))
    pix_vecs = np.array(hp.pix2vec(nside, pix)).T
    angs = np.degrees(np.arccos(np.clip(pix_vecs @ center_vec, -1, 1)))
    vals = m[pix]
    bins = np.linspace(0, 15, 75)
    idx = np.digitize(angs, bins[1:-1])
    prof = np.array([((bins[i]+bins[i+1])/2, np.mean(vals[idx==i])) for i in range(74) if (idx==i).sum() > 0])
    r, v = prof[:, 0], prof[:, 1]
    T0 = v[0]
    # 半峰: 由 T0 升到 0 嘅一半
    target = T0/2
    # 搵 v 由 T0 方向穿越 target 嘅位
    hr = np.nan
    for j in range(1, len(v)):
        if (v[j] - target) * (v[j-1] - target) <= 0:
            # 線性插值
            t = (target - v[j-1])/(v[j] - v[j-1])
            hr = r[j-1] + t*(r[j] - r[j-1])
            break
    dev = abs(hr - a_edge/(2*np.pi))/(a_edge/(2*np.pi))*100 if hr == hr else np.nan
    print(f"{s:>6}{T0*1e6:>10.1f}{hr:>10.2f}{dev:>9.1f}%" if hr == hr else f"{s:>6}{T0*1e6:>10.1f}{'N/A':>10}")

# ===== 4. 儲存 (完整數據, 唔係得 header) =====
with open("/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o8_scale_radius/data/coldspot_profile.txt", "w") as f:
    f.write(f"# O8 冷斑 profile 分析\n")
    f.write(f"# 冷斑 (209°,-57°) 中心溫度 + 半峰半徑 per 平滑尺度\n")
    f.write(f"# 格式: scale centerT_uK HWHM_deg\n")
    # 重新收集全部尺度數據
    for s in all_scales:
        m = hp.remove_dipole(hp.read_map(f"{cache_dir}/smica2_smooth{s}.fits", field=0))
        nside = hp.get_nside(m)
        center_vec = hp.ang2vec(l_deg[0], b_deg[0], lonlat=True)
        pix = hp.query_disc(nside, center_vec, np.radians(15))
        pix_vecs = np.array(hp.pix2vec(nside, pix)).T
        angs = np.degrees(np.arccos(np.clip(pix_vecs @ center_vec, -1, 1)))
        vals = m[pix]
        bins = np.linspace(0, 15, 75)
        idx = np.digitize(angs, bins[1:-1])
        prof = np.array([((bins[i]+bins[i+1])/2, np.mean(vals[idx==i])) for i in range(74) if (idx==i).sum() > 0])
        r, v = prof[:, 0], prof[:, 1]
        T0 = v[0]
        target = T0/2
        hr = np.nan
        for j in range(1, len(v)):
            if (v[j] - target) * (v[j-1] - target) <= 0:
                t = (target - v[j-1])/(v[j] - v[j-1])
                hr = r[j-1] + t*(r[j] - r[j-1])
                break
        f.write(f"{s} {T0*1e6:.1f} {hr:.3f}\n")
print("✅ 已存: data/coldspot_profile.txt (完整數據)")
