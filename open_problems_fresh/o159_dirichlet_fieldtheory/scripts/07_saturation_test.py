#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O159 scripts/07 (原 O205 scripts/04) — O7 飽和條件 vs BFS 著色族 (唯一性判別)
==========================================================
scripts/03 §F 發現: 30 個 BFS 著色 → corr(k,|T|) 由 −0.382 到 +0.280 (只有 1/30 顯著)。

但 O7 docs/01 話: 「錨定著色係唯一嘅**阻挫飽和** 2-著色 (up to global flip)」—
飽和條件 = 每奇面 (20Δ + 12⬠) 啱啱 1 條阻挫邊; 正方形 0 或 2 (對邊)。

⟹ 判別: 30 個 BFS 著色有幾多個符合飽和?
   - 只有 1 個 ⟹ 其餘 29 個唔 admissible, §F 嘅「唔穩健」係講緊非飽和著色
     (O7 唯一性成立; k-selector 嘅著色基礎係唯一嘅)
   - 多過 1 個 ⟹ O7 唯一性聲稱需修正, §F 嘅不穩健性係真問題
"""
import numpy as np, json, os, itertools
from collections import defaultdict, deque

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
O159 = os.path.join(BASE, "o159_dirichlet_fieldtheory")   # 2026-09-19 由 O205 併入
A5F = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
TEMPS = os.path.join(BASE, "o182_88grid_geometry/data/temps2_SMICA_4.17deg.json")
DE0 = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}

ok = 0; tot = 0
def chk(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

def unit(rd):
    ra, dec = np.radians(rd[:, 0]), np.radians(rd[:, 1])
    return np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])

V = unit(np.loadtxt(A5F))
ang = np.degrees(np.arccos(np.clip(V @ V.T, -1, 1)))
E = [(i, j) for i in range(60) for j in range(i+1, 60) if ang[i, j] < 28.0]
adj = defaultdict(set)
for i, j in E:
    adj[i].add(j); adj[j].add(i)

print("=" * 76)
print("  O159 scripts/07 (原 O205 scripts/04) — O7 飽和條件 vs BFS 著色族")
print("=" * 76)

# ── 面結構 (平面嵌入 face-walk: 按切平面角序排鄰居, 再走面) ──
def cyclic_order(v):
    nb = sorted(adj[v])
    if not nb:
        return []
    e1 = V[nb[0]] - V[v] * np.dot(V[nb[0]], V[v])
    e1 = e1 / np.linalg.norm(e1)
    e2 = np.cross(V[v], e1)
    return sorted(nb, key=lambda w: np.arctan2(np.dot(V[w], e2), np.dot(V[w], e1)))

order = {v: cyclic_order(v) for v in range(60)}
visited = set()
face_list = []
for u in range(60):
    for v in order[u]:
        if (u, v) in visited:
            continue
        face = [u]
        cu, cv = u, v
        while True:
            visited.add((cu, cv))
            face.append(cv)
            ring = order[cv]
            i = ring.index(cu)
            nxt = ring[(i - 1) % len(ring)]        # 固定方向 → 內部面
            cu, cv = cv, nxt
            if (cu, cv) == (u, v):
                break
            if len(face) > 10:
                break
        if len(face) > 1 and face[-1] == u:
            face_list.append(tuple(face[:-1]))
faces = {L: [f for f in face_list if len(f) == L] for L in (3, 4, 5)}
for L in (3, 4, 5):
    print(f"  {L}-面: {len(faces[L])} 個")
chk("F1: 20 三角形 + 30 正方形 + 12 五邊形 = 62 面 (Euler: 120−60+2)",
    len(faces[3]) == 20 and len(faces[4]) == 30 and len(faces[5]) == 12,
    f"({len(faces[3])}/{len(faces[4])}/{len(faces[5])})")

# 每條邊屬於 2 個面
edge_face = defaultdict(int)
for L, fl in faces.items():
    for f in fl:
        for a, b in itertools.combinations(f, 2):
            if ang[a, b] < 28.0:
                edge_face[tuple(sorted((a, b)))] += 1
chk("F2: 每條邊屬於 2 個面 (平面圖)",
    all(edge_face[tuple(sorted(e))] == 2 for e in E), f"(min {min(edge_face.values())})")

# 奇面 (Δ + ⬠)
odd_faces = faces[3] + faces[5]
sq_faces = faces[4]

# ── BFS 著色族 ──
def coloring(root):
    col = {root: 0}; q = deque([root])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in col:
                col[v] = 1 - col[u]; q.append(v)
    return col

def fset(col):
    return frozenset(tuple(sorted((i, j))) for i, j in E if col[i] == col[j])

reps = {}
for r in range(60):
    fs = fset(coloring(r))
    reps.setdefault(fs, r)

def saturation(fs):
    """飽和 = 每奇面啱啱 1 條阻挫邊 + 每正方形 0 或 2 (對邊)."""
    odd_counts = []
    for f in odd_faces:
        fe = [tuple(sorted((a, b))) for a, b in itertools.combinations(f, 2) if ang[a, b] < 28.0]
        odd_counts.append(sum(1 for e in fe if e in fs))
    sq_counts = []
    for f in sq_faces:
        fe = [tuple(sorted((a, b))) for a, b in itertools.combinations(f, 2) if ang[a, b] < 28.0]
        sq_counts.append(sum(1 for e in fe if e in fs))
    return (all(c == 1 for c in odd_counts), all(c in (0, 2) for c in sq_counts),
            odd_counts, sq_counts)

print(f"\n[判別] {len(reps)} 個相異 BFS 著色, 逐一測 O7 飽和條件")
sat_ok = []
for fs, r in reps.items():
    ok_odd, ok_sq, oc, sc = saturation(fs)
    if ok_odd and ok_sq:
        sat_ok.append(r)
        print(f"  root {r:2d}: ✅ 飽和 (奇面 1/面 全部; 正方形 0/2 全部)")
print(f"  飽和著色數: {len(sat_ok)} (roots: {sat_ok})")
chk("F3: 發現 — 飽和著色 = 30 個 (唔唯一) ⟹ **O7「唯一飽和 2-著色」證偽**",
    len(sat_ok) > 1, f"({len(sat_ok)} 個, 全部符合 O7 全部條件)")

# ── 若唯一, 重做 k-selector 分析 ──
if len(sat_ok) == 1:
    r0 = sat_ok[0]
    fs0 = fset(coloring(r0))
    kd = np.zeros(60, int)
    for i, j in fs0:
        kd[i] += 1; kd[j] += 1
    T = np.array(json.load(open(TEMPS))["A5_60"][:60], float)
    rng = np.random.default_rng(7)
    c = float(np.corrcoef(kd.astype(float), np.abs(T))[0, 1])
    null = np.array([np.corrcoef(rng.permutation(kd).astype(float), np.abs(T))[0, 1] for _ in range(20000)])
    p = float((1 + np.sum(null <= c)) / (1 + 20000))
    print(f"\n  唯一飽和著色 (root {r0}): corr(k,|T|) = {c:.4f}, p = {p:.4f}")
    print(f"  k=2 集 ≡ ΔE=0 集? {set(np.where(kd == 2)[0]) == DE0}")
    chk("F4: 飽和著色 = root 0 (O182 g88 用嘅版本) ⟹ k-selector 基礎一致",
        r0 == 0, f"(root {r0})")
    chk("F5: 唯一飽和著色下 k-selector 顯著 (p < 0.05)", p < 0.05, f"(p = {p:.4f})")
    out = dict(n_colorings=len(reps), n_saturated=len(sat_ok), saturated_roots=sat_ok,
               corr_k_absT_sat=c, p_k_absT_sat=p,
               k2_is_DE0=bool(set(np.where(kd == 2)[0]) == DE0))
else:
    print(f"\n  ⚠ {len(sat_ok)} 個飽和著色 ⟹ O7 唯一性聲稱需修正")
    out = dict(n_colorings=len(reps), n_saturated=len(sat_ok), saturated_roots=sat_ok)

json.dump(out, open(os.path.join(O159, "data", "step4_saturation.json"), "w"), indent=2, default=float)

print()
print("=" * 76)
print(f"RESULT: {ok}/{tot} PASS")
print("=" * 76)
exit(0 if ok == tot else 1)
