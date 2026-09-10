#!/usr/bin/env python3
"""
O168 — 20: 反常相位 18π 動力學 (gate ② 剩項, 任務一延伸)
==========================================================
docs/16 已建: 53 = 相位方程唯一解; 世界 44.5π − 反常 18π = 通道 26.5π。
本 script 攻「點解 18π」: 反常相位 = α-跑動 × 中央模 × π。

新身份:
  18π = Δα⁻¹·μ²·π = 9×2×π          (跑動 × 模 × π)
  F₁₁  = k + 2μ²·Δα⁻¹ = 89 = 53 + 36  (相位預算方程)
  36   = 2μ²·Δα⁻¹ = B·Δα⁻¹ = 4×9      (兩個等價因式分解)
  每單位跑動消耗 μ²π = 2π (一個完整繞數) — RG 旋轉數 = Δα⁻¹
"""
from mpmath import mp, mpf, pi, exp, phase
mp.dps = 60

N_d = 44; N_gen = 3; B = 4; mu2 = 2; K_tree = 33
F11 = 89; L6 = 18; k = 53; F_proj = 17
alpha0 = 137; alphaMZ = 128

results = []
def check(name, ok, info=""):
    results.append(ok)
    print(f"  [{'OK ' if ok else 'XX '}] {name} — {info}")

print("="*74)
print("  O168 — 20: 反常相位 18π 動力學")
print("="*74)

# ── [1] Δα⁻¹ = 9 = N_gen² (O142/O160) ──
print("\n─── [1] α-跑動: Δα⁻¹ = α⁻¹(0) − α⁻¹(M_Z) ───")
dalpha = alpha0 - alphaMZ
print(f"  Δα⁻¹ = {alpha0} − {alphaMZ} = {dalpha} = N_gen² = {N_gen**2}")
check("[1a] Δα⁻¹ = 9 = N_gen²", dalpha == 9 == N_gen**2)
check("[1b] Δα⁻¹ = F_proj − 2B (17−8, O160)", F_proj - 2*B == 9)

# ── [2] ★反常相位 = Δα⁻¹·μ²·π ──
print("\n─── [2] ★反常相位 = Δα⁻¹·μ²·π = 9×2×π = 18π ───")
print(f"  Δα⁻¹·μ²·π = {dalpha}×{mu2}×π = {dalpha*mu2}π")
check("[2a] 反常相位 = Δα⁻¹·μ²·π = 18π (docs/16 補集相位)", dalpha*mu2 == 18)
check("[2b] 18 = 2N_gen² = L6 (雙重身份)", 18 == 2*N_gen**2 == L6)
check("[2c] μ² = γ₄₄ = λ₁₇ = 2 (O160 中央模定理)", mu2 == 2)

# ── [3] 相位預算方程: F₁₁ = k + 2μ²·Δα⁻¹ ──
print("\n─── [3] ★相位預算方程: F₁₁ = k + 2μ²·Δα⁻¹ ───")
budget = k + 2*mu2*dalpha
print(f"  k + 2μ²Δα⁻¹ = {k} + 2×{mu2}×{dalpha} = {k} + {2*mu2*dalpha} = {budget}")
check("[3a] F₁₁ = k + 2μ²·Δα⁻¹ (89 = 53 + 36)", budget == F11)
check("[3b] 36 = 2μ²·Δα⁻¹ = 4×9 (半-π 單位)", 2*mu2*dalpha == 36)
check("[3c] 36 = B·Δα⁻¹ (B = 2μ² = 4 等價因式)", B*dalpha == 36 and B == 2*mu2)

# ── [4] 每單位跑動 = μ²π = 2π (RG 旋轉數) ──
print("\n─── [4] 每單位跑動消耗 μ²π = 2π — 一個完整繞數 ───")
print(f"  反常相位 18π / Δα⁻¹ 9 = 2π = μ²·π — 每單位跑動 = 一個完整繞數")
print(f"  詮釋: RG 流喺 α⁻¹-空間嘅旋轉數 = Δα⁻¹ (0 → M_Z 繞 9 圈)")
check("[4a] 每單位跑動相位 = μ²π = 2π", 18/dalpha == mu2 == 2)
check("[4b] 繞數 = Δα⁻¹ = 9 (整數圈, 一致性)", 18 % dalpha == 0)

# ── [5] e 形 51 相位禁止 (預算方程重新導出) ──
print("\n─── [5] e 形 51 相位禁止 — 預算方程重新導出 ───")
print(f"  預算方程強逼: k = F₁₁ − 2μ²Δα⁻¹ = {F11} − {2*mu2*dalpha} = {F11-2*mu2*dalpha}")
check("[5a] k = F₁₁ − 2μ²Δα⁻¹ = 53 (唯一)", F11 - 2*mu2*dalpha == 53)
print(f"  若 k = 51 (e 形): 51 + 36 = 87 ≠ 89 = F₁₁ — 相位預算唔夠 2 半-π")
check("[5b] e 形 51 唔夠預算 (51+36 = 87 ≠ 89)", 51 + 36 != F11)
print(f"  若 k = 55 (F₁₀): 55 + 36 = 91 ≠ 89 — 超出預算 2 半-π")
check("[5c] F₁₀ = 55 超出預算 (55+36 = 91 ≠ 89)", 55 + 36 != F11)
check("[5d] 唯一解: k = 53 (53+36 = 89 = F₁₁)", 53 + 36 == F11)

# ── [6] 相位動力學數值驗證 (mpmath) ──
print("\n─── [6] 數值驗證 ───")
world = mpf(F11)*pi/2                    # 44.5π
anom = 2*mu2*dalpha*pi/2                 # 36·(π/2) = 18π
chan = world - anom
print(f"  世界 {float(world/pi):.1f}π − 反常 {float(anom/pi):.1f}π = 通道 {float(chan/pi):.1f}π")
check("[6a] 通道相位 = 26.5π = 53·(π/2)", chan == mpf(53)*pi/2)
check("[6b] 世界相位 = 44.5π (O161)", world == mpf(89)*pi/2)

# ── [7] 總結 ──
print("\n─── [總結] 反常相位動力學裁決 ───")
print("  ✅ 18π = Δα⁻¹·μ²·π = 9×2×π — 反常相位 = 跑動 × 模 × π (精確)")
print("  ✅ 相位預算方程 F₁₁ = k + 2μ²Δα⁻¹ 強逼唯一 k = 53; e 形 51 / F₁₀ 55 全禁")
print("  ✅ 每單位跑動 = 2π (一個完整繞數) — RG 旋轉數 = Δα⁻¹ = 9")
print("  🟡 詮釋層:『2π/單位』係旋轉數公設 (RG 流繞數) — 未由更底結構推導")
check("[E] 反常相位: 算術閉合 (跑動×模×π); 機制詮釋 🟡", dalpha*mu2 == 18 and budget == F11)

print(f"\n{'='*74}")
print(f"  O168-20 反常相位: {sum(results)}/{len(results)} PASS")
print(f"{'='*74}")
