#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
42_pmns_wfield_texture.py — PMNS 從 W-field 味本徵結構推導
=============================================================
方向 (用戶): PMNS = 中微子味本徵, 中微子 = W-Field 激發態

W-field 機制 (O36-O39, O49, O65, O69 已確立):
  - K = K_chain ⊗ K_tree;  γ_n = 4sin²(nπ/88);  ω_n = 2sin(nπ/88) = √γ_n
  - 費米子耦合 g_n = κ·ω_n (κ = 1/16);  質量 m_n ∝ g_n²/ω_n = κ²ω_n ∝ ω_n
  - 中微子 = p6 模式 (n=6);  質量譜 m₁:m₂:m₃ = φ⁻²:φ⁻¹:1 (tree sector, O49)
  - 輕子模式 (O69): e→n=1, μ→n=7, τ→n=20;  PMNS 模式 (O69): θ₁₂→{2,3}, θ₂₃→{6,7}, θ₁₃→{6}
  - O65 公式: sin²θ₁₂ = γ₂/(γ₂+γ₃), sin²θ₂₃ = γ₇/(γ₇+γ₆), sin²θ₁₃ = γ₆/2³

關鍵結構觀察: sin²θ = γ_a/(γ_a+γ_b) ⟺ rank-1 塊 M = vv†, v = (√γ_a, √γ_b)
  = (ω_a, ω_b)⊗(ω_a, ω_b) — W-field 耦合 texture (g_α g_β = κ²ω_αω_β)

任務:
  1. 由 NuFIT 5.2 角度重建 M_flavor = U·diag(φ⁻²,φ⁻¹,1)·U†, 檢視條目結構
  2. 測試 W-field texture 候選: T1 (tree-adjacency), T2 (rank-1 混合), T3 (O65 塊結構)
  3. 對角化 → 角度 vs NuFIT;  唯一性 + null-control
  4. δ_CP 候選檢查 (Z₅: 72°, 144°;  obs 230°)
"""
import numpy as np
import cmath, math
from itertools import product

phi = (1+math.sqrt(5))/2
def gamma(n): return 4*math.sin(n*math.pi/88)**2
def omega(n): return 2*math.sin(n*math.pi/88)

# ---- 1. NuFIT 5.2 (NO) best fit ----
s12_2, s23_2, s13_2, dcp = 0.304, 0.573, 0.0222, math.radians(230)
s12, s23, s13 = math.sqrt(s12_2), math.sqrt(s23_2), math.sqrt(s13_2)
c12, c23, c13 = math.sqrt(1-s12_2), math.sqrt(1-s23_2), math.sqrt(1-s13_2)
e = cmath.exp(-1j*dcp)
U = np.array([
    [c12*c13, s12*c13, s13*e],
    [-s12*c23 - c12*s23*s13*e.conjugate(), c12*c23 - s12*s23*s13*e.conjugate(), s23*c13],
    [s12*s23 - c12*c23*s13*e.conjugate(), -c12*s23 - s12*c23*s13*e.conjugate(), c23*c13],
], dtype=complex)
# unitarity check
UU = U @ U.conj().T
print(f"NuFIT unitarity max|UU†-I| = {np.max(np.abs(UU-np.eye(3))):.2e}")

# ---- 2. M_flavor from φ-hierarchy ----
mvec = np.array([phi**-2, phi**-1, 1.0])  # m₁:m₂:m₃
Mf = U @ np.diag(mvec) @ U.conj().T
print("\n=== M_flavor = U·diag(φ⁻²,φ⁻¹,1)·U† (m₃=1 單位) ===")
for i in range(3):
    row = "  ".join(f"{Mf[i,j].real:+.6f}{Mf[i,j].imag:+.6f}i" if abs(Mf[i,j].imag)>1e-12 else f"{Mf[i,j].real:+.6f}    " for j in range(3))
    print(f"  {row}")

# ---- 3. 候選結構值 ----
print("\n=== 候選結構值 ===")
gvals = {n: gamma(n) for n in [2,3,6,7,20,1]}
wvals = {n: omega(n) for n in [2,3,6,7,20,1]}
for n in [1,2,3,6,7,20]:
    print(f"  γ_{n:2d} = {gvals[n]:.6f}   ω_{n:2d} = {wvals[n]:.6f}   √(γ₂γ₃) = {math.sqrt(gvals[2]*gvals[3]):.6f}  √(γ₆γ₇) = {math.sqrt(gvals[6]*gvals[7]):.6f}")
print(f"  φ⁻¹={phi**-1:.6f} φ⁻²={phi**-2:.6f} φ⁻³={phi**-3:.6f} φ⁻⁴={phi**-4:.6f}")
print(f"  γ₆/8 = {gvals[6]/8:.6f}   γ₆/16 = {gvals[6]/16:.6f}")

# M_flavor 條目 vs 候選
print("\n=== M_flavor 條目 vs 候選 ===")
Mflat = [(i,j,Mf[i,j]) for i in range(3) for j in range(3)]
cands = {
    "γ₂": gvals[2], "γ₃": gvals[3], "γ₆": gvals[6], "γ₇": gvals[7], "γ₂₀": gvals[20],
    "√(γ₂γ₃)": math.sqrt(gvals[2]*gvals[3]), "√(γ₆γ₇)": math.sqrt(gvals[6]*gvals[7]),
    "ω₂ω₃": wvals[2]*wvals[3], "ω₆ω₇": wvals[6]*wvals[7],
    "φ⁻¹": phi**-1, "φ⁻²": phi**-2, "φ⁻³": phi**-3, "φ⁻⁴": phi**-4, "φ⁻⁵": phi**-5,
    "1/2": 0.5, "1/3": 1/3, "1/4": 0.25, "1/8": 0.125,
}
for (i,j,Mij) in Mflat:
    if abs(Mij.imag) > 1e-10:
        continue
    v = Mij.real
    best = sorted(cands.items(), key=lambda kv: abs(kv[1]-v))[:3]
    print(f"  M[{i+1}{j+1}] = {v:+.6f}  近: " + ", ".join(f"{k}={w:.5f} (Δ{abs(w-v):.5f})" for k,w in best))

# ---- 4. 候選 texture 對角化 ----
def angles_from_U(Um):
    """從 3×3 unitary 提取 (θ₁₂, θ₂₃, θ₁₃, δ)"""
    s13 = abs(Um[0,2]);  s13_2 = s13**2
    s12_2 = abs(Um[0,1])**2/(1-s13_2)
    s23_2 = abs(Um[1,2])**2/(1-s13_2)
    d = -cmath.phase(Um[0,2])  # δ from U_e3 phase (convention)
    return math.degrees(math.asin(s13)), math.degrees(math.asin(math.sqrt(s12_2))), math.degrees(math.asin(math.sqrt(s23_2))), math.degrees(d)

def report(name, M):
    w, V = np.linalg.eigh(M)
    # 排序: 質量升序, V 行 = 味, 列 = 質量本徵
    th13, th12, th23, d = angles_from_U(V)
    print(f"\n[{name}] 特徵值 = {np.sort(w).round(5)}")
    print(f"  θ₁₃ = {th13:.3f}° (NuFIT 8.54°) | θ₁₂ = {th12:.3f}° (33.41°) | θ₂₃ = {th23:.3f}° (49.2°/42.2°)")
    return V

print("\n=== 4. 候選 texture 對角化 (m₃=1 單位) ===")
# T1: φ-diag + λ·tree-adjacency (Fibonacci recursion 鄰接)
for lam in [phi**-1, phi**-2, 1/math.sqrt(5), 0.2754, phi**-3]:
    M1 = np.diag([phi**-2, phi**-1, 1.0]) + lam*np.array([[0,1,0],[1,0,1],[0,1,0]])
    report(f"T1 φ-diag + λ={lam:.4f}·adjacency", M1)

# T2: φ-diag + λ·J (democratic)
for lam in [phi**-1, phi**-2, 0.2754, 0.5]:
    M2 = np.diag([phi**-2, phi**-1, 1.0]) + lam*np.ones((3,3))
    report(f"T2 φ-diag + λ={lam:.4f}·J", M2)

# T3: O65 塊結構 — 12 塊 v₂₃v₂₃† + 23 塊 v₆₇v₆₇† (W-field 耦合 texture)
v23 = np.array([math.sqrt(gvals[2]), math.sqrt(gvals[3])]); v23 /= np.linalg.norm(v23)
v67 = np.array([math.sqrt(gvals[6]), math.sqrt(gvals[7])]); v67 /= np.linalg.norm(v67)
for s in [1.0, phi, phi**2, 9.0]:
    M3 = np.zeros((3,3))
    M3[:2,:2] += s*np.outer(v23, v23)
    M3[1:,1:] += s*np.outer(v67, v67)
    report(f"T3 W-texture s={s}", M3)

# T4: 完整 W-field texture: M_αβ ∝ ω_α ω_β (lepton modes) + φ-diag
wL = np.array([wvals[1], wvals[7], wvals[20]])
for c in [0.01, 0.03, 0.1, 0.3, 1.0]:
    M4 = np.diag([phi**-2, phi**-1, 1.0]) + c*np.outer(wL, wL)
    report(f"T4 φ-diag + c={c}·(ω₁,ω₇,ω₂₀)⊗²", M4)

# ---- 5. NuFIT M_flavor 嘅結構匹配: 邊個 texture 最接近? ----
print("\n=== 5. M_flavor 匹配度 (Frobenius) ===")
cands_mat = {
    "T1 λ=φ⁻¹": np.diag([phi**-2, phi**-1, 1.0]) + phi**-1*np.array([[0,1,0],[1,0,1],[0,1,0]]),
    "T2 λ=φ⁻¹ J": np.diag([phi**-2, phi**-1, 1.0]) + phi**-1*np.ones((3,3)),
    "T3 s=1": None,
    "T4 c=0.03": np.diag([phi**-2, phi**-1, 1.0]) + 0.03*np.outer(wL, wL),
}
M3full = np.zeros((3,3))
M3full[:2,:2] += np.outer(v23, v23); M3full[1:,1:] += np.outer(v67, v67)
cands_mat["T3 s=1"] = M3full
for name, Mc in cands_mat.items():
    d = np.linalg.norm(Mf - Mc)
    print(f"  {name}: ‖Mf−M‖ = {d:.4f}")

# ---- 6. δ_CP 候選 ----
print("\n=== 6. δ_CP 候選 (obs 230°, NuFIT 5.2 NO) ===")
for dname, dv in [("2π/5 = 72°", 72), ("4π/5 = 144°", 144), ("2π/5+180°=252°", 252), ("232°(obs)", 232)]:
    print(f"  {dname}: Δ = {abs(dv-230):.1f}°")
