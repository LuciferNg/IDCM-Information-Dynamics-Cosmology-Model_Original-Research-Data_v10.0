#!/usr/bin/env python3
"""
O257 scripts/12 — KILLER TEST: 1/76 係咪後驗揀值? (2026-10-21)
================================================================
調律者: 「76平方根10有湊數可能」+ P6 docs/02: 「n=71..81 數值窗
全部 0.003-0.06% 近——76 唯一性靠 operator 身份, 唔係數值唯一」

Killer test 設計:
  A. 用「校準 target」(獨立觀測: M_cal = 3.6909e13, 唔係 O66 公式值)
     target_cal = log10(M_pl/M_cal) = 5.5195478...
     掃 x ∈ [50,100]: 1/γ₆−1/x 邊個最準?
     → 若 1/75 比 1/76 更準, 則「76」唔係數值最優 (後驗揀值坐實)
  B. hop 階梯補數族: 88−x for x∈{1,4,8,11,12} = {87,84,80,77,76}
     呢啲修正項全唔全近 target? (若 80/77 都近 → 唔係「hop_max 唯一」)
  C. 「76 身份」是否事前? hop_max=12 係 O179 事前閉合, 但「點解
     M_comp 修正要揀 hop_max 補數而唔係 hop 階梯其他元素」—
     若所有 hop 補數同級命中, 揀 hop_max 就係後驗
  D. O66 公式 vs 校準: M_comp 公式值 3.68898e13 vs 校準 3.6909e13
     差 0.052% — 呢個差本身就喺「1/75 vs 1/76」嘅分辨能力之下
"""
import mpmath as mp
mp.mp.dps = 60

B, Nd, N, Ngen = 4, 44, 88, 3

def gamma(n, NN=N):
    return 4 * mp.sin(n * mp.pi / NN) ** 2

print("=" * 72)
print("O257 scripts/12 — KILLER TEST: 1/76 係咪後驗揀值?")
print("=" * 72)

g6 = gamma(6)
inv6 = 1/g6
M_pl = mp.mpf("1.2209e19")
M_cal = mp.mpf("3.6909e13")
M_o66 = mp.mpf("3.6890e13")

target_cal = mp.log10(M_pl/M_cal)
target_o66 = mp.log10(M_pl/M_o66)
print(f"target_cal (校準) = {mp.nstr(target_cal, 14)}  (M_cal = 3.6909e13)")
print(f"target_o66 (公式) = {mp.nstr(target_o66, 14)}  (M_o66 = 3.6890e13)")
print(f"1/γ₆ = {mp.nstr(inv6, 14)}")
print()

# ── A. 校準 target 掃 x ──
print("[A] 用校準 target 掃 x∈[50,100]: 1/γ₆−1/x 最準係邊個?")
rows = []
for x in range(50, 101):
    v = inv6 - 1/mp.mpf(x)
    dev_cal = abs(v - target_cal)/target_cal*100
    dev_o66 = abs(v - target_o66)/target_o66*100
    rows.append((x, v, dev_cal, dev_o66))
rows.sort(key=lambda r: r[2])
print("  最準 10 個 (對校準 target):")
for x, v, dc, do in rows[:10]:
    print(f"    x={x}: dev_cal {mp.nstr(dc,6)}%  dev_o66 {mp.nstr(do,6)}%  value {mp.nstr(v,12)}")
best = rows[0]
print(f"\n  ★ 校準 target 最準: x={best[0]} (dev {mp.nstr(best[2],6)}%)")
print(f"  ★ 76 嘅校準 dev: {mp.nstr(rows[75-50][2] if False else next(r[2] for r in rows if r[0]==76), 6)}%")
d75 = next(r for r in rows if r[0]==75)
d76 = next(r for r in rows if r[0]==76)
print(f"  x=75: dev_cal {mp.nstr(d75[2],6)}%  (75=3×25=無身份)")
print(f"  x=76: dev_cal {mp.nstr(d76[2],6)}%  (76=L₉/88−12=有身份)")
print(f"  → 若 75 比 76 近校準: 76 唔係數值最優, 揀佢係身份導向 = 後驗")
print()

# ── B. hop 補數族 ──
print("[B] hop 階梯補數族: 88−hop ∈ {87,84,80,77,76}")
hop_ladder = [1, 4, 8, 11, 12]
for h in hop_ladder:
    x = 88 - h
    v = inv6 - 1/mp.mpf(x)
    dc = abs(v - target_cal)/target_cal*100
    do = abs(v - target_o66)/target_o66*100
    tag = " ★76" if x == 76 else ""
    print(f"    hop={h:2d} → 88−{h}={x:3d}: dev_cal {mp.nstr(dc,7)}%  dev_o66 {mp.nstr(do,7)}%{tag}")
print("  → 若除 76 外仲有近命中: 「hop_max 補數唯一」唔成立")
print()

# ── C. 誤差窗分辨能力 ──
print("[C] O66 公式 vs 校準: 0.052% 差 vs 1/75↔1/76 之分辯能力")
diff_o66_cal = abs(M_o66 - M_cal)/M_cal*100
print(f"  O66 vs 校準 dev = {mp.nstr(diff_o66_cal, 5)}%")
print(f"  x=75 同 x=76 喺校準 target 嘅 dev 差: {mp.nstr(abs(d75[2]-d76[2]), 6)}%")
print(f"  → 揀 76 而唔揀 75 嘅「數值改善」係 {mp.nstr(abs(d75[2]-d76[2]), 6)}% —")
print(f"    而 O66 自己 vs 校準偏差 0.052% ≫ 呢個差 ⟹ 分辨唔到")
print()

# ── D. 校準 target 對應嘅「完美 x」──
print("[D] 校準 target 需要幾大修正?")
x_perfect_cal = 1/(inv6 - target_cal)
print(f"  校準 target 需要 x* = {mp.nstr(x_perfect_cal, 8)} (修正 1/x*)")
inv_xp = 1/x_perfect_cal
print(f"  → 用校準, 完美修正係 1/{mp.nstr(x_perfect_cal, 6)} ≈ 1/{mp.nstr(inv_xp, 6)}")
print(f"  x*=74.72 — 最近整數 75, 唔係 76!")
print()
print("=" * 40)
print("判決:")
print("  若 x=75 比 x=76 更接近校準 target → 「1/76」係後驗揀值,")
print("  76 嘅身份 (L₉/88−12/4×19) 係『先有數值近, 後配身份』 — 湊數坐實")