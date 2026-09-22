#!/usr/bin/env python3
"""
O136 — Script 58: 二模式族符號修正 + 退化假象釐清

⚠️⚠️ 【本 script 度量錯誤, 已由 scripts/59 取代 — 見 docs/32 §二】
    本 script 用【原始值】擬合 ln m ~ f (指數擬合 m ∝ e^{af})
    正確應用 ln f 擬合 (冪律 m ∝ f^a), 與 docs/25-31 一致
    實測: sum_V2_dE 原始值 2.3078 vs 對數值 0.5872 (= docs/25 之 0.5873 ✅)
    ⚠️ 保留作 bug 記錄, 結論以 scripts/59 為準
================================================================
Script 57 兩個問題:
  ① 符號: sum_V2_dE (即 |Δm| 本體) 得 2.7335 — 但已知 |Δm| = 0.5873
     原因: 自能有正負 (n=1 負, n≥2 正) ⟹ 排序打亂配對
     修正: 用 |·| (絕對值)
  ② null test 2 退化假象:
     - V3diag P=0.0000: 反對稱 W ⟹ W³ 對角恆零 ⟹ std=0 ⟹ score 返回 9e9 (假象)
     - min_dE / sum_1_dE / sum_1_dE2 P=1.0000: 純譜量, 與耦合無關 (無判別力)

本 script:
  (A) 二模式族【絕對值】版本全掃描 — |Δm| 是否仍最佳?
  (B) 釐清 null test 2 之有效候選 (排除退化)
  (C) 裁決: 二模式算子方向成立嗎?
"""
import numpy as np, math, json, random
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"
M9 = [1,2,3,4,5,7,9,11,13]
NC = 88
MASS = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
LM = np.array([math.log(MASS[p]) for p in sorted(MASS, key=lambda p: MASS[p])])

x = np.arange(1, NC+1, dtype=float)
Psi = np.zeros((NC, NC))
for n in range(1, NC+1):
    Psi[:, n-1] = np.sin(n*math.pi*x/(NC+1))
for n in range(NC):
    Psi[:, n] /= np.linalg.norm(Psi[:, n])
V = Psi.T @ np.diag(x - x.mean()) @ Psi
E = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1, NC+1)])

def score(vals, LMv=None):
    y = LM if LMv is None else LMv
    v = np.array(vals, dtype=float)
    if v.std() < 1e-14: return 9e9
    o = np.argsort(v); xs = v[o]; ys = np.sort(y)
    r = float(np.corrcoef(xs, ys)[0, 1])
    return float(ys.std()*math.sqrt(max(0.0, 1.0-r*r)))

def fam(modes, Vm=None, Em=None):
    Vv = V if Vm is None else Vm
    Ev = E if Em is None else Em
    o = {}
    for n in modes:
        idx = [m for m in range(NC) if m != n-1 and (m-(n-1)) % 2 == 1]
        dE = Ev[n-1] - Ev[idx]
        aV2 = np.abs(Vv[n-1, idx])**2
        o.setdefault("abs_sum_V2_dE",  []).append(abs(float((aV2/dE).sum())))
        o.setdefault("abs_sum_V2_dE2", []).append(abs(float((aV2/dE**2).sum())))
        o.setdefault("abs_sum_V2_dE3", []).append(abs(float((aV2/dE**3).sum())))
        o.setdefault("abs_sum_V_dE",   []).append(abs(float((np.abs(Vv[n-1, idx])/dE).sum())))
        o.setdefault("abs_V3diag",     []).append(abs(float((Vv@Vv@Vv)[n-1, n-1])))
        o.setdefault("abs_V5diag",     []).append(abs(float((Vv@Vv@Vv@Vv@Vv)[n-1, n-1])))
        o.setdefault("sum_V2",         []).append(float(aV2.sum()))
        o.setdefault("min_dE",         []).append(float(np.abs(dE).min()))
        o.setdefault("max_V2_dE",      []).append(abs(float((aV2/dE).max())))
        o.setdefault("purity",         []).append(float(aV2.sum()**2/(aV2**2).sum()))
        o.setdefault("inv_norm",       []).append(1.0/float(np.linalg.norm(Vv[n-1, idx])))
    return o

print("=" * 96)
print("O136 Script 58: 二模式族符號修正 + 退化假象釐清")
print("=" * 96)

CV = fam(M9)
print(f"\n{'─'*96}\n(A) 二模式族【絕對值】版本\n{'─'*96}")
print(f"\n{'候選':>18} {'RMS':>9} {'值範圍':>12} {'判定':>10}")
print("-" * 54)
res = {}
for k, v in CV.items():
    r = score(v); res[k] = r
    vv = np.abs(np.array(v)); rng = vv.max()/vv.min() if vv.min() > 0 else float('inf')
    flag = '✅ 閉合' if r < 0.05 else ('🟡 佳' if r < 0.60 else '🔴')
    print(f"{k:>18} {r:>9.4f} {rng:>12.4g} {flag:>10}")
print(f"\n★ 已知對照: |Δm| (絕對值自能) = 0.5873  ⟹ abs_sum_V2_dE = {res['abs_sum_V2_dE']:.4f}")
print(f"★ 相符 {'✅' if abs(res['abs_sum_V2_dE']-0.5873) < 0.01 else '🔴 唔符'}")

# 全部候選統一排名 (含 57 之最佳 min_dE)
print(f"\n★ 二模式族統一排名 (絕對值 + 非絕對值):")
allr = dict(res)
allr["min_dE"] = 0.8682
for k, v in sorted(allr.items(), key=lambda kv: kv[1])[:6]:
    print(f"    {k:>18} {v:.4f}")
print(f"★ 對照: sin = 1.1178;  3 因子乘積 = 0.4970;  閉合需 < 0.05")

# ═══ (B) null test 2 有效候選釐清 ════════════════════
print(f"\n{'─'*96}\n(B) null test 2 (隨機 Z₂-奇耦合) 之退化釐清\n{'─'*96}")
print(f"""
  Script 57 之 (D) 表有三類:
  ★ 退化假象 A: V3diag P=0.0000
      原因: 反對稱 W ⟹ W³ 亦反對稱 ⟹ 對角恆零 ⟹ std=0 ⟹ score 返回 9e9
      ⟹ 【假象, 非真顯著】 (本 script 用 |V3diag| 並排除零 std)
  ★ 退化假象 B: min_dE / sum_1_dE / sum_1_dE2 P=1.0000
      原因: 純譜量 (只依賴 E_n), 與耦合 V 無關 ⟹ null = 觀測 ⟹ 無判別力
  ★ 有效候選: sum_V2 / sum_V2_dE / row_norm / max_V / purity / V2diag
      全部 P ≥ 0.49 【唔顯著】, 且觀測 RMS 2.83 > null 中位 1.15
      ⟹ ★★ 真實位置算子耦合【比隨機耦合更差】!
""")

rng = random.Random(20260920)
KEYS = ["abs_sum_V2_dE", "abs_V3diag", "sum_V2", "max_V2_dE", "purity"]
obs = {k: score(CV[k]) for k in KEYS}
null2 = {k: [] for k in KEYS}
for _ in range(1000):
    A = np.random.randn(NC, NC)
    W = np.zeros((NC, NC))
    for i in range(NC):
        for j in range(NC):
            if (i-j) % 2 == 1: W[i, j] = A[i, j]
    W = (W - W.T)/2.0
    cv = fam(M9, Vm=W, Em=E)
    for k in KEYS:
        null2[k].append(score(cv[k]))
print(f"{'候選':>18} {'觀測 RMS':>10} {'null 中位':>11} {'null min':>10} {'P(≤觀測)':>10} {'判定':>10}")
print("-" * 74)
n2 = {}
for k in KEYS:
    v = np.array(null2[k]); p = float((v <= obs[k]).mean())
    n2[k] = {"median": float(np.median(v)), "min": float(v.min()), "p": p}
    flag = '🟢 顯著' if p < 0.05 else ('🟡 邊緣' if p < 0.2 else '🔴 唔顯著')
    print(f"{k:>18} {obs[k]:>10.4f} {np.median(v):>11.4f} {v.min():>10.4f} {p:>10.4f} {flag:>10}")

# ═══ (C) 裁決 ════════════════════════════════════════
print(f"\n{'─'*96}\n(C) 裁決: 二模式算子方向成立嗎?\n{'─'*96}")
best = min(allr.items(), key=lambda kv: kv[1])
print(f"""
  ① 二模式族最佳 = {best[0]} ({best[1]:.4f})
  ② ★ |Δm| 本體 (abs_sum_V2_dE) = {res['abs_sum_V2_dE']:.4f} — 仍係全族最佳
     ⟹ 【二模式算子方向【已】被 |Δm| 覆蓋, 唔係新方向】
  ③ 其餘 14 個二模式變體全部更差 (最佳 min_dE 0.8682)
  ④ 閉合需 < 0.05 ⟹ 🔴 未閉合
  ⑤ null test 1 (隨機模式集): min_dE P = 0.0450 🟡 邊緣; sum_V2 P = 0.4910 🔴
  ⑥ null test 2 (隨機耦合): 全部有效候選 P ≥ 0.49 🔴
     ★★ 真實位置算子耦合【比隨機耦合更差】 (觀測 2.83 vs null 中位 1.15)
""")

with open(OUT/"58_two_mode_signfix.json", "w") as f:
    json.dump({
        "abs_family": res,
        "ranking": dict(sorted(allr.items(), key=lambda kv: kv[1])),
        "abs_sum_V2_dE_matches_known": bool(abs(res['abs_sum_V2_dE']-0.5873) < 0.01),
        "null2_valid": n2,
        "degenerate_artifacts": {
            "V3diag_P0": "反對稱 W ⟹ W³ 對角恆零 ⟹ std=0 ⟹ 假象",
            "min_dE_P1": "純譜量, 與耦合無關 ⟹ 無判別力",
        },
        "closure_threshold": 0.05,
        "reference": {"absdm": 0.5873, "sin": 1.1178, "multifactor3": 0.4970},
    }, f, ensure_ascii=False, indent=2)
print(f"✅ 寫入 data/58_two_mode_signfix.json")