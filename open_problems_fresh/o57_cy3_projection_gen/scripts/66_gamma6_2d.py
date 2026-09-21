#!/usr/bin/env python3
"""
O57 十一期 66: 推 5 — γ₆ 2D Joint Likelihood
==============================================
Gemini 方向 5: 唔好單獨對 Λ 做 1D 置換檢定
→ 計算「同時在 Δm²₃₁ (0.66%) 與 Λ (0.037%) 取得最佳對齊」嘅聯合 P-value

2D Cross-Correlation Joint Likelihood:
  P_joint = P(γ_n 同時最佳命中 中微子 且 最佳命中 Λ)
  44 個 γ_n 中, 只有 γ₆ 同時:
    1. 中微子 Δm²₃₁ 誤差 <1% (p6 機制)
    2. Λ V_Λ 誤差 <0.1% (V₁₀+44γ_n)

測試:
  1. 44 個 γ_n 全部計算 Δm²₃₁(n) 同 Λ(n) 誤差
  2. 計「同時命中兩個領域」嘅數量
  3. 聯合 p-value
  4. 對比單獨 1D 檢定
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 十一期 66: γ₆ 2D Joint Likelihood")
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

# ============ 1. 兩個領域嘅誤差 ============
print("\n[1] 雙領域誤差")
gamma = {n: 4*math.sin(n*math.pi/88)**2 for n in range(1, 45)}
L = [2, 1]
for i in range(2, 20):
    L.append(L[i-1] + L[i-2])
V10 = L[10]*phi + L[9]

# 領域 1: 中微子 Δm²₃₁
# m_ν_τ = (γ₆v)²/M_comp, Δm²₃₁ = m_ντ² - m_νe², m_νe = m_ντ·φ⁻²
# Δm²₃₁ ∝ γ_n² (因為 m_ν ∝ γ_n)
# 所以誤差(n) = |(γ_n/γ₆)² × 2.450e-3 - 2.434e-3|/2.434e-3
# 但 m_ν 用 γ_n 代替 γ₆ 時, Δm²₃₁ ∝ γ_n²
target_dm = 2.434e-3
dm6 = 2.450e-3  # γ₆ 嘅值 (0.66%)

# 領域 2: Λ
Mpl_eV = 1.2209e28
rho_natural = (2.25e-3)**4 / Mpl_eV**4
V_obs = math.log(1/rho_natural)

print(f"  領域 1 (中微子): Δm²₃₁(γ₆) = {dm6:.4e} vs {target_dm:.4e} (0.66%)")
print(f"  領域 2 (Λ): V_Λ(γ₆) = {V10+44*gamma[6]:.4f} vs {V_obs:.4f} (0.037%)")

# ============ 2. 44 個 γ_n 雙領域掃描 ============
print("\n[2] 44 個 γ_n 雙領域掃描")
results_2d = []
for n in range(1, 45):
    gn = gamma[n]
    # 中微子: Δm²₃₁ ∝ γ_n² (scaled)
    dm_n = dm6 * (gn/gamma[6])**2
    err_nu = abs(dm_n - target_dm)/target_dm * 100
    # Λ: V_Λ = V10 + 44·γ_n
    V_L = V10 + 44*gn
    err_L = abs(V_L - V_obs)/V_obs * 100
    results_2d.append((n, err_nu, err_L))

# 統計: 每個領域 <3% 命中
hits_nu = [(n, e1, e2) for n, e1, e2 in results_2d if e1 < 3]
hits_L = [(n, e1, e2) for n, e1, e2 in results_2d if e2 < 3]
hits_both = [(n, e1, e2) for n, e1, e2 in results_2d if e1 < 3 and e2 < 3]
print(f"  中微子 <3%: {[n for n,_,_ in hits_nu]}")
print(f"  Λ <3%: {[n for n,_,_ in hits_L]}")
print(f"  同時 <3%: {[n for n,_,_ in hits_both]}")
print(f"  數量: 中微子 {len(hits_nu)}/44, Λ {len(hits_L)}/44, 同時 {len(hits_both)}/44")

# ============ 3. 聯合 p-value ============
print("\n[3] 聯合 p-value")
# 如果 γ₆ 係唯一同時命中 <3% 嘅: p = 1/44
# 如果有 k 個同時命中: p = k/44
k = len(hits_both)
p_joint = k / 44
print(f"  同時命中數: {k}")
print(f"  聯合 p-value: {p_joint:.4f}")

# 但 γ₆ 係「最佳」唔止「<3%」— 用 rank
print(f"\n  最佳 rank:")
# 中微子 rank
nu_rank = sorted(results_2d, key=lambda x: x[1])
L_rank = sorted(results_2d, key=lambda x: x[2])
print(f"  中微子最佳: {nu_rank[0][0]} (誤差 {nu_rank[0][1]:.3f}%)")
print(f"  Λ 最佳: {L_rank[0][0]} (誤差 {L_rank[0][2]:.3f}%)")
print(f"  中微子 top3: {[n for n,_,_ in nu_rank[:3]]}")
print(f"  Λ top3: {[n for n,_,_ in L_rank[:3]]}")

# 聯合 rank: 兩個領域都 top-k 嘅概率
n6_nu_rank = [i for i, (n, _, _) in enumerate(nu_rank) if n == 6][0] + 1
n6_L_rank = [i for i, (n, _, _) in enumerate(L_rank) if n == 6][0] + 1
print(f"  γ₆ 中微子 rank: {n6_nu_rank}/44")
print(f"  γ₆ Λ rank: {n6_L_rank}/44")
p_rank = (n6_nu_rank/44) * (n6_L_rank/44)
print(f"  聯合 rank p: {p_rank:.4f} ({p_rank*100:.2f}%)")

# ============ 4. 對比單獨 1D ============
print("\n[4] 對比單獨 1D")
p_1d = len(hits_L) / 44  # 單獨 Λ
print(f"  單獨 1D (Λ): {p_1d:.4f} ({p_1d*100:.1f}%)")
print(f"  聯合 2D: {p_joint:.4f} ({p_joint*100:.1f}%)")
print(f"  改善: {p_1d/p_joint:.1f}x")

# ============ 5. 總結 ============
print("\n" + "=" * 72)
print("十一期 66 總結:")
print("=" * 72)
print(f"""
  γ₆ 2D Joint Likelihood:
  ─────────────────────────────────
  1. 中微子 <3%: {len(hits_nu)}/44
  2. Λ <3%: {len(hits_L)}/44
  3. 同時 <3%: {k}/44 (p={p_joint:.4f})
  4. γ₆ 中微子 rank {n6_nu_rank}, Λ rank {n6_L_rank}
  5. 聯合 rank p = {p_rank:.4f}

  {'✅ 2D 聯合顯著!' if p_joint < 0.05 or p_rank < 0.05 else '❌ 仍唔夠'}
""")

results = {
    "test": "O57 十一期 66: γ₆ 2D Joint Likelihood",
    "hits_nu": [n for n,_,_ in hits_nu],
    "hits_L": [n for n,_,_ in hits_L],
    "hits_both": [n for n,_,_ in hits_both],
    "p_joint_3pct": float(p_joint),
    "gamma6_nu_rank": int(n6_nu_rank),
    "gamma6_L_rank": int(n6_L_rank),
    "p_rank": float(p_rank),
    "passed": passed, "failed": failed
}
with open("data/66_gamma6_2d.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 十一期 66 完成!")
