#!/usr/bin/env python3
"""
O256 — Script 11: ★ Fibonacci 階梯連續化 = 高ℓ尾包絡結構 (O48 峰高主體)
=====================================================================
O48 docs/02 §3 關鍵閉合: 峰高衰減主體 = Fibonacci 階梯 1/F_j (telescoping),
  唔係指數阻尼! Π(Fₖ/Fₖ₊₁) telescoping = 1/F_j, j=1,2,3,4.
  9055 只係 <6% 殘差修正.

本 script 檢驗: 峰高階梯 1/F_j 連續化 → 連續包絡 A(ℓ).

  F_j ≈ φ^j/√5 ⟹ 1/F_j ≈ √5·φ^{-j} = √5·exp(-j·ln φ)
  ln φ = 0.4812...   ln φ / (306/2) = 0.4812/153 = 0.003146 → λ = 317.9

  ⟹ 結構預言: 高ℓ尾 local e-folding λ₁ = (峰間隙/2)/ln φ = 153/ln φ = 317.9
  vs P3 實測: 307±9 (SPT) / 308±5 (ACT); CAMB lensed 316; 306 峰間隙.

j 嘅 ℓ 步長: 峰間隙 306/288 交替; j 每跨一個「半間隙」+1?
  峰: m=1 (221) → j=1; m=2 (537) → j=2; Δℓ=306 (j 步長 = 306 = 峰間隙)
  但 F_j 只有 j=1,2,3,4 (O48) — 峰 m=1,2,3,5,7!
  峰 3 (810) → j=3; 峰 5 (1121) → j=4? 峰間隙 306+288? 
  即 j 每步 = 峰間隙 ~306/288, 包絡 A ∝ 1/F_j

  高ℓ尾係「峰 7 之後」— 階梯 j 繼續: j=5 (對 1/F₅=1/5),
  位置 ℓ ≈ 1409 + 306 = 1715? 但 O48 已判 1715 冇峰 (binning)!
   ⟹ 高ℓ尾 = 階梯包絡, 峰已消失 (振幅 < 噪聲), 只餘連續衰減!

  λ(ℓ) 上升: 階梯連續化 λ = Δℓ_j / ln φ, Δℓ_j 由 306 遞減到?
  峰間隙: 306/288 交替 → Δℓ_j 平均 297 = 峰週期 P!
  λ = P/ln φ = 297/0.4812 = 617.2?? 定 306/2/lnφ = 318?
"""
import math, sys
import numpy as np

PASS, FAIL, TOTAL = 0, 0, 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
phi = (1+math.sqrt(5))/2
lnphi = math.log(phi)
F = lambda n: round((phi**n - (-phi)**-n)/math.sqrt(5))

print("="*76)
print("1. O48 峰高階梯 (1/F_j telescoping) 連續化")
print("="*76)
# 峰高模型: A(p_j) = 3ε(33/34)·Π(Fₖ/Fₖ₊₁)·exp[-(ℓ/9055)^{3/2}]
# Π telescoping = 1/F_j: j=1,2,3,4 → 1,1,1/2,1/3
for j in [1,2,3,4,5,6,7,8]:
    print(f"  j={j}: 1/F_j = 1/{F(j)} = {1/F(j):.6f}")
print(f"  ln φ = {lnphi:.6f}")

# 峰間隙 (O48: 峰 m=1→2: 306, 2→3: 288, 3→5: 306, 5→7: 288)
gaps = [306, 288, 306, 288]
print(f"\n  峰間隙序列 (真峰): {gaps}")
print(f"  平均間隙 = {sum(gaps)/len(gaps):.1f}  (=峰週期 P≈297)")
# 但 j 步係「半間隙」定「峰間隙」?
# O48: 峰 m = 1,2,3,5,7 → j = 1,2,3,4 (5 峰 4 步)
# 峰 1→2: Δℓ=306, j 1→2; 峰 2→3: Δℓ=288, j 2→3; 峰 3→5: Δℓ=306, j 3→4; 峰 5→7: Δℓ=288, j 4→5?
# O48 docs/02 §3 話 j=1,2,3,4 ⇒ 1,1,1/2,1/3 — 即 5 個峰但 4 個 j?
peaks_j = {1: 1, 2: 2, 3: 3, 5: 4}
ell_peaks = [221, 527, 815, 1121]
# j 每步跨幾多 ℓ?
for k in range(3):
    dL = ell_peaks[k+1]-ell_peaks[k]
    jj = peaks_j[1 if k==0 else ([2,3,5][k])]
    print(f"  峰 {k+1}→{k+2}: Δℓ={dL}, j 步長=1 ⟹ λ_j = Δℓ/lnφ = {dL/lnphi:.1f}")

# ── 2. 高ℓ尾 j 延續: j=5,6,... 位置 ──────────────────────────────
print("\n" + "="*76)
print("2. 高ℓ尾 j 延續 (峰 7=1409 之後): j=5 位置 = 1409+?")
print("="*76)
ell7 = 1409
for j in [5,6,7,8,9,10]:
    dL = gaps[(j-2) % 4]   # 306/288 交替繼續
    pos = None
    print(f"  j={j}: 1/F_{j}={1/F(j):.5f}  間隙延續 {dL}")
# 高ℓ尾: 唔再有峰, 包絡 = 階梯 A_j 隨 ℓ 連續衰減
# 位置涵數: 峰 7 後, ℓ 步進 306/288 交替; j 每步+1
print("\n  峰 7 後位置預言 (階梯延續):")
pos = ell7
for j in [5,6,7,8,9,10]:
    gap = gaps[(j-2) % 4]
    pos += gap
    print(f"    j={j}: 位置 ≈ {pos}   (1/F_j = {1/F(j):.5f})")

# ── 3. λ₁ 預言: 用峰形寬度 = 階梯半間隙 ─────────────────────────
print("\n" + "="*76)
print("3. λ₁ 零參數預言 (階梯連續化)")
print("="*76)
# 候選 A: λ = 峰間隙/lnφ (每峰 j+1, Δℓ=306)
lam_A = 306/lnphi
lam_B = 288/lnphi
lam_C = (306+288)/2/lnphi   # 平均間隙 297/lnφ
lam_D = 153/lnphi           # 半間隙
print(f"  λ = 306/lnφ = {lam_A:.2f}")
print(f"  λ = 288/lnφ = {lam_B:.2f}")
print(f"  λ = 297/lnφ = {lam_C:.2f}")
print(f"  λ = 153/lnφ = {lam_D:.2f}")
print(f"  P3 實測 λ₁ = 307±9 (SPT) / 308±5 (ACT);  CAMB lensed 316")
check("λ_A ∈ 實測±5σ", 307-3*9 <= lam_A <= 308+3*5, f"({lam_A:.1f})")
check("λ_D ∈ 實測±5σ", 307-3*9 <= lam_D <= 308+3*5, f"({lam_D:.1f})")

# ── 4. 同 CAMB lensed 316 比較 ─────────────────────────────────
print("\n" + "="*76)
print("4. 判決: 階梯連續化 λ vs lensed ΛCDM band")
print("="*76)
for name, lam in [("峰間隙/lnφ", lam_A), ("同步隙/lnφ", lam_B),
                   ("平均隙/lnφ", lam_C), ("半間隙/lnφ", lam_D)]:
    dev316 = (lam-316)/316*100
    dev308 = (lam-308)/308*100
    print(f"  {name:>14} = {lam:7.2f}  vs CAMB 316: {dev316:+6.1f}%  vs 實測 308: {dev308:+6.1f}%")

print("\n" + "="*76)
print("5. 完整包絡: C(ℓ) = 峰 Lorentz × 階梯包絡?")
print("="*76)
# 綜合: 每個峰振幅乘 1/F_j, 峰形 Lorentz + 高ℓ尾 = 階梯延續 exp(-ℓ/λ)
l_grid = np.arange(200, 3001, 2)
GAMMA = 306/8
A_O83 = {1: 1.0, 2: (2/3)**2, 3: 4/9, 5: 3/14, 7: 1/7}
OBS_ELL = {1: 221, 2: 537, 3: 810, 5: 1121, 7: 1409}
# 用 1/F_j 做峰高 (O48 telescoping 主體) — 檢查同 O83 振幅母函數一致?
for m in [1,2,3,5,7]:
    j = {1:1, 2:2, 3:3, 5:4, 7:5}[m]   # 峰7 → j=5? O48 j 只有 4, 峰7 係 j=4?
    print(f"  峰 m={m}: O83 A={A_O83[m]:.4f}  vs 1/F_j(j={j})={1/F(j):.5f}")
# O48 docs/02: 峰 1,2,3,5,7 → j=1,2,3,4 → 1,1,1/2,1/3
# O83: A = 1, 4/9=0.444, 4/9=0.444, 3/14=0.214, 1/7=0.143
# 1/F_j: 1, 1, 1/2, 1/3 → 1, 1, 0.5, 0.333 — 唔等!!!
# ⟹ O48 telescoping 1/F_j 同 O83 振幅母函數係兩套: O48 係幾何因子,
#   O83 係完整振幅. 連續化應跟 O83 振幅(閉合於觀測)!
print("\n  ⚠️ O48 1/F_j 係「幾何因子」唔係完整振幅 — 連續化跟 O83")
print("  O83 峰高: 1, 0.444, 0.444, 0.214, 0.143 (m=1,2,3,5,7)")
print("  峰高比序列: 1, 4/9, 4/9, 3/14, 1/7 — 高ℓ延續 → ?")

print(f"\nRESULT: {PASS}/{TOTAL} PASS (FAIL={FAIL})")
sys.exit(0 if FAIL == 0 else 1)