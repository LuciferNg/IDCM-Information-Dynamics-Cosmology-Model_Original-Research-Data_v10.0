#!/usr/bin/env python3
"""
O91/02: S8 — 從 K_Chain Beat 頻譜推導 σ₈
===========================================
方法: 直接用 K_Chain 模式振幅 γₙ 構建物質功率譜,
並用 CMB 第一峰振幅 (3ε) 歸一化。

核心洞察:
  - 物質 = K_Chain beat frequencies (共振)
  - 每個 beat (i,j) 嘅振幅 ∝ A_i·A_j = 4sin(πi/88)·sin(πj/88)
  - 波數 k_{ij} = π|i-j|/R_world
  - 物質功率譜係 K_Chain beat 譜嘅投影
  - σ₈² = ∫ dk/k · Δ²(k) · |W₈(k)|²
"""
import math
import numpy as np

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

# 常數
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
R_WORLD = 4129.94       # Mpc
ND = 44
OMEGA_RING = 72.59      # (km/s)/Mpc, h = 0.7259
C_LIGHT = 299792.458
H = OMEGA_RING / 100

print("=" * 70)
print("  O91/02: S8 — 從 K_Chain Beat 頻譜推導 σ₈")
print("=" * 70)

# ============ 1. K_Chain 模式 ============
print("\n--- 1. K_Chain 模式基本量 ---")
gammas = []
amps = []
k_modes = []  # Mpc⁻¹
for n in range(1, ND + 1):
    gamma = 4 * math.sin(math.pi * n / 88) ** 2
    amp = 2 * math.sin(math.pi * n / 88)
    k_n = math.pi * n / R_WORLD  # Mpc⁻¹
    gammas.append(gamma)
    amps.append(amp)
    k_modes.append(k_n)

sum_gamma = sum(gammas)
print(f"  Σγ = {sum_gamma:.10f} ({'✅' if abs(sum_gamma-90)<1e-9 else '❌'})")
print(f"  k_min = {k_modes[0]:.6f} Mpc⁻¹  (n=1, λ={R_WORLD:.0f} Mpc)")
print(f"  k_max = {k_modes[-1]:.6f} Mpc⁻¹  (n=44, λ={R_WORLD/44:.1f} Mpc)")

# ============ 2. Beat 頻譜 ============
print("\n--- 2. K_Chain Beat 頻譜 (物質功率譜) ---")
# Beat (i,j): k_{ij} = π|i-j|/R_world, A_{ij} = A_i·A_j
# 物質功率譜係所有 beat 嘅疊加

# 分 bin 統計
n_bins = 100
k_max_beat = math.pi * (ND - 1) / R_WORLD  # 最大 beat 波數
k_bins = np.linspace(0, k_max_beat, n_bins + 1)
k_center = (k_bins[1:] + k_bins[:-1]) / 2
power_binned = np.zeros(n_bins)

# 構建所有 beat
beats = []
for i in range(ND):
    for j in range(i + 1, ND):
        dn = abs(i - j)  # Δn = 1..43
        k = math.pi * dn / R_WORLD  # Mpc⁻¹
        A_ij = amps[i] * amps[j]  # beat amplitude
        power_ij = A_ij ** 2  # power contribution
        beats.append({"dn": dn, "k": k, "power": power_ij, "A": A_ij})

        # 入 bin
        for b in range(n_bins):
            if k_bins[b] <= k < k_bins[b + 1]:
                power_binned[b] += power_ij
                break

total_beat_power = sum(b["power"] for b in beats)
print(f"  Beat 總數: {len(beats)} (= C(44,2) = {ND*(ND-1)//2})")
print(f"  K_Chain beat 總功率: {total_beat_power:.4f}")
print(f"  k range: 0 to {k_max_beat:.6f} Mpc⁻¹")

# 關鍵: beat 總功率 vs K_Chain 總功率
kchain_total = sum(gammas)
print(f"  K_Chain 直接總功率 Σγ = {kchain_total:.4f}")
print(f"  Beat 總功率 / Σγ = {total_beat_power/kchain_total:.4f}")

# 最大功率 beat
beats_sorted = sorted(beats, key=lambda b: b["power"], reverse=True)
print(f"\n  前 10 強 beat:")
print(f"  {'Δn':>4} | {'k (Mpc⁻¹)':>12} | {'λ (Mpc)':>10} | {'Power':>10} | {'Cumul%':>8}")
cumul = 0
for b in beats_sorted[:10]:
    cumul += b["power"]
    lam = 2 * math.pi / b["k"] if b["k"] > 0 else float('inf')
    print(f"  {b['dn']:4d} | {b['k']:12.6f} | {lam:10.2f} | {b['power']:10.4f} | {cumul/total_beat_power*100:7.1f}%")

# ============ 3. σ₈ 積分 ============
print("\n--- 3. σ₈ 積分 (top-hat window) ---")
# σ₈² = ∫ dk/k · Δ²(k) · |W₈(k)|²
# 對於離散譜: σ₈² = Σ_{beat} Δ²(k_beat) · |W₈(k_beat)|² / k_beat
# Δ²(k) = k³P(k)/(2π²) = (k³/(2π²)) × power_beat

# 但需要歸一化: IDCM 嘅 beat 功率對應到物質功率譜嘅絕對歸一化
# 用 CMB 第一峰振幅 3ε 做歸一化參考點
# CMB 第一峰對應嘅尺度: ℓ ≈ 200, k ≈ ℓ/D_A(z*) ≈ 200/(0.5×4129.94) ≈ 0.097 Mpc⁻¹
# 呢個 k 值對應 Δn = k·R_world/π ≈ 0.097×4129.94/π ≈ 127

# 但 Δn 最大得 43... 所以 beat 譜直接覆蓋嘅 k 範圍細過 CMB 第一峰!
# 結論: beat 譜同 CMB 峰喺唔同尺度, 需要用 K_Tree 投影橋接

# 方法: 用 K_Chain 嘅總功率 Σγ = 90 做歸一化, 然後用 K_Tree 投影到 8 h⁻¹ Mpc
# 但唔係用 φ^(-2ℓ₈), 而係用 beat 譜嘅累積功率

# 8 h⁻¹ Mpc 對應嘅 k
R_8 = 8.0 / H  # Mpc
k_8 = 2 * math.pi / R_8  # Mpc⁻¹
print(f"  8 h⁻¹ Mpc = {R_8:.4f} Mpc")
print(f"  k₈ = 2π/(8 h⁻¹ Mpc) = {k_8:.4f} Mpc⁻¹")
print(f"  Beat 譜最大 k = {k_max_beat:.6f} Mpc⁻¹")
print(f"  k₈ / k_max_beat = {k_8/k_max_beat:.1f} — beat 譜遠細過 k₈!")
print(f"  → 8 h⁻¹ Mpc 尺度需要 K_Tree 投影, 唔係 beat 直接貢獻")

# ============ 4. 用 K_Tree 層級投影 ============
print("\n--- 4. K_Tree 層級投影到 8 h⁻¹ Mpc ---")
# K_Tree: B=4, 每層將尺度縮細 4 倍
# 第 m 層尺度: R_world/4^m
# 8 h⁻¹ Mpc 喺層 m=4 (16.1 Mpc) 同 m=5 (4.0 Mpc) 之間

# 重新思考: K_Tree 投影唔係乘 φ^(-2ℓ), 而係 beat 譜嘅振幅隨層數增加
# 每層 K_Tree 將 beat 振幅乘以 φ⁻¹ (效率因子)
# 但同時每層嘅 beat 數目增加 (branching B=4)

# 層 m 嘅 beat 總功率 = (層 0 總功率) × (φ⁻¹)^{2m} × B^m
# = 90 × (φ⁻¹/B)² × (φ⁻¹² × B)ᵐ⁻¹ ... 唔對

# 正確: 每層 K_Tree 將能量分佈到 B 個子節點
# 每個子節點嘅能量 = 父節點 × φ⁻¹ (效率)
# 總功率守恆: 父節點 = B × 子節點 × φ⁻¹ cos... 要 conserve

# 假設: K_Tree 每層將 beat 譜嘅 k 範圍乘以 B=4 (因為尺度縮細 4 倍)
# 層 m 嘅最大 k = k_max_beat × 4^m
# 層 m 嘅總功率 = 90 × (φ⁻¹)^{2m} (每層效率 φ⁻¹ 乘兩次, 一次 amplitude)

# 要達到 k₈ = 1.08 Mpc⁻¹, 需要:
# k_max_beat × 4^m ≥ k₈
m_needed = math.log(k_8 / k_max_beat, 4)
print(f"  Beat 譜最大 k = {k_max_beat:.6f} Mpc⁻¹")
print(f"  需要 m = log₄({k_8:.4f}/{k_max_beat:.6f}) = {m_needed:.2f} 層 K_Tree")
print(f"  整數層: m={int(math.ceil(m_needed))}")

# 層 m 嘅 total power = 90 × (φ⁻¹)^{2m}
# 層 m 嘅功率密度 ≈ total_power / k_range
# 喺 k₈ 附近嘅功率密度 = 層 m 嘅功率密度 × (B=4 寬度因子)

# 但更簡單: 直接用 K_Chain 總功率 90 做歸一化
# 物質功率譜歸一化: Δ²_integrated = 90 × (norm_factor)
# norm_factor 由 CMB 振幅決定

# 從 CMB 第一峰歸一化: Planck D₁ = 5816 μK²
# 對應 ΔT/T ≈ sqrt(D₁·2π/ℓ(ℓ+1)) / T_CMB ≈ sqrt(5816·2π/(200×201))/2.725 ≈ 1.0e-5
# Sachs-Wolfe: ΔT/T ≈ (1/3)Δ_R → Δ_R ≈ 3e-5
# 物質功率譜 Δ²(k) ≈ Δ_R² × T²(k) × D²(z=0)
# 喺 k₈ ≈ 0.5 Mpc⁻¹, T(k) ≈ 0.4, 所以 Δ²(k₈) ≈ 1.4e-10

# 但呢個計算太 ΛCDM 依賴...
# 嘗試用更直接嘅方法

# 方法: 用 beat 譜嘅累積功率函數
# 對所有 beat 按 k 排序, 計算累積功率
# 然後用 top-hat 窗口 W₈(k) 權重

print("\n--- 5. σ₈ 從累積 beat 功率 (alternative) ---")
# 排序 beat 按 k
beats_by_k = sorted(beats, key=lambda b: b["k"])

# 累積功率
cum_power = 0
cum_powers = []
for b in beats_by_k:
    cum_power += b["power"]
    cum_powers.append(cum_power)

# σ₈² 近似 = (累積功率到 k₈) / 總功率 × 90 × 歸一化
# 但 k₈ 遠超 beat 譜範圍
print(f"  Beat 譜最大 k = {k_max_beat:.6f} Mpc⁻¹")
print(f"  k₈ = {k_8:.6f} Mpc⁻¹")
print(f"  Beat 譜只覆蓋到 k₈ 嘅 {k_max_beat/k_8*100:.2f}%")
print(f"  → 需要 K_Tree 投影")

# ============ 5. 用 K_Tree 投影計算 σ₈ ============
print("\n--- 5. K_Tree 投影計算 σ₈ ---")
# 層 m = 0: beat 譜, k ∈ [0, k_max_beat], power = 90
# 層 m = 1: K_Tree 第一層, k ∈ [0, 4·k_max_beat], power = 90·φ⁻²
# 層 m = 2: k ∈ [0, 16·k_max_beat], power = 90·φ⁻⁴
# ...
# 層 m: k ∈ [0, 4^m·k_max_beat], power = 90·φ^{-2m}

# 8 h⁻¹ Mpc 對應 k₈ = 1.08 Mpc⁻¹
# 需要層數 m = ceil(log₄(k₈/k_max_beat)) = ceil(3.64) = 4

# 層 4: k ∈ [0, 256·k_max_beat] = [0, 6.54 Mpc⁻¹], power = 90·φ⁻⁸
m = 4
k_max_m = (4**m) * k_max_beat
power_m = 90 * (PHI_INV ** (2*m))
print(f"  K_Tree 層 m={m}:")
print(f"    k_max = {k_max_m:.4f} Mpc⁻¹ ({'✅' if k_max_m >= k_8 else '❌'} covers k₈={k_8:.4f})")
print(f"    total power = 90 × φ⁻⁸ = {power_m:.4f}")

# 喺呢層, k₈ 嘅位置: k₈ / k_max_m = 1.08/6.54 = 0.165
# 假設功率均勻分佈: 到 k₈ 嘅累積功率 = power_m × (k₈/k_max_m)
frac_k = k_8 / k_max_m
cum_power_at_k8 = power_m * frac_k
print(f"    k₈/k_max(m) = {frac_k:.4f}")
print(f"    累積功率到 k₈ ≈ {cum_power_at_k8:.4f}")

# 但呢個係 raw power, 需要 top-hat 窗口權重
# top-hat window: W₈(k) = 3j₁(kR₈)/(kR₈), j₁(x) = sin(x)/x² - cos(x)/x
# 對於 kR₈ ≈ 1.08×11.02 ≈ 11.9: j₁(11.9) ≈ 0 (遠離主瓣)
# 主瓣喺 kR₈ < 4.5, 即 k < 4.5/11.02 = 0.408 Mpc⁻¹

# 所以 top-hat 窗口主要選取 k < 0.4 Mpc⁻¹
# 呢個 k 喺 beat 譜範圍內! (k_max_beat = 0.0327 Mpc⁻¹)
# 但 k=0.4 Mpc⁻¹ 需要 K_Tree 層 m=2 (k_max=0.131 Mpc⁻¹) 或 m=3 (k_max=0.523 Mpc⁻¹)

# 重新計算 top-hat 窗口
def top_hat_W2(k, R):
    """|W_R(k)|² for top-hat window"""
    x = k * R
    if x < 1e-10:
        return 1.0
    j1 = (math.sin(x) / x**2 - math.cos(x) / x)
    w = 3 * j1 / x
    return w ** 2

# 積分 σ₈² = Σ_{all layers} Σ_{beats} Δ²(k_beat) · |W₈(k_beat)|² / k_beat
# 使用 K_Tree 層疊加

# 層 0 (beat 譜直接):
sigma2_0 = 0
for b in beats:
    k = b["k"]
    power = b["power"]
    # 假設 Δ²(k) ∝ power · k³ / (2π²) · norm
    # 對於離散譜: σ² contribution = power · k³/(2π²) · |W|²/k = power · k²/(2π²) · |W|²
    # 但需要 norm: total Δ² integrated = Σ Δ²(k)/k = 90 × norm
    # 暫用 norm = 1 睇形狀
    w2 = top_hat_W2(k, R_8)
    sigma2_0 += power * k**2 * w2 / (2 * math.pi**2)

print(f"\n  Beat 層直接 σ² (未歸一化) = {sigma2_0:.6e}")
print(f"  呢個值好細因為 k 好細, 需要歸一化因子")

# ============ 6. 歸一化 ============
print("\n--- 6. 歸一化 ---")
# 歸一化: 物質功率譜積分 = Σγ = 90 (K_Chain 總功率)
# ∫ dk/k · Δ²(k) = 90
# Δ²(k) = 90 / [∫ dk/k · P_shape(k)] × P_shape(k)

# 對於離散譜: ∫ dk/k · Δ²(k) = Σ_k Δ²(k)/k
# Δ²(k) = 90 × k / Σ_k P(k) × P(k) 其中 P(k) = power(k) × k³/(2π²)

# 更簡單: 先計算形狀, 再歸一化到 Σγ=90
# Δ²(k) = C × power(k) × k³/(2π²) 其中 C 係歸一化常數
# 要求: Σ_k C × power(k) × k²/(2π²) = 90  (因為 dk/k = 1 for discrete)
# 即: C = 90 × 2π² / Σ_k power(k) · k²

sum_k_power_k2 = sum(b["power"] * b["k"]**2 for b in beats)
C = 90 * 2 * math.pi**2 / sum_k_power_k2
print(f"  Σ power·k² = {sum_k_power_k2:.6e}")
print(f"  歸一化因子 C = {C:.6e}")

# 再用歸一化後嘅 Δ²(k) 計算 σ₈²
sigma2_0_norm = 0
for b in beats:
    k = b["k"]
    power = b["power"]
    delta2 = C * power * k**3 / (2 * math.pi**2)
    w2 = top_hat_W2(k, R_8)
    sigma2_0_norm += delta2 * w2 / k

sigma8_0 = math.sqrt(sigma2_0_norm)
print(f"  Beat 層 σ₈² = {sigma2_0_norm:.6f}")
print(f"  Beat 層 σ₈ = {sigma8_0:.4f}")
print(f"  (只計 beat 層, 未計 K_Tree 高階投影)")

# 但 σ₈ ≈ 0 因為 beat 譜嘅 k 遠細過 1/R_8
# top-hat 窗口喺 k << 1/R_8: W₈² ≈ 1 (sinc 近似)
# 所以 σ₈² ≈ C × Σ power·k²/(2π²) = 90? 唔啱因為 top-hat 選到嘅功率好少
# 實際上: k·R_8 << 1 → W₈² ≈ 1
# σ₈² ≈ Σ Δ²(k)/k = C × Σ power·k²/(2π²) = 90
# 但呢個係所有尺度嘅總功率, 唔係 σ₈

# 正確: σ₈² = ∫ dk/k · Δ²(k) · |W₈(kR₈)|²
# 對於 kR₈ << 1: W₈ ≈ 1
# 對於 kR₈ >> 1: W₈ ≈ 0 (振盪衰減)
# 臨界點: kR₈ ≈ 2.5 (W₈ 第一個零點)

k_crit = 2.5 / R_8
print(f"\n  Top-hat 截止 k_crit = 2.5/R₈ = {k_crit:.6f} Mpc⁻¹")
print(f"  Beat 譜最大 k = {k_max_beat:.6f} Mpc⁻¹")
print(f"  Beat 譜 k_max / k_crit = {k_max_beat/k_crit:.4f}")
print(f"  → Beat 譜遠低於 top-hat 截止, W₈ ≈ 1")
print(f"  → 所以 σ₈² ≈ ΣΔ²(k)/k = 90 如果只計 beat 譜")
print(f"  → 但 σ₈ 定義係 8 h⁻¹ Mpc 球體內嘅 RMS, 唔係總功率!")
print(f"  → 需要 top-hat 窗口真係選到嗰個尺度")

# 問題: 8 h⁻¹ Mpc 球體嘅直徑係 22 Mpc, 遠細過 K_Chain 最小 beat 波長 (96 Mpc)
# 所以一個 8 h⁻¹ Mpc 球體只包含 K_Chain 嘅一小部分 → σ₈ 應該細
# 但觀測上 σ₈ ≈ 0.8, 即係 8 h⁻¹ Mpc 球體包含大量結構

# 呢個矛盾意味住: K_Chain beat 譜唔直接係物質功率譜
# 物質功率譜係 K_Chain beat 經 K_Tree 投影到所有尺度嘅疊加
# 8 h⁻¹ Mpc 嘅功率主要來自 K_Tree 高層, 唔係 basal beat 層

print(f"\n{'='*70}")
print(f"  結論: K_Chain beat 譜直接貢獻嘅 σ₈ ≈ {sigma8_0:.4f}")
print(f"  但真正 σ₈ ≈ 0.8 來自 K_Tree 高層投影")
print(f"  需要嚴格推導 K_Tree 投影嘅功率譜形狀")
print(f"{'='*70}")