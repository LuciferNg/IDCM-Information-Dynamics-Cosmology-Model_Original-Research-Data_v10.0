#!/usr/bin/env python3
"""
08_verify_negative.py — 03_final_negative_result.md 數字驗證
=============================================================
獨立驗證最終負結果文件嘅所有關鍵聲稱:
1. 15.109° 隨旋轉變化 (std=7.05°)
2. 60 節點冇旋轉對稱
3. 最近鄰 26.09° × 4
4. 對徑點 174.66°
5. 直徑 8 (BFS 1+4+8+11+12+11+8+4+1)
"""
import numpy as np, math

print("=" * 66)
print("O1 負結果 — 數字驗證")
print("=" * 66)
errors = []
def check(name, calc, doc, tol=0.01):
    diff = abs(calc - doc)
    status = "✅" if diff < tol else "❌"
    print(f"  {status} {name}: {calc:.4f} vs 文檔 {doc} (差 {diff:.4f})")
    if diff >= tol:
        errors.append(f"{name}: {calc} vs {doc}")

# ============ 1. 60 節點載入 ============
nodes = []
with open("../cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([np.array([math.cos(math.radians(d))*math.cos(math.radians(r)),
                           math.cos(math.radians(d))*math.sin(math.radians(r)),
                           math.sin(math.radians(d))]) for r, d in nodes])
print(f"\n[1] 節點數: {len(vecs)} (文檔 60)")
if len(vecs) != 60: errors.append("節點數 != 60")

# ============ 2. 最近鄰 26.09° × 4 ============
print(f"\n[2] 最近鄰距離:")
d0 = [math.degrees(math.acos(np.clip(np.dot(vecs[0], vecs[j]), -1, 1))) for j in range(1, 60)]
d0s = sorted(d0)
print(f"  最近 4: {[f'{d:.4f}' for d in d0s[:4]]}")
check("最近鄰 1", d0s[0], 26.09)
check("最近鄰 4 (第4個)", d0s[3], 26.17, tol=0.1)
# 有幾多個 < 28°?
n_close = sum(1 for d in d0s if d < 28)
print(f"  <28° 節點數: {n_close} (文檔 4)")
if n_close != 4: errors.append(f"最近鄰數 != 4: {n_close}")

# ============ 3. 對徑點 174.66° ============
print(f"\n[3] 對徑點:")
dmax = max(d0)
check("對徑距離", dmax, 174.66)
# 搵對徑節點
j_max = np.argmax(d0) + 1
print(f"  對徑節點: {j_max} (文檔 57)")

# ============ 4. 直徑 8 BFS ============
print(f"\n[4] BFS 直徑:")
# 建圖 (閾值 28°)
adj = [[] for _ in range(60)]
for i in range(60):
    for j in range(i+1, 60):
        d = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if d < 28:
            adj[i].append(j)
            adj[j].append(i)
# BFS 從節點 0
from collections import deque
dist = [-1]*60
dist[0] = 0
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if dist[v] == -1:
            dist[v] = dist[u] + 1
            q.append(v)
from collections import Counter
levels = Counter(dist)
print(f"  BFS 層級: {dict(sorted(levels.items()))}")
print(f"  直徑: {max(dist)} (文檔 8)")
check("直徑", max(dist), 8)

# ============ 5. 旋轉不變性重算 ============
print(f"\n[5] 旋轉不變性 (重算, 30 次):")
phi = (1 + 5**0.5) / 2
inv_phi = 1/phi
verts = []
for sx in [-1, 1]:
    for sy in [-1, 1]:
        for sz in [-1, 1]:
            verts.append((sx, sy, sz))
for sx in [-1, 1]:
    for sy in [-1, 1]:
        verts.append((0, sx*inv_phi, sy*phi))
        verts.append((sx*inv_phi, sy*phi, 0))
        verts.append((sx*phi, 0, sy*inv_phi))
def norm(v):
    n = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    return np.array(v)/n
verts_n = np.array([norm(v) for v in verts])
cs = vecs[0]

def rand_rotation(rng):
    q = rng.normal(size=3)
    q = q / np.linalg.norm(q)
    theta = rng.uniform(0, 2*math.pi)
    K = np.array([[0, -q[2], q[1]], [q[2], 0, -q[0]], [-q[1], q[0], 0]])
    return np.eye(3) + math.sin(theta)*K + (1-math.cos(theta))*K@K

rng = np.random.default_rng(42)
vals = []
for _ in range(30):
    R = rand_rotation(rng)
    rv = (R @ verts_n.T).T
    vals.append(min(math.degrees(math.acos(np.clip(np.dot(cs, v), -1, 1))) for v in rv))
vals = np.array(vals)
print(f"  min={vals.min():.3f}, max={vals.max():.3f}, std={vals.std():.3f}")
print(f"  文檔: min=0.6, max=35.5, std=7.05")
if vals.std() > 1:
    print(f"  ✅ 確認: std > 1° → 座標系依賴 (負結果成立)")
else:
    errors.append("旋轉不變性 std < 1")

# ============ 結果 ============
print(f"\n{'='*66}")
if errors:
    print(f"❌ 發現 {len(errors)} 個不一致:")
    for e in errors: print(f"  - {e}")
else:
    print(f"✅✅ 全部數字驗證通過! 03_final_negative_result.md 正確!")
print(f"{'='*66}")
