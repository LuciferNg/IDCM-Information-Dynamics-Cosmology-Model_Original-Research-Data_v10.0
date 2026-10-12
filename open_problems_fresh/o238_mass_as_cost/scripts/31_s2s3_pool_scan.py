#!/usr/bin/python3
"""O238 — Script 31: S2/S3 質量集 C/M₀ 對 196 結構池正式掃描

docs/04 §二 P2 只掃咗 S1 (v1.1 混標度), S2/S3 用「同量級唔會改變池結論」論證跳過。
調律者: 「Freeze v2 一直都在」⟹ S2 一直都在, 冇理由唔正式掃。

方法: 完全沿用 scripts/01 P3 結構池 (γ特殊位/Σγ/N_d/B/μ²/F_k/L_k/φ冪/γ高次), 2% 窗,
     分别掃 C(S1)/M₀, C(S2)/M₀, C(S3)/M₀ — 密度基準照計.
判準: 三套都 0 命中 = 「C 冇池身份係 scheme 無關」由論證升級為實掃; S2 命中 = 新發現 (但係後見)。

補充: O210 教訓 — 池必須凍結、唔准中途加料; scripts/01 池原樣保留.
"""
import numpy as np, math, json, os

base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o238_mass_as_cost"
os.chdir(base)

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
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2
M0 = 27.900915
SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]

# 三套質量集 (scripts/08 定義)
MS = {
    "S1_v11": {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
               "u": 93.4/42.890, "d": 93.4/42.890*2.1505, "s": 93.4,
               "c": 93.4*11.652, "b": 93.4*11.652*3.291, "t": 172690.0},
    "S2_v2_3GeV": {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
                   "u": 93.4/42.890, "d": 93.4/42.890*2.1505, "s": 93.4,
                   "c": 93.4*11.652, "b": 93.4*11.652*4.586, "t": 172690.0},
    "S3_v2_RGI": {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
                  "u": 2.97, "d": 6.53, "s": 130.0, "c": 1484.2, "b": 6938.0,
                  "t": 172690.0},
}

# scripts/01 P3 結構池 — 原樣 (凍結)
pool = {}
pool["gamma_1"] = gam[0]
pool["gamma_22"] = gam[21]
pool["gamma_44"] = gam[43]
pool["sum_gamma"] = gam.sum()  # 90
pool["N_d"] = 44.0
pool["B"] = 4.0
pool["mu2"] = 2.0
pool["F_5"] = 5.0
pool["F_7"] = 13.0
pool["F_9"] = 34.0
pool["F_10"] = 55.0
pool["L_5"] = 11.0
pool["L_7"] = 29.0
for k in range(-88, 89):
    pool[f"phi^{k}"] = PHI ** k
for nm, v in [("g1^2", gam[0]**2), ("g1^3", gam[0]**3), ("g44^2", gam[43]**2),
              ("g22*B", gam[21]*4), ("g1*N_d", gam[0]*44), ("g1*sum*g1", gam[0]*gam.sum())]:
    pool[nm] = v

print(f"結構池大小 = {len(pool)} (凍結, scripts/01 原樣)")
results = {}
for sname, mset in MS.items():
    logm = np.log([mset[p] for p in names9])
    logd = np.log([admn[n - 1] for n in SEL9])
    Cf = math.exp((logm - PHI2 * logd).mean())
    ratio = Cf / M0
    hits = []
    for nm, v in pool.items():
        if v <= 0:
            continue
        if abs(v - ratio) / ratio < 0.02:
            hits.append((nm, v, abs(v - ratio) / ratio))
    hits.sort(key=lambda x: x[2])
    logspan = max(math.log(v) for v in pool.values() if v > 0) - min(math.log(v) for v in pool.values() if v > 0)
    dens = len([1 for v in pool.values() if v > 0]) / logspan * (2 * 0.02)
    results[sname] = {"C": float(Cf), "C/M0": float(ratio), "hits": len(hits), "dens": float(dens),
                      "hit_list": [(h[0], float(h[1]), float(h[2])) for h in hits[:10]]}
    print(f"\n{sname}: C = {Cf:.8g} MeV, C/M₀ = {ratio:.6g}")
    print(f"  2% 窗命中 = {len(hits)} (密度基準 {dens:.1f})")
    for nm, v, re in hits[:10]:
        print(f"    {nm:12s} = {v:.10g}  dev={re*100:.4f}%")

out = {"pool_size": len(pool), "results": {k: {kk: vv for kk, vv in v.items()} for k, v in results.items()}}
with open("data/31_s2s3_pool_scan.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print("\nRESULT:")
for sname in MS:
    r = results[sname]
    verdict = "🔴 命中!" if r["hits"] > 0 else "🟢 0 命中 — 池身份 scheme 無關由實掃確認"
    print(f"  {sname}: {r['hits']} hits (dens {r['dens']:.1f}) — {verdict}")