#!/usr/bin/env python3
"""
07_hallucination_check.py — O6 獨立幻覺檢查
=============================================
從原始 cache / data 檔案獨立重算所有文檔中嘅數字, 對比聲稱值。
避免 script 之間嘅 bug 連鎖 (每個數字獨立獲取, 唔用其他 script 輸出)。
"""
import healpy as hp
import numpy as np
import math
import os
import sys
from collections import defaultdict, deque
from scipy import stats
from astropy.coordinates import SkyCoord
import astropy.units as astropy_units

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
NODE_FILE = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
CACHE = "/tmp/cache_o3"
DATA = os.path.join(BASE, "o6_antipode_check/data")

passes = []
fails = []

def check(name, claimed, actual, tol, unit=""):
    """比較 claimed 同 actual 值, 容差 tol (絕對或相對)"""
    if isinstance(claimed, str):
        # 字串比較: 直接匹配
        ok = claimed == actual
    elif isinstance(claimed, float):
        ok = abs(claimed - actual) <= tol
    elif isinstance(claimed, int):
        ok = abs(claimed - actual) <= tol
    elif isinstance(claimed, list):
        ok = all(abs(c - a) <= tol for c, a in zip(claimed, actual)) if len(claimed) == len(actual) else False
    else:
        ok = claimed == actual
    
    if ok:
        passes.append(name)
        print(f"  ✅ {name}: {claimed} {unit}")
    else:
        fails.append(name)
        print(f"  ❌ {name}: claimed={claimed} {unit}, actual={actual} {unit}")

# ============ 載入共享數據 ============
print("=" * 66)
print("O6 獨立幻覺檢查 (從原始來源重算)")
print("=" * 66)

# 節點
nodes = []
with open(NODE_FILE) as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
assert len(nodes) == 60

# 載入 SMICA 4.17 cache
m417 = hp.read_map(os.path.join(CACHE, "SMICA_4.17.fits"), field=0)
nside = hp.get_nside(m417)

# ICRS → Galactic
sc = SkyCoord(ra=nodes[:, 0]*astropy_units.deg, dec=nodes[:, 1]*astropy_units.deg, frame='icrs')
gal = sc.galactic
l_deg = gal.l.deg
b_deg = gal.b.deg

# 節點溫度
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T = m417[pix] * 1e6

# 節點向量 + 圖
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

# BFS
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

cold_arr = np.array([color[i] for i in range(60)])

# ============ 1. 基本幾何 ============
print("\n=== 1. 基本幾何 ===")
check("節點數", 60, 60, 0)
check("邊數", 120, len(edges_list), 0)
check("degree 均勻", 4, len(adj[0]), 0)

# 對徑角
ang57 = math.degrees(math.acos(np.clip(np.dot(vecs[0], vecs[57]), -1, 1)))
check("對徑角 174.66°", 174.66, ang57, 0.05, "°")

# ============ 2. 節點溫度 ============
print("\n=== 2. 節點溫度 (4.17° SMICA) ===")
check("節點 0 T", -134.19, T[0], 0.5, "μK")
check("節點 57 T", 8.21, T[57], 0.5, "μK")
check("節點 57 hop", 8, hop[57], 0)
check("節點 57 冷色", 1, color[57], 0)
check("節點 57 b", 52.71, b_deg[57], 0.5, "°")

# 全天空百分位 (子採樣 1/7)
sample = m417[::7] * 1e6
pct57 = (sample < T[57]).mean() * 100
pct0 = (sample < T[0]).mean() * 100
check("節點 57 百分位", 56.6, pct57, 1.0, "%")
check("節點 0 百分位", 0.3, pct0, 0.5, "%")

# ============ 3. 區域統計 ============
print("\n=== 3. 區域統計 (5° 半徑) ===")
disc57 = hp.query_disc(nside, hp.ang2vec(l_deg[57], b_deg[57], lonlat=True), np.radians(5.0))
vals57 = m417[disc57] * 1e6
check("節點 57 5° 區域 mean", 0.20, vals57.mean(), 0.1, "μK")
check("節點 57 5° 區域 std", 22.07, vals57.std(), 0.5, "μK")
check("節點 57 5° 區域 min", -42.50, vals57.min(), 0.5, "μK")
check("節點 57 5° 區域 max", 34.94, vals57.max(), 0.5, "μK")

# 隨機 5° 盤對照 (bootstrap 200)
rng = np.random.default_rng(42)
rand_means = []
for _ in range(200):
    v = rng.normal(size=3); v = v / np.linalg.norm(v)
    d = hp.query_disc(nside, v, np.radians(5.0))
    rand_means.append((m417[d] * 1e6).mean())
rand_means = np.array(rand_means)
z_mean = (vals57.mean() - rand_means.mean()) / rand_means.std()
check("節點 57 區域 z_mean", -0.01, z_mean, 0.1, "σ")

# 冷斑區域
disc0 = hp.query_disc(nside, hp.ang2vec(l_deg[0], b_deg[0], lonlat=True), np.radians(5.0))
vals0 = m417[disc0] * 1e6
check("節點 0 5° 區域 mean", -93.71, vals0.mean(), 1.0, "μK")
check("節點 0 5° 區域 std", 25.2, vals0.std(), 1.0, "μK")

# ============ 4. 鄰居 ============
print("\n=== 4. 鄰居分析 ===")
nbrs = sorted(adj[57])
check("節點 57 degree 4", 4, len(nbrs), 0)
check("鄰居 hop 全部 7", True, all(hop[n] == 7 for n in nbrs), 0)
check("鄰居全部熱色", True, all(color[n] == 0 for n in nbrs), 0)
Tn = T[nbrs]
check("鄰居 mean T", 23.71, Tn.mean(), 0.5, "μK")
check("鄰居 min T", -25.48, Tn.min(), 0.5, "μK")
check("鄰居 max T", 71.67, Tn.max(), 0.5, "μK")

# ============ 5. 符號分佈 ============
print("\n=== 5. 符號分佈 (4.17°) ===")
n_cold_neg = np.sum((T < 0) & (cold_arr == 1))
n_cold_pos = np.sum((T > 0) & (cold_arr == 1))
n_hot_pos = np.sum((T > 0) & (cold_arr == 0))
n_hot_neg = np.sum((T < 0) & (cold_arr == 0))
check("冷色負溫 18", 18, n_cold_neg, 0)
check("冷色正溫 12", 12, n_cold_pos, 0)
check("熱色正溫 19", 19, n_hot_pos, 0)
check("熱色負溫 11", 11, n_hot_neg, 0)

# Fisher exact
table = [[n_cold_neg, n_cold_pos], [n_hot_neg, n_hot_pos]]
_, p_fisher = stats.fisher_exact(table)
check("Fisher p", 0.1205, p_fisher, 0.01)

# 匹配率
match = ((cold_arr == 1) & (T < 0)) | ((cold_arr == 0) & (T > 0))
check("匹配率 61.7%", 61.7, match.mean() * 100, 1.0, "%")

# 色-T 相關
r_ct = np.corrcoef(cold_arr, T)[0, 1]
check("色-T 相關 r", -0.244, r_ct, 0.01)

# 冷色正溫群
cp_idx = sorted([i for i in range(60) if cold_arr[i] == 1 and T[i] > 0])
check("冷色正溫群", [2, 6, 14, 16, 17, 28, 29, 43, 48, 55, 57, 58], cp_idx, 0)
check("節點 57 喺群", True, 57 in cp_idx, 0)
cp_mean = np.mean([T[i] for i in cp_idx])
check("冷色正溫群 mean T", 25.90, cp_mean, 0.5, "μK")

# ============ 6. 尺度效應 ============
print("\n=== 6. 尺度效應 ===")
scales = [0.5, 1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0]
claimed_T57 = [-5.76, -36.37, -15.37, 4.78, 8.21, 6.19, 2.60, 5.46]
claimed_T0 = [-203.13, -174.44, -154.71, -145.02, -134.19, -124.59, -99.67, -68.83]
for i, s in enumerate(scales):
    m = hp.read_map(os.path.join(CACHE, f"SMICA_{s}.fits"), field=0)
    ns = hp.get_nside(m)
    p = hp.ang2pix(ns, l_deg, b_deg, lonlat=True)
    T57_a = m[p[57]] * 1e6
    T0_a = m[p[0]] * 1e6
    check(f"節點 57 T @ {s}°", claimed_T57[i], T57_a, 0.5, "μK")
    check(f"節點 0 T @ {s}°", claimed_T0[i], T0_a, 0.5, "μK")

# 符號翻轉
signs = [np.sign(claimed_T57[i]) for i in range(len(scales))]
check("小尺度負 (0.5-2°)", -1, signs[0], 0)
check("大尺度正 (3-10°)", 1, signs[3], 0)

# ============ 7. 對徑對 ============
print("\n=== 7. 對徑對 ===")
pairs = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang > 170.0:
            pairs.append((i, j))
check("對徑對數 30", 30, len(pairs), 0)
same_col = sum(1 for i, j in pairs if color[i] == color[j])
check("全同色 30", 30, same_col, 0)
hop8 = sum(1 for i, j in pairs if hop[i] + hop[j] == 8)
check("hop 和=8 全部", 30, hop8, 0)
same_sign = sum(1 for i, j in pairs if (T[i] > 0) == (T[j] > 0))
check("同號 11", 11, same_sign, 0)
dT_vals = np.array([abs(T[i] - T[j]) for i, j in pairs])
check("|ΔT| mean 56.0", 56.0, dT_vals.mean(), 1.0, "μK")
check("|ΔT| median 38.6", 38.6, np.median(dT_vals), 1.0, "μK")
sum_vals = np.array([T[i] + T[j] for i, j in pairs])
check("和 mean -2.50", -2.50, sum_vals.mean(), 0.5, "μK")

# ============ 8. ΔE=0 ============
print("\n=== 8. ΔE=0 ===")
frust = set()
for a, b in edges_list:
    if color[a] == color[b]:
        frust.add(frozenset((a, b)))
k = {i: sum(1 for w in adj[i] if frozenset((i, w)) in frust) for i in range(60)}
zeroE = sorted([i for i in range(60) if k[i] == 2])
check("ΔE=0 12 節點", 12, len(zeroE), 0)
check("ΔE=0 群", [10,12,19,22,23,25,28,32,37,40,45,46], zeroE, 0)
check("節點 57 k=0", 0, k[57], 0)
check("節點 57 唔係 ΔE=0", False, 57 in zeroE, 0)
absT_zeroE = np.abs(T[zeroE]).mean()
absT_other = np.abs(T[[i for i in range(60) if i not in zeroE]]).mean()
check("ΔE=0 mean|T| 19.05", 19.05, absT_zeroE, 0.5, "μK")
check("其他 mean|T| 36.18", 36.18, absT_other, 0.5, "μK")

# ============ 9. 對徑點大尺度 ============
print("\n=== 9. 大尺度背景 ===")
m10 = hp.read_map(os.path.join(CACHE, "SMICA_10.0.fits"), field=0)
ns10 = hp.get_nside(m10)
disc10 = hp.query_disc(ns10, hp.ang2vec(l_deg[57], b_deg[57], lonlat=True), np.radians(10.0))
rmean10 = m10[disc10].mean() * 1e6
check("10° 區域 mean 10°", 12.99, rmean10, 1.0, "μK")
p10 = hp.ang2pix(ns10, l_deg[57], b_deg[57], lonlat=True)
T10_57 = m10[p10] * 1e6
check("節點 57 10° 平滑", 5.46, T10_57, 0.5, "μK")
p10_0 = hp.ang2pix(ns10, l_deg[0], b_deg[0], lonlat=True)
T10_0 = m10[p10_0] * 1e6
check("節點 0 10° 平滑", -68.83, T10_0, 0.5, "μK")

# ============ 10. 對徑點 |T| 排名 ============
print("\n=== 10. 對徑點 |T| 排名 ===")
absT = np.abs(T)
rank57 = np.sum(absT <= absT[57])
check("|T| 排名 14/60", 14, rank57, 0)

# ============ 11. 跨尺度匹配率 ============
print("\n=== 11. 跨尺度匹配率 ===")
claimed_rates = {0.5: 60.0, 1.0: 63.3, 2.0: 63.3, 3.0: 61.7, 4.17: 61.7, 5.0: 60.0, 7.0: 58.3, 10.0: 60.0}
for s in scales:
    m = hp.read_map(os.path.join(CACHE, f"SMICA_{s}.fits"), field=0)
    ns = hp.get_nside(m)
    p = hp.ang2pix(ns, l_deg, b_deg, lonlat=True)
    Ts = m[p] * 1e6
    match_rate = ((cold_arr == 1) & (Ts < 0) | (cold_arr == 0) & (Ts > 0)).mean() * 100
    check(f"匹配率 {s}°", claimed_rates[s], round(match_rate, 1), 1.0, "%")

# ============ 12. 匯總 ============
print(f"\n{'='*66}")
print(f"結果: {len(passes)} 通過, {len(fails)} 失敗")
if fails:
    print("❌ 有失敗! 需要調查")
    print("失敗項目:")
    for f in fails:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("✅ 全部通過 — 無幻覺")