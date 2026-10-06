# O233 SESSION_START — C_f 結構身份：生成器 hunt → 鋸齒/Z₂ → lepton 槽 n≡1 (mod 4)（由 O206 第10-15輪轉移）

<!-- registry
pid:     O233
title:   C_f 結構身份：生成器 hunt → 鋸齒/Z₂ → lepton 槽 n≡1 (mod 4)（由 O206 第10-15輪轉移）
state:   partial
verdict: partial
flags:   -
owner:   O233
created: 2026-10-06
updated: 2026-10-06
prereq:  O120, O137, O206
source:  O206 第10-15輪（O120 session 內越界完成, 2026-10-06, 調律者裁決轉移）
-->

> **Session**: 2026-10-06（由 O206 承接轉移）
> **狀態**: 🟡 **已承接 O206 第10-15輪推導**（git mv 自 O206）
> **來源**: O206 第十至十五輪（C_f 推導；原於 O120 session 內越界完成, 調律者裁決開新 O 轉移）
> **前置**: O120, O137, O206
> **位置**: `open_problems_fresh/o233_c_f_identity/`

---

## 一、接手起點

**2026-10-06 轉移事件**：O206 嘅第十至十五輪推導（C_f 結構身份戰線）原喺 O120 closeout
session 內越界完成。調律者裁決（「這個不是O206 session」）：二選一——開新 O 轉移／刪除還原
只寫交接。**本 O 揀 Option 1（開新 O 轉移）**：git mv scripts/29–39、docs/33–43、
logs/29–39、data/29–39 由 O206 搬入本 O；O206 保留前十輪本體（scripts/01–28/docs/01–32）。

**內容現況（第十五輪終點）**：C_f 結構身份已達五個正結果（鋸齒 split p=0.0138、階梯 T-rank
p=0.00117、兩者獨立同時極端、u/d 身份層穩健、lepton 槽 n≡1 mod 4 p=0.0476/0.0179）；
剩餘 🔴：輕子槽成因（點解 ≡1 唔係 ≡3）、up-type 冇固定 residue、even/odd 兩流算子身份。

## 二、先做嘅第一步

```
1. 睇 docs/11（第十五輪 charge-residue 更正）→ 確認正確 residue 表
2. 輕子槽成因: 以 O158 mod-4 判準 + O210-T1（k ≡ ±|B−L| mod B, B=4）為錨,
   查 A₅ 手性投影（O137）會唔會強制「輕子 ≡1 mod 4」
3. 若成因路線有具體候選 → 寫 scripts/40 獨立驗證（pre-registered null）
```

## 三、已知陷阱

```
⚠️ docs/10_ B4 原表有誤: ≡3 = {d, c(UP!), b}——c 係 up-type（+2/3）, 唔係 down-type（docs/11_ 更正）
⚠️ T_k+1/2^k+1 峰值/谷值地址係 numeric red herring——真身 = rank parity Z₂（docs/06_ §二）
⚠️ κ 非對角方向已失格（載體 CSSG-v3 第十輪已降級）——禁區唔重推
⚠️ 同一 8 點 dataset 已多輪 look——新盲測要 pre-register 並會計 look-elsewhere
⚠️ 舊 register notes（O206 pid）ref 指 docs/33-43——git mv 後 REF-MISSING 屬結構性轉移,
   唔係記錄錯誤（O206 note 已說明）
```

## 四、關鍵數字

| 量 | 值 | 出處 |
|:---|:---|:-----|
| 合法模式集 | {1,2,3,4,5,7,9,11,13} | O137 R19 |
| M₀（W-field 標度）| 27.900915 MeV | O38 |
| C_f(e,u,d,s,μ,c,τ,b) | 3.594, 3.803, 3.662, 41.32, 30.03, 186.06, 159.64, 255.75 | O120 |
| 鋸齒 7/7 交替 p | 0.0138（MC 10⁶, log-uniform H0）| docs/05_ |
| Z₂ rank 分裂 | even {u,s,c,b} / odd {e,d,μ,τ} 各自單調增, 相鄰 4/4 | docs/06_ |
| 分裂類 1055/40320 = 2.6% | 升序係其中一個非唯一 | docs/07_ |
| u/d 閾值 | ln(u/d) > ln(γ₂/γ₃) = 0.44539 | docs/07_ |
| 冪律 α | 2.0634 ≈ 2（envelope 非生成器）| docs/08_ |
| L1 quark/lepton 分層 | p=0.0714 邊緣 FAIL（誠實）| docs/09_ |
| L4 lepton modes | {1,5,9} 等差 4 | docs/09_ → 升格 docs/10_ |
| ★ lepton 槽 p | B1 {1,5,9}: 0.0179；B3 ≡1 mod 4: 0.0476 | docs/10_ |
| 正確 residue 表 | ≡0: s(4)；≡1: e,μ,τ,t(1,5,9,13)；≡2: u(2)；≡3: d,c(UP),b(3,7,11) | docs/11_ |

## 五、交接 / 依賴

```
- 前置: O120（C_f 定義）— O137（模式集 + A₅ 指派）— O206（γ-階梯/塊層 v8-v10 本體）
- 移交出: 輕子槽成因 → 候選銜接 O158（mod-4 判準家族）/O210（B−L mod B）/O139（手性橋）
- 範圍警告: 唔做 O206 前十輪本體（頻率審計/映射層）——保留原位; 唔做質量值本身（O120 已 closeout）
```

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**
> 當前狀態以 `open_problems_fresh/README.md` 為準；生命週期事件以 `problem_register/` 為準。

---

## 六、append 2026-10-06（第十六輪攻堅 R1a–R3）

- **R1a 全新診斷**：Assignment 分歧——O209 唯一分配（|Δm| 排序, 1=t…13=e, 輕子 {3,5,13}）vs 本 O/O137-R19 用嘅 γ 升序（1=e…13=t, 輕子 {1,5,9}）**方向相反**；O137 docs/36 §1.3 已以 O209 集判 lepton 槽 ❌（0/14）。
- **R1b**（scripts/12）：輕子 ≡1 只喺 A_γ 成立（8-mode P=1/56=0.0179, =docs/10 B1）；「6 夸克空缺」無鑑別力（max residue class 4<6）；O210-T3 讀法1（Q≡1）只喺 A_γ 成立，讀法2 兩可。
- **R2**（scripts/13）：look-elsewhere family 校正（5 個 mod-k 類, MC 10⁶）⟹ **P=0.1204 > 0.05**——lepton 槽 B1/B3 過唔到 family-wise 校正，降為「樣本外單目標 nominal」。
- **R3**（scripts/14）：鋸齒 7/7 交替（p=0.0138）**只喺 A_γ**；A_|Δm| 下 3/4 反向（消失）；X 算子 Z₂ 同 rank-parity 非直接同源（未證）。
- ⟹ **O233 五項正結果全部建基於 γ 升序 assignment 選擇**；該選擇與 O209 權威（345/345）衝突，需跨 O 裁決。
- 交付：docs/12 + scripts/12–14 + data/12–14（舊檔零改動）。

## 七、append 2026-10-06（裁決收錄：O137 R22 + O209 closeout 回覆）

- **O137 授權**（`SESSION_START` §R22, 17:13）：A₅ γ 升序 = 正式指派（e→1…t→13, 輕子{1,5,9}≡1 mod 4）；docs/36 §1.3 [3,5,13] = 檢定 O209 提案，非 O137 採用。
- **O209 回覆**（closeout, 17:13）：|Δm| 唯一分配喺自身 ansatz 內成立；典範性屬跨 O 問題 → 移交 O137 裁定；O209 核心閉合不受影響。
- **綜合**：γ 升序正式勝出 ⟹ O233 五項正結果 assignment 基礎合法；但 look-elsewhere 校正（P=0.1204>0.05）獨立於 assignment 維持——lepton 槽/鋸齒仍 nominal 級，唔自動升格。
- 已入 docs/12 §七（裁決收錄）；跨 O 檔零改動（O137/O209/O120 只經 register）。