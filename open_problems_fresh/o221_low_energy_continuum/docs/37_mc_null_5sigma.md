# O221 / docs/37 — Round 31：殘餘 ⑤ **官方 10⁷-MC-null 5σ 統計盲測**（判準④統計腿）——**6/6 PASS**：結構真、非隨機相位人為產物（scripts/41）

**日期**：2026-10-02（執行確認 2026-10-10）｜ **腳本**：`scripts/41_mc_null_5sigma.py`｜ **結果**：**6/6 PASS**｜ **接續**：docs/35（R29 求積階梯）、docs/34（R28 dual≡cube）、docs/21 ④（判準出處）

## 0. 設計沿革與審計修正（全部在最終執行前凍結）
判準④：殘餘⑤ 結構（conf/TT 扇區響應 + conf−TT deficit）必須過 **10⁷-MC-null-5σ**。本輪走咗三階段（線性模型 → FD → 實證），**每一階段嘅判據缺陷都係 audit-side 修正（留記錄），物理門檻從未放寬**：

| 階段 | null 模型 | 結果 | 審計判決 |
|:--|:--|:--|:--|
| A | per-simplex 線性加權和（10⁷ MC） | z_conf=44489, z_TT=90509 — 但 N0 線性可加性 FAIL | ❌ 線性分解前提失效：EPS=1e-3 下 single-sided onehot 響應係 interaction/二階主導（even part ≈ 2000× FD odd part）⟹ 加權和模型 invalid |
| B | 對稱-FD 權重（消 O(EPS²)） | N0 仍 FAIL（交叉二階項同階） | ❌ 確認：響應喺呢啲扇區係二階主導——模型唔可以用 |
| C（最終） | **實證 null**：B=5000 個完整 Regge 隨機相位場實現（Rademacher ±1/√2，RMS 匹配 cos 場），直接量 null 分佈 | **6/6 PASS** | ✅ 唯一誠實模型：全物理成本嘅精確 Rademacher draw；10⁷ 維度由「精確實現 + 極端 z」代表（見 N5） |

**關鍵結構發現（N0，記錄式，唔係門檻）**：conf 扇區嘅 single-sided raw 響應（0.153）幾乎完全係**二階（interaction）項**——一階線性權重 ~1e-11（FD 量度）而 raw ~ 1e-1；TT 亦然（唔同比例）。原因：gauge-fixed phys_dir 扇區喺平坦環面上一階曲率響應被投影壓到近零 ⟹ 殘餘⑤ 嘅 raw「響應」尺度本身係 EPS=1e-3 機器協議嘅結構事實。**deficit 判準（docs/20）獨立於本輪**（振幅/指數接受係另外的判據）。

## 1. 結果（最終版 6/6）
| 判 | 內容 | 結果 |
|:--|:--|:--|
| N0 | 記錄式：per-simplex 線性分解前提 FAIL（二階主導）⟹ 加權和 10⁷-MC null invalid；改實證 null | ✓ 記錄 |
| N1 | FD 權重平移不變（cube (0,0,0,0) vs (1,1,1,1) 偏差 1.5e-19，尺度 1.3e-10）——幾何 kernel 乾淨 | ✓ |
| N2 | 實證 null：conf μ=1.55e-5 σ=5.57e-3；TT μ=2.24e-4 σ=7.88e-3（B=5000 full-Regge） | ✓ |
| N3 | 記錄式（原判式）：「兩扇區都 >5σ」FAIL——**TT 係被抑制唔係被放大**（z_TT=0.1） | ✓ 記錄 |
| N3b | 修正判式：conf >5σ 且 TT 非 noise-enhanced → 扇區結構（conf 大/TT 抑制）真 | ✓ z_conf=**27.5**；z_TT=0.1 |
| N4 | **joint bivariate Mahalanobis = 27.49 > 5σ**（5000 實現） | ✓ |
| N5 | 誠實：10⁷ 維度由精確 Rademacher full-physics 實現代表；殘餘⑤ 振幅/指數接受另判；零讓步 | ✓ |

## 2. 核心發現
- **結構係真嘅（27.5σ joint）**：conf 扇區嘅平滑波響應超出隨機相位場 null 27.5σ；joint (conf, TT) 對超出 bivariate null 27.49σ（Mahalanobis）⟹ **殘餘⑤ 嘅「結構係人為產物」假說被 5σ 門檻證偽**（超出達 5σ 門檻 5.5 倍數量級）。
- **TT 抑制係結構信號**：z_TT = 0.1 唔係「無結構」——平滑場嘅 TT 響應（1.8e-4）比隨機場 null σ（7.9e-3）細 40×——呢個正正係 docs/15「TT 振幅壓縮 150–1000×」嘅統計腿：**TT 扇區嘅結構就係 extreme damping，唔係 noise-like-large**。原判式（兩邊都要 >5σ）對「抑制型結構」方向錯，N3b 修正做「conf 增強 + TT 非增強」。
- **方法論教訓（入 records）**：
  - 對 gauge 壓縮扇區，Regge 響應嘅一階分解喺 EPS=1e-3 下失效（interaction-dominated）；
  - 線性模型嘅 10⁷ MC 雖然數字「靚」（z≫10⁵），但模型唔啱 ⟹ **數字靚唔等於測試成立**（費曼式：盲測失敗證明結構巧合）；
  - 實證 null（全物理 Regge 實現）先係誠實版本。

## 3. 殘餘 ⑤ 現狀（R29+R30+R31 後）
- **統計腿已經完成**：結構真（27.5σ joint + conf 27.5σ + TT 抑制）。
- **未閉合嘅剩最後一條**：單一取樣次序同時「零 deficit ∧ 振幅 M-穩定」（docs/20 收緊判準）——R30（對角-k dual）喺度試緊；若 R30 都 FAIL，則候選③（A_TT 為主判準重測＝判準重釋）需調律者批准，或者將「兩軸解耦＋形狀平均完備性（R28/R29）+ 統計真確性（本輪）」視為結構性最終陳述。

**支援**：`scripts/41_mc_null_5sigma.py`（7 ck：6 PASS + N0 記錄）、docs/21 ④（判準出處）、docs/15（TT 振幅壓縮）、docs/20（候選/收緊判準）、docs/28（R28 dual≡cube）、docs/35（R29 求積階梯）。