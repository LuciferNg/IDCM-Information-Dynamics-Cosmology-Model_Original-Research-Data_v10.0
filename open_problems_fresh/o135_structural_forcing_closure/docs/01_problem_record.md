# O135 — 結構強制完整驗證

> **創建日期**: 2026-08-29
> **狀態**: 🔴 未開始
> **來源**: v9.0 項目審計 — `wfield_lattice/structural_forcing.md + structural_forcing.py`
> **前置**: O115 (夸克質量) 🔴, O54 (輕子質量) 🟢, O95 (44 唯一性) 🟢
> **定位**: 從 v9.0 structural_forcing.md + structural_forcing.py 遷移 — 所有結構強制公式在 v10.0 中的完整驗證

---

## 一、問題

從 v9.0 structural_forcing.md + structural_forcing.py 遷移 — 所有結構強制公式在 v10.0 中的完整驗證

## 二、假設

1. v9.0 推導在 v10.0 非膨脹框架中部分或全部有效
2. 需要驗證的關鍵假設：
   - 是否依賴膨脹宇宙假設？
   - 是否使用 v9.0 已 demote 的參數（如 ζ(z)）？
   - 是否與 v10.0 已閉合結果（O76, O100, O51 等）一致？

## 三、驗證步驟

### 步驟 1：讀取 v9.0 原始推導
- 路徑: `wfield_lattice/structural_forcing.md + structural_forcing.py`
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

- `wfield_lattice/structural_forcing.md + structural_forcing.py`

## 五、開放問題

1. v9.0 推導是否在 v10.0 中有效？
2. 是否需要修正以適應非膨脹框架？
3. 與 O1-O121 中已閉合結果的關係？

---

## 六、推導時序索引 (2026-09-27 前置驗證輪)

| 時間 | script | 結果 | 記錄 doc |
|:-----|:-------|:-----|:---------|
| 2026-09-27 | `scripts/01_v9_structural_forcing_inventory.py` | 39/39 PASS — v9.0 全 13 層值盤點 (mpmath dps=50) | `data/01_v9_inventory.json` |
| 2026-09-27 | `scripts/02_v10_migration_crosscheck.py` | 22/22 PASS — 逐項 v9.0→v10.0 遷移判決 | `data/02_migration_crosscheck.json` |
| 2026-09-27 | `scripts/03_tail_truncation_identity.py` | 4/4 PASS — ε/Ω_Λ φ 形 = 精確式 Lucas 尾截斷 (EXACT) | `data/03_tail_truncation.json` |
| 2026-09-27 | 判決 doc | — | `docs/02_migration_verdict.md` |

**依賴鏈 (對照源)**: O135 → {O97 (φ), O191 (K_tree/二模量), O211 (h¹¹/h²¹ 生成), O148 (ε/Ω_Λ 尾),
O37/O39 (Ω_Λ 撤銷), O40 (v_SM), O166 (T_CMB 降級), O204 (W₀), O36 (γ_n 譜), O54/O136 (質量譜),
O65/O123 (CKM/PMNS), O169 (E(0))}

**譜定義注意**: v9.0 用 **φ-power ladder** (m ∝ φ^−k); v10.0 用 **γ_n = 4sin²(πn/88) 譜**
(m ∝ γ_n) — 兩者係不同語言, 唔可直接混用數字。

**答案 (§五)**: ① 骨架 ✅ 遷移 / 物理量 🔴 失效 (非「部分有效」); ② 非膨脹依賴僅 T_CMB 一項
(已降級), 其餘失效係「φ-ladder → γ_n 譜」架構取代; ③ v9.0 物理量 = v10.0 已閉合結果嘅舊表達。

## 七、狀態

🟢 **前置驗證閉合 (2026-09-27)** — v9.0 推導喺 v10.0 之有效性逐項判定完成 (65/65 PASS)。
無本 O 專屬新缺口; v9.0 檔案降級為史料 + 負結果對照。詳見 `docs/02_migration_verdict.md`。
