#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O144-31 — 問題 6: 8 膠子與鏈的關係
========================================================================
問題原文 (01_problem_record.md 開放問題 6):
  「8 膠子與鏈的關係: 8 = 3²−1 = B×2 = F₆, SU(3)_C = B−1」

上游事實 (只讀, 未改):
  ★ o124_qcd_gluon_scattering/docs/03_derivation.md §A.2:
      「8 = dim adj SU(3) = N_c² − 1 = F₆ = (T̂⁶)₁₂
        = Σ_f N_c Q_f²  (3 代 × (4/3 + 1/3 + 1) = 8)」
      「N_c = B − 1 = 3 (剛性代數分解, 非近似)」 (O85 V14, Pati-Salam)
      「12 = 1+8+3 = L₅+1 = B·N_gen」
  ★ o142_boson_mass_derivation/final_result.md:
      「8 = F₆ = dim(adj SU(3)) 膠子數; F₆ = b₀+1」
  ★ o124 docs/02 L77: 膠子數 8 = F₆ = N_c²−1 = Σ_f N_c Q_f² (雙重身份)

本腳本 (寫入限於 o144_boson_identity/):
  §A N_c = B−1 之結構內容
  §B 8 = (B−1)²−1 之展開 — 「雙重身份」之退化性
  §C 8 = Σ_f N_c Q_f² (QED β 費米子和) 之核實
  §D 12 = 1+8+3 之身份鏈
  §E 密度測試
  §F 判決
"""
import numpy as np
import mpmath as mp
import itertools, json, sys
from fractions import Fraction

mp.mp.dps = 40
PASS = FAIL = 0
ROWS = []

def chk(cid, name, got, want, tol=1e-30):
    global PASS, FAIL
    ok = abs(mp.mpf(got) - mp.mpf(want)) <= tol
    PASS += 1 if ok else 0
    FAIL += 0 if ok else 1
    ROWS.append({"id": cid, "check": name, "ok": bool(ok)})
    print(f"  [{'PASS' if ok else 'FAIL'}] {cid} {name}")

def chkb(cid, name, cond):
    global PASS, FAIL
    ok = bool(cond)
    PASS += 1 if ok else 0
    FAIL += 0 if ok else 1
    ROWS.append({"id": cid, "check": name, "ok": ok})
    print(f"  [{'PASS' if ok else 'FAIL'}] {cid} {name}")

def hdr(s):
    print("\n" + "=" * 78); print(s); print("=" * 78)

N_d, B, N_gen, M_tree = 44, 4, 3, 33
mu2 = mp.mpf(2)
L4, L5, L7, L10 = 7, 11, 29, 123
F6, F7, F8, F9, F10, F11 = 8, 13, 21, 34, 55, 89

def save():
    json.dump({"passed": PASS, "failed": FAIL, "rows": ROWS},
              open("data/31_gluon_chain.json", "w"), ensure_ascii=False, indent=1)

# ================================================================
hdr("[§A] N_c = B − 1 = 3 之結構內容")
# ================================================================
N_c = B - 1
chk("A1", f"N_c = B − 1 = {N_c} = N_gen = 3 (O85 V14)", N_c, N_gen)
chk("A2", f"B = N_c + 1 = {N_c+1} = 4 (分形級聯分支數, O34 §4)", B, N_c + 1)
print(f"""
  N_c = B − 1 之來源 (O85 V14, Pati-Salam): SU(12) 破缺鏈中色扇區秩 = B−1
  ⟹ N_c = 3 係**推導結果** (非輸入), 前提係 B = 4 = 分形級聯分支數 (O34 🟢)""")

# ================================================================
hdr("[§B] 8 = (B−1)²−1 之展開 — 「雙重身份」之退化性")
# ================================================================
glu = N_c ** 2 - 1
chk("B1", f"膠子數 = N_c² − 1 = {glu} = 8 (adjoint SU(3))", glu, 8)
chk("B2", f"N_c² − 1 = (B−1)² − 1 = B² − 2B = {B*B-2*B}", B * B - 2 * B, 8)
chk("B3", f"B² − 2B = B(B−2) = {B*(B-2)}", B * (B - 2), 8)
chk("B4", f"2B = {2*B} = 8", 2 * B, 8)
chk("B5", f"F₆ = {F6} = 8", F6, 8)
chk("B6", f"B(B−2) = 2B ⟺ B² − 4B = 0 ⟺ B = 4 (單一方程)",
    B * (B - 2) - 2 * B, 0)
# 退化性: 三個身份係同一條方程
chkb("B7", "「雙重身份」退化: N_c²−1 = 2B = F₆ 全部 ⟺ B = 4 (同一方程)",
     (B * (B - 2) - 2 * B) == 0 and F6 == 2 * B)
print(f"""
  ★ 關鍵結構事實: N_c²−1 = B(B−2); 要求 = 2B ⟹ B²−4B = 0 ⟹ **B = 4**
     ⟹ 「8 = N_c²−1」與「8 = 2B = F₆」**唔係兩個獨立事實**,
        而係**同一條方程** (B=4) 之兩個讀法
     ⚠️ 即「雙重身份」係**退化**嘅 (degenerate), 唔增加信息
  ★ 真正獨立之內容 = N_c = B−1 (O85 V14) + B = 4 (O34)""")

# ================================================================
hdr("[§C] 8 = Σ_f N_c Q_f² (QED β 費米子和) 之核實")
# ================================================================
# 3 代, 每代: u-type (Q=2/3, ×N_c), d-type (Q=−1/3, ×N_c), e-type (Q=−1, ×1)
Qu, Qd, Qe = Fraction(2, 3), Fraction(-1, 3), Fraction(-1)
sum_per_gen = N_c * Qu ** 2 + N_c * Qd ** 2 + 1 * Qe ** 2
chk("C1", f"每代 Σ N_c Q² = N_c(4/9) + N_c(1/9) + 1 = {sum_per_gen} = 8/3",
    mp.mpf(sum_per_gen.numerator) / sum_per_gen.denominator, mp.mpf(8) / 3)
total = N_gen * sum_per_gen
chk("C2", f"Σ_f N_c Q_f² = {N_gen} × {sum_per_gen} = {total} = 8",
    mp.mpf(total.numerator) / total.denominator, 8)
# 一般 B: Σ_f N_c Q_f² = N_gen[(B−1)·5/9 + 1]
gen_B = lambda b, ng: Fraction(ng) * (Fraction(b - 1) * Fraction(5, 9) + 1)
chkb("C3", f"一般式: Σ_f N_c Q_f² = N_gen[(B−1)·5/9 + 1] = {gen_B(B,N_gen)} (B=4, N_gen=3)",
     gen_B(B, N_gen) == 8)
chkb("C4", "Σ_f N_c Q_f² = N_c²−1 只喺 (B, N_gen) = (4, 3) 成立 (非恆等式)",
     gen_B(5, 3) != (5 - 1) ** 2 - 1 and gen_B(4, 2) != (4 - 1) ** 2 - 1)
print(f"""
  ★ 核實: Σ_f N_c Q_f² = 3 × 8/3 = 8 (標準 SM QED β 費米子和)
  ⚠️ 但呢個 = N_c²−1 只喺 (B, N_gen) = (4, 3) 成立:
     一般式 N_gen[(B−1)·5/9 + 1]; B=5, N_gen=3 → 3[20/9+1] = 29/3 ≠ 24
     ⟹ 又係**一個巧合** (喺 B=4, N_gen=3 交匯), 非恆等式""")

# ================================================================
hdr("[§D] 12 = 1 + 8 + 3 之身份鏈")
# ================================================================
chk("D1", f"1 + 8 + 3 = {1+8+3} = 12 (SU(3) 表示維度: 單態+伴隨+基礎)",
    1 + 8 + 3, 12)
chk("D2", f"12 = B·N_gen = {B*N_gen}", B * N_gen, 12)
chk("D3", f"12 = L₅ + 1 = {L5+1}", L5 + 1, 12)
chk("D4", f"12 = 2L₄ − μ² = {2*L4-mu2} (2L₄ = N_gen+L₅ = 14, O142 v11)",
    2 * L4 - mu2, 12)
chk("D5", f"SU(12) 基本表示 = 12 (O85 V1: = L₅+1)", 12, L5 + 1)
print(f"""
  12 = 1+8+3 = B·N_gen = L₅+1 = SU(12) fundamental
  ⟹ SU(12) 基本表示維度同時係 SM gauge boson 數 (O85 V17)
  ⚠️ 但 1+8+3 之「8」係 adjoint, 「3」係 fundamental, 「1」係 singlet —
     呢個係 SU(3) 之表示維度, 唔係 SU(12) 之分解 (O85 另有分解鏈)""")

# ================================================================
hdr("[§E] 密度測試 — 「8」有幾特殊")
# ================================================================
VOCAB = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 17, 21, 29, 33, 34, 44, 55, 66, 88, 89, 90, 123, 176]
# 形式 a±b, a·b, a/b, a²±b, a²−1 等
hits = set()
for a in VOCAB:
    for b in VOCAB:
        if a + b == 8: hits.add(f"{a}+{b}")
        if a - b == 8: hits.add(f"{a}−{b}")
        if a * b == 8: hits.add(f"{a}×{b}")
        if b != 0 and Fraction(a, b) == 8: hits.add(f"{a}/{b}")
        if a ** 2 - b == 8: hits.add(f"{a}²−{b}")
        if a ** 2 + b == 8: hits.add(f"{a}²+{b}")
chkb("E1", f"「8」之結構表達數 (a±b, a×b, a/b, a²±b; 詞彙 {len(VOCAB)}) = {len(hits)}",
     len(hits) >= 8)
print(f"  命中 (首 20): {sorted(hits)[:20]}")
print(f"  總命中數: {len(hits)}")
# 對照: 非特殊目標 (e.g. 10) 之命中數
def count_hits(t):
    h = set()
    for a in VOCAB:
        for b in VOCAB:
            if a + b == t: h.add(f"{a}+{b}")
            if a - b == t: h.add(f"{a}−{b}")
            if a * b == t: h.add(f"{a}×{b}")
            if b != 0 and Fraction(a, b) == t: h.add(f"{a}/{b}")
            if a ** 2 - b == t: h.add(f"{a}²−{b}")
            if a ** 2 + b == t: h.add(f"{a}²+{b}")
    return len(h)
h10, h8 = count_hits(10), count_hits(8)
print(f"  對照: 「10」命中 = {h10}; 「8」命中 = {h8}")
chkb("E2", f"「8」命中數 ({h8}) 唔顯著高於對照 「10」({h10}) ⟹ 無密度優勢",
     h8 <= 2 * h10)
print(f"""
  ⚠️ 誠實: 「8」之結構表達**眾多** (F₆, 2B, N_c²−1, B(B−2), Σ N_c Q², 3²−1, …)
     ⟹ 「8 有結構身份 X」**唔構成**推導 (密度產物風險)
     真推導鏈: N_c = B−1 (O85) ⟹ adjoint = N_c²−1 = 8
     ⟹ 唯一真正**獨立**輸入 = N_c = B−1, 其餘全部係其代數後果""")

# ================================================================
hdr("[§F] 判決")
# ================================================================
print(f"""
  ✅ 問題 6 之結構答案:
     ① **推導鏈**: B = 4 (分形級聯分支數, O34 🟢) ⟹ N_c = B−1 = 3 (O85 V14)
        ⟹ 膠子數 = dim(adj SU(3)) = N_c²−1 = 8
     ② 「8 = 2B = F₆」**唔係**獨立事實 —— 係 N_c²−1 = 2B ⟺ B=4 之**同一方程**
        ⟹ 「雙重身份」**退化** (degenerate), 唔增加信息
     ③ 「8 = Σ_f N_c Q_f²」亦係巧合 (只喺 B=4, N_gen=3 交匯; 一般式
        N_gen[(B−1)·5/9+1] ≠ N_c²−1)
     ④ 12 = 1+8+3 = B·N_gen = L₅+1 (SM gauge boson 數)

  ⚠️ 誠實:
     - 真正未解部分**唔係**「8 點嚟」(已由 N_c = B−1 導出), 而係
       「為何 N_c = B−1」(即 SU(12) → SU(3)×SU(2)×U(1) 之破缺機制)
       ⟹ 問題 6 **實質上歸約到問題 2** (O85 只有代數分類, 動力學未導出)
     - 「8」之多重身份係密度產物風險; 唯一獨立輸入 = N_c = B−1

  驗證: scripts/31 = {PASS} PASS / {FAIL} FAIL
""")

save()
print(f"{'='*78}\n總計: {PASS} PASS / {FAIL} FAIL\n{'='*78}")
sys.exit(1 if FAIL else 0)
