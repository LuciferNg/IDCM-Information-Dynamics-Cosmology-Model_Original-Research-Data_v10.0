#!/usr/bin/env python3
"""
04_sign_asymmetry.py — O30: 冷/熱端符號不對稱 (O24 關聯)
===========================================================
問題: 60節點有冇冷端/熱端不對稱?
  - O24: 極端節點 (最冷10/最熱10) 冷色 vs 熱色匹配唔對稱
  - O30: 全 60 節點冷/熱 count 比 + 冷熱 mean|T| 比
方法:
  1. 4.17° 60節點: 冷 count vs 熱 count (binomial vs 30:30)
  2. 冷端 mean|T| vs 熱端 mean|T| (Welch)
  3. 符號檢驗: 每節點 sign vs 隨機期望 (1000 組隨機 60 點 sign count 分佈)
  4. 與 O24 對比: 最冷10/最熱10 冷色匹配率
  5. 高緯子集重複
框架: 4.17° 平滑 SMICA
"""
import healpy as hp
import numpy as np
import os
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy import stats
from collections import Counter

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache/smica2_smooth4.17.fits")
NODES = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
COLOR = os.path.join(BASE, "cmb_cold_spot/data/anchored_coloring.txt")
OUT = os.path.join(BASE, "o30_node_systematics/data")

RNG = np.random.default_rng(20260817)
N_CONTROL = 1000

print("=" * 66)
print("O30-04: 冷/熱端符號不對稱")
print("=" * 66)

m = hp.read_map(CACHE, field=0)
nside = hp.get_nside(m)
npix = hp.nside2npix(nside)

nodes = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T = m[pix] * 1e6
hi_mask = np.abs(b_deg) >= 30

# 著色 (冷=1)
color = {}
with open(COLOR) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        color[int(parts[0])] = int(parts[3])
color_arr = np.array([color[i] for i in range(60)])

# ---------- 1. 冷/熱 count ----------
n_cold = (T < 0).sum()
n_hot = (T > 0).sum()
p_binom = stats.binomtest(n_cold, 60, 0.5).pvalue  # two-sided exact

# 隨機期望: 1000 組隨機 60 點 sign count
ctrl_counts = np.empty(N_CONTROL)
for k in range(N_CONTROL):
    rpix = RNG.integers(0, npix, size=60)
    ctrl_counts[k] = (m[rpix] < 0).sum()
mu_cc, sd_cc = ctrl_counts.mean(), ctrl_counts.std(ddof=1)
z_count = (n_cold - mu_cc) / sd_cc

print(f"\n--- 1. 冷/熱 count ---")
print(f"冷 {n_cold} : 熱 {n_hot} (60)")
print(f"binomial p (vs 30:30) = {p_binom:.4f}")
print(f"隨機冷 count 分佈 = {mu_cc:.1f} ± {sd_cc:.1f} → z = {z_count:+.2f}σ")

# ---------- 2. 冷熱 mean|T| ----------
# 注意: 唔可以用 signed T 做 ttest (sign 分組 mean 必然分離, trivial)
# 正確: 比較 |T_cold| vs |T_hot| 嘅 mean 大小 (冷端係咪真係更強)
T_cold, T_hot = T[T < 0], T[T > 0]
A_cold, A_hot = np.abs(T_cold), np.abs(T_hot)
m_cold, m_hot = A_cold.mean(), A_hot.mean()
t_wh, p_wh = stats.ttest_ind(A_cold, A_hot, equal_var=False)
print(f"\n--- 2. 冷/熱 mean|T| ---")
print(f"冷 mean|T| = {m_cold:.2f} μK (n={len(T_cold)}), 熱 mean|T| = {m_hot:.2f} μK (n={len(T_hot)})")
print(f"比 = {m_cold/m_hot:.3f}x, Welch t (|T|) = {t_wh:+.2f}, p = {p_wh:.4f}")

# ---------- 3. 極端節點冷色匹配 (O24 對比) ----------
order = np.argsort(T)
cold10 = order[:10]   # 最冷 10
hot10 = order[-10:]   # 最熱 10
c_cold10 = (color_arr[cold10] == 1).sum()
c_hot10 = (color_arr[hot10] == 1).sum()
print(f"\n--- 3. 極端 10 vs 著色 (O24 對比) ---")
print(f"最冷10 冷色: {c_cold10}/10 (O24: 8/10)")
print(f"最熱10 冷色: {c_hot10}/10 (O24: 6/10 熱色)")

# 隨機對照: 隨機 10 點冷色期望
ctrl_cold10 = []
for k in range(N_CONTROL):
    r10 = RNG.choice(60, 10, replace=False)
    ctrl_cold10.append((color_arr[r10] == 1).sum())
ctrl_cold10 = np.array(ctrl_cold10)
p_cc = (ctrl_cold10 >= c_cold10).mean()
print(f"隨機 10 點冷色 ≥ {c_cold10}: p = {p_cc:.4f} (期望 ~30% = 3/10)")

# ---------- 4. 高緯子集 ----------
Th = T[hi_mask]
n_cold_h = (Th < 0).sum()
n_hot_h = len(Th) - n_cold_h
print(f"\n--- 4. 高緯子集 ({hi_mask.sum()} 節點) ---")
print(f"冷 {n_cold_h} : 熱 {n_hot_h}")
# 同緯度隨機對照
ctrl_h = np.empty(N_CONTROL)
for k in range(N_CONTROL):
    rl = RNG.uniform(0, 360, size=hi_mask.sum())
    rpix = hp.ang2pix(nside, rl, b_deg[hi_mask], lonlat=True)
    ctrl_h[k] = (m[rpix] < 0).sum()
z_h = (n_cold_h - ctrl_h.mean()) / ctrl_h.std(ddof=1)
print(f"隨機冷 count = {ctrl_h.mean():.1f} ± {ctrl_h.std(ddof=1):.1f} → z = {z_h:+.2f}σ")

# ---------- 5. 儲存 ----------
with open(os.path.join(OUT, "04_sign_asymmetry.txt"), "w") as f:
    f.write("# O30-04: 冷/熱符號不對稱\n")
    f.write(f"# 日期: 2026-08-21, 4.17° 平滑, 控制 {N_CONTROL}\n")
    f.write(f"# COLD_HOT_COUNT: {n_cold}/{n_hot} | binom_p={p_binom:.4f} | z={z_count:+.3f}\n")
    f.write(f"# COLD_ABS={m_cold:.3f} HOT_ABS={m_hot:.3f} RATIO={m_cold/m_hot:.3f} | welch_t={t_wh:+.3f} p={p_wh:.4f}\n")
    f.write(f"# EXTREME: cold10_coldcolor={c_cold10}/10 (p_ctrl={p_cc:.4f}) hot10_coldcolor={c_hot10}/10\n")
    f.write(f"# HI({hi_mask.sum()}): cold={n_cold_h} hot={n_hot_h} z={z_h:+.3f}\n")

print(f"\n✅ 已存: {os.path.join(OUT, '04_sign_asymmetry.txt')}")
