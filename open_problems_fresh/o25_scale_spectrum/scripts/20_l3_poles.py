#!/usr/bin/env python3
"""
20_l3_poles.py — O25: l=3 所有極點定位 + 冷區中心對照
======================================================
Octupole Y3m 有 6 個瓣 (3 冷 + 3 熱)。全局最冷 (82,17) 唔係冷區中心,
但冷區中心可能係另一個局部冷極!

方法:
1. 搵 l=3 地圖所有局部極小值 (冷極) + 極大值 (熱極)
2. 對照: 冷區中心 / node9 / node0 係咪局部冷極?
3. 統計: 局部冷極同 A₅ 節點距離
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
print("l=3 所有極點定位 + 冷區中心對照")
print("=" * 70)

# l=3 地圖
alm = hp.map2alm(m_low, lmax=10)
n_alm = hp.Alm.getsize(10)
alm3 = np.zeros(n_alm, dtype=complex)
for mm in range(-3, 4):
    idx = hp.Alm.getidx(10, 3, abs(mm))
    alm3[idx] = alm[idx]
only3 = hp.alm2map(alm3, nside_low, lmax=10)

# ============ 1. 搵局部極值 ============
print("\n[1] l=3 局部極值 (冷/熱)")
# nside=512 已經夠 (像素 6.9', l=3 尺度極大)
nside_hi = 512
only3_hi = only3  # 已有
npix_hi = hp.nside2npix(nside_hi)
neigh = hp.get_all_neighbours(nside_hi, np.arange(npix_hi))
neigh = neigh.reshape(8, npix_hi).T
neigh = np.where(neigh < 0, np.arange(npix_hi)[:, None], neigh)  # 邊界處理

is_local_min = (only3_hi[:, None] < only3_hi[neigh]).all(axis=1)
is_local_max = (only3_hi[:, None] > only3_hi[neigh]).all(axis=1)
pix_min = np.where(is_local_min)[0]
pix_max = np.where(is_local_max)[0]
print(f"  局部極小: {len(pix_min)}, 局部極大: {len(pix_max)}")

# 按值排序, 攞 top 冷極
cold_vals = only3_hi[pix_min]
hot_vals = only3_hi[pix_max]
order_c = np.argsort(cold_vals)[:6]
order_h = np.argsort(hot_vals)[-6:]

def angdist(l1, b1, l2, b2):
    l1, b1, l2, b2 = map(np.radians, [l1, b1, l2, b2])
    return np.degrees(np.arccos(np.clip(np.sin(b1)*np.sin(b2)+np.cos(b1)*np.cos(b2)*np.cos(l1-l2), -1, 1)))

print("\n  冷極 (top 6):")
cold_poles = []
for i in order_c:
    l, b = hp.pix2ang(2048, pix_min[i], lonlat=True)
    cold_poles.append((float(l), float(b), float(cold_vals[i])*1e6))
    print(f"    ({float(l):>7.2f}, {float(b):>+7.2f}): {float(cold_vals[i])*1e6:+.2f} μK")

print("\n  熱極 (top 6):")
hot_poles = []
for i in order_h:
    l, b = hp.pix2ang(2048, pix_max[i], lonlat=True)
    hot_poles.append((float(l), float(b), float(hot_vals[i])*1e6))
    print(f"    ({float(l):>7.2f}, {float(b):>+7.2f}): {float(hot_vals[i])*1e6:+.2f} μK")

# ============ 2. 冷區中心 vs 冷極 ============
print("\n[2] 冷區中心 / node9 / node0 vs l=3 冷極")
targets = {
    "冷區中心": (197.74, -20.26),
    "node9": (214.92, -31.16),
    "node0 冷斑": (209.00, -57.00),
}
for tname, (tl, tb) in targets.items():
    d_min = 999
    best = None
    for cl, cb, cv in cold_poles:
        d = angdist(tl, tb, cl, cb)
        if d < d_min:
            d_min = d
            best = (cl, cb, cv)
    print(f"  {tname}: 最近冷極 ({best[0]:.2f}, {best[1]:.2f}) = {best[2]:+.2f} μK, 距離 {d_min:.2f}°")

# ============ 3. 冷區中心係咪局部冷極? ============
print("\n[3] 冷區中心喺 l=3 地圖嘅值")
pix_cc = hp.ang2pix(nside_hi, 197.74, -20.26, lonlat=True)
pix_n9 = hp.ang2pix(nside_hi, 214.92, -31.16, lonlat=True)
pix_n0 = hp.ang2pix(nside_hi, 209.00, -57.00, lonlat=True)
print(f"  冷區中心 l=3 值: {only3_hi[pix_cc]*1e6:+.2f} μK")
print(f"  node9 l=3 值:    {only3_hi[pix_n9]*1e6:+.2f} μK")
print(f"  node0 l=3 值:    {only3_hi[pix_n0]*1e6:+.2f} μK")
print(f"  冷極最小值: {cold_vals[order_c[0]]*1e6:+.2f} μK")

# ============ 4. 對徑結構 ============
print("\n[4] 冷極對徑關係 (octupole 6 瓣)")
print("  冷極對:")
for i in range(3):
    l1, b1, v1 = cold_poles[i]
    l2, b2, v2 = cold_poles[i+3] if i+3 < len(cold_poles) else cold_poles[i]
    d = angdist(l1, b1, (l2+180) % 360, -b2)
    print(f"    ({l1:.1f},{b1:+.1f}) ↔ 對徑 ({l2:.1f},{b2:+.1f}): 距離 {d:.2f}°")

out = {
    "cold_poles": [{"l": p[0], "b": p[1], "T": p[2]} for p in cold_poles],
    "hot_poles": [{"l": p[0], "b": p[1], "T": p[2]} for p in hot_poles],
    "targets": {},
}
for tname, (tl, tb) in targets.items():
    d_min = 999; best = None
    for cl, cb, cv in cold_poles:
        d = angdist(tl, tb, cl, cb)
        if d < d_min:
            d_min = d; best = (cl, cb, cv)
    out["targets"][tname] = {"nearest_cold_pole": {"l": best[0], "b": best[1], "T": best[2]}, "dist": float(d_min)}
out["l3_values"] = {"coldcenter": float(only3_hi[pix_cc]*1e6), "node9": float(only3_hi[pix_n9]*1e6), "node0": float(only3_hi[pix_n0]*1e6)}
with open(os.path.join(DATA, "l3_poles.json"), "w") as f:
    json.dump(out, f, indent=2)
print("\n✅ saved data/l3_poles.json")
