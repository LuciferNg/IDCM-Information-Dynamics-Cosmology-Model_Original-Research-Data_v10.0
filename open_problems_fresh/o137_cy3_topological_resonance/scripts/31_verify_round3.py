#!/usr/bin/env python3
"""O137 — Round 3 verification (docs/23-25) 獨立核對"""
import numpy as np
from math import sin, pi, isclose
from itertools import permutations

PASS, FAIL = [], []
def ck(name, got, exp, tol=1e-3):
    ok = isclose(got, exp, rel_tol=tol) if isinstance(exp,(int,float)) else got==exp
    (PASS if ok else FAIL).append(name)
    print(f"  {'✅' if ok else '❌'} {name} = {got}" + ("" if ok else f"  ❗EXP={exp}"))

M0 = 27.900915
def gamma_n(n): return 4*sin(n*pi/88)**2
MASS = {'e':0.5110,'u':2.1600,'d':4.6700,'s':93.40,'mu':105.6584,
        'c':1270.0,'tau':1776.86,'b':4180.0,'t':172690.0}

print("=== A₅ 動差準則 (O136 docs/19) ===")
odd = [n for n in range(1,14) if n%2==1]
even = [n for n in range(2,5) if n%2==0]
A5 = sorted(odd+even)
ck("奇 n≤13 = 7 個 (L₄)", len(odd), 7)
ck("偶 n≤4 = 2 個", len(even), 2)
ck("A₅ 集 = {1,2,3,4,5,7,9,11,13}", A5, [1,2,3,4,5,7,9,11,13])
ck("A₅ = 世代塊 {1,2,3}/{4,5,7}/{9,11,13}", [A5[0:3],A5[3:6],A5[6:9]],
   [[1,2,3],[4,5,7],[9,11,13]])

print("\n=== docs/24: mod-8 規則 vs A₅ 衝突 ===")
def odd_part(n):
    while n%2==0: n//=2
    return n
viol = [n for n in A5 if odd_part(n)%8 not in [1,5,7]]
ck("A₅ 被 mod-8 規則排除 = [3,11]", viol, [3,11])

print("\n=== docs/24: Φ 目錄枚舉 (0 有效指派) ===")
X3=[1,5,9]; X3P=[0,1,3,4,6,7]
PHI={}
for i,a in enumerate(X3):
    for j,b in enumerate(X3P): PHI[(i,j)]=1+a*b
CF_FULL=[(k,v/d) for k,v in PHI.items() for d in [1,2,4]]
valid=0; total=0
for trio in permutations(CF_FULL,3):
    total+=1; ok=True
    for p,(k,Cf) in zip(['e','mu','tau'],trio):
        gt=MASS[p]/(M0*Cf)
        b=min(range(1,45), key=lambda n: abs(gamma_n(n)-gt))
        if abs(gamma_n(b)-gt)/gt > 0.01: ok=False; break
    if ok: valid+=1
ck("枚舉總數 = 148824", total, 148824)
ck("有效指派 = 0", valid, 0)
ck("C_e 需要值 = 3.5941", MASS['e']/(M0*gamma_n(1)), 3.5941, 1e-4)
ck("Φ 目錄無 3.5941 (最近 3.5)", min(sorted(set(v/d for v in PHI.values() for d in [1,2,4])), key=lambda c: abs(c-3.5941)), 3.5, 1e-6)

print("\n=== docs/25: A₅ 升序配對 C_f ===")
order = sorted(MASS, key=lambda p: MASS[p])
C = [MASS[p]/(M0*gamma_n(n)) for p,n in zip(order, A5)]
ck("C_f(e) = 3.5941", C[0], 3.5941, 1e-4)
ck("C_f(u) = 3.8029", C[1], 3.8029, 1e-4)
ck("C_f(d) = 3.6620", C[2], 3.6620, 1e-4)
ck("Gen1 跨度 = 1.058", max(C[:3])/min(C[:3]), 1.058, 1e-3)
ck("Gen2 跨度 = 6.196", max(C[3:6])/min(C[3:6]), 6.196, 1e-3)
ck("Gen3 跨度 = 48.38", max(C[6:9])/min(C[6:9]), 48.38, 1e-3)

print("\n=== docs/25: 每世代冪律 ===")
blocks={1:[0,1,2],2:[3,4,5],3:[6,7,8]}
exp_p={1:(1.0120,0.0208),2:(2.4709,0.4316),3:(6.3992,0.7835)}
for g,idx in blocks.items():
    ps=[order[i] for i in idx]; ns=[A5[i] for i in idx]
    xs=np.log([gamma_n(n) for n in ns]); ys=np.log([MASS[p] for p in ps])
    A=np.vstack([xs,np.ones_like(xs)]).T
    coef,*_=np.linalg.lstsq(A,ys,rcond=None)
    rms=float(np.sqrt(np.mean((ys-A@coef)**2)))
    ck(f"Gen{g} p = {exp_p[g][0]}", coef[0], exp_p[g][0], 1e-3)
    ck(f"Gen{g} RMS = {exp_p[g][1]}", rms, exp_p[g][1], 1e-3)

print("\n=== docs/25: null test P = 0.0002 ===")
rng=np.random.default_rng(20260830)
g3=[gamma_n(1),gamma_n(2),gamma_n(3)]
obs=max(C[:3])/min(C[:3])
cnt=0;N=20000
for _ in range(N):
    ms=10**rng.uniform(np.log10(0.3),np.log10(8.0),3)
    rr=[ms[i]/g3[i] for i in range(3)]
    if max(rr)/min(rr)<=obs: cnt+=1
ck("null P = 0.0002", cnt/N, 0.0002, 0.3)

print("\n=== docs/25: 雙因子 RMS = 0.8789 ===")
E=np.array([gamma_n(n) for n in range(1,45)])
V=np.zeros((44,44))
for i in range(44):
    for j in range(44):
        if (i+1)%2!=(j+1)%2: V[i,j]=1.0/(abs(E[i]-E[j])+1e-9)
D2=np.abs(np.array([sum(V[n,m]*V[m,n]/(E[n]-E[m]) for m in range(44) if m!=n and V[n,m]!=0) for n in range(44)]))
mass=np.array([MASS[p] for p in order])
X=np.vstack([np.ones(9),np.log([gamma_n(n) for n in A5]),np.log([D2[n-1] for n in A5])]).T
coef,*_=np.linalg.lstsq(X,np.log(mass),rcond=None)
rms=float(np.sqrt(np.mean((np.log(mass)-X@coef)**2)))
ck("雙因子 RMS = 0.8789", rms, 0.8789, 1e-3)

print(f"\n{'='*60}\nPASS: {len(PASS)}, FAIL: {len(FAIL)}")
if FAIL:
    for f in FAIL: print(f"  ❌ {f}")
print('='*60)
