#!/usr/bin/env python3
"""
★ 7 嘅身份 — 點解高次數端點 7 係 magic row?
==============================================
發現: 低次數 = 偶數 ∪ {11,33}, 7 係高次數 (gcd=1)
問題: 7 有咩特殊? 令佢成為唯一高次數 magic row
"""
from math import gcd
from collections import Counter

def phi(n):
    r=n; p=2
    while p*p<=n:
        if n%p==0:
            while n%p==0: n//=p
            r-=r//p
        p+=1
    if n>1: r-=r//n
    return r

print("="*72)
print("1. 7 喺數論結構嘅位置")
print("="*72)
print(f"7 = L₄ (Lucas 4)")
print(f"7 = 176/25.14? no")
print(f"7 = 44/6.29? no")
print(f"7 = F₆−1 = 8−1")
print(f"7 = 2³−1 (Mersenne!)")
print(f"176 mod 7 = {176 % 7}")
print(f"44 mod 7 = {44 % 7}")
print(f"φ(7) = {phi(7)} = 6")
print(f"7 係質數? 係")
print(f"176 = 2⁴×11, 7 唔係 176 嘅因子")

print("\n" + "="*72)
print("2. 7 同其他 magic rows 嘅 gcd 關係")
print("="*72)
magic = [7, 14, 20, 22, 33]
for m in magic:
    g = gcd(m, 176)
    print(f"  gcd({m}, 176) = {g}")
print()
print("  7: gcd=1 (高次數)")
print("  14: gcd=2 (deg20)")
print("  20: gcd=4 (deg10)")
print("  22: gcd=22 (deg2)")
print("  33: gcd=11 (deg4)")

print("\n" + "="*72)
print("3. ★ magic rows 嘅 gcd 階梯!")
print("="*72)
print("""
  magic rows: 7, 14, 20, 22, 33
  
  gcd 值: 1, 2, 4, 22, 11
  排序:   1, 2, 4, 11, 22
  對應 deg: 40, 20, 10, 4, 2
  
  ★ magic rows = 176 因子嘅「代表」!
    176 = 2⁴ × 11
    因子: 1, 2, 4, 8, 16, 11, 22, 44, 88, 176
  
  magic 揀咗: 1→7, 2→14, 4→20, 11→33, 22→22
  缺: 8, 16, 44, 88, 176
""")

print("\n" + "="*72)
print("4. ★ 每個 gcd 類別嘅『代表』= magic row!")
print("="*72)
# 每個 gcd 類 n 值
gcd_classes = {}
for n in range(1, 45):
    dd = abs(44-n)
    g = gcd(dd, 176) if dd != 0 else 176
    gcd_classes.setdefault(g, []).append(n)
print("gcd 類別同 magic row 代表:")
rep_map = {1: 7, 2: 14, 4: 20, 11: 33, 22: 22}
for g in sorted(gcd_classes):
    ns = gcd_classes[g]
    magic_rep = rep_map.get(g, "—")
    print(f"  gcd={g:3d} ({len(ns)} 個): {ns}")
    print(f"         magic 代表: {magic_rep}")

print("\n" + "="*72)
print("5. ★ 7 嘅 magic 身份: gcd=1 類別嘅代表!")
print("="*72)
print("""
  gcd=1 類別 (高次數, 20 個): 
    1, 3, 5, 7, 9, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 35, 37, 39, 41, 43
  
  點解 7 係代表而唔係 1/3/5?
  
  可能原因:
  a) 7 = L₄ (Lucas 4) — 唯一 Lucas 數喺類別入面?
  檢查: 1, 3, 7 = Lucas {1,3,7}! 但 11 唔喺 (gcd=11)
  
  b) 7 係類別入面嘅「質數中心」?
  
  c) 7 = m7 anchor — O35 質量公式用 7 做 anchor
     n/p = γ₇/γ₂₀ (O13)
     m_7 = 13.8 MeV (DM)
""")

print("\n" + "="*72)
print("6. Lucas 數喺 gcd=1 類別")
print("="*72)
L = {0:2, 1:1, 2:3, 3:4, 4:7, 5:11, 6:18, 7:29}
gcd1_ns = gcd_classes[1]
lucas_in = [v for v in L.values() if v in gcd1_ns]
print(f"gcd=1 類別: {gcd1_ns}")
print(f"Lucas 數喺入面: {lucas_in} = L₁,L₂,L₄,L₇")
print(f"→ Lucas 4 = 7 係類別入面最大嘅『細 Lucas』(L₇=29 都喺)")
print(f"→ 但 29 都係 gcd=1... 點解唔係 29 做代表?")
print()
print("7 同 29 嘅分別:")
print(f"  7 = L₄, 29 = L₇")
print(f"  7 < 22 (half), 29 > 22")
print(f"  7 喺前半 (n<22), 29 喺後半 (n>22)")
print(f"  7 對應 m7 anchor (DM 13.8 MeV) — 物理角色!")
