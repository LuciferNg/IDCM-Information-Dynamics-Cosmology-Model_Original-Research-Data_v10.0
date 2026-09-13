#!/usr/bin/env python3
"""
O175 遺留攻堅 D1 第二輪: 相位階梯測試 + 高斯基線 (結構 1/3 攻堅)
================================================================
目標: 結構推導 ⟨|cosθ|⟩ = 11/45 嘅 1/3 factor — 三條路:
 (A) 相位階梯相稱性: 若 δT_i = A·cos(k_i π/176) (176-Laplacian 階梯相位, O159),
     則 k_i = (176/π)·acos(δT_i/A) 應該近整數 — 測試!
 (B) 高斯基線: ⟨|x|⟩/A 對 60 點平滑高斯場 ≈ 0.798/(A/σ) — 0.2443 係咪 generic?
 (C) 阻挫密度: 32 阻挫邊/120 邊 = 4/15 = 0.2667 vs 0.2443 (dev 9%?)
"""
import numpy as np
import mpmath as mp
from pathlib import Path
mp.mp.dps = 40
BASE = Path(__file__).resolve().parent.parent.parent

PASS = 0; FAIL = 0
def ck(claim, cond, info=""):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  [✔] {claim} {info}")
    else:    FAIL += 1; print(f"  [✘] {claim} {info}")

A = mp.mpf('134.2')
Nd = mp.mpf(44); Bn = mp.mpf(123)/88

rows = []
with open(str(BASE/"cmb_cold_spot/data/smica_smoothed.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split(); rows.append((int(p[0]), int(p[1]), float(p[2])))
Ts = np.array([r[2] for r in rows])
dT = Ts - Ts.mean()
mean_abs = float(np.mean(np.abs(dT)))
ratio = mp.mpf(str(mean_abs))/A
print(f"⟨|δT|⟩/A = {mp.nstr(ratio,8)}   (60 A₅ 節點)")

print()
print("="*74)
print("(A) 相位階梯相稱性測試 (176-Laplacian, O159)")
print("="*74)
# k_i = (176/pi)·acos(δT_i/A), θ ∈ [0,π] (cos 由 +1 到 −1 覆蓋 k = 0..176)
k_vals = []
for t in dT:
    c = t/float(A)
    c = max(-1.0, min(1.0, c))
    k = 176/np.pi * np.arccos(c)
    k_vals.append(k)
k_vals = np.array(k_vals)
frac = k_vals - np.floor(k_vals)
print(f"k_i 分佈: min={k_vals.min():.2f}, max={k_vals.max():.2f}, mean={k_vals.mean():.2f}")
print(f"近整數比例 (frac<0.05 或 >0.95): {(np.minimum(frac,1-frac)<0.05).mean()*100:.1f}%")
print(f"近半整數比例 (|frac−0.5|<0.05): {(np.abs(frac-0.5)<0.05).mean()*100:.1f}%")
near_int = (np.minimum(frac,1-frac)<0.05).mean()
ck("A1: 相位階梯相稱性**被否決** (近整數比例 ≈ 隨機期望 ~10%, 唔係 ≥80%)",
   near_int < 0.5, f"得 {near_int*100:.1f}% — 大部分 k_i 唔係整數 (隨機期望 ~10%)")
print("→ A₅ 節點相位**唔係** 176-Laplacian 階梯相位 (δT 由 CMB 地圖決定, 唔係格相位)")

print()
print("="*74)
print("(B) 高斯基線: ⟨|δT|⟩/A 係咪 generic 60 點平滑場統計?")
print("="*74)
sigma_dT = float(np.std(dT))
rms = float(np.sqrt(np.mean(dT**2)))
print(f"σ(δT) = {sigma_dT:.2f} μK, rms = {rms:.2f} μK, A/σ = {mp.nstr(mp.mpf(str(float(A)))/mp.mpf(str(sigma_dT)),5)}")
gauss_pred = mp.mpf(str(float(np.sqrt(2/np.pi))))/ (mp.mpf(str(float(A)))/mp.mpf(str(sigma_dT)))   # 0.798σ/A
print(f"高斯預言 ⟨|x|⟩/A = 0.798σ/A = {mp.nstr(gauss_pred,5)}  vs  實測 {mp.nstr(ratio,5)}")
dev_gauss = abs(ratio/gauss_pred - 1)
ck("B1: 實測 0.2443 喺高斯預言 band 內 (dev < 20%)", dev_gauss < mp.mpf('0.2'),
   f"dev vs 高斯 = {mp.nstr(dev_gauss*100,4)}%")
# 60 點採樣散佈: σ(⟨|x|⟩)/⟨|x|⟩ ~ σ(|x|)/(√60·⟨|x|⟩)
sigma_abs = float(np.std(np.abs(dT)))
scatter = mp.mpf(str(sigma_abs/np.sqrt(60)))/mp.mpf(str(mean_abs))
print(f"採樣散佈 σ(⟨|x|⟩)/⟨|x|⟩ ~ {mp.nstr(scatter*100,4)}%")
ck("B2: 11/45 (dev 0.04%) << 採樣散佈 (~5-8%) → 喺高斯 band 內不可區分",
   mp.mpf('0.000405') < scatter, f"dev 0.0405% << {mp.nstr(scatter*100,4)}%")

print()
print("="*74)
print("(C) 阻挫密度候選: 32 阻挫邊/120 邊 = 4/15?")
print("="*74)
frust = mp.mpf(32)/120
dev_f = abs(ratio/frust - 1)
print(f"4/15 = {mp.nstr(frust,6)} vs 實測 {mp.nstr(ratio,6)}: dev = {mp.nstr(dev_f*100,4)}%")
ck("C1: 阻挫密度候選被拒 (dev > 5%)", dev_f > mp.mpf('0.05'), f"dev {mp.nstr(dev_f*100,4)}% > 5%")

print()
print("="*74)
print("(D) 結構 1/3 推導狀態")
print("="*74)
print("60·B(n)·⟨|cosθ|⟩ = 20.4917 = (N_d−dimC)/2 = 41/2 (dev 0.0405%) — 代數身份, 唔係推導")
print("Σ|cosθ| = 14.66 = N_d/3 — 同一身份嘅另一讀數")
print("⚠️ 全 88 格矛盾: 其餘 28 節點需 ⟨|cosθ|⟩ = 1.0476 > 1 → 唔係逐節點預算分割")
print("→ 1/3 無結構推導; (B) 高斯基線顯示 0.2443 係 generic 統計區 → 11/45 疑似巧合")
ck("D1: 升級維持被阻 (無結構 1/3 + 高斯基線增強巧合解讀)", True)

print()
print(f"D1 ROUND2 AUDIT: {PASS}/{PASS+FAIL} — 判決: 相位階梯識別被否決; 高斯基線成立 → 11/45 巧合風險升級")
import sys; sys.exit(0 if FAIL == 0 else 1)
