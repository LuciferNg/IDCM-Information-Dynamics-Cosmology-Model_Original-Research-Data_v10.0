# O127 — 宇宙網各向異性 ξ(s)

> **創建日期**: 2026-08-29
> **狀態**: 🔴 未開始
> **來源**: v9.0 項目審計 — `open_problems_fresh/kchain_cosmic_web/anisotropic_xi/`
> **前置**: O76 (z 紅移翻譯) 🟢, O51 (群延遲修正) 🟢, O100 (C_ℓ→P(k)) 🟢
> **定位**: 從 v9.0 anisotropic_xi/ 遷移 — K_Chain 投影的宇宙網各向異性相關函數分析

---

## 一、問題

從 v9.0 anisotropic_xi/ 遷移 — K_Chain 投影的宇宙網各向異性相關函數分析

## 二、假設

1. v9.0 推導在 v10.0 非膨脹框架中部分或全部有效
2. 需要驗證的關鍵假設：
   - 是否依賴膨脹宇宙假設？
   - 是否使用 v9.0 已 demote 的參數（如 ζ(z)）？
   - 是否與 v10.0 已閉合結果（O76, O100, O51 等）一致？

## 三、驗證步驟

### 步驟 1：讀取 v9.0 原始推導
- 路徑: `open_problems_fresh/kchain_cosmic_web/anisotropic_xi/`
- 目標: 提取所有公式和數值

### 步驟 2：識別 v9.0 特有假設
- 列出所有依賴膨脹宇宙的假設
- 列出所有使用 v9.0 demote 參數的公式

### 步驟 3：在 v10.0 框架中重新驗證
- 用 v10.0 的 idcm_core.py 常數重新計算
- 與 v10.0 已閉合結果交叉驗證

### 步驟 4：遷移或重建
- 如果 v9.0 推導有效 → 遷移到 v10.0
- 如果 v9.0 推導失效 → 建立新推導

## 四、已知 v9.0 參考文件

- `open_problems_fresh/kchain_cosmic_web/anisotropic_xi/`

## 五、開放問題

1. v9.0 推導是否在 v10.0 中有效？
2. 是否需要修正以適應非膨脹框架？
3. 與 O1-O121 中已閉合結果的關係？

---

## 六、推導時序索引（2026-09-26 攻堅，禁回溯污染）

> 本節只**追加**記錄，唔改寫上面已凍結嘅問題記錄。全部腳本 `scripts/01–05`。

| 序 | 動作 | 產出 | 時間 |
|---|---|---|---|
| 0 | v9.0 源頭審計（`kchain_cosmic_web/anisotropic_xi/` 42/43/44 + scripts 45–72） | 無有效正面閉合；三偽影 | 本 session 早段 |
| 1 | `scripts/01_data_audit.py` — eBOSS 官方 ξ data vector 核對 + h 單位審計 | `data/verify/01_data_audit.log` | — |
| 2 | `scripts/02_bao_position_and_harmonic_null.py` — P1a BAO 尺度 α-fit + P1b 諧波 null | `docs/02`, `data/02_results.json`, 11/11 | — |
| 3 | `scripts/03_xi2_structural_derivation.py` — P2 RSD kernel 第一性推導 | `docs/03`, `data/03_results.json`, 8/8 | — |
| 4 | `scripts/04_desi_dr2_blindtest.py` — P3 DESI DR2 out-of-sample 盲測 | `docs/04`, `data/04_results.json`, 3/3 | — |
| 5 | `scripts/05_density_baseline_audit.py` — P4 密度基準 + 獨立核對 + v9.0 錯誤重建 | `docs/05`, 11/11 | — |
| 6 | `docs/06_conclusion.md` + `RESULT.md` — 總結裁定 | 本 O 閉合 | — |

### 數據來源（全部官方原始，含 cov）
- eBOSS DR16 LRG ξ(s) data vector + BAO model：`data/raw/Data_LRGxi_NGCSGC_0.6z1.0_{pre,post}recon.txt`
  （`svn.sdss.org/public/data/eboss/DR16cosmo/tags/v1_0_1/dataveccov/lrg_elg_qso/LRG_xi/`）
- eBOSS DR16 LRG catalogs（data+randoms, 4 FITS）：`data/raw/eBOSS_LRG_clustering_*.fits`（未用於本輪，留作自算 ξ 交叉核對）
- DESI DR2 BAO：arXiv:2503.14738（7 tracers, r_d^fid = 147.05 Mpc）

### 狀態變更
`🔴 未開始` → **`🟡 部分閉合`**（BAO 尺度子命題 🟢 零參數閉合）

