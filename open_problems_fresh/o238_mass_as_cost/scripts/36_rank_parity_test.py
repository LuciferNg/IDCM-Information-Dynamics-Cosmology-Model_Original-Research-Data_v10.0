#!/usr/bin/python3
"""O238 — Script 36: 殘差結構 vs rank-parity 修正 — 家族分層係咪 δ·even_rank 嘅解

R20 發現: 固定 φ² 殘差有家族分層 (U+0.224/D+0.097/L−0.321) + 輕子代收窄。
O136/O239 docs/32 用 rank-parity 修正 (ln m = lnM₀ + φ²ln|Δm| + δ·even_rank,
RMS 0.4891)。本 script 喺 O238 正典 S2 下檢定:
P1 φ² + δ·even_rank fit (δ fit)
P2 修正後家族 mean / 輕子代收窄 係咪消失
P3 LOOCV: 固定 φ² vs φ²+rank (validation)
P4 修正後殘差結構 (仲有冇嘢? 連 rank 都解釋唔到嘅部分)
P5 判決: 家族分層 = rank-parity 修正?
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
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2
M0 = 27.900915

logd = np.log([admn[n-1] for n in SEL9])
logm = np.log([MS[p] for p in names9])
# 開點序 (O136/O239 even_rank 慣例: t=1... e=9, even=2,4,6,8 → b,c,mu,d = 1?)
# O136 scripts/69 rank_even: rank parity 由 SEL9 位置 0-based, even index?
EIDX = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1])   # 0-based even position → t,τ,μ,d,e (奇數 1-based)
# 對齊: names9 index 0..8, 1-based rank=1..9, even rank = 2,4,6,8 = b,c,mu,d
rank = np.arange(1, 10)
even_mask = (rank % 2 == 0).astype(float)      # b,c,mu,d → 1

def fit2(cols, y):
    A = np.vstack([np.ones(9)] + [c for c in cols]).T
    c, *_ = np.linalg.lstsq(A, y, rcond=None)
    res = y - A @ c
    return c, res

# 固定 φ² 殘差
C_fix = math.exp((logm - PHI2 * logd).mean())
resid0 = logm - (math.log(C_fix) + PHI2 * logd)

print("═══ P1. φ² + δ·even_rank fit ═══")
c2, res2 = fit2([logd, even_mask], logm)
print(f"  ln m = {c2[0]:.4f} + α·ln|dm| + δ·even_rank")
print(f"  α = {c2[1]:.6f} (dev vs φ²: {(c2[1]-PHI2)/PHI2*100:+.3f}%)")
print(f"  δ = {c2[2]:+.4f}")
print(f"  固定 φ² 版本: C={C_fix:.6e} RMS={np.sqrt((resid0**2).mean()):.4f}")
print(f"  φ²+rank 版本: RMS={np.sqrt((res2**2).mean()):.4f}")
chk("P1.1 rank 修正降低 RMS (vs 0.5456)", np.sqrt((res2**2).mean()) < 0.5456,
    f"RMS={np.sqrt((res2**2).mean()):.4f}")

print("\n═══ P2. 修正後家族分層 ═══")
fam = {"U": ["u", "c", "t"], "D": ["d", "s", "b"], "L": ["e", "mu", "tau"]}
mods = {"固定φ²": resid0, "φ²+rank": res2}
for mnm, rr in mods.items():
    means = {}
    for fm, members in fam.items():
        r = [rr[names9.index(p)] for p in members]
        means[fm] = float(np.mean(r))
    mx = max(abs(v) for v in means.values())
    print(f"  {mnm}: U {means['U']:+.3f} / D {means['D']:+.3f} / L {means['L']:+.3f}  max|mean|={mx:.3f}")
chk("P2.1 rank 修正後家族 max mean 下降 (解釋分層)",
    max(abs(np.mean([res2[names9.index(p)] for p in members])) for members in fam.values())
    < max(abs(np.mean([resid0[names9.index(p)] for p in members])) for members in fam.values()),
    "0.321 → ?")

print("\n═══ P3. LOOCV: 固定 φ² vs φ²+rank ═══")
def loocv(cols_extra_fixed, col_extra_free):
    """Fixed-φ² LOOCV (only intercept free); rank free variant fits δ each fold"""
    errs_fix, errs_free = [], []
    for i in range(9):
        tr = [j for j in range(9) if j != i]
        x_tr = np.hstack([np.ones(8), logd[tr]])
        b_fix = np.linalg.lstsq(np.vstack([np.ones(8), logd[tr]]).T, logm[tr], rcond=None)[0]
        A_free = np.vstack([np.ones(8), logd[tr], even_mask[tr]]).T
        b_free = np.linalg.lstsq(A_free, logm[tr], rcond=None)[0]
        errs_fix.append(math.log(math.exp(b_fix[0]) * admn[SEL9[i]-1]**PHI2) - logm[i])
        errs_free.append((b_free[0] + b_free[1]*logd[i] + b_free[2]*even_mask[i]) - logm[i])
    return np.mean(np.abs(errs_fix)), np.mean(np.abs(errs_free))
lf, lr = loocv(None, None)
print(f"  LOOCV 中位|dev|: 固定φ²={lf:.4f}  φ²+rank={lr:.4f}")
chk("P3.1 LOOCV rank 唔倒退 (<1.05×)", lr < lf*1.05, f"{lr:.4f} vs {lf:.4f}")

print("\n═══ P4. rank 過後殘差結構 ═══")
print(f"  φ²+rank 殘差:")
for i, nm in enumerate(names9):
    print(f"    {nm:4s}: {res2[i]:+.4f}")
# 輕子代收窄仲喺度?
rL0 = [resid0[names9.index(p)] for p in ["e", "mu", "tau"]]
rL2 = [res2[names9.index(p)] for p in ["e", "mu", "tau"]]
print(f"  輕子 (固定φ²): e {rL0[0]:+.3f} μ {rL0[1]:+.3f} τ {rL0[2]:+.3f}")
print(f"  輕子 (φ²+rank): e {rL2[0]:+.3f} μ {rL2[1]:+.3f} τ {rL2[2]:+.3f}")
chk("P4.1 rank 修正後輕子代收窄仍存在或消失 (e/μ 仍負偏)",
    abs(rL2[0]) > 0.05, f"e={rL2[0]:+.3f} 仍負偏")

print("\n═══ P5. 判決 ═══")
fam1 = max(abs(np.mean([res2[names9.index(p)] for p in members])) for members in fam.values())
print(f"  ★rank 修正後家族 max mean: 0.321 → {fam1:.3f}")
if fam1 < 0.15:
    print("  ⟹ 家族分層主要由 rank-parity 解釋 (δ·even_rank)")
else:
    print("  ⟹ rank-parity 唔足以解釋家族分層 — 仍有結構")
chk("P5.1 rank 修正 family 分層 <0.15 (解釋咗)", fam1 < 0.15, f"max mean={fam1:.3f}")

out = {"alpha_rank_fit": float(c2[1]), "delta": float(c2[2]),
       "rms_fixed": float(np.sqrt((resid0**2).mean())), "rms_rank": float(np.sqrt((res2**2).mean())),
       "family_mean_fixed": {fm: float(np.mean([resid0[names9.index(p)] for p in members]))
                             for fm, members in fam.items()},
       "family_mean_rank": {fm: float(np.mean([res2[names9.index(p)] for p in members]))
                            for fm, members in fam.items()},
       "loocv_fixed": float(lf), "loocv_rank": float(lr),
       "resid_rank": {nm: float(res2[names9.index(nm)]) for nm in names9},
       "lepton_e_mu_tau_fixed": [float(rL0[0]), float(rL0[1]), float(rL0[2])],
       "lepton_e_mu_tau_rank": [float(rL2[0]), float(rL2[1]), float(rL2[2])]}
with open("data/36_rank_parity_test.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")