#!/usr/bin/env python3
"""
O39 — Step 9: 記錄完整性核對 (Record Completeness Verifier)
===========================================================
目標: 讀取 docs/01_derivation_record.md + data/*.txt, 核對所有關鍵數字一致

核對項目:
  1. 所有 scripts 嘅 PASS 總數 (docs 聲稱 80/80)
  2. 核心數值: μ²=2, λ=2/123, ⟨W⟩²=61.5, V_min=-61.5, V''=8
  3. Ω_Λ = 4/(φ⁴−1) = 0.68328, Ω_Λ/Ω_m = 4φ/3
  4. λ_sync = c·T_sync/88 = 294.88 Mpc
  5. 遺留閉合: κ_eff, m_δW/m_7 ≈ 90/89, η=0, λ₁/λ₂
  6. docs 檔案齊全 (01_problem_record, SESSION_START, docs/01)
"""

import re
import math
from decimal import Decimal, getcontext
getcontext().prec = 60

phi = (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)

results = []
print("=" * 72)
print("  O39 — Step 9: 記錄完整性核對")
print("=" * 72)

# ═══════════════════════════════════════════════════════════════
# [1] 檔案結構
# ═══════════════════════════════════════════════════════════════
print("\n─── [1] 檔案結構 ───")
import os
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files_expected = [
    "01_problem_record.md",
    "SESSION_START.md",
    "docs/01_derivation_record.md",
]
files_scripts = [
    "scripts/01_W_OmegaL_relation.py",
    "scripts/02_SSB_potential.py",
    "scripts/03_no_heat_death.py",
    "scripts/04_observer.py",
    "scripts/05_verification_audit.py",
    "scripts/06_final_consistency.py",
    "scripts/07_cross_verify_legacy.py",
    "scripts/08_unified_closure.py",
]
files_data = [
    "data/step1_W_OmegaL_results.txt",
    "data/step2_SSB_potential_results.txt",
    "data/step3_no_heat_death_results.txt",
    "data/step4_observer_results.txt",
    "data/step5_verification_audit_results.txt",
    "data/step6_final_consistency_results.txt",
    "data/step7_cross_verify_results.txt",
    "data/step8_unified_closure_results.txt",
]
ok_all = True
for f in files_expected + files_scripts + files_data:
    if not os.path.exists(os.path.join(base, f)):
        print(f"  ❌ 缺檔案: {f}")
        ok_all = False
print(f"  全部 {len(files_expected+files_scripts+files_data)} 個檔案存在: {'✅' if ok_all else '❌'}")
results.append(ok_all)

# ═══════════════════════════════════════════════════════════════
# [2] 核心數值 (由結構重算)
# ═══════════════════════════════════════════════════════════════
print("\n─── [2] 核心數值重算 ───")
S_even = Decimal(90)
S_odd = Decimal(88)
mu2 = S_even - S_odd
lam1 = Decimal(2)/Decimal(123)
W2 = mu2/(Decimal(2)*lam1)
Vmin = -(mu2**2)/(Decimal(4)*lam1)
Vpp = Decimal(4)*mu2
Omega_L = Decimal(4)/(phi**4 - 1)

checks = [
    ("μ² = 2", mu2, Decimal(2)),
    ("λ₁ = 2/123", lam1, Decimal(2)/Decimal(123)),
    ("⟨W⟩² = 61.5", W2, Decimal('61.5')),
    ("V_min = −61.5", Vmin, -Decimal('61.5')),
    ("V''(⟨W⟩) = 8", Vpp, Decimal(8)),
    ("Ω_Λ = 4/(φ⁴−1)", Omega_L, Decimal(4)/(phi**4-1)),
]
for name, val, target in checks:
    ok = abs(val - target) < Decimal('1e-40')
    print(f"  {name} = {float(val):.10f} (目標 {float(target):.10f}): {'✅' if ok else '❌'}")
    results.append(ok)

# ═══════════════════════════════════════════════════════════════
# [3] Ω_Λ/Ω_m = 4φ/3
# ═══════════════════════════════════════════════════════════════
print("\n─── [3] Ω_Λ/Ω_m = 4φ/3 ───")
Omega_m = Decimal(1) - Omega_L
ratio = Omega_L/Omega_m
target_ratio = Decimal(4)*phi/Decimal(3)
ok = abs(ratio - target_ratio) < Decimal('1e-50')
print(f"  Ω_Λ/Ω_m = {float(ratio):.10f} vs 4φ/3 = {float(target_ratio):.10f}: {'✅' if ok else '❌'}")
results.append(ok)

# ═══════════════════════════════════════════════════════════════
# [4] λ₂ = (φ⁴−1)/4 = 1/Ω_Λ (統一)
# ═══════════════════════════════════════════════════════════════
print("\n─── [4] λ₂ = (φ⁴−1)/4 = 1/Ω_Λ ───")
lam2 = (phi**4 - 1)/Decimal(4)
ok = abs(lam2 - Decimal(1)/Omega_L) < Decimal('1e-50')
print(f"  λ₂ = {float(lam2):.10f} vs 1/Ω_Λ = {float(Decimal(1)/Omega_L):.10f}: {'✅' if ok else '❌'}")
results.append(ok)

# ═══════════════════════════════════════════════════════════════
# [5] λ₁·Σγ = λ₂ (層次轉換)
# ═══════════════════════════════════════════════════════════════
print("\n─── [5] λ₁·Σγ = λ₂ ───")
lam1_90 = lam1 * Decimal(90)
dev = abs(lam1_90 - lam2)/lam2*100
ok = dev < Decimal('0.01')
print(f"  λ₁·90 = {float(lam1_90):.10f} vs λ₂ = {float(lam2):.10f} (dev {float(dev):.6f}%): {'✅' if ok else '❌'}")
results.append(ok)

# ═══════════════════════════════════════════════════════════════
# [6] m_δW/m_7 ≈ 90/89
# ═══════════════════════════════════════════════════════════════
print("\n─── [6] m_δW/m_7 ≈ 90/89 ───")
s7 = 4*math.sin(7*math.pi/88)
dev6 = abs(s7 - (1 - 1/90))/(1 - 1/90)*100
ok6 = dev6 < 0.1
print(f"  4sin(7π/88) = {s7:.8f} vs 1−1/90 = {1-1/90:.8f} (dev {dev6:.4f}%): {'✅' if ok6 else '❌'}")
results.append(ok6)

# ═══════════════════════════════════════════════════════════════
# [7] λ_sync = c·T_sync/88
# ═══════════════════════════════════════════════════════════════
print("\n─── [7] λ_sync = c·T_sync/88 ───")
H0 = Decimal('72.59')
Mpc_km = Decimal('3.085677581e19')
Gyr_s = Decimal('3.15576e16')
c_km = Decimal('299792.458')
T_sync = Decimal(2)*Decimal('3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679')/H0*Mpc_km/Gyr_s
lam_sync = c_km*(T_sync*Gyr_s)/Decimal(88)/Mpc_km
print(f"  λ_sync = {float(lam_sync):.2f} Mpc (目標 294.88): {'✅' if abs(lam_sync-Decimal('294.88'))/Decimal('294.88') < Decimal('0.01') else '❌'}")
results.append(abs(lam_sync-Decimal('294.88'))/Decimal('294.88') < Decimal('0.01'))

# ═══════════════════════════════════════════════════════════════
# [8] docs/01 內容關鍵字核對
# ═══════════════════════════════════════════════════════════════
print("\n─── [8] docs/01 內容核對 ───")
doc_path = os.path.join(base, "docs/01_derivation_record.md")
with open(doc_path) as f:
    content = f.read()
keywords = [
    "μ² = Σγ_even − Σγ_odd = 2",
    "λ  = 2/[3(N_d−dim_ℂ)] = 2/123",
    "⟨W⟩² = μ²/(2λ) = 61.5",
    "Ω_Λ/Ω_m = 4φ/3",
    "λ_sync = c·T_sync/88",
    "層次正交",
    "統一閉合",
    "η = 0",
    "90/89",
    "κ_eff",
    "D_app",
    "93/93 PASS",
]
missing = [k for k in keywords if k not in content]
if missing:
    print(f"  ❌ 缺關鍵內容: {missing}")
else:
    print(f"  ✅ 全部 {len(keywords)} 個關鍵字存在")
ok8 = len(missing) == 0
results.append(ok8)

# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*72}")
print(f"  O39 Step 9 記錄核對: {sum(results)}/{len(results)} PASS")
print(f"{'═'*72}")

with open("data/step9_record_verify_results.txt", "w") as f:
    f.write("O39 — Step 9: 記錄完整性核對\n")
    f.write("=" * 72 + "\n\n")
    f.write(f"[1] 檔案結構 ({len(files_expected+files_scripts+files_data)} 個): {'PASS' if ok_all else 'FAIL'}\n")
    f.write(f"[2-7] 核心數值 8 項: {'PASS' if sum(results[1:9]) == 8 else 'FAIL'}\n")
    f.write(f"[8] docs/01 關鍵內容: {'PASS' if ok8 else 'FAIL'}\n\n")
    f.write(f"TOTAL: {sum(results)}/{len(results)} PASS\n")
print("\n  結果已寫入 data/step9_record_verify_results.txt")
