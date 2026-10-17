#!/usr/bin/env python3
"""
O252 — Script 16: hop=2 中心檢驗 (後驗, μ_hat 導出) (2026-10-17)
=================================================================
R10: μ_hat=235.7±21.6, V_max/2=204.9 (hop=2) 係唯一入 CI 結構候選。
⚠️ POST-HOC: 候選由観測位置導出, 唔係事前預言 — 測試只係辨識力,
   唔可以當獨立命中統計。誠實標記。
檢驗:
  [H2a] 窗中心 204.9±189.52: 12 個獨立 dip 使命率
  [H2b] χ² (對 204.9) vs χ² (對 289.76) — 邊個中心描述更好
  [H2c] MC null: 均勻池中 204.9 窗命中率 vs 289.76 窗 (p_single)
  [H2d] hop=2 結構身份: n=8 節點層, M₂/M₀? (O179: hop=2 → W 權重?)
"""
import json, math, os
import numpy as np

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
LOG = []
def ck(name, cond, detail=''):
    LOG.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

sig_E = 189.525
v_abs4 = 289.759          # hop=4
v_abs2 = 204.89           # hop=2, V_max/2

with open(f"{DATA}/07_full_sample_scan.json") as f:
    d7 = json.load(f)
res = [r for r in d7["results"] if r["sig"] and abs(r["dv"]) < 700 and r["depth"] < 1.2]
# 去重 (每源·線, 優先 h)
gr_rank = {'g395h': 0, 'g395m': 1}
best = {}
for r in res:
    key = (r["src"], r["line"])
    g = r.get("grating", "g395m")
    if key not in best or gr_rank.get(g,1) < gr_rank.get(best[key].get("grating","g395m"),1):
        best[key] = r
uniq = list(best.values())
dv = np.array([r["dv"] for r in uniq])
dv_abs = np.abs(dv)
n = len(dv)

print("="*84)
print("O252/16 — hop=2 中心檢驗 ⚠後驗 (μ_hat 導出)")
print("="*84)
print(f"n={n} 獨立 dip: |dv| = {sorted(round(x,1) for x in dv_abs)}")

def hit_frac(center, width):
    h = np.sum((dv_abs >= center-width) & (dv_abs <= center+width))
    return int(h), h/n

for name, c in [("hop4 289.76", v_abs4), ("hop2 204.89", v_abs2), ("μ_hat 235.7", 235.7)]:
    nh, frac = hit_frac(c, sig_E)
    print(f"  窗中心 {name:12s} ({c:6.1f}): 命中 {nh}/{n} ({frac*100:.0f}%)")

# H2a: hop=2 使命率
nh2, f2 = hit_frac(v_abs2, sig_E)
nh4, f4 = hit_frac(v_abs4, sig_E)
print(f"\nH2a: hop=2 命中 {nh2}/{n} vs hop=4 命中 {nh4}/{n}")
ck("H2a hop=2 使命率 ≥ hop=4", nh2 >= nh4, f"{nh2} vs {nh4}")

# H2b: χ² 比較 (用 σ_meas=71.6)
sigma_m = 71.6
chi2_4 = sum(((x-v_abs4)/sigma_m)**2 for x in dv_abs)
chi2_2 = sum(((x-v_abs2)/sigma_m)**2 for x in dv_abs)
chi2_m = sum(((x-235.7)/sigma_m)**2 for x in dv_abs)
print(f"H2b: χ²(hop4)= {chi2_4:.1f}, χ²(hop2)= {chi2_2:.1f}, χ²(μ_hat)= {chi2_m:.1f} "
      f"(ν={n-1})")
ck("H2b hop=2 χ² < hop=4", chi2_2 < chi2_4, f"{chi2_2:.1f} < {chi2_4:.1f}")

# H2c: MC null (均勻 ±1500)
rng = np.random.default_rng(90210)
n_sim = 20000
mc4 = np.zeros(n_sim); mc2 = np.zeros(n_sim)
for i in range(n_sim):
    pts = rng.uniform(0, 1500, n)
    mc4[i] = np.sum((pts >= v_abs4-sig_E) & (pts <= v_abs4+sig_E))
    mc2[i] = np.sum((pts >= v_abs2-sig_E) & (pts <= v_abs2+sig_E))
p4 = np.mean(mc4 >= nh4)
p2 = np.mean(mc2 >= nh2)
print(f"H2c: MC null p(hop4)={p4:.4g}, p(hop2)={p2:.4g} (窗命中 {nh4} vs {nh2})")
ck("H2c hop2 MC null < 0.01", p2 < 0.01, f"p={p2:.4g}")
ck("H2c' hop4 MC null 維持 < 0.01", p4 < 0.01, f"p={p4:.4g}")

# H2d: hop=2 結構身份 — O179 W 權重
# W(hop) ∝ W₀·[1+(B/L₅)cos(π·hop/4)] (docs/01_position_dof)
# L₅=11, B=4, W₀ ~ 7.842?  用 W 權重比 W(2)/W(4)
B, L5 = 4, 11
def W(hop): return 1+(B/L5)*math.cos(math.pi*hop/4)
w2, w4 = W(2), W(4)
print(f"H2d: W(hop=2)={w2:.4f}, W(hop=4)={w4:.4f} → 比 {w2/w4:.3f} "
      f"(hop=2 質量權重較低 ✓? 吸收少啲)")
print(f"    M₄/M₀=7/15=0.4667 (O179); M₂/M₀=? (若 W²∝M: {w2*w2:.3f})")
ck("H2d hop=2 W 權重 < hop=4 (吸收層係 hop=2?)", abs(w2) < abs(w4),
   f"W2={w2:.3f} vs W4={w4:.3f}")

data = {"post_hoc": True, "note": "候選由 μ_hat=235.7 導出 — 只係辨識力",
        "n": n,
        "hits_hop4": int(nh4), "hits_hop2": int(nh2),
        "chi2_hop4": float(chi2_4), "chi2_hop2": float(chi2_2),
        "mc_p_hop4": float(p4), "mc_p_hop2": float(p2),
        "W2": w2, "W4": w4,
        "checks": [{"name": x, "pass": p, "detail": d} for x,p,d in LOG]}
with open(f"{DATA}/16_hop2_center.json","w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
np_ok = sum(1 for _,p,_ in LOG if p)
print(f"\n結果: {np_ok}/{len(LOG)} PASS → data/16_hop2_center.json")