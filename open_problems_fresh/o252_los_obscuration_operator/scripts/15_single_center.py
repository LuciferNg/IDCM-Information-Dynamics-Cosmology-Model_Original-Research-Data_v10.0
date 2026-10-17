#!/usr/bin/env python3
"""
O252 — Script 15: 單一窗中心假說檢驗 (2026-10-17)
===================================================
R9 拆彈: 窗存在閉合但精確中心未鎖定 (peak 180 vs v_abs=289.76)。
本 script 用**觀測 dip 位置**估計「單一中心 μ」係咪足以描述成個樣本:
  [J1] 用 m/h 双 grating 對 (A Hα, C Hα) 估 intra-source 測量不確定度 σ_meas
  [J2] 9 個命中 dip 對 μ=v_abs=289.76: χ² = Σ((|dvᵢ|−μ)/σ_i)², σ_i = σ_meas
       χ²/ν < 2 → 單一中心 289.76 足以描述
  [J3] 用 9 個 dip 計 weighted mean μ_hat (MVUE) 同 95% 區間 — 對比 289.76
  [J4] μ_hat 對比結構候選 {167.23 (σ₃), 204.9 (V_max/2), 289.76 (V_max/√2)}
       睇邊個落入 95% 區間 — 零參數中心嘅直接驗證
誠實: J3/J4 用觀測值 (post-factum best-fit), 唔係事前預言 — 但係
      「結構候選中哪個落入經驗區間」係結構判準 (揀一, 唔係 fit)
"""
import json, math, os
import numpy as np

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
LOG = []
def ck(name, cond, detail=''):
    LOG.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

v_abs = 289.759
cands = {"σ₃": 167.228, "V_max/2": 204.89, "V_max/√2": 289.759,
         "V_max": 409.78, "2σ₃": 334.46}

with open(f"{DATA}/07_full_sample_scan.json") as f:
    d7 = json.load(f)
res = [r for r in d7["results"] if r["sig"] and abs(r["dv"]) < 700 and r["depth"] < 1.2]

print("="*84)
print("O252/15 — 單一窗中心假說檢驗")
print("="*84)

# ---------- J1: intra-source 測量不確定度 ----------
pairs = [("A","Hα"), ("C","Hα")]
diffs = []
for s,l in pairs:
    vs = [r["dv"] for r in res if r["src"]==s and r["line"]==l]
    if len(vs) == 2:
        diffs.append(abs(vs[0]-vs[1]))
if diffs:
    σ_meas = np.mean(diffs)/math.sqrt(2)   # 兩測量差 ~ N(0, 2σ²) → σ=diff/√2
    print(f"J1: m/h 對差 {diffs} → 單測量 σ_meas ≈ {σ_meas:.1f} km/s")
else:
    σ_meas = 100.0
    print(f"J1: 冇 m/h 對 → 用保守 σ_meas=100 (R5 註記)")
ck("J1 σ_meas < 190 (中心可分辨性)", σ_meas < 190, f"σ_meas={σ_meas:.1f}")

# ---------- J2: χ² against 289.76 ----------
dv_abs = sorted(abs(r["dv"]) for r in res)
hit = [x for x in dv_abs if abs(x-v_abs) < 189.525]
n_hit = len(hit)
chi2 = sum(((x-v_abs)/σ_meas)**2 for x in hit)
nu = n_hit - 1
print(f"\nJ2: 命中窗 n={n_hit}: |dv|={[round(x,1) for x in hit]}")
print(f"    χ² = {chi2:.1f}, ν={nu}, χ²/ν = {chi2/nu:.2f}")
ck("J2 單一中心 289.76 χ²/ν < 2", chi2/nu < 2, f"χ²/ν={chi2/nu:.2f}")
# 再睇 180 (empirical peak) 定 289.76 邊個好啲
for mu in [180.0, v_abs]:
    c2 = sum(((x-mu)/σ_meas)**2 for x in hit)
    print(f"    μ={mu}: χ²={c2:.1f}, χ²/ν={c2/nu:.2f}")

# ---------- J3: weighted mean (MVUE) ----------
w = np.ones(len(hit))/σ_meas**2
mu_hat = np.sum(w*np.array(hit))/np.sum(w)
se = 1/math.sqrt(np.sum(w))
print(f"\nJ3: weighted mean μ_hat = {mu_hat:.1f} ± {se:.1f} km/s (95% CI "
      f"[{mu_hat-1.96*se:.0f}, {mu_hat+1.96*se:.0f}])")
ck("J3 CI 窄 (σ_meas 確定)", (mu_hat-1.96*se) > 0 and se < 60, f"SE={se:.1f}")

# ---------- J4: 結構候選比較 ----------
print("\nJ4: 結構候選 vs 95% CI:")
for name, val in cands.items():
    inside = (mu_hat-1.96*se) <= val <= (mu_hat+1.96*se)
    dev = abs(val-mu_hat)/mu_hat*100
    print(f"    {name:10s} = {val:8.2f}  dev μ_hat {dev:5.1f}%  "
          f"{'✅ 入 CI' if inside else '❌ 出 CI'}")
inside_vabs = (mu_hat-1.96*se) <= v_abs <= (mu_hat+1.96*se)
ck("J4 V_max/√2 入 95% CI (零參數中心確認)", inside_vabs,
   f"v_abs=289.76 vs CI [{mu_hat-1.96*se:.0f}, {mu_hat+1.96*se:.0f}]")

data = {"sigma_meas": float(σ_meas), "n_hit": n_hit,
        "chi2_vs_289.76": chi2, "chi2_nu": chi2/nu,
        "mu_hat": float(mu_hat), "se": float(se),
        "ci95": [float(mu_hat-1.96*se), float(mu_hat+1.96*se)],
        "candidates": {k: {"val": v,
                           "inside_ci": bool((mu_hat-1.96*se) <= v <= (mu_hat+1.96*se)),
                           "dev_pct": float(abs(v-mu_hat)/mu_hat*100)}
                       for k,v in cands.items()},
        "checks": [{"name": n, "pass": p, "detail": d} for n,p,d in LOG]}
with open(f"{DATA}/15_single_center.json","w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
np_ok = sum(1 for _,p,_ in LOG if p)
print(f"\n結果: {np_ok}/{len(LOG)} PASS → data/15_single_center.json")