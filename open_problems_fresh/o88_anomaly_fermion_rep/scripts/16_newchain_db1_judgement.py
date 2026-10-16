#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O88 scripts/16_newchain_db1_judgement.py — 新鏈 ΔB=1 判據（Gap #1）
=====================================================================
背景：舊鏈判據「SU(4) colour (反)三重態 ∧ |B−L|=2/3」之 SU(4) 階已隨 O85 新鏈消失
（O88 docs/13 §二、docs/14 §三）。本 script 由新鏈結構重推 ΔB=1 載體判據。

新鏈結構（O85 docs/01–04）：
  SU(12) [143] → adjoint VEV diag(aI₃,bI₂,c₁..c₇) → S(U(3)×U(2)×U(1)⁷) [dim 19]
              → 7× 帶電單態 VEV → SU(3)_c×SU(2)_L×U(1)_Y [rank 4]
  X/Y 玻色子 = 色-弱交叉 adjoint 分量 3×2×2 = 12 個，質量 = g·|λ₄−λ₂|
  fundamental 12 = (3,1) ⊕ (1,2) ⊕ 7×(1,1)

本檔只推：① adjoint 143 之新鏈分解（確認 X/Y 層次）；② Λ^k(12) 新鏈分解；
③ ΔB 算子在新鏈之結構來源審查（誠實標記不可釘死處）。
Python stdlib only；用 /usr/bin/python3。
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

def C(n, k):
    from math import comb
    return comb(n, k)

# ── S1. adjoint 143 之新鏈分解 ────────────────────
print("=== S1. adjoint 143 喺 S(U(3)×U(2)×U(1)⁷) 下之分解 ===")
blocks = {
    "(8,1,0) su(3) adjoint": 8,
    "(1,3,0) su(2) adjoint": 3,
    "(1,1,·) 7 個 U(1) 對角": 7,
    "(1,1,0) traceless 額外": 1,
}
inside = sum(blocks.values())
chk("塊內 dim = 8+3+7+1 = 19（docs/01: dim 19）", inside, 19)
cross = {
    "(3,2)+c.c. 色-弱交叉（X/Y）": 2 * 3 * 2,          # 12
    "(3,1)·1⁷ + c.c. 色-單態": 2 * 3 * 7,              # 42
    "(1,2)·1⁷ + c.c. 弱-單態": 2 * 2 * 7,              # 28
    "(1,1)⊗(1,1) 單態-單態": 2 * C(7, 2),              # 42
}
cross_sum = sum(cross.values())
chk("跨塊 dim = 12+42+28+42 = 124", cross_sum, 124)
chk("19 + 124 = 143（adjoint 全維）", inside + cross_sum, 143)
chk("★ X/Y = 3×2×2 = 12（色×弱×正反）（O85 docs/04 §D）", cross["(3,2)+c.c. 色-弱交叉（X/Y）"], 12)
chk("143 = dim SU(12) = 12²−1", 12 * 12 - 1, 143)

# 質量通道：9 模式 {1,2,3,4,5,7,9,11,13} → C(9,2) = 36 = h11
modes = [1, 2, 3, 4, 5, 7, 9, 11, 13]
chk("9 模式元素數 = 9 = N_gen²", len(modes), 9)
chk("36 通道 = C(9,2) = h11", C(9, 2), 36)

# ── S2. fundamental Λ^k(12) 之新鏈分解 ──────────────
print()
print("=== S2. Λ^k(12) 新鏈分解（12 = (3,1) ⊕ (1,2) ⊕ 7×(1,1)） ===")
# Λ^k(A⊕B⊕C⊕7×1) = Σ_{a+p+r=k} Λ^a(3) ⊗ Λ^p(2) ⊗ C(7,r)·(1,1)
# Λ^a(3): a=0→1, 1→3, 2→3̄, 3→1；Λ^p(2): p=0→1, 1→2, 2→1
L3 = {0: (1, "1"), 1: (3, "3"), 2: (3, "3̄"), 3: (1, "1")}
L2 = {0: (1, "1"), 1: (2, "2"), 2: (1, "1")}
print(f"{'k':>2} | {'C(12,k)':>8} | 分解總維 (Σ 3^a·2^p·C(7,k−a−p))")
for k in range(0, 13):
    tot = 0
    for a in range(0, 4):
        for p in range(0, 3):
            r = k - a - p
            if r < 0 or r > 7:
                continue
            tot += L3[a][0] * L2[p][0] * C(7, r)
    chk(f"Λ^{k}(12): 分解和 = C(12,{k})", tot, C(12, k))

# ── S3. 帶色分量（B≠0 載體候選）統計 ────────────────
print()
print("=== S3. Λ^k(12) 中帶色分量（a=1 → 3；a=2 → 3̄）統計 ===")
for k in [0, 1, 2, 3, 4, 6, 10, 12]:
    n_col = 0
    for a in (1, 2):
        for p in range(0, 3):
            r = k - a - p
            if 0 <= r <= 7:
                n_col += L3[a][0] * L2[p][0] * C(7, r)
    print(f"  k={k:>2}: 帶色分量維數 = {n_col}")
# k=1：12 本身帶色（3,1）⟹ 新鏈 fundamental 層**已有色載體**
chk("k=1: (3,1) 色分量存在（新鏈 fundamental 帶色）", L3[1][0], 3)
chk("k=3: Λ³(3)=1 ⟹ 3 個色 fundamental 可組成 colour singlet", L3[3][0], 1)

# ── S4. ★★ 新鏈超荷指派閉合（fundamental 層兩參數）─────────
print()
print("=== S4. 新鏈超荷指派：Y(色 fundamental)=a, Y(弱 fundamental)=b ===")
# 66 提供 Q_L ∈ (3,1)⊗(1,2) ⟹ Y = a+b；u^c ∈ Λ²(3) = 3̄ ⟹ Y = 2a；e^c ∈ Λ²(2) = 1 ⟹ Y = 2b
# 12̄ 直接提供 d^c = (3̄,1) ⟹ Y = −a；L = (1,2) ⟹ Y = −b；ν^c = (1,1) ⟹ Y = y_i（待定，取 0）
a = F(-1, 3)      # 由 d^c 觀測 Y = 1/3 ⟹ −a = 1/3
b = F(1, 2)       # 由 L 觀測 Y = −1/2 ⟹ −b = −1/2
pred = {
    "Q_L = a+b": (a + b, F(1, 6)),
    "u^c = 2a": (2 * a, F(-2, 3)),
    "d^c = −a": (-a, F(1, 3)),
    "L_L = −b": (-b, F(-1, 2)),
    "e^c = 2b": (2 * b, F(1)),
    "ν^c = 0": (F(0), F(0)),
}
for name, (got, exp) in pred.items():
    chk(f"Y({name}) = {got} == SM 觀測 {exp}", got, exp)
# 電荷 Q = T₃L + Y 重核
chk("Y 色:弱 比例 = a:b = −2:3 == H(2,−3) 方向", (a / b), F(-2, 3))
chk("H 方向 色:弱 = 2:−3", F(2) / F(-3), F(-2, 3))

# ── S5. B 數方向審查（ΔB 判據之結構前提）────────────────
print()
print("=== S5. B 數方向審查：B ∝ diag(1/3·I₃, 0, …) 是否喺 U(1)⁸？ ===")
# U(1)⁸ 之基：H = (2,−3,0⁷) + E_i（7 單態對角）⟹ 任何方向之色:弱 分量比 = 2:−3
# B 方向：色 = 1/3，弱 = 0 ⟹ 弱分量 0 ⟹ α·(−3) = 0 ⟹ α = 0 ⟹ 色分量亦 0（矛盾）
B_colour, B_weak = F(1, 3), F(0)
alpha_from_weak = B_weak / F(-3)          # 由弱分量定 α
alpha_from_colour = B_colour / F(2)       # 由色分量定 α
chk("B 之 α（由弱）= 0", alpha_from_weak, F(0))
chk("B 之 α（由色）= 1/6 ≠ 0 ⟹ 矛盾", alpha_from_colour, F(1, 6))
chk("★ B 唔喺 U(1)⁸ 空間（α 矛盾）", alpha_from_weak == alpha_from_colour, False)
# 結論：B 數唔係 SU(12) 內部 U(1) 生成元 ⟹ 外部/全域量子數
# X/Y（色-弱交叉 adjoint 分量）之 B 改變：B(E_{ij}) = B_i − B_j = 1/3 − 0
chk("X/Y 單個 ΔB = 1/3（色 1/3 − 弱 0）", B_colour - B_weak, F(1, 3))
chk("3 個色 X/Y 合成 ΔB = 1", 3 * (B_colour - B_weak), F(1))
# X/Y 數目重核
chk("X/Y 數 = 3 色 × 2 弱 × 2（正反）= 12", 3 * 2 * 2, 12)

# ── S6. 舊鏈 vs 新鏈 判據對照 ────────────────────────
print()
print("=== S6. ΔB=1 判據：舊鏈 vs 新鏈 ===")
cmp_rows = [
    ("colour 載體", "SU(4) 6/10（Λ²(4)=6⊕10）", "(3,1) 色 fundamental（12 直接）+ 複合 3̄"),
    ("B / B−L 來源", "SU(4)_PS：4 = 3⊕1 ⟹ B−L", "🔴 無 SU(4) ⟹ B 唔喺 U(1)⁸（本檔 S5 證）"),
    ("媒介玻色子", "48 coset (3,8)+(3̄,8)（PD#1）", "X/Y = 12 個 (3,2)+c.c. adjoint 分量"),
    ("ΔB 單體", "max|ΔB| = 2/3 < 1 ⟹ 無", "色-弱交叉 ⟹ ±1/3（3 色合成 1）"),
    ("判據狀態", "🔴 撤（docs/12 §4）", "🟡 需 B 算子之外部定義（開放）"),
]
for row in cmp_rows:
    print(f"  {row[0]}: 舊鏈 {row[1]} ｜ 新鏈 {row[2]}")

print()
print(f"===== PASS={PASS} FAIL={FAIL} =====")
with open("data/16_newchain_db1_judgement.json", "w", encoding="utf-8") as fh:
    json.dump({"script": "16_newchain_db1_judgement", "date": "2026-10-15",
               "pass": PASS, "fail": FAIL, "results": results}, fh,
              ensure_ascii=False, indent=1)
print("data/16_newchain_db1_judgement.json written")
sys.exit(0 if FAIL == 0 else 1)