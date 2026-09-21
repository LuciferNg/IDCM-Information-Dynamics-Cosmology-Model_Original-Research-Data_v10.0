#!/usr/bin/env python3
"""
O57 十七期 89: ν 世代結構 — 盲測 fail 後真正機制
====================================================
盲測 (scripts/87) 證明: ν 世代 φ 階梯 (m₂=m₃/φ, m₁=m₃/φ²) FAIL
  Δm²₂₁ 差 9 倍 (6.77e-4 vs 7.53e-5)

真正機制探索:
  1. 用實驗數據反推質量比: Δm²₃₁=2.434e-3, Δm²₂₁=7.53e-5
  2. m₃ 固定 (由 γ₆ 預言 0.0536 eV) → 解 m₁, m₂
  3. 質量比 m₂/m₁ 有冇 γ 結構?
  4. 測試: m_i = m₃ × f_i, f_i 係 γ_n 組合?
"""
import sys, os, math
import json
import numpy as np

phi = (1 + math.sqrt(5)) / 2
gamma6 = 0.18073600929096323

print("=" * 72)
print("O57 十七期 89: ν 世代結構 (盲測後)")
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

# ============ 1. 實驗數據 ============
print("\n[1] 實驗輸入")
dm31 = 2.434e-3  # eV²
dm21 = 7.53e-5   # eV²
m3_fixed = 0.0536  # eV (γ₆ 預言, 非-tautology)

# NH: m₃² - m₁² = dm31, m₂² - m₁² = dm21
m1 = math.sqrt(max(m3_fixed**2 - dm31, 0))
m2 = math.sqrt(m1**2 + dm21)
print(f"  m₃ = {m3_fixed:.5f} eV (γ₆ 預言)")
print(f"  m₁ = {m1:.5f} eV (由 Δm²₃₁ 解)")
print(f"  m₂ = {m2:.5f} eV (由 Δm²₂₁ 解)")
print(f"  m₂/m₁ = {m2/m1:.5f}")
print(f"  m₃/m₂ = {m3_fixed/m2:.5f}")
print(f"  m₃/m₁ = {m3_fixed/m1:.5f}")
print(f"  Σm_ν = {m1+m2+m3_fixed:.5f} eV")

# ============ 2. 質量比結構 ============
print("\n[2] 質量比結構")
print(f"  m₂/m₁ = {m2/m1:.5f}")
print(f"  φ = {phi:.5f}, φ⁻¹ = {1/phi:.5f}")
print(f"  γ₂/γ₁ = {4*math.sin(2*math.pi/88)**2/4*math.sin(math.pi/88)**2:.5f}")
g1 = 4*math.sin(1*math.pi/88)**2
g2 = 4*math.sin(2*math.pi/88)**2
g3 = 4*math.sin(3*math.pi/88)**2
g6 = gamma6
print(f"  γ₁ = {g1:.5f}, γ₂ = {g2:.5f}, γ₃ = {g3:.5f}, γ₆ = {g6:.5f}")
print(f"  γ₂/γ₁ = {g2/g1:.4f}")
print(f"  γ₃/γ₁ = {g3/g1:.4f}")
print(f"  γ₆/γ₃ = {g6/g3:.4f}")
print(f"  γ₆²/γ₁² = {(g6/g1)**2:.4f}")

# 質量比候選
print(f"\n  質量比 vs γ 候選:")
print(f"    m₂/m₁ = {m2/m1:.4f} vs γ₂/γ₁ = {g2/g1:.4f} ({abs(m2/m1-g2/g1)/(g2/g1)*100:.1f}%)")
print(f"    m₂/m₁ = {m2/m1:.4f} vs 4γ₁/γ₂ = {4*g1/g2:.4f}")
print(f"    m₂/m₁ = {m2/m1:.4f} vs √φ = {math.sqrt(phi):.4f}")
print(f"    m₂/m₁ = {m2/m1:.4f} vs φ/√2 = {phi/math.sqrt(2):.4f}")

# ============ 3. 關鍵: m₂/m₁ 有冇簡單結構? ============
print("\n[3] m₂/m₁ 結構")
r21 = m2/m1
print(f"  m₂/m₁ = {r21:.6f}")
print(f"  log(r21)/log(φ) = {math.log(r21)/math.log(phi):.4f} (φ 冪)")
print(f"  log(r21)/log(γ₁) = {math.log(r21)/math.log(g1):.4f}")
print(f"  log(r21)/log(γ₂) = {math.log(r21)/math.log(g2):.4f}")
print(f"  r21² = {r21**2:.6f}")
print(f"  r21³ = {r21**3:.6f}")

# m₃/m₂
r32 = m3_fixed/m2
print(f"\n  m₃/m₂ = {r32:.6f}")
print(f"  log(r32)/log(φ) = {math.log(r32)/math.log(phi):.4f}")
print(f"  log(r32)/log(γ₆) = {math.log(r32)/math.log(g6):.4f}")

# ============ 4. 關鍵測試: m_i 係咪 = m₃ × (γ 組合)? ============
print("\n[4] m_i = m₃ × f_i 測試")
print(f"  f₁ = m₁/m₃ = {m1/m3_fixed:.6f}")
print(f"  f₂ = m₂/m₃ = {m2/m3_fixed:.6f}")
print(f"  f₁ 候選:")
print(f"    γ₁/γ₆ = {g1/g6:.6f} ({abs(m1/m3_fixed-g1/g6)/(g1/g6)*100:.1f}%)")
print(f"    (γ₁/γ₆)² = {(g1/g6)**2:.6f} ({abs(m1/m3_fixed-(g1/g6)**2)/((g1/g6)**2)*100:.1f}%)")
print(f"    γ₂/γ₆ = {g2/g6:.6f}")
print(f"  f₂ 候選:")
print(f"    γ₂/γ₆ = {g2/g6:.6f} ({abs(m2/m3_fixed-g2/g6)/(g2/g6)*100:.1f}%)")
print(f"    (γ₂/γ₆)² = {(g2/g6)**2:.6f} ({abs(m2/m3_fixed-(g2/g6)**2)/((g2/g6)**2)*100:.1f}%)")
print(f"    γ₃/γ₆ = {g3/g6:.6f} ({abs(m2/m3_fixed-g3/g6)/(g3/g6)*100:.1f}%)")

# ============ 5. 質量平方差 ============
print("\n[5] 質量平方差結構")
print(f"  Δm²₃₁ = {dm31:.4e} eV²")
print(f"  Δm²₂₁ = {dm21:.4e} eV²")
print(f"  Δm²₃₁/Δm²₂₁ = {dm31/dm21:.2f}")
print(f"  φ⁷ = {phi**7:.2f}, φ⁸ = {phi**8:.2f}")
print(f"  L₅ = 11, L₆ = 18")
print(f"  44/5.5 = 8, 44/6 = 7.33")
check("Δm² 比 ≈ 32 (2⁵)?", abs(dm31/dm21 - 32) < 5, f"({dm31/dm21:.1f} vs 32)")
check("Δm² 比 ≈ φ⁷?", abs(dm31/dm21 - phi**7)/phi**7 < 0.3, f"({dm31/dm21:.1f} vs {phi**7:.1f})")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("十七期 89 總結:")
print("=" * 72)
print(f"""
  ν 世代結構 (盲測後):
  ─────────────────────────────────
  1. NH 質量: m₁ = {m1:.5f}, m₂ = {m2:.5f}, m₃ = {m3_fixed:.5f} eV
  2. m₂/m₁ = {r21:.4f} (唔係 φ = {phi:.4f})
  3. m₃/m₂ = {r32:.4f} (唔係 φ)
  4. Δm²₃₁/Δm²₂₁ = {dm31/dm21:.1f} ≈ ? (φ⁷={phi**7:.1f}, 32)

  {'✅ Δm² 比有結構!' if abs(dm31/dm21-32)<5 or abs(dm31/dm21-phi**7)/phi**7<0.3 else '❌ Δm² 比冇簡單結構'}
  {'✅ f_i 有 γ 結構!' if min(abs(m1/m3_fixed-g1/g6),abs(m1/m3_fixed-(g1/g6)**2)) < 0.3 else '❌ f_i 冇 γ 結構'}
""")

results = {
    "test": "O57 十七期 89: ν 世代",
    "m1": float(m1), "m2": float(m2), "m3": float(m3_fixed),
    "r21": float(r21), "r32": float(r32),
    "dm_ratio": float(dm31/dm21),
    "passed": passed, "failed": failed
}
with open("data/89_nu_generation.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
exit(0)
