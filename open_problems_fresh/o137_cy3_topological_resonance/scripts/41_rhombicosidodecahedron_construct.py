#!/usr/bin/env python3
"""
小斜方截半二十面體 (Rhombicosidodecahedron) 第一性原理構造
============================================================
展開正二十面體: 每個面 → 一個三角形; 每個邊 → 一個正方形; 每個頂點 → 一個五邊形
頂點數 = 20 面 × 3 = 60 = |(face, vertex) 關聯|

構造: 對每個面 f (中心 ĉ) 及每個頂點 v:
  p̂ = normalize(v − (v·ĉ)ĉ)      (v 在 ⊥ ĉ 平面嘅分量方向)
  point = cos(θ₃) ĉ + sin(θ₃) p̂
其中 θ₃ = 頂點到三角形中心嘅角 = arccos(√(R² − (a/√3)²)/R)
"""
import numpy as np, math, itertools
phi=(1+5**0.5)/2
def norm(P): return P/np.linalg.norm(P,axis=1,keepdims=True)
def rot(ax,an):
    a=np.array(ax,float); a/=np.linalg.norm(a)
    K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3)+math.sin(an)*K+(1-math.cos(an))*K@K

# 正二十面體 (邊長 2, 外接半徑 √(1+φ²))
ico=set()
for b in [(0,1,phi),(0,1,-phi),(0,-1,phi),(0,-1,-phi)]:
    for p in [(0,1,2),(1,2,0),(2,0,1)]: ico.add(tuple(round(b[i],10) for i in p))
ICO=np.array(sorted(ico),float)
R_ico=np.linalg.norm(ICO[0])
ICO=ICO/R_ico
print(f"正二十面體: {len(ICO)} 頂點, 邊長角距 = {np.degrees(np.arccos(1-4/(2*R_ico**2))):.4f}°")

# 面: 兩兩距離 = 邊長 嘅三元組
d=np.linalg.norm(ICO[:,None,:]-ICO[None,:,:],axis=2)
e=np.min(d[d>1e-9])
faces=[c for c in itertools.combinations(range(12),3)
       if all(abs(d[i,j]-e)<1e-6 for i,j in itertools.combinations(c,2))]
print(f"面數 = {len(faces)}")

# RH 外接半徑 (邊長 2)
R_rh = math.sqrt(11+4*math.sqrt(5))/2*2/2*2  # = 2.2329505094... × 2
R_rh = 2*math.sqrt(11+4*math.sqrt(5))/2
# θ₃: 頂點到三角形中心
cos3 = math.sqrt(R_rh**2 - (2/math.sqrt(3))**2)/R_rh
th3 = math.acos(cos3)
print(f"R_rh = {R_rh:.6f}   θ₃ = {math.degrees(th3):.6f}°")
cos5 = math.sqrt(R_rh**2 - (2/(2*math.sin(math.pi/5)))**2)/R_rh
print(f"θ₅ (頂點到五邊形中心) = {math.degrees(math.acos(cos5)):.6f}°")

pts=[]
for f in faces:
    c=ICO[list(f)].sum(0); c/=np.linalg.norm(c)
    for i in f:
        v=ICO[i]; p=v-(v@c)*c; p/=np.linalg.norm(p)
        pts.append(math.cos(th3)*c+math.sin(th3)*p)
pts=np.array(pts)
# 去重
uniq=[]
for p in pts:
    if not any(np.allclose(p,q,atol=1e-9) for q in uniq): uniq.append(p)
RH=norm(np.array(uniq))
print(f"RH 頂點 (去重後) = {len(RH)}")

def dev(P,g):
    Q=norm(P@g.T); D=np.clip(Q@P.T,-1,1); return np.degrees(np.arccos(D.max(axis=1))).max()
G=[np.eye(3)]; fr=[np.eye(3)]
R1,R2=rot([0,1,phi],2*math.pi/5), rot([1,1,1],2*math.pi/3)
while fr:
    new=[]
    for g in fr:
        for h in (R1,R2):
            p=h@g
            if not any(np.allclose(p,q,atol=1e-9) for q in G): G.append(p); new.append(p)
    fr=new
print(f"|I| = {len(G)}")
print(f"RH I-不變性偏差 = {max(dev(RH,g) for g in G):.6f}°")
M=np.clip(RH@(-RH).T,-1,1)
print(f"RH 中心對稱 max 角距 = {np.degrees(np.arccos(M.max(axis=1))).max():.6f}°")
# 邊結構
dd=np.degrees(np.arccos(np.clip(RH@RH.T,-1,1))); np.fill_diagonal(dd,1e9)
A=(dd<dd.min()*1.05).astype(int); np.fill_diagonal(A,0)
print(f"RH 最近鄰角距 = {dd.min():.6f}°, 度數 {A.sum(1).min()}-{A.sum(1).max()}, 邊 {int(A.sum()//2)}, 三角形 {int(np.trace(A@A@A)//6)}")
Tn=np.polynomial.chebyshev.Chebyshev.basis
def modes(P,tol=1e-3,nmax=44):
    x=P@P[0]
    return [n for n in range(1,nmax+1) if abs(float(Tn(n)(x).sum())-len(P)*(0 if n%2 else 1/(1-n*n)))<tol]
print(f"RH 模式數 = {len(modes(RH))}  = {modes(RH) if len(modes(RH))<=12 else str(modes(RH)[:6])+' ... '+str(modes(RH)[-3:])}")

# 與 IDCM 節點比較
raw=np.loadtxt("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt")
ra,dec=np.radians(raw[:,0]),np.radians(raw[:,1])
V=np.column_stack([np.cos(dec)*np.cos(ra),np.cos(dec)*np.sin(ra),np.sin(dec)])
V/=np.linalg.norm(V,axis=1,keepdims=True)
D=np.degrees(np.arccos(np.clip(V@RH.T,-1,1)))
print(f"\nIDCM 節點 → 最近 RH 頂點: min={D.min():.4f}° mean={D.mean():.4f}°")
print(f"RH 頂點 → 最近 IDCM 節點: min={D.min(axis=0).min():.4f}° mean={D.min(axis=0).mean():.4f}° max={D.min(axis=0).max():.4f}°")
MV=np.clip(V@(-V).T,-1,1)
print(f"IDCM 節點 中心對稱 max 角距 = {np.degrees(np.arccos(MV.max(axis=1))).max():.6f}°")
print(f"IDCM 節點 模式數 = {len(modes(V))} = {modes(V)}")
np.save("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/rhombicosidodecahedron_unit.npy", RH)
print("\n已存 data/rhombicosidodecahedron_unit.npy")
