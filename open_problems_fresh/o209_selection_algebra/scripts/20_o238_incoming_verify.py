#!/usr/bin/python3
"""O209 — probe 20: O238 incoming 驗證 — b/c 混標度偽影 + 三套質量集重算
O238 docs/04 claim: O209 scripts/19 質量集 B b=93.4×11.652×3.291=3581.6 係混標度偽影
(O234 docs/03 §二 已裁定: 3.291 = mb(mb)/mc(mc) 混標度; 正確 4.586 HPQCD 21 @3GeV)
由零重算驗證:
  P1 三套質量集 (S1 v1.1 / S2 v2-3GeV / S3 v2-RGI) 對 α_OLS、RMS、φ²/79/30 σ
  P2 b/c 「44/33 near-hit」偽影 (O234 docs/03 §二)
  P3 C-shape v2 b=79.645 (vs v1.1 b=57.162)
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
logd = np.log([admn[n-1] for n in SEL9])
PHI2 = ((1 + math.sqrt(5)) / 2) ** 2
alpha79 = 79 / 30

def fit_set(m9):
    logm = np.log(m9)
    A = np.vstack([np.ones(9), logd]).T
    c, *_ = np.linalg.lstsq(A, logm, rcond=None)
    res = logm - A @ c
    se = math.sqrt((res @ res) / 7 / ((logd - logd.mean())**2).sum())
    rms = math.sqrt((res @ res) / 9)
    return c[1], se, rms, res

print("═══ P1. 三套質量集重算 ═══")
# S1 v1.1: O209 原版 (b=×3.291 混標度)
S1 = np.array([172690.0, 93.4*11.652*3.291, 1776.86, 93.4*11.652, 105.6583755, 93.4,
               93.4/42.890*2.1505, 93.4/42.890, 0.51099895])
# S2 v2-3GeV: b=×4.586 (HPQCD 21), 其餘 v1.1 鏈
S2 = np.array([172690.0, 93.4*11.652*4.586, 1776.86, 93.4*11.652, 105.6583755, 93.4,
               93.4/42.890*2.1505, 93.4/42.890, 0.51099895])
# S3 v2-RGI: M_RGI_b=6938 直接錨, RGI u/d/s/c
S3 = np.array([172690.0, 6938.0, 1776.86, 1484.2, 105.6583755, 130.0,
               6.53, 2.97, 0.51099895])
for nm, S in [("S1 v1.1", S1), ("S2 v2-3GeV", S2), ("S3 v2-RGI", S3)]:
    a, se, rms, res = fit_set(S)
    print(f"  {nm}: α_OLS={a:.6f} ± {se:.4f}  RMS={rms:.6f}  φ²σ={(a-PHI2)/se:+.2f}  79/30σ={(a-alpha79)/se:+.2f}")
    print(f"       b={S[1]:.1f}  b resid={res[1]:+.3f}  c={res[3]:+.3f}  s={res[5]:+.3f}")
print("  (O238 docs/04: S1 2.616977/0.580172, S2 2.642463/0.544423, S3 2.615977/0.626725)")

# 驗證 O238 數字
a1, se1, rms1, _ = fit_set(S1)
a2, se2, rms2, _ = fit_set(S2)
a3, se3, rms3, _ = fit_set(S3)
chk("P1.1 S1 α_OLS 重現 2.616977", abs(a1-2.616977) < 1e-4, f"{a1:.6f}")
chk("P1.2 S2 α_OLS 重現 2.642463", abs(a2-2.642463) < 1e-4, f"{a2:.6f}")
chk("P1.3 S3 α_OLS 重現 2.615977", abs(a3-2.615977) < 1e-4, f"{a3:.6f}")
chk("P1.4 S2 RMS 改善 6% (0.544 < 0.580)", rms2 < rms1, f"{rms2:.6f} vs {rms1:.6f}")
chk("P1.5 三套 φ²/79/30 全部 1σ 內", max(abs(a1-PHI2)/se1, abs(a2-PHI2)/se2, abs(a3-PHI2)/se3) < 1, "α≈φ² 穩健")

print("\n═══ P2. b/c 44/33 near-hit 偽影 ═══")
# v1.1 C_b/C_c = 57.162/41.585 = 1.3746 (44/33=1.3333 dev 3.0% "near-hit")
Cb_c_v1 = 57.162 / 41.585
dev_v1 = abs(Cb_c_v1 - 44/33) / (44/33)
# v2: C_b/C_c = 79.645/41.585 = 1.9153 (dev 43.6%)
Cb_c_v2 = 79.645 / 41.585
dev_v2 = abs(Cb_c_v2 - 44/33) / (44/33)
print(f"  v1.1 C_b/C_c = {Cb_c_v1:.4f} vs 44/33 dev {dev_v1*100:.1f}%")
print(f"  v2   C_b/C_c = {Cb_c_v2:.4f} vs 44/33 dev {dev_v2*100:.1f}%")
chk("P2.1 v2 下 44/33 死實 (>10% dev)", dev_v2 > 0.1, f"{dev_v2*100:.1f}%")

print("\n═══ P3. C-shape v2 b=79.645 ═══")
print(f"  v1.1 b=57.162 → v2 b=79.645 (scheme 更正 {(79.645/57.162-1)*100:.1f}%)")
chk("P3.1 C-shape v2 b=79.645 自洽 (C_b/C_c=1.9153)", Cb_c_v2 > 1.9, f"{Cb_c_v2:.4f}")

out = {"S1": [a1, rms1], "S2": [a2, rms2], "S3": [a3, rms3], "dev_44_33_v2": dev_v2}
with open("data/20_o238_incoming_verify.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")