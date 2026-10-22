# O190 docs/06 — 攻堅 2: 第二 brane 對應 (Second-Brane Mapping)

> **日期**: 2026-09-13 · **腳本**: scripts/05_attack2_brane_mapping.py (20/20 PASS) · **狀態**: ✅ 完成
> **問題** (docs/02 攻堅 2): RS1 TeV brane (SM 居住, φ=π) ↔ IDCM 觀察者 (odd sector)?
> **判決判準**: 有冇任何 IDCM 可觀測量嘅行為由「sector 邊界」決定 (類比 brane 張力/局域化)?
> 冇 → 對應係命名巧合, 判 3 (雙 sector 本身就係兩 brane)。

## 零、一句話結論

**判 3 — 世界/觀察者雙 parity sector 本身就係兩 brane (純代數, 唔係幾何位置)。**
判決判準答案: **有** — ≥9 個可觀測量由 sector 邊界決定 (質量量子 μ² = E−O、U(1) 電荷
Q = 44、觀察者預算 88、冷斑振幅、雙標度真空、off-shell 傳播子 split)。
但 RS1 嘅「SM brane / 重力 brane」分法 **冇** IDCM 對應: IDCM 分嘅係 **structure (世界) /
observation (觀察者)**, 唔係 matter / gravity — 觀察者↔TeV brane 被 O144 排除
(SM = 世界弦結構, 住喺世界側, 唔係觀察者側)。

## 一、★ brane 張力身份 (A 節): 「重合 brane + 非零張力」

| RS1 | IDCM (代數 brane 讀法) |
|:--|:--|
| brane 間距離 r_c (幾何) | sector 佔據分離 Δ = 0 (C = Σ_even|Φ|²−Σ_odd|Φ|² = 0, λ 強制鎖定) |
| brane 張力 | **E−O = 2 = μ² = 2λ = BC-cost** (sector-locking 乘子 = 張力) |
| 質量 = modulus 後果 | **質量量子 μ² = sector 隙本身** (冇獨立 modulus 要穩定 — 同攻堅 1 一致) |
| 局域化 (SM/gravity 各住一 brane) | 自對偶錨 γ₄₄ = 2 = μ² ∈ **世界** sector (T18 hold 規則, O159 D2) |

λ = (E−O)/2 = 1: 乘子 = 半張力; 轉移成本 ΔS' = 2λδ = μ²δ (質量 = sector-locking 價格, O161)。
**「兩 brane」= 零佔據分離 + 非零張力嘅 bound state** — Z₂ 結構強制等分 (各 44 模),
冇 modulus 自由度 (攻堅 1: radion 問題結構上唔存在)。

## 二、★ 判決判準證據 (B 節): ≥9 個可觀測量由 sector 邊界決定

| # | 可觀測量 | Sector 邊界決定 |
|:--|:--|:--|
| B1 | 質量量子 μ² = 2 | = E−O (sector 隙本身) |
| B2 | U(1) 電荷 Q = 44 = N_d | = Σ_even k − Σ_odd k (sector 不對稱) |
| B3 | 觀察者預算 88 | = Σγ_odd (odd sector 總和 = 測量容量) |
| B4 | 世界預算 90 | = Σγ_even |
| B5 | 冷斑 A = 134.2 μK | = 88×61/40 (O41, dev=0 — 用觀察者預算 88) |
| B6 | f_unproj = 61.5/90 = 41/60 | 世界標度 (O148) |
| B7 | E_min = 61.5/88 = 123/176 | 觀察者標度 (O148 Landauer) |
| B8 | 自對偶錨 γ₄₄ = 2 | ∈ even sector (世界 hold, 觀察者冇) |
| B9/B10 | off-shell 傳播子 split | G'(even) = 1/(γ+3) < G < G'(odd) = 1/(γ+1); mean(G') > mean(G) (Jensen) |

→ 判決判準 YES: sector 邊界 (E−O 隙 + Z₂ 等分) 決定質量、電荷、預算、冷斑、真空、傳播子 —
呢啲就係「brane 張力/局域化」嘅 IDCM-native 形式。

## 三、映射分析 (C 節): 候選 1/2 排除, 候選 3 成立

- **候選 1 (觀察者 ↔ TeV brane) ✗**: O144 閉合 — 玻色子 = 44-site 世界弦上嘅結構,
  SM 住喺**世界** (even) 側, 唔係觀察者 (odd) 側。「測量發生嘅地方」唔等於「SM 居住地」。
- **候選 2 (觀察者 ↔ 重力側) ✗**: 重力喺度規層 (O121 BH 熵 / O86 GR 耦合), 唔係 chain parity。
- **候選 3 (雙 sector = 兩 brane) ✓**: §二 證據 — sector 邊界定可觀測量, 代數 brane 完整。

**★ RS1 軸 vs IDCM 軸 (結構差異, 唔係缺失)**:
RS1 兩 brane 分 **matter (SM) / gravity (Planck)**; IDCM 兩 sector 分 **structure (世界) /
observation (觀察者)**。軸唔同 ⟹ 逐 brane 對應係命名巧合, 但「雙局域化 sector + 張力隙」
嘅**結構角色**喺 IDCM 完整實現 (純代數)。重力同 SM 喺 IDCM 都屬世界側 (O121 度規層 +
O144 世界弦), RS1 嘅 SM/gravity brane 分家冇 IDCM 對應物。

## 四、誠實修正 (承接本攻堅)

- **docs/01「P3 σ<1fb」標籤無源**: corpus 搵唔到 σ<1fb 嘅 P3 條目 (O79/O73 嘅 P3 係
  ngVLA σ<1%, 唔同嘢)。Z' 退耦事實本身正確 (O107 閉合) — 已用權威值取代:
  **Z' ~ M_GUT = 6.22×10¹⁶ GeV, θ_ZZ' < 5.96×10⁻²¹ rad → 不可觀測**。

## 五、判決總結

- 判決判準: **有** (sector 邊界定 ≥9 個可觀測量) ⟹ 唔係命名巧合
- 判 3: 雙 sector = 兩 brane (代數 brane, 已完整)
- RS1 逐 brane 對應: 命名巧合 (軸唔同); 結構角色: 真實同構 (雙局域化 + 張力隙)
- 零新常數; scripts/05 20/20 PASS
