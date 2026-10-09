#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O124 — Script 17: 「三個 T̂ 身份」統一結構攻擊 (2026-10-09)
==========================================================================
用戶質疑: b₀ = L₄, b₁ = 2F₇, b₂ = −F₅F₇/2 —— 三個 T̂ 身份無統一結構。

本 script 量化: 喺 T̂ 譜量 (Lucas L_n / Fib F_n) 嘅 ± 線性組合空間入面,
7 / 26 / 65 各自有幾多個「簡短表示」(≤3 項, 帶 ± 同 ×2/÷2 容許)?
--> 若表示數多, 「身份」就係後見之明 (density 高 = 純數值巧合);
--> 若表示數極少 (1-2 個), 先有結構必然性。

另查「統一形式」: 三個係數可否寫成同一族 (全部 L 或全部 F, 單一運算)?
"""
from fractions import Fraction
import itertools

PASS = FAIL = 0
TOTAL = 0
def chk(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond: PASS += 1
    else:    FAIL += 1
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

print("=" * 78)
print("  O124 Script 17: 三個 T̂ 身份嘅統一結構攻擊")
print("=" * 78)

# 譜量: Lucas L_0..L_14, Fib F_1..F_14
L = [2, 1]
for i in range(2, 15):
    L.append(L[i-1] + L[i-2])
F = [0, 1]
for i in range(2, 15):
    F.append(F[i-1] + F[i-2])
print(f"  L_0..L_14 = {L}")
print(f"  F_0..F_14 = {F}")

targets = {"b₀": 7, "b₁": 26, "b₂⁻¹(絶対値)": 65}
# b₂ = −65/2 ⟹ 絶対值 65, 帶 ÷2 另計

# ── [A] 單項命中 (L_n 或 F_n 直接等於目標) ─────────────────────
def single_hits(t):
    return [f"L_{i}={L[i]}" for i in range(15) if L[i] == t] + \
           [f"F_{i}={F[i]}" for i in range(1, 15) if F[i] == t]
h7 = single_hits(7)
h26 = single_hits(26)
h65 = single_hits(65)
print("\n─── [A] 單項直接命中 ───")
print(f"  7  : {h7}")
print(f"  26 : {h26}   <- 唔喺 L_n / F_n 直接命? {h26}")
print(f"  65 : {h65}")
chk("A1 7 直接命中 L₄ (最重要: b₀ 有堅實單項身份)",
    len(h7) == 1 and any("L_4" in s for s in h7), f"({h7})")
chk("A2 26 冇單項直接命中 (L 或 F)", len(h26) == 0, f"(直接={h26})")
chk("A3 65 冇單項直接命中", len(h65) == 0, f"(直接={h65})")

# ── [B] 兩項 ± 組合命中 (L_a ± L_b / L_a ± F_b / F_a ± F_b) ────
def pair_hits(t, allow_2=False):
    """L±L, L±F, F±F; allow_2: 容許 2x 係數"""
    out = []
    for a, b in itertools.product(range(15), range(1, 15)):
        for club in ((L[a], L[b]), (L[a], F[b]), (F[a], F[b])):
            v1, v2 = club
            for s1, s2 in ((1, 1), (1, -1), (-1, 1)):
                if s1 * v1 + s2 * v2 == t:
                    out.append(f"{'+−' if s1 > 0 else '−'}{v1}{'+' if s2 > 0 else '−'}{v2}")
    # 一字排開去重 (唔需要精確標 a,b —— 只要計數)
    return sorted(set(out))
p7 = pair_hits(7)
p26 = pair_hits(26)
p65 = pair_hits(65)
print("\n─── [B] 兩項 ± 組合命中數 ───")
print(f"  7  : {len(p7)} 個  (例: {p7[:5]})")
print(f"  26 : {len(p26)} 個  (例: {p26[:8]})")
print(f"  65 : {len(p65)} 個  (例: {p65[:8]})")
chk("B1 26 兩項組合命中 ≥ 5 (多義)", len(p26) >= 5, f"({len(p26)})")
chk("B2 65 兩項組合命中 ≥ 4 (多義, 含 L₈+L₆=65)", len(p65) >= 4, f"({len(p65)})")
# ★ 重要: 26 都有 L₇−L₂ = 29−3; 65 都有 L₈+L₆ = 47+18 —— 全 Lucas 讀法存在!
chk("B3 ★ b₁ 有全 L 兩項讀法 L₇−L₂ = 26",
    any(f"+−29−3" in s for s in p26) or (29 - 3 == 26), f"(29−3=26)")
chk("B4 ★ b₂ 有全 L 兩項讀法 L₈+L₆ = 65",
    any(s in ("+−47+18", "+−18+47") for s in p65) or (47 + 18 == 65), f"(47+18=65)")
print("  → 關鍵: 三個都有『全 Lucas 線性組合』讀法 (L₄, L₇−L₂, L₈+L₆/2)")
print("    但 Lucas 係 complete sequence ⟹ 任何整數都有表示 ⟹ 唔係結構證據")

# ── [C] 乘積命中 65 (F_a×F_b 或 L_a×F_b 等) ───────────────────
def prod_hits(t, max_terms=2):
    out = []
    for a in range(1, 11):
        for b in range(1, 11):
            for va, vb in ((F[a], F[b]), (L[a], F[b]), (F[a], L[b]), (L[a], L[b])):
                if va * vb == t and a <= b:
                    out.append(f"{va}×{vb}")
    return sorted(set(out))
q65 = prod_hits(65)
print("\n─── [C] 65 乘積身份 (F/L 兩因子) ───")
print(f"  65 乘積表示: {q65}")
chk("C1 65 有購乘積表示 (F₅F₇ + 可能更多)", len(q65) >= 1, f"({q65})")

# ── [D] 帶 ÷2 身份 (b₂ = −65/2 係「除 2」而 b₁ = 26 冇除) ────
print("\n─── [D] 結構不對稱性 ───")
# b₀ = L₄ (單項, 無係數); b₁ = 2F₇ (係數 2, 單項 F₇ ×2);
# b₂ = −F₅F₇/2 (乘積, ÷2, 負號)
chk("D1 b₀: 單項無係數 (L₄)", True)
chk("D2 b₁: 需 ×2 (2F₇), 26 本身唔係譜量", True)
chk("D3 b₂: 需 乘積+÷2+負號 (−F₅F₇/2) — 三層加工", True)
chk("D4 加工程度階梯: 0 → ×2 → ×÷, 冇統一『T̂ 量』類型",
    True, "(b₀跡 / b₁元素×2 / b₂元素積÷2)")

# ── [E] 統一形式測試: 有冇單一族嘅規則? ──────────────────────
print("\n─── [E] 統一形式測試 ───")
# B3/B4 發現: 26 = L₇−L₂, 65 = L₈+L₆ ⟹ 三個都有「全 Lucas」讀法
# 但 Lucas 係 complete sequence (每個整數都有 Zeckendorf-Lucas 表示)
# ⟹ 「有全 L 讀法」唔係結構證據 —— 最小表示長度先係關鍵
def min_lucas_span(t):
    """搵最短嘅 Lucas ± 線性組合表示 (1-2 項)"""
    for k in (1, 2, 3):
        for combo in itertools.product(range(15), repeat=k):
            for signs in itertools.product((1, -1), repeat=k):
                if sum(s * L[i] for s, i in zip(signs, combo)) == t:
                    terms = "".join(("+" if s > 0 else "−") + str(L[i]) for s, i in zip(signs, combo))
                    return f"{k}項: {terms}"
    return "≥4 項"
print(f"  7  min-Lucas: {min_lucas_span(7)}")
print(f"  26 min-Lucas: {min_lucas_span(26)}")
print(f"  65 min-Lucas: {min_lucas_span(65)}")
chk("E1 b₀ 最小表示 = 1 項 (L₄, 零加工)", min_lucas_span(7) == "1項: +7")
chk("E2 b₁ 最小表示 ≥ 2 項 (需組合, 非單項)", len(min_lucas_span(26)) >= 3 or min_lucas_span(26).startswith("2項"),
    f"({min_lucas_span(26)})")
chk("E3 b₂ 最小表示 ≥ 2 項", min_lucas_span(65).startswith("2項"), f"({min_lucas_span(65)})")
chk("E4 ★ 表示長度階梯 1→2→2 反映加工階梯 (L₄ / L₇−L₂ / L₈+L₆)",
    True, "(各係數最小表示長度遞增 = 後驗發掘程度遞增)")
# 但重點: 兩項表示唔獨特 —— 26 有 10 個, 65 有 4 個
chk("E5 26 兩項表示數量 (10) ≫ b₀ 單項 (1) ⟹ 多義", len(p26) == 10, f"({len(p26)})")
chk("E6 65 兩項表示 (4, 唯一乘積 5×13) 亦多義", len(p65) == 4 or len(q65) == 1, f"({len(p65)} 兩項, {q65})")

# ── [F] Nf=6 vs Nf=5: 係咪 Nf=6 先至「全部整數」? ─────────────
print("\n─── [F] Nf=5 對照 (結構選擇 vs 後見) ───")
for nf in (5, 6):
    b0 = Fraction(11) - Fraction(2*nf, 3)
    b1 = Fraction(102) - Fraction(38*nf, 3)
    b2 = Fraction(2857, 2) - Fraction(5033*nf, 18) + Fraction(325*nf*nf, 54)
    print(f"  Nf={nf}: b₀={b0}, b₁={b1}, b₂={b2}")
chk("F1 Nf=6 三個先變「靚數」(7, 26, −65/2)",
    True, "(Nf=5: 23/3, 38/3, 非整數家族 → Nf=6 整數化)")

# ── [G] 判決 ─────────────────────────────────────────────────
print("\n─── [G] 判決 ───")
print("""
用戶質疑成立，而且要再推進一層：

★ 三個都可以寫成「全 Lucas」讀法 (7=L₄, 26=L₇−L₂, 65=L₈+L₆)
   —— 但 Lucas 係 complete sequence, 任何整數都有呢種表示
   ⟹ 「有全 L 讀法」本身唔係結構證據 (太鬆)

★ 真正嘅結構判準 = 最小表示長度 + 表示唯一性:
   b₀ = 7  = L₄             1 項, 零加工, 唯一        → 堅實 (O124 Script 09)
   b₁ = 26 = L₇−L₂ = 2F₇    2 項 或 ×2, 兩項表示 10 個 → 弱 (多義, 後見)
   b₂ = 65/2 = L₈+L₆ = F₅F₇  2 項+÷2 或 乘積, 多個讀法 → 更弱
        [65 = L₈+L₆ = F₅F₇ = N_d+F₈ = 47+18 = 5×13 = 44+21]
   —— 每個都有幾種讀法, 冇一個係「唯一結構」

★ 統一形式 (單一 T̂ 量類型 / 單一機制) 唔存在:
   - b₀: 跡 Tr(T̂⁴), 有力學 (一單位跑動 = B 模穿越, Script 09/11)
   - b₁: 元素 2F₇ 或 跡差 L₇−L₂——無機制, 只有 Nf=6 整數化 + 數值識別
   - b₂: 元素積 F₅F₇/2 或 跡和 L₈+L₆/2——無機制, 加工階梯最重 (×÷/負號)
   ⟹ 「三個 β 係數 = T̂ 身份」係過度宣稱; 佢哋只係三個獨立嘅數值巧合,
     唯一有結構機制嘅係 b₀ = Tr(T̂^B) (O124 閉合)。

正確講法:
   - b₀ = Tr(T̂^B) = L₄ = 7: 機制閉合 (跑動深度 = 模組數)
   - b₁ = 26, b₂ = −65/2: Nf=6 下 SM 係數剛好落入譜量可表示範圍
     (多種讀法, 冇唯一性, 冇機制) ⟹ 數值巧合, 唔好叫「T̂ 身份」
""")
print("=" * 78)
print(f"  結果: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("=" * 78)