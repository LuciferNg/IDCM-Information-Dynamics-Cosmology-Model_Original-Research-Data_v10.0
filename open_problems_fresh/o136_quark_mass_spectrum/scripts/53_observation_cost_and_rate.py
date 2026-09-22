#!/usr/bin/env python3
"""
O136 — Script 53: 觀察代價族 (逆向冪次) + 質量=速率族 + 截斷/黑洞極限
================================================================================
觸發:
  (1) Script 52 發現逆向冪次 Σ_i c^{−k} 明顯優於正向 — Σ c^{−2} = 0.6854 (第二佳)
      (物理: 投影小 = 難觀察 = 重 — 正是「觀察代價」直覺)
  (2) 用戶新提案: 「質量是否可能是時間賦予的? 質量密度越大 ⟺ 交互時間阻尼越大;
      阻尼無限大 → 投影截斷 → 黑洞」

本 script:
  (A) ★ 觀察代價族全掃描: Σ_i c^{−k}, min_i c^{−k}, (Σ c^{−1})^k, Π_i c^{−1}
  (B) ★ 質量=速率族 (Fermi golden rule / DOS / 解相干 / 截斷距離)
  (C) ★ 截斷極限檢驗: 有咩量喺 n = N_d = 44 發散? (Nyquist v_g=0 / OPAQUE 邊)
  (D) null test: 最佳候選 vs 隨機

對照: |Δm| 二階自能 0.5873 | Σ c^{−2} 0.6854 | cumprod 0.7106 | sin 0.8028 | 上限 3.8588
"""
import numpy as np, math, json, itertools, random
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = ROOT / "cmb_cold_spot" / "data"
OUT = Path(__file__).parent.parent / "data"
M9 = [1,2,3,4,5,7,9,11,13]
ND = 44
MASS = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
SP = sorted(MASS, key=lambda p: MASS[p])
LM = np.array([math.log(MASS[p]) for p in SP])

nodes = np.loadtxt(DATA / "a5_nodes.txt")
ra, dec = np.radians(nodes[:,0]), np.radians(nodes[:,1])
U = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
cold = U[0].copy()
beta = np.arccos(np.clip(U @ cold, -1, 1))

print("=" * 96)
print("O136 Script 53: 觀察代價族 + 質量=速率族 + 截斷極限")
print("=" * 96)

def rms_best(vals):
    v = np.abs(np.array(vals))
    if np.any(v <= 1e-300): return None
    X = np.log(v); best = (9e9, None, None)
    for perm in itertools.permutations(range(9)):
        Xp = X[list(perm)]
        A = np.vstack([np.ones(9), Xp]).T
        c, *_ = np.linalg.lstsq(A, LM, rcond=None)
        r = float(np.sqrt(np.mean((A@c-LM)**2)))
        if r < best[0]: best = (r, perm, float(c[1]))
    return best

C = {n: np.cos(n*beta/2)**2 for n in M9}

# ═══ (A) 觀察代價族 ═════════════════════════════════
print(f"\n{'─'*96}\n(A) ★ 觀察代價族 (逆向冪次) 全掃描\n{'─'*96}")
cands = {}
for k in [1,2,3,4,5,6,8]:
    cands[f"Σ_i c^(−{k})"] = [float((C[n]**(-k)).sum()) for n in M9]
    cands[f"min_i c^(−{k})"] = [float((C[n]**(-k)).min()) for n in M9]
for k in [1,2,3]:
    cands[f"(Σ_i c^(−1))^{k}"] = [float((C[n]**(-1)).sum()**k) for n in M9]
cands["Π_i c^(−1)"] = [float(np.prod(C[n]**(-1))) for n in M9]
cands["Σ_i ln(1/c)"] = [float(np.log(1.0/C[n]).sum()) for n in M9]

print(f"\n{'候選':>20} {'最佳 RMS':>11} {'α':>9} {'m 範圍':>12} {'判定':>8}")
print("-" * 66)
resA = {}
for name, vals in cands.items():
    vv = np.abs(np.array(vals))
    if vv.min() <= 1e-300 or len(set(np.round(vv,10))) < 3:
        print(f"{name:>20} {'退化':>11} {'—':>9} {'—':>12} {'🔴':>8}"); continue
    b = rms_best(vals)
    if b is None: continue
    resA[name] = (b[0], b[2], b[1])
    rng = vv.max()/vv.min()
    flag = '🟢' if b[0] < 0.3 else ('🟡' if b[0] < 0.8 else '🔴')
    print(f"{name:>20} {b[0]:>11.4f} {b[2]:>9.4f} {rng:>12.3g} {flag:>8}")

# ═══ (B) 質量=速率族 ═════════════════════════════════
print(f"\n{'─'*96}\n(B) ★ 質量 = 速率族 (時間/阻尼讀法)\n{'─'*96}")
g = lambda n: 4*math.sin(n*math.pi/88)**2          # 44-鏈 γ_n
g176 = lambda n: 4*math.sin(n*math.pi/176)**2      # 176-鏈
vg = lambda n: math.cos(n*math.pi/88)              # 群速度/c
candsB = {
    "DOS = 1/|dE/dn|": [1.0/max(abs(2*math.sin(2*n*math.pi/88)), 1e-300) for n in M9],
    "Fermi Γ ∝ DOS/γ": [1.0/max(abs(2*math.sin(2*n*math.pi/88))*g(n), 1e-300) for n in M9],
    "1/(1−cos(nπ/88))": [1.0/(1-math.cos(n*math.pi/88)) for n in M9],
    "1/sin²(nπ/176)": [1.0/g176(n) for n in M9],
    "1/v_g²": [1.0/max(vg(n)**2, 1e-300) for n in M9],
    "1/(N_d−n)^k": [1.0/(ND-n) for n in M9],
    "n^1 (對照)": [float(n) for n in M9],
    "1/γ_n (44鏈)": [1.0/g(n) for n in M9],
    "γ_n (44鏈)": [g(n) for n in M9],
    "1/γ_n²": [1.0/g(n)**2 for n in M9],
    "解相干率 1/cos": [1.0/max(vg(n), 1e-300) for n in M9],
}
print(f"\n{'候選':>20} {'最佳 RMS':>11} {'α':>9} {'m 範圍':>12} {'判定':>8}")
print("-" * 66)
resB = {}
for name, vals in candsB.items():
    vv = np.abs(np.array(vals))
    b = rms_best(vals)
    if b is None: continue
    resB[name] = (b[0], b[2], b[1])
    rng = vv.max()/vv.min()
    flag = '🟢' if b[0] < 0.3 else ('🟡' if b[0] < 0.8 else '🔴')
    print(f"{name:>20} {b[0]:>11.4f} {b[2]:>9.4f} {rng:>12.3g} {flag:>8}")

# ═══ (C) 截斷極限檢驗 ════════════════════════════════
print(f"\n{'─'*96}\n(C) ★ 截斷極限: 有咩量喺 n = N_d = 44 發散?\n{'─'*96}")
print(f"\n{'量':>26} {'n=1':>12} {'n=22':>12} {'n=44':>14} {'發散?':>8}")
print("-" * 76)
for name, fn in [("v_g/c = cos(nπ/88)", lambda n: math.cos(n*math.pi/88)),
                 ("1/v_g", lambda n: 1.0/max(math.cos(n*math.pi/88), 1e-300)),
                 ("1/(1−cos)", lambda n: 1.0/(1-math.cos(n*math.pi/88))),
                 ("DOS ∝ 1/|sin(2nπ/88)|", lambda n: 1.0/max(abs(math.sin(2*n*math.pi/88)), 1e-300)),
                 ("γ_n (44鏈)", lambda n: 4*math.sin(n*math.pi/88)**2),
                 ("γ_n (176鏈)", lambda n: 4*math.sin(n*math.pi/176)**2)]:
    v1, v22, v44 = fn(1), fn(22), fn(44)
    div = "★ 是" if abs(v44) > 1e6 else ("是" if abs(v44) > abs(v1)*10 else "否")
    print(f"{name:>26} {v1:>12.6g} {v22:>12.6g} {v44:>14.6g} {div:>8}")
print(f"\n  ★ n=44 (Nyquist): v_g = 0 精確 (駐波) ⟹ 1/v_g 結構發散")
print(f"  ★ 但 44 = N_d 唔喺 9 選模式內 ⟹ 質量譜唔直接受影響")
print(f"  ★ OPAQUE 邊 = 32 條 (O182) = 已存在嘅「投影截斷」結構")

# ═══ (D) null test → 已移至 scripts/54 (快速版, 避免 300 × 9! = 1.09e8) ═══
print(f"\n{'─'*96}\n(D) null test → 見 scripts/54_observation_cost_null.py\n{'─'*96}")

with open(OUT/"53_observation_cost_and_rate.json", "w") as f:
    json.dump({
        "observation_cost": {k: {"rms": v[0], "alpha": v[1],
                                 "pairing": {SP[i]: M9[v[2][i]] for i in range(9)}} for k, v in resA.items()},
        "rate_family": {k: {"rms": v[0], "alpha": v[1],
                            "pairing": {SP[i]: M9[v[2][i]] for i in range(9)}} for k, v in resB.items()},
        "reference": {"2nd_order": 0.5873, "c_m2_script52": 0.6854, "cumprod": 0.7106,
                      "sin": 0.8028, "upper": float(LM.std())},
    }, f, ensure_ascii=False, indent=2)
print(f"\n✅ 寫入 data/53_observation_cost_and_rate.json")