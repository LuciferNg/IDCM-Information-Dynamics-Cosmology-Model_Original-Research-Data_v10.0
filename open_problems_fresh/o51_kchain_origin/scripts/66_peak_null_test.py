#!/usr/bin/env python3
"""
O51/66: λ_sync 諧波 Peak/Null Testing — eBOSS DR16 raw ξ(s)
===============================================================
skill §9.3 框架: 最精細方式測量 — 同時測峰位同谷位

IDCM 預言:
  Peak:  s_n = λ_sync/n, n = 2,3,...,10   (諧波峰)
  Null:  s_n = λ_sync/(n+0.5)             (諧波之間嘅谷)

數據: eBOSS DR16 LRG raw ξ(s), s = 7.5-247.5 h⁻¹Mpc (49 bins)
統計: 期望位置嘅 S/N (ξ/σ), 峰應該 >0, 谷應該 <0
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

# ============ 1. 讀數據 ============
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

# ============ 2. IDCM 預言位置 ============
R_H = 4129.94
h = 0.6727
lambda_sync = 2 * math.pi * R_H / 88
lambda_h = lambda_sync * h

print("=" * 62)
print("λ_sync 諧波 Peak/Null Testing")
print("=" * 62)
print(f"λ_sync = {lambda_sync:.2f} Mpc = {lambda_h:.2f} h⁻¹Mpc")

# ============ 3. Peak 檢驗 ============
print("\n--- Peak 檢驗: s_n = λ_sync/n ---")
peak_results = []
for n in range(2, 11):
    s_n = lambda_h / n
    if s.min() <= s_n <= s.max():
        idx = np.argmin(np.abs(s - s_n))
        snr = xi[idx] / err[idx]
        peak_results.append((n, s_n, s[idx], xi[idx], snr))
        print(f"  n={n:2d}: s_pred={s_n:6.2f} → bin {s[idx]:6.1f} (Δ={s[idx]-s_n:+5.1f}), ξ={xi[idx]:.4f}, S/N={snr:+.2f}")

n_peaks = len(peak_results)
n_pos = sum(1 for _,_,_,_,snr in peak_results if snr > 0)
print(f"\n峰檢驗: {n_pos}/{n_peaks} 正 S/N")
check("Peak: 多數期望位置 S/N > 0", n_pos >= n_peaks * 0.7, f"{n_pos}/{n_peaks}")

# ============ 4. Null 檢驗 ============
print("\n--- Null 檢驗: s_n = λ_sync/(n+0.5) ---")
null_results = []
for n in range(2, 11):
    s_n = lambda_h / (n + 0.5)
    if s.min() <= s_n <= s.max():
        idx = np.argmin(np.abs(s - s_n))
        snr = xi[idx] / err[idx]
        null_results.append((n, s_n, s[idx], xi[idx], snr))
        print(f"  n={n:2d}: s_pred={s_n:6.2f} → bin {s[idx]:6.1f} (Δ={s[idx]-s_n:+5.1f}), ξ={xi[idx]:.4f}, S/N={snr:+.2f}")

n_nulls = len(null_results)
n_neg = sum(1 for _,_,_,_,snr in null_results if snr < 0)
print(f"\n谷檢驗: {n_neg}/{n_nulls} 負 S/N")
check("Null: 多數期望位置 S/N < 0", n_neg >= n_nulls * 0.7, f"{n_neg}/{n_nulls}")

# ============ 5. 峰谷交替檢驗 ============
print("\n--- 峰谷交替檢驗 ---")
print("IDCM 預言: 峰 (n) 同谷 (n+0.5) 交替出現")
print("即 ξ(λ_sync/n) > ξ(λ_sync/(n+0.5)) > ξ(λ_sync/(n+1))...")
alternations = 0
total_pairs = 0
for n in range(2, 10):
    s_peak = lambda_h / n
    s_null = lambda_h / (n + 0.5)
    s_next = lambda_h / (n + 1)
    if s.min() <= s_next <= s.max():
        idx_p = np.argmin(np.abs(s - s_peak))
        idx_n = np.argmin(np.abs(s - s_null))
        idx_nx = np.argmin(np.abs(s - s_next))
        # 峰 > 谷 < 峰
        if xi[idx_p] > xi[idx_n] < xi[idx_nx]:
            alternations += 1
        total_pairs += 1
        print(f"  n={n}: ξ(峰)={xi[idx_p]:.4f}, ξ(谷)={xi[idx_n]:.4f}, ξ(峰2)={xi[idx_nx]:.4f} "
              f"{'✅' if xi[idx_p] > xi[idx_n] < xi[idx_nx] else '❌'}")

print(f"\n交替檢驗: {alternations}/{total_pairs} 峰>谷<峰")
check("峰谷交替: 多數符合", alternations >= total_pairs * 0.6, f"{alternations}/{total_pairs}")

# ============ 6. 對照: 隨機位置 ============
print("\n--- 對照: 隨機位置 S/N 分佈 ---")
rng = np.random.default_rng(42)
N_SIM = 1000
random_pos_snr = []
for _ in range(N_SIM):
    # 隨機揀 9 個位置
    idxs = rng.choice(len(s), size=9, replace=False)
    random_pos_snr.extend(xi[idxs] / err[idxs])

mean_random = np.mean(random_pos_snr)
mean_peak = np.mean([snr for _,_,_,_,snr in peak_results])
mean_null = np.mean([snr for _,_,_,_,snr in null_results])
print(f"隨機位置 mean S/N = {mean_random:+.3f}")
print(f"峰位置 mean S/N   = {mean_peak:+.3f}")
print(f"谷位置 mean S/N   = {mean_null:+.3f}")
check("峰 mean S/N > 隨機 mean", mean_peak > mean_random, f"{mean_peak:+.3f} vs {mean_random:+.3f}")
check("谷 mean S/N < 隨機 mean", mean_null < mean_random, f"{mean_null:+.3f} vs {mean_random:+.3f}")

# ============ 7. 總結 ============
print(f"\n{'=' * 62}")
print(f"Peak/Null Testing 總結: ✅ {PASS} / {PASS+FAIL}")
print(f"{'=' * 62}")

result = {
    'lambda_sync_h': round(lambda_h, 3),
    'peak_results': [{'n': n, 's_pred': round(sp,2), 's_bin': float(sb), 'xi': round(x,4), 'snr': round(snr,2)} for n,sp,sb,x,snr in peak_results],
    'null_results': [{'n': n, 's_pred': round(sp,2), 's_bin': float(sb), 'xi': round(x,4), 'snr': round(snr,2)} for n,sp,sb,x,snr in null_results],
    'alternations': f'{alternations}/{total_pairs}',
    'mean_peak_snr': round(float(mean_peak), 3),
    'mean_null_snr': round(float(mean_null), 3),
    'mean_random_snr': round(float(mean_random), 3),
    'pass': PASS,
    'fail': FAIL
}

with open('data/66_peak_null_test.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"\n✅ 結果 -> data/66_peak_null_test.json")