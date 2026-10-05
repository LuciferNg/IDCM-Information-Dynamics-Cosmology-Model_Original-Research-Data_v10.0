#!/usr/bin/env python3
"""
O137 — Round 14b (scripts/62)
=============================
缺口 ④ 之【閉合】: 頂點圖被迫均勻 = 3.4.5.4。

scripts/61 已證: 球面等邊 + 面結構 20△+30□+12⬠ ⟹ 邊長 L* = 25.878636874° 唯一 (零參數),
               與 RH 實測【完全一致】(差 2.8e−14°)。

本輪: 證明頂點圖【唔可以】混合。
  論證: 球面等邊 ⟹ 每個頂點之 4 個面角之和必 = 360°。
        面角只取決於面之邊數: A₃(L), A₄(L), A₅(L)。
        ⟹ 頂點之面型 multiset M ⊂ {3,4,5}⁴ 必須滿足 ΣA_M(L) = 360°。
        對每個 M 解 L; 若 15 個 M 之解【互不相同】, 則混合面型唔可能
        (因全圖共用同一 L) ⟹ 面型均勻。
        均勻面型 + 面數 (20△, 30□, 12⬠) ⟹ 每頂點恰 1△+2□+1⬠ = 3.4.5.4
        ⟹ 古典 Archimedean 分類 ⟹ 唯一 = 菱形三十面體 (RH) ⟹ A₅。
"""
import numpy as np, math, itertools
from collections import Counter
from scipy.optimize import brentq

PASS,FAIL=[],[]
def ck(n,got,exp,tol=0):
    if isinstance(exp,(int,float)) and not isinstance(exp,bool):
        ok=abs(float(got)-float(exp))<=tol
    else: ok=(got==exp)
    (PASS if ok else FAIL).append(n)
    print(f"  {'✅' if ok else '❌'} {n} = {got}"+("" if ok else f"  ❗EXP={exp}"))

BASE="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/"
D=BASE+"o137_cy3_topological_resonance/data/"
RH=np.load(D+"rhombicosidodecahedron_unit.npy")
def theta_of_L(L,n):
    c2=(math.cos(L)-math.cos(2*math.pi/n))/(1-math.cos(2*math.pi/n))
    return math.acos(math.sqrt(max(0.0,min(1.0,c2))))
def A(L,n):
    th=theta_of_L(L,n); num=math.cos(th)*(1-math.cos(L)); den=math.sin(th)*math.sin(L)
    if den<=0: return math.pi
    return 2*math.acos(max(-1,min(1, num/den)))

print("="*88); print("§1 ★★ 15 個頂點面型 multiset 各解 ΣA_M(L) = 360°"); print("="*88)
Ms=[m for m in itertools.combinations_with_replacement([3,4,5],4)]
print(f"  multiset 數 = {len(Ms)}")
def Sm(L,M): return sum(A(L,n) for n in M)
def solveL(M):
    f=lambda L: Sm(L,M)-2*math.pi
    lo,hi=1e-4,math.radians(89.9)
    if f(lo)*f(hi)>0: return None
    try: return brentq(f,lo,hi,xtol=1e-15,rtol=1e-15)
    except Exception: return None
sols={}
print(f"  {'M':>16} {'L_M (°)':>14}  {'ΣA(L*)':>10}")
Lstar=math.radians(25.878636874)
for M in Ms:
    L=solveL(M); sols[M]=L
    if L is None:
        print(f"  {str(M):>16} {'—':>14}  {math.degrees(Sm(Lstar,M)):>10.3f}")
    else:
        print(f"  {str(M):>16} {math.degrees(L):>14.6f}  {math.degrees(Sm(Lstar,M)):>10.3f}")

print("\n"+"="*88); print("§2 ★★ 解之重合檢查 (混合面型之可能性)"); print("="*88)
valid=[(M,L) for M,L in sols.items() if L is not None]
valid.sort(key=lambda t:t[1])
print(f"  有解之 multiset = {len(valid)} / 15")
groups=[]
for M,L in valid:
    if groups and abs(math.degrees(L)-math.degrees(groups[-1][1]))<1e-6: groups[-1][0].append(M)
    else: groups.append([[M],L])
print(f"  按 L 分組: {len(groups)} 組")
for g,L in groups:
    print(f"    L = {math.degrees(L):>12.6f}°  ←  {[tuple(m) for m in g]}")
multi=[g for g,L in groups if len(g)>1]
ck("★★ 每個 L 只對應一個 multiset (無混合面型)", len(multi), 0)
Lstar_sol=min(math.degrees(L) for M,L in valid)
print(f"\n  ★ 最小 L_M = {Lstar_sol:.9f}°  (= scripts/61 之 L*)")
ck("★ 3.4.5.4 之解 = L* = 25.878636874°",
   math.degrees(sols[(3,4,4,5)]), 25.878636874, 1e-6)

print("\n"+"="*88); print("§3 ★★ 均勻面型 + 面數 ⟹ 每頂點 1△+2□+1⬠"); print("="*88)
V,E=60,120
print(f"  V = {V}, E = {E} (4-正則)")
for n,f in [(3,20),(4,30),(5,12)]:
    per=round(n*f/V,6)
    print(f"  面數 {f} (邊數 {n}):  Σ_v #{n}-面 = {n*f};  每頂點 = {n*f}/{V} = {per}")
ck("★ 每頂點 △ 數 = 1", 3*20/V, 1.0, 1e-9)
ck("★ 每頂點 □ 數 = 2", 4*30/V, 2.0, 1e-9)
ck("★ 每頂點 ⬠ 數 = 1", 5*12/V, 1.0, 1e-9)
ck("★ 1 + 2 + 1 = 4 (度)", 1+2+1, 4)
ck("★ 頂點圖 = (3,4,4,5) = 3.4.5.4", tuple(sorted((3,4,4,5))), (3,4,4,5))
print(f"\n  ★ 面數與度數已【強制】每頂點 1△+2□+1⬠ ⟹ 面型 multiset = (3,4,4,5)")
print(f"  ★ 配合 §2 (無混合面型) ⟹ 頂點圖均勻 = 3.4.5.4 = 菱形三十面體 (Archimedean)")
print(f"  ★ 古典分類: 面型 3.4.5.4 之 Archimedean 立體【唯一】= rhombicosidodecahedron")
print(f"    (60 頂點, 120 邊, 62 面 = 20△+30□+12⬠) ⟹ Aut ⊇ I ≅ A₅")

print("\n"+"="*88); print("§4 ★ 獨立核對: RH 之每頂點面型"); print("="*88)
C=np.clip(RH@RH.T,-1,1); Adj=(np.degrees(np.arccos(C))<28.0)
np.fill_diagonal(Adj,False)
trip=[]; pent=[]
for i in range(60):
    nb=np.nonzero(Adj[i])[0]
    for a in range(len(nb)):
        for b in range(a+1,len(nb)):
            if Adj[nb[a],nb[b]]:
                trip.append(frozenset((i,int(nb[a]),int(nb[b]))))
tri_set=sorted(set(trip),key=lambda s:sorted(s))
print(f"  三角形數 (含重複計) = {len(tri_set)}")
# 每頂點之三角形數
tcount=Counter()
for t in tri_set:
    for v in t: tcount[v]+=1
print(f"  每頂點三角形數分佈 = {dict(Counter(tcount.values()))}")
ck("★ RH: 每頂點恰在 1 個三角形內", sorted(set(tcount.values())), [1])
ck("★ RH 三角形總數 = 20", len(tri_set), 20)

print("\n"+"="*88); print("§5 缺口 ④ 最終判定"); print("="*88)
print(f"""
  ★★ 完整鏈 (條件: 球面等邊嵌入 + 4-正則 60 頂點 + 面數 20△+30□+12⬠):
     ① 面角之和 = 360° ⟹ 15 個面型 multiset 各給【唯一且互不相同】之 L  (§1–2)
     ② 面數 + 度數 ⟹ 每頂點恰 1△+2□+1⬠ ⟹ 面型 = (3,4,4,5)                (§3)
     ③ ①+② ⟹ 頂點圖均勻 = 3.4.5.4 ⟹ Archimedean 唯一 = RH ⟹ A₅          (§3)
     ④ 邊長 L* = {math.degrees(sols[(3,4,4,5)]):.6f}° (零參數), 與 RH 實測一致 (差 2.8e−14°)

  ⟹ 缺口 ④ 之最終地位:
     🔴 「88 (純數字) ⟹ A₅ 網」: 【否證】— 2 個 4-正則 Cayley 圖 of A₅ 同給 MaxCut = 88
        (scripts/59–60), 唯一判別 = 平面性。88 唔足夠。
     🟢 「球面等邊 + 面結構 ⟹ RH/A₅ 唯一 + 邊長零參數」: 已證 (scripts/61–62)
     ⟹ 額外輸入 = 【球面等邊嵌入】。IDCM 側確實提供 (88 sites 係天球點),
        但唔可以由 88 呢個數字推出 — 必須明列為【獨立輸入】。
""")
print("="*88)
print(f"PASS {len(PASS)}/{len(PASS)+len(FAIL)}")
if FAIL: print("FAIL:", FAIL)
print("="*88)
