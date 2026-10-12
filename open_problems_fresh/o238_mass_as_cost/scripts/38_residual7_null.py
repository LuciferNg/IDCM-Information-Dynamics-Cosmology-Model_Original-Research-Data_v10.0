#!/usr/bin/python3
"""O238 — Script 38: rank 過後 7 點殘餘 MC null — 係咪純 noise

R21/22 後真正剩餘: rank-parity 過後剔 b/s 7 點殘餘
t+0.167/c+0.376/u−0.369/μ−0.183/d−0.132/e−0.064, RMS 0.2406。
本 script 用 MC null 檢定 7 點殘餘有冇結構:

P1 7 點 RMS 0.2406 vs 隨機 null (RMS 分佈) —— 會唔會低得唔正常?
P2 家族 mean (剔 b/s 後 U/D/L) vs MC null —— max|mean| 顯著?
P3 正負聚類: 4+/3− signed 結構 vs 隨機?
P4 代際: 1st(u,d,e)/2nd(c,μ)/3rd(t) mean vs null
P5 判決: 7 點殘餘 = 純 noise 定有結構
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

logd = np.log([admn[n-1] for n in SEL9])
logm = np.log([MS[p] for p in names9])
rank = np.arange(1, 10)
even_mask = (rank % 2 == 0).astype(float)

A = np.vstack([np.ones(9), logd, even_mask]).T
c, *_ = np.linalg.lstsq(A, logm, rcond=None)
res = logm - A @ c
KEEP7 = [p for p in names9 if p not in ("b", "s")]
res7 = {p: float(res[names9.index(p)]) for p in KEEP7}
r7 = np.array([res7[p] for p in KEEP7])
RMS7 = float(np.sqrt((r7**2).mean()))
print(f"rank 過後 7 點殘餘: {res7}")
print(f"RMS7 = {RMS7:.4f}")

rng = np.random.default_rng(238001)
NMC = 200000

print("\n═══ P1. RMS7 0.2406 vs 隨機 null ═══")
rms_null = np.empty(NMC)
for k in range(NMC):
    r = rng.normal(0, RMS7, 7)
    rms_null[k] = float(np.sqrt((r**2).mean()))
p_rms = float((rms_null < RMS7).mean())  # 實際值 vs null 係咪低 (過度收緊?)
# 更有意義: 實際 RMS7 相對「剔兩點嘅條件」——隨機 9 殘差剔兩點後最小 RMS 分佈
print(f"  MC: 隨機 7 點 (σ=RMS7) 產生 RMS<實際 機率 = {p_rms*100:.2f}% (呢個係先天 tautology)")
chk("P1.1 RMS7 本身唔係判據 (tautology 附註)", True, f"p={p_rms*100:.2f}% (冇預期值)")

print("\n═══ P2. 7 點家族 max|mean| vs MC null ═══")
fam7 = {"U": ["u", "c", "t"], "D": ["d"], "L": ["e", "mu", "tau"]}  # D 得返 d
def fam_stat(r):
    means = [np.mean([r[KEEP7.index(p)] for p in members]) for members in fam7.values()]
    return max(abs(m) for m in means), means
obs_max, obs_means = fam_stat(r7)
mx = np.empty(NMC)
for k in range(NMC):
    r = rng.normal(0, RMS7, 7)
    mx[k], _ = fam_stat(r)
p2 = float((mx > obs_max).mean())
# 注意: 用 RMS7 做 σ 係後見 (post-hoc)——null 應更保守
print(f"  實際家族 mean: U {obs_means[0]:+.3f} / D {obs_means[1]:+.3f} / L {obs_means[2]:+.3f}")
print(f"  max|mean| = {obs_max:.3f}")
print(f"  MC null (σ=RMS7, 後見寬鬆): max|mean|>實際 = {p2*100:.2f}%")
chk("P2.1 家族分層 7 點冇咗 (max|mean| 唔顯著)", p2 > 0.05, f"p={p2*100:.2f}%")

print("\n═══ P3. 正負聚類 vs null ═══")
obs_pos = int((r7 > 0).sum())
print(f"  實際: {obs_pos}+ / {7-obs_pos}-")
# null: 睇最大 |mean| 但有兩群 (正負對稱) — 用「signed-run 或群聚」太 ad hoc
# 簡單: 全 7 點 signed sum / 7 (平均符號偏置)
obs_signed = float(r7.mean())
sp = np.empty(NMC)
for k in range(NMC):
    r = rng.normal(0, RMS7, 7)
    sp[k] = float(r.mean())
p3 = float((np.abs(sp) > abs(obs_signed)).mean())
print(f"  signed mean = {obs_signed:+.4f}")
print(f"  MC null: |signed mean|>實際 = {p3*100:.2f}%")
chk("P3.1 平均符號偏置唔顯著", p3 > 0.05, f"p={p3*100:.2f}%")

print("\n═══ P4. 代際 mean vs null ═══")
gen7 = {"1st": ["u", "d", "e"], "2nd": ["c", "mu"], "3rd": ["t"]}
def gen_stat(r):
    means = [np.mean([r[KEEP7.index(p)] for p in members]) for members in gen7.values()]
    return max(abs(m) for m in means), means
obs_gm, obs_gmeans = gen_stat(r7)
gm = np.empty(NMC)
for k in range(NMC):
    r = rng.normal(0, RMS7, 7)
    gm[k], _ = gen_stat(r)
p4 = float((gm > obs_gm).mean())
print(f"  實際代際: 1st {obs_gmeans[0]:+.3f} / 2nd {obs_gmeans[1]:+.3f} / 3rd {obs_gmeans[2]:+.3f}")
print(f"  max|mean| = {obs_gm:.3f}, MC null p = {p4*100:.2f}%")
chk("P4.1 代際分層唔顯著", p4 > 0.05, f"p={p4*100:.2f}%")

print("\n═══ P5. 判決 ═══")
print(f"  ★P2 家族: p={p2*100:.2f}%  P3 符號: p={p3*100:.2f}%  P4 代際: p={p4*100:.2f}%")
if min(p2, p3, p4) < 0.05:
    print("  ⟹ 至少一項顯著 → 7 點殘餘有結構候選 (需再查)")
else:
    print("  ⟹ 全部唔顯著 → 7 點殘餘 consistent 純 noise")
chk("P5.1 7 點殘餘 = 純 noise (全部 p>5%)",
    min(p2, p3, p4) > 0.05, f"p2={p2*100:.2f}% p3={p3*100:.2f}% p4={p4*100:.2f}%")

out = {"res7": res7, "rms7": RMS7, "p_family": float(p2), "p_signed": float(p3),
       "p_generation": float(p4), "n_mc": NMC, "fam7_means": [float(m) for m in obs_means],
       "gen7_means": [float(m) for m in obs_gmeans]}
with open("data/38_residual7_null.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")