#!/usr/bin/env python3
"""
01_mean_vs_random.py — O30: 60節點整體均值 vs 隨機位置 (Welch t-test)
=====================================================================
問題: 60個A₅節點全部有微冷/微熱系統性?
方法:
  1. 4.17° 平滑 SMICA (smooth_cache) → 抽 60 節點溫度
  2. 零假設: 1000 組隨機 60 點 → mean 分佈
     - 控制 A: 各向同性隨機 sky (uniform)
     - 控制 B: 同緯度重抽 (固定 b, 隨機 l) — 保留緯度分佈, 更保守
  3. Welch t-test: 60節點 mean vs 隨機 mean 分佈
  4. 高緯度子集 (|b|≥30°, 31節點) 重複
  5. 剔除 node0/node9 後重複 → 系統性是否由單一強冷驅動
框架: ICRS→Galactic (a5_nodes.txt 係 ICRS!) + 銀河遮罩
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
os.makedirs(OUT, exist_ok=True)

RNG = np.random.default_rng(20260817)
N_CONTROL = 1000

print("=" * 66)
print("O30-01: 60節點 mean vs 隨機位置 (Welch t-test)")
print("=" * 66)

# ---------- 1. 載入平滑 SMICA + 節點 ----------
m = hp.read_map(CACHE, field=0)
nside = hp.get_nside(m)
npix = hp.nside2npix(nside)
print(f"SMICA 4.17°: NSIDE={nside}, std={m.std()*1e6:.1f} μK")

nodes = np.loadtxt(NODES)  # (60,2) RA, Dec (ICRS!)
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T_node = m[pix] * 1e6  # μK
hi_mask = np.abs(b_deg) >= 30
n_hi = hi_mask.sum()

print(f"\n高緯度子集 (|b|≥30°): {n_hi} 節點")

def control_means(lat_deg, n_pts, n_trials, mode):
    """生成控制組 mean 分佈. mode: 'iso'=各向同性, 'same_lat'=同緯度重抽"""
    out = np.empty(n_trials)
    for k in range(n_trials):
        if mode == 'iso':
            # 均勻 sky: 用 random pixel (等價於均勻 (l,b))
            rpix = RNG.integers(0, npix, size=n_pts)
            out[k] = m[rpix].mean() * 1e6
        else:  # same_lat: 固定 b, 隨機 l (保留緯度分佈)
            rl = RNG.uniform(0, 360, size=n_pts)
            rpix = hp.ang2pix(nside, rl, lat_deg, lonlat=True)
            out[k] = m[rpix].mean() * 1e6
    return out

# ---------- 2. 控制組 ----------
print(f"生成 {N_CONTROL} 組控制 (各向同性 + 同緯度)...")
ctrl_iso = control_means(b_deg, 60, N_CONTROL, 'iso')
ctrl_lat = control_means(b_deg, 60, N_CONTROL, 'same_lat')
ctrl_iso_hi = control_means(b_deg[hi_mask], n_hi, N_CONTROL, 'iso')
ctrl_lat_hi = control_means(b_deg[hi_mask], n_hi, N_CONTROL, 'same_lat')

def report(name, T, ctrl):
    mu, sd = T.mean(), T.std(ddof=1)
    cmu, csd = ctrl.mean(), ctrl.std(ddof=1)
    z = (mu - cmu) / csd
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    t_obs, p_w = stats.ttest_1samp(T, cmu)
    verdict = '🟢🟢 >3σ' if abs(z) > 3 else ('🟢 2-3σ 邊緣' if abs(z) > 2 else '🔴 <2σ')
    print(f"\n--- {name} ---")
    print(f"節點 mean = {mu:+.2f} μK, std = {sd:.2f} μK")
    print(f"隨機 mean 分佈 = {cmu:+.2f} ± {csd:.2f} μK")
    print(f"z = {z:+.2f}σ, p(z) = {p:.4f} | Welch t = {t_obs:+.2f}, p = {p_w:.4f} → {verdict}")
    return dict(mu=mu, sd=sd, cmu=cmu, csd=csd, z=z, p=p, t=t_obs, pw=p_w)

r_all_iso = report("全部 60 節點 (各向同性控制)", T_node, ctrl_iso)
r_all_lat = report("全部 60 節點 (同緯度控制)", T_node, ctrl_lat)
r_hi_iso = report(f"高緯子集 {n_hi} 節點 (各向同性)", T_node[hi_mask], ctrl_iso_hi)
r_hi_lat = report(f"高緯子集 {n_hi} 節點 (同緯度)", T_node[hi_mask], ctrl_lat_hi)

# ---------- 3. 剔除 node0+node9 ----------
keep = np.array([i for i in range(60) if i not in (0, 9)])
T_keep = T_node[keep]
b_keep = b_deg[keep]
ctrl_k_iso = control_means(b_keep, len(keep), N_CONTROL, 'iso')
ctrl_k_lat = control_means(b_keep, len(keep), N_CONTROL, 'same_lat')
r_k_iso = report(f"剔除 node0+node9 ({len(keep)} 節點, 各向同性)", T_keep, ctrl_k_iso)
r_k_lat = report(f"剔除 node0+node9 ({len(keep)} 節點, 同緯度)", T_keep, ctrl_k_lat)

# ---------- 4. 冷/熱端符號統計 ----------
T_cold, T_hot = T_node[T_node < 0], T_node[T_node > 0]
print(f"\n--- 符號統計 ---")
print(f"冷 (T<0): {len(T_cold)}/60, 熱 (T>0): {len(T_hot)}/60")
print(f"冷端 mean|T| = {np.abs(T_cold).mean():.1f} μK, 熱端 mean|T| = {np.abs(T_hot).mean():.1f} μK")
print(f"冷:熱 count 比 = {len(T_cold)}:{len(T_hot)} (隨機期望 30:30)")

# ---------- 5. 儲存 ----------
with open(os.path.join(OUT, "01_mean_vs_random.txt"), "w") as f:
    f.write("# O30-01: 60節點 mean vs 隨機位置\n")
    f.write(f"# 日期: 2026-08-21, 平滑 4.17°, 控制組 {N_CONTROL} 組 (iso=各向同性, lat=同緯度重抽)\n")
    f.write(f"# ALL_ISO: mean={r_all_iso['mu']:+.3f} z={r_all_iso['z']:+.3f} p={r_all_iso['p']:.4f} welch_p={r_all_iso['pw']:.4f}\n")
    f.write(f"# ALL_LAT: mean={r_all_lat['mu']:+.3f} z={r_all_lat['z']:+.3f} p={r_all_lat['p']:.4f} welch_p={r_all_lat['pw']:.4f}\n")
    f.write(f"# HI_ISO({n_hi}): mean={r_hi_iso['mu']:+.3f} z={r_hi_iso['z']:+.3f} p={r_hi_iso['p']:.4f}\n")
    f.write(f"# HI_LAT({n_hi}): mean={r_hi_lat['mu']:+.3f} z={r_hi_lat['z']:+.3f} p={r_hi_lat['p']:.4f}\n")
    f.write(f"# DROP0,9_ISO({len(keep)}): mean={r_k_iso['mu']:+.3f} z={r_k_iso['z']:+.3f} p={r_k_iso['p']:.4f}\n")
    f.write(f"# DROP0,9_LAT({len(keep)}): mean={r_k_lat['mu']:+.3f} z={r_k_lat['z']:+.3f} p={r_k_lat['p']:.4f}\n")
    f.write(f"# COLD_HOT: {len(T_cold)}/{len(T_hot)} | cold_mean_abs={np.abs(T_cold).mean():.2f} hot_mean_abs={np.abs(T_hot).mean():.2f}\n")
    f.write("# ctrl_iso ctrl_lat ctrl_iso_hi ctrl_lat_hi\n")
    for k in range(N_CONTROL):
        f.write(f"{ctrl_iso[k]:.4f} {ctrl_lat[k]:.4f} {ctrl_iso_hi[k]:.4f} {ctrl_lat_hi[k]:.4f}\n")

print(f"\n✅ 已存: {os.path.join(OUT, '01_mean_vs_random.txt')}")
