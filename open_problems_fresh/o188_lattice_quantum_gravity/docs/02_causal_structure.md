# O188 docs/02 — 因果結構：sign_rank(K) ≤ 3 vs Spin Foam Causality

**日期**: 2026-10-04（Route L2）
**腳本**: `scripts/02_causal_structure.py` — **5/5 PASS**（logs/02.txt）
**對應路線**: O188 01_problem_record §四 L2

---

## 〇、一句話

IDCM 因果張量帶**嚴格的秩 **3** 符號實現**（O222 閉合定理），而 spin foam 因果結構係 **2-complex + Pachner moves**。
兩者共享「因果可分層 ≤ 3」嘅階層直覺，但秩定理係**線性代數**性質、Pachner 係**組合拓撲**性質 —— 非同一物件，不強行對應。

---

## 一、IDCM 側（引用 O222，定理級）

- **sign_rank(K) = 3 精確**（O222 Session 18 R20）：600/600 候選 r=3 全接受、r=2 由 circular-arc lemma 排除（M7）⟹ 因果張量可被 3 個隱變量層符號實現。
- 早期記錄 [5,6]（R19）已由 M3 修正為 [2,3] 再鎖定 = 3。
- Bell 結果：共存層 CHSH ≤ 2 精確（LHV-class）、rollback 層超額係 history-mediated contextuality（O222 B5）—— IDCM 因果秩 3 與「量子非局域」**無**直接連結。

## 二、Spin foam 側（文獻 + 本輪組合學復現）

| 量 | 值 | 出處 |
|:---|:---|:-----|
| Spin foam | 2 維複形（面/邊/頂點），dual 到 4D triangulation | 文獻回顧 |
| Pachner 1-5 | 一個 4-simplex → 5 個（net +4, 頂點 +1） | 本輪 C2 ✅ |
| Pachner 2-4 | 兩個 4-simplex 共享四面體 → 4 個（內部邊 recoupling） | 本輪 C3 ✅ |
| 因果 orientation | 2-complex 邊帶 future/past（causal spin foam） | 文獻 |

## 三、對應項 vs 非對應項明細（S1）

### ✅ 對應項
1. **可敘事因果階層**：IDCM 秩 ≤ 3 ⟹ 因果結構可壓成 3 層；spin foam causality 天然有「過去/現在/未來」3 分類 —— **同為「層數 ≤ 3」的結構直覺**（注意：係直覺，唔係定理等價）。
2. **細化作為演化**：IDCM L7 細化流係演化程序（O213）；spin foam 亦有 refinement 程序（1-5 moves 及 coarse graining）—— 兩者都係「時空由細化/重組生成」。

### ⚠️ 巧合候選（C4，誠實標記）
3. **數字 4**：IDCM 細化比 4:1（M → 4M）與 Pachner 1-5 增加 4 個 4-simplex —— 數字相同但**機制唔同**（IDCM = 固定尺度流；Pachner = 尺度不變局部 move）⟹ 本輪**明確不宣稱結構同一**，只記巧合候選。

### ❌ 非對應項（S2）
- **秩定理 vs 組合 move**：sign_rank ≤ 3 係**矩陣分解**性質；Pachner moves 係**複形重三角化** —— 冇已知映射。
- **約束結構**：LQG 有 Hamiltonian 約束（微分同胚不變），IDCM 冇此概念（O188 SESSION_START 陷阱清單）。
- **因果方向**：spin foam causal orientation 來自 2-complex 定向；IDCM「因果」來自求值 chaining（O222 thunk/force）—— 語義不同。

---

## 四、判決

- **L2 = 結構直覺對應，冇形式化定理**：IDCM rank-3 與 spin foam causality 之間「可敘事階層 ≤ 3」係有意義類比，但唔係數學同構；數字 4 嘅重合列為巧合候選。
- 符合 S3：**本質性對應障礙（秩 vs 組合、約束缺席）已如實記錄**，冇為閉合而擬合。