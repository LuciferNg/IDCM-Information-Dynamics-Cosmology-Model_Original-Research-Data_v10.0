#!/usr/bin/python3
"""O239 — Script 03: 近/遠挫阻節點屬性分組（觀測 + 邊屬性層 signature）
============================================================================
scripts/01 已確立: 88 節點 → 最近挫阻距離 d_i（median 16.107°, MC null PASS, 離散帶）。
本 script 將 88 節點按 d_i split 近/遠（median 兩半），測三層屬性差異:

  E1 觀測層-CMB: 近/遠挫阻節點嘅 ⟨|δT|⟩/A（M1, SMICA 4.17°）差異
     （O182 docs/03 有 G88 vs G32frust 全組表, 但從未做 88 內部按挫阻距離 split）
  E2 觀測層-跨地圖: 同一 split 喺 Commander/SEVEM 4.17° 嘅 M1 差異（一致性）
  E3 邊屬性-端點挫阻負擔: 88 條透明邊嘅端點 (u,v) 喺 anchored_coloring 嘅
     frustration_neighbors 總和——近/遠挫阻節點（= 邊）組差異
  E4 邊屬性-短/長分類: 88 透明邊按 O223 docs/06 短(△,□)/長(⬠,□) 分類——
     近/遠挫阻組嘅短/長比例差異（挫阻扣減係咪改變透明邊長度分佈）

預註冊判據（permutation null, 10⁴ shuffle, α=0.5% 兩尾 = p<0.005 先算結構）:
  E1: |ΔM1_near-far| > perm 99.5th ⟹ CMB 溫度隨挫阻距離分組有結構差異
  E2: E1 顯著性喺 3 張圖至少 2 張一致（跨地圖 robust）
  E3: 端點挫阻負擔差 > perm 99.5th
  E4: 短/長比例差 > perm 99.5th
所有比較用同一固定 split（d_i > median = far; <= median = near）。
"""
import json, math
import numpy as np
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
O182 = ROOT / "o182_88grid_geometry/data"
CS   = ROOT / "cmb_cold_spot/data"
rng = np.random.default_rng(20261012)
N_PERM = 10000
ALPHA = 0.005

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

def sph(ra, dec):
    ra, dec = np.radians(ra), np.radians(dec)
    return np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])

# ── 讀挫阻距離（scripts/01 已算, 重用唔重算）──
d1 = json.load(open(Path(__file__).parent.parent / "data" / "01_frust_distance_field.json"))
d_i = np.array(d1["d_i"])
far = d_i > np.median(d_i)   # 44 個
near = ~far                  # 44 個
print(f"split: near={near.sum()} far={far.sum()} (d>median)")

# ── E1/E2: CMB 溫度 M1 ──
MAPS = ["SMICA", "Commander", "SEVEM"]
A = 134.2
def m1(T):
    T = np.asarray(T, float)
    dT = T - T.mean()
    return np.mean(np.abs(dT)) / A

def perm_test(stat_obs, group, X, nperm=N_PERM, seed=20261012):
    rr = np.random.default_rng(seed)
    cnt = 0
    for _ in range(nperm):
        g2 = rr.permutation(group)
        # 保持 split 大小, 重算 stat
        if callable(stat_obs):
            s = stat_obs(X[g2], X[~g2])
        else:
            s = None
        raise NotImplementedError
    return None

# 通用: diff of m1 between two groups
def diff_m1(grp, X):
    return m1(X[grp]) - m1(X[~grp])

results = {}
print("\n── E1/E2: 近/遠挫阻 CMB M1（SMICA/Commander/SEVEM @4.17°）──")
sig_maps = []
for name in MAPS:
    T = np.array(json.load(open(O182 / f"temps2_{name}_4.17deg.json"))["G88"], float)
    obs = diff_m1(near, T)
    rr = np.random.default_rng(hash(name) % (2**32))
    perm = np.empty(N_PERM)
    for k in range(N_PERM):
        g = rr.permutation(near)  # shuffle 標籤, 保持 44/44
        perm[k] = diff_m1(g, T)
    p_lo = np.percentile(perm, ALPHA*100)
    p_hi = np.percentile(perm, (1-ALPHA)*100)
    pval = min((perm >= obs).mean(), (perm <= obs).mean()) * 2
    sig = obs < p_lo or obs > p_hi
    results[name] = {"obs_m1_diff": float(obs), "perm99.5": float(p_hi),
                     "perm0.5": float(p_lo), "pval_2tail": float(pval)}
    print(f"  {name:>9}: ΔM1(near−far) = {obs:+.5f}  perm=[{p_lo:.5f},{p_hi:.5f}]  "
          f"p={pval:.4f}  {'★顯著' if sig else '—'}")
    if sig: sig_maps.append(name)
chk("E1 CMB M1 split 顯著（SMICA）", results["SMICA"]["obs_m1_diff"] < results["SMICA"]["perm0.5"]
    or results["SMICA"]["obs_m1_diff"] > results["SMICA"]["perm99.5"],
    f"ΔM1={results['SMICA']['obs_m1_diff']:+.5f}")
chk("E2 跨地圖一致性（≥2/3 圖同向顯著）",
    len(sig_maps) >= 2, f"顯著圖: {sig_maps}")

# ── E3: 端點挫阻負擔 ──
print("\n── E3: 88 透明邊端點 frustration_neighbors 總和 ──")
col = {}
for line in (CS / "anchored_coloring.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split()
    col[int(p[0])] = int(p[4])   # frustration_neighbors
edges = []
for line in (O182 / "g88_edge_map.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split()
    edges.append((int(p[0]), int(p[1]), int(p[2])))  # mid_idx, u, v
assert len(edges) == 88
burden = np.array([col[u] + col[v] for _, u, v in edges])
obs3 = burden[near].mean() - burden[far].mean()
rr = np.random.default_rng(20261012)
perm3 = np.empty(N_PERM)
for k in range(N_PERM):
    g = rr.permutation(near)
    perm3[k] = burden[g].mean() - burden[~g].mean()
p3lo, p3hi = np.percentile(perm3, [ALPHA*100, (1-ALPHA)*100])
sig3 = obs3 < p3lo or obs3 > p3hi
print(f"  端點挫阻負擔: near={burden[near].mean():.3f} far={burden[far].mean():.3f} "
      f"Δ={obs3:+.3f}  perm=[{p3lo:.3f},{p3hi:.3f}]  {'★' if sig3 else '—'}")
chk("E3 端點挫阻負擔 split 顯著", sig3, f"Δ={obs3:+.3f}")

# ── E4: 短/長邊分類 ──
print("\n── E4: 透明邊短/長分類（O223: (△,□)短 60/(⬠,□)長 60）──")
# O223 scripts/06 已分類: edge_classes = {(4,5):60(長), (3,4):60(短)} —— 但冇 per-edge 表。
# 用距離直接分類: 26.0913 短 vs 26.1664 長（間隙 0.0751 ≫ 0.0001 spread）
nodes = np.loadtxt(O182 / "g88_nodes.txt")
Vn = sph(nodes[:, 0], nodes[:, 1])
# 60 A5 節點重建邊長
a5 = np.loadtxt(CS / "a5_nodes.txt")
Va = sph(a5[:, 0], a5[:, 1])
Daa = np.degrees(np.arccos(np.clip(Va @ Va.T, -1, 1)))
elen = np.array([Daa[u, v] for _, u, v in edges])
short = elen < 26.13   # 短 26.0913 / 長 26.1664 中點
print(f"  透明邊短/長: short={short.sum()} long={(~short).sum()}（期望 88 全為 26.09/26.17 級）")
print(f"  近挫阻組: short={short[near].sum()}/{near.sum()}, "
      f"遠挫阻組: short={short[far].sum()}/{far.sum()}")
obs4 = short[near].mean() - short[far].mean()
rr = np.random.default_rng(20261012)
perm4 = np.empty(N_PERM)
for k in range(N_PERM):
    g = rr.permutation(near)
    perm4[k] = short[g].mean() - short[~g].mean()
p4lo, p4hi = np.percentile(perm4, [ALPHA*100, (1-ALPHA)*100])
sig4 = obs4 < p4lo or obs4 > p4hi
print(f"  Δshort ratio = {obs4:+.4f}  perm=[{p4lo:.4f},{p4hi:.4f}]  {'★' if sig4 else '—'}")
chk("E4 短/長比例 split 顯著", sig4, f"Δ={obs4:+.4f}")

out = {"E1_E2": results, "E3": {"obs": float(obs3), "perm99.5": float(p3hi),
        "perm0.5": float(p3lo), "near_mean": float(burden[near].mean()),
        "far_mean": float(burden[far].mean())},
       "E4": {"obs": float(obs4), "perm99.5": float(p4hi), "perm0.5": float(p4lo),
              "near_short": int(short[near].sum()), "near_n": int(near.sum()),
              "far_short": int(short[far].sum()), "far_n": int(far.sum()),
              "total_short": int(short.sum())},
       "split": {"near": int(near.sum()), "far": int(far.sum())}}
outfile = Path(__file__).parent.parent / "data" / "03_near_far_attributes.json"
outfile.parent.mkdir(parents=True, exist_ok=True)
with open(outfile, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

n_pass = sum(1 for _, c_, _ in checks if c_)
print(f"\nRESULT: {n_pass}/{len(checks)} checks passed")