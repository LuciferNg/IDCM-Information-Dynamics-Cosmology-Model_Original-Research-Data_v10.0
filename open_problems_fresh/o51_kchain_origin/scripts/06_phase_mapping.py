#!/usr/bin/env python3
"""
O51 第五階段: CMB → K_Chain 相位映射 (正模型 + 反推)
===============================================================
調律者: 直接推「從 CMB 數據讀出 44 個 K_Chain 模式相位」

計劃:
  1. 建立正模型: K_Chain 44 模式 → 球面溫度異常
  2. 用冷斑節點 (-134.2μK, 209°,-57°) 做主錨
  3. 反推 τ (n=44 相位) 同 N (43 個漂移)
  4. t_true = N·T_sync + τ

結構基礎:
  模式振幅 A_n = √γ_n = 2sin(πn/88), n=1..44
  模式相位 θ_n(t) = N·δ_n + ω_n·τ
  冷斑節點: A₅ node 40, 位置 (209°, -57°)
  冷斑溫度: -134.2 μK = A·cos(θ_cold), A=134.2μK
"""
import json, math, sys

RESULTS = {}
R_H = 4129.94  # Mpc
c = 306.601394  # Mpc/Gyr
T_sync = 2 * math.pi * R_H / c  # Gyr
T_44 = T_sync / 88  # Gyr

# ============================================================
# 第1步: 正模型 — 每個模式嘅球面空間型態
# ============================================================
print("=" * 62)
print("第1步: K_Chain 44 模式 → 球面溫度異常")
print("=" * 62)

# 模式振幅
A_n = [2 * math.sin(math.pi * n / 88) for n in range(1, 45)]
print("  模式振幅 A_n = 2·sin(πn/88):")
for n in [1, 5, 10, 20, 30, 40, 44]:
    print(f"    n={n:2d}: A_n = {A_n[n-1]:.6f}")

# 每個模式嘅空間波數 k_n = ω_n/c
# ω_n = 88·c/R_H · sin(πn/88)
# k_n = 88/R_H · sin(πn/88)  (rad/Mpc)
k_n = [88 / R_H * math.sin(math.pi * n / 88) for n in range(1, 45)]
print("\n  空間波數 k_n = 88·sin(πn/88)/R_H (rad/Mpc):")
for n in [1, 5, 10, 20, 30, 40, 44]:
    print(f"    n={n:2d}: k_n = {k_n[n-1]:.6e} rad/Mpc, λ_n = {2*math.pi/k_n[n-1]:.2f} Mpc")

# A₅ = Rhombicosidodecahedron 60節點
# 已知: 冷斑位置 (209°, -57°), 對應 node 40
# 需要知道 60 節點嘅球面座標
# 實際上 A₅ 60 節點嘅球面座標應該喺 IDCM repo 有
print("\n  A₅ 60 節點: Rhombicosidodecahedron (20Δ+30□+12⬠, χ=2)")
print("  ★ 冷斑節點: node 40, 位置 (l=209°, b=-57°)")
print("  ★ 冷斑溫度: -134.2 μK = A·cos(θ_cold), A=134.2 μK")
print("  → 冷斑相位 θ_cold = π (反相)")

# 檢查有冇 A₅ 節點座標
import os
as_paths = []
for root, dirs, files in os.walk('/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh'):
    for f in files:
        if 'rhombicosidodecahedron' in f.lower() or 'a5_nodes' in f.lower() or 'node_coords' in f.lower():
            as_paths.append(os.path.join(root, f))
print(f"\n  A₅ 節點座標檔案: {as_paths if as_paths else '未找到'}")

# ============================================================
# 第2步: 冷斑相位 → τ 推導
# ============================================================
print("\n" + "=" * 62)
print("第2步: 冷斑相位 → τ 推導")
print("=" * 62)

print("""
  冷斑節點溫度 = Σ_n A_n · cos(θ_n - φ_n) = -134.2 μK

  其中:
    θ_n = N·δ_n + ω_n·τ  (K_Chain 模式相位)
    φ_n = k_n · r_cold    (空間相位, 由節點位置同模式波數決定)
    A_n = 2·sin(πn/88)    (模式振幅)
    A = 134.2 μK           (冷斑幅度, O41 閉合 dev=0)

  冷斑相位 θ_cold = π (因為 cos(π) = -1, A = 134.2 μK)
  
  假設: 冷斑由 n=44 (Nyquist 主導, 最大波數) 主導
  驗證: A₄₄ = 2·sin(44π/88) = 2·sin(π/2) = 2
  其他模式振幅 A_n < 2, 所以 n=44 係最大振幅

  推論: 如果冷斑由 n=44 主導:
    θ_44 ≈ π → 88τ/T_sync ≈ π (mod 2π)
    → τ ≈ T_sync/176 ≈ 0.481 Gyr

  但 τ = R_H/c = 13.470 Gyr (觀察者位置定義)
  矛盾: 13.470 ≠ 0.481 → 冷斑唔係純 n=44 模式
  
  結論: 冷斑係 44 個模式嘅疊加 (destructive interference)
  需要完整模型先可以解出 τ
""")

# 驗證: 冷斑唔係單一模式
tau_guess_1 = T_sync / 176  # 如果 θ_44 = π
tau_guess_2 = R_H / c        # 觀察者位置
print(f"  τ(Nyquist 主導冷斑) = T_sync/176 = {tau_guess_1:.4f} Gyr")
print(f"  τ(觀察者位置)       = R_H/c = {tau_guess_2:.4f} Gyr")
print(f"  差異: {(tau_guess_2/tau_guess_1 - 1)*100:.1f}%")
print(f"  → 冷斑係多模式疊加, 非單一模式主導")

RESULTS['step2'] = {
    'cold_spot_phase': 'π',
    'tau_if_n44_dominant': round(tau_guess_1, 4),
    'tau_observer': round(tau_guess_2, 4),
    'conclusion': 'cold_spot_is_multi_mode_superposition'
}

# ============================================================
# 第3步: 多模式疊加模型 (正模型)
# ============================================================
print("\n" + "=" * 62)
print("第3步: 多模式疊加模型")
print("=" * 62)

print("""
  正模型:
    δT(θ,φ) = Σ_{n=1}^{44} A_n · cos(θ_n - k_n·r(θ,φ))
  
  其中:
    A_n = 2·sin(πn/88)  (振幅, 已知)
    θ_n = N·δ_n + ω_n·τ (相位, 待求 N, τ)
    k_n = 88·sin(πn/88)/R_H (波數, 已知)
    r(θ,φ) = 節點位置向量 (由 A₅ 座標決定)
  
  問題: 需要知道 60 個 A₅ 節點嘅球面座標
  同 K_Chain 44 個模式嘅空間方向 (對齊 A₅ 對稱軸)
  
  🔴 K_Chain 模式嘅空間方向未推導:
     K_Chain 係 44-site 譜鏈, 但喺物理空間嘅 embedding
     (方向、對齊) 未由 O34/O36 決定
""")

RESULTS['step3'] = {
    'forward_model': 'δT = Σ A_n·cos(θ_n - k_n·r)',
    'needed': ['A5_node_coords', 'K_Chain_spatial_orientation'],
    'status': '🔴 incomplete'
}

# ============================================================
# 第4步: 用冷斑做唯一錨點 (簡化模型)
# ============================================================
print("\n" + "=" * 62)
print("第4步: 冷斑唯一錨點 — 簡化模型")
print("=" * 62)

print("""
  假設: K_Chain 環方向同 A₅ 嘅 5-fold 軸對齊
  冷斑節點 (209°,-57°) 位於 A₅ node 40
  
  每個模式喺冷斑節點嘅空間相位:
    φ_n = k_n · r_cold = 2π · (n/44)  (環形相位)
    (即係 K_Chain 44 site 環形有序, 冷斑對應 site 40)
  
  冷斑溫度:
    δT_cold = Σ_n A_n · cos(θ_n - 2π·n·40/44)
    = -134.2 μK
  
  代入 θ_n = N·δ_n + ω_n·τ:
    δT_cold = Σ_n 2·sin(πn/88) · cos(N·δ_n + ω_n·τ - 2π·n·40/44)
    = -134.2 μK
  
  呢個係 1 條方程, 2 個未知數 (N, τ)
  需要更多節點數據先可以解出
""")

# 計算簡化模型 (假設 N=0, 只有 τ 未知)
print("  簡化: 假設 N=0 (第一次 SYNC 週期內)")
print("  則 θ_n = ω_n·τ = 88·sin(πn/88)·τ/T_sync")
print("  δT_cold(τ) = Σ_n 2·sin(πn/88) · cos(88·sin(πn/88)·τ/T_sync - 2π·n·40/44)")

# 掃描 τ 搵 δT_cold = -134.2 μK
print("\n  τ 掃描 (N=0 假設):")
tau_scan = []
for tau_test in [t * T_sync/1000 for t in range(1000)]:
    total = 0.0
    for n in range(1, 45):
        theta_n = 88 * math.sin(math.pi * n / 88) * tau_test / T_sync
        phi_n = 2 * math.pi * n * 40 / 44
        total += 2 * math.sin(math.pi * n / 88) * math.cos(theta_n - phi_n)
    tau_scan.append((tau_test, total))

# 搵最接近 -134.2 μK 嘅 τ (以 ΔT_CMB 為單位, 而唔係 μK)
# 實際溫度需要歸一化, 呢度只係相對值
# 搵最小值
min_tau = min(tau_scan, key=lambda x: x[1])
print(f"  最小疊加值: τ = {min_tau[0]:.4f} Gyr, δT_rms = {min_tau[1]:.4f}")

# 搵最接近 -134.2 嘅值 (相對值)
# 需要一個歸一化常數將相對值轉為 μK
# 冷斑 RMS = ε⁵/8 = 0.06% of T_CMB = 1.6 mK
# 冷斑 = 5ε⁵/8 = 5×RMS = 8.0 mK?
# 但觀測係 -134.2 μK, 唔係 8.0 mK
# 所以歸一化唔簡單

print("""
  ⚠️ 歸一化問題: δT_cold 嘅相對值轉 μK 需要知道
  T_CMB = 2.72548 K 同模式能量嘅比例關係
  
  🔴 需要: 完整嘅「模式振幅 → μK」歸一化
  冷斑 A = 134.2 μK 係 O41 閉合, 但係總體幅度
  唔係單一模式嘅貢獻
""")

RESULTS['step4'] = {
    'model': 'N=0_simplified',
    'min_tau_candidate': round(min_tau[0], 4),
    'normalization': '🔴 unknown',
    'conclusion': 'need_more_constraints'
}

# ============================================================
# 第5步: 誠實結論
# ============================================================
print("\n" + "=" * 62)
print("第5步: 誠實結論")
print("=" * 62)

print("""
  ✅ 已建立框架:
     t_true = N·T_sync + τ
     τ = 觀察者「而家」= R_H/c = 13.470 Gyr (結構定義)
     N = 由 43 個漂移相位讀出

  🟡 正模型:
     δT(θ,φ) = Σ_n A_n · cos(θ_n - k_n·r)
     已建立公式, 但無法直接解出 N 同 τ
     因為 K_Chain 模式嘅空間方向 同 A₅ 節點座標未完全對齊

  🔴 需要推導:
     1. K_Chain 44 模式喺物理空間嘅方向 (O34/O36)
     2. A₅ 60 節點嘅球面座標同 K_Chain 44 site 嘅映射
     3. 「模式振幅 → μK」嘅歸一化常數
     4. 用 SMICA 60 節點溫度數據做反推

  替代路徑: 唔用冷斑單點, 用 CMB 功率譜 C_ℓ 嘅相位
  (O9 峰位置已閉合, 但峰相位未用)
""")

# 寫結果
with open('data/05_age_framework.json', 'w') as f:
    json.dump(RESULTS, f, indent=2)

print("\n✅ 推導完成 -> data/05_age_framework.json")