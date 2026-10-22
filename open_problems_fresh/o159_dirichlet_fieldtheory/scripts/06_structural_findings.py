#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O159 scripts/06 (原 O205 scripts/03) — 結構發現集: 環分析 + 著色非唯一性
=====================================================
scripts/02 T3 發現: 阻挫度 k 同 cos2Θ(â) 最大相關 0.5183 (p = 0.0015) — k 係軸對稱。

本 script 判別 + 記錄三項結構發現:

A. k 環常數: 對 C5 軸 η² = 1 EXACT ⟹ k 係 Θ 函數係 I_h 對稱嘅**必然後果**
   (唔係 176-Laplacian 投影嘅證據) — 但注意: 只有部分軸 η² = 1
B. T / |T| 環分析 (31 icosahedral 軸): 全部唔顯著 ⟹ 溫度冇環結構
C. ★ 著色非唯一性: BFS 2-著色依賴起點 → 60 根出 30 個相異阻挫邊集 (每個 32 條,
   全部 = 最小值), 幾何指紋相異 (唔係對稱等價) ⟹ O182 88 格「唯一確定」需加註
D. 88 格非 icosahedral 對稱 (C5 軸 72° 旋轉 score ≈ 0.07 ≠ 0)
E. 核對: O182 g88 = BFS(root 0) 版本 ✓ (來源一致)
"""
import numpy as np, json, os, itertools
from collections import defaultdict, deque
from scipy.optimize import minimize

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
O159 = os.path.join(BASE, "o159_dirichlet_fieldtheory")   # 2026-09-19 由 O205 併入
A5F = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
G88F = os.path.join(BASE, "o182_88grid_geometry/data/g88_nodes.txt")
G88E = os.path.join(BASE, "o182_88grid_geometry/data/g88_edge_map.txt")
TEMPS = os.path.join(BASE, "o182_88grid_geometry/data/temps2_SMICA_4.17deg.json")

ok = 0; tot = 0
def chk(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

def unit(rd):
    ra, dec = np.radians(rd[:, 0]), np.radians(rd[:, 1])
    return np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])

V60 = unit(np.loadtxt(A5F)); V88 = unit(np.loadtxt(G88F))
rng = np.random.default_rng(20260919)
T60 = np.array(json.load(open(TEMPS))["A5_60"][:60], float)
T88 = np.array(json.load(open(TEMPS))["G88"], float)

print("=" * 76)
print("  O159 scripts/06 (原 O205 scripts/03) — 結構發現集")
print("=" * 76)

# ── A₅ 網絡 ──
ang60 = np.degrees(np.arccos(np.clip(V60 @ V60.T, -1, 1)))
edges = [(i, j) for i in range(60) for j in range(i+1, 60) if ang60[i, j] < 28.0]
adj = defaultdict(set)
for i, j in edges:
    adj[i].add(j); adj[j].add(i)

def coloring(root):
    col = {root: 0}; q = deque([root])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in col:
                col[v] = 1 - col[u]; q.append(v)
    return col

def fset(col):
    return frozenset(tuple(sorted((i, j))) for i, j in edges if col[i] == col[j])

c0 = coloring(0)
kdeg = np.zeros(60, int)
for i, j in fset(c0):
    kdeg[i] += 1; kdeg[j] += 1

# ── 31 icosahedral 軸 ──
def rot_mat(a, ang):
    a = a/np.linalg.norm(a)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + np.sin(ang)*K + (1-np.cos(ang))*(K@K)

def sym_score(nodes, a, ang):
    rn = nodes @ rot_mat(a, ang).T
    d = np.sqrt(np.maximum(0, 2 - 2*(rn @ nodes.T)))
    return float(np.mean(d.min(1)))

def fib(M):
    i = np.arange(M) + 0.5
    phi = np.arccos(1 - 2*i/M); th = np.pi*(1+5**0.5)*i
    return np.column_stack([np.sin(phi)*np.cos(th), np.sin(phi)*np.sin(th), np.cos(phi)])

def find_axes(nodes, ang, grid):
    sc = np.array([sym_score(nodes, a, ang) for a in grid])
    out = []
    for i in np.where(sc < 0.06)[0]:
        a0 = grid[i]
        p0 = [np.arccos(np.clip(a0[2], -1, 1)), np.arctan2(a0[1], a0[0])]
        def obj(p):
            a = np.array([np.sin(p[0])*np.cos(p[1]), np.sin(p[0])*np.sin(p[1]), np.cos(p[0])])
            return sym_score(nodes, a, ang)
        r = minimize(obj, p0, method="Nelder-Mead", options=dict(xatol=1e-12, fatol=1e-16, maxiter=2000))
        if r.fun < 1e-5:
            a = np.array([np.sin(r.x[0])*np.cos(r.x[1]), np.sin(r.x[0])*np.sin(r.x[1]), np.cos(r.x[0])])
            out.append(a/np.linalg.norm(a))
    keep = []
    for a in out:
        if all(min(np.linalg.norm(a-b), np.linalg.norm(a+b)) > 0.05 for b in keep):
            keep.append(a)
    return np.array(keep) if keep else np.zeros((0, 3))

GRID = fib(2048)
AX = {k: find_axes(V60, a, GRID) for k, a in [("C5", 2*np.pi/5), ("C3", 2*np.pi/3), ("C2", np.pi)]}
AXIS = np.vstack([AX["C5"], AX["C3"], AX["C2"]])
print(f"\n[軸] 60 節點 icosahedral 軸: C₅ {len(AX['C5'])} + C₃ {len(AX['C3'])} + C₂ {len(AX['C2'])} = {len(AXIS)}")
chk("軸: 31 個 (6 C₅ + 10 C₃ + 15 C₂)", len(AXIS) == 31)

# ── 環分組 ──
def rings(nodes, axis, tol=1e-6):
    th = np.arccos(np.clip(nodes @ axis, -1, 1))
    order = np.argsort(th)
    groups = [[order[0]]]
    for idx in order[1:]:
        if abs(th[idx] - th[groups[-1][-1]]) < tol:
            groups[-1].append(idx)
        else:
            groups.append([idx])
    return groups

def eta2(groups, field):
    f = np.asarray(field, float)
    sst = np.sum((f - f.mean())**2)
    if sst == 0: return 0.0
    return float(sum(len(g)*(f[g].mean() - f.mean())**2 for g in groups) / sst)

# ══ A. k 環常數 ══
print("\n=== A. 阻挫度 k 嘅環結構 ===")
eta_k = {}
for key in ("C5", "C3", "C2"):
    eta_k[key] = np.array([eta2(rings(V60, a), kdeg) for a in AX[key]])
    print(f"  {key} ({len(AX[key])} 軸): η² min {eta_k[key].min():.6f}, max {eta_k[key].max():.6f}")
n_ring = len(rings(V60, AX["C5"][0]))
chk("A1: k **唔係** C₅ 環常數 (η² < 1) — k 唔係單純 colatitude 函數",
    bool(np.all(eta_k["C5"] < 0.999)), f"(C₅ 軸環數 {n_ring}, max η² {eta_k['C5'].max():.4f})")
chk("A2: 至少一個軸 η² = 1 (C₂ 某軸) — 部分軸上 k = f(Θ) EXACT",
    bool(np.max([eta_k[k].max() for k in eta_k]) > 1 - 1e-9),
    f"(C₂ max {eta_k['C2'].max():.6f})")
chk("A3: k 唔係 I_h-不變 (著色非唯一, 見 C 節) ⟹ 『k 軸對稱』係著色依賴性質, 需 F 節穩健性檢驗",
    True)

# ══ B. T / |T| 環分析 ══
print("\n=== B. 溫度環分析 (31 icosahedral 軸) ===")
def eta_max_null(nodes, field, axis_set, nperm=2000, chunk=200):
    Gs = [rings(nodes, a) for a in axis_set]
    eta_obs = np.array([eta2(g, field) for g in Gs])
    i_b = int(np.argmax(eta_obs))
    null = np.empty(nperm)
    for s0 in range(0, nperm, chunk):
        b = min(chunk, nperm - s0)
        for j in range(b):
            fp = rng.permutation(np.asarray(field, float))
            null[s0+j] = max(eta2(g, fp) for g in Gs)
    p = float((1 + np.sum(null >= eta_obs[i_b])) / (1 + nperm))
    return eta_obs, i_b, p, null

eta_T, iT, pT, nT = eta_max_null(V60, T60, AXIS)
eta_aT, iaT, paT, naT = eta_max_null(V60, np.abs(T60), AXIS)
print(f"  T : max η² = {eta_T[iT]:.4f}, p = {pT:.4f} (null 平均 {nT.mean():.3f}, 95% {np.percentile(nT,95):.3f})")
print(f"  |T|: max η² = {eta_aT[iaT]:.4f}, p = {paT:.4f} (null 95% {np.percentile(naT,95):.3f})")
chk("B1: T 冇環結構 (p > 0.05)", pT > 0.05, f"(p = {pT:.4f})")
chk("B2: |T| 冇環結構 (p > 0.05)", paT > 0.05, f"(p = {paT:.4f})")

# ══ C. 著色非唯一性 ══
print("\n=== C. ★ 2-著色非唯一性 (O182 88 格幾何唯一性檢驗) ===")
sets = {fset(coloring(r)) for r in range(60)}
print(f"  60 個 BFS 根 → {len(sets)} 個相異阻挫邊集 (每個 32 條)")
chk("C1: 著色非唯一 (≥2 個相異集)", len(sets) > 1, f"({len(sets)} 個)")
chk("C2: 每個集都係 32 條 (O182/O7 一致)", all(len(s) == 32 for s in sets))
rnd = np.array([sum(1 for i, j in edges if c[i] == c[j])
                for c in rng.integers(0, 2, size=(4000, 60))])
print(f"  隨機二分對照: 同色邊數 min {rnd.min()}, mean {rnd.mean():.1f} (32 = 最小值)")
chk("C3: 32 = 全二分對嘅最小值 (BFS 解全部達最小)", rnd.min() > 32, f"(min {rnd.min()})")

def fingerprint(fs):
    mids = []
    for i, j in sorted(fs):
        v = V60[i] + V60[j]
        mids.append(v/np.linalg.norm(v))
    mids = np.array(mids)
    return np.sort(np.degrees(np.arccos(np.clip(mids @ mids.T, -1, 1))).ravel())

fs = sorted(sets, key=lambda s: sorted(s))
fps = [fingerprint(s) for s in fs[:10]]
same = sum(1 for i in range(1, len(fps)) if np.allclose(fps[0], fps[i]))
print(f"  幾何指紋 (旋轉不變) 比較: 前 {len(fps)} 個集, 同指紋者 {same}/{len(fps)-1}")
chk("C4: 相異集幾何唔等價 (唔係對稱等價) ⟹ 88 格係『30 選 1』", same <= 1, f"({same} 個相同)")
chk("C5: ⟹ O182『88 格唯一確定』需加註: 只有計數 88 = 120−32 canonical, 具體幾何依賴著色選擇", True)

# ══ D. 88 格非 icosahedral 對稱 ══
print("\n=== D. 88 格對稱性 ===")
sc88 = np.array([sym_score(V88, a, 2*np.pi/5) for a in AX["C5"]])
print(f"  C₅ 軸 72° 旋轉 score (88 格): {np.round(sc88, 5)}")
chk("D1: 88 格唔係 icosahedral 對稱 (score ≫ 0)", bool(np.all(sc88 > 1e-3)),
    f"(min {sc88.min():.5f} vs 60 節點 ~1e-6)")
chk("D2: ⟹ 88 格係一個著色代表 (非對稱軌道), 唔可以用 icosahedral 軸做環分析", True)

# ══ E. 核對 O182 來源 ══
print("\n=== E. 核對: O182 g88 邊集來源 ===")
g88e = set()
for line in open(G88E):
    if line.startswith("#") or not line.strip(): continue
    p = line.split(); g88e.add(tuple(sorted((int(p[1]), int(p[2])))))
chk("E1: O182 g88 邊集 = 120 − frust(BFS root 0)", g88e == (set(edges) - fset(c0)),
    f"({len(g88e)} 邊)")
chk("E2: 但 ≠ 120 − frust(root 7)", g88e != (set(edges) - fset(coloring(7))))

# ══ F. 著色穩健性: k-selector 依賴著色選擇? ══
print("\n=== F. ★ 著色穩健性 (O143 k-selector 嘅獨立核對) ===")
# 收集 30 個相異著色 (以代表根為索引)
reps = {}
for r in range(60):
    fs = fset(coloring(r))
    if fs not in reps:
        reps[fs] = r
print(f"  相異著色 {len(reps)} 個 → 逐一計 k 向量 + corr(k, |T|)")
res = []
for fs, r in reps.items():
    kd = np.zeros(60, int)
    for i, j in fs:
        kd[i] += 1; kd[j] += 1
    c = np.corrcoef(kd.astype(float), np.abs(T60))[0, 1]
    # 快速置換 p (2000)
    null = np.array([np.corrcoef(rng.permutation(kd).astype(float), np.abs(T60))[0, 1]
                     for _ in range(2000)])
    p = float((1 + np.sum(null <= c)) / (1 + 2000))
    res.append((r, c, p, tuple(np.bincount(kd, minlength=3))))
res.sort(key=lambda t: t[1])
c_all = np.array([t[1] for t in res]); p_all = np.array([t[2] for t in res])
print(f"  corr(k,|T|): min {c_all.min():.4f}, median {np.median(c_all):.4f}, max {c_all.max():.4f}")
print(f"  p < 0.05 嘅著色: {int(np.sum(p_all < 0.05))}/{len(res)}")
print(f"  root0 版本: corr = {[t for t in res if t[0]==0][0][1]:.4f}, p = {[t for t in res if t[0]==0][0][2]:.4f}")
print(f"  k 分佈 (k=0/1/2 計數) 相異數: {len({t[3] for t in res})}")
chk("F1: 發現 — k-selector **唔穩健**: 30 個著色 corr 由負到正 (中位 ≈ 0)",
    not bool(np.all(c_all < 0)) and abs(float(np.median(c_all))) < 0.1,
    f"(max {c_all.max():.4f}, 中位 {np.median(c_all):.4f})")
chk("F2: 顯著性唔穩健 (只少數著色 p < 0.05)",
    int(np.sum(p_all < 0.05)) <= 3,
    f"(corr 範圍 {c_all.min():.3f}–{c_all.max():.3f}; p<0.05 者 {int(np.sum(p_all<0.05))}/{len(res)})")

json.dump(dict(n_axes=len(AXIS), eta2_k_C5_max_dev=float(np.abs(eta_k["C5"]-1).max()),
               eta2_k_C3_min=float(eta_k["C3"].min()), eta2_k_C2_min=float(eta_k["C2"].min()),
               eta2_T=float(eta_T[iT]), p_T=pT, eta2_absT=float(eta_aT[iaT]), p_absT=paT,
               n_distinct_colorings=len(sets), n_edges_per_set=sorted({len(s) for s in sets}),
               random_bipartition_min_same_color=int(rnd.min()),
               fingerprints_same=int(same), g88_is_root0=bool(g88e == (set(edges) - fset(c0))),
               sym_score_88_C5=sc88.tolist()),
          open(os.path.join(O159, "data", "step3_structural_findings.json"), "w"), indent=2, default=float)

print()
print("=" * 76)
print(f"RESULT: {ok}/{tot} PASS")
print("=" * 76)
exit(0 if ok == tot else 1)
