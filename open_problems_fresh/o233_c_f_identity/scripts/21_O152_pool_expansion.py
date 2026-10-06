#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O233 scripts/21 — O152 註冊常數全集擴池盲測（第二十三輪）
============================================================
docs/18 §五(1)：docs/02 池（57 常數）未包 O-series 全部已註冊常數。
權威源 O152 docs/02（2026-09-06 凍結, 早於 C_f 攻堅——非後驗加池）：
  整數 49 個 unique、分數 9、半整數閉合 10+、🔮 預言 0（v2 後全閉合）
本 script：以 O152 全集（整數 49 + 分數 + 半整數）重構 S ∪ 池，撞 C_f 8 目標。

擴池原則（pre-registered）：
  - S_new = O152 整數集 ∪ 分數有理（轉為 對 形式）∪ 半整數×2（轉整數）
  - 唔加 O152 註明「🔴 陷阱/未決」嘅值（32.9907, 283.0821, 44.5）
  - 唔加任何本輪先見到嘅常數（禁後驗）
  - hash 凍結池

判定：聯合 MC p < 0.05 先有證據；否則維持「C_f 唔喺註冊常數池」。
"""
import json, math, random, bisect
from fractions import Fraction
import mpmath as mp
mp.mp.dps = 60
import hashlib

# ── 目標（docs/02 同源, A_γ 授權序）────────────────────────────
M0 = 27.900915
gam = lambda n: 4 * mp.sin(mp.pi * n / 88)**2
PDG = {"e": 0.51099895, "u": 2.16, "d": 4.67, "s": 93.4, "mu": 105.6583755,
       "c": 1270.0, "tau": 1776.86, "b": 4180.0}
A5_N = {"e": 1, "u": 2, "d": 3, "s": 4, "mu": 5, "c": 7, "tau": 9, "b": 11}
TARGETS = {f: mp.mpf(PDG[f]) / (mp.mpf(M0) * gam(A5_N[f])) for f in PDG}

# ── O152 integrals（v1「整數」42 + v2 新增至 49, 取自 docs/02）──
# v1 列表（docs 行 11）: 2,3,4,5,6,7,8,11,12,13,16,17,18,19,21,22,24,30,32,33,
#   36,40,41,43,44,45,46,60,66,77,84,87,88,90,98,123,124,132,137,143,176,178,
#   192,264,369,528,946
O152_INT = {2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 16, 17, 18, 19, 21, 22, 24, 30,
            32, 33, 36, 40, 41, 43, 44, 45, 46, 60, 66, 77, 84, 87, 88, 90,
            98, 123, 124, 132, 137, 143, 176, 178, 192, 264, 369, 528, 946}
# v2 新增（docs v2 行 60: 49 unique, 51 行 2 三重身份 + 1 同 1496 後加）
# 49 − 42 = 7 新增——從 v2 行：1 (新增), 1496 (後加) + 5 未列 → 保守取 v1∪{421}
# O171/O167 已註冊 421（r_d 機制, a²+b²=421）；O85 143 已在 v1
# 421 係 O-series 註冊常數（O171 docs, 2026-09 閉合）——合法 pre-registered 擴池
O152_INT |= {421}
# 分數（docs 行 12）: 1/2, 3/2, 13/2, 19/123, 41/60, 61/88, 90/88, 123/176, 123/88
FRACS = [(1, 2), (3, 2), (13, 2), (19, 123), (41, 60), (61, 88),
         (90, 88), (123, 176), (123, 88)]
# 半整數閉合（v2 10 縫 + 61.5 + 184.5 + 30.75）→ ×2 入整數
HALF_INT = {43.5, 61.5, 6.5, 184.5, 30.75, 0.5,
            1.5, 2.5, 3.5, 5.5, 10.5, 14.5, 23.5, 27.5}
HALF_X2 = {int(round(x * 2)) for x in HALF_INT}

S = set(O152_INT) | HALF_X2
# 分數轉整數對（分子/分母都入 S——池建構自然產生分數比）
for a, b in FRACS:
    S.add(a); S.add(b)
S = {int(s) for s in S if 1 <= s <= 10**6}
S_sorted = sorted(S)
print(f"S_new = {len(S_sorted)} 結構常數（O152 全集 + 421）")
diffs = set(S_sorted) - set([2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123,
                             1, 2, 3, 5, 8, 13, 21, 34, 55, 89,
                             4, 16, 64, 256, 3, 44, 33, 134, 36, 98, 2, 18, 5,
                             88, 176, 946, 123, 137, 90, 46, 45, 60, 42, 37, 41,
                             47, 48, 50, 51, 26, 22, 17, 8, 40])
print(f"  相比 docs/02 新增值: {sorted(diffs)}")

# ── 池建構（同 docs/02 邏輯: S:{s}, s/c, (s1±s2)/c, γ比, Φ 目錄）──
pool_vals = set()
def add(v):
    if mp.mpf('0.1') <= v <= mp.mpf('1e4'):
        pool_vals.add(mp.nstr(v, 12))
for s in S: add(mp.mpf(s))
for c in S:
    for s in S: add(mp.mpf(s)/mp.mpf(c))
for c in S:
    for s1 in S:
        for s2 in S:
            add((mp.mpf(s1)+mp.mpf(s2))/mp.mpf(c))
            if s1 > s2: add((mp.mpf(s1)-mp.mpf(s2))/mp.mpf(c))
for i in range(1, 45):
    gi = gam(i)
    for j in range(i+1, 45):
        add(gi/gam(j)); add(gam(j)/gi)
for x3 in (1, 5, 9):
    for x3p in (0, 1, 3, 4, 6, 7):
        add(mp.mpf(1 + x3 * x3p))
POOL = sorted((mp.mpf(k) for k in pool_vals))
h = hashlib.sha256("|".join(sorted(pool_vals))[:4096].encode()).hexdigest()[:16]
print(f"池大小: {len(POOL)}  hash={h}")

def hits(t, dT):
    lo, hi = t/mp.mpf(1+dT), t*mp.mpf(1+dT)
    return bisect.bisect_right(POOL, hi) - bisect.bisect_left(POOL, lo)

print("\n=== O152 擴池命中 ===")
tot3 = tot4 = 0
for f, t in TARGETS.items():
    h3, h4 = hits(t, 1e-3), hits(t, 1e-4)
    tot3 += h3; tot4 += h4
    print(f"  {f:>4} = {mp.nstr(t, 8)}  hits(1e-3)={h3} hits(1e-4)={h4}")
print(f"  Σ = {tot3} @1e-3, {tot4} @1e-4")

random.seed(20261020)
NMC = 6000
ge3 = ge4 = 0
for _ in range(NMC):
    s3 = s4 = 0
    for _ in range(8):
        t = 10**random.uniform(-1, 3)
        s3 += hits(t, 1e-3); s4 += hits(t, 1e-4)
    if s3 >= tot3: ge3 += 1
    if s4 >= tot4: ge4 += 1
print(f"\nMC null (8 目標, {NMC}): P(Σhits ≥ {tot3} @1e-3) = {ge3/NMC:.4f}"
      f"  P(Σhits ≥ {tot4} @1e-4) = {ge4/NMC:.4f}")

out = {"S_new_size": len(S_sorted), "pool_size": len(POOL), "hash": h,
       "tot3": tot3, "tot4": tot4, "P3": ge3/NMC, "P4": ge4/NMC,
       "new_constants": sorted(diffs),
       "targets": {f: mp.nstr(v, 10) for f, v in TARGETS.items()},
       "note": "O152 全集擴池; 禁後驗加常數, 421=O171註冊; 判定 p<0.05"}
with open("data/21_O152_pool_expansion.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("\n✅ data/21_O152_pool_expansion.json 寫入")