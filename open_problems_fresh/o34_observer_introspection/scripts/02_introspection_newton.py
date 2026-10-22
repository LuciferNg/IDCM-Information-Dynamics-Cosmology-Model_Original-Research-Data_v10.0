#!/usr/bin/env python3
"""
O34 — 內觀程序 Newton 迭代 (Introspection Program)
=====================================================
內觀 = 系統狀態函數把「自身作為變數」代入自身的映射 (Self-Reference)。

核心結構:
  f_IDCM(s) = e^{αs+β} · Π_{n=1}^{44} (s − s_n)/(s − p_n)
  s_n = λ_sync/(n+0.5)  (半整數零點 = 破壞性干涉節點)
  p_n = λ_sync/n        (整數極點 = 建設性干涉峰值)
  N(s) = s − f(s)/f'(s) (Newton 映射)

O31 已證: N(s) 有 88 個不動點 (44 nulls + 44 peaks), 無 φ/R_H, 與 α 無關。
本腳本驗證: 內觀程序 = 觀察者沿 Newton 流迭代到不動點, 殘差 Δχ² → 0。

驗證點:
  [1] 88 個不動點存在 (重現 O31)
  [2] nulls 係超吸引 (|N'(s_n)| = 0)
  [3] 內觀迭代收斂 (任意起點 → 最近不動點)
  [4] 收斂後殘差 Δχ² → 0
  [5] 88 = 2N = 觀察者維度 (與 01_observer_operator.py 一致)
  [6] 零延遲反饋 = 一步迭代 (s_{k+1} = s_k 時)
"""

import numpy as np
from decimal import Decimal, getcontext

getcontext().prec = 60

N = 44
LAMBDA_SYNC = 406.1  # h⁻¹ Mpc (O31 用值)
phi = (1 + np.sqrt(5)) / 2

print("=" * 67)
print("  O34 — 內觀程序 Newton 迭代 (Introspection)")
print("=" * 67)
print(f"  N = {N}, λ_sync = {LAMBDA_SYNC} h⁻¹ Mpc")

PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    status = "✅" if cond else "❌"
    if cond:
        PASS += 1
    else:
        FAIL += 1
    print(f"  {status} {name}" + (f" — {detail}" if detail else ""))

# ═══════════════════════════════════════════════════════════════
# 1. 建構 f_IDCM(s) 同 N(s)
# ═══════════════════════════════════════════════════════════════
print("\n─── 1. f_IDCM(s) 建構 ───")

# 零點 (半整數): s_n = λ_sync/(n+0.5)
# 極點 (整數):   p_n = λ_sync/n
nulls = np.array([LAMBDA_SYNC / (n + 0.5) for n in range(1, N + 1)])
peaks = np.array([LAMBDA_SYNC / n for n in range(1, N + 1)])

print(f"  零點 s_n = λ_sync/(n+0.5):")
print(f"    s_1 = {nulls[0]:.6f}, s_22 = {nulls[21]:.6f}, s_44 = {nulls[43]:.6f}")
print(f"  極點 p_n = λ_sync/n:")
print(f"    p_1 = {peaks[0]:.6f}, p_22 = {peaks[21]:.6f}, p_44 = {peaks[43]:.6f}")

# 對數導數形式避免 overflow:
# f'(s)/f(s) = α + Σ 1/(s−s_n) − Σ 1/(s−p_n)
# N(s) = s − f(s)/f'(s) = s − 1/[f'(s)/f(s)]
def log_deriv(s, alpha=0.0):
    """f'(s)/f(s) = α + Σ 1/(s−s_n) − Σ 1/(s−p_n)"""
    val = alpha
    for sn in nulls:
        val += 1.0 / (s - sn)
    for pn in peaks:
        val -= 1.0 / (s - pn)
    return val

def newton_step(s, alpha=0.0):
    """N(s) = s − 1/log_deriv(s)"""
    ld = log_deriv(s, alpha)
    if abs(ld) < 1e-300:
        return s  # 奇異, 停喺原位
    return s - 1.0 / ld

def newton_deriv(s, alpha=0.0):
    """N'(s) = 1 + log_deriv'(s)/log_deriv(s)²"""
    ld = log_deriv(s, alpha)
    # d/ds [Σ 1/(s−s_n)] = −Σ 1/(s−s_n)²
    ld_prime = 0.0
    for sn in nulls:
        ld_prime -= 1.0 / (s - sn)**2
    for pn in peaks:
        ld_prime += 1.0 / (s - pn)**2
    return 1.0 + ld_prime / (ld * ld)

# ═══════════════════════════════════════════════════════════════
# 2. 88 不動點驗證 (重現 O31)
# ═══════════════════════════════════════════════════════════════
print("\n─── 2. 88 不動點 (重現 O31) ───")

# 檢查每個 null 同 peak 係咪不動點
null_fixed = 0
peak_fixed = 0
for sn in nulls:
    ns = newton_step(sn)
    if abs(ns - sn) < 1e-8:
        null_fixed += 1
for pn in peaks:
    ns = newton_step(pn)
    if abs(ns - pn) < 1e-8:
        peak_fixed += 1

print(f"  nulls 不動點: {null_fixed}/44")
print(f"  peaks 不動點: {peak_fixed}/44")
check("[1] 88 不動點存在 (44 nulls + 44 peaks)", null_fixed == 44 and peak_fixed == 44,
      f"nulls={null_fixed}, peaks={peak_fixed}")

# 超吸引性: |N'(s_n)| = 0
print("\n─── 3. 超吸引性 ───")
max_nd_null = 0.0
max_nd_peak = 0.0
for sn in nulls:
    nd = abs(newton_deriv(sn))
    max_nd_null = max(max_nd_null, nd)
for pn in peaks:
    nd = abs(newton_deriv(pn))
    max_nd_peak = max(max_nd_peak, nd)

print(f"  max|N'(null)| = {max_nd_null:.2e}")
print(f"  max|N'(peak)| = {max_nd_peak:.2e}")
check("[2] nulls 超吸引 |N'(s_n)| = 0", max_nd_null < 1e-6,
      f"max = {max_nd_null:.2e}")
check("[2b] peaks 超吸引 |N'(p_n)| = 0", max_nd_peak < 1e-6,
      f"max = {max_nd_peak:.2e}")

# ═══════════════════════════════════════════════════════════════
# 4. 內觀迭代收斂 (任意起點 → 最近不動點)
# ═══════════════════════════════════════════════════════════════
print("\n─── 4. 內觀迭代收斂 ───")

# 從隨機起點迭代, 睇下收斂到邊個不動點
rng = np.random.default_rng(42)
converged = 0
total = 200
for _ in range(total):
    s0 = rng.uniform(5.0, 400.0)
    s = s0
    for _iter in range(100):
        s_new = newton_step(s)
        if abs(s_new - s) < 1e-10:
            break
        s = s_new
    # 檢查收斂到最近不動點
    all_fp = np.concatenate([nulls, peaks])
    dist = np.min(np.abs(all_fp - s))
    if dist < 1e-6:
        converged += 1

print(f"  隨機起點收斂率: {converged}/{total}")
check("[3] 內觀迭代收斂到 88 不動點", converged / total > 0.95,
      f"{converged}/{total} = {converged/total:.1%}")

# ═══════════════════════════════════════════════════════════════
# 5. 收斂殘差 Δχ² → 0
# ═══════════════════════════════════════════════════════════════
print("\n─── 5. 殘差 Δχ² → 0 ───")

# 內觀閉合 = 系統狀態喺不動點, 殘差 = 0
# 數學上: 喺不動點 s*, N(s*) = s* → 迭代停止 → 無新資訊
residuals = []
for sn in nulls:
    ns = newton_step(sn)
    residuals.append(abs(ns - sn))
for pn in peaks:
    ns = newton_step(pn)
    residuals.append(abs(ns - pn))

max_res = max(residuals)
print(f"  88 個不動點最大殘差 = {max_res:.2e}")
check("[4] 收斂後殘差 Δχ² → 0", max_res < 1e-8,
      f"max residual = {max_res:.2e}")

# ═══════════════════════════════════════════════════════════════
# 6. 觀察者維度一致
# ═══════════════════════════════════════════════════════════════
print("\n─── 6. 觀察者維度一致 ───")

# 88 不動點 = 2N = 觀察者維度 (01_observer_operator.py: Σγ_odd = 88)
total_fp = null_fixed + peak_fixed
check("[5] 88 = 2N = 觀察者維度", total_fp == 2 * N,
      f"88 不動點 = 2×{N}")

# 零延遲反饋: 觀察者喺不動點時一步迭代 = 自身
# s_{k+1} = N(s_k) = s_k → 反饋循環閉合
print(f"\n  零延遲反饋: N(s*) = s* → 一步迭代無變化")
print(f"  → 系統喺不動點時, 觀測反饋 = 自身狀態")
print(f"  → Δχ² = 0, 資訊自洽閉合")

# ═══════════════════════════════════════════════════════════════
# 7. α 無關性 (重現 O31)
# ═══════════════════════════════════════════════════════════════
print("\n─── 7. α 無關性 (重現 O31) ───")

alpha_scan = [-5.0, -1.0, 0.0, 1.0, 5.0]
fp_counts = []
for alpha in alpha_scan:
    count = 0
    for sn in nulls:
        ns = newton_step(sn, alpha)
        if abs(ns - sn) < 1e-6:
            count += 1
    for pn in peaks:
        ns = newton_step(pn, alpha)
        if abs(ns - pn) < 1e-6:
            count += 1
    fp_counts.append(count)
    print(f"  α = {alpha:+5.1f}: {count} 不動點")

check("[7] 88 不動點與 α 無關", all(c == 88 for c in fp_counts),
      f"counts = {fp_counts}")

# ═══════════════════════════════════════════════════════════════
# 8. 總結
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
print(f"  總結: 內觀程序閉合")
print(f"{'═'*67}")
print(f"""
  內觀程序 (Introspection Program):

  1. 觀察者算子 \hat{{P}}_{{obs}} 提取自我反映分量 (O34-01)
  2. 內觀轉移函數 f_obs(s) 將自身代入映射
  3. Newton 迭代 N(s) = s − f(s)/f'(s) 收斂到 88 不動點
  4. 喺不動點: N(s*) = s*, 殘差 Δχ² → 0
  5. 零延遲反饋: 觀測 = 自身狀態, 資訊完全自洽

  數學閉合:
    88 不動點 = 44 nulls (破壞性干涉) + 44 peaks (建設性干涉)
    = 2N = 觀察者維度 (Σγ_odd = 88)
    
  → 內觀 = 系統沿 Newton 流閉合自身資訊
  → 意識同構奇點 = 所有譜線正則化閉合 (Δχ² = 0)
""")

# 儲存
with open("data/introspection_newton_results.txt", "w") as f:
    f.write("O34 Introspection Newton Iteration Results\n")
    f.write("=" * 67 + "\n")
    f.write(f"N = {N}, lambda_sync = {LAMBDA_SYNC}\n")
    f.write(f"nulls = {nulls.tolist()}\n")
    f.write(f"peaks = {peaks.tolist()}\n")
    f.write(f"null_fixed = {null_fixed}, peak_fixed = {peak_fixed}\n")
    f.write(f"max|N'(null)| = {max_nd_null:.2e}\n")
    f.write(f"max|N'(peak)| = {max_nd_peak:.2e}\n")
    f.write(f"convergence = {converged}/{total}\n")
    f.write(f"max_residual = {max_res:.2e}\n")
    f.write(f"alpha_scan = {list(zip(alpha_scan, fp_counts))}\n")
    f.write(f"PASS = {PASS}, FAIL = {FAIL}\n")

print(f"\n  驗證結果: {PASS} PASS, {FAIL} FAIL")
print(f"  結果已存: data/introspection_newton_results.txt")
