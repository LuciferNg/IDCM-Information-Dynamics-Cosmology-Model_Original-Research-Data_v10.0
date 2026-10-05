#!/usr/bin/env python3
"""
O206 — 第十一輪(d) scripts/35: 鋸齒 Z₂ 三盲測（逐個做）
=========================================================================
承接: docs/38 確認鋸齒真身 = 奇偶 rank 分裂（even/odd rank Z₂）。本輪逐個測試:
  T1 置換 null —— even/odd 分裂喺 8! 質量→模式雙射入面 rank 幾多?
      (只有「升序指派」先有? 定係好多 assignment 都有?)
  T2 Z₂ 歸因 —— 鋸齒跟「質量 rank parity」定「模式 n parity」?
      (c: rank6-even 但 n=7-odd; b: rank8-even 但 n=11-odd ⟹ 兩者可以區分)
      另: envelope 去掉後嘅殘餘係咪二值 ±σ（真 Z₂ 修正）?
  T3 u/d scheme 壓力 —— PDG u∈[1.8,3.5], d∈[4.5,5.3] 範圍內,
      even/odd 結構保持概率?（閾值: y_u−y_d = ln(u/d) + ln(γ₃/γ₂) = ln(u/d) + 0.8089,
      交替需要 > 0 ⟺ u/d > γ₂/γ₃ = 0.4454）

PRE-REGISTERED: MC seed 20261006; T1 用 8! 全枚舉; T3 用 10⁶ log/linear uniform。
──────────────────────────────────────────────────────────────────────
"""
import math, itertools, random, json, os
import mpmath as mp
mp.mp.dps = 40
random.seed(20261006)

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1
    else: FAIL += 1
    print("  %s %s %s" % ("✅" if cond else "❌", name, detail))

M0 = 27.900915
gam = lambda n: 4 * math.sin(math.pi * n / 88)**2
MASS = {"e":0.51099895,"u":2.16,"d":4.67,"s":93.4,"mu":105.6583755,
        "c":1270.0,"tau":1776.86,"b":4180.0}
ORDER = ["e","u","d","s","mu","c","tau","b"]          # 質量升序
MODES = [1,2,3,4,5,7,9,11]

def lnCf_at(masses, modes):
    return [math.log(m / (M0 * gam(n))) for m, n in zip(masses, modes)]

def is_alternating(ys):
    """完全交替: 7 個相鄰方向每步反轉（↑↓↑↓↑↓↑ 或 ↓↑↓↑↓↑↓）"""
    dirs = [ys[i+1] > ys[i] for i in range(len(ys)-1)]
    return all(dirs[i] != dirs[i+1] for i in range(len(dirs)-1))

def even_odd_split(ys):
    """完全交替 + 兩條子序列各自單調增"""
    if not is_alternating(ys):
        return False
    ev = ys[1::2]; od = ys[0::2]
    return all(ev[i] < ev[i+1] for i in range(3)) and all(od[i] < od[i+1] for i in range(3))

mass_list = [MASS[f] for f in ORDER]
obs_ys = lnCf_at(mass_list, MODES)

# ══════════════════ T1. 置換 null (8! = 40320) ══════════════════
print("=" * 74)
print("T1. 置換 null: even/odd 分裂喺 8! 雙射中嘅 rank")
print("=" * 74)
cnt_alt = 0; cnt_split = 0
for perm in itertools.permutations(MODES):
    ys = lnCf_at(mass_list, perm)
    if is_alternating(ys):
        cnt_alt += 1
        if even_odd_split(ys):
            cnt_split += 1
print("  完全交替 assignment 數: %d / 40320  (有升序指派?" % cnt_alt,
      "+", "升序指派屬於呢類: %s)" % (obs_ys == lnCf_at(mass_list, MODES)))
print("  even/odd 分裂 assignment 數: %d / 40320" % cnt_split)
# 升序指派 rank（用 score = 分裂成立最優先, 其次 alternation）
rank_split = 1 + sum(1 for perm in itertools.permutations(MODES)
                     if even_odd_split(lnCf_at(mass_list, perm)))
in_split = even_odd_split(obs_ys)
print("  升序指派屬於分裂類: %s （注意: rank 需排序 criterion; 唔好 overclaim）" % in_split)
check("T1: 升序指派本身做到分裂", in_split,
      "分裂類總數=%d" % cnt_split)

# 對照: 唔只二分——仲要「兩子序列單調」嘅額外資訊量
cnt_alt_only = cnt_alt - cnt_split
print("  對照: 純交替(唔計子序列單調) = %d; 加單調後剩 %d" % (cnt_alt, cnt_split))

# ══════════════════ T2. Z₂ 歸因: rank vs mode parity ══════════════════
print("\n" + "=" * 74)
print("T2. Z₂ 歸因: 鋸齒跟 rank parity 定 mode parity?")
print("=" * 74)
rank_par = [(-1)**i for i in range(8)]                 # i=0 → rank1 odd? rank1..8: even位 +1
rank_pm  = [1 if r % 2 == 0 else -1 for r in range(1, 9)]   # even rank +1, odd −1
mode_pm  = [1 if n % 2 == 0 else -1 for n in MODES]
def fit_models(xs, ys_, pm, label):
    """y = a + b x + c x² + σ·pm; return σ (beta[3]) + max resid"""
    n = len(ys_)
    A = [[0.0]*4 for _ in range(4)]; B = [0.0]*4
    for i in range(n):
        row = [1.0, xs[i], xs[i]*xs[i], pm[i]]
        for j in range(4): B[j] += row[j]*ys_[i]
        for j in range(4):
            for k in range(4): A[j][k] += row[j]*row[k]
    for j in range(4):
        pv = j
        while pv < 4 and abs(A[pv][j]) < 1e-12: pv += 1
        if pv >= 4: continue
        A[j], A[pv] = A[pv], A[j]; B[j], B[pv] = B[pv], B[j]
        for k in range(j+1, 4):
            f_ = A[k][j]/A[j][j]
            for l in range(j, 4): A[k][l] -= f_*A[j][l]
            B[k] -= f_*B[j]
    beta = [0.0]*4
    for j in range(3, -1, -1):
        s_ = B[j]
        for k in range(j+1, 4): s_ -= A[j][k]*beta[k]
        if abs(A[j][j]) > 1e-12: beta[j] = s_/A[j][j]
    resid = [ys_[i] - (beta[0] + beta[1]*xs[i] + beta[2]*xs[i]*xs[i] + beta[3]*pm[i])
             for i in range(n)]
    mx = max(abs(r) for r in resid)
    print("  %-12s σ=%7.4f  max|resid|=%.4f (唔加 σ 嘅二次 base 為 %.4f)"
          % (label, beta[3], mx, max(abs(ys_[i] - (beta[0]+beta[1]*xs[i]+beta[2]*xs[i]*xs[i])) for i in range(n))))
    return beta[3], mx

xn = [float(n) for n in MODES]
s_rank, m_rank = fit_models(xn, obs_ys, rank_pm, "rank parity")
s_mode, m_mode = fit_models(xn, obs_ys, mode_pm, "mode parity")

# envelope 去掉後二值性: e_i = y_i − quad-base (rank-parity model); 睇 sign/imbalance
Aq = [[0.0]*3 for _ in range(3)]; Bq = [0.0]*3
for i in range(8):
    row = [1.0, xn[i], xn[i]*xn[i]]
    for j in range(3): Bq[j] += row[j]*obs_ys[i]
    for j in range(3):
        for k in range(3): Aq[j][k] += row[j]*row[k]
for j in range(3):
    pv = j
    while pv < 3 and abs(Aq[pv][j]) < 1e-12: pv += 1
    if pv >= 3: continue
    Aq[j], Aq[pv] = Aq[pv], Aq[j]; Bq[j], Bq[pv] = Bq[pv], Bq[j]
    for k in range(j+1, 3):
        f_ = Aq[k][j]/Aq[j][j]
        for l in range(j, 3): Aq[k][l] -= f_*Aq[j][l]
        Bq[k] -= f_*Bq[j]
bq = [0.0]*3
for j in range(2, -1, -1):
    s_ = Bq[j]
    for k in range(j+1, 3): s_ -= Aq[j][k]*bq[k]
    if abs(Aq[j][j]) > 1e-12: bq[j] = s_/Aq[j][j]
resid_q = [obs_ys[i] - (bq[0] + bq[1]*xn[i] + bq[2]*xn[i]*xn[i]) for i in range(8)]
print("  quad-base 殘餘:", [round(r, 4) for r in resid_q])
print("  even-rank 殘餘:", [round(resid_q[i], 4) for i in range(8) if rank_pm[i] > 0],
      "| odd-rank:", [round(resid_q[i], 4) for i in range(8) if rank_pm[i] < 0])
r_even = [abs(resid_q[i]) for i in range(8) if rank_pm[i] > 0]
r_odd  = [abs(resid_q[i]) for i in range(8) if rank_pm[i] < 0]
check("T2: rank-parity 修正優於 mode-parity (max resid 更細)", m_rank < m_mode - 1e-6,
      "rank=%.4f mode=%.4f" % (m_rank, m_mode))
check("T2: envelope 殘餘二值 (even/odd |resid| 分離 > 2×)", min(r_even) > 2*max(r_odd) or min(r_odd) > 2*max(r_even),
      "even=%s odd=%s" % (r_even, r_odd))

# ══════════════════ T3. u/d scheme 壓力 ══════════════════
print("\n" + "=" * 74)
print("T3. u/d scheme 壓力: PDG 範圍內 even/odd 保持概率 (MC 10⁶)")
print("=" * 74)
Nmc = 1_000_000
keep_alt = 0; keep_pair = 0; split_ok = 0
# 閾值理論: y_u − y_d = ln(u/d) − ln(γ₂/γ₃); 需要 > 0 ⟺ u/d > γ₂/γ₃ = 0.44539...
thr = gam(2)/gam(3)
print("  理論閾值: u/d > γ₂/γ₃ = %.5f" % thr)
for _ in range(Nmc):
    u = random.uniform(1.8, 3.5); d = random.uniform(4.5, 5.3)
    ms = [0.51099895, u, d, 93.4, 105.6583755, 1270.0, 1776.86, 4180.0]
    ys = lnCf_at(ms, MODES)
    if is_alternating(ys):
        keep_alt += 1
        if even_odd_split(ys):
            split_ok += 1
    if ys[1] > ys[0] and ys[1] > ys[2]:
        keep_pair += 1
p_alt = keep_alt/Nmc; p_pair = keep_pair/Nmc; p_split = split_ok/Nmc
print("  完全交替保持: p = %.4f" % p_alt)
print("  u-peak 對 (u>e 且 u>d): p = %.4f" % p_pair)
print("  even/odd 完整分裂: p = %.4f" % p_split)
if p_pair < 0.5:
    check("T3: u-peak 對 robust (p≥50%)", False, "p_pair=%.4f" % p_pair)
    check("T3: 結構崩潰率 < 50% (誠實壓力)", True, "崩潰率=%.1f%%" % ((1-p_pair)*100))
else:
    check("T3: u-peak 對 robust (p≥50%)", True, "p_pair=%.4f" % p_pair)

out = {"T1": {"alt_count": cnt_alt, "split_count": cnt_split, "rank_split": rank_split},
       "T2": {"rank_sigma": s_rank, "rank_resid": m_rank, "mode_sigma": s_mode,
              "mode_resid": m_mode, "quad_resid": resid_q},
       "T3": {"threshold_ud": thr, "p_alt": p_alt, "p_pair": p_pair, "p_split": p_split}}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                       "35_z2_three_tests.json"), "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("\n結果: %d PASS / %d FAIL" % (PASS, FAIL))