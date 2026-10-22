# O225 docs/03 — R2 合約：G1 完整語義表 ＋ 動態側 17 全枚舉（`r2-g1-dyn-v1`）
> 凍結日 2026-10-01｜**先預註冊後運算**：下表 P-期望值於 `scripts/11_r2_g1_table.py`、`scripts/12_r2_dyn17.py` **首次執行之前**寫死。
> 依據：`01_problem_record.md` §三 判決項 3（動態側 17）、4（G1 完整語義表）｜診斷：R1 已閉合 part 1/2（`docs/02`）。
> 上游權威：O222 `docs/40`（R26 G1/G8）、`docs/41` §17 掃描、`docs/44` Q5；實作：`scripts/30` `ledger_replay`、`scripts/18` `replay_protocol`、`scripts/65/66`、`scripts/70`。

## §1 操作空間（封死）
1. **凍結協定（逐字沿用 O222 `scripts/30_g1g8_gaps.ledger_replay`）**：pair 序 = `[(a,b)]` 之 lex 序（或其 5 種 variant，見 §2）；`COST = 123/88`、`EMIN = 123/176`、`BUDGET = 10^9`、`order = [(a,b) for a in range(62) for b in range(62)]`；讀三步（a、b、pop 後重讀）、memo 單值、命中 = 值級比較。
2. **機器**：`o222/scripts/12_b5_budget.load_machine() → (mm, K, MUL, hx, idx, types)`（唯讀）。**唔准**改 O222 任何檔。
3. **校準閘（R2 之 entry gate）**：本 o 之 replay 與 `o222/scripts/18_d6_mapping.replay_protocol` 逐 pair 0 mismatch（`misses`、`top`、`ledger_len` 三欄全對）。唔過閘 ⟹ 全部結果作廢。
4. **允許算子**：整數／`Fraction`；`splitmix64`（整數）；**禁止**：浮點、`math`／`random`／`numpy`／`statistics`／`cmath`、擬合、per-state 自由參數。
5. **強制者**：`scripts/10_r2_contract.py`（AST 禁字掃描 ＋ 陽性對照（必須拒）＋ 合約標籤檢查 ＋ SHA-256 凍結 ＋ GATE OPEN/CLOSED）。

## §2 定義
- **D1 運行量族 Q（凍結，參數為零）**：對每個 (order, s0) 之 replay，記錄以下量（全部為該軌跡之函數）：
  ```
  q1  hits              q2  overrides            q3  stale              q4  agree_repeat
  q5  overrides_first   q6  #visited states      q7  #distinct (s,ctx)  q8  #distinct ctx
  q9  ledger_len(final) q10 Σ misses = pass reads q11 miss histogram 之鍵集合 + 各鍵計數
  q12 pair-level top 之分佈    q13 first_hit 之 pair 數    q14 non-first hit 之 pair 數
  q15 軌跡態序列之前週期／循環長（週期檢測）
  ```
- **D2 兩種「17 缺席」判準（本輪分開測，唔准混）**：
  ```
  M-value : 17 ∉ V ，V := ⋃_{order,s0} {q 之所有取值}（含 histogram 鍵與計數）
  M-div   : 不存在 v ∈ V＼{0} 使 17 | v
  ```
  O222 `scripts/70` P2 只做 M-div 且用**手寫**清單；本輪兩者都做，且值域係**機械**收集。
- **D3 結構數清單（沿用 docs/41 §17 掃描之凍結列表，逐項重算因式分解）**：
  `{62, 120, 3844, 7440, 11532, 124, 7564, 4728, 44, 88, 176, 60, 990, 12, 20, 30}`。
- **D4 階級分拆（R2A 之刻畫用，全部機械判定常數性）**：
  (P1) `s0` 之 K-row 類（12 類）｜(P2) `s0` 之 2I 共軛類（9 類）｜(P3) `s0` 之元素階（1,2,3,4,5,6,10）｜
  (P4) 中心對 {s, −s}（60 類）｜(P5) 由 ctx 距離三軌道導出之態側等價（3 類）。

## §3 預註冊謂詞（**見數前**）
```
P1  校準閘：replay 與 I7 `replay_protocol` 逐 pair 0 mismatch（3,844 pairs）
P2  [upstream] hits ≡ 124 = 2N 對全部 120 個 s0 恆定
P3  [upstream] overrides(s0) ∈ [52, 80]，且恰 26 個相異值
P4  [upstream] 校準 s0 = 0 → overrides = 65
P5  [upstream] 恆等式 overrides = stale = hits − agree_repeat（120/120）
P6  [upstream] #ctx = 62、#distinct (s,ctx) = 4728、#visited states = 120（全部 s0 相同）
P7  [upstream 誠實記錄] 記錄所載「58 出現於 28/30、10 個態給 65」**不可重現**；本輪要報實測
    histogram；預期 58 出現 1 次、65 出現 3 次、68 出現 10 次（依 docs/40 §一）
P8  [new] ★ 刻畫：overrides(s0) 在哪個分拆上恆定？逐個測 P1–P5；報**最細**之恆定分拆
    （預期：P1/P2/P3/P4 皆唔恆定；若 P5 恆定則 G1 語義降為 3 類定律）
P9  [new] ★ 完整表：全 120 列 (s0, q1..q9) 入 data/11_r2_g1_table.json（唔抽樣、唔截斷）
P10 [new] ★ M-value：17 ∉ V（機械值域）—— 註 O222 從未測 value 判準
P11 [new] ★ M-div：17 ∤ v ∀v ∈ V＼{0}
P12 [new] ★ 陽性對照（非空洞）：同一掃描器必須**報出**已知在場之數（62, 120, 124, 4728, 3844, 7440）
P13 [new] ★ 植入對照：把一個人造量 q* ≡ 17 加入族 Q ⟹ 掃描器必須命中 17（證明 NOWHERE 非掃描器壞）
P14 [new] ★ 素支撐：V 之素因子支撐 = {2,3,5,31,61}（或實測值）；並判 17 ∉ 該支撐
P15 [new] ★ D3 清單：17 唔整除任何一項（重算因式分解，逐項列出）
P16 [new] 五種 order（lex/diag/antidiag/block/stride）之下，M-value 與 M-div 仍成立
    （預期：hit/override 之值集隨 order 改變，但 17 仍缺席）
P17 [new] 可證偽：若任何 (order, s0) 使某 q = 17 或 17 | q（q ≠ 0），則 P10/P11 否證
```

## §4 四道硬測試
```
① 零參數：Q 全由凍結協定決定；無自由參數（僅 §2 D1 之凍結清單）
② null：本項無 MC 需求（**全枚舉**取代抽樣）；取而代之 = 陽性對照 P12 + 植入對照 P13（掃描器之有效性檢定）
③ 可證偽＋樣本外：P17；另以 5 種 order（其中 4 種未參與上游推導）作 out-of-sample
④ 剛性：擾動測試 = 改一個 K 元素後重掃（報 17 是否出現）；另測「移除 tie 條目」之 M-b 變體讀出表（R1 之 K_b）下 17 是否出現
```

## §5 產物
`scripts/10_r2_contract.py`（強制者）｜`scripts/11_r2_g1_table.py`（R2A）｜`scripts/12_r2_dyn17.py`（R2B）｜`scripts/13_r2_audit.py`（獨立審計）
`docs/04_r2_results.md`｜`data/10..13_r2_*.json`｜`logs/10..13_r2_*.out`｜MANIFEST 更新｜register `O225/R2`（預註冊先於運算）。
**宣告上限**：本輪只判（i）G1 之完整表與分拆刻畫、（ii）17 於凍結運行量族之缺席（值判準＋整除判準）＋ 掃描器有效性。**唔**宣稱「17 於任何可能意義下皆不可能出現」。
