#!/usr/bin/env python3
"""
O137 — 決定性測試: A₅ 9 模式 × 粒子配對, 能否令 C_f 全部來自 Φ 幾何?
若可以 ⟹ 兩框架可統一 (標度律問題有解) ⟹ 有研究價值
若不可以 ⟹ 標度律只係參數化失敗 ⟹ 無研究價值
"""
import numpy as np
from math import sin, pi
from itertools import permutations

M0 = 27.900915
def gamma_n(n): return 4*sin(n*pi/88)**2
MASS = {'e':0.5110,'u':2.1600,'d':4.6700,'s':93.40,'mu':105.6584,
        'c':1270.0,'tau':1776.86,'b':4180.0,'t':172690.0}
A5 = [1,2,3,4,5,7,9,11,13]
blocks = {1:[0,1,2], 2:[3,4,5], 3:[6,7,8]}   # A₅ index blocks
gen_of = {'e':1,'u':1,'d':1,'s':2,'mu':2,'c':2,'tau':3,'b':3,'t':3}
gparts = {1:['e','u','d'], 2:['s','mu','c'], 3:['tau','b','t']}

PHI = {}
for i,a in enumerate([1,5,9]):
    for j,b in enumerate([0,1,3,4,6,7]): PHI[(i,j)] = 1+a*b
CAT = sorted(set(v/d for v in PHI.values() for d in [1,2,4]))
print(f"Φ C_f 目錄 ({len(CAT)} 值): {CAT}")

def hits_for(n, p, tol=0.01):
    Cf = MASS[p]/(M0*gamma_n(n))
    return [c for c in CAT if abs(c-Cf)/Cf < tol]

print("\n" + "="*78)
print("(A) 全部 216 個世代內配對 (3!×3!×3!): 命中 Φ 目錄嘅 C_f 數")
print("="*78)
best = []
for perm1 in permutations(blocks[1]):
    for perm2 in permutations(blocks[2]):
        for perm3 in permutations(blocks[3]):
            perms = {1:perm1, 2:perm2, 3:perm3}
            tot = 0; detail = {}
            for g in [1,2,3]:
                for pi_, ai in zip(gparts[g], perms[g]):
                    n = A5[ai]
                    h = hits_for(n, pi_)
                    detail[pi_] = (n, MASS[pi_]/(M0*gamma_n(n)), h)
                    if h: tot += 1
            best.append((tot, detail))
best.sort(key=lambda t: -t[0])
print(f"\n最佳配對命中數: {best[0][0]}/9")
print(f"{'粒子':>5} {'n':>3} {'C_f':>10}  命中嘅 Φ 值")
for p in ['e','u','d','s','mu','c','tau','b','t']:
    n, Cf, h = best[0][1][p]
    print(f"{p:>5} {n:>3} {Cf:>10.4f}  {h if h else '❌ 無'}")

# 全部配對嘅命中數分佈
from collections import Counter
dist = Counter(t for t,_ in best)
print(f"\n命中數分佈: {dict(sorted(dist.items()))}")
print(f"最佳 = {best[0][0]}/9,  中位 = {sorted(t for t,_ in best)[len(best)//2]}/9")

print("\n" + "="*78)
print("(B) null test: 隨機質量指派 → 命中數分佈 (N=20000)")
print("="*78)
rng = np.random.default_rng(20260830)
allp = ['e','u','d','s','mu','c','tau','b','t']
mvals = np.array([MASS[p] for p in allp])
N = 20000; nulld = []
for _ in range(N):
    shuffled = rng.permutation(mvals)
    tot = 0
    for g in [1,2,3]:
        idxs = blocks[g]
        for k, pi_ in enumerate(gparts[g]):
            n = A5[idxs[k]]
            Cf = shuffled[allp.index(pi_)]/(M0*gamma_n(n))
            if any(abs(c-Cf)/Cf < 0.01 for c in CAT): tot += 1
    nulld.append(tot)
nulld = np.array(nulld)
obs = best[0][0]
pval = float(np.mean(nulld >= obs))
print(f"null 命中數: 中位={np.median(nulld):.0f}  平均={nulld.mean():.2f}  max={nulld.max()}")
print(f"觀測最佳 = {obs}/9  ⟹ P(≥觀測) = {pval:.4f}  "
      f"{'🟢 顯著' if pval<0.05 else '🔴 唔顯著 (密度效應可解釋)'}")

print("\n" + "="*78)
print("(C) 對照: O54 模式集嘅命中數")
print("="*78)
O54 = {'e':1,'u':1,'d':1,'mu':7,'s':14,'c':34,'tau':20,'b':33,'t':None}
tot = 0
for p,n in O54.items():
    if n is None:
        print(f"{p:>5}  (Higgs VEV, 無模式)"); continue
    Cf = MASS[p]/(M0*gamma_n(n)); h = hits_for(n,p)
    tot += bool(h)
    print(f"{p:>5} n={n:<3} C_f={Cf:>10.4f}  {h if h else '❌'}")
print(f"\nO54 命中 = {tot}/8")
print(f"⟹ A₅ 最佳 {obs}/9 vs O54 {tot}/8 — "
      f"{'A₅ 勝' if obs>tot else ('O54 勝' if tot>obs else '平手')}")

print("\n" + "="*78)
print("(D) 判定")
print("="*78)
print(f"""
標度律問題可否歸約為配對問題?
  A₅ 最佳配對命中 {obs}/9, null P = {pval:.4f}
  ⟹ {'✅ 配對有結構信號 — 值得追' if pval<0.05 else '🔴 配對無結構信號 — 密度效應主導'}
""")
