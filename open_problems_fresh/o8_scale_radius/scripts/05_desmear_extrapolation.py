#!/usr/bin/env python3
"""
05_desmear_extrapolation.py — O8 去平滑外推 (真實影響半徑)
=============================================================
平滑會將凹陷抹開 → 量度嘅半峰半徑 > 真實值
用 σ² 相加規則外推返 σ→0:
  σ_meas² = σ_true² + σ_smooth²
  (Gaussian 捲積: 方差相加)

如果冷斑真實 profile 係 Gaussian 凹陷:
  半峰半徑 HWHM_meas² = HWHM_true² + σ_smooth²×2ln2
  即 HWHM_meas² vs σ_smooth² 應該係直線, 截距 = HWHM_true²

呢個截距就係「真實結構半徑」— 對比 a/2π = 4.153°
"""
import healpy as hp
import numpy as np
import math
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy import stats

a_edge = 26.091346
pred = a_edge/(2*np.pi)
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

# ===== 2. 冷斑半峰半徑 per 平滑尺度 (高精度) =====
scales = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
results = []
print("=== 冷斑半峰半徑 (HWHM) 隨平滑尺度 ===")
for s in scales:
    m = hp.remove_dipole(hp.read_map(f"{cache_dir}/smica2_smooth{s}.fits", field=0))
    nside = hp.get_nside(m)
    center_vec = hp.ang2vec(l_deg[0], b_deg[0], lonlat=True)
    pix = hp.query_disc(nside, center_vec, np.radians(15))
    pix_vecs = np.array(hp.pix2vec(nside, pix)).T
    angs = np.degrees(np.arccos(np.clip(pix_vecs @ center_vec, -1, 1)))
    vals = m[pix]
    bins = np.linspace(0, 15, 150)  # 0.1° bins
    idx = np.digitize(angs, bins[1:-1])
    prof = np.array([((bins[i]+bins[i+1])/2, np.mean(vals[idx==i])) for i in range(149) if (idx==i).sum() > 0])
    r, v = prof[:, 0], prof[:, 1]
    T0 = v[0]
    target = T0/2
    hr = np.nan
    for j in range(1, len(v)):
        if (v[j] - target) * (v[j-1] - target) <= 0:
            t = (target - v[j-1])/(v[j] - v[j-1])
            hr = r[j-1] + t*(r[j] - r[j-1])
            break
    results.append((s, hr, T0))
    print(f"  {s:>5}°: HWHM={hr:.3f}°, T0={T0*1e6:.1f} μK")

results = np.array(results)
s_smooth = results[:, 0]
hwhm = results[:, 1]
T0s = results[:, 2]

# ===== 3. σ² 外推 =====
# HWHM² = HWHM_true² + (σ_smooth² × 2ln2)
# σ_smooth (rad) = FWHM/(2√(2ln2)); 喺度 FWHM = s (平滑尺度)
sigma_smooth_deg = s_smooth / (2*math.sqrt(2*math.log(2)))
x = sigma_smooth_deg**2
y = hwhm**2

# 用細平滑 (0.5-3.0°) 做線性擬合 (避開大平滑嘅非線性)
mask = s_smooth <= 3.0
slope, intercept, rval, pval, serr = stats.linregress(x[mask], y[mask])
hwhm_true = math.sqrt(max(0, intercept))
print(f"\n=== σ² 外推 (Gaussian 捲積) ===")
print(f"用尺度 {scales[0]}-3.0° 擬合: HWHM² = {intercept:.4f} + {slope:.4f}·σ²")
print(f"  R² = {rval**2:.4f}, p = {pval:.4f}")
print(f"真實 HWHM (σ→0 外推) = {hwhm_true:.4f}°")
print(f"a/2π = {pred:.4f}° → 偏差 {(hwhm_true-pred)/pred*100:.2f}%")
print(f"180/44 = {180/44:.4f}° → 偏差 {(hwhm_true-180/44)/(180/44)*100:.2f}%")

# 用所有尺度擬合 (對比)
mask2 = s_smooth <= 7.0
slope2, intercept2, rval2, pval2, serr2 = stats.linregress(x[mask2], y[mask2])
hwhm_true2 = math.sqrt(max(0, intercept2))
print(f"\n用尺度 0.5-7.0° 擬合: HWHM_true = {hwhm_true2:.4f}° (偏差 {(hwhm_true2-pred)/pred*100:.2f}%)")

# ===== 4. 理論預測檢查 =====
print("\n=== 理論候選 ===")
cands = {
    "a/2π": pred,
    "180/44": 180/44,
    "180/(2×43)": 360/86,
    "a×ε": a_edge*eps if (eps := (1/phi)/4) else 0,
    "a/(2π)×(1+1/44)": pred*(1+1/44),
}
for name, val in cands.items():
    dev = abs(val - hwhm_true)/hwhm_true*100
    print(f"  {name:<22} = {val:.4f}° (偏差 {dev:.2f}%)")

# ===== 5. 誤差分析 =====
print(f"\n=== 誤差分析 ===")
print(f"HWHM_true = {hwhm_true:.4f}° ± {serr/np.sqrt(intercept)/2*hwhm_true:.3f}° (擬合誤差)")
print(f"對比 a/2π = {pred:.4f}°: 偏差 {(hwhm_true-pred)/pred*100:.2f}%")
print(f"呢個偏差喺高斯捲積模型嘅誤差內? R²={rval**2:.3f}")
print(f"如果 R² 高 (>0.95): 模型正確, 截距 = 真實半徑")
print(f"如果 R² 低: profile 唔係 Gaussian, 要諗其他")

# 儲存
with open("/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o8_scale_radius/data/desmear_result.txt", "w") as f:
    f.write(f"# O8 去平滑外推結果\n")
    f.write(f"# HWHM_true (σ→0) = {hwhm_true:.4f}° (擬合 R²={rval**2:.4f})\n")
    f.write(f"# a/2π = {pred:.4f}° → 偏差 {(hwhm_true-pred)/pred*100:.2f}%\n")
    f.write(f"# 180/44 = {180/44:.4f}° → 偏差 {(hwhm_true-180/44)/(180/44)*100:.2f}%\n")
    for s, h, t0 in results:
        f.write(f"# scale {s}: HWHM={h:.3f} T0={t0*1e6:.1f}\n")
print("\n✅ 已存: data/desmear_result.txt")
