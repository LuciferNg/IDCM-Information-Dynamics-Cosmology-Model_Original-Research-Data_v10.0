#!/usr/bin/env python3
"""
O136 — Script 22: 公平密度檢驗 (局部零模型)
================================================================
Script 21 的密度檢驗用全局 log-uniform 平均 (變異大, max 56)。
本 script 用局部零模型: 在目標比附近 ±10% 窗口內生成隨機目標,
計算期望候選數 → 公平判定每條公式是否超越巧合。
"""
import math, json, random
from pathlib import Path

Nd, B_, dimC = 44, 4, 3
mass = {"e": 0.510999, "mu": 105.6584, "tau": 1776.86,
        "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0,
        "W": 80377.0, "Z": 91187.6, "H": 125250.0}
def sinm(n): return math.sin(n*math.pi/88)

TOL = 0.005
random.seed(12345)

# 預計算所有 sin 比
ratios = []
for n in range(1, 45):
    for m in range(1, 45):
        if n != m:
            ratios.append(sinm(n)/sinm(m))
ratios.sort()

def count_within(t):
    return sum(1 for r in ratios if abs(r/t - 1) < TOL)

print("=" * 92)
print("O136 Script 22: 公平密度檢驗 (局部零模型)")
print("=" * 92)

targets = {
    "u/d": mass["u"]/mass["d"], "mu/tau": mass["mu"]/mass["tau"],
    "c/b": mass["c"]/mass["b"], "W/Z": mass["W"]/mass["Z"],
    "H/W": mass["H"]/mass["W"], "s/d": mass["s"]/mass["d"],
    "t/b": mass["t"]/mass["b"],
}

print(f"\n{'─'*92}")
print(f"局部零模型: 目標 ±10% 窗口內 1000 個隨機目標的期望候選數")
print(f"{'─'*92}")
print(f"\n{'配對':>8} {'目標比':>12} {'實際候選':>10} {'局部期望':>10} {'比值':>8} {'p-value':>10} {'判定':>10}")
print("-" * 78)

results = {}
for label, t in targets.items():
    actual = count_within(t)
    # 局部零模型: t×[0.9, 1.1] 均勻
    null_counts = []
    for _ in range(1000):
        tt = t * random.uniform(0.9, 1.1)
        null_counts.append(count_within(tt))
    mean_null = sum(null_counts)/len(null_counts)
    # p-value: P(null <= actual)
    p = sum(1 for c in null_counts if c <= actual)/len(null_counts)
    ratio = actual/mean_null if mean_null > 0 else float('inf')
    verdict = "結構 🟢" if p < 0.05 else ("邊緣 🟡" if p < 0.2 else "巧合 🔴")
    results[label] = {"actual": actual, "mean_null": mean_null, "ratio": ratio, "p": p}
    print(f"{label:>8} {t:>12.6f} {actual:>10} {mean_null:>10.2f} {ratio:>8.2f} {p:>10.3f} {verdict:>10}")

# ═══ 判決 ═══════════════════════════════════════════
print(f"\n{'─'*92}")
print("判決: 幾多條公式超越巧合?")
print(f"{'─'*92}")

sig = [l for l, r in results.items() if r["p"] < 0.05]
marg = [l for l, r in results.items() if 0.05 <= r["p"] < 0.2]
coinc = [l for l, r in results.items() if r["p"] >= 0.2]

print(f"\n🟢 結構性 (p<0.05): {sig if sig else '無'}")
print(f"🟡 邊緣 (0.05≤p<0.2): {marg if marg else '無'}")
print(f"🔴 巧合 (p≥0.2): {coinc if coinc else '無'}")

print(f"\n★ 誠實結論: {len(sig)}/{len(results)} 條公式在 0.5% 容差下超越巧合")

# ═══ 收緊容差檢驗 ═══════════════════════════════════
print(f"\n{'─'*92}")
print("收緊容差: 0.1% 下的檢驗 (更嚴格)")
print(f"{'─'*92}")

TOL2 = 0.001
def count2(t):
    return sum(1 for r in ratios if abs(r/t - 1) < TOL2)

print(f"\n{'配對':>8} {'目標比':>12} {'實際':>6} {'局部期望':>10} {'p-value':>10} {'判定':>10}")
print("-" * 64)
for label, t in targets.items():
    actual = count2(t)
    null_counts = [count2(t*random.uniform(0.9,1.1)) for _ in range(1000)]
    mean_null = sum(null_counts)/len(null_counts)
    p = sum(1 for c in null_counts if c <= actual)/len(null_counts)
    verdict = "結構 🟢" if p < 0.05 else ("邊緣 🟡" if p < 0.2 else "巧合 🔴")
    print(f"{label:>8} {t:>12.6f} {actual:>6} {mean_null:>10.2f} {p:>10.3f} {verdict:>10}")

# ═══ 保存 ═══════════════════════════════════════════
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "22_density_test.json", "w") as f:
    json.dump({
        "tol": TOL,
        "results": {k: {kk: (round(vv,6) if isinstance(vv,float) else vv) 
                        for kk, vv in v.items()} for k, v in results.items()},
        "structural": sig, "marginal": marg, "coincidence": coinc,
        "verdict": f"{len(sig)}/{len(results)} 超越巧合",
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/22_density_test.json")