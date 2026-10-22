#!/usr/bin/env python3
"""
P14 層2 獨立審計 — 第四數據源 SEVEM (Planck PR3 官方第四分量分離法)
=================================================================
問: NILC 7.0° p=0.126 失敗位 — 係地圖特定定係大尺度稀釋嘅普遍限制?

方法: 完全照抄 scripts/35 流程 (節點選取/置換檢驗/判據), 只加 SEVEM:
  4 地圖 × 5 平滑 = 20 個獨立測量
  判據同原 script: ratio < 0.85 且 置換 p < 0.10 → 🟢
"""
import healpy as hp
import numpy as np
import math, sys, os
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grt_common import (build_graph, compute_frustration_edges,
                        load_nodes, load_colors, edge_threshold_from_histogram)

MAP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'planck_pr3')

# ---------- 1. 節點 + ΔE=0 (同 scripts/35) ----------
nodes, vecs = load_nodes()
N = len(nodes)
thresh, dists = edge_threshold_from_histogram(vecs)
adj = build_graph(vecs, thresh)
colors = load_colors()
frust = compute_frustration_edges(adj, colors)

zero_nodes = []
for i in range(N):
    k = sum(1 for j in adj[i] if (min(i, j), max(i, j)) in frust)
    if k == 2:
        zero_nodes.append(i)
normal_nodes = [i for i in range(N) if i not in zero_nodes]

nodes_arr = np.array(nodes)
sc = SkyCoord(ra=nodes_arr[:, 0]*u.deg, dec=nodes_arr[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = gal.l.deg
b_deg = gal.b.deg
print(f"ΔE=0 (k=2): {len(zero_nodes)} 個; 其他: {len(normal_nodes)} 個")

# ---------- 2. 讀 4 張地圖 ----------
maps = {}
m = hp.read_map(os.path.join(MAP_DIR, 'smica2.fits'), field=0)
nside = hp.get_nside(m)
maps['SMICA'] = m
m = hp.read_map(os.path.join(MAP_DIR, 'nilc.fits'), field=0, nest=True)
maps['NILC'] = hp.reorder(m, n2r=True)
m = hp.read_map(os.path.join(MAP_DIR, 'commander.fits'), field=0, nest=True)
maps['Commander'] = hp.reorder(m, n2r=True)
m = hp.read_map(os.path.join(MAP_DIR, 'sevem.fits'), field=0, nest=True)
maps['SEVEM'] = hp.reorder(m, n2r=True)
for name, mm in maps.items():
    print(f"  {name}: nside={hp.get_nside(mm)}, std={mm.std()*1e6:.1f} μK")

# ---------- 3. 多尺度掃描 (同 scripts/35 判據) ----------
scales = [0.5, 1.0, 3.0, 5.0, 7.0]
results = {}
rng = np.random.default_rng(7)   # 同原 script seed, 公平比較

print(f"\n  {'地圖':<10} | {'平滑':>5} | {'ΔE=0 mean|T|':>13} | {'其他 mean|T|':>12} | {'比':>6} | {'MWU p':>7} | {'置換 p':>7} | {'狀態'}")
print(f"  {'-'*10} | {'-'*5} | {'-'*13} | {'-'*12} | {'-'*6} | {'-'*7} | {'-'*7} | {'-'*4}")

for mname, m in maps.items():
    for fwhm in scales:
        sigma = np.radians(fwhm) / (2*np.sqrt(2*np.log(2)))
        m_s = hp.smoothing(m, sigma=sigma)
        m_f = hp.remove_dipole(m_s)
        pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
        T = m_f[pix] * 1e6

        T_zero = T[zero_nodes]
        T_norm = T[normal_nodes]
        mean_zero = np.abs(T_zero).mean()
        mean_norm = np.abs(T_norm).mean()
        ratio = mean_zero / mean_norm if mean_norm > 0 else float('inf')

        try:
            _, p_mwu = stats.mannwhitneyu(np.abs(T_zero), np.abs(T_norm), alternative='less')
        except Exception:
            p_mwu = 1.0

        n_trials = 5000
        cnt = 0
        for _ in range(n_trials):
            samp = rng.choice(T, size=len(zero_nodes), replace=False)
            if np.abs(samp).mean() <= mean_zero:
                cnt += 1
        p_perm = cnt / n_trials

        ok = "🟢" if (ratio < 0.85 and p_perm < 0.10) else ("🟡" if ratio < 0.95 else "🔴")
        print(f"  {mname:<10} | {fwhm:>4.1f}° | {mean_zero:>13.2f} | {mean_norm:>12.2f} | {ratio:>6.2f} | {p_mwu:>7.3f} | {p_perm:>7.3f} | {ok}")
        results[(mname, fwhm)] = {'mean_zero': mean_zero, 'mean_norm': mean_norm,
                                  'ratio': ratio, 'p_mwu': p_mwu, 'p_perm': p_perm}

# ---------- 4. 綜合 ----------
print("\n  ===== 綜合 (4 地圖 × 5 尺度 = 20) =====")
n_ratio_pass = sum(1 for r in results.values() if r['ratio'] < 0.85)
n_perm_pass = sum(1 for r in results.values() if r['p_perm'] < 0.10)
n_both = sum(1 for r in results.values() if r['ratio'] < 0.85 and r['p_perm'] < 0.10)
print(f"  ratio<0.85: {n_ratio_pass}/20; 置換 p<0.10: {n_perm_pass}/20; 兩者: {n_both}/20")

print("\n  ★ 關鍵比對 — 7.0° 四地圖:")
for mname in ['SMICA', 'NILC', 'Commander', 'SEVEM']:
    r = results[(mname, 7.0)]
    print(f"    {mname:10s} 7.0°: ratio={r['ratio']:.2f}, p_perm={r['p_perm']:.3f}  {'🟢 過' if r['p_perm'] < 0.10 and r['ratio'] < 0.85 else '🟡 未過'}")

sevem_all = [r for (m, _f), r in results.items() if m == 'SEVEM']
print(f"\n  SEVEM 5 尺度通過率: {sum(1 for r in sevem_all if r['ratio']<0.85 and r['p_perm']<0.10)}/5, mean ratio={np.mean([r['ratio'] for r in sevem_all]):.3f}")