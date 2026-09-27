# O128 docs/02 — v9.0 σ8_norm 遷移裁決

> **日期**: 2026-09-27
> **腳本**: `scripts/01_v9_migration_ruling.py`（**7/7 PASS**）→ `data/01_v9_migration_ruling.log`
> **v9.0 來源**: `IDCM-v9.0--W-Field-Lattice/open_problems_fresh/sigma8_norm/01_derive_sigma8.py`（唯一檔案，165 行）
> **對應 SESSION_START §前置驗證 第 1–5 條**

---

## 一、結論一句

> **v9.0 `sigma8_norm` 冇任何可遷移之結構內容 —— 遷移結果 = 空集。該 script 嘅「σ8 預言」係
> `σ8 = √(Σγ_n/n²) × 0.1`，其中 `0.1` 係**手動縮放常數**，且 PASS 判準寫成
> `|σ8 − 0.811| < 0.1`（直接量度「距目標有幾近」）。依 SESSION_START 第 5 條 ⇒
> **需建立新推導**（v10.0 路徑，見 `docs/03`）。**

---

## 二、逐項判定（V1–V5）

### V1 執行環境 —— 全部失效

| 硬編碼路徑 | exists |
|:---|:---:|
| `/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web` | ❌ |
| `/home/wsl/IDCM/sync_bump_analysis/ross_dr12_corrfunc.zip` | ❌ |

原樣執行 ⇒ `ModuleNotFoundError: No module named '_core'`（V1b）。
（`/home/wsl/IDCM` 目錄已唔存在；現行樹係 `/home/wsl/Projects/IDCM-Original/`。）

### V2 σ8 預言部分 —— 含手動縮放

```
A_chain = Σ_{n=1..43} γ_n/n² = 0.169957          ← 純結構數（可接受）
v9.0 寫法: σ8 = √A_chain × 0.1 = 0.0412          ← 0.1 無結構來源
```

**縮放因子掃描**（σ8 ∝ s ⇒ 任何目標皆有解）：

| 目標 σ8 | 所需 s |
|:---:|:---:|
| 0.70 | 1.697964 |
| 0.783（BOSS） | 1.899294 |
| 0.811（Planck） | 1.967212 |
| 0.95 | 2.304380 |

⟹ 該「預言」對任何目標值都可調中 ⇒ **零判別力**。

### V3 判定準則 —— post-hoc

源碼（`01_derive_sigma8.py` 尾段）：

```python
'✅ K_Chain predicts σ₈ within ΛCDM range' if abs(sigma8_kchain - 0.811) < 0.1 else ...
```

PASS 準則 = 「距目標 0.811 有幾近」⇒ 直接違反 **禁看到目標湊算子** 鐵律。

### V4 數據部分 —— 身份係「量度」而非「推導」

`σ8 ≈ √ξ(8 h⁻¹Mpc)` 與 top-hat 積分 `σ8² = (3/R³)∫₀^R ds s²ξ(s)W(s)` 係由 BOSS DR12 ξ(s)
**量度** σ8。作為**觀測錨**合法，但唔構成 IDCM 預言。

### V5 可遷移公式清單

| 項 | 可否遷移 | 理由 |
|:---|:---:|:---|
| `γ_n = 4sin²(πn/88)` | ⬜ | v10.0 已有（K_Chain 譜），非本檔貢獻 |
| `A_chain = Σγ_n/n²` | ❌ | 純數，無量綱歸一化 ⇒ 唔構成 σ8 |

**可遷移之 σ8 結構公式 = 0 條。**

---

## 三、裁決

| 項 | 判定 |
|:---|:---|
| 環境 | 🔴 硬編碼路徑全失效，原樣執行 ImportError |
| 預言 | 🔴 `σ8 = √A_chain × 0.1`，0.1 手動縮放 |
| 準則 | 🔴 PASS = 距目標有幾近（post-hoc） |
| 數據 | 🟡 由 BOSS ξ(s) 量度 σ8（合法觀測錨，非預言） |
| **遷移** | **⬜ 空集 —— v9.0 該項唔可遷移** |

> **⟹ v10.0 之 σ8 歸一化必須由零重推。** 現行路徑 = O100 逆投影算符 ℳ
> （Planck TT 第一峰 D₁ = 5750 μK² 唯一錨），已於 `docs/03` 獨立重推並復現。

---

## 四、依賴

O128 → O100（ℳ 線譜）→ O213 R4（ℓ-測度 / A_φφ）
