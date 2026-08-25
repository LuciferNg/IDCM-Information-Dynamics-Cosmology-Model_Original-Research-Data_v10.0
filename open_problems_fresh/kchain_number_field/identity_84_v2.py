#!/usr/bin/env python3
"""
F₈ = 21 嘅 IDCM 角色 — 84 = B×F₈ 嘅結構基礎
============================================
發現: 84 = 4×21 = B×F₈
問題: F₈ = 21 喺 IDCM 有冇其他身份? 21 係咪真結構數?
"""
from math import pi, sin, gcd, lcm

print("="*72)
print("1. 21 (F₈) 喺 IDCM 嘅出現")
print("="*72)
known_21 = []
# 搜尋已知結構
checks = {
    "F₈ = 21": 21, "3×L₄ = 21": 3*7, "L₅+L₄+L₃ = 22? no": 11+7+4,
    "2N_d/4+10": None, "L₆+L₀+L₁ = 21": 18+2+1, "L₅+L₄+L₂+L₁ = 22": 11+7+3+1,
    "F₇+F₆ = 21": 13+8, "3×F₆+1": 25,
}
for name, val in checks.items():
    if val is not None:
        print(f"  {name} = {val} {'✅ 21!' if val == 21 else ''}")

print()
print("21 喺 master_atlas 已知出現:")
# 從記憶: d=21 行 (m_s/m_d 用 d=21), 21 = L₇−F₆? 29−8
print(f"  d=21 行: m_s/m_d (O35) 用 d=21")
print(f"  21 = 29−8 = L₇−F₆")
print(f"  21 = 33−12 = M−12")
print(f"  21 = 44−23")
print(f"  21 = 88/4 − 1 = 22−1")

print("\n" + "="*72)
print("2. ★ 21 對 × 4 = 84 嘅對偶詮釋")
print("="*72)
print("""
  88-site Z₂ 對偶: γ_k + γ_{88−k} = 4
  
  84 = 21 對 × 4  = 21 對 × (每對和 = 4)
  
  21 對 = 邊集嘅對偶 pair 數 (m=3..85 奇數)
        = 世界嘅對偶 pair 數 (k=2..42 偶數)
  
  ★ 84 嘅本質 = 「21 個 Z₂ 對, 每對能量 4」
  ★ 21 = 兩條鏈共享嘅對偶對數
  ★ 4 = Z₂ 對偶和 (γ_k + γ_{88−k})
""")

print("\n" + "="*72)
print("3. 21 對嘅幾何 — 點解係 21 而唔係 22?")
print("="*72)
print("""
  88-site 有 44 對 (k=1..44 ↔ 88−k), 但:
    k=44: 自對偶 (γ_44 = 2, 只計一次)
    k=88: 冇對偶 (γ_88 = 4, 單獨)
  → 真正「對」: 43 對 (k=1..43, 唔計 44 自對偶)
  
  世界 (偶數 k): 2,4,...,42 → 21 對
  觀察者 (奇數 k): 1,3,...,43 → 22 對
  差: 世界 21 對 vs 觀察者 22 對
  
  ★ 世界少一對 (因為 k=44 自對偶佔咗偶數位!)
  ★ 21 對 = 世界嘅對偶數 = 邊集嘅對偶數
  ★ 呢個「21」係世界結構嘅 signature — 唔係巧合
""")

print("\n" + "="*72)
print("4. 驗證: 21 對 = 世界偶數對 = 邊集奇數對")
print("="*72)
world_pairs = [(k, 88-k) for k in range(2, 44, 2)]
edge_pairs = [(m, 88-m) for m in range(3, 86, 2) if m < 88-m]
print(f"世界偶數對 (k=2..42): {len(world_pairs)} 對")
print(f"  索引: {world_pairs[0]} .. {world_pairs[-1]}")
print(f"邊集奇數對 (m=3..43): {len(edge_pairs)} 對")
print(f"  索引: {edge_pairs[0]} .. {edge_pairs[-1]}")
# 對數統計
odd_full = [(m, 88-m) for m in range(1, 44, 2)]
print(f"觀察者奇數對 (m=1..43): {len(odd_full)} 對")
print(f"→ 觀察者 22 對 = 邊集 21 對 + (1,87) 對")

print("\n" + "="*72)
print("5. 84 嘅結構身份總結")
print("="*72)
print(f"""
  ★ 84 = 21 對 × 4 = B×F₈ = 4×21
     但更根本: 84 = 「世界/邊集共享嘅對偶核心」
     
  21 嘅結構角色:
    世界 21 對 (偶數 2..42)
    邊集 21 對 (奇數 3..43)
    F₈ = 21 (Fibonacci)
    3×L₄ = 21 (Lucas 組合)
    
  ⚠️ 誠實: 84 = 21×4 係「21 對」嘅直接結果
     21 嘅 Fibonacci 身份 (F₈) 係 bonus, 唔係推導
     真正結構: 88-site 對偶 → 世界/邊集各 21 對
""")
