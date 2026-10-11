# O123 — 中微子 δ_CP 從 CY₃ 投影

> **創建日期**: 2026-08-29
> **狀態**: 🔴 未開始
> **來源**: v9.0 項目審計 — `open_problems_fresh/p_nu_delta_cp/`
> **前置**: O54 (ν/l 統一) 🟢, O59 (Z₃ 12 維) 🟢, O53 (CY₃ 真實性) 🟢
> **定位**: 從 v9.0 p_nu_delta_cp 遷移 — 中微子 CP 相位從 CY₃(36,98) 投影的精確推導

---

## 一、問題

從 v9.0 p_nu_delta_cp 遷移 — 中微子 CP 相位從 CY₃(36,98) 投影的精確推導

## 二、假設

1. v9.0 推導在 v10.0 非膨脹框架中部分或全部有效
2. 需要驗證的關鍵假設：
   - 是否依賴膨脹宇宙假設？
   - 是否使用 v9.0 已 demote 的參數（如 ζ(z)）？
   - 是否與 v10.0 已閉合結果（O76, O100, O51 等）一致？

## 三、驗證步驟

### 步驟 1：讀取 v9.0 原始推導
- 路徑: `open_problems_fresh/p_nu_delta_cp/`
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

- `open_problems_fresh/p_nu_delta_cp/`

## 五、開放問題

1. v9.0 推導是否在 v10.0 中有效？
2. 是否需要修正以適應非膨脹框架？
3. 與 O1-O121 中已閉合結果的關係？

---

# 2026-09-27 Session — Stage B + Stage A 結果

> **append-only**：以上原文一字不刪。

## 狀態更新

🔴 未開始 → 🟡 **部分閉合**（δ_PMNS 結構候選 + 上游候選否證；π 分支/有限深度未推導）

## 推導時序索引 (T-row)

| # | 時間 | script | 結果 | 記錄 |
|:--:|:--|:--|:--|:--|
| T1 | 2026-09-27 | `scripts/01_treephase_nogo.py` | 2/4 PASS — tree ⊂ ℝ；atan(實比) 家族 null 0% (有選擇性)；無 1e-8 候選 | docs/02 §1 |
| T2 | 2026-09-27 | `scripts/02_tensor_phase_nogo.py` | 4/4 PASS — 張量積譜全實；複結構來源 = 0（Z₅ 被 P4 殺） | docs/02 §2 |
| T3 | 2026-09-27 | `scripts/04_numerology_null_230.py` | 230° 4 Hard Tests 3 關 FAIL（coverage 100%、115 witness、循環 J） | docs/02 §3 |
| T4 | 2026-09-27 | `scripts/03_delta_pmns_derivation.py` | **7/7 PASS** — δ_PMNS = π + atan(β) = 211.7175°；J_CP = −0.0176 | docs/03 |
| T5 | 2026-09-27 | `scripts/05_pi_branch_chirality.py` | **7/7 PASS** — π 分支定理: tree 唯一負物件 −φ⁻¹; δ_sector = arg(Z)+atan\|Z\|; Sector-Chirality J_PMNS<0<J_CKM | docs/04 |
| T6 | 2026-09-27 | `scripts/06_depth_and_uniqueness.py` | **3/4 PASS** — 深度: 精確 = β (族=有理收斂子); 唯一性 1e-8 (mult=1, 競爭者 0.05°); D2 J 帶統計辨別誠實 FAIL | docs/04 |

## 依賴鏈

```
O54 🟢 (ν/l 統一) ─┐
O59 🟢 (Z₃ 12維)  ─┼→ O123 ─→ tree 本徵向量角 atan(β) (= docs/09 §4.1 θ₁₂ 基角)
O53 🟢 (CY₃真實性) ─┘         └→ F-matrix 元 −φ⁻¹ = e^{iπ}φ⁻¹
ckm_reconstruction T9 (PMNS 角集) ─→ J_max = 0.033530
ChronologicalStringSpectralGeometry-v2/docs/06 (Z₅ 主張) ─→ 本輪否證
```

## 本輪裁決摘要

- **SESSION_START 指定路線（CY₃ 投影 / Z₅ twisted sector）→ 🔴 死**: P4 no-go（uniform Z₅ twist ⇒ J≡0）+ sector separation。
- **上游 4 個互相矛盾候選全部否證**: 222.5° (φ-trap)、72°/144° (Z₅ no-go)、72.6° (無源)、230° (numerology)。
- **新候選 🟡**: `δ_PMNS = π + atan(β) = 211.717474°`，J_CP = −0.0176（符號負）。
- **Round 2 續推**: π 分支定理 🟢（tree 唯一負物件 −φ⁻¹ ⇒ Sector-Chirality J_PMNS < 0 < J_CKM）；
  深度釘死 🟡（精確 = β；理論窗 0.29° 有界）；唯一性 🟢（1e-8, mult=1, 競爭者間距 0.05°）。
- **剩餘 🔴**: 統一相位公式 δ = arg Z + atan|Z| 嘅底層推導（由 U_PMNS 構造, 唔係 pattern 推論）。

## 譜定義注意

- tree sector 譜: T̂ = [[1,1],[1,0]]，特徵值 {φ, −1/φ}（**實**）。
- 本 O 用 **176-Laplacian** 慣例: γ_k = 4sin²(kπ/176)（同 ckm_reconstruction T7/T9 一致）。
- δ_CKM 用 atan(ω₂₁/ω₉)（ω = √γ），δ_PMNS 用 atan(β)（tree 量）— **兩者扇區唔同，唔可以混用 γ 索引**。
