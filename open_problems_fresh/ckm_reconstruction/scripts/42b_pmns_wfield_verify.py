#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
42b_pmns_wfield_verify.py — W-field 味本徵結構完整驗證
========================================================
比較三組 PMNS 公式 vs NuFIT 5.2 (NO, 2024):
  sin²θ₁₂ = 0.304±0.012, sin²θ₂₃ = 0.573+0.018-0.023, sin²θ₁₃ = 0.0222±0.0006, δ = 230°+36°-25°

A. Chain 組 (O65/O69): sin²θ₁₂ = γ₂/(γ₂+γ₃), sin²θ₂₃ = γ₇/(γ₇+γ₆), sin²θ₁₃ = γ₆/2³
B. Tree 組 (pmns_derivation §2): θ₁₂ = atan(φ⁻¹)+1/K_tree, θ₂₃ = 45° (SYNC), θ₁₃ = arcsin(ε(M-1)/M), δ = 2π/5
C. 混合組 (各取最優): θ₁₂ tree, θ₂₃ chain, θ₁₃ tree
D. √-ratio |U| 條目 vs NuFIT (W-field 耦合比 U_αi = ω/√(Σω²))
E. J_CP for δ = 72°/144°/230°
F. Unitarity defect 分析
"""
import numpy as np, math, cmath

phi = (1+math.sqrt(5))/2
eps = phi**-1/4
K_tree = 33
def gamma(n): return 4*math.sin(n*math.pi/88)**2
def omega(n): return 2*math.sin(n*math.pi/88)

# NuFIT 5.2 (NO)
s12_2N, s23_2N, s13_2N, dN = 0.304, 0.573, 0.0222, 230.0

print("=== A. Chain 組 (O65/O69) ===")
s12_2A = gamma(2)/(gamma(2)+gamma(3))
s23_2A = gamma(7)/(gamma(7)+gamma(6))
s13_2A = gamma(6)/8
for name, v, t in [("sin²θ₁₂", s12_2A, s12_2N), ("sin²θ₂₃", s23_2A, s23_2N), ("sin²θ₁₃", s13_2A, s13_2N)]:
    print(f"  {name} = {v:.6f} vs NuFIT {t:.4f}  Δ = {abs(v-t)/t*100:.2f}%")
print(f"  θ₁₂ = {math.degrees(math.asin(math.sqrt(s12_2A))):.3f}°  θ₂₃ = {math.degrees(math.asin(math.sqrt(s23_2A))):.3f}°  θ₁₃ = {math.degrees(math.asin(math.sqrt(s13_2A))):.3f}°")

print("\n=== B. Tree 組 ===")
th12_B = math.degrees(math.atan(phi**-1)) + 1/K_tree*180/math.pi
s12_2B = math.sin(math.radians(th12_B))**2
th13_B = math.degrees(math.asin(eps*(K_tree-1)/K_tree))
s13_2B = math.sin(math.radians(th13_B))**2
print(f"  θ₁₂ = atan(φ⁻¹) + 1/33 = {th12_B:.4f}° (sin² = {s12_2B:.6f}, NuFIT Δ = {abs(s12_2B-s12_2N)/s12_2N*100:.2f}%)")
print(f"  θ₂₃ = 45° (SYNC): sin² = 0.5 vs NuFIT 0.573 → {abs(0.5-0.573)/0.573*100:.1f}% (3.2σ)")
print(f"  θ₁₃ = arcsin(ε·32/33) = {th13_B:.4f}° (sin² = {s13_2B:.6f}, NuFIT Δ = {abs(s13_2B-s13_2N)/s13_2N*100:.2f}%)")

print("\n=== C. 混合組 (θ₁₂ tree / θ₂₃ chain / θ₁₃ tree) ===")
for nm, v, t in [("θ₁₂", th12_B, math.degrees(math.asin(math.sqrt(s12_2N)))), 
                 ("θ₂₃", math.degrees(math.asin(math.sqrt(s23_2A))), math.degrees(math.asin(math.sqrt(s23_2N)))),
                 ("θ₁₃", th13_B, math.degrees(math.asin(math.sqrt(s13_2N))))]:
    print(f"  {nm}: IDCM {v:.3f}° vs NuFIT {t:.3f}°  Δ = {abs(v-t):.3f}°")

print("\n=== D. √-ratio |U| 條目 (W-field 耦合比) ===")
def Unufit(s12_2, s23_2, s13_2, ddeg):
    s12,s23,s13 = math.sqrt(s12_2),math.sqrt(s23_2),math.sqrt(s13_2)
    c12,c23,c13 = math.sqrt(1-s12_2),math.sqrt(1-s23_2),math.sqrt(1-s13_2)
    e = cmath.exp(-1j*math.radians(ddeg))
    return np.array([[c12*c13, s12*c13, s13*e],
        [-s12*c23-c12*s23*s13*e.conjugate(), c12*c23-s12*s23*s13*e.conjugate(), s23*c13],
        [s12*s23-c12*c23*s13*e.conjugate(), -c12*s23-s12*c23*s13*e.conjugate(), c23*c13]])
U = Unufit(s12_2N, s23_2N, s13_2N, dN)
cand = {
    "|U_e1|": math.sqrt(gamma(3)/(gamma(2)+gamma(3))),
    "|U_e2|": math.sqrt(gamma(2)/(gamma(2)+gamma(3))),
    "|U_e3|": math.sqrt(gamma(6)/8),
    "|U_μ3|": math.sqrt(gamma(7)/(gamma(7)+gamma(6))),
    "|U_μ2|": math.sqrt(gamma(6)/(gamma(7)+gamma(6))),
    "|U_τ3|": math.sqrt(gamma(6)/(gamma(7)+gamma(6))),
}
labels = [(0,0,"|U_e1|"),(0,1,"|U_e2|"),(0,2,"|U_e3|"),(1,2,"|U_μ3|"),(1,1,"|U_μ2|")]
for (i,j,nm) in labels:
    obs = abs(U[i,j])
    if nm in cand:
        print(f"  {nm}: W-ratio {cand[nm]:.4f} vs NuFIT {obs:.4f}  Δ = {abs(cand[nm]-obs)/obs*100:.2f}%")

print("\n=== E. J_CP ===")
s12,s23,s13 = math.sqrt(s12_2N),math.sqrt(s23_2N),math.sqrt(s13_2N)
c12,c23,c13 = math.sqrt(1-s12_2N),math.sqrt(1-s23_2N),math.sqrt(1-s13_2N)
Jmax = s12*c12*s23*c23*s13*c13**2
for d in [72.0, 144.0, 230.0]:
    print(f"  J_CP(δ={d:.0f}°) = {Jmax*abs(math.sin(math.radians(d))):.4f}")

print("\n=== F. Unitarity defect (混合組 U) ===")
th12, th23, th13 = th12_B, math.degrees(math.asin(math.sqrt(s23_2A))), th13_B
Uc = Unufit(math.sin(math.radians(th12))**2, math.sin(math.radians(th23))**2, math.sin(math.radians(th13))**2, 72)
UU = Uc@Uc.conj().T
print(f"  混合組+δ=72°: max|UU†−I| = {np.max(np.abs(UU-np.eye(3))):.4f}")
print(f"  |U| ="); 
for i in range(3):
    print(f"    [{abs(Uc[i,0]):.3f}  {abs(Uc[i,1]):.3f}  {abs(Uc[i,2]):.3f}]")
# 同 NuFIT 比較
print(f"  vs NuFIT |U|:")
for i in range(3):
    print(f"    [{abs(U[i,0]):.3f}  {abs(U[i,1]):.3f}  {abs(U[i,2]):.3f}]")

print("\n=== G. 中微子質量譜檢查 (O49) ===")
m0 = (gamma(6)*246)**2/3.9325e13*1e9  # (γ₆v)²/M_comp [GeV]→[eV]; M_comp = M_Pl/(2·h¹¹·h²¹·N_d)
m0p = m0*phi**(1/8)
m3, m2, m1 = m0p, m0p*phi**-1, m0p*phi**-2
dm31 = m3**2-m1**2; dm21 = (m2**2-m1**2)/9
print(f"  m₀' = {m0p:.5f} eV;  m₃:m₂:m₁ = {m3:.5f}:{m2:.5f}:{m1:.5f}")
print(f"  Δm²₃₁ = {dm31:.4e} eV² (PDG 2.437e-3, {abs(dm31-2.437e-3)/2.437e-3*100:.2f}%)")
print(f"  Δm²₂₁ = {dm21:.4e} eV² (PDG 7.53e-5, {abs(dm21-7.53e-5)/7.53e-5*100:.2f}%)")
print(f"  Σm = {m1+m2+m3:.4f} eV (Planck < 0.12)")

print("\n=== H. 1/K_tree co-closure 檢查 ===")
need12 = math.degrees(math.asin(math.sqrt(0.304))) - math.degrees(math.atan(phi**-1))
print(f"  θ₁₂: NuFIT − atan(φ⁻¹) = {need12:.4f}° vs 1/33 rad = {1/33*180/math.pi:.4f}° (Δ {abs(need12-1/33*180/math.pi):.4f}°)")
for n in [31,32,33,34,35]:
    print(f"    1/{n} rad = {180/(n*math.pi):.4f}°  (Δ {abs(need12-180/(n*math.pi)):.4f}°)")
# θ₁₃: sinθ₁₃ = ε(1−1/K_tree) — 需要值
need13 = math.sin(math.radians(math.degrees(math.asin(math.sqrt(0.0222)))))
print(f"  θ₁₃: NuFIT sinθ = {need13:.6f} vs ε(1−1/33) = {eps*(1-1/33):.6f} (Δ {abs(need13-eps*(1-1/33))/need13*100:.2f}%) vs ε = {eps:.6f} (Δ {abs(need13-eps)/need13*100:.2f}%)")
# 2-adic 對照: γ₆/2³ vs ε²(1−1/33)²
print(f"  sin²θ₁₃: γ₆/8 = {gamma(6)/8:.6f} vs (ε·32/33)² = {(eps*(1-1/33))**2:.6f} vs NuFIT 0.0222")
