#!/usr/bin/env python3
"""
診斷: m_15 為何會 ≈ 0? 機制鑑定

假說:
  λ(v) := ⟨P_15(v··), I_15⟩ 係 v 嘅 15 次 I-不變調和 ⟹ λ = κ I_15
  m_15(v; c) = λ(v) I_15(c)  ⟹  m_15(v; v) = κ I_15(v)² ≥ 0  (完全平方)
  若 I_15 = δ = ∏_{a∈A2}(a·x) (15 個鏡面線性型之積)
     ⟹ m_15(v;v) = 0 ⟺ v 落在某鏡面上 ⟺ achiral

檢驗:
  (1) m_15(v;v) 係否恆 ≥ 0?
  (2) m_15(v;v) / δ(v)² 係否常數?
  (3) 模式數 24 嘅種子係否就係近鏡面種子?
"""
import numpy as np, math
from collections import Counter

phi=(1+5**0.5)/2
def rot(ax,an):
    a=np.array(ax,float); a/=np.linalg.norm(a)
    K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3)+math.sin(an)*K+(1-math.cos(an))*K@K
G=[np.eye(3)]; fr=[np.eye(3)]
R1,R2=rot([0,1,phi],2*math.pi/5), rot([1,1,1],2*math.pi/3)
while fr:
    new=[]
    for g in fr:
        for h in (R1,R2):
            p=h@g
            if not any(np.allclose(p,q,atol=1e-9) for q in G): G.append(p); new.append(p)
    fr=new
def order(g):
    M=g.copy(); k=1
    while not np.allclose(M,np.eye(3),atol=1e-8) and k<12: M=M@g; k+=1
    return k
A2=[]
for g in G:
    if order(g)==2:
        w,Vv=np.linalg.eig(g); ax=np.real(Vv[:,np.argmin(np.abs(w-1))]); ax/=np.linalg.norm(ax)
        if not any(abs(abs(ax@u)-1)<1e-8 for u in A2): A2.append(ax)
A2=np.array(A2)
Tn=np.polynomial.chebyshev.Chebyshev.basis
Pl=np.polynomial.legendre.Legendre.basis
def a0(n): return 0.0 if n%2 else 1.0/(1-n*n)
def orbit(v): return np.unique(np.round(np.array([g@v for g in G]),10),axis=0)
def modes(P,c,tol=1e-3,nmax=44):
    return [n for n in range(1,nmax+1) if abs(float(Tn(n)(P@c).sum())-len(P)*a0(n))<tol]
def m(P,j,c): return float(Pl(j)(P@c).sum())

rng=np.random.default_rng(20260830)
N=800
rec=[]
for _ in range(N):
    v=rng.normal(size=3); v/=np.linalg.norm(v)
    o=orbit(v)
    if len(o)!=60: continue
    rec.append((v, o, len(modes(o,o[0])), m(o,15,o[0]), float(np.prod(A2@v)), float(np.abs(A2@v).min())))
print(f"有效樣本 = {len(rec)}")

print("\n=== (1) m_15(v;v) 恆 ≥ 0? ===")
vals=np.array([r[3] for r in rec])
print(f"  min = {vals.min():.6e}   max = {vals.max():.6e}   #負 = {int((vals<0).sum())}")
print(f"  ⟹ {'✅ 恆非負 (與 κ I₁₅² 一致)' if (vals<-1e-9).sum()==0 else '🔴 有負值'}")

print("\n=== (2) m_15(v;v) / δ(v)² 係否常數? ===")
rat=[r[3]/r[4]**2 for r in rec if abs(r[4])>1e-30]
rat=np.array(rat)
rat=rat[np.isfinite(rat)]
print(f"  m_15/δ² 樣本數 = {len(rat)}")
if len(rat):
    print(f"    min={rat.min():.6e}  median={np.median(rat):.6e}  max={rat.max():.6e}")
    print(f"    max/median = {rat.max()/np.median(rat):.2f}")
    print(f"    ⚠️ 大範圍 ⟹ m_15 唔係簡單 ∝ δ²")

print("\n=== (3) 模式數 vs 距最近鏡面 ===")
by=Counter(r[2] for r in rec)
print(f"  模式數分佈: {dict(sorted(by.items()))}")
print(f"\n  {'模式數':>6} {'樣本':>5} {'median min|a·v|':>18} {'median |δ|':>14} {'median m₁₅':>14}")
for mm in sorted(by):
    sub=[r for r in rec if r[2]==mm]
    print(f"  {mm:>6} {len(sub):>5} {np.median([s[5] for s in sub]):>18.3e} {np.median([abs(s[4]) for s in sub]):>14.3e} {np.median([s[3] for s in sub]):>14.3e}")

print("\n=== (4) 關鍵: 模式數 9 vs >9 嘅 m₁₅ 尺度 ===")
nine=[r[3] for r in rec if r[2]==9]
more=[r[3] for r in rec if r[2]>9]
print(f"  9 模式 (n={len(nine)}): m₁₅ median = {np.median(nine):.4e}   min = {min(nine):.4e}")
if more: print(f"  >9 模式 (n={len(more)}): m₁₅ median = {np.median(more):.4e}   max = {max(more):.4e}")
print(f"  ⟹ 兩組 m₁₅ 尺度分離 ⟹ 判準係 |a₁₅ m₁₅| < tol 嘅容差效應, 而 m₁₅ 本身連續")

print("\n=== (5) 決定性測試: 用相對容差重算 ===")
def modes_rel(P,c,eps=1e-6,nmax=44):
    """相對容差: |D_n| / max_j |a_j(n) m_j(c)| < eps"""
    x=P@c; out=[]
    for n in range(1,nmax+1):
        D=float(Tn(n)(x).sum())-len(P)*a0(n)
        if abs(D)<1e-14: out.append(n); continue
        # 各 j 分量尺度
        scale=0.0
        for j in range(n,1,-2):
            aj=float(np.polynomial.legendre.Legendre.basis(j)(1.0))  # placeholder
        # 用 Σ|T_n| 作尺度
        scale=np.abs(Tn(n)(x)).sum()
        if abs(D) < eps*scale: out.append(n)
    return out
cnt=Counter(len(modes_rel(r[1],r[0])) for r in rec)
print(f"  相對容差 (eps=1e-6) 模式數分佈: {dict(sorted(cnt.items()))}")
