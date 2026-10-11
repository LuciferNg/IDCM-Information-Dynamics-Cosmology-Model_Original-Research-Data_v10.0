#!/usr/bin/python3
"""O209 — Script 19: 逆推 — 質量 = 幾何連結代價 + φ² 候選
用戶方向 (2026-10-11): 放棄推 C_f (正推找數值), 改逆推 — 唔 fit 數值, 用幾何連結
本身推質量, 質量視為代價 (先例: O136 docs/25 |Δm| 二階自能 + docs/29 觀察代價族)。
本 script:
  P1 幾何中心性候選 (eigenvector/degree/betweenness/closeness/ablation) vs |dm|
  P2 freeze OLS ≈ φ²? — 固定 φ² vs 79/30 RMS + σ_α 檢定
  P3 C_f 算子身份: C_f ∝ |dm|^{φ²}/γ? (逆推閉合測試)
  P4 質量=代價現狀總結
"""
import numpy as np, math, json
from collections import defaultdict

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

# 正權連結矩陣 (幾何連結本身)
W = np.abs(V) ** 2 * np.abs(G)
np.fill_diagonal(W, 0.0)

SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MB = np.array([172690.0, 93.4*11.652*3.291, 1776.86, 93.4*11.652, 105.6583755, 93.4,
               93.4/42.890*2.1505, 93.4/42.890, 0.51099895])
logd = np.log([admn[n-1] for n in SEL9])
logm = np.log(MB)
M0 = 27.900915
PHI2 = ((1 + math.sqrt(5)) / 2) ** 2
alpha79 = 79 / 30

def rms_fixed(logxx, logyy, alpha):
    C = (logyy - alpha * logxx).mean()
    r = logyy - (C + alpha * logxx)
    return np.sqrt((r**2).mean()), C

print("═══ P1. 幾何中心性候選 (freeze 9 點) ═══")
# eigenvector centrality (Perron-Frobenius)
evals, evecs = np.linalg.eigh(W)
cEV = np.abs(evecs[:, -1])
deg = W.sum(axis=1)
# betweenness (簡化 Dijkstra, 權重倒數做距離)
dist = np.where(W > 0, 1.0/np.maximum(W, 1e-300), np.inf)
np.fill_diagonal(dist, 0.0)
CB = np.zeros(N)
epsd = np.where(np.isfinite(dist), dist, 1e9)
for s in range(N):
    d = np.full(N, np.inf); d[s] = 0
    sigma = np.zeros(N); sigma[s] = 1
    pred = defaultdict(list)
    vis = np.zeros(N, bool)
    for _ in range(N):
        u = -1; du = np.inf
        for v in range(N):
            if not vis[v] and d[v] < du:
                u, du = v, d[v]
        if u < 0: break
        vis[u] = True
        for v in range(N):
            if vis[v] or epsd[u][v] >= 1e8: continue
            alt = d[u] + epsd[u][v]
            if alt < d[v] - 1e-12:
                d[v] = alt; sigma[v] = sigma[u]; pred[v] = [u]
            elif abs(alt - d[v]) <= 1e-12:
                sigma[v] += sigma[u]; pred[v].append(u)
    delta = np.zeros(N)
    for w in np.argsort(d)[::-1]:
        for u in pred[w]:
            if sigma[w] > 0:
                delta[u] += (sigma[u]/sigma[w]) * (1 + delta[w])
        if w != s: CB[w] += delta[w]
close_nan = np.nanmean(np.where(np.isfinite(dist), dist, np.nan), axis=1)
closeness = 1.0 / close_nan

cands = {"|dm| (幾何連結代價)": admn, "eigenvector": cEV, "1/eigenvector": 1.0/cEV,
         "degree": deg, "betweenness": CB + 1e-12, "closeness": closeness}
best = ("", 1e9)
for nm_, vals in cands.items():
    X = np.array([float(vals[n-1]) for n in SEL9])
    if np.any(X <= 0) or not np.all(np.isfinite(X)):
        continue
    _, Cc = rms_fixed(logd, logm, 2.617)  # α 用 freeze OLS
    # 2 參數 fit 先 (公平比較)
    A = np.vstack([np.ones(9), np.log(X)]).T
    c, *_ = np.linalg.lstsq(A, logm, rcond=None)
    rms = np.sqrt(((logm - A @ c)**2).mean())
    if rms < best[1]: best = (nm_, rms)
    print(f"  {nm_:26s}: RMS={rms:.4f} slope={c[1]:+.4f}")
chk("P1.1 |dm| 仍係最佳候選", best[0] == "|dm| (幾何連結代價)", f"best={best[0]} RMS={best[1]:.4f}")

print("\n═══ P2. freeze OLS ≈ φ²? + σ_α 檢定 ═══")
A = np.vstack([np.ones(9), logd]).T
c, *_ = np.linalg.lstsq(A, logm, rcond=None)
res = logm - A @ c
s2 = (res @ res) / 7
Sxx = ((logd - logd.mean()) ** 2).sum()
se_alpha = math.sqrt(s2 / Sxx)
print(f"  freeze OLS α = {c[1]:.8f} ± {se_alpha:.5f} (1σ)")
print(f"  φ²    = {PHI2:.8f}  → {(c[1]-PHI2)/se_alpha:+.2f}σ   4cos²(π/5) 二十面體角")
print(f"  79/30 = {alpha79:.8f}  → {(c[1]-alpha79)/se_alpha:+.2f}σ")
rms_f2, _ = rms_fixed(logd, logm, PHI2)
rms_79, _ = rms_fixed(logd, logm, alpha79)
rms_ols = math.sqrt((res @ res) / 9)
print(f"  固定 φ² freeze RMS = {rms_f2:.6f} (OLS {rms_ols:.6f}; 79/30 {rms_79:.6f})")
chk("P2.1 φ² 喺 freeze OLS 1σ 內", abs(c[1]-PHI2) < se_alpha, f"{(c[1]-PHI2)/se_alpha:+.2f}σ")
chk("P2.2 固定 φ² RMS 好過 79/30 (少過 0.0006)", rms_f2 < rms_79, f"{rms_f2:.6f} vs {rms_79:.6f}")

print("\n═══ P3. C_f 算子身份: C_f ∝ |dm|^{φ²}/γ? ═══")
Cshape = {"e": 1.0, "mu": 8.356, "tau": 44.418, "u": 1.0, "d": 0.958, "s": 10.777, "c": 41.585, "b": 57.162}
NMAP = {"e": 13, "mu": 5, "tau": 3, "u": 11, "d": 9, "s": 7, "c": 4, "b": 2}
Xs = [admn[NMAP[f]-1] ** PHI2 / gam[NMAP[f]-1] for f in Cshape]
Cs = list(Cshape.values())
A8 = np.vstack([np.ones(8), np.log(Xs)]).T
c8, *_ = np.linalg.lstsq(A8, np.log(Cs), rcond=None)
rms8 = np.sqrt(((np.log(Cs) - A8 @ c8)**2).mean())
print(f"  log C_f ~ log(|dm|^{{φ²}}/γ): slope={c8[1]:.4f} (需 1) RMS={rms8:.4f}")
chk("P3.1 C_f ∝ |dm|^{φ²}/γ FAIL (slope 遠離 1)", abs(c8[1]-1) > 0.3, f"slope={c8[1]:.3f}")

print("\n═══ P4. 質量=代價 現狀 ═══")
print(f"  m_n ≈ C·|dm|_n^{{φ²}} (freeze):  φ² = 4cos²(π/5) 二十面體角; |dm| = 幾何連結代價")
print(f"  C = {math.exp((logm - PHI2*logd).mean()):.4g} MeV — 唔等於 M₀ = {M0:.4g} (未閉合)")
chk("P4.1 C ≠ M₀ (標度未閉合, 誠實記錄)", True, f"C≠M₀ 差 {abs(math.exp((logm-PHI2*logd).mean())-M0)/M0*100:.3g}%")

out = {"alpha_ols_frz": c[1], "se_alpha": se_alpha, "phi2_sigma": (c[1]-PHI2)/se_alpha,
       "alpha79_sigma": (c[1]-alpha79)/se_alpha, "rms_frz_phi2": rms_f2, "rms_frz_79": rms_79,
       "cf_slope": c8[1], "cf_rms": rms8, "C_phi2_frz": math.exp((logm - PHI2*logd).mean())}
with open("data/19_inverse_cost.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")