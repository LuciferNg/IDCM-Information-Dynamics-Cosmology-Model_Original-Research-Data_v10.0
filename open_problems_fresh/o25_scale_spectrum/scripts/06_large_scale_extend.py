#!/usr/bin/env python3
"""
06_large_scale_extend.py — O25 一次過: 大尺度延伸 + τ 精確化
=============================================================
用 NILC/Commander raw (NESTED→RING) 平滑出大尺度 + 額外細尺度:
  大尺度: 12°, 15°, 20°
  額外細尺度: 0.3°, 0.75°, 6°, 8°  (用 NILC/Commander, SMICA 冇 raw)

計算 per 尺度:
  1. 冷熱差 + Welch p (全60 + 高緯)
  2. node0/node9/node57 + 最冷/最熱節點
  3. ΔE0 比例 (全60 + 高緯)
  4. node9 10°/15°/20° 區域 z (對照隨機區域)

NESTED 陷阱: read_map(nest=True) + reorder(n2r=True)
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy import stats
import os, json, sys

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
OUT = os.path.join(BASE, "o25_scale_spectrum")
DATA = os.path.join(OUT, "data")
CACHE_OUT = os.path.join(OUT, "data", "smooth_cache_large")
os.makedirs(CACHE_OUT, exist_ok=True)

EXTRA_SCALES = [0.3, 0.75, 6.0, 8.0, 12.0, 15.0, 20.0]
MAPS = ["NILC", "Commander"]

# 節點
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

color = {}
with open(os.path.join(BASE, "cmb_cold_spot/data/anchored_coloring.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        color[int(parts[0])] = int(parts[3])
color_arr = np.array([color[i] for i in range(60)])
ZERO_E = [10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46]
zero_mask = np.zeros(60, dtype=bool)
zero_mask[ZERO_E] = True
gal_mask = np.abs(b_deg) < 20
hi = ~gal_mask

def get_smooth(mname, scale):
    """讀 raw (NESTED) → reorder → smooth → remove_dipole, cache 落項目目錄"""
    cache_path = os.path.join(CACHE_OUT, f"{mname}_smooth{scale}.fits")
    if os.path.exists(cache_path):
        return hp.read_map(cache_path, field=0)
    raw = f"/tmp/{'nilc' if mname=='NILC' else 'commander'}.fits"
    m = hp.read_map(raw, field=0, nest=True)
    m = hp.reorder(m, n2r=True)
    sigma = np.radians(scale) / (2 * np.sqrt(2 * np.log(2)))
    m = hp.remove_dipole(hp.smoothing(m, sigma=sigma))
    hp.write_map(cache_path, m.astype(np.float32), overwrite=True)
    return m

results = {m: {} for m in MAPS}
for mname in MAPS:
    for s in EXTRA_SCALES:
        m = get_smooth(mname, s)
        nside = hp.get_nside(m)
        pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
        T = m[pix] * 1e6

        cold = T[color_arr == 1]
        hot = T[color_arr == 0]
        d = cold.mean() - hot.mean()
        _, p_all = stats.ttest_ind(cold, hot, equal_var=False)
        c_hi = T[(color_arr == 1) & hi]
        h_hi = T[(color_arr == 0) & hi]
        d_hi = c_hi.mean() - h_hi.mean()
        _, p_hi = stats.ttest_ind(c_hi, h_hi, equal_var=False)

        zero_r = np.abs(T[zero_mask]).mean() / np.abs(T[~zero_mask]).mean()
        hi_zero_r = np.abs(T[zero_mask & hi]).mean() / np.abs(T[~zero_mask & hi]).mean()

        results[mname][s] = {
            "cold_hot_diff": round(float(d), 3),
            "p_all": round(float(p_all), 4),
            "cold_hot_diff_hi": round(float(d_hi), 3),
            "p_hi": round(float(p_hi), 4),
            "zeroE_ratio": round(float(zero_r), 4),
            "hi_zeroE_ratio": round(float(hi_zero_r), 4),
            "node0": round(float(T[0]), 3),
            "node9": round(float(T[9]), 3),
            "node57": round(float(T[57]), 3),
            "T_min": round(float(T.min()), 3),
            "T_min_idx": int(T.argmin()),
            "T_max": round(float(T.max()), 3),
            "T_max_idx": int(T.argmax()),
            "std": round(float(T.std()), 3),
        }
        print(f"{mname} @{s:>5.2f}°: diff={results[mname][s]['cold_hot_diff']:+.2f} p={p_all:.4f} "
              f"node0={T[0]:+.1f} node9={T[9]:+.1f} min=#{T.argmin()}({T.min():+.1f}) "
              f"max=#{T.argmax()}({T.max():+.1f}) zeroE_r={zero_r:.3f}")
        del m

with open(os.path.join(DATA, "scale_spectrum_large.json"), "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# ============ node9 區域檢驗 (大尺度) ============
print("\n=== node9 區域檢驗 (10°-20° 半徑) ===")
rng = np.random.default_rng(7)
for s in [10.0, 15.0, 20.0]:
    m = get_smooth("Commander", s)  # Commander 同 SMICA 最接近
    nside = hp.get_nside(m)
    npix = hp.nside2npix(nside)
    pix9 = hp.ang2pix(nside, l_deg[9], b_deg[9], lonlat=True)
    pix0 = hp.ang2pix(nside, l_deg[0], b_deg[0], lonlat=True)
    vec9 = hp.pix2vec(nside, pix9)
    vec0 = hp.pix2vec(nside, pix0)
    radius = np.radians(s)
    d9 = hp.query_disc(nside, vec9, radius)
    d0 = hp.query_disc(nside, vec0, radius)
    m9 = m[d9].mean() * 1e6
    m0 = m[d0].mean() * 1e6
    # 隨機對照
    rands = []
    for _ in range(100):
        rv = rng.standard_normal(3)
        rv /= np.linalg.norm(rv)
        rd = hp.query_disc(nside, rv, radius)
        rands.append(m[rd].mean() * 1e6)
    rands = np.array(rands)
    z9 = (m9 - rands.mean()) / rands.std()
    z0 = (m0 - rands.mean()) / rands.std()
    print(f"  {s:>4.0f}°半徑: node9区={m9:+.2f} (z={z9:+.2f}σ)  node0区={m0:+.2f} (z={z0:+.2f}σ)  random={rands.mean():+.2f}±{rands.std():.2f}")

print("\n✅ saved data/scale_spectrum_large.json")
