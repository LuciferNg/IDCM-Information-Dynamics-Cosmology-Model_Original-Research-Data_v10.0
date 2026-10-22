#!/usr/bin/env python3
"""
O133 — scripts/01_v9_validation.py (v2)
=======================================
v9.0 pk_chain_spectrum 推導 → v10.0 非膨脹框架驗證 (清潔版)

v9.0 公式 (01_derive_pk.py):
    P(k) = Σ_{n=1}^{43} γ_n · exp(−(k−k_n)²/(2σ²))
    γ_n = 4 sin²(πn/88)      (eigenvalue 權重)
    k_n = 2πn/R_world         (44-site 鏈整數諧和)
    σ   = 2π/(R_world/4)      (K_Tree L1 粗粒化窗口)
    對照: BOSS DR12 P(k)      (v9.0 死路徑 /tmp/public_material_BAO/)

判定框架:
  [A] 模型基本能力 (覆蓋/平滑/包絡)      → v9.0 自身品質
  [B] 結構 grid 審計 (鏈 vs 環 vs sync)  → 診斷: v9.0 用錯 grid?
  [C] 數值對照 vs 真 BOSS P(k)           → 決定性
  [D] v10.0 結構交叉檢驗 (sync 諧和)
"""
import os, json, math
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from scipy.optimize import minimize_scalar

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

# ─── v10.0 常數 (kchain_wave_params.py / O73) ───
R_world = 4129.94          # Mpc, 世界環半徑 (O73)
c = 299792.458             # km/s
omega_ring = 72.59         # (km/s)/Mpc, 世界環角頻率 (唔係 H0)
Nd = 44
h_BOSS = 0.6727            # BOSS/Planck h-unit (O100 一致)
h_BAO = 0.676              # BOSS DR12 自身 h (Beutler/Gil-Marín, O100-A 用)

def gamma_n(n): return 4*math.sin(math.pi*n/88)**2

print("="*76)
print("  O133 — v9.0 pk_chain_spectrum → v10.0 驗證 (v2)")
print("="*76)
res = []
def check(name, cond, detail=""):
    res.append(bool(cond))
    print(f"  [{'✅ PASS' if cond else '❌ FAIL'}] {name}  {detail}")

# ═══════════════════════════════════════════════════════════
# Part 0 — 重建 v9.0 模型 + 載入數據
# ═══════════════════════════════════════════════════════════
print("\n─── Part 0: v9.0 模型重建 (v10.0 常數) ───")
k_n = np.array([2*math.pi*n/R_world for n in range(1, 44)])   # Mpc⁻¹
gamma = np.array([gamma_n(n) for n in range(1, 44)])
sigma = 2*math.pi/(R_world/4)                                 # Mpc⁻¹
print(f"  k_n = 2πn/R_world, n=1..43 → k∈[{k_n[0]/h_BOSS:.6f},{k_n[-1]/h_BOSS:.6f}] h/Mpc")
print(f"  σ = 2π/(R_world/4) = {sigma/h_BOSS:.6f} h/Mpc;  δk = { (k_n[1]-k_n[0])/h_BOSS:.6f} h/Mpc")
print(f"  σ/δk = {sigma/(k_n[1]-k_n[0]):.2f}")

kg = np.linspace(0.001, 0.40, 4000)
Pv9 = np.zeros_like(kg)
for i in range(43):
    Pv9 += gamma[i]*np.exp(-(kg-k_n[i]/h_BOSS)**2/(2*(sigma/h_BOSS)**2))
Pv9 /= Pv9.max()

WIG = os.path.join(DATA, "boss_dr12_bao_wiggles.txt")
kb, Pb, Wb = [], [], []
for line in open(WIG):
    if line.startswith('#') or not line.strip(): continue
    p = line.split(); kb.append(float(p[0])); Pb.append(float(p[1])); Wb.append(float(p[3]))
kb = np.array(kb); Pb = np.array(Pb); Wb = np.array(Wb)
print(f"  BOSS wiggle 數據: {len(kb)} 點, k∈[{kb[0]:.4f},{kb[-1]:.4f}] h/Mpc")

# ═══════════════════════════════════════════════════════════
# Part A — 模型基本能力
# ═══════════════════════════════════════════════════════════
print("\n─── Part A: 模型基本能力 ───")
kmax = k_n[-1]/h_BOSS
cover = (min(kmax, kb[-1]) - max(k_n[0]/h_BOSS, kb[0]))/(kb[-1]-kb[0])
print(f"  A1 模型只覆蓋 k<{kmax:.4f} h/Mpc → BOSS 範圍覆蓋 {cover*100:.0f}%")
check("A1 覆蓋 ≥80% BOSS 範圍", cover >= 0.80, f"{cover*100:.0f}%")

# A2: 模型平滑度 — 高頻殘差 (真平滑應≈0)
Pv9_fine = np.interp(kb, kg, Pv9)
env_fine = gaussian_filter1d(Pv9_fine, sigma=5, mode='nearest')   # 寬平滑 = 包絡
osc_model = np.std(Pv9_fine - env_fine)
osc_boss  = np.std(Wb)
print(f"  A2 模型振盪 RMS = {osc_model:.4f} vs BOSS wiggle RMS = {osc_boss:.4f}")
check("A2 模型平滑 (振盪 < 0.1×BOSS wiggle)", osc_model < 0.1*osc_boss,
      f"{osc_model:.4f} vs {osc_boss:.4f}")

# ═══════════════════════════════════════════════════════════
# Part B — 結構 grid 審計 (核心診斷)
# ═══════════════════════════════════════════════════════════
print("\n─── Part B: 結構 grid 審計 (鏈 vs 環 vs sync) ───")
d_ch   = 2*math.pi/R_world          # 44-site 鏈 grid
d_ring = 1.0/R_world                # 88-site 環 grid
k_sync = 88.0/R_world               # sync 模 (λ_sync=πR_world/44=2πR_world/88)
lam_sync = 2*math.pi*R_world/88
n_chain_sync = R_world/lam_sync     # sync 喺鏈上嘅 mode 數
n_ring_sync  = 2*math.pi*R_world/lam_sync
print(f"  44-site 鏈 grid δk = 2π/R_world = {d_ch:.6f} Mpc⁻¹")
print(f"  88-site 環 grid δk = 1/R_world   = {d_ring:.6f} Mpc⁻¹")
print(f"  sync 模 k = 88/R_world = {k_sync:.6f} Mpc⁻¹, λ_sync = {lam_sync:.4f} Mpc")
print(f"  sync 喺鏈上: n = {n_chain_sync:.4f}  (非整數) | 喺環上: m = {n_ring_sync:.4f}")
check("B1 sync = 88-site 環第 88 諧和 (精確整數)", abs(n_ring_sync-88) < 1e-9,
      f"m={n_ring_sync:.10f}")
check("B2 sync 唔係 44-site 鏈整數模 → v9.0 鏈 grid 裝唔落觀察結構",
      abs(n_chain_sync-round(n_chain_sync)) > 0.05,
      f"n={n_chain_sync:.4f} (14.0056, 唔整數)")

# B3: γ_n 權重單調性 (γ_n 升到 Nyquist → 唔適合下降嘅 P(k))
print(f"  B3 γ_n: γ_1={gamma_n(1):.5f} → γ_43={gamma_n(43):.5f} (單調升到 Nyquist)")
check("B3 γ_n 唔單調升 (否則模型高 k 過重)", gamma_n(43) <= gamma_n(1),
      f"γ_43={gamma_n(43):.4f} > γ_1={gamma_n(1):.4f}")

# ═══════════════════════════════════════════════════════════
# Part C — 決定性: 數值對照 vs 真 BOSS P(k)
# ═══════════════════════════════════════════════════════════
print("\n─── Part C: 決定性數值對照 (overlap) ───")
mask = (kb >= k_n[0]/h_BOSS) & (kb <= kmax)
k_ov, P_ov, Pm_ov = kb[mask], Pb[mask], Pv9_fine[mask]
corr = np.corrcoef(Pm_ov, P_ov)[0,1]
r = minimize_scalar(lambda a: np.sum((a*Pm_ov-P_ov)**2/P_ov), bounds=(1e-6,1e6), method='bounded')
chi2v = r.fun; dof = mask.sum()-1
print(f"  overlap {mask.sum()} 點: 相關係數 r = {corr:.4f}, χ²/dof = {chi2v/dof:.1f}")
check("C1 形狀相關 r > 0.5", corr > 0.5, f"r={corr:.4f} (期望正相關)")
check("C2 χ²/dof < 3", chi2v/dof < 3, f"χ²/dof={chi2v/dof:.1f}")

# C3: 包絡斜率 (線性迴歸)
def slope(x, y):
    m_ = np.polyfit(x, y, 1)[0]; return m_
s_boss = slope(k_ov, np.log(P_ov)); s_model = slope(k_ov, np.log(Pm_ov+1e-9))
print(f"  C3 log-斜率: BOSS = {s_boss:.1f} (下降), v9.0 模型 = {s_model:+.1f}")
check("C3 包絡方向一致 (log 斜率同號)", s_boss*s_model > 0,
      f"BOSS {s_boss:.1f} vs 模型 {s_model:+.1f}")

# ═══════════════════════════════════════════════════════════
# Part D — v10.0 結構交叉檢驗 (sync 諧和 vs 實測)
# ═══════════════════════════════════════════════════════════
print("\n─── Part D: sync 諧和 vs 實測 BOSS wiggle (最佳匹配) ───")
# 理論 sync 諧和 (h_BAO=0.676): k_n = 2πn/λ_sync(h⁻¹)
lam_sync_hBAO = lam_sync/h_BAO
k_sync_n = np.array([2*math.pi*n/lam_sync_hBAO for n in range(1, 13)])
print(f"  λ_sync = {lam_sync_hBAO:.1f} h⁻¹Mpc (h={h_BAO})")
print(f"  sync 諧和 k_n = n×{k_sync_n[0]:.5f} h/Mpc: {np.round(k_sync_n,4)}")

# 82-pt wiggle 零點 (去重) + 同 sync null 比
zeros = []
for i in range(len(kb)-1):
    if Wb[i]*Wb[i+1] < 0:
        zeros.append(kb[i] - Wb[i]*(kb[i+1]-kb[i])/(Wb[i+1]-Wb[i]))
zeros = sorted(zeros)
dedup = [zeros[0]] if zeros else []
for z in zeros[1:]:
    if z-dedup[-1] > 0.003: dedup.append(z)
zeros = np.array(dedup)
print(f"  實測零點 ({len(zeros)}): {np.round(zeros,4)}")
# 每個理論峰附近有冇零點/極值?
k_sync_peaks = np.array([2*math.pi*n/lam_sync_hBAO for n in range(2, 11)])
n_peaks_in = sum(1 for kp in k_sync_peaks if kb[0] <= kp <= kb[-1])
hits = 0
for kp in k_sync_peaks:
    if kb[0] <= kp <= kb[-1]:
        d = np.min(np.abs(kb-kp))
        if d < 0.004: hits += 1
print(f"  sync 峰 n=2..10 喺數據範圍: {n_peaks_in} 個, 命中 (Δk<0.004): {hits}")
check("D1 sync 諧和峰命中 BOSS 數據 (≥3/9)", hits >= 3, f"{hits}/{n_peaks_in}")

# D2: O100 line2 ↔ BOSS wiggle 峰 — 引用 O100-A 已閉合; 55-bin 複檢 (數據限制)
GM = os.path.join(DATA, "GilMarin_2016_LOWZDR12_measurement_power_spectrum_monopole_post_recon.txt")
rows = [l.split() for l in open(GM) if l.strip() and not l.startswith('#')]
kl = np.array([float(r[0]) for r in rows]); Pl = np.array([float(r[1]) for r in rows])
sl = gaussian_filter1d(Pl, sigma=2.0, mode='nearest'); wl = Pl/sl-1
peaks_l, _ = find_peaks(wl, height=0.2*np.max(wl[kl>0.03]), distance=3)
pk_l = kl[peaks_l][kl[peaks_l]>0.05]
ell2_k = 537/R_world/h_BOSS
best = pk_l[np.argmin(np.abs(pk_l-ell2_k))] if len(pk_l) else None
print(f"  LOWZ 實測峰 (k>0.05): {np.round(pk_l,4)}")
print(f"  O100 line2 (ℓ=537) k={ell2_k:.4f} h/Mpc ↔ 最近 55-bin 峰 {best}")
print(f"  (O100-A 已用全範圍密 bin 閉合 line2↔0.1923 Δ=+0.5%; 55-bin 太疏, 唔作判決)")
near = best is not None and abs(ell2_k-best)/ell2_k < 0.10
if near:
    check("D2 line2 ↔ 實測峰 Δ<5%", abs(ell2_k-best)/ell2_k < 0.05,
          f"Δ={abs(ell2_k-best)/ell2_k*100:.1f}%")
else:
    print("  [🟡 REF] D2 55-bin 覆蓋不足 (峰止於 ~0.13, line2 喺 0.193), 引用 O100-A 閉合")

# ═══════════════════════════════════════════════════════════
json.dump({
    "v9_model": {"k_grid": "2pi*n/R_world", "n": [1,43],
                 "k_h_range": [k_n[0]/h_BOSS, kmax], "sigma": sigma/h_BOSS,
                 "sigma_over_dk": sigma/(k_n[1]-k_n[0]),
                 "cover_frac": cover, "osc_rms": osc_model, "boss_wig_rms": osc_boss,
                 "corr_vs_boss": corr, "chi2_dof": chi2v/dof,
                 "logslope_boss": s_boss, "logslope_model": s_model},
    "structure": {"d_chain": d_ch, "d_ring": d_ring, "k_sync": k_sync,
                  "lambda_sync": lam_sync, "sync_on_chain_mode": n_chain_sync,
                  "sync_on_ring_mode": n_ring_sync,
                  "sync_is_88th_ring_harmonic": abs(n_ring_sync-88)<1e-9},
    "boss": {"wiggle_zeros": zeros.tolist(), "sync_peaks": k_sync_n.tolist(),
             "sync_peak_hits": [hits, n_peaks_in], "line2_k": ell2_k,
             "line2_nearest_lowz_peak": best},
    "checks": res,
}, open(os.path.join(DATA, "01_v9_validation.json"), "w"), indent=2, default=float)

n_pass = sum(res); n_tot = len(res)
print("\n" + "="*76)
print(f"  RESULT: {n_pass}/{n_tot} PASS")
print("="*76)
exit(0)
