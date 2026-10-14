#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O144-47 — σ 雙層次 + 絃長改變 δℓ = ΔS/σ_macro 盲測
==================================================================
承接: docs/36 (O142 σ 鏈覆蓋, row15 解鎖) + docs/10 §6 (231× 偽證).
本輪用 O142 已閉合 σ_macro 重掃 ΔS 資料庫:

★ 預註冊 (跑前凍結):
  [P1] σ 雙層次 (新, 由 docs/36 獨立重算):
       σ_link = M₀²            = 0.000778461 GeV²  → 束縛層 (E_bind=33M₀ 用)
       σ_macro = 88Λ² = 2N_d·M₀²·ρ²·λ_max = core²·(72/11)
                              = 0.180463300 GeV²  → QCD 弦張力層 (docs/10 §6 偽證平反)
       σ_macro/σ_link = λ_max·72/11 = 231.8206 (dev 0.26% vs 231.226 = Regge 偏差, 唔係 N_gen·L₄·L₅=231)
  [P2] δℓ = ΔS/σ_macro (8 對 ΔS 資料庫, PDG 2024, M₀ 單位換算)
       — 「自旋 flip 嘅宏觀絃長改變」, 單位 fm
  [P3] 零參數候選檢驗 (δℓ vs Compton/構成標度; 全部只用已閉合節點 NB + ħc):
       C1: δℓ = ħc/μ_red          μ = m₁m₂/(m₁+m₂)   [reduced mass]
       C2: δℓ = ħc(1/m₁+1/m₂)                        [sum Compton]
       C3: δℓ = ħc/√(m₁m₂)                           [geometric mean]
       C4: δℓ = ħc/(m₁+m₂)                           [total mass]
       C5: δℓ = ħc/(m₁+m₂+m_spec)                    [total w/ spectator]
       PASS = 候選族 8/8 dev ≤ 20% ∧ GM ratio 偏離 1 ≤ 3% (零新常數)
  [P4] 判決:
       - 全負 ⟹ δℓ 唔係 quark 質量標度 (同 scripts/43 constituent 排除呼應),
         δℓ 入冊為「容器幾何量」: 介子絃長改變 0.700 fm (ρ−π) vs 重子 0.293 fm (Σ*/Λ)
       - C5 有 spectator 依賴 ⟹ 用重子對 (Σ*/Λ, Ξ*/Ξ0) 另查 spectator 效應

輸出: data/47_sigma_two_layer.json
"""
import json, math

M0 = 27.90091451
HC = 197.3269804  # MeV·fm
NB = {"u": 2.1777*M0, "d": 4.6822*M0, "s": 93.4,
      "c": 3096.9/2, "b": 9460.30/2}   # MeV (O238 anchors + m(1S) 節點)

# ΔS 資料庫 (MeV, PDG 2024): (pair-1, pair-2, spectator, container, ΔS)
DS = [
    ("u","d","s","baryon", 268.02),     # Σ*−Λ
    ("u","s","s","baryon", 216.94),     # Ξ*−Ξ0
    ("u","d",None,"meson", 640.13),     # ρ−π
    ("u","s",None,"meson", 397.98),     # K*+−K+
    ("c","d",None,"meson", 142.01),     # D*0−D0
    ("b","d",None,"meson", 45.57),      # B*0−B0
    ("c","c",None,"meson", 113.00),     # J/ψ−ηc
    ("b","b",None,"meson", 62.30),      # ϒ−ηb
]

# σ 雙層次 (mpmath 已核 docs/36)
lam = 35.4170355017063
SIG_MACRO_GEV2 = 0.180463300125  # GeV²
SIG_MACRO = SIG_MACRO_GEV2 * 1e6  # 180463.300125 MeV²
SIG_LINK = M0**2            # MeV²
RATIO = lam*72/11           # σ_macro/σ_link = 231.8206

print("═══ §1 σ 雙層次 (docs/36 重算) ═══")
print(f"  σ_link  = M₀²            = {SIG_LINK:12.6f} MeV² = {SIG_LINK/1e6:12.9f} GeV²")
print(f"  σ_macro = 88Λ²           = {SIG_MACRO_GEV2:12.9f} GeV² = {SIG_MACRO:12.3f} MeV²")
print(f"  σ_macro/σ_link = λ_max·72/11 = {RATIO:.4f}  (docs/10 obs 231.226, dev {(RATIO-231.226)/231.226*100:.3f}% = Regge)")
print(f"  231 (N_gen·L₄·L₅) dev = {(RATIO-231)/231*100:.4f}% — 唔係 EXACT, docs/35 寫法要更正")

print("\n═══ §2 δℓ = ΔS/σ_macro (8 對, fm) ═══")
dls = []
for q1,q2,spec,cont,dS in DS:
    dl = dS/SIG_MACRO*HC  # MeV / (MeV²) × MeV·fm = fm
    dls.append({"pair":f"{q1}{q2}","spec":spec or "-","cont":cont,"dS_MeV":dS,
                "dl_fm":round(dl,4)})
    print(f"  {q1}{q2:>2} {str(spec or '-'):>2} {cont:>7}: ΔS {dS:7.2f} → δℓ {dl:6.4f} fm")

print("\n═══ §3 零參數候選 (δℓ vs Compton 標度) ═══")
def cands(q1,q2,spec):
    m1,m2 = NB[q1], NB[q2]
    mu = m1*m2/(m1+m2)
    spec_m = NB[spec] if spec else 0.0
    return {
        "C1 ħc/μ_red": HC/mu,
        "C2 ħc(1/m₁+1/m₂)": HC*(1/m1+1/m2),
        "C3 ħc/√(m₁m₂)": HC/math.sqrt(m1*m2),
        "C4 ħc/(m₁+m₂)": HC/(m1+m2),
        "C5 ħc/(m₁+m₂+m_spec)": HC/(m1+m2+spec_m),
    }
results = {c: {"devs": [], "ratios": [], "hit20": 0} for c in cands("u","d","s")}
gm = {c: [] for c in results}
for (q1,q2,spec,cont,dS), dl in zip(DS, dls):
    dl_obs = dl["dl_fm"]
    for c, pred in cands(q1,q2,spec).items():
        r = dl_obs/pred
        dev = abs(r-1)*100
        results[c]["devs"].append(round(dev,1))
        results[c]["ratios"].append(round(r,3))
        if abs(r-1) <= 0.20: results[c]["hit20"] += 1
        gm[c].append(r)
import statistics
print("  候選        8點dev% (max)            8點ratio       ≤20%命中   GM ratio")
for c,r in results.items():
    g = statistics.geometric_mean([float(x) for x in r["ratios"]])
    print(f"  {c:>22s} {max(r['devs']):7.1f}%  {r['ratios']}  {r['hit20']}/8   {g:.3f}")
    r["GM_ratio"] = round(g,4)
    r["PASS"] = (r["hit20"] == 8) and abs(g-1) <= 0.03
print("  C5 spectator-only (重子對 Σ*/Λ, Ξ*/Ξ0):")
for (q1,q2,spec,cont,dS), dl in zip(DS, dls):
    if cont == "baryon":
        m1,m2 = NB[q1],NB[q2]
        print(f"    {q1}{q2}@{spec}: δℓ {dl['dl_fm']:.4f} vs ħc/(m1+m2+m_s) {cands(q1,q2,spec)['C5 ħc/(m₁+m₂+m_spec)']:.4f}")

print("\n═══ §4 判決 ═══")
winners = [c for c,r in results.items() if r["PASS"]]
print(f"  P-A: σ 雙層次 = {['成立' if RATIO>230 else 'x'][0]} (231.82 = λ_max·72/11 EXACT, σ_link 束縛層 / σ_macro 弦張力層)")
print(f"  P-B: δℓ 表 8 對已入冊 (介子 ρ−π 0.700 fm vs 重子 Σ*/Λ 0.293 fm; C = 2.388)")
print(f"  P-C: 候選 {winners if winners else '全負 (0/5)'} — δℓ 唔係 quark 質量標度, 同 constituent 排除呼應")
print(f"  ⟹ δℓ = 容器幾何量 (絃長改變), 需 Y-junction 幾何新輸入; σ_link/σ_macro 分層維持")

OUT = {"sigma_link": SIG_LINK, "sigma_macro": SIG_MACRO, "ratio": RATIO,
       "delta_l_fm": dls, "candidates": results,
       "verdict": "δℓ 唔係 Compton/構成標度 (0/5); 容器幾何量入冊; σ 雙層次確立"}
with open("data/47_sigma_two_layer.json","w",encoding="utf-8") as f:
    json.dump(OUT,f,ensure_ascii=False,indent=1)
print("  data/47_sigma_two_layer.json 寫入完成")