#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O119 - Script 14: p_CR 結構化攻堅 (真實 AMS-02 質子譜)
====================================================
剩餘開放項: 「CR 譜指數 p_CR = 2.7 結構」。
本 script 用真實 AMS-02 質子通量 (72 點, 剛度 1-1800 GV, CRDB) 量度實際指數,
然後測試 IDCM 結構推導路線:
  (A) 強激波擴散加速 (DSA): p_inj = (r+2)/(r-1), r = 壓縮比
      IDCM: r = B = 4 (K_Tree 分支數 / 強激波) ⟹ p_inj = 2 = μ²
  (B) 觀測指數 = p_inj + δ (傳播); δ 掃結構數池
  (C) 直接掃 p_CR 本身嘅結構身份 (含密度基準)
數據源: data/obs/ams02_proton_flux_R.csv (CRDB; Aguilar+ 2021 Phys.Rept.894)
"""
import csv, io, math, os
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBS = os.path.join(BASE, "data", "obs")

print("=" * 74)
print("O119 Script 14: p_CR 結構化攻堅")
print("=" * 74)

R, Phi, sig = [], [], []
with io.open(os.path.join(OBS, "ams02_proton_flux_R.csv"), encoding="utf-8") as fh:
    for line in fh:
        if line.startswith("#") or not line.strip():
            continue
        p = next(csv.reader([line]))
        R.append(float(p[1])); Phi.append(float(p[4]))
        st = max(float(p[5]), float(p[6])); sy = max(float(p[7]), float(p[8]))
        sig.append(math.sqrt(st**2 + sy**2))
R = np.array(R); Phi = np.array(Phi); sig = np.array(sig)
print(f"  載入 {len(R)} 點, R ∈ [{R.min():.2f}, {R.max():.0f}] GV")

passed = 0; total = 0
def check(name, cond, detail=""):
    global passed, total
    total += 1
    if cond: passed += 1; print(f"  ✅ {name} {detail}")
    else: print(f"  ❌ {name} {detail}")

def fit_index(mask):
    x = np.log(R[mask]); y = np.log(Phi[mask]); s = sig[mask] / Phi[mask]
    w = 1.0 / s**2
    W = w.sum(); swx = (w*x).sum(); swy = (w*y).sum()
    swxx = (w*x*x).sum(); swxy = (w*x*y).sum()
    det = W*swxx - swx**2
    m = (W*swxy - swx*swy)/det
    b = (swxx*swy - swx*swxy)/det
    sm = math.sqrt(W/det)
    return m, sm, b

print("\n[1] 真實質子譜指數 (d ln Phi / d ln R)")
for lo, hi in ((1, 1800), (10, 1800), (30, 1800), (100, 1800), (1, 10), (200, 1800)):
    m = (R >= lo) & (R <= hi)
    if m.sum() < 3: continue
    slope, sm, b = fit_index(m)
    print(f"  R ∈ [{lo:>4}, {hi:>4}] GV: {m.sum():>2} 點 -> 指數 = {-slope:.3f} ± {sm:.3f}")
slope_all, sm_all, _ = fit_index(np.ones(len(R), bool))
slope_hard, sm_hard, _ = fit_index(R >= 10)   # 太陽調制以上
print(f"  全範圍加權指數 = {-slope_all:.3f} ± {sm_all:.3f} (含低 R 太陽調制)")
print(f"  R > 10 GV 指數 = {-slope_hard:.3f} ± {sm_hard:.3f} (太陽調制以上, 物理值)")
check("太陽調制以上真實指數 > 2.5 (確認係硬譜)", -slope_hard > 2.5, f"({-slope_hard:.3f})")

# ---------- 2. DSA 路線 ----------
print("\n[2] DSA 結構路線: p_inj = (r+2)/(r-1)")
print(f"  {'r (壓縮比)':>12}{'p_inj':>10}  來源")
for r, src in ((4, "強激波 / K_Tree B=4"), (3, "—"), (5, "—"), (2, "—")):
    print(f"  {r:>12}{ (r+2)/(r-1):>10.3f}  {src}")
print("  ⟹ r = B = 4 給 p_inj = 2 = μ² (IDCM 結構數)")
print("  ⚠️ 但 r = 4 係任何強激波嘅普適值 (γ=5/3 Rankine-Hugoniot), 唔係 IDCM 獨有")
p_inj = 2.0
delta = -slope_hard - p_inj
print(f"  ⟹ 需要傳播修正 δ = p_obs - p_inj = {-slope_hard:.3f} - 2 = {delta:.3f}")

# δ 結構掃描 + 密度基準
print("\n[3] 傳播指數 δ 結構掃描 (含密度基準)")
POOL = {"N_d": 44, "B": 4, "N_gen": 3, "mu2": 2, "M": 33, "F_proj": 17,
        "F5": 5, "F6": 8, "F7": 13, "F8": 21, "F9": 34,
        "L4": 7, "L5": 11, "L6": 18, "L7": 29, "L8": 47,
        "Sgamma": 90, "h11": 36, "N88": 88, "N176": 176, "C44_2": 946, "dimC528": 528}
def exprs(pool):
    ks = list(pool); vs = [pool[k] for k in ks]; n = len(ks); out = []
    for i in range(n):
        for j in range(n):
            if i == j: continue
            a, b = vs[i], vs[j]
            out.append((f"{ks[i]}/{ks[j]}", a/b))
            for k in range(n):
                if k in (i, j): continue
                c = vs[k]
                out.append((f"({ks[i]}+{ks[j]})/{ks[k]}", (a+b)/c))
                out.append((f"({ks[i]}-{ks[j]})/{ks[k]}", (a-b)/c))
                out.append((f"{ks[i]}/({ks[j]}+{ks[k]})", a/(b+c)))
                if abs(b-c) > 1e-12: out.append((f"{ks[i]}/({ks[j]}-{ks[k]})", a/(b-c)))
    return [(l, v) for l, v in out if v > 0 and math.isfinite(v)]
E = exprs(POOL); V = np.array(sorted(v for _, v in E))
print(f"  N_search = {len(V)}")

def baseline(target, lo, hi, N=100000, seed=11):
    i = int(np.searchsorted(V, target))
    cand = []
    if i < len(V): cand.append(abs(V[i] / target - 1))
    if i > 0: cand.append(abs(V[i - 1] / target - 1))
    dev = min(cand)
    rng = np.random.default_rng(seed)
    ts = np.exp(rng.uniform(math.log(lo), math.log(hi), N))
    idx = np.searchsorted(V, ts)
    dv = np.full(N, np.inf)
    m = idx < len(V); dv[m] = np.minimum(dv[m], np.abs(V[idx[m]]/ts[m]-1))
    m = idx > 0; dv[m] = np.minimum(dv[m], np.abs(V[idx[m]-1]/ts[m]-1))
    return dev, float(np.median(dv)), float(np.mean(dv <= dev)), int(np.sum(np.abs(V/target-1) <= dev))

qmap = {}
for tgt, nm in ((delta, "delta_prop"), (2.7, "p_CR"), (2.0, "p_inj")):
    dev, dm, q, hits = baseline(tgt, 0.2, 4.0)
    best = min((abs(v/tgt-1), l, v) for l, v in E)
    qmap[nm] = q
    print(f"  {nm:<14} 目標 {tgt:.3f}: 池內最近 {best[1]} = {best[2]:.4f} (dev {best[0]*100:.3f}%), "
          f"q_obs = {q:.3f}, 命中 {hits}")
q_delta = qmap["delta_prop"]; q_p_CR = qmap["p_CR"]

print(f"\n  ⟹ δ = {delta:.3f}: q_obs = {q_delta:.3f}")
check("δ 冇唯一結構 (q_obs > 5%)", q_delta > 0.05, f"(q={q_delta:.3f})")
check("p_CR = 2.7 冇唯一結構 (q_obs > 5%)", q_p_CR > 0.05, f"(q={q_p_CR:.3f})")

print("\n" + "=" * 74)
print("[4] 結論")
print("=" * 74)
print(f"""
  ★ 真實 AMS-02 質子譜指數 = {-slope_hard:.3f} ± {sm_hard:.3f} (R > 10 GV, 太陽調制以上)。
  ★ DSA 路線 (r = B = 4): p_inj = 2 = μ² —— 結構上乾淨, 但 r = 4 係普適強激波值,
    唔係 IDCM 獨有 ⟹ 🟡 弱結構。
  ★ 剩餘 δ = {delta:.3f} (傳播修正) 冇唯一 IDCM 結構 (q_obs = {q_delta:.3f})。
  ⟹ p_CR = 2.7 唔可以從 IDCM 結構推導: 佢 = (普適 DSA 注入 2) + (傳播 δ)。
    兩者都屬 CR 加速/傳播物理 (框架外), 同 script 11 嘅指數透明性定理一致。
""")
print(f"RESULT: {passed}/{total} PASS")

import json
with open(os.path.join(BASE, "data", "14_pcr_structure.json"), "w") as fh:
    json.dump({
        "p_CR_fit": -slope_hard, "sigma": sm_hard, "n_points": int(len(R)),
        "DSA_r_B4_p_inj": p_inj, "delta_propagation": delta,
        "q_obs_delta": q_delta, "q_obs_pcr": q_p_CR,
        "verdict": "p_CR = DSA(普適 2) + δ(無結構); 唔可由 IDCM 推導",
    }, fh, indent=1, ensure_ascii=False)
print("✅ data/14_pcr_structure.json")
if passed < total: exit(1)
