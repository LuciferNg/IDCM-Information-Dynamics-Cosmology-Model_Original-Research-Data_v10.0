#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""診斷: 24 之 lock 判定 vs 獨立真值（逐形式）"""
import sympy as sp, os, sys
from fractions import Fraction as Fr
BASE=os.path.dirname(os.path.abspath(__file__))
P="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o229_mu2_b4_particle_accounting/scripts/24_r5_discrimination.py"
src=open(P,encoding='utf-8').read()
G={'__file__':P,'__name__':'probe'}
exec(src.split('nz=sum(1 for v in ATOMS')[0],G)
TERMS=G['TERMS']; roots_of=G['roots_of']; vec_of=G['vec_of']; b=G['b']
CVV=[];ISPOW=[]
for (c,k,val,ee) in TERMS:
    pw=any(pp.base==2 and pp.exp.free_symbols for pp in ee.atoms(sp.Pow)); ISPOW.append(pw)
    if pw: CVV.append(None); continue
    dd={}
    for (a,),co in sp.Poly(ee,b).as_dict().items():
        r=sp.Rational(co); dd[int(a)]=Fr(r.p,r.q)
    CVV.append(dd)
COEF=[TERMS[i][0] for i in range(len(TERMS))]
print("TERMS 項數 =",len(TERMS),flush=True)
print("24 自身 lock(137) =",G['lock'][137]," lock(16) =",G['lock'][16],flush=True)
def fast_true(comb,v):
    d={};cp=0
    for i in comb:
        if ISPOW[i]: cp+=COEF[i]
        else:
            for deg,co in CVV[i].items(): d[deg]=d.get(deg,Fr(0))+co
    d[0]=d.get(0,Fr(0))-v
    if not any(x!=0 for x in d.values()): return "ID"
    den=1
    for x in d.values(): den=max(den,x.denominator)
    top=max(d); co=[int(d[i]*den) if i in d else 0 for i in range(top,-1,-1)]
    while len(co)>1 and co[0]==0: co.pop(0)
    if cp==0:
        L=abs(co[0]); mx=max([abs(c) for c in co[1:]] or [0]); bd=min(10**4,1+(mx//max(1,L))+2)
        return [Bv for Bv in range(1,bd+1) if sum(c*(Bv**(len(co)-1-j)) for j,c in enumerate(co))==0]
    return [Bv for Bv in range(1,10001) if sum(c*(Bv**(len(co)-1-j)) for j,c in enumerate(co))+cp*2**Bv==0]
bad=[]
for v in (137,16):
    for comb in G['forms_by_val'].get(v,[]):
        if not any(G['BDEP'][TERMS[i][1]] for i in comb): continue
        r24,_=roots_of(comb,v); rt=fast_true(comb,v)
        if (r24==[4]) != (rt==[4]): bad.append((v,comb,r24,rt))
print("不符形式數:",len(bad),flush=True)
for v,comb,r24,rt in bad[:6]:
    co,_,ok=vec_of(comb,v)
    print(f"\nv={v} comb={comb} 24->{r24} 真值->{rt}")
    print("  項 =",[(TERMS[i][0],TERMS[i][1],TERMS[i][2]) for i in comb])
    print("  24 vec =",co)
    if co:
        L=abs(co[0]); mx=max([abs(c) for c in co[1:]] or [0]); print("  lead=",L,"mx=",mx,"bound=",min(10**4,1+(mx//max(1,L))+2))
PY=1
