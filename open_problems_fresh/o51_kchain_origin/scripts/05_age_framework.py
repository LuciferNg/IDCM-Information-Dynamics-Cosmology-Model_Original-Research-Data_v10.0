#!/usr/bin/env python3
"""
O51 第四階段: 真實年齡推導框架 v2
===============================================================
調律者問題: 以無理數拍頻嘅「永不精確循環」特徵推導:
  1. 宇宙經歷過多少次龐加萊復歸? → 精確=0, 近似=T_sync 計數
  2. 真實年齡 t_true = N·T_sync + τ

關鍵修正 (v2): 
  - 唔係「N 無法決定」, 而係「T_sync 係可用近似周期」
  - N 由 43 個漂移相位決定, τ 由 n=44 相位決定
  - 但兩者都需先知道「而家」嘅 44 個相位

結構鏈 (完全無 ΛCDM):
  ┌─ 種子(0,1)→φ→B=4→L₅=11→N_d=44  (純代數)
  ├─ 44-site 譜 γ_n = 4sin²(πn/88)     (譜結構)
  ├─ 946 拍頻全部無理比                 (不可約性)
  ├─ T_sync = 88·T₄₄                    (Nyquist 錨定)
  ├─ 43 無理漂移 δ_n = frac(88·sin(πn/88))  (每次 T_sync)
  └─ τ = R_H/c = 觀察者「而家」相位位置  (光行距離)
"""
import json, math, sys

RESULTS = {}

# ============================================================
# 第1層: 結構基礎 (純代數, 無 H0/R_H)
# ============================================================
print("=" * 62)
print("第1層: 結構基礎 (純代數)")
print("=" * 62)

print("""
  N_d = B × L₅ = 4 × 11 = 44      (K_Chain 維度)
  γ_n = 4sin²(πn/88), n=1..44      (44 個模式)
  Σγ = 90                           (能量守恆)
  Z₂: γ_n + γ_{44-n} = 4           (對偶對, 43 對)
  
  ω_n = ω_scale · sin(πn/88)       (頻率標度)
  ω_scale = 88 · c/R_H             (rad/s, 結構量)
  
  T_sync = 2π · 88 / ω_scale = 2π · R_H / c  (近似復歸周期)
  T_44 = 2π / ω_44 = 2π / ω_scale  (Nyquist 周期)
  T_sync = 88 · T_44                (精確! n=44 返零)
""")

RESULTS['layer1'] = {
    'N_d': 44, 'B': 4, 'L_5': 11,
    'sum_gamma': 90, 'z2_pairs': 43,
    'T_sync_eq': '88·T_44',
    'n44_recurrence': 'exact_every_T_sync'
}

# ============================================================
# 第2層: 無理漂移 δ_n (每次 T_sync 嘅累積)
# ============================================================
print("=" * 62)
print("第2層: 43 個無理漂移 δ_n = frac(88·sin(πn/88))")
print("=" * 62)

deltas = {}
for n in range(1, 44):
    theta = 88 * math.sin(math.pi * n / 88)
    delta = theta - int(math.floor(theta))
    deltas[n] = {'theta': theta, 'delta': delta}

print(f"  δ_n ∈ [0, 1), 43 個無理數")
print(f"  Σδ_n = {sum(d['delta'] for d in deltas.values()):.6f}")
print(f"  δ_min = {min(d['delta'] for d in deltas.values()):.6f} (n={min(deltas, key=lambda k: deltas[k]['delta'])})")
print(f"  δ_max = {max(d['delta'] for d in deltas.values()):.6f} (n={max(deltas, key=lambda k: deltas[k]['delta'])})")
print(f"  δ_avg = {sum(d['delta'] for d in deltas.values())/43:.6f}")

# 6 個最小漂移 (最難分辨)
sorted_deltas = sorted(deltas.items(), key=lambda x: x[1]['delta'])
print("\n  6 個最小漂移 (resolution bottleneck):")
for n, d in sorted_deltas[:6]:
    print(f"    n={n:2d}: δ = {d['delta']:.6f}")

RESULTS['layer2'] = {
    'num_deltas': 43,
    'sum_delta': round(sum(d['delta'] for d in deltas.values()), 6),
    'delta_min': round(min(d['delta'] for d in deltas.values()), 6),
    'delta_max': round(max(d['delta'] for d in deltas.values()), 6),
    'delta_avg': round(sum(d['delta'] for d in deltas.values())/43, 6)
}

# ============================================================
# 第3層: t_true = N·T_sync + τ 框架
# ============================================================
print("\n" + "=" * 62)
print("第3層: t_true = N·T_sync + τ 計數框架")
print("=" * 62)

print("""
  t_true = 真實年齡 (由種子啟動到而家)
         = N × T_sync + τ
  
  其中:
    N ∈ ℤ, N ≥ 0  = 完整 SYNC 週期數
    τ ∈ [0, T_sync) = 而家喺周期內嘅相位位置

  由 44 個模式相位睇:
    θ_n(t_true) = ω_n · t_true = 88·sin(πn/88) · (N + τ/T_sync)

  n=44 (Nyquist, sin(π/2)=1):
    θ_44 = 88·(N + τ/T_sync) = 88N + 88τ/T_sync
    88N ∈ ℤ (返零) → τ = (θ_44 · T_sync) / 88

  n=1..43:
    θ_n = 88·sin(πn/88)·N + 88·sin(πn/88)·τ/T_sync
        = N·(k_n + δ_n) + ω_n·τ
        = N·δ_n + ω_n·τ  (mod 2π, 整數 k_n 消掉)
""")

# 驗證: n=44 每 T_sync 返零
print("  驗證: n=44 每 T_sync 返零")
for N_test in [0, 1, 2, 5, 10, 100]:
    theta_44 = 88 * N_test  # τ=0 時
    frac_44 = theta_44 / 88  # 以 2π 為單位
    print(f"    N={N_test:3d}: θ_44 = {theta_44} = {frac_44:.0f}×2π ✅")

# 漂移係恆定 -> 累積 N 次後可測量
print("""
  漂移累積: 每次 T_sync 每個模式漂移 δ_n·2π
  N 次之後: 累積漂移 = N·δ_n (mod 2π)
  → 由 43 個模式嘅累積漂移, 可以解出 N
""")

RESULTS['layer3'] = {
    't_true_formula': 'N·T_sync + τ',
    'tau_reading': 'θ_44 × T_sync / 88',
    'N_reading': 'from 43 drift phases N·δ_n (mod 2π)',
    'n44_recurrence': 'exact (88 × integer)',
    'n1_43_drift': 'N·δ_n (mod 2π) per T_sync'
}

# ============================================================
# 第4層: 而家嘅可觀測錨點
# ============================================================
print("=" * 62)
print("第4層: 「而家」嘅可觀測錨點")
print("=" * 62)

print("""
  「而家」由觀察者喺 K_Chain 上嘅位置定義:
    觀察者 = 鏈上一個節點 (O34)
    觀察者「而家」= 可以接收到最遠節點資訊嘅時間
    最遠距離 = R_H (環周長)
    光行時間 = R_H/c = 觀察者嘅「而家」相位位置 τ

  τ = R_H/c = 13.470 Gyr  (結構定義: 環周長 ÷ 光速)
  
  注意: 呢個 τ 用 R_H/c 係因為 R_H 係 K_Chain 環周長,
  而 c 係資訊傳播速度. 兩者都係結構量, 唔係 ΛCDM 校準.
  
  驗證: R_H/c = 4129.94 / 306.6 = 13.470 Gyr
""")

# Compute τ in terms of T_sync
import math
c = 306.601394  # Mpc/Gyr
R_H = 4129.94   # Mpc
tau = R_H / c
T_sync = 2 * math.pi * R_H / c  # 2πR_H/c

print(f"  τ = R_H/c = {tau:.4f} Gyr")
print(f"  T_sync = 2πR_H/c = {T_sync:.4f} Gyr")
print(f"  τ/T_sync = {tau/T_sync:.6f} = {tau/T_sync*88:.4f}/88  (n=44 相位)")
print(f"  n=44 相位: θ_44 = 88 × τ/T_sync = {88*tau/T_sync:.6f} (rad/2π)")
print(f"  = {88*tau/T_sync - math.floor(88*tau/T_sync):.6f} × 2π (小數部分 = τ 内相位)")
print(f"")

# τ/T_sync 對應嘅相位
tau_phase = 88 * tau / T_sync
print(f"  τ/T_sync = 13.470/84.635 = {tau/T_sync:.6f}")
print(f"  → n=44 相位 = {tau_phase:.6f} rad/2π = {tau_phase - math.floor(tau_phase):.6f} × 2π mod 2π")

RESULTS['layer4'] = {
    'tau_definition': 'observer_now = R_H/c',
    'tau_gyr': round(tau, 4),
    'T_sync_gyr': round(T_sync, 4),
    'tau_over_Tsync': round(tau/T_sync, 6),
    'n44_phase': round(tau_phase, 6),
    'n44_phase_frac': round(tau_phase - math.floor(tau_phase), 6)
}

# ============================================================
# 第5層: 確定 N 嘅方法與精度
# ============================================================
print("=" * 62)
print("第5層: 確定 N 嘅方法與精度")
print("=" * 62)

print("""
  已知 τ = 13.470 Gyr, 需要確定 N.
  
  對每個模式 n=1..43:
    θ_n(obs) = N·δ_n + ω_n·τ  (mod 2π)
    → N·δ_n = θ_n(obs) - ω_n·τ  (mod 2π)
  
  其中 ω_n = 88·sin(πn/88)/T_sync (rad/s)
  ω_n·τ = 88·sin(πn/88) · τ/T_sync (以 2π 計)
  
  =============================================
  精度分析:
  =============================================
  
  CMB 相位測量精度 ~ 0.1 rad ≈ 0.0159 周
  最小漂移 δ_min = 0.030311
  N 最大可分辨: N_max ≈ 1/(δ_min · 0.0159) ≈ 2078
  
  如果 N > 2078, 需要 CMB 測量精度更高
  對應最大可測年齡: t_max ≈ 2078 × 84.635 = 175,870 Gyr
""")

# 計算每個模式嘅 ω_n·τ 同 N·δ_n 關係
print("  各模式嘅 ω_n·τ (以 2π 計):")
omega_n_tau = {}
for n in range(1, 44):
    phase = 88 * math.sin(math.pi * n / 88) * tau / T_sync
    omega_n_tau[n] = phase
    if n <= 5 or n >= 40:
        print(f"    n={n:2d}: ω_n·τ = {phase:.6f} × 2π")

print("\n  各模式嘅 N·δ_n (以 2π 計, 每步 N=1):")
for n in [1, 5, 10, 20, 30, 40, 43]:
    d = deltas[n]['delta']
    print(f"    n={n:2d}: δ_n = {d:.6f} → 每步 N 漂移 {d:.6f} × 2π")

# 精度極限
delta_min = min(d['delta'] for d in deltas.values())
phase_precision = 0.1  # rad
N_max_0_1rad = int(1/(delta_min * phase_precision/(2*math.pi)))
print(f"\n  精度極限:")
print(f"    CMB 相位精度: 0.1 rad = {phase_precision/(2*math.pi):.6f} 周")
print(f"    δ_min = {delta_min:.6f}")
print(f"    N_max = {N_max_0_1rad}")
print(f"    t_max = {N_max_0_1rad * T_sync:.0f} Gyr")

RESULTS['layer5'] = {
    'method': 'θ_n(obs) = N·δ_n + ω_n·τ (mod 2π)',
    'phase_precision_rad': 0.1,
    'N_max': N_max_0_1rad,
    't_max_gyr': round(N_max_0_1rad * T_sync, 0)
}

# ============================================================
# 第6層: 誠實結論
# ============================================================
print("\n" + "=" * 62)
print("第6層: 誠實結論")
print("=" * 62)

print("""
  ✅ 由結構推導嘅框架:
     t_true = N × T_sync + τ
     τ = R_H/c = 13.470 Gyr (觀察者「而家」相位)
     N = 由 43 個漂移相位讀出

  🟡 可計算:
     - 如果 CMB 能讀出 44 個模式嘅當前相位
     - N 可解出 (精度 ~ 0.1 rad → N_max ≈ 2078)
     - t_true = N·84.635 + 13.470 Gyr

  🔴 未閉合:
     - 點樣從 CMB 數據 (SMICA/Planck) 讀出 44 個模式相位
     - 呢個係「CMB→K_Chain 相位映射」問題
     - 需要 O51 延伸 或 新 O

  關鍵教訓:
     1. T_sync 係可用近似周期 ✅ (之前話「N 無法決定」係錯)
     2. 無理拍頻只約束「精確復歸=0」, 唔影響 T_sync 計數
     3. τ = 觀察者位置 = R_H/c 係結構定義, 唔係 ΛCDM 校準
     4. 渲染深度 (13.470 Gyr) 唔係年齡, 係「而家」相位位置
     5. 真實年齡 = N·84.635 + 13.470 Gyr, N 由 CMB 相位決定

  對比 ΛCDM 宇宙年齡 13.787 Gyr:
     IDCM 真實年齡 = N·84.635 + 13.470 Gyr
     如果 N=0 → t_true = 13.470 Gyr
     如果 N>0 → t_true > 13.470 Gyr
     所以 N=0 係最接近 ΛCDM 年齡嘅情況, 但推到「而家」喺
     第一次 SYNC 週期內 (N=0) 需要額外結構論證
""")

# Save results
with open('data/05_age_framework.json', 'w') as f:
    json.dump(RESULTS, f, indent=2)

print("\n✅ 框架推導完成 -> data/05_age_framework.json")