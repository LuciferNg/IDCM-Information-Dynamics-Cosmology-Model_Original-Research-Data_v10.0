#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O182 scripts/19 — 審計 cmb_cold_spot/data/a5_nodes.txt: 係咪精確 I-軌道?"""
import numpy as np, math, itertools
from pathlib import Path
BASE = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
phi = (1+5**0.5)/2
def rot(ax, ang):
    ax = np.asarray(ax,float); ax=ax/np.linalg.norm(ax)
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

a5 = np.loadtxt(BASE/"cmb_cold_spot/data/a5_nodes.txt")
ra,dec = np.radians(a5[:,0]), np.radians(a5[:,1])
V = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
V /= np.linalg.norm(V,axis=1,keepdims=True)
print(f"檔案: {len(a5)} 點, 座標小數位: RA={len(str(a5[0,0]).split('.')[-1])}, Dec={len(str(a5[0,1]).split('.')[-1])}")

def sym_arccos(P, tol):
    Q = P/np.linalg.norm(P,axis=1,keepdims=True); n=len(Q)
    Dm = np.arccos(np.clip(Q@Q.T,-1,1))
    best=(-1,None)
    for i in range(min(n,15)):
        for j in range(n):
            for k in range(n):
                if len({i,j,k})<3: continue
                Pp=np.array([Q[i],Q[j],Q[k]]).T; dt=abs(np.linalg.det(Pp))
                if dt>best[0]: best=(dt,(i,j,k,Pp,Dm[i,j],Dm[i,k],Dm[j,k]))
    _, (i0,i1,i2,P1,d01,d02,d12)=best
    P1i=np.linalg.inv(P1); out=[]; seenO=set()
    for a in range(n):
        for b in [b for b in range(n) if abs(Dm[a,b]-d01)<tol]:
            for c in [c for c in range(n) if abs(Dm[a,c]-d02)<tol and abs(Dm[b,c]-d12)<tol]:
                Qq=np.array([Q[a],Q[b],Q[c]]).T; O=Qq@P1i
                if not np.allclose(O@O.T,np.eye(3),atol=1e-8): continue
                key=tuple(np.round(O.ravel(),8))
                if key in seenO: continue
                dev=max(float(np.min(np.arccos(np.clip(Q@w,-1,1)))) for w in (O@Q.T).T)
                if dev<tol: seenO.add(key); out.append((round(np.linalg.det(O)),dev))
    return out

print("\n1. sym_group(實測 a5) 各容差:")
for tol, nm in [(1e-7,"1e-7 rad"),(1e-6,"1e-6 rad"),(1e-5,"1e-5 rad"),(1e-4,"1e-4 rad"),(8.7e-4,"0.05°")]:
    r = sym_arccos(V, tol)
    print(f"   tol={nm}: |Sym|={len(r)}  det {{+1:{[d for d,_ in r].count(1)}, −1:{[d for d,_ in r].count(-1)}}}  "
          f"max dev={max((dv for _,dv in r), default=0):.2e}")

# 2. 由檔案自身第 0 點生成軌道, 對比
seed = V[0]
orb = []
for M in I_rot:
    w = M@seed
    if not any(np.allclose(w,o,atol=1e-9) for o in orb): orb.append(w)
O = np.array(orb); O/=np.linalg.norm(O,axis=1,keepdims=True)
print(f"\n2. 由檔案第 0 點生成 I-軌道: {len(O)} 點 (期望 60)")
# 最優對齊 (Kabsch) — 用 NN 對應
from numpy.linalg import svd
Pm = O; Qm = V.copy()
# NN matching
idx = [int(np.argmin(np.arccos(np.clip(V@w,-1,1)))) for w in Pm]
Qm = V[idx]
H = Pm.T@Qm; U,S_,Vt = svd(H); d = np.sign(np.linalg.det(Vt.T@U.T))
R = Vt.T@np.diag([1,1,d])@U.T
Pr = (R@Pm.T).T
res = np.degrees(np.arccos(np.clip(np.sum(Pr*Qm,axis=1),-1,1)))
print(f"   對齊殘餘: mean {res.mean():.5f}°, max {res.max():.5f}°, std {res.std():.5f}°")
# 3. 檔案距離譜 vs 軌道距離譜
specF = np.sort(np.degrees(np.arccos(np.clip(V@V.T,-1,1)))[0])
specO = np.sort(np.degrees(np.arccos(np.clip(O@O.T,-1,1)))[0])
print(f"\n3. 距離譜 (由第 0 點): 檔案 vs 自身軌道 max|Δ| = {np.abs(specF-specO).max():.6f}°")
print(f"   檔案前 8: {np.round(specF[:8],4)}")
print(f"   軌道前 8: {np.round(specO[:8],4)}")
# 4. 檢查 60 點係咪 orbit of (209,-57) 冷斑
from astropy.coordinates import SkyCoord
import astropy.units as u
cs = SkyCoord(l=209*u.deg, b=-57*u.deg, frame='galactic').icrs
vcs = np.array([math.cos(math.radians(cs.dec.deg))*math.cos(math.radians(cs.ra.deg)),
                math.cos(math.radians(cs.dec.deg))*math.sin(math.radians(cs.ra.deg)),
                math.sin(math.radians(cs.dec.deg))])
specC = np.sort(np.degrees(np.arccos(np.clip(np.array([m@vcs for m in I_rot])@np.array([m@vcs for m in I_rot]).T,-1,1)))[0])
print(f"\n4. 檔案距離譜 vs (209,−57) 冷斑軌道 max|Δ| = {np.abs(specF-specC).max():.6f}°")
print(f"   冷斑軌道前 8: {np.round(specC[:8],4)}")
# 5. 精確軌道自身 sym
print(f"\n5. sym_group(精確冷斑軌道): {len(sym_arccos(np.array([m@vcs for m in I_rot]), 1e-6))} (期望 60)")
