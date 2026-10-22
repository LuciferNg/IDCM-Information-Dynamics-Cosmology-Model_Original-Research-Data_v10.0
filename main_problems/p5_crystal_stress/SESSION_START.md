# crystal_stress — Session Handoff (下一 session 交接)

> **交接日期**: 2026-09-27 (原 2026-09-13)
> **狀態**: 🟢 UHECR 主體閉合 + **全量重驗完成** (2026-09-27) — 路線 2+3 已執行
> (2026-10-17, 見 §2026-10-17 執行)；剩餘路線 1/4 + P9′ 等數據
> LRD 已獨立 (09-13)；UHECR 詳細已分拆 (09-27)；O169 修正點已重驗 ✅

## 已完成 (本項目)

1. **GZK = Nyquist 閉合** — E_GZK = hc/(L_P·φ⁴⁴) = 4.891e19 eV (2.18%) ✅ 重驗
2. **Oh-My-God 上限閉合** — E_max = 4φ·E_GZK = 3.166e20 eV (1.08%) ✅ 重驗
3. **Auger 各向異性** — 6 能量層 Fisher 2.66σ / 能量加權 Fisher 3.99σ (109 events) ✅ 重驗
4. **星系團節點核心真空** — 4 目錄 Fisher **3.43σ** ✅ 重驗 (4 目錄重新下載)
5. **雙重對稱性分裂** — 星系團避開 ↔ LRD 聚集 **3.6σ** (LRD 側已獨立)
6. **master verification 45/45 PASS** (T1-T45)
7. **全量重驗 (2026-09-27)** — scripts/10-15, 見 §重驗結果

## 重驗結果 (2026-09-27)

| 劇本 | 內容 | 結果 |
|:-----|:-----|:----:|
| 02 | O169 伸長律修正 (#17) | 6/6 🟢 |
| 10 | UHECR 能量尺度 | 8/8 🟢 |
| 11 | Auger 各向異性 | 全部一致 🟢 |
| 12 | 星系團節點真空 (重新下載) | 全部一致 🟢 |
| 13 | 譜結構 + LRD 標度 | 18/18 🟢 |
| 14 | 偏振/GRB/盲測 | 7/9 🟡 (盲測功效表不自洽) |

- **方法學 🟡**: §2.5 能量加權 Fisher (3.99σ) 係 ad hoc 加權統計量，標準 Fisher (2.66σ) 為保守值。
- **盲測功效 🟡**: 文檔「20→3.1σ, 50→5.2σ」不自洽 (z 比 1.677 ≠ √2.5)；自洽值雙比例 3.07σ/4.86σ。
- 詳見 `01_problem_record.md` (root)/`docs/04`/`docs/06` 底部「重驗註記」。

## 未完成 / 移交 (下一 session)

- [ ] **路線 1**: CMB 偏振宇稱違反 — 文獻檢驗完成 🟡, 等 CMB-S4/SO 偏振數據
- [x] **路線 2**: DESI 星系團確認 (第 5 重) — **已執行 2026-10-17** (CluMPR 2024, Fisher5=4.69σ; ⚠ 非光譜 DR2, 見 §2026-10-17)
- [x] **路線 3**: 盲測 — **第一輪已執行 2026-10-17** (4 事件 P0/P1/P2 全中, 功效表已修正; N<20 唔達否證門檻, 見 §2026-10-17)
- [ ] **P9′**: 節點級 UHECR 源模型 — 等 AugerPrime >5σ (2035)

## 工作目錄

`main_problems/p5_crystal_stress/` — root `01_problem_record.md` + `docs/` (04_master_summary,
06_gemini, 07_o169_correction_reverify) + `scripts/` (00/01 歷史 + 02, 10-15 重驗) +
`data/` (重驗輸出) + `final_result.md` + 本文件。

> 2026-09-27: `records/` 更名為 `docs/`。

## 相關項目

- **小紅點 (LRD) 已獨立** → `main_problems/p11_little_red_dots/` (2026-09-13 分家)
- **UHECR 詳細已分拆** → `main_problems/p12_uhecrs/` (2026-09-27 分家；scripts 01-21, data/, records/)

## 判準提醒

- 零新常數 / 結構強逼唯一解 / 沙漠審計 (O166 四步法)
- 反秘數 (O165): 半整數重開只適用雙向通道
- 時序潔癖: 新發現 append, 唔改舊結論
- scripts/00/01 為歷史，不修改；重驗一律新劇本 (10-15)

---

## ✅ O169 修正點 (2026-09-15) — 已重驗 (2026-09-27)

**修正點** (上游 O169):

- 伸長定律 `E = 1 + 2φ⁻¹ℓ` **已證偽** (DESI DR2 D_M×6 排除 4.88σ) → `E(ℓ) = ℓ + 1.11911398` (= ⟨γ⟩_odd/2·ℓ + 1/⟨v_g⟩_{1..22}); `δ(ℓ) = −φ⁻³(ℓ−1/2)`, `C = 1−2φ⁻¹ = −(√5−2)`

**問題** (本 O 受影響點):

- `docs/04_master_summary.md:184` — #17 D_app/N(z) 互補

**狀態**: [x] 已重驗 (2026-09-27) → `docs/07_o169_correction_reverify.md`

**重驗結果:** #17 新閉合形式 `D_app/R_H + 4^{-ℓ} = 1 + (1−4^{-ℓ})·(ℓ + 0.11911398)`
(0.11911398 = 1/⟨v_g⟩_{1..22} − 1); 互補結構 (ℓ=0→1、單一算子 P=4^{-ℓ}) 不變;
`scripts/02_o169_correction_reverify.py` 6/6 PASS。舊記錄未改寫 (時序潔癖), 只加新 doc。

---

## 2026-10-17 — 路線 2+3 執行 (詳見 `docs/08_routes_2_3_execution.md`)

### 路線 3: 盲測第一輪 (scripts/18_blind_test_execute.py) ✅
- 4 個 E>150 EeV 事件 (公開 Auger SD 目錄): **P0/P1/P2 方向全中** —
  median d_node = 7.73° (<9.6° 預報); 8° 內 3/4 (null 31.4%); 10° 內 3/4 (null 47.6%)。
- 二項檢定: P1 p=0.095, P2 p=0.277 (N=4 功效極低) → **預註冊維持, 等 AugerPrime N≥20**。
- **功效表修正**: 舊「20→3.1σ, 50→5.2σ」唔自洽; 雙比例 N=20→3.07σ, N=50→4.86σ,
  **N_for_5σ=53** (≈5.3yr @10/yr); 單比例 N=20→4.20σ, N=50→6.64σ, N_for_5σ=29。
- 輸出: `data/reverify_blind_test.json`。

### 路線 2: DESI 第 5 重節點核心真空 (scripts/17_desi_dr2_vacuum.py v2) ✅
- ⚠️ **數據源更正**: DESI DR2 (光譜) 無官方星系團 VAC → 用 CluMPR 2024
  (DESI-Legacy DR9 光度, Zenodo 10727242, 298,487 團) 作獨立第 5 族。
- null = scramble RA keep dec (footprint-safe; 全天均勻 null 演示 footprint artifact)。
- **節點核心真空單調衰減**: 2.5° z=6.04σ (Phase B) → 4.5° z=4.93σ → 8.5° 轉正 (z=+2.08)。
- **Fisher5 = 4.69σ** (p_DESI clamp 2.0e-4; Fisher4 重現 3.431σ)。
- 輸出: `data/reverify_desi_dr2.json` + `data/_desi_clusters_2024_simple.fits` (留碟)。

### 路線 1+4 預註冊 (2026-10-17, scripts/19 + docs/09) ✅
- **路線 1 (CMB 偏振宇稱)**: 32 阻挫邊 edge-band HEALPix mask 凍結
  (Nside=128, r_band=2.0°, control area-matched; band=8.73% 天空) —
  ★ 邊長全部等長 26.09°。預言 ~1e-5 rad 旋轉; 等 CMB-S4/SO (mask 到埗即測)。
  輸出: `data/edge_band_mask_20261017.json` + `.npz`。
- **路線 4 (Euclid 60 節點)**: 歸屬 = P5 (60 節點 = A5 crystal nodes 核心物件;
  cold-spot O-series lineage cross-ref; 最終確認留用戶)。規格 = script 17 同款
  (scramble-RA null, radii 2.5-8.5°, Fisher6)。等 **Euclid DR1 (2026-11-12)** —
  Q1 (~98 deg²) 太細。

### DESI Phase C (v3 追加) ✅
- 內層 1.0-2.0°: **r<2.0° z=7.72σ** (最強); 1.5°→5.83σ; 1.0°→4.14σ。
  真空核心氹: 2.0-2.5° 峰值區域。Gaussian p (norm.sf(7.72))≈6e-15 僅上限參考;
  主要報導維持 clamp p=2e-4 → Fisher5=4.69σ 不變。

### 剩餘
- 全部路線 1-4 + P9′: 狀態見 docs/09 總結表 — 唯一實質等待係外部數據
  (CMB-S4/SO, Euclid DR1 2026-11-12, AugerPrime 2035)。無內部可推。
- scripts 17/18/19 未加入 scripts/15 全量重驗 harness (執行型, 計算重);
  docs/08 + docs/09 為權威記錄。
- 建議 (p12 專屬 session 交接): CluMPR 3.0° p 改 Gaussian 估計 + 更密 inner grid 係
  「確認性」工作, 已 clamp 保守報導, 唔影響 4.69σ 結論。
- register: P5 (P 系列) 唔喺 register 範圍 (O-series only) — 唔註冊, 「P5」slug
  碰撞僅影響日後若開 O 系列同名時 (建議新 O 號)。
