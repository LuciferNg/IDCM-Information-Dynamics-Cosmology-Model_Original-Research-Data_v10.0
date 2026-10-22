#!/usr/bin/env python3
"""
O43 MASTER VERIFY — 獨立重算所有 O43 關鍵數值, 與文檔對照
==========================================================
原則: 由原始數據獨立重算, 核對每個文檔聲稱值 (禁止循環引用)
"""
import numpy as np
import math, os
from collections import deque, Counter

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
O43 = f"{BASE}/open_problems_fresh/o43_holographic_untested"

passes, fails = [], []
def check(name, claim, value, tol=0):
    if isinstance(claim, str):
        if claim == value: passes.append(name)
        else: fails.append(f"{name}: claim={claim} actual={value}")
    elif abs(claim - value) <= tol:
        passes.append(name)
    else:
        fails.append(f"{name}: claim={claim} actual={value:.4f}")

print("=" * 70)
print("O43 MASTER VERIFY — 獨立重算所有關鍵數值")
print("=" * 70)

# ═══════════════════════════════════════════════════════
# A. O43-A: Silk 阻尼 / M=33 截斷
# ═══════════════════════════════════════════════════════
print("\n─── A. O43-A: M=33 截斷 vs Silk 阻尼 ───")
planck = np.loadtxt(f"{BASE}/open_problems_fresh/o9_high_ell_peaks/data/planck_tt.txt")
ell = planck[:, 0].astype(int)
C = planck[:, 1]
err = planck[:, 2]
D = C * ell * (ell + 1) / (2 * np.pi)
D_err = err * ell * (ell + 1) / (2 * np.pi)

from scipy.optimize import curve_fit
def silk_env(l, A, l_silk, beta, alpha):
    return A * (l/1000)**alpha * np.exp(-((l/l_silk)**beta))

mask = (ell > 800) & (ell < 2500)
popt, _ = curve_fit(silk_env, ell[mask], D[mask],
                     p0=[2000, 2000, 1.5, 0], maxfev=10000)
A_fit, l_silk, beta, alpha = popt
check("A-1 Silk A", 3952.3, A_fit, 50)
check("A-2 Silk ℓ_silk", 3083.3, l_silk, 100)
check("A-3 Silk β", 0.000, abs(beta), 0.05)
check("A-4 Silk α", -2.425, alpha, 0.1)
print(f"   A={A_fit:.1f}, ℓ_silk={l_silk:.1f}, β={beta:.4f}, α={alpha:.4f}")

# ℓ=1452 前後跳變
before = D[(ell >= 1430) & (ell < 1452)]
after = D[(ell >= 1452) & (ell < 1475)]
sb = silk_env(ell[(ell >= 1430) & (ell < 1452)], *popt)
sa = silk_env(ell[(ell >= 1452) & (ell < 1475)], *popt)
data_jump = np.mean(before) - np.mean(after)
silk_jump = np.mean(sb) - np.mean(sa)
extra = data_jump - silk_jump
check("A-5 數據跳變 39.2", 39.2, data_jump, 2)
check("A-6 Silk 跳變 22.1", 22.1, silk_jump, 2)
check("A-7 額外跳變 17.1", 17.1, extra, 2)
print(f"   1430-1452: {np.mean(before):.1f} → 1452-1475: {np.mean(after):.1f}")
print(f"   數據跳變 {data_jump:.1f}, Silk {silk_jump:.1f}, 額外 {extra:.1f}")

# 高ℓ殘差
D_pred = silk_env(ell, *popt)
res_all = (D - D_pred) / D_pred * 100
res_high = res_all[ell > 1448]
check("A-8 高ℓ殘差 mean", -8.6, np.mean(res_high), 2)
check("A-9 高ℓ殘差 std", 21.6, np.std(res_high), 2)
print(f"   高ℓ殘差: mean={np.mean(res_high):.1f}%, std={np.std(res_high):.1f}%")

# ℓ=1452 附近 d²D
d2 = np.diff(D, 2)
d2_1452 = d2[np.abs(ell[1:-1] - 1452) < 5]
all_d2_high = d2[ell[1:-1] > 1400]
check("A-10 d²D@1452 ≈ 13.2", 13.2, d2_1452[0] if len(d2_1452) else 0, 2)
check("A-11 高ℓ d²D std ≈ 17.8", 17.8, np.std(all_d2_high), 1)
print(f"   d²D@1452={d2_1452[0]:.1f} (std高ℓ={np.std(all_d2_high):.1f})")

# ═══════════════════════════════════════════════════════
# B. O43-B: 同調群 Betti 數 + 圖性質
# ═══════════════════════════════════════════════════════
print("\n─── B. O43-B: Betti 數 + 圖性質 ───")
nodes = []
with open(f"{BASE}/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])

adj = [set() for _ in range(60)]
edges = []
for i in range(60):
    for j in range(i+1, 60):
        a = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if a < 28:
            adj[i].add(j); adj[j].add(i)
            edges.append((i, j))

check("B-1 E=120", 120, len(edges))
check("B-2 4-regular", True, all(len(adj[i])==4 for i in range(60)))
print(f"   V=60, E={len(edges)}, 4-regular={all(len(adj[i])==4 for i in range(60))}")

triangles = set()
for i in range(60):
    for j in adj[i]:
        if j <= i: continue
        for kk in adj[i] & adj[j]:
            if kk > j:
                triangles.add(tuple(sorted((i, j, kk))))
check("B-3 三角形=20", 20, len(triangles))

# Laplacian 特徵值
A = np.zeros((60, 60))
for i, j in edges:
    A[i, j] = A[j, i] = 1
L = np.diag([4]*60) - A
eigvals = np.linalg.eigvalsh(L)
zero_eigs = np.sum(np.abs(eigvals) < 1e-10)
check("B-4 零特徵值=1", 1, zero_eigs)
nz = sorted([v for v in eigvals if v > 1e-10])
check("B-5 λ₁≈0.382", 0.382, nz[0], 0.001)
check("B-6 λ₄≈1.075", 1.075, nz[3], 0.001)
print(f"   零特徵值={zero_eigs}, 前5={[f'{v:.4f}' for v in nz[:5]]}")

# Betti 數 (GF(2))
edge_to_idx = {e: idx for idx, e in enumerate(edges)}
tri_list = list(triangles)
T = len(tri_list); E = len(edges)
d1 = np.zeros((E, 60), dtype=int)
for ei, (i, j) in enumerate(edges):
    d1[ei, i] = 1; d1[ei, j] = 1
d2 = np.zeros((T, E), dtype=int)
for ti, tri in enumerate(tri_list):
    for a, b in [(tri[0],tri[1]),(tri[1],tri[2]),(tri[0],tri[2])]:
        e = (min(a,b), max(a,b))
        if e in edge_to_idx: d2[ti, edge_to_idx[e]] = 1

def rank_gf2(M):
    if len(M) == 0 or len(M[0]) == 0: return 0
    A = M.copy() % 2
    m, n = A.shape
    rank = 0; row = 0
    for col in range(n):
        pivot = -1
        for r in range(row, m):
            if A[r, col] == 1: pivot = r; break
        if pivot == -1: continue
        A[[row, pivot]] = A[[pivot, row]]
        for r in range(m):
            if r != row and A[r, col] == 1: A[r] ^= A[row]
        row += 1; rank += 1
        if row == m: break
    return rank

r1 = rank_gf2(d1)
r2 = rank_gf2(d2)
beta0 = 60 - r1
beta1 = (E - r1) - r2
beta2 = T - r2
check("B-7 β₀=1", 1, beta0)
check("B-8 β₁=41", 41, beta1)
check("B-9 β₂=0", 0, beta2)
check("B-10 Euler χ=-40", -40, beta0 - beta1 + beta2)
print(f"   β₀={beta0}, β₁={beta1}, β₂={beta2}, χ={beta0-beta1+beta2}")

# 平面性 (networkx)
import networkx as nx
G = nx.Graph()
G.add_edges_from(edges)
is_planar, _ = nx.check_planarity(G)
check("B-11 平面圖=True", True, is_planar)
print(f"   平面圖: {is_planar}")

# ═══════════════════════════════════════════════════════
# C. O43-D: k-T 分層統計
# ═══════════════════════════════════════════════════════
print("\n─── C. O43-D: k-T 分層統計 ───")
T_node = {}
with open(f"{BASE}/open_problems_fresh/o3_node_temperatures/data/node_temps.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split()
        T_node[int(p[0])] = float(p[2])
T_arr = np.array([T_node[i] for i in range(60)])

k = []
with open(f"{BASE}/main_problems/p4_cmb_cold_spot/data/anchored_coloring.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split()
        k.append(int(p[-1]))
k = np.array(k)

k0m = k == 0; k1m = k == 1; k2m = k == 2
m0 = np.mean(np.abs(T_arr[k0m]))
m1 = np.mean(np.abs(T_arr[k1m]))
m2 = np.mean(np.abs(T_arr[k2m]))
check("C-1 k0 mean|T|=64.8", 64.8, m0, 0.1)
check("C-2 k1 mean|T|=30.4", 30.4, m1, 0.1)
check("C-3 k2 mean|T|=19.0", 19.0, m2, 0.1)
check("C-4 k 分佈 8/40/12", "8/40/12", f"{np.sum(k0m)}/{np.sum(k1m)}/{np.sum(k2m)}")
print(f"   k0={m0:.1f}, k1={m1:.1f}, k2={m2:.1f}")

from scipy.stats import mannwhitneyu
u02, p02 = mannwhitneyu(np.abs(T_arr[k0m]), np.abs(T_arr[k2m]), alternative='greater')
u01, p01 = mannwhitneyu(np.abs(T_arr[k0m]), np.abs(T_arr[k1m]), alternative='greater')
check("C-5 MW p(k0>k2)=0.0194", 0.0194, p02, 0.003)
check("C-6 MW p(k0>k1)=0.0419", 0.0419, p01, 0.005)
print(f"   MW: k0vsK2 p={p02:.4f}, k0vsK1 p={p01:.4f}")

# Cohen's d
def cohens_d(x, y):
    return (np.mean(x) - np.mean(y)) / np.sqrt((np.std(x)**2 + np.std(y)**2) / 2)
d02 = cohens_d(np.abs(T_arr[k0m]), np.abs(T_arr[k2m]))
d01 = cohens_d(np.abs(T_arr[k0m]), np.abs(T_arr[k1m]))
check("C-7 Cohen's d(k0-k2)=1.329", 1.329, d02, 0.01)
check("C-8 Cohen's d(k0-k1)=0.903", 0.903, d01, 0.01)
print(f"   Cohen's d: k0-k2={d02:.3f}, k0-k1={d01:.3f}")

# Bootstrap (10000)
rng = np.random.default_rng(42)
N_BOOT = 10000
cnt = 0
for _ in range(N_BOOT):
    idx = rng.choice(60, 60, replace=True)
    kb, Tb = k[idx], T_arr[idx]
    b0 = np.mean(np.abs(Tb[kb==0]))
    b1 = np.mean(np.abs(Tb[kb==1]))
    b2 = np.mean(np.abs(Tb[kb==2]))
    if b0 > b1 > b2: cnt += 1
check("C-9 Bootstrap 93.4%", 93.4, cnt/N_BOOT*100, 1.5)
print(f"   Bootstrap k0>k1>k2: {cnt/N_BOOT*100:.1f}%")

# Permutation
obs_diff = m0 - m2
cnt_p = 0
for _ in range(N_BOOT):
    ks = k.copy()
    rng.shuffle(ks)
    d0 = np.mean(np.abs(T_arr[ks==0]))
    d2 = np.mean(np.abs(T_arr[ks==2]))
    if d0 - d2 >= obs_diff: cnt_p += 1
check("C-10 Permutation p=0.0011", 0.0011, cnt_p/N_BOOT, 0.002)
print(f"   Permutation p = {cnt_p/N_BOOT:.4f}")

# 移除極端
mask_t = np.ones(60, dtype=bool)
for r in [0, 9, 53]: mask_t[r] = False
kt, Tt = k[mask_t], T_arr[mask_t]
r0 = np.mean(np.abs(Tt[kt==0]))
r1 = np.mean(np.abs(Tt[kt==1]))
r2 = np.mean(np.abs(Tt[kt==2]))
check("C-11 移除極端後 k0=33.1", 33.1, r0, 0.5)
check("C-12 移除極端後 k1=30.4", 30.4, r1, 0.3)
check("C-13 移除極端後 k2=19.0", 19.0, r2, 0.3)
print(f"   移除 0,9,53: k0={r0:.1f}, k1={r1:.1f}, k2={r2:.1f}")

# ═══════════════════════════════════════════════════════
# D. O43-E: Kuratowski / 平面性
# ═══════════════════════════════════════════════════════
print("\n─── D. O43-E: 平面性 ───")
check("D-1 NetworkX planar", True, is_planar)
# K5 subgraph?
k5 = False
for i in range(60):
    nb = list(adj[i])
    if len(nb) < 4: continue
    for combo in __import__('itertools').combinations(nb, 4):
        if all(combo[a] in adj[combo[b]] for a in range(4) for b in range(a+1,4)):
            k5 = True; break
    if k5: break
check("D-2 冇 K5 子圖", False, k5)
print(f"   K5 subgraph: {k5}, planar: {is_planar}")

# ═══════════════════════════════════════════════════════
# E. O43-F: k=0 節點 + hop
# ═══════════════════════════════════════════════════════
print("\n─── E. O43-F: k=0 節點 ───")
k0_idx = sorted([int(i) for i in range(60) if k[i] == 0])
check("E-1 k=0 節點 8 個", str([0,4,9,20,35,53,54,57]), str(k0_idx))
print(f"   k=0: {k0_idx}")

# BFS hop
hop = [-1]*60
q = deque([0]); hop[0] = 0
while q:
    u = q.popleft()
    for v in adj[u]:
        if hop[v] == -1:
            hop[v] = hop[u] + 1
            q.append(v)

extreme = [0, 9, 53]
mild = [4, 20, 35, 54, 57]
h_ext = np.mean([hop[i] for i in extreme])
h_mild = np.mean([hop[i] for i in mild])
check("E-2 極端 mean hop=1.3", 1.3, h_ext, 0.1)
check("E-3 普通 mean hop=5.6", 5.6, h_mild, 0.1)
print(f"   極端 hop mean={h_ext:.1f}, 普通 hop mean={h_mild:.1f}")
for i in k0_idx:
    print(f"   #{i}: T={T_arr[i]:+.1f}, hop={hop[i]}")

# ═══════════════════════════════════════════════════════
# 結果
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 70)
print(f"PASS: {len(passes)}  FAIL: {len(fails)}")
for f in fails:
    print(f"  ❌ {f}")
if fails:
    print("❌ 有 FAIL")
else:
    print("✅ 全部通過 — O43 所有文檔聲稱值與原始數據重算一致")

with open(f"{O43}/data_o43_master_verify.txt", "w") as f:
    f.write(f"O43 MASTER VERIFY: {len(passes)}/{len(passes)+len(fails)} PASS\n")
    for line in [f"  ❌ {x}" for x in fails]:
        f.write(line + "\n")
print(f"\n結果寫入 data_o43_master_verify.txt")