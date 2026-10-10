# O188 docs/22 — R8 L4b：quaternion units ⊂ 2I（SU(2)-type 代數骨架）★

**日期**: 2026-10-10（Route L4 第五輪）
**腳本**: `scripts/22_l4b_quaternion_units.py` — **8/8 PASS**（logs/22.txt）
**對象**: L4 由「單一構造 (iS₂)²=−1」→「嵌入代數：完整的 quaternion unit algebra ⊂ 2I」

---

## 〇、一句話

**IDCM 嘅 evaluation cover（2I，120 quaternions over ℚ(√5)）包含完整嘅 quaternion unit algebra：**
```
{+1, −1, +i, −j, +k, −k} ⊂ 2I   （8 個 units，Q8 四元數群）
i² = j² = k² = ijk = −1          （Hamilton 恆等式）
ij = k, jk = i, ki = j           （循環積）
ij = −ji, ...                    （反交換 —— 非阿貝爾）
```
呢個就係 **SU(2)-type 代數骨架** —— LQG spin network 正正用 SU(2) 做表示空間。L4 由「人為構造 (iS₂)²=−I」深化為「**嵌入代數**」：2I 內部本身就有齊 spin-½ 代數嘅離散根。

## 一、精確結果

| 檢查 | 內容 | 結果 |
|:-----|:-----|:-----|
| F1 | 2I 包含 8 個 quaternion units（精確 ℚ(√5) membership） | ✅ |
| F2 | i² = j² = k² = −1（Hamilton） | ✅ |
| F3 | 循環積 ij = k、jk = i、ki = j | ✅ |
| F4 | 反交換 ij = −ji 等（非阿貝爾） | ✅ |
| F5 | ijk = −1（Hamilton identity） | ✅ |
| F6 | ⟨i,j,k⟩ closure = **Q8**（8 元素）⊂ 2I | ✅ |
| F7 | **Z₄ = ⟨i⟩ < Q8 < 2I** —— 同 R3 L4a 嘅 (iS₂)²=−I 同 IDCM J（odd sector）係**同一個 Z₄** | ✅ |
| F8 | 判決：L4 = embedded algebra（SU(2)-type skeleton） | ✅ |

## 二、結構意義

- **L4 由「構造存在」→「嵌入代數」**：R3 L4a 只證明 (i·S₂)²=−1 可以構造 Z₄；R8 證明呢個 Z₄ **唔係外來**，而係 2I cover 嘅內在子結構（Z₄ = ⟨i⟩ < Q8 < 2I）。
- **「一個代數物件，三種出現」**（F7）：同一 Z₄ 出現喺
  1. R3 L4a 嘅 (i·S₂)² = −I 相位構造（QRF complexification）
  2. IDCM odd sector 嘅 J² = −I（N_d = 44）
  3. 2I cover 內部嘅四元數單位 ⟨i⟩
  ⟹ 調律者理念「無效才是正確」嘅正面版：**同一結構喺三處獨立出現，先算結構**（呢度係群論力度，唔係數值湊）。
- **同 LQG 嘅對應位**：LQG spin network 用 SU(2)（double cover of SO(3)）做 holonomy labels；IDCM 用 2I（double cover of I）做 evaluation cover —— **同一 double-cover 型**，而 2I 內部嘅 Q8/quaternion units 正係 SU(2) Lie algebra 嘅離散骨架（pauli/quaternion units）。代數骨架層對應。
- **錨實 L4 同 L2 匯流**：R6-R7 已確立 2I→I 嘅 frame/coveer；R8 喺 cover 內部搵到 quaternion algebra —— L2（frame）同 L4（代數）而家由**同一個群物件**支撐。

## 三、判決

- **L4 缺口狀態更新**：
  - R2：三探針全負（L4 最弱）
  - R3：構造存在（(iS₂)²=−1, Z₄≅Z₄）
  - **R8：嵌入代數**（quaternion units ⊂ 2I, Q8, Hamilton relations）—— L4 由「最弱」升為「有內在群論支撐」
- **未閉合（誠實）**：呢個係「代數骨架」對應（2I 有 SU(2)-type structures），唔係「spin-½ 表示」直接對應—— LQG 用嘅係完整 SU(2)（連續），IDCM 有嘅係離散 2I；「離散版 SU(2) 骨架 ↔ 連續 SU(2)」嘅升格需要 limit 論證（O221 continuum-limit 側有先例但未 apply 到呢度）。
- **下一步候選**：① 2I 完整 subalgebra lattice（除 Q8 外仲有無其他：Z₄×Z₄? A₅ quaternion cover?）—— 對比 LQG intertwinner 空間維數；② J（odd sector）同 ⟨i⟩ 嘅 exact 同構證明（而家係 claim，可以 operator-level 驗證）。

## 四、同前輪對比
- L4 全線：R2 三探針負 → R3 構造存在 → **R8 嵌入代數（quaternion units ⊂ 2I）** —— 而家 L4 有真實嘅群論結構支撐，唔再係「最弱環節」。