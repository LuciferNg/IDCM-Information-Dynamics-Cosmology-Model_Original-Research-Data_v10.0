# docs/04 — O222 / B2 結果：C(θ) 由 2I 群元素在 62 條晶格軸上的重疊分佈導出

**狀態**：共存層（coexistence level）導出**完成**（負面結果，見 §0）；rollback / sequential 層**未定義**（需修正 A2）。
**合約**：`docs/03_b2_contract.md`（Contract v1，frozen，sha256 `01d2fb03…`）——本文件**唔改**該檔任何一行；所有修訂記於 §6。
**強制者**：`scripts/04_b2_contract.py`（sha256 `830dbf75…`；14/14 PASS，GATE = OPEN）。
**凍結實作**：`scripts/05_b2_correlation.py`（sha256 `be946911c087862d7bd02b460235b0b47fe1ff4ed85d2a855b6855f717e49235`）。
**獨立核對**：`scripts/06_b2_gpu_verify.py`（cupy int64，GTX 1060 3GB；見 §7）。
**結果**：凍結輪 18/18 PASS（`logs/05_b2_correlation.out`）；reveal 輪 19/19 PASS（`logs/05_b2_correlation_reveal.out`）。

---

## 0. 一句話結論

1. **共存層 kernel 係古典嘅**：`C[a][b] = (1/120)Σ_{g∈2I} sign(u_a·(g n̂))·sign(u_b·(g n̂))`，`|S| ≤ 2` 精確成立（LHV-class，符合預註冊 P2），**冇任何超額**。
2. **`C ≠ −cos θ`（逐點）**：全 3844 對中只有 **634 對** C² 精確等於 cos²θ（全部係平凡巧合：`|C|=1 ⟺ |cos θ|=1` 與 `C=0 ⟺ cos θ=0`）；其餘系統性偏差，最大 `|Δ| = 8/9`。C 只取 **7 個值** `{0, ±1/3, ±2/3, ±1}`（分母 120）。
3. **原始「|S| = 2」有兩個平凡來源**：對蹠 setting（任何 sign kernel 都 `C = −1`）＋ 重複/相反分區（`C = ±1`）。剔除後，在**匹配嘅 12 頂點子集**上晶格 `|S|max = 4/3` **低於**隨機 unit-quaternion null 嘅中位數 `22/15 ≈ 1.467` ⟹ 晶格在共存層**唔比隨機更「量子」**。
4. ⟹ 若 QM 語義（C = −cos θ、CHSH 超額、Born 權重）要出現，**必須**在 rollback / sequential（不可逆對賬）層，而唔係共存層。呢個正係合約 §3 預先指定嘅架構（P3），亦係下一步唯一有價值嘅方向。

---

## 1. 定義（全部由 docs/03 §3 凍結，此處只重述）

- **群**：`G = 2I`（120 個單位 quaternion，精確 Q(√5)）；對照 `I60`（60 個旋轉，`±q` 同一元素）；另報 `I_h`。
- **Setting 集**：**62 條晶格原生軸**，全部由群元素階導出（無人手選）：12 頂點（階 5）／20 面心（階 3）／30 邊中點（階 2）。方位定向與否皆精確。
- **Kernel**：`K(g,a) = sign(u_a · (g n̂))`，平局按 **H3**（取 u 首個非零分量符號）**指派**（非排除）。
- **關聯**：`C[a][b] = Σ_g w(g) K(g,a) K(g,b)`，`w = 1/120`（uniform on 2I）⟹ 精確有理，分母 120。
- **掃描**：**全部 62² = 3844 有序對**（無選點；選子集本身即超參數）。DEV `V×V` = 144（reveal 前唯一可見）／BLIND = 3700（凍結後才揭示，sha256 `1b0420a6…`）。
- **禁令**：無三角函數、無浮點字面值、無 `−cos θ` 補丁、無擬合；比較用**精確代數** `C² ≟ cos²θ ∈ Q(√5)`。

---

## 2. 結構驗證（凍結輪 PASS 清單要點）

| 檢查 | 結果 |
|---|---|
| P0 結構復現 | `\|2I\| = 120`、`\|I\| = 60`、軸 62（V12/F20/E30）|
| P0b 重數精確 | 每條頂點方向被擊中 **10 次（2I）／5 次（I60）**；`12×10 = 120`、`12×5 = 60` |
| P0c 雙路徑 | 快速頂點表 == 直接 120 元素 loop（行多重集、平局、全部 144 個 DEV 關聯）→ 0 不符 |
| P1 marginal | **每條軸 1/2 精確**（2I 與 I60 皆是）；非零 marginal 0/62；平局事件（ref V00）1200 |
| P1b H4 穩健 | 62 個參考軸 × 12 頂點：marginal 全消 0，違反 0 |
| H5 局域性 | `C(a,a) = 1` 精確；因子表只含單 setting |
| L-SET2 | setting 集含 **31 對對蹠軸**（⟹ 全部 CHSH 陳述須同時報 raw 與 antipodal-free，見 A4）|

**平局的結構來源**：邊中點軸恰 **⊥ 4 個頂點方向** × 重數 5 = **20 平局/軸**；指派後 7200 個平局事件、0 不平衡 ⟹ `P = 1/2` 連平局仍精確（A1）。

---

## 3. 結果 A：C 表結構

- C 只取 **7 個值**：`{−1, −2/3, −1/3, 0, +1/3, +2/3, +1}`（分母 120）。
- `C = ±1` 只可能來自：① 對蹠軸對（`u_b = −u_a`）② 兩軸在 2I 軌道上有**相同/相反**的符號分區（e.g. `C(V00,E31) = +1`、`C(V00,E57) = −1`）。
- 類型均值（`mean|C|`，reveal 輪）：

| 類 | n | mean\|C\| | max\|C\| |
|---|---|---|---|
| V×V | 144 | 4/9 ≈ 0.4444 | 1 |
| V×F | 240 | 1/3 ≈ 0.3333 | 2/3 |
| V×E | 360 | 11/27 ≈ 0.4074 | 1 |
| F×F | 400 | 2/5 = 0.4 | 1 |
| F×E | 600 | 16/45 ≈ 0.3556 | 1 |
| E×E | 900 | 53/135 ≈ 0.3926 | 1 |

（V×V 嘅 12 軸子集：`mean|C| = 1093/2883 ≈ 0.3791`。）

---

## 4. 結果 B：與 `cos²θ` 嘅精確代數比較（**無 tolerance 可調**）

- **DEV（144 對）**：精確吻合 **24/144**；`max |Δ| = 4/45`。
- **全網格（3844 對）**：精確吻合 **634/3844 = 16.5%**；`max |Δ| = 8/9`。
- 吻合全部屬**平凡**類：`|C| = 1 ⟺ cos²θ = 1`（同向／對蹠／重複分區）與 `C = 0 ⟺ cos²θ = 0`（軸互相垂直）。其餘：`|C| = 1/3 ⟺ cos²θ = 1/5`（`1/9 vs 1/5` ✗）、`|C| = 2/3 ⟺ cos²θ = ?` 等，系統性唔等。
- **判定（P4s）**：共存層 kernel **唔**重現 `−cos θ`。呢個係精確陳述（`C²` 與 `cos²` 都在 `Q(√5)` 內，逐對比較係整數運算），唔涉及任何數值容差。
- 結構解讀：`C_coex` 係「兩個符號分區嘅一致率」= **step kernel**（分段常數），六面體/二十面體角度落喺 `{0, ±1/3, ±2/3, ±1}` 幾格；`−cos θ` 係連續函數。兩者只在退化點相交。

---

## 5. 結果 C：CHSH（共存層）

| 統計量 | 值 | argmax |
|---|---|---|
| P2 全 62⁴（14,776,336 有序 tuple） | \|S\| = **2** | `(V00,V00,V00,V00)` — **退化**（四 setting 相同）|
| P2e 四 setting 相異（13,388,280 tuple） | \|S\| = **2** | `(V00,V01,V10,V04)` — 含**對蹠對** `(V01,V10)` |
| P2g **antipodal-free**（A4） | \|S\| = **2** | `(V01,V04,F01,V00)` — 四 setting 相異、無對蹠對，四項 `C` ∈ {±40,±80}/120（**非平凡**）|
| P2d 符號約定不變性 | 四個減號位置 → max 全 = 2 | — |
| H1 度量對照（I60 vs 2I） | 兩者皆 2 | — |
| P6 ablation（獨立抽樣） | `C ≡ 0` 精確（靠恆等式 `Σ_g K(g,a) = 0`；實例雙重和驗證 10 對）| — |

**三重平凡性分析（誠實披露）**：
1. 原始 max 由 `(V00,V00,V00,V00)` 達成（`1+1+1−1 = 2`）⟹ 與群無關，等於冇測 → 改用四 setting 相異統計量（A3）。
2. 四 setting 相異之 max 仍經對蹠對達成（對蹠軸 `C = −1` 對**任何** sign kernel 都成立）⟹ 改用 antipodal-free（A4）。
3. 全 62 軸下 antipodal-free 仍達 2（`(V01,V04,F01,V00)`，四項 `C` 皆 40–80/120，**無** `|C| = 1`）⟹ **呢個先係真嘅非平凡飽和**：晶格在共存層**確實**達到古典上界（`|S| = 2`），但**唔超過**（無 Tsirelson 型超額：`|S|² = 4 < 8`，精確有理比較）。族內設定（12 頂點）嘅 antipodal-free max 只有 **4/3**。

**與 null 嘅配對比較（同 12 頂點 setting）**：
- 晶格（12 頂點、antipodal-free）：`|S|max = 4/3 ≈ 1.333`。
- 隨機 rational unit-quaternion null（seed 222，500 draws，同一統計量）：median `22/15 ≈ 1.467`、95th `8/5 = 1.6`、max `26/15 ≈ 1.733`。
- ⟹ 晶格值**低於**隨機 null 中位數 ⟹ **共存層冇「量子性」超額**（負面結果）。null (i)（10⁴ 隨機方向對）亦一致：null `mean|C| = 1973/5000 ≈ 0.3946` 對晶格 `1093/2883 ≈ 0.3791` ⟹ 晶格唔比隨機更相關。

---

## 6. 合約修訂記錄（A1–A4）——連「moving goalposts」的誠實標記

**原則**：docs/03 凍結後任何改動 → 版本 +1、新 hash、新文檔、明寫。以下四項全部發生喺**寫 05 之後、任何最終數字之前或同時**，且**冇一項**係為咗令結果更似 QM：

| # | 內容 | 時間點 | 影響判定？ |
|---|---|---|---|
| **A1** | 平局按 H3 **指派**（非排除）；`P1b` 段加入 | 見到「max tie count = 20」之後 | 否（marginal 1/2 仍精確）|
| **A2** | rollback / sequential 層之構造**仍未定義** → P3 標為 NOT COMPUTED | 一開始 | 是（P3 冇數）——**未**執行 |
| **A3** | CHSH 統計量改為「四 setting 相異」（原統計量被退化 tuple 支配）| R5，見到 argmax = `(V00,V00,V00,V00)` 之後 | 否（raw 與 distinct 都 ≤ 2，判定不變）|
| **A4** | 新增 **antipodal-free** 統計量（原 max 由對蹠對達成，對任何 kernel 皆然）| R10，見到 null 亦 = 2 之後 | 否（新增統計量；raw/distinct 值仍完整保留）；**削弱**表面結果 |

**判準**：A3/A4 係「統計量定義修正」，兩者皆**向下修正**（令結果睇落更弱），並且原始統計量全部保留在同一份報告中；`docs/03` 內 H8 預註冊窗口（`|S|` vs 2、`|S|²` vs 8）**從未改動**。若日後要改窗口本身 = Contract v2（另開文檔、另開 hash）。

---

## 7. 獨立 GPU / 精確整數核對（scripts/06）

**目的**：用**唔同實作 + 唔同硬件 + 純 int64**（`p+q√5 → (P,Q)` 整數對，用 `A² vs 5B²` 判號）重算凍結結果；兩者必須**逐位一致**，否則其中一個錯。**完全不碰凍結 hash**（06 唔改 05，唔改 docs/03）。

| 檢查 | 結果 |
|---|---|
| G1 相關表 | GPU int64 表 == 凍結 CPU 精確表，**3844/3844 全等，0 不符**（分母 120，`\|G\| = 120`）|
| G2 全 62⁴ sweep | GPU max `240/120` == 凍結 `240/120`，argmax 相同 `(V00,V00,V00,V00)` |
| G3 四 setting 相異 | GPU `240/120`、argmax `(V00,V01,V10,V04)` == 凍結記錄（`logs/05_b2_correlation.out`）|
| G4 null (ii) 500 draws | GPU median/95th/max == 凍結 `22/15 / 8/5 / 26/15`（逐 draw 完全一致：同一 splitmix64、同一採樣器、同一統計量）|
| 結構恆等式 | GPU 自行重算 2I 軌道：12 頂點方向 × **重數 10**（總 120）——唔假設，重算 |

**最終**：`scripts/06_b2_gpu_verify.py 500` → **4/4 PASS**（`logs/06_b2_gpu_verify.out`；GPU = GTX 1060 3GB）。核對用嘅係**唔同實作 + 唔同硬件 + 純 int64**；凍結檔（`docs/03`、`scripts/05`）**一個 byte 都冇改**。

**GPU 端自身捉到嘅四個 bug（06）**——記錄以免重犯：
1. **方向表重數**：全部算成 1（只 12 方向而非 12×10）⟹ 整張表同凍結值不符（G1 FAIL）。已在 06 內自行**重算 2I 軌道**取重數（唔假設 = 10）。
2. **null 對蹠表**誤用展開後（120 項）方向表 ⟹ 對蹠判斷全錯。
3. **旋轉矩陣公式手寫錯**（`r1_ = C0·e0 + C2·e2 − C3·e1`，冇平方項）⟹ GPU null 同 CPU null 唔一致；已改標準四元數旋轉矩陣（整數分子/n²）+ 加**正交性 assert**（`Rnum Rnumᵀ = n⁴ I`）。
4. **mask 漏兩個「四 setting 兩兩相異」約束**（漏 `a′≠b`、`a′≠b′`）⟹ 容許重用 setting 嘅 tuple，得出 `|S| = 236/120`（該 tuple 為 `(a=0,a′=1,b=1,b′=6)`）；補齊六對全部約束後 G4 逐 draw 完全一致。**教訓：四元 tuple 嘅相異約束有六對，唔可以只寫「同 a 唔同」+「b≠b′」**。
5. （另）06 曾自帶舊 LCG，令 G4 實際比較兩個唔同 null ⟹ 已改為與 05 逐 byte 相同嘅 splitmix64。

---

## 8. 推導過程捉到嘅真 bug／陷阱（方法論資產）

1. **非單位四元數**：`d = inv(ONE + (r2, F(0)))` 中 `ONE + tuple` 係 **tuple 串接**（唔係 Num 加法）⟹ 分母變 1 ⟹ 隨機四元數唔歸一 ⟹ null 退化。已加硬護欄：每個 q 檢查 `q q* = 1`（P5b0，500 draws，0 非單位）。
2. **弱 LCG**：乘積式 LCG 細模（`% 13`）週期短，連續抽取相關 ⟹ 換 splitmix64 混合器（純函數、無 import、seed 222）。
3. **立體投影採樣本質上只覆蓋 identity 附近**：細參數聚喺 identity，大參數趨向 `(−1,0,0,0)`（在 SO(3) 中與 identity 同一旋轉）⟹ **兩種 regime 都退化**（null marginals ±76…120，而隨機集應為 ±11）。最終改用 **Pythagorean 四元數拒絕採樣**（`a²+b²+c²+d² = n²`，`q = (a,b,c,d)/n`），覆蓋 S³ 且保持精確有理。護欄 P5b1：每 draw ≥ 100 個相異旋轉、null marginal 在隨機遊走尺度。
4. **日誌新鮮度**：R10 凍結輪因 `is_antipodal` 未定義而在中途 crash，但 `logs/05_b2_correlation_reveal.out` 與 `logs/06…out` 仍然係上一輪（R9）舊貨 ⟹ **唔可以只睇 log 內容**，必須核對 mtime／gate 狀態／impl hash。

---

## 9. 對 O222 主問題（IDCM↔QM 連接）嘅裁決

- 共存層（single-setting distribution、無對賬）：**古典、LHV、CHSH 無超額、kernel ≠ −cos θ**。
- ⟹ 「IDCM = QM 之離散實現」在共存層**唔成立**（同時亦**唔被否證**：QM 語義本來就唔應該住喺共存層）。
- 唯一仍然開放嘅位置 = **rollback / sequential 層**（thunk/force 之不可逆對賬，O222 §3 之 L3）。呢層需要先有**定義**（A2）：寫入凍結合約（新 hash）＋新預註冊窗口，然後才可按同一紀律出數。此即 P3，目前報 `NOT COMPUTED`（誠實留白，非隱藏）。

---

## 10. 下一步（按合約紀律）

1. **A2**：rollback 層 C(θ) 之構造定義 + 預註冊窗口（新 doc，新 hash；**必須**在見數前凍結）。
2. **B3**（CHSH 盲測）、**B4**（no-signalling **推導**：二十面體中心對稱 ⟹ 任一方向 6 正/6 負 × I-軌道重數 5 = 30/30 精確）、**B5**（接 D5 回滾）。
3. 若 A2 凍結後 rollback 層仍無 `−cos θ`，則 B2 全案（共存 + rollback）為**否證性結論**：IDCM 嘅 QM 連接唔在關聯函數層，需回到 W-field 相位模／測量層（O138）另找接口。

---

## 11. 重跑指令

```bash
cd open_problems_fresh/o222_qm_evaluation_semantics
/usr/bin/python3 scripts/04_b2_contract.py                          # 14/14, GATE 狀態
/usr/bin/python3 scripts/04_b2_contract.py --freeze-impl scripts/05_b2_correlation.py
/usr/bin/python3 scripts/05_b2_correlation.py                       # 凍結輪 18/18（DEV 可見，BLIND 隱藏）
/usr/bin/python3 scripts/05_b2_correlation.py --reveal              # 19/19（全 3844 對聚合）
/usr/bin/python3 scripts/06_b2_gpu_verify.py 500                    # GPU 精確整數獨立核對
```

**產物**：`data/05_b2_correlation.json`（3844 精確分子／分母 120）、`data/05_b2_dev_values.json`、`data/05_b2_blind_values.json`、`data/05_b2_results.json`、`data/06_b2_gpu_verify.json`、`data/04_b2_freeze_r11.json`（impl hash `be946911…`）。

---

## 12. 執行／工具注意（實錄踩過）

1. **`scripts/04_b2_contract.py` 唔加 `--freeze-impl` 會報 1 FAIL（`[contract] unfrozen implementation present`）並重寫 `data/04_b2_freeze.json` 嘅 `frozen_at`**（impl hash 與 gate 狀態不變）。⟹ 驗證**必須**用 `--freeze-impl scripts/05_b2_correlation.py`（該模式 14/14 PASS，並重記同一 impl hash）；純跑（無旗標）唔可以當「驗證通過」，亦唔可以當凍結記錄。
2. **日誌新鮮度**：log 檔內容唔可以單憑「有 PASS 行」就信 —— 必須核 `mtime` / gate 狀態 / impl hash。實錄：R10 凍結輪因 `NameError` 中途 crash，但 `05_..._reveal.out` 與 `06_...out` 仍是上一輪（R9）舊貨，一度令人以為「已重跑」。
3. **凍結檔零改動**：`docs/03_b2_contract.md`（`01d2fb03…`）、`scripts/04`（`830dbf75…`）自 Contract v1 凍結後未改一個 byte；`scripts/05` 之改動全部走 R1→R11 重凍記錄（`data/04_b2_freeze_r{2,5,9,10,11}.json` + `logs/04_gate_b2impl_r*.out`）。
4. **最後一次確認**：`frozen_at = 2026-09-29T21:01:03+08:00`，impl `be946911087…`（= `scripts/05` 現行 sha256，逐 byte 核對 MATCH = True），GATE = OPEN。

### 12.1 產物雜湊（2026-09-29 20:37–21:01，防覆蓋核對）

- `logs/05_b2_correlation.out` = `9d693c9c5a174a7acf65c62232d98f83e3dcb537e2e02a264a913798a18b69e4`
- `logs/05_b2_correlation_reveal.out` = `34556c6a14a9668190a99e74f4cfe256f15f96d2e3cff094f2a5e67cd0c94311`
- `logs/06_b2_gpu_verify.out` = `b8bb6d7686195e958b2a5010cb3cb0006467a6d4307878f764a0ab48e30b0f5a`
- `logs/04_gate_b2impl_final.out` = `dd21451d24a38476a742e5de45755cb8e747a4901762d4e8678b04a4d252da75`
- `data/05_b2_correlation.json` = `ed3cc92049e0514fd72e337292937fa534bfae06ef4b9620e7b9407225378f86`
- `data/05_b2_results.json` = `e92f6ab9f5b7030c1a02ff7259371c6c37a2bcf618481d27dbe5b451c86e9b0c`
- `data/06_b2_gpu_verify.json` = `84b376c225321bfa990050f56e700b82329dd63007a491dc67e66ca1161d1663`
- `data/04_b2_freeze.json` = `4b2e070d4388554cda19d15ff479e48335d90f3841073a811b997e61320f1f46`
- `scripts/05_b2_correlation.py` = `be946911c087862d7bd02b460235b0b47fe1ff4ed85d2a855b6855f717e49235`
- `scripts/06_b2_gpu_verify.py` = `add870a68eeddf841016cca8b9b2b2964ac64317464fb55f90672102b32b0d37`

★ 實錄（21:0x）：一個早前 session 遺留嘅**背景行程**被 SIGTERM 收掉，而其命令同樣重定向到 `logs/05_b2_correlation.out`（同一路徑）。事後即時核對：該 log 仍然 86 行、mtime 20:36:05、`RESULT: 18/18 PASS mode = frozen-run`、sha256 與上表一致 ⟹ **未被覆蓋**。教訓：**同一 log 路徑唔可以有兩個寫入者**；收尾時先確認無舊行程，並把產物 sha256 寫入文檔，令任何日後覆蓋可被一秒偵測。

★ 機制（補充，21:1x 第二次事故）：`>` 與 `tee` **開檔即 truncate**；舊行程嘅 fd 會跨過我嘅重寫繼續存在，**只有當佢之後再寫入**才會污染。今次兩個舊行程皆在計算中掛住（Fraction 效能），死前零寫入 ⟹ 檔案逐 byte 不變（sha256 重驗 = 表內值）。**操作規則**：凍結輪用**唯一 log 名**（`logs/05_..._R11.out` 式）或每次引用前即時驗 sha256；收尾 `pgrep` 確認零寫入者。

### 12.2 不可變凍結副本（2026-09-29 21:2x，根治「共用 log 路徑被舊行程覆蓋」）

**背景**：本輪收尾期間先後有 **3 個**早前 session 遺留嘅背景行程被 SIGKILL/SIGTERM 收掉，全部命令都重定向到 `logs/05_b2_correlation.out`（`>` 或 `tee`，開檔即 truncate）。三次即時驗 sha256 皆**逐 byte 不變**（該三行程卡在 Fraction 運算，死前零寫入），但共用路徑本身係設計缺陷。

**處置**：凍結產物一律**版本化副本**落 `logs/frozen/`、`data/frozen/`（含凍結 impl 本體）；canonical 路徑若日後被覆蓋，可由此逐 byte 還原。

| 副本 | sha256 |
|:---|:---|
| `logs/frozen/05_b2_correlation_R11.out` | `9d693c9c5a174a7acf65c62232d98f83e3dcb537e2e02a264a913798a18b69e4` |
| `logs/frozen/05_b2_correlation_reveal_R11.out` | `34556c6a14a9668190a99e74f4cfe256f15f96d2e3cff094f2a5e67cd0c94311` |
| `logs/frozen/06_b2_gpu_verify_500.out` | `b8bb6d7686195e958b2a5010cb3cb0006467a6d4307878f764a0ab48e30b0f5a` |
| `logs/frozen/04_gate_final.out` | `dd21451d24a38476a742e5de45755cb8e747a4901762d4e8678b04a4d252da75` |
| `data/frozen/05_b2_correlation.json` | `ed3cc92049e0514fd72e337292937fa534bfae06ef4b9620e7b9407225378f86` |
| `data/frozen/05_b2_results.json` | `e92f6ab9f5b7030c1a02ff7259371c6c37a2bcf618481d27dbe5b451c86e9b0c` |
| `data/frozen/06_b2_gpu_verify.json` | `84b376c225321bfa990050f56e700b82329dd63007a491dc67e66ca1161d1663` |
| `data/frozen/04_b2_freeze_r11_final.json` | `4b2e070d4388554cda19d15ff479e48335d90f3841073a811b997e61320f1f46` |
| `data/frozen/05_b2_correlation_IMPL_be946911.py` | `be946911c087862d7bd02b460235b0b47fe1ff4ed85d2a855b6855f717e49235` |

**規則**：① 凍結輪用唯一 log 名（`*_R11.out` 式）② 引用前即時驗 sha256 ③ 收尾 `pgrep` 確認零寫入者 ④ 副本唔可以被任何腳本寫入（只讀）。

### 12.3 由凍結 JSON 獨立重算（2026-09-29 21:5x）

唔重跑腳本，只由 `data/frozen/05_b2_correlation.json`（`ed3cc92049e0514fd72e337292937fa534bfae06ef4b9620e7b9407225378f86`）嘅 `N2I`（62×62 分子）+ `cos2`（3844 個 `p,q√5`）用 `fractions.Fraction` 重算，**標題數字逐個命中**：

- `C²` 值集 = `{0, 1/9, 4/9, 1}`，重數 `{960, 1660, 960, 264}`（總 3844）⟹ 與 `C ∈ {0, ±1/3, ±2/3, ±1}`（7 值）一致。
- **精確 `C² == cos²θ` 命中 634**（DEV 24 + BLIND 610、`max |C² − cos²| = 8/9`（在 `(E00,E29)`，`C²=1/9` vs `cos²=1`））—— 與 `docs/04` §0/§11 完全一致。
- **更硬嘅事實（新增）**：3844 對中有 **1920 對** `cos²θ` 係**無理數**（`q ≠ 0`）⟹ `C²`（分母 120²，有理）**在算術上不可能等於**佢哋（無理性論證，唔係統計問題）⟹ 可吻合上限 1924；其餘 1290 對全部不吻合。
- 平凡家族精確化：`cos²=1` 對 124 個、`cos²=0` 對 600 個（合共 724 個候選），其中 **634** 吻合 ⟹ 餘 90 個候選係 `|C| < 1` 或 `|C| > 0` 之非平凡偏離。
- `results.blind_sha256` = `1b0420a6…ba96` **逐字等於** `data/05_b2_blind_values.json` 現行 sha256 ⟹ 凍結輪內容之**密碼學鎖**；另 `dev 144 + blind 3700 = 3844`、無重複、`DEV = V×V` ✓。

**第 4 次事故（同批滯後通知）**：`proc_694c4fcea03c` 報 exit=0（同一命令、同一 log 路徑）。即時核對：log 仍 `9d693c9c…`、4 個 data JSON 全部符號一致、mtime 仍 `20:36:05` ⟹ 該行程之寫入**發生在我 R11 輪之前**，通知只係**滯後派送**；零損傷。其後 `logs/frozen/`、`data/frozen/` 版本化副本已就位（§12.2），未來任何覆蓋可逐 byte 還原。

| 補充副本 | sha256 |
|:---|:---|
| `data/frozen/05_b2_dev_values.json` | `a76bd7438f1e26c7e12df22d93ae2c7a127c80b34fd38fad99e04115508446cf` |
| `data/frozen/05_b2_blind_values.json` | `1b0420a620eacd7b130a1a6da0a181124d5ad0c17f1de17c9626413538a6ba96` |

**第 5 次滯後通知（同批末件，21:5x）**：`proc_6336699e0faa`（R6 鏈：frozen + reveal 兩個 log）報 exit=0。本次改為**由 `docs/04` 直接讀返記錄雜湊再比對**（唔再靠人手轉錄）：canonical 12 件與文檔記錄**全部 MATCH**、mtime 全部維持 R11 輪時間軸（20:36:05 / 20:37:49 / 20:59:47 / 21:00:19 / 21:01:03）⟹ 零損傷、寫入全在我 R11 輪之前。★ 教訓：**核對要用機器讀返嘅記錄值**（人手打雜湊會引入假陽性 DIFF，本次即出現一次）；另補 `data/frozen/06_b2_gpu_verify_IMPL_add870a6.py`（`add870a68eeddf841016cca8a9b2b2964ac64317464fb55f90672102b32b0d37`）令**兩個核對腳本本體**同樣有不可變副本。

### 12.4 完整性工具（`scripts/07_artifact_integrity.py` + `data/frozen/MANIFEST.json`）

**第 6 次滯後通知**（`proc_dd96dc0e4763` = R9 鏈，一次過寫 05 frozen + reveal + **06 GPU** 三個 log；報 `all_exit=0`）：即時用新工具核對 → **12/12 OK、drift=0、live writers=NONE** ⟹ 再一次證實係滯後派送、寫入全在 R11 輪之前。

**工具**（**唔屬於凍結合約**，從不寫入 `logs/`、`data/05_*`、`data/06_*`、`scripts/04_*`、`scripts/05_*`）：
```
/usr/bin/python3 scripts/07_artifact_integrity.py            # 只核對；有 drift 即 exit 1
/usr/bin/python3 scripts/07_artifact_integrity.py --restore  # 核對 + 由不可變副本逐 byte 還原（先驗副本本身）
```
**manifest**（`data/frozen/MANIFEST.json`，12 件、機器可讀）：每件記 canonical sha256 + 對應不可變副本 + 來源輪次；覆蓋 4 個 log、6 個 data JSON（含 freeze / GPU / dev / blind）、**兩個腳本本體**（`scripts/05` 凍結 impl、`scripts/06` 核對腳本）。
**為何要有**：本輪收尾期間連續 6 個早前 session 遺留嘅背景行程被逐個收掉，全部命令都重定向到同一批 log 路徑（`>` 或 `tee`，開檔即 truncate）⟹ 每次都必須核對；有了 manifest + 工具，同類事故由「逐個手查」變成**一行指令**，而且 canonical 被覆蓋時可**逐 byte 還原**（副本先驗 hash，拒絕用壞副本還原）。

**滯後通知累計 10 次（`proc_*`：R5/R6/R9/R10 鏈、原始 R11 鏈、最初 06 GPU 失敗輪 ×2、3 個單發行程），每次即時核對皆 `drift=0`、`live writers=NONE`；只有 §12.2 之第 1–4 次係「未知輪次」，第 5–9 次全部證實為滯後派送（寫入皆早於 R11 輪）。**

**第 8 次滯後通知（原始 R11 鏈，`chain_exit=0`）**：`proc_daac690ee0f5` 自己嘅 grep 輸出**獨立佐證**本輪引述之數字——
```
logs/04_gate_b2impl_r11.out: RESULT: 14/14 PASS  (0 FAIL, 0 claims excluded)   GATE = OPEN
logs/05_b2_correlation.out:  RESULT: 18/18 PASS  (0 FAIL, 4 claims excluded)   mode = frozen-run
logs/05_b2_correlation_reveal.out: RESULT: 19/19 PASS (0 FAIL, 5 claims excluded) mode = REVEAL
logs/06_b2_gpu_verify.out:   RESULT: 2/4 PASS  (2 FAIL)   GPU = NVIDIA GeForce GTX 1060 3GB
```
首三行與 `docs/04` 完全一致；**第 4 行嘅 2/4 係修好兩個 GPU 側 bug 之前嘅狀態**（§7：旋轉矩陣手寫式無平方項、四 setting 相異 mask 漏兩對約束），修正後最終輪 = **4/4 PASS**（現行 canonical log `b8bb6d76…`，mtime 21:00:19）。即時核對：12/12 OK、drift=0、restored=0、live writers=NONE。
⟹ 滯後通知除咗係風險（同路徑寫入者），亦係**意外的獨立佐證**：每條鏈自己嘅 grep 記錄了當時嘅 RESULT 行，可與凍結記錄逐行對比。
