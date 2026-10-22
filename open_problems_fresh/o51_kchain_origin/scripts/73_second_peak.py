#!/usr/bin/env python3
"""
O51/73: 第二峰檢驗 — BOSS post-recon ξ(s) 高 s 段
===============================================================
IDCM 預言: 第二峰喺 2×λ_sync/2 = 198.36 h⁻¹Mpc
BOSS post-recon ξ(s) 只到 s=177.5, 睇唔到 198.36

用 eBOSS full ξ(s) (s=7.5-247.5) 檢查高 s 段:
  - 第二峰期望 ~198 h⁻¹Mpc
  - 第三峰期望 ~297 h⁻¹Mpc
"""
import json, math, numpy as np

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

# ============ 1. 讀 eBOSS full ξ(s) ============
s_vals, xi_vals, err_vals = [], [], []
with open('/home/wsl/Projects/IDCM-Original/IDCM-v9.0--W-Field-Lattice/sync_bump_analysis/eboss_dr16_lrg_xi.txt') as f:
    for line in f:
        if line.startswith('#') or not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 3:
            s_vals.append(float(parts[0]))
            xi_vals.append(float(parts[1]))
            err_vals.append(float(parts[2]))

s = np.array(s_vals)
xi = np.array(xi_vals)
err = np.array(err_vals)

print("=" * 62)
print("第二峰檢驗 — eBOSS DR16 full ξ(s)")
print("=" * 62)
print(f"數據: {len(s)} bins, s = {s.min():.1f}-{s.max():.1f} h⁻¹Mpc")

# ============ 2. IDCM 預言 ============
R_H = 4129.94
h = 0.6727
lambda_sync = 2 * math.pi * R_H / 88
lambda_h = lambda_sync * h
print(f"\nλ_sync = {lambda_h:.2f} h⁻¹Mpc")
print(f"峰 1 (BAO): λ_sync/2 = {lambda_h/2:.2f}")
print(f"峰 2:       λ_sync   = {lambda_h:.2f}")
print(f"峰 3:      3λ_sync/2 = {3*lambda_h/2:.2f}")

# ============ 3. 高 s 段 ξ(s) 分析 ============
print(f"\n--- 高 s 段 (s ≥ 100) ξ(s) 分析 ---")
xs2 = xi * s**2
err_xs2 = err * s**2

print(f"{'s':>8} {'ξ(s)':>12} {'ξ×s²':>12} {'S/N':>8}")
print("-" * 40)
for i in range(len(s)):
    if s[i] >= 100:
        snr = xi[i] / err[i]
        sy = " ← BAO" if abs(s[i] - lambda_h/2) < 5 else ""
        sy += " ← λ_sync" if abs(s[i] - lambda_h) < 5 else ""
        sy += " ← 3λ/2" if abs(s[i] - 3*lambda_h/2) < 5 else ""
        print(f"{s[i]:>8.1f} {xi[i]:>+12.6f} {xs2[i]:>12.4f} {snr:>+8.2f}{sy}")

# ============ 4. 第二峰搜索 ============
print(f"\n--- 第二峰搜索 (s = 150-250) ---")
mask2 = (s >= 150) & (s <= 250)
if mask2.sum() > 0:
    i_max = np.argmax(xi[mask2]) + np.where(mask2)[0][0]
    print(f"ξ(s) 最大: s={s[i_max]:.1f}, ξ={xi[i_max]:.6f}")
    i_xs2 = np.argmax(xs2[mask2]) + np.where(mask2)[0][0]
    print(f"ξ×s² 最大: s={s[i_xs2]:.1f}, ξs²={xs2[i_xs2]:.4f}")
    
    # 第二峰附近有冇局部峰?
    peaks = []
    for i in range(2, len(s)-2):
        if s[i] >= 150 and xi[i] > xi[i-1] and xi[i] > xi[i-2] and xi[i] > xi[i+1] and xi[i] > xi[i+2]:
            peaks.append((s[i], xi[i], xi[i]/err[i]))
    if peaks:
        print(f"\n局部峰 (s≥150):")
        for sp, xip, snr in peaks:
            sy = ""
            if abs(sp - lambda_h) < 10:
                sy = " ← λ_sync"
            if abs(sp - 3*lambda_h/2) < 10:
                sy = " ← 3λ_sync/2"
            print(f"  s={sp:7.1f}, ξ={xip:+.6f}, S/N={snr:+.2f}{sy}")
    
    # 最近 IDCM 預言嘅 bin
    for name, pred in [("λ_sync", lambda_h), ("3λ_sync/2", 3*lambda_h/2), ("2λ_sync", 2*lambda_h)]:
        if s.min() <= pred <= s.max():
            idx = np.argmin(np.abs(s - pred))
            print(f"\nIDCM {name} = {pred:.1f}: s={s[idx]:.1f}, ξ={xi[idx]:.6f}, S/N={xi[idx]/err[idx]:+.2f}")

# ============ 5. 總結 ============
print(f"\n{'=' * 62}")
print(f"第二峰檢驗: 數據截止 s=247.5, 預言峰 198.4 喺範圍內")
# 檢查最近嘅 bin 係咪有訊號
idx_198 = np.argmin(np.abs(s - lambda_h))
idx_297 = np.argmin(np.abs(s - 3*lambda_h/2))
snr_198 = xi[idx_198] / err[idx_198]
snr_297 = xi[idx_297] / err[idx_297]
check("λ_sync 峰 S/N > 3 (eBOSS)", snr_198 > 3, f"S/N={snr_198:.2f}")
check("3λ_sync/2 峰 S/N > 3 (eBOSS)", snr_297 > 3, f"S/N={snr_297:.2f}")

result = {
    'lambda_sync_h': round(lambda_h, 2),
    's_peak2_pred': round(lambda_h, 2),
    's_peak2_bin': round(float(s[idx_198]), 2),
    'snr_peak2': round(float(snr_198), 2),
    's_peak3_pred': round(3*lambda_h/2, 2),
    's_peak3_bin': round(float(s[idx_297]), 2),
    'snr_peak3': round(float(snr_297), 2),
    'pass': PASS,
    'fail': FAIL
}

with open('data/73_second_peak.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"\n✅ 結果 -> data/73_second_peak.json")