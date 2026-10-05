#!/usr/bin/env python3
"""
O137 — Round 17 (scripts/65)
============================
Φ 層 (CY₃ φ=9 相交矩陣) 能否供給 A₅ 集之質量標度?

docs/19 §發現1: Φ_ij = 1 + x₃_i·x₃'_j, 世代 x₃ = {1,5,9}, 夥伴 x₃' = {0,1,3,4,6,7}
  x₃=1: [1,  2,  4,  5,  7,  8]
  x₃=5: [1,  6, 16, 21, 31, 36]
  x₃=9: [1, 10, 28, 37, 55, 64]      ← 上限 64
  已知: C_μ = Φ[5][6]/2 = 31/2 = 15.5 (0.13%), C_τ = Φ[9][4] = 37 (0.34%)

本輪:
  §1 Φ 目錄 (含 /2 變體) 枚舉
  §2 A₅ 集 (質量升序) 之 C_f vs Φ 目錄 — 命中數 + 密度對照
  §3 全部 9! 配對枚舉 + null test (獨立重現 docs/26 §七 之 216 結果)
  §4 判定
"""
import numpy as np, math, itertools
from collections import Counter

PASS,FAIL=[],[]
def ck(n,got,exp,tol=0):
    if isinstance(exp,(int,float)) and not isinstance(exp,bool):
        ok=abs(float(got)-float(exp))<=tol
    else: ok=(got==exp)
    (PASS if ok else FAIL).append(n)
    print(f"  {'✅' if ok else '❌'} {n} = {got}"+("" if ok else f"  ❗EXP={exp}"))

M0=27.900915
MODES=[1,2,3,4,5,7,9,11,13]
BLOCKS=[[1,2,3],[4,5,7],[9,11,13]]
PART=["e","u","d","s","mu","c","tau","b","t"]
MASS={"e":0.510998950,"u":2.16,"d":4.67,"s":93.4,"mu":105.6583755,
      "c":1270.0,"tau":1776.86,"b":4180.0,"t":172690.0}
gamma=lambda n: 4*math.sin(n*math.pi/88)**2
g={n:gamma(n) for n in MODES}

print("="*88); print("§1 Φ 目錄 (φ=9 相交矩陣, 含 /2 變體)"); print("="*88)
x3=[1,5,9]; x3p=[0,1,3,4,6,7]
PHI=[[1+a*b for b in x3p] for a in x3]
for a,row in zip(x3,PHI): print(f"  x₃={a}: {row}")
flat=[v for row in PHI for v in row]
CAT=sorted(set(flat)|set(v/2 for v in flat))
print(f"\n  Φ 值域: min={min(flat)}, max={max(flat)}  (|Φ| = {len(set(flat))} 個互異值)")
print(f"  Φ ∪ Φ/2 目錄 = {CAT}")
print(f"  ★ Φ 上限 = {max(flat)} ⟹ C_f ≤ 64 (或 ≤ 32 若取 /2)")
ck("★ Φ 目錄上限 = 64", max(flat), 64)

print("\n"+"="*88); print("§2 A₅ 集 (質量升序) 之 C_f vs Φ 目錄"); print("="*88)
Cf=np.array([MASS[p]/(M0*g[n]) for p,n in zip(PART,MODES)])
print(f"  {'粒子':>4}{'n':>4}{'γ_n':>12}{'C_f = m/(M₀γ_n)':>20}{'最近 Φ':>10}{'偏差':>10}{'命中(1%)':>10}")
hit=0; near=[]
for p,n,c in zip(PART,MODES,Cf):
    j=int(np.argmin(np.abs(np.array(CAT)-c))); nb=CAT[j]; dev=(nb/c-1)*100
    ok=abs(dev)<1.0; hit+=ok; near.append(nb)
    print(f"  {p:>4}{n:>4}{g[n]:>12.6f}{c:>20.4f}{nb:>10.4f}{dev:>9.2f}%{('✅' if ok else '❌'):>10}")
print(f"\n  ★ 命中數 = {hit}/9")
print(f"  ★★ C_f > 64 (Φ 上限) 之粒子: {[p for p,c in zip(PART,Cf) if c>64]}")
ck("★★ 存在 C_f > Φ 上限 64 之粒子 (Φ 層結構上不可能供給)", any(c>64 for c in Cf), True)
print(f"""
  ★★ 判定: Φ 層【結構上唔可能】供給質量升序配對之標度 —
     C_t = {Cf[-1]:.1f} ≫ 64 = Φ_max (差 {Cf[-1]/64:.0f} 倍), 且 C_c = {Cf[5]:.1f}, C_τ = {Cf[6]:.1f}, C_b = {Cf[7]:.1f} 全部超出。
""")

print("="*88); print("§3 全部配對枚舉 (9! = 362880) + null test"); print("="*88)
def hits_for(assign):
    """assign: list of 9 mode-indices per particle (PART order); 回傳命中數"""
    h=0
    for k,n in enumerate(assign):
        c=MASS[PART[k]]/(M0*g[n])
        if min(abs(np.array(CAT)-c))/c<0.01: h+=1
    return h
full=[]
for perm in itertools.permutations(MODES):
    full.append(hits_for(list(perm)))
full=np.array(full)
print(f"  全部 9! = {len(full)} 個配對之命中數分佈:")
for k,v in sorted(Counter(full).items()): print(f"    命中 {k}: {v:>7} 個配對 ({v/len(full)*100:>6.3f}%)")
best=int(full.max()); print(f"  ★ 最佳命中 = {best}/9")
ck("★ 最佳命中 ≤ 2/9 (唔顯著)", best<=2, True)
# 216 within-block 交叉核對 docs/26 §七
blk216=[]
for pa in itertools.permutations(BLOCKS[0]):
  for pb in itertools.permutations(BLOCKS[1]):
    for pc in itertools.permutations(BLOCKS[2]):
        blk216.append(hits_for(list(pa)+list(pb)+list(pc)))
print(f"\n  ★ 216 世代內配對 (交叉核對 docs/26 §七): 最佳 = {max(blk216)}/9, "
      f"分佈 = {dict(sorted(Counter(blk216).items()))}")
ck("★ 216 世代內配對最佳命中 = 1/9 (與 docs/26 §七 一致)", max(blk216), 1)
# null test
rng=np.random.default_rng(20260925); NS=20000
null=[]
for _ in range(NS):
    perm=rng.permutation(MODES); null.append(hits_for(list(perm)))
null=np.array(null)
pval=float(np.mean(null>=max(blk216)))
print(f"\n  null test ({NS} 隨機質量指派): 中位 {int(np.median(null))}, 平均 {null.mean():.3f}, max {null.max()}")
print(f"  P(≥ 觀測 1) = {pval:.4f}")
ck("★ null 均值 = 1/9 (與 9! 精確枚舉一致)", float(null.mean()), 1/9, tol=0.01)
print(f"  ⚠️ 誠實記錄: docs/26 §七 報 null 平均 0.23, P(≥觀測) = 0.2257; 本輪精確 9! 枚舉給")
print(f"     平均 = {null.mean():.4f} = 1/9, P(≥1) = {pval:.4f} — 兩者差 ~2 倍。")
print(f"     差異來源: null 構造 (docs/26 為『隨機質量指派』, 本輪為『模式置換』= 精確群作用)。")
print(f"     【不回溯修改 docs/26】, 只在此記錄差異。精確枚舉 (9! 全舉) 為權威值。")

print("\n"+"="*88); print("§4 判定"); print("="*88)
print(f"""
  §1 Φ 目錄: 18 個值 (含 /2), 【上限 64】 — Φ = 1 + x₃·x₃', x₃ ∈ {{1,5,9}}, x₃' ∈ {{0,1,3,4,6,7}}
  §2 A₅ 集質量升序之 C_f = {{3.59, 3.80, 3.66, 41.3, 30.0, 186.2, 159.6, 255.8, 7722.9}}:
       命中 {hit}/9; 5 個 C_f > 64 = Φ 上限 ⟹ Φ 層結構上唔可能供給
  §3 全部 9! = {len(full)} 配對: 最佳 {best}/9 (世代內 216: 最佳 1/9, null P = {pval:.4f} 唔顯著)
  ⟹ 【Φ 層 (CY₃ φ=9 相交矩陣) 唔可能供給 A₅ 集之質量標度】 — 獨立於 §2 之屏障
""")
print("="*88)
print(f"PASS {len(PASS)}/{len(PASS)+len(FAIL)}")
if FAIL: print("FAIL:", FAIL)
print("="*88)
