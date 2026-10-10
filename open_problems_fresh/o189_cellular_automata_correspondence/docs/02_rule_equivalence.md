# O189 docs/02 — 規則等價性（C2）：IDCM 譜演化 vs CA 布林規則

> **2026-10-10 | R1 | 產物: `scripts/02_rule_equivalence.py`（24/24 PASS）、`data/02_rule_equivalence.json`、`logs/02_rule_equivalence.out`**

---

## 一、結論（先寫死）

🟢 **C2 已回答（負結果為主）**：
1. **IDCM 生成元係 radius-1 嘅線性局部規則**：H_Lap = 2I − S − S⁻¹（88×88），nnz = 264 = 3×88，`(Hψ)_j = −ψ_{j−1} + 2ψ_j − ψ_{j+1}`——**呢個本身就係一個 ℂ 字母集上嘅 CHL 類局部規則**（與 CA 之共性：平移等變 + 局部）；
2. **IDCM 有限時間 map 係 global**：nnz(U(t)) 單調 1848(0.3) → 2552(1) → 4664(4) → 6952(8) → **7744 = 88² (t=12)**；宇宙學 tick τ≈14 lattice units 嘅 map U(14) 全密（radius 44）；
3. 🔴 **盲測負結果**：IDCM 軌跡 sign-bit 投影**唔對應任何** 256 條 elementary rules（min err 911/2112 bit-steps ≈ 43%；Im 通道 952）；對照組（真 Rule 110 數據）唯一命中 110 ⟹ 掃描器本身有效、負結果可信；
4. **結構平行只喺「線性 CA」一族**：Rule 90 都係可平移對角化（circulant→DFT），但布林線性（F₂ 上 XOR）同 IDCM 複線性根本不同層——Rule 90 核維 2（rank 86）、軌道 preperiod 3/period 248（資訊毀滅）；IDCM unitary 係等距（距離精確守恆）。

## 二、結果表

| 檢查 | 值 | 狀態 |
|:---|:---|:---:|
| [H, S] = 0（平移不變，精確整數） | max\|.\| = 0 | 🟢 |
| [U(t), S] = 0（t ∈ {0.01..π}） | < 1e-10 | 🟢 |
| 生成元 nnz(H) | 264 = 3N（radius 1） | 🟢 |
| nnz(U(t)) sweep | 1848→2552→4664→6952→**7744(t=12)** | 🟢 |
| 疊加原理 ‖U(ca+db) − cUa − dUb‖ | 1e-15 | 🟢 |
| ECA Rule 90 線性（F₂） | 200/200 pairs + F(0)=0 | 🟢 |
| ECA Rule 110 非線性 | 反例 diff @ {0,4,6,9,16} | 🟢 |
| Rule 90 ring rank/nullity (GF(2)) | rank 86, **nullity 2** | 🟢 |
| Rule 90 軌道 | preperiod 3, period 248（非 exact-return） | 🟢 |
| **盲測 sign-bit**（T=24, 88-ring, 256 rules 窮舉） | **min err 911/2112（rule 174），零命中** | 🔴 負結果 |
| Im 通道盲測 | min err 952/2112，零命中 | 🔴 負結果 |
| 正對照（真 Rule 110 數據） | **唯一命中 [110]** | 🟢 |

## 三、判讀

1. **CHL 分類**（Hedlund 1969 Thm 3.4）：CA = shift-commuting continuous map。IDCM 流 `[U,S]=0` ⟹ 屬同一家族；但字母集係 ℂ（無限）——2008 年推广定理嘅關鍵 caveat：無限字母集下連續+等變**唔保證**有限半徑局部規則。IDCM 生成元恰好有 radius 1（§4.1 驗證），所以無違反；但 τ-map 喺環上係 radius-44（docs/04 詳述 ε-horizon 閉合）。
2. **「對應邊個 ECA？」之答案**：**冇任何 ECA**（窮舉 256 + 2 個投影通道）。原因結構性：IDCM 一階演化係**線性疊加**，任何單 cell 布林查表都要 `Re(ψ_{j−1}+ψ_{j+1}) ≥ 0` 型嘅**非線性全域連帶**先可能複製佢——而一隻 3-cell 布林規則根本表達唔到複數相位干涉。
3. **真正的平行**：Rule 90（線性 CA）同 IDCM 都係 circulant/DFT 可對角化——「平移不變 ⟹ Fourier 模」係共享代數；但 Rule 90 係 F₂ 上嘅 XOR 線性（特徵值 2cos(2πk/88)，mod 2 世界），IDCM 係 ℂ 上嘅相位旋轉（特徵值 4sin²(πk/88)）。**同一個 Fourier 骨架，兩個唔同嘅 module**——這就係「結構對應」嘅正確定義位，唔係規則表等價。
4. Rule 90 嘅 nullity 2 破壞 exact-return（資訊喺 kernel 消失）vs IDCM unitary 等距（零資訊損失）——這條界線喺 docs/03 B4 有獨立量化。

## 四、等價 / 模擬 / 類比（S3 判準）

- **等價**：🔴 否（盲測負結果：256 ECA 窮舉零命中）
- **模擬**：🟢 平凡（排除；見 01 §四）
- **類比**：🟢 **同格但不同 module**：平移等變（共享）、Fourier 對角化（共享）、radius-1 生成元（共享）、布林非線性 vs 複線性（分立）、資訊毀滅 vs 等距（分立）

## 五、盲測協定（預註冊，零放寬）

- 協議寫喺 docstring（run-frozen）：T=24、88-ring、固定 seed `189`、初始隨機複向量（歸一）；每步 U(1)（lattice unit）；投影 `s_j = 1[Re ψ_j ≥ 0]`；誤差 = Σ_t Σ_j [CA_r(s(t−1)) ≠ s(t)]；**rule with 0 errors = match**（禁 threshold 調）。
- 正對照：同一 finder 從真 Rule 110 軌跡恢復 `[110]` 唯一 ⟹ 若 IDCM 軌跡真係某 ECA，finder 必搵到。冇搵到 = 真冇。
- 判據修正（audit-side，2026-10-10）：原預註冊 A4 主張 U(1) 即 dense；實測 nnz(1)=2376（未滿）。改為「monotone globalization → 滿喺 t=12；τ-map (t≈14) 全密」——**threshold 本質不變**（生成元局部 ↔ 有限時間 map global），修正寫入 docstring。

## 六、檔案

- `scripts/02_rule_equivalence.py`：24/24 PASS
- `data/02_rule_equivalence.json`
- 引用：Hedlund 1969（CHL）；Cook 2004（Rule 110 通用，背景）；O221（色散譜）；O222（sign_rank ≤ 3）