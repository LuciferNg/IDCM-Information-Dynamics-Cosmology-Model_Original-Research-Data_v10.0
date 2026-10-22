#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O182 scripts/17 — 診斷: 理想 88-grid 對稱群 4 vs 群論 stabilizer 2 之矛盾"""
import numpy as np, math, itertools
from fractions import Fraction as F
from pathlib import Path
import networkx as nx

BASE = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
O182 = BASE / "o182_88grid_geometry"
phi = (1+5**0.5)/2

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
I_rot=np.array(grp)

D = np.degrees(np.arccos(np.clip(Vu@Vu.T,-1,1)))
G = nx.Graph(); G.add_nodes_from(range(60))
for a in range(60):
    for b in range(a+1,60):
        if D[a,b] < 28.0: G.add_edge(a,b)

# 著色 (parity from w0 = 冷斑節點對應)
a5 = np.loadtxt(BASE/"cmb_cold_spot/data/a5_nodes.txt")
ra,dec = np.radians(a5[:,0]), np.radians(a5[:,1])
Vo = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
Do = np.degrees(np.arccos(np.clip(Vo@Vo.T,-1,1)))
Go = nx.Graph(); Go.add_nodes_from(range(60))
for a in range(60):
    for b in range(a+1,60):
        if Do[a,b] < 28.0: Go.add_edge(a,b)
GM = nx.algorithms.isomorphism.GraphMatcher(G, Go)
iso = next(GM.isomorphisms_iter()); inv = {v:k for k,v in iso.items()}
w0 = inv[0]
dist_w0 = nx.single_source_shortest_path_length(G, w0)
col = {v: dist_w0[v]%2 for v in range(60)}
E88 = [(u,v) for u,v in G.edges() if col[u]!=col[v]]
E32 = [(u,v) for u,v in G.edges() if col[u]==col[v]]
M88 = np.array([(V[u]+V[v])/2 for u,v in E88])
M120 = np.array([(V[u]+V[v])/2 for u,v in G.edges()])
print(f"E88={len(E88)} E32={len(E32)}")

# ── 1. 中點相異性 ──
def mindist(P):
    Q = P/np.linalg.norm(P,axis=1,keepdims=True)
    Dm = np.degrees(np.arccos(np.clip(Q@Q.T,-1,1)))
    np.fill_diagonal(Dm, 999)
    return Dm.min()
print(f"\n1. 中點相異性: 120 中點 min 角距 = {mindist(M120):.6f}°, 88 中點 = {mindist(M88):.6f}°")
# 檢查 88 中點 vs 32 中點 之間
M32 = np.array([(V[u]+V[v])/2 for u,v in E32])
q88 = M88/np.linalg.norm(M88,axis=1,keepdims=True); q32 = M32/np.linalg.norm(M32,axis=1,keepdims=True)
Dc = np.degrees(np.arccos(np.clip(q88@q32.T,-1,1)))
print(f"   88 中點 ↔ 32 中點 min 角距 = {Dc.min():.6f}° (若 ~0 = 有重合!)")
allm = np.vstack([M88,M32]); qa = allm/np.linalg.norm(allm,axis=1,keepdims=True)
Da = np.degrees(np.arccos(np.clip(qa@qa.T,-1,1))); np.fill_diagonal(Da,999)
print(f"   全部 120 中點 min 角距 = {Da.min():.6f}°")

# ── 2. 幾何 sym_group 揾到嘅 4 個元素 ──
def sym_group_detail(P, tol=1e-6):
    Q = P/np.linalg.norm(P,axis=1,keepdims=True); n=len(Q)
    Dm = np.arccos(np.clip(Q@Q.T,-1,1))
    best=(-1,None)
    for i in range(min(n,12)):
        for j in range(n):
            for k in range(n):
                if len({i,j,k})<3: continue
                Pp = np.array([Q[i],Q[j],Q[k]]).T; dt=abs(np.linalg.det(Pp))
                if dt>best[0]: best=(dt,(i,j,k,Pp,Dm[i,j],Dm[i,k],Dm[j,k]))
    _, (i0,i1,i2,P1,d01,d02,d12) = best
    P1i = np.linalg.inv(P1); out=[]; seenO=set()
    for a in range(n):
        for b in [b for b in range(n) if abs(Dm[a,b]-d01)<tol]:
            for c in [c for c in range(n) if abs(Dm[a,c]-d02)<tol and abs(Dm[b,c]-d12)<tol]:
                Qq = np.array([Q[a],Q[b],Q[c]]).T; O = Qq@P1i
                if not np.allclose(O@O.T,np.eye(3),atol=1e-6): continue
                key=tuple(np.round(O.ravel(),8))
                if key in seenO: continue
                dev = max(float(np.min(np.arccos(np.clip(Q@w,-1,1)))) for w in (O@Q.T).T)
                if dev<tol: seenO.add(key); out.append((O,dev,a,b,c))
    return out
res = sym_group_detail(M88)
print(f"\n2. 幾何 sym_group(M88): {len(res)} 個元素")
for O,dev,a,b,c in res:
    det = round(np.linalg.det(O))
    # 是否把 60 頂點集映到自己
    W = (O@Vu.T).T
    devV = max(float(np.min(np.arccos(np.clip(Vu@w,-1,1)))) for w in W)
    # 是否在 Ih
    inIh = any(np.allclose(O, M, atol=1e-8) for M in I_rot) 
    inIhM = any(np.allclose(O, np.diag([1.,1.,-1.])@M, atol=1e-8) for M in I_rot)
    # 映射邊集
    perm = tuple(int(np.argmin(np.arccos(np.clip(Vu@w,-1,1)))) for w in W)
    e88map = set(tuple(sorted((perm[u],perm[v]))) for u,v in E88)
    print(f"   det={det:+d} dev(M88)={dev:.2e} dev(V60)={devV:.2e} inI={inIh} inRefl·I={inIhM} "
          f"E88→E88={e88map==set(tuple(sorted(e)) for e in E88)} E88→E32={e88map==set(tuple(sorted(e)) for e in E32)}")

# ── 3. Ih 全 120 元素對 M88 / V60 嘅作用 ──
print(f"\n3. Ih 120 元素:")
cnt88=cnt32=cntV=0
for M in np.concatenate([I_rot, np.array([np.diag([1.,1.,-1.])@X for X in I_rot])]):
    q = M88/np.linalg.norm(M88,axis=1,keepdims=True)
    Wq = (M@q.T).T
    devm = max(float(np.min(np.arccos(np.clip(q@w,-1,1)))) for w in Wq)
    if devm < 1e-6: cnt88+=1
    # V60
    Wv = (M@Vu.T).T
    devv = max(float(np.min(np.arccos(np.clip(Vu@w,-1,1)))) for w in Wv)
    if devv < 1e-6: cntV+=1
print(f"   Ih 中保持 M88 = {cnt88}, 保持 V60 = {cntV}")
