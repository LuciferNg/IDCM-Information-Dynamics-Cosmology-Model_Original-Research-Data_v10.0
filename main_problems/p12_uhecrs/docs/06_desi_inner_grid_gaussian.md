# 路線 2 精化 — CluMPR inner grid + Gaussian/exact p (2026-10-18)

> **P12 攻堅** · scripts: `22_desi_inner_grid_gaussian.py` + `23_desi_exact_binomial_validation.py`
> **數據**: CluMPR 2024 / DESI-Legacy DR9 光度星系團 (Yantovski-Barth+2023, Zenodo 8157751/10727242, 298,487 團)
> **來源**: P5 SESSION_START (2026-10-17) 交接建議:「CluMPR 3.0° p 改 Gaussian 估計 + 更密 inner grid」

---

## 一、動機

P5 script 17 (2026-10-17) Phase B: 3.0° z=4.22 但 **p_raw=0**（6000 次 MC 全部 obs<mean）→
Fisher5 用 clamp p=1/5001=2e-4（MC 解像度下限）→ z5=4.694σ。交接建議將 clamp 換成精確尾
估計，並加密 inner grid（0.25° step）確認真空核心氹形狀。

## 二、方法（唔改 P5 方法，只加統計精化）

- null: **scramble RA keep dec**（footprint-safe，P5 預註冊保守 null）；seed 42
- 22 號: radii 1.0–3.5 step 0.25 + 4.0/4.5/5.0 對照；N_MC=6000；float32 加速（0.083s/scan）
- Gaussianity 檢驗（KS + 經驗尾 vs norm.sf）先過關先准用 Gaussian p
- 23 號: **exact Binomial CDF**（Binom(N, p̂=MC_mean/N)，scipy boost 大 N 精確）— 唔靠 Gaussian 假設做 Gold Standard

## 三、結果

### 3.1 更密 inner grid（script 22，N_MC=6000）

| r(°) | obs | MC mean±sd | z_def | p_gauss | KS p |
|:----:|:---:|:----------:|:-----:|:-------:|:----:|
| 1.00 | 1142 | 1292.0±35.9 | 4.18 | 1.48e-5 | 0.281 |
| 1.25 | 1781 | 2010.4±43.8 | 5.23 | 8.3e-8 | 0.461 |
| 1.50 | 2582 | 2888.4±53.0 | 5.79 | 3.62e-9 | 0.500 |
| 1.75 | 3490 | 3928.3±62.5 | 7.01 | 1.18e-12 | 0.522 |
| **2.00** | **4600** | **5135.4±70.4** | **7.61** | **1.4e-14** | **0.452** |
| 2.25 | 5940 | 6514.0±78.2 | 7.34 | 1.11e-13 | 0.700 |
| 2.50 | 7527 | 8056.9±87.3 | 6.07 | 6.31e-10 | 0.367 |
| 2.75 | 9287 | 9764.2±96.0 | 4.97 | 3.31e-7 | 0.799 |
| 3.00 | 11199 | 11642.9±105.3 | 4.22 | 1.25e-5 | 0.802 |
| 3.25 | 13143 | 13688.0±114.4 | 4.76 | 9.5e-7 | 0.349 |
| 3.50 | 15395 | 15898.3±122.6 | 4.10 | 2.03e-5 | 0.773 |
| 4.00 | 20237 | 20817.1±137.2 | 4.23 | 1.18e-5 | 0.754 |
| 4.50 | 25688 | 26414.2±152.3 | 4.77 | 9.23e-7 | 0.731 |
| 5.00 | 31904 | 32661.2±165.7 | 4.57 | 2.43e-6 | 0.660 |

→ **真空核心氹形狀確認**: 1.0°→2.0° 單調增強（z 4.18→7.61），2.0°→5.0° 單調衰減。
**z=7.61 喺 r=2.0°（探索性最強點）**；儲備同 P5 Phase B z=7.72 一致（N_MC 同 seed 尾差）。

### 3.2 Gaussianity（判準: KS p>0.05 + 經驗尾≈norm.sf）

- 全 14 點 KS p ∈ [0.28, 0.80] — 冇任何點拒絕 Gaussian
- 2.0°: emp{2σ:0.024, 3σ:0.0012} vs Gaussian{0.0228, 0.00135} ✓
- 3.0°: emp{2σ:0.023, 3σ:0.0015} vs Gaussian{0.0228, 0.00135} ✓
- → Gaussian 尾估計合法

### 3.3 Exact Binomial Gold Standard（script 23）

| r(°) | p_exact (Binom CDF) | p_gauss (script 22) | z_exact | z_MC |
|:----:|:-------------------:|:-------------------:|:-------:|:----:|
| 1.75 | 3.91e-13 | 1.18e-12 | 7.16 | 7.01 |
| 2.00 | 9.2e-15 | 1.39e-14 | 7.66 | 7.61 |
| 2.25 | 1.55e-13 | 1.11e-13 | 7.29 | 7.34 |
| 2.50 | 7.57e-10 | 6.31e-10 | 6.04 | 6.07 |
| 3.00 | 1.242e-5 | 1.25e-5 | 4.216 | 4.216 |

→ **兩獨立方法一致（同 order 或更細）**；Gaussian 冇 systemically overstate。
3.0° 甚至估得略保守 (1.25e-5 vs 1.242e-5)。

## 四、Fisher5 更新（PSZ1/PSZ2/MCXC/Abell p 由 reverify_cluster_vacuum.json 提取）

| DESI p 來源 | p_DESI | Fisher5 χ² | p | z |
|:-----------|:------:|:----:|:-----:|:---:|
| clamp (P5, 2026-10-17) | 2.0e-4 | 46.17 | 1.34e-6 | 4.694σ |
| **exact@3.0（指定點）** | **1.242e-5** | **51.73** | **1.28e-7** | **5.153σ** |
| gauss@3.0（script 22） | 1.245e-5 | 51.72 | 1.29e-7 | 5.153σ |
| exact@2.0（探索性最強） | 9.2e-15 | 93.77 | 9.5e-16 | 7.947σ |

## 五、宣稱分級（誠實）

- 🟢 **正式宣稱 = exact@3.0°**: Fisher5 z=**5.153σ**。3.0° 係 P5 交接建議（10-17）**事前指定**嘅
  報告點，非掃描後揀出 → 無 look-elsewhere 懲罰。由 4.694σ（clamp 下限）升到 5.153σ ——
  clamp 低估咗 DESI 第 5 重嘅獨立顯著性。
- 🟡 **探索性提示 = r=2.0°**: z=7.66（exact）。呢個係 14 點掃描後取最強 → 有 trials 因素；
  唔可以做正式宣稱。但 7.66σ 即使計 look-elsewhere（~14 獨立 trials，Bonferroni z_eff =
  norm.isf(p×14) ≈ 7.2σ）仍遠超 5σ → 氹形狀（1.0→2.0 上升、2.0→5.0 衰減）係穩健結構特徵。
- 兩個獨立統計方法（MC-Gaussian 尾 + exact Binomial）完全一致 → **非 method artifact**。

## 六、局限

1. CluMPR = DESI-Legacy 光度團（非 DESI DR2 光譜）——已標籤更正；獨立第 5 族身份成立
   （Planck SZ×2 + MCXC X-ray + Abell 光學 之外嘅另一望遠鏡/方法/波長）
2. scramble-RA 保留 dec 嘅 null 已處理部分天區 footprint；全天均勻 null 唔啱用（見 P5 docs/08）
3. PSZ1/PSZ2 有部分重疊（已知）；MCXC/Abell/CluMPR 相互獨立
4. look-elsewhere 只影響「掃描最強點」宣稱，唔影響指定點 3.0°
5. p̂ 用 MC_mean/N（1 decimal round 後 micro error）；exact p 對 p̂ 誤差唔敏感（z 4-7 區間）

## 七、產物

- `scripts/22_desi_inner_grid_gaussian.py` — 更密 grid + Gaussianity + 三版 Fisher5
- `scripts/23_desi_exact_binomial_validation.py` — exact Binomial Gold Standard
- `data/reverify_desi_inner_grid.json` — script 22 輸出
- `data/reverify_desi_exact_p.json` — script 23 輸出（權威 p 值表）

*P12 路線 2 精化 · 2026-10-18*