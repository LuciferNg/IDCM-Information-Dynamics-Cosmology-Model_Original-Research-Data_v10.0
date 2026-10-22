#!/usr/bin/env python3
"""
O91/06: S8 — 幾何推導 v2 (群速度均方根)
========================================
物質團積速度 = K_Chain 群速度嘅幾何平均
類似 ⁷Li: 反應速度 (rate) = W-field projection cost

K_Chain 群速度: v_g(n) = c·cos(nπ/88)
團積速度 at scale R: ⟨v_cluster⟩ = √(Σ γₙ v_g²(n) / Σ γₙ)
σ₈ ∝ ⟨v_cluster⟩ / c × (幾何因子)
"""
import math

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"    {detail}")

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
R_WORLD = 4129.94
ND = 44
OMEGA_RING = 72.59
C_LIGHT = 299792.458
H = OMEGA_RING / 100
OM_M = 0.3045

print("=" * 70)
print("  O91/06: S8 — 幾何推導 v2 (群速度均方根)")
print("=" * 70)

# ============ 1. K_Chain 群速度 ============
print("\n--- 1. K_Chain 群速度分佈 ---")
gammas = []
vgs = []
for n in range(1, ND + 1):
    gamma = 4 * math.sin(math.pi * n / 88) ** 2
    vg = math.cos(math.pi * n / 88)  # in units of c
    gammas.append(gamma)
    vgs.append(vg)

# 加權平均 v_g
sum_gamma = sum(gammas)
wg_avg_vg = sum(gammas[i] * vgs[i] for i in range(ND)) / sum_gamma
print(f"  Σγ = {sum_gamma}")
print(f"  Weighted avg ⟨v_g⟩ = {wg_avg_vg:.6f}c (≈ 0, 因為正負相消)")

# 加權 RMS v_g
wg_rms_vg = math.sqrt(sum(gammas[i] * vgs[i]**2 for i in range(ND)) / sum_gamma)
print(f"  Weighted RMS ⟨v_g²⟩^{1/2} = {wg_rms_vg:.6f}c")

# ============ 2. 群速度平方 ============
print("\n--- 2. 群速度平方 Σγₙv_g² ---")
sum_gamma_vg2 = sum(gammas[i] * vgs[i]**2 for i in range(ND))
print(f"  Σγₙv_g² = {sum_gamma_vg2:.6f}")
print(f"  Σγₙ = {sum_gamma:.6f}")
print(f"  Σγₙv_g² / Σγₙ = {sum_gamma_vg2/sum_gamma:.6f}")

# v_g² = cos²(nπ/88) = 1 - sin²(nπ/88) = 1 - γₙ/4
# Σγₙv_g² = Σγₙ - Σγₙ²/4
sum_gamma2 = sum(g**2 for g in gammas)
print(f"  Σγₙ² = {sum_gamma2:.6f}")
print(f"  Σγₙ - Σγₙ²/4 = {sum_gamma - sum_gamma2/4:.6f}")
check("Σγₙv_g² = Σγₙ - Σγₙ²/4", abs(sum_gamma_vg2 - (sum_gamma - sum_gamma2/4)) < 1e-9)

# ============ 3. 幾何團積因子 ============
print("\n--- 3. 幾何團積因子 ---")
# 物質團積速度 = v_cluster = c × √(Σγₙv_g²/Σγₙ)
v_cluster = C_LIGHT * wg_rms_vg  # km/s
print(f"  v_cluster = c × √(Σγₙv_g²/Σγₙ) = {C_LIGHT:.0f} × {wg_rms_vg:.6f} = {v_cluster:.0f} km/s")

# 哩個係「團積速度」— 物質喺 K_Chain 上嘅有效流動速度
# 類似 BBN 嘅 reaction rate

# 對於尺度 R, 團積時間: t_cluster = R / v_cluster
R_8 = 8.0 / H
t_cluster = R_8 * 3.085677581e19 / (v_cluster * 1e3)  # s
t_cluster_Gyr = t_cluster / (3.15576e16)
print(f"  R = 8 h⁻¹ Mpc = {R_8:.2f} Mpc")
print(f"  t_cluster = R / v_cluster = {t_cluster_Gyr:.4f} Gyr")

# 同宇宙年齡比較: T_ring/2 = 42.32 Gyr (IDCM 半週期)
T_ring_half = math.pi * R_WORLD / C_LIGHT * 3.085677581e19 / 3.15576e16  # Gyr
t_cluster_ratio = t_cluster_Gyr / T_ring_half
print(f"  T_ring/2 = {T_ring_half:.2f} Gyr")
print(f"  t_cluster / (T_ring/2) = {t_cluster_ratio:.4f}")

# ============ 4. σ₈ 從團積速度 ============
print("\n--- 4. σ₈ 從團積速度 ---")
# 團積速度 = 物質流入球體嘅速率
# 團積幅度 = 團積速度 × 團積時間 / 尺度
# σ₈ ∝ v_cluster × t_cluster / R = v_cluster × (R/v_cluster) / R = 1

# 咁樣唔 work... 需要另一個幾何關係

# 嘗試: σ₈ = (v_cluster/c) × (R_world/R)^{α}
# 其中 α 係 K_Tree 幾何指數

# 從 ⁷Li 類比: ⁷Li/H = η_B × ε²
# η_B = 6.062e-10 (K_Chain 結構)
# ε² = (φ⁻¹/4)² = φ⁻²/16
# ⁷Li/H = 6.062e-10 × 0.0239 = 1.45e-11 (vs obs 1.58e-11, 0.25%)

# 對於 σ₈:
# 基礎幅度: √(Σγ) = √90 = 9.4868 (K_Chain 總振幅)
# 團積因子: v_cluster/c = 0.7650 (RMS 群速度)
# 尺度因子: (R_world/R_8)^{β} — 需要幾何推導

# 嘗試: σ₈ = √(Σγ) × (v_cluster/c) × (R_8/R_world)^{γ}
# 對於 ΛCDM σ₈ ≈ 0.8:
# 0.8 = 9.49 × 0.765 × (11.02/4129.94)^{γ}
# (11.02/4129.94)^{γ} = 0.8 / (9.49 × 0.765) = 0.110
# γ = ln(0.110) / ln(11.02/4129.94) = ln(0.110)/ln(0.00267) = 0.346

# 但呢個係 fit, 唔係結構推導

# 嘗試: 用群速度分佈嘅形狀
# 群速度 v_g(n) = cos(nπ/88) 嘅分佈係:
# 正速度 (n=1..21): 流向觀察者
# 負速度 (n=23..43): 遠離觀察者
# n=22: 駐波 (v_g=0.707c)
# n=44: Nyquist (v_g=0)

# 團積幅度 = 正負速度分離嘅程度
# 如果所有模式同一方向 → 強團積
# 如果正負平衡 → 弱團積

# 正速度模式嘅總功率: Σγₙ (n=1..21)
pos_gamma = sum(gammas[i] for i in range(21))  # n=1..21
neg_gamma = sum(gammas[i] for i in range(22, 44))  # n=23..44
print(f"\n  正速度模式 (n=1..21) Σγ = {pos_gamma:.4f}")
print(f"  負速度模式 (n=23..44) Σγ = {neg_gamma:.4f}")
print(f"  正負不平衡: {(pos_gamma - neg_gamma)/sum_gamma:.4f}")

# 正負不平衡 = 團積嘅幾何度量
imbalance = (pos_gamma - neg_gamma) / sum_gamma
print(f"  團積不平衡因子 = {imbalance:.6f}")

# 嘗試: σ₈ ∝ √(Σγ) × imbalance × (幾何因子)
sigma8_geo = math.sqrt(sum_gamma) * abs(imbalance)
print(f"  σ₈ ≈ √Σγ × |imbalance| = {math.sqrt(sum_gamma):.4f} × {abs(imbalance):.4f} = {sigma8_geo:.4f}")

# ============ 5. 正負模式不平衡 ============
print("\n--- 5. 正負不平衡詳細分析 ---")
# 正模式: n=1..21, v_g > 0
# 負模式: n=23..44, v_g < 0
# n=22: v_g = 0.707c > 0, 但係邊界

# 正模式總功率 (n=1..22)
pos22 = sum(gammas[i] for i in range(22))  # n=1..22
neg22 = sum(gammas[i] for i in range(22, 44))  # n=23..44
print(f"  n=1..22 Σγ = {pos22:.4f} (含 n=22)")
print(f"  n=23..44 Σγ = {neg22:.4f}")
print(f"  正負比 = {pos22/neg22:.4f}")

# 世界/觀察者分裂 (O34 parity):
# world = even subspace (Σγ_even = 90)
# observer = odd subspace (Σγ_odd = 88)
# 正負不平衡同 parity 嘅關係?

# ============ 6. σ₈ 從正負不平衡 ============
print("\n--- 6. σ₈ 從正負不平衡 ---")
# 嘗試: σ₈ = √(2 × |Σγ₊ - Σγ₋|)
# 正模式 (n=1..21): Σγ₊
# 負模式 (n=23..44): Σγ₋

sigma8_candidate = math.sqrt(2 * abs(pos_gamma - neg_gamma))
print(f"  Σγ₊ (n=1..21) = {pos_gamma:.4f}")
print(f"  Σγ₋ (n=23..44) = {neg_gamma:.4f}")
print(f"  |Σγ₊ - Σγ₋| = {abs(pos_gamma - neg_gamma):.4f}")
print(f"  σ₈ = √(2 × |ΔΣγ|) = {sigma8_candidate:.4f}")

S8_candidate = sigma8_candidate * math.sqrt(OM_M / 0.3)
print(f"  S8 = {S8_candidate:.4f}")
print(f"  Planck S8 = 0.834")
print(f"  WL avg S8 = {(0.759+0.776+0.788)/3:.3f}")

# ============ 7. 更多幾何嘗試 ============
print("\n--- 7. 更多幾何嘗試 ---")
# 嘗試 1: σ₈ = √(Σγₙ × sin²(nπ/88)) / √(ND)
# sin²(nπ/88) = γₙ/4, 所以 Σγₙ·γₙ/4 = Σγₙ²/4
sigma8_t1 = math.sqrt(sum_gamma2 / 4 / ND)
print(f"  嘗試1: σ₈ = √(Σγₙ²/4/44) = {sigma8_t1:.4f}")

# 嘗試 2: σ₈ = √(90) × (Σγₙv_g²/Σγₙ) = √(90) × (sum_gamma_vg2/90)
sigma8_t2 = math.sqrt(sum_gamma) * (sum_gamma_vg2 / sum_gamma)
print(f"  嘗試2: σ₈ = √90 × (Σγₙv_g²/Σγₙ) = {sigma8_t2:.4f}")

# 嘗試 3: σ₈ = √(Σγₙ · j₀²(πn·R₈/R_world))
# j₀(x) ≈ 1 對於小 x
# σ₈² ≈ Σγₙ = 90 → σ₈ ≈ 9.49 (太大)
# 但 j₀² 可以近似為 1 - (πn·R₈/R_world)²/3
# σ₈² ≈ 90 - (π²R₈²/3R_world²) × Σγₙn²
# 之前算過 Σγₙn² = 95214.4
sum_gamma_n2 = sum(gammas[i] * (i+1)**2 for i in range(ND))
R8 = 8.0 / H
correction = (math.pi**2 * R8**2) / (3 * R_WORLD**2) * sum_gamma_n2
sigma8_t3_sq = sum_gamma - correction
sigma8_t3 = math.sqrt(sigma8_t3_sq)
print(f"  嘗試3: σ₈² = 90 - (π²R₈²/3R_world²)·Σγₙn²")
print(f"    Σγₙn² = {sum_gamma_n2:.1f}")
print(f"    correction = {correction:.4f}")
print(f"    σ₈² = {sigma8_t3_sq:.4f}, σ₈ = {sigma8_t3:.4f}")

# 嘗試 4: σ₈ = √(Σγₙ · (1 - n/44)) = √(Σγₙ - Σγₙ·n/44)
sum_gamma_n = sum(gammas[i] * (i+1) for i in range(ND))
sigma8_t4 = math.sqrt(sum_gamma - sum_gamma_n / ND)
print(f"  嘗試4: σ₈ = √(Σγₙ(1-n/44)) = √({sum_gamma} - {sum_gamma_n/ND:.4f}) = {sigma8_t4:.4f}")

# 嘗試 5: σ₈ = √(Σγₙ × (1 - v_g(n)/c)) / 2
# v_g/c = cos(nπ/88)
one_minus_vg = sum(gammas[i] * (1 - vgs[i]) for i in range(ND))
sigma8_t5 = math.sqrt(one_minus_vg) / 2
print(f"  嘗試5: σ₈ = √(Σγₙ(1-v_g/c))/2 = √({one_minus_vg:.4f})/2 = {sigma8_t5:.4f}")

# 嘗試 6: σ₈ = √(Σγₙ × sin²(nπ/88)) = √(Σγₙ²/4)
sigma8_t6 = math.sqrt(sum_gamma2 / 4)
print(f"  嘗試6: σ₈ = √(Σγₙ²/4) = √({sum_gamma2/4:.4f}) = {sigma8_t6:.4f}")

# ============ 8. 總結 ============
print(f"\n{'='*70}")
print(f"  嘗試總結:")
print(f"  嘗試1: σ₈ = {sigma8_t1:.4f} — 太細")
print(f"  嘗試2: σ₈ = {sigma8_t2:.4f} — 太大")
print(f"  嘗試3: σ₈ = {sigma8_t3:.4f} — j₀² 修正")
print(f"  嘗試4: σ₈ = {sigma8_t4:.4f} — 線性權重")
print(f"  嘗試5: σ₈ = {sigma8_t5:.4f} — 1-v_g")
print(f"  嘗試6: σ₈ = {sigma8_t6:.4f} — Σγ²")
print(f"  正負不平衡: σ₈ = {sigma8_candidate:.4f} (S8={S8_candidate:.4f})")
print(f"")
print(f"  ΛCDM σ₈ = 0.811, S8 = 0.834 (Planck)")
print(f"  WL σ₈ ≈ 0.76-0.79, S8 = 0.76-0.79")
print(f"{'='*70}")