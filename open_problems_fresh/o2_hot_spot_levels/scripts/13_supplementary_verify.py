#!/usr/bin/env python3
"""
O2 獨立核對補充 v20260909 — script 13
========================================
2026-09-09 建立。補充 script 12 未覆蓋嘅細節值 (第二輪核對):
C1: §7 raw 行 (SMICA 原圖): map_std 108.4, 冷斑 -283.3, 熱節點 +24.3, gap 54.4, raw max 7899
C2: §7 F₆ (157.8,-70.3) 5° 圓盤: mean 69.2 μK, 88.7% 正數
C3: §3 masked max 位置: |b|>=25 -> (171.8,-45.8), |b|>=50 -> (181.3,-54.3); §2 對徑 max 位置 (19.93,56.47)
C4: §3 F₅ >= 150 μK pixel 數 = 350
C5: §6 Wiener weights: w(node0)=0.906, w(node9)=0.788 (wiener_filter.txt)
"""
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, sys, re

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o2_hot_spot_levels'
CACHE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o5_catalog_compare/data/smooth_cache'
CMB = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data'
SMICA_RAW = '/tmp/smica2.fits'  # -> o26 本地 SMICA 原圖 (持久)

passed = failed = 0
def check(name, obs, exp, tol, unit=''):
    global passed, failed
    ok = abs(obs - exp) <= tol
    if ok: passed += 1
    else: failed += 1
    print(f"  {'✅' if ok else '❌'} {name}: {obs:.4f}{unit} vs {exp}{unit} (Δ={abs(obs-exp):.4f})")

print("="*68)
print("O2 獨立核對補充 v20260909 (script 13)")
print("="*68)

# ============ C1: §7 raw 行 (SMICA 原圖) ============
print("\n[C1] §7 raw 行 (SMICA 原圖, 無平滑)")
m = hp.read_map(SMICA_RAW, field=0)
nside = hp.get_nside(m)
check("raw map std 108.4", m.std()*1e6, 108.4, 0.1, ' μK')
# 冷斑 (209,-57) raw
check("raw 冷斑 -283.3", m[hp.ang2pix(nside, 209, -57, lonlat=True)]*1e6, -283.3, 0.1, ' μK')
# 熱節點 raw 平均 (anchored_coloring, hot=0)
nodes = np.loadtxt(f'{CMB}/a5_nodes.txt')
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
coloring = np.loadtxt(f'{CMB}/anchored_coloring.txt', usecols=[0,3])
hot_mask = (coloring[:,1] == 0)
pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
T_raw = m[pix]*1e6
check("raw 熱節點平均 +24.3", T_raw[hot_mask].mean(), 24.3, 0.2, ' μK')
cold_T = T_raw[~hot_mask]
check("raw 冷熱 gap 54.4", T_raw[hot_mask].mean() - cold_T.mean(), 54.4, 0.3, ' μK')
check("raw 全天最熱 7899 (foreground)", m.max()*1e6, 7899, 50, ' μK')
del m

# ============ C2: F₆ 5° 圓盤 ============
print("\n[C2] §7 F₆ (157.8,-70.3) 5° 圓盤 (smooth 1.0° + 5° cap)")
# 文檔定義: F₆ 發現尺度 1.0° 平滑 + 半徑 5° cap (已由組合掃描確認: smooth1.0+cap5.0 = 69.2/88.6)
m5 = hp.read_map(f'{CACHE}/smica2_smooth1.0.fits')
nside = hp.get_nside(m5)
f6 = hp.ang2pix(nside, 157.8, -70.3, lonlat=True)
vec = np.array(hp.pix2vec(nside, f6))
all_vec = np.array(hp.pix2vec(nside, np.arange(hp.nside2npix(nside))))
dot = all_vec[0]*vec[0] + all_vec[1]*vec[1] + all_vec[2]*vec[2]
disc = dot > np.cos(np.radians(5.0))
T_disc = m5[disc]*1e6
check("F₆ 5° 圓盤 mean 69.2", T_disc.mean(), 69.2, 0.2, ' μK')
check("F₆ 5° 圓盤 88.7% 正數", (T_disc>0).mean()*100, 88.7, 0.2, ' %')
del m5

# ============ C3: masked max 位置 ============
print("\n[C3] §3 masked max 位置 (smooth 5.0)")
m5 = hp.read_map(f'{CACHE}/smica2_smooth5.0.fits')
l_pix, b_pix = hp.pix2ang(nside, np.arange(len(m5)), lonlat=True)
for mb, exp_l, exp_b in [(25, 171.8, -45.8), (50, 181.3, -54.3)]:
    T_m = m5.copy()
    T_m[np.abs(b_pix) < mb] = -np.inf
    mi = np.argmax(T_m)
    lm, bm = hp.pix2ang(nside, mi, lonlat=True)
    check(f"|b|>={mb} max l = {exp_l}", lm, exp_l, 0.3, ' °')
    check(f"|b|>={mb} max b = {exp_b}", bm, exp_b, 0.3, ' °')
# §2 對徑 5° 圓盤 max 位置 (19.93, 56.47) — 對徑點 = -cold_vec
cold_vec = -np.array(hp.pix2vec(nside, hp.ang2pix(nside, 209, -57, lonlat=True)))
dot2 = all_vec[0]*cold_vec[0] + all_vec[1]*cold_vec[1] + all_vec[2]*cold_vec[2]
disc2 = dot2 > np.cos(np.radians(5.0))
T_disc2 = m5[disc2]*1e6
mi2 = np.where(disc2)[0][np.argmax(T_disc2)]
l2, b2 = hp.pix2ang(nside, mi2, lonlat=True)
check("§2 對徑 max l = 19.93", l2, 19.93, 0.1, ' °')
check("§2 對徑 max b = 56.47", b2, 56.47, 0.1, ' °')
del m5

# ============ C4: F₅ >= 150 μK pixel 數 ============
print("\n[C4] §3 F₅ >= 150 μK pixel 數 (smooth 5.0)")
m5 = hp.read_map(f'{CACHE}/smica2_smooth5.0.fits')
check("F₅ >=150 μK pixels = 350", np.sum(m5*1e6 >= 150.0), 350, 5, ' px')
del m5

# ============ C5: Wiener weights ============
print("\n[C5] §6 Wiener weights (wiener_filter.txt)")
with open(f'{BASE}/data/wiener_filter.txt') as f:
    w = {}
    for line in f:
        p = line.split()
        if len(p) == 9 and p[0].isdigit():
            w[int(p[0])] = float(p[6])  # header: idx color bfs_d T_obs sign expected wiener_w T_restored residual
check("w(node0, F₅) = 0.906", w[0], 0.906, 0.001)
check("w(node9, F₄) = 0.788", w[9], 0.788, 0.001)

print("\n" + "="*68)
print(f"RESULT: {passed} passed, {failed} failed")
print("🎉 ALL SUPPLEMENTARY CHECKS PASSED" if failed == 0 else "❌ FAILURES PRESENT")
print("="*68)
