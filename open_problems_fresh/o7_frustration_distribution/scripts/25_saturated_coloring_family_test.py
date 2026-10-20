#!/usr/bin/env python3
"""
O7 — 25_saturated_coloring_family_test.py (2026-10-11)
====================================================================
O7/natural-write-closure 第十一輪: 30 飽和著色家族 — 面級阻挫定理通用性
====================================================================
docs/11 面級阻挫定理 (每奇面 1 邊) 只喺錨定著色證實。O159/O143 有
30 個相異飽和著色 (BFS 家族)。本輪:

  F1. BFS 著色家族生成 (60 根 → 相異 30) + 驗證全部 32 阻挫邊
  F2. 面級定理 30/30? — △{1:20} ⬠{1:12} 係咪每個著色都成立
  F3. 阻挫邊型計數 3A/5A 係咪家族不變 (20/12)?
  F4. 縫合線數 + 單型比例家族分佈 — 錨定 10/20 單型係咪典型?
  F5. 縫合線 ↔ △面 bijection 30/30?
"""

import numpy as np
from pathlib import Path
from itertools import combinations
from collections import Counter, defaultdict, deque
import re

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = ROOT / "cmb_cold_spot/data"
GRAM_TOL = 1e-5
PT_TOL = 5e-3

results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

print("=" * 76)
print("  O7 — 30 飽和著色家族: 面級定理通用性 (F1-F5)")
print("=" * 76)

# ── 網絡 ──
nodes = np.loadtxt(DATA / "a5_nodes.txt")
ra, dec = np.radians(nodes[:, 0]), np.radians(nodes[:, 1])
V = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
G_gram = V @ V.T
dist = np.arccos(np.clip(G_gram, -1, 1))
edges = [(i, j) for i in range(60) for j in range(i+1, 60) if dist[i, j] < np.radians(28.0)]
adj = defaultdict(set)
for (i, j) in edges:
    adj[i].add(j); adj[j].add(i)

col0 = {}
for line in (DATA / "anchored_coloring.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split(); col0[int(p[0])] = int(p[3])
anchored = np.array([col0[i] for i in range(60)])

# 面
tri_faces = []; pent_faces = []
edge_type = {}
for line in (DATA / "faces.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    mm = re.search(r"\[([^\]]+)\]", line)
    vs = [int(x) for x in mm.group(1).split(',')]
    if len(vs) == 3:
        tri_faces.append(vs)
        for a in range(3):
            e = tuple(sorted((vs[a], vs[(a+1) % 3])))
            edge_type[e] = edge_type.get(e, 'tri')
    elif len(vs) == 5:
        pent_faces.append(vs)
        for a in range(5):
            e = tuple(sorted((vs[a], vs[(a+1) % 5])))
            edge_type[e] = edge_type.get(e, 'pent')

def face_type(e):
    return edge_type.get(tuple(sorted(e)))

def seams_of(frust_set):
    """縫合線 (阻挫邊 components)"""
    fn = [v for v in range(60) if sum(1 for e in frust_set if v in e) > 0]
    seen = set(); seams = []
    for s in fn:
        if s in seen: continue
        comp = []; q = deque([s]); seen.add(s)
        while q:
            u = q.popleft(); comp.append(u)
            for w in adj[u]:
                if w not in seen and tuple(sorted((u, w))) in frust_set:
                    seen.add(w); q.append(w)
        seams.append(sorted(comp))
    return seams

# ── A₅ 重建 (邊型用) ──
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
label = [None]*60
for M, p, d in rots:
    label[int(p[0])] = M
assert all(label[i] is not None for i in range(60))
phi = (1+np.sqrt(5))/2; psi = (1-np.sqrt(5))/2
TRACES = [3.0, -1.0, 0.0, float(phi), float(psi)]
CLS_NAME = ['1A', '2A', '3A', '5A', '5B']
def dclass(A):
    t = float(np.trace(A))
    ds = [abs(t-v) for v in TRACES]
    return int(np.argmin(ds))
def edge_cls(e):
    i, j = e
    return dclass(label[i].T @ label[j])

# ── F1. BFS 著色家族 ──
print("\n─── F1. BFS 著色家族生成 ───")
def bfs_coloring(root):
    c = {root: 0}; q = deque([root])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if w not in c:
                c[w] = 1 - c[u]; q.append(w)
    return np.array([c[i] for i in range(60)])

fam = []
seen_f = set()
for r in range(60):
    c = bfs_coloring(r)
    key = tuple(c.tolist())
    inv = tuple((1 - c).tolist())
    if key in seen_f or inv in seen_f: continue
    seen_f.add(key); seen_f.add(inv)
    fam.append(c)
print(f"  相異著色家族: {len(fam)}")
check("F1a: 家族數 = 30", len(fam) == 30, f"{len(fam)}")

fam_frust = []
ok32 = 0
for fi, c in enumerate(fam):
    fs = set()
    for (i, j) in edges:
        if c[i] == c[j]: fs.add((i, j))
    fam_frust.append(fs)
    if len(fs) == 32: ok32 += 1
print(f"  32 阻挫邊家族: {ok32}/30")
check("F1b: 全部家族 32 阻挫邊 (飽和)", ok32 == 30, f"{ok32}")

# ── F2. 面級定理 30/30 ──
print("\n─── F2. 面級定理 (每奇面 1 邊) 家族通用?? ───")
tri_ok = 0; pent_ok = 0
face_fam = []
for fi, fs in enumerate(fam_frust):
    tc = Counter(); pc = Counter()
    for e in fs:
        t = face_type(e)
        if t == 'tri':
            for f in tri_faces:
                eset = {tuple(sorted((f[a], f[(a+1) % 3]))) for a in range(3)}
                if tuple(sorted(e)) in eset: tc[tuple(sorted(f))] += 1
        elif t == 'pent':
            for f in pent_faces:
                eset = {tuple(sorted((f[a], f[(a+1) % 5]))) for a in range(5)}
                if tuple(sorted(e)) in eset: pc[tuple(sorted(f))] += 1
    face_fam.append((tc, pc))
    if sum(tc.values()) == 20 and all(v == 1 for v in tc.values()): tri_ok += 1
    if sum(pc.values()) == 12 and all(v == 1 for v in pc.values()): pent_ok += 1
print(f"  △每面1邊: {tri_ok}/30;  ⬠每面1邊: {pent_ok}/30")
check("F2a: 面級定理全家族成立 (△ 30/30)", tri_ok == 30, f"{tri_ok}")
check("F2b: 面級定理全家族成立 (⬠ 30/30)", pent_ok == 30, f"{pent_ok}")

# ── F3. 邊型計數家族不變? ──
print("\n─── F3. 3A/5A 阻挫邊計數家族分佈 ───")
cls_counts = Counter()
for fs in fam_frust:
    c3a = sum(1 for e in fs if CLS_NAME[edge_cls(e)] == '3A')
    c5a = sum(1 for e in fs if CLS_NAME[edge_cls(e)] == '5A')
    cls_counts[(c3a, c5a)] += 1
print(f"  (3A,5A) 分佈: {dict(cls_counts)}")
check("F3a: 3A/5A = 20/12 家族不變", all(k == (20, 12) for k in cls_counts), f"{dict(cls_counts)}")

# ── F4. 縫合線數 + 單型比例家族分佈 ──
print("\n─── F4. 縫合線數/單型比例家族分佈 ───")
seam_stats = []
for fs in fam_frust:
    ss = seams_of(fs)
    types = []
    for comp in ss:
        se = [tuple(sorted((u, w))) for u in comp for w in comp if u < w and tuple(sorted((u, w))) in fs]
        ts = {CLS_NAME[edge_cls(e)] for e in se}
        types.append(len(ts) == 1)
    seam_stats.append((len(ss), sum(types)))
print(f"  (縫合線數, 單型數) 分佈: {Counter(seam_stats)}")
anch = (20, 10)
print(f"  錨定著色: (20, 10)")
mostly = sum(1 for n, s in seam_stats if n == 20)
check("F4a: 縫合線數=20 普遍 (家族不變)", mostly == 30, f"{mostly}/30")

# ── F5. 縫合線 ↔ △面 bijection 家族 ──
print("\n─── F5. 縫合線 ↔ △面 bijection 家族通用?? ───")
bio_ok = 0
for fi, (fs, (tc, pc)) in enumerate(zip(fam_frust, face_fam)):
    ss = seams_of(fs)
    tri_hit = set()
    for comp in ss:
        for u in comp:
            for w in comp:
                e = tuple(sorted((u, w)))
                if e in fs and face_type(e) == 'tri':
                    for f in tri_faces:
                        eset = {tuple(sorted((f[a], f[(a+1) % 3]))) for a in range(3)}
                        if e in eset: tri_hit.add(tuple(sorted(f)))
    if len(tri_hit) == 20 and len(ss) == 20: bio_ok += 1
print(f"  縫合線20 + △20覆蓋: {bio_ok}/30")
check("F5a: 縫合線↔△ bijection 家族通用", bio_ok == 30, f"{bio_ok}")

# ── 總結 ──
print("\n" + "=" * 76)
print(f"  結果: {sum(results)}/{len(results)} PASS")
print("=" * 76)