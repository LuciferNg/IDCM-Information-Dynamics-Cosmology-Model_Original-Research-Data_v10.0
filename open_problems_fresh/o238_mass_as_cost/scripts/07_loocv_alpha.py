#!/usr/bin/python3
"""O238 — Script 07: φ² vs 79/30 LOOCV 樣本外判別 (路線 2)

O238 problem record 路線 2: φ² vs 79/30 統計判別 — 需要樣本外盲測.
冇新質量點可用 ⟹ 用 LOOCV 留一法做樣本外預測:
  每輪 8 點 fit 標度 C (α 固定 = 候選值), 預測留出點, 比較 MSPE(φ²) vs MSPE(79/30).
  α 唔 fit — 只 fit C (標度), 然後 blind 預測留出質量.

盲測紀律:
- 參數只有 C (每輪由 8 點 fit); α 係候選凍結值
- 逐點預測誤差表 + paired 檢定 (唔淨睇均值)
- LOOCV 唔係獨立樣本外 (同一 9 點) — 誠實標明係「留一交叉驗證」, 唔等於新數據
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
gam = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)])

SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MB = np.array([172690.0, 93.4*11.652*3.291, 1776.86, 93.4*11.652, 105.6583755, 93.4,
               93.4/42.890*2.1505, 93.4/42.890, 0.51099895])
logd = np.log([admn[n-1] for n in SEL9])
logm = np.log(MB)
M0 = 27.900915
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2
A79 = 79.0 / 30.0

print("═══ P1. LOOCV blind 預測: φ² vs 79/30 ═══")
res_f, res_a = [], []
for i in range(9):
    tr = [j for j in range(9) if j != i]
    Cf = math.exp((logm[tr] - PHI2 * logd[tr]).mean())
    Ca = math.exp((logm[tr] - A79 * logd[tr]).mean())
    pf = Cf * admn[SEL9[i]-1] ** PHI2
    pa = Ca * admn[SEL9[i]-1] ** A79
    ef = math.log(pf) - logm[i]
    ea = math.log(pa) - logm[i]
    res_f.append(ef); res_a.append(ea)
    w = "φ²" if abs(ef) < abs(ea) else "79/30"
    print(f"  {names9[i]:4s}: pred(φ²) err={ef:+.4f} | pred(79/30) err={ea:+.4f} | 較佳={w}")

mspe_f = np.mean(np.array(res_f)**2)
mspe_a = np.mean(np.array(res_a)**2)
print(f"\n  MSPE(φ²)   = {mspe_f:.6f}  (RMS {math.sqrt(mspe_f):.4f})")
print(f"  MSPE(79/30)= {mspe_a:.6f}  (RMS {math.sqrt(mspe_a):.4f})")
print(f"  比率 = {mspe_f/mspe_a:.4f}")
# paired: 逐點絕對誤差差
df = np.abs(np.array(res_f)) - np.abs(np.array(res_a))
wins_f = sum(1 for i in range(9) if abs(res_f[i]) < abs(res_a[i]))
print(f"  φ² 逐點勝出 {wins_f}/9")
# sign test (二項): P(≥wins 中 φ² 勝) 以 p=0.5
from math import comb
p_sign = sum(comb(9, k) * 0.5**9 for k in range(wins_f, 10))
print(f"  sign test P = {p_sign:.4f}")
chk("P1.1 φ² MSPE 好過 79/30", mspe_f < mspe_a, f"ratio={mspe_f/mspe_a:.4f}")
chk("P1.2 φ² 勝出唔顯著 (sign P>0.05, 誠實不可分)", p_sign > 0.05,
    f"P={p_sign:.4f}")

print("\n═══ P2. α fit vs 凍結兩值比較 (對照) ═══")
# OLS fit 全 9 點
A = np.vstack([np.ones(9), logd]).T
c, *_ = np.linalg.lstsq(A, logm, rcond=None)
r_ols = logm - A @ c
rms_ols = np.sqrt((r_ols**2).mean())
print(f"  OLS α = {c[1]:.4f}, RMS = {rms_ols:.4f}")
Cf_all = math.exp((logm - PHI2 * logd).mean())
rms_f2 = np.sqrt(((logm - (math.log(Cf_all) + PHI2 * logd))**2).mean())
print(f"  φ² 固定 RMS = {rms_f2:.4f}")

print("\n═══ P3. 剔除 c/s 後 LOOCV (8 點內再留一: 7 訓練) ═══")
keep = [i for i in range(9) if i not in (3, 5)]
resf7, resa7 = [], []
for i in keep:
    tr = [j for j in keep if j != i]
    Cf = math.exp((logm[tr] - PHI2 * logd[tr]).mean())
    Ca = math.exp((logm[tr] - A79 * logd[tr]).mean())
    ef = math.log(Cf * admn[SEL9[i]-1]**PHI2) - logm[i]
    ea = math.log(Ca * admn[SEL9[i]-1]**A79) - logm[i]
    resf7.append(ef); resa7.append(ea)
mspe_f7 = np.mean(np.array(resf7)**2)
mspe_a7 = np.mean(np.array(resa7)**2)
print(f"  7 點 MSPE(φ²)={mspe_f7:.6f} vs MSPE(79/30)={mspe_a7:.6f}  ratio={mspe_f7/mspe_a7:.4f}")

out = {"mspe_phi2": float(mspe_f), "mspe_79": float(mspe_a),
       "sign_p": float(p_sign), "wins9": wins_f,
       "mspe7_phi2": float(mspe_f7), "mspe7_79": float(mspe_a7)}
with open("data/07_loocv_alpha.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")