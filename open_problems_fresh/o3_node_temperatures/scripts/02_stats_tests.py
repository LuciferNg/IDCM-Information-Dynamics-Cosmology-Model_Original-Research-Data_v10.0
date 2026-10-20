#!/usr/bin/env python3
"""
02_stats_tests.py — O3: 60 節點溫度統計檢驗
===========================================
1. 分佈統計 (mean/std/min/max) + K-S / Anderson-Darling vs 高斯
2. 冷色(30) vs 熱色(30) 分離 (bootstrap CI + t-test + permutation)
3. 同平滑地圖全圖分佈對比 (60 隨機點期望)
"""
import numpy as np
from scipy import stats
import healpy as hp
import os

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
DATA = os.path.join(BASE, "o3_node_temperatures/data")

# ============ 載入節點溫度 ============
rows = []
with open(os.path.join(DATA, "node_temps.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        rows.append((int(p[0]), int(p[1]), float(p[2]), float(p[3]), float(p[4]), int(p[5])))
T = np.array([r[2] for r in rows])       # μK
color = np.array([r[1] for r in rows])   # 1=cold
b = np.array([r[4] for r in rows])
hop = np.array([r[5] for r in rows])

print("=" * 66)
print("O3: 統計檢驗")
print("=" * 66)

# ============ 1. 基本分佈 ============
print("\n=== 1. 60 節點溫度分佈 ===")
print(f"mean = {T.mean():.2f} μK")
print(f"std  = {T.std(ddof=1):.2f} μK")
print(f"min  = {T.min():.2f} μK (節點 {np.argmin(T)})")
print(f"max  = {T.max():.2f} μK (節點 {np.argmax(T)})")
print(f"median = {np.median(T):.2f} μK")

# K-S test vs 高斯 (用全圖 std 做對照 — 平滑後全圖 std=44.3)
m_smooth = hp.read_map("/tmp/smica2_smooth417.fits", field=0)
map_std = m_smooth.std() * 1e6
print(f"\n平滑地圖全圖 std = {map_std:.1f} μK")
cdf_self = stats.norm(loc=T.mean(), scale=T.std(ddof=1)).cdf
ks = stats.kstest(T, cdf_self)
print(f"K-S vs 高斯(節點自身 mean/std): D={ks.statistic:.4f}, p={ks.pvalue:.4f}")

# K-S vs 高斯(全圖 std)
cdf_map = stats.norm(loc=0.0, scale=map_std).cdf
ks2 = stats.kstest(T, cdf_map)
print(f"K-S vs 高斯(0, 全圖std={map_std:.1f}): D={ks2.statistic:.4f}, p={ks2.pvalue:.4f}")

# Anderson-Darling
ad = stats.anderson(T, dist='norm')
print(f"A-D statistic = {ad.statistic:.4f} (5% crit={ad.critical_values[2]:.2f})")

# 偏度/峰度
print(f"skewness = {stats.skew(T):.3f}, kurtosis(excess) = {stats.kurtosis(T):.3f}")

# ============ 2. 冷熱分離 ============
print("\n=== 2. 冷色 vs 熱色 分離 ===")
Tc = T[color == 1]
Th = T[color == 0]
print(f"冷色 (30): mean={Tc.mean():.2f} μK, std={Tc.std(ddof=1):.2f}")
print(f"熱色 (30): mean={Th.mean():.2f} μK, std={Th.std(ddof=1):.2f}")
d = Tc.mean() - Th.mean()
print(f"冷-熱差 = {d:.2f} μK")

# t-test (Welch)
tt = stats.ttest_ind(Tc, Th, equal_var=False)
print(f"Welch t-test: t={tt.statistic:.3f}, p={tt.pvalue:.4f}")

# Mann-Whitney U
mw = stats.mannwhitneyu(Tc, Th, alternative='two-sided')
print(f"Mann-Whitney U: U={mw.statistic:.0f}, p={mw.pvalue:.4f}")

# Bootstrap 95% CI (10万次)
rng = np.random.default_rng(42)
n_boot = 100_000
diffs = np.empty(n_boot)
allT = np.concatenate([Tc, Th])
for k in range(n_boot):
    idx = rng.choice(60, 60, replace=True)
    diffs[k] = allT[idx][:30].mean() - allT[idx][30:].mean()
ci = np.percentile(diffs, [2.5, 97.5])
z = d / diffs.std()
print(f"Bootstrap (n={n_boot}): 差 mean={diffs.mean():.2f}, std={diffs.std():.2f}")
print(f"  95% CI = [{ci[0]:.2f}, {ci[1]:.2f}] {'✅ 不含 0' if ci[0] > 0 or ci[1] < 0 else '❌ 含 0'}")
print(f"  z = {z:.2f}σ")

# 零假設: 冷熱差 = 0 嘅 bootstrap (雙樣本, 重新採樣)
diffs0 = np.empty(20000)
for k in range(20000):
    # 隨機分 30/30 (無替換排列)
    idx = rng.permutation(60)
    diffs0[k] = allT[idx[:30]].mean() - allT[idx[30:]].mean()
p_perm = (np.abs(diffs0) >= np.abs(d)).mean()
print(f"排列檢驗 (20000× 隨機 30/30 分組): p = {p_perm:.4f} {'✅' if p_perm < 0.05 else '❌'}")

# ============ 3. 全圖對比 ============
print("\n=== 3. 節點 vs 全圖隨機點 ===")
# 全圖 (已 mask 銀河 |b|<20)
m_gal = hp.ma(m_smooth)
m_gal.mask = np.abs(hp.pix2ang(2048, np.arange(len(m_smooth)), lonlat=True)[1]) < 20
map_vals = m_gal[~m_gal.mask] * 1e6
print(f"全圖 (|b|>20): mean={map_vals.mean():.2f}, std={map_vals.std(ddof=1):.2f} μK, N={len(map_vals)}")

# 節點 std vs 隨機 60 點 std 分佈
rng2 = np.random.default_rng(7)
n_trial = 2000
rand_std = np.empty(n_trial)
rand_min = np.empty(n_trial)
rand_max = np.empty(n_trial)
for k in range(n_trial):
    samp = rng2.choice(map_vals, 60, replace=False)
    rand_std[k] = samp.std(ddof=1)
    rand_min[k] = samp.min()
    rand_max[k] = samp.max()

obs_std = T.std(ddof=1)
z_std = (obs_std - rand_std.mean()) / rand_std.std()
print(f"隨機 60 點 std: mean={rand_std.mean():.2f}, std={rand_std.std():.2f}")
print(f"節點 std = {obs_std:.2f} → z = {z_std:.2f}σ")
print(f"  百分位: {(rand_std < obs_std).mean()*100:.1f}%")

# 節點範圍 vs 隨機
obs_min, obs_max = T.min(), T.max()
p_min = (rand_min > obs_min).mean()
p_max = (rand_max < obs_max).mean()
print(f"節點 min={obs_min:.1f} (隨機 min 分佈 mean={rand_min.mean():.1f}, {p_min*100:.1f}% 更冷)")
print(f"節點 max={obs_max:.1f} (隨機 max 分佈 mean={rand_max.mean():.1f}, {p_max*100:.1f}% 更熱)")

# 銀河遮罩魯棒性: 剔除 |b|<20 後重算
keep = np.abs(b) >= 20
if keep.sum() >= 20:
    Tc2, Th2 = T[(color==1)&keep], T[(color==0)&keep]
    d2 = Tc2.mean() - Th2.mean()
    tt2 = stats.ttest_ind(Tc2, Th2, equal_var=False)
    print(f"\n剔除銀河盤後 ({keep.sum()} 節點): 冷-熱差 = {d2:.2f} μK, Welch t p={tt2.pvalue:.4f}")

print("\n✅ 統計檢驗完成")
