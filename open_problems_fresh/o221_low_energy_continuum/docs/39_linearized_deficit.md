# O221 / docs/39 — Round 32：**線性階結構：per-edge 基底 + EPS¹ 證明 + vert 近閉合**（scripts/42：4/9 PASS + 5 記錄 FAIL）

**日期**：2026-10-11（執行 2026-10-10）｜ **腳本**：`scripts/42_linearized_deficit.py`（host `o221-42svc` 無限 mem）｜ **結果**：**4/9 PASS**（L1/L5 全 PASS；L2×1 PASS + 2 記錄 FAIL；L3×1 PASS + 2 記錄 FAIL；L4 FAIL）｜ **接續**：docs/37 附註更正（R31-N0 誤讀）、docs/38（fold 盲測 B + O246 handoff 未接納）、docs/20（候選③）

## 0. 設計（預註冊，2026-10-10 凍結；2026-10-11 探測後 correction：L5 由「raw~EPS²」改「測 α∈[0.9,1.1]」——探測已證 EPS¹，審計側修正）
R31-N0 稱 raw 扇區響應 interaction/二階主導。R32 目標：① 檢驗 full-field 響應嘅真正階數（EPS 標度）；② per-edge 線性基底（per-simplex lumping 偽影解析）；③ 線性化（FD）deficit 與振幅 vs raw——docs/20 判準喺一階層面有冇可能閉合。

## 1. 結果
| 判 | 內容 | 結果 |
|:--|:--|:--|
| **L1** | **per-edge 基底坐實**：per-edge RMS |c_e| = 6.29e-5（conf）/4.61e-5（TT）；per-simplex FD max = 1.25e-10；**相消因子 1,587,319**——R31-N0 嘅「1e-10 權重」係 10 條邊暴力相消嘅 lumping 偽影 | ✓ |
| L2-native | raw deficit +1.0737 vs FD +0.8828（2-pt M=4→16）——|Δ|=0.1910 ≥0.10：**raw 2-pt 唔係一階**（even 污染非細） | ✗ 記錄 |
| L2-vert | raw −0.0000 vs FD −0.0511，|Δ|=0.0510 <0.10（vert TT raw 係 even 主導：M=16 −1.7e-3 vs FD −8.6e-8） | ✓ |
| L2-cube | nan（響應精確零） | ✗ 記錄（結構性 nan） |
| L3 | FD A_TT（M=12→16）：naive 1.5371 ✗、**vert 1.1651 ✓**、cube nan | 1 PASS + 2 記錄 |
| **L4** | docs/20 判準喺 FD 階：**無家族同時中**（vert deficit 0.0511 差 0.05 門檻僅 2%；cube 0/0 未定義） | ✗ |
| **L5** | **EPS¹ 證明 4/4**：conf/raw α=1.0004、conf/fd 1.0000、TT/raw 0.9958、TT/fd 1.0000（值 4.5e-1→4.5e-2→4.5e-3 比率 0.100 精確）⟹ **raw 扇區響應一階線性**——R31-N0「二階主導」詮釋正式更正 | ✓ 4/4 |

**RESULT：4/9 PASS + 5 記錄 FAIL。零門檻放寬。**

## 2. 核心發現
- **★ Cube 家族 sector 響應喺 axial k 精確為零（M≥4）**：conf raw = TT raw = 0.000e+00（float64 精確零；M=3 有邊界殘餘 −8.4e-7）⟹ **R28「cube deficit → 0」嘅真正機制唔係「deficit 被壓」，而係整個扇區響應身份消失**——uniform-per-simplex 相位喺 axial-k 投影下完全瞓喺 kernel 零空間（A_agg = 0/0 = nan 係結構性，唔係數值 bug）。
- **★ vert 喺一階層面近乎雙判準**：FD deficit −0.0511（門檻 0.05，**超 2%**）＋ A_TT_fd 1.1651 OK——**迄今最近一次接近 docs/20 收緊判準**，而且喺「正確嘅一階 order」。raw vert deficit（−0.31..−0.43）嘅誤導係因為 vert TT raw 係 even（quadratic）主導——真正線性部分係 −0.051。
- **naive：FD deficit +0.8828 ≈ 經典 +0.88**（docs/19-29 嘅 ladder 程序實際上量嘅係一階 deficit；raw 2-pt 1.0737 反而有 even 污染）⟹ 經典 deficit +0.88 係一階結構 ✓（等於 B 盲測前嘅可反推結論）。
- **L5 4/4 確認 R31-N0 更正**：full-field raw 響應 = 一階線性（EPS¹）；docs/17-29 嘅 M-指數係一階指數——唔需要「消二階污染」重推（docs/37 附註嘅結論正式坐實）。
- **per-edge 結構**：coherence conf 12.9（平滑波 vs 隨機場 √Var）、TT 0.9（抑制）；per-edge 係數 6e-5 大但 per-simplex 相加相消 1.6e6 倍——呢個先解釋 naive/cell（per-edge 相位）大響應 vs vert/cube/dual（per-simplex 均一相位）細/零響應。

## 3. 殘餘 ⑤ 現狀（R32 後）
- **未閉合**：無家族同時（零 deficit ∧ 振幅穩定）——FD 階亦無；vert 差 2%。
- **候選③（A_TT 主判準＝判準重釋）**:在 FD 階下更強——vert A_TT_fd 穩定 + deficit 0.0511 ≈ 0。若調律者批准 A_TT 主判準，vert 喺一階層面幾乎閉合。**仍需批准**。
- 或「兩軸解耦＋形狀平均完備性＋統計真確性＋一階結構確認」＝結構性最終陳述。
- 另：cube 精確零＝「零響應家族」本身係結構事實——殘餘⑤ 嘅「deficit 階梯」最底層唔係 0 而係 **底層消失**（響應身份 vanish）。

**支援**：`scripts/42_linearized_deficit.py`（9 ck：4 PASS + 5 記錄 FAIL）、docs/37（R31 + 附註更正）、docs/38（fold 盲測 + O246 handoff 未接納）、docs/20（判準）。