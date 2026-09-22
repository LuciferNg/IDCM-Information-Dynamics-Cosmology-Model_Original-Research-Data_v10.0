#!/usr/bin/env python3
"""
O136 — Script 23: 最佳匹配偏差分佈 — 決定性判決
================================================================
核心問題: 「8/8 質量比閉合」是否超越隨機?

方法: 對隨機目標, 計算 sin 譜中可達到的最佳偏差。
      若觀測偏差 ≈ 隨機最佳偏差 → 匹配係密度效應, 非結構。
"""
import math, json, random
from pathlib import Path

Nd, B_, dimC = 44, 4, 3
def sinm(n): return math.sin(n*math.pi/88)

# 所有 sin 比
ratios = sorted(sinm(n)/sinm(m) for n in range(1,45) for m in range(1,45) if n != m)

def best_dev(t):
    """min |r/t − 1| over all sin ratios"""
    import bisect
    i = bisect.bisect_left(ratios, t)
    cands = []
    for j in range(max(0,i-3), min(len(ratios), i+4)):
        cands.append(abs(ratios[j]/t - 1))
    return min(cands)*100

print("=" * 92)
print("O136 Script 23: 最佳匹配偏差分佈 — 決定性判決")
print("=" * 92)

random.seed(999)
N = 20000
null_devs = []
for _ in range(N):
    t = math.exp(random.uniform(math.log(0.036), math.log(28)))
    null_devs.append(best_dev(t))
null_devs.sort()

print(f"\n{'─'*92}")
print("隨機目標的最佳 sin 匹配偏差分佈 (20000 樣本)")
print(f"{'─'*92}")
for q in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
    v = null_devs[int(N*q/100)]
    print(f"  {q:>3}% 分位: {v:.4f}%")
print(f"  平均: {sum(null_devs)/N:.4f}%")
print(f"  最小: {null_devs[0]:.6f}%")

# ═══ 觀測偏差 ═══════════════════════════════════════
print(f"\n{'─'*92}")
print("觀測偏差 vs 隨機分佈")
print(f"{'─'*92}")

obs = [
    ("u/d", 0.026, "(10,24)", "純 sin"),
    ("mu/tau", 0.160, "(1,18)", "純 sin"),
    ("c/b", 0.368, "(8,33)", "純 sin"),
    ("W/Z", 0.146, "(30,41)", "純 sin"),
    ("H/W", 0.064, "(38,19)", "純 sin"),
    ("s/d", 0.393, "(22,1)+φ", "φ 修正"),
    ("t/b", 0.005, "(19,33)+φ", "φ 修正"),
    ("mu/e", 0.001, "純 φ", "純 φ"),
]

print(f"\n{'配對':>8} {'觀測偏差':>10} {'模式':>12} {'類型':>8} {'隨機分位':>10} {'判定':>10}")
print("-" * 66)
verdicts = []
for label, dev, mode, typ in obs:
    # 分位: 幾多百分比的隨機目標有更差(更大)的偏差
    pct = sum(1 for v in null_devs if v > dev)/N*100
    verdict = "超越隨機 🟢" if pct < 10 else ("邊緣 🟡" if pct < 30 else "巧合 🔴")
    verdicts.append((label, dev, pct, verdict))
    print(f"{label:>8} {dev:>9.4f}% {mode:>12} {typ:>8} {pct:>9.1f}% {verdict:>10}")

# ═══ 聯合機率 ═══════════════════════════════════════
print(f"\n{'─'*92}")
print("★ 聯合機率: 5 條純 sin 公式全部達到觀測偏差的機率")
print(f"{'─'*92}")

pure_obs = [0.026, 0.160, 0.368, 0.146, 0.064]
probs = []
for dev in pure_obs:
    p = sum(1 for v in null_devs if v > dev)/N
    probs.append(p)
joint = 1.0
for p in probs:
    joint *= p
print(f"\n各公式的單獨機率: {[f'{p:.4f}' for p in probs]}")
print(f"聯合機率 (獨立假設): {joint:.6f}")
print(f"→ {'🟢 超越隨機' if joint < 0.05 else ('🟡 邊緣' if joint < 0.2 else '🔴 巧合')}")

# 更保守: 用觀測中位數
med = sorted(pure_obs)[2]
p_med = sum(1 for v in null_devs if v > med)/N
print(f"\n最保守估計 (全部用中位數偏差 {med}%): p = {p_med:.4f}, p⁵ = {p_med**5:.6f}")

# ═══ 判決 ═══════════════════════════════════════════
print(f"\n{'─'*92}")
print("判決")
print(f"{'─'*92}")

n_beat = sum(1 for _, _, pct, v in verdicts if "超越" in v)
n_marg = sum(1 for _, _, pct, v in verdicts if "邊緣" in v)
print(f"""
🟢 超越隨機: {n_beat}/{len(obs)}
🟡 邊緣: {n_marg}/{len(obs)}
🔴 巧合: {len(obs)-n_beat-n_marg}/{len(obs)}

核心結論:
  sin 譜在 [0.036, 28] 區間有 1936 個比值 → 密度高
  隨機目標的最佳匹配偏差中位數 = {null_devs[N//2]:.4f}%
  O34/O35 觀測偏差中位數 = 0.146%

  → 觀測偏差 {'≈' if abs(math.log(0.146/null_devs[N//2])) < 0.5 else '≠'} 隨機最佳偏差
  → {'🔴 匹配係密度效應, 唔係結構' if abs(math.log(0.146/null_devs[N//2])) < 1.0 else '🟢 觀測顯著優於隨機'}
""")

# ═══ 保存 ═══════════════════════════════════════════
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "23_best_match_test.json", "w") as f:
    json.dump({
        "n_samples": N,
        "null_median_dev_pct": null_devs[N//2],
        "null_mean_dev_pct": sum(null_devs)/N,
        "null_quantiles": {str(q): null_devs[int(N*q/100)] for q in [1,5,10,25,50,75,90,95,99]},
        "observed": [{"pair": l, "dev_pct": d, "mode": m, "type": t, 
                      "pct_better": round(p,2), "verdict": v} for l,d,m,t,p,v in 
                     [(l,d,m,t, sum(1 for x in null_devs if x > d)/N*100, v) for l,d,m,t,v in 
                      [(a,b,c,e,"") for a,b,c,e in obs]]],
        "joint_prob_pure_sin": joint,
        "n_beats_random": n_beat,
        "n_marginal": n_marg,
    }, f, indent=2, ensure_ascii=False)
print(f"✅ 結果已寫入 data/23_best_match_test.json")