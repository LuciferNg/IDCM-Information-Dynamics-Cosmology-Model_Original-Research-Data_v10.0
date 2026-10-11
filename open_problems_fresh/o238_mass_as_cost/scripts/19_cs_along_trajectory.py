#!/usr/bin/python3
"""O238 — Script 19: c/s 沿軌跡位置誤差定量 — 垂直 vs 沿軌跡分解

docs/09: Spearman(PC1, log m)=+1.0 (質量排序=軌跡排序); PC2 唔捕捉 c/s ⟹
c/s 離群係「沿軌跡位置誤差」非垂直偏離. 本 script 定量分解:

  P1 每點: 沿軌跡位置誤差 (質量→推斷 PC1 vs mode 實際 PC1)
  P2 c/s 位置誤差 vs 其他粒子 — 顯著?
  P3 修正模型: log m = a + b·PC1 + h(n) 其中 h 只喺 c/s — RMS 改善?
  P4 沿軌跡誤差有冇譜身份 (誤差 vs γ / |dm| / n)?
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
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2

SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MS2 = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
       "u": 93.4/42.890, "d": 93.4/42.890*2.1505, "s": 93.4,
       "c": 93.4*11.652, "b": 93.4*11.652*4.586, "t": 172690.0}
logm = np.array([math.log(MS2[p]) for p in names9])
X = np.array([[math.log(gam[n-1]), math.log(admn[n-1])] for n in SEL9])

# PC1 座標 (全 9 點 PCA)
Xc = X - X.mean(axis=0)
cov = Xc.T @ Xc / 8
evals, evecs = np.linalg.eigh(cov)
order = np.argsort(evals)[::-1]
evecs = evecs[:, order]
pc1 = Xc @ evecs[:, 0]
pc2 = Xc @ evecs[:, 1]

print("═══ P1. 沿軌跡位置誤差 ═══")
# fit log m = a + b·PC1 (全 9 點)
A = np.vstack([np.ones(9), pc1]).T
c, *_ = np.linalg.lstsq(A, logm, rcond=None)
# 質量→推斷 PC1: PC1_hat = (log m − c0)/c1
print(f"  log m = {c[0]:.4f} + {c[1]:.4f}·PC1")
for i, p in enumerate(names9):
    pc1_hat = (logm[i] - c[0]) / c[1]
    dpos = pc1_hat - pc1[i]
    resid_pc1 = logm[i] - (c[0] + c[1]*pc1[i])
    print(f"  {p:4s}: PC1_act={pc1[i]:+8.4f}  PC1_from_m={pc1_hat:+8.4f}  ΔPC1={dpos:+8.4f}  resid={resid_pc1:+.4f}")

print("\n═══ P2. c/s 位置誤差 vs 其他 ═══")
dpos = {}
for i, p in enumerate(names9):
    pc1_hat = (logm[i] - c[0]) / c[1]
    dpos[p] = pc1_hat - pc1[i]
cs_vals = [abs(dpos["c"]), abs(dpos["s"])]
oth_vals = [abs(dpos[p]) for p in names9 if p not in ("c", "s")]
print(f"  |ΔPC1| c/s: {cs_vals}")
print(f"  |ΔPC1| 其他: {['%.4f' % v for v in oth_vals]}")
print(f"  c/s 平均 = {np.mean(cs_vals):.4f} vs 其他平均 = {np.mean(oth_vals):.4f}  ratio={np.mean(cs_vals)/max(np.mean(oth_vals),1e-9):.2f}")
chk("P2.1 c/s 位置誤差大過其他 (ratio>1.5)", np.mean(cs_vals)/np.mean(oth_vals) > 1.5,
    f"ratio={np.mean(cs_vals)/np.mean(oth_vals):.2f}")

print("\n═══ P3. 修正模型: +h(c/s) ═══")
# baseline: 冪律 fixed φ² (RMS 0.5456); PC1 model (RMS 0.6458); 加 c/s dummy
A1 = np.vstack([np.ones(9), pc1]).T
r1 = logm - A1 @ c
rms1 = math.sqrt((r1**2).mean())
dm_cs = np.array([1.0 if p in ("c", "s") else 0.0 for p in names9])
A2 = np.vstack([np.ones(9), pc1, dm_cs]).T
c2, *_ = np.linalg.lstsq(A2, logm, rcond=None)
r2 = logm - A2 @ c2
rms2 = math.sqrt((r2**2).mean())
print(f"  PC1 only:       RMS = {rms1:.6f}")
print(f"  PC1 + c/s dummy: RMS = {rms2:.6f}  (h(c/s) = {c2[2]:+.4f})")
Cf = math.exp((logm - PHI2 * np.log([admn[n-1] for n in SEL9])).mean())
res_pow = logm - (math.log(Cf) + PHI2 * np.log([admn[n-1] for n in SEL9]))
rms_pow = math.sqrt((res_pow**2).mean())
print(f"  冪律 φ²:          RMS = {rms_pow:.6f}")

print("\n═══ P4. 位置誤差有冇譜身份 ═══")
for nm_, fv in [("log γ", [math.log(gam[n-1]) for n in SEL9]),
                ("log|dm|", [math.log(admn[n-1]) for n in SEL9]),
                ("PC2", pc2), ("n", SEL9)]:
    cc_ = np.corrcoef([dpos[p] for p in names9], fv)[0,1]
    print(f"  corr(ΔPC1, {nm_:8s}) = {cc_:+.4f}")

out = {"dpos": {p: float(dpos[p]) for p in names9},
       "rms_pc1": float(rms1), "rms_pc1_cs": float(rms2), "rms_pow": float(rms_pow)}
with open("data/19_cs_along_trajectory.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")