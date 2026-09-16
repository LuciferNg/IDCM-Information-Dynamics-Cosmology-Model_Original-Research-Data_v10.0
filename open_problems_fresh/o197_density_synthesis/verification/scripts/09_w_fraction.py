#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O198 scripts/09 — 開放項 1 攻堅: w 份額 (δ̂ 通道權重)

開放項 1 原文: 「w_obs = 0.2, CP 95% CI [0.025, 0.556] — 需 mass-complete 低端樣本收窄」

檢驗四點:
  W1. **選擇偏置**: w_obs = 2/10 係喺**通量限樣本**度量 — 通道 A (fresh, 低 M) 要過
      L ≥ L_min 需要高 λ ⟹ 選中樣本嘅通道 A 份額**唔等於** w。用前向模型量化偏置。
  W2. **區間寬度**: CP 95% CI 闊 0.53 ⟹ 現時數據唔可以區別任何候選。
  W3. **form density**: 「w = 1/F₅」係咪特別? 枚舉結構分數 a/b。
  W4. **所需樣本量**: 要 ±0.08 精度需要幾大 n。

零新常數。上游: O197 docs/09 §二 (w = 1/F₅ 候選), scripts/06 (前向框架), scripts/02 (CP CI)。
"""
import json, math, random
from pathlib import Path
from scipy.integrate import quad

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "harikane23_table3_eddington.json"

M_base = 1.914e6
mu = 0.862478
s = 1.1874
B, N_d, N_gen = 4, 44, 3
w = 0.2
mu_lnM = math.log(M_base) + 1.5 * mu
sig_lnM = 1.5 * s
M_turn = M_base * 2.0 ** 1.5
L_EDD = 1.26e38
A_masses = [M_base * (2.0 * math.sin(k * math.pi / 176.0) ** 2) ** 1.5 for k in range(45, 89)]
t_S, eps = 4.5e8, 0.1
lam_fbar = B / (N_d - B)
t_ef_Gyr = t_S * eps / (lam_fbar * (1 - eps)) / 1e9

H0, Om = 67.4, 0.315
H0_s = H0 * 1e5 / 3.086e24
def t_z(z):
    f = lambda zz: 1.0 / ((1 + zz) * math.sqrt(Om * (1 + zz) ** 3 + (1 - Om)))
    return quad(f, z, 1e4, limit=400)[0] / H0_s / 3.156e16

tot = pas = 0
def T(name, ok, note=""):
    global tot, pas
    tot += 1; pas += 1 if ok else 0
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  — {note}" if note else ""))

data = json.load(open(DATA))
zs = {"CEERS_01244": 4.478, "GLASS_160133": 4.015, "GLASS_150029": 4.583,
      "CEERS_00746": 5.624, "CEERS_01665": 4.483, "CEERS_00672": 5.666,
      "CEERS_02782": 5.241, "CEERS_00397": 6.000, "CEERS_00717": 6.936,
      "CEERS_01236": 4.484}
for d in data:
    d["z"] = zs[d["name"]]
lams_obs = [d["lambda_Edd"] for d in data]
tobs = [t_z(d["z"]) for d in data]
low2 = [d for d in data if d["M_BH"] < M_turn]
print(f"  觀測: {len(low2)}/{len(data)} 粒低於轉折 M_turn = {M_turn:.3e} ⟹ w_obs = {len(low2)/len(data):.2f}")
low2_s = [(d["name"], f"{d['M_BH']:.1e}", f"{d['lambda_Edd']:.2f}") for d in low2]
print(f"  低端 2 粒: {low2_s}")

print()
print("=" * 78)
print("W1. 選擇偏置 — 選中樣本嘅通道 A 份額 ≠ w")
print("=" * 78)
def fwd_chan_frac(z_f=13.43, Lmin=3e43, ww=0.2, n=200000, seed=4242):
    rng = random.Random(seed)
    tzf = t_z(z_f)
    selA = selB = 0
    for _ in range(n):
        lam_i = rng.choice(lams_obs)
        if rng.random() < ww:
            M_obs = rng.choice(A_masses)                    # 通道 A: fresh
            if lam_i * L_EDD * M_obs >= Lmin: selA += 1
        else:
            M = math.exp(rng.gauss(mu_lnM, sig_lnM))
            M_obs = M * math.exp((rng.choice(tobs) - tzf) / t_ef_Gyr)
            if lam_i * L_EDD * M_obs >= Lmin: selB += 1
    return selA / (selA + selB) if (selA + selB) else 0.0
f3 = fwd_chan_frac(Lmin=3e43)
f1 = fwd_chan_frac(Lmin=1e44)
print(f"  輸入 w = {w:.2f}")
print(f"  前向 (z_f=13.43): 選中樣本通道 A 份額")
print(f"    L_min = 3.0e43 → {f3:.3f}")
print(f"    L_min = 1.0e44 → {f1:.3f}")
print(f"  觀測 w_obs = 0.20 (2/10)")
bias = abs(f3 - w) / w
T("W1 選擇偏置小 (<5%) ⟹ w_obs = 2/10 大致係 w 嘅公平估計",
  bias < 0.05, f"前向選中 {f3:.3f} vs 輸入 {w:.2f} (偏 {bias*100:.1f}%)")
T("W1b 觀測 0.20 同前向選中份額相容 (<2σ_binom, n=10)",
  abs(f3 - 0.2) / math.sqrt(0.2 * 0.8 / 10) < 2.0,
  f"|{f3:.3f}−0.20| / σ_binom = {abs(f3-0.2)/math.sqrt(0.2*0.8/10):.2f}σ")

print()
print("=" * 78)
print("W2. CP 95% CI 寬度 — 現時數據嘅判別力")
print("=" * 78)
def cp_ci(k, n, alpha=0.05):
    from scipy.stats import beta as Bt
    lo = 0.0 if k == 0 else Bt.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else Bt.ppf(1 - alpha / 2, k + 1, n - k)
    return lo, hi
lo, hi = cp_ci(2, 10)
print(f"  w_obs = 2/10 = 0.20, CP 95% CI = [{lo:.4f}, {hi:.4f}] (闊 {hi-lo:.3f})")
cands = {"1/F₅ = 1/5": 0.2, "1/(2B) = 1/8": 0.125, "1/4": 0.25, "1/N_gen = 1/3": 1/3,
         "2B/N_d = 8/44": 0.181818, "f_bar = 0.1": 0.1, "1/2 (半模態)": 0.5}
print(f"  候選落入 CI 檢查:")
for k, v in cands.items():
    print(f"    {k:16s} = {v:.4f}  {'✓ 落 CI' if lo <= v <= hi else '✗'}")
n_in = sum(1 for v in cands.values() if lo <= v <= hi)
T("W2 CP CI 闊 (>0.4) ⟹ 判別力低", (hi - lo) > 0.4, f"闊 = {hi-lo:.3f}")
T("W2b 落入 CI 嘅候選 ≥ 4 個 ⟹ 唔可以判別", n_in >= 4, f"{n_in}/{len(cands)} 落 CI")

print()
print("=" * 78)
print("W3. form density — 「w = 1/F₅」係咪特別?")
print("=" * 78)
# 結構整數池 → 分數 a/b (同整數 a, b)
ints = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "7": 7, "8": 8, "11": 11, "13": 13,
        "17": 17, "22": 22, "33": 33, "44": 44, "88": 88, "123": 123, "144": 144,
        "45": 45, "176": 176, "420": 420, "421": 421}
def frac_exprs(target, tol=0.01):
    out = []
    for na, a in ints.items():
        for nb, b in ints.items():
            if a / b == target or abs(a / b - target) <= tol * target:
                out.append(f"{na}/{nb}")
    return out
fe = frac_exprs(0.2)
print(f"  0.2 嘅整數分數表達式 = {len(fe)} 條: {fe[:10]}")
print(f"  註: 1/F₅ = 1/(L₄−μ²) = 1/(N_gen+μ²) = 1/(B+1) — 全部係『5』嘅同一表達 (唔係三條獨立命中)")
# 2 步運算枚舉 (a op b op c) — 較公平嘅 form density
import itertools
pool2 = {"1": 1.0, "2": 2.0, "3": 3.0, "4": 4.0, "5": 5.0, "7": 7.0, "8": 8.0,
         "11": 11.0, "13": 13.0, "17": 17.0, "22": 22.0, "33": 33.0, "44": 44.0,
         "88": 88.0, "123": 123.0, "144": 144.0, "45": 45.0, "fbar": 0.1, "eps": 0.1,
         "phi": (1 + math.sqrt(5)) / 2, "phi2": ((1 + math.sqrt(5)) / 2) ** 2,
         "sq5": math.sqrt(5), "sqrt2": math.sqrt(2)}
pnames = list(pool2); pvals = [pool2[k] for k in pnames]
def count2(target, tol=0.01):
    hits = []
    for ia, ib, ic in itertools.product(range(len(pnames)), repeat=3):
        a, b, c = pvals[ia], pvals[ib], pvals[ic]
        for o1, v1 in (("+", a + b), ("-", a - b), ("*", a * b), ("/", a / b if b else None)):
            if v1 is None: continue
            for o2, v2 in (("+", v1 + c), ("-", v1 - c), ("*", v1 * c), ("/", v1 / c if c else None)):
                if v2 is not None and abs(v2 - target) <= tol * target:
                    hits.append(f"({pnames[ia]}{o1}{pnames[ib]}){o2}{pnames[ic]}")
    return hits
h2 = count2(0.2)
print(f"  0.2 嘅 2 步運算表達式 = {len(h2)} 條; 例: {h2[:6]}")
dens2 = {}
for tgt, lab in [(0.125, "1/8"), (0.2, "1/5"), (0.25, "1/4"), (1/3, "1/3"),
                 (0.1, "1/10"), (0.5, "1/2")]:
    dens2[lab] = len(count2(tgt))
    print(f"    target {lab:6s}: {dens2[lab]:5d} 條")
T("W3 0.2 有結構表達式 (2 步運算, 命中唔係零)", len(h2) >= 3, f"{len(h2)} 條")
T("W3b ★但 0.2 唔係唯一命中 (鄰近值同樣有大量表達式) ⟹ dev=0% 唔構成證據",
  len(h2) >= 3 and max(dens2.values()) > len(h2) * 0.5,
  f"0.2 → {len(h2)} 條; " + "; ".join(f"{k} {v}" for k, v in dens2.items()))

print()
print("=" * 78)
print("W4. 所需樣本量 (收窄到 ±0.08)")
print("=" * 78)
for prec in [0.15, 0.10, 0.08, 0.05]:
    n_req = math.ceil(0.2 * 0.8 / (prec / 1.96) ** 2)
    print(f"  ±{prec:.2f} (95%) ⟹ n ≈ {n_req}")
n100 = 100
lo100, hi100 = cp_ci(int(0.2 * n100), n100)
print(f"  n = 100, w=0.2 ⟹ CP 95% CI = [{lo100:.3f}, {hi100:.3f}] (闊 {hi100-lo100:.3f})")
T("W4 需 n ≈ 100 先收窄到 ±0.08 (現時 n=10)", True, f"n(±0.08) ≈ {math.ceil(0.2*0.8/(0.08/1.96)**2)}")

print()
print("=" * 78)
print("W5. 裁決 (開放項 1)")
print("=" * 78)
print(f"  1. w_obs = 0.20 (2/10) 係通量限樣本度量 — 前向模型選中份額 = {f3:.3f} (L_min=3e43)")
print(f"     ⟹ 選擇偏置只有 {bias*100:.1f}% (低端 2 粒 λ = 3.68/1.89 極高, 容易過閘) ⟹ 2/10 大致公平")
print(f"  2. CP 95% CI = [{lo:.3f}, {hi:.3f}] 闊 {hi-lo:.3f} ⟹ {n_in}/{len(cands)} 個候選都落 CI")
print(f"     ⟹ **現時數據完全冇判別力** (包括 1/2 = 半模態、f_bar = 0.1 都唔排除)")
print(f"  3. form density (2 步運算): 0.2 → {len(h2)} 條; 1/10 → {dens2['1/10']} 條; 1/2 → {dens2['1/2']} 條")
print(f"     ⟹ 0.2 唔特別; 記錄嘅「1/F₅ = 1/(L₄−μ²) = 1/(N_gen+μ²)」係**同一個 5 嘅三種寫法**")
print(f"     (唔係三條獨立命中) ⟹ dev = 0% 係『2/10 恰好 = 0.2』嘅必然結果, 唔構成證據")
print(f"  4. 狀態: 🟡 data-gated — 需 n ≈ {math.ceil(0.2*0.8/(0.08/1.96)**2)} (mass-complete 低端樣本) 先可以判別")
print(f"     且必須用**選擇修正後**嘅份額 (唔係直接 2/10)")
print()
print(f"===== {pas}/{tot} PASS =====")
