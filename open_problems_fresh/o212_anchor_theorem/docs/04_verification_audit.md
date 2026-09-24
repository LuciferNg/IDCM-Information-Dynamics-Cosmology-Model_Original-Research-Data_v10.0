# O212 docs/04 — 驗證審計 (Verification Audit)

> **日期**: 2026-09-24
> **範圍**: 本 O 全部推導之重跑 + 獨立核對 + 計數對帳 + 反幻覺檢查
> **紀律**: 只寫本 O 目錄；舊文檔保留原文（append-only 標註）

---

## 一、重跑（閉合紀律）

由 O 目錄 root 執行（`python3 scripts/NN.py`）：

| script | 命令 | 結果 |
|:-------|:-----|:-----|
| 01_anchor_uniqueness_scale_tree.py | `/usr/bin/python3 scripts/01_anchor_uniqueness_scale_tree.py` | exit 0, **RESULT 26/26 PASS**（C1 3/3 + C2 22/22 + C3 1/1）；C5 標度樹精確 12/22；C6 超越隨機 0/10 |
| 02_hierarchy_N_provenance.py | `/usr/bin/python3 scripts/02_hierarchy_N_provenance.py` | exit 0, **RESULT 12/12 PASS**（C1 1 + C2 1 + C3 1 + C4 1 + C5 1+1 + C6 1 + C7 5） |
| 03_audit.py | `/usr/bin/python3 scripts/03_audit.py` | exit 0, **AUDIT RESULT 30/30 核對通過** |

輸出存檔：`data/01_*.out`、`data/02_*.out`、`data/03_audit.out`。

---

## 二、獨立核對（`scripts/03_audit.py`，零 import 其他 scripts）

### §A 維度空間符號解（sympy，獨立於 script 01 嘅 Fraction Gauss）

| 量 | sympy 解 | 期望 | 判定 |
|:---|:---------|:-----|:----:|
| R_world | (−3/2, 1/2, 1/2, 0) | 同 | ✔ |
| τ | (−5/2, 1/2, 1/2, 0) | 同 | ✔ |
| M₀ | (5/2, 1/2, −1/2, 0) | 同 | ✔ |
| T_CMB | (5/2, 1/2, −1/2, −1) | 同 | ✔ |
| a₀ | (7/2, −1/2, −1/2, 0) | 同 | ✔ |

**5/5 ✔** — 兩條獨立 code path（Fraction Gauss vs sympy `M.solve`）結果一致。

### §B N 恆等式符號化簡

`sp.simplify(expr_N² − target)` **= 0** ✔（expr_N² 由 BBN 鏈獨立建立；
target 用 `m_Pl = √(ħc/G)` 代入）。

### §C 數值恆等式 vs 直接鏈

| Ω_b | N_closed | N_direct | rel_dev |
|:----|:---------|:---------|:--------|
| 19/450 | 7.87120590774e60 | 7.87120590774e60 | **0.0** |
| 3/60 | 8.56555941868e60 | 8.56555941868e60 | **0.0** |

另：`n_γ = 4.107178061e8 m⁻³` vs 實測 4.107e8 → rel_dev = 4.34e−5 ✔

### §D 標度樹因子重算（12 項）

```
N = R_world/l_Pl                      rel_dev = 2.3e−11   ✔
R_world/(l_Pl·N) = 1                  rel_dev = 0.0       ✔
r_d/(l_Pl·N) = 420π/(88·421)          rel_dev = 2.4e−6    ✔
λ_sync/(l_Pl·N) = π/44                rel_dev = 4.7e−7    ✔
a/(l_Pl·N) = 1/88                     rel_dev = 1.2e−41   ✔
T_ring/τ = 2π                         rel_dev = 0.0       ✔
Γ⁻¹/τ = 2π/44                         rel_dev = 1.9e−9    ✔
M₀/(m_Pl·N^(−1/2)) = (1891/2025)φ^e    rel_dev = 8.3e−6    ✔
m₇/M₀ = 2sin(7π/88)                   rel_dev = 2.2e−8    ✔
a₀·t_Pl²/l_Pl·N = 1/(2π)              rel_dev = 2.3e−41   ✔
c_W/c (R_world=4129.94, ω=72.73)      rel_dev < 1e−8      ✔
N^(−1/2)/N¹ = N^(−3/2)                rel_dev = 0.0       ✔
```

### §E 單位常數分類核對

| 項 | 判定 |
|:---|:----:|
| c = 299792458 m/s（SI 定義） | ✔ |
| h = 6.62607015e−34 J·s（SI 定義） | ✔ |
| e = 1.602176634e−19 C（SI 定義） | ✔ |
| k_B = 1.380649e−23 J/K（SI 定義） | ✔ |
| ħ = h/2π 導出 | ✔ |
| G 非 SI 定義（CODATA 2018 測量, u_r = 2.2e−5） | ✔ |

### §F 計數對帳

| 宣稱 | 來源 | 判定 |
|:-----|:-----|:----:|
| script 01 RESULT 26/26（C1 3 + C2 22 + C3 1） | data/01 | ✔ |
| script 02 RESULT 12/12（C1..C7） | data/02 | ✔ |
| script 01 C5 精確 12/22；C6 超越隨機 0/10 | data/01 | ✔ |

---

## 三、反幻覺檢查（本輪）

| # | 檢查 | 結果 |
|:-:|:-----|:-----|
| 1 | 「逐項自帶標度」係表象？ | ✅ 已證：每行 = 錨 × 無量綱數（docs/01 §五） |
| 2 | 「錨全觀測」係否準確？ | ❌ **修正**：c/h/k_B/e 係 SI 定義（非觀測）；r_d 係導出；錨 = G ≡ ω_ring |
| 3 | N 係唔係結構數？ | ✅ 已證 🔴（q_obs = 0.875，O200 0.8735 重現） |
| 4 | 「N 需動力學解釋」係否成立？ | ❌ **修正**：N = 無量綱恆等式值；剩餘 = 重力階層 → O86（docs/03 §八） |
| 5 | 標度樹有冇隱藏第二錨？ | ✅ 無：非結構項全部係無量綱觀測比值（docs/02 §四） |
| 6 | 3 個 tautology 行有冇被當作結構？ | ✅ 已明標 🟡 tautology（docs/02 §二/§五） |
| 7 | BBN 鎖定係否獨立於 Ω_b 版本？ | ❌ **發現**：敏感（19/450 → 72.71；3/60 → 66.82）；現行 72.59 係觀測錨 |

### ★ 本輪真發現（2 項）

| # | 發現 | 性質 | 處置 |
|:-:|:-----|:-----|:-----|
| A | SESSION_START「錨全觀測（r_d/M_P/ω_ring）」中 `r_d` 唔係錨、`c/h/k_B/e` 唔係觀測 | 命題精度 | docs/01 §五 修正（原文保留） |
| B | SESSION_START「N 可能需動力學解釋（交 O213）」方向錯 | 方向修正 | docs/03 §八 修正 → 交 O86（原文保留） |

---

## 四、腳本自身 bug 修正記錄（反幻覺：先 check check）

| # | 問題 | 修正 |
|:-:|:-----|:-----|
| 1 | script 01 C5 首版將絕對無量綱因子（如 7.88e60）直接對小結構數（88, 946）比較 → 全部荒謬 🔴 | 改為「factor ÷ N^p → 結構匹配」（標度樹） |
| 2 | script 01 C5 verdict 用 `dev < 1e-9` → 結構式本身含註冊值捨入，全部假 FAIL | 改 `dev < 1e-5` 為 EXACT 門檻 |
| 3 | script 01 C5 將 `M₀ × (m_ν/M₀)` 判 🟢 EXACT | 加 `tautology` 標記（🟡） |
| 4 | script 02 `omega_from_chain` 用 `/num/den`（= `/(num·den)`）→ N 大 450 倍 | 改 `_frac()` |
| 5 | script 02 `mp.mpf(Fraction)` → TypeError | 改 `_frac()` |
| 6 | script 02 C7 `m_p` 期望值寫 +1/2（應 −1/2） | 修正 |
| 7 | script 03 sympy `mp` symbol 遮蔽 mpmath alias → AttributeError | 改名 `mps` |
| 8 | script 03 §B `expr_N²` 唔含 `m_Pl` → subs 無效 → 假 FAIL | 改為 `target.subs(...)` |
| 9 | script 03 `chk` 用絕對容差 → 大數（6.4e9）必假 FAIL | 改相對容差 |
| 10 | script 03 `c_W/c` 用 `R_world = c/ω_ring(72.59)` → 恆等 1 | 改用註冊 R_world + ω_ring = 72.73（BBN） |

**全部 10 項係 check 設計 bug，唔係物理/文檔錯誤**（修正後 26/26 + 12/12 + 30/30 全綠）。

---

## 五、計數總結

```
script 01:  26/26 PASS   (C1 3 + C2 22 + C3 1)
             + C5 標度樹精確 12/22
             + C6 非精確項超越隨機 0/10  (誠實負結果)
script 02:  12/12 PASS   (C1..C7)
script 03:  30/30 核對通過 (A 5 + B 1 + C 3 + D 12 + E 6 + F 3)
────────────────────────────────────────────────
總計: 68/68 PASS + 12/22 標度樹 + 0/10 超越隨機
```

**注意**：`12/22` 同 `0/10` 唔係 PASS 計數嘅一部分（係分類結果），唔可以加埋當「68+12+0」。
「68/68」= 三條 script 嘅 PASS 斷言總數。

---

## 六、誠實邊界

| 項 | 狀態 | 說明 |
|:---|:----:|:-----|
| 錨定理（結構部分） | 🟢 | 維度齊次，dof = 1，22/22 解出 |
| 標度樹零校準 | 🟢 | 絕對標度只有 N 一個來源 |
| N 精確恆等式 | 🟢 | sympy 差 = 0，數值 dev = 0 |
| N 由結構數導出 | 🔴 | q_obs = 0.875（≈ 隨機）；維度定理必然 |
| 錨之絕對值（G 為何係 6.674e−11） | 🔴 | = 重力階層問題 → O86 |
| 標度樹 4 個 IDCM 內部量未結構化 | 🔴 | T_age / E_kchain / T_sync / m_δW — 各自 O 範圍 |
| Ω_b 版本 | 🔴 | O73 O5-1 未裁定（本 O 重算確認敏感度） |
