#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
46_rge_calibration.py — Gemini RGE 尺度流公式校準
===================================================
Gemini 主張: θ₂₃ 殘差 −0.1222° = 176→44 尺度收縮嘅拓撲流 ∫β d ln N。
校準:
1. θ₂₃(N) = atan(sin(7π/N)/sin(6π/N)) 喺 N = 176/88/44/33
2. 自然積分 θ(44)−θ(176) vs 宣稱 −0.1222°
3. Gemini β 公式 (1/2π 因子) 內部一致性
4. 需要邊個 N 先到 49.198°
5. 殘差候選 (1/462, (γ₇−γ₆)/30, 1/469)
6. 三角度殘差總和 ≈ 1/352?
"""
import math
DEG = 180.0/math.pi

def th23(N):
    """θ₂₃(N) = atan(sin(7π/N)/sin(6π/N)) — 176 慣例 (Gemini 嘅 GUT 尺度)"""
    return math.degrees(math.atan(math.sin(7*math.pi/N)/math.sin(6*math.pi/N)))

print("1) θ₂₃(N) 尺度流 (176 慣例)")
for N in (176, 88, 44, 33, 41, 42):
    print(f"   N={N:4d}: θ₂₃ = {th23(N):.6f}°")

print("\n2) 自然積分 (端點差) vs Gemini 宣稱 −0.1222°")
d = th23(44) - th23(176)
print(f"   θ(44)−θ(176) = {d:+.4f}°  (Gemini 宣稱 −0.1222° — 差 {abs(d-(-0.1222)):.4f}°)")
d88 = th23(44) - th23(88)
print(f"   θ(44)−θ(88)  = {d88:+.4f}°  (框架 θ₂₃ 定義喺 N=88)")

print("\n3) Gemini β 公式內部一致性")
# dθ/dlnN 精確微分: u = √(γ₇/γ₆) = sin(7π/N)/sin(6π/N)
# dθ/dlnN = u/(2(1+u²))·(∂lnγ₇/∂lnN − ∂lnγ₆/∂lnN)  ← 冇 1/2π
# Gemini: (1/2π)·√(γ₇γ₆)/(γ₇+γ₆)·(∂lnγ₇/∂N − ∂lnγ₆/∂N)  ← ∂N 唔係 ∂lnN, 加 1/2π
# 若 β = dθ/dlnN 精確, ∫β dlnN = θ(N₁)−θ(N₀) 必等 (端點定理); 1/2π 因子必然破壞呢個性質
print("   若 β_top = dθ/dlnN, ∫β dlnN = 端點差 (微積分基本定理)")
print("   加 1/2π 因子 ⇒ ∫β dlnN ≠ 端點差 ⇒ 公式內部矛盾 ✗")
print("   ∂lnγ/∂N vs ∂lnγ/∂lnN 混用 — 維度不一致 ✗")

print("\n4) 要達到 49.1980° 需要嘅 N")
lo, hi = 30, 60
for N in range(lo, hi+1):
    if abs(th23(N)-49.1980) < 0.05:
        print(f"   N={N}: θ₂₃ = {th23(N):.4f}°")
print(f"   (框架尺度: 88/176/44/33/42 — 41.5 唔係框架尺度)")

print("\n5) 殘差候選 (框架常數)")
res = 49.3202 - 49.1980   # 框架值 − NuFIT
res_rad = res*math.pi/180
print(f"   殘差 = {res:.4f}° = {res_rad:.8f} rad")
for name, n in [("2N_gen·L₄·L₅", 6*7*11), ("(γ₇−γ₆)/30", None)]:
    if n:
        v = 1/n*DEG
        print(f"   1/{name} = 1/{n} = {v:.4f}° (Δ {abs(v-res):.4f}° = {abs(v-res)/res*100:.1f}%)")
g6 = 4*math.sin(6*math.pi/88)**2
g7 = 4*math.sin(7*math.pi/88)**2
v = (g7-g6)/30*DEG
print(f"   (γ₇−γ₆)/30 = {v:.4f}° (Δ {abs(v-res):.4f}° = {abs(v-res)/res*100:.1f}%)")
print(f"   1/469 = {1/469*DEG:.4f}° (Δ {abs(1/469*DEG-res):.4f}° — 469 冇結構)")

print("\n6) 三角度殘差總和 vs 1/352")
sumres = (33.4532-33.4602) + res + (8.6169-8.5690)
print(f"   總和 = {sumres:+.4f}° = {sumres*math.pi/180:.6f} rad; 1/352 rad = {1/352*DEG:.4f}° (Δ {abs(abs(sumres)-1/352*DEG):.4f}° = {abs(abs(sumres)-1/352*DEG)/(1/352*DEG)*100:.1f}%)")
