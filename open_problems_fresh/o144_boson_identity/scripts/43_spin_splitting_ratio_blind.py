#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O144-43 — 自旋分裂比例盲測: 5 固定配方 × 6 獨立比例 (零參數)
==================================================================
承接: scripts/42 發現自旋分裂隨重味含量單調減, 但 H1 (單常數 10.5 M₀) 否證。
本輪攻「自旋分裂嘅形式」: 用**等味自旋對比例**做預註冊盲測。

★ 關鍵結構優勢: ΔS = M(J+) − M(J−) 用同 nodes 對 (Σ*/Λ, Ξ*/Ξ0, ρ/π, K*/K0,
D*/D0, B*/B0, J/ψ/ηc, ϒ/ηb) ⟹ 基線 E_link 喺差度**消走** (只要 E_link 係 J 無關)
⟹ ΔS 純自旋, 比例 r = ΔS₁/ΔS₂ 唔依賴任何 scale。

★ 預註冊 (跑前凍結, 唔准 tune):
  [P1] 資料庫: 8 個純自旋对 + Δ−p (味修正標注, 唔入主測) (PDG 2024)
  [P2] ΔS 值 (M₀ 單位): Σ*/Λ 9.606, Ξ*/Ξ0 7.890, ρ/π 22.943, K*/K0 14.263,
       D*/D0 5.090 (D*0=2006.85), B*/B0 1.633, J/ψ−ηc 4.050, ϒ−ηb 2.233
  [P3] 6 個獨立比例 (預註冊固定):
       r1 = Σ*/Λ ÷ Ξ*/Ξ0   r2 = ρ/π ÷ K*/K0   r3 = K*/K0 ÷ D*/D0
       r4 = D*/D0 ÷ B*/B0  r5 = J/ψ−ηc ÷ ϒ−ηb  r6 = ρ/π ÷ J/ψ−ηc
  [P4] 5 個固定配方 f(pair) (同一規則庫作用於所有對, 唔係逐對揀):
       P1: f = 1/(γ_{m1}·γ_{m2})          (γ = 4sin²(πn/88) 鏈譜)
       P2: f = 1/(E′_{m1}·E′_{m2})        (E′ = SU(12) 每纖維能量, data/35)
       P3: f = 1/√(E′_{m1}·E′_{m2})
       P4: f = 1/√(m_{m1}·m_{m2})        (m = NB 節點質量)
       P5: f = 1/γ_{|m1−m2|}              (mode 距離譜反比)
  [P5] 判準 (任一配方要過齊: r_pred 全部 6 個 |dev| ≤ 3% ∧ 無單一 >5%)
  [P6] 判決: 有配方過 ⟹ 自旋形式閉合 (樣本外升級); 無 ⟹ 誠實負 —
       5 個自然譜函數配方正式排除 (與 T0-T6 一齊入冊), ΔS 表留底做現象層

輸出: data/43_spin_splitting_ratio_blind.json
"""
import json, math

M0 = 27.90091451
NA = {"u": 93.4 / 42.890, "d": 93.4 / 42.890 * 2.1505, "s": 93.4,
      "c": 93.4 * 11.652, "b": 93.4 * 11.652 * 4.586}
NB = dict(NA)
NB["c"] = 3096.9 / 2
NB["b"] = 9460.30 / 2
MODE = {"u": 11, "d": 9, "s": 7, "c": 4, "b": 2}

def gam(n):
    return 4 * math.sin(n * math.pi / 88) ** 2

# E'(q_m) — SU(12) 移位每纖維 (data/35 gold)
EF = {11: 165.586979074824, 9: 195.235149040176, 7: 134.717027433432,
      4: 114.865277982844, 2: 202.400151085512}

# 純自旋對: (name, ΔM MeV, quarks) — ΔM = M(J+) − M(J−), 同 nodes
PAIRS = [
    ("Sigma*-Lambda", 268.02,  ["u", "d"]),
    ("Xi*-Xi0",       220.14,  ["u", "s"]),
    ("rho-pi",        640.13,  ["u", "d"]),
    ("K*-K0",         397.94,  ["d", "s"]),
    ("D*-D0",         142.01,  ["c", "d"]),
    ("B*-B0",          45.57,  ["b", "d"]),
    ("Jpsi-etac",     113.00,  ["c", "c"]),
    ("Upsilon-etab",   62.30,  ["b", "b"]),
]
# 6 個預註冊比例 (pair 索引)
RATIOS = [("r1 Sigma*/Lambda ÷ Xi*/Xi0", 0, 1), ("r2 rho/pi ÷ K*/K0", 2, 3),
          ("r3 K*/K0 ÷ D*/D0", 3, 4), ("r4 D*/D0 ÷ B*/B0", 4, 5),
          ("r5 J/psi-etac ÷ Upsilon-etab", 6, 7), ("r6 rho/pi ÷ J/psi-etac", 2, 6)]

def f_P1(ms):
    return 1.0 / (gam(MODE[ms[0]]) * gam(MODE[ms[1]]))
def f_P2(ms):
    return 1.0 / (EF[MODE[ms[0]]] * EF[MODE[ms[1]]])
def f_P3(ms):
    return 1.0 / math.sqrt(EF[MODE[ms[0]]] * EF[MODE[ms[1]]])
def f_P4(ms):
    return 1.0 / math.sqrt(NB[ms[0]] * NB[ms[1]])
def f_P5(ms):
    dm = abs(MODE[ms[0]] - MODE[ms[1]])
    if dm == 0:
        return float("nan")  # 同味對結構上未定義 (γ₀=0) — 記錄為 N/A, 唔係 fit
    return 1.0 / gam(dm)

FAMS = {"P1": f_P1, "P2": f_P2, "P3": f_P3, "P4": f_P4, "P5": f_P5}

print("═══ §1 純自旋對 ΔS (M₀ 單位) ═══")
dS = [(name, dM / M0, ms) for name, dM, ms in PAIRS]
for name, v, ms in dS:
    print(f"  {name:>14s} ΔS = {v:7.4f} M₀ ({v*M0:7.2f} MeV)  modes {ms}")

print("\n═══ §2 6 個觀測比例 vs 5 配方預言 ═══")
obs = {}
for label, i, j in RATIOS:
    obs[label] = dS[i][1] / dS[j][1]
    print(f"  {label}: obs = {obs[label]:8.5f}")

print("\n═══ §3 配方盲測 ═══")
results = {}
for fam, fn in FAMS.items():
    devs = []
    for label, i, j in RATIOS:
        pred = fn(dS[i][2]) / fn(dS[j][2])
        dev = abs(pred - obs[label]) / obs[label]
        devs.append(dev)
        print(f"  {fam} {label:>38s}: pred {pred:8.5f}  dev {dev*100:6.2f}%")
    le3 = sum(1 for d in devs if d <= 0.03)
    mx = max(devs)
    ok = (le3 == 6) and (mx <= 0.05)
    results[fam] = {"le3": le3, "max": round(mx, 5), "PASS": ok}
    print(f"    {fam}: ≤3% {le3}/6, max {mx*100:.2f}%  {'✅' if ok else '✗ 排除'}")

print("\n═══ §4 判決 ═══")
winners = [f for f, r in results.items() if r["PASS"]]
print(f"  通過配方: {winners if winners else '無 — 誠實負: 5 個自然譜配方正式排除'}")
print(f"  ΔS 資料庫: 8 對 (現象層留底, 含 PDG 2024 誤差 ±0.2-3 MeV)")

OUT = {"M0": M0, "pairs": [{"name": n, "dS_M0": round(v, 5), "dS_MeV": round(v * M0, 3),
                            "quarks": ms} for n, v, ms in dS],
       "obs_ratios": {l: round(o, 6) for l, o in obs.items()},
       "family_results": results, "winners": winners,
       "verdict": "closed" if winners else "honest-negative"}
with open("data/43_spin_splitting_ratio_blind.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)
print("  data/43_spin_splitting_ratio_blind.json 寫入完成")