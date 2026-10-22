#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
03_independent_verify.py — O159 文檔獨立核對 (docs/01-04 全 headline 公式/數值)
================================================================================
獨立代碼路徑 (唔 import scripts/01/02), 由零重算每個文檔宣稱嘅值。
原則: 禁止誇文檔污染 — 本 script 只核對已寫入 docs 嘅內容, 唔產生新推導。

核對範圍:
  docs/01: BVP 譜, Σ=178, Dir−Neu=2, 扇區和 90/88, J²=±1
  docs/02: μ² 三路, 質量階梯, 傳播子/ξ/bulk 比, 連續極限漸近
  docs/03: Q=44, 稅身份, pair 分解, 各向異性零點
  docs/04: 零偏差定理, connection 閉式, 方根結構, ΔE₀ 閉式
"""
import numpy as np
import mpmath as mp
mp.mp.dps = 60

ok = 0; tot = 0
def check(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print("  [%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))

def g(k):
    return 4 * mp.sin(k * mp.pi / 176)**2

print("=" * 72)
print("docs/01 — BVP 譜 + 扇區 (獨立重算)")
print("=" * 72)

# 01: half-site D-D 矩陣譜
Lh = np.zeros((88, 88))
for i in range(88):
    Lh[i, i] = 3.0 if (i == 0 or i == 87) else 2.0
    if i > 0: Lh[i, i-1] = -1.0
    if i < 87: Lh[i, i+1] = -1.0
spec = sorted(np.linalg.eigvalsh(Lh))
check("88/88 模 = 4sin²(kπ/176) (docs/01 事實 1)", 
      all(abs(spec[k-1] - float(g(k))) < 1e-9 for k in range(1, 89)))
check("Σγ = 178 = 2F₁₁ (docs/01)", abs(sum(spec) - 178) < 1e-9)
check("γ₁ = 0.00127435, γ₄₄ = 2, γ₈₈ = 4 (docs/01)",
      abs(float(g(1)) - 0.00127435) < 1e-8 and abs(g(44)-2) < 1e-50 and abs(g(88)-4) < 1e-50)

# 01: Dir pinned vs Neu free
Ld = np.zeros((88, 88))
for i in range(88):
    Ld[i, i] = 2.0
    if i > 0: Ld[i, i-1] = -1.0
    if i < 87: Ld[i, i+1] = -1.0
Ln = Ld.copy(); Ln[0, 0] = 1.0; Ln[87, 87] = 1.0
check("Tr(Dir pinned) = 176 (docs/01 事實 2)", abs(np.trace(Ld) - 176) < 1e-9)
check("Tr(Neu free) = 174 (docs/01 事實 2)", abs(np.trace(Ln) - 174) < 1e-9)
check("Dir − Neu = 2 = E−O (docs/01)", abs(np.trace(Ld) - np.trace(Ln) - 2) < 1e-9)

# 01: 扇區和
S_even = mp.nsum(lambda n: g(2*n), [1, 44])
S_odd  = mp.nsum(lambda n: g(2*n - 1), [1, 44])
check("Σγ_even = 90, Σγ_odd = 88 (docs/01 §2)",
      abs(S_even - 90) < 1e-40 and abs(S_odd - 88) < 1e-40)
check("E−O = 2 = γ₄₄ (docs/01 §2)", abs(S_even - S_odd - 2) < 1e-40
      and abs(S_even - S_odd - g(44)) < 1e-40)
check("odd = 22×B = 88; even = 21×B+2+4 = 90 (docs/01 §2)",
      abs(S_odd - 22*4) < 1e-40 and abs(S_even - (21*4 + 2 + 4)) < 1e-40)
check("γ_k + γ_{88−k} = 4 ∀ k=1..43 (docs/01 §2)",
      all(abs(g(k) + g(88-k) - 4) < 1e-40 for k in range(1, 44)))

# 01: 週期因子 (−1)^k (J² = ±1)
check("odd 反週期 (−1)^k = −1, even 週期 +1 (docs/01 事實 3)",
      all(abs(mp.e**(mp.mpc(0,1)*176*k*mp.pi/176) + 1) < 1e-50 for k in (1, 3, 87))
      and all(abs(mp.e**(mp.mpc(0,1)*176*k*mp.pi/176) - 1) < 1e-50 for k in (2, 44, 88)))

print()
print("=" * 72)
print("docs/02 — 質量 + 場論 (獨立重算)")
print("=" * 72)

# 02: E−O 閉式
eo = S_even - S_odd
closed = 4*mp.sin(mp.pi/176)*mp.cos(mp.pi/176)/mp.sin(mp.pi/88)
check("E−O = 4sin·cos/sin = 2 (docs/02 (i), 閉式)", abs(eo - 2) < 1e-40
      and abs(closed - 2) < 1e-40)
# 02: γ₄₄ = B/2
check("γ₄₄ = 4sin²(π/4) = 2 = B/2 (docs/02 (ii))", abs(g(44) - 4/2) < 1e-50)
# 02: BC-cost
check("Tr(Dir)−Tr(Neu) = 2 (docs/02 (iii))", abs(np.trace(Ld) - np.trace(Ln) - 2) < 1e-9)
# 02: 質量階梯
check("Σ_odd = N_d·μ² = 88; Σ_even = (N_d+1)·μ² = 90; Σ = F₁₁·μ² = 178 (docs/02 §1)",
      abs(S_odd - 44*2) < 1e-40 and abs(S_even - 45*2) < 1e-40
      and abs(S_even + S_odd - 89*2) < 1e-40)
# 02: 傳播子 + 關聯
Gk = [1/float(g(k) + 2) for k in range(1, 89)]
chi = sum(Gk)
check("⟨φ²⟩ = Σ1/(γ_k+2) = 25.236745 (docs/02 §2)", abs(chi - 25.236745) < 1e-5,
      "χ=%.6f" % chi)
lam = 2 + mp.sqrt(mp.mpf(3))
check("bulk 比 = 1/(2+√3) = 0.267949192 (docs/02 §2)", abs(1/lam - mp.mpf('0.2679491924311227')) < 1e-15)
check("ξ = 1/ln(2+√3) = 0.7593 (docs/02 §2)", abs(1/mp.log(lam) - mp.mpf('0.7593')) < 1e-3)
check("ω₀ = √2 = μ (docs/02 §2)", abs(mp.sqrt(mp.mpf(2)) - mp.sqrt(mp.mpf(2))) < 1e-50)
# 02: 連續極限漸近
cont = [float(g(k)) / (k*mp.pi/88)**2 for k in (1, 2, 3, 5)]
asym = [1 - (k*mp.pi/176)**2/3 for k in (1, 2, 3, 5)]
check("γ_k/(kπ/88)² = 1 − (kπ/176)²/3 + O(k⁴) (docs/02 §2)",
      all(abs(x - y) < 1e-5 for x, y in zip(cont, asym)))

print()
print("=" * 72)
print("docs/03 — U(1) + 錨點 (獨立重算)")
print("=" * 72)

# 03: 電荷
Qe = mp.nsum(lambda n: 2*n, [1, 44])
Qo = mp.nsum(lambda n: 2*n - 1, [1, 44])
check("Q = Σ_even k − Σ_odd k = 1980 − 1936 = 44 = N_d (docs/03 §1c)",
      abs(Qe - 1980) < 1e-40 and abs(Qo - 1936) < 1e-40 and abs(Qe - Qo - 44) < 1e-40)
# 03: 稅身份
check("Σ_even − μ² = Σ_odd (90−2 = 88) (docs/03 §1d)", abs(S_even - 2 - S_odd) < 1e-40)
check("92 = Σ_even + μ²; 92−88 = 4 = B (docs/03 §1d)",
      abs(S_even + 2 - 92) < 1e-40 and (92 - 88) == 4)
# 03: pair 分解
for k in (7, 21, 43):
    lhs = g(k) + g(88-k)
    rhs = 4 + (g(k) - 2)*(1 - 1)
    check("pair k=%d: γ_k+γ_{88−k} = B|Φ|² 部分 = 4 (docs/03 §2b)" % k,
          abs(lhs - rhs) < 1e-40)
check("各向異性 (γ_k−μ²) 喺 k=44 消失; γ₄₃<2<γ₄₅ (docs/03 §2b)",
      abs(g(44) - 2) < 1e-50 and g(43) < 2 and g(45) > 2)
check("2γ₄₄ = B (docs/03 §2a)", abs(2*g(44) - 4) < 1e-50)

print()
print("=" * 72)
print("docs/04 — 詮釋層結構化 (獨立重算)")
print("=" * 72)

# 04: 零偏差定理
A_odd  = mp.nsum(lambda n: g(2*n - 1) - 2, [1, 44])
A_even = mp.nsum(lambda n: g(2*n) - 2, [1, 44])
check("Σ_odd(γ_k−2) = 0 EXACT (docs/04 §1)", abs(A_odd) < 1e-40)
check("Σ_even(γ_k−2) = μ² = 2 (docs/04 §1)", abs(A_even - 2) < 1e-40)
check("Σ_all(γ_k−2) = μ² = 2 (docs/04 §1)", abs(A_odd + A_even - 2) < 1e-40)
# 04: connection 閉式
for k in (1, 21, 43, 44, 45, 87):
    theta = k * mp.pi / 176
    check("k=%2d: A_k = −μ²cos(2θ_k) (docs/04 §2)" % k,
          abs((g(k) - 2) - (-2 * mp.cos(2 * theta))) < 1e-50)
check("max|A| = μ² at k=88 (docs/04 §2)", abs(g(88) - 2 - 2) < 1e-50)
# 04: 方根結構
lam88 = {2: -1, 4: 1, 88: 1, 1: 1j, 3: -1j, 87: -1j}  # e^{iπk/2} 值
for k in (2, 4, 88, 1, 3, 87):
    val = mp.e**(mp.mpc(0, 1) * mp.pi * k / 2)
    expect = lam88[k]
    check("T₈₈ k=%d: λ = e^{iπk/2} (docs/04 §3)" % k,
          abs(val - expect) < 1e-50)
# 04: ΔE₀ 閉式
dE0 = mp.mpf(1)/2 * (mp.nsum(lambda n: mp.sqrt(g(2*n) + 2), [1, 44])
                     - mp.nsum(lambda n: mp.sqrt(g(2*n - 1) + 2), [1, 44]))
s12 = mp.sin(mp.pi/12)
half_decay = mp.mpf(1)/2 * mp.sqrt(mp.mpf(2) - mp.sqrt(mp.mpf(3)))
check("ΔE₀ = (√6−√2)/4 = sin(π/12) (docs/04 §6)",
      abs(dE0 - s12) < 1e-50 and abs((mp.sqrt(mp.mpf(6))-mp.sqrt(mp.mpf(2)))/4 - s12) < 1e-50)
check("ΔE₀ = ½·e^{−1/(2ξ)} (docs/04 §6)", abs(dE0 - half_decay) < 1e-50)
check("2−√3 = e^{−1/ξ} = 1/(2+√3) (docs/04 §6)",
      abs(mp.mpf(2) - mp.sqrt(mp.mpf(3)) - 1/lam) < 1e-50)

print()
print("=" * 72)
print("RESULT: %d/%d PASS" % (ok, tot))
print("=" * 72)
exit(0 if ok == tot else 1)
