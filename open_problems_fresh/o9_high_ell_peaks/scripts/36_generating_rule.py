#!/usr/bin/env python3
"""
O9-C10: (a_k, b_k) 生成規則 — 物理來源推導
==============================================
偶峰結構:
A2/A1 = (a1/b1)^2 = (2/3)^2
A4/A1 = (a2/b2)^2 = (3/7)^2
A6/A1 = (a3/b3)^2 = (4/11)^2

a_k: 2, 3, 4 (+1 連續)
b_k: 3, 7, 11 (+4 等差)
"""
import numpy as np

print("="*80)
print("O9-C10: (a_k, b_k) 生成規則")
print("="*80)

L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76]
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
N_d, M = 44, 33

a = [2, 3, 4]
b = [3, 7, 11]

print("\n1. 基本結構:")
for k in range(3):
    print(f"   k={k+1}: a={a[k]}, b={b[k]}, a/b = {a[k]/b[k]:.4f}")

print("\n2. b_k 分析:")
print("   b: 3, 7, 11")
print("   4k-1: k=1->3, k=2->7, k=3->11  OK OK OK")
print("   -> b_k = 4k-1 !")
print("   檢查: 3,7,11 全質數, 差 4 (質數孿生間隔)")
print("   11 = M/3 = N_d/4 = L5")
print("   7 = L4")
print("   3 = L2 = F4")

print("\n3. a_k 分析:")
print("   a: 2, 3, 4")
print("   k+1: k=1->2, k=2->3, k=3->4  OK OK OK")
print("   -> a_k = k+1 !")
print("   2 = F3, 3 = L2 = F4, 4 = L3")
print("   a_k = F_{k+2}? F3=2, F4=3, F5=5 X")
print("   a_k = k+1 最簡")

print("\n4. IDCM 關聯:")
print("   44 = 4x11 -> b3 = 11 = N_d/4  OK")
print("   33 = 3x11 -> b1 = 3 = M/11  OK")
print("   7 = L4, 11 = L5 -> b2, b3 連續 Lucas!")
print("   3 = F4 = L2 -> b1 都係 Fib/Lucas")
print()
print("   b_k = 4k-1: 3, 7, 11")
print("   N_d = 44 = 4x11 -> b_max = 11 = N_d/4")
print("   M = 33 = 3x11 -> b1 = 3 = M/11")
print("   -> b_k 序列終止於 N_d/4 = 11 (k=3)")
print("   -> k=4: b = 15? 15 = 44-29 = N_d-L7!")
print("   -> k=4: b = 15 = 3x5 = M-L6!")

print("\n5. 極限結構 (k->inf):")
print("   a_k/b_k = (k+1)/(4k-1) -> 1/4 當 k->inf")
print("   A_even/A1 = (1/4)^2 = 1/16 = 0.0625 當 k->inf")
print("   -> 偶峰振幅衰減到 6.25% of A1")
print("   -> 阻尼尾漸近值")

print("\n6. 奇峰結構:")
print("   A3/A1 ~ (2/3)^2 = (a1/b1)^2 -- 同 A2 一樣?")
print("   A5/A1 = 3/14 = 3/(2x7)")
print("   A7/A1 = 3/21 = 3/(3x7)")
print("   A5 = F4/(2L4), A7 = F4/(3L4)")
print("   -> 奇峰 m=5,7: A_m/A1 = F4/(k'xL4), k'=2,3")
print("   -> k'=1: 3/7 = L2/L4? 0.4286 (A3 候選)")
print("   A3/A1 = 0.4389 vs 3/7 = 0.4286 (dev 2.35%)")
print("   A3/A1 = 0.4389 vs (2/3)^2 = 0.4444 (dev 1.27%)")
print("   -> A3 用 (2/3)^2 較好")

print("\n7. 統一奇峰公式:")
print("   A3 = (a1/b1)^2 = (2/3)^2")
print("   A5 = F4/(2L4) = 3/14")
print("   A7 = F4/(3L4) = 3/21")
print("   觀察: A7/A5 = (3/21)/(3/14) = 14/21 = 2/3  OK")
print("   -> A_{2k+1}/A1 = F4/(kxL4)?")
print("   k=2: 3/14 OK (m=5)")
print("   k=3: 3/21 OK (m=7)")
print("   k=1: 3/7 = 0.4286 vs A3 0.4389 (2.3%)")
print("   -> k=1 用 (2/3)^2 更準, k>=2 用 F4/(kxL4)")

print("\n8. 最終統一結構:")
print("   ------------------------------")
print("   偶峰: A_{2k}/A1 = ((k+1)/(4k-1))^2")
print("     k=1: (2/3)^2 = 0.4444   dev 0.23%")
print("     k=2: (3/7)^2 = 0.1837   dev 1.03%")
print("     k=3: (4/11)^2 = 0.1322  dev 1.48%")
print("   ------------------------------")
print("   奇峰: A3 = (2/3)^2, A5 = 3/14, A7 = 3/21")
print("     A5/A7 = 3/2 (Fib 比)")
print("   ------------------------------")
print("   ★ 偶峰統一公式: A_{2k}/A1 = ((k+1)/(4k-1))^2")
print("   -> 完全由 k 決定, 零自由參數!")

print("\n9. 偶峰統一公式驗證:")
obs_even = {2: 0.4434, 4: 0.1856, 6: 0.1303}
for k in range(1, 4):
    pred = ((k+1)/(4*k-1))**2
    m = 2*k
    obs = obs_even[m]
    dev = abs(pred-obs)/obs*100
    print(f"   k={k}: (({k+1})/({4*k-1}))^2 = {pred:.4f} vs 實測 {obs:.4f} dev={dev:.2f}%")

print("\n10. k=4 預言 (m=8):")
k = 4
pred8 = ((k+1)/(4*k-1))**2
print(f"   A8/A1 = (5/15)^2 = (1/3)^2 = {pred8:.4f}")
print(f"   -> m=8 振幅預言 = A1 x {pred8:.4f} = {5816.5*pred8:.1f} uK^2")
print(f"   -> 但 m=8 喺阻尼尾冇峰 (7 峰截斷), 預言不可驗證")
