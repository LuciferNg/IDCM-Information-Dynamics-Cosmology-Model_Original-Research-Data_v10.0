#!/usr/bin/env python3
"""
O136 — Script 69: mass-shape 三因子閉環 (R6 攻艱 ②, 2026-10-06)
================================================================
承接: O209 docs/12 P5 (rank-parity 兩值修正: δ=+0.731, RMS 0.5087, 收益 1.22×)
      O209 docs/11 P9 (修正項掃描負結果: (n−1)%4 等冇實質 LOOCV 改善)
任務: ★ 三因子閉環 — ln m = ln M₀ + α·ln|dm| + δ·even_rank + ε·g(n)
      其中 g(n) ∈ {γ_n, ln|dm| 級, C_f 比, 塊指標, log n, n, 1/ΔE 類}
      ★ 檢驗 rank-parity 修正後殘餘有冇結構 (O209 只報 RMS, 未分析殘餘)

判準 (方法論定理 2/4 繼承):
  * 置換 null 退化 ⟹ 唔用重排配對; 用隨機因子指派 null (固定配對)
  * LOOCV 逐點預言 (唔靠 in-sample RMS) — 「閉環」= 樣本外
  * 新增 g(n) 必須帶 LOOCV 實質改善 (Δ ≥ 5pp), 唔係 in-sample 好睇
  * 度量: 對數值 (方法論定理 3)

權威構造 (scripts/68 同款): O209 scripts/11 定義 |dm|; MASS PDG; O209 frame
"""
import json, math
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
rng = np.random.default_rng(20261006)

NC = 88
MASS = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
        "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0}
# O209 frame |Δm| 降序: 1→t 2→b 3→τ 4→c 5→μ 7→s 9→d 11→u 13→e
PARTS = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MODES = [1, 2, 3, 4, 5, 7, 9, 11, 13]
rank_even = np.array([1.0 if (i + 1) % 2 == 0 else 0.0 for i in range(9)])  # even-rank {b,c,s,d,u}? O209: even8 用 rank8+1

# ── |Δm| 權威 (O209 scripts/11) ───────────────────────────────────────
idx = np.arange(1, NC + 1)
psi = np.array([np.sin(n * math.pi * idx / (NC + 1)) for n in range(1, NC + 1)])
psi = psi / np.linalg.norm(psi, axis=1)[:, None]
V = psi @ np.diag(idx - idx.mean()) @ psi.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, NC + 1)])
D = E[:, None] - E[None, :]
Gm = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(Gm, 0.0)
dm_all = np.einsum("ab,ab->a", V ** 2, Gm)
dm = np.abs(dm_all[[n - 1 for n in MODES]])
gamma = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in MODES])
logm = np.log(np.array([MASS[p] for p in PARTS]))
logdm = np.log(dm)
loggamma = np.log(gamma)

print("=" * 96)
print("O136 Script 69: mass-shape 三因子閉環 (R6)")
print("=" * 96)

def ols(X, y):
    A = np.column_stack([np.ones(len(y))] + list(X))
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    rms = float(np.sqrt(((y - pred) ** 2).mean()))
    return coef, rms

checks = []
def chk(name, cond, detail=""):
    checks.append({"name": name, "pass": bool(cond), "detail": detail})
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))

# ── P1. 基線: 單一冪律 ────────────────────────────────────────────────
_, rms1 = ols([logdm], logm)
print(f"\nP1. 基線 ln m = c + α ln|dm|:  RMS = {rms1:.4f}  (O209 0.5872 預期)")
chk("P1.1 基線 RMS ≈ 0.5872", abs(rms1 - 0.5872) < 0.01, f"{rms1:.4f}")

# ── P2. 兩因子: + rank-parity (O209 P5 重現) ──────────────────────────
coef2, rms2 = ols([logdm, rank_even], logm)
print(f"\nP2. + even-rank 兩值: α={coef2[1]:.4f} δ={coef2[2]:+.4f}  RMS = {rms2:.4f}  (O209 0.5087 預期)")
chk("P2.1 rank-parity 修正重現 (RMS < 0.530)", rms2 < 0.530, f"{rms2:.4f}")
resid2 = logm - (np.column_stack([np.ones(9), logdm, rank_even]) @ coef2)

# ── P3. rank-parity 修正後殘餘 vs 結構量 ─────────────────────────────
print(f"\nP3. rank-parity 修正後殘餘 ({rms2:.4f}) vs 結構量:")
struct = {
    "gamma": loggamma, "gamma_ratio_next": np.roll(loggamma, -1),
    "n": np.log(MODES), "n_lin": MODES,
    "mode_odd": np.array([1.0 if n % 2 else 0.0 for n in MODES]),
    "logdm2": np.log(np.abs(dm_all[[n - 1 for n in MODES]]) ** 2),
    "v2_44": np.array([0.0 if (44 - n) % 2 == 1 else 1.0 for n in MODES]),
    "rank_parity_after": resid2,
}
# 真實殘餘相關 (唔可以靠 r=0.988 嗰種)
corrs = {}
for k, v in struct.items():
    if k == "rank_parity_after":
        continue
    r = float(np.corrcoef(resid2, np.asarray(v, dtype=float))[0, 1])
    corrs[k] = r
    print(f"    {k:>20}: r = {r:+.4f}")
chk("P3.1 殘餘 vs γ 唔顯著 (|r|<0.7)", abs(corrs["gamma"]) < 0.7, f"r={corrs['gamma']:.4f}")

# ── P4. 三因子掃描: g(n) ∈ 候選庫 ────────────────────────────────────
print(f"\nP4. 三因子掃描 (α + even_rank + g):")
gpools = {
    "gamma": loggamma,
    "log_mode": np.log(MODES),
    "mode_lin": np.array(MODES, float) / 44.0,
    "1_dE": np.array([1.0 / abs(E[n - 1] - E[(n % 88)]) for n in MODES]),
    "loggamma_cent": loggamma - loggamma.mean(),
    "rank_sq": (rank_even - 0.5) ** 2,
    "block23": np.array([1.0 if i in (1, 4, 7) else 0.0 for i in range(9)]),  # 中層 c,μ,s
    "block_mid": np.array([1.0 if i in (3, 4, 5) else 0.0 for i in range(9)]),
    "omega_sync": np.array([math.sin(n * math.pi / 88) for n in MODES]),
}
g_results = {}
for gname, gv in gpools.items():
    coef, rms = ols([logdm, rank_even, gv], logm)
    g_results[gname] = rms
    print(f"    {gname:>16}: RMS = {rms:.4f}  (Δ vs P2 = {rms2 - rms:+.4f})")
best_g = min(g_results.items(), key=lambda kv: kv[1])
print(f"    最佳 g = {best_g[0]} (RMS {best_g[1]:.4f})")
chk("P4.1 三因子有實質改善 (< 0.46)", best_g[1] < 0.46, f"{best_g[1]:.4f}")

# ── P5. LOOCV 盲測: 單/雙/三因子 逐點預言 ────────────────────────────
def loocv(Xlist, y):
    devs = []
    for i in range(len(y)):
        Xi = [np.delete(x, i) for x in Xlist]
        yi = np.delete(y, i)
        coef, _ = ols(Xi, yi)
        pred = coef[0] + sum(coef[k + 1] * Xlist[k][i] for k in range(len(Xlist)))
        devs.append(abs(y[i] - pred))
    return float(np.median(devs)), [float(d) for d in devs]

loocv1 = loocv([logdm], logm)
loocv2 = loocv([logdm, rank_even], logm)
gv_best = gpools[best_g[0]]
loocv3 = loocv([logdm, rank_even, gv_best], logm)
print(f"\nP5. LOOCV 逐點預言 (中位 |dev|, 對數):")
print(f"    1 因子: {loocv1[0]:.4f}   2 因子: {loocv2[0]:.4f}   3 因子 (+{best_g[0]}): {loocv3[0]:.4f}")
chk("P5.1 LOOCV 有實質改善 (3因子 < 2因子 − 0.05)", loocv3[0] < loocv2[0] - 0.05,
    f"{loocv2[0]:.4f} → {loocv3[0]:.4f}")
chk("P5.2 LOOCV 2因子 < 1因子", loocv2[0] < loocv1[0], f"{loocv1[0]:.4f} → {loocv2[0]:.4f}")

# ── P6. rank-parity null: 隨機 even/odd 指派 (╌恰好 4 個 1, 同觀測複雜度) ──
print(f"\nP6. rank-parity null (隨機 2 值指派, 恰好 4 個 1, N=2000):")
null_rms = []
base_perm = np.zeros(9)
for _ in range(2000):
    perm = base_perm.copy()
    perm[rng.choice(9, 4, replace=False)] = 1.0
    _, r = ols([logdm, perm], logm)
    null_rms.append(r)
null_rms = np.array(null_rms)
p_parity = float((null_rms <= rms2).mean())
print(f"    觀測 RMS {rms2:.4f} vs null median {np.median(null_rms):.4f}  P = {p_parity:.4f}")
chk("P6.1 rank-parity 顯著 (P<0.05)", p_parity < 0.05, f"P={p_parity:.4f}")

# ── P7. 誠實分級 + 殘餘診断 ──────────────────────────────────────────
coef3b, rms3b = ols([logdm, rank_even, gv_best], logm)
resid3 = logm - (np.column_stack([np.ones(9), logdm, rank_even, gv_best]) @ coef3b)
print(f"\nP7. 最終三因子殘餘 (RMS {rms3b:.4f}):")
for i, p in enumerate(PARTS):
    print(f"    {p:>4} (n={MODES[i]:>2}): resid {resid3[i]:+.4f}  ({np.expm1(resid3[i])*100:+.2f}%)")
cs_resid3 = abs(resid3[3]) + abs(resid3[5])  # c, s
chk("P7.1 c/s 殘餘減弱 (三因子後 |c|+|s| < 兩因子)", abs(resid3[3]) + abs(resid3[5]) < abs(resid2[3]) + abs(resid2[5]),
    f"{abs(resid2[3])+abs(resid2[5]):.3f} → {cs_resid3:.3f}")

print(f"\n== 判定 ==")
print(f"   rank-parity 兩值: {'🟢 有效修正 (P<0.05)' if p_parity < 0.05 else '🔴 唔顯著'}")
print(f"   三因子閉環: {'🟢 LOOCV 實質改善' if (loocv3[0] < loocv2[0] - 0.05) else '🔴 未閉環 (LOOCV 冇實質改善)'}")
print(f"   R6 整體: {'🟢 接近閉環' if loocv3[0] < 0.25 else '🔴 仍開放'}")

out = {
    "rms_baseline": rms1, "rms_rankparity": rms2, "coef2_alpha": float(coef2[1]), "coef2_delta": float(coef2[2]),
    "resid_after_rp": {PARTS[i]: float(resid2[i]) for i in range(9)},
    "g_scan": {k: float(v) for k, v in g_results.items()},
    "best_g": best_g[0], "rms_3factor": rms3b,
    "loocv_1": loocv1[0], "loocv_2": loocv2[0], "loocv_3": loocv3[0],
    "loocv_2_devs": loocv2[1], "loocv_3_devs": loocv3[1],
    "null_parity_p": p_parity, "null_parity_median": float(np.median(null_rms)),
    "resid_after_3": {PARTS[i]: float(resid3[i]) for i in range(9)},
    "checks": checks,
}
(DATA / "69_mass_shape_three_factor.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print("\ndata/69_mass_shape_three_factor.json written")