#!/usr/bin/env python3
"""
★ 爆炸性發現: 邊集前半/後半和 = 已知物理拍頻!
==============================================
前半 (k=1..21): Σ = 1.34282889 = m_s/m_d beat (O35)
後半 (k=22..43): Σ = 0.58578644 = 2−√2 = beat(22,44)
"""
from math import pi, sin, sqrt

N = 44
w = lambda n: 2*sin(pi*n/88)
beat = lambda i,j: abs(w(j)-w(i))
e = [w(k+1)-w(k) for k in range(1,N)]

front = sum(e[:21])   # k=1..21 → 邊 (1,2)..(21,22)
back = sum(e[21:])    # k=22..43 → 邊 (22,23)..(43,44)

print("="*72)
print("1. 前半/後半和嘅身份")
print("="*72)
print(f"前半 (k=1..21) Σ = {front:.10f}")
print(f"後半 (k=22..43) Σ = {back:.10f}")
print(f"總和 = {front+back:.10f} = ω_44 − ω_1 = {w(44)-w(1):.10f}")
print()
print("前半 = Σ_{k=1}^{21} e_k = ω_22 − ω_1 = beat(1,22)!!")
print(f"  驗證: beat(1,22) = {beat(1,22):.10f} {'✅' if abs(front-beat(1,22))<1e-12 else '❌'}")
print("後半 = Σ_{k=22}^{43} e_k = ω_44 − ω_22 = beat(22,44)!!")
print(f"  驗證: beat(22,44) = {beat(22,44):.10f} {'✅' if abs(back-beat(22,44))<1e-12 else '❌'}")

print("\n" + "="*72)
print("2. 呢兩個拍頻嘅身份")
print("="*72)
print(f"beat(1,22) = {beat(1,22):.10f}")
print(f"  → m_s/m_d (O35): m_s/m_d = φ^(10/528)×sin(22)/sin(1) 用嘅就係 d=21 行!")
print(f"  → master_atlas: (1,22) 標記 'm_s/m_d (O35)'")
print(f"  → 即係: 前半邊和 = m_s/m_d 拍頻!")
print()
print(f"beat(22,44) = {beat(22,44):.10f}")
print(f"  → = 2 − √2 = {2-sqrt(2):.10f} (閉合根式!)")
print(f"  → master_atlas: 6 個閉合根式之一")
print(f"  → 即係: 後半邊和 = 2−√2 = beat(22,44)")

print("\n" + "="*72)
print("3. 結構意義: 邊集喺 k=22 分開 = 半節點!")
print("="*72)
print(f"""
  e_1..e_21 (前半) 和 = beat(1,22) = m_s/m_d 拍頻 (O35 物理!)
  e_22..e_43 (後半) 和 = beat(22,44) = 2−√2 (閉合根式)
  
  k=22 = 半節點 (44/2) — 邊集喺度切開!
  
  → 前半 = 「1→22 半鏈」= m_s/m_d
  → 後半 = 「22→44 半鏈」= 2−√2
  → 邊集自然分成兩半, 各自對應已知物理拍頻!
""")

print("="*72)
print("4. 更深: 前半/後半比例")
print("="*72)
print(f"front/back = {front/back:.10f}")
print(f"front/back vs φ = {front/back/((1+sqrt(5))/2):.6f}")
print(f"front/(front+back) = {front/(front+back):.6f} = 69.6%")
print(f"back/(front+back) = {back/(front+back):.6f} = 30.4%")
print(f"front+back = {front+back:.10f} = beat(1,44)")
print(f"beat(1,44) = {beat(1,44):.10f}")
print()
# 檢查其他分界
print("5. 其他分界點會唔會產生物理拍頻?")
print("="*72)
phys = {(1,22):"m_s/m_d", (10,24):"u/d", (8,22):"c/s", (19,33):"t/b",
        (1,18):"m_mu/m_tau", (7,20):"n/p", (30,41):"m_W/m_Z", (19,38):"m_H/m_W"}
for (i,j), name in sorted(phys.items(), key=lambda x: x[0][1]-x[0][0]):
    front_sum = sum(e[i-1:j-1])  # 邊 k=i..j-1
    direct = beat(i,j)
    print(f"  {name:10s} ({i:2d},{j:2d}): 邊和={front_sum:.8f} = beat {direct:.8f} {'✅' if abs(front_sum-direct)<1e-12 else '❌'}")
