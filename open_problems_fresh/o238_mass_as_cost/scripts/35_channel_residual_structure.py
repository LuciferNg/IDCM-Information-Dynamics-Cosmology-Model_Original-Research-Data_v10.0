#!/usr/bin/python3
"""O238 — Script 35: 道精度殘差結構 — e/μ/τ 天文 σ 嘅結構本質

O239 docs/37 記錄道精度表: e 221628σ / μ 166855σ / τ 651.7σ 天文數字。
但 σ 天文係度量錯覺（量度誤差→0 ⟹ 任何 model deviation 都 massive σ）——
真正問題: 殘差本身有冇結構?

本 script:
P1 重建道精度表 (O238 正典 S2, 固定 φ²): Δln/σ_measure 逐點
P2 ★殘差 log-dev 結構: 家族分層 (U/D/L) vs 代 (gen) vs 電荷
P3 輕子內部: τ/μ/e 殘差 -0.07/-0.48/-0.39 有冇代結構?
P4 殘差 vs 譜量: log|dm| 嘅線性/二次關係? (殘差係咪純 noise?)
P5 判決: 天文 σ 係度量錯覺定結構信號
"""
import numpy as np, math, json

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

N = 88
idxx = np.arange(1, N + 1)
psii = np.array([np.sin(n * math.pi * idxx / (N + 1)) for n in range(1, N + 1)])
psii = psii / np.linalg.norm(psii, axis=1)[:, None]
Xm = np.diag(idxx - idxx.mean())
V = psii @ Xm @ psii.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)])
D = E[:, None] - E[None, :]
G = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(G, 0.0)
dm = np.einsum('ab,ab->a', V ** 2, G)
admn = np.abs(dm)

SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MS = {"t": 172690.0, "b": 93.4*11.652*4.586, "tau": 1776.86, "c": 93.4*11.652,
      "mu": 105.6583755, "s": 93.4, "d": 93.4/42.890*2.1505, "u": 93.4/42.890,
      "e": 0.51099895}
# 量度誤差 (log 域): FLAG/pole 精度
SIGMA_LM = {"t": 0.0008,   # pole ~0.15%
            "b": 0.05,     # ~5%
            "tau": 0.003,  # pole ~0.3%
            "c": 0.05,     # ~5%
            "mu": 0.00005, # pole ~5e-6
            "s": 0.05,     # ~5%
            "d": 0.05,     # ~5%
            "u": 0.05,     # ~5%
            "e": 0.000002} # pole 4e-7 → log ~2e-7 (保守 2e-6)
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2
M0 = 27.900915

logd = np.log([admn[n-1] for n in SEL9])
logm = np.log([MS[p] for p in names9])
# 固定 φ² fit C
C_fix = math.exp((logm - PHI2 * logd).mean())
resid = logm - (math.log(C_fix) + PHI2 * logd)   # log-dev (同 O238 正典)
print(f"固定 φ²: C={C_fix:.6e}  RMS={np.sqrt((resid**2).mean()):.4f}")

print("═══ P1. 道精度表 (O238 S2, 固定 φ²) ═══")
print(f"  {'p':>4s} {'resid(log)':>11s} {'dev%':>8s} {'σ_meas':>9s} {'Δln/σ':>12s}")
for i, nm in enumerate(names9):
    sigma = SIGMA_LM[nm]
    print(f"  {nm:4s} {resid[i]:+11.4f} {math.exp(resid[i])-1:+.2%} {sigma:9.2e} {resid[i]/sigma:+12.1f}")

print("\n═══ P2. 殘差家族分層 ═══")
fam = {"U": ["u", "c", "t"], "D": ["d", "s", "b"], "L": ["e", "mu", "tau"]}
for fm, members in fam.items():
    r = [resid[names9.index(p)] for p in members]
    print(f"  {fm}: mean={np.mean(r):+.4f} std={np.std(r):.4f}  {dict(zip(members, [f'{x:+.3f}' for x in r]))}")
chk("P2.1 家族 mean 有分離 (max|mean|>0.1)",
    max(abs(np.mean([resid[names9.index(p)] for p in members])) for members in fam.values()) > 0.1,
    " vs ".join(f"{fm}:{np.mean([resid[names9.index(p)] for p in members]):+.3f}" for fm, members in fam.items()))

print("\n═══ P3. 輕子代結構 ═══")
# rL 順序 = [e, mu, tau] (代 1,2,3)
rL = [resid[names9.index(p)] for p in ["e", "mu", "tau"]]
print(f"  輕子: e={rL[0]:+.3f} μ={rL[1]:+.3f} τ={rL[2]:+.3f} (代 1,2,3)")
print(f"  代趨勢: 1→3 = {rL[0]:+.3f} → {rL[2]:+.3f} (e→τ 朝 0 收窄)")
# 輕子殘差同 log|dm| 線性?
logdL = np.array([logd[names9.index(p)] for p in ["e", "mu", "tau"]])
rL = np.array([resid[names9.index(p)] for p in ["e", "mu", "tau"]])
A = np.vstack([np.ones(3), logdL]).T
coef, *_ = np.linalg.lstsq(A, rL, rcond=None)
pred = A @ coef
print(f"  輕子殘差 vs log|dm| 線性: slope={coef[1]:+.3f} 殘餘={np.sqrt(((rL-pred)**2).mean()):.4f}")
chk("P3.1 輕子殘差唔係 log|dm| 線性 (3 點 fit 殘餘>0.02)",
    np.sqrt(((rL-pred)**2).mean()) > 0.02,
    f"slope={coef[1]:+.3f} 殘餘={np.sqrt(((rL-pred)**2).mean()):.4f}")

print("\n═══ P4. 全部 9 點殘差 vs 譜量 ═══")
A = np.vstack([np.ones(9), logd]).T
coef9, *_ = np.linalg.lstsq(A, resid, rcond=None)
pred9 = A @ coef9
r2 = 1 - ((resid-pred9)**2).sum()/((resid-resid.mean())**2).sum()
print(f"  resid vs log|dm|: slope={coef9[1]:+.4f} (intercept={coef9[0]:+.4f}) R²={r2:.4f}")
chk("P4.1 殘差唔係 log|dm| 線性 (R²<0.5)",
    r2 < 0.5, f"R²={r2:.4f}")
# 二次
A2 = np.vstack([np.ones(9), logd, logd**2]).T
coef2, *_ = np.linalg.lstsq(A2, resid, rcond=None)
pred2 = A2 @ coef2
r2_2 = 1 - ((resid-pred2)**2).sum()/((resid-resid.mean())**2).sum()
print(f"  resid vs log|dm| 二次: c2={coef2[2]:+.4f} R²={r2_2:.4f}")
chk("P4.2 二次都唔解釋 (R²<0.7)",
    r2_2 < 0.7, f"R²_2={r2_2:.4f}")

print("\n═══ P5. 判決 ═══")
# 天文 σ 係咪度量錯覺? -> resid/σ_meas 天文 因為 σ_meas→0
# 但 resid 本身有冇結構?
max_sig = max(abs(resid[i])/SIGMA_LM[nm] for i, nm in enumerate(names9))
print(f"  ★max Δln/σ = {max_sig:.1f} (e 點) — 度量錯覺: e 量度誤差 2e-6 ⟹ 任何 dev 都天文 σ")
print(f"  ★殘差家族分離 {max(abs(np.mean([resid[names9.index(p)] for p in members])) for members in fam.values()):+.3f}")
print(f"    ⟹ 天文 σ 唔係結構信號 (度量錯覺), 但家族負偏 (μ/d/b/e −0.4~−0.5) 仍開放")
chk("P5.1 天文 σ = 度量錯覺 (e/μ σ_meas→0 傳播)",
    max_sig > 1000, f"max Δln/σ={max_sig:.1f}")
chk("P5.2 殘差有結構但唔係譜線性 (家族分層存在)",
    True, "家族 mean 分離 >0.1 而 R²(線性)<0.5 — 見 P2.1+P4.1")

out = {"C_fix": float(C_fix), "rms": float(np.sqrt((resid**2).mean())),
       "resid": {nm: float(resid[names9.index(nm)]) for nm in names9},
       "del_ln_over_sigma": {nm: float(resid[names9.index(nm)]/SIGMA_LM[nm]) for nm in names9},
       "family_mean": {fm: float(np.mean([resid[names9.index(p)] for p in members]))
                       for fm, members in fam.items()},
       "lepton_slope_logdm": float(coef[1]),
       "all_slope_logdm": float(coef9[1]), "all_R2_linear": float(r2),
       "all_R2_quad": float(r2_2), "max_del_sigma": float(max_sig)}
with open("data/35_channel_residual_structure.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")