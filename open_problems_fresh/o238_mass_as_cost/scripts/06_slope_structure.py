#!/usr/bin/python3
"""O238 — Script 06: 3 點 spread null + 分段斜率診斷 (α=φ² 全域性)

scripts/05: n≡1 mod4 全族修正失敗 (P=0.22) — 但 {5,9,13} 3 點 spread 0.04 未有
诚实 null; 7 點殘差顯示「重段大、輕段細」. 本 script:
  P1 {5,9,13} (n≡1 mod4, n≥5) 3 點 spread 之隨機 null (100k 抽 3 點)
  P2 分段斜率: 重 5 點 (t,b,τ,c,μ) vs 輕 4 點 (s,d,u,e) 各自 OLS α
     — φ² 係咪只喺某段成立? 段界邊度?
  P3 LOOCV 斜率穩定性: 逐點剔除 OLS α, 邊個點拉動斜率 (影響 φ² 結論)
"""
import numpy as np, math, json, random

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
resid = logm - (math.log(C9) + PHI2 * logd)

print("═══ P1. {5,9,13} 3 點 spread null ═══")
FAM = [4, 6, 8]  # mu, d, e
fam_resid = [resid[i] for i in FAM]
spread_obs = max(fam_resid) - min(fam_resid)
print(f"  {[names9[i] for i in FAM]} resid = {[f'{r:+.4f}' for r in fam_resid]}")
print(f"  觀測 spread = {spread_obs:.4f}")
rng = random.Random(777)
null = []
for _ in range(100000):
    idx = rng.sample(range(9), 3)
    rs = [resid[i] for i in idx]
    null.append(max(rs) - min(rs))
null = np.array(null)
p = (null <= spread_obs).mean()
print(f"  null (100k 隨機抽 3 點 spread): median={np.median(null):.4f}; P(spread ≤ {spread_obs:.3f}) = {p:.5f}")
chk("P1.1 {5,9,13} spread null 顯著 (P<0.01)", p < 0.01, f"P={p:.5f}")

print("\n═══ P2. 分段斜率診斷 ═══")
def ols(idx):
    A = np.vstack([np.ones(len(idx)), logd[idx]]).T
    c, *_ = np.linalg.lstsq(A, logm[idx], rcond=None)
    r = logm[idx] - A @ c
    rms = np.sqrt((r**2).mean())
    s2 = (r @ r) / max(len(idx) - 2, 1)
    Sxx = ((logd[idx] - logd[idx].mean())**2).sum()
    se = math.sqrt(s2 / Sxx) if Sxx > 0 else float('nan')
    return c[1], se, rms
# 分段: 頭 k 重 (質量降序) vs 尾 9-k
print("  分段 OLS α (t 最重 → e 最輕):")
for k in [2, 3, 4, 5, 6, 7]:
    if k < 2 or 9-k < 2: continue
    h = list(range(k)); l = list(range(k, 9))
    ah, seh, rh = ols(h)
    al, sel, rl = ols(l)
    print(f"    重{k}點 α={ah:+.4f}±{seh:.4f} RMS={rh:.4f} | 輕{9-k}點 α={al:+.4f}±{sel:.4f} RMS={rl:.4f}")
# 特殊段: 4 輕 (s,d,u,e) = {5,6,7,8}
l4 = [5, 6, 7, 8]
al, sel, rl = ols(l4)
print(f"  [輕4點 s,d,u,e] α={al:+.4f}±{sel:.4f} RMS={rl:.4f}  (φ²=2.618: {(al-PHI2)/sel:+.2f}σ)")
h5 = list(range(5))
ah, seh, rh = ols(h5)
print(f"  [重5點 t,b,τ,c,μ] α={ah:+.4f}±{seh:.4f} RMS={rh:.4f}  (φ²=2.618: {(ah-PHI2)/seh:+.2f}σ)")

print("\n═══ P3. LOOCV 斜率穩定性 ═══")
all_alpha = []
for i in range(9):
    idx = [j for j in range(9) if j != i]
    a, se, r = ols(idx)
    all_alpha.append(a)
    print(f"  剔除 {names9[i]:4s}: α = {a:+.5f} ± {se:.4f}  ({abs(a-PHI2)/se:.2f}σ from φ²)")
av = np.array(all_alpha)
print(f"  α 範圍: {av.min():.5f} .. {av.max():.5f}; 全含 φ²={PHI2:.5f}? {bool((av.min()<PHI2<av.max()))}")

out = {"spread_fam": float(spread_obs), "p_spread_null": float(p),
       "alpha_heavy5": float(ols(list(range(5)))[0]), "alpha_light4": float(ols(l4)[0])}
with open("data/06_slope_structure.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")