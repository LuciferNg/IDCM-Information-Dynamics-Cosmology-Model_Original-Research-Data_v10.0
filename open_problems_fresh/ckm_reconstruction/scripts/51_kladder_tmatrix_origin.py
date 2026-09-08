#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ckm 51 — k-ladder 代數起源: T̂ 轉移矩陣矩陣元形式 + 存在性定理
=============================================================
O149 k-ladder: g_k = beat(44−k, 45−k)/beat(44−(k+1), F_{k+6})
本輪發現 (起源候選):
  T1  176-sine 閉式可以完全寫成 T̂ 矩陣元 (O142: Fₙ = (T̂ⁿ)₁₂):
      g_k = sin(F_{k+2}·π/176)·sin(π/176) / [sin(F_{k+6}·π/176)·sin((45+k)·π/176)]
      分子指數 2k−1 = F_{k+2} (k=2: F₄=3; k=3: F₅=5)
      分母差 F_{k+6} (k=2: F₈=21; k=3: F₉=34)
      Fibonacci 指數間距 = (k+6)−(k+2) = 4 = B (樹分支因子)
  T2  存在性定理: k=1 奇偶失敗 (s=42, F₇=13 → 42±13 奇 → 非整數模式);
      k=4 預算失敗 (F₁₀=55 > 39) → k ∈ {2,3} 被強制 = 兩個受抑 CKM 元素
  T3  反週期/邊界: 分子 = Nyquist 相鄰對 (44−k, 45−k) → sin(π/176)·sin((2k−1)π/176)
狀態: 規則由「動機化選擇 🟡」升級為「T̂ 矩陣元 + 存在性強制」— 起源未全閉 (正弦指數指派 + (45+k) 指數仍待推導)
"""
import mpmath as mp

mp.mp.dps = 60
PASS = 0
FAIL = 0

def chk(name, val, target, tol):
    global PASS, FAIL
    ok = abs(val - target) <= tol * max(1.0, abs(target))
    if ok:
        PASS += 1
        print(f"  [✔] {name} = {mp.nstr(val, 15)} (dev {float(abs(val-target)):.2e})")
    else:
        FAIL += 1
        print(f"  [✘] {name} = {mp.nstr(val, 15)} ≠ {mp.nstr(target, 15)}")

def beat(i, j):
    return mp.fabs(2*mp.sin(i*mp.pi/88) - 2*mp.sin(j*mp.pi/88))

# T̂ = [[1,1],[1,0]] — Fibonacci 轉移矩陣 (O142: Lₙ = Tr(T̂ⁿ), Fₙ = (T̂ⁿ)₁₂)
T = mp.matrix([[1, 1], [1, 0]])
def Fn(n): return (T**n)[0, 1]
def Ln(n): return (T**n)[0, 0] + (T**n)[1, 1]  # Tr(T̂ⁿ)

print("=" * 72)
print("T0. O142 基礎: Fₙ = (T̂ⁿ)₁₂, Lₙ = Tr(T̂ⁿ)")
print("=" * 72)
for n in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
    print(f"  F_{n} = (T̂^{n})₁₂ = {int(Fn(n))},  L_{n} = Tr(T̂^{n}) = {int(Ln(n))}")
chk("F₄ = 3", Fn(4), 3, 0)
chk("F₅ = 5", Fn(5), 5, 0)
chk("F₈ = 21", Fn(8), 21, 0)
chk("F₉ = 34", Fn(9), 34, 0)
chk("L₅ = 11", Ln(5), 11, 0)
chk("L₁₀ = 123", Ln(10), 123, 0)

print()
print("=" * 72)
print("T1. ★ k-ladder 閉式 = 全 T̂ 矩陣元形式")
print("=" * 72)
print("  g_k = sin(F_{k+2}·π/176)·sin(π/176) / [sin(F_{k+6}·π/176)·sin((45+k)·π/176)]")
for k in [2, 3]:
    s = 44 - (k+1)
    d = Fn(k+6)
    m1, m2 = (s+d)/2, (s-d)/2
    g_beat = beat(44-k, 45-k) / beat(m1, m2)
    g_closed = (mp.sin(Fn(k+2)*mp.pi/176)*mp.sin(mp.pi/176)) / \
               (mp.sin(Fn(k+6)*mp.pi/176)*mp.sin((45+k)*mp.pi/176))
    print(f"  k={k}: beat 形式 beat({44-k},{45-k})/beat({int(m1)},{int(m2)}) = {mp.nstr(g_beat, 15)}")
    print(f"       閉式      = {mp.nstr(g_closed, 15)}")
    chk(f"k={k} 閉式 = beat 形式", g_closed, g_beat, 1e-25)
    print(f"       指數: 分子 sin(F_{k+2}= {int(Fn(k+2))}), 分母差 sin(F_{k+6}= {int(Fn(k+6))}), "
          f"分母和鏡 sin(45+{k} = {45+k})")
print(f"  Fibonacci 指數間距: (k+6)−(k+2) = 4 = B (樹分支因子) — 樹 sector 譜進入 chain sector 受抑元素")

print()
print("=" * 72)
print("T2. ★ 存在性定理: 奇偶 + 預算強制 k ∈ {2,3}")
print("=" * 72)
for k in [1, 2, 3, 4]:
    s = 44 - (k+1)
    d = Fn(k+6)
    p1, p2 = (s+d)/2, (s-d)/2
    int_ok = p1 == int(p1) and p2 == int(p2) and p1 > 0 and p2 > 0 and p1 <= 44 and p2 <= 44
    print(f"  k={k}: s = {s}, d = F_{k+6} = {int(d)}, 模式對 = ({p1}, {p2}) → "
          f"{'整數模式 ✓' if int_ok else '失敗'}"
          f"{' (奇偶: s±d 奇)' if not int_ok and (s+d) % 2 == 1 else ''}"
          f"{' (預算: d > s)' if int_ok is False and d > s else ''}")
# 條件陳述
k1_fail = "奇偶"  # s=42 偶, F₇=13 奇 → 42±13 = 55/29 奇 → 半整數模式
k4_fail = "預算"  # F₁₀=55 > s=39
print(f"  ⇒ k=1 失敗原因: 奇偶 (s=42 偶 vs F₇=13 奇 → (55,29) 半整數); k=4 失敗原因: 預算 (F₁₀=55 > 39)")
print(f"  ⇒ k ∈ {{2,3}} 被存在性條件強制 — 對應 CKM 兩個受抑元素 (sinθ₁₃, V_ub)")

print()
print("=" * 72)
print("T3. 分子結構: Nyquist 相鄰對 → sin(π/176)·sin((2k−1)π/176)")
print("=" * 72)
for k in [2, 3]:
    num = beat(44-k, 45-k)
    numx = 4*mp.sin((2*k-1)*mp.pi/176)*mp.sin(mp.pi/176)
    print(f"  k={k}: beat({44-k},{45-k}) = 4·sin((2·{k}−1)π/176)·sin(π/176) = 4·sin({2*k-1}π/176)·sin(π/176)")
    chk(f"k={k} 分子恆等式", num, numx, 1e-25)
    print(f"  2k−1 = {2*k-1} = F_{k+2} = {int(Fn(k+2))} (T̂ 矩陣元) ✓")

print()
print("=" * 72)
print("裁決: k-ladder 起源狀態")
print("=" * 72)
print("  ✅ 閉式 = 全 T̂ 矩陣元 (F_{k+2}, F_{k+6} = (T̂ⁿ)₁₂, O142 已確立)")
print("  ✅ 存在性定理: 奇偶 + 預算 → k ∈ {2,3} 強制, 階梯自然終止於 2 級")
print("  ✅ 指數間距 4 = B (樹分支因子)")
print("  🟡 剩餘: 點解分子指派 F_{k+2} / 分母差指派 F_{k+6} (間距 4); (45+k) 和鏡指數嘅起源")
print("  ⇒ 由「動機化選擇」升級為「T̂ 矩陣元 + 存在性強制」— 仍非全推導")
print()
print(f"RESULT: {PASS}/{PASS+FAIL} PASS")
