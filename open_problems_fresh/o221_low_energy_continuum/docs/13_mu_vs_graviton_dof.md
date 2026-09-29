# O221 / docs/13 — 裁決：重力子自由度 = 2，**唔係 μ**

**問題**（用戶 2026-09-29）：「重力子自由度是什麼？μ嗎？」
**腳本**：`scripts/16_mu_vs_graviton_dof.py`（**13/13 PASS**，`data/16_mu_vs_graviton_dof.txt`）
**RAG 查證**（version-isolated）：v6 `quantum_gravity/AV2_GRAVITON_WFIELD`（「引力子 = W-field 的無質量自旋-2 模態 ✅ 微分同胚不變性保持」）、v7 `gravitational_phenomena/04-graviton_dispersion_derivation`（ω² = 4sin²(πn/2N_d)，由 chain Laplacian N_d = 44 推），v10 `o155/scripts/19_mu2_switch_operator.py`、`o160/docs/06_central_mode_theorem.md`、`o78/scripts/06_nyquist_identity.py`（μ² 一脈）。

## 一、答案：DoF = D(D−3)/2，在 D = B = 4 下 = 2

三種等價計數（全部係**結構計數**，唔係譜值）：

| 判據 | 內容 | D=4 |
|---|---|---|
| 小群／表示論 | 無質量自旋 2 ⟹ SO(D−2) 對稱無跡 2-張量維數 = SO(2) ⟹ helicity ±2 | **2** |
| 通式 | `DoF = D(D−3)/2`（有質量：D(D−1)/2 − 1）| **2** |
| ADM／二次型 | `DoF = rank(Q) − D = 6 − 4` | **2** |

scripts/15 Q5 已精確核實：rank(Q) = N − D（D=4：10 → 6）、規範不變 |ΔQ| = 4.44e-16、偏振 = rank − D。IDCM 側：**D = B = 4**（O124：γ_{44±j} = 4 + α⁻¹(0) = 137 ⟹ B² = 16）✓。

## 二、μ（μ²）係另一個扇區嘅量

μ² = γ_{44}(176-chain) = 4sin²(π/4) = **2**，即 K_chain 嘅**四分之一模**（O196/O160/O211/O215 一脈）。實測：**任何 M 嘅四分之一模都恰 = 2**（M = 88/176/352/704，max dev 4.44e-16）⟹ 呢個「2」係 **operator eigenvalue（值）**；graviton 嘅 2 係 **representation dimension（計數）**。

## 三、四個判別（全部已實測）

1. **D 依賴**：若 DoF = μ²，D=3 亦得 2——但真值 = **0**（scripts/15 Q5.3.3 已算）✗；D=5 真值 = 5，μ² 仍 2 ✗。（IDCM 內部：譜／鏈扇區按 docs/09 給 d_space = N_gen = **3** ⟹ 預言 0；畀 2 嘅係度量扇區的 B = 4。）
2. **質量依賴**：規範不變性破缺（D=4 有質量自旋 2）⟹ DoF = **5**，而 μ² 不動 ✗。
3. **連續 vs 離散**：譜值係**連續量**——隨機耦合擾動 ε = 1e-3 / 1e-2 / 1e-1 ⟹ 四分之一模鄰近特徵值漂移 **1.05e-4 / 2.82e-3 / 2.80e-2**（單調增長）；而 DoF 係**整數階梯**（步長 D−2：0,2,5,9），**唔可以漂移** ✗。
4. **多重度結構**：鏈嘅「2」係 **±n 宇稱對**（n=0 與 n=M/2 為 1，generic 為 2）——係反射簡併，唔係偏振指標；而 TT 計數在**任何動量**都係 2（四個動量實測全部 2）⟹ **同值唔同源** ✗。鏈模式每個只有 1 個分量（無偏振指標）⟹ 一維鏈天生供唔出 2 個 TT 偏振。

跨因子搬「2」（K_chain → K_tree）＝ 後驗湊算子，違反鐵律。

## 四、正確嘅結構對應（真連結）

重力子嘅 2 = metric perturbation 嘅 **TT（transverse-traceless）／shear 扇區**。docs/10 已證「**跡矩算子盲 shear、Regge 盲 trace，盲區互補**」⟹ 重力子恰恰住喺「**Regge 有反應、跡矩冇反應**」嘅扇區 ✓。再下一層：**2 個偏振係微分同胚不變性嘅後果**，而微觀格算子天生帶嘅係跡型（volume）結構 ⟹ 呢個直接連去 O221 收窄後嘅真缺口：「度量自身帶導數、微分同胚不變嘅動力學本體」。

## 五、版本裁決（RAG）

v6/v7 提供**色散形式**（ω² = 4sin² 家族，與 γ_n 同族 ✓）但**冇偏振數**；且 v7 係由一維 chain Laplacian 推 ⟹ 在 v10 語言下：**色散可共享、偏振必須來自度量／TT 扇區**。呢個係 O221 對 v6/v7 嘅一處結構修正（唔改舊版本記錄，只在此裁決）。

## 六、併入缺口 1 嘅判據（TT criterion）

Regge 端逐動量／約束分解抽 DoF = 2 時，四項判據：
1. `rank(Q) = N − D`（D=4 ⟹ 6）；
2. `DoF = rank − D = D(D−3)/2 = 2`（且 D=3 必須得 0 作對照）；
3. 規範方向逐點**零響應**（|ΔQ| ~ 1e-16 級）；
4. 必須見到 **TT 投影**（traceless **且** transverse）——**唔接受跡型（volume）響應冒充**偏振自由度。
