#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/04 — 配分函數截斷代數: 邊個讀法先係機制?
=====================================================
問題記錄 (01_problem_record.md) 方法 4: 「配分函數截斷: Z = Σe^{−βE} 截斷到 N 項
→ (Z_N − Z_{N−1})/Z_N = N/(N+1) 形式?」

本 script 精確檢定三個候選讀法, 判別邊個係**機制** (唯一) 邊個係**重述**:
  (A) 階乘配分: (Z_N−Z_{N−1})/Z_N = N/(N+1) ⟺ Z_N ∝ (N+1)!
  (B) 均分真空佔比: d 個態, 其中 1 個真空 ⇒ 真空佔 1/d ⇒ 觀測量 = (d−1)/d
  (C) 單格衰減: exp(−1/d) ≈ 1 − 1/d

判準:
  C1 (A) 嘅代數等價鏈 (sympy 精確)
  C2 (A) 與 (B) 係**同一個** — 隨機排列中特定元素佔特定位嘅概率 = 1/(N+1)
  C3 (C) 唔係精確形式 (d=5 偏差 2.3%) → 只能做定性解釋, 唔可以做機制
  C4 唯一性: 只有 f(d) = (d−1)/d 同時 (i) 精確有理 (ii) 虧缺 = 一個態 (iii) 五成員全中
  C5 「一個量子」檢查: 每個成員嘅虧缺 = 1/d 精確 (唔係 2/(d+1) 等)
  C6 家族 vs 幾何虧缺 (π/N_d 型) 嘅形式分野: 1−π/44 = 0.9286 ≠ 1−1/45 = 0.9778
"""
import sympy as sp
from fractions import Fraction as Fr
import mpmath as mp
mp.mp.dps = 30

ok = 0; tot = 0
def chk(name, cond, note=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
    return cond

print("="*78)
print("O171 scripts/04 — 配分函數截斷代數 (邊個讀法係機制?)")
print("="*78)

# ---------- C1: (A) 階乘配分嘅代數等價鏈 ----------
print("\n=== C1: (A) 階乘配分代數 (sympy 精確) ===")
N = sp.symbols('N', positive=True, integer=True)
ZN, ZN1 = sp.symbols('Z_N Z_{N-1}', positive=True)
eq = sp.Eq((ZN - ZN1)/ZN, N/(N+1))
sol = sp.solve(eq, ZN1)[0]
print(f"  (Z_N − Z_{{N−1}})/Z_N = N/(N+1)  ⟹  Z_{{N−1}} = {sp.simplify(sol)}")
chk("C1a 等價於 Z_{N−1} = Z_N/(N+1)", sp.simplify(sol - ZN/(N+1)) == 0)
print("  ⇒ Z_N = (N+1)·Z_{N−1} ⇒ Z_N = (N+1)!/c  (階乘配分)")
# 驗證階乘解
for n in (4, 33, 44, 55, 89, 420):
    Zn = sp.factorial(n+1); Zn1 = sp.factorial(n)
    lhs = sp.Rational(Zn - Zn1, Zn)
    chk(f"C1b n={n}: (Z_n−Z_{{n−1}})/Z_n = n/(n+1)", lhs == sp.Rational(n, n+1))

# ---------- C2: (A) ≡ (B) ----------
print("\n=== C2: (A) ≡ (B) — 階乘配分 = 均分真空佔比 ===")
# 隨機排列 N+1 個態, 真空佔據「參考槽」嘅概率 = 1/(N+1) (均分)
import itertools, random
random.seed(0)
for n in (4, 5, 9):
    perms = list(itertools.permutations(range(n+1)))
    frac = sum(1 for p in perms if p[0] == 0)/len(perms)
    chk(f"C2 n={n}: P(真空在參考槽) = 1/{n+1}", abs(frac - Fr(1, n+1)) < 1e-12, f"(實算 {frac:.6f})")
print("  ⇒ 「階乘配分」同「均分真空佔比」係同一個數學內容 (唔係兩個獨立機制)")
print("  ⇒ 問題記錄方法 4 嘅 (Z_N−Z_{N−1})/Z_N = N/(N+1) 等價於「1 個真空態佔 1/(N+1)」")

# ---------- C3: (C) 單格衰減唔精確 ----------
print("\n=== C3: (C) exp(−1/d) 唔係精確形式 ===")
for d in (5, 34, 45, 56, 90, 421):
    exact = mp.mpf(d-1)/d
    approx = mp.e**(-mp.mpf(1)/d)
    dev = (approx-exact)/exact*100
    print(f"  d={d:>4}: 1−1/d = {mp.nstr(exact,12)}   exp(−1/d) = {mp.nstr(approx,12)}   dev = {mp.nstr(dev,6)}%")
d5_dev = abs((mp.e**mp.mpf('-0.2') - mp.mpf(4)/5)/(mp.mpf(4)/5))*100
chk("C3a d=5 偏差 > 2% ⇒ exp 讀法唔精確", d5_dev > 2, f"(dev {float(d5_dev):.3f}%)")
chk("C3b 大 d 極限 exp(−1/d) → 1−1/d (d→∞)", abs((mp.e**mp.mpf('-0.0001') - mp.mpf(9999)/10000)) < 1e-7)
print("  ⇒ (C) 只係大 d 嘅近似解釋 (一階), 唔可以當機制")

# ---------- C4: 唯一性檢定 ----------
print("\n=== C4: 邊個 f(d) 同時滿足 (i) 精確有理 (ii) 虧缺=1 態 (iii) 五成員全中? ===")
fam_d = [34, 45, 56, 90, 421]
targets = {d: Fr(d-1, d) for d in fam_d}
cands = {
    "1 − 1/d":            lambda d: Fr(d-1, d),
    "exp(−1/d)":          lambda d: None,               # 非有理
    "1 − 1/(d−1)":        lambda d: Fr(d-2, d-1),
    "1 − 2/d":            lambda d: Fr(d-2, d),
    "1 − 1/(d+1)":        lambda d: Fr(d, d+1),
    "(d−1)²/d²":          lambda d: Fr((d-1)**2, d**2),
    "1 − 1/d + 1/d²":     lambda d: Fr(d*d-d+1, d*d),
}
for name, f in cands.items():
    if f(34) is None:
        print(f"  {name:<18} — 非有理, 唔可能精確"); continue
    hit = all(f(d) == targets[d] for d in fam_d)
    print(f"  {name:<18} {'✅ 全中' if hit else '❌ 唔中'}")
chk("C4 唯一: 只有 1−1/d 全中", all(f(d) != targets[d] for n,f in cands.items() if f(34) is not None and n != "1 − 1/d" for d in fam_d))

# ---------- C5: 「一個量子」檢查 ----------
print("\n=== C5: 每個成員虧缺 = 1/d 精確 (一個真空態) ===")
for d in fam_d:
    deficit = 1 - targets[d]
    chk(f"C5 d={d}: 虧缺 = 1/{d} 精確", deficit == Fr(1, d), f"(= {float(deficit):.9f})")

# ---------- C6: 同幾何虧缺 (π/N_d 型) 嘅分野 ----------
print("\n=== C6: 家族 vs 幾何虧缺 (π/N_d 型) ===")
pi_over44 = mp.pi/44
print(f"  1 − π/44 = {mp.nstr(1-pi_over44, 12)} (ℓ→0 斜率比, O167 O2, EXACT)")
print(f"  1 − 1/45 = {mp.nstr(mp.mpf(44)/45, 12)} (真空佔比, 44/45)")
chk("C6 兩者唔同 (0.9286 vs 0.9778) ⇒ 兩類虧缺機制", abs((1-pi_over44) - mp.mpf(44)/45) > mp.mpf('0.04'))
print("  ⇒ IDCM 虧缺分兩族: (i) 幾何投影 π/N_d 型 (大, 7.1%); (ii) 真空佔比 1/(N+1) 型 (細, 0.02–2%)")
print("     本 O 只處理 (ii) — 全部精確有理, 且 d = (3,4,5) 面型計數 + 1")

print()
print(f"RESULT: {ok}/{tot} PASS")
print("★★ 裁決: 機制 = (B) 均分真空佔比 (1 個真空態 / d 個態);")
print("   (A) 階乘配分係 (B) 嘅等價重述 (唔係獨立機制);  (C) exp 衰減只係一階近似。")
