#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O144-46 — 容器因子樣本外擴展: 4 點表 + C=2 檢驗 + 零參數候選批
==================================================================
承接: docs/32 (容器維度必在, C=2.388 單點)。本輪用**樣本外**重味重子
自旋分裂展開容器因子表:

★ 預註冊 (跑前凍結):
  [P1] 新數據 (PDG 2024, 樣本外 — 從未入過 O238/O144 fit):
       Σc(2455)0−Λc+ = 2453.75−2286.46 = 167.29 ± 0.20 MeV
       Σb0−Λb0     ≈ (5810.56+5815.64)/2 − 5619.60 = 193.50 ± 1.9 MeV
       Ξ*(1530)0−Ξ0  = 1531.80−1314.86 = 216.94 ± 0.38 MeV   (us pair flip)
       (已有: Σ*(1385)0−Λ0 = 268.02 ± 1.0; ρ0−π0 = 640.13 ± 0.34;
        K*0−K0 = 397.98 ± 0.24 (ds), K*+−K+ = 397.98 ± 0.26 (us))
  [P2] 容器因子 C(pair; Q) = ΔS_meson(pair) / ΔS_baryon(pair; Q):
       C(ud; s) = ρ−π / (Σ*−Λ) = 640.13/268.02 = 2.3884
       C(ud; c) = ρ−π / (Σc−Λc) = 640.13/167.29 = 3.8268
       C(ud; b) = ρ−π / (Σb−Λb) = 640.13/193.50 = 3.3082
       C(us; s) = K*−K / (Ξ*−Ξ) = 397.98/216.94 = 1.8345
  [P3] 判準 P-A: C=2 (QCD 純色因子比) 假設 → 全部 C 偏離 ≫ σ 即否證
       (Note: 2 = SU(Nc) qq̄-singlet:qq-3̄ 色因子比 = −2C_F:−C_F, 群論定理)
       P-B: C 唔係常數 (4 點差 ≫ σ) ⟹ 容器因子係 pair × spectator 函數
       P-C: 零參數結構候選批 (只准用已證標量 {M₀, nodes, K_tree=33, L₅=11,
             μ²=2, B=4}, ω = C/2 目標):
             ω1 = 1 + (m₁+m₂)/(M₀·K_tree)      [弦長相關]
             ω2 = 1 + m₁/m₂                     [pair 比]
             ω3 = 1 + (m₁·m₂)/(M₀²·B)          [pair 積/格]
             ω4 = (m₁+m₂+M₀)/(m₁+m₂)           [輕對離子修正]
             ω5 = 1 + ln(1 + (m₁+m₂)/M₀)/L₅     [對數族試探]
             PASS = 任一族 4/4 ≤ 3%
  [P4] 判決: 全排除 ⟹ 容器因子 = 已註冊現象 (pair×spectator 結構,
       非單調: C(c)=3.83 > C(b)=3.31 — 即真實 Σb−Λb > Σc−Λc puzzle,
       同 QCD 未解現象並列), 需 W-field 弦幾何新結構輸入

輸出: data/46_container_factor_table.json
"""
import json, math

M0 = 27.90091451
NB = {"u": 93.4 / 42.890, "d": 93.4 / 42.890 * 2.1505, "s": 93.4,
      "c": 3096.9 / 2, "b": 9460.30 / 2}
K_TREE = 33  # O210 C9 mode-count
L5 = 11
B = 4
MU2 = 2

# ΔS (MeV): (pair, spectator, baryon_partner) 表
# meson partition (pair) — ΔS meson
DS_MESON = {("u", "d"): 640.13, ("u", "s"): 397.98, ("d", "s"): 397.98}
DS_BARYON = {("u", "d", "s"): 268.02, ("u", "d", "c"): 167.29,
             ("u", "d", "b"): 193.50, ("u", "s", "s"): 216.94}

PAIRS = [("u", "d", "s"), ("u", "d", "c"), ("u", "d", "b"), ("u", "s", "s")]

print("═══ §1 容器因子表 (PDG 2024) ═══")
Ctab = {}
for pair in PAIRS:
    m_pair = (pair[0], pair[1])
    sp = pair[2]
    DM = DS_MESON[m_pair]
    DB = DS_BARYON[pair]
    C = DM / DB
    Ctab[f"{m_pair};{sp}"] = round(C, 4)
    print(f"  C({m_pair[0]},{m_pair[1]}; spectator {sp}) = {DM:.2f}/{DB:.2f} = {C:8.4f}")

print("\n═══ §2 P-A: C = 2 (QCD 純色因子比) 檢驗 ═══")
for k, v in Ctab.items():
    dev = (v - 2.0) / 2.0 * 100
    print(f"  {k}: C = {v:8.4f} vs 2.0 → dev {dev:+6.1f}% {'✗ 否證' if abs(dev) > 3 else '?'}")
cvals = list(Ctab.values())
spread = (max(cvals) - min(cvals)) / min(cvals) * 100
print(f"  4 點 spread = {spread:.1f}% ≫ σ (0.1-0.5%) ⟹ P-B: C 唔係常數 ✅")

print("\n═══ §3 P-C: 零參數結構候選 (ω = C/2 目標) ═══")
def msum(pair):
    return NB[pair[0]] + NB[pair[1]]
def mprod(pair):
    return NB[pair[0]] * NB[pair[1]]

def w1(pair):
    return 1 + msum(pair) / (M0 * K_TREE)
def w2(pair):
    return 1 + NB[pair[0]] / NB[pair[1]]
def w3(pair):
    return 1 + mprod(pair) / (M0 ** 2 * B)
def w4(pair):
    return (msum(pair) + M0) / msum(pair)
def w5(pair):
    return 1 + math.log(1 + msum(pair) / M0) / L5

FAMS = {"w1 1+(m₁+m₂)/(M₀·K_tree)": w1, "w2 1+m₁/m₂": w2,
        "w3 1+m₁m₂/(M₀²·B)": w3, "w4 (Σm+M₀)/Σm": w4,
        "w5 1+ln(1+Σm/M₀)/L₅": w5}
obs_w = {k: v / 2.0 for k, v in Ctab.items()}
results = {}
for name, fn in FAMS.items():
    devs = []
    for pair in PAIRS:
        mp = (pair[0], pair[1])
        k = f"{mp};{pair[2]}"
        pred = fn(mp)
        dev = abs(pred - obs_w[k]) / obs_w[k] * 100
        devs.append(round(dev, 1))
    le3 = sum(1 for d in devs if d <= 3.0)
    results[name] = {"devs_pct": devs, "le3": le3, "PASS": le3 == 4}
    print(f"  {name:>30s}: devs% {devs}  {'✅' if le3 == 4 else '✗'}")

print("\n═══ §4 判決 ═══")
w = [k for k, r in results.items() if r["PASS"]]
print(f"  P-A (C=2): {'存活' if all(abs(v-2)/2 < 0.03 for v in Ctab.values()) else '否證 (最大偏離見上)'}")
print(f"  P-B (C 常數): {'存活' if spread < 3 else '否證 — C 係 pair×spectator 函數 ✅'}")
print(f"  P-C (零參數族): {w if w else '全排除 (0/5) — 容器因子無零參數譜函數形式'}")
print(f"  ★ 現象: C(ud;c)=3.83 > C(ud;b)=3.31 非單調 ⟺ Σb−Λb > Σc−Λc 真實 puzzle (QCD 未解)")
print(f"  ⟹ 容器維度 = W-field 弦幾何 (1絃 vs 3絃 junction) 結構出生點; 已註冊現象")

OUT = {"container_table": Ctab, "spread_pct": round(spread, 2),
       "C2_test": {k: round((v - 2) / 2 * 100, 2) for k, v in Ctab.items()},
       "omega_candidates": results,
       "verdict": "P-A/P-B 否證; P-C 全排除; 容器因子 = 已註冊現象 (pair×spectator, 非單調)"}
with open("data/46_container_factor_table.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)
print("  data/46_container_factor_table.json 寫入完成")