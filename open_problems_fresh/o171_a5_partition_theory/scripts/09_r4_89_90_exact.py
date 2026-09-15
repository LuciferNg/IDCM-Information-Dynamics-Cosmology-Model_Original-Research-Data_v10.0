#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/09 — R4: 89/90 精確化 (m_δW/m_7 到底係咩?)
=========================================================
問題 (docs/03 §6 O171-R4): 4sin(7π/88) = 0.9892260 vs 89/90 = 0.9888889, dev 0.034%
                          — 需確認係精確結構定近似 (O39 成員)。

O39 scripts/07 嘅精確關係:
  m_δW = M₀/2                (O37 漲落)
  m_7  = M₀·2sin(7π/88)      (O34 質量譜 m_n ∝ sin(nπ/88))
  ⇒ m_δW/m_7 = 1/(4sin(7π/88))  ← 呢個係**精確**結構值 (兩個輸入都係結構式)
  而 90/89 = 1/(1−1/90) 係「真空佔比」讀法

本 script 檢定邊個係精確:
  C1 精確比值 (60 dps) + 候選 dev 表
  C2 無理性: 4sin(7π/88) 係咪有理? (分母掃描 + Dirichlet 界比較)
  C3 ★ 密度背景掃描: (n, d) 全掃描, 幾多對命中 < 1e-4?
  C4 反向: γ_7 = 4sin²(7π/88) 嘅結構身份掃描
  C5 裁決 (誠實: 精確 vs 巧合)
"""
import mpmath as mpm
from fractions import Fraction as Fr

mp = mpm.mp; mp.dps = 60
pi, sin, sqrt, nstr, mpf = mp.pi, mp.sin, mp.sqrt, mp.nstr, mp.mpf

ok = 0; tot = 0
def chk(name, cond, note=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
    return cond

B, N_gen, N_d, R, F5, L4, L5, L7, F11 = 4, 3, 44, 11, 5, 7, 11, 29, 89

print("="*80)
print("O171 scripts/09 — R4: 89/90 精確化 (m_δW/m_7)")
print("="*80)

# ---------- C1: 精確比值 ----------
print("\n=== C1: 精確比值 1/(4sin(7π/88)) (60 dps) ===")
s7 = sin(7*pi/88)
ratio = 1/(4*s7)
print(f"  4sin(7π/88)   = {nstr(4*s7, 25)}")
print(f"  m_δW/m_7      = 1/(4sin(7π/88)) = {nstr(ratio, 25)}")
x = 4*s7
print(f"\n  ★ 一致方向比較 (全部候選 = (d−1)/d 同向, 對 4sin(7π/88) = {nstr(x,12)}):")
print(f"    O39 記錄: 4sin(7π/88) ≈ 89/90 = 1 − 1/90,  90 = Σγ_even")
tab = []
for d in range(86, 98):
    v = mpf(d-1)/d
    dev = abs(x - v)/x
    tab.append((dev, d))
    tag = " ← O39 記錄 (真空佔比)" if d == 90 else ""
    print(f"    (d−1)/d = {d-1:>3}/{d:<3} = {nstr(v,18)}   dev = {nstr(dev*100, 10)}%{tag}")
tab.sort()
chk("C1 精確比值算得 (60 dps)", abs(ratio - 1/(4*sin(7*pi/88))) < mpf('1e-50'))
print(f"  → 最近 (d−1)/d = {tab[0][1]-1}/{tab[0][1]} (dev {nstr(tab[0][0]*100,10)}%)")
dev90 = [dv for dv, d in tab if d == 90][0]
rank90c = [d for _, d in tab].index(90) + 1
print(f"  → O39 嘅 d=90 dev = {nstr(dev90*100,10)}% (排第 {rank90c}/{len(tab)})")
chk("C1b d=90 唔係最佳 (有 5 個更好: 93/92/94/91/95)", rank90c > 1, f"(排第 {rank90c})")

# ---------- C2: 無理性 ----------
print("\n=== C2: 4sin(7π/88) 係咪有理? (分母掃描 + Dirichlet 界) ===")
x = 4*s7
best_q, best_dev = None, None
for q in range(1, 2001):
    p = int(mp.nint(x*q))
    if p == 0: continue
    dev = abs(x - mpf(p)/q)
    if best_dev is None or dev < best_dev:
        best_dev, best_q, best_p = dev, q, p
print(f"  最佳有理逼近 (q ≤ 2000): {best_p}/{best_q} = {nstr(mpf(best_p)/best_q,20)}")
print(f"    dev = {nstr(best_dev, 8)}  (相對 {nstr(best_dev/x*100, 8)}%)")
chk("C2 最佳有理逼近 dev > 1e-12 ⇒ 4sin(7π/88) 無理", best_dev > mpf('1e-12'))
print(f"  Dirichlet 界 (q=421): 1/q² ≈ {nstr(mpf(1)/421**2, 6)}")
print(f"  Dirichlet 界 (q=2000): 1/q² ≈ {nstr(mpf(1)/2000**2, 6)}")
d_90 = abs(x - mpf(89)/90)
print(f"  |4sin(7π/88) − 89/90| = {nstr(d_90, 8)}  (相對 {nstr(d_90/x*100,8)}%)")
chk("C2b 89/90 嘅 dev (3.4e-4) **差過** 同分母級別嘅 Dirichlet 典型界 (1/421² ≈ 5.6e-6)",
    d_90/x > mpf(1)/421**2,
    f"⇒ 唔特殊 (隨機有理數都可達)")
print("  ⇒ 結論: 4sin(7π/88) 無理; 89/90 唔可能精確; 而且其貼近程度**唔優於隨機**")

# ---------- C3: 密度背景掃描 ----------
print("\n=== C3: ★ 密度背景掃描 — (n, d) 全掃描 ===")
hits = []
for n in range(1, 89):
    xn = 4*sin(n*pi/88)
    for d in range(2, 3001):
        tgt = mpf(d-1)/d
        dev = abs(xn - tgt)/tgt
        if dev < mpf('1e-4'):
            hits.append((n, d, dev))
print(f"  命中 |4sin(nπ/88) − (d−1)/d| / target < 1e-4 (0.01%) 嘅 (n,d) 對數 = {len(hits)}")
hits.sort(key=lambda t: t[2])
print("  最近 12 對:")
for n, d, dev in hits[:12]:
    star = " ★" if (n == 7 and d == 90) else ""
    print(f"    n={n:>3}, d={d:>4}: dev = {nstr(dev*100, 8)}%{star}")
chk("C3 命中對數少 (值本身罕見) — 但同一 n 內仍有更佳 d (見 C3b/C3c)",
    len(hits) < 50, f"({len(hits)} 對, 全部 n ∈ {{7, 81}} — 即同一值嘅鏡像)")
print(f"  ⚠️ 誠實: 命中少 ≠ 90 特別; 關鍵係**同一 n 內 90 唔係最佳** (C3b/C3c)")
# n=7 專項: 最佳 d
best_d = None
devs = []
for d in range(2, 3001):
    tgt = mpf(d-1)/d
    dev = abs(x - tgt)/tgt
    devs.append((dev, d))
    if best_d is None or dev < best_d[0]: best_d = (dev, d)
devs.sort()
rank90 = [d for _, d in devs].index(90) + 1
dev90 = [dv for dv, d in devs if d == 90][0]
print(f"  n=7 專項: 最佳 d = {best_d[1]} (dev {nstr(best_d[0]*100,8)}%);  "
      f"d=90 (89/90) 排第 {rank90} (dev {nstr(dev90*100,8)}%)")
print(f"  n=7 前 5 名: " + ", ".join(f"d={d}({nstr(dv*100,6)}%)" for dv, d in devs[:5]))
chk("C3b n=7 嘅最佳 d ≠ 90 ⇒ 90/89 唔係最佳命中", best_d[1] != 90)
chk("C3c 至少有 5 個 d 比 90 更貼近 ⇒ 90 冇結構特權", rank90 > 5, f"(排第 {rank90})")
print("  ⇒ d=92 (= Σγ_even+μ² = 2(N_d+μ²)) 同 d=93 (= 2N_d+F₅) 都**有結構身份**且更貼近")
print("     ⇒ 多個結構 d 並列 ⇒ 冇法用「貼近」揀 d ⇒ 該歸類無結構內容")

# ---------- C4: γ_7 結構身份掃描 ----------
print("\n=== C4: γ_7 = 4sin²(7π/88) 嘅結構身份掃描 ===")
g7 = 4*s7**2
print(f"  γ_7 = {nstr(g7, 25)}")
struct = [
    ("11/45 = L₅/(N_d+1)", Fr(11,45)),
    ("1/4 = μ²/8", Fr(1,4)),
    ("N_gen/12.26?", None),
    ("(L₇−4)/102?", None),
    ("1/(2L₄) = 1/14", Fr(1,14)),
    ("F₅/20.44?", None),
    ("(L₄−2)/20.45?", None),
    ("11/(44+1) 同形", Fr(11,45)),
    ("5/20.44", None),
]
for nm, fr in struct:
    if fr is None: continue
    v = mpf(fr.numerator)/fr.denominator
    print(f"    {nm:<24} = {nstr(v,18)}  dev = {nstr(abs(g7-v)/g7*100, 8)}%")
chk("C4 γ_7 冇 <0.05% 結構命中 (除 11/45 = 0.07%)",
    all(abs(g7-mpf(fr.numerator)/fr.denominator)/g7 > mpf('5e-4') for _, fr in struct if fr is not None))

# ---------- C5: 裁決 ----------
print("=== C5: 裁決 ===")
print("  🟢 精確值 = 1/(4sin(7π/88)) (m_δW 同 m_7 兩條結構式之比) — 無理數")
print("  🔴 89/90 = 1−1/90 嘅「真空佔比」讀法 **唔精確** (dev 0.0341%)")
print("  🔴 判別邏輯 (關鍵): m_δW = M₀/2 同 m_7 = M₀·2sin(7π/88) **兩邊都係精確可算**,")
print("     所以 0.0341% 嘅偏差係**真證偽**, 唔係「觀測不確定度」(對比其他成員):")
print("       33/34   : 因子精確有理; 觀測量係擬合 (RMS 0.31%) ⇒ 0.04% 落喺擬合品質內 ✓")
print("       44/45   : 因子精確 = Σγ_odd/Σγ_even = 88/90 恒等 ⇒ 精確 ✓")
print("       55/56   : 因子精確有理; 觀測比 dev 0.0023% ✓")
print("       420/421 : 因子精確有理; 觀測 dev 0.0012% ✓")
print("       89/90   : **兩邊精確可算而唔等** ⇒ 唔可能係該觀測量嘅精確因子 ✗")
print("  🔴 且 89/90 唔係最佳: d ∈ {93, 92, 94, 91, 95} 全部更貼近 (d=93 dev 0.0022%, 16× 好)")
print("     而 d=92 (= Σγ_even+μ²) 同 d=93 (= 2N_d+F₅) 都**有結構身份** ⇒ 無法用貼近揀 d")
print("  🔴 Dirichlet: |4sin(7π/88) − 89/90| = 3.4e-4 差過 1/421² ≈ 5.6e-6 ⇒ 連「接近」都唔特殊")
print("  ⇒ O171-R4 裁決: 89/90 由 🟡 **降級** 為 🔴 (數值巧合, 非精確結構)")
print("     (配分佔比家族由五成員縮為**四成員**: 33/34, 44/45, 55/56, 420/421)")
print("  ⚠️ 註 1: O39 嘅 m_δW/m_7 = 1/(4sin(7π/88)) 本身仍係精確結構 (唔受影響);")
print("           被降級嘅只係「佢屬 N/(N+1) 配分家族」呢個**歸類**。")
print("  ⚠️ 註 2: d = 90 = Σγ_even = F₁₁+1 本身**仍然係有效 sector 計數** (docs/01 §3.1);")
print("           只係冇任何已建立觀測量以 (d−1)/d 精確命中佢 ⇒ 該 sector 暫無成員。")

print()
print(f"RESULT: {ok}/{tot} PASS")
