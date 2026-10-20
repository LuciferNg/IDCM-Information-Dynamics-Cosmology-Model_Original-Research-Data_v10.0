#!/usr/bin/env python3
"""
O7 開放問題 A 深入: 多尺度端點 vs connector 溫度梯度
============================================================
之前只用 2 個尺度 (5° 平滑 + 帶通) 方向相反 (p≈0.07)
而家有 10 個平滑尺度 cache (0.5°-10° FWHM), 做多尺度掃描

方法:
1. 每個尺度: 讀 smooth cache, 抽 60 節點溫度
2. 計每節點溫度梯度 |T_v - mean(T_neighbors)|
3. 比較 deg-1 (端點) vs deg-2 (connector) vs 非阻挫
4. 睇有冇尺度依賴結構
"""
import numpy as np, math, os
from collections import defaultdict, deque
from scipy.stats import ttest_ind, mannwhitneyu

DATA = "/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data"
CACHE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare/data/smooth_cache"

# ============ 1. 載入圖 ============
nodes = []
with open(f"{DATA}/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)

vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                   math.cos(math.radians(d))*math.sin(math.radians(r)),
                   math.sin(math.radians(d))] for r,d in nodes])

adj = defaultdict(set)
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j)
            adj[j].add(i)

# 阻挫子圖
frust_edges = set()
with open(f"{DATA}/frustration_edges.txt") as f:
    f.readline()
    for line in f:
        p = line.strip().split()
        u, v = int(p[0]), int(p[1])
        frust_edges.add((min(u, v), max(u, v)))

frust_adj = defaultdict(set)
for u, v in frust_edges:
    frust_adj[u].add(v); frust_adj[v].add(u)

deg1 = sorted([v for v in range(60) if v in frust_adj and len(frust_adj[v]) == 1])
deg2 = sorted([v for v in range(60) if v in frust_adj and len(frust_adj[v]) == 2])
non_frust = sorted([v for v in range(60) if v not in frust_adj])

print("=" * 75)
print("O7 開放問題 A 深入: 多尺度端點 vs connector 溫度梯度")
print("=" * 75)
print(f"端點 (deg-1): {len(deg1)}, 連接器 (deg-2): {len(deg2)}, 非阻挫: {len(non_frust)}")

# ============ 2. 座標轉換 (ICRS → Galactic) ============
try:
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
    gal = sc.galactic
    l_deg = gal.l.deg
    b_deg = gal.b.deg
    print("Astropy 座標轉換 OK")
except Exception as e:
    print(f"Astropy 失敗: {e}, 用近似")
    l_deg = nodes[:, 0]
    b_deg = nodes[:, 1]

def load_smooth_map(fname):
    m = hp.read_map(fname, field=0)
    # 減偶極
    m = hp.remove_dipole(m)
    return m

import healpy as hp

# ============ 3. 多尺度掃描 ============
scales = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
results = []

print(f"\n{'尺度':>6} {'端點梯度':>10} {'連接器梯度':>10} {'非阻挫梯度':>10} {'t p值':>8} {'MW p值':>8} {'端點-連接器差':>14}")
print(f"{'-'*72}")

for fwhm in scales:
    fname = f"{CACHE}/smica2_smooth{fwhm}.fits"
    if not os.path.exists(fname):
        print(f"  {fwhm:>5}°  檔案唔存在, 跳過")
        continue
    m = hp.read_map(fname, field=0)
    m = hp.remove_dipole(m)
    nside = hp.get_nside(m)
    pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
    T = m[pix]

    # 每節點梯度
    def grad(v):
        nbrs = list(adj[v])
        return abs(T[v] - np.mean(T[nbrs]))

    g1 = np.array([grad(v) for v in deg1]) * 1e6
    g2 = np.array([grad(v) for v in deg2]) * 1e6
    gnf = np.array([grad(v) for v in non_frust]) * 1e6

    t_stat, t_p = ttest_ind(g1, g2)
    u_stat, u_p = mannwhitneyu(g1, g2, alternative='two-sided')

    diff = np.mean(g1) - np.mean(g2)
    results.append({
        'fwhm': fwhm, 'g1': np.mean(g1), 'g2': np.mean(g2),
        'gnf': np.mean(gnf), 't_p': t_p, 'u_p': u_p, 'diff': diff
    })

    arrow = ">>>" if diff > 10 else ">" if diff > 0 else "<"
    sig = "🟡" if t_p < 0.05 else "  "
    print(f"  {fwhm:>4}° {np.mean(g1):>10.2f} {np.mean(g2):>10.2f} {np.mean(gnf):>10.2f} {t_p:>8.4f} {u_p:>8.4f} {diff:>+12.2f} {arrow} {sig}")

# ============ 4. 端點 vs 全部節點 (隨機對照) ============
print(f"\n{'='*75}")
print("📐 端點 vs 全部節點 (每尺度)")
print(f"{'='*75}")

rng = np.random.RandomState(42)
print(f"\n{'尺度':>6} {'端點':>10} {'全部':>10} {'隨機40':>10} {'百分位':>8}")
print(f"{'-'*50}")
for r in results:
    fwhm = r['fwhm']
    fname = f"{CACHE}/smica2_smooth{fwhm}.fits"
    m = hp.read_map(fname, field=0)
    m = hp.remove_dipole(m)
    nside = hp.get_nside(m)
    pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
    T = m[pix]
    def grad(v):
        nbrs = list(adj[v])
        return abs(T[v] - np.mean(T[nbrs]))
    g1 = np.array([grad(v) for v in deg1]) * 1e6
    gall = np.array([grad(v) for v in range(60)]) * 1e6
    # 隨機 40
    rand_means = []
    for _ in range(2000):
        idx = rng.choice(60, 40, replace=False)
        rand_means.append(np.mean([grad(v) for v in idx]) * 1e6)
    pct = np.mean([x <= np.mean(g1) for x in rand_means]) * 100
    print(f"  {fwhm:>4}° {np.mean(g1):>10.2f} {np.mean(gall):>10.2f} {np.mean(rand_means):>10.2f} {pct:>7.1f}%")

# ============ 5. 總結 + 建議 ============
print(f"\n{'='*75}")
print("📋 總結")
print(f"{'='*75}")

sig_any = [r for r in results if r['t_p'] < 0.05]
sig_direction = []
for r in results:
    if r['t_p'] < 0.05:
        direction = "端點>connector" if r['diff'] > 0 else "端點<connector"
        sig_direction.append((r['fwhm'], direction))

print(f"   顯著尺度 (p<0.05): {len(sig_any)}/{len(results)}")
for fwhm, d in sig_direction:
    print(f"     {fwhm}°: {d}")

if not sig_any:
    print(f"   → 冇任何尺度顯示端點梯度顯著大於 connector")
    print(f"   → 預測 3 (端點溫度梯度 > connector) 未獲得支持 🟡")
    print(f"   → 可能原因: 端點同 connector 嘅拓撲角色差異唔體現喺溫度梯度上")
    print(f"   → 或者: 5° 平滑以上嘅尺度太大, 需要更高分辨率")
else:
    print(f"   → 有顯著尺度, 睇方向一致性")

# 儲存結果
with open(f"{DATA}/o7_multiscale_gradient.txt", "w") as f:
    f.write("# O7 開放問題 A: 多尺度端點 vs connector 溫度梯度\n")
    f.write(f"# 尺度 FWHM 端點梯度μK 連接器梯度μK 非阻挫梯度μK t_p MW_p 差\n")
    for r in results:
        f.write(f"{r['fwhm']} {r['g1']:.2f} {r['g2']:.2f} {r['gnf']:.2f} {r['t_p']:.4f} {r['u_p']:.4f} {r['diff']:.2f}\n")
print(f"\n✅ 已存: {DATA}/o7_multiscale_gradient.txt")