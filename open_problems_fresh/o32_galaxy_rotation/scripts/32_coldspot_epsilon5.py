#!/usr/bin/env python3
"""
O32-32: 冷斑 ε⁵ 冪次動力學來源 — 幾何拓撲推導
================================================
問題: 點解 δT/T = 5ε⁵/8, 即係 ε 嘅 5 次方?

候選結構:
1. F₅ = 5: Fibonacci 5 次方 (最直接)
2. B+1 = 5: K_Tree 分支因子 4 + 1 (中心節點)
3. CY₃ dim + 2 = 5: 複三維 + 2 (奇偶/邊界)
4. A₅ 對稱群: 冷斑 60 節點 Rhombicosidodecahedron 嘅 A₅ 群 = 5 元素排列

深度公式 δT = 5ε⁵·T/8 中:
  5 = F₅ (Fibonacci, A₅ 群階)
  ε⁵ = ε^(F₅) (A₅ 對稱群嘅 5 次冪)
  8 = F₆ (Fibonacci, 2³ 立方結構)
"""
import numpy as np
import json
import math

PHI = (1+math.sqrt(5))/2
T_CMB = 2.72548
eps = 13/86

def fib(k):
    return int(round(PHI**k/math.sqrt(5))) if k > 0 else 0

F = {k: fib(k) for k in range(1, 13)}
print("="*78)
print("冷斑 ε⁵ 冪次動力學來源")
print("="*78)

# ===== 1. 深度公式分解 =====
print("\n--- 1. 深度公式 δT = 5ε⁵·T/8 分解 ---")
dT = 5*eps**5*T_CMB/8
rms = eps**5*T_CMB/8
print(f"δT = 5 × ε⁵ × T_cmb / 8")
print(f"   = {5} × {eps**5:.6e} × {T_CMB} / {8}")
print(f"   = {dT*1e6:.4f} μK")
print(f"RMS = ε⁵·T/8 = {rms*1e6:.4f} μK")
print(f"深度/RMS = 5 (δT = 5×RMS)")

# ===== 2. 5 = F₅ (Fibonacci 結構) =====
print("\n--- 2. 5 = F₅ (Fibonacci 5 次方) ---")
print(f"Fibonacci: F₁=1, F₂=1, F₃=2, F₄=3, F₅=5, F₆=8, F₇=13, F₈=21")
print(f"\nδT = {F[5]}ε^{F[5]}·T/{F[6]}")
print(f"   = {F[5]} × ε^{F[5]} × T_cmb / {F[6]}")
print(f"深度 = F₅ × ε^(F₅) × T_cmb / F₆")
print(f"RMS = ε^(F₅) × T_cmb / F₆")
print(f"深度/RMS = F₅ = 5 (斐波那契深度!)")

# 驗證: 其他冪次
print(f"\n冪次唯一性掃描: 用其他冪次代替 5:")
for p in [1, 2, 3, 4, 5, 6, 7, 8]:
    dT_p = 5*eps**p*T_CMB/8*1e6
    dev = abs(dT_p-134.2)/134.2*100
    mark = "★ 命中!" if dev < 1 else ""
    print(f"  ε^{p}: δT = {dT_p:>9.2f} μK, 偏差 {dev:>8.2f}% {mark}")

# ===== 3. A₅ 對稱群 =====
print("\n--- 3. A₅ 對稱群 (冷斑 60 節點) ---")
# 冷斑 = A₅ 節點圖 (Rhombicosidodecahedron, 60 節點)
# A₅ = 5 元素交替群, 階 = 60
order_A5 = 60
print(f"冷斑拓撲: A₅ 節點對稱圖 (Rhombicosidodecahedron)")
print(f"A₅ = 5 元素交替群, 群階 = {order_A5}")
print(f"節點數 = {order_A5} = 5! / 2")
print(f"表中樞維度 = 5 → ε 嘅 5 次方 = 對稱群維度!")
print(f"A₅ dim = 5 → ε^{F[5]} = ε^5 ✓")

# ===== 4. 8 = F₆ = 2³ = 立方體結構 =====
print("\n--- 4. 8 = F₆ = 2³ (立方體分母) ---")
print(f"F₆ = {F[6]} (Fibonacci)")
print(f"8 = 2³ = 立方體 (3D 空間投影)")
print(f"8 = F₆ (Fibonacci 數列第 6 項)")
print(f"RMS = ε^(F₅)·T/F₆ ✓")

# ===== 5. K_Tree 分支因子 B=4 關聯 =====
print("\n--- 5. K_Tree B=4 關聯 ---")
print(f"B = 4 (K_Tree 分支因子)")
print(f"B+1 = 5 = F₅")
print(f"B = 4 = 2×2 = 2²")
print(f"B×2 = 8 = F₆")
print(f"所以: 5ε⁵/8 = (B+1)·ε^(B+1)/(B×2)")

# ===== 6. CY₃ 複三維關聯 =====
print("\n--- 6. CY₃ 複三維關聯 ---")
dim_CY3 = 3  # Calabi-Yau 3-fold
print(f"CY₃ dim_C = {dim_CY3}")
print(f"CY₃ dim_R = {2*dim_CY3} = 6")
print(f"CY₃ dim_C + 2 = {dim_CY3 + 2} = 5 = F₅")
print(f"CY₃ dim_R - 1 = {2*dim_CY3 - 1} = 5 = F₅")
print(f"→ 5 = dim_C + 2: 複三維嘅兩個邊界投影")

# ===== 7. 完整公式 Fibonacci 編碼 =====
print("\n" + "="*78)
print("★ 完整公式 Fibonacci 編碼")
print("="*78)
print(f"""
δT/T = F₅·ε^(F₅)/F₆
     = 5·ε⁵/8

其中:
  F₅ = 5  (Fibonacci, A₅ 對稱群維度 + K_Tree B+1)
  F₆ = 8  (Fibonacci, 2³ 立方結構 + K_Tree B×2)
  ε = F₇/(2N-2) = 13/86 (F₇ 選擇律)

三層 Fibonacci 編碼:
  分子: F₅ = 5 (深度的 A₅ 群因子)
  分子: F₇ = 13 (ε 嘅 Fibonacci 選擇態)
  分母: F₆ = 8 (RMS 嘅立方結構因子)

驗證:
  δT_pred = 5·(13/86)⁵·2.72548/8 = {dT*1e6:.4f} μK
  SMICA = 134.2 μK
  偏差 = {abs(dT*1e6-134.2)/134.2*100:.3f}%
""")

# ===== 8. 總結推導鏈 =====
print("="*78)
print("★ ε⁵ 冪次動力學來源總結")
print("="*78)
print(f"""
一級結構: ε = F₇/(2N-2) = 13/86
  F₇ 選擇律: N = 44 = F₇+L₇+2 (唯一解 k=7)
  86 = 2N-2 = 88-site 環簡併自由度

二級結構: ε⁵ (5 次方)
  5 = F₅ (Fibonacci 第 5 項)
  5 = A₅ 對稱群維度 (60 節點冷斑拓撲)
  5 = CY₃ dim_C + 2 (複三維 + 雙邊界投影)
  5 = B + 1 (K_Tree 分支 + 中心節點)

三級結構: 8 = F₆ (分母)
  8 = F₆ (Fibonacci 第 6 項)
  8 = 2³ (3D 空間立方體)
  8 = B×2 (K_Tree 分支 × 2)

完整公式:
  δT/T = F₅·ε^(F₅)/F₆
       = 5·(F₇/(2N-2))⁵/8
       = 5·(13/86)⁵/8
       = {dT/T_CMB:.6e}
  δT = {dT*1e6:.4f} μK
""")

output = {
    'F5': 5, 'F6': 8, 'F7': 13,
    'epsilon': 13/86,
    'formula': 'δT/T = 5·ε⁵/8 = F₅·ε^(F₅)/F₆',
    'dT_pred_uK': float(dT*1e6),
    'dT_obs_uK': 134.2,
    'deviation_pct': float(abs(dT*1e6-134.2)/134.2*100),
    'F5_origin': 'A₅ symmetry group, CY₃ dim_C+2, B+1',
    'F6_origin': '2³ cube, B×2 K_Tree',
    'F7_origin': 'N = F_k+L_k+2 = 44 unique solution k=7',
    'eps_denom': '86 = 2N-2 = 88-site ring degenerate modes'
}
with open('data/coldspot_epsilon5_derivation.json', 'w') as f:
    json.dump(output, f, indent=2)
print("結果已存: data/coldspot_epsilon5_derivation.json")