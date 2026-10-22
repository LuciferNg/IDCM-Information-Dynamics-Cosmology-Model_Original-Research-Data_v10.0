#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O182 scripts/20 — 三種實現之對照 + a5 檔案直接檢定
==================================================
(A) 直接檢定: 精確冷斑軌道之 60 個對稱作用於實測檔 → 證實檔案 = 軌道 round 到 1e-4°
(B) 冷斑軌道實現 (項目實際幾何) 之 88-grid → |Sym|
(C) 理想 Rhombicosidodecahedron (canonical 代數) 之 88-grid → |Sym| = 4 覆核
(D) 4 個穩定元素之幾何刻畫
"""
import numpy as np, math, itertools, json
from fractions import Fraction as F
from pathlib import Path
import networkx as nx
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
O182 = BASE/"o182_88grid_geometry"; OUT = O182/"data"
phi = (1+5**0.5)/2

def rot(ax, ang):
    ax = np.asarray(ax,float); ax = ax/np.linalg.norm(ax)
    c,s_ = math.cos(ang), math.sin(ang)
    K = np.array([[0,-ax[2],ax[1]],[ax[2],0,-ax[0]],[-ax[1],ax[0],0]])
    return np.eye(3)+s_*K+(1-c)*K@K
g1,g2 = rot([0,1,phi],2*math.pi/5), rot([1,1,1],2*math.pi/3)
grp=[np.eye(3)]; seen={tuple(np.round(np.eye(3).ravel(),12))}; i=0
while i<len(grp):
    M=grp[i]; i+=1
    for g in (g1,g2):
        N=g@M; k=tuple(np.round(N.ravel(),12))
        if k not in seen: seen.add(k); grp.append(N)
I_rot = np.array(grp)

def s(a,b): return (F(a),F(b))
BT = [[s(1,0),s(1,0),s(2,1)], [s(F(3,2),F(1,2)),s(F(1,2),F(1,2)),s(1,1)], [s(F(5,2),F(1,2)),s(0,0),s(F(3,2),F(1,2))]]
def cyc(t): return [t,(t[1],t[2],t[0]),(t[2],t[0],t[1])]
ev=[]
for tri in BT:
    for p in cyc(tri):
        sp=[i for i in range(3) if not (p[i][0]==0 and p[i][1]==0)]
        for sg in itertools.product([1,-1],repeat=len(sp)):
            v=list(p)
            for k,i2 in enumerate(sp):
                v[i2]=(-v[i2][0],-v[i2][1]) if sg[k]<0 else v[i2]
            if tuple(v) not in [tuple(x) for x in ev]: ev.append(tuple(v))
Vc = np.array([[float(a)+float(b)*5**0.5 for a,b in t] for t in ev])
Vc /= np.linalg.norm(Vc,axis=1,keepdims=True)

def sym_mats(P, tol_s=1e-11):
    Q = np.asarray(P,float); Q=Q/np.linalg.norm(Q,axis=1,keepdims=True); n=len(Q)
    S = Q@Q.T; best=(-1,None)
    for i in range(min(n,15)):
        for j in range(n):
            for k in range(n):
                if len({i,j,k})<3: continue
                Pp=np.array([Q[i],Q[j],Q[k]]).T; dt=abs(np.linalg.det(Pp))
                if dt>best[0]: best=(dt,(i,j,k,Pp,S[i,j],S[i,k],S[j,k]))
    _, (i0,i1,i2,P1,s01,s02,s12)=best
    P1i=np.linalg.inv(P1); out=[]; seenO=set()
    for a in range(n):
        for b in [b for b in range(n) if abs(S[a,b]-s01)<tol_s]:
            for c in [c for c in range(n) if abs(S[a,c]-s02)<tol_s and abs(S[b,c]-s12)<tol_s]:
                Qq=np.array([Q[a],Q[b],Q[c]]).T; O=Qq@P1i
                if not np.allclose(O@O.T,np.eye(3),atol=1e-8): continue
                key=tuple(np.round(O.ravel(),8))
                if key in seenO: continue
                dev=max(float(np.min(1.0-Q@w)) for w in (O@Q.T).T)
                if dev<tol_s: seenO.add(key); out.append((O,round(np.linalg.det(O)),dev))
    return out

# ── (A) 直接檢定 a5 檔 ──
a5 = np.loadtxt(BASE/"cmb_cold_spot/data/a5_nodes.txt")
ra,dec = np.radians(a5[:,0]), np.radians(a5[:,1])
Vf = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
Vf /= np.linalg.norm(Vf,axis=1,keepdims=True)
cs = SkyCoord(l=209*u.deg, b=-57*u.deg, frame='galactic').icrs
vcs = np.array([math.cos(math.radians(cs.dec.deg))*math.cos(math.radians(cs.ra.deg)),
                math.cos(math.radians(cs.dec.deg))*math.sin(math.radians(cs.ra.deg)),
                math.sin(math.radians(cs.dec.deg))])
orb = []
for M in I_rot:
    w = M@vcs
    if not any(np.allclose(w,o,atol=1e-9) for o in orb): orb.append(w)
Vo = np.array(orb); Vo/=np.linalg.norm(Vo,axis=1,keepdims=True)
print("="*74); print("  (A) 直接檢定: 精確冷斑軌道之 60 對稱 vs 實測 a5_nodes 檔"); print("="*74)
sym_o = sym_mats(Vo, 1e-11)
print(f"  精確軌道 sym_group: |Sym| = {len(sym_o)}  det {{+1:{[d for _,d,_ in sym_o].count(1)}, −1:{[d for _,d,_ in sym_o].count(-1)}}}")
devs = []
for O, det, _ in sym_o:
    W = (O@Vf.T).T
    dev = max(float(np.min(1.0 - Vf@w)) for w in W)
    devs.append(dev)
devs = np.array(devs)
print(f"  逐個對稱作用於實測檔: dev 中位數 {np.median(devs):.2e} (點積), max {devs.max():.2e}")
print(f"  換算角度: max dev = {np.degrees(np.arccos(1-devs.max())):.6f}°")
for tol_deg in (0.05, 0.01, 0.001):
    cnt = int((np.degrees(np.arccos(np.clip(1-devs,-1,1))) < tol_deg).sum())
    print(f"   在 tol = {tol_deg}° 下: {cnt}/60 個對稱存活")

# ── 建立圖 + 著色 (canonical) ──
def graph_of(V, thr=28.0):
    D = np.degrees(np.arccos(np.clip(V@V.T,-1,1)))
    G = nx.Graph(); G.add_nodes_from(range(60))
    for a in range(60):
        for b in range(a+1,60):
            if D[a,b]<thr: G.add_edge(a,b)
    return G
Gc = graph_of(Vc)
Go = graph_of(Vo)
iso = next(nx.algorithms.isomorphism.GraphMatcher(Gc, Go).isomorphisms_iter())  # canonical → orbit
# 著色: 軌道實現上 = 由冷斑節點 (軌道中最近 vcs 者) 之圖距離奇偶
w0_o = int(np.argmin(np.arccos(np.clip(Vo@vcs,-1,1))))
d_o = nx.single_source_shortest_path_length(Go, w0_o)
col_o = {v: d_o[v]%2 for v in range(60)}
E88_o = [(u,v) for u,v in Go.edges() if col_o[u]!=col_o[v]]
E32_o = [(u,v) for u,v in Go.edges() if col_o[u]==col_o[v]]
print(f"\n  (B) 冷斑軌道實現: 冷斑節點 = {w0_o}, 透明邊 {len(E88_o)}, 阻挫邊 {len(E32_o)}")
M88_o = np.array([(Vo[u]+Vo[v])/2 for u,v in E88_o])
g_o = sym_mats(M88_o, 1e-11)
print(f"      ★ |Sym(88-grid 冷斑軌道實現)| = {len(g_o)}, det {{+1:{[d for _,d,_ in g_o].count(1)}, −1:{[d for _,d,_ in g_o].count(-1)}}}")

# ── (C) canonical 覆核 ──
col_c = {iso_inv if False else k: None for k in []}
w0_c = int(np.argmin(np.arccos(np.clip(Vc@Vc[0],-1,1))))  # 佔位
# 用同構把軌道著色搬回 canonical
inv_iso = {v:k for k,v in iso.items()}
col_c = {inv_iso[v]: col_o[v] for v in range(60)}
E88_c = [(u,v) for u,v in Gc.edges() if col_c[u]!=col_c[v]]
E32_c = [(u,v) for u,v in Gc.edges() if col_c[u]==col_c[v]]
M88_c = np.array([(Vc[u]+Vc[v])/2 for u,v in E88_c])
g_c = sym_mats(M88_c, 1e-11)
print(f"\n  (C) canonical 理想實現: 透明 {len(E88_c)} / 阻挫 {len(E32_c)}")
print(f"      ★ |Sym(88-grid canonical)| = {len(g_c)}, det {{+1:{[d for _,d,_ in g_c].count(1)}, −1:{[d for _,d,_ in g_c].count(-1)}}}")
# 邊類型: 三角邊 vs 非三角邊
def etype(G,u,v):
    return "tri" if len(set(G[u])&set(G[v]))>0 else "pent"
from collections import Counter
print(f"      88 邊組成: {Counter(etype(Gc,u,v) for u,v in E88_c)}; 32 邊: {Counter(etype(Gc,u,v) for u,v in E32_c)}")
print(f"      全 120 邊: {Counter(etype(Gc,u,v) for u,v in Gc.edges())}")

# ── (D) canonical 4 元素刻畫 ──
print(f"\n  (D) canonical 88-grid 之 {len(g_c)} 個穩定元素:")
for O,det,dev in g_c:
    W=(O@Vc.T).T
    perm = tuple(int(np.argmin(np.arccos(np.clip(Vc@w,-1,1)))) for w in W)
    fixed = [v for v in range(60) if perm[v]==v]
    # 旋轉角/鏡面
    ev_, evec = np.linalg.eig(O)
    ang = math.degrees(math.acos(max(-1,min(1,(np.trace(O)-1)/2))))
    e88map = set(tuple(sorted((perm[u],perm[v]))) for u,v in E88_c)
    print(f"    det={det:+d}  trace={np.trace(O):+.4f}  旋轉角≈{ang:6.1f}°  固定頂點 {fixed}  "
          f"E88→E88={e88map==set(tuple(sorted(e)) for e in E88_c)}")
print("\nDONE")
