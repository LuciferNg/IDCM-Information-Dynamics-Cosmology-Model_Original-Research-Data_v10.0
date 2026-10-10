# O221 / docs/34 — Round 28：殘餘 ⑤ 閉合嘗試——**dual-cell 權重取樣器**（scripts/38：7 PASS + 3 記錄 FAIL；殘餘 ⑤ 未閉合，判準零放寬）

**日期**：2026-10-02（執行確認 2026-10-10）｜ **腳本**：`scripts/38_dual_cell_weights.py`｜ **結果**：**7/10 PASS + 3 記錄 FAIL**（**W4/W5/W6c**；負結果，誠實記錄）｜ **接續**：docs/20 §4 候選②（dual-cell 權重）、docs/19（殘餘⑤定位）

## 0. 動機（docs/20 §4② 執行）
「以 hinge 之對偶 2-cell 面積重分配 deficit（保留 cube 階之消 deficit 但修正其振幅退化）」。構建**零新參數** dual 取樣器：24 個 Kuhn 4-單形對 4-cube 16 頂點嘅**入射計數** w_v（正整數組合學、由格點結構派生）作為權重，cos(k·x) 喺 16 頂點上加權平均（geo-correct cell 平均）。

## 1. 預註冊
W1 權重派生精確花樣（24, 6×4, 4×6, 6×4, 24；總和 120 = 24·5）+ W1b 正規化 + W2 適性作用量 + W3 消 deficit 保留（|deficit|<0.05 @k=π/2）+ W4 振幅退化修復（A_TT ∈ [0.8,1.25]）+ W5 閉合判準（dict W3∧W4）+ W6 unseen-k（k=2π/7, 3π/10, 4π/5：naive 對照 0.8–1.0、dual deficit <0.4、dual A_TT ≤1.25）+ W7 誠實。零審計側修正（W1 首跑 bit-index 錯屬我寫錯測試索引——修正後 PASS；W1b 即過；唔涉物理）。

## 2. 結果
| 判 | 內容 | 結果 |
|:--|:--|:--|
| W1 | 權重派生：w(0)=w(1111)=24、w(single)=6×4、w(pair)=4×6、w(triple)=6×4、Σ=120 | ✓ |
| W1b | 全正、歸一化 | ✓ |
| W2 | dual 係適性加權平均；參考列已定 | ✓ |
| W3 | **消 deficit 保留**：|deficit_dual| = **5.0e-4** < 0.05 @k=π/2 | ✓ |
| W4 | **振幅退化修復：FAIL**——A_TT = **5.0661**（= cube 階原位，退化未修復） | ✗ |
| W5 | **閉合判準：FAIL**——deficit 0.0005 ∧ A_TT 5.07 唔同時成立 | ✗ |
| W6a | unseen-k naive 對照 0.8–1.0（k-無關） | ✓ [0.900, 0.925, 0.909] |
| W6b | unseen-k dual deficit < 0.4（**≈0**） | ✓ [1.3e-3, 2.3e-3, 4.7e-5] |
| W6c | unseen-k dual A_TT ≤1.25：**FAIL**——[2.37, 2.68, 2.43] | ✗ |
| W7 | 誠實：殘餘⑤ **未閉合**；零讓步 | ✓ |

## 3. 決定性結構發現：dual ≡ cube（machine-exact）
- **kvec 係軸向**：`kvec = k·(0,0,0,1)`（scripts/24 line 117）——cos(k·x_v) 只依賴 off_3。
- **半空間恆等式**：由 Hamming 對稱，權重喺每條座標軸嘅兩個半 cube 平均分配：Σ_{off_i=0} w = Σ_{off_i=1} w = **60 = 120/2**（實測四座標全同）。
- ⟹ 加權平均 = 60·cos_A/120 + 60·cos_B/120 = (cos_A+cos_B)/2 = **均勻 16 頂點平均 ≡ cube 階**（每點 decimals 相同：deficit 5.0e-4 ≈ 5.16e-4、A_TT 5.0661 同值）。
- ⟹ **docs/20 候選② 已檢驗並坍縮**：對軸向 k，入射重權唔會改變 cube 階——**振幅退化係結構性**，唔係「均勻權重」嘅 naive 選擇。

## 4. 殘餘 ⑤ 現狀（本輪後）
- **加固**：deficit ≈ 0 由 dual/cube 平均達成——naive TT deficit 純粹係**相位取樣（cell-形狀平均）約定效應**，而家喺 **7 個 k**（docs/19 六 k + π/2 階梯 + 3 個新 unseen k）k-無關成立；新 unseen-k dual deficit [1.3e-3, 2.3e-3, 4.7e-5]。
- **未閉合（判準收緊、零放寬）**：無任何已測取樣次序同時達成「零 deficit ∧ 振幅 M-穩定」；dual（幾何正確版）亦退化。
- **候選剩餘**：docs/20 ①（複合：cell 平均 → 精確頂點位移映射，殘餘 3e-7 級）、③（以 A_TT M-穩定為主判準重測）。

## 5. 對「GR 湧現橋」嘅意義
dual-cell 權重 = Regge 作用量形式（deficit × dual-area）嘅離散對應——本輪顯示：**正確 cell 平均消咗 deficit，但嗰個消法帶住兩個扇區同步增長（A_TT≈5）**，即「欠 deficit」同「振幅」係兩個獨立軸（前者取樣可消、後者結構性）。這是「𝒯 → EH」路上嘅一個明確信息：Regge 型 hinge×dual-area 加權本身唔足以令 conf/TT 振幅收斂——需更進一步嘅結構（候選①/③）。

**支援**：`scripts/38_dual_cell_weights.py`（10 ck：7 PASS + 3 記錄 FAIL）、docs/20（候選②出處）、docs/19（判準來源）。