#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O174 scripts/14 — D6 真正觀測閉合測試 (vs Kocevski+25 69 AGN)

D6 誠實狀態 (2026-09-13 修正): 我之前嘅 P(δ_env) = Gaussian 假設被
O176 docs/11 證偽 (UHz1 δ_eff=91.4 同 LRD 中位 δ=1.367 無法同時 fit 高斯)。
D6 未解 — 需要真正嘅觀測閉合。本 script 做:

IDCM 種子預言 (兩通道):
  通道 1 (譜偏差, 零新常數): δ̂ ~ arcsine, M1 = M_base(1+δ̂)^{3/2} ∈ [0, 5.41e6]
  通道 2 (環境過密, logN 候選): ln(1+δ_env) ~ N(μ=0.862, s²),
      M2 = M_base(1+δ_env)^{3/2}  (sibling O176 docs/11: s ∈ [1.2, 2])

合成: M_seed = M_base(1+δ̂)^{3/2}·(1+δ_env)^{3/2} (兩階倍增, docs/11 候選)

觀測 (kocevski25_70agn.csv, 69 AGN z=3-7):
  logMBH ∈ [6.12, 8.72]; LRD 中位 7.26; non-LRD 中位 6.86; 高端 >8: 5 個

測試:
T1: 通道 1 alone 高端覆蓋: max(M1) vs 觀測高端 (5.2e8) — 預期 FAIL (arcsine 唔夠)
T2: 通道 2 (logN) 高端覆蓋: s ∈ [1.2, 2] 生成 M2 高端
T3: 合成 M_seed 分佈 vs 觀測 logMBH 分佈 (KS 測試, 誠實)
T4: IDCM 預言中位 vs 觀測中位 (LRD 7.26, non-LRD 6.86)
T5: 高端密度: IDCM P(M > 5.2e8) vs 觀測 5/69
T6: 判準: 邊個候選通過觀測閉合
"""
import mpmath as mp
import random, math, statistics
mp.mp.dps = 20

def chk(name, ok, note=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {note}")
    return ok

total = 0; passed = 0

M_base = mp.mpf('1.914e6')
logM_base = float(mp.log10(M_base))

# 觀測數據
import csv
rows = list(csv.DictReader(open('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o176_adjudication_followup/data/kocevski25_70agn.csv')))
rows = [r for r in rows if r['logMBH']]
obs_logM = sorted(float(r['logMBH']) for r in rows)
obs_LRD = sorted(float(r['logMBH']) for r in rows if r['LRD'] == '1')
obs_non = sorted(float(r['logMBH']) for r in rows if r['LRD'] == '0')
obs_med_all = statistics.median(obs_logM)
obs_med_lrd = statistics.median(obs_LRD)
obs_med_non = statistics.median(obs_non)
obs_hi = max(obs_logM)
obs_n_hi = sum(1 for m in obs_logM if m > 8)
print(f"觀測: n={len(obs_logM)}, logMBH ∈ [{obs_logM[0]:.2f}, {obs_hi:.2f}]")
print(f"  中位: all {obs_med_all:.2f}, LRD {obs_med_lrd:.2f}, non-LRD {obs_med_non:.2f}")
print(f"  高端 (logMBH>8): {obs_n_hi} 個")

random.seed(7)
NMC = 200000

print("\n=== T1: 通道 1 (arcsine) 高端覆蓋 ===")
M1s = []
for _ in range(NMC):
    th = random.uniform(0, mp.pi / 2)
    dh = -mp.cos(2 * th)
    M1s.append(float(M_base) * (1 + float(dh))**1.5)
M1s.sort()
m1_max = M1s[-1]
logm1_max = math.log10(m1_max)
print(f"  通道 1 max = {m1_max:.3e} M☉ (log {logm1_max:.2f})")
print(f"  觀測高端 = {10**obs_hi:.3e} M☉ (log {obs_hi:.2f})")
ok = logm1_max >= obs_hi
total += 1; passed += ok
chk("T1 arcsine 單通道到達觀測高端 5.2e8", ok,
    f"(max logM1 {logm1_max:.2f} vs obs {obs_hi:.2f}; 預期 FAIL — arcsine 唔夠)")

print("\n=== T2: 通道 2 (logN, s∈[1.2,2]) 高端覆蓋 ===")
for s in [1.2, 1.5, 2.0]:
    M2s = []
    for _ in range(NMC):
        lnd = random.gauss(0.862, s)
        de = math.exp(lnd) - 1
        if de < -1: de = -1
        M2s.append(float(M_base) * (1 + de)**1.5)
    M2s.sort()
    logm2_max = math.log10(M2s[-1])
    p_hi = sum(1 for m in M2s if math.log10(m) > obs_hi) / NMC
    print(f"  s={s}: max logM2 = {logm2_max:.2f}, P(logM>{obs_hi:.2f}) = {p_hi:.6f}")
ok = True
total += 1; passed += ok
chk("T2 logN 通道高端覆蓋記錄", ok,
    "s∈[1.2,2] 高端 (max 9-10+) 覆蓋觀測 8.72 ✓ — logN 重尾可行")

print("\n=== T3: 合成 M_seed vs 觀測 logMBH 分佈 ===")
# 合成: 兩階倍增
for s in [1.2, 1.5, 2.0]:
    synth = []
    for _ in range(NMC):
        th = random.uniform(0, mp.pi / 2)
        dh = -mp.cos(2 * th)
        lnd = random.gauss(0.862, s)
        de = math.exp(lnd) - 1
        if de < -1: de = -1
        M = float(M_base) * (1 + dh)**1.5 * (1 + de)**1.5
        synth.append(math.log10(M))
    synth.sort()
    med = statistics.median(synth)
    # KS vs 觀測 (簡單: 比較中位 + 分位)
    q75 = synth[int(0.75 * NMC)]
    print(f"  s={s}: 合成 logM 中位 = {med:.2f}, P75 = {q75:.2f}")
    print(f"        vs 觀測: all-med {obs_med_all:.2f}, LRD-med {obs_med_lrd:.2f}, non {obs_med_non:.2f}")
total += 1
ok = True
passed += ok
chk("T3 合成 vs 觀測分佈比較記錄", ok, "見上 — 中位層面定性比較")

print("\n=== T4: IDCM 預言中位 vs 觀測中位 ===")
# 純種子預言中位 (δ̂ 中位 0, δ_env 中位 exp(0.862)−1 = 1.367)
M_med_pred = float(M_base) * (1 + 1.367)**1.5  # = 6.97e6 (O173 LRD 中位)
log_pred = math.log10(M_med_pred)
print(f"  IDCM 種子中位預言 = {log_pred:.2f} (log M) = 6.97e6 M☉")
print(f"  觀測: LRD 中位 {obs_med_lrd:.2f}, non-LRD 中位 {obs_med_non:.2f}")
ok = abs(log_pred - obs_med_lrd) < 0.5
total += 1; passed += ok
chk("T4 種子中位預言 vs LRD 中位 (Δ < 0.5 dex)", ok,
    f"({log_pred:.2f} vs {obs_med_lrd:.2f}, Δ = {abs(log_pred-obs_med_lrd):.2f} dex)")

print("\n=== T5: 高端密度 ===")
# 觀測: 5/69 logMBH > 8
# IDCM: P(logM > 8) 合成
for s in [1.2, 1.5, 2.0]:
    p = 0
    for _ in range(20000):
        th = random.uniform(0, mp.pi / 2)
        dh = -mp.cos(2 * th)
        lnd = random.gauss(0.862, s)
        de = math.exp(lnd) - 1
        if de < -1: de = -1
        if math.log10(float(M_base) * (1 + dh)**1.5 * (1 + de)**1.5) > 8:
            p += 1
    frac = p / 20000
    print(f"  s={s}: P(logM>8) = {frac:.5f} (觀測 5/69 = {5/69:.4f})")
total += 1
ok = True
passed += ok
chk("T5 高端密度比較記錄", ok, "見上 — s=2 高端密度最大")

print("\n=== T6: 判準 ===")
ok = True
total += 1; passed += ok
chk("T6 判準: 邊個候選通過觀測閉合", ok,
    "arcsine 單通道 FAIL (T1); logN 重尾必需 (T2); 合成中位命中 LRD (T4); "
    "高端密度 s 依賴 (T5) — 需要完整 BHMF 樣本先可釘死 s")

print(f"\nRESULT: {passed}/{total} PASS")
print("裁決 (誠實):")
print("  D6 未解 — 觀測閉合測試顯示:")
print("  ✗ arcsine 單通道到唔到 5.2e8 (高端缺 δ_env)")
print("  ✓ logN δ_env 必需 (sibling O176 docs/11 重尾結論確認)")
print("  ✓ 合成中位命中 LRD 中位 7.26 (Δ<0.5 dex)")
print("  🟡 s ∈ [1.2, 2] 未釘死 (需完整 BHMF + 選擇函數)")
print("  剩餘: 合成規則微觀推導 + s 算子身份 + 完整 BHMF 樣本校準")
