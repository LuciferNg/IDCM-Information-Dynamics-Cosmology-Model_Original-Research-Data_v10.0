#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O182 scripts/22 — 輸出理想代數座標檔 (O213 交接交付物)
=====================================================
a5_nodes_ideal.txt / g88_nodes_ideal.txt / g32_frustration_ideal.txt / ideal_algebraic_coords.json
驗證: 回讀誤差 < 1e-10; JSON 結構完整; 邊表與圖一致。
"""
import numpy as np, math, itertools, json
from fractions import Fraction as F
from pathlib import Path
import networkx as nx

BASE = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
O182 = BASE/"o182_88grid_geometry"; OUT = O182/"data"
ok=0; tot=0
def chk(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

# ── 精確代數頂點 (Q(√5)³) ──
def q(a,b): return (F(a),F(b))
BASES = [[q(1,0),q(1,0),q(2,1)],
         [q(F(3,2),F(1,2)),q(F(1,2),F(1,2)),q(1,1)],
         [q(F(5,2),F(1,2)),q(0,0),q(F(3,2),F(1,2))]]
exact=[]
for base in BASES:
    for perm in (base,(base[1],base[2],base[0]),(base[2],base[0],base[1])):
        nz=[i for i in range(3) if perm[i]!=(F(0),F(0))]
        for sg in itertools.product((1,-1),repeat=len(nz)):
            v=list(perm)
            for j,i in enumerate(nz):
                if sg[j]<0: v[i]=(-v[i][0],-v[i][1])
            if tuple(v) not in [tuple(x) for x in exact]: exact.append(tuple(v))
Vex_raw = np.array([[float(a)+float(b)*math.sqrt(5) for a,b in v] for v in exact])
Vex = Vex_raw / np.linalg.norm(Vex_raw, axis=1, keepdims=True)   # 單位向量 (同 sky 檔慣例)
print(f"  慣例: .txt = 單位向量 (歸一 by 1/√(11+4√5)); JSON = 未歸一精確 a+b√5 (|v| = {math.sqrt(11+4*math.sqrt(5)):.6f})")

# ── 圖 + 著色 (由 cmb_cold_spot anchored_coloring 經同構傳遞) ──
D = np.degrees(np.arccos(np.clip(Vex@Vex.T,-1,1)))
Gc = nx.Graph(); Gc.add_nodes_from(range(60))
for i in range(60):
    for j in range(i+1,60):
        if D[i,j]<28.0: Gc.add_edge(i,j)
a5 = np.loadtxt(BASE/"cmb_cold_spot/data/a5_nodes.txt")
ra,dec = np.radians(a5[:,0]), np.radians(a5[:,1])
Vs = np.column_stack([np.cos(dec)*np.cos(ra),np.cos(dec)*np.sin(ra),np.sin(dec)])
Vs /= np.linalg.norm(Vs,axis=1,keepdims=True)
Ds = np.degrees(np.arccos(np.clip(Vs@Vs.T,-1,1)))
Go = nx.Graph(); Go.add_nodes_from(range(60))
for i in range(60):
    for j in range(i+1,60):
        if Ds[i,j]<28.0: Go.add_edge(i,j)
iso = next(nx.algorithms.isomorphism.GraphMatcher(Gc,Go).isomorphisms_iter())   # canonical → observed
col_obs={}
for ln in (BASE/"cmb_cold_spot/data/anchored_coloring.txt").read_text().splitlines():
    if ln.startswith("#") or not ln.strip(): continue
    p=ln.split(); col_obs[int(p[0])]=int(p[3])
col_c = {k: col_obs[v] for k,v in iso.items()}
E88 = [(u,v) for u,v in Gc.edges() if col_c[u]!=col_c[v]]
E32 = [(u,v) for u,v in Gc.edges() if col_c[u]==col_c[v]]
chk("1: 88/32 分割", len(E88)==88 and len(E32)==32, f"({len(E88)}/{len(E32)})")

# ── 中點 (精確 a+b√5 → float) ──
def mid_exact(u,v):
    return tuple(((exact[u][k][0]+exact[v][k][0])/2, (exact[u][k][1]+exact[v][k][1])/2) for k in range(3))
def to_float(m):
    return np.array([float(a)+float(b)*math.sqrt(5) for a,b in m])
M88_ex = [mid_exact(u,v) for u,v in E88]
M32_ex = [mid_exact(u,v) for u,v in E32]
M88 = np.array([to_float(m) for m in M88_ex])
M32 = np.array([to_float(m) for m in M32_ex])
chk("2: 88/32 中點計算", M88.shape==(88,3) and M32.shape==(32,3))
# 單位化 (同 a5_nodes_ideal.txt 慣例: .txt 全部係單位向量; JSON 保留未歸一精確值)
M88_u = M88 / np.linalg.norm(M88, axis=1, keepdims=True)
M32_u = M32 / np.linalg.norm(M32, axis=1, keepdims=True)

# ── 寫檔 ──
np.savetxt(OUT/"a5_nodes_ideal.txt", Vex, fmt="%.17g",
           header=("x y z (canonical frame) — Rhombicosidodecahedron 60 vertices, UNIT vectors\n"
                   "normalised by 1/sqrt(11+4sqrt5); unnormalised EXACT algebraic (a+b*sqrt5) form is in\n"
                   "ideal_algebraic_coords.json. edge length 2 (angular 25.878637 deg)\n"
                   "generated 2026-09-25 by o182 scripts/22 (O213 handoff)"))
np.savetxt(OUT/"g88_nodes_ideal.txt", M88_u, fmt="%.17g",
           header=("x y z (canonical frame) — midpoints of the 88 transparent edges, UNIT vectors\n"
                   "normalised (midpoint radius of the unit-vertex realisation = cos(25.878637/2 deg)\n"
                   "= 0.974624); edge order = same as data/g88_edge_map.txt; EXACT unnormalised\n"
                   "algebraic form in ideal_algebraic_coords.json. generated 2026-09-25 by o182 scripts/22"))
np.savetxt(OUT/"g32_frustration_ideal.txt", M32_u, fmt="%.17g",
           header=("x y z (canonical frame) — midpoints of the 32 frustrated edges, UNIT vectors\n"
                   "normalised; EXACT unnormalised algebraic form in ideal_algebraic_coords.json\n"
                   "generated 2026-09-25 by o182 scripts/22 (O213 handoff)"))
payload = {
  "generated": "2026-09-25",
  "provenance": "o182_88grid_geometry/scripts/22_write_ideal_coords.py (O213 handoff, docs/06)",
  "note": "coordinates = a + b*sqrt(5) with a,b rational (EXACT). canonical frame. |v|^2 = 11+4*sqrt(5).",
  "a5_vertices_60": [[[str(a),str(b)] for a,b in v] for v in exact],
  "g88_midpoints_88": [[[str(a),str(b)] for a,b in m] for m in M88_ex],
  "g32_midpoints_32": [[[str(a),str(b)] for a,b in m] for m in M32_ex],
  "edge_map_88": [[int(u),int(v)] for u,v in E88],
  "edge_map_32": [[int(u),int(v)] for u,v in E32],
  "coloring_canonical": {str(k):int(v) for k,v in col_c.items()},
  "iso_canonical_to_observed_a5": {str(k):int(v) for k,v in iso.items()},
  "symmetry": {
     "canonical_88grid": {"size": 4, "det_plus": 2, "det_minus": 2, "elements": "e, sigma(mirror,4 fixed vtx), -I(inversion), -sigma", "chirality": "achiral"},
     "coldspot_orbit_88grid": {"size": 2, "det_plus": 2, "det_minus": 0, "elements": "e, -sigma (180deg rot)", "chirality": "CHIRAL"},
     "canonical_60vertices": {"size": 120, "det_plus": 60, "det_minus": 60, "chirality": "achiral"},
     "coldspot_orbit_60nodes": {"size": 60, "det_plus": 60, "det_minus": 0, "chirality": "CHIRAL"},
     "structural_note": "120 edges = 2 I-orbits x 60 (triangle-edges / pentagon-edges) => no 88-edge subset is I-invariant => |Sym| != 60 necessarily"
  }
}
with open(OUT/"ideal_algebraic_coords.json","w") as f:
    json.dump(payload, f, indent=1)

# ── 驗證 ──
V_re = np.loadtxt(OUT/"a5_nodes_ideal.txt"); chk("3: a5_nodes_ideal.txt 回讀 < 1e-10", np.abs(V_re-Vex).max()<1e-10, f"(max {np.abs(V_re-Vex).max():.2e})")
M_re = np.loadtxt(OUT/"g88_nodes_ideal.txt"); chk("4: g88_nodes_ideal.txt 回讀 < 1e-10", np.abs(M_re-M88_u).max()<1e-10, f"(max {np.abs(M_re-M88_u).max():.2e})")
K_re = np.loadtxt(OUT/"g32_frustration_ideal.txt"); chk("5: g32_frustration_ideal.txt 回讀 < 1e-10", np.abs(K_re-M32_u).max()<1e-10, f"(max {np.abs(K_re-M32_u).max():.2e})")
chk("5b: 三個 .txt 全部係單位向量", max(abs(np.linalg.norm(V_re,axis=1)-1).max(), abs(np.linalg.norm(M_re,axis=1)-1).max(), abs(np.linalg.norm(K_re,axis=1)-1).max())<1e-15,
    f"(max |‖v‖−1| = {max(abs(np.linalg.norm(V_re,axis=1)-1).max(), abs(np.linalg.norm(M_re,axis=1)-1).max(), abs(np.linalg.norm(K_re,axis=1)-1).max()):.2e})")
J = json.load(open(OUT/"ideal_algebraic_coords.json"))
chk("6: JSON 結構完整", len(J["a5_vertices_60"])==60 and len(J["g88_midpoints_88"])==88
    and len(J["g32_midpoints_32"])==32 and len(J["edge_map_88"])==88 and len(J["edge_map_32"])==32)
# 精確驗證: a+b√5 重建 = 未歸一精確座標
rec = np.array([[float(F(a))+float(F(b))*math.sqrt(5) for a,b in v] for v in J["a5_vertices_60"]])
chk("7: JSON 精確 a+b√5 重建 = 未歸一座標 (< 1e-12)", np.abs(rec-Vex_raw).max()<1e-12, f"(max {np.abs(rec-Vex_raw).max():.2e})")
# 88 中點精確 (Fraction 算術) = (u+v)/2
okmid = True
for i,(u,v) in enumerate(E88):
    for k in range(3):
        a = (F(J["g88_midpoints_88"][i][k][0]), F(J["g88_midpoints_88"][i][k][1]))
        b = ((exact[u][k][0]+exact[v][k][0])/2, (exact[u][k][1]+exact[v][k][1])/2)
        if a != b: okmid = False
chk("8: 88 中點 = 邊端點平均 (精確 Fraction 算術)", okmid)
# 單位化一致性: .txt 歸一後 = 精確座標歸一
chk("9: .txt 單位向量 = 未歸一精確座標歸一", np.abs(V_re - Vex_raw/np.linalg.norm(Vex_raw,axis=1,keepdims=True)).max()<1e-15,
    f"(max {np.abs(V_re - Vex_raw/np.linalg.norm(Vex_raw,axis=1,keepdims=True)).max():.2e})")
print(f"\nRESULT: {ok}/{tot} PASS")
print(f"寫入: {OUT}/a5_nodes_ideal.txt, g88_nodes_ideal.txt, g32_frustration_ideal.txt, ideal_algebraic_coords.json")
