#!/usr/bin/env python3
"""
O57 — 探索 01: 結構數全譜系身份驗證
=====================================
核心問題: 946 beats / 134 moduli / rank 109 / 66 態 / 198? / 272?
呢啲數字嘅結構身份係咩? 佢哋點樣自然由 K_Chain 44-site 生成?

關鍵洞見候選:
  G1: 946 = C(44,2) = dim Λ²(R⁴⁴) — beat 空間 = 2-form 空間
  G2: 134 = Nd + Σγ = 44 + 90 — moduli 空間 = site ⊕ energy
  G3: rank 109 = ? — 投影算子嘅有效維度
  G4: 66 = 3×22 = ? — 三代 × 半鏈
  G5: 109 = 134 − 25? 25 = 5² = L₅×2+3?
"""
import math, json
import numpy as np
from itertools import combinations

phi = (1 + math.sqrt(5)) / 2
Nd = 44

print("=" * 72)
print("O57 探索 01: 結構數全譜系身份")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 核心結構數 ============
print("\n[1] 核心結構數 (由 x²+x−1=0 → φ 派生)")
B = 4          # K_Tree 分支
L5 = 11        # Lucas 5
L6 = 18        # Lucas 6
F6 = 8         # Fibonacci 6
F7 = 13
F8 = 21
F10 = 55
F11 = 89
F12 = 144
L10 = 123

print(f"  B={B}, L5={L5}, L6={L6}, F6={F6}, F7={F7}, F8={F8}")
print(f"  F10={F10}, F11={F11}, F12={F12}, L10={L10}")

# K_Chain
gamma = np.array([4 * math.sin(math.pi * n / 88)**2 for n in range(1, Nd+1)])
S_gamma = gamma.sum()  # 90
print(f"  Nd={Nd}, Σγ={S_gamma}")

# CY3
h11, h21 = 36, 98
chi = -124
print(f"  h11={h11}, h21={h21}, χ={chi}")

# Beat 空間
C44_2 = Nd * (Nd-1) // 2
print(f"\n  C(44,2) = {C44_2}")

# ============ 2. 946 嘅身份 ============
print("\n[2] 946 = dim Λ²(R⁴⁴) = C(44,2)")
check("946 = C(44,2)", C44_2 == 946)
check("946 = dim Λ²(R⁴⁴)", C44_2 == Nd*(Nd-1)//2)

# parity 分解: even beats (n+m even) vs odd beats (n+m odd)
# even beats: (even,even) ∪ (odd,odd) → C(22,2)+C(22,2) = 2×C(22,2) = 462
# odd beats:  (even,odd) → 22×22 = 484
even_beats = 2 * (22*21//2)   # 462
odd_beats = 22 * 22            # 484
print(f"\n  Parity 分解:")
print(f"    Even beats (n+m even): 2×C(22,2) = {even_beats}")
print(f"    Odd beats  (n+m odd):  22×22 = {odd_beats}")
print(f"    Total: {even_beats + odd_beats}")
check("even+odd = 946", even_beats + odd_beats == 946)
check("even beats = 462", even_beats == 462)
check("odd beats = 484", odd_beats == 484)

# Z₂ charge 分解
# z2 = +1 if (n+m) even else -1 → same as parity!
z2_plus = even_beats   # 462
z2_minus = odd_beats   # 484
print(f"  Z₂ charge 分解 (同 parity):")
print(f"    z2=+1: {z2_plus}, z2=-1: {z2_minus}")

# ============ 3. 462/484 嘅結構身份 ============
print("\n[3] 462 同 484 嘅結構身份")
# 462 = 2×C(22,2) = C(22,2)+C(22,2)
# 484 = 22²
print(f"  462 = 2×C(22,2) = {2*231}")
print(f"  484 = 22² = {22**2}")
print(f"  22 = Nd/2 = 44/2")
print(f"  462 = 3×154? 154 = 2×7×11")
print(f"  462 mod 44 = {462 % 44}")
print(f"  462/44 = {462/44}")
print(f"  484/44 = {484/44}")
print(f"  484 = 44×11 = Nd×L5?  {44*11}")
print(f"  462 = 44×10.5? 唔整數")
print(f"  462+484 = 946")

# 重要: 462 = C(22,2)+C(22,2) = dim Λ²(R²²) ⊕ Λ²(R²²)
# 484 = 22×22 = dim (R²² ⊗ R²²) — 兩個 half-chain 嘅張量積!
print(f"\n  候選身份:")
print(f"    462 = 2×dim Λ²(R²²) (兩個 half-chain 各自嘅 2-form)")
print(f"    484 = dim (R²²⊗R²²) (兩個 half-chain 嘅張量積 = 混合 2-form)")
check("462 = 2×C(22,2)", 462 == 2 * (22*21//2))
check("484 = 22²", 484 == 22**2)

# ============ 4. 134 嘅身份 ============
print("\n[4] 134 = Nd + Σγ = 44 + 90")
print(f"  134 = {Nd} + {int(S_gamma)}")
check("134 = 44+90", 134 == Nd + S_gamma)
print(f"  134 = 2×67? 67 prime")
print(f"  134 mod 44 = {134 % 44}")
print(f"  134 = 66×2 + 2 = {66*2+2}")
print(f"  134 = 109 + 25? 25 = 5²")
print(f"  134 = 4×33 + 2 = {4*33+2}")
print(f"  33 = M (K_Tree 層數)")

# ============ 5. rank 109 嘅身份 ============
print("\n[5] rank 109 嘅結構身份")
# 109 係修正版 P̂ (scripts/14) 嘅秩
# 109 = 134 − 25? 25 = 5² = (L5−6)²? 或者 = 36−11?
print(f"  109 = 134 − 25")
print(f"  25 = 5²")
print(f"  25 = 44 − 19? 19 prime")
print(f"  25 = 90 − 65? 65 = 5×13")
print(f"  109 = 44 + 65? 65 = 5×13 = 5×F7")
print(f"  109 = 36 + 73? 73 prime")
print(f"  109 = 3×36 + 1 = {3*36+1}")
print(f"  109 = 2×44 + 21 = {2*44+21}")
print(f"  21 = F8 = 第 8 個 Fibonacci")
print(f"  109 = 2Nd + F8 = 88 + 21 = {88+21}")
check("109 = 2Nd + F8", 109 == 2*44 + 21)

# 其他分解
print(f"  109 = 90 + 19? 19 prime")
print(f"  109 = 62 + 47? 47 prime")
print(f"  109 = 66 + 43? 43 prime")
print(f"  109 = 55 + 54 = F10 + 3×L6?  {55 + 54}")
check("109 = F10 + 3L6", 109 == 55 + 54)

# ============ 6. 66 嘅身份 ============
print("\n[6] 66 = 3×22 同 C(12,2)")
print(f"  66 = 3×22 (3 代 × Nd/2)")
print(f"  66 = C(12,2) (12 維空間嘅 2-form 數)")
print(f"  66 = C(12,2): {12*11//2}")
check("66 = 3×22", 66 == 3*22)
check("66 = C(12,2)", 66 == 12*11//2)
print(f"  12 = h11/3 = 36/3")
print(f"  22 = Nd/2")

# ============ 7. 新數字: 198, 272 ============
print("\n[7] 新結構候選")
# 946 → 198? 272?
print(f"  946 − 2×374? 唔整數")
print(f"  946 = 44×21.5? 唔整數")
print(f"  946 mod 33 = {946 % 33}  (33 = K_Tree 層數)")
print(f"  946 mod 22 = {946 % 22}")
print(f"  946/22 = {946/22} = 43")
check("946 = 22×43", 946 == 22*43)
print(f"  946 = 43×22 = (Nd−1)×(Nd/2)!")
print(f"  43 = Nd−1, 22 = Nd/2")
print(f"  946 = (Nd−1)·Nd/2 = C(44,2) ✓ 自然")

# 946 = Σ_{n=1}^{43} n (triangular!)
print(f"  946 = T(43) = 43×44/2 (triangular number)")
check("946 = T(43)", 946 == 43*44//2)

# 272 = ?
print(f"\n  272 = ?")
print(f"  272 = 16×17")
print(f"  272 = 2×136")
print(f"  272 = 4×68")
print(f"  272 = 8×34")
print(f"  272 = 44×6.18...? 唔整數")
print(f"  272 = 2×(134+2) = 272?  {2*136}")
print(f"  272 = 134×2 + 4 = {134*2+4}")
print(f"  272 = 2h11 + 2h21 + 4?")
print(f"  272 = 2×134 + 4 = 2×(h11+h21) + 2B?  {2*134 + 8}")
print(f"  272 = 2×134 + 4, 4 = B")

# 198 = ?
print(f"\n  198 = ?")
print(f"  198 = 2×99")
print(f"  198 = 44×4.5? 唔整數")
print(f"  198 = 2×(36+62) = {2*98}")
print(f"  198 = 2×99, 99 = h21+1")
print(f"  198 = 2h21 + 2 = 196+2")
print(f"  198 = 134 + 64? 64 = 2⁶")
print(f"  198 = 90 + 108? 108 = 6×18 = 6L6")

# ============ 8. Beat 空間嘅代數結構 ============
print("\n[8] Beat 空間 = Λ²(R⁴⁴) 嘅子結構")
# 每個 beat (n,m) = 2-form e_n ∧ e_m
# 44-dim 空間 R⁴⁴ split: R²² ⊕ R²² (even/odd sites 或 quadrant 1-2 / 3-4)
# Λ²(R⁴⁴) = Λ²(R²²⊕R²²) = Λ²(R²²) ⊕ Λ²(R²²) ⊕ (R²²⊗R²²)
# dim: 231 + 231 + 484 = 946 ✓✓✓
dim_Lambda2_R22 = 22*21//2
print(f"  Λ²(R⁴⁴) = Λ²(R²²⊕R²²)")
print(f"           = Λ²(R²²) ⊕ Λ²(R²²) ⊕ (R²²⊗R²²)")
print(f"  dim = {dim_Lambda2_R22} + {dim_Lambda2_R22} + {22*22} = {dim_Lambda2_R22*2 + 22*22}")
check("Λ²(R⁴⁴) 分解 = 946", dim_Lambda2_R22*2 + 22*22 == 946)
print(f"  ⭐ 2-form 空間自然分解: 462 (even) + 484 (odd)")
print(f"  ⭐ Even beats (462) = Λ²(R²²) ⊕ Λ²(R²²) — 同一 half-chain 內")
print(f"  ⭐ Odd beats  (484) = R²²⊗R²² — 跨 half-chain 混合")

# ============ 9. Hodge 對應 ============
print("\n[9] Hodge 對應候選")
# CY₃ Hodge diamond:
#        h⁰⁰ = 1
#     h¹⁰ = 0   h⁰¹ = 0
#  h²⁰ = 0   h¹¹ = 36   h⁰² = 0
# h³⁰ = 1  h²¹ = 98  h¹² = 98  h⁰³ = 1
#      h³¹ = 0   h²² = 0
#           h³³ = 1
# 2-forms: H^{1,1} = 36 (Kähler)
# 3-forms: H^{2,1} + H^{1,2} = 196, H^{3,0}+H^{0,3} = 2
print(f"  CY₃ Hodge diamond:")
print(f"    h¹¹ = 36 (2-forms, Kähler)")
print(f"    h²¹ = 98 (3-forms, complex structure)")
print(f"    h¹² = 98 (3-forms, anti-holomorphic)")
print(f"    2×(h²¹+h¹²) = {4*98}? 唔, h²¹+h¹² = 196")
print(f"    b₂ = h¹¹ = 36")
print(f"    b₃ = 2×(1+h²¹) = 2×99 = 198  ← 198!!")
check("b₃ = 2(1+h²¹) = 198", 2*(1+98) == 198)
print(f"    ⭐ 198 = b₃ = third Betti number!")
print(f"    ⭐ 272 = b₂ + b₃ + b₄ + ...?")
print(f"    b₂ = 36, b₃ = 198")
print(f"    b₂+b₃ = 234")
print(f"    272 − 234 = 38")
print(f"    272 = 36 + 198 + 38? 38 = ?")
print(f"    272 = 2×134 + 4 = 2(h11+h21) + B")

# ============ 10. 投影維度關係 ============
print("\n[10] 投影維度關係總結")
print(f"  Beat 空間:      dim Λ²(R⁴⁴) = 946")
print(f"  Moduli 空間:    h¹¹+h²¹ = 134 = 44+90")
print(f"  Kähler 2-forms: h¹¹ = 36 = 2×18 = 2L₆")
print(f"  CPX 3-forms:    h²¹ = 98 = 44+54 = B×L₅ + 3L₆")
print(f"  b₃ (3-cycle):   198 = 2(1+h²¹) = 2×99")
print(f"  χ = 2(h¹¹−h²¹) = −124")
print(f"  b₂+b₃+b₄:      36+198+36 = 270")

# ============ 總結 ============
print("\n" + "=" * 72)
print("探索 01 總結:")
print("=" * 72)
print(f"""
  ✅ 946 = C(44,2) = dim Λ²(R⁴⁴) — beat 空間係 2-form 空間!
     Parity 分解:
       even (462) = 2×Λ²(R²²)  (half-chain 內)
       odd  (484) = R²²⊗R²²    (跨 half-chain)
  ✅ 134 = Nd + Σγ = 44 + 90 — moduli = site ⊕ energy
  ✅ 198 = b₃ = 2(1+h²¹) — third Betti number
  ✅ 66 = 3×22 = C(12,2)
  ✅ 109 = 2Nd + F8 = 88 + 21 = F10 + 3L6

  關鍵結構:
  - beat 空間自然 = Λ²(R⁴⁴), 2-form 空間
  - CY₃ 嘅 Hodge 結構 (2-forms, 3-forms) 對應 K_Chain 投影
  - b₃ = 198 = 2(1+h²¹) 係 3-cycle 嘅完整維度
""")

results = {
    "test": "O57 探索 01: 結構數身份",
    "946": {"identity": "C(44,2) = dim Λ²(R⁴⁴)", "parity_split": [462, 484],
            "even": "2×Λ²(R²²)", "odd": "R²²⊗R²²"},
    "134": "Nd + Σγ = 44 + 90",
    "109": "2Nd + F8 = 88+21 = F10+3L6",
    "66": "3×22 = C(12,2)",
    "198": "b₃ = 2(1+h²¹)",
    "272": "2(h11+h21) + B? 待驗證",
    "passed": passed, "failed": failed
}
with open("data/01_structure_numbers.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 探索 01 完成!")
