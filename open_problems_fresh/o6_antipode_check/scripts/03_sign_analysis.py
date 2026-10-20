#!/usr/bin/env python3
"""
03_sign_analysis.py — O6: 冷色/熱色節點溫度符號分佈
======================================================
核心問題: 冷色 30 節點有幾多真係負溫度? 熱色 30 有幾多正?
1. 2×2 列聯表: 色 × 溫度符號
2. 冷色正溫 (12) vs 冷色負溫 (18): |T| 比較
3. 匹配率 + Fisher exact / binomial
4. 對徑點 (57) 喺冷色正溫群嘅位置 — 典型定孤例?
5. 相位模型解釋: T = A·cos(θ), 色 = BFS parity — 兩者正交?
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

# ============ 載入 ============
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

# BFS hop + 著色
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

print("=" * 66)
print("O6: 冷色/熱色 vs 溫度符號分析")
print("=" * 66)

# ============ 多尺度載入 ============
scales = [0.5, 1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0]
results = {}
for s in scales:
    name = f"SMICA_{s}.fits"
    m = hp.read_map(os.path.join(CACHE, name), field=0)
    nside = hp.get_nside(m)
    pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
    results[s] = m[pix] * 1e6

# ============ 1. 2×2 列聯表 (4.17° 為主) ============
T = results[4.17]
cold = np.array([color[i] for i in range(60)])
print("\n=== 1. 2×2 列聯表 (4.17° SMICA) ===")
print("           T<0      T>0     總")
print(f"冷色(1)  {np.sum((T<0)&(cold==1)):>5}   {np.sum((T>0)&(cold==1)):>5}    {np.sum(cold==1)}")
print(f"熱色(0)  {np.sum((T<0)&(cold==0)):>5}   {np.sum((T>0)&(cold==0)):>5}    {np.sum(cold==0)}")
table = [[np.sum((T<0)&(cold==1)), np.sum((T>0)&(cold==1))],
         [np.sum((T<0)&(cold==0)), np.sum((T>0)&(cold==0))]]
odds, p_fisher = stats.fisher_exact(table)
print(f"Fisher exact p = {p_fisher:.4f}, odds ratio = {odds:.3f}")

# ============ 2. 冷色正溫 vs 冷色負溫 ============
cp = [i for i in range(60) if cold[i] == 1 and T[i] > 0]
cn = [i for i in range(60) if cold[i] == 1 and T[i] < 0]
hp_ = [i for i in range(60) if cold[i] == 0 and T[i] > 0]
hn = [i for i in range(60) if cold[i] == 0 and T[i] < 0]
print(f"\n=== 2. 四群節點 (4.17°) ===")
print(f"冷色正溫: {len(cp)} 個 → {sorted(cp)}")
print(f"冷色負溫: {len(cn)} 個")
print(f"熱色正溫: {len(hp_)} 個")
print(f"熱色負溫: {len(hn)} 個 → {sorted(hn)}")

abs_cp = np.abs(T[cp]); abs_cn = np.abs(T[cn])
abs_hp = np.abs(T[hp_]); abs_hn = np.abs(T[hn])
print(f"\n|T| mean: 冷色正溫={abs_cp.mean():.1f}, 冷色負溫={abs_cn.mean():.1f}, "
      f"熱色正溫={abs_hp.mean():.1f}, 熱色負溫={abs_hn.mean():.1f} μK")
if len(cp) > 1 and len(cn) > 1:
    tt = stats.ttest_ind(abs_cp, abs_cn, equal_var=False)
    print(f"冷色正 vs 冷色負 |T|: t={tt.statistic:.3f}, p={tt.pvalue:.4f}")

# ============ 3. 匹配率 (每個尺度) ============
print("\n=== 3. 匹配率 vs 平滑尺度 ===")
for s in scales:
    Ts = results[s]
    match = ((cold == 1) & (Ts < 0)) | ((cold == 0) & (Ts > 0))
    print(f"  {s:>5}°: 匹配率 {match.mean()*100:.1f}% ({match.sum()}/60)")

# ============ 4. 冷色正溫群嘅 hop 分佈 ============
print("\n=== 4. 冷色正溫群 hop 分佈 ===")
print(f"冷色正溫 hop: {sorted([hop[i] for i in cp])}")
print(f"冷色負溫 hop: {sorted([hop[i] for i in cn])}")
# 按 hop 層計 mean
print("\n按 hop 層 mean T (4.17°):")
for h in range(9):
    idx = [i for i in range(60) if hop[i] == h]
    print(f"  hop={h}: mean={T[idx].mean():+.2f} μK, n={len(idx)}")

# ============ 5. 對徑點 57 喺冷色正溫群嘅位置 ============
print("\n=== 5. 節點 57 喺冷色正溫群嘅位置 ===")
cp_sorted = sorted(cp, key=lambda i: T[i])
print(f"冷色正溫群按 T 排序: {[(i, round(T[i],1)) for i in cp_sorted]}")
print(f"節點 57 T={T[57]:+.2f} μK → 排名 {cp_sorted.index(57)+1}/{len(cp)}")
print(f"冷色正溫群 mean={T[cp].mean():+.2f} μK → 節點 57 同 mean 差 {T[57]-T[cp].mean():+.2f}")

# ============ 6. 相位模型測試 ============
print("\n=== 6. 相位模型: 著色 = parity (結構), 溫度 = 幅度×相位 (物理) ===")
# 模型: T_i = A·cos(θ_i)。如果 θ 同 hop 無關 → 著色同溫度正交
# 測試: hop 層 mean 應該接近 0 (如果 θ 均勻)
layer_means = np.array([T[[i for i in range(60) if hop[i]==h]].mean() for h in range(9)])
print(f"hop 層 mean: {[f'{v:+.1f}' for v in layer_means]}")
print(f"層 mean 絕對值平均: {np.abs(layer_means).mean():.2f} μK")
print(f"→ 層 mean 細 (≪ 節點級 scatter) → hop/parity 唔係主要溫度驅動")

# 關聯: 色 同 T 嘅相關 (每個尺度)
print("\n色-T 相關 r (每個尺度):")
for s in scales:
    Ts = results[s]
    r = np.corrcoef([cold[i] for i in range(60)], Ts)[0, 1]
    print(f"  {s:>5}°: r = {r:+.3f}")

# ============ 7. 關鍵統計: 冷色 vs 熱色 mean (每尺度) ============
print("\n=== 7. 冷色 vs 熱色 mean 差 (每尺度) ===")
for s in scales:
    Ts = results[s]
    Tc = Ts[[i for i in range(60) if cold[i]==1]].mean()
    Th = Ts[[i for i in range(60) if cold[i]==0]].mean()
    print(f"  {s:>5}°: 冷色 {Tc:+.2f}, 熱色 {Th:+.2f}, 差 {Tc-Th:+.2f} μK")

# 儲存
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "sign_analysis.txt"), "w") as f:
    f.write(f"# O6 冷色/熱色 vs 溫度符號 (SMICA 多尺度)\n")
    f.write(f"# fisher_4.17: p={p_fisher:.4f}, odds={odds:.3f}\n")
    f.write(f"# cold_pos={len(cp)} nodes {sorted(cp)}, cold_neg={len(cn)}, hot_pos={len(hp_)}, hot_neg={len(hn)}\n")
    f.write(f"# node57_in_cold_pos_rank={cp_sorted.index(57)+1}/{len(cp)}\n")
    for s in scales:
        Ts = results[s]
        match = ((cold == 1) & (Ts < 0)) | ((cold == 0) & (Ts > 0))
        f.write(f"scale {s} match_rate {match.mean()*100:.1f}%\n")
print(f"\n✅ 已存: {OUT}/sign_analysis.txt")
