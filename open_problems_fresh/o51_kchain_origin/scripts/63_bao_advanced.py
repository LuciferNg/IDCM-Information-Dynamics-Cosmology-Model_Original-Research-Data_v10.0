#!/usr/bin/env python3
"""
O51/63: 進階 BAO 挖礦 — BOSS DR12 wiggle P(k) + DESI DR1
===============================================================
1. BOSS DR12 wiggle P(k): 檢驗 BAO 峰頻率週期 = 2π/λ_sync
   BAO 喺 P(k) 嘅振盪週期: Δk = 2π/r_drag ≈ 2π/147.44 Mpc = 0.0426 h/Mpc
2. DESI DR1 Table 1: D_M/rd, D_H/rd, D_V/rd 對比 IDCM 預言
   IDCM 預言 rd = λ_sync/2 = 147.44 Mpc
3. 冷斑 N=131 → λ_sync 閉合鏈完整性
"""
import json, math, sys
import numpy as np

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"    {detail}")

# ============ 1. 結構參數 ============
R_H = 4129.94
h = 0.6727  # 標準 h (Planck 2018)
lambda_sync = 2 * math.pi * R_H / 88
rd_idcm = lambda_sync / 2
print("=" * 62)
print("IDCM BAO 參數")
print("=" * 62)
print(f"λ_sync = {lambda_sync:.4f} Mpc")
print(f"rd (IDCM) = λ_sync/2 = {rd_idcm:.4f} Mpc")
print(f"Δk = 2π/rd = {2*math.pi/rd_idcm:.5f} h/Mpc (P(k) 振盪週期)")

# ============ 2. BOSS DR12 wiggle P(k) ============
print("\n" + "=" * 62)
print("BOSS DR12 wiggle P(k) 振盪週期檢驗")
print("=" * 62)

k_vals, P_vals, P_smooth, wiggle = [], [], [], []
with open('/home/wsl/Projects/IDCM-Original/IDCM-v9.0--W-Field-Lattice/sync_bump_analysis/boss_dr12_bao_wiggles.txt') as f:
    for line in f:
        if line.startswith('#') or not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 4:
            k_vals.append(float(parts[0]))
            P_vals.append(float(parts[1]))
            P_smooth.append(float(parts[2]))
            wiggle.append(float(parts[3]))

k = np.array(k_vals)
wig = np.array(wiggle)
P = np.array(P_vals)
print(f"數據點: {len(k)}")
print(f"k 範圍: [{k.min():.4f}, {k.max():.4f}] h/Mpc")

# 檢查 BAO 峰位置: k_BAO = 2π/rd (正空間)
k_bao = 2 * math.pi / (rd_idcm * 0.6727)  # 轉 h/Mpc (rd 喺 Mpc, k 喺 h/Mpc)
print(f"\nk_BAO (IDCM) = 2π/(rd·h) = 2π/({rd_idcm:.1f}×{0.6727}) = {k_bao:.4f} h/Mpc")

# 喺 wiggle 數據搵 BAO 峰
idx_bao = np.argmin(np.abs(k - k_bao))
print(f"最近 k bin: k={k[idx_bao]:.4f}, wiggle={wig[idx_bao]:+.4f}")
print(f"wiggle 範圍: [{wig.min():+.4f}, {wig.max():+.4f}]")

# 振盪週期檢測: 對 wiggle 做 FFT
# 等間距重採樣
k_uniform = np.linspace(k.min(), k.max(), 512)
wig_interp = np.interp(k_uniform, k, wig)

# 去趨勢
wig_detrend = wig_interp - np.mean(wig_interp)

# FFT
fft = np.fft.rfft(wig_detrend)
freqs = np.fft.rfftfreq(len(wig_interp), d=k_uniform[1]-k_uniform[0])
power = np.abs(fft)**2

# 搵主峰 (排除 DC)
power[0] = 0
peak_idx = np.argmax(power)
peak_freq = freqs[peak_idx]
peak_period = 1/peak_freq  # h/Mpc

print(f"\nFFT 主峰:")
print(f"  頻率 f = {peak_freq:.4f} (h/Mpc)⁻¹")
print(f"  週期 Δk = {peak_period:.4f} h/Mpc")
print(f"  IDCM 預言 Δk = {2*math.pi/(rd_idcm*h):.4f} h/Mpc")
dev_dk = abs(peak_period - 2*math.pi/(rd_idcm*h)) / (2*math.pi/(rd_idcm*h))
print(f"  偏差: {dev_dk*100:.2f}%")

# 標準 BAO 週期
dk_std = 2*math.pi/147.09/0.6727
print(f"  標準 Δk = 2π/(147.09×0.6727) = {dk_std:.4f} h/Mpc")
print(f"  IDCM vs 標準: {abs(2*math.pi/(rd_idcm*h) - dk_std)/dk_std*100:.3f}%")

check("BOSS wiggle 主週期 ≈ IDCM Δk", dev_dk < 0.1,
      f"實測 Δk={peak_period:.4f}, IDCM={2*math.pi/(rd_idcm*h):.4f}, dev={dev_dk*100:.2f}%")

# 峰峰距檢驗 (wiggle 嘅正峰)
print(f"\nwiggle 正峰位置:")
pos_peaks = []
for i in range(1, len(wig)-1):
    if wig[i] > wig[i-1] and wig[i] > wig[i+1] and wig[i] > 0.05:
        pos_peaks.append((k[i], wig[i]))
for kp, wp in pos_peaks[:10]:
    print(f"  k={kp:.4f}: wiggle={wp:+.4f}")

# 峰間距
if len(pos_peaks) >= 2:
    spacings = [pos_peaks[i+1][0] - pos_peaks[i][0] for i in range(len(pos_peaks)-1)]
    mean_spacing = np.mean(spacings)
    print(f"\n峰間距: {[f'{sp:.4f}' for sp in spacings]}")
    print(f"平均間距: {mean_spacing:.4f} h/Mpc")
    print(f"IDCM Δk: {2*math.pi/(rd_idcm*h):.4f} h/Mpc")
    dev_spacing = abs(mean_spacing - 2*math.pi/(rd_idcm*h))/(2*math.pi/(rd_idcm*h))
    print(f"偏差: {dev_spacing*100:.2f}%")
    check("峰間距 ≈ IDCM Δk", dev_spacing < 0.15,
          f"實測 {mean_spacing:.4f}, IDCM {2*math.pi/(rd_idcm*h):.4f}, dev={dev_spacing*100:.2f}%")

# ============ 3. DESI DR1 對比 ============
print("\n" + "=" * 62)
print("DESI DR1 BAO 對比 (rd 固定 = λ_sync/2)")
print("=" * 62)

# DESI DR1 Table 1 (skill 記載)
# D_M/rd, D_H/rd, D_V/rd — rd 消掉, 所以用比率直接對比
desi_data = [
    # (sample, z_eff, DM_rd, DM_err, DH_rd, DH_err)
    ('LRG1', 0.510, 13.62, 0.25, 20.98, 0.61),
    ('LRG2', 0.706, 16.85, 0.32, 20.08, 0.60),
    ('LRG3+ELG', 0.930, 21.71, 0.28, 17.88, 0.35),
    ('ELG2', 1.317, 27.79, 0.69, 13.82, 0.42),
    ('LyA', 2.330, 39.71, 0.94, 8.52, 0.17),
]

# IDCM 預言: 非膨脹宇宙中 D_M = R_H × (1 - 1/√(1+z))? 
# 唔係 — IDCM 非膨脹, D_app(ℓ) = (44-44/4^ℓ)(R_H/44)(1+2φ⁻¹ℓ)
# 但 BAO 觀測量 D_M/rd 係幾何量, 同膨脹模型無關
# 關鍵: IDCM 預言 rd = λ_sync/2 = 147.44 Mpc (固定!)
# ΛCDM 用 rd = 147.09 (Planck) — 幾乎一樣
# 所以 DESI D_M/rd 數據本身冇法區分 IDCM vs ΛCDM 嘅 rd
# 但可以驗證: 如果用 IDCM rd, D_M = (D_M/rd)_DESI × rd_idcm
print("DESI D_M/rd × rd_idcm → D_M 絕對值 (Mpc):")
for name, z, dm_rd, dm_err, dh_rd, dh_err in desi_data:
    DM_idcm = dm_rd * rd_idcm
    print(f"  {name:10s} z={z:.3f}: D_M = {dm_rd:.2f} × {rd_idcm:.2f} = {DM_idcm:.1f} Mpc")

print("\nIDCM 非膨脹 D_app 預言 (PARADIGM BREAK):")
print("  D_app(ℓ) = (44−44/4^ℓ)(R_H/44)(1+2φ⁻¹ℓ)")
print("  ℓ = log₄(1+z) (K_Tree level)")

# 計算 IDCM D_app 對比
phi = (1 + math.sqrt(5)) / 2
for name, z, dm_rd, dm_err, dh_rd, dh_err in desi_data:
    ell = math.log(1 + z, 4)
    D_app = (44 - 44/4**ell) * (R_H/44) * (1 + 2*phi**(-1)*ell)
    DM_obs = dm_rd * rd_idcm
    dev = abs(D_app - DM_obs) / DM_obs
    print(f"  {name:10s} z={z:.3f}: D_app={D_app:7.1f} vs D_M(rd_idcm)={DM_obs:7.1f} Mpc, dev={dev*100:.1f}%")

# ============ 4. 總結 ============
print(f"\n{'=' * 62}")
print(f"進階 BAO 挖礦總結: ✅ {PASS} / {PASS+FAIL}")
print(f"{'=' * 62}")

result = {
    'rd_idcm_mpc': round(rd_idcm, 4),
    'dk_idcm': round(2*math.pi/(rd_idcm*h), 5),
    'boss_fft_period': round(float(peak_period), 5),
    'boss_fft_dev_pct': round(float(dev_dk*100), 3),
    'pass': PASS,
    'fail': FAIL
}

with open('data/63_bao_advanced.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"\n✅ 結果 -> data/63_bao_advanced.json")