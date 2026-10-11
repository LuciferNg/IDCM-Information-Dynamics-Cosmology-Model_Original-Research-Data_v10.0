#!/usr/bin/python3
"""O209 — Script 16: R6/R8 質量譜 scheme 穩健性重推 (v2)
真正 fit 定義 (scripts/11 一致): log m(MeV) ~ α·log|dm|, 9 點含 t, α=+2.633254
對照兩套質量集:
  A) PDG 絕對質量 (docs/11 用, 含混標度:c_s = m_c(m_c)/m_s(2GeV))
  B) O234 freeze v1.1 自洽質量 (以 m_s(2GeV)=93.4 為錨; c=11.652·s=1088MeV(同scheme), b=3.291·c=3582MeV, t 用 pole)
焦點: α=79/30 喺 freeze 下死唔死? c/s resid 點變? RMS 有冇淨?
"""
import numpy as np, math, json

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

N, NC = 88, 88
idxx = np.arange(1, N + 1)
psii = np.array([np.sin(n * math.pi * idxx / (N + 1)) for n in range(1, NC + 1)])
psii = psii / np.linalg.norm(psii, axis=1)[:, None]
Xm = np.diag(idxx - idxx.mean())
V = psii @ Xm @ psii.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, NC + 1)])
D = E[:, None] - E[None, :]
G = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(G, 0.0)
dm = np.einsum('ab,ab->a', V ** 2, G)
admn = np.abs(dm)

SEL = [1, 2, 3, 4, 5, 7, 9, 11, 13]
absdm = np.abs(dm[[n - 1 for n in SEL]])
logdm = np.log(absdm)

# 質量集 A: PDG (scripts/11 用)
MA = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
      "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0}
# 質量集 B: O234 freeze v1.1 自洽 (m_s=93.4 錨; ratio: d/u=2.1505, s/u=42.890, c/s=11.652, b/c=3.291, μ/e, τ/μ)
MB = {"e": 0.51099895, "mu": 206.77 * 0.51099895, "tau": 16.817 * 206.77 * 0.51099895,
      "s": 93.4,
      "u": 93.4 / 42.890, "d": 93.4 / 42.890 * 2.1505,
      "c": 93.4 * 11.652, "b": 93.4 * 11.652 * 3.291,
      "t": 172690.0}  # t 保留 pole (VEV 分離, scheme 角色唔同)

name9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]  # O209 |dm| 分配 frame: n=1,2,3,4,5,7,9,11,13 降序
# O209 唯一分配: |dm| 最大 n=1 → t(最重), ..., n=13 → e(最輕) — scripts/11 配對
print("═══ P1. 兩套質量集 + log m vs log|dm| ═══")
print(f"  {'n':>2s} {'f':4s} {'|dm|':>9s} {'m_A(PDG)':>10s} {'m_B(frz)':>10s}")
for i, n in enumerate(SEL):
    f = name9[i]
    print(f"  {n:2d} {f:4s} {absdm[i]:9.1f} {MA[f]:10.2f} {MB[f]:10.2f}")

def fit(mset):
    logm = np.log(np.array([mset[p] for p in name9]))
    A = np.vstack([np.ones(9), logdm]).T
    coef, *_ = np.linalg.lstsq(A, logm, rcond=None)
    res = logm - A @ coef
    rms = float(np.sqrt((res ** 2).mean()))
    corr = float(np.corrcoef(logdm, logm)[0, 1])
    return coef[1], rms, corr, name9, res, logm

alpha_A, rms_A, corr_A, nm, res_A, logm_A = fit(MA)
alpha_B, rms_B, corr_B, nm, res_B, logm_B = fit(MB)
print(f"\nP1. α_OLS: PDG = {alpha_A:.8f} (RMS {rms_A:.6f} corr {corr_A:.6f})")
print(f"          FRZ = {alpha_B:.8f} (RMS {rms_B:.6f} corr {corr_B:.6f})")
chk("P1.1 PDG α_OLS = 2.63325408 (docs/11 重現)", abs(alpha_A - 2.63325408) < 1e-4, f"{alpha_A:.6f}")
chk("P1.2 PDG RMS = 0.58722813 (docs/11 重現)", abs(rms_A - 0.58722813) < 1e-4, f"{rms_A:.6f}")

# ── P2. 79/30 喺 freeze scheme 下 ──
alpha79 = 79 / 30
print(f"\n═══ P2. α=79/30 候選穩健性 ═══")
print(f"  79/30 = {alpha79:.10f}")
print(f"  PDG rel_dev = {abs(alpha79-alpha_A)/alpha_A:.2e}   FRZ rel_dev = {abs(alpha79-alpha_B)/alpha_B:.2e}")
chk("P2.1 PDG dev < 1e-4 (docs/11)", abs(alpha79 - alpha_A) / alpha_A < 1e-4, f"{abs(alpha79-alpha_A)/alpha_A:.2e}")
chk("P2.2 FRZ dev < 1e-3 (scheme 穩健 → 候選生存)", abs(alpha79 - alpha_B) / alpha_B < 1e-3, f"{abs(alpha79-alpha_B)/alpha_B:.2e}")

# 固定 α=79/30 下兩 scheme RMS
def fix_rms(mset):
    logm = np.log(np.array([mset[p] for p in name9]))
    M0 = (logm - alpha79 * logdm).mean()
    r = logm - (M0 + alpha79 * logdm)
    return float(np.sqrt((r ** 2).mean()))
print(f"  固定 79/30: PDG RMS={fix_rms(MA):.6f}  FRZ RMS={fix_rms(MB):.6f}")

# ── P3. resid 對照 (freeze 下 c/s 離群點?) ──
print(f"\n═══ P3. resid 對照 ═══")
print(f"  {'f':4s} {'resid_A':>8s} {'resid_B':>8s}")
for i, p in enumerate(name9):
    print(f"  {p:4s} {res_A[i]:+8.3f} {res_B[i]:+8.3f}")
chk("P3.1 PDG c/s 離群 (resid>+0.5)", res_A[name9.index('c')] > 0.5 and res_A[name9.index('s')] > 0.5,
    f"c={res_A[name9.index('c')]:+.3f} s={res_A[name9.index('s')]:+.3f}")
chk("P3.2 freeze c/s 離群仍在 (scheme 唔係離群根源)", res_B[name9.index('c')] > 0.5 and res_B[name9.index('s')] > 0.5,
    f"c={res_B[name9.index('c')]:+.3f} s={res_B[name9.index('s')]:+.3f}")

# ── P4. 凍結層 C_f (比層) 對 |dm|: C_f = m/(M₀γ) ──
print(f"\n═══ P4. freeze C_f shape vs log|dm| (docs/14 β=6/5 重審) ═══")
M0 = 27.900915
gam_n = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, 14)])
ns8 = [1, 2, 3, 4, 5, 7, 9, 11]
frame8 = {1: 'e', 2: 'u', 3: 'd', 4: 's', 5: 'mu', 7: 'c', 9: 'tau', 11: 'b'}
ld8 = np.log(admn[[n - 1 for n in ns8]])
lg8 = np.log(gam_n[[n - 1 for n in ns8]])
# C_f = m/(M₀γ): PDG vs freeze (每扇區標度由錨決定 — freeze 用 m_B)
cfA = np.log([MA[frame8[n]] / (M0 * gam_n[n - 1]) for n in ns8])
cfB = np.log([MB[frame8[n]] / (M0 * gam_n[n - 1]) for n in ns8])
def beta_of(lcf):
    A8 = np.vstack([np.ones(8), ld8]).T
    c, *_ = np.linalg.lstsq(A8, lcf, rcond=None)
    r = lcf - A8 @ c
    return -c[1], float(np.sqrt((r ** 2).mean())), float(np.corrcoef(ld8, lcf)[0, 1])
bA, rA, cA = beta_of(cfA)
bB, rB, cB = beta_of(cfB)
print(f"  C_f ~ |dm|^β: PDG β={bA:.4f} (RMS {rA:.4f}) | FRZ β={bB:.4f} (RMS {rB:.4f})")
chk("P4.1 PDG β ≈ 6/5 dev<0.2% (docs/14 重現)", abs(bA - 1.2) / 1.2 < 0.002, f"{bA:.4f}")
chk("P4.2 FRZ β 偏離 6/5 > 1% (scheme artifact 確認)", abs(bB - 1.2) / 1.2 > 0.01, f"{abs(bB-1.2)/1.2*100:.2f}%")

out = {
    "alpha_A": alpha_A, "alpha_B": alpha_B, "rms_A": rms_A, "rms_B": rms_B,
    "dev79_A": abs(alpha79 - alpha_A) / alpha_A, "dev79_B": abs(alpha79 - alpha_B) / alpha_B,
    "resid_A": {p: round(res_A[i], 4) for i, p in enumerate(name9)},
    "resid_B": {p: round(res_B[i], 4) for i, p in enumerate(name9)},
    "beta_PDG": bA, "beta_FRZ": bB,
    "rms_fixed_A": fix_rms(MA), "rms_fixed_B": fix_rms(MB),
}
with open("data/16_scheme_rerun.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c, _ in checks if c)}/{len(checks)} checks passed")
for nm, c, dt in checks:
    print(f"  [{'OK' if c else 'XX'}] {nm} — {dt}")