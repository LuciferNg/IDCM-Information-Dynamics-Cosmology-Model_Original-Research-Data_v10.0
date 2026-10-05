#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
42c_pmns_normalization.py — PMNS 歸一化結構分析
=================================================
用戶觀察: 混合來源怪怪的, 未歸一化。
確認: e-row W-ratio = 1.0226 ≠ 1 (γ₆/8 溢出 12-sector 歸一化)。

1. 條件概率完成: |U_e1|² = (γ₃/(γ₂+γ₃))·(1−γ₆/8) 等 — row 和 = 1 精確
2. 歸一化質量矩陣: M = m₀'·[diag(φ⁻²,φ⁻¹,1) + s·(P₁₂+P₂₃)], P = 歸一化 projector
3. s 掃描 → 角度 vs NuFIT; s 結構身份檢查
4. δ = 230° 全矩陣測試 (角度啱唔啱?)
5. δ_CP 身份候選
"""
import numpy as np, math, cmath

phi = (1+math.sqrt(5))/2
def gamma(n): return 4*math.sin(n*math.pi/88)**2
def omega(n): return 2*math.sin(n*math.pi/88)

s12_2N, s23_2N, s13_2N, dN = 0.304, 0.573, 0.0222, 230.0

def angles_from_U(Um, label=""):
    s13 = abs(Um[0,2]); s13_2 = s13**2
    s12_2 = abs(Um[0,1])**2/(1-s13_2)
    s23_2 = abs(Um[1,2])**2/(1-s13_2)
    d = -cmath.phase(Um[0,2])
    print(f"  {label}: θ₁₃ = {math.degrees(math.asin(s13)):.3f}° | θ₁₂ = {math.degrees(math.asin(math.sqrt(s12_2))):.3f}° | θ₂₃ = {math.degrees(math.asin(math.sqrt(s23_2))):.3f}° | δ = {math.degrees(d):.1f}°")
    return s12_2, s23_2, s13_2

print("=== 1. 條件概率完成 (e-row 歸一化) ===")
g2, g3, g6, g7 = gamma(2), gamma(3), gamma(6), gamma(7)
s13A2 = g6/8
ue1 = math.sqrt(g3/(g2+g3)*(1-s13A2))
ue2 = math.sqrt(g2/(g2+g3)*(1-s13A2))
ue3 = math.sqrt(s13A2)
print(f"  |U_e1|² = {ue1**2:.6f} (NuFIT 0.681) |U_e2|² = {ue2**2:.6f} (0.297) |U_e3|² = {ue3**2:.6f} (0.0222)")
print(f"  row sum = {ue1**2+ue2**2+ue3**2:.8f} (應 = 1)")
print(f"  vs NuFIT: e1 Δ = {abs(ue1**2-0.681)/0.681*100:.2f}%, e2 Δ = {abs(ue2**2-0.297)/0.297*100:.2f}%, e3 Δ = {abs(ue3**2-0.0222)/0.0222*100:.2f}%")
print(f"  γ₆/8 = {s13A2:.6f} vs 1/N_d = {1/44:.6f} (Δ {abs(s13A2-1/44)/(1/44)*100:.2f}%)")

print("\n=== 2. 歸一化質量矩陣 M = diag(φ) + s·(P₁₂+P₂₃) ===")
# P₁₂: 12-sector projector (e, μ) — mode 3→ν₁ (e 位), mode 2→ν₂ (μ 位)
v12 = np.array([omega(3), omega(2), 0.0]); v12 /= np.linalg.norm(v12)
# P₂₃: 23-sector projector (μ, τ) — mode 6→ν₂ (μ 位), mode 7→ν₃ (τ 位)
v23 = np.array([0.0, omega(6), omega(7)]); v23 /= np.linalg.norm(v23)
P12 = np.outer(v12, v12); P23 = np.outer(v23, v23)
print(f"  P₁₂ trace = {np.trace(P12):.6f}, P₂₃ trace = {np.trace(P23):.6f} (歸一化 ✓)")
D = np.diag([phi**-2, phi**-1, 1.0])
for s in [0.3, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0]:
    M = D + s*(P12+P23)
    w, V = np.linalg.eigh(M)
    angles_from_U(V, f"s={s}")

print("\n=== 3. 另一 assignment: v₁₂ = (ω₂, ω₃), v₂₃ = (ω₇, ω₆) ===")
v12b = np.array([omega(2), omega(3), 0.0]); v12b /= np.linalg.norm(v12b)
v23b = np.array([0.0, omega(7), omega(6)]); v23b /= np.linalg.norm(v23b)
P12b = np.outer(v12b, v12b); P23b = np.outer(v23b, v23b)
for s in [0.5, 1.0, 2.0, 5.0]:
    M = D + s*(P12b+P23b)
    w, V = np.linalg.eigh(M)
    angles_from_U(V, f"s={s} (b)")

print("\n=== 4. 角度啱, δ = 230° vs 72° 全矩陣 ===")
def Unufit(s12_2, s23_2, s13_2, ddeg):
    s12,s23,s13 = math.sqrt(s12_2),math.sqrt(s23_2),math.sqrt(s13_2)
    c12,c23,c13 = math.sqrt(1-s12_2),math.sqrt(1-s23_2),math.sqrt(1-s13_2)
    e = cmath.exp(-1j*math.radians(ddeg))
    return np.array([[c12*c13, s12*c13, s13*e],
        [-s12*c23-c12*s23*s13*e.conjugate(), c12*c23-s12*s23*s13*e.conjugate(), s23*c13],
        [s12*s23-c12*c23*s13*e.conjugate(), -c12*s23-s12*c23*s13*e.conjugate(), c23*c13]])
# 混合組角度: θ₁₂ tree, θ₂₃ chain, θ₁₃ tree
th12 = math.degrees(math.atan(phi**-1)) + 1/33*180/math.pi
th23 = math.degrees(math.atan(math.sqrt(g7/g6)))
th13 = math.degrees(math.asin(phi**-1/4*(1-1/33)))
print(f"  混合組角度: θ₁₂ = {th12:.4f}°, θ₂₃ = {th23:.4f}°, θ₁₃ = {th13:.4f}°")
for d in [72.0, 230.0]:
    U = Unufit(math.sin(math.radians(th12))**2, math.sin(math.radians(th23))**2, math.sin(math.radians(th13))**2, d)
    UN = Unufit(s12_2N, s23_2N, s13_2N, 230.0)
    dm = np.abs(np.abs(U) - np.abs(UN))
    print(f"  δ = {d:.0f}°: 全矩陣 maxΔ|U| = {np.max(dm):.3f}, meanΔ = {np.mean(dm):.4f}")
    print(f"    逐條目 %差: " + " ".join(f"{dm[i,j]/np.abs(UN[i,j])*100:5.1f}%" for i in range(3) for j in range(3)))

print("\n=== 5. δ_CP 身份候選 (obs 230°±36°) ===")
cands = {
    "2π/5 (Z₅)": 72, "4π/5 (twisted)": 144, "2×72+86": 230,
    "144+90−B (4π/5+Σγ_even−B)": 144+90-4, "3×72+14": 3*72+14,
    "360−128 (2⁷)": 360-128, "176+56": 176+56, "2π−72−58": 360-72-58,
    "360−2π/φ (222.5 trap)": 360-2*180/math.pi*math.acos(-1)/phi,
}
for nm, v in cands.items():
    print(f"  {nm} = {v:.2f}°  (Δ vs 230 = {abs(v-230):.1f}°)")

print("\n=== 6. s 結構身份檢查 (若 §2 有命中) ===")
for nm, v in [("1/ε", 1/(phi**-1/4)), ("1/γ₆", 1/g6), ("K_tree", 33), ("2B", 8), ("N_d", 44), ("1/φ⁻²", phi**2), ("L₅", 11)]:
    print(f"  {nm} = {v:.4f}")
