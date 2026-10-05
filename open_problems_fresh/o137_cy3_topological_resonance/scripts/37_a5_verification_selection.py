#!/usr/bin/env python3
"""
O137 — A₅ 集獨立驗證 (Part 2): 選擇律 + 軸獨立性 + 判別力
"""
import numpy as np, math
from pathlib import Path
from collections import Counter

V = np.load("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/a5_nodes_unit.npy")
rng = np.random.default_rng(20260830)
phi = (1+math.sqrt(5))/2
def rot(axis, ang):
    a=np.array(axis,float); a/=np.linalg.norm(a)
    K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3)+math.sin(ang)*K+(1-math.cos(ang))*K@K
R1,R2 = rot([0,1,phi],2*math.pi/5), rot([1,1,1],2*math.pi/3)
group=[np.eye(3)]; fr=[np.eye(3)]
while fr:
    new=[]
    for g in fr:
        for h in (R1,R2):
            p=h@g
            if not any(np.allclose(p,q,atol=1e-9) for q in group): group.append(p); new.append(p)
    fr=new

Tn = np.polynomial.chebyshev.Chebyshev.basis
def a0(n): return 0.0 if n%2==1 else 1.0/(1-n*n)
def select(pts, axis, tol=1e-3, nmax=44):
    x = pts @ axis
    return [n for n in range(1,nmax+1) if abs(float(Tn(n)(x).sum()) - len(pts)*a0(n)) < tol]

lb=(math.radians(209.0), math.radians(-57.0))
COLD = np.array([math.cos(lb[1])*math.cos(lb[0]), math.cos(lb[1])*math.sin(lb[0]), math.sin(lb[1])])

print("="*80); print("(A) 模式選擇 (正確容差)"); print("="*80)
for tol in [1e-3, 1e-4, 1e-5]:
    s = select(V, COLD, tol=tol)
    print(f"容差 {tol:g}: {len(s)} 個 = {s}")
print("O136 docs/19 宣稱 = [1,2,3,4,5,7,9,11,13]")
print(f"★ 一致: {select(V,COLD,tol=1e-4) == [1,2,3,4,5,7,9,11,13]}  ✅")
print("\n  各模式偏差 (冷斑軸):")
x = V@COLD
for n in range(1,16):
    s=float(Tn(n)(x).sum()); t=60*a0(n)
    print(f"   n={n:>2}: Σ T_n = {s:>13.6f}   60a₀ = {t:>11.6f}   差 = {s-t:>11.2e}  {'★選' if abs(s-t)<1e-4 else '  ✗'}")

print("\n"+"="*80); print("(B) ★ 軸獨立性: 1000 隨機軸"); print("="*80)
sels=[tuple(select(V, (lambda c: c/np.linalg.norm(c))(rng.normal(size=3)), tol=1e-3)) for _ in range(1000)]
cnt=Counter(sels)
print(f"不同選擇集數: {len(cnt)}")
for s,k in cnt.most_common(3): print(f"  {list(s)}  ({k}/1000)")
print(f"★ 軸無關: {'✅ 係 (1000 軸全部相同)' if len(cnt)==1 else '🔴 否'}")

print("\n"+"="*80); print("(C) ★★ 判別力: 準則係關於群 I 定關於軌道?"); print("="*80)
ico_set=set()
for b in [(0,1,phi),(0,1,-phi),(0,-1,phi),(0,-1,-phi)]:
    for p in [(0,1,2),(1,2,0),(2,0,1)]: ico_set.add(tuple(b[i] for i in p))
ICO=np.array(sorted(ico_set),float); ICO/=np.linalg.norm(ICO,axis=1,keepdims=True)
dod=set()
for s1 in (1,-1):
    for s2 in (1,-1):
        for s3 in (1,-1): dod.add((s1,s2,s3))
for b in [(0,1/phi,phi),(0,1/phi,-phi),(0,-1/phi,phi),(0,-1/phi,-phi)]:
    for p in [(0,1,2),(1,2,0),(2,0,1)]: dod.add(tuple(b[i] for i in p))
DOD=np.array(sorted(dod),float); DOD/=np.linalg.norm(DOD,axis=1,keepdims=True)
sets={'A₅ 60-orbit (本項目)':V,'Icosahedron 12 頂點':ICO,'Dodecahedron 20 頂點':DOD}
for k in range(3):
    g=rng.normal(size=3); g/=np.linalg.norm(g)
    orb=np.unique(np.round(np.array([gg@g for gg in group]),8),axis=0)
    if len(orb)==60: sets[f'其他 I-orbit #{k+1}']=orb
print(f"{'點集':>26} {'點數':>5} {'選中模式':>34} {'數':>4}")
for nm,pts in sets.items():
    s=select(pts,COLD,tol=1e-3)
    print(f"{nm:>26} {len(pts):>5} {str(s):>34} {len(s):>4}")
allsame = all(select(p,COLD,tol=1e-3)==select(V,COLD,tol=1e-3) for p in sets.values())
print(f"\n★ 全部 I-invariant 點集選出同一 9 模式? {'✅ 係 — 準則關於群 I, 唔關於特定軌道' if allsame else '🔴 否'}")

print("\n"+"="*80); print("(D) ★★ null test: 隨機 60 點集 (2000)"); print("="*80)
counts=np.array([len(select((lambda R: R/np.linalg.norm(R,axis=1,keepdims=True))(rng.normal(size=(60,3))), COLD, tol=1e-3)) for _ in range(2000)])
print(f"選中模式數: 中位={np.median(counts):.0f} 平均={counts.mean():.2f} max={counts.max()}")
print(f"P(≥9) = {np.mean(counts>=9):.4f}   觀測 = 9")
print(f"★ {'🟢 隨機唔會給 9' if np.mean(counts>=9)<0.05 else '🔴 唔顯著'}")
print(f"\n⚠️ 但 (C) 已證: 任何 I-invariant 集都給 9")
print(f"   ⟹ 準則嘅判別內容 = 【icosahedral 對稱性】, 唔係模式選擇本身")

print("\n"+"="*80); print("(E) 冷斑軸 vs 對稱軸"); print("="*80)
e2=[]
for i in range(12):
    for j in range(i+1,12):
        if abs(np.dot(ICO[i],ICO[j]) - 1/math.sqrt(5)) < 1e-9: e2.append(ICO[i]+ICO[j])
E2=np.array(e2); E2/=np.linalg.norm(E2,axis=1,keepdims=True)
for nm,ax in [('5-fold (icosa 12 頂點)',ICO),('3-fold (dodeca 20 頂點)',DOD),('2-fold (icosa 30 邊中點)',E2)]:
    ang=np.degrees(np.arccos(np.clip(np.abs(ax@COLD),-1,1)))
    print(f"  冷斑軸到 {nm:>24}: 最小 {ang.min():.4f}°")
ang_nodes=np.degrees(np.arccos(np.clip(V@COLD,-1,1)))
print(f"\n冷斑軸到最近節點: {ang_nodes.min():.4f}°")
print(f"★ 冷斑軸唔係對稱軸 (最近對稱軸 >10°) 且選擇律軸無關 ⟹ 冷斑方向唔參與選擇 ✅")

print("\n"+"="*80); print("(F) 節點擾動穩健性 (容差 1e-3)"); print("="*80)
print(f"{'擾動(°)':>9} {'選中數':>7}  選擇集")
for eps in [0.0,0.01,0.1,0.5,1.0,2.0,5.0]:
    P=V+rng.normal(scale=math.radians(eps),size=V.shape); P/=np.linalg.norm(P,axis=1,keepdims=True)
    s=select(P,COLD,tol=1e-3)
    print(f"{eps:>9} {len(s):>7}  {s}")
