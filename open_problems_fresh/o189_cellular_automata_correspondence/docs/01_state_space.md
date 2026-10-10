# O189 docs/01 — 狀態空間比較（C1）：IDCM 88-site 鏈 vs 細胞自動機

> **2026-10-10 | R1 | 產物: `scripts/01_state_space.py`（13/13 PASS）、`data/01_state_space.json`、`logs/01_state_space.out`**

---

## 一、結論（先寫死）

🟢 **C1 已回答**：IDCM 88-site 鏈同 ECA 嘅狀態空間**同格但唔同勢**：
- 格點數一致（88 cell / 88 site）；
- ECA 狀態空間 = 離散 `2^88 = 309,485,009,821,345,068,724,781,056`（精確）；
- IDCM = 連續複振幅 `ℂ^88`（site 基底 176 實自由度；44 個 Fourier 譜模式 ⟹ 88 實自由度），不可數；
- **Coarse-grain 門檻**：每 site 幅度量化到 q 級 ⟹ `88·log₂q` bits；**q=2 剛好重製 CA 容量**（88 bits = 2^88 configs）；q≥3 即超過；
- **雙鏈結構因子**：mode 基底量化只畀 44 bits（= 88-site 嘅一半），IDCM 譜空間比 site 空間稀疏 2 倍——這是 N_d=44 dual-chain 嘅直接印記（O95/O211 Σγ=90 系）。

誠實缺口：coarse-grain 嘅**動力學兼容性**（quantize 之後演化仲係咪「同一系統」）未喺本輪證明——只有狀態空間容量對齊，映射本身（C2）另見 docs/02 嘅盲測負結果。

## 二、狀態空間表

| 量 | 值 | 出處/計算 |
|:---|:---|:---|
| CA configs（88 cells, 2-state） | 2^88 = 3.09×10^26（27 位數） | scripts/01 C1.1 |
| IDCM site 基底實 DOF | 176 = 2×88 | scripts/01 C1.2 |
| IDCM 譜模式實 DOF | 88 = 2×44（44 個複 Fourier 模） | scripts/01 C1.2 |
| 譜權重 γ_n = 4sin²(πn/88), n=1..44 | Σ = 90 精確（O221 B1 恆等式） | scripts/01 C1.3；O221 docs/05 |
| 譜測度 Shannon 熵 H(p) | **5.03677 bits**（均勻上限 log₂44 = 5.45943） | scripts/01 C1.5 |
| 有效模式數 2^H | **32.83**（< 44 ⟹ 測度高度集中喺 band edge） | scripts/01 §B |
| p_max / 均勻 | **1.9556**（p_max = 0.04444 = 2/45） | scripts/01 C1.6 |
| 宇宙學 tick τ = 1/ω_ring | **13.47006 Gyr**（4.25×10^17 s） | scripts/01 C1.10（O121） |

**Coarse-grain 階梯**（每 site/每 mode 量化 q 級 → bits）：

| q | site-quant bits | mode-quant bits |
|:--:|:--:|:--:|
| 2 | **88** = CA 容量 🟢 | 44 |
| 3 | 139.5 | 69.7 |
| 4 | 176 | 88 |
| 16 | 352 | 176 |

## 三、判讀

1. **「CA = IDCM 嘅 1-bit 粗粒化」係數學恆等（容量層）** —— 但要小心：呢個只有「數得掂」層面成立；CA 嘅 88 bits 係**任意思維組合**（2^88 全空間），IDCM 嘅 q=2 投射只係 `ℂ^88 → {0,1}^88` 嘅**一個超平面扇**，兩者嘅**可達集**唔同（見 docs/02 盲測：投射後軌跡唔似任何 ECA）。
2. **譜測度熵 5.04 bits** ⟹ IDCM 模式空間嘅「有效維度」約 33 個模式。band-edge 集中（γ_44 = 4 最大）係 arcsine 譜（O221 B8 KS = 1/N_modes）嘅即時後果——IDCM 唔係均勻「44 個等權盒子」，而係一個有結構嘅測度。
3. **時間尺度階層**：CA 一步 = 組合邏輯層（~ns）；IDCM tick ≈ 13.47 Gyr。兩者差 ~10^30 個數量級。IDCM 有**雙時間尺度**（連續流 + 宇宙學 tick），CA 得離散步——結構對應裡時間本身要 coarse-grain。

## 四、等價 / 模擬 / 類比（S3 判準）

- **等價**：🔴 否（可數 vs 不可數；除非固定 q 與精度，但動力學唔兼容，見 C2）
- **模擬**：🟢 平凡成立（任何一方可模擬另一方，圖靈完備對圖靈完備——但 O189 起手式已排除「模擬=對應」）
- **類比**：🟢 狀態空間同格（88/88）、CA = 1-bit 粗粒化容量恆等、雙鏈因子

## 五、四道硬測試對應

① 自由度：零新參數（只用 O221 譜 γ_n 與 τ） ✅
② MC null：本輪冇閉合宣稱要 MC（容量陳述係恆等式，N_search=1） ✅ 純代數
③ 可證偽：狀態空間比較本身可證偽（如 q=2 唔等 88 bits 即倒） ✅
④ 剛性：spectrum 改動會即時改 H(p) 同容量表（零 tolerance） ✅

## 六、檔案

- `scripts/01_state_space.py`：13/13 PASS，可重跑（`/usr/bin/python3`，numpy+mpmath）
- `data/01_state_space.json`：全數值
- 引用：O95（N_d=44）、O121（τ）、O221（譜恆等式、arcsine）、O222（γ_n/90 規範）