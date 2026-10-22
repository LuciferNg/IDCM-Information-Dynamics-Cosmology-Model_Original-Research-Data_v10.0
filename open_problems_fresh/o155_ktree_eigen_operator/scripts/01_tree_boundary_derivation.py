#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
45_tree_boundary_derivation.py — +1/33 樹邊界算子剛性商值
===========================================================
用戶要求: 將 θ₁₂ = atan(φ⁻¹)+1/33 嘅 +1/33 從唯象項還原為 K_tree 邊界算子商值。
假設: 1/33 = Tr(P_B)/K_tree — 邊界 level 喺 33-level tree 嘅歸一化密度;
      32/33 = Tr(P_I)/K_tree — 內部密度; co-closure: P_B + P_I = 1。
檢驗:
1. atan(1/33) vs 1/33 rad
2. tan 加法: θ₁₂ = atan(β)+atan(1/33) = atan((K_tree+φ)/(K_tree·φ−1))
3. 邊界/內部 = 1/33 + 32/33 = 1
4. 33-level tree Laplacian 總和 = 66 = 2K_tree = 2N_gen·L₅
5. θ₂₃ 殘差 0.123° 嘅候選修正 (唔宣稱)
6. null: 1/n 家族邊個 n 最好
"""
import math
DEG = 180.0/math.pi
N, KTREE = 88, 33          # 框架 convention: ω_n = 2sin(nπ/88) (同 CKM beat 記錄一致)
phi = (1+math.sqrt(5))/2
beta = 1/phi
omega = lambda k: 2*math.sin(k*math.pi/N)

# NuFIT 目標
t12_n, t23_n, t13_n = 33.4602, 49.1980, 8.5690

print("1) atan(1/33) vs 1/33 rad")
a1 = math.degrees(math.atan(1/KTREE))
a2 = 1/KTREE*DEG
print(f"   atan(1/33) = {a1:.6f}° | 1/33 rad = {a2:.6f}° | Δ = {abs(a1-a2)*60:.2f} arcmin")

print("\n2) tan 加法形式")
t12 = math.degrees(math.atan(beta)) + math.degrees(math.atan(1/KTREE))
tanf = (KTREE+phi)/(KTREE*phi-1)
print(f"   θ₁₂ = atan(β)+atan(1/33) = {t12:.4f}° (NuFIT {t12_n}°, Δ {t12-t12_n:+.4f}°)")
print(f"   tanθ₁₂ = (K_tree+φ)/(K_tree·φ−1) = {tanf:.8f} vs tan(θ₁₂) = {math.tan(math.radians(t12)):.8f}")

print("\n3) 邊界/內部 unity 分解")
print(f"   1/33 + 32/33 = {1/KTREE + 32/KTREE:.12f}")

print("\n4) 33-level tree Laplacian")
Lap = sum(4*math.sin(k*math.pi/68)**2 for k in range(1, 34))
print(f"   sum 4sin^2(k*pi/68) k=1..33 = {Lap:.6f} = 2K_tree = {2*KTREE} = 2N_gen*L5 = {2*3*11}")

print("\n5) θ₂₃ 殘差候選 (唔宣稱)")
t23 = math.degrees(math.atan(omega(7)/omega(6)))
res = t23 - t23_n
print(f"   θ₂₃ = atan(ω₇/ω₆) = {t23:.4f}°, 殘差 = {res:+.4f}° = {abs(res)*math.pi/180:.6f} rad")
cand = {"2K_tree·L₄": 2*33*7, "N_d⁻·L₅": 42*11, "K_tree·L₆": 33*18, "2K_tree·2N_gen": 2*33*6}
for name, n in cand.items():
    print(f"   候選 1/{name} = 1/{n} = {1/n*DEG:.4f}° → θ₂₃−1/{name} = {t23-1/n*DEG:.4f}° (Δ {t23-1/n*DEG-t23_n:+.4f}°)")

print("\n6) 1/n 家族 (θ₁₂) — 邊個 n 最好 (1/n rad)")
best = []
for n in range(30, 38):
    v = math.degrees(math.atan(beta)) + (1/n)*DEG   # 1/n rad
    best.append((abs(v-t12_n), n, v))
    print(f"   n={n}: θ₁₂ = {v:.4f}° Δ = {v-t12_n:+.4f}°")
best.sort()
print(f"   ★ 最細殘差: n = {best[0][1]} (Δ {best[0][0]:.4f}°), 次佳 n = {best[1][1]} (Δ {best[1][0]:.4f}°) → 比率 {best[1][0]/best[0][0]:.1f}×")

print("\n7) 邊界算子商值表述")
print(f"   Tr(P_B)/K_tree = 1/33 → θ₁₂ = atan(β) + atan(Tr(P_B)/K_tree)")
print(f"   Tr(P_I)/K_tree = 32/33 → sinθ₁₃ = ε·Tr(P_I)/K_tree")
print(f"   sinθ₁₃ = {math.sin(math.radians(t13_n)):.6f} vs ε·32/33 = {beta/4*32/33:.6f} ({abs(math.sin(math.radians(t13_n))-beta/4*32/33)/(beta/4*32/33)*100:.2f}%)")
