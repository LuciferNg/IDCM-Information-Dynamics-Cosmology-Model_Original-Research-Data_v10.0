#!/usr/bin/env python3
"""
O48 Q1.8: 完整 forward model — IDCM 鋸齒梳 × lensing 卷積 vs Planck
=============================================================
修正 21 script 嘅「冇 lensing」bias:
  21 script 否證相位梳時冇計 CMB lensing smoothing。
  但 lensing 會將 44-週期梳抹平 — Planck 全譜見唔到對合元集中可能係預期效應。

Forward model:
  C_ℓ_model = A(ℓ) × [ IDCM 峰集梳 T(ℓ) ] ⊗ G(ℓ, σ_lens)
  其中 T(ℓ) = 對合元相位 {±1,±21} 處峰值嘅 44-週期梳 (鋸齒形)
       G    = Gaussian lensing kernel (σ_lens 掃描)
  對比: Planck detrend 殘差 correlation

對照: 正弦聲學振盪 (ΛCDM 近似) ⊗ 同一 lensing

盲測原則: 峰位/峰高全部結構公式輸入, 唯一掃描 = lensing 尺度 σ_lens
          (物理參數, 唔係 fit 目標 — lensing 尺度有文獻值)
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

# ---------- IDCM 峰集梳 ----------
print("="*72)
print("A. IDCM 峰集梳 T(ℓ)")
print("="*72)
# 峰位置 (結構公式): 真峰 5 + 假峰 2
peaks = {221: 1.0, 527: 1.0, 815: 1.0, 1013: 0.5, 1121: 1.0, 1337: 0.5, 1409: 1.0}
ALLOWED = {1, 21, 23, 43}

# 梳定義: ℓ mod 44 ∈ 對合元 → +1 (峰值/谷值交替? 先試純相位梳)
# 鋸齒形: 對合元 +1, 禁區 −1
def comb_ell(ell):
    return 1.0 if int(round(ell)) % 44 in ALLOWED else -1.0

# 結構峰梳 (delta 喺 IDCM 預言位置) — 用 Gaussian broadened 峰集
ells_full = np.arange(100, 2600, 4.0)  # 粗格
def comb_model(ells, sigma_lens, peak_model="comb"):
    """返回 T(ℓ) 模型: 44-週期梳 或 峰集 delta 梳, 卷積 Gaussian"""
    T = np.zeros_like(ells, dtype=float)
    if peak_model == "comb":
        for i, e in enumerate(ells):
            T[i] = comb_ell(e)
    elif peak_model == "delta":
        # 峰集: 每個峰加寬 Gaussian
        for p, amp in peaks.items():
            T += amp * np.exp(-0.5 * ((ells - p) / max(sigma_lens, 1e-3)) ** 2)
    # lensing 卷積 (Gaussian kernel 喺 ℓ 空間)
    if sigma_lens > 0 and peak_model == "comb":
        # 頻域卷積太貴, 直接做 space 卷積
        ker = np.exp(-0.5 * ((np.arange(len(ells)) * (ells[1]-ells[0])) / sigma_lens) ** 2)
        ker /= ker.sum()
        T = np.convolve(T, ker, mode="same")
    return T

# ---------- B. Planck detrend 殘差 ----------
print("="*72)
print("B. Planck 殘差 (detrend 包絡)")
print("="*72)
ells_p = np.array([e for e, d in planck_tt if 200 < e < 2500])
Ds_p = np.array([d for e, d in planck_tt if 200 < e < 2500])
logD = np.log(Ds_p)
coef = np.polyfit(ells_p, logD, 2)
env = np.exp(np.polyval(coef, ells_p))
res = Ds_p / env
res_n = (res - res.mean()) / res.std()
print(f"  包絡 fit: lnD = {coef[0]:.2e}ℓ² + {coef[1]:.3e}ℓ + {coef[2]:.3f}")
print(f"  殘差 std: {res.std():.3f}")

# ---------- C. 梳模型 correlation 掃描 ----------
print("="*72)
print("C. correlation(梳⊗lensing, Planck殘差) vs σ_lens")
print("="*72)
# 對齊: 插值模型到 Planck ℓ
for model_name in ["comb", "delta"]:
    print(f"  --- {model_name} 模型 ---")
    best = (0, -1)
    for sigma in [0, 10, 20, 40, 60, 80, 100, 150, 200, 300, 400]:
        T = comb_model(ells_full, sigma, model_name)
        Tint = np.interp(ells_p, ells_full, T)
        if Tint.std() == 0:
            continue
        Tn = (Tint - Tint.mean()) / Tint.std()
        corr = float(np.corrcoef(Tn, res_n)[0, 1])
        marker = " <--" if corr > best[1] else ""
        if corr > best[1]:
            best = (sigma, corr)
        print(f"    σ_lens={sigma:4d}: corr={corr:+.3f}{marker}")
    print(f"  best: σ_lens={best[0]}, corr={best[1]:+.3f}")

# ---------- D. 對照: 正弦振盪 (ΛCDM 近似) ----------
print("="*72)
print("D. 對照 — 正弦聲學振盪 ⊗ lensing")
print("="*72)
# ΛCDM 近似: 聲學 peak period Δℓ ≈ 300, oscillation D(ℓ) = 1 + a·cos(2πℓ/Δ + φ)
# 最簡單: cos(2πℓ/Δℓ_A) Δℓ_A ≈ 300 (峰間距平均)
best_sin = (0, -1)
for phase_deg in [0, 20, 40, 60, 80]:
    ph = phase_deg * math.pi / 180
    Tsin = 1 + 0.5 * np.cos(2 * math.pi * ells_full / 300 + ph)
    Tint = np.interp(ells_p, ells_full, Tsin)
    Tn = (Tint - Tint.mean()) / Tint.std()
    corr = float(np.corrcoef(Tn, res_n)[0, 1])
    if corr > best_sin[1]:
        best_sin = (phase_deg, corr)
    print(f"    sin phase={phase_deg}°: corr={corr:+.3f}")
print(f"  best sin: phase={best_sin[0]}° corr={best_sin[1]:+.3f}")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)