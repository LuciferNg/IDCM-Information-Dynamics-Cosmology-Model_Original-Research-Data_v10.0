#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O182 probe: scripts/16 C4 之 Ih 框架 bug 之獨立裁決"""
import numpy as np, math, itertools
from fractions import Fraction as F
from pathlib import Path
BASE = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
phi = (1+5**0.5)/2
def s(a,b): return (F(a),F(b))
BT = [[s(1,0),s(1,0),s(2,1)],[s(F(3,2),F(1,2)),s(F(1,2),F(1,2)),s(1,1)],
      [s(F(5,2),F(1,2)),s(0,0),s(F(3,2),F(1,2))]]
ex=[]
for tri in BT:
    for perm in [tri,(tri[1],tri[2],tri[0]),(tri[2],tri[0],tri[1])]:
        nz=[i for i in range(3) if perm[i]!=(F(0),F(0))]
        for sg in itertools.product((1,-1),repeat=len(nz)):
            v=list(perm)
            for j,i in enumerate(nz):
                if sg[j]<0: v[i]=(-v[i][0],-v[i][1])
            if tuple(v) not in [tuple(x) for x in ex]: ex.append(tuple(v))
Vex=np.array([[float(a)+float(b)*math.sqrt(5) for a,b in v] for v in ex])
Vex/=np.linalg.norm(Vex,axis=1,keepdims=True)

def sym_mats(V,tol=1e-9):
    V=np.asarray(V,float); V=V/np.linalg.norm(V,axis=1,keepdims=True); n=len(V)
    S=V@V.T; best=(-1,None)
    for i in range(min(n,20)):
        for j in range(n):
            for k in range(n):
                if len({i,j,k})<3: continue
                P=np.array([V[i],V[j],V[k]]).T; d=abs(np.linalg.det(P))
                if d>best[0]: best=(d,(i,j,k,P,S[i,j],S[i,k],S[j,k]))
    _, (i0,i1,i2,P1,s01,s02,s12)=best
    P1i=np.linalg.inv(P1); res=[]; seen=set()
    for a in range(n):
        for b in [b for b in range(n) if abs(S[a,b]-s01)<tol]:
            for c in [c for c in range(n) if abs(S[a,c]-s02)<tol and abs(S[b,c]-s12)<tol]:
                O=np.array([V[a],V[b],V[c]]).T@P1i
                if not np.allclose(O@O.T,np.eye(3),atol=1e-7): continue
                key=tuple(np.round(O.ravel(),7))
                if key in seen: continue
                if max(float(np.min(1.0-V@w)) for w in (O@V.T).T)<tol:
                    seen.add(key); res.append(O)
    return np.array(res)

Ih_true = sym_mats(Vex)
print(f"幾何 Sym(Vex) = {len(Ih_true)}")

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
I_rot=np.array(grp)
refl=np.diag([1.,1.,-1.])
Ih16=np.concatenate([I_rot, np.array([refl@M for M in I_rot])])

def in_set(M, S, tol=1e-6):
    return min(np.abs(M-S).max(axis=(1,2))) < tol

print(f"I_rot ⊆ Sym(Vex)?   {all(in_set(M, Ih_true) for M in I_rot)}  (I_rot 60 個, 命中 {sum(in_set(M,Ih_true) for M in I_rot)})")
print(f"Ih16 ⊆ Sym(Vex)?    {sum(in_set(M,Ih_true) for M in Ih16)}/120")
print(f"refl ∈ Sym(Vex)?    {in_set(refl, Ih_true)}")

# E88
D=np.degrees(np.arccos(np.clip(Vex@Vex.T,-1,1)))
import networkx as nx
G=nx.Graph(); G.add_nodes_from(range(60))
for i in range(60):
    for j in range(i+1,60):
        if D[i,j]<28.0: G.add_edge(i,j)
w0=0
d0=nx.single_source_shortest_path_length(G,w0)
col={v:d0[v]%2 for v in range(60)}
E88=[(u,v) for u,v in G.edges() if col[u]!=col[v]]
E88s=set(tuple(sorted(e)) for e in E88)
print(f"E88 = {len(E88)}")
for name, Ih in [("Sym(Vex) [幾何真值]", Ih_true), ("Ih16 [scripts/16]", Ih16)]:
    stab=0; dets=[]
    for M in Ih:
        W=(M@Vex.T).T
        perm=tuple(int(np.argmin(np.arccos(np.clip(Vex@w,-1,1)))) for w in W)
        if set(tuple(sorted((perm[u],perm[v]))) for u,v in E88)==E88s:
            stab+=1; dets.append(round(np.linalg.det(M)))
    print(f"  {name}: E88-stabilizer = {stab}, det {dets.count(1)},{dets.count(-1)}")
