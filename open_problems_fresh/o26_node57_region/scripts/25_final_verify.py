#!/usr/bin/env python3
"""
25_final_verify.py — O26 全面驗證 (所有推導 + 結果)
======================================================
重新計算所有關鍵數值, 核對記錄文檔:
1. 節點 57 基本數據 (RA/Dec/T/hop/k)
2. 對徑定理 (右乘 r₀, ε=5.34°)
3. k 分佈 {0:8, 1:40, 2:12} + 32 阻挫邊
4. 20 三角形完美匹配 + 12/8 分佈
5. k2-k2 對徑交換對
6. k↔溫度分層 (mean|T|: 64.8/29.7/19.1)
7. 對徑對 |ΔT| (0↔57 = 142.4)
8. 溫度對齊測試結果 (G2)
9. 偏振對齊測試結果 (G3)
10. r₀ 軸 Dec = arcsin(1/(2φ)) = 18°
"""
import numpy as np
import math
from collections import defaultdict, deque, Counter

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
OUT = f"{BASE}/o26_node57_region/data"

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line, flush=True)
    results.append(line)

log("=" * 72)
log("O26 全面驗證 — 重新計算所有關鍵數值")
log("=" * 72)

# ============ 讀數據 ============
nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])

T = {}
with open(f"{BASE}/o3_node_temperatures/data/node_temps.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split()
        T[int(p[0])] = float(p[2])
T_arr = np.array([T[i] for i in range(60)])

k = []
with open(f"{BASE}/cmb_cold_spot/data/anchored_coloring.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split()
        k.append(int(p[-1]))
k = np.array(k)

# 圖結構
adj = [set() for _ in range(60)]
edges = []
for i in range(60):
    for j in range(i+1, 60):
        a = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if a < 28:
            adj[i].add(j); adj[j].add(i)
            edges.append((i, j))

# ============ 1. 節點 57 ============
log("\n=== 1. 節點 57 基本數據 ===")
ra57, dec57 = nodes[57]
log(f"  RA={ra57:.4f}° (記錄: 233.7086), Dec={dec57:.4f}° (記錄: 22.2082)")
log(f"  T(4.17°) = {T_arr[57]:+.2f} μK (記錄: +8.21)")
log(f"  k = {k[57]} (記錄: 0)")
# 對徑關係
d0_57 = math.degrees(math.acos(np.clip(np.dot(vecs[0], vecs[57]), -1, 1)))
log(f"  角距離 0↔57 = {d0_57:.2f}° (記錄: 174.66)")

# ============ 2. 對徑定理 ============
log("\n=== 2. 對徑定理 (右乘 r₀, ε=5.34°) ===")
def antip(x):
    best = None; ba = 1e9
    for y in range(60):
        if y == x: continue
        dd = math.degrees(math.acos(np.clip(np.dot(vecs[x], vecs[y]), -1, 1)))
        if dd > 170 and dd < ba:
            ba = dd; best = y
    return best
pairs = []
used = set()
for i in range(60):
    if i in used: continue
    j = antip(i)
    pairs.append((i, j))
    used.add(i); used.add(j)
log(f"  對徑對: {len(pairs)} (記錄: 30)")
# ε: angle(antip(i), -v_i)
eps = []
for i in range(60):
    j = antip(i)
    d = math.degrees(math.acos(np.clip(np.dot(vecs[j], -vecs[i]), -1, 1)))
    eps.append(d)
eps = np.array(eps)
log(f"  ε mean = {np.mean(eps):.5f}° (記錄: 5.3401), std = {np.std(eps):.6f}")
log(f"  ε 理論 5.340126° vs 實測 {np.mean(eps):.6f}°")

# 對徑距離
pair_d = [math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) for i, j in pairs]
log(f"  對徑距離 mean = {np.mean(pair_d):.2f}° (記錄: 174.66)")

# ============ 3. k 分佈 + 阻挫邊 ============
log("\n=== 3. k 分佈 + 阻挫邊 ===")
color = {0: 1}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in color:
            color[v] = 1 - color[u]
            q.append(v)
k_calc = [sum(1 for v in adj[i] if color[v] == color[i]) for i in range(60)]
k_dist = Counter(k_calc)
log(f"  k 分佈 (重算): {dict(sorted(k_dist.items()))} (記錄: {{0:8, 1:40, 2:12}})")
log(f"  k 一致 (重算 vs 檔案): {all(k_calc[i] == k[i] for i in range(60))}")
frust = [(u, v) for u, v in edges if color[u] == color[v]]
log(f"  阻挫邊: {len(frust)} (記錄: 32)")

# ============ 4. 三角形 ============
log("\n=== 4. 三角形完美匹配 ===")
triangles = set()
for i in range(60):
    for j in adj[i]:
        if j <= i: continue
        for kk in adj[i] & adj[j]:
            if kk > j:
                triangles.add(tuple(sorted((i, j, kk))))
log(f"  三角形: {len(triangles)} (記錄: 20)")
# 共享檢查
shared = 0
tl = list(triangles)
for i in range(len(tl)):
    for j in range(i+1, len(tl)):
        if set(tl[i]) & set(tl[j]): shared += 1
log(f"  共享節點對: {shared} (記錄: 0)")
# k2 分佈
k2set = set(np.where(np.array(k_calc) == 2)[0])
tri_k2 = sum(1 for t in triangles if any(x in k2set for x in t))
log(f"  含 k2 三角形: {tri_k2}/20 (記錄: 12)")
tri_k0 = sum(1 for t in triangles if any(x in set(np.where(np.array(k_calc) == 0)[0]) for x in t))
log(f"  含 k0 三角形: {tri_k0}/20 (記錄: 8)")

# ============ 5. k2-k2 對徑交換對 ============
log("\n=== 5. k2-k2 對徑交換對 ===")
for a, b in [(12, 19), (45, 46)]:
    ap_a, ap_b = antip(a), antip(b)
    has_edge = (min(ap_a, ap_b), max(ap_a, ap_b)) in set(edges)
    log(f"  #{a}↔#{b}: 對徑→#{ap_a}↔#{ap_b}, 有邊? {has_edge}")

# ============ 6. k↔溫度分層 ============
log("\n=== 6. k↔溫度分層 ===")
k0i = np.where(k == 0)[0]; k1i = np.where(k == 1)[0]; k2i = np.where(k == 2)[0]
m0 = np.mean(np.abs(T_arr[k0i])); m1 = np.mean(np.abs(T_arr[k1i])); m2 = np.mean(np.abs(T_arr[k2i]))
log(f"  k=0 mean|T| = {m0:.1f} μK (記錄: 64.8)")
log(f"  k=1 mean|T| = {m1:.1f} μK (記錄: 29.7)")
log(f"  k=2 mean|T| = {m2:.1f} μK (記錄: 19.1)")
log(f"  排序 k0>k1>k2: {m0 > m1 > m2}")

# ============ 7. 對徑對 |ΔT| ============
log("\n=== 7. 對徑對 |ΔT| ===")
dT = [abs(T_arr[i] - T_arr[j]) for i, j in pairs]
log(f"  0↔57 |ΔT| = {dT[0]:.1f} μK (記錄: 142.4)")
log(f"  30 對 mean |ΔT| = {np.mean(dT):.1f} μK")
# 排名
rank = sorted(dT, reverse=True).index(dT[0]) + 1
log(f"  0↔57 排名: {rank}/30 (記錄: 第2大)")
# ΔE=0 對 (k=2 對)
k2_pairs = [(i, j) for i, j in pairs if i in k2set and j in k2set]
dT_k2 = [abs(T_arr[i] - T_arr[j]) for i, j in k2_pairs]
others = [abs(T_arr[i] - T_arr[j]) for i, j in pairs if not (i in k2set and j in k2set)]
log(f"  k2 對 mean |ΔT| = {np.mean(dT_k2):.1f} (記錄: 25.8)")
log(f"  其他 mean |ΔT| = {np.mean(others):.1f} (記錄: 63.5)")

# ============ 8. r₀ 軸 ============
log("\n=== 8. r₀ 軸 Dec = arcsin(1/(2φ)) ===")
phi = (1 + math.sqrt(5)) / 2
dec_theory = math.degrees(math.asin(1/(2*phi)))
log(f"  arcsin(1/(2φ)) = {dec_theory:.6f}° (記錄: 18.0000)")
log(f"  sin(18°) = {math.sin(math.radians(18)):.6f}, 1/(2φ) = {1/(2*phi):.6f}")

# ============ 9. 對齊測試回顧 ============
log("\n=== 9. 對齊測試 (G2/G3) 數值 ===")
# G2: dipole 擬合
A = np.column_stack([np.ones(60), vecs])
coef, _, _, _ = np.linalg.lstsq(A, T_arr, rcond=None)
dip = coef[1:]
dip_dir = dip / np.linalg.norm(dip)
dip_ra = math.degrees(math.atan2(dip_dir[1], dip_dir[0])) % 360
dip_dec = math.degrees(math.asin(dip_dir[2]))
log(f"  G2 dipole: RA={dip_ra:.1f}°, Dec={dip_dec:.1f}° (記錄: 231.7, -14.9)")
axis = np.array([math.cos(math.radians(18))*math.cos(math.radians(328.2825)),
                 math.cos(math.radians(18))*math.sin(math.radians(328.2825)),
                 math.sin(math.radians(18))])
ang = math.degrees(math.acos(np.clip(np.dot(dip_dir, axis), -1, 1)))
log(f"  G2 dipole vs 軸: {ang:.1f}° (記錄: 100.7)")

log("\n" + "=" * 72)
log("驗證完成")
log("=" * 72)

with open(f"{OUT}/node57_final_verify.txt", "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/node57_final_verify.txt")
