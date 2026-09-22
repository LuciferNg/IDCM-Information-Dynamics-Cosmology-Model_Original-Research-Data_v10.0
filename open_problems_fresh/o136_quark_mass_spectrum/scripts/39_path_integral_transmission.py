#!/usr/bin/env python3
"""
O136 — Script 39: 路徑積分穿透 (質量 = 穿透率 的最終形式)
================================================================
修正後基礎 (docs/22):
  a5_nodes 係 ICRS (RA, Dec)
  A₅ 節點 0 = 冷斑 (48.2999°, −20.4373°) = galactic (209°, −57°)
  88 透明邊 + 32 阻挫邊

物理圖像:
  模式 n 在網絡上傳播, 穿透 = 所有路徑的和 (path integral)
  Z(n) = Σ_paths Π_{e∈path} t_e(n)
  t_e(n) = 邊 e 的穿透振幅

候選 t_e(n):
  (a) cos²(n·β_m/2), β_m = 冷斑到邊中點的角距
  (b) cos²(n·θ_ij/2), θ_ij = 節點 i,j 的角距
  阻挫邊: t = 0 (障壁)

傳輸矩陣 M(n)_ij = t_ij(n)  (僅透明邊)
Z(n) 候選:
  Z1 = ln det(I − M)      (路徑和生成函數)
  Z2 = tr((I−M)^{-1})
  Z3 = λ_max(M)
  Z4 = Σ_ij [M^k]_ij  (k = 1,2,3,5)
"""
import numpy as np, math, json, itertools
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = ROOT / "cmb_cold_spot/data"
O182 = ROOT / "o182_88grid_geometry/data"
OUT = Path(__file__).parent.parent / "data"

mass = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
M9 = [1,2,3,4,5,7,9,11,13]
sp = sorted(mass, key=lambda p: mass[p])
LM = np.array([math.log(mass[p]) for p in sp])
pairs_idx = list(itertools.combinations(range(9), 2))
lmd = np.array([LM[i]-LM[j] for i,j in pairs_idx])

# ═══ 幾何 (正確 frame) ═══════════════════════════════
nodes = np.loadtxt(DATA / "a5_nodes.txt")
ra, dec = np.radians(nodes[:,0]), np.radians(nodes[:,1])
U = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
cold = U[0].copy()   # ★ 節點 0 = 冷斑 (docs/22)
print("=" * 96)
print("O136 Script 39: 路徑積分穿透")
print("=" * 96)
print(f"\n★ frame: a5_nodes = ICRS; 節點 0 = 冷斑 = {np.round(nodes[0],4)}")

# 透明邊
emap = []
for line in (O182 / "g88_edge_map.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split(); emap.append((int(p[0]), int(p[1]), int(p[2])))
emap.sort()
transp_edges = [(u,v) for _,u,v in emap]

# 全 120 邊 + 著色
col = {}
for line in (DATA / "anchored_coloring.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split(); col[int(p[0])] = int(p[3])
color = np.array([col[i] for i in range(60)])
dist = np.arccos(np.clip(U @ U.T, -1, 1))
all_edges = [(i,j) for i in range(60) for j in range(i+1,60) if dist[i,j] < np.radians(28.0)]
frust_edges = [(i,j) for i,j in all_edges if color[i]==color[j]]
print(f"邊: 全 {len(all_edges)}, 透明 {len(transp_edges)}, 阻挫 {len(frust_edges)}")

# 邊中點 β
beta_mid = {}
for u,v in all_edges:
    m = U[u]+U[v]; m /= np.linalg.norm(m)
    beta_mid[(u,v)] = math.acos(np.clip(float(m @ cold), -1, 1))

# ═══ 傳輸矩陣 ═══════════════════════════════════════
def build_M(n, mode="mid"):
    M = np.zeros((60,60))
    for u,v in transp_edges:
        if mode == "mid":
            t = math.cos(n*beta_mid[(u,v)]/2)**2
        else:
            t = math.cos(n*dist[u,v]/2)**2
        M[u,v] = t; M[v,u] = t
    return M

def Z_vals(n, mode="mid"):
    Mx = build_M(n, mode)
    out = {}
    out["trM"] = float(np.trace(Mx))
    ev = np.linalg.eigvalsh(Mx)
    out["lmax"] = float(ev.max())
    # (I - M) 路徑和
    I = np.eye(60)
    A = I - Mx
    sgn, logdet = np.linalg.slogdet(A)
    out["logdet"] = float(logdet) if sgn > 0 else float('nan')
    try:
        out["trinv"] = float(np.trace(np.linalg.inv(A)))
    except Exception:
        out["trinv"] = float('nan')
    for k in [1,2,3,5,10]:
        Mk = np.linalg.matrix_power(Mx, k)
        out[f"sumM{k}"] = float(Mk.sum())
    return out

print(f"\n{'─'*96}")
print("1. 各種路徑和量")
print(f"{'─'*96}")

Z = {}
keys = None
for n in M9:
    Z[n] = Z_vals(n, "mid")
    if keys is None: keys = list(Z[n].keys())

print(f"\n{'n':>3} " + " ".join(f"{k:>12}" for k in keys))
print("-" * (4 + 13*len(keys)))
for n in M9:
    print(f"{n:>3} " + " ".join(f"{Z[n][k]:>12.6f}" if abs(Z[n][k]) < 1e6 else f"{Z[n][k]:>12.3e}" for k in keys))

# ═══ 2. σ(α) 檢驗 ═══════════════════════════════════
print(f"\n{'─'*96}")
print("2. ★ σ(α) 檢驗 (單調配對)")
print(f"{'─'*96}")

def sig(vals):
    v = np.array(vals)
    order = np.argsort(v); vp = v[order]
    d = np.array([vp[i]-vp[j] for i,j in pairs_idx])
    if np.abs(d).min() < 1e-12: return None, None
    al = lmd/d
    return float(al.std()), float(np.median(al))

print(f"\n{'量':>12} {'σ(α)':>12} {'α_med':>12} {'判定':>8}")
print("-" * 48)
scores = []
for k in keys:
    vals = [Z[n][k] for n in M9]
    if any(math.isnan(x) or math.isinf(x) for x in vals): 
        print(f"{k:>12} {'NaN/inf':>12}"); continue
    sd, med = sig(vals)
    if sd is None: continue
    v = '🟢' if sd < 0.02 else ('🟡' if sd < 0.1 else '🔴')
    scores.append((sd, k, med))
    print(f"{k:>12} {sd:>12.6f} {med:>12.6f} {v:>8}")

print(f"\n★ 對照: 純 sin(nπ/88) σ(α) = 15.0871")
print(f"★ 對照: 逐節點連乘 Σln cos² σ(α) = 1.0288 (正確 frame)")

scores.sort()
print(f"\n★ 最佳: {scores[0][1]}, σ(α) = {scores[0][0]:.6f}")
print(f"→ {'🟢 穿透率解釋質量!' if scores[0][0] < 0.02 else ('🟡 接近' if scores[0][0] < 0.1 else '🔴 唔解釋')}")

# ═══ 3. ★★ 全配對搜索 (最佳量) ══════════════════════
print(f"\n{'─'*96}")
print("3. ★★ 全配對搜索 (最佳量)")
print(f"{'─'*96}")

bk = scores[0][1]
bv = np.array([Z[n][bk] for n in M9])
res = []
for perm in itertools.permutations(range(9)):
    vp = bv[list(perm)]
    d = np.array([vp[i]-vp[j] for i,j in pairs_idx])
    if np.abs(d).min() < 1e-12: continue
    al = lmd/d
    res.append((float(al.std()), perm, float(np.median(al))))
res.sort(key=lambda z: z[0])
print(f"\n量 = {bk}, 搜索 9! = {math.factorial(9)}")
print(f"\n最佳 5 個:")
print(f"\n{'σ(α)':>10} {'配對 (模式→粒子)':>46} {'α_med':>10}")
print("-" * 70)
for sd, perm, med in res[:5]:
    ps = " ".join(f"{p}:{M9[i]}" for p, i in zip(sp, perm))
    print(f"{sd:>10.6f} {ps:>46} {med:>10.6f}")

print(f"\n★ 最佳 σ(α) = {res[0][0]:.6f}")

# ═══ 4. 保存 ════════════════════════════════════════
with open(OUT / "39_path_integral_transmission.json", "w") as f:
    json.dump({
        "frame": "a5_nodes = ICRS, node0 = cold spot",
        "Z_values": {str(n): {k: (None if math.isnan(v) or math.isinf(v) else v) for k,v in Z[n].items()} for n in M9},
        "sigma_alpha": {k: s for s, k, m in scores},
        "best": {"quantity": scores[0][1], "sigma": scores[0][0],
                 "best_pairing_sigma": res[0][0],
                 "best_pairing": dict(zip(sp, [M9[i] for i in res[0][1]])), "alpha_med": res[0][2]},
        "reference": {"sin": 15.0871, "per_node_product": 1.0288},
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/39_path_integral_transmission.json")