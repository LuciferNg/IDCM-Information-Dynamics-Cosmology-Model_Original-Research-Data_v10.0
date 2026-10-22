#!/usr/bin/env python3
"""
O35 — 獨立核對 (verification_audit)
=====================================
用 Decimal 高精度 + 獨立推導驗證 O35 所有關鍵數值,
唔係重跑 scripts, 而係從頭獨立計算。

核對清單:
  [1] 和差化積恆等式 (隨機 5 對 n,m, Decimal 50 位)
  [2] m_t/m_b O34 閉合公式 (φ^(8+71/132) × sin(19π/88)/sin(33π/88))
  [3] sin 比值結構 (倒數/鏈式/週期)
  [4] Σγ_odd = 88, Σγ_even = 90 (半整數分解)
  [5] Koide Q (輕子質量)
  [6] tan/cos 恆等式 sin(A)/sin(B) = tan(A)/tan(B) × cos(A)/cos(B)
  [7] m_u/m_d, m_s/m_d 現狀 (確認 O34 🟡 未閉合, O35 任務)
  [8] 審計發現: 搜索 fit 嘅 k 值結構性 (確認 overfit 風險)
"""

from decimal import Decimal, getcontext
import math

getcontext().prec = 60

# 高精度 π
PI = Decimal('3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679')
PHI = (Decimal(1) + PI.sqrt() if False else (Decimal(1) + (Decimal(5).sqrt())) / Decimal(2))
# 修正: PHI = (1+√5)/2
PHI = (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)

def dsin(x):
    """Decimal sin (Taylor 展開, 60 位)"""
    x = x % (2 * PI)
    term = x
    result = Decimal(0)
    n = 1
    while abs(term) > Decimal('1e-50'):
        result += term
        term *= -x * x / ((2*n) * (2*n+1))
        n += 1
    return result

def dcos(x):
    return dsin(x + PI/2)

def dtan(x):
    return dsin(x) / dcos(x)

def dsin_pi_n_over_88(n):
    """sin(nπ/88)"""
    return dsin(Decimal(n) * PI / Decimal(88))

def dcos_pi_n_over_176(n):
    """cos(nπ/176)"""
    return dcos(Decimal(n) * PI / Decimal(176))

print("=" * 67)
print("  O35 — 獨立核對 (Decimal 60 位)")
print("=" * 67)
results = []

# ═══════════════════════════════════════════════════════════════
# [1] 和差化積恆等式 (獨立 Decimal 驗證)
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [1] 和差化積: ω_n − ω_m = 4cos((n+m)π/176)·sin((n−m)π/176) ───")
pairs = [(8, 1), (19, 33), (18, 37), (1, 2), (7, 27)]
max_dev1 = Decimal(0)
for n, m in pairs:
    lhs = Decimal(2)*dsin_pi_n_over_88(n) - Decimal(2)*dsin_pi_n_over_88(m)
    rhs = Decimal(4)*dcos_pi_n_over_176(n+m)*dsin(Decimal(n-m)*PI/Decimal(176))
    dev = abs(lhs - rhs)
    max_dev1 = max(max_dev1, dev)
    print(f"  ({n},{m}): LHS={lhs:.20f} RHS={rhs:.20f} dev={dev:.2e}")
PASS1 = max_dev1 < Decimal('1e-30')
print(f"  [1] {'✅ PASS' if PASS1 else '❌ FAIL'} (max dev {max_dev1:.2e})")
results.append(PASS1)

# ═══════════════════════════════════════════════════════════════
# [2] m_t/m_b O34 閉合公式
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [2] m_t/m_b = φ^(8+71/132) × sin(19π/88)/sin(33π/88) ───")
k_t = Decimal(8) + Decimal(71)/Decimal(132)
phi_k = PHI ** k_t
sin19 = dsin_pi_n_over_88(19)
sin33 = dsin_pi_n_over_88(33)
r_tb = phi_k * sin19 / sin33
target_tb = Decimal('172.76e3') / Decimal('4.18e3')
dev_tb = abs(r_tb - target_tb) / target_tb * 100
print(f"  φ^(8+71/132) = {phi_k:.10f}")
print(f"  sin(19π/88)/sin(33π/88) = {sin19/sin33:.10f}")
print(f"  m_t/m_b = {r_tb:.10f}")
print(f"  目標 = {target_tb:.10f} (172.76/4.18 GeV)")
print(f"  dev = {dev_tb:.6f}%")
PASS2 = dev_tb < Decimal('0.01')
print(f"  [2] {'✅ PASS' if PASS2 else '❌ FAIL'} (O34 聲稱 0.0049%)")
results.append(PASS2)

# ═══════════════════════════════════════════════════════════════
# [3] sin 比值結構 (倒數/鏈式/週期)
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [3] sin 比值結構 ───")
# 倒數: sinr(n1,n2) = 1/sinr(n2,n1)
dev_recip = abs((dsin_pi_n_over_88(1)/dsin_pi_n_over_88(2)) - Decimal(1)/(dsin_pi_n_over_88(2)/dsin_pi_n_over_88(1)))
print(f"  倒數對稱 sin(1,2)·sin(2,1) = 1: dev = {dev_recip:.2e}")
# 鏈式: sinr(1,2)·sinr(2,3) = sinr(1,3)
chain = (dsin_pi_n_over_88(1)/dsin_pi_n_over_88(2)) * (dsin_pi_n_over_88(2)/dsin_pi_n_over_88(3))
direct = dsin_pi_n_over_88(1)/dsin_pi_n_over_88(3)
print(f"  鏈式 sin(1,2)·sin(2,3) vs sin(1,3): dev = {abs(chain-direct):.2e}")
# 週期 88
per = abs((dsin_pi_n_over_88(1+88)/dsin_pi_n_over_88(2+88)) - (dsin_pi_n_over_88(1)/dsin_pi_n_over_88(2)))
print(f"  週期 88: dev = {per:.2e}")
PASS3 = dev_recip < Decimal('1e-30') and abs(chain-direct) < Decimal('1e-30')
print(f"  [3] {'✅ PASS' if PASS3 else '❌ FAIL'}")
results.append(PASS3)

# ═══════════════════════════════════════════════════════════════
# [4] Σγ_odd = 88, Σγ_even = 90
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [4] 半整數分解能量 ───")
# γ_k = 4sin²(πk/176), k=1..88
# odd k: Σ 4sin²(π(2n-1)/176) for n=1..44 → 88?
# even k: Σ 4sin²(π(2n)/176) for n=1..44 → 90?
# 用恆等式 Σsin² = N/2 - sin(2Nθ)/(4sinθ)... 直接數值
sum_odd = Decimal(0)
sum_even = Decimal(0)
for n in range(1, 45):
    g_odd = Decimal(4) * dsin(Decimal(2*n-1)*PI/Decimal(176))**2
    g_even = Decimal(4) * dsin(Decimal(2*n)*PI/Decimal(176))**2
    sum_odd += g_odd
    sum_even += g_even
print(f"  Σγ_odd = {sum_odd:.10f} (目標 88)")
print(f"  Σγ_even = {sum_even:.10f} (目標 90)")
PASS4 = abs(sum_odd - 88) < Decimal('1e-25') and abs(sum_even - 90) < Decimal('1e-25')
print(f"  [4] {'✅ PASS' if PASS4 else '❌ FAIL'}")
results.append(PASS4)

# ═══════════════════════════════════════════════════════════════
# [5] Koide Q (輕子)
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [5] Koide Q = 2/3 ───")
m_e, m_mu, m_tau = Decimal('0.511'), Decimal('105.658'), Decimal('1776.93')
Q = (m_e + m_mu + m_tau) / (m_e.sqrt() + m_mu.sqrt() + m_tau.sqrt())**2
print(f"  Q = {Q:.10f} vs 2/3 = {Decimal(2)/Decimal(3):.10f}")
PASS5 = abs(Q - Decimal(2)/Decimal(3)) < Decimal('0.001')
print(f"  [5] {'✅ PASS' if PASS5 else '❌ FAIL'}")
results.append(PASS5)

# ═══════════════════════════════════════════════════════════════
# [6] tan/cos 恆等式
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [6] sin(A)/sin(B) = tan(A)/tan(B) × cos(A)/cos(B) ───")
max_dev6 = Decimal(0)
for n, m in pairs:
    lhs = dsin_pi_n_over_88(n) / dsin_pi_n_over_88(m)
    rhs = (dtan(Decimal(n)*PI/Decimal(88)) / dtan(Decimal(m)*PI/Decimal(88))) * \
          (dcos(Decimal(n)*PI/Decimal(88)) / dcos(Decimal(m)*PI/Decimal(88)))
    dev = abs(lhs - rhs)
    max_dev6 = max(max_dev6, dev)
print(f"  max dev = {max_dev6:.2e}")
PASS6 = max_dev6 < Decimal('1e-30')
print(f"  [6] {'✅ PASS' if PASS6 else '❌ FAIL'}")
results.append(PASS6)

# ═══════════════════════════════════════════════════════════════
# [7] m_u/m_d, m_s/m_d 現狀 (O34 🟢 / O35 任務)
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [7] m_u/m_d, m_s/m_d 現狀 ───")
r_ud_target = Decimal('2.16')/Decimal('4.67')
r_ud_sin = dsin_pi_n_over_88(10)/dsin_pi_n_over_88(24)  # O34 正確配對 (10,24)!
dev_ud = abs(r_ud_sin - r_ud_target)/r_ud_target*100
print(f"  m_u/m_d 目標 = {r_ud_target:.6f}")
print(f"  sin(10,24) = {r_ud_sin:.6f}  ← O34 正確配對")
print(f"  dev = {dev_ud:.4f}% → O34 🟢 已閉合 (0.026%)")
# 對比錯誤配對 (1,2)
r_ud_wrong = dsin_pi_n_over_88(1)/dsin_pi_n_over_88(2)
dev_ud_wrong = abs(r_ud_wrong - r_ud_target)/r_ud_target*100
print(f"  ⚠️ 錯誤配對 sin(1,2) = {r_ud_wrong:.6f} → dev {dev_ud_wrong:.4f}% (陷阱!)")

r_sd_target = Decimal('93.4')/Decimal('4.67')
r_sd_sin = dsin_pi_n_over_88(22)/dsin_pi_n_over_88(1)
dev_sd = abs(r_sd_sin - r_sd_target)/r_sd_target*100
print(f"  m_s/m_d 目標 = {r_sd_target:.6f} (= 20)")
print(f"  sin(22,1) = {r_sd_sin:.6f}")
print(f"  dev = {dev_sd:.4f}% → O34 🟡 唯一未閉合, O35 任務")
k_sd = (r_sd_target / r_sd_sin).ln() / PHI.ln()
print(f"  k = log_φ(20/19.81) = {k_sd:.6f}")
print(f"  10/528 = {Decimal(10)/Decimal(528):.6f} (dev {abs(k_sd - Decimal(10)/Decimal(528)):.6f})")
PASS7 = abs(dev_ud - Decimal('0.026')) < Decimal('0.01')  # m_u/m_d 0.026% 已閉合
print(f"  [7] 現狀確認: {'✅ PASS' if PASS7 else '❌ FAIL'} (m_u/m_d 0.026% 已閉合, m_s/m_d 0.94% 🟡)")
results.append(PASS7)

# ═══════════════════════════════════════════════════════════════
# [8] 審計: 搜索 fit 嘅 k 結構性
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [8] 搜索 fit 嘅 k 結構性 (overfit 風險確認) ───")
# m_t/m_b 審計 fit: sin(25,13)×φ^(79/12)
r_sin_25_13 = dsin_pi_n_over_88(25)/dsin_pi_n_over_88(13)
r_pred_audit = r_sin_25_13 * PHI**(Decimal(79)/Decimal(12))
dev_audit = abs(r_pred_audit - target_tb)/target_tb*100
print(f"  審計 fit: sin(25,13)×φ^(79/12) = {r_pred_audit:.6f}")
print(f"  目標 m_t/m_b = {target_tb:.6f}")
print(f"  dev = {dev_audit:.4f}% (比 O34 0.0049% 更準!)")
print(f"  但 (25,13) 冇結構意義: 25≠Lucas/Fibonacci, 13=F₇?")
print(f"  → overfit 風險確認: 搜索 fit 唔可以取代結構閉合 ✅")
PASS8 = dev_audit < Decimal('0.001')  # 確認 fit 更準 (0.0002%)
print(f"  [8] {'✅ PASS (overfit 風險確認)' if PASS8 else '❌ FAIL'}")
results.append(PASS8)

# ═══════════════════════════════════════════════════════════════
# 總結
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print(f"  獨立核對結果: {sum(results)}/{len(results)} PASS")
print(f"{'═'*67}")

with open("data/verification_audit_results.txt", "w") as f:
    f.write("O35 — 獨立核對 (Decimal 60 位)\n")
    f.write("日期: 2026-08-19\n\n")
    f.write(f"[1] 和差化積 (5 對): {'PASS' if PASS1 else 'FAIL'} max dev {max_dev1:.2e}\n")
    f.write(f"[2] m_t/m_b O34 閉合: {'PASS' if PASS2 else 'FAIL'} dev {dev_tb:.6f}%\n")
    f.write(f"[3] sin 比值結構: {'PASS' if PASS3 else 'FAIL'}\n")
    f.write(f"[4] Σγ_odd=88, Σγ_even=90: {'PASS' if PASS4 else 'FAIL'}\n")
    f.write(f"[5] Koide Q=2/3: {'PASS' if PASS5 else 'FAIL'} Q={Q:.10f}\n")
    f.write(f"[6] tan/cos 恆等式: {'PASS' if PASS6 else 'FAIL'} max dev {max_dev6:.2e}\n")
    f.write(f"[7] m_u/m_d 0.026% 已閉合 (sin(10)/sin(24)), m_s/m_d 0.94% 未閉合: {'PASS' if PASS7 else 'FAIL'}\n")
    f.write(f"[8] overfit 風險確認: {'PASS' if PASS8 else 'FAIL'} (審計 fit {dev_audit:.4f}%)\n")
    f.write(f"\n總計: {sum(results)}/{len(results)} PASS\n")
print(f"\n  結果已寫入 data/verification_audit_results.txt")
