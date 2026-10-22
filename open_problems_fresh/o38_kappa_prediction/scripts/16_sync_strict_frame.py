#!/usr/bin/env python3
"""
O38 — 遺留 #1: 44-tone 同步嚴格證明 (Step 1+2: 框架 + 判定)
================================================================
開放問題原句 (docs/01 §7): 「44-tone 同步」嘅嚴格動力學證明
(所有模態同時回相) 未形式化。

嚴格形式化:
  世界 = 44 模態, 頻率 ω_n = ω_scale·sin(πn/88), n = 1..44
  T_sync = 2π/H₀ (O39 數值閉合 84.64 Gyr), ω_scale = 88·H₀
  「模態 n 喺 T 回相」⟺ ω_n·T/(2π) ∈ ℤ
  「所有模態同時回相」⟺ ∃T: ω_n·T/(2π) ∈ ℤ ∀n

  代入 T_sync:
    ω_n·T_sync/(2π) = ω_scale·sin(πn/88)·(2π/H₀)/(2π)
                     = 88·sin(πn/88) × (H₀/H₀) = 88·sin(πn/88)

  ⟹ 回相條件: 88·sin(πn/88) ∈ ℤ, n = 1..44

數學引理 (Niven, 1956): sin(πr) ∈ ℚ ⟺ sin(πr) ∈ {0, ±1/2, ±1}
  88·sin(πn/88) = k ∈ ℤ ⟹ sin(πn/88) = k/88 ∈ ℚ
  ⟹ sin(πn/88) ∈ {0, ±1/2, ±1} (Niven)
  求解 n ∈ [1,44]:
    sin(πn/88) = 1  ⟹ πn/88 = π/2        ⟹ n = 44  ✅
    sin(πn/88) = −1 ⟹ πn/88 = 3π/2       ⟹ n = 132 ∉ [1,44]
    sin(πn/88) = 1/2 ⟹ πn/88 = π/6, 5π/6 ⟹ n = 44/3, 220/3 ∉ ℤ
    sin(πn/88) = −1/2 ⟹ πn/88 = 7π/6, 11π/6 ⟹ n = 308/3, 484/3 ∉ ℤ
    sin(πn/88) = 0  ⟹ n = 0, 176 ∉ [1,44]

  ⟹ 唯一解: n = 44 (最高模態, ω_44 = ω_scale, 88·sin(π/2) = 88 ∈ ℤ)

判定: 「所有 44 模態同時精確回相」數學上不可能 (Niven 禁止),
      唯一精確回相模態 = n = 44 (88 圈)。

本 script: 高精度數值驗證 Niven 判定 (mpmath 80 位)。
"""
from mpmath import mp, mpf, sin, pi, floor
mp.dps = 80

# ═══ 常數 ═══
N_d = 44
omega_ring = mpf("72.59")      # (km/s)/Mpc, O73 已閉合
H0_s = omega_ring * 1000 / (mpf("3.085677581e19") * 1000)
T_sync_s = 2*pi / H0_s        # 秒

print("=" * 72)
print("  O38 遺留 #1: 44-tone 同步 — 嚴格框架 + Niven 判定")
print("=" * 72)

results = []

# ═══ [1] 回相條件表 ═══
print("\n─── [1] 回相條件: phase_n = 88·sin(πn/88) ───")
print(f"  n | 88·sin(πn/88)    | 距最近整數 | 精確回相?")
integer_hits = []
nearest_int = {}
for n in range(1, N_d + 1):
    phase = 88 * sin(pi*n/88)
    nearest = round(phase)
    dist = abs(phase - nearest)
    nearest_int[n] = (nearest, dist)
    is_int = (dist < mpf("1e-60"))
    if is_int:
        integer_hits.append(n)
    flag = "✅ 整數" if is_int else ("~" if dist < mpf("1e-8") else "")
    print(f"  {n:2d} | {float(phase):12.6f} | {float(dist):12.2e} | {flag}")

print(f"\n  ★ 88·sin(πn/88) ∈ ℤ 嘅 n: {integer_hits}")
print(f"  (期望: 淨 n = 44 — Niven 定理唯一解)")
ok1 = integer_hits == [44]
print(f"  {'✅ PASS' if ok1 else '❌ FAIL'} 唯一整數命中 n=44")
results.append(ok1)

# ═══ [2] Niven 引理驗證 ═══
print("\n─── [2] Niven 引理驗證 (sin(πn/88) 有理性) ───")
rational_count = 0
for n in range(1, N_d + 1):
    s = sin(pi*n/88)
    # k/88 有理測試: 用高精度分數逼近誤差
    k = round(s * 88)
    diff = abs(s - k/88)
    if diff < mpf("1e-75"):
        rational_count += 1
        print(f"  n={n}: sin(πn/88) ≈ {k}/88 有理?? diff={float(diff):.2e}")
print(f"  sin(πn/88) 有理命中: {rational_count} (Niven 期望: 僅 n=44)")
ok2 = (rational_count == 1)
print(f"  {'✅ PASS' if ok2 else '❌ FAIL'} 僅 n=44 有理 (sin=1)")
results.append(ok2)

# ═══ [3] 最高模態 n=44 精確回相 ═══
print("\n─── [3] 模態 44 精確回相 (T_sync 內轉 88 圈) ───")
phase44 = 88 * sin(pi*44/88)
print(f"  ω_44·T_sync/(2π) = 88·sin(π·44/88) = 88·sin(π/2) = {float(phase44):.1f} ∈ ℤ")
ok3 = abs(phase44 - 88) < mpf("1e-60")
print(f"  {'✅ PASS' if ok3 else '❌ FAIL'} n=44 轉 88 整圈")
results.append(ok3)

# ═══ [4] 判斷: 精確 44-tone 同步不可能 ═══
print("\n─── [4] 判定 ───")
print(f"  「所有 44 模態同時精確回相」⟺ 88·sin(πn/88) ∈ ℤ ∀n")
print(f"  Niven 定理: sin(πr) ∈ ℚ ⟹ sin(πr) ∈ {{0, ±1/2, ±1}}")
print(f"  解集合 (n ∈ [1,44]): {{44}} — 唯一 n = 44")
print(f"  ⟹ 除 n=44 外全部 43 個模態 88·sin(πn/88) ∉ ℤ")
print(f"  ⟹ 嚴格意義嘅「同時精確回相」數學上唔可能 (Niven)")
ok4 = len(integer_hits) == 1 and integer_hits[0] == 44
print(f"  {'✅ PASS' if ok4 else '❌ FAIL'} 判定成立")
results.append(ok4)

# ═══ [5] 近整數分析 (準同步候選) ═══
print("\n─── [5] 近整數 (準同步結構) ───")
print(f"  88·sin(πn/88) ≈ πn (弦長≈弧長) — 偏差 = 88·sin(πn/88) − πn")
for n in list(range(1, 7)) + [11, 22, 33, 44]:
    phase = 88 * sin(pi*n/88)
    arc = pi * n
    dev = (phase - arc) / arc
    print(f"  n={n:2d}: 88 sin = {float(phase):10.6f} vs πn = {float(arc):10.6f}, dev = {float(dev)*100:+.4f}%")
print(f"  (準同步: n 細時 88·sin(πn/88) ≈ πn — 見 Step 3 弦-弧偏差結構)")

print(f"\n{'='*72}")
print(f"  結果: {sum(results)}/{len(results)} PASS")
print("=" * 72)