#!/usr/bin/python3
"""O239 — Script 48: ★固化判決重審 —— 完整候選集 + 細網格（O136 docs/35 候選對照）
============================================================================
狀態: 2026-10-12（「檢查handoff」觸發）—— O136 scripts/92 (2026-10-15) 發現
      O239 R38 固化 (scripts/46) 只測試{φ² vs 自由 α}, 冇測 O136 docs/35
      已識別候選集 {79/30, π−1/2, 2+5/8}。O136 側重算:
        φ² = 2.6180: LOOCV 0.3335
        π−1/2 = 2.6416: LOOCV 0.2811  ← 好 16%
        2+5/8 = 2.6250: LOOCV 0.3110  ← 好 7%
        α_obs = 2.6333: LOOCV 0.2900  ← 好 13%
      判定: φ² 唔係唯一好 LOOCV 值。
      另 scripts/93 36 比盲測: 79/30 家族最佳, φ² 50.7σ 差。

本重審（O239 側, 對齊 O136 程序）:
  R1: 完整候選集 {79/30, π−1/2, 2+5/8, φ², α_obs} LOOCV + 自由 α —— 重現 O136
  R2: ★細網格掃描 α∈[1.2, 4.0] step 0.05 —— 全局極小喺邊? φ² 係咪谷底?
  R3: 誠實裁定: R38「唯一極小+鄰點×1.3」係咪仲成立?
      若 φ² 唔係全局/候選集極小 ⟹ R38 固化要降級/修正（唔可以維持）

產物: data/48_freeze_reaudit.json
"""
import json
import math
import numpy as np

print("=" * 78)
print("O239 scripts/48 — 固化判決重審: 完整候選集 + 細網格")
print("=" * 78)

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

PHI = (1 + 5**0.5)/2
PHI2 = PHI**2
PARTS = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MODES = [1, 2, 3, 4, 5, 7, 9, 11, 13]
MASS = np.array([172690.0, 4180.0, 1776.86, 1270.0, 105.6584, 93.4, 4.67, 2.16, 0.510999])
NC = 88

# 譜計算（同 scripts/39/46 一致）
idx = np.arange(1, NC + 1)
psi = np.array([np.sin(n * math.pi * idx / (NC + 1)) for n in range(1, NC + 1)])
psi = psi / np.linalg.norm(psi, axis=1)[:, None]
V = psi @ np.diag(idx - idx.mean()) @ psi.T
E_n = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, NC + 1)])
D = E_n[:, None] - E_n[None, :]
Gm = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(Gm, 0.0)
dm_all = np.einsum("ab,ab->a", V**2, Gm)
dm = np.abs(dm_all[[n - 1 for n in MODES]])
logdm = np.log(dm)
logm = np.log(MASS)

# 正典 LOOCV（O136 scripts/92 同款: 兩因子 [logdm, rank_even], 中位|dev|）
rank_even = np.array([1.0 if (i + 1) % 2 == 0 else 0.0 for i in range(9)])  # O136 0-index: i+1 even
Xlist = [logdm, rank_even]

def loocv_fixed(alpha):
    devs = []
    for i in range(9):
        rest = [np.delete(x, i) for x in Xlist[1:]]
        ys = np.delete(logm, i)
        Xr = np.column_stack([np.ones(8)] + rest)
        c, *_ = np.linalg.lstsq(Xr, ys - alpha * np.delete(logdm, i), rcond=None)
        pred = alpha * logdm[i] + c[0] + sum(c[k+1] * Xlist[k+1][i] for k in range(len(rest)))
        devs.append(abs(logm[i] - pred))
    return float(np.median(devs))

def loocv_free():
    devs = []
    for i in range(9):
        Xs = [np.delete(x, i) for x in Xlist]
        ys = np.delete(logm, i)
        c, *_ = np.linalg.lstsq(np.column_stack([np.ones(8)] + Xs), ys, rcond=None)
        pred = c[0] + sum(c[k+1] * Xlist[k][i] for k in range(len(Xlist)))
        devs.append(abs(logm[i] - pred))
    return float(np.median(devs))

# ── R1: 完整候選集 LOOCV ──
print("\n── R1: 完整候選集 LOOCV（O136 docs/35 候選, 對齊 scripts/92）──")
CANDS = {
    "79/30 = 2.63333": 79/30,
    "π−1/2 = 2.64159": math.pi - 0.5,
    "2+5/8 = 2.62500": 2 + 5/8,
    "φ² = 2.61803": PHI2,
    "α_OLS = 2.63325": float(np.polyfit(logdm, logm, 1)[0]),
}
res = {}
for name, a in CANDS.items():
    res[name] = loocv_fixed(a)
    print(f"   {name:>18}: LOOCV = {res[name]:.4f}")
free_lv = loocv_free()
print(f"   自由 α+δ (3 free): LOOCV = {free_lv:.4f}")
phi_lv = res["φ² = 2.61803"]
best_name = min(res, key=lambda k: res[k])
best_lv = res[best_name]
print(f"   φ² = {phi_lv:.4f}, 最佳其他 = {best_name} = {best_lv:.4f}, "
      f"差 = {phi_lv - best_lv:+.4f}")
chk("R1 重現 O136: π−1/2 好過 φ²", res["π−1/2 = 2.64159"] < phi_lv,
    f"π−1/2 {res['π−1/2 = 2.64159']:.4f} vs φ² {phi_lv:.4f}")
chk("R1b φ² 唔係候選集最佳", best_lv < phi_lv,
    f"{best_name}={best_lv:.4f} < φ²={phi_lv:.4f}")

# ── R2: 細網格掃描 ──
print("\n── R2: 細網格掃描 α ∈ [1.2, 4.0] step 0.05 ──")
alphas = np.arange(1.2, 4.0 + 1e-9, 0.05)
vals = np.array([loocv_fixed(a) for a in alphas])
imin = int(np.argmin(vals))
print(f"   全局極小: α={alphas[imin]:.3f} LOOCV={vals[imin]:.4f}")
print(f"   φ²={PHI2:.3f} → {phi_lv:.4f} (rank {np.sum(vals < phi_lv - 1e-9) + 1}/{len(alphas)})")
for a_cand in [79/30, math.pi-0.5, 2+5/8, PHI2]:
    i = int(np.argmin(np.abs(alphas - a_cand)))
    print(f"   候選 α={a_cand:.4f}: 網格最近 {alphas[i]:.3f} LOOCV={vals[i]:.4f}")
# φ² 喺細網格入面? 2.61803 唔喺 0.05 網格 (2.60, 2.65), 檢查鄰近
i_phi = int(np.argmin(np.abs(alphas - PHI2)))
is_global = vals[imin] >= phi_lv - 1e-9 and abs(alphas[imin] - PHI2) < 0.06
print(f"   φ² 位置 LOOCV={phi_lv:.4f} vs 全局極小 {vals[imin]:.4f} @ α={alphas[imin]:.3f}")
chk("R2 φ² 係細網格全局極小", is_global,
    f"全局 @ {alphas[imin]:.3f}={vals[imin]:.4f}; φ²={phi_lv:.4f}")
chk("R2b 細網格確認: 全域極小接近 π−1/2/79/30 區而非 φ²", 
    abs(alphas[imin] - math.pi + 0.5) < 0.1 or abs(alphas[imin] - 79/30) < 0.1,
    f"極小 @ {alphas[imin]:.3f}")

# ── R3: 誠實裁定 ──
print("\n── R3: R38 固化判決重審 ──")
print("   R38 H2 用粗網格 {1.5,2.0,2.5,φ²,3.0,3.5,4.0} 宣稱『唯一極小+鄰點×1.3』")
print("   ⟹ 網格內唯一, 唔係候選空間唯一:")
print(f"   - 候選集空間: 最佳 {best_name}={best_lv:.4f} < φ²={phi_lv:.4f}")
print(f"   - 細網格空間: 極小 @ {alphas[imin]:.3f}={vals[imin]:.4f}")
c1 = best_lv < phi_lv
c2 = vals[imin] < phi_lv - 1e-9
if c1 or c2:
    verdict = "📉 R38『α=φ² 結構固化』降級: φ² 唔係候選空間/細網格唯一極小 —— O136 docs/35 否證維持; R38 只證明『粗網格內 φ² 局部好』"
else:
    verdict = "🟡 R38 固化維持（φ² 全空間唯一極小, 需再驗 MC null）"
print(f"   裁定: {verdict}")
chk("R3 誠實降級/維持", (c1 or c2), verdict[:80])

json.dump({
    "verdict": verdict,
    "candidates_loocv": res,
    "free_loocv": free_lv,
    "grid": {"alphas": alphas.tolist() if len(alphas) < 100 else alphas[::4].tolist(),
             "vals": vals.tolist() if len(vals) < 100 else vals[::4].tolist(),
             "global_min_alpha": float(alphas[imin]), "global_min_loocv": float(vals[imin])},
    "note": "O136 scripts/92 + docs/43 觸發; R38 固化判決需修正",
}, open("data/48_freeze_reaudit.json", "w"), indent=1, ensure_ascii=False)

print(f"\n判定: {sum(1 for _, c in P if c)}/{len(P)} PASS")