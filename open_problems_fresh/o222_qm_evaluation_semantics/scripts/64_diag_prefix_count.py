#!/usr/bin/env python3
"""O222 scripts/64 (diagnostic) -- why does the prefix-decomposition total fall short of EC(5) = 972000?
Compare per-prefix constructible counts from brute force against the BEST completion counts with both root choices.
Usage: /usr/bin/python3 -u scripts/64_diag_prefix_count.py"""
import io, json, os
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
def det_int(M):
    n=len(M); A=[[F(x) for x in r] for r in M]; det=F(1)
    for c in range(n):
        p=None
        for i in range(c,n):
            if A[i][c]!=0: p=i; break
        if p is None: return 0
        if p!=c: A[c],A[p]=A[p],A[c]; det=-det
        det*=A[c][c]
        for i in range(c+1,n):
            f=A[i][c]/A[c][c]
            if f: A[i]=[A[i][k]-f*A[c][k] for k in range(n)]
    return det
def tau(edges_out,n,root):
    L=[[0]*n for _ in range(n)]
    for u in range(n):
        for v in edges_out[u]:
            if u!=v: L[u][u]+=1; L[u][v]-=1
    idx=[i for i in range(n) if i!=root]
    return det_int([[L[i][j] for j in idx] for i in idx])
def fact(x):
    r=1
    for i in range(2,x+1): r*=i
    return r
def crit(P,n):
    A=set(a for a,b in P); B=set(b for a,b in P)
    for a in sorted(A):
        for a2 in sorted(A):
            if a==a2: continue
            c=sum(1 for q in B if q not in (a,a2) and (a,q) in P and (a2,q) in P)
            if c>=2: return True
    return False
def completions(n,P,root_mode):
    used=set(P); u=P[-1][1]
    res=[[] for _ in range(n)]
    for v in range(n):
        for w in range(n):
            if v!=w and (v,w) not in used: res[v].append(w)
    G2=[list(r) for r in res]; G2[0].append(u)
    deg=[len(G2[v]) for v in range(n)]
    if any(d==0 for d in deg): return 0, False
    outdeg=[sum(1 for x in G2[v]) for v in range(n)]
    indeg=[0]*n
    for v in range(n):
        for w in G2[v]: indeg[w]+=1
    balanced=all(outdeg[v]==indeg[v] for v in range(n))
    r = u if root_mode=="head" else 0
    t=tau(G2,n,r)
    if t==0: return 0,balanced
    p=1
    for v in range(n): p*=fact(outdeg[v]-1)
    return t*p, balanced
def trails(n,L,first=(0,1)):
    out=[]; used={first}
    def rec(v,path):
        if len(path)==L: out.append(list(path)); return
        for w in range(n):
            if w==v or (v,w) in used: continue
            used.add((v,w)); path.append((v,w)); rec(w,path); path.pop(); used.remove((v,w))
    rec(first[1],[first]); return out
n,L=5,9
# brute force: bucket circuits by their canonical prefix
out_adj=[sorted(j for j in range(n) if j!=v) for v in range(n)]
buck={}
def dfs(v,d,used,seq):
    if d==n*(n-1):
        if v==0:
            pre=tuple(seq[:L]); buck[pre]=buck.get(pre,0)+1
        return
    for w in out_adj[v]:
        e=(v,w)
        if e in used: continue
        if d==0 and e!=(0,1): continue
        if d==n*(n-1)-1 and w!=0: continue
        used.add(e); seq.append(e); dfs(w,d+1,used,seq); seq.pop(); used.remove(e)
dfs(0,0,set(),[])
tot_b=sum(buck.values())
print("brute circuits =",tot_b,"distinct prefixes =",len(buck))
P=trails(n,L); print("trail prefixes enumerated =",len(P))
badH=bad0=unbal=0; sumH=sum0=0
mism=0
for pp in P:
    key=tuple(pp); b=buck.get(key,0)
    cH,balH=completions(n,pp,"head"); c0,_=completions(n,pp,"tail")
    sumH+=cH; sum0+=c0
    if not balH: unbal+=1
    if cH!=b: badH+=1
    if c0!=b: bad0+=1
    if badH and mism<5: print("  mismatch(prefix len %d end %d): brute %d head %d tail %d"% (len(pp),pp[-1][1],b,cH,c0)); mism+=1
print("sum(head-root)=",sumH," sum(tail-root)=",sum0," | brute total",tot_b, "EC(5)=",n**(n-2)*fact(n-2)**n)
print("prefixes with head-root mismatch:",badH," with tail-root mismatch:",bad0," unbalanced G'':",unbal)
json.dump({"brute_total":tot_b,"sum_head":sumH,"sum_tail":sum0,"ec":n**(n-2)*fact(n-2)**n,
           "prefixes":len(P),"mismatch_head":badH,"mismatch_tail":bad0,"unbalanced":unbal},
          open(os.path.join(ROOT,"data","64_diag_prefix_count.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
