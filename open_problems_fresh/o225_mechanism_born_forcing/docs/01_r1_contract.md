# O225 docs/01 — R1 合約：機制層 Born 權重之障礙定理 ＋ 最小修改族（`r1-barrier-v1`）
> 凍結日 2026-10-01｜**先預註冊後運算**：本檔 P 表之期望值喺機器 `scripts/03_r1_barrier.py` **首次執行之前**寫死。
> 依據：`01_problem_record.md` §三 判決項 1–2；權威上游 = 憲章 `o222.../docs/45` §2 B3；診斷 = `docs/00_recon_inventory.md`。

## §1 操作空間（封死）
1. **只讀資產**：O222 凍結機器（`09_a2_rollback` 之輸入載入器 ＋ `12_b5_budget.load_machine` 之構造）。
   本 o **唔重推**該構造、**唔改** O222 任何檔案（跨 O 只經 register）。
2. **物件**：讀出表 `K ∈ {±1}^{120×62}`（態集 `S` = 120 個 2I 左正則態，凍結次序；context 集 `C` = 62 軸，凍結次序）。
3. **允許算子**：整數／`fractions.Fraction` 精確算術；`splitmix64`（O222 凍結 null 生成器，純整數）。
4. **禁止**：浮點（任何 `float` 字面值／除法）、`math`／`random`／`numpy`／`statistics` import、
   任何擬合、任何 per-state 自由參數（明文標示之最小修改族除外）、三角函數（複相位分析一律化為**秩判準**）。
5. **強制者**：`scripts/02_r1_contract.py` —— AST 掃描 `scripts/03_r1_barrier.py`（禁字集）＋ SHA-256 凍結 ＋ 陽性/陰性自測。

## §2 定義
- **D1 機制層權重族**：`W ∈ Q^{120×62}`，`W[s,a] >= 0`，且 `Σ_a W[s,a] = 1`（∀s）。
- **D2 態敏感**：`W` 之 120 行唔全同（否則 `W` 只係均勻測度之換殼，冇 context 條件信息）。
- **D3 結構生成族（允許清單，事先凍結）**
  ```
  族 A（仿射）      W = alpha·J + beta·X ，alpha,beta ∈ Q 全域（唔准 per-state）
  族 M1（複讀出）   W[s,a] = |alpha + beta·e^{i phi_a}·K[s,a]|^2，phi 全域或 per-context（無 per-(s,a) 相位）
  族 M2（非決定）   W = p 任意 ∈ [0,1]^{120×62}
  族 M3（多副本 k） X_k = K 水平重複 k 次
  最小修改族 Mk(m)  X' = [K | c_1 | ... | c_m]，每個 c_i ∈ {±1}^120 且 Σ_s c_i(s) = 0（保持軸平衡）
  ```
- **D4 障礙判準**：族 A 之歸一方程 = `n·alpha + beta·R(s) = 1`（`n` = 欄數，`R(s) = Σ_a K[s,a]`）。
- **D5 最小修復數**：`m_min(X) := min{ m >= 0 : ∃A 整數，|A − R_X(s)| <= m 且 A − R_X(s) ≡ m (mod 2) ∀s }`。
  （後一個同餘條件係必要：m 個 ±1 欄之和 `C(s) = Σ_i c_i(s)` 恆滿足 `C(s) ≡ m (mod 2)`。）

## §3 預註冊謂詞（**見數前**寫死；`[recon]` = 已於 recon 觀察之描述性事實，`[new]` = 本輪新定理主張）
```
P1  [recon] K 值重數 = {+1:3720, -1:3720}；每欄 Σ_s = 0 且恰 60 個 +1
P2  [recon] R(s) 恰取 {+10, -10}，60/60；Delta = 20
P3  [recon] rank_Q(K) = 6；相異 row = 12（重數全 10）
P4  [new]  ★ 障礙定理（充要）：族 A 存在「非負 ＋ 歸一 ＋ 態敏感」解
             ⟺ R 在 s 上恆常數。對凍結 K（R = ±10，非常數）之唯一歸一解 = (alpha,beta) = (1/62, 0)
             ⟹ W 恆等於均勻 ⟹ 態盲目（D2 失敗）。
             判準：① 方程組對 (alpha,beta) 之解集 = 單點 {(1/62,0)}（精確 Gauss）且 beta = 0；
                   ② 反事實（R 恆常之對照）：X' = [K | (−theta) x10]（n = 72, R' ≡ 0）⟹
                      解集 = { alpha = 1/72, beta 自由 }；|beta| <= 1/72 時非負、beta ≠ 0 時態敏感
                      （相異 row 數 = 12 = K 之相異 row 數）。
             ⚠️ 單欄（n = 63）**唔**可能修復：c = A − 10·theta 需取值 {0, 20}，唔屬 {±1}。
P5  [new]  ★ 最小修改數 m_min(K) = 10（`ceil(Delta/2) = 10` 且同餘條件成立，A = 0）
P6  [new]  ★ 唯一性：m = 10 之解被強制為 c_i = −theta（10 欄完全相同），且自動 Σ_s c_i = 0（平衡）
P7  [new]  ★ m <= 9 不可能：需要 max C − min C >= Delta = 20，而 |C(s)| <= m ⟹ 2m >= 20 ⟹ m >= 10
P8  [new]  ★ 多副本 M3：Delta_k = 20k，m_min(X_k) = 10k（k = 1,2,3,4 逐一驗）
P9  [new]  ★ 複讀出 M1 之 no-go：per-context 相位修復存在 ⟺ 線性系統 K·x = c·1 可解
             ⟺ 1 ∈ range(K) ⟺ rank[K|1] = rank(K)。實測 rank[K|1] = 7 > 6 ⟹ **不存在**。
             （全域相位：|e^{i phi}K| = 1 恆常 ⟹ 均勻 ⟹ 態盲目。）
P10 [new]  M2 之參數計數：W = p 需 120·(62−1) = 7320 個自由實數；凍結機器之可及隨機性 = log2(60) < 6 bits
             ⟹ M2「存在」但唔係由凍結機器生成（係加新獨立隨機源）。
P11 [new]  ★ 盲測（out-of-sample）：m_min 公式（D5）對**未參與定理推導**之表通用 ——
             (a) edge-only 子表（30 軸，Delta = 20）預測 m_min = 10；
             (b) vertex(12 軸)／face(20 軸) 子表（Delta = 0）預測 m_min = 0；
             (c) 200 個 O222 式隨機軸機器，逐個以 D5 精確計 m_min，並以**顯式構造**驗證修復成功。
P12 [new]  可證偽（硬測試③）：若存在任一表使「D5 所報 m_min 之修復構造」無法令 R 變常數
             （即在 m = m_min 欄內做不到），則 P5/P11 被否證。
P13 [new]  null（硬測試②）：N1 = 200 個隨機軸機器；N2 = 200 個隨機平衡 ±1 表 ＋ 解析界
             P(單一 row 之 #(-1) ∈ {26,36}) = 2·C(62,26)/2^62；120 個 row 全中 = 該值^120。
             預註冊預期：N1/N2 命中「恰兩值且其中一值為 -10、另一值為 +10」之次數 = 0。
```

## §4 判準與記帳
- 每條 P 一個 PASS/FAIL；`[PROOF]` 類（純代數不等式）另列，**唔入 PASS 分母**。
- PASS 分母只含可由機器重算之 check；結構聲稱另印 `[CLAIM]`。
- 四道硬測試：① 零參數（本輪全部由 K 與 group 決定，無自由擬合參數）② null = P13
  ③ 盲測 = P11（out-of-sample：子表與隨機軸機器）④ 剛性 = 擾動測試（翻轉一個 K 元素後 m_min 之變化，記入 docs/02）。
- **宣告上限**：本輪**唔**宣稱導出 Born 律；只判定（i）障礙之充要形式、（ii）最小修改族之行為。

## §5 產物
`scripts/01_recon_invariants.py`（15/15）｜`scripts/02_r1_contract.py`（強制者）｜`scripts/03_r1_barrier.py`（機器）｜
`scripts/04_r1_audit.py`（獨立審計，**不 import 03**）｜`data/01..04_*.json`｜`logs/01..04_*.out`｜本檔｜`docs/00`、`docs/02`。
