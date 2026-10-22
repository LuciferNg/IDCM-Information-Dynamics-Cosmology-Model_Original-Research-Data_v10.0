#!/usr/bin/env python3
"""O222 R24/K5++ -- exact minimal polynomial of G = sum_{n=28}^{44}(z88^n + z88^-n) over Q (cross-check of R20/M4:
degree 20, monic in Z[X], coefficient of X^19 = +40 i.e. Tr_K(G) = -40, 20 distinct conjugates).
Exact arithmetic in Z[z88] (deg-40) with the K = Q(z88)^+ (deg-20) basis {z^k+z^-k : k=1..43 odd, gcd(k,88)=1}.
Usage: /usr/bin/python3 -u scripts/59_r24_k5_minpoly.py"""
import os, json
from fractions import Fraction as F
from math import gcd
def ptrim(p):
    while len(p)>1 and p[-1]==0: p.pop()
    return p
def pmul(a,b):
    r=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        if x:
            for j,y in enumerate(b): r[i+j]+=x*y
    return ptrim(r)
def pdiv(a,b):
    a=list(a); q=[0]*(max(0,len(a)-len(b)+1))
    while len(a)>=len(b) and any(a):
        d=len(a)-len(b); c=a[-1]//b[-1]
        assert c*b[-1]==a[-1]
        q[d]=c
        for i,x in enumerate(b): a[d+i]-=c*x
        a=ptrim(a)
    assert not any(a)
    return ptrim(q)
cyc={}
def cyclo(n):
    if n in cyc: return cyc[n]
    p=[-1]+[0]*(n-1)+[1]
    for d in range(1,n):
        if n%d==0: p=pdiv(p,cyclo(d))
    cyc[n]=ptrim(p); return cyc[n]
PHI=cyclo(88); m=len(PHI)-1
def red(v):
    v=list(v)
    while len(v)>m:
        c=v[-1]
        if c:
            base=len(v)-1-m
            for i in range(m): v[base+i]-=c*PHI[i]
        v.pop()
    v=v[:m]
    return v+[0]*(m-len(v))
def zp(k):
    v=[0]*(k%88+1); v[k%88]=1; return red(v)
def add(a,b): return [x+y for x,y in zip(a,b)]
def neg(a): return [-x for x in a]
def mul(a,b):
    raw=[0]*(2*m-1)
    for i,x in enumerate(a):
        if x:
            for j,y in enumerate(b):
                if y: raw[i+j]+=x*y
    return red(raw)
B20=[add(zp(k),zp((-k)%88)) for k in range(1,21)]
print("K-basis size =",len(B20))
def _rank(vs):
    A=[[F(x) for x in v] for v in vs]; r=0
    for c in range(len(vs[0])):
        pr=None
        for i in range(r,len(vs)):
            if A[i][c]!=0: pr=i; break
        if pr is None: continue
        A[r],A[pr]=A[pr],A[r]; pv=A[r][c]; A[r]=[x/pv for x in A[r]]
        for i in range(len(vs)):
            if i!=r and A[i][c]!=0:
                f=A[i][c]; A[i]=[A[i][k]-f*A[r][k] for k in range(len(vs[0]))]
        r+=1
    return r
print("rank(K-basis) =",_rank(B20),"  (must be 20)")
# solve an element (vector in Z[z88]) as coordinates on B20 : 40 x 20 system, exact Gaussian elimination
def coords(v):
    A=[[F(B20[j][i]) for j in range(20)]+[F(v[i])] for i in range(m)]
    rows=len(A); cols=20; r=0; piv=[]
    for c in range(cols):
        pr=None
        for i in range(r,rows):
            if A[i][c]!=0: pr=i; break
        if pr is None: continue
        A[r],A[pr]=A[pr],A[r]; pv=A[r][c]; A[r]=[x/pv for x in A[r]]
        for i in range(rows):
            if i!=r and A[i][c]!=0:
                f=A[i][c]; A[i]=[A[i][k]-f*A[r][k] for k in range(cols+1)]
        piv.append(c); r+=1
        if r==cols: break
    for i in range(r,rows):
        assert A[i][cols]==0, "element not in K"
    x=[F(0)]*cols
    for i,c in enumerate(piv): x[c]=A[i][cols]
    return x
def coordvec2vec(x):
    v=[0]*m
    for j,c in enumerate(x):
        if c:
            v=add(v,[int(c)*B20[j][i] if c.denominator==1 else None for i in range(m)])
    return v
G=[0]*m
for n in range(28,45): G=add(G, add(zp(n), zp((-n)%88)))
units=[a for a in range(1,88) if gcd(a,88)==1]
seen=set(); conj=[]
for a in units:
    key=min(a,88-a)
    if key in seen: continue
    seen.add(key)
    v=[0]*m
    for n in range(28,45): v=add(v, add(zp((a*n)%88), zp((-a*n)%88)))
    conj.append(v)
print("distinct conjugates =",len(conj))
Xs=[coords(v) for v in conj]
def cmul(x,y):
    v=[F(0)]*m
    for j,c in enumerate(x):
        if c: v=add(v,[c*B20[j][i] for i in range(m)])
    w=[F(0)]*m
    for j,c in enumerate(y):
        if c: w=add(w,[c*B20[j][i] for i in range(m)])
    z=mul([int(t) if t.denominator==1 else None for t in v] if all(t.denominator==1 for t in v) else None,None) if False else None
    # exact field product via integer vectors scaled by common denominators
    from math import lcm
    L=1
    for t in list(v)+list(w): L=lcm(L,t.denominator)
    vi=[int(t*L) for t in v]; wi=[int(t*L) for t in w]
    prod=mul(vi,wi)
    return coords([F(t, L*L) for t in prod])
# powers
P=[]
for x in Xs:
    pw=[None]*21; pw[0]=coords(zp(0))
    for k in range(1,21): pw[k]=cmul(pw[k-1],x)
    P.append(pw)
# solve sum_{k<20} c_k x_a^k = -x_a^20
import itertools
A=[[P[a][k][i] for k in range(20)]+[-P[a][20][i]] for a in range(20) for i in range(20)]
rows=[r for r in A if any(x!=0 for x in r[:20]) or r[20]!=0]
M=[[F(x) for x in r] for r in rows]
nr=len(M); r=0; piv=[]
for c in range(20):
    pr=None
    for i in range(r,nr):
        if M[i][c]!=0: pr=i; break
    if pr is None: continue
    M[r],M[pr]=M[pr],M[r]; pv=M[r][c]; M[r]=[x/pv for x in M[r]]
    for i in range(nr):
        if i!=r and M[i][c]!=0:
            f=M[i][c]; M[i]=[M[i][k]-f*M[r][k] for k in range(21)]
    piv.append(c); r+=1
    if r==20: break
for i in range(r,nr):
    if all(M[i][k]==0 for k in range(20)) and M[i][20]!=0: print("INCONSISTENT"); break
sol=[F(0)]*20
for i,c in enumerate(piv): sol[c]=M[i][20]
monic = all(s.denominator==1 for s in sol)
print("minimal polynomial coefficients (ascending) integral?",monic)
if monic:
    cf=[int(s) for s in sol]+[1]
    print("P(X) = X^20 + %d X^19 + ... "%cf[19], "| [X^19] =",cf[19],"| Tr = -[X^19] =",-cf[19])
    print("all coefficients:",cf)
    print("nonzero count =",sum(1 for c in cf if c!=0))
out={"distinct_conjugates":len(conj),"integral":monic,
     "coeffs_ascending":([int(s) for s in sol]+[1]) if monic else None,
     "trace": (-int(sol[19])) if monic else None}
json.dump(out,open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"data","59_r24_k5_minpoly.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
