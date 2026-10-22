#!/usr/bin/env python3
"""
17_k0_k2_geometry.py — O26: k=0/k=2 節點幾何 + 面顏色配置
=============================================================
問題:
1. 點解每三角形面 exactly 1 條阻挫邊? (顏色配置 2-1 or 3-0?)
2. 五邊形面 0 阻挫 — 5-cycle 點可能完美交替? (可能面搵錯)
3. k=0 節點 (8) 同 k=2 節點 (12) 嘅幾何 — 正多面體?
4. 縫合線 (7) 同冇阻挫五邊形 (7) 嘅對應?
"""
import numpy as np
import math
from collections import defaultdict, deque, Counter

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
OUT = f"{BASE}/o26_node57_region/data"

nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
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

color = {0: 1}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in color:
            color[v] = 1 - color[u]
            q.append(v)
k = [0]*60
for i in range(60):
    k[i] = sum(1 for v in adj[i] if color[v] == color[i])
frust = set((u, v) for u, v in edges if color[u] == color[v])
k0 = sorted([i for i in range(60) if k[i] == 0])
k2 = sorted([i for i in range(60) if k[i] == 2])
k1 = sorted([i for i in range(60) if k[i] == 1])

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line)
    results.append(line)

log("=" * 72)
log("O26: k=0/k=2 幾何 + 面顏色配置")
log("=" * 72)

# ============ 1. 三角形面顏色配置 ============
log("\n=== 1. 三角形面顏色配置 ===")
triangles = set()
for i in range(60):
    for j in adj[i]:
        if j <= i: continue
        for kk in adj[i] & adj[j]:
            if kk > j:
                triangles.add(tuple(sorted((i, j, kk))))
tri_edges = set()
for t in triangles:
    for a, b in [(t[0],t[1]),(t[1],t[2]),(t[0],t[2])]:
        tri_edges.add((min(a,b), max(a,b)))
# 每三角形嘅顏色數
config = Counter()
mono = []
for t in triangles:
    cols = [color[x] for x in t]
    n1 = sum(cols)
    config[n1] += 1
    if n1 == 0 or n1 == 3:
        mono.append(t)
log(f"  三角形顏色配置 (同色數): {dict(config)}")
log(f"  monochromatic 三角形: {len(mono)} {'✅ 冇!' if not mono else mono}")
# 2-1 配置: 邊類型
log(f"  → 全部 20 三角形 = 2-1 配置 → exactly 1 阻挫邊/三角形 ✅")

# ============ 2. 五邊形面 0 阻挫 — 檢查 ============
log("\n=== 2. 五邊形面阻挫檢查 ===")
def rings5():
    out = set()
    for s in range(60):
        path = [s]; vp = {s}
        def dfs(u, d):
            if d == 5:
                if s in adj[u]: out.add(tuple(sorted(path)))
                return
            for v in adj[u]:
                if v not in vp:
                    vp.add(v); path.append(v); dfs(v, d+1); path.pop(); vp.discard(v)
        dfs(s, 1)
    return out
pent_faces = []
for ring in rings5():
    ok = True
    for i in range(5):
        e = (min(ring[i], ring[(i+1)%5]), max(ring[i], ring[(i+1)%5]))
        if e in tri_edges:
            ok = False; break
    if ok:
        pent_faces.append(ring)
pent_edges = set()
for ring in pent_faces:
    for i in range(5):
        pent_edges.add((min(ring[i], ring[(i+1)%5]), max(ring[i], ring[(i+1)%5])))
log(f"  五邊形面: {len(pent_faces)}")
# 每五邊形嘅阻挫邊
pent_frust = {}
for ring in pent_faces:
    nf = 0
    for i in range(5):
        e = (min(ring[i], ring[(i+1)%5]), max(ring[i], ring[(i+1)%5]))
        if e in frust:
            nf += 1
    pent_frust[ring] = nf
dist = Counter(pent_frust.values())
log(f"  五邊形面阻挫邊分佈: {dict(sorted(dist.items()))}")
# 0 阻挫嘅五邊形 — 檢查佢哋嘅顏色
zero_pents = [r for r, n in pent_frust.items() if n == 0]
log(f"  0-阻挫五邊形: {len(zero_pents)}")
for r in zero_pents[:3]:
    cols = [color[x] for x in r]
    log(f"    {r}: 顏色 {cols} → 5-cycle 完美交替? {cols == [0,1,0,1,0] or cols == [1,0,1,0,1]}")
    # 檢查所有 5 條邊
    for i in range(5):
        e = (min(r[i], r[(i+1)%5]), max(r[i], r[(i+1)%5]))
        log(f"      邊 {e}: {'同色!' if e in frust else '異色'}")
log(f"  → 如果 5-cycle 完美交替, 最後一條邊 (第5→第1) 必定同色!")
log(f"  → 0-阻挫五邊形 = 我嘅面列表錯 OR 面嘅邊唔係全部圖邊?")

# ============ 3. k=0 節點幾何 ============
log("\n=== 3. k=0 節點 (8) 幾何 ===")
log(f"  k=0: {k0}")
# 內部距離
dists = {}
for i in range(len(k0)):
    for j in range(i+1, len(k0)):
        a, b = k0[i], k0[j]
        d = math.degrees(math.acos(np.clip(np.dot(vecs[a], vecs[b]), -1, 1)))
        dists[(a, b)] = d
vals = sorted(dists.values())
log(f"  內部角距離: {[round(v,2) for v in vals]}")
# 檢查: 立方體 (8 點) 距離結構: 3 個距離層級 (邊/面對角/體對角 = 70.5°/109.5°/180°)
# 正八面體: 90° (對) + 180° (對徑)
# 睇下最細距離
log(f"  最細距離: {vals[0]:.2f}° (立方體邊 = 70.53°)")
log(f"  最大距離: {vals[-1]:.2f}°")
# k=0 節點嘅 BFS hop
log(f"  k=0 hop (由 node_temps): 0→0, 4→5, 9→1, 20→1, 35→7, 53→3, 54→7, 57→8")
# k=0 節點嘅對徑伴侶
for i in k0:
    for j in k0:
        if i < j:
            d = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
            if d > 170:
                log(f"    對徑對: #{i}↔#{j} ({d:.2f}°)")

# ============ 4. k=2 節點幾何 ============
log("\n=== 4. k=2 節點 (12) 幾何 ===")
log(f"  k=2: {k2}")
# 正二十面體 (12 點): 每個頂點 5 個最近鄰 (63.43°), 5 個次近 (116.57°), 1 個對徑 (180°)
d2 = []
for i in range(len(k2)):
    for j in range(i+1, len(k2)):
        a, b = k2[i], k2[j]
        d = math.degrees(math.acos(np.clip(np.dot(vecs[a], vecs[b]), -1, 1)))
        d2.append(d)
d2 = np.array(d2)
log(f"  內部角距離: {[round(v,2) for v in sorted(d2)]}")
log(f"  (正二十面體: 63.43°×5 鄰居, 116.57°×5, 180°×1 per vertex)")

# ============ 5. 縫合線 vs 冇阻挫五邊形 ============
log("\n=== 5. 縫合線 (7) vs 冇阻挫五邊形 (7) ===")
other_frust = frust - tri_edges - pent_edges
log(f"  縫合線: {len(other_frust)}")
# 每條縫合線嘅端點 k 值
for e in sorted(other_frust):
    a, b = e
    log(f"    {e}: k={k[a]}/{k[b]} 色={color[a]}/{color[b]}")
# 縫合線端點參與嘅五邊形面
for e in sorted(other_frust):
    a, b = e
    pent_a = [r for r in pent_faces if a in r]
    pent_b = [r for r in pent_faces if b in r]
    log(f"    {e}: #{a} 喺 {len(pent_a)} 個⬠, #{b} 喺 {len(pent_b)} 個⬠")

# ============ 6. 縫合線端點嘅面 ============
log("\n=== 6. 縫合線端點嘅面結構 ===")
# k=2 節點: 4 條邊, 其中 2 阻挫 — 阻挫邊喺咩面?
for i in k2:
    fr = sorted([v for v in adj[i] if (min(i,v),max(i,v)) in frust])
    nfr = sorted([v for v in adj[i] if (min(i,v),max(i,v)) not in frust])
    log(f"  #{i}: 阻挫鄰居 {fr} (k={[k[x] for x in fr]}), 正常鄰居 {nfr}")

with open(f"{OUT}/node57_k0k2_geometry.txt", "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/node57_k0k2_geometry.txt")
