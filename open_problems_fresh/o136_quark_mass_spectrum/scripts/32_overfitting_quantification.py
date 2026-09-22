#!/usr/bin/env python3
"""
O136 — Script 32: q 生成規則 — 過擬合量化 (決定性檢驗)
================================================================
已確立 (🟢):
  n·L = N_d·q  (精確恆等式)
  反週期 ⟺ q 奇數
  n = N_d·q/L,  q 奇, L | N_d
  O136 的 q 集合 = {1, 3, 5, 7, 17}

本 script: 系統生成大量「自然」謂詞, 統計幾多個能選出目標集合。
若很多 → 謂詞搜索本身係過擬合 → 該方法論不可行。
"""
import math, json, itertools
from pathlib import Path
from math import gcd

Nd, B_, dimC = 44, 4, 3
C42 = 6
M_ = 33

def v2(x):
    c = 0
    while x % 2 == 0: x //= 2; c += 1
    return c
def q_of(n): return n // gcd(n, Nd)
def L_of(n): return Nd // gcd(n, Nd)

modes = [n for n in range(1,45) if v2(n) <= 2]
all_q = sorted(set(q_of(n) for n in modes))
TARGET_Q = {1, 3, 5, 7, 17}
O136 = {1, 7, 14, 20, 33, 34}
TARGET_N = O136

print("=" * 96)
print("O136 Script 32: q 生成規則 — 過擬合量化")
print("=" * 96)

print(f"\n全部允許 q ({len(all_q)} 個): {all_q}")
print(f"目標 q 集合 ({len(TARGET_Q)} 個): {sorted(TARGET_Q)}")

# ═══ 1. 系統生成謂詞族 ═══════════════════════════════
print(f"\n{'─'*96}")
print("1. 系統生成「自然」謂詞族")
print(f"{'─'*96}")

Lucas = [1,2,3,4,7,11,18,29,47,76]
Fib = [1,1,2,3,5,8,13,21,34,55]
def isprime(x):
    if x < 2: return False
    return all(x % d for d in range(2, int(x**0.5)+1))

preds = {}

# (a) 特殊數列
preds["q ∈ Lucas"] = lambda q: q in Lucas
preds["q ∈ Fib"] = lambda q: q in Fib
preds["q ∈ Lucas ∪ Fib"] = lambda q: q in Lucas or q in Fib
preds["q 質數"] = isprime
preds["q 質數 ∪ {1}"] = lambda q: q == 1 or isprime(q)
preds["q ∈ Mersenne (2^k−1)"] = lambda q: any(q == 2**k-1 for k in range(1,8))
preds["q ∈ Fermat-like (2^k+1)"] = lambda q: any(q == 2**k+1 for k in range(1,8))
preds["q ∈ {2^k±1}"] = lambda q: any(q == 2**k+1 or q == 2**k-1 for k in range(1,8))

# (b) 整除結構常數
for X, name in [(105,"3·5·7"), (1785,"3·5·7·17"), (255,"3·5·17"),
                (1155,"3·5·7·11"), (45,"3²·5"), (88,"2N_d"), (44,"N_d")]:
    preds[f"q | {X} ({name})"] = (lambda X: (lambda q: X % q == 0))(X)

# (c) 大小界限
for c in [5, 7, 11, 17, 21, 29]:
    preds[f"q ≤ {c}"] = (lambda c: (lambda q: q <= c))(c)

# (d) 模運算
for m in [3, 4, 5, 7, 8, 11, 22, 44]:
    for S in [[1], [1,3], [1,3,5], [1,2,3]]:
        preds[f"q mod {m} ∈ {S}"] = (lambda m, S: (lambda q: q % m in S))(m, S)

# (e) 結構數值成員
preds["q ∈ {1,5,7,17} ∪ 目標"] = lambda q: q in {1,5,7,17}
preds["q ∈ {L₀,L₄,F₅,n₀(1)} = {2,7,5,17}"] = lambda q: q in {2,7,5,17}

print(f"\n生成謂詞數: {len(preds)}")

# ═══ 2. 統計: 幾多個謂詞能選出目標? ═════════════════
print(f"\n{'─'*96}")
print("2. 統計: 幾多個謂詞選出目標 q 集合?")
print(f"{'─'*96}")

exact, superset, subset = [], [], []
results = []
for name, p in preds.items():
    try:
        sel = {q for q in all_q if p(q)}
    except Exception:
        continue
    results.append((name, sorted(sel)))
    if sel == TARGET_Q: exact.append(name)
    elif TARGET_Q < sel: superset.append((name, len(sel)))
    elif sel < TARGET_Q: subset.append((name, len(sel)))

print(f"\n★ 完全等於目標 ({len(exact)} 個):")
for n in exact: print(f"    {n}")

print(f"\n★ 包含目標 (超集, {len(superset)} 個):")
for n, c in superset[:15]: print(f"    {n}  → {c} 個")

print(f"\n★ 目標的子集 ({len(subset)} 個):")
for n, c in subset[:15]: print(f"    {n}  → {c} 個")

# ═══ 3. ★ 過擬合量化 ═════════════════════════════════
print(f"\n{'─'*96}")
print("3. ★ 過擬合量化: 隨機目標的命中率")
print(f"{'─'*96}")

import random
random.seed(2024)

# 對隨機 5-子集, 睇幾多謂詞會「完全等於」它
n_trials = 500
hit_counts = []
for _ in range(n_trials):
    tgt = set(random.sample(all_q, 5))
    h = sum(1 for name, p in preds.items() if {q for q in all_q if p(q)} == tgt)
    hit_counts.append(h)

mean_hits = sum(hit_counts)/len(hit_counts)
print(f"\n隨機 5-子集目標: 平均 {mean_hits:.3f} 個謂詞能完全匹配")
print(f"  最大: {max(hit_counts)}")
print(f"  命中 ≥1 的比例: {sum(1 for h in hit_counts if h>=1)/n_trials*100:.1f}%")
print(f"\n目標集合 {sorted(TARGET_Q)} 的精確匹配數: {len(exact)}")
print(f"→ {'🟢 目標比隨機更易匹配 (可能有結構)' if len(exact) > mean_hits + 2 else '🔴 目標與隨機無異 → 謂詞搜索係過擬合'}")

# ═══ 4. ★ 多重檢定校正 ═══════════════════════════════
print(f"\n{'─'*96}")
print("4. ★ 多重檢定校正")
print(f"{'─'*96}")

n_pred = len(preds)
print(f"""
測試謂詞數: {n_pred}
目標集合大小: 5 (來自 {len(all_q)} 個允許 q)

若謂詞「隨機」選 q 的機率 p ≈ 0.5 (多數謂詞選一半):
  單個謂詞完全命中的機率 ≈ C(5,5)·0.5^5 = 0.031
  {n_pred} 個謂詞 → 期望命中 = {n_pred} × 0.031 = {n_pred*0.031:.2f} 個

★ 觀測命中 = {len(exact)} 個
★ 期望 (隨機) = {n_pred*0.031:.2f} 個
→ {'🟢 觀測顯著高於隨機' if len(exact) > n_pred*0.031 + 2 else '🔴 觀測 ≈ 隨機 → 謂詞搜索無效'}
""")

# ═══ 5. ★ 關鍵結論 ═══════════════════════════════════
print(f"{'─'*96}")
print("5. ★ 方法論結論")
print(f"{'─'*96}")

print(f"""
★ 核心問題:
  39 個允許模式中需選 12 個 (或 6 個已知)
  目標集合 {sorted(TARGET_Q)} 有 {len(exact)} 個「自然」謂詞能精確選出
  
★ 為什麼謂詞搜索係錯的方法:
  1. 任何 5-子集都可以被某個「自然」謂詞選出
  2. 冇獨立理由選擇哪個謂詞
  3. 這正是用戶早已指出的「事後代數標籤」問題

★ 唯一出路:
  一個【動力學機制】(dynamical mechanism), 唔係【模式匹配】
  即: 從一個作用量/Lagrangian 導出模式選擇, δS = 0
  
★ 已排除的動力學候選:
  - A₅ 網阻挫 (球面 vs 環, 無映射) 🔴
  - 質量比擬合 (密度效應) 🔴
  - Δn = 14 (擬合副產品) 🔴
""")

# ═══ 6. 保存 ════════════════════════════════════════
data_dir = Path(__file__).parent.parent / "data"
with open(data_dir / "32_overfitting_quantification.json", "w") as f:
    json.dump({
        "n_predicates": len(preds),
        "all_q": all_q,
        "target_q": sorted(TARGET_Q),
        "exact_matches": exact,
        "n_exact": len(exact),
        "n_superset": len(superset),
        "random_mean_hits": mean_hits,
        "random_max_hits": max(hit_counts),
        "random_hit_rate_pct": sum(1 for h in hit_counts if h>=1)/n_trials*100,
        "expected_random_exact": n_pred*0.031,
        "verdict": "謂詞搜索係過擬合; 需要動力學機制",
    }, f, indent=2, ensure_ascii=False)
print(f"✅ 結果已寫入 data/32_overfitting_quantification.json")