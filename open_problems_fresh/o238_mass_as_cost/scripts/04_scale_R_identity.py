#!/usr/bin/python3
"""O238 — Script 04: 標度 R 身份 — 全譜歸一化候選 + 譜泛函掃描 + 殘差交替

scripts/03: C7/M₀ 池 0 命中; 雙參數低於密度基準. 本 script 轉攻 R 身份:
  m_n = M₀·(|dm|_n/R)^{φ²}  ⟺  m_n = C·|dm|_n^{φ²}, R = (M₀/C)^{1/φ²} = 603.207
  (re-parameterization: RMS 唔變, 但 R 有框架身份 = 標度閉合)

候選 (全譜泛函, 零新常數):
  P1 R = φ²-power mean: R^φ² = ⟨|dm|^φ²⟩_全譜 (C = M₀/⟨|dm|^φ²⟩) — 全譜歸一化
  P2 R 對全部 p-power mean (p ∈ 0.5..8 檢掃) + 幾何 mean + harmonic mean + median
  P3 R 對 C_f 池 (O137 9 值? 唔得 — 只檢 R 本身) — 改: R 對 γ 特殊位組合
  P4 殘差 sign 交替統計 (docs/25「±60% 正負交替」): 交替長度 vs 隨機
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
C9 = math.exp((logm - PHI2 * logd).mean())
R = (M0 / C9) ** (1.0 / PHI2)
print(f"基線: C9 = {C9:.6g} MeV;  R = (M₀/C)^{{1/φ²}} = {R:.6f}   ← 要搵身份")

print("\n═══ P1. R = φ²-power mean (全譜歸一化) ═══")
powmean = (admn ** PHI2).mean() ** (1.0 / PHI2)
print(f"  ⟨|dm|^{{φ²}}⟩^{{1/φ²}} = {powmean:.6f}  vs R = {R:.6f}  dev = {abs(powmean-R)/R*100:.3f}%")
chk("P1.1 全譜 φ²-power mean = R (dev<2%)", abs(powmean-R)/R < 0.02,
    f"dev={abs(powmean-R)/R*100:.3f}%")

print("\n═══ P2. p-power mean / 譜泛函掃描 ═══")
best = []
for p10 in range(5, 81, 1):   # p = 0.5 .. 8.0
    p = p10 / 10.0
    # 全譜 p-power mean (正數, 全 modes 有 |dm| > 0)
    pm = (admn ** p).mean() ** (1.0 / p)
    d = abs(pm - R) / R
    best.append((d, p, pm))
best.sort()
for d, p, pm in best[:8]:
    print(f"  p={p:.1f}: power-mean = {pm:.6f}  dev={d*100:.3f}%")
# 幾何 / harmonic / median
gm = math.exp(np.log(admn).mean())
hm = N / (1.0 / admn).sum()
med = np.median(admn)
for nm, v in [("geomean", gm), ("harmonic", hm), ("median", med), ("quadratic", (admn**2).mean()**0.5)]:
    print(f"  {nm:10s} = {v:.6f}  dev={abs(v-R)/R*100:.3f}%")
chk("P2.1 有譜泛函命中 R (dev<2%)", min(b[0] for b in best[:1]) < 0.02 or min(
    abs(v-R)/R for v in [gm, hm, med]) < 0.02,
    f"best={best[0][0]*100:.3f}%")

print("\n═══ P3. R 對 γ 特殊位 / 結構數組合 (對數匹配) ═══")
pool = {"gamma_1": gam[0], "gamma_22": gam[21], "gamma_44": gam[43],
        "sum_gamma": gam.sum(), "N_d": 44.0, "B": 4.0, "mu2": 2.0,
        "F_5": 5.0, "F_7": 13.0, "F_9": 34.0, "F_10": 55.0, "L_5": 11.0, "L_7": 29.0}
for k in range(-88, 89):
    pool[f"phi^{k}"] = PHI ** k
# R 有量綱? 無: |dm| 無量綱 ⟹ R 無量綱. 啱.
hits = [(nm, v, abs(v-R)/R) for nm, v in pool.items() if v > 0 and abs(v-R)/R < 0.02]
hits.sort(key=lambda x: x[2])
logspan = max(math.log(v) for v in pool.values() if v > 0) - min(math.log(v) for v in pool.values() if v > 0)
dens = len(pool) / logspan * (2 * 0.02)
print(f"  池 {len(pool)}; 2% 窗命中 = {len(hits)} (密度基準 {dens:.1f})")
for nm, v, d in hits[:8]:
    print(f"    {nm:12s} = {v:.6f}  dev={d*100:.3f}%")

print("\n═══ P4. 殘差 sign 交替統計 ═══")
resid = logm - (math.log(C9) + PHI2 * logd)
signs = [1 if r > 0 else -1 for r in resid]
print(f"  resid sign: {signs}")
runs = []
cur, cnt = signs[0], 1
for s in signs[1:]:
    if s == cur: cnt += 1
    else: runs.append(cnt); cur, cnt = s, 1
runs.append(cnt)
print(f"  run 長度: {runs}  (run 數 = {len(runs)})")
# 隨機對照: 9 位 ± 之預期 run 數
E_runs = 2 * (5*4)/9 + 1   # 期望 run 數 = 1 + 2*n1*n2/N
n1 = signs.count(1); n2 = 9 - n1
E = 1 + 2*n1*n2/9
print(f"  期望 run 數 (隨機) = {E:.2f}; 實際 = {len(runs)}")
# 交替度: |runs 數 - E| 大細 (N=9 無 MC, 只報)
chk("P4.1 run 數顯著少於隨機 (< E-2)", len(runs) < E - 2,
    f"runs={len(runs)} E={E:.1f}")

out = {"R": float(R), "powmean_phi2": float(powmean),
       "best_p": [{"p": p, "pm": float(pm), "dev": float(d)} for d, p, pm in best[:3]],
       "runs": runs, "E_runs": float(E)}
with open("data/04_scale_R_identity.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")