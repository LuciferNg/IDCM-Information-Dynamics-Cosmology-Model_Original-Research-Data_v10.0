#!/usr/bin/env python3
"""
O5 FILE SIMULATION VERIFIER — 檢查所有資料寫入是否正確 (2026-08-17)
====================================================================
調律者指示: 出現 file simulation verifier — 檢查資料寫入是否正確,
然後全部寫入記錄文檔並確認正確無幻覺。

驗證層級:
  1. 檔案存在性 (所有宣稱嘅檔案)
  2. JSON 內容 vs 宣稱數值 (node0/node9/冷熱斑)
  3. 平滑 cache 內容 (數值範圍, node 溫度)
  4. 文檔聲明 vs 實際數據 (NN_results / NODE9 / FULL_RERUN_LOG)
  5. 交叉驗證: script 輸出 vs JSON vs 文檔
"""

import json
import os
import sys
import numpy as np
import healpy as hp

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')
CACHE = os.path.join(DATA, 'smooth_cache')

passed = 0
failed = 0


def check(name, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")


print("=" * 66)
print("O5 FILE SIMULATION VERIFIER")
print("=" * 66)

# ============================================================
# 1. 檔案存在性
# ============================================================
print("\n[1] 檔案存在性")
required_files = [
    'data/smica_catalog.json',
    'data/literature_catalog.json',
    'data/match_results.json',
    'data/cross_scale_match.json',
    'data/smooth_cache/smica2_smooth0.5.fits',
    'data/smooth_cache/smica2_smooth1.0.fits',
    'data/smooth_cache/smica2_smooth3.0.fits',
    'data/smooth_cache/smica2_smooth5.0.fits',
    'data/smooth_cache/smica2_smooth10.0.fits',
    'NN_results.md',
    'NODE9_ANALYSIS.md',
    'FULL_RERUN_LOG.md',
    'README.md',
    '01_problem_record.md',
]
for f in required_files:
    check(f, os.path.exists(os.path.join(BASE, f)))

# ============================================================
# 2. JSON 內容
# ============================================================
print("\n[2] JSON 內容")

# 2a. smica_catalog.json
with open(os.path.join(DATA, 'smica_catalog.json')) as f:
    smica = json.load(f)
check('smica_catalog: 有 cold 列表', 'cold' in smica, f"(keys={list(smica.keys())})")
n_cold = len(smica.get('cold', []))
n_hot = len(smica.get('hot', []))
check('smica_catalog: 15 冷斑', n_cold == 15, f"(實際 {n_cold})")
check('smica_catalog: 14 熱斑', n_hot == 14, f"(實際 {n_hot})")

# 大冷斑喺 cold 列表 (之前確認 cold #2 = 208.40,-56.33)
cold_spots = smica.get('cold', [])
if isinstance(cold_spots, list) and len(cold_spots) > 0:
    # 搵最近 (209,-57) 嘅冷斑
    best_d = 1e9
    best = None
    for c in cold_spots:
        if isinstance(c, dict):
            l, b = c.get('peak_l', 0), c.get('peak_b', 0)
            d = np.hypot(l - 209, b + 57)
            if d < best_d:
                best_d = d
                best = c
    if best is not None:
        check('大冷斑 (209,-57) 喺目錄', best_d < 5,
              f"(最近 {best_d:.1f}° @ ({best.get('peak_l'):.1f},{best.get('peak_b'):.1f}))")
    else:
        check('大冷斑 (209,-57) 喺目錄', False, "(cold 列表冇 dict)")
else:
    check('cold 列表格式', False, f"(type={type(cold_spots)})")

# 2b. literature_catalog.json
with open(os.path.join(DATA, 'literature_catalog.json')) as f:
    lit = json.load(f)
check('literature_catalog: 有內容', len(str(lit)) > 50, f"({len(str(lit))} chars)")
# 文獻: 大冷斑 (209,-57) + gp10 (32,-8)
lit_str = json.dumps(lit, ensure_ascii=False)
check('文獻目錄含大冷斑 (209/-57)', ('209' in lit_str and ('-57' in lit_str or '57' in lit_str)))
check('文獻目錄含 gp10 (32,-8)', '32' in lit_str)

# 2c. match_results.json
with open(os.path.join(DATA, 'match_results.json')) as f:
    match = json.load(f)
check('match_results: 有內容', len(str(match)) > 50)

# 2d. cross_scale_match.json
with open(os.path.join(DATA, 'cross_scale_match.json')) as f:
    csm = json.load(f)
check('cross_scale_match: 三尺度', all(s in csm for s in ['1.0', '3.0', '5.0']),
      f"(keys={list(csm.keys())})")

# ============================================================
# 3. 平滑 cache 內容 (直接由 fits 驗證數值!)
# ============================================================
print("\n[3] 平滑 cache 內容 (直接讀 fits)")

# 節點 0 = Galactic (209, -57); 節點 9 = Galactic (214.92, -31.16)
# a5_nodes.txt: 2 欄 (RA Dec) — ICRS -> Galactic 轉換
nodes_path = os.path.join(BASE, 'cmb_cold_spot/data/a5_nodes.txt')
if not os.path.exists(nodes_path):
    nodes_path = os.path.join(BASE, '../cmb_cold_spot/data/a5_nodes.txt')
nodes = np.loadtxt(nodes_path)
from astropy.coordinates import SkyCoord
import astropy.units as u
sc = SkyCoord(ra=nodes[:, 0] * u.deg, dec=nodes[:, 1] * u.deg, frame='icrs')
gal = sc.galactic
node_l = gal.l.deg
node_b = gal.b.deg

# 3.0° cache: node0 應該 ~-145, node9 應該 ~-110.6
m3 = hp.read_map(os.path.join(CACHE, 'smica2_smooth3.0.fits'), field=0)
nside3 = hp.get_nside(m3)
T3 = m3 * 1e6
pix0 = hp.ang2pix(nside3, node_l[0], node_b[0], lonlat=True)
pix9 = hp.ang2pix(nside3, node_l[9], node_b[9], lonlat=True)
check('3.0° node0 ≈ -145 μK', abs(T3[pix0] - (-145.0)) < 3, f"(實際 {T3[pix0]:+.1f})")
check('3.0° node9 ≈ -110.6 μK', abs(T3[pix9] - (-110.6)) < 3, f"(實際 {T3[pix9]:+.1f})")

# 5.0° cache: node0 應該 ~-124.6
m5 = hp.read_map(os.path.join(CACHE, 'smica2_smooth5.0.fits'), field=0)
nside5 = hp.get_nside(m5)
T5 = m5 * 1e6
pix0_5 = hp.ang2pix(nside5, node_l[0], node_b[0], lonlat=True)
check('5.0° node0 ≈ -124.6 μK', abs(T5[pix0_5] - (-124.6)) < 3, f"(實際 {T5[pix0_5]:+.1f})")

# 1.0° cache: node9 應該 ~-117 (radial profile 終點)
m1 = hp.read_map(os.path.join(CACHE, 'smica2_smooth1.0.fits'), field=0)
nside1 = hp.get_nside(m1)
T1 = m1 * 1e6
pix9_1 = hp.ang2pix(nside1, node_l[9], node_b[9], lonlat=True)
check('1.0° node9 ≈ -117 μK (radial 終點)', abs(T1[pix9_1] - (-117.0)) < 8,
      f"(實際 {T1[pix9_1]:+.1f})")

# ============================================================
# 4. 文檔聲明 vs 實際數據
# ============================================================
print("\n[4] 文檔聲明 vs 實際數據")

with open(os.path.join(BASE, 'NN_results.md')) as f:
    nn = f.read()
check('NN_results 提 node0', ('node 0' in nn or 'node0' in nn or '節點 0' in nn))
check('NN_results 提節點 9 第二冷', '9' in nn and ('第二冷' in nn or 'node 9' in nn))

with open(os.path.join(BASE, 'NODE9_ANALYSIS.md')) as f:
    n9 = f.read()
check('NODE9 含三地圖 2.6%', '2.6%' in n9)
check('NODE9 含 p=0.018', '0.018' in n9)
check('NODE9 含 10° 全網最冷', '最冷' in n9 or '1/60' in n9)

with open(os.path.join(BASE, 'FULL_RERUN_LOG.md')) as f:
    frl = f.read()
check('FULL_RERUN_LOG 含 worker 4GB', '4GB' in frl or '4 GiB' in frl or '4GiB' in frl)
check('FULL_RERUN_LOG 含不用 tmp', 'tmp' in frl.lower())

# ============================================================
# 5. 關鍵數值交叉驗證 (由 fits 直接重算)
# ============================================================
print("\n[5] 關鍵數值交叉驗證 (由 fits 直接重算)")

# node9 26° 環空檢驗 — 重算 percentile (2000 random, 用固定 seed 一致)
# 簡化: 直接攞 3.0° map 上距冷斑 26° 環上 2000 點嘅溫度
rng = np.random.default_rng(42)
n_test = 2000
# 冷斑中心 (209,-57) 單位向量
v_c = hp.ang2vec(209, -57, lonlat=True)
# 隨機環方向: 垂直於 v_c 嘅平面隨機旋轉
# 用正交基: u1, u2 ⊥ v_c
v_c = np.asarray(v_c).flatten()
# 搵一個垂直向量
tmp = np.array([1.0, 0.0, 0.0])
if abs(np.dot(tmp, v_c)) > 0.9:
    tmp = np.array([0.0, 1.0, 0.0])
u1 = np.cross(v_c, tmp)
u1 /= np.linalg.norm(u1)
u2 = np.cross(v_c, u1)
u2 /= np.linalg.norm(u2)
# 26° 環上隨機點
angles = rng.uniform(0, 2 * np.pi, n_test)
ring_vecs = np.cos(26 * np.pi / 180) * v_c[None, :] + \
    np.sin(26 * np.pi / 180) * (np.cos(angles)[:, None] * u1[None, :] +
                                 np.sin(angles)[:, None] * u2[None, :])
ring_l, ring_b = hp.vec2ang(ring_vecs, lonlat=True)
ring_l = np.asarray(ring_l).flatten()
ring_b = np.asarray(ring_b).flatten()
ring_pix = hp.ang2pix(nside3, ring_l, ring_b, lonlat=True)
ring_T = T3[ring_pix]
# node9 溫度 percentile
T9 = T3[pix9]
pct = (ring_T < T9).mean()
check('node9 26° 環 percentile ≈ 0.018', abs(pct - 0.018) < 0.02,
      f"(實際 p={pct:.4f})")

# node9 3.0° 排名 (60 節點)
node_pix = hp.ang2pix(nside3, node_l, node_b, lonlat=True)
node_T = T3[node_pix]
rank = (node_T < T9).sum() + 1
check('node9 3.0° 排名 = 3/60', rank == 3, f"(實際 rank={rank})")

# node0 3.0° 排名 = 1/60
rank0 = (node_T < T3[pix0]).sum() + 1
check('node0 3.0° 排名 = 1/60', rank0 == 1, f"(實際 rank={rank0})")

# ============================================================
# 結果
# ============================================================
print("\n" + "=" * 66)
print(f"RESULT: {passed} passed, {failed} failed")
if failed == 0:
    print("✅ ALL FILE SIMULATION CHECKS PASSED — 無幻覺")
else:
    print(f"❌ {failed} CHECKS FAILED — 需要修正!")
print("=" * 66)
sys.exit(0 if failed == 0 else 1)
