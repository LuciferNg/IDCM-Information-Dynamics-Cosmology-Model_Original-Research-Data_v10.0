#!/usr/bin/env python3
"""
02_stack_radial.py — O30: 60節點堆疊 radial profile vs 隨機位置
=================================================================
方法:
  1. 4.17° 平滑 SMICA → ud_grade 到 nside 128 (光束 4.17° ≫ 像素 0.46°, 無損)
  2. 每節點: 0-10° 環帶 (0.5° bin) 平均溫度 → 60 節點堆疊 profile
  3. 1000 組隨機 60 點 (各向同性) → 隨機堆疊分佈 per bin
  4. 節點 vs 隨機: 每 bin z-score + 全 profile χ²
  5. 高緯度子集 (|b|≥30°) 重複
  6. 剔除 node0/node9 重複 (系統性 vs 單一強冷)
框架: ICRS→Galactic + query_disc (C 實作, 快)
"""
import healpy as hp
import numpy as np
import os, time
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy import stats

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache/smica2_smooth4.17.fits")
NODES = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
OUT = os.path.join(BASE, "o30_node_systematics/data")

RNG = np.random.default_rng(20260817)
N_CONTROL = 1000
R_MAX = 10.0
BIN = 0.5
BINS = np.arange(0, R_MAX + 1e-9, BIN)  # 20 bins: 0-0.5 ... 9.5-10
N_BIN = len(BINS) - 1
NSIDE_D = 128  # 降採樣 nside

print("=" * 66)
print("O30-02: 60節點堆疊 radial profile vs 隨機")
print("=" * 66)

t0 = time.time()
# ---------- 1. 載入 + 降採樣 ----------
m = hp.read_map(CACHE, field=0)
m_d = hp.ud_grade(m, NSIDE_D)  # 4.17° beam → nside 128 (0.46° pix) 無損
npix_d = hp.nside2npix(NSIDE_D)
print(f"SMICA 4.17° → nside {NSIDE_D} ({npix_d} pix), std={m_d.std()*1e6:.1f} μK")

# ---------- 2. 節點 (ICRS→Galactic) ----------
nodes = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg
hi_mask = np.abs(b_deg) >= 30
vecs = hp.ang2vec(l_deg, b_deg, lonlat=True)  # (60,3)

def radial_profile(centers_vecs, m_map, nsd):
    """每中心 0.5° 環帶 mean → (n_centers, N_BIN)"""
    prof = np.full((len(centers_vecs), N_BIN), np.nan)
    for i, v in enumerate(centers_vecs):
        pix_disc = hp.query_disc(nsd, v, np.radians(R_MAX), inclusive=True)
        if len(pix_disc) == 0:
            continue
        vpix = hp.pix2vec(nsd, pix_disc)
        vpix = np.array(vpix).T  # (n,3)
        dots = np.clip(vpix @ v, -1, 1)
        angs = np.degrees(np.arccos(dots))  # (n,)
        vals = m_map[pix_disc] * 1e6
        for bi in range(N_BIN):
            sel = (angs >= BINS[bi]) & (angs < BINS[bi+1])
            if sel.sum() > 0:
                prof[i, bi] = vals[sel].mean()
    return prof

# ---------- 3. 節點堆疊 ----------
print("節點堆疊 profile...")
prof_node = radial_profile(vecs, m_d, NSIDE_D)
mean_node = np.nanmean(prof_node, axis=0)
std_node = np.nanstd(prof_node, axis=0, ddof=1)

prof_hi = radial_profile(vecs[hi_mask], m_d, NSIDE_D)
mean_hi = np.nanmean(prof_hi, axis=0)

keep = np.array([i for i in range(60) if i not in (0, 9)])
prof_keep = radial_profile(vecs[keep], m_d, NSIDE_D)
mean_keep = np.nanmean(prof_keep, axis=0)

print(f"  完成 ({time.time()-t0:.0f}s)")

# ---------- 4. 隨機控制 (1000 組) ----------
print(f"隨機控制 {N_CONTROL} 組 × 60 點...")
t1 = time.time()
ctrl = np.zeros((N_CONTROL, N_BIN))
for k in range(N_CONTROL):
    rpix = RNG.integers(0, npix_d, size=60)
    rvec = hp.pix2vec(NSIDE_D, rpix)
    rvec = np.array(rvec).T
    prof_r = radial_profile(rvec, m_d, NSIDE_D)
    ctrl[k] = np.nanmean(prof_r, axis=0)
print(f"  完成 ({time.time()-t1:.0f}s)")

ctrl_mean = ctrl.mean(axis=0)
ctrl_std = ctrl.std(axis=0, ddof=1)

z = (mean_node - ctrl_mean) / ctrl_std
z_hi = (mean_hi - ctrl_mean) / ctrl_std
z_keep = (mean_keep - ctrl_mean) / ctrl_std

# 全 profile χ² (合併 10 bin 為 5 個 1° bin 增統計力)
def chi2_profile(zs, dof=None):
    # 用每 bin z² 和 (獨立性近似)
    chi2 = np.nansum(zs**2)
    dof = dof or N_BIN
    p = 1 - stats.chi2.cdf(chi2, dof)
    return chi2, p

chi2_all, p_all = chi2_profile(z)
chi2_hi, p_hi = chi2_profile(z_hi)
chi2_keep, p_keep = chi2_profile(z_keep)

print(f"\n{'bin(°)':>9} {'節點':>8} {'高緯':>8} {'剔0,9':>8} {'隨機':>8} {'z':>7} {'z_hi':>7}")
for bi in range(N_BIN):
    print(f"{BINS[bi]:>4.1f}-{BINS[bi+1]:>4.1f} {mean_node[bi]:>+8.2f} {mean_hi[bi]:>+8.2f} {mean_keep[bi]:>+8.2f} {ctrl_mean[bi]:>+8.2f} {z[bi]:>+7.2f} {z_hi[bi]:>+7.2f}")

print(f"\nχ² (全部 60): {chi2_all:.1f}/{N_BIN}dof, p={p_all:.4f}")
print(f"χ² (高緯 31): {chi2_hi:.1f}/{N_BIN}dof, p={p_hi:.4f}")
print(f"χ² (剔0,9 58): {chi2_keep:.1f}/{N_BIN}dof, p={p_keep:.4f}")

# 中心 bin 特寫
z0 = z[0]
print(f"\n中心 bin (0-0.5°): 節點 {mean_node[0]:+.2f} vs 隨機 {ctrl_mean[0]:+.2f}±{ctrl_std[0]:.2f} → z={z0:+.2f}σ")
print(f"內 2° 平均 z = {np.nanmean(z[:4]):+.2f}σ (4 bin)")

# ---------- 5. 儲存 ----------
with open(os.path.join(OUT, "02_stack_radial.txt"), "w") as f:
    f.write("# O30-02: 堆疊 radial profile (μK), nside 128 降採樣\n")
    f.write(f"# 日期: 2026-08-21, 4.17° 平滑, 控制組 {N_CONTROL}, bin={BIN}°\n")
    f.write(f"# CHI2_ALL: {chi2_all:.3f}/{N_BIN}dof p={p_all:.4f} | HI: {chi2_hi:.3f} p={p_hi:.4f} | DROP: {chi2_keep:.3f} p={p_keep:.4f}\n")
    f.write(f"# Z0_CENTER: {z0:+.3f}\n")
    f.write("# bin_start bin_end node_mean node_std hi_mean keep_mean ctrl_mean ctrl_std z z_hi z_keep\n")
    for bi in range(N_BIN):
        f.write(f"{BINS[bi]:.1f} {BINS[bi+1]:.1f} {mean_node[bi]:+.3f} {std_node[bi]:.3f} {mean_hi[bi]:+.3f} {mean_keep[bi]:+.3f} {ctrl_mean[bi]:+.3f} {ctrl_std[bi]:+.3f} {z[bi]:+.3f} {z_hi[bi]:+.3f} {z_keep[bi]:+.3f}\n")

print(f"\n✅ 已存: {os.path.join(OUT, '02_stack_radial.txt')} (總時 {time.time()-t0:.0f}s)")
