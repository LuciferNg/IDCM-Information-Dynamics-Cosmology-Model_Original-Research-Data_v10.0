# O254 docs/04 — 全面審計報告（2026-10-20 R3）

> 性質: 審計（verify & audit O254 資料夾所有數字及資料）
> 方法: 重跑 determinism + 獨立重算 + AST 空 check 掃描 + 文獻反查 + records 交叉核對
> 結果: **數字全部真確；3 項記錄問題已修正（見下）**

## 一、執行摘要

| 項目 | 結果 |
|:-----|:-----|
| 重跑全部 scripts ×3 | ✅ **DETERMINISM: STABLE**（logs/data hash 前後一致） |
| 獨立重算核心數字 ×15 | ✅ 全部 PASS（dev 0.0000%） |
| AST 空 check 掃描 | 🔴 發現 3 個 vacuous → **已修正清零** |
| 文獻 ref 反查 ×8 | 🔴 發現 2 處引用錯 → **已修正** |
| docs/data/logs 交叉 | 🔴 data/01 conclusion stale → **已修** |
| README/register/01_record 一致性 | ✅ 已核（數字一致，PASS 數已同步） |

## 二、scripts 重跑 determinism ✅

`scripts/01` (8/8), `scripts/02` (4/4), `scripts/03` (3 assert)——重跑後 logs/data sha256 前後一致，exit 0 ×3。

## 三、獨立重算（零依賴 scripts 邏輯）✅

用 SI 基本常數獨立重推 15 項數據，全部 dev 0.0000%：
E_ph, ω_ring rad/s, E_q_ring, E_Pl, E_coherent, N_ph/mJ, UHECR×2, Λ₀, E_vac_world, resp_mJ×2, 1m_hops, earth_hops。

**附加發現（已修）**：`N_IDCM` 用 register 3-sig 值 7.88e60 令 E3a「恆等」dev 0.06%；改用結構定義 N_exact = 1/(ω_ring·t_Pl) = **7.884689e60** ⟹ dev 0.000000%（真正恆等，E3a 驗證意義升級）。

## 四、AST 空 check 掃描（🔴→✅ 修正）

**verify-all-system 明文反模式：`chk(..., True)` 自證 PASS，proves nothing。**

修正前：
- `scripts/01`: **E2**（`chk("E2", True, ...)`）、**E6**（`chk("E6", True, ...)`）→ 聲稱 8/8，實質 6 個真 check
- `scripts/02`: **C4**（`chk("C4", True, ...)`）；C3 係 hardcoded const compare（`dim_bz_crystal != 1` 永恒 True）→ 聲稱 5/5，實質 3 個真 check + 2 偽

修正後：
- `scripts/01` E2 → 真比較 `E_q_ring < E_ph`；E6 → 真比較 `E_uhecr_2 < 1e40 < E_vac_world`（1e40 落喺兩錨之間 = 冇結構身份）
- `scripts/02` C3 → **降為報告行**（定性結構論證，冇獨立數值判據，誠實唔計 PASS）；C4 → 複合真條件 `E_coherent/E_mJ > 1e10`（獨立重算 path）
- **AST 復檢: 三 script vacuous=[] const-compare=[]，總計 0**
- **誠實 recount: scripts/01 8/8 全真；scripts/02 5/5 → 4/4**。全部 docs/README/register 已同步更正（append 標記「審計更正 5/5→4/4」）

## 五、文獻 ref 反查（🔴→✅ 修正）

用 web_search 逐條反查 docs/02 引用（8 條關鍵 ref）：

| Ref | 反查結果 |
|:----|:---------|
| Süsstrunk & Huber, Science 349:47-50 (2015) | ✅ 真（DASH PDF 證實） |
| Wang, Lu & Bertoldi, PRL 115:104302 (2015) | ✅ 真（bulk Chern 1,2） |
| ~~He et al., PRApplied 10:014017 (2018)~~ | 🔴 **作者錯** → **Ge et al.**（arXiv:1803.00828, Hao Ge 第一作者） |
| Zhang et al., Comms Physics 1:97 (2018) | ✅ 真 |
| Xu et al., PRApplied 19:034062 (2023) | ✅ 真（Jiachao Xu 第一作者） |
| Wächtler & Platero, PRR 5:023021 (2023) | ✅ 真（= arXiv:2208.01061） |
| ~~Liu et al., Sci. Adv. 11:eady5649 (2025)~~ | 🔴 **張冠李戴** → eady5649 係 **Li et al. 單一 vdP 振子**；兩振子同步實為 **Liu et al. arXiv:2509.18423** |
| Ghosh, arXiv:2502.13814 (BaMnSb₂) | ✅ 真 |

已修正 docs/02 三處（Ge/He + 2025 行拆兩條 + 附錄）。**結論不受影響**（全部 ref 都係「同一耦合系統內」，O254 否證結論不變）。

## 六、records 交叉核對 ✅

- README O254 行數字（1.6e4 / 1.96e9 / 5.2e69 / 4.84e-24 / 0.062%）vs data ✅ 一致
- register notes（R1/R2 + 交回 P14 ×2）vs docs ✅ 一致
- SESSION_START / 01_problem_record 冇舊值残留（1.955 / 1.23e10 / 7.88e60 已清除）
- register check: O254 唔喺任何 drift 列（STATUS-DRIFT/REF-MISSING/BLOCK-DRIFT/SEED-DISAGREE）

## 七、審計後遺留（已知、唔阻結論）

1. `scripts/02` C3 降報告行 ⟹ 否證文件「三層論證」中「定義域」層由數值 check 變定性論證——結論唔變，但強度由「PASS」降為「結構性陳述」（文件已在 reports 標明）
2. docs/02 附錄有行「檢索工具經 web_search（keyless tier），引用前應以官方 DOI 頁複核」——已遵守，經官方 arXiv/APS/Science 頁反查
3. E_coherent 數值由 1.9549e9 → **1.9561e9**（N 精確化），docs/01/03/README 已同步

## 八、結論

**O254 所有數字及資料：審計通過**（全部可重現、獨立重算一致、ref 真確）。過程發現 3 類記錄問題（空 check、ref 錯、stale 值）已全數修正並 append 標記，無改寫任何已 commit 結論。**O254 verdict 維持: 否證 🔴（「晶體=宇宙電話」假說）**。