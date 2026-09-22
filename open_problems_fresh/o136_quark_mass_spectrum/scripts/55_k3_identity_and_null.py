#!/usr/bin/env python3
"""
O136 — Script 55: k=3 結構身份攻堅 + 真正有判別力嘅 null test
================================================================
Script 53 結果: Σ_i c^{−k} 之 RMS ≈ 0.685–0.726 (k=1..8) — 【對 k 幾乎平坦】
                k=3 之範圍 = 3.08e5 ≈ 所需 3.379e5

★ 關鍵自我檢查: 若 RMS 對 k 平坦, 則 k 唔可能由【形狀】決定
   ⟹ 「k=3 給出正確範圍」只係【用 k 去 tune 範圍】= 擬合, 唔係推導

本 script:
  (A) 精確 k 掃描 (細網格) — 最優 k 係幾多? 結構值 (3, B−1, N_gen, dimℂ) 特異嗎?
  (B) ★ 代數身份: c^{−1} = sec²(nβ/2) (折射率²) — 與 O203 sec 族之關係
  (C) ★★ null test 1: 隨機觀測方向 (N=2000) — 冷斑方向特異嗎?
  (D) ★★ null test 2: 隨機節點集 (N=1000) — A₅ 幾何特異嗎?
  (E) 裁決: k=3 有結構身份嗎?
"""
import numpy as np, math, json, random, itertools
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = ROOT / "cmb_cold_spot" / "data"
OUT = Path(__file__).parent.parent / "data"
M9 = [1,2,3,4,5,7,9,11,13]
ND = 44; B_ = 4; NGEN = 3
MASS = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
SP = sorted(MASS, key=lambda p: MASS[p])
LM = np.array([math.log(MASS[p]) for p in SP])
NEED_RANGE = max(MASS.values())/min(MASS.values())

nodes = np.loadtxt(DATA / "a5_nodes.txt")
ra, dec = np.radians(nodes[:,0]), np.radians(nodes[:,1])
U = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
cold = U[0].copy()

def fit_monotone(vals, LMv, agrid=None):
    if agrid is None: agrid = np.linspace(-8, 8, 1601)
    X = np.log(np.abs(np.array(vals))); Xs = np.sort(X)
    best = 9e9
    for a in agrid:
        res = LMv - a*Xs
        r = float(np.sqrt(np.mean((res - res.mean())**2)))
        if r < best: best = r
    return best

def stat_k(beta, k):
    return [float(((np.cos(n*beta/2)**2)**(-k)).sum()) for n in M9]

print("=" * 96)
print("O136 Script 55: k=3 結構身份 + 真正 null test")
print("=" * 96)

beta = np.arccos(np.clip(U @ cold, -1, 1))

# ═══ (A) 精確 k 掃描 ═════════════════════════════════
print(f"\n{'─'*96}\n(A) 精確 k 掃描 (細網格) — 最優 k 係幾多?\n{'─'*96}")
print(f"\n{'k':>7} {'最佳 RMS':>11} {'m 範圍':>13} {'範圍/所需':>11}")
print("-" * 46)
ks = [1.0,1.5,2.0,2.5,3.0,3.5,4.0,5.0,6.0,7.0,8.0,10.0]
kres = {}
for k in ks:
    vals = stat_k(beta, k)
    r = fit_monotone(vals, LM)
    vv = np.abs(np.array(vals)); rng = vv.max()/vv.min()
    kres[k] = (r, rng)
    mark = "  ★ k=3" if k == 3.0 else ("  ← 範圍最接近" if abs(rng/NEED_RANGE-1) < 0.15 else "")
    print(f"{k:>7.2f} {r:>11.4f} {rng:>13.4g} {rng/NEED_RANGE:>11.3f}{mark}")

best_rms_k = min(kres.items(), key=lambda kv: kv[1][0])
print(f"\n★ RMS 最優 k = {best_rms_k[0]} (RMS {best_rms_k[1][0]:.4f})")
print(f"★ RMS 之 k 跨度: [{min(v[0] for v in kres.values()):.4f}, {max(v[0] for v in kres.values()):.4f}]"
      f" → 變化僅 {max(v[0] for v in kres.values())/min(v[0] for v in kres.values()):.3f}×")
print(f"★★★ RMS 對 k 【幾乎平坦】⟹ k 唔由形狀決定")
print(f"★★★ 「k=3 給出正確範圍」= 用 k tune 範圍 = 擬合, 非推導")

# ═══ (B) 代數身份 ════════════════════════════════════
print(f"\n{'─'*96}\n(B) ★ 代數身份: c^{{−1}} = sec²(nβ/2) (折射率²)\n{'─'*96}")
print(f"  c_{{i,n}} = cos²(nβ_i/2) = (1+cos(nβ_i))/2")
print(f"  ⟹ c_{{i,n}}^{{−1}} = 2/(1+cos(nβ_i)) = 1/cos²(nβ_i/2) = sec²(nβ_i/2)")
print(f"  ⟹ Σ_i c^{{−k}} = Σ_i sec^{{2k}}(nβ_i/2)")
print(f"\n  ★ 與 O203 之關係: O203 排除 sec 族作【漂移】(Nyquist 發散),")
print(f"    但此處用於【質量】— 發散點 n=44 唔喺 9 選模式內, 故不衝突")
print(f"  ★ 物理讀法: sec = ω/k = 折射率 ⟹ Σ sec² = 折射率平方和 = 光程²")

# ═══ (C) ★★ null test 1: 隨機觀測方向 ═══════════════
print(f"\n{'─'*96}\n(C) ★★ null test 1: 隨機觀測方向 (N=2000) — 冷斑方向特異嗎?\n{'─'*96}")
rng = random.Random(20260920)
K_NULL = [1.0, 2.0, 3.0, 4.0, 6.0]
obs = {k: fit_monotone(stat_k(beta, k), LM) for k in K_NULL}
nulls1 = {k: [] for k in K_NULL}
for _ in range(2000):
    z = rng.uniform(-1, 1); ph = rng.uniform(0, 2*math.pi)
    r = math.sqrt(max(0.0, 1-z*z))
    d = np.array([r*math.cos(ph), r*math.sin(ph), z])
    bd = np.arccos(np.clip(U @ d, -1, 1))
    for k in K_NULL:
        nulls1[k].append(fit_monotone(stat_k(bd, k), LM, np.linspace(-8, 8, 401)))
print(f"\n{'k':>6} {'觀測 RMS':>10} {'null 中位':>11} {'null min':>10} {'P(≤觀測)':>10} {'判定':>10}")
print("-" * 66)
n1res = {}
for k in K_NULL:
    v = np.array(nulls1[k]); p = float((v <= obs[k]).mean())
    n1res[k] = {"median": float(np.median(v)), "min": float(v.min()), "p": p}
    flag = '🟢 顯著' if p < 0.05 else ('🟡 邊緣' if p < 0.2 else '🔴 唔顯著')
    print(f"{k:>6.1f} {obs[k]:>10.4f} {np.median(v):>11.4f} {v.min():>10.4f} {p:>10.4f} {flag:>10}")

# ═══ (D) ★★ null test 2: 隨機節點集 ═════════════════
print(f"\n{'─'*96}\n(D) ★★ null test 2: 隨機 60 節點集 (N=1000) — A₅ 幾何特異嗎?\n{'─'*96}")
nulls2 = {k: [] for k in K_NULL}
for _ in range(1000):
    z = np.array([rng.uniform(-1, 1) for _ in range(60)])
    ph = np.array([rng.uniform(0, 2*math.pi) for _ in range(60)])
    r = np.sqrt(np.maximum(0.0, 1-z*z))
    Ur = np.column_stack([r*np.cos(ph), r*np.sin(ph), z])
    bd = np.arccos(np.clip(Ur @ cold, -1, 1))
    for k in K_NULL:
        nulls2[k].append(fit_monotone(stat_k(bd, k), LM, np.linspace(-8, 8, 401)))
print(f"\n{'k':>6} {'觀測 RMS':>10} {'null 中位':>11} {'null min':>10} {'P(≤觀測)':>10} {'判定':>10}")
print("-" * 66)
n2res = {}
for k in K_NULL:
    v = np.array(nulls2[k]); p = float((v <= obs[k]).mean())
    n2res[k] = {"median": float(np.median(v)), "min": float(v.min()), "p": p}
    flag = '🟢 顯著' if p < 0.05 else ('🟡 邊緣' if p < 0.2 else '🔴 唔顯著')
    print(f"{k:>6.1f} {obs[k]:>10.4f} {np.median(v):>11.4f} {v.min():>10.4f} {p:>10.4f} {flag:>10}")

# ═══ (E) 裁決 ════════════════════════════════════════
print(f"\n{'─'*96}\n(E) 裁決: k = 3 有結構身份嗎?\n{'─'*96}")
print(f"""
  ① RMS 對 k 平坦 (變化 {max(v[0] for v in kres.values())/min(v[0] for v in kres.values()):.3f}×)
     ⟹ 形狀【唔】決定 k
  ② 範圍可由 k 自由調節 (k=1 → 65; k=3 → 3.08e5; k=8 → 1.36e14)
     ⟹ 「k=3 命中所需範圍」係【用 k 擬合範圍】
  ③ 結構候選 k ∈ {{3, B−1=3, N_gen=3, dimℂ=3}} 全部同值 ⟹ 【無法區分】
     (3, 3, 3, 3 — 四個結構常數都係 3, 冇判別力)
  ④ null test 1 (隨機方向) P = {n1res[3.0]['p']:.4f}
  ⑤ null test 2 (隨機節點集) P = {n2res[3.0]['p']:.4f}
""")

with open(OUT/"55_k3_identity_and_null.json", "w") as f:
    json.dump({
        "k_scan": {str(k): {"rms": v[0], "range": v[1], "range_ratio": v[1]/NEED_RANGE}
                   for k, v in kres.items()},
        "best_rms_k": best_rms_k[0],
        "rms_span_ratio": max(v[0] for v in kres.values())/min(v[0] for v in kres.values()),
        "algebraic_identity": "c^{−1} = sec²(nβ/2) (折射率²); Σc^{−k} = Σ sec^{2k}",
        "null1_random_direction": {str(k): v for k, v in n1res.items()},
        "null2_random_nodes": {str(k): v for k, v in n2res.items()},
        "need_range": NEED_RANGE,
        "reference": {"2nd_order": 0.5873, "c_m2": 0.6854, "sin": 0.8028},
    }, f, ensure_ascii=False, indent=2)
print(f"✅ 寫入 data/55_k3_identity_and_null.json")