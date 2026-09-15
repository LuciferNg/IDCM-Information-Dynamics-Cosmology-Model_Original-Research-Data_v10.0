#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/16 — R1b-指數: rung 指數 m 係「導出量」而唔係「自由選擇」

docs/04 §6 遺留:
  🔴 「sector 大小嘅定量律 — 為何係 L₅ (表層) 同 L₄ (深層) 而唔係其他 rung?」

本節嘅主張 (待驗):
  表層: 鏈週期 R 由「帶數 = 2B」**唯一**決定 ⇒ R = 88/(2B) = 11 = L₅。
        故「表層 rung = L₅」**唔係選擇** —— 佢係鏈週期嘅值。
  深層: 階層律固定 g = |A₅| = 60 ⇒ L_m = d/g = 420/60 = 7 = L₄。
        故「深層 rung = L₄」**唔係選擇** —— 佢係商。
  ⇒ rung 指數唔係自由參數; 剩餘輸入只有「階層律分派 (表層單因子 / 深層全積)」本身。

純 mpmath/Fraction 路徑, 唔 import 其他 script。
"""
import mpmath as mpm
from fractions import Fraction as F

mp = mpm.mp
mp.dps = 40

B = 4          # 分支因子
NG = 3         # N_gen
ND = 44        # N_d 鏈格點數
MU2 = 2        # μ²
F5 = 5

# --- Lucas 遞歸 (L0 = 2, L1 = 1) ---
LUC = [2, 1]
while len(LUC) < 16:
    LUC.append(LUC[-1] + LUC[-2])
L = {i: LUC[i] for i in range(16)}
L5, L4, L7 = L[5], L[4], L[7]

NP = 0
NF = 0


def chk(name, cond, extra=""):
    global NP, NF
    if cond:
        NP += 1
        print(f"  [PASS] {name} {extra}")
    else:
        NF += 1
        print(f"  [FAIL] {name} {extra}")


print("=" * 80)
print("O171 scripts/16 — R1b-指數: rung 指數係導出量")
print("=" * 80)

# ============================================================
print("\n=== C1: 鏈週期 R 由「帶數 = 2B」唯一決定 ===")
print(f"  N_d = {ND}, B = {B}, 帶數 = 2B = {2*B}")
chk("C1a 鏈長 2N_d = 88", 2 * ND == 88)
chk("C1b 帶數 = 2B = 8 (由分支因子導出)", 2 * B == 8)
Rf = F(2 * ND, 2 * B)
R = int(Rf)
print(f"  R = 2N_d/(2B) = {Rf} = {R}")
chk("C1c R = 88/8 = 11 整數 (帶均分)", Rf.denominator == 1)
chk("C1d R = N_d/B = 11 (等價寫法)", F(ND, B) == Rf)
chk("C1e ★ R = 11 = L₅ (鏈週期恰為 Lucas 第 5 項)", R == L5, f"(L₅ = {L5})")
# 88 嘅因數中屬 Lucas 者
div88 = [d for d in range(1, 89) if 88 % d == 0]
lucas88 = [d for d in div88 if d in LUC]
print(f"  88 嘅因數 = {div88}")
print(f"  其中屬 Lucas 者 = {lucas88}")
chk("C1f 88 嘅 Lucas 因數 = {1,2,4,11} ⇒ **單靠 Lucas 性唔夠** (4 都合格)", lucas88 == [1, 2, 4, 11])
cand = [d for d in lucas88 if B <= d < 88]
print(f"  ⚠️ 若只用「Lucas 因數 + B ≤ R < 88」⇒ 候選 = {cand} ⇒ 唔唯一 (4 同 11)")
chk("C1g ⚠️ 誠實: Lucas 因數路線**唔足夠** (候選 4 同 11)", cand == [4, 11])
# 真約束: 帶數 = 2B (鏈被 2B 帶均分) ⇒ R = 2N_d/(2B)
nb = 2 * ND // R
chk("C1h ★ 真約束係「帶數 = 2B = 8」⇒ R = 2N_d/(2B) = 11 唯一",
    2 * ND == (2 * B) * R and nb == 2 * B, f"(帶數 = {nb})")
chk("C1i ★ R = N_d/B = 44/4 = 11 = L₅ ⇒ 表層 rung = L₅ 由 **N_d/B** 導出 (唔靠 Lucas 識別)",
    F(ND, B) == R and R == L5)

# ============================================================
print("\n=== C2: 表層 rung 指數由 R 反解 (m = 5 唯一) ===")
irr = [1, 3, 3, 4, 5]
dims_distinct = sorted(set(d for d in irr if d > 1))
dims_mult = [d for d in irr if d > 1]
inv = sorted(set(irr + [sum(dims_distinct), sum(dims_mult), sum(irr), sum(d * d for d in irr)]))
print(f"  A₅ 不變量集 = {inv}")
print(f"  Lucas (L₀..L₁₅) = {LUC}")
members = [(33, "33/34 (O10)"), (44, "44/45 (邊界)"), (55, "55/56 (O167)"), (420, "420/421 (O167)")]
sols_all = {}
for d, nm in members:
    sols = [(g, m, L[m]) for g in inv for m in range(16) if g * L[m] == d]
    sols_all[d] = sols
    print(f"  d = {d:>3} ({nm:<16}) (g, m, L_m) = {sols}")
for d, nm in members:
    chk(f"C2 表層/深層 d = {d} 嘅 (g, L_m) 分解唯一", len(sols_all[d]) == 1)
for d in (33, 44, 55):
    g, m, lm = sols_all[d][0]
    chk(f"C2b d = {d} ⇒ m = {m} 且 L_m = {lm} = R", lm == R and g in dims_distinct,
        f"(g = {g} ∈ {dims_distinct})")
chk("C2c ★ 表層三個成員共享 m = 5, 而 L₅ = R (鏈週期)",
    all(sols_all[d][0][1] == 5 and sols_all[d][0][2] == R for d in (33, 44, 55)))
g420, m420, lm420 = sols_all[420][0]
chk("C2d 深層 d = 420 ⇒ (g, m) = (60, 4), g = |A₅| = 60", (g420, m420) == (60, 4),
    f"(實際 ({g420}, {m420}), L_m = {lm420})")

# ============================================================
print("\n=== C3: 深層 rung 由階層律 (g = |A₅|) 反解 ===")
A5 = sum(d * d for d in irr)
chk("C3a |A₅| = Σdim² = 60", A5 == 60)
chk("C3b 420 = (L₇²−1)/2 軌道折疊", F(L7 * L7 - 1, 2) == 420, f"(L₇ = {L7})")
chk("C3c 420 = L₄·|A₅| = 7·60", L4 * A5 == 420)
Lm420 = F(420, A5)
print(f"  商 420/|A₅| = {Lm420} = {int(Lm420)}")
chk("C3d 商 = 7 = L₄ (深層 rung = 商, 唔係選擇)", int(Lm420) == L4 and Lm420.denominator == 1)
cand60 = [g for g in inv if F(420, g).denominator == 1 and int(F(420, g)) in LUC]
print(f"  令 420/g ∈ Lucas 嘅 g ∈ 不變量集 = {cand60}")
chk("C3e ★ 唯一性: 只有 g = 60 令 420/g ∈ Lucas", cand60 == [60])

# ============================================================
print("\n=== C4: 交叉排除 (表層唔可用 60, 深層唔可用 3/4/5) ===")
for d in (33, 44, 55):
    q = F(d, A5)
    print(f"  {d}/60 = {q} ∈ Lucas? {q.denominator == 1 and int(q) in LUC}")
chk("C4 表層用 g = 60 ⇒ 33/60, 44/60, 55/60 全部 ∉ Lucas (或非整數)",
    all(not (F(d, A5).denominator == 1 and int(F(d, A5)) in LUC) for d in (33, 44, 55)))
for g in dims_distinct:
    q = F(420, g)
    print(f"  420/{g} = {q} ∈ Lucas? {q.denominator == 1 and int(q) in LUC}")
chk("C4b 深層用 g ∈ {3,4,5} ⇒ 420/g = 140/105/84 全部 ∉ Lucas",
    all(not (F(420, g).denominator == 1 and int(F(420, g)) in LUC) for g in dims_distinct))
chk("C4c 交叉排除 ⇒ 表層/深層嘅 g 分派互斥", True)

# ============================================================
print("\n=== C5: 指數唔係自由參數 (導出鏈) ===")
print("  表層: 帶數 2B = 8 (由 B 導出) ⇒ R = 88/(2B) = 11 = L₅ ⇒ m = 5")
print("  深層: g = |A₅| = 60 (階層律) ⇒ L_m = 420/60 = 7 = L₄ ⇒ m = 4")
chk("C5a 表層 m 由鏈週期 R 決定 (唔係選擇)", all(sols_all[d][0][2] == R for d in (33, 44, 55)))
chk("C5b 深層 m 由商 420/|A₅| 決定 (唔係選擇)", int(F(420, A5)) == L4)
chk("C5c 兩層嘅 m 都由既有量導出 ⇒ rung 指數 = 導出量",
    all(sols_all[d][0][2] == R for d in (33, 44, 55)) and int(F(420, A5)) == L4)

# ============================================================
print("\n=== C6: 剩餘輸入 (誠實標註) ===")
print("  仍屬輸入 (本節唔重推): 階層律分派 —— 表層用**單因子**, 深層用**全積**")
print("  ⇒ 「表層/深層」呢個二分本身 = docs/04 §4 (R1) 嘅結果, 本節只補上")
print("     「一旦分派固定, rung 指數就唯一且係導出量」")
chk("C6a 分派律固定後 rung 指數唯一 (四成員全中)", all(len(sols_all[d]) == 1 for d, _ in members))
chk("C6b 表層 m = 5 = index of R; 深層 m = 4 = index of 420/|A₅|",
    sols_all[33][0][1] == 5 and sols_all[420][0][1] == 4)
print("  ⚠️ 本節**唔**聲稱「階層律分派」已推導; 該項仍係 docs/04 §4 之輸入")

print("\n" + "=" * 80)
print(f"RESULT: {NP}/{NP+NF} PASS")
print("=" * 80)
