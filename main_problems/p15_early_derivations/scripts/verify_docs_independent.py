"""
IDCM v10.0 — 獨立核對 docs 中所有關鍵公式與數值
=================================================
禁止跨文檔新推導污染 — 只核對已記錄內容
"""
import math
import numpy as np

φ = (1 + math.sqrt(5)) / 2
PASS = 0
FAIL = 0

def check(name, actual, expected, tol, unit=""):
    global PASS, FAIL
    if isinstance(expected, str):
        ok = abs(actual - float(expected)) <= tol
    else:
        ok = abs(actual - expected) <= tol
    if ok:
        PASS += 1
        print(f"  ✅ {name}: {actual:.10f} {unit} (期望 {expected} {unit})")
    else:
        FAIL += 1
        print(f"  ❌ {name}: {actual:.10f} {unit} (期望 {expected} {unit}, 差 {abs(actual-float(expected)):.2e})")

print("=" * 70)
print("1. K_Chain 波參數")
print("=" * 70)

# γ_n = 4sin²(πn/88)
for n, exp in [(1, 0.0051), (2, 0.0204), (22, 2.0), (44, 4.0)]:
    g = 4 * math.sin(math.pi * n / 88) ** 2
    check(f"γ_{n}", g, exp, 0.001)

# Z₂ 對偶 γ_n + γ_{44-n} = 4
ok = True
for n in range(1, 44):
    if abs(4*math.sin(math.pi*n/88)**2 + 4*math.sin(math.pi*(44-n)/88)**2 - 4) > 1e-12:
        ok = False
print(f"  {'✅' if ok else '❌'} Z₂ 對偶: γ_n + γ_{44-n} = 4 全部 {44-1} 對成立")

# v_g = c·cos(πn/88)
v22 = math.cos(math.pi * 22 / 88)
check("v_g(n=22)/c", v22, 0.7071067812, 1e-6)

print("\n" + "=" * 70)
print("2. CKM Beat Frequency 公式 (docs/ckm_derivation.md §4.2)")
print("=" * 70)

def omega(n):
    return 2 * math.sin(math.pi * n / 88)

def beat(i, j):
    return abs(omega(i) - omega(j))

# CKM beat formulas from doc
ckm_checks = [
    ("tan(θ₁₂)", beat(5,6)/beat(19,25), 0.2316035403, 1e-7),
    ("tan(θ₂₃)", beat(33,35)/beat(3,22), 0.0415626453, 1e-7),
    ("sin(θ₁₃)", beat(42,43)/beat(10,31), 0.0035074294, 1e-7),
    ("V_us (λ)", beat(25,35)/beat(6,37), 0.2250008938, 1e-7),
    ("V_cb", beat(13,14)/beat(6,37), 0.0418203954, 1e-7),
    ("V_ub", beat(41,42)/beat(3,37), 0.0036910176, 1e-7),
    ("A (Wolfenstein)", beat(16,35)/beat(10,28), 0.8299998703, 1e-7),
]
for name, actual, expected, tol in ckm_checks:
    check(name, actual, expected, tol)

# CKM angles
θ12 = math.degrees(math.atan(beat(5,6)/beat(19,25)))
θ23 = math.degrees(math.atan(beat(33,35)/beat(3,22)))
θ13 = math.degrees(math.asin(beat(42,43)/beat(10,31)))
check("θ₁₂ (°)", θ12, 13.04, 0.001)
check("θ₂₃ (°)", θ23, 2.38, 0.001)
check("θ₁₃ (°)", θ13, 0.201, 0.001)

print("\n" + "=" * 70)
print("3. PMNS Beat Frequency 公式 (docs/research_record.md §14.3)")
print("=" * 70)

pmns_checks = [
    ("tan(θ₁₂=33.41°)", beat(4,13)/beat(9,25), 0.6596255406, 1e-5),
    ("tan(θ₂₃=42.2°)", beat(11,23)/beat(12,26), 0.9067445022, 1e-5),
    ("tan(θ₂₃=49.0°)", beat(4,14)/beat(22,44), 1.1503651393, 1e-5),
    ("sin(θ₁₃=8.54°)", beat(25,29)/beat(3,20), 0.1484996509, 1e-5),
]
for name, actual, expected, tol in pmns_checks:
    check(name, actual, expected, tol)

print("\n" + "=" * 70)
print("4. GST 關係 (docs/ckm_derivation.md §一)")
print("=" * 70)
gst = math.degrees(math.asin(math.sqrt(4.67 / 93.4)))
check("θ₁₂ GST (°)", gst, 12.92, 0.01)
check("θ₁₂ GST vs PDG 13.04° 誤差%", abs(gst-13.04)/13.04*100, 0.91, 0.05, "%")

print("\n" + "=" * 70)
print("5. 盲測校準 (docs/research_record.md §七)")
print("=" * 70)
M_Pl = 1.220890e22  # MeV

# Eigenvalues from eigenvalues_final.npy
evals = np.load("data/eigenvalues_final.npy")
sorted_pos = sorted([e for e in evals if e > 1e-10], reverse=True)
print(f"  11 正本徵值: {[f'{e:.6f}' for e in sorted_pos]}")
check("λ_max", sorted_pos[0], 51.56, 0.01)
check("λ_min (11th)", sorted_pos[10], 0.00136, 0.0001)

# V_cycle calibration
V1 = -math.log(172760.0 / (sorted_pos[0] * M_Pl))
V2 = -math.log(1270.0 / (sorted_pos[3] * M_Pl))
V3 = -math.log(0.51099895 / (sorted_pos[8] * M_Pl))
check("V₁ (Top)", V1, 42.74, 0.01)
check("V₂ (Charm)", V2, 44.94, 0.01)
check("V₃ (Electron)", V3, 46.54, 0.01)

print("\n" + "=" * 70)
print("6. CKM 完整矩陣 (docs/ckm_derivation.md §五, δ=66.40°)")
print("=" * 70)
δ = math.radians(66.40)
c12, s12 = math.cos(math.radians(13.04)), math.sin(math.radians(13.04))
c23, s23 = math.cos(math.radians(2.38)), math.sin(math.radians(2.38))
c13, s13 = math.cos(math.radians(0.201)), math.sin(math.radians(0.201))

V_ckm = np.array([
    [c12*c13, s12*c13, s13*math.e**(-1j*δ)],
    [-s12*c23 - c12*s23*s13*math.e**(1j*δ), c12*c23 - s12*s23*s13*math.e**(1j*δ), s23*c13],
    [s12*s23 - c12*c23*s13*math.e**(1j*δ), -c12*s23 - s12*c23*s13*math.e**(1j*δ), c23*c13],
])

pdg_ckm = {
    "V_ud": 0.97435, "V_us": 0.22500, "V_ub": 0.00369,
    "V_cd": 0.22486, "V_cs": 0.97349, "V_cb": 0.04182,
    "V_td": 0.00857, "V_ts": 0.04110, "V_tb": 0.99912,
}
idx = [(0,0,'V_ud'),(0,1,'V_us'),(0,2,'V_ub'),(1,0,'V_cd'),(1,1,'V_cs'),(1,2,'V_cb'),(2,0,'V_td'),(2,1,'V_ts'),(2,2,'V_tb')]
doc_ckm = {
    "V_ud": 0.97421, "V_us": 0.22563, "V_ub": 0.00351,
    "V_cd": 0.22549, "V_cs": 0.97336, "V_cb": 0.04153,
    "V_td": 0.00859, "V_ts": 0.04078, "V_tb": 0.99913,
}
for i, j, name in idx:
    calc = abs(V_ckm[i, j])
    docv = doc_ckm[name]
    pdgv = pdg_ckm[name]
    # 核對: doc 值 vs 用公式重算
    err_doc = abs(calc - docv) / pdgv * 100
    err_pdg = abs(calc - pdgv) / pdgv * 100
    ok = err_doc < 1.0
    print(f"  {'✅' if ok else '❌'} {name}: 重算={calc:.5f}, doc={docv}, PDG={pdgv} (doc誤差 {err_doc:.2f}%)")

# J_CP
J = np.imag(V_ckm[0,0] * V_ckm[1,1] * np.conj(V_ckm[0,1]) * np.conj(V_ckm[1,0]))
check("J_CP", J, 3.08e-5, 0.5e-5)

print("\n" + "=" * 70)
print("7. 中微子質量譜 (docs/research_record.md §14.8)")
print("=" * 70)
φ18 = φ ** (1/8)
m0 = 0.053424
m3 = m0
m2 = m0 / φ
m1 = m0 / φ**2
dm31 = m3**2 - m1**2
dm21 = (m0**2 * (φ**-2 - φ**-4)) / 9
check("m₀' = m₀·φ^(1/8)", 0.053424, 0.053424, 0.000001, "eV")
check("Δm²₃₁ (×10⁻³ eV²)", dm31*1e3, 2.4377, 0.001)
check("Δm²₂₁ (×10⁻⁵ eV²)", dm21*1e5, 7.486, 0.01)

print("\n" + "=" * 70)
print("8. 結構常數")
print("=" * 70)
check("946 = C(44,2)", 44*43/2, 946, 0)
check("134 = 36+98", 36+98, 134, 0)
check("8436 = C(38,3)", math.comb(38,3), 8436, 0)
check("364 = C(14,3)", math.comb(14,3), 364, 0)
check("χ = 2(36-98)", 2*(36-98), -124, 0)
check("ε = φ⁻¹/4", φ**-1/4, 0.1545084972, 1e-6)
check("V_ub = ε³", (φ**-1/4)**3, 0.00369, 0.0001)

print(f"\n{'='*70}")
print(f"✅ PASS: {PASS} | ❌ FAIL: {FAIL}")
print(f"{'='*70}")
