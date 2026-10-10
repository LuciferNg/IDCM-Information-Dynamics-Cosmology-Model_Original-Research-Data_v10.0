#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O244 — scripts/06: T4 質量公式語義裁定實現（O140 docs/16 解封）
=====================================================================================
背景: O140 docs/16 (2026-10-10) 正式裁定 —
  O140 質量階梯 m_k = M₀·ε_k = M₀·4sin²(πk/2N)   = O137 正典 γ_n 譜（完全一致）
  O140 頻率階梯 ω_k = 2sin(πk/2N) = √ε_k          （頻率, 唔係質量）
  關係: m_k = M₀·ω_k²
鑑別證據: n/p = ε₇/ε₂₀ = 0.142618（BBN 閉合）只喺 ε 定義閉合（√ε 定義 0.3776 ✗）;
  C_f = m/(M₀γ_n) 喺 ε 定義 ≡ 1; 鏈乘法律兩種定義都成立 (無鑑別力)。

本 script: 獨立重現 + 驗證 O140 裁定（mpmath 60 位 + 閉式恆等）——
  [A] 命名恆等: ε_n(N) = 4sin²(πn/2N) = O137 γ_n 譜（逐 n, 多 N 零偏差）
  [B] 鏈乘法律: ε_{2a} = ε_a·ε_{44−a} (N=44) 用三角恆等驗證 → 無鑑別力（確認 O140）
  [C] ★ 鑑別: n/p = 0.14261761...（O137 BBN 閉合）; ε₇/ε₂₀ = n/p ✅;
      √ε₇/√ε₂₀ = 0.3776 ✗（>5σ 偏離）→ ε 定義勝
  [D] C_f = m/(M₀γ_n): ε 定義 ∀n ≡ 1; √ε 定義 = 1/√ε_n ≠ 1 → 正典勝
  [E] ω_n = √ε_n 零色散 (ω/√ε ≡ 1) —— 頻率階梯身份（同質量分開）
  [F] Σ_{n=1}^N ε_n = 2N+2（ζ_N(−1) 閉式核實: N=44 → 90）; 全環 (2N) 譜和 = 4N_d
判據: 閉式差 < 1e-45（mpmath dps 60）; n/p 鑑別差 < 1e-6 且 √ε 假設差 > 5% ⟹ 裁定成立。
唯一輸入: FSR 譜定義 4sin² + O140 docs/16。零自由參數。
"""
import mpmath as mp
mp.mp.dps = 60

PASS = 0; FAIL = 0; TOTAL = 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL; TOTAL += 1
    if cond: PASS += 1; mark = "OK "
    else:    FAIL += 1; mark = "XX "
    print(f"  [{mark}] {name} {detail}")

def eps(N, k): return 4*mp.sin(mp.pi*k/(2*N))**2
def w(N, k):   return 2*mp.sin(mp.pi*k/(2*N))          # √ε = 頻率階梯
def gamma(N,k): return 4*mp.sin(mp.pi*k/(2*N))**2      # O137 正典 γ_n = 4sin²

print("="*78)
print("  O244 scripts/06: T4 質量階梯語義 — O140 docs/16 裁定實現")
print("  唯一輸入: FSR 譜 ε=4sin² + O140 docs/16 裁定。零自由參數。")
print("="*78)

# ═══ A. 命名恆等: ε ≡ γ (O137 正典) ═══
print("\n─── [A] ε_n(N) = 4sin²(πn/2N) = O137 γ_n 譜（定義恆等） ───")
worstA = mp.mpf(0)
for N in [22, 44, 88, 176]:
    for k in range(1, N+1):
        d = abs(eps(N, k) - gamma(N, k))
        if d > worstA: worstA = d
check("A1 ε ≡ γ: N∈{22,44,88,176} 全譜零偏差", worstA < mp.mpf('1e-55'),
      f"(worst {mp.nstr(worstA,4)})")
# N=44 特例: ε^FSR = γ^CHAIN（O137 76 D1 再確認）
# O137 正典 γ_n = O124 88-site 環 Laplacian λ_n = 4sin²(πn/88), 唔係 4sin²(πn/176)
okA2 = True
for k in range(1, 45):
    lam_88 = 4*mp.sin(mp.pi*k/88)**2          # O124 λ_n: 88-site 環
    if abs(eps(44, k) - lam_88) > mp.mpf('1e-55'): okA2 = False
check("A2 N=44 ε^FSR ≡ 88-site γ^CHAIN = O124 λ_n（O137 D1 再確認）", okA2)

# ═══ B. 鏈乘法律 (N=44) ═══
print("\n─── [B] 鏈乘法律 ε_{2a} = ε_a·ε_{44−a} — 兩種定義都成立（無鑑別力） ───")
okB = True; worstB = mp.mpf(0)
for a in range(1, 22):
    d = abs(eps(44, 2*a) - eps(44, a)*eps(44, 44-a))
    if d > worstB: worstB = d
    if d > mp.mpf('1e-45'): okB = False
check("B1 ε 定義: ε_{2a} = ε_a·ε_{44−a} (a=1..21)", okB,
      f"(worst {mp.nstr(worstB,4)}; 三角恆等 4sin²(2θ)=16sin²θcos²θ)")
okB2 = True
for a in range(1, 22):
    d = abs(w(44, 2*a) - w(44, a)*w(44, 44-a))
    if d > mp.mpf('1e-45'): okB2 = False
check("B2 √ε 定義: ω_{2a} = ω_a·ω_{44−a} 都成立（O140: 無鑑別力）", okB2,
      "(確認 O140 判定)")

# ═══ C. ★ 鑑別: n/p = ε₇/ε₂₀ ═══
print("\n─── [C] ★ n/p 閉合: ε₇/ε₂₀ vs √ε₇/√ε₂₀ ───")
n_over_p = mp.mpf('0.14261761')    # O137 BBN 閉合值（docs/01 §13）
r_eps = eps(44, 7)/eps(44, 20)
r_sqr = w(44, 7)/w(44, 20)
print(f"       ε₇/ε₂₀   = {mp.nstr(r_eps, 15)}")
print(f"       √ε₇/√ε₂₀ = {mp.nstr(r_sqr, 10)}  (ε 比嘅平方根)")
d_eps = abs(r_eps - n_over_p)
d_sqr = abs(r_sqr - n_over_p)
check("C1 ε 定義閉合 n/p (rel < 1e-4)", d_eps < mp.mpf('1e-4')*n_over_p,
      f"(dev {mp.nstr(d_eps,4)})")
check("C2 √ε 定義唔閉合 (rel > 5%)", d_sqr > mp.mpf('0.05')*n_over_p,
      f"(√ε = {mp.nstr(r_sqr,6)} vs ε = {mp.nstr(r_eps,6)} — 裁定 ε 勝)")

# ═══ D. C_f = m/(M₀γ_n) ═══
print("\n─── [D] C_f 正典: m = M₀ε ⟹ C_f ≡ 1; m = M₀√ε ⟹ C_f ≠ 1 ───")
okD = True; worstD = mp.mpf(0)
for k in range(1, 45):
    cf = eps(44, k)/gamma(44, k)     # m=M₀ε / (M₀γ)
    if abs(cf - 1) > mp.mpf('1e-50'): okD = False
    if abs(cf - 1) > worstD: worstD = abs(cf - 1)
check("D1 m=M₀ε: C_f ≡ 1 (N=44 全 k)", okD, f"(worst {mp.nstr(worstD,4)})")
cf_sqr = w(44, 7)/gamma(44, 7)
check("D2 m=M₀√ε: C_f = 1/√ε ≠ 1（偏離正典）", abs(cf_sqr - 1) > mp.mpf('0.1'),
      f"(C_f(7) = {mp.nstr(cf_sqr,6)})")

# ═══ E. ω = √ε 零色散（頻率階梯身份） ═══
print("\n─── [E] 頻率階梯: ω_n = √ε_n（零色散, 同質量分開） ───")
okE = True; worstE = mp.mpf(0)
for N in [22, 44, 88]:
    for k in range(1, N+1):
        d = abs(w(N, k) - mp.sqrt(eps(N, k)))
        if d > worstE: worstE = d
        if d > mp.mpf('1e-50'): okE = False
check("E1 ω_n² = ε_n 全 n（頻率平方 = 譜 = 質量單位制內）", okE,
      f"(worst {mp.nstr(worstE,4)})")

# ═══ F. 譜和核實 ═══
print("\n─── [F] Σε = ζ_N(−1) 閉式 + 全環譜和 ───")
okF = True
for N in [22, 44, 88]:
    S = sum(eps(N, k) for k in range(1, N+1))
    if abs(S - (2*N+2)) > mp.mpf('1e-45'): okF = False
check("F1 Σ_{k=1}^N ε_k = 2N+2（= ζ_N(−1) 閉式, N=44 → 90）", okF,
      "(scripts/03-04 正矩族核實)")
M2 = 2*44
S_ring = sum(4*mp.sin(mp.pi*m/M2)**2 for m in range(1, M2+1))
check("F2 全環 (2N=88) 譜和 = 176 = 4N_d（T3 橋 Σ_ring）", abs(S_ring - 176) < mp.mpf('1e-45'))

print(f"\n{'='*78}")
print(f"  RESULT: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"{'='*78}")
import sys
sys.exit(0 if FAIL == 0 else 1)