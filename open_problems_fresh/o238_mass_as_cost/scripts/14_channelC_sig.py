#!/usr/bin/python3
"""O238 — Script 14: 分通道 C 間距 MC null — C=投影算符讀數 顯著性檢定

docs/07 P3 觀察: 連續層=|dm|^{φ²} 下 C_A(free e,μ)≈9.63e-7, C_B(coll τ,t)≈1.47e-6,
C_C(lattice u,d,s,c,b)≈1.85e-6 — 通道間 C 系統性遞增. 但每通道得 2-5 點,
單點結構唔算數. 本 script:

  P1 統計量: 通道幾何中位 C_g 嘅 log 差距 (C_log 內 spread 0.020/0.011 vs 通道間 ~0.43)
     用 ANOVA-like: 通道間 SS / 通道內 SS (F 統計量)
  P2 MC null: 9 點隨機分成 2/2/5 三組 100k 次, F 分佈 — 觀測 F 嘅 p-value
  P3 穩健: group 內 spread 中位數 (穩健版 F, 唔靠方差)
  P4 拆解: C_C 內部 (u,d,s,c,b) spread 0.642 大部分係 c/s — 睇 c/s 對 F 嘅貢獻
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
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2

SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MS2 = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
       "u": 93.4/42.890, "d": 93.4/42.890*2.1505, "s": 93.4,
       "c": 93.4*11.652, "b": 93.4*11.652*4.586, "t": 172690.0}

# 每點 log C_i (連續層 = |dm|^{φ²})
logC = {}
for i, p in enumerate(names9):
    logC[p] = math.log(MS2[p]) - PHI2 * math.log(admn[SEL9[i]-1])
print("log C_i:")
for p in names9:
    print(f"  {p:4s}: {logC[p]:+.5f}")

CH_A = ["e", "mu"]; CH_B = ["tau", "t"]; CH_C = ["u", "d", "s", "c", "b"]

def F_stat(groups):
    """log 域單向 ANOVA F = SS_between/SS_within (df 調整唔影響 MC p)"""
    allv = [logC[p] for g in groups for p in g]
    grand = np.mean(allv)
    ss_b = sum(len(g) * (np.mean([logC[p] for p in g]) - grand)**2 for g in groups)
    ss_w = sum((logC[p] - np.mean([logC[p] for p in g]))**2 for g in groups for p in g)
    k, n = len(groups), len(allv)
    return (ss_b/(k-1)) / (ss_w/(n-k))

F_obs = F_stat([CH_A, CH_B, CH_C])
print(f"\n觀測 F = {F_obs:.3f}  (groups: A{len(CH_A)} B{len(CH_B)} C{len(CH_C)})")

# MC null: 隨機分組 (保持 2/2/5)
rng = np.random.default_rng(20261011)
allp = names9[:]
sizes = [2, 2, 5]
NMC = 100000
cnt = 0
Fnulls = []
for _ in range(NMC):
    perm = rng.permutation(allp)
    groups = []
    idx = 0
    for s in sizes:
        groups.append(list(perm[idx:idx+s])); idx += s
    Fn = F_stat(groups)
    Fnulls.append(Fn)
    if Fn >= F_obs:
        cnt += 1
Fnulls = np.array(Fnulls)
p_val = cnt / NMC
print(f"MC null (100k): P(F ≥ {F_obs:.3f}) = {p_val:.6f}")
print(f"  null F: mean={Fnulls.mean():.3f}  p95={np.percentile(Fnulls,95):.3f}  p99={np.percentile(Fnulls,99):.3f}  max={Fnulls.max():.3f}")
chk("P1 C 通道間距顯著 (F MC p<0.05)", p_val < 0.05, f"F={F_obs:.3f} p={p_val:.6f}")

# P3 穩健: MAD-based spread 比
def mad_log(g):
    v = np.array([logC[p] for p in g])
    return np.median(np.abs(v - np.median(v)))
mad_A, mad_B, mad_C = mad_log(CH_A), mad_log(CH_B), mad_log(CH_C)
print(f"\nMAD(log C): A={mad_A:.5f} B={mad_B:.5f} C={mad_C:.5f}")
print(f"通道間距 (中位C差): |medB-medA|={abs(np.median([logC[p] for p in CH_B])-np.median([logC[p] for p in CH_A])):.4f}")

# P4: 剔 c/s 後 C 通道距
CH_C7 = ["u", "d", "b"]  # 剔 c,s
F7 = F_stat([CH_A, CH_B, CH_C7])
cnt7 = 0
for _ in range(NMC):
    allv7 = [p for p in names9 if p not in ("c", "s")]
    perm = rng.permutation(allv7)
    groups = [list(perm[0:2]), list(perm[2:4]), list(perm[4:7])]
    if F_stat(groups) >= F7:
        cnt7 += 1
p7 = cnt7 / NMC
print(f"\n剔 c/s 後 (A2/B2/C3): F={F7:.3f}  MC p={p7:.6f}")

out = {"F_obs": float(F_obs), "p_mc": float(p_val), "F_null_max": float(Fnulls.max()),
       "mad": {"A": float(mad_A), "B": float(mad_B), "C": float(mad_C)},
       "F_no_cs": float(F7), "p_no_cs": float(p7)}
with open("data/14_channelC_sig.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")