#!/usr/bin/env python3
"""
21_falsification_test.py — O26: 證偽測試 (最嚴格)
=====================================================
核心問題: O26 嘅物理主張有冇真正嘅可證偽性?

分類:
A. 數學定理 (恆真, 唔需要證偽): 對徑=右乘r₀, k不變量, 三角形匹配
B. 物理主張 (需要證偽):
   B1: k↔溫度分層 (k=0 極端, k=2 平穩, p=0.024)
   B2: ΔE=0 對徑對 |ΔT| 細 (p=0.030 原始, 0.071 去背景)
   B3: 冷斑 = k=0 零散射通道
   B4: 對徑軸 Dec=18° B-mode 對齊 (O26-G1)

測試方法:
1. Train/test split: 30 節點擬合, 30 節點驗證 (真正證偽!)
2. Bonferroni 多重比較校正
3. NILC/Commander 獨立交叉驗證 (已做, 再確認)
4. 對徑相關 r 嘅 bootstrap CI
5. Permutation 檢驗: k↔|T| 關聯係咪 robust
"""
import numpy as np
import math
import os
from collections import defaultdict, deque, Counter
from scipy import stats

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
OUT = f"{BASE}/o26_node57_region/data"

# ============ 讀取數據 ============
# 節點座標
nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)

# 溫度 (SMICA 4.17)
T = {}
with open(f"{BASE}/o3_node_temperatures/data/node_temps.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split()
        T[int(p[0])] = float(p[2])
T_arr = np.array([T[i] for i in range(60)])

# k 值 (anchored_coloring 最後一欄)
k = []
with open(f"{BASE}/cmb_cold_spot/data/anchored_coloring.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split()
        k.append(int(p[-1]))
k = np.array(k)

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line, flush=True)
    results.append(line)

log("=" * 72)
log("O26: 證偽測試 — 物理主張嘅可證偽性")
log("=" * 72)

# ============ A. 數學定理分類 ============
log("\n=== A. 數學定理 (恆真, 唔需要證偽) ===")
log("""
1. 對徑映射 = 右乘 r₀ (ε=5.34° 常數): 由節點座標定義, 60/60 驗證
   → 唔係宇宙學主張, 係幾何事實。任何框架 (暴脹/靜態) 都要接受。
2. k 分佈 {0:8,1:40,2:12} = 圖不變量: 5000 random anchor 全同
   → 圖論必然, 冇得證偽 (亦唔需要)。
3. 20 三角形 = 完美 3-匹配: 圖結構事實
   → 同上。
""")

# ============ B1. k↔溫度分層 train/test split ============
log("=" * 72)
log("B1. k↔溫度分層 — Train/Test Split (真正證偽)")
log("=" * 72)

# 對徑對 (30 對) — 用對徑對做 split (每對一個 train 一個 test)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
def antip(x):
    best = None; ba = 1e9
    for y in range(60):
        if y == x: continue
        dd = math.degrees(math.acos(np.clip(np.dot(vecs[x], vecs[y]), -1, 1)))
        if dd > 170 and dd < ba:
            ba = dd; best = y
    return best
pairs = []
used = set()
for i in range(60):
    if i in used: continue
    j = antip(i)
    pairs.append((i, j))
    used.add(i); used.add(j)
log(f"  對徑對: {len(pairs)}")

rng = np.random.default_rng(42)
N_SPLIT = 1000
split_results = []
for trial in range(N_SPLIT):
    train_idx = []
    test_idx = []
    for i, j in pairs:
        if rng.random() < 0.5:
            train_idx.append(i); test_idx.append(j)
        else:
            train_idx.append(j); test_idx.append(i)
    train_idx = np.array(train_idx)
    test_idx = np.array(test_idx)
    # Train: k=0 vs k=2 mean|T|
    tr_k0 = np.abs(T_arr[train_idx][k[train_idx] == 0])
    tr_k2 = np.abs(T_arr[train_idx][k[train_idx] == 2])
    if len(tr_k0) < 2 or len(tr_k2) < 2: continue
    # 方向: k0 mean > k2 mean?
    direction = np.mean(tr_k0) > np.mean(tr_k2)
    # Test: 同一方向?
    te_k0 = np.abs(T_arr[test_idx][k[test_idx] == 0])
    te_k2 = np.abs(T_arr[test_idx][k[test_idx] == 2])
    if len(te_k0) < 2 or len(te_k2) < 2: continue
    test_dir = np.mean(te_k0) > np.mean(te_k2)
    split_results.append((direction, test_dir))

consistent = sum(1 for d, t in split_results if d == t)
log(f"  {N_SPLIT} 次 random split:")
log(f"  方向一致性 (train 預測 test): {consistent}/{len(split_results)} = {consistent/len(split_results)*100:.1f}%")
log(f"  (50% = 隨機; >70% = 有預測力)")
# 實際 train/test 一次
train_idx = np.array([p[0] for p in pairs])
test_idx = np.array([p[1] for p in pairs])
for name, idx in [("Train (30)", train_idx), ("Test (30)", test_idx)]:
    k0_t = np.abs(T_arr[idx][k[idx] == 0])
    k1_t = np.abs(T_arr[idx][k[idx] == 1])
    k2_t = np.abs(T_arr[idx][k[idx] == 2])
    log(f"  {name}: k0 mean|T|={np.mean(k0_t):.1f} ({len(k0_t)}), k1={np.mean(k1_t):.1f} ({len(k1_t)}), k2={np.mean(k2_t):.1f} ({len(k2_t)})")

# ============ B1b. Bonferroni 校正 ============
log("\n=== B1b. Bonferroni 校正 ===")
# 我哋做過幾多個統計測試? (O26 系列)
n_tests = 0
# 列舉: k0 vs k2 (p=0.024), k0 vs k1, k1 vs k2, 對徑|ΔT| (0.030), 去背景 (0.071),
#       異號率 (0.20), k0 r, k1 r, k2 r, 0↔57 排名...
log(f"  我哋做過嘅統計測試 (O26):")
tests = [
    ("k0 vs k2 mean|T|", 0.024),
    ("ΔE=0 對 |ΔT| (原始)", 0.030),
    ("ΔE=0 對 |ΔT| (去背景)", 0.071),
    ("異號率 19/30", 0.200),
    ("k0 對徑 r=+0.469", 0.53),  # 4 對, n=4
    ("k2 對徑 r=-0.415", 0.41),  # 6 對
    ("k0 vs k1 mean|T|", None),
    ("k1 vs k2 mean|T|", None),
]
for name, p in tests:
    if p is not None:
        log(f"    {name}: p={p:.3f}")
        n_tests += 1
log(f"  總測試數 ≈ {n_tests} (只計有 p 值)")
bonf = 0.05 / n_tests
log(f"  Bonferroni 閾值: 0.05/{n_tests} = {bonf:.4f}")
log(f"  全部 p 值 {'✅ 通過' if all(p >= bonf for _, p in tests if p is not None) else '❌ 全部小於閾值!'}")
log(f"  → p=0.024 喺多重比較下唔再顯著!")

# ============ B1c. Permutation (嚴格) ============
log("\n=== B1c. Permutation 檢驗 (k↔|T| 關聯) ===")
# 原統計: k=0 mean|T| vs k=2 mean|T| 差值
obs_diff = np.mean(np.abs(T_arr)[k == 0]) - np.mean(np.abs(T_arr)[k == 2])
perms = []
for _ in range(10000):
    kp = rng.permutation(k)
    d = np.mean(np.abs(T_arr)[kp == 0]) - np.mean(np.abs(T_arr)[kp == 2])
    perms.append(d)
perms = np.array(perms)
p_perm = np.mean(perms >= obs_diff)
log(f"  觀察: k0 mean|T| − k2 mean|T| = {obs_diff:.2f} μK")
log(f"  Permutation p (單尾, k0>k2): {p_perm:.4f}")
log(f"  {'✅ 顯著' if p_perm < 0.05 else '⚠️ 唔顯著 (p>0.05)'}")

# ============ B2. ΔE=0 對 |ΔT| 證偽 ============
log("\n=== B2. ΔE=0 對 |ΔT| 細 (train/test) ===")
# ΔE=0 節點 = k=2
k2set = set(np.where(k == 2)[0])
k2_pairs = [(i, j) for i, j in pairs if i in k2set and j in k2set]
log(f"  k=2 對徑對: {len(k2_pairs)} 對")
# 用一半對徑對做 train, 一半 test — 但只有 6 對, 太少
log(f"  ⚠️ 只有 6 對 — train/test split 無統計力 (n=3 vs 3)")
log(f"  → 呢個 claim 本質上無法用 60 節點數據獨立驗證")

# ============ B3. 冷斑 = k=0 通道 ============
log("\n=== B3. 冷斑 = k=0 通道 (部分證偽) ===")
k0list = np.where(k == 0)[0]
log(f"  k=0 節點: {sorted(k0list.tolist())}")
log(f"  溫度: {[f'{T_arr[i]:+.1f}' for i in k0list]}")
log(f"  → 只有 2/8 極端 (|T|>100: #0=-134, #53=+112)")
log(f"  → 其他 6/8 普通 (#57=+8.2, #4=-3.5!)")
log(f"  ⚠️ 如果 k=0 = 零散射通道 → 全部應該極端")
log(f"  → 呢個 claim 已部分被自身數據證偽 (6/8 唔極端)")
log(f"  → 正確表述: k=0 容許極端, 唔係必然極端")

# ============ B4. 對徑相關 r 值 ============
log("\n=== B4. 對徑溫度相關 r (bootstrap CI) ===")
for kk in [0, 1, 2]:
    idx = np.where(k == kk)[0]
    pair_k = [(i, j) for i, j in pairs if i in idx and j in idx]
    if len(pair_k) < 3:
        log(f"  k={kk}: 只有 {len(pair_k)} 對 — 冇統計力")
        continue
    ts = np.array([T_arr[i] for i, j in pair_k])
    ts2 = np.array([T_arr[j] for i, j in pair_k])
    r, p = stats.pearsonr(ts, ts2)
    log(f"  k={kk}: r={r:+.3f}, p={p:.3f} (n={len(pair_k)})")
    # bootstrap CI
    rng2 = np.random.default_rng(7)
    rs = []
    for _ in range(2000):
        idx2 = rng2.integers(0, len(pair_k), len(pair_k))
        rs.append(stats.pearsonr(ts[idx2], ts2[idx2])[0])
    rs = np.array(rs)
    log(f"    Bootstrap 95% CI: [{np.percentile(rs,2.5):+.3f}, {np.percentile(rs,97.5):+.3f}]")

# ============ B5. NILC/Commander 獨立驗證 ============
log("\n=== B5. 獨立數據交叉驗證 (SMICA vs NILC/Commander) ===")
# 檢查 O21 已做過嘅三地圖一致性
log(f"  O21 已證: Node 9 SMICA -106.99 / NILC -107.21 / Commander -104.47 (2.58% spread)")
log(f"  O26 已證: Node 57 SMICA +8.21 / NILC +7.83 / Commander +8.55 (0.72 μK spread)")
log(f"  → 溫度真實, 唔係 artifact ✅")
log(f"  ⚠️ 但「真實」唔等於「結構」— 三地圖共享 sky signal")

# ============ C. 總結 ============
log("\n" + "=" * 72)
log("C. 證偽性總結")
log("=" * 72)
log("""
┌─────────────────────────────────────────────────────────────┐
│ 主張                          │ 類型   │ 可證偽? │ 現狀     │
├─────────────────────────────────────────────────────────────┤
│ 對徑 = 右乘 r₀ (ε=5.34°)      │ 數學   │ 恆真    │ ✅ 60/60 │
│ k 分佈 {0:8,1:40,2:12}        │ 數學   │ 恆真    │ ✅ 5000  │
│ 20 三角形完美匹配              │ 數學   │ 恆真    │ ✅       │
│ k↔溫度分層 (p=0.024)          │ 物理   │ ✅      │ ⚠️ 弱    │
│ ΔE=0 對 |ΔT| 細 (p=0.071)    │ 物理   │ ✅      │ ❌ 唔顯著 │
│ 冷斑 = k=0 通道               │ 物理   │ ✅      │ ⚠️ 部分反  │
│ 對徑軸 B-mode 對齊 (O26-G1)   │ 物理   │ ✅      │ 🔴 未測  │
│ M=33 相干截斷                 │ 物理   │ ✅      │ 🟡 O9    │
└─────────────────────────────────────────────────────────────┘

★ 核心發現: 幾何定理全部恆真 (冇得證偽, 亦唔需要),
  但物理主張全部可證偽 — 而而家證據強度:
  - k↔溫度: p=0.024 → permutation p=? (睇結果)
  - ΔE=0 |ΔT|: 去背景後 p=0.071 唔顯著
  - 冷斑通道: 6/8 k=0 唔極端 (部分證偽)
  - B-mode: 未測試 (真正嘅前瞻預測!)
""")

with open(f"{OUT}/node57_falsification.txt", "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/node57_falsification.txt")
