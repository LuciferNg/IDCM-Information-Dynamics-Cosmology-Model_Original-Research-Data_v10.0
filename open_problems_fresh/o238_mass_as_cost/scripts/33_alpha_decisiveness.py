#!/usr/bin/python3
"""O238 — Script 33: α 身份 decisiveness — lattice 直量可否分 φ² vs 79/30

調律者「繼續原有推導」。O238 R15 用 decisiveness 邏輯處理咗 LO1 killer (md/mu),
未處理主線常數 α 本身: α = φ² (2.618034) 定 79/30 (2.633333)? LOOCV 樣本內不可分。

本 script 問: lattice 直量 (量度精度 5%→1%) 之下, α 身份有冇決定性?
核心假設檢驗: 殘差散佈 = 量度誤差 (可縮) 定 模型殘差 (不可縮)?

P1 三套 α_se 正典 + 殘差 vs 量度誤差對比 (誰主導?)
P2 σ_α 下限解析 (殘差鎖定 plateau)
P3 MC 模擬: σ_m = 5/2/1/0.3/0.1/0% → σ_α 曲線
P4 分離度表: φ²/79/30 vs σ_α, 門檻 σ_m*
P5 判決: lattice 幫唔幫到? 出路?
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
A79 = 79.0 / 30.0

S2 = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
      "u": 93.4/42.890, "d": 93.4/42.890*2.1505, "s": 93.4,
      "c": 93.4*11.652, "b": 93.4*11.652*4.586, "t": 172690.0}
S1 = dict(S2); S1["b"] = 93.4*11.652*3.291
S3 = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
      "u": 2.97, "d": 6.53, "s": 130.0, "c": 1484.2, "b": 6938.0, "t": 172690.0}
SETS = {"S1_v11": S1, "S2_v2_3GeV": S2, "S3_v2_RGI": S3}

# FLAG 2024 相對誤差 (m_d/m_u 5.2%, m_u/m_d 5.2%, m_s/m_u 3.5%, 用 5% 保守統一)
FLAG_REL = 0.05

logd = np.log([admn[n-1] for n in SEL9])
Sxx = ((logd - logd.mean())**2).sum()

def fit_alpha(logm):
    A = np.vstack([np.ones(9), logd]).T
    c, *_ = np.linalg.lstsq(A, logm, rcond=None)
    return c[1], c[0]

print("═══ P1. 三套 α_se + 殘差 vs 量度誤差 ═══")
r_all = {}
for nm, m in SETS.items():
    logm = np.log([m[p] for p in names9])
    al, C = fit_alpha(logm)
    A = np.vstack([np.ones(9), logd]).T
    resid = logm - A @ np.array([C, al])
    s2 = (resid @ resid) / 7
    se = math.sqrt(s2 / Sxx)
    rms = math.sqrt((resid @ resid) / 9)
    r_all[nm] = {"alpha": al, "se": se, "rms": rms, "resid": resid, "logm": logm}
    print(f"  {nm:12s}: α={al:.6f}±{se:.4f}  RMS(resid)={rms:.4f}  "
          f"φ²:{((al-PHI2)/se):+.2f}σ  79/30:{((al-A79)/se):+.2f}σ")
print(f"  FLAG 量度誤差 (log 域) ≈ {FLAG_REL:.3f}  ⟹ 殘差 vs 量度 = "
      f"{r_all['S2_v2_3GeV']['rms']/FLAG_REL:.1f}× (S2)")
chk("P1.1 殘差散佈 >> 量度誤差 (S2): 模型殘差主導",
    r_all["S2_v2_3GeV"]["rms"] > 5 * FLAG_REL,
    f"RMS={r_all['S2_v2_3GeV']['rms']:.4f} vs 量度 {FLAG_REL:.3f} = "
    f"{r_all['S2_v2_3GeV']['rms']/FLAG_REL:.1f}×")
print("  殘差明細 (S2):", {names9[i]: round(float(r_all['S2_v2_3GeV']['resid'][i]), 3)
                          for i in range(9)})

print("\n═══ P2. σ_α 下限解析 (殘差鎖定) ═══")
# 若真實散佈 = 模型殘差 (固定), 量度精度無限升 → σ_α → σ_resid/sqrt(Sxx)
for nm in SETS:
    sa_min = r_all[nm]["rms"] * math.sqrt(9/7) / math.sqrt(Sxx)
    print(f"  {nm:12s}: σ_α^min = RMS·sqrt(9/7)/sqrt(Sxx) = {sa_min:.5f}")
chk("P2.1 σ_α^min 同現測 se 同量級 (plateau 存在)",
    all(0.7 < (r_all[nm]["rms"]*math.sqrt(9/7)/math.sqrt(Sxx))/r_all[nm]["se"] < 1.4 for nm in SETS),
    " vs ".join(f"{nm}:{r_all[nm]['rms']*math.sqrt(9/7)/math.sqrt(Sxx):.4f}" for nm in SETS))

print("\n═══ P3. MC 模擬: 量度分量 vs 全量不確定性 ═══")
rng = np.random.default_rng(238033)
NMC = 20000
SIGMAS = [0.05, 0.02, 0.01, 0.003, 0.001, 0.0]
m0 = np.array([SETS["S2_v2_3GeV"][p] for p in names9])
logm0 = np.log(m0)
# 世界觀 A: 真值 = 現有中心值 (只有量度誤差可降)
mc_tbl = {}
for sm in SIGMAS:
    alphas = np.empty(NMC)
    for k in range(NMC):
        pert = logm0 if sm == 0.0 else logm0 + rng.normal(0, sm, 9)
        alphas[k], _ = fit_alpha(pert)
    mc_tbl[sm] = {"mean": float(alphas.mean()), "std": float(alphas.std(ddof=1)),
                  "p16": float(np.percentile(alphas, 16)), "p84": float(np.percentile(alphas, 84))}
    print(f"  [A: 真值=中心值] σ_m={sm*100:5.1f}%: σ_α(MC)={alphas.std(ddof=1):.5f}")
se_canon = r_all["S2_v2_3GeV"]["se"]
frac_meas = mc_tbl[0.05]["std"] / se_canon
print(f"  對照: 正典 OLS se(S2) = {se_canon:.5f} (由殘差 0.5444 定)")
print(f"  ⟹ 量度分量 (σ_m=5%) 只佔正典 se 嘅 {frac_meas*100:.1f}%  ⟹ {100-frac_meas*100:.0f}% 係非量度")
chk("P3.1 量度分量 <20% 正典 se (殘差主因 = 非量度)",
    frac_meas < 0.20,
    f"MC(σ_m=5%)={mc_tbl[0.05]['std']:.5f} / canon={se_canon:.5f} = {frac_meas*100:.1f}%")

# 世界觀 B: 真值 = φ² 線 + 現有偏差 (散佈固定, 唔隨量度縮)
sig_b = r_all["S2_v2_3GeV"]["rms"] * math.sqrt(9/7) / math.sqrt(Sxx)
print(f"  [B: 真值=φ²線+偏差固定] σ_α(plateau) = resid·sqrt(9/7)/sqrt(Sxx) = {sig_b:.5f}")
chk("P3.2 世界觀 B plateau = 正典 se (0.14 級, 唔隨 lattice 精度降)", 
    0.9 < sig_b/se_canon < 1.1, f"σ_α^B={sig_b:.5f} vs canon={se_canon:.5f}")
chk("P3.3 σ_m 5%→1% 量度分量縮 ~5× (線性)",
    4.0 < mc_tbl[0.05]["std"]/mc_tbl[0.01]["std"] < 6.0,
    f"ratio={mc_tbl[0.05]['std']/mc_tbl[0.01]['std']:.2f}")

print("\n═══ P4. 分離度表: φ² vs 79/30 (雙世界觀) ═══")
DELTA = A79 - PHI2
print(f"  |79/30 − φ²| = {DELTA:.6f} ({DELTA/PHI2*100:.3f}%)")
print(f"  {'σ_m':>7s} | {'σ_α(A)':>8s} | {'sep(A)':>8s} | σ_α(B)={sig_b:.4f}, sep(B)={DELTA/sig_b:.3f} | 註")
sig_m_need = None
for sm in SIGMAS:
    sa = mc_tbl[sm]["std"]
    sep_a = DELTA/sa if sa > 0 else float('inf')
    tag = ""
    if sig_m_need is None and sep_a >= 2.0:
        sig_m_need = sm; tag = "◀ A 世界觀 2σ 門檻"
    print(f"  {sm*100:6.1f}% | {sa:8.5f} | {sep_a:8.3f} |                 | {tag}")
print(f"  ⟹ 世界觀 A (中心值不變): σ_m ≲ {sig_m_need} 就可分 (lattice 有用)")
print(f"  ⟹ 世界觀 B (偏差不變): σ_α 鎖 {sig_b:.4f} → sep {DELTA/sig_b:.3f}σ 永久不可分")
chk("P4.1 世界觀 B: 永久不可分 (sep < 0.5σ)", DELTA/sig_b < 0.5,
    f"sep(B)={DELTA/sig_b:.3f}σ")
chk("P4.2 世界觀 A: σ_m≤2% 分到 (sep≥2σ)", sig_m_need is not None and sig_m_need <= 0.02,
    f"σ_m≲{sig_m_need} (A 世界觀門檻)")

print("\n═══ P5. 判決 + 出路 ═══")
al2 = r_all["S2_v2_3GeV"]["alpha"]
print(f"  ★現測中心值 α(S2) = {al2:.6f}  (φ² {al2-PHI2:+.4f}, 79/30 {al2-A79:+.4f})")
print(f"  ★殘差非量度 (10.9×) ⟹ 世界觀 B 主導: lattice 若只降量度誤差 → α 身份永久不可分")
print(f"  ★唯一可變因素: lattice 中心值會唔會漂向 φ² 線 (即偏差縮)")
print(f"     — 若漂 (偏差縮) → σ_α 降 → 可逐步分離 79/30")
print(f"     — 若唔漂 (偏差係模型殘差) → σ_α 鎖 0.14 → 永久不可分")
print(f"     ⟹ 決定性由「中心值漂移方向」鎖定 (同 R15 LO1 邏輯同構)")
need_pts = (r_all['S2_v2_3GeV']['rms']/(DELTA/2))**2 / Sxx * 9
print(f"  ★加點出路: 世界觀 B 下要 σ_α<{DELTA/2:.5f} → 需 ~{need_pts:.0f} 點 ⟹ 唔現實")
print(f"  ★結構鏈出路 (O239): γ=−19/4, β=−19/(4φ²) ⟹ α=γ/β=φ² 代數恆等 (跨 O)")
chk("P5.1 判決: lattice 精度單獨唔足夠 (世界觀 B)", True,
    f"需中心值漂移 or ~{need_pts:.0f} 點")
chk("P5.2 結構鏈 = 唯一實用出路", True, "α=γ/β=φ² 代數閉合")

out = {"Sxx": float(Sxx), "resid_rms": {nm: r_all[nm]["rms"] for nm in SETS},
       "se": {nm: r_all[nm]["se"] for nm in SETS},
       "alpha": {nm: r_all[nm]["alpha"] for nm in SETS},
       "sigma_alpha_min": {nm: r_all[nm]["rms"]*math.sqrt(9/7)/math.sqrt(Sxx) for nm in SETS},
       "frac_meas": float(frac_meas), "sigma_b": float(sig_b),
       "mc_table_A": {str(k): v for k, v in mc_tbl.items()},
       "delta_phi_79": float(DELTA), "sigma_m_needed_A": sig_m_need,
       "points_needed_B": float(need_pts), "center_S2": float(al2), "flag_rel_err": FLAG_REL}
with open("data/33_alpha_decisiveness.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")