# O221 — 連續化層：低能極限過渡 (Continuum / Low-Energy Limit: GR & QM 還原)

## 狀態: 🟡 部分閉合（階段性 close-out 2026-09-29：增量已驗 667/667 + 獨立審計 102/102 + 文檔核對 99/99）
（R1 ✅ / R2 ✅ / R3 🟡 / R4 🟢 骨架 / R5 🟡 / U3 🟡 維數已達 3、瓶頸 = 動態度量結構 / U5 ✅ C_b 定理 + 🔴 窗反例 / U6 🟢 閘已行使 / 路線 ① ② ④ 已推 / 重力子 DoF = 2 已裁決 / 缺口 1 🟡 部分閉合（(c) ✅ 閉合、dim(TT) = 2 精確））

## 結論
IDCM 的低能過渡可由**單一極限程序 L**（細化流 ∘ 共動重標定，唯一控制變量 x = πn/M = ka/2）形式化；QM 骨架（正則結構、路徑積分測度）在細化下 ℓ-不變 ⟹ IDCM 係 QM 的有限維離散實現而非「導出 QM」；GR 側跡型譜作用量已被否證（a₂ = −Tr(L) 超局部、κ 非普適 24.7×），Regge 型導數泛函則可由 𝒯 **既有**虧角資料零新參數組裝（A₅ 凝聚多面體 Σδ = 4π = 2πχ），且 4D 連續端給出正確 graviton DoF = D(D−3)/2 = 2。

## 關鍵公式
- L：M → 4M、a → a/4、√J → 4√J，取 ℓ → ∞；x = πn/M = k a/2（唯一控制變量）
- ω_n = c k_n sin(x)/x，c = a√J = R_world·ω_ring；v_g = c cos x；a = 2πR_world/88、L = λ_sync = πa
- 存活判準 S1–S4：只依賴 x ／極限有限非零 + 冪次率 ／不引新量綱常數 ／物理量在 ℓ = 0 取值
- 跡矩（已否證為 EH）：a₂ = −Tr(L)（任意圖 Laplacian）、∫R√g = (2/9)ε²G2、c₁ ≡ 0、κ 非普適 24.7×
- 維數／DoF：K(D) = (D−1)(D−2)；**DoF_grav = D(D−3)/2**（D = 4 ⟹ 2、D = 3 ⟹ 0）；dim(TT) = (D−1)(D−2)/2 − 1
- Regge：S = Σ_h L_h δ_h/(16πG)，δ = 2π − Σθ；A₅ 凝聚多面體 δ = π/3、π/5、**π/15 = 12°**，Σδ = 4π = 2πχ；正 4-單形二面角 = arccos(1/4)
- 4D 連續端：rank(Q) = N − D = 6、kernel = 4（gauge h = k⊗ξ+ξ⊗k）、簽名 1 vs 5（單獨同號方向 = conformal 扇區）
- K_chain：γ_n = 4sin²(πn/M)、Σγ = 2M；μ² = γ_{M/4} = 4sin²(π/4) = 2 精確（任何 M）
- U6 閘：Λ₂ = √12/a₀ = 7.51252e-41 GeV vs 界 1.3e11 GeV（赤字 51.238 orders ⟹ reading A 排除）

## 依賴
O210 → O140 → O139 → O138 → O86 → O213 → O221（並列 O202 / O212 / O220）

## 密度基準
- N_search = 1（本題為極限程序與判定準則；全部 check 為精確恆等式、整數計數或閉式收斂率）
- N_mc = 4×10⁵ walkers，seed = 20260928（MC 只作 d_s ≈ 1 的獨立確認：0.9752）
- d_obs = 51.238158 orders（reading A 之 LIV 赤字，對界 1.3e11 GeV）
- d_med = —（無隨機對照；null 用三種階梯 + 兩套基集）
- q_obs = — → 🟡（純代數 / 結構判定；依 O208 規則以 N_search = 1 跳過 MC 分位數）

## 問題
建立 𝒯 = K_chain ⊗ K_tree 的低能／長波長極限程序 L，還原 (i) GR、(ii) QM，判別極限下「物理 vs lattice artifact」。

## 開放項目
- 本 O 續推（不開新 O）：**U5 已閉（docs/07）**；**U3 已收窄** —— 瓶頸 = **動態度量結構**（3D 可分形變下 |c₁|/c₂ = 0.0033）；3 份鏈之來源（N_gen = 3 / B = 4 已定）；簽名仍為輸入 🔴
- **缺口 1 殘餘（docs/14，下一輪主攻）**：① 🔴 TT 幅度受壓 **150–1000×**（判別格點偽影 vs 真結構）；② 🔴 精確位移商計數（用 Regge-native 位移商繞過天真度量映射）；③ 🟡 Regge 型泛函唯一性
- 跨 O（已入 `problem_register`）：觀測端逐項映射（`cmb_cl/o221-sinc-cl-mapping`，卡 O202 ℓ-軸測度）；reading B 用語裁決（O180 / O159）
- **重跑注意**：`scripts/17_momentum_dof.py` 由 argv 取 M（預設 3）；`data/17_momentum_dof.txt` 係派生聚合檔，全線重跑會覆蓋它（程序見 `01_problem_record.md` §二十一）

## 驗證
- `scripts/01..19`：58/44/15/4/89/**99**/12/22/42/22/14/13/17/23/25/13/44/9/**102** = **667/667**（scripts/17 = 11/11 × M=3,4,6,8）
- 增量獨立審計 `scripts/19_audit_increment.py`（**零 import**、由第一原理：精確算術 / 顯式線性化 EH 二次型 / 直接單形幾何 / 平坦 torus 摺角）：**102/102**
- 舊輪獨立審計 `scripts/05_audit_independent.py`（零 import、不同算法：MC 遊走 / 4 階差分 / 另寫 d_s 掃描器）：**89/89**
- 文檔核對 `scripts/06_doc_crosscheck.py`（read-only，docs 01–14 全覆蓋）：**99/99**
- 審計披露：① d_s 譜定義含零模 ② plateau mid 網格敏感 ③ E[γ] 兩 convention ④ §二十一列 5 項審計側判據修正（文檔數值錯誤 **0**）
