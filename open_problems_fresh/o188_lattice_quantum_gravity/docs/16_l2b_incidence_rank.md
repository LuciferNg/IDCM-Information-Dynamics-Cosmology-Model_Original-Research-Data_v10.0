# O188 docs/16 — R4 L2b：incidence 機制檢查（誠實修正）

**日期**: 2026-10-10（Route L2 第四輪）
**腳本**: `scripts/16_l2b_incidence_rank.py` — **5/5 PASS**（logs/16.txt）
**對象**: L2 殘留「換機制：correlation/incidence 表」

---

## 〇、一句話

試圖由「comparability」換到「**incidence（boundary operator）**」機制驗證 L2。
結果（誠實修正）：**incidence 機制係中性** —— 稀疏 incidence 唔似 comparability 咁強制 sign_rank≥4（子矩陣精確 min sign-rank 低至 1），**冇關閉門畀 rank-3**；但亦冇建立到 rank-3 同 IDCM 嘅對應。
**「類型不匹配」只對 causal-comparability 成立；incidence 係 OPEN DOOR。**

## 一、精確結果

| 檢查 | 內容 | 結果 |
|:-----|:-----|:-----|
| R1 | d_3（5×10 tetra←tri）、d_2（10×10 tri←edge）pattern + rank over R | ✅ d_3=4（組合秩）、d_2=6 |
| R2 | all-±1 rectangular 子矩陣 bound | ✅ max=1（太弱，唔可以強制 ≥4） |
| R3 | d_3 子矩陣精確 min sign-rank：5×4→**1**、4×4→**1** | ✅ 低秩 completion 存在 |
| R4 | Control：全 ±1 3×3 rank=3（rank-3 可達） | ✅ |
| R5 | **修正判決：incidence 中性** | ✅ |

## 二、同第一版嘅修正說明（誠實）

- **第一版錯誤**：用「all-±1 方形子矩陣」下界想證明 incidence 都要 ≥4 —— 對稀疏 incidence **方法失效**（d_3 冇 k≥3 嘅 all-±1 block）。
- **修正後事實**：d_3 嘅代表性子矩陣（5×4、4×4）精確 min sign-rank = **1** —— **incidence 容許極低秩**，同 comparability（{2,2,4,{4,5}}）本質唔同。
- 呢個係**方法論修正**（唔係放寬判準）：數據推翻咗錯誤嘅假設「incidence 都要 rank≥4」。

## 三、結構意義

- **L2 嘅「類型不匹配」要精確化**：只適用於 causal-comparability（R2/R3 嘅 4-simplex、R3 嘅維數規則）。**spin-foam 嘅 cell-incidence（boundary operator）係另一個機制，佢冇閉關門畀 IDCM rank-3**。
- **OPEN DOOR**：理論上可以構造一個 rank-3 嘅 incidence-type 結構對應到 IDCM —— 但需要實際構造（未做）。
- **與 O222 連結**：IDCM K 表本身係「correlation / 符號」表（sign_rank=3）；spin-foam incidence 同樣係「0/±1 符號」表 —— 呢類符號表對 rank-3 開放。

## 四、判決

- **L2 缺口狀態更新**：由 R2/R3 嘅「類型不匹配（負）」→ **「comparability 側否證（維持）；incidence 側開放（未測封）」**。
- 🔴 未閉合：需要實際構造「rank-3 incidence-type 對應」先可以閉合 L2 正面；本輪只做咗「冇關閉門」嘅檢查。
- **下一步候選**：用 O222 嘅 correlation 表構建方式（120×62 或 62×62 sign matrix）直接對比 spin-foam 嘅某個 incidence —— 建立實際 rank-3 對應（若存在）。