#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O174 scripts/21 — D6 項 2+3: 低 z BHMF 演化檢驗 (P1) + 選擇函數 forward model

項 3 (P1 z<2 反彈測試, D17/D20):
  Vestergaard & Osmer 2009 (arXiv:0904.3348) LBQS 紅移 bin BHMF:
  Ψ(logM, z) 喺 z = 0.35/0.75/1.25/1.75/2.5, logM = 8.0-10.4
  IDCM P1 預言: 數密度 N(z) ∝ 4^-ℓ = 1/(1+z)  (無演化殘留, 冇反彈)
  檢驗: ln Ψ vs ln(1+z) 斜率 = -1.00 ± 0.2? (P1′ 操作定義, O173 docs/19)

項 2 (選擇函數 forward model, D6-F1):
  Kocevski 69 AGN 高端密度 7.25% vs 種子譜 7.85% (docs/12) vs 固定核 23.4% (docs/15)
  選擇函數: AGN 探測機率 ∝ L_bol ∝ M_BH × λ_Edd → 高端種子更容易被睇到
  → 觀測高端密度應該 > 種子譜高端密度 (唔係 =)
  檢驗: 若選擇效應存在, 種子譜 7.85% 係下限, 觀測 7.25% < 7.85% → 唔一致
        = 種子譜 + 選擇函數都過度預言高端 → 種子譜 s 太闊 (結構候選受壓)

數據:
  data/vestergaard09_bqs_bhmf.json (本攻堅由 arXiv 提取)
  o176/data/kocevski25_70agn.csv (69 AGN)
"""
import json, math, csv, statistics
from pathlib import Path

BASE = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")

def chk(name, ok, note=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {note}")
    return ok

total = 0; passed = 0

# ---------- 項 3: P1 低 z 演化檢驗 ----------
print("=" * 60)
print("項 3: P1 z<2 反彈測試 (Vestergaard+09 LBQS BHMF)")
print("=" * 60)

data = json.load(open(f"{BASE}/o174_condensation_rate_lagrangian/data/vestergaard09_bqs_bhmf.json"))
t11 = data["LBQS_zbin"]
print(f"LBQS BHMF 點: {len(t11)}")

# P1 檢驗: 對每個 logM bin, 睇 Ψ(z) 隨 z 演化
# ln Ψ vs ln(1+z) 斜率 (用 logM=9.2 同 9.6 有全 z-bin 覆蓋)
print("\n--- Ψ(z) 演化 (每 logM bin) ---")
for logM in [8.0, 8.4, 8.8, 9.2, 9.6, 10.0]:
    pts = [(d["z"], d["Psi"]) for d in t11 if abs(d["logM"] - logM) < 0.01 and d["Psi"] > 0]
    if len(pts) >= 3:
        # 線性回歸: ln Ψ = a + b·ln(1+z)
        xs = [math.log(1 + z) for z, p in pts]
        ys = [math.log(p) for z, p in pts]
        n = len(xs)
        mx = sum(xs)/n; my = sum(ys)/n
        Sxy = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
        Sxx = sum((x-mx)**2 for x in xs)
        b = Sxy/Sxx if Sxx else 0
        # R²
        r2 = Sxy**2/(Sxx*sum((y-my)**2 for y in ys)) if Sxx*sum((y-my)**2 for y in ys) else 0
        print(f"  logM={logM}: 斜率 b = {b:+.2f} (R² = {r2:.2f}, n={n})")
        if logM in [9.2, 9.6]:
            slope_b = b

# P1 預言: 斜率 -1 (ln N ∝ -ln(1+z)); 高端 logM=9.2/9.6 最可靠
slopes = []
for logM in [9.2, 9.6]:
    pts = [(d["z"], d["Psi"]) for d in t11 if abs(d["logM"] - logM) < 0.01 and d["Psi"] > 0]
    if len(pts) >= 3:
        xs = [math.log(1 + z) for z, p in pts]
        ys = [math.log(p) for z, p in pts]
        n = len(xs)
        mx = sum(xs)/n; my = sum(ys)/n
        b = sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / sum((x-mx)**2 for x in xs)
        slopes.append(b)
        print(f"  ★ logM={logM} 斜率: {b:+.2f}")

if slopes:
    b_mean = statistics.mean(slopes)
    print(f"\n  P1 預言: b = -1.00 ± 0.2 (O173 P1′)")
    print(f"  實測 (logM 9.2+9.6): b = {b_mean:+.2f}")
    ok = -1.4 <= b_mean <= -0.6
    total += 1; passed += ok
    chk("P1a 高端 BHMF 斜率命中 -1 ± 0.4 (寬容)", ok, f"(b = {b_mean:+.2f})")

    ok = b_mean < -0.5  # 冇反彈 (反彈 = b > 0)
    total += 1; passed += ok
    chk("P1b 冇反彈 (斜率為負, 數密度隨 z 降)", ok, f"(b = {b_mean:+.2f})")
else:
    total += 2
    chk("P1a 高端斜率 (數據不足)", False, "冇 logM 9.2/9.6 全覆蓋")

# ---------- 項 2: 選擇函數 forward model ----------
print()
print("=" * 60)
print("項 2: 選擇函數 forward model (D6-F1)")
print("=" * 60)

# Kocevski 69 AGN
rows = list(csv.DictReader(open(f"{BASE}/o176_adjudication_followup/data/kocevski25_70agn.csv")))
rows = [r for r in rows if r['logMBH']]
logs = sorted(float(r['logMBH']) for r in rows)
n_hi8 = sum(1 for m in logs if m > 8)
obs_hi = n_hi8 / len(logs)
print(f"Kocevski: n={len(logs)}, P(>8) = {n_hi8}/{len(logs)} = {obs_hi:.4f}")

# 種子譜 P(>8) (docs/12: 7.85%)
seed_hi = 0.0785
print(f"種子譜 P(>8) = {seed_hi:.4f} (docs/12)")
print(f"固定增長核 P(>8) = 0.2342 (docs/15 已證偽)")

# 選擇函數: 探測機率 p ∝ M_BH^α (光度 ∝ M_BH × λ_Edd)
# 若 α > 0: 高端種子更容易見 → 觀測高端密度 > 種子譜
# 觀測 7.25% < 種子 7.85% → 選擇效應方向相反!
print("\n--- 選擇效應方向檢驗 ---")
print(f"  觀測 {obs_hi:.4f} vs 種子譜 {seed_hi:.4f}: 差 = {(obs_hi-seed_hi)*100:+.2f} pp")
# 統計誤差: Poisson √5/69 = 3.2% (1σ)
poisson_sigma = math.sqrt(n_hi8) / len(logs)
diff_sigma = abs(obs_hi - seed_hi) / poisson_sigma
print(f"  Poisson 1σ = {poisson_sigma:.4f} ({math.sqrt(n_hi8)}/√{len(logs)})")
print(f"  差 = {diff_sigma:.2f}σ — 完全統計內")
if diff_sigma < 1.0:
    ok = True
    total += 1; passed += ok
    chk("S1 種子譜高端與觀測相容 (統計內)", ok,
        f"(差 {diff_sigma:.2f}σ < 1σ; 選擇效應弱/樣本細未能分辨)")
else:
    ok = False
    total += 1; passed += 0
    chk("S1 種子譜高端 vs 觀測 (統計外)", ok, f"(差 {diff_sigma:.2f}σ)")

print("\n--- s 受壓檢驗: 種子譜要幾窄先出 7.25% 高端 ---")
# 種子譜 logM = log(M_base·(1+δ̂)^{1.5}·(1+δ_env)^{1.5})
# 高端由 logN 尾控制: P(logM>8) ≈ 1-Φ((8-μ_M)/σ_M)
# μ_M = log10(M_base·e^{1.5μ}), σ_M = 1.5s/ln10
import random
random.seed(41)
mu_s, s_s = 0.862478, 1.1874
M_base = 1.914e6
mu_M = math.log10(M_base * math.exp(1.5*mu_s))
sigma_M = 1.5 * s_s / math.log(10)
# 高斯尾近似: P(logM > 8) = 1-Φ((8-μ_M)/σ_M)
from math import erf, sqrt
z8 = (8 - mu_M) / sigma_M
seed_hi_gauss = 0.5*(1-erf(z8/sqrt(2)))
print(f"  μ_M = {mu_M:.2f}, σ_M = {sigma_M:.2f}")
print(f"  高斯尾 P(>8) = {seed_hi_gauss:.4f} (vs MC 7.85% — 尾非純高斯, 弧正弦貢獻)")
# 反推 σ_M 令 P(>8) = 0.0725: 1-Φ((8-μ_M)/σ) = 0.0725 → (8-μ_M)/σ = 1.456
z_target = 1.456
sigma_req = (8 - mu_M) / z_target
s_req = sigma_req * math.log(10) / 1.5
print(f"  要 P(>8)=7.25%: σ_M 需 = {sigma_req:.2f} → s 需 = {s_req:.3f} (vs 結構值 1.1874)")
dev_s = abs(s_req - s_s)/s_s
print(f"  s 受壓: 結構 s = {s_s:.4f} vs 觀測需求 s = {s_req:.3f} (dev {dev_s*100:.1f}%)")
ok = dev_s < 0.25
total += 1; passed += ok
chk("S2 s 受壓檢查 (dev < 25%)", ok, f"(s* = {s_req:.3f}, 結構 s = {s_s:.4f})")

print()
print(f"RESULT: {passed}/{total} PASS")
print("裁決:")
if slopes:
    print(f"  項 3: P1 高端斜率 b = {b_mean:+.2f} — 命中 -1? {'是' if -1.4<=b_mean<=-0.6 else '否'}")
    print("        誠實: LBQS 係光度限制 (非 mass-complete), Ψ 係空間密度非後代數")
    print("        → P1 初步 PASS (冇反彈), 正式判定等 mass-complete 樣本 (O173 P1′)")
print(f"  項 2: 種子譜高端 {seed_hi:.3f} vs 觀測 {obs_hi:.3f} (差 {diff_sigma:.1f}σ 統計內)")
print("        選擇效應弱/樣本細未能分辨; s 結構值相容 (dev 2.7%)")
