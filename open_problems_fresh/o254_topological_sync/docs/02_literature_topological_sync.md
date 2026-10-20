# O254 docs/02 — 文獻審：topological phononics + 「topological synchronization」語義

> 2026-10-20 · 文獻搜尋（arXiv / APS / Nature Comms / Science）+ 語義重建
> 目的：Q1「聲子拓撲等價可操作 vs 純類比」+ Q3「全局共享 vs 預耦合」嘅外部物理基礎

## 結論先行

**「拓撲同步」喺文獻係真概念，但語義同 P14/IDCM 完全唔同：**

```text
文獻「topological synchronization」= 同一塊耦合晶格內, 位於拓撲邊界嘅
    oscillator 透過 bulk 拓撲態同步 (PRR 5, 023021; 2025 non-Hermitian 電路)
P14 candidates/IDCM「拓撲同步」= 兩塊物理分離晶體, 無 EM/聲學介質, 共享陳數 → 非局域

兩者嘅關鍵差別 = 有冇「同一個 Hamiltonian + 同一個 BZ」
文獻: 有 → 同步經 bulk 傳播, 受 c 限制, 唔係非局域
P14:  冇 → 兩塊晶體係兩個獨立 Hamiltonian, 各自 BZ, 各自陳數
```

**二號結論：聲子 Berry 曲率 / 陳數物理係真（2015+ 已實驗），所以「晶體拓撲 = 可操作物理」成立——但呢個只係普通凝聚態拓撲，唔係「宇宙格共享」；宇宙格側嘅「拓撲同步」冇任何物理基礎。**

## 一、topological phononics — 已實驗（2015+）

| 年份 | 工作 | 系統 | 關鍵量 |
|:----:|:-----|:-----|:-------|
| 2015 | Süsstrunk & Huber, Science 349:47 (arXiv:1503.06808) | 機械振子陣列 QSHE analogue | phononic helical edge states, 拓撲保護（缺陷免疫）|
| 2015 | Wang, Lu & Bertoldi, PRL 115:104302 | gyroscopic phononic crystals | 一維 chiral edge waves, bulk C=1,2 免疫背散射 |
| 2018 | Ge et al., PRApplied 10:014017 (arXiv:1803.00828) | acoustic Weyl phononic crystal | 3D Weyl points + Fermi arcs, 一步障礙零反射 |
| 2018 | Zhang et al., Comms Physics 1:97 | 綜述 | "Topological sound": spin/valley 自由度, 缺陷免疫 |
| 2018 | Zhang et al., NSR 5:314 (arXiv:1707.07142) | Perspective | phonon Berry phase/曲率定義 + honeycomb platform |
| 2023 | Xu et al., PRApplied 19:034062 | phononic crystal | topological valley Hall edge states（材料差異實現）|
| 2025 | arXiv:2502.13814 | BaMnSb₂ | phonon Berry curvature ∝ electronic valley Chern number（繼承機制）|

**一致性**：所有實驗嘅拓撲邊界態都喺**單一連續晶格**內，靠 bulk 能隙 + 邊界條件實現；聲子傳播仍受群速度限制（kHz–MHz 級），冇任何「超越物質分離嘅即時響應」。聲子拓撲物理真實存在 = Q1 嘅「晶體側可操作」成立，但係普通凝聚態，唔係 IDCM 特定預言（聲子色散 sin² 本身係所有最近鄰鏈嘅通用形式——見 docs/29 承認「比率 1.0000」只係形狀同構）。

## 二、「topological synchronization」— 文獻真實語義

| 年份 | 工作 | 內容 | 有冇「分離晶體無介質」? |
|:----:|:-----|:-----|:-----------------------|
| 2023 | Wächtler & Platero, PRR 5:023021 | quantum vdP oscillators 喺 SSH chain / Kagome lattice 上, 邊界 oscillator 經拓撲態同步 | ❌ 同一 lattice, 邊界↔bulk 耦合 |
| 2025 | Li et al., Sci. Adv. 11:eady5649 | 單一 trapped-ion 量子 vdP 振子（實驗首例） | ❌ 單一離子, 唔涉及兩體同步 |
| 2025 | Liu et al., arXiv:2509.18423 | 兩個 trapped-ion 量子 vdP 振子 sync（量子同步兩體首例） | ❌ 同一離子阱, engineered collective dissipation 耦合 |
| 2025 | Di et al., Comms Physics (s42005-025-01999-1) | non-Hermitian topological synchronization — 非線性 topolectrical circuit 實驗 | ❌ 同一電路網絡 |
| 2023 | (PMC8847423) | 混沌系統「拓撲同步」= multifractal structure 收斂 | ❌ 耦合的兩個 oscillator, zipper effect |

**判讀**：即使用最廣義文獻定義，「topological synchronization」都要求**同一 Hamiltonian / 共享耦合通道**。兩個完全分離、各自獨立 Hamiltonian 嘅晶體共享陳數——喺文獻中零先例、零機制、零實驗。拓撲不變量（陳數）係**單一帶結構**嘅性質；兩塊晶體 = 兩個帶結構 = 兩個獨立陳數。要共享，必要條件係耦合（隧道/機械/聲學/EM——都係局域相互作用）。

**⟹ Q3 外部答案：全局共享唔存在免費版本；必須預先耦合。** 同 P14 docs/21「地球兩部機喺同一晶格胞 → IDCM 機制根本不適用地面通信」一致——1m 分離喺宇宙 hop 6.7 Mpc 尺度 = 4.84e-24 hops，兩塊晶體**喺宇宙晶格意義上根本未分離**，測得到嘅只係局部晶體自身響應。

## 三、與 IDCM 結構對照

- **IDCM 已確立且與文獻兼容**：γ_n = 4sin²(πn/88) ↔ 最近鄰鏈色散（文獻：任何 1D 單原子鏈都係 sin² 形狀；P14 已承認「比率 1.0000」係形狀同構）。
- **IDCM 對應結構疑點**：陳數係 2D BZ 積分（C = (1/2π)∮Ω d²k），而 K_Chain / A5 係 1D / 圖——「共享陳數」引用嘅係 2D 拓撲不變量概念，落到 1D 圖冇直接對應（P14 scripts/57 亦只做咗「陳數整數化係拓撲約束」嘅定性聲明 — docs/31 未獨立重算）。⚠️ 呢個係結構層缺口：Chern number 定義域 vs IDCM 1D/圖結構。
- **O7 阻挫邊重聯（UHECR anchor）**：呢個係 IDCM 自有但無文獻對應嘅拓撲事件模型（graph Ising 翻轉）；docs/01 E4 顯示其能量 ~16 J ≫ mJ——獨立於文獻嘅內部束縛成立。

## 四、Q1/Q3 初步裁決（結合 docs/01 能量圍堵）

```text
Q1「拓撲等價可操作 vs 純類比」:
  晶體側: 可操作 ✅ (文獻 2015+ 已證聲子拓撲物理; 但係普通凝聚態, 唔係宇宙格)
  宇宙格側: 純類比 🔴 (冇任何機制: 冇耦合算子, 冇「兩塊分離晶體共享陳數」先例,
            陳數定義域 (2D BZ) vs IDCM (1D/圖) 未對接)
  ⟹ Q1 判決傾向: 晶體聲子拓撲 = 真物理 (但非 IDCM 專屬); IDCM 版「宇宙格共享」= 無物理基礎

Q3「全局共享 vs 預耦合」:
  文獻: 必須預耦合 (同一 Hamiltonian 先有共享拓撲)
  IDCM: docs/21 已裁定地面晶體喺同一胞 → 唔係「分離系統」
          ⟹ 「兩塊分離晶體」喺宇宙格尺度 = 同一對象嘅兩個局部 → 冇非局域同步可言

Q2 已由 docs/01 圍堵: mJ 端否證 (能量差 ≥4 個數量級), 10⁴⁰ J = 佔位數
```

## 五、下一步候選
1. **正式否證文件**（若 Q1/Q3 維持 🔴）→ 回報 P14 docs/30 降級（SESSION_START §五 已預告）
2. Docs/01 E7b 捕獲 scripts/56 算術錯 → register handoff 交回 P14
3. 剩餘 🔴：讀取機制（晶體 B 點感應拓撲態改變）、人造調制器——兩者都建基於 Q1/Q3 有物理基礎，現傾向於「否證文件」一併收口

## 附：文獻檢索記錄（不要當圖書館引用）
- arXiv:1707.07142 (phonon Berry phase & topology Perspective)
- arXiv:1503.06808 → Science 349:47 (2015)
- PRL 115, 104302 (2015); PRApplied 10, 014017 (2018); Comms Physics 1:97 (2018)
- PRR 5, 023021 (2023); Sci. Adv. 11:eady5649 (Li 2025 單 vdP); arXiv:2509.18423 (Liu 2025 兩 vdP); Comms Physics 2025 (non-Hermitian)
- 檢索工具經 web_search（keyless tier），引用前應以官方 DOI 頁複核；本文件只攞結構性結論（都係「同一耦合系統內」），唔依賴特定數字