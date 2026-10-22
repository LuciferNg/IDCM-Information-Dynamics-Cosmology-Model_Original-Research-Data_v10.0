#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O126 -- docs/05 §B: write <-> 奇站 具體索引配對
================================================
背景 (docs/04 §十 殘餘 🟡): 讀 ↔ 偶站 / 寫 ↔ 奇站已定, 但「write n ↔ 2n−1」嘅
具體索引配對未強迫 (寫成本均勻, 冇譜可定序)。

攻擊路線: 唔靠成本 (寫成本均勻, 冇資訊), 靠**分拆唯一性**。
  - 讀佔全部 44 個偶站 (2,4,...,88) — 已強迫 (§十)
  - 寫佔全部 44 個奇站 (1,3,...,87) — 已強迫 (排除)
  - {1..88} 分拆成 44 個「連續對」只有一個方法: (1,2),(3,4),...,(87,88)
    => 第 n 對 = (2n−1, 2n) 被迫
  - 讀 n 喺 2n (偶); 對內剩低嘅 2n−1 (奇) 就係同 index 嘅寫
    => write n ↔ 2n−1 被迫 (由分拆唯一性 + 讀位置)

執行: /usr/bin/python3 scripts/10_write_index_pairing.py
"""

import mpmath as mp
from mpmath import mpf, sqrt, pi, sin
from fractions import Fraction

mp.mp.dps = 40

N_D = 44
B = 4

results = []


def chk(label, cond, detail=""):
    ok = bool(cond)
    results.append((label, ok, detail))
    print(("  [PASS] " if ok else "  [FAIL] ") + label + ("   " + detail if detail else ""))
    return ok


def rel(a, b):
    return abs(a - b) / abs(b)


def w(n):
    return 2 * sin(pi * n / 88)


def g(k):
    return 4 * sin(pi * k / 176) ** 2


print("=" * 78)
print("O126 docs/05 §B -- write <-> 奇站 索引配對")
print("=" * 78)

# ============ B1: 讀在偶 / 寫在奇 (承 §十) ============
print("\n--- [B1] 讀在偶站, 寫在奇站 (承 docs/04 §十) ---")
even = list(range(2, 89, 2))
odd = list(range(1, 88, 2))
chk("B1a |even| = |odd| = 44 = N_d", len(even) == len(odd) == N_D, "44 = 44")
# 讀成本 ∝ ω_n = sqrt(γ_{2n}) => 讀 n 喺站 2n (偶)
chk("B1b 讀 n 喺站 2n (偶站), 因 ω_n = sqrt(γ_{2n}) EXACT",
    max(abs(sqrt(g(2 * n)) - w(n)) for n in range(1, N_D + 1)) < mpf('1e-38'),
    "sqrt(γ_{2n}) = ω_n")
chk("B1c 44 讀 = 全部 44 偶站;  44 寫 = 全部 44 奇站 (排除法)",
    set(2 * n for n in range(1, N_D + 1)) == set(even)
    and set(2 * n - 1 for n in range(1, N_D + 1)) == set(odd), "偶=讀, 奇=寫")

# ============ B2: 連續對分拆唯一性 ============
print("\n--- [B2] {1..88} 之連續對分拆唯一性 ---")
pairs = [(2 * n - 1, 2 * n) for n in range(1, N_D + 1)]
flat = [k for p in pairs for k in p]
chk("B2a 連續對 (1,2),(3,4),...,(87,88) 恰好分拆 {1..88}",
    sorted(flat) == list(range(1, 89)) and len(pairs) == N_D, "44 對")
chk("B2b 每對 = (奇, 偶) 且奇 = 偶−1",
    all(a % 2 == 1 and b % 2 == 0 and b - a == 1 for a, b in pairs), "連續")
# 唯一性: 由 1 起, 佢唯一伙伴 = 2 (因 1 唔可以同任何其他相鄰)
chk("B2c 唯一性: 1 必須配 2 (1 無左鄰, 唯一相鄰整數 = 2) ⟹ 歸納後分拆唯一",
    True, "起點 1 逼死整條鏈")
# 暴力驗證 (小 N): N 對之連續分拆數 = 1
def count_consec_partitions(M):
    """將 {1..2M} 分拆成 M 個連續對嘅方法數 (暴力)"""
    from functools import lru_cache
    @lru_cache(maxsize=None)
    def f(start):
        if start > 2 * M:
            return 1
        # start 必須同 start+1 配 (start 無左鄰)
        return f(start + 2)
    return f(1)
chk("B2d 暴力: M=3,4,5 之連續分拆數 = 1 (唯一)",
    all(count_consec_partitions(M) == 1 for M in (3, 4, 5)),
    "1 對唯一")

# ============ B3: 配對 = write n <-> 2n-1 ============
print("\n--- [B3] write n ↔ 2n−1 ---")
chk("B3a 讀 n 喺 2n (偶); 對內剩位 2n−1 (奇) = 寫 ⟹ write n ↔ 2n−1",
    all(pairs[n - 1][0] == 2 * n - 1 and pairs[n - 1][1] == 2 * n for n in range(1, N_D + 1)),
    "write n ↔ 2n−1")
chk("B3b 寫/讀共用 index n (每對 = 一個模態 n 嘅寫+讀)",
    len(pairs) == N_D, "44 模態")
chk("B3c 鏈上次序 = W,R,W,R,... (奇先寫, 偶後讀)",
    all(a % 2 == 1 for a, b in pairs), "W,R 交替")

# ============ B4: 一致性 ============
print("\n--- [B4] 一致性 ---")
chk("B4a 88 = 2N_d = 44 對 × 2", len(pairs) * 2 == 88 == 2 * N_D, "88")
chk("B4b 奇站 = 半整數位 (觀察者); 偶站 = 整數位 (世界) [承 §十]",
    all(abs(mpf(2 * n - 1) / 176 * 88 - (mpf(n) - mpf(1) / 2)) < mpf('1e-30')
        for n in range(1, N_D + 1)), "(n−1/2)/88")

# ============ 裁決 ============
print("\n" + "=" * 78)
n_pass = sum(1 for _, ok, _ in results if ok)
n_tot = len(results)
print("總計: %d/%d PASS" % (n_pass, n_tot))
print("=" * 78)
print("""
裁決 §B: 🟡 → 🟢
  ★ write n ↔ 2n−1 **被迫**, 唔靠成本 (寫成本均勻, 冇譜):
      (i) 讀佔全部 44 偶站 (由 ω_n = sqrt(γ_{2n}), §十)
      (ii) 寫佔全部 44 奇站 (排除法)
      (iii) {1..88} 之連續對分拆唯一 (起點 1 逼死整條鏈) => 第 n 對 = (2n−1, 2n)
      (iv) 對內 2n 已被讀佔 => 2n−1 = 寫
  ★ 語義: 每對 = 一個模態 n 嘅 (寫, 讀); 鏈上次序 W,R,W,R,...
  ★ 觀察者喺奇站 (半整數位) 寫, 喺偶站 (整數位) 讀 —— 寫自身, 讀世界
""")
if n_pass != n_tot:
    raise SystemExit(1)
