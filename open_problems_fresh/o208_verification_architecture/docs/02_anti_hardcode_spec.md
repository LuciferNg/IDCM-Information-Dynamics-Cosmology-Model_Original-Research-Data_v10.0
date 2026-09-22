# O208 docs/02 — 反硬編碼規則 (Anti-Hardcode Spec)

> **日期**: 2026-09-22
> **性質**: 驗證架構標準 — Phase 0 交付物 2
> **狀態**: 🟢 已定案
> **來源**: O115 docs/02 缺陷 3 + O208 全目錄掃描實測

---

## 一、問題

實測: `open_problems_fresh/` 全目錄掃描（2026-09-22, 語義級）：
- **9 個 script** 含「字面 True 冒充驗證」— 共 **45 處**（O86 17, O117 6, O69 8, O65 4, O54 5, O121 3, O66 3, O49 3）
- 形態分兩種:
  - **C 型**: `check("描述", True)` — 檢查函數收到字面 `True`，必 PASS
  - **D 型**: dict 值 `"檢查名": True` — 結果 JSON 硬寫 PASS，冇任何計算
- **1 個假陽性**（O21 `"nest": True` = healpix API 參數，唔係驗證斷言）→ 證明需要語義級掃描，唔係字面 grep

**後果**: 「34/34 PASS」可以係 17 個真計算 + 17 個字面 True（O86 實例）—— 閉合帳本被污染。

---

## 二、規則（強制）

### 2.1 禁止形態

| 形態 | 例子 | 判定 |
|:-----|:-----|:-----|
| A. `assert True` | `assert True` | 🔴 禁止 |
| B. `check("名", True)` | `check("φ=8 維度", True)` | 🔴 禁止 — 必須傳入真計算表達式 |
| C. `assert expr is True / == True` | `assert ok is True` | 🟡 禁止 — 用 `assert ok` 或 `assert bool(expr)` |
| D. dict 值字面 True | `"閉合": True` | 🔴 禁止 — 必須由變量/計算產生 |
| E. 無條件 accumulator | `ok = True` 然後從未設 False | 🟡 禁止 — 必須由條件設定 |

### 2.2 豁免（唔算硬編碼）

| 情況 | 例子 | 理由 |
|:-----|:-----|:-----|
| API 參數 | `lonlat=True`, `nest=True`, `exist_ok=True`, `overwrite=True` | 函數參數，唔係驗證 |
| 配置 dict | `"pre_smoothed": True` | 描述數據屬性，唔係 PASS 聲稱 |
| 算法初始化 | `visited[start] = True` | BFS/DFS 狀態標記 |
| flag 起點 | `ok = True` 但**之後**喺條件下可設 False | 合法 accumulator 模式 |
| 符號常量 | `HAVE_MP = True` 檢查依賴存在 | 環境檢測 |

### 2.3 替代寫法

```python
# 🔴 舊 (O69 實例):
check("φ=8 扇區維度 = F₅ = 5", True)

# 🟢 新: 傳入真計算
check("φ=8 扇區維度 = F₅ = 5", n_modes == F5)

# 🔴 舊 (O86 實例):
"Einstein-Hilbert嵌入": True,

# 🟢 新: 由計算產生，或明確分級
"Einstein-Hilbert嵌入": (L_GR_terms == expected_terms),  # 數值檢查
# 若無法數值化 → 明確分級 🟡（結構聲稱，非驗證），唔可以寫 True
```

### 2.4 分級原則

- 可以數值化嘅檢查 → 真計算（PASS/FAIL 有實質）
- 無法數值化嘅結構聲稱（「嵌入」「閉合」「零自由參數」）→ **明確分級 🟢/🟡/🔴**，寫入「聲稱」section，**唔可以**入 PASS 計數
- 任何 script 輸出 `RESULT: N/N PASS` 時，N 必須只計真計算檢查

---

## 三、審計程序（每個 script）

1. 語義級掃描（`scripts/01_hardcode_scanner.py`，排除豁免形態）
2. 逐處分類: 真硬編碼 / 可數值化 / 結構聲稱 / 假陽性
3. 可數值化 → 改為真計算
4. 結構聲稱 → 降級標記（`🟡` + 註釋「非數值驗證」）
5. 重跑確認: 字面 True 歸零（排除豁免）
6. 每 script 一份審計記錄 → `audit/NN_<o>_<script>.md`

---

## 四、驗收

- [ ] 全目錄語義掃描: 0 個真硬編碼斷言（豁免形態除外）
- [ ] 每個被審計 script 有 audit 記錄
- [ ] 掃描器可重用（O208 scripts/01，新 O 入場檢查）

---

## 五、附錄：O208 審計清單（全 10 個高風險 script）

| # | Script | 字面 True 數 | 分類 | 處置 |
|:-:|:-------|:------------|:-----|:-----|
| 1 | O86 scripts/05_final_verification.py | 17 | D 型 17 | 重寫: 可數值化 11 → 真計算, 6 → 🟡 聲稱 |
| 2 | O117 scripts/09_first_principles_closure.py | 6 | D 型 6 | 重寫: 已有 chi² 數值 → 用變量 |
| 3 | O69 scripts/06_verify_geometric_derivation.py | 8 | B 型 3 + D 型 5 | 重寫 |
| 4 | O54 scripts/06_antiparticle_origin.py | 5 | D 型 5 | 重寫: 結論 dict → 🟡 聲稱 |
| 5 | O65 scripts/04_final_verification.py | 4 | B 型 1 + D 型 3 | 重寫 |
| 6 | O121 scripts/05_information_paradox.py | 2 | D 型 2 | 重寫: 用前面已有計算 |
| 7 | O121 scripts/10_singularity_resolution.py | 1 | D 型 1 | 重寫: 用已有 K_ds_core |
| 8 | O66 scripts/00_verification_check.py | 3 | D 型 3 | 重寫 |
| 9 | O49 scripts/06_structural_closure.py | 3 | D 型 3 | 重寫 |
| 10 | O21 scripts/03_cross_map_verify.py | 3 | **假陽性** (API/config) | 豁免 — 記錄即可 |
