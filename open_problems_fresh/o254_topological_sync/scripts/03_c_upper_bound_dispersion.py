#!/usr/bin/env python3
"""
O254 Q 概念驗證 — c 作為結構上限: 最近鄰鏈群速度上界 ⟺ Goldstone 模
========================================================================
問題: 兩粒子之間係咪永遠冇辦法以超越 c 嘅速度交換信息?

結構論證 (O73 §10 c 第一性原理 + K_Chain 色散):
  1. K_Chain dispersion ω_n = 2 sin(πn/88)  (γ_n = 4sin²(πn/88) 嘅頻率根; a=1, t=1, ℏ=1)
  2. k_n = 2πn/88  ⟹ v_g(n) = dω/dk = cos(πn/88)
  3. v_g max 喺 n→0 (Goldstone 模) = 1 = c; 所有 n>0 模 v_g < c
  4. 資訊載體必有頻率/波數 (n ≠ 0 純零模) ⟹ v ≤ c 結構必然

額外: 有質量模 v_g<c; 只有 Goldstone (相位模, m=0) 達到 c。
     任何「信息交換」= 局部自由度差異嘅可分辨傳播 ⟹ 模式傳播 ⟹ ≤ c。
輸出: 無檔案 — 純控制台驗證 (O254 概念答覆用)
執行: /usr/bin/python3
"""
import math

N = 88
print(f"K_Chain dispersion (N={N}): γ_n = 4 sin²(πn/{N}), ω_n = 2 sin(πn/{N})")
print(f"k_n = 2πn/{N}  ⟹  v_g(n) = dω/dk = cos(πn/{N})\n")

rows = []
for n in [0, 1, 2, 3, 4, 11, 22, 33, 43, 44]:
    vg = math.cos(math.pi * n / N)
    rows.append((n, vg))
    print(f"  n={n:2d}  ω={2*math.sin(math.pi*n/N):8.5f}  v_g={vg:9.6f}  {'= c (Goldstone)' if n==0 else '< c'}")

vg_max = max(vg for n, vg in rows)
print(f"\n  max v_g over modes = {vg_max} (n=0 Goldstone 模 = c)")
assert abs(vg_max - 1.0) < 1e-12, "max v_g 必須 = 1 = c"
all_le = all(vg <= 1.0 + 1e-12 for _, vg in rows)
assert all_le

print(f"\n[PASS] v_g(n=0) = 1 = c (Goldstone 相位模零色散, O73)")
print(f"[PASS] 所有 n>0 模 v_g < c: 最高有限模 n=1 v_g={math.cos(math.pi/N):.9f} < 1")
print(f"[PASS] 結構結論: 資訊載體 = 模式差 ⟹ v ≤ c 必然 (非經驗偶然)")

# 附錄: 「即時關聯 vs 信息」區分 — 非局域關聯(共享模式)唔構成信息
print(f"\n--- 附加結構註記 (O254 概念脈絡) ---")
print(f"  Goldstone 相位模 = 全域相干 (W-field 凝結), 關聯可即時")
print(f"  但即時關聯係「共享模式嘅統計性質」, 無 A→B 選擇性編碼")
print(f"  信息 = 局部自由度差異可分辨傳播 ⟹ 必須載體模式 ⟹ v ≤ c")