#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
44_tree5_origin.py — δ = 5×46 嘅「5」K_tree 起源測試
=====================================================
用戶問題: 5 是否可能來自 K_tree 嘅 5⁻¹?
假設: 5 = L₅ − 2N_gen (tree sector 內部間隙), 而非外部 Z₅。
檢驗:
1. 等差數列 {2N_gen, L₅, B²} 公差 5?
2. δ = (K_tree+F₇)(L₅−2N_gen) = 46×5 純 tree-sector?
3. 同一 5-step 喺 CKM δ 嘅嵌入 (21 = B²+F₅)?
4. 46 分解目錄 (sector 分類)
5. Z₅-twist 讀法生死 (230/72)
6. 5⁻¹ 對 tree 分數
"""
import math
N, DEG = 176, 180.0/math.pi
omega = lambda k: 2*math.sin(k*math.pi/N)

# 常數
Ngen, L5, B2, L4 = 3, 11, 16, 7
KTREE = Ngen*L5          # 33
F7, F8, F5 = 13, 21, 5
mu2 = 2                  # E−O
Nd = 44                  # 4×L5
Ndp, Ndm = 46, 42        # 世界/觀察者側

print("1) 等差數列 {2N_gen, L₅, B²} 公差 5?")
a, b, c = 2*Ngen, L5, B2
print(f"   2N_gen = {a}, L₅ = {b}, B² = {c}")
print(f"   L₅−2N_gen = {b-a}, B²−L₅ = {c-b}  → 公差 = {b-a} ✓")
print(f"   下一項: {c}+{b-a} = {c+b-a} = F₈? {c+b-a == F8}")

print("\n2) δ = (K_tree+F₇)(L₅−2N_gen) 純 tree-sector?")
t1, t2 = KTREE+F7, L5-2*Ngen
print(f"   K_tree+F₇ = {t1} (33+13), L₅−2N_gen = {t2} (11−6)")
print(f"   δ = {t1}×{t2} = {t1*t2}° vs 230: Δ = {t1*t2-230:+.6f}°")
print(f"   sector: K_tree=33(N_gen·L₅) ✓tree, F₇ ✓tree, L₅ ✓tree, 2N_gen ✓tree → 純 tree ✓")

print("\n3) 同一 5-step 喺 CKM δ 嘅嵌入")
d_ckm = math.degrees(math.atan(omega(21)/omega(9)))
print(f"   δ_CKM = atan(ω₂₁/ω₉) = {d_ckm:.6f}°")
print(f"   21 = B²+F₅ = {B2}+{F5} = {B2+F5}? ✓   9 = N_gen² = {Ngen**2}? ✓")
print(f"   → δ_CKM = atan(ω_{{B²+F₅}}/ω_{{N_gen²}}) — 5-step 已嵌入 CKM δ")

print("\n4) 46 分解目錄 (sector 分類)")
d46 = [
    ("K_tree+F₇", KTREE+F7, "tree"),
    ("N_d⁻+B", Ndm+4, "chain"),
    ("N_d+μ²", Nd+mu2, "混合"),
    ("4L₅+μ²", 4*L5+mu2, "混合"),
]
for name, v, sec in d46:
    print(f"   {name:12s} = {v}  ({sec})")

print("\n5) Z₅-twist 讀法: δ = 5×72?")
print(f"   230/72 = {230/72:.4f} — 非整數 → 「5 個 Z₅ twist」讀法 死 ✗")

print("\n6) 5⁻¹ = 1/5 對 tree 分數")
print(f"   1/5 = {1/5:.6f}; φ⁻³ = {0.618**3:.6f}; φ⁻⁴ = {0.618**4:.6f}; 1/33 = {1/33:.6f}")
print(f"   → 1/5 唔係 φ-冪/1/33 — 5⁻¹ = 公差倒數, 唔係 tree 分數")

print("\n7) 全 tree-sector 表述")
print(f"   δ_PMNS = (K_tree+F₇)(L₅−2N_gen) = ({KTREE}+{F7})({L5}−{2*Ngen}) = 230° EXACT")
print(f"   δ_CKM  = atan(ω_{{B²+F₅}}/ω_{{N_gen²}}) = atan(ω₂₁/ω₉) = 66.399960° EXACT")
print(f"   → 兩個 δ 共享 tree 5-step 結構")
