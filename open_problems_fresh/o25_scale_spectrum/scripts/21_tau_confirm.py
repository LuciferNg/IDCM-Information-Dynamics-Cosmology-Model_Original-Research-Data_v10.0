#!/usr/bin/env python3
"""
21_tau_confirm.py — O25: 25°/30° 平滑確認冷區中心 τ
====================================================
用 NILC/Commander raw (NESTED→RING) 平滑 25°/30° (nside=512 夠),
計冷區中心 20° 盤溫度, 連同 12/15/20° 確認衰減 τ。
"""
import healpy as hp
import numpy as np
import os, json

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
O25 = os.path.join(BASE, "o25_scale_spectrum")
DATA = os.path.join(O25, "data")
os.makedirs(DATA, exist_ok=True)

cold_center = {"l": 197.74, "b": -20.26}

# raw 地圖 (NESTED)
print("載入 raw NILC/Commander (NESTED)...")
maps = {}
for name in ["NILC", "Commander"]:
    m = hp.read_map(f"/tmp/{name.lower()}.fits", field=0, nest=True)
    maps[name] = m
    print(f"  {name}: nside={hp.get_nside(m)}, finite={np.isfinite(m).all()}")

# 平滑 25°/30° (直接喺 nside=512 做)
print("\n平滑 25°/30° (nside=512)...")
results = {}
for name, m_raw in maps.items():
    for fw in [25.0, 30.0]:
        m512 = hp.ud_grade(m_raw, 512, order_in="NESTED", order_out="RING")
        m_smooth = hp.smoothing(m512, fwhm=np.radians(fw))
        # 冷區中心 20° 盤
        vec = hp.ang2vec(cold_center["l"], cold_center["b"], lonlat=True)
        d = hp.query_disc(512, vec, np.radians(20.0))
        T = m_smooth[d].mean() * 1e6
        results[f"{name}_{fw}"] = T
        print(f"  {name} {fw}°: 20°盤 = {T:+.2f} μK")

# 連同已有 12/15/20°
print("\n冷區中心 20° 盤衰減 (全部尺度):")
scales_all = [12.0, 15.0, 20.0, 25.0, 30.0]
T_all = []
for s in scales_all:
    vals = []
    for mname in ["NILC", "Commander"]:
        key = f"{mname}_{s}"
        if key in results:
            vals.append(results[key])
        else:
            # 讀已有 cache
            fname = os.path.join(O25, "data", "smooth_cache_large", f"{mname}_smooth{s}.fits")
            if os.path.exists(fname):
                mm = hp.read_map(fname, field=0)
                mm_low = hp.ud_grade(mm, 512)
                d = hp.query_disc(512, hp.ang2vec(cold_center["l"], cold_center["b"], lonlat=True), np.radians(20.0))
                vals.append(mm_low[d].mean()*1e6)
    if vals:
        T_all.append((s, np.mean(vals)))
        print(f"  {s}°: {np.mean(vals):+.2f} μK (NILC/Commander avg)")

# 衰減擬合 (線性 + 指數)
scales_arr = np.array([t[0] for t in T_all])
T_arr = np.array([t[1] for t in T_all])
slope, intercept = np.polyfit(scales_arr, T_arr, 1)
print(f"\n線性擬合: slope={slope:.3f} μK/°, intercept={intercept:.2f} μK")
print(f"  (全尺度範圍衰減: {T_arr[-1]-T_arr[0]:+.2f} μK over {scales_arr[-1]-scales_arr[0]}°)")

# 相對變化率 (每 10°)
rate = (T_arr[-1] - T_arr[0]) / (scales_arr[-1] - scales_arr[0]) * 10
print(f"  每 10° 衰減: {rate:.2f} μK")

# 特徵尺度: 半衰尺度 (衰到一半)
T_half = (T_arr[0] + T_arr[-1]) / 2
print(f"  中點溫度: {T_half:.2f} μK")

out = {
    "cold_center": cold_center,
    "results": results,
    "scales": [float(s) for s in scales_arr],
    "T_avg": [float(t) for t in T_arr],
    "linear": {"slope": float(slope), "intercept": float(intercept)},
    "decay_per_10deg": float(rate),
}
with open(os.path.join(DATA, "tau_confirm.json"), "w") as f:
    json.dump(out, f, indent=2)
print("\n✅ saved data/tau_confirm.json")
