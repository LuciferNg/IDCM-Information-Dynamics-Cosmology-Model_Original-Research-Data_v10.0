#!/usr/bin/python3
"""O239 — Script 12: T3 冪律方案敏感度（用 freeze v1.1/v2 現有數據, 唔使等）
============================================================================
調律者質疑: 「點解一定要等 freeze v2, 而唔可以靠 freeze v1.1 或 PDG?」

事實核對:
  1. O206 MASS = PDG2024 = O234 freeze v1.0（同一批數字）⟹ T3 已經用緊 freeze v1
  2. freeze v2 已存在（O234 docs/03, FLAG 2024 RGI 已入層, 2026-10-06 凍結）
  3. 真正未做: scheme 統一 + 誤差傳播——唔係「等新數據」

本 script 用 freeze 層現有誤差做敏感度/穩健性檢定:
  S1 主檢定重現: O206 MASS 9 點 γ = slope(ln m, ln θ)（確認基線）
  S2 ★誤差傳播: 9 點質量各 ±1σ（FLAG2024/PDG 誤差, 由 freeze v1.0 攞）
     重算 γ —— γ 嘅 spread 係咪 << |γ|（結構穩）定 ~|γ|（數據敏感）?
  S3 ★freeze v2 RGI 方案: u/d/s 用 RGI 值（mu=2.97, md=6.53, ms=130, md/mu=2.1987）
     + PDG pole (c,b,t) + pole 輕子 —— 重算 γ, 同 O206 混合 scheme γ 比
  S4 判決: γ 穩定（方案間 dev < 10%）⟹ 現有 freeze v1.1/v2 已夠判斷 T3 冪律,
     「等 freeze v2 新量度」只係加緊誤差, 唔係結構必要;
     γ 漂移大 ⟹ scheme/數據選擇敏感 → O234「lattice 直量 1-2%」先有牙
"""
import json, math
import numpy as np
from scipy import stats

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/12 — T3 冪律方案敏感度（freeze v1.1/v2 現有數據）")
print("=" * 78)

# A5 模態 + θ
O9 = json.load(open("data/09_o206_inputs.json"))
PAIR = O9["PAIR"]  # [(1,'t'),(2,'b'),...]
MODES = [n for n, _ in PAIR]
theta = np.array([n*np.pi/88 for n in MODES])
lt = np.log(theta)

# freeze v1.0 誤差 (O234 data/01_frozen_observations.json: FLAG2024 + PDG2024)
# m: pdg 值、err: 相對誤差 (MeV 單位 -> 用 %)
MASS = np.array([172690.0, 4180.0, 1776.86, 1270.0, 105.6584, 93.4, 4.67, 2.16, 0.510999])
# PDG2024/FLAG: t=172.57±0.29 (0.17%), b=4.18±0.03 (0.7%), c=1.27±0.02 (1.6%),
#   s=93.4±1.0 (1.1%), d=4.67±0.48 (10%), u=2.16±0.49 (23%), e(精確), mu(精確), tau(精確)
REL_ERR = np.array([0.0017, 0.0072, 0.00023, 0.0157, 0.000034, 0.0107, 0.103, 0.227, 0.000012])
# 註: u/d 誤差巨大 (23%/10%)——FLAG mu_md 0.465±0.024 亦 ~5%
labels = [p for _, p in PAIR]

# ── S1: 基線 ──
r0 = stats.linregress(lt, np.log(MASS))
g0 = r0.slope
print("\n── S1: 基線 γ (O206/PDG 混合 scheme) ──")
print(f"   γ₀ = {g0:.4f} ± {r0.stderr:.4f}  R² = {r0.rvalue**2:.4f}")
chk("S1 基線重現 (γ ≈ −4.75)", abs(g0 + 4.75) < 0.5, f"γ₀={g0:.4f}")

# ── S2: 誤差傳播 (每次一個點 ±1σ, 其餘不變) ──
print("\n── S2: 9 點 ±1σ 誤差傳播 ──")
gs = []
for i in range(9):
    for sgn in (+1, -1):
        m2 = MASS.copy()
        m2[i] *= (1 + sgn * REL_ERR[i])
        r = stats.linregress(lt, np.log(m2))
        gs.append(r.slope)
    print(f"   {labels[i]:<3} ±1σ: γ ∈ [{min(gs[-2], gs[-1]):.3f}, {max(gs[-2], gs[-1]):.3f}]")
gs = np.array(gs)
print(f"   18 個變體 γ: 範圍 [{gs.min():.3f}, {gs.max():.3f}]  spread={gs.max()-gs.min():.3f}")
print(f"   相對 spread {abs(gs.max()-gs.min())/abs(g0)*100:.1f}%")
spread_rel = abs(gs.max()-gs.min())/abs(g0)
chk("S2 γ 誤差傳播 spread < 15% (結構穩, 唔係數據敏感)",
    spread_rel < 0.15, f"spread={spread_rel*100:.1f}%")
# 最大單點影響: u 或 d (誤差最大)
wi = np.argmax([abs(g0 - min(gs[2*i], gs[2*i+1])) for i in range(9)])
print(f"   最大單點影響: {labels[wi]} (誤差 {REL_ERR[wi]*100:.1f}%)")

# ── S3: freeze v2 RGI 方案 ──
print("\n── S3: freeze v2 RGI 方案 (u/d/s 用 RGI, 其餘 PDG) ──")
# RGI: mu=2.97, md=6.53 (M_RGI_u/d), ms=130.0 (RGI_ms)
MASS_RGI = MASS.copy()
i_u = labels.index('u'); i_d = labels.index('d'); i_s = labels.index('s')
MASS_RGI[i_u] = 2.97
MASS_RGI[i_d] = 6.53
MASS_RGI[i_s] = 130.0
r_rgi = stats.linregress(lt, np.log(MASS_RGI))
g_rgi = r_rgi.slope
print(f"   RGI u/d/s + PDG 其餘: γ = {g_rgi:.4f} ± {r_rgi.stderr:.4f}  R² = {r_rgi.rvalue**2:.4f}")
print(f"   vs 基線 γ₀ = {g0:.4f}: dev = {abs(g_rgi-g0)/abs(g0)*100:.1f}%")
chk("S3 RGI 方案 vs 基線 dev < 10% (scheme 選擇唔影響結構)",
    abs(g_rgi-g0)/abs(g0) < 0.10, f"dev={abs(g_rgi-g0)/abs(g0)*100:.1f}%")

# 额外: md/mu 用 freeze v2 derived 2.1987 vs PDG 2.16 嘅影響
print("\n── S3b: md/mu scheme 差異 (freeze v2 RGI 2.1987 vs PDG 2.16) ──")
# PDG: md=4.67, mu=2.16 → md/mu=2.162; RGI: 6.53/2.97=2.1987 (+1.7%)
print(f"   PDG md/mu={4.67/2.16:.4f}; RGI md/mu={6.53/2.97:.4f} (+{(6.53/2.97)/(4.67/2.16)-1:.2%})")
print(f"   ⟹ md/mu scheme 差異 1.7% ≪ u/d 單獨誤差 (10-23%)——S2 已覆蓋")

# ── S4: 判決 ──
print("\n── S4: 判決 ──")
s2ok = spread_rel < 0.15
s3ok = abs(g_rgi-g0)/abs(g0) < 0.10
if s2ok and s3ok:
    print("   ✅ γ 對數據誤差 (±1σ) 同 scheme 選擇 (RGI vs PDG) 都穩定:")
    print("   ⟹ 現有 freeze v1.1/v2 已夠判斷 T3 冪律穩定性——「等 freeze v2」唔係結構必要")
    print("   ⟹ β/γ/α 冪律係 freeze 現有數據嘅穩健結論; freeze v2 新量度只會加緊誤差")
else:
    print("   🔴 γ 對誤差/scheme 敏感:")
    print("   ⟹ O239 冪律依賴數據選擇; 「lattice 直量 1-2%」真係結構必要 (O234 立場成立)")

json.dump({
    "S1_gamma0": g0, "S1_R2": r0.rvalue**2,
    "S2_spread": float(gs.max()-gs.min()), "S2_spread_rel": float(spread_rel),
    "S2_worst": labels[wi],
    "S3_gamma_RGI": g_rgi, "S3_dev": float(abs(g_rgi-g0)/abs(g0)),
    "S4_verdict": "現有 freeze 夠判斷" if (s2ok and s3ok) else "需 freeze v2 新量度",
    "note": "O206 MASS = PDG2024 = freeze v1.0; freeze v2 (FLAG2024 RGI) 已存在",
}, open("data/12_scheme_robustness.json", "w"), indent=1, ensure_ascii=False)

n_pass = sum(1 for _, c_ in P if c_)
print(f"\nRESULT: {n_pass}/{len(P)} checks passed")