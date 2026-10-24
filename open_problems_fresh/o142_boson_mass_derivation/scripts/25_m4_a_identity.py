#!/usr/bin/env python3
"""O142 scripts/25 — M4 handoff 處理: A 譜身份可否由 σ 橋算子化

輸入
  M4 → O142 handoff 2026-10-24T13:23:34 (ref: m4 docs/19_delivery_processing.md)
  P6 01_problem_record §A: m_ν = A·γ_n²; A = 1.64337 eV/γ² (v_SM); m₁/₂/₃ = 0.0209452/0.0226848/0.0536815 eV

目標量
  x ≡ A/M₀ = 5.890022e-08  (M₀ = 27.900915 MeV, O142 docs/16 L58)

事前判準（寫死，先於任何掃描）
  U1  升格需 dev < 0.1%  ∧  MC density < 5%（P6/M4 同閘）
  U2  單一生成元可命中 ⟺ |x* − 最近整數| < 0.02，其中 x* = ln(x)/ln(g)
      （否則單元冪次結構上唔可能；唔准用非整數冪「湊」）
  U3  族成員預先宣告，跑完唔准加減

族（預先宣告，σ 橋算子代數）
  FA  (σ 橋純代數)      (Λ/M₀)^a · γ₂₀^b · γ₁^k , a,b ∈ [−6,6], k ∈ [−45,45]   (= 15379)
  FB  (FA / 結構分母)    FA / d, d ∈ D = {1,3,9,88,7744,5,25,7,49,11,121,4,16,21,441,41,45,60,90,123,421}
  FC  (P6/M4 式)         n·γ₁^k , n ∈ [1,200], k ∈ [−45,45]

密度定義（MC，種子寫死）
  目標 log-uniform ∈ [10⁻¹², 10⁰]；2×10⁵ 抽樣；tol = 0.1%（相對）
  density = P(隨機目標落入族任一成員 ±0.1% 帶)

執行: /usr/bin/python3 scripts/25_m4_a_identity.py
"""
import json
import math
import os
import sys

from mpmath import mp, mpf, sqrt, cos, sin, pi, log

mp.dps = 50

# ---------- 上游原定義（不重導）----------
M0_MeV = mpf("27.900915")          # O142 docs/16 L58
N_d = 88                           # L₄·L₅+N_gen
N_gen = 3
L4, L5, B, F5, F8 = 7, 11, 4, 5, 21
rho = mpf(N_gen) / mpf(L5)         # 3/11
g20 = 4 * cos(rho * pi) ** 2       # 4cos²(ρπ) = 4sin²(20π/88)
lam_max = mpf(36) - 1 / g20        # B·N_gen² − 1/γ₂₀
Lam_M0 = rho * sqrt(lam_max)       # Λ/M₀ = ρ√λ_max
g1 = 4 * sin(pi / N_d) ** 2        # γ₁ = 4sin²(π/88)

A_eV = mpf("1.64337")              # P6 v_SM 版（v=246.0 版 1.64044 保留）
x = A_eV / (M0_MeV * mpf("1e6"))   # 無量綱目標

print("=" * 78)
print("O142 scripts/25 — A 譜身份: σ 橋算子化可達性審計")
print("=" * 78)
print(f"M₀            = {mp.nstr(M0_MeV, 12)} MeV")
print(f"γ₁            = {mp.nstr(g1, 18)}")
print(f"γ₂₀           = {mp.nstr(g20, 18)}")
print(f"λ_max         = {mp.nstr(lam_max, 18)}")
print(f"Λ/M₀ = ρ√λ_max= {mp.nstr(Lam_M0, 18)}")
print(f"A             = {mp.nstr(A_eV, 10)} eV/γ²")
print(f"x = A/M₀      = {mp.nstr(x, 10)}  (={mp.nstr(x*1e8, 12)}e-8)")

# ---------- ① 核 M4 / P6 引用數字 ----------
print("\n① 核 M4 引用（獨立重算）")
checks = []
cand_87 = 87 * g1 ** 4 * M0_MeV * mpf("1e6")
dev87 = abs(cand_87 - A_eV) / A_eV
checks.append(("87·γ₁⁴·M₀ [eV]", mp.nstr(cand_87, 10), f"{float(dev87)*100:.4f}%",
               "M4: 1.63673 eV, 0.404%"))
barrier = g1 / x
checks.append(("量級障 γ₁/x", mp.nstr(barrier, 10), "—", "M4: 86515×"))
x_m4 = mpf("5.890022e-8")
checks.append(("x vs M4 值", mp.nstr(x, 12), f"{float(abs(x-x_m4)/x)*100:.5f}%", "M4: 5.890022e-08"))
for name, val, dev, note in checks:
    print(f"  {name:22s} = {val:>18s}   Δ={dev:>9s}   [{note}]")

# ---------- ② 事前族宣告 + 單元判據 U2 ----------
print("\n② 單元可達性（U2：|x*−最近整數| < 0.02）")
for label, g in (("Λ/M₀", Lam_M0), ("γ₂₀", g20), ("γ₁", g1)):
    xs = log(x) / log(g)
    nearest = int(mp.nint(xs))
    print(f"  g = {label:6s} = {mp.nstr(g, 10):>16s} → x* = {mp.nstr(xs, 8):>12s}"
          f"  最近整數 {nearest:+d}  殘距 {mp.nstr(abs(xs-nearest), 6)}"
          f"  {'✅可達' if abs(xs-nearest) < mpf('0.02') else '🔴 結構上唔可能（單元）'}")

# ---------- ③ 族成員 + 最佳命中 ----------
D = [1, 3, 9, 88, 88 * 88, 5, 25, 7, 49, 11, 121, 4, 16, 21, 441, 41, 45, 60, 90, 123, 421]

def fam_FA():
    for a in range(-6, 7):
        for b in range(-6, 7):
            base = (Lam_M0 ** a) * (g20 ** b)
            for k in range(-45, 46):
                yield base * (g1 ** k)

def fam_FB():
    for v in fam_FA():
        for d in D:
            yield v / d

def fam_FC():
    for n in range(1, 201):
        for k in range(-45, 46):
            yield n * (g1 ** k)

FAMS = [("FA σ橋純代數", fam_FA), ("FB FA/結構分母", fam_FB), ("FC n·γ₁^k", fam_FC)]

print("\n③ 族掃描（最佳命中）")
results = {}
for name, gen in FAMS:
    best = (mpf(0), None)
    cnt = 0
    for v in gen():
        if v <= 0:
            continue
        cnt += 1
        d = abs(v - x) / x
        if best[1] is None or d < best[0]:
            best = (d, v)
    results[name] = (cnt, best)
    print(f"  {name:16s} |members|={cnt:6d}  最佳 dev={float(best[0])*100:.4f}%"
          f"  值={mp.nstr(best[1], 10)}")

# ---------- ④ MC 密度（U1 第二閘）----------
print("\n④ MC density（10⁻¹²–10⁰ log-uniform, 2×10⁵, tol 0.1%）")
import random
rng = random.Random(20261024)
NT = 200000
toLs = [math.log10(rng.uniform(0, 1)) * 12 - 12 for _ in range(NT)]  # log10 uniform [-12,0]
targets = [10 ** t for t in toLs]
TOL = 1e-3

for name, gen in FAMS:
    vals = sorted(float(v) for v in gen() if v > 0)
    import bisect
    hit = 0
    for t in targets:
        lo = bisect.bisect_left(vals, t * (1 - TOL))
        if lo < len(vals) and vals[lo] <= t * (1 + TOL):
            hit += 1
    dens = hit / NT
    print(f"  {name:16s} density = {dens*100:.3f}%   "
          f"{'✅ <5%' if dens < 0.05 else '🔴 ≥5% 無鑑別力'}")

# ---------- ⑤ 判決 ----------
print("\n⑤ 判決")
devFA = float(results["FA σ橋純代數"][1][0])
print(f"  FA 最佳 dev = {devFA*100:.4f}%  → " + ("命中" if devFA < 1e-3 else "🔴 未達 0.1%"))
print("  結論: 見 docs/38（本腳本輸出為唯一數值依據）")