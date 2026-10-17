#!/usr/bin/env python3
"""
O252 — Script 11: depth 第二結構候選 + depth 相關性掃描 (2026-10-17)
=====================================================================
R5: τ_w=⟨hop⟩=4 係深度上限, SNR bias 否證 → depth 分佈要 per-source 解。
新候選 (O179 已閉合, 唔係 W 算子):
  D-e: τ_eff = ⟨hop⟩·(M₄/M₀) = 4·7/15 = 28/15 = 1.8667
       M₄/M₀ = 7/15 = L₄/(L₅+B) (O179: hop=4 波節質量 vs hop=0 錨點)
       → depth = 1−e^{−28/15} = 0.8454 vs obs 中位 0.816 (dev?)
       物理: 凝聚層唔係實心 — 有效遮蔽 = 凝聚重心質量 fraction
相關性掃描 (都唔係零常數預言, 只係診斷):
  [C1] corr(depth, |dv|) — 帶幾何預言 depth∝光程→|v|相關?
  [C2] corr(depth, σ_dip)
  [C3] corr(depth, 解像) — m vs h 深淺?
判定:
  [D1] τ_eff=28/15 中位命中 (dev<10%)
  [D2] τ_eff 上限? top-3 應該 ≤ 0.982 上限 (要有解釋)
  [C1]-[C3]: 診斷性, 唔改結構
"""
import json, math, os
import numpy as np

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
LOG = []
def ck(name, cond, detail=''):
    LOG.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

with open(f"{DATA}/07_full_sample_scan.json") as f:
    d7 = json.load(f)
res = [r for r in d7["results"] if r["sig"] and abs(r["dv"]) < 700 and r["depth"] < 1.2]

depths = np.array([r["depth"] for r in res])
dvs = np.array([abs(r["dv"]) for r in res])
sigs = np.array([r["sig_dip"] for r in res])
N = len(res)
print("="*84)
print("O252/11 — depth 結構候選 D-e + 相關性診斷")
print("="*84)

# D-e: τ_eff = ⟨hop⟩·M₄/M₀ = 4·(7/15)
tau_eff = 4.0*7/15
depth_pred = 1 - math.exp(-tau_eff)
med_obs = float(np.median(depths))
dev = abs(med_obs - depth_pred)/depth_pred*100
print(f"D-e: τ_eff = 4·7/15 = {tau_eff:.4f} → depth_pred = {depth_pred:.4f} vs obs 中位 {med_obs:.4f} (dev {dev:.2f}%)")
ck("D1 τ_eff=28/15 中位命中 (dev<10%)", dev < 10, f"dev {dev:.2f}%")

# 上限: top-3
top3 = sorted(res, key=lambda r: -r["depth"])[:3]
t3m = np.mean([r["depth"] for r in top3])
print(f"top-3 depth mean = {t3m:.3f} (上限 τ_w=4 → 0.9817; τ_eff → 0.845)")
ck("D2 top-3 近 τ_w=4 上限 (dev<8%)", abs(t3m-0.9817)/0.9817 < 0.08,
   f"top3={t3m:.3f} vs 0.9817 (dev {abs(t3m-0.9817)/0.9817*100:.1f}%)")

# C1: corr(depth, |dv|)
c1 = np.corrcoef(depths, dvs)[0,1]
ck("C1 corr(depth, |dv|) ~ 0 (帶幾何唔主導)", abs(c1) < 0.4, f"ρ={c1:.3f}")

# C2: corr(depth, σ_dip)
c2 = np.corrcoef(depths, sigs)[0,1]
ck("C2 corr(depth, σ_dip) ~ 0", abs(c2) < 0.4, f"ρ={c2:.3f}")

# C3: m vs h (解像) depth
m_d = [r["depth"] for r in res if 'm' in str(r.get("fn","")) or True]
# script 07 冇存 grating 名 — 用 ΔAIC 同 σ 分: high σ>190 → 可能 h? 唔, 用入面已有 'grating' if any
gr = [r.get("grating","?") for r in res]
if any(g != "?" for g in gr):
    from collections import defaultdict
    byg = defaultdict(list)
    for r in res:
        byg[r.get("grating","?")].append(r["depth"])
    print("grating depth:", {k: round(float(np.median(v)),3) for k,v in byg.items()})
else:
    # 冇 grating info — 用 ΔAIC 近似 (h 高解像通常 ΔAIC 大): corr 已測 → 跳過
    print("C3: grating info 唔喺 data/07 — 用 ΔAIC proxy (G2/G4 已測 SNR) — 跳過")

# τ_eff 對每源? 冇 per-source 質量 → 只可以中位對照 (done)
data = {"tau_eff_4xM4": tau_eff, "depth_pred": depth_pred,
        "obs_median": med_obs, "dev_pct": dev,
        "top3_mean": t3m, "corr_depth_dv": c1, "corr_depth_sigma": c2,
        "note": "D-e 用 O179 M₄/M₀=7/15 質量 fraction; C1-C3 診斷性",
        "checks": [{"name": n, "pass": p, "detail": d} for n,p,d in LOG]}
with open(f"{DATA}/11_depth_structure.json","w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
np_ok = sum(1 for _,p,_ in LOG if p)
print(f"\n結果: {np_ok}/{len(LOG)} PASS → data/11_depth_structure.json")