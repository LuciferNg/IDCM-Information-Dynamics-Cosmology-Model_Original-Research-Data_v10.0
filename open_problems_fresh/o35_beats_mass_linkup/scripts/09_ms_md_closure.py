#!/usr/bin/env python3
"""
O35 — Step 8: m_s/m_d 精確閉合 (O34 唯一 🟡 → 🟢)
=====================================================
m_s/m_d = sin(22π/88)/sin(1π/88) × φ^k = 20.000

k = log_φ(20/sin(22,1)) = 0.019714
結構候選:
  10/528 = 0.018939  (dev 0.000775)
  11/528 = 0.020833  (dev 0.001119)
  2/88   = 0.022727  (dev 0.003013)

驗證:
  [1] φ^(10/528) × sin(22)/sin(1) = ?
  [2] φ^(11/528) × sin(22)/sin(1) = ?
  [3] 最佳結構 k (分母 528, 分子結構數)
  [4] 結構意義: 分子 10/11 = u 嘅 n? L₅?
"""

import numpy as np
from decimal import Decimal, getcontext

getcontext().prec = 60
phi = (1 + np.sqrt(5)) / 2

def sin_ratio(n1, n2):
    return np.sin(np.pi * n1 / 88) / np.sin(np.pi * n2 / 88)

def k_phi(r):
    return np.log(r) / np.log(phi)

print("=" * 67)
print("  O35 — Step 8: m_s/m_d 精確閉合")
print("=" * 67)

target_sd = 20.0  # m_s/m_d (93.4/4.67)
r_sin = sin_ratio(22, 1)
print(f"  m_s/m_d 目標 = {target_sd}")
print(f"  sin(22π/88)/sin(1π/88) = {r_sin:.6f}")
print(f"  原始偏差 = {abs(r_sin-target_sd)/target_sd*100:.4f}%")

k_exact = k_phi(target_sd / r_sin)
print(f"\n  k_exact = log_φ(20/19.811) = {k_exact:.8f}")

# ═══════════════════════════════════════════════════════════════
# [1-2] 結構 k 候選 (分母 528 = dimC·B·N_d)
# ═══════════════════════════════════════════════════════════════
print(f"\n─── 結構 k 候選 (分母 528) ───")
# 分子候選: 結構數 (Lucas L_n, Fibonacci F_n, 9, 10, 11, 12...)
numerator_cands = list(range(1, 30))
best = []
for num in numerator_cands:
    k_cand = num / 528
    r_pred = r_sin * phi**k_cand
    dev = abs(r_pred - target_sd)/target_sd*100
    best.append((dev, num, k_cand, r_pred))
best.sort()
for dev, num, k, r in best[:8]:
    print(f"  φ^({num}/528) → {r:.6f} (dev {dev:.4f}%)")

# ═══════════════════════════════════════════════════════════════
# [3] 最佳結構 k
# ═══════════════════════════════════════════════════════════════
print(f"\n─── 最佳結構 k ───")
best_dev, best_num, best_k, best_r = best[0]
print(f"  最佳: φ^({best_num}/528) → {best_r:.6f} (dev {best_dev:.4f}%)")
print(f"  分子 {best_num} 結構意義:")
print(f"    {best_num} = ?")
# 檢查: 10 = u 嘅 n! (O34: u(10))
# 11 = L₅!
print(f"    if num=10: 10 = n_u (u 夸克模式!)")
print(f"    if num=11: 11 = L₅ (Lucas)")

# ═══════════════════════════════════════════════════════════════
# [4] 結構意義深入
# ═══════════════════════════════════════════════════════════════
print(f"\n─── 結構意義 ───")
for num in [10, 11]:
    k_cand = num / 528
    r_pred = r_sin * phi**k_cand
    dev = abs(r_pred - target_sd)/target_sd*100
    print(f"  φ^({num}/528) = φ^({num}/(dimC·B·N_d))")
    print(f"    = φ^({num}/(3×4×44))")
    print(f"    → m_s/m_d = {r_pred:.6f} (dev {dev:.4f}%)")

# 同 O34 已閉合公式比較:
# m_μ/m_e = φ^(11+7/88): k 分母 88
# m_t/m_b = φ^(8+71/132): k 分母 132
# m_s/m_d = φ^(k/528): k 分母 528?
# 分母遞減: 88 → 132 → 528? 唔係單調
print(f"\n  O34 k 分母對比:")
print(f"    m_μ/m_e: L₄/88 = 7/88 (分母 88 = 2N_d)")
print(f"    m_t/m_b: 71/132 (分母 132 = dimC·N_d)")
print(f"    m_s/m_d: ?/528 (分母 528 = dimC·B·N_d)?")

# 檢查 k_exact 近 1/44?
print(f"\n  k_exact = {k_exact:.6f}")
print(f"  1/44 = {1/44:.6f} (dev {abs(k_exact-1/44):.6f})")
print(f"  10/528 = {10/528:.6f} (dev {abs(k_exact-10/528):.6f})")
print(f"  11/528 = {11/528:.6f} (dev {abs(k_exact-11/528):.6f})")
print(f"  2/88 = {2/88:.6f} (dev {abs(k_exact-2/88):.6f})")

# 用高精度 Decimal 驗證最佳
print(f"\n─── Decimal 高精度驗證 ───")
from decimal import Decimal
PHI = (Decimal(1) + Decimal(5).sqrt()) / 2
# 重新算 sin 比值用 float (夠精確到 1e-12)
for num in [10, 11]:
    k_cand = Decimal(num) / Decimal(528)
    r_pred_dec = Decimal(str(r_sin)) * (PHI ** k_cand)
    dev_dec = abs(r_pred_dec - Decimal('20')) / Decimal('20') * 100
    print(f"  φ^({num}/528) Decimal: {r_pred_dec:.10f} (dev {dev_dec:.6f}%)")

# 最終結論
print(f"\n{'═'*67}")
print(f"  結論: m_s/m_d = sin(22π/88)/sin(1π/88) × φ^(k/528)")
print(f"  k = 10 (n_u) 或 11 (L₅) 候選")
print(f"  需要更多結構論證鎖定 k (下一步)")
print(f"{'═'*67}")

with open("data/step8_ms_md_closure_results.txt", "w") as f:
    f.write("O35 — Step 8: m_s/m_d 精確閉合\n")
    f.write("=" * 67 + "\n\n")
    f.write(f"目標 m_s/m_d = {target_sd}\n")
    f.write(f"sin(22,1) = {r_sin:.6f} (原始 dev {abs(r_sin-target_sd)/target_sd*100:.4f}%)\n")
    f.write(f"k_exact = {k_exact:.8f}\n\n")
    for dev, num, k, r in best[:5]:
        f.write(f"  phi^({num}/528): {r:.6f} (dev {dev:.4f}%)\n")
    f.write(f"\n候選: k = 10 (n_u) 或 11 (L₅)\n")
print(f"\n  結果已寫入 data/step8_ms_md_closure_results.txt")
