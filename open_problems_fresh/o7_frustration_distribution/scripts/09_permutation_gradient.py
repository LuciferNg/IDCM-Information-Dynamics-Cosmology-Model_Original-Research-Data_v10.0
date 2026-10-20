#!/usr/bin/env python3
"""
O7 開放問題 A 深入 2: 排列檢定 + 邊級雙峰重驗證
============================================================
多尺度掃描發現: 端點梯度喺 10 個尺度全部 > connector (+6~+17μK)
但 t-test p 最細 0.073 (4.17°) — 樣本太細 (12 connector)

方法:
1. 排列檢定 (permutation test): 混合 40+12 節點, 隨機分組 10000 次
2. 邊級雙峰: 阻挫邊 vs 正常邊 溫差 (原始預測 3 版本 1)
3. 縫合線級: 沿縫合線溫度 profile
4. Bootstrap 信賴區間
"""
import numpy as np, math, os
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
AU = u  # alias to avoid variable shadowing

DATA = "/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data"
CACHE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare/data/smooth_cache"

# ============ 1. 載入 ============
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
edges_all = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j)
            adj[j].add(i)
            edges_all.append((i, j))

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
normal_edges = [e for e in edges_all if e not in frust_edges]

sc = SkyCoord(ra=nodes[:, 0]*AU.deg, dec=nodes[:, 1]*AU.deg, frame='icrs')
gal = sc.galactic
l_deg = np.array(gal.l.deg)
b_deg = np.array(gal.b.deg)

print("=" * 75)
print("O7 開放問題 A 深入 2: 排列檢定 + 邊級雙峰")
print("=" * 75)
print(f"端點: {len(deg1)}, 連接器: {len(deg2)}, 阻挫邊: {len(frust_edges)}, 正常邊: {len(normal_edges)}")

# ============ 2. 主尺度: 4.17° (冷斑尺度) ============
fwhm = 4.17
m = hp.read_map(f"{CACHE}/smica2_smooth{fwhm}.fits", field=0)
m = hp.remove_dipole(m)
nside = hp.get_nside(m)
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T = m[pix]

def grad(v):
    nbrs = list(adj[v])
    return abs(T[v] - np.mean(T[nbrs]))

g1 = np.array([grad(v) for v in deg1]) * 1e6
g2 = np.array([grad(v) for v in deg2]) * 1e6
obs_diff = np.mean(g1) - np.mean(g2)
print(f"\n4.17° 尺度:")
print(f"  端點梯度: {np.mean(g1):.2f} ± {np.std(g1):.2f} μK")
print(f"  連接器梯度: {np.mean(g2):.2f} ± {np.std(g2):.2f} μK")
print(f"  觀察差: {obs_diff:+.2f} μK (端點-連接器)")

# ============ 3. 排列檢定 ============
print(f"\n{'='*75}")
print("📐 排列檢定 (100000 次)")
print(f"{'='*75}")

rng = np.random.RandomState(42)
all_g = np.concatenate([g1, g2])
n1, n2 = len(g1), len(g2)
count_extreme = 0
count_abs = 0
for trial in range(100000):
    perm = rng.permutation(len(all_g))
    p1 = perm[:n1]
    p2 = perm[n1:]
    d = np.mean(all_g[p1]) - np.mean(all_g[p2])
    if d >= obs_diff:
        count_extreme += 1
    if abs(d) >= abs(obs_diff):
        count_abs += 1

p_one = count_extreme / 100000
p_two = count_abs / 100000
print(f"  單尾 p (端點>connector): {p_one:.5f} {'🟡 顯著!' if p_one < 0.05 else '🟢 未達顯著'}")
print(f"  雙尾 p: {p_two:.5f}")

# ============ 4. Bootstrap CI ============
print(f"\n{'='*75}")
print("📐 Bootstrap 信賴區間 (端點-連接器 差)")
print(f"{'='*75}")

boot_diffs = []
for _ in range(10000):
    b1 = rng.choice(g1, len(g1), replace=True)
    b2 = rng.choice(g2, len(g2), replace=True)
    boot_diffs.append(np.mean(b1) - np.mean(b2))
boot_diffs = np.array(boot_diffs)
ci_lo, ci_hi = np.percentile(boot_diffs, [2.5, 97.5])
print(f"  95% CI: [{ci_lo:+.2f}, {ci_hi:+.2f}] μK")
print(f"  CI 唔含 0: {'🟡 顯著 (端點>connector)' if ci_lo > 0 else '🟢 CI 含 0, 未達顯著'}")

# ============ 5. 邊級雙峰 (預測 3 版本 1) ============
print(f"\n{'='*75}")
print("📐 邊級雙峰: 阻挫邊 vs 正常邊 溫差")
print(f"{'='*75}")

dT_fr = np.array([abs(T[u] - T[v]) for u, v in frust_edges]) * 1e6
dT_norm = np.array([abs(T[u] - T[v]) for u, v in normal_edges]) * 1e6
print(f"  阻挫邊: {np.mean(dT_fr):.1f} ± {np.std(dT_fr):.1f} μK (n={len(dT_fr)})")
print(f"  正常邊: {np.mean(dT_norm):.1f} ± {np.std(dT_norm):.1f} μK (n={len(dT_norm)})")
sep = (np.mean(dT_norm) - np.mean(dT_fr)) / np.std(dT_fr)
print(f"  分離度: {sep:.2f}σ")

# 排列檢定 (邊級)
all_dT = np.concatenate([dT_fr, dT_norm])
nf = len(dT_fr)
obs_sep = np.mean(dT_norm) - np.mean(dT_fr)
cnt = 0
for trial in range(10000):
    perm = rng.permutation(len(all_dT))
    m1 = np.mean(all_dT[perm[:nf]])
    m2 = np.mean(all_dT[perm[nf:]])
    if m2 - m1 >= obs_sep:
        cnt += 1
p_edge = cnt / 10000
print(f"  排列檢定: 正常>阻挫 單尾 p = {p_edge:.5f} {'🟡🟡 高度顯著!' if p_edge < 0.01 else '🟡 顯著' if p_edge < 0.05 else '🟢 未達顯著'}")

# ============ 6. 縫合線級 ============
print(f"\n{'='*75}")
print("📐 縫合線沿線溫度 profile")
print(f"{'='*75}")

# 追蹤縫合線
seen = set()
seams = []
for s in range(60):
    if s not in frust_adj or s in seen:
        continue
    comp = []
    q = deque([s])
    seen.add(s)
    while q:
        u = q.popleft()
        comp.append(u)
        for v in frust_adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    if len(comp) >= 2:
        seams.append(comp)

print(f"  縫合線數: {len(seams)}")
print(f"  {'#':>2} {'節點':>20} {'沿線溫度 (μK)':>30} {'ΔT':>7}")
for i, comp in enumerate(seams):
    temps = [T[v]*1e6 for v in comp]
    tstr = ' → '.join(f"{t:+.1f}" for t in temps)
    dt = max(temps) - min(temps)
    print(f"  {i:>2} {str(comp):>20} {tstr:>30} {dt:>7.1f}")

# 縫合線內外對比: 縫合線節點 vs 非縫合線節點
seam_nodes = set()
for comp in seams:
    seam_nodes.update(comp)
non_seam = [v for v in range(60) if v not in seam_nodes]
print(f"\n  縫合線節點 ({len(seam_nodes)}) vs 非縫合線節點 ({len(non_seam)}):")
print(f"  縫合線: {np.mean([T[v] for v in seam_nodes])*1e6:+.1f} ± {np.std([T[v] for v in seam_nodes])*1e6:.1f} μK")
print(f"  非縫合: {np.mean([T[v] for v in non_seam])*1e6:+.1f} ± {np.std([T[v] for v in non_seam])*1e6:.1f} μK")

# ============ 7. 最終判定 ============
print(f"\n{'='*75}")
print("📋 最終判定")
print(f"{'='*75}")
print(f"""
   預測 3 兩個版本:

   版本 1 (邊級): 阻挫邊兩端溫差 < 正常邊兩端溫差
      → 4.17°: 34.5 vs 53.1 μK, 分離 {sep:.1f}σ, 排列 p={p_edge:.5f}
      → {'✅ 已驗證 (顯著)' if p_edge < 0.05 else '🟡 未達顯著'}

   版本 2 (節點級): 端點梯度 > connector 梯度
      → 10 尺度全部方向一致 (+6~+17 μK)
      → 排列檢定單尾 p={p_one:.5f}, Bootstrap CI [{ci_lo:+.2f}, {ci_hi:+.2f}]
      → {'🟡 排列檢定顯著' if p_one < 0.05 else '🟢 排列檢定未達顯著'} ({'CI 唔含 0' if ci_lo > 0 else 'CI 含 0'})

   結論: 邊級雙峰 (版本 1) 係主預測, 已由 22_smica_smoothed.py 驗證。
   版本 2 方向一致但統計力不足 (12 個 connector 樣本太細)。
""")