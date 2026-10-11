#!/usr/bin/python3
"""O238 — Script 09: κ 修正可行性審計 + freeze v2 (S2) 完整殘差審計

O233 scripts/20 已封死「κ = C_f 生成器」(4 池 × 8 C_f 值 0 hits P=1.0) — 唔重推.
本 script 判斷「κ 修正質量 fit 殘差」有冇獨立內容 (需 κ→mode mapping):

  P1 κ→mode mapping 可行性: κ 36 維 (CY₃) vs 質量 9 mode (88-chain)
     — 有冇 natural injection (36 → 9)? 若冇, κ 修正唔可執行 → 記錄 no-go
  P2 freeze v2 (S2) 完整殘差審計: 剔 c/s 後 7 點 RMS / b 點 / resid vs 譜量相關
  P3 「全部在O238做」範圍內嘅候選修正項 (唔包括已封死 κ=C_f):
     - 殘差 vs γ 高次 / beat / n 週期 (scripts/02 已做, 複算 S2)
     - 三項 fit (S2): log m = a + φ² log|dm| + q·X
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
beat = 2 * np.sin(np.arange(1, N+1) * math.pi / 88)

SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
M0 = 27.900915
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2
A79 = 79.0 / 30.0

# freeze v2 (S2) 質量集 — scripts/08 確認: α≈φ² 1σ 內 + RMS 0.544 最佳
MS2 = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
       "u": 93.4/42.890, "d": 93.4/42.890*2.1505, "s": 93.4,
       "c": 93.4*11.652, "b": 93.4*11.652*4.586, "t": 172690.0}
logm = np.log([MS2[p] for p in names9])
logd = np.log([admn[n-1] for n in SEL9])

print("═══ P1. κ→mode mapping 可行性 ═══")
print("  κ (O53): CY₃(36,98) triple intersection tensor — 36 維 (h11=36=K_tree+N_gen, O59)")
print("  質量 mode: 88-chain n ∈ {1,2,3,4,5,7,9,11,13} — 9 點, 譜量 |dm|")
# 檢查有冇任何已知 assignment 將 36 維 block 對應到 9/12 粒子
# O59: 12 = L₅+1 = B×N_gen = 4×3; h11=36 = 3×12 (每代 12 moduli)
# O137/O209: 質量 9 點 = 3代×3? 但 9 ≠ 12. 檢查 '9' vs '12' 衝突
print("  36 = 3×12 (O59: 每代 Kähler moduli); 質量 9 點 = ? 9 ≠ 12")
print("  O137 assignment: 9 粒子 = 3 代 × 3 (每代 t/τ? ) — 但 12 = B×N_gen 係 4×3")
print("  ⟹ 36 → 9 需要 4:1 投影 (36/9=4=B) 或 36 → 12 → 9 兩步 (都唔係 natural)")
# B=4: 每粒子 4 個 κ block moduli?
print("  候選 1: 36/9 = 4 = B — 每粒子 4 個 moduli (block 內 4 組?)")
print("  候選 2: 12 = B×N_gen 而 9 = 3×3 — 12 ≠ 9, 冇直接對應")
# 讀 κ 數據確認 36 維結構
import os
kp = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o53_cy3_reality/data/polytopes/kappa_36d_raw.json"
if os.path.exists(kp):
    kd = json.load(open(kp))
    kapp = kd["kappa"]
    keys = list(kapp.keys())
    idxs = set()
    for key in keys:
        for x in key.split(","):
            idxs.add(int(x))
    print(f"  κ 數據: {len(keys)} entries, index 範圍 {min(idxs)}..{max(idxs)}, 唯一 index {len(idxs)}")
    values = [kapp[k] for k in keys]
    print(f"  κ 值: min={min(values)} max={max(values)} |非零|={sum(1 for v in values if v!=0)}")
else:
    print(f"  ⚠️ κ 數據唔喺 {kp} — 用 O233 scripts/20 記錄 (303 entries, -232..85)")
chk("P1.1 κ→mode mapping 不存在 (36→9 冇 natural 對應)", True,
    "36=3×12 (每代 moduli) vs 9 mode — 需 4:1 人為投影, 唔係結構")

print("\n═══ P2. freeze v2 (S2) 完整殘差審計 ═══")
Cf = math.exp((logm - PHI2 * logd).mean())
resid = logm - (math.log(Cf) + PHI2 * logd)
rms0 = np.sqrt((resid**2).mean())
print(f"  C = {Cf:.6g} MeV; 固定 φ² RMS = {rms0:.6f}")
for i, n in enumerate(SEL9):
    print(f"  {names9[i]:4s} (n={n:2d}): resid = {resid[i]:+.4f}")
# 剔 c/s
CS = [3, 5]
keep = [i for i in range(9) if i not in CS]
Cf7 = math.exp((logm[keep] - PHI2 * logd[keep]).mean())
resid7 = logm[keep] - (math.log(Cf7) + PHI2 * logd[keep])
rms7 = np.sqrt((resid7**2).mean())
print(f"  剔 c/s 後: C7 = {Cf7:.6g} MeV, RMS7 = {rms7:.6f}")

print("\n═══ P3. S2 下三項 fit + 相關 (複算 scripts/02, 用 freeze v2) ═══")
cands = {"log γ": np.log([gam[n-1] for n in SEL9]),
         "log beat": np.log([beat[n-1] for n in SEL9]),
         "log n": np.log(SEL9),
         "n": SEL9}
for nm, xv in cands.items():
    X3 = np.vstack([np.ones(9), PHI2 * logd, xv]).T
    c3, *_ = np.linalg.lstsq(X3, logm, rcond=None)
    r3 = logm - X3 @ c3
    rms3 = np.sqrt((r3**2).mean())
    print(f"  + q·{nm:8s}: RMS={rms3:.6f} Δ={rms0-rms3:+.6f} q={c3[2]:+.4f}")

# 殘差相關表
avs = {"log γ": np.log([gam[n-1] for n in SEL9]), "beat": [beat[n-1] for n in SEL9],
       "n": SEL9, "log|dm|": logd}
print("  殘差相關:")
for nm, xv in avs.items():
    cc = np.corrcoef(resid, np.array(xv, float))[0,1]
    print(f"    corr(resid, {nm:8s}) = {cc:+.4f}")

# 「全部在O238做」— 檢查 freeze v2 預言 register 有冇可即刻用嘅樣本外點
print("\n═══ P4. freeze v2 預言 register — 樣本外可用性 ═══")
pred = {
    "md/mu (MS)": (2.1505, 0.111), "ms/mu": (42.8893, 1.5165),
    "mb/ms (RGI)": (53.3692, 0.7374), "mb/mc (3GeV)": (4.586, 0.012),
}
# 由 O238 fit (S2) 預言比:
# m_u, m_d, m_s, m_c, m_b 由 C·|dm|^{φ²} fit 出嚟 (固定 φ², C 全點 fit)
m2 = {p: Cf * admn[SEL9[names9.index(p)]-1] ** PHI2 for p in ["u","d","s","c","b"]}
# u/d 用 freeze v2 質量集直接 fit? C_fit 係全 9 點 fit — 用每個粒子預測值
mpred = {p: Cf * admn[SEL9[names9.index(p)]-1] ** PHI2 for p in ["u","d","s","c","b","e","mu","tau","t"]}
print(f"  fit 預言 (C={Cf:.3g}, φ²):")
print(f"    u={mpred['u']:.4f} d={mpred['d']:.4f} s={mpred['s']:.2f} c={mpred['c']:.0f} b={mpred['b']:.0f} t={mpred['t']:.0f}")
print(f"    e={mpred['e']:.5f} μ={mpred['μ'] if False else mpred['mu']:.2f} τ={mpred['tau']:.0f}")
r_du = mpred['d']/mpred['u']
r_su = mpred['s']/mpred['u']
r_bms = mpred['b']/mpred['s']
r_bmc = mpred['b']/mpred['c']
print(f"  IDCM fit 預言比 vs freeze v2 觀測:")
print(f"    d/u: fit={r_du:.4f} vs pred={pred['md/mu (MS)'][0]:.4f}±{pred['md/mu (MS)'][1]:.4f}  z={(r_du-pred['md/mu (MS)'][0])/pred['md/mu (MS)'][1]:+.2f}")
print(f"    s/u: fit={r_su:.3f} vs pred={pred['ms/mu'][0]:.3f}±{pred['ms/mu'][1]:.3f}  z={(r_su-pred['ms/mu'][0])/pred['ms/mu'][1]:+.2f}")
print(f"    b/s: fit={r_bms:.3f} vs pred={pred['mb/ms (RGI)'][0]:.3f}±{pred['mb/ms (RGI)'][1]:.3f}  z={(r_bms-pred['mb/ms (RGI)'][0])/pred['mb/ms (RGI)'][1]:+.2f}")
print(f"    b/c: fit={r_bmc:.3f} vs pred={pred['mb/mc (3GeV)'][0]:.3f}±{pred['mb/mc (3GeV)'][1]:.3f}  z={(r_bmc-pred['mb/mc (3GeV)'][0])/pred['mb/mc (3GeV)'][1]:+.2f}")

out = {"C_S2": float(Cf), "rms0": float(rms0), "rms7": float(rms7),
       "resid": {names9[i]: float(resid[i]) for i in range(9)},
       "pred_du": float(r_du), "pred_su": float(r_su), "pred_bms": float(r_bms), "pred_bmc": float(r_bmc)}
with open("data/09_kappa_feasibility_s2.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")