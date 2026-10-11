#!/usr/bin/python3
"""O238 — Script 03: c/s 離群遮蔽測試 — 標度 C 分層診斷

docs/02 + scripts/02: g_n (殘差) 冇簡單譜身份; c/s 離群機制已定位 O209 docs/17
(κ 張量非對角, O53/O59, 跨 O). 本 script 測試: c/s 離群係咪遮蔽咗 C 嘅結構身份 —
剔除 c/s 後 7 點 fit 嘅 C 有冇更接近框架 (M₀ / φ 冪 / 譜和)?

盲測紀律:
- 全 9 點 fit 係基線; 7 點 (無 c/s) fit 係「κ 修正後」嘅代理 (誠實標明: 唔係 κ 計算, 係剔除)
- C7/M₀ 對結構池掃描 (196 值) + 密度基準
- LOOCV leverage: 逐點剔除睇 C 變化, 邊個點最影響標度
- 唔准見 target 凑; 池同 scripts/01 一樣凍結
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
MB = np.array([172690.0, 93.4*11.652*3.291, 1776.86, 93.4*11.652, 105.6583755, 93.4,
               93.4/42.890*2.1505, 93.4/42.890, 0.51099895])
logd = np.log([admn[n-1] for n in SEL9])
logm = np.log(MB)
M0 = 27.900915
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2

CS_IDX = [3, 5]  # c, s

print("═══ P1. 全 9 點 vs 7 點 (無 c/s) fit ═══")
C9 = math.exp((logm - PHI2 * logd).mean())
keep = [i for i in range(9) if i not in CS_IDX]
C7 = math.exp((logm[keep] - PHI2 * logd[keep]).mean())
r9 = logm - (math.log(C9) + PHI2 * logd)
r7_pts = logm[keep] - (math.log(C7) + PHI2 * logd[keep])
rms7 = np.sqrt((r7_pts**2).mean())
print(f"  C (9點) = {C9:.8g} MeV")
print(f"  C (7點, 無 c/s) = {C7:.8g} MeV")
print(f"  C 變化 = {(C7-C9)/C9*100:+.3f}%")
print(f"  7 點 RMS = {rms7:.6f}")
for i in CS_IDX:
    print(f"  剔除 {names9[i]} (n={SEL9[i]}): log resid = {logm[i]-(math.log(C9)+PHI2*logd[i]):+.3f}")
chk("P1.1 7點剔除 c/s 後 C 變化顯著 (>20%)", abs(C7-C9)/C9 > 0.20,
    f"{(C7-C9)/C9*100:+.2f}%")

print("\n═══ P2. C7/M₀ 無量綱身份 (結構池掃描, 同 scripts/01 凍結) ═══")
ratio7 = C7 / M0
ratio9 = C9 / M0
print(f"  C9/M₀ = {ratio9:.10g} (scripts/01 已掃: 池 0 命中)")
print(f"  C7/M₀ = {ratio7:.10g}")
pool = {}
pool["gamma_1"] = gam[0]; pool["gamma_22"] = gam[21]; pool["gamma_44"] = gam[43]
pool["sum_gamma"] = gam.sum(); pool["N_d"] = 44.0; pool["B"] = 4.0; pool["mu2"] = 2.0
pool["F_5"] = 5.0; pool["F_7"] = 13.0; pool["F_9"] = 34.0; pool["F_10"] = 55.0
pool["L_5"] = 11.0; pool["L_7"] = 29.0
for k in range(-88, 89):
    pool[f"phi^{k}"] = PHI ** k
for nm, v in [("g1^2", gam[0]**2), ("g1^3", gam[0]**3), ("g44^2", gam[43]**2),
              ("g22*B", gam[21]*4), ("g1*N_d", gam[0]*44), ("g1*sum*g1", gam[0]*gam.sum())]:
    pool[nm] = v
hits = [(nm, v, abs(v-ratio7)/ratio7) for nm, v in pool.items()
        if v > 0 and abs(v-ratio7)/ratio7 < 0.02]
hits.sort(key=lambda x: x[2])
logspan = max(math.log(v) for v in pool.values() if v > 0) - min(math.log(v) for v in pool.values() if v > 0)
dens = len([1 for v in pool.values() if v > 0]) / logspan * (2 * 0.02)
print(f"  池 {len(pool)} 值; 2% 窗命中 = {len(hits)} (密度基準 {dens:.1f})")
for nm, v, re in hits[:10]:
    print(f"    {nm:12s} = {v:.10g}  dev={re*100:.4f}%")
chk("P2.1 C7/M₀ 池命中 < 4 (剔除無助身份)", len(hits) < 4,
    f"hits={len(hits)} dens={dens:.1f}")

print("\n═══ P3. LOOCV leverage (逐點剔除影響度) ═══")
for i in range(9):
    kp = [j for j in range(9) if j != i]
    Ci = math.exp((logm[kp] - PHI2 * logd[kp]).mean())
    print(f"  剔除 {names9[i]:4s} (n={SEL9[i]:2d}): C={Ci:.6g}  Δ={math.log(Ci)-math.log(C9):+.4f}")
dm_loocv = [abs(math.exp((logm[[j for j in range(9) if j!=i]] -
                          PHI2*logd[[j for j in range(9) if j!=i]]).mean()) - C9)/C9
            for i in range(9)]
worst = sorted(range(9), key=lambda i: -dm_loocv[i])[:3]
print(f"  最影響標度嘅 3 點: {[names9[i]+f'({dm_loocv[i]*100:.1f}%)' for i in worst]}")

print("\n═══ P4. C 對 M₀ 嘅距離檢定 ═══")
print(f"  log1p(C9/M₀) = {math.log(1+ratio9):.6f}")
print(f"  log1p(C7/M₀) = {math.log(1+ratio7):.6f}")
# C 有量綱 (MeV): 嘗試 C = M₀ × γ1^p × φ^k 雙參數空間 (細掃描, 有密度基準)
print("\n═══ P5. C = M₀·γ₁^{p}·φ^{k} 雙參數掃描 (p∈{-5..5 step .5}, k∈{-88..88}) ═══")
hits2 = []
for p10 in range(-100, 101, 5):
    p = p10 / 10.0
    for k in range(-88, 89):
        cand = M0 * gam[0] ** p * PHI ** k
        if cand <= 0: continue
        dev = abs(cand - C7) / C7
        if dev < 0.02:
            hits2.append((k, p, cand, dev))
hits2.sort(key=lambda x: x[3])
print(f"  掃描 {201*177} 組合; 2% 窗命中 = {len(hits2)}")
for k, p, v, dev in hits2[:10]:
    print(f"    k={k:4d} p={p:+.1f}: M0·γ1^{p}·φ^{k} = {v:.6g}  dev={dev*100:.3f}%")
# 密度: 2%窗 / 參數空間有效跨度
eff = 201 * 177
pdens = eff * (0.04 ** 2)  # 粗糙 2D 密度估計
print(f"  2D 密度基準 ≈ {pdens:.0f} 預期命中 (窗 2%×2%)")
chk("P5.1 雙參數命中唔超過密度基準", len(hits2) <= pdens * 2,
    f"hits={len(hits2)} dens~{pdens:.0f}")

out = {"C9": float(C9), "C7": float(C7), "C_change_pct": float((C7-C9)/C9*100),
       "rms7": float(rms7), "ratio7": float(ratio7), "hits_pool7": len(hits),
       "loocv_worst": [names9[i] for i in worst]}
with open("data/03_cs_mask_scale.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")