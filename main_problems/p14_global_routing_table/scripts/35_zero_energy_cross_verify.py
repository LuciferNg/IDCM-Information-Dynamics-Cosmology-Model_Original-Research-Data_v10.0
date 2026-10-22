#!/usr/bin/env python3
"""
GRT-35: ΔE=0 節點預言複驗 — 3 地圖 × 多平滑尺度交叉驗證
================================================================
複驗 GRT-34: 12 個 ΔE=0 節點 (k=2 阻挫) 溫度 ≈ 0 μK

改進:
1. 3 張 CMB 地圖: SMICA / NILC / Commander (O2 已驗證讀法)
2. 多平滑尺度: 0.5° / 1.0° / 3.0° / 5.0° / 7.0°
3. 3 種統計: mean|T| 比 / 置換檢驗 / MWU
4. 共 3×5 = 15 個獨立測量 → 一致性判定
"""
import healpy as hp
import numpy as np
import math
import sys, os
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy import stats

sys.path.insert(0, ".")
from grt_common import (build_graph, compute_frustration_edges,
                        edge_threshold_from_histogram, load_colors,
                        load_nodes, ang_deg)

OUT = "../data"
os.makedirs(OUT, exist_ok=True)

LINES = []
def L(s=""):
    LINES.append(str(s))
    print(s)

L("=" * 84)
L("  GRT-35: ΔE=0 節點預言複驗 — 3 地圖 × 5 平滑尺度")
L("=" * 84)

# ============================================================
# 一、載入圖 + ΔE=0 節點
# ============================================================
nodes, vecs = load_nodes()
N = len(nodes)
thresh, dists = edge_threshold_from_histogram(vecs)
adj = build_graph(vecs, thresh)
colors = load_colors()
frust = compute_frustration_edges(adj, colors)

zero_nodes = []
for i in range(N):
    k = sum(1 for j in adj[i] if (min(i,j), max(i,j)) in frust)
    if k == 2:
        zero_nodes.append(i)
normal_nodes = [i for i in range(N) if i not in zero_nodes]

nodes_arr = np.array(nodes)
sc = SkyCoord(ra=nodes_arr[:, 0]*u.deg, dec=nodes_arr[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = gal.l.deg
b_deg = gal.b.deg

L(f"""
┌──────────────────────────────────────────────────────────────┐
│  ΔE=0 節點 (k=2): {len(zero_nodes)} 個                          │
│  其他節點: {len(normal_nodes)} 個                                 │
│  地圖: SMICA / NILC / Commander                              │
│  平滑: 0.5° / 1.0° / 3.0° / 5.0° / 7.0°                     │
│  → 3×5 = 15 個獨立測量                                       │
└──────────────────────────────────────────────────────────────┘
""")

# ============================================================
# 二、載入 3 張地圖
# ============================================================
L("━" * 84)
L("  一、載入 3 張地圖 (O2 已驗證讀法)")
L("━" * 84)

maps = {}
MAP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'planck_pr3')
m_sm = hp.read_map(os.path.join(MAP_DIR, 'smica2.fits'), field=0)
nside = hp.get_nside(m_sm)
maps['SMICA'] = m_sm

m_nilc = hp.read_map(os.path.join(MAP_DIR, 'nilc.fits'), field=0, nest=True)
maps['NILC'] = hp.reorder(m_nilc, n2r=True)

m_cmd = hp.read_map(os.path.join(MAP_DIR, 'commander.fits'), field=0, nest=True)
maps['Commander'] = hp.reorder(m_cmd, n2r=True)

for name, m in maps.items():
    L(f"  {name}: nside={hp.get_nside(m)}, std={m.std()*1e6:.1f} μK")

# ============================================================
# 三、多尺度掃描
# ============================================================
L("━" * 84)
L("  二、多尺度掃描 — 3 地圖 × 5 平滑")
L("━" * 84)

scales = [0.5, 1.0, 3.0, 5.0, 7.0]
results = {}

L(f"  {'地圖':<10} | {'平滑':>5} | {'ΔE=0 mean|T|':>13} | {'其他 mean|T|':>12} | {'比':>6} | {'MWU p':>7} | {'置換 p':>7} | {'狀態'}")
L(f"  {'-'*10} | {'-'*5} | {'-'*13} | {'-'*12} | {'-'*6} | {'-'*7} | {'-'*7} | {'-'*4}")

rng = np.random.default_rng(7)
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

        # MWU
        try:
            _, p_mwu = stats.mannwhitneyu(np.abs(T_zero), np.abs(T_norm), alternative='less')
        except Exception:
            p_mwu = 1.0

        # 置換檢驗
        n_trials = 5000
        cnt = 0
        for _ in range(n_trials):
            samp = rng.choice(T, size=len(zero_nodes), replace=False)
            if np.abs(samp).mean() <= mean_zero:
                cnt += 1
        p_perm = cnt / n_trials

        ok = "🟢" if (ratio < 0.85 and p_perm < 0.10) else ("🟡" if ratio < 0.95 else "🔴")
        L(f"  {mname:<10} | {fwhm:>4.1f}° | {mean_zero:>13.2f} | {mean_norm:>12.2f} | {ratio:>6.2f} | {p_mwu:>7.3f} | {p_perm:>7.3f} | {ok}")

        results[(mname, fwhm)] = {'mean_zero': mean_zero, 'mean_norm': mean_norm,
                                  'ratio': ratio, 'p_mwu': p_mwu, 'p_perm': p_perm}

# ============================================================
# 四、綜合分析
# ============================================================
L("━" * 84)
L("  三、綜合分析 — 15 個獨立測量")
L("━" * 84)

# 統計通過率
n_ratio_pass = sum(1 for r in results.values() if r['ratio'] < 0.85)
n_perm_pass = sum(1 for r in results.values() if r['p_perm'] < 0.10)
n_both = sum(1 for r in results.values() if r['ratio'] < 0.85 and r['p_perm'] < 0.10)
n_total = len(results)

L(f"  15 個測量統計:")
L(f"    比 < 0.85 (ΔE=0 細 15%+): {n_ratio_pass}/{n_total}")
L(f"    置換 p < 0.10: {n_perm_pass}/{n_total}")
L(f"    兩者同時通過: {n_both}/{n_total}")

# 按地圖
L(f"\n  按地圖:")
for mname in maps:
    sub = {k: v for k, v in results.items() if k[0] == mname}
    n_pass = sum(1 for v in sub.values() if v['ratio'] < 0.85 and v['p_perm'] < 0.10)
    mean_ratio = np.mean([v['ratio'] for v in sub.values()])
    L(f"    {mname}: {n_pass}/5 通過, mean ratio = {mean_ratio:.2f}")

# 按尺度
L(f"\n  按平滑尺度:")
for fwhm in scales:
    sub = {k: v for k, v in results.items() if k[1] == fwhm}
    n_pass = sum(1 for v in sub.values() if v['ratio'] < 0.85 and v['p_perm'] < 0.10)
    mean_ratio = np.mean([v['ratio'] for v in sub.values()])
    L(f"    {fwhm}°: {n_pass}/3 通過, mean ratio = {mean_ratio:.2f}")

# ============================================================
# 五、綜合判定
# ============================================================
L("━" * 84)
L("  四、綜合判定")
L("━" * 84)

# 判定標準: 
# 強: ≥12/15 通過 (80%)
# 中: ≥8/15 通過
# 弱: ≥4/15 通過
# 無: <4/15

if n_both >= 12:
    verdict = "🟢🟢 強確認 — 預言喺 3 地圖 × 多尺度都成立!"
elif n_both >= 8:
    verdict = "🟢 確認 — 大部分測量支持預言"
elif n_both >= 4:
    verdict = "🟡 部分支持 — 有傾向但唔一致"
else:
    verdict = "🔴 複驗失敗 — 預言唔穩定 (可能係平滑假象)"

L(f"""
  ══════════════════════════════════════════════════════════
  {verdict}
  ══════════════════════════════════════════════════════════

  最終判定數字:
  比 < 0.85: {n_ratio_pass}/{n_total}
  置換 p < 0.10: {n_perm_pass}/{n_total}
  兩者: {n_both}/{n_total}
""")

# 儲存
with open(os.path.join(OUT, "zero_energy_cross_verify.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(LINES) + "\n")
print(f"\n✅ 已寫入: ../data/zero_energy_cross_verify.txt")
