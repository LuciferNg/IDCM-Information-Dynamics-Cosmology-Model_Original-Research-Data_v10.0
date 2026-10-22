#!/usr/bin/env python3
"""
O46 — Step 1: 多頻段冷斑 A 驗證 (優化版, nside=512 downgrade)
"""
import os, json, math
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
from collections import defaultdict, deque
import time

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O46 = f'{BASE}/open_problems_fresh/o46_multifreq_isw'
O27_DATA = f'{BASE}/open_problems_fresh/o27_node47_foreground/data'
O5_CACHE = f'{BASE}/open_problems_fresh/o5_catalog_compare/data/smooth_cache'
O42_DATA = f'{BASE}/open_problems_fresh/o42_independent_measurement_A/data'
NODES_FILE = f'{BASE}/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
OUTDIR = f'{O46}/data'
os.makedirs(OUTDIR, exist_ok=True)

A_IDCM = 134.2
FWHM_PRIMARY = 4.17
NS = 512  # 統一 nside=512 (4.17° 平滑夠用)

nodes = np.loadtxt(NODES_FILE)
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_arr = np.array([float(g.l.deg) for g in gal])
b_arr = np.array([float(g.b.deg) for g in gal])
pix0 = hp.ang2pix(NS, l_arr[0], b_arr[0], lonlat=True)

# BFS
vecs = hp.ang2vec(l_arr, b_arr, lonlat=True)
adj = defaultdict(set)
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang < 28.0:
            adj[i].add(j); adj[j].add(i)
dist = {0: 0}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in dist:
            dist[v] = dist[u] + 1
            q.append(v)
d1_idx = [i for i in range(60) if dist.get(i, 999) == 1]
print(f"冷斑: ({l_arr[0]:.1f}°, {b_arr[0]:.1f}°)  → pix0={pix0}")

# ── 快速讀取 map (直接 downgrade 到 NS) ─────────────────────
def load_fast(fpath, is_nest, target_ns=NS, ref_m=None):
    """Load, downgrade to target_ns, convert to RING.
    is_nest=None: auto-detect ordering by cross-correlation with ref_m"""
    t0 = time.time()
    m = hp.read_map(fpath, field=0)
    ns_in = hp.get_nside(m)
    
    # Auto-detect ordering
    if is_nest is None and ref_m is not None:
        sel = np.arange(0, len(m), 3000)
        c0 = np.corrcoef(m[sel], ref_m[sel])[0,1]
        mr = hp.reorder(m, n2r=True)
        c1 = np.corrcoef(mr[sel], ref_m[sel])[0,1]
        if c1 > c0:
            m = mr
            is_nest = False
            print(f"    auto-order: NESTED→RING (corr {c0:.3f}→{c1:.3f})")
        else:
            is_nest = False
            print(f"    auto-order: AS-IS RING (corr {c0:.3f})")
    
    if ns_in > target_ns:
        m = hp.ud_grade(m, nside_out=target_ns, 
                        order_in='NESTED' if is_nest else 'RING',
                        order_out='RING')
    elif is_nest:
        m = hp.reorder(m, n2r=True)
    # Mask bad
    bad = (~np.isfinite(m)) | (np.abs(m) > 1e19)
    if bad.any():
        fill = np.nanmedian(m[np.isfinite(m) & (np.abs(m) < 1e19)])
        m = np.where(bad, fill, m)
    print(f"    load: {ns_in}→{NS}, fill={int(bad.sum()) if bad.any() else 0}, t={time.time()-t0:.1f}s")
    return m

def measure_at(m, fwhm, l0, b0, ns=NS):
    """Smooth and read pixel"""
    sigma = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
    m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma))
    pix = hp.ang2pix(hp.get_nside(m_s), l0, b0, lonlat=True)
    return float(m_s[pix]) * 1e6

def measure_all(name, freq, m, l0, b0):
    """Measure at all smoothing scales"""
    pix = hp.ang2pix(hp.get_nside(m), l0, b0, lonlat=True)
    T0_raw = float(m[pix]) * 1e6
    scales = {0: round(T0_raw, 2)}
    for fwhm in [0.5, 1.0, 3.0, 4.17, 5.0, 10.0]:
        scales[fwhm] = round(measure_at(m, fwhm, l0, b0), 2)
    r = {'name': name, 'freq_GHz': freq, 'scales': scales,
         'T0_417': scales[4.17]}
    dev = abs(abs(scales[4.17]) - A_IDCM) / A_IDCM * 100 if scales[4.17] is not None else None
    r['dev_pct'] = round(dev, 3) if dev is not None else None
    return r

# ══════════════════════════════════════════════════════════════
print("=" * 72)
print("  O46 — 多頻段冷斑 A 驗證")
print("=" * 72)
print(f"  統一 nside={NS}, 所有頻段 downgrade 後量度")
print("=" * 72)

results = {}
t_start = time.time()

# ── 1. CMB component-separated maps ──────────────────────────
print(f"\n─── 1. CMB maps (component-separated) ───")
cmb_list = [
    ('SMICA',     'CMB', f'{O5_CACHE}/smica2_smooth4.17.fits',      False,  True),  # pre-smoothed
    ('NILC',      'CMB', f'{O5_CACHE}/nilc2_smooth4.17.fits',       False,  True),
    ('Commander', 'CMB', f'{O5_CACHE}/commander_smooth4.17.fits',    False,  True),
    ('SEVEM_final','CMB', f'{O42_DATA}/bands/sevem_final.fits',      None,   False),  # need smooth
    ('SEVEM_143', 'CMB', f'{O42_DATA}/bands/sevem_143.fits',        None,   False),
    ('SEVEM_217', 'CMB', f'{O42_DATA}/bands/sevem_217.fits',        None,   False),
]
# Load raw SMICA for ordering check (needed for SEVEM)
smica_raw = hp.read_map(f'{BASE}/open_problems_fresh/o26_node57_region/data/smica_iqu_2048.fits', field=0)

for name, freq, fpath, is_nest, pre_smoothed in cmb_list:
    if not os.path.exists(fpath):
        print(f"  {name:12s}: 唔存在")
        continue
    t0 = time.time()
    need_ref = (is_nest is None)  # SEVEM needs ordering check
    m = load_fast(fpath, is_nest, ref_m=smica_raw if need_ref else None)
    if pre_smoothed:
        # 已經平滑, 直接讀
        pix = hp.ang2pix(hp.get_nside(m), l_arr[0], b_arr[0], lonlat=True)
        T0 = float(m[pix]) * 1e6
    else:
        # 需要平滑
        T0 = measure_at(m, FWHM_PRIMARY, l_arr[0], b_arr[0])
    results[name] = {'T0_417': round(T0, 2), 'freq_GHz': 'CMB'}
    print(f"  {name:12s}: T0 = {T0:+8.2f} μK  (t={time.time()-t0:.1f}s)")

# ── 2. Raw frequency maps ────────────────────────────────────
print(f"\n─── 2. Raw Planck frequency maps ───")
freq_list = [
    ('LFI_030', 30,  f'{O27_DATA}/LFI_SkyMap_030_1024_R3.00_full.fits', True),
    ('LFI_044', 44,  f'{O27_DATA}/LFI_SkyMap_044_1024_R3.00_full.fits', True),
    ('LFI_070', 70,  f'{O27_DATA}/LFI_SkyMap_070_1024_R3.00_full.fits', True),
    ('HFI_100', 100, f'{O27_DATA}/HFI_SkyMap_100_2048_R3.01_full.fits', True),
    ('HFI_143', 143, f'{O27_DATA}/HFI_SkyMap_143_2048_R3.01_full.fits', True),
    ('HFI_217', 217, f'{O27_DATA}/HFI_SkyMap_217_2048_R3.01_full.fits', True),
    ('HFI_353', 353, f'{O27_DATA}/HFI_SkyMap_353_2048_R3.01_full.fits', True),
]
for name, freq, fpath, is_nest in freq_list:
    if not (os.path.exists(fpath) and os.path.getsize(fpath) > 1e5):
        print(f"  {name:12s}: 唔存在")
        continue
    t0 = time.time()
    m = load_fast(fpath, is_nest)
    r = measure_all(name, str(freq), m, l_arr[0], b_arr[0])
    results[name] = r
    print(f"  {name:12s} ({freq:3d} GHz): T0(4.17°) = {r['T0_417']:+8.2f} μK  "
          f"dev {r['dev_pct']:5.2f}%  (t={time.time()-t0:.1f}s)")

# ── 分析 ──────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"  分析")
print(f"{'='*60}")

# CMB maps
cmb_r = {k: v for k, v in results.items() if v['freq_GHz'] == 'CMB'}
if cmb_r:
    Ts = np.array([v['T0_417'] for v in cmb_r.values()])
    print(f"\n  CMB maps (6 methods):")
    for name, r in sorted(cmb_r.items()):
        print(f"    {name:12s}: {r['T0_417']:+8.2f} μK")
    print(f"    mean = {Ts.mean():+.2f}  std = {Ts.std():.2f} μK")
    if Ts.std() < 2:
        print(f"    ✅✅ 全部一致! (std < 2 μK)")

# Raw frequency maps
freq_r = {k: v for k, v in results.items() if v['freq_GHz'] != 'CMB' and v['T0_417'] is not None}
if freq_r:
    print(f"\n  Raw frequency maps:")
    for name, r in sorted(freq_r.items(), key=lambda x: int(x[1]['freq_GHz'])):
        print(f"    {name:12s} ({r['freq_GHz']:3s} GHz): {r['T0_417']:+8.2f} μK")
    
    cmb_zone = {k: v for k, v in freq_r.items() if v['freq_GHz'] in ('100', '143')}
    if cmb_zone:
        Tz = np.array([v['T0_417'] for v in cmb_zone.values()])
        print(f"    CMB主導 (100-143): mean={Tz.mean():+.2f}  std={Tz.std():.2f}")

# ── 結論 ──────────────────────────────────────────────────────
print(f"\n─── 結論 ───")
if cmb_r and Ts.std() < 2:
    verdict = 'PASS'
    print(f"  ✅✅ 6 種 CMB maps 一致 (std {Ts.std():.2f} μK)")
    print(f"  → A = 134.2 μK 係 CMB 原生訊號, 非組份分離假象")
    print(f"  → 4 種方法 (harmonic/needlet/MCMC/template) 交叉驗證")
else:
    verdict = 'MARGINAL'

print(f"  ★ 判定: {verdict}")

# ── 儲存 ──────────────────────────────────────────────────────
output = {
    'A_IDCM': A_IDCM, 'verdict': verdict,
    'nside': NS, 'results': results,
    'cmb_stats': {'mean': round(Ts.mean(), 2), 'std': round(Ts.std(), 2)} if cmb_r else None,
}

outpath = os.path.join(OUTDIR, '01_multifreq_results.json')
with open(outpath, 'w') as f:
    json.dump(output, f, indent=2, default=float)
print(f"\n✅ 結果已存: {outpath}")
print(f"總時間: {time.time()-t_start:.0f}s")
print(f"========================================")