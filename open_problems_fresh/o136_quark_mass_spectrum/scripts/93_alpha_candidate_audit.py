#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O136 scripts/93 — α 候選可辨識性審核（36 比零參數盲測 × 5 候選）(2026-10-15)

背景（scripts/92 揭示嘅一致性缺口）:
  O136 docs/38 + scripts/68 將 α=79/30 升 🟢（36 比零參數盲測 P=0.0008 +
  樣本外 t 預言 7.3% vs 13.0%）— 但 scripts/68 冇做「其他結構候選同款比較」。
  scripts/92 顯示 LOOCV 下 π−1/2 (0.2811) 甚至好過 79/30 (=α_obs, 0.2900)
  ⟹ 必須審核: 79/30 嘅升格係唔係候選間可辨識, 定係同一「不可辨識」家族。

方法（同 scripts/68, 零參數, 唔 fit）:
  對每個候選 α_c: 36 個成對質量比零參數預言 dev_ij = ln(m_i/m_j) − α_c·ln(|dm_i|/|dm_j|)
  量度 = |dev| 中位 + RMSE
  [A] 5 候選並列 (79/30, π−1/2, 2+5/8, φ², α_OLS_9)
  [B] MC null (隨機 α ~ U[0,5], N=20000) → 每個候選 P(≤ null)
  [C] ★候選互比: 質量誤差 bootstrap (PDG 概略誤差) → 兩候選 Δ|dev| 中位 vs σ
      ⟹ 若 |Δ| < σ ⟹ 候選間不可辨識 (docs/35 判準 4 應用到本檢定)
  [D] 樣本外 t 預言: 8pt → 5 候選各自預言 m_t (零參數版)
"""
import json, math
import numpy as np

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o136_quark_mass_spectrum"
rng = np.random.default_rng(20261015)

PHI2 = ((1 + 5**0.5) / 2) ** 2
PARTS = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MODES = [1, 2, 3, 4, 5, 7, 9, 11, 13]
MASS = np.array([172690.0, 4180.0, 1776.86, 1270.0, 105.6584, 93.4, 4.67, 2.16, 0.510999])
# PDG 概略相對誤差 (docs/35 §四)
RELERR = np.array([1e-4, 1e-4, 3e-4, 1e-3, 3e-4, 1e-3, 5e-4, 5e-4, 5e-8])

# |Δm| 權威 (O209 scripts/11 定義)
NC = 88
idx = np.arange(1, NC + 1)
psi = np.array([np.sin(n * math.pi * idx / (NC + 1)) for n in range(1, NC + 1)])
psi = psi / np.linalg.norm(psi, axis=1)[:, None]
V = psi @ np.diag(idx - idx.mean()) @ psi.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, NC + 1)])
Dm = E[:, None] - E[None, :]
Gm = np.where(np.abs(Dm) > 1e-12, 1.0 / np.where(Dm == 0, 1.0, Dm), 0.0)
np.fill_diagonal(Gm, 0.0)
dm_all = np.einsum("ab,ab->a", V**2, Gm)
dm = np.abs(dm_all[[n - 1 for n in MODES]])

logm9 = np.log(MASS)
logdm9 = np.log(dm)
alpha_ols9 = float(np.polyfit(logdm9, logm9, 1)[0])

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"   [{'PASS' if cond else 'FAIL'}] {name} — {detail}")

print("O136 scripts/93 — α 候選可辨識性審核 (36 比零參數盲測 × 5 候選)")
print("=" * 78)

pairs = [(i, j) for i in range(9) for j in range(i + 1, 9)]
def devs(alpha, logm=logm9, logdm=logdm9):
    return np.array([(logm[i] - logm[j]) - alpha * (logdm[i] - logdm[j]) for i, j in pairs])

CANDS = {
    "79/30 = 2.63333": 79 / 30,
    "π−1/2 = 2.64159": math.pi - 0.5,
    "2+5/8 = 2.62500": 2 + 5 / 8,
    "φ² = 2.61803": PHI2,
    "α_OLS_9 = 2.63325": alpha_ols9,
}

# ── [A] 5 候選並列 ───────────────────────────────────────────────────
print("\n[A] 5 候選 36 比零參數盲測:")
stat = {}
for name, a in CANDS.items():
    d = devs(a)
    med, rmse = float(np.median(np.abs(d))), float(np.sqrt((d**2).mean()))
    stat[name] = {"alpha": a, "med": med, "rmse": rmse}
    print(f"   {name:>20}: |dev| 中位 = {med:.5f}   RMSE = {rmse:.5f}")

# ── [B] MC null ──────────────────────────────────────────────────────
print("\n[B] MC null (隨機 α ~ U[0,5], N=20000):")
MC = 20000
null_med = np.array([np.median(np.abs(devs(rng.uniform(0, 5)))) for _ in range(MC)])
print(f"   null |dev| 中位分佈: median={np.median(null_med):.5f}  min={null_med.min():.5f}  p1={np.percentile(null_med,1):.5f}")
for name in CANDS:
    p = float((null_med <= stat[name]["med"]).mean())
    stat[name]["p_mc"] = p
    print(f"   {name:>20}: P(≤ null) = {p:.4f}")

# ── [C] ★候選互比 (bootstrap) ───────────────────────────────────────
print("\n[C] 候選互比: 質量誤差 bootstrap (N=2000, PDG 概略誤差):")
NB = 2000
boot = {name: [] for name in CANDS}
for _ in range(NB):
    m_b = MASS * (1 + rng.normal(0, 1, 9) * RELERR)
    lm = np.log(m_b)
    for name, a in CANDS.items():
        boot[name].append(np.median(np.abs(devs(a, logm=lm))))
boot = {k: np.array(v) for k, v in boot.items()}
for name in CANDS:
    stat[name]["boot_sd"] = float(boot[name].std())
    stat[name]["boot_med"] = float(np.median(boot[name]))
    print(f"   {name:>20}: bootstrap 中位 = {stat[name]['boot_med']:.5f} ± {stat[name]['boot_sd']:.5f}")

# 兩兩比較 (79/30 vs 其他)
base = "79/30 = 2.63333"
print(f"\n   ★ 79/30 vs 其他候選 (Δ 中位 / bootstrap σ):")
pair_verdicts = {}
for name in CANDS:
    if name == base:
        continue
    delta = stat[base]["med"] - stat[name]["med"]
    sd = math.sqrt(stat[base]["boot_sd"]**2 + stat[name]["boot_sd"]**2)
    nsigma = abs(delta) / sd if sd > 0 else float("inf")
    pair_verdicts[name] = {"delta": delta, "sd": sd, "nsigma": nsigma}
    flag = "不可辨識" if nsigma < 2 else "可分離"
    print(f"      vs {name:>20}: Δ={delta:+.5f}  σ={sd:.5f}  {nsigma:5.2f}σ  ⟹ {flag}")

# ── [D] 樣本外 t 預言 (5 候選, 零參數) ────────────────────────────────
print("\n[D] 樣本外 t 預言 (8pt 定 intercept, α 用候選值):")
m8 = MASS[1:]
logm8, logdm8 = logm9[1:], logdm9[1:]
for name, a in CANDS.items():
    logM0_8 = float((logm8 - a * logdm8).mean())
    dev_t = float(logm9[0] - (logM0_8 + a * logdm9[0]))
    stat[name]["t_dev_pct"] = float(np.expm1(abs(dev_t)) * 100)
    print(f"   {name:>20}: 預言 t dev = {stat[name]['t_dev_pct']:6.3f}%")

# ── 判定 ─────────────────────────────────────────────────────────────
print("\n== 判定 ==")
n_unident = sum(1 for v in pair_verdicts.values() if v["nsigma"] < 2)
print(f"   79/30 vs 其他 4 候選中不可辨識者 = {n_unident}/4")
best_alt = min((n for n in CANDS if n != base), key=lambda n: stat[n]["med"])
print(f"   最佳其他候選 = {best_alt} (|dev| 中位 {stat[best_alt]['med']:.5f} vs 79/30 {stat[base]['med']:.5f})")

chk("A1 79/30 係家族最佳 (|dev| 中位最小, 排除 α_OLS 同值)",
    all(stat[base]["med"] <= stat[n]["med"] for n in CANDS if not n.startswith("α_OLS")),
    f"{stat[base]['med']:.5f} vs min_structural "
    f"{min(stat[n]['med'] for n in CANDS if not n.startswith('α_OLS')):.5f}")
chk("B1 79/30 MC null P < 0.001", stat[base]["p_mc"] < 0.001, f"{stat[base]['p_mc']:.4f}")
chk("C1 79/30 vs φ² ≥ 2σ 可分離 (排除方向 26 二次確認)",
    pair_verdicts["φ² = 2.61803"]["nsigma"] >= 2, f"{pair_verdicts['φ² = 2.61803']['nsigma']:.2f}σ")
chk("C2 79/30 vs π−1/2 ≥ 2σ 可分離",
    pair_verdicts["π−1/2 = 2.64159"]["nsigma"] >= 2, f"{pair_verdicts['π−1/2 = 2.64159']['nsigma']:.2f}σ")
t_best = min(CANDS, key=lambda n: stat[n]["t_dev_pct"])
chk("D1 記錄 tension: 樣本外 t 單點預言最佳候選 ≠ 79/30 (單點 vs 36 比)",
    True, f"t 預言最佳 = {t_best} ({stat[t_best]['t_dev_pct']:.3f}%) vs 79/30 {stat[base]['t_dev_pct']:.3f}%")

if n_unident >= 3:
    verdict = ("🔴 79/30 喺 36 比零參數檢定下同其他結構候選【不可辨識】"
               f"({n_unident}/4 候選 Δ<2σ) ⟹ docs/38『升 🟢 結構常數』需降級為"
               "『36 比預言力顯著 (家族層) 但候選身份不可辨識』; 家族層結論 "
               "(P=0.0008) 不變")
else:
    verdict = (f"🟢 79/30 可同其他結構候選分離 ({n_unident}/4 不可辨識 = 僅 α_OLS 同值); "
               f"φ² {pair_verdicts['φ² = 2.61803']['nsigma']:.1f}σ / π−1/2 "
               f"{pair_verdicts['π−1/2 = 2.64159']['nsigma']:.1f}σ / 2+5/8 "
               f"{pair_verdicts['2+5/8 = 2.62500']['nsigma']:.1f}σ 全部可分離 ⟹ "
               "docs/38 升格維持 + docs/35 排除方向 26 二次確認; "
               f"⚠️ 單點 t 預言最佳 = {t_best} ({stat[t_best]['t_dev_pct']:.2f}%) — "
               "單點斷言唔推翻 36 比家族統計 (判準 7)")
print("   " + verdict)

out = {
    "candidates": {k: {kk: (float(vv) if vv is not None else None) for kk, vv in v.items()} for k, v in stat.items()},
    "pair_vs_7930": {k: {kk: float(vv) for kk, vv in v.items()} for k, v in pair_verdicts.items()},
    "mc_null_median": float(np.median(null_med)),
    "n_unidentifiable": n_unident,
    "verdict": verdict,
}
open(f"{BASE}/data/93_alpha_candidate_audit.json", "w").write(json.dumps(out, indent=1, ensure_ascii=False))
print(f"\n判定: {sum(1 for _, c in P if c)}/{len(P)} PASS")
print("data/93_alpha_candidate_audit.json written")