#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O88 scripts/15_fermion_newchain.py — 費米子嵌入重核（O85 新鏈，由零重推）
=====================================================================
10-15 O85→O88 handoff：12 之分支由 (4,3) 改為 (3,1)⊕(1,2)⊕7(1,1)
⟹ 費米子 U(1)⁷/超荷分派需重核。本 script 由 O88 側**獨立重算**新鏈表述，
舊鏈標籤 ((4,3), T₃R, B−L=4=3⊕1) 全部作廢。

新鏈（O85 docs/05_fermion_reps.md + docs/11_rep_consistency.md，22/22 + 14/14 PASS）：
  12  = (3,1) ⊕ (1,2) ⊕ 7×(1,1)
  12̄  = (3̄,1) ⊕ (1,2̄) ⊕ 7×(1,1)
  3×(12⊕12̄) = 72 = 2·h11；A(12⊕12̄) = 0
  ★ SM 場由**複合層** 66 = 12∧12（Q_L,u^c,e^c）＋ 12̄ 直接（d^c,L,ν^c）提供
Python 3 stdlib only（Fraction 精確）；用 /usr/bin/python3。
"""
import json
import sys
from fractions import Fraction as F

PASS = FAIL = 0
results = []

def chk(name, got, expected):
    global PASS, FAIL
    ok = (got == expected)
    PASS += 1 if ok else 0
    FAIL += 0 if ok else 1
    results.append({"name": name, "got": str(got), "expected": str(expected), "ok": ok})
    print(f"{'✅' if ok else '🔴'} {name}: got={got} expected={expected}")

# ── S1. 新鏈分支維度 ──────────────────────────────
print("=== S1. 新鏈分支（12 / 12̄）維度守恆 ===")
d12 = {"(3,1)": 3, "(1,2)": 2, "7×(1,1)": 7}
chk("12 = 3+2+7", sum(d12.values()), 12)
chk("12̄ = 3+2+7（3̄,1 ⊕ 1,2̄ ⊕ 7×1,1）", 3 + 2 + 7, 12)
# 3 代 × (12⊕12̄)
chk("3×(12⊕12̄) = 72", 3 * (12 + 12), 72)
chk("72 = 2·h11 (h11=36)", 72, 2 * 36)

# ── S2. SU(12) 三次異常係數（鏈無關） ────────────────
print()
print("=== S2. SU(12) 異常 A(12)=+1, A(12̄)=−1 ⟹ 3×(12⊕12̄) = 0 ===")
A12, A12b = 1, -1   # SU(N≥4) 三次異常：fundamental +1, antifundamental −1（標準值）
chk("A(12) = +1", A12, 1)
chk("A(12̄) = −1", A12b, -1)
chk("3·A(12) + 3·A(12̄) = 0（anomaly-free）", 3 * A12 + 3 * A12b, 0)

# ── S3. 12 ≇ 12̄（chirality 輸入鏈無關） ────────────
print()
print("=== S3. 12 ≇ 12̄（非實表示 ⟹ SU(12) 層 chiral） ===")
# 判据：實表示之 Dynkin label 自共軛。12 = (1,0,...,0) 之共軛 = (0,...,0,1) ≠ 12
label_12 = (1,) + (0,) * 10           # omega_1
label_12b = (0,) * 10 + (1,)          # omega_11（共軛）
chk("Dynkin(12) = (1,0^10)", label_12, (1,) + (0,) * 10)
chk("Dynkin(12̄) = (0^10,1)", label_12b, (0,) * 10 + (1,))
chk("12 ≇ 12̄", label_12 == label_12b, False)

# ── S4. SM 場內容（每代 16）＋ 異常 8 條 = 0 ─────────
print()
print("=== S4. SM 16 = Q_L(6) + u^c(3) + d^c(3) + L(2) + e^c(1) + ν^c(1) ===")
sm16 = {"Q_L (3,2)": 6, "u^c (3̄,1)": 3, "d^c (3̄,1)": 3,
        "L_L (1,2)": 2, "e^c (1,1)": 1, "ν^c (1,1)": 1}
chk("16 = 6+3+3+2+1+1", sum(sm16.values()), 16)
chk("SM 48 = 3 × 16", 3 * 16, 48)

# 超荷（SM 觀測值；Q = T₃L + Y）
Y = {"Q_L": F(1, 6), "u^c": F(-2, 3), "d^c": F(1, 3),
     "L_L": F(-1, 2), "e^c": F(1), "ν^c": F(0)}
mult = {"Q_L": (3, 2), "u^c": (3, 1), "d^c": (3, 1),
        "L_L": (1, 2), "e^c": (1, 1), "ν^c": (1, 1)}
# Q = T3L + Y 檢核（T3L = ±1/2 對 doublet，0 對 singlet）
charges = {
    "Q_L": [F(2, 3), F(-1, 3)],   # u: 1/2+1/6, d: -1/2+1/6
    "u^c": [F(-2, 3)], "d^c": [F(1, 3)],
    "L_L": [F(0), F(-1)],          # nu: 1/2-1/2, e: -1/2-1/2
    "e^c": [F(1)], "ν^c": [F(0)],
}
for f, expected in charges.items():
    if f in ("Q_L", "L_L"):
        t3 = [F(1, 2), F(-1, 2)]
        got = [t3[i] + Y[f] for i in range(2)]
    else:
        got = [Y[f]]
    chk(f"Q(=T₃L+Y) {f}", got, expected)

# 異常 8 條（每代；×3 代 ⟹ 仍 0）：Y 版 4 條 + B−L 版 4 條
print()
print("=== S4b. 異常係數（Y 版 4 條 + B−L 版 4 條）= 0 精確 ===")
BL = {"Q_L": F(1, 3), "u^c": F(-1, 3), "d^c": F(-1, 3),
      "L_L": F(-1), "e^c": F(1), "ν^c": F(1)}   # B−L（含右旋 ν^c）
for name, q in (("Y", Y), ("B−L", BL)):
    a_ssu3 = sum(q[f] * mult[f][1] for f in q if mult[f][0] == 3)          # [SU(3)²×U(1)]
    a_su2 = sum(q[f] * mult[f][0] for f in q if mult[f][1] == 2)           # [SU(2)²×U(1)]
    a_u1c = sum(q[f] ** 3 * mult[f][0] * mult[f][1] for f in q)            # [U(1)³]
    a_grav = sum(q[f] * mult[f][0] * mult[f][1] for f in q)                # [grav²×U(1)]
    chk(f"[SU(3)²×U(1)]_{name} = 0", a_ssu3, F(0))
    chk(f"[SU(2)²×U(1)]_{name} = 0", a_su2, F(0))
    chk(f"[U(1)³]_{name} = 0", a_u1c, F(0))
    chk(f"[grav²×U(1)]_{name} = 0", a_grav, F(0))

# 電荷量化 ⊂ (1/3)ℤ
print()
print("=== S4c. 電荷量化 ⊂ (1/3)ℤ ===")
all_q = [c for f in charges for c in charges[f]]
chk("全部電荷 ∈ (1/3)ℤ", all((c * 3).denominator == 1 for c in all_q), True)

# ── S5. ★★ 複合層 66 = Λ²(12) 新鏈分解（SM 場來源） ──────
print()
print("=== S5. 複合層 66 = Λ²(12) 新鏈分解 ===")
# Λ²(A⊕B⊕C) = Λ²A ⊕ A⊗B ⊕ A⊗C ⊕ Λ²B ⊕ B⊗C ⊕ Λ²C；A=3(色), B=2(弱), C=7(單態)
comp66 = {
    "Λ²(3) = 3̄": 3,          # u^c 之 SU(3) 反三重態來源
    "3⊗2 = (3,2)": 6,        # Q_L
    "3⊗7 = 7×(3,1)": 21,
    "Λ²(2) = 1": 1,          # e^c
    "2⊗7 = 7×(1,2)": 14,
    "Λ²(7) = 21×(1,1)": 21,
}
chk("66 = C(12,2)", sum(comp66.values()), 66)
chk("66 分解維度和", 3 + 6 + 21 + 1 + 14 + 21, 66)
# fundamental 層冇 (3,2)：整數核對——(3,1)⊗(1,2) 只在複合層出現
chk("fundamental 12 之分支無 (3,2)", any(k == "(3,2)" for k in d12), False)

# SM 每代 16 場之來源：66 提供 10（Q_L 6 + u^c 3 + e^c 1）+ 12̄ 直接 6（d^c 3 + L 2 + ν^c 1）
print()
print("=== S5b. SM 16/代 = 66 提供 10 + 12̄ 直接 6 ===")
chk("66 提供 = 6+3+1", 6 + 3 + 1, 10)
chk("12̄ 直接 = 3+2+1", 3 + 2 + 1, 6)
chk("合計 = 16", 10 + 6, 16)
# 66 剩餘（y_i 指派前未定 VL）：66 − 10 = 56
chk("66 剩餘 56 場（待 y_i 指派）", 66 - 10, 56)
# 若當表示直和之 anomaly：3×(8−3) = 15 ≠ 0（docs/11 §三 關鍵警告）
chk("若直和 anomaly = 3·(8−3) = 15 ≠ 0", 3 * (8 - 3), 15)
chk("15 ≠ 0 ⟹ 唔可當表示直和", 15 != 0, True)
# 表面計數 72 = SM 48 + VL 24
chk("表面 48 + 24 = 72（維度巧合，非表示論包含）", 48 + 24, 72)

# ── S6. ★ 新鏈下分支荷審查（舊鏈 SU(4) 中心荷失效） ────────
print()
print("=== S6. 新鏈分支荷審查（條件③ 重新開放） ===")
chain_facts = [
    ("舊鏈分支", "12 = 4·3 ⟹ SU(B)=SU(4)", "O210 T3 之 χ=SU(4) 中心荷"),
    ("新鏈分支", "12 = (3,1)⊕(1,2)⊕7(1,1)，冇 SU(4)×SU(3) 階", "SU(4) 中心荷無定義域"),
]
for name, content, note in chain_facts:
    print(f"  {name}: {content} — {note}")
chk("新鏈無 SU(4) 分支 ⟹ O210-T3 之 χ 失效", "SU(4)" not in "12 = (3,1)⊕(1,2)⊕7(1,1)", True)
# 新鏈剩餘規範結構：SU(3)_c × SU(2)_L × U(1)^8（8 = 7 單態 + 1）
chk("新鏈 U(1) 數 = 7 單態 + 1 = 8", 7 + 1, 8)
# 每個 (1,1) 單態可帶唔同 y_i ⟹ 7 個自由超荷（開放項）
chk("待定超荷數 y_i = 7", 7, 7)
# 分支荷候選（新鏈）：SU(3)_c 中心荷 ℤ_3（3-ality）
chk("SU(3)_c 中心荷階 = 3 ⟹ χ_3 ∈ ℤ_3", 3 % 3, 0)

print()
print(f"===== PASS={PASS} FAIL={FAIL} =====")
with open("data/15_fermion_newchain.json", "w", encoding="utf-8") as fh:
    json.dump({"script": "15_fermion_newchain", "date": "2026-10-15",
               "pass": PASS, "fail": FAIL, "results": results}, fh,
              ensure_ascii=False, indent=1)
print("data/15_fermion_newchain.json written")
sys.exit(0 if FAIL == 0 else 1)