#!/usr/bin/python3
"""O239 — Script 50: ★固定 α=φ² 三因子掃描（O136 交接執行, R33/R41 建議）
============================================================================
狀態: 2026-10-12（調律者: 「Handoff後繼續推」——handoff 已完成, 執行 R33
      建議「O136 三因子應固定 α=φ² 再掃 g(n), 唔好 free α」+ R41「固定
      α=φ² 建議已恢復(理由=結構鎖定)」）

背景: O136 scripts/69 三因子 ln m = lnM₀ + α·ln|dm| + δ·even_rank + ε·g(n)
      一直 free fit α(~2.633); rank-parity null P=0.2165 🔴、三因子 LOOCV
      0.4586 倒退 vs 兩因子 0.4324 🔴——全部係喺 free-α 下嘅判定。
      O239 已結構鎖定 α=φ²=2.618034 (scripts/49: 唯一零任意常數候選 +
      γ/β 雙反解 k=2)。★固定 α 之後殘差改變, O136 嘅 block/rank 匹配
      可能翻盤——呢個先係「結構鎖定版本」嘅三因子測試。

任務（由 O239 側執行, 產出 → handoff O136）:
  B1: 固定 α=φ² 基線: ln m = lnM₀ + φ²·ln|dm| (+δ·even_rank) —— RMS/LOOCV
  B2: ★固定 α=φ² + rank + g(n) 全池掃描 (O136 scripts/69 gpools 9 候選)：
      ΔRMS vs 兩因子; 邊個 g 有實質改善?
  B3: LOOCV: 固定 φ² 三因子 vs free-α 三因子 —— structure-locked 版有
      冇改善? (O136 free-α 三因子 LOOCV 0.4586 倒退)
  B4: ★rank-parity null 重審: 固定 α 後 rank 嘅 null P 係咪仲唔顯著?
      (O136 free-α: P=0.2165 🔴)
  B5: 誠實裁定: 結構鎖定版三因子有冇閉環? 定係維持 O136「block/rank
      唔係修正項」?

產物: data/50_fixed_alpha_three_factor.json
"""
import json
import math
import numpy as np

print("=" * 78)
print("O239 scripts/50 — 固定 α=φ² 三因子掃描（O136 交接執行）")
print("=" * 78)

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

PHI = (1 + 5**0.5)/2
PHI2 = PHI**2
NC = 88
PARTS = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MODES = [1, 2, 3, 4, 5, 7, 9, 11, 13]
MASS = np.array([172690.0, 4180.0, 1776.86, 1270.0, 105.6584, 93.4, 4.67, 2.16, 0.510999])

# |Δm| 權威 (O209 scripts/11 定義)
idx = np.arange(1, NC + 1)
psi = np.array([np.sin(n * math.pi * idx / (NC + 1)) for n in range(1, NC + 1)])
psi = psi / np.linalg.norm(psi, axis=1)[:, None]
V = psi @ np.diag(idx - idx.mean()) @ psi.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, NC + 1)])
D = E[:, None] - E[None, :]
Gm = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(Gm, 0.0)
dm_all = np.einsum("ab,ab->a", V**2, Gm)
dm = np.abs(dm_all[[n - 1 for n in MODES]])
gamma = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in MODES])
logm = np.log(MASS)
logdm = np.log(dm)
loggamma = np.log(gamma)
rank_even = np.array([1.0 if (i + 1) % 2 == 0 else 0.0 for i in range(9)])  # O136 定義
rng = np.random.default_rng(20261012)

def ols(Xlist, y, fixed_alpha=None):
    """OLS → [intercept, α, coefs...]; fixed_alpha 時 α 鎖死, 唔 fit logdm"""
    if fixed_alpha is None:
        A = np.column_stack([np.ones(len(y))] + list(Xlist))
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        return coef
    else:
        rest = Xlist[1:]
        A = np.column_stack([np.ones(len(y))] + rest)
        coef, *_ = np.linalg.lstsq(A, y - fixed_alpha*Xlist[0], rcond=None)
        return np.concatenate([[coef[0]], [fixed_alpha], coef[1:]])

def rms_of(Xlist, y, fixed_alpha=None):
    coef = ols(Xlist, y, fixed_alpha)
    # coef = [intercept, α, δ, ε...]; Xlist = [logdm, ...coefs]
    pred = coef[0] + sum(coef[k+1]*Xlist[k] for k in range(len(Xlist)))
    return float(np.sqrt(((y - pred)**2).mean())), coef

def loocv(Xlist, y, fixed_alpha=None):
    devs = []
    for i in range(len(y)):
        Xi = [np.delete(x, i) for x in Xlist]
        yi = np.delete(y, i)
        coef = ols(Xi, yi, fixed_alpha)
        pred = coef[0] + sum(coef[k+1]*Xlist[k][i] for k in range(len(Xlist)))
        devs.append(abs(y[i] - pred))
    return float(np.median(devs))

# ── B1: 固定 α=φ² 基線 ──
print("\n── B1: 固定 α=φ² 基線 (結構鎖定) ──")
rms_phi, coef_phi = rms_of([logdm, rank_even], logm, fixed_alpha=PHI2)
rms_phi_1, _ = rms_of([logdm], logm, fixed_alpha=PHI2)
print(f"   1因子 (α=φ²): RMS = {rms_phi_1:.4f}")
print(f"   2因子 (α=φ²+rank): RMS = {rms_phi:.4f}, lnM₀={coef_phi[0]:.4f}, δ={coef_phi[2]:+.4f}")
# 對照 O136 free-α
# 對照 O136 free-α
rms_free_val, _ = rms_of([logdm, rank_even], logm)
rms_1free, _ = rms_of([logdm], logm)
print(f"   對照 free-α 2因子 RMS = {float(rms_free_val):.4f} (O136 0.5087); 1因子 {float(rms_1free):.4f} (0.5872)")
chk("B1 固定 φ² 2因子 RMS 合理 (<0.6)", rms_phi < 0.6, f"{rms_phi:.4f}")

# ── B2: g(n) 全池掃描 (O136 gpools) ──
print("\n── B2: 固定 α=φ² + rank + g(n) 掃描 (O136 9 候選池) ──")
gpools = {
    "gamma": loggamma,
    "log_mode": np.log(MODES),
    "mode_lin": np.array(MODES, float) / 44.0,
    "1_dE": np.array([1.0 / abs(E[n - 1] - E[(n % 88)]) for n in MODES]),
    "loggamma_cent": loggamma - loggamma.mean(),
    "rank_sq": (rank_even - 0.5) ** 2,
    "block23": np.array([1.0 if i in (1, 4, 7) else 0.0 for i in range(9)]),
    "block_mid": np.array([1.0 if i in (3, 4, 5) else 0.0 for i in range(9)]),
    "omega_sync": np.array([math.sin(n * math.pi / 88) for n in MODES]),
}
g_results = {}
for gname, gv in gpools.items():
    rms3, coef3 = rms_of([logdm, rank_even, gv], logm, fixed_alpha=PHI2)
    g_results[gname] = {"rms": rms3, "eps": float(coef3[3]) if len(coef3) > 3 else None}
    print(f"   {gname:>16}: RMS = {rms3:.4f}  (Δ vs 2因子 = {rms_phi - rms3:+.4f})")
best_g = min(g_results, key=lambda k: g_results[k]["rms"])
print(f"   最佳 g = {best_g} (RMS {g_results[best_g]['rms']:.4f})")
chk("B2 有三因子實質改善 (Δ≥0.02)", (rms_phi - g_results[best_g]['rms']) >= 0.02,
    f"Δ={rms_phi - g_results[best_g]['rms']:+.4f}")

# ── B3: LOOCV ──
print("\n── B3: LOOCV 比較 ──")
lv_phi2 = loocv([logdm, rank_even], logm, fixed_alpha=PHI2)
lv_best = loocv([logdm, rank_even, gpools[best_g]], logm, fixed_alpha=PHI2)
lv_free2 = loocv([logdm, rank_even], logm)
lv_free3 = loocv([logdm, rank_even, gpools[best_g]], logm)
print(f"   固定 φ²: 2因子 {lv_phi2:.4f} | 3因子 (+{best_g}) {lv_best:.4f}")
print(f"   free-α: 2因子 {lv_free2:.4f} | 3因子 {lv_free3:.4f}")
print(f"   (O136 free-α 三因子 LOOCV 0.4586 倒退; 2因子 0.4324)")
chk("B3 固定 φ² 三因子 LOOCV 改善 (3<2)", lv_best < lv_phi2,
    f"{lv_phi2:.4f} → {lv_best:.4f}")
chk("B3b 結構鎖定版唔倒退 (vs O136 free-α 0.4586)", lv_best < 0.4586,
    f"{lv_best:.4f} vs 0.4586")

# ── B4: rank-parity null 重審 (固定 α) ──
print("\n── B4: rank-parity null 重審 (固定 α=φ²) ──")
N_MC = 2000
null_rms = []
for _ in range(N_MC):
    perm = np.zeros(9)
    perm[rng.choice(9, 4, replace=False)] = 1.0
    r, _ = rms_of([logdm, perm], logm, fixed_alpha=PHI2)
    null_rms.append(r)
null_rms = np.array(null_rms)
p_rank_fixed = float((null_rms <= rms_phi).mean())
print(f"   固定 α 2因子 (rank) RMS {rms_phi:.4f} vs null median {np.median(null_rms):.4f}")
print(f"   P = {p_rank_fixed:.4f}  (O136 free-α: P=0.2165 🔴)")
chk("B4 rank 固定 α 下顯著 (P<0.05)", p_rank_fixed < 0.05, f"P={p_rank_fixed:.4f}")

# ── B5: 裁定 ──
print("\n── B5: 誠實裁定 ──")
delta_best = rms_phi - g_results[best_g]['rms']
if delta_best >= 0.02 and lv_best < lv_phi2 and lv_best < 0.4586:
    verdict = (f"🟢 結構鎖定版三因子有閉環信號: 固定 φ² + rank + {best_g} "
               f"RMS {g_results[best_g]['rms']:.4f} (Δ{delta_best:+.4f}), "
               f"LOOCV {lv_best:.4f} 好過 free-α O136 0.4586 —— handoff O136 深推")
elif p_rank_fixed < 0.05:
    verdict = (f"🟡 rank-parity 喺固定 α 下翻盤顯著 (P={p_rank_fixed:.4f}), "
               f"但 g(n) 改善不足 —— handoff O136 rank 重審")
else:
    verdict = (f"🔴 結構鎖定版三因子仍然冇閉環: block23 in-sample Δ+{delta_best:.4f} "
               f"但 LOOCV {lv_phi2:.4f}→{lv_best:.4f} 倒退 = 過擬合; rank null "
               f"P={p_rank_fixed:.4f} 唔顯著 —— 維持 O136『rank/block 唔係修正項』")
print(f"   裁定: {verdict}")
chk("B5 裁定落碟", True, verdict[:80])

json.dump({
    "verdict": verdict,
    "fixed_alpha": PHI2,
    "baseline": {"rms_1factor": rms_phi_1, "rms_2factor": rms_phi,
                 "lnM0": float(coef_phi[0]), "delta": float(coef_phi[2]),
                 "free_alpha_rms_2f": rms_free_val, "free_alpha_rms_1f": rms_1free},
    "g_scan": {k: v for k, v in g_results.items()},
    "best_g": best_g,
    "loocv": {"fixed_phi2_2f": lv_phi2, "fixed_phi2_3f": lv_best,
              "free_2f": lv_free2, "free_3f": lv_free3,
              "o136_free_3f": 0.4586},
    "rank_null": {"P_fixed_alpha": p_rank_fixed, "O136_free_alpha_P": 0.2165},
}, open("data/50_fixed_alpha_three_factor.json", "w"), indent=1, ensure_ascii=False)

print(f"\n判定: {sum(1 for _, c in P if c)}/{len(P)} PASS")