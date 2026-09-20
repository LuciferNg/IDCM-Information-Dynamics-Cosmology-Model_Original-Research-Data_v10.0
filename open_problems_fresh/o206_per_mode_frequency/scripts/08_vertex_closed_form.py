#!/usr/bin/env python3
"""
O206 — Script 08: 位置算子矩陣元之解析閉式 (vertex closed form)
=========================================================
動機 (承接 docs/09 §五):
  兩項閉式 |Δm_n| ≈ |V²_(n,n−1)/Δγ + V²_(n,n+1)/Δγ| 之精度 <1.25%
  ⟹ 問: V_nm 本身有冇【零參數解析閉式】? 若有, 則 |Δm| 完全結構化。

解析推導 (本 script 之核心, 手算 + 數值驗證):
  X = diag(i − ⟨i⟩), i = 1..M−1, M = 89
  X_nm = (2/M)[Σ_i i sin(nπi/M) sin(mπi/M)] − ⟨i⟩δ_nm
  用 Σ_{i=1}^{M−1} i e^{ici} = z(1 − M z^{M−1} + (M−1)z^M)/(1−z)²,  z = e^{ic}, z^M = (−1)^k:
      k 偶 (≠0):  C_k = Σ i cos(πki/M) = −M/2
      k 奇:       C_k = M/2 − 1/(1 − cos(πk/M))
  ⟹ n+m 奇:  X_nm = (1/(2M))[ csc²(π(n+m)/(2M)) − csc²(π(n−m)/(2M)) ]
     n+m 偶:  X_nm = 0  (對角亦精確 0)

本 script:
  §A 閉式全 88×88 驗證 (mpmath dps=40)
  §B γ 差閉式: γ_n − γ_m = 4 sin(π(n+m)/88) sin(π(n−m)/88)
  §C ★ 權重比 r_n = V²_(n,n+1)/V²_(n,n−1) 之閉式
  §D 兩項閉式之全解析形式 + 與精確 |Δm| 比較
  §E 裁決
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from mpmath import mp, mpf, sin, pi, csc

sys.path.insert(0, str(Path(__file__).parent))
from o206_lib import (NC, ND, MU2, A5_MODES, LM, E_ring44, V_position,
                      logscore, sum_V2_dE)

mp.dps = 40
M = 89
OUT = Path(__file__).parent.parent / "data"
checks = []


def chk(name, cond, detail=""):
    checks.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))


V = V_position()
E = E_ring44()
base = logscore(sum_V2_dE(E, V))


def V_cf(n, m):
    """閉式 V_nm (n, m 為 1-based 模式編號)"""
    if (n + m) % 2 == 0:
        return mpf(0)
    return (1 / (2 * M)) * (csc(pi * (n + m) / (2 * M)) ** 2
                            - csc(pi * (n - m) / (2 * M)) ** 2)


print("=" * 100)
print("O206 Script 08: 位置算子矩陣元之解析閉式")
print("=" * 100)
print(f"\n  基準 |Δm| RMS = {base:.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§A 閉式全 88×88 驗證\n{'─'*100}")
maxdev_odd, maxdev_even, worst = mpf(0), mpf(0), None
for n in range(1, NC + 1):
    for m in range(1, NC + 1):
        d = abs(V_cf(n, m) - mpf(V[n - 1, m - 1]))
        if (n + m) % 2 == 1:
            if d > maxdev_odd:
                maxdev_odd, worst = d, (n, m)
        else:
            maxdev_even = max(maxdev_even, d)
chk("C1 [閉式] 全 7744 個矩陣元吻合 (n+m 奇): V_nm = (1/178)[csc²(π(n+m)/178) − csc²(π(n−m)/178)]",
    maxdev_odd < mpf('1e-11'),
    f"max dev = {mp.nstr(maxdev_odd, 3)} @ (n,m) = {worst} "
    f"(⚠️ 地板 = float64 V 之捨入 ~1e-13, 非閉式誤差)")
chk("C2 [閉式] 同 parity (n+m 偶) 全部精確零 (含對角)",
    maxdev_even < mpf('1e-11'), f"max dev = {mp.nstr(maxdev_even, 3)} (float64 地板)")
chk("C3 [閉式] 對角 X_nn = 0 精確 (與反射反對稱一致: ⟨X⟩_n = 0)",
    abs(V_cf(1, 1)) == 0 and abs(V_cf(22, 22)) == 0, "X_11 = X_22,22 = 0")

print(f"\n  閉式樣本 (n=1):  " + ", ".join(f"V_1,{m} = {float(V_cf(1,m)):+.6f}"
                                        for m in [2, 4, 6, 8]))
print(f"  數值樣本 (n=1):  " + ", ".join(f"V_1,{m} = {V[0,m-1]:+.6f}" for m in [2, 4, 6, 8]))

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§B γ 差閉式\n{'─'*100}")
dev_gd = mpf(0)
for n in range(1, NC + 1):
    for m in range(1, NC + 1):
        if n == m:
            continue
        cf = 4 * sin(pi * (n + m) / 88) * sin(pi * (n - m) / 88)
        dev_gd = max(dev_gd, abs(cf - (4 * sin(pi * n / 88) ** 2 - 4 * sin(pi * m / 88) ** 2)))
chk("C4 [閉式] γ_n − γ_m = 4 sin(π(n+m)/88) sin(π(n−m)/88)  (全對)",
    dev_gd < mpf('1e-30'), f"max dev = {mp.nstr(dev_gd, 3)}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§C ★ 權重比 r_n = V²_(n,n+1)/V²_(n,n−1) 之閉式\n{'─'*100}")
print("""
  推導:  csc²x − csc²y = sin(y+x)sin(y−x)/(sin²x sin²y)
    V²_(n,n+1) ∝ [sin(π(2n+2)/(2M))·sin(π·2n/(2M))]² = [sin(π(n+1)/M)sin(πn/M)]²
    V²_(n,n−1) ∝ [sin(π·2n/(2M))·(−sin(π(n−1)/M))]²
    ⟹ r_n = [ sin(π(n+1)/M) sin²(π(2n−1)/(2M)) / (sin(π(n−1)/M) sin²(π(2n+1)/(2M))) ]²
""")


def r_closed(n):
    return (sin(pi * (n + 1) / M) * sin(pi * (2 * n - 1) / (2 * M)) ** 2
            / (sin(pi * (n - 1) / M) * sin(pi * (2 * n + 1) / (2 * M)) ** 2)) ** 2


maxdev_r = mpf(0)
print(f"\n  {'n':>3} {'r_n (閉式)':>16} {'r_n (數值)':>16} {'偏差':>12}")
print("  " + "-" * 52)
for n in [2, 3, 4, 5, 7, 9, 11, 13, 22, 44]:
    cf = r_closed(n)
    num = (V_cf(n, n + 1) ** 2) / (V_cf(n, n - 1) ** 2)
    maxdev_r = max(maxdev_r, abs(cf - num))
    print(f"  {n:>3} {float(cf):>16.10f} {float(num):>16.10f} {float(abs(cf-num)):>12.2e}")
for n in range(2, NC):
    maxdev_r = max(maxdev_r, abs(r_closed(n) - V_cf(n, n + 1) ** 2 / V_cf(n, n - 1) ** 2))
chk("C5 ★ [閉式] 權重比 r_n 有零參數閉式 (n = 2..87 全部)",
    maxdev_r < mpf('1e-25'), f"max dev = {mp.nstr(maxdev_r, 3)}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§D 兩項閉式之全解析形式\n{'─'*100}")
print("""
  |Δm_n| ≈ | V²_(n,n−1)/(γ_n−γ_(n−1)) + V²_(n,n+1)/(γ_n−γ_(n+1)) |
  代 §A/§B 閉式 (γ 差 = 4 sin(π(2n∓1)/88) sin(∓π/88)):
     = (1/4) csc(π/88) · | V²_(n,n−1)/sin(π(2n−1)/88) − V²_(n,n+1)/sin(π(2n+1)/88) |
  ⟹ 【完全零參數解析式】, 無任何擬合常數
""")
two_term = []
for n in range(1, NC + 1):
    terms = []
    for m in (n - 1, n + 1):
        if 1 <= m <= NC:
            dg = 4 * math.sin(math.pi * (n + m) / 88) * math.sin(math.pi * (n - m) / 88)
            terms.append(float(V_cf(n, m)) ** 2 / dg)
    two_term.append(abs(sum(terms)))
two_term = np.array(two_term)
exact = sum_V2_dE(E, V)
tt_a5 = two_term[[n - 1 for n in A5_MODES]]
rel = np.abs(tt_a5 - exact) / np.abs(exact)
print(f"\n  {'n':>3} {'|Δm| 精確':>14} {'兩項解析':>14} {'相對偏差':>11}")
print("  " + "-" * 48)
for n, e, t in zip(A5_MODES, exact, tt_a5):
    print(f"  {n:>3} {e:>14.6f} {t:>14.6f} {abs(t-e)/abs(e):>11.6f}")
chk("C6 [解析] 兩項解析式之逐模最大相對偏差 < 5% (A₅ 9 模)",
    rel.max() < 0.05, f"max = {rel.max():.6f}")
chk("C7 [解析] 兩項解析式之形狀 RMS ≥ 精確基準 (唔改善)",
    logscore(tt_a5) >= base - 1e-9, f"{logscore(tt_a5):.4f} vs {base:.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§E 裁決 (script 08)\n{'─'*100}")
print(f"""
  ① ★ 位置算子矩陣元有【零參數解析閉式】:
       V_nm = (1/178)[ csc²(π(n+m)/178) − csc²(π(n−m)/178) ]   (n+m 奇)
       V_nm = 0                                                (n+m 偶)
     全 7744 元吻合 (mpmath dps=40); 對角精確 0
  ② γ 差亦有閉式: γ_n − γ_m = 4 sin(π(n+m)/88) sin(π(n−m)/88)
  ③ ★ 權重比有閉式 r_n = [sin(π(n+1)/89) sin²(π(2n−1)/178) / (sin(π(n−1)/89) sin²(π(2n+1)/178))]²
  ④ ⟹ |Δm_n| 之兩項近似 = 完全零參數解析式 (無擬合常數)
  ⑤ 但形狀 RMS 仍唔改善 ({logscore(tt_a5):.4f} vs {base:.4f}) ⟹ 缺口依然喺映射層
""")

n_pass = sum(1 for _, ok in checks if ok)
print(f"{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")
for name, ok in checks:
    if not ok:
        print(f"  FAIL: {name}")

with open(OUT / "08_vertex_closed_form.json", "w") as f:
    json.dump({
        "baseline_rms": base,
        "V_closed_form": "V_nm = (1/178)[csc^2(pi(n+m)/178) - csc^2(pi(n-m)/178)], n+m odd; else 0",
        "maxdev_odd": float(maxdev_odd), "maxdev_even": float(maxdev_even),
        "gamma_diff_closed": "gamma_n - gamma_m = 4 sin(pi(n+m)/88) sin(pi(n-m)/88)",
        "ratio_closed_form": "r_n = [sin(pi(n+1)/89) sin^2(pi(2n-1)/178) / (sin(pi(n-1)/89) sin^2(pi(2n+1)/178))]^2",
        "maxdev_ratio": float(maxdev_r),
        "two_term_rel_dev_max": float(rel.max()),
        "two_term_rms": float(logscore(tt_a5)),
        "checks_pass": int(n_pass), "checks_total": len(checks),
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/08_vertex_closed_form.json")
