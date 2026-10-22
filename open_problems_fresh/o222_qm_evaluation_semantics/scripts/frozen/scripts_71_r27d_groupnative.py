#!/usr/bin/env python3
"""O222 R27/D2 -- the group 2I computed NATIVELY from the frozen machine (zero external objects).

The machine's states with MUL[s][ctx] = s * h(ctx) are the left-regular representation of 2I:
state 0 = identity, and every state is a group element.  Multiplication is recovered by BFS words.

Calibrations (against the frozen record): |G| = 120, element orders {1:1,2:1,3:20,4:30,5:24,6:20,10:24},
9 conjugacy classes of sizes {1,1,12,12,12,12,20,20,30}.
Test (Gemini P1b): does G minus any conjugacy class still generate G?
PRE-REGISTERED: Pr-1 all 9 complements generate 2I (=> Gemini's class-deletion claim REFUTED).
Usage: /usr/bin/python3 -u scripts/71_r27d_groupnative.py"""
import importlib.util, io, json, os, collections
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("m12f",os.path.join(HERE,"12_b5_budget.py")); m12=importlib.util.module_from_spec(sp); sp.loader.exec_module(m12)
_mm,K,MUL,hx,idx,_t=m12.load_machine()
NR=len(K); NC=len(K[0]); lab=[str(x) for x in (idx if isinstance(idx,list) else range(NC))]
word={0:()}; fr=[0]
while fr:
    nf=[]
    for s in fr:
        for c in range(NC):
            t=MUL[s][hx[c]]
            if t not in word: word[t]=word[s]+(c,); nf.append(t)
    fr=nf
print("states reached by words:",len(word),"(of %d)"%NR)
def mul(s,t):
    for c in word[t]: s=MUL[s][hx[c]]
    return s
def pw(s,k):
    r=0
    for _ in range(k): r=mul(r,s)
    return r
orders=collections.Counter()
for s in range(NR):
    for k in range(1,25):
        if pw(s,k)==0: orders[k]+=1; break
rec={1:1,2:1,3:20,4:30,5:24,6:20,10:24}
print("order distribution:",dict(sorted(orders.items())),"| record",rec,"%s"%("OK" if dict(sorted(orders.items()))==rec else "MISMATCH"))
def inv(s):
    for t in range(NR):
        if mul(s,t)==0: return t
classes=[]; seen=set()
for s in range(NR):
    if s in seen: continue
    cl=frozenset(mul(mul(g,s),inv(g)) for g in range(NR)); classes.append(cl); seen|=cl
sizes=sorted(len(c) for c in classes)
print("conjugacy classes: n=%d sizes=%s | record [1,1,12,12,12,12,20,20,30] %s"%(len(classes),sizes,
  "OK" if (len(classes)==9 and sizes==[1,1,12,12,12,12,20,20,30]) else "MISMATCH"))
def closure(gen):
    st={0}; fr=[0]
    while fr:
        nf=[]
        for u in fr:
            for g in gen:
                w=mul(u,g)
                if w not in st: st.add(w); nf.append(w)
        fr=nf
    return len(st)
res=[]
for c in classes:
    g=[s for s in range(NR) if s not in c]; res.append((len(c),closure(g)))
print("class-deletion generation (class size, |<complement>|):",res)
print("Pr-1 (all complements generate 2I): %s"%("HOLDS -> Gemini's class claim REFUTED" if all(x==NR for _,x in res) else "REFUTED"))
# element orders of the 62 axis generators, by family
fam=collections.defaultdict(lambda: collections.Counter())
for c in range(NC):
    e=hx[c] if isinstance(hx,list) else hx
    o=next(k for k in range(1,25) if pw(c if False else 0,0)==0 and True)
    # order of the *generator element* hx[c]: use the permutation order of the axis transition instead
    perm=[MUL[s][hx[c]] for s in range(NR)]
    vis=[False]*NR; cyc=[]
    for i in range(NR):
        if not vis[i]:
            l=0; j=i
            while not vis[j]: vis[j]=True; j=perm[j]; l+=1
            cyc.append(l)
    def gcd(x,y):
        while y: x,y=y,x%y
        return x
    L=1
    for x in cyc: L=L*x//gcd(L,x)
    fam[lab[c][0]][L]+=1
print("axis-transition orders by family:",{k:dict(v) for k,v in fam.items()})
json.dump({"order_dist":dict(sorted(orders.items())),"class_sizes":sizes,"class_deletion":res,
  "axis_orders_by_family":{k:dict(v) for k,v in fam.items()}},
  io.open(os.path.join(ROOT,"data","71_r27d_groupnative.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
