#!/usr/bin/env python3
"""
O100 — Step 3: BOSS DR12 P(k) 正則 + σ_8 閉合檢驗
==================================================
用 Step 2 嘅 P_3D(k) 線譜 (IDCM 首推, 零參數):

  1. σ_8² = Σ_m Δ²(k_m)·W²_R(k_m)     (R = 8 h⁻¹Mpc top-hat)
  2. 正則: 線譜 → Gaussian 平滑 → 對照 BOSS P(k) 形狀
  3. 對照: BOSS DR12 積分 σ8(z_eff)=0.783 (O99/13) ; 目標 0.81±0.05
  4. 可證偽預言判定: 🟢 閉合 / 🟡 半閉合 / 🔴 脫靶

窗函數:
  W_R(x) = 3(sin x − x cos x)/x³,  x = k·R
  σ_8² = ∫₀^∞ (dk/k)·Δ²(k)·W²_R(k)  → 離散線譜: Σ_m Δ²_m·W²(x_m)
"""
import os, json, math
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'✅ PASS' if cond else '❌ FAIL'}] {name}  {detail}")

print("="*72)
print("  O100 Step 3: σ_8 閉合檢驗 (BOSS 正則)")
print("="*72)

# ─── 載入 Step 2 產物 ───
d2 = json.load(open(os.path.join(OUT, "02_inverse_abel.json")))
ells = np.array(d2["ell"]); Delta2 = np.array(d2["Delta2"])
k_h  = np.array(d2["k_h"])           # h/Mpc
k_M  = np.array(d2["k_Mpc"])         # Mpc⁻¹

# ─── 1. σ_8 (χ*=R_world 主線) ───
def top_hat(x):
    x = np.asarray(x, float)
    return 3*(np.sin(x)-x*np.cos(x))/x**3

R8 = 8.0                              # h⁻¹Mpc
h = 0.6727                            # BOSS h-units
x_m = k_h * R8                        # 無量綱 kR
W2 = top_hat(x_m)**2
sigma8_sq = np.sum(Delta2 * W2)
sigma8 = math.sqrt(sigma8_sq)
sigma8_idcm = round(sigma8, 4)
print(f"\n─── 1. IDCM σ_8 (χ*=R_world, k/k_H=ℓ 恆等) ───")
print(f"  x_m = kR      = {np.round(x_m,3)}")
print(f"  W²(x_m)       = {np.round(W2,4)}")
print(f"  σ_8² = Σ Δ²W² = {sigma8_sq:.5f}")
print(f"  σ_8^IDCM      = {sigma8_idcm}")

# 主貢獻峰
contrib = Delta2*W2
order = np.argsort(-contrib)
print(f"  主貢獻: m = {order[:3]+1} (ℓ={np.round(ells)[order[:3]].astype(int)}, "
      f"佔比 {100*contrib[order[:3]].sum()/contrib.sum():.1f}%)")

# ─── 對照目標 ───
OBS_BOSS = 0.783     # O99/13: BOSS DR12 P(k) top-hat 積分 (z_eff)
OBS_PLAN = 0.81      # 目標 (Planck 相容)
dev_boss = (sigma8 - OBS_BOSS)/OBS_BOSS*100
dev_plan = (sigma8 - OBS_PLAN)/OBS_PLAN*100
print(f"\n  σ_8^ID = {sigma8:.3f}  vs  BOSS {OBS_BOSS} (Δ {dev_boss:+.1f}%)  vs  目標 {OBS_PLAN}±0.05 (Δ {dev_plan:+.1f}%)")
check(f"σ_8 同量級 (σ8^ID ∈ [0.3, 1.5])", 0.3 <= sigma8 <= 1.5, f"({sigma8:.3f})")
check(f"σ_8 閉合至 BOSS ±20%", abs(dev_boss) < 20, f"({dev_boss:+.1f}%)")
check(f"σ_8 閉合至目標 0.81±0.05 (可證偽預言)", 0.76 <= sigma8 <= 0.86, f"({sigma8:.3f})")

# ─── 2. 正則: 線譜 → 平滑 P(k) ───
print("\n─── 2. 正則化: IDCM 線譜 → 平滑 P(k) vs BOSS ───")
WIG = "/home/wsl/IDCM/sync_bump_analysis/boss_dr12_bao_wiggles.txt"
kb, Pb, Psb = [], [], []
for line in open(WIG):
    if line.startswith('#') or not line.strip(): continue
    p = line.split()
    if len(p) < 4: continue
    kb.append(float(p[0])); Pb.append(float(p[1])); Psb.append(float(p[2]))
kb = np.array(kb); Pb = np.array(Pb); Psb = np.array(Psb)

P_m = np.array(d2["P_Mpc3"])          # Mpc³ (k 物理)
# IDCM P(k) 轉 h-units: P[h⁻³Mpc³] = P[Mpc³]/h³
P_m_h = P_m/h**3
# Gaussian 平滑 (σ_k = 0.02 h/Mpc) — 未歸一化卷積, 質量守恆 (總積分 = Σ 線)
sigma_k = 0.02
Kdiff = (kb.reshape(-1,1) - k_h.reshape(1,-1))/sigma_k          # (Nboss, Nlines)
Wg = np.exp(-0.5*Kdiff**2)
P_smooth = np.sum(P_m_h.reshape(1,-1)*Wg, axis=1)
norm = Wg.sum(axis=1)

# 形狀對照: 只比同 k 範圍 (BOSS k ∈ [0.016, 0.145])
mask = (kb >= 0.016) & (kb <= 0.145) & (norm > 1e-3)
if mask.sum() > 10:
    ratio = P_smooth[mask]/Psb[mask]
    med_r = np.median(ratio)
    print(f"  P_IDCM/P_BOSSsmooth 中位數 = {med_r:.3f}  (σ = {ratio.std():.3f})")
    check("正則 P(k) 形狀同量級 (中位比 ∈ [0.3, 3])", 0.3 <= med_r <= 3.0, f"({med_r:.3f})")

# ─── 3. 敏感度報告 (χ 變體 + 峰數) ───
print("\n─── 3. 敏感度 ───")
for chi_name, fact in [("R_world", 1.0), ("πR_world", math.pi)]:
    x2 = k_h*fact*R8
    s8 = math.sqrt(np.sum(Delta2*top_hat(x2)**2))
    print(f"  χ*={chi_name:10s}: σ_8 = {s8:.3f}")
# 峰數敏感度 (去掉 m=8,9)
s8_7 = math.sqrt(np.sum(Delta2[:7]*W2[:7]))
print(f"  只用 m=1..7   : σ_8 = {s8_7:.3f}")

# 判定
if 0.76 <= sigma8 <= 0.86:
    verdict = "🟢 閉合"
elif 0.3 <= sigma8 <= 1.5:
    verdict = "🟡 半閉合 (同量級, 具體缺口標記)"
else:
    verdict = "🔴 脫靶"
print(f"\n  ★ 判定: {verdict}")

json.dump({
    "sigma8_idcm": sigma8, "sigma8_boss": OBS_BOSS, "sigma8_target": OBS_PLAN,
    "dev_boss_pct": dev_boss, "dev_target_pct": dev_plan,
    "per_peak": {"ell": ells.tolist(), "Delta2": Delta2.tolist(),
                 "W2": W2.tolist(), "contrib": contrib.tolist()},
    "sensitivity": {"chi_R": sigma8, "chi_piR": float(math.sqrt(np.sum(Delta2*top_hat(k_h*math.pi*R8)**2))),
                    "m1_7": s8_7},
    "verdict": verdict,
}, open(os.path.join(OUT, "03_sigma8.json"), "w"), indent=2)

n_pass = sum(results); n_tot = len(results)
print("="*72)
print(f"  RESULT: {n_pass}/{n_tot} PASS")
print("="*72)
exit(0 if n_pass == n_tot else 1)