#!/usr/bin/python3
"""O238 — Script 02: 殘差結構 g_n 攻堅 (第二修正候選掃描)

docs/02 確立: log g_n = log C_n − mean = 殘差 = c/s 離群結構; 標度 C 同離群係同一問題.
本 script 攻 g_n 嘅結構身份 (盲測紀律: 全部候選有結構動機, 先報基線 RMS 再報減幅):

  P1 殘差重現 + 方差分解: mod-4 / mod-8 / 對稱對 (n, 89−n) 分組有冇解釋力 (ANOVA F)
  P2 三項組合 fit: log m = a + φ² log|dm| + q·log γ  (第二修正 = γ^q 冪律)
     — 睇 RMS 減幅 + q 有冇結構身份 (報 q 對結構池密度)
  P3 三項 fit 變體: q·log beat / q·log(1/γ) / q·log sin(nπ/88) — 全部對比
  P4 殘差相關表: resid vs (log γ, beat, v_g, n, |dm|) — 邊個有線性相關
  P5 分段結構: n≡1 mod4 族 {5,9,13} 殘差是否一致 (−0.42±0.02?) — 若一致 = 局部 offset 訊號
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
beat = 2 * np.sin(np.arange(1, N+1) * math.pi / 88)
vg = np.cos(np.arange(1, N+1) * math.pi / 88)

SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MB = np.array([172690.0, 93.4*11.652*3.291, 1776.86, 93.4*11.652, 105.6583755, 93.4,
               93.4/42.890*2.1505, 93.4/42.890, 0.51099895])
logd = np.log([admn[n-1] for n in SEL9])
logm = np.log(MB)
M0 = 27.900915
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2

# 基線: 固定 φ² 殘差
C0 = (logm - PHI2 * logd).mean()
resid = logm - (C0 + PHI2 * logd)
rms0 = np.sqrt((resid**2).mean())
print(f"基線: 固定 φ² RMS = {rms0:.6f}; 殘差 = {[f'{r:+.3f}' for r in resid]}")

def report(label, rms, q=None, se=None):
    print(f"  {label:34s}: RMS={rms:.6f}  Δ={rms0-rms:+.6f}  {'q='+format(q,'.5f') if q is not None else ''}")

print("\n═══ P1. 殘差分組方差分解 (ANOVA) ═══")
def anova(resid, groups):
    # 組內平方和 vs 總平方和
    sst = ((resid - resid.mean())**2).sum()
    ssw = 0.0
    for g in set(groups):
        r = resid[np.array(groups) == g]
        ssw += ((r - r.mean())**2).sum()
    r2 = 1 - ssw / sst if sst > 0 else 0
    return r2

mod4 = [n % 4 for n in SEL9]
mod8 = [n % 8 for n in SEL9]
mirror = [min(n, 89-n) for n in SEL9]
mod11 = [n % 11 for n in SEL9]
for nm, grp in [("mod-4", mod4), ("mod-8", mod8), ("mirror min(n,89-n)", mirror), ("mod-11", mod11)]:
    r2 = anova(resid, grp)
    print(f"  {nm:24s}: R²(組間解釋) = {r2:.4f}")

print("\n═══ P2. 三項 fit: log m = a + φ² log|dm| + q·log γ ═══")
X2 = np.vstack([np.ones(9), PHI2 * logd, np.log([gam[n-1] for n in SEL9])]).T
c2, *_ = np.linalg.lstsq(X2, logm, rcond=None)
r2_ = logm - X2 @ c2
rms2 = np.sqrt((r2_**2).mean())
report("+ q·log γ", rms2, c2[2])
# 誤差
r = logm - X2 @ c2
s2e = (r @ r) / 6
XtXi = np.linalg.inv(X2.T @ X2)
se_q = math.sqrt(s2e * XtXi[2,2])
print(f"    q = {c2[2]:+.5f} ± {se_q:.5f} ({(c2[2])/se_q:+.2f}σ from 0)")

print("\n═══ P3. 其他第二修正候選 ═══")
cands = {
    "log beat": np.log([beat[n-1] for n in SEL9]),
    "log(1/γ)": -np.log([gam[n-1] for n in SEL9]),
    "log sin": np.log([math.sin(n*math.pi/88) for n in SEL9]),
    "log n": np.log(SEL9),
    "n": SEL9,
}
for nm, xv in cands.items():
    X3 = np.vstack([np.ones(9), PHI2 * logd, xv]).T
    c3, *_ = np.linalg.lstsq(X3, logm, rcond=None)
    r3 = logm - X3 @ c3
    rms3 = np.sqrt((r3**2).mean())
    report(f"+ q·{nm}", rms3, c3[2])

print("\n═══ P4. 殘差相關表 ═══")
avs = {"log γ": np.log([gam[n-1] for n in SEL9]), "beat": [beat[n-1] for n in SEL9],
       "v_g": [vg[n-1] for n in SEL9], "n": SEL9, "log|dm|": logd,
       "log C_n": np.log([MB[i]/admn[SEL9[i]-1]**PHI2 for i in range(9)])}
for nm, xv in avs.items():
    xa = np.array(xv, float)
    cc = np.corrcoef(resid, xa)[0,1]
    print(f"  corr(resid, {nm:10s}) = {cc:+.4f}")

print("\n═══ P5. n≡1 mod4 族 {5,9,13} 殘差一致? ═══")
fam = [i for i, n in enumerate(SEL9) if n % 4 == 1 and n != 1]
fr = [resid[i] for i in fam]
print(f"  {[names9[i] for i in fam]} resid = {[f'{r:+.4f}' for r in fr]}")
print(f"  族內 spread = {max(fr)-min(fr):.4f} (vs 全譜 std {resid.std():.4f})")
chk("P5.1 n≡1 mod4 族 (μ,d,e) 殘差明顯一致 (spread < 0.1)", (max(fr)-min(fr)) < 0.1,
    f"spread={max(fr)-min(fr):.4f}")

out = {"rms0": float(rms0), "resid": [float(r) for r in resid],
       "rms_qgamma": float(rms2), "q_gamma": float(c2[2]),
       "q_gamma_sigma": float(c2[2]/se_q),
       "family14_spread": float(max(fr)-min(fr))}
with open("data/02_residual_structure.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")