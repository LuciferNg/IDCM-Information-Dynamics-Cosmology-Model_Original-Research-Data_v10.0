# O137 — 方向一攻堅路線圖：CY₃ 拓撲諧振

> **狀態**: 🔴 全部未推導
> **目標**: 從 CY₃(36,98) 的拓撲幾何正向推導 SM 費米子的 K_Chain 模式分配

---

## 總體目標

建立並求解 88-site K_Chain ⊗ CY₃(36,98) 的**拓撲諧振方程**，證明只有 n=1, 7, 20 以及夸克對應的 n 值能形成不衰減的駐波模式。

---

## 未推導項目完整清單

### 🔴 項目 A：CY₃ 同調群與 K_Chain 耦合方程

**問題**: 1D K_Chain 的每個模式 n 在 CY₃ 的 6D 內部空間中如何分佈？哪些 cycle 與之耦合？

**已知邊界條件**:
- h¹¹ = 36 個 2-cycle (Kähler)
- h²¹ = 98 個 3-cycle (Complex structure)
- CY₃ = 134 = h¹¹ + h²¹

**需推導**:
- [ ] K_Chain 模式 n 與 CY₃ cycle 的耦合項在 Lagrangian 中的形式
- [ ] 每個模式 n 的「拓撲作用量」S_n 的表達式
- [ ] 作用量極值條件 δS_n = 0 的方程

**參考路徑**: 從 O80 W-field Lagrangian 的 kinetic term 出發，加入 CY₃ 內部空間的緊化項。

---

### 🔴 項目 B：駐波條件 (Quantization Rule)

**問題**: 什麼決定了模式 n 在 CY₃ 上形成駐波的能力？

**核心方程**:
```
∮_{C_k} dφ_n = 2πm
```

其中 C_k 是 CY₃ 的 k-cycle，φ_n = exp(i·n·θ) 是 K_Chain 第 n 模式的相位。

**需推導**:
- [ ] 相位 φ_n 在 CY₃ cycle 上的積分表達式
- [ ] 整數 m 與 CY₃ intersection numbers 的關係
- [ ] 從駐波條件導出 n 的允許值集合

**已知提示**: 在 88-site 環上，相位 φ_n = 2πn/88。駐波條件要求這個相位在 CY₃ 的 cycle 上完成整數圈。

---

### 🔴 項目 C：特徵值流與極值點

**問題**: 在 88 個 n 模式中，哪些在 CY₃ 卷積後其幾何作用量處於極值？

**需推導**:
- [ ] 作用量 S_n = S_chain(n) + S_CY₃(n) + S_coupling(n) 的完整形式
- [ ] 對 n 求導 dS/dn = 0 的方程
- [ ] 驗證 n=1, 7, 20 是否為極值點

**方法**: 將 S_chain(n) 視為 γ_n = 4sin²(nπ/88) 的函數，S_CY₃(n) 為 CY₃ 投影的函數，找總作用量的極值。

---

### 🔴 項目 D：色荷纏繞偏移

**問題**: 夸克帶有 SU(3)_c 色荷，其模式 n_q 與輕子模式 n_l 有何關係？

**核心假設**:
```
n_q = n_l + Δn_color(h¹¹/h²¹)
```

**需推導**:
- [ ] 色荷纏繞 Δn_color 的精確形式
- [ ] h¹¹/h²¹ = 36/98 在色荷偏移中的角色
- [ ] 驗證: 對於給定的輕子 n_l, 夸克 n_q 是否落在 O136 候選的 n 值上

**候選偏移**:
- 上型夸克: Δn_up = ?
- 下型夸克: Δn_down = ?

---

### 🔴 項目 E：D_quark 的幾何推導

**問題**: v9.0 的色荷修正 D_quark = 1 + h¹¹/h²¹ × ε × (1+ε) 能從 CY₃ 拓撲推出嗎？

**需推導**:
- [ ] D_quark 作為 CY₃ 同調群的譜序列 (spectral sequence)
- [ ] 為什麼 h¹¹/h²¹ 出現，而不是其他 Hodge 數組合
- [ ] ε × (1+ε) 作為自能 propagator 展開的幾何解釋

---

### 🔴 項目 F：投影因子 P_f 的 CY₃ 推導

**問題**: O54 的 P_f 值 (L₆/F₅, Nd-E_proj, Nd-L₄) 能從 CY₃ 的 intersection numbers 推出嗎？

**需推導**:
- [ ] CY₃ intersection numbers 的數值 (需從 toric 幾何計算)
- [ ] P_f 與 intersection numbers 的關係
- [ ] 為什麼輕子 P_f 採用 Nd-L₄ 等形式

---

## 攻堅優先順序

```
Phase 1: A + B + C
    ↓
建立諧振方程 → 計算駐波條件 → 找極值點
    ↓
驗證 n=1, 7, 20 是否為極值
    ↓
Phase 2: D
    ↓
色荷纏繞 → 夸克模式分配
    ↓
Phase 3: E + F
    ↓
D_quark 幾何推導 → P_f 幾何推導
```

## 依賴關係

- **Phase 1** 依賴: O80 (W-field Lagrangian), O34 (質量譜), O36 (自能)
- **Phase 2** 依賴: Phase 1 結果, O53 (CY₃ toric geometry) 🟢
- **Phase 3** 依賴: Phase 1+2 結果, O59 (SU(12) subspace) 🟢

## 成功標準

1. 從諧振方程精確導出 n=1, 7, 20
2. 從色荷纏繞導出夸克 n 值
3. 所有導出 n 值與 O136 候選一致 (或給出更好的候選)
4. 偏差 < 1% 的質量預言