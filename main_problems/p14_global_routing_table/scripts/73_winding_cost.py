#!/usr/bin/env python3
"""
P14 推進 — winding 成本結構 + 最小覆蓋定律 (2026-10-21)
=========================================================
docs/36 開放項:
  #2 最小覆蓋定律: 斜坡 L 節點建立 m 嘅最小 L?
  #1 能量成本: twist 建立成本 vs γ_m (K_Chain 譜)?

猜想: 成本(每邊) ∝ (2πm/88)² ≈ γ_m (細 m) → 寫入成本 = 目標 winding 譜本徵值

W5: 掃描斜坡節點數 L 建立 m=1, 睇最小 L (鬆弛後 winding 保持?)
W6: 成本 Σ(Δθ)² 對比 γ_m for m=1..21
W7: 穩定性判據 v_g(2m) > 0 連接 (cos(2πm/88) = v_g(2m))
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

def winding(theta):
    diff = np.diff(np.concatenate([theta, theta[:1]]))
    return np.sum(np.mod(diff+np.pi, 2*np.pi) - np.pi) / (2*np.pi)

def relax(theta, steps=125000):
    for s in range(steps):
        theta = theta + dt*deriv(theta, K)
        theta = np.mod(theta, 2*np.pi)
    return theta

def ramp_write(m, L, seed=0):
    """前 L 連續節點 0→2πm 斜坡, 其餘 0"""
    theta = np.zeros(N)
    for i in range(L):
        theta[i] = 2*np.pi*m*i / L
    return theta

def elastic_cost(theta):
    """彈性成本: Σ(Δθ)² (每邊相位差平方和)"""
    diff = np.diff(np.concatenate([theta, theta[:1]]))
    diff = np.mod(diff + np.pi, 2*np.pi) - np.pi
    return np.sum(diff**2)

print("=" * 72)
print("  W5: 最小覆蓋定律 — 斜坡 L 節點建立 m=1")
print("=" * 72)
print(f"  {'L':>4} {'初始 winding':>12} {'鬆弛後':>10} {'判定':>4}")
for L in [88, 44, 30, 22, 16, 12, 8, 6, 4, 3, 2]:
    th = ramp_write(1, L)
    w0 = winding(th)
    th_r = relax(th.copy())
    w1 = winding(th_r)
    verdict = "🟢" if abs(w1-1) < 0.05 else ("🟡" if abs(w1) > 0.5 else "🔴")
    print(f"  {L:>4} {w0:>12.4f} {w1:>10.4f} {verdict:>4}")

print("""
  推測: 最小 L 要滿足局部差 δ=2π/L 唔超過駐波穩定性界?
  twist 整體 stable iff cos(2πm/88) > 0; 但局部斜坡係「陡峭」嘅版本 (L 細 = 每步差大)
""")

print("=" * 72)
print("  W6: 建立成本 Σ(Δθ)² vs γ_m (K_Chain 譜) — for m=1..21")
print("=" * 72)
print(f"  {'m':>3} {'cost Σ(Δθ)²':>12} {'γ_m':>10} {'cost/γ_m':>9}")
gammas = [4*np.sin(np.pi*n/N)**2 for n in range(1, 44)]
ratios = []
for m in range(1, 22):
    th = ramp_write(m, 88)   # 全環斜坡 = 標準 twist
    c = elastic_cost(th)
    g = 4*np.sin(np.pi*m/N)**2
    ratios.append(c/g)
    print(f"  {m:>3} {c:>12.5f} {g:>10.6f} {c/g:>9.4f}")
print(f"\n  cost/γ_m: mean={np.mean(ratios):.4f}, std={np.std(ratios):.4f}, "
      f"極端 {np.min(ratios):.3f}..{np.max(ratios):.3f}")
print(f"  若 constant → 成本 ∝ γ_m 確立 (m 細時 γ_m ≈ (2πm/88)² = 每邊成本)")

print("=" * 72)
print("  W7: 穩定性判據 = v_g(2m)?  cos(2πm/88) vs v_g(n)=cos(πn/88)")
print("=" * 72)
for m in [1, 11, 21, 22, 23]:
    ck = np.cos(2*np.pi*m/N)
    vg2m = np.cos(np.pi*2*m/N)
    print(f"  m={m:>3}: cos(2πm/88)={ck:+.6f}  v_g(2m)={vg2m:+.6f}  "
          f"相同={np.isclose(ck, vg2m)}  → 穩定 {ck > 0}")
print("\n  cos(2πm/88) = cos(π·(2m)/88) = v_g(2m) — 穩定性判據 = 偶模式群速度正!")

# 穩定 sector 計數: v_g(2m)>0 嘅 m 數
n_stable = sum(1 for m in range(0, 88) if np.cos(2*np.pi*m/N) > 0 and winding(ramp_write(m if m>0 else 1, 88))>=0)
# 直接數: cos(2πm/88)>0, m=0..43 內 (m 同 88-m 同 winding)
stable_m = [m for m in range(0, 44) if np.cos(2*np.pi*m/N) > 0]
print(f"  穩定 m ∈ {stable_m}")
print(f"  計數: {len(stable_m)} (非零 m: {len(stable_m)-1})")