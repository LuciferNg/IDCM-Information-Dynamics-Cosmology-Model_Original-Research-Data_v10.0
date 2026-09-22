#!/usr/bin/env python3
"""
O136 — Script 57: 二模式質量算子攻堅

⚠️⚠️ 【本 script 度量錯誤, 已由 scripts/59 取代 — 見 docs/32 §二】
    本 script 用【原始值】擬合 ln m ~ f (指數擬合 m ∝ e^{af})
    正確應用 ln f (冪律 m ∝ f^a); 實測 sum_V2_dE 原始 2.7335 vs 對數 0.5872
    ⚠️ 保留作 bug 記錄; 結論以 scripts/59 為準
================================================================
結構動機 (由既有定理強制, 非猜測):
  ★ docs/26 §一 定理: 冇任何【n 的函數】能同時滿足 9 個質量比 (α 跨度 42.6×)
  ★ docs/31 §五 飽和: 15 因子庫多因子乘積，參數 1→4 僅改善 1.18×
  ★ 22 個已排除方向【全部】把觀察者當【固定外部基準】或【無觀察者】
  ⟹ 結構性空白: 【二模式算子】M(n,m) — 觀察者係變量

既有權威構造 (scripts/41, docs/25):
  88-site D-D 鏈: ψ_n(i) = sin(nπi/89), i=1..88
  X = diag(i − ⟨i⟩)  ⟹ V_nm = ⟨n|X|m⟩  (Z₂-奇: |n−m| 奇時非零)
  E_n = 4sin²(nπ/88)  (44-鏈譜, Σγ=90)

本 script:
  (A) 重建 V 矩陣 + 驗證 Z₂-奇結構
  (B) 二模式量族全掃描 (Σ|V|²/ΔE^p, 行範數, 主導夥伴, (V^k)_nn, ...)
  (C) ★★ null test 1: 隨機 9 模式集 (N=2000) — A₅ 模式集特異嗎?
  (D) ★★ null test 2: 隨機 Z₂-奇耦合 (N=1000)
  (E) 裁決
"""
import numpy as np, math, json, random, itertools
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"
M9 = [1,2,3,4,5,7,9,11,13]
NC = 88
MASS = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
SP = sorted(MASS, key=lambda p: MASS[p])
LM = np.array([math.log(MASS[p]) for p in SP])
NEED = 0.05

# ═══ (A) 重建 V ══════════════════════════════════════
x = np.arange(1, NC+1, dtype=float)
Psi = np.zeros((NC, NC))
for n in range(1, NC+1):
    Psi[:, n-1] = np.sin(n*math.pi*x/(NC+1))
for n in range(NC):
    Psi[:, n] /= np.linalg.norm(Psi[:, n])
X = np.diag(x - x.mean())
V = Psi.T @ X @ Psi
E = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1, NC+1)])

print("=" * 96)
print("O136 Script 57: 二模式質量算子攻堅")
print("=" * 96)
print(f"\n{'─'*96}\n(A) V = ⟨n|X|m⟩ 結構驗證\n{'─'*96}")
same = max(abs(V[n,m]) for n in range(30) for m in range(30) if n != m and (n-m) % 2 == 0)
diff = max(abs(V[n,m]) for n in range(30) for m in range(30) if (n-m) % 2 == 1)
print(f"  |V_nm| max, |n−m| 偶 = {same:.3e}   (應 ≈ 0)")
print(f"  |V_nm| max, |n−m| 奇 = {diff:.3e}   (應非零)")
print(f"  ⟹ Z₂-奇結構 {'✅ 確認' if same < 1e-9 and diff > 1e-3 else '🔴 失敗'}")
print(f"  Σγ (n=1..88) = {E.sum():.6f}  (已知 90 × 2 = 180? 註: 44-鏈慣例 n=1..44)")
E44 = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1, 45)])
print(f"  Σγ (n=1..44) = {E44.sum():.6f}  (= 90 ✅)")

# ═══ 候選族 ══════════════════════════════════════════
def cand_values(modes, Vm=None, Em=None):
    Vv = V if Vm is None else Vm
    Ev = E if Em is None else Em
    out = {}
    for n in modes:
        idx = [m for m in range(NC) if m != n-1 and (m-(n-1)) % 2 == 1]
        dE = Ev[n-1] - Ev[idx]
        aV2 = np.abs(Vv[n-1, idx])**2
        out.setdefault("sum_V2", []).append(float(aV2.sum()))
        out.setdefault("sum_V2_dE", []).append(float((aV2/dE).sum()))
        out.setdefault("sum_V2_dE2", []).append(float((aV2/dE**2).sum()))
        out.setdefault("sum_V2_dE3", []).append(float((aV2/dE**3).sum()))
        out.setdefault("row_norm", []).append(float(np.linalg.norm(Vv[n-1, idx])))
        out.setdefault("max_V", []).append(float(np.abs(Vv[n-1, idx]).max()))
        out.setdefault("max_V2_dE", []).append(float((aV2/dE).max()))
        out.setdefault("min_dE", []).append(float(np.abs(dE).min()))
        out.setdefault("V2diag", []).append(float((Vv @ Vv)[n-1, n-1]))
        out.setdefault("V3diag", []).append(float((Vv @ Vv @ Vv)[n-1, n-1]))
        out.setdefault("V4diag", []).append(float((Vv @ Vv @ Vv @ Vv)[n-1, n-1]))
        out.setdefault("sum_absV_dE", []).append(float((np.abs(Vv[n-1, idx])/dE).sum()))
        out.setdefault("sum_1_dE", []).append(float((1.0/np.abs(dE)).sum()))
        out.setdefault("sum_1_dE2", []).append(float((1.0/dE**2).sum()))
        out.setdefault("purity", []).append(float(aV2.sum()**2/(aV2**2).sum()))
    return out

def score(vals, LMv=None):
    y = LM if LMv is None else LMv
    v = np.array(vals)
    if v.std() < 1e-14: return 9e9
    o = np.argsort(v); xs = v[o]; ys = np.sort(y)
    r = float(np.corrcoef(xs, ys)[0, 1])
    return float(ys.std()*math.sqrt(max(0.0, 1.0-r*r)))

CV = cand_values(M9)
print(f"\n{'─'*96}\n(B) 二模式量族全掃描 ({len(CV)} 候選)\n{'─'*96}")
print(f"\n{'候選':>16} {'RMS':>9} {'值範圍':>12} {'判定':>10}")
print("-" * 52)
res = {}
for k, v in CV.items():
    r = score(v); res[k] = r
    vv = np.abs(np.array(v))
    rng = vv.max()/vv.min() if vv.min() > 0 else float('inf')
    flag = '✅ 閉合' if r < NEED else ('🟡 佳' if r < 0.60 else '🔴')
    print(f"{k:>16} {r:>9.4f} {rng:>12.4g} {flag:>10}")
best = min(res.items(), key=lambda kv: kv[1])
print(f"\n★ 最佳 = {best[0]} (RMS {best[1]:.4f})")
print(f"★ 對照: 已知最佳 |Δm| = 0.5873;  sin = 1.1178;  閉合需 < {NEED}")

# ═══ (C) ★★ null test 1: 隨機模式集 ══════════════════
print(f"\n{'─'*96}\n(C) ★★ null test 1: 隨機 9 模式集 (N=2000) — A₅ 模式集特異嗎?\n{'─'*96}")
rng = random.Random(20260920)
KEYS = list(CV.keys())
obs = {k: score(CV[k]) for k in KEYS}
null1 = {k: [] for k in KEYS}
for _ in range(2000):
    md = rng.sample(range(1, NC+1), 9)
    cv = cand_values(md)
    for k in KEYS:
        null1[k].append(score(cv[k]))
print(f"\n{'候選':>16} {'觀測 RMS':>10} {'null 中位':>11} {'null min':>10} {'P(≤觀測)':>10} {'判定':>10}")
print("-" * 72)
n1 = {}
for k in KEYS:
    v = np.array(null1[k]); p = float((v <= obs[k]).mean())
    n1[k] = {"median": float(np.median(v)), "min": float(v.min()), "p": p}
    flag = '🟢 顯著' if p < 0.05 else ('🟡 邊緣' if p < 0.2 else '🔴 唔顯著')
    print(f"{k:>16} {obs[k]:>10.4f} {np.median(v):>11.4f} {v.min():>10.4f} {p:>10.4f} {flag:>10}")

# ═══ (D) ★★ null test 2: 隨機 Z₂-奇耦合 ═════════════
print(f"\n{'─'*96}\n(D) ★★ null test 2: 隨機 Z₂-奇耦合 (N=1000)\n{'─'*96}")
null2 = {k: [] for k in KEYS}
for _ in range(1000):
    W = np.zeros((NC, NC))
    A = np.random.randn(NC, NC)
    for i in range(NC):
        for j in range(NC):
            if (i-j) % 2 == 1: W[i, j] = A[i, j]
    W = (W - W.T)/2.0
    cv = cand_values(M9, Vm=W, Em=E)
    for k in KEYS:
        null2[k].append(score(cv[k]))
print(f"\n{'候選':>16} {'觀測 RMS':>10} {'null 中位':>11} {'null min':>10} {'P(≤觀測)':>10} {'判定':>10}")
print("-" * 72)
n2 = {}
for k in KEYS:
    v = np.array(null2[k]); p = float((v <= obs[k]).mean())
    n2[k] = {"median": float(np.median(v)), "min": float(v.min()), "p": p}
    flag = '🟢 顯著' if p < 0.05 else ('🟡 邊緣' if p < 0.2 else '🔴 唔顯著')
    print(f"{k:>16} {obs[k]:>10.4f} {np.median(v):>11.4f} {v.min():>10.4f} {p:>10.4f} {flag:>10}")

# ═══ (E) 裁決 ════════════════════════════════════════
print(f"\n{'─'*96}\n(E) 裁決\n{'─'*96}")
print(f"""
  ① 二模式量族最佳: {best[0]} = {best[1]:.4f}  (對照 |Δm| = 0.5873)
  ② 閉合所需: < {NEED}  ⟹ {'✅' if best[1] < NEED else '🔴 未閉合'}
  ③ null test 1 (隨機模式集): {best[0]} P = {n1[best[0]]['p']:.4f}
  ④ null test 2 (隨機耦合):   {best[0]} P = {n2[best[0]]['p']:.4f}
  ⑤ ★ 有效 null: 本輪配對由【重排不等式】定 ⟹ 隨機化【模式集/耦合】而非質量
     ⟹ 避免 docs/31 §六 之置換退化 ✅
""")

with open(OUT/"57_two_mode_operator.json", "w") as f:
    json.dump({
        "z2_check": {"same_parity_max": float(same), "diff_parity_max": float(diff)},
        "candidates": {k: {"rms": v, "range": float(np.abs(np.array(CV[k])).max()/np.abs(np.array(CV[k])).min())
                           if np.abs(np.array(CV[k])).min() > 0 else None}
                       for k, v in res.items()},
        "best": {"name": best[0], "rms": best[1]},
        "null1_random_modeset": n1,
        "null2_random_coupling": n2,
        "closure_threshold": NEED,
        "reference": {"absdm": 0.5873, "sin": 1.1178, "multifactor3": 0.4970},
    }, f, ensure_ascii=False, indent=2)
print(f"✅ 寫入 data/57_two_mode_operator.json")