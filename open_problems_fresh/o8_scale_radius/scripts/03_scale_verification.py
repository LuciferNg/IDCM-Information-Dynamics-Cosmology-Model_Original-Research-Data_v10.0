#!/usr/bin/env python3
"""
03_scale_verification.py — O8 尺度閉合驗證
============================================
核心問題: 4.17° 影響半徑 = 26.09/2π 係咪真?
0.4% 偏差係咪平滑誤差?

三重驗證:
A. 角徑向 profile 高精度半峰半徑 (interpolated)
B. 信號對比度隨尺度嘅變化 (邊個尺度信號最強?)
C. 星系團真空 (4.5-5°) 交叉: 同 4.17° 一致?
"""
import healpy as hp
import numpy as np
import math
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy.interpolate import interp1d

phi = (1 + 5**0.5) / 2
a_edge = 26.091346
pred_a_2pi = a_edge/(2*np.pi)

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

# ===== 2. 高精度 profile (4.17° 平滑, 0.2° bins) =====
cache_dir = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare/data/smooth_cache"
m = hp.remove_dipole(hp.read_map(f"{cache_dir}/smica2_smooth4.17.fits", field=0))
nside = hp.get_nside(m)

def radial_profile_fine(m, nside, cl, cb, rmax=25, nbins=125):
    center_vec = hp.ang2vec(cl, cb, lonlat=True)
    pix = hp.query_disc(nside, center_vec, np.radians(rmax))
    pix_vecs = np.array(hp.pix2vec(nside, pix)).T
    angs = np.degrees(np.arccos(np.clip(pix_vecs @ center_vec, -1, 1)))
    vals = m[pix]
    bins = np.linspace(0, rmax, nbins+1)
    idx = np.digitize(angs, bins[1:-1])
    prof = np.array([( (bins[i]+bins[i+1])/2, np.mean(vals[idx==i]) ) for i in range(nbins) if (idx==i).sum() > 0])
    return prof

# 全部 60 節點 (呢個要少少時間, 用 nside 降級加速? 唔好 — 要精確)
print("計算 60 節點高精度 profile...")
all_prof = []
for i in range(60):
    p = radial_profile_fine(m, nside, l_deg[i], b_deg[i])
    all_prof.append(p)
    if (i+1) % 10 == 0:
        print(f"  {i+1}/60")

# ===== A. 半峰半徑 (interpolated) =====
print("\n=== A. 高精度半峰半徑 ===")
half_radii = []
for p in all_prof:
    r, v = p[:, 0], np.abs(p[:, 1])
    c0 = v[0]
    base = v[-1]
    target = (c0 + base)/2
    # interpolate
    f = interp1d(v, r, kind='linear', bounds_error=False, fill_value='extrapolate')
    hr = float(f(target))
    if 0 < hr < 25:
        half_radii.append(hr)
half_radii = np.array(half_radii)
print(f"半峰半徑 (interpolated): median={np.median(half_radii):.3f}°, mean={half_radii.mean():.3f}°")
print(f"  std={half_radii.std():.3f}°, min={half_radii.min():.3f}, max={half_radii.max():.3f}")
print(f"  四分位: 25%={np.percentile(half_radii,25):.3f}, 75%={np.percentile(half_radii,75):.3f}")

# 穩健平均 (trimmed)
trim = np.sort(half_radii)[3:-3]
print(f"  trimmed mean (10% trim): {trim.mean():.3f}°")

print(f"\n預測: a/2π = {pred_a_2pi:.4f}°, Vielva R8 = 4.17°, 180/44 = {180/44:.4f}°")
med = np.median(half_radii)
print(f"實測 median vs a/2π: 偏差 {abs(med-pred_a_2pi)/pred_a_2pi*100:.2f}%")
print(f"實測 median vs R8:   偏差 {abs(med-4.17)/4.17*100:.2f}%")

# ===== B. 信號對比度隨尺度 =====
print("\n=== B. 信號對比度隨平滑尺度 ===")
print("檢查 4.17° 係咪「最佳尺度」(節點-背景對比度最高)")
scales = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
contrast = []
for s in scales:
    try:
        ms = hp.remove_dipole(hp.read_map(f"{cache_dir}/smica2_smooth{s}.fits", field=0))
        # 節點值
        pix = hp.ang2pix(hp.get_nside(ms), l_deg, b_deg, lonlat=True)
        T_node = ms[pix]
        # 背景: 隨機 6000 點
        npix = hp.get_nside(ms)
        rpix = np.random.randint(0, hp.nside2npix(npix), 6000)
        T_bg = ms[rpix]
        # 對比度 = |節點 mean| / 背景 std
        c = abs(T_node.mean()) / T_bg.std()
        contrast.append((s, c, abs(T_node.mean())*1e6, T_bg.std()*1e6))
        print(f"  {s:>5}°: 節點 mean={abs(T_node.mean())*1e6:6.1f} μK, 背景 std={T_bg.std()*1e6:6.1f}, 對比度={c:.3f}")
    except Exception as e:
        print(f"  {s}°: ❌ {e}")

contrast = np.array(contrast)
best = contrast[np.argmax(contrast[:, 2])]
print(f"\n最大節點信號尺度: {best[0]}° (節點 mean {best[2]:.1f} μK)")

# ===== C. 星系團真空交叉 =====
print("\n=== C. 星系團真空交叉 (4.5-5°) ===")
print(f"星系團真空: 4.5-5° (PSZ1 4.5°, MCXC 5.0°)")
print(f"冷斑 FWHM R8: 4.17° (Vielva)")
print(f"實測節點影響半徑: {med:.2f}°")
print(f"a/2π 預測: {pred_a_2pi:.2f}°")
print(f"""
交叉分析:
  星系團真空半徑 (4.5-5°) vs 影響半徑 (4.17°): 偏差 {(4.5-4.17)/4.17*100:.0f}% 到 {(5.0-4.17)/4.17*100:.0f}%
  → 星系團「被排除」區域應該 ≥ 影響半徑 (物質要避開節點核心)
  → 4.5-5° > 4.17° 一致: 排除區比影響區略大 (因為物質需要更遠離)

  a/2π = {pred_a_2pi:.2f}°: 影響半徑嘅結構預測
  星系團真空 4.5-5°: 物質排除區 (觀測)
  差異 {4.5-pred_a_2pi:.2f}-{5.0-pred_a_2pi:.2f}° = 0.35-0.85°: 物質排除需要額外緩衝
""")

# 儲存
with open("/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o8_scale_radius/data/scale_verification.txt", "w") as f:
    f.write(f"# O8 尺度閉合驗證\n")
    f.write(f"# 半峰半徑 median = {med:.4f}°, mean = {half_radii.mean():.4f}°, std = {half_radii.std():.4f}\n")
    f.write(f"# a/2π = {pred_a_2pi:.4f}° (偏差 {abs(med-pred_a_2pi)/pred_a_2pi*100:.2f}%)\n")
    f.write(f"# Vielva R8 = 4.17° (偏差 {abs(med-4.17)/4.17*100:.2f}%)\n")
    f.write(f"# 180/44 = {180/44:.4f}° (偏差 {abs(med-180/44)/(180/44)*100:.2f}%)\n")
    for s, c, tn, ts in contrast:
        f.write(f"# scale {s}: contrast={c:.3f} node={tn:.1f} bg={ts:.1f}\n")
np.save("/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o8_scale_radius/data/half_radii_fine.npy", half_radii)
print("\n✅ 已存: data/scale_verification.txt, data/half_radii_fine.npy")
