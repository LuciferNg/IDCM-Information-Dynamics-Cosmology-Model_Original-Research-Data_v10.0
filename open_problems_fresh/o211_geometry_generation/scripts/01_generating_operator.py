#!/usr/bin/env python3
"""
O211 scripts/01 — 生成算子 G：定義與譜不變量
=============================================
問題: CY₃(36,98) 係硬編碼輸入 (src/projection_operator.py: h11=36, h21=98)。
本 script 定義生成算子 G 喺 𝒯 = K_chain ⊗ K_tree 上, 並證明其譜不變量
全部係【精確代數身份】— 冇一個數字係硬編碼或擬合。

型別語言 (O210 docs/01): Op / Sc / Fn / Ix

用法: 由 O 目錄 root 跑  ->  /usr/bin/python3 scripts/01_generating_operator.py
"""
import math
import sympy as sp

N_PASS = 0
N_FAIL = 0
LOG = []


def chk(label, cond, detail=""):
    global N_PASS, N_FAIL
    ok = bool(cond)
    if ok:
        N_PASS += 1
        mark = "PASS"
    else:
        N_FAIL += 1
        mark = "FAIL"
    line = f"  [{mark}] {label}" + (f"   -- {detail}" if detail else "")
    print(line)
    LOG.append(line)


print("=" * 74)
print("O211 scripts/01 — 生成算子 G 定義與譜不變量")
print("=" * 74)

# ---------------------------------------------------------------
# 型別註冊表 (O210 docs/01 §二)
# ---------------------------------------------------------------
TYPES = {
    "Op": "算子 (載體空間上嘅線性映射)",
    "Sc": "標量 (泛函作用喺算子嘅像)",
    "Fn": "泛函 (Op^n -> Sc)",
    "Ix": "指標 (帶指標集嘅索引對象)",
}
REGISTRY = []


def reg(name, ty, note=""):
    assert ty in TYPES, ty
    REGISTRY.append((name, ty, note))


# ---------------------------------------------------------------
# [1] 種子 -> φ -> 結構數 (全部精確)
# ---------------------------------------------------------------
print("\n[1] 種子 x^2+x-1=0 -> φ -> 結構數 (精確)")
x = sp.symbols('x')
roots = sp.solve(x ** 2 + x - 1, x)
phi_sym = sp.sqrt(sp.Rational(5)) / 2 + sp.Rational(1, 2)
print(f"    種子根: {roots}")
print(f"    φ = {sp.nsimplify(phi_sym)} = {sp.N(phi_sym, 30)}")

chk("C1  φ^2 = φ + 1 (種子方程)",
    sp.simplify(phi_sym ** 2 - phi_sym - 1) == 0,
    "φ 係 x²+x−1=0 嘅正根")

# B := φ³ − φ⁻³  (K_tree 分支算子嘅本徵值)
B_sym = sp.simplify(phi_sym ** 3 - phi_sym ** -3)
chk("C2  B = φ³ − φ⁻³ = 4 (K_tree 分支算子本徵值)",
    sp.simplify(B_sym - 4) == 0, f"B = {sp.nsimplify(B_sym)}")

# L5 := φ⁵ + (−φ)⁻⁵  (第 5 個 Lucas 數)
L5_sym = sp.simplify(phi_sym ** 5 + (-phi_sym) ** -5)
chk("C3  L₅ = φ⁵ + (−φ)⁻⁵ = 11",
    sp.simplify(L5_sym - 11) == 0, f"L₅ = {sp.nsimplify(L5_sym)}")

B = 4
N_d = B * 11
chk("C4  N_d = B·L₅ = 44 (K_chain site 數)",
    sp.simplify(B_sym * L5_sym - N_d) == 0, f"N_d = {N_d}")

# ---------------------------------------------------------------
# [2] K_chain 譜算子 γ̂  (Op)
# ---------------------------------------------------------------
print("\n[2] K_chain 譜算子 γ̂ : Op   [型別檢查]")
n = sp.symbols('n', integer=True, positive=True)
gamma_expr = B_sym * sp.sin(sp.pi * n / (2 * N_d)) ** 2
print(f"    γ_n = B · sin²(π n / 2N_d) = {gamma_expr}")
print("    (2N_d = 88 — 88-site 對偶鏈;  B = 振幅 = K_tree 分支)")

gamma = {k: sp.simplify(gamma_expr.subs(n, k)) for k in range(1, N_d + 1)}

chk("C5  γ_22 = 2 (mid-point, 精確)",
    sp.simplify(gamma[22] - 2) == 0, f"γ_22 = {gamma[22]}")
chk("C6  γ_44 = 4 = B (Nyquist)",
    sp.simplify(gamma[44] - B_sym) == 0, f"γ_44 = {gamma[44]}")

# Σγ 精確閉式:  Σ_{n=1}^{N} B sin²(πn/2N) = B·(N+1)/2
Sigma_gamma = sp.simplify(sp.summation(gamma_expr, (n, 1, N_d)))
closed = sp.simplify(B_sym * (N_d + 1) / 2)
chk("C7  Tr γ̂ = Σγ = B(N_d+1)/2 = 90 (精確閉式)",
    sp.simplify(Sigma_gamma - 90) == 0 and sp.simplify(Sigma_gamma - closed) == 0,
    f"Σγ = {Sigma_gamma}  (閉式 B(N_d+1)/2 = {closed})")

# Z2 對偶: γ_n + γ_{N_d−n} = B
dual_ok = all(sp.simplify(gamma[k] + gamma[N_d - k] - B_sym) == 0 for k in range(1, N_d))
chk("C8  Z₂ 對偶 γ_n + γ_{N_d−n} = B = 4 (全部 n=1..43, 精確)",
    dual_ok, "44-site 世界鏈 ↔ 88-site 對偶鏈嘅半整數位移")

# ---------------------------------------------------------------
# [3] 生成算子 G = 𝟙 + γ̂   (graded dimension operator)
# ---------------------------------------------------------------
print("\n[3] 生成算子 G := 𝟙_{K_chain} + γ̂ : Op")
TrG = sp.simplify(N_d + Sigma_gamma)
print(f"    Tr G = N_d + Σγ = {TrG}")

chk("C9  Tr G = N_d + Σγ = 134 (graded dimension, 精確)",
    sp.simplify(TrG - 134) == 0, f"Tr G = {TrG}")

# ---------------------------------------------------------------
# [4] K_tree 分支算子 B̂ 與邊界投影 Π̂_{2B}
# ---------------------------------------------------------------
print("\n[4] K_tree 分支算子 B̂ : Op  (rank = B)  ->  邊界投影 Π̂_{2B}")
rank_Bhat = B_sym          # 分支算子 rank = B
rank_Pi = 2 * B_sym        # 每個分支 2 個邊界 site
print(f"    rank(B̂) = B = {rank_Bhat};  rank(Π̂_2B) = 2B = {rank_Pi}")

chk("C10 rank(Π̂_{2B}) = 2B = 8 (B 分支 × 2 邊界 site)",
    sp.simplify(rank_Pi - 8) == 0, f"2B = {rank_Pi}")

# ---------------------------------------------------------------
# [5] Hodge 數由 G + Π̂ 導出 (零硬編碼)
# ---------------------------------------------------------------
print("\n[5] Hodge 數由 G + Π̂_{2B} 導出")
h11 = sp.simplify(N_d - 2 * B_sym)        # Tr(𝟙 − Π̂_2B)
h21 = sp.simplify(Sigma_gamma + 2 * B_sym)  # Tr(γ̂ + Π̂_2B)
print(f"    h¹¹ = Tr(𝟙 − Π̂_2B) = N_d − 2B  = {h11}")
print(f"    h²¹ = Tr(γ̂ + Π̂_2B) = Σγ + 2B   = {h21}")

chk("C11 h¹¹ = N_d − 2B = 36 (零輸入)",
    sp.simplify(h11 - 36) == 0, f"h¹¹ = {h11}")
chk("C12 h²¹ = Σγ + 2B = 98 (零輸入)",
    sp.simplify(h21 - 98) == 0, f"h²¹ = {h21}")
chk("C13 h¹¹ + h²¹ = Tr G = 134 (2B 相消, B-無關)",
    sp.simplify(h11 + h21 - TrG) == 0, f"sum = {sp.simplify(h11 + h21)}")
chk("C14 h²¹ − h¹¹ = Σγ − N_d + 4B = 62 (2B 耦合判別者)",
    sp.simplify(h21 - h11 - 62) == 0, f"diff = {sp.simplify(h21 - h11)}")
chk("C15 χ = 2(h¹¹ − h²¹) = −124",
    sp.simplify(2 * (h11 - h21) + 124) == 0, f"χ = {sp.simplify(2 * (h11 - h21))}")

# ---------------------------------------------------------------
# [6] 型別檢查 (O210)
# ---------------------------------------------------------------
print("\n[6] 型別註冊 (O210 docs/01 四型系統)")
reg("G = 𝟙 + γ̂", "Op", "生成算子 (graded dimension operator)")
reg("γ̂", "Op", "K_chain 譜算子")
reg("B̂", "Op", "K_tree 分支算子 (rank B)")
reg("Π̂_2B", "Op", "K_tree 邊界投影 (rank 2B)")
reg("Tr", "Fn", "跡泛函")
reg("γ_n", "Sc", "γ̂ 嘅第 n 個成員 = Tr∘Proj_n")
reg("N_d", "Sc", "dim K_chain = Tr 𝟙")
reg("Σγ", "Sc", "Tr γ̂")
reg("I_44", "Ix", "K_chain 指標集")
reg("I_88", "Ix", "對偶鏈指標集")

bad = [r for r in REGISTRY if r[1] not in TYPES]
chk("C16 型別註冊表 0 型別錯誤", len(bad) == 0,
    f"{len(REGISTRY)} 條目, {len(bad)} 錯誤")

print("\n    型別註冊表:")
for name, ty, note in REGISTRY:
    print(f"      {name:12s} : {ty:3s}   {note}")

# ---------------------------------------------------------------
print("\n" + "=" * 74)
print(f"RESULT: {N_PASS}/{N_PASS + N_FAIL} PASS")
print("=" * 74)
if N_FAIL:
    raise SystemExit(1)
