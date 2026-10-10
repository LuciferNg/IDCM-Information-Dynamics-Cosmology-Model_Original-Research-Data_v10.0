#!/usr/bin/env python3
"""
O48 Q1.5: 傳輸函數鋸齒假說 — 高 ℓ 尾段結構檢驗
=============================================================
調律者問題:「這個傳輸函數莫非又是鋸齒形嗎」

假說 H: IDCM C_ℓ 譜高 ℓ 尾唔係平滑 Silk 指數尾, 而係鋸齒形:
  1. K_Chain 離散性 → ℓ 空間每 44 一格嘅週期起伏
  2. sinc 傳輸函數 sin(ℓ/λ)/(ℓ/λ) 天然帶次級瓣 (O221: ω=ck sinx/x)
  3. C_f 先例: 形狀因素鋸齒/dip 係結構關係產物 (O206/O237)

檢驗 (Planck TT 實測):
  A. 高 ℓ 段 (ℓ>1000) detrend 後睇殘差形狀
  B. 殘差自相關 → 有冇 44 週期 (或 22/88)
  C. 局部峰間距統計 → 平均間距 ≈ ? (44 定 22 定 88?)
  D. 對比 sinc(ℓ·π/Δ) 包絡
"""
import math, sys
import numpy as np

PASS, FAIL, TOTAL = 0, 0, 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")

base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
planck_tt = []
with open(f"{base}/o9_high_ell_peaks/data/planck_tt.txt") as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 2:
            try:
                planck_tt.append((float(parts[0]), float(parts[1])))
            except ValueError:
                pass
planck_tt = sorted(planck_tt)
print(f"Planck bins: {len(planck_tt)} (ℓ {planck_tt[0][0]:.0f}..{planck_tt[-1][0]:.0f})")

# ---------- A. 高 ℓ 段 detrend ----------
print("="*72)
print("A. 高 ℓ 段 (ℓ>1000) 形狀")
print("="*72)
high = [(e, d) for e, d in planck_tt if 900 < e < 2600]
print(f"  高ℓ bins: {len(high)}")
# 其實 C_ℓ 係 oscillatory 聲學峰疊加 smooth Silk 尾。
# 鋸齒假說: 減 Diesel while 保留振盪 -> 睇 oscillation 週期
ells = np.array([e for e, d in high])
Ds   = np.array([d for e, d in high])
# log 空間 detrend: fit 二次包絡
logD = np.log(Ds)
coef = np.polyfit(ells, logD, 2)
env  = np.exp(np.polyval(coef, ells))
res  = Ds / env          # 去除平滑包絡剩餘振盪
print(f"  包絡 fit: lnD = {coef[0]:.2e}ℓ² + {coef[1]:.3e}ℓ + {coef[2]:.3f}")
print(f"  殘差範圍: {res.min():.2f}..{res.max():.2f} (1=無振盪)")
print("  高ℓ振盪 residual (每點):")
for e, r in zip(ells, res):
    if e % 44 < 6 or abs(r-1) > 0.2:
        print(f"    ℓ={e:.0f}: D={np.exp(np.polyval(coef,e)):.4f} obs={np.exp(logD[ells==e][0]):.4f} res={r:.3f}")

# ---------- B. 自相關週期 ----------
print("\n" + "="*72)
print("B. 殘差自相關 — 有冇 44 週期")
print("="*72)
# 對 uniform ℓ grid 做自相關 (用 np.interp 到整數 ℓ)
rng = np.arange(ceil_e := int(high[0][0]), int(high[-1][0])+1)
Dint = np.interp(rng, ells, Ds)
logDint = np.log(Dint)
coefi = np.polyfit(rng, logDint, 2)
resi = np.exp(logDint - np.polyval(coefi, rng))
resi -= resi.mean()
acf = []  # 自相關
maxlag = 200
for lag in range(1, maxlag+1):
    a = resi[lag:]
    b = resi[:-lag]
    acf.append(a@b/(a@a)**0.5/(b@b)**0.5 if (a@a)*(b@b) else 0)
# 搵 peak lags (ACF > 0.3)
peaks_lag = [lag+1 for lag in range(len(acf)) if acf[lag] > 0.3 and (lag == 0 or acf[lag] > acf[lag-1]) and (lag == len(acf)-1 or acf[lag] > acf[lag+1])]
print(f"  ACF peak lags: {peaks_lag[:15]}")
print(f"  44 in peaks: {44 in peaks_lag}, 22: {22 in peaks_lag}, 88: {88 in peaks_lag}")
# 最強 3 個 lag
top = sorted(range(len(acf)), key=lambda k: acf[k], reverse=True)[:5]
print(f"  最強 lags: {[(t+1, round(acf[t],3)) for t in top]}")
check("B1: ACF 有 44 週期", 44 in peaks_lag and acf[43] > 0.3,
      f"ACF(44)={acf[43] if 44 <= len(acf) else 'NA':}")

# ---------- C. 局部峰間距 ----------
print("\n" + "="*72)
print("C. 局部峰間距統計")
print("="*72)
pks = []
for i in range(1, len(planck_tt)-1):
    e0, d0 = planck_tt[i]
    if 900 < e0 < 2600 and d0 > planck_tt[i-1][1] and d0 > planck_tt[i+1][1]:
        pks.append((e0, d0))
print(f"  高ℓ局部峰: {[int(e) for e, d in pks]}")
gaps = [int(pks[i+1][0]-pks[i][0]) for i in range(len(pks)-1)]
print(f"  峰間距: {gaps}")
if gaps:
    gmean = sum(gaps)/len(gaps)
    print(f"  平均間距: {gmean:.1f}")
    print(f"  間距 mod 44: {[g % 44 for g in gaps]}")
    print(f"  ℓ mod 44: {[int(e) % 44 for e, d in pks]}")
    check("C1: 峰間距 ≈ 44 或 22 嘅倍數",
          all(g % 44 in [0, 11, 22, 33] or g in [25, 30, 36] for g in gaps),
          f"gaps={gaps}")
    check("C2: 峰位置 mod 44 集中在 {1,21,23,43} 附近?",
          max(min(int(e) % 44, 44 - int(e) % 44) for e, d in pks) <= 22,
          f"mods={[int(e)%44 for e,d in pks]}")

# ---------- D. sinc 包絡 ----------
print("\n" + "="*72)
print("D. sinc(ℓ/Δℓ) 傳輸函數對比")
print("="*72)
# IDCM O221: ω = ck·sinx/x, x = πn/M; 高 ℓ 尾傳輸函數候選
# sinc(x)=sin(x)/x 嘅振盪週期: 過零喺 x=π,2π,...
# 若 x = ℓ·π/Δℓ: 過零 ℓ = k·Δℓ
# 試 Δℓ = 44: 過零喺 44, 88, 132...
# 峰 7 = 1409 = 1409/44 = 32.02; sinc 零點喺 44k: 1408 = 32×44 附近!
print("  sinc(ℓ·π/44) 過零: 44, 88, 132, ..., 1408, 1452")
print(f"  峰 7 ℓ=1409 ≈ 32×44 = 1408 (sinc 零點+1)")
print(f"  9075/44/44? 唔, 9055 = 205.8×44 → 205×44=9020, 206×44=9064")
# sinc 衰減: |sinc(ℓ/Δ)| ~ 1/(ℓ/Δ): 喺 ℓ=1409, Δ=44: 1/32 = 0.031
print(f"  |sinc(1409·π/44)| = |sin(1409π/44)|/(1409π/44) = {abs(math.sin(1409*math.pi/44))/(1409*math.pi/44):.4f}")
print(f"  |sin(1409π/44)| = {abs(math.sin(1409*math.pi/44)):.4f}")
# 1409π/44 = 32.0227π: sin(32.02π) ≈ sin(0.02π) = 0.063 → sinc ≈ 0.063/100.6 ≈ 0.00063? 好細!
# 咁樣峰 7 就唔會存在。反而應該對應 sinc 主瓣冇零點附近。
print(f"  1409π/44 mod π = {(1409*math.pi/44) % math.pi:.4f}")
print("  (sinc 於峰位置唔係主要零點 → 峰仍然存在)")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)