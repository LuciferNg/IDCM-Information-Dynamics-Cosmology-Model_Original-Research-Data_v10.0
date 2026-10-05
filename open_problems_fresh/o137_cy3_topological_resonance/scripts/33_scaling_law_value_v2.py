#!/usr/bin/env python3
"""
O137 — 標度律研究價值評估 (修正版)
修正: (a) s2 計算 (b) M4 必須用固定階梯 p 值 (c) 用 F-test 比較階梯
"""
import numpy as np
from math import sin, pi

M0 = 27.900915
def gamma_n(n): return 4*sin(n*pi/88)**2
def omega_n(n): return 2*sin(n*pi/88)
MASS = {'e':0.5110,'u':2.1600,'d':4.6700,'s':93.40,'mu':105.6584,
        'c':1270.0,'tau':1776.86,'b':4180.0,'t':172690.0}
A5 = [1,2,3,4,5,7,9,11,13]
order = ['e','u','d','s','mu','c','tau','b','t']
blocks = {1:[0,1,2], 2:[3,4,5], 3:[6,7,8]}
def xy(g):
    idx = blocks[g]
    return (np.log([gamma_n(A5[i]) for i in idx]),
            np.log([MASS[order[i]] for i in idx]))

print("="*78); print("(1) p_g 標準誤"); print("="*78)
pg, seg = {}, {}
print(f"{'世代':>4} {'模式':>12} {'p':>8} {'SE(p)':>8} {'rel':>7} {'RMS':>7} {'p=1 RMS':>9}")
for g in [1,2,3]:
    x,y = xy(g); xb=x.mean(); Sxx=float(np.sum((x-xb)**2))
    A=np.vstack([x,np.ones_like(x)]).T
    coef,*_=np.linalg.lstsq(A,y,rcond=None)
    res=y-A@coef; SSE=float(np.sum(res**2)); dof=len(x)-2
    SE=float(np.sqrt((SSE/dof)/Sxx))
    rms=float(np.sqrt(SSE/len(x)))
    c1=float(np.mean(y-x)); rms1=float(np.sqrt(np.mean((y-x-c1)**2)))
    pg[g],seg[g]=coef[0],SE
    print(f"{g:>4} {str([A5[i] for i in blocks[g]]):>12} {coef[0]:>8.4f} {SE:>8.4f} "
          f"{SE/abs(coef[0])*100:>6.1f}% {rms:>7.4f} {rms1:>9.4f}")

print("\n"+"="*78); print("(2) 階梯步顯著性"); print("="*78)
for a,b in [(1,2),(2,3),(1,3)]:
    d=pg[b]-pg[a]; S=float(np.sqrt(seg[a]**2+seg[b]**2))
    print(f"p{b}−p{a} = {d:+.4f} ± {S:.4f} ⟹ z = {d/S:+.2f}σ "
          f"{'🟢' if abs(d/S)>2 else '🔴 唔顯著'}")
print(f"\n各世代 vs (F₅/2)^(g−1):")
for g in [1,2,3]:
    pr=(5/2)**(g-1); print(f"  g={g}: {pg[g]:.4f}±{seg[g]:.4f} vs {pr:.2f} ⟹ z={(pg[g]-pr)/seg[g]:+.2f}σ")

print("\n"+"="*78); print("(3) ★ 階梯可辨識性 — F-test vs 自由 p_g"); print("="*78)
def sse_fixed(g, p):
    x,y=xy(g); r=y-p*x; r=r-r.mean(); return float(np.sum(r**2))
SSE_free = sum(sse_fixed(g,pg[g]) for g in [1,2,3])
print(f"自由 p_g (M3) SSE = {SSE_free:.4f}  (k=6, dof=3)")
ladders = {'(5/2)^(g-1)':[1,2.5,6.25], 'F_{2g+1}/2':[1,2.5,6.5], 'g²':[1,4,9],
           '(2g-1)':[1,3,5], '2^(g-1)':[1,2,4], 'g!':[1,2,6],
           '3^(g-1)':[1,3,9], '(g²+g)/2':[1,3,6]}
print(f"\n{'階梯':>14} {'SSE':>9} {'F':>8} {'p-value':>9} 判定")
from math import exp
res={}
for name,ps in ladders.items():
    S=sum(sse_fixed(g,ps[g-1]) for g in [1,2,3])
    F=((S-SSE_free)/2)/(SSE_free/3)
    # F(2,3) 上尾 p-value (closed form)
    import math
    x_ = 2*F/(2*F+3) if F>0 else 0
    # P(F_{2,3} > f) = 1 - I_{2f/(2f+3)}(1, 1.5)
    try:
        from scipy.stats import f as fdist
        pv = float(fdist.sf(F,2,3))
    except Exception:
        pv = float('nan')
    res[name]=(S,F,pv)
    print(f"{name:>14} {S:>9.4f} {F:>8.3f} {pv:>9.4f} "
          f"{'🟢 相容' if (pv!=pv or pv>0.05) else '🔴 排除'}")
ok=[k for k,(S,F,pv) in res.items() if (pv!=pv or pv>0.05)]
print(f"\n★ 相容階梯: {len(ok)}/{len(ladders)} → {ok}")
print(f"★ 最佳 SSE: {min(res.items(), key=lambda kv: kv[1][0])[0]} (SSE={min(v[0] for v in res.values()):.4f})")

print("\n"+"="*78); print("(4) 模型比較 (修正 M4)"); print("="*78)
yall=np.log([MASS[p] for p in order]); xall=np.log([gamma_n(n) for n in A5])
def sse(pfun, pergen):
    tot=0.0
    for g in [1,2,3]:
        x,y=xy(g)
        if pergen: pred = pfun(g)*x + (y-pfun(g)*x).mean()
        else:
            pred = pfun(g)*x + float(np.mean(yall-xall))
        tot+=float(np.sum((y-pred)**2))
    return tot
rows=[('M1: γ_n·C  (k=1)', 1, sse(lambda g:1.0, False)),
      ('M2: γ_n·C_g (k=3)', 3, sse(lambda g:1.0, True)),
      ('M3: γ_n^{p_g}·C_g free (k=6)', 6, sse(lambda g:pg[g], True)),
      ('M4: γ_n^{(5/2)^{g-1}}·C_g (k=4)', 4, sse(lambda g:(5/2)**(g-1), True))]
n=9
print(f"{'模型':>32} {'k':>3} {'SSE':>9} {'AIC':>8} {'BIC':>8} {'RMS':>7}")
for nm,k,S in rows:
    print(f"{nm:>32} {k:>3} {S:>9.4f} {2*k+n*np.log(S/n):>8.2f} "
          f"{k*np.log(n)+n*np.log(S/n):>8.2f} {np.sqrt(S/n):>7.4f}")
print(f"\n★ AIC 最佳 = {min(rows, key=lambda r: 2*r[1]+n*np.log(r[2]/n))[0]}")
print(f"★ M3 vs M4: SSE {rows[2][2]:.4f} vs {rows[3][2]:.4f} → "
      f"階梯 {'冇損失' if abs(rows[2][2]-rows[3][2])/rows[2][2]<0.05 else '有損失'}")

print("\n"+"="*78); print("(5) 約定依賴"); print("="*78)
for g in [1,2,3]:
    xg,y=xy(g); xw=np.log([omega_n(A5[i]) for i in blocks[g]])
    print(f"Gen{g}: p_γ = {np.polyfit(xg,y,1)[0]:.4f}   p_ω = {np.polyfit(xw,y,1)[0]:.4f}")
print("★ O136 docs/02 用 m_n = M₀√γ_n = M₀ω_n (p_ω=1); O54/O137 用 m = M₀γ_n·C_f (p_γ=1)")
print("⟹ 同一譜, 兩約定差 2 次冪 ⟹ 階梯絕對值依約定而定")

print("\n"+"="*78); print("(6) ★★ 真結構分歧: A₅ 升序 vs O54 Φ 幾何"); print("="*78)
PHI={(i,j):1+a*b for i,a in enumerate([1,5,9]) for j,b in enumerate([0,1,3,4,6,7])}
print(f"{'粒子':>5} {'A₅ 反解 C_f':>13} {'Φ 最近值':>10} {'偏差':>8}   {'O54 模式':>9} {'Φ 幾何 C_f':>11} {'偏差':>8}")
for p,nA,nO,kO in [('mu',5,7,(1,4)),('tau',9,20,(2,3))]:
    CfA=MASS[p]/(M0*gamma_n(nA))
    cat=sorted(set(v/d for v in PHI.values() for d in [1,2,4]))
    nb=min(cat,key=lambda c:abs(c-CfA)); dA=abs(nb-CfA)/CfA*100
    CfO=PHI[kO]/2 if kO==(1,4) else PHI[kO]
    mO=M0*gamma_n(nO)*CfO; dO=abs(mO-MASS[p])/MASS[p]*100
    print(f"{p:>5} {CfA:>13.4f} {nb:>10.4f} {dA:>7.2f}%   n={nO:<2} Φ[{kO[0]+1}][{kO[1]+1}]={CfO:<5} {dO:>7.2f}%")
print(f"\n★ τ 需要 C_f = {MASS['tau']/(M0*gamma_n(9)):.1f} — Φ 目錄最大值 {max(PHI.values())} ⟹ 無對應")
print(f"★ 但 n=20 ∉ A₅ ⟹ A₅ 與 O54 輕子模式分配不可共存")
