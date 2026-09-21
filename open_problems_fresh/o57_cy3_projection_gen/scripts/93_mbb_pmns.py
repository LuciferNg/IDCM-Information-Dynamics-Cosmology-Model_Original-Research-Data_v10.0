#!/usr/bin/env python3
"""
O57 十八期 93: m_ββ 預言 — PMNS 精確值 (唔再係 U_ei²≈1/3)
============================================================
scripts/90 用 U_ei² ≈ 1/3 近似 (大混合角)
而家有實驗 PMNS 值 (NuFIT 2024):
  sin²θ₁₂ = 0.303, sin²θ₂₃ = 0.572, sin²θ₁₃ = 0.02203

m_ββ = |Σ U_ei² m_i| 需要:
  U_e1² = |U_e1|², U_e2², U_e3² (electron row)

用 PMNS 參數化:
  U_e1 = c₁₂c₁₃, U_e2 = s₁₂c₁₃, U_e3 = s₁₃·e^{-iδ}
  (Majorana 相位 α₁, α₂ 加入)
"""
import sys, os, math
import json

print("=" * 72)
print("O57 十八期 93: m_ββ 精確 PMNS")
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

# ============ 1. PMNS 參數 (NuFIT 2024) ============
print("\n[1] PMNS 參數 (NuFIT 2024)")
s12_2 = 0.303   # sin²θ₁₂
s23_2 = 0.572   # sin²θ₂₃
s13_2 = 0.02203 # sin²θ₁₃
delta = 1.19    # δ_CP (rad) ≈ 68°
c12 = math.sqrt(1 - s12_2)
c13 = math.sqrt(1 - s13_2)
s12 = math.sqrt(s12_2)
s13 = math.sqrt(s13_2)
print(f"  sin²θ₁₂ = {s12_2}, sin²θ₂₃ = {s23_2}, sin²θ₁₃ = {s13_2}")
print(f"  δ_CP = {delta:.2f} rad = {delta*180/math.pi:.1f}°")

# Electron row (Dirac 相位)
Ue1 = c12*c13
Ue2 = s12*c13
Ue3 = s13
print(f"\n  U_e1 = {Ue1:.4f} (|U_e1|² = {Ue1**2:.4f})")
print(f"  U_e2 = {Ue2:.4f} (|U_e2|² = {Ue2**2:.4f})")
print(f"  U_e3 = {Ue3:.4f} (|U_e3|² = {Ue3**2:.4f})")
print(f"  Σ|U_ei|² = {Ue1**2+Ue2**2+Ue3**2:.6f} (應=1)")

# ============ 2. m_ββ 計算 ============
print("\n[2] m_ββ (NH, m₁=0.02095, m₂=0.02269, m₃=0.0536)")
m1, m2, m3 = 0.02095, 0.02269, 0.0536  # eV

# Majorana 相位 α₁, α₂ ∈ [0, 2π)
# m_ββ = |Ue1²m₁ + Ue2²m₂e^{iα₁} + Ue3²m₃e^{iα₂}|
best = None
worst = None
for a1 in [0, math.pi/2, math.pi, 3*math.pi/2]:
    for a2 in [0, math.pi/2, math.pi, 3*math.pi/2]:
        mbb = abs(Ue1**2*m1 + Ue2**2*m2*complex(math.cos(a1), math.sin(a1))
                  + Ue3**2*m3*complex(math.cos(a2), math.sin(a2)))
        mbb = abs(mbb)
        if best is None or mbb < best[0]:
            best = (mbb, a1, a2)
        if worst is None or mbb > worst[0]:
            worst = (mbb, a1, a2)

mbb_min, a1_min, a2_min = best
mbb_max, a1_max, a2_max = worst
print(f"  m_ββ 範圍 (PMNS 精確): [{mbb_min:.4f}, {mbb_max:.4f}] eV")
print(f"    = [{mbb_min*1e3:.1f}, {mbb_max*1e3:.1f}] meV")
print(f"  對比 scripts/90 近似: [18.4, 32.4] meV")
print(f"  範圍收窄: {abs(mbb_max-mbb_min)*1e3:.1f} meV")

# ============ 3. 對比 ============
print("\n[3] 對比 scripts/90 近似")
print(f"  scripts/90 (U_ei²≈1/3): [18.4, 32.4] meV")
print(f"  scripts/93 (PMNS 精確): [{mbb_min*1e3:.1f}, {mbb_max*1e3:.1f}] meV")
print(f"  重疊: {max(mbb_min*1e3, 18.4):.1f} - {min(mbb_max*1e3, 32.4):.1f} meV")
print(f"  預言中值: {(mbb_min+mbb_max)/2*1e3:.1f} meV")

# ============ 4. 實驗比較 ============
print("\n[4] 實驗比較")
exp = {
    "KamLAND-Zen 2025": (28, 122),
    "LEGEND-200": (75, 200),
    "GERDA": (79, 180),
}
for name, (lo, hi) in exp.items():
    excluded = hi < mbb_min*1e3
    print(f"  {name}: < {lo}-{hi} meV → {'❌ 排除 IDCM' if excluded else '✅ 未排除'}")

# KamLAND2-Zen / LEGEND-1000
print(f"\n  下一代:")
print(f"  KamLAND2-Zen (2027): 目標 20 meV → {'🟢 覆蓋' if 20 <= mbb_max*1e3 else '🟡'}")
print(f"  LEGEND-1000 (2028-30): 9-24 meV → {'🟢 覆蓋下限' if 9 <= mbb_max*1e3 and 24 >= mbb_min*1e3 else '🟡'}")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("十八期 93 總結:")
print("=" * 72)
print(f"""
  m_ββ 預言 (PMNS 精確):
  ─────────────────────────────────
  [{mbb_min*1e3:.1f}, {mbb_max*1e3:.1f}] meV (Majorana 相位掃描)
  (scripts/90 近似: [18.4, 32.4] meV)

  精確化後:
  {'✅ 範圍收窄' if (mbb_max-mbb_min)*1e3 < 14 else '🟡 範圍類似'}
  預言中值: {(mbb_min+mbb_max)/2*1e3:.1f} meV

  實驗:
  現有: 全部未排除
  2027: KamLAND2-Zen (20 meV) {'覆蓋' if 20 <= mbb_max*1e3 else '未覆蓋'}
  2030: LEGEND-1000 (9-24 meV) {'覆蓋' if 9 <= mbb_max*1e3 and 24 >= mbb_min*1e3 else '未覆蓋'}
""")

results = {
    "test": "O57 十八期 93: m_ββ PMNS 精確",
    "pmns": {"s12_2": s12_2, "s23_2": s23_2, "s13_2": s13_2},
    "mbb_range_meV": [float(mbb_min*1e3), float(mbb_max*1e3)],
    "mbb_approx_meV": [18.4, 32.4],
    "passed": passed, "failed": failed
}
with open("data/93_mbb_pmns.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十八期 93 完成!")
