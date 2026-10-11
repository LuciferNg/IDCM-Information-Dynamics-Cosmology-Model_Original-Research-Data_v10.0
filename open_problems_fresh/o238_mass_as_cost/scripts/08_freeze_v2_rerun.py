#!/usr/bin/python3
"""O238 — Script 08: freeze v2 scheme 重跑 — b/c 混標度偽影審計

O234 docs/03 §二 裁定: O209 質量集 B 嘅 b = 93.4×11.652×3.291 = 3582 MeV 用咗
PDG mb(mb)/mc(mc) = 3.291 混標度 (兩個唔同 scheme 標度相除) — 偽影死實.
freeze v2: b/c @3GeV = 4.586 (HPQCD 21) / M_RGI_b = 6938 MeV.

本 script 用三套質量集重跑 O238 R1 全部核心 fit, 審計結論穩定性:
  S1 v1.1 (O209 原版): u=93.4/42.89, d=×2.1505, s=93.4, c=×11.652, b=×3.291, t=pole
  S2 v2-3GeV (最小修正): 同上但 b/c=4.586 → b = 4991 (保留 v1.1 錨鏈)
  S3 v2-RGI (RGI 錨): u=2.97, d=6.53, s=130.0 (由 mb/ms RGI 53.369), c=1484.2(mc/mu derived), b=6938.0
  輕子同 t 三套一致 (e=0.51099895, μ=105.6583755, τ=1776.86, t=172690)

檢查:
  P1 α_OLS 三套對比 (φ²/79/30 σ 檢定)
  P2 C (固定 φ²) 三套對比 + C/M₀ 池掃描
  P3 殘差: c/s 離群三套下生存? b 離群點點變?
  P4 LOOCV φ² vs 79/30 三套下 MSPE
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

SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
M0 = 27.900915
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2
A79 = 79.0 / 30.0

# 三套質量集 (eV→MeV 統一; 全 MeV)
sets = {
    "S1_v11": {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
               "u": 93.4/42.890, "d": 93.4/42.890*2.1505, "s": 93.4,
               "c": 93.4*11.652, "b": 93.4*11.652*3.291, "t": 172690.0},
    "S2_v2_3GeV": {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
                   "u": 93.4/42.890, "d": 93.4/42.890*2.1505, "s": 93.4,
                   "c": 93.4*11.652, "b": 93.4*11.652*4.586, "t": 172690.0},
    "S3_v2_RGI": {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
                  "u": 2.97, "d": 6.53, "s": 130.0,
                  "c": 1484.2, "b": 6938.0, "t": 172690.0},
}
for nm_, d in sets.items():
    assert len(d) == 9, nm_
    print(f"{nm_}: b = {d['b']:.1f}  u={d['u']:.4f} d={d['d']:.4f} s={d['s']:.2f} c={d['c']:.1f}")

logd = np.log([admn[n-1] for n in SEL9])

def full_fit(mset):
    logm = np.log([mset[p] for p in names9])
    A = np.vstack([np.ones(9), logd]).T
    c, *_ = np.linalg.lstsq(A, logm, rcond=None)
    res = logm - A @ c
    s2 = (res @ res) / 7
    Sxx = ((logd - logd.mean())**2).sum()
    se = math.sqrt(s2 / Sxx)
    rms_ols = math.sqrt((res @ res) / 9)
    Cf = math.exp((logm - PHI2 * logd).mean())
    rms_f2 = math.sqrt(((logm - (math.log(Cf) + PHI2 * logd))**2).mean())
    # LOOCV blind
    rf, ra = [], []
    for i in range(9):
        tr = [j for j in range(9) if j != i]
        Cfi = math.exp((logm[tr] - PHI2 * logd[tr]).mean())
        Cai = math.exp((logm[tr] - A79 * logd[tr]).mean())
        rf.append(math.log(Cfi * admn[SEL9[i]-1]**PHI2) - logm[i])
        ra.append(math.log(Cai * admn[SEL9[i]-1]**A79) - logm[i])
    mspe_f = float(np.mean(np.array(rf)**2))
    mspe_a = float(np.mean(np.array(ra)**2))
    return {"alpha": c[1], "se": se, "rms_ols": rms_ols, "C": Cf, "rms_f2": rms_f2,
            "resid": {names9[i]: float(res[i]) for i in range(9)},
            "mspe_f": mspe_f, "mspe_a": mspe_a}

print("\n═══ P1. α_OLS + σ 檢定 (φ²/79/30) 三套對比 ═══")
res_all = {}
for nm_, mset in sets.items():
    r = full_fit(mset)
    res_all[nm_] = r
    f_sig = (r["alpha"] - PHI2) / r["se"]
    a_sig = (r["alpha"] - A79) / r["se"]
    print(f"  {nm_:12s}: α={r['alpha']:.6f}±{r['se']:.4f}  φ²:{f_sig:+.2f}σ  79/30:{a_sig:+.2f}σ  RMS={r['rms_ols']:.6f}")
chk("P1.1 α≈φ² 三套都喺 1σ 內", all(abs(res_all[s]["alpha"]-PHI2)/res_all[s]["se"] < 1 for s in sets),
    " vs ".join(f"{s}:{(res_all[s]['alpha']-PHI2)/res_all[s]['se']:+.2f}σ" for s in sets))

print("\n═══ P2. C (固定 φ²) + C/M₀ ═══")
for nm_, mset in sets.items():
    r = res_all[nm_]
    print(f"  {nm_:12s}: C={r['C']:.6g} MeV  C/M₀={r['C']/M0:.6g}  RMS_f2={r['rms_f2']:.6f}")

print("\n═══ P3. 殘差 (c/s 離群三套下? b 點?) ═══")
for nm_, mset in sets.items():
    r = res_all[nm_]
    cs = f"c={r['resid']['c']:+.3f} s={r['resid']['s']:+.3f} b={r['resid']['b']:+.3f}"
    print(f"  {nm_:12s}: {cs}  | 超出 0.5: {[p for p in names9 if abs(r['resid'][p])>0.5]}")
chk("P3.1 c/s 離群喺 v2 下仍在 (非 scheme artifact)", 
    all(abs(res_all[s]["resid"]["c"]) > 0.5 and abs(res_all[s]["resid"]["s"]) > 0.5 for s in sets),
    " c/s ".join(f"{s}:c={res_all[s]['resid']['c']:+.2f},s={res_all[s]['resid']['s']:+.2f}" for s in sets))

print("\n═══ P4. LOOCV φ² vs 79/30 ═══")
for nm_, mset in sets.items():
    r = res_all[nm_]
    print(f"  {nm_:12s}: MSPE(φ²)={r['mspe_f']:.5f} MSPE(79/30)={r['mspe_a']:.5f} ratio={r['mspe_f']/r['mspe_a']:.4f}")
chk("P4.1 LOOCV 唔可分維持 (ratio ∈ [0.9,1.1])", 
    all(0.9 < res_all[s]["mspe_f"]/res_all[s]["mspe_a"] < 1.1 for s in sets),
    " vs ".join(f"{s}:{res_all[s]['mspe_f']/res_all[s]['mspe_a']:.4f}" for s in sets))

out = {"sets": {nm_: {k: v for k, v in r.items() if k != "resid"}
                for nm_, r in res_all.items()},
       "resid": {nm_: r["resid"] for nm_, r in res_all.items()}}
with open("data/08_freeze_v2_rerun.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")