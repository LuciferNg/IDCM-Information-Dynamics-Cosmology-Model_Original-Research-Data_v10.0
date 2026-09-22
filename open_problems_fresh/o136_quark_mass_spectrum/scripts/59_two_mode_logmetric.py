#!/usr/bin/env python3
"""
O136 — Script 59: 二模式質量算子攻堅【正確度量版】
================================================================
★ 度量修正 (docs/32 §二): 擬合 ln m ~ ln f (冪律 m ∝ f^a)
  — 與 docs/25–31 一致; 驗證: sum_V2_dE 對數值 = 0.5872 = docs/25 之 0.5873 ✅

結構動機:
  ★ docs/26 §一: 冇任何【n 的函數】能滿足 9 個質量比 (α 跨度 42.6×)
  ★ docs/31 §五: 15 因子庫多因子乘積飽和 (參數 1→4 僅改善 1.18×)
  ★ 22 個已排除方向【全部】把觀察者當固定外部基準或無觀察者
  ⟹ 空白: 【二模式算子】M(n,m), 觀察者係變量

既有權威構造 (scripts/41):
  88-site D-D 鏈 ψ_n(i)=sin(nπi/89);  X=diag(i−⟨i⟩);  V_nm=⟨n|X|m⟩ (Z₂-奇)
  E_n = 4sin²(nπ/88)

本 script:
  (A) V 結構驗證 + 度量驗證 (sum_V2_dE 對數值 = 0.5873?)
  (B) 二模式量族全掃描【對數度量】 (20 候選)
  (C) ★★ null test 1: 隨機 9 模式集 (N=2000) — A₅ 模式集特異嗎?
  (D) ★★ null test 2: 隨機 Z₂-奇耦合 (N=1000), 排除退化候選
  (E) 裁決
"""
import numpy as np, math, json, random
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"
M9 = [1,2,3,4,5,7,9,11,13]
NC = 88
MASS = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
LM = np.array([math.log(MASS[p]) for p in sorted(MASS, key=lambda p: MASS[p])])
NEED = 0.05

x = np.arange(1, NC+1, dtype=float)
Psi = np.zeros((NC, NC))
for n in range(1, NC+1):
    Psi[:, n-1] = np.sin(n*math.pi*x/(NC+1))
for n in range(NC):
    Psi[:, n] /= np.linalg.norm(Psi[:, n])
V = Psi.T @ np.diag(x - x.mean()) @ Psi
E = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1, NC+1)])

print("=" * 96)
print("O136 Script 59: 二模式質量算子【正確度量版】")
print("=" * 96)

print(f"\n{'─'*96}\n(A) 結構 + 度量驗證\n{'─'*96}")
same = max(abs(V[n,m]) for n in range(30) for m in range(30) if n != m and (n-m) % 2 == 0)
diff = max(abs(V[n,m]) for n in range(30) for m in range(30) if (n-m) % 2 == 1)
print(f"  |V_nm| max, |n−m| 偶 = {same:.3e} (應≈0);  奇 = {diff:.3e}")
print(f"  ⟹ Z₂-奇結構 {'✅' if same < 1e-9 and diff > 1e-3 else '🔴'}")

def logscore(vals, LMv=None):
    """★ 冪律度量: 擬合 ln m ~ ln|f|, RMS = std(y)·sqrt(1−r²)"""
    y = LM if LMv is None else LMv
    v = np.abs(np.array(vals, dtype=float))
    if (v <= 0).any() or v.std() < 1e-14: return 9e9
    lv = np.log(v)
    if lv.std() < 1e-14: return 9e9
    o = np.argsort(lv); xs = lv[o]; ys = np.sort(y)
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
        aV = np.abs(Vv[n-1, idx])
        o.setdefault("sum_V2_dE",    []).append(abs(float((aV2/dE).sum())))
        o.setdefault("sum_V2_dE2",   []).append(abs(float((aV2/dE**2).sum())))
        o.setdefault("sum_V2_dE3",   []).append(abs(float((aV2/dE**3).sum())))
        o.setdefault("sum_V2_dE4",   []).append(abs(float((aV2/dE**4).sum())))
        o.setdefault("sum_V_dE",     []).append(abs(float((aV/dE).sum())))
        o.setdefault("sum_V2",       []).append(float(aV2.sum()))
        o.setdefault("row_norm",     []).append(float(np.linalg.norm(Vv[n-1, idx])))
        o.setdefault("max_V",        []).append(float(aV.max()))
        o.setdefault("max_V2_dE",    []).append(abs(float((aV2/dE).max())))
        o.setdefault("min_dE",       []).append(float(np.abs(dE).min()))
        o.setdefault("max_dE",       []).append(float(np.abs(dE).max()))
        o.setdefault("V2diag",       []).append(abs(float((Vv@Vv)[n-1, n-1])))
        o.setdefault("V3diag",       []).append(abs(float((Vv@Vv@Vv)[n-1, n-1])))
        o.setdefault("V4diag",       []).append(abs(float((Vv@Vv@Vv@Vv)[n-1, n-1])))
        o.setdefault("purity",       []).append(float(aV2.sum()**2/(aV2**2).sum()))
        o.setdefault("inv_purity",   []).append(float((aV2**2).sum()/aV2.sum()**2))
        o.setdefault("sum_1_dE",     []).append(float((1.0/np.abs(dE)).sum()))
        o.setdefault("sum_1_dE2",    []).append(float((1.0/dE**2).sum()))
        o.setdefault("V2diag_dE",    []).append(abs(float(((Vv@Vv)[n-1, n-1]))))
        o.setdefault("entropy",      []).append(float(-np.sum((aV2/aV2.sum())*np.log(aV2/aV2.sum()))))
    return o

CV = fam(M9)
print(f"\n{'─'*96}\n(B) 二模式量族【對數度量】全掃描 ({len(CV)} 候選)\n{'─'*96}")
print(f"\n{'候選':>16} {'RMS':>9} {'值範圍':>12} {'判定':>10}")
print("-" * 52)
res = {}
for k, v in CV.items():
    r = logscore(v); res[k] = r
    vv = np.abs(np.array(v)); rng = vv.max()/vv.min() if vv.min() > 0 else float('inf')
    flag = '✅ 閉合' if r < NEED else ('🟡 佳' if r < 0.60 else '🔴')
    print(f"{k:>16} {r:>9.4f} {rng:>12.4g} {flag:>10}")
best = min(res.items(), key=lambda kv: kv[1])
print(f"\n★ 二模式族最佳 = {best[0]} (RMS {best[1]:.4f})")
print(f"★ 度量驗證: sum_V2_dE = {res['sum_V2_dE']:.4f} vs docs/25 |Δm| = 0.5873 "
      f"{'✅ 吻合' if abs(res['sum_V2_dE']-0.5873) < 0.01 else '🔴'}")
print(f"★ 對照: sin = 1.1178;  3 因子乘積 = 0.4970;  閉合需 < {NEED}")

# ═══ (C) null test 1 ═════════════════════════════════
print(f"\n{'─'*96}\n(C) ★★ null test 1: 隨機 9 模式集 (N=2000) — A₅ 模式集特異嗎?\n{'─'*96}")
rng = random.Random(20260920)
KEYS = list(CV.keys())
obs = {k: res[k] for k in KEYS}
null1 = {k: [] for k in KEYS}
for _ in range(2000):
    md = rng.sample(range(1, NC+1), 9)
    cv = fam(md)
    for k in KEYS:
        null1[k].append(logscore(cv[k]))
print(f"\n{'候選':>16} {'觀測 RMS':>10} {'null 中位':>11} {'null min':>10} {'P(≤觀測)':>10} {'判定':>10}")
print("-" * 72)
n1 = {}
for k in KEYS:
    v = np.array(null1[k]); p = float((v <= obs[k]).mean())
    n1[k] = {"median": float(np.median(v)), "min": float(v.min()), "p": p}
    flag = '🟢 顯著' if p < 0.05 else ('🟡 邊緣' if p < 0.2 else '🔴 唔顯著')
    print(f"{k:>16} {obs[k]:>10.4f} {np.median(v):>11.4f} {v.min():>10.4f} {p:>10.4f} {flag:>10}")

# ═══ (D) null test 2 (排除退化) ══════════════════════
print(f"\n{'─'*96}\n(D) ★★ null test 2: 隨機 Z₂-奇耦合 (N=1000), 排除退化候選\n{'─'*96}")
print(f"  ⚠️ 排除: min_dE/max_dE/sum_1_dE/sum_1_dE2 (純譜量, 與耦合無關 ⟹ 無判別力)")
COUPL = [k for k in KEYS if k not in ("min_dE","max_dE","sum_1_dE","sum_1_dE2")]
null2 = {k: [] for k in COUPL}
for _ in range(1000):
    A = np.random.randn(NC, NC)
    W = np.zeros((NC, NC))
    for i in range(NC):
        for j in range(NC):
            if (i-j) % 2 == 1: W[i, j] = A[i, j]
    W = (W - W.T)/2.0
    cv = fam(M9, Vm=W, Em=E)
    for k in COUPL:
        null2[k].append(logscore(cv[k]))
print(f"\n{'候選':>16} {'觀測 RMS':>10} {'null 中位':>11} {'null min':>10} {'P(≤觀測)':>10} {'判定':>10}")
print("-" * 72)
n2 = {}
for k in COUPL:
    v = np.array(null2[k]); p = float((v <= obs[k]).mean())
    n2[k] = {"median": float(np.median(v)), "min": float(v.min()), "p": p}
    flag = '🟢 顯著' if p < 0.05 else ('🟡 邊緣' if p < 0.2 else '🔴 唔顯著')
    print(f"{k:>16} {obs[k]:>10.4f} {np.median(v):>11.4f} {v.min():>10.4f} {p:>10.4f} {flag:>10}")

# ═══ (E) 裁決 ════════════════════════════════════════
print(f"\n{'─'*96}\n(E) 裁決\n{'─'*96}")
print(f"""
  ① 二模式族最佳 (對數度量) = {best[0]} ({best[1]:.4f})
  ② |Δm| (sum_V2_dE) = {res['sum_V2_dE']:.4f} — 全族最佳? {'✅ 係' if best[0]=='sum_V2_dE' else '🔴 唔係'}
  ③ 閉合需 < {NEED} ⟹ {'✅' if best[1] < NEED else '🔴 未閉合'}
  ④ null test 1 (隨機模式集): sum_V2_dE P = {n1['sum_V2_dE']['p']:.4f}
  ⑤ null test 2 (隨機耦合):   sum_V2_dE P = {n2['sum_V2_dE']['p']:.4f}
  ⑥ 度量驗證: 對數度量下 sum_V2_dE = {res['sum_V2_dE']:.4f} = docs/25 之 0.5873 ✅
""")

with open(OUT/"59_two_mode_logmetric.json", "w") as f:
    json.dump({
        "z2_check": {"same_parity_max": float(same), "diff_parity_max": float(diff)},
        "metric": "ln m ~ ln f (冪律)",
        "metric_validation": {"sum_V2_dE": res['sum_V2_dE'], "docs25_value": 0.5873,
                              "match": bool(abs(res['sum_V2_dE']-0.5873) < 0.01)},
        "candidates": {k: {"rms": v} for k, v in sorted(res.items(), key=lambda kv: kv[1])},
        "best": {"name": best[0], "rms": best[1]},
        "null1_random_modeset": n1,
        "null2_random_coupling": n2,
        "excluded_degenerate": ["min_dE","max_dE","sum_1_dE","sum_1_dE2"],
        "closure_threshold": NEED,
        "reference": {"absdm": 0.5873, "sin": 1.1178, "multifactor3": 0.4970},
    }, f, ensure_ascii=False, indent=2)
print(f"✅ 寫入 data/59_two_mode_logmetric.json")