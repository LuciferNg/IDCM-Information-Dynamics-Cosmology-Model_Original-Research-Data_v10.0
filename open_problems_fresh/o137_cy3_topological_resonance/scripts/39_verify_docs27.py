#!/usr/bin/env python3
"""O137 — docs/27 A₅ 驗證 獨立核對"""
import numpy as np, math
from math import isclose
from pathlib import Path
from collections import Counter

PASS, FAIL = [], []
def ck(n, got, exp, tol=1e-3):
    ok = isclose(got, exp, rel_tol=tol, abs_tol=tol) if isinstance(exp,(int,float)) else got==exp
    (PASS if ok else FAIL).append(n)
    print(f"  {'✅' if ok else '❌'} {n} = {got}" + ("" if ok else f"  ❗EXP={exp}"))

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
raw = np.loadtxt(ROOT/"cmb_cold_spot/data/a5_nodes.txt")
ra, dec = np.radians(raw[:,0]), np.radians(raw[:,1])
V = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
V /= np.linalg.norm(V,axis=1,keepdims=True)
phi=(1+math.sqrt(5))/2
def rot(ax,an):
    a=np.array(ax,float); a/=np.linalg.norm(a)
    K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3)+math.sin(an)*K+(1-math.cos(an))*K@K
R1,R2=rot([0,1,phi],2*math.pi/5), rot([1,1,1],2*math.pi/3)
G=[np.eye(3)]; fr=[np.eye(3)]
while fr:
    new=[]
    for g in fr:
        for h in (R1,R2):
            p=h@g
            if not any(np.allclose(p,q,atol=1e-9) for q in G): G.append(p); new.append(p)
    fr=new

print("=== §1 幾何 ===")
ck("|I| = 60", len(G), 60, 0)
devs=[]
for g in G:
    D=(V@g.T)@V.T; idx=np.argmax(D,axis=1)
    devs.append(np.degrees(np.arccos(np.clip(D[np.arange(60),idx],-1,1))).max())
ck("群作用下最大偏差 = 0.000097°", max(devs), 0.000097, 1e-2)
Dm=np.arccos(np.clip(V@V.T,-1,1)); np.fill_diagonal(Dm,np.pi)
nn=np.degrees(np.sort(Dm,axis=1)[:,0])
ck("最近鄰 min = 26.0913°", nn.min(), 26.0913, 1e-4)
ck("最近鄰 max = 26.0914°", nn.max(), 26.0914, 1e-4)

print("\n=== §2 Molien ===")
LMAX=26
ser=np.zeros(LMAX+1)
for g in G:
    th=math.acos(max(-1,min(1,(np.trace(g)-1)/2))); c=math.cos(th)
    U=[1.0]
    if LMAX>=1: U.append(2*c)
    for k in range(2,LMAX+1): U.append(2*c*U[-1]-U[-2])
    ser+=np.convolve(np.ones(LMAX+1), np.array(U[:LMAX+1]))[:LMAX+1]
ser/=len(G); dim=np.round(ser).astype(int)
h=np.array([dim[l]-(dim[l-2] if l>=2 else 0) for l in range(LMAX+1)])
h0={1,2,3,4,5,7,8,9,11,13,14,17,19,23}
h1={6,10,12,15,16,18,20,21,22,24,25,26}
ck("h(l)=0 集合", sorted(l for l in range(1,LMAX+1) if h[l]==0), sorted(h0))
ck("h(l)=1 集合", sorted(l for l in range(1,LMAX+1) if h[l]==1), sorted(h1))

print("\n=== §2-3 動差 + 選擇 ===")
Tn=np.polynomial.chebyshev.Chebyshev.basis; Pl=np.polynomial.legendre.Legendre.basis
lb=(math.radians(209.0),math.radians(-57.0))
CW=np.array([math.cos(lb[1])*math.cos(lb[0]),math.cos(lb[1])*math.sin(lb[0]),math.sin(lb[1])])
from astropy.coordinates import SkyCoord, Galactic
import astropy.units as u
cs=SkyCoord(l=209*u.deg,b=-57*u.deg,frame=Galactic).icrs
CT=np.array([math.cos(math.radians(cs.dec.deg))*math.cos(math.radians(cs.ra.deg)),
             math.cos(math.radians(cs.dec.deg))*math.sin(math.radians(cs.ra.deg)),
             math.sin(math.radians(cs.dec.deg))])
ck("node0 = 冷斑 (角距 <1e-4°)", math.degrees(math.acos(np.clip(np.dot(V[0],CT),-1,1))), 0.0, 1e-4)
ck("錯軸偏離真冷斑 = 100.8843°", math.degrees(math.acos(np.clip(np.dot(CW,CT),-1,1))), 100.8843, 1e-4)
xw,xt=V@CW,V@CT
docs19={6:0.873778,10:0.267446,12:-5.288945,15:0.199879,16:-1.175282}
for l,e in docs19.items(): ck(f"docs19 Σ P_{l} (錯軸) = {e}", float(Pl(l)(xw).sum()), e, 1e-5)
corr={6:0.272434,10:0.013661,12:3.307513,15:2.897525,16:6.287750}
for l,e in corr.items(): ck(f"正確軸 Σ P_{l} = {e}", float(Pl(l)(xt).sum()), e, 1e-5)
for l in range(1,6): ck(f"5-design: Σ P_{l} ≈ 0", abs(float(Pl(l)(xw).sum()))<1e-5, True)
def sel(pts, ax, tol=1e-4):
    x=pts@ax; return [n for n in range(1,45) if abs(float(Tn(n)(x).sum())-len(pts)*(0 if n%2 else 1/(1-n*n)))<tol]
ck("錯軸選擇 = 9 模式", sel(V,CW), [1,2,3,4,5,7,9,11,13])
ck("正確軸選擇 = 9 模式", sel(V,CT), [1,2,3,4,5,7,9,11,13])

print("\n=== §4 軸獨立性 ===")
rng=np.random.default_rng(20260830)
cnt=Counter()
for _ in range(1000):
    c=rng.normal(size=3); c/=np.linalg.norm(c)
    cnt[tuple(sel(V,c,tol=1e-3))]+=1
ck("973/1000 給同一 9 模式", cnt[tuple([1,2,3,4,5,7,9,11,13])], 973, 0.02)

print("\n=== §5 判別力 ===")
ico=set()
for b in [(0,1,phi),(0,1,-phi),(0,-1,phi),(0,-1,-phi)]:
    for p in [(0,1,2),(1,2,0),(2,0,1)]: ico.add(tuple(b[i] for i in p))
ICO=np.array(sorted(ico),float); ICO/=np.linalg.norm(ICO,axis=1,keepdims=True)
dod=set()
for s1 in (1,-1):
    for s2 in (1,-1):
        for s3 in (1,-1): dod.add((s1,s2,s3))
for b in [(0,1/phi,phi),(0,1/phi,-phi),(0,-1/phi,phi),(0,-1/phi,-phi)]:
    for p in [(0,1,2),(1,2,0),(2,0,1)]: dod.add(tuple(b[i] for i in p))
DOD=np.array(sorted(dod),float); DOD/=np.linalg.norm(DOD,axis=1,keepdims=True)
ck("Icosahedron(12) → 24 模式", len(sel(ICO,CT,tol=1e-3)), 24)
ck("Dodecahedron(20) → 24 模式", len(sel(DOD,CT,tol=1e-3)), 24)
cnts=[]
for _ in range(500):
    R=rng.normal(size=(60,3)); R/=np.linalg.norm(R,axis=1,keepdims=True)
    cnts.append(len(sel(R,CT,tol=1e-3)))
cnts=np.array(cnts)
ck("隨機 60 點 max 模式數 ≤ 2", int(cnts.max())<=2, True)
ck("P(≥9) = 0.0000", float(np.mean(cnts>=9)), 0.0, 1.0)

print("\n=== §6 Legendre 分量 ===")
xq,wq=np.polynomial.legendre.leggauss(120)
f=Tn(6)(xq); a6=(2*6+1)/2*np.sum(wq*f*Pl(6)(xq))
ck("n=6: a₆ = 2.2165", a6, 2.21645022, 1e-6)
f=Tn(8)(xq); a6b=(2*6+1)/2*np.sum(wq*f*Pl(6)(xq))
ck("n=8: a₆ = −1.1821", a6b, -1.18210678, 1e-6)
f=Tn(15)(xq); a15=(2*15+1)/2*np.sum(wq*f*Pl(15)(xq))
ck("n=15: a₁₅ = 3.4611", a15, 3.46105915, 1e-6)

print("\n=== §7 擾動 (多 seed 分佈) ===")
for eps in [0.0, 0.01, 0.1, 1.0]:
    res=[]
    for sd in range(5):
        r=np.random.default_rng(1000+sd)
        P=V+r.normal(scale=math.radians(eps),size=V.shape); P/=np.linalg.norm(P,axis=1,keepdims=True)
        res.append(len(sel(P,CT,tol=1e-3)))
    print(f"  擾動 {eps}°: 選中數 = {res}  (5 seeds)")
    if eps==0.0: ck("擾動 0° → 9 模式 (全部 seed)", all(x==9 for x in res), True)
    if eps==0.01: ck("擾動 0.01° → 全部 ≤ 5 模式", all(x<=5 for x in res), True)
    if eps==0.1: ck("擾動 0.1° → 全部 ≤ 1 模式", all(x<=1 for x in res), True)

print(f"\n{'='*56}\nPASS: {len(PASS)}, FAIL: {len(FAIL)}")
for f in FAIL: print(f"  ❌ {f}")
print('='*56)
