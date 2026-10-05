#!/usr/bin/env python3
"""
邊集 = 半格點採樣 — 同 88-site 對偶鏈嘅關係
=============================================
邊 e_k = 4sin(π/176)·cos((2k+1)π/176) = 4sin(π/176)·cos(π/88·(k+0.5))
→ 半格點採樣! 而 88-site 對偶鏈 γ_k = 4sin²(πk/176), k=1..88

問題: 43 條邊嘅「半格點 cos」同 88-site 對偶鏈「整格點 sin²」有咩關係?
"""
from math import gcd, lcm, pi, sin, cos

N = 44
w = lambda n: 2*sin(pi*n/88)

print("="*72)
print("1. 邊集 (半格點) vs 88-site 譜 (整格點)")
print("="*72)
print("""
  邊:     e_k = 4sin(π/176)·cos((2k+1)π/176), k=1..43  [半格點 k+0.5]
  88譜:   γ_n = 4sin²(nπ/176), n=1..88                 [整格點]
  
  對比:
  e_k = 4sin(π/176)·cos((2k+1)π/176)
      = 4sin(π/176)·sin(π/2 − (2k+1)π/176)
      = 4sin(π/176)·sin((88−2k−1)π/176)  [補角]
      = 4sin(π/176)·sin((87−2k)π/176)
""")

# 驗證補角關係
print("驗證補角:")
for k in [1, 10, 22, 33, 43]:
    e = 4*sin(pi/176)*cos((2*k+1)*pi/176)
    alt = 4*sin(pi/176)*sin((87-2*k)*pi/176)
    print(f"  e_{k:2d} = {e:.10f} = 4sin(π/176)·sin((87−{2*k})π/176) = {alt:.10f} {'✅' if abs(e-alt)<1e-12 else '❌'}")

print("\n" + "="*72)
print("2. 邊嘅 88-site 索引映射")
print("="*72)
print("e_k 對應 88-site 譜嘅第 (87−2k) 個點?")
print("  87−2k: k=1→85, k=10→67, k=22→43, k=33→21, k=43→1")
print("  → 邊集 = 88-site 譜嘅【奇數索引】子集! (85,83,...,1)")
odd_idx = [87-2*k for k in range(1,N)]
print(f"  奇數索引: {odd_idx[0]}..{odd_idx[-1]} = {len(odd_idx)} 個 = 全部奇數 1..85!")
print(f"  → 43 條邊 = 88-site 譜嘅 43 個奇數格點 (1,3,...,85)")

print("\n" + "="*72)
print("3. ★ 關鍵: 邊集 vs 觀察者鏈 (Σγ_odd = 88)")
print("="*72)
# 88-site: γ_n = 4sin²(nπ/176)
# 觀察者 = 奇數 k = 2n−1: Σγ_odd = 88
# 邊索引 = 87−2k = 奇數 (1..85)
# 但 γ 係 sin², 邊係 sin·cos — 唔同?
print("""
  88-site 譜: γ_n = 4sin²(nπ/176)     (能量, sin²)
  邊集:       e_k = 4sin(π/176)·sin(mπ/176), m=87−2k (奇數)
  
  → 邊集唔係 γ 本身, 而係 γ 嘅「平方根交叉項」
  → e_k² = 16sin²(π/176)·sin²(mπ/176) = 4sin²(π/176)·γ_m
  → 邊² = 4sin²(π/176) × 88-site 譜!
""")
for k in [1, 22, 43]:
    e = 4*sin(pi/176)*cos((2*k+1)*pi/176)
    m = 87-2*k
    g = 4*sin(m*pi/176)**2
    print(f"  e_{k:2d}² = {e*e:.12f}, 4sin²(π/176)·γ_{m} = {4*sin(pi/176)**2*g:.12f} {'✅' if abs(e*e - 4*sin(pi/176)**2*g)<1e-15 else '❌'}")

print("\n" + "="*72)
print("4. 邊嘅平方和 (能量)")
print("="*72)
e_list = [4*sin(pi/176)*cos((2*k+1)*pi/176) for k in range(1,N)]
sum_e2 = sum(e*e for e in e_list)
print(f"Σ e_k² = {sum_e2:.10f}")
# 理論: Σcos²((2k+1)π/176) for k=1..43
sum_cos2 = sum(cos((2*k+1)*pi/176)**2 for k in range(1,N))
print(f"Σ cos²((2k+1)π/176) = {sum_cos2:.10f}  (43 個半格點)")
print(f"Σ e_k² = 16sin²(π/176)·Σcos² = {16*sin(pi/176)**2*sum_cos2:.10f}")

# 全 88 格點 vs 43 半格點
sum_cos2_88 = sum(cos((2*k+1)*pi/176)**2 for k in range(0,88))
print(f"全 88 半格點 Σcos² = {sum_cos2_88:.10f} (= 88/2 = 44?)")
print(f"我哋嘅 43 個 = {sum_cos2:.10f}")

print("\n" + "="*72)
print("5. 邊集對稱性 — 到底對稱喺邊?")
print("="*72)
# e_k 對稱於 k=22? e_22 = 0.0496, e_21 = 0.0514, e_23 = 0.0477
# 唔對稱! 但 cos((2k+1)π/176) 對稱於 (2k+1)=88 → k=43.5
print("cos((2k+1)π/176) 對稱軸: (2k+1) = 88 → k = 43.5 (唔係整數!)")
print("→ 43 條邊冇對稱軸 — 因為採樣點係 k+0.5, 對稱軸喺半格點")
print("→ 邊集係『反對稱補集』: e_k ↔ e_{44-k} 唔相等 (見 v2)")

# 真正對稱: 補角
print("\n補角對稱: cos((2k+1)π/176) vs cos((176−(2k+1))π/176)")
for k in [1, 22, 43]:
    c1 = cos((2*k+1)*pi/176)
    c2 = cos((176-(2*k+1))*pi/176)
    print(f"  k={k:2d}: cos({2*k+1:3d}π/176)={c1:.8f} vs cos({176-(2*k+1):3d}π/176)={c2:.8f}")

print("\n" + "="*72)
print("6. 總結: 邊集嘅 88-site 身份")
print("="*72)
print("""
  e_k = 4sin(π/176)·cos((2k+1)π/176)
      = 4sin(π/176)·sin((87−2k)π/176)
  
  ★ 43 條邊 = 88-site 譜嘅奇數子集 (m = 87−2k = 85,83,...,1)
  ★ e_k² = 4sin²(π/176) × γ_m (88-site 能量譜嘅線性標度)
  
  → 邊集係「88-site 對偶鏈嘅奇數半鏈」嘅平方根表示
  → 43 邊 + 44 self loop = 87 = 88 − 1 (差 1 = 種子?)
""")
