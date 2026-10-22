#!/usr/bin/env python3
"""
06_amplitude_test.py — O30: mean|T| 幅度檢驗 (IDCM 假說真正嘅測試)
=====================================================================
關鍵: IDCM「全部節點有異常」= 拓撲縫合點 → 相位 θ_i 隨節點而異
  → 預測唔係「全部同 sign」(mean 檢驗測唔出), 而係「|T| 增大」(幅度)
正確測試: 60 節點 mean|T| vs 隨機位置 mean|T| (1000 組)
  - 如果節點真係異常 → mean|T| 應該 > 隨機 mean|T| (幅度增大)
  - 控制: 各向同性 + 同緯度
  - 高緯子集重複 (避開銀河面)
  - 剔除 node0/node9 (排除已知強冷驅動)
框架: 4.17° 平滑 SMICA
"""
import healpy as hp
import numpy as np
import os
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy import stats

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache/smica2_smooth4.17.fits")
NODES = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
OUT = os.path.join(BASE, "o30_node_systematics/data")

RNG = np.random.default_rng(20260817)
N_CONTROL = 1000

print("=" * 66)
print("O30-06: mean|T| 幅度檢驗 (IDCM 假說真正測試)")
print("=" * 66)

m = hp.read_map(CACHE, field=0)
nside = hp.get_nside(m)
npix = hp.nside2npix(nside)
print(f"SMICA 4.17°: NSIDE={nside}")

nodes = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T = m[pix] * 1e6
hi_mask = np.abs(b_deg) >= 30
keep = np.array([i for i in range(60) if i not in (0, 9)])

A_node = np.abs(T)
A_hi = A_node[hi_mask]
A_keep = A_node[keep]

def ctrl_amplitude(lat_deg, n_pts, mode):
    """隨機位置 mean|T| 分佈"""
    out = np.empty(N_CONTROL)
    for k in range(N_CONTROL):
        if mode == 'iso':
            rpix = RNG.integers(0, npix, size=n_pts)
        else:
            rl = RNG.uniform(0, 360, size=n_pts)
            rpix = hp.ang2pix(nside, rl, lat_deg, lonlat=True)
        out[k] = np.abs(m[rpix]).mean() * 1e6
    return out

print(f"生成 {N_CONTROL} 組控制 (每組 60 點 mean|T|)...")
c_iso = ctrl_amplitude(b_deg, 60, 'iso')
c_lat = ctrl_amplitude(b_deg, 60, 'same_lat')
c_iso_hi = ctrl_amplitude(b_deg[hi_mask], hi_mask.sum(), 'iso')
c_lat_hi = ctrl_amplitude(b_deg[hi_mask], hi_mask.sum(), 'same_lat')
c_iso_k = ctrl_amplitude(b_deg[keep], len(keep), 'iso')
c_lat_k = ctrl_amplitude(b_deg[keep], len(keep), 'same_lat')

def report(name, A, ctrl):
    mu, sd = A.mean(), A.std(ddof=1)
    cmu, csd = ctrl.mean(), ctrl.std(ddof=1)
    z = (mu - cmu) / csd
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    t_obs, p_w = stats.ttest_1samp(A, cmu)
    # 單尾: IDCM 預測幅度增大 (右尾)
    p_one = 1 - stats.norm.cdf(z)
    verdict = '🟢🟢 >3σ' if z > 3 else ('🟢 2-3σ' if z > 2 else '🔴 <2σ')
    print(f"\n--- {name} ---")
    print(f"節點 mean|T| = {mu:.2f} μK, std = {sd:.2f} μK")
    print(f"隨機 mean|T| 分佈 = {cmu:.2f} ± {csd:.2f} μK")
    print(f"z = {z:+.2f}σ, p(雙尾) = {p:.4f}, p(單尾, 幅度↑) = {p_one:.4f}")
    print(f"Welch t = {t_obs:+.2f}, p = {p_w:.4f} → {verdict}")
    return dict(mu=mu, sd=sd, cmu=cmu, csd=csd, z=z, p=p, p1=p_one)

r1 = report("全部 60 節點 (各向同性)", A_node, c_iso)
r2 = report("全部 60 節點 (同緯度)", A_node, c_lat)
r3 = report(f"高緯 {hi_mask.sum()} 節點 (各向同性)", A_hi, c_iso_hi)
r4 = report(f"高緯 {hi_mask.sum()} 節點 (同緯度)", A_hi, c_lat_hi)
r5 = report(f"剔除 0,9 ({len(keep)} 節點, 各向同性)", A_keep, c_iso_k)
r6 = report(f"剔除 0,9 ({len(keep)} 節點, 同緯度)", A_keep, c_lat_k)

# 額外: mean|T| 對比 O3 已知 36.2 (ΔE=0 測試)
print(f"\n--- 參考 (O3) ---")
print(f"全部 60 mean|T| = {A_node.mean():.2f} μK (O3: 36.2)")
print(f"ΔE=0 12節點 mean|T| = {A_node[[10,12,19,22,23,25,28,32,37,40,45,46]].mean():.2f} (O3: 19.05)")

# 儲存
with open(os.path.join(OUT, "06_amplitude_test.txt"), "w") as f:
    f.write("# O30-06: mean|T| 幅度檢驗\n")
    f.write(f"# 日期: 2026-08-21, 4.17°, 控制 {N_CONTROL}\n")
    f.write(f"# ALL_ISO: mean|T|={r1['mu']:.3f} z={r1['z']:+.3f} p2={r1['p']:.4f} p1={r1['p1']:.4f}\n")
    f.write(f"# ALL_LAT: mean|T|={r2['mu']:.3f} z={r2['z']:+.3f} p2={r2['p']:.4f} p1={r2['p1']:.4f}\n")
    f.write(f"# HI_ISO: mean|T|={r3['mu']:.3f} z={r3['z']:+.3f} p2={r3['p']:.4f} p1={r3['p1']:.4f}\n")
    f.write(f"# HI_LAT: mean|T|={r4['mu']:.3f} z={r4['z']:+.3f} p2={r4['p']:.4f} p1={r4['p1']:.4f}\n")
    f.write(f"# DROP_ISO: mean|T|={r5['mu']:.3f} z={r5['z']:+.3f} p2={r5['p']:.4f} p1={r5['p1']:.4f}\n")
    f.write(f"# DROP_LAT: mean|T|={r6['mu']:.3f} z={r6['z']:+.3f} p2={r6['p']:.4f} p1={r6['p1']:.4f}\n")

print(f"\n✅ 已存: {os.path.join(OUT, '06_amplitude_test.txt')}")
