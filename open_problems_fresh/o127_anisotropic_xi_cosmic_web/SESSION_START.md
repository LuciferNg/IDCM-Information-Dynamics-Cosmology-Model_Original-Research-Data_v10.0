# O127 — 宇宙網各向異性 ξ(s)

> **Session**: 2026-09-26（v10.0 重建攻堅）
> **狀態**: 🟡 **部分閉合**（BAO 尺度子命題 🟢 零參數閉合）
> **來源**: v9.0 項目審計後發現不屬於 v10.0 O1-O114 任何現有系列
> **v10.0 位置**: `IDCM-v10.0--It-From-Beat/open_problems_fresh/o127_anisotropic_xi_cosmic_web/`
> **v9.0 來源**: `open_problems_fresh/kchain_cosmic_web/anisotropic_xi/`

## 問題

見 `docs/01_problem_record.md`

## 結論（先行）

1. **🟢 BAO 尺度零參數閉合** — `r_d = λ_sync/2 = πR_world/88 = 147.4386 Mpc`
   對 eBOSS DR16 LRG（−0.231%）+ DESI DR2（−0.27σ）兩個獨立數據集。
2. **🟡 ξ₂ 各向異性結構源頭** — 由紅移-距離律第一性推導 kernel `K(z) = (dD/dℓ)/(c ln4)`
   （禁 Kaiser ✅）；但 `z<1.5` `|R−1| < 3.8%` ⟹ LRG 結構上無法鑑別。
3. **🔴 v9.0 三偽影證偽** — 203 h⁻¹Mpc（÷h 換算錯）、18/18 諧波檢測（幾何必然）、阻抗反射 R_n（全正）。

## 交付物

| 檔 | 內容 |
|---|---|
| `docs/01_problem_record.md` | 問題記錄 + 推導時序索引 |
| `docs/02_p1_bao_position_null.md` | P1: BAO 尺度 + 諧波 null（11/11） |
| `docs/03_p2_xi2_structural_source.md` | P2: ξ₂ RSD kernel 推導（8/8） |
| `docs/04_p3_desi_dr2_blindtest.md` | P3: DESI DR2 盲測（3/3） |
| `docs/05_p4_density_baseline.md` | P4: 密度基準 + 獨立核對（11/11） |
| `docs/06_conclusion.md` | 總結裁定 + 4 Hard Tests |
| `RESULT.md` | O-series 結論摘要 |
| `scripts/01–05` | 全部可重跑，PASS |
| `data/raw/` | eBOSS ξ data vector + model + LRG catalogs（官方） |

## 前置

O76 (z 紅移翻譯) 🟢, O51 (群延遲修正) 🟢, O100 (C_ℓ→P(k)) 🟢, O73/O167/O169/O170/O213 🟢

## 遺留

1. O51 推導時序審計（確認 `λ_sync`/`r_d` 係真盲測預言）
2. IDCM 速度場 growth 因子（完整 ξ₂ 振幅）
3. Lyα ξ₂ (z=2.33) DESI DR2 full-shape
4. eBOSS 目錄自算 ξ(s) 交叉核對（catalogs 已下載）

---

## ⚠️ O126 交回 (2026-09-27) — 待本 O 重驗

> **來源**: O126 (runtime ISA 攻堅), `o126_runtime_isa_verification/docs/05_remaining_gaps_closure.md` §D + `docs/02_v9_to_v10_verification.md` (L55/66)
> **用戶指示**: O126 側**未改動本 O 任何檔案**；現列與本 O 相關之裁決 + 重驗要求，由本 O session 自行執行。
> **狀態**: [ ] 未重驗

### ① O126 之相關裁決

O126 判 v9.0 **sync dip (`z_c = 0.6`) 🔴 撤回** (v9.0 膨脹偽影; 見 O126 docs/05 §D)。
O126 `docs/02` L55/66 將「z = 0.6 同步轉折」歸屬 **O127/O129**。

### ② 本 O 重驗要求

1. 本 O `docs/06` 已**證偽**「阻抗反射 `R_n` 產生各向異性」(`R_n` 全正, `Z_n` 單調) ——
   確認此證偽同 O126 §D 之撤回**一致** (即本 O 無殘留 v9.0 sync dip 機制)。
2. 本 O `docs/03` L47: `R(z)` 非單調, 喺 `z ≈ 0.7` 有極小 —— 檢視呢個 `z ≈ 0.7` 特徵係咪
   v9.0 sync dip 之殘留, 需否同 O126 §D (`z = 0.6` 撤回) 對齊措辭。
3. 確認本 O 全文**無** `z = 0.6` dip 之正面聲稱; 若有 → 應標 🔴 撤回。

### ③ 交回

由本 O (O127) session 自行重驗 + 寫入; O126 側不代改。
