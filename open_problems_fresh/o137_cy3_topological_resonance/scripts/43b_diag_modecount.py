#!/usr/bin/env python3
"""診斷: 1500 個 chiral 60-軌道嘅模式數分佈係結構定容差偽影?"""
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
Tn=np.polynomial.chebyshev.Chebyshev.basis
Pl=np.polynomial.legendre.Legendre.basis
def a0(n): return 0.0 if n%2 else 1.0/(1-n*n)

def orbit(v):
    return np.unique(np.round(np.array([g@v for g in G]),10), axis=0)

def modes(P,c,tol=1e-3,nmax=44):
    x=P@c
    return [n for n in range(1,nmax+1) if abs(float(Tn(n)(x).sum())-len(P)*a0(n))<tol]

def D(P,c,n):
    return float(Tn(n)(P@c).sum()) - len(P)*a0(n)

rng=np.random.default_rng(20260830)
# 找幾個樣本
samples={}
for _ in range(4000):
    v=rng.normal(size=3); v/=np.linalg.norm(v)
    o=orbit(v)
    if len(o)!=60: continue
    m=len(modes(o,o[0]))
    if m not in samples: samples[m]=(v,o,m)
    if len(samples)>=6 and 9 in samples and max(samples)>=20: break

print("=== 樣本: 各模式數嘅 D_n 值 (n=15,17,19,21) ===")
print(f"{'模式數':>6} {'D_15':>12} {'D_17':>12} {'D_19':>12} {'D_21':>12} {'D_23':>12}")
for m in sorted(samples):
    v,o,_=samples[m]
    print(f"{m:>6} " + " ".join(f"{D(o,o[0],n):>12.4e}" for n in [15,17,19,21,23]))

print("\n=== m_j(c) 值 (j = h(j)≠0 者), 樣本 9 模式 vs 24 模式 ===")
J=[6,10,12,15,16,18,20,21,22,24,25,26]
for m in [9,24]:
    if m not in samples: continue
    v,o,_=samples[m]
    print(f"\n  模式數 {m}:  c = v₀ = ({v[0]:.4f},{v[1]:.4f},{v[2]:.4f})")
    for j in J:
        val=float(Pl(j)(o@o[0]).sum())
        print(f"     m_{j:<3} = {val:>14.6e}")

print("\n=== 大 n 時 Σ T_n 嘅自然尺度 ===")
v,o,_=samples.get(9,(None,None,None))
if o is not None:
    print(f"  9-模式樣本: {'n':>4} {'Σ T_n':>14} {'N·a₀(n)':>12} {'D_n':>14} {'|T_n| max':>12}")
    for n in [1,3,5,7,9,11,13,15,17,21,25,31,43]:
        s=float(Tn(n)(o@o[0]).sum()); t=len(o)*a0(n)
        print(f"  {'':>12}{n:>4} {s:>14.6e} {t:>12.6f} {s-t:>14.4e} {np.abs(Tn(n)(o@o[0])).max():>12.4f}")

print("\n=== 結論判定 ===")
print("  若 24-模式樣本嘅 m_15, m_21, ... 全部 ~0 ⟹ 結構性 (該種子嘅 m_j 恰好消失)")
print("  若 m_j 非零但 D_n 細 ⟹ 容差偽影")
