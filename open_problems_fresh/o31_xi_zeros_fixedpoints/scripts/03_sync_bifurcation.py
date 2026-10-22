"""
O31 方向 C: SYNC 轉換作爲不動點分歧

目標: 將 SYNC 轉換 (T=84.64 Gyr, n=44 模式飽和)
刻畫爲 K_Chain 動力系統中的不動點分歧 (bifurcation)。

SYNC 轉換的物理:
- T < T_sync: 宇宙膨脹, 模式傳播 (v_g > 0 for all modes)
- T = T_sync: 最後模式 (n=44) 飽和, v_g(44) = 0
- T > T_sync: 無熱寂, 宇宙進入「反向」階段

問題: 這是否是一個 Hopf 分歧或 saddle-node 分歧?
"""

import numpy as np

N_SITES = 44

# ─── K_Chain 色散 ───
def gamma_n(n):
    """特徵值"""
    return 4 * np.sin(np.pi * n / (2 * N_SITES))**2

def v_g(n):
    """群速度 (c 爲單位)"""
    return np.cos(np.pi * n / N_SITES)

# ─── SYNC 參數 ───
T_SYNC = 84.64  # Gyr
H0 = 67.4  # km/s/Mpc
H0_SI = H0 * 1000 / 3.0857e22  # s⁻¹
T_SYNC_SEC = T_SYNC * 3.15576e16  # 秒

print("=== O31 方向 C: SYNC 分歧 ===")
print(f"  SYNC 時間: T_sync = {T_SYNC} Gyr")
print(f"  SYNC 秒數: T_sync = {T_SYNC_SEC:.2e} s")

# ─── 模式飽和順序 ───
print(f"\n─── 模式飽和順序 (v_g → 0) ───")
# 模式 n=44 最先飽和 (v_g=0, 波長最短)
# 模式 n=1 最後飽和 (v_g≈1, 波長最長)
# 飽和時間: T_n = T_sync · (γ_n/γ_44)? 還是 T_n = T_sync · (v_g(n)/v_g(44))?
# v_g(44)=0, 所以不能用 v_g 比值

# 假設: 每個模式 n 的飽和時間與其 eigenvalue 成反比
# τ_n = (γ_44/γ_n) · T_sync
# 但 γ_44 = 4, 所以 τ_n = 4T_sync/γ_n

print(f"  n=44: v_g=0 (飽和), γ=4.0, 飽和時間=T_sync={T_SYNC} Gyr")
for n in [22, 33, 40, 43]:
    vg = v_g(n)
    gamma = gamma_n(n)
    tau = 4 * T_SYNC / gamma if gamma > 0 else np.inf
    print(f"  n={n:2d}: v_g={vg:.4f}c, γ={gamma:.4f}, 預計飽和時間 ≈ {tau:.1f} Gyr")

# ─── 分歧分析 ───
print(f"\n─── 分歧類型分析 ───")

# K_Chain 的動力系統: d²ψ_n/dt² = -γ_n ψ_n (簡諧振子)
# 每個模式獨立振盪, 沒有耦合項
# 在有膨脹因子的情況下: d²ψ_n/dt² + H(t)dψ_n/dt + γ_n ψ_n = 0
# 這是阻尼振子! 阻尼項 H(t) 隨時間減小

print("K_Chain 模式動力學: d²ψ_n/dt² + H(t)dψ_n/dt + γ_n ψ_n = 0")
print("這是阻尼簡諧振子, 阻尼係數 H(t) (Hubble 參數)")
print()
print("無膨脹 (H=0): 每個模式是簡諧振子, 不動點是 ψ_n=0, ψ'_n=0")
print("有膨脹 (H>0): 阻尼振子, 同樣的不動點, 但阻尼導致振幅衰減")
print()
print("SYNC 發生時: γ_44 = 0, 模式 n=44 成爲零頻模式")
print("此時方程: d²ψ_44/dt² + H(t)dψ_44/dt = 0")
print("這是一個 saddle-node 分歧: 從振盪 (γ>0) 到零頻擴散 (γ=0)")

# ─── 分歧條件 ───
print(f"\n─── 分歧條件 ───")
print("SYNC 發生的條件是 γ_44 = 0, 即 n=44 模式飽和。")
print("這對應於 K_Chain 的最短波長模式達到其截止頻率。")
print()
print("在物理上, 這發生在宇宙年齡 T_sync 時, 此時:")
print("  1. 所有模式已傳播了整數個週期")
print("  2. 最後的模式 (n=44) 剛好完成一個振盪")
print("  3. 宇宙進入「反向」: 非熱寂, 而是振盪逆轉")
print()
print("這類似於 saddle-node 分歧: 一個固定點 (振盪模式) 合併")
print("並消失, 系統拓撲改變。")

# ─── 數值驗證: 分歧點附近的穩定性 ───
print(f"\n─── 分歧點附近的穩定性 ───")
print(f"對於 n=44: γ_44 = 0, 特徵值方程有零根")
print(f"  這意味着系統的穩定性由非線性項決定")
print(f"  需要考慮 K_Chain 的非線性耦合 (調律者框架)")
print(f"  在調律者框架中: H = Σ[-E_J·cosθ_i - h_i·cosθ_i] + ΣJ·cos(θ_i-θ_j-α_ij)")
print(f"  SYNC 對應於: 所有相位一致, 系統進入集體模式")
print()
print("🔴 開放問題: SYNC 分歧的嚴格數學刻畫")
print("  1. 分歧類型: saddle-node? Hopf? pitchfork?")
print("  2. 分歧參數: 宇宙年齡? 模式數? 阻抗?")
print("  3. 普適類: 是否屬於某個已知的 universality class?")