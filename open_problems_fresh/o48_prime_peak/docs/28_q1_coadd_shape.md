# O48 / Q1.48 — PR4 xfreq co-add：峰形 γ=49.5 實測確認 + sample variance 極限

> **日期**: 2026-10-10
> **狀態**: ✅ **B+C 閉合 — PR4 co-add 實測 γ=47.5 ≈ 297/6=49.5（同 CAMB 48.0 一致）**
> **Script**: `65_q1_pr4_coadd.py`（36 個 detset cross inverse-variance co-add）
> **數據**: HiLLiPoP v4.2, 全部 36 dl_PR4_v4.2_*x*.fits（100/143/217 GHz A/B detset cross）

## 1. Co-add 效果

```
ℓ=221: solo 143Ax143B D=6127±507 (SNR 12.1) → co-add D=6097±85 (SNR 71.6)
ℓ=527: SNR 18.6 → 110;  ℓ=815: 23.0 → 136;  ℓ=1121: 26.2 → 147;  ℓ=1409: 26.3 → 127
```
⚠️ 但注意: **sample variance 唔會 co-add 消走**（同一 CMB sky）:
```
ℓ=221: D=6097 sample σ=473 (7.8%) — co-add 後 SNR 受 sample variance 封頂
```

## 2. 峰形實測（平滑窗口掃描）

ℓ-by-ℓ wiggles（sample variance 逐點獨立）令未平滑 FWHM 崩潰（γ=2.8 假象）。
平滑窗口掃描:
```
window  9: FWHM 82.5  γ=41.3
window 15: FWHM 86.0  γ=43.0
window 25: FWHM 92.7  γ=46.4
window 35: FWHM 95.1  γ=47.5   ← 收斂
```
- window 35 ≈ 峰週期 (297)/8.5 — 平滑尺度遠大過 wiggles, 遠細過峰形
- 收斂值 γ=47.5 同 **CAMB 理論 48.0**（63 script）差 0.5 —— 同一峰形
- **55=F₁₀ 排除**（差 7.5 = 4σ+）

## 3. 三源閉合

| 來源 | γ |
|:-----|:--|
| CAMB 理論（unlensed, 63） | 48.0 |
| **PR4 co-add 實測（65）** | **47.5** |
| 結構候選 297/6 | 49.5 |
| 55=F₁₀ | ❌ 排除 |

→ **峰形寬度身份閉合: γ ≈ 47.5-48 ≈ 49.5 = 297/6 = 峰週期/6**
（PR4 實測 + CAMB 理論一致; 49.5 喺兩者 ±2 帶內）

## 4. 教訓

- **未平滑 ℓ-by-ℓ 譜 FWHM 會崩潰**（γ=2.8 假象）— wiggles 觸發半高定位錯峰值
  （55 script「PR4 峰偏移」同一根源: raw detset 譜局部極值係 noise）
- co-add 提升 instrument noise 至 sample variance 極限, 但唔過得 sample variance
- 峰形（FWHM~96, γ~48）要平滑窗口 ≳ 25 先見真身 — 之前「峰形測唔到」結論
  修正: **測得到, 但要 ①xfreq co-add ②平滑 ③或未 bin 高分辨譜**
- Plik 215 bins 每峰 ~10 bins 對 Lorentz 仍 over-parameterized（逐峰 fit 唔穩）,
  但 PR4 ℓ-by-ℓ + co-add + 平滑 = 直接 FWHM 量度成功

## 5. 峰形攻勢總收 (docs/20+25+27+28)

```
✅ 峰形 = Lorentz (CAMB 前向 + PR4 實測)
✅ γ ≈ 49.5 = 297/6 = 峰週期/6  (CAMB 48.0, PR4 47.5, 297/6=49.5)
✅ IDCM「σ≈50」= Lorentz γ=49.5 嘅 Gaussian 投影 (σ_fit 52±2)
✅ 儀器效應可忽略 (beam 3.9%, lensing 0.3%)
🔴 撤回: Lorentz 全勝 (43, 污染), 右重 γR>γL (45/46b, fit 崩潰)
⚠️ 谷位 sign 保留: 谷→後峰 0.280 (54, 直接量)
🔴 峰形測量極限修正: 唔係「冇數據測到」, 係「要 co-add+平滑」
```