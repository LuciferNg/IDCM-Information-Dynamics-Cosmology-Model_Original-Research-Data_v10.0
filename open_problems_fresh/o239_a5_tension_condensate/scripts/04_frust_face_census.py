#!/usr/bin/python3
"""O239 — Script 04: 挫阻扣減面型 census（邊層 signature 正式鎖定）
============================================================================
scripts/01-03 觀察（P1 幾何層）:
  a) 挫阻距離場 d_i 離散 6 帶, unique 45 << MC 88（scripts/02 D1-D5 全 PASS）
  b) 帶 13.306°×40 = 短邊 40 條完美對應（scripts/03 E4 觀察: 短邊全入近挫阻組）
  c) 帶分佈: 13.306°×40 / 16.107°×20 / 21.674°×12 / 24.395°×10 / 26.048°×2 / 29.353°×4

本 script 將觀察鎖定為結構定理，用 O223 方法重建面型:
  F1 重建面 tracing（O223 scripts/04 Q2 方法）→ F = 62 = 20△ + 30□ + 12⬠
  F2 120 邊全部分類: 兩側面型 (3,3)/(3,4)/(4,4)/(4,5)/(5,5)/(3,5) census
     （O223 docs/06 已證只有 (3,4) 短 60 + (4,5) 長 60 —— 重現）
  F3 32 挫阻邊兩側面型 census: 期望 = 20 條 (△,□) 短 + 12 條 (⬠,□) 長
     （O223 docs/03: 32 挫阻 ↔ 32 奇面 bijection = 20△ + 12⬠）
  F4 88 透明邊兩側面型 census: 期望 = 40 短 (△,□) + 48 長 (⬠,□)（=120−32嘅 corollary）
  F5 ★挫阻距離帶 ↔ 邊分類: 帶 13.306° 嘅 40 條 = 40 條短透明邊（0 overlap, 完美二分）
     —— 用 permutation null 檢定(保持短/長 40/48, shuffle 短標籤 10⁴次,
     「短邊喺 13.306° 帶」命中數 obs=40 vs perm 分佈)
  F6 挫阻中點 idx ↔ 挫阻邊面型: 13.306° 帶嘅 20 個 frust idx（scripts/02 觀察
     = 20 idx × 2 nodes）係咪啱好 = 20 個△-挫阻中點？（若係: 13.306° 帶 = 「同面型
     家族嘅磨邊-挫阻距離」, 帶簡併 40 = 20△-挫阻 × 2 條短邊）

盲測紀律: F1-F4 係重現已知定理（O223）——sanity; F5 判據跑前凍結 (命中數=40);
F6 只記錄對應關係, 唔宣稱機制。
"""
import os, math, json
import numpy as np
from collections import Counter
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
O182 = ROOT / "o182_88grid_geometry/data"
CS   = ROOT / "cmb_cold_spot/data"
rng = np.random.default_rng(20261012)
N_PERM = 10000

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

def sph(ra, dec):
    ra, dec = np.radians(ra), np.radians(dec)
    return np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])

# ── A5 60 節點 + 120 邊重建 ──
a5 = np.loadtxt(CS / "a5_nodes.txt")
Va = sph(a5[:, 0], a5[:, 1])
Daa = np.degrees(np.arccos(np.clip(Va @ Va.T, -1, 1)))
dss = np.sort(Daa[np.triu_indices(60, 1)]); thr = (dss[119] + dss[120]) / 2
A = (Daa < thr); np.fill_diagonal(A, False)
nbr = {i: [int(j) for j in np.where(A[i])[0]] for i in range(60)}
Eset = frozenset((min(i,j), max(i,j)) for i in range(60) for j in nbr[i])
assert len(Eset) == 120

# 著色（阻挫 = 同色邊）
col = {}
for line in (CS / "anchored_coloring.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split(); col[int(p[0])] = int(p[3])
def is_frust(u, v): return col[u] == col[v]

# ── 旋轉系統 + 面 tracing（O223 scripts/04 Q1-Q6 方法）──
rot = {}
for v in range(60):
    n = Va[v]
    e1 = Va[nbr[v][0]] - n * (Va[nbr[v][0]] @ n); e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    order = []
    for w in nbr[v]:
        d = Va[w] - n * (Va[w] @ n)
        order.append((math.atan2(d @ e2, d @ e1), w))
    order.sort()
    rot[v] = [w for _, w in order]
def next_dir(u, v):
    i = rot[v].index(u)
    return v, rot[v][(i - 1) % len(rot[v])]
visited = set(); faces = []
for u in range(60):
    for v in nbr[u]:
        if (u, v) in visited: continue
        f = []; cu, cv = u, v
        while (cu, cv) not in visited:
            visited.add((cu, cv)); f.append(cu)
            cu, cv = next_dir(cu, cv)
            if len(f) > 100: break
        if f: faces.append(f)
sizes = Counter(len(f) for f in faces)
F = len(faces)
print(f"F1 面 tracing: F={F}, sizes={dict(sorted(sizes.items()))}, chi={60-120+F}")
chk("F1 F=62 = 20△+30□+12⬠", F == 62 and sizes[3] == 20 and sizes[4] == 30 and sizes[5] == 12,
    str(dict(sorted(sizes.items()))))

# 每條邊兩側面型: face set => 邊→面型對
def face_edges(f):
    return [frozenset((f[i], f[(i+1) % len(f)])) for i in range(len(f))]
edge_faces = {}
for f in faces:
    for e in face_edges(f):
        edge_faces.setdefault(e, []).append(len(f))
assert all(len(v) == 2 for v in edge_faces.values()), "每邊兩側面"

def eclass(u, v):
    return tuple(sorted(edge_faces[frozenset((u, v))]))

# F2: 120 邊面型 census
c120 = Counter(eclass(u, v) for (u, v) in Eset)
print(f"\nF2 120 邊兩側面型: {dict(sorted(c120.items()))}")
chk("F2 (3,4)=60 短 + (4,5)=60 長（重現 O223 docs/06）",
    c120[(3, 4)] == 60 and c120[(4, 5)] == 60, str(dict(sorted(c120.items()))))

# F3: 32 挫阻邊面型
frust_edges = [(u, v) for (u, v) in Eset if is_frust(u, v)]
cf = Counter(eclass(u, v) for (u, v) in frust_edges)
print(f"\nF3 32 挫阻邊: {dict(sorted(cf.items()))}  (expect (3,4):20 + (4,5):12)")
chk("F3 挫阻 = 20(△,□)短 + 12(⬠,□)長", cf[(3, 4)] == 20 and cf[(4, 5)] == 12,
    str(dict(sorted(cf.items()))))

# F4: 88 透明邊面型
norm_edges = [(u, v) for (u, v) in Eset if not is_frust(u, v)]
cn = Counter(eclass(u, v) for (u, v) in norm_edges)
print(f"\nF4 88 透明邊: {dict(sorted(cn.items()))}  (expect (3,4):40 + (4,5):48)")
chk("F4 透明 = 40(△,□)短 + 48(⬠,□)長（=120−32 corollary）",
    cn[(3, 4)] == 40 and cn[(4, 5)] == 48, str(dict(sorted(cn.items()))))

# ── F5: 挫阻距離帶 ↔ 短透明邊 ──
d1 = json.load(open(Path(__file__).parent.parent / "data" / "01_frust_distance_field.json"))
d_i = np.array(d1["d_i"])
# 讀 transparent edge map（mid_idx → u,v）配序同 g88_nodes 一致
edges = []
for line in (O182 / "g88_edge_map.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split(); edges.append((int(p[0]), int(p[1]), int(p[2])))
elen = np.array([Daa[u, v] for _, u, v in edges])
short = elen < 26.13          # 短 26.0913 / 長 26.1664
band13 = np.round(d_i, 2) == 13.31
n_hit = int((band13 & short).sum())
n_band = int(band13.sum()); n_short = int(short.sum())
print(f"\nF5 13.306° 帶 ∩ 短邊: {n_hit} (帶 {n_band} 條, 短邊 {n_short} 條)")
# permutation null: shuffle 短標籤, 統計「13.306° 帶內短邊數」
perm_hits = np.empty(N_PERM)
for k in range(N_PERM):
    s = rng.permutation(short)
    perm_hits[k] = (band13 & s).sum()
plo, phi = np.percentile(perm_hits, [0.5, 99.5])
print(f"  perm(10⁴): mean={perm_hits.mean():.3f} 99.5th={phi:.1f}  obs={n_hit}")
chk("F5 短邊=13.306°帶 完美二分 (obs 命中 > perm 99.5th)", n_hit > phi,
    f"obs={n_hit} vs perm99.5={phi:.1f}")
chk("F5b 帶內全短 (no long in band)", n_hit == n_band,
    f"hit={n_hit} band={n_band}")

# ── F6: 13.306° 帶 frust idx vs △-挫阻中點 ──
# 挫阻中點 = frust 邊 (u,v) 中點; 面型 (3,4) 嘅 frust 邊 = 20 △-挫阻
# O182 scripts/01 順序 = edges (i,j) ascending -> frust filter; 同 g32 檔順序一致
edges_asc = [(i, j) for i in range(60) for j in range(i + 1, 60) if (min(i, j), max(i, j)) in Eset]
frust_asc = [(u, v) for (u, v) in edges_asc if is_frust(u, v)]
assert len(frust_asc) == 32
frust_mid = {}
for u, v in frust_asc:
    m = (Va[u] + Va[v]); m /= np.linalg.norm(m)
    ra = np.degrees(np.arctan2(m[1], m[0])) % 360
    dec = np.degrees(np.arcsin(m[2]))
    frust_mid[(round(ra, 4), round(dec, 4))] = eclass(u, v)
# g32 挫阻中點檔（O182 4dp）對應面型
gf = np.loadtxt(O182 / "g32_frustration_midpoints.txt")
gf_keys = [(round(a, 4), round(b, 4)) for a, b in gf]
gf_cls = [frust_mid[k] for k in gf_keys]
gf_cls_arr = np.array([1 if c == (3, 4) else 0 for c in gf_cls])  # 1 = △-挫阻(短)
# scripts/02 觀察: 13.306° 帶嘅 frust idx = {20 個 idx × 2 nodes}
# 每 node 最近挫阻 idx
Vn = sph(np.loadtxt(O182 / "g88_nodes.txt")[:, 0], np.loadtxt(O182 / "g88_nodes.txt")[:, 1])
Vf = sph(gf[:, 0], gf[:, 1])
D = np.degrees(np.arccos(np.clip(Vn @ Vf.T, -1, 1)))
nn_idx = D.argmin(axis=1)
band_idx = set(nn_idx[band13])
band_cls = set(gf_cls_arr[list(band_idx)])
print(f"\nF6 13.306° 帶最近挫阻 idx: {len(band_idx)} 個, 面型類別: {sorted(gf_cls_arr[list(band_idx)].tolist())}")
print(f"     全部 32 挫阻面型: △(短) x{gf_cls_arr.sum()}, ⬠(長) x{(~gf_cls_arr.astype(bool)).sum()}")
chk("F6 13.306°帶挫阻 = 啱好 20 個△-挫阻", len(band_idx) == 20 and gf_cls_arr[list(band_idx)].sum() == 20,
    f"idx={len(band_idx)}, 其中△={gf_cls_arr[list(band_idx)].sum()}")

out = {
    "F1_faces": dict(sorted(sizes.items())), "F": F, "chi": 60 - 120 + F,
    "F2_all120": {f"{k[0]},{k[1]}": v for k, v in sorted(c120.items())},
    "F3_frust32": {f"{k[0]},{k[1]}": v for k, v in sorted(cf.items())},
    "F4_transparent88": {f"{k[0]},{k[1]}": v for k, v in sorted(cn.items())},
    "F5": {"band13_hits": n_hit, "band_n": n_band, "short_n": n_short,
           "perm_mean": float(perm_hits.mean()), "perm99.5": float(phi)},
    "F6": {"n_band_frust_idx": len(band_idx), "tri_frust_idx": int(gf_cls_arr[list(band_idx)].sum()),
           "total_tri_frust": int(gf_cls_arr.sum())},
}
outfile = Path(__file__).parent.parent / "data" / "04_frust_face_census.json"
outfile.parent.mkdir(parents=True, exist_ok=True)
with open(outfile, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

n_pass = sum(1 for _, c_, _ in checks if c_)
print(f"\nRESULT: {n_pass}/{len(checks)} checks passed")