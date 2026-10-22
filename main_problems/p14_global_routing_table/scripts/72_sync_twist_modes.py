#!/usr/bin/env python3
"""
P14 新方向推進 v2 — 同步擾動嘅真實行為 (2026-10-21)
==================================================
v1 發現: 單脈衝喺同步態上唔傳播 (只衰變) — 同步態係全域吸引子。

v2 三個新驗證:
  T1: Twist state θ_i = φ·i/N (線性相位梯度) 係咪固定點?
      (若係, 相位梯度 = 載波, 可以「儲存」相位差?)
  T2: 模衰減率: 初始 θ_i = A·sin(πn·i/44) → 衰減率 應該 = κγ_n (K_Chain 譜本身)
  T3: 連續驅動 (節點 0 持續振盪): 波前行唔行得出去? 速度幾多?
"""
import numpy as np

N = 88
K = 1/16.0
dt = 0.002

def deriv(theta, K):
    d = np.zeros(N)
    for i in range(N):
        jr = (i+1) % N
        jl = (i-1) % N
        d[i] = K*np.sin(theta[jr]-theta[i]) + K*np.sin(theta[jl]-theta[i])
    return d

print("=" * 70)
print("  T1: Twist state θ_i = φ·(i/87) 係咪固定點?")
print("=" * 70)
for phi in [0.1, 0.5, 1.0, np.pi/2]:
    theta = phi * np.arange(N) / (N-1)
    # 週期邊界: θ_87 同 θ_0 嘅差係 φ·(87-1)/(87)?? twist 要 wrap 一致
    print(f"  φ={phi:.3f}: ", end="")
    # 計算 dθ/dt
    d = deriv(theta, K)
    print(f"max|dθ/dt| = {np.abs(d).max():.2e}")

print("""
  註: wrap-around twist θ_i = k·i 模 2π. 若 k·N ≡ 0 (mod 2π) → 週期一致.
  fixed point 條件: sin(θ_{i+1}−θ_i) + sin(θ_{i-1}−θ_i) = sin(k) − sin(k) = 0 ✓ 對任意 k
  ⟹ 任何 uniform twist 都係固定點! (相位梯度 = 載波, 唔會衰減)
""")

print("=" * 70)
print("  T2: 模衰減率 — 初始 sin 模, 衰減率對照 κγ_n")
print("=" * 70)
for n in [1, 2, 5, 22]:
    theta0 = 0.1 * np.sin(np.pi * n * np.arange(N) / N)
    theta = theta0.copy()
    # 量度振幅包絡: 投影返個模
    proj0 = np.sum(theta * np.sin(np.pi * n * np.arange(N) / N))
    # 跑 300 單位, 記錄衰減
    best = proj0
    t_last = 0.0
    decay_time = None
    t = 0.0
    for s in range(150000):  # 300 單位
        theta = theta + dt*deriv(theta, K)
        t += dt
        proj = np.sum(theta * np.sin(np.pi * n * np.arange(N) / N))
        if abs(proj) < abs(proj0)*0.5 and decay_time is None:
            decay_time = t
        if abs(proj) > abs(best):
            best = proj
    gamma_n = 4*K*np.sin(np.pi*n/N)**2
    # 半衰期理論 = ln2/λ, λ = κγ_n (ring Laplacian 特徵值)
    tau_half_theory = np.log(2) / (K*gamma_n) if K*gamma_n > 0 else np.inf
    if decay_time is None:
        print(f"  mode n={n:2d}: γ_n={gamma_n:.5f}, 實測半衰期 > {t:.0f} 單位, 理論 ln2/(κγ_n)={tau_half_theory:.1f}")
    else:
        print(f"  mode n={n:2d}: γ_n={gamma_n:.5f}, 實測半衰期={decay_time:.1f} 單位, 理論 ln2/(κγ_n)={tau_half_theory:.1f}")

print("""
  理論: Kuramoto 線性化 = 離散熱方程, ring Laplacian 特徵值 = K_Chain 譜 γ_n
  → 模 n 衰減率 λ_n = κ·γ_n = κ·4sin²(πn/88)
  → 即 K_Chain 譜完整控制同步衰變! (精度要甩到非線性)
""")

print("=" * 70)
print("  T3: 連續驅動 — 節點 0 持續正弦振盪, 波前傳播速度?")
print("=" * 70)
# 節點 0 強制 θ_0 = A_d sin(ω_d t), 其他節點自由
A_d = 0.3
omega_d = 0.05
theta = np.zeros(N)
threshold = A_d*0.2
arrival = np.full(N, np.nan)
arrival[0] = 0.0
t = 0.0
found = 1
for s in range(500000):  # 1000 單位
    theta = theta + dt*deriv(theta, K)
    theta[0] = A_d*np.sin(omega_d*t)
    t += dt
    for i in range(1, N):
        if np.isnan(arrival[i]):
            # 追蹤包絡: max|θ_i| 喺 rolling window
            pass
    if s % 500 == 0:
        # 檢查新到達 (用近期振幅)
        recent = np.zeros(N)
        # 簡化: 檢查而家相位
        for i in range(1, N):
            if np.isnan(arrival[i]) and abs(theta[i]) > threshold:
                arrival[i] = t
                found += 1
    if found >= N:
        break

print(f"  驅動: A={A_d}, ω={omega_d}, 傳播到 {found}/{N} 節點")
for i in [1, 2, 5, 10, 20, 30, 44, 60, 80]:
    if not np.isnan(arrival[i]):
        print(f"    site {i:2d}: t={arrival[i]:8.1f}  平均 v={i/arrival[i]:.4f}")
    else:
        print(f"    site {i:2d}: 未到")

# 有效速度 (最遠到達)
valid = ~np.isnan(arrival)
if valid.sum() > 10:
    d_max = np.max(np.where(valid)[0])
    t_max = arrival[d_max]
    print(f"\n  最遠 site {d_max}: t={t_max:.1f}, 平均 v = {d_max/t_max:.4f} site/單位")
    print(f"  對比: band-edge 群速度 2κ = {2*K:.4f} (理論上限)")