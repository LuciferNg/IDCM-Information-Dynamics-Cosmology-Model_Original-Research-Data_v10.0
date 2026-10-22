#!/usr/bin/env python3
"""
10_node53_ring_background.py — O30: node53 環背景扣除 + dust tracer
====================================================================
09 script 顯示: 所有目標點 (連 node0 冷斑) 喺 raw HFI map 都顯示 217>143
上升 — 因為高緯背景 dust 本身有梯度。單靠 217/143>1.5 判前景係錯嘅 (只啱 b≈0)。

嚴謹方法:
  1. 對每個目標點, 用 4°-8° 環做當地背景 (減 dust 大尺度梯度)
  2. 節點中心 (3° 盤) − 環背景 = 當地超出 ΔT(freq)
  3. CMB 信號 ⇒ ΔT 平譜 (頻率無關, K_CMB 單位)
  4. Dust 集中 ⇒ ΔT 喺 217/353 上升
  5. 353 GHz = dust tracer: node53 353 超出 ≈ 0 ⇒ 冇 dust 集中 ⇒ 熱信號係 CMB

判定:
  🟢🟢 ΔT 平譜 (100≈143≈217 喺 ~30% 內) + 353 冇超出 → 真實 CMB
  🔴 ΔT 上升 (217>>143, 353>>217) → dust 集中
"""
import healpy as hp
import numpy as np
import os, json
from astropy.coordinates import SkyCoord
import astropy.units as u

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
R_IN, R_OUT = 4.0, 8.0  # 環背景
R_CORE = 2.0  # 核心盤

# node53 銀道座標 (O3 確認: l=319.5, b=-34.2)
TARGETS = [
    (319.50, -34.20, "node53"),
    (209.00, -57.00, "node0"),
    (214.92, -31.16, "node9"),
    (313.47,  -8.58, "node47"),
]

print("=" * 70)
print("O30: node53 環背景扣除 + dust tracer (353 GHz)")
print("=" * 70)

# 載入 + 平滑 (同 09)
maps = {}
for freq, path in FREQ_MAPS.items():
    if not os.path.exists(path) or os.path.getsize(path) < 2e9:
        print(f"  [skip] {freq} GHz")
        continue
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
    print(f"  {freq} GHz: 平滑完成")

# SMICA 4.17° (O30 主尺度)
ms = hp.read_map(os.path.join(CACHE, "smica2_smooth4.17.fits"), field=0)
nside = hp.get_nside(ms)

def core_ring(l, b):
    """核心 2° 盤平均 + 4-8° 環背景平均"""
    vec = hp.ang2vec(l, b, lonlat=True)
    out = {}
    for freq, m in maps.items():
        ns = hp.get_nside(m)
        p_core = hp.query_disc(ns, vec, np.radians(R_CORE))
        p_ring = hp.query_disc(ns, vec, np.radians(R_OUT)) 
        p_ring_in = hp.query_disc(ns, vec, np.radians(R_IN))
        p_ring = np.setdiff1d(p_ring, p_ring_in)
        core = np.nanmean(m[p_core]) * 1e6
        ring = np.nanmean(m[p_ring]) * 1e6
        out[freq] = {"core": float(core), "ring": float(ring),
                     "dT": float(core - ring)}
    # SMICA 4.17°
    p_core = hp.query_disc(nside, vec, np.radians(R_CORE))
    p_ring = hp.query_disc(nside, vec, np.radians(R_OUT))
    p_ring_in = hp.query_disc(nside, vec, np.radians(R_IN))
    p_ring = np.setdiff1d(p_ring, p_ring_in)
    out["SMICA"] = {"core": float(np.mean(ms[p_core]) * 1e6),
                    "ring": float(np.mean(ms[p_ring]) * 1e6),
                    "dT": float((np.mean(ms[p_core]) - np.mean(ms[p_ring])) * 1e6)}
    return out

print(f"\n{'目標':<9}{'freq':>5}{'核心':>9}{'環背':>9}{'ΔT':>9}")
results = {}
for l, b, name in TARGETS:
    r = core_ring(l, b)
    results[name] = r
    for freq in [100, 143, 217, 353]:
        if freq in r:
            v = r[freq]
            print(f"{name:<9}{freq:>5}{v['core']:>+9.1f}{v['ring']:>+9.1f}{v['dT']:>+9.1f}")
    v = r["SMICA"]
    print(f"{name:<9}{'SMICA':>5}{v['core']:>+9.1f}{v['ring']:>+9.1f}{v['dT']:>+9.1f}")
    print()

# ---------- 判定 ----------
r53 = results["node53"]
dT = {f: r53[f]["dT"] for f in [100, 143, 217] if f in r53}
print("--- node53 當地超出 ΔT (核心 − 4-8° 環) ---")
for f, v in dT.items():
    print(f"  {f} GHz: {v:+.1f} μK")
dT353 = r53.get(353, {}).get("dT", None)

# 平譜檢驗: max-min spread
vals = list(dT.values())
spread = (max(vals) - min(vals)) / max(abs(v) for v in vals) if vals else 99
mean_dT = np.mean(vals)
print(f"  ΔT spread = {spread:.2f} ({'平譜' if spread < 0.5 else '上升/非平'})")
print(f"  mean ΔT = {mean_dT:+.1f} μK")
if dT353 is not None:
    print(f"  353 GHz ΔT = {dT353:+.1f} μK ({'冇 dust 超出' if abs(dT353) < 0.5*abs(mean_dT)+15 else '有 dust!'})")

# node0 對照
r0 = results["node0"]
dT0 = {f: r0[f]["dT"] for f in [100, 143, 217] if f in r0}
vals0 = list(dT0.values())
print(f"\n--- node0 對照 ---")
for f, v in dT0.items():
    print(f"  {f} GHz: {v:+.1f} μK")
print(f"  spread = {(max(vals0)-min(vals0))/max(abs(v) for v in vals0):.2f}, mean = {np.mean(vals0):+.1f} μK")

# 最終判定
verdict, reasons = "🟡 混合", []
if dT353 is not None and abs(dT353) < 0.5 * abs(mean_dT) + 15:
    reasons.append(f"353 GHz dust tracer 冇超出 ({dT353:+.1f} μK)")
    if spread < 0.5:
        verdict = "🟢🟢 真實 CMB 熱異常 — 平譜超出 + 冇 dust 集中"
        reasons.append(f"ΔT 平譜 (spread={spread:.2f}, mean={mean_dT:+.1f} μK)")
    else:
        verdict = "🟢 CMB 為主, 有輕微前景成分"
        reasons.append(f"ΔT 非完全平 (spread={spread:.2f}) 但 dust 冇超出")
else:
    if spread > 0.8 and dT353 is not None and abs(dT353) > abs(mean_dT):
        verdict = "🔴 dust 集中 (353 超出 + 上升光譜)"
        reasons.append(f"353 ΔT={dT353:+.1f} μK 顯著, spread={spread:.2f}")
    else:
        verdict = "🟡 混合/需更多數據"
        reasons.append(f"353 ΔT={dT353:+.1f} μK (nan?), spread={spread:.2f}")

print(f"\n判定: {verdict}")
for r in reasons:
    print(f"  - {r}")

with open(os.path.join(OUT, "10_node53_ring_background.json"), "w") as f:
    json.dump({"r_core": R_CORE, "r_ring": [R_IN, R_OUT], "results": results,
               "node53_dT": dT, "node53_dT353": dT353, "spread": spread,
               "mean_dT": mean_dT, "verdict": verdict, "reasons": reasons},
              f, indent=2, default=str)
print(f"\n✅ 已存: {os.path.join(OUT, '10_node53_ring_background.json')}")
