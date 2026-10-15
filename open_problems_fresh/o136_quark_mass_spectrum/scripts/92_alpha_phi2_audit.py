#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O136 scripts/92 — 獨立審核 O239「α=φ² 結構鎖定」宣稱 (2026-10-15)

背景:
  O136 docs/35 (2026-09-20) 已裁定 α=φ² 唔可辨識 (ΔRMS 0.000423 ≪ bootstrap σ,
  1.89σ, 8/11 候選落喺 1% 寬度內) ⟹ 已排除方向 26。
  O239 docs/32 + scripts/39 (2026-10-12) 宣稱「α=φ² 結構鎖定」, 新論證:
    (1) γ/β 兩條冪律合成 α = γ/β = φ² (代數閉合)
    (2) LOOCV: 固定 φ² (0.3335) 好過自由 α (0.4324)  ⟹ 有獨立預言力
  但 O239 冇做決定性 control: docs/35 嘅 in-sample 最佳候選 π−1/2 同 2+5/8
  喺 LOOCV 下有冇同樣好? 若同樣好 ⟹ φ² 冇特殊性, docs/35 否證維持。

本 script (獨立於 O136 原推導, 由原始常數重算):
  [A] |Δm| 權威重算 (O209 scripts/11 定義: psi norm, V²·Gm, 有符號)
  [B] ln m vs ln|Δm| OLS → α_obs, SE (對齊 O239 scripts/39)
  [C] ★決定性 control: LOOCV 固定 {φ², π−1/2, 2+5/8, 2.633(最優)} + 自由 α
      — 每個候選同一程序, 零特權
  [D] 判定: 若 min(其他候選) ≤ φ² + 0.03 ⟹ φ² 唔係唯一好 LOOCV 值
      ⟹「結構鎖定」宣稱唔成立 (docs/35 否證維持或升級為「LOOCV 都不可辨識」)
"""
import json, math
import numpy as np

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o136_quark_mass_spectrum"

PHI = (1 + 5**0.5) / 2
PHI2 = PHI**2
PARTS = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MODES = [1, 2, 3, 4, 5, 7, 9, 11, 13]
MASS = np.array([172690.0, 4180.0, 1776.86, 1270.0, 105.6584, 93.4, 4.67, 2.16, 0.510999])

CHK = []
def chk(name, ok, msg=""):
    CHK.append((name, bool(ok), msg))
    print(f"   [{'PASS' if ok else 'FAIL'}] {name} — {msg}")

print("O136 scripts/92 — 獨立審核 O239 α=φ² 宣稱")
print("=" * 78)

# ── [A] |Δm| 權威重算 ────────────────────────────────────────────────
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
DMAUTH = [16862, 4988, 2960, 1802, 1187, 609.9, 360.2, 229.9, 152.5]
rel = np.abs(dm - np.array(DMAUTH)) / np.array(DMAUTH)
print("\n[A] |Δm| 重算 vs O136 docs/38 權威表:")
for p, d, r in zip(PARTS, dm, rel):
    print(f"   {p:>4}: {d:9.3f}  rel_delta {r*100:6.4f}%")
chk("A1 |Δm| 9 值重現權威表 (<0.1%)", (rel < 1e-3).all(), f"最大 {rel.max()*100:.4f}%")

# ── [B] OLS ──────────────────────────────────────────────────────────
logm = np.log(MASS)
logdm = np.log(dm)
r = np.polyfit(logdm, logm, 1, cov=True)
a_obs, intc = r[0]
cov = r[1]
# polyfit cov: [[var(a),cov],[cov,var(b)]] — 第 0 個係 slope
a_se = math.sqrt(cov[0][0]) if cov[0][0] > 0 else float("nan")
print(f"\n[B] OLS: α_obs = {a_obs:.6f} ± {a_se:.6f},  dev vs φ² = {abs(a_obs-PHI2)/a_se:.2f}σ")
chk("B1  α_obs 重現 (≈ 2.6333, ±0.01)", abs(a_obs - 2.6333) < 0.01, f"{a_obs:.4f}")

# ── [C] ★決定性 LOOCV control ───────────────────────────────────────
print("\n[C] LOOCV 固定 α 候選 (同一程序, 零特權):")
rank_even = np.array([1.0 if (i + 1) % 2 == 0 else 0.0 for i in range(9)])
Xlist = [logdm, rank_even]

def loocv_fixed(alpha):
    """固定 α: 剔除後 fit intercept+δ (2 free), 預言 θ_i"""
    devs = []
    for i in range(9):
        rest = [np.delete(x, i) for x in Xlist[1:]]
        ys = np.delete(logm, i)
        Xr = np.column_stack([np.ones(8)] + rest)
        c, *_ = np.linalg.lstsq(Xr, ys - alpha * np.delete(logdm, i), rcond=None)
        pred = alpha * logdm[i] + c[0] + sum(c[k+1] * Xlist[k+1][i] for k in range(len(rest)))
        devs.append(abs(logm[i] - pred))
    return float(np.median(devs)), devs

cands = {
    "φ² = 2.6180": PHI2,
    "π−1/2 = 2.6416": math.pi - 0.5,
    "2+5/8 = 2.6250": 2 + 5/8,
    "α_obs = 2.6333": a_obs,
}
results = {}
for name, val in cands.items():
    med, devs = loocv_fixed(val)
    results[name] = {"alpha": val, "loocv_med": med, "devs": devs}
    print(f"   {name:>18}: LOOCV 中位 |dev| = {med:.4f}  (per-point: "
          + ", ".join(f"{d:.2f}" for d in devs) + ")")

# 自由版本 (fit intercept+α+δ, 3 free)
def loocv_free():
    devs = []
    for i in range(9):
        Xs = [np.delete(x, i) for x in Xlist]
        ys = np.delete(logm, i)
        c, *_ = np.linalg.lstsq(np.column_stack([np.ones(8)] + Xs), ys, rcond=None)
        pred = c[0] + sum(c[k+1] * Xlist[k][i] for k in range(len(Xlist)))
        devs.append(abs(logm[i] - pred))
    return float(np.median(devs)), devs
med_free, devs_free = loocv_free()
results["自由 α+δ (3 free)"] = {"alpha": None, "loocv_med": med_free, "devs": devs_free}
print(f"   自由 α+δ (3 free): LOOCV 中位 |dev| = {med_free:.4f}")

# ── [D] 判定 ─────────────────────────────────────────────────────────
print("\n[D] 判定:")
phi_med = results["φ² = 2.6180"]["loocv_med"]
others = {k: v["loocv_med"] for k, v in results.items() if k != "φ² = 2.6180"}
best_other = min(others.values())
best_other_name = min(others, key=lambda k: others[k])
print(f"   φ² LOOCV = {phi_med:.4f}  最佳其他 = {best_other_name} {best_other:.4f}")
print(f"   差 = {abs(phi_med - best_other):.4f}  (O239 門檻 +0.03)")

if best_other <= phi_med + 0.03:
    chk("D1 φ² 唔係唯一好 LOOCV 值 (其他候選 ≤ φ²+0.03)",
        True, f"{best_other_name} {best_other:.4f} ≤ {phi_med:.4f}+0.03 → φ² 冇特殊性")
    verdict = "🔴 O239『α=φ² 結構鎖定』LOOCV 論證唔成立: docs/35 最佳候選 π−1/2 同 2+5/8 喺 LOOCV 下一樣好 (甚至更好) ⟹ α 喺樣本外都不可辨識, docs/35 否證 (排除方向 26) 維持"
else:
    chk("D1 φ² 係唯一好 LOOCV 值", True, f"{best_other:.4f} > {phi_med:.4f}+0.03")
    verdict = "🟡 O239 LOOCV 論證有獨立預言力: 其他候選明顯差過 φ² — 需查 O239 合成律 γ/β 做唔做到 (docs/35 in-sample 否證仍成立但樣本外為 φ² 加分)"
print(verdict)

out = {
    "alpha_obs": a_obs, "alpha_se": a_se, "dev_sigma_vs_phi2": abs(a_obs-PHI2)/a_se,
    "dm9": dm.tolist(), "dm9_auth_delta": (rel*100).tolist(),
    "loocv": {k: {"alpha": v["alpha"], "med": v["loocv_med"]} for k, v in results.items()},
    "verdict": verdict,
}
open(f"{BASE}/data/92_alpha_phi2_audit.json", "w").write(json.dumps(out, indent=1, ensure_ascii=False))
print(f"\n判定: {sum(1 for _, c, _ in CHK if c)}/{len(CHK)} PASS")
print("data/92_alpha_phi2_audit.json written")