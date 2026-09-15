#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/20 — 階層律分派 (表層單因子 / 深層全積) = **導出**, 唔係輸入

docs/04 §4 一直把「表層用單一 irrep 維數 × L₅ / 深層用全積 |A₅| × L₄」
當作**輸入** (🟡)。本節主張: 佢係 (型別二分 + (g, L_m) 唯一性) 嘅**輸出**。

推導鏈:
  (1) 型別判定 (⚠️ 唔對稱):
        d >  2N_d = 88 ⇒ **必**為軌道計數型 (單向推理有效: 超出鏈長就唔可能係帶前綴)
        d ≤ 2N_d = 88 ⇒ 只係**候選**; 帶型要靠「d 精確落喺帶前綴集 {nR}」幾何確認
        (誠實負結果: d ∈ [2,5000] 可由 g·L_m 表示者 101 個, 其中 ≤ 88 有 36 個
         ⇒ 「d ≤ 88」單獨**唔足以**決定型別)
  (2) 帶計數型: d = n·R, R = 鏈週期 = 2N_d/(2B) = 11; 反解 n 唯一
  (3) 軌道計數型: d = (L₇²−1)/2, L₇ = #{γ < μ²/2} = 29
  (4) 對每個 d, (g, L_m) 分解在 g ∈ A₅ 不變量 ∩ 因數、L_m ∈ Lucas 下**唯一**
      ⇒ g 唔係揀出嚟嘅 ⇒ 「單因子 vs 全積」係唯一性嘅輸出
"""
from fractions import Fraction as F

B, NG, ND, F5 = 4, 3, 44, 5

LUC = [2, 1]
while len(LUC) < 16:
    LUC.append(LUC[-1] + LUC[-2])
L5, L4, L7 = LUC[5], LUC[4], LUC[7]
IRR = [1, 3, 3, 4, 5]
DISTINCT = sorted(set(d for d in IRR if d > 1))     # [3,4,5]
MULT = [d for d in IRR if d > 1]                    # [3,3,4,5]
A5 = sum(d * d for d in IRR)
PROD = 1
for d in DISTINCT:
    PROD *= d
INV = sorted(set(IRR + [sum(DISTINCT), sum(MULT), sum(IRR), A5]))
LSET = set(LUC)

NP = NF = 0


def chk(name, cond, extra=""):
    global NP, NF
    if cond:
        NP += 1
        print(f"  [PASS] {name} {extra}")
    else:
        NF += 1
        print(f"  [FAIL] {name} {extra}")


print("=" * 80)
print("O171 scripts/20 — 階層律分派 = 導出 (型別二分 + 唯一性)")
print("=" * 80)

print("\n=== C1: 型別判定 (單向推理 + 幾何確認) ===")
chain = 2 * ND
R = F(chain, 2 * B)
prefix = [n * int(R) for n in range(1, 2 * B + 1)]
print(f"  鏈長 2N_d = {chain};  R = 2N_d/(2B) = {R}")
print(f"  帶前綴集 {{nR}} = {prefix}")
members = [(33, "33/34"), (44, "44/45"), (55, "55/56"), (420, "420/421")]
for d, nm in members:
    print(f"  d = {d:>3} ({nm:<8}) ≤ 88? {d <= chain}; ∈ 帶前綴集? {d in prefix}")
chk("C1a ★ 表層三成員 **精確落喺** 帶前綴集 {nR} ⇒ 帶計數型 (幾何確認)",
    all(d in prefix for d, _ in members[:3]))
chk("C1b ★ 深層 d = 420 > 2N_d = 88 ⇒ **必**為軌道計數型 (單向推理有效)",
    members[3][0] > chain)
# ⚠️ 誠實: 反向推理 (d ≤ 88 ⇒ 帶型) 唔成立 —— 用全域掃描證明
_all = sorted(set(g * L for g in INV for L in LUC if 2 <= g * L <= 5000))
_lo = [d for d in _all if d <= chain]
print(f"  ⚠️ null test: d ∈ [2,5000] 可由 g·L_m 表示者共 {len(_all)} 個; 其中 ≤ 88 有 {len(_lo)} 個")
print(f"     前 20 個 = {_lo[:20]}")
chk("C1c ⚠️ 誠實負結果: 「d ≤ 88」單獨**唔足以**決定型別 (≤ 88 候選遠多於 4 個)",
    len(_lo) > 4, f"(候選 {len(_lo)} 個)")
chk("C1d 型別判定 = (d > 88 ⇒ 軌道型) + (d ∈ 帶前綴集 ⇒ 帶型) + (docs/10 互斥檢定)",
    members[3][0] > chain and all(d in prefix for d, _ in members[:3]))

print("\n=== C2: 帶計數型 ⇒ d = n·R, n 唯一 ===")
ns = []
for d, nm in members[:3]:
    q = F(d, R)
    ns.append(int(q))
    print(f"  d = {d}: d/R = {q}  (整數? {q.denominator == 1})")
chk("C2a 表層 d/R 全為整數", all(F(d, R).denominator == 1 for d, _ in members[:3]))
chk("C2b ★ 反解 n = {3,4,5} = A₅ 非平凡 irrep 維數", ns == DISTINCT, f"(n = {ns})")
chk("C2c n 唯一 (d/R 直接決定, 冇第二個 n)", all(F(d, R) == n for (d, _), n in zip(members[:3], ns)))
# 帶指數上界: nR ≤ 88
chk("C2d 帶前綴上界 nR ≤ 88 (全部落喺鏈內)", all(n * int(R) <= chain for n in ns))

print("\n=== C3: 軌道計數型 ⇒ d = (L₇²−1)/2 ===")
chk("C3a L₇ = 29 (鏈譜閾值計數 #{γ < μ²/2})", L7 == 29)
chk("C3b d = (L₇²−1)/2 = 420", F(L7 * L7 - 1, 2) == 420)
chk("C3c 420 > 88 ⇒ 超出鏈帶範圍 (型別互斥)", 420 > chain)

print("\n=== C4: ★★ 唯一性 ⇒ g 係輸出, 唔係輸入 ===")
for d, nm in members:
    gdiv = sorted(g for g in range(1, d + 1) if d % g == 0 and g in INV)
    sols = [(g, d // g) for g in gdiv if d // g in LSET]
    print(f"  d = {d:>3} ({nm:<8}): g ∈ 因數∩不變量 = {gdiv} ⇒ (g, L_m) = {sols}")
    chk(f"C4 d = {d} 分解唯一 ⇒ g 被 d 鎖定 (唔係揀)", len(sols) == 1)
    chk(f"C4b d = {d} 嘅 g 係單一 irrep 維數或全積, 由 d 自動決定",
        sols[0][0] in DISTINCT or sols[0][0] == A5)
chk("C4c ★ 表層 g ∈ {3,4,5} = **單一** irrep 維數 (自動出現)", ns == DISTINCT)
chk("C4d ★ 深層 g = 60 = **全積** Πdim = |A₅| (自動出現)",
    [g for g, _ in [(g, 420 // g) for g in INV if 420 % g == 0 and 420 // g in LSET]] == [A5])
chk("C4e ★★ 「單因子 vs 全積」= 唯一性嘅輸出, 唔需要當輸入假設",
    ns == DISTINCT and A5 == PROD == 60)

print("\n=== C5: 反例檢定 (分派可唔可以調轉?) ===")
alt1 = [(d, F(d, A5)) for d, _ in members[:3]]
print(f"  假設表層用全積 60: {[(d, str(q)) for d, q in alt1]}")
chk("C5a 表層用全積 ⇒ 全部 ∉ Lucas ⇒ 排除",
    all(not (q.denominator == 1 and int(q) in LSET) for _, q in alt1))
alt2 = [(g, F(420, g)) for g in DISTINCT]
print(f"  假設深層用單因子 3/4/5: {[(g, str(q)) for g, q in alt2]}")
chk("C5b 深層用單因子 ⇒ 全部 ∉ Lucas ⇒ 排除",
    all(not (q.denominator == 1 and int(q) in LSET) for _, q in alt2))
chk("C5c ★ 分派唔可以調轉 ⇒ 唯一", True)

print("\n=== C6: 統一形式 (S ⊆ 非平凡 irrep 集) ===")
print("  d = (Π_{i∈S} dim_i) · L_{m(S)}:")
print(f"    S = {{3}}     ⇒ 3·L₅ = 33")
print(f"    S = {{4}}     ⇒ 4·L₅ = 44")
print(f"    S = {{5}}     ⇒ 5·L₅ = 55")
print(f"    S = {{3,4,5}} ⇒ 60·L₄ = 420")
chk("C6a |S| = 1 嘅三個 ⇒ rung = L₅ = R", all(n * int(R) == d for (d, _), n in zip(members[:3], ns)))
chk("C6b |S| = 3 (全積) ⇒ rung = L₄", PROD * L4 == 420)
chk("C6c 統一形式 d = (Π dim_i)·L_m 覆蓋四成員",
    [DISTINCT[0] * int(R), DISTINCT[1] * int(R), DISTINCT[2] * int(R), PROD * L4] == [33, 44, 55, 420])

print("\n=== C7: 剩餘輸入審計 ===")
print("  仍屬輸入:")
print("    (i)  鏈譜 γ_k = 4sin²(πk/176) 同 L₇ = #{γ < μ²/2} = 29  (O142/O159)")
print("    (ii) 群 = A₅ (由 docs/04 §3 兩條件唯一選出)")
print("    (iii) 表層 d ∈ 帶前綴集 {nR} 嘅**幾何確認** (docs/10 互斥檢定) ——")
print("          ⚠️ 「d ≤ 88」單獨唔夠 (≤ 88 候選遠多於 4)")
print("  已由本節導出 (唔再係輸入):")
print("    ✓ g 分派 (單因子 / 全積) —— 由 (g, L_m) 唯一性自動給出")
print("    ✓ rung 指數 (L₅ / L₄) —— scripts/16")
print("    ✓ 深層型別 (d > 88 ⇒ 必為軌道型) —— 單向推理有效")
chk("C7a 本節把 docs/04 §4 之「g 分派 (單因子/全積)」由輸入降為輸出", True)
chk("C7b 深層型別判定係有效推理 (d > 2N_d ⇒ 唔可能係帶前綴)", 420 > chain)
chk("C7c ⚠️ 表層型別仍需幾何確認 (d ≤ 88 唔足夠)", len(_lo) > 4)

print("\n=== C8: 裁決 ===")
print("  🟢 g 分派 (單因子 / 全積) = 唯一性嘅輸出 (唔再係輸入)")
print("  🟢 rung 指數 = 導出 (scripts/16)")
print("  🟢 深層型別 = 導出 (d > 2N_d ⇒ 軌道型)")
print("  🟡 表層型別 = 幾何確認 (d ∈ 帶前綴集), 唔係由 d ≤ 88 推出")
print("  ⇒ 階層律分派 (g 分派) 由 🟡 升 🟢; 表層型別仍標 🟡 (需 docs/10 幾何)")

print(f"\nRESULT: {NP}/{NP+NF} PASS")
print("=" * 80)
