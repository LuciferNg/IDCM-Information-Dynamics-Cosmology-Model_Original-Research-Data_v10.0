#!/usr/bin/env python3
"""
O48 Q1.24: lensing 前向 — 理論 σ_lens vs IDCM 候選 {49.5, 50, 55}
=============================================================
Q1.23: σ 身份平台未分辨 (49.5=297/6, 50, 55=F₁₀ 全 Δχ²<6.6)。
用 CAMB 計真正 lensing smoothing 寬度, 分辨邊個候選係物理。

方法 (Lewis & Challinor 2006, 標準):
  lensed C_ℓ ≈ ∫ C_ℓ' W(ℓ, ℓ') dℓ' 嘅 kernel 寬度
  實務上: lensing smoothing 可以用 Gaussian 近似, 寬度
    σ_lens² ≈ (1/2)·Σ_ℓ [(2ℓ+1)/(4π)] ℓ(ℓ+1) C_ℓ^φφ / W_ℓ ...
  標準公式 (Planck lensing): σ_lens ≈ sqrt( 1/2 Σ_ℓ (2ℓ+1)/(4π) ℓ(ℓ+1) C_ℓ^φφ )
  (呢個係 C_ℓ 對數導數尺度嘅 1σ 平滑寬度)

步驟:
  1. CAMB → C_ℓ^φφ (lensing potential power)
  2. 計 σ_lens 理論值 (用 Planck 2018 參數)
  3. 對比 IDCM 候選 49.5/50/55
  4. 再計: 將 delta 梳真 lensing 卷積 vs Gaussian 近似嘅 χ² 差異
"""
import math, sys
import numpy as np
import camb

print("="*72)
print("A. CAMB lensing potential → 理論 σ_lens")
print("="*72)
# Planck 2018 最佳擬合參數 (plik + BAO)
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, mnu=0.06,
                   omk=0, tau=0.0544)
pars.InitPower.set_params(As=2.1e-9, ns=0.9649)
pars.set_for_lmax(4000, max_eta_k=8000)
pars.NonLinear = camb.model.NonLinear_none

print("CAMB 計算中...")
results = camb.get_results(pars)
# CAMB 2.0.1: get_lens_potential_cls col0 = C_φφ (l=2 5e-8, 標準量級)
c_phiphi = results.get_lens_potential_cls(lmax=4000)[:, 0]
# 標準公式: σ_lens² = ½ Σ (2ℓ+1)/(4π) ℓ(ℓ+1) C_ℓ^ϕϕ
# 但係 CAMB 嘅 C_ϕϕ 可以係 dimensionless (rad²), 視版本
ll = np.arange(len(c_phiphi))
term = ((2*ll+1)/(4*np.pi)) * ll*(ll+1) * c_phiphi
sigma2 = 0.5 * np.sum(term)
sigma = math.sqrt(sigma2)
print(f"C_ϕϕ[:10] = {c_phiphi[:10]}")
print(f"σ_lens² = ½Σ(2ℓ+1)/4π·ℓ(ℓ+1)C_ℓϕϕ = {sigma2:.6f}")
print(f"理論 σ_lens = {sigma:.2f}")

# lensing kernel 2D: 用 C_ℓ^ϕϕ 計 kernel 標準寬度 (FWHM)
# 另一常用量: lensing RMS displacement
disp2 = np.sum((2*ll+1)/(4*np.pi) * c_phiphi)  # <ϕ²> (無 ℓ(ℓ+1))
print(f"<ϕ²> = {disp2:.6f} rad²,  RMS ϕ = {math.sqrt(disp2):.4f} rad = "
      f"{math.sqrt(disp2)*180/np.pi*60:.2f} arcmin")

print("\n" + "="*72)
print("B. IDCM 候選對比")
print("="*72)
cands = [49.5, 50.0, 55.0]
print(f"理論 σ_lens = {sigma:.2f}")
for c in cands:
    print(f"  候選 {c}: 差 = {abs(c - sigma):.2f} ({'PASS' if abs(c-sigma) < 3 else 'FAIL'})")

print("\n" + "="*72)
print("C. 檢查: 如果 σ_lens 唔啱, 試其他 CAMB 單位解釋")
print("="*72)
# C_ϕϕ 標準 CAMB 單位: cable C_ϕϕ 係 (無單位 rad²) 但值通常 ~1e-8;
# 睇下我計到嘅 σ 有冇物理意義 (Planck lensing σ_lens ~ 0.3° = 40-60 in ℓ?)
print(f"  計到 σ_lens={sigma:.2f} — 期望 ~40-60 (Planck lensing 寬度)")
if 30 < sigma < 70:
    print("  ✅ σ_lens 量級正確")
else:
    print("  ⚠ 量級唔對, 檢查單位")

# 順便計 lensed power (用嚟做 forward 測試)
print("\n" + "="*72)
print("D. CAMB lensed TT 檢驗 (對照用)")
print("="*72)
pars2 = camb.CAMBparams()
pars2.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, mnu=0.06, omk=0, tau=0.0544)
pars2.InitPower.set_params(As=2.1e-9, ns=0.9649)
pars2.set_for_lmax(4000)
pars2.set_accuracy(AccuracyBoost=2)
# 計 lensed output — CAMB 2.0.1 用 get_cmb_power_spectra dict
pars2.WantScalars = True
res2 = camb.get_results(pars2)
specs2 = res2.get_cmb_power_spectra(lmax=4000, raw_cl=True)
lensed_cl = specs2['total']      # [TT, EE, BB, TE]
unlensed_cl = specs2['unlensed_total']
print(f"lensed_cl shape = {lensed_cl.shape}")
print(f"ℓ=2000 TT lensed: {lensed_cl[2000, 0]:.3e}, unlensed: {unlensed_cl[2000, 0]:.3e}")

# 獨立交叉檢驗: lensed/unlensed 峰谷平滑 — 用比值嘅高ℓ衰減估計 smoothing
# lensing 令峰谷對比 (peak/valley) 壓制, 用第一峰到高ℓ谷做係數
# 標準: C_lensed ≈ C_unl ⊗ Gauss(σ) → ratio D_l/D_u ≈ exp(-(ℓσ)²/2)? 唔係直接
# 更直接: lensed 峰谷 smooth 量 — 用 lensed TT spectrum 相對 unlensed 嘅
# "均方根平滑" 寬度: σ_est = sqrt( -2 ln(ratio起伏)/(ℓ²) )
ell2 = np.arange(len(lensed_cl))
# 攞最高幾個峰位 (CAMB 譜, 喺 ℓ>1409 冇 IDCM 峰 — 平滑 tail)
# 用 2000 附近 lensed/unlensed 比值斜率
mask = (ell2 > 1500) & (ell2 < 3000)
r_spec = lensed_cl[mask, 0] / unlensed_cl[mask, 0]  # lensed 通常 > unlensed 喺高ℓ阻尼?
# 平均平滑寬度: σ² = avg[ln(r)] / (ℓ(ℓ+1)/2) ... 粗糙
sig_est = np.sqrt(np.mean(2*np.log(np.clip(r_spec, 1e-3, None)) / (ell2[mask]*(ell2[mask]+1))))
print(f"lensed/unlensed ratio ℓ1500-3000: mean={r_spec.mean():.4f}, range=[{r_spec.min():.4f},{r_spec.max():.4f}]")
print(f"粗糙 σ_est = {sig_est:.2f}")

print("\n" + "="*72)
print("裁決")
print("="*72)
best = min(cands, key=lambda c: abs(c - sigma))
print(f"理論 σ_lens = {sigma:.2f} ≈ 候選 {best} {'✅ 一致' if abs(best-sigma)<5 else '❌ 唔一致'}")
sys.exit(0 if abs(best-sigma) < 5 else 1)