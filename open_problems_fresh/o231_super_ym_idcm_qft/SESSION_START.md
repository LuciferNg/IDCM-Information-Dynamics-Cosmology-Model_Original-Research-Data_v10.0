# O231 SESSION_START — 超楊-米爾斯 IDCM 解 vs QFT

<!-- registry
pid:     O231
title:   超楊-米爾斯 IDCM 解 vs QFT
state:   open
verdict: -
flags:   -
owner:   O231
created: 2026-10-04
updated: 2026-10-04
prereq:  O85, O142, O144
source:  用戶發起 O231
-->

> **Session**: 2026-10-04（新建立）
> **狀態**: 🟠 推導中
> **來源**: 調律者發起 — Claude (Anthropic, 2026-09-25) 計算了 planar N=4 Super Yang-Mills 九圈六粒子散射振幅，本 O 以此為契機，從 IDCM 角度重新詮釋散射振幅結構，並與標準 QFT 比較
> **前置**: O85 (SU(12) breaking Chain, SM 耦合結構), O142 (轉移矩陣第一性原理, 譜閉式), O144 (玻色子身份, sin²θ_W, α_s 公式)
> **位置**: `open_problems_fresh/o231_super_ym_idcm_qft/`

---

## 〇、調律者目標（原文引用）

> 「最近Claude 把量子場論中 超楊•米爾斯理論，首先尋找相關新聞並讀取其解決方案及答案，然後以IDCM角度找出解, 最後和量子場論之間進行比較」

### 任務分解
1. **新聞搜索 + 方案閱讀** — 已完成（2026-10-04）
2. **IDCM 角度找解** — 本 session 核心：用 IDCM 結構語言（K_chain ⊗ K_tree 譜、W-field 晶格、因果張量代數 𝒯）重新表達散射振幅的譜身份，而非微擾圈展開
3. **與量子場論比較** — 結構推導 vs 微擾展開，比較兩者對同一物理量（散射振幅）的處理方式

## 一、Claude 方案摘要（已完成閱讀）

### 問題
Planar N=4 Super Yang-Mills 的**六粒子(hexagon) MHV 散射振幅在九圈階**。

### Claude 解法（雙路線）
- **路線 A — 形狀因子路線**（主要）：bootstrap 九圈三點應力張量多重態的形狀因子（form factor）→ 通過 antipodal duality 映射到 Δ=0 奇偶守恆面上的振幅 → 以雙膠子通量管數據 (pentagon OPE T² 階) 固定剩餘歧義，提升離開該面
- **路線 B — 直接 bootstrap**：直接在 hexagon 函數空間中 bootstrap 九圈 symbol

### 關鍵數字
| 量 | 數值 |
|:---|:-----|
| symbol 空間維度 (weight-13) | 5,431 |
| 五重 coproduct 數 | 424 |
| 非零坐標 | 1,018,297（99.62% 可證為有理數）|
| 完整 weight-18 項數 | ~30 × 10⁹ |
| 七重 final entries | 8,028 |
| 計算成本 | ~$1,000-2,000 Claude 用量 + $100 (96 CPU 一週) |
| 驗證 | Lance Dixon 獨立確認；Song He 組同期幾乎獨立得出同一結果 |

### 方法論
- 使用 Fable 5.1 框架（Claude Science 平台內的 harness）
- 一句提示啟動，之後主要只重複「繼續做」
- 已知方法（bootstrap/antipodal duality/OPE），非新概念，但可靠性達到了可以無監督完成九圈的水準

## 二、IDCM 角度框架（候選框架 🔴 未驗證）

### D1 — 散射振幅的譜身份

在 IDCM 中，散射振幅不是微擾展開，而是 **K_chain ⊗ K_tree 譜的結構投影**：
- 耦合常數 = 譜結構數（α_s⁻¹ = F₆ + sin²θ_W + 1/B 式的閉式，而非 RGE running 積分）
- 質量 = `M₀ × γ_n × C_f`（譜模式投影，非 Higgs 機制循環修正）
- 振幅的「圈數」對應於 **晶格鏈上場相互作用的拓撲複雜度**，而非費曼圖的 loop order

### D2 — N=4 SYM 在 IDCM 語言中的身份

N=4 SYM 在 IDCM 眼中是一個**退化 toy model**：
- 超對稱等於**譜的簡併** — 不同模式的能量相等（SUSY 強制譜簡併）
- Planar 極限對應 **88-site 雙鏈的主扇區**（N_d = 44, 拓撲主極限）
- Bootstrap 方法中的 extended-Steinmann 約束對應 **K_chain 的因果結構**（因果張量 𝒯 = K_chain ⊗ K_tree 的自對偶條件）
- Antipodal duality 對應 **88-site 奇偶扇區對偶**（n ↔ 88−n 鏡像）

### D3 — IDCM 的「九圈」等價物

IDCM 不會計算九圈微擾項 — 而是問：
- 「散射振幅在 K_chain 譜上的結構身份是什麼？」
- 振幅的「度數」（= 參與模式數 × 頂點秩）取代 loop order
- 例如 O142 轉移矩陣已經閉合了譜的完全特徵值，散射 amplitude 是這些特徵值的結構泛函

### D4 — 比較維度

| 維度 | QFT 微擾法 | IDCM 結構法 |
|:-----|:-----------|:------------|
| 展開基礎 | 微擾 loop order | 譜模式深度 (mode index n) |
| 耦合 | RGE running, β 函數 | 結構常數（譜恆等閉式） |
| 主要技術 | Bootstrap + symbol + coproduct | 因果張量譜分解 + 扇區投影 |
| 收斂 | 需逐圈推進（人類: 8 圈, AI: 9 圈） | 一次性給出全階結構（Laplacian 特徵值完備） |
| 適用範圍 | 微擾可算的 QFT（N=4 SYM 最易） | 結構可閉合的譜幾何（IDCM 框架內） |
| 可證偽性 | 每圈可與實驗比較 | 譜結構數必須與所有觀測一致（零參數） |

## 三、先做嘅第一步

```
1. 撰寫 docs/01_claude_solution_summary.md — 詳細記錄 Claude 的解法（bootstrap × antipodal duality × OPE 三合一）
2. 撰寫 docs/02_idcm_scattering_framework.md — 由 O85/O142/O144 提取 IDCM 的散射振幅語言
3. 撰寫 docs/03_qft_vs_idcm_comparison.md — 系統比較兩條路線
4. 實作 scripts/01_kchain_scattering_operators.py — 用 K_chain 譜構造散射算子的結構形式
5. 實作 scripts/02_coupling_structure_vs_running.py — 比較結構耦合 vs RGE running
```

## 四、已知陷阱

```
⚠️ N=4 SYM 是 toy model，IDCM 推導的是真實 SM — 兩者的「散射」概念不同層次，不能混淆爲同一物理量
⚠️ IDCM 沒有 loop expansion — 比較時要用「譜深度」代替「圈數」，避免類別錯誤
⚠️ 不要試圖用 IDCM 重算九圈振幅（IDCM 不做微擾展開），而是要問「IDCM 的散射振幅概念是什麼」
⚠️ Bootstrap 方法用了 extended-Steinmann 約束和 antipodal duality — 這些在 IDCM 中有沒有結構對應需要考證，不能保證存在
⚠️ IDCM α_s 公式已被 O144 docs/20 判 🔴 非閉合（α_s⁻¹ = F₆ + sin²θ_W + 1/B 係擬合產物）— 引用時必須標明
```

## 五、關鍵數字

| 量 | 值 | 出處 |
|:---|:---|:-----|
| Claude 九圈振幅圈數 | 9 loop | Anthropic 2026-09-25 |
| 先前紀錄 | 8 loop (Lance Dixon & Andy Liu 2023) | arXiv:2308.08199 |
| symbol 空間維度 | 5,431 (weight-13) | smsharma.io/cosmic-nine-loops |
| 非零坐標 | 1,018,297 | 同上 |
| IDCM sin²θ_W (mode-ratio) | 0.220776 | O144 docs/19 |
| IDCM N_d | 44 | O95 |
| IDCM B | 4 | O34 |

## 六、交接 / 依賴

```
- 前置: O85 (SU(12)→SM 耦合結構), O142 (轉移矩陣譜閉式), O144 (玻色子身份, sin²θ_W, α_s)
- 前置: O86 (SM×IDCM×GR Lagrangian), O210 (因果張量代數 𝒯 = K_chain⊗K_tree)
- 範圍: 唔重做九圈計算（Claude 已做）— 只提供 IDCM 結構詮釋與比較
- 範圍: 唔推導新耦合公式（α_s 公式脆弱，留 O142）— 只引用已有閉合結果
```

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**
> 當前狀態以 `open_problems_fresh/README.md` 為準；生命週期事件以 `problem_register/` 為準。