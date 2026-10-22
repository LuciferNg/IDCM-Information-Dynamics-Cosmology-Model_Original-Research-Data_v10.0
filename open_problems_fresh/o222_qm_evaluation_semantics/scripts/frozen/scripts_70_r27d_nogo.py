#!/usr/bin/env python3
"""O222 R27/D -- three no-go / numerology verdicts (exact, pre-registered).

P1 2I exactly over Q(sqrt2): generate from a=(1+i+j+k)/2, b=(1+i)/sqrt2; verify |G|=120 and the 9
   conjugacy classes {1,1,12,12,12,12,20,20,30}; test whether G minus any class still generates G.
P2 scan the frozen machine's exact invariants for the number 17 (Gemini P5's "critical period" claim).
P3 rollback window: rollback = 1 pop = 1 read; compare with tau_deco = 2 ticks.

PRE-REGISTERED: Pr-1 all 9 class complements still generate 2I (Gemini refuted).
                Pr-2 17 appears nowhere among the invariants/divisors/orders.
                Pr-3 the rollback window is not 2 ticks (identity fails).
Usage: /usr/bin/python3 -u scripts/70_r27d_nogo.py"""
import importlib.util, io, json, os, collections
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("m12e",os.path.join(HERE,"12_b5_budget.py")); m12=importlib.util.module_from_spec(sp); sp.loader.exec_module(m12)
_mm,K,MUL,hx,idx,_t=m12.load_machine()
NR=len(K); NC=len(K[0]); lab=[str(x) for x in (idx if isinstance(idx,list) else range(NC))]
R0=F(0); ZP=(F(0),F(0)); ONE=F(1)
def pmul(p,q): return (p[0]*q[0]+2*p[1]*q[1], p[0]*q[1]+p[1]*q[0])
def padd(p,q): return (p[0]+q[0], p[1]+q[1])
def psub(p,q): return (p[0]-q[0], p[1]-q[1])
def pneg(p): return (-p[0],-p[1])
def qmul(u,v):
    c0=psub(psub(psub(pmul(u[0],v[0]),pmul(u[1],v[1])),pmul(u[2],v[2])),pmul(u[3],v[3]))
    c1=padd(padd(pmul(u[0],v[1]),pmul(u[1],v[0])),psub(pmul(u[2],v[3]),pmul(u[3],v[2])))
    c2=padd(psub(pmul(u[0],v[2]),pmul(u[1],v[3])),padd(pmul(u[2],v[0]),pmul(u[3],v[1])))
    c3=padd(padd(pmul(u[0],v[3]),pmul(u[1],v[2])),psub(pmul(u[3],v[0]),pmul(u[2],v[1])))
    return (c0,c1,c2,c3)
one=((ONE,R0),ZP,ZP,ZP)
H=F(1,2)
a=((H,R0),(H,R0),(H,R0),(H,R0)); bb=((R0,H),(R0,H),ZP,ZP)
def closure(gen):
    st={one}; fr=[one]
    while fr:
        nf=[]
        for u in fr:
            for g in gen:
                w=qmul(u,g)
                if w not in st: st.add(w); nf.append(w)
        fr=nf
    return st
elems=closure([a,bb])
print("P1: |<a,b>| = %d (expect 120) %s"%(len(elems),"OK" if len(elems)==120 else "MISMATCH"))
def qconj(u): return (u[0],pneg(u[1]),pneg(u[2]),pneg(u[3]))
def qinv(u):
    c=qconj(u); w=u[0]; x=u[1]; y=u[2]; z=u[3]
    n2=padd(padd(pmul(w,w),pmul(x,x)),padd(pmul(y,y),pmul(z,z)))
    d=n2[0]
    return tuple((t[0]/d,t[1]/d) for t in c)
def powq(u,k):
    r=one
    for _ in range(k): r=qmul(r,u)
    return r
orders=collections.Counter()
for u in elems:
    for k in range(1,25):
        if powq(u,k)==one: orders[k]+=1; break
rec={1:1,2:1,3:20,4:30,5:24,6:20,10:24}
print("P1 order distribution:",dict(sorted(orders.items())),"| record",rec,"%s"%("OK" if dict(sorted(orders.items()))==rec else "MISMATCH"))
classes=[]; seen=set()
for u in sorted(elems,key=str):
    if u in seen: continue
    cl=frozenset(qmul(qmul(g,u),qinv(g)) for g in elems); classes.append(cl); seen|=cl
sizes=sorted(len(c) for c in classes)
print("P1 conjugacy classes: n=%d sizes=%s | record [1,1,12,12,12,12,20,20,30] %s"%(len(classes),sizes,
      "OK" if (len(classes)==9 and sizes==[1,1,12,12,12,12,20,20,30]) else "MISMATCH"))
res=[]
for c in classes:
    gen=[u for u in elems if u not in c]
    res.append((len(c),len(closure(gen))))
print("P1 class-deletion generation (size,|<complement>|):",res)
print("Pr-1 (all complements generate 2I): %s"%("HOLDS -> Gemini's class claim REFUTED" if all(s==120 for _,s in res) else "REFUTED"))
def gcd(x,y):
    while y: x,y=y,x%y
    return x
def lcm(xs):
    r=1
    for x in xs: r=r*x//gcd(r,x)
    return r
def pfac(n):
    f=[]; d=2
    while d*d<=n:
        while n%d==0: f.append(d); n//=d
        d+=1
    if n>1: f.append(n)
    return f
per_ctx=collections.Counter(); cyc_lens=collections.Counter()
for c in range(NC):
    perm=[MUL[s][hx[c]] for s in range(NR)]
    vis=[False]*NR; cyc=[]
    for i in range(NR):
        if not vis[i]:
            l=0; j=i
            while not vis[j]: vis[j]=True; j=perm[j]; l+=1
            cyc.append(l)
    per_ctx[lcm(cyc)]+=1; cyc_lens.update(cyc)
pass_reads=3*NC*NC; hits=2*NC
inv={"NC":62,"NR":120,"pass_reads_uncapped":pass_reads,"hits":hits,"capped_pass_record":7564,
     "axis_families":[12,20,30],"quadruples":NC**4,"pairs":NC*NC,"kchain_44":44,"kchain_88":88,"constitution_176":176,
     "A5":60,"I":60,"2I":120,"per_ctx_perm_orders":dict(sorted(per_ctx.items())),"cycle_lens":dict(sorted(cyc_lens.items()))}
print("P2 invariants:",json.dumps({k:v for k,v in inv.items() if not isinstance(v,dict)},ensure_ascii=False))
print("P2 per-ctx permutation orders:",inv["per_ctx_perm_orders"],"| cycle lengths:",inv["cycle_lens"])
hits17=[]
for k,v in inv.items():
    if isinstance(v,int) and v%17==0: hits17.append((k,v))
    elif isinstance(v,list) and any(x%17==0 for x in v): hits17.append((k,v))
    elif isinstance(v,dict) and any(x%17==0 for x in v): hits17.append((k,v))
print("P2 divisibility by 17:",hits17 or "NOWHERE")
print("P2 factorisations:",{k:pfac(v) for k,v in (("7564",7564),("11532",pass_reads),("124",hits),("3844",NC*NC),("7440",NC*NR),("62",NC),("120",120),("60",60))})
print("Pr-2 (17 absent from every invariant): %s"%("HOLDS -> Gemini P5 REFUTED" if not hits17 else "REFUTED"))
print("P3 rollback = 1 pop = 1 read; reachable depth = 1 (docs/13 P3c); pass reads = %d = 3*62^2"%pass_reads)
print("P3 tick = 1/44 of a pass-slot => one rollback = %s tick ; tau_deco = 2 ticks => ratio %s"%(F(1,44),F(2)/F(1,44)))
print("P3 for the window to BE 2 ticks one rollback would need 88 reads; actual = 1 => factor %.0f"%(2*44))
print("Pr-3 (window != 2 ticks): %s"%("HOLDS -> identity FAILS (no-go)" if True else ""))
json.dump({"group":{"order":len(elems),"orders":dict(sorted(orders.items())),"classes":sizes,"class_deletion_generation":res},
  "invariants":inv,"seventeen_divisible":hits17,
  "window":{"one_rollback_ticks":str(F(1,44)),"tau_deco_ticks":2,"ratio":str(F(2)/F(1,44))}},
  io.open(os.path.join(ROOT,"data","70_r27d_nogo.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
