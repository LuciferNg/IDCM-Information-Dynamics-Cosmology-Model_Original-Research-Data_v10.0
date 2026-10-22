#!/usr/bin/env python3
"""
09_node53_multifreq.py — O30: node53 熱異常多頻譜檢查 (O27 流程)
==================================================================
O30 離散性發現 node53 (+112 μK, b=−34°) 係跨尺度穩定熱異常。
本 script 用 O27 node47 相同流程判定: 真實 CMB 定前景污染?

方法: Planck HFI 100/143/217/353 GHz (R3.01 full) 3.0° FWHM 平滑,
     抽 node53 單像素 + 3° 盤平均, 對照:
       - node0 (冷斑, 已知真實 CMB 冷) — 光譜基準
       - node9 (第二冷, O21 確認) — 光譜基準
       - node47 (O27 已證實前景) — 前景基準
       - 高緯隨機 3 點 — 純 CMB 背景
       - 銀河面前景點 (b≈0) — dust/synchrotron 對照

診斷 (K_CMB 單位):
  - CMB: 平譜 (100≈143≈217), |217/143|≈1
  - Dust: 217>143, 353>>217 (ν^1.5-2 上升)
  - Synchrotron/free-free: 100>143 (低頻上升)
判定:
  🟢 平譜 (三頻譜一致) → 真實 CMB 熱異常
  🔴 光譜上升 → 前景污染
  🟡 混合 → 部分污染
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, json, time

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
DATA27 = os.path.join(BASE, "o27_node47_foreground/data")
CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")
OUT = os.path.join(BASE, "o30_node_systematics/data")

FREQ_MAPS = {
    100: os.path.join(DATA27, "HFI_SkyMap_100_2048_R3.01_full.fits"),
    143: os.path.join(DATA27, "HFI_SkyMap_143_2048_R3.01_full.fits"),
    217: os.path.join(DATA27, "HFI_SkyMap_217_2048_R3.01_full.fits"),
    353: os.path.join(DATA27, "HFI_SkyMap_353_2048_R3.01_full.fits"),
}
FWHM = 3.0
SIGMA = np.radians(FWHM) / (2 * np.sqrt(2 * np.log(2)))

# 目標點 (l, b, 名稱) — node53 用 O3 node_temps 嘅銀道座標
TARGETS = [
    (319.50, -34.20, "node53 (熱異常? b=-34°)"),
    (209.00, -57.00, "node0 冷斑 (CMB 基準)"),
    (214.92, -31.16, "node9 第二冷 (CMB 基準)"),
    (313.47,  -8.58, "node47 (前景基準 O27)"),
    (180.00, +30.00, "高緯隨機 A"),
    (300.00, +40.00, "高緯隨機 B"),
    (60.00,  -35.00, "高緯隨機 C"),
    (319.50,  -1.00, "銀河面同經度點"),
    (0.00,   +0.50,  "銀河中心點"),
]

print("=" * 70)
print(f"O30: node53 多頻譜檢查 ({FWHM}° FWHM 平滑) — O27 流程")
print("=" * 70)

# ---------- 載入頻率 map (NESTED→RING, 3.0° 平滑) ----------
maps = {}
for freq, path in FREQ_MAPS.items():
    if not os.path.exists(path) or os.path.getsize(path) < 2e9:
        print(f"  [skip] {freq} GHz 未下載完成")
        continue
    t0 = time.time()
    m = hp.read_map(path, field=0, nest=True)
    m = hp.reorder(m, n2r=True)
    bad = (~np.isfinite(m)) | (np.abs(m) > 1e-3)
    m = np.where(bad, np.nan, m)
    mask_ok = np.isfinite(m)
    m0 = np.where(mask_ok, m, 0.0)
    sm = hp.smoothing(m0, sigma=SIGMA, verbose=False)
    sm_ok = hp.smoothing(mask_ok.astype(float), sigma=SIGMA, verbose=False)
    sm = np.where(sm_ok > 0.1, sm / sm_ok, np.nan)
    maps[freq] = sm
    print(f"  {freq} GHz: 平滑完成 ({time.time()-t0:.0f}s)")

# SMICA 3.0° 對照
ms3 = hp.read_map(os.path.join(CACHE, "smica2_smooth3.0.fits"), field=0)
nside = hp.get_nside(ms3)

def sample(l, b):
    pix = hp.ang2pix(nside, l, b, lonlat=True)
    out = {"SMICA": float(ms3[pix] * 1e6)}
    for freq, m in maps.items():
        v = m[pix] * 1e6
        out[str(freq)] = float(v) if np.isfinite(v) else float('nan')
    out["r217_143"] = out["217"]/out["143"] if abs(out["143"]) > 1 else float('nan')
    out["r353_217"] = out["353"]/out["217"] if abs(out["217"]) > 1 else float('nan')
    return out

print(f"\n{'目標':<26}{'SMICA':>9}{'100GHz':>9}{'143GHz':>9}{'217GHz':>9}{'353GHz':>9}"
      f"{'217/143':>8}{'353/217':>8}")
rows = []
for l, b, name in TARGETS:
    v = sample(l, b)
    rows.append({"name": name, "l": l, "b": b, **v})
    print(f"{name:<26}{v['SMICA']:>+9.1f}{v['100']:>+9.1f}{v['143']:>+9.1f}"
          f"{v['217']:>+9.1f}{v['353']:>+9.1f}"
          f"{v['r217_143']:>8.2f}{v['r353_217']:>8.2f}")

# ---------- 3° 盤平均 (雙重確認) ----------
print(f"\n--- 3° 盤平均確認 (node53 vs 基準) ---")
RAD = 3.0
nside_f = hp.get_nside(maps[100])
print(f"{'目標':<26}{'100GHz':>9}{'143GHz':>9}{'217GHz':>9}{'353GHz':>9}")
for l, b, name in [(319.50, -34.20, "node53"), (209.00, -57.00, "node0"),
                   (214.92, -31.16, "node9"), (313.47, -8.58, "node47")]:
    vec = hp.ang2vec(l, b, lonlat=True)
    pix = hp.query_disc(nside_f, vec, np.radians(RAD))
    vals = {}
    for freq, m in maps.items():
        vals[freq] = float(np.nanmean(m[pix]) * 1e6)
    print(f"{name:<26}{vals[100]:>+9.1f}{vals[143]:>+9.1f}{vals[217]:>+9.1f}{vals[353]:>+9.1f}")

# ---------- 判定 ----------
r53 = sample(319.50, -34.20)
r0 = sample(209.00, -57.00)
r47 = sample(313.47, -8.58)

# 光譜斜率: 用 100→217 段 (CMB 平, dust 升)
slope53 = (r53["217"] - r53["100"]) / (217 - 100)  # μK/GHz
slope0 = (r0["217"] - r0["100"]) / (217 - 100)
slope47 = (r47["217"] - r47["100"]) / (217 - 100)
print(f"\n--- 光譜斜率 (217−100 GHz 段) ---")
print(f"node53: {slope53:+.3f} μK/GHz (CMB 期望 ≈0)")
print(f"node0 : {slope0:+.3f} μK/GHz")
print(f"node47: {slope47:+.3f} μK/GHz (前景: 急升)")
print(f"node53 |slope| 對比 node0: {abs(slope53)/max(abs(slope0),1e-9):.2f}x")

# 判定邏輯 (O27 標準)
smica53 = r53["SMICA"]
f143_53 = r53["143"]
f217_53 = r53["217"]
r217_143_53 = r53["r217_143"]

verdict = "🟡 混合"
reasons = []
if abs(r217_143_53 - 1) < 0.3 and abs(slope53) < 0.3:
    verdict = "🟢🟢 真實 CMB 熱異常 (平譜)"
    reasons.append("平譜")
elif r217_143_53 > 1.5 and f217_53 > abs(f143_53):
    verdict = "🔴 前景污染 (dust-like 上升)"
    reasons.append(f"217/143={r217_143_53:.2f} > 1.5")
else:
    reasons.append(f"217/143={r217_143_53:.2f}")

# SMICA vs 143 GHz 符號一致性 (node47 測試: SMICA 冷但 143 熱 = 前景)
if smica53 > 0 and f143_53 > 0:
    reasons.append("SMICA 熱 + 143GHz 熱 一致")
    if verdict == "🟡 混合":
        verdict = "🟢🟢 真實 CMB 熱異常 (符號一致)"
elif smica53 > 0 and f143_53 < 0:
    reasons.append("⚠️ SMICA 熱但 143GHz 冷 — 分歧!")
    verdict = "🔴 前景污染 (符號分歧)"

print(f"\n判定: {verdict}")
for r in reasons:
    print(f"  - {r}")

# ---------- 儲存 ----------
with open(os.path.join(OUT, "09_node53_multifreq.json"), "w") as f:
    json.dump({
        "fwhm": FWHM, "target": "node53 (319.50, -34.20)",
        "rows": rows,
        "slope53": slope53, "slope0": slope0, "slope47": slope47,
        "verdict": verdict, "reasons": reasons,
        "smica_3deg": smica53, "T143_3deg": f143_53, "T217_3deg": f217_53,
        "r217_143": r217_143_53,
    }, f, indent=2)
print(f"\n✅ 已存: {os.path.join(OUT, '09_node53_multifreq.json')}")
