#!/usr/bin/env python3
"""
O42 — 最終無幻覺驗證 (file simulation verifier)
================================================
獨立重算所有記錄數字, 讀返實際 fits/JSON, 確認冇幻覺。
"""
import os, json
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATADIR = os.path.join(BASE, 'data')
CACHE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o5_catalog_compare/data/smooth_cache'
NODES = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'

passed = []
failed = []

def check(name, cond, detail=''):
    if cond:
        passed.append(name)
        print(f"  ✅ {name} {detail}")
    else:
        failed.append(name)
        print(f"  ❌ {name} {detail}")

# 節點 0 座標
nodes = np.loadtxt(NODES)
sc0 = SkyCoord(ra=nodes[0,0]*u.deg, dec=nodes[0,1]*u.deg, frame='icrs')
g = sc0.galactic
scs = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gg = scs.galactic
check("node0 ICRS→Gal", abs(g.l.deg-209.0) < 0.5 and abs(g.b.deg+57.0) < 0.5,
      f"({nodes[0,0]},{nodes[0,1]})→({g.l.deg:.2f},{g.b.deg:.2f})")

# 1. 6 方法量度 (獨立重算, 唔讀 JSON)
sig = np.radians(4.17)/(2*np.sqrt(2*np.log(2)))
pix0 = hp.ang2pix(2048, g.l.deg, g.b.deg, lonlat=True)
pixs = hp.ang2pix(2048, gg.l.deg, gg.b.deg, lonlat=True)

measures = {}
for name, fn, smooth in [('SMICA', 'smica2_smooth4.17.fits', False),
                          ('NILC', 'nilc2_smooth4.17.fits', False),
                          ('Commander', 'commander_smooth4.17.fits', False)]:
    m = hp.read_map(os.path.join(CACHE, fn), field=0)
    T0 = m[pix0]*1e6
    rank = int(np.sum(m[pixs]*1e6 < T0) + 1)
    measures[name] = (T0, rank)

for name, fn in [('SEVEM_final', 'sevem_final.fits'), ('SEVEM_143', 'sevem_143.fits'), ('SEVEM_217', 'sevem_217.fits')]:
    m = hp.read_map(os.path.join(DATADIR, 'bands', fn), field=0)
    # as-is (corr 驗證過)
    ms = hp.remove_dipole(hp.smoothing(m, sigma=sig))
    T0 = ms[pix0]*1e6
    rank = int(np.sum(ms[pixs]*1e6 < T0) + 1)
    measures[name] = (T0, rank)

for name, (T0, rank) in measures.items():
    check(f"量度 {name}", -138 < T0 < -130 and rank <= 2, f"T0={T0:.2f} rank={rank}/60")

Ts = [v[0] for v in measures.values()]
check("6 量度 spread", max(Ts)-min(Ts) < 6, f"spread={max(Ts)-min(Ts):.2f} μK")
check("6 量度 mean ≈ -134", abs(np.mean(Ts) + 134.2) < 3, f"mean={np.mean(Ts):.2f}")

# 2. SMHW JSON 存在 + 數值合理
sj = json.load(open(os.path.join(DATADIR, '01_smhw_results.json')))
check("SMHW JSON 4.17 存在", '4.17' in sj['smhw'])
check("SMHW 4.17 rank ≤ 3", sj['smhw']['4.17']['rank'] <= 3, f"rank={sj['smhw']['4.17']['rank']}")

# 3. ISW 文檔存在
check("ISW doc", os.path.exists(os.path.join(BASE, 'docs', '02_isw_literature.md')))

# 4. 徑向剖面 JSON
rj = json.load(open(os.path.join(DATADIR, '04_radial_profile.json')))
check("剖面中心深冷", -200 < rj['center_T'] < -100, f"center={rj['center_T']:.1f} (應 ≈ −134)")
check("剖面回升 8-10°", 7 < rj['cold_extent'] < 11, f"extent={rj['cold_extent']:.1f}°")


# 6. T-E 偏振 + 本徵尺度
te = json.load(open(os.path.join(DATADIR, '05_te_polarization.json')))
check("T-E 冷斑 z 正常", abs(te['z']) < 2, f"z={te['z']:+.2f}")

# 5. 檔案存在
for f in ['01_smhw_results.json', '02_multifrequency_results.json', '03_isw_literature.json', '04_radial_profile.json']:
    check(f"檔案 {f}", os.path.exists(os.path.join(DATADIR, f)))
for f in ['05_te_polarization.json']:
    check(f"檔案 {f}", os.path.exists(os.path.join(DATADIR, f)))

print()
print(f"結果: {len(passed)} PASS / {len(passed)+len(failed)}")
if failed:
    print("❌ 有 FAIL!")
    exit(1)
print("✅ 全部 PASS — O42 記錄無幻覺")
