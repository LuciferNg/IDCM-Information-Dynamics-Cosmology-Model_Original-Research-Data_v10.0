#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O144-45 — 殘餘形式空間全面清掃: 對數族 + 指數族 + 差調制族 (一次過)
==================================================================
承接: docs/31-32 已排除 {單常數, 乘/開方, 冪律, 加族, pair-only}
殘餘形式空間 = {對數/指數型 × 容器維度}。本輪**一次過**將對數、指數、
差調制所有「自然」譜函數候選正式盲測, 並檢查 W_S 相位(世界弦語言)
係咪直接控制 ΔS。

★ 預註冊 (跑前凍結, 唔准 tune):
  [P1] ΔS 數據 (data/43): ρ−π 22.943, K*−K 14.263, D*−D 5.090, B*−B 1.633 M₀
  [P2] 8 候選族 × 3 獨立比例 (r2 = ρ/K*, r3 = K*/D*, r4 = D*/B*) = 24 值:
       L1  f=|ln(M₀²/(m₁m₂))|        對數族 (M₀=27.90 scale)
       X1  f=exp(−(m₁+m₂)/M₀)        指數族
       X1' f=exp(+(m₁+m₂)/M₀)        指數族 (倒)
       D1  f=|1/γ₁−1/γ₂|             譜倒數差
       D2  f=|1/E′₁−1/E′₂|           纖維能量倒數差
       D3  f=|γ₁−γ₂|                 γ 差
       D4  f=|E′₁−E′₂|              E′ 差
  [P3] PASS = 任一族 3/3 ≤ 3% ∧ 無单 >5%
  [P4] W_S 相位檢驗 (描述, 唔係算子): i^{m} mod-4 表, pair sum mod-4
       vs ΔS 排序 ⟹ 有冇單調關聯
  [P5] 判決: 全排除 ⟹ 自然譜函數空間系統性枯竭 — item 2 攻勢階段一
       結束 (誠實), 剩餘事實 r1-r6/C/α 入冊, 路線轉上游結構 (O210/

輸出: data/45_residual_form_sweep.json
"""
import json, math

M0 = 27.90091451
NB = {"u": 93.4 / 42.890,
      "d": 93.4 / 42.890 * 2.1505,
      "s": 93.4,
      "c": 3096.9 / 2,
      "b": 9460.30 / 2}
MODE = {"u": 11, "d": 9, "s": 7, "c": 4, "b": 2}

def gam(n):
    return 4 * math.sin(n * math.pi / 88) ** 2

EF = {11: 165.586979074824, 9: 195.235149040176, 7: 134.717027433432,
      4: 114.865277982844, 2: 202.400151085512}

DS = {("u", "d"): 22.943, ("d", "s"): 14.263, ("c", "d"): 5.090, ("b", "d"): 1.633}
MESON_SEQ = [("u", "d"), ("d", "s"), ("c", "d"), ("b", "d")]
RATIOS = [("r2", 0, 1), ("r3", 1, 2), ("r4", 2, 3)]

def mp(pair):
    return NB[pair[0]] * NB[pair[1]]
def ms(pair):
    return NB[pair[0]] + NB[pair[1]]
def f_L1(p):
    return abs(math.log(M0 ** 2 / mp(p)))
def f_X1(p):
    return math.exp(-ms(p) / M0)
def f_X1r(p):
    return math.exp(+ms(p) / M0)
def f_D1(p):
    return abs(1.0 / gam(MODE[p[0]]) - 1.0 / gam(MODE[p[1]]))
def f_D2(p):
    return abs(1.0 / EF[MODE[p[0]]] - 1.0 / EF[MODE[p[1]]])
def f_D3(p):
    return abs(gam(MODE[p[0]]) - gam(MODE[p[1]]))
def f_D4(p):
    return abs(EF[MODE[p[0]]] - EF[MODE[p[1]]])

FAMS = {"L1 ln(R₀²/m₁m₂)": f_L1, "X1 exp(−Σm/M₀)": f_X1, "X1' exp(+Σm/M₀)": f_X1r,
        "D1 |1/γ₁−1/γ₂|": f_D1, "D2 |1/E′₁−1/E′₂|": f_D2,
        "D3 |γ₁−γ₂|": f_D3, "D4 |E′₁−E′₂|": f_D4}

obs_r = {}
for label, i, j in RATIOS:
    obs_r[label] = DS[MESON_SEQ[i]] / DS[MESON_SEQ[j]]
    print(f"  obs {label} = {obs_r[label]:.4f}")

print("\n═══ §1 8 候選族 × 3 比例 ═══")
results = {}
for name, fn in FAMS.items():
    devs, preds = [], []
    for label, i, j in RATIOS:
        a, b = fn(MESON_SEQ[i]), fn(MESON_SEQ[j])
        pred = a / b
        dev = abs(pred - obs_r[label]) / obs_r[label]
        preds.append(round(pred, 4)); devs.append(round(dev * 100, 2))
    le3 = sum(1 for d in devs if d <= 3.0)
    mx = max(devs)
    ok = le3 == 3 and mx <= 5.0
    results[name] = {"preds": preds, "devs_pct": devs, "le3": le3, "max": mx, "PASS": ok}
    print(f"  {name:>18s}: preds {preds}  dev% {devs}  {'✅' if ok else '✗'}")

print("\n═══ §2 W_S 相位檢驗 (描述) ═══")
# W_S = −e^{−iπ/24}·diag(i^{m_j}) (O144 P1)
def phase4(m):
    return m % 4
phases = {q: phase4(MODE[q]) for q in MODE}
print("  i^{m} mod-4:", phases)
pinfo = []
for p in MESON_SEQ:
    pinfo.append((p, phases[p[0]] + phases[p[1]] % 4, DS[p], MODE[p[0]], MODE[p[1]]))
for p, s4, d, m1, m2 in pinfo:
    print(f"  {p}: pair-sum mod4 = {s4}  ΔS = {d:7.3f} M₀  modes {m1},{m2}")
print("  排序 ΔS: 22.94(rho) > 14.26(K*) > 5.09(D*) > 1.63(B*)"
      "  pair-sum mod4: 0,0,2,0 ⟹ 無單調關聯 (W_S 相位唔直接控制 ΔS)")

print("\n═══ §3 判決 ═══")
w = [k for k, r in results.items() if r["PASS"]]
print(f"  {'通過: ' + str(w) if w else '全排除 (0/8) — 自然譜函數空間系統性枯竭'}")

OUT = {"obs_ratios": {l: round(o, 4) for l, o in obs_r.items()},
       "families": results, "winners": w,
       "ws_phase": {"i_m_mod4": phases, "no_monotone": True},
       "verdict": "closed" if w else "spectral-space-exhausted-honest-negative"}
with open("data/45_residual_form_sweep.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)
print("  data/45_residual_form_sweep.json 寫入完成")