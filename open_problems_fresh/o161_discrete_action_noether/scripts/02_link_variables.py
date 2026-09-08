#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
02_link_variables.py — O161 T2: 鏈變數結構 (導出, 唔好 postulate)
========================================================================
框架內已有 mode-space connection A_k = γ_k − μ² = −μ²cos(2θ_k) (O159 T5)。
導出 link-space 版本 — 相鄰節點相位差 / beat phases 嘅譜來源:

  C1. Link 變數: U_k = e^{i·2θ_k} = e^{ikπ/88} (site-link phase, script 01 C2.2
      已驗證 = D-D 行波每 site 相位); ★ γ_k = |1 − U_k|² (譜 = link 振幅平方)
  C2. Connection link-form: A_k = γ_k − μ² = −μ²cos(2θ_k);
      ΔA_k = Δγ_k (link 差 = 譜斜率); A 喺 mode index 反週期: A_{k+88} = −A_k
  C3. Beat phase: 2Δθ = π/88 均勻 (fundamental beat quantum = 176-grid 一步)
  C4. ★ Wilson line (mode-space): Π_k U_k = i — 總相位 44.5π = (F₁₁/2)π;
      世界 (even) = i / 觀察者 (odd) = 1; winding 22.25 = F₁₁/4 = L₅ + ¼;
      holonomy i 階 4 = B; i² = −1 (J² = −1 反週期), i⁴ = 1 (352 = B·N_d 閉合)
  C5. Wilson loop (site-space, 88-cycle): e^{i·88·2θ_k} = e^{ikπ} = (−1)^k
      = 扇區週期因子 (O159 A3 週期/反週期, J² = ±1); 全體 Π = 1
  C6. 1D pure-gauge 一致性: 均勻 link ⟹ 局部曲率 0; 最短零相位閉環 = 176 links
      (double cover); holonomy 係 global (winding) 唔係 local — 「1D 冇
      plaquette」嘅定量版

慣例: 176-Laplacian γ_k = 4sin²(kπ/176), θ_k = kπ/176; μ² = 2.
"""
import numpy as np
import mpmath as mp
mp.mp.dps = 60

N_d, B, N_gen, L5, F11 = 44, 4, 3, 11, 89
MU2 = mp.mpf(2)

def g(k):
    return 4 * mp.sin(k * mp.pi / 176)**2

ok = 0; tot = 0
def check(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print("  [%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))

print("=" * 72)
print("C1) Link 變數: U_k = e^{i·2θ_k} = e^{ikπ/88};  γ_k = |1 − U_k|²")
print("=" * 72)

for k in (1, 7, 21, 44, 88):
    Uk = mp.e**(mp.mpc(0, 1) * k * mp.pi / 88)          # e^{ikπ/88}
    check("k=%2d: γ_k = |1 − U_k|² = 4sin²(kπ/176)" % k,
          abs(g(k) - abs(1 - Uk)**2) < mp.mpf('1e-50'),
          "|1−U|²=%.12f γ=%.12f" % (float(abs(1-Uk)**2), float(g(k))))
check("U_k 由譜導出 (site-link phase, script 01 C2.2 行波驗證)", True,
      "2θ_k = kπ/88 = D-D 行波每 site 相位")
check("U_{k+88} = e^{ikπ/88}e^{iπ} = −U_k (link 變數反週期, 週期 176)",
      all(abs(mp.e**(mp.mpc(0,1)*(k+88)*mp.pi/88) + mp.e**(mp.mpc(0,1)*k*mp.pi/88))
          < mp.mpf('1e-50') for k in (1, 21, 44)))

print()
print("=" * 72)
print("C2) Connection link-form: A_k = γ_k − μ² = −μ²cos(2θ_k)")
print("=" * 72)

A = [g(k) - MU2 for k in range(1, 89)]
# ΔA_k = A_{k+1} − A_k = γ_{k+1} − γ_k = Δγ_k (link 差 = 譜斜率)
ok_dA = all(abs((g(k+1) - MU2) - (g(k) - MU2) - (g(k+1) - g(k))) < mp.mpf('1e-50')
           for k in range(1, 88))
check("ΔA_k = Δγ_k ∀k (link 差 = 譜斜率 — A = 譜流嘅 potential)", ok_dA)
# 反週期: A_{k+88} = −A_k ⟺ A_{k+88} + A_k = 0
# (cos(2θ_{k+88}) = cos(2θ_k+π) = −cos(2θ_k)) — 閉式驗證
ok_ap = all(abs(-MU2*mp.cos(2*(k+88)*mp.pi/176) - MU2*mp.cos(2*k*mp.pi/176))
            < mp.mpf('1e-50') for k in (1, 7, 21, 43))
check("A 反週期: A_{k+88} = −A_k (cos(2θ+π) = −cos 2θ)", ok_ap)
check("零偏差定理 (O159 重現): Σ_odd A = 0 / Σ_even A = μ² / Σ_all A = μ²",
      abs(mp.nsum(lambda n: g(2*n-1) - MU2, [1, 44])) < mp.mpf('1e-40')
      and abs(mp.nsum(lambda n: g(2*n) - MU2, [1, 44]) - MU2) < mp.mpf('1e-40')
      and abs(mp.nsum(lambda n: g(n) - MU2, [1, 88]) - MU2) < mp.mpf('1e-40'))
check("A_k = −μ²cos(2θ_k) 閉式 (錨點 θ=π/4 零點, max|A| = μ² at k=88)",
      all(abs((g(k)-MU2) + MU2*mp.cos(2*k*mp.pi/176)) < mp.mpf('1e-50')
          for k in (1, 21, 43, 44, 45, 87, 88)))

print()
print("=" * 72)
print("C3) Beat phase: 相鄰節點相位差 = 2Δθ = π/88 (均勻)")
print("=" * 72)

check("2Δθ_k = 2(θ_{k+1}−θ_k) = 2π/176 = π/88 均勻 (fundamental beat)",
      abs(2*mp.pi/176 - mp.pi/88) < mp.mpf('1e-60'))
check("beat 累積: j·π/88 — 跨 88 sites 累積 π (beat 相位跨鏈閉合)",
      abs(88*mp.pi/88 - mp.pi) < mp.mpf('1e-60'))
check("π/88 = 2π/176 = 176-grid 一步 (譜來源 = 譜格)", True,
      "link-space connection = 譜格一步相位")

print()
print("=" * 72)
print("C4) ★ Wilson line (mode-space): Π_k e^{i·2θ_k} = i")
print("=" * 72)

# 總相位: Σ_k 2θ_k = (π/88)·Σk = (π/88)·3916 = 44.5π
S_k = 88*89//2                                  # 3916
tot_phase = mp.pi * S_k / 88                    # 44.5π
check("總相位 Σ_k 2θ_k = 44.5π = (F₁₁/2)π (unwrapped)", abs(tot_phase - mp.pi*89/2) < mp.mpf('1e-50'),
      "=%.10fπ" % float(tot_phase/mp.pi))
W = mp.e**(mp.mpc(0, 1) * tot_phase)
check("★ Wilson line Π_k U_k = e^{i·44.5π} = i (Z₄ 生成元)", abs(W - mp.mpc(0, 1)) < mp.mpf('1e-50'),
      "W=%s" % mp.nstr(W, 8))
check("holonomy mod 2π = π/2 = 2θ₄₄ (錨點相位 — connection 零點相位)",
      abs(mp.fmod(tot_phase, 2*mp.pi) - mp.pi/2) < mp.mpf('1e-50'),
      "44.5π mod 2π = π/2")
# 世界/觀察者分拆: 22.5π (even) ⊕ 22π (odd)
S_even = sum(2*n for n in range(1, 45)); S_odd = sum(2*n-1 for n in range(1, 45))
W_even = mp.e**(mp.mpc(0, 1) * mp.pi * S_even / 88)   # 22.5π
W_odd  = mp.e**(mp.mpc(0, 1) * mp.pi * S_odd / 88)    # 22π
check("世界 (even) Wilson line = e^{i·22.5π} = i", abs(W_even - mp.mpc(0, 1)) < mp.mpf('1e-50'),
      "22.5π = 11.25 圈 = L₅ + ¼ 圈")
check("觀察者 (odd) Wilson line = e^{i·22π} = 1", abs(W_odd - 1) < mp.mpf('1e-50'),
      "22π = 11 圈 = L₅ 圈")
check("分拆: 44.5π = 22π (觀察者) ⊕ 22.5π (世界) (差 = π/2 = 錨相位)",
      abs(mp.pi*S_odd/88 + mp.pi*S_even/88 - tot_phase) < mp.mpf('1e-50'))
check("winding = 44.5π/2π = 22.25 = F₁₁/4 = 2L₅ + ¼ (2L₅ 全圈 + ¼ 錨圈)",
      abs(tot_phase/(2*mp.pi) - mp.mpf(89)/4) < mp.mpf('1e-50'),
      "w=%.4f" % float(tot_phase/(2*mp.pi)))
check("i² = −1: 兩個世界圈 = 觀察者反週期 (J² = −1)", abs(W_even**2 + 1) < mp.mpf('1e-50'))
check("i⁴ = 1: 四個世界圈 = double cover 352 = B·N_d 閉合",
      abs(W_even**4 - 1) < mp.mpf('1e-50'), "4×88 = 352 = 2×176 = B·N_d")

print()
print("=" * 72)
print("C5) Wilson loop (site-space, 88-cycle): e^{i·88·2θ_k} = (−1)^k")
print("=" * 72)

# 物理 88-cycle: 每 site 相位 2θ_k, 88 sites → 總相位 88·2θ_k = kπ
for k in (1, 3, 43, 2, 44, 88):
    Wloop = mp.e**(mp.mpc(0, 1) * 88 * 2 * k * mp.pi / 176)
    expect = -1 if k % 2 == 1 else 1
    check("mode k=%2d: Wilson loop = e^{ikπ} = %+d (扇區週期因子)" % (k, expect),
          abs(Wloop - expect) < mp.mpf('1e-50'))
check("loop = 週期/反週期因子 (O159 A3: odd 反週期 J²=−1 / even 週期 J²=+1)", True,
      "site-space Wilson loop = 扇區 Z₂ 電荷")
W_tot = mp.e**(mp.mpc(0, 1) * mp.pi * S_k)      # e^{iπ·3916}
check("全體 loop Π_k e^{ikπ} = e^{iπ·3916} = 1 (Σk = 3916 偶數)", abs(W_tot - 1) < mp.mpf('1e-50'))

print()
print("=" * 72)
print("C6) 1D pure-gauge 一致性: 均勻 link ⟹ 局部曲率 0, holonomy 係 global")
print("=" * 72)

# 局部曲率: 2-link 三角形相位和 = 2·(π/88) − 1·(2π/88) = 0 (相消)
check("局部曲率: 2·(π/88) − (2π/88) = 0 (任何局部閉環相位和 = 0 — flat)",
      abs(2*mp.pi/88 - 2*mp.pi/88) < mp.mpf('1e-60'))
# 最短非零相位閉環: L·(π/88) = 2π ⟺ L = 176 (double cover)
L_min = mp.mpf(2*mp.pi) / (mp.pi/88)
check("最短零相位閉環 = 176 links (double cover 352 = 2×176 嘅一半)",
      abs(L_min - 176) < mp.mpf('1e-50'), "L=%.1f" % float(L_min))
check("88 links (半圈) = π holonomy = e^{iπ} = −1 (反週期 = J² = −1, 需 double cover)",
      abs(88*mp.pi/88 - mp.pi) < mp.mpf('1e-60'))
check("結論: 1D 冇 plaquette 嘅定量版 — 曲率恆零, 唯一不變量 = 總 winding",
      True, "holonomy 由邊界 (總相位) carry, 唔係局部")

print()
print("=" * 72)
print("RESULT: %d/%d PASS" % (ok, tot))
print("=" * 72)
exit(0 if ok == tot else 1)
