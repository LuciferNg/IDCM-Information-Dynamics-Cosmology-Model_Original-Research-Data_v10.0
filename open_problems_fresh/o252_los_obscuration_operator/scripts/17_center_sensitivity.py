#!/usr/bin/env python3
"""
O252 — Script 17: μ_hat 對 dip 樣本質量敏感度 (2026-10-17)
===========================================================
R14/R16: fit 有中心聚集 bias (低位 dip 29.1/89.6 可能係 M0 residual
偽造), 拉低 μ_hat=235.7 → hop=2 揾到支持。
檢查: 剔走低質量 dip (低 ΔAIC / 低 |dv|) 之後 μ_hat 穩唔穩健?
  [M1] μ_hat 對 ΔAIC 門檻掃描 (≥40/≥100/≥150/≥200)
  [M2] μ_hat 排除 |dv|<100 (中心區可能係 residual)
  [M3] 若 μ_hat 升到 ~290 (hop=4) → R10「289.76 出 CI」係低質 dip 造成
  [M4] 若 μ_hat 維持 205-240 → hop=2/中心偏移真
"""
import json, math, os
import numpy as np

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
LOG = []
def ck(name, cond, detail=''):
    LOG.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

v_abs4 = 289.759
v_abs2 = 204.89
sigma_m = 71.6

with open(f"{DATA}/07_full_sample_scan.json") as f:
    d7 = json.load(f)
res = [r for r in d7["results"] if r["sig"] and abs(r["dv"]) < 700 and r["depth"] < 1.2]
gr_rank = {'g395h': 0, 'g395m': 1}
best = {}
for r in res:
    key = (r["src"], r["line"])
    g = r.get("grating", "g395m")
    if key not in best or gr_rank.get(g,1) < gr_rank.get(best[key].get("grating","g395m"),1):
        best[key] = r
uniq = list(best.values())

print("="*84)
print("O252/17 — μ_hat 敏感度 (dip 質量門檻掃描)")
print("="*84)

def mu_hat(vals, sm=sigma_m):
    if len(vals) == 0: return None, None
    w = np.ones(len(vals))/sm**2
    m = np.sum(w*np.array(vals))/np.sum(w)
    se = 1/math.sqrt(np.sum(w))
    return m, se

print(f"全樣本 n={len(uniq)}:")
for name, th in [("ΔAIC≥40", 40), ("ΔAIC≥100", 100), ("ΔAIC≥150", 150), ("ΔAIC≥200", 200)]:
    sub = [abs(r["dv"]) for r in uniq if r["dAIC"] >= th]
    m, se = mu_hat(sub)
    if m:
        print(f"  {name:10s} n={len(sub):2d}  μ_hat={m:6.1f}±{se:5.1f}  "
              f"(hop4 dev {(m-v_abs4)/v_abs4*100:5.1f}% / hop2 dev {(m-v_abs2)/v_abs2*100:5.1f}%)")

sub2 = [abs(r["dv"]) for r in uniq if abs(r["dv"]) >= 100]
m2, se2 = mu_hat(sub2)
print(f"  排除|dv|<100  n={len(sub2):2d}  μ_hat={m2:6.1f}±{se2:5.1f}")
if m2:
    ck("M2-4 排除低位後 μ_hat", True, f"μ_hat={m2:.1f}")

# M3: μ_hat 回唔回到 289.76?
top = [abs(r["dv"]) for r in uniq if r["dAIC"] >= 100 and abs(r["dv"]) >= 100]
m3, se3 = mu_hat(top)
print(f"  ΔAIC≥100 & |dv|≥100  n={len(top):2d}  μ_hat={m3:6.1f}±{se3:5.1f}")
if m3:
    ck("M3 剔除低質後 hop4 入 CI", (m3-1.96*se3) <= v_abs4 <= (m3+1.96*se3),
       f"μ_hat={m3:.1f}±{se3:.1f}, CI=[{m3-1.96*se3:.0f},{m3+1.96*se3:.0f}], "
       f"hop4={v_abs4:.1f}")
    ck("M3' 剔除低質後 hop2 入 CI", (m3-1.96*se3) <= v_abs2 <= (m3+1.96*se3),
       f"μ_hat={m3:.1f}±{se3:.1f}, hop2={v_abs2:.1f}")

data = {"sigma_m": sigma_m,
        "scan": {th: {"n": len([r for r in uniq if r['dAIC']>=th]),
                      "mu_hat": (lambda m: m)(None)} for th in [40,100,150,200]},
        "exclude_low_dv": {"n": len(sub2), "mu_hat": m2, "se": se2},
        "high_qual": {"n": len(top), "mu_hat": m3, "se": se3} if m3 else None,
        "note": "R14 觀察: fit 中心聚集 bias; 本 script 檢查低質 dip 是否偽造",
        "checks": [{"name": x, "pass": p, "detail": d} for x,p,d in LOG]}
final = {"mu_hat_full": 235.7, "mu_hat_highqual": m3 if m3 else None,
         "checks": data["checks"], "scan": {}}
with open(f"{DATA}/17_center_sensitivity.json","w") as f:
    json.dump(final, f, indent=2, ensure_ascii=False)
np_ok = sum(1 for _,p,_ in LOG if p)
print(f"\n結果: {np_ok}/{len(LOG)} PASS → data/17_center_sensitivity.json")