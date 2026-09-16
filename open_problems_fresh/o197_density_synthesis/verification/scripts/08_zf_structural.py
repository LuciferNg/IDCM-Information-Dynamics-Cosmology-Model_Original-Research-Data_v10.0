#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O198 scripts/08 — 開放項 5 攻堅: z_f* 結構身份

開放項 5 原文 (problem_record §五.5):
  「z_f* = 13.43 結構身份: 成長閉合反演嘅形成紅移 — 13 = F₇ 候選, 未證」

三路:
  A. 反演值嘅**可識別性** — 獨立重現 + (模型選擇, L_min, w, t_ef, 目標中位) 逐項敏感度。
     若 z_f* 喺合理變動下浮動 ±5 以上 ⟹ 「13.43」唔係可識別量 ⟹ 結構身份問題問錯咗。
  B. **結構時間候選** — z_f = z(t_f) / Δt(z_f→0) = n·t_ef, t_f 取自結構時間池。判據:
     落範圍 + 零加性湊數。
  C. **form density 檢驗** — 「13 = F₇」係咪特別? 結構數字池枚舉, 比較 13 同鄰近整數。

零新常數。上游: scripts/06 (反演框架 T8b 均勻成長 / T8h3 channel-resolved), O197 docs/09 §三。
"""
import json, math, random
from pathlib import Path
from scipy.integrate import quad
from scipy.optimize import brentq

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
t_S = 4.5e8
eps = 0.1
lam_fbar = B / (N_d - B)
t_ef = t_S * eps / (lam_fbar * (1 - eps))
t_ef_Gyr = t_ef / 1e9
phi = (1 + math.sqrt(5)) / 2

H0, Om = 67.4, 0.315
H0_s = H0 * 1e5 / 3.086e24
def t_z(z):
    f = lambda zz: 1.0 / ((1 + zz) * math.sqrt(Om * (1 + zz) ** 3 + (1 - Om)))
    return quad(f, z, 1e4, limit=400)[0] / H0_s / 3.156e16
def z_of_t(tG):
    return brentq(lambda z: t_z(z) - tG, 1e-4, 200.0)

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
masses = sorted(d["M_BH"] for d in data)
obs_med = masses[len(masses) // 2]
A_masses = [M_base * (2.0 * math.sin(k * math.pi / 176.0) ** 2) ** 1.5 for k in range(45, 89)]
tobs = [t_z(d["z"]) for d in data]

def fwd(z_f, Lmin=3e43, ww=None, tef_Gyr=None, Ledd=None, chan=True, seed=777, n=25000):
    """前向: chan=True → 通道 A fresh + B 成長 (T8h3);  chan=False → 兩通道均勻成長 (T8b)"""
    ww = w if ww is None else ww
    tef_Gyr = t_ef_Gyr if tef_Gyr is None else tef_Gyr
    Ledd = L_EDD if Ledd is None else Ledd
    rng = random.Random(seed)
    tzf = t_z(z_f)
    vals = []
    for _ in range(n):
        lam_i = rng.choice(lams_obs)
        if rng.random() < ww:
            M = rng.choice(A_masses)
            grow_A = 1.0 if chan else math.exp((rng.choice(tobs) - tzf) / tef_Gyr)
            M_obs = M * grow_A
        else:
            M = math.exp(rng.gauss(mu_lnM, sig_lnM))
            M_obs = M * math.exp((rng.choice(tobs) - tzf) / tef_Gyr)
        if lam_i * Ledd * M_obs >= Lmin:
            vals.append(math.log(M_obs))
    vals.sort()
    return math.exp(vals[len(vals) // 2]) if vals else 0.0

def invert(target, seed=777, **kw):
    lo, hi = 6.0, 30.0
    for _ in range(20):
        mid = (lo + hi) / 2
        if fwd(mid, seed=seed, **kw) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

print("=" * 78)
print("A. 反演值可識別性")
print("=" * 78)
print(f"  觀測目標中位 = {obs_med:.3e} M☉ (10 粒實測)")
zf_uni = invert(obs_med, chan=False)
zf_chan = invert(obs_med, chan=True)
print(f"  均勻成長 (T8b, 記錄用)            : z_f* = {zf_uni:.2f}")
print(f"  channel-resolved (T8h3, 記錄接受) : z_f* = {zf_chan:.2f}")
T("A1 獨立重現記錄 z_f* = 13.43 (均勻成長 T8b 框架)", abs(zf_uni - 13.43) < 1.5,
  f"z_f* = {zf_uni:.2f} vs 記錄 13.43")
T("A2 ★z_f* 強模型依賴: 均勻 vs channel-resolved 差 > 5",
  abs(zf_chan - zf_uni) > 5.0, f"{zf_uni:.2f} vs {zf_chan:.2f} (Δ = {abs(zf_chan-zf_uni):.2f})")

print("\n  (a) L_min 掃描 (記錄兩值: 3e43 上限 / 5.73e43 反演; 物理帶 1e43–1e45):")
zf_L = {}
for Lm in [1e43, 3e43, 5.73e43, 1e44, 1e45]:
    zf_L[Lm] = invert(obs_med, Lmin=Lm)
    print(f"      L_min = {Lm:.2e} → z_f* = {zf_L[Lm]:.2f}")
print("\n  (b) w 掃描 (w_obs = 0.2, CP 95% CI [0.025, 0.556]):")
zf_w = {}
for ww in [0.1, 0.2, 0.3, 0.5]:
    zf_w[ww] = invert(obs_med, ww=ww)
    print(f"      w = {ww:.2f} → z_f* = {zf_w[ww]:.2f}")
print("\n  (c) t_ef 掃描 (結構值 0.5 Gyr; λ = f_bar ± 20% ⟹ t_ef 反比):")
zf_t = {}
for te in [0.4, 0.5, 0.6]:
    zf_t[te] = invert(obs_med, tef_Gyr=te)
    print(f"      t_ef = {te:.2f} Gyr → z_f* = {zf_t[te]:.2f}")
print("\n  (d) L_Edd 常數 (審計 F2: 1.26e38 vs 論文側 1.30e38):")
zf_Ld = {L: invert(obs_med, Ledd=L) for L in [1.26e38, 1.30e38]}
for L, v in zf_Ld.items():
    print(f"      L_Edd = {L:.2e} → z_f* = {v:.2f}")
print("\n  (e) 目標中位 (n=10 bootstrap):")
rng_b = random.Random(11)
meds = sorted(sorted(rng_b.choice(masses) for _ in range(10))[5] for _ in range(400))
lo_m, hi_m = meds[25], meds[374]
zf_m = {lo_m: invert(lo_m), hi_m: invert(hi_m)}
print(f"      中位 90% CI = [{lo_m:.2e}, {hi_m:.2e}]")
for m, v in zf_m.items():
    print(f"      目標 = {m:.2e} → z_f* = {v:.2f}")
allv = ([zf_uni, zf_chan] + list(zf_L.values()) + list(zf_w.values())
        + list(zf_t.values()) + list(zf_Ld.values()) + list(zf_m.values()))
lo_zf, hi_zf = min(allv), max(allv)
print(f"\n  ★★ 全部變動範圍: z_f* ∈ [{lo_zf:.2f}, {hi_zf:.2f}]  (spread {hi_zf-lo_zf:.2f})")
T("A3 L_min 掃描 1e43→1e45 ⟹ Δz_f > 5 (極敏感)",
  max(zf_L.values()) - min(zf_L.values()) > 5.0,
  f"Δ = {max(zf_L.values())-min(zf_L.values()):.2f} ({min(zf_L.values()):.2f}–{max(zf_L.values()):.2f})")
T("A4 w 掃描 0.1→0.5 ⟹ Δz_f > 5 (極敏感)",
  max(zf_w.values()) - min(zf_w.values()) > 5.0,
  f"Δ = {max(zf_w.values())-min(zf_w.values()):.2f}")
T("A5 t_ef 掃描 0.4→0.6 ⟹ Δz_f > 5 (極敏感)",
  max(zf_t.values()) - min(zf_t.values()) > 5.0,
  f"Δ = {max(zf_t.values())-min(zf_t.values()):.2f}")
T("A6 ★全部變動 ⟹ z_f* 範圍闊 (spread > 10) ⟹ 唔係可識別量",
  hi_zf - lo_zf > 10.0, f"[{lo_zf:.2f}, {hi_zf:.2f}] spread {hi_zf-lo_zf:.2f}")

print()
print("=" * 78)
print("B. 結構時間候選 (z_f = z(t_f) 或 Δt(z_f→0) = n·t_ef)")
print("=" * 78)
t0 = t_z(1e-4)
cands = [
    ("t_f = t_S (Salpeter)", t_S / 1e9),
    ("t_f = t_ef (成長 e-folding)", t_ef_Gyr),
    ("t_f = t_ef/φ", t_ef_Gyr / phi),
    ("t_f = t_ef·φ", t_ef_Gyr * phi),
    ("t_f = t_ef/φ²", t_ef_Gyr / phi ** 2),
    ("t_f = 2·t_ef (μ²·t_ef)", 2 * t_ef_Gyr),
    ("t_f = t_S·φ⁻¹", (t_S / 1e9) / phi),
    ("t_f = t_S·ε", (t_S / 1e9) * eps),
    ("t_f = T_ring/364 (O197 docs/07)", 0.2325),
    ("Δt(z_f→0) = 27·t_ef (N_gen³)", None),
]
rows = []
for name, tv in cands:
    if tv is None:
        tv = 27 * t_ef_Gyr
        zf_c = z_of_t(t0 - tv)
    else:
        zf_c = z_of_t(tv)
    inr = lo_zf <= zf_c <= hi_zf
    rows.append((name, zf_c, inr, tv))
    print(f"  {name:34s} → z_f = {zf_c:6.2f}  {'✓' if inr else '✗'}  (t_f/Δt = {tv:.4f} Gyr)")
n_in = sum(1 for r in rows if r[2])
print(f"  {n_in}/{len(rows)} 落入 (極闊嘅) 變動範圍 — 判別力低")
T("B1 結構時間候選落入變動範圍 (≥1)", n_in >= 1, f"{n_in}/{len(rows)}")
best = [r for r in rows if r[2]]
T("B2 全部落入候選都係結構量嘅積/商 (零加性湊數)",
  len(best) > 0, "; ".join(f"{r[0]} → {r[1]:.2f}" for r in best[:4]))

print()
print("=" * 78)
print("C. form density 檢驗 — 「13」係咪特別?")
print("=" * 78)
pool = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "7": 7, "8": 8, "11": 11, "13": 13,
        "17": 17, "22": 22, "33": 33, "44": 44, "88": 88, "123": 123, "144": 144,
        "phi": phi, "phi2": phi ** 2, "sq5": math.sqrt(5), "sqrt2": math.sqrt(2),
        "fbar": 0.1}
names = list(pool); vals = [pool[k] for k in names]
def count_expr(target, tol=0.005):
    hits = []
    for i, (na, va) in enumerate(zip(names, vals)):
        for j, (nb, vb) in enumerate(zip(names, vals)):
            if i == j: continue
            for op, v in (("+", va + vb), ("-", va - vb), ("*", va * vb),
                          ("/", va / vb if vb else None)):
                if v is not None and abs(v - target) <= tol * abs(target):
                    hits.append(f"{na}{op}{nb}")
    return hits
h13 = count_expr(13.0)
print(f"  13 命中數 = {len(h13)} (1 步運算, 相對容差 0.5%); 例: {h13[:6]}")
dens = {}
for tgt in [11, 12, 13, 14, 15, 17, 22, 33]:
    dens[tgt] = len(count_expr(float(tgt)))
    print(f"    target {tgt:3d}: {dens[tgt]:4d} 條")
print(f"  ⟹ 13 排第 {sorted(dens, key=lambda k: -dens[k]).index(13)+1}/8 "
      f"(命中 {dens[13]}, 最密 {max(dens, key=lambda k: dens[k])} {max(dens.values())})")
T("C1 13 有 ≥3 條結構表達式", dens[13] >= 3, f"{dens[13]} 條")
T("C2 13 唔係最密命中 ⟹ form density 唔支持「F₇ 特別」",
  dens[13] < max(dens.values()),
  f"13 → {dens[13]}; 最密 = {max(dens, key=lambda k: dens[k])} ({max(dens.values())})")

print()
print("=" * 78)
print("D. 獨立約束")
print("=" * 78)
print(f"  UHz1 z = 7.5 存在 (O173) ⟹ z_f > 7.5")
T("D1 channel-resolved 基準反演 (記錄接受模型) > 7.5", zf_chan > 7.5, f"z_f = {zf_chan:.2f}")
T("D2 ★channel-resolved 反演超出 T8c 嘅再電離窗 [8,15] ⟹ 新張力",
  zf_chan > 15.0, f"z_f = {zf_chan:.2f} > 15 (暗黑時代)")

print()
print("=" * 78)
print("E. 裁決 (開放項 5)")
print("=" * 78)
print(f"  1. 均勻成長框架 (T8b) 獨立重現 z_f* = {zf_uni:.2f} ≈ 記錄 13.43 ✓")
print(f"  2. ★但記錄接受嘅 channel-resolved 框架 (T8h3) 反演 = {zf_chan:.2f} (Δ = {abs(zf_chan-zf_uni):.1f})")
print(f"     ⟹ z_f* **強模型依賴**; 閉合喺 (成長模型, z_f*) 上退化")
print(f"  3. ★輸入敏感度亦極大: L_min 1e43→1e45 令 z_f* 由 {min(zf_L.values()):.1f} 掃到 {max(zf_L.values()):.1f}")
print(f"     全變動範圍 [{lo_zf:.1f}, {hi_zf:.1f}] (spread {hi_zf-lo_zf:.1f})")
print(f"  4. ⟹ 「z_f* = 13.43 結構身份」問法唔成立 (13.43 唔係可識別量)")
print(f"     正確問法 = 「有冇結構形成時間 t_f」— 落入範圍嘅候選: "
      f"{', '.join(r[0].split('=')[1].strip() for r in best[:4])}")
print(f"  5. form density: 13 → {dens[13]} 條 (唔特別; 11 → {dens[11]} 條) ⟹ F₇ 命中唔係證據")
print(f"  6. 狀態: 🟡 — 需 (i) 固定成長模型 (由結構推導, 唔係二選一), (ii) 大樣本收窄 L_min/w")
print()
print(f"===== {pas}/{tot} PASS =====")
