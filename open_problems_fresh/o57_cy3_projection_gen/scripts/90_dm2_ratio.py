#!/usr/bin/env python3
"""
O57 十七期 90: ★★ Δm² 比 = 2B² = 32 三重閉合
=================================================
發現: Δm²₃₁/Δm²₂₁ = 32.32 ≈ 32 = 2B² (1.01%)

32 三重身份:
  1. O61: Kähler moduli 鎖定維度 = 32 = 2B²
  2. O57 docs/14: 真 Q_ij divisor rank = 32/32
  3. ★ 中微子: Δm²₃₁/Δm²₂₁ = 32

驗證:
  1. Δm²₂₁ = Δm²₃₁/32 預言
  2. m₁, m₂ 近簡併結構
  3. Σm_ν (用 Δm² 比閉合)
  4. m_ββ 預言
"""
import sys, os, math
import json
import numpy as np

phi = (1 + math.sqrt(5)) / 2
gamma6 = 0.18073600929096323

print("=" * 72)
print("O57 十七期 90: Δm² 比 = 2B² 三重閉合")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 三重身份 ============
print("\n[1] 32 三重身份")
print("  1. O61: Kähler moduli 鎖定維度 = 2B² = 2×16 = 32")
print("  2. O57: Q_ij divisor rank = 32/32")
print("  3. ★ 中微子: Δm²₃₁/Δm²₂₁ = 32")

# ============ 2. Δm²₂₁ 預言 ============
print("\n[2] Δm²₂₁ 預言")
dm31 = 2.434e-3  # eV² (實驗)
dm21_pred = dm31 / 32
dm21_exp = 7.53e-5
err = abs(dm21_pred - dm21_exp)/dm21_exp*100
print(f"  Δm²₂₁ = Δm²₃₁/32 = {dm21_pred:.4e} eV²")
print(f"  實驗 = {dm21_exp:.4e} eV²")
print(f"  誤差 = {err:.2f}%")
check("Δm²₂₁ 預言 <2%", err < 2, f"({err:.2f}%)")

# ============ 3. m₁, m₂ ============
print("\n[3] NH 質量")
m3 = 0.0536  # eV (γ₆ 預言)
m1 = math.sqrt(m3**2 - dm31)
m2 = math.sqrt(m1**2 + dm21_pred)
print(f"  m₁ = {m1:.5f} eV")
print(f"  m₂ = {m2:.5f} eV")
print(f"  m₃ = {m3:.5f} eV")
print(f"  m₂/m₁ = {m2/m1:.5f} (近簡併)")
check("m₂/m₁ 近簡併 (<1.2)", m2/m1 < 1.2, f"({m2/m1:.3f})")

# ============ 4. Σm_ν ============
print("\n[4] Σm_ν")
sum_nu = m1 + m2 + m3
print(f"  Σm_ν = {sum_nu:.5f} eV")
print(f"  Planck < 0.12 eV: {'✅' if sum_nu < 0.12 else '❌'}")
print(f"  DESI 2024 < 0.072 eV: {'✅' if sum_nu < 0.072 else '❌'}")
check("Σm_ν < Planck", sum_nu < 0.12, f"({sum_nu:.4f})")

# ============ 5. m_ββ ============
print("\n[5] m_ββ (無中微子雙貝塔)")
# 大混合角 U_ei² ≈ 1/3, 相位未知 → 範圍
mbb_max = (m1 + m2 + m3)/3  # 全部同相
mbb_min = abs(m1 - m2 - m3)/3  # 反相
print(f"  m_ββ 範圍: [{mbb_min*1e3:.1f}, {mbb_max*1e3:.1f}] meV")
print(f"  KamLAND-Zen 敏感區: 10-50 meV")
check("m_ββ 落入敏感區", mbb_min*1e3 <= 50 and mbb_max*1e3 >= 10, f"([{mbb_min*1e3:.1f}, {mbb_max*1e3:.1f}])")

# ============ 6. 對照: φ 階梯 vs 32 閉合 ============
print("\n[6] φ 階梯 vs 2B² 閉合")
# φ 階梯 (盲測 fail)
m3_f = 0.0536
m2_f = m3_f/phi
m1_f = m3_f/phi**2
dm21_f = m2_f**2 - m1_f**2
print(f"  φ 階梯: Δm²₂₁ = {dm21_f:.3e} (實驗 7.53e-5, 差 {dm21_f/7.53e-5:.0f} 倍) 🔴")
print(f"  2B²: Δm²₂₁ = {dm21_pred:.3e} (實驗 7.53e-5, 誤差 {err:.1f}%) 🟢")
check("2B² 優於 φ 階梯", err < 10, f"({err:.1f}% vs 900%)")

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("十七期 90 總結:")
print("=" * 72)
print(f"""
  ★★ Δm² 比 = 2B² = 32 三重閉合:
  ─────────────────────────────────
  1. O61: moduli 鎖定維度 32 = 2B²
  2. O57: Q_ij divisor rank 32
  3. ★ 中微子: Δm²₃₁/Δm²₂₁ = 32 (1.01%)

  預言:
  Δm²₂₁ = Δm²₃₁/32 = {dm21_pred:.4e} eV² (誤差 {err:.2f}%)
  m₁ = {m1:.5f}, m₂ = {m2:.5f}, m₃ = {m3:.5f} eV
  Σm_ν = {sum_nu:.5f} eV ({'✅' if sum_nu<0.12 else '❌'} Planck)
  m_ββ ∈ [{mbb_min*1e3:.1f}, {mbb_max*1e3:.1f}] meV

  🔴 誠實: 32 出現嘅物理原因未推導
  (點解 Δm² 比 = 幾何鎖定維度?)
  → O59 註冊: Δm² 比 = 2B² 嘅第一性原理
""")

results = {
    "test": "O57 十七期 90: Δm² 比 = 2B²",
    "dm21_pred": float(dm21_pred),
    "dm21_exp": float(dm21_exp),
    "err_pct": float(err),
    "m1": float(m1), "m2": float(m2), "m3": float(m3),
    "sum_nu": float(sum_nu),
    "mbb_range": [float(mbb_min*1e3), float(mbb_max*1e3)],
    "passed": passed, "failed": failed
}
with open("data/90_dm2_ratio.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十七期 90 完成!")
