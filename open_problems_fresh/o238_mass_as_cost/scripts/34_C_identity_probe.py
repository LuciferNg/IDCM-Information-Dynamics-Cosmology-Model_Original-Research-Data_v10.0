#!/usr/bin/python3
"""O238 — Script 34: C 身份推導 — O239 橋合成後 C 結構探測

O239 docs/32 橋: m ∝ |Δm|^(γ/β) = |Δm|^φ², ln m = ln M₀ + φ²·ln|Δm|.
O238 一致架構: m_n = C·|dm|_n^φ² ⟹ C = m/|dm|^φ² per point.

本 script 問: 固定 φ² 下 C_n per point 係咪常數? C/M₀ 同 88-chain 譜有冇結構關係?
P1 C_n per point (9 質量點) — 幾何平均 C, log std
P2 C/M₀ vs 1/88³, M₀/88³, 譜統計
P3 目標 log|dm| = ln(M₀/C)/φ² 有冇譜點命中
P4 C 身份候選掃描 (88-chain 譜函數: mean/median/geo-mean/min/max of |dm|)
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
M0 = 27.900915

logd = np.log([admn[n-1] for n in SEL9])
logm = np.log([MS[p] for p in names9])

print("═══ P1. C_n per point (固定 φ² = m/|dm|^φ²) ═══")
C_n = np.array([MS[p] for p in names9]) / np.array([admn[n-1]**PHI2 for n in SEL9])
for nm, cn in zip(names9, C_n):
    print(f"  {nm:4s}: C_n = {cn:.6e}  log10 = {math.log10(cn):.4f}")
C_geo = math.exp(np.log(C_n).mean())
C_logstd = float(np.log(C_n).std())
print(f"  geometric mean C = {C_geo:.6e}")
print(f"  log std = {C_logstd:.4f}  ⟹ C 係唔係常數?: ", "YES" if C_logstd < 0.05 else "NO (有結構)")
chk("P1.1 C_n 唔係常數 (有 9 點離散, log std > 0.1)", C_logstd > 0.1,
    f"log std = {C_logstd:.4f}")

print("\n═══ P2. C/M₀ vs 譜常數 ═══")
print(f"  C_geo/M₀        = {C_geo/M0:.6e}")
print(f"  C_fit(S2)/M₀    = {1.5215078563621918e-06/27.900915:.6e} (正典 docs/04)")
print(f"  1/88³           = {1/88**3:.6e}")
print(f"  M₀/88³          = {M0/88**3:.6e}")
print(f"  C_geo 同正典 C 差: {(C_geo-1.5215078563621918e-06)/1.5215078563621918e-06*100:+.2f}%")

print("\n═══ P3. In(M₀/C)/φ² 有冇譜點 ═══")
target = math.log(M0/C_geo)/PHI2
logdm_all = np.log(admn)
idx = int(np.argmin(np.abs(logdm_all - target)))
print(f"  target log|dm| = {target:.4f}")
print(f"  最近譜點 n={idx+1}: log|dm|={logdm_all[idx]:.4f} |dm|={admn[idx]:.6e}")
print(f"  誤差 = {abs(logdm_all[idx]-target):.4f}")
chk("P3.1 目標 log|dm| 有近譜點 (<2)", abs(logdm_all[idx]-target) < 2.0,
    f"n={idx+1} 誤差={abs(logdm_all[idx]-target):.4f}")

print("\n═══ P4. C 身份候選掃描 (88-chain |dm| 譜函數) ═══")
cands = {
    "1/88^3": 1/88**3,
    "M0/88^3": M0/88**3,
    "geo_mean|dm|": math.exp(np.log(admn).mean()),
    "mean|dm|": float(admn.mean()),
    "median|dm|": float(np.median(admn)),
    "min|dm|": float(admn.min()),
    "max|dm|": float(admn.max()),
    "|dm|_1 (t點)": float(admn[0]),
    "|dm|_13 (e點)": float(admn[12]),
    "std|dm|": float(admn.std()),
}
print(f"  target C_geo = {C_geo:.6e}")
best = None
for nm, v in cands.items():
    dev = (v - C_geo)/C_geo*100
    print(f"  {nm:16s}: {v:.6e}  dev = {dev:+.3f}%")
    if best is None or abs(dev) < abs(best[1]):
        best = (nm, dev)
print(f"  ★最近候選: {best[0]} dev {best[1]:+.3f}%")
chk("P4.1 有候選 <25% dev", best[1] < 25.0, f"{best[0]} {best[1]:+.3f}%")

out = {"C_per_point": {nm: float(cn) for nm, cn in zip(names9, C_n)},
       "C_geo": float(C_geo), "C_geo_logstd": C_logstd,
       "C_fit_S2": 1.5215078563621918e-06, "M0": M0,
       "C_geo_over_M0": float(C_geo/M0), "inv_88_3": 1/88**3,
       "target_logdm": float(target), "nearest_n": idx+1, "nearest_err": float(abs(logdm_all[idx]-target)),
       "candidates": cands, "best_candidate": best[0], "best_dev_pct": best[1]}
with open("data/34_C_identity_probe.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")