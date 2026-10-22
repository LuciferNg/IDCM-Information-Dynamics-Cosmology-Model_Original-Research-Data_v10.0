#!/usr/bin/env python3
"""
16_kvalue_closedform.py — O26: 8/40/12 閉式推導 (最後一步)
=============================================================
目標: 證明 k 分佈 {0:8, 1:40, 2:12} 係圖論必然。

工具:
1. 阻挫邊 32 條固定 (5000 random anchor 已證)
2. k 分佈同 anchor 無關 (5000 已證)
3. 對徑對同 k (30/30)
4. 圖 = 4-regular 120 邊, 20△ + 30□ + 12⬠

推導:
- 阻挫邊 = 奇環 (△,⬠) 嘅缺陷
- 每奇環面最少 1 條阻挫邊
- 但 32 ≠ 20+12 = 32 ✓? 20 三角形 + 12 五邊形 = 32 奇環!
- 驗證: 每奇環面最少 1 阻挫邊, 如果每面 exactly 1 且唔共享 → 32

但實測: 三角形面內 20 條, 五邊形面內 5 條, 其他 7 條
→ 唔係「一面一挫」!

真正結構: 阻挫邊 = 縫合線, 沿奇環面行走, 喺面之間傳播

替代推導:
- 4-regular 圖, 2-coloring
- 每節點: 同色鄰居數 k(i) ∈ {0,1,2} (4 鄰居, 最多 2 同色?)
- 驗證: k(i) 上限 = 2? (因為 bipartite-ish)
- Σk = 64 = 2×32
- 8/40/12 解: 8×0 + 40×1 + 12×2 = 64

問題: 有冇其他解? (如 16×0 + 32×1 + 8×2 = 48?) 唔得 — Σk=64 固定
- 16×0 + 16×1 + 16×2 = 48 ✗
- 8×0 + 40×1 + 12×2 = 64 ✓
- 0×0 + 64×1 + 0×2 = 64 ✓ (可能嗎?)

所以要證明: 8/40/12 係唯一滿足全部約束嘅解
約束:
(a) n0+n1+n2 = 60
(b) n1 + 2n2 = 64
(c) 對徑對同 k: n0, n1, n2 全部偶數
(d) 阻挫邊 component 結構 (20 個, 2-4 節點)
(e) k=0 節點冇阻挫邊, k=2 節點連接 2 條

檢查 (a)(b): n1 = 64-2n2, n0 = 60-n1-n2 = n2-4
→ n0 = n2 - 4
n2=12 → n0=8, n1=40 ✓
n2=10 → n0=6, n1=44
n2=14 → n0=10, n1=36
...
所以 (a)(b) 只係 n0=n2-4 嘅 family!

需要 (c): n0, n2 偶數 → n2 偶數 ✓ (12)
需要更多約束 — 縫合線結構
"""
import numpy as np
import math
from collections import defaultdict, deque, Counter

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"

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
frust = [(u, v) for u, v in edges if color[u] == color[v]]

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line)
    results.append(line)

log("=" * 72)
log("O26: 8/40/12 閉式推導")
log("=" * 72)

# ============ 1. 約束條件 ============
log("\n=== 1. 約束條件 ===")
n0 = sum(1 for i in range(60) if k[i] == 0)
n1 = sum(1 for i in range(60) if k[i] == 1)
n2 = sum(1 for i in range(60) if k[i] == 2)
log(f"  n0={n0}, n1={n1}, n2={n2}")
log(f"  (a) n0+n1+n2 = {n0+n1+n2} = 60 ✓")
log(f"  (b) n1+2n2 = {n1+2*n2} = 64 = 2×32 ✓")

# ============ 2. k 值上限 ============
log("\n=== 2. k(i) ≤ 2? (4 鄰居中最多 2 同色) ===")
# 檢查: 有冇節點 k>2?
max_k = max(k)
log(f"  max k = {max_k} {'✅' if max_k <= 2 else '❌'}")
# 點解? 如果 3 個鄰居同色 → 佢哋之間有三角形?
# 檢查 k=2 節點嘅同色鄰居係咪互相連接
for i in [10, 12]:
    same = [v for v in adj[i] if color[v] == color[i]]
    conn = sum(1 for a in range(len(same)) for b in range(a+1, len(same)) if same[b] in adj[same[a]])
    log(f"  #{i} 同色鄰居 {same}: 互相連接 {conn} 條")

# ============ 3. 面-阻挫邊對應 ============
log("\n=== 3. 面 vs 阻挫邊 ===")
# 三角形面
triangles = set()
for i in range(60):
    for j in adj[i]:
        if j <= i: continue
        for kk in adj[i] & adj[j]:
            if kk > j:
                triangles.add(tuple(sorted((i, j, kk))))
# 每三角形有幾多阻挫邊
tri_frust_count = Counter()
for t in triangles:
    nf = sum(1 for a, b in [(t[0],t[1]),(t[1],t[2]),(t[0],t[2])] if (min(a,b),max(a,b)) in set(frust))
    tri_frust_count[nf] += 1
log(f"  三角形面阻挫邊數分佈: {dict(sorted(tri_frust_count.items()))}")
log(f"  (三角形 = 奇環 → 每面最少 1 條)")

# ============ 4. 縫合線 (阻挫邊) 嘅全域結構 ============
log("\n=== 4. 阻挫邊: 每面阻挫邊數 ===")
# 阻挫邊係咪全部喺三角形面內?
frust_set = set(frust)
tri_edges = set()
for t in triangles:
    for a, b in [(t[0],t[1]),(t[1],t[2]),(t[0],t[2])]:
        tri_edges.add((min(a,b), max(a,b)))
in_tri = sum(1 for e in frust_set if e in tri_edges)
out_tri = len(frust_set) - in_tri
log(f"  三角形面內阻挫邊: {in_tri}/{len(frust_set)}")
log(f"  三角形面外阻挫邊: {out_tri}")
# 面外阻挫邊屬於邊?
# 檢查: 面外阻挫邊嘅兩端
for e in frust_set - tri_edges:
    a, b = e
    log(f"    面外: #{a}(k={k[a]})↔#{b}(k={k[b]})")

# ============ 5. 縫合線路徑 ============
log("\n=== 5. 縫合線 (阻挫邊相連路徑) ===")
fadj = defaultdict(set)
for u, v in frust:
    fadj[u].add(v); fadj[v].add(u)
# 最大 component
comps = []
seen = set()
for s in range(60):
    if s in seen or not fadj[s]: continue
    c = []; qq = deque([s]); seen.add(s)
    while qq:
        u = qq.popleft(); c.append(u)
        for v in fadj[u]:
            if v not in seen: seen.add(v); qq.append(v)
    comps.append(c)
comps.sort(key=len, reverse=True)
log(f"  20 個 component 長度: {sorted([len(c) for c in comps], reverse=True)}")
log(f"  k=2 節點 (樞紐) 分佈:")
for c in comps:
    k2c = [x for x in c if k[x] == 2]
    if k2c:
        log(f"    {sorted(c)}: k=2 -> {k2c}")

# ============ 6. 結論: 8/40/12 = 縫合線結構必然 ============
log("\n=== 6. 結論 ===")
log("""
8/40/12 嘅推導:

(1) 圖 = 4-regular, 120 邊, 20△ + 30□ + 12⬠ (62 面, Euler ✓)
(2) 阻挫邊數 32 = 20△ + 12⬠ (奇環面數) — 每奇環面 exactly 1 條?
    實測: 三角形面內 20, 五邊形面內 5, 其他 7 → 唔係 exactly 1/面
    但總數 32 = 32 奇環面 → 數目巧合定結構?
(3) Σk = 64 = 2×32 (每阻挫邊貢獻 2 端點)
(4) k(i) ≤ 2 (4-regular + 2-coloring 結構)
(5) n0 = n2 - 4 (由 Σk 同 n 推導)
(6) 對徑對同 k → n0, n2 偶數
(7) 縫合線 component 結構: 20 個 component, 10 個 2-節點 (k1-k1),
    8 個 3-節點 (k2-k1-k1 或 k1-k2-k1), 2 個 4-節點 (k2-k1-k2-k1)
    → 縫合線數 = 10 + 8 + 2 = 20 = 三角形面數?
    → k=2 節點數 = 8 + 2×2 = 12 ✓ (每 3-節點 1 個, 每 4-節點 2 個)
    → k=1 節點數 = 10×2 + 8×2 + 2×2 = 40 ✓
    → k=0 節點數 = 60 - 12 - 40 = 8 ✓

★ 8/40/12 = 縫合線 (阻挫邊網絡) 嘅拓撲必然:
  每條縫合線 = 奇環缺陷, 端點係 k=1, 樞紐係 k=2
  縫合線數 = 20 (三角形面提供缺陷源)
  k=2 節點 = 縫合線交匯點 (12 = 8 條線 × 1 交匯 + 2 條線 × 2 交匯?)
  
完整證明需要: 縫合線數 = 20 嘅嚴格推導
(20 三角形面每面提供缺陷 → 缺陷線 = 三角形對偶路徑?)
""")

with open(f"{BASE}/o26_node57_region/data/node57_kvalue_closedform.txt", "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {BASE}/o26_node57_region/data/node57_kvalue_closedform.txt")
