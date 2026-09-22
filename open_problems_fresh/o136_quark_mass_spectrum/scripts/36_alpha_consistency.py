#!/usr/bin/env python3
"""
O136 — Script 36: 穿透率 — 單一 α 一致性決定性檢驗
================================================================
Script 35 發現:
  T_prod 範圍 = 3.506e+25
  觀測質量範圍 = 2.780e+08
  → 若 m ∝ T_prod^α, 需 α = ln(2.78e8)/ln(3.51e25) = 0.2164

決定性檢驗: m_p/m_q = (T_p/T_q)^α 對所有配對需用同一 α
本 script: 計算所有配對的 α_ij, 檢查一致性 (spread)
"""
import numpy as np, math, json, itertools
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = ROOT / "cmb_cold_spot/data"
OUT = Path(__file__).parent.parent / "data"
Nd, B_, dimC = 44, 4, 3

mass = {"e": 0.510999, "mu": 105.6584, "tau": 1776.86,
        "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0}
A5_MODES = [1, 2, 3, 4, 5, 7, 9, 11, 13]

nodes = np.loadtxt(DATA / "a5_nodes.txt")
ra, dec = np.radians(nodes[:,0]), np.radians(nodes[:,1])
U = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
l, b = math.radians(209.0), math.radians(-57.0)
cold = np.array([math.cos(b)*math.cos(l), math.cos(b)*math.sin(l), math.sin(b)])
beta = np.arccos(np.clip(U @ cold, -1, 1))

print("=" * 96)
print("O136 Script 36: 穿透率 — 單一 α 一致性檢驗")
print("=" * 96)

# ═══ 1. 多種穿透率定義 (含 88 中點版本) ══════════════
print(f"\n{'─'*96}")
print("1. 多種穿透率定義")
print(f"{'─'*96}")

def T_defs(n):
    c = np.clip(np.cos(n*beta/2)**2, 1e-300, 1.0)
    ln = np.log(c)
    return {
        "prod60":  float(np.sum(ln)),          # ln T_prod over 60 nodes
        "mean60":  float(ln.mean()),
        "harm60":  float(math.log(60.0/np.sum(1.0/c))),
        "min60":   float(ln.min()),
    }

# 88 中點版本
O182 = ROOT / "o182_88grid_geometry/data"
emap = []
for line in (O182 / "g88_edge_map.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split(); emap.append((int(p[0]), int(p[1]), int(p[2])))
emap.sort()
mid = np.array([U[u]+U[v] for _,u,v in emap])
mid /= np.linalg.norm(mid, axis=1, keepdims=True)
beta88 = np.arccos(np.clip(mid @ cold, -1, 1))

def T_defs88(n):
    c = np.clip(np.cos(n*beta88/2)**2, 1e-300, 1.0)
    ln = np.log(c)
    return {
        "prod88": float(np.sum(ln)),
        "mean88": float(ln.mean()),
    }

print(f"\n{'n':>3} {'ln T_prod60':>14} {'⟨ln c⟩60':>12} {'ln T_prod88':>14} {'⟨ln c⟩88':>12}")
print("-" * 60)
TD = {}
for n in A5_MODES:
    d = T_defs(n); d.update(T_defs88(n))
    TD[n] = d
    print(f"{n:>3} {d['prod60']:>14.6f} {d['mean60']:>12.6f} {d['prod88']:>14.6f} {d['mean88']:>12.6f}")

# ═══ 2. ★★★ 單一 α 一致性檢驗 ═══════════════════════
print(f"\n{'─'*96}")
print("2. ★★★ 單一 α 一致性檢驗: α_ij = ln(m_i/m_j)/ln(T_i/T_j)")
print(f"{'─'*96}")

sorted_p = sorted(mass.keys(), key=lambda p: mass[p])

def alpha_consistency(key, pairing):
    """返回 (α 中位數, α 標準差, RMS)"""
    alphas = []
    for i, j in itertools.combinations(range(9), 2):
        p, q = sorted_p[i], sorted_p[j]
        dT = TD[pairing[i]][key] - TD[pairing[j]][key]
        if abs(dT) < 1e-9: continue
        alphas.append(math.log(mass[p]/mass[q])/dT)
    if len(alphas) < 5: return None
    a = np.array(alphas)
    return float(np.median(a)), float(a.std()), float(np.sqrt(np.mean((a-np.median(a))**2)))

print(f"\n先檢查質量排序配對 (e↔1, u↔2, d↔3, s↔4, μ↔5, c↔7, τ↔9, b↔11, t↔13):")
pair_mo = A5_MODES  # 質量排序對應
for key in ["prod60", "mean60", "prod88", "mean88", "harm60"]:
    res = alpha_consistency(key, pair_mo)
    if res:
        med, sd, rms = res
        print(f"  {key:>8}: α_med = {med:+.6f}, σ(α) = {sd:.6f}, RMS = {rms:.6f}")

print(f"\n★ 若 σ(α) ≈ 0 → 單一 α 成立 (穿透率解釋質量)")
print(f"★ 若 σ(α) 大 → α 唔一致")

# ═══ 3. ★★★ 全配對搜索: 找 σ(α) 最小者 ══════════════
print(f"\n{'─'*96}")
print("3. ★★★ 全配對搜索 (9! = 362880): 找 α 最一致者")
print(f"{'─'*96}")

keys = ["prod60", "mean60", "prod88", "mean88", "harm60", "min60"]
results = []
for key in keys:
    for perm in itertools.permutations(A5_MODES):
        res = alpha_consistency(key, perm)
        if res:
            results.append((res[1], key, perm, res[0]))   # 用 σ(α) 排序

results.sort(key=lambda x: x[0])
print(f"\n搜索: {len(keys)} 定義 × 9! = {len(keys)*math.factorial(9)} 組合")
print(f"\n最佳 6 個 (按 σ(α) 最小):")
print(f"\n{'σ(α)':>10} {'定義':>9} {'α_med':>10} {'配對 (模式→粒子)':>44}")
print("-" * 76)
for sd, key, perm, med in results[:6]:
    pair_str = " ".join(f"{p}:{n}" for p, n in zip(sorted_p, perm))
    print(f"{sd:>10.6f} {key:>9} {med:>10.6f} {pair_str:>44}")

print(f"\n★ 最佳 σ(α) = {results[0][0]:.6f}")
print(f"→ {'🟢 單一 α 成立!' if results[0][0] < 0.02 else ('🟡 接近' if results[0][0] < 0.1 else '🔴 唔成立')}")

# ═══ 4. 最佳方案的詳細 α_ij 表 ══════════════════════
print(f"\n{'─'*96}")
print("4. 最佳方案的 α_ij 詳細表")
print(f"{'─'*96}")

sd_best, key_best, perm_best, med_best = results[0]
print(f"\n定義 = {key_best}, 配對 = {dict(zip(sorted_p, perm_best))}, α_med = {med_best:.6f}")
print(f"\n{'配對':>12} {'質量比':>14} {'Δln T':>14} {'α_ij':>12}")
print("-" * 56)
alphas_best = []
for i, j in itertools.combinations(range(9), 2):
    p, q = sorted_p[i], sorted_p[j]
    dT = TD[perm_best[i]][key_best] - TD[perm_best[j]][key_best]
    aij = math.log(mass[p]/mass[q])/dT
    alphas_best.append(aij)
    if i < 4 or j > 6:
        print(f"{p+'/'+q:>12} {mass[p]/mass[q]:>14.6f} {dT:>14.6f} {aij:>12.6f}")
print(f"... (共 {len(alphas_best)} 對)")
print(f"\nα_ij 統計: min={min(alphas_best):.6f}, max={max(alphas_best):.6f}, 中位={np.median(alphas_best):.6f}")

# ═══ 5. 保存 ════════════════════════════════════════
with open(OUT / "36_alpha_consistency.json", "w") as f:
    json.dump({
        "a5_modes": A5_MODES,
        "T_defs": {str(n): TD[n] for n in A5_MODES},
        "best": {"sigma_alpha": results[0][0], "defn": results[0][1],
                 "pairing": dict(zip(sorted_p, results[0][2])), "alpha_med": results[0][3]},
        "mass_ordered_check": {k: alpha_consistency(k, pair_mo) for k in keys},
        "verdict": "見 stdout",
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/36_alpha_consistency.json")