#!/usr/bin/env python3
"""
O137 — 「為何係二十面體群?」: 所有有限旋轉群嘅受保護模式數掃描
=================================================================
問題: 9 模式係 I (icosahedral) 獨有, 定係其他群都畀得出?

方法 (容差無關嘅結構判準):
  模式集 = { n ≤ 44 : a_j(n)·m_j(c) = 0  ∀ j ≥ 2 }
    a_j(n) := ((2j+1)/2)∫₋₁¹ T_n(x)P_j(x)dx      (Gauss-Legendre, 精確零)
    m_j(c) := Σᵢ P_j(vᵢ·c)                        (軌道動差)
    h(j) := dim(G-不變調和, 次數 j) = (1/|G|)Σ_g χ_{Harm^j}(g)
  h(j)=0 ⟹ m_j ≡ 0 (結構性); h(j)≠0 且 |m_j| > ε·scale ⟹ 活躍 ⟹ 禁止 j ≤ n 嘅模式
"""
import numpy as np, math, itertools
from collections import Counter

PASS,FAIL=[],[]
def ck(n,got,exp,tol=0):
    ok=(abs(got-exp)<=tol) if isinstance(exp,(int,float)) else (got==exp)
    (PASS if ok else FAIL).append(n); print(f"  {'✅' if ok else '❌'} {n} = {got}"+("" if ok else f"  ❗EXP={exp}"))

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
GROUPS={}
GROUPS['C3']=closure([rot([0,0,1],2*math.pi/3)])
GROUPS['C4']=closure([rot([0,0,1],math.pi/2)])
GROUPS['C5']=closure([rot([0,0,1],2*math.pi/5)])
GROUPS['C6']=closure([rot([0,0,1],math.pi/3)])
GROUPS['D3']=closure([rot([0,0,1],2*math.pi/3), rot([1,0,0],math.pi)])
GROUPS['D4']=closure([rot([0,0,1],math.pi/2), rot([1,0,0],math.pi)])
GROUPS['D5']=closure([rot([0,0,1],2*math.pi/5), rot([1,0,0],math.pi)])
# O (cube, 24): 全部 det=+1 帶號置換矩陣
O=[]
for perm in itertools.permutations(range(3)):
    for sgn in itertools.product([1,-1],repeat=3):
        M=np.zeros((3,3)); 
        for i,p in enumerate(perm): M[i,p]=sgn[i]
        if abs(np.linalg.det(M)-1)<1e-9: O.append(M)
GROUPS['O']=O
# T (tetrahedron, 12): O 中保持四面體頂點集者
TV=np.array([[1,1,1],[1,-1,-1],[-1,1,-1],[-1,-1,1]],float)
T=[M for M in O if all(any(np.allclose(M@v,w,atol=1e-9) for w in TV) for v in TV)]
GROUPS['T']=T
# I (icosahedron, 60)
GROUPS['I']=closure([rot([0,1,phi],2*math.pi/5), rot([1,1,1],2*math.pi/3)])
GROUPS['C2']=closure([rot([0,0,1],math.pi)])
GROUPS['D2']=closure([rot([1,0,0],math.pi), rot([0,1,0],math.pi)])

print("="*84); print("§1 群階數"); print("="*84)
for k in ['C2','C3','C4','C5','C6','D2','D3','D4','D5','T','O','I']:
    print(f"  {k:>3}: |G| = {len(GROUPS[k]):>3}")

# Gauss-Legendre 節點 (n+j ≤ 88 ⟹ 需 >44 節點)
gx,gw=np.polynomial.legendre.leggauss(128)
Tn=np.polynomial.chebyshev.Chebyshev.basis; Pl=np.polynomial.legendre.Legendre.basis
def a_jn(j,n):
    return ((2*j+1)/2)*float(np.sum(gw*Tn(n)(gx)*Pl(j)(gx)))
def harm_char(g):
    """χ_{Harm^l}(g) 逐 l — 用 trace 求旋轉角 (eigvals 排序唔可靠, order-2 元素會誤報)"""
    ang=math.acos(max(-1.0,min(1.0,(float(np.trace(g))-1)/2)))
    out=[]
    for l in range(0,45):
        out.append(2*l+1 if abs(ang)<1e-12 else float(np.sum([np.exp(1j*m*ang) for m in range(-l,l+1)]).real))
    return np.array(out)
def hseries(G,L=44):
    s=np.zeros(L+1)
    for g in G: s+=harm_char(g)[:L+1]
    return np.round(s/len(G)).astype(int)
def orbit_of(v,G,dec=14): return np.unique(np.round(np.array([g@v for g in G]),dec),axis=0)
def mode_set(P,c,G,rel=1e-9,L=44):
    h=hseries(G,L); H={j for j in range(2,L+1) if h[j]!=0}
    ms={j:float(Pl(j)(P@c).sum()) for j in H}
    scale=max((abs(x) for x in ms.values()),default=1.0)
    act={j for j,x in ms.items() if abs(x)>rel*scale}
    out=[]
    for n in range(1,L+1):
        if all(abs(a_jn(j,n))<1e-12 for j in act if j<=n): out.append(n)
    return out,act,h

print("\n"+"="*84); print("§2 各群 h(l) 結構 (首個非零 j)"); print("="*84)
print(f"  {'群':>3} {'|G|':>4} {'h(j)≠0 之 j ≤ 30':<40} {'首個':>5}")
H_cache={}
for k in ['C2','C3','C4','C5','C6','D2','D3','D4','D5','T','O','I']:
    G=GROUPS[k]; h=hseries(G,44); H_cache[k]=(h,{j for j in range(2,45) if h[j]!=0})
    lst=sorted(j for j in H_cache[k][1] if j<=30)
    print(f"  {k:>3} {len(G):>4} {str(lst):<40} {min(H_cache[k][1]):>5}")

print("\n"+"="*84); print("§3 ★ 各群 generic 軌道嘅受保護模式數 (nmax=44)"); print("="*84)
rng=np.random.default_rng(20260924)
print(f"  {'群':>3} {'|軌道|':>6} {'模式數':>6}  模式集")
RES={}
for k in ['C2','C3','C4','C5','C6','D2','D3','D4','D5','T','O','I']:
    G=GROUPS[k]; v=rng.normal(size=3); v/=np.linalg.norm(v)
    P=orbit_of(v,G)
    ms,act,h=mode_set(P,P[0],G)
    RES[k]=(len(P),len(ms),ms)
    print(f"  {k:>3} {len(P):>6} {len(ms):>6}  {ms if len(ms)<=12 else str(ms[:12])+'...'}")

print("\n"+"="*84); print("§4 邊個群畀得出 9?"); print("="*84)
nine=[k for k in RES if RES[k][1]==9]
print(f"  模式數 = 9 嘅群: {nine if nine else '（無）'}")
ck("★ I 畀 9 模式", RES['I'][1], 9, 0)
ck("★ I 模式集 = {1,2,3,4,5,7,9,11,13}", set(RES['I'][2]), {1,2,3,4,5,7,9,11,13})
ck("O (立方群) 模式數 ≤ 5", bool(RES['O'][1]<=5), True)
ck("T (四面體群) 模式數 ≤ 5", bool(RES['T'][1]<=5), True)
print(f"\n  ⟹ 9 = {sorted(set(RES[k][1] for k in RES))} 之中嘅最小值?")
vals=sorted(set(RES[k][1] for k in RES))
print(f"     全部群嘅模式數值集: {vals}")

print("\n"+"="*84); print("§5 A₅ 種子嘅 |δ(v₀)| 百分位"); print("="*84)
def poly_mul(p,q):
    r={}
    for e1,c1 in p.items():
        for e2,c2 in q.items():
            k=(e1[0]+e2[0],e1[1]+e2[1],e1[2]+e2[2]); r[k]=r.get(k,0)+c1*c2
    return r
def order(g):
    M=g.copy(); k=1
    while not np.allclose(M,np.eye(3),atol=1e-8) and k<12: M=M@g; k+=1
    return k
A2=[]
for g in GROUPS['I']:
    if order(g)==2:
        w,Vv=np.linalg.eig(g); ax=np.real(Vv[:,np.argmin(np.abs(w-1))]); ax/=np.linalg.norm(ax)
        if not any(abs(abs(ax@u)-1)<1e-8 for u in A2): A2.append(ax)
dp={(0,0,0):1.0}
for a in A2: dp=poly_mul(dp,{(1,0,0):a[0],(0,1,0):a[1],(0,0,1):a[2]})
def deval(V):
    V=np.atleast_2d(V); o=np.zeros(len(V))
    for (i,j,k),c in dp.items(): o+=c*(V[:,0]**i)*(V[:,1]**j)*(V[:,2]**k)
    return o
Vr=np.array([(lambda z:z/np.linalg.norm(z))(rng.normal(size=3)) for _ in range(20000)])
dvals=np.abs(deval(Vr))
D="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/"
V=np.load(D+"a5_nodes_unit.npy"); d0=abs(float(deval(V[0])[0]))
pct=100.0*np.mean(dvals<d0)
print(f"  |δ(v₀)| = {d0:.6e}")
print(f"  20000 隨機方向: median = {np.median(dvals):.3e}, 95% = {np.percentile(dvals,95):.3e}, max = {dvals.max():.3e}")
print(f"  ⟹ A₅ 種子百分位 = {pct:.1f}%  (>95% ⟹ 遠離所有鏡面)")
ck("A₅ 種子 |δ| > 隨機 median", bool(d0>np.median(dvals)), True)

print(f"\n{'='*84}\nPASS: {len(PASS)}, FAIL: {len(FAIL)}")
for f in FAIL: print(f"  ❌ {f}")
print("="*84)
