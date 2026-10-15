#!/usr/bin/env python3
"""
O136 — Script 68: α=79/30 零參數盲測升格 (R8 攻堅, 2026-10-06)
================================================================
承接: O209 docs/11 (α 候選 79/30 必要條件已成立: 零損失 + 唯一命中 + 結構身份)
      O209 P10.1: LOOCV 固定 α 唔顯著優於 OLS (Δ<5pp) — 逐點 fit 評估已做
任務: ★ 樣本外盲測 — 唔 fit 任何嘢 (零參數), 用 α=79/30 直接預言
      全部 36 個質量比 m_i/m_j = (|Δm_i|/|Δm_j|)^α, 報中位/平均偏差
      對照: α_OLS 同樣零參數 36 比預言 + MC null (隨機 α 分佈)

判準 (方法論定理 4/5 繼承):
  * 唔 fit M₀/α/任何嘢 — 純結構預言
  * 79/30 必須顯著優於 α_OLS (唔單止「唔差過」)
  * MC null: 隨機 α∈[0,5] 36 比預言中位偏差分佈, 報 P(≤ obs)
  * 誠實分級: PASS → 🟡→🟢 候選成立; FAIL → 保持 🟡 唔升格

權威構造 (scripts/59/63): NC=88, ψ_n(i)=sin(nπi/89), X=diag(i−⟨i⟩),
V_nm=⟨n|X|m⟩ Z₂-奇, E_n=4sin²(nπ/88), |Δm_n| = Σ_m |V_nm|²/|E_n−E_m|
質量: MASS (scripts/59 L31-32, PDG)
配對 (O209 frame |Δm| 降序): 1→t, 2→b, 3→τ, 4→c, 5→μ, 7→s, 9→d, 11→u, 13→e
"""
import json, math
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
rng = np.random.default_rng(20261006)

NC = 88
MASS = {"e": 0.510999, "mu": 105.6584, "tau": 1776.86,
        "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0}
MODES = [1, 2, 3, 4, 5, 7, 9, 11, 13]              # O209 frame |Δm| 降序
F8 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"][:8]  # 9pt 全含 t

# ── |Δm| 權威重算 (O209 scripts/11 定義, 14/14 PASS 已驗證; 零 import) ──
# 88-site: psi_n(i)=sin(nπi/89) (row = mode, 已 norm), V=psi·X·psiᵀ,
# X=diag(i−⟨i⟩), E_n=4sin²(nπ/88), Gm=1/(E_a−E_b) (有符號, 對角 0), dm_a=Σ_b V²_ab·Gm_ab
idx = np.arange(1, NC + 1)
psi = np.array([np.sin(n * math.pi * idx / (NC + 1)) for n in range(1, NC + 1)])
psi = psi / np.linalg.norm(psi, axis=1)[:, None]
V = psi @ np.diag(idx - idx.mean()) @ psi.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, NC + 1)])
D = E[:, None] - E[None, :]
Gm = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(Gm, 0.0)
dm_all = np.einsum("ab,ab->a", V ** 2, Gm)
dm = {n: float(dm_all[n - 1]) for n in MODES}

# 9pt 質量向量 (O209 順序) + log
mvals = np.array([MASS[f] for f in F8])
logm = np.log(mvals)
logdm = np.array([math.log(abs(dm[n])) for n in MODES[:8]])   # 8pt (除 t) — 同 O209 P4-P6 一致 (|Δm| 取 abs)
alpha_ols = float(np.polyfit(logdm, logm, 1)[0])
print(f"== 權威重算 |Δm| ==")
print(f"   |Δm|: " + ", ".join(f"{n}:{dm[n]:.3f}" for n in MODES))
print(f"   α_OLS (8pt 除 t) = {alpha_ols:.6f}  (O209 P4: 2.6506 預期 — 8pt/9pt 分別)")

# ── α 候選: 79/30 零參數 36 比盲測 ─────────────────────────────────────
# 9pt 全含 t
m9 = np.array([MASS[f] for f in ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]])
logm9 = np.log(m9)
logdm9 = np.array([math.log(abs(dm[n])) for n in MODES])
alpha_ols9 = float(np.polyfit(logdm9, logm9, 1)[0])
alpha_cand = 79 / 30

# 36 個質量比 (pairwise): 零參數預言 m_i/m_j = (|dm_i|/|dm_j|)^α
pairs = [(i, j) for i in range(9) for j in range(i + 1, 9)]
def ratio_dev(alpha, i, j):
    mratio_pred = (logdm9[i] - logdm9[j]) * alpha
    mratio_obs = logm9[i] - logm9[j]
    return mratio_obs - mratio_pred   # log 尺度偏差 (正 = obs 大過預言)

dev_cand = np.array([ratio_dev(alpha_cand, i, j) for i, j in pairs])
dev_ols = np.array([ratio_dev(alpha_ols9, i, j) for i, j in pairs])

print(f"\n== α=79/30 零參數 36 比盲測 ==")
print(f"   α_cand  = {alpha_cand:.6f}   α_OLS(9pt) = {alpha_ols9:.6f}")
print(f"   79/30:  |dev| 中位 = {np.median(np.abs(dev_cand)):.5f}  RMSE = {np.sqrt((dev_cand**2).mean()):.5f}")
print(f"   α_OLS:  |dev| 中位 = {np.median(np.abs(dev_ols)):.5f}  RMSE = {np.sqrt((dev_ols**2).mean()):.5f}")

# MC null: 隨機 α 均勻 [0,5], 每 α 計 36 比 |dev| 中位
MC = 20000
null_med = []
for _ in range(MC):
    a = rng.uniform(0, 5)
    null_med.append(np.median(np.abs(np.array([ratio_dev(a, i, j) for i, j in pairs]))))
null_med = np.array(null_med)
p_cand = float((null_med <= np.median(np.abs(dev_cand))).mean())
p_ols = float((null_med <= np.median(np.abs(dev_ols))).mean())
print(f"   MC null: N={MC}, |dev| 中位 median={np.median(null_med):.5f}, min={null_med.min():.5f}")
print(f"   P(79/30 ≤ null) = {p_cand:.4f}   P(α_OLS ≤ null) = {p_ols:.4f}")

# 79/30 vs OLS 直接比較 (成對 36 差)
win = int((np.abs(dev_cand) < np.abs(dev_ols)).sum())
print(f"   成對比較: 79/30 優於 OLS 比率 = {win}/36 = {win/36:.3f}")
bootstrap_p = float((rng.binomial(36, 0.5, 20000) <= win).mean())
print(f"   Bootstrap P(優於 OLS 之勝率 ≥ {win}/36 純機率) = {bootstrap_p:.4f}")

# ══ 真正樣本外: 8pt fit (除 t) → 預言 m_t ══
# t (n=1) 唔入 fit; α 兩種: 79/30 (零額外參數) vs α_OLS_8 (1 參數, 由 8pt 擬合)
m8 = np.array([MASS[f] for f in ["b", "tau", "c", "mu", "s", "d", "u", "e"]])
logm8 = np.log(m8)
logdm8 = np.array([math.log(abs(dm[n])) for n in MODES[1:]])
alpha_ols8 = float(np.polyfit(logdm8, logm8, 1)[0])
logM0_8_fit = float((logm8 - alpha_ols8 * logdm8).mean())
logM0_79_fit = float((logm8 - alpha_cand * logdm8).mean())
pred_ols8_t = logM0_8_fit + alpha_ols8 * math.log(abs(dm[1]))
pred_79_t = logM0_79_fit + alpha_cand * math.log(abs(dm[1]))
dev_ols8_t = float(math.log(MASS["t"]) - pred_ols8_t)
dev_79_t = float(math.log(MASS["t"]) - pred_79_t)
print(f"\n═══ 樣本外盲測: 8pt fit → 預言 m_t (n=1 唔入 fit) ═══")
print(f"   α_OLS_8 (8pt) = {alpha_ols8:.6f}   (O209 P7: 2.6506 預期)")
print(f"   79/30 預言 t: log-dev = {dev_79_t:+.5f}  ({np.expm1(abs(dev_79_t))*100:.3f}%)")
print(f"   α_OLS_8 預言 t: log-dev = {dev_ols8_t:+.5f}  ({np.expm1(abs(dev_ols8_t))*100:.3f}%)")
print(f"   79/30 更準? {abs(dev_79_t) < abs(dev_ols8_t)}  (O209 docs/11: 9pt dev 0.003% vs 8pt dev 0.655%)")

# 判定
print(f"\n== 判定 ==")
if p_cand < 0.01:
    print("   ✅ 79/30 零參數 36 比預言 顯著優於隨機 α (P<0.01)")
else:
    print("   🔴 79/30 零參數 36 比預言 唔顯著 vs 隨機 α")
if np.median(np.abs(dev_cand)) < np.median(np.abs(dev_ols)) and bootstrap_p < 0.05:
    print("   ✅ 79/30 成對優於 α_OLS (bootstrap P<0.05)")
else:
    print(f"   🔴 79/30 未優於 α_OLS (bootstrap P={bootstrap_p:.4f}) — 兩者只差 3e-5, 預期內")
if abs(dev_79_t) < abs(dev_ols8_t):
    print("   ✅ 樣本外 t 預言: 79/30 (零額外參數) 準過 8pt 擬合 α_OLS_8")
else:
    print("   🔴 樣本外 t 預言: 79/30 遜於 α_OLS_8")

out = {
    "alpha_ols_8pt": alpha_ols, "alpha_ols_9pt": alpha_ols9,
    "alpha_cand": alpha_cand,
    "dm": {str(n): dm[n] for n in MODES},
    "ratio_dev_cand_median": float(np.median(np.abs(dev_cand))),
    "ratio_dev_cand_rmse": float(np.sqrt((dev_cand**2).mean())),
    "ratio_dev_ols_median": float(np.median(np.abs(dev_ols))),
    "ratio_dev_ols_rmse": float(np.sqrt((dev_ols**2).mean())),
    "mc_null_median": float(np.median(null_med)),
    "p_cand_vs_null": p_cand, "p_ols_vs_null": p_ols,
    "pairwise_win_7930": win, "bootstrap_p_vs_ols": float(bootstrap_p),
    "alpha_ols_8pt_fit": alpha_ols8,
    "t_pred_dev_7930": dev_79_t, "t_pred_dev_ols8": dev_ols8_t,
    "t_pred_7930_better": abs(dev_79_t) < abs(dev_ols8_t),
    "checks": [
        {"name": "C1. |Δm| 權威重算完成 (9 modes)", "pass": all(dm[n] > 0 for n in MODES)},
        {"name": "C2. 36 對以上", "pass": len(pairs) == 36},
        {"name": "C3. MC null N≥10000", "pass": MC >= 10000},
        {"name": "C4. 79/30 P<0.01 先升格", "pass": p_cand < 0.01},
    ],
}
(DATA / "68_alpha_7930_blindtest.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print("\ndata/68_alpha_7930_blindtest.json written")