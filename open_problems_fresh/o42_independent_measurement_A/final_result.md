# O42 — 冷斑 A 獨立量度方案 (Independent Measurement of Cold Spot Amplitude)

## 狀態: 🟢 已閉合 (2026-08-25) — A = 134.2 μK 六方法獨立量度確認 + 本徵尺度閉合

## 結論
O41 結構公式 A = 88×61/40 = 134.2 μK 由 4 種獨立組份分離方法 × 6 個產品一致量度確認
(mean −133.80, std 0.99 μK, spread 3.02 μK, max dev 1.75%)；冷斑本徵直徑 8.66° ≈ 2×R8，
T-E 偏振正常（溫度-only 結構），ISW 解釋唔到冷斑（rms 0.56 μK）→ 支持 IDCM 零暗能量。

## 關鍵公式
- A = Σγ_odd(Σγ_even − L₇)/40 = 88×61/40 = 134.2 μK (O41, 零參數)
  - 61 = Σγ_even − L₇ = 90 − 29 (世界能量 − Lucas₇) = ⟨W⟩² − log₄2 = 61.5 − 0.5
  - 40 = 端點數 (O7 C 結構保證)
- 六方法量度: SMICA −134.19 / NILC −134.09 / Commander −133.32 / SEVEM_final −134.47 /
  SEVEM_143 −134.87 / SEVEM_217 −131.85 μK
- 冷斑本徵尺度: σ_fit=4.08° (χ²=0.4) → 去卷積 (σ_kernel=1.771°) → σ_intrinsic=3.68°
  → 本徵 FWHM 8.66° ≈ 2×R8 = 8.34° (偏差 3.7%), Planck 2013 直徑 ~10°
- SMHW: 冷斑 rank 1-2/60, 全天空 percentile 0.4-2.5%, kurtosis +0.11 (Cruz 2005 方向)
- T-E 偏振: 冷斑 |P|=0.55 μK, 60 節點 z=+0.2σ → 冇偏振異常
- 徑向剖面: 中心 −134.2 μK (=A), 回升 8.2°

## 依賴
O41 → O42 → (O5/O7 前置數據) → 延伸: 本徵尺度/T-E/ISW
(O41 真空能=觀察者預算 → O42 獨立量度 → 未來 O: E/B 分解偏振、DESI ISW)

## 審計
- scripts/06_verify.py: 20/20 PASS (2026-08-25, 2026-09-12 遷移後重驗)
- scripts/10_final_audit.py: 51/51 PASS (2026-08-25, 2026-09-12 遷移後重驗)
- 推導時序索引: 01_problem_record.md §〇 (13 步, 2026-08-25 建立)
- ⚠️ v1 量綱錯誤已修正: R8=4.17° 係 FWHM (唔係 σ), 本徵閉合用 2×R8
- 🟡 未閉合: SMHW 係數→pixel 完整換算、E/B 分解偏振、DESI Eridanus ISW (2026+)
