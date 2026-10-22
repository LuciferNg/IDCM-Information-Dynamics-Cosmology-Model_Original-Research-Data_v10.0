#!/usr/bin/env python3
"""
P14 新方向推進 — 同步擾動傳播速度 (2026-10-21)
==================================================
P3 推進: 自發同步係「譜擴散」 — 但擴散幾快? 有冇訊號速度上限?

方法: 全域同步態 (θ=0) + 節點 0 加相位擾動 δθ₀
  → 量度波前到達每個節點嘅時間 (相位偏離 > 閾值)
  → 前緣速度 v_front (site/時間單位)
  → 同「擴散常數 D = κ」理論比對 (離散熱方程)

理論: Kuramoto 線性化 = 離散熱方程
  dθ_i/dt = κ(θ_{i+1} − 2θ_i + θ_{i−1})   →  D = κ = 1/16
  連續化: ∂θ/∂t = D ∂²θ/∂x², 訊號前緣 ~ 2√(Dt)
  特徵速度 v ~ √(2D/t)? 前緣: x_front ~ 2√(D·t)
"""
import numpy as np

N = 88
K = 1/16.0
dt = 0.002

def deriv_full(theta, K):
    """無阻挫 ring, 全 sin (非線性)"""
    d = np.zeros(N)
    for i in range(N):
        jr = (i+1) % N
        jl = (i-1) % N
        d[i] = K*np.sin(theta[jr]-theta[i]) + K*np.sin(theta[jl]-theta[i])
    return d

# 初始: 全域同步 θ=0, 節點 0 加擾動 δ
delta = 0.5   # rad (唔好太大, 保持近線性; 0.5 中等)
theta = np.zeros(N)
theta[0] = delta

threshold = delta/2   # 波前定義: |θ_i| 首次過 delta/2

# 追蹤每節點首次到達時間
arrival = np.full(N, np.nan)
arrival[0] = 0.0
t = 0.0
max_t = 50000
found = 0
for s in range(max_t):
    theta = theta + dt*deriv_full(theta, K)
    t += dt
    # 檢查新到達
    for i in range(N):
        if np.isnan(arrival[i]) and abs(theta[i]) > threshold:
            arrival[i] = t
            found += 1
    if found >= N-1:
        break

print("=" * 70)
print("  同步擾動傳播 — 波前速度量度 (K=κ=1/16, δ=0.5)")
print("=" * 70)
print(f"  完成: {found+1}/{N} 節點受擾, 時間 {t:.1f} 單位")

# 速度: 節點 i 到達時間 vs 距離 site
valid = ~np.isnan(arrival)
dist = np.arange(N)
# 分隔左右兩方向
v_left = []
v_right = []
for i in range(1, N//2):
    if not np.isnan(arrival[i]):
        v_right.append((i, arrival[i]))
for i in range(N//2, N):
    if not np.isnan(arrival[i]):
        v_left.append(((N-i), arrival[i]))

# 用到達時間 vs 距離做線性擬合 (前緣, 取最近 20 site)
print("\n  近場 (site 1-10, 右向):")
for i in range(1, 21):
    if not np.isnan(arrival[i]):
        print(f"    site {i:2d}: t={arrival[i]:8.1f}  v={i/arrival[i]:.4f} site/單位")

# 線性擬合 site = v·t
from numpy.polynomial import polynomial as P
idx = np.arange(1, 41)
tmsk = ~np.isnan(arrival[idx])
x = arrival[idx][tmsk]
y = idx[tmsk]
if len(x) > 10:
    coefs = np.polyfit(x, y, 1)
    v_fit = coefs[0]
    print(f"\n  線性擬合 (site 1-40): v_front = {v_fit:.5f} site/時間單位")
    print(f"  理論擴散: x ≈ 2√(Dt) → v(t) = √(D/t) 會隨時間減慢; 離散鏈應有有限最大速度")
    # 對比: 最近鄰速度下界 — 單步耦合傳播需時?
    # 線性化矩陣 L: dθ = κ·L·θ, 訊號最大群速度 = κ·2 (band edge)
    print(f"  理論 band-edge 群速度 v_g,max = 2κ·cos(π/88) ≈ 2κ = {2*K:.4f} site/單位?")
    print(f"  (離散熱方程 v_max = 2κ·|cos(ka/2)| 頻散廣義)")
    if v_fit <= 2*K/16:  # 遠慢過相鄰耦合
        print(f"  ⚡ v_front ({v_fit:.5f}) << 相鄰耦合率 (2κ={2*K:.4f}) → 前緣係擴散主導")
    else:
        print(f"  v_front ({v_fit:.5f}) ≈ 相鄰耦合率量級 → 前緣機制要再細分")

# 對稱檢查: 另一方向
print(f"\n  右向 site 20 t={arrival[20] if not np.isnan(arrival[20]) else -1:.1f}, "
      f"左向 site 68(=20) t={arrival[68] if not np.isnan(arrival[68]) else -1:.1f}")

# 長距離: 對面 (44 sites) 到達時間
t_opp = arrival[44] if not np.isnan(arrival[44]) else np.nan
print(f"\n  ★ 對面 (site 44, 44 hops): t = {t_opp:.1f} 時間單位")
print(f"    平均速度 = {44/t_opp:.4f} site/單位 (直接前緣)")

# 定標討論: 物理單位
print("""
  定標 (docs/34 P3 開放項):
    IDCM: 1 site = 1 hop = 6.70 Mpc; 1 hop 光傳播 = 21.85 Myr
    光跨越 44 hops = 21.85×44 = 961.4 Myr
    同步擴散跨越 44 sites = t_opp (單位)
  → 若時間單位 = T_site (IDCM site 週期), 比較 v_sync vs c 需要 T_site/t_hop 比值
  → 待 docs/35 定標
""")