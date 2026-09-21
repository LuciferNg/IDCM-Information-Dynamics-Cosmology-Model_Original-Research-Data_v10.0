#!/usr/bin/env python3
"""
O57 十九期 98: ★★ sin²θ₁₃ = γ₆/(2B) — PMNS θ₁₃ 閉合
========================================================
scripts/97 發現: sin²θ₁₃ = γ₆/8 = 0.02259 (實驗 0.02203, 誤差 2.55%)
               θ₁₃ = 8.645° (實驗 8.536°, 誤差 1.28%)

驗證:
  1. sin²θ₁₃ = γ₆/(2B) 閉合
  2. 其他 PMNS 角 (θ₁₂, θ₂₃) 有冇 γ 結構?
  3. 檢查 γ₆ 共用問題 (m_ν 已用 γ₆)
  4. 統計顯著性 (44 個 γ_n 揀 1 個嘅 LEE 懲罰)
"""
import sys, os, math
import json
import numpy as np

print("=" * 72)
print("O57 十九期 98: PMNS θ₁₃ 閉合")
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

phi = (1 + math.sqrt(5)) / 2
g = {n: 4*math.sin(n*math.pi/88)**2 for n in range(1, 45)}

# ============ 1. θ₁₃ 閉合 ============
print("\n[1] sin²θ₁₃ = γ₆/(2B)")
s13_exp = 0.02203
s13_pred = g[6]/8
err13 = abs(s13_pred - s13_exp)/s13_exp*100
theta13_pred = math.asin(math.sqrt(s13_pred))*180/math.pi
theta13_exp = math.asin(math.sqrt(s13_exp))*180/math.pi
print(f"  γ₆/(2B) = {g[6]:.6f}/8 = {s13_pred:.6f}")
print(f"  實驗 sin²θ₁₃ = {s13_exp}")
print(f"  誤差 = {err13:.2f}%")
print(f"  θ₁₃ 預言 = {theta13_pred:.3f}°, 實驗 = {theta13_exp:.3f}°")
check("sin²θ₁₃ < 5%", err13 < 5, f"({err13:.2f}%)")

# ============ 2. θ₁₂ 嘗試 ============
print("\n[2] θ₁₂ (實驗 33.41°, sin²θ₁₂ = 0.303)")
s12_exp = 0.303
# 用 γ 組合
cands12 = {
    "γ₆/(γ₆+γ₇)": g[6]/(g[6]+g[7]),
    "γ₁/(γ₁+γ₂)": g[1]/(g[1]+g[2]),
    "γ₆/γ₂₀×√2": g[6]/g[20]*math.sqrt(2),
    "γ₂/(γ₂+γ₃)": g[2]/(g[2]+g[3]),
    "γ₆/(2γ₆+γ₁)": g[6]/(2*g[6]+g[1]),
    "γ₇/(γ₇+γ₆)": g[7]/(g[7]+g[6]),
    "γ₆²/γ₃": g[6]**2/g[3],
    "γ₁/γ₂×2": g[1]/g[2]*2,
}
best12 = None
for name, val in cands12.items():
    err = abs(val - s12_exp)/s12_exp*100
    print(f"  {name} = {val:.4f} (誤差 {err:.1f}%)")
    if best12 is None or err < best12[1]:
        best12 = (name, err, val)
print(f"\n  最佳: {best12[0]} = {best12[2]:.4f} (誤差 {best12[1]:.1f}%)")

# ============ 3. θ₂₃ 嘗試 ============
print("\n[3] θ₂₃ (實驗 49.1°, sin²θ₂₃ = 0.572)")
s23_exp = 0.572
cands23 = {
    "γ₆/(γ₆+γ₃)": g[6]/(g[6]+g[3]),
    "γ₃/(γ₃+γ₆)": g[3]/(g[3]+g[6]),
    "γ₇/(γ₇+γ₆)": g[7]/(g[7]+g[6]),
    "γ₆/(γ₆+γ₁)": g[6]/(g[6]+g[1]),
    "γ₂₀/(γ₂₀+γ₇)": g[20]/(g[20]+g[7]),
    "γ₆/γ₃/2": g[6]/g[3]/2,
    "γ₆/(γ₆+γ₂)": g[6]/(g[6]+g[2]),
    "γ₇/(γ₇+γ₁)": g[7]/(g[7]+g[1]),
}
best23 = None
for name, val in cands23.items():
    err = abs(val - s23_exp)/s23_exp*100
    print(f"  {name} = {val:.4f} (誤差 {err:.1f}%)")
    if best23 is None or err < best23[1]:
        best23 = (name, err, val)
print(f"\n  最佳: {best23[0]} = {best23[2]:.4f} (誤差 {best23[1]:.1f}%)")

# ============ 4. LEE 懲罰 ============
print("\n[4] LEE 懲罰 (44 個 γ_n 揀 1 個)")
# sin²θ₁₃ = γ_n/8 對所有 n 測試
print("  sin²θ₁₃ = γ_n/8 對 44 個 n:")
hits13 = []
for n in range(1, 45):
    val = g[n]/8
    err = abs(val - s13_exp)/s13_exp*100
    if err < 5:
        hits13.append((n, val, err))
print(f"  <5% 命中: {len(hits13)}/44")
for n, val, err in hits13:
    print(f"    n={n}: γ_{n}/8 = {val:.5f} (誤差 {err:.1f}%)")

# ============ 5. 統計 ============
print("\n[5] 統計顯著性")
# n=6 係唯一 <5%?
if len(hits13) == 1 and hits13[0][0] == 6:
    print("  ✅ γ₆ 係唯一 <5% 命中 (1/44 = 2.3%)")
    print("  但 γ₆ 已經用喺 m_ν → 唔係獨立發現")
    print("  → 正確解讀: 呢個係 γ₆ 嘅第三個角色!")
else:
    print(f"  ⚠️ {len(hits13)} 個命中: {[h[0] for h in hits13]}")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("十九期 98 總結:")
print("=" * 72)
print(f"""
  sin²θ₁₃ = γ₆/(2B) 閉合!
  ─────────────────────────────────
  γ₆ = {g[6]:.6f} (K_Chain n=6 諧波)
  γ₆/(2B) = γ₆/8 = {s13_pred:.6f}
  sin²θ₁₃ 實驗 = {s13_exp} (誤差 {err13:.2f}%)
  θ₁₃ 預言 = {theta13_pred:.3f}° vs {theta13_exp:.3f}° (誤差 1.28%)

  γ₆ 三角色:
  1. m_ν₃ = (γ₆v)²/M_comp = 0.0536 eV ✅
  2. Δm² 比 = 2B² = 32 (γ₆ 譜位置) ✅
  3. ★ sin²θ₁₃ = γ₆/(2B) = 0.0226 (誤差 2.6%) ← 新!

  其他角:
  θ₁₂ 最佳: {best12[0]} (誤差 {best12[1]:.1f}%) 
  θ₂₃ 最佳: {best23[0]} (誤差 {best23[1]:.1f}%)

  {'🟢 θ₁₃ 閉合! (γ₆ 第三角色)' if err13 < 5 else '❌ θ₁₃ 未閉合'}
  {'🟡 θ₁₂/θ₂₃ 未閉合 (需更多結構)' if best12[1] > 5 or best23[1] > 5 else '🟢 全部閉合!'}
""")

results = {
    "test": "O57 十九期 98: PMNS θ₁₃",
    "s13_pred": float(s13_pred), "s13_exp": float(s13_exp),
    "s13_err_pct": float(err13),
    "theta13_pred": float(theta13_pred), "theta13_exp": float(theta13_exp),
    "gamma6_roles": 3,
    "best12": [best12[0], float(best12[1])],
    "best23": [best23[0], float(best23[1])],
    "hits13": [[int(n), float(err)] for n, v, err in hits13],
    "passed": passed, "failed": failed
}
with open("data/98_pmns_theta13.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十九期 98 完成!")
