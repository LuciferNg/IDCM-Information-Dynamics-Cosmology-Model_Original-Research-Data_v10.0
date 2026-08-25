# O75 — 命名規範統一 (Naming Convention Unification)

> **日期**: 2026-08-25
> **狀態**: 🔴 **開放問題 — 待攻堅 (O74-B 移交)**
> **來源**: 用戶指示 (08-25)「命名規則要改為開放問題」+ O73 docs/06 建議
> **前置**: O73 (ω_ring/R_world/T_ring rename 完成), O14 (Ω_b 直接), O33/O34 (能量配分), O39 (凝聚), PARADIGM BREAK (ζ(z) demoted)
> **定位**: 統一 IDCM 全部參數命名, 除 FLRW/ΛCDM 包袱 (Ω, H, ζ...), 建立符號化、簡潔嘅理論語言

---

## 0. 核心問題

```
IDCM 冇膨脹 (PARADIGM BREAK) → 多個繼承自 ΛCDM 嘅符號係語意包袱:
  Ω_Λ: Ω = ρ/ρ_c 依賴 FLRW 臨界密度 (ρ_c = 3H²/8πG) — IDCM 冇呢個概念!
  Ω_m, Ω_b, Ω_DM: 同級問題
  H(z): 膨脹率 — IDCM 冇膨脹, 真實身份係投影導出量
  ζ(z): 已 demoted (PARADIGM BREAK)

需要: 一套 IDCM 本名, 每個符號對應真實物理 (世界環幾何/K_Chain 譜/投影)
```

## 1. O73 已完成嘅 rename (參考模式)

```
✅ H₀ → ω_ring (世界環角頻率, c/R_world)
✅ R_H → R_world (世界環半徑)
✅ T_sync → T_ring (世界環周期)
✅ src 11 檔案 rename + deprecated alias 向後兼容

模式: 新名反映 IDCM 物理身份, 舊名留 alias 唔刪
```

## 2. O75 候選改名表 (O73 docs/06 建議 A)

| 舊 (ΛCDM 包袱) | 新 (IDCM) | 定義 | 值 | 來源 |
|:---------------|:----------|:-----|:---|:-----|
| Ω_Λ | **f_unproj** (未被投影比例) | E_unproj/E_total = 61.5/90 | 0.683282 | O33/O34 |
| Ω_m | **f_matter** (物質比例) | E_matter/E_total = 28.5/90 | 0.316718 | O33/O34 |
| Ω_b | **f_baryon** (重子比例) | 2φ⁻¹/(5(φ⁴-1)) | 0.042229 | O14 |
| Ω_DM | **f_dm** (暗物質比例) | 13f_baryon/2 | 0.274489 | O14 |
| Ω_b/Ω_m = 2/15 | r_bm (結構比) | 保持 | 0.13333 | O14 |
| Ω_DM/Ω_b = 13/2 | r_dmb (結構比) | 保持 | 6.5 | O14 |
| Ω_Λ/Ω_m = 4φ/3 | r_um (結構比) | 保持 | 2.15734 | O39 |
| H(z) | H_proj(z) = c/(dD_app/dz) | 投影深度函數 | O51 | 🟡 |
| ζ(z) | 🛑 已 demote | — | — | PARADIGM BREAK |

## 3. 遷移策略 (跟 O73 rename 模式)

```
1. src/ 加 alias: Omega_Lambda = f_unproj (deprecated), Omega_m = f_matter
2. 新代碼用 f_* 名
3. 公式唔變 — 只係 re-label (數值/閉合唔受影響)
4. 文檔同步: O73 docs/04 (BBN 鏈 Ω_b→f_baryon), O14, O33/O34, README
5. 保留 deprecated alias 向後兼容 (同 ω_ring 模式)
```

## 4. 替代方案

| 方案 | 優點 | 缺點 |
|:-----|:-----|:-----|
| A. 全改 f_unproj/f_matter | 徹底除 FLRW 包袱 | 文檔遷移量大 |
| B. 保留 Ω 但加註釋 | 零遷移 | Ω 符號繼續誤導 |
| C. 用 IDCM 原文「未被投影/已投影」 | 最貼近物理 | 符號冗長 |

**初步建議 A** (同 O73 原則一致) — 但係開放問題, 歡迎其他方案

## 5. 開放問題 (要問)

```
1. f_* 定係其他前綴? (f = fraction? u_ 未投影? 定係中文直譯?)
2. H_proj(z) 定係 ω_proj(z)? (H 本身係包袱?)
3. 需要唔需要統一「結構比」命名 (r_bm, r_dmb, r_um)?
4. 有冇其他包袱符號未列入? (Σγ? N_d? B? 呢啲係咪 OK?)
5. 文檔遷移範圍: 全部舊文檔定只係新文檔?
```

## 6. 誠實標記

| 項目 | 狀態 |
|:-----|:----:|
| 候選改名表 | 🟡 建議 A (待用戶確認) |
| 遷移策略 | 🟡 模式確認 (O73 已示範) |
| 開放問題清單 | 🔴 未答 |
| src alias | 🔴 未執行 (等確認) |

## 7. 成功標準

```
- 全部 IDCM 參數有 IDCM 本名 (零 ΛCDM 包袱)
- src + 文檔一致
- 向後兼容 (deprecated alias)
```
