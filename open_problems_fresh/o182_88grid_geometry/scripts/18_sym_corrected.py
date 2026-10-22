#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O182 scripts/18 — 修正版: 理想 88-grid 對稱群 (正確 frame)
==========================================================
scripts/17 診斷: 用生成子造嘅 I_rot 與代數頂點集朝向唔一致 (只共享 T_d 24 元素),
故 scripts/16 C4 嘅「Ih-stabilizer」與幾何 sym_group 皆不可靠。
本腳本: 由代數頂點集自身抽 120 個 Ih 元素 (正確 frame), 再算 88-邊集 stabilizer。
"""
import numpy as np, math, itertools, json
from fractions import Fraction as F
from pathlib import Path
import networkx as nx

BASE = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
O182 = BASE / "o182_88grid_geometry"; OUT = O182 / "data"

def s(a, b): return (F(a), F(b))
BT = [[s(1,0), s(1,0), s(2,1)], [s(F(3,2),F(1,2)), s(F(1,2),F(1,2)), s(1,1)],
      [s(F(5,2),F(1,2)), s(0,0), s(F(3,2),F(1,2))]]
def cyc(t): return [t, (t[1],t[2],t[0]), (t[2],t[0],t[1])]
ev = []
for tri in BT:
    for p in cyc(tri):
        sp = [i for i in range(3) if not (p[i][0]==0 and p[i][1]==0)]
        for sg in itertools.product([1,-1], repeat=len(sp)):
            v = list(p)
            for k,i in enumerate(sp):
                v[i] = (-v[i][0], -v[i][1]) if sg[k] < 0 else v[i]
            if tuple(v) not in [tuple(x) for x in ev]: ev.append(tuple(v))
V = np.array([[float(a)+float(b)*5**0.5 for a,b in t] for t in ev])
Vu = V/np.linalg.norm(V,axis=1,keepdims=True)

ok=0; tot=0
def chk(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

def sym_group_mats(P, tol_s=1e-12):
    """回傳 [(O, det, dev)] — 精確對稱群。
    用點積度量 (避開 arccos 近 1 之 1e-8 rad 精度地板):
      - 距離匹配: |S[a,b] − S[i,j]| < tol_s
      - 集合成員測試: dev = max_w min_q (1 − q·w) < tol_s
    """
    Q = np.asarray(P, float); Q = Q/np.linalg.norm(Q, axis=1, keepdims=True); n = len(Q)
    S = Q @ Q.T
    best = (-1, None)
    for i in range(min(n, 15)):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) < 3: continue
                Pp = np.array([Q[i], Q[j], Q[k]]).T; dt = abs(np.linalg.det(Pp))
                if dt > best[0]: best = (dt, (i, j, k, Pp, S[i, j], S[i, k], S[j, k]))
    _, (i0, i1, i2, P1, s01, s02, s12) = best
    assert best[0] > 1e-3, f"參考框退化 (|det|={best[0]:.2e})"
    P1i = np.linalg.inv(P1); out = []; seenO = set()
    for a in range(n):
        for b in [b for b in range(n) if abs(S[a, b]-s01) < tol_s]:
            for c in [c for c in range(n) if abs(S[a, c]-s02) < tol_s and abs(S[b, c]-s12) < tol_s]:
                Qq = np.array([Q[a], Q[b], Q[c]]).T; O = Qq @ P1i
                if not np.allclose(O @ O.T, np.eye(3), atol=1e-9): continue
                key = tuple(np.round(O.ravel(), 9))
                if key in seenO: continue
                dev = max(float(np.min(1.0 - Q @ w)) for w in (O @ Q.T).T)
                if dev < tol_s:
                    seenO.add(key); out.append((O, round(np.linalg.det(O)), dev))
    return out

print("="*74); print("  修正版: 理想 88-grid 對稱群 (正確 frame)"); print("="*74)

# ── Ih (120) 由頂點集自身抽出 ──
Ih = sym_group_mats(Vu, tol_s=1e-11)
det_Ih = [d for _, d, _ in Ih]
print(f"\n1. Ih = sym_group(V60): |Ih| = {len(Ih)}, det {{+1: {det_Ih.count(1)}, −1: {det_Ih.count(-1)}}}, "
      f"max dev = {max(d for _,_,d in Ih):.2e} rad")
chk("1a: |Ih| = 120 (Rhombi-60 非手性)", len(Ih) == 120 and det_Ih.count(1) == 60 and det_Ih.count(-1) == 60)
chk("1b: 所有 Ih 元素精確 (dev < 1e-12 rad)", max(d for _,_,d in Ih) < 1e-12,
    f"(max dev {max(d for _,_,d in Ih):.2e})")
chk("1c: Ih 為群 (封閉性抽樣 200 對)", all(any(np.allclose(A@B, C, atol=1e-8) for C,_,_ in Ih)
        for A,_,_ in Ih[:14] for B,_,_ in Ih[:15]))

# ── 著色 / 88 邊 ──
D = np.degrees(np.arccos(np.clip(Vu@Vu.T,-1,1)))
G = nx.Graph(); G.add_nodes_from(range(60))
for a in range(60):
    for b in range(a+1,60):
        if D[a,b] < 28.0: G.add_edge(a,b)
a5 = np.loadtxt(BASE/"cmb_cold_spot/data/a5_nodes.txt")
ra,dec = np.radians(a5[:,0]), np.radians(a5[:,1])
Vo = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
Do = np.degrees(np.arccos(np.clip(Vo@Vo.T,-1,1)))
Go = nx.Graph(); Go.add_nodes_from(range(60))
for a in range(60):
    for b in range(a+1,60):
        if Do[a,b] < 28.0: Go.add_edge(a,b)
iso = next(nx.algorithms.isomorphism.GraphMatcher(G, Go).isomorphisms_iter())
inv = {v:k for k,v in iso.items()}
col = {v: nx.single_source_shortest_path_length(G, inv[0])[v] % 2 for v in range(60)}
E88 = [(u,v) for u,v in G.edges() if col[u]!=col[v]]
E32 = [(u,v) for u,v in G.edges() if col[u]==col[v]]
E88s = set(tuple(sorted(e)) for e in E88)
print(f"\n2. 理想著色: 冷 {sum(col.values())} / 熱 {60-sum(col.values())}; 透明 88 / 阻挫 32")
chk("2a: 88/32 分割", len(E88)==88 and len(E32)==32)

# ── ★ 88-邊集 stabilizer (在正確 Ih 內) ──
perms = []
for O, det, dev in Ih:
    W = (O@Vu.T).T
    perm = tuple(int(np.argmin(np.arccos(np.clip(Vu@w,-1,1)))) for w in W)
    perms.append((O, det, perm))
stab = [(O,det,perm) for O,det,perm in perms
        if set(tuple(sorted((perm[u],perm[v]))) for u,v in E88) == E88s]
print(f"\n★ 3. Sym(88-grid) = Stab_Ih(88 邊集): |Sym| = {len(stab)}, "
      f"det {{+1: {[d for _,d,_ in stab].count(1)}, −1: {[d for _,d,_ in stab].count(-1)}}}")
for O,det,perm in stab:
    fix = sum(1 for v in range(60) if perm[v]==v)
    print(f"     det={det:+d}  固定頂點數={fix}  (perm 週期結構: "
          f"{sorted({len(list(nx.simple_cycles(nx.DiGraph([(v,perm[v]) for v in range(60)]))))})})")

# ── 幾何交叉驗證 (緊容差) ──
M88 = np.array([(V[u]+V[v])/2 for u,v in E88])
M32 = np.array([(V[u]+V[v])/2 for u,v in E32])
g88 = sym_group_mats(M88, tol_s=1e-11)
g32 = sym_group_mats(M32, tol_s=1e-11)
print(f"\n4. 幾何 sym_group (點積度量 tol_s 1e-11):")
print(f"   M88: |Sym| = {len(g88)}, det {{+1: {[d for _,d,_ in g88].count(1)}, −1: {[d for _,d,_ in g88].count(-1)}}}, "
      f"max dev {max(d for _,_,d in g88):.2e} rad")
print(f"   M32: |Sym| = {len(g32)}, det {{+1: {[d for _,d,_ in g32].count(1)}, −1: {[d for _,d,_ in g32].count(-1)}}}, "
      f"max dev {max(d for _,_,d in g32):.2e} rad")
chk("4a: 幾何 |Sym(M88)| = 群論 Stab", len(g88) == len(stab), f"({len(g88)} vs {len(stab)})")
chk("4b: 幾何 |Sym(M32)| = |Sym(M88)|", len(g32) == len(g88))
chk("4c: 88-grid 含 improper 元素 (det = −1)", [d for _,d,_ in g88].count(-1) > 0,
    f"(det −1 數 = {[d for _,d,_ in g88].count(-1)})")

# ── 邊集 orbit 分析 (結構性解釋) ──
# I (60 proper) 對 120 邊嘅 orbit
I_proper = [(O,det,perm) for O,det,perm in perms if det==1]
orb_sets = []
seen_e = set()
for u,v in G.edges():
    e = tuple(sorted((u,v)))
    if e in seen_e: continue
    orb = set()
    for O,det,perm in I_proper:
        orb.add(tuple(sorted((perm[u],perm[v]))))
    orb_sets.append(orb); seen_e |= orb
print(f"\n5. I(60 proper) 對 120 邊嘅 orbit 數 = {len(orb_sets)}, 大小 = {[len(o) for o in orb_sets]}")
chk("5a: 120 邊 = 2 個 I-orbit × 60 (故無 88 邊 I-不變子集)",
    len(orb_sets)==2 and all(len(o)==60 for o in orb_sets))
chk("5b: 88-邊集非 I-不變 (88 ≠ 60/120)", len(E88) not in (60, 120))
# Ih 對邊 orbit
seen_e = set(); orb_sets_h = []
for u,v in G.edges():
    e = tuple(sorted((u,v)))
    if e in seen_e: continue
    orb = set()
    for O,det,perm in perms:
        orb.add(tuple(sorted((perm[u],perm[v]))))
    orb_sets_h.append(orb); seen_e |= orb
print(f"   Ih(120) 對 120 邊嘅 orbit 數 = {len(orb_sets_h)}, 大小 = {[len(o) for o in orb_sets_h]}")
# 修正 (2026-09-26): Rhombicosidodecahedron **唔係** edge-transitive — 120 邊在 I 及 Ih 下
# 皆分裂為 2 個軌道 × 60 (三角邊 / 五邊邊)。反射唔會合併兩者 (面類型必須保持)。
chk("5c: 120 邊 = 2 個 Ih-orbit × 60 (唔係 edge-transitive)",
    len(orb_sets_h)==2 and all(len(o)==60 for o in orb_sets_h),
    f"({len(orb_sets_h)} 軌道, 大小 {[len(o) for o in orb_sets_h]})")

print(f"\nRESULT: {ok}/{tot} PASS")
