#!/usr/bin/env python3
"""
O136 — Script 51: Gemini 提案補測 — 唯一非退化幾何量 (A₅ 質心)
================================================================
Script 50 結果: 10 個 |O⟩ 定義全部失敗。三個退化:
  (a) |O⟩=A₅ Node 0 → c_{0,n}=1 ∀n (β₀=0)
  (d) |O⟩=世界扇區  → 0/1 by parity
  (e) |O⟩=鏈基態    → 鏈模式正交 ⟹ ⟨n|m⟩=δ_nm

但 Script 50 意外發現一個【非退化】量:
  w_n = Σ_i c_{i,n} v_i  (A₅ 投影之向量質心)
  方向有模式依賴: n=1 → 0.000013°, n=3 → 179.999981°, n=5 → 146.94°,
                 n=7 → 117.11°, n=9 → 160.25°, n=11 → 35.46°, n=13 → 67.31°
  ⚠️ 但 n=2, 4 (兩個偶模式) |w|=0 → 無方向

本 script: 測試質心相關候選
  (A) |w_n|^k
  (B) (1 − cos∠(w_n, n0))^k
  (C) sin²(∠/2) (弦長²)
  (D) 質心與最遠節點之關係
  (E) 投影二階矩 Σ c β² (展開寬度)
"""
import numpy as np, math, json, itertools
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"
M9 = [1,2,3,4,5,7,9,11,13]
MASS = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
SP = sorted(MASS, key=lambda p: MASS[p])
LM = np.array([math.log(MASS[p]) for p in SP])

A5 = [tuple(map(float, l.split()[:2])) for l in
      open("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/cmb_cold_spot/data/a5_nodes.txt").read().strip().splitlines()
      if len(l.split()) >= 2]
v = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
               math.cos(math.radians(d))*math.sin(math.radians(r)),
               math.sin(math.radians(d))] for r, d in A5])
n0 = v[0]
beta = np.arccos(np.clip(v @ n0, -1, 1)); bd = np.degrees(beta)

print("=" * 96)
print("O136 Script 51: Gemini 提案補測 — A₅ 質心相關候選")
print("=" * 96)

def rms_best(vals):
    vv = np.abs(np.array(vals))
    if np.any(vv <= 1e-300): return None
    X = np.log(vv); best = (9e9, None, None)
    for perm in itertools.permutations(range(9)):
        Xp = X[list(perm)]
        A = np.vstack([np.ones(9), Xp]).T
        c, *_ = np.linalg.lstsq(A, LM, rcond=None)
        r = float(np.sqrt(np.mean((A@c-LM)**2)))
        if r < best[0]: best = (r, perm, float(c[1]))
    return best

# ── 質心量 ──
W, ANG, M2, M4 = {}, {}, {}, {}
for n in M9:
    c = np.cos(n*beta/2)**2
    w = (c[:, None]*v).sum(axis=0)
    W[n] = float(np.linalg.norm(w))
    if W[n] > 1e-9:
        ANG[n] = math.degrees(math.acos(max(-1, min(1, float(w @ n0)/W[n]))))
    else:
        ANG[n] = None
    M2[n] = float((c*bd**2).sum()/c.sum())      # 二階矩 (展開寬度)
    M4[n] = float((c*bd**4).sum()/c.sum())

print(f"\n{'─'*96}\n1. 質心量一覽\n{'─'*96}")
print(f"\n{'n':>3} {'|w_n|':>10} {'∠(w,n0)':>12} {'Σcβ²/Σc':>12} {'Σcβ⁴/Σc':>12}")
print("-" * 52)
for n in M9:
    a = f"{ANG[n]:.4f}" if ANG[n] is not None else "—(零)"
    print(f"{n:>3} {W[n]:>10.5f} {a:>12} {M2[n]:>12.2f} {M4[n]:>12.2f}")

# ── 候選 ──
cands = {}
cands["|w_n|"] = [W[n] for n in M9]
cands["1/|w_n|"] = [1.0/W[n] if W[n] > 1e-9 else 1e-300 for n in M9]
cands["Σcβ²/Σc (寬度)"] = [M2[n] for n in M9]
cands["Σcβ⁴/Σc"] = [M4[n] for n in M9]
cands["1/寬度"] = [1.0/M2[n] for n in M9]
# 角度相關 (n=2,4 無角度 → 用 180° 填充, 並另測只用 7 個奇模式)
ang_fill = [ANG[n] if ANG[n] is not None else 180.0 for n in M9]
cands["cos∠(w,n0)"] = [math.cos(math.radians(a)) for a in ang_fill]
cands["1−cos∠"] = [1 - math.cos(math.radians(a)) for a in ang_fill]
cands["sin²(∠/2) 弦長²"] = [math.sin(math.radians(a)/2)**2 for a in ang_fill]
cands["∠(w,n0) 度"] = [a for a in ang_fill]

print(f"\n{'─'*96}\n2. 譜形檢驗 (RMS, 最佳配對)\n{'─'*96}")
print(f"\n{'候選':>22} {'最佳 RMS':>10} {'α':>9} {'m 範圍':>12} {'判定':>8}")
print("-" * 66)
res = {}
for name, vals in cands.items():
    vv = np.abs(np.array(vals))
    rng = (vv.max()/vv.min()) if vv.min() > 1e-300 else float('inf')
    if len(set(np.round(vv, 12))) < 3 or vv.min() <= 1e-300:
        print(f"{name:>22} {'退化':>10} {'—':>9} {rng:>12.3g} {'🔴':>8}"); continue
    b = rms_best(vals)
    if b is None: continue
    res[name] = (b[0], b[2], b[1])
    ps = " ".join(f"{SP[i][0]}:{M9[b[1][i]]}" for i in range(9))
    flag = '🟢' if b[0] < 0.3 else ('🟡' if b[0] < 0.8 else '🔴')
    print(f"{name:>22} {b[0]:>10.4f} {b[2]:>9.4f} {rng:>12.3g} {flag:>8}   {ps}")

# ── 只用 7 個奇模式 (質心非零) ──
print(f"\n{'─'*96}\n3. 只用 7 個奇模式 (質心非零, 無退化)\n{'─'*96}")
M7 = [1,3,5,7,9,11,13]
PARTS7 = ["e","mu","tau","u","d","s","c","b","t"]
# 7 模式 vs 9 粒子 → 無法完整覆蓋, 只報相關性
print(f"  ⚠️ 7 模式 vs 9 粒子 → 無法完整覆蓋 ⟹ 結構上唔可以係完整處方")
for name, fn in [("∠(w,n0)", lambda n: ANG[n]), ("|w_n|", lambda n: W[n]),
                 ("Σcβ²/Σc", lambda n: M2[n])]:
    xs = [fn(n) for n in M7]
    ys = [MASS[p] for p in ["e","mu","tau","u","d","s","c"][:7]]
    r = float(np.corrcoef(xs, np.log(ys))[0,1])
    print(f"  {name:>12}: 7 模式 vs 7 最輕粒子 之 corr = {r:>7.4f}")

print(f"\n★ 對照: |Δm| 0.5873 | 累積乘積 0.7106 | sin 0.8028 | 上限 3.8588")
print(f"★ 所需 m 範圍 = {max(MASS.values())/min(MASS.values()):.3e}")

with open(OUT/"51_centroid_test.json", "w") as f:
    json.dump({
        "centroid": {str(n): {"|w|": W[n], "angle_deg": ANG[n], "M2": M2[n], "M4": M4[n]} for n in M9},
        "rms": {k: {"rms": v[0], "alpha": v[1],
                    "pairing": {SP[i]: M9[v[2][i]] for i in range(9)}} for k, v in res.items()},
        "degenerate": {"n_2_4": "|w|=0 (偶模式質心為零)", "M7_vs_9": "7 奇模式無法覆蓋 9 粒子"},
        "reference": {"2nd_order": 0.5873, "cumprod": 0.7106, "sin": 0.8028, "upper": float(LM.std())},
    }, f, ensure_ascii=False, indent=2)
print(f"\n✅ 寫入 data/51_centroid_test.json")