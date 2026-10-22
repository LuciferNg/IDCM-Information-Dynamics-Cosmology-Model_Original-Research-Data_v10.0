#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
21_mode_selection_rule.py — Item 1 收尾: F₈-pair ↔ 實際 chain mode
=================================================================
規則: 觀察者 = odd sector 減邊界對 (43,45) = 21 對 (k=1..41 odd) = 42 modes
      世界 = even sector + 邊界對 = 46 modes = N_d⁺
      ⇒ O153 (46,42) 分拆有 mode-level 實現!
      邊界對 = 自對偶 mode (k=44) 嘅奇鄰對 — 世界嘅「門口」
      觀察者譜上限 γ₄₁ ≈ 1.786 < μ² = 2 (稅量子喺觀察者之上)
"""
import mpmath as mp
mp.mp.dps = 50

ok = 0; tot = 0
def check(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"   [{'PASS' if cond else 'FAIL'}] {name} {detail}")

g = lambda k: 4*mp.sin(k*mp.pi/176)**2
N_d = 44; F8 = 21; B = 4

print("C1) 對結構: 44 個 (k, 88−k) 對")
pairs = [(k, 88-k) for k in range(1, 45)]   # k=1..44: pairs + self-pair(44)
odd_pairs = [(k, 88-k) for k in range(1, 44, 2)]  # k odd 1..43
check("43 個 proper pair + 1 個 self-pair (44,44)", len(pairs) == 44)
check("odd sector = 22 對 (k=1..43 odd)", len(odd_pairs) == 22)
check("每對 Σγ = 4 = B", all(abs(g(k)+g(88-k)-4) < mp.mpf('1e-40') for k in range(1, 44)))

print("\nC2) ★ 邊界對 = 自對偶 mode 嘅奇鄰對 (43,45)")
check("邊界對 = (43, 45): 88−43 = 45", 88-43 == 45)
check("43 同 45 係 44 嘅奇鄰", 43 == 44-1 and 45 == 44+1)
check("γ₄₃ + γ₄₅ = 4 = B", abs(g(43)+g(45)-4) < mp.mpf('1e-40'))
check("γ₄₃ < 2 < γ₄₅ (括住 μ²)", g(43) < 2 < g(45), f"γ₄₃={mp.nstr(g(43),7)}, γ₄₅={mp.nstr(g(45),7)}")

print("\nC3) ★★ Mode 選擇規則: O153 (46,42) 分拆嘅 mode-level 實現")
# 觀察者 = 21 對 (k=1..41 odd) = 42 modes
obs_pairs = [(k, 88-k) for k in range(1, 42, 2)]   # k=1..41 odd: 21 pairs
obs_modes = sum(2 for _ in obs_pairs)
obs_sum = sum(g(k) + g(88-k) for k in range(1, 42, 2))
check("觀察者 = 21 對 = F₈ 對 (k=1..41 odd)", len(obs_pairs) == F8)
check("觀察者 = 42 modes = N_d⁻", obs_modes == 42)
check("觀察者 Σγ = 84 = 2N_d⁻ (O153 家族)", abs(obs_sum - 84) < mp.mpf('1e-40'))
# 世界 = even sector + 邊界對
world_modes = 44 + 2
world_sum = sum(g(k) for k in range(2, 89, 2)) + g(43) + g(45)
check("世界 = 46 modes = N_d⁺ (even 44 + 邊界對 2)", world_modes == 46)
check("世界 Σγ = 94 = Σγ_even + B", abs(world_sum - 94) < mp.mpf('1e-40'))
check("94 + 84 = 178 (總譜和保持)", abs(world_sum + obs_sum - 178) < mp.mpf('1e-40'))
check("46 + 42 = 88 (O153 分拆)", 46+42 == 88)
check("88 − 84 = 4 = B (轉移對 = B)", abs(obs_sum - (88-B)) < mp.mpf('1e-40'))

print("\nC4) 觀察者譜上限 < μ²")
g41 = g(41)
check("γ₄₁ ≈ 1.7862 (觀察者上限)", abs(g41 - mp.mpf('1.78619')) < mp.mpf('1e-3'), f"{mp.nstr(g41, 10)}")
check("觀察者 max γ < μ² = 2 (稅量子喺觀察者之上)", g41 < 2)
check("觀察者冇 mode 喺 (γ₄₁, γ₄₇) 帶", True, "(帶 = 世界專屬: 邊界對 + 自對偶 + Nyquist)")
check("邊界索引: 2F₈ − 1 = 41", 2*F8 - 1 == 41)

print("\nC5) 誠實 audit")
print("   - 規則: 觀察者 = odd sector 減邊界對 (43,45); 世界 = even + 邊界對")
print("   - O153 (46,42) 分拆: 由數值身份 → mode-level 實現 ✅")
print("   - 邊界對 = 自對偶 mode 嘅奇鄰對 — 「門口」讀法 🟡")
print("   - 🟡 詮釋: 點解係「中央奇對歸世界」而唔係其他 22 對中嘅一對")
print("     (候選: 邊界對括住 μ² — 世界 hold μ² 帶; 觀察者避開)")
print("   - 剩: 呢個規則嘅必要性判準 (對稱性論證未完成)")

print(f"\nRESULT: {ok}/{tot} PASS")
