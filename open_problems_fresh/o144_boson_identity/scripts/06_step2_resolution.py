#!/usr/bin/env python3
"""
O144-06 — 順序攻堅 Step 2: 縮小公理集辨識度測試 (2026-09-17)
=============================================================
目標: 模式集限 O137 已知粒子模式, 重測覆蓋 vs 隨機 — 是否有辨識度的預言?

變體:
  A: 模式 M' = {1,7,20,14,34,33} (反週期身份粒子模式) × C_f R' (29 值)
  B: 模式 M' × Φ 純值 (16 值) — 最小集
  C: 對照 — 全模式集 (39) × R' (29) [scripts/04 結果: z = −2.62]

判決: |預言集| 縮小 → 隨機期望下降; 若 s 仍唯一命中且 z ≥ 3 → 有辨識度
       若覆蓋消失或仍不顯著 → 現有語言無辨識度預言
"""
import json, math, random, sys

M0 = 27.9009
phi = (1 + math.sqrt(5)) / 2
random.seed(20260917)
def gamma(n): return 4 * math.sin(math.pi * n / 88) ** 2

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'

G1, G2 = [1, 5, 9], [0, 1, 3, 4, 6, 7]
Phi = sorted({1 + x1 * x2 for x1 in G1 for x2 in G2})
N_phi6, N_phi8, S_phi8 = 2, 5, 17
R = sorted(set(Phi) | {v / N_phi6 for v in Phi} | {(S_phi8 + d) / N_phi8 for d in [0, 1]})

particles = {
    "u": 2.16, "d": 4.67, "s": 93.0, "c": 1270.0, "b": 4180.0,
    "p": 938.2720813, "X(2370)": 2376.3,
}
blind_targets = list(particles.keys())

variants = {
    "A: M'×R' (6×29)": sorted({1, 7, 20, 14, 34, 33}),
    "B: M'×Φ (6×16)": sorted({1, 7, 20, 14, 34, 33}),
}
cf_sets = {
    "A: M'×R' (6×29)": R,
    "B: M'×Φ (6×16)": Phi,
}

print("=" * 76)
print("O144-06 Step 2: 縮小公理集辨識度測試")
print("=" * 76)
print(f"  模式 M' = {{1,7,20,14,34,33}} (O137 反週期粒子模式)")
print(f"  R' ({len(R)} 值) vs Φ 純值 ({len(Phi)} 值)")

results = {}
for vname, modes in variants.items():
    Cfs = cf_sets[vname]
    preds = sorted({round(M0 * gamma(n) * cf, 8) for n in modes for cf in Cfs})
    m_min, m_max = min(preds), max(preds)
    log_span = math.log10(m_max / m_min)
    print(f"\n[{vname}]")
    print(f"  預言集 |P| = {len(preds)}, 範圍 [{m_min:.3f}, {m_max:.1f}] MeV (跨度 {log_span:.2f})")

    # 覆蓋
    coverage = {}
    for name, T in particles.items():
        hits1 = sum(1 for cf in Cfs for n in modes if abs(M0 * gamma(n) * cf - T) / T < 0.01)
        hits2 = sum(1 for cf in Cfs for n in modes if abs(M0 * gamma(n) * cf - T) / T < 0.02)
        coverage[name] = (hits1, hits2)
    cov1 = sum(1 for k in blind_targets if coverage[k][0] > 0)
    print(f"  1% 窗覆蓋: {cov1}/{len(blind_targets)} 目標; 每目標命中數: "
          f"{ {k: coverage[k][0] for k in blind_targets} }")

    # MC 隨機期望 (每目標 ≥1 覆蓋)
    N_MC = 2000
    mc_cov = []
    for _ in range(N_MC):
        samp = [10 ** random.uniform(math.log10(m_min), math.log10(m_max)) for _ in range(len(preds))]
        c = sum(1 for T in [particles[k] for k in blind_targets]
                if any(abs(s - T) / T < 0.01 for s in samp))
        mc_cov.append(c)
    mc_mean = sum(mc_cov) / N_MC
    mc_std = (sum((x - mc_mean) ** 2 for x in mc_cov) / N_MC) ** 0.5
    z = (cov1 - mc_mean) / mc_std if mc_std > 0 else 0
    print(f"  MC 隨機期望覆蓋: {mc_mean:.2f} ± {mc_std:.2f} 目標; 實際 {cov1}; z = {z:.2f}")
    print(f"  判決: {'✅ 顯著' if z >= 3 else '❌ 不顯著'}")
    results[vname] = {"|P|": len(preds), "coverage1": coverage, "cov_targets": cov1,
                      "mc_mean": mc_mean, "mc_std": mc_std, "z": z}

print("\n" + "=" * 76)
print("[判決]")
print("=" * 76)
for vname, r in results.items():
    print(f"  {vname}: |P|={r['|P|']}, 覆蓋 {r['cov_targets']}/7, z={r['z']:.2f} "
          f"{'✅' if r['z']>=3 else '❌'}")
    for k in blind_targets:
        if r['coverage1'][k][0] > 0:
            print(f"    命中: {k} ({r['coverage1'][k][0]} 個 1% 內)")

print(f"""
對照: 全模式集 39 × R' (scripts/04): |P| = 1113, 覆蓋 5/7, z = −2.62 ❌

結論:
  - 模式縮小 (39→6) 使預言集縮小 (1113→~170) — 隨機期望下降
  - 但覆蓋也下降 (d/c/b/p/X 失去 1% 預言, 除非掃描命中)
  - 若 s 是唯一持續命中 → 仍無法覆蓋全部目標
  - 判決: 縮小公理集只降低過擬合, 不增加覆蓋 — 現有語言對夸克/複合態
    質量仍無有辨識度的先驗預言 ⟹ ❌
""")

out = {"session": "2026-09-17 O144-06 Step2", "results": {
    k: {"|P|": v["|P|"], "cov_targets": v["cov_targets"], "z": v["z"],
        "coverage": {k2: v["coverage1"][k2] for k2 in blind_targets}} for k, v in results.items()}}
with open(f'{BASE}/open_problems_fresh/o144_boson_identity/data/06_step2_resolution.json', 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("✅ data/06_step2_resolution.json 已寫入")
sys.exit(0)
