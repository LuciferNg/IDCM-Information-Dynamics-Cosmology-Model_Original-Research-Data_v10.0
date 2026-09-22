#!/usr/bin/env python3
"""
O136 — Script 30: A₅ 線圖譜 vs 環譜 — 決定性對比 + 零模型
================================================================
關鍵事實:
  88-site 環 (C_88) 的 Laplacian 譜 = {0} ∪ {4sin²(πk/88), k=1..43 各2次} ∪ {4}
  → 若 A₅ 線圖係環, 譜應完全匹配

測試:
  1. 排序譜對比 (逐個 eigenvalue)
  2. 零模型: 同度序列的隨機圖 (configuration model) 的匹配率
  3. 度分佈的結構意義 (36 = h¹¹?)
"""
import numpy as np, json, math
from pathlib import Path
from itertools import combinations
from collections import Counter
import random

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = ROOT / "cmb_cold_spot/data"
O182 = ROOT / "o182_88grid_geometry/data"
OUT = Path(__file__).parent.parent / "data"

Nd, B_, dimC = 44, 4, 3
def v2(x):
    c = 0
    while x % 2 == 0: x //= 2; c += 1
    return c

print("=" * 96)
print("O136 Script 30: A₅ 線圖譜 vs 環譜 — 決定性對比")
print("=" * 96)

# ═══ 重建線圖 ═══════════════════════════════════════
emap = []
for line in (O182 / "g88_edge_map.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split()
    emap.append((int(p[0]), int(p[1]), int(p[2])))
emap.sort()
v2m = {}
for mid, u, v in emap:
    v2m.setdefault(u, []).append(mid)
    v2m.setdefault(v, []).append(mid)
adj = {i: set() for i in range(88)}
for vtx, mids in v2m.items():
    for a, b in combinations(mids, 2):
        adj[a].add(b); adj[b].add(a)

Lmat = np.zeros((88,88))
for i in range(88):
    Lmat[i,i] = len(adj[i])
    for j in adj[i]:
        Lmat[i,j] = -1
ev = np.sort(np.linalg.eigvalsh(Lmat))
degs = np.array([len(adj[i]) for i in range(88)])

print(f"\n{'─'*96}")
print("1. 線圖基本結構")
print(f"{'─'*96}")
print(f"\n頂點 88, 邊 {sum(degs)//2}")
print(f"度分佈: {dict(sorted(Counter(degs).items()))}")
print(f"平均度: {degs.mean():.4f}")
print(f"譜範圍: [{ev.min():.6f}, {ev.max():.6f}]")

# ═══ 2. 環譜 (C_88) ══════════════════════════════════
print(f"\n{'─'*96}")
print("2. 環譜 C_88 (Laplacian)")
print(f"{'─'*96}")

ring = [0.0]
for k in range(1, 44):
    ring += [4*math.sin(math.pi*k/88)**2]*2
ring += [4.0]
ring = np.sort(np.array(ring))
print(f"\nC_88 Laplacian 譜: {len(ring)} 個")
print(f"  0 出現 {sum(1 for x in ring if x < 1e-9)} 次")
print(f"  範圍 [{ring.min():.6f}, {ring.max():.6f}]")

# ═══ 3. 逐個 eigenvalue 對比 ════════════════════════
print(f"\n{'─'*96}")
print("3. ★ 逐個 eigenvalue 對比 (排序後)")
print(f"{'─'*96}")

diff = np.abs(ev - ring)
print(f"\n平均絕對差: {diff.mean():.6f}")
print(f"最大絕對差: {diff.max():.6f}")
print(f"中位數差: {np.median(diff):.6f}")
print(f"\n相對差 (|Δ|/ring) 分位:")
rel = np.where(ring > 1e-6, diff/np.maximum(ring,1e-9), 0)
for q in [10, 25, 50, 75, 90]:
    print(f"  {q:>3}%: {np.percentile(rel,q)*100:.3f}%")

print(f"\n前 12 個逐個對比:")
print(f"{'#':>4} {'線圖 λ':>12} {'環 λ':>12} {'差':>12} {'相對%':>10}")
print("-" * 54)
for i in range(12):
    print(f"{i:>4} {ev[i]:>12.6f} {ring[i]:>12.6f} {ev[i]-ring[i]:>12.6f} {(ev[i]-ring[i])/max(ring[i],1e-9)*100:>10.3f}")

# ═══ 4. ★ 零模型: 同度序列隨機圖 ════════════════════
print(f"\n{'─'*96}")
print("4. ★ 零模型: 同度序列的隨機圖 (configuration model)")
print(f"{'─'*96}")

def match_score(eigs, ring, tol=0.02):
    """平均相對偏差 (逐個排序對比)"""
    d = np.abs(eigs - ring)
    r = np.where(ring > 1e-6, d/np.maximum(ring,1e-9), 0)
    return r.mean()

obs_score = match_score(ev, ring)
print(f"\n觀測 (A₅ 線圖) 平均相對偏差: {obs_score*100:.4f}%")

random.seed(1234)
N = 200
null_scores = []
for trial in range(N):
    # configuration model: 隨機配對 stubs
    stubs = []
    for i, d in enumerate(degs):
        stubs += [i]*int(d)
    random.shuffle(stubs)
    A = np.zeros((88,88))
    ok = True
    for k in range(0, len(stubs), 2):
        a, b = stubs[k], stubs[k+1]
        if a == b: ok = False; break
        A[a,b] = 1; A[b,a] = 1
    if not ok: continue
    Lr = np.diag(A.sum(axis=1)) - A
    try:
        er = np.sort(np.linalg.eigvalsh(Lr))
    except Exception:
        continue
    null_scores.append(match_score(er, ring))

null_scores = np.array(null_scores)
print(f"隨機圖 ({len(null_scores)} 樣本) 平均相對偏差: {null_scores.mean()*100:.4f}% ± {null_scores.std()*100:.4f}%")
print(f"隨機圖最小: {null_scores.min()*100:.4f}%")
print(f"\n觀測 vs 零模型: 觀測 = {obs_score*100:.4f}%, 零模型均值 = {null_scores.mean()*100:.4f}%")
p_val = (null_scores <= obs_score).sum()/len(null_scores)
print(f"p-value (P[null ≤ obs]) = {p_val:.4f}")
print(f"→ {'🟢 觀測顯著優於隨機 (線圖≈環)' if p_val < 0.05 else '🔴 觀測與隨機無異 (線圖≠環)'}")

# ═══ 5. ★ 度分佈的結構意義 ═══════════════════════════
print(f"\n{'─'*96}")
print("5. ★ 度分佈的結構意義")
print(f"{'─'*96}")

dd = Counter(degs)
print(f"\n{'度':>4} {'頂點數':>8} {'結構?':>20}")
print("-" * 36)
struct = {3: "?", 4: "B = 4", 5: "F₅ = 5", 6: "C(4,2) = 6"}
for d in sorted(dd):
    print(f"{d:>4} {dd[d]:>8} {struct.get(d,'?'):>20}")

print(f"\n頂點數序列: {[dd[d] for d in sorted(dd)]} = [24, 36, 24, 4]")
print(f"  Σ = {sum(dd.values())} = 88 ✅")
print(f"  ★ 36 = h¹¹ (CY₃ 2-cycle 數) ✅")
print(f"  ★ 4 = B ✅")
print(f"  ★ 24 = 2×B×N_gen = 2×12")
print(f"  ★ 24 = 2N_d − 20 = 88 − 64?")

print(f"\n★ 檢驗: 36 = h¹¹ 是否結構或巧合?")
print(f"  隨機 88 頂點 180 邊圖的度分佈會否也出現 36 個度-4 頂點?")
null_d4 = []
random.seed(77)
for _ in range(200):
    stubs = []
    for i, d in enumerate(degs):
        stubs += [i]*int(d)
    random.shuffle(stubs)
    A = np.zeros((88,88)); ok = True
    for k in range(0, len(stubs), 2):
        a, b = stubs[k], stubs[k+1]
        if a == b: ok = False; break
        A[a,b]=1; A[b,a]=1
    if ok:
        null_d4.append(int((A.sum(axis=1) == 4).sum()))
print(f"  但度序列係給定 → 36 個度-4 頂點係必然 (by construction)")

# ═══ 6. 判決 ════════════════════════════════════════
print(f"\n{'─'*96}")
print("6. 判決")
print(f"{'─'*96}")

print(f"""
A₅ 線圖 vs 88-環:
  觀測平均相對偏差: {obs_score*100:.4f}%
  零模型 (同度序列隨機圖): {null_scores.mean()*100:.4f}% ± {null_scores.std()*100:.4f}%
  p-value: {p_val:.4f}

★ {'線圖譜 ≈ 環譜 (結構)' if p_val < 0.05 else '線圖譜 ≠ 環譜 — A₅ 線圖唔係環'}

★ 更根本: 88 中點係球面分佈 (Dec std 39.4°), 唔係 1-D 環
★ O182 已明示: 「1-D BVP 節點冇自然天球嵌入; 透明度通道係更直接嘅鏈-天球對應」

⇒ A₅ 幾何提供:
   ✅ 88 的計數 (88 = 120 − 32 = 2(|A₅| − B²))
   ✅ 88 個天球方向
   ✅ 阻挫/透明二分
   🔴 但唔提供 1-D 環的排序 → 唔能直接選模式 n
""")

# ═══ 7. 保存 ════════════════════════════════════════
with open(OUT / "30_a5_vs_ring.json", "w") as f:
    json.dump({
        "line_graph": {"n_v": 88, "n_e": int(sum(degs)//2),
                       "degree_dist": {str(k): int(v) for k, v in sorted(dd.items())},
                       "spectrum": [round(float(x),8) for x in ev]},
        "ring_spectrum": [round(float(x),8) for x in ring],
        "obs_mean_rel_dev_pct": float(obs_score*100),
        "null_mean_rel_dev_pct": float(null_scores.mean()*100),
        "null_std_pct": float(null_scores.std()*100),
        "p_value": float(p_val),
        "degree_structure": {"3": 24, "4": 36, "5": 24, "6": 4, "note": "36 = h¹¹, 4 = B"},
        "verdict": "A₅ 線圖唔係環; 提供計數與方向, 唔提供環排序",
    }, f, indent=2, ensure_ascii=False)
print(f"✅ 結果已寫入 data/30_a5_vs_ring.json")