# O188 docs/21 — R7 L2e：全量 120×62 K 表驗證（threshold identity + 表層 double cover）★

**日期**: 2026-10-10（Route L2 第七輪）
**腳本**: `scripts/21_l2e_full_k_double_cover.py` — **7/7 PASS**（logs/21.txt）
**對象**: R5（30-row slice）→ **full-table 驗證**；R6（frame 級）→ **表層 double-cover**

---

## 〇、一句話

完整 120×62 K 表（74 40 entries）**全表**驗證通過：
- **K[i][a] = sign(⟨rot_ref(q_i, U₀), u_a⟩)** — 7440 個 entries 零 mismatch（精確 Fraction）
- **2:1 double cover 喺表層面實現**：row(q) = row(−q) ∀q；generic reference 下 **60 個 distinct rows = |I|**，multiplicity 2
- **Vertex reference 令 K 表嘅 row space 直接等於 12 個二十面體 vertices**（multiplicity 10 = |2I|/12）—— 表嘅行空間本身係 vertex set
- 附加結構：vertex/face column block 嘅 +1 fraction = **0.5**；edge block = **1/3**（記錄，唔係判準）

## 一、精確結果

| 檢查 | 內容 | 結果 |
|:-----|:-----|:-----|
| E1 | 完整 K：120×62，字母 {−1,0,+1}（0 = 精確正交） | ✅ |
| E2 | **Threshold identity 全表**：7440 entries，mismatch = **0** | ✅ |
| E3a | Vertex-reference rows：row(q)=row(−q) 120/120；**distinct rows = 12 = 二十面體 vertices**；multiplicity {10} | ✅ |
| E3b | Generic-reference rows：row(q)=row(−q) 120/120；**distinct rows = 60 = \|I\|**；multiplicity {2} —— 純 2:1 cover | ✅ |
| E4 | Sign balance（informative）：vertex/face block +1 fraction = 0.5、edge = 1/3 | ✅（記錄） |
| E5 | sign_rank ≤ 3 by factor-rank bound（O222 600/600 作證人） | ✅ |
| E6 | 判決：IDCM evaluation 表層帶 SU(2)-type 2:1 結構 | ✅ |

## 二、結構意義

- **R5 嘅 slice 結論而家係全表定理**：唔只 30 行，**成個 120×62 K 都係 ℝ³ threshold 矩陣**（由構造保證 sign_rank≤3）。
- **表層 double cover（E3b）**：120 個 quaternions 摺成 60 個 distinct rows = |I| —— IDCM 嘅 QM evaluation 層**本身就帶 SU(2)→SO(3) 型 2:1 摺疊**（spin-½ 先需要嘅 cover），同 LQG 用 SU(2) 做 state space 嘅結果同構（**cover 結構層面**）。
- **Vertex reference（E3a）**：用 O222 嘅原 reference axis（U₀ = vertex axis）時，K 表 row space **直接就係 12 個二十面體 vertices** —— 即 evaluation 表嘅「狀態空間」喺最天然嘅 reference 下就係 icosahedron 嘅 vertex set（同 R6 嘅 62=12V+20F+30E frame 完全自洽）。
- **Sign balance（E4）**：vertex/face block = 1/2（中性對稱），edge block = 1/3 —— 反映 edge-direction 幾何相對於 vertex reference 嘅投影統計；記錄以供後續（例如 = 1/3 對應 edge/face 比？唔過度詮釋）。

## 三、判決

- **L2 缺口狀態更新**：
  - 🔴 comparability（R2/R3）：否證
  - 🔴 incidence（R4）：中性
  - ✅ threshold family（R5）：抽象家族
  - ✅ 具體 frame（R6）：二十面體 cell frame
  - ✅ **全表驗證（R7）**：threshold identity 全表 + 表層 2:1 double cover + row space = vertex set
- **未閉合（誠實）**：elementwise spin-label 對應仍未 claim；「cover 結構」係群論層面（2I→I = SU(2)→SO(3) 嘅離散類比），唔係 spin-½ 表示嘅直接對應。
- **下一步候選**：① K 表 columns 按 vertex/face/edge 分塊嘅 sign 統計有結構（edge=1/3）—— 可以對比 LQG boundary state 嘅 area distribution；② L1 單點 (22,1) 嘅 operator identity（需要新算子）；③ 檢查 R1 嘅 176-L parity 有冇喺 62-axes frame 出現（176 = 88×2 = 2×88？176 vs 62？—— 純數值比較要小心）。

## 四、同 R5/R6 對比
- R5：30-row slice threshold identity（構造層）
- R6：62 axes = 二十面體 frame；2I(120) → I(60)（群層）
- R7：**全表 threshold identity + 表層 double cover（表層）** —— 三輪由「構造」到「群」到「表」完整閉環。