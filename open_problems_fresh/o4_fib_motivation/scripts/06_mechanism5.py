#!/usr/bin/env python3
"""
06_mechanism5.py — ε 截斷機制 + 3 級起源
==========================================
O4 機制 5: ε³ 截斷 = 3 代 → 3 級?

深入檢查:
1. ε 嘅權力結構: ε⁵/8 = RMS (已知), ε³ = 3 代截斷
2. 3 級 = F₅/F₄/F₃ 對應 3 個「可分辨」等級
3. 等級數 = 3 嘅深層原因

關鍵新視角:
- AIC/BIC 顯示 continuous φ^-d 係最佳 (1 參數)
- 3 級只係 continuous 嘅整數閉合取樣 (d=0,1,2)
- 真正嘅「3」係: 冷斑 F₅ + 鄰居 F₄ + 基態 F₃
  = 源 + 第一層 + 其餘 (唔係 3 個獨立級)
"""
import numpy as np
import math

phi = (1 + 5**0.5) / 2
eps = (1/phi) / 4
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

print("=" * 72)
print("O4 06: ε 截斷機制 — 點解 3 級?")
print("=" * 72)

# ---------- 1. ε 權力結構 ----------
print("\n=== ε 權力結構 ===")
print(f"ε = φ⁻¹/4 = {eps:.6f}")
for k in range(1, 8):
    print(f"ε^{k} = {eps**k:.6e} (×1e6 = {eps**k*1e6:.3f})")

print(f"\nε⁵/8 = RMS = {eps**5/8:.6e}")
print(f"5ε⁵/8 = 冷斑 = {5*eps**5/8:.6e}")

# ---------- 2. 3 級嘅結構來源 ----------
print("\n=== 3 級結構: 源 + 第一層 + 基態 ===")
print("""
模型 3lv: A(d) = F₅ (d=0), F₄ (d=1), F₃ (d≥2)

結構解讀 (唔係 3 個獨立級):
  d=0: 冷斑 = 源 (F₅ = 5×RMS, 已閉合 5ε⁵/8)
  d=1: 第一鄰居層 (F₄ = 3×RMS)
  d≥2: 基態 (F₃ = 2×RMS)

3 個「級」其實 = 3 個拓撲地位:
  1. 源 (群恆等元素 e)
  2. 第一層 (生成元)
  3. 其餘 (複合 word length)
""")

# ---------- 3. 對比 2+1 = 3 ----------
print("\n=== 2+1 = 3 (data + inversion) ===")
print("IDCM 核心: 3 代 = 2 bits + 1 inversion")
print("對應: 3 級 = 源 + 第一層 + 基態")
print("")
print("操作維 (K_Chain): 2+1 = 3 代 (SM)")
print("尺度維 (A₅): 2+1 = 3 級 (BFS 距離 0,1,≥2)")
print("→ 同一結構 2+1=3 喺兩個維度重現!")

# ---------- 4. ε³ 截斷 ----------
print("\n=== ε³ 截斷 ===")
print(f"ε³ = {eps**3:.6f}")
print(f"ε³ 量級 = {eps**3*30:.3f} μK (×30 μK RMS)")
print(f"→ ε³×RMS 級別 = 0.11 μK << 噪聲 45.8 μK")
print(f"→ ε³ 截斷: 低於 ε³ 嘅結構無法分辨 → 統一為 F₃")

# 等級的 ε 表達
print(f"\n=== 等級嘅 ε 表達 ===")
print(f"F₅ = 5: 5ε⁵/8 (已知)")
print(f"F₄ = 3: 3ε⁵/8 = (F₅-F₂)ε⁵/8")
print(f"F₃ = 2: 2ε⁵/8 = F₂ε⁵/8")
print(f"F₅ = F₄ + F₃ → 5ε⁵/8 = 3ε⁵/8 + 2ε⁵/8 ✅ 疊加!")
print(f"→ 冷斑振幅 = 鄰居層 + 基態層 (干涉疊加)")

# ---------- 5. 關鍵: 點解係 F₃=2 做基態? ----------
print("\n=== 點解 F₃=2 做基態? ===")
print(f"候選: F₂=1 (30 μK) 定 F₃=2 (60 μK)?")
print(f"觀測 d≥2 層: |T| mean = 30.5, 36.6, 30.8, 27.7, 23.6, 36.4 μK")
print(f"→ 全部 ≈ 30 μK = F₂ = 1×RMS 附近!")
print(f"→ 觀測顯示基態其實係 F₂=1×RMS, 唔係 F₃=2×RMS!")
print(f"\n⚠️ 重要修正: 3lv 模型 (F₃=60 μK 基態) 過高")
print(f"   d≥2 觀測 mean ≈ 30 μK = F₂ (1×RMS)")
print(f"   5lv 模型 (F₂=30 基態) 更貼近!")

# ---------- 6. 重新評估 ----------
print("\n=== 重新評估: 真正嘅等級結構 ===")
print(f"5lv χ² = 29.6 < 3lv χ² = 51.4 (節點級)")
print(f"→ 5 級 (F₅/F₄/F₃/F₂/F₁) 確實更好")
print(f"→ 但 continuous φ^-d χ² = 33.5 (1 參數) 幾乎一樣好")
print(f"→ BIC: continuous 37.6 << 5lv 50.1")
print(f"→ 結論: 連續 φ 衰減係本質, 離散 Fibonacci 係整數閉合")

# 儲存
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o4_fib_motivation/data/mechanism5.txt', 'w') as f:
    f.write("# O4 06: ε 截斷機制\n")
    f.write(f"# ε={eps:.6f}, ε³={eps**3:.6e}, ε⁵/8={eps**5/8:.6e}\n")
    f.write(f"# F₅=5ε⁵/8 (冷斑), F₄=3ε⁵/8, F₃=2ε⁵/8, F₂=1ε⁵/8\n")
    f.write(f"# 5 = 3 + 2 (F₅ = F₄ + F₃, 疊加)\n")
    f.write(f"# 觀測 d≥2 |T| ≈ 30 μK = F₂, 3lv 基態 60 μK 過高\n")
    f.write(f"# BIC: continuous=37.6 < 3lv=63.7 < 5lv=50.1 < 6lv=54.6\n")
    f.write(f"# 結論: 連續 φ 衰減 + 整數閉合 = Fibonacci 等級\n")
print(f"\n✅ 已存: data/mechanism5.txt")
