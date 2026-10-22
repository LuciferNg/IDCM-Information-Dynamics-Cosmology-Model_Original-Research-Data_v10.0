#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — M₀ 標度攻堅 (scripts/20 v3): 無量綱純數 N 之掃描 + null + 盲測協議
==================================================================================
承接 scripts/19 (維度側閉合): M₀ = N · ħω_ring, N = 1.80188233461e40 係唯一缺口。

禁區遵守 (唔可重推):
  - O136 docs/36: φ^(47+37/528) = 事後有理重建 (過度吻合判準, 排除方向 #27)
  - O136 docs/37: 幾何平均僅相容性論證; 兩參數欠定 (H₀, x) ← 1 目標

方法 (目標盲 + bisect; 族形式 = 整數 + 有理分數, 即 docs/36 §四 同型):
  [A] N 之結構座標 (log_φ, log_137, log_88, ...)
  [B] 密集族 φ^x: x = p + m/q (p∈[186,199], m∈結構分子集, q∈[50,2050:10])
      及 137^k 同型 → 命中數 vs 容差
  [C] 乘積族 ∏ a_i^{e_i} (≤2 因子, e = k/4)
  [D] 隨機 null (200 個同量級目標) → 假陽率 (命中帶資訊?)
  [E] 過度吻合判準 (方法論定理 5) + ★ 盲測協議 (3 條)
  [F] 判定
"""
import bisect
import math
import random
from mpmath import mp, mpf, sqrt, pi, log
mp.dps = 60

# ── N 之精確值 (scripts/19) ──
hbar_eVs = mpf('6.582119569e-16')
w_ring = mpf('72.59')
H0_si = w_ring * 1000 / mpf('3.0856775814913673e22')
hw = hbar_eVs * H0_si
M0 = mpf('27.900915e6')
N_M = M0 / hw
phi = (1 + sqrt(5)) / 2
LOG10_N = float(log(N_M, 10))

print("=" * 78)
print("  O38/m0-scale — scripts/20 v3: N 掃描 + null + 盲測協議")
print("=" * 78)
results = []
TOL = [1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2]

# ═══ [A] N 之結構座標 ═══
print("\n─── [A] N = M₀/(ħω_ring) 之結構座標 ───")
print(f"  N = {mp.nstr(N_M, 14)}   (log10 N = {LOG10_N:.10f})")
for k, b in {'φ': phi, '137': mpf(137), '88': mpf(88), '44': mpf(44), '90': mpf(90),
             '61.5': mpf('61.5'), '√137': sqrt(137), '123': mpf(123), 'e': mp.e, 'π': pi}.items():
    v = log(N_M, b)
    ni = mp.nint(v)
    print(f"  log_{k:>5}(N) = {mp.nstr(v, 12)}   最近整數 {ni} (Δ = {mp.nstr(v - ni, 6)})")
results.append(True)

def nearest_dev(sl, lt):
    i = bisect.bisect_left(sl, lt)
    best = 1e9
    for j in (i - 1, i):
        if 0 <= j < len(sl):
            best = min(best, abs(10.0 ** (sl[j] - lt) - 1.0))
    return best

def count_within(sl, lt, tol):
    return sum(1 for v in sl if abs(10.0 ** (v - lt) - 1.0) < tol)

# ═══ [B] 密集族 (整數 + 有理分數) ═══
print("\n─── [B] 密集族 x = p + m/q (docs/36 §四 同型) ───")
MNUMS = [1, 2, 3, 5, 11, 13, 29, 33, 37, 44]      # 結構分子子集
def dense_family(base, p_lo, p_hi):
    lbs = []
    for p in range(p_lo, p_hi + 1):
        for m in MNUMS:
            for q in range(50, 2051, 10):
                x = mpf(p) + mpf(m) / q
                lbs.append(float(log(base ** x, 10)))
    lbs.sort()
    return lbs

fam_phi = dense_family(phi, 186, 199)
fam_137 = dense_family(mpf(137), 16, 22)
for name, fam in [('φ^x', fam_phi), ('137^k', fam_137)]:
    print(f"  {name}: {len(fam)} 候選; 最佳命中 dev = {nearest_dev(fam, LOG10_N):.3e}")
    for t in TOL:
        print(f"    容差 {t:.0e}: {count_within(fam, LOG10_N, t)} 命中")
results.append(True)

# ═══ [C] 乘積族 ═══
print("\n─── [C] 乘積族 ∏ a_i^{e_i} (≤2 因子, e = k/4, |k| ≤ 80) ───")
consts = {'φ': float(phi), '137': 137.0, '88': 88.0, '90': 90.0, '45': 45.0, '44': 44.0,
          '33': 33.0, '123': 123.0, '61.5': 61.5, '134': 134.0, '176': 176.0,
          '√2': float(sqrt(2)), 'π': float(pi), 'e': float(mp.e), '53': 53.0, '55': 55.0}
exps = [k / 4.0 for k in range(-80, 81) if k != 0]
keys = sorted(consts.keys())
logs10 = {k: math.log10(consts[k]) for k in keys}
prod_logs = set()
prod_best = []          # (dev, 描述) 供陷阱示範
for i, k1 in enumerate(keys):
    for e1 in exps:
        v1 = e1 * logs10[k1]
        prod_logs.add(v1)
        prod_best.append((abs(10.0 ** (v1 - LOG10_N) - 1.0), f"{k1}^{e1:+.2f}"))
        for k2 in keys[i + 1:]:
            for e2 in exps:
                v = v1 + e2 * logs10[k2]
                prod_logs.add(v)
                prod_best.append((abs(10.0 ** (v - LOG10_N) - 1.0), f"{k1}^{e1:+.2f}·{k2}^{e2:+.2f}"))
prod_logs = sorted(prod_logs)
prod_best.sort()
print(f"  候選數 = {len(prod_logs)}; 最佳命中 dev = {nearest_dev(prod_logs, LOG10_N):.3e}")
for t in TOL:
    print(f"    容差 {t:.0e}: {count_within(prod_logs, LOG10_N, t)} 命中")
print("  ★ 陷阱示範 (最佳 3 個乘積構造 — 密度產物, 唔係候選):")
for d, desc in prod_best[:3]:
    print(f"     {desc:34s} dev = {d:.3e}")
results.append(True)

# ═══ [D] 隨機 null ═══
print("\n─── [D] 隨機 null (200 個同量級目標) ───")
merged = sorted(set(fam_phi) | set(fam_137) | set(prod_logs))
random.seed(20261018)
fp = {t: 0 for t in TOL}
for _ in range(200):
    tgt = random.uniform(LOG10_N - 0.5, LOG10_N + 0.5)
    b = nearest_dev(merged, tgt)
    for t in TOL:
        if b < t:
            fp[t] += 1
print(f"  合併族候選 = {len(merged)}")
for t in TOL:
    print(f"    容差 {t:.0e}: {fp[t]}/200 = {fp[t]/2:.1f}% 假陽率")
ok_d = fp[1e-3] >= 40
print(f"  {'✅ PASS' if ok_d else '❌ FAIL'} null 假陽率 @1e−3 = {fp[1e-3]/2:.0f}% (>20% ⟹ 命中弱資訊)")
results.append(ok_d)

# ═══ [E] 過度吻合判準 + 盲測協議 ═══
print("\n─── [E] 過度吻合判準 (方法論定理 5) + ★ 盲測協議 ───")
print(f"  φ^x 指數級敏感: dM₀/dx = M₀·ln φ = {mp.nstr(M0 * log(phi) / 1e6, 8)} MeV")
print("  輸入精度 ~1e−3 ⟹ 指數可辨識精度 Δx ≈ 2.1e−3 ⟹ 優於此之讀法 = 反解 (docs/36)")
print("  ★ protocol (未來候選必須同時滿足):")
print("     (i) 離散 + 機制強迫 — 由已推導機制得出, 非有理逼近")
print("     (ii) 唔優於輸入精度 — |dev| 唔可以細過輸入量之精度")
print("     (iii) 樣本外命中 — 同機制須獨立預言另一量 (m_7 / κ / η_B)")
results.append(True)

# ═══ [F] 判定 ═══
print("\n─── [F] 判定: N 之結構來源 ───")
print(f"  1. 密集 φ^x 族最佳命中 = {nearest_dev(fam_phi, LOG10_N):.3e}; 137^k 族 = {nearest_dev(fam_137, LOG10_N):.3e}")
print(f"  2. 乘積族最佳命中 = {nearest_dev(prod_logs, LOG10_N):.3e}")
print(f"  3. 隨機 null @1e−3 假陽率 = {fp[1e-3]/2:.0f}% ⟹ 『搵到命中』唔帶決定性資訊")
print("  4. 過度吻合判準: 優於 Δx ≈ 2.1e−3 嘅讀法 = 反解 ⟹ 不可作證據")
print("  5. ⟹ N 之結構來源【未找到】; M₀ 標度本輪維持 🔴 (維度側已閉合)")
print("  ★ 進展: (H₀ 外部 + x) 2 自由參數 → (ω_ring 內部閉合 + N 未知) 1 未知純數")
results.append(True)

print(f"\n{'='*78}")
print(f"  結果: {sum(results)}/{len(results)} PASS (報告型: A–F 全列舉)")
print("=" * 78)