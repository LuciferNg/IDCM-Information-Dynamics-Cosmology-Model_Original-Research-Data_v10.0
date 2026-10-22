#!/usr/bin/env python3
"""
O52 — DeltaE=0 最後裁決: 多頻譜 + 平滑尺度掃描 (v2, 2026-09-11)
================================================================
SESSION_START 下一步 #1: raw SMICA 冇抑制 (p=0.209) vs 4.17 deg 跨地圖顯著 (p=0.03-0.05)。
本 script 用本地可用數據做最後裁決:
  A. HFI 143/217 GHz 多頻譜 (raw + 0.3 deg + 4.17 deg 自平滑)
  B. SMICA 平滑尺度掃描 (0.5-10 deg caches)
  C. 每 map 三個子集測試: 全部 60 / 高緯 (|b|>=30) / R3 unmasked

判決邏輯:
  - 143/217 @ 4.17 deg 重現抑制 (esp. 高緯子集) -> DeltaE=0 係真實大尺度 CMB 特徵
  - 143/217 冇抑制 -> 4.17 deg 抑制 = SMICA 組件分離/平滑假象

方法 (對齊 05_deltaE0_crossmap.py):
  - a5_nodes.txt ICRS -> Galactic lonlat 先採樣 (frame 鐵律)
  - R3 mask RING, 1=保留
  - permutation test: mean|T| DE0(12) vs non-DE0(48); 高緯 DE0_HIGH(4) vs 高緯其他(27)
  - 每 map 20k perms x 5 seeds -> median p (RNG 變異 ±0.02 鐵律)
  - HFI maps: NESTED -> RING, bad |T|>1e-3 K -> NaN (O27 方法)

執行: /usr/bin/python3 scripts/06_deltaE0_verdict.py
"""
import numpy as np
import healpy as hp
import json, os, time
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
OPF = f'{BASE}/open_problems_fresh'
O52 = f'{OPF}/o52_node_systematics'
CACHE = f'{OPF}/o5_catalog_compare/data/smooth_cache'
CACHE_LARGE = f'{OPF}/o25_scale_spectrum/data/smooth_cache_large'
NODES_FILE = f'{OPF}/cmb_cold_spot/data/a5_nodes.txt'
RAW_SMICA = f'{OPF}/o26_node57_region/data/smica_iqu_2048.fits'
HFI100 = f'{OPF}/o27_node47_foreground/data/HFI_SkyMap_100_2048_R3.01_full.fits'
HFI143 = f'{OPF}/o27_node47_foreground/data/HFI_SkyMap_143_2048_R3.01_full.fits'
HFI217 = f'{OPF}/o27_node47_foreground/data/HFI_SkyMap_217_2048_R3.01_full.fits'
MASK_R3 = f'{OPF}/o27_node47_foreground/data/COM_Mask_CMB-common-Mask-Int_2048_R3.00.fits'
OUTDIR = f'{O52}/data'
os.makedirs(OUTDIR, exist_ok=True)

DE0 = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}
DE0_HIGH = {10, 22, 25, 32}
SEEDS = [20260831, 20260911, 777, 12345, 888]
N_PERM = 20000

# ── 載入節點 (frame 鐵律: ICRS -> Galactic) ──────────────────────
nodes = np.loadtxt(NODES_FILE)
assert nodes.shape == (60, 2)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_arr = np.array([float(g.l.deg) for g in gal])
b_arr = np.array([float(g.b.deg) for g in gal])
high_lat = np.abs(b_arr) >= 30.0

# R3 mask (RING, 1 = keep)
mask_r3 = hp.read_map(MASK_R3, field=0)
nside_m = hp.get_nside(mask_r3)
unmasked = mask_r3[hp.ang2pix(nside_m, l_arr, b_arr, lonlat=True)] > 0.5

de0_idx = np.array([i for i in range(60) if i in DE0])
non_de0_idx = np.array([i for i in range(60) if i not in DE0])
de0_hl_idx = np.array([i for i in range(60) if i in DE0_HIGH])
non_de0_hl_idx = np.array([i for i in range(60) if high_lat[i] and i not in DE0_HIGH])
um_de0_idx = np.array([i for i in range(60) if (i in DE0) and unmasked[i]])
um_non_de0_idx = np.array([i for i in range(60) if (i not in DE0) and unmasked[i]])

print(f"DE0: {len(de0_idx)}/60, 非DE0: {len(non_de0_idx)}/60")
print(f"高緯: {high_lat.sum()}/60 (DE0_HIGH {len(de0_hl_idx)} vs 其他 {len(non_de0_hl_idx)})")
print(f"R3 unmasked: {unmasked.sum()}/60 (DE0 {len(um_de0_idx)} vs 其他 {len(um_non_de0_idx)})")

# ── 向量化 permutation test (mean|T| one-sided lower-tail) ───────
def perm_test_vec(vals_de0, vals_other, seeds=SEEDS, n_perm=N_PERM):
    d = vals_de0[np.isfinite(vals_de0)]
    o = vals_other[np.isfinite(vals_other)]
    if len(d) < 2 or len(o) < 2:
        return np.nan, np.nan, np.nan, np.nan
    abs_d, abs_o = np.abs(d), np.abs(o)
    obs = abs_d.mean() - abs_o.mean()
    all_abs = np.concatenate([abs_d, abs_o])
    n1, n = len(abs_d), len(all_abs)
    ps = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        P = np.argsort(rng.random((n_perm, n)), axis=1)
        diff = all_abs[P[:, :n1]].mean(axis=1) - all_abs[P[:, n1:]].mean(axis=1)
        ps.append((np.sum(diff <= obs) + 1) / (n_perm + 1))
    return obs, abs_d.mean(), abs_o.mean(), ps

def welch_p(vals_de0, vals_other):
    from scipy import stats
    d = np.abs(vals_de0[np.isfinite(vals_de0)])
    o = np.abs(vals_other[np.isfinite(vals_other)])
    if len(d) > 1 and len(o) > 1:
        return float(stats.ttest_ind(d, o, equal_var=False).pvalue)
    return np.nan

def read_temps(m, ns, nest=False):
    """採樣 60 節點; 回傳 μK array (bad -> NaN)"""
    pix = hp.ang2pix(ns, l_arr, b_arr, lonlat=True)
    vals = np.array(m[pix], dtype=float)
    bad = (~np.isfinite(vals)) | (np.abs(vals) > 1e-3)
    vals = np.where(bad, np.nan, vals)
    return vals * 1e6  # K -> uK

# ── 地圖清單 ─────────────────────────────────────────────────────
def map_list():
    maps = []
    # SMICA raw
    if os.path.exists(RAW_SMICA):
        maps.append(('SMICA_raw', RAW_SMICA, None, False))
    # SMICA smooth caches (尺度掃描)
    for s in [0.5, 1.0, 2.0, 3.0, 4.17, 7.0, 10.0]:
        f = f'{CACHE}/smica2_smooth{s}.fits'
        if os.path.exists(f):
            maps.append((f'SMICA_{s}deg', f, None, False))
    # NILC / Commander 0.3 + 4.17 caches
    for nm, f in [('NILC_0.3deg', f'{CACHE_LARGE}/NILC_smooth0.3.fits'),
                  ('Commander_0.3deg', f'{CACHE_LARGE}/Commander_smooth0.3.fits'),
                  ('NILC_4.17deg', f'{CACHE}/nilc2_smooth4.17.fits'),
                  ('Commander_4.17deg', f'{CACHE}/commander_smooth4.17.fits')]:
        if os.path.exists(f):
            maps.append((nm, f, None, False))
    # HFI 100/143/217: raw + 0.3 + 4.17 (自平滑, NESTED)
    hfi = [('HFI100_raw', HFI100, True), ('HFI143_raw', HFI143, True),
           ('HFI217_raw', HFI217, True)]
    for nm, path, nest in hfi:
        if os.path.exists(path):
            maps.append((nm, path, None, nest))
            for s in [0.3, 4.17]:
                maps.append((f'{nm}_smooth{s}deg', path, s, nest))
    return maps

def load_map(fpath, smooth_fwhm, nest):
    """O27 方法: bad -> NaN; 平滑用 masked-smoothing (zero-fill + 歸一化)
    避免 NaN 污染成個 map; 平滑後再 cut 一次 bad. 回傳 K units map."""
    t0 = time.time()
    m = hp.read_map(fpath, field=0, nest=nest)
    if nest:
        m = hp.reorder(m, n2r=True)
    bad = (~np.isfinite(m)) | (np.abs(m) > 1e-3)
    m = np.where(bad, np.nan, m)
    if smooth_fwhm is not None:
        fwhm_rad = np.radians(smooth_fwhm)
        mask_ok = np.isfinite(m)
        m0 = np.where(mask_ok, m, 0.0)
        sm = hp.smoothing(m0, fwhm=fwhm_rad, iter=3)
        sm_ok = hp.smoothing(mask_ok.astype(float), fwhm=fwhm_rad, iter=3)
        m = np.where(sm_ok > 0.1, sm / sm_ok, np.nan)
        # 平滑後再 cut (前景殘餘)
        m = np.where(np.abs(m) > 1e-3, np.nan, m)
    print(f"  [load] {os.path.basename(fpath)} fwhm={smooth_fwhm} nest={nest} "
          f"{time.time()-t0:.0f}s", flush=True)
    return m

# ══════════════════════════════════════════════════════════════
print("=" * 76)
print("  O52 — DeltaE=0 最後裁決 (多頻譜 + 尺度掃描)")
print("=" * 76)

results = {}
summary_rows = []
for name, fpath, smooth_fwhm, nest in map_list():
    m = load_map(fpath, smooth_fwhm, nest)
    T = read_temps(m, hp.get_nside(m))
    n_valid = int(np.sum(~np.isnan(T)))
    print(f"  {name}: valid nodes {n_valid}/60", flush=True)
    if n_valid < 30:
        print(f"  !! 太少有效節點, skip", flush=True)
        continue

    tests = {}
    for tname, d_idx, o_idx in [('all', de0_idx, non_de0_idx),
                                ('highlat', de0_hl_idx, non_de0_hl_idx),
                                ('unmasked', um_de0_idx, um_non_de0_idx)]:
        if len(d_idx) == 0 or len(o_idx) == 0:
            continue
        obs, md, mo, ps = perm_test_vec(T[d_idx], T[o_idx])
        wp = welch_p(T[d_idx], T[o_idx])
        tests[tname] = {
            'de0_mean_abs': round(md, 3) if md == md else None,
            'other_mean_abs': round(mo, 3) if mo == mo else None,
            'ratio': round(md/mo, 4) if mo not in (0, np.nan) and md == md else None,
            'perm_p_median': round(float(np.median(ps)), 4) if ps else None,
            'perm_p_min': round(float(np.min(ps)), 4) if ps else None,
            'perm_p_max': round(float(np.max(ps)), 4) if ps else None,
            'welch_p': round(wp, 4) if wp == wp else None,
            'n_de0': int(len(d_idx)), 'n_other': int(len(o_idx)),
        }
    results[name] = tests

    t = tests['all']
    hl = tests.get('highlat', {})
    print(f"  all: ratio={t['ratio']} p={t['perm_p_median']} "
          f"(hl ratio={hl.get('ratio')} p={hl.get('perm_p_median')})", flush=True)
    summary_rows.append({
        'map': name, 'ratio_all': t['ratio'], 'p_all': t['perm_p_median'],
        'ratio_hl': hl.get('ratio'), 'p_hl': hl.get('perm_p_median'),
    })

# ── 聚集度控制: DE0 vs 非DE0 節點角距分佈 ───────────────────────
def mean_pair_dist(idx):
    v = hp.ang2vec(l_arr[idx], b_arr[idx], lonlat=True)
    d = []
    for i in range(len(v)):
        for j in range(i+1, len(v)):
            d.append(np.degrees(np.arccos(np.clip(np.dot(v[i], v[j]), -1, 1))))
    return float(np.mean(d)), float(np.min(d))
md_de0, mn_de0 = mean_pair_dist(de0_idx)
md_oth, mn_oth = mean_pair_dist(non_de0_idx)
clustering = {'de0_mean_pair_deg': md_de0, 'de0_min_pair_deg': mn_de0,
              'other_mean_pair_deg': md_oth, 'other_min_pair_deg': mn_oth}
print(f"\n聚集度: DE0 mean pair {md_de0:.1f} deg (min {mn_de0:.1f}) | "
      f"其他 mean pair {md_oth:.1f} deg (min {mn_oth:.1f})")

# ── 4.17 deg 節點值 dump (SMICA / HFI) ──────────────────────────
node_dump = {}
for nm, fpath, smooth_fwhm, nest in map_list():
    if nm == 'SMICA_4.17deg' or (nm.startswith('HFI') and 'smooth4.17deg' in nm):
        m = load_map(fpath, smooth_fwhm, nest)
        T = read_temps(m, hp.get_nside(m))
        node_dump[nm] = {f'n{i}': (round(float(T[i]), 3) if T[i] == T[i] else None)
                         for i in range(60)}

def is_sig(r, key_ratio, key_p):
    v = r.get(key_p)
    return v is not None and v < 0.05 and r.get(key_ratio) is not None and r.get(key_ratio) < 0.8

def r417_sig(nm, res, subset):
    t = res.get(subset)
    return t is not None and t.get('perm_p_median') is not None \
        and t['perm_p_median'] < 0.05 and t.get('ratio') is not None and t['ratio'] < 0.8

# ── 跨地圖 4.17 deg 一致性 ───────────────────────────────────────
print("\n" + "=" * 76)
print("  4.17 deg 跨地圖總結")
print("=" * 76)
print(f"{'Map':<26}{'ratio':<8}{'p_med':<8}{'p_min':<8}{'p_max':<8}{'hl_ratio':<10}{'hl_p':<8}")
f417 = [r for r in summary_rows if '4.17' in r['map']]
for r in f417:
    t = results[r['map']]['all']
    hl = results[r['map']].get('highlat', {})
    print(f"{r['map']:<26}{r['ratio_all']:<8.3f}{r['p_all']:<8.4f}"
          f"{t['perm_p_min']:<8.4f}{t['perm_p_max']:<8.4f}"
          f"{r['ratio_hl'] if r['ratio_hl'] is not None else float('nan'):<10.3f}"
          f"{r['p_hl'] if r['p_hl'] is not None else float('nan'):<8.4f}")

sig_all = [r['map'] for r in f417 if is_sig(r, 'ratio_all', 'p_all')]
sig_hl = [r['map'] for r in f417 if is_sig(r, 'ratio_hl', 'p_hl')]
print(f"\n4.17 deg 全部 60 節點抑制 (p<0.05 & ratio<0.8): {len(sig_all)}/{len(f417)} -> {sig_all}")
print(f"4.17 deg 高緯子集抑制 (p<0.05 & ratio<0.8): {len(sig_hl)}/{len(f417)} -> {sig_hl}")

# ── 裁決 (data-driven, 有 guard) ────────────────────────────────
hfi417 = {nm: results[nm] for nm in results if nm.startswith('HFI') and 'smooth4.17deg' in nm}
hfi_present = [nm for nm, r in hfi417.items() if r and 'all' in r]
hfi_sig_all = [nm for nm in hfi_present
               if r417_sig(nm, hfi417[nm], 'all')]
hfi_sig_hl = [nm for nm in hfi_present
              if r417_sig(nm, hfi417[nm], 'highlat')]
comp417 = [nm for nm in ('SMICA_4.17deg', 'NILC_4.17deg', 'Commander_4.17deg') if nm in results]
comp_sig_all = [nm for nm in comp417 if r417_sig(nm, results[nm], 'all')]
comp_sig_hl = [nm for nm in comp417 if r417_sig(nm, results[nm], 'highlat')]

print(f"\n組件分離地圖 (SMICA/NILC/Commander) @4.17: all {len(comp_sig_all)}/{len(comp417)} 顯著, "
      f"高緯 {len(comp_sig_hl)}/{len(comp417)} 顯著")
print(f"多頻譜 (100/143/217 GHz) @4.17: all {len(hfi_sig_all)}/{len(hfi_present)} 顯著, "
      f"高緯 {len(hfi_sig_hl)}/{len(hfi_present)} 顯著")

verdict = ''
if not hfi_present:
    verdict = ('VERDICT_X: HFI 4.17 deg 結果缺失 (平滑失敗), 裁決唔成立 — 修正後重跑。')
elif comp_sig_hl or hfi_sig_hl:
    verdict = ('VERDICT_A: 高緯子集有顯著抑制 -> DeltaE=0 係真實大尺度 CMB 特徵候選 '
               '(需 PR4 做最終確認)。')
elif hfi_sig_all:
    verdict = ('VERDICT_B: 多頻譜全 60 節點重現抑制但高緯唔顯著 -> 效應主體喺銀河盤內, '
               '高緯證據不足; 🟡 弱效應 (非穩健)。')
elif comp_sig_all:
    verdict = ('VERDICT_C: 組件分離地圖 all-60 顯著但 143/217 GHz 多頻譜冇重現 -> '
               '4.17 deg 抑制係 SMICA 組件分離/平滑假象。DeltaE=0 線路判死 🔴。')
else:
    verdict = ('VERDICT_D: 冇任何地圖喺任何子集重現顯著抑制 -> DeltaE=0 抑制唔存在, '
               'O52 完全閉合 (只有 node0/node9 係真異常)。')
print("\n" + "=" * 76)
print("  裁決")
print("=" * 76)
print(verdict)

out = {
    'generated': '2026-09-11',
    'method': 'O52 06_deltaE0_verdict.py: perm test mean|T|, 20k perms x 5 seeds, '
              'HFI NESTED->RING, bad>1e-3K->NaN, smooth fwhm deg',
    'seeds': SEEDS,
    'de0_set': sorted(DE0), 'de0_high': sorted(DE0_HIGH),
    'clustering_control': clustering,
    'results': results,
    'node_dump_4p17': node_dump,
    'verdict': verdict,
}
outpath = os.path.join(OUTDIR, 'o52_deltaE0_verdict.json')
with open(outpath, 'w') as f:
    json.dump(out, f, indent=1, default=float)
print(f"\n✅ 已存 {outpath}")
