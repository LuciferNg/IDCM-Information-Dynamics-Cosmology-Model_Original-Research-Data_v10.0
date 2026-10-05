#!/usr/bin/env python3
"""
O137 — 模式判準嘅精確結構: I₁₅ = δ (15 鏡面線性型之積)
=========================================================
上輪 (docs/28) 確立 chiral 60-軌道 → 9 模式。本輪追問「13」同「4」從何來, 意外發現判準本身嘅精確結構。

★ 核心結果:
  (1) m_j(v;c) := Σᵢ P_j(vᵢ·c) ∈ (Harm^j)^I
      對 j 使 h(j)=1: m_j(v;·) = λ_j(v)·I_j(·),  且 λ_j(v) ∈ (Harm^j)^I ⟹ λ_j = κ_j I_j
      ⟹ m_j(v;v) = κ_j I_j(v)²   【完全平方, 恆 ≥ 0】
  (2) 奇 j 之 I_j ∝ δ · (偶不變量),  其中 δ := ∏_{a∈A2}(a·x)  (15 個 2-fold 軸 = 鏡面法向)
      ⟹ 所有奇 m_j(v;v) 同時 ∝ δ(v)² ⟹ 同時消失
  (3) ⟹ 模式集係【精確二分】:
         δ(v) ≠ 0 (chiral)  ⟹ 9 模式
         δ(v) = 0 (achiral) ⟹ 24 模式
      中間模式數 (10–23) 純屬數值容差偽影 (δ² 對典型 v 極細)

推導鏈:
  I ⊂ I_h (Coxeter H₃), 基本次數 2,6,10, #反射 = 15
  R^I = R^{I_h} ⊕ δ·R^{I_h}, deg δ = 15 ⟹ Σ_l h(l)t^l = (1+t¹⁵)/((1−t⁶)(1−t¹⁰))
  首個奇不變調和 = 15 ⟹ 奇模式截斷 n ≤ 13;  首個偶 = 6 ⟹ 偶 n ≤ 4
"""
import numpy as np, math
from collections import defaultdict, Counter

D="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/"
phi=(1+5**0.5)/2
PASS,FAIL=[],[]
def ck(n,got,exp,tol=1e-6):
    ok=abs(got-exp)<=tol if isinstance(exp,(int,float)) else got==exp
    (PASS if ok else FAIL).append(n)
    print(f"  {'✅' if ok else '❌'} {n} = {got}"+("" if ok else f"   ❗EXP={exp}"))

def rot(ax,an):
    a=np.array(ax,float); a/=np.linalg.norm(a)
    K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3)+math.sin(an)*K+(1-math.cos(an))*K@K
G=[np.eye(3)]; fr=[np.eye(3)]
R1,R2=rot([0,1,phi],2*math.pi/5), rot([1,1,1],2*math.pi/3)
while fr:
    new=[]
    for g in fr:
        for h in (R1,R2):
            p=h@g
            if not any(np.allclose(p,q,atol=1e-9) for q in G): G.append(p); new.append(p)
    fr=new
def order(g):
    M=g.copy(); k=1
    while not np.allclose(M,np.eye(3),atol=1e-8) and k<12: M=M@g; k+=1
    return k
A2=[]
for g in G:
    if order(g)==2:
        w,Vv=np.linalg.eig(g); ax=np.real(Vv[:,np.argmin(np.abs(w-1))]); ax/=np.linalg.norm(ax)
        if not any(abs(abs(ax@u)-1)<1e-8 for u in A2): A2.append(ax)
A2=np.array(A2)
Tn=np.polynomial.chebyshev.Chebyshev.basis; Pl=np.polynomial.legendre.Legendre.basis
def a0(n): return 0.0 if n%2 else 1.0/(1-n*n)
def orbit(v,dec=14): return np.unique(np.round(np.array([g@v for g in G]),dec),axis=0)
def modes(P,c,tol=1e-3,nmax=44):
    return [n for n in range(1,nmax+1) if abs(float(Tn(n)(P@c).sum())-len(P)*a0(n))<tol]
def mj(P,j,c): return float(Pl(j)(P@c).sum())

# ---- δ = ∏_{a∈A2}(a·x) ----
def poly_mul(p,q):
    r=defaultdict(float)
    for e1,c1 in p.items():
        for e2,c2 in q.items(): r[(e1[0]+e2[0],e1[1]+e2[1],e1[2]+e2[2])]+=c1*c2
    return r
delta_poly={(0,0,0):1.0}
for a in A2:
    delta_poly=poly_mul(delta_poly,{(1,0,0):a[0],(0,1,0):a[1],(0,0,1):a[2]})
def delta_eval(V):
    V=np.atleast_2d(V); out=np.zeros(len(V))
    for (i,j,k),c in delta_poly.items(): out+=c*(V[:,0]**i)*(V[:,1]**j)*(V[:,2]**k)
    return out

print("="*84); print("§1 δ = ∏_{a∈A2}(a·x): 次數 + 調和性"); print("="*84)
deg=max(sum(e) for e in delta_poly)
ck("deg δ = 15", deg, 15, 0)
ck("項數 = C(17,2) = 136 (3 變量 15 次全部單項式)", len(delta_poly), 136, 0)
lap=defaultdict(float)
for (i,j,k),c in delta_poly.items():
    if i>=2: lap[(i-2,j,k)]+=i*(i-1)*c
    if j>=2: lap[(i,j-2,k)]+=j*(j-1)*c
    if k>=2: lap[(i,j,k-2)]+=k*(k-1)*c
mlap=max((abs(v) for v in lap.values()), default=0.0)
print(f"  Δδ 最大係數 = {mlap:.3e}")
ck("δ 係調和 (Δδ = 0)", mlap, 0.0, 1e-9)
# δ 嘅尺度
rng=np.random.default_rng(11)
Vr=np.array([(lambda z:z/np.linalg.norm(z))(rng.normal(size=3)) for _ in range(2000)])
dv=np.abs(delta_eval(Vr))
print(f"  |δ(v)| 分佈: median={np.median(dv):.3e}  min={dv.min():.3e}  max={dv.max():.3e}")

print("\n"+"="*84); print("§2 ★ m₁₅(v;v) = κ δ(v)² (完全平方 + 比例性)"); print("="*84)
N=600; rec=[]
for _ in range(N):
    v=rng.normal(size=3); v/=np.linalg.norm(v)
    o=orbit(v)
    if len(o)!=60: continue
    rec.append((v,o,mj(o,15,o[0]),float(delta_eval(v)[0])))
vals=np.array([r[2] for r in rec])
ck("m₁₅(v;v) ≥ 0 (完全平方)", int((vals<-1e-8).sum()), 0, 0)
well=[r for r in rec if abs(r[3])>1e-7]
rat=np.array([r[2]/r[3]**2 for r in well])
print(f"  良好條件樣本 (|δ|>1e-7): n={len(well)}")
print(f"    m₁₅/δ² : min={rat.min():.6e}  median={np.median(rat):.6e}  max={rat.max():.6e}")
print(f"    max/median = {rat.max()/np.median(rat):.4f}   (1.0 = 完美比例)")
ck("m₁₅/δ² 常數 (max/median < 2.0)", float(rat.max()/np.median(rat)), 1.0, 1.0)
# κ 用 median 定
kap=float(np.median(rat))
pred=np.array([kap*r[3]**2 for r in well]); act=np.array([r[2] for r in well])
print(f"    κ = {kap:.6e};  max 相對偏差 = {np.abs(pred-act).max()/act.max():.3e}")
ck("κ δ² 重現 m₁₅", float(np.abs(pred-act).max()/act.max()), 0.0, 1e-3)

print("\n"+"="*84); print("§3 所有奇 m_j(v;v) 同時 ∝ δ²"); print("="*84)
for j in [15,21,25]:
    vv=np.array([mj(r[1],j,r[0]) for r in rec])
    w2=[(r,val) for r,val in zip(rec,vv) if abs(r[3])>1e-7]
    rr=np.array([val/r[3]**2 for r,val in w2])
    print(f"  j={j}: m_j(v;v) min={vv.min():.3e} (#負={int((vv<-1e-8).sum())}),  m_j/δ² median={np.median(rr):.4e} (n={len(w2)})")
    ck(f"m_{j}(v;v) ≥ 0", int((vv<-1e-8).sum()), 0, 0)
# 相關性: 小 δ ⟹ 小 m_j
small=[r for r in rec if abs(r[3])<1e-7]; big=[r for r in rec if abs(r[3])>3e-7]
print(f"\n  |δ|<1e-6 組 (n={len(small)}): m₁₅ median={np.median([r[2] for r in small]):.3e}")
print(f"  |δ|>3e-7 組 (n={len(big)}): m₁₅ median={np.median([r[2] for r in big]):.3e}")
ck("δ→0 ⟹ m₁₅→0", bool(np.median([r[2] for r in small]) < np.median([r[2] for r in big])), True)

print("\n"+"="*84); print("§4 ★ 精確二分: chiral → 9, achiral → 24"); print("="*84)
# 構造 achiral 種子: v ⊥ 某 2-fold 軸
ach=[]
for k in range(6):
    a=A2[k]
    t=rng.normal(size=3); t-= (t@a)*a; t/=np.linalg.norm(t)
    o=orbit(t)
    ach.append((t,o,len(o),float(delta_eval(t)[0]),len(modes(o,o[0])),len(modes(o,o[0],tol=1e-6))))
print(f"  {'k':>2} {'點數':>5} {'δ':>12} {'模式(1e-3)':>11} {'模式(1e-6)':>11}")
for k,(t,o,n,dv2,m1,m2) in enumerate(ach):
    print(f"  {k:>2} {n:>5} {dv2:>12.2e} {m1:>11} {m2:>11}")
ck("achiral 種子: δ = 0", max(abs(a[3]) for a in ach), 0.0, 1e-12)
ck("achiral 種子: 模式數 = 24 (兩種容差)", set(a[5] for a in ach)|set(a[4] for a in ach), {24})
# 實際 A₅ 節點集
V=np.load(D+"a5_nodes_unit.npy"); RH=np.load(D+"rhombicosidodecahedron_unit.npy")
print(f"\n  實際 A₅ 節點集: δ(v₀) = {float(delta_eval(V[0])[0]):.6e},  m₁₅ = {mj(V,15,V[0]):.4f}")
print(f"    κ δ² = {kap*float(delta_eval(V[0])[0])**2:.4f}  (對比 m₁₅ = {mj(V,15,V[0]):.4f})")
ck("A₅ 節點集: m₁₅ = κ δ²", float(kap*delta_eval(V[0])[0]**2), mj(V,15,V[0]), 1e-2*abs(mj(V,15,V[0]))+1e-3)
Vo=orbit(V[0])   # 由種子精確生成 ⟹ 精確 I-不變
ck("A₅ 載入節點集 模式數 (tol=1e-3)", len(modes(V,V[0],tol=1e-3)), 9, 0)
ck("A₅ 精確 I-不變軌道 模式數 (tol=1e-10)", len(modes(Vo,Vo[0],tol=1e-10)), 9, 0)
mx13=max(abs(mj(Vo,j,Vo[0])) for j in [1,3,5,7,9,11,13])
ck("精確軌道: 奇 j≤13 動差 = 0 (<1e-11)", mx13, 0.0, 1e-11)
mx13L=max(abs(mj(V,j,V[0])) for j in [1,3,5,7,9,11,13])
print(f"  載入節點集 (含 9.7e-5° 殘差): 奇 j≤13 最大動差 = {mx13L:.3e}")
print(f"  ⟹ 載入集之殘差令 tol=1e-6 時低模式亦失敗; 精確軌道則 tol=1e-9 亦得 9")
print(f"  ★ docs/27 §7 之「0.01° 擾動即崩潰」= 破壞 I-不變性, 非判準本身脆弱")
ck("RH 模式數 = 24", len(modes(RH,RH[0])), 24, 0)
ck("RH 模式集 = 全奇 + {2,4}", set(modes(RH,RH[0])), set(list(range(1,44,2))+[2,4]))
ck("A₅ 模式集", set(modes(V,V[0])), {1,2,3,4,5,7,9,11,13})

print("\n"+"="*84); print("§5 容差偽影量化"); print("="*84)
cntA=Counter(len(modes(r[1],r[0],tol=1e-3)) for r in rec)
cntB=Counter(len(modes(r[1],r[0],tol=1e-6)) for r in rec)
print(f"  600 隨機 chiral 種子:")
print(f"    絕對容差 1e-3: {dict(sorted(cntA.items()))}")
print(f"    絕對容差 1e-6: {dict(sorted(cntB.items()))}")
print(f"  ⟹ 容差收緊令 9 模式比例 {cntA[9]}/{sum(cntA.values())} → {cntB[9]}/{sum(cntB.values())}")
print(f"  ⟹ 中間模式數係偽影: |δ| 細 ⟹ m_j(v;v)=κδ² 細 ⟹ |D_n| 跌落容差以下")
print(f"  ⟹ 典型 |δ| median = {np.median(dv):.3e} ⟹ δ² ~ {np.median(dv)**2:.2e} (極細)")
print(f"  ★ 結構真值: chiral ⟹ 9, achiral ⟹ 24 (精確二分)")

print("\n"+"="*84); print("§6 為何截斷於 13 同 4 (生成函數)"); print("="*84)
print(f"""
  h(l) := dim(I-不變調和, 次數 l)
  Σ_l h(l) t^l = (1 + t¹⁵)/((1−t⁶)(1−t¹⁰))
  來源: R^I = R^{{I_h}} ⊕ δ·R^{{I_h}},  R^{{I_h}} = R[f₂,f₆,f₁₀],  deg δ = 15
  h(odd l) = 0 對 l ≤ 13;  h(15) = h(21) = h(25) = 1
  h(6) = 1 (首個非零, = 5-design 之後)
  ⟹ 奇模式: 需 a_j(n)=0 ∀ j∈{{15,21,25,...}}∩[2,n] ⟹ n ≤ 13 (7 個)
  ⟹ 偶模式: 需 a_j(n)=0 ∀ j∈{{6,10,12,...}}∩[2,n] ⟹ n ≤ 4 (2 個)
  ⟹ 合計 9
  ★ 而 deg δ = 15 = #H₃ 反射面 = #icosahedron 鏡面 = #I 嘅 2-fold 軸
""")
ck("deg δ = #2-fold 軸", deg, len(A2), 0)

print(f"\n{'='*84}\nPASS: {len(PASS)}, FAIL: {len(FAIL)}")
for f in FAIL: print(f"  ❌ {f}")
print("="*84)
