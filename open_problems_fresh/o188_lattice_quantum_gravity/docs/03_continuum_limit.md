# O188 docs/03 — 連續極限比較：IDCM decimation → GR vs LQG spin foam → GR

**日期**: 2026-10-04（Route L3）
**腳本**: `scripts/03_continuum_limit.py` — **6/6 PASS**（logs/03.txt）
**對應路線**: O188 01_problem_record §四 L3

---

## 〇、一句話

兩條通往 GR 嘅離散路線**共享 Regge 作用量作為共同物件**，但到達方式相反：
IDCM 用**精確細化流 L**（M → 4M，c 不動點）零新參數組裝 Regge 泛函；
LQG 用**半經典大-j 極限**（spin foam vertex → e^{iS_Regge}）但帶 Immirzi 參數自由度。
Regge 係共同語言；**參數自由 vs 零參數**係最關鍵分歧。

---

## 一、IDCM → GR（引用 O221，已閉合 900/900）

| 量 | 值 | 出處 |
|:---|:---|:-----|
| 極限程序 L | M → 4M、a → a/4、√J → 4√J；ℓ → ∞ | O221 docs/01 |
| 不變量 | c = a_ℓ√J_ℓ = R_world·ω_ring（ℓ=0..6 dev=0） | O221 docs/01 💾 本輪 D1 |
| 色散 | ω_n = c k · sin(x)/x（x = πn/M） | O221 docs/01 💾 本輪 D2 |
| Regge 泛函 | S_R = Σ_h A_h δ_h（虧角組裝，零新參數） | O221 docs/12 💾 本輪 D4 |
| Graviton DoF | D(D−3)/2 = 2（4D） | O221 docs/12 💾 本輪 D3 |
| 4-simplex 二面角 | arccos(1/4) = 1.3181160717 | O221 docs/12 💾 本輪 D4 |

## 二、LQG → GR（文獻）

| 量 | 值 | 出處 |
|:---|:---|:-----|
| 半經典極限 | 大 j 駐點：vertex amplitude → e^{iS_Regge}（Ponzano-Regge 3D 精確；4D EPRL 型半經典） | 文獻 |
| 面積譜 | Â 本徵值 ∝ 8πγ l_P² √(j(j+1))，γ = Immirzi | 文獻 💾 本輪 D5 |
| 連續極限地位 | spin foam → GR 係**半經典極限**（非細化流）；dof 配對完整性仍開放 | 文獻 |

## 三、對應項 vs 非對應項明細（S1）

### ✅ 對應項
1. **Regge 作用量係共同物件**：IDCM S_R = ΣA_h δ_h 與 LQG 半經典 vertex 極限 **同一個泛函族** —— 這是兩路線實質交集（最強對應）。
2. **離散譜**：IDCM γ_n（譜值）與 LQG 面積 √(j(j+1)) 都係離散；低能取極限後都指向連續 GR。
3. **Graviton DoF = 2**：兩條路線都預言 4D 重力兩個偏振（IDCM 經連續端二次型 rank；LQG 經 4D Regge/boundary）。

### ❌ 非對應項（S2）
- **極限程序**：IDCM 係**精確細化流**（每一層都係流動的一部分，c 不動點）；LQG 冇 decimation analog —— spin foam 嘅「連續極限」係**半經典駐點**，係近似。
- **參數自由度**：IDCM Regge 組裝**零新參數**；LQG 面積譜帶 **Immirzi 參數 γ**（自由，需固定）—— 結構自由度成本 0 vs 1。
- **網格角色**：IDCM 有固定格點（88-site）+ 共動重標定；LQG 冇固定格、圖係任意 ── 背景獨立性主張相反面。

---

## 四、判決

- **L3 結構對應 = 中等**：Regge 泛函 + graviton dof 係**真對應**；極限程序與參數自由度係**本質性分歧**（IDCM 零參數精確流 vs LQG 帶 γ 半經典極限）。
- 符合 S3：冇宣稱「LQG 嘅 GR 極限 ≡ IDCM 嘅 GR 極限」；**兩路線收斂到同一 GR，但一個無自由參數、一個帶 Immirzi**。
- **隨附修正**：初版 D2 級數截斷至 x⁸（dev 8.4e-23 假 FAIL）⟹ 擴至 x²⁰（dev < 1e-50，PASS）；判準不變。