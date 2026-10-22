# O218 docs/02 — 統一可執行判準 (Unified Executable Criterion)

> **日期**: 2026-09-28
> **狀態**: 🟢 本 O 交付物 (核心)
> **實作**: `scripts/o218_lib.py`（純函數, 零 I/O）+ `scripts/02_identity_criterion.py`（22/22 PASS）
> **合成來源**: O200 三分類 + O201 常數掃描 11 條 + O204 結構 null test 五步 + O208 密度三件套 + O148/O151 陷阱窗

---

## 一、設計原則（= SESSION_START 鐵律之實作）

```
① 可執行      — 判準係函數: 輸入 (候選式, 目標, 容差) → 輸出 (判級)。禁「靠經驗判斷」。
② 零人手      — 判級只由 gate 決定; _decide() 內冇任何案例名分支 (docs/06 C 反作弊掃描證明)。
③ 池自動閉包  — 池由 ATOM_TABLE 自動生成 + 對 {+,−,×} 閉包, 禁手選 (O204 實錄: 手選漏 15)。
④ 禁截斷重建  — 唔用 sp.nsimplify / limit_denominator 對截斷值做有理還原 (O201 ③)。
⑤ 誠實        — 冇密度基準 / 冇精確證書 ⟹ 報 🟡 未閉合, 唔可以白拿 🟢。
⑥ 零副作用    — o218_lib.py 不開任何檔案 (docs/06 B 快照證明)。
```

---

## 二、O200 三分類（判準第一層分派）

| class | 目標性質 | 檢定方式 |
|:--|:--|:--|
| `identity` | 純代數/算子恆等式, 目標 = 框架自身閉式 | **精確證書** (符號化簡 = 0 或 mpmath 60 位 \|差\| < 1e-45) ⟹ `N_search = 1`, 唔受密度檢定 |
| `prediction_residual` | 框架預言 vs **觀測** (有 σ) | 受量度誤差預算 σ (O208 例外 2) + 陷阱窗 + 兩級測試 |
| `pool_match` | 候選值 vs **無 σ 之目標**, 靠池命中 | 受 G5 密度檢定 (MC 分位數 或 Farey 解析) |

> ⚠️ 混淆三者 = 方法論錯誤 (O200)。判準**強制**呼叫者指定 class, 唔可以靠判準猜。

---

## 三、Gate 表（全部可執行）

### 第 0 步 — 葉審計 (O201 ① 語法合法性)

| gate | 條件 | FAIL 之判級 |
|:--|:--|:--|
| `G1_G2_leaf_audit` | 每個**數值葉** ∈ {UNIT(0,1), REGISTERED, DEPTH1, RATIO(分子分母皆合法)} 且**無 BARELITERAL / EXOTIC**; 每個**符號葉**已註冊或有 O 出處 (`allow_symbols` 之 scaffolding 例外) | `ILLEGAL` |
| `G3_zero_free_param` | 無 `FITTED` 葉 (Float 字面值 / 分子或分母無出處之 Rational) | `FITTED` |

**葉分類體系** (`LEAF_STATUS`): `UNIT` 0,1 = 算術單位元（零信息） / `REGISTERED` 已註冊結構數 / `DEPTH1` 深度 1 衍生（需報表示數 R） / `RATIO` 有出處之有理比 / `CLOSURE_TRIVIAL` 落喺閉包區間但無結構身份 / `BARELITERAL` 裸數 / `FITTED` 擬合常數 / `EXOTIC` 未註冊實數 / `EXTERNAL` 外部框架內容。

> ★ 關鍵細節（曾產生假 FAIL）: sympy 會把 `x/2` 自動化為 `x·Rational(1,2)`, 故有理字面值必須**分子分母逐個審**, 唔可以一律當 FITTED; 負號亦然 (`Pow(w,−1)` 之 −1)。

### 第 1 步 — 等式真偽 G0

```
dev = |lhs − rhs| / |rhs|      (已註冊名先代入數值再求值)
tol_use = tol_rel                          (prediction/pool_match: max(tol_rel, target_precision))
G0 = PASS ⟺ dev ≤ tol_use
```
符號恆等式證書 (`symbolic`, 差 = 0) 或精確數值證書 (`numeric`, |差| < 1e-45) ⟹ G0 PASS。FAIL ⟹ `FALSE`。

### 第 2 步 — 結構內容三測 + 兩級

| tag | 條件 | 判級 |
|:--|:--|:--|
| `T1_tautology` | 共有量 (O151「重言式」) 換成自由符號後, 其他已註冊名代入數值, **化簡差 = 0** ⟹ 等式對該量恆等 | `TAUTOLOGY` |
| `T2_cross_framework` | dev = 0 但兩邊**無共同推導來源**且一邊係另一框架之導出常數（SM b₁ / MSSM b₁ / ΛCDM 擬合值） | `COINCIDENCE` |
| `T3_free_multiplier` | 目標超出身框架可達範圍 ⟹ 靠自由乘數供給 | `MULTIPLIER` |
| `T5_two_level` | 主體偏差 ≫ 目標精度 (`> max(5·prec, 1e-3)`) 而全式 dev ≈ 0 ⟹ **乘性修正承載匹配** (O204 步驟 2 兩級測試) | `MULTIPLIER` |
| `U_nonunique` | 目標之深度 1 表示數 `R ≥ 2` ⟹ 目錄表示非唯一 | `NONUNIQUE` |

> `T2` **唔適用**於 prediction/prediction_residual — 「IDCM 預言 對 觀測」係合法檢定 (O208 例外 4), 該類由 G0/G4/T5/G5 處理。

### 第 3 步 — 陷阱窗 G4（O148/O151）

```
窗 = (1e-5, 1e-3)
前置條件 (O201 §2, 曾致誤殺): 目標精度必須優於窗寬 ⟹ 只有 target_precision < 1e-3 時窗律才綁定。
dev ∈ 窗 且 precondition 成立 ⟹ FAIL ⟹ TRAP
```
例: C_old = −0.1697 最近命中 dev = 1.42e-4 且目標精度 1e-4 ⟹ 綁定 → 🔴；
log₂(S_dS) vs 406 之 dev 5.9e-4 ⟹ 綁定 → 🔴；
但「0.63% 擬合值」(精度 6.3e-3 ≫ 窗寬) ⟹ 窗律 n/a, 唔誤殺 (C8b, 02 script)。

### 第 4 步 — 密度基準 G5（O208 三件套, 兩條路徑）

| 路徑 | 用法 | 判級 |
|:--|:--|:--|
| MC `q_obs` | 候選空間可枚舉: `d_obs` vs 隨機目標之中位偏差, `N_mc = 1e5`, seed 固定 | `q ≤ 1%` 🟢 / `≤ 5%` 🟡 / `> 5%` 🔴 `DENSITY` |
| **Farey 解析** ★ | 候選空間隨因子數爆炸: `N_search ≈ (3/π²)·q_max²·2·tol_rel·T` | `N < 1` 🟢 / `< 10` 🟡 / `≥ 10` 🔴 `DENSITY` |
| identity 例外 | 精確證書 ⟹ `N_search = 1` | 🟢 `IDENTITY_OK` |
| σ 內例外 | prediction 且 `dev ≤ target_precision` ⟹ 報 σ 替代分位數 (O208 例外 2) | 🟢 `MATCH_OK` |

★ **Farey 密度論證**（本 O 新結果, `scripts/o218_lib.farey_density`）: 由結構池 {a} (a ≤ A) 造出之有理表達式值域 ⊆ {p/q : q ≤ q_max}；分母 ≤ q_max 之有理數喺長度 L 之區間內數目 ≈ L·(3/π²)·q_max²。**呢個就係 O136「符號庫爆炸」之定量根源**, 亦係 O201 §19「整數目標 null = 1.000」之推廣：2 因子商積 (q_max = 990²) 對 dev = 1e-9 之目標已給 `N_search ≈ 11.7 ≫ 1` ⟹ 任意目標都「命中」⟹ 零判別力。

### 第 5 步 — 數域分離 G6（O201 §11）

```
Q(ζ_{m1}) ∩ Q(ζ_{m2}) = Q(ζ_gcd(m1,m2)) ;  gcd = 1 ⟹ 交集 = Q
⟹ 兩代數數結構上唔可能相等 (即使數值差 < 容差) ⟹ FIELD
```
例: b_spec ∈ Q(ζ₁₇₆)⁺ vs √5/2 ∈ Q(√5), gcd(5,176) = 1 ⟹ 🔴 域分離（O201 T4b）。

### 第 6 步 — 輸出

```
{name, class, gates(12), density, dev, verdict, emoji, notes, derived_leaves,
 closure_trivial_leaves, exact_certified}
```

---

## 四、判級表（`V`, 14 codes）

| code | 級 | 意義 |
|:--|:--:|:--|
| `IDENTITY_OK` | 🟢 | 恆等式類, 精確證書 + `N_search = 1` |
| `MATCH_OK` | 🟢 | prediction 類, σ 內或密度通過 |
| `FORMAL_OK` | 🟡 | 形式通過但**冇密度基準/證書** ⟹ 未閉合 (O208) |
| `WEAK_DENSITY` | 🟡 | `q_obs ∈ (1%, 5%]` |
| `FALSE` | 🔴 | 等式唔成立 |
| `ILLEGAL` | 🔴 | 非法葉 (裸數/未註冊符號/異數) |
| `FITTED` | 🔴 | 含擬合常數 |
| `TAUTOLOGY` | 🔴 | 重言式 (O151) |
| `COINCIDENCE` | 🔴 | 跨框架巧合 (O151) |
| `MULTIPLIER` | 🔴 | 自由乘數 / 乘性修正承載匹配 (O204) |
| `NONUNIQUE` | 🔴 | 目錄表示非唯一 |
| `TRAP` | 🔴 | 陷阱窗 (O148/O151) |
| `DENSITY` | 🔴 | 密度基準失敗 (O208) |
| `FIELD` | 🔴 | 數域分離 (O201) |

**判級優先序**（`_decide`, 實測輸出）:

```
ILLEGAL → FITTED → FALSE → TAUTOLOGY → COINCIDENCE → MULTIPLIER(T3/T5)
  → FIELD → NONUNIQUE → TRAP → [identity?] IDENTITY_OK / MATCH_OK
  → DENSITY → WEAK_DENSITY → FORMAL_OK
```

原則 = **結構性判死先於數值性判死**:
- 語法/參數層 (ILLEGAL/FITTED) 先於數值層 — O201 之 ① → ③ → 數值 次序;
  （2026-09-28 修正: 曾把 G0 排第一, 令「含擬合常數且數值都唔對」之案例失去 `FITTED` 診斷信息)
- `FIELD` / `NONUNIQUE` 係**結構上不可能 / 結構上非唯一**, 強於 `TRAP`（精度論證）；
  故 A8 (`b_spec` vs √5/2) 同時觸發 G4 與 G6 時, 判級 = `FIELD`（G4 記錄於 gates 但不判死）

---

## 五、用法（pipeline）

```python
import o218_lib as L
P = L.closure_pool()

# 1. 恆等式 (已知閉合)
cert = L.certify_exact_numeric(L.sum_gamma(1, 44), 90)      # Σγ = 90
r = L.criterion("Σγ = B(N_d+1)/2", "Sigma_gamma", "B*(N_d+1)/2",
                "identity", P, exact_cert=("numeric", cert[1]))
print(r["verdict"], r["emoji"])        # IDENTITY_OK 🟢

# 2. 跨框架巧合 (已知判死)
r = L.criterion("b₁×30 = L₁₀", "b1_SM*30", "L_10", "pool_match", P)
print(r["verdict"])                    # COINCIDENCE 🔴

# 3. 複合救援式 (自由乘數 + 兩級測試)
fd = L.farey_density(0.02, 1e-9, L.q_max_for_form("quotient_product", 990))
r = L.criterion("(1/45)·(9/10) = 2%", "mdot_2pct",
                "mu2/(2*N_d+mu2) * N_gen**2/(N_gen**2+1)", "prediction_residual",
                P, density=fd, leading_dev=0.1111, target_precision=1e-4)
print(r["verdict"])                    # MULTIPLIER 🔴
```

---

## 六、已知限制（誠實清單）

```
🟡 G3 對「有出處之有理比」寬鬆 — 1/45 之類係合法葉, 佢嘅問題由 U/T5/G5 處理, 唔由 G3。
🟡 譜符號之**鏈標籤** (γ⁽⁸⁸⁾ / γ⁽¹⁷⁶⁾) 必須由呼叫者聲明, 引擎唔會自動推斷 (docs/06 §F)。
🟡 `WEAK_DENSITY` 判級已定義但**未有真實案例觸發** — 唔會為咗填滿判級表而調參數去命中 (docs/06 §E)。
🟡 判準只判「形式身份」, 唔判物理意義 — 標籤 (Higgs/W-field) 屬另一翻譯步驟。
🟡 密度 MC 只覆蓋可枚舉候選空間; 因子數 ≥ 3 之空間必須用 Farey 解析 (否則跑唔完)。
🔴 判準唔識自動生成候選表達式 — 候選仍要人/上游給, 判準只負責**判**。
```
