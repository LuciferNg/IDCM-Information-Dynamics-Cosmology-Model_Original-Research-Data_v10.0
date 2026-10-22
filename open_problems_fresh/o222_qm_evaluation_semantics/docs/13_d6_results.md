# 13. D6 對映表操作化 — 結果（`d6-contract-v1`，2026-09-30）

## 0 一句話結論

D6 將「IDCM ↔ QM」由**名詞對照**變成**可計算謂詞表**：13 格中 **9 ✅ / 1 🟡 / 3 🔴**。
IDCM 之 evaluation semantics 在**語義操作層**四對映皆可計算（thunk↔態、force↔測量、memo↔記錄、sharing↔糾纏），
但在**機制層**三項缺席：**Born 概率結構（G7）**、**記錄冗餘（G8）**、**CHSH 非局部性（P4b）**。
關鍵新發現：**非因式化 ≠ 非局部**——秩 61/62（幾乎滿秩）與 CHSH ≤ 2 同時成立，兩者係獨立性質。
本輪**唔宣稱**導出 QM／ħ／Hilbert 公理／Born（戒律）。

## 1 謂詞表（13 格；全部由 scripts/18 精確計算，無浮點、無取樣）

- **P1a ✅** 2I 作用於 62 軸：軌道 = **{12, 20, 30}**（vertex／face／edge 族，型別不變），120/120 群元素皆為置換。
  診斷：62 個標籤 = **31 條對蹠線之雙重覆蓋**（31 對蹠對，每軸恰有一個對蹠）。
- **P1b ✅** 態轉移 s → MUL[s][h(a)] 對 **62/62** 軸皆為 120 階置換 ⟹ 確定性＋可逆。
- **P1c 🟡** 組合律 𝒯 = K_chain ⊗ K_tree **只有 provenance**（O210 `docs/01`、`docs/02`、`final_result.md`、
  `data/02_type_registry.json`）；上游**無載維數**（G6）⟹ 無維數自洽交叉核對 ⟹ 只可報 🟡。
- **P2a ✅** 凍結機器對 **3844/3844** 對 (a,b) 完全可重現；且**獨立 replay 之命中律**預測 lex（15 對）＋ block（18 對）
  全部 **33/33** 對之讀數逐對相同（lex 2 對命中、block 12 對命中）。
- **P2b ✅** **62/62** 設定之值唔係設定之函數（歷史敏感；例 V00 ∈ {−1, +1}）。
- **P2c ✅** 每對 ledger 淨增 = misses − 1 ≥ **1**（lex 總增 28、block 總增 24）⟹ rollback 還原**態**但唔還原**記錄**（不可逆）。
- **P2d 🔴** 表值係**帶號相關**：C1／C2 值集 15 個（±1、±2/3、±1/3、±4/15、±1/5、±2/15、±1/15、0），
  行和 ≠ 1（例 2、4、−8/15、52/15、−10/3…）⟹ **無非負歸一權重** ⟹ 無 Born 型概率結構。
- **P3a ✅** 記錄 append-only：pushes = reads = **85**，14 個命中對**零寫入**；
  靜態規則（只讀頂 `L[-1]`、只 append、`pop` 僅用於 rollback）由 scripts/17 C6 在**凍結源碼**上機械核對。
- **P3b ✅** 記錄**支配**當前態：**2** 對命中返回「當前態唔會給出」之舊值（例：對 (V02,V00)，存 **1** vs 當前 **−1**）。
- **P3c 🔴** 可及深度 = **1**（只讀頂）⟹ 冗餘度 = **1** ⟹ **單副本記錄**，無環境冗餘（QM decoherence 冗餘要求缺席）。
- **P4a ✅** 精確秩（Rational 消元；由 Bareiss 分數自由消元獨立覆核）：rank **C1 = 61**、rank **C2 = 62**、
  rank **C1rev = 61**；rank 1 ⟺ 可因式分解 ⟹ 遠離 rank 1 ⟹ **強非因式化**。
- **P4b 🔴** CHSH：預算內乾淨 `all4` = **16/15 (E1)**、**13/15 (E2)** < 2；界限外 `all4` = 2 (E1)／3 (E2) 屬對蹠污染。
  引 `data/15_b3r2_results.json`（**未重推**）。
- **P4c ✅** no-signalling：**62/62** 軸之 ±1 平衡（Σ_s K[s][a] = 0，列和集合 = {0}）⟹ 每個局部邊際恰 **1/2**；
  另引 A2 之 3844/3844 條件邊際 = 1/2。
  （註：C 之行和 ≠ 0 **唔係**判據——相關 ≠ 邊際；本輪首跑曾誤用作判據，已修，見 §3。）

## 2 三個結構發現（本輪新增；全部可獨立重跑）

**(a) 62 軸 = 31 線之雙重覆蓋。** 62 個軸標籤兩兩成對蹠對（31 對，每軸恰一個對蹠），
但 2I 之**型別**軌道仍是 {12, 20, 30} ⟹ 型別標籤（V/F/E）係按**線**分族，方向本身係雙覆蓋。
呢個解釋咗 A2／B2／B3R2 之 `anti` 表（對蹠配對）為何必須存在。

**(b) 讀算子含 1200/7440 = 16.13 ％ 之「tie」條目。** 當 dot = 0（幾何上正交），凍結建構**唔係**取 0，
而係取「旋轉後參考方向 r 之首個非零分量之符號」（scripts/12 `load_machine`）。
scripts/19 A2b 由**幾何 ＋ 該 tie 規則完全重建整個 K 表：0/7440 mismatch** ⟹ tie 係凍結定義之組成部分，非誤差；
但意味 **K 唔可以由純幾何符號函數重建** ⟹ P1／P2 之任何「純幾何」論述必須附此限定。

**(c) 非因式化 ≠ 非局部。** rank C1 = 61、rank C2 = 62（最大 62）⟹ 表係「幾乎滿秩」之非乘積型；
同時預算內 CHSH ≤ 16/15 < 2 ⟹ **兩者獨立**。故「sharing ↔ 糾纏」之對映：**結構含量（非乘積分解）有**、
**Bell 型非局部性冇**（P4a vs P4b）。

## 3 修正與流程披露（誠實記錄）

1. **機器首跑兩處「過嚴」檢查**（首跑 log 保留 `logs/18_d6_firstrun_impl_defect.out`，首跑 impl = `9d9fff37205d7db6…`）：
   - P1a：我加了合約以外之條件「62 個相異方向」⟹ 誤判 🟡（真相 = 31 線雙覆蓋，屬結構事實非缺陷）；
   - P4c：我誤以 **C 之行和**作 no-signalling 判據 ⟹ 誤判 🔴（真正判據 = ±1 邊際平衡）。
   兩者**皆係 impl 過嚴／用錯判據**，合約 `docs/12` 原文正確 ⟹ **修 impl、重凍、唔改謂詞／門檻**。
2. **審計首跑兩錯**：① 我用「核關係」推軸置換時**漏咗右乘**（旋轉 = 共軛 = 左乘 × 右乘，唔係純左乘）⟹ 得假軌道 {30,32}；
   改為**自寫精確四元數共軛**（完全唔用 `rot_ref`）⟹ {12,20,30} 與 18 一致。
   ② 我假設 trail 有 `top` 欄（實際只有 pair／misses／budget_after）⟹ 改用**閉式命中律**（top = 上一對之 b）獨立預測。
3. **審計 `sign5` bug**：Q(√5) 之 p、q **同號**時仍去比 p² vs 5q² ⟹ 符號判錯；修後 A2b 0/7440 mismatch。
4. **閘自身兩缺陷（已修）**：① C6 切片止於 `xa = rd(a)` ⟹ 漏咗 `pop`；② 有 FAIL 仍寫 `GATE = OPEN` ⟹ 加 `all_ok` 閘門（FAIL ⟹ `CLOSED` 並拒開）。
5. 以上**均未改動任何科學謂詞或數字**：修後重凍、重跑，13 格全部重新計算。

## 4 驗證三件套結果

- 合約閘 `scripts/17`（12 條 C-claims）：**12/12 PASS**，`data/17_d6_freeze.json` **GATE = OPEN**，impl = `a681ae8cf6bcfd69b50a9a3c776f8c43011c3b6c52149bc1f1f565abbe797cf7`。
- 機器 `scripts/18`（13 格）：9 ✅ / 1 🟡 / 3 🔴。
- **獨立審計 `scripts/19`（10 條 A-claims，唔 import 18）：10/10 PASS**；含 A2b 之 K 表完全重建、A4 之閉式命中律 33/33、
  A5 每對淨增 ≥ 1、A6 之 62/62 平衡與歷史敏感、A7 之引用值與 B3R2 記錄逐字相同。

## 5 未閉合缺口（登記在案）

G1（D5 觸發所需 `ctx → s` 映射**唔存在於凍結記錄**；D6 禁自創）、G2（O206 `f(n)` 🔴）、
G4（公平分配之唯一性）、G5（矩形判據之充要刻畫）、**G7（Born 結構 🔴，本輪新增）**、
**G8（記錄冗餘 🔴，本輪新增）**、C2（memo 命中表）、`F_proj = 17 = dim ker T_pipe` 之身份統一。

## 6 重跑與產物

```
cd open_problems_fresh/o222_qm_evaluation_semantics
/usr/bin/python3 scripts/17_d6_contract.py --freeze-impl scripts/18_d6_mapping.py   # 12/12
/usr/bin/python3 scripts/18_d6_mapping.py                                          # 13 格
/usr/bin/python3 scripts/19_d6_audit.py                                            # 10/10
```

| 檔案 | sha256 |
|---|---|
| scripts/17_d6_contract.py | `f63c8d6218404896ac3303cf7c9d1aa492a4c22d922c4abbf6670d01a3eb16bc` |
| scripts/18_d6_mapping.py（凍結 impl） | `a681ae8cf6bcfd69b50a9a3c776f8c43011c3b6c52149bc1f1f565abbe797cf7` |
| scripts/19_d6_audit.py | `23150c60addda1b1c9bd7264b4b8f3fa9293b3f946fd346fea496fbae68c7bd1` |
| data/17_d6_freeze.json | `0dccd562ea07b93849dde0a9ae8b5034c99d56fdb98969db80c1883203bfd2b8` |
| data/18_d6_results.json | `4f53ba00f9c79d5889c979bee0fc442838843e77bd91a8c7c68918bc377bb2be` |
| data/19_d6_audit.json | `44a6d88ae11775a96cc185779282960e84343480ce66d96f9b03a2505a21b803` |

logs：`18_d6.out`、`18_d6_firstrun_impl_defect.out`、`19_d6_audit.out`。
