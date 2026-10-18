#!/usr/bin/env python3
"""
O252 — Script 21: 每源凝聚密度可行性診斷 (2026-10-17)
=====================================================
問題: 深度 per-source scatter (0.44-0.95) 有冇結構可推?
      (每源凝聚密度 = 每源 M₄/M₀ 或 ℓ_band(θ(v)) 投影)

步驟:
  A. 相關矩陣: depth vs {dv, |dv|, sig_dip, dAIC} (Pearson+Spearman)
  B. 類別測試: line (Hα/Hβ), side (藍/紅), 每源 — depth 差異 (Welch t)
  C. 帶幾何 ℓ_band 預言 vs obs — 殘差有冇結構
     ℓ_band(θ(v)): 帶長比 17/15 → depth_band = 1−exp(−τ_eff·ℓ_band/ℓ_ref)
  D. 判準: 可推 (相關顯著 + 殘差有結構) / 不可推 (全無結構 = noise)
"""
import json, math, os
import numpy as np

DATA = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/data"
LOG = []
def ck(name, cond, detail=''):
    LOG.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

d07 = json.load(open(f"{DATA}/07_full_sample_scan.json"))
res = [r for r in d07["results"] if r["sig"] and 0.05 <= r["depth"] <= 1.0
       and abs(r["dv"]) < 700]   # 剔 bound/退化 fit (J Hβ +493 depth1.5, E Hβ −800)
print(f"分析樣本: {len(res)} 顯著 dip (剔 bound/退化)")

depth = np.array([r["depth"] for r in res])
dv    = np.array([r["dv"] for r in res])
adv   = np.abs(dv)
sig   = np.array([r["sig_dip"] for r in res])
aic   = np.array([r["dAIC"] for r in res])
srcs  = [r["src"] for r in res]
lines = [r["line"] for r in res]

def corr(x, y, method="pearson"):
    if len(x) < 3: return (float("nan"), 1.0)
    if method == "pearson":
        return (float(np.corrcoef(x, y)[0, 1]), float(np.nan))
    from scipy import stats
    r, p = stats.spearmanr(x, y)
    return (float(r), float(p))

print("\n=== A. 相關矩陣 (depth vs 每源量) ===")
for name, x in [("dv", dv), ("|dv|", adv), ("sig_dip", sig), ("dAIC", aic)]:
    rp, _ = corr(depth, x)
    print(f"  depth vs {name:8s}: Pearson ρ={rp:+.3f}")

# B. 類別測試
print("\n=== B. 類別 depth 差異 ===")
for lbl, mask in [("Hα", [l=="Hα" for l in lines]),
                  ("藍側 dv<0", [v<0 for v in dv]),
                  ("紅側 dv>0", [v>0 for v in dv])]:
    m = np.array(mask)
    if m.sum() >= 2 and (~m).sum() >= 2:
        a, b = depth[m], depth[~m]
        from scipy import stats
        t, p = stats.ttest_ind(a, b, equal_var=False)
        print(f"  {lbl:9s}: n={m.sum():2d} mean={a.mean():.3f} vs 其他 n={(~m).sum():2d} "
              f"mean={b.mean():.3f} — Welch t={t:+.2f} p={p:.3f}")
    else:
        print(f"  {lbl:9s}: n 太少跳過")

# C. 帶幾何預言殘差
print("\n=== C. 帶幾何 ℓ_band 預言 vs obs ===")
# 帶幾何: 視線光程 ∝ |v| 帶內位置 (R6: ρ=+0.466 弱正相關)
tau_eff = 28/15
# ℓ_band(θ): θ(v)=arccos(v/c) — 光程長 ∝ 1/cos? 用最簡 ℓ ∝ |dv|/dv_max 線性代理
# (R6 冇鎖定函數形式 — 呢度只測「線性 |dv| 預言」可唔可以解釋 scatter)
dvmax = 409.78
x_lin = adv / dvmax
# 線性 fit depth ~ x_lin
A = np.vstack([x_lin, np.ones_like(x_lin)]).T
coef, res_, _, _ = np.linalg.lstsq(A, depth, rcond=None)
pred_lin = A @ coef
resid = depth - pred_lin
print(f"  depth ~ α·(|dv|/dvmax)+β: α={coef[0]:+.3f} β={coef[1]:+.3f}")
print(f"  R²={1-res_.sum()/((depth-depth.mean())**2).sum():.3f} (線性 |dv| 預言)")
print(f"  obs depth 範圍 [{depth.min():.3f},{depth.max():.3f}], "
      f"殘差 std={resid.std():.3f} (scatter 未被 |dv| 解釋)")
# 殘差 vs 其他量
for name, x in [("dv", dv), ("sig_dip", sig), ("dAIC", aic)]:
    rp, _ = corr(resid, x)
    print(f"  殘差 vs {name:8s}: ρ={rp:+.3f}")

# D. 判準
print("\n=== D. 判準 ===")
scat = float(depth.std())
linr = float(abs(np.corrcoef(adv, depth)[0,1]))
ck("|dv| 相關 < 0.3 (帶幾何唔主導)", linr < 0.3, f"ρ={linr:.3f}")
ck("殘差 vs 每源量全無關 (無結構可推)", all(abs(corr(resid, x)[0]) < 0.3
   for x in (dv, sig, aic)), "")
print(f"scatter std = {scat:.3f} (τ_eff=28/15 預言 0.845, 殘差 std {resid.std():.3f})")
verdict = "🔴 唔可推: depth scatter 係 noise/外部 absorber 性質, 冇每源結構量可預測" \
    if abs(corr(adv, depth)[0]) < 0.3 and all(abs(corr(resid, x)[0]) < 0.3
           for x in (dv, sig, aic)) else \
    "🟡 部分可推: 有弱結構但 n 細, 需更多源先鎖定函數形式"
print(f"\n裁決: {verdict}")

out = {"n": len(res),
       "corr_depth_dv": corr(depth, dv)[0], "corr_depth_adv": corr(depth, adv)[0],
       "corr_depth_sig": corr(depth, sig)[0], "corr_depth_aic": corr(depth, aic)[0],
       "lin_fit": {"alpha": float(coef[0]), "beta": float(coef[1]),
                   "R2": float(1-res_.sum()/((depth-depth.mean())**2).sum())},
       "resid_std": float(resid.std()), "depth_std": scat,
       "rows": [{"src": s, "line": l, "dv": float(v), "depth": float(dp),
                 "resid": float(rr)} for s, l, v, dp, rr in
                zip(srcs, lines, dv, depth, resid)],
       "verdict": verdict,
       "checks": [{"name": n, "pass": p, "detail": x} for n, p, x in LOG]}
with open(f"{DATA}/21_density_feasibility.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
ok = sum(1 for _, p, _ in LOG if p)
print(f"\n結果: {ok}/{len(LOG)} → data/21_density_feasibility.json")