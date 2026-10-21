#!/usr/bin/env python3
"""
O257 scripts/13 — R5: 結合 R4 結論嘅新事實判定 (2026-10-21)
==========================================================
R4 已判死: 1/76 log10 修正 = 後驗凑合 (校準最優 1/75, O66 circular)。

R5 新事實 (reprobe):
  A. 無 log root 形式 M_comp = M_pl·10^{1/x}/(88³/2):
     x=75 dev 0.1075% / x=76 dev 0.0671% / x=77 dev 0.0277% /
     x=78 dev 0.0106%  ← 最優! / x=79 dev?   x*= 77.72
     → 78 = N−2F₅ = 88−10 = log 底 10=2F₅ 嘅補數 (R1 身份!)
     → 76 = N−hop_max 唔係 root 形式最優 — 又一個後驗揀值
  B. 主項 10^{-1/γ₆} vs 校準: dev −3.03% (唔係「接近閉合」)
     ratio gap: (M_cal−M_main)/M_main = 0.031289, 1/gap = 31.960 ≈ 32 = N_d−12? (dev 0.12%)

問題:
  1. 78 喺 root 次數帶內有幾「唯一」? (look-elsewhere: x 帶內全部近命中?)
  2. 78 = N−2F₅ 係咪真 operator 身份 (2F₅ = log 底 = hop 週期)?
     定係同 76 一樣係帶內揀值?
  3. 主項缺口 ≈ 32 = N_d−hop_max 又係 hop 補數家族 — 有冇獨立機制?

判準: 密度閘 (帶內近命中數) + MC null + look-elsewhere。
"""
import mpmath as mp
mp.mp.dps = 50
import random

M_pl = mp.mpf("1.220910e19")
M_cal = mp.mpf("3.6909e13")
g6 = 4*mp.sin(6*mp.pi/88)**2
inv_g6 = 1/g6
target = mp.log10(M_pl/M_cal)

print("="*72)
print("O257 scripts/13 — R5: root 次數 78 vs 76 + 主項缺口")
print("="*72)
print(f"1/γ₆ = {mp.nstr(inv_g6, 16)}")
print(f"target log10(M_pl/M_cal) = {mp.nstr(target, 16)}")
print(f"1/γ₆ − target = {mp.nstr(inv_g6-target, 16)}  (x* = {mp.nstr(1/(inv_g6-target), 10)})")

# ── A. root 形式帶寬掃描 + look-elsewhere ──
print("\n[A] 無 log root 形式 M = M_pl·10^(1/x)/(88³/2): 帶內掃描")
N3 = mp.mpf(88)**3/2
results = []
for x in range(60, 101):
    M = M_pl * mp.power(10, mp.mpf(1)/x) / N3
    dev = (M - M_cal)/M_cal*100
    results.append((x, dev))
best = min(results, key=lambda t: abs(t[1]))
print(f"  帶 [60,100] 最優: x={best[0]} dev {mp.nstr(best[1], 8)}%")
for x, dev in results:
    mark = " ★" if x in (76, 78) else ""
    print(f"    x={x}: dev {mp.nstr(dev, 8)}%{mark}")

# 帶內近命中統計 (look-elsewhere: 幾多個 x 喺 ±0.05%?)
within005 = [x for x, dev in results if abs(dev) < 0.05]
within01 = [x for x, dev in results if abs(dev) < 0.1]
print(f"\n  帶 [60,100]: |dev|<0.05% → {len(within005)} 個 x: {within005}")
print(f"  帶 [60,100]: |dev|<0.1%  → {len(within01)} 個 x: {within01}")

# x=78 vs x=76 判別
d78 = abs(dict(results)[78])
d76 = abs(dict(results)[76])
print(f"  |dev(78)| = {mp.nstr(d78,8)}%  vs  |dev(76)| = {mp.nstr(d76,8)}%")
print(f"  78 優於 76 嘅改善: {mp.nstr(abs(d76-d78),8)}% — 帶寬級 (0.05%) 內")
print(f"  → 分辨力: 若改善 ≪ 帶內散佈, 78 唔係「唯一」, 只係另一個帶內值")

# MC null: 隨機 target 嘅最優 x 分布
print("\n  MC null: 隨機 target 喺帶內最優 x 分布 (20000 抽)")
random.seed(25713)
cnt_best = {x: 0 for x in range(60, 101)}
for _ in range(20000):
    t = mp.mpf(random.uniform(5.0, 6.0))  # 隨機 log10 比 (接近實際 5.52)
    best_x = min(range(60, 101), key=lambda x: abs((inv_g6 - mp.mpf(1)/x) - t))
    cnt_best[best_x] += 1
p78 = cnt_best[78]/20000*100
p76 = cnt_best[76]/20000*100
print(f"  最優 x=78 出現率: {p78:.2f}%   最優 x=76 出現率: {p76:.2f}%")
print(f"  → 若 P(78) 唔異常高, target 揀 78 冇信息量")

# ── B. log 底對偶: 78 = N−2F₅ ──
print("\n[B] 78 = N−2F₅ = 88−10 (log 底身份對偶?)")
print("  R1: log10 = log_{2F₅} (ν hop 通道週期 N=10)")
print("  78 = N − 2F₅; 76 = N − hop_max (12)")
F5 = 5
cand = [
    (88-2*F5, "N−2F₅ (88−10)"),
    (88-12, "N−hop_max (88−12)"),
    (88-11, "N−L₅ (88−11)"),
    (88-8, "N−2B (88−8)"),
    (88-9, "N−9 (88−9)"),
    (88-13, "N−F₇ (88−13)"),
]
print(f"  校準最優 x* = {mp.nstr(1/(inv_g6-target), 10)}")
for v, name in cand:
    print(f"    {name} = {v}")
print(f"  x*=77.72: 最近結構候選 = 78 (N−2F₅) dev {mp.nstr(abs((inv_g6-mp.mpf(1)/78)-target)/target*100, 6)}%")

# 結構池 x 掃描: 邊啲結構數 x 令 1/γ₆−1/x 近 target?
print("\n  結構池 x 對 log10 形式: dev vs target")
pool_x = [76, 78, 75, 77, 74, 79, 80, 84, 87, 88, 90, 44, 60, 29, 47, 123]
for x in sorted(set(pool_x)):
    dev = abs((inv_g6 - mp.mpf(1)/x) - target)/target*100
    print(f"    x={x}: dev {mp.nstr(dev, 6)}%")

# ── C. 主項缺口 32 ──
print("\n[C] 主項缺口: (M_cal − M_main)/M_main")
M_main = M_pl * mp.power(10, -inv_g6)
gap = (M_cal - M_main)/M_main
invgap = 1/gap
print(f"  M_main dev vs cal: {mp.nstr((M_main-M_cal)/M_cal*100, 8)}%")
print(f"  gap = {mp.nstr(gap, 14)}   1/gap = {mp.nstr(invgap, 12)}")
for v, name in [(32, "32 = N_d−12 = N_d−hop_max"), (44-12, "N_d−12"),
                (33, "33"), (88-55, "88−55=F₁₀"), (22, "22"), (31, "31"),
                (88-56, "88−56"), (44-13, "44−13=F₇"), (90-58, "90−58"), (176/5.5, "176/5.5")]:
    dev = abs(invgap - v)/v*100
    flag = " ←" if dev < 0.5 else ""
    print(f"    {name} = {v}: dev {mp.nstr(dev, 5)}%{flag}")

# 帶寬對照: 主項缺口 3% 有冇 operator 地位?
print(f"\n  → 主項 dev 3.03%: 量級閉合 (10⁻¹/γ⁶), 唔係精確閉合")
print(f"  → 1/gap ≈ 31.96 ≈ 32 (N_d−hop_max), dev 0.12% — 近對偶, 同上族")

print("\n" + "="*40)
print("R5 判定: 78 = N−2F₅ 係 root 形式帶內最優, 但需 look-elsewhere")