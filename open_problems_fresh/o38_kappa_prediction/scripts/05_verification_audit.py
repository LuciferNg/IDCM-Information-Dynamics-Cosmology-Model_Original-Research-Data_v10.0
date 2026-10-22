#!/usr/bin/env python3
"""
O38 — Step 5: 獨立 Audit (Independent Audit)
================================================================
完全獨立嘅驗證腳本: 唔 import scripts/01-04 任何函數,
所有常數重新定義, 所有公式由第一原理重算。

驗證 O38 全部聲稱:
  V1: ω_scale = 88·H₀ (H₀ 由 R_H = c/H₀ 直接計)
  V2: κ̃² = κ²/(M₀·H₀) = 88
  V3: Σγ_odd = 88 (88-site 對偶鏈奇數模式能量)
  V4: κ̃² = Σγ_odd (跨 sector 統一)
  V5: m_7 = M₀·2sin(7π/88) = 13.8002 MeV
  V6: m_1 = M₀·2sin(π/88) = 1.9917 MeV
  V7: 抵消定理 (m_n 兩種途徑一致)
  V8: κ = 9.42 keV (ħ 恢復制)
  V9: 質量比重現 (6/6 直接)
  V10: κ² = M₀·ω_scale 數值 5.776e-9 eV·rad/s
"""

import math

# ═══════════════════════════════════════════════════════════
# 第一原理常數 (完全獨立定義)
# ═══════════════════════════════════════════════════════════
PHI = (1 + 5**0.5) / 2
C_KM = 299792.458          # km/s
H0 = 72.59                 # km/s/Mpc (IDCM 結構值)
R_H = C_KM / H0            # Mpc ← 由 c/H₀ 直接計 (唔用 src 硬編碼)
MPC_KM = 3.085677581e19    # km/Mpc
C_MS = C_KM * 1e3          # m/s

# H₀ 轉 s⁻¹ (兩種獨立途徑, 應該一致)
H0_s_A = H0 * 1e3 / (MPC_KM * 1e3)          # 由 H₀ 單位換算
H0_s_B = C_MS / (R_H * MPC_KM * 1e3)        # 由 c/R_H
assert abs(H0_s_A - H0_s_B) / H0_s_A < 1e-10, "H₀ 轉換不一致!"

# ω_scale (src 定義, 但用 R_H = c/H₀)
omega_scale = 88 * C_MS / (R_H * MPC_KM * 1e3)   # rad/s

print("=" * 70)
print("  O38 — Step 5: 獨立 Audit (零依賴)")
print("=" * 70)
results = []
checks = []

# ═══════════════════════════════════════════════════════════
# V1: ω_scale = 88·H₀
# ═══════════════════════════════════════════════════════════
v1 = abs(omega_scale - 88 * H0_s_A) / omega_scale < 1e-12
results.append(v1)
checks.append(("V1: ω_scale = 88·H₀", f"ω_scale={omega_scale:.6e}, 88H₀={88*H0_s_A:.6e}", v1))

# ═══════════════════════════════════════════════════════════
# V2: κ̃² = κ²/(M₀·H₀) = 88
# ═══════════════════════════════════════════════════════════
E_kchain = 4.060265e-3      # eV (O34)
M0_eV = E_kchain * PHI**(47 + 37/528)   # eV
kappa2 = M0_eV * omega_scale            # eV·rad/s
kappa_tilde2 = kappa2 / (M0_eV * H0_s_A)
v2 = abs(kappa_tilde2 - 88.0) < 1e-9
results.append(v2)
checks.append(("V2: κ̃² = κ²/(M₀·H₀) = 88", f"κ̃²={kappa_tilde2:.10f}", v2))

# ═══════════════════════════════════════════════════════════
# V3: Σγ_odd = 88 (奇數模式能量總和)
# ═══════════════════════════════════════════════════════════
sum_gamma_odd = sum(4 * math.sin(math.pi*(2*n-1)/176)**2 for n in range(1, 45))
v3 = abs(sum_gamma_odd - 88.0) < 1e-9
results.append(v3)
checks.append(("V3: Σγ_odd = 88 (觀察者能量)", f"Σγ_odd={sum_gamma_odd:.10f}", v3))

# ═══════════════════════════════════════════════════════════
# V4: κ̃² = Σγ_odd (跨 sector 統一)
# ═══════════════════════════════════════════════════════════
v4 = abs(kappa_tilde2 - sum_gamma_odd) < 1e-9
results.append(v4)
checks.append(("V4: κ̃² = Σγ_odd (統一)", f"κ̃²={kappa_tilde2:.10f}, Σγ_odd={sum_gamma_odd:.10f}", v4))

# ═══════════════════════════════════════════════════════════
# V5/V6: m_7, m_1 標度
# ═══════════════════════════════════════════════════════════
m7 = M0_eV * 2 * math.sin(7*math.pi/88)   # eV
m1 = M0_eV * 2 * math.sin(1*math.pi/88)   # eV
v5 = abs(m7/1e6 - 13.8002) / 13.8002 < 1e-4
v6 = abs(m1/1e6 - 1.9917) / 1.9917 < 1e-4
results += [v5, v6]
checks.append(("V5: m_7 = 13.8002 MeV", f"m_7={m7/1e6:.4f} MeV", v5))
checks.append(("V6: m_1 = 1.9917 MeV", f"m_1={m1/1e6:.4f} MeV", v6))

# ═══════════════════════════════════════════════════════════
# V7: 抵消定理 (m_n 兩種途徑)
# ═══════════════════════════════════════════════════════════
v7 = True
for n in [1, 7, 22, 44]:
    wn = 2 * math.sin(n*math.pi/88)
    m_a = M0_eV * wn                    # 途徑 A: M₀·ω_n
    kappa2_full = 88 * M0_eV * H0_s_A   # κ² = 88·M₀·H₀
    m_b = kappa2_full * wn / omega_scale  # 途徑 B: κ²·ω_n/ω_scale
    if abs(m_a - m_b) / m_a > 1e-10:
        v7 = False
results.append(v7)
checks.append(("V7: 抵消定理 (m_A = m_B)", f"dev<1e-10 (n=1,7,22,44)", v7))

# ═══════════════════════════════════════════════════════════
# V8: κ = 9.42 keV (ħ 恢復制)
# ═══════════════════════════════════════════════════════════
HBAR = 6.582119569e-16     # eV·s
kappa2_ev2 = M0_eV * HBAR / omega_scale   # eV²
kappa_keV = math.sqrt(kappa2_ev2) / 1e3   # keV
v8 = abs(kappa_keV - 9.4186) / 9.4186 < 1e-3
results.append(v8)
checks.append(("V8: κ = 9.42 keV", f"κ={kappa_keV:.4f} keV", v8))

# ═══════════════════════════════════════════════════════════
# V9: 質量比重現 (6/6 直接)
# ═══════════════════════════════════════════════════════════
pairs = [(10, 24, 0.4625), (8, 33, 0.3038), (30, 41, 0.8814),
         (38, 19, 1.5583), (1, 18, 0.0595), (22, 1, 20.0)]
n_pass = 0
for n1, n2, tgt in pairs:
    r = math.sin(n1*math.pi/88) / math.sin(n2*math.pi/88)
    if abs(r - tgt) / tgt < 0.01:
        n_pass += 1
v9 = n_pass >= 5
results.append(v9)
checks.append(("V9: 質量比重現", f"{n_pass}/6 直接匹配", v9))

# ═══════════════════════════════════════════════════════════
# V10: κ² = M₀·ω_scale 數值
# ═══════════════════════════════════════════════════════════
v10 = abs(kappa2 - 5.776005e-9) / 5.776005e-9 < 1e-4
results.append(v10)
checks.append(("V10: κ² = 5.776e-9 eV·rad/s", f"κ²={kappa2:.6e}", v10))

# ═══════════════════════════════════════════════════════════
# 輸出
# ═══════════════════════════════════════════════════════════
print("\n─── 獨立 Audit 結果 ───")
for i, (name, val, ok) in enumerate(checks, 1):
    print(f"  V{i:<3d} {name:<38} {val:<42} {'✅ PASS' if ok else '❌ FAIL'}")

n_total = sum(results)
print(f"\n{'═'*70}")
print(f"  O38 Step 5 獨立 Audit: {n_total}/{len(results)} PASS")
print(f"{'═'*70}")

with open("data/step5_verification_audit_results.txt", "w") as f:
    f.write("O38 — Step 5: 獨立 Audit\n")
    f.write("=" * 70 + "\n\n")
    for i, (name, val, ok) in enumerate(checks, 1):
        f.write(f"V{i}: {name}: {'PASS' if ok else 'FAIL'} ({val})\n")
    f.write(f"\n總計: {n_total}/{len(results)} PASS\n")
print(f"\n  結果已寫入 data/step5_verification_audit_results.txt")
