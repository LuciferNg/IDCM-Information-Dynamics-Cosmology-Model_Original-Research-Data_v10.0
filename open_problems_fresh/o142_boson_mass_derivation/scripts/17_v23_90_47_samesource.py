#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O142 v23 - 90/47 同源測試: 「譜身份」137=Σγ+α_GUT⁻¹ 係咪 tautology?

背景: 用戶提出 137 嘅「影身份」= Z_cr=1/α（branch point 逆推，Zα=1 奇點），
譜身份 (90+47) 可能係「同義反覆」——90 同 47 唔係獨立結構源。

測試: 將 90 同 47 各自嘅 O56/O89 operator 身份展開，
檢查有冇共同根源（B/2 對稱？共享基本量？）
"""
from fractions import Fraction

# === 基本結構常數（O56/O211 定義）===
N_d   = 44
B     = 4
N_gen = 3
L_4   = 7    # Lucas L_4 = 7（O124 b₀ = L₄ = 7）
L_5   = 11
L_6   = 18
F_7   = 13   # Fibonacci F_7 = 13（O89 用）
K_tree = 33  # O89: 2×K_tree = 66 ⟹ K_tree = 33

print("="*72)
print("A. 90 嘅 operator 身份（O56/O211）")
print("="*72)
# O211 record: Σγ = 90, O56 EXACT; O211 docs: Σγ = B(N_d+1)/2
sig_90a = B*(N_d+1)//2          # = 4×45/2 = 90
sig_90b = B*Fraction(45,2)      # O56: 4×(45/2) = 90 EXACT
sig_90c = 5*L_6                  # O56 D2: Σγ = 5×L₆ = 90
sig_90d = 2*N_d + B//2           # 2×44+2 = 90  ← 拆出 B/2
print(f"  (i)  Σγ = B(N_d+1)/2     = 4×45/2     = {sig_90a}")
print(f"  (ii) Σγ = 4×(45/2)       = 90 EXACT   (O56 scripts/05 B段)")
print(f"  (iii)Σγ = 5·L₆           = 5×18       = {sig_90c}   (O56 D2)")
print(f"  (iv) Σγ = 2N_d + B/2     = 88 + 2     = {sig_90d}   ← B/2 顯式")
print(f"  對齊: 2N_d = κ̃² = 88 (O142 docs/25 閉合幾何量)")
print()

print("="*72)
print("B. 47 嘅 operator 身份（O89 docs/02 問題2）")
print("="*72)
# O89: 47 = 53 − 6; 53 = 2×K_tree − F₇ = 66−13; Δ=6 = B+N_gen−1
p47_a = 2*K_tree - F_7           # 66−13 = 53
p47_b = B + N_gen - 1            # 6
p47_1 = p47_a - p47_b            # 53−6 = 47
print(f"  (i)  53 = 2·K_tree − F₇  = 2×33 − 13 = {p47_a}")
print(f"  (ii) Δ  = B+N_gen−1      = 4+3−1     = {p47_b}  (5 關係一致)")
print(f"  (iii)α_GUT⁻¹ = 53−Δ      = 53−6      = {p47_1}")
L4sq = L_4**2
print(f"  (iv) L₄² = {L4sq}  →  47 = L₄² − B/2 = {L4sq} − 2 = {L4sq - B//2}")
print(f"       驗證: 2×33−13−6 = {p47_1} vs 49−2 = {L4sq - B//2}  {'✓ 同值' if p47_1 == L4sq-B//2 else '✗ 唔同'}")
print()

print("="*72)
print("C. 關鍵: 90 + 47 拆件後 B/2 抵消")
print("="*72)
n90  = 2*N_d + B//2
n47  = L_4**2 - B//2
print(f"  90 = 2N_d + B/2   = 88 + 2")
print(f"  47 = L₄²  − B/2   = 49 − 2")
print(f"  137 = 2N_d + L₄²  = 88 + 49 = {n90+n47}")
print(f"  B/2 抵消!  →  137 = κ̃² + L₄²  = 2N_d + b₀²")
print(f"  其中 κ̃² = 88 (O142 docs/25 幾何閉合), L₄ = 7 = b₀ (O124 QCD β)")
print()

print("="*72)
print("D. 同源判決")
print("="*72)
print("  90 同 47 唔係獨立結構源:")
print("  · 90 = 2N_d + B/2 —— 基本量 2N_d(=κ̃²=88) 帶 +B/2")
print("  · 47 = L₄²  − B/2 —— 基本量 L₄²(=b₀²=49) 帶 −B/2")
print("  · 相加: +B/2 同 −B/2 完全抵消 ⟹ 137 = 2N_d + L₄²")
print("  ·「譜身份」137=90+47 嘅拆件 (Σγ 同 α_GUT⁻¹) 各自吸收 ±B/2")
print("    ——係同一個基本對 {κ̃², L₄²} 嘅 B/2 對稱變體")
print("  ⟹ 拆件帶 K_Tree 對稱擾動, 並非兩個獨立生成源")
print()
print("  ★ 137 嘅『直接身份』: 137 = κ̃² + L₄² = 2N_d + b₀² = 88 + 49")
print("    - κ̃² = 88  全部 O142 自身閉合量 (docs/25)")
print("    - L₄ = 7 = b₀  O124 QCD β 係數 (Tr(T̂^B))")
print("    - 零外部常數, 零拆件")

# === 驗證 ===
ok = True
checks = [
    ("Σγ=B(N_d+1)/2=90", sig_90a == 90),
    ("Σγ=5L₆=90", sig_90c == 90),
    ("Σγ=2N_d+B/2=90", sig_90d == 90),
    ("47=2K_tree−F₇−(B+N_gen−1)", p47_1 == 47),
    ("47=L₄²−B/2", L4sq - B//2 == 47),
    ("137=2N_d+L₄²", n90+n47 == 137),
    ("137=κ̃²+b₀²", 88 + 7**2 == 137),
]
for name, cond in checks:
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    ok = ok and cond
print(f"\nRESULT: {sum(c for _,c in checks)}/{len(checks)} PASS")
import sys; sys.exit(0 if ok else 1)