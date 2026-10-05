#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
42d_pmns_null_delta.py — 混合組 null-control + δ_CP 分析
===========================================================
1. 三種形式對隨機 target 嘅命中率 (固定常數, 唔係搜尋):
   F1: θ₁₂ = atan(β) + atan(1/33)  [固定]
   F2: θ₂₃ = atan(√(γ₇/γ₆))       [O69 選定模式]
   F3: θ₁₃ = arcsin(ε(1−1/33))    [固定]
2. 全矩陣 δ = 230° 完整結果 + J_CP
3. δ_CP 候選分析
"""
import numpy as np, math, cmath, random

phi = (1+math.sqrt(5))/2
def gamma(n): return 4*math.sin(n*math.pi/88)**2
def omega(n): return 2*math.sin(n*math.pi/88)

# 框架值
th12_F = math.degrees(math.atan(phi**-1)) + math.degrees(math.atan(1/33))
th23_F = math.degrees(math.atan(math.sqrt(gamma(7)/gamma(6))))
th13_F = math.degrees(math.asin(phi**-1/4*(1-1/33)))
print(f"框架角度: θ₁₂ = {th12_F:.4f}°, θ₂₃ = {th23_F:.4f}°, θ₁₃ = {th13_F:.4f}°")
print(f"NuFIT:    θ₁₂ = 33.460°, θ₂₃ = 49.198°, θ₁₃ = 8.569°")

print("\n=== 1. Null-control (固定形式 vs 隨機 target) ===")
random.seed(42)
# F2: atan(√(γ_a/γ_b)) — O69 選定 (7,6). 隨機 target 命中率 (用隨機 (a,b) 對): 密度檢查
# 但關鍵: (7,6) 係固定對. 測試: 隨機 target 喺 (7,6) 嘅命中率 = 應該極低
hits = 0; N = 10000
for _ in range(N):
    t = random.uniform(5, 55)  # 隨機角度 target
    if abs(t - th23_F) < 0.5:
        hits += 1
print(f"F2: 隨機 target 命中 θ₂₃=49.32° (±0.5°) 機率 = {hits/N*100:.3f}%  (框架值固定 (7,6))")
# F1: atan(β)+atan(1/33) — 固定
hits = 0
for _ in range(N):
    t = random.uniform(10, 45)
    if abs(t - th12_F) < 0.5:
        hits += 1
print(f"F1: 隨機 target 命中 θ₁₂=33.45° (±0.5°) 機率 = {hits/N*100:.3f}%")
# F3
hits = 0
for _ in range(N):
    t = random.uniform(1, 20)
    if abs(t - th13_F) < 0.5:
        hits += 1
print(f"F3: 隨機 target 命中 θ₁₃=8.62° (±0.5°) 機率 = {hits/N*100:.3f}%")

# 對照: 若形式係「搜尋所有 (a,b) 對」— 密度檢查
print("\n  對照: 若用所有 (a,b) 對搜尋 atan(√(γ_a/γ_b)):")
allvals = sorted(math.degrees(math.atan(math.sqrt(gamma(a)/gamma(b)))) for a in range(1,45) for b in range(1,45) if a != b)
hits = 0
for _ in range(N):
    t = random.uniform(1, 89)
    if any(abs(t-v) < 0.5 for v in allvals):
        hits += 1
print(f"  隨機 target 被某 (a,b) 命中 (±0.5°) 機率 = {hits/N*100:.1f}% (密度假象確認)")

print("\n=== 2. 全矩陣 δ = 230° (標準參數化, 零自由度) ===")
def Unufit(s12_2, s23_2, s13_2, ddeg):
    s12,s23,s13 = math.sqrt(s12_2),math.sqrt(s23_2),math.sqrt(s13_2)
    c12,c23,c13 = math.sqrt(1-s12_2),math.sqrt(1-s23_2),math.sqrt(1-s13_2)
    e = cmath.exp(-1j*math.radians(ddeg))
    return np.array([[c12*c13, s12*c13, s13*e],
        [-s12*c23-c12*s23*s13*e.conjugate(), c12*c23-s12*s23*s13*e.conjugate(), s23*c13],
        [s12*s23-c12*c23*s13*e.conjugate(), -c12*s23-s12*c23*s13*e.conjugate(), c23*c13]])
s12_2F = math.sin(math.radians(th12_F))**2
s23_2F = math.sin(math.radians(th23_F))**2
s13_2F = math.sin(math.radians(th13_F))**2
UN = Unufit(0.304, 0.573, 0.0222, 230.0)
for d in [230.0, 230.4, 72.0]:
    U = Unufit(s12_2F, s23_2F, s13_2F, d)
    dm = np.abs(np.abs(U)-np.abs(UN))
    # J_CP
    J = s12_2F**0.5*math.sqrt(1-s12_2F)*s23_2F**0.5*math.sqrt(1-s23_2F)*math.sqrt(s13_2F)*(1-s13_2F)*abs(math.sin(math.radians(d)))
    print(f"  δ = {d:.1f}°: maxΔ|U| = {np.max(dm):.4f}, meanΔ = {np.mean(dm):.5f}, J_CP = {J:.4f} (NuFIT 0.0254)")

print("\n=== 3. δ_CP 候選身份 ===")
dCKM = 66.399960
cands = [
    ("2π/5 (Z₅ 基本相位)", 72.0),
    ("4π/5 (Z₅ twisted)", 144.0),
    ("4π/5 + Σγ_even − B", 144+90-4),
    ("180 + δ_CKM − B²", 180+dCKM-16),
    ("360 − 2⁷", 232.0),
    ("176 + 2×28", 176+56),
    ("3×72 + 2L₄ (14)", 3*72+14),
]
for nm, v in cands:
    print(f"  {nm} = {v:.2f}°  (Δ vs NuFIT 230° = {abs(v-230):.1f}°, 1σ 範圍 205-266°)")

print("\n=== 4. δ = 230° 對比 NuFIT 5.2 完整 |U| ===")
U = Unufit(s12_2F, s23_2F, s13_2F, 230.0)
print("  IDCM |U| (混合組 + δ=230°):")
for i in range(3):
    print(f"    [{abs(U[i,0]):.4f}  {abs(U[i,1]):.4f}  {abs(U[i,2]):.4f}]")
print("  NuFIT |U|:")
for i in range(3):
    print(f"    [{abs(UN[i,0]):.4f}  {abs(UN[i,1]):.4f}  {abs(UN[i,2]):.4f}]")
