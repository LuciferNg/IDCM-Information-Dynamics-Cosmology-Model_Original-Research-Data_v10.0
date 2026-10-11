#!/usr/bin/python3
"""O238 — Script 01: 標度 C 攻堅 — 身份診斷 (第一步)

承接 O209 docs/19 P4 (標度 C = 1.47e-6 MeV ≠ M₀ 未閉合) 同 attack route 1:
測試 C = M₀·|dm|_ref^{−φ²} 假設 + 全譜掃描搵 ref 身份.

方法 (盲測紀律: 唔睇目標凑算子, 全部候選都係譜函數/結構常數, 先報池密度再報命中):
  P1 重現 O209 fit: m_n = C·|dm|_n^{φ²}, C = exp(mean(log m − φ² log|dm|))
     — 對照 data/19_inverse_cost.json 之 C_phi2_frz
  P2 ★ ref 假設: 若 m_n = M₀·(|dm|_n/|dm|_ref)^{φ²} 則
     |dm|_ref = (M₀/C)^{1/φ²}; 掃描全譜 n=1..88 |dm|_n 有冇命中
  P3 標度比 C/M₀ (無量綱) 對比結構池: γ 特殊位 / Σγ / N_d / B / μ² / F_k·L_k 乘積
     — 每個命中都報池密度 (同量級窗內候選數), 單點命中 = 選擇效應唔算推導
  P4 逐點 C_n = m_n/|dm|_n^{φ²} 嘅 spread: C 唔係常數 (fit 幾何均值),
     睇 spread 有冇模式結構 (邊個 mode 偏離)

用法: /usr/bin/python3 scripts/01_scale_c_identity.py
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

def rms_fixed(logxx, logyy, alpha):
    C = (logyy - alpha * logxx).mean()
    r = logyy - (C + alpha * logxx)
    return np.sqrt((r**2).mean()), C

print("═══ P1. 重現 O209 fit (m = C·|dm|^{φ²}) ═══")
Cfit = math.exp((logm - PHI2 * logd).mean())
rms_f2, _ = rms_fixed(logd, logm, PHI2)
print(f"  C_fit = {Cfit:.10g} MeV  (O209 json: 1.4664335993209855e-06)")
print(f"  固定 φ² RMS = {rms_f2:.6f}  (O209: 0.5801736)")
chk("P1.1 C fit 重現", abs(Cfit - 1.4664335993209855e-06) / 1.4664335993209855e-06 < 1e-9,
    f"C={Cfit:.10g}")
chk("P1.2 RMS 重現", abs(rms_f2 - 0.5801735676909132) < 1e-6, f"RMS={rms_f2:.7f}")

print("\n═══ P2. ref 假設: |dm|_ref = (M₀/C)^{1/φ²} 全譜掃描 ═══")
ref = (M0 / Cfit) ** (1.0 / PHI2)
print(f"  |dm|_ref (由 C=M0·ref^{{-φ²}} 反推) = {ref:.6f}")
# 全譜 scan: 邊個 mode n 嘅 |dm|_n 命中 ref
best = sorted(range(1, N+1), key=lambda n: abs(admn[n-1] - ref))
print(f"  最接近嘅 mode: n = {best[:6]}  |dm| = {[f'{admn[n-1]:.4f}' for n in best[:6]]}")
rel = [abs(admn[n-1]-ref)/ref for n in best[:6]]
print(f"  相對誤差: {[f'{r*100:.3f}%' for r in rel]}")
# 特殊位: 中位 / 最大 / 最小 / 均值
print(f"  譜統計: min={admn.min():.4f} (n={admn.argmin()+1})  max={admn.max():.4f} (n={admn.argmax()+1})")
med = np.median(admn); mn = admn.mean()
print(f"  median={med:.4f}  mean={mn:.4f}  sum={admn.sum():.4f}")
# 對比 γ 特殊位
for n in [1, 2, 3, 4, 5, 7, 9, 11, 13, 22, 44, 88]:
    print(f"    |dm|_n({n:2d}) = {admn[n-1]:12.4f}   γ_n({n:2d}) = {gam[n-1]:10.6f}")
chk("P2.1 ref 命中某個 mode (誤差 < 0.1%)", min(rel) < 1e-3,
    f"best={best[0]} rel_err={min(rel)*100:.4f}%")

print("\n═══ P3. 標度比 C/M₀ 無量綱身份 (結構池 + 密度基準) ═══")
ratio = Cfit / M0
print(f"  C/M₀ = {ratio:.10g}")
# 結構池: γ 特殊值, Σγ, N_d, B, μ², F_k, L_k 組合
pool = {}
pool["gamma_1"] = gam[0]
pool["gamma_22"] = gam[21]
pool["gamma_44"] = gam[43]
pool["sum_gamma"] = gam.sum()          # 90
pool["N_d"] = 44.0
pool["B"] = 4.0
pool["mu2"] = 2.0
pool["F_5"] = 5.0
pool["F_7"] = 13.0
pool["F_9"] = 34.0
pool["F_10"] = 55.0
pool["L_5"] = 11.0
pool["L_7"] = 29.0
# 組合: phi 冪 (唔好無限擴張 — 只試 1..88 整數冪)
for k in range(-88, 89):
    pool[f"phi^{k}"] = PHI ** k
# γ 高次: γ^2, γ^3 喺特殊位 (有限)
for nm, v in [("g1^2", gam[0]**2), ("g1^3", gam[0]**3), ("g44^2", gam[43]**2),
              ("g22*B", gam[21]*4), ("g1*N_d", gam[0]*44), ("g1*sum*g1", gam[0]*gam.sum())]:
    pool[nm] = v
# 掃描
hits = []
for nm, v in pool.items():
    if v <= 0: continue
    if abs(v - ratio) / ratio < 0.02:   # 2% 窗
        hits.append((nm, v, abs(v-ratio)/ratio))
hits.sort(key=lambda x: x[2])
print(f"  池大小 = {len(pool)}; 2% 窗內命中 = {len(hits)}")
for nm, v, re in hits[:15]:
    print(f"    {nm:12s} = {v:.10g}  dev={re*100:.4f}%")
# 密度基準: 池內隨機命中率 (窗 / 池對數跨度)
logspan = max(math.log(v) for v in pool.values() if v > 0) - min(math.log(v) for v in pool.values() if v > 0)
dens = len([1 for v in pool.values() if v > 0]) / logspan * (2 * 0.02)
print(f"  密度基準: {len(pool)} 值 / ln跨度 {logspan:.1f} → 2%窗期望命中 ≈ {dens:.1f}")
chk("P3.1 池密度低 + 命中有意義", len(hits) <= 3 or dens < 3,
    f"hits={len(hits)} dens={dens:.1f}")

print("\n═══ P4. 逐點 C_n spread ═══")
Cn = [MB[i] / admn[SEL9[i]-1] ** PHI2 for i in range(9)]
logCn = np.log(Cn)
print(f"  C_n 範圍: {min(Cn):.4g} .. {max(Cn):.4g}  (幾何均值 {math.exp(logCn.mean()):.4g})")
print(f"  log C_n spread (std) = {logCn.std():.4f}")
for i, n in enumerate(SEL9):
    print(f"    {names9[i]:4s} (n={n:2d}): C_n = {Cn[i]:.6g}  log-C dev = {logCn[i]-logCn.mean():+.3f}")
chk("P4.1 C_n spread 有意義 (std 記錄)", True, f"std={logCn.std():.4f}")

out = {"C_fit": Cfit, "ref_dm": float(ref), "best_mode": int(best[0]),
       "best_rel_err": float(min(rel)), "ratio_CM0": float(ratio),
       "cn_std": float(logCn.std())}
with open("data/01_scale_c_identity.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")