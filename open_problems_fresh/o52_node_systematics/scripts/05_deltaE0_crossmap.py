#!/usr/bin/env python3
"""
O52 ΔE=0 跨地圖驗證 (v1)
=========================
原始問題: 12 個 ΔE=0 節點 mean|T| = 19.05 μK vs 非 ΔE=0 36.18 μK (p=0.038, SMICA 4.17°).
O4 發現: 只係 SMICA 4.17° 顯著, NILC/Commander 唔顯著.
本 script: 用 raw (unsmoothed) 地圖重新驗證, 睇 ΔE=0 抑制係咪跨地圖一致.

方法:
  1. Raw SMICA (nside=2048, 無平滑) — 直接讀 pixel
  2. NILC/Commander @ 0.3° (最小可用平滑, O25 cache)
  3. 對比: ΔE=0 12節點 vs 非 ΔE=0 48節點, 用 mean|T| 做 permutation test
  4. 高緯 4 節點子集 {10,22,25,32} 獨立測試
  5. R3 mask 分層

反幻覺鐵律:
  - 所有座標用 Galactic frame (lonlat=True)
  - 先 frame check 再採樣
  - 讀取 raw 地圖即時轉 μK
"""

import numpy as np
import healpy as hp
import json, os, sys
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O52 = f'{BASE}/open_problems_fresh/o52_node_systematics'
CACHE = f'{BASE}/open_problems_fresh/o5_catalog_compare/data/smooth_cache'
CACHE_LARGE = f'{BASE}/open_problems_fresh/o25_scale_spectrum/data/smooth_cache_large'
NODES_FILE = f'{BASE}/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
RAW_SMICA = f'{BASE}/open_problems_fresh/o26_node57_region/data/smica_iqu_2048.fits'
MASK_R3 = f'{BASE}/open_problems_fresh/o27_node47_foreground/data/COM_Mask_CMB-common-Mask-Int_2048_R3.00.fits'
OUTDIR = f'{O52}/data'
os.makedirs(OUTDIR, exist_ok=True)

# ── ΔE=0 節點 ────────────────────────────────────────────────
DE0 = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}
DE0_HIGH = {10, 22, 25, 32}  # 高緯子集 (|b|>=30°)

# ── 載入節點 ─────────────────────────────────────────────────
nodes = np.loadtxt(NODES_FILE)
assert nodes.shape == (60, 2)

sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_arr = np.array([float(g.l.deg) for g in gal])
b_arr = np.array([float(g.b.deg) for g in gal])
high_lat = np.abs(b_arr) >= 30.0

# R3 mask
mask_r3 = hp.read_map(MASK_R3, field=0)
nside_m = hp.get_nside(mask_r3)
unmasked = mask_r3[hp.ang2pix(nside_m, l_arr, b_arr, lonlat=True)] > 0.5

de0_idx = np.array([i for i in range(60) if i in DE0])
node0_idx = np.array([i for i in range(60) if i not in DE0])
de0_high_idx = np.array([i for i in range(60) if i in DE0_HIGH])

print(f"ΔE=0 節點: {len(de0_idx)}/60 (高緯 {len(de0_high_idx)}/4)")
print(f"非 ΔE=0: {len(node0_idx)}/60")
print(f"高緯度: {high_lat.sum()}/60")
print(f"R3 unmasked: {unmasked.sum()}/60")

# ── 地圖定義 ─────────────────────────────────────────────────
MAPS = []

# 1. Raw SMICA (無平滑)
MAPS.append(('SMICA_raw', 'raw', RAW_SMICA, None, False, 2048))

# 2. NILC 0.3° (最小平滑)
f_nilc = f'{CACHE_LARGE}/NILC_smooth0.3.fits'
if os.path.exists(f_nilc):
    MAPS.append(('NILC_0.3°', 'cmb', f_nilc, None, False, 2048))

# 3. Commander 0.3° (最小平滑)
f_cmd = f'{CACHE_LARGE}/Commander_smooth0.3.fits'
if os.path.exists(f_cmd):
    MAPS.append(('Commander_0.3°', 'cmb', f_cmd, None, False, 2048))

# 4. SMICA 4.17° (對照)
f_sm4 = f'{CACHE}/smica2_smooth4.17.fits'
if os.path.exists(f_sm4):
    MAPS.append(('SMICA_4.17°', 'cmb', f_sm4, None, False, 2048))

# 5. NILC 4.17° (對照)
f_n4 = f'{CACHE}/nilc2_smooth4.17.fits'
if os.path.exists(f_n4):
    MAPS.append(('NILC_4.17°', 'cmb', f_n4, None, False, 2048))

# 6. Commander 4.17° (對照)
f_c4 = f'{CACHE}/commander_smooth4.17.fits'
if os.path.exists(f_c4):
    MAPS.append(('Commander_4.17°', 'cmb', f_c4, None, False, 2048))

def read_node_temps(m, ns, l_arr, b_arr):
    """Read node temperatures from a map"""
    pix = hp.ang2pix(ns, l_arr, b_arr, lonlat=True)
    vals = m[pix]
    # Check for bad values
    bad = (~np.isfinite(vals)) | (np.abs(vals) > 1e19)
    if bad.any():
        print(f"  ⚠️ {bad.sum()} bad pixels, replacing with NaN")
        vals = np.where(bad, np.nan, vals)
    return vals * 1e6  # K → μK

def permutation_test(T_de0, T_other, n_perm=10000, seed=20260831):
    """Permutation test for mean|T| difference"""
    rng = np.random.default_rng(seed)
    obs_de0 = np.nanmean(np.abs(T_de0))
    obs_other = np.nanmean(np.abs(T_other))
    obs_diff = obs_de0 - obs_other
    all_vals = np.concatenate([T_de0[~np.isnan(T_de0)], T_other[~np.isnan(T_other)]])
    n_de0 = sum(~np.isnan(T_de0))
    n_other = sum(~np.isnan(T_other))
    n_total = n_de0 + n_other
    count = 0
    for _ in range(n_perm):
        rng.shuffle(all_vals)
        perm_de0 = np.nanmean(np.abs(all_vals[:n_de0]))
        perm_other = np.nanmean(np.abs(all_vals[n_de0:]))
        if (perm_de0 - perm_other) <= obs_diff:
            count += 1
    p = (count + 1) / (n_perm + 1)
    return obs_de0, obs_other, obs_diff, p

# ══════════════════════════════════════════════════════════════
print("=" * 72)
print("  O52 — ΔE=0 跨地圖驗證")
print("=" * 72)

results = {}
for name, mtype, fpath, _, is_nest, ns in MAPS:
    if not os.path.exists(fpath):
        print(f"\n  {name}: 檔案唔存在 ❌")
        continue
    print(f"\n─── {name} ───")
    
    m = hp.read_map(fpath, field=0)
    
    # Raw SMICA needs special handling: it's in K, includes IQU
    if 'raw' in mtype or 'raw' in name.lower():
        # Check if units are reasonable
        med = np.median(m[np.isfinite(m)])
        print(f"  raw map median={med:.2e}, range=[{m.min():.2e}, {m.max():.2e}]")
    
    T = read_node_temps(m, ns, l_arr, b_arr)
    n_valid = sum(~np.isnan(T))
    print(f"  valid nodes: {n_valid}/60")
    
    if n_valid < 30:
        print(f"  ⚠️ 太少有效節點, skip")
        continue
    
    # ── 全部 60 節點 ──────────────────────────────────────
    T_de0 = T[de0_idx]
    T_other = T[node0_idx]
    m_de0, m_other, diff, p = permutation_test(T_de0, T_other)
    ratio = m_de0 / m_other if m_other != 0 else np.nan
    
    # Welch t-test on mean|T|
    from scipy import stats
    abs_de0 = np.abs(T_de0[~np.isnan(T_de0)])
    abs_other = np.abs(T_other[~np.isnan(T_other)])
    if len(abs_de0) > 1 and len(abs_other) > 1:
        t_stat, p_welch = stats.ttest_ind(abs_de0, abs_other, equal_var=False)
    else:
        t_stat, p_welch = np.nan, np.nan
    
    print(f"  ΔE=0 mean|T| = {m_de0:.2f} μK (n={sum(~np.isnan(T_de0))})")
    print(f"  非ΔE=0 mean|T| = {m_other:.2f} μK (n={sum(~np.isnan(T_other))})")
    print(f"  ratio = {ratio:.3f}, perm p = {p:.4f}, Welch p = {p_welch:.4f}")
    
    # ── 高緯子集 ──────────────────────────────────────────
    hl = high_lat
    if hl.sum() >= 5:
        T_hl_de0 = T[de0_high_idx]
        T_hl_other = T[hl & ~np.isin(np.arange(60), list(DE0_HIGH))]
        if len(T_hl_other) > 0:
            m_hl_de0 = np.nanmean(np.abs(T_hl_de0))
            m_hl_other = np.nanmean(np.abs(T_hl_other))
            hl_ratio = m_hl_de0 / m_hl_other if m_hl_other != 0 else np.nan
            print(f"  高緯 ΔE=0 mean|T| = {m_hl_de0:.2f} μK (n={sum(~np.isnan(T_hl_de0))})")
            print(f"  高緯 其他 mean|T| = {m_hl_other:.2f} μK (n={sum(~np.isnan(T_hl_other))})")
            print(f"  高緯 ratio = {hl_ratio:.3f}")
        else:
            m_hl_de0 = m_hl_other = hl_ratio = np.nan
    else:
        m_hl_de0 = m_hl_other = hl_ratio = np.nan
    
    # ── R3 unmasked 子集 ──────────────────────────────────
    um = unmasked
    um_de0_bool = np.array([i in DE0 for i in range(60)]) & um
    um_other_bool = np.array([i not in DE0 for i in range(60)]) & um
    if um.sum() >= 5 and um_other_bool.sum() > 0:
        T_um_de0 = T[um_de0_bool]
        T_um_other = T[um_other_bool]
        m_um_de0 = np.nanmean(np.abs(T_um_de0)) if len(T_um_de0) > 0 else np.nan
        m_um_other = np.nanmean(np.abs(T_um_other))
        um_ratio = m_um_de0 / m_um_other if m_um_other != 0 and m_um_other is not np.nan else np.nan
        if not np.isnan(m_um_de0):
            print(f"  R3 um ΔE=0 mean|T| = {m_um_de0:.2f} μK (n={sum(~np.isnan(T_um_de0))})")
            print(f"  R3 um 其他 mean|T| = {m_um_other:.2f} μK (n={sum(~np.isnan(T_um_other))})")
            print(f"  R3 um ratio = {um_ratio:.3f}")
    else:
        m_um_de0 = m_um_other = um_ratio = np.nan
    
    results[name] = {
        'de0_mean_abs': round(m_de0, 3),
        'other_mean_abs': round(m_other, 3),
        'ratio': round(ratio, 4),
        'perm_p': round(p, 4),
        'welch_p': round(p_welch, 4),
        'n_de0': int(sum(~np.isnan(T_de0))),
        'n_other': int(sum(~np.isnan(T_other))),
        'hl_de0_mean_abs': round(m_hl_de0, 3) if not np.isnan(m_hl_de0) else None,
        'hl_other_mean_abs': round(m_hl_other, 3) if not np.isnan(m_hl_other) else None,
        'hl_ratio': round(hl_ratio, 4) if not np.isnan(hl_ratio) else None,
        'um_de0_mean_abs': round(m_um_de0, 3) if not np.isnan(m_um_de0) else None,
        'um_other_mean_abs': round(m_um_other, 3) if not np.isnan(m_um_other) else None,
        'um_ratio': round(um_ratio, 4) if not np.isnan(um_ratio) else None,
    }

# ── 總結 ──────────────────────────────────────────────────────
print("\n" + "=" * 72)
print("  總結")
print("=" * 72)
print(f"\n{'Map':<20} {'ΔE=0 mean|T|':<18} {'non-ΔE=0':<18} {'ratio':<10} {'perm p':<10} {'判決':<10}")
print("-" * 86)
for name, r in results.items():
    ratio = r['ratio']
    p = r['perm_p']
    if p < 0.05 and ratio < 0.8:
        verdict = '✅ 有抑制'
    elif p < 0.1 and ratio < 0.9:
        verdict = '🟡 邊緣'
    else:
        verdict = '🔴 冇抑制'
    print(f"{name:<20} {r['de0_mean_abs']:<18.2f} {r['other_mean_abs']:<18.2f} {ratio:<10.3f} {p:<10.4f} {verdict}")

# 跨地圖一致性判定
print(f"\n--- 跨地圖一致性 ---")
p_values = [r['perm_p'] for r in results.values() if r['perm_p'] is not None]
sig_count = sum(1 for p in p_values if p < 0.05)
if sig_count >= 3:
    print(f"✅✅ {sig_count}/{len(p_values)} 地圖顯著 → ΔE=0 抑制係跨地圖真效應")
elif sig_count >= 1:
    print(f"🟡 {sig_count}/{len(p_values)} 地圖顯著 → ΔE=0 抑制係地圖特定")
else:
    print(f"🔴 0/{len(p_values)} 地圖顯著 → ΔE=0 抑制唔存在")

# ── 儲存 ──────────────────────────────────────────────────────
outpath = os.path.join(OUTDIR, 'o52_deltaE0_crossmap.json')
with open(outpath, 'w') as f:
    json.dump(results, f, indent=2, default=float)
print(f"\n✅ 結果已存: {outpath}")