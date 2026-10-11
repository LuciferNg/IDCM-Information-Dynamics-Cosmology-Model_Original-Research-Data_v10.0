#!/usr/bin/python3
"""O238 — Script 10: freeze v2 誤差權重 fit — c/s 離群 σ 級 + α 穩健性

scripts/09 P4 顯示 fit 預言比 vs lattice 全部巨大偏差 — 但 unweighted.
本 script 加 freeze v2 誤差權重 (lattice 精度), 誠實評估:
  P1 質量 log 誤差傳播 (由 freeze v2 比誤差)
  P2 weighted OLS (α, C) vs unweighted — α≈φ² 喺 weighted 下穩唔穩?
  P3 weighted 固定 φ² → c/s 離群嘅正規化 z-score (resid/σ)
  P4 比空間: 每對 quark 比 fit 預言 vs lattice z
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
M0 = 27.900915
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2

# freeze v2 (S2) 質量集 + 誤差 (MeV; 比誤差由 O234 預言 register)
# d/u=2.1505±0.111(5.2%), s/u=42.8893±1.5165(3.5%), c/s=11.652(maintained, 誤差取 FLAG~1.5%),
# b/c=4.586±0.012(0.26%), b/ms RGI=53.3692±0.7374(1.4%) — 個別質量取:
MS2 = {"e": (0.51099895, 1e-7), "mu": (105.6583755, 1e-5), "tau": (1776.86, 1e-3),
       "u": (93.4/42.890, 0.0934*0.035*93.4/42.890/0.0934) if False else (93.4/42.890, 93.4/42.890*0.035),
       "d": (93.4/42.890*2.1505, 93.4/42.890*2.1505*0.052),
       "s": (93.4, 93.4*0.035),
       "c": (93.4*11.652, 93.4*11.652*0.015),
       "b": (93.4*11.652*4.586, 93.4*11.652*4.586*0.0026),
       "t": (172690.0, 172690.0*0.003)}
logm = np.array([math.log(MS2[p][0]) for p in names9])
logd = np.array([math.log(admn[n-1]) for n in SEL9])
sig = np.array([MS2[p][1]/MS2[p][0] for p in names9])   # 相對誤差 → log 誤差 ≈ 相對
print("質量 log 誤差 (≈相對誤差):")
for i, p in enumerate(names9):
    print(f"  {p:4s}: m={MS2[p][0]:10.4f}  σ_rel={sig[i]:.4e}")

print("\n═══ P1. weighted OLS ═══")
w = 1.0 / sig**2
A = np.vstack([np.ones(9), logd]).T
W = np.diag(w)
AWA = A.T @ W @ A
AWh = A.T @ (W @ logm)
c_w, *_ = np.linalg.lstsq(AWA, AWh, rcond=None)
# 誤差: cov = inv(A^T W A)
cov = np.linalg.inv(AWA)
se_w = math.sqrt(cov[1,1])
res_w = logm - A @ c_w
rms_w = math.sqrt(np.average(res_w**2, weights=w))
print(f"  weighted α = {c_w[1]:.6f} ± {se_w:.5f}  (φ² dev: {(c_w[1]-PHI2)/se_w:+.3f}σ, 79/30 dev: {(c_w[1]-79/30)/se_w:+.3f}σ)")
# unweighted 對照
c_u, *_ = np.linalg.lstsq(A, logm, rcond=None)
res_u = logm - A @ c_u
rms_u = math.sqrt((res_u**2).mean())
print(f"  unweighted α = {c_u[1]:.6f}  RMS= {rms_u:.6f}")
chk("P1.1 weighted α 仍然 φ² 3σ 內", abs(c_w[1]-PHI2)/se_w < 3,
    f"α_w={c_w[1]:.5f}±{se_w:.5f} {abs(c_w[1]-PHI2)/se_w:.2f}σ")

print("\n═══ P2. weighted 固定 φ² → C + z-score ═══")
# weighted 平均 log C (固定斜率 φ²): 最小化 Σw(m - a - φ²·d)²
logC_w = np.average(logm - PHI2*logd, weights=w)
seC = math.sqrt(1.0/w.sum())
resid_f = logm - (logC_w + PHI2*logd)
print(f"  log C = {logC_w:.6f} ± {seC:.5f}  (C = {math.exp(logC_w):.6g} MeV)")
print(f"  每個點: resid, z=resid/σ, σ")
for i, p in enumerate(names9):
    z = resid_f[i]/sig[i]
    print(f"  {p:4s}: resid={resid_f[i]:+.4f}  z={z:+.1f}σ  σ={sig[i]:.2e}")

print("\n═══ P3. 比空間: fit 預言比 vs lattice z ═══")
Cw = math.exp(logC_w)
mp = {p: Cw * admn[SEL9[names9.index(p)]-1] ** PHI2 for p in ["u","d","s","c","b"]}
pairs = [("d","u",2.1505,0.111), ("s","u",42.8893,1.5165), ("c","s",11.652,0.175),
         ("b","c",4.586,0.012), ("b","s",53.3692,0.7374)]
big = 0
for p1, p2, lat, lat_e in pairs:
    fp = mp[p1]/mp[p2]
    z = (fp-lat)/lat_e
    if abs(z) > 3: big += 1
    print(f"  {p1}/{p2}: fit={fp:9.4f} vs lattice={lat:9.4f}±{lat_e:.4f}  z={z:+.1f}σ")
chk("P3.1 至少 3/5 個比 fit 偏離 lattice >3σ (誠實負)", big >= 3,
    f"{big}/5 比 >3σ")

print("\n═══ P4. 剔 c/s 後 weighted fit — 剩 7 點結構 ═══")
keep = [i for i in range(9) if i not in (3, 5)]
A7 = A[keep]; W7 = np.diag(w[keep]); lm7 = logm[keep]; ld7 = logd[keep]
c7, *_ = np.linalg.lstsq(A7.T @ W7 @ A7, A7.T @ (W7 @ lm7), rcond=None)
res7 = lm7 - A7 @ c7
rms7w = math.sqrt(np.average(res7**2, weights=w[keep]))
print(f"  7 點 weighted α = {c7[1]:.6f}  RMS_w = {rms7w:.6f}")
for j, i in enumerate(keep):
    p = names9[i]
    print(f"  {p:4s}: z={res7[j]/sig[i]:+.1f}σ  resid={res7[j]:+.4f}")

out = {"alpha_w": float(c_w[1]), "se_w": float(se_w), "alpha_u": float(c_u[1]),
       "logC_w": float(logC_w), "zscores": {names9[i]: float(resid_f[i]/sig[i]) for i in range(9)},
       "pair_zs": {}}
with open("data/10_freeze_v2_weighted.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")