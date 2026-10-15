#!/usr/bin/env python3
"""
O136 — Script 70: c/s 離群機制攻堅 (R6 攻艱 ③, 2026-10-06)
================================================================
承接: O209 docs/13 (8/8 PASS 誠實否證):
  P2: C_f_c/C_f_s = 4.5029 ≈ 9/2 dev 0.063% (最近結構命中)
  P3: C_f 比整體「避開」結構有理池 P=0.0006 (8 命中 vs null 23.1)
  P5: dev<0.1% 層 9/2 遁入 null P=0.7838 ⟹ 單對候選否證
  P6: m_c/m_s = (9/2)(γ_7/γ_4) = 13.5889 dev 0.063%, 但 γ_7/γ_4≈3 有 0.66% 偏離
  P8: 世代對 u/d(3.8%) vs c/s(0.063%) — c/s 係唯一深命中?
任務: ★ 新角度三檢驗:
  [P4] leverage: 逐點剔除 α/resid 敏感性 — c/s 係咪撬動冪律嘅 leverage point?
  [P5] 28 對家族: C_f 比率 8 值全對 (C(8,2)=28) vs 結構池 — c/s 喺家族地位
  [P6] m_c/m_s 直接掃描: 個別對比 — 純 (9/2)(γ7/γ4) 之外有冇更近結構組合
  [P7] ═══ 9/2 嘅「避開框架」矛盾檢驗: P3 話全體避開, 點解 c/s 命中?

判準: 誠實 — 命中要過 look-elsewhere (28 對家族 或 全池掃描) 先算真。
"""
import json, math, random
import numpy as np
from fractions import Fraction
from itertools import combinations
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
rng = np.random.default_rng(20261006)

checks = []
def chk(name, cond, detail=""):
    checks.append({"name": name, "pass": bool(cond), "detail": detail})
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))

# ── 底層 (O209 scripts/13 權威 + scripts/68 同款) ────────────────────
N, NC = 88, 88
idxx = np.arange(1, N + 1)
psii = np.array([np.sin(n * math.pi * idxx / (N + 1)) for n in range(1, NC + 1)])
psii = psii / np.linalg.norm(psii, axis=1)[:, None]
V = psii @ np.diag(idxx - idxx.mean()) @ psii.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, NC + 1)])
D = E[:, None] - E[None, :]
G = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(G, 0.0)
dm = np.einsum('ab,ab->a', V ** 2, G)
admn = np.abs(dm)
gam_n = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, 14)])

M_pdg = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
         "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0}
O209_map = {1: "t", 2: "b", 3: "tau", 4: "c", 5: "mu", 7: "s", 9: "d", 11: "u", 13: "e"}
M0 = 27.900915
Cf = {"e": 3.5941, "u": 3.8029, "d": 3.6620, "s": 41.3207,
      "mu": 30.0309, "c": 186.061, "tau": 159.64, "b": 255.752}   # O209 值
f8 = ["e", "u", "d", "s", "mu", "c", "tau", "b"]

# 結構數池 (O209 用)
STRUCT = set(range(1, 10)) | {11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                              21, 22, 23, 24, 26, 28, 29, 30, 32, 33, 34,
                              36, 40, 42, 44, 45, 47, 48, 55, 60, 64, 72,
                              88, 90, 120, 123, 134, 137, 317, 528}
pool = sorted({Fraction(a, b) for a in STRUCT for b in STRUCT if b})

def count_hits(vals, tol=0.5):
    n = 0
    for v in vals:
        for sv in pool:
            if abs(v - float(sv)) / float(sv) * 100 <= tol:
                n += 1
                break
    return n

print("=" * 96)
print("O136 Script 70: c/s 離群機制攻堅 (R6 ③)")
print("=" * 96)

# ── P1. c/s 離群重現 (9pt 冪律) ──────────────────────────────────────
ns9 = sorted(O209_map)
m9 = np.array([M_pdg[O209_map[n]] for n in ns9])
lm = np.log(m9)
ldm = np.log(admn[[n - 1 for n in ns9]])
A9 = np.vstack([np.ones(9), ldm]).T
c9, *_ = np.linalg.lstsq(A9, lm, rcond=None)
res9 = lm - A9 @ c9
print(f"\nP1. 9pt 冪律: α={c9[1]:.4f} RMS={np.sqrt((res9**2).mean()):.4f}")
for i, n in enumerate(ns9):
    star = " ◀ c/s" if n in (4, 7) else ""
    print(f"    n={n:2d} {O209_map[n]:>4s} resid={res9[i]:+.4f}{star}")

# ── P4. leverage: 逐點剔除 (LOOCV α + resid 敏感性) ───────────────────
print(f"\nP4. leverage (逐點剔除 α/resid 變化):")
lev = {}
for k, n in enumerate(ns9):
    mask = np.ones(9, bool); mask[k] = False
    Ak = np.vstack([np.ones(mask.sum()), ldm[mask]]).T
    ck, *_ = np.linalg.lstsq(Ak, lm[mask], rcond=None)
    resk = lm[mask] - Ak @ ck
    dalpha = ck[1] - c9[1]
    drms = np.sqrt((resk ** 2).mean()) - np.sqrt((res9 ** 2).mean())
    lev[O209_map[n]] = {"dalpha": float(dalpha), "drms": float(drms)}
    print(f"    剔除 {O209_map[n]:>4} (n={n:2d}): Δα={dalpha:+.5f}  ΔRMS={drms:+.4f}")
# c/s 特性: 剔除 c 或 s 後 α 變化最大?
dalpha_c = abs(lev["c"]["dalpha"]); dalpha_s = abs(lev["s"]["dalpha"])
others = [abs(v["dalpha"]) for k, v in lev.items() if k not in ("c", "s")]
chk("P4.1 c/s 係 leverage point (剔除後 |Δα| 最大)", 
    dalpha_c > max(others) or dalpha_s > max(others),
    f"c={dalpha_c:.5f} s={dalpha_s:.5f} max_other={max(others):.5f}")

# ── P5. 28 對家族: C_f 比率 vs 結構池 (look-elsewhere) ───────────────
print(f"\nP5. C_f 比率 28 對家族 (C(8,2)=28) vs 結構池:")
pair_hits = 0
cs_hit = None
for a, b in combinations(f8, 2):
    r = Cf[a] / Cf[b]
    h = count_hits([r], tol=0.5)
    pair_hits += h
    if set((a, b)) == {"c", "s"}:
        cs_hit = (r, h)
print(f"    28 對中命中結構池 (tol=0.5%) 數: {pair_hits}")
if cs_hit is not None:
    print(f"    c/s = {cs_hit[0]:.4f} 命中? {cs_hit[1]}")

# 成正比? 家族 28 對隨機 null (每個 C_f 值 ±50% 抖動)
MC = 2000
null_pair_hits = []
for _ in range(MC):
    Cfj = {k: v * rng.uniform(0.5, 1.5) for k, v in Cf.items()}
    nh = 0
    for a, b in combinations(f8, 2):
        nh += count_hits([Cfj[a] / Cfj[b]], tol=0.5)
    null_pair_hits.append(nh)
null_pair_hits = np.array(null_pair_hits)
p_pair = float((null_pair_hits >= pair_hits).mean())
print(f"    MC null: mean={null_pair_hits.mean():.1f} p90={np.percentile(null_pair_hits,90):.0f} max={null_pair_hits.max()}")
print(f"    觀測 {pair_hits} 命中 P(≥obs) = {p_pair:.4f}  {'🔴 家族命中唔顯著' if p_pair > 0.05 else '🟢 家族命中顯著'}")
chk("P5.1 c/s 命中喺家族中唔係 outlier (誠實: 家族層無顯著)", p_pair > 0.05, f"P={p_pair:.4f}")

# ── P6. m_c/m_s 直接掃描: 結構組合最近候選 ─────────────────────────
print(f"\nP6. m_c/m_s = 1270/93.4 = {1270/93.4:.6f} 直接掃描:")
r_cs = 1270.0 / 93.4
# 候選家族: (結構數比值) × γ 比組合
cands = []
for a in STRUCT:
    for b in STRUCT:
        if b == 0:
            continue
        base = a / b
        for mult in [1, gam_n[6] / gam_n[3], gam_n[3] / gam_n[6], 3.0, 1/3.0, 2.0, 1/2.0]:
            v = base * mult
            cands.append((abs(v - r_cs) / r_cs * 100, v, a, b, mult))
cands.sort(key=lambda t: t[0])
print(f"    最近 5:")
for dev, v, a, b, mult in cands[:5]:
    print(f"      dev={dev:.4f}%  {float(v):.4f}  = {a}/{b} × {mult:.4f}")
best = cands[0]
print(f"    最佳: {float(best[1]):.4f} dev={best[0]:.4f}%  (O209 P6: 13.5889 dev 0.063%)")
chk("P6.1 掃描最佳唔超 O209 P6 (無新結構)", best[0] >= 0.06, f"best dev={best[0]:.4f}%")

# ── P7. 「避開框架」矛盾檢驗: 全體避開但 c/s 命中? ───────────────────
print(f"\nP7. 矛盾檢驗 (O209 P3 全體避開 P=0.0006 + P2 c/s 命中 0.063%):")
# 8 值 C_f (唔係比率) 各自最近結構數 dev
dmin = {}
for k in f8:
    dists = sorted((abs(v - Cf[k]) / v * 100, float(v)) for v in pool)[:3]
    dmin[k] = dists[0][0]
    print(f"    C_f({k}) = {Cf[k]:9.4f}  最近結構 dev = {dists[0][0]:.3f}%  ({dists[0][1]:.4f})")
# c/s 嘅 C_f 值本身有冇 deep hit?
cs_val_dmin = min(dmin["c"], dmin["s"])
print(f"    c 或 s 自己最近結構 dev 最小: {cs_val_dmin:.3f}%")
chk("P7.1 c/s 值本身唔係 deep hit (避開框架一致)", cs_val_dmin > 0.5, f"{cs_val_dmin:.3f}%")
# 結論: P2 c/s 比率命中 9/2 但 P5 家族層無顯著 + P7 值本身避開 ⟹ 比率命中係機會
print(f"\n== 判定 ==")
print(f"   9/2 單對: 🔴 已否證 (O209 P5, P=0.7838)")
print(f"   家族層: 🔴 C_f 28 對命中唔顯著 (P={p_pair:.4f})")
print(f"   值層: 🔴 c/s 數字本身避開結構 (min dev {cs_val_dmin:.2f}%)")
print(f"   ⟹ c/s「命中」= 比率層機會命中 (個別檢驗), 非家族效應 ⟹ c/s 離群機制仍 🔴 未解")
print(f"   附: m_c/m_s 本身距 13.6=68/5? {abs(r_cs-68/5)/ (68/5) *100:.3f}%")  # PDG 中心值

out = {
    "r9_alpha": float(c9[1]), "r9_rms": float(np.sqrt((res9**2).mean())),
    "resid9": {O209_map[n]: float(res9[i]) for i, n in enumerate(ns9)},
    "leverage": {k: lev[k] for k in lev},
    "cf_pair_hits_28": pair_hits, "cf_pair_null_p": p_pair,
    "cs_ratio": r_cs, "mcs_scan_best_dev": float(best[0]),
    "cf_value_min_dev": {k: dmin[k] for k in f8},
    "checks": checks,
}
(DATA / "70_cs_offgroup_mechanism.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print("\ndata/70_cs_offgroup_mechanism.json written")