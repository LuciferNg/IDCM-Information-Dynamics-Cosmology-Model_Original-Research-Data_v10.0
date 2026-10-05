#!/usr/bin/env python3
"""
O137 — 開放問題 #1 充分性 null test (Round 3)

測試 docs/23 的三個宣稱:
  (A) "輕子模式唯一性" 係唔係有信息量? (密度測試)
  (B) C_f ← Φ 條目配對係唔係唯一? (枚舉測試)
  (C) mod-8 ∈ {1,5,7} 規則 vs O136 A₅ 集 (P=0.0155) 衝突檢查
"""
import numpy as np
from math import sin, pi
from itertools import permutations, product
import random

random.seed(20260830)
rng = np.random.default_rng(20260830)

M0 = 27.900915
def gamma_n(n): return 4*sin(n*pi/88)**2
def sqrt_gamma(n): return 2*sin(n*pi/88)

# ================= 數據 =================
# SM 電荷費米子質量 (MeV), PDG-ish (O136 docs/34 用值)
MASS = {'e':0.5110,'u':2.1600,'d':4.6700,'mu':105.6584,'s':93.40,
        'c':1270.0,'tau':1776.86,'b':4180.0,'t':172690.0}
# O137 模式分配
O137_MODE = {'e':1,'u':1,'d':1,'mu':7,'s':14,'c':34,'tau':20,'b':33}
# O136 A5 模式集
A5_MODE = {'t':1,'b':2,'tau':3,'c':4,'mu':5,'s':7,'d':9,'u':11,'e':13}

# φ=9 相交矩陣 Φ = 1 + x3_i·x3'_j
X3  = [1,5,9]              # 世代行 (1+Bk, step 4)
X3P = [0,1,3,4,6,7]        # 夥伴列
PHI = {}
for i,a in enumerate(X3):
    for j,b in enumerate(X3P):
        PHI[(i,j)] = 1 + a*b
PHI_VALS = sorted(set(PHI.values()))
print("Φ 矩陣值:", PHI_VALS)

# 除數候選 (結構: 1, 2, 4=B)
DIVS = [1,2,4]
CF_CATALOG = sorted(set(v/d for v in PHI_VALS for d in DIVS))
print(f"Φ C_f 目錄 ({len(CF_CATALOG)} 值):", CF_CATALOG)

print("\n" + "="*70)
print("(A) 密度測試: 隨機質量 → (mode, C_f) 匹配率")
print("="*70)

def count_matches(m, tol=0.01, catalog=CF_CATALOG, modes=range(1,45)):
    """數幾多個 (mode, C_f) 組合能重現質量 m (相對容差 tol)"""
    hits = []
    for Cf in catalog:
        gt = m/(M0*Cf)
        for n in modes:
            if gt > 0 and abs(gamma_n(n)-gt)/gt < tol:
                hits.append((n,Cf))
    return hits

print(f"\n{'粒子':>4} {'n':>3} {'m (MeV)':>10} {'匹配數':>7} {'C_f 反解':>9}  匹配嘅 C_f")
for p in ['e','u','d','mu','s','c','tau','b']:
    n = O137_MODE[p]; m = MASS[p]
    hits = count_matches(m)
    Cf_solve = m/(M0*gamma_n(n))
    print(f"{p:>4} {n:>3} {m:>10.4f} {len(hits):>7} {Cf_solve:>9.4f}  {sorted(set(c for _,c in hits))}")

# ★ null: 隨機質量 (log-uniform 覆蓋同一範圍)
print("\n--- null: 2000 個隨機質量 (log-uniform [0.5, 5000] MeV) ---")
nul = []
for _ in range(2000):
    m = 10**rng.uniform(np.log10(0.5), np.log10(5000))
    nul.append(len(count_matches(m)))
nul = np.array(nul)
print(f"null 匹配數: 中位={np.median(nul):.0f}  平均={nul.mean():.1f}  P(≥1)={np.mean(nul>=1):.3f}")

print("\n" + "="*70)
print("(B) 枚舉測試: C_f ← Φ 條目配對唯一性")
print("="*70)

LEP = ['e','mu','tau']
PHI_ENTRIES = list(PHI.items())  # 18 條目

# B1: 無世代約束 — 所有 (entry, divisor) 配對任選
CF_FULL = [(k, v/d) for k, v in PHI.items() for d in DIVS]
print(f"\n候選 (entry, C_f) 組合: {len(CF_FULL)}")

def count_valid_assignments(tol=0.01, gen_constraint=False):
    """數幾多個 (e,μ,τ) → (entry, Cf) 指派能令 3 個質量全閉合"""
    valid = 0
    total = 0
    for trio in permutations(CF_FULL, 3):
        # gen 約束: e→row0, μ→row1, τ→row2
        if gen_constraint:
            rows = [t[0][0] for t in trio]
            if rows != [0,1,2]:
                continue
        total += 1
        ok = True
        for p,(k,Cf) in zip(LEP, trio):
            # 用最佳 mode
            gt = MASS[p]/(M0*Cf)
            best = min(range(1,45), key=lambda n: abs(gamma_n(n)-gt))
            if abs(gamma_n(best)-gt)/gt > tol:
                ok = False; break
        if ok: valid += 1
    return valid, total

v,t = count_valid_assignments(tol=0.01, gen_constraint=False)
print(f"無世代約束, tol=1%:  {v} / {t} 個指派有效  ({100*v/t:.3f}%)")

v2_,t2_ = count_valid_assignments(tol=0.01, gen_constraint=True)
print(f"有世代約束 (e→r0,μ→r1,τ→r2), tol=1%:  {v2_} / {t2_}  ({100*v2_/t2_:.3f}%)")

v3,t3 = count_valid_assignments(tol=0.002, gen_constraint=True)
print(f"有世代約束, tol=0.2%:  {v3} / {t3}  ({100*v3/t3:.3f}%)")

# B2: 用 [5][6]/2 同 [9][4] 嘅實際指派
actual = [((1,3), 31/2), ((2,3), 37)]   # μ: row1(x3=5), x3'=3? ; τ: row2(x3=9), x3'=3
print(f"\n★ 文檔宣稱: C_μ = Φ[5][6]/2 = {31/2}, C_τ = Φ[9][4] = {37}")
print(f"   Φ[(1,3)] = 1+5*4 = {PHI[(1,3)]}, /2 = {PHI[(1,3)]/2}")
print(f"   Φ[(2,3)] = 1+9*4 = {PHI[(2,3)]}")
print(f"   Φ[(1,4)] = 1+5*6 = {PHI[(1,4)]}  (docs 用 [5][6] 命名)")
print(f"   Φ[(2,3)] = {PHI[(2,3)]}  (docs 用 [9][4] 命名)")

print("\n" + "="*70)
print("(C) mod-8 規則 vs A₅ 集衝突檢查")
print("="*70)

def odd_part(n):
    while n%2==0: n//=2
    return n

print(f"\nA₅ 模式集 (O136, P=0.0155): {sorted(A5_MODE.values())}")
print(f"{'n':>3} {'odd part':>9} {'mod 8':>6} {'docs/23 規則':>14}")
viol = []
for n in sorted(set(A5_MODE.values())):
    op = odd_part(n); r = op%8
    ok = r in [1,5,7]
    if not ok: viol.append(n)
    print(f"{n:>3} {op:>9} {r:>6} {'✅ 合格' if ok else '🔴 排除':>14}")
print(f"\n🔴 A₅ 集被 docs/23 mod-8 規則排除嘅模式: {viol}")
print(f"   ⟹ {'直接衝突!' if viol else '無衝突'}")

print(f"\nO137 模式集: {sorted(set(O137_MODE.values()))}")
for n in sorted(set(O137_MODE.values())):
    op = odd_part(n); r = op%8
    print(f"{n:>3} {op:>9} {r:>6} {'✅' if r in [1,5,7] else '🔴'}")

print("\n" + "="*70)
print("(D) γ-譜密度: '唯一模式' 係唔係必然?")
print("="*70)
for n in [1,7,20,14,33,34]:
    g = gamma_n(n)
    # 最近鄰距離
    nb = min(abs(gamma_n(k)-g) for k in range(1,45) if k!=n)
    print(f"n={n:>2}: γ={g:.6f}  最近鄰距={nb:.6f}  1% 窗口={0.01*g:.6f}  "
          f"{'唯一 (必然)' if 0.01*g < nb else '可能歧義'}")
print("\n★ 結論: 1% 容差 ≪ γ 譜間距 ⟹ 任何質量嘅模式都【必然唯一】")
print("   ⟹ docs/23 '唯一性' 宣稱【零信息量】(trivially true)")
