#!/usr/bin/python3
"""O238 — Script 16: PCA 軌跡 — A₅ 共線方向 + 沿軌跡位置 ↔ log m

docs/06 §八 + docs/08 §四 候選①: SEL9 喺 (log|dm|, logγ) 二維譜平面嘅
投影 signature 係一條共線軌跡 (R²=0.992). PCA 拆解:

  P1 PCA: 9 點 2D 協方差 → PC1 (軌跡方向) + PC2 (垂直偏差)
  P2 沿 PC1 位置 ↔ log m: 有冇單調關係 (質量排序 = 軌跡排序)?
     — 投影 operator 嘅幾何形式: m = g(PC1 座標)?
  P3 PC2 (垂直偏差) ↔ 已知殘差: c/s 離群喺 PC2 突出?
  P4 zero-α 對照: PC1 座標同 log γ / log|dm| 單獨比, 邊個解釋 log m 最強
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

# 2D 譜平面座標
X = np.array([[math.log(gam[n-1]), math.log(admn[n-1])] for n in SEL9])
logm = np.array([math.log(MS2[p]) for p in names9])

print("═══ P1. PCA ═══")
Xc = X - X.mean(axis=0)
cov = Xc.T @ Xc / (len(SEL9)-1)
evals, evecs = np.linalg.eigh(cov)
order = np.argsort(evals)[::-1]
evals, evecs = evals[order], evecs[:, order]
print(f"  PC1 方向 = ({evecs[0,0]:+.4f}, {evecs[1,0]:+.4f})  特徵值 {evals[0]:.4f} ({evals[0]/evals.sum()*100:.1f}% var)")
print(f"  PC2 方向 = ({evecs[0,1]:+.4f}, {evecs[1,1]:+.4f})  特徵值 {evals[1]:.4f} ({evals[1]/evals.sum()*100:.1f}% var)")
# PC1 = a·logγ + b·log|dm|; slope 喺 (logγ, log|dm|) 平面
slope_pc1 = evecs[1,0]/evecs[0,0]
print(f"  PC1 斜率 d log|dm|/d logγ = {slope_pc1:+.4f}  (共線線 log|dm| = {slope_pc1:+.4f}·logγ + const)")
chk("P1.1 PC1 佔 >90% 變異 (一維軌跡)", evals[0]/evals.sum() > 0.9, f"ratio={evals[0]/evals.sum():.4f}")

# PC 座標
P = Xc @ evecs
pc1, pc2 = P[:,0], P[:,1]

print("\n═══ P2. 沿 PC1 位置 ↔ log m ═══")
corr_pc1 = np.corrcoef(pc1, logm)[0,1]
print(f"  corr(PC1 座標, log m) = {corr_pc1:+.6f}")
# 單調性 (Spearman)
r_pc1 = np.argsort(np.argsort(pc1)); r_m = np.argsort(np.argsort(logm))
sp = np.corrcoef(r_pc1, r_m)[0,1]
print(f"  Spearman(PC1, log m) = {sp:+.6f}")
print("  排序 (PC1 → log m):")
for p, a, b in sorted(zip(names9, pc1, logm)):
    print(f"    {p:4s}: PC1={a:+9.4f}  log m={b:+9.4f}")
# fit log m = a + b·PC1
A = np.vstack([np.ones(9), pc1]).T
c, *_ = np.linalg.lstsq(A, logm, rcond=None)
res = logm - A @ c
rms_pc1 = math.sqrt((res**2).mean())
print(f"  log m = {c[0]:.4f} + {c[1]:.4f}·PC1, RMS = {rms_pc1:.6f}")
chk("P2.1 PC1 ↔ log m 強相關 (|corr|>0.95)", abs(corr_pc1) > 0.95, f"corr={corr_pc1:+.6f}")

print("\n═══ P3. PC2 (垂直偏差) vs 已知殘差 ═══")
resid_f = logm - (math.log(MS2['t']) - 0) - 0  # placeholder, 直接用 fit 版:
Cf = math.exp((logm - PHI2 * np.log([admn[n-1] for n in SEL9])).mean())
resid_model = logm - (math.log(Cf) + PHI2 * np.log([admn[n-1] for n in SEL9]))
corr_pc2 = np.corrcoef(pc2, resid_model)[0,1]
print(f"  corr(PC2, 冪律模型殘差) = {corr_pc2:+.6f}")
print("  逐點 (PC2, resid):")
for p, a, b in zip(names9, pc2, resid_model):
    print(f"    {p:4s}: PC2={a:+9.4f}  resid={b:+.4f}")
chk("P3.1 PC2 捕捉 c/s 離群 (|PC2(c)|,|PC2(s)| 最大)", 
    max(abs(pc2[names9.index('c')]), abs(pc2[names9.index('s')])) > max(abs(pc2[i]) for i in range(9) if names9[i] not in ('c','s')),
    f"PC2(c)={pc2[3]:+.4f} PC2(s)={pc2[5]:+.4f}")

print("\n═══ P4. 對照: PC1 vs log γ vs log|dm| 單獨解釋力 ═══")
for nm, xv in [("PC1", pc1), ("logγ", X[:,0]), ("log|dm|", X[:,1])]:
    A_ = np.vstack([np.ones(9), xv]).T
    c_, *_ = np.linalg.lstsq(A_, logm, rcond=None)
    r_ = logm - A_ @ c_
    rms_ = math.sqrt((r_**2).mean())
    print(f"  {nm:8s}: RMS = {rms_:.6f}")

out = {"pc1_dir": [float(evecs[0,0]), float(evecs[1,0])], "pc1_var": float(evals[0]/evals.sum()),
       "corr_pc1_logm": float(corr_pc1), "rms_pc1": float(rms_pc1),
       "corr_pc2_resid": float(corr_pc2), "slope_pc1": float(slope_pc1)}
with open("data/16_pca_trajectory.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")