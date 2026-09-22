#!/usr/bin/env python3
"""
O136 — Script 21: 決定性檢驗 — 模式分配全局一致性
================================================================
發現 (script 20):
  d: u/d 公式要求 d↔24; s/d 公式要求 d↔1  → 衝突
  W: W/Z 公式要求 W↔30; H/W 公式要求 W↔19 → 衝突

本 script: 對每個質量比, 枚舉所有符合的 (n,m) 對, 檢查是否存在
           全局一致的模式分配。
若不存在 → 框架係數值巧合集合, 唔係結構分配。
"""
import math, json
from pathlib import Path
from itertools import product

phi = (1 + math.sqrt(5))/2
lnphi = math.log(phi)
Nd, B_, dimC = 44, 4, 3

mass = {"e": 0.510999, "mu": 105.6584, "tau": 1776.86,
        "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0,
        "W": 80377.0, "Z": 91187.6, "H": 125250.0}

def sinm(n): return math.sin(n*math.pi/88)

print("=" * 92)
print("O136 Script 21: 模式分配全局一致性檢驗")
print("=" * 92)

# 純 sin 比配對
pure_ratios = [("u","d"), ("mu","tau"), ("c","b"), ("W","Z"), ("H","W")]
# φ 修正配對 (sin 對唔直接決定模式)
phi_ratios = [("s","d"), ("t","b")]

TOL = 0.005   # 0.5%

print(f"\n{'─'*92}")
print(f"1. 枚舉每個比的所有 (n,m) 候選 (容差 {TOL*100:.1f}%)")
print(f"{'─'*92}")

all_cands = {}
for a, b in pure_ratios:
    target = mass[a]/mass[b]
    cands = []
    for n in range(1, 45):
        for m in range(1, 45):
            r = sinm(n)/sinm(m)
            if abs(r/target - 1) < TOL:
                cands.append((n, m, r, (r-target)/target*100))
    all_cands[(a,b)] = cands
    print(f"\n{a}/{b}: 目標 {target:.6f}")
    print(f"  候選數: {len(cands)}")
    for n, m, r, dev in sorted(cands, key=lambda x: abs(x[3]))[:6]:
        print(f"    ({n:>2},{m:>2}): {r:.6f}  {dev:+.4f}%")
    if len(cands) > 6:
        print(f"    ... 另 {len(cands)-6} 個")

# ═══ 2. 全局一致性搜尋 ═══════════════════════════════
print(f"\n{'─'*92}")
print("2. 全局一致性搜尋 (每個粒子唯一模式)")
print(f"{'─'*92}")

# 從每個 ratio 的候選中選一個, 檢查同一粒子模式是否一致
particles = ["u","d","mu","tau","c","b","W","Z","H"]
sols = []

def search(idx, assign):
    if idx == len(pure_ratios):
        sols.append(dict(assign))
        return
    a, b = pure_ratios[idx]
    for n, m, r, dev in all_cands[(a,b)]:
        if a in assign and assign[a] != n: continue
        if b in assign and assign[b] != m: continue
        na, nb = dict(assign), dict(assign)
        na[a] = n; na[b] = m
        search(idx+1, na)

search(0, {})
print(f"\n全局一致的分配方案數: {len(sols)}")

if sols:
    print(f"\n{'方案':>4} " + " ".join(f"{p:>4}" for p in particles))
    print("-" * (6 + 5*len(particles)))
    for i, s in enumerate(sols[:15]):
        print(f"{i:>4} " + " ".join(f"{s.get(p,'—'):>4}" for p in particles))
    if len(sols) > 15:
        print(f"... 另 {len(sols)-15} 個方案")
else:
    print(f"\n🔴 無全局一致方案 → 模式分配唔存在!")

# ═══ 3. 檢查 O34/O35 實際用的分配 ═══════════════════
print(f"\n{'─'*92}")
print("3. O34/O35 實際使用的分配 vs 一致性")
print(f"{'─'*92}")

used = {"u":10, "d":24, "mu":1, "tau":18, "c":8, "b":33, "W":30, "Z":41, "H":38}
print(f"\n{'粒子':>6} {'用模式':>8}")
print("-" * 18)
for p, n in used.items():
    print(f"{p:>6} {n:>8}")

print(f"\n─── 檢查每條公式是否與此分配相容 ───")
print(f"\n{'公式':>10} {'分配給出':>14} {'PDG比':>12} {'偏差%':>10} {'狀態':>8}")
print("-" * 60)
for a, b in pure_ratios:
    na, nb = used[a], used[b]
    r = sinm(na)/sinm(nb)
    target = mass[a]/mass[b]
    dev = (r-target)/target*100
    ok = abs(dev) < TOL*100
    print(f"{a+'/'+b:>10} {f'({na},{nb})':>14} {target:>12.6f} {dev:>+10.3f} {'✅' if ok else '🔴':>8}")

# ═══ 4. 密度效應量化 ═════════════════════════════════
print(f"\n{'─'*92}")
print("4. ★ 密度效應量化 — 隨機目標會有多少命中?")
print(f"{'─'*92}")

import random
random.seed(42)
n_trials = 2000
hits = []
for _ in range(n_trials):
    # 隨機目標比 (log-uniform 在 [0.02, 50])
    t = math.exp(random.uniform(math.log(0.02), math.log(50)))
    c = 0
    for n in range(1, 45):
        for m in range(1, 45):
            if abs(sinm(n)/sinm(m)/t - 1) < TOL:
                c += 1
    hits.append(c)

mean_hits = sum(hits)/len(hits)
print(f"\n隨機目標在 {TOL*100:.1f}% 內的候選數:")
print(f"  平均 = {mean_hits:.2f}")
print(f"  中位數 = {sorted(hits)[len(hits)//2]}")
print(f"  最大 = {max(hits)}")
print(f"\nO34/O35 實際候選數: {[len(all_cands[k]) for k in pure_ratios]}")
print(f"\n★ 若實際候選數 ≈ 隨機平均 → 密度效應主導, 唔係結構 🔴")

# ═══ 5. 判決 ════════════════════════════════════════
print(f"\n{'─'*92}")
print("5. 判決")
print(f"{'─'*92}")

print(f"""
純 sin 配對的候選數 vs 隨機期望:
""")
print(f"{'配對':>10} {'實際候選':>10} {'隨機平均':>10} {'比值':>8} {'判定':>10}")
print("-" * 54)
for a, b in pure_ratios:
    c = len(all_cands[(a,b)])
    ratio = c/mean_hits if mean_hits > 0 else float('inf')
    verdict = "結構" if ratio < 0.5 else ("巧合" if ratio < 2 else "富餘")
    print(f"{a+'/'+b:>10} {c:>10} {mean_hits:>10.2f} {ratio:>8.2f} {verdict:>10}")

# ═══ 6. 保存 ════════════════════════════════════════
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "21_global_consistency.json", "w") as f:
    json.dump({
        "tol": TOL,
        "candidates": {f"{a}/{b}": [(n, m, round(r,6), round(d,4)) for n,m,r,d in c] 
                       for (a,b), c in all_cands.items()},
        "n_consistent_solutions": len(sols),
        "solutions": [dict(s) for s in sols[:20]],
        "used_assignment": used,
        "random_mean_hits": mean_hits,
        "verdict": "無全局一致方案" if not sols else f"{len(sols)} 個方案",
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/21_global_consistency.json")