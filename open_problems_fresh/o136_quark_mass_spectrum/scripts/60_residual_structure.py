#!/usr/bin/env python3
"""
O136 — Script 60: |Δm| 殘餘結構分析 — 缺嘅係「代數修正因子」定「世代因子」?
================================================================
背景 (docs/32):
  ★★★ |Δm| 二階自能 = 0.5872, 結構雙重顯著 (P=0.0155 模式集 / 0.0080 耦合)
  ★ 典型誤差 1.80×, 而質量總跨度 3.4e5× ⟹ 已捕捉 99.9995% 範圍
  ⟹ 剩餘係 ~1.8× 殘餘【形狀偏差】, 唔係方向問題

★ 關鍵觀察 (docs/25 最佳配對):
    t↔1, b↔2, τ↔3 | c↔4, μ↔5, s↔7 | d↔9, u↔11, e↔13
    ⟹ 【世代對應模式塊】{1,2,3} / {4,5,7} / {9,11,13}!

本 script 測兩個假設:
  H1 (代數修正): 殘餘 ∝ ln deg(n), deg = 40/2^{v₂(44−n)} (docs/28)
     9 模式中 deg ≠ 40 者只有 n=2 (deg 20) 與 n=4 (deg 5)
     ⟹ 預言: 呢兩個模式之殘餘異常
  H2 (世代因子): 殘餘有【逐世代系統偏移】
     ⟹ 預言: 三個模式塊之殘餘均值顯著不同

方法:
  (A) 最佳擬合 + 逐粒子殘餘 (含世代標籤)
  (B) 世代塊殘餘均值 + permutation test
  (C) 殘餘與結構量之相關 (deg, v₂, n mod 4, γ, n, ...) + permutation p
  (D) 裁決
"""
import numpy as np, math, json, random, itertools
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"
M9 = [1,2,3,4,5,7,9,11,13]
MASS = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
DM = {1:-4310.877431, 2:1275.174080, 3:756.841933, 4:460.723130, 5:303.463670,
      7:155.939172, 9:92.106867, 11:58.797781, 13:39.011703}
GEN = {"e":1,"u":1,"d":1,"mu":2,"c":2,"s":2,"tau":3,"t":3,"b":3}

print("=" * 96)
print("O136 Script 60: |Δm| 殘餘結構分析")
print("=" * 96)

# ═══ (A) 最佳擬合 + 殘餘 ═════════════════════════════
lnDM = np.array([math.log(abs(DM[n])) for n in M9])
sp = sorted(MASS, key=lambda p: MASS[p])
lm = np.array([math.log(MASS[p]) for p in sp])

# 重排配對 (依 ln|Δm| 排序)
o = np.argsort(lnDM)
pair = list(zip([M9[i] for i in o], sp))
print(f"\n{'─'*96}\n(A) 最佳擬合與逐粒子殘餘\n{'─'*96}")
print(f"\n  重排配對: {', '.join(f'{p}↔{n}' for n,p in pair)}")
xs = lnDM[o]; ys = lm
alpha = float(np.polyfit(xs, ys, 1)[0]); beta = float(np.polyfit(xs, ys, 1)[1])
res = ys - (alpha*xs + beta)
rms = float(np.sqrt(np.mean(res**2)))
r2 = float(1 - np.var(res)/np.var(ys))
print(f"\n  擬合: ln m = {alpha:.6f}·ln|Δm| + {beta:.6f}")
print(f"  RMS = {rms:.4f}   R² = {r2:.6f}   典型誤差 = e^{rms:.4f} = {math.exp(rms):.4f}×")
print(f"\n  {'粒子':>5} {'世代':>5} {'n':>4} {'質量(MeV)':>12} {'ln|Δm|':>11} {'殘餘':>10} {'倍數':>9}")
print("  " + "-"*62)
recs = []
for i, (n, p) in enumerate(pair):
    recs.append({"p": p, "gen": GEN[p], "n": n, "m": MASS[p], "res": float(res[i])})
    print(f"  {p:>5} {GEN[p]:>5} {n:>4} {MASS[p]:>12.4f} {xs[i]:>11.5f} {res[i]:>10.4f} {math.exp(res[i]):>9.4f}")

# ═══ (B) 世代塊分析 ══════════════════════════════════
print(f"\n{'─'*96}\n(B) 世代塊殘餘 (模式塊 {{1,2,3}} / {{4,5,7}} / {{9,11,13}})\n{'─'*96}")
print(f"\n  {'世代':>5} {'模式塊':>14} {'殘餘均值':>11} {'殘餘 std':>10} {'倍數':>9}")
print("  " + "-"*54)
gm = {}
for g in [3,2,1]:
    rs = [r["res"] for r in recs if r["gen"] == g]
    ns = [r["n"] for r in recs if r["gen"] == g]
    gm[g] = float(np.mean(rs))
    print(f"  {g:>5} {str(sorted(ns)):>14} {np.mean(rs):>11.4f} {np.std(rs, ddof=1):>10.4f} {math.exp(np.mean(rs)):>9.4f}")
spread = max(gm.values()) - min(gm.values())
print(f"\n  ★ 世代均值跨度 = {spread:.4f}  (倍數 {math.exp(spread):.4f}×)")
print(f"  ★ 殘餘 RMS = {rms:.4f} ⟹ 世代跨度佔 RMS 之 {spread/rms*100:.1f}%")

# permutation test: 隨機重排世代標籤
rng = random.Random(20260920)
resarr = np.array([r["res"] for r in recs])
obs_ss = float(np.var([gm[g] for g in [1,2,3]]))
null_ss = []
for _ in range(10000):
    lab = [1,1,1,2,2,2,3,3,3]
    rng.shuffle(lab)
    means = [np.mean(resarr[[i for i,l in enumerate(lab) if l==g]]) for g in [1,2,3]]
    null_ss.append(float(np.var(means)))
p_gen = float((np.array(null_ss) >= obs_ss).mean())
print(f"\n  ★ permutation test (N=10000): 觀測世代間方差 = {obs_ss:.5f}")
print(f"    null 中位 = {np.median(null_ss):.5f},  P(≥觀測) = {p_gen:.4f}")
print(f"    ⟹ {'🟢 世代因子顯著' if p_gen < 0.05 else ('🟡 邊緣' if p_gen < 0.2 else '🔴 唔顯著')}")

# ═══ (C) 殘餘與結構量之相關 ═══════════════════════════
print(f"\n{'─'*96}\n(C) 殘餘 vs 結構量 (N=9, permutation p)\n{'─'*96}")
def v2(k):
    c = 0
    while k % 2 == 0 and k > 0: c += 1; k //= 2
    return c
def deg(n):
    return 40 // (2 ** v2(44-n))

ns_ordered = [r["n"] for r in recs]
Q = {
    "deg(n)":        [deg(n) for n in ns_ordered],
    "v2(44-n)":      [v2(44-n) for n in ns_ordered],
    "v2(n)":         [v2(n) for n in ns_ordered],
    "n":             [n for n in ns_ordered],
    "n mod 4":       [n % 4 for n in ns_ordered],
    "gamma_n":       [4*math.sin(n*math.pi/88)**2 for n in ns_ordered],
    "ln|Dm|":        [math.log(abs(DM[n])) for n in ns_ordered],
    "gen":           [r["gen"] for r in recs],
    "sector_up":     [1 if r["p"] in "uct" else 0 for r in recs],
    "sector_down":   [1 if r["p"] in "dsb" else 0 for r in recs],
    "sector_lepton": [1 if r["p"] in ("e","mu","tau") else 0 for r in recs],
}
print(f"\n  {'結構量':>14} {'Pearson r':>11} {'perm p':>9} {'判定':>10}")
print("  " + "-"*50)
cr = {}
for k, v in Q.items():
    v = np.array(v, dtype=float)
    if v.std() < 1e-14:
        print(f"  {k:>14} {'—':>11} {'—':>9} {'常數':>10}"); cr[k] = {"r": None, "p": None}
        continue
    r = float(np.corrcoef(v, resarr)[0, 1])
    nv = []
    for _ in range(10000):
        p_ = v.copy().tolist(); rng.shuffle(p_); p_ = np.array(p_)   # ★ 修 tolist 副本 bug
        nv.append(abs(float(np.corrcoef(p_, resarr)[0, 1])))
    pv = float((np.array(nv) >= abs(r)).mean())
    cr[k] = {"r": r, "p": pv}
    flag = '🟢 顯著' if pv < 0.05 else ('🟡 邊緣' if pv < 0.2 else '🔴 唔顯著')
    print(f"  {k:>14} {r:>11.4f} {pv:>9.4f} {flag:>10}")

# ═══ (D) H1 專門測試 ═════════════════════════════════
print(f"\n{'─'*96}\n(D) H1 專門測試: deg ≠ 40 之模式 (n=2, n=4) 殘餘異常?\n{'─'*96}")
spec = [r for r in recs if deg(r["n"]) != 40]
norm = [r for r in recs if deg(r["n"]) == 40]
print(f"\n  deg ≠ 40: " + ", ".join(f"n={r['n']} (deg={deg(r['n'])}, 殘餘={r['res']:.4f})" for r in spec))
print(f"  deg = 40: 7 個模式, 殘餘均值 = {np.mean([r['res'] for r in norm]):.4f}, std = {np.std([r['res'] for r in norm], ddof=1):.4f}")
print(f"  ★ 特殊組均值 = {np.mean([r['res'] for r in spec]):.4f}")
print(f"  ★ 差距 = {abs(np.mean([r['res'] for r in spec]) - np.mean([r['res'] for r in norm])):.4f}")
print(f"  ⟹ {'🟢 支持 H1' if abs(np.mean([r['res'] for r in spec]) - np.mean([r['res'] for r in norm])) > rms else '🔴 唔支持 H1'}")

# ═══ (E) 裁決 ════════════════════════════════════════
print(f"\n{'─'*96}\n(E) 裁決\n{'─'*96}")
print(f"""
  ① |Δm| 擬合: RMS = {rms:.4f}, R² = {r2:.6f}
  ② 世代塊均值: {', '.join(f'G{g}={gm[g]:.4f}' for g in [3,2,1])}
     跨度 {spread:.4f} (倍數 {math.exp(spread):.4f}×); permutation P = {p_gen:.4f}
  ③ 最強殘餘相關: {max([(k,v) for k,v in cr.items() if v['r'] is not None], key=lambda kv: abs(kv[1]['r']))[0]}
  ④ H1 (deg 修正): {'🟢 支持' if abs(np.mean([r['res'] for r in spec]) - np.mean([r['res'] for r in norm])) > rms else '🔴 唔支持'}
  ⑤ 殘餘 RMS {rms:.4f} vs 世代跨度 {spread:.4f} ⟹ 世代解釋 {spread/rms*100:.1f}%
""")

with open(OUT/"60_residual_structure.json", "w") as f:
    json.dump({
        "fit": {"alpha": alpha, "beta": beta, "rms": rms, "r2": r2, "typical_error": math.exp(rms)},
        "pairing": [[n, p] for n, p in pair],
        "records": recs,
        "generation_means": {str(g): gm[g] for g in [1,2,3]},
        "generation_spread": spread,
        "generation_perm_p": p_gen,
        "residual_correlations": cr,
        "H1_deg_test": {
            "special_modes": [[r["n"], deg(r["n"]), r["res"]] for r in spec],
            "special_mean": float(np.mean([r["res"] for r in spec])),
            "normal_mean": float(np.mean([r["res"] for r in norm])),
            "supported": bool(abs(np.mean([r['res'] for r in spec]) - np.mean([r['res'] for r in norm])) > rms),
        },
        "closure_threshold": 0.05,
    }, f, ensure_ascii=False, indent=2)
print(f"✅ 寫入 data/60_residual_structure.json")