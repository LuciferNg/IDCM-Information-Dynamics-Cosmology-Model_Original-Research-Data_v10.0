#!/usr/bin/env python3
"""
O45 — 閉合攻堅 6b: 正環控制測試 (向量化, 2026-09-12)
======================================================
問題: 冷斑 10-20° 環 mean +28 μK — 結構性補償環定係背景 CMB?
向量化: dot product 分批計算 500 隨機點嘅環 mean
"""
import os, json
import numpy as np
import healpy as hp

PROJECT = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
CACHE = os.path.join(PROJECT, 'open_problems_fresh/o5_catalog_compare/data/smooth_cache')
OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

COLD = (209.0, -57.0)
N_RAND = 500
CHUNK = 50

m = hp.read_map(os.path.join(CACHE, 'smica2_smooth4.17.fits'))
m = hp.ud_grade(m, 256)  # 4.17° smooth 下 nside=256 已夠 (pixel 0.23° << 4.17°)
nside = hp.get_nside(m)
npix = hp.nside2npix(nside)
T = m * 1e6
v_pix = hp.pix2vec(nside, np.arange(npix))  # (3, npix)

def rings_for_vecs(vecs, lo_deg, hi_deg):
    """vecs: (N,3) → 每個點嘅 [lo,hi) 環 mean"""
    vecs = np.atleast_2d(np.asarray(vecs, dtype=float))
    if vecs.shape[1] != 3:
        vecs = vecs.T  # 強制 (N,3)
    N = len(vecs)
    out = np.empty(N)
    for i in range(0, N, CHUNK):
        vc = vecs[i:i+CHUNK]  # (c,3)
        cosang = np.clip(vc @ v_pix, -1, 1)  # (c, npix)
        ang = np.degrees(np.arccos(cosang))
        mask = (ang >= lo_deg) & (ang < hi_deg)
        # 每行 mean (忽略空行)
        cnt = mask.sum(axis=1)
        s = (mask * T[None, :]).sum(axis=1)
        out[i:i+CHUNK] = np.where(cnt > 0, s/np.maximum(cnt,1), np.nan)
    return out

v0 = hp.ang2vec(COLD[0], COLD[1], lonlat=True)

cs_ring_10_20 = rings_for_vecs(v0[None,:], 10, 20)[0]
cs_ring_12_18 = rings_for_vecs(v0[None,:], 12, 18)[0]
cs_core = rings_for_vecs(v0[None,:], 0, 8)[0]
print(f"冷斑: 核心 0-8° = {cs_core:.2f} μK, 正環 10-20° = {cs_ring_10_20:.2f} μK, 12-18° = {cs_ring_12_18:.2f} μK")

# 隨機控制
print(f"\n全天空隨機控制 (N={N_RAND}, 向量化):")
rng = np.random.default_rng(42)
u = rng.uniform(-1, 1, N_RAND)
phi = rng.uniform(0, 2*np.pi, N_RAND)
theta = np.arccos(u)
rand_vecs = hp.ang2vec(theta, phi).T  # (N,3)

ring_vals = rings_for_vecs(rand_vecs, 10, 20)
ring_vals_12_18 = rings_for_vecs(rand_vecs, 12, 18)
core_vals = rings_for_vecs(rand_vecs, 0, 8)

print(f"  10-20° 環: 隨機 mean={np.nanmean(ring_vals):+.2f} ± {np.nanstd(ring_vals):.2f} μK")
z10 = (cs_ring_10_20 - np.nanmean(ring_vals))/np.nanstd(ring_vals)
pct10 = np.mean(ring_vals > cs_ring_10_20)*100
print(f"  冷斑 +{cs_ring_10_20:.2f}: z={z10:+.2f}σ, percentile={pct10:.1f}%")
print(f"  12-18° 環: 隨機 mean={np.nanmean(ring_vals_12_18):+.2f} ± {np.nanstd(ring_vals_12_18):.2f} μK")
z18 = (cs_ring_12_18 - np.nanmean(ring_vals_12_18))/np.nanstd(ring_vals_12_18)
pct18 = np.mean(ring_vals_12_18 > cs_ring_12_18)*100
print(f"  冷斑 +{cs_ring_12_18:.2f}: z={z18:+.2f}σ, percentile={pct18:.1f}%")
print(f"  0-8° 核心: 隨機 mean={np.nanmean(core_vals):+.2f} ± {np.nanstd(core_vals):.2f} μK (冷斑 {cs_core:.2f})")
z_core = (cs_core - np.nanmean(core_vals))/np.nanstd(core_vals)
print(f"  冷斑核心 z={z_core:+.2f}σ (對照: 冷斑本身係最冷結構)")

# 對蹠點
anti_ring = rings_for_vecs((-v0)[None,:], 10, 20)[0]
anti_core = rings_for_vecs((-v0)[None,:], 0, 8)[0]
print(f"\n對蹠點: 10-20° = {anti_ring:+.2f} μK, 0-8° = {anti_core:+.2f} μK")

# 儲存
out = {
    'product': 'O45 closure-6: ring control test (vectorized)',
    'date': '2026-09-12',
    'cold_spot': {'ring_10_20': float(cs_ring_10_20), 'ring_12_18': float(cs_ring_12_18),
                  'core': float(cs_core)},
    'random_control': {
        'N': N_RAND,
        'ring_10_20_mean': float(np.nanmean(ring_vals)), 'ring_10_20_std': float(np.nanstd(ring_vals)),
        'z_10_20': float(z10), 'percentile_10_20': float(pct10),
        'ring_12_18_mean': float(np.nanmean(ring_vals_12_18)), 'ring_12_18_std': float(np.nanstd(ring_vals_12_18)),
        'z_12_18': float(z18), 'percentile_12_18': float(pct18),
        'core_mean': float(np.nanmean(core_vals)), 'core_std': float(np.nanstd(core_vals)),
        'z_core': float(z_core)},
    'antipode': {'ring_10_20': float(anti_ring), 'core': float(anti_core)},
}
with open(os.path.join(OUTDIR, '08_ring_control.json'), 'w') as f:
    json.dump(out, f, indent=2)
print(f"\n儲存: {OUTDIR}/08_ring_control.json")