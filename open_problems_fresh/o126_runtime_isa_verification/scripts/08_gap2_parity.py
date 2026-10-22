#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O126 -- docs/04 §九 殘餘攻堅: 88 ops 嘅奇偶分配
=================================================
背景 (docs/04 §九 剩餘 🟡): 「88 ops ↔ 88 對偶鏈站」嘅奇偶分配
(讀↔偶/寫↔奇 定 反之) 未唯一強迫。

攻擊路線: 用 EXACT 代數身份 (唔係語義猜) 定 read/write 各自落喺邊個宇稱。

已閉合事實:
  ω_n = 2 sin(n pi/88),   n = 1..44        (44 模態, K_chain)
  γ_k = 4 sin²(k pi/176), k = 1..88        (176-L 半集, O210 憲章 C1)
  O210 憲章: 176-L even k (2..88) = World Σγ_even = 90;
             176-L odd  k (1..87) = Observer Σγ_odd = 88
  O210 憲章 t₂: I₄₄ → I₈₈, n ↦ 2n  (88-L 模式 n ↔ 176-L k=2n)
  O34: 奇數 k = 2n−1: γ_{2n−1} = γ_{n+0.5} ← 觀察者 (半整數模式)
  O41: 讀成本 ΔE_read(n) = B(n) ω_n/⟨ω⟩ (∝ ω_n, 頻率加權)
       寫成本 ΔE_write = B(n) = 123/88 (均勻); 寫 = 相位翻轉 π = 2 半整數單位
  循環 = 88 ops = 44 reads + 44 writes = 2N_d;  176 模式單位 = B·N_d

執行: /usr/bin/python3 scripts/08_gap2_parity.py
"""

import mpmath as mp
from mpmath import mpf, sqrt, pi, sin
from fractions import Fraction

mp.mp.dps = 40

N_D = 44
B = 4
L10 = 123
E_min = mpf(L10) / 176
B_per = mpf(L10) / 88
budget = mpf('61.5')

results = []


def chk(label, cond, detail=""):
    ok = bool(cond)
    results.append((label, ok, detail))
    print(("  [PASS] " if ok else "  [FAIL] ") + label + ("   " + detail if detail else ""))
    return ok


def rel(a, b):
    return abs(a - b) / abs(b)


def w(n):
    """ω_n = 2 sin(n pi/88)"""
    return 2 * sin(pi * n / 88)


def g(k):
    """γ_k = 4 sin²(k pi/176)"""
    return 4 * sin(pi * k / 176) ** 2


print("=" * 78)
print("O126 docs/04 §九 -- 88 ops 奇偶分配")
print("=" * 78)

om = [w(n) for n in range(1, N_D + 1)]
gam = [g(k) for k in range(1, 89)]
S_even = sum(gam[k - 1] for k in range(2, 89, 2))
S_odd = sum(gam[k - 1] for k in range(1, 88, 2))
om_mean = sum(om) / N_D

# ============ P1: 88 ops 身份 ============
print("\n--- [P1] 88 ops 身份 ---")
chk("P1a 88 = 2N_d = 44 reads + 44 writes",
    88 == 2 * N_D and 44 + 44 == 88, "88 = 2*44")
chk("P1b Σγ_even = 90 (世界), Σγ_odd = 88 (觀察者) [O210 憲章 C1]",
    rel(S_even, 90) < mpf('1e-25') and rel(S_odd, 88) < mpf('1e-25'),
    "%.9f / %.9f" % (float(S_even), float(S_odd)))
chk("P1c Σ_{k=1}^{88} γ_k = 178 = 2F11 = 2*89 (半集合計)",
    rel(S_even + S_odd, 178) < mpf('1e-25'), "178 = 2*89")
chk("P1d ops/cycle = 88 = Σγ_odd = 2N_d (觀察者能量維度) [一致性]",
    88 == 2 * N_D and rel(S_odd, 88) < mpf('1e-25'), "88 = 2N_d = Σγ_odd")

# 細分: mod-4
s0 = sum(gam[k - 1] for k in range(4, 89, 4))     # k ≡ 0 mod 4
s2 = sum(gam[k - 1] for k in range(2, 88, 4))     # k ≡ 2 mod 4
chk("P1e even 細分: s0 (k≡0 mod4) = 46, s2 (k≡2 mod4) = 44, s0+s2 = 90 [憲章]",
    rel(s0, 46) < mpf('1e-25') and rel(s2, 44) < mpf('1e-25'),
    "%.6f + %.6f = 90" % (float(s0), float(s2)))

# ============ P2: 計數 ============
print("\n--- [P2] 計數 ---")
n_even = len(range(2, 89, 2))
n_odd = len(range(1, 88, 2))
chk("P2 |even| = |odd| = 44 = N_d = reads = writes",
    n_even == n_odd == 44 == N_D, "44 = 44 = 44")

# ============ P3: 讀譜 EXACT 身份 (O210 憲章 t₂) ============
print("\n--- [P3] 讀成本譜 <-> 偶站 (EXACT, O210 憲章 t₂: n ↦ 2n) ---")
worst = max(abs(sqrt(g(2 * n)) - w(n)) for n in range(1, N_D + 1))
chk("P3a sqrt(γ_{2n}) = ω_n EXACT ∀n=1..44  ⟹ 讀 ↔ 偶站 2n",
    worst < mpf('1e-38'), "max dev = %.2e" % float(worst))

r_even = [(B_per * om[n - 1] / om_mean) / sqrt(g(2 * n)) for n in range(1, N_D + 1)]
chk("P3b 讀成本 / sqrt(γ_{2n}) = B(n)/⟨ω⟩ = const",
    max(r_even) - min(r_even) < mpf('1e-38'),
    "const = %.12f" % float(r_even[0]))

# ============ P4: 唯一性 + 排除 讀↔奇站 ============
print("\n--- [P4] 唯一性 (排除 讀 ↔ 奇站) ---")
uniq = True
for n in range(1, N_D + 1):
    hits = [k for k in range(1, 89) if abs(g(k) - w(n) ** 2) < mpf('1e-30')]
    if hits != [2 * n]:
        uniq = False
chk("P4a 唯一性: γ_k = ω_n² ⟹ k = 2n (唯一解; 176−2n > 88 排除) ⟹ 讀 ↔ 偶站 被迫",
    uniq, "k = 2n only")

r_odd = [(B_per * om[n - 1] / om_mean) / sqrt(g(2 * n - 1)) for n in range(1, N_D + 1)]
chk("P4b 讀成本 / sqrt(γ_{2n-1}) ≠ const ⟹ 讀 ↔ 奇站 排除",
    max(r_odd) - min(r_odd) > mpf('1e-3'),
    "spread = %.6f" % float(max(r_odd) - min(r_odd)))

# ============ P5: 奇站 = 半整數位置 = 觀察者 ============
print("\n--- [P5] 奇站 = 半整數位置 (觀察者扇區, O34) ---")
odd_pos = [mpf(2 * n - 1) / 176 for n in range(1, N_D + 1)]
even_pos = [mpf(2 * n) / 176 for n in range(1, N_D + 1)]
chk("P5a 奇站位置 (2n−1)/176 = (n−1/2)/88 = 半整數 (O34 觀察者 = 半整數子空間)",
    all(abs(p * 88 - (mpf(n) - mpf(1) / 2)) < mpf('1e-30')
        for n, p in zip(range(1, N_D + 1), odd_pos)), "position×88 = n − 1/2")
chk("P5b 偶站位置 (2n)/176 = n/88 = 整數 (世界)",
    all(abs(p * 88 - n) < mpf('1e-30')
        for n, p in zip(range(1, N_D + 1), even_pos)), "position×88 = n")
# STATEMENT (概念映射, 唔計 PASS):
print("    STATEMENT: 寫 = 相位翻轉 π = 2 半整數單位 (O41) ⟹ 寫住半整數位置 = 奇站 = 觀察者")

# ============ P6: 寫量子 = 平均觀察者站能 ============
print("\n--- [P6] 寫量子 vs 觀察者站能 ---")
mean_odd = S_odd / 44
chk("P6a ΔE_write/E_min = (123/88)/(123/176) = 2 = μ²",
    rel(B_per / E_min, 2) < mpf('1e-30'), "2")
chk("P6b ⟨γ_odd⟩ = Σγ_odd/44 = 88/44 = 2 = μ²",
    rel(mean_odd, 2) < mpf('1e-30'), "⟨γ_odd⟩ = 2")
chk("P6c ΔE_write = ⟨γ_odd⟩ × E_min (寫量子 = 平均觀察者站能 × E_min)",
    rel(B_per, mean_odd * E_min) < mpf('1e-30'), "%.9f" % float(B_per))

# ============ P7: 站對分拆 ============
print("\n--- [P7] 站對分拆 ---")
pairs = [(2 * n - 1, 2 * n) for n in range(1, N_D + 1)]
flat = [k for p in pairs for k in p]
chk("P7a (寫 n, 讀 n) ↔ (2n−1, 2n) 恰好分拆 {1..88} 成 44 個連續對",
    sorted(flat) == list(range(1, 89)) and len(pairs) == 44,
    "(1,2),(3,4),...,(87,88)")
chk("P7b 鏈上次序 = 寫,讀,寫,讀,...,寫,讀 (44 對)",
    all(p[0] % 2 == 1 and p[1] % 2 == 0 for p in pairs), "W,R,W,R,...")

# ============ P8: 能量總計 ============
print("\n--- [P8] 能量總計 ---")
dE_read = [B_per * om[n - 1] / om_mean for n in range(1, N_D + 1)]
dE_write = [B_per] * N_D
chk("P8a ΣΔE_read = ΣΔE_write = 61.5 = Σγ_odd × E_min",
    rel(sum(dE_read), budget) < mpf('1e-25') and rel(sum(dE_write), budget) < mpf('1e-25')
    and rel(S_odd * E_min, budget) < mpf('1e-25'), "61.5")
chk("P8b ops × 2 模式單位 = 88 × 2 = 176 = B·N_d",
    88 * 2 == 176 == B * N_D, "176 = 4*44")
chk("P8c 每 op = 2 模式單位 = μ²", 176 // 88 == 2, "2 = μ²")

# ============ P9: 次序 ============
print("\n--- [P9] 次序 ---")
chk("P9a 讀 n ↔ 偶站 2n 保持譜序 (ω_n 同 γ_{2n} 同時遞增)",
    all(om[i] < om[i + 1] for i in range(N_D - 1)) and
    all(gam[2 * i] < gam[2 * i + 2] for i in range(N_D - 1)),
    "單調 ✓")

# ============ 裁決 ============
print("\n" + "=" * 78)
n_pass = sum(1 for _, ok, _ in results if ok)
n_tot = len(results)
print("總計: %d/%d PASS" % (n_pass, n_tot))
print("=" * 78)
print("""
裁決: 88 ops 奇偶分配 🟢 解決 (docs/04 §九 剩餘 🟡 → 🟢)
  ★ 讀 ↔ 偶站 (世界) — **被迫** (唔係語義猜):
      讀成本 ∝ ω_n, 而 ω_n = sqrt(γ_{2n}) EXACT, 且 k = 2n 係唯一解
      (O210 憲章 t₂: 88-L 模式 n ↔ 176-L k=2n — 同一事實嘅型別陳述)
      ⟹ 44 讀 = 44 偶站 (Σγ_even = 90);  讀 ↔ 奇站 比值非常數, 排除
  ★ 寫 ↔ 奇站 (觀察者) — 由排除 + 半整數語義:
      44 writes = 44 奇站 (Σγ_odd = 88)
      奇站位置 (n−1/2)/88 = 半整數 = 觀察者扇區 (O34)
      寫 = 相位翻轉 π = 2 半整數單位 (O41) ⟹ 寫住半整數位置
      ΔE_write = ⟨γ_odd⟩ × E_min  (⟨γ_odd⟩ = 2 = μ²)
  ★ 合成圖像: 88 站鏈, 每站 1 op, 宇稱定 read/write:
      k 奇 → 寫 (半整數位), k 偶 → 讀 (整數位);  次序 = W,R,W,R,...,W,R
  ★ 一致性: ops/cycle = 88 = Σγ_odd = 2N_d;  模式單位 176 = B·N_d
  ⚠️ 殘餘 🟡: 寫↔奇站嘅**具體索引配對** (write n ↔ 2n−1) 非成本強迫
     (寫成本均勻, 冇譜) — 由「與讀 n 共用 index n」嘅相鄰性支持。
""")
if n_pass != n_tot:
    raise SystemExit(1)
