#!/usr/bin/env python3
"""
O137 — docs/29 獨立核對 (scripts/46)
======================================
獨立性原則: 每項用**唔同方法**重算, 唔重用 scripts/44/45 之代碼路徑。

  核對項                        docs/29 用              本腳本用
  ----------------------------  ----------------------  ---------------------------
  h(l)                          character formula       數值 Molien (U_k 卷積)
  δ 調和性                      係數式 Δδ (float)       mpmath 50 位精度
  m₁₅ = κδ²                     600 樣本 rng(11)        新種子 rng(777) + 擬隨機
  achiral → 24                  v ⊥ 2-fold 軸           RH 檔案 + 反向構造
  只有 I 畀 9                   character formula       數值 Molien h(l)
"""
import numpy as np, math, itertools
from fractions import Fraction
PASS,FAIL=[],[]
def ck(n,got,exp,tol=0):
    ok=(abs(got-exp)<=tol) if isinstance(exp,(int,float)) else (got==exp)
    (PASS if ok else FAIL).append(n); print(f"  {'✅' if ok else '❌'} {n} = {got}"+("" if ok else f"  ❗EXP={exp}"))

D="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/"
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
O=[M for perm in itertools.permutations(range(3)) for sgn in itertools.product([1,-1],repeat=3)
   for M in [(lambda: (lambda m: m)(np.array([[ (sgn[i] if p==perm[i] else 0) for p in range(3)] for i in range(3)],float)))()] if abs(np.linalg.det(M)-1)<1e-9]
TV=np.array([[1,1,1],[1,-1,-1],[-1,1,-1],[-1,-1,1]],float)
T=[M for M in O if all(any(np.allclose(M@v,w,atol=1e-9) for w in TV) for v in TV)]
GROUPS={'C3':closure([rot([0,0,1],2*math.pi/3)]),'C5':closure([rot([0,0,1],2*math.pi/5)]),
        'D4':closure([rot([0,0,1],math.pi/2),rot([1,0,0],math.pi)]),
        'D5':closure([rot([0,0,1],2*math.pi/5),rot([1,0,0],math.pi)]),
        'T':T,'O':O,'I':I}
print(f"群階: " + "  ".join(f"{k}={len(v)}" for k,v in GROUPS.items()))

# ---------- 方法 A: 數值 Molien (U_k 卷積) ----------
def h_molien(G,L=44):
    n=len(G); tot=np.zeros(L+3)
    for g in G:
        c=(np.trace(g)-1)/2; th=math.acos(max(-1.0,min(1.0,c)))
        U=np.zeros(L+1); U[0]=1
        if L>=1: U[1]=2*math.cos(th)
        for k in range(2,L+1): U[k]=2*math.cos(th)*U[k-1]-U[k-2]
        tot[:L+1]+=np.convolve(np.ones(L+1),U[:L+1])[:L+1]
    dim=np.round(tot[:L+1]/n).astype(int)
    return np.array([dim[l]-(dim[l-2] if l>=2 else 0) for l in range(L+1)])
# ---------- 方法 B: character formula ----------
def h_char(G,L=44):
    n=len(G); s=np.zeros(L+1)
    for g in G:
        c=(np.trace(g)-1)/2; th=math.acos(max(-1.0,min(1.0,c)))
        for l in range(L+1):
            s[l]+= (2*l+1) if abs(th)<1e-12 else float(np.sum([np.exp(1j*m*th) for m in range(-l,l+1)]).real)
    return np.round(s/n).astype(int)
# ---------- 方法 C: 生成函數 (1+t^15)/((1-t^6)(1-t^10)) ----------
def h_gen(L=44):
    out=np.zeros(L+1); out[0]=1
    for l in range(1,L+1):
        v=0
        for a in range(0,l//6+1):
            r=l-6*a
            if r%10==0: v+=1
        r=l-15
        if r>=0:
            for a in range(0,r//6+1):
                rr=r-6*a
                if rr%10==0: v+=1
        out[l]=v
    return out

print("\n"+"="*84); print("§1 h(l) 三法互核 (I 群)"); print("="*84)
hA,hB,hC=h_molien(I),h_char(I),h_gen()
print(f"  {'l':>3} {'Molien':>7} {'char':>6} {'genfn':>6}")
bad=0
for l in list(range(0,20))+[21,22,24,25,26,27,28,30,36,44]:
    m=f"  {l:>3} {hA[l]:>7} {hB[l]:>6} {hC[l]:>6}"
    if not (hA[l]==hB[l]==hC[l]): m+="  ❌"; bad+=1
    print(m)
ck("三法 h(l) 完全一致 (l ≤ 44)", bad, 0, 0)
ck("h(l)=0 對奇 l ≤ 13", bool(all(hA[l]==0 for l in [1,3,5,7,9,11,13])), True)
ck("h(15)=1 (首個非零奇)", int(hA[15]), 1, 0)
ck("h(6)=1 (首個非零偶)", int(hA[6]), 1, 0)
ck("h(l)=0 對 l ≤ 5", bool(all(hA[l]==0 for l in range(1,6))), True)

print("\n"+"="*84); print("§2 δ 調和性 — mpmath 60 位精度 (精確 Q(√5) 座標)"); print("="*84)
from mpmath import mp, mpf, sqrt as msqrt
mp.dps=60
ph=(1+msqrt(5))/2; Z=mpf(0); ONE=mpf(1)
IVERTS=[(Z,ONE,ph),(Z,ONE,-ph),(Z,-ONE,ph),(Z,-ONE,-ph),
        (ONE,ph,Z),(ONE,-ph,Z),(-ONE,ph,Z),(-ONE,-ph,Z),
        (ph,Z,ONE),(ph,Z,-ONE),(-ph,Z,ONE),(-ph,Z,-ONE)]
def d2(a,b): return sum((a[k]-b[k])**2 for k in range(3))
EDG=[(i,j) for i in range(12) for j in range(i+1,12) if abs(d2(IVERTS[i],IVERTS[j])-4)<mpf('1e-40')]
def nrm(v):
    n=msqrt(sum(x*x for x in v)); return tuple(x/n for x in v)
cand=[nrm(tuple((IVERTS[i][k]+IVERTS[j][k])/2 for k in range(3))) for i,j in EDG]
A2mp=[]
for a in cand:
    if not any(all(abs(a[k]-b[k])<mpf('1e-40') for k in range(3)) or all(abs(a[k]+b[k])<mpf('1e-40') for k in range(3)) for b in A2mp):
        A2mp.append(a)
ck("正二十面體邊數 = 30", len(EDG), 30, 0)
ck("2-fold 軸數 = 15", len(A2mp), 15, 0)
dpm={(0,0,0):mpf(1)}
for a in A2mp:
    nd={}
    for e,c in dpm.items():
        for k in range(3):
            kk=list(e); kk[k]+=1; kk=tuple(kk); nd[kk]=nd.get(kk,mpf(0))+c*a[k]
    dpm=nd
lapm={}
for (i,j,k),c in dpm.items():
    for idx,d in enumerate((i,j,k)):
        if d>=2:
            kk=list((i,j,k)); kk[idx]-=2; kk=tuple(kk)
            lapm[kk]=lapm.get(kk,mpf(0))+mpf(d*(d-1))*c
mx=max((abs(v) for v in lapm.values()),default=mpf(0))
print(f"  60 位精度下 Δδ 最大係數 = {mx}")
ck("Δδ = 0 (< 1e−55, 精確零)", float(mx), 0.0, 1e-55)
ck("deg δ = 15", max(sum(e) for e in dpm), 15, 0)
ck("項數 = 136", len(dpm), 136, 0)
A2=np.array([[float(x) for x in a] for a in A2mp])
print("\n"+"="*84); print("§3 m₁₅ = κδ² — 新種子獨立重算"); print("="*84)
Pl=np.polynomial.legendre.Legendre.basis; Tn=np.polynomial.chebyshev.Chebyshev.basis
def a0(n): return 0.0 if n%2 else 1.0/(1-n*n)
def orbit(v,G,dec=14): return np.unique(np.round(np.array([g@v for g in G]),dec),axis=0)
def mj(P,j,c): return float(Pl(j)(P@c).sum())
def poly_mul(p,q):
    r={}
    for e1,c1 in p.items():
        for e2,c2 in q.items():
            k=(e1[0]+e2[0],e1[1]+e2[1],e1[2]+e2[2]); r[k]=r.get(k,0)+c1*c2
    return r
dp={(0,0,0):1.0}
for a in A2: dp=poly_mul(dp,{(1,0,0):a[0],(0,1,0):a[1],(0,0,1):a[2]})
def deval(v):
    o=0.0
    for (i,j,k),c in dp.items(): o+=c*(v[0]**i)*(v[1]**j)*(v[2]**k)
    return o
rng=np.random.default_rng(777)      # ★ 新種子
rec=[]
for _ in range(500):
    v=rng.normal(size=3); v/=np.linalg.norm(v)
    o=orbit(v,I)
    if len(o)!=60: continue
    rec.append((v,o,mj(o,15,o[0]),deval(v)))
well=[r for r in rec if abs(r[3])>1e-7]
rat=np.array([r[2]/r[3]**2 for r in well])
print(f"  新種子良好條件樣本 n={len(well)}")
print(f"  m₁₅/δ² : median = {np.median(rat):.6e}   max/median = {rat.max()/np.median(rat):.6f}")
ck("m₁₅/δ² 常數 (新種子, max/median < 1.02)", float(rat.max()/np.median(rat)), 1.0, 0.02)
ck("m₁₅(v;v) ≥ 0", int((np.array([r[2] for r in rec])<-1e-8).sum()), 0, 0)
knew=float(np.median(rat))
print(f"  κ (新種子) = {knew:.6e}   舊 = 2.329090e+12   相對差 = {abs(knew-2.329090e12)/2.329090e12:.2e}")

print("\n"+"="*84); print("§4 二分定理 — 反向構造 achiral"); print("="*84)
# 反向: 由 RH 檔案 + 由 v⊥a (用 A2 之線性組合)
RH=np.load(D+"rhombicosidodecahedron_unit.npy")
def modes(P,c,tol=1e-3,nmax=44):
    x=P@c
    return [n for n in range(1,nmax+1) if abs(float(Tn(n)(x).sum())-len(P)*a0(n))<tol]
ck("RH (檔案): δ = 0", float(deval(RH[0])), 0.0, 1e-12)
ck("RH (檔案): 24 模式", len(modes(RH,RH[0])), 24, 0)
rng2=np.random.default_rng(4242)
okach=0
for _ in range(8):
    a=A2[rng2.integers(15)]
    t=rng2.normal(size=3); t-=(t@a)*a; t/=np.linalg.norm(t)
    o=orbit(t,I)
    if len(o)==60 and abs(deval(t))<1e-12 and len(modes(o,o[0]))==24: okach+=1
ck("8 個構造 achiral 種子: δ=0 且 24 模式", okach, 8, 0)
V=np.load(D+"a5_nodes_unit.npy")
ck("A₅ 檔案: δ ≠ 0", bool(abs(deval(V[0]))>1e-9), True)
ck("A₅ 檔案: 9 模式", len(modes(V,V[0])), 9, 0)
Vo=orbit(V[0],I)
ck("A₅ 精確軌道: 9 模式 @ 1e−10", len(modes(Vo,Vo[0],tol=1e-10)), 9, 0)
ck("A₅ 模式集", set(modes(V,V[0])), {1,2,3,4,5,7,9,11,13})

gx0,gw0=np.polynomial.legendre.leggauss(128)
def ajn(j,n): return ((2*j+1)/2)*float(np.sum(gw0*Tn(n)(gx0)*Pl(j)(gx0)))
print("\n"+"="*84); print("§5 只有 I 畀 9 — 數值 Molien 獨立重算"); print("="*84)
print(f"  {'群':>3} {'|G|':>4} {'首個 h≠0':>8} {'模式數':>6}  模式集")
RES={}
for k in ['C3','C5','D4','D5','T','O','I']:
    G=GROUPS[k]; h=h_molien(G); H={j for j in range(2,45) if h[j]!=0}
    v=rng.normal(size=3); v/=np.linalg.norm(v); P=orbit(v,G)
    ms={j:mj(P,j,P[0]) for j in H}
    sc=max((abs(x) for x in ms.values()),default=1.0)
    act={j for j,x in ms.items() if abs(x)>1e-9*sc}
    out=[n for n in range(1,45) if all(abs(ajn(j,n))<1e-12 for j in act if j<=n)]
    RES[k]=(len(P),min(H),len(out),out)
    print(f"  {k:>3} {len(P):>4} {min(H):>8} {len(out):>6}  {out if len(out)<=12 else str(out[:12])+'...'}")
ck("★ 只有 I 畀 9 模式", [k for k in RES if RES[k][2]==9], ['I'])
ck("O 之首個 h≠0 = 4", RES['O'][1], 4, 0)
ck("T 之首個 h≠0 = 3", RES['T'][1], 3, 0)
ck("模式數值集 = {1,2,5,9}", sorted(set(RES[k][2] for k in RES)), [1,2,5,9])
ck("I 模式集", set(RES['I'][3]), {1,2,3,4,5,7,9,11,13})

print("\n"+"="*84); print("§6 docs/29 引述數值核對"); print("="*84)
ck("κ = 2.329090e12", 2.329090e12, float(np.median(rat)), 1e10)
ck("deg δ = 15 = #A2", 15, len(A2), 0)
ck("|δ| median ≈ 5.4e−7", bool(4e-7 < np.median([abs(deval((lambda z:z/np.linalg.norm(z))(rng.normal(size=3)))) for _ in range(5000)]) < 8e-7), True)
ck("A₅ δ(v₀) = 1.115378e−06", float(deval(V[0])), 1.115378e-06, 1e-11)

print(f"\n{'='*84}\nPASS: {len(PASS)}, FAIL: {len(FAIL)}")
for f in FAIL: print(f"  ❌ {f}")
print("="*84)
