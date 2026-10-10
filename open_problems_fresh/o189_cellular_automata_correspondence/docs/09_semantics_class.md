# O189 docs/09 — R-A：O222 求值語義層之計算類判定（R4，最後殘餘）

> **2026-10-10 | R4 | 產物: `scripts/09_semantics_class.py`（10/10 PASS）、`data/09_semantics_class.json`、`logs/09_semantics_class.out`**

---

## 一、結論（先寫死）

🟢 **R-A 已回答——O222 求值語義層之計算類：依條款（限界）= 有限狀態機；TC 需要一條 O222 冇寫嘅額外條款（遞歸 thunk 圖，D7）。** 三層聲稱全部成立（scripts/09，10/10 PASS）：

1. **限制版（O222 as stated，資源有界）＝有限態機，唔係 Turing-complete**：
   - D1 語義（force 單值、memo 純函數、換 ctx = 新 thunk）＋ A6 塌縮固定點迭代 **200 步上限** ＋ B5 預算語言（memo ≤ 3844 對）＋ gen 係有限晶格算子集 ⟹ 轉移系統有限；
   - **E4 基數論證**：可達配置 ≤ (|U|+1)^8·CAP（本輪 = 1.63e11，實測 |reach|=1），有界全函數 ⟹ 對角線論證 ⟹ 不是萬能機；
2. **TC 門檻喺一條 O222 冇寫嘅條款**：O222 冇遞歸 thunk 圖（無循環）。加一條 D7（thunk 生成器可自引用 = 惰性定點）就升到 μ-遞歸 ⟹ TC。**E3 構造盲測**：factorial(10)、fib(20)、gcd(21,14)、ackermann(3,3)=61，全部由 memoized thunk 強制引擎計出（自引用 rec 係引擎內建，非外部 Python 遞歸）；
3. **stated cap 係 TC-blocker（E2）**：countdown 1000→0 要 1000 步，喺 200 步上限下被禁（x=800 卡死），上限 1000 就過——量化咗「資源界限」就係令佢唔通用嘅原因（對接 O228 k_min ≥ ⌈log₂m⌉ 資源幾何）。

**R-A 因此正式閉合**：O189 全部殘餘（R-A/R-B/R-C/R-D + 兩條 R2 殘餘）已答完。O189 保持 `partial`（唔聲稱「IDCM 世界 = 通用電腦」；物理層三層分離唔踰越）。

## 二、模型提取（每條款→機械規則，零新增假設）

| O222 條款 | 機械規則 |
|:---|:---|
| D1-a 三元組 T=(gen,σ,ctx) | thunk 不可變；key = (gen,σ,ctx) |
| D1-a force 單值 | memo 查找／寫入確定；每 key 一值 |
| D1-b memo 命中 ≡ 冷算 | memo 命中唔再寫入（本輪 E1 tick 計數反映） |
| D1-c 換 ctx = 另一 thunk | key 含 ctx；舊條目不動 |
| D1-e 塌縮 = 限步精確收斂 | **固定點迭代 + 200 步上限（A6）** |
| B5 預算語言 | memo 條目上限（3844 對），本輪小參數版 CAP/基數驗證 |
| gen 有限晶格算子集 | 44 模式＋2I 旋轉等 ⇒ finite |

**D7（冇寫，係 R-A 嘅發現）**：thunk 生成器可以自引用（遞歸 thunk 圖／循環）——O222 任何條款都冇畀，所以限界版 static 上係 acyclic。

## 三、結果表（scripts/09，10/10 PASS）

| 檢查 | 值 | 狀態 |
|:---|:---|:---:|
| E1a 可達配置有限 | |reach| = 1 < 10⁶ | 🟢 |
| E1b 全部有界運行喺 200 步內終止 | max tick = 12 | 🟢 |
| E2a countdown 1000→0 被 200 步上限禁 | x=800 卡死 | 🟢 |
| E2b 同計算喺 1000 步上限通過 | x=0, steps=1000 | 🟢 |
| E3a factorial(10) via D7 | 3628800 | 🟢 |
| E3b fib(20) via D7 | 6765 | 🟢 |
| E3c gcd(21,14) via D7 | 7 | 🟢 |
| E3d ackermann(3,3) via D7 | **61**（μ-遞歸 ⟹ TC） | 🟢 |
| E4a 基數上界 | 1.63e11，實測 1 | 🟢 |
| E4b 冇 D7 機器全總（4000 orders 全終止） | 有界全 ⟹ 非萬能 | 🟢 |

## 四、判讀

1. **同 R1 C3 對接**：「O222 已證通用計算」唔止「冇證明」——喺條款下係**錯**嘅（限界機器有界⟹唔通用）；O222 真正嘅身份係**資源界限確定性語義**（同 audit 一致）。而家連「TC 要補乜」都列明：**一條 D7 遞歸 thunk 條款**。
2. **同 O228 對接**：資源幾何 k_min ≥ ⌈log₂m⌉ 同呢度「cap = TC-blocker」互補——O228 講**點解有限資源夠唔到**，本輪講**用幾多步先算得完**（countdown 例子量化）。
3. **三層分離（唔踰越）**：L1 晶格 = class II⁺（R1 C3）唔變；L2 語義層 = 限界 FS／＋D7 先 TC；L3 物理模擬宣稱完全唔做。**「IDCM 世界係通用電腦」呢類宣稱依然係🔴禁區。**
4. 誠實邊界：E3 嘅 D7 係「假如條款」——唔係宣稱 O222 而家有；E4 基數上界用 leaf-8 memo 配置（實際 memo 更細，所以實測 1）。

## 五、殘餘狀態（R4 後）

- ✅ R-A（理論整體計算類）——**閉合**
- ✅ R-B（sign_rank 約束力）——已 handoff O228（治管裁決）
- ✅ R-C／R-D／殘餘①②——R2/R3 閉合
- **O189 所有歸屬殘餘已答完**。O189 狀態保持 `partial`（結構對應研究完成；物理宣稱三層分離唔踰越）。

## 六、檔案

- `scripts/09_semantics_class.py`（10/10）；`data/09_semantics_class.json`；`logs/09_semantics_class.out`
- 引用：O222 docs/02（D1-a..f、A1/A4/A6/A8）、O222 final_result（B5 預算）、O228（k_min ≥ ⌈log₂m⌉）、R1 docs/03（三層分離）、R1 docs/05-08（mod-q／2adic／248／ε-CHL）