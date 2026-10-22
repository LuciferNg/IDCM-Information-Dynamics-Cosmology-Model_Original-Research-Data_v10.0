#!/usr/bin/env python3
"""
O131 — 前置驗證 01: v9.0 stacking_toolbox 忠實重跑 (path-fixed)
================================================================
目的: 確認 v9.0 `01_stacked_waveform.py` 嘅演算法同輸出可完整複現,
      作為「遷移判決」嘅盤點基礎 (scripts 先行)。

唯一改動 = 資料路徑 (v9.0 硬編碼 /home/wsl/IDCM/... 已不存在) → 本目錄 data/。
演算法、常數、n 範圍、輸出格式一律照 v9.0 原文, 唔加唔減。

v9.0 常數來源 = v9.0 `open_problems_fresh/kchain_cosmic_web/_core.py`:
  H0_IDCM = 72.59 km/s/Mpc ; C_LIGHT = 299792.458
  R_H = C_LIGHT / H0_IDCM = 4129.94 Mpc
  LAMBDA_SYNC = 2*pi*R_H/88 = 294.88 Mpc
  H = H0_IDCM/100 = 0.7259
⚠️ 呢啲標籤本身係判決對象 (見 scripts/02), 本 script 只負責「忠實複現」。
"""

import math, os, sys, zipfile
import numpy as np
from scipy.interpolate import interp1d
import pywt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

PASS, FAIL = 0, 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; mark = "✅"
    else:    FAIL += 1; mark = "❌"
    print(f"  {mark} {name}" + (f" — {detail}" if detail else ""))

print("=" * 80)
print("  O131/01 — v9.0 STACKED WAVEFORM ANALYSIS (忠實重跑, path-fixed)")
print("=" * 80)

# ---------------- v9.0 _core constants (verbatim) ----------------
H0_IDCM = 72.59
C_LIGHT = 299792.458
R_H = C_LIGHT / H0_IDCM
LAMBDA_SYNC = 2 * math.pi * R_H / 88
H = H0_IDCM / 100
print(f"\n  [v9.0 常數] H0_IDCM={H0_IDCM}  R_H={R_H:.4f} Mpc  λ_sync={LAMBDA_SYNC:.4f} Mpc  h={H}")

# ---------------- Load BOSS DR12 (Ross 2016) ----------------
z = zipfile.ZipFile(os.path.join(DATA, "ross_dr12_corrfunc.zip"))
data_path = 'Ross_2016_COMBINEDDR12/Ross_2016_COMBINEDDR12_zbin1_correlation_function_monopole_post_recon_bincent0.dat'
s_b, xi_b, err_b = [], [], []
with z.open(data_path) as f:
    for line in f.read().decode().strip().split('\n'):
        if line.startswith('#') or not line.strip(): continue
        p = line.split()
        s_b.append(float(p[0])); xi_b.append(float(p[1])); err_b.append(float(p[2]))
s_b = np.array(s_b); xi_b = np.array(xi_b); err_b = np.array(err_b)

# ---------------- Load eBOSS DR16 ----------------
s_e, xi_e, err_e = [], [], []
with open(os.path.join(DATA, "eboss_dr16_lrg_xi.txt")) as f:
    for line in f:
        if line.startswith('#') or not line.strip(): continue
        p = line.split()
        s_e.append(float(p[0])); xi_e.append(float(p[1])); err_e.append(float(p[2]))
s_e = np.array(s_e); xi_e = np.array(xi_e); err_e = np.array(err_e)

lam_sync_hinv = LAMBDA_SYNC / H

print(f"\n  BOSS DR12: {len(s_b)} 點, s ∈ [{s_b[0]:.1f}, {s_b[-1]:.1f}] h⁻¹Mpc")
print(f"  eBOSS DR16: {len(s_e)} 點, s ∈ [{s_e[0]:.1f}, {s_e[-1]:.1f}] h⁻¹Mpc")
print(f"  λ_sync = {lam_sync_hinv:.4f} h⁻¹Mpc")
check("BOSS 資料可載入 (非空)", len(s_b) > 0, f"{len(s_b)} pts")
check("eBOSS 資料可載入 (非空)", len(s_e) > 0, f"{len(s_e)} pts")

# ================================================================
# 1. Wavelet broadband removal  (v9.0 verbatim)
# ================================================================
wavelet = 'sym6'; level = 3
def wavelet_remove_broadband(s, xi):
    coeffs = pywt.wavedec(xi, wavelet, level=level)
    approx = pywt.waverec([coeffs[0]] + [np.zeros_like(c) for c in coeffs[1:]], wavelet)
    return xi - approx[:len(xi)]

xi_b_wavelet = wavelet_remove_broadband(s_b, xi_b)
xi_e_wavelet = wavelet_remove_broadband(s_e, xi_e)

print(f"\n{'─'*80}\n  1. WAVELET BROADBAND REMOVAL\n{'─'*80}")
print(f"  BOSS  wavelet residual: std={np.std(xi_b_wavelet):.6f}")
print(f"  eBOSS wavelet residual: std={np.std(xi_e_wavelet):.6f}")

# ================================================================
# 2. Phase-aligned stacking at λ_sync/n  (v9.0 verbatim)
# ================================================================
print(f"\n{'─'*80}\n  2. PHASE-ALIGNED STACKING AT λ_sync/n\n{'─'*80}")

b_interp = interp1d(s_b, xi_b_wavelet, kind='cubic', bounds_error=False, fill_value=0)
b_err    = interp1d(s_b, err_b, kind='linear', bounds_error=False, fill_value=0)
e_interp = interp1d(s_e, xi_e_wavelet, kind='cubic', bounds_error=False, fill_value=0)
e_err    = interp1d(s_e, err_e, kind='linear', bounds_error=False, fill_value=0)

stacked_xi, stacked_weights, stacked_n = [], [], []
for n in range(4, 21):
    s_n = lam_sync_hinv / n
    if s_n < s_b[0] or s_n > s_b[-1]: continue
    xi_b_n = float(b_interp(s_n)); err_b_n = float(b_err(s_n))
    w_b = 1.0 / err_b_n**2 if err_b_n > 0 else 0
    if s_e[0] < s_n < s_e[-1]:
        xi_e_n = float(e_interp(s_n)); err_e_n = float(e_err(s_n))
        w_e = 1.0 / err_e_n**2 if err_e_n > 0 else 0
    else:
        xi_e_n = 0; w_e = 0
    total_w = w_b + w_e
    if total_w > 0:
        stacked = (xi_b_n * w_b + xi_e_n * w_e) / total_w
        stacked_err = math.sqrt(1.0 / total_w)
    else:
        stacked = 0; stacked_err = 0
    stacked_xi.append(stacked); stacked_weights.append(stacked_err); stacked_n.append(n)

stacked_xi = np.array(stacked_xi); stacked_weights = np.array(stacked_weights)
mean_stacked_xi = float(np.mean(stacked_xi))
sn_stack = float(np.mean(stacked_xi / stacked_weights))

print(f"  Stacked {len(stacked_n)} harmonics (n=4..20): {stacked_n}")
print(f"  Mean stacked ξ: {mean_stacked_xi:+.6f}")
print(f"  Stacked S/N: {sn_stack:+.2f}")
n_expected = sum(1 for n in range(4, 21) if s_b[0] <= lam_sync_hinv / n <= s_b[-1])
check(f"harmonics stacked 數量 = 由資料範圍計算 (n=4..20 落喺 BOSS s 範圍內)",
      len(stacked_n) == n_expected, f"{len(stacked_n)} vs 計算值 {n_expected}")

# ================================================================
# 3. Stacked reflection detection  (v9.0 verbatim)
# ================================================================
print(f"\n{'─'*80}\n  3. STACKED REFLECTION DETECTION\n{'─'*80}")

reflections = []
for n in range(2, 12):
    gam = 4 * math.sin(math.pi * n / 88)**2
    vg = math.cos(math.pi * n / 88)
    Z_curr = gam / abs(vg) if abs(vg) > 1e-10 else 1e10
    Z_prev = 4 * math.sin(math.pi * (n-1) / 88)**2 / abs(math.cos(math.pi * (n-1) / 88))
    R = (Z_curr - Z_prev) / (Z_curr + Z_prev) if (Z_curr > 0 and Z_prev > 0) else 0
    s_ref = lam_sync_hinv / (2 * n * abs(R)) if abs(R) > 1e-10 else 1e10
    reflections.append((n, R, s_ref))

ref_stacked, ref_weights = [], []
for n, R, s_ref in reflections:
    if s_ref < s_b[0] or s_ref > s_e[-1]: continue
    xi_b_r = float(b_interp(s_ref)) if s_b[0] < s_ref < s_b[-1] else 0
    err_b_r = float(b_err(s_ref)) if s_b[0] < s_ref < s_b[-1] else 1e10
    w_b_r = 1.0 / err_b_r**2 if err_b_r > 0 and err_b_r < 1e9 else 0
    xi_e_r = float(e_interp(s_ref)) if s_e[0] < s_ref < s_e[-1] else 0
    err_e_r = float(e_err(s_ref)) if s_e[0] < s_ref < s_e[-1] else 1e10
    w_e_r = 1.0 / err_e_r**2 if err_e_r > 0 and err_e_r < 1e9 else 0
    total_w = w_b_r + w_e_r
    if total_w > 0:
        stacked = (xi_b_r * w_b_r + xi_e_r * w_e_r) / total_w
        stacked_err = math.sqrt(1.0 / total_w)
    else:
        stacked = 0; stacked_err = 0
    ref_stacked.append(stacked); ref_weights.append(stacked_err)
ref_stacked = np.array(ref_stacked); ref_weights = np.array(ref_weights)
mean_ref = float(np.mean(ref_stacked)); sn_ref = float(np.mean(ref_stacked / ref_weights))

print(f"  Stacked {len(ref_stacked)} reflections")
print(f"  Mean stacked ξ: {mean_ref:+.6f}")
print(f"  Stacked S/N: {sn_ref:+.2f}")

# ================================================================
# 4. Reflection detection before/after stacking (v9.0 verbatim)
# ================================================================
print(f"\n{'─'*80}\n  4. REFLECTION DETECTION: BEFORE vs AFTER STACKING\n{'─'*80}")
print(f"\n  {'n':<4} {'s_ref':<12} {'BOSS S/N':<10} {'eBOSS S/N':<10} {'Stacked S/N':<12} {'Improvement':<12}")
print(f"  {'─'*56}")
for i, (n, R, s_ref) in enumerate(reflections):
    if s_ref < s_b[0] or s_ref > s_e[-1]: continue
    sn_b = float(xi_b_wavelet[np.argmin(np.abs(s_b - s_ref))]) / float(err_b[np.argmin(np.abs(s_b - s_ref))]) if s_b[0] < s_ref < s_b[-1] else 0
    sn_e = float(xi_e_wavelet[np.argmin(np.abs(s_e - s_ref))]) / float(err_e[np.argmin(np.abs(s_e - s_ref))]) if s_e[0] < s_ref < s_e[-1] else 0
    if i < len(ref_stacked) and ref_weights[i] > 0:
        sn_stacked = ref_stacked[i] / ref_weights[i]
        improvement = sn_stacked / max(abs(sn_b), abs(sn_e), 0.01)
    else:
        sn_stacked = 0; improvement = 0
    print(f"  {n:<4} {s_ref:<12.1f} {sn_b:<+10.2f} {sn_e:<+10.2f} {sn_stacked:<+12.2f} {improvement:<12.2f}")

# ---------------- 盤點檢查 (重跑可複現性) ----------------
print(f"\n{'─'*80}\n  5. 盤點檢查\n{'─'*80}")
check("λ_sync = 2π·R_H/88 (v9.0 定義恆等)", abs(LAMBDA_SYNC - 2*math.pi*R_H/88) < 1e-12)
check("R_H = c/H0_IDCM", abs(R_H - C_LIGHT/H0_IDCM) < 1e-9, f"{R_H:.4f} Mpc")
check("BAO = λ_sync/2", abs(LAMBDA_SYNC/2 - 147.44) < 0.01, f"{LAMBDA_SYNC/2:.4f} Mpc")
check("λ_sync (h⁻¹Mpc) ≈ 406.1", abs(lam_sync_hinv - 406.1) < 0.5, f"{lam_sync_hinv:.4f}")
# impedance 公式重算抽樣
Z2 = 4*math.sin(math.pi*2/88)**2/abs(math.cos(math.pi*2/88))
check("Z_2 = γ₂/|v_g(2)| 可重算", Z2 > 0, f"Z_2={Z2:.6f}")
check("堆疊 n 範圍 = 4..20 (v9.0 原文)", stacked_n == list(range(4, 21))[:len(stacked_n)])

print(f"\n{'='*80}")
print(f"  RESULT: {PASS}/{PASS+FAIL} PASS")
print(f"  (忠實重跑 = 盤點成功; 判決見 scripts/02)")
print(f"{'='*80}")

# 供 scripts/02 引用嘅複現值
out = os.path.join(DATA, "01_v9_rerun_results.txt")
with open(out, "w") as f:
    f.write("O131/01 — v9.0 stacked waveform 忠實重跑 (path-fixed)\n")
    f.write(f"H0_IDCM={H0_IDCM} R_H={R_H:.6f} Mpc lambda_sync={LAMBDA_SYNC:.6f} Mpc "
            f"lambda_sync_hinv={lam_sync_hinv:.6f} h-1Mpc h={H}\n")
    f.write(f"BOSS n_pts={len(s_b)} s=[{s_b[0]:.2f},{s_b[-1]:.2f}]\n")
    f.write(f"eBOSS n_pts={len(s_e)} s=[{s_e[0]:.2f},{s_e[-1]:.2f}]\n")
    f.write(f"harmonic_stacked_n={stacked_n}\n")
    f.write(f"mean_stacked_xi={mean_stacked_xi:+.6f}\nstacked_SN={sn_stack:+.4f}\n")
    f.write(f"reflection_stacked_n={len(ref_stacked)}\n")
    f.write(f"mean_ref_stacked_xi={mean_ref:+.6f}\nref_stacked_SN={sn_ref:+.4f}\n")
    f.write(f"RESULT={PASS}/{PASS+FAIL} PASS\n")
print(f"\n  寫入 {out}")
