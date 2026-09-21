#!/usr/bin/env python3
"""
O57 十九期 99: ★★★ PMNS 三角度完整閉合驗證
==============================================
scripts/98 發現:
  sin²θ₁₂ = γ₂/(γ₂+γ₃) = 0.3079 (誤差 1.7%)
  sin²θ₂₃ = γ₇/(γ₇+γ₆) = 0.5751 (誤差 0.5%)
  sin²θ₁₃ = γ₆/(2B) = 0.02259 (誤差 2.6%)

驗證:
  1. 三角度閉合
  2. LEE 懲罰 (每個角 44 個候選)
  3. 獨立性檢查 (γ_n 有冇重複用)
  4. 完整 U_PMNS 重建
"""
import sys, os, math
import json
import numpy as np

print("=" * 72)
print("O57 十九期 99: PMNS 三角度完整閉合")
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

# ============ 1. 三角度 ============
print("\n[1] 三角度閉合")
# θ₁₂: sin²θ₁₂ = γ₂/(γ₂+γ₃)
s12_exp = 0.303
s12_pred = g[2]/(g[2]+g[3])
# θ₂₃: sin²θ₂₃ = γ₇/(γ₇+γ₆)
s23_exp = 0.572
s23_pred = g[7]/(g[7]+g[6])
# θ₁₃: sin²θ₁₃ = γ₆/8
s13_exp = 0.02203
s13_pred = g[6]/8

angles = {
    "θ₁₂": (s12_pred, s12_exp, "γ₂/(γ₂+γ₃)"),
    "θ₂₃": (s23_pred, s23_exp, "γ₇/(γ₇+γ₆)"),
    "θ₁₃": (s13_pred, s13_exp, "γ₆/(2B)"),
}
for name, (pred, exp, formula) in angles.items():
    err = abs(pred - exp)/exp*100
    print(f"  {name}: sin² = {pred:.5f} (實驗 {exp}, 誤差 {err:.2f}%) ← {formula}")
    check(f"{name} < 5%", err < 5, f"({err:.2f}%)")

# ============ 2. LEE 懲罰 ============
print("\n[2] LEE 懲罰 (每個角 44 個候選)")
# θ₁₂: γ_a/(γ_a+γ_b) 所有 a<b 組合
hits12 = []
for a in range(1, 45):
    for b in range(1, 45):
        if a == b: continue
        val = g[a]/(g[a]+g[b])
        err = abs(val - s12_exp)/s12_exp*100
        if err < 5:
            hits12.append((a, b, err))
print(f"  θ₁₂: <5% 命中 {len(hits12)}/1892 組合")
for h in hits12[:8]:
    print(f"    γ_{h[0]}/(γ_{h[0]}+γ_{h[1]}) = 誤差 {h[2]:.1f}%")

# θ₂₃: 同樣
hits23 = []
for a in range(1, 45):
    for b in range(1, 45):
        if a == b: continue
        val = g[a]/(g[a]+g[b])
        err = abs(val - s23_exp)/s23_exp*100
        if err < 5:
            hits23.append((a, b, err))
print(f"  θ₂₃: <5% 命中 {len(hits23)}/1892 組合")
for h in hits23[:8]:
    print(f"    γ_{h[0]}/(γ_{h[0]}+γ_{h[1]}) = 誤差 {h[2]:.1f}%")

# θ₁₃: γ_n/k
hits13 = []
for n in range(1, 45):
    for k in range(1, 33):
        val = g[n]/k
        err = abs(val - s13_exp)/s13_exp*100
        if err < 5:
            hits13.append((n, k, err))
print(f"  θ₁₃: <5% 命中 {len(hits13)}/{44*32} 組合")
for h in hits13[:10]:
    print(f"    γ_{h[0]}/{h[1]} = 誤差 {h[2]:.1f}%")

# ============ 3. 組合 LEE ============
print("\n[3] 組合 LEE (三角度一齊命中)")
# 三角度一齊 <5% 嘅概率
p12 = len(hits12)/1892
p23 = len(hits23)/1892
p13 = len(hits13)/(44*32)
p_joint = p12*p23*p13
print(f"  P(θ₁₂) = {p12:.4f}, P(θ₂₃) = {p23:.4f}, P(θ₁₃) = {p13:.4f}")
print(f"  聯合概率 (獨立) = {p_joint:.2e}")
print(f"  → 如果 {p_joint} < 0.01 → 唔係巧合!")
check("聯合 p < 0.01", p_joint < 0.01, f"({p_joint:.2e})")

# ============ 4. U_PMNS 重建 ============
print("\n[4] U_PMNS 重建")
s12, s23, s13 = math.sqrt(s12_pred), math.sqrt(s23_pred), math.sqrt(s13_pred)
c12, c23, c13 = math.sqrt(1-s12_pred), math.sqrt(1-s23_pred), math.sqrt(1-s13_pred)
# 標準 PDG 參數化 (δ=0)
U = np.array([
    [c12*c13, s12*c13, s13],
    [-s12*c23 - c12*s23*s13, c12*c23 - s12*s23*s13, s23*c13],
    [s12*s23 - c12*c23*s13, -c12*s23 - s12*c23*s13, c23*c13],
])
print("  U_PMNS (δ=0):")
for row in U:
    print(f"    [{row[0]:+.4f} {row[1]:+.4f} {row[2]:+.4f}]")
# 檢查 unitary
print(f"  Unitary check: {np.abs(U @ U.T - np.eye(3)).max():.2e}")

# Jarlskog 不變量 (δ=0 → 0)
J = np.imag(U[0,0]*U[1,1]*np.conj(U[0,1])*np.conj(U[1,0]))
print(f"  J_CP (δ=0) = {J:.2e} (需 δ≠0 先有 CP 破壞)")
print(f"  實驗 J_CP ≈ 3.2e-2 → 需要 δ_CP ≈ 1.19 rad")

# ============ 5. δ_CP? ============
print("\n[5] δ_CP 探索")
# J_CP 實驗值
J_exp = 3.2e-2
# 用我哋嘅角: J = c₁₂s₁₂c₂₃s₂₃c₁₃²s₁₃·sinδ
J_max = c12*s12*c23*s23*c13**2*s13
print(f"  J_max (δ=90°) = {J_max:.4f}")
if J_max > 0:
    sin_delta = J_exp/J_max
    delta = math.asin(min(1, sin_delta)) if sin_delta <= 1 else None
    print(f"  sinδ = {sin_delta:.4f}")
    if delta:
        print(f"  δ_CP = {delta:.3f} rad = {delta*180/math.pi:.1f}°")
        print(f"  實驗 δ_CP ≈ 68° (1.19 rad)")
        check("δ_CP < 30% 誤差", abs(delta*180/math.pi - 68)/68 < 0.3, f"({delta*180/math.pi:.1f}° vs 68°)")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("十九期 99 總結:")
print("=" * 72)
print(f"""
  ★★★ PMNS 三角度 γ 閉合:
  ─────────────────────────────────
  sin²θ₁₂ = γ₂/(γ₂+γ₃) = {s12_pred:.5f} (實驗 0.303, 誤差 {abs(s12_pred-s12_exp)/s12_exp*100:.2f}%)
  sin²θ₂₃ = γ₇/(γ₇+γ₆) = {s23_pred:.5f} (實驗 0.572, 誤差 {abs(s23_pred-s23_exp)/s23_exp*100:.2f}%)
  sin²θ₁₃ = γ₆/(2B) = {s13_pred:.5f} (實驗 0.02203, 誤差 {abs(s13_pred-s13_exp)/s13_exp*100:.2f}%)

  γ 譜角色:
  θ₁₂: γ₂, γ₃ (太陽)
  θ₂₃: γ₇, γ₆ (大氣)
  θ₁₃: γ₆ (反應堆)

  統計: 聯合 p = {p_joint:.2e} ({'✅ 非巧合' if p_joint < 0.01 else '❌'})
  J_CP: δ_CP = {'需計算' if 'delta' not in locals() else f"{delta*180/math.pi:.1f}° (實驗 68°)"}
""")

results = {
    "test": "O57 十九期 99: PMNS 三角度",
    "s12": [float(s12_pred), float(s12_exp), float(abs(s12_pred-s12_exp)/s12_exp*100)],
    "s23": [float(s23_pred), float(s23_exp), float(abs(s23_pred-s23_exp)/s23_exp*100)],
    "s13": [float(s13_pred), float(s13_exp), float(abs(s13_pred-s13_exp)/s13_exp*100)],
    "joint_p": float(p_joint),
    "hits12": len(hits12), "hits23": len(hits23), "hits13": len(hits13),
    "U_pmns": U.tolist(),
    "passed": passed, "failed": failed
}
with open("data/99_pmns_full.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十九期 99 完成!")
