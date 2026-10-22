#!/usr/bin/env python3
"""
P14 推進 — #1 twist 能量橋 + #2 k_c 數列檢驗 (2026-10-21)
===========================================================
docs/37 開放項 #1: C(m) ↔ O41 ΔE_write 橋
  ⚠️ 修正: O41 嘅 γ=192 係 μK↔IDCM 換算 (4N_d+B²), 唔係 K_Chain 譜 γ_n

真正 twist 能量 = Kuramoto 勢能差:
  V = −K Σ cos(θ_{i+1}−θ_i)   (ring, twist m → 每邊 Δθ=2πm/88)
  ΔV(m) = 88K(1−cos(2πm/88))
  細 m: 1−cos x ≈ x²/2 → ΔV ≈ (88K/2)(2πm/88)² = (K/2)·C(m)
  檢驗: ΔV(m) = (κ/2)·C(m) 準唔準?

#2: L_min 數列 4,7,11,15,18,22,26,29,33,36
  試 L_min = round(3.65·m)?? 3.65 有咩結構?  另試 k_c=2πm/L 恆定?
  m=1..10 全表已知, 掃 m=11..16 攞多啲點
"""
import numpy as np

N = 88
K = 1/16.0
dt = 0.002
MUK = 192.0          # μK/IDCM 單位 (O41 γ = 4N_d+B²)

def C(m):
    """彈性梯度 L2: Σ(Δθ)² for full-ring twist"""
    return N * (2*np.pi*m/N)**2

print("=" * 72)
print("  QU1: ΔV_twist(m) = 88K(1−cos(2πm/88)) vs (K/2)·C(m)")
print("=" * 72)
print(f"  {'m':>3} {'ΔV(IDCM)':>10} {'C·K/2':>10} {'比率':>7} {'ΔV(μK)':>9}")
for m in [1, 2, 3, 5, 11, 15, 21]:
    dV = 88*K*(1 - np.cos(2*np.pi*m/N))
    ck2 = K/2 * C(m)
    print(f"  {m:>3} {dV:>10.6f} {ck2:>10.6f} {dV/ck2:>7.4f} {dV*MUK:>9.3f}")

print("""
  若比率≈1 → ΔV = (κ/2)·C(m) 細 m 成立 (x²/2 近似).
  C(m) 本身唔係能量! 能量係 Kuramoto 勢能 ΔV. docs/37 要補註.
""")

print("=" * 72)
print("  QU2: O41 橋 — ΔV_twist(m) vs ΔE_write = B(n)·γ·|cosθ|")
print("=" * 72)
B_n = 123/88.0
print(f"  B(n) = {B_n:.6f} IDCM = {B_n*MUK:.2f} μK (每模態預算)")
print(f"  ΔE_write(max,|cosθ|=1) = {B_n*MUK:.2f} μK")
print(f"  ΔV(μK) m=1:  {(88*K*(1-np.cos(2*np.pi*1/N)))*MUK:.3f} μK")
print(f"  ΔV(μK) m=21: {(88*K*(1-np.cos(2*np.pi*21/N)))*MUK:.3f} μK")
print(f"  ΔV(μK) m=44(=2π/2): {(88*K*(1-np.cos(2*np.pi*44/N)))*MUK:.3f} μK (=2×88K)")
print("""
  比較: 單節點翻轉 ΔE_write(max) ≈ 268 μK — twist m=21 全環 ≈ 980 μK
  → 全環 twist 能量 ≈ 3.65× 單節點最大寫入 (m=21); m=1 ≈ 1% 單節點
  語義: 一個係「局部翻轉」, 一個係「全域梯度」— 唔同操作, 唔可以直接比
""")

print("=" * 72)
print("  QU3: L_min 數列 — 掃 m=11..16 (scripts/74 未覆蓋)")
print("=" * 72)

def deriv(theta, K):
    d = np.zeros(N)
    for i in range(N):
        jr = (i+1) % N
        jl = (i-1) % N
        d[i] = K*np.sin(theta[jr]-theta[i]) + K*np.sin(theta[jl]-theta[i])
    return d

def winding(theta):
    diff = np.diff(np.concatenate([theta, theta[:1]]))
    return np.sum(np.mod(diff+np.pi, 2*np.pi) - np.pi) / (2*np.pi)

def relax(theta, steps=60000):
    for s in range(steps):
        theta = theta + dt*deriv(theta, K)
        theta = np.mod(theta, 2*np.pi)
    return theta

known = {1:4, 2:7, 3:11, 4:15, 5:18, 6:22, 7:26, 8:29, 9:33, 10:36}
print(f"  m=1..10 已知: {list(known.values())}")
for m in range(11, 17):
    found = None
    for L in range(2, 5*m+6):
        th = np.zeros(N)
        for i in range(L):
            th[i] = 2*np.pi*m*i/L
        w1 = winding(relax(th.copy()))
        if abs(w1 - m) < 0.05:
            found = L
            break
    known[m] = found
    print(f"  m={m:>2}: L_min={found}")

print()
print("  全表: ", [known[m] for m in sorted(known)])
lms = [known[m] for m in sorted(known)]
print("  差值: ", np.diff(lms))
# 3.65 檢驗
err365 = [abs(known[m] - round(3.65*m)) for m in sorted(known)]
print(f"  |L − round(3.65m)|: {err365}  max={max(err365)}")
# 線性擬合
x = np.array(sorted(known), dtype=float)
y = np.array(lms, dtype=float)
A = np.polyfit(x, y, 1)
print(f"  線性擬合: L ≈ {A[0]:.4f}·m + {A[1]:.3f}")