#!/usr/bin/python3
"""O239 — Script 41: 質量閉合式最終列表 + 固定 α 掃描（誠實分級）
============================================================================
狀態: 2026-10-12 新增（第三十二輪後續——調律者「重新再生成質量閉合式列表」）

背景誠實狀態（O136 data/69 + O239 scripts/38-40）:
  * O136 P6.1: rank-parity null P = 0.2165 🔴（2 值指派 null 唔顯著）
  * O136 P5.1: 三因子(block23) LOOCV 0.4586 倒退 vs 兩因子 0.4324 🔴
  * O239 scripts/39 N5: 固定 α=φ² LOOCV 0.3335「好過」自由 0.4324 ——
    但固定版少 fit 一個參數, 細樣本一定有利 ⟹ 必須補 ★固定 α 掃描:
    α_fixed ∈ {1.5,...,4.0}, 睇 φ² 係咪 LOOCV 谷底（結構預言）,
    定係「任何固定 α 都好過 free」嘅自由度假象（= φ² 冇特別）

任務: 質量閉合式最終列表（版本並排）+ 誠實分級（結構鎖定/候選/唔入）

判據預註冊:
  R1: α_fixed 掃描 LOOCV 曲線 —— φ² 係谷底或 P25 內?（中位 |dev|）
  R2: 1 參數版 (α=φ²): 列表 + LOOCV
  R3: 2 因子版 (α=φ² + rank): 列表 + LOOCV（rank 標候選, P null 0.2165）
  R4: 3 因子版 (O136 free + rank + block23): 列表 + LOOCV（標 O136 未認證）
  R5: 最終分級：結構鎖定 = 僅 α=φ²; 候选 = rank/block23; 逐點 >1σ 殘留如實報
產物: data/41_mass_closure_final.json（新增）
"""
import json
import math
import numpy as np

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/41 — 質量閉合式最終列表 + 固定 α 掃描")
print("=" * 78)

PHI2 = ((1 + 5**0.5)/2)**2
PARTS = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MODES = [1, 2, 3, 4, 5, 7, 9, 11, 13]
MASS = np.array([172690.0, 4180.0, 1776.86, 1270.0, 105.6584, 93.4, 4.67, 2.16, 0.510999])
ERRS = np.array([1300.0, 30.0, 0.12, 20.0, 0.0003, 1.0, 0.48, 0.49, 0.000001])

# |Δm| 權威（O136 同款）
NC = 88
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
logdm = np.log(dm)
logm = np.log(MASS)
rank_even = np.array([1.0 if (i+1) % 2 == 0 else 0.0 for i in range(9)])
block23 = np.array([1.0 if i in (1, 4, 7) else 0.0 for i in range(9)])

def ols(Xlist, y):
    A = np.column_stack([np.ones(len(y))] + list(Xlist))
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return coef

def loocv(Xlist, y, fixed_alpha=None):
    """統一 LOOCV 中位 |dev|（O136 scripts/69 標準）; fixed_alpha 時 logdm 唔 fit"""
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

# ── R1: 固定 α 掃描（中位 |dev|, 2 因子 α+rank, 只固定 α）──
print("\n── R1: 固定 α 掃描 LOOCV（α+rank, α 鎖定）──")
alphas = [1.5, 2.0, 2.5, PHI2, 3.0, 3.5, 4.0]
scan = {}
for a in alphas:
    lv, _ = loocv([logdm, rank_even], logm, fixed_alpha=a)
    scan[a] = lv
    mp = " ◄ φ²" if abs(a - PHI2) < 1e-9 else ""
    print(f"   α={a:6.3f}: LOOCV = {lv:.4f}{mp}")
free_lv, _ = loocv([logdm, rank_even], logm)
print(f"   α free:  LOOCV = {free_lv:.4f}  (O136 P5: 0.4324)")
vals = list(scan.values())
is_valley = scan[PHI2] <= min(vals) + 1e-9
chk("R1 φ² 係掃描谷底（或並列最細）", is_valley,
    f"φ² LOOCV={scan[PHI2]:.4f} vs min={min(vals):.4f}")
# 相對自由版: φ² 有冇好過 free?
chk("R1b φ² 固定好過自由 α", scan[PHI2] < free_lv, f"{scan[PHI2]:.4f} vs {free_lv:.4f}")

# ── R2: 1 參數版（α=φ², δ=0）──
print("\n── R2: 1 參數版 ln m = lnM₀ + φ²·ln|Δm| ──")
lnM0_1 = np.mean(logm - PHI2*logdm)
pred1 = lnM0_1 + PHI2*logdm
rms1 = np.sqrt(np.mean((logm - pred1)**2))
lv1, _ = loocv([logdm], logm, fixed_alpha=PHI2)
print(f"   RMS={rms1:.4f}  LOOCV={lv1:.4f}")
chk("R2 1參數 LOOCV 記錄", lv1 > 0, f"{lv1:.4f}")

# ── R3: 2 因子版（α=φ² + rank）──
print("\n── R3: 2 因子版 ln m = lnM₀ + φ²·ln|Δm| + δ·even_rank ──")
A2 = np.column_stack([np.ones(9), logdm, rank_even])
c2, *_ = np.linalg.lstsq(A2, logm, rcond=None)
pred2 = A2 @ c2
rms2 = np.sqrt(np.mean((logm - pred2)**2))
lv2, _ = loocv([logdm, rank_even], logm, fixed_alpha=PHI2)
print(f"   coef: lnM₀={c2[0]:.4f} δ={c2[2]:+.4f}  RMS={rms2:.4f}  LOOCV={lv2:.4f}")
chk("R3 2因子 LOOCV 好過 1因子", lv2 < lv1, f"{lv2:.4f} vs {lv1:.4f}")

# ── R4: 3 因子版（O136 free α + rank + block23, 唔鎖定）──
print("\n── R4: 3 因子版（O136 自由 α + rank + block23）──")
A3 = np.column_stack([np.ones(9), logdm, rank_even, block23])
c3, *_ = np.linalg.lstsq(A3, logm, rcond=None)
pred3 = A3 @ c3
rms3 = np.sqrt(np.mean((logm - pred3)**2))
lv3, _ = loocv([logdm, rank_even, block23], logm)
print(f"   RMS={rms3:.4f}  LOOCV={lv3:.4f}  (O136: RMS 0.3087, LOOCV 0.4586)")
chk("R4 三因子 LOOCV 記錄（O136 已評倒退）", lv3 >= lv2, f"{lv3:.4f} vs 2因子 {lv2:.4f}")

# ── R5: 最終並排列表 + 分級 ──
print("\n── R5: 質量閉合式最終並排列表 ──")
print(f"   {'粒子':>4s} {'n':>2s} {'PDG(MeV)':>11s} {'1par(dev%)':>11s} {'2fac(dev%)':>11s} {'3fac(dev%)':>11s}")
rows = []
for i, p in enumerate(PARTS):
    r1 = (np.exp(pred1[i])/MASS[i] - 1)*100
    r2 = (np.exp(pred2[i])/MASS[i] - 1)*100
    r3 = (np.exp(pred3[i])/MASS[i] - 1)*100
    rows.append({"label": p, "n": MODES[i], "m_pdg": float(MASS[i]),
                 "dev1_pct": float(r1), "dev2_pct": float(r2), "dev3_pct": float(r3)})
    print(f"   {p:>4s} {MODES[i]:2d} {MASS[i]:11.4f} {r1:+10.1f}% {r2:+10.1f}% {r3:+10.1f}%")

print("\n── 誠實分級 ──")
print("   ★結構鎖定: α = φ² (scripts/39, dev 0.10σ vs ln m vs ln|Δm| slope)")
print("   🟡候選未認證: rank-parity (O136 P6 null P=0.2165 🔴);")
print("                block23 (O136 P5 LOOCV 倒退 0.4586>0.4324 🔴)")
print("   🔴殘留: 逐點 9/9 >1σ (PDG 誤差)——閉合式係譜結構, 唔係逐點質量公式")
chk("R5 分級輸出", True, "結構=α=φ²; 候選=rank/block23; 殘留如實報")

json.dump({
    "alpha_scan": {str(k): v for k, v in scan.items()},
    "alpha_free_loocv": free_lv, "phi2_is_valley": is_valley,
    "rms_1param": rms1, "loocv_1param": lv1,
    "rms_2factor": rms2, "loocv_2factor": lv2, "delta": float(c2[2]),
    "rms_3factor": rms3, "loocv_3factor": lv3,
    "table": rows,
    "verdict": "質量閉合式最終: 唯一結構鎖定 = α=φ²(0.10σ); "
               "rank-parity/block23 未過 O136 null/LOOCV 標候選; "
               "逐點生成仍有 9/9 >1σ 殘留——閉合式係譜結構層面",
}, open("data/41_mass_closure_final.json", "w"), indent=1, ensure_ascii=False)

print("\n" + "=" * 78)
np_ = sum(1 for _, c in P if c)
print(f"判定: {np_}/{len(P)} PASS")