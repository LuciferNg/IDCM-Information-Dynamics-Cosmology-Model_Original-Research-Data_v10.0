#!/usr/bin/env python3
"""O222 R24/P6exact -- exact class-level prevalence for n >= 6 by prefix decomposition + BEST counting.

For the frozen convention (circuits of K_n* starting at 0 with first edge (0,1), i.e. EC(n) = n^{n-2}((n-2)!)^n):
    #{circuits whose prefix of length L satisfies the G5 criterion} = SUM over trails P of length L (first edge (0,1))
                                                                       of  #Eulerian trails of K_n* - P from end(P) to 0
and  #Eulerian trails of G from u to 0 = tau_0(G + edge(0->u)) * prod_w (deg_out''(w) - 1)!     (fixed-first-edge BEST)
tau = number of spanning in-arborescences rooted at the vertex (exact determinant, Matrix-Tree for digraphs).
Criterion (frozen G5 definition, replicated): exists a != a2 in A(P) with
     c(a,a2) = |{ q in B(P) : (a,q),(a2,q) in P, q not in {a,a2}, not anti[a][q], not anti[a2][q] }| >= 2.
Control: brute-force enumeration for n = 4 (L=5) and n = 5 (L=9) must reproduce the recorded values
     n=4: 0/256   n=5: 184704/972000 = 19.0%
Then: exact n = 6 (L = 9, 10) ; L = 21 for n = 6, 7 remains out of exact reach (5^20 prefixes) -> large-sample estimate.
Usage: /usr/bin/python3 -u scripts/63_r24_fullclass_exact.py
"""
import importlib.util, json, os, sys, time
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
def load(fn,name):
    sp=importlib.util.spec_from_file_location(name,os.path.join(HERE,fn)); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
def det_int(M):
    n=len(M); A=[[F(x) for x in r] for r in M]; det=F(1)
    for c in range(n):
        p=None
        for i in range(c,n):
            if A[i][c]!=0: p=i; break
        if p is None: return 0
        if p!=c: A[c],A[p]=A[p],A[c]; det=-det
        det*=A[c][c]
        inv=A[c][c]
        for i in range(c+1,n):
            f=A[i][c]/inv
            if f: A[i]=[A[i][k]-f*A[c][k] for k in range(n)]
    return det
def tau_0(edges_out, n, root=0):
    """# spanning in-arborescences rooted at `root` (all edges directed toward root) of digraph given by out-adjacency lists."""
    L=[[0]*n for _ in range(n)]
    for u in range(n):
        for v in edges_out[u]:
            if u!=v: L[u][u]+=1; L[u][v]-=1     # Laplacian (out-degree on diagonal)
    idx=[i for i in range(n) if i!=root]
    return det_int([[L[i][j] for j in idx] for i in idx])
def fact(x):
    r=1
    for i in range(2,x+1): r*=i
    return r
def anti_of(n, full_anti=None):
    if full_anti is None: return set()
    return set((a,b) for (a,b) in full_anti if a<n and b<n)
def crit(P, n, anti):
    A=set(a for (a,b) in P); B=set(b for (a,b) in P)
    for a in sorted(A):
        for a2 in sorted(A):
            if a==a2: continue
            c=0
            for q in B:
                if q in (a,a2): continue
                if (a,q) in P and (a2,q) in P and (a,q) not in anti and (a2,q) not in anti:
                    c+=1
                    if c>=2: return True
    return False
def trails(n, L, start=0, first=(0,1)):
    """all edge-trails of length L starting with `first` (DFS, no repeated edges)."""
    out=[]
    used={first}
    def rec(v, path):
        if len(path)==L: out.append(list(path)); return
        for w in range(n):
            if w==v: continue
            e=(v,w)
            if e in used: continue
            used.add(e); path.append(e); rec(w, path); path.pop(); used.remove(e)
    rec(first[1], [first])
    return out
def count_completions(n, P):
    """exact # Eulerian trails of K_n*-P from end(P) to 0  = tau_0(G'')*prod(deg''-1)! with G''=residual+(0->u)."""
    used=set(P); u=P[-1][1]
    res_out=[[] for _ in range(n)]
    for v in range(n):
        for w in range(n):
            if v!=w and (v,w) not in used: res_out[v].append(w)
    if len(res_out[0])==0 and u==0: return 1 if len(P)==n*(n-1) else 0
    G2=[list(r) for r in res_out]; G2[0].append(u)
    for v in range(n):
        if len(G2[v])==0: return 0
    deg=[len(G2[v]) for v in range(n)]
    t=tau_0(G2, n, u)
    if t==0: return 0
    p=1
    for v in range(n): p*=fact(deg[v]-1)
    return t*p
def exact_prevalence(n, L, anti):
    tot=0; num=0; t0=time.time()
    for P in trails(n,L):
        c=count_completions(n,P); tot+=c
        if c and crit(P,n,anti): num+=c
    ec=n**(n-2)*fact(n-2)**n
    return num,tot,ec,time.time()-t0
def brute(n,L,anti):
    out_adj=[sorted(j for j in range(n) if j!=v) for v in range(n)]
    tot=0; num=0; res=[0,0]
    ec=n**(n-2)*fact(n-2)**n
    def dfs(v,d,used,seq):
        if d==n*(n-1):
            if v==0:
                res[0]+=1
                if crit(seq[:L],n,anti): res[1]+=1
            return
        for w in out_adj[v]:
            e=(v,w)
            if e in used: continue
            if d==0 and e!=(0,1): continue
            if d==n*(n-1)-1 and w!=0: continue
            used.add(e); seq.append(e); dfs(w,d+1,used,seq); seq.pop(); used.remove(e)
    dfs(0,0,set(),[])
    return res[1],res[0],ec
def sample(n,L,anti,K,seed):
    A,C,M=1103515245,12345,2**31
    x=seed; tot=0; num=0
    out_adj=[sorted(j for j in range(n) if j!=v) for v in range(n)]
    te=n*(n-1)
    for _ in range(K):
        x=(A*x+C)%M
        rem=[list(r) for r in out_adj]; stack=[0]; vlist=[]
        guard=0
        while stack and guard<100*te:
            guard+=1; v=stack[-1]
            if rem[v]:
                x=(A*x+C)%M; w=rem[v].pop(x%len(rem[v])); stack.append(w)
            else: vlist.append(stack.pop())
        vlist.reverse()
        seq=[(vlist[i],vlist[i+1]) for i in range(len(vlist)-1)]
        if len(seq)==te and len(set(seq))==te and all(seq[i][1]==seq[i+1][0] for i in range(len(seq)-1)) and seq[-1][1]==seq[0][0]:
            k0=seq.index((0,1)); seq=seq[k0:]+seq[:k0]
            tot+=1
            if crit(seq[:L],n,anti): num+=1
    return num,tot
def main():
    print("="*100); print("O222 scripts/63 -- exact class prevalence via prefix decomposition + BEST"); print("="*100,flush=True)
    out={}
    # controls (brute force)
    for (n,L) in ((4,5),(5,9)):
        b=brute(n,L,set()); e=exact_prevalence(n,L,set())
        print("CONTROL n=%d L=%d : brute %d/%d (ec %d) | counting %d/%d (ec %d) | match %s"%(
            n,L,b[0],b[1],b[2],e[0],e[1],e[2], (b[0]==e[0] and b[1]==e[1])),flush=True)
        out["control_%d_%d"%(n,L)]={"brute":[b[0],b[1] if False else b[1]],"counting":[e[0],e[1]],"ec":e[2],"match":(b[0]==e[0] and b[1]==e[1])}
    for (n,L) in ((6,9),(6,10)):
        e=exact_prevalence(n,L,set())
        print("EXACT n=%d L=%d : constructible %d / total %d  = %.6f%%"%(n,L,e[0],e[1],100.0*e[0]/e[1]),flush=True)
        out["exact_%d_%d"%(n,L)]={"constructible":e[0],"total":e[1],"pct":100.0*e[0]/e[1],"seconds":e[3]}
    for (n,L,K) in ((6,21,20000),(7,21,20000)):
        s=sample(n,L,set(),K,20260930)
        print("SAMPLE n=%d L=%d K=%d : %d/%d = %.4f%%  [🟡 sampling]"%(n,L,K,s[0],s[1],100.0*s[0]/max(1,s[1])),flush=True)
        out["sample_%d_%d"%(n,L)]={"constructible":s[0],"circuits":s[1],"pct":100.0*s[0]/max(1,s[1]),"K":K,"sampled":True}
    json.dump(out,open(os.path.join(ROOT,"data","63_r24_fullclass_exact.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
    print("done",flush=True)
main()
