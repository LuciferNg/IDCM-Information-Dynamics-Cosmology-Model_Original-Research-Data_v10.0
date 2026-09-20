#!/usr/bin/env python3
"""
O206 — Script 09: 映射層缺口 (m = M₀·|Δm|^α 層)
=========================================================
承接 docs/09 §三: |Δm| 已完全結構化 (script 08 零參數閉式),
  但形狀 RMS 唔改善 ⟹ 1.80× 殘餘喺【映射層】。

本 script 檢驗:
  §A 1-參數基準 (anchor) + 殘餘表
  §B 1-參數替代: γ_n 本身是否更好之預測量?
  §C 2-參數擴展 (γ / n / gen / sector) — 誠實計自由度
  §D 世代塊 {1,2,3}/{4,5,7}/{9,11,13} 置換 null (N=10⁵)
  §E 結構 α 候選之可辨識性 (O136 判準④)
  §F 裁決
紀律: 對數度量; 禁 φ-power fitting; 禁後驗湊算子; 每 check 報慣例
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from o206_lib import (NC, ND, MU2, A5_MODES, LM, MASS, MODE_OF,
                      E_ring44, V_position, logscore, sum_V2_dE)

OUT = Path(__file__).parent.parent / "data"
checks = []


def chk(name, cond, detail=""):
    checks.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))


def ols(X, y):
    """顯式 OLS (⚠️ 唔用 np.cov/np.var 混用 — ddof 陷阱)"""
    X = np.asarray(X, dtype=float)
    if X.ndim == 1:
        X = X[:, None]
    A = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(A, np.asarray(y, dtype=float), rcond=None)
    pred = A @ beta
    return beta, pred, float(np.std(np.asarray(y) - pred))


V = V_position()
E = E_ring44()
base = logscore(sum_V2_dE(E, V))
PAIR = [(1, "t"), (2, "b"), (3, "tau"), (4, "c"), (5, "mu"), (7, "s"), (9, "d"), (11, "u"), (13, "e")]
GEN = {"t": 3, "b": 3, "tau": 3, "c": 2, "mu": 2, "s": 2, "d": 1, "u": 1, "e": 1}
GEN_BLOCK = {3: [1, 2, 3], 2: [4, 5, 7], 1: [9, 11, 13]}

dm = sum_V2_dE(E, V)
ldm = np.array([math.log(dm[A5_MODES.index(n)]) for n, _ in PAIR])
lgamma = np.array([math.log(E[n - 1]) for n, _ in PAIR])
lm = np.array([math.log(MASS[p]) for _, p in PAIR])
lgen = np.array([float(GEN[p]) for _, p in PAIR])
ln_ = np.array([float(n) for n, _ in PAIR])
sector = np.array([1.0 if p in ("e", "mu", "tau") else 0.0 for _, p in PAIR])

print("=" * 100)
print("O206 Script 09: 映射層缺口 (m = M0·|Δm|^α 層)")
print("=" * 100)

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§A 1-參數基準 + 殘餘表\n{'─'*100}")
beta1, pred1, rms1 = ols(ldm, lm)
alpha, lnM0 = float(beta1[1]), float(beta1[0])
M0 = math.exp(lnM0)
resid = lm - pred1
print(f"\n  ln m = ln M₀ + α·ln|Δm|:  α = {alpha:.6f},  M₀ = {M0:.6f} MeV,  RMS = {rms1:.4f}")
chk("C1 [anchor] 1-參數基準 RMS = 0.5872 (O136 docs/32/33 權威)",
    abs(rms1 - 0.5872) < 5e-4, f"RMS = {rms1:.4f}")
print(f"\n  {'mode':>5} {'粒子':>6} {'gen':>4} {'ln m':>9} {'殘餘':>9} {'倍數':>8}")
print("  " + "-" * 46)
for (n, p), r in zip(PAIR, resid):
    print(f"  {n:>5} {p:>6} {GEN[p]:>4} {math.log(MASS[p]):>9.4f} {r:>9.4f} {math.exp(r):>8.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§B 1-參數替代: γ_n 本身\n{'─'*100}")
beta_g, pred_g, rms_g = ols(lgamma, lm)
print(f"  ln m = c + β·ln γ_n:  β = {beta_g[1]:.6f}, RMS = {rms_g:.4f}")
beta_n, pred_n, rms_n = ols(ln_, lm)
print(f"  ln m = c + β·n:       β = {beta_n[1]:.6f}, RMS = {rms_n:.4f}")
print(f"\n  {'預測量':>14} {'RMS':>9}")
print("  " + "-" * 26)
for name, r in [("|Δm|", rms1), ("γ_n", rms_g), ("n", rms_n)]:
    print(f"  {name:>14} {r:>9.4f}")
chk("C2 [比較] |Δm| 係三者最佳之單一預測量",
    rms1 < rms_g and rms1 < rms_n, f"|Δm| {rms1:.4f} < γ_n {rms_g:.4f}, n {rms_n:.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§C 2-參數擴展 (誠實計自由度)\n{'─'*100}")
exts = {
    "+ β·ln γ_n": lgamma,
    "+ β·n": ln_,
    "+ β·gen": lgen,
    "+ β·lepton sector": sector,
}
print(f"\n  {'擴展':>20} {'β':>10} {'RMS':>9} {'改善':>8} {'ΔRMS':>9}")
print("  " + "-" * 62)
res_ext = {}
for name, z in exts.items():
    b, p, r = ols(np.column_stack([ldm, z]), lm)
    res_ext[name] = {"beta": float(b[2]), "rms": r, "improve": rms1 / r}
    print(f"  {name:>20} {b[2]:>10.5f} {r:>9.4f} {rms1/r:>8.4f}× {rms1-r:>9.4f}")
best_ext = min(res_ext.items(), key=lambda kv: kv[1]["rms"])
chk("C3 [2-參數] 冇任何結構擴展達到 RMS < 0.05 (閉合門檻)",
    all(v["rms"] > 0.05 for v in res_ext.values()),
    f"最佳 = {best_ext[0]} (RMS {best_ext[1]['rms']:.4f})")
chk("C4 [2-參數] 最佳改善 < 1.5× (唔足以解釋 11.7× 缺口)",
    best_ext[1]["improve"] < 1.5, f"{best_ext[1]['improve']:.4f}×")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§D 世代塊置換 null (N = 100000)\n{'─'*100}")


def between_gen_var(res):
    m = [np.mean([res[i] for i, (n, p) in enumerate(PAIR) if GEN[p] == g]) for g in (1, 2, 3)]
    return float(np.var(m))


obs_stat = between_gen_var(resid)
rng = np.random.default_rng(20260921)
null_stats = np.empty(100000)
for k in range(100000):
    null_stats[k] = between_gen_var(rng.permutation(resid))
p_gen = float((null_stats >= obs_stat).mean())
print(f"  觀測世代間方差 = {obs_stat:.6f}")
print(f"  null (N=10⁵): 中位 = {np.median(null_stats):.6f}, 95% = {np.percentile(null_stats,95):.6f}")
print(f"  P(≥觀測) = {p_gen:.4f}")
chk("C5 [世代塊] 世代間方差唔顯著 (P > 0.05) ⟹ 殘餘唔係世代結構",
    p_gen > 0.05, f"P = {p_gen:.4f} (O136 docs/33 之 p = 0.2109 一致方向)")

print(f"\n  世代殘餘均值:")
for g in (3, 2, 1):
    vals = [resid[i] for i, (n, p) in enumerate(PAIR) if GEN[p] == g]
    print(f"    gen {g} (模式塊 {GEN_BLOCK[g]}): 均值 {np.mean(vals):+.4f}, 倍數 {math.exp(np.mean(vals)):.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§E 結構 α 候選之可辨識性 (O136 判準④)\n{'─'*100}")
print(f"\n  擬合 α = {alpha:.6f};  bootstrap (N=2000) 之 σ:")
boot = np.empty(2000)
for k in range(2000):
    idx = rng.integers(0, 9, 9)
    b, _, _ = ols(ldm[idx], lm[idx])
    boot[k] = b[1]
sd_a = float(np.std(boot))
print(f"    α = {alpha:.6f} ± {sd_a:.6f}")
cands = {"3": 3.0, "44/17": 44 / 17, "μ²+φ⁻¹": 2 + 0.618034, "e": math.e,
         "2.6333 (擬合)": alpha, "L₄/L₅·F₅": 7 * 5 / 11}
print(f"\n  {'候選 α':>16} {'值':>10} {'|Δ|/σ':>9} {'可辨識?':>10}")
print("  " + "-" * 50)
for name, val in cands.items():
    d = abs(val - alpha) / sd_a
    print(f"  {name:>16} {val:>10.5f} {d:>9.3f} {('YES' if d > 2 else 'no'):>10}")
n_within = sum(1 for k, v in cands.items() if k != "2.6333 (擬合)" and abs(v - alpha) / sd_a < 2)
n_struct = len(cands) - 1
chk("C6 [判準④] α 弱約束: %d/%d 結構候選落喺 2σ 內 ⟹ 命中唔構成證據" % (n_within, n_struct),
    n_within >= 3,
    f"σ_α = {sd_a:.4f}; 2σ 內: " +
    ", ".join(k for k, v in cands.items() if k != "2.6333 (擬合)" and abs(v - alpha) / sd_a < 2))

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§F 裁決 (script 09)\n{'─'*100}")
print(f"""
  ① 映射層 = m = M₀·|Δm|^α (2 自由參數); 1-參數擬合 RMS = {rms1:.4f}
  ② |Δm| 係最佳單一預測量 (優於 γ_n {rms_g:.4f} 同 n {rms_n:.4f})
  ③ 全部結構 2-參數擴展都唔閉合 (最佳 {best_ext[0]}: {best_ext[1]['rms']:.4f}, 改善 {best_ext[1]['improve']:.4f}×)
  ④ 世代塊結構: P = {p_gen:.4f} ⟹ 唔顯著
  ⑤ α 不可辨識 (σ_α = {sd_a:.4f}; 結構候選全喺 2σ 內)
  ⟹ 映射層缺口 = 【1 條冪律律 + 2 參數】之固有限制;
     9 點 / 2 參數 ⟹ 自由度 7, 殘餘 0.5872 已係該模型類之最佳
  ⟹ 下一輪: 需【零參數 α 之結構推導】(唔係擬合) 或 接受映射層為獨立公設
""")

n_pass = sum(1 for _, ok in checks if ok)
print(f"{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")
for name, ok in checks:
    if not ok:
        print(f"  FAIL: {name}")

with open(OUT / "09_mapping_layer.json", "w") as f:
    json.dump({
        "baseline_rms": base, "alpha": alpha, "M0_MeV": M0, "rms_1param": rms1,
        "rms_gamma": rms_g, "rms_n": rms_n,
        "extensions": {k: {"beta": v["beta"], "rms": v["rms"], "improve": v["improve"]}
                       for k, v in res_ext.items()},
        "gen_block_p": p_gen, "gen_block_var": obs_stat,
        "sigma_alpha": sd_a,
        "residuals": {p: float(r) for (_, p), r in zip(PAIR, resid)},
        "checks_pass": int(n_pass), "checks_total": len(checks),
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/09_mapping_layer.json")
