#!/usr/bin/env python3
"""
03_extreme_test.py — O3: 節點極端值 vs 隨機天空位置
====================================================
1. 最冷/最熱節點排名 (全 60 節點)
2. 1000+ 組隨機 60 點: min/max/冷熱差 分佈對比
3. 節點極端性: 係咪比隨機更極端?
4. 冷色著色與溫度符號匹配率 (binomial)
"""
import numpy as np
from scipy import stats
import healpy as hp
import os

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
DATA = os.path.join(BASE, "o3_node_temperatures/data")

# ============ 載入 ============
rows = []
with open(os.path.join(DATA, "node_temps.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        rows.append((int(p[0]), int(p[1]), float(p[2]), float(p[3]), float(p[4]), int(p[5])))
T = np.array([r[2] for r in rows])
color = np.array([r[1] for r in rows])
l_deg = np.array([r[3] for r in rows])
b_deg = np.array([r[4] for r in rows])

print("=" * 66)
print("O3: 節點極端值 vs 隨機天空位置")
print("=" * 66)

# ============ 1. 完整 ranking ============
print("\n=== 1. 節點溫度排名 (全 60) ===")
order = np.argsort(T)
print("最冷 10:")
for i in order[:10]:
    c = "冷" if color[i] == 1 else "熱"
    flag = "✅" if (color[i] == 1) == (T[i] < 0) else "⚠️"
    print(f"  #{i}: {T[i]:+8.2f} μK  色={c} {flag}")
print("最熱 10:")
for i in order[-10:][::-1]:
    c = "冷" if color[i] == 1 else "熱"
    flag = "✅" if (color[i] == 0) == (T[i] > 0) else "⚠️"
    print(f"  #{i}: {T[i]:+8.2f} μK  色={c} {flag}")

# ============ 2. 著色-溫度符號匹配 ============
print("\n=== 2. 著色 vs 溫度符號 ===")
match = ((color == 1) & (T < 0)) | ((color == 0) & (T > 0))
print(f"匹配: {match.sum()}/60 = {match.sum()/60*100:.1f}%")
# 去除接近零嘅節點
nz = np.abs(T) > 10
match_nz = match & nz
print(f"匹配 (|T|>10μK, {nz.sum()} 節點): {match_nz.sum()}/{nz.sum()} = {match_nz.sum()/nz.sum()*100:.1f}%")
p_binom = stats.binomtest(match.sum(), 60, 0.5).pvalue
print(f"Binomial p = {p_binom:.4f}")

# ============ 3. 隨機對照 (1000 組) ============
print("\n=== 3. 隨機 60 點對照 (1000 組) ===")
m_smooth = hp.read_map("/tmp/smica2_smooth417.fits", field=0)
nside = 2048
theta, phi = hp.pix2ang(nside, np.arange(len(m_smooth)), lonlat=True)
gal_mask = np.abs(phi) < 20  # |b|<20 masked (phi = latitude in lonlat)
pix_ok = np.where(~gal_mask)[0]
map_vals = m_smooth[pix_ok] * 1e6
print(f"可抽樣像素 (|b|>20): {len(pix_ok)}")

rng = np.random.default_rng(123)
N = 2000
rand_min = np.empty(N)
rand_max = np.empty(N)
rand_std = np.empty(N)
rand_coldhot = np.empty(N)  # 隨機分 30/30 嘅差
for k in range(N):
    idx = rng.choice(len(pix_ok), 60, replace=False)
    samp = map_vals[idx]
    rand_min[k] = samp.min()
    rand_max[k] = samp.max()
    rand_std[k] = samp.std(ddof=1)
    perm = rng.permutation(60)
    rand_coldhot[k] = samp[perm[:30]].mean() - samp[perm[30:]].mean()

# 最冷節點 vs 隨機最冷
obs_min = T.min()
p_colder = (rand_min > obs_min).mean()
z_min = (obs_min - rand_min.mean()) / rand_min.std()
print(f"\n最冷節點: {obs_min:.2f} μK (節點 {np.argmin(T)})")
print(f"隨機 60 點最冷: mean={rand_min.mean():.2f}, std={rand_min.std():.2f}")
print(f"  更冷比例: {p_colder*100:.1f}%  z={z_min:.2f}σ")

# 最熱節點 vs 隨機最熱
obs_max = T.max()
p_hotter = (rand_max < obs_max).mean()
z_max = (obs_max - rand_max.mean()) / rand_max.std()
print(f"\n最熱節點: {obs_max:.2f} μK (節點 {np.argmax(T)})")
print(f"隨機 60 點最熱: mean={rand_max.mean():.2f}, std={rand_max.std():.2f}")
print(f"  更熱比例: {p_hotter*100:.1f}%  z={z_max:.2f}σ")

# 冷熱差 vs 隨機
obs_d = T[color == 1].mean() - T[color == 0].mean()
p_d = (np.abs(rand_coldhot) >= np.abs(obs_d)).mean()
print(f"\n冷熱差: {obs_d:.2f} μK (隨機 30/30 差: mean={rand_coldhot.mean():.2f}, std={rand_coldhot.std():.2f})")
print(f"  |差| ≥ 觀測值比例: {p_d*100:.1f}%  z={(abs(obs_d)-np.abs(rand_coldhot).mean())/rand_coldhot.std():.2f}σ")

# std 對比
obs_std = T.std(ddof=1)
p_std = (rand_std > obs_std).mean()
print(f"\n節點 std: {obs_std:.2f} vs 隨機 std 分佈 mean={rand_std.mean():.2f}")
print(f"  更大比例: {p_std*100:.1f}%")

# ============ 4. 雙極端同時出現 (min AND max 都極端) ============
print("\n=== 4. 雙極端聯合檢驗 ===")
joint = (rand_min > obs_min) & (rand_max < obs_max)
print(f"隨機組同時更冷 AND 更熱: {joint.mean()*100:.1f}% (期望 <5% 先有意義)")

# ============ 5. 排名檢驗: 冷色是否傾向低溫端 ============
print("\n=== 5. 冷色著色 vs 低溫端 (rank sum) ===")
from scipy.stats import ranksums
Tc = T[color == 1]
Th = T[color == 0]
rs = ranksums(Tc, Th)
print(f"冷色 median={np.median(Tc):.2f}, 熱色 median={np.median(Th):.2f}")
print(f"rank-sum p = {rs.pvalue:.4f}")

# 前 20 冷嘅有幾多係冷色?
n_top = 20
top_cold = color[order[:n_top]]
print(f"最冷 {n_top} 節點中冷色: {top_cold.sum()}/{n_top}")
p_hyper = stats.hypergeom.sf(top_cold.sum()-1, 60, 30, n_top)
print(f"hypergeometric p = {p_hyper:.4f}")

n_top_hot = 20
top_hot = color[order[-n_top_hot:]]
print(f"最熱 {n_top_hot} 節點中熱色: {(~top_hot.astype(bool)).sum()}/{n_top_hot}")
p_hyper2 = stats.hypergeom.sf((~top_hot.astype(bool)).sum()-1, 60, 30, n_top_hot)
print(f"hypergeometric p = {p_hyper2:.4f}")

print("\n✅ 極端檢驗完成")
