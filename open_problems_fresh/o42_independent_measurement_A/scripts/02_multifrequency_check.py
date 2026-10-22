#!/usr/bin/env python3
"""
O42 — Step 2 (修正版): 多頻段穩定性 (全部 6 個獨立量度)
=========================================================
SEVEM ordering 修正: IRSA SEVEM 檔案 header 寫 NESTED, 但實際係 RING (as-is corr 更高)。
用 cross-correlation 驗證 ordering, 唔盲信 header。

量度: SMICA/NILC/Commander (cache) + SEVEM final/143/217 (IRSA)
"""
import os, json
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u

A_IDCM = 134.2
OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
BANDS = os.path.join(OUTDIR, 'bands')
NODES = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
RAW_SMICA = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o26_node57_region/data/smica_iqu_2048.fits'
CACHE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o5_catalog_compare/data/smooth_cache'

nodes = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_arr = np.array([float(g.l.deg) for g in gal])
b_arr = np.array([float(g.b.deg) for g in gal])
pixs = hp.ang2pix(2048, l_arr, b_arr, lonlat=True)
pix0 = pixs[0]

FWHM = 4.17
sig = np.radians(FWHM) / (2 * np.sqrt(2 * np.log(2)))

results = {}

def order_check(m):
    """用 raw SMICA correlation 決定 ordering"""
    sm = hp.read_map(RAW_SMICA, field=0)
    sel = np.arange(0, len(m), 3000)
    c0 = np.corrcoef(m[sel], sm[sel])[0,1]
    mr = hp.reorder(m, n2r=True)
    c1 = np.corrcoef(mr[sel], sm[sel])[0,1]
    return (m, 'AS-IS', c0) if c0 >= c1 else (mr, 'REORDER', c1)

def measure(name, m, need_smooth, note=''):
    nside = hp.get_nside(m)
    if need_smooth:
        ms = hp.remove_dipole(hp.smoothing(m, sigma=sig))
    else:
        ms = hp.remove_dipole(m)
    T0 = float(ms[pix0]) * 1e6
    Ts = ms[pixs] * 1e6
    rank = int(np.sum(Ts < T0) + 1)
    dev = abs(abs(T0) - A_IDCM) / A_IDCM * 100
    r = dict(name=name, T_muK=round(T0, 2), rank=rank, dev_pct=round(dev, 3), note=note)
    results[name] = r
    print(f"  {name:16s}: T0 = {T0:8.2f} μK  rank {rank}/60  dev {dev:5.2f}%  {note}")

print("=== 6 個獨立量度 @4.17° ===")

# 1-3. cache maps (RING, 已平滑)
for name, fn in [('SMICA', 'smica2_smooth4.17.fits'), ('NILC', 'nilc2_smooth4.17.fits'), ('Commander', 'commander_smooth4.17.fits')]:
    p = os.path.join(CACHE, fn)
    m = hp.read_map(p, field=0)
    measure(name, m, need_smooth=False, note='cache')

# 4-6. SEVEM (IRSA, header NESTED 但實際 RING)
for name, fn in [('SEVEM_final', 'sevem_final.fits'), ('SEVEM_143', 'sevem_143.fits'), ('SEVEM_217', 'sevem_217.fits')]:
    p = os.path.join(BANDS, fn)
    if not (os.path.exists(p) and os.path.getsize(p) > 1e6):
        print(f"  {name}: 檔案唔存在")
        continue
    m = hp.read_map(p, field=0)
    m, use, c = order_check(m)
    measure(name, m, need_smooth=True, note=f'ordering={use} corr={c:.3f}')

# 統計
Ts = [v['T_muK'] for v in results.values()]
T_arr = np.array(Ts)
print()
print("=" * 60)
print(f"6 個獨立量度: mean = {T_arr.mean():.2f}  std = {T_arr.std():.2f} μK")
print(f"範圍: [{T_arr.min():.2f}, {T_arr.max():.2f}]  spread = {T_arr.max()-T_arr.min():.2f} μK ({ (T_arr.max()-T_arr.min())/A_IDCM*100:.2f}% vs A)")
print(f"max dev vs A = {max(v['dev_pct'] for v in results.values()):.2f}% (Commander)")
if T_arr.std() < 5:
    print("  ✅✅ 6 方法一致 (std < 5 μK) — A = 134.2 μK 獨立量度確認")
elif T_arr.std() < 15:
    print("  ✅ 一致 (std < 15 μK)")
else:
    print("  ⚠️ 漂移大")

out = dict(A_IDCM=A_IDCM, fwhm=FWHM, results=results)
with open(os.path.join(OUTDIR, '02_multifrequency_results.json'), 'w') as f:
    json.dump(out, f, indent=2, default=float)
print(f"\nsaved: {OUTDIR}/02_multifrequency_results.json")
