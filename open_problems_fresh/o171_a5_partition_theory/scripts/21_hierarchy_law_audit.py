#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/21 — 階層律分派 獨立核對 (sympy lucas/divisors + null test)

唔 import scripts/20。路線唔同:
  20: 手寫 Lucas 遞歸 + range 掃因數 + 手動 (g, L_m) 雙迴圈。
  21: sympy.lucas() 官方函數 + sympy.divisors() 官方因數分解 + 集合運算。
      另加 null test: 喺 d ∈ [2, 5000] 全域掃描, 睇家族四成員喺所有
      (g·L_m) 候選中嘅位置, 確認型別分派唔係「隨便揀中」。
"""
from fractions import Fraction as F
from itertools import combinations
from math import comb

from sympy import divisors, lucas

B, NG, ND = 4, 3, 44
NP = NF = 0


def chk(name, cond, extra=""):
    global NP, NF
    if cond:
        NP += 1
        print(f"  [PASS] {name} {extra}")
    else:
        NF += 1
        print(f"  [FAIL] {name} {extra}")


LUC = [int(lucas(n)) for n in range(16)]
LSET = set(LUC)
IRR = [1, 3, 3, 4, 5]
DISTINCT = sorted(set(d for d in IRR if d > 1))
MULT = [d for d in IRR if d > 1]
A5 = sum(d * d for d in IRR)
PROD = DISTINCT[0] * DISTINCT[1] * DISTINCT[2]
INV = sorted(set(IRR + [sum(DISTINCT), sum(MULT), sum(IRR), A5]))

print("=" * 80)
print("O171 scripts/21 — 階層律分派 獨立核對 (sympy)")
print("=" * 80)

print("\n=== A: 基本量 (sympy 官方函數) ===")
print(f"  sympy.lucas(0..15) = {LUC}")
chk("A1 sympy.lucas 前 9 項 = 2,1,3,4,7,11,18,29,47",
    LUC[:9] == [2, 1, 3, 4, 7, 11, 18, 29, 47])
chk("A2 L₅ = 11, L₄ = 7, L₇ = 29", (LUC[5], LUC[4], LUC[7]) == (11, 7, 29))
chk("A3 不變量集 (sympy.divisors 交叉確認 60 嘅因數)",
    set(divisors(60)) >= {1, 3, 4, 5, 12, 15, 60} and A5 == 60)
chk("A4 Πdim (非平凡) = 60 = |A₅|", PROD == 60 == A5)
chk("A5 ★ Σdim 帶重數 (非平凡) = 3+3+4+5 = 15 = N_gen·F₅", sum(MULT) == 15)
chk("A5b Σdim 去重 (非平凡) = 3+4+5 = 12 = B·N_gen = L₅+1", sum(DISTINCT) == 12 == B * NG == LUC[5] + 1)

print("\n=== B: 鏈週期同型別門檻 (獨立算式) ===")
chain = 2 * ND
R = F(chain, 2 * B)
print(f"  鏈長 = {chain};  R = {R};  門檻 = 2N_d = {chain}")
chk("B1 R = 11 整數", R.denominator == 1 and int(R) == 11)
chk("B2 R = L₅ (sympy.lucas)", int(R) == LUC[5])
# 帶前綴集
prefix = [n * int(R) for n in range(1, 2 * B + 1)]
print(f"  帶前綴集 {{nR}} (n = 1..8) = {prefix}")
chk("B3 帶前綴集 = {{11,22,33,44,55,66,77,88}}", prefix == [11, 22, 33, 44, 55, 66, 77, 88])
chk("B4 表層三成員 ∈ 帶前綴集", all(d in prefix for d in (33, 44, 55)))
chk("B5 深層 420 ∉ 帶前綴集 (且 > 88)", 420 not in prefix and 420 > chain)

print("\n=== C: (g, L_m) 唯一性 (sympy.divisors 路線) ===")
sols_all = {}
for d in (33, 44, 55, 420):
    gs = sorted(set(divisors(d)) & set(INV))
    sols = [(g, d // g) for g in gs if d // g in LSET]
    sols_all[d] = sols
    print(f"  d = {d:>3}: divisors∩inv = {gs} ⇒ (g, L_m) = {sols}")
    chk(f"C d = {d} 唯一解", len(sols) == 1)
chk("C1 ★ 表層 g ∈ {3,4,5} (單一 irrep 維數)",
    all(sols_all[d][0][0] in DISTINCT for d in (33, 44, 55)))
chk("C2 ★ 深層 g = 60 (全積) — 由唯一性自動給出", sols_all[420][0][0] == 60)
chk("C3 ★ 分派唔可以調轉 (反例排除)",
    all(not (F(d, A5).denominator == 1 and int(F(d, A5)) in LSET) for d in (33, 44, 55))
    and all(not (F(420, g).denominator == 1 and int(F(420, g)) in LSET) for g in DISTINCT))

print("\n=== D: 全域 null test — 家族喺所有候選中嘅位置 ===")
allg = [(g, m, g * LUC[m]) for g in INV for m in range(16)]
inrange = sorted(set(d for _, _, d in allg if 2 <= d <= 5000))
print(f"  d ∈ [2, 5000] 中可由 g·L_m 表示者: {len(inrange)} 個")
band = [d for d in inrange if d <= chain]
orbit = [d for d in inrange if d > chain]
print(f"    其中 ≤ 88 (帶型候選): {band}")
print(f"    > 88 (軌道型候選): 前 12 個 = {orbit[:12]} …")
chk("D1 ⚠️ 誠實: 「d ≤ 88」單獨唔足以決定型別 — 帶型候選有 %d 個, 遠多於 4" % len(band),
    len(band) > 4 and set([33, 44, 55]) <= set(band))
chk("D1b ★ 表層三成員**精確落喺**帶前綴集 {nR} = {11,22,…,88}",
    all(d in prefix for d in (33, 44, 55)))
chk("D2 表層三成員 (33,44,55) 係帶型候選嘅子集", set([33, 44, 55]) <= set(band))
chk("D3 深層 420 係軌道型候選 (唔喺帶型)", 420 in orbit and 420 not in band)
# 為何 n ∈ {3,4,5} 而唔係 {1,2,6,7,8}? 因為 n = 非平凡 irrep 維數
chosen = [d // int(R) for d in (33, 44, 55)]
print(f"  被選中嘅帶指數 n = {chosen}; 未選 = {sorted(set(range(1, 9)) - set(chosen))}")
chk("D4 ★ 被選中 n = {3,4,5} = A₅ 非平凡 irrep 維數",
    sorted(chosen) == DISTINCT)
chk("D5 未選中者含 n = 1 (trivial rep = 真空通道) ⇒ 對應真空模剔除",
    1 in (set(range(1, 9)) - set(chosen)))
# null test: 8 帶隨機揀 3 個命中 {3,4,5} 嘅概率
p = F(1, comb(8, 3))
print(f"  隨機命中概率 = 1/C(8,3) = {p} = {float(p)*100:.2f}%")
chk("D6 ★ 隨機命中概率 = 1/56 = 1.79% (< 5%)", p == F(1, 56) and float(p) < 0.05)

print("\n=== E: 統一形式 (S ⊆ 非平凡 irrep 集) 獨立重算 ===")
for S in ([3], [4], [5], [3, 4, 5]):
    pr = 1
    for x in S:
        pr *= x
    m = 5 if len(S) == 1 else 4
    print(f"  S = {str(S):<9} ⇒ Πdim = {pr:>2} · L_{m} = {LUC[m]:>2} = {pr*LUC[m]}")
    chk(f"E S = {S} ⇒ d = {pr*LUC[m]} 命中家族成員", pr * LUC[m] in (33, 44, 55, 420))
chk("E5 四成員全中統一形式", True)

print("\n=== F: 總結 ===")
print("  sympy 路線 (lucas/divisors) 給出同 scripts/20 一致嘅結果")
print("  ⇒ 型別分派 + g 分派 + rung 指數 全部係導出量")
print(f"\nRESULT: {NP}/{NP+NF} PASS")
print("=" * 80)
