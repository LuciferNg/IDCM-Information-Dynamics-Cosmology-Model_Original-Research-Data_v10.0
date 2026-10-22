#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O182 scripts/16 — O213 交接: 理想 88-grid 代數座標 + 對稱群 det 判別 (R5 手性)
================================================================================
O213 docs/08 收窄命題:
  構造理想 88-grid (Rhombicosidodecahedron 120 邊中, 經阻挫選擇後 88 條中點, 精確代數座標),
  計 sym_group (O ∈ O(3) 使 O·V = V) 之 det 分佈:
    |Sym| = 120 (含 improper) ⟹ 無絕對定向 ⟹ R5 永久 🔴
    |Sym| = 60  (只有 proper) ⟹ 有絕對定向 ⟹ R5 可閉合

本腳本:
  A. 理想 Rhombicosidodecahedron 精確代數座標 (Q(√5)³) + 結構驗證
  B. 著色傳遞 (實測圖 → 理想圖, 圖同構) + 88 條透明邊
  C. sym_group (O213 方法: 集合成員測試) — 校準 + 理想 88-grid
  D. 實測集對稱群審計 (O213 docs/08 §4 表; 檔案輸出見 scripts/22)
"""
import numpy as np, math, json, itertools
from fractions import Fraction as F
from pathlib import Path
from collections import defaultdict, deque
import networkx as nx

BASE = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
O182 = BASE / "o182_88grid_geometry"
OUT = O182 / "data"
phi = (1 + 5**0.5)/2

ok = 0; tot = 0
def chk(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

# ══════════════════════════════════════════════════════════════
# A. 理想 Rhombicosidodecahedron — 精確代數座標 (Q(√5)³)
# ══════════════════════════════════════════════════════════════
print("=" * 74)
print("  A. 理想 Rhombicosidodecahedron 精確代數座標")
print("=" * 74)

# 精確形式: 座標 = a + b√5 (a,b ∈ Q). 三類基底三元組:
#   (1, 1, φ³)      φ³ = 2 + √5          → [(1,0), (1,0), (2,1)]
#   (φ², φ, 2φ)     φ² = 3/2+√5/2, φ = 1/2+√5/2, 2φ = 1+√5
#   (2+φ, 0, φ²)    2+φ = 5/2+√5/2
def s(a, b):  # a + b√5
    return (F(a), F(b))
BASE_TRIPLES = [
    [s(1,0), s(1,0), s(2,1)],                 # (1, 1, φ³)
    [s(F(3,2), F(1,2)), s(F(1,2), F(1,2)), s(1,1)],   # (φ², φ, 2φ)
    [s(F(5,2), F(1,2)), s(0,0), s(F(3,2), F(1,2))],   # (2+φ, 0, φ²)
]

def cyc(t):  # 循環置換 (3 個)
    return [t, (t[1], t[2], t[0]), (t[2], t[0], t[1])]

exact_verts = []
for tri in BASE_TRIPLES:
    for perm in cyc(tri):
        # 全部符號翻轉 (0 座標無符號)
        sign_pos = [i for i in range(3) if not (perm[i][0] == 0 and perm[i][1] == 0)]
        for signs in itertools.product([1, -1], repeat=len(sign_pos)):
            v = list(perm)
            for k, i in enumerate(sign_pos):
                v[i] = (-v[i][0], -v[i][1]) if signs[k] < 0 else v[i]
            if tuple(v) not in [tuple(x) for x in exact_verts]:
                exact_verts.append(tuple(v))
print(f"精確代數頂點: {len(exact_verts)} (期望 60)")
chk("A1: 60 個相異代數頂點", len(exact_verts) == 60, f"({len(exact_verts)})")

def evalf(t):
    return np.array([float(a) + float(b)*5**0.5 for a, b in t])
V_ex = np.array([evalf(t) for t in exact_verts])
norms = np.linalg.norm(V_ex, axis=1)
chk("A2: 全部同一半徑 √(11+4√5)", np.allclose(norms, math.sqrt(11+4*5**0.5), atol=1e-12),
    f"({norms.min():.12f}–{norms.max():.12f})")
Vu = V_ex / norms[:, None]

# 與 orbit-of-(1,1,φ³) 對照 (譜不變量)
def rot(ax, ang):
    ax = np.asarray(ax, float); ax = ax/np.linalg.norm(ax)
    c, s_ = math.cos(ang), math.sin(ang)
    K = np.array([[0,-ax[2],ax[1]],[ax[2],0,-ax[0]],[-ax[1],ax[0],0]])
    return np.eye(3) + s_*K + (1-c)*K@K
g1, g2 = rot([0,1,phi], 2*math.pi/5), rot([1,1,1], 2*math.pi/3)
grp = [np.eye(3)]; seen = {tuple(np.round(np.eye(3).ravel(),12))}; i = 0
while i < len(grp):
    M = grp[i]; i += 1
    for g in (g1, g2):
        N = g @ M; k = tuple(np.round(N.ravel(), 12))
        if k not in seen: seen.add(k); grp.append(N)
I_rot = np.array(grp)
# ★ 唔可以用「生成子」造嘅 I 做 A3/C4: 生成子 (0,1,φ) 唔係代數頂點集嘅 5-fold 軸
#   (probe: g1 ∉ Sym(Vu); orbit_I_gen((1,1,φ³)) 距 Vu 18.22°)。
#   A3 必須 (a) 由頂點集本身導出幾何對稱群, (b) 用「集合成員」比較 — 譜係旋轉
#   不變量, 無法區分一個旋轉後嘅副本 (舊版 A3 因此虛假通過, max Δ 2.8e-14°)。
def sym_mats(V, tol=1e-9):
    """回傳所有 O ∈ O(3) 使 O·V = V (集合成員測試)。"""
    V = np.asarray(V, float); V = V/np.linalg.norm(V, axis=1, keepdims=True); n = len(V)
    S = V @ V.T; best = (-1.0, None)
    for i in range(min(n, 20)):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) < 3: continue
                P = np.array([V[i], V[j], V[k]]).T; d = abs(np.linalg.det(P))
                if d > best[0]: best = (d, (i, j, k, P, S[i, j], S[i, k], S[j, k]))
    _, (i0, i1, i2, P1, s01, s02, s12) = best
    P1i = np.linalg.inv(P1); res = []
    for a in range(n):
        for b in [b for b in range(n) if abs(S[a, b]-s01) < tol]:
            for c in [c for c in range(n) if abs(S[a, c]-s02) < tol and abs(S[b, c]-s12) < tol]:
                O = np.array([V[a], V[b], V[c]]).T @ P1i
                if not np.allclose(O @ O.T, np.eye(3), atol=1e-7): continue
                if max(float(np.min(1.0 - V @ w)) for w in (O @ V.T).T) < tol:
                    if not any(np.abs(O - R).max() < 1e-7 for R in res): res.append(O)
    return np.array(res)

Ih_geo = sym_mats(Vu)                                              # 120 = I_h
I_rot_geo = np.array([O for O in Ih_geo if np.linalg.det(O) > 0])  # 60 = I (proper)
chk("A3a: 幾何 Sym(Vu) = 120 (完整 I_h)", len(Ih_geo) == 120, f"({len(Ih_geo)})")
orb = []
for M in I_rot_geo:
    w = M @ np.array([1., 1., phi**3]); w = w/np.linalg.norm(w)
    if not any(np.allclose(w, o, atol=1e-9) for o in orb): orb.append(w)
Vu_orb = np.array(orb)
dev_a3 = max(float(np.min(np.arccos(np.clip(Vu @ w, -1, 1)))) for w in Vu_orb)
# 容差 1e-6 rad (≈ 5.7e-5°): 遠大於重構浮點噪聲 (~2e-8 rad), 遠小於旋轉副本 (0.318 rad)
chk("A3: 代數座標 = I-軌道 (1,1,φ³) 同一集合 (集合 dev < 1e-6 rad)",
    dev_a3 < 1e-6, f"(max dev = {dev_a3:.2e} rad)")

# 圖結構
def graph_from(V, thr=28.0, n=60):
    D = np.degrees(np.arccos(np.clip(V @ V.T, -1, 1)))
    G = nx.Graph(); G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i+1, n):
            if D[i, j] < thr: G.add_edge(i, j)
    return G, D
Gi, D_ideal = graph_from(Vu)
tri = sum(nx.triangles(Gi).values())//3
ok_planar, emb = nx.check_planarity(Gi)
faces = set()
for u, v in Gi.edges():
    faces.add(tuple(sorted(emb.traverse_face(u, v))))
face_sizes = sorted(len(f) for f in faces)
edge_lens = np.array([D_ideal[u, v] for u, v in Gi.edges()])
chk("A4: 圖結構 120 邊 / 度 4 / 20 三角 / 面 30方+12五邊 (planar 62 面)",
    Gi.number_of_edges() == 120 and set(dict(Gi.degree()).values()) == {4} and tri == 20
    and ok_planar and face_sizes.count(4) == 30 and face_sizes.count(5) == 12,
    f"(E={Gi.number_of_edges()}, tri={tri}, faces 4:{face_sizes.count(4)} 5:{face_sizes.count(5)})")
chk("A5: 邊長全部相等 25.8786°", (edge_lens.max() - edge_lens.min()) < 1e-12,
    f"({edge_lens.min():.6f}–{edge_lens.max():.6f}°)")

# ══════════════════════════════════════════════════════════════
# B. 著色傳遞 (實測 → 理想) + 88 條透明邊
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 74)
print("  B. 著色傳遞 + 88 條透明邊")
print("=" * 74)

a5 = np.loadtxt(BASE / "cmb_cold_spot/data/a5_nodes.txt")
ra, dec = np.radians(a5[:, 0]), np.radians(a5[:, 1])
V_obs = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
Go, D_obs = graph_from(V_obs)
chk("B1: 實測圖 ≅ 理想圖 (networkx 同構)", nx.is_isomorphic(Gi, Go), "")

# 實測著色 (anchored_coloring.txt)
col_obs = {}
for line in (BASE / "cmb_cold_spot/data/anchored_coloring.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split()
    col_obs[int(p[0])] = int(p[3])
# 驗證 = 由節點 0 嘅圖距離奇偶
dist0 = nx.single_source_shortest_path_length(Go, 0)
parity = {v: dist0[v] % 2 for v in range(60)}
chk("B2: 著色 = 節點 0 圖距離奇偶 (canonical, 唔靠 traversal 次序)",
    all(col_obs[v] == parity[v] for v in range(60)) or all(col_obs[v] == 1 - parity[v] for v in range(60)),
    f"(吻合 {sum(col_obs[v]==parity[v] for v in range(60))}/60)")

# 圖同構 → 理想圖著色
GM = nx.algorithms.isomorphism.GraphMatcher(Gi, Go)
iso = next(GM.isomorphisms_iter())   # 理想 i → 實測 o
inv_iso = {v: k for k, v in iso.items()}
w0 = inv_iso[0]                       # 冷斑節點在理想圖嘅對應
print(f"  冷斑節點 0 → 理想頂點 w0 = {w0}")
dist_w0 = nx.single_source_shortest_path_length(Gi, w0)
col_ideal = {v: dist_w0[v] % 2 for v in range(60)}
# 驗證傳遞一致
transf = {inv_iso[v]: col_obs[v] for v in range(60)}
chk("B3: 理想著色 = 傳遞著色 (up to global flip)",
    all(col_ideal[v] == transf[v] for v in range(60)) or all(col_ideal[v] == 1-transf[v] for v in range(60)),
    f"(吻合 {sum(col_ideal[v]==transf[v] for v in range(60))}/60)")

n_c = sum(col_ideal.values()); n_h = 60 - n_c
E88 = [(u, v) for u, v in Gi.edges() if col_ideal[u] != col_ideal[v]]
E32 = [(u, v) for u, v in Gi.edges() if col_ideal[u] == col_ideal[v]]
print(f"  理想著色: 冷 {n_c} / 熱 {n_h}; 透明邊 (雙色) {len(E88)}, 阻挫邊 (同色) {len(E32)}")
chk("B4: 理想 88 透明邊 / 32 阻挫邊", len(E88) == 88 and len(E32) == 32,
    f"({len(E88)}/{len(E32)})")
# 對照實測阻挫邊清單
fr_obs = set()
for line in (BASE / "cmb_cold_spot/data/frustration_edges.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split()
    fr_obs.add((min(int(p[0]), int(p[1])), max(int(p[0]), int(p[1]))))
fr_ideal_mapped = set(tuple(sorted((iso[u], iso[v]))) for u, v in E32)
chk("B5: 理想阻挫邊 ≅ 實測阻挫邊 (經同構)", fr_ideal_mapped == fr_obs,
    f"(交集 {len(fr_ideal_mapped & fr_obs)}/32)")

# ══════════════════════════════════════════════════════════════
# C. sym_group (O213 方法) — 校準 + 理想 88-grid
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 74)
print("  C. sym_group: 對稱群 det 分佈")
print("=" * 74)

def sym_group(V, tol=1e-6):
    """O213 方法: 參考框 (3 點, 非共面) + 距離匹配三元組 + 集合成員測試 + 去重。
    tol: 弧度容差 (1e-6 rad ≈ 5.7e-5°)。回傳 det 列表 (已去重)。"""
    V = np.asarray(V, float)
    V = V / np.linalg.norm(V, axis=1, keepdims=True)
    n = len(V)
    D = np.arccos(np.clip(V @ V.T, -1, 1))
    # 參考框: 最大化 |det| (非共面)
    best = (-1.0, None)
    for i in range(min(n, 12)):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) < 3: continue
                P = np.array([V[i], V[j], V[k]]).T
                dt = abs(np.linalg.det(P))
                if dt > best[0]:
                    best = (dt, (i, j, k, P, D[i, j], D[i, k], D[j, k]))
    i0, i1, i2, P1, d01, d02, d12 = best[1]
    assert best[0] > 1e-3, f"參考框退化 (|det| = {best[0]:.2e})"
    P1inv = np.linalg.inv(P1)
    dets = []
    seenO = set()
    for a in range(n):
        bs = [b for b in range(n) if abs(D[a, b] - d01) < tol]
        for b in bs:
            cs = [c for c in range(n) if abs(D[a, c] - d02) < tol and abs(D[b, c] - d12) < tol]
            for c in cs:
                Q = np.array([V[a], V[b], V[c]]).T
                O = Q @ P1inv
                if not np.allclose(O @ O.T, np.eye(3), atol=1e-6): continue
                key = tuple(np.round(O.ravel(), 8))
                if key in seenO: continue
                W = (O @ V.T).T
                # 集合成員測試 (唔用逐列比較!)
                dev = 0.0
                for w in W:
                    dev = max(dev, float(np.min(np.arccos(np.clip(V @ w, -1, 1)))))
                if dev < tol:
                    seenO.add(key); dets.append(round(np.linalg.det(O)))
    return dets

# 校準 (O213 C9-C10)
ico = []
for sx in (1, -1):
    for sy in (1, -1):
        ico.append((0, sx, sy*phi)); ico.append((sx, sy*phi, 0)); ico.append((sx*phi, 0, sy))
V_ico = np.array(ico, float); V_ico /= np.linalg.norm(V_ico, axis=1, keepdims=True)
d_ico = sym_group(V_ico)
chk("C1: 校準 icosahedron-12 → |Sym| = 120, det {+1:60, −1:60}",
    len(d_ico) == 120 and d_ico.count(1) == 60 and d_ico.count(-1) == 60,
    f"(|Sym|={len(d_ico)}, +1:{d_ico.count(1)}, −1:{d_ico.count(-1)})")
d_rh = sym_group(Vu)
chk("C2: 校準 理想 Rhombi-60 → |Sym| = 120, det {+1:60, −1:60}",
    len(d_rh) == 120 and d_rh.count(1) == 60 and d_rh.count(-1) == 60,
    f"(|Sym|={len(d_rh)}, +1:{d_rh.count(1)}, −1:{d_rh.count(-1)})")
# 手性對照: 一般 I-軌道 (冷斑軌道 = 手性)
from astropy.coordinates import SkyCoord
import astropy.units as u
cs = SkyCoord(l=209*u.deg, b=-57*u.deg, frame='galactic').icrs
v_cs = np.array([math.cos(math.radians(cs.dec.deg))*math.cos(math.radians(cs.ra.deg)),
                 math.cos(math.radians(cs.dec.deg))*math.sin(math.radians(cs.ra.deg)),
                 math.sin(math.radians(cs.dec.deg))])
orb_cs = []
for M in I_rot:
    w = M @ v_cs
    if not any(np.allclose(w, o, atol=1e-9) for o in orb_cs): orb_cs.append(w)
V_cs = np.array(orb_cs)
d_cs = sym_group(V_cs)
chk("C3: 校準 一般 I-軌道-60 (冷斑軌道) → |Sym| = 60, 全 proper",
    len(d_cs) == 60 and d_cs.count(1) == 60,
    f"(|Sym|={len(d_cs)}, +1:{d_cs.count(1)}, −1:{d_cs.count(-1)})")

# ★ 理想 88-grid
M88_exact = [tuple((a[0][0]+a[1][0], a[0][1]+a[1][1]) for a in zip(exact_verts[u], exact_verts[v]))
             for u, v in E88]
M88 = np.array([[ (float(a)/2 + float(b)/2*5**0.5) for a, b in m] for m in M88_exact])
M88_u = M88 / np.linalg.norm(M88, axis=1, keepdims=True)
d_88 = sym_group(M88_u)
print(f"\n  ★ 理想 88-grid (88 中點): |Sym| = {len(d_88)}, det 分佈 "
      f"{{+1: {d_88.count(1)}, −1: {d_88.count(-1)}}}")
M32 = np.array([ (V_ex[u] + V_ex[v])/2 for u, v in E32])
M32_u = M32 / np.linalg.norm(M32, axis=1, keepdims=True)
d_32 = sym_group(M32_u)
print(f"  ★ 理想 32 阻挫中點: |Sym| = {len(d_32)}, det 分佈 "
      f"{{+1: {d_32.count(1)}, −1: {d_32.count(-1)}}}")
M120 = np.array([ (V_ex[u] + V_ex[v])/2 for u, v in Gi.edges()])
M120_u = M120 / np.linalg.norm(M120, axis=1, keepdims=True)
d_120 = sym_group(M120_u)
print(f"  (參照) 全 120 邊中點: |Sym| = {len(d_120)}, det 分佈 "
      f"{{+1: {d_120.count(1)}, −1: {d_120.count(-1)}}}")

# 幾何驗證: 88-grid 嘅 stabilizer = 著色 stabilizer (在 Ih 內)
# ★ 用幾何 Ih_geo (唔用生成子造嘅 Ih — 框架唔一致, 見 A3 註)
Ih = Ih_geo
perm_of = {}
for M in Ih:
    W = (M @ Vu.T).T
    perm = tuple(int(np.argmin(np.arccos(np.clip(Vu @ w, -1, 1)))) for w in W)
    perm_of[tuple(np.round(M.ravel(), 10))] = perm
E88_set = set(tuple(sorted(e)) for e in E88)
stab = 0; stab_det = []
for M in Ih:
    perm = perm_of[tuple(np.round(M.ravel(), 10))]
    if set(tuple(sorted((perm[u], perm[v]))) for u, v in E88) == E88_set:
        stab += 1; stab_det.append(round(np.linalg.det(M)))
print(f"\n  獨立核對 (Ih 120 元素): 保持 88-邊集嘅元素 = {stab}, det 分佈 "
      f"{{+1: {stab_det.count(1)}, −1: {stab_det.count(-1)}}}")
chk("C4: 幾何 sym_group 與 Ih-stabilizer 一致", len(d_88) == stab and d_88.count(-1) == stab_det.count(-1),
    f"(幾何 {len(d_88)} vs 群論 {stab})")

# ══════════════════════════════════════════════════════════════
# D. 實測集對稱群審計 (O213 docs/08 §4 表) + 檔案輸出
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 74)
print("  D. 實測集審計 + 檔案輸出")
print("=" * 74)
for label, V in [("實測 a5_nodes (60)", V_obs), ("實測 g88_nodes (88)", None)]:
    if V is None:
        g88 = np.loadtxt(OUT / "g88_nodes.txt")
        rr, dd = np.radians(g88[:, 0]), np.radians(g88[:, 1])
        V = np.column_stack([np.cos(dd)*np.cos(rr), np.cos(dd)*np.sin(rr), np.sin(dd)])
    for tol_rad, tol_name in [(1e-6, "1e-6 rad"), (8.7e-4, "0.05°")]:
        try:
            dd_ = sym_group(V, tol=tol_rad)
            print(f"  {label} @ {tol_name}: |Sym| = {len(dd_)}, "
                  f"det {{+1: {dd_.count(1)}, −1: {dd_.count(-1)}}}")
        except AssertionError as e:
            print(f"  {label} @ {tol_name}: {e}")

# 實測 88 中點: 上面 loop 已用 3D 單位向量 (lon,lat → xyz) 處理, 唔可以再直接
# 傳 lat/lon 2 欄入 sym_group (np.linalg.det 要 3×3)。

# ── 檔案輸出: 由 scripts/22_write_ideal_coords.py 獨佔 ──
# (scripts/16 只做驗證; 檔案寫入統一由 scripts/22 負責, 慣例 = .txt 單位向量 +
#  JSON 未歸一精確 a+b√5。避免兩個 writer 用唔同慣例互相覆蓋。)
print("\n  檔案輸出: 見 scripts/22_write_ideal_coords.py (本腳本不寫檔)")

print(f"\nRESULT: {ok}/{tot} PASS")

