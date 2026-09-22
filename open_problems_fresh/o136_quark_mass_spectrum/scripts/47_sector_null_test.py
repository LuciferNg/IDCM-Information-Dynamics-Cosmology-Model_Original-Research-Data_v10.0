#!/usr/bin/env python3
"""
O136 — Script 47: 扇區標度 — null test + 結構比值檢驗
================================================================
Script 46 結果 (★ 突破):
  sin(nπ/88) + 3 扇區標度 (L/U/D) → RMS = 0.3549  (vs 無扇區 1.1178, 改善 3.1×)
  |Δm|       + 3 扇區標度 (L/U/D) → RMS = 0.3885  (vs 無扇區 0.5878)

⚠️ 多 3 個參數 → 必須排除過擬合。本 script:
  (A) 最佳配對 + 扇區指派 (結構檢驗: 扇區內模式集合有意義嗎?)
  (B) ★ null test: 隨機扇區標籤 (同尺寸 3/3/3) 嘅 RMS 分佈 → p 值
  (C) ★ null test 2: 隨機質量 (保留扇區尺寸) → 分佈
  (D) 扇區標度比值 vs 結構常數字典 (L₄L₅−μ²=75, N_gen=3, ...)
"""
import numpy as np, math, json, itertools, random
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"
phi = (1+math.sqrt(5))/2; ph2 = phi**2
L4, L5, ND, B_, DIMC, MU2 = 7, 11, 44, 4, 3, 2.0

MASS = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
SECTOR3 = {"e":"L","mu":"L","tau":"L","u":"U","c":"U","t":"U","d":"D","s":"D","b":"D"}
PARTS = ["e","mu","tau","u","c","t","d","s","b"]
LM = np.array([math.log(MASS[p]) for p in PARTS])
M9 = [1,2,3,4,5,7,9,11,13]
SIN = np.array([math.sin(n*math.pi/88) for n in M9])

# |Δm|
Nc = 44
x = np.arange(1, Nc+1, dtype=float)
Psi = np.zeros((Nc, Nc))
for n in range(1, Nc+1):
    Psi[:, n-1] = np.sin(n*math.pi*x/(Nc+1))
for n in range(Nc):
    Psi[:, n] /= np.linalg.norm(Psi[:, n])
V = Psi.T @ np.diag(x - x.mean()) @ Psi
E = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1, 45)])
DM = []
for n in M9:
    t = 0.0
    for m in range(Nc):
        if m == n-1 or (m-(n-1)) % 2 == 0: continue
        dE = E[n-1]-E[m]
        if abs(dE) < 1e-12: continue
        t += V[n-1, m]**2/dE
    DM.append(abs(t))
DM = np.array(DM)

def fit_sector(cand, secs, alpha_grid=None):
    if alpha_grid is None: alpha_grid = np.linspace(0.05, 8.0, 160)
    LC = np.log(cand)
    names = sorted(set(secs))
    sizes = {s: secs.count(s) for s in names}
    best = (9e9, None, None, None)
    def assignments(nm, pos):
        if len(nm) == 1: yield {nm[0]: list(pos)}; return
        s = nm[0]; k = sizes[s]
        for c in itertools.combinations(pos, k):
            rest = [p for p in pos if p not in c]
            for sub in assignments(nm[1:], rest): yield {s: list(c), **sub}
    for asg in assignments(names, list(range(9))):
        pmap = {}
        for s in names:
            ps = sorted([i for i, p in enumerate(PARTS) if secs[i] == s], key=lambda i: -MASS[PARTS[i]])
            cs = sorted(asg[s], key=lambda k: -LC[k])
            for pp, cc in zip(ps, cs): pmap[pp] = cc
        base = np.array([LC[pmap[i]] for i in range(9)])
        for a in alpha_grid:
            pred = a*base; res = LM - pred
            for s in names:
                ps = [i for i, p in enumerate(PARTS) if secs[i] == s]
                res[ps] = res[ps] - res[ps].mean()
            rms = float(np.sqrt(np.mean(res**2)))
            if rms < best[0]:
                sc = {s: float(np.mean(LM[[i for i, p in enumerate(PARTS) if secs[i] == s]] -
                                         pred[[i for i, p in enumerate(PARTS) if secs[i] == s]]))
                      for s in names}
                best = (rms, float(a), sc, {PARTS[i]: M9[pmap[i]] for i in range(9)})
    return best

print("=" * 96)
print("O136 Script 47: 扇區標度 null test + 結構比值")
print("=" * 96)

# ═══ (A) 最佳解 ══════════════════════════════════════
print(f"\n{'─'*96}\n(A) 最佳配對 + 扇區指派\n{'─'*96}")
best = {}
for cname, cand in [("sin(nπ/88)", SIN), ("|Δm|", DM)]:
    rms, a, sc, asg = fit_sector(cand, [SECTOR3[p] for p in PARTS])
    best[cname] = (rms, a, sc, asg)
    print(f"\n★ {cname}: RMS = {rms:.4f}, α = {a:.4f}")
    for s in ["L", "U", "D"]:
        ps = [p for p in PARTS if SECTOR3[p] == s]
        print(f"   扇區 {s}: " + ", ".join(f"{p}↔n={asg[p]}" for p in sorted(ps, key=lambda q: -MASS[q])))
    print(f"   標度: " + ", ".join(f"{s}={math.exp(sc[s]):.4g} MeV" for s in ["L","U","D"]))

# ═══ (B) ★ null test 1: 隨機扇區標籤 ═════════════════
print(f"\n{'─'*96}\n(B) ★ null test 1: 隨機扇區標籤 (尺寸固定 3/3/3, N=300)\n{'─'*96}")
rng = random.Random(20260920)
base_labels = [SECTOR3[p] for p in PARTS]
null1 = {"sin(nπ/88)": [], "|Δm|": []}
for _ in range(300):
    lab = base_labels[:]; rng.shuffle(lab)
    for cname, cand in [("sin(nπ/88)", SIN), ("|Δm|", DM)]:
        r, _, _, _ = fit_sector(cand, lab, np.linspace(0.05, 8.0, 40))
        null1[cname].append(r)
for cname in null1:
    v = np.array(null1[cname]); obs = best[cname][0]
    p = float((v <= obs).mean())
    print(f"  {cname:>12}: 觀測 RMS = {obs:.4f} | null 中位 = {np.median(v):.4f}, "
          f"min = {v.min():.4f} | P(null ≤ 觀測) = {p:.4f}  {'🟢 顯著' if p < 0.05 else '🔴 唔顯著'}")

# ═══ (C) ★ null test 2: 隨機質量 (扇區固定) ═══════════
print(f"\n{'─'*96}\n(C) ★ null test 2: 隨機質量 (扇區固定 3/3/3, N=300)\n{'─'*96}")
mvals = np.array([math.log(MASS[p]) for p in PARTS])

def fit_sector_LM(cand, secs, LMv, alpha_grid):
    LC = np.log(cand); names = sorted(set(secs)); sizes = {s: secs.count(s) for s in names}
    bst = 9e9
    def assignments(nm, pos):
        if len(nm) == 1: yield {nm[0]: list(pos)}; return
        s = nm[0]; k = sizes[s]
        for c in itertools.combinations(pos, k):
            rest = [p for p in pos if p not in c]
            for sub in assignments(nm[1:], rest): yield {s: list(c), **sub}
    for asg in assignments(names, list(range(9))):
        pmap = {}
        for s in names:
            ps = sorted([i for i, p in enumerate(PARTS) if secs[i] == s], key=lambda i: -LMv[i])
            cs = sorted(asg[s], key=lambda k: -LC[k])
            for pp, cc in zip(ps, cs): pmap[pp] = cc
        base = np.array([LC[pmap[i]] for i in range(9)])
        for a in alpha_grid:
            pred = a*base; res = LMv - pred
            for s in names:
                ps = [i for i, p in enumerate(PARTS) if secs[i] == s]
                res[ps] = res[ps] - res[ps].mean()
            r = float(np.sqrt(np.mean(res**2)))
            if r < bst: bst = r
    return bst

null2 = {"sin(nπ/88)": [], "|Δm|": []}
for _ in range(300):
    perm = list(range(9)); rng.shuffle(perm)
    LMp = mvals[perm]
    for cname, cand in [("sin(nπ/88)", SIN), ("|Δm|", DM)]:
        null2[cname].append(fit_sector_LM(cand, [SECTOR3[p] for p in PARTS], LMp, np.linspace(0.05, 8.0, 40)))
for cname in null2:
    v = np.array(null2[cname]); obs = best[cname][0]
    p = float((v <= obs).mean())
    print(f"  {cname:>12}: 觀測 RMS = {obs:.4f} | null 中位 = {np.median(v):.4f}, "
          f"min = {v.min():.4f} | P(null ≤ 觀測) = {p:.4f}  {'🟢 顯著' if p < 0.05 else '🔴 唔顯著'}")

# ═══ (D) 結構比值 ════════════════════════════════════
print(f"\n{'─'*96}\n(D) ★ 扇區標度比值 vs 結構常數字典\n{'─'*96}")
DICT = {"L₄L₅−μ² = 75": 75, "N_gen = 3": 3, "B = 4": 4, "L₆ = 18": 18, "Σγ = 90": 90,
        "N_d = 44": 44, "F₇ = 13": 13, "L₇ = 29": 29, "F₉ = 34": 34, "μ² = 2": 2,
        "φ² = 2.618": ph2, "φ³ = 4.236": phi**3, "φ⁴ = 6.854": phi**4, "φ⁵ = 11.09": phi**5,
        "φ⁶ = 17.94": phi**6, "φ⁷ = 29.03": phi**7, "φ⁸ = 46.98": phi**8,
        "N_d−B = 40": 40, "L₄L₅ = 77": 77, "2N_d = 88": 88, "C(9,2) = 36": 36}
for cname, (rms, a, sc, asg) in best.items():
    sv = {s: math.exp(sc[s]) for s in sc}
    print(f"\n  ★ {cname} (RMS {rms:.4f}):")
    for pair in [("U","L"), ("U","D"), ("D","L")]:
        r = sv[pair[0]]/sv[pair[1]]
        hits = [(k, v, 100*abs(r-v)/v) for k, v in DICT.items() if abs(r-v)/v < 0.15]
        hits.sort(key=lambda z: z[2])
        hs = " | ".join(f"{k} (dev {d:.2f}%)" for k, v, d in hits[:3]) or "—"
        print(f"     {pair[0]}/{pair[1]} = {r:>10.4f}   {hs}")

with open(OUT/"47_sector_null_test.json", "w") as f:
    json.dump({"best": {k: {"rms": v[0], "alpha": v[1],
                            "scales": {s: math.exp(v[2][s]) for s in v[2]},
                            "assignment": v[3]} for k, v in best.items()},
               "null1_random_labels": {k: {"median": float(np.median(v)), "min": float(np.min(v)),
                                           "p": float((np.array(v) <= best[k][0]).mean())} for k, v in null1.items()},
               "null2_random_masses": {k: {"median": float(np.median(v)), "min": float(np.min(v)),
                                           "p": float((np.array(v) <= best[k][0]).mean())} for k, v in null2.items()},
               }, f, ensure_ascii=False, indent=2)
print(f"\n✅ 寫入 data/47_sector_null_test.json")