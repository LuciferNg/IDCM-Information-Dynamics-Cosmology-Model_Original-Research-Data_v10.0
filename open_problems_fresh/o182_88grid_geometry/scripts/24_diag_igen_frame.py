#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O182 probe2: I_rot (生成子) 究竟係唔係 Vu 嘅對稱群? A3 是否虛假通過?"""
import numpy as np, math, itertools
from fractions import Fraction as F
from pathlib import Path
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
print(f"Vu[0] = {Vex[0]}  (= (1,1,phi^3) normalized?)")

def rot(ax,ang):
    ax=np.asarray(ax,float); ax=ax/np.linalg.norm(ax)
    c,s_=math.cos(ang),math.sin(ang)
    K=np.array([[0,-ax[2],ax[1]],[ax[2],0,-ax[0]],[-ax[1],ax[0],0]])
    return np.eye(3)+s_*K+(1-c)*K@K
g1=rot([0,1,phi],2*math.pi/5); g2=rot([1,1,1],2*math.pi/3)

def is_sym(M,V,tol=1e-6):
    W=(M@V.T).T
    return max(float(np.min(np.arccos(np.clip(V@w,-1,1)))) for w in W) < tol
print(f"g1 ∈ Sym(Vu)? {is_sym(g1,Vex)}   g2 ∈ Sym(Vu)? {is_sym(g2,Vex)}")
print(f"refl=diag(1,1,-1) ∈ Sym(Vu)? {is_sym(np.diag([1.,1.,-1.]),Vex)}")

# orbit of (1,1,phi^3) under I_rot vs Vu
grp=[np.eye(3)]; seen={tuple(np.round(np.eye(3).ravel(),12))}; i=0
while i<len(grp):
    M=grp[i]; i+=1
    for g in (g1,g2):
        N=g@M; k=tuple(np.round(N.ravel(),12))
        if k not in seen: seen.add(k); grp.append(N)
I_rot=np.array(grp)
orb=[]
for M in I_rot:
    w=M@np.array([1.,1.,phi**3]); w=w/np.linalg.norm(w)
    if not any(np.allclose(w,o,atol=1e-9) for o in orb): orb.append(w)
Vorb=np.array(orb)
# 對每個 Vorb 點搵 Vu 最近點
dev=max(float(np.min(np.arccos(np.clip(Vex@w,-1,1)))) for w in Vorb)
print(f"orbit_I_rot((1,1,phi^3)) 對 Vu 之 max min-dev = {math.degrees(dev):.6f}°")
# A3 用嘅譜比較
sa=np.sort(np.degrees(np.arccos(np.clip(Vex@Vex.T,-1,1)))[0])
sb=np.sort(np.degrees(np.arccos(np.clip(Vorb@Vorb.T,-1,1)))[0])
print(f"A3 譜比較 max|Δ| = {np.abs(sa-sb).max():.3e}°   (A3 若 < 1e-9 = PASS)")
print(f"  但集合 max min-dev = {math.degrees(dev):.6f}°  ⟹ 兩者係唔係同一集合: {math.degrees(dev)<1e-6}")

# 真正 Vu 嘅 60 proper 對稱
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
    P1i=np.linalg.inv(P1); res=[]
    for a in range(n):
        for b in [b for b in range(n) if abs(S[a,b]-s01)<tol]:
            for c in [c for c in range(n) if abs(S[a,c]-s02)<tol and abs(S[b,c]-s12)<tol]:
                O=np.array([V[a],V[b],V[c]]).T@P1i
                if not np.allclose(O@O.T,np.eye(3),atol=1e-7): continue
                if max(float(np.min(1.0-V@w)) for w in (O@V.T).T)<tol:
                    if not any(np.abs(O-R).max()<1e-7 for R in res): res.append(O)
    return np.array(res)
Ih=sym_mats(Vex)
print(f"\n幾何 Sym(Vu) = {len(Ih)}; proper = {sum(round(np.linalg.det(O))==1 for O in Ih)}")
print(f"  幾何 I(60 proper) ∩ I_rot = {sum(any(np.abs(O-R).max()<1e-6 for R in I_rot) for O in Ih if round(np.linalg.det(O))==1)}")
