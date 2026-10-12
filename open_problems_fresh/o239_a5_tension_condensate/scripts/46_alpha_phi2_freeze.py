#!/usr/bin/python3
"""O239 — Script 46: ★α=φ² 固化測試套件（一票終審, 預註冊判據）
============================================================================
狀態: 2026-10-12（調律者: 「剛先說φ^2 的必然性，現在又降級，要用測試固化
      才對，不然就像C_f一樣浪費時間」）

原則: α=φ² 嘅宣稱強度唔可以再逐輪漂移——預註冊閘門、跑一次、鎖結論。
      以後引用一律用本套件結果（docs/38），唔可以再「睇心情升/降級」。

★閘門（預註冊, 跑到前鎖死, 零放寬）:
  硬閘 (任何一個 FAIL ⟹ α=φ² 降級📉為候選):
    H1 全體 fit:  |α_all − φ²|/SE < 2σ
    H2 掃描谷底:  α=φ² 係固定 α 掃描 LOOCV 嘅唯一極小,
                  且兩側鄰點 (2.5, 3.0) 值 > φ² 值 × 1.3
    H3 MC null:   隨機譜 fit 斜率落入 [φ²±0.15] 嘅機率 < 1%
                  （φ² 唔係「任何譜都 fit 到」嘅常見值, 先有預言力）
  軟閘 (FAIL 唔會單獨降級, 但記錄為瑕疵):
    S1 scale 分組: pole {e,μ,τ,t} / 2GeV {u,d,s} / 全體 —— 每組 |dev| < 3σ
    S2 族分組:     Up {t,c,u} / Down {b,s,d} / Lepton {τ,μ,e} —— 每組 |dev| < 3σ
    S3 固定 < 自由: LOOCV(固定 φ²) < LOOCV(自由 α)  （少 dof 有利之對照）

判定: 硬閘全過 + 軟閘記錄 ⟹ ★結構固化（以後引用 0.10σ/谷底/池三合一）;
      硬閘任何 FAIL ⟹ 📉正式降級為候選（唔可以再講「鎖定」）。

產物: data/46_alpha_phi2_freeze.json
"""
import json
import math
import numpy as np
from scipy import stats

rng = np.random.default_rng(20261012)

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

print("=" * 78)
print("O239 scripts/46 — α=φ² 固化測試套件（預註冊閘門, 一票終審）")
print("=" * 78)

PHI = (1 + 5**0.5)/2
PHI2 = PHI**2
PARTS = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MODES = [1, 2, 3, 4, 5, 7, 9, 11, 13]
MASS = np.array([172690.0, 4180.0, 1776.86, 1270.0, 105.6584, 93.4, 4.67, 2.16, 0.510999])
NC = 88

# ── 譜計算（同 scripts/38/39 一致）──
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

# ── H1: 全體 fit ──
print("\n── H1 全體 fit |dev| < 2σ ──")
rg = stats.linregress(logdm, logm)
dev1 = (rg.slope - PHI2)/rg.stderr
print(f"   α_all = {rg.slope:.4f} ± {rg.stderr:.4f}, dev = {dev1:+.2f}σ")
h1 = abs(dev1) < 2.0
chk("H1 全體 fit <2σ", h1)

# ── H2: 固定 α 掃描谷底（重跑 scripts/41 掃描, ★正典 LOOCV 定義）──
print("\n── H2 掃描谷底: φ² 係唯一極小 + 鄰點 ×1.3 (正典 2因子+中位|dev|) ──")

def ols(Xlist, y):
    A = np.column_stack([np.ones(len(y))] + list(Xlist))
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return coef

# ★正典 LOOCV（O136 scripts/69 標準, scripts/41 同款）: 兩因子 [logdm, rank_even],
#   中位 |dev|; fixed_alpha 時 logdm 唔 fit、rank_even 照 fit
rank_even = np.array([1.0 if (i % 2 == 0) else 0.0 for i in range(9)])
def loocv(Xlist, y, fixed_alpha=None):
    devs = []
    for i in range(len(y)):
        Xs = [np.delete(x, i) for x in Xlist]
        ys = np.delete(y, i)
        if fixed_alpha is None:
            coef = ols(Xs, ys)
            pred = coef[0] + sum(coef[k+1]*Xlist[k][i] for k in range(len(Xlist)))
        else:
            rest = Xs[1:]
            Xr = np.column_stack([np.ones(len(ys))] + rest)
            coef, *_ = np.linalg.lstsq(Xr, ys - fixed_alpha*Xs[0], rcond=None)
            pred = fixed_alpha*Xlist[0][i] + coef[0] + sum(coef[k+1]*Xlist[k+1][i] for k in range(len(rest)))
        devs.append(float(abs(y[i] - pred)))
    return float(np.median(devs)), devs

avec = np.array([1.5, 2.0, 2.5, PHI2, 3.0, 3.5, 4.0])
sc = np.array([loocv([logdm, rank_even], logm, fixed_alpha=a)[0] for a in avec])
imin = int(np.argmin(sc))
print(f"   α 掃描: " + " ".join(f"{a:.3f}:{v:.4f}" for a, v in zip(avec, sc)))
print(f"   極小喺 index {imin} = {avec[imin]:.4f} ({'φ²' if imin==3 else '✗ 唔係 φ²!'})")
h2a = imin == 3
# 鄰點 ×1.3: 2.5 同 3.0 都要 > φ²值 ×1.3
neigh = [sc[2], sc[4]]
h2b = all(nv > sc[3]*1.3 for nv in neigh)
print(f"   鄰點: 2.5 → {sc[2]:.4f} ({'P' if sc[2] > sc[3]*1.3 else 'X'}); "
      f"3.0 → {sc[4]:.4f} ({'P' if sc[4] > sc[3]*1.3 else 'X'}) [閘: >{sc[3]*1.3:.4f}]")
h2 = h2a and h2b
chk("H2 掃描谷底", h2, f"極小=φ²({h2a}) + 鄰點×1.3({h2b})")

# ── H3: MC null —— 隨機譜 fit 斜率命中 φ² 機率 ──
print("\n── H3 MC null: 隨機譜 fit α 落入 [φ²±0.15] 機率 < 1% ──")
# null 設計: 保持 ln m 9 點不變, 隨機 9 點 logdm（範圍同實測一致）, fit 斜率
# —> 問: 任意譜 fit 出 α≈φ² 有幾常見? 若 <1%, φ² 有預言力（非萬能 fit）
N_MC = 20000
lo, hi = logdm.min(), logdm.max()
cnt = 0
alphas = np.empty(0)
# 分批, 慳記憶
BATCH = 2000
for _ in range(N_MC // BATCH):
    rdm = rng.uniform(lo, hi, size=(BATCH, 9))
    # linregress 每行——用解析式加速 (slope = cov/sxx)
    xm = rdm.mean(axis=1, keepdims=True)
    ym = logm.mean()
    sxx = ((rdm - xm)**2).sum(axis=1)
    sxy = ((rdm - xm) * (logm - ym)).sum(axis=1)
    a = sxy / sxx
    cnt += int(np.sum(np.abs(a - PHI2) < 0.15))
p3 = cnt / N_MC
print(f"   隨機譜 α 落入 [φ²±0.15] = {cnt}/{N_MC} = {p3:.4f}  (窗 [{(PHI2-0.15):.3f}, {(PHI2+0.15):.3f}])")
h3 = p3 < 0.01
chk("H3 MC null < 1%", h3)

# ── S1: scale 分組 ──
print("\n── S1 scale 分組 |dev| < 3σ（軟閘）──")
is2gev = {"t": False, "b": False, "tau": False, "c": False, "mu": False,
          "s": True, "d": True, "u": True, "e": False}
grp_scale = {
    "pole": [i for i in range(9) if not is2gev[PARTS[i]]],
    "2GeV": [i for i in range(9) if is2gev[PARTS[i]]],
}
s1_ok = True
for gn, gi in grp_scale.items():
    rg2 = stats.linregress(logdm[gi], logm[gi])
    d = (rg2.slope - PHI2)/rg2.stderr
    ok = abs(d) < 3.0
    s1_ok &= ok
    print(f"   {gn} (n={len(gi)}): α={rg2.slope:.4f}±{rg2.stderr:.4f} dev={d:+.2f}σ "
          f"{'PASS' if ok else 'FAIL'}")
chk("S1 scale 組全 <3σ", s1_ok)

# ── S2: 族分組 ──
print("\n── S2 族分組 |dev| < 3σ（軟閘）──")
grp_fam = {
    "Up": [i for i, p in enumerate(PARTS) if p in ("t", "c", "u")],
    "Down": [i for i, p in enumerate(PARTS) if p in ("b", "s", "d")],
    "Lepton": [i for i, p in enumerate(PARTS) if p in ("tau", "mu", "e")],
}
s2_ok = True
for gn, gi in grp_fam.items():
    rg3 = stats.linregress(logdm[gi], logm[gi])
    d = (rg3.slope - PHI2)/rg3.stderr
    ok = abs(d) < 3.0
    s2_ok &= ok
    print(f"   {gn} (n={len(gi)}): α={rg3.slope:.4f}±{rg3.stderr:.4f} dev={d:+.2f}σ "
          f"{'PASS' if ok else 'FAIL'}")
chk("S2 族組全 <3σ", s2_ok)

# ── S3: 固定 < 自由 LOOCV ──
print("\n── S3 固定 φ² LOOCV < 自由 α LOOCV（軟閘, 正典定義）──")
cv_fix = sc[3]
cv_free, _ = loocv([logdm, rank_even], logm)  # 自由 α, 兩因子
print(f"   LOOCV 固定 φ² = {cv_fix:.4f} vs 自由 α = {cv_free:.4f}")
s3 = cv_fix < cv_free
chk("S3 固定 < 自由", s3)

# ── 總判定 ──
print("\n" + "=" * 78)
hard = [h1, h2, h3]
soft = [s1_ok, s2_ok, s3]
hardn = sum(hard); softn = sum(soft)
verdict = ("★結構固化" if all(hard) else "📉正式降級為候選")
print(f"硬閘: {hardn}/3 過  |  軟閘: {softn}/3 過")
print(f"判定: {verdict}")
print("=" * 78)

json.dump({
    "verdict": verdict,
    "hard": {"H1_all_fit_dev_sigma": float(dev1), "H2_min_is_phi2": bool(h2a),
             "H2_neighbor_1_3x": bool(h2b), "H3_mc_null_p": float(p3),
             "all_pass": bool(all(hard))},
    "soft": {"S1_scale": bool(s1_ok), "S2_family": bool(s2_ok),
             "S3_fixed_lt_free": bool(s3), "fixed_loocv": float(cv_fix),
             "free_loocv": float(cv_free)},
    "details": {
        "alpha_all": float(rg.slope), "alpha_all_se": float(rg.stderr),
        "scan": {f"{a:.4f}": float(v) for a, v in zip(avec, sc)},
        "mc_null_hit_rate": float(p3),
        "scale_groups": {gn: {"n": len(gi)} for gn, gi in grp_scale.items()},
    },
    "gate_criteria": "H1<2σ, H2 谷底+鄰點1.3x, H3<1%; S1/S2<3σ, S3 固定<自由",
    "note": "預註冊閘門, 跑一次鎖結論; 以後 α=φ² 宣稱只引用本套件 + docs/38",
}, open("data/46_alpha_phi2_freeze.json", "w"), indent=1, ensure_ascii=False)

print(f"\n判定: {sum(1 for _, c in P if c)}/{len(P)} PASS")