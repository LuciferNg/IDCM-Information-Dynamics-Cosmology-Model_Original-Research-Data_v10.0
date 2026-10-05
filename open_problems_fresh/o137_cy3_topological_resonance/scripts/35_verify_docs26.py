#!/usr/bin/env python3
"""O137 — docs/26 標度律評估 獨立核對"""
import numpy as np
from math import sin, pi, isclose
from itertools import permutations
from collections import Counter

PASS, FAIL = [], []
def ck(n, got, exp, tol=1e-3):
    ok = isclose(got, exp, rel_tol=tol) if isinstance(exp,(int,float)) else got==exp
    (PASS if ok else FAIL).append(n)
    print(f"  {'✅' if ok else '❌'} {n} = {got}" + ("" if ok else f" ❗EXP={exp}"))

M0 = 27.900915
def gamma_n(n): return 4*sin(n*pi/88)**2
def omega_n(n): return 2*sin(n*pi/88)
MASS = {'e':0.5110,'u':2.1600,'d':4.6700,'s':93.40,'mu':105.6584,
        'c':1270.0,'tau':1776.86,'b':4180.0,'t':172690.0}
A5 = [1,2,3,4,5,7,9,11,13]
order = ['e','u','d','s','mu','c','tau','b','t']
blocks = {1:[0,1,2],2:[3,4,5],3:[6,7,8]}
def xy(g):
    idx=blocks[g]
    return (np.log([gamma_n(A5[i]) for i in idx]), np.log([MASS[order[i]] for i in idx]))

print("=== §2 p_g 與 SE ===")
pg, seg = {}, {}
for g in [1,2,3]:
    x,y=xy(g); Sxx=float(np.sum((x-x.mean())**2))
    A=np.vstack([x,np.ones_like(x)]).T
    c,*_=np.linalg.lstsq(A,y,rcond=None)
    SSE=float(np.sum((y-A@c)**2))
    pg[g]=c[0]; seg[g]=float(np.sqrt((SSE/(len(x)-2))/Sxx))
ck("p1 = 1.0120", pg[1], 1.0120, 1e-4); ck("SE(p1) = 0.0230", seg[1], 0.0230, 5e-3)
ck("p2 = 2.4709", pg[2], 2.4709, 1e-4); ck("SE(p2) = 0.9503", seg[2], 0.9503, 1e-3)
ck("p3 = 6.3992", pg[3], 6.3992, 1e-4); ck("SE(p3) = 2.7461", seg[3], 2.7461, 1e-3)

print("\n=== §3 階梯步 z ===")
for a,b,e in [(1,2,1.53),(2,3,1.35),(1,3,1.96)]:
    S=float(np.sqrt(seg[a]**2+seg[b]**2))
    ck(f"z(p{b}-p{a}) = {e}", (pg[b]-pg[a])/S, e, 1e-2)

print("\n=== §4 階梯 F-test ===")
def sse_fixed(g,p):
    x,y=xy(g); r=y-p*x; r=r-r.mean(); return float(np.sum(r**2))
SSE_free=sum(sse_fixed(g,pg[g]) for g in [1,2,3])
ck("SSE_free = 2.4017", SSE_free, 2.4017, 1e-4)
for nm,ps,e in [('(5/2)^(g-1)',[1,2.5,6.25],2.4080),('F_{2g+1}/2',[1,2.5,6.5],2.4050),
                ('g²',[1,4,9],5.5007),('g!',[1,2,6],2.5781)]:
    S=sum(sse_fixed(g,ps[g-1]) for g in [1,2,3])
    ck(f"SSE({nm}) = {e}", S, e, 1e-3)
ck("最佳 SSE 唔係 (5/2)^(g-1)", sum(sse_fixed(g,[1,2.5,6.5][g-1]) for g in [1,2,3]) <
   sum(sse_fixed(g,[1,2.5,6.25][g-1]) for g in [1,2,3]), True)

print("\n=== §5 約定依賴 ===")
for g,e in [(1,2.0240),(2,4.9417),(3,12.7985)]:
    xg,y=xy(g); xw=np.log([omega_n(A5[i]) for i in blocks[g]])
    ck(f"p_ω(g={g}) = {e}", np.polyfit(xw,y,1)[0], e, 1e-4)

print("\n=== §6 模型比較 ===")
yall=np.log([MASS[p] for p in order]); xall=np.log([gamma_n(n) for n in A5])
def sse(pf, pergen):
    t=0.0
    for g in [1,2,3]:
        x,y=xy(g)
        pred = pf(g)*x + ((y-pf(g)*x).mean() if pergen else float(np.mean(yall-xall)))
        t+=float(np.sum((y-pred)**2))
    return t
ck("M1 SSE = 51.7935", sse(lambda g:1.0,False), 51.7935, 1e-4)
ck("M2 SSE = 10.8595", sse(lambda g:1.0,True), 10.8595, 1e-4)
ck("M3 SSE = 2.4017", sse(lambda g:pg[g],True), 2.4017, 1e-4)
ck("M4 SSE = 2.4080", sse(lambda g:(5/2)**(g-1),True), 2.4080, 1e-4)
ck("M4 RMS = 0.5173", float(np.sqrt(sse(lambda g:(5/2)**(g-1),True)/9)), 0.5173, 1e-3)

print("\n=== §7 配對搜索 ===")
PHI={(i,j):1+a*b for i,a in enumerate([1,5,9]) for j,b in enumerate([0,1,3,4,6,7])}
CAT=sorted(set(v/d for v in PHI.values() for d in [1,2,4]))
gparts={1:['e','u','d'],2:['s','mu','c'],3:['tau','b','t']}
cnt=Counter(); best=0
for p1 in permutations(blocks[1]):
    for p2 in permutations(blocks[2]):
        for p3 in permutations(blocks[3]):
            pr={1:p1,2:p2,3:p3}; tot=0
            for g in [1,2,3]:
                for pi_,ai in zip(gparts[g],pr[g]):
                    Cf=MASS[pi_]/(M0*gamma_n(A5[ai]))
                    if any(abs(c-Cf)/Cf<0.01 for c in CAT): tot+=1
            cnt[tot]+=1; best=max(best,tot)
ck("配對總數 = 216", sum(cnt.values()), 216)
ck("最佳命中 = 1", best, 1)
ck("分佈 {0:72, 1:144}", dict(cnt), {0:72,1:144})
ck("Φ 目錄大小 = 36", len(CAT), 36)
ck("Φ 目錄 max = 64", max(CAT), 64)

print(f"\n{'='*56}\nPASS: {len(PASS)}, FAIL: {len(FAIL)}")
for f in FAIL: print(f"  ❌ {f}")
print('='*56)
