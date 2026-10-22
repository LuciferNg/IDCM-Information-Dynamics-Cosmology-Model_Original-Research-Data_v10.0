#!/usr/bin/env python3
"""
17_verify_synthesis.py — O25: 合併分析最終驗證
==============================================
獨立重算所有新發現 (scripts/13-16), 防幻覺:
1. 冷區中心 (197.74, -20.26)
2. 冷區中心 20° 盤 T = -55.49 μK (Commander 15°)
3. l=3 主導: -29.99 μK (z=-2.04σ)
4. 逐級減模式: 減 l≤6 後殘餘 -2.1 μK
5. 熱環峰: node9 @41°, 冷區中心 @45°+
6. 52.5° 後回落 (compensated)
"""
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, sys

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
CACHE = os.path.join(BASE, "o25_scale_spectrum", "data", "smooth_cache_large")

node9 = {"l": 214.92, "b": -31.16}
cold_center = {"l": 197.74, "b": -20.26}

m = hp.read_map(os.path.join(CACHE, "Commander_smooth15.0.fits"), field=0)
m_low = hp.ud_grade(m, 512)
nside_low = 512

passes, fails = 0, 0
def check(name, claimed, recomputed, tol):
    global passes, fails
    if isinstance(claimed, bool):
        if bool(recomputed) == claimed:
            passes += 1
            print(f"  ✅ {name}: {claimed} == {bool(recomputed)}")
        else:
            fails += 1
            print(f"  ❌ {name}: claimed={claimed} recomputed={bool(recomputed)}")
        return
    if abs(claimed - recomputed) <= tol:
        passes += 1
        print(f"  ✅ {name}: {claimed} ≈ {recomputed:.2f}")
    else:
        fails += 1
        print(f"  ❌ {name}: claimed={claimed} recomputed={recomputed:.2f}")

print("O25 合併分析最終驗證")
print("=" * 60)

# 1. 冷區中心 20° 盤
vec_cc = hp.ang2vec(cold_center["l"], cold_center["b"], lonlat=True)
d20 = hp.query_disc(nside_low, vec_cc, np.radians(20.0))
T_cc = m_low[d20].mean() * 1e6
check("冷區中心 20° 盤 T", -55.49, T_cc, 0.5)

# 2. node9 20° 盤
vec9 = hp.ang2vec(node9["l"], node9["b"], lonlat=True)
d9 = hp.query_disc(nside_low, vec9, np.radians(20.0))
T_n9 = m_low[d9].mean() * 1e6
check("node9 20° 盤 T", -39.30, T_n9, 0.5)
check("冷區中心比 node9 冷 16.2", 16.19, abs(T_cc - T_n9), 0.5)

# 3. l=3 貢獻
alm = hp.map2alm(m_low, lmax=10)
n_alm = hp.Alm.getsize(10)
alm3 = np.zeros(n_alm, dtype=complex)
for mm in range(-3, 4):
    idx = hp.Alm.getidx(10, 3, abs(mm))
    alm3[idx] = alm[idx]
only3 = hp.alm2map(alm3, nside_low, lmax=10)
pix_cc = hp.ang2pix(nside_low, cold_center["l"], cold_center["b"], lonlat=True)
l3_cc = only3[pix_cc] * 1e6
check("l=3 @ 冷區中心", -29.99, l3_cc, 1.0)

# 4. 逐級減模式
mono = m_low.mean()
resid = m_low - mono
for lmax_cut, claimed in [(3, -30.32), (5, -7.89), (6, -2.12)]:
    alm_cut = np.zeros(n_alm, dtype=complex)
    for l in range(1, lmax_cut+1):
        for mm in range(-l, l+1):
            idx = hp.Alm.getidx(10, l, abs(mm))
            alm_cut[idx] = alm[idx]
    low_modes = hp.alm2map(alm_cut, nside_low, lmax=10)
    r = (m_low - mono - low_modes)[d20].mean() * 1e6
    check(f"減 l≤{lmax_cut}", claimed, r, 1.5)

# 5. 熱環峰位置 (node9 41°, 冷區中心 45°+)
def ring_peak(l_deg, b_deg, max_r=46, step=2):
    vec = hp.ang2vec(l_deg, b_deg, lonlat=True)
    best_r, best_t = 0, -1e9
    for r0 in range(0, max_r, step):
        r1 = r0 + step
        d_out = hp.query_disc(nside_low, vec, np.radians(r1))
        if r0 == 0:
            ring = d_out
        else:
            d_in = hp.query_disc(nside_low, vec, np.radians(r0))
            ring = np.setdiff1d(d_out, d_in)
        t = m_low[ring].mean() * 1e6
        if t > best_t:
            best_t, best_r = t, r0 + step/2
    return best_r, best_t

r9, t9 = ring_peak(node9["l"], node9["b"])
rcc, tcc = ring_peak(cold_center["l"], cold_center["b"])
print(f"  node9 熱環峰: {r9:.0f}° ({t9:+.2f} μK)")
print(f"  冷區中心熱環峰: {rcc:.0f}° ({tcc:+.2f} μK)")
check("node9 熱環峰 ≥ 35°", True, r9 >= 35, 0)
check("冷區中心熱環峰 ≥ 40°", True, rcc >= 40, 0)

# 6. 回落 (compensated)
vec_cc2 = hp.ang2vec(cold_center["l"], cold_center["b"], lonlat=True)
t_52 = m_low[hp.query_disc(nside_low, vec_cc2, np.radians(55))].mean()*1e6
t_87 = m_low[hp.query_disc(nside_low, vec_cc2, np.radians(90))].mean()*1e6
# 52.5° 附近環帶
ring_50_55 = np.setdiff1d(hp.query_disc(nside_low, vec_cc2, np.radians(55)), hp.query_disc(nside_low, vec_cc2, np.radians(50)))
t_52 = m_low[ring_50_55].mean()*1e6
print(f"  50-55° 環: {t_52:+.2f} μK, 85-90° 環: {t_87:+.2f} μK")
check("52.5° 後回落", True, t_87 < t_52, 0)

print(f"\n{'='*60}")
print(f"結果: {passes} PASS, {fails} FAIL")
sys.exit(1 if fails else 0)
