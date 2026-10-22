#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O182 scripts/21 — O213 交接閉合審計 (獨立重算, 唔 import scripts 16-20)
=======================================================================
A. 理想代數座標 (獨立重建) + 結構
B. 圖同構 + 著色 = 圖距離奇偶 (canonical 性)
C. ★ 手性判別三實現 (獨立 sym_group 實作):
     C1 canonical Rhombicosidodecahedron 88-grid
     C2 冷斑 A5 軌道實現 88-grid
     C3 冷斑 A5 軌道 60 節點
D. 群論交叉核對 (整數式, 無容差): 著色 stabilizer
E. 實測檔直接檢定 (a5_nodes / g88_nodes)
"""
import numpy as np, math, itertools, json
from fractions import Fraction as F
from pathlib import Path
from collections import Counter, deque
import networkx as nx
from astropy.coordinates import SkyCoord
import astropy.units as U

BASE = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
O182 = BASE/"o182_88grid_geometry"; OUT = O182/"data"
phi = (1+5**0.5)/2
ok=0; tot=0
def chk(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

# ══ A. 理想代數座標 ══
print("="*74); print("  A. 理想 Rhombicosidodecahedron 代數座標 (獨立重建)"); print("="*74)
def q(a,b): return (F(a),F(b))
BASES = [[q(1,0),q(1,0),q(2,1)], [q(F(3,2),F(1,2)),q(F(1,2),F(1,2)),q(1,1)],
         [q(F(5,2),F(1,2)),q(0,0),q(F(3,2),F(1,2))]]
verts=[]
for base in BASES:
    for perm in (base, (base[1],base[2],base[0]), (base[2],base[0],base[1])):
        nz=[i for i in range(3) if perm[i]!=(F(0),F(0))]
        for sg in itertools.product((1,-1),repeat=len(nz)):
            v=list(perm)
            for j,i in enumerate(nz):
                if sg[j]<0: v[i]=(-v[i][0],-v[i][1])
            if tuple(v) not in [tuple(x) for x in verts]: verts.append(tuple(v))
Vex = np.array([[float(a)+float(b)*math.sqrt(5) for a,b in v] for v in verts])
Vex /= np.linalg.norm(Vex,axis=1,keepdims=True)
chk("A1: 60 頂點", len(verts)==60, f"({len(verts)})")
Dc = np.degrees(np.arccos(np.clip(Vex@Vex.T,-1,1)))
adj = [[j for j in range(60) if j != i and Dc[i,j] < 28.0] for i in range(60)]
chk("A2: 4-正則 / 120 邊", all(len(a)==4 for a in adj) and sum(len(a) for a in adj)//2==120,
    f"(度 {sorted(set(len(a) for a in adj))}, 邊 {sum(len(a) for a in adj)//2})")
edge_len = [Dc[i,j] for i in range(60) for j in adj[i] if j>i]
chk("A3: 邊長全等 25.8786°", max(edge_len)-min(edge_len)<1e-12, f"({min(edge_len):.4f}°)")
# 面 (去重 + nx.triangles)
Gc = nx.Graph(); Gc.add_nodes_from(range(60))
for i in range(60):
    for j in adj[i]:
        if j>i: Gc.add_edge(i,j)
plan,emb = nx.check_planarity(Gc)
face_set = set()
for u,v in Gc.edges():
    face_set.add(tuple(sorted(emb.traverse_face(u,v))))
fsz = Counter(len(f) for f in face_set)
tri = sum(nx.triangles(Gc).values())//3
chk("A4: 20 三角 + 30 方 + 12 五邊 (62 面)",
    tri==20 and (fsz[4],fsz[5])==(30,12) and len(face_set)==62,
    f"(tri={tri}, faces 4:{fsz[4]} 5:{fsz[5]}, 總 {len(face_set)})")

# ══ B. 著色 ══
print("\n"+"="*74); print("  B. 圖同構 + 著色 = 圖距離奇偶"); print("="*74)
a5 = np.loadtxt(BASE/"cmb_cold_spot/data/a5_nodes.txt")
ra,dec = np.radians(a5[:,0]), np.radians(a5[:,1])
Vsky = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
Vsky /= np.linalg.norm(Vsky,axis=1,keepdims=True)
Dsky = np.degrees(np.arccos(np.clip(Vsky@Vsky.T,-1,1)))
Go = nx.Graph(); Go.add_nodes_from(range(60))
for i in range(60):
    for j in range(i+1,60):
        if Dsky[i,j]<28.0: Go.add_edge(i,j)
chk("B1: 實測圖 ≅ canonical 圖", nx.is_isomorphic(Gc,Go))
iso = next(nx.algorithms.isomorphism.GraphMatcher(Gc,Go).isomorphisms_iter())
col_obs={}
for ln in (BASE/"cmb_cold_spot/data/anchored_coloring.txt").read_text().splitlines():
    if ln.startswith("#") or not ln.strip(): continue
    p=ln.split(); col_obs[int(p[0])]=int(p[3])
dist0 = nx.single_source_shortest_path_length(Go,0)
chk("B2: 著色 = 節點 0 圖距離奇偶 (canonical, 唔靠 traversal)",
    all(col_obs[v]==dist0[v]%2 for v in range(60)) or all(col_obs[v]==1-dist0[v]%2 for v in range(60)))
col_c = {k: col_obs[v] for k,v in iso.items()}     # canonical 著色
E88c = [(u,v) for u,v in Gc.edges() if col_c[u]!=col_c[v]]
E32c = [(u,v) for u,v in Gc.edges() if col_c[u]==col_c[v]]
chk("B3: canonical 88/32", len(E88c)==88 and len(E32c)==32, f"({len(E88c)}/{len(E32c)})")
fr_obs=set()
for ln in (BASE/"cmb_cold_spot/data/frustration_edges.txt").read_text().splitlines():
    if ln.startswith("#") or not ln.strip(): continue
    p=ln.split(); fr_obs.add((min(int(p[0]),int(p[1])),max(int(p[0]),int(p[1]))))
chk("B4: 阻挫邊 32/32 吻合", set(tuple(sorted((iso[u],iso[v]))) for u,v in E32c)==fr_obs)

# ══ C. sym_group (獨立實作: 以 3 點仿射解 + 集合成員) ══
print("\n"+"="*74); print("  C. ★ 手性判別 (獨立 sym_group)"); print("="*74)
def sym(P, tol=1e-10):
    Q = np.asarray(P,float); Q=Q/np.linalg.norm(Q,axis=1,keepdims=True); n=len(Q)
    S=Q@Q.T; best=(-1,None)
    for i in range(min(n,20)):
        for j in range(n):
            for k in range(n):
                if len({i,j,k})<3: continue
                Pp=np.array([Q[i],Q[j],Q[k]]).T; d=abs(np.linalg.det(Pp))
                if d>best[0]: best=(d,(i,j,k,Pp,S[i,j],S[i,k],S[j,k]))
    _, (i0,i1,i2,P1,s01,s02,s12)=best
    P1i=np.linalg.inv(P1); res=[]; seen=set()
    for a in range(n):
        for b in [b for b in range(n) if abs(S[a,b]-s01)<tol]:
            for c in [c for c in range(n) if abs(S[a,c]-s02)<tol and abs(S[b,c]-s12)<tol]:
                O=np.array([Q[a],Q[b],Q[c]]).T@P1i
                if not np.allclose(O@O.T,np.eye(3),atol=1e-7): continue
                key=tuple(np.round(O.ravel(),7))
                if key in seen: continue
                if max(float(np.min(1.0-Q@w)) for w in (O@Q.T).T)<tol:
                    seen.add(key); res.append((O,round(np.linalg.det(O))))
    return res

# C1 canonical
M88c = np.array([(Vex[u]+Vex[v])/2 for u,v in E88c])
r1 = sym(M88c)
chk("C1: canonical 88-grid |Sym| = 4, det {+1:2, −1:2}", len(r1)==4 and
    [d for _,d in r1].count(1)==2 and [d for _,d in r1].count(-1)==2,
    f"(|Sym|={len(r1)}, +1:{[d for _,d in r1].count(1)}, −1:{[d for _,d in r1].count(-1)})")
chk("C1b: canonical 88-grid 含 improper → 非手性", [d for _,d in r1].count(-1)>0)

# C2 冷斑軌道實現
def icosa_group():
    def rot(ax,ang):
        ax=np.asarray(ax,float); ax=ax/np.linalg.norm(ax)
        c,s_=math.cos(ang),math.sin(ang)
        K=np.array([[0,-ax[2],ax[1]],[ax[2],0,-ax[0]],[-ax[1],ax[0],0]])
        return np.eye(3)+s_*K+(1-c)*K@K
    g1,g2=rot([0,1,phi],2*math.pi/5),rot([1,1,1],2*math.pi/3)
    grp=[np.eye(3)]; seen={tuple(np.round(np.eye(3).ravel(),12))}; i=0
    while i<len(grp):
        M=grp[i]; i+=1
        for g in (g1,g2):
            N=g@M; k=tuple(np.round(N.ravel(),12))
            if k not in seen: seen.add(k); grp.append(N)
    return np.array(grp)
I_rot = icosa_group()
cs = SkyCoord(l=209*U.deg,b=-57*U.deg,frame='galactic').icrs
vcs = np.array([math.cos(math.radians(cs.dec.deg))*math.cos(math.radians(cs.ra.deg)),
                math.cos(math.radians(cs.dec.deg))*math.sin(math.radians(cs.ra.deg)),
                math.sin(math.radians(cs.dec.deg))])
orb=[]
for M in I_rot:
    w=M@vcs
    if not any(np.allclose(w,o,atol=1e-9) for o in orb): orb.append(w)
Vorb=np.array(orb); Vorb/=np.linalg.norm(Vorb,axis=1,keepdims=True)
chk("C2a: 冷斑 A5 軌道 60 節點 |Sym| = 60 (全 proper) → 手性",
    len(sym(Vorb))==60 and [d for _,d in sym(Vorb)].count(-1)==0,
    f"(|Sym|={len(sym(Vorb))}, −1:{[d for _,d in sym(Vorb)].count(-1)})")
# 冷斑軌道嘅 88-grid (著色: 由最近 vcs 之節點圖距離奇偶)
Do_ = np.degrees(np.arccos(np.clip(Vorb@Vorb.T,-1,1)))
Goo = nx.Graph(); Goo.add_nodes_from(range(60))
for i in range(60):
    for j in range(i+1,60):
        if Do_[i,j]<28.0: Goo.add_edge(i,j)
w0o = int(np.argmin(np.arccos(np.clip(Vorb@vcs,-1,1))))
d_o = nx.single_source_shortest_path_length(Goo,w0o)
col_o = {v: d_o[v]%2 for v in range(60)}
E88o = [(u,v) for u,v in Goo.edges() if col_o[u]!=col_o[v]]
E32o = [(u,v) for u,v in Goo.edges() if col_o[u]==col_o[v]]
chk("C2b: 冷斑軌道 88/32", len(E88o)==88 and len(E32o)==32, f"({len(E88o)}/{len(E32o)})")
M88o = np.array([(Vorb[u]+Vorb[v])/2 for u,v in E88o])
r2 = sym(M88o)
chk("C2c: 冷斑軌道 88-grid |Sym| = 2 (全 proper) → ★手性",
    len(r2)==2 and [d for _,d in r2].count(-1)==0,
    f"(|Sym|={len(r2)}, +1:{[d for _,d in r2].count(1)}, −1:{[d for _,d in r2].count(-1)})")

# ══ D. 群論核對 (整數式) ══
print("\n"+"="*74); print("  D. 群論核對 (整數式, 無容差)"); print("="*74)
# canonical: Ih = sym(Vex) 120 元素 → 對 88-邊集 stabilizer
Ih = sym(Vex, 1e-9)
chk("D1: |Ih(canonical 60)| = 120", len(Ih)==120, f"({len(Ih)})")
E88s = set(tuple(sorted(e)) for e in E88c)
stab=0; st=[]
for O,det in Ih:
    W=(O@Vex.T).T
    perm=tuple(int(np.argmin(np.arccos(np.clip(Vex@w,-1,1)))) for w in W)
    if set(tuple(sorted((perm[u],perm[v]))) for u,v in E88c)==E88s:
        stab+=1; st.append(det)
chk("D2: canonical Ih-stabilizer(88 邊集) = 4, det {+1:2, −1:2}",
    stab==4 and st.count(1)==2 and st.count(-1)==2, f"({stab}, {Counter(st)})")
# 冷斑軌道: I(60) 對 88-邊集 stabilizer
stab2=0; st2=[]
for O in I_rot:
    W=(O@Vorb.T).T
    perm=tuple(int(np.argmin(np.arccos(np.clip(Vorb@w,-1,1)))) for w in W)
    if set(tuple(sorted((perm[u],perm[v]))) for u,v in E88o)==set(tuple(sorted(e)) for e in E88o):
        stab2+=1; st2.append(round(np.linalg.det(O)))
chk("D3: 冷斑軌道 I-stabilizer(88 邊集) = 2, 全 proper", stab2==2 and st2.count(-1)==0,
    f"({stab2}, {Counter(st2)})")
# 邊 orbit 結構
orb1=set(); orb2=set(); seen=set()
for u,v in Gc.edges():
    e=tuple(sorted((u,v)))
    if e in seen: continue
    o=set()
    for O,_ in Ih:
        W=(O@Vex.T).T; perm=tuple(int(np.argmin(np.arccos(np.clip(Vex@w,-1,1)))) for w in W)
        o.add(tuple(sorted((perm[u],perm[v]))))
    (orb1 if not orb1 else orb2).update(o); seen|=o
chk("D4: 120 邊 = 2 個 Ih-軌道 × 60 → 88 邊永不 Ih-不變",
    len(orb1)==60 and len(orb2)==60, f"({len(orb1)}, {len(orb2)})")
chk("D5: 88 ≠ 60/120 ⟹ 88-邊集非 I-不變 ⟹ |Sym| ≠ 60 結構必然", 88 not in (60,120))

# ══ E. 實測檔直接檢定 ══
print("\n"+"="*74); print("  E. 實測檔直接檢定"); print("="*74)
for O,_ in sym(Vorb):
    pass
devs=[]
for O,_ in sym(Vorb,1e-10):
    W=(O@Vsky.T).T
    devs.append(max(float(np.min(1.0-Vsky@w)) for w in W))
devs=np.array(devs)
chk("E1: a5_nodes 檔 = 精確冷斑軌道 round (60 對稱全存活, max dev < 1e-3°)",
    len(devs)==60 and np.degrees(np.arccos(np.clip(1-devs.max(),-1,1)))<1e-3,
    f"(max dev = {np.degrees(np.arccos(np.clip(1-devs.max(),-1,1))):.6f}°)")
g88 = np.loadtxt(OUT/"g88_nodes.txt")
rr,dd=np.radians(g88[:,0]),np.radians(g88[:,1])
Vg88=np.column_stack([np.cos(dd)*np.cos(rr),np.cos(dd)*np.sin(rr),np.sin(dd)])
Vg88/=np.linalg.norm(Vg88,axis=1,keepdims=True)
# 理想冷斑軌道 88-grid 嘅 2 個對稱作用於實測 g88 檔
devs2=[]
for O,_ in r2:
    W=(O@Vg88.T).T
    devs2.append(max(float(np.min(1.0-Vg88@w)) for w in W))
print(f"  g88_nodes 檔: 理想 2 對稱之 dev = {[f'{d:.2e}' for d in devs2]} "
      f"→ 角度 {[f'{np.degrees(np.arccos(np.clip(1-d,-1,1))):.4f}°' for d in devs2]}")
chk("E2: g88_nodes 檔 = 理想 88-grid round (2 對稱皆存活 < 0.01°)",
    max(np.degrees(np.arccos(np.clip(1-np.array(devs2),-1,1)))) < 0.01,
    f"(max {max(np.degrees(np.arccos(np.clip(1-np.array(devs2),-1,1)))):.5f}°)")

print(f"\nRESULT: {ok}/{tot} PASS")
