#!/usr/bin/env python3
"""
O11 Maser H₀ 偏移結構搜索
=========================
目標: 鎖定 Maser 偏移 +1.80% (H₀_maser = 73.9 vs H₀_idcm = 72.59)

鐵律 (theoretical-physics-validation):
- 禁止數字遊戲: 每個候選公式必須有結構來源
- κφ⁻¹ 家族: TRGB -κφ⁻¹, Miras +κφ⁻¹/4, SH0ES +φ⁻¹/100
- Maser 係「純幾何」方法 → 投影層應該係「最深」或「全深度」
- 1.80% 好細 → 要同 κφ⁻¹ 家族比較, 唔好亂撞

結構常數:
- φ = (1+√5)/2, φ⁻¹ = 0.618034
- κ = 1/16 = 0.0625
- ε = α/√N = 1.025/√44 ≈ 0.1545 (cosmic)
- K_Chain: 44-site, Σγ=90, γ_n = 4sin²(nπ/88)
- K_Tree: 33-site (B=4)
- H₀_idcm = 72.59, Maser = 73.9, offset = +1.803%
"""
import math
import itertools
from fractions import Fraction

phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi
kappa = 1 / 16
N = 44
alpha = 1.025
eps = alpha / math.sqrt(N)

H0_idcm = 72.59
H0_maser = 73.9
offset = H0_maser / H0_idcm - 1  # +1.803%
print(f"{'='*70}")
print(f"H₀_idcm = {H0_idcm}, H₀_maser = {H0_maser}")
print(f"offset  = {offset*100:.4f}%")
print(f"{'='*70}")

# ---- 1. κφ⁻¹ 家族對比 ----
print("\n[1] κφ⁻¹ 家族 (已鎖定)")
family = {
    "TRGB  -κφ⁻¹      ": -kappa * phi_inv,
    "Miras  κφ⁻¹/4    ": kappa * phi_inv / 4,
    "SH0ES  φ⁻¹/100   ": phi_inv / 100,
    "Maser  ? (目標)  ": offset,
}
for k, v in family.items():
    print(f"  {k} = {v*100:+.4f}%")

# ---- 2. 結構候選掃描 (有來源嘅組合) ----
print("\n[2] 結構候選 (κφ⁻¹ 家族延伸 + 結構常數組合)")

# 2a. κφ⁻¹ 家族插值: Miras 係 /4, 如果 Maser 係幾何全深度 → ?
# 假設: 偏移量級 = κφ⁻¹ × f(結構因子)
cands = [
    # (名稱, 公式, 結構來源)
    ("2φ⁻¹/100        ", 2 * phi_inv / 100,          "SH0ES×2 — 舊候選, 差 31%"),
    ("κφ⁻¹/2          ", kappa * phi_inv / 2,         "Miras 中間值 (κφ⁻¹/4 → κφ⁻¹/2)"),
    ("κφ⁻¹×3/4        ", kappa * phi_inv * 3 / 4,     "Miras 同 TRGB 之間"),
    ("κφ⁻¹×4/3        ", kappa * phi_inv * 4 / 3,     "超 Miras"),
    ("κφ⁻¹×2          ", kappa * phi_inv * 2,         "超 Miras 2x"),
    ("φ⁻²/17          ", phi_inv**2 / 17,             "舊候選 φ⁻²/17"),
    ("φ⁻¹²            ", phi_inv**12,                 "舊候選"),
    ("ε⁴              ", eps**4,                      "舊候選"),
    ("ε²φ⁻¹           ", eps**2 * phi_inv,            "ε²×φ⁻¹"),
    ("φ⁻³/7           ", phi_inv**3 / 7,              "φ⁻³/7"),
    ("φ⁻²/9           ", phi_inv**2 / 9,              "φ⁻²/9"),
    ("κφ⁻²            ", kappa * phi_inv**2,          "κ×φ⁻²"),
    ("κφ⁻¹/φ          ", kappa * phi_inv / phi,       "κφ⁻¹/φ (Miras/φ)"),
    ("κφ⁻¹×φ          ", kappa * phi_inv * phi,       "κφ⁻¹×φ (Miras×φ)"),
    ("φ⁻¹×κ×2         ", phi_inv * kappa * 2,         "=κφ⁻¹/8×16?"),
    ("φ⁻²×κ×4         ", phi_inv**2 * kappa * 4,      "φ⁻²×4κ"),
    ("φ⁻¹×ε           ", phi_inv * eps,               "φ⁻¹×ε"),
    ("ε×κ             ", eps * kappa,                 "ε×κ"),
    ("ε/16            ", eps / 16,                    "ε/16"),
    ("εφ⁻¹/6          ", eps * phi_inv / 6,           "εφ⁻¹/6"),
]

print(f"\n{'候選':22s} {'偏移%':>10s} {'目標 1.803%':>12s} {'偏差%':>10s} 來源")
print("-" * 95)
best = []
for name, val, src in cands:
    dev = abs(val - offset) / offset * 100
    mark = "✅" if dev < 1 else ("🟡" if dev < 10 else "❌")
    print(f"{mark} {name:20s} {val*100:10.4f} {offset*100:12.4f} {dev:9.2f}%  {src}")
    best.append((dev, name, val, src))
best.sort()
print(f"\n最佳 3:")
for dev, name, val, src in best[:3]:
    print(f"  {name} → {val*100:.4f}% (偏差 {dev:.2f}%)")

# ---- 3. 結構插值: 用現有家族推導 ----
print("\n[3] 結構插值分析")
print("家族偏移: TRGB -3.86%, Miras +0.98%, SH0ES +0.62%")
print(f"Maser 目標 +1.80%")
print(f"Miras 0.98% → Maser 1.80%: 比例 = {offset/(kappa*phi_inv/4):.3f}")
print(f"  即 Maser ≈ κφ⁻¹/4 × {offset/(kappa*phi_inv/4):.3f}")
print(f"  {offset/(kappa*phi_inv/4):.3f} ≈ √3? {abs(3**0.5 - offset/(kappa*phi_inv/4)):.4f}")
print(f"  {offset/(kappa*phi_inv/4):.3f} ≈ φ? {abs(phi - offset/(kappa*phi_inv/4)):.4f}")
print(f"  {offset/(kappa*phi_inv/4):.3f} ≈ 44/25? {abs(44/25 - offset/(kappa*phi_inv/4)):.4f}")
print(f"  {offset/(kappa*phi_inv/4):.3f} ≈ 7/4? {abs(7/4 - offset/(kappa*phi_inv/4)):.4f}")
print(f"  {offset/(kappa*phi_inv/4):.3f} ≈ 3/2? {abs(3/2 - offset/(kappa*phi_inv/4)):.4f}")

# SH0ES → Maser
print(f"\nSH0ES 0.618% → Maser 1.803%: 比例 = {offset/(phi_inv/100):.3f}")
print(f"  ≈ 2.919 ≈ 44/15.07?  ≈ 3 - 0.081?  ≈ 2.9?")

# ---- 4. 關鍵結構數: K_Chain 譜 ----
print("\n[4] K_Chain 譜候選")
gammas = [4 * math.sin(math.pi * n / 88)**2 for n in range(1, 45)]
sum90 = sum(gammas)
# γ_n / 90 比例
for n in [1, 2, 3, 4, 5, 7, 11, 22]:
    print(f"  γ_{n}/Σγ = {gammas[n-1]/sum90*100:.4f}%  (γ_{n} = {gammas[n-1]:.4f})")

print(f"\n目標 1.803% ≈ γ_n/Σγ?")
for n in range(1, 45):
    r = gammas[n-1] / sum90 * 100
    if abs(r - offset*100) / (offset*100) < 0.15:
        print(f"  ✅ γ_{n}/Σγ = {r:.4f}% (偏差 {(r-offset*100)/(offset*100)*100:.2f}%)")
print("  (冇 15% 內嘅 → 唔係單一 γ_n/Σγ)")

# ---- 5. 密度比例 ----
print("\n[5] 密度/配分候選")
density = {
    "Ω_b/Ω_m = 2/15": 2/15,
    "Ω_DM/Ω_b = 13/2": 13/2,
    "Ω_Λ = 4/(φ⁴-1)": 4/(phi**4 - 1),
    "Ω_m = 1-Ω_Λ": 1 - 4/(phi**4 - 1),
    "61.5/90 (sync 比例)": 61.5/90,
    "28.5/90 (物質比例)": 28.5/90,
}
for name, val in density.items():
    # 檢查邊個比例 × κφ⁻¹/4 或 × φ⁻¹/100 接近 1.803%
    for fname, fval in [("κφ⁻¹/4", kappa*phi_inv/4), ("φ⁻¹/100", phi_inv/100), ("κφ⁻¹", kappa*phi_inv)]:
        comb = val * fval
        dev = abs(comb - offset) / offset * 100
        if dev < 5:
            print(f"  ✅ {name} × {fname} = {comb*100:.4f}% (偏差 {dev:.2f}%)")

# ---- 6. 零點檢查: 1.80% 係咪誤差範圍? ----
print("\n[6] 統計檢查")
print(f"MCP XIII: H₀ = 73.9 ± 3.0 → offset 1.803% ± 4.13%")
print(f"  → offset 喺 1σ 誤差內: {'✅ 係' if 3.0/73.9*100 > offset*100 else '❌ 唔係'}")
print(f"MCP 2025 profile likelihood: 73.5 ± 3.0 → offset = 73.5/72.59-1 = {(73.5/72.59-1)*100:.3f}%")
print(f"  → 如果最新值係 73.5, offset 得 {(73.5/72.59-1)*100:.3f}%, 唔係 1.803%")
print(f"  73.5/72.59 - 1 = {(73.5/72.59-1)*100:.4f}%")

print("\n" + "="*70)
print("結論: 見 02_structural_search.md")
print("="*70)
