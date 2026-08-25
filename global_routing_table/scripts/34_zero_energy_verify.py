#!/usr/bin/env python3
"""
GRT-34: 可觀測預言驗證 — ΔE=0 節點溫度 ≈ 0 μK (SMICA 實測)
================================================================
驗證 GRT-33 預言: 12 個 ΔE=0 節點 (k=2 阻挫) 嘅 CMB 溫度應該 ≈ 0 μK
(相位正交: θ ≈ π/2 或 3π/2, cos θ ≈ 0)

方法 (沿用 22_smica_smoothed.py 已驗證流程):
1. 讀取 SMICA (/tmp/smica2.fits)
2. 4.17° FWHM 平滑 (冷斑尺度)
3. 減偶極
4. 60 節點抽溫度 (ICRS → 銀道)
5. 分組: ΔE=0 節點 (k=2) vs 其他節點
6. 統計檢驗: ΔE=0 組溫度是否顯著接近 0? |T| 是否顯著細?
"""
import healpy as hp
import numpy as np
import math
import sys, os
from collections import defaultdict, deque
from astropy.coordinates import SkyCoord
import astropy.units as u

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
L("  GRT-34: 可觀測預言驗證 — ΔE=0 節點溫度 ≈ 0 μK")
L("=" * 84)

# ============================================================
# 一、載入圖 + 搵 ΔE=0 節點
# ============================================================
nodes, vecs = load_nodes()
N = len(nodes)
thresh, dists = edge_threshold_from_histogram(vecs)
adj = build_graph(vecs, thresh)
colors = load_colors()
frust = compute_frustration_edges(adj, colors)

# ΔE=0 節點: 翻轉唔使能量 = k=2 阻挫邊 (2 阻挫 + 2 正常)
zero_nodes = []
for i in range(N):
    k = sum(1 for j in adj[i] if (min(i,j), max(i,j)) in frust)
    if k == 2:
        zero_nodes.append(i)

# k=1 節點 (普通): 翻轉要能量
normal_nodes = [i for i in range(N) if i not in zero_nodes]

L(f"""
┌──────────────────────────────────────────────────────────────┐
│  ΔE=0 節點 (k=2 阻挫, 零能量寫入): {len(zero_nodes)} 個                │
│  {sorted(zero_nodes)}                                      │
│                                                              │
│  預言 (GRT-33): 呢啲節點相位正交 → 溫度 ≈ 0 μK               │
│  對照組: 其他 {len(normal_nodes)} 節點 (|T| 應該較大)               │
└──────────────────────────────────────────────────────────────┘
""")

# ============================================================
# 二、SMICA 溫度提取 (沿用已驗證流程)
# ============================================================
L("━" * 84)
L("  一、SMICA 溫度提取 (4.17° 平滑 + 減偶極)")
L("━" * 84)

m = hp.read_map('/tmp/smica2.fits', field=0)
nside = hp.get_nside(m)

fwhm_deg = 4.17
fwhm_rad = np.radians(fwhm_deg)
sigma_rad = fwhm_rad / (2 * np.sqrt(2 * np.log(2)))
m_smooth = hp.smoothing(m, sigma=sigma_rad, verbose=False)
m_final = hp.remove_dipole(m_smooth)

# 節點抽溫
nodes_arr = np.array(nodes)
sc = SkyCoord(ra=nodes_arr[:, 0]*u.deg, dec=nodes_arr[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = gal.l.deg
b_deg = gal.b.deg
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)

T_all = m_final[pix] * 1e6  # μK

L(f"  SMICA nside={nside}, 平滑 {fwhm_deg}° FWHM")
L(f"  節點 0 (冷斑): T = {T_all[0]:.1f} μK (預期 ~-134)")
L(f"  全部 60 節點: mean={T_all.mean():.1f}, std={T_all.std():.1f} μK")
L(f"")

# ============================================================
# 三、分組統計
# ============================================================
L("━" * 84)
L("  二、分組統計 — ΔE=0 vs 其他")
L("━" * 84)

T_zero = T_all[zero_nodes]
T_norm = T_all[normal_nodes]

L(f"  {'組':<20} | {'N':>3} | {'mean T (μK)':>12} | {'std':>8} | {'mean |T|':>10} | {'median |T|':>11}")
L(f"  {'-'*20} | {'-'*3} | {'-'*12} | {'-'*8} | {'-'*10} | {'-'*11}")
L(f"  {'ΔE=0 (預言≈0)':<20} | {len(T_zero):>3} | {T_zero.mean():>12.2f} | {T_zero.std():>8.2f} | {np.abs(T_zero).mean():>10.2f} | {np.median(np.abs(T_zero)):>11.2f}")
L(f"  {'其他節點':<20} | {len(T_norm):>3} | {T_norm.mean():>12.2f} | {T_norm.std():>8.2f} | {np.abs(T_norm).mean():>10.2f} | {np.median(np.abs(T_norm)):>11.2f}")

# 逐節點列表
L(f"\n  ΔE=0 節點溫度 (預言 ≈ 0 μK):")
L(f"  {'節點':>4} | {'T (μK)':>9} | {'|T| (μK)':>9} | {'顏色':>4} | {'預言符合?'}")
L(f"  {'-'*4} | {'-'*9} | {'-'*9} | {'-'*4} | {'-'*10}")
for i in zero_nodes:
    c = "冷" if colors[i] == 1 else "熱"
    ok = "✅ |T|<15" if abs(T_all[i]) < 15 else "❌"
    L(f"  {i:>4} | {T_all[i]:>9.2f} | {abs(T_all[i]):>9.2f} | {c:>4} | {ok}")

# ============================================================
# 四、統計檢驗
# ============================================================
L("━" * 84)
L("  三、統計檢驗 — ΔE=0 組是否顯著接近 0?")
L("━" * 84)

from scipy import stats

# 檢驗 1: |T| 是否顯著細 (Mann-Whitney U, 單尾)
u_stat, p_mw = stats.mannwhitneyu(np.abs(T_zero), np.abs(T_norm), alternative='less')
L(f"  檢驗 1: Mann-Whitney U (|T| 零組 < 其他組):")
L(f"    U = {u_stat:.0f}, p = {p_mw:.4f} {'✅ 顯著' if p_mw < 0.05 else '❌ 唔顯著'}")

# 檢驗 2: 零組 mean |T| vs 全天空隨機期望
# 隨機期望: 60 個隨機點嘅 |T| (高斯場, σ=std)
sigma_sky = m_final.std() * 1e6
E_abs_random = sigma_sky * math.sqrt(2/math.pi)  # 高斯 |X| 期望
L(f"  檢驗 2: ΔE=0 組 mean|T| vs 隨機場期望:")
L(f"    全天空 σ = {sigma_sky:.1f} μK")
L(f"    高斯 |X| 期望 = σ√(2/π) = {E_abs_random:.1f} μK")
L(f"    ΔE=0 組 mean|T| = {np.abs(T_zero).mean():.1f} μK")
L(f"    → 比 = {np.abs(T_zero).mean()/E_abs_random:.2f} {'✅ <1 (細過隨機)' if np.abs(T_zero).mean() < E_abs_random else '❌'}")
L(f"")

# 檢驗 3: 零組同 0 嘅 t-test
t_stat, p_ttest = stats.ttest_1samp(T_zero, 0)
L(f"  檢驗 3: ΔE=0 組 T 對 0 嘅 t-test:")
L(f"    t = {t_stat:.3f}, p = {p_ttest:.4f} {'✅ 唔拒絕 T=0' if p_ttest > 0.05 else '❌ 拒絕'}")

# ============================================================
# 五、控制檢驗 — 隨機 12 點 vs ΔE=0
# ============================================================
L("━" * 84)
L("  四、控制檢驗 — 隨機 12 點分組")
L("━" * 84)

rng = np.random.default_rng(42)
n_trials = 10000
count_le = 0
obs_mean_abs = np.abs(T_zero).mean()
for _ in range(n_trials):
    samp = rng.choice(T_all, size=len(zero_nodes), replace=False)
    if np.abs(samp).mean() <= obs_mean_abs:
        count_le += 1
p_perm = count_le / n_trials

L(f"  置換檢驗 ({n_trials} 次, 隨機抽 {len(zero_nodes)} 節點):")
L(f"    觀測 mean|T| (ΔE=0 組) = {obs_mean_abs:.2f} μK")
L(f"    隨機抽樣 mean|T| ≤ 觀測值 嘅比例 = {p_perm:.4f}")
L(f"    → p = {p_perm:.4f} {'✅ 顯著細 (預言支持!)' if p_perm < 0.05 else '❌ 唔顯著'}")
L(f"")

# ============================================================
# 六、綜合結論
# ============================================================
L("━" * 84)
L("  五、綜合結論")
L("━" * 84)

# 判定
criteria = []
if np.abs(T_zero).mean() < E_abs_random:
    criteria.append(("|T| < 隨機場期望", True))
else:
    criteria.append(("|T| < 隨機場期望", False))
if p_perm < 0.05:
    criteria.append(("置換檢驗 p<0.05", True))
else:
    criteria.append(("置換檢驗 p<0.05", False))
if p_ttest > 0.05:
    criteria.append(("t-test 唔拒絕 T=0", True))
else:
    criteria.append(("t-test 唔拒絕 T=0", False))

n_pass = sum(1 for _, ok in criteria if ok)
L(f"  判據總結:")
for name, ok in criteria:
    L(f"    {'✅' if ok else '❌'} {name}")
L(f"  通過 {n_pass}/{len(criteria)}")

if n_pass >= 2:
    verdict = "🟢 預言支持 — ΔE=0 節點溫度確實傾向 ≈ 0 (零能量寫入位確認!)"
elif n_pass >= 1:
    verdict = "🟡 部分支持 — 有傾向但未夠強"
else:
    verdict = "🔴 預言失敗 — ΔE=0 節點溫度冇異常 (相位模型要修正)"
L(f"""
  ══════════════════════════════════════════════════════════
  {verdict}
  ══════════════════════════════════════════════════════════
""")

# 儲存
with open(os.path.join(OUT, "zero_energy_nodes_verification.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(LINES) + "\n")
print(f"\n✅ 已寫入: ../data/zero_energy_nodes_verification.txt")
