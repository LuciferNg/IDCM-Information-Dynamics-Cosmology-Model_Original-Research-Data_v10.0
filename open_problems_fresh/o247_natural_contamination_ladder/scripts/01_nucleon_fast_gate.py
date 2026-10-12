#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""O247 Q2 快閘 01 — 核子層數字池密度判決 (判據預註冊)

調律者 2026-10-12: 本 session 集中 O247 只推質子、中子、原子。
docs/01 §二 快閘: n→p 質量差 2.53099 m_e / m_p/M₀ 33.63 / m_n/m_p 1.00143
過唔到池密度即刻入禁區，過到先算候選（O206 pool 密度先例 P=0.4175）。

判據（預註冊，跑前凍結）:
  G1 候選表: 5 個核子觀測量 (r1..r5) 對結構數池最近命中 + dev%
  G2 池密度: 每一量 (r_i) 以窗口 δ=1% 對同一池掃命中數; MC null = 同池抽
     log-uniform r∈[0.5,50] × 10000 次, 攞命中數分佈 → z = (obs−mean)/std
  G3 判決: z ≥ 5σ 先升候選; 3σ≤z<5σ = 線索非證據 (維持 O206 水平值裁決);
     z<3σ = 池密度否決, 入禁區 (唔重推)
  G4 三點檢定: 只有 z≥5σ 先做兄弟值檢查 (同一候選公式套鰶開其他核子量)

結構數池 (IDCM corpus 算子候選, 凍結):
  P_int = {1..20} ∪ {22,29,30,33,34,37,42,44,45,47,55,60,61,62,64,68,70,71,76,79,85,86,88,89,90,123,137,178,199,233,264,322,377,521,528,610,843,1364,1547,1554}
  P_phi = {φ^k: k=-5..10}  (φ=1.618.., 禁 0/負)
  P_lucas = {2,1,3,4,7,11,18,29,47,76,123,199,322,521,843,1364}
  P_fib   = {1,1,2,3,5,8,13,21,34,55,89,144,233,377,610,987}
  池 = P_int ∪ P_lucas ∪ P_fib ∪ P_phi ∪ {a/b: a,b ∈ P_int, b≠0, 簡化後 a,b ≤ 200}
      ∪ {k/88: k=1..88}
      去重後全池大小記入 log (池規模係密度判定一部份)

觀測值 (PDG 2024 / O38):
  M₀ = 27.900915 MeV
  m_p = 938.27208816 MeV (PDG 2024)
  m_n = 939.5654205 MeV
  m_e = 0.51099895000 MeV
  r1 = m_p/M₀        (候選: 33.6287 — docs/01 已記「無意義」, 本 script 量度化)
  r2 = m_n/M₀        (33.6747)
  r3 = (m_n−m_p)/m_e  (2.53099 — docs/01 快閘目標)
  r4 = (m_n−m_p)/M₀  (0.046351)
  r5 = m_n/m_p        (1.0014286 — docs/01 1+1/700 線索)

輸出: G1/G2/G3 判決 + RESULT line
"""
import math
import random
import numpy as np

# ---------- 判據 ----------
DELTA_REL = 0.01          # 窗口 = 1% 相對 (凍結)
MC_N = 10000              # null 樣本
Z_GATE = 5.0              # 升候選閘
Z_LINE = 3.0              # 線索閘
logmin, logmax = 0.5, 50.0

# ---------- 結構數池 (凍結) ----------
P_int = set(range(1, 21)) | {22, 29, 30, 33, 34, 37, 42, 44, 45, 47, 55, 60, 61, 62,
                             64, 68, 70, 71, 76, 79, 85, 86, 88, 89, 90, 123, 137,
                             178, 199, 233, 264, 322, 377, 521, 528, 610, 843,
                             1364, 1547, 1554}
phi = (1 + math.sqrt(5)) / 2
P_phi = {phi ** k for k in range(-5, 11) if phi ** k > 0}
P_lucas = {2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322, 521, 843, 1364}
P_fib = {1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987}
pool = set(P_int) | P_phi | P_lucas | P_fib
# a/b 有理候選 (a,b ∈ P_int, 簡化)
fracs = set()
for a in P_int:
    for b in P_int:
        if b == 0:
            continue
        g = math.gcd(a, b)
        aa, bb = a // g, b // g
        if aa <= 200 and bb <= 200:
            fracs.add(aa / bb)
pool |= fracs
pool |= {k / 88 for k in range(1, 89)}
pool.discard(0.0)
pool_list = sorted(pool)

# ---------- 觀測 (PDG2024 / O38) ----------
M0 = 27.900915
mp = 938.27208816
mn = 939.5654205
me = 0.51099895000
obs = {
    "r1 m_p/M0":    mp / M0,
    "r2 m_n/M0":    mn / M0,
    "r3 (mn-mp)/me": (mn - mp) / me,
    "r4 (mn-mp)/M0": (mn - mp) / M0,
    "r5 m_n/m_p":   mn / mp,
}

def hits_in_window(r, pool_arr, rel=DELTA_REL):
    """池內候選命中數 (相對窗口)"""
    return int(np.sum(np.abs(pool_arr / r - 1.0) < rel))

pool_arr = np.array(pool_list)

# ---------- G1: 最近命中 ----------
print("=" * 78)
print("G1  候選表 (池=%d)" % len(pool_list))
print("=" * 78)
best = {}
for name, r in obs.items():
    dev = np.abs(pool_arr / r - 1.0)
    i = int(np.argmin(dev))
    print("%-14s r=%11.7f  最近: %-26.15g dev=%8.4f%%%s" % (
        name, r, pool_arr[i], dev[i] * 100,
        "  <-- 窗口內" if dev[i] < DELTA_REL else ""))
    best[name] = (pool_arr[i], dev[i])

# ---------- G2: MC null ----------
print()
print("=" * 78)
print("G2  池密度 MC null (窗口=%.0f%%, N=%d, log-uniform [%.1f,%.0f])" % (
    DELTA_REL * 100, MC_N, logmin, logmax))
print("=" * 78)
rng = np.random.default_rng(20261012)
logr = rng.uniform(math.log(logmin), math.log(logmax), size=MC_N)
null_r = np.exp(logr)
null_hits = np.array([hits_in_window(r, pool_arr) for r in null_r])
print("null 命中數: mean=%.3f std=%.3f max=%d" % (
    null_hits.mean(), null_hits.std(), null_hits.max()))
res = []
for name, r in obs.items():
    h = hits_in_window(r, pool_arr)
    if null_hits.std() > 0:
        z = (h - null_hits.mean()) / null_hits.std()
    else:
        z = float("inf")
    p_above = float(np.mean(null_hits >= h))
    tag = "升候選" if z >= Z_GATE else ("線索非證據" if z >= Z_LINE else "池密度否決")
    print("%-14s 命中=%d  z=%7.2f  P(≥)=%7.5f  ⟹ %s" % (name, h, z, p_above, tag))
    res.append((name, h, z, p_above, tag))

# ---------- G3: 判決 ----------
print()
print("=" * 78)
print("G3  判決")
print("=" * 78)
verdict = ["PASS" if tag == "升候選" else ("LINE" if "線索" in tag else "FAIL")
           for _, _, _, _, tag in res]
for (name, h, z, p, tag), v in zip(res, verdict):
    print("%-14s %s" % (name, v))
n_pass = verdict.count("PASS")
n_fail = verdict.count("FAIL")
n_line = verdict.count("LINE")
print()
print("RESULT: %d 檢查 (命中 %d + 線索 %d + 否決 %d)" % (
    len(verdict), n_pass, n_line, n_fail))