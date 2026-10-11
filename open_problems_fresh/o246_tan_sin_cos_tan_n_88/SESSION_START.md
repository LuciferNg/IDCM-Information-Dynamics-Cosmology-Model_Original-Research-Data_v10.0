# O246 SESSION_START — tan 家族開譜掃描：sin/cos → tan²(nπ/88) 全開放問題探針

<!-- registry
pid:     O246
title:   tan 家族開譜掃描：sin/cos → tan²(nπ/88) 全開放問題探針
state:   registered
verdict: -
flags:   -
owner:   O246
created: 2026-10-10
updated: 2026-10-10
prereq:  -
source:  調律者 2026-10-10: 開新O掃全部開放問題; tan 分析示範
-->

> **Session**: 2026-10-10（新建立）
> **狀態**: 📄 **已註冊 — 未開始（開完不推）**
> **來源**: 調律者 telegram 2026-10-10: 「開新o, 把所有開放問題掃一遍就知道了，剛才就當作示範，記錄在新o中，叫新o再驗證後交接到歸屬o, 同樣開完不推」
> **前置**: -
> **位置**: `open_problems_fresh/o246_tan_sin_cos_tan_n_88/`

---

## 一、接手起點

新 O（2026-10-10 註冊，未開始）。調律者指示：掃全部開放問題（130 主 O + 157 子問題），以 tan²(nπ/88) 分析做**示範**，驗證後交接去歸屬 O，**開完不推**。

tan 示範分析已完成並實測（2026-10-10 當日，mpmath 40-50 dps）：
1. tan² 譜行為：n=44 pole（cos²=0）→ 唔可以做譜基底
2. arctan∘tan = 三角波 fold（88 格全 ✓）→ tan 本質 = 方波積分橋
3. 三角家族全景：IDCM 已有 sin/cos/sec/csc/atan（O117 sec、O140 csc、O123 atan）
4. 88=8×11：tan 喺 n=11k 取八角分圓值
5. **新發現 Σtan²(nπ/88) = 1247 EXACT**（閉式 (N−1)(N−2)/6 = C(87,2)/3 = 29×43；RAG 無命中）
6. O221 0.2457 對 88/176 格唔整 → 唔可以直接閉合

完整分析 → docs/02_tan_demo_analysis.md；驗證 → scripts/01_tan_spectral_sweep.py（10/10 PASS）。

## 二、先做嘅第一步

```
1. 讀 docs/02_tan_demo_analysis.md（tan 示範分析全文）
2. 跑 scripts/01_tan_spectral_sweep.py 確認 10/10 PASS
3. 完成「全開放問題掃描分類表」（130 主 O + 157 子問題 → tan 適用/唔適用/需測試）
4. 逐項 register handoff 去歸屬 O（O140/O117/O123/O7/O221/O35），跨 O 零檔案寫入
5. register.py check 確認回落基線（無新 HARD DRIFT）
```

## 三、已知陷阱

```
⚠️ tan²(nπ/88) 喺 n=44 必然爆（pole）——任何用 tan 嘅公式要定義域排除 n=44（或 n≡132 mod 88）
⚠️ Σtan² 有閉式 1247 = C(87,2)/3——但係「整數巧合」唔等於物理身份，未經盲測唔准引用為閉合
⚠️ 跨 O 交接只限 register（handoff/note）——禁寫入其他 O 任何檔案
⚠️ RAG 搜「1247」無命中——確認係新數字，但要 grep 全 repo 先可以宣稱新產物
⚠️ f-string 唔好用 mpf 格式化（用 mp.nstr）——慣例
```

## 四、關鍵數字

| 量 | 值 | 出處 |
|:---|:---|:-----|
| Σsin²(πn/88), n=1..87 | 44 = N/2（Parseval） | scripts/01 |
| Σtan²(nπ/88), n=1..43 | **1247 EXACT** = C(87,2)/3 = 29×43 | scripts/01（新發現） |
| tan(11π/88)=tan(π/8) | √2−1（八角分圓） | scripts/01 |
| tan(33π/88)=tan(3π/8) | √2+1 | scripts/01 |
| O221 相位差 0.2457 | n\*=6.88（88格）/ 13.76（176格）皆唔整 | scripts/01 |
| O221 dual 0.1303 | 同樣唔整 | scripts/01 |
| 開放主 O (state open/partial/registered) | 130 | register.sqlite 2026-10-10 |
| 開放子問題 (O\*/xxx) | 157 | register.sqlite 2026-10-10 |

## 五、交接 / 依賴

```
- 前置: 無（O246 係新掃描 O）
- 移交出: tan 示範結果 → O140（csc 家族）/ O117（sec）/ O123（atan）/ O7（相位滑移）/ O221（0.2457 對照）/ O35（拍頻 tan）；Σtan²=1247 → formula-registry 候選
- 範圍警告: 🔴 唔推導（開完不推）；唔寫其他 O 檔案；唔可以為 1247 安 physics label（結構證明完備先命名）
```

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**
> 當前狀態以 `open_problems_fresh/README.md` 為準；生命週期事件以 `problem_register/` 為準。

---

## Session 記錄

### Session 2026-10-11（掃描收尾 — 開完不推）

**執行內容**（對應「先做嘅第一步」）：

1. ✅ 讀 docs/02_tan_demo_analysis.md（示範全文）
2. ✅ 跑 scripts/01_tan_spectral_sweep.py → **10/10 PASS**（pole/FOLD/Parseval×2/八角/Σtan²=1247/O221×2/φ盲測/Σcsc²=2581）
3. ✅ 「全開放問題掃描分類表」完成（docs/03 + scripts/02 擴展）：
   - **主 O 131**（open-family snap 2026-10-11）：A=14 · B=55 · C=62
   - **子問題 157**（O*/xxx）：A=18 · B=77 · C=62
   - 分類判準：A = tan 可能直接適用（相位/位元/二元/摺疊/對稱/時間/譜相）；B = 需進一步測試（譜和/閉式/質量/算子）；C = 唔適用（純觀測/工具/命名/方法論）
4. ✅ 6 項 register handoff 去歸屬 O（跨 O 零檔案寫入）：
   - O246 → **O221**：三角波 fold 身份（arctan∘tan=fold；O221 殘餘⑤雙 description 可能適合 fold 語言）
   - O246 → **O140**：γ=csc 家族延伸（Σtan² vs Σcsc² 同 digamma 家族；tan²=sec²−1）
   - O246 → **O117**：sec 家族延伸（tan²=sec²−1；八角子格 n=11k 可能關 M(l)=sec(π n_c/88)）
   - O246 → **O123**：tan 角度身份（atan(β) 已閉合；tan 唯一合法身份=角度提取）
   - O246 → **O7**：相位滑移 π（tan pole=相位翻轉點；O7 位元寫入相位滑移 π 結構同源）
   - O246 → **O35**：拍頻 tan（O35 標題已含 Sin/Cos/Tan；tan 版本未評）
5. ✅ 1247 查重：RAG 無命中＋**全 repo grep 確認無 Σtan² 先例**（其餘「1247」命中皆 2.8284271247=2√2、1.041247565=100θ*、7.1247e16、12471.14 等尾段）⟹ 新產物確認 → formula-registry 加候選 entry（status 🔮，未安 physics label）
6. ✅ register.py check：HARD DRIFT 回落基線 18（O246 唔喺 drift 列）、NO-BLOCK 567、SEED-DISAGREE 48 都係既有基線
7. ✅ README O246 行新增（狀態：🟡 已掃描 — 全部開放問題分類完成 (10-11, 開完不推)）

**判決**：本 O 任務完成（掃描＋示範驗證＋交接）。**開完不推** —— 唔做任何後續 tan 推導；後續 tan 攻擊由歸屬 O 決定（O221/O140/O117/O123/O7/O35）。

**剩餘（誠實記錄）**：docs/03 分類由 keyword 規則產生（scripts/02），細類可能有邊界誤判；A/B 類 O 嘅實際 tan 適用性**未逐一盲測**（本 O 範圍外，屬歸屬 O 各自攻堅）。

### Session 2026-10-11（六項 handoff 全撤回 — O140 基準重審）

**觸發**：調律者指示「O140 O117均已否決，把其餘的用O140 O117相同基準再計算一次，不符合就撤回register交接」。

**執行**：

1. ✅ O140 否決確認（docs/17，09:00 note）：五項審查中盲測/預測性/適用性 FAIL——`(N−1)(N−2)/6` 係**標準 digamma/cot² 重述**（tan² 半譜=½Σcot² 全譜），「新發現」宣稱過度；1247 對 FSR 零交集
2. ✅ O117 否決確認（docs/06，09:20 note）：八角格 sec 對 6×M_obs 零命中；唯一交點 n=22=√2 係 O170 已知鎖定點；tan²=sec²−1 argument-blind
3. ✅ scripts/03 重審其餘 4 項（O140 五項基準，mpmath 50 dps，6 檢查 PASS 全確認不適用）：
   - O221：fold 喺任意實數成立（∀x），88 格 fold 值 43 個全係自身摺疊 → 定義級恆等，零預言
   - O7：tan pole 喺 π/2 **唔係** π（tan(π)=0）；「同源」無機制
   - O123：atan(β)=31.717° → n*=15.506 非整數，88 格無格點
   - O35：拍頻 B(d,s)=4sin·cos 純 sin·cos，tan 零交集
4. ✅ register note：O246 一條總撤回記錄（ref=docs/04）
5. ✅ docs/04_handoff_withdrawal.md 全新檔（撤回理由完整）
6. ✅ docs/02 §2.4 append-only 更正附註：1247「新發現」降格為「cot² 家族已知結構之重述」
7. ✅ formula-registry 1247 entry：status 🔮→🟡，notes 加否決
8. ✅ README O246 行更新（六項 handoff 全撤回）

**判決**：**六項 handoff 全部撤回，註銷為 O246 自身產物**。數學恆等本身成立（EXACT、N 通用 13/13），但「適用性/新發現」宣稱級全部 FAIL。docs/03 掃描分類表獨立於 handoff 有效性，仍然係本 O 掃描產物（130 主 O + 157 子問題已掃，A/B/C 分類保留）。

**剩餘（誠實記錄）**：tan 對 IDCM「位元/二元層潛在適用」維持「未驗證」🟡 狀態（docs/02 §三 判定 3）——冇任何 O 實質承接；1247 只係 tan 家族譜和事實。