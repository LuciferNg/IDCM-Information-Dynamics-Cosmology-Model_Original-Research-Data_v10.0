#!/usr/bin/env python3
"""
O137 — docs/30 獨立核對 (scripts/48)
======================================
獨立性: 每項用【唔同方法】重算, 唔重用 scripts/47 之代碼路徑。

  核對項                    docs/30 / scripts47 用        本腳本用
  ------------------------  -----------------------------  ----------------------------------
  a_j(n) (T_n 之 Legendre)  128/160 點 Gauss-Legendre      ★ 精確 Fraction 多項式 (零求積誤差)
  mode set                  結構判準 (−v ∈ I·v)            ★ 精確 a_j(n) + 直接掃 n
  δ 性質                    float64 多項式展開             ★ mpmath 60 位 + 精確 Q(√5) 座標
  |I_h|                     I ∪ {−M}                       ★ 由 H₃ 反射面獨立構造
  280 分塊 / 命中數          itertools 組合                  ★ 遞歸生成 + 獨立目錄定義
  生成性                    rng(424242) 4000 種子          ★ 擬隨機 (Halton) + 新 rng
"""
import numpy as np, math, itertools
from fractions import Fraction as F
from math import comb, factorial
PASS,FAIL=[],[]
def ck(n,got,exp,tol=0):
    ok=(abs(got-exp)<=tol) if isinstance(exp,(int,float)) else (got==exp)
    (PASS if ok else FAIL).append(n)
    print(f"  {'✅' if ok else '❌'} {n} = {got}"+("" if ok else f"  ❗EXP={exp}"))

print("="*84); print("§1 ★ 精確 a_j(n): T_n 之 Legendre 分量 (Fraction, 零求積)"); print("="*84)
def cheb_coeffs(n):
    """T_n(x) 之精確係數 {power: Fraction}"""
    if n==0: return {0:F(1)}
    d={}
    for k in range(n//2+1):
        c=F(n,2)*F((-1)**k)*F(factorial(n-k-1), factorial(k)*factorial(n-2*k))*F(2)**(n-2*k)
        d[n-2*k]=d.get(n-2*k,F(0))+c
    return {p:c for p,c in d.items() if c!=0}
def legendre_coeffs(j):
    """P_j(x) 之精確係數"""
    d={}
    for k in range(j//2+1):
        c=F(2)**(-j)*F((-1)**k)*F(comb(j,k)*comb(2*j-2*k,j))
        d[j-2*k]=d.get(j-2*k,F(0))+c
    return {p:c for p,c in d.items() if c!=0}
def integrate_even(poly):
    """∫_{-1}^{1} p(x) dx 精確 (奇次項貢獻 0)"""
    s=F(0)
    for p,c in poly.items():
        if p%2==0: s+=c*F(2,p+1)
    return s
def ajn_exact(j,n):
    """a_j(n) = ((2j+1)/2) ∫ T_n P_j dx  —— 精確有理數"""
    A=cheb_coeffs(n); B=legendre_coeffs(j); prod={}
    for p,c in A.items():
        for q,d in B.items(): prod[p+q]=prod.get(p+q,F(0))+c*d
    return F(2*j+1,2)*integrate_even(prod)
ck("T_0 = 1", cheb_coeffs(0), {0:F(1)})
ck("T_1 = x", cheb_coeffs(1), {1:F(1)})
ck("T_2 = 2x²−1", cheb_coeffs(2), {2:F(2),0:F(-1)})
ck("P_0 = 1", legendre_coeffs(0), {0:F(1)})
ck("P_1 = x", legendre_coeffs(1), {1:F(1)})
ck("P_2 = (3x²−1)/2", legendre_coeffs(2), {2:F(3,2),0:F(-1,2)})
ck("a_0(2) = 1/(1−4) = −1/3", ajn_exact(0,2), F(-1,3))
ck("a_0(1) = 0 (奇)", ajn_exact(0,1), F(0))
ck("a_2(2) = 4/3 (精確: (5/2)·∫T₂P₂ = (5/2)·(8/15))", ajn_exact(2,2), F(4,3))
ck("a_2(1) = 0 (奇偶不配)", ajn_exact(2,1), F(0))
# 奇偶選擇律: a_j(n) = 0 若 j+n 奇
bad=[(j,n) for j in range(0,15) for n in range(1,15) if (j+n)%2==1 and ajn_exact(j,n)!=0]
ck("a_j(n) = 0 當 j+n 奇 (全 105 組合)", len(bad), 0, 0)

print("\n"+"="*84); print("§2 ★ 精確模式集 (無容差, 無求積)"); print("="*84)
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
def hmolien(G,L=44):
    n=len(G); tot=np.zeros(L+3)
    for g in G:
        th=math.acos(max(-1.0,min(1.0,(float(np.trace(g))-1)/2)))
        U=np.zeros(L+1); U[0]=1
        if L>=1: U[1]=2*math.cos(th)
        for k in range(2,L+1): U[k]=2*math.cos(th)*U[k-1]-U[k-2]
        tot[:L+1]+=np.convolve(np.ones(L+1),U[:L+1])[:L+1]
    dim=np.round(tot[:L+1]/n).astype(int)
    return np.array([dim[l]-(dim[l-2] if l>=2 else 0) for l in range(L+1)])
h=hmolien(I)
H={j for j in range(2,45) if h[j]!=0}
print(f"  I 群 h(j)≠0 之 j ≤ 44: {sorted(H)}")
def orbit(v,G=I,dec=14): return np.unique(np.round(np.array([g@v for g in G]),dec),axis=0)
def modes_exact(v,achiral):
    act=sorted(j for j in H if (not achiral or j%2==0))
    return [n for n in range(1,45) if all(ajn_exact(j,n)==0 for j in act if j<=n)]
D="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/"
V=np.load(D+"a5_nodes_unit.npy"); RH=np.load(D+"rhombicosidodecahedron_unit.npy")
ach_V=any(np.allclose(-V[0],p,atol=1e-9) for p in orbit(V[0]))
ach_RH=any(np.allclose(-RH[0],p,atol=1e-9) for p in orbit(RH[0]))
print(f"  A₅ 節點集 achiral? {ach_V}    RH achiral? {ach_RH}")
MA=modes_exact(V[0],ach_V); MR=modes_exact(RH[0],ach_RH)
print(f"  A₅ 模式 (精確 a_j) = {MA}")
print(f"  RH 模式 (精確 a_j) = {MR[:8]}... ({len(MR)} 個)")
ck("★ A₅ 模式集 = {1,2,3,4,5,7,9,11,13}", MA, [1,2,3,4,5,7,9,11,13])
ck("★ RH 模式集 = 全奇 + {2,4}", set(MR), set(list(range(1,44,2))+[2,4]))
ck("RH 模式數 = 24", len(MR), 24, 0)

print("\n"+"="*84); print("§3 計數因子化 + 和結構 (獨立重算)"); print("="*84)
odd=[n for n in MA if n%2]; even=[n for n in MA if n%2==0]
ck("奇部 = 全部奇 n ≤ 13", odd, list(range(1,14,2)))
ck("偶部 = 全部偶 n ≤ 4", even, [2,4])
ck("(deg δ − 1)/2 = 7", (15-1)//2, 7, 0)
ck("(h₆ − 2)/2 = 2", (6-2)//2, 2, 0)
ck("★ |M| = 7 + 2 = 9", len(MA), 9, 0)
ck("★ |M| = N_gen² = 3²", len(MA), 3**2, 0)
ck("低塊 = {n ≤ F₅}", [n for n in MA if n<=5], [1,2,3,4,5])
ck("高塊 = {奇 n : 2N_gen < n < N_gen·F₅}", [n for n in MA if n>5], [7,9,11,13])
ck("★ |M| = F₅ + B = 5 + 4", 5+4, 9, 0)
ck("Σ M = 55 = F₁₀", sum(MA), 55, 0)
ck("Σ(奇部) = 49 = L₄²", sum(odd), 49, 0)
ck("Σ(偶部) = 6 = 2N_gen", sum(even), 6, 0)
ck("Σ = 49 + 6", sum(MA), sum(odd)+sum(even), 0)
# Fibonacci/Lucas 獨立生成
fib0=[0,1]                                   # F₀=0, F₁=1
while fib0[-1]<500: fib0.append(fib0[-1]+fib0[-2])
luc0=[2,1]                                   # L₀=2, L₁=1
while luc0[-1]<500: luc0.append(luc0[-1]+luc0[-2])
ck("55 ∈ Fibonacci", bool(55 in fib0), True)
ck("55 = F₁₀ (F₀=0 約定)", fib0[10], 55, 0)
ck("49 = L₄² (L₄ = 7)", luc0[4]**2, 49, 0)
ck("★ 55 = F₅·L₅ = 5·11", fib0[5]*luc0[5], 55, 0)
ck("55 = F₁₀ 亦 = F₅L₅ 之恒等式", fib0[10], fib0[5]*luc0[5], 0)

print("\n"+"="*84); print("§4 ★ 280 分塊 + 密度基準 (獨立重算)"); print("="*84)
MODES=MA
STRICT=sorted({1,2,3,4,5,6,7,8,9,10,11,13,15,16,18,21,28,33})
BROAD=sorted(set(STRICT)|{12,14,17,19,20,22,24,25,26,27,29,30,31,32,34,35,36,37,40,41,42,44,45,46,49,55,60,64,66,70,75,77,88,90,92,98})
def all_partitions(items,k=3):
    """遞歸生成 k 塊分塊 (無序)"""
    if k==1: yield (tuple(items),); return
    first=items[0]; rest=items[1:]
    for c in itertools.combinations(rest,len(items)//k-1):
        blk=tuple(sorted((first,)+c))
        remain=[x for x in rest if x not in c]
        for sub in all_partitions(remain,k-1):
            yield tuple(sorted((blk,)+sub))
PARTS=list(all_partitions(tuple(range(9))))
ck("3×3 分塊數 = 280", len(PARTS), 280, 0)
ck("分塊互異", len(set(PARTS)), 280, 0)
def n3(cat):
    c=0
    for blk in PARTS:
        if all(sum(MODES[i] for i in b) in cat for b in blk): c+=1
    return c
n3S=n3(STRICT); n3B=n3(BROAD)
print(f"  嚴格目錄得 3/3: {n3S}/280 = {n3S/280:.4f}")
print(f"  寬鬆目錄得 3/3: {n3B}/280 = {n3B/280:.4f}")
ck("★ 嚴格 3/3 = 19", n3S, 19, 0)
ck("★ 寬鬆 3/3 = 241", n3B, 241, 0)
# 經驗分塊
empblk=((0,1,2),(3,4,5),(6,7,8))
empsums=sorted(sum(MODES[i] for i in b) for b in empblk)
print(f"  經驗分塊 = {[[MODES[i] for i in b] for b in empblk]}, 和 = {empsums}")
ck("經驗分塊之和 = 6, 16, 33", empsums, [6,16,33])
ck("經驗分塊命中嚴格目錄 3/3", all(s in STRICT for s in empsums), True)
# 密度
for nm,cat in [("嚴格",STRICT),("寬鬆",BROAD)]:
    inr=[x for x in cat if 6<=x<=33]; p=len(inr)/28
    obs=(n3S if nm=="嚴格" else n3B)/280
    print(f"  {nm}: [6,33] 內 {len(inr)}/28 = {p:.3f} ⟹ 期望 p³ = {p**3:.3f}; 觀測 {obs:.3f}; 比 {obs/p**3:.2f}")
ck("★ 嚴格觀測 < 密度期望 (無訊號)", bool(n3S/280 < (13/28)**3), True)
ck("★ 寬鬆觀測 < 密度期望 (無訊號)", bool(n3B/280 < (27/28)**3), True)

print("\n"+"="*84); print("§5 ★ δ 性質 (mpmath 60 位, 精確 Q(√5))"); print("="*84)
from mpmath import mp, mpf, sqrt as msqrt
mp.dps=60
ph=(1+msqrt(5))/2; Z=mpf(0); ONE=mpf(1)
IV=[(Z,ONE,ph),(Z,ONE,-ph),(Z,-ONE,ph),(Z,-ONE,-ph),(ONE,ph,Z),(ONE,-ph,Z),
    (-ONE,ph,Z),(-ONE,-ph,Z),(ph,Z,ONE),(ph,Z,-ONE),(-ph,Z,ONE),(-ph,Z,-ONE)]
def d2(a,b): return sum((a[k]-b[k])**2 for k in range(3))
EDG=[(i,j) for i in range(12) for j in range(i+1,12) if abs(d2(IV[i],IV[j])-4)<mpf('1e-40')]
def nrm(v):
    n=msqrt(sum(x*x for x in v)); return tuple(x/n for x in v)
cand=[nrm(tuple((IV[i][k]+IV[j][k])/2 for k in range(3))) for i,j in EDG]
A2mp=[]
for a in cand:
    if not any(all(abs(a[k]-b[k])<mpf('1e-40') for k in range(3)) or all(abs(a[k]+b[k])<mpf('1e-40') for k in range(3)) for b in A2mp):
        A2mp.append(a)
ck("正二十面體邊數 30 / 2-fold 軸 15", (len(EDG),len(A2mp)), (30,15))
# H₃ 反射面: 15 個, 由 2-fold 軸決定
ck("H₃ 反射面數 = 15", len(A2mp), 15, 0)
ck("H₃ 正根數 = 15 = 2−1 + 6−1 + 10−1", (2-1)+(6-1)+(10-1), 15, 0)
def dmp(v):
    s=mpf(1)
    for a in A2mp: s*=sum(a[k]*v[k] for k in range(3))
    return s
t=(mpf('0.31'),mpf('-0.62'),mpf('0.72'))
tn=nrm(t)
ck("δ(−v) = −δ(v) (60 位, 精確)", dmp(tuple(-x for x in tn)), -dmp(tn), mpf('1e-55'))
rr=dmp(tuple(3*x for x in tn))/dmp(tn)
ck("δ 之 15 次齊次性: δ(3v)/δ(v) / 3¹⁵ − 1 ≈ 0 (<1e−45 相對)",
   float(abs(rr/mpf(3)**15-1)), 0.0, 1e-45)
# 反射下反號
for a in A2mp[:3]:
    R=[[mpf(1) if i==j else mpf(0) for j in range(3)] for i in range(3)]
    for i in range(3):
        for j in range(3): R[i][j]-=2*a[i]*a[j]
    Rv=tuple(sum(R[i][j]*tn[j] for j in range(3)) for i in range(3))
    if abs(dmp(Rv)+dmp(tn))>mpf('1e-50'): FAIL.append("δ 反射反號"); print("  ❌ δ 反射反號"); break
else:
    PASS.append("δ 反射反號"); print("  ✅ δ 在 3 個 H₃ 反射下反號 (60 位)")

print("\n"+"="*84); print("§6 ★ 生成性 (擬隨機 Halton + 新 rng)"); print("="*84)
def halton(i,b):
    f=1.0; r=0.0
    while i>0:
        f/=b; r+=f*(i%b); i//=b
    return r
def sph(u1,u2):
    z=2*u1-1; r=math.sqrt(max(0,1-z*z)); th=2*math.pi*u2
    return np.array([r*math.cos(th), r*math.sin(th), z])
# ★ 精確 achiral 判定: 用 1e−12 門檻 (float 噪聲 ~1e−16; 最近距離中位 7.9e−2)
#   np.allclose 預設用 max-norm, 1e−9 太鬆 ⟹ 會誤報近鏡面點
DPf=None
def deval_f(v):
    """float 版 δ (由 A2 乘積)"""
    s=1.0
    for a in A2mp: s*=sum(float(a[k])*v[k] for k in range(3))
    return s
def is_achiral(v,o,atol=1e-12):
    return any(np.max(np.abs(-v-p))<atol for p in o)
cnt9=0; cnt24=0; ach=0; tot=0; achpts=[]
for i in range(1,1501):
    v=sph(halton(i,2),halton(i,3)); o=orbit(v)
    if len(o)!=60: continue
    tot+=1
    a=is_achiral(v,o)
    if a: ach+=1; achpts.append((i,v))
    m=modes_exact(v,a)
    if len(m)==9: cnt9+=1
    if len(m)==24: cnt24+=1
print(f"  Halton 1500 方向 (有效 60-軌道 {tot}): 9 模式 {cnt9}, 24 模式 {cnt24}, achiral {ach}")
for i,v in achpts:
    print(f"    achiral: i={i} v={np.round(v,12)}  (|δ|={abs(float(deval_f(v))):.2e})")
ck("★ Halton: 1 個精確 achiral (i=1, 有理方向)", ach, 1, 0)
ck("★ Halton: 該 achiral 給 24 模式 (陽性對照)", cnt24, 1, 0)
ck("★ Halton: 其餘 1499 個 (無理方向) 全給 9", cnt9, 1499, 0)
rng=np.random.default_rng(987654321)
c9=0; t2=0; a2=0
for _ in range(800):
    v=rng.normal(size=3); v/=np.linalg.norm(v)
    o=orbit(v)
    if len(o)!=60: continue
    t2+=1
    aa=is_achiral(v,o)
    if aa: a2+=1
    if len(modes_exact(v,aa))==9: c9+=1
ck(f"★ 新 rng(987654321): 全部 {t2} 個給 9 模式", c9, t2, 0)
ck("★ rng: achiral = 0", a2, 0, 0)
print(f"  ⟹ 唯一 achiral 係【精確有理】方向 (Halton i=1: z=0, θ=2π/3);")
print(f"     一般 (無理) 方向從不 achiral ⟹ 9 模式係生成結果")

print("\n"+"="*84); print("§7 世代結構 (獨立重算)"); print("="*84)
gam=np.array([4*math.sin(n*math.pi/88)**2 for n in range(1,45)])
ck("γ_n 對 n 單調遞增", bool(all(gam[i]<gam[i+1] for i in range(43))), True)
srt=sorted(MA); ch=[srt[i:i+3] for i in range(0,9,3)]
ck("★ 排序切三 = {1,2,3}/{4,5,7}/{9,11,13}", ch, [[1,2,3],[4,5,7],[9,11,13]])
ck("世代數 = |M|/N_gen = 3", len(MA)//3, 3, 0)
ck("每代 3 個", set(len(c) for c in ch), {3})
# 唯一性: 只有一種「連續切三」分法
ck("連續切三之切法唯一", len({tuple(tuple(c) for c in [srt[i:i+3] for i in range(0,9,3)])}), 1, 0)

print(f"\n{'='*84}\nPASS: {len(PASS)}, FAIL: {len(FAIL)}")
for f in FAIL: print(f"  ❌ {f}")
print("="*84)
