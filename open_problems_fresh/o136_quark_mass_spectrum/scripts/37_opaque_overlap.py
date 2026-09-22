#!/usr/bin/env python3
"""
O136 — Script 37: 質量 = 阻挫(OPAQUE)通道重疊?
================================================================
物理圖像 (O182 + O7):
  88 邊 = TRANSPARENT (CMB 穿過唔改)  → 透明通道
  32 邊 = OPAQUE (同色阻挫)           → 拓撲位元/寫入通道
  O7: 阻挫邊 = Ising 翻轉位元, H = -56

★ 假設: 質量 = 模式對 OPAQUE 通道的重疊 (blockage)

檢驗量:
  P(n) = Σ over 88 透明中點 of cos²(nβ/2)   (透明重疊)
  O(n) = Σ over 32 阻挫中點 of cos²(nβ/2)   (阻挫重疊)
  候選: O, O/P, O/(O+P), P/O, ...
"""
import numpy as np, math, json, itertools
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = ROOT / "cmb_cold_spot/data"
O182 = ROOT / "o182_88grid_geometry/data"
OUT = Path(__file__).parent.parent / "data"
Nd, B_, dimC = 44, 4, 3

mass = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
A5_MODES = [1,2,3,4,5,7,9,11,13]

print("=" * 96)
print("O136 Script 37: 質量 = 阻挫(OPAQUE)通道重疊?")
print("=" * 96)

# ═══ 幾何 ═══════════════════════════════════════════
nodes = np.loadtxt(DATA / "a5_nodes.txt")
ra, dec = np.radians(nodes[:,0]), np.radians(nodes[:,1])
U = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
l, b = math.radians(209.0), math.radians(-57.0)
cold = np.array([math.cos(b)*math.cos(l), math.cos(b)*math.sin(l), math.sin(b)])

emap = []
for line in (O182 / "g88_edge_map.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split(); emap.append((int(p[0]), int(p[1]), int(p[2])))
emap.sort()
transp_mid = np.array([U[u]+U[v] for _,u,v in emap])
transp_mid /= np.linalg.norm(transp_mid, axis=1, keepdims=True)

fnodes = np.loadtxt(O182 / "g32_frustration_midpoints.txt")
f_mid = np.array([math.cos(math.radians(d2))*math.cos(math.radians(r2)) for r2, d2 in fnodes])
f_mid = np.column_stack([np.cos(np.radians(fnodes[:,1]))*np.cos(np.radians(fnodes[:,0])),
                          np.cos(np.radians(fnodes[:,1]))*np.sin(np.radians(fnodes[:,0])),
                          np.sin(np.radians(fnodes[:,1]))])
f_mid /= np.linalg.norm(f_mid, axis=1, keepdims=True)

beta_P = np.arccos(np.clip(transp_mid @ cold, -1, 1))
beta_O = np.arccos(np.clip(f_mid @ cold, -1, 1))

print(f"\n透明中點: {len(transp_mid)}, β ∈ [{np.degrees(beta_P).min():.2f}°, {np.degrees(beta_P).max():.2f}°]")
print(f"阻挫中點: {len(f_mid)}, β ∈ [{np.degrees(beta_O).min():.2f}°, {np.degrees(beta_O).max():.2f}°]")

# ═══ 重疊量 ═════════════════════════════════════════
def P(n): return float((np.cos(n*beta_P/2)**2).sum())
def O(n): return float((np.cos(n*beta_O/2)**2).sum())

print(f"\n{'─'*96}")
print("1. 透明/阻挫重疊")
print(f"{'─'*96}")
print(f"\n{'n':>3} {'P(n) 透明':>12} {'O(n) 阻挫':>12} {'O/P':>10} {'O/(O+P)':>10} {'ln(O/P)':>10}")
print("-" * 62)
D = {}
for n in A5_MODES:
    p_, o_ = P(n), O(n)
    D[n] = {"P": p_, "O": o_, "OP": o_/p_, "Of": o_/(o_+p_), "lnOP": math.log(o_/p_)}
    print(f"{n:>3} {p_:>12.6f} {o_:>12.6f} {o_/p_:>10.6f} {o_/(o_+p_):>10.6f} {math.log(o_/p_):>10.6f}")

# ═══ 2. ★ 單一 α 一致性檢驗 ══════════════════════════
print(f"\n{'─'*96}")
print("2. ★ 單一 α 一致性檢驗")
print(f"{'─'*96}")

sorted_p = sorted(mass, key=lambda p: mass[p])

def sig_alpha(key, pairing):
    al = []
    for i, j in itertools.combinations(range(9), 2):
        p, q = sorted_p[i], sorted_p[j]
        x = D[pairing[i]][key]; y = D[pairing[j]][key]
        if abs(x-y) < 1e-12: continue
        al.append(math.log(mass[p]/mass[q])/(x-y))
    if len(al) < 5: return None
    a = np.array(al)
    return float(a.std()), float(np.median(a))

keys = ["lnOP", "O", "P", "Of", "OP"]
print(f"\n質量排序配對 (e↔1,u↔2,d↔3,s↔4,μ↔5,c↔7,τ↔9,b↔11,t↔13):")
for k in keys:
    r = sig_alpha(k, A5_MODES)
    if r: print(f"  {k:>6}: σ(α) = {r[0]:.6f}, α_med = {r[1]:+.6f}")

# ═══ 3. ★★★ 全配對搜索 ═══════════════════════════════
print(f"\n{'─'*96}")
print("3. ★★★ 全配對搜索 (找 σ(α) 最小)")
print(f"{'─'*96}")

# 預計算
X = {k: np.array([D[n][k] for n in A5_MODES]) for k in keys}
LM = np.array([math.log(mass[p]) for p in sorted_p])
import itertools as it
M_IDX = np.arange(9)
# 預計算所有對的 ln mass 差
pairs_idx = list(it.combinations(range(9), 2))
lnm_diff = np.array([LM[i]-LM[j] for i,j in pairs_idx])

results = []
for k in keys:
    xv = X[k]
    # 對每個排列計算
    for perm in it.permutations(range(9)):
        xp = xv[list(perm)]
        d = np.array([xp[i]-xp[j] for i,j in pairs_idx])
        if np.abs(d).min() < 1e-12: continue
        al = lnm_diff/d
        sd = float(al.std())
        results.append((sd, k, perm, float(np.median(al))))

results.sort(key=lambda z: z[0])
print(f"\n搜索: {len(keys)} 量 × 9! = {len(keys)*math.factorial(9)} 組合")
print(f"\n最佳 6 個:")
print(f"\n{'σ(α)':>10} {'量':>7} {'α_med':>10} {'配對 (模式→粒子)':>44}")
print("-" * 76)
for sd, k, perm, med in results[:6]:
    ps = " ".join(f"{p}:{A5_MODES[i]}" for p, i in zip(sorted_p, perm))
    print(f"{sd:>10.6f} {k:>7} {med:>10.6f} {ps:>44}")

print(f"\n★ 最佳 σ(α) = {results[0][0]:.6f}")
print(f"→ {'🟢 單一 α 成立!' if results[0][0] < 0.02 else ('🟡 接近' if results[0][0] < 0.1 else '🔴 唔成立')}")

# ═══ 4. 保存 ════════════════════════════════════════
with open(OUT / "37_opaque_overlap.json", "w") as f:
    json.dump({
        "a5_modes": A5_MODES,
        "overlaps": {str(n): D[n] for n in A5_MODES},
        "best": {"sigma_alpha": results[0][0], "quantity": results[0][1],
                 "pairing": dict(zip(sorted_p, [A5_MODES[i] for i in results[0][2]])),
                 "alpha_med": results[0][3]},
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/37_opaque_overlap.json")