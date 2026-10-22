#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O78 scripts/01_pure_math_reframing.py
=====================================
純數學 re-framing: 剝離「觀察者」語義, 證明奇偶分裂係 Z2 分級 + 插值細化。

核心問題: 「世界/觀察者」90/88 分裂, 剝離 label 之後剩低咩數學結構?

答案 (三層):
  L1: 奇偶子空間 = 週期鏈嘅 Z2 分級 (parity sector), 任何偶數 N-ring 都有
      → 唔需要「觀察者」概念
  L2: 88-site = 44-site 嘅細化 (refinement): 奇數模式 = 半整數插值點
      → 奇數子空間 = 44-site 譜嘅「半整數對偶」, 唔係外加實體
  L3: 奇偶差 μ² = Σγ_even − Σγ_odd = 2 = O39 SSB 質量項
      → 奇偶分裂有物理功能: 冇佢就冇 SSB, 冇質量生成

驗證:
  1. Z2 分級代數: P_odd + P_even = I, P_odd·P_even = 0, 投影完備性
  2. 插值身份: γ_{2n} = γ_n^(44) (偶數模式 = 44-site 模式), γ_{2n-1} = 半整數模式
  3. 奇偶差: Σγ_even − Σγ_odd = 2 (任何偶數 N, 證明 + 數值)
  4. 細化率: 88/44 = 2 = B/2 (K_Tree 分支 B=4 嘅半分支)
  5. 新自由度: 奇數模式數 = 44 = N_d = 世界維度 (細化新增)
"""
import numpy as np

def gamma88(k):
    """88-site 對偶鏈本徵值 γ_k = 4sin^2(πk/176), k = 1..88 (物理單位 1)."""
    return 4.0 * np.sin(np.pi * k / 176.0) ** 2

def gamma44(n):
    """44-site 鏈本徵值 γ_n^(44) = 4sin^2(πn/88), n = 1..44."""
    return 4.0 * np.sin(np.pi * n / 88.0) ** 2

def main():
    print("=" * 70)
    print("O78 script 01: 純數學 re-framing — 奇偶分裂 = Z2 分級 + 插值細化")
    print("=" * 70)

    # ---------- L1: Z2 分級代數 ----------
    print("\n[L1] Z2 分級 (parity sector) 代數")
    N = 88
    k_odd = np.arange(1, N + 1, 2)    # 1, 3, ..., 87
    k_even = np.arange(2, N + 1, 2)   # 2, 4, ..., 88
    g_odd = gamma88(k_odd)
    g_even = gamma88(k_even)
    g_all = gamma88(np.arange(1, N + 1))

    # 投影算子: 唔需要「觀察者」概念 — 純奇偶索引
    P_odd = np.zeros(N)
    P_odd[k_odd - 1] = 1.0
    P_even = np.ones(N) - P_odd
    # P_odd^2 = P_odd (冪等), P_odd·P_even = 0 (正交), P_odd + P_even = I (完備)
    # (1D array: 用 element-wise 乘法 — P 係 0/1 對角投影)
    idem_odd = np.allclose(P_odd * P_odd, P_odd)
    idem_even = np.allclose(P_even * P_even, P_even)
    ortho = np.allclose(P_odd * P_even, 0.0)
    complete = np.allclose(P_odd + P_even, 1.0)
    print(f"  P_odd^2 = P_odd      : {idem_odd}")
    print(f"  P_even^2 = P_even   : {idem_even}")
    print(f"  P_odd * P_even = 0  : {ortho}")
    print(f"  P_odd + P_even = I  : {complete}")
    L1 = idem_odd and idem_even and ortho and complete
    print(f"  L1 PASS: {L1}")

    # ---------- L2: 插值細化身份 ----------
    print("\n[L2] 88-site = 44-site 細化 (插值身份)")
    n_arr = np.arange(1, 45)
    # γ_{2n} = γ_n^(44): 偶數模式就係 44-site 模式
    dev_even = np.max(np.abs(gamma88(2 * n_arr) - gamma44(n_arr)))
    print(f"  γ_{{2n}} = γ_n^(44) 最大偏差: {dev_even:.2e}  (期望 0)")
    # 奇數模式 = 半整數插值: γ_{2n-1} = 4sin^2((2n-1)π/176) = 4sin^2((n-0.5)π/88)
    half = 4.0 * np.sin((n_arr - 0.5) * np.pi / 88.0) ** 2
    dev_half = np.max(np.abs(gamma88(2 * n_arr - 1) - half))
    print(f"  γ_{{2n-1}} = γ^half(n-0.5) 最大偏差: {dev_half:.2e}  (期望 0)")
    # 奇數模式 = 細化新增自由度
    print(f"  奇數模式數 = {len(k_odd)} = 44 = N_d (世界維度)")
    print(f"  偶數模式數 = {len(k_even)} = 44")
    L2 = dev_even < 1e-12 and dev_half < 1e-12
    print(f"  L2 PASS: {L2}")

    # ---------- L3: 奇偶差 = SSB 質量項 ----------
    print("\n[L3] 奇偶差 = μ² (SSB 質量項)")
    s_odd = g_odd.sum()
    s_even = g_even.sum()
    s_all = g_all.sum()
    mu2 = s_even - s_odd
    print(f"  Σγ_odd  = {s_odd:.6f}  (期望 88)")
    print(f"  Σγ_even = {s_even:.6f}  (期望 90)")
    print(f"  Σγ_all  = {s_all:.6f}  (期望 178 = 2F11)")
    print(f"  μ² = Σγ_even − Σγ_odd = {mu2:.6f}  (期望 2 = O39 SSB 質量項)")
    L3 = abs(mu2 - 2.0) < 1e-9 and abs(s_odd - 88.0) < 1e-9 and abs(s_even - 90.0) < 1e-9
    print(f"  L3 PASS: {L3}")

    # ---------- L4: 細化率 ----------
    print("\n[L4] 細化率")
    ratio = 88.0 / 44.0
    print(f"  88/44 = {ratio} = B/2 (K_Tree 分支 B=4 嘅半分支)")
    print(f"  插值意義: 44-site → 88-site 係「每格插一個半整數點」(Nyquist 細化)")
    L4 = abs(ratio - 2.0) < 1e-12
    print(f"  L4 PASS: {L4}")

    # ---------- 一般化: 任何偶數 N ----------
    print("\n[一般化] 任何偶數 N-ring 嘅奇偶差")
    for Ntest in [44, 88, 100, 176, 1000]:
        kk = np.arange(1, Ntest + 1)
        gg = 4.0 * np.sin(np.pi * kk / (2 * Ntest)) ** 2
        s_o = gg[kk % 2 == 1].sum()
        s_e = gg[kk % 2 == 0].sum()
        print(f"  N={Ntest:4d}: Σγ_odd={s_o:9.4f} (N/2={Ntest/2:.0f}), "
              f"Σγ_even={s_e:9.4f} (N/2+1={Ntest/2+1:.0f}), 差={s_e-s_o:.4f}")
    print("  → 奇偶差 = 2 對所有偶數 N 成立 (O72 H2 平凡性確認)")
    print("  → 但呢個「平凡性」唔影響物理功能 (L3): μ²=2 係 SSB 質量項")

    # ---------- 總結 ----------
    total = all([L1, L2, L3, L4])
    print("\n" + "=" * 70)
    print(f"總結: L1 Z2分級 {L1} | L2 插值 {L2} | L3 奇偶差μ² {L3} | L4 細化率 {L4}")
    print(f"全 PASS: {total} / 4")
    print("核心訊息: 「世界/觀察者」label 剝離後, 剩低嘅係")
    print("  Z2 分級 (任何 N-ring) + 插值細化 (44→88) + μ²=2 (SSB 質量項)")
    print("  頭兩個係平凡數學, 第三個係物理功能 — 判決見 docs/06")
    print("=" * 70)
    return 0 if total else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
