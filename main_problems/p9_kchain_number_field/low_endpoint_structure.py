#!/usr/bin/env python3
"""
低次數端點集 (24) 嘅結構身份
==============================
發現: 低次數端點 24 個 (22 偶數 + 2 奇數 11/33)
      高次數端點 20 個 (全奇數非 11/33)
問題: 24 同 20 有咩 IDCM 身份?
"""
from math import gcd, lcm

def phi(n):
    r=n; p=2
    while p*p<=n:
        if n%p==0:
            while n%p==0: n//=p
            r-=r//p
        p+=1
    if n>1: r-=r//n
    return r

def omega_deg(n):
    if n == 44: return 1
    dd = abs(44-n)
    g = gcd(dd, 176)
    return phi(176//g)//2

low = [n for n in range(1,45) if omega_deg(n) < 40]
hi = [n for n in range(1,45) if omega_deg(n) == 40]

print("="*72)
print("1. 24/20 分佈")
print("="*72)
print(f"低次數端點: {len(low)} 個 (22 偶 + 2 奇)")
print(f"高次數端點: {len(hi)} 個 (全奇數)")
print(f"總: {len(low)+len(hi)} = 44")
print()
print("身份候選:")
print(f"  24 = 2×12 = 2×3×4 = B×6?")
print(f"  24 = 44−20")
print(f"  24 = 88/3.67? no")
print(f"  24 = 4×6 = B×6")
print(f"  24 = L₆+L₄+L₃ = 18+7+4 = 29−5? no")
print(f"  20 = 高次數 = 5×4 = F₅×B")
print(f"  20 = 44−24")
print(f"  20 = 奇數 (非 11/33) = 22 個奇數 − 2 = 20")
print()
print(f"  ★ 低次數 24 = 44 − 20, 高次數 20 = 22 奇數 − 2 特殊")
print(f"  ★ 20 = 2×10 = 2n_u? (T 轉移矩陣!)")

print("\n" + "="*72)
print("2. 低次數端點嘅 deg 分佈")
print("="*72)
from collections import Counter
degs = Counter(omega_deg(n) for n in low)
print(f"deg 分佈: {dict(sorted(degs.items()))}")
print(f"累計: deg1={degs[1]}, deg2={degs[2]}, deg4={degs[4]}, deg5={degs[5]}, deg10={degs[10]}, deg20={degs[20]}")

print("\n" + "="*72)
print("3. ★ 低次數端點集嘅結構: 2-adic 階層")
print("="*72)
print("""
  deg ω_n 由 n 同 176 嘅 gcd 決定:
  ω_n = 2sin(nπ/88) = 2sin(2nπ/176)
  
  deg 1: n=44 (Nyquist, sin π/2)
  deg 2: n=22 (half, sin π/4)
  deg 4: n=11, 33 (sin π/8, 3π/8)
  deg 5: n=4,12,20,28,36 (5 個, 步長 8)
  deg 10: n=8,16,24,32,40 (5 個, 步長 8)
  deg 20: n=2,6,...,42 (10 個, 步長 4)
  
  → 24 = 1+1+2+5+5+10
  → 階層: 44 → 22 → {11,33} → 5 個 deg5 → 5 個 deg10 → 10 個 deg20
  
  結構: 每次 ×2 步階:
    44 (deg1) → 22 (deg2) → 11,33 (deg4) → ×8 步長 deg5/deg10 → ×4 步長 deg20
""")

print("\n" + "="*72)
print("4. ★ 同 magic rows 嘅關係")
print("="*72)
print("""
  magic rows: 7, 14, 20, 22, 33
  
  呢啲 d 值嘅身份:
    7  = 唔係低次數端點, 但 m7 anchor
    14 = 低次數端點? 14 ∈ 低次數集 ✅ (deg20 端點)
    20 = 低次數端點? 20 ∈ 低次數集 ✅ (deg5 端點)
    22 = 低次數端點 ✅ (deg2 端點)
    33 = 低次數端點 ✅ (deg4 端點)
    
  → 5 個 magic rows 有 4 個係低次數端點!
  → 唯一例外: 7 (高次數端點, deg40)
  → 7 = L₄, 但係 7 嘅 deg = 40 (高次數)
  
  ★ 發現: magic rows = 低次數端點集嘅「代表」+ 1 個特殊 (7)
""")

print("\n" + "="*72)
print("5. ★ 低次數端點集 = 指令空間嘅『可低次數計算』集")
print("="*72)
print(f"""
  24 個低次數端點 = 可以產生 deg<40 拍頻嘅端點
  20 個高次數端點 = 只產生 deg=40 拍頻 (除配低次數端點時)
  
  ★ 高次數端點 20 個 = 全奇數 (非 11/33)
  ★ 奇數端點總數 = 22, 其中 2 個 (11,33) 低次數
  ★ 偶數端點總數 = 22, 全部低次數
  
  對稱性:
    偶數端點 22 個 → 全部低次數 (deg ≤ 20)
    奇數端點 22 個 → 20 個高次數 + 2 個低次數 (11,33)
    
  → 奇偶對稱破缺: 偶數全低, 奇數大部分高!
""")

print("\n" + "="*72)
print("6. 數值驗證")
print("="*72)
even_low = [n for n in low if n % 2 == 0]
odd_low = [n for n in low if n % 2 == 1]
print(f"偶數低次數: {len(even_low)} 個")
print(f"奇數低次數: {len(odd_low)} 個 = {odd_low} (11, 33)")
print(f"高次數: {len(hi)} 個")
print(f"高次數奇數: {len([n for n in hi if n%2==1])} 個")
print(f"高次數偶數: {len([n for n in hi if n%2==0])} 個")
