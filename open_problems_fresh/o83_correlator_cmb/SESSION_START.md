# O83 — SESSION START

> **Session**: 2026-08-25 (由 O72 移交)
> **狀態**: 🔴 已註冊 — 待攻堅

---

## 定位

Correlator ⟨φφ⟩ ↔ C_ℓ — 由 O72 未完成工作移交。

## 交接點

```
來源: O72 docs/19_unfinished_inventory.md
狀態: 🔴 未開始
```

## 相關資源

```
- O72 docs/19_unfinished_inventory.md — 移交清單
- O72 docs/01-18 — 背景
```


---

## ★ 全樹路徑衛生審計註記（2026-10-02，append-only）

> 由 skill `script-chain-reproducibility` 全鏈核對器（`path_hygiene_scan.py`）全樹掃描建立——
> **2026-10-02 首次**。**本節唔改動上方任何內容。**
>
> ⚠️ 本節係**工具層審計**（產物路徑衛生），**唔屬本 O 推導**；亦冇對本 O 任何結論作出判定。
> 完整報告：`path_hygiene_audit_20261002/REPORT.md`

### 〇. 一句話

本目錄命中 **2 個 ghost-tree call site**。

### 一. 命中清單

#### ⚠️ ghost tree 依赖

| # | 檔案:行 | 讀取目標（ghost tree 內）|
|:--|:--|:--|
| 1 | `o83_correlator_cmb/scripts/07_file_verifier.py:191` | `open_problems_fresh/o83_correlator_cmb/docs/01_problem_record.md` |
| 2 | `o83_correlator_cmb/scripts/07_file_verifier.py:193` | `open_problems_fresh/o83_correlator_cmb/docs/02_derivation_record.md` |

### 二. 處置（別 O 執行；本節只記移交）

```
⚠️ ghost tree 依赖：2 個 call site 讀 `/home/wsl/Projects/IDCM/IDCM-v10.0/`。
   ① 把所需檔搬入本 O `data/`（或記明「唯讀外部輸入」）
   ② `BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` ＋ 相對路徑
   ③ 風險（已量化）：ghost tree 係 2026-09-08 副本（全樹 288K）。全樹 301 個 call site 分類：
      ① 69 個目標仍存在（讀嘅係**陳舊副本**）；② 231 個目標已失踪但同相對路徑在 repo 存在
      （⟹ **改一行即可，零資料損失**）；③ 1 個 repo 內完全冇。逐 O 對照表 → 同報告目錄 `ghost_dispatch.md`
```

> ⚠️ 依據 `idcm-closeout` §8.1：跨 O 問題**只登記移交，唔准就地修**。本節由**外部審計**寫入，
> 本 O 之 session **有權刪去或改寫本節**（上方內容不受影響）——但如果決定保留，
> 請在 GATE / 下輪 round doc 裏明文記下「已接納 / 已處理」。

---

## ★ 2026-10-23 審計後狀態（append-only，上方原文不動）

> ⚠️ 上方 body 仍係 08-25 骨架：08-25 實際攻堅已完成、10-23 審計後裁決為 **🟡 partial**。
> body 未改（物證保留），狀態以本節為準。

### 路徑（2026-10-23 實測）

```
本 O 現址: /home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o83_correlator_cmb
舊址 (ghost) /home/wsl/Projects/IDCM/IDCM-v10.0/... 已冇 o83 目錄 ⟹ 06/07 原本 FAIL
✅ 已修: scripts/01, 06, 07 全改相對路徑 (2026-10-02 外部審計 §二 選項②)
```

### 裁決

```
🟡 partial — 橋接形式成立；峰位/振幅屬繼承後驗
🟢 保留: Σγ 精確和 (44-site=90; 88-site 偶90/奇88/178=2F₁₁, sympy)
        G_n(0)=1/(2ω_n)≡1/(4sin(nπ/88)) 代數恆等; 熱態形式
🟡 降級: 「零自由參數 58/58」→ 實質 129 check (11 個空洞 check 改 📝 註記)
        RMS 0.335% → 權威 0.84% (O9 最終閉合矩陣 obs; cmb_cl 舊 obs 才 0.34%)
        ℓ_sync=44 係定義恆等 (λ_sync≡πR_world/44)；「2N_d」標籤錯 (應 =N_d)
        振幅: w_m ≡ A_m/G_m(0) 反解 ⟹ 零預測力
        m=5 F₆/F₈ 硬寫後驗
```

### 檔案

```
docs/02_derivation_record.md  — 08-25 推導記錄 (8752 bytes 完好) + 10-23 更正附註
docs/03_audit_report.md       — ★ 全量審計報告 (18 項, 證據齊)
scripts/08_audit.py           — 審計腳本 (可重跑)
root/01_problem_record.md     — 攻擊路線原文重建 (§ 2026-10-23)
docs/01_problem_record.md     — 10-15 覆蓋事件物證 (811 bytes, 不改)
```

### 重跑

```bash
cd .../o83_correlator_cmb
for s in scripts/0[1-7]*.py; do /usr/bin/python3 "$s"; done   # 129 實質 check
/usr/bin/python3 scripts/08_audit.py                          # 審計 18 項
```
