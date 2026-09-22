#!/usr/bin/env python3
"""
O136 — Script 35: 質量 = 穿透率? (穿透率假設檢驗)
================================================================
用戶假設: 質量來自穿透率 (transmission)

依據 (O182):
  88 邊 = TRANSPARENT (CMB 穿過唔改) — 透明通道
  32 邊 = OPAQUE (同色阻挫) — 拓撲位元, 寫入通道
  c_{i,n} = cos²(nβ_i/2) — 逐節點穿透權重 (O81 §7.3)

檢驗候選:
  T_prod(n) = Π_i c_{i,n}              (總穿透率)
  T_geo(n)  = T_prod^(1/60)            (幾何平均)
  T_arith(n)= (1/60)Σ_i c_{i,n}        (算術平均)
  T_log(n)  = exp((1/60)Σ_i ln c_{i,n}) (對數平均)

目標: m_p/m_q = T(n_p)/T(n_q) 或其他函數關係
"""
import numpy as np, math, json, itertools
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = ROOT / "cmb_cold_spot/data"
OUT = Path(__file__).parent.parent / "data"
Nd, B_, dimC = 44, 4, 3

mass = {"e": 0.510999, "mu": 105.6584, "tau": 1776.86,
        "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0}
A5_MODES = [1, 2, 3, 4, 5, 7, 9, 11, 13]

print("=" * 96)
print("O136 Script 35: 質量 = 穿透率?")
print("=" * 96)

# ═══ 1. 幾何 + 穿透權重 ══════════════════════════════
nodes = np.loadtxt(DATA / "a5_nodes.txt")
ra, dec = np.radians(nodes[:,0]), np.radians(nodes[:,1])
U = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
l, b = math.radians(209.0), math.radians(-57.0)
cold = np.array([math.cos(b)*math.cos(l), math.cos(b)*math.sin(l), math.sin(b)])
beta = np.arccos(np.clip(U @ cold, -1, 1))

# 透明度權重 (由著色)
col = {}
for line in (DATA / "anchored_coloring.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split(); col[int(p[0])] = int(p[3])
color = np.array([col[i] for i in range(60)])

print(f"\n{'─'*96}")
print("1. 幾何 + 穿透權重")
print(f"{'─'*96}")
print(f"\nA₅ 節點 60, 著色 {int(color.sum())} 冷 / {60-int(color.sum())} 非冷")
print(f"β_i 範圍: [{np.degrees(beta).min():.2f}°, {np.degrees(beta).max():.2f}°]")

# ═══ 2. ★ 各種穿透率定義 ═════════════════════════════
print(f"\n{'─'*96}")
print("2. ★ 各種穿透率定義")
print(f"{'─'*96}")

def transmissions(n):
    c = np.cos(n*beta/2)**2
    c = np.clip(c, 1e-300, 1.0)
    return {
        "prod":  float(np.prod(c)),
        "geo":   float(np.exp(np.log(c).mean())),
        "arith": float(c.mean()),
        "log":   float(np.log(c).mean()),
        "harm":  float(60.0/np.sum(1.0/c)),
    }

print(f"\n{'n':>3} {'T_prod':>14} {'T_geo':>12} {'T_arith':>10} {'⟨ln c⟩':>12} {'T_harm':>10}")
print("-" * 66)
T = {}
for n in A5_MODES:
    T[n] = transmissions(n)
    print(f"{n:>3} {T[n]['prod']:>14.6e} {T[n]['geo']:>12.6f} {T[n]['arith']:>10.6f} {T[n]['log']:>12.6f} {T[n]['harm']:>10.6f}")

# ═══ 3. ★★ 關鍵檢驗: 穿透率比 vs 質量比 ══════════════
print(f"\n{'─'*96}")
print("3. ★★ 關鍵檢驗: 穿透率比 vs 觀測質量比")
print(f"{'─'*96}")

particles = ["e","mu","tau","u","d","s","c","b","t"]
obs = {}
for a, bb in itertools.combinations(particles, 2):
    obs[(a,bb)] = mass[a]/mass[bb]

print(f"\n觀測質量比範圍: [{min(obs.values()):.3e}, {max(obs.values()):.3e}]")
print(f"  = {max(obs.values())/min(obs.values()):.3e} 倍")

for key in ["prod", "geo", "arith", "harm"]:
    vals = [T[n][key] for n in A5_MODES]
    rng = max(vals)/min(vals)
    print(f"\nT_{key} 範圍: [{min(vals):.6e}, {max(vals):.6e}] = {rng:.3e} 倍")

print(f"\n─── 檢查: 有冇一個定義的範圍匹配觀測的 {max(obs.values())/min(obs.values()):.3e} 倍? ───")

# ═══ 4. ★★★ 直接檢驗: 所有配對 + 所有冪次 ══════════
print(f"\n{'─'*96}")
print("4. ★★★ 直接檢驗: 找最佳 (定義, 配對, 冪次)")
print(f"{'─'*96}")

sorted_p = sorted(particles, key=lambda p: mass[p])
best_results = []

for key in ["prod", "geo", "arith", "harm"]:
    # 用 log 線性檢驗: ln(m) = a + b·ln(T)?
    for perm in itertools.permutations(A5_MODES):
        xs = np.array([math.log(T[n][key]) for n in perm])
        ys = np.array([math.log(mass[p]) for p in sorted_p])
        if xs.std() < 1e-12: continue
        # 線性回歸
        A_ = np.vstack([np.ones(9), xs]).T
        coef, res, *_ = np.linalg.lstsq(A_, ys, rcond=None)
        pred = A_ @ coef
        rms = float(np.sqrt(np.mean((pred-ys)**2)))
        best_results.append((rms, key, perm, coef[0], coef[1]))

best_results.sort(key=lambda x: x[0])
print(f"\n搜索: 4 定義 × 9! 配對 = {4*math.factorial(9)} 組合")
print(f"\n最佳 5 個 (按 ln(m) vs ln(T) 線性擬合 RMS):")
print(f"\n{'RMS':>8} {'定義':>7} {'配對 (模式→粒子)':>44} {'斜率':>10}")
print("-" * 76)
for rms, key, perm, a0, a1 in best_results[:5]:
    pair_str = " ".join(f"{p}:{n}" for p, n in zip(sorted_p, perm))
    print(f"{rms:>8.4f} {key:>7} {pair_str:>44} {a1:>10.4f}")

print(f"\n★ 最佳 RMS = {best_results[0][0]:.4f}")
print(f"★ 隨機期望 RMS (ln m 的標準差) = {np.std([math.log(mass[p]) for p in sorted_p]):.4f}")
print(f"→ {'🟢 穿透率解釋質量!' if best_results[0][0] < 0.5 else '🔴 唔解釋'}")

# ═══ 5. ★ 直接比值檢驗 (無需回歸) ════════════════════
print(f"\n{'─'*96}")
print("5. ★ 直接比值檢驗: T 比 vs 質量比 (對數斜率)")
print(f"{'─'*96}")

for key in ["prod", "geo", "arith", "harm"]:
    ratios = []
    for i, j in itertools.combinations(A5_MODES, 2):
        tr = T[i][key]/T[j][key]
        ratios.append(abs(math.log(tr)))
    print(f"\nT_{key} 的 |ln(T_i/T_j)| 範圍: [{min(ratios):.4f}, {max(ratios):.4f}]")

obs_log = [abs(math.log(v)) for v in obs.values()]
print(f"\n觀測 |ln(m_a/m_b)| 範圍: [{min(obs_log):.4f}, {max(obs_log):.4f}]")

# ═══ 6. 保存 ════════════════════════════════════════
with open(OUT / "35_transmission_test.json", "w") as f:
    json.dump({
        "a5_modes": A5_MODES,
        "transmissions": {str(n): T[n] for n in A5_MODES},
        "observed_range": max(obs.values())/min(obs.values()),
        "best_fit": {"rms": best_results[0][0], "defn": best_results[0][1],
                     "perm": list(best_results[0][2]), "slope": best_results[0][4]},
        "verdict": "見 stdout",
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/35_transmission_test.json")