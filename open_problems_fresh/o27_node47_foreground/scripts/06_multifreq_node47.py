#!/usr/bin/env python3
"""
06_multifreq_node47.py — O27: 多頻譜檢查 (100/143/217/353 GHz)
================================================================
核心判決: node47 嘅冷信號係 CMB-like (平譜) 定 foreground-like (光譜上升)?

方法: 每個頻率 map (R3.01 full, NESTED→RING) 喺目標點 3.0° 盤平均。
目標點:
  - node47 (313.47°, -8.58°)  — 問題點
  - node0 (209.00°, -57.00°)  — 冷斑對照 (已知真實 CMB 冷結構)
  - node9 (214.92°, -31.16°)  — 第二冷結構 (O21 確認)
  - 高緯隨機 3 點              — 純 CMB 背景
  - 銀河面前景點 (b≈0)        — 前景對照 (dust/synchrotron)

診斷 (K_CMB 單位):
  - CMB: 平譜 (100≈143≈217)
  - Dust: 217>143, 353>>217 (ν^1.5-2 喺 K_CMB)
  - Synchrotron/free-free: 100>143 (低頻上升)
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, json, time

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
OUT = os.path.join(BASE, "o27_node47_foreground")
DATA = os.path.join(OUT, "data")

FREQ_MAPS = {
    100: os.path.join(DATA, "HFI_SkyMap_100_2048_R3.01_full.fits"),
    143: os.path.join(DATA, "HFI_SkyMap_143_2048_R3.01_full.fits"),
    217: os.path.join(DATA, "HFI_SkyMap_217_2048_R3.01_full.fits"),
    353: os.path.join(DATA, "HFI_SkyMap_353_2048_R3.01_full.fits"),
}

# 目標點 (l, b, 名稱)
TARGETS = [
    (313.47, -8.58,  "node47 (問題點)"),
    (209.00, -57.00, "node0 冷斑 (真實 CMB 冷結構)"),
    (214.92, -31.16, "node9 (第二冷結構)"),
    (180.00, +30.00, "高緯隨機 A"),
    (300.00, +40.00, "高緯隨機 B"),
    (60.00,  -35.00, "高緯隨機 C"),
    (313.47,  -0.50, "銀河面前景點 (node47 下方 b≈0)"),
    (0.00,   +0.50,  "銀河中心前景點"),
]

RAD_DEG = 3.0  # 盤半徑 (對應 3.0° 尺度)

print("=" * 70)
print("O27: 多頻譜檢查 (100/143/217/353 GHz)")
print("=" * 70)

# 載入所有頻率 map (NESTED → RING)
maps = {}
for freq, path in FREQ_MAPS.items():
    if not os.path.exists(path) or os.path.getsize(path) < 2e9:
        print(f"  [skip] {freq} GHz 未下載完成 ({path})")
        continue
    t0 = time.time()
    m = hp.read_map(path, field=0, nest=True)
    m = hp.reorder(m, n2r=True)
    # fill value 處理: 非有限 或 |T|>1e-3 K 視為 bad
    bad = (~np.isfinite(m)) | (np.abs(m) > 1e-3)
    if bad.any():
        print(f"  {freq} GHz: {bad.sum()} bad pixels ({bad.mean()*100:.2f}%), set to NaN")
        m = np.where(bad, np.nan, m)
    maps[freq] = m
    print(f"  {freq} GHz: nside={hp.get_nside(m)}, std={np.nanstd(m)*1e6:.1f} μK ({time.time()-t0:.0f}s)")

if len(maps) < 4:
    print("\n⚠️ 頻率 map 未齊 — 等完成再跑")
    raise SystemExit(1)

# 抽值 (3° 盤平均)
print(f"\n{'目標':<28}{'100GHz':>10}{'143GHz':>10}{'217GHz':>10}{'353GHz':>10}"
      f"{'217/143':>9}{'353/217':>9}")
rows = []
for l, b, name in TARGETS:
    vals = {}
    nside = hp.get_nside(maps[100])
    vec = hp.ang2vec(l, b, lonlat=True)
    pix = hp.query_disc(nside, vec, np.radians(RAD_DEG))
    for freq, m in maps.items():
        vals[freq] = float(np.nanmean(m[pix]) * 1e6)
    r217_143 = vals[217] / vals[143] if abs(vals[143]) > 1 else float('nan')
    r353_217 = vals[353] / vals[217] if abs(vals[217]) > 1 else float('nan')
    rows.append({"name": name, "l": l, "b": b, **{f"T{f}": vals[f] for f in [100, 143, 217, 353]},
                 "r217_143": r217_143, "r353_217": r353_217})
    print(f"{name:<28}{vals[100]:>+10.1f}{vals[143]:>+10.1f}{vals[217]:>+10.1f}{vals[353]:>+10.1f}"
          f"{r217_143:>9.2f}{r353_217:>9.2f}")

with open(os.path.join(DATA, "multifreq_node47.json"), "w") as f:
    json.dump({"rad_deg": RAD_DEG, "rows": rows}, f, indent=2)
print(f"\n✅ 已存 data/multifreq_node47.json")
