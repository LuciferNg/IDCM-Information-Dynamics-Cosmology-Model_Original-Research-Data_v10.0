#!/usr/bin/env python3
"""
O206 — 第十一輪 scripts/32: C_f 統一生成式掃描（Unified Generator Scan）
=========================================================================
承接: 第十輪（docs/34）判死「逐點池命中」（p=0.9955/0.8214）；第十輪 docs/34 指出
生成器需「新結構輸入（detent/κ/非 F2 形式）」。本輪轉攻三類新測試：
  A. 統一生成式（global shape）：C_f(n) = A·f(n)，8 點一次過，A = 幾何中位 scale。
     ⚠️ 形狀 fit 同「逐點撞池」本質唔同：逐點 hit 會被池密度殺，shape fit 係
     一條曲線 8 個點同時收斂先得 — 自由度成本高，唔受 per-point density 影響。
  B. detent 重標度：γ_n(N) = 4sin²(nπ/N), N ∈ {22,44,60,88,176}；檢查邊個 N
     令 C_f(N) = m/(M₀γ_n(N)) 嘅 γ-階梯性質（塊跨度/整體方差）最強。
  C. 比值家族 joint null（控制項）：7 個相鄰比值撞 F1' 池（期望負）。

──────────────────────────────────────────────────────────────────────
PRE-REGISTERED（執行前凍結, hash 記入輸出）:
  U 族（f(n)，A = 幾何中位 scale，零新常數）:
    U1  γ_n
    U2  γ_n/(4−γ_n)                  [γ₄₄−γ_n 倒數 pole 型]
    U3  1 − γ_n/4                    [= cos²(nπ/88)]
    U4  (1 − γ_n/4)/γ_n              [= 1/γ_n − 1/4]
    U5  γ_n²
    U6  sin(nπ/88)                   [= ω_n/2, 玻色塔?]
    U7  sin(nπ/44)                   [δω 家族]
    U8  1/n                          [對照, 前九輪已淡化]
    U9  γ_n/(1+γ_n)
    U10 γ_n/(2−γ_n)                  [pole at γ=2 = μ²]
  （對照）U11: A·γ_n^p，p 自由（2-參數）— 唔入主清單, 作 overfit 對照
  判據: max|ln(C_f/(A·f))| < 1% ⟹ 形狀候選（PASS）；1%–10% ⟹ 待改進；>10% ⟹ 族內無統一式
  B 族 detent: N ∈ {22, 44, 60, 88, 176}（偶；33/55 奇已結構性排除 O206 第六輪）
  C 族比值: 7 個相鄰 C 比值（質量升序排列）
──────────────────────────────────────────────────────────────────────
"""
import math, json, os, hashlib, random, sys
import mpmath as mp
mp.mp.dps = 60

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1
    else: FAIL += 1
    print("  %s %s  %s" % ("✅" if cond else "❌", name, detail))

random.seed(20261006)  # 第十一輪 seed

M0 = mp.mpf("27.900915")
def gam(n, N=88):
    return 4 * mp.sin(mp.pi * n / N)**2

PDG = {"e":"0.51099895","u":"2.16","d":"4.67","s":"93.4","mu":"105.6583755",
       "c":"1270.0","tau":"1776.86","b":"4180.0"}
N5 = {"e":1,"u":2,"d":3,"s":4,"mu":5,"c":7,"tau":9,"b":11}
ORDER = ["e","u","d","s","mu","c","tau","b"]
Cf = {f: mp.mpf(PDG[f]) / (M0 * gam(N5[f])) for f in PDG}
print("C_f (60 dps):")
for f in ORDER:
    print("   %-3s %s" % (f, mp.nstr(Cf[f], 14)))

# ── A. 統一生成式 ──────────────────────────────────────────────────
print("\n" + "=" * 78)
print("A. 統一生成式 C_f(n) = A·f(n)   [A = 幾何中位 scale]")
print("=" * 78)
def geo_median(vals):
    n = len(vals); v = sorted(float(mp.log(x)) for x in vals)
    return mp.mpf(math.exp(v[n // 2] if n % 2 else (v[n//2-1] + v[n//2]) / 2))

U = {
 "U1":  lambda m: 4*mp.sin(mp.pi*m/88)**2,
 "U2":  lambda m: (4*mp.sin(mp.pi*m/88)**2) / (4 - 4*mp.sin(mp.pi*m/88)**2),
 "U3":  lambda m: 1 - 4*mp.sin(mp.pi*m/88)**2/4,
 "U4":  lambda m: (1 - 4*mp.sin(mp.pi*m/88)**2/4) / (4*mp.sin(mp.pi*m/88)**2),
 "U5":  lambda m: (4*mp.sin(mp.pi*m/88)**2)**2,
 "U6":  lambda m: mp.sin(mp.pi*m/88),
 "U7":  lambda m: mp.sin(mp.pi*m/44),
 "U8":  lambda m: mp.mpf(1)/m,
 "U9":  lambda m: (4*mp.sin(mp.pi*m/88)**2) / (1 + 4*mp.sin(mp.pi*m/88)**2),
 "U10": lambda m: (4*mp.sin(mp.pi*m/88)**2) / (2 - 4*mp.sin(mp.pi*m/88)**2),
}
upre = ";".join(sorted(U))
results = {}
for name, fn in sorted(U.items()):
    fvals = [fn(N5[f]) for f in ORDER]
    A = geo_median([Cf[f] / fval for f, fval in zip(ORDER, fvals)])
    ln_dev = [float(mp.log(Cf[f] / (A * fval))) for f, fval in zip(ORDER, fvals)]
    mx = max(abs(d) for d in ln_dev)
    rms = math.sqrt(sum(d*d for d in ln_dev) / len(ln_dev))
    results[name] = {"A": mp.nstr(A, 8), "max_dev": mx, "rms": rms}
    print("  %-4s A=%-9s max_dev=%.4e  rms=%.4e  %s"
          % (name, mp.nstr(A, 7), mx, rms, "✅<1%" if mx < 0.01 else ("🟡1-10%" if mx < 0.10 else "❌>10%")))

# U11 兩參數對照（p 自由 via least squares in log-log）
def fit_power():
    xs = [float(mp.log(4*mp.sin(mp.pi*N5[f]/88)**2)) for f in ORDER]
    ys = [float(mp.log(Cf[f])) for f in ORDER]
    n = len(xs)
    mx_, my_ = sum(xs)/n, sum(ys)/n
    sxx = sum((x-mx_)**2 for x in xs); sxy = sum((x-mx_)*(y-my_) for x, y in zip(xs, ys))
    p = sxy / sxx if sxx > 0 else 0
    lnA = my_ - p*mx_
    dev = [ys[i] - (p*xs[i] + lnA) for i in range(n)]
    return p, math.exp(lnA), max(abs(d) for d in dev)
p11, A11, mx11 = fit_power()
print("  U11 對照 A·γ^p (2-參數):  p=%.4f  A=%.4e  max_dev=%.4e" % (p11, A11, mx11))
results["U11"] = {"A": mp.nstr(A11, 6), "p": p11, "max_dev": mx11}

# U12 兩參數對照: ln C = a + b·ln(γ/(4−γ))
def fit_frac():
    xs = [float(mp.log(gam(N5[f]) / (4 - gam(N5[f])))) for f in ORDER]
    ys = [float(mp.log(Cf[f])) for f in ORDER]
    n = len(xs)
    mx_, my_ = sum(xs)/n, sum(ys)/n
    sxx = sum((x-mx_)**2 for x in xs); sxy = sum((x-mx_)*(y-my_) for x, y in zip(xs, ys))
    b = sxy / sxx if sxx > 0 else 0
    lnA = my_ - b*mx_
    dev = [ys[i] - (b*xs[i] + lnA) for i in range(n)]
    return b, math.exp(lnA), max(abs(d) for d in dev)
p12, A12, mx12 = fit_frac()
print("  U12 對照 A·(γ/(4−γ))^b (2-參數):  b=%.4f  A=%.4e  max_dev=%.4e" % (p12, A12, mx12))
results["U12"] = {"A": mp.nstr(A12, 6), "b": p12, "max_dev": mx12}

top = sorted(results.items(), key=lambda kv: kv[1]["max_dev"])[:3]
print("\n  Top-3 形狀: " + "  ".join("%s %.2e" % (k, v["max_dev"]) for k, v in top))
best = top[0][1]["max_dev"]
check("統一生成式族內存在 <1% 形狀", best < 0.01, "best=%.3e" % best)
check("統一生成式族內無任何 <10% 形狀（關鍵負結果）", best >= 0.10, "best=%.3e" % best)

# ── B. detent 重標度 ──────────────────────────────────────────────
print("\n" + "=" * 78)
print("B. detent 重標度 γ_n(N): C_f(N) = m/(M₀γ_n(N))")
print("=" * 78)
blocks = [["e","u","d"], ["s","mu","c"], ["tau","b"]]
def block_span_sum(Nval):
    tot = 0; allvar = []
    for blk in blocks:
        cs = [float(mp.log(mp.mpf(PDG[f]) / (M0 * gam(N5[f], Nval)))) for f in blk]
        tot += max(cs) - min(cs)
        allvar += cs
    var = sum((x - sum(allvar)/len(allvar))**2 for x in allvar) / len(allvar)
    return tot, var
for Nv in (22, 44, 60, 88, 176):
    sp, var = block_span_sum(Nv)
    rel = sp / block_span_sum(88)[0]
    print("  N=%3d : Σ塊ln跨度=%.4f (rel 88=%5.2f)   lnC 方差=%.4f" % (Nv, sp, rel, var))
span88 = block_span_sum(88)[0]
bval = min(((block_span_sum(Nv)[0], Nv) for Nv in (22,44,60,176)), default=(1e9, None))
check("detent 令 γ-階梯顯著改善（Σ跨度 < 88 之 50%）", bval[0] < 0.5 * span88,
      "best N=%s span=%.4f vs 88=%.4f" % (bval[1], bval[0], span88))

# ── C. 比值家族 joint null（控制項）───────────────────────────────
print("\n" + "=" * 78)
print("C. 7 個相鄰 C 比值 vs F1' 池（控制項, 預期負）")
print("=" * 78)
# S 集合（同 scripts/30 定義）
L = [2, 1]
for k in range(2, 15): L.append(L[-1] + L[-2])
F = [0, 1]
for k in range(2, 21): F.append(F[k-1] + F[k-2])
S = set(L) | set(F[2:]) | {4,16,64,256,3,44,33,134,36,98,2,18,5,88,176,946,123,137,
                           90,46,45,60,42,37,41,47,48,50,51,26,22,17,8,40}
S = {int(s) for s in S if 1 <= s <= 10**6}
pool = set()
for c in S:
    for s1 in S:
        pool.add(mp.mpf(s1)/mp.mpf(c))
        for s2 in S:
            pool.add((mp.mpf(s1)+mp.mpf(s2))/mp.mpf(c))
            if s1 > s2:
                pool.add((mp.mpf(s1)-mp.mpf(s2))/mp.mpf(c))
POOL = sorted((mp.mpf(p) for p in pool), key=lambda x: float(mp.log(x)))
import bisect
def hits(t, delta):
    i0 = bisect.bisect_left(POOL, t/(1+delta)); i1 = bisect.bisect_right(POOL, t*(1+delta))
    return POOL[i0:i1]
RATIOS = []
for a, b_ in zip(ORDER, ORDER[1:]):
    r = Cf[a] / Cf[b_]
    RATIOS.append((a+"/"+b_, r))
    print("  C_%s = %s   1e-3窗命中 %d" % (RATIOS[-1][0], mp.nstr(r, 10), len(hits(r, 1e-3))))
LOGLO, LOGHI = math.log(min(float(r) for _, r in RATIOS)), math.log(max(float(r) for _, r in RATIOS))
obs = sum(len(hits(r, 1e-3)) for _, r in RATIOS)
Nmc = 100_000
mc = [sum(len(hits(mp.mpf(math.exp(random.uniform(LOGLO, LOGHI))), 1e-3)) for _ in RATIOS)
      for _ in range(Nmc)]
pval = sum(1 for h in mc if h >= obs) / Nmc
print("  joint 命中 = %d | MC 中位 = %d | P(≥obs) = %.4f" % (obs, sorted(mc)[Nmc//2], pval))
check("比值家族無富集（控制項確認）", pval > 0.05, "p=%.4f" % pval)

# 凍結記錄
frozen = hashlib.sha256((upre + "|" + ",".join(str(Nv) for Nv in (22,44,60,88,176))
                         + "|" + ",".join(r for r, _ in RATIOS)).encode()).hexdigest()[:16]
out = {"frozen_hash": frozen, "unified": {k: {kk: str(vv) for kk, vv in v.items()}
                                          for k, v in results.items()},
       "best_unified_dev": results[top[0][0]]["max_dev"],
       "top3": [k for k, _ in top],
       "detent_spans": {str(Nv): block_span_sum(Nv)[0] for Nv in (22,44,60,88,176)},
       "ratio_joint": {"obs": obs, "p": pval}}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                       "32_unified_generator.json"), "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("\n" + "=" * 78)
print("結果: %d PASS / %d FAIL   frozen_hash = %s" % (PASS, FAIL, frozen))
sys.exit(1 if FAIL else 0)