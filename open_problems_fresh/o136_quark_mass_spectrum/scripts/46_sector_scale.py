#!/usr/bin/env python3
"""
O136 — Script 46: 扇區依賴標度攻堅 (剩餘開放 #1/#3)
================================================================
承接 docs/25-26:
  m_n = C·|Δm_n|^{φ²} → RMS 0.5873, 但 C = 5.387e−5 MeV ≠ M₀ = 27.900915 MeV
  → 標度未接入框架。docs/26 §六 候選解釋 #1: 「質量依賴扇區 (輕子/上夸克/下夸克)」

★ 重新表述 (本 script 起點):
  |Δm| 範圍 110.5×, 取 α=φ² → 110.5^2.618 = 2.23e5× ≈ 觀測 3.379e5×
  ⟹ 範圍【已經對】; 真正障礙只有形狀。
  → 「範圍/比值分離」框架修正: 範圍唔係獨立障礙 (任何無界函數 + 冪次都可達任何範圍)

模型: ln m_p = ln C_{sector(p)} + α·ln|Δm_{n_p}|
  sector ∈ {lepton, up, down} (3 標度) 或 {lepton, quark} (2 標度) 或 {全部} (1 標度)
  A₅ 選擇律預言 9 模式 = 3 輕子 + 6 夸克 ⟹ 扇區分裂係結構預言, 非後驗
"""
import numpy as np, math, json, itertools
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"
phi = (1+math.sqrt(5))/2; ph2 = phi**2
ND = 44; MU2 = 2.0

MASS = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
SECTOR3 = {"e":"L","mu":"L","tau":"L","u":"U","c":"U","t":"U","d":"D","s":"D","b":"D"}
SECTOR2 = {"e":"L","mu":"L","tau":"L","u":"Q","c":"Q","t":"Q","d":"Q","s":"Q","b":"Q"}
PARTS = ["e","mu","tau","u","c","t","d","s","b"]        # 固定次序
LM = np.array([math.log(MASS[p]) for p in PARTS])
M9 = [1,2,3,4,5,7,9,11,13]

# ── 幾何: 位置算子 + 二階自能 ──
Nc = 44
x = np.arange(1, Nc+1, dtype=float)
Psi = np.zeros((Nc, Nc))
for n in range(1, Nc+1):
    Psi[:, n-1] = np.sin(n*math.pi*x/(Nc+1))
for n in range(Nc):
    Psi[:, n] /= np.linalg.norm(Psi[:, n])
V = Psi.T @ np.diag(x - x.mean()) @ Psi
E = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1, 45)])

SE2 = {}
for n in M9:
    t = 0.0
    for m in range(Nc):
        if m == n-1 or (m-(n-1)) % 2 == 0: continue
        dE = E[n-1]-E[m]
        if abs(dE) < 1e-12: continue
        t += V[n-1, m]**2/dE
    SE2[n] = abs(t)
DM = np.array([SE2[n] for n in M9])

# Gap 方程主本徵向量 (docs/26 §二)
K = np.zeros((Nc, Nc))
for n in range(Nc):
    for m in range(Nc):
        if m == n: continue
        K[n, m] = V[n, m]**2 / E[m]**2
w, vec = np.linalg.eig(K)
i0 = int(np.argmax(np.abs(w)))
Gv = np.abs(vec[:, i0].real)
GV = np.array([Gv[n-1] for n in M9])
GV = GV/GV.max()

print("=" * 96)
print("O136 Script 46: 扇區依賴標度攻堅")
print("=" * 96)

print(f"\n{'─'*96}\n1. 範圍檢驗 (修正「範圍/比值分離」框架)\n{'─'*96}")
for a in [1.0, ph2, 2.0, 3.0]:
    rng = (DM.max()/DM.min())**a
    print(f"  |Δm|^α, α={a:.4f}: 範圍 = {rng:.3e}   (觀測 {max(MASS.values())/min(MASS.values()):.3e}, 比 {rng/(max(MASS.values())/min(MASS.values())):.2f}×)")
print(f"  ⟹ ★ 範圍唔係獨立障礙: 任何無界函數 + 冪次可達任意範圍")

# ── 扇區標度擬合 ──
def fit_sector(cand, sector_map, alpha_grid=None):
    """搜尋【所有】扇區指派 (允許非連續) + α。
    cand: 9 值 (M9 次序)。扇區內採單調配對 (對固定 α 係 rearrangement 最優)。"""
    if alpha_grid is None:
        alpha_grid = np.linspace(0.05, 8.0, 160)
    LC = np.log(cand)
    secs = [sector_map[p] for p in PARTS]
    names = sorted(set(secs))
    sizes = {s: secs.count(s) for s in names}
    pos = list(range(9))
    best = (9e9, None, None, None)

    # 所有扇區指派: 把 9 個模式位置分給各扇區
    def assignments(names, pos):
        if len(names) == 1:
            yield {names[0]: list(pos)}; return
        s = names[0]; k = sizes[s]
        for c in itertools.combinations(pos, k):
            rest = [p for p in pos if p not in c]
            for sub in assignments(names[1:], rest):
                yield {s: list(c), **sub}

    for asg in assignments(names, pos):
        # 每個扇區內: 質量由大到小 ↔ cand 由大到小
        pmap = {}          # PARTS index -> M9 index (0-based)
        ok = True
        for s in names:
            ps = [i for i, p in enumerate(PARTS) if secs[i] == s]
            ps = sorted(ps, key=lambda i: -MASS[PARTS[i]])
            cs = sorted(asg[s], key=lambda k: -LC[k])
            if len(ps) != len(cs): ok = False; break
            for pp, cc in zip(ps, cs):
                pmap[pp] = cc
        if not ok: continue
        base = np.array([LC[pmap[i]] for i in range(9)])
        for a in alpha_grid:
            pred = a * base
            res = LM - pred
            for s in names:
                ps = [i for i, p in enumerate(PARTS) if secs[i] == s]
                res[ps] = res[ps] - res[ps].mean()
            rms = float(np.sqrt(np.mean(res**2)))
            if rms < best[0]:
                sc = {}
                for s in names:
                    ps = [i for i, p in enumerate(PARTS) if secs[i] == s]
                    sc[s] = float(np.mean(LM[ps] - pred[ps]))
                best = (rms, float(a), sc, {PARTS[i]: M9[pmap[i]] for i in range(9)})
    return best

print(f"\n{'─'*96}\n2. 扇區標度擬合 (單調扇區內指派)\n{'─'*96}")
print(f"\n{'候選':>14} {'扇區':>8} {'RMS':>9} {'α':>9} {'扇區標度 (MeV)':>34}")
print("-" * 80)

results = {}
for cname, cand in [("|Δm|", DM), ("G (Gap)", GV), ("sin(nπ/88)", np.array([math.sin(n*math.pi/88) for n in M9]))]:
    for sname, smap in [("3 (L/U/D)", SECTOR3), ("2 (L/Q)", SECTOR2), ("1 (全部)", {p:"X" for p in PARTS})]:
        rms, a, scales, _ = fit_sector(cand, smap)
        results[f"{cname}|{sname}"] = (rms, a, scales)
        sc = " ".join(f"{k}={math.exp(v):.4g}" for k, v in sorted(scales.items()))
        print(f"{cname:>14} {sname:>8} {rms:>9.4f} {a:>9.4f} {sc:>34}")

print(f"\n★ 對照: 無扇區 2-參數擬合 (docs/25) = 0.5873 | sin 譜 = 0.8028 | 上限 3.8588")
best = min(results.items(), key=lambda kv: kv[1][0])
print(f"★ 本輪最佳: {best[0]}  RMS = {best[1][0]:.4f}  α = {best[1][1]:.4f}")

# ── 扇區標度比值 ──
print(f"\n{'─'*96}\n3. ★ 扇區標度比值 (對照「輕子 vs 夸克差 4 個數量級」)\n{'─'*96}")
for k, (rms, a, scales) in sorted(results.items()):
    if len(scales) >= 2:
        sv = {kk: math.exp(vv) for kk, vv in scales.items()}
        mx, mn = max(sv.values()), min(sv.values())
        print(f"  {k:>18}: 標度比 max/min = {mx/mn:.4g}   ({', '.join(f'{kk}={vv:.4g}' for kk, vv in sorted(sv.items()))})")

with open(OUT/"46_sector_scale.json", "w") as f:
    json.dump({"range_check": {str(a): float((DM.max()/DM.min())**a) for a in [1.0, ph2, 2.0, 3.0]},
               "fits": {k: {"rms": v[0], "alpha": v[1],
                            "scales": {kk: float(math.exp(vv)) for kk, vv in v[2].items()}}
                        for k, v in results.items()},
               "reference": {"no_sector": 0.5873, "sin": 0.8028, "upper": 3.8588}},
              f, ensure_ascii=False, indent=2)
print(f"\n✅ 寫入 data/46_sector_scale.json")