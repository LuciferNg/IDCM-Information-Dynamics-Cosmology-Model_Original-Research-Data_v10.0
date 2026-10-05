#!/usr/bin/env python3
"""
O206 — 第十一輪 scripts/06_: C_f 鋸齒交替盲測（Alternation Null, MC）
=========================================================================
scripts/05_ 觀察: C_f 對合法模式 n∈{1,2,3,4,5,7,9,11} 呈完全鋸齒交替
（相鄰方向 ↑↓↑↓↑↓↑, 7/7 步）; 峰值位置 {2,4,7,11} = {1,3,6,10}+1 = 三角數+1,
谷位 {3,5,9} = {2,4,8}+1 = 2^k+1。

⚠️ 誠實警戒: C_f = m/(M₀γ_n), 質量同 γ 都升序指派。交替方向 =
sign(ln(m_{i+1}/m_i) − ln(γ_{i+1}/γ_i))。呢個「係唔係稀有」要對 H0 計:
H0 = 「8 個質量以升序指派到合法模式, 質量數值隨機（log-uniform order stats）」。
MC 10⁶ 計: ①完全交替概率 ②峰值位置恰好 = 三角數+1（容許 4 個峰任意位 vs 指定位）
③谷位恰好 = 2^k+1。

PRE-REGISTERED: MC seed 20261006, N = 10⁶, score = 7 步全交替。
──────────────────────────────────────────────────────────────────────
"""
import math, random, json, os
import mpmath as mp
mp.mp.dps = 60
random.seed(20261006)

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1
    else: FAIL += 1
    print("  %s %s %s" % ("✅" if cond else "❌", name, detail))

M0 = 27.900915
gam = lambda n: 4 * math.sin(math.pi * n / 88)**2
NS = [1, 2, 3, 4, 5, 7, 9, 11]
GAM = [gam(n) for n in NS]

# 實測 C_f 序列方向
PDG = [0.51099895, 2.16, 4.67, 93.4, 105.6583755, 1270.0, 1776.86, 4180.0]
def sign_seq(vals):
    return [1 if vals[i+1] > vals[i] else -1 for i in range(len(vals)-1)]

def alternates(vals):
    s = sign_seq(vals)
    return all(s[i] != s[i+1] for i in range(len(s)-1))

obs = sign_seq([m/(M0*g) for m, g in zip(PDG, GAM)])
print("實測 C_f 方向序列:", obs, " 完全交替:", alternates([m/(M0*g) for m, g in zip(PDG, GAM)]))

# H0: 8 log-uniform 質量（先排序=m 升序）→ 交替概率
N = 1_000_000
cnt = 0
for _ in range(N):
    ms = sorted(math.exp(random.uniform(math.log(0.5), math.log(5000))) for _ in range(8))
    s = [1 if ms[i+1]/GAM[i+1] > ms[i]/GAM[i] else -1 for i in range(7)]
    if all(s[i] != s[i+1] for i in range(6)):
        cnt += 1
p_alt = cnt / N
print("H0 完全交替: p = %.5f  (%d/%d)" % (p_alt, cnt, N))
check("alternation 顯著 (p<0.05)", p_alt < 0.05, "p=%.4f" % p_alt)

# 極值位置: peaks 恰 = {2,4,7,11}, valleys 恰 = {3,5,9}（喺「完全交替」嘅 sample 內）
# 完全交替下, peaks = 奇數步位置升 (2,4,6,8 index) 或 (3,5,7) 視起始 — 實測 peaks n ∈ {2,4,7,11}.
# 對 H0 sample 計「peak 嘅 γ-模式 == {2,4,7,11}」概率
peak_tgt = {2, 4, 7, 11}; val_tgt = {3, 5, 9}
cnt_alt = 0; cnt_both = 0
for _ in range(N):
    ms = sorted(math.exp(random.uniform(math.log(0.5), math.log(5000))) for _ in range(8))
    cf = [m/g for m, g in zip(ms, GAM)]
    peaks = {NS[i] for i in range(8) if (i == 0 or cf[i] > cf[i-1]) and (i == 7 or cf[i] > cf[i+1])}
    vals = {NS[i] for i in range(8) if 0 < i < 7 and cf[i] < cf[i-1] and cf[i] < cf[i+1]}
    if peaks == peak_tgt and vals == val_tgt:
        cnt_both += 1
print("H0 峰值恰={%s} 谷值恰={%s}: p = %.6f  (%d/%d)"
      % (sorted(peak_tgt), sorted(val_tgt), cnt_both / N, cnt_both, N))
check("極值位置命中 (p<0.05)", cnt_both / N < 0.05, "p=%.5f" % (cnt_both / N))

out = {"obs_seq": obs, "p_alternate": p_alt, "p_extrema": cnt_both / N}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                       "06_alternation_null.json"), "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("\n結果: %d PASS / %d FAIL" % (PASS, FAIL))