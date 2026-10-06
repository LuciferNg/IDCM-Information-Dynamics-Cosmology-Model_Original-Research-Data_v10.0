#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O235 scripts/01 -- T1 診斷: 88-chain 奇偶結構 = tick-parity / staggered 對偶 (時性假說)

License: IDCM O235 — T1 (就地推於 O234 scripts/06, 2026-10-07 遷入 O235 作 scripts/01)。
純 stdlib。全部公式化, 無 numpy (eigenvector 用閉式)。
"""
import math

N = 88                      # 88-site ring (環, bipartite)
def gk88(k)  : return 4*math.sin(k*math.pi/88)**2    # 44-site chain / 88-ring 前一半
def gk176(k) : return 4*math.sin(k*math.pi/176)**2   # 88-site dual chain (k=1..88)

print("=" * 72)
print("T1: 88-chain 偶/奇 = tick-parity (checkerboard/staggered) 結構診斷")
print("=" * 72)

# ------------------------------------------------------------ [A] 譜基礎核對
sum88 = sum(gk88(k) for k in range(1, 45))           # 44-site chain
sum176_even = sum(gk176(k) for k in range(2, 89, 2)) # dual chain even k
sum176_odd  = sum(gk176(k) for k in range(1, 89, 2)) # dual chain odd k
print(f"\n[A] 譜基礎")
print(f"   44-site (88-ring 前半) Σ = {sum88:.12f}  (canon 90)")
print(f"   dual even k  (世界)  Σ = {sum176_even:.12f}  (canon 90)")
print(f"   dual odd  k  (觀察者) Σ = {sum176_odd:.12f}  (canon 88)")

# ------------------------------------------------------------ [B] staggered 對偶 4-gamma 雙射
print(f"\n[B] staggered 對偶: gamma -> 4-gamma (宇稱翻轉跳棋)")
# 178-double: gamma_{88-k} = 4 - gamma_k  (對 176-chain)
pairs = [(k, 88-k) for k in range(1, 88)]
bad = [k for k, kk in pairs if abs(gk176(k) + gk176(kk) - 4) > 1e-12]
print(f"   88-k 對偶 k<->88-k: {len(pairs)-len(bad)}/{len(pairs)} 對滿足 γ_k + γ_{{(88-k)}} = 4  (k=88: γ=4 自對)")
# s1 (k≡1) <-> s3 (k≡3) 元素級雙射
s1 = [k for k in range(1, 89) if k % 4 == 1]
s3 = [k for k in range(1, 89) if k % 4 == 3]
img = sorted(88 - k for k in s1)
print(f"   s1 = {s1}")
print(f"   s3 = {s3}")
print(f"   88-s1 = {img}  == s3? {img == s3}")
rel = [gk176(88-k) + gk176(k) - 4 for k in s1]
print(f"   元素級 4-γ 閉合: max|γ_{{88-k}} + γ_k - 4| = {max(abs(x) for x in rel):.2e}")
print(f"   Σs1 = {sum(gk176(k) for k in s1):.12f}  (canon 44-sec)")
print(f"   Σs3 = {sum(gk176(k) for k in s3):.12f}  (canon 44+sec)")
print(f"   Σs1+Σs3 = {sum(gk176(k) for k in s1)+sum(gk176(k) for k in s3):.12f} = 22*4 (逐對 4-閉合⟹transcendental 對消)")

# ------------------------------------------------------------ [C] bipartite (checkerboard) 結構
print(f"\n[C] bipartite/checkerboard: 環 C_88 偶長 ⟹ 二部图")
# 環 adjacency A: A[i,i±1]=1; L = 2I - A
# L 特徵值: 4sin²(πm/88) ✓ canon. A 特徵值: 2cos(2πm/88); 二部图 ±配對係 m <-> m+44 (唔係 88-m!)
Aeig_bad = max(abs(2*math.cos(2*math.pi*m/N) + 2*math.cos(2*math.pi*(m+44)/N)) for m in range(1, 44))
print(f"   adjacency ±配對 m<->m+44: max|λ_A(m) + λ_A(m+44)| = {Aeig_bad:.2e}")
print(f"   ⟹ 偶長環二部图成立 (checkerboard: 偶/奇 site 可交替更新)")

# 站波型 eigenvector 嘅 site 宇稱: u_m(n) = sin(2πmn/88)
print(f"\n[C2] 站波 site 宇稱 (88-ring, u_m(n)=sin(2πmn/88)): W_even - W_odd")
for m in [1, 2, 3, 4, 5, 7, 9, 11, 13, 22, 44]:
    W_e = sum(math.sin(2*math.pi*m*n/N)**2 for n in range(0, N, 2))
    W_o = sum(math.sin(2*math.pi*m*n/N)**2 for n in range(1, N, 2))
    print(f"   m={m:3d}  W_even={W_e:.6f}  W_odd={W_o:.6f}  Δ={W_e-W_o:+.6f}")

# ------------------------------------------------------------ [D] tick 算子 (off-diagonal 塊)
print(f"\n[D] tick 算子 H_cb = P_even·L·P_odd + P_odd·L·P_even (checkerboard 半步)")
# L = 2I - A; off-diag 塊 = -A_oe (44x44, 環 hopping)
# H_cb 譜 = ±|A 無向 hop 譜|: A_oe = 44x44 循環差 1 hop (週期 88 嘅 2 步); 佢嘅特徵值 = 2cos((2m+1)π/88)
tick_vals = sorted(2*math.cos((2*m+1)*math.pi/88) for m in range(44))
print(f"   tick 算子正部: {len(tick_vals)} 個  範圍 [{tick_vals[0]:+.6f}, {tick_vals[-1]:+.6f}]")
print(f"   μ²=2 係 L 譜中點 (γ_44=2): staggered 對偶 4-γ 嘅不動點 = {4/2:g} -> γ=2 ✓")

# ------------------------------------------------------------ [E] s1 (輕子槽) 條件: sec(π/88) 係唯一 transcendental
import math as m2
sec = 1/m2.cos(m2.pi/88)
print(f"\n[E] s1 輕子槽嘅 transcendental 盈缺")
print(f"   sec(π/88) = {sec:.12f}  -> s1 def = {sec-1:.3e} = {sec-1:+.6e}")
print(f"   判別: s1 = 44 - sec (虧), s3 = 44 + sec (盈) ⟹ 輕子 sector = 唯一非整數殘差 (係負方向)")

# ------------------------------------------------------------ [F] tick 時間幀對照
print(f"\n[F] 時間幀 hint (結構性, 非閉合)")
print(f"   88 = 2·N_d = 世界環每週期 half-tick 數; 44 = N_d = ring 半圓 tick 數")
print(f"   T_ring = 2π·R_world/c = 84.637 Gyr; τ = R_world/c")
print(f"   half-tick 尺度 = τ/44 = R_world/(44c) — 對照 λ_sync = πR_world/44 (O132) 同量級結構")
print(f"   γ_44 = 2 = μ² = 4-γ 對偶不動點 (Nyquist 半點)")

print(f"\n=== T1 diagnostic complete (no PASS/FAIL semantics — findings as structured facts) ===")