#!/usr/bin/env python3
"""
P6 工具 #1: hop 層 bound-state 定位器 (Green 函數極點法) v2
========================================================
問題(#1): 束縛態 γ₁=γ₄+Δcos(2π/8), γ₂=γ₄+Δcos(2π/10) 嘅 hop 強度係咪
         唯一 t = Δ/2? 定係有其他 t 都得?

正確模型 — Feshbach 缺陷極點:
  chain {γ_n}, 缺陷喺位置 x₀ (hop 干涉核權重 ψ_n(x₀)²)
  bound state E* 滿足 det[1 − t·Σ_n ψ_n(x₀)²/(E*−γ_n)] = 0
  → 對 target γ*: t(x₀, γ*) = 1/G₀(x₀, γ*)

關鍵測試:
  1. 掃 x₀ ∈ [1,88] (缺陷位置)
  2. 對 γ₁, γ₂ 分別計 t₁(x₀), t₂(x₀)
  3. 有冇 x₀ 令 t₁(x₀) = t₂(x₀) = Δ/2 ?!
     — 有 → O179 hop 缺陷自洽產生兩個 bound state, hop 強度自動 = Δ/2
     — 冇 → t=Δ/2 係外在設定, 機制唔閉 (仍需 hop 層 der)

用法: python3 scripts/06_hop_bound_state_locator.py
"""
import math

def gamma(n, N=88):
    return 4 * math.sin(n * math.pi / N) ** 2

g4, g5, g6 = gamma(4), gamma(5), gamma(6)
DELTA = g5 - g4
T0 = DELTA / 2

GAM1 = g4 + DELTA*math.cos(2*math.pi/8)   # N=8 bound state
GAM2 = g4 + DELTA*math.cos(2*math.pi/10)  # N=10 bound state

def G0(x0, E, N=88):
    """Green 函數缺陷位置: Σ sin²(nπx₀/88) / (E−γₙ), 用單側 n=1..44"""
    s = 0.0
    for n in range(1, 45):
        s += math.sin(n*math.pi*x0/88)**2 / (E - gamma(n))
    return s

print("="*78)
print("【1】掃描缺陷位置 x₀: t₁(x₀), t₂(x₀)")
print("="*78)
print(f"target γ₁ = {GAM1:.8f}  γ₂ = {GAM2:.8f}  T0 = Δ/2 = {T0:.8f}\n")

best = []
for x0f in range(1, 89):
    x0 = float(x0f)
    g1, g2 = G0(x0, GAM1), G0(x0, GAM2)
    if g1 == 0 or g2 == 0:
        continue
    t1, t2 = 1.0/g1, 1.0/g2
    # 同時接近 Δ/2?
    d1 = abs(t1-T0)/T0
    d2 = abs(t2-T0)/T0
    if d1 < 0.05 and d2 < 0.05:
        best.append((x0, t1, t2, d1, d2))

print(f"同時命中 Δ/2 (±5%): {len(best)} 個位置")
for x0, t1, t2, d1, d2 in best[:20]:
    print(f"  x₀={x0:3.0f}: t₁={t1:.8f} (dev {d1*100:.3f}%)  t₂={t2:.8f} (dev {d2*100:.3f}%)")

# 各 N 單獨最接近
for label, tg in [("γ₁(N=8)", GAM1), ("γ₂(N=10)", GAM2)]:
    vals = []
    for x0f in range(1, 89):
        x0 = float(x0f)
        g = G0(x0, tg)
        if g == 0: continue
        t = 1.0/g
        vals.append((abs(t-T0)/T0, x0, t))
    vals.sort()
    print(f"\n{label}: 最接近 Δ/2 嘅 x₀:")
    for d, x0, t in vals[:5]:
        print(f"    x₀={x0:3.0f}: t={t:.8f} dev {d*100:.4f}%")

print()
print("="*78)
print("【2】x₀ 連續掃描 + t₁=t₂ 條件")
print("="*78)
# 真正測試: t₁(x₀) = t₂(x₀) 即 G₀(x₀,γ₁) = G₀(x₀,γ₂)
# 同埋該共同值係咪 = Δ/2?
crossings = []
prev = None
N_p = 400
for i in range(N_p+1):
    x0 = 1.0 + 87.0*i/N_p
    D = G0(x0, GAM1) - G0(x0, GAM2)
    if prev is not None and prev*D < 0:
        crossings.append(x0)
    prev = D

print(f"G₀(x₀,γ₁)=G₀(x₀,γ₂) 交叉點: {len(crossings)}")
for x0 in crossings[:10]:
    t12 = 1.0/G0(x0, GAM1)
    print(f"  x₀={x0:.2f}: t₁=t₂={t12:.8f}  dev vs Δ/2 = {abs(t12-T0)/T0*100:.4f}%")

print()
print("="*78)
print("【3】結論")
print("="*78)
print("""
  判準:
  - 存在 x₀ 令 t₁≈t₂≈Δ/2 (dev<1%) → Green 極點自然產出 hop 強度 → 🟢 機制閉合
  - 冇 x₀ 令共同 t ≈ Δ/2 → t=Δ/2 唔係缺陷幾何嘅自然產物 → 🟡 仍需 hop der
  - 留意: 用 sin² 權重係「對偶鏈 (dual chain)」嘅自然投影 (modal 權重)
""")