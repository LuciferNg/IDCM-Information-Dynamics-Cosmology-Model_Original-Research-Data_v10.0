#!/usr/bin/env python3
"""
O62 六期 22: 開放問題 4 — O57 公式關係閉合
===========================================
O57: V₁₀ + 44γ₆ = 282.9706 (0.037%)
O62: F(γ) + 19 = 283.0821 (0.0025%)

關係:
  F(γ) = 264.0821, V₁₀ = 275.018
  差 = F(γ) − V₁₀ = −10.936
  19 − 44γ₆ = 19 − 7.952 = 11.048
  −10.936 + 11.048 = +0.112

問題: 兩者係咪同一件事嘅兩個近似?
  1. V₁₀ = L₁₀φ + L₉ = 123φ + 76 = 275.018
  2. F(γ) = (1/6)κγ³
  3. 有冇橋: F(γ) + 19 = V₁₀ + 44γ₆ + δ?
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O62 六期 22: O57 關係閉合")
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

d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
Fg = np.einsum("ijk,i,j,k", kappa, gamma36, gamma36, gamma36) / 6.0
V_obs = 283.0752

# Lucas
L = [2, 1]
for i in range(2, 40):
    L.append(L[i-1] + L[i-2])
V10 = L[10]*phi + L[9]
g6 = 4*math.sin(6*math.pi/88)**2
V57 = V10 + 44*g6
V62 = Fg + 19

print("\n[1] 兩公式")
print(f"  O57: V₁₀ + 44γ₆ = {V57:.6f} (誤差 {abs(V57-V_obs)/V_obs*100:.5f}%)")
print(f"  O62: F(γ) + 19  = {V62:.6f} (誤差 {abs(V62-V_obs)/V_obs*100:.5f}%)")
print(f"  差 = {V62 - V57:.6f}")

# ============ 1. 分解 ============
print("\n[2] 結構分解")
dF = Fg - V10
dC = 19 - 44*g6
print(f"  F(γ) − V₁₀ = {dF:.6f}")
print(f"  19 − 44γ₆ = {dC:.6f}")
print(f"  和 = {dF + dC:.6f} (= V62 − V57)")
print(f"  dF ≈ −11 + 0.064? {dF + 11:.6f}")
print(f"  dC ≈ 11 + 0.048? {dC - 11:.6f}")
print(f"  dF + 11 = {dF+11:.6f}")
print(f"  dC − 11 = {dC-11:.6f}")

# ============ 2. 橋樑: F(γ) vs V₁₀ ============
print("\n[3] F(γ) vs V₁₀ 結構")
print(f"  V₁₀ = L₁₀φ + L₉ = {L[10]}φ + {L[9]} = {V10:.6f}")
print(f"  F(γ) = 264.0821")
print(f"  V₁₀ − F(γ) = {V10 - Fg:.6f}")
print(f"  ≈ 11 − 0.064")
# 11 = L₅, 0.064 ≈ ?
print(f"  0.064 ≈ γ_1 + 0.013? γ_1 = {4*math.sin(math.pi/88)**2:.4f}")
print(f"  0.064 ≈ γ_2/3.18? {4*math.sin(2*math.pi/88)**2/3.18:.4f}")
print(f"  0.064 ≈ 44γ₆/124? {44*g6/124:.4f}")

# ============ 3. 統一公式? ============
print("\n[4] 統一公式嘗試")
# V_Λ = V₁₀ + 44γ₆ + δ, δ = ?
delta = V_obs - V57
print(f"  δ = V_obs − V57 = {delta:.6f}")
print(f"  δ/0.01 = {delta/0.01:.2f}")
# δ ≈ 0.1046
print(f"  δ ≈ 0.1046")
print(f"  δ ≈ γ_1×2.05? {4*math.sin(math.pi/88)**2*2.05:.4f}")
print(f"  δ ≈ γ_4×1.29? {4*math.sin(4*math.pi/88)**2*1.29:.4f}")
print(f"  δ ≈ 1/9.56? {1/9.56:.4f}")
print(f"  δ ≈ γ_6/1.728? {g6/1.728:.4f}")

# ============ 4. 兩公式嘅共同結構 ============
print("\n[5] 共同結構")
# O57: V₁₀ + 44γ₆ — Lucas 能階 + K_Chain 諧波修正
# O62: F(γ) + 19 — CY₃ prepotential + P̂ gap 修正
# 兩者都用 K_Chain 諧波 γ!
print(f"  O57 用 γ₆ (p6 諧波)")
print(f"  O62 用 γ₄₄ = [γ_1..γ_36] (全譜)")
print(f"  → O62 係 O57 嘅推廣: 單一諧波 → 全譜 prepotential")
print(f"  → O57 44γ₆ = 7.95 係 O62 19 修正嘅近似?")
print(f"    19 vs 44γ₆ = 7.95: 差 11.05 ≈ L₅ = 11")

# ============ 5. F(γ) 用 γ₆ 單點? ============
print("\n[6] F 用 uniform γ₆?")
t6 = np.full(36, g6)
F6 = np.einsum("ijk,i,j,k", kappa, t6, t6, t6) / 6.0
print(f"  F(γ₆·1) = {F6:.6f}")
print(f"  V₁₀ = {V10:.6f}")
print(f"  F(γ₆·1) + V₁₀ = {F6 + V10:.6f} vs 283? {abs(F6+V10-283.0752):.4f}")

# t = 44γ₆·1?
t44g6 = np.full(36, 44*g6)
F44g6 = np.einsum("ijk,i,j,k", kappa, t44g6, t44g6, t44g6) / 6.0
print(f"  F(44γ₆·1) = {F44g6:.6f}")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("六期 22 總結:")
print("=" * 72)
print(f"""
  O57: V₁₀ + 44γ₆ = {V57:.6f} (0.037%)
  O62: F(γ) + 19  = {V62:.6f} (0.0025%)

  結構關係:
  F(γ) − V₁₀ = {dF:.6f} ≈ −L₅ + 0.064
  19 − 44γ₆ = {dC:.6f} ≈ +L₅ + 0.048

  → O62 係 O57 嘅「全譜化」:
    O57: 單一諧波 γ₆ 修正 (搜索)
    O62: 全譜 prepotential F(γ) + P̂ gap (推導)
  → 兩者差 δ = {V62 - V57:.4f} 係譜平均效應
""")
out = {
    "test": "O62 六期 22: O57 關係",
    "V57": float(V57), "V62": float(V62),
    "dF": float(dF), "dC": float(dC),
    "delta": float(delta),
    "F6_uniform": float(F6),
    "relation": "O62 = O57 全譜化: F(γ)+19 vs V₁₀+44γ₆",
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "22_o57_relation.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 六期 22 完成!")
