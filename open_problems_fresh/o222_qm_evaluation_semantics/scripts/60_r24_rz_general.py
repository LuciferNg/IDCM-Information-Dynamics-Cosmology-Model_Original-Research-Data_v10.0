#!/usr/bin/env python3
"""O222 R24/rz -- rz(n) = max #1s in an n x n 0-1 matrix with no all-1 2x2  (= Zarankiewicz z(n,n;2,2), C4-free bipartite).
 (A) DERIVED bound: row pairs share <=1 column => sum_i C(r_i,2) <= C(n,2); convexity => m(m-n) <= n^2(n-1)
     => m <= n/2 (1+sqrt(4n-3))   (Kotvari-Sos-Turan, re-derived here)
 (B) exact rz(n) for n <= 7 by attaining the bound with explicit constructions (LCG local search; Fano plane for 7)
 (C) infinite family: PG(2,q) attains the bound  =>  rz(q^2+q+1) = (q+1)(q^2+q+1)  [verified q = 2,3,4]
 (D) declaration: general n = open Zarankiewicz problem; no closed form known.
Usage: /usr/bin/python3 -u scripts/60_r24_rz_general.py"""
import os, json, itertools
from math import isqrt
def upper(n):
    m=0
    while (m+1)*((m+1)-n) <= n*n*(n-1): m+=1
    return m
class LCG:
    def __init__(s,seed): s.x=seed & 0xFFFFFFFF
    def nxt(s):
        s.x=(1103515245*s.x+12345)&0x7FFFFFFF
        return s.x
    def below(s,k): return s.nxt()%k
def violates(M,n):
    for i in range(n):
        for i2 in range(i+1,n):
            c=[j for j in range(n) if M[i][j] and M[i2][j]]
            if len(c)>1: return (i,i2,c[0],c[1])
    return None
def local_search(n, target, seed, restarts=4000):
    rng=LCG(seed); best=(0,None)
    for t in range(restarts):
        d=target
        M=[[0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if rng.below(n*n) < d: M[i][j]=1
        for _ in range(4000):
            v=violates(M,n)
            if v is None: break
            i,i2,j,j2=v
            pick=rng.below(4)
            if pick==0: M[i][j]=0
            elif pick==1: M[i2][j]=0
            elif pick==2: M[i][j2]=0
            else: M[i2][j2]=0
        if violates(M,n) is not None: continue
        improved=True
        while improved:
            improved=False
            order=list(range(n*n)); rng.shuffle(order) if hasattr(rng,"shuffle") else None
            for cell in range(n*n):
                i,j=divmod(cell,n)
                if M[i][j]: continue
                M[i][j]=1
                if violates(M,n) is None:
                    improved=True
                else:
                    M[i][j]=0
        tot=sum(sum(r) for r in M)
        if tot>best[0] and violates(M,n) is None: best=(tot,[r[:] for r in M])
        if best[0]>=target: break
    return best
res={"upper":{},"found":{},"exact":{}}
for n in range(2,8):
    up=upper(n)
    val,M=local_search(n,up,20260930+n*7)
    res["upper"][n]=up; res["found"][n]=val; res["exact"][n]=(val==up)
    print("n=%d  upper=%d  found=%d  %s"%(n,up,val,"EXACT (bound attained)" if val==up else "gap -> only bounded"))
# (C) PG(2,q)
def gf(q):
    if q==4:
        def mul(a,b):
            r=0
            for i in range(2):
                if (b>>i)&1:
                    sh=a<<i
                    if sh&4: sh^=0b111
                    r^=sh
            return r
        return (lambda a,b:(a^b), mul)
    return (lambda a,b:(a+b)%q, lambda a,b:(a*b)%q)
def PG2(q):
    add,mul=gf(q); pts=[]; seen=set()
    for v in itertools.product(range(q),repeat=3):
        if v==(0,0,0): continue
        idx=next(i for i in range(3) if v[i]!=0)
        e=v[idx]
        inv=next(c for c in range(1,q) if mul(e,c)==1)
        w=tuple(mul(x,inv) for x in v)
        if w not in seen: seen.add(w); pts.append(w)
    lines=[]
    for p in pts:
        lines.append([j for j,r in enumerate(pts) if add(add(mul(p[0],r[0]),mul(p[1],r[1])),mul(p[2],r[2]))==0])
    M=[[0]*len(pts) for _ in pts]
    for i,L in enumerate(lines):
        for j in L: M[i][j]=1
    return M,len(pts)
for q in (2,3,4):
    M,n=PG2(q); o=sum(sum(r) for r in M); up=upper(n)
    res["PG2_%d"%q]={"n":n,"is_q2q1":n==q*q+q+1,"ones":o,"formula":(q+1)*(q*q+q+1),"upper":up,"no_rect":violates(M,n) is None,"attains":o==up}
    print("PG(2,%d): n=%d (q^2+q+1=%s)  ones=%d  (q+1)n=%d  upper=%d  no-2x2=%s  attains=%s"%(q,n,n==q*q+q+1,o,(q+1)*n,up,violates(M,n) is None,o==up))
print("\nrz(3)=6 rz(4)=9 rz(5)=12 rz(6)=16 rz(7)=21 (bound attained). rz(q^2+q+1)=(q+1)(q^2+q+1) for q=2,3,4.")
json.dump(res,open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"data","60_r24_rz_general.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
