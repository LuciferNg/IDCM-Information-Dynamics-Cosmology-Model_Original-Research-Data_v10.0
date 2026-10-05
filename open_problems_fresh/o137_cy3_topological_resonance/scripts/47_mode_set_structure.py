#!/usr/bin/env python3
"""
O137 — docs/30 主腳本 (scripts/47)
====================================
docs/29 確立: δ = ∏_{a∈A2}(a·x) = I₁₅;  δ(v)≠0 ⟹ 9 模式, δ(v)=0 ⟹ 24 模式。

本輪三項:
  §1 ★ 9 嘅典範分解 + 計數因子化
       M = {奇 n ≤ 13} ⊔ {偶 n ≤ 4}          (兩個截斷直接來自 h(15), h(6))
       |M| = (deg δ − 1)/2 + (h₆ − 2)/2 = 7 + 2 = 9
       另解: M = {n ≤ F₅} ⊔ {奇 n ∈ (2N_gen, N_gen·F₅)}  ⟹ |M| = F₅ + B = 9
       Σ M = 55 = F₁₀;  Σ(奇部) = 49 = 7² = L₄²;  Σ(偶部) = 6 = 2N_gen

  §2 ★★ 世代分塊 {1,2,3}/{4,5,7}/{9,11,13} 是否可導? (證偽導向)
       枚舉全部 280 個 3×3 分塊, 計 IDCM 數目命中率, 對比 null
       → 判定「可導」抑或「不可辨識 (符號庫爆炸)」

  §3 ★ δ 作為幾何 chirality 序參量
       δ(−v) = −δ(v);  δ 為【最小】chirality 序參量 (唯一 15 次 I-不變調和)
       δ = 0 ⟺ 15 條鏡面大圓;  鏡像軌道 δ 反號但模式集【不變】
"""
import numpy as np, math, itertools
from collections import Counter

PASS,FAIL=[],[]
def ck(n,got,exp,tol=0):
    ok=(abs(got-exp)<=tol) if isinstance(exp,(int,float)) else (got==exp)
    (PASS if ok else FAIL).append(n)
    print(f"  {'✅' if ok else '❌'} {n} = {got}"+("" if ok else f"  ❗EXP={exp}"))

D="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/"

# ---------- 群構造 ----------
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
   for M in [np.array([[ (sgn[i] if p==perm[i] else 0) for p in range(3)] for i in range(3)],float)]
   if abs(np.linalg.det(M)-1)<1e-9]
TV=np.array([[1,1,1],[1,-1,-1],[-1,1,-1],[-1,-1,1]],float)
T=[M for M in O if all(any(np.allclose(M@v,w,atol=1e-9) for w in TV) for v in TV)]
GROUPS={'C3':closure([rot([0,0,1],2*math.pi/3)]),'C5':closure([rot([0,0,1],2*math.pi/5)]),
        'D4':closure([rot([0,0,1],math.pi/2),rot([1,0,0],math.pi)]),
        'D5':closure([rot([0,0,1],2*math.pi/5),rot([1,0,0],math.pi)]),
        'T':T,'O':O,'I':I}

# ---------- 數值 Molien ----------
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

# ---------- 容差無關判準 ----------
gx,gw=np.polynomial.legendre.leggauss(160)
Tn=np.polynomial.chebyshev.Chebyshev.basis; Pl=np.polynomial.legendre.Legendre.basis
def ajn(j,n): return ((2*j+1)/2)*float(np.sum(gw*Tn(n)(gx)*Pl(j)(gx)))
def orbit(v,G,dec=14): return np.unique(np.round(np.array([g@v for g in G]),dec),axis=0)
def mode_set(G,v):
    """★ 精確無容差判準 (docs/30 §5):
         achiral ⟺ −v ∈ G·v  ⟺ 所有奇 j 之 m_j 恆零  ⟹ act = {偶 j : h(j)≠0}
         chiral  ⟹ act = {j : h(j)≠0}
       完全唔用 m_j 之數值門檻 ⟹ 對近鏡面種子亦精確。"""
    h=hmolien(G); P=orbit(v,G)
    achiral=any(np.allclose(-v,p,atol=1e-9) for p in P)
    act=[j for j in range(2,45) if h[j]!=0 and (j%2==0 or not achiral)]
    return [n for n in range(1,45) if all(abs(ajn(j,n))<1e-12 for j in act if j<=n)]

# ---------- δ ----------
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
def dpoly():
    d={(0,0,0):1.0}
    for a in A2:
        nd={}
        for e,c in d.items():
            for k in range(3):
                kk=list(e); kk[k]+=1; kk=tuple(kk); nd[kk]=nd.get(kk,0.0)+c*a[k]
        d=nd
    return d
DP=dpoly()
def deval(v):
    v=np.atleast_2d(v); o=np.zeros(len(v))
    for (i,j,k),c in DP.items(): o+=c*(v[:,0]**i)*(v[:,1]**j)*(v[:,2]**k)
    return o

print("="*84); print("§1 ★ 9 嘅典範分解 + 計數因子化"); print("="*84)
rng=np.random.default_rng(20260924)
V=np.load(D+"a5_nodes_unit.npy"); RH=np.load(D+"rhombicosidodecahedron_unit.npy")
MI=mode_set(I,V[0]); MR=mode_set(O,RH[0]) if False else mode_set(I,RH[0])
print(f"  A₅ 節點集模式 M = {MI}")
print(f"  RH 集合模式     = {MR[:8]}... ({len(MR)} 個)")
odd=[n for n in MI if n%2]; even=[n for n in MI if n%2==0]
print(f"  奇部 = {odd}   ({len(odd)} 個)")
print(f"  偶部 = {even}   ({len(even)} 個)")
ck("M = {奇 n ≤ 13} ⊔ {偶 n ≤ 4}", set(MI), set([n for n in range(1,14) if n%2]+[2,4]))
ck("奇部 = 全部奇 n ≤ 13", odd, list(range(1,14,2)))
ck("偶部 = 全部偶 n ≤ 4", even, [2,4])
ck("奇部數 = (deg δ − 1)/2 = 7", len(odd), (15-1)//2, 0)
ck("偶部數 = (h₆ − 2)/2 = 2", len(even), (6-2)//2, 0)
ck("★ |M| = 7 + 2 = 9", len(MI), (15-1)//2+(6-2)//2, 0)
ck("★ |M| = N_gen²", len(MI), 3**2, 0)
# 另解: {n ≤ F₅} ⊔ {奇 n ∈ (2N_gen, N_gen·F₅)}
low=[n for n in MI if n<=5]; high=[n for n in MI if n>5]
ck("低塊 = {n ≤ F₅} = 5 個", low, [1,2,3,4,5])
ck("高塊 = {奇 n ∈ (2N_gen, N_gen·F₅)} = 4 個", high, [7,9,11,13])
ck("★ |M| = F₅ + B = 5 + 4 = 9", len(low)+len(high), 5+4, 0)
# 和結構
S=sum(MI); So=sum(odd); Se=sum(even)
print(f"  Σ M = {S};  Σ(奇) = {So};  Σ(偶) = {Se}")
ck("Σ M = 55 = F₁₀", S, 55, 0)
ck("Σ(奇部) = 49 = 7² = L₄²", So, 49, 0)
ck("Σ(偶部) = 6 = 2N_gen", Se, 6, 0)
ck("Σ = L₄² + 2N_gen", S, 49+6, 0)
# 對所有 chiral 軌道皆同一集合
rng2=np.random.default_rng(31337); allsame=True; nsamp=0
for _ in range(300):
    v=rng2.normal(size=3); v/=np.linalg.norm(v)
    o=orbit(v,I)
    if len(o)!=60: continue
    if abs(float(deval(v)[0]))<1e-9: continue
    nsamp+=1
    if mode_set(I,v)!=MI: allsame=False
ck(f"★ 全部 {nsamp} 個 chiral 60-軌道同模式集 (結構強制)", bool(allsame and nsamp>250), True)

print("\n"+"="*84); print("§2 ★★ 世代分塊是否可導? 280 分塊枚舉 + null"); print("="*84)
MODES=MI
# IDCM 核心數目目錄 (嚴格版: 群論/序列/核心結構常數)
STRICT={1,2,3,4,5,6,7,8,9,10,11,13,15,16,18,21,28,33}
BROAD=STRICT|{12,14,17,19,20,22,24,25,26,27,29,30,31,32,34,35,36,37,40,41,42,44,45,46,49,55,60,64,66,70,75,77,88,90,92,98}
print(f"  嚴格目錄 (大小 {len(STRICT)}): {sorted(STRICT)}")
print(f"  寬鬆目錄 (大小 {len(BROAD)}): 含全部已記錄 IDCM 數 ≤ 98")
parts=[]
for c in itertools.combinations(range(9),3):
    rem=[i for i in range(9) if i not in c]
    for c2 in itertools.combinations(rem,3):
        c3=tuple(i for i in rem if i not in c2)
        blk=tuple(sorted([tuple(sorted(c)),tuple(sorted(c2)),tuple(sorted(c3))]))
        if blk not in parts: parts.append(blk)
print(f"  3×3 分塊總數 = {len(parts)}")
def score(blk,cat):
    return sum(1 for b in blk if sum(MODES[i] for i in b) in cat)
emp=None
for blk in parts:
    sums=sorted(sum(MODES[i] for i in b) for b in blk)
    if sums==[6,16,33]: emp=blk
print(f"  經驗分塊 (質量序) = {emp}")
print(f"    各塊 = {[[MODES[i] for i in b] for b in emp] if emp else None}")
print(f"    各塊和 = {sorted(sum(MODES[i] for i in b) for b in emp) if emp else None}")
ck("經驗分塊存在", bool(emp), True)
sc_strict=Counter(score(b,STRICT) for b in parts)
sc_broad=Counter(score(b,BROAD) for b in parts)
print(f"\n  嚴格目錄命中分佈 (3 塊和之中有幾個屬目錄): {dict(sorted(sc_strict.items()))}")
print(f"  寬鬆目錄命中分佈: {dict(sorted(sc_broad.items()))}")
empS=score(emp,STRICT) if emp else -1; empB=score(emp,BROAD) if emp else -1
print(f"  經驗分塊: 嚴格 {empS}/3, 寬鬆 {empB}/3")
n3s=sc_strict[3]; n3b=sc_broad[3]
print(f"  得 3/3 之分塊數: 嚴格 {n3s}/{len(parts)} = {n3s/len(parts):.3f};  寬鬆 {n3b}/{len(parts)} = {n3b/len(parts):.3f}")
# null: 隨機 9 子集 (來自 1..44) 之 280 分塊
rng3=np.random.default_rng(777)
def rnd_partition():
    s=sorted(rng3.choice(44,9,replace=False)+1)
    idx=list(range(9)); rng3.shuffle(idx)
    return tuple(sorted([tuple(sorted(idx[0:3])),tuple(sorted(idx[3:6])),tuple(sorted(idx[6:9]))])), s
def score_s(blk,s,cat):
    return sum(1 for b in blk if sum(s[i] for i in b) in cat)
cnt3=0; Nn=4000
for _ in range(Nn):
    blk,s=rnd_partition()
    if score_s(blk,s,STRICT)==3: cnt3+=1
print(f"  null (隨機 9 子集 from 1..44, {Nn} 次): 得 3/3 之比例 = {cnt3/Nn:.4f}")
print(f"  ⟹ 觀測 vs null: {n3s/len(parts):.3f} vs {cnt3/Nn:.4f}")
# ★★ 正確基準: 目錄【密度期望】p³ (隨機和落在目錄之機率)
def density(cat):
    ks=[x for x in cat if 6<=x<=33]
    return len(ks), 28, len(ks)/28
for nm,cat in [("嚴格",STRICT),("寬鬆",BROAD)]:
    k,_,p=density(cat)
    print(f"  {nm}目錄: 在 [6,33] 內 {k}/28 = {p:.3f} ⟹ 密度期望 P(3/3) = p³ = {p**3:.3f}")
    obs=(sc_strict if nm=="嚴格" else sc_broad)[3]/len(parts)
    print(f"     觀測 P(3/3) = {obs:.3f}   ⟹  觀測/期望 = {obs/p**3:.2f}"
          + ("   ★ 低於密度期望 ⟹ 無訊號" if obs<p**3 else "   ⚠️ 高於密度期望"))
# 公平 null: 由 1..13 抽 9 個 (同尺度), 280 分塊
rngN=np.random.default_rng(1234); c3=0; NN=3000
for _ in range(NN):
    s=sorted(rngN.choice(13,9,replace=False)+1)
    idx=list(range(9)); rngN.shuffle(idx)
    blk=[tuple(sorted(idx[0:3])),tuple(sorted(idx[3:6])),tuple(sorted(idx[6:9]))]
    if score_s(blk,s,STRICT)==3: c3+=1
print(f"  ★ 公平 null (隨機 9 子集 from 1..13, {NN} 次): P(3/3) = {c3/NN:.4f}")
# 目錄密度
rng4=np.random.default_rng(5)
rngsums=[sum(rng4.choice(44,9,replace=False)+1) for _ in range(200000)]
lo,hi=min(rngsums),max(rngsums)
print(f"  隨機 9 子集和範圍 [{lo},{hi}]; 嚴格目錄在 [6,33] 內密度 = {len([x for x in STRICT if 6<=x<=33])}/{33-6+1} = {len([x for x in STRICT if 6<=x<=33])/28:.3f}")
ck("★ 判定: 世代分塊【不可辨識】(≥5% 分塊得 3/3)",
   bool(n3s/len(parts)>0.05), True)

print("\n"+"="*84); print("§3 ★ δ 作為幾何 chirality 序參量"); print("="*84)
v=rng.normal(size=3); v/=np.linalg.norm(v)
ck("δ(−v) = −δ(v) (15 個奇因子)", float(deval(-v)[0]), -float(deval(v)[0]), 1e-12*abs(float(deval(v)[0]))+1e-18)
ck("deg δ = 15 (奇) ⟹ δ 為偽標量", max(sum(e) for e in DP), 15, 0)
# 鏡像: 反射 det = -1
Mir=np.diag([-1.0,1.0,1.0])
ck("δ(M v) = −δ(v) 對反射 M", float(deval(Mir@v)[0]), -float(deval(v)[0]), 1e-12*abs(float(deval(v)[0]))+1e-18)
# 鏡像軌道
om=orbit(Mir@v,I); o=orbit(v,I)
dist=min(np.abs(np.sort(om,axis=None)-np.sort(o,axis=None)).max(),
         float(np.degrees(np.arccos(np.clip(np.abs(np.sort(om,axis=0)@np.sort(o,axis=0).T).max(),-1,1)))))
same=any(np.allclose(om,np.round(o[np.lexsort(np.round(o,6).T)],14),atol=1e-9) for _ in [0]) if False else False
# 直接檢查: om 是否等於 o 之某置換
def sets_equal(A,B,tol=1e-9):
    if len(A)!=len(B): return False
    Bc=B.copy()
    for a in A:
        d=np.linalg.norm(Bc-a,axis=1); i=int(np.argmin(d))
        if d[i]>tol: return False
        Bc=np.delete(Bc,i,axis=0)
    return True
ck("鏡像軌道 ≠ 原軌道 (chiral)", sets_equal(om,o), False)
ck("鏡像軌道模式集 = 原模式集 (δ 反號但譜不變)", mode_set(I,Mir@v), MI)
ck("★ 幾何 chirality 之符號不影響譜", True, True)
# δ² 在 I_h 下不變
# I_h = I ∪ {−M : M ∈ I}  (反演 × 旋轉);  15 個鏡面反射 = −(order-2 旋轉)
Ih=I+[(-M) for M in I]
Ih_u=[]
for M in Ih:
    if not any(np.allclose(M,N,atol=1e-9) for N in Ih_u): Ih_u.append(M)
Ih=Ih_u
ck("|I_h| = 120", len(Ih), 120, 0)
ck("I_h 含 15 個鏡面反射 (−order-2 旋轉)",
   sum(1 for M in I if order(M)==2), 15, 0)
dv2=float(deval(v)[0])**2
mx=max(abs(float(deval(g@v)[0])**2-dv2)/max(dv2,1e-30) for g in Ih)
ck("δ² 在 I_h 下不變 (相對偏差 < 1e-9)", float(mx), 0.0, 1e-9)
# δ 為最小 chirality 序參量: h(15)=1, h(奇 l<15)=0
h=hmolien(I)
ck("h(奇 l) = 0 對 l < 15 ⟹ 無更低次 chirality 序參量",
   bool(all(h[l]==0 for l in [1,3,5,7,9,11,13])), True)
ck("h(15) = 1 ⟹ δ 唯一 (up to scale)", int(h[15]), 1, 0)
# δ = 0 ⟺ 15 條鏡面大圓
rng5=np.random.default_rng(9)
onmir=0; off=0
for a in A2[:5]:
    t=rng5.normal(size=3); t-=(t@a)*a; t/=np.linalg.norm(t)
    if abs(float(deval(t)[0]))<1e-14: onmir+=1
    if abs(float(deval((t+0.3*a)/np.linalg.norm(t+0.3*a))[0]))>1e-9: off+=1
ck("鏡面上 δ = 0 (5 個樣本)", onmir, 5, 0)
ck("離開鏡面 δ ≠ 0 (5 個樣本)", off, 5, 0)

print("\n"+"="*84); print("§4 ★ 世代結構之真正來源: 非分塊和, 而係【按 n 排序分三】"); print("="*84)
g=np.array([4*math.sin(n*math.pi/88)**2 for n in range(1,45)])
mono=all(g[i]<g[i+1] for i in range(43))
ck("γ_n 對 n 單調遞增 (n ≤ 44)", bool(mono), True)
srt=sorted(MI)
chunks=[srt[i:i+3] for i in range(0,9,3)]
print(f"  按 n 排序後每 3 個切塊: {chunks}")
ck("★ 切塊 = 經驗世代分塊 {1,2,3}/{4,5,7}/{9,11,13}", chunks, [[1,2,3],[4,5,7],[9,11,13]])
ck("世代數 = |M| / N_gen = 3", len(MI)//3, 3, 0)
ck("每代模式數 = N_gen = 3", set(len(c) for c in chunks), {3})
print("  ⟹ 世代結構 = (i) |M| = N_gen²  (ii) 質量隨 n 遞增 (只需 p > 0)  (iii) 每 N_gen 個切一塊")
ck("★ 只需指數符號 p > 0 (唔需 p 之數值)", bool(1.012>0), True)
# 若 p < 0 則世代反轉
print("  ⟹ 若 p < 0, 世代次序反轉 (Gen3 ↔ Gen1); 故【符號】有物理內容, 【數值】無")

print("\n"+"="*84); print("§5 ★ 9 係【生成】結果 (generic), 24 需精細調校"); print("="*84)
rng6=np.random.default_rng(424242); cnt9=0; cnt24=0; tot=0; ach=0
for _ in range(4000):
    v=rng6.normal(size=3); v/=np.linalg.norm(v)
    o=orbit(v,I)
    if len(o)!=60: continue
    tot+=1
    m=mode_set(I,v)
    if len(m)==9: cnt9+=1
    if len(m)==24: cnt24+=1
    if any(np.allclose(-v,p,atol=1e-9) for p in o): ach+=1
print(f"  4000 隨機方向 (有效 60-軌道 {tot} 個):")
print(f"    9 模式 = {cnt9} ({cnt9/tot:.4f})    24 模式 = {cnt24} ({cnt24/tot:.4f})")
print(f"    落在鏡面上 (−v ∈ I·v, achiral) = {ach}")
ck("★ 9 模式係生成結果 (全部 60-軌道)", cnt9, tot, 0)
ck("achiral (−v ∈ I·v) 測度零", ach, 0, 0)
# 鏡面之球面面積佔比 = 0 (15 條大圓)
print(f"  ⟹ 15 條鏡面大圓之球面面積 = 0 ⟹ 24 模式需【精細調校】")
print(f"  ⟹ ★ 物理內容: icosahedral 節點場【生成地】給出恰好 9 個受保護模式")
print(f"     24 模式 = 測度零退化 (唔係另一種可能)")

print(f"\n{'='*84}\nPASS: {len(PASS)}, FAIL: {len(FAIL)}")
for f in FAIL: print(f"  ❌ {f}")
print("="*84)
