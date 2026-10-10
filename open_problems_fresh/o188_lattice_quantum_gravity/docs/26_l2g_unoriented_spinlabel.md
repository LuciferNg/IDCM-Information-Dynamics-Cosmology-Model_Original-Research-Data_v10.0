# O188 docs/26 — R12 L2g：unoriented 60×31 表 + spin-label 候選測試（最後殘留正面攻擊）

**日期**: 2026-10-10（Route L2 第九輪）
**腳本**: `scripts/26_l2g_unoriented_spinlabel.py` — **6/6 PASS**（logs/26.txt）
**對象**: 「elementwise spin-label map 唔 claim」—— O188 唯一未閉合位置，正面嘗試

---

## 〇、一句話

**對「elementwise 唔 claim」做咗正面攻擊**：
1. 建構 **unoriented evaluation table U[60][31]**（120 rows → 60 按 q/−q cover；62 columns → 31 按 ± axes merge）—— 一個乾淨嘅 shared object
2. 測試自然 spin-label 候選：**stabiliser order → j = (order−1)/2**（C₅→j=2、C₃→j=1、C₂→j=½，dim 5/3/2）
3. **面積譜對照 FAIL**（√(j(j+1)) = {√6, √2, √3/2} vs frame norms {√(5/2), √3, 1}：ratios 1.549/0.816/0.866 無共同比例）⟹ **自然候選被結構性否定** —— 「唔 claim」而家有結構根據

## 一、精確結果

| 檢查 | 內容 | 結果 |
|:-----|:-----|:-----|
| C1 | **Unoriented table U[60][31]**：60 distinct rows（generic reference）、31 lines、entries {−1,0,+1}、rows 全 unique、zeros=60（記錄） | ✅ |
| C2 | 120 elements → 60 row-classes、multiplicity pure 2:1（unoriented 下 cover 完整） | ✅ |
| C3 | **Pointwise stabiliser**（2I 內精確）：vertex 10、face 6、edge 4 ⟹ I 內 C₅/C₃/C₂ | ✅ |
| C4 | Spin-label 候選：{j=2 ×6, j=1 ×10, j=½ ×15}；**dim sum = 90** = Σγ_even（R1 176-L parity）—— coincidence candidate，冇 operator identity，唔 claim | ✅ |
| C5 | **面積譜對照 FAIL**：無共同比例 ⟹ 自然候選唔 work（誠實結構性否定） | ✅ |
| C6 | 判決：elementwise spin-label **no**，但係有結構根據嘅 no；unoriented 表係乾淨共享物件 | ✅ |

## 二、結構意義

- **「唔 claim」由「未嘗試」→「有根據嘅否定」**：O188 一直誠實標記 elementwise 唔 claim；R12 試咗最自然嘅候選（stabiliser→spin label），**面積譜對照揭穿** —— 表示論(j)同幾何對稱(order)唔係直接同一。
- **U[60][31] 係新 shared object**：unoriented evaluation table —— 120→60（SU(2)-type cover 摺疊）+ 62→31（antipodal merge）後，係 I 嘅 **60 rotations × 31 lines** 嘅 sign 表 —— 同 LQG boundary state 嘅「unoriented edge + node」picture 對齊嘅候選（但係呢個 table 本身有 zeros=60，記錄咗）。
- **C4 嘅 dim sum = 90**：6×5+10×3+15×2 = 90 = Σγ_even（176-L parity）—— 有趣但**純 coincidence candidate**（冇 operator identity 將 line dims 接到 chain spectrum）；按紀律唔 claim。
- **C5 嘅否定係有價值嘅**：佢敍明點解 elementwise map 唔會係「stabiliser order ↔ spin label」—— 兩個量尺度唔同（表示論 vs 對稱階）。

## 三、判決

- **L2g：完成（unoriented 表）+ 誠實否定（spin-label 自然候選）**
- **L2 缺口最終狀態**：frame 級對應**完整**（threshold、cover、per-row 統計、unoriented 表）；elementwise spin-label **冇**，但「冇」而家有結構根據（表示論 vs 幾何對稱嘅 mismatch）
- 🔴 未閉合：pattern-wise spin-label map（rep-theoretic 而非 geometric-symmetry）需要新思路；dim sum 90 係 coincidence candidate

## 四、同前輪對比
- R5：K 表係 ℝ³ threshold（構造層）；R7：全表 + cover；R10：per-row 統計定理；**R12：unoriented 表 + spin-label 候選被否定** —— L2 嘅「唔 claim」而家有完整嘅否定鏈