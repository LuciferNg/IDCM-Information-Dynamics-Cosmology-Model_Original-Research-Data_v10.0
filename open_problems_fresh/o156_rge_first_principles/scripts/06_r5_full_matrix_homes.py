#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
06_r5_full_matrix_homes.py — R5 續: 混合家全矩陣預測 (O156)
==========================================================
若 θ₂₃ 住喺 55 (chain 耦合比), θ₁₂/θ₁₃ 留 tree (33), δ = 230°:
標準參數化 PMNS 矩陣用 {θ₁₂, θ₂₃(55), θ₁₃, δ} vs {θ₂₃(88)} 對比 NuFIT |U|。
獨立預測: 混合家矩陣應該好過全-88 矩陣 (如果 55-home 係真)。
"""
import math
DEG = 180.0/math.pi
RAD = math.pi/180.0

def th23(N):
    return math.degrees(math.atan(math.sin(7*math.pi/N)/math.sin(6*math.pi/N)))

def pmns_matrix(t12, t23, t13, delta):
    """標準參數化 (PDG): c_i = cos, s_i = sin"""
    c12, s12 = math.cos(t12*RAD), math.sin(t12*RAD)
    c23, s23 = math.cos(t23*RAD), math.sin(t23*RAD)
    c13, s13 = math.cos(t13*RAD), math.sin(t13*RAD)
    e = math.cos(delta*RAD) + 1j*math.sin(delta*RAD)
    U = [
        [c12*c13, s12*c13, s13*e.conjugate()],
        [-s12*c23 - c12*s23*s13*e, c12*c23 - s12*s23*s13*e, s23*c13],
        [s12*s23 - c12*c23*s13*e, -c12*s23 - s12*c23*s13*e, c23*c13],
    ]
    return U

# NuFIT 5.2 |U| (docs/09)
NUFIT = [
    [0.8250, 0.5452, 0.1490],
    [0.3083, 0.5871, 0.7485],
    [0.4737, 0.5984, 0.6462],
]

# 框架角 (docs/09): θ₁₂ = atan((K_tree+φ)/(K_tree·φ−1)), φ = 1.618034
phi = 1.61803398875
t12 = math.degrees(math.atan((33+phi)/(33*phi-1)))  # 33.4532
t13 = math.degrees(math.asin((0.154508)*(32/33)))  # 8.6169
delta = 230.0

print("框架角: θ₁₂ = {:.4f}°, θ₁₃ = {:.4f}°, δ = {:.0f}°".format(t12, t13, delta))

for label, t23v in [("θ₂₃(88) 全-88", th23(88)), ("θ₂₃(55) 混合家", th23(55)),
                    ("θ₂₃(88)−1/462", th23(88)-1/462)]:
    U = pmns_matrix(t12, t23v, t13, delta)
    print(f"\n--- {label}: θ₂₃ = {t23v:.4f}° ---")
    maxd, meand = 0.0, 0.0
    for i in range(3):
        row = []
        for j in range(3):
            d = abs(abs(U[i][j]) - NUFIT[i][j])
            row.append(d)
            maxd = max(maxd, d)
            meand += d
        print(f"   |U| row{i+1}: {[f'{abs(U[i][j]):.4f}' for j in range(3)]}  Δ={[f'{d:.4f}' for d in row]}")
    print(f"   maxΔ|U| = {maxd:.4f}  meanΔ = {meand/9:.4f}")
    # J_CP
    J = abs((U[0][0]*U[1][1]*U[0][1].conjugate()*U[1][0]).imag)
    print(f"   J_CP = {J:.4f} (NuFIT 0.0254)")

print("\n裁決:")
print("   - 若混合家 (θ₂₃(55)) maxΔ|U| < 全-88: 支持 55-home 獨立預測")
print("   - 若兩者差唔多: 55-home 對矩陣級冇獨立預測力 (只有 sin²θ₂₃ 角級)")
