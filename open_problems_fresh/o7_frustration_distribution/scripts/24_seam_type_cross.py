#!/usr/bin/env python3
"""
O7 — 24_seam_type_cross.py (2026-10-11)
====================================================================
O7/natural-write-closure 第十輪: 縫合線 × 邊型 (3A/5A) 交叉
====================================================================
純 O7 問題: docs/10 發現邊差共軛類 = 面型 (三角=3A, 五邊=5A, 120/120)。
O7 核心 = 20 縫合線 (獨立 π 相位單位, 位元)。兩者交叉:

  S1. 每條縫合線嘅阻挫邊 → 3A/5A 型 — 單型縫合線? 混合?
  S2. 20 縫合線 ↔ 20△ 面 對應: 每條縫合線係咪對應唯一三角形面?
      (阻挫邊 20 條 3A = 20△面嘅「正邊」涉及? 12 條 5A = 12⬠?)
  S3. 縫合線對應面嘅 3A邊/5A邊 比例 vs 位元數量 (20 = 40/2?)

非 O7 攻堅 (O162 鏈嵌入負結果 / O143 混疊 / O220 瓶頸) 只交接, 唔喺度推。
"""

import numpy as np
from pathlib import Path
from itertools import combinations
from collections import Counter, defaultdict
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
print("  O7 — 縫合線 × 邊型 (3A/5A) 交叉 (S1-S3)")
print("=" * 76)

# ── 網絡 + 著色 + 群 ──
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
frust_set = set(tuple(sorted(e)) for e in frust)

# A₅ 重建 (O171 方法)
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

# 面型
edge_type = {}
tri_faces = []; pent_faces = []
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
print(f"  面: {len(tri_faces)}△ + {len(pent_faces)}⬠")

# ── 縫合線 (O7 20 位元) ──
def component(seed, edgeset):
    seen = {seed}; q = [seed]; comp = []
    while q:
        u = q.pop(); comp.append(u)
        for w in range(60):
            if w not in seen and (tuple(sorted((u, w)))) in edgeset:
                seen.add(w); q.append(w)
    return sorted(comp)

frust_nodes = [v for v in range(60) if sum(1 for e in frust if v in e) > 0]
seams = []
seen = set()
for s in frust_nodes:
    if s in seen: continue
    comp = component(s, frust_set)
    for x in comp: seen.add(x)
    seams.append(comp)
seam_edges = []
for comp in seams:
    se = [tuple(sorted((u, w))) for u in comp for w in comp if u < w and tuple(sorted((u, w))) in frust_set]
    seam_edges.append(se)
print(f"  縫合線: {len(seams)} 條 (位元數 = {len(seams)})")

# ═══ S1. 每條縫合線嘅邊型 ═══
print("\n─── S1. 縫合線 × 邊型 (3A/5A) ───")
type_seams = []
for si, se in enumerate(seam_edges):
    cls = [CLS_NAME[edge_cls(e)] for e in se]
    et = [edge_type.get(e, '?') for e in se]
    type_seams.append((cls, et))
    print(f"  seam {si:2d} ({len(se)}邊): 類 {'/'.join(cls):12s} 面型 {'/'.join(et)}")
allc = [c for cs, _ in type_seams for c in cs]
print(f"  全部縫合邊類分佈: {Counter(allc)}")
single = sum(1 for cs, _ in type_seams if len(set(cs)) == 1)
print(f"  單型縫合線: {single}/{len(seams)}")
check("S1a: 有單型縫合線 (位元有邊型身份)", single > 0, f"{single}")

# ═══ S2. 縫合線 ↔ 面 對應 ═══
print("\n─── S2. 每條縫合線嘅阻挫邊對應面 ───")
seam_face = []
for si, se in enumerate(seam_edges):
    faces_hit = set()
    for e in se:
        t = edge_type.get(e)
        if t == 'tri':
            for f in tri_faces:
                eset = {tuple(sorted((f[a], f[(a+1) % 3]))) for a in range(3)}
                if tuple(sorted(e)) in eset: faces_hit.add(('tri', tuple(sorted(f))))
        elif t == 'pent':
            for f in pent_faces:
                eset = {tuple(sorted((f[a], f[(a+1) % 5]))) for a in range(5)}
                if tuple(sorted(e)) in eset: faces_hit.add(('⬠', tuple(sorted(f))))
    seam_face.append(faces_hit)
# 3A 阻挫邊 = 20 條 (docs/10) — 佢哋對應 20△面?
tri_hit = set()
for si in range(len(seams)):
    for t, f in seam_face[si]:
        if t == 'tri': tri_hit.add(f)
print(f"  縫合線接觸嘅三角形面: {len(tri_hit)} (總 {len(tri_faces)})")
print(f"  縫合線接觸嘅五邊形面: {sum(1 for si in range(len(seams)) for t, f in seam_face[si] if t == '⬠')} 次")
check("S2a: 20 條縫合線接觸全部 20△ 面 (一一對應)", len(tri_hit) == 20, f"{len(tri_hit)}/20")

# ═══ S3. 位元數量 = 3A邊/2? ═══
print("\n─── S3. 阻挫邊型計數 vs 20 位元 ───")
frust_cls = Counter(CLS_NAME[edge_cls(e)] for e in frust)
print(f"  阻挫邊型: {dict(frust_cls)} (總 {sum(frust_cls.values())})")
print(f"  3A 阻挫邊 = 20 = 位元數? {frust_cls.get('3A', 0)} vs 20")
print(f"  5A 阻挫邊 = 12 = 五邊面數? {frust_cls.get('5A', 0)} vs 12")
check("S3a: 3A 阻挫邊 = 20 = 位元數", frust_cls.get('3A', 0) == 20, f"{frust_cls.get('3A', 0)}")
check("S3b: 5A 阻挫邊 = 12 = 五邊面數", frust_cls.get('5A', 0) == 12, f"{frust_cls.get('5A', 0)}")

# ═══ S4. 面級阻挫邊計數 (畢鴨巢: count=面數 + 全覆蓋 ⟹ 每面一條) ═══
print("\n─── S4. 每個 △/⬠ 面嘅阻挫邊數 ───")
frust_count_face = Counter()
for e in frust:
    es = tuple(sorted(e))
    t = edge_type.get(es)
    if t == 'tri':
        for f in tri_faces:
            eset = {tuple(sorted((f[a], f[(a+1) % 3]))) for a in range(3)}
            if es in eset:
                frust_count_face[('tri', tuple(sorted(f)))] += 1
    elif t == 'pent':
        for f in pent_faces:
            eset = {tuple(sorted((f[a], f[(a+1) % 5]))) for a in range(5)}
            if es in eset:
                frust_count_face[('⬠', tuple(sorted(f)))] += 1
tri_dist = Counter(c for (t, _), c in frust_count_face.items() if t == 'tri')
pent_dist = Counter(c for (t, _), c in frust_count_face.items() if t == '⬠')
print(f"  △面阻挫邊數分佈: {dict(tri_dist)}  (覆蓋 {sum(tri_dist.values())}/20)")
print(f"  ⬠面阻挫邊數分佈: {dict(pent_dist)}  (覆蓋 {sum(pent_dist.values())}/12)")
check("S4a: 每個△面剛好 1 條阻挫邊 (20×1)", sum(tri_dist.values()) == 20 and tri_dist.get(1, 0) == 20, f"{dict(tri_dist)}")
check("S4b: 每個⬠面剛好 1 條阻挫邊 (12×1)", sum(pent_dist.values()) == 12 and pent_dist.get(1, 0) == 12, f"{dict(pent_dist)}")

# ── 總結 ──
print("\n" + "=" * 76)
print(f"  結果: {sum(results)}/{len(results)} PASS")
print("=" * 76)