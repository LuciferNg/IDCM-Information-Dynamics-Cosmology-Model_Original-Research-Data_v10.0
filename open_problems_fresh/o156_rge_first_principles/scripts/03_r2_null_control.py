#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
03_r2_null_control.py — R2: θ₂₃ 殘差候選 null-control (O156)
==========================================================
方法論 (docs/05): 隨機 target 命中率 = 結構性度量.
   1. 精度: ≤1e-8 結構 / 1e-5~1e-6 search-grade / >1e-3 form-precision
   2. 多重度: unique vs 退化
   3. null-control: 隨機 target 命中率 <5% 結構, >50% 巧合

候選:
   A. 1/462 = 1/(2N_gen·L₄·L₅)      (1.5% off)  — 1/n 家族
   B. (γ₇−γ₆)/30                     (0.1% off)  — (γ_a−γ_b)/c 家族
   C. 1/469 EXACT (0.03% off)        — 469 = 7×67 冇結構身份 → 結構判準直接殺
   D. θ(55) = 49.1966° vs NuFIT 49.198° (0.003% off) — 框架 N 家族

每個家族: 對 2000 隨機 target 做同精度 best-hit, 統計命中率.
"""
import math, random
random.seed(20260907)
DEG = 180.0/math.pi
RAD = math.pi/180.0

RESID = 49.320228 - 49.1980          # 0.1222°
TARGET_NUFIT = 49.1980

def th(N, k1=7, k2=6):
    return math.degrees(math.atan(math.sin(k1*math.pi/N)/math.sin(k2*math.pi/N)))

def gamma(n, N=88):
    return 4*math.sin(n*math.pi/N)**2

print("0) 候選精度表")
cands = [
    ("1/462 = 1/(2N_gen·L₄·L₅)", 1/462*DEG),
    ("(γ₇−γ₆)/30", (gamma(7)-gamma(6))/30*DEG),
    ("1/469 (7×67 無結構)", 1/469*DEG),
    ("θ(55) = F₁₀", th(55)),
]
for name, v in cands:
    dd = abs(v - RESID)
    print(f"   {name:28s}: {v:.4f}°  Δ={dd:.4f}° ({dd/RESID*100:.2f}%)")

print("\n1) 家族 A: 1/n, n ∈ 框架常數乘積 (≤3 因子, 300≤n≤700)")
FC = [2, 3, 4, 5, 6, 7, 8, 11, 13, 16, 21, 33, 42, 44, 46, 55, 66, 88, 176]
prod3 = set()
for a in FC:
    for b in FC:
        if a*b > 700: continue
        for c in FC:
            p = a*b*c
            if 300 <= p <= 700: prod3.add(p)
prod3 = sorted(prod3)
print(f"   框架 3-乘積喺 [300,700]: {prod3}")
print(f"   1/n 命中 0.1222° (tol 1.5%): " +
      f"{[f'1/{n}={1/n*DEG:.4f}°' for n in prod3 if abs(1/n*DEG-RESID)/RESID < 0.015]}")

print("\n2) 家族 B: (γ_a−γ_b)/c, a<b∈[1,44], c ∈ 框架常數")
Cs = [5, 6, 8, 15, 30, 33, 42, 44, 66, 88]
hitsB = []
for a in range(1, 44):
    for b in range(a+1, 45):
        for c in Cs:
            v = (gamma(b)-gamma(a))/c*DEG
            if abs(v-RESID)/RESID < 0.02:
                hitsB.append((a, b, c, v))
print(f"   tol 2% 內命中: {len(hitsB)} 個")
for h in hitsB[:12]: print(f"      (γ_{h[0]},γ_{h[1]})/{h[2]} = {h[3]:.4f}°")
print(f"   → 家族密度極高 — 單獨命中零信息量 (需要結構判準: c 身份 + 精確度)")

print("\n3) 家族 C: 1/469 結構身份檢查")
print(f"   469 = 7×67; 67 = ? 框架身份: 67 = 2K_tree+1? {'67 == 2*33+1'}")
print(f"   67 = 2·33+1 = 67 ✓ (但 '2K_tree+1' 唔係算子字典成員) → 結構判準: 拒")
print(f"   精度 0.03% 係 'EXACT' 但冇身份 ⇒ 過適示範 (SESSION_START 已記)")

print("\n4) ★ 家族 D: θ(N), N ∈ 框架尺度 — 隨機 target 命中率 (0.003% tol)")
NAT = [176, 88, 55, 46, 44, 42, 33]
angles = {N: th(N) for N in NAT}
print(f"   框架 N 角度: " + ", ".join(f"θ({N})={angles[N]:.4f}°" for N in NAT))
print(f"   目標 49.1980°: 最近 = θ(55) = {angles[55]:.4f}° (Δ {abs(angles[55]-TARGET_NUFIT):.4f}°)")
tol_deg = 0.0015   # 0.003% of 49.2°
hit = 0; NT = 2000
lo, hi = min(angles.values()), max(angles.values())
for _ in range(NT):
    t = random.uniform(lo, hi)
    if any(abs(a - t) < tol_deg for a in angles.values()):
        hit += 1
print(f"   隨機 target 命中率: {hit}/{NT} = {hit/NT*100:.1f}% (tol {tol_deg:.4f}° = 0.003%)")
print(f"   判準: <5% 結構 ⇒ {'✅ 低於 5% — N=55 命中唔係密度巧合' if hit/NT < 0.05 else '❌ 密度可解釋'}")

print("\n5) 家族 D 對比: 如果用『任何整數 N』(唔限框架)")
hit2 = 0
for _ in range(NT):
    t = random.uniform(lo, hi)
    if any(abs(th(N) - t) < tol_deg for N in range(33, 177)):
        hit2 += 1
print(f"   整數 N∈[33,176] 命中率: {hit2/NT*100:.1f}% — 對比框架 7 尺度: 密度 ×{max(1, hit2/max(1,hit)):.0f}")
print(f"   ⇒ 框架尺度限制 (7 個 N) 本身係強結構約束; N=55 喺約束內唯一命中")

print("\n6) 唯一性: 7 個框架 N 對目標 49.1980° 嘅距離")
for N in NAT:
    print(f"   θ({N:3d}) = {angles[N]:.4f}°  Δ={abs(angles[N]-TARGET_NUFIT):.4f}° ({abs(angles[N]-TARGET_NUFIT)/TARGET_NUFIT*100:.4f}%)")
print(f"   → 唯一 θ(55) 喺 0.003%; 次近 θ(46) 0.09° (30× 遠) ⇒ multiplicity 1")

print("\n7) 總結裁決")
print("   A. 1/462: 1.5% off = form-precision, 家族 1/n 密度中 — 🟡 記檔")
print("   B. (γ₇−γ₆)/30: 0.1% off = form-precision, 家族極密 — 🟡 記檔 (0.1% 未達結構)")
print("   C. 1/469: 精度好但 469 冇結構身份 — 🔴 過適示範 (SESSION_START 已定)")
print("   D. N=55: 0.003% off + 框架尺度內唯一 + null 3-4% < 5% ⇒ 🟡 升格候選 (未推導)")
