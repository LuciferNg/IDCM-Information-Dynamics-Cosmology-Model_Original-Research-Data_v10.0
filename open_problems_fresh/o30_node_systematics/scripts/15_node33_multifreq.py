#!/usr/bin/env python3
"""
15_node33_multifreq.py — O30: node33 多頻譜檢查 (O27/O30-node53 流程)
======================================================================
node33 (l=191.4°, b=-16.1°) 係 O30 離散性發現嘅跨尺度穩定冷異常
(T=-83 μK @4.17°, zbar=-2.10, 冷端排名 #4/60)。b=-16° 接近銀河面邊緣
(|b|<20° = O27 前景高危區)。

流程 (同 node53):
  1. 多頻譜 raw 抽值 (100/143/217/353 GHz, 3.0° FWHM) — 對照 node0/node9/node53/node47
  2. 環背景扣除 (核心 2° − 4-8° 環) — 當地超出 ΔT(freq)
  3. 三地圖一致性 (SMICA/NILC/Commander 4.17°)
  4. R3 mask 狀態
判定:
  🟢🟢 三地圖一致 + 平譜 + unmasked → 真實 CMB 冷異常
  🔴 光譜上升 / 符號分歧 / masked → 前景污染
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

L33, B33 = 191.4, -16.1  # node33
TARGETS = [
    (191.4,  -16.1, "node33 (b=-16°)"),
    (209.00, -57.00, "node0 冷斑 (CMB 基準)"),
    (214.92, -31.16, "node9 (CMB 基準)"),
    (319.50, -34.20, "node53 (熱異常 CMB)"),
    (313.47,  -8.58, "node47 (前景基準)"),
    (180.00, +30.00, "高緯隨機 A"),
    (191.4,   -1.0,  "銀河面同經度 (b≈0)"),
]

print("=" * 70)
print(f"O30: node33 多頻譜檢查 ({FWHM}° FWHM) — O27/node53 流程")
print("=" * 70)

# ---------- 載入頻率 map + 平滑 ----------
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

ms3 = hp.read_map(os.path.join(CACHE, "smica2_smooth3.0.fits"), field=0)
nside = hp.get_nside(ms3)
# 4.17° SMICA (環背景用)
m417 = hp.read_map(os.path.join(CACHE, "smica2_smooth4.17.fits"), field=0)
nside417 = hp.get_nside(m417)

def sample(l, b):
    pix = hp.ang2pix(nside, l, b, lonlat=True)
    out = {"SMICA": float(ms3[pix] * 1e6)}
    for freq, m in maps.items():
        v = m[pix] * 1e6
        out[str(freq)] = float(v) if np.isfinite(v) else float('nan')
    out["r217_143"] = out["217"]/out["143"] if abs(out["143"]) > 1 else float('nan')
    return out

print(f"\n--- 1. Raw 抽值 (3.0° 平滑單像素) ---")
print(f"{'目標':<22}{'SMICA':>9}{'100GHz':>9}{'143GHz':>9}{'217GHz':>9}{'353GHz':>9}{'217/143':>8}")
rows = []
for l, b, name in TARGETS:
    v = sample(l, b)
    rows.append({"name": name, "l": l, "b": b, **v})
    print(f"{name:<22}{v['SMICA']:>+9.1f}{v['100']:>+9.1f}{v['143']:>+9.1f}"
          f"{v['217']:>+9.1f}{v['353']:>+9.1f}{v['r217_143']:>8.2f}")

# ---------- 2. 環背景扣除 ----------
print(f"\n--- 2. 當地超出 ΔT (核心 2° − 4-8° 環) ---")
def core_ring(l, b):
    vec = hp.ang2vec(l, b, lonlat=True)
    out = {}
    for freq, m in maps.items():
        ns = hp.get_nside(m)
        pc = hp.query_disc(ns, vec, np.radians(2.0))
        pr = hp.query_disc(ns, vec, np.radians(8.0))
        pi = hp.query_disc(ns, vec, np.radians(4.0))
        pr = np.setdiff1d(pr, pi)
        out[freq] = (np.nanmean(m[pc]) - np.nanmean(m[pr])) * 1e6
    # SMICA 4.17°
    pc = hp.query_disc(nside417, vec, np.radians(2.0))
    pr = hp.query_disc(nside417, vec, np.radians(8.0))
    pi = hp.query_disc(nside417, vec, np.radians(4.0))
    pr = np.setdiff1d(pr, pi)
    out["SMICA"] = (np.mean(m417[pc]) - np.mean(m417[pr])) * 1e6
    return out

dT = {}
for l, b, name in [(191.4,-16.1,"node33"), (209.0,-57.0,"node0"), (319.5,-34.2,"node53"), (313.47,-8.58,"node47")]:
    r = core_ring(l, b)
    dT[name] = r
    line = f"{name:<9}"
    for f in [100, 143, 217, 353]:
        line += f" {f}GHz={r[f]:+7.1f}"
    line += f" SMICA={r['SMICA']:+7.1f}"
    print(line)

# node33 平譜檢驗
r33 = dT["node33"]
vals33 = [r33[f] for f in [100, 143, 217] if f in r33]
spread33 = (max(vals33) - min(vals33)) / max(abs(v) for v in vals33)
mean33 = np.mean(vals33)
print(f"\nnode33 ΔT: 100={r33[100]:+.1f} 143={r33[143]:+.1f} 217={r33[217]:+.1f}")
print(f"  spread={spread33:.2f} ({'平譜' if spread33 < 0.5 else '非平'}), mean={mean33:+.1f} μK")
print(f"  353 GHz dust tracer: {r33[353]:+.1f} μK")

# ---------- 3. 三地圖一致性 ----------
print(f"\n--- 3. 三地圖一致性 (4.17°) ---")
vals3 = {}
for name, fname in [("SMICA","smica2_smooth4.17.fits"), ("NILC","nilc2_smooth4.17.fits"),
                     ("Commander","commander_smooth4.17.fits")]:
    mm = hp.read_map(os.path.join(CACHE, fname), field=0)
    ns = hp.get_nside(mm)
    vec = hp.ang2vec(L33, B33, lonlat=True)
    p3 = hp.query_disc(ns, vec, np.radians(3.0))
    vals3[name] = np.mean(mm[p3]) * 1e6
    print(f"  {name:<12} 3°盤: {vals3[name]:+.2f} μK")
spread3 = (max(vals3.values()) - min(vals3.values())) / abs(np.mean(list(vals3.values()))) * 100
print(f"  spread = {spread3:.1f}%")

# ---------- 4. R3 mask ----------
print(f"\n--- 4. R3 mask 狀態 ---")
mk = hp.read_map(os.path.join(DATA27, "COM_Mask_CMB-common-Mask-Int_2048_R3.00.fits"), field=0)
ns = hp.get_nside(mk)
p33 = mk[hp.ang2pix(ns, L33, B33, lonlat=True)]
print(f"  node33 R3 mask pixel = {p33:.3f} ({'✅ unmasked' if p33 > 0.5 else '🔴 masked'})")

# ---------- 判定 ----------
print(f"\n--- 判定 ---")
r217_143_33 = r33[217] / r33[143] if abs(r33[143]) > 1 else 99
smica33 = vals3["SMICA"]
verdict_parts = []
if spread3 < 5:
    verdict_parts.append(f"三地圖一致 ({spread3:.1f}%)")
else:
    verdict_parts.append(f"三地圖分歧 ({spread3:.1f}%)")
if spread33 < 0.5:
    verdict_parts.append(f"平譜 (spread={spread33:.2f})")
else:
    verdict_parts.append(f"非平譜 (spread={spread33:.2f})")
if abs(r33[353]) < abs(mean33) * 0.8 + 15:
    verdict_parts.append(f"dust 冇超出 (353={r33[353]:+.1f})")
else:
    verdict_parts.append(f"dust 顯著 (353={r33[353]:+.1f})")
if p33 > 0.5:
    verdict_parts.append("R3 unmasked")
else:
    verdict_parts.append("R3 MASKED")

n_good = sum([spread3 < 5, spread33 < 0.5, abs(r33[353]) < abs(mean33)*0.8+15, p33 > 0.5])
if n_good == 4:
    verdict = "🟢🟢 真實 CMB 冷異常"
elif n_good == 3:
    verdict = "🟢 CMB 為主, 有前景成分"
elif n_good == 2:
    verdict = "🟡 混合"
else:
    verdict = "🔴 前景污染"
print(f"  {' | '.join(verdict_parts)}")
print(f"  得分: {n_good}/4 → {verdict}")

with open(os.path.join(OUT, "15_node33_multifreq.json"), "w") as f:
    json.dump({"l": L33, "b": B33, "raw": rows, "ring_dT": dT,
               "node33_dT": {str(k): v for k, v in r33.items()},
               "spread_ring": spread33, "mean_dT": mean33,
               "crossmap": vals3, "spread_crossmap": spread3,
               "mask_pixel": float(p33), "verdict": verdict,
               "parts": verdict_parts}, f, indent=2, default=str)
print(f"\n✅ 已存: {os.path.join(OUT, '15_node33_multifreq.json')}")
