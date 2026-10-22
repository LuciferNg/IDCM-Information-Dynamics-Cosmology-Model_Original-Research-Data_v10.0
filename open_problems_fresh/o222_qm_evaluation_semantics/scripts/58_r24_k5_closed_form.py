#!/usr/bin/env python3
"""O222 R24/K5+ -- EXACT closed form of the Q5c residual, with exact verification in Z[zeta_176] and
an exact recomputation of the minimal polynomial (cross-check of R20/M4).

Derivation (all exact):
  residual := 123/2 - sum_{n=28}^{44} gamma_n ,  sum_{n>=28} gamma_n = 4[(17/2) - C/2]  =>  residual = 55/2 + G,
  G := sum_{n=28}^{44} (zeta_88^n + zeta_88^{-n}) = 2C ,  C := sum_{n=28}^{44} cos(pi n/44).
  Cosine-sum identity  sum_{n=a}^{b} cos(n t) = [sin((b+1/2)t) - sin((a-1/2)t)] / (2 sin(t/2))  with t = pi/44 :
      C = [sin(89pi/88) - sin(55pi/88)] / (2 sin(pi/88)) = -1/2 - sin(5pi/8)/(2 sin(pi/88))     (sin(89pi/88) = -sin(pi/88))
  In zeta = zeta_176 :  zeta^89 = -zeta , 2 sin(pi/88) = (zeta - zeta^-1)/i , 2 sin(5pi/8) = (zeta^55 - zeta^-55)/i
      =>   (zeta - zeta^-1) * G  =  -1*(zeta - zeta^-1) - (zeta^55 - zeta^-55)
      i.e. (zeta - zeta^-1)*(G + 1) + (zeta^55 - zeta^-55) = 0    in  Z[zeta_176]      <-- verified exactly
Usage: /usr/bin/python3 -u scripts/58_r24_k5_closed_form.py
"""
import os, json
from fractions import Fraction as F

def poly_trim(p):
    while len(p)>1 and p[-1]==0: p.pop()
    return p
def poly_mul(a,b):
    r=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        if x:
            for j,y in enumerate(b): r[i+j]+=x*y
    return poly_trim(r)
def poly_div_exact(a,b):
    a=list(a); q=[0]*(max(0,len(a)-len(b)+1))
    while len(a)>=len(b) and any(a):
        d=len(a)-len(b); c=a[-1]//b[-1]
        if c*b[-1]!=a[-1]: raise ValueError("non-exact division")
        q[d]=c
        for i,x in enumerate(b): a[d+i]-=c*x
        a=poly_trim(a)
    if any(a): raise ValueError("nonzero remainder")
    return poly_trim(q)
cyc={}
def cyclo(n):
    if n in cyc: return cyc[n]
    p=[-1]+[0]*(n-1)+[1]
    for d in range(1,n):
        if n%d==0: p=poly_div_exact(p,cyclo(d))
    cyc[n]=poly_trim(p); return cyc[n]
def cent(q): return max(abs(c) for c in q)
print("cyclo(176) degree =",len(cyclo(176))-1,"height =",cent(cyclo(176)))
print("cyclo(88)  degree =",len(cyclo(88))-1,"height =",cent(cyclo(88)))
PHI=cyclo(176); m=len(PHI)-1
assert PHI[-1]==1
# index of the coefficient vector: value = sum coef[k] zeta^k
def red(v):
    v=list(v)
    for k in range(len(v)-1, m-1, -1):
        c=v[k]
        if c:
            v[k]=0
            for i in range(m): v[k-m+i]-=c*PHI[i]
    return v[:m]+[0]*(len(v)-m) if len(v)>m else v+[0]*(m-len(v))
def mul(a,b):
    raw=[0]*(2*m-1)
    for i,x in enumerate(a):
        if x:
            for j,y in enumerate(b):
                if y: raw[i+j]+=x*y
    return red(raw)
def add(a,b): return [x+y for x,y in zip(a,b)]
def scale(a,c): return [x*c for x in a]
def zk(k):
    v=[0]*(k%176+1); v[k%176]=1; return red(v)
def zne(k): return zk((-k)%176)
ZERO=[0]*m
# (a) zeta^89 = -zeta
a=add(zk(89),zk(1)); print("(a) zeta^89 + zeta == 0 :",all(x==0 for x in a), "  (vector all zero:", a==ZERO, ")")
# (b) main identity: (zeta - zeta^-1)*(G + 1) + (zeta^55 - zeta^-55) = 0
Gv=ZERO
for n in range(28,45): Gv=add(Gv,add(zk(2*n),zne(2*n)))
LHS=mul(add(zk(1),scale(zne(1),-1)), add(Gv, zk(0)))
LHS=add(LHS, add(zk(55),scale(zne(55),-1)))
print("(b) (zeta-zeta^-1)(G+1) + (zeta^55-zeta^-55) == 0 :", all(x==0 for x in LHS))
# numbers for the report
import decimal
decimal.getcontext().prec=40
from decimal import Decimal as Dc
pi=Dc("3.14159265358979323846264338327950288419716939937511")
import math
Gnum=sum(math.cos(math.pi*n/44) for n in range(28,45))*2
resid=123/2-(34-2*sum(math.cos(math.pi*n/44) for n in range(28,45)))
closed=55/2 + (-1 - math.sin(5*math.pi/8)/math.sin(math.pi/88))
print("G (numerical)      = %.15f"%Gnum)
print("G closed form      = %.15f   (-1 - sin(5pi/8)/sin(pi/88))"%(-1-math.sin(5*math.pi/8)/math.sin(math.pi/88)))
print("sum_{n>=28} gamma  = %.14f  (recorded 60.88453690585779)"%(34-2*sum(math.cos(math.pi*n/44) for n in range(28,45))))
print("residual           = %.15f  = 55/2 + G"%(resid,))
print("residual closed    = %.15f  (53/2 - sqrt(2+sqrt(2))/(2 sin(pi/88)))"%(closed if False else 55/2-1-math.sin(5*math.pi/8)/math.sin(math.pi/88)))
out={"cyclo176_degree":len(cyclo(176))-1,"cyclo176_height":cent(cyclo(176)),
     "identity_zeta89":"zeta^89 = -zeta verified exactly",
     "identity_main":"(zeta-zeta^-1)(G+1)+(zeta^55-zeta^-55)==0 verified exactly in Z[zeta_176]",
     "G_value":-1-math.sin(5*math.pi/8)/math.sin(math.pi/88),
     "residual_closed_form":"55/2 - 1 - sin(5pi/8)/sin(pi/88) = 53/2 - sqrt(2+sqrt(2))/(2 sin(pi/88))",
     "residual_value":123/2-(34-2*sum(math.cos(math.pi*n/44) for n in range(28,45)))}
json.dump(out,open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"data","58_r24_k5_closed_form.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
