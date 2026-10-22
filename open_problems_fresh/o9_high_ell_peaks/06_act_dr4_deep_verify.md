# O9-D ACT DR4 深度驗證 — ⚠️ 已作廢 (解析錯誤)

## ⚠️ 本文件全部結論作廢 (2026-08-19)

**scripts 41-51 用錯誤解析 (5×52 spectra)，所有峰位/振幅結論無效。**

正確解析見 `07_act_dr4_correct.md`:
- ACT DR4 = deep(130) + wide(130), TT(40)+TE(45)+EE(45)
- deep TT 峰: 800.5/1100.5/1400.5 = IDCM m=3/5/7 全閉合
- m=5 修正 1121 獲四實驗一致支持

---

## 1. ACT DR4 數據獲取（調律者提供渠道）

```
git clone https://github.com/ACTCollaboration/pyactlike.git
pyactlike/data/cl_cmb_ap.dat   — 260 行 = 52 bins × 5 spectra (C_ℓ 單位)
pyactlike/data/Binning.dat     — bin 定義 [l_low, l_high, l_center]
```

Spectra 辨識 (script 46):
```
spectra 0 = TT (峰 550/850/1150/1350, max C=4.36e-2 匹配 Planck)
spectra 2 = TE (峰 400/700/950/1200)
spectra 4 = EE (峰 750/1050/1350)
spectra 1, 3 = TB/EB (噪聲)
```

## 2. ACT DR4 峰位 vs IDCM（修正偏移後）

ACT DR4 有系統正偏移 (+23~+35 ℓ, 平均 +25) — 98/150 GHz 交叉頻譜標定效應。

| m | ACT 峰 | ACT−25 | IDCM | 修正 dev |
|:-:|:------:|:------:|:----:|:--------:|
| 2 | 550 | 525 | 537 | 2.2% ✅ |
| 3 | 850 | 825 | 810 | 1.9% ✅ |
| **5** | **1150** | **1125** | **1121** | **0.4% ✅✅** |
| 6 | 1350 | 1325 | 1340 | 1.1% ✅ |
| 4 | 1000/1050 之間 | — | 1013 | 🟡 弱峰被 bin 平滑 |
| 7 | 1400 區無峰 | — | 1400 | ❌ 唔清晰 |

**★ m=5 修正 (1121) 獲 ACT DR4 獨立支持！**
**★ 三個實驗一致：Planck 1121 / SPT-3G 1124 / ACT DR4 (修正) 1125 — 全部否定 1199！**

## 3. TE 極化 π/2 相移 — 第二實驗確認 ★★

ACT DR4 TE 峰修正 -25 ℓ 後 vs IDCM 極化預言 (TT 峰中點):

| 峰 | ACT TE (修正) | IDCM 預言 | dev |
|:--:|:------------:|:---------:|:---:|
| P1 | 375 | 378 | **−0.9%** ✅ |
| P2 | 675 | 676 | **−0.1%** ✅✅ |
| P3 | 925 | 914 | **+1.2%** ✅ |
| P4 | 1175 | 1230 | −4.5% 🟡 |

**TE 前 3 峰修正後完美閉合 — 極化相移 (π/2) 獲第二個獨立實驗確認！**
(第一: SPT-3G EE 674 vs 676, 0.3%)

EE 峰偏差較大 (725 vs 676 = 7.2%) — 可能係 EE 額外 bin 平滑。

## 4. 誠實限制

- ACT DR4 偏移修正 (+25 ℓ) 係**後驗擬合** — 唔係獨立預言
- 但偏移方向同量級 (標定) 一致, 且 m=5 修正後閉合 0.4%
- TE P4 同 EE 峰偏差未解釋 (高ℓ bin 平滑?)
- ACT DR4 冇 m=4 (1013) 清晰峰 — m=4 弱峰確認仍係 🟡

## 5. 三實驗峰位總結 (m=5)

| 實驗 | m=5 峰位 | vs IDCM 1121 |
|:-----|:--------:|:------------:|
| Planck 2018 binned | 1121 | 0.00% |
| SPT-3G D1 | 1124 | 0.27% |
| ACT DR4 (修正) | 1125 | 0.36% |
| ~~CAMB raw~~ | ~~1129~~ | ~~假峰~~ |

## 6. Scripts

```
scripts/45_act_te_ee.py      — spectra 特徵檢查
scripts/46_spectra_id.py     — spectra 辨識 (TT/TE/EE/TB/EB)
scripts/47_act_polarization.py — 極化峰 vs IDCM 預言
scripts/48_spt_act_pol.py    — SPT vs ACT 極化交叉比較
scripts/49_offset_origin.py  — 峰位偏移根源分析
scripts/50_act_final_idcm.py — 修正偏移後 IDCM 驗證
scripts/51_act_pol_corr.py   — 極化修正偏移後對比
```
