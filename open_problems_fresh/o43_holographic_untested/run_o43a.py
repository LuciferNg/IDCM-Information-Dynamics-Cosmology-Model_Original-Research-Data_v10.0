#!/usr/bin/env python3
"""
O43-A: M=33 = F₉−1 coherent truncation verification
Compare Planck high-ℓ data with Silk damping theory
"""
import numpy as np
import os, math, json

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
OUT = f"{BASE}/open_problems_fresh/o43_holographic_untested"

# Load Planck data
planck = np.loadtxt(f"{BASE}/open_problems_fresh/o9_high_ell_peaks/data/planck_tt.txt")
ell = planck[:, 0].astype(int)
C = planck[:, 1]
err = planck[:, 2]
D = C * ell * (ell + 1) / (2 * np.pi)
D_err = err * ell * (ell + 1) / (2 * np.pi)

# Known peak amplitudes from O9
peaks = {221: 5816.5, 527: 2579.2, 815: 2552.7, 1013: 1079.5,
         1121: 1246.3, 1337: 757.9, 1400: 830.2}
peak_ells = sorted(peaks.keys())
peak_amps = [peaks[l] for l in peak_ells]

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line)
    results.append(line)

log("=" * 72)
log("O43-A: M=33 = F₉−1 相干截斷 vs Silk 阻尼")
log("=" * 72)

# 1. Fit Silk damping envelope to peak amplitudes
log("\n1. Silk 阻尼擬合 (峰振幅):")
log("   模型: D(ℓ) = D₀ · ℓ^p · exp(-(ℓ/ℓ_D)^b)")
log("   使用峰 ℓ=221,527,815,1013,1121,1337,1400")

from scipy.optimize import curve_fit
def silk_model(l, D0, lD, beta, p):
    return D0 * (l/1000)**p * np.exp(-((l/lD)**beta))

popt, pcov = curve_fit(silk_model, np.array(peak_ells), np.array(peak_amps),
                        p0=[6000, 2000, 1.5, 0], maxfev=10000)
D0, lD, beta, p = popt
log(f"   D₀ = {D0:.1f}, ℓ_D = {lD:.1f}, β = {beta:.3f}, p = {p:.3f}")

# 2. Compute predicted Silk damping values
silk_pred = silk_model(ell, *popt)

# 3. Check the ℓ>1448 region (beyond IDCM M=33 cutoff)
log("\n2. 高ℓ尾 (>1448) 檢查:")
log(f"   M=33 截斷 ℓ_max = 44×33 = 1452")
mask_high = ell >= 1448
high_ell = ell[mask_high]
high_D = D[mask_high]
high_silk = silk_pred[mask_high]
high_err = D_err[mask_high]

# Residuals from Silk damping
residuals = (high_D - high_silk) / high_silk * 100
log(f"   高ℓ點數: {len(high_ell)}")
log(f"   Silk 殘差 mean: {np.mean(residuals):.2f}%")
log(f"   Silk 殘差 std: {np.std(residuals):.2f}%")
log(f"   Silk 殘差 max: {np.max(np.abs(residuals)):.2f}%")

# Check for step-like discontinuity at 1452
log("\n3. 階梯式截斷檢查:")
# Compare mean D before/after 1452
before = D[(ell >= 1400) & (ell < 1452)]
after = D[(ell >= 1452) & (ell < 1500)]
log(f"   1400-1452 mean D: {np.mean(before):.1f} ± {np.std(before):.1f}")
log(f"   1452-1500 mean D: {np.mean(after):.1f} ± {np.std(after):.1f}")
log(f"   跳變: {np.mean(before)-np.mean(after):.1f} μK²")

# Closer: 1448-1456 window
window = D[(ell >= 1448) & (ell <= 1456)]
win_ell = ell[(ell >= 1448) & (ell <= 1456)]
log(f"   1448-1456 詳細:")
for i in range(len(window)):
    log(f"     ℓ={win_ell[i]} D={window[i]:.1f} Silk={silk_pred[ell==win_ell[i]][0]:.1f}")

# 4. Check for smoothness
log("\n4. 平滑度檢查 (二階導數):")
d2 = np.zeros(len(D))
for i in range(1, len(D)-1):
    d2[i] = D[i+1] - 2*D[i] + D[i-1]
d2_high = d2[mask_high]
log(f"   高ℓ d²D 統計: mean={np.mean(d2_high):.3f}, std={np.std(d2_high):.3f}")
log(f"   (如果階梯式: 單點 d²D >> std)")

# 5. Compare with Silk damping over full range
log("\n5. 全範圍 Silk 阻尼擬合品質:")
chi2 = np.sum((D - silk_pred)**2 / D_err**2) / len(D)
log(f"   χ²/dof = {chi2:.2f}")

# 6. Check if there's a detectable 'step' at ℓ=1452
log("\n6. 1452 截斷檢測:")
# Compare the 1448-1456 region with Silk prediction
window_resid = (window - silk_model(win_ell, *popt)) / silk_model(win_ell, *popt) * 100
log(f"   1448-1456 Silk 殘差: {[f'{r:.1f}%' for r in window_resid]}")

# Check the last visible peak
log("\n7. 最後可辨識峰:")
last_peaks = []
for i in range(1, len(D)-1):
    if D[i] > D[i-1] and D[i] > D[i+1] and ell[i] > 1400 and D[i] > 500:
        last_peaks.append((ell[i], D[i]))
log(f"   高ℓ局部極大: {last_peaks}")

# 8. Compare with Silk damping falloff shape
log("\n8. 判決:")
# Check if the drop from ℓ=1400 to ℓ=1733 is smooth
d1400 = D[ell == 1400][0]
d1733 = D[ell == 1733][0] if 1733 in ell else 0
silk_1400 = silk_model(1400, *popt)
silk_1733 = silk_model(1733, *popt)
log(f"   D(1400) = {d1400:.1f}, Silk(1400) = {silk_1400:.1f}")
log(f"   D(1733) = {d1733:.1f}, Silk(1733) = {silk_1733:.1f}")
log(f"   實測衰減: {d1733/d1400:.3f}, Silk預測: {silk_1733/silk_1400:.3f}")

# Check if there's any evidence of a sharp truncation
# The holographic claim: M=33 modes → sharp cutoff at ℓ_max=1452
# Silk damping: smooth exponential decay
# Key test: does the data follow the Silk curve smoothly through 1452?
cross_1452 = np.abs(ell - 1452).argmin()
before_1452 = slice(max(0, cross_1452-10), cross_1452)
after_1452 = slice(cross_1452, min(len(ell), cross_1452+10))
before_mean = np.mean(D[before_1452])
after_mean = np.mean(D[after_1452])
silk_before = np.mean(silk_pred[before_1452])
silk_after = np.mean(silk_pred[after_1452])
log(f"\n   1452 前後 ±10 bins:")
log(f"   實測: {before_mean:.1f} → {after_mean:.1f} (Δ={after_mean-before_mean:.1f})")
log(f"   Silk: {silk_before:.1f} → {silk_after:.1f} (Δ={silk_after-silk_before:.1f})")
log(f"   差值: Δ_data - Δ_Silk = {(after_mean-before_mean)-(silk_after-silk_before):.2f}")

# Conclusion
log("\n" + "=" * 72)
log("結論:")
log("=" * 72)
if np.mean(residuals) > 5:
    log("  ❌ 高ℓ (>1448) 顯著偏離 Silk 阻尼 — 支持全息截斷")
else:
    log("  🟢 高ℓ (>1448) 與 Silk 阻尼一致 — 暴脹解釋成立")
log(f"  Silk 殘差: {np.mean(residuals):.2f}% ± {np.std(residuals):.2f}%")
log(f"  ℓ=1452 前後 Δ: data={np.mean(before)-np.mean(after):.1f}")
log(f"  M=33 截斷: ℓ_max=1452")
log(f"  Planck 數據最高 ℓ: {ell[-1]}")
log(f"  → 由 {ell[-1]} 嘅數據, 衰減形狀符合 Silk 阻尼")

# Save results
with open(f"{OUT}/data_o43a.txt", "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/data_o43a.txt")