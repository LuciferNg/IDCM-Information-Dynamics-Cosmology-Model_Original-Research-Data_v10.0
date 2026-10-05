#!/usr/bin/env python3
"""診斷: Halton/rng 出現 achiral 係真結構抑或偽影?"""
import numpy as np, math
def rot(ax,an):
    a=np.array(ax,float); a/=np.linalg.norm(a)
    K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3)+math.sin(an)*K+(1-math.cos(an))*K@K
def closure(gens):
    G=[np.eye(3)]; fr=[np.eye(3)]
    while fr:
        new=[]
        for g in fr:
            for h in gens:
                p=h@g
                if not any(np.allclose(p,q,atol=1e-9) for q in G): G.append(p); new.append(p)
        fr=new
    return G
phi=(1+5**0.5)/2
I=closure([rot([0,1,phi],2*math.pi/5), rot([1,1,1],2*math.pi/3)])
def order(g):
    M=g.copy(); k=1
    while not np.allclose(M,np.eye(3),atol=1e-8) and k<12: M=M@g; k+=1
    return k
A2=[]
for g in I:
    if order(g)==2:
        w,Vv=np.linalg.eig(g); ax=np.real(Vv[:,np.argmin(np.abs(w-1))]); ax/=np.linalg.norm(ax)
        if not any(abs(abs(ax@u)-1)<1e-8 for u in A2): A2.append(ax)
A2=np.array(A2)
DP={(0,0,0):1.0}
for a in A2:
    nd={}
    for e,c in DP.items():
        for k in range(3):
            kk=list(e); kk[k]+=1; kk=tuple(kk); nd[kk]=nd.get(kk,0.0)+c*a[k]
    DP=nd
def deval(v):
    v=np.atleast_2d(v); o=np.zeros(len(v))
    for (i,j,k),c in DP.items(): o+=c*(v[:,0]**i)*(v[:,1]**j)*(v[:,2]**k)
    return o
def orbit(v,dec=14): return np.unique(np.round(np.array([g@v for g in I]),dec),axis=0)
def halton(i,b):
    f=1.0; r=0.0
    while i>0: f/=b; r+=f*(i%b); i//=b
    return r
def sph(u1,u2):
    z=2*u1-1; r=math.sqrt(max(0,1-z*z)); th=2*math.pi*u2
    return np.array([r*math.cos(th), r*math.sin(th), z])

print("=== Halton 首 5 個 ===")
for i in range(1,6):
    v=sph(halton(i,2),halton(i,3)); o=orbit(v)
    d=abs(float(deval(v)[0])); mn=min(np.linalg.norm(-v-p) for p in o)
    print(f"  i={i} |orbit|={len(o)} |δ|={d:.3e} min|−v−p|={mn:.3e} achiral={mn<1e-9}")

print("\n=== 掃描 Halton 1..1500 之 achiral ===")
bad=[]
for i in range(1,1501):
    v=sph(halton(i,2),halton(i,3)); o=orbit(v)
    if len(o)!=60: continue
    mn=min(np.linalg.norm(-v-p) for p in o)
    if mn<1e-9: bad.append((i,v,mn,abs(float(deval(v)[0]))))
print(f"  achiral 數 = {len(bad)}")
for i,v,mn,d in bad[:6]:
    print(f"    i={i} v={np.round(v,12)} min={mn:.3e} |δ|={d:.3e} |v·A2|max={np.abs(A2@v).max():.15f}")

print("\n=== rng(987654321) 之 achiral ===")
rng=np.random.default_rng(987654321)
for k in range(800):
    v=rng.normal(size=3); v/=np.linalg.norm(v)
    o=orbit(v)
    if len(o)!=60: continue
    mn=min(np.linalg.norm(-v-p) for p in o)
    if mn<1e-9:
        print(f"    k={k} v={np.round(v,12)} min={mn:.3e} |δ|={abs(float(deval(v)[0])):.3e}")
        print(f"      |v·A2|max = {np.abs(A2@v).max():.15f}")

print("\n=== 用 1e-6 門檻重掃 (更嚴) ===")
for thr in [1e-9,1e-8,1e-7,1e-6,1e-5,1e-4,1e-3]:
    c=0
    for i in range(1,1501):
        v=sph(halton(i,2),halton(i,3)); o=orbit(v)
        if len(o)!=60: continue
        if min(np.linalg.norm(-v-p) for p in o)<thr: c+=1
    print(f"  門檻 {thr:.0e}: achiral 數 = {c}")
print("\n=== 最近距離分佈 (Halton 1500) ===")
ds=[]
for i in range(1,1501):
    v=sph(halton(i,2),halton(i,3)); o=orbit(v)
    if len(o)!=60: continue
    ds.append(min(np.linalg.norm(-v-p) for p in o))
ds=np.array(ds)
print(f"  min={ds.min():.3e}  1%={np.percentile(ds,1):.3e}  中位={np.median(ds):.3e}")
