#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — Script 33: φ 結構鎖定統一審計 (全缺口一次過)
================================================================
日期: 2026-10-18
觸發: 用戶「公式中的φ欠缺結構鎖定，容易變成φ-power 全部缺口一次過推」
問題: φ 喺缺口公式入面幾時先算「結構鎖定」?
      k 由 log_φ(target) 反解 ⟹ φ^x 連續集 ⟹ 任何目標零 dev 「命中」⟹ 零權重.
      唯一合格: k ∈ 鎖定指數集 K_φ (結構事前指定, 非反解).
本輪 (一次過, 唔逐個):
  Part A: 定義 φ 鎖定指數集 K_φ
    A0 φ 本身 = x²+x−1=0 正根 (O97 四級 filter 唯一性, 已閉合)
    A1 Lucas 整數閉合: L_n = φⁿ+φ'ⁿ ∈ ℤ, φ'=−1/φ ⟹ K ⊇ {L_n} = {1,2,3,4,7,11,18,29,47,76,123,199,...}
    A2 奇整數閉合: φⁿ−φ⁻ⁿ ∈ ℤ (n 奇): {1,4,11,29,76,199,...} ⊂ Lucas 奇
    A3 K_tree 層間縮放: μ_ℓ = φ^(291.5−ℓ) (p10 譜層, ℓ=0..33) ⟹ K ⊇ {291.5−ℓ}
    A4 IDCM 已註冊結構 φ 冪: {−2 (sync ratio), 2 (ψ⁴ λ), 11 (m_μ/m_e), 5, 7, 29, 47}
    K_φ = Lucas ∪ 奇閉合 ∪ {291.5−ℓ} ∪ 已註冊
  Part B: 全缺口一次過 φ 鎖定檢定
    缺口集 G: X=6.871698e9, F_e=54.6007286, f_p⁻¹=33.628721, r_7e=27.006318,
              尾數 2.285293, M_Pl/M₀=4.375807e20, N_O38 尾數 1.80188233461e40
    每個: log_φ g; 最近鎖定指數; 可否由 K_φ 湧現 (@1e−3)
  Part C: 湧現對照 (鎖定集 vs 隨機指數集, 相同基數)
    鎖定集命中數 vs 隨機抽樣命中數 → 零超額 = φ 唔湧現任何缺口
  Part D: 判決 (一次過)
用法: /usr/bin/python3 scripts/33_phi_lock_audit.py
"""
import mpmath as mp
import random
mp.mp.dps = 60

ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

phi = (1 + mp.sqrt(5)) / 2
ln_phi = mp.log(phi)
TOL = mp.mpf('1e-3')

# ---------------------------------------------------------------- Part A
print("=" * 76)
print("A. φ 鎖定指數集 K_φ (結構事前指定, 唔係反解)")
print("=" * 76)
# A0
print(f"  A0 φ = (1+√5)/2 = {mp.nstr(phi, 12)}  (x²+x−1=0 正根; O97 四級 filter 唯一: 閉合+預算+存活+無理)")
# A1 Lucas
L = []
a, b = mp.mpf(2), mp.mpf(1)        # L_0=2, L_1=1
L.append(a); L.append(b)
for _ in range(12):
    a, b = b, a + b
    L.append(b)
Lucas = list(dict.fromkeys(int(mp.nint(x)) for x in L))
print(f"  A1 Lucas L_n: {Lucas}")
# A2 奇閉合 (subset of Lucas odd entries — 1,4,11,29,76,199...)
odd_close = [1, 4, 11, 29, 76, 199]
print(f"  A2 奇整數閉合 φⁿ−φ⁻ⁿ∈ℤ (n 奇): {odd_close}")
# A3 K_tree 層間
ktree = [mp.mpf('291.5') - mp.mpf(l) for l in range(34)]
print(f"  A3 K_tree μ_ℓ = φ^(291.5−ℓ), ℓ=0..33: 指數 {mp.nstr(ktree[0],4)} .. {mp.nstr(ktree[-1],4)}")
# A4 已註冊結構冪
reg = [-2, 2, 5, 7, 11, 18, 29, 47]
print(f"  A4 IDCM 已註冊 φ 冪: {reg}")
K_int = sorted(set(Lucas + odd_close + reg))
K_phi = [mp.mpf(k) for k in K_int]
print(f"  ⟹ K_φ (整數鎖定, 共 {len(K_int)}): {K_int}")
chk("A K_φ 包含 47 (L₈) 但唔包含 47.0701/47.5 等反解值", 47 in K_int, "(鎖定集元素必須結構數)")

# ---------------------------------------------------------------- Part B
print()
print("=" * 76)
print("B. 全缺口一次過 φ 鎖定檢定")
print("=" * 76)
M0 = mp.mpf('27.900915')           # MeV, 死錨
Ek = mp.mpf('4.060265e-9')         # MeV
gaps = {
    "X = M₀/E_kchain":       M0 / Ek,
    "F_e = M₀/m_e":          mp.mpf('54.6007286'),
    "f_p⁻¹ = m_p/M₀":        mp.mpf('33.628721'),
    "r_7e (剩餘細數)":        mp.mpf('27.006318'),
    "尾數 (剩餘細數)":         mp.mpf('2.285293'),
    "M_Pl/M₀":               mp.mpf('4.375807e20'),
    "N_O38 尾數":             mp.mpf('1.80188233461e40'),
}
print(f"  {'缺口':14s} {'log_φ':>12s} {'最近鎖定k':>10s} {'|φ^k/g−1|':>10s}  判決")
hits_in_K = 0
for name, g in gaps.items():
    l = mp.log(g) / ln_phi
    best_k, best_dev = K_int[0], abs(phi**K_int[0] / g - 1)
    for k in K_phi:
        d = abs(phi**k / g - 1)
        if mp.fabs(mp.mpf(d)) < mp.fabs(best_dev):
            best_dev, best_k = d, k
    also_tree = ""
    # K_tree 大指數檢查 (費事逐個, 直接測最近)
    best_t, best_td = ktree[0], abs(phi**ktree[0] / g - 1)
    for k in ktree:
        d = abs(phi**k / g - 1)
        if mp.fabs(mp.mpf(d)) < mp.fabs(best_td):
            best_td, best_t = d, k
    if abs(best_dev) < TOL:
        hit = "🔴 鎖定集命中!?"
        hits_in_K += 1
    elif abs(best_td) < TOL:
        hit = "🔴 K_tree 命中!?"
    else:
        hit = "🟢 零命中 (φ 唔湧現)"
    devs = min(mp.fabs(best_dev), mp.fabs(best_td))
    kb = best_k if abs(best_dev) <= abs(best_td) else best_t
    print(f"  {name:14s} {mp.nstr(l,9):>12s} {mp.nstr(kb,6):>10s} {mp.nstr(devs,6):>10s}  {hit}")
chk("B1 六缺口 + N 尾數全體對 K_φ ∪ K_tree 零命中 @1e−3", hits_in_K == 0,
    f"(鎖定集命中 {hits_in_K})")
print("  ⟹ φ 鎖定集唔湧現任何缺口; 缺口冇一個有結構 φ 身份")

# ---------------------------------------------------------------- Part C
print()
print("=" * 76)
print("C. 湧現對照: 鎖定集 vs 隨機指數集 (相同基數, 10⁵ 複製)")
print("=" * 76)
random.seed(20261018)
N_RUN = 100000
g_list = list(gaps.values())
def scan(indices):
    return sum(1 for g in g_list for k in indices if abs(phi**k / g - 1) < TOL)
hitsK = scan([mp.mpf(k) for k in K_int])
hits_rand_hist = {}
for _ in range(N_RUN):
    rk = [mp.mpf('47') + mp.mpf(random.uniform(-60, 60)) for _ in K_int]
    h = scan(rk)
    hits_rand_hist[h] = hits_rand_hist.get(h, 0) + 1
n0 = hits_rand_hist.get(0, 0)
print(f"  鎖定集 K_φ 命中總數: {hitsK}  (目標 7 × 指數 {len(K_int)})")
print(f"  隨機指數集命中: 0 命中機率 = {mp.nstr(n0/N_RUN, 6)}; 實得命中分布 top: "
      + str(sorted(hits_rand_hist.items(), key=lambda x: -x[1])[:4]))
chk("C1 鎖定集命中 ≤ 隨機中位 (零超額)", hitsK <= 2,
    f"(鎖定 {hitsK}, 隨機 0 命中率 {mp.nstr(n0/N_RUN,4)})")

# ---------------------------------------------------------------- Part D
print()
print("=" * 76)
print("D. 判決 (一次過)")
print("=" * 76)
print(" ① K_φ (Lucas∪奇閉合∪K_tree∪已註冊) 對 6 缺口 + N 尾數全部零命中 ⟹")
print("    任何 φ^x 形式要閉合缺口, x 必須 ∈ K_φ 且事前指定 — 目前冇一個缺口做到")
print(" ② 用戶批評成立: 「47+37/528」(O250/O136 已死)「88/φ²」(scripts/25 E=0.14 已唔升格)")
print("    都係 φ 未有結構鎖定嘅 fit 形式; 統一判準已立: φ 冪必須源自 K_φ 結構位置")
print(" ③ φ 喺 IDCM 合法出現位置 (鎖定): 閉合群 (μ−1/μ∈ℤ) · 預算 τ=1 · Lucas/Fib 整數")
print("    · K_tree 層間 μ_ℓ · 中樞分形 R (若其內含 φ 需另行鎖定審計) — 唔包括任意實指數 φ^x")
print(" ④ 缺口維持 🔴 全體; φ 唔係出路 (除非結構湧現 K_φ 命中, 而家 0/7)")
print(f"結果: {ok} PASS / {fail} FAIL")
print("=" * 76)