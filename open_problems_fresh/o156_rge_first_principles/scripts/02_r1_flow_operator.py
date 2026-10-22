#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
02_r1_flow_operator.py — R1: 尺度流算子 R_top(μ) 正確定義 (O156)
=============================================================
問題: θ₂₃ 殘差 −0.1222° 係咪「尺度流」? 自然尺度之間嘅流唔等於殘差 (已證)。
本腳本:
1. 正式定義流算子: θ(N) = atan(sin(7π/N)/sin(6π/N)), 流向量場 dθ/dlnN
2. 精確導數公式 + 數值驗證 (微分同胚性: 單調性, 平滑性, 零點)
3. 自然端點 null 表: 所有自然尺度對 (N₁,N₂) 嘅流積分 vs 殘差
4. 最近對分析 + 結論
5. Gemini β_top 公式 vs 精確 dθ/dlnN (記錄)
"""
import math
DEG = 180.0/math.pi
RAD = math.pi/180.0

RESID = 49.320228 - 49.1980          # 框架 θ₂₃(88) − NuFIT 5.2 = +0.1222°
RESID_RAD = RESID*RAD
print(f"殘差 r = {RESID:.4f}° = {RESID_RAD:.8f} rad\n")

def th(N, k1=7, k2=6):
    """θ(N) = atan(sin(k1π/N)/sin(k2π/N)) — 176 慣例 (ω_n = 2sin(nπ/N))"""
    return math.degrees(math.atan(math.sin(k1*math.pi/N)/math.sin(k2*math.pi/N)))

def dtheta_dlnN(N):
    """精確: dθ/dlnN = N·u'/(1+u²), u = sin(7π/N)/sin(6π/N)
    u' = [−7π cos(7π/N) sin(6π/N) + 6π sin(7π/N) cos(6π/N)] / (N² sin²(6π/N))"""
    a, b = 7*math.pi/N, 6*math.pi/N
    u = math.sin(a)/math.sin(b)
    up = (-7*math.pi*math.cos(a)*math.sin(b) + 6*math.pi*math.sin(a)*math.cos(b)) / (N*N*math.sin(b)**2)
    return N*up/(1+u*u)*DEG   # °/unit lnN

print("1) 流向量場 dθ/dlnN (精確) 喺自然尺度")
for N in (176, 88, 55, 44, 42, 46, 33):
    print(f"   N={N:4d}: θ={th(N):.6f}°  dθ/dlnN={dtheta_dlnN(N):+.4f} °/ln-unit")

print("\n2) 微分同胚性: 單調性 + 平滑性 + 零點掃描")
vals = [th(N) for N in range(33, 200)]
mono_inc = all(vals[i] < vals[i+1] for i in range(len(vals)-1))
print(f"   θ(N) 喺 [33,200] 嚴格單調遞增: {mono_inc}  (θ(176)=49.379 > θ(88)=49.320 > θ(55)=49.197 > θ(33)=48.827)")
# 零點 / 固定點: dθ/dlnN = 0?
zeros = [N for N in range(33, 500) if abs(dtheta_dlnN(N)) < 1e-6]
print(f"   dθ/dlnN 零點喺 [33,500]: {zeros if zeros else '無 (流無固定點)'}")
curv = (dtheta_dlnN(89) - dtheta_dlnN(87))/2
print(f"   曲率 d²θ/dlnN²|₈₈ ≈ {curv:+.4f} °/ln² — {'平滑' if abs(curv) < 1 else '異常'}")

print("\n3) 自然端點 null 表 — 流積分 θ(N₁)−θ(N₂) vs 殘差 −0.1222°")
NAT = [176, 88, 55, 46, 44, 42, 33]
print(f"   {'N₁':>4} {'N₂':>4} {'θ(N₁)−θ(N₂)':>14} {'Δ vs r':>12} {'|Δ|/r':>8}")
best = None
for N1 in NAT:
    for N2 in NAT:
        if N1 == N2: continue
        d = th(N1) - th(N2)
        dd = abs(d - (-RESID))
        if best is None or dd < best[0]: best = (dd, N1, N2, d)
        print(f"   {N1:>4} {N2:>4} {d:+14.6f}° {dd:+12.6f}° {dd/RESID:7.1%}")

print(f"\n   最近對: θ({best[1]})−θ({best[2]}) = {best[3]:+.6f}° (Δ {best[0]:.6f}° = {best[0]/RESID:.1%} 殘差)")
print(f"   ⇒ 流解釋喺自然尺度: 全部 fail (最近 1.1% off = form-precision 級, 唔係流)")

print("\n4) 連續解: 邊個 N* 令 θ(N*) = NuFIT 49.1980°?")
# θ(N) 遞增: θ(33)=48.827 < 49.198 < θ(55)=49.197 < θ(56)=49.204 — 根喺 (55,56)
lo, hi = 33.0, 200.0
f = lambda N: th(N) - 49.1980
for _ in range(100):
    mid = (lo+hi)/2
    if f(mid) > 0: hi = mid   # f 遞增
    else: lo = mid
Nstar = (lo+hi)/2
print(f"   N* = {Nstar:.6f}  (θ(N*) = {th(Nstar):.6f}°)")
print(f"   框架尺度最近: 55 = F₁₀ (θ(55) = {th(55):.6f}°, Δ {th(55)-49.1980:+.4f}°)")
print(f"                56 (θ(56) = {th(56):.6f}°, Δ {th(56)-49.1980:+.4f}°)")
print(f"   ⇒ 連續 N* = {Nstar:.2f} 冇結構; 最近框架尺度 55 = F₁₀ 命中 0.003%")

print("\n5) Gemini β_top vs 精確 dθ/dlnN (記錄)")
g6 = 4*math.sin(6*math.pi/88)**2
g7 = 4*math.sin(7*math.pi/88)**2
# Gemini: β = (1/2π)·√(γ₇γ₆)/(γ₇+γ₆)·(∂lnγ₇/∂N − ∂lnγ₆/∂N)  ← ∂N 版本
dln_g7_dN = (2*math.pi/88)*math.cos(7*math.pi/88)/math.sin(7*math.pi/88)  # d ln γ/dN = 2π cos/N sin ... 唔啱
# 正確: γ = 4sin²(nπ/N); d lnγ/dN = 2·(cos(nπ/N))·(−nπ/N²)/sin(nπ/N)
dln_g7_dN = -2*(7*math.pi/88**2)*math.cos(7*math.pi/88)/math.sin(7*math.pi/88)
dln_g6_dN = -2*(6*math.pi/88**2)*math.cos(6*math.pi/88)/math.sin(6*math.pi/88)
beta_gem = (1/(2*math.pi))*math.sqrt(g7*g6)/(g7+g6)*(dln_g7_dN - dln_g6_dN)*DEG
print(f"   Gemini β_top(88) = {beta_gem:+.6f} °/N-unit (∂N 混用版)")
print(f"   精確 dθ/dlnN(88)  = {dtheta_dlnN(88):+.6f} °/ln-unit")
print(f"   Gemini ∫β dN ≈ β·ΔN 亦唔等於 θ 差 (微積分基本定理破壞) — 公式已死, 只記錄")
