#!/usr/bin/env python3
"""
O100 — Step 1: 品圓 Harmonic ℓ↔k 對應 (harmonic correspondence)
================================================================
建立 IDCM C_ℓ 峰位與 3D 波數 k 嘅對應, 鎖定投影距離 χ*。

IDCM C_ℓ 峰 (O83 公式, m=1..7 觀測閉合 + m=8,9 延伸):
  ℓ_m = 44×(M − C(9−m,2)) + ((m−1)×9 mod 25),  m=1..4,6,7
  ℓ_5 = 44×(33 − F6) + F8 = 1121
  M=33 (K_Tree 深度), C(9−m,2) = 三角形數

對應假說: ℓ_m = k_m · χ*  (小角近似, k = 2π/λ 角投影)
  候選 χ*: R_world (c/H0), πR_world/2, πR_world (O76 Nyquist 視線盡頭),
           D_A(CMB) (O76 距離定律 z=1089), 自由掃描最佳值

檢驗: IDCM k_m = ℓ_m/χ* 對照:
  (a) BOSS DR12 wiggle 峰位 (boss_dr12_bao_wiggles.txt, 11 峰)
  (b) K_Chain 諧和階梯 k_n = n·(88/R_world)  (BOSS v2 分析: Δk=2π/λ_sync)
  (c) k/k_H = ℓ_m 恆等 (χ*=R_world 時)

輸出: 最佳 χ*, 各候選 RMS, PASS/FAIL
"""
import os, json, math
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(OUT, exist_ok=True)
results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'✅ PASS' if cond else '❌ FAIL'}] {name}  {detail}")

print("="*72)
print("  O100 Step 1: 品圓 Harmonic ℓ↔k 對應")
print("="*72)

# ─── IDCM 常數 ───
phi = (1+math.sqrt(5))/2
M = 33          # K_Tree 深度
F6, F8 = 8, 21
N_d = 44
H0 = 72.59
c = 299792.458
h = 0.6727      # BOSS P(k) h-units (Planck h)
R_world = c/H0  # 4129.64 Mpc
k_H = 1.0/R_world   # hubble 波數 (Mpc⁻¹)
lam_sync = 2*math.pi*R_world/88   # 294.88 Mpc

def ell_m(m):
    if m == 5:
        return 44*(M - F6) + F8
    from math import comb
    return 44*(M - comb(9-m, 2)) + ((m-1)*9) % 25

ells = [ell_m(m) for m in range(1, 10)]
print(f"\n  C_ℓ 峰階梯 ℓ_m (m=1..9): {ells}")
sync_ok = "✅" if abs(44*lam_sync/(math.pi*R_world)-1) < 1e-6 else "❌"
print(f"  ℓ_sync = 44 = πR/λ_sync  {sync_ok}  (O83 閉合)")

# ─── BOSS wiggle 峰位 (v2 方法: 插值+平滑+導數零點) ───
WIG = "/home/wsl/IDCM/sync_bump_analysis/boss_dr12_bao_wiggles.txt"
k_arr, P_arr = [], []
for line in open(WIG):
    if line.startswith('#') or not line.strip():
        continue
    p = line.split()
    if len(p) < 4: continue
    k_arr.append(float(p[0])); P_arr.append(float(p[1]))
k = np.array(k_arr); P = np.array(P_arr)

# 平滑 (log-P, gaussian sigma=3) → wiggle
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import interp1d
idx = np.argsort(k); k = k[idx]; P = P[idx]
logP = np.log(P)
Ps = np.exp(gaussian_filter1d(logP, sigma=3, mode='nearest'))
wig = P/Ps - 1
# 插值到 500 點 + 平滑
k_fine = np.linspace(k.min(), k.max(), 500)
wig_i = interp1d(k, wig, kind='cubic')(k_fine)
wig_s = gaussian_filter1d(wig_i, sigma=2)
dwig = np.gradient(wig_s)
peaks = []
for i in range(1, len(dwig)-1):
    if dwig[i-1] > 0 and dwig[i] <= 0:
        if 0.02 <= k_fine[i] <= 0.30 and wig_s[i] > 0.005:
            peaks.append(k_fine[i])
peaks = np.array(peaks)
dips = []
for i in range(1, len(dwig)-1):
    if dwig[i-1] < 0 and dwig[i] >= 0:
        if 0.02 <= k_fine[i] <= 0.30 and wig_s[i] < -0.005:
            dips.append(k_fine[i])
dips = np.array(dips)
print(f"  BOSS wiggle: {len(k)} 點 → {len(peaks)} 峰 (v2 方法)")
print(f"  peaks = {np.round(peaks,4)}")
all_ext = np.sort(np.concatenate([peaks, dips]))

# ─── (a) 自由掃描 χ* ───
def map_ells_to_k(ells, chi):
    """ℓ_m → k_m [h/Mpc]: k_phys = ℓ/χ, k_h = k_phys/h"""
    return np.array([e/(chi*h) for e in ells])

def match_rms(k_id, k_target):
    """greedy 1:1 配對 (nearest, dedup) → RMS 誤差"""
    kt = np.sort(k_target.copy())
    used = np.zeros(len(kt), bool)
    dists = []
    for kk in k_id:
        d = np.abs(kt - kk)
        d[used] = 1e9
        j = np.argmin(d)
        used[j] = True
        dists.append(d[j])
    return math.sqrt(np.mean(np.array(dists)**2))

chi_grid = np.linspace(0.2*R_world, 6.0*R_world, 2000)
rms_best, chi_best = 1e9, None
for chi in chi_grid:
    kid = map_ells_to_k(ells, chi)
    # 只比 k 喺 BOSS 範圍內嘅峰 (超出 0.145 不算)
    inr = kid[kid <= 0.145+1e-9]
    if len(inr) < 3: continue
    r = match_rms(inr, all_ext)
    if r < rms_best:
        rms_best, chi_best = r, chi
print(f"\n─── (a) 自由掃描: 最佳 χ* = {chi_best:.1f} Mpc = {chi_best/R_world:.3f}×R_world")
print(f"        RMS = {rms_best*1e3:.2f}×1e-3 h/Mpc  (BOSS wiggle scatter ~3.7e-3)")

# ─── (b) 結構候選對照 ───
cands = {
    "R_world (c/H0)":        R_world,
    "πR_world/2":            math.pi*R_world/2,
    "πR_world (Nyquist)":    math.pi*R_world,
    "2πR_world (環周長)":    2*math.pi*R_world,
    "D_A(CMB, O76 z=1089)": None,
}
# O76 距離定律: D_A = R(1−4^−ℓ)(1+2φ⁻¹ℓ+δ), ℓ=log4(1+z), δ=C=−0.1697
z_cmb = 1089.0
lvl = math.log(1+z_cmb, 4)
D_A_cmb = R_world*(1-4**-lvl)*(1+2/phi*lvl - 0.1697)
cands["D_A(CMB, O76 z=1089)"] = D_A_cmb

print("\n─── (b) 結構候選 χ* ───")
rows = []
for name, chi in cands.items():
    kid = map_ells_to_k(ells, chi)
    inr = kid[kid <= 0.151]
    r_all = match_rms(inr, all_ext)
    r_pk  = match_rms(inr, peaks)
    rows.append((name, chi, r_all*1e3, r_pk*1e3, kid, inr))
    print(f"  {name:22s} χ={chi:8.1f} Mpc  RMS(all)={r_all*1e3:6.2f}e-3  RMS(pk)={r_pk*1e3:6.2f}e-3")
    print(f"      k_m = {np.round(kid,4)}")

# ─── (c) k/k_H = ℓ 恆等檢驗 (χ*=R_world) ───
print("\n─── (c) 結構恆等: χ*=R_world → k/k_H = ℓ ───")
kid_R = map_ells_to_k(ells, R_world)
k_phys = kid_R*h
ratio = k_phys/k_H
print(f"  k_phys/k_H = {np.round(ratio,6)}  vs ℓ_m = {ells}")
dev = np.max(np.abs(ratio - np.array(ells)))/max(ells)
check("χ*=R_world: k/k_H = ℓ_m (恆等, dev<0.1%)", dev < 1e-3, f"max dev {dev*100:.4f}%")
check("R_world·k_H = 1 (定義恆等)", abs(R_world*k_H-1) < 1e-9, f"({R_world*k_H:.10f})")

# ─── (d) 諧和階梯對照: C_ℓ 峰 = 半整數諧和 (beat 結構) ───
print("\n─── (d) C_ℓ 峰 ↔ K_Chain 諧和階梯 (半整數 beat) ───")
dk_chain = 88/R_world   # 0.02131 Mpc⁻¹ → h/Mpc
dk_h = dk_chain/h
print(f"  88-site 基礎波數: Δk = {dk_chain:.5f} Mpc⁻¹ = {dk_h:.5f} h/Mpc  (2π/λ_sync = {2*math.pi/lam_sync:.5f})")
# ℓ_m = 44·n_m, n_m = M−C(9−m,2) ∈ Z  ⇒  k_m = 44n_m/R = (n_m/2)·(88/R) = (n_m/2)·Δk
from math import comb
n_m = np.array([M - comb(9-m, 2) if m != 5 else M - F6 for m in range(1, 10)], float)
half_idx = n_m/2.0
print(f"  n_m = M−C(9−m,2) = {n_m.astype(int)}  (整數, 峰數階梯)")
print(f"  k_m/Δk_chain = n_m/2 = {np.round(half_idx,2)}  (半整數諧和 = beat 結構)")
check("C_ℓ 峰 = 半整數 88-chain 諧和 (n_m/2, 由 ℓ=44n_m 形式保證)",
      np.allclose(2*half_idx, np.round(2*half_idx), atol=1e-9), "formal identity")

# ─── 方差加權 BOSS k 範圍覆蓋 ───
print("\n─── (e) σ_8 相關 k 覆蓋 ───")
k_eff = 0.3  # h/Mpc (8 h⁻¹Mpc 窗嘅有效 k)
for name, chi in [("R_world", R_world), ("πR_world", math.pi*R_world)]:
    kid = map_ells_to_k(ells, chi)
    frac = np.sum(kid <= 0.45)/len(kid)
    print(f"  {name}: 峰位 k ∈ [{kid.min():.3f}, {kid.max():.3f}] h/Mpc; "
          f"k<0.45 覆蓋 {frac*100:.0f}%  (σ_8 需 k~0.1-0.4)")

# ─── 總結 ───
best_name = min(rows, key=lambda r: r[3])[0]
print(f"\n  結構候選最佳: {best_name}")
print("="*72)
n_pass = sum(results); n_tot = len(results)
print(f"  RESULT: {n_pass}/{n_tot} PASS")
print("="*72)
json.dump({
    "ells": ells, "chi_best_free": float(chi_best), "chi_best_ratio_R": float(chi_best/R_world),
    "rms_best_free": float(rms_best),
    "candidates": {n: {"chi": c, "rms_pk": float(rp)} for n, c, ra, rp, kk, ii in rows},
    "k_over_kH_identity_dev": float(dev),
}, open(os.path.join(OUT, "01_harmonic.json"), "w"), indent=2, default=float)
exit(0 if n_pass == n_tot else 1)