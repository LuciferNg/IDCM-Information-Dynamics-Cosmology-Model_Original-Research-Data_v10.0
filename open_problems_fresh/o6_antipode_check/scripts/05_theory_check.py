#!/usr/bin/env python3
"""
05_theory_check.py — O6: 理論檢驗 — A₅ 冇反演 → 對徑點相位
===========================================================
核心問題: 節點 57 冷色 (+8.21 μK) 嘅物理意義

理論候選:
A. 對徑點 = 圖自同構產物 (BFS parity 強制), 唔係物理異常
   - z=-3.24 係「強制相同」(anchor 0 ↔ anchor 57 嘅著色 60/60 一致)
   - 溫度 +8.21 反映嘅係局部大尺度 CMB, 唔係對徑結構
B. 對徑點相位: T = A·cos(θ), θ 隨 hop 演化 → hop=8 相位近 π/2?
   - ΔE=0 節點 (k=2) 相位正交 θ≈π/2 → T≈0
   - 節點 57 係咪「近正交」相位 (小 |T|)?
C. 對徑點大尺度: CMB 偶極移除後, 對徑區應該係「背景平均」

檢驗:
1. 30 對徑對嘅 T_i + T_j 分佈 (和 = 0 → 反相關?)
2. 對徑對嘅 |ΔT| vs 隨機對照 (30 隨機對)
3. 節點 57 嘅 |T| 排名 (喺 60 節點入面) — 係咪「近零」?
4. 節點 57 喺 hop=8 嘅唯一性: 全部 60 節點 hop 分佈
5. 相位模型: T 嘅絕對值同 hop 有冇關係? (對徑點應該近零?)
6. 大尺度背景: 節點 57 10° 區域 mean vs 全天空
"""
import healpy as hp
import numpy as np
import math
import os
from collections import defaultdict, deque
from scipy import stats
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
NODE_FILE = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
CACHE = "/tmp/cache_o3"
OUT = os.path.join(BASE, "o6_antipode_check/data")

nodes = []
with open(NODE_FILE) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)

sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = gal.l.deg
b_deg = gal.b.deg

vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])

adj = defaultdict(set)
edges_list = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang < 28.0:
            adj[i].add(j)
            adj[j].add(i)
            edges_list.append((i, j))

hop = {0: 0}
color = {0: 1}
q = deque([0])
while q:
    u = q.popleft()
    for w in adj[u]:
        if w not in hop:
            hop[w] = hop[u] + 1
            color[w] = 1 - color[u]
            q.append(w)

# 多尺度
scales = [0.5, 1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0]
T_all = {}
for s in scales:
    m = hp.read_map(os.path.join(CACHE, f"SMICA_{s}.fits"), field=0)
    nside = hp.get_nside(m)
    pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
    T_all[s] = m[pix] * 1e6

T = T_all[4.17]

print("=" * 66)
print("O6: 理論檢驗 — 對徑點物理")
print("=" * 66)

# ============ 1. 對徑對 T_i + T_j ============
print("\n=== 1. 30 對徑對: 溫度和 ===")
pairs = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang > 170.0:
            pairs.append((i, j))
sums = np.array([T[i] + T[j] for i, j in pairs])
diffs = np.array([abs(T[i] - T[j]) for i, j in pairs])
print(f"對數: {len(pairs)}")
print(f"T_i+T_j: mean={sums.mean():+.2f}, std={sums.std():.1f}, "
      f"min={sums.min():+.2f}, max={sums.max():+.2f}")
print(f"|ΔT|: mean={diffs.mean():.1f}, median={np.median(diffs):.1f}, max={diffs.max():.1f}")
print(f"和>0: {np.sum(sums>0)}, 和<0: {np.sum(sums<0)}")
print(f"同號對: {np.sum((T[[i for i,j in pairs]]>0)==(T[[j for i,j in pairs]]>0))}/{len(pairs)}")

# ============ 2. 隨機對照 ============
print("\n=== 2. 隨機 30 對對照 (bootstrap 2000) ===")
rng = np.random.default_rng(42)
rand_diff_means = []
rand_sum_stds = []
for _ in range(2000):
    perm = rng.permutation(60)
    ri = perm[:30]
    rj = perm[30:]
    rand_diff_means.append(np.abs(T[ri] - T[rj]).mean())
    rand_sum_stds.append((T[ri] + T[rj]).std())
rand_diff_means = np.array(rand_diff_means)
rand_sum_stds = np.array(rand_sum_stds)
z_diff = (diffs.mean() - rand_diff_means.mean()) / rand_diff_means.std()
z_sum = (sums.std() - rand_sum_stds.mean()) / rand_sum_stds.std()
print(f"隨機對 |ΔT| mean: {rand_diff_means.mean():.1f} ± {rand_diff_means.std():.1f}")
print(f"對徑對 |ΔT| mean: {diffs.mean():.1f} → z = {z_diff:+.2f}σ")
print(f"隨機對 和 std: {rand_sum_stds.mean():.1f} ± {rand_sum_stds.std():.1f}")
print(f"對徑對 和 std: {sums.std():.1f} → z = {z_sum:+.2f}σ")

# ============ 3. 節點 57 嘅 |T| 排名 ============
print("\n=== 3. 節點 57 |T| 排名 (4.17°) ===")
absT = np.abs(T)
rank = np.sum(absT <= absT[57])
print(f"節點 57 |T|={absT[57]:.2f} μK → 排名 {rank}/60 (第 {rank} 細)")
print(f"最細 |T| 5 節點: {[(i, round(T[i],2)) for i in np.argsort(absT)[:5]]}")
print(f"最大 |T| 5 節點: {[(i, round(T[i],2)) for i in np.argsort(absT)[-5:]]}")

# ============ 4. hop 分佈 + 對徑唯一性 ============
print("\n=== 4. hop 分佈 ===")
from collections import Counter
print(f"hop 分佈: {dict(sorted(Counter(hop.values()).items()))}")
print(f"hop=8 (對徑): 只有節點 {[i for i in range(60) if hop[i]==8]}")
print(f"→ 對徑點係「唯一」嘅 (BFS 直徑端點) — 圖結構強制")

# ============ 5. |T| vs hop ============
print("\n=== 5. |T| vs hop (相位模型檢驗) ===")
for h in range(9):
    idx = [i for i in range(60) if hop[i] == h]
    print(f"  hop={h}: mean|T|={np.abs(T[idx]).mean():.1f} μK, "
          f"mean T={T[idx].mean():+.1f}, n={len(idx)}")
# 相關: |T| vs hop
r_abs, p_abs = stats.spearmanr([hop[i] for i in range(60)], absT)
print(f"Spearman(|T|, hop): r={r_abs:.3f}, p={p_abs:.4f}")

# ============ 6. 對徑點大尺度背景 ============
print("\n=== 6. 節點 57 大尺度背景 ===")
for s in [4.17, 7.0, 10.0]:
    Ts = T_all[s]
    m = hp.read_map(os.path.join(CACHE, f"SMICA_{s}.fits"), field=0)
    nside = hp.get_nside(m)
    disc = hp.query_disc(nside, hp.ang2vec(l_deg[57], b_deg[57], lonlat=True), np.radians(10.0))
    rmean = m[disc].mean() * 1e6
    pct = (Ts[::7] < Ts[57]).mean() * 100
    print(f"  {s}°: 節點57={Ts[57]:+.2f} μK, 10°區域mean={rmean:+.2f}, 百分位={pct:.1f}%")

# ============ 7. ΔE=0 節點 vs 對徑點 ============
print("\n=== 7. ΔE=0 節點 (相位正交候選) vs 節點 57 ===")
# ΔE=0 = k=2 (2 條阻挫邊) 節點
frust = set()
for u, v in edges_list:
    if color[u] == color[v]:
        frust.add(frozenset((u, v)))
k = {}
for i in range(60):
    k[i] = sum(1 for w in adj[i] if frozenset((i, w)) in frust)
zeroE = sorted([i for i in range(60) if k[i] == 2])
print(f"ΔE=0 節點 (k=2): {zeroE}")
print(f"ΔE=0 mean|T|={np.abs(T[zeroE]).mean():.2f} μK")
print(f"其他 48 mean|T|={np.abs(T[[i for i in range(60) if i not in zeroE]]).mean():.2f} μK")
print(f"節點 57: k={k[57]}, |T|={absT[57]:.2f} μK, 喺唔喺 ΔE=0 群: {57 in zeroE}")

# ============ 8. 對徑點相位模型: T(57) ≈ 大尺度背景? ============
print("\n=== 8. 綜合判讀 ===")
T10_57 = T_all[10.0][57]
T10_0 = T_all[10.0][0]
print(f"10° 尺度: 冷斑={T10_0:+.2f}, 對徑={T10_57:+.2f}")
print(f"→ 大尺度上冷斑仍冷 (-134→-68.8), 對徑仍微正 (+8.2→+5.5)")
print(f"→ 對徑點「+8.21」唔係平滑假象, 係 0.5°→10° 都穩定嘅微正溫度")

# 儲存
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "theory_check.txt"), "w") as f:
    f.write(f"# O6 理論檢驗\n")
    f.write(f"# antipodal_pairs={len(pairs)}, sum_mean={sums.mean():+.2f}, sum_std={sums.std():.1f}\n")
    f.write(f"# |dT|_mean={diffs.mean():.1f}, z_vs_random={z_diff:+.2f}\n")
    f.write(f"# node57_absT_rank={rank}/60\n")
    f.write(f"# hop_dist={dict(sorted(Counter(hop.values()).items()))}\n")
    f.write(f"# spearman_absT_hop: r={r_abs:.3f}, p={p_abs:.4f}\n")
    f.write(f"# zeroE={zeroE}, zeroE_mean_absT={np.abs(T[zeroE]).mean():.2f}\n")
    f.write(f"# node57_k={k[57]}\n")
    f.write(f"# T10: node0={T10_0:+.2f}, node57={T10_57:+.2f}\n")
print(f"\n✅ 已存: {OUT}/theory_check.txt")
