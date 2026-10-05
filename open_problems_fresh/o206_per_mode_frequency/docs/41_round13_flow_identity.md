# O206 — 第十三輪 docs/41: even/odd 兩流身份（2 PASS / 1 FAIL + exploratory）

> **日期**: 2026-10-06 · **Script**: `scripts/37_flow_identity.py`（**2 PASS / 1 FAIL**）· **Log**: `logs/37_flow_identity.out` · **Data**: `data/37_flow_identity.json`
> **承接**: 第十二輪後剩餘——even/odd 兩流身份（{u,s,c,b} vs {e,d,μ,τ}）。「繼續」⟹ L1 quark/lepton 分層 null · L2 塊層 even/odd 比 · L3 u/d 二重結構 · L4 exploratory。
> **verdict**: **①light lepton 全落 odd rank 概率 p=0.0714——邊緣 FAIL（誠實）**，但附註「5 quark 只 4 even 位，4/5 quark even 已達分層極限」；②**u/d 二重結構確立：rank 身份對 u/d 零變（保持率 1.0000）＋ C_f 鋸齒敏感（0.7740）**——「身份 vs 振幅」兩層分離；③**κ 非對角方向失格**（載體 CSSG-v3 第十輪已降級）——唔列為開放方向；④L4 exploratory：lepton modes = {1,5,9} 等差 4（事件後觀察，1/56 nominal，**唔當 PASS**，需下一輪 pre-register 盲測）。

---

## L1. quark/lepton 分層 null —— 邊緣 FAIL（誠實）

- P(3 輕子全落 odd rank) = C(4,3)/C(8,3) = **4/56 = 0.0714**（1/14）——唔達 0.05 ⟹ ❌
- 實測：e→rank1(odd)、μ→rank5(odd)、τ→rank7(odd) = 全 odd ✓（但對應嘅 null 概率邊緣）
- **附註（重要）**: 8 rank 只有 4 even 位，而 quark 有 5 個 ⟹ 「4/5 quark even」已係**分層極限**——
  任何結構最多只能做到 4/5 quark 喺 even 位；實測**達極限**（犧牲者 = d，最輕嘅 down-type）。
  用「極限到達」做 framing：P(極限) = P(輕子全奇位) = 0.0714，仍然是邊緣。

## L2. 塊層 even/odd 幾何中位比（只報告, 唔設閘）

| 塊 | even 流 | odd 流 | ratio |
|:--|:--|:--|:--|
| gen1 (e,u,d) | u = 3.803 | sqrt(e·d) = 3.628 | **1.048** |
| gen2 (s,μ,c) | sqrt(s·c) = 87.682 | μ = 30.031 | **2.920** |
| gen3 (τ,b) | b = 255.752 | τ = 159.644 | **1.602** |

- 全部 >1（同鋸齒一致）；gen2 嘅 2.92× 最突出（s, c 同時大過 μ）。
- gen1 嘅 1.048 極小 —— **u 對奇流嘅優勢極脆弱**（對應 u/d 崩潰區：u 只要輕過 0.4454·d 就反轉）。

## L3. u/d 二重結構 —— 身份 vs 振幅 分離 ✅（2 PASS）

- **rank 身份**（lepton 全 odd rank）喺 PDG u/d 範圍內**保持率 = 1.0000** ✅（u∈[1.8,3.5], d∈[4.5,5.3] 下 lepton 奇位永恆）
- **C_f 鋸齒**（交替）保持率 = **0.7740** ✅（同 T3 一致, ±1% 內）
- ⟹ **「even/odd 身份」同「鋸齒振幅」係兩個獨立層**：身份（quark/lepton 分類）對 u/d 完全穩健；
  振幅（C_f 交替序）對 u/d 敏感 23%。層次分明 —— 呢個係先前 23% 崩潰區嘅正確歸因。

## L4. exploratory —— lepton modes {1,5,9}（等差 4）🎯 事件後, 唔當 PASS

- 將正序指派 rank→mode 翻譯：lepton（e,μ,τ）→ modes {1,5,9}，公差 [4,4] —— 等差 4
- nominal P(指定 3-subset) = 1/C(8,3) = **1/56 ≈ 0.018**
- ⚠️ **事件後觀察**：唔係 pre-registered；「公 4」係 4 個 odd-subset 中特別選出嘅一個（{1,3,5} 公 2 亦等差）
  ⟹ 唔入 PASS count。盲測設計（下一輪 pre-register）：H0 = quark/lepton label 隨機 8! 次，
  命中「lepton modes 等差」＋「全奇位」聯合頻率。
- 附加提醒：L4 本質上係 L1 嘅 mode 翻譯（全奇 rank ⟺ modes ⊂ {1,3,5,9}）；
  「等差 4」只係 subset {1,5,9} 比其餘 3 個 odd-subset 額外靚 —— 需要盲測先可以列結構。

## ★ κ 非對角方向失格（判決）

- 第十一輪/十二輪列「κ 張量非對角組合」為唯一未封死方向——**撤回**。
- 理由：`κ_ijk = 18·I₉` 出自 **CSSG-v3**（O64 後驗 assignment），而 CSSG-v3 喺第十輪 docs/33
  已裁定：**5/9 非法模式 + 後驗池擬合 ⟹ 9/9 閉合降級**。載體本身已失格 ⟹ 「κ 非對角」唔係合法結構輸入。
- 已否證／降級路線唔重推（register 禁區紀律）。

## 總結（誠實）

| 問題 | 結果 | 意義 |
|:--|:--|:--|
| L1 分層 null | ❌ p=0.0714 邊緣 | quark/lepton 分層有方向但未過 5%——「4/5 quark even = 極限」係最強 framing |
| L2 塊層比 | 報告 | gen2 2.92× 突出；gen1 1.048 脆弱（u/d 閘） |
| L3 u/d 二重 | ✅✅ | 身份（rank）穩定 + 振幅（C_f 序）脆弱——兩層分離 |
| L4 lepton {1,5,9} | 🎯 exploratory | 等差 4, nominal 1/56, 需盲測 |
| κ 非對角 | 🔴 失格 | CSSG-v3 載體已降級 |

**剩餘方向（更新）**:
- 🔬 L4 盲測（lepton modes 等差 + 全奇位聯合 null）——下一輪主攻
- 🔴 even/odd 兩流「成因」仍開放（身份層穩健、振幅層脆弱 —— 兩層各自要生成器？）
- 🟡 u/d 崩潰區 23%（已歸因為「振幅層」）
- 🟢 已關: κ 非對角（載體失格）

## 文件動作

- scripts/37 + logs/37 + data/37 json + docs/41（本文件）。
- SESSION_START append（第十三輪節）· README O206 行 round-13 更新 · register O206 note。