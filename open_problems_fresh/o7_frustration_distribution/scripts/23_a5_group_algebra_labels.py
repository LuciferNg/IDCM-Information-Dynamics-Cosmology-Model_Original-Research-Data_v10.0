#!/usr/bin/env python3
"""
O7 — 23_a5_group_algebra_labels.py (2026-10-11)
====================================================================
O7/natural-write-closure 第九輪: A₅ 群代數標籤 — 88 透明邊結構
====================================================================
承接 docs/09 (88 中點 line graph 唔係鏈) + O171 (A₅ 自由作用於 60 頂點/120 邊):

  G1. 重建 A₅ (O171 方法: Gram 候選 → 60 個旋轉 + 頂點標籤 = 群元素)
  G2. 邊差分佈: 每條邊 (i,j) → d = g_i⁻¹g_j 嘅共軛類 (1A,2A,3A,5A,5B)
      — Cayley 測試: 若 120 邊 = Cayley(S), 邊差集中喺小集合
  G3. 透明 vs 阻挫邊差交叉表 — 88/32 喺群代數層面分唔分到?
  G4. G88 = (60 節點, 88 透明邊) 子圖: connected / 度分佈 / Euler 路徑
      — 「一條邊鏈掃描全部 88 透明邊」= 鏈結構隱藏線索
  G5. G32 同理 (32 阻挫邊)

方法重現 O171 scripts/02 (Gram 容差 1e-5, 點容差 5e-3 rad) — 唔 import。
"""

import numpy as np
from pathlib import Path
from itertools import combinations
from collections import Counter, defaultdict

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = ROOT / "cmb_cold_spot/data"
GRAM_TOL = 1e-5
PT_TOL = 5e-3

results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

print("=" * 76)
print("  O7 — A₅ 群代數標籤: 88 透明邊結構 (G1-G5)")
print("=" * 76)

# ── 1. 網絡 ──
nodes = np.loadtxt(DATA / "a5_nodes.txt")
ra, dec = np.radians(nodes[:, 0]), np.radians(nodes[:, 1])
V = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
col = {}
for line in (DATA / "anchored_coloring.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split(); col[int(p[0])] = int(p[3])
color = np.array([col[i] for i in range(60)])
G_gram = V @ V.T
dist = np.arccos(np.clip(G_gram, -1, 1))
edges = [(i, j) for i in range(60) for j in range(i+1, 60) if dist[i, j] < np.radians(28.0)]
transp = [(i, j) for (i, j) in edges if color[i] != color[j]]
frust = [(i, j) for (i, j) in edges if color[i] == color[j]]
print(f"  網絡: {len(edges)} 邊 (透明 {len(transp)} / 阻挫 {len(frust)})")
check("G1a: 120 邊, 88+32", len(edges) == 120 and len(transp) == 88 and len(frust) == 32)

# ── 2. 重建 A₅ (O171 方法) ──
ref = [0, 1, 2]
Gr = np.array([[G_gram[a, b] for b in ref] for a in ref])
cand = []
for a, b, c in combinations(range(60), 3):
    for p in [(a, b, c), (a, c, b), (b, a, c), (b, c, a), (c, a, b), (c, b, a)]:
        if (abs(G_gram[p[0], p[1]] - Gr[0, 1]) < GRAM_TOL and abs(G_gram[p[0], p[2]] - Gr[0, 2]) < GRAM_TOL
                and abs(G_gram[p[1], p[2]] - Gr[1, 2]) < GRAM_TOL):
            cand.append(p)
A_ref_inv = np.linalg.inv(V[ref].T)
group = []; seen_keys = set()
for p in cand:
    M = V[list(p)].T @ A_ref_inv
    if not np.allclose(M @ M.T, np.eye(3), atol=1e-3): continue
    W = V @ M.T
    D = np.arccos(np.clip(W @ V.T, -1, 1))
    perm = np.argmin(D, axis=1)
    if D[np.arange(60), perm].max() > PT_TOL or len(set(perm.tolist())) != 60: continue
    key = tuple(np.round(M.ravel(), 5))
    if key in seen_keys: continue
    seen_keys.add(key); group.append((M, perm, float(np.linalg.det(M))))
rots = [(M, p, d) for (M, p, d) in group if d > 0.5]
print(f"  重建旋轉群: {len(rots)} 元素")
check("G1b: 60 個 A₅ 元素", len(rots) == 60)

# ── 3. 頂點標籤: 每個頂點 i ↔ 群元素 g_i ──
# 揀 v0 = 0 做中性元 e; g_i = 令 g·v0 = v_i 嘅唯一 A₅ 元素
label = [None]*60
for M, p, d in rots:
    label[int(p[0])] = M  # p[0] = 元素作用後嘅 v0 影像
assert all(label[i] is not None for i in range(60))
print("  頂點標籤: 60 個頂點 ↔ 60 個 A₅ 元素 (自由作用 bijection)")
check("G1c: 標籤 bijection (每頂點有唯一群元素)", all(label[i] is not None for i in range(60)))

# ── 4. 邊差分佈: d_ij = g_i⁻¹ g_j 嘅共軛類 ──
phi = (1+np.sqrt(5))/2; psi = (1-np.sqrt(5))/2
TRACES = [3.0, -1.0, 0.0, float(phi), float(psi)]
CLS_NAME = ['1A', '2A', '3A', '5A', '5B']
def dclass(A):
    t = float(np.trace(A))
    ds = [abs(t-v) for v in TRACES]
    return int(np.argmin(ds))

def edge_diffs(elist):
    c = Counter()
    vals = defaultdict(list)
    for (i, j) in elist:
        d = label[i].T @ label[j]
        k = dclass(d)
        c[k] += 1
        vals[k].append((i, j))
    return c, vals

print("\n─── G2. 邊差共軛類分佈 (Cayley 測試) ───")
c_all, v_all = edge_diffs(edges)
c_tr, v_tr = edge_diffs(transp)
c_fr, v_fr = edge_diffs(frust)
print(f"  全部 120 邊: " + " ".join(f"{CLS_NAME[k]}={c_all.get(k,0)}" for k in range(5)))
print(f"  透明 88 邊:  " + " ".join(f"{CLS_NAME[k]}={c_tr.get(k,0)}" for k in range(5)))
print(f"  阻挫 32 邊:  " + " ".join(f"{CLS_NAME[k]}={c_fr.get(k,0)}" for k in range(5)))
# Cayley 測試: 若 120 邊係 Cayley(S), 每頂點 4 條邊只有 2 個生成元 → 邊差集中
n_distinct = len(set(tuple(np.round((label[i].T @ label[j]).ravel(), 6)) for (i, j) in edges))
print(f"  120 邊嘅相異邊差數: {n_distinct} (Cayley 生成集 S 預期 ≤4)")
check("G2a: 邊差唔係 Cayley 小集合 (相異差 > 4)", n_distinct > 4)

# ── 5. 交叉表: 透明 vs 阻挫 嘅共軛類 ──
print("\n─── G3. 透明/阻挫 × 共軛類 交叉 ───")
tbl = np.zeros((2, 5), int)
for k in range(5):
    tbl[0, k] = c_tr.get(k, 0)
    tbl[1, k] = c_fr.get(k, 0)
for r, name in [(0, "透明"), (1, "阻挫")]:
    print(f"  {name}: " + " ".join(f"{CLS_NAME[k]}={tbl[r,k]}" for k in range(5)))
# 透明 88 邊成份: 睇吓係咪冚冚跨類但集中
check("G3a: 透明邊嘅類分佈唔係全 5 類 (集中)", sum(1 for k in range(5) if tbl[0, k] > 0) <= 4)

# ── 6. G88 子圖結構 ──
print("\n─── G4. G88 = (60 節點, 88 透明邊) 子圖 ───")
deg88 = defaultdict(int)
for (i, j) in transp:
    deg88[i] += 1; deg88[j] += 1
dhist = Counter(deg88.values())
print(f"  度分佈: {sorted(dhist.items())} (頂點度>0: {len(deg88)})")
# connected?
adj88 = defaultdict(set)
for (i, j) in transp:
    adj88[i].add(j); adj88[j].add(i)
seen = {0}; stack = [0]
while stack:
    u = stack.pop()
    for w in adj88[u]:
        if w not in seen: seen.add(w); stack.append(w)
print(f"  connected（由 0 出發）: {len(seen)}/60 頂點")
check("G4a: G88 connected", len(seen) == 60, f"{len(seen)}/60")
# Euler 路徑: 0 或 2 個奇度頂點
odd = [v for v, d in deg88.items() if d % 2 == 1]
print(f"  奇度頂點數: {len(odd)} (Euler 路徑需 0 或 2)")
check("G4b: G88 有 Euler 路徑 (奇度 ≤2)", len(odd) <= 2, f"奇度={len(odd)}")

# ── 7. G32 子圖結構 ──
print("\n─── G5. G32 = (60 節點, 32 阻挫邊) 子圖 ───")
deg32 = defaultdict(int)
for (i, j) in frust:
    deg32[i] += 1; deg32[j] += 1
dhist32 = Counter(deg32.values())
print(f"  度分佈: {sorted(dhist32.items())} (頂點度>0: {len(deg32)})")
adj32 = defaultdict(set)
for (i, j) in frust:
    adj32[i].add(j); adj32[j].add(i)
seen32 = {0}
if deg32.get(0, 0) > 0:
    stack = [0]
    while stack:
        u = stack.pop()
        for w in adj32[u]:
            if w not in seen32: seen32.add(w); stack.append(w)
print(f"  connected（由 0 出發）: {len(seen32)}/60 頂點")
odd32 = [v for v, d in deg32.items() if d % 2 == 1]
print(f"  奇度頂點數: {len(odd32)} (Euler 路徑需 0 或 2)")
check("G5a: G32 有 Euler 路徑", len(odd32) <= 2, f"奇度={len(odd32)}")

# ── 8. G6: 面邊類型 × 共軛類 交叉 (三角形邊=3A? 五邊形邊=5A?) ──
print("\n─── G6. 面邊類型 × 邊差共軛類 (60△邊+60⬠邊 = 120?) ───")
edge_type = {}  # (i,j) -> 'tri' | 'pent'
for line in (DATA / "faces.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    import re
    mm = re.search(r"\[([^\]]+)\]", line)
    vs = [int(x) for x in mm.group(1).split(',')]
    if len(vs) == 3:
        for a in range(3):
            e = tuple(sorted((vs[a], vs[(a+1) % 3])))
            edge_type[e] = edge_type.get(e, 'tri')
    elif len(vs) == 5:
        for a in range(5):
            e = tuple(sorted((vs[a], vs[(a+1) % 5])))
            edge_type[e] = edge_type.get(e, 'pent')
ntri = sum(1 for t in edge_type.values() if t == 'tri')
npent = sum(1 for t in edge_type.values() if t == 'pent')
print(f"  faces 邊分類: 三角 {ntri} / 五邊 {npent} (總 {len(edge_type)})")
# 每個面型嘅邊 → 共軛類
tbl_tp = np.zeros((2, 5), int)  # row: tri/pent, col: class
mismatch = []
for (i, j) in edges:
    e = tuple(sorted((i, j)))
    t = edge_type.get(e)
    k = dclass(label[i].T @ label[j])
    if t is not None:
        tbl_tp[0 if t == 'tri' else 1, k] += 1
        if (t == 'tri' and k != 2) or (t == 'pent' and k != 3):
            mismatch.append((e, t, CLS_NAME[k]))
    else:
        mismatch.append((e, '?', CLS_NAME[k]))
print(f"  三角邊: " + " ".join(f"{CLS_NAME[k]}={tbl_tp[0,k]}" for k in range(5)))
print(f"  五邊邊: " + " ".join(f"{CLS_NAME[k]}={tbl_tp[1,k]}" for k in range(5)))
print(f"  唔匹配 (型↔類): {len(mismatch)} — 首 5: {mismatch[:5]}")
check("G6a: 三角形面邊全部 = 3A (60/60)", tbl_tp[0, 2] == 60 and tbl_tp[0].sum() == 60, f"3A={tbl_tp[0,2]}")
check("G6b: 五邊形面邊全部 = 5A (60/60)", tbl_tp[1, 3] == 60 and tbl_tp[1].sum() == 60, f"5A={tbl_tp[1,3]}")
# 透明/阻挫 × 面型
print("\n─── G7. 透明/阻挫 × 面型 ───")
tbl_tp2 = np.zeros((2, 2), int)  # row: 透明/阻挫, col: tri/pent
for (i, j) in transp:
    e = tuple(sorted((i, j)))
    t = edge_type.get(e)
    if t == 'tri': tbl_tp2[0, 0] += 1
    elif t == 'pent': tbl_tp2[0, 1] += 1
for (i, j) in frust:
    e = tuple(sorted((i, j)))
    t = edge_type.get(e)
    if t == 'tri': tbl_tp2[1, 0] += 1
    elif t == 'pent': tbl_tp2[1, 1] += 1
print(f"  透明 88: 三角 {tbl_tp2[0,0]} / 五邊 {tbl_tp2[0,1]}")
print(f"  阻挫 32: 三角 {tbl_tp2[1,0]} / 五邊 {tbl_tp2[1,1]}")
print(f"  (期望若 3A:5A 全局 1:1 → 透明 44:44, 阻挫 16:16)")

# ── 總結 ──
print("\n" + "=" * 76)
print(f"  結果: {sum(results)}/{len(results)} PASS")
print("=" * 76)